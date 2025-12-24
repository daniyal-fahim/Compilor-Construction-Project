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

def process_input(text, interpreter):
    try:
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        program = parser.parse()
        
        semantic = SemanticAnalyzer()
        semantic.visit(program)
        
        ir_gen = IRGenerator()
        optimizer = Optimizer()
        
        for stmt in program.statements:
            code = ir_gen.generate(stmt)
            opt_code = optimizer.optimize(code)
            interpreter.execute(opt_code)
        
    except Exception as e:
        print(f"Error: {e}")

def repl():
    print("LogicEval Compiler v1.0 (REPL Mode)")
    print("Type 'help;' for commands.")
    
    interpreter = Interpreter()
    buffer = ""
    
    while True:
        try:
            if buffer:
                prompt = "... "
            else:
                prompt = "> "
                
            line = input(prompt)
            
            if line.strip() == 'exit':
                break
            
            buffer += line + "\n"
            
            if ';' in line:
                # Process complete statements
                process_input(buffer, interpreter)
                buffer = ""
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

def main():
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                text = f.read()
            interpreter = Interpreter()
            process_input(text, interpreter)
        else:
            print(f"File not found: {filename}")
    else:
        repl()

if __name__ == "__main__":
    main()
