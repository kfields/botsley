'''
%lex
%token INVALID COMMENT NEWLINE EOL TERMINATOR INDENT OUTDENT
%token LONGARROW

digit   [0-9]
L			  [a-zA-Z_]
verb    [a-z_]+[a-zA-Z0-9_]*
noun    [A-Z_]+[a-zA-Z0-9_]*
id      [a-zA-Z_]+[a-zA-Z0-9_]*
cr      [\r?\n]+
%%

{digit}+						return 'NUMBER';
"true"      return 'TRUE';
"false"      return 'FALSE';
//
"import"          return 'IMPORT';
"def"             return 'DEF';
"sig"             return 'SIG';
"not"             return 'NOT';
"return"          return 'RETURN';
"halt"            return 'HALT';
//
"where"           return 'WHERE';
"-->"             return 'LONGARROW';
"!->"             return 'NOTARROW';
"==>"             return 'LONGFATARROW';
"!=>"             return 'NOTFATARROW';
//
"->"              return '->';
//
"+"               return '+';
"-"               return '-';
"-+"              return '-+';
"*"               return '*';
"@"               return '@';
"/"               return '/';
//
"=="              return '==';
"!="              return '!=';
"="               return '=';
"!"               return '!';
"instanceof"      return 'instanceof';
//
\${id}						return 'VARIABLE';
{noun}\:            return 'TYPE';
\:{noun}            return 'POSTTYPE';
{verb}\:            return 'PROPERTY';
{verb}						return 'VERB';
{noun}						return 'NOUN';

//
"("               return '(';
")"               return ')';
","               return ',';
"&"               return '&';
"::"              return '::';
"^"              return '^';
"<:"              return '<:';
"<<:"             return '<<:';
//
"#".*{cr}             //return 'COMMENT'
"|".*             return 'SNIPPET';
"{".*"}"          return 'CODE';

//"\""*"\""         return 'STRING';
L?\"(\\.|[^\\"])*\"	return 'STRING';

[\r?\n]+					return 'NEWLINE';
[\s\t]+           //skip whitespace
<<EOF>>           return 'EOF';
.                 return 'INVALID';

/lex

%left '::'
%left '@'
//%right ':'
%left '<:'
%left '<<:'

%start File
%%
'''

'''
Skip
  : COMMENT | NEWLINE | SEMICOLON | INVALID
  ;
'''
    @_('COMMENT', 'NEWLINE', 'SEMICOLON', 'INVALID')
    def Skip(self, p):
        pass
'''
File
  : Module EOF
    { return $1; }
  ;
'''
    @_('Module EOF')
    def File(self, p):
        return p.Module
'''
Module
  : Body
    { $$ = new yy.Module($1); }
  ;
'''
    @_('Body')
    def Module(self, p):
        return yy.Module(p.Body)
'''
Block
  : INDENT OUTDENT
    { $$ = new yy.Block(); }
  | INDENT Body OUTDENT
    { $$ = $2; }
  ;
'''
    @_('INDENT OUTDENT')
    def Block(self, p):
        return yy.Block()

    @_('INDENT Body OUTDENT')
    def Block(self, p):
        return p.Body
'''
Body
  : Line
    { $$ = new yy.Block($1); }
  | Body TERMINATOR Line
    {$$ = $1; $1.add($3);}
  | Body TERMINATOR
  ;
'''
    @_('Line')
    def Body(self, p):
        return yy.Block(p.Line)

    @_('Body TERMINATOR Line')
    def Body(self, p):
        p.Body.add(p.Line)
        return p.Body

    @_('Body TERMINATOR')
    def Body(self, p):
        return p.Body
'''
ExprList
  :
  | Expression
    {$$ = [$1];}
  | ExprList TERMINATOR Expression
    {$$ = $1; $1.push($3);}
  | ExprList TERMINATOR
  ;
'''
    @_('Expression')
    def ExprList(self, p):
        return [p.expr]

    @_('ExprList TERMINATOR Expression')
    def ExprList(self, p):
        return p.ExprList.append(p.Expression)

    @_('ExprList TERMINATOR')
    def ExprList(self, p):
        return p.ExprList
'''
Line
  : Statement | Expression
  ;
'''
    @_('Statement', 'Expression')
    def Line(self, p):
        return p[0]
'''
Statement
  : Import | Def | Sig | Sig | Return | Halt
  ;
'''
    @_('Import', 'Def', 'Sig', 'Sig', 'Return', 'Halt')
    def Statement(self, p):
        return p[0]
'''
Action
  : Expression
    { $$ = new yy.Action($1); }
  ;
'''
    @_('Expression')
    def Action(self, p):
        return yy.Action(p.expr)
