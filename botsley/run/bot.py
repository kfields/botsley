from copy import copy
from uuid import uuid1
from loguru import logger

from botsley.run import *
from botsley.run import _impasse
from botsley.run.behavior import *
from botsley.run.context import Context
from botsley.run.policy import Policy

class Bot(Policy):
    def __init__(self):
        super().__init__()
        self.policy: Policy = self
        self.id = uuid1()
        self.ctx = Context()
        self.tasks: List[Task] = []
        self.posts: List[Message] = []
        self.proposals: List[Message] = []
        self.scheduled: bool = False
        self.impassed: bool = False
        self.signals = None
        self._tree: Task = None

    @property
    def tree(self) -> Task:
        return self._tree

    @tree.setter
    def tree(self, tree: Task):
        self._tree = tree
        self.schedule(tree)

    def broadcast(self, msg: Message):
        m = copy(msg)
        logger.debug(f"Broadcast:\t{m}")
        m.sender = self
        self.post(m)
        return map(self.tasks, lambda t: t.broadcast(m))

    def post(self, msg: Message):
        if not msg.sender:
            msg.sender = self
        logger.debug(f"Post:\t{msg}")
        return self.posts.append(msg)

    def fork(self, t: Task):
        logger.debug(f"Fork:\t{t.msg}")
        child = Bot()
        child.policy = self.policy
        child.ctx = self.ctx.copy()
        return child.run(t)

    def dispatch(self, msg: Message):
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

    def fire(self, msg: Message):
        for m in msg.sender.matchRules(msg):
            logger.debug(f"Fire:\t{m}:")
            self.schedule(m.rule.action, m)

    async def main(self, msg=None):
        logger.debug(f"@main {self.id}")

        posts = self.posts
        self.posts = []
        for post in posts:
            self.dispatch(post)

        if self.idle() and self.impasse() and not self.scheduled:
            for msg in self.proposals:
                for m in msg.sender.matchRules(msg):
                    self.fork(m.to)

        self.proposals = []
        self.status = TS_SUCCESS

        return self.status

    def idle(self):
        return len(self.posts) == 0 and len(self.tasks) == 0

    def signal (self, trigger, task):
        logger.debug(trigger.verb)
        self.signals.get(trigger.verb).append(task)
        
    def impasse(self):
        if self.impassed:
            return True 
        logger.debug(f"@impasse {self.id}")
        self.impassed = True
        self.post(Attempt(Achieve(None, _impasse, None)))
        #self.schedule(self)
        return False

Bot_ = lambda before: Bot(before)
