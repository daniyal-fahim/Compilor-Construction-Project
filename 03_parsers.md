# Parsing Techniques in LogicHorizon

## 1. Introduction

This document provides a comprehensive analysis of the parsing techniques employed in the LogicHorizon compiler. The parser transforms a flat token stream into a hierarchical Abstract Syntax Tree (AST) representation, validating syntactic correctness according to the language grammar. The LogicHorizon parser implements a **recursive descent parsing** strategy based on an LL(1) grammar with explicit operator precedence handling.

---

## 2. Grammar Classification

### 2.1 Grammar Type

The LogicHorizon grammar is classified as **LL(1)**:
- **LL**: Left-to-right scan, Leftmost derivation
- **1**: One token lookahead suffices for parsing decisions

**Key Properties:**
- Deterministic parsing (no backtracking required)
- Efficient O(n) time complexity
- Suitable for hand-written recursive descent parsers
- No left recursion in grammar productions

### 2.2 Extended Backus-Naur Form (EBNF) Grammar

```ebnf
program         ::= stmt_list
stmt_list       ::= stmt stmt_list | ε
stmt            ::= expr_stmt | set_stmt | table_stmt | eval_stmt 
                  | rule_stmt | infer_stmt

expr_stmt       ::= "expr" (ID)? expression ";"
set_stmt        ::= "set" ID "=" BOOL ";"
table_stmt      ::= "table" (ID)? ";"
eval_stmt       ::= "eval" ";"
rule_stmt       ::= ID ":" expression ";"
infer_stmt      ::= "infer" id_list ";"

expression      ::= implication
implication     ::= or_expr ("->" implication)?
or_expr         ::= xor_expr ("|" xor_expr)*
xor_expr        ::= and_expr ("xor" and_expr)*
and_expr        ::= not_expr ("&" not_expr)*
not_expr        ::= "!" not_expr | primary
primary         ::= ID | "(" expression ")" | BOOL
id_list         ::= ID ("," ID)*
```

### 2.3 Grammar Properties Analysis

**Left Recursion Elimination:**

The grammar avoids left recursion, which is incompatible with recursive descent parsing. For example:

❌ Left-recursive (problematic):
```ebnf
or_expr ::= or_expr "|" xor_expr | xor_expr
```

✅ Right-recursive/iterative (implemented):
```ebnf
or_expr ::= xor_expr ("|" xor_expr)*
```

**First and Follow Sets:**

Critical for LL(1) parsing decisions:

| Non-terminal | FIRST | FOLLOW |
|--------------|-------|--------|
| program | {expr, set, table, eval, infer, ID, ε} | {EOF} |
| stmt | {expr, set, table, eval, infer, ID} | {expr, set, table, eval, infer, ID, EOF} |
| expression | {ID, BOOL, !, (} | {;, ), \|, &, ->, xor} |
| primary | {ID, BOOL, (} | {;, ), \|, &, ->, xor} |

---

## 3. Recursive Descent Parsing

### 3.1 Parsing Strategy

**Recursive Descent** is a top-down parsing technique where:
1. Each non-terminal in the grammar has a corresponding parsing function
2. The structure of the function mirrors the grammar production
3. Terminal symbols are matched and consumed
4. Non-terminal symbols trigger recursive function calls

**Advantages:**
- Natural correspondence between grammar and code
- Easy to understand and maintain
- Flexible error recovery and reporting
- No separate parser generator tool needed

**Disadvantages:**
- Grammar must be LL(k) compatible (no left recursion)
- Manual implementation required
- Can be less efficient than table-driven parsers

### 3.2 Implementation Structure

The `Parser` class in `src/parser.py` implements the recursive descent strategy:

```python
class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]
    
    def eat(self, token_type: str):
        """Consume expected token or raise error"""
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error(f"Expected {token_type}, found {self.current_token.type}")
    
    def peek(self) -> Token:
        """Lookahead one token without consuming"""
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]
```

---

## 4. Statement Parsing

### 4.1 Statement Dispatcher

The `parse_stmt()` method implements a dispatcher pattern based on the leading token:

```python
def parse_stmt(self) -> Stmt:
    token_type = self.current_token.type
    
    if token_type == 'KW_EXPR':
        return self.parse_expr_stmt()
    elif token_type == 'KW_SET':
        return self.parse_set_stmt()
    elif token_type == 'KW_TABLE':
        return self.parse_table_stmt()
    elif token_type == 'KW_EVAL':
        return self.parse_eval_stmt()
    elif token_type == 'KW_INFER':
        return self.parse_infer_stmt()
    elif token_type == 'ID':
        # Disambiguate: rule_stmt if followed by ':'
        if self.peek().type == 'COLON':
            return self.parse_rule_stmt()
        else:
            self.error("Unexpected ID")
    else:
        self.error(f"Unexpected token {token_type}")
```