'''
Import
  : IMPORT Expression
    { $$ = new yy.ImportStmt($2); }
  ;
'''
    @_('IMPORT Expression')
    def Import(self, p):
        return yy.ImportStmt(p.expr)
'''
Trigger
  : Expression
    { $$ = new yy.Trigger($1); }
  ;
'''
    @_('Expression')
    def Trigger(self, p):
        return yy.Trigger(p.expr)
'''
Def
  : DEF '(' Trigger ')' Block
    { $$ = new yy.Def($3, $5); }
  ;
'''
    @_('DEF LPAREN Trigger RPAREN Block')
    def Def(self, p):
        return yy.Def(p.Trigger, p.Block)
'''
Sig
  : SIG '(' Trigger ')' Block
    { $$ = new yy.Sig($3, $5); }
  ;
'''
    @_('SIG LPAREN Trigger RPAREN Block')
    def Sig(self, p):
        return yy.Sig(p.Trigger, p.Block)
'''
Condition
  : QClause | QNegClause | QFilter
  ;
'''
    @_('QClause', 'QNegClause', 'QFilter')
    def Condition(self, p):
        return p[0]
'''
QClause
  : Clause
    {$$ = new yy.QClause($1);}
  ;
'''
    @_('Clause')
    def QClause(self, p):
        return yy.QClause(p.Clause)
'''
QNegClause
  : NegClause
    {$$ = new yy.QNegClause($1);}
  ;
'''
    @_('NegClause')
    def QNegClause(self, p):
        return yy.QNegClause(p.NegClause)
'''
QFilter
  : Expression
    {$$ = new yy.QFilter($1);}
  ;
'''
    @_('Expression')
    def QFilter(self, p):
        return yy.QFilter(p.Expression)
'''
Where
  : WHERE INDENT Lhs OUTDENT Rhs
    {$$ = new yy.Query($3, $5);}
  ;
'''
    @_('WHERE INDENT Lhs OUTDENT Rhs')
    def Where(self, p):
        return yy.Query(p.Lhs, p.Rhs)
'''
Lhs
  : Condition
    {$$ = new yy.Lhs($1);}
  | Lhs TERMINATOR Condition
    {$$ = $1; $1.add($3);}
  | Lhs TERMINATOR
  ;
'''
    @_('Condition')
    def Lhs(self, p):
        return yy.Lhs(p.Condition)

    @_('Lhs TERMINATOR Condition')
    def Lhs(self, p):
        p.Lhs.add(p.Condition)
        return p.Lhs

    @_('Lhs TERMINATOR')
    def Lhs(self, p):
        return p.Lhs
'''
Rhs
  : WhereTrue
    {$$ = new yy.Rhs($1);}
  | Rhs WhereFalse
    {$$ = $1; $1.add($2);}
  | Rhs WhereAllTrue
    {$$ = $1; $1.add($2);}
  | Rhs WhereAllFalse
    {$$ = $1; $1.add($2);}
  ;
'''
    @_('WhereTrue')
    def Rhs(self, p):
        return yy.Rhs(p.WhereTrue)

    @_('Rhs WhereFalse')
    def Rhs(self, p):
        p.Rhs.add(p.WhereFalse)
        return p.Rhs

    @_('Rhs WhereAllTrue')
    def Rhs(self, p):
        p.Rhs.add(p.WhereAllTrue)
        return p.Rhs

    @_('Rhs WhereAllFalse')
    def Rhs(self, p):
        p.Rhs.add(p.WhereAllFalse)
        return p.Rhs
'''
WhereTrue
  : LONGARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;
'''
    @_('LONGARROW Block')
    def WhereTrue(self, p):
        return yy.Actions(p.Block, p.LONGARROW)
'''
WhereFalse
  : NOTARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;
'''
    @_('NOTARROW Block')
    def WhereFalse(self, p):
        return yy.Actions(p.Block, p.NOTARROW)
'''
WhereAllTrue
  : LONGFATARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;
'''
    @_('LONGFATARROW Block')
    def WhereAllTrue(self, p):
        return yy.Actions(p.Block, p.LONGFATARROW)
'''
WhereAllFalse
  : NOTFATARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;
'''
    @_('NOTFATARROW Block')
    def WhereAllFalse(self, p):
        return yy.Actions(p.Block, p.LONGFATARROW)
'''
Expression
  : ParExpr | PrefixExpr | PostfixExpr | BinaryExpr | Paragraph | Terminal
  ;
'''
    @_('ParExpr', 'PrefixExpr', 'PostfixExpr', 'BinaryExpr', 'Paragraph', 'Terminal')
    def Expression(self, p):
        return p[0]
