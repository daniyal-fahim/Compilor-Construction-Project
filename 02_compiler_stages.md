# Compiler Stages: LogicEval Implementation

## Introduction

This document provides a detailed examination of each compilation stage in the LogicEval compiler, including theoretical foundations, implementation details, and the transformations performed at each phase. The LogicEval compiler implements all six classical phases of compilation, demonstrating a complete compilation pipeline from source text to executable intermediate representation.

---

## Phase 1: Lexical Analysis (Scanning)

### Theoretical Foundation

Lexical analysis is the initial phase of compilation that transforms a sequence of characters into a sequence of lexical tokens. This phase implements finite automata (DFA/NFA) to recognize token patterns defined by regular expressions. The lexer performs linear scanning with O(n) complexity, where n is the input length.

### Implementation: `src/lexer.py`

**Key Components:**

1. **Token Class**: Represents a lexical unit with attributes:
   - `type`: Token category (e.g., `ID`, `KW_EXPR`, `AND`)
   - `value`: Actual text of the token
   - `line`: Line number for error reporting
   - `column`: Column position for precise diagnostics

2. **Lexer Class**: State machine for token recognition
   - Maintains position (`pos`), line, and column counters
   - Implements character-by-character scanning
   - Recognizes keywords, operators, identifiers, and literals

**Token Categories:**

| Category | Pattern | Examples |
|----------|---------|----------|
| Keywords | Reserved words | `expr`, `set`, `table`, `eval`, `infer` |
| Identifiers | `[A-Za-z][A-Za-z0-9_]*` | `A`, `var1`, `rule_x` |
| Booleans | `[01]` | `0`, `1` |
| Operators | Single/multi-char | `&`, `|`, `!`, `->`, `xor`, `^` |
| Delimiters | Single characters | `(`, `)`, `;`, `:`, `,`, `=` |
| Whitespace | Spaces, tabs, newlines | (Ignored) |

**Algorithm:**

```
while position < input_length:
    skip whitespace
    if current_char is alphabetic:
        scan identifier or keyword
        check against keyword table
        emit appropriate token
    elif current_char is digit ('0' or '1'):
        emit BOOL token
    elif current_char is operator character:
        check for multi-character operators (->)
        emit operator token
    elif current_char is delimiter:
        emit delimiter token
    else:
        raise lexical error
```

**Key Features:**
- Single-pass scanning
- Lookahead for multi-character operators (`->`)
- Position tracking for error diagnostics
- Keyword recognition via post-processing identifier tokens

**Example Transformation:**

```
Input:  "expr A & B;"
Output: [
    Token(KW_EXPR, 'expr', 1, 1),
    Token(ID, 'A', 1, 6),
    Token(AND, '&', 1, 8),
    Token(ID, 'B', 1, 10),
    Token(SEMICOL, ';', 1, 11),
    Token(EOF, '', 1, 12)
]
```

---

## Phase 2: Syntax Analysis (Parsing)

### Theoretical Foundation

Syntax analysis verifies that the token sequence conforms to the language grammar and constructs an Abstract Syntax Tree (AST). The LogicEval parser implements a **recursive descent parser** based on an LL(1) grammar, where parsing decisions are made by examining one token of lookahead.

### Grammar Specification (EBNF)

```ebnf
program         ::= stmt_list
stmt_list       ::= stmt stmt_list | ε
stmt            ::= expr_stmt | set_stmt | table_stmt | eval_stmt | rule_stmt | infer_stmt

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

### Operator Precedence and Associativity

| Precedence | Operator | Associativity | Description |
|------------|----------|---------------|-------------|
| 1 (lowest) | `->` | Right | Implication |
| 2 | `|` | Left | Disjunction (OR) |
| 3 | `xor`, `^` | Left | Exclusive OR |
| 4 | `&` | Left | Conjunction (AND) |
| 5 (highest) | `!` | Right | Negation (NOT) |

### Implementation: `src/parser.py`

**Key Components:**

1. **Parser Class**: Implements recursive descent parsing
   - `tokens`: Input token stream
   - `pos`: Current position in token stream
   - `current_token`: Lookahead token

2. **Parsing Methods**: One method per grammar production
   - `parse()`: Entry point, returns `Program` AST node
   - `parse_stmt()`: Statement dispatcher
   - `parse_expression()`: Expression parsing with precedence
   - `parse_primary()`: Atomic expressions
   - `eat(token_type)`: Consumes expected token or raises error

**Recursive Descent Strategy:**

Each non-terminal in the grammar corresponds to a parsing method:

```python
def parse_implication():
    left = parse_or()                    # Parse left operand
    if current_token == '->':            # Check for operator
        eat('->')                         # Consume operator
        right = parse_implication()       # Right-associative recursion
        return BinaryOp(left, '->', right)
    return left

