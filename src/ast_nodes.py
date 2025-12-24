from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

# Expressions
@dataclass
class Expr(ASTNode):
    pass

@dataclass
class BinaryOp(Expr):
    left: Expr
    op: str  # '&', '|', '->'
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str  # '!'
    operand: Expr

@dataclass
class Literal(Expr):
    value: bool

@dataclass
class Var(Expr):
    name: str

# Statements
@dataclass
class Stmt(ASTNode):
    pass

@dataclass
class ExprStmt(Stmt):
    expr: Expr
    name: Optional[str] = None

@dataclass
class SetStmt(Stmt):
    name: str
    value: bool

@dataclass
class TableStmt(Stmt):
    target_id: Optional[str]

@dataclass
class EvalStmt(Stmt):
    pass

@dataclass
class RuleStmt(Stmt):
    name: str
    expr: Expr

@dataclass
class InferStmt(Stmt):
    rule_names: List[str]
