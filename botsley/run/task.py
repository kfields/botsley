import time
import contextvars
from contextlib import contextmanager
from uuid import uuid1
from copy import copy
import inspect
from loguru import logger

from botsley.run import *

TS_INITIAL = "Initial"
TS_RUNNING = "Running"
TS_SUCCESS = "Success"
TS_FAILURE = "Failure"
TS_CANCELLED = "Cancelled"
TS_SUSPENDED = "Suspended"
TS_HALTED = "Halted"


class method:
    def __init__(self, instance, func):
        self.im_self = instance
        self.im_class = instance.__class__
        self.im_func = func

    def __call__(self, *args, **kw):
        if self.im_self:
            args = (self.im_self,) + args
        return self.im_func(*args, **kw)


class Task:
    def __init__(self, action=None, msg=None):
        if action:
            self.use(action)
        self.msg = msg
        self.coro = None
        self.awaited = None
        self.awaiter = None
        self.result = None

        self.id = uuid1()
        self.bot = None
        self.parent = None
        self.children = []
        self.result = None
        self.status = TS_INITIAL
        self.tasks = None

    def __await__(self):
        return (yield self)

    async def main(self, msg=None):
        pass

    async def sleep(self, period=None):
        # print('sleep', period)
        if not period or period == 0:
            # quick and dirty way to yield control back to the runner
            return await self
        return await Sleep(period)

    def check(self):
        if self.status == TS_RUNNING:
            return True
        return False

    def use(self, fn):
        if not inspect.iscoroutinefunction(fn):
            raise Exception("Not a coroutine function!", fn)
        self.main = method(self, fn)

    def begin(self):
        self.coro = self.main(self.msg)
        self.status = TS_RUNNING
        # print(self.coro)

    def add(self, child):
        child.parent = self
        child.tasks = self.tasks
        self.children.append(child)
        return self

    def remove(self, child):
        index = self.children.indexOf(child)
        if index > -1:
            self.children.splice(index, 1)
        return self

    #
    # EXECUTION
    #
    def strategy(self, child):
        status = child.status
        if status == TS_FAILURE:
            # raise Failure()
            return status
        elif status == TS_SUCCESS:
            return status

    def schedule(self, task, msg=None):
        runner.schedule(task, msg)

    def run(self):
        runner.run(self)

    def suspend(self):
        self.status = TS_SUSPENDED
        return self.status

    def resume(self):
        self.status = TS_RUNNING
        return self.status

    def succeed(self):
        self.status = TS_SUCCESS
        return self.status

    def fail(self):
        print("fail")
        self.status = TS_FAILURE
        if self.parent:
            return self.parent.strategy(self)
        else:
            return self.status

    def cancel(self):
        print("cancel")
        self.status = TS_CANCELLED
        for child in self.children:
            child.cancel()

    def halt(self):
        if self.bot:
            self.bot.halt()
        self.status = TS_HALTED
        return self.status

    def broadcast(self, msg):
        pass

    def post(self, msg):
        msg.sender = self
        return self.bot.post(msg)

    #
    # Utility
    #
    def toJSON(self):
        return {TYPE: self.__class__.__name, MSG: self.msg}

    #
    # DSL
    #
    def chain(self, b):
        a = self.children[self.children.length - 1]
        if a:
            a.dst = b
            b.src = a
        self.add(b)
        return self


class Trap(Task):
    pass


class Sleep(Trap):
    def __init__(self, period):
        super().__init__()
        self.period = period
        self.start = time.time()

    async def main(self, msg=None):
        while True:
            current = time.time()
            elapsed = current - self.start
            logger.debug(f"elapsed {elapsed}")
            logger.debug(f"period {self.period}")
            if elapsed >= self.period:
                logger.debug("sleeps over")
                return elapsed
            logger.debug("sleep some more")
            await self.sleep()


#
# Runner
#
class Runner:
    def __init__(self):
        self.queue = []
        self.callbacks = []

    def trap(self, task):
        if isinstance(task, Sleep):
            # run it as a normal task
            self.schedule(task)
        else:
            raise Exception("Not implemented")

    def schedule(self, obj, msg=None):
        logger.debug(f"schedule msg {msg}")
        task = None
        if inspect.iscoroutinefunction(obj):
            task = Task(obj, msg)
        elif not isinstance(obj, Task):
            raise Exception("Not a Task!", obj)
        else:
            task = obj
        task.begin()
        self.queue.append(task)

    def reschedule(self, task):
        task.status = TS_RUNNING
        self.queue.append(task)

    def step(self):
        logger.debug("runner.step")
        queue = self.queue
        self.queue = []
        for task in queue:
            logger.debug(f"task {task}")
            logger.debug(f"task.status {task.status}")
            try:
                logger.debug(f"task.coro {task.coro}")
                result = None
                if task.awaited:
                    result = task.awaited.result
                    task.awaited = None
                awaited = task.coro.send(result)
                logger.debug("awaited", awaited)

                if awaited is task:
                    # quick and dirty way to yield control back to the runner
                    logger.debug("task yielded control")
                    self.reschedule(task)
                elif awaited:
                    task.status = TS_SUSPENDED
                    task.awaited = awaited
                    awaited.awaiter = task
                    # self.schedule(awaited)
                    if isinstance(awaited, Trap):
                        self.trap(awaited)
                    else:
                        self.schedule(awaited)

            except StopIteration as exception:
                result = exception.value
                logger.debug(f"stop result {result}")
                task.result = result
                if task.awaiter:
                    logger.debug(f"task.awaiter {task.awaiter}")
                    self.reschedule(task.awaiter)

            # except Failure as exception:

        callbacks = self.callbacks
        self.callbacks = []
        for callback in callbacks:
            callback()

    def run(self, task):
        logger.debug("runner.run")
        self.schedule(task)
        while len(self.queue) != 0:
            self.step()


runner = Runner()
