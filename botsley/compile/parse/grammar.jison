/* Mia Grammar */

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
Skip
  : COMMENT | NEWLINE | SEMICOLON | INVALID
  ;

File
  : Module EOF
    { return $1; }
  ;

Module
  : Body
    { $$ = new yy.Module($1); }
  ;

Block
  : INDENT OUTDENT
    { $$ = new yy.Block(); }
  | INDENT Body OUTDENT
    { $$ = $2; }
  ;

Body
  : Line
    { $$ = new yy.Block($1); }
  | Body TERMINATOR Line
    {$$ = $1; $1.add($3);}
  | Body TERMINATOR
  ;

ExprList
  :
  | Expression
    {$$ = [$1];}
  | ExprList TERMINATOR Expression
    {$$ = $1; $1.push($3);}
  | ExprList TERMINATOR
  ;

Line
  : Statement | Expression
  ;

Statement
  : Import | Def | Sig | Where | Return | Halt
  ;

Action
  : Expression
    { $$ = new yy.Action($1); }
  ;

Import
  : IMPORT Expression
    { $$ = new yy.ImportStmt($2); }
  ;

Trigger
  : Expression
    { $$ = new yy.Trigger($1); }
  ;

Def
  : DEF '(' Trigger ')' Block
    { $$ = new yy.Def($3, $5); }
  ;

Sig
  : SIG '(' Trigger ')' Block
    { $$ = new yy.Sig($3, $5); }
  ;

Condition
  : QClause | QNegClause | QFilter
  ;

QClause
  : Clause
    {$$ = new yy.QClause($1);}
  ;

QNegClause
  : NegClause
    {$$ = new yy.QNegClause($1);}
  ;

QFilter
  : Expression
    {$$ = new yy.QFilter($1);}
  ;

Where
  : WHERE INDENT Lhs OUTDENT Rhs
    {$$ = new yy.Query($3, $5);}
  ;

Lhs
  : Condition
    {$$ = new yy.Lhs($1);}
  | Lhs TERMINATOR Condition
    {$$ = $1; $1.add($3);}
  | Lhs TERMINATOR
  ;

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

WhereTrue
  : LONGARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;

WhereFalse
  : NOTARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;

WhereAllTrue
  : LONGFATARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;

WhereAllFalse
  : NOTFATARROW Block
    { $$ = new yy.Actions($2, $1); }
  ;

Expression
  : ParExpr | PrefixExpr | PostfixExpr | BinaryExpr | Paragraph | Terminal
  ;

Terminal
  : Literal | Variable | Term | Snippet | Code
  ;

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

Variable
  : VARIABLE
    { $$ = new yy.Variable($1.slice(1)); }
  ;

Verb
  : VERB
    { $$ = new yy.term_($1); }
  ;

Term
  : NOUN
    { $$ = new yy.term_($1); }
  ;

Snippet
  : SNIPPET
    { $$ = new yy.Snippet($1); }
  ;

Code
  : CODE
    { $$ = new yy.Code($1); }
  ;

Paragraph
: Sentence
  {$$ = $1;}
| Expression '::' INDENT ExprList OUTDENT
  {$$ = new yy.Paragraph($1, $4);}
;

SentenceList
  :
  | Sentence
    {$$ = [$1];}
  | SentenceList TERMINATOR Sentence
    {$$ = $1; $1.push($3);}
  | SentenceList TERMINATOR
  ;

Sentence
  : ClauseExpr
    {$$ = $1;}
  | ClauseExpr '&' AmpList
    {$$ = new yy.Sentence($1, $3);}
  ;

AmpList
  :
  | Expression
    {$$ = [$1];}
  | AmpList '&' Expression
    {$$ = $1; $1.push($3);}
  ;

ClauseExpr
  : Clause
    {$$ = $1;}
  | BindExpr
    {$$ = $1;}
  ;

BindExpr
  : Clause '->' Variable
    { $$ = $1; $1.binding = $3; }
  ;

NegClause
: NotOp Clause
  {$$ = $2;}
;

Clause
  : SimpleClause
    {$$ = $1;}
  | SimpleClause Properties
    {$$ = $1; $1.xtra = $2;}
  ;

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

ObjExpr
  : CommaList
    {$$ = ($1.length == 1 ? $1[0] : new yy.Array($1));}
  ;

CommaList
  :
  | Expression
    {$$ = [$1];}
  | CommaList ',' Expression
    {$$ = $1; $1.push($3);}
  ;

TypeName
  : TYPE
  { $$ = $1.slice(0, -1); }
;

PostTypeName
  : POSTTYPE
  { $$ = $1.slice(1); }
;

PropertyName
  : PROPERTY
  { $$ = $1.slice(0, -1); }
;

Property
  :
  PropertyName
    { $$ = new yy.Property($1); }
  | PropertyName Expression
    { $$ = new yy.Property($1, $2); }
  ;

Properties
  :
    Property
    {$$ = new yy.Properties($1);}
  | Properties Property
    {$$ = $1; $1.add($2);}
  ;

ParExpr
  : '(' ')'
    { $$ = null; }
  | '(' Expression ')'
    { $$ = $2; }
  ;

PrefixExpr
  : Typed | Not | Slash | Message
  ;

Typed
  : TypeName Expression
  { $2.type = yy.type_($1); $$ = $2; }
  ;

NotOp : '!' | NOT ;

Not
  : NotOp Expression
  { $$ = new yy.PrefixExpr($2, $1); }
  ;

Slash
  : '/' Expression
  { $2.slash = true; $$ = $2; }
  ;

Message
  : Propose | Attempt | Assert | Retract | Modify
  ;

Propose
  : '*' Expression
  { $$ = new yy.Propose($2); }
  ;

Attempt
  : '@' Expression
  { $$ = new yy.Attempt($2); }
  ;

Assert
  : '+' Expression
    { $$ = new yy.Assert($2); }
  ;

Retract
  : '-' Expression
  { $$ = new yy.Retract($2); }
  ;

Modify
  : '-+' Expression
  { $$ = new yy.Modify($2); }
  ;

PostfixExpr
  : PostTyped | Achieve
  ;

PostTyped
  : Expression PostTypeName
  { $1.type = yy.type_($2); $$ = $1; }
  ;

Achieve
  : Expression '!'
  { $$ = new yy.PostfixExpr($2, $1); }
  ;

BinaryExpr
  : ContextExpr | InjectExpr | TypeOfExpr | AssignExpr | EqualExpr | NotEqualExpr | InstanceOfExpr
  ;

ContextExpr
  : Expression '<:' INDENT ExprList OUTDENT
    { $$ = new yy.BinaryExpr($1, $4, $2); }
  ;

InjectExpr
  : Expression '<<:' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;

TypeOfExpr
  : Expression '^' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;

AssignExpr
  : Expression '=' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;

EqualExpr
  : Expression '==' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;

NotEqualExpr
  : Expression '!=' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;

InstanceOfExpr
  : Expression 'instanceof' Expression
    { $$ = new yy.BinaryExpr($1, $3, $2); }
  ;

Return
  : RETURN Expression
    { $$ = new yy.Return($2); }
  | RETURN
    { $$ = new yy.Return(null); }
  ;

Halt
  : HALT Expression
    { $$ = new yy.Halt($2); }
  | HALT
    { $$ = new yy.Halt(null); }
  ;
