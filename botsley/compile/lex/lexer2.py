import sly.lex as lex
import decimal
from botsley.compile.lex.tokens import tokens

EOF = 'EOF'
NEWLINE = 'NEWLINE'
SEMICOLON = 'SEMICOLON'
TERMINATOR = 'TERMINATOR'
INDENT = 'INDENT'
DEDENT = 'DEDENT'

def _new_token(type, lineno, lexpos):
    tok = lex.LexToken()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.lexpos = lexpos
    return tok

# Synthesize a TERMINATOR tag
def _TERMINATOR(lineno, lexpos):
    return _new_token(TERMINATOR, lineno, lexpos)

# Synthesize an INDENT tag
def _INDENT(lineno, lexpos):
    return _new_token(INDENT, lineno, lexpos)
    
# Synthesize a DEDENT tag
def _DEDENT(lineno, lexpos):
    return _new_token(DEDENT, lineno, lexpos)
    
class Lexer:
    tokens = tokens
    def __init__(self):
        self.linepos = 0
        self.paren_count = 0
        self.at_line_start = False
        self.prevTokenType = TERMINATOR
        self.indentstack = [0]
        self.queue = []
        self.eof = False
    
    def build(self, **kwargs):
        #self.lexer = lex.lex(object=self, debug=True, **kwargs)
        self.lexer = lex.lex(object=self, **kwargs)

    def input_file(self, f):
        s = f.read()
        self.input(s)

    def input(self, s):
        self.lexer.input(s)
        
    def next(self):
        return self.lexer.token()
        
    def find_indent(self, token):
        last_cr = self.linepos
        if last_cr < 0:
            last_cr = 0
        indent = token.lexpos - last_cr
        return indent
    
    def finish(self):
        while self.indentstack[-1] > 0:
            self.indentstack.pop()
            #self.queue.append(_DEDENT(lineno, lexpos))
            #TODO: Need lineno and lexpos.  How?
            self.queue.append(_DEDENT(0, 0))
        self.queue.append(None)

    def token(self):
        tok = None
        latok = None
        indent = 0
        lineno = 0
        lexpos = 0

        if self.queue:
            tok = self.queue.pop(0)
            if tok:
                self.prevTokenType = tok.type
            return tok
        
        tok = self.next()

        if not tok:
            if self.eof:
                return None
            self.eof = True
            self.finish()
        elif tok.type == NEWLINE:
            while 1:
                latok = self.next()
                if not latok:
                    self.finish()
                    return self.queue.pop(0)
                if latok.type != NEWLINE:
                    break
            indent = self.find_indent(latok)
            lineno = latok.lineno
            lexpos = latok.lexpos
            if indent > self.indentstack[-1]:
                self.indentstack.append(indent)
                self.queue.append(_INDENT(lineno, lexpos))
            elif indent < self.indentstack[-1]:
                while indent < self.indentstack[-1]:
                    self.indentstack.pop()
                    self.queue.append(_DEDENT(lineno, lexpos))
                self.queue.append(_TERMINATOR(lineno, lexpos))
            else:
                if self.prevTokenType != TERMINATOR:
                    self.queue.append(_TERMINATOR(lineno, lexpos))
            self.queue.append(latok)
        else:
            self.queue.append(tok)
        #
        tok = self.queue.pop(0)
        if tok != None:
            self.prevTokenType = tok.type
        return tok
    
    #t_NUMBER = r'\d+'
    # taken from decimal.py but without the leading sign
    def t_NUMBER(self, t):
        r"""(\d+(\.\d*)?|\.\d+)([eE][-+]? \d+)?"""
        t.value = decimal.Decimal(t.value)
        return t
    
    def t_STRING(self, t):
        r"'([^\\']+|\\'|\\\\)*'"  # I think self is right ...
        #t.value=t.value[1:-1].decode("string-escape") # .swapcase() # for fun
        return t
    
    t_NLONGTHINARROW = r'!-->'
    t_LONGTHINARROW = r'-->'        
    t_NTHINARROW = r'!->'
    t_THINARROW = r'->'
    t_NLONGFATARROW = r'!==>'        
    t_LONGFATARROW = r'==>'
    t_NFATARROW = r'!=>'
    t_FATARROW = r'=>'
    
    t_GRAVE = r'`'
    t_COLON = r':'
    t_DBLCOLON = r'::'
    t_AT = r'@'
    t_EQ = r'=='
    t_NEQ = r'!='
    t_ASSIGN = r'='
    t_LT = r'<'
    t_GT = r'>'
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_MULT = r'\*'
    t_DIV = r'/'
    t_COMMA = r','
    t_SEMICOLON = r';'
    
    #
    
    RESERVED = {
      "class": "CLASS",          
      "predicate": "PREDICATE",
      "def": "DEF",
      "if": "IF",
      "return": "RETURN",
      }

    def t_VARIABLE(self, t):
        r'\$[a-zA-Z_][a-zA-Z0-9_]*'
        return t
    
    def t_VERB(self, t):
        #r'[a-zA-Z_][a-zA-Z0-9_]*'
        r'[a-z_]+[a-zA-Z0-9_]*'
        t.type = self.RESERVED.get(t.value, "VERB")
        return t

    def t_NOUN(self, t):
        #r'[a-zA-Z_][a-zA-Z0-9_]*'
        r'[A-Z_]+[a-zA-Z0-9_]*'
        return t
        
    # Putting self before t_WS let it consume lines with only comments in
    # them so the latter code never sees the WS part.  Not consuming the
    # newline.  Needed for "if 1: #comment"
    def t_comment(self, t):
        r"[ ]*\043[^\r?\n]*"  # \043 is '#'
        pass

    def t_SNIPPET(self, t):
        r"\|.*"
        return t
    
    # Whitespace
    def t_WS(self, t):
        r' [ \t]+ '
        if self.at_line_start and self.paren_count == 0:
            return t
    
    # Don't generate newline tokens when inside of parenthesis, eg
    #   a = (1,
    #        2, 3)
    def t_newline(self, t):
        r'\r?\n+'
        self.linepos = t.lexpos + len(t.value)
        t.lexer.lineno += len(t.value)
        t.type = "NEWLINE"
        if self.paren_count == 0:
            return t
    
    def t_LPAR(self, t):
        r'\('
        self.paren_count += 1
        return t
    
    def t_RPAR(self, t):
        r'\)'
        # check for underflow?  should be the job of the parser
        self.paren_count -= 1
        return t
    
    
    def t_error(self, t):
        print("Skipping", repr(t.value[0]))
        raise SyntaxError("Unknown symbol %r" % (t.value[0],))
        #print("Illegal character %s" % t.value[0])
        #print("Illegal character:  ", t)
        t.lexer.skip(1)
        