**Parsing Decision Logic:**

The parser uses **one token lookahead** (LL(1)) to distinguish between statement types:

| Current Token | Next Token | Statement Type |
|---------------|------------|----------------|
| `KW_EXPR` | - | `expr_stmt` |
| `KW_SET` | - | `set_stmt` |
| `KW_TABLE` | - | `table_stmt` |
| `KW_EVAL` | - | `eval_stmt` |
| `KW_INFER` | - | `infer_stmt` |
| `ID` | `COLON` | `rule_stmt` |
| `ID` | other | Error |

### 4.2 Statement Production Implementations

#### 4.2.1 Expression Statement

**Grammar:**
```ebnf
expr_stmt ::= "expr" (ID)? expression ";"
```

**Implementation:**
```python
def parse_expr_stmt(self) -> ExprStmt:
    self.eat('KW_EXPR')
    name = None
    
    # Heuristic: If ID followed by expression start, ID is name
    if self.current_token.type == 'ID':
        next_tok = self.peek()
        if next_tok.type in ['ID', 'LPAREN', 'NOT', 'BOOL']:
            name = self.current_token.value
            self.eat('ID')
    
    expr = self.parse_expression()
    self.eat('SEMICOL')
    return ExprStmt(expr, name)
```

**Ambiguity Resolution:**

The optional name creates ambiguity:
- `expr A;` → Could be `ExprStmt(Var('A'), name=None)` or `ExprStmt(???, name='A')`

**Resolution Strategy:**

The parser uses a two-token lookahead heuristic:
- If `ID` is followed by expression-starting tokens (`ID`, `BOOL`, `!`, `(`), the first `ID` is the name
- Otherwise, the `ID` begins the expression

#### 4.2.2 Set Statement

**Grammar:**
```ebnf
set_stmt ::= "set" ID "=" BOOL ";"
```

**Implementation:**
```python
def parse_set_stmt(self) -> SetStmt:
    self.eat('KW_SET')
    name = self.current_token.value
    self.eat('ID')
    self.eat('EQUAL')
    val_token = self.current_token
    self.eat('BOOL')
    self.eat('SEMICOL')
    return SetStmt(name, val_token.value == '1')
```

This is a straightforward sequential parse with no ambiguity.

#### 4.2.3 Table Statement

**Grammar:**
```ebnf
table_stmt ::= "table" (ID)? ";"
```

**Implementation:**
```python
def parse_table_stmt(self) -> TableStmt:
    self.eat('KW_TABLE')
    target_id = None
    if self.current_token.type == 'ID':
        target_id = self.current_token.value
        self.eat('ID')
    self.eat('SEMICOL')
    return TableStmt(target_id)
```

The optional `ID` is handled by checking the current token type before consuming.

#### 4.2.4 Rule Statement

**Grammar:**
```ebnf
rule_stmt ::= ID ":" expression ";"
```

**Implementation:**
```python
def parse_rule_stmt(self) -> RuleStmt:
    name = self.current_token.value
    self.eat('ID')
    self.eat('COLON')
    expr = self.parse_expression()
    self.eat('SEMICOL')
    return RuleStmt(name, expr)
```

#### 4.2.5 Infer Statement

**Grammar:**
```ebnf
infer_stmt ::= "infer" id_list ";"
id_list    ::= ID ("," ID)*
```

**Implementation:**
```python
def parse_infer_stmt(self) -> InferStmt:
    self.eat('KW_INFER')
    rule_names = []
    rule_names.append(self.current_token.value)
    self.eat('ID')
    
    while self.current_token.type == 'COMMA':
        self.eat('COMMA')
        rule_names.append(self.current_token.value)
        self.eat('ID')
    
    self.eat('SEMICOL')
    return InferStmt(rule_names)
```

This demonstrates **repetition parsing** using a while loop to handle the `*` operator in the EBNF grammar.

---

## 5. Expression Parsing with Operator Precedence

### 5.1 Precedence Climbing Technique

Boolean expressions require precedence-aware parsing to correctly associate operators. LogicHorizon implements **precedence climbing** by encoding precedence levels in the grammar hierarchy:

**Precedence Table:**

