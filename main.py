from tokenizer import tokenize
from parse import Parser
from executor import Executor
import re
from datastructures import Row, Relation

relation_title = re.compile(r"(?P<table>\w*) \((?P<columns>(?:\w*(?:, )?)*)\) = {")

definitions = "./definitions.rel"
text = open(definitions, "r").read().strip().split("\n\n")

relations = {}
for relation in text:
    relation = relation.split("\n")
    if relation[-1] != '}':
        raise ValueError('Missing closing bracket')

    metadata = relation_title.match(relation[0]).groupdict()
    columns = metadata['columns'].split(', ')

    relations[metadata['table']] = set()
    for row in map(str.strip, relation[1:-1]):
        cells = row.split(", ")
        relations[metadata['table']].add(Row(zip(columns, cells)))
    relations[metadata['table']] = Relation(relations[metadata['table']])

queryfile = "./query.rel"
for text in open(queryfile, "r").read().splitlines():
    tokens = tokenize(text)
    ast = Parser.parse(tokens)
    res = Executor.execute(ast, relations)

    print(f"Query: {text}")
    for column in res.columns:
        print(str(column).rjust(15), end="")
    print('\n' + '-' * 15 * len(res.columns))
    for row in res:
        for column in res.columns:
            print(str(row[column]).rjust(15), end="")
        print()
    print()
