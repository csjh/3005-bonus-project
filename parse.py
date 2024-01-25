from enum import Enum
from tokenizer import TokenType
import re
import operator as op

ExpressionType = Enum('ExpressionType', ['NUMBER', 'IDENTIFIER', 'UNARY_OPERATOR', 'BINARY_OPERATOR'])

class Parser:
    @staticmethod
    def parse(tokens: list[tuple[TokenType, str]]):
        return Parser(tokens).parse_expression()
    
    def __init__(self, tokens: list[tuple[TokenType, str]]):
        self.tokens = tokens
        self.index = 0

    def parse_expression(self, greedy=False):
        expr = None
        while True:
            if self.tokens[self.index][1] == '(':
                self.index += 1
                expr = self.parse_expression()
                self.index += 1
            elif self.tokens[self.index][0] == TokenType.UNARY_OPERATOR:
                operator = self.tokens[self.index][1]
                self.index += 1
                args = None
                if operator == 'π':
                    self.index += 1
                    args = self.read_pi_columns()
                    self.index += 1
                elif operator == '𝞂':
                    self.index += 1
                    args = self.read_predicate()
                    self.index += 1
                elif operator == 'ρ':
                    self.index += 1
                    args = self.read_renamed_columns()
                    self.index += 1
                expr = (ExpressionType.UNARY_OPERATOR, operator, args, self.parse_expression(greedy=True))
            elif self.tokens[self.index][0] == TokenType.IDENTIFIER:
                identifier = self.tokens[self.index][1]
                self.index += 1
                expr = (ExpressionType.IDENTIFIER, identifier)
            elif self.tokens[self.index][0] == TokenType.DELIMITER and (self.tokens[self.index][1] == 'EOF' or self.tokens[self.index][1] == ')'):
                return expr
            else:
                raise Exception(f'Unexpected token: {self.tokens[self.index][1]} of type {self.tokens[self.index][0]}')

            if greedy or self.index == len(self.tokens) or self.tokens[self.index][0] != TokenType.BINARY_OPERATOR:
                return expr

            operator = self.tokens[self.index][1]
            self.index += 1
            
            if operator in ['⨝', '⟕', '⟖', '⟗']:
                columns = self.read_join_columns()
                expr = (ExpressionType.BINARY_OPERATOR, operator, expr, self.parse_expression(), columns)
            else:
                expr = (ExpressionType.BINARY_OPERATOR, operator, expr, self.parse_expression())
                
    def read_renamed_columns(self):
        columns = []
        while self.tokens[self.index][1] != '}':
            if self.tokens[self.index][0] != TokenType.IDENTIFIER:
                raise Exception('Expected identifier')
            left_col = self.tokens[self.index][1]
            self.index += 1

            if self.tokens[self.index][1] != '→':
                raise Exception(f'Expected →')
            self.index += 1

            if self.tokens[self.index][0] != TokenType.IDENTIFIER:
                raise Exception('Expected identifier')
            right_col = self.tokens[self.index][1]
            self.index += 1

            columns.append([left_col, right_col])

            if self.tokens[self.index][1] == ',':
                self.index += 1
        return columns

    def read_join_columns(self):
        if self.tokens[self.index][1] != '{': return None
        self.index += 1
        columns = []
        while self.tokens[self.index][1] != '}':
            if self.tokens[self.index][0] != TokenType.IDENTIFIER:
                raise Exception('Expected identifier')
            left_col = self.tokens[self.index][1]
            self.index += 1

            if self.tokens[self.index][1] != '=':
                raise Exception(f'Expected =')
            self.index += 1

            if self.tokens[self.index][0] != TokenType.IDENTIFIER:
                raise Exception('Expected identifier')
            right_col = self.tokens[self.index][1]
            self.index += 1

            columns.append([left_col, right_col])

            if self.tokens[self.index][1] == ',':
                self.index += 1
        self.index += 1
        return columns

    def read_pi_columns(self):
        columns = []
        while self.tokens[self.index][1] != '}':
            if self.tokens[self.index][0] != TokenType.IDENTIFIER:
                raise Exception(f'Expected identifier got {self.tokens[self.index][1]}')
            columns.append(self.tokens[self.index][1])
            self.index += 1
            if self.tokens[self.index][1] == ',':
                self.index += 1
        return columns

    def read_pi_columns(self):
        columns = []
        while self.tokens[self.index][1] != '}':
            if self.tokens[self.index][0] != TokenType.IDENTIFIER:
                raise Exception(f'Expected identifier got {self.tokens[self.index][1]}')
            columns.append(self.tokens[self.index][1])
            self.index += 1
            if self.tokens[self.index][1] == ',':
                self.index += 1
        return columns
    
    def read_predicate(self):
        left, operator, right = None, None, None
        if self.tokens[self.index][1] == '"':
            self.index += 1
            left = ('string', self.tokens[self.index][1])
            self.index += 2
        elif self.tokens[self.index][0] == TokenType.IDENTIFIER:
            left = ('identifier', self.tokens[self.index][1])
            self.index += 1
        else:
            raise Exception('Expected identifier or string')
        
        if self.tokens[self.index][1] == '<':
            operator = op.lt
        elif self.tokens[self.index][1] == '>':
            operator = op.gt
        elif self.tokens[self.index][1] == '=':
            operator = op.eq
        elif self.tokens[self.index][1] == '≤':
            operator = op.le
        elif self.tokens[self.index][1] == '≥':
            operator = op.ge
        elif self.tokens[self.index][1] == '≠':
            operator = op.ne
        else:
            raise Exception('Expected predicate operator')
        self.index += 1
        
        if self.tokens[self.index][1] == '"':
            self.index += 1
            right = ('string', self.tokens[self.index][1])
            self.index += 2
        elif self.tokens[self.index][0] == TokenType.IDENTIFIER:
            right = ('identifier', self.tokens[self.index][1])
            self.index += 1
        elif self.tokens[self.index][0] == TokenType.NUMBER:
            right = ('number', float(self.tokens[self.index][1]))
            self.index += 1
        else:
            print(self.tokens[self.index])
            raise Exception('Expected identifier or string')
        
        return (left, operator, right)
