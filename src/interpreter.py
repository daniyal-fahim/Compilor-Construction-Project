import itertools
from typing import List, Dict, Set

class Interpreter:
    def __init__(self):
        self.variables: Dict[str, int] = {} # Stores current values of variables
        self.rules: Dict[str, str] = {} # Stores rule results (simplified)
        self.last_ir: List[str] = [] # Cache for the last executed IR
        self.saved_code: Dict[str, List[str]] = {} # Cache for named expressions/rules

    def execute(self, code: List[str]):
        # Update last_ir if this code contains logic (assignments to temps or ops)
        # We want to avoid 'set A = 1' overwriting the expression logic.
        is_expr = False
        output_vars = []
        
        for line in code:
            parts = line.split()
            if not parts: continue
            
            if any(op in parts for op in ['AND', 'OR', 'NOT', 'IMPLIES', 'XOR']):
                is_expr = True
            if parts[0].startswith('t'):
                is_expr = True
            
            # Check for named assignment
            if len(parts) >= 3 and parts[1] == '=' and not parts[0].startswith('t'):
                # Only treat as expression if RHS is not a simple literal (0 or 1)
                # This prevents 'set C=1' from overwriting the last interesting expression
                if parts[2] not in ['0', '1']:
                    output_vars.append(parts[0])
                    is_expr = True # Named assignment is also an expression/rule

        if is_expr:
            self.last_ir = code
            for var in output_vars:
                self.saved_code[var] = code

        # First pass: Check for TABLE/EVAL command to handle it specially
        # INFER needs to run after execution to get values
        for line in code:
            if line.startswith("TABLE"):
                self.handle_table(code, line)
                return
            if line.startswith("EVAL"):
                self.handle_eval()
                return

        # Normal execution (just running statements)
        self.run_code(code)

        # Handle INFER after execution
        for line in code:
            if line.startswith("INFER"):
                self.handle_infer(line)
                return

    def handle_eval(self):
        if self.last_ir:
            res = self.run_code(self.last_ir)
            print(res)
        else:
            print("No expression to evaluate.")

    def run_code(self, code: List[str], local_vars: Dict[str, int] = None) -> int:
        # local_vars is used for truth table generation to override global vars
        context = self.variables.copy()
        if local_vars:
            context.update(local_vars)
        
        temps: Dict[str, int] = {}
        last_result = 0

        for line in code:
            parts = line.split()
            if not parts: continue

            if parts[0] == 'TABLE' or parts[0] == 'EVAL' or parts[0] == 'INFER':
                continue

            if len(parts) >= 3 and parts[1] == '=':
                target = parts[0]
                op = parts[2]
                
                val = 0
                if op == 'AND':
                    arg1 = self.get_val(parts[3], context, temps)
                    arg2 = self.get_val(parts[4], context, temps)
                    val = 1 if (arg1 == 1 and arg2 == 1) else 0
                elif op == 'OR':
                    arg1 = self.get_val(parts[3], context, temps)
                    arg2 = self.get_val(parts[4], context, temps)
                    val = 1 if (arg1 == 1 or arg2 == 1) else 0
                elif op == 'IMPLIES':
                    arg1 = self.get_val(parts[3], context, temps)
                    arg2 = self.get_val(parts[4], context, temps)
                    val = 1 if (arg1 == 0 or arg2 == 1) else 0
                elif op == 'XOR':
                    arg1 = self.get_val(parts[3], context, temps)
                    arg2 = self.get_val(parts[4], context, temps)
                    val = 1 if (arg1 != arg2) else 0
                elif op == 'NOT':
                    arg1 = self.get_val(parts[3], context, temps)
                    val = 1 if arg1 == 0 else 0
                else:
                    # Assignment: target = val (or target = var)
                    # parts[2] is the value/var
                    val = self.get_val(parts[2], context, temps)

                if target.startswith('t'):
                    temps[target] = val
                else:
                    # It's a variable or rule name
                    self.variables[target] = val
                    context[target] = val # Update context as well
                
                last_result = val

        return last_result

    def get_val(self, operand: str, context: Dict[str, int], temps: Dict[str, int]) -> int:
        if operand == '0': return 0
        if operand == '1': return 1
        if operand in temps: return temps[operand]
        if operand in context: return context[operand]
        # Default to 0 if undefined (or raise error?)
        # For truth table, we expect all vars to be defined in the loop.
        return 0

    def handle_table(self, code: List[str], table_cmd: str):
        # Determine which code to use
        target_code = code
        target_id = None
        
        parts = table_cmd.split()
        if len(parts) > 1:
            target_id = parts[1].strip(';')
            if target_id == "LAST_EXPR":
                target_id = None
        
        if target_id:
            if target_id in self.saved_code:
                target_code = self.saved_code[target_id]
            else:
                print(f"Error: Unknown rule or expression '{target_id}'")
                return
        elif not any('=' in line for line in code) and self.last_ir:
            target_code = self.last_ir

        # Extract variables used in the code
        vars_found = set()
        for line in target_code:
            parts = line.split()
            for part in parts:
                if part.isalpha() and part not in ['AND', 'OR', 'NOT', 'IMPLIES', 'XOR', 'TABLE', 'EVAL', 'INFER'] and not part.startswith('t'):
                    vars_found.add(part)
        
        # Remove target of assignment if it's a rule name or temp
        # Actually, we want input variables.
        # Simple heuristic: Any ID that appears as an operand.
        input_vars = set()
        for line in target_code:
            parts = line.split()
            if len(parts) > 2 and parts[1] == '=':
                # RHS operands
                for i in range(2, len(parts)):
                    op = parts[i]
                    if op.isalpha() and op not in ['AND', 'OR', 'NOT', 'IMPLIES', 'XOR'] and not op.startswith('t'):
                         input_vars.add(op)
        
        # If we are using last_ir, we still need to run the code to get the result for the table
        # But handle_table calls run_code internally.
        # We need to make sure run_code runs target_code.
        
        sorted_vars = sorted(list(input_vars))
        if not sorted_vars:
            print("No variables to generate table for.")
            return

        # Print Header
        header = " | ".join(sorted_vars) + " | Result"
        print(header)
        print("-" * len(header))

        # Generate Truth Table
        for values in itertools.product([0, 1], repeat=len(sorted_vars)):
            local_vars = dict(zip(sorted_vars, values))
            result = self.run_code(target_code, local_vars)
            row = " | ".join(str(v) for v in values) + f" | {result}"
            print(row)

    def handle_infer(self, line: str):
        # INFER rule1 rule2 ...
        parts = line.split()
        rules = parts[1:]
        print(f"Inferring from rules: {', '.join(rules)}")
        # For now, just print their current values
        for r in rules:
            val = self.variables.get(r, "Undefined")
            print(f"{r}: {val}")