'''
Terminal
  : Literal | Variable | Term | Snippet | Code
  ;
'''
    @_('Literal', 'Variable', 'Term', 'Snippet', 'Code')
    def Terminal(self, p):
        return p[0]
'''
Literal
  : STRING
    { $$ = new yy.Literal($1); }
  | NUMBER
    { $$ = new yy.Literal($1); }
  | TRUE
    { $$ = new yy.Literal($1); }
  | FALSE
    { $$ = new yy.Literal($1); }
  ;
'''
    @_('STRING', 'NUMBER', 'TRUE', 'FALSE')
    def Literal(self, p):
        return p[0]
'''
Variable
  : VARIABLE
    { $$ = new yy.Variable($1.slice(1)); }
  ;
'''
    @_('VARIABLE')
    def Variable(self, p):
        return yy.Variable(p.VARIABLE.slice(1))
'''
Verb
  : VERB
    { $$ = new yy.term_($1); }
  ;
'''
    @_('VERB')
    def Verb(self, p):
        return yy.term_(p.VERB)()
'''
Term
  : NOUN
    { $$ = new yy.term_($1); }
  ;
'''
    @_('NOUN')
    def Term(self, p):
        return yy.term_(p.NOUN)()
'''
Snippet
  : SNIPPET
    { $$ = new yy.Snippet($1); }
  ;
'''
    @_('SNIPPET')
    def Snippet(self, p):
        return yy.Snippet(p.SNIPPET)()
'''
Code
  : CODE
    { $$ = new yy.Code($1); }
  ;
'''
    @_('CODE')
    def Code(self, p):
        return yy.Code(p.CODE)()
'''
Paragraph
: Sentence
  {$$ = $1;}
| Expression '::' INDENT ExprList OUTDENT
  {$$ = new yy.Paragraph($1, $4);}
;
'''
    @_('Sentence')
    def Paragraph(self, p):
        return p.Sentence

    @_('Expression DCOLON INDENT ExprList OUTDENT')
    def Paragraph(self, p):
        return yy.Paragraph(p.Expression, p.ExprList)
'''
SentenceList
  :
  | Sentence
    {$$ = [$1];}
  | SentenceList TERMINATOR Sentence
    {$$ = $1; $1.push($3);}
  | SentenceList TERMINATOR
  ;
'''
    @_('Sentence')
    def SentenceList(self, p):
        return p.Sentence

    @_('SentenceList TERMINATOR Sentence')
    def SentenceList(self, p):
        p.SentenceList.append(p.Sentence)
        return p.SentenceList

    @_('SentenceList TERMINATOR')
    def SentenceList(self, p):
        return p.SentenceList
'''
Sentence
  : ClauseExpr
    {$$ = $1;}
  | ClauseExpr '&' AmpList
    {$$ = new yy.Sentence($1, $3);}
  ;
'''
    @_('ClauseExpr')
    def Sentence(self, p):
        return p.ClauseExpr

    @_('ClauseExpr AMP AmpList')
    def Sentence(self, p):
        return yy.Sentence(p.ClauseExpr, p.AmpList)
'''
AmpList
  :
  | Expression
    {$$ = [$1];}
  | AmpList '&' Expression
    {$$ = $1; $1.push($3);}
  ;
'''
    @_('Expression')
    def AmpList(self, p):
        return p.Expression

    @_('AmpList AMP Expression')
    def AmpList(self, p):
        p.AmpList.append(p.Expression)
        return p.AmpList
'''
ClauseExpr
  : Clause
    {$$ = $1;}
  | BindExpr
    {$$ = $1;}
  ;
'''
    @_('Clause', 'BindExpr')
    def ClauseExpr(self, p):
        return p.Expression
'''
BindExpr
  : Clause '->' Variable
    { $$ = $1; $1.binding = $3; }
  ;
'''
    @_('Clause ARROW Variable')
    def BindExpr(self, p):
        p.Clause.binding = p.Variable
        return p.Clause
'''
NegClause
: NotOp Clause
  {$$ = $2;}
;
'''
    @_('NotOp Clause')
    def NegClause(self, p):
        p.Clause.negated = True
        return p.Clause
'''
Clause
  : SimpleClause
    {$$ = $1;}
  | SimpleClause Properties
    {$$ = $1; $1.xtra = $2;}
  ;
'''
    @_('SimpleClause')
    def Clause(self, p):
        return p.SimpleClause

    @_('SimpleClause Properties')
    def Clause(self, p):
        p.SimpleClause.xtra = Properties
        return p.SimpleClause
