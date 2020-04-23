from json import JSONEncoder

from botsley.compile.ast.metanode import MetaNode

KIND = "KIND"
NAME = "NAME"
TYPE = "TYPE"
NODES = "NODES"
SUBJ = "SUBJ"
VERB = "VERB"
OBJ = "OBJ"
XTRA = "XTRA"
TRIGGER = "TRIGGER"
BODY = "BODY"
FLAVOR = "FLAVOR"
BINDING = "BINDING"
VALUE = "VALUE"
ARG = "ARG"

_terms = {}
_types = {}


class AstEncoder(JSONEncoder):
    def default(self, o):
        return o.toJSON()


class Node(object, metaclass=MetaNode):
    def __init__(self, kind=None):
        super().__init__()
        self.kind = kind or self.__class__.__name__
        self.nodes = [None] * self.nodeCount
        self.type = None
        self.scope = None
        self.binding = None

    def add(self, child):
        # child.parent = self
        return self.nodes.append(child)

    def remove(self, child):
        index = self.nodes.indexOf(child)
        if index > -1:
            return self.nodes.splice(index, 1)

    def walk(self, fn):
        fn.apply(self)
        return self.nodes.map(lambda child: child.walk(fn))

    def __next__(self):
        for node in self.NODES:
            yield node


class Array(Node):
    def __init__(self, nodes):
        super().__init__()
        self.nodes = nodes

    def toJSON(self):
        return {KIND: self.kind, TYPE: self.type, NODES: self.nodes}


class Property(Node):
    def __init__(self, name, val):
        super.__init__()
        self.name = name
        self.value = val

    def toJSON(self):
        return {KIND: self.kind, NAME: self.name, VALUE: self.value}


class Properties(Node):
    def __init__(self, child):
        super().__init__()
        self.add(child)


