# Charts and Diagrams: LogicHorizon Compiler

## 1. Introduction

This document provides visual representations of the LogicHorizon compiler's architecture, workflows, and internal structures. These diagrams illustrate the compilation pipeline, data transformations, parsing algorithms, and execution flows to provide a comprehensive visual understanding of the system.

---

## 2. Compiler Architecture Overview

### 2.1 High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        LogicHorizon Compiler                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐      ┌──────────────┐      ┌──────────────┐ │
│   │   Source    │──▶   │   FRONTEND   │──▶   │   BACKEND    │ │
│   │    Code     │      │   (Analysis) │      │  (Synthesis) │ │
│   └─────────────┘      └──────────────┘      └──────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

FRONTEND COMPONENTS:              BACKEND COMPONENTS:
┌──────────────────┐              ┌──────────────────┐
│ Lexical Analyzer │              │  IR Generator    │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
┌────────▼─────────┐              ┌────────▼─────────┐
│  Syntax Analyzer │              │    Optimizer     │
└────────┬─────────┘              └────────┬─────────┘
         │                                 │
┌────────▼─────────┐              ┌────────▼─────────┐
│ Semantic Analyzer│              │   Interpreter    │
└──────────────────┘              └──────────────────┘
```

### 2.2 Detailed Compilation Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                      COMPILATION PIPELINE                        │
└──────────────────────────────────────────────────────────────────┘

INPUT: "expr A & B;"
   │
   │  ┌─────────────────────────────────────┐
   ├─▶│  PHASE 1: Lexical Analysis          │
   │  │  Module: lexer.py                   │
   │  │  Function: Tokenization             │
   │  └─────────────────────────────────────┘
   │
   ▼  Tokens: [KW_EXPR, ID(A), AND, ID(B), SEMICOL, EOF]
   │
   │  ┌─────────────────────────────────────┐
   ├─▶│  PHASE 2: Syntax Analysis           │
   │  │  Module: parser.py                  │
   │  │  Function: AST Construction         │
   │  └─────────────────────────────────────┘
   │
   ▼  AST: ExprStmt(BinaryOp(Var(A), '&', Var(B)))
   │
   │  ┌─────────────────────────────────────┐
   ├─▶│  PHASE 3: Semantic Analysis         │
   │  │  Module: semantic.py                │
   │  │  Function: Validation               │
   │  └─────────────────────────────────────┘
   │
   ▼  Validated AST
   │
   │  ┌─────────────────────────────────────┐
   ├─▶│  PHASE 4: IR Generation             │
   │  │  Module: ir_generator.py            │
   │  │  Function: 3AC Translation          │
   │  └─────────────────────────────────────┘
   │
   ▼  3AC: ["t1 = AND A B"]
   │
   │  ┌─────────────────────────────────────┐
   ├─▶│  PHASE 5: Optimization              │
   │  │  Module: optimizer.py               │
   │  │  Function: Code Improvement         │
   │  └─────────────────────────────────────┘
   │
   ▼  Optimized 3AC: ["t1 = AND A B"]
   │
   │  ┌─────────────────────────────────────┐
   └─▶│  PHASE 6: Interpretation            │
      │  Module: interpreter.py             │
      │  Function: Execution                │
      └─────────────────────────────────────┘
      │
      ▼
   OUTPUT: Truth Table / Evaluation Result
```

---

## 3. Data Flow Diagrams

### 3.1 Token Flow Through Lexer

```
INPUT: "set A = 1;"

┌──────────────────────────────────────────────────┐
│           LEXICAL ANALYSIS PROCESS               │
└──────────────────────────────────────────────────┘

Character Stream: 's' 'e' 't' ' ' 'A' ' ' '=' ' ' '1' ';'
                  │   │   │   │   │   │   │   │   │   │
                  └───┴───┴───┘   │   │   │   │   │   │
                        │         │   │   │   │   │   │
                   ┌────▼────┐    │   │   │   │   │   │
                   │ Keyword │    │   │   │   │   │   │
                   │  Check  │    │   │   │   │   │   │
                   └────┬────┘    │   │   │   │   │   │
                        │         │   │   │   │   │   │
                   Token('KW_SET', 'set', 1, 1)
                                   │   │   │   │   │   │
                                   └───┘   │   │   │   │
                                     │     │   │   │   │
                                ┌────▼────┐│   │   │   │
                                │  Alpha  ││   │   │   │
                                │  Check  ││   │   │   │
                                └────┬────┘│   │   │   │
                                     │     │   │   │   │
                                Token('ID', 'A', 1, 5)
                                           │   │   │   │
                                           │   │   │   │
                                    Token('EQUAL', '=', 1, 7)
                                               │   │   │
                                        Token('BOOL', '1', 1, 9)
                                                   │   │
                                           Token('SEMICOL', ';', 1, 10)

OUTPUT: [Token(KW_SET), Token(ID), Token(EQUAL), Token(BOOL), Token(SEMICOL), Token(EOF)]
```

### 3.2 AST Construction Flow

```
INPUT TOKENS: [KW_EXPR, ID(A), OR, ID(B), SEMICOL]

┌────────────────────────────────────────────────────┐
│              PARSING & AST CONSTRUCTION            │
└────────────────────────────────────────────────────┘

parse()
  │
  └─▶ parse_stmt()
        │
        └─▶ parse_expr_stmt()
              │
              ├─▶ eat(KW_EXPR)        [consume 'expr']
              │
              └─▶ parse_expression()
                    │
                    └─▶ parse_implication()
                          │
                          └─▶ parse_or()
                                │
                                ├─▶ parse_xor()
                                │     │
                                │     └─▶ parse_and()
                                │           │
                                │           └─▶ parse_not()
                                │                 │
                                │                 └─▶ parse_primary()
                                │                       │
                                │                       └─▶ Var('A')
                                │
                                ├─▶ eat(OR)      [consume '|']
                                │
                                └─▶ parse_xor()
                                      │
                                      └─▶ ... → Var('B')

RESULTING AST:

         ExprStmt
            │
            ├─ name: None
            │
            └─ expr: BinaryOp
                      │
                      ├─ left: Var('A')
                      ├─ op: '|'
                      └─ right: Var('B')
```

### 3.3 Three-Address Code Generation

