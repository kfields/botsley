import botsley.compile.visitor


class Var:
    def __init__(self, name, value, kind):
        self.name = name
        self.value = value
        self.kind = kind


class Scope:
    def __init__(self, parent):
        self.parent = parent
        self.vars = {}

    def add(self, v):
        k = v.name
        # if not self.vars[k]
        v1 = self.find(k)
        if v1:
            return v1

        self.vars[k] = v
        return v

    def find(self, k):
        v = self.vars[k]
        if v:
            return v
        if self.parent:
            return self.parent.find(k)


class AstVisitor(botsley.compile.visitor.Visitor):
    def __init__(self, parent=None, iterable=(), **kwargs):
        super().__init__(parent, iterable, **kwargs)
        self.states = []
        # State members
        self.scope = None
        self.block = None
        self.stmt = None
        self.subj = None
        self.value = None

    def scope_(self, node):
        if node.scope:
            self.scope = node.scope
        else:
            self.scope = Scope(self.scope)
            node.scope = self.scope
        return node

    def var_(self, k, v):
        return self.scope.add(k, {key: k, value: v})

    def qvar_(self, k, v):
        return self.scope.add(k, {key: k, value: v, qvar: true})

    def save(self):
        return self.states.append(
            {
                policy: self.policy,
                scope: self.scope,
                block: self.block,
                stmt: self.stmt,
                subj: self.subj,
                value: self.value,
            }
        )

    def restore(self):
        state = self.states.pop()
        self.policy, self.scope, self.block, self.stmt, self.subj, self.value = state
        return state

    def visit_node(self, node):
        result = None
        if node.scope:
            # self.save()
            self.scope = node.scope
            result = super().visit_node(node)
            # self.restore()
        else:
            result = super().visit_node(node)
        return result
