import sly

EOF = 'EOF'
NEWLINE = 'NEWLINE'
SEMICOLON = 'SEMICOLON'
TERMINATOR = 'TERMINATOR'
INDENT = 'INDENT'
OUTDENT = 'OUTDENT'

def create_token(type, value, lineno, index):
    tok = sly.lex.Token()
    tok.type = type
    tok.value = None
    tok.lineno = lineno
    tok.index = index
    tok.end = index + 1
    return tok

# Synthesize a TERMINATOR tag
def _TERMINATOR(lineno, index):
    return create_token(TERMINATOR, None, lineno, index)

# Synthesize an INDENT tag
def _INDENT(lineno, index):
    return create_token(INDENT, None, lineno, index)
    
# Synthesize a OUTDENT tag
def _OUTDENT(lineno, index):
    return create_token(OUTDENT, None, lineno, index)

class LexerBase(sly.Lexer):
    def __init__(self):
        super().__init__()
        self.linepos = 0
        self.paren_count = 0
        self.at_line_start = False
        self.prevTokenType = TERMINATOR
        self.indentstack = [0]
        self.queue = []
        self.eof = False
        
    def find_indent(self, token):
        lascr = self.linepos
        if lascr < 0:
            lascr = 0
        indent = token.index - lascr
        return indent
    
    def finish(self):
        while self.indentstack[-1] > 0:
            self.indentstack.pop()
            #self.queue.append(_OUTDENT(lineno, index))
            #TODO: Need lineno and index.  How?
            self.queue.append(_OUTDENT(0, 0))
        self.queue.append(None)

    def tokenizefile(self, f):
        s = f.read()
        self.tokenize(s)
        
    def tokenize(self, text, lineno=1, index=0):
        print('tokenize')
        tokenStream = super().tokenize(text, lineno, index)
        while True:
            tok = None
            latok = None
            indent = 0
            lineno = 0
            index = 0

            if self.queue:
                tok = self.queue.pop(0)
                if tok:
                    self.prevTokenType = tok.type
                yield tok
            
            tok = next(tokenStream, None)

            if not tok:
                if self.eof:
                    return None
                self.eof = True
                self.finish()
            elif tok.type == NEWLINE:
                while True:
                    latok = next(tokenStream, None)
                    if not latok:
                        self.finish()
                        yield self.queue.pop(0)
                        return
                    if latok.type != NEWLINE:
                        break
                indent = self.find_indent(latok)
                lineno = latok.lineno
                index = latok.index
                if indent > self.indentstack[-1]:
                    self.indentstack.append(indent)
                    self.queue.append(_INDENT(lineno, index))
                elif indent < self.indentstack[-1]:
                    while indent < self.indentstack[-1]:
                        self.indentstack.pop()
                        self.queue.append(_OUTDENT(lineno, index))
                    self.queue.append(_TERMINATOR(lineno, index))
                else:
                    if self.prevTokenType != TERMINATOR:
                        self.queue.append(_TERMINATOR(lineno, index))
                self.queue.append(latok)
            else:
                self.queue.append(tok)
            #
            tok = self.queue.pop(0)
            if tok != None:
                self.prevTokenType = tok.type
            yield tok

    tokens = {
        INDENT,
        OUTDENT,
        COMMENT,
        IMPORT,
        INSTANCEOF,
        HALT,
        PROPERTY,
        CODE,
        SIG,
        TRUE,
        FALSE,
        NOT,
        AMP,
        BANG,
        SLASH,
        STAR,
        DCOLON,
        TYPE,
        POSTTYPE,
        WHERE,
        CLASS,
        PREDICATE,
        DEF,
        IF,
        VARIABLE,
        VERB,
        NOUN,
        NUMBER,  # Python decimals
        SNIPPET,
        STRING,  # single quoted strings only; syntax of raw strings
        LPAR,
        RPAR,
        NLONGARROW,  #!-->
        LONGARROW,  # -->
        NARROW,  #!->
        ARROW,  # ->
        NLONGFATARROW,  #!==>
        LONGFATARROW,  # ==>
        NFATARROW,  #!=>
        FATARROW,  # =>
        GRAVE,
        CARET,
        COLON,
        DBLCOLON,
        LTCOLON,
        LTLTCOLON,
        AT,
        EQ,
        EQEQ,
        NEQ,
        ASSIGN,
        LT,
        GT,
        PLUS,
        MINUS,
        MINUSPLUS,
        MULT,
        DIV,
        RETURN,
        WS,
        NEWLINE,
        TERMINATOR,
        COMMA,
        SEMICOLON,
        INDENT,
        OUTDENT,
        EOF,
    }