```
INPUT AST: BinaryOp(Var('A'), '&', BinaryOp(Var('B'), '|', Var('C')))

┌──────────────────────────────────────────────────────┐
│          IR GENERATION (POST-ORDER TRAVERSAL)        │
└──────────────────────────────────────────────────────┘

                    BinaryOp(&)
                    /         \
                Var(A)      BinaryOp(|)
                             /        \
                         Var(B)     Var(C)

TRAVERSAL ORDER (Post-Order):
1. Visit Var(B)      → Return: "B"
2. Visit Var(C)      → Return: "C"
3. Visit BinaryOp(|) → Generate: "t1 = OR B C"    Return: "t1"
4. Visit Var(A)      → Return: "A"
5. Visit BinaryOp(&) → Generate: "t2 = AND A t1"  Return: "t2"

OUTPUT 3AC:
┌──────────────────┐
│ t1 = OR B C      │
│ t2 = AND A t1    │
└──────────────────┘
```

---

## 4. Parsing Diagrams

### 4.1 Recursive Descent Parse Tree

```
INPUT: "A & B | C"

PARSE TREE CONSTRUCTION:

                        expression
                            │
                      implication
                            │
                         or_expr
                        /   │   \
                   xor_expr '|' xor_expr
                      │            │
                   and_expr     and_expr
                   /   │   \       │
              not_expr '&' not_expr  not_expr
                 │          │          │
              primary    primary    primary
                 │          │          │
              Var(A)     Var(B)     Var(C)

RESULTING AST:

            BinaryOp(|)
            /          \
      BinaryOp(&)      Var(C)
       /      \
   Var(A)   Var(B)
```

### 4.2 Operator Precedence Tree

```
EXPRESSION: "!A & B | C -> D"

PRECEDENCE LEVELS (1=lowest, 5=highest):

Level 1: →   (Implication)
Level 2: |   (OR)
Level 3: xor (XOR)
Level 4: &   (AND)
Level 5: !   (NOT)

PRECEDENCE-AWARE PARSE TREE:

                  BinaryOp(->)                  ← Level 1
                  /          \
           BinaryOp(|)        Var(D)            ← Level 2
           /          \
      BinaryOp(&)     Var(C)                    ← Level 4
       /      \
   UnaryOp(!)  Var(B)                           ← Level 5
       |
    Var(A)

EVALUATION ORDER: 
1. !A
2. (!A) & B
3. ((!A) & B) | C
4. (((!A) & B) | C) -> D
```

### 4.3 Left vs Right Associativity

```
LEFT-ASSOCIATIVE (OR):
Expression: "A | B | C"

Parse Tree:
      BinaryOp(|)
      /          \
  BinaryOp(|)    Var(C)
   /      \
Var(A)   Var(B)

Equivalent: (A | B) | C


RIGHT-ASSOCIATIVE (IMPLIES):
Expression: "A -> B -> C"

Parse Tree:
  BinaryOp(->)
   /         \
Var(A)    BinaryOp(->)
           /         \
        Var(B)     Var(C)

Equivalent: A -> (B -> C)
```

---

## 5. Finite Automata Diagrams

### 5.1 DFA for Identifiers

```
┌──────────────────────────────────────────┐
│  DFA: Identifier Recognition             │
│  Pattern: [A-Za-z][A-Za-z0-9_]*         │
└──────────────────────────────────────────┘

         [A-Za-z]          [A-Za-z0-9_]
  ┌───┐  ───────▶  ┌───┐  ────────────▶  ┌───┐
  │ 0 │            │ 1 │  ◄────────────   │ 1 │  (ACCEPT)
  └───┘            └───┘                  └───┘
 START                ^                     │
                      └─────────────────────┘

States:
  0: Initial state
  1: Accept state (valid identifier)

Transitions:
  0 → 1: [A-Za-z]         (first character must be letter)
  1 → 1: [A-Za-z0-9_]     (subsequent characters can include digits/underscore)

Examples:
  "A"      → ACCEPT
  "var1"   → ACCEPT
  "rule_X" → ACCEPT
  "1var"   → REJECT (starts with digit)
  "_test"  → REJECT (starts with underscore)
```

### 5.2 DFA for Boolean Literals

```
┌──────────────────────────────────────────┐
│  DFA: Boolean Literal Recognition        │
│  Pattern: 0 | 1                          │
└──────────────────────────────────────────┘

            '0'
        ┌────────┐
  ┌───┐ │        ▼
  │ 0 │           ┌───┐
  └───┘           │ 1 │  (ACCEPT)
 START  │        └───┘
        └────────┐
            '1'  │
                 ▼
                ┌───┐
                │ 2 │  (ACCEPT)
                └───┘

States:
  0: Initial state
  1: Accept state (recognized '0')
  2: Accept state (recognized '1')

Transitions:
  0 → 1: '0'
  0 → 2: '1'

Examples:
  "0" → ACCEPT (Boolean false)
  "1" → ACCEPT (Boolean true)
  "2" → REJECT
```

### 5.3 DFA for Implication Operator

```
┌──────────────────────────────────────────┐
│  DFA: Implication Operator Recognition   │
│  Pattern: ->                             │
└──────────────────────────────────────────┘

         '-'           '>'
  ┌───┐ ────▶  ┌───┐ ────▶  ┌───┐
  │ 0 │        │ 1 │        │ 2 │  (ACCEPT)
  └───┘        └───┘        └───┘
 START

States:
  0: Initial state
  1: Intermediate state (seen '-')
  2: Accept state (recognized '->')

Transitions:
  0 → 1: '-'
  1 → 2: '>'

Examples:
  "->"  → ACCEPT (Implication operator)
  "-"   → REJECT (incomplete)
  "-x"  → REJECT (invalid second character)
```

---

## 6. Optimization Flowcharts

### 6.1 Constant Folding Algorithm

```
┌────────────────────────────────────────────────────┐
│         CONSTANT FOLDING OPTIMIZATION              │
└────────────────────────────────────────────────────┘

START
  │
  ▼
┌───────────────────────┐
│ Parse Instruction     │
│ Format: res = OP a b  │
└───────┬───────────────┘
        │
        ▼
    ┌──────────────┐
    │ Is OP binary?│──── NO ───▶ [Check Unary Ops]
    └──────┬───────┘
           │ YES
           ▼
    ┌──────────────────────┐
    │ Are a and b both     │──── NO ───▶ [Skip Optimization]
    │ constants (0 or 1)?  │
    └──────┬───────────────┘
           │ YES
           ▼
    ┌──────────────────────┐
    │  Evaluate Result     │
    │  Based on Operator   │
    └──────┬───────────────┘
           │
           ├─── AND ──▶ result = a & b
           ├─── OR  ──▶ result = a | b
           ├─── XOR ──▶ result = a ^ b
           └─── IMPL ─▶ result = !a | b
           │
           ▼
    ┌──────────────────────┐
    │ Replace instruction  │
    │ with: res = result   │
    └──────┬───────────────┘
           │
           ▼
         END

EXAMPLE:
  Input:  t1 = AND 1 0
  Output: t1 = 0
```

### 6.2 Identity Law Simplification

