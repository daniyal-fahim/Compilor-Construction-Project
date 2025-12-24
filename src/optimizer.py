from typing import List

class Optimizer:
    def __init__(self):
        pass

    def optimize(self, code: List[str]) -> List[str]:
        optimized_code = []
        for line in code:
            parts = line.split()
            if len(parts) >= 5 and parts[1] == '=':
                # Format: res = OP arg1 arg2
                res = parts[0]
                op = parts[2]
                arg1 = parts[3]
                
                if op == 'NOT':
                    # Constant folding: NOT 0 -> 1, NOT 1 -> 0
                    if arg1 == '0':
                        optimized_code.append(f"{res} = 1")
                        continue
                    elif arg1 == '1':
                        optimized_code.append(f"{res} = 0")
                        continue
                
                if len(parts) == 5:
                    arg2 = parts[4]
                    # Constant folding for binary ops
                    if op == 'AND':
                        if arg1 == '0' or arg2 == '0':
                            optimized_code.append(f"{res} = 0")
                            continue
                        if arg1 == '1' and arg2 == '1':
                            optimized_code.append(f"{res} = 1")
                            continue
                        # Identity: 1 & X -> X
                        if arg1 == '1':
                            optimized_code.append(f"{res} = {arg2}")
                            continue
                        if arg2 == '1':
                            optimized_code.append(f"{res} = {arg1}")
                            continue
                            
                    elif op == 'OR':
                        if arg1 == '1' or arg2 == '1':
                            optimized_code.append(f"{res} = 1")
                            continue
                        if arg1 == '0' and arg2 == '0':
                            optimized_code.append(f"{res} = 0")
                            continue
                        # Identity: 0 | X -> X
                        if arg1 == '0':
                            optimized_code.append(f"{res} = {arg2}")
                            continue
                        if arg2 == '0':
                            optimized_code.append(f"{res} = {arg1}")
                            continue
                    
                    elif op == 'XOR':
                        # Constant folding: 0 ^ 0 -> 0, 1 ^ 1 -> 0, 1 ^ 0 -> 1, 0 ^ 1 -> 1
                        if arg1 == '0' and arg2 == '0':
                            optimized_code.append(f"{res} = 0")
                            continue
                        if arg1 == '1' and arg2 == '1':
                            optimized_code.append(f"{res} = 0")
                            continue
                        if (arg1 == '0' and arg2 == '1') or (arg1 == '1' and arg2 == '0'):
                            optimized_code.append(f"{res} = 1")
                            continue
                        # Identity: X ^ 0 -> X
                        if arg1 == '0':
                            optimized_code.append(f"{res} = {arg2}")
                            continue
                        if arg2 == '0':
                            optimized_code.append(f"{res} = {arg1}")
                            continue
                        # Inverse: X ^ 1 -> !X (not implemented in single step, leave as XOR)
                        # Self inverse: X ^ X -> 0 (requires variable tracking, skipping for simple optimizer)

            optimized_code.append(line)
        return optimized_code
