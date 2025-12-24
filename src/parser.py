from typing import List, Optional
from .lexer import Token, Lexer
from .ast_nodes import *

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[0]

    def eat(self, token_type: str):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error(f"Expected token {token_type}, found {self.current_token.type}")

    def error(self, msg: str):
        raise Exception(f"Parser Error at {self.current_token.line}:{self.current_token.column}: {msg}")

    def parse(self) -> Program:
        statements = []
        while self.current_token.type != 'EOF':
            stmt = self.parse_stmt()
            if stmt:
                statements.append(stmt)
        return Program(statements)

    def parse_stmt(self) -> Stmt:
        if self.current_token.type == 'KW_EXPR':
            return self.parse_expr_stmt()
        elif self.current_token.type == 'KW_SET':
            return self.parse_set_stmt()
        elif self.current_token.type == 'KW_TABLE':
            return self.parse_table_stmt()
        elif self.current_token.type == 'KW_EVAL':
            return self.parse_eval_stmt()
        elif self.current_token.type == 'KW_INFER':
            return self.parse_infer_stmt()
        elif self.current_token.type == 'ID':
            # Could be rule_stmt (ID : expr ;)
            if self.peek().type == 'COLON':
                return self.parse_rule_stmt()
            else:
                self.error("Unexpected ID at start of statement. Did you mean 'expr' or 'set'?")
        else:
            self.error(f"Unexpected token {self.current_token.type} at start of statement")

    def peek(self) -> Token:
        if self.pos + 1 < len(self.tokens):
            return self.tokens[self.pos + 1]
        return self.tokens[-1]

    def parse_expr_stmt(self) -> ExprStmt:
        self.eat('KW_EXPR')
        name = None
        # Check if next token is ID and the one after is NOT a binary operator or semicolon or parenthesis (start of expr)
        # Actually, simpler: if we see ID, and then another ID or literal or '(', it's likely a name.
        # But 'A & B' starts with ID 'A'.
        # 'expr A & B;' -> name=None, expr=A&B
        # 'expr expr1 A & B;' -> name=expr1, expr=A&B
        # We can peek twice?
        # If current is ID:
        #   If next is '=' or ':' or start of expression...
        #   Ambiguity: 'expr A' could be name 'A' with missing expr, or expr 'A'.
        #   Let's assume if there are two IDs in a row, the first is the name.
        #   Or if we see ID then (
        
        # Heuristic: If current is ID, and next is also ID or '(', or '!', or 'BOOL', then current is name.
        # If current is ID and next is operator (AND, OR, IMPLIES, SEMICOL), then current is part of expression.
        
        if self.current_token.type == 'ID':
            next_tok = self.peek()
            if next_tok.type in ['ID', 'LPAREN', 'NOT', 'BOOL']:
                name = self.current_token.value
                self.eat('ID')
        
        expr = self.parse_expression()
        self.eat('SEMICOL')
        return ExprStmt(expr, name)

    def parse_set_stmt(self) -> SetStmt:
        self.eat('KW_SET')
        name = self.current_token.value
        self.eat('ID')
        self.eat('EQUAL')
        val_token = self.current_token
        self.eat('BOOL')
        self.eat('SEMICOL')
        return SetStmt(name, val_token.value == '1')

    def parse_table_stmt(self) -> TableStmt:
        self.eat('KW_TABLE')
        target_id = None
        if self.current_token.type == 'ID':
            target_id = self.current_token.value
            self.eat('ID')
        self.eat('SEMICOL')
        return TableStmt(target_id)

    def parse_eval_stmt(self) -> EvalStmt:
        self.eat('KW_EVAL')
        self.eat('SEMICOL')
        return EvalStmt()

    def parse_rule_stmt(self) -> RuleStmt:
        name = self.current_token.value
        self.eat('ID')
        self.eat('COLON')
        expr = self.parse_expression()
        self.eat('SEMICOL')
        return RuleStmt(name, expr)

    def parse_infer_stmt(self) -> InferStmt:
        self.eat('KW_INFER')
        rule_names = []
        rule_names.append(self.current_token.value)
        self.eat('ID')
        while self.current_token.type == 'COMMA':
            self.eat('COMMA')
            rule_names.append(self.current_token.value)
            self.eat('ID')
        self.eat('SEMICOL')
        return InferStmt(rule_names)

    # Expression Parsing
    def parse_expression(self) -> Expr:
        return self.parse_implication()

    def parse_implication(self) -> Expr:
        node = self.parse_or()
        if self.current_token.type == 'IMPLIES':
            op = self.current_token.value
            self.eat('IMPLIES')
            right = self.parse_implication() # Right associative
            node = BinaryOp(node, op, right)
        return node

    def parse_or(self) -> Expr:
        node = self.parse_xor()
        while self.current_token.type == 'OR':
            op = self.current_token.value
            self.eat('OR')
            right = self.parse_xor()
            node = BinaryOp(node, op, right)
        return node

    def parse_xor(self) -> Expr:
        node = self.parse_and()
        while self.current_token.type == 'XOR':
            op = self.current_token.value
            self.eat('XOR') # consume 'xor' or '^'
            right = self.parse_and()
            node = BinaryOp(node, 'xor', right) # Normalize op name
        return node

    def parse_and(self) -> Expr:
        node = self.parse_not()
        while self.current_token.type == 'AND':
            op = self.current_token.value
            self.eat('AND')
            right = self.parse_not()
            node = BinaryOp(node, op, right)
        return node

    def parse_not(self) -> Expr:
        if self.current_token.type == 'NOT':
            op = self.current_token.value
            self.eat('NOT')
            node = self.parse_not()
            return UnaryOp(op, node)
        return self.parse_primary()

    def parse_primary(self) -> Expr:
        token = self.current_token
        if token.type == 'ID':
            self.eat('ID')
            return Var(token.value)
        elif token.type == 'BOOL':
            self.eat('BOOL')
            return Literal(token.value == '1')
        elif token.type == 'LPAREN':
            self.eat('LPAREN')
            node = self.parse_expression()
            self.eat('RPAREN')
            return node
        else:
            self.error(f"Unexpected token in expression: {token.type}")