```
┌────────────────────────────────────────────────────┐
│       IDENTITY LAW SIMPLIFICATION                  │
└────────────────────────────────────────────────────┘

START
  │
  ▼
┌─────────────────────┐
│ Parse Instruction   │
│ res = OP arg1 arg2  │
└─────────┬───────────┘
          │
          ▼
     Is OP = AND?
     /          \
   YES           NO
    │             │
    ▼             ▼
┌──────────┐   Is OP = OR?
│ arg1='1'?│   /          \
│  or      │ YES           NO
│ arg2='1'?│  │             │
└────┬─────┘  ▼             ▼
     │    ┌──────────┐   Is OP = XOR?
  YES│    │ arg1='0'?│        │
     │    │  or      │     [Continue]
     ▼    │ arg2='0'?│
┌─────────┐└────┬─────┘
│Replace  │     │
│res=other│  YES│
└─────────┘     ▼
           ┌─────────┐
           │Replace  │
           │res=other│
           └─────────┘

EXAMPLES:
  Input:  t1 = AND A 1    →  Output: t1 = A
  Input:  t2 = OR B 0     →  Output: t2 = B
  Input:  t3 = XOR C 0    →  Output: t3 = C
```

---

## 7. Execution Flow Diagrams

### 7.1 Truth Table Generation

```
┌─────────────────────────────────────────────────────┐
│           TRUTH TABLE GENERATION FLOW               │
└─────────────────────────────────────────────────────┘

INPUT: "expr A & B; table;"
  │
  └─▶ Compile to 3AC: ["t1 = AND A B", "TABLE LAST_EXPR"]
        │
        ▼
     ┌────────────────────────────────┐
     │ Extract Input Variables        │
     │ from 3AC                       │
     │ Found: {A, B}                  │
     └────────┬───────────────────────┘
              │
              ▼
     ┌────────────────────────────────┐
     │ Generate All Permutations      │
     │ 2^n combinations               │
     │ n = 2 variables                │
     └────────┬───────────────────────┘
              │
              ▼
     ┌────────────────────────────────┐
     │ Iteration 1: A=0, B=0          │
     │ Execute 3AC                    │
     │ Result: t1 = 0 AND 0 = 0       │
     │ Print: 0 | 0 | 0               │
     └────────┬───────────────────────┘
              │
              ▼
     ┌────────────────────────────────┐
     │ Iteration 2: A=0, B=1          │
     │ Execute 3AC                    │
     │ Result: t1 = 0 AND 1 = 0       │
     │ Print: 0 | 1 | 0               │
     └────────┬───────────────────────┘
              │
              ▼
     ┌────────────────────────────────┐
     │ Iteration 3: A=1, B=0          │
     │ Execute 3AC                    │
     │ Result: t1 = 1 AND 0 = 0       │
     │ Print: 1 | 0 | 0               │
     └────────┬───────────────────────┘
              │
              ▼
     ┌────────────────────────────────┐
     │ Iteration 4: A=1, B=1          │
     │ Execute 3AC                    │
     │ Result: t1 = 1 AND 1 = 1       │
     │ Print: 1 | 1 | 1               │
     └────────┬───────────────────────┘
              │
              ▼
           END

OUTPUT:
A | B | Result
--------------
0 | 0 | 0
0 | 1 | 0
1 | 0 | 0
1 | 1 | 1
```

### 7.2 REPL Execution Flow

```
┌─────────────────────────────────────────────────────┐
│              REPL (Interactive Mode)                │
└─────────────────────────────────────────────────────┘

     START
       │
       ▼
  ┌──────────────┐
  │ Initialize   │
  │ Interpreter  │
  └──────┬───────┘
         │
         ▼
  ┌──────────────┐
  │ Print Prompt │◄──────────────┐
  │ "> "         │               │
  └──────┬───────┘               │
         │                       │
         ▼                       │
  ┌──────────────┐               │
  │ Read Line    │               │
  │ from User    │               │
  └──────┬───────┘               │
         │                       │
         ▼                       │
   ┌───────────┐                 │
   │ Input =   │── YES ─▶ EXIT  │
   │ 'exit'?   │                 │
   └─────┬─────┘                 │
         │ NO                    │
         ▼                       │
   ┌───────────┐                 │
   │ Append to │                 │
   │ Buffer    │                 │
   └─────┬─────┘                 │
         │                       │
         ▼                       │
   ┌───────────┐                 │
   │ Contains  │── NO ──────────┤
   │ ';' ?     │                 │
   └─────┬─────┘                 │
         │ YES                   │
         ▼                       │
  ┌──────────────┐               │
  │ Compile &    │               │
  │ Execute      │               │
  │ Buffer       │               │
  └──────┬───────┘               │
         │                       │
         ▼                       │
  ┌──────────────┐               │
  │ Clear Buffer │               │
  └──────┬───────┘               │
         │                       │
         └───────────────────────┘

EXAMPLE SESSION:
> expr A & B;
[Compiles and stores expression]
> set A = 1;
[Sets A to 1]
> set B = 1;
[Sets B to 1]
> eval;
1
[Evaluates stored expression with current variable values]
> exit
[Terminates REPL]
```

---

## 8. Module Dependency Graph

```
┌──────────────────────────────────────────────────────┐
│            MODULE DEPENDENCY GRAPH                   │
└──────────────────────────────────────────────────────┘

                 logichorizon.py (Main)
                       │
                       │ imports
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    lexer.py      parser.py     semantic.py
        │              │              │
        │              ├──────────────┤
        │              │              │
        │              ▼              ▼
        │         ast_nodes.py       │
        │                            │
        ▼                            ▼
  [Token class]              [Visitor Pattern]
        
        │                            │
        └──────────┬─────────────────┘
                   │
                   ▼
             ir_generator.py
                   │
                   │ produces
                   ▼
              [3AC Code]
                   │
                   ▼
             optimizer.py
                   │
                   │ produces
                   ▼
          [Optimized 3AC]
                   │
                   ▼
            interpreter.py


DEPENDENCY SUMMARY:
┌────────────────┬─────────────────────────────┐
│ Module         │ Dependencies                │
├────────────────┼─────────────────────────────┤
│ logichorizon.py│ All modules                 │
│ lexer.py       │ None (standalone)           │
│ ast_nodes.py   │ None (data definitions)     │
│ parser.py      │ lexer, ast_nodes            │
│ semantic.py    │ ast_nodes                   │
│ ir_generator.py│ ast_nodes                   │
│ optimizer.py   │ None (operates on strings)  │
│ interpreter.py │ None (executes 3AC strings) │
└────────────────┴─────────────────────────────┘
```

---

## 9. State Transition Diagrams

