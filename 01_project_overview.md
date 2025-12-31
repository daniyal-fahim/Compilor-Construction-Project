# Project Overview: LogicHorizon Compiler

## 1. Purpose of the Compiler

The **LogicHorizon** compiler is a domain-specific language (DSL) processor designed for evaluating boolean logic expressions and generating truth tables. This pedagogical compiler serves as a comprehensive demonstration of fundamental compiler construction principles and techniques. The system accepts boolean expressions with variables, evaluates them under specified or all possible variable assignments, and outputs truth tables or computed results. The compiler provides both batch processing capabilities for source files and an interactive Read-Eval-Print Loop (REPL) for dynamic expression evaluation.

## 2. Programming Language and Tools

The LogicHorizon compiler is implemented in **Python 3**, leveraging Python's object-oriented features, dataclasses for abstract syntax tree (AST) node representation, and standard libraries for pattern matching and iteration. The implementation emphasizes clarity and educational value, making the compiler architecture transparent and accessible for academic study.

### Key Python Features Utilized:
- **Dataclasses**: AST node definitions with type annotations
- **Regular Expressions**: Token pattern matching in lexical analysis
- **Object-Oriented Programming**: Visitor pattern for tree traversal
- **Type Hints**: Enhanced code readability and maintainability

## 3. High-Level Architecture

The LogicHorizon compiler follows the classical multi-phase compiler architecture, implementing all six fundamental phases of compilation:

### 3.1 Frontend Phases

**Phase 1: Lexical Analysis**
- Transforms raw source text into a token stream
- Identifies keywords, operators, identifiers, and literals
- Tracks line and column numbers for error reporting

**Phase 2: Syntax Analysis**
- Implements a recursive descent parser based on LL(1) grammar
- Constructs an Abstract Syntax Tree (AST) representing program structure
- Validates syntactic correctness according to language grammar

**Phase 3: Semantic Analysis**
- Performs context-sensitive validation on the AST
- Detects duplicate rule definitions
- Verifies rule references in inference statements
- Manages symbol tables for variables and rules

### 3.2 Backend Phases

**Phase 4: Intermediate Code Generation**
- Translates AST into Three-Address Code (3AC) representation
- Produces linearized, machine-independent intermediate representation
- Facilitates subsequent optimization and execution

**Phase 5: Code Optimization**
- Applies peephole optimizations on 3AC
- Performs constant folding (e.g., `1 & 0` → `0`)
- Implements identity law simplifications (e.g., `A & 1` → `A`)
- Reduces XOR operations with constant operands

**Phase 6: Execution/Interpretation**
- Directly interprets optimized 3AC instructions
- Maintains runtime environment for variable bindings
- Generates truth tables through exhaustive variable assignment iteration
- Implements evaluation and inference commands

## 4. Execution Flow: Source Code to Output

The compilation and execution pipeline follows this systematic sequence:

### 4.1 Input Processing
```
Source Code (.logic file or REPL input)
    ↓
[Lexical Analysis]
    ↓
Token Stream
```

### 4.2 Analysis and Translation
```
Token Stream
    ↓
[Syntax Analysis]
    ↓
Abstract Syntax Tree (AST)
    ↓
[Semantic Analysis]
    ↓
Validated AST
    ↓
[IR Generation]
    ↓
Three-Address Code (3AC)
    ↓
[Optimization]
    ↓
Optimized 3AC
```

### 4.3 Execution
```
Optimized 3AC
    ↓
[Interpreter]
    ↓
Output (Truth Tables, Expression Values, Inference Results)
```

### 4.4 Detailed Execution Flow

1. **Lexical Analysis**: The `Lexer` class scans the input character by character, producing tokens such as `KW_EXPR`, `ID`, `AND`, `BOOL`, etc. Each token includes positional metadata (line, column) for diagnostics.

2. **Syntax Analysis**: The `Parser` class consumes the token stream using recursive descent parsing. It constructs an AST composed of statement nodes (`ExprStmt`, `SetStmt`, `TableStmt`, etc.) and expression nodes (`BinaryOp`, `UnaryOp`, `Var`, `Literal`).

3. **Semantic Analysis**: The `SemanticAnalyzer` traverses the AST using the visitor pattern. It maintains sets of declared variables and defined rules, checking for semantic errors such as duplicate rule definitions or references to undefined rules in inference statements.