def parse_or():
    left = parse_xor()                   # Parse left operand
    while current_token == '|':          # Left-associative loop
        eat('|')
        right = parse_xor()
        left = BinaryOp(left, '|', right)
    return left
```

**AST Construction:**

The parser builds a tree of AST nodes defined in `ast_nodes.py`:

- **Program**: Root node containing statement list
- **Statement Nodes**: `ExprStmt`, `SetStmt`, `TableStmt`, `EvalStmt`, `RuleStmt`, `InferStmt`
- **Expression Nodes**: `BinaryOp`, `UnaryOp`, `Var`, `Literal`

**Example Transformation:**

```
Input Tokens: [KW_EXPR, ID('A'), AND, ID('B'), SEMICOL, EOF]

Output AST:
Program(
    statements=[
        ExprStmt(
            expr=BinaryOp(
                left=Var('A'),
                op='&',
                right=Var('B')
            ),
            name=None
        )
    ]
)
```

---

## Phase 3: Semantic Analysis

### Theoretical Foundation

Semantic analysis performs context-sensitive checks that cannot be expressed in context-free grammars. This phase ensures type correctness, variable declarations, scope resolution, and semantic constraints. The LogicEval analyzer implements the **Visitor Pattern** for AST traversal.

### Implementation: `src/semantic.py`

**Key Components:**

1. **SemanticAnalyzer Class**: AST visitor implementing semantic checks
   - `declared_vars`: Set of variables assigned via `set` statements
   - `defined_rules`: Set of rule names defined via `rule_stmt`

2. **Visitor Methods**: One method per AST node type
   - `visit(node)`: Dispatcher method using reflection
   - `visit_Program(node)`: Traverses all statements
   - `visit_RuleStmt(node)`: Checks for duplicate rule definitions
   - `visit_InferStmt(node)`: Verifies rule existence

**Semantic Checks Performed:**

1. **Rule Definition Uniqueness**
   - Ensures each rule name is defined only once
   - Error: `"Rule 'X' already defined"`

2. **Rule Reference Validation**
   - Verifies that `infer` statements reference existing rules
   - Error: `"Inference on undefined rule 'X'"`

3. **Variable Usage Tracking**
   - LogicEval allows implicit variable declaration
   - Variables in expressions need not be explicitly declared
   - `set` statements register variables in symbol table

**Traversal Algorithm:**

```python
def visit(node):
    method_name = 'visit_' + node.__class__.__name__
    visitor_method = getattr(self, method_name)
    return visitor_method(node)

def visit_RuleStmt(node):
    if node.name in self.defined_rules:
        raise Exception(f"Rule '{node.name}' already defined")
    self.defined_rules.add(node.name)
    self.visit(node.expr)  # Recursively check expression
```

**Example Validation:**

```
Input AST:
Program([
    RuleStmt(name='R1', expr=Var('A')),
    RuleStmt(name='R1', expr=Var('B')),  # Error: duplicate
    InferStmt(rule_names=['R2'])          # Error: R2 undefined
])