### 9.1 Interpreter State Machine

```
┌──────────────────────────────────────────────────────┐
│         INTERPRETER STATE TRANSITIONS                │
└──────────────────────────────────────────────────────┘

            ┌──────────────┐
            │  IDLE STATE  │
            │              │
            │ variables={}  │
            │ last_ir=[]   │
            └───────┬──────┘
                    │
     ┌──────────────┼──────────────┐
     │              │              │
     │ set stmt     │ expr stmt    │ table stmt
     │              │              │
     ▼              ▼              ▼
┌─────────┐   ┌──────────┐   ┌──────────┐
│ UPDATE  │   │  STORE   │   │ GENERATE │
│  VAR    │   │   IR     │   │  TABLE   │
└────┬────┘   └─────┬────┘   └────┬─────┘
     │              │              │
     │              │              │ executes
     │              │              │ stored IR
     │              │              │ multiple
     │              │              │ times
     │              │              │
     └──────────────┴──────────────┘
                    │
                    ▼
            ┌──────────────┐
            │  IDLE STATE  │
            │ (updated)    │
            └──────────────┘

EXAMPLE STATE TRANSITIONS:

Initial: IDLE → {variables: {}, last_ir: []}

After "set A = 1;":
  IDLE → UPDATE_VAR → IDLE
  {variables: {A: 1}, last_ir: []}

After "expr A & B;":
  IDLE → STORE_IR → IDLE
  {variables: {A: 1}, last_ir: ["t1 = AND A B"]}

After "table;":
  IDLE → GENERATE_TABLE → IDLE
  [Executes last_ir 4 times with different variable bindings]
  {variables: {A: 1}, last_ir: ["t1 = AND A B"]}
```

---

## 10. Memory Layout Diagrams

### 10.1 AST Memory Structure

```
┌───────────────────────────────────────────────────────┐
│     AST NODE MEMORY LAYOUT (Object Hierarchy)         │
└───────────────────────────────────────────────────────┘

Program Object @ 0x1000
├─ statements: List[Stmt] @ 0x1008
│  │
│  ├─ [0] → ExprStmt @ 0x2000
│  │        ├─ expr: BinaryOp @ 0x3000
│  │        │        ├─ left: Var @ 0x4000
│  │        │        │        └─ name: "A"
│  │        │        ├─ op: "&"
│  │        │        └─ right: Var @ 0x4100
│  │        │                 └─ name: "B"
│  │        └─ name: None
│  │
│  └─ [1] → SetStmt @ 0x2100
│           ├─ name: "A"
│           └─ value: True
│
└─ (end of list)


MEMORY REFERENCES:
0x1000: Program object
0x1008: List of statements
0x2000: ExprStmt object
0x2100: SetStmt object
0x3000: BinaryOp object
0x4000: Var object (A)
0x4100: Var object (B)
```

### 10.2 Runtime Symbol Table

```
┌───────────────────────────────────────────────────────┐
│              INTERPRETER SYMBOL TABLE                 │
└───────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                  Global Variables                   │
├────────────┬──────────┬────────────────────────────┤
│ Variable   │  Value   │  Last Modified             │
├────────────┼──────────┼────────────────────────────┤
│ A          │    1     │  Line 3 (set A = 1;)       │
│ B          │    0     │  Line 4 (set B = 0;)       │
│ result     │    0     │  Line 1 (expr result ...)  │
└────────────┴──────────┴────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│              Temporary Variables                    │
├────────────┬──────────┬────────────────────────────┤
│ Temp       │  Value   │  Instruction               │
├────────────┼──────────┼────────────────────────────┤
│ t1         │    0     │  t1 = AND A B              │
│ t2         │    0     │  t2 = OR t1 C              │
└────────────┴──────────┴────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                 Defined Rules                       │
├────────────┬───────────────────────────────────────┤
│ Rule Name  │  Expression IR                        │
├────────────┼───────────────────────────────────────┤
│ rule1      │  ["t1 = AND A B", "rule1 = t1"]       │
│ impl_test  │  ["t2 = IMPLIES C D", "impl_test=t2"] │
└────────────┴───────────────────────────────────────┘
```

---

## 11. Comparative Parsing Techniques

This section presents seven fundamental parsing techniques used in compiler construction, each illustrated with clear diagrams suitable for academic study and examination preparation.

---

### 11.1 Recursive Descent Parsing Flow

**Description:**  
Recursive descent is a top-down parsing technique where each non-terminal in the grammar has a corresponding parsing function. The parser makes predictive decisions based on lookahead tokens.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│          RECURSIVE DESCENT PARSING FLOW                     │
│          Grammar: E → T E'                                  │
│                   E' → + T E' | ε                          │
│                   T → F T'                                  │
│                   T' → * F T' | ε                          │
│                   F → ( E ) | id                           │
└─────────────────────────────────────────────────────────────┘

Input: id + id * id

                    parseE()
                       │
                       ├─ parseT()
                       │    │
                       │    ├─ parseF()
                       │    │    └─ match(id)  ✓
                       │    │
                       │    └─ parseT'()
                       │         └─ [lookahead: +] → ε
                       │
                       └─ parseE'()
                            │
                            ├─ [lookahead: +] → match(+)  ✓
                            │
                            ├─ parseT()
                            │    │
                            │    ├─ parseF()
                            │    │    └─ match(id)  ✓
                            │    │
                            │    └─ parseT'()
                            │         │
                            │         ├─ [lookahead: *] → match(*)  ✓
                            │         │
                            │         ├─ parseF()
                            │         │    └─ match(id)  ✓
                            │         │
                            │         └─ parseT'()
                            │              └─ [lookahead: $] → ε
                            │
                            └─ parseE'()
                                 └─ [lookahead: $] → ε

RESULT: Parse successful!

KEY PRINCIPLES:
1. Each non-terminal becomes a function
2. Terminals are matched with eat()/match()
3. Productions guide recursive calls
4. Lookahead determines which production to use
5. ε-productions return without consuming tokens
```

**Explanation:**  
Recursive descent parsing follows the grammar structure directly. For input "id + id * id", the parser starts with `parseE()`, which calls `parseT()` to handle the first term. The lookahead token (+) determines which production to apply for `E'`. The process continues recursively, building the parse tree implicitly through function call chains. This technique is simple and intuitive but requires an LL(1) grammar without left recursion.

---

### 11.2 LL(1) Parsing Table and Stack

**Description:**  
LL(1) parsing uses a parsing table constructed from FIRST and FOLLOW sets. The parser operates with a stack and makes deterministic decisions based on the current stack symbol and input token.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│                 LL(1) PARSING TABLE                         │
│                                                             │
│         Grammar:  S → A B                                   │
│                   A → a A | ε                              │
│                   B → b B | ε                              │
└─────────────────────────────────────────────────────────────┘

