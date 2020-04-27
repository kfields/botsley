from botsley.run import *

class Query:
    def __init__(self, ctx):
        self.ctx = ctx
        self.conds = []
        self.success = False
        self.failure = False

    def totalFailure(self):
        return self.state.failure and not self.state.success

    def add(self, c):
        c.query = self
        c.ctx = self.ctx
        return self.conds.append(c)

    def _and(self, t, s, v, o=None, x=None):
        cond = QClause(t, s, v, o, x)
        src = self.conds[-1] if len(self.conds) > 0 else None
        cond.src = src
        self.add(cond)
        return self

    def _not(self, t, s, v, o=None, x=None):
        cond = QNegClause(t, s, v, o, x)
        src = self.conds[-1]
        if src:
            cond.src = src
        self.add(cond)
        return self

    def filter(self, fn):
        cond = QFilter(fn)
        src = self.conds[-1]
        if src:
            cond.src = src
        self.add(cond)
        return self

    def binders(self):
        yield from self.conds[-1].binders()

    def exec(self, onSuccess):
        for binder in self.binders():
            return onSuccess(binder)

query_ =  lambda ctx: Query(ctx)

class Condition:
    def blank(self):
        yield {}

    def bound(self, b, v):
        if b[v.name]:
            return True
        return False

    def binding(self, b, v):
        if v:
            return b.get(v.name)
        return None

class QFilter(Condition):
    def __init__(self, fn):
        super().__init__()
        self.fn = fn

    def binders(self):
        source = None
        if self.src:
            source = self.src.binders()
        else:
            source = self.blank()
        for binder in source:
            if self.fn(binder):
                yield binder

class QClause(Condition):
    def __init__(self, t, s, v, o=None, x=None):
        super().__init__()
        self.t = t
        self.s = s
        self.v = v
        self.o = o
        self.x = x
        self.src = None

    def binders(self):
        source = None
        if self.src:
            source = self.src.binders()
        else:
            source = self.blank()
        
        for binder in source:
            s = self.binding(binder, self.s) or self.s
            o = self.binding(binder, self.o) or self.o
            if isinstance(s, Variable):
                if isinstance(o, Variable):
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        result = {s.name: c.subj, o.name: c.obj}
                        result.update(binder)
                        yield result

                else:
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        result = {s.name: c.subj}
                        result.update(binder)
                        yield result

            else:
                if isinstance(o, Variable):
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        result = {o.name: c.obj}
                        result.update(binder)
                        yield result

                else:
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        yield binder


class QNegClause(Condition):
    def __init__(self, t, s, v, o, x):
        super().__init__()
        self.t = t
        self.s = s
        self.v = v
        self.o = o
        self.x = x

    def binders(self):
        source = None
        if self.src:
            source = self.src.binders()
        else:
            source = self.blank()

        for binder in source:
            s = self.binding(binder, self.s) or self.s
            o = self.binding(binder, self.o) or self.o
            if isinstance(s, Variable):
                if isinstance(o, Variable):
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        result = {s.name: c.subj, o.name: c.obj}
                        result.update(binder)
                        yield result

                else:
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        result = {s.name: c.subj}
                        result.update(binder)
                        yield result
            else:
                if isinstance(o, Variable):
                    for c in self.ctx.match(self.t, s, self.v, o, self.x):
                        result = {o.name: c.obj}
                        result.update(binder)
                        yield result
                else:
                    if not self.ctx.exists(self.t, s, self.v, o, self.x):
                        yield binder
