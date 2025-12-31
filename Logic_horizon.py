import sys
import os

# Add src to path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.lexer import Lexer
from src.parser import Parser
from src.semantic import SemanticAnalyzer
from src.ir_generator import IRGenerator
from src.optimizer import Optimizer
from src.interpreter import Interpreter

# ============================================================================
#                         COMPILER STAGE FUNCTIONS
# ============================================================================

def print_stage_header(stage_name):
    """Print a clean header for each compiler stage"""
    print(f"\n===== {stage_name} =====")

def lexicalAnalysis(source_code):
    """
    STAGE 1: LEXICAL ANALYSIS (SCANNER)
    Converts source code into tokens
    """
    print_stage_header("LEXICAL ANALYSIS")
    
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Display tokens (excluding EOF for cleaner output)
        for token in tokens:
            if token.type != 'EOF':
                print(f"Token: {token.type:<12} ({token.value})")
        
        print(f"Total Tokens: {len([t for t in tokens if t.type != 'EOF'])}")
        print("Status: SUCCESS")
        return tokens
    
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")
        return None

def syntaxAnalysis(tokens):
    """
    STAGE 2: SYNTAX ANALYSIS (PARSER)
    Constructs Abstract Syntax Tree (AST) from tokens
    """
    print_stage_header("SYNTAX ANALYSIS")
    
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Display parse summary
        stmt_count = len(ast.statements)
        print(f"Parsing Tokens into AST...")
        print(f"Statements Parsed: {stmt_count}")
        
        # Display statement types
        for i, stmt in enumerate(ast.statements, 1):
            stmt_type = stmt.__class__.__name__.replace('Stmt', '')
            print(f"  Statement {i}: {stmt_type}")
        
        print("Status: SUCCESS - Syntax is valid")
        return ast
    
    except Exception as e:
        print(f"Status: FAILED - Syntax Error")
        print(f"Error: {e}")
        return None

def semanticAnalysis(ast):
    """
    STAGE 3: SEMANTIC ANALYSIS
    Validates semantic correctness of the program
    """
    print_stage_header("SEMANTIC ANALYSIS")
    
    try:
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        
        # Display semantic analysis results
        print(f"Checking Semantic Rules...")
        
        if analyzer.declared_vars:
            print(f"Variables Declared: {', '.join(sorted(analyzer.declared_vars))}")
        
        if analyzer.defined_rules:
            print(f"Rules Defined: {', '.join(sorted(analyzer.defined_rules))}")
        
        print("Status: SUCCESS - No semantic errors")
        return True
    
    except Exception as e:
        print(f"Status: FAILED - Semantic Error")
        print(f"Error: {e}")
        return False

def generateIntermediateCode(ast):
    """
    STAGE 4: INTERMEDIATE CODE GENERATION
    Generates Three-Address Code (3AC) from AST
    """
    print_stage_header("INTERMEDIATE CODE GENERATION")
    
    try:
        ir_generator = IRGenerator()
        all_code = []
        
        for stmt in ast.statements:
            code = ir_generator.generate(stmt)
            all_code.extend(code)
        
        # Display generated code - print once, not in loop
        if all_code:
            for instruction in all_code:
                print(f"{instruction}")
        else:
            print("(No intermediate code generated)")
        
        print(f"Total Instructions: {len(all_code)}")
        print("Status: SUCCESS")
        return all_code
    
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")
        return None

def optimizeCode(intermediate_code):
    """
    STAGE 5: CODE OPTIMIZATION (OPTIONAL)
    Applies peephole optimizations to intermediate code
    """
    print_stage_header("CODE OPTIMIZATION")
    
    try:
        optimizer = Optimizer()
        optimized = optimizer.optimize(intermediate_code)
        
        # Check if any optimizations were applied
        changes = sum(1 for orig, opt in zip(intermediate_code, optimized) if orig != opt)
        
        print(f"Applying Peephole Optimizations...")
        print(f"Optimizations Applied: {changes}")
        
        if changes > 0:
            # Show optimized code
            print("Optimized Code:")
            for instruction in optimized:
                print(f"  {instruction}")
        else:
            print("No optimizations needed")
        
        print("Status: SUCCESS")
        return optimized
    
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")
        return intermediate_code

def generateTargetCode(optimized_code, interpreter):
    """
    STAGE 6: TARGET CODE GENERATION / EXECUTION
    Executes the optimized intermediate code and generates output
    """
    print_stage_header("TARGET CODE / OUTPUT")
    
    try:
        # Execute the code - the interpreter will print the actual output
        interpreter.execute(optimized_code)
        print("Status: SUCCESS")
        return True
    
    except Exception as e:
        print(f"Status: FAILED")
        print(f"Error: {e}")
        return False