FIRST and FOLLOW Sets:
┌──────────┬───────────────┬───────────────┐
│ Symbol   │ FIRST         │ FOLLOW        │
├──────────┼───────────────┼───────────────┤
│ S        │ {a, b, ε}     │ {$}           │
│ A        │ {a, ε}        │ {b, $}        │
│ B        │ {b, ε}        │ {$}           │
└──────────┴───────────────┴───────────────┘

LL(1) PARSING TABLE:
┌──────────┬───────────────┬───────────────┬───────────────┐
│          │       a       │       b       │       $       │
├──────────┼───────────────┼───────────────┼───────────────┤
│    S     │   S → A B     │   S → A B     │   S → A B     │
│    A     │   A → a A     │   A → ε       │   A → ε       │
│    B     │               │   B → b B     │   B → ε       │
└──────────┴───────────────┴───────────────┴───────────────┘

PARSING TRACE for input: a a b $

┌──────┬───────────────────┬──────────────┬─────────────────┐
│ Step │ Stack             │ Input        │ Action          │
├──────┼───────────────────┼──────────────┼─────────────────┤
│  0   │ $ S               │ a a b $      │ S → A B         │
│  1   │ $ B A             │ a a b $      │ A → a A         │
│  2   │ $ B A a           │ a a b $      │ match(a)        │
│  3   │ $ B A             │ a b $        │ A → a A         │
│  4   │ $ B A a           │ a b $        │ match(a)        │
│  5   │ $ B A             │ b $          │ A → ε           │
│  6   │ $ B               │ b $          │ B → b B         │
│  7   │ $ B b             │ b $          │ match(b)        │
│  8   │ $ B               │ $            │ B → ε           │
│  9   │ $                 │ $            │ Accept          │
└──────┴───────────────────┴──────────────┴─────────────────┘

ALGORITHM:
1. Push start symbol and $ onto stack
2. Repeat until stack is empty:
   - If top = terminal: match with input
   - If top = non-terminal: consult table M[top, input]
   - If M[top, input] = empty: error
   - If M[top, input] = production: pop and push RHS (reverse)
3. Accept if input exhausted and stack empty
```

**Explanation:**  
LL(1) parsing is a table-driven predictive parsing method. The table is constructed using FIRST and FOLLOW sets to ensure each cell contains at most one production (the "1" in LL(1) means one token lookahead). During parsing, the stack holds grammar symbols to be matched, and the table determines which production to apply based on the current non-terminal and lookahead token. This method is efficient (O(n)) but limited to LL(1) grammars.

---

### 11.3 LR(0) Parsing Automaton

**Description:**  
LR(0) parsing builds a DFA of items (productions with a dot indicating parsing position). The automaton guides shift and reduce actions. LR(0) is the simplest LR parser but has limited power.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│              LR(0) PARSING AUTOMATON (DFA)                  │
│                                                             │
│              Grammar:  S → E                                │
│                        E → E + T | T                        │
│                        T → id                               │
│                                                             │
│              Augmented: S' → S                              │
└─────────────────────────────────────────────────────────────┘

STATE DIAGRAM:

    ┌──────────────────┐
    │      I₀          │     
    │  S' → · S        │──────S────▶ ┌──────────────────┐
    │  S  → · E        │             │      I₁          │
    │  E  → · E + T    │             │  S' → S ·        │
    │  E  → · T        │             │  [Accept]        │
    │  T  → · id       │             └──────────────────┘
    └──────────────────┘
         │      │
         │      id
         │      │
         E      ▼
         │   ┌──────────────────┐
         │   │      I₃          │
         │   │  T → id ·        │
         │   │  [Reduce T→id]   │
         │   └──────────────────┘
         │
         ▼
    ┌──────────────────┐
    │      I₂          │──────T────▶ ┌──────────────────┐
    │  S  → E ·        │             │      I₅          │
    │  E  → E · + T    │             │  E → T ·         │
    └──────────────────┘             │  [Reduce E→T]    │
         │                           └──────────────────┘
         +
         │
         ▼
    ┌──────────────────┐
    │      I₄          │──────T────▶ ┌──────────────────┐
    │  E → E + · T     │             │      I₆          │
    │  T → · id        │             │  E → E + T ·     │
    └──────────────────┘             │  [Reduce E→E+T]  │
         │                           └──────────────────┘
         id
         │
         ▼
    ┌──────────────────┐
    │      I₇          │
    │  T → id ·        │
    │  [Reduce T→id]   │
    └──────────────────┘

LR(0) PARSING TABLE:

┌───────┬────────┬────────┬─────────┬────────┬────────┬────────┐
│ State │  id    │   +    │    $    │   S    │   E    │   T    │
├───────┼────────┼────────┼─────────┼────────┼────────┼────────┤
│  I₀   │  s3    │        │         │   1    │   2    │   5    │
│  I₁   │        │        │  accept │        │        │        │
│  I₂   │        │   s4   │  r1     │        │        │        │
│  I₃   │  r3    │   r3   │   r3    │        │        │        │
│  I₄   │  s7    │        │         │        │        │   6    │
│  I₅   │  r2    │   r2   │   r2    │        │        │        │
│  I₆   │  r2    │   r2   │   r2    │        │        │        │
│  I₇   │  r3    │   r3   │   r3    │        │        │        │
└───────┴────────┴────────┴─────────┴────────┴────────┴────────┘

LEGEND:
  s#   = shift and goto state #
  r#   = reduce by production #
  accept = parsing complete
  blank = error

KEY CONCEPTS:
1. Items: Productions with · marking parse position
2. Closure: Add items for non-terminals after ·
3. Goto: Advance · over a symbol
4. Conflicts: Multiple actions in same cell (LR(0) limitation)
```

**Explanation:**  
LR(0) automaton states represent sets of items indicating parsing progress. The parser uses a stack to track states and symbols. "Shift" pushes the next input and a new state; "Reduce" pops symbols matching a production's RHS and pushes the LHS. The automaton is built using closure (adding implied items) and goto (transitioning on symbols). LR(0) often has shift/reduce or reduce/reduce conflicts, limiting its practical use without lookahead.

---

### 11.4 SLR Parsing with FOLLOW Sets

**Description:**  
SLR (Simple LR) enhances LR(0) by using FOLLOW sets to resolve some conflicts. A reduce action is only performed if the lookahead is in FOLLOW of the production's LHS.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│           SLR PARSING WITH FOLLOW SETS                      │
│                                                             │
│           Grammar:  S → E                                   │
│                     E → T + E | T                          │
│                     T → id                                  │
└─────────────────────────────────────────────────────────────┘

