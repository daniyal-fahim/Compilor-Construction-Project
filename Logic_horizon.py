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
    print("\n" + "=" * 60)
    print(f"  {stage_name}")
    print("=" * 60)

def lexicalAnalysis(source_code):
    """
    STAGE 1: LEXICAL ANALYSIS (SCANNER)
    Converts source code into tokens
    """
    print_stage_header("STAGE 1: LEXICAL ANALYSIS")
    
    try:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        # Display tokens (excluding EOF for cleaner output)
        token_count = 0
        for token in tokens:
            if token.type != 'EOF':
                print(f"  Token: {token.type:<12} Value: {token.value:<10} Pos: {token.line}:{token.column}")
                token_count += 1
        
        print(f"\n  Total Tokens Generated: {token_count}")
        print("  Status: ✓ Lexical Analysis Successful")
        return tokens
    
    except Exception as e:
        print(f"  Status: ✗ Lexical Error")
        print(f"  Error: {e}")
        return None

def syntaxAnalysis(tokens):
    """
    STAGE 2: SYNTAX ANALYSIS (PARSER)
    Constructs Abstract Syntax Tree (AST) from tokens
    """
    print_stage_header("STAGE 2: SYNTAX ANALYSIS")
    
    try:
        parser = Parser(tokens)
        ast = parser.parse()
        
        # Display parse summary
        stmt_count = len(ast.statements)
        print(f"  Parsing Input Tokens...")
        print(f"  Abstract Syntax Tree Created")
        print(f"  Total Statements: {stmt_count}")
        
        # Display statement types
        for i, stmt in enumerate(ast.statements, 1):
            stmt_type = stmt.__class__.__name__
            print(f"    Statement {i}: {stmt_type}")
        
        print("  Status: ✓ Syntax Analysis Successful")
        return ast
    
    except Exception as e:
        print(f"  Status: ✗ Syntax Error")
        print(f"  Error: {e}")
        return None

def semanticAnalysis(ast):
    """
    STAGE 3: SEMANTIC ANALYSIS
    Validates semantic correctness of the program
    """
    print_stage_header("STAGE 3: SEMANTIC ANALYSIS")
    
    try:
        analyzer = SemanticAnalyzer()
        analyzer.visit(ast)
        
        # Display semantic analysis results
        print(f"  Checking Semantic Rules...")
        print(f"  Variables Declared: {len(analyzer.declared_vars)}")
        if analyzer.declared_vars:
            print(f"    {', '.join(sorted(analyzer.declared_vars))}")
        
        print(f"  Rules Defined: {len(analyzer.defined_rules)}")
        if analyzer.defined_rules:
            print(f"    {', '.join(sorted(analyzer.defined_rules))}")
        
        print("  Status: ✓ Semantic Analysis Successful")
        return True
    
    except Exception as e:
        print(f"  Status: ✗ Semantic Error")
        print(f"  Error: {e}")
        return False

def generateIntermediateCode(ast):
    """
    STAGE 4: INTERMEDIATE CODE GENERATION
    Generates Three-Address Code (3AC) from AST
    """
    print_stage_header("STAGE 4: INTERMEDIATE CODE GENERATION")
    
    try:
        ir_generator = IRGenerator()
        all_code = []
        
        print("  Generating Three-Address Code (3AC)...")
        
        for stmt in ast.statements:
            code = ir_generator.generate(stmt)
            all_code.extend(code)
        
        # Display generated code
        if all_code:
            print(f"\n  Generated 3AC Instructions: {len(all_code)}")
            for i, instruction in enumerate(all_code, 1):
                print(f"    {i:2d}. {instruction}")
        else:
            print("  No intermediate code generated")
        
        print("\n  Status: ✓ Intermediate Code Generation Successful")
        return all_code
    
    except Exception as e:
        print(f"  Status: ✗ IR Generation Error")
        print(f"  Error: {e}")
        return None

def optimizeCode(intermediate_code):
    """
    STAGE 5: CODE OPTIMIZATION (OPTIONAL)
    Applies peephole optimizations to intermediate code
    """
    print_stage_header("STAGE 5: CODE OPTIMIZATION")
    
    try:
        optimizer = Optimizer()
        optimized = optimizer.optimize(intermediate_code)
        
        # Check if any optimizations were applied
        changes = sum(1 for i, (orig, opt) in enumerate(zip(intermediate_code, optimized)) if orig != opt)
        
        print(f"  Applying Peephole Optimizations...")
        print(f"  Original Instructions: {len(intermediate_code)}")
        print(f"  Optimized Instructions: {len(optimized)}")
        print(f"  Optimizations Applied: {changes}")
        
        if changes > 0:
            print("\n  Optimization Examples:")
            count = 0
            for orig, opt in zip(intermediate_code, optimized):
                if orig != opt and count < 3:  # Show max 3 examples
                    print(f"    Before: {orig}")
                    print(f"    After:  {opt}")
                    count += 1
        
        print("\n  Status: ✓ Code Optimization Successful")
        return optimized
    
    except Exception as e:
        print(f"  Status: ✗ Optimization Error")
        print(f"  Error: {e}")
        return intermediate_code

def executeCode(optimized_code, interpreter):
    """
    STAGE 6: CODE EXECUTION
    Executes the optimized intermediate code
    """
    print_stage_header("STAGE 6: CODE EXECUTION / OUTPUT")
    
    try:
        print("  Executing Optimized Code...")
        print()
        interpreter.execute(optimized_code)
        print("\n  Status: ✓ Execution Completed")
        return True
    
    except Exception as e:
        print(f"  Status: ✗ Execution Error")
        print(f"  Error: {e}")
        return False

# ============================================================================
#                         MAIN COMPILATION FUNCTION
# ============================================================================

def compileAndRun(source_code, interpreter, verbose=True):
    """
    Main compilation pipeline - orchestrates all compiler stages
    """
    if verbose:
        print("\n" + "╔" + "=" * 58 + "╗")
        print("║" + " " * 10 + "LOGICHORIZON COMPILER - COMPILATION PIPELINE" + " " * 3 + "║")
        print("╚" + "=" * 58 + "╝")
    
    # STAGE 1: Lexical Analysis
    tokens = lexicalAnalysis(source_code)
    if not tokens:
        return False
    
    # STAGE 2: Syntax Analysis
    ast = syntaxAnalysis(tokens)
    if not ast:
        return False
    
    # STAGE 3: Semantic Analysis
    if not semanticAnalysis(ast):
        return False
    
    # STAGE 4: Intermediate Code Generation
    intermediate_code = generateIntermediateCode(ast)
    if not intermediate_code:
        return False
    
    # STAGE 5: Code Optimization
    optimized_code = optimizeCode(intermediate_code)
    if not optimized_code:
        return False
    
    # STAGE 6: Code Execution
    success = executeCode(optimized_code, interpreter)
    
    if verbose and success:
        print("\n" + "=" * 60)
        print("  COMPILATION AND EXECUTION COMPLETED SUCCESSFULLY")
        print("=" * 60 + "\n")
    
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
    print("\n" + "╔" + "=" * 58 + "╗")
    print("║" + " " * 8 + "LogicHorizon Compiler v1.0 - REPL Mode" + " " * 9 + "║")
    print("╚" + "=" * 58 + "╝")
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
            print("╔" + "=" * 58 + "╗")
            print("║" + " " * 20 + "SOURCE CODE" + " " * 27 + "║")
            print("╚" + "=" * 58 + "╝")
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
