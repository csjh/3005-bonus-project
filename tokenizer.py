from enum import Enum

delimiter = ['(', ')', ',', '{', '}', '"', 'EOF']
unary_operator = ['π', '𝞂', 'ρ']
binary_operator = ['⨉', '⨝', '⟕', '⟖', '⟗', '∪', '∩', '-', '/']
predicate_operator = ['<', '>', '=', '≤', '≥', '≠', '→']
TokenType = Enum('TokenType', ['NUMBER', 'IDENTIFIER', 'UNARY_OPERATOR', 'BINARY_OPERATOR', 'PREDICATE_OPERATOR', 'DELIMITER'])

def tokenize(text: str) -> list[tuple[TokenType, str]]:
    tokens = []
    i = 0
    while i < len(text):
        if text[i].isspace():
            i += 1
            continue
        if text[i] in delimiter:
            tokens.append((TokenType.DELIMITER, text[i]))
            i += 1
            continue
        if text[i] in unary_operator:
            tokens.append((TokenType.UNARY_OPERATOR, text[i]))
            i += 1
            continue
        if text[i] in binary_operator:
            tokens.append((TokenType.BINARY_OPERATOR, text[i]))
            i += 1
            continue
        if text[i] in predicate_operator:
            tokens.append((TokenType.PREDICATE_OPERATOR, text[i]))
            i += 1
            continue
        if text[i].isdigit():
            j = i + 1
            while j < len(text) and text[j].isdigit():
                j += 1
            tokens.append((TokenType.NUMBER, text[i:j]))
            i = j
            continue
        if text[i].isalpha():
            j = i + 1
            while j < len(text) and text[j].isalnum():
                j += 1
            tokens.append((TokenType.IDENTIFIER, text[i:j]))
            i = j
            continue
        raise ValueError('Unknown token: ' + text[i])
    
    tokens.append((TokenType.DELIMITER, 'EOF'))

    return tokens