# ============================================================================
#                         MAIN COMPILATION FUNCTION
# ============================================================================

def compileAndRun(source_code, interpreter, verbose=True):
    """
    Main compilation pipeline - orchestrates all compiler stages
    Each stage executes in strict order and prints output exactly once
    """
    if verbose:
        print("\n" + "=" * 65)
        print("  LOGICHORIZON COMPILER - COMPILATION PIPELINE")
        print("=" * 65)
    
    # STAGE 1: Lexical Analysis (runs first)
    tokens = lexicalAnalysis(source_code)
    if not tokens:
        return False
    
    # STAGE 2: Syntax Analysis (runs only if lexical analysis succeeds)
    ast = syntaxAnalysis(tokens)
    if not ast:
        return False
    
    # STAGE 3: Semantic Analysis (runs only if syntax is valid)
    if not semanticAnalysis(ast):
        return False
    
    # STAGE 4: Intermediate Code Generation (runs after semantic checks)
    intermediate_code = generateIntermediateCode(ast)
    if not intermediate_code:
        return False
    
    # STAGE 5: Code Optimization (optional - runs before target code gen)
    optimized_code = optimizeCode(intermediate_code)
    if not optimized_code:
        return False
    
    # STAGE 6: Target Code Generation (runs last)
    success = generateTargetCode(optimized_code, interpreter)
    
    if verbose and success:
        print("\n" + "=" * 65)
        print("  COMPILATION COMPLETED SUCCESSFULLY")
        print("=" * 65 + "\n")
    
    return success

def process_input(text, interpreter):
    """Legacy wrapper for backward compatibility"""
    try:
        return compileAndRun(text, interpreter, verbose=True)
    except Exception as e:
        print(f"\n  ✗ Compilation Failed")
        print(f"  Error: {e}\n")

# ============================================================================
#                         REPL AND MAIN FUNCTIONS
# ============================================================================

def repl():
    """Interactive Read-Eval-Print Loop"""
    print("\n" + "=" * 65)
    print("  LogicHorizon Compiler v1.0 - REPL Mode")
    print("=" * 65)
    print("\n  Commands:")
    print("    Type your LogicHorizon code and end with ';'")
    print("    Type 'exit' to quit")
    print("    Type 'verbose' to toggle verbose mode")
    print()
    
    interpreter = Interpreter()
    buffer = ""
    verbose = False  # REPL mode is less verbose by default
    
    while True:
        try:
            if buffer:
                prompt = "... "
            else:
                prompt = ">>> "
                
            line = input(prompt)
            
            if line.strip() == 'exit':
                print("\nExiting LogicHorizon Compiler. Goodbye!\n")
                break
            
            if line.strip() == 'verbose':
                verbose = not verbose
                print(f"  Verbose mode: {'ON' if verbose else 'OFF'}\n")
                continue
            
            buffer += line + "\n"
            
            if ';' in line:
                # Process complete statements
                if verbose:
                    compileAndRun(buffer, interpreter, verbose=True)
                else:
                    # Quick mode - just show execution results
                    try:
                        lexer = Lexer(buffer)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        ast = parser.parse()
                        semantic = SemanticAnalyzer()
                        semantic.visit(ast)
                        ir_gen = IRGenerator()
                        optimizer = Optimizer()
                        
                        for stmt in ast.statements:
                            code = ir_gen.generate(stmt)
                            opt_code = optimizer.optimize(code)
                            interpreter.execute(opt_code)
                    except Exception as e:
                        print(f"  Error: {e}")
                
                buffer = ""
                print()  # Add spacing
                
        except KeyboardInterrupt:
            print("\n\nExiting LogicHorizon Compiler. Goodbye!\n")
            break
        except EOFError:
            print("\n")
            break

def main():
    """Main entry point for the compiler"""
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        
        # Check for verbose flag
        verbose = '--verbose' in sys.argv or '-v' in sys.argv
        
        if os.path.exists(filename):
            print(f"\nCompiling file: {filename}\n")
            
            with open(filename, 'r') as f:
                source_code = f.read()
            
            if not source_code.strip():
                print("  Error: Empty source file\n")
                return
            
            # Display source code
            print("=" * 65)
            print("  SOURCE CODE")
            print("=" * 65)
            for i, line in enumerate(source_code.strip().split('\n'), 1):
                print(f"  {i:2d} | {line}")
            
            # Compile and execute
            interpreter = Interpreter()
            compileAndRun(source_code, interpreter, verbose=True)
        else:
            print(f"  ✗ Error: File not found: {filename}\n")
            print("  Usage: python Logic_horizon.py <filename.logic> [--verbose]\n")
    else:
        # Interactive REPL mode
        repl()

if __name__ == "__main__":
    main()
