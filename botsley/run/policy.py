import inspect
from copy import copy
from botsley.run.policymeta import PolicyMeta

#
# Rule
#
class Rule:
    def __init__(self, trigger, action, prodname=None, filename=None, lineno=None):
        self.trigger = trigger
        self.action = action
        self.prodname = prodname
        self.filename = filename
        self.lineno = lineno

    def match(self, msg):
        result = self.trigger.match(msg)
        if not result:
            return False
        m = copy(msg)
        m.rule = self
        return m


define = lambda t, a: Rule(t, a)

#
# Policy
#
class Policy(metaclass=PolicyMeta):
    def __init__(self):
        self.parent = None
        #self.rules = []
        self.rules = self.__class__.rules

    def add(self, r):
        self.rules.append(r)

    def find(self, msg):
        result = []
        for r in self.rules:
            if r.match(msg):
                result.append(r)

        policy = self.parent
        while policy:
            rules = policy.find(msg)
            result = result.concat(rules)
            policy = policy.parent
        return result

    def match(self, msg):
        for r in self.rules:
            m = r.match(msg)
            if m:
                print('rule match', r, m)
                yield m

        policy = self.parent
        while policy:
            yield from policy.match(msg)
            policy = policy.parent

    @classmethod
    def __build_rules(cls, functions):
        rules = []
        errors = ''
        for name, func in functions:
            rule = _build_rule(func)
            rules.append(rule)
        return rules

    @classmethod
    def __collect_functions(cls, definitions):
        '''
        Collect all of the tagged grammar rules
        '''
        rules = [ (name, value) for name, value in definitions
                  if callable(value) and hasattr(value, 'triggers') ]
        return rules

    @classmethod
    def _build(cls, definitions):
        if vars(cls).get('_build', False):
            return

        # Collect all of the rule functions from the class definition
        functions = cls.__collect_functions(definitions)
        #print('functions')
        #print(functions)

        cls.rules = cls.__build_rules(functions)

def _build_rule(func):
    triggers = []
    prodname = func.__name__
    unwrapped = inspect.unwrap(func)
    filename = unwrapped.__code__.co_filename
    lineno = unwrapped.__code__.co_firstlineno
    for trigger, lineno in zip(func.triggers, range(lineno+len(func.triggers)-1, 0, -1)):
        print('trigger')
        print(trigger)
        triggers.append(trigger)

    rule = Rule(triggers[0], func, prodname=prodname, filename=filename, lineno=lineno)
    print('rule')
    print(rule)
    return rule