Output: Semantic errors detected and raised
```

---

## Phase 4: Intermediate Code Generation

### Theoretical Foundation

Intermediate code generation translates the AST into an intermediate representation (IR) that is machine-independent and facilitates optimization. The LogicEval compiler generates **Three-Address Code (3AC)**, a linearized form where each instruction performs at most one operation and has up to three operands.

### Three-Address Code Format

**Generic Format:**
```
result = operator operand1 operand2
```

**LogicEval 3AC Instructions:**

| Instruction Format | Description | Example |
|-------------------|-------------|---------|
| `t1 = AND A B` | Binary AND operation | `t1 = AND A B` |
| `t2 = OR t1 C` | Binary OR operation | `t2 = OR t1 C` |
| `t3 = NOT A` | Unary NOT operation | `t3 = NOT A` |
| `t4 = IMPLIES A B` | Implication | `t4 = IMPLIES A B` |
| `t5 = XOR A B` | Exclusive OR | `t5 = XOR A B` |
| `A = 1` | Variable assignment | `A = 1` |
| `expr1 = t5` | Named expression storage | `expr1 = t5` |
| `TABLE expr1` | Truth table directive | `TABLE expr1` |
| `EVAL` | Evaluation directive | `EVAL` |
| `INFER R1 R2` | Inference directive | `INFER R1 R2` |

### Implementation: `src/ir_generator.py`

**Key Components:**

1. **IRGenerator Class**: AST-to-3AC translator
   - `temp_counter`: Generates unique temporary variable names
   - `code`: Accumulates generated 3AC instructions
   - `new_temp()`: Returns next temporary (`t1`, `t2`, ...)

2. **Generation Methods**: Visitor pattern for AST nodes
   - `generate(node)`: Entry point
   - `visit_expression(node)`: Recursively generates code for expressions
   - Returns temporary variable holding expression result

**Translation Algorithm:**

```python
def visit_expression(node: BinaryOp) -> str:
    left_temp = visit_expression(node.left)    # Get left operand
    right_temp = visit_expression(node.right)  # Get right operand
    result_temp = new_temp()                   # Allocate result temp
    emit(f"{result_temp} = {node.op} {left_temp} {right_temp}")
    return result_temp                         # Return result location
```

**Example Transformation:**

```
Input AST:
ExprStmt(
    expr=BinaryOp(
        left=BinaryOp(
            left=Var('A'),
            op='&',
            right=Var('B')
        ),
        op='|',
        right=Var('C')
    )
)

Generated 3AC:
t1 = AND A B
t2 = OR t1 C
```

**Statement Translation:**

- **SetStmt**: `A = 1`
- **ExprStmt**: Sequence of expression operations, optionally assigning to named expression
- **TableStmt**: `TABLE <target_id>`
- **EvalStmt**: `EVAL`
- **RuleStmt**: Generate expression code and assign to rule name
- **InferStmt**: `INFER R1 R2 ...`

---

## Phase 5: Code Optimization

### Theoretical Foundation

Code optimization transforms intermediate code to improve execution efficiency while preserving semantic equivalence. The LogicEval optimizer performs **peephole optimization**, examining small windows of instructions to apply local transformations based on algebraic identities.

### Implementation: `src/optimizer.py`

**Optimization Techniques:**

#### 5.1 Constant Folding

Evaluates operations with constant operands at compile time.

| Original | Optimized | Rule |
|----------|-----------|------|
| `t1 = AND 0 X` | `t1 = 0` | 0 ∧ X = 0 |
| `t1 = AND 1 1` | `t1 = 1` | 1 ∧ 1 = 1 |
| `t1 = OR 1 X` | `t1 = 1` | 1 ∨ X = 1 |
| `t1 = OR 0 0` | `t1 = 0` | 0 ∨ 0 = 0 |
| `t1 = NOT 0` | `t1 = 1` | ¬0 = 1 |
| `t1 = NOT 1` | `t1 = 0` | ¬1 = 0 |
| `t1 = XOR 0 0` | `t1 = 0` | 0 ⊕ 0 = 0 |
| `t1 = XOR 1 1` | `t1 = 0` | 1 ⊕ 1 = 0 |
| `t1 = XOR 0 1` | `t1 = 1` | 0 ⊕ 1 = 1 |

#### 5.2 Identity Law Simplification

Applies boolean algebra identities to eliminate redundant operations.

| Original | Optimized | Rule |
|----------|-----------|------|
| `t1 = AND X 1` | `t1 = X` | X ∧ 1 = X |
| `t1 = AND 1 X` | `t1 = X` | 1 ∧ X = X |
| `t1 = OR X 0` | `t1 = X` | X ∨ 0 = X |
| `t1 = OR 0 X` | `t1 = X` | 0 ∨ X = X |
| `t1 = XOR X 0` | `t1 = X` | X ⊕ 0 = X |
| `t1 = XOR 0 X` | `t1 = X` | 0 ⊕ X = X |

**Optimization Algorithm:**

```python
def optimize(code):
    optimized = []
    for instruction in code:
        if is_binary_operation(instruction):
            op, arg1, arg2 = parse_instruction(instruction)
            
            # Constant folding
            if is_constant(arg1) and is_constant(arg2):
                result = evaluate(op, arg1, arg2)
                emit(f"{target} = {result}")
                continue
            
            # Identity laws
            if is_identity_case(op, arg1, arg2):
                emit(simplified_instruction)
                continue
        
        optimized.append(instruction)
    return optimized
