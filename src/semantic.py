from typing import List, Set, Dict
from .ast_nodes import *

class SemanticAnalyzer:
    def __init__(self):
        self.declared_vars: Set[str] = set()
        self.defined_rules: Set[str] = set()

    def visit(self, node: ASTNode):
        method_name = 'visit_' + node.__class__.__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: ASTNode):
        raise Exception(f"No visit_{node.__class__.__name__} method")

    def visit_Program(self, node: Program):
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ExprStmt(self, node: ExprStmt):
        self.visit(node.expr)

    def visit_SetStmt(self, node: SetStmt):
        # In LogicEval, 'set' implicitly declares a variable if not seen before,
        # or updates it. So we just track it.
        self.declared_vars.add(node.name)

    def visit_TableStmt(self, node: TableStmt):
        if node.target_id:
            # If table is for a specific rule/ID, check if it exists (or is a variable)
            # For now, we assume it refers to a rule or a variable.
            pass 

    def visit_EvalStmt(self, node: EvalStmt):
        pass

    def visit_RuleStmt(self, node: RuleStmt):
        if node.name in self.defined_rules:
            raise Exception(f"Semantic Error: Rule '{node.name}' already defined.")
        self.defined_rules.add(node.name)
        self.visit(node.expr)

    def visit_InferStmt(self, node: InferStmt):
        for name in node.rule_names:
            if name not in self.defined_rules:
                raise Exception(f"Semantic Error: Inference on undefined rule '{name}'.")

    def visit_BinaryOp(self, node: BinaryOp):
        self.visit(node.left)
        self.visit(node.right)

    def visit_UnaryOp(self, node: UnaryOp):
        self.visit(node.operand)

    def visit_Literal(self, node: Literal):
        pass

    def visit_Var(self, node: Var):
        # LogicEval allows using variables in expressions without prior 'set'.
        # They are just free variables.
        pass
