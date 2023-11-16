from typing import Any, Callable, List, Optional, Union, Coroutine

import inspect
from copy import copy

from botsley.run.behavior import Behavior
from botsley.run.policymeta import PolicyMeta
from .essentials import Message


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

    def match(self, msg: Message):
        result = self.trigger.match(msg)
        if not result:
            return False
        m = copy(msg)
        m.rule = self
        return m


#
# Policy
#
class Policy(Behavior, metaclass=PolicyMeta):
    def __init__(self):
        super().__init__()
        self.rules: List[Rule] = self.__class__.rules

    def add(self, r: Rule):
        self.rules.append(r)

    def remove(self, r: Rule):
        try:
            self.rules.remove(r)
        except ValueError as e:
            print(e)
            exit()
        return self


    def subscribe(self, trigger, action):
        rule = Rule(trigger, action)
        self.add(rule)
        return rule

    def unsubscribe(self, rule):
        self.remove(rule)

    def find(self, msg: Message):
        result = []
        for r in self.rules:
            if r.match(msg):
                result.append(r)

        policy: Policy = self.parent
        while policy:
            rules = policy.find(msg)
            result = result.extend(rules)
            policy = policy.parent
        return result

    def match(self, msg):
        for r in self.rules:
            m = r.match(msg)
            if m:
                print("rule match", r, m)
                yield m

        policy: Policy = self.parent
        while policy:
            yield from policy.match(msg)
            policy = policy.parent

    @classmethod
    def __build_rules(cls, functions) -> List[Rule]:
        rules = []
        for name, func in functions:
            rule = _build_rule(func)
            rules.append(rule)
        return rules

    @classmethod
    def __collect_functions(cls, definitions) -> List[Callable]:
        functions = [
            (name, value)
            for name, value in definitions
            if callable(value) and hasattr(value, "triggers")
        ]
        return functions

    @classmethod
    def _build(cls, definitions):
        if vars(cls).get("_build", False):
            return

        # Collect all of the rule functions from the class definition
        functions = cls.__collect_functions(definitions)
        # print('functions')
        # print(functions)

        cls.rules = cls.__build_rules(functions)


def _build_rule(func: Callable):
    triggers = []
    prodname = func.__name__
    unwrapped = inspect.unwrap(func)
    filename = unwrapped.__code__.co_filename
    lineno = unwrapped.__code__.co_firstlineno
    for trigger, lineno in zip(
        func.triggers, range(lineno + len(func.triggers) - 1, 0, -1)
    ):
        print("trigger")
        print(trigger)
        triggers.append(trigger)

    rule = Rule(triggers[0], func, prodname=prodname, filename=filename, lineno=lineno)
    print("rule")
    print(rule)
    return rule
