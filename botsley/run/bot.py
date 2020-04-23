import asyncio
from copy import copy
from uuid import uuid1

from botsley.app import logger
from botsley.run import *
from botsley.run import _impasse
from botsley.run.task import Task, Module, TS_RUNNING, TS_SUCCESS
from botsley.run.context import Context
from botsley.run.policy import Policy

class Bot(Task):
    def __init__(self):
        super().__init__()
        self.id = uuid1()
        self.ctx = Context()
        self.tasks = []
        self.posts = []
        self.queue = []
        self.proposals = []
        self.scheduled = False
        self.impassed = False
        # self.post(Attempt(Achieve(null, _start, null)))
        '''
        self.signals = Map([
            [_impasse, []]
        ])
        '''
        self.signals = None
    '''
    def schedule(self, t):
        if t == self:
            return super().schedule(t)

        if isinstance(t, Bot):
            t.run()
        # self.schedule(self)
        return t
        #Else ...
        t.bot = self
        self.queue.append(t)
        self.schedule(self)
        return t
    '''
    def broadcast(self, msg):
        m = copy(msg)
        logger.debug(f"Broadcast:\t{m}")
        m.sender = self
        self.post(m)
        return map(self.tasks, lambda t: t.broadcast(m))

    def post(self, msg):
        if not msg.sender:
            msg.sender = self
        logger.debug(f"Post:\t{msg}")
        return self.posts.append(msg)

    def fork(self, t):
        logger.debug(f"Fork:\t{t.msg}")
        child = Bot()
        child.policy = self.policy
        child.ctx = self.ctx.copy()
        return child.run(t)

    def dispatch(self, msg):
        T = type(msg)
        if T is Propose:
            logger.debug(f"* \t{msg}")
            pmsg = Attempt()
            pmsg.update(msg)

            self.proposals.append(pmsg)
            return
        elif T is Assert:
            logger.debug(f"+ \t{msg}")
            self.ctx.add(msg.data)
            return self.fire(msg)
        elif T is Retract:
            logger.debug(f"- \t${msg}")
            self.ctx.remove(msg.data)
            return self.fire(msg)
        else:
            logger.debug(f"Eval:\t{msg}")
            return self.fire(msg)

    def fire(self, msg):
        for m in msg.sender.matchRules(msg):
            logger.debug(f"Fire:\t{m}:")
            #self.schedule(m.to)
            self.schedule(m.rule.action)

    async def main(self, msg=None):
        t = None
        status = None
        post = None
        logger.debug(f"@main {self.id}")
        logger.debug('eval tasks')
        if len(self.queue) != 0:
            t = self.queue.pop(0)
            while t:
                logger.debug(f"Tick:\t({t.constructor.name}) {t.msg}")
                status = t.action()
                if status == TS_RUNNING:
                    self.queue.append(t)
                elif t.parent:
                    pStatus = t.parent.strategy(t)
                    if pStatus == TS_RUNNING:
                        self.queue.append(t.parent)
                elif t.caller:
                    t.caller.resume()
                    self.queue.append(t.caller)

                t = self.queue.pop(0)

        logger.debug('eval posts')

        posts = self.posts
        self.posts = []
        for post in posts:
            self.dispatch(post)

        if self.idle() and self.impasse() and not self.scheduled:
            for msg in self.proposals:
                for m in msg.sender.matchRules(msg):
                    self.fork(m.to)

        self.proposals = []
        #self.resolve()
        self.status = TS_SUCCESS

        return self.status

    def idle(self):
        return len(self.posts) == 0 and len(self.queue) == 0 and len(self.tasks) == 0

    def signal (self, trigger, task):
        console.log(trigger.verb)
        self.signals.get(trigger.verb).append(task)

    def impasse(self):
        if self.impassed:
            return true 
        logger.debug(f"@impasse {self.id}")
        self.impassed = True
        self.post(Attempt(Achieve(None, _impasse, None)))
        #self.schedule(self)
        return False
    '''
    def run(self, **queue):
        for task in queue:
            self.schedule(task)
        return self.main()
    '''

Bot_ = lambda before: Bot(before)