class Variable(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.info = None

    def toJSON(self):
        return {KIND: self.kind, NAME: self.name, TYPE: self.type, INFO: self.info}


class Term(Node):
    def __init__(self, name, kind="Term"):
        super().__init__(kind)
        self.name = name

    def toJSON(self):
        return {KIND: self.kind, NAME: self.name, TYPE: self.type}


def term_(name):
    term = _terms.get(name)
    if not term:
        term = Term(name)
        _terms[name] = term
    return term


class Type(Term):
    def __init__(self, name):
        super().__init__(name, "Type")
        self.builtin = False

    def toJSON(self):
        return {KIND: self.kind, NAME: self.name}


def type_(name):
    t = _types.get(name)
    if not t:
        t = Type(name)
        _types[name] = t
    return t


def builtin_(name):
    t = type_(name)
    t.builtin = True
    return t


_Goal = builtin_("Goal")
_Achieve = builtin_("Achieve")
_Believe = builtin_("Believe")
#


class Literal(Node):
    def __init__(self, value):
        super().__init__("Literal")
        self.value = value

    def toJSON(self):
        return {KIND: self.kind, VALUE: self.value}


_null = Literal("null")
#


class ExprList(Node):
    def __init__(self, child, kind="ExprList"):
        super().__init__(kind)
        if child:
            self.add(child)


class Block(ExprList):
    def __init__(self, child, kind="Block"):
        super().__init__(child, kind)

    def toJSON(self):
        return {KIND: self.kind, NODES: self.nodes}


#
# Module
#
class Module(Block):
    def __init__(self, child):
        super().__init__(child, "Module")


class Snippet(Node):
    def __init__(t):
        super().__init__()
        t = t.slice(1)
        t = t.trim()
        self.text = t

    def toJSON(self):
        return {KIND: self.kind, text: self.text}


class Code(Node):
    def __init__(self, t):
        super().__init__()
        t = t.substring(1, t.length - 1)
        t = t.trim()
        self.text = t

    def toJSON(self):
        return {KIND: self.kind, text: self.text}


class Paragraph(Node):
    Node.node("subj")
    Node.node("list")

    def __init__(self, subj, arr):
        super().__init__()
        self.subj = subj
        self.list = arr

    def toJSON(self):
        return {KIND: self.kind, TYPE: self.type, SUBJ: self.subj, LIST: self.list}


class Sentence(Node):
    Node.node("clause")
    Node.node("list")

    def __init__(self, clause, arr):
        super().__init__()
        self.clause = clause
        self.list = arr

    def toJSON(self):
        return {KIND: self.kind, TYPE: self.type, clause: self.clause, LIST: self.list}


class Clause(Node):
    Node.node("subj")
    Node.node("verb")
    Node.node("obj")

    def __init__(self, subj, verb, obj, t=type_("Believe")):
        super().__init__()
        self.subj = subj
        self.verb = verb
        self.obj = obj
        self.type = t
        self.xtra = None
        self.binding = None

    def toJSON(self):
        return {
            KIND: self.kind,
            TYPE: self.type,
            SUBJ: self.subj,
            VERB: self.verb,
            OBJ: self.obj,
            XTRA: self.xtra,
        }


class Trigger(Node):
    def __init__(self, arg):
        super().__init__()
        msg = None
        if isinstance(arg, Clause):
            clause = arg
            if not clause.subj:
                clause.type = type_("Achieve")
                msg = Attempt(clause)
            else:
                clause.type = type_("Believe")
                msg = Assert(clause)
        else:
            msg = arg

        self.flavor = msg.type
        expr = msg.arg
        self.type = expr.type
        if isinstance(expr, Clause):
            self.subj = expr.subj
            self.verb = expr.verb
            self.obj = expr.obj
            self.xtra = expr.xtra
            self.binding = expr.binding
        elif isinstance(expr, Variable):
            self.binding = expr

    def toJSON(self):
        return {
            KIND: self.kind,
            FLAVOR: self.flavor,
            TYPE: self.type,
            SUBJ: self.subj,
            VERB: self.verb,
            OBJ: self.obj,
            XTRA: self.xtra,
            BINDING: self.binding,
        }


class UnaryExpr(Node):
    Node.node("arg")

    def __init__(self, arg, kind="UnaryExpr"):
        super().__init__(kind)
        self.arg = arg

    def toJSON(self):
        return {KIND: self.kind, ARG: self.arg}


class PrefixExpr(UnaryExpr):
    def __init__(self, arg, kind="PrefixExpr"):
        super().__init__(arg, kind)


#
# Messages
#
_Propose = builtin_("Propose")
_Attempt = builtin_("Attempt")
_Assert = builtin_("Assert")
_Retract = builtin_("Retract")


class Message(PrefixExpr):
    def __init__(self, arg, t=_Assert):
        super().__init__(arg, "Message")

        self.type = t
        if isinstance(arg, Clause):
            clause = arg
            if not clause.subj:
                clause.type = type_("Achieve")

    def toJSON(self):
        return {KIND: self.kind, TYPE: self.type, ARG: self.arg}


class Propose(Message):
    def __init__(self, arg):
        super().__init__(arg, _Propose)


class Attempt(Message):
    def __init__(self, arg):
        super().__init__(arg, _Attempt)


class Assert(Message):
    def __init__(self, arg):
        super().__init__(arg, _Assert)


class Retract(Message):
    def __init__(self, arg):
        super(arg, _Retract)


class PostfixExpr(UnaryExpr):
    def __init__(self, arg, kind="PostfixExpr"):
        super().__init__(arg, kind)


class BinaryExpr(Node):
    Node.node("left")
    Node.node("right")

    def __init__(self, left, right, kind="BinaryExpr"):
        super().__init__(kind)
        self.left = left
        self.right = right

    def toJSON(self):
        return {KIND: self.kind, op: self.op, left: self.left, right: self.right}


class Contextualize(Node):
    Node.node("left")
    Node.node("right")

    def __init__(self, left, right):
        super().__init__("Contextualize")
        self.left = left
        self.right = right

    def toJSON(self):
        return {KIND: self.kind, left: self.left, right: self.right}


class Statement(Node):
    def __init__(self, kind="Statement"):
        super().__init__(kind)

    def toJSON(self):
        return {KIND: self.kind}


class Def(Statement):
    Node.node("trigger")
    Node.node("body")

    def __init__(self, trigger, body, kind="Def"):
        super().__init__(kind)
        self.trigger = trigger
        self.body = body

    def toJSON(self):
        return {KIND: self.kind, TRIGGER: self.trigger, BODY: self.body}


class Sig(Def):
    def __init__(self, trigger, body):
        super(trigger, body, "Sig")


class ImportStmt(Statement):
    def __init__(self, expr):
        super().__init__("ImportStmt")
        self.expr = expr

    def toJSON(self):
        return {KIND: self.kind, expr: self.expr}


#
class Query(Statement):
    Node.node("lhs")
    Node.node("rhs")

    def __init__(self, lhs, rhs):
        super().__init__("Query")
        self.lhs = lhs
        self.rhs = rhs

    def toJSON(self):
        return {KIND: self.kind, lhs: self.lhs, rhs: self.rhs}


class Condition(Node):
    Node.node("expr")

    def __init__(self, expr, kind="Condition"):
        super().__init__(kind)
        self.expr = expr

    def toJSON(self):
        return {KIND: self.kind, expr: self.expr}


class QClause(Condition):
    def __init__(self, expr):
        super.__init__(expr, "QClause")


class QNegClause(Condition):
    def __init__(expr):
        super().__init__(expr, "QNegClause")


class QFilter(Condition):
    def __init__(self, expr):
        super().__init__(expr, "QFilter")


class Lhs(ExprList):
    def __init__(self, child, kind):
        super().__init__(child, "Lhs")


class Rhs(Block):
    def __init__(self, child, kind):
        super(child, "Rhs")


#
# Actions
#
class Actions(Node):
    def __init__(self, body, kind):
        super().__init__(self, kind)
        self.body = body

    def toJSON(self):
        return {KIND: self.kind, BODY: self.body}


#
class Action(Node):
    def __init__(self, expr, kind="Action"):
        super().__init__(kind)
        self.expr = expr

    def toJSON(self):
        return {KIND: self.kind, expr: self.expr}


#
class Return(Node):
    def __init__(expr):
        super().__init__("Return")
        self.expr = expr

    def toJSON(self):
        return {KIND: self.kind, expr: self.expr}


class Halt(Node):
    def __init__(self, expr):
        super().__init__("Halt")
        self.expr = expr

    def toJSON(self):
        return {KIND: self.kind, expr: self.expr}
