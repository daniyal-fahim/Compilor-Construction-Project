# Reflection: LogicHorizon Compiler Project

## What was learned

### 1. Compiler Pipeline
Building LogicHorizon reinforced the understanding of the standard compiler pipeline:
- **Lexical Analysis**: Converting raw text into a stream of tokens.
- **Syntax Analysis**: Using a recursive descent parser to build an Abstract Syntax Tree (AST) from tokens.
- **Semantic Analysis**: Validating the AST for correctness (e.g., checking for undefined rules).
- **Intermediate Representation (IR)**: Transforming the AST into a linear sequence of instructions (3-Address Code), which simplifies optimization and execution.
- **Optimization**: Applying simple rules (constant folding, identity laws) to improve the IR.
- **Code Generation/Interpretation**: Executing the IR to produce the final result (truth tables).

### 2. Recursive Descent Parsing
Implementing the parser manually showed the power and simplicity of recursive descent for LL(1) grammars. Handling operator precedence (OR < AND < NOT) was achieved through a hierarchy of methods (`parse_expression`, `parse_term`, `parse_factor`).

### 3. Intermediate Representation
Designing the 3AC format was crucial. It decoupled the front-end (parsing) from the back-end (execution). This allowed for an optimizer to be inserted easily. The 3AC format `result = op arg1 arg2` is simple yet powerful enough for this domain.

### 4. Truth Table Generation
The `table` command required a shift from single-pass execution to multi-pass execution. Identifying all variables, generating their permutations, and re-executing the IR for each permutation was an interesting challenge in the interpreter design.

### 5. Python for Compilers
Python proved to be an excellent language for prototyping a compiler due to its string handling capabilities and ease of defining data structures (AST nodes). However, for a production compiler, a statically typed language might offer better performance and safety.

## Conclusion
This project successfully demonstrated the creation of a domain-specific language from scratch, covering all major phases of compilation. The resulting `LogicHorizon` compiler is a functional tool for boolean logic analysis.