FOLLOW SETS:
┌──────────┬────────────────────┐
│ Symbol   │ FOLLOW             │
├──────────┼────────────────────┤
│    S     │ {$}                │
│    E     │ {$}                │
│    T     │ {+, $}             │
└──────────┴────────────────────┘

LR(0) AUTOMATON STATES:

I₀:                      I₁:                    I₂:
S' → · S                S' → S ·               S → E ·
S  → · E                [Accept on $]          [Reduce S→E on $]
E  → · T + E                                   
E  → · T                I₃:                    I₄:
T  → · id               T → id ·               E → T · + E
                        [Reduce T→id           E → T ·
                         on +, $]              [Reduce E→T on $]

I₅:                      I₆:
E → T + · E             E → T + E ·
E → · T + E             [Reduce E→T+E on $]
E → · T
T → · id

I₇:
T → id ·
[Reduce T→id on +, $]

SLR PARSING TABLE (with FOLLOW resolution):

┌───────┬────────────────┬────────────────┬─────────────────┐
│ State │      id        │       +        │       $         │
├───────┼────────────────┼────────────────┼─────────────────┤
│  I₀   │  shift 3       │                │                 │
│  I₁   │                │                │  accept         │
│  I₂   │                │                │  reduce S→E     │
│  I₃   │                │  reduce T→id   │  reduce T→id    │
│  I₄   │                │  shift 5       │  reduce E→T     │
│  I₅   │  shift 7       │                │                 │
│  I₆   │                │                │  reduce E→T+E   │
│  I₇   │                │  reduce T→id   │  reduce T→id    │
└───────┴────────────────┴────────────────┴─────────────────┘

CONFLICT RESOLUTION EXAMPLE:
┌─────────────────────────────────────────────────────────────┐
│ State I₄ has LR(0) conflict:                                │
│   - Item: T → id ·      [suggests reduce T→id]             │
│   - Item: E → T · + E   [suggests shift on +]              │
│                                                             │
│ SLR Resolution:                                             │
│   - Reduce T→id only if lookahead ∈ FOLLOW(T) = {+, $}    │
│   - On '+': Can shift OR reduce, but shift has priority    │
│   - On '$': Only reduce (no shift option)                  │
│   → Conflict resolved by preferring shift over reduce      │
└─────────────────────────────────────────────────────────────┘

PARSING TRACE for input: id + id $

┌──────┬──────────┬──────────┬─────────────────────────┐
│ Step │  Stack   │  Input   │  Action                 │
├──────┼──────────┼──────────┼─────────────────────────┤
│  1   │ 0        │ id+id$   │ shift 3                 │
│  2   │ 0 id 3   │ +id$     │ reduce T→id, goto 4     │
│  3   │ 0 T 4    │ +id$     │ shift 5                 │
│  4   │ 0 T 4 +5 │ id$      │ shift 7                 │
│  5   │ 0T4+5id7 │ $        │ reduce T→id, goto 6     │
│  6   │ 0T4+5T6  │ $        │ reduce E→T+E, goto 2    │
│  7   │ 0 E 2    │ $        │ reduce S→E, goto 1      │
│  8   │ 0 S 1    │ $        │ accept                  │
└──────┴──────────┴──────────┴─────────────────────────┘
```

**Explanation:**  
SLR improves LR(0) by consulting FOLLOW sets before reducing. In state I₄, the parser only reduces T→id if the lookahead is in FOLLOW(T) = {+, $}. This resolves many conflicts that plague LR(0) parsers. However, SLR is still not as powerful as canonical LR because it uses global FOLLOW sets rather than context-specific lookaheads, which can still result in conflicts for some grammars.

---

### 11.5 CLR Parsing with Canonical LR Items

**Description:**  
Canonical LR (CLR) is the most powerful LR parser, using LR(1) items that include explicit lookahead tokens. Each item is [A → α·β, a] where 'a' is the specific lookahead for this reduction.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│         CLR (CANONICAL LR) PARSING AUTOMATON                │
│                                                             │
│         Grammar:  S → C C                                   │
│                   C → c C | d                              │
│                                                             │
│         Augmented: S' → S                                   │
│                                                             │
│         LR(1) Items: [Production, Lookahead]               │
└─────────────────────────────────────────────────────────────┘

CLR AUTOMATON (Selected States):

╔════════════════════════════════════╗
║            I₀                      ║
╠════════════════════════════════════╣
║  [S' → · S, $]                    ║
║  [S  → · C C, $]                  ║
║  [C  → · c C, c/d]  ← lookahead   ║
║  [C  → · d, c/d]                  ║
╚════════════════════════════════════╝
      │         │         │
      S         c         d
      │         │         │
      ▼         ▼         ▼
    ┌────┐  ┌─────────┐  ┌─────────┐
    │ I₁ │  │   I₂    │  │   I₃    │
    └────┘  └─────────┘  └─────────┘

╔════════════════════════════════════╗
║            I₁                      ║
╠════════════════════════════════════╣
║  [S' → S ·, $]                    ║
║  ACCEPT                            ║
╚════════════════════════════════════╝

╔════════════════════════════════════╗
║            I₂                      ║
╠════════════════════════════════════╣
║  [C → c · C, c/d]                 ║
║  [C → · c C, c/d]                 ║
║  [C → · d, c/d]                   ║
╚════════════════════════════════════╝

╔════════════════════════════════════╗
║            I₃                      ║
╠════════════════════════════════════╣
║  [C → d ·, c/d]                   ║
║  Reduce C→d on lookahead c,d      ║
╚════════════════════════════════════╝

╔════════════════════════════════════╗
║            I₄                      ║
╠════════════════════════════════════╣
║  [S → C · C, $]                   ║
║  [C → · c C, $]  ← different LA   ║
║  [C → · d, $]                     ║
╚════════════════════════════════════╝

CLR vs SLR COMPARISON:

┌─────────────────────────────────────────────────────────────┐
│  KEY DIFFERENCE: Context-Specific vs Global Lookahead       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SLR Item:            │  CLR Item:                          │
│    C → · d            │    [C → · d, c/d]  (in I₀)        │
│                       │    [C → · d, $]    (in I₄)        │
│                       │                                     │
│  SLR uses:            │  CLR uses:                          │
│    FOLLOW(C) = {c,d,$}│    Actual lookahead in context     │
│                       │                                     │
│  Problem: Too broad   │  Solution: Precise lookahead       │
│  May cause conflicts  │  Resolves more conflicts           │
└─────────────────────────────────────────────────────────────┘

CLR PARSING TABLE (Partial):

┌───────┬─────────┬─────────┬──────────┬─────────┬─────────┐
│ State │    c    │    d    │    $     │    S    │    C    │
├───────┼─────────┼─────────┼──────────┼─────────┼─────────┤
│  I₀   │ shift 2 │ shift 3 │          │ goto 1  │ goto 4  │
│  I₁   │         │         │ accept   │         │         │
│  I₂   │ shift 2 │ shift 3 │          │         │ goto 5  │
│  I₃   │ reduce  │ reduce  │          │         │         │
│       │  C→d    │  C→d    │          │         │         │
│  I₄   │ shift 6 │ shift 7 │          │         │ goto 8  │
│  I₅   │ reduce  │ reduce  │          │         │         │
│       │  C→cC   │  C→cC   │          │         │         │
│  I₆   │ shift 6 │ shift 7 │          │         │ goto 9  │
│  I₇   │         │         │ reduce   │         │         │
│       │         │         │  C→d     │         │         │
│  I₈   │         │         │ reduce   │         │         │
│       │         │         │  S→CC    │         │         │
└───────┴─────────┴─────────┴──────────┴─────────┴─────────┘

NOTICE: State I₃ reduces on {c,d}, State I₇ reduces only on {$}
This precision eliminates conflicts!
```

