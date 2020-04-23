from typing import Pattern
import json


class Variable:
    def __init__(self, name, pattern):
        self.name = name
        self.pattern = pattern


def variable_(name, pattern):
    return Variable(name, pattern)


def match(p, v, b=True):
    if p == __ or p == v:
        return b
    if callable(p) and p(v):
        return b
    if isinstance(p, Pattern) and p.test(v):
        return b
    if isinstance(p, Variable):
        if p.pattern and not match(p.pattern, v):
            return False
        if type(b, object):
            b[p.name] = v
            return b
        return {[p.name]: v}

    return False


class Term:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name

    def toJSON(self):
        return {TYPE: self.constructor.name, NAME: self.name}


class Subject(Term):
    pass


class Verb(Term):
    pass


#
# Object to Term
#
terms = {}


def term_(arg, T=None):
    term = None
    if type(arg) is str:
        term = terms.get(arg)
        if not term:
            if not T:
                if arg[0].isupper():
                    T = Subject
                else:
                    T = Verb
            elif type(T) is str:
                T = eval(f"{type} = class {type} Term:")
            terms[arg] = term = T(arg)
    elif type(arg, object):
        term = {}
        for e in arg:
            n = "_" + e
            obj[n] = term_(e)
    return term


_I = term_("I")
_start = term_("start")
_impasse = term_("impasse")

#
# Clause
#


class Clause:
    def __init__(self, subj, verb, obj, **xtra):
        self.subj = subj
        self.verb = verb
        self.obj = obj
        for k in xtra:
            self[k] = xtra[k]

    def __repr__(self):
        xtra = []
        for k in self.__dict__:
            v = self.__dict__[k]
            if (k != "subj") and (k != "verb") and (k != "obj"):
                xtra.push(f"{k}: {v}")

        return " ".join(
            [
                self.__class__.__name__,
                str(self.subj),
                str(self.verb),
                str(self.obj),
                str(xtra),
            ]
        )

    def toJSON(self):
        return {
            TYPE: self.__class__.__name__,
            SUBJ: self.subj and JSON.stringify(self.subj),
            VERB: self.verb and JSON.stringify(self.verb),
            OBJ: self.obj and JSON.stringify(self.obj),
        }

    def match(self, T, s, v, o, x):
        return isinstance(self, T) and match(
            s, self.subj, match(v, self.verb, match(o, self.obj))
        )

    def isEqual(self, clause):
        return (
            self.__class__.__name__ == clause.__class__.__name__
            and self.subj == clause.subj
            and self.verb == clause.verb
            and self.obj == clause.obj
        )


clause_ = lambda T, s, v, o, x: T(s, v, o, x)
#
class Believe(Clause):
    pass


believe_ = lambda s, v, o, x: Believe(s, v, o, x)
#
class Goal(Clause):
    pass


#
class Achieve(Goal):
    pass


#
# Message
#
class Message:
    def __init__(self, data, sender=None, to=None):
        self.data = data
        self.sender = sender
        self.to = to

    def __repr__(self):
        return " ".join([self.__class__.__name__, str(self.data)])

    def toJSON(self):
        return {
            TYPE: self.__class__.__name__,
            DATA: self.data.toJSON(),
            TO: self.to and self.to.toJSON(),
            FROM: self.sender and self.sender.toJSON(),
        }

    def match(F, T, s, v, o, x):
        return isinstance(self, F) and self.data.match(T, s, v, o, x)


class Propose(Message):
    pass


propose_ = lambda T, s, v, o, x: Propose(T(s, v, o, x))


class Attempt(Message):
    pass


attempt_ = lambda T, s, v, o, x: Attempt(T(s, v, o, x))


class Assert(Message):
    pass


assert_ = lambda T, s, v, o, x: Assert(T(s, v, o, x))


class Retract(Message):
    pass


retract_ = lambda T, s, v, o, x: Retract(T(s, v, o, x))
#
# Trigger
#
class Trigger:
    def __init__(self, flavor, T, subj, verb, obj, xtra):
        self.flavor = flavor #message type
        self.type = T #clause type
        self.subj = subj
        self.verb = verb
        self.obj = obj
        self.xtra = xtra

    def match(m):
        return m.match(
            self.flavor, self.type, self.subj, self.verb, self.obj, self.xtra
        )


#
class OnAssert(Trigger):
    def __init__(self, T, s, v, o, x):
        super().__init__(Assert, T, s, v, o, x)


onAssert_ = lambda T, s, v, o, x: OnAssert(T, s, v, o, x)
#
class OnRetract(Trigger):
    pass


onRetract_ = lambda T, s, v, o, x: OnRetract(T, s, v, o, x)


class OnAttempt(Trigger):
    def __init__(self, T, s, v, o, x):
        super().__init__(Attempt, T, s, v, o, x or Achieve)


onAttempt_ = lambda T, s, v, o, x: OnAttempt(T, s, v, o, x)