| Level | Operator | Associativity | Method |
|-------|----------|---------------|--------|
| 1 (low) | `->` | Right | `parse_implication()` |
| 2 | `\|` | Left | `parse_or()` |
| 3 | `xor` | Left | `parse_xor()` |
| 4 | `&` | Left | `parse_and()` |
| 5 (high) | `!` | Right | `parse_not()` |
| 6 (atomic) | ID, BOOL, `()` | - | `parse_primary()` |

**Parsing Strategy:**

Lower precedence operators call higher precedence parsing functions as operands:

```
parse_expression()
    → parse_implication()
        → parse_or()
            → parse_xor()
                → parse_and()
                    → parse_not()
                        → parse_primary()
```

### 5.2 Expression Parsing Methods

#### 5.2.1 Implication (Right-Associative)

**Grammar:**
```ebnf
implication ::= or_expr ("->" implication)?
```

**Implementation:**
```python
def parse_implication(self) -> Expr:
    node = self.parse_or()
    
    if self.current_token.type == 'IMPLIES':
        op = self.current_token.value
        self.eat('IMPLIES')
        right = self.parse_implication()  # Right-associative recursion
        node = BinaryOp(node, op, right)
    
    return node
```

**Right Associativity:**

The recursive call `parse_implication()` on the right side makes `->` right-associative:

```
A -> B -> C
```

Parsed as:
```
BinaryOp(
    left=Var('A'),
    op='->',
    right=BinaryOp(
        left=Var('B'),
        op='->',
        right=Var('C')
    )
)
```

Equivalent to: `A -> (B -> C)`

#### 5.2.2 OR, XOR, AND (Left-Associative)

**Grammar:**
```ebnf
or_expr  ::= xor_expr ("|" xor_expr)*
xor_expr ::= and_expr ("xor" and_expr)*
and_expr ::= not_expr ("&" not_expr)*
```

**Implementation Pattern:**
```python
def parse_or(self) -> Expr:
    node = self.parse_xor()  # Parse left operand
    
    while self.current_token.type == 'OR':  # Left-associative loop
        op = self.current_token.value
        self.eat('OR')
        right = self.parse_xor()
        node = BinaryOp(node, op, right)  # Build left tree
    
    return node
```

**Left Associativity:**

The iterative while loop builds a left-associative tree:

```
A | B | C
```

Parsed as:
```
BinaryOp(
    left=BinaryOp(
        left=Var('A'),
        op='|',
        right=Var('B')
    ),
    op='|',
    right=Var('C')
)
```

Equivalent to: `(A | B) | C`

#### 5.2.3 NOT (Prefix Unary, Right-Associative)

**Grammar:**
```ebnf
not_expr ::= "!" not_expr | primary
```

**Implementation:**
```python
def parse_not(self) -> Expr:
    if self.current_token.type == 'NOT':
        op = self.current_token.value
        self.eat('NOT')
        node = self.parse_not()  # Right-associative recursion
        return UnaryOp(op, node)
    return self.parse_primary()
```

**Right Associativity for Prefix Operators:**

Multiple `!` operators associate right-to-left:

```
!!A
```

Parsed as:
```
UnaryOp(
    op='!',
    operand=UnaryOp(
        op='!',
        operand=Var('A')
    )
)
```

Equivalent to: `!(!(A))`

#### 5.2.4 Primary Expressions

**Grammar:**
```ebnf
primary ::= ID | "(" expression ")" | BOOL
```

**Implementation:**
```python
def parse_primary(self) -> Expr:
    token = self.current_token
    
    if token.type == 'ID':
        self.eat('ID')
        return Var(token.value)
    
    elif token.type == 'BOOL':
        self.eat('BOOL')
        return Literal(token.value == '1')
    
    elif token.type == 'LPAREN':
        self.eat('LPAREN')
        node = self.parse_expression()  # Restart from top precedence
        self.eat('RPAREN')
        return node
    
    else:
        self.error(f"Unexpected token: {token.type}")
```

**Parenthesized Expressions:**

Parentheses reset precedence by calling `parse_expression()`, allowing any expression inside.

---

## 6. AST Construction

### 6.1 AST Node Hierarchy

The parser builds a typed AST using dataclasses defined in `ast_nodes.py`:

```
ASTNode (abstract base)
├── Program(statements: List[Stmt])
├── Stmt (abstract)
│   ├── ExprStmt(expr: Expr, name: Optional[str])
│   ├── SetStmt(name: str, value: bool)
│   ├── TableStmt(target_id: Optional[str])
│   ├── EvalStmt()
│   ├── RuleStmt(name: str, expr: Expr)
│   └── InferStmt(rule_names: List[str])
└── Expr (abstract)
    ├── BinaryOp(left: Expr, op: str, right: Expr)
    ├── UnaryOp(op: str, operand: Expr)
    ├── Var(name: str)
    └── Literal(value: bool)
```

