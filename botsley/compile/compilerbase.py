from botsley.compile.ast.visitor import AstVisitor

class State(object):
    def __init__(self, classDef):
        self.classDef = classDef

class CompilerBase(AstVisitor):
    def __init__(self, parent=None, iterable=(), **kwargs):
        super().__init__(parent, iterable, **kwargs)
        #self.policies = policies
        self.out = []
        self.indentlevel = 0
        self.indentation = ''
        self.states = []
        #
        self.classDef = None

    def compile(self, ast):
        self.visit(ast)

    def save(self):
        state = State(self.classDef)
        self.states.append(state)

    def restore(self):
        state = self.states.pop()
        self.classDef = state.classDef

    def write(self, s):
        print(self.indentation + s)

    def writeLn(self, s=''):
        '''
        if not self.out
            return
        return this.out.write(this.indentation + s + '\n');
        '''
        print(self.indentation + s)

    def indent(self):
        self.indentlevel += 1
        self.indentation = ' ' * (self.indentlevel + 1) * 4
        
    def dedent(self):
        self.indentlevel -= 1
        self.indentation = ' ' * (self.indentlevel + 1) * 4
        
