from botsley.compile.compilerbase import CompilerBase
#from botsley.compile.policies.default import DefaultPolicy
import botsley.compile.ast.node as yy

class Compiler(CompilerBase):
    def __init__(self, options={ 'filename': None }):
        super().__init__(None, {
            "-->": self.Success,
            "!=>": self.TotalFailure,
            "=": self.BinaryExpr,
            "==": self.BinaryExpr,
            "!=": self.BinaryExpr,
            "instanceof": self.BinaryExpr
        })
        self.options = options

    def Paragraph(self, n):
        return ''.join([self.visit(c) for c in n.nodes])
        '''
        arr = []
        for c in n.list:
            arr.append(self.visit(c))
        return arr.join('')
        '''
    def Action(self, n):
        #print(n)
        result = self.visit(n.expr)
        if result:
            self.writeLn(result)

    def Array(self, n):
        return f"[ { str(self.visit(c)) for c in n.nodes } ]"
        '''
        arr = []
        for c in n.nodes:
            arr.append(self.visit(c))
        return [
            '[',
            arr.join(),
            ']'
        ].join('')
        '''
    def Return(self, n):
        self.writeLn(f"yield self.succeed({self.visit(n.expr)})")

    def Halt(self, n):
        self.writeLn(f"yield self.halt({self.visit(n.expr)})")

    def Snippet(self, n):
        self.writeLn(f"print({n.text})")

    def Code(self, n):
        if isinstance(self.top(-1), Block):
            self.writeLn(n.text)
        else:
            return n.text

    def Literal(self, n):
        return n.value

    def Variable(self, n):
        return '$' + n.name

    def Term(self, n):
        return '_' + n.name

    def Type(self, n):
        return n.name

    def Properties(self, n):
        return ''.join([self.visit(c) for c in n.nodes])
        '''
        arr = []
        for c in n.nodes:
            arr.append(self.visit(c))
        return [
            '{',
            arr,
            '}'
        ].join('')
        '''

    def Property(self, n):
        return ''.join([self.visit(c) for c in n.nodes])
        '''
        return [
            n.name, ': ',
            self.visit(n.value)
        ].join('')
        '''
    def Query(self, node):
        v = None
        if node.scope:
            for k in node.scope.vars:
                v = node.scope.vars[k]
                if (v.type):
                    self.writeLn(f"_${k} = new Variable('${k}', (v) => v instanceof {v.type.name})")
                elif v.qvar:
                    self.writeLn(f"_${k} = new Variable('${k}')")

        def Variable(self, n):
            v = self.scope.find(n.name)
            if v.qvar:
                return f"_.{n.name}"
            else:
                return self.visitVariable(n)

        self.policy_({
            Variable
        })
        return self.visit_node(node)

    def Block(self, node):
        if (node.scope):
            for k in node.scope.vars:
                v = node.scope.vars[k]
                val = v.value
                if not val:
                    val = 'undefined'
                    self.writeLn(f"${k} = {val}")
        return self.visit_node(node)

    def Module(self, n):
        k, v = None, None
        self.write('''\
from botsley.run import Context, Term, Goal, Believe, Achieve, Assert, Retract, Attempt
from botsley.run import __, term_, _$, module_, Message, Rule, Trigger, Variable, runner_\
'''
        )
        self.writeLn('')

        for k in yy._types:
            v = yy._types[k]
            if not v.builtin:
                self.writeLn(f"class {k}(Term)']")

        for k in yy._terms:
            v = yy._terms[k];
            if v.type:
                self.writeLn(f"_{k} = term_({k})({v.type.name})")
            else:
                self.writeLn(f"_{k} = term_({k})")

        self.writeLn()
        self.Block(n)

        if not self.options['filename']: #were running in a sandbox
            self.writeLn("runner_().run(module.exports)")
        else:
            self.writeLn("if (require.main == module) { runner_(module.exports).run() }")

    def Import(self, n):
        self.writeLn(f"require({n.expr.value}).action.call(self)")

    def Def(self, n):
        self.writeLn(f"@rule({self.visit(n.trigger)})")
        self.writeLn(f"def {n.trigger.verb.name}():")
        self.indent()
        self.visit(n.body)
        self.dedent()

    def Sig(self, n):
        self.writeLn(f"self.sig({self.visit(n.trigger)}, function*()")
        self.indent()
        self.visit(n.body)
        self.dedent()
        self.writeLn('});')

    def Trigger(self, node):
        self.save()
        def Variable(self, n):
            return '__'
        self.policy_({
            'Variable': Variable
        })
        return ''.join([
            'Trigger(',
            ', '.join([
                self.visit(node.flavor),
                self.visit(node.type),
                self.visit(node.subj) or '__',
                self.visit(node.verb) or '__',
                self.visit(node.obj) or '__',
                self.visit(node.xtra) or '__'
            ]),
            ')'
        ])

    def Message(self, n):
        arr = None
        if isinstance(n.arg, list):
            arr = n.arg
        else:
            arr = [n.arg]
        for c in arr:
            t = n.type
            if t == yy._Assert:
                self.writeLn(f"self.assert({self.visit(c)})")
            elif t == yy._Retract:
                self.writeLn(f"self.retract({self.visit(c)})")
            elif t == yy._Attempt:
                self.visitAttempt(n)
            elif t == yy._Propose:
                self.writeLn(f"self.propose({self.visit(c)})")

    def Attempt(self, n):
        header = 'self.perform(' if n.arg.slash else 'yield self.call('
        print(n)
        self.writeLn(''.join([
            header,
            ''.join([
                self.visit(n.arg.subj),
                self.visit(n.arg.verb),
                self.visit(n.arg.obj),
            ]),
            ')'
        ]))

    def Clause(self, n):
        return ''.join([
            self.visit(n.type),
            '(',
            ', '.join(filter(lambda x: x or None, [
                self.visit(n.subj),
                self.visit(n.verb),
                self.visit(n.obj),
                self.visit(n.xtra)
            ])),
            ')'
        ])

    def QClause(self, node):
        def Variable(n):
            if n.info.qvar:
                return '_$' + n.name
            else:
                return '$' + n.name

        self.policy_({
            Variable
        })
        c = node.expr
        header = "$query = self.bot.ctx.query(" if node.first else ".and("
        return self.writeLn(''.join([
            header,
            ''.join([
                self.visit(c.type),
                self.visit(c.subj),
                self.visit(c.verb),
                self.visit(c.obj)
            ]),
            ")"
        ])
        )

    def QNegClause(self, node):
        def Variable(n):
            if n.info.qvar:
                return '_$' + n.name
            else:
                return '$' + n.name
        self.policy_({
            Variable
        })
        c = node.expr
        header =  "$query = self.bot.ctx.query(" if node.first else ".not("
        return self.writeLn(''.join([
            header,
            ''.join([
                self.visit(c.type),
                self.visit(c.subj),
                self.visit(c.verb),
                self.visit(c.obj)
            ]),
            ")"
        ])
        )

    def QFilter(self, node):
        return self.writeLn(''.join([
            ".filter((_) => ",
            self.visit(node.expr),
            ")"
        ])
        )

    def Success(self, node):
        #self.writeLn(".exec((_) => {")
        self.writeLn('for (_ of $query.binders()) {')
        self.indent()
        self.visit(node.body)
        self.dedent()
        #self.writeLn('})')
        self.writeLn('}')

    def TotalFailure(self, node):
        #self.writeLn(".exec((_) => {")
        self.writeLn('if (!$query.binders().next()) {')
        self.indent()
        self.visit(node.body)
        self.dedent()
        #self.writeLn('})')
        self.writeLn('}')

    def UnaryExpr(self, n):
        return ''.join([
            f" {n.kind} ",
            self.visit(n.arg)
        ])

    def BinaryExpr(self, n):
        result = ''.join([
            self.visit(n.left),
            f" {n.kind} ",
            self.visit(n.right)
        ])
        if isinstance(self.top(-1), Block):
            self.writeLn(result)
        else:
            return result
