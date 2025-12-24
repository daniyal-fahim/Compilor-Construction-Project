from typing import List, Tuple
from .ast_nodes import *

class IRGenerator:
    def __init__(self):
        self.temp_counter = 0
        self.code = []

    def new_temp(self) -> str:
        self.temp_counter += 1
        return f"t{self.temp_counter}"

    def generate(self, node: ASTNode) -> List[str]:
        self.code = []
        self.visit(node)
        return self.code

    def visit(self, node: ASTNode):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise Exception(f"No IR visit_{node.__class__.__name__} method")

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ExprStmt(self, node: ExprStmt):
        result = self.visit_expression(node.expr)
        if node.name:
            self.code.append(f"{node.name} = {result}")
        # Ensure we have some code for the expression if it's just a variable or literal
        if not self.code:
            self.code.append(f"t_res = {result}")

    def visit_SetStmt(self, node: SetStmt):
        val = '1' if node.value else '0'
        self.code.append(f"{node.name} = {val}")

    def visit_TableStmt(self, node: TableStmt):
        target = node.target_id if node.target_id else "LAST_EXPR"
        self.code.append(f"TABLE {target}")

    def visit_EvalStmt(self, node: EvalStmt):
        self.code.append("EVAL")

    def visit_RuleStmt(self, node: RuleStmt):
        # For rules, we might want to store the expression logic.
        # In 3AC, we can treat it as a label or assignment.
        # Simplified: Assign result of expr to the rule name.
        result = self.visit_expression(node.expr)
        self.code.append(f"{node.name} = {result}")

    def visit_InferStmt(self, node: InferStmt):
        args = " ".join(node.rule_names)
        self.code.append(f"INFER {args}")

    def visit_expression(self, node: Expr) -> str:
        if isinstance(node, BinaryOp):
            left = self.visit_expression(node.left)
            right = self.visit_expression(node.right)
            temp = self.new_temp()
            op_map = {'&': 'AND', '|': 'OR', '->': 'IMPLIES', 'xor': 'XOR'}
            self.code.append(f"{temp} = {op_map[node.op]} {left} {right}")
            return temp
        elif isinstance(node, UnaryOp):
            operand = self.visit_expression(node.operand)
            temp = self.new_temp()
            self.code.append(f"{temp} = NOT {operand}")
            return temp
        elif isinstance(node, Literal):
            return '1' if node.value else '0'
        elif isinstance(node, Var):
            return node.name
        return ""