**Explanation:**  
CLR parsing uses LR(1) items where each item includes a specific lookahead token. The lookahead indicates valid tokens for reduction in that particular context. This eliminates conflicts that occur in SLR by distinguishing between different contexts for the same production. The cost is a larger automaton with more states. CLR accepts all LR(1) grammars, making it the most powerful shift-reduce parser, though practical implementations often use LALR to reduce state count.

---

### 11.6 LALR Parsing with State Merging

**Description:**  
LALR (Lookahead LR) merges CLR states that have identical cores (same items except for lookaheads), creating a more compact parser table while retaining most of CLR's power.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│        LALR PARSING: STATE MERGING FROM CLR                 │
│                                                             │
│        Grammar:  S → a A d | b B d | a B e | b A e        │
│                  A → c                                      │
│                  B → c                                      │
└─────────────────────────────────────────────────────────────┘

CLR AUTOMATON (Before Merging):

╔══════════════════════╗     ╔══════════════════════╗
║   CLR State I₅       ║     ║   CLR State I₇       ║
╠══════════════════════╣     ╠══════════════════════╣
║ [A → c ·, d]         ║     ║ [B → c ·, e]         ║
╚══════════════════════╝     ╚══════════════════════╝
    Core: A → c ·               Core: B → c ·
    Lookahead: {d}              Lookahead: {e}

          │                           │
          │    LALR MERGING           │
          │    (Same Core)            │
          └──────────┬────────────────┘
                     ▼
           ╔═══════════════════════╗
           ║   LALR State I₅₇      ║
           ╠═══════════════════════╣
           ║ [A → c ·, d]          ║
           ║ [B → c ·, e]          ║
           ╚═══════════════════════╝
              Core: A/B → c ·
              Lookahead: {d, e}

MERGING ALGORITHM:

Step 1: Identify CLR states with identical cores
┌──────────┬─────────────────────────────────────┐
│ CLR I₅   │ Items: [A → c ·, d]                 │
│ CLR I₇   │ Items: [B → c ·, e]                 │
│          │                                     │
│ Core:    │ Both have "X → c ·" pattern        │
│ Merge?   │ YES - same item structure          │
└──────────┴─────────────────────────────────────┘

Step 2: Union of lookaheads
┌─────────────────────────────────────────────────┐
│ LALR I₅₇ = merge(I₅, I₇)                       │
│                                                 │
│ Lookaheads = {d} ∪ {e} = {d, e}               │
│                                                 │
│ New Items: [A → c ·, d/e]                      │
│            [B → c ·, d/e]                      │
└─────────────────────────────────────────────────┘

Step 3: Update transitions
  All transitions to I₅ or I₇ now go to I₅₇

LALR vs CLR STATE COUNT:

Grammar Example:
┌─────────────────────────────────────────────────┐
│ Production Count: 10                            │
│ CLR States: 87                                  │
│ LALR States: 42  (48% reduction)               │
│ LR(0)/SLR States: 42                           │
└─────────────────────────────────────────────────┘

POTENTIAL CONFLICTS:

Merging can introduce reduce/reduce conflicts:

Before (CLR - no conflict):
  State I₅: [A → c ·, d]  → reduce A→c on 'd'
  State I₇: [B → c ·, e]  → reduce B→c on 'e'
  Different states, different lookaheads ✓

After (LALR - possible conflict):
  State I₅₇: [A → c ·, d]  → reduce A→c on 'd'
             [B → c ·, e]  → reduce B→c on 'e'
  Same state, but lookaheads still distinct ✓
  
  BUT if lookaheads overlap:
  State Iₓ: [A → c ·, d]  → reduce A→c on 'd'
            [B → c ·, d]  → reduce B→c on 'd'
  CONFLICT! Can't decide which production ✗

LALR PARSING TABLE STRUCTURE:

┌───────┬──────────┬──────────┬──────────┬───────────┐
│ State │    a     │    b     │    c     │    d/e    │
├───────┼──────────┼──────────┼──────────┼───────────┤
│  I₀   │ shift 1  │ shift 2  │          │           │
│  I₁   │          │          │ shift 3  │           │
│  I₂   │          │          │ shift 3  │           │
│  I₃   │          │          │          │ r(A→c) /  │
│(I₅₇)  │          │          │          │ r(B→c)    │
└───────┴──────────┴──────────┴──────────┴───────────┘
        ↑                                      ↑
        Fewer states than CLR        Combined lookaheads

KEY CHARACTERISTICS:
1. Same number of states as SLR
2. More powerful than SLR (accepts more grammars)
3. Less powerful than CLR (rare conflicts possible)
4. Used by YACC/Bison parser generators
```

**Explanation:**  
LALR merges CLR states with identical cores (same items ignoring lookaheads), unioning their lookahead sets. This drastically reduces the number of states while preserving most parsing power. LALR parsers are as compact as SLR but can handle more grammars. The tradeoff is that merging can occasionally introduce reduce/reduce conflicts that wouldn't exist in CLR. In practice, LALR is the sweet spot for parser generators, combining efficiency with broad grammar support.

---

### 11.7 Operator Precedence Parsing Table

**Description:**  
Operator precedence parsing is a simple technique for expression grammars. It uses precedence and associativity relations between operators to make shift/reduce decisions without constructing a full parsing table.

**Diagram:**

```
┌─────────────────────────────────────────────────────────────┐
│         OPERATOR PRECEDENCE PARSING                         │
│                                                             │
│         Expression Grammar:                                 │
│         E → E + E | E - E | E * E | E / E | (E) | id       │
└─────────────────────────────────────────────────────────────┘