### 6.2 AST Construction Example

**Input Source:**
```
expr result A & (B | !C);
set A = 1;
table result;
```

**Generated AST:**
```python
Program(
    statements=[
        ExprStmt(
            expr=BinaryOp(
                left=Var('A'),
                op='&',
                right=BinaryOp(
                    left=Var('B'),
                    op='|',
                    right=UnaryOp(
                        op='!',
                        operand=Var('C')
                    )
                )
            ),
            name='result'
        ),
        SetStmt(name='A', value=True),
        TableStmt(target_id='result')
    ]
)
```

---

## 7. Error Handling and Recovery

### 7.1 Syntax Error Detection

The parser detects syntax errors through:

1. **Token Mismatch:**
```python
def eat(self, token_type: str):
    if self.current_token.type != token_type:
        self.error(f"Expected {token_type}, found {self.current_token.type}")
```

2. **Unexpected Tokens:**
```python
def parse_stmt(self):
    if self.current_token.type not in VALID_STMT_STARTS:
        self.error(f"Unexpected token {self.current_token.type}")
```

### 7.2 Error Messages

Error messages include positional information from tokens:

```python
def error(self, msg: str):
    raise Exception(
        f"Parser Error at {self.current_token.line}:{self.current_token.column}: {msg}"
    )
```

**Example Error Output:**
```
Input: "expr A & ;"
Error: Parser Error at 1:10: Unexpected token in expression: SEMICOL
```

### 7.3 Error Recovery

The current implementation uses **panic mode recovery**:
- On error, raises an exception and terminates parsing
- No attempt to synchronize and continue parsing
- Suitable for batch compilation where first error stops processing

**Potential Improvements:**
- Synchronization on statement boundaries (semicolons)
- Error production rules for common mistakes
- Multiple error reporting before termination

---

## 8. Parsing Complexity Analysis

### 8.1 Time Complexity

**O(n)** where n is the number of tokens:
- Each token is consumed exactly once
- No backtracking
- Constant work per token (assuming hash table lookups for keywords)

### 8.2 Space Complexity

**O(d)** where d is the maximum nesting depth:
- Recursive descent uses call stack
- Stack depth equals maximum expression nesting
- AST size is O(n) for n tokens

### 8.3 Grammar Characteristics

| Property | Value |
|----------|-------|
| Grammar Class | LL(1) |
| Lookahead | 1 token (occasionally 2 for disambiguation) |
| Left Recursion | None |
| Ambiguity | Minimal (resolved by lookahead) |
| Operator Precedence Levels | 5 |

---

## 9. Comparison with Alternative Parsing Techniques

### 9.1 Recursive Descent vs. Alternatives

| Technique | Advantages | Disadvantages |
|-----------|------------|---------------|
| **Recursive Descent** (Used) | Simple, maintainable, flexible error handling | Requires LL grammar, manual implementation |
| **LL Parser Generator** | Automated, table-driven | Less flexible, requires separate tool |
| **LR Parser (YACC/Bison)** | Handles more grammars, efficient | Complex, harder to debug, requires generator |
| **PEG Parser** | Handles ambiguity naturally | Backtracking overhead |
| **Pratt Parsing** | Elegant precedence handling | Less familiar to students |

### 9.2 Why Recursive Descent for LogicHorizon?

1. **Educational Clarity**: Direct correspondence between grammar and code
2. **Simplicity**: No external tools required
3. **Grammar Compatibility**: LogicHorizon grammar is naturally LL(1)
4. **Maintainability**: Easy to modify and extend
5. **Error Reporting**: Simple to provide detailed error messages

---

## 10. Conclusion

The LogicHorizon parser demonstrates a well-structured implementation of recursive descent parsing with explicit precedence handling. The design choices—LL(1) grammar, precedence climbing, and single-pass parsing—provide an excellent balance of simplicity, efficiency, and educational value. The clear correspondence between grammar productions and parsing methods makes the parser easy to understand and maintain, while the O(n) time complexity ensures efficient processing of source programs.

The parsing technique successfully handles the core challenges of expression parsing: operator precedence, associativity, and syntactic ambiguity resolution. This implementation serves as a solid foundation for students learning compiler construction, demonstrating practical application of parsing theory in a real-world compiler context.