'''
SimpleClause
  : Expression Verb ObjExpr
    { $$ = new yy.Clause($1, $2, $3); }
  | Expression Verb
    { $$ = new yy.Clause($1, $2, yy._null); }
  | Verb ObjExpr
    { $$ = new yy.Clause(yy._null, $1, $2); }
  | Verb
    { $$ = new yy.Clause(yy._null, $1, yy._null); }
  ;
'''
    @_('Expression Verb ObjExpr')
    def SimpleClause(self, p):
        return yy.Clause(p.Expression, p.Verb, p.ObjExpr)

    @_('Expression Verb')
    def SimpleClause(self, p):
        return yy.Clause(p.Expression, p.Verb, yy._null)

    @_('Verb ObjExpr')
    def SimpleClause(self, p):
        return yy.Clause(yy._null, p.Verb, p.ObjExpr)

    @_('Verb')
    def SimpleClause(self, p):
        return yy.Clause(yy._null, p.Verb, yy._null)
'''
ObjExpr
  : CommaList
    {$$ = ($1.length == 1 ? $1[0] : new yy.Array($1));}
  ;
'''
    @_('CommaList')
    def ObjExpr(self, p):
        return p.CommaList if len(p.CommaList) == 1 else yy.Array(p.CommaList)
'''
CommaList
  :
  | Expression
    {$$ = [$1];}
  | CommaList ',' Expression
    {$$ = $1; $1.push($3);}
  ;
'''
    @_('Expression')
    def CommaList(self, p):
        return [p.Expression]

    @_('CommaList COMMA Expression')
    def CommaList(self, p):
        p.CommaList.append(p.Expression)
        return p.CommaList
'''
TypeName
  : TYPE
  { $$ = $1.slice(0, -1); }
;
'''
    @_('TYPE')
    def TypeName(self, p):
        return p.TYPE.slice(0, -1)
'''
PostTypeName
  : POSTTYPE
  { $$ = $1.slice(1); }
;
'''
    @_('POSTTYPE')
    def PostTypeName(self, p):
        return p.POSTTYPE.slice(1)
'''
PropertyName
  : PROPERTY
  { $$ = $1.slice(0, -1); }
;
'''
    @_('PROPERTY')
    def PropertyName(self, p):
        return p.PROPERTY.slice(0, -1)
'''
Property
  :
  PropertyName
    { $$ = new yy.Property($1); }
  | PropertyName Expression
    { $$ = new yy.Property($1, $2); }
  ;
'''
    @_('PropertyName')
    def Property(self, p):
        return yy.Property(p.PropertyName)

    @_('PropertyName Expression')
    def Property(self, p):
        return yy.Property(p.PropertyName, p.Expression)
'''
Properties
  :
    Property
    {$$ = new yy.Properties($1);}
  | Properties Property
    {$$ = $1; $1.add($2);}
  ;
'''
    @_('Property')
    def Properties(self, p):
        return yy.Properties(p.Property)

    @_('Properties Property')
    def Properties(self, p):
        p.Properties.add(p.Property)
        return p.Properties
'''
ParExpr
  : '(' ')'
    { $$ = null; }
  | '(' Expression ')'
    { $$ = $2; }
  ;
'''
    @_('LPAR RPAR')
    def ParExpr(self, p):
        return None

    @_('LPAR Expression RPAR')
    def ParExpr(self, p):
        return p.Expression
'''
PrefixExpr
  : Typed | Not | Slash | Message
  ;
'''
    @_('Typed', 'Not', 'Slash', 'Message')
    def PrefixExpr(self, p):
        return p[0]
'''
Typed
  : TypeName Expression
  { $2.type = yy.type_($1); $$ = $2; }
  ;
'''
    @_('TypeName Expression')
    def Typed(self, p):
        p.Expression.type = yy.type_(p.TypeName)
        return p.Expression
'''
NotOp : '!' | NOT ;
'''
    @_('BANG', 'NOT')
    def NotOp(self, p):
        return p[0]
'''
Not
  : NotOp Expression
  { $$ = new yy.PrefixExpr($2, $1); }
  ;
'''
    @_('NotOp Expression')
    def Not(self, p):
        return yy.PrefixExpr(p.Expression, p.NotOp)
'''
Slash
  : '/' Expression
  { $2.slash = true; $$ = $2; }
  ;
'''
    @_('SLASH Expression')
    def Slash(self, p):
        p.Expression.slash = True
        return p.Expression
'''
Message
  : Propose | Attempt | Assert | Retract | Modify
  ;
'''
    @_('Propose', 'Attempt', 'Assert', 'Retract', 'Modify')
    def Message(self, p):
        return p[0]
