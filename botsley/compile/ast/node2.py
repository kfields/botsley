from json import JSONEncoder

class AstEncoder(JSONEncoder):
    def default(self, o):
        return o.toJSON()

class Node(object):
    def __init__(self):
        pass
        
class List(Node):
    def __init__(self, children=[]):
        self.children = children
    def push(self, child):
        self.children.append(child)
        
class Block(List):
    def __init__(self, children=[]):
        super(Block, self).__init__(children)
        self.kind = 'Block'
        
    def toJSON(self):
        return {'kind': self.kind, 'children': self.children}

class Class(Node):
    def __init__(self, name, block):
        self.kind = 'Class'
        self.name = name
        self.block = block
    def toJSON(self):
        return {'kind': self.kind, 'name': self.name, 'block': self.block}

class Method(Node):
    def __init__(self, name, trigger, block):
        self.kind = 'Method'
        self.name = name
        self.trigger = trigger
        self.block = block
    def toJSON(self):
        return {'kind': self.kind, 'name': self.name, 'trigger': self.trigger, 'block': self.block}
        
class Clause(Node):
    def __init__(self, subj, pred, obj):
        self.kind = 'Clause'
        self.subj = subj
        self.pred = pred
        self.obj = obj
    def toJSON(self):
        return {'kind': self.kind, 'subj': self.subj, 'pred': self.pred, 'obj': self.obj}

class Snippet(Node):
    def __init__(self, code):
        self.kind = 'Snippet'
        self.code = code
        
    def toJSON(self):
        return {'kind': self.kind, 'code': self.code}
        