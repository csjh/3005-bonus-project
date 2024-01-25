from parse import ExpressionType
from functools import reduce
from operator import __and__
from datastructures import Row, Relation

class Executor:
    @staticmethod
    def execute(ast, relations) -> Relation:
        return Executor(ast, relations)._execute()

    def __init__(self, ast, relations):
        self.ast = ast
        self.relations = relations

    def _execute(self) -> Relation:
        if self.ast[0] == ExpressionType.IDENTIFIER:
            return self.relations[self.ast[1]]
        elif self.ast[0] == ExpressionType.UNARY_OPERATOR:
            return self.execute_unary_operator()
        elif self.ast[0] == ExpressionType.BINARY_OPERATOR:
            return self.execute_binary_operator()

    def execute_unary_operator(self) -> Relation:
        if self.ast[1] == 'π':
            return self.execute_pi()
        elif self.ast[1] == '𝞂':
            return self.execute_sigma()
        elif self.ast[1] == 'ρ':
            return self.execute_rho()
        else:
            raise Exception(f'Unknown unary operator: {self.ast[1]}')

    def execute_rho(self) -> Relation:
        columns = dict(self.ast[2])
        relation = Executor.execute(self.ast[3], self.relations)
        return Relation(Row((columns.get(k, k), v) for k, v in row) for row in relation)

    def execute_pi(self) -> Relation:
        columns = self.ast[2]
        relation = Executor.execute(self.ast[3], self.relations)
        return Relation(Row(filter(lambda x: x[0] in columns, row)) for row in relation)

    def execute_sigma(self) -> Relation:
        predicate = self.ast[2]
        relation = Executor.execute(self.ast[3], self.relations)
        return Relation(row for row in relation if self.execute_predicate(predicate, row))

    def execute_predicate(self, predicate, row) -> bool:
        left, operator, right = predicate
        
        is_num = left[0] == 'number' or right[0] == 'number'

        if left[0] == 'identifier':
            left = row[left[1]]
        else:
            left = left[1]

        if right[0] == 'identifier':
            right = row[right[1]]
        else:
            right = right[1]
            
        if is_num:
            left = float(left)
            right = float(right)

        return operator(left, right)

    def execute_binary_operator(self) -> Relation:
        if self.ast[1] == '⨉':
            return self.execute_cross_product()
        elif self.ast[1] == '⨝':
            return self.execute_innerjoin()
        elif self.ast[1] == '⟕':
            return self.execute_left_outerjoin()
        elif self.ast[1] == '⟖':
            return self.execute_right_outerjoin()
        elif self.ast[1] == '⟗':
            return self.execute_full_outerjoin()
        elif self.ast[1] == '∪':
            return self.execute_union()
        elif self.ast[1] == '∩':
            return self.execute_intersection()
        elif self.ast[1] == '-':
            return self.execute_difference()
        elif self.ast[1] == '/':
            return self.execute_division()
        else:
            raise Exception(f'Unknown binary operator: {self.ast[1]}')

    def execute_cross_product(self) -> Relation:
        left = Executor.execute(self.ast[2], self.relations)
        right = Executor.execute(self.ast[3], self.relations)
        return Relation(l | r for l in left for r in right)
    
    def get_inner_rows(self, left, right, columns):
        l, r = [], []
        for lrow in left:
            for rrow in right:
                if all(lrow[left_key] == rrow[right_key] for left_key, right_key in columns):
                    l.append(lrow)
                    r.append(rrow)
        return (l, r)

    def do_join(self, isleft, isright):
        left = Executor.execute(self.ast[2], self.relations)
        right = Executor.execute(self.ast[3], self.relations)
        columns = self.ast[4] or [[x, x] for x in left.columns & right.columns]

        right_columns = right.columns - left.columns
        left_columns = left.columns - right.columns
        left_rows, right_rows = self.get_inner_rows(left, right, columns)

        base = Relation(r | l for l, r in zip(left_rows, right_rows))

        if isleft:
            base |= Relation(l | Row({(key, None) for key in right_columns}) for l in left if l not in left_rows)
        if isright:
            base |= Relation(r | Row({(key, None) for key in left_columns}) for r in right if r not in right_rows)
        
        return base

    def execute_innerjoin(self) -> Relation:
        return self.do_join(False, False)
    
    def execute_left_outerjoin(self) -> Relation:
        return self.do_join(True, False)
    
    def execute_right_outerjoin(self) -> Relation:
        return self.do_join(False, True)

    def execute_full_outerjoin(self) -> Relation:
        return self.do_join(True, True)

    def execute_union(self) -> Relation:
        left = Executor.execute(self.ast[2], self.relations)
        right = Executor.execute(self.ast[3], self.relations)
        return left | right
    
    def execute_intersection(self) -> Relation:
        left = Executor.execute(self.ast[2], self.relations)
        right = Executor.execute(self.ast[3], self.relations)
        return left & right
    
    def execute_difference(self) -> Relation:
        left = Executor.execute(self.ast[2], self.relations)
        right = Executor.execute(self.ast[3], self.relations)
        return left - right

    def execute_division(self) -> Relation:
        left = Executor.execute(self.ast[2], self.relations)
        right = Executor.execute(self.ast[3], self.relations)
        groups = { row: set() for row in right }
        for row in left:
            for key in groups:
                if key <= row:
                    groups[key].add(Row(row - key))
        return Relation(reduce(__and__, map(Relation, groups.values())))