'''
Propose
  : '*' Expression
  { $$ = new yy.Propose($2); }
  ;
'''
    @_('STAR Expression')
    def Propose(self, p):
        return yy.Propose(p.Expression)
'''
Attempt
  : '@' Expression
  { $$ = new yy.Attempt($2); }
  ;
'''
    @_('AT Expression')
    def Attempt(self, p):
        return yy.Attempt(p.Expression)
'''
Assert
  : '+' Expression
    { $$ = new yy.Assert($2); }
  ;
'''
    @_('PLUS Expression')
    def Assert(self, p):
        return yy.Assert(p.Expression)
'''
Retract
  : '-' Expression
  { $$ = new yy.Retract($2); }
  ;
'''
    @_('MINUS Expression')
    def Retract(self, p):
        return yy.Retract(p.Expression)
'''
Modify
  : '-+' Expression
  { $$ = new yy.Modify($2); }
  ;
'''
    @_('MINUSPLUS Expression')
    def Modify(self, p):
        return yy.Modify(p.Expression)
'''
PostfixExpr
  : PostTyped | Achieve
  ;
'''
    @_('PostTyped', 'Achieve')
    def PostfixExpr(self, p):
        return p[0]
'''
PostTyped
  : Expression PostTypeName
  { $1.type = yy.type_($2); $$ = $1; }
  ;
'''
    @_('Expression PostTypeName')
    def PostTyped(self, p):
        p.Expression.type = yy.type_(p.PostTypeName)
        return p.Expression
'''
Achieve
  : Expression '!'
  { $$ = new yy.PostfixExpr($2, $1); }
  ;
'''
    @_('Expression BANG')
    def Achieve(self, p):
        return yy.PostfixExpr(p.Expression, p.BANG)
'''
BinaryExpr
  : ContextExpr | InjectExpr | TypeOfExpr | AssignExpr | EqualExpr | NotEqualExpr | InstanceOfExpr
  ;
'''
    @_('ContextExpr', 'InjectExpr', 'TypeOfExpr', 'AssignExpr', 'EqualExpr', 'NotEqualExpr', 'InstanceOfExpr')
    def BinaryExpr(self, p):
        return p[0]
'''
ContextExpr
  : Expression '<:' INDENT ExprList OUTDENT
    { $$ = new yy.BinaryExpr($1, $4, $2); }
  ;
'''
    @_('Expression LTCOLON INDENT ExprList OUTDENT')
    def ContextExpr(self, p):
        return yy.BinaryExpr(p.Expression, p.ExprList, p.LTCOLON)
'''
InjectExpr
  : Expression '<<:' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;
'''
    @_('Expression LTLTCOLON Expression')
    def InjectExpr(self, p):
        return yy.BinaryExpr(p[0], p[2], p.LTLTCOLON)
'''
TypeOfExpr
  : Expression '^' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;
'''
    @_('Expression CARET Expression')
    def TypeOfExpr(self, p):
        return yy.BinaryExpr(p[0], p[2], p.CARET)
'''
AssignExpr
  : Expression '=' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;
'''
    @_('Expression EQ Expression')
    def AssignExpr(self, p):
        return yy.BinaryExpr(p[0], p[2], p.EQ)
'''
EqualExpr
  : Expression '==' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;
'''
    @_('Expression EQEQ Expression')
    def EqualExpr(self, p):
        return yy.BinaryExpr(p[0], p[2], p.EQEQEQ)
'''
NotEqualExpr
  : Expression 'BANGEQ' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;
'''
    @_('Expression EQEQ Expression')
    def NotEqualExpr(self, p):
        return yy.BinaryExpr(p[0], p[2], p.BANGEQ)
'''
InstanceOfExpr
  : Expression 'instanceof' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;
'''
    @_('Expression INSTANCEOF Expression')
    def InstanceOfExpr(self, p):
        return yy.BinaryExpr(p[0], p[2], p.INSTANCEOF)
'''
Return
  : RETURN Expression
    { $$ = new yy.Return($2); }
  | RETURN
    { $$ = new yy.Return(null); }
  ;
'''
    @_('RETURN Expression')
    def Return(self, p):
        return yy.Return(p.Expression)

    @_('RETURN')
    def Return(self, p):
        return yy.Return()
'''
Halt
  : HALT Expression
    { $$ = new yy.Halt($2); }
  | HALT
    { $$ = new yy.Halt(null); }
  ;
'''
    @_('HALT Expression')
    def Halt(self, p):
        return yy.Halt(p.Expression)

    @_('HALT')
    def Halt(self, p):
        return yy.Halt()
