
import sly

from botsley.compile.lex.lexer import Lexer
from botsley.compile.ast.node import *

class Parser(sly.Parser):
    tokens = Lexer.tokens
    def __init__(self):
        super().__init__()
            
    @_('Root : ')
    def p_root_empty(self, p):
        return Block()

    @_('Root : Body')
    def p_root_body(self, p):
        return p[0]

    @_('Root : Block TERMINATOR')
    def p_root_block(self, p):
        p[0] = p[1]

    @_('Block : INDENT Body DEDENT')
    def p_block_body(self, p):
        #p[0] = p[2]
        return p[1]

    @_('Body : Line')
    def p_body_line(self, p):
        return Block([p[0]])

    @_('Body : Body TERMINATOR Line')
    def p_body_body_line(self, p):
        p[0].add(p[2])
        return p[0]

    @_('Body : Body TERMINATOR')
    def p_body_body(self, p):
        p[0] = p[1]

    @_('Line : Expression', 'Line : Statement')
    def p_line(self, p):
        return p[0]
       
    @_('Expression : Clause', 'Expression : Term')
    def p_expr(self, p):
        #p[0] = p[1]
        return p[0]

    @_('Term : VARIABLE', 'Term : NOUN', 'Term : STRING')
    def p_term(self, p):
        #p[0] = p[1]
        return p[0]

    @_('Term : SNIPPET')
    def p_snippet(self, p):
        return Snippet(p[0])

    @_('ParExpr : LPAR Expression RPAR')
    def p_parexpr(self, p):
        p[0] = p[2]

    @_('ParExpr : LPAR RPAR')
    def p_parexpr_empty(self, p):
        p[0] = None

    @_('Statement : Class', 'Statement : Method')
    def p_stmt(self, p):
        return p[0]

    @_('Class : CLASS Identifier Block')
    def p_class(self, p):
        p[0] = Class(p[2], p[3])
    
    @_('Method : DEF Identifier ParExpr Block')
    def p_def(self, p):
        return Method(p[1], p[2], p[3])

    @_('Clause : Expression VERB Expression')
    def p_clause1(self, p):
        return Clause(p[0], p[1], p[2]);
        
    @_('Clause : Expression VERB')
    def p_clause2(self, p):
        p[0] = Clause(p[1], p[2], None);

    @_('Clause : VERB Expression')
    def p_clause3(self, p):
        #p[0] = Clause(None, p[1], p[2]);
        return Clause(None, p[0], p[1]);

    @_('Clause : VERB')
    def p_clause4(self, p):
        return Clause(None, p[0], None);
        
    @_('Clause : Expression')
    def p_clause5(self, p):
        p[0] = p[1]

    @_('Identifier : VERB', 'Identifier : NOUN')        
    def p_id(self, p):
        #p[0] = p[1]
        return p[0]
                    
    def p_error(self, p):
        if p:
            print("Syntax error at '%s'" % p.value)
        else:
            print("Syntax error at EOF")
