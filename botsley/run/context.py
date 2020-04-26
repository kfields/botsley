from botsley.run import term_, Believe, clause_

# {Query} = require('./query');


class Context:
    def __init__(self, clauses=[]):
        self.clauses = clauses

    def __iter__(self):
        yield from self.clauses

    def copy(self):
        other = Context(self.clauses.slice())
        return other

    def load(self, loader):
        return loader.load(self)

    def config(self, cfg):
        if not cfg:
            return self
        for k in cfg:
            v = cfg[k]
            if k == "clauses":
                for c in v:
                    self.add(c)
                break
            else:
                self[k] = v
        return self

    def add(self, c):
        if type(c) is list:
            self.clauses = self.clauses.concat(c)
            return self.clauses
        else:
            return self.clauses.append(c)

    def remove(self, clause):
        self.clauses = self.clauses.filter(
            lambda value, index, arr: notvalue.isEqual(clause)
        )
        return self

    def believe(self, s, v, o, x):
        self.add(Believe(s, v, o, x))
        return self

    def exists(self, t, s, v, o, x):
        for c in self.clauses:
            if c.match(t, s, v, o, x):
                return True
        return False

    def find(self, t, s, v, o, x):
        result = []
        for c in self.match(t, s, v, o, x):
            result.push(c)
        return result

    def match(self, t, s, v, o, x):
        for c in self.clauses:
            if c.match(t, s, v, o, x):
                yield c

    """
    def query(self, t, s, v, o, x):
        return Query(self).and(t, s, v, o, x)
    """

    def __repr__(self):
        result = ""
        for c in self.clauses:
            result += str(c) + "\n"
        return result

    def fromJSON(self, json):
        for k in json:
            v = json[k]
            t = v.type
            subj = term_(k, t)
            for vk in v:
                vv = v[vk]
                verb = term_(vk)
                if type(vv) is list:
                    for obj in vv:
                        self.believe(subj, verb, term_(obj))
                else:
                    self.believe(subj, verb, term_(vv))


context_ = lambda cfg: Context().config(cfg)
