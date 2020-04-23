import inspect

from botsley.run.taskmeta import TaskMeta
from botsley.run.policy import Policy
from botsley.run.main import term_, Term, Message, Propose, Attempt, Assert, Retract, Achieve


TS_RUNNING = 'Running'
TS_SUCCESS = 'Success'
TS_FAILURE = 'Failure'
TS_SUSPENDED = 'Suspended'
TS_HALTED = 'Halted'

class Task(Policy):
  def __init__(self, init):
    super().__init__()
    self.id = uuidv1()
    self.init = init
    self.bot = None
    self._msg = None
    self._parent = None
    self.tasks = []
    self.result = None
    self.status = TS_RUNNING
    self.policy = self

  def toJSON(self):
    return {
      TYPE: self.__class__.__name,
      MSG: self.msg
    }

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

  def strategy(self, child):
      if child.status == TS_FAILURE:
        self.remove(child)
        return self.fail()
      elif child.status == TS_SUCCESS:
        self.remove(child)
        if (tasks.length == 0):
            return self.succeed()

  def add(self, child):
    child.parent = self
    self.tasks.push(child)
    return self

  def remove(self, child):
    index = self.tasks.indexOf(child)
    if index > -1:
      self.tasks.splice(index, 1)
    return self

  #
  # EXECUTION
  #

  def init(self):
    if self.main:
      self.action = self.main
      self.status = self.action()
    return self.status

  def action(self):
    if inspect.isgeneratorfunction(self.init):
      gen = self.init()
      def action(self) {
        result = next(gen)
        self.status = toStatus(result.value)
        return self.status
      }
      self.action = action
      return self.status = toStatus(self.action())
    else:
      self.status = toStatus(self.init())
      if self.main:
        self.action = self.main
        self.status = toStatus(self.action())
      return self.status

  def schedule(self, t):
    if t.scheduled:
        return t
    t.scheduled = True
    def tick() {
      t.scheduled = False
      try:
        return t.status = toStatus(t.action())
      except err:
        return t.reject(err)

        loop = asyncio.get_event_loop()
        loop.create_task(tick)
    return t

  #DSL
  def chain(self, b):
    a = self.tasks[self.tasks.length - 1]
    if (a):
      a.dst = b
      b.src = a
    self.add(b)
    return self

  def task(self, action):
    child = Task(action)
    self.add(child)
    return self

  def loop(self, action):
    child = Loop(action)
    self.add(child)
    return self

  def counter(self, start, stop, action):
    child = Counter(start, stop, action)
    self.add(child)
    return self

  def sequence(self, action):
    child = Sequence(action)
    self.add(child)
    return self

  def suspend(self):
    return self.status = TS_SUSPENDED

  def resume(self):
    return self.status = TS_RUNNING

  def succeed(self):
    return self.status = TS_SUCCESS

  def fail(self):
    return self.status = TS_FAILURE

  def halt(self):
    if (self.bot):
      self.bot.halt()

    return self.status = TS_HALTED

  def broadcast(self, msg):
      pass

  def post(self, msg):
    msg.from = self
    return self.bot.post(msg)

  def spawn(self, o, wait=False):
    task = None
    if type(o, function):
      task = Task(o)
    elif isinstance(o, Task):
      task = o
    else:
        raise Error('Expecting Function or Task')
    if wait:
      task.caller = self

    return self.bot.schedule(task)

  def call(self, s, p, o, x):
    c = Achieve(s, p, o, x)
    m = Attempt(c, self)
    m.caller = self
    self.post(m)
    return self.suspend()

  def perform(self, s, p, o, x):
    c = Achieve(s, p, o, x)
    m = Attempt(c, self)
    return self.post(m)

  def propose(self, c):
    return self.post(Propose(c, self))

  def attempt(self, c):
    return self.post(Attempt(c, self))

  def assert(self, c):
    return self.post(Assert(c, self))

  def retract(self, c) {
    return self.post(Retract(c, self))

task_ = lambda action: Task(action)
#
class Impostor(Task):
  def __init__(self, identity, action):
    super().__init__(action)
    self.identity = identity

  def define(self, trigger, action):
      return self.identity.define(trigger, action) }

#
class Chain(Task):
  def __init__(self, action):
    super().__init__(action)

  def main(self):
    child = self.tasks[0]
    self.bot.schedule(child)
    return self.suspend()

  def strategy(self, child):
    self.remove(child)
    if child.status == TS_FAILURE):
      return self.fail()
    if child.dst:
      return self.bot.schedule(child.dst)


chain_ = lambda action: Chain(action)

class Parallel(Task):
  def __init__(self, action):
    super(action)

  def main():
    for child in self.tasks):
      self.bot.schedule(child)

    return self.suspend()

  def strategy(self, child):
    self.remove(child)
    if child.status == TS_FAILURE:
      return self.fail()
    #else
    return self.resume()

#
#Loop
#
class Loop(Task):
  def __init__(self, action):
    super().__init__(action)

  def main(self):
    child = self.tasks.shift()
    self.tasks.push(child)
    #else
    self.bot.schedule(child)
    return self.suspend()

  def strategy(self, child):
    if child.status == TS_FAILURE:
      return self.fail()
    #else
    return self.resume()

#
#Counter
#
class Counter(Task):
  def __init__(start, stope, action):
    super().__init__(action)
    self.value = start
    self.stop = to
    self.index = 0

  def main(self):
    child = self.tasks[self.index]
    if not child:
      child = self.tasks[(self.index = 0)]

    self.bot.schedule(child)
    return self.suspend()

  def strategy(self, child):
    self.index += 1
    if child.status == TS_FAILURE:
      return self.fail()
    #else
    if self.value + 1 == self.to:
      return self.succeed()
    #else
    return self.resume()

#
#Sequence
#
class Sequence(Task):
  def __init__(self, action):
    super(action)

  def main():
    child = self.tasks.shift()
    if child == None:
      return self.succeed()
    #else
    self.bot.schedule(child)
    return self.suspend()

  def strategy(self, child):
    if child.status == TS_FAILURE:
      return self.fail()
    #else
    if self.tasks.length > 0:
      return self.resume()
    #else
    return self.succeed()

#
# Method
#
class Method(Sequence):
    pass

method_ = lambda action: Method(action)

#
#Module
#
class Module(Method):
    pass

module_ = lambda action: Module(action)

#
#Rule
#
class Rule:
  def __init__(self, trigger, action, produce=lambda action: Method(action)):
    self.trigger = trigger
    self.action = action
    self.produce = produce

  def match(self, msg):
    result = self.trigger.match(msg)
    if not result:
        return false
    #t = Method(self.action)
    t = self.produce(self.action)
    m = clone(msg, result)
    m.rule = self
    m.to = t
    t.msg = m
    t.caller = m.caller
    return m

define = lambda t, a: Rule(t, a)

sequence_ = lambda action: Sequence(action)

counter_ = lambda start, stop, action: Counter(start, stop, action)

parallel_ = lambda action: Parallel(action)
