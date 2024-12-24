from AST import * 
import re 
import sys 

def isIdentifier(token):
    return re.match(r"[a-zA-Z_]\w*\b",token)

def parse_program(tokens):
   try:
        function_definition = parse_function_definition(tokens)
        return Program(function_definition)
   except Exception as e:
        print(e)
        sys.exit(1)
        
def parse_function_definition(tokens):
   try:
        expect("int", tokens)
        identifier, tokens = take_token(tokens)
        if not isIdentifier(identifier):
            raise Exception('Invalid Identier')
        expect("(", tokens)
        expect("void", tokens)
        expect(")", tokens)
        expect("{", tokens)
        statement = parse_statement(tokens)
        expect("}", tokens)
        if tokens:
            raise ValueError('Junk spotted at the end of code')
        return Function(identifier, statement)
   except Exception as e:
       sys.exit(1)


def parse_statement(tokens):
    expect("return", tokens)
    exp = parse_exp(tokens)
    expect(";", tokens)
    return Return(exp)

def parse_int(tokens):
    token, tokens = take_token(tokens)
    try:
        value = int(token)
        return Constant(value)
    except ValueError:
        raise SyntaxError(f"Expected an integer, got {token}")

def parse_identifier(tokens):
    token, tokens = take_token(tokens)
    if not isIdentifier(token):
        raise SyntaxError(f"Expected an identifier, got {token}")
    return Identifier(token)

def parse_exp(tokens):
    try:
        return parse_int(tokens)
    except SyntaxError:
        token, _ = take_token(tokens)
        raise SyntaxError(f"Expected integer, got {token}")

def take_token(tokens):
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    token = tokens.pop(0)
    return token, tokens

def expect(expected, tokens):
    token, tokens = take_token(tokens)
    if token != expected:
        sys.exit(1)
        raise SyntaxError(f"Expected {expected}, got {token}")
    return tokens