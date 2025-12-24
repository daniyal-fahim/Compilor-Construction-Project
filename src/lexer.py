import re
from typing import List, Tuple, Optional

class Token:
    def __init__(self, type: str, value: str, line: int, column: int):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, '{self.value}', {self.line}:{self.column})"

class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def error(self, msg: str):
        raise Exception(f"Lexer Error at {self.line}:{self.column}: {msg}")

    def tokenize(self) -> List[Token]:
        while self.pos < len(self.text):
            char = self.text[self.pos]

            # Whitespace
            if char.isspace():
                if char == '\n':
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.pos += 1
                continue

            # Keywords and Identifiers
            if char.isalpha():
                start_col = self.column
                value = ""
                while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                    value += self.text[self.pos]
                    self.pos += 1
                    self.column += 1
                
                token_type = 'ID'
                if value == 'expr': token_type = 'KW_EXPR'
                elif value == 'set': token_type = 'KW_SET'
                elif value == 'table': token_type = 'KW_TABLE'
                elif value == 'eval': token_type = 'KW_EVAL'
                elif value == 'infer': token_type = 'KW_INFER'
                elif value == 'xor': token_type = 'XOR'
                
                self.tokens.append(Token(token_type, value, self.line, start_col))
                continue

            # Numbers (Booleans)
            if char in ('0', '1'):
                self.tokens.append(Token('BOOL', char, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            # Operators and Punctuation
            if char == '-':
                if self.pos + 1 < len(self.text) and self.text[self.pos + 1] == '>':
                    self.tokens.append(Token('IMPLIES', '->', self.line, self.column))
                    self.pos += 2
                    self.column += 2
                    continue
                else:
                    self.error(f"Unexpected character '{char}'")

            single_char_tokens = {
                '&': 'AND',
                '|': 'OR',
                '!': 'NOT',
                '^': 'XOR',
                '(': 'LPAREN',
                '(': 'LPAREN',
                ')': 'RPAREN',
                ';': 'SEMICOL',
                '=': 'EQUAL',
                ':': 'COLON',
                ',': 'COMMA'
            }

            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, self.line, self.column))
                self.pos += 1
                self.column += 1
                continue

            self.error(f"Unexpected character '{char}'")

        self.tokens.append(Token('EOF', '', self.line, self.column))
        return self.tokens
