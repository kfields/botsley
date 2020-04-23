import sly
import decimal
from botsley.compile.lex.lexerbase import LexerBase, create_token
    
class Lexer(LexerBase):
    tokens = LexerBase.tokens
    def __init__(self):
        super().__init__()

    @_(r"""(\d+(\.\d*)?|\.\d+)([eE][-+]? \d+)?""")
    def NUMBER(self, p):
        return decimal.Decimal(p.NUMBER)

    CODE = r"{.*}"
    STRING = r"'([^\\']+|\\'|\\\\)*'"
    
    TRUE = r'True'
    FALSE = r'False'

    NLONGARROW = r'!-->'
    LONGARROW = r'-->'        
    NARROW = r'!->'
    ARROW = r'->'
    NLONGFATARROW = r'!==>'        
    LONGFATARROW = r'==>'
    NFATARROW = r'!=>'
    FATARROW = r'=>'
    
    GRAVE = r'`'
    CARET = r'\^'
    COLON = r':'
    DCOLON = r'::'
    LTCOLON = r'<:'
    LTLTCOLON = r'<<:'
    AMP = r'&'
    BANG = r'!'
    SLASH = r'/'
    STAR = r'&'
    NOT = r'not'
    AT = r'@'
    EQEQ = r'=='
    EQ = r'=='
    NEQ = r'!='
    ASSIGN = r'='
    LT = r'<'
    GT = r'>'
    MINUSPLUS = r'-+'
    PLUS = r'\+'
    MINUS = r'-'
    MULT = r'\*'
    DIV = r'/'
    COMMA = r','
    SEMICOLON = r';'
    
    IMPORT = r'import'
    SIG = r'sig'
    WHERE = r'where'
    INSTANCEOF = r'instanceof'
    HALT = 'halt'
    #
    
    RESERVED = {
      "class": "CLASS",
      "predicate": "PREDICATE",
      "def": "DEF",
      "if": "IF",
      "return": "RETURN",
      'import': 'IMPORT',
      'sig': 'SIG',
      'where': 'WHERE',
      'instanceof': 'INSTANCEOF',
      'halt': 'HALT'
      }

    PROPERTY = r'\$[a-zA-Z_][a-zA-Z0-9_]*\:'
    VARIABLE = r'\$[a-zA-Z_][a-zA-Z0-9_]*'
    
    @_(r'[a-z_]+[a-zA-Z0-9_]*')
    def VERB(self, t):
        r = self.RESERVED.get(t.value)
        if r:
            return create_token(r, t.value, t.lineno, t.index)
        else:
            return t

    TYPE = r'[A-Z_]+[a-zA-Z0-9_]*\:'
    POSTTYPE = r'\:[A-Z_]+[a-zA-Z0-9_]*'
    NOUN = r'[A-Z_]+[a-zA-Z0-9_]*'
        
    @_(r"[ ]*\043[^\r?\n]*")
    def COMMENT(self, t):
        pass

    SNIPPET = r"\|.*"
    
    '''
    WS = r' +'

    # Don't generate newline tokens when inside of parenthesis, eg
    #   a = (1,
    #        2, 3)
    @_(r'\r?\n+')
    def NEWLINE(self, t):
        self.linepos = t.index + len(t.value)
        self.lineno += len(t.value)
        #t.type = "NEWLINE"
        if self.paren_count == 0:
            return t
    '''
    # Whitespace
    #@_(r' [ \t]+ ')
    @_(r' +')
    def WS(self, t):
        if self.at_line_start and self.paren_count == 0:
            return t
    
    # Don't generate newline tokens when inside of parenthesis, eg
    #   a = (1,
    #        2, 3)
    @_(r'\r?\n+')
    def NEWLINE(self, t):
        self.linepos = t.index + len(t.value)
        self.lineno += len(t.value)
        t.type = "NEWLINE"
        if self.paren_count == 0:
            return t
    
    @_(r'\(')
    def LPAR(self, t):
        self.paren_count += 1
        return t
    
    @_(r'\)')
    def RPAR(self, t):
        # check for underflow?  should be the job of the parser
        self.paren_count -= 1
        return t
    
    
    def error(self, t):
        print('Line %d: Bad character %r' % (self.lineno, t.value[0]))
        self.index += 1
        