PRECEDENCE AND ASSOCIATIVITY:

┌──────────────┬────────────┬──────────────────┐
│  Operator    │ Precedence │  Associativity   │
├──────────────┼────────────┼──────────────────┤
│  + , -       │     1      │  Left            │
│  * , /       │     2      │  Left            │
│  (unary) -   │     3      │  Right           │
└──────────────┴────────────┴──────────────────┘

OPERATOR PRECEDENCE TABLE:

       Relations: ⋖ (less than), ≐ (equal), ⋗ (greater than)

┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
│     │  +  │  -  │  *  │  /  │  (  │  )  │ id  │  $  │
├─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┤
│  +  │  ⋗  │  ⋗  │  ⋖  │  ⋖  │  ⋖  │  ⋗  │  ⋖  │  ⋗  │
│  -  │  ⋗  │  ⋗  │  ⋖  │  ⋖  │  ⋖  │  ⋗  │  ⋖  │  ⋗  │
│  *  │  ⋗  │  ⋗  │  ⋗  │  ⋗  │  ⋖  │  ⋗  │  ⋖  │  ⋗  │
│  /  │  ⋗  │  ⋗  │  ⋗  │  ⋗  │  ⋖  │  ⋗  │  ⋖  │  ⋗  │
│  (  │  ⋖  │  ⋖  │  ⋖  │  ⋖  │  ⋖  │  ≐  │  ⋖  │     │
│  )  │  ⋗  │  ⋗  │  ⋗  │  ⋗  │     │  ⋗  │     │  ⋗  │
│ id  │  ⋗  │  ⋗  │  ⋗  │  ⋗  │     │  ⋗  │     │  ⋗  │
│  $  │  ⋖  │  ⋖  │  ⋖  │  ⋖  │  ⋖  │     │  ⋖  │     │
└─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘

RELATION SEMANTICS:
  a ⋖ b : Shift (a has lower precedence, b should be shifted)
  a ≐ b : Match (equal precedence, typically for parentheses)
  a ⋗ b : Reduce (a has higher precedence, reduce left)

PARSING ALGORITHM:

Input: id + id * id $
Stack: $ 

┌──────┬─────────────────┬──────────────┬────────────────────┐
│ Step │     Stack       │    Input     │  Action            │
├──────┼─────────────────┼──────────────┼────────────────────┤
│  1   │ $               │ id+id*id$    │ $ ⋖ id: shift      │
│  2   │ $ id            │ +id*id$      │ id ⋗ +: reduce E→id│
│  3   │ $ E             │ +id*id$      │ $ ⋖ +: shift       │
│  4   │ $ E +           │ id*id$       │ + ⋖ id: shift      │
│  5   │ $ E + id        │ *id$         │ id ⋗ *: reduce E→id│
│  6   │ $ E + E         │ *id$         │ + ⋖ *: shift       │
│  7   │ $ E + E *       │ id$          │ * ⋖ id: shift      │
│  8   │ $ E + E * id    │ $            │ id ⋗ $: reduce E→id│
│  9   │ $ E + E * E     │ $            │ * ⋗ $: reduce E→E*E│
│ 10   │ $ E + E         │ $            │ + ⋗ $: reduce E→E+E│
│ 11   │ $ E             │ $            │ Accept             │
└──────┴─────────────────┴──────────────┴────────────────────┘

VISUALIZATION OF PARSE:

Input: id + id * id

           E                    Final parse tree
         / | \                  (after reductions)
        E  +  E
        |    / | \
       id   E  *  E
            |     |
           id    id

Reduction order (reverse):
  1. id → E   (rightmost id)
  2. E * E → E  (multiplication)
  3. id → E   (middle id)
  4. E + E → E  (addition)
  5. id → E   (leftmost id)

KEY PRINCIPLES:

1. Shift (⋖):   When next operator has higher precedence
2. Reduce (⋗):  When stack operator has higher precedence
3. Match (≐):   For balanced delimiters (parentheses)

ADVANTAGES:
  ✓ Simple table
  ✓ Efficient for expressions
  ✓ Natural precedence handling
  ✓ No grammar needed (just operators)

LIMITATIONS:
  ✗ Only works for operator expressions
  ✗ Can't handle all context-free grammars
  ✗ Limited to simple precedence relationships
  ✗ No support for complex syntax structures
```

**Explanation:**  
Operator precedence parsing uses a compact table of precedence relations (⋖, ≐, ⋗) between terminal symbols. When the top of the stack and the next input have a relation, the parser decides to shift, reduce, or match based on that relation. This technique is ideal for arithmetic expressions where operator precedence and associativity are well-defined. It's simpler than LR parsing but limited to operator grammars. Modern compilers often use this technique for expression sub-grammars within a larger parser.

---

## 12. Summary

This document has provided comprehensive visual representations of the LogicHorizon compiler's architecture, including:

1. **System Architecture**: High-level overview of compiler organization
2. **Data Flow**: Token and AST transformation pipelines
3. **Parsing Diagrams**: Parse trees and precedence structures
4. **Finite Automata**: Token recognition state machines
5. **Optimization**: Algorithm flowcharts for code improvement
6. **Execution**: Runtime behavior and truth table generation
7. **Dependencies**: Module interaction graphs
8. **State Machines**: Interpreter state transitions
9. **Memory Layout**: AST and runtime data structures
10. **Parsing Techniques**: Seven comprehensive parser type comparisons
    - Recursive Descent Parsing (top-down, predictive)
    - LL(1) Parsing (table-driven, FIRST/FOLLOW)
    - LR(0) Automaton (shift-reduce, basic)
    - SLR Parsing (LR with FOLLOW sets)
    - CLR Parsing (canonical LR with lookahead)
    - LALR Parsing (state merging optimization)
    - Operator Precedence Parsing (expression-specific)

These diagrams complement the textual documentation by providing intuitive visual models of compiler operation, facilitating deeper understanding of the LogicHorizon implementation for students and developers studying compiler construction.

1. **System Architecture**: High-level overview of compiler organization
2. **Data Flow**: Token and AST transformation pipelines
3. **Parsing Diagrams**: Parse trees and precedence structures
4. **Finite Automata**: Token recognition state machines
5. **Optimization**: Algorithm flowcharts for code improvement
6. **Execution**: Runtime behavior and truth table generation
7. **Dependencies**: Module interaction graphs
8. **State Machines**: Interpreter state transitions
9. **Memory Layout**: AST and runtime data structures

These diagrams complement the textual documentation by providing intuitive visual models of compiler operation, facilitating deeper understanding of the LogicHorizon implementation for students and developers studying compiler construction.
