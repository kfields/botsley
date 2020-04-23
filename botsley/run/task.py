import contextvars
from contextlib import contextmanager
from uuid import uuid1
from copy import copy
import inspect

from botsley.run import *
from botsley.run.policy import Policy

TS_INITIAL = "Initial"
TS_RUNNING = "Running"
TS_SUCCESS = "Success"
TS_FAILURE = "Failure"
TS_SUSPENDED = "Suspended"
TS_HALTED = "Halted"

#
# Context Management
#
PARENT = "parent"

ctx_parent = contextvars.ContextVar("ctx_parent", default=None)


def ctx_enter(parent, child):
    if not parent:
        parent = ctx_parent.get()
    if parent:
        child.parent = parent
        parent.add(child)

    ctx_parent.set(child)
    return {PARENT: parent}


def ctx_exit(ctx):
    ctx_parent.set(ctx[PARENT])


class method:
    def __init__(self, instance, func):
        self.im_self = instance
        self.im_class = instance.__class__
        self.im_func = func

    def __call__(self, *args, **kw):
        if self.im_self:
            args = (self.im_self,) + args
        return self.im_func(*args, **kw)


# class Task(metaclass=TaskMeta):
class Task(Policy):
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
        self.policy = self
        self.tasks = None

    def __await__(self):
        return (yield self)

    async def main(self, msg=None):
        pass

    def use(self, fn):
        if not inspect.iscoroutinefunction(fn):
            raise Exception("Not a coroutine function!", fn)
        self.main = method(self, fn)

    def start(self):
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

    def define(self, trigger, action):
        return self.addRule(Rule(trigger, action))

    def sig(self, trigger, action):
        # self.bot.signal(trigger, self)
        return self.define(trigger, action)

    def addRule(self, r):
        if not self.policy:
            self.policy = Policy(self)
        return self.policy.add(r)

    def findRule(self, m):
        return self.findRules(m).pop()

    def findRules(self, m):
        if self.policy:
            return self.policy.find(m)
        return []

    def matchRule(self, m):
        return self.matchRules(m).pop()

    def matchRules(self, m):
        if self.policy:
            return self.policy.match(m)
        return []

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

    def schedule(self, task):
        runner.schedule(task)

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

    """
    def fail(self):
        self.status = TS_FAILURE
        raise Failure()
    """

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

    async def spawn(self, o, wait=False):
        task = None
        if type(o, function):
            task = Task(o)
        elif isinstance(o, Task):
            task = o
        else:
            raise Exception("Expecting Function or Task")
        if wait:
            task.caller = self

        return runner.schedule(task)

    """
    def call(self, s, p, o, x):
        c = Achieve(s, p, o, x)
        m = Attempt(c, self)
        m.caller = self
        self.post(m)
        return self.suspend()
    """

    async def call(self, task):
        await runner.schedule(task)
        return self.suspend()

    def perform(self, s, p, o, x):
        c = Achieve(s, p, o, x)
        m = Attempt(c, self)
        return self.post(m)

    def propose(self, c):
        return self.post(Propose(c, self))

    def attempt(self, c):
        return self.post(Attempt(c, self))

    def declare(self, c):
        return self.post(Assert(c, self))

    def retract(self, c):
        return self.post(Retract(c, self))

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


#
# Condition
#
class Condition(Task):
    pass


@contextmanager
def condition(parent=None):
    child = Condition()
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


condition_ = lambda: Condition()

#
# Action
#
class Action(Task):
    pass


@contextmanager
def action(parent=None):
    child = Action()
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


action_ = lambda action: Action(action)


#
# Sequence
#
class Sequence(Task):
    def __init__(self):
        super().__init__()

    async def main(self, msg=None):
        for child in self.children:
            result = await child
            if result == TS_FAILURE:
                return self.fail()


@contextmanager
def sequence(parent=None):
    child = Sequence()
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


#
# Loop
#
class Timer(Task):
    def __init__(self, timeout):
        super().__init__()
        self.timeout = timeout

    async def main(self, msg=None):
        for child in self.children:
            try:
                await child
            except Failure:
                return


@contextmanager
def timer(timeout, parent=None):
    child = Timer(timeout)
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


#
# Loop
#
class Loop(Task):
    def __init__(self):
        super().__init__()

    async def main(self, msg=None):
        while True:
            for child in self.children:
                result = await child
                print("loop result", result)
                if result == TS_FAILURE:
                    return self.fail()


@contextmanager
def loop(parent=None):
    child = Loop()
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


#
# Counter
#
class Counter(Task):
    def __init__(self, start, stop):
        super().__init__()
        self.count_start = start
        self.count_stop = stop
        self.count = 0

    async def main(self, msg=None):
        for i in range(self.count_start, self.count_stop):
            self.count = i
            for child in self.children:
                result = await child
                print("counter result", result)
                if result == TS_FAILURE:
                    return self.fail()


@contextmanager
def counter(start, stop, parent=None):
    child = Counter(start, stop)
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


#
# Parallel
#
class Parallel(Task):
    def __init__(self):
        super().__init__()

    async def main(self, msg=None):
        for child in self.children:
            self.schedule(child)
        return self.suspend()


@contextmanager
def parallel(parent=None):
    child = Parallel()
    ctx = ctx_enter(parent, child)
    yield child
    ctx_exit(ctx)


#
# Chain
#
class Chain(Task):
    def __init__(self, action):
        super().__init__(action)

    def main(self):
        child = self.children[0]
        self.bot.schedule(child)
        return self.suspend()

    def strategy(self, child):
        self.remove(child)
        if child.status == TS_FAILURE:
            return self.fail()
        if child.dst:
            return self.bot.schedule(child.dst)


chain_ = lambda action: Chain(action)


#
# Method
#
class Method(Sequence):
    pass


method_ = lambda action: Method(action)

#
# Module
#
class Module(Method):
    pass


module_ = lambda action: Module(action)

sequence_ = lambda action: Sequence(action)

counter_ = lambda start, stop, action: Counter(start, stop, action)

parallel_ = lambda action: Parallel(action)

#
# Runner
#
class Runner:
    def __init__(self):
        self.queue = []
        self.callbacks = []

    def schedule(self, obj, msg=None):
        task = None
        if inspect.iscoroutinefunction(obj):
            task = Task(obj, msg)
        elif not isinstance(obj, Task):
            raise Exception("Not a Task!", obj)
        else:
            task = obj
        task.start()
        self.queue.append(task)

    def reschedule(self, task):
        task.status = TS_RUNNING
        self.queue.append(task)

    def step(self):
        queue = self.queue
        self.queue = []
        for task in queue:
            print("task", task)
            print("task.status", task.status)
            try:
                print('task.coro', task.coro)
                awaited = task.coro.send(task.awaited.result if task.awaited else None)
                print("awaited", awaited)
                if awaited:
                    task.status = TS_SUSPENDED
                    task.awaited = awaited
                    awaited.awaiter = task
                    self.schedule(awaited)

            except StopIteration as exception:
                result = exception.value
                print("stop result", result)
                task.result = result
                if task.awaiter:
                    print("task.awaiter", task.awaiter)
                    self.reschedule(task.awaiter)

            # except Failure as exception:

        callbacks = self.callbacks
        self.callbacks = []
        for callback in callbacks:
            callback()

    def run(self, task):
        self.schedule(task)
        while len(self.queue) != 0:
            self.step()


runner = Runner()
