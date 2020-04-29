from botsley.run.task import *

#
# Context Management
#
PARENT = "parent"

ctx_parent = contextvars.ContextVar("ctx_parent", default=None)


def ctx_enter(child):
    parent = ctx_parent.get()
    if parent:
        child.parent = parent
        child.bot = parent.bot
        parent.add(child)

    ctx_parent.set(child)
    return {PARENT: parent}


def ctx_exit(ctx):
    ctx_parent.set(ctx[PARENT])

class Behavior(Task):
    def __init__(self, action=None, msg=None):
        super().__init__(action, msg)

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

    def propose(self, c):
        return self.post(Propose(c, self))

    def attempt(self, c):
        return self.post(Attempt(c, self))

    def declare(self, c):
        return self.post(Assert(c, self))

    def retract(self, c):
        return self.post(Retract(c, self))

    def perform(self, s, p, o, x):
        c = Achieve(s, p, o, x)
        m = Attempt(c, self)
        return self.post(m)

    def call(self, s, p, o, x):
        c = Achieve(s, p, o, x)
        m = Attempt(c, self)
        m.caller = self
        self.post(m)
        return self.suspend()


#
# Sensor
#
class Sensor(Behavior):
    pass


@contextmanager
def sensor():
    task = Sensor()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


sensor_ = lambda: Sensor()

#
# Condition
#
class Condition(Behavior):
    async def main(self, msg=None):
        for child in self.children:
            result = await child
            if result == TS_FAILURE:
                return self.fail()

@contextmanager
def condition(task=None):
    if not task:
        task = Condition()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


condition_ = lambda: Condition()

#
# Action
#
class Action(Behavior):
    pass


@contextmanager
def action(task=None):
    if not task:
        task = Action()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


action_ = lambda action: Action(action)


#
# Sequence
#
class Sequence(Behavior):
    def __init__(self):
        super().__init__()

    async def main(self, msg=None):
        for child in self.children:
            result = await child
            if result == TS_FAILURE:
                return self.fail()


@contextmanager
def sequence():
    task = Sequence()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


#
# Selector
#
class Selector(Behavior):
    def __init__(self):
        super().__init__()
    '''
    async def main(self, msg=None):
        for child in self.children:
            result = await child
    '''
    async def main(self, msg=None):
        while True:
            for child in self.children:
                result = await child
                if result == TS_SUCCESS:
                    break
            else:
                self.fail()

@contextmanager
def selector():
    task = Selector()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)

#
# Loop
#
class Timer(Behavior):
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
def timer(timeout):
    task = Timer(timeout)
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


#
# Loop
#
class Loop(Behavior):
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
def loop():
    task = Loop()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


#
# Counter
#
class Counter(Behavior):
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
def counter(start, stop):
    task = Counter(start, stop)
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)


#
# Parallel
#
class Parallel(Behavior):
    def __init__(self):
        super().__init__()

    async def main(self, msg=None):
        for child in self.children:
            self.schedule(child)
        return self.suspend()


@contextmanager
def parallel():
    task = Parallel()
    ctx = ctx_enter(task)
    yield task
    ctx_exit(ctx)

#
# Root
#
class Root(Parallel):
    pass

@contextmanager
def root(bot=None):
    task = Root()
    task.bot = bot
    ctx = ctx_enter(task)
    yield task
    bot.tree = task
    ctx_exit(ctx)


#
# Chain
#
class Chain(Behavior):
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