4. **IR Generation**: The `IRGenerator` walks the AST and produces 3AC instructions. Each complex expression is decomposed into a sequence of simple operations with temporary variables (e.g., `t1 = AND A B`, `t2 = OR t1 C`).

5. **Optimization**: The `Optimizer` performs peephole optimizations on the 3AC. It applies algebraic simplifications based on boolean algebra laws, reducing code complexity and improving execution efficiency.

6. **Interpretation**: The `Interpreter` executes the optimized 3AC. It maintains a symbol table for variable values and implements:
   - **Direct evaluation**: Computing expression results with current variable values
   - **Truth table generation**: Iterating through all possible boolean assignments for input variables
   - **Rule inference**: Displaying values of specified rules

## 5. Module Interaction and Dependencies

The LogicHorizon compiler is organized as a modular system with clear separation of concerns:

### 5.1 Core Module Hierarchy

```
logichorizon.py (Main Entry Point)
    |
    ├── src/lexer.py (Lexical Analysis)
    |       └── Produces: Token stream
    |
    ├── src/parser.py (Syntax Analysis)
    |       └── Depends on: lexer.py, ast_nodes.py
    |       └── Produces: AST
    |
    ├── src/ast_nodes.py (AST Definitions)
    |       └── Defines: Data structures for AST representation
    |
    ├── src/semantic.py (Semantic Analysis)
    |       └── Depends on: ast_nodes.py
    |       └── Validates: AST correctness
    |
    ├── src/ir_generator.py (Intermediate Code Generation)
    |       └── Depends on: ast_nodes.py
    |       └── Produces: 3AC instructions
    |
    ├── src/optimizer.py (Code Optimization)
    |       └── Transforms: 3AC → Optimized 3AC
    |
    └── src/interpreter.py (Execution Engine)
            └── Executes: Optimized 3AC
            └── Produces: Program output
```

### 5.2 Module Interactions

**logichorizon.py (Main Driver)**
- Orchestrates the compilation pipeline
- Implements REPL functionality
- Coordinates module invocation in proper sequence
- Handles file I/O and command-line argument parsing

**ast_nodes.py (Data Definitions)**
- Provides dataclass definitions for all AST node types
- Defines hierarchical structure: `Program` → `Stmt` → `Expr`
- Serves as a shared contract between parser, semantic analyzer, and IR generator

**lexer.py → parser.py**
- Lexer produces `Token` objects consumed by the parser
- Parser calls lexer methods to obtain token stream before parsing

**parser.py → semantic.py → ir_generator.py**
- Sequential processing pipeline through visitor pattern
- Each phase accepts the AST from the previous phase
- Parser builds AST, semantic analyzer validates it, IR generator translates it

**ir_generator.py → optimizer.py → interpreter.py**
- IR generator produces 3AC as list of strings
- Optimizer transforms 3AC in-place
- Interpreter executes final 3AC instructions

### 5.3 Data Flow Summary

```
User Input (Source Code)
    ↓
Lexer (Token Generation)
    ↓
Parser (AST Construction) ←→ AST Node Definitions
    ↓
Semantic Analyzer (Validation)
    ↓
IR Generator (3AC Translation)
    ↓
Optimizer (3AC Transformation)
    ↓
Interpreter (Execution)
    ↓
Output (Results, Truth Tables)
```

### 5.4 Design Patterns Employed

- **Visitor Pattern**: Used in semantic analysis and IR generation for AST traversal
- **Interpreter Pattern**: Direct execution of 3AC without code generation
- **Factory Pattern**: AST node creation in parser
- **Strategy Pattern**: Different execution strategies (evaluation, truth table, inference)

## 6. Compilation vs. Interpretation

While structured as a compiler with distinct compilation phases, LogicHorizon ultimately functions as an **interpreted system**. The final phase executes 3AC instructions directly rather than generating native machine code or bytecode. This hybrid architecture—compilation frontend with interpretation backend—is pedagogically valuable for demonstrating compiler construction principles while maintaining implementation simplicity.

## 7. Summary

The LogicHorizon compiler exemplifies classical compiler architecture, implementing all fundamental phases from lexical analysis through execution. Its modular design, clear separation of concerns, and straightforward implementation make it an effective educational tool for understanding compiler construction. The system successfully processes boolean logic expressions through a complete compilation pipeline, demonstrating practical applications of parsing theory, semantic analysis, intermediate representations, optimization techniques, and runtime interpretation.