```

**Example Optimization:**

```
Original 3AC:
t1 = AND A 1
t2 = OR t1 0
t3 = XOR B B
t4 = AND 0 C

Optimized 3AC:
t1 = A
t2 = t1
t3 = 0
t4 = 0
```

**Limitations:**

The current optimizer performs single-pass peephole optimization. More advanced optimizations not implemented include:
- Dead code elimination
- Common subexpression elimination
- Algebraic simplification across multiple instructions (e.g., `X ⊕ X = 0`)
- Temporary variable propagation

---

## Phase 6: Code Execution (Interpretation)

### Theoretical Foundation

The final phase executes the optimized intermediate code. Unlike traditional compilers that generate machine code, LogicEval interprets 3AC directly. The interpreter maintains a runtime environment with variable bindings and implements specialized execution modes.

### Implementation: `src/interpreter.py`

**Key Components:**

1. **Interpreter Class**: Runtime execution engine
   - `variables`: Symbol table mapping variable names to boolean values
   - `rules`: Storage for computed rule results
   - `last_ir`: Cache of most recently executed expression
   - `saved_code`: Map of named expressions to their 3AC

2. **Execution Modes:**
   - **Direct Evaluation**: Execute code with current variable values
   - **Truth Table Generation**: Exhaustively enumerate variable assignments
   - **Rule Inference**: Display values of specified rules

**Execution Algorithm (Direct Evaluation):**

```python
def run_code(code, local_vars=None):
    context = merge(global_variables, local_vars)
    temps = {}
    
    for instruction in code:
        if instruction is binary_operation:
            result = temps[target] = evaluate_operation(op, arg1, arg2)
        elif instruction is assignment:
            variables[target] = get_value(source)
        elif instruction is directive:
            handle_directive(instruction)
    
    return last_result
```

**Truth Table Generation:**

```python
def handle_table(code, target_id):
    input_vars = extract_variables(code)
    sorted_vars = sort(input_vars)
    
    print_header(sorted_vars)
    
    # Enumerate all 2^n boolean assignments
    for assignment in product([0, 1], repeat=len(sorted_vars)):
        local_context = dict(zip(sorted_vars, assignment))
        result = run_code(code, local_context)
        print_row(assignment, result)
```

**Example Execution:**

```
Input 3AC:
A = 1
B = 0
t1 = AND A B
t2 = OR t1 B
EVAL

Execution Trace:
1. Set A = 1
2. Set B = 0
3. Compute t1 = 1 AND 0 = 0
4. Compute t2 = 0 OR 0 = 0
5. Print result: 0
```

**Truth Table Example:**

```
Input: expr A & B; table;

Generated 3AC:
t1 = AND A B
TABLE LAST_EXPR

Execution Output:
A | B | Result
--------------
0 | 0 | 0
0 | 1 | 0
1 | 0 | 0
1 | 1 | 1
```

---

## Summary of Phase Interactions

| Phase | Input | Output | Key Transformation |
|-------|-------|--------|-------------------|
| Lexical Analysis | Character stream | Token stream | Text → Tokens |
| Syntax Analysis | Token stream | AST | Tokens → Tree structure |
| Semantic Analysis | AST | Validated AST | Validation checks |
| IR Generation | AST | 3AC | Tree → Linear code |
| Optimization | 3AC | Optimized 3AC | Code improvement |
| Interpretation | 3AC | Program output | Execution |

Each phase operates independently with well-defined input/output contracts, demonstrating the modularity of compiler design. This separation enables independent testing, maintenance, and potential replacement of individual phases (e.g., replacing interpretation with code generation).

---

## Conclusion

The LogicEval compiler implements a complete, pedagogically-oriented compilation pipeline. Each phase demonstrates fundamental compiler construction techniques: finite automata in lexical analysis, recursive descent parsing, tree-based semantic checking, AST-to-IR translation, peephole optimization, and direct interpretation. This architecture provides a comprehensive foundation for understanding modern compiler implementation.
