import re
import sys

from _Ast import (  # <-- Make sure your _Ast.py matches these classes
    Program, 
    Function, 
    Return, 
    Constant, 
    Unary, 
    Identifier, 
    UnaryOperator
)

def isIdentifier(token):
    # Matches valid C-like identifier (starts with letter or underscore)
    # and followed by zero or more word characters (letters, digits, underscore)
    return re.match(r"^[a-zA-Z_]\w*$", token)

def parse_program(tokens):
    """
    <program> ::= <function>
    """
    try:
        function_definition = parse_function_definition(tokens)
        
        # The grammar says only one function. If there's anything left, it's junk.
        if tokens:
            raise SyntaxError("Unexpected tokens after function definition")
        
        return Program(function_definition)
    except Exception as e:
        print(e)
        sys.exit(1)

def parse_function_definition(tokens):
    """
    <function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
    """
    try:
        # Expect "int"
        expect("int", tokens)
        
        # Parse <identifier>
        identifier_token, tokens = take_token(tokens)
        if not isIdentifier(identifier_token):
            raise SyntaxError(f"Invalid identifier: {identifier_token}")
        func_name = Identifier(identifier_token)
        
        # Expect "(" "void" ")" 
        expect("(", tokens)
        expect("void", tokens)
        expect(")", tokens)
        
        # Expect "{" 
        expect("{", tokens)
        
        # Parse <statement>
        statement = parse_statement(tokens)
        
        # Expect "}"
        expect("}", tokens)
        
        # Return a Function node
        return Function(func_name, statement)
    except Exception as e:
        print(e)
        sys.exit(1)

def parse_statement(tokens):
    """
    <statement> ::= "return" <exp> ";"
    """
    # Expect "return"
    expect("return", tokens)
    
    # Parse <exp>
    exp_node = parse_exp(tokens)
    
    # Expect ";"
    expect(";", tokens)
    
    return Return(exp_node)

def parse_exp(tokens):
    """
    <exp> ::= <int> | <unop> <exp> | "(" <exp> ")"
    """
    # Look at the first token but do not consume it (yet).
    if not tokens:
        raise SyntaxError("Unexpected end of input in expression.")
    
    next_token = tokens[0]

    # 1. If it's an integer literal, parse_int.
    if re.match(r"^-?\d+$", next_token):  
        return parse_int(tokens)
    
    # 2. If it's one of the unary operators
    elif next_token in ("-", "~"):
        unop, tokens = take_token(tokens)
        
        if unop == "-":
            operator = UnaryOperator.NEGATE
        else:
            operator = UnaryOperator.COMPLEMENT
        
        # Parse the sub-expression after the unary operator
        subexpr = parse_exp(tokens)
        return Unary(operator, subexpr)
    
    # 3. If it's "(" then parse a parenthesized expression: "(" <exp> ")"
    elif next_token == "(":
        expect("(", tokens)
        subexpr = parse_exp(tokens)
        expect(")", tokens)
        return subexpr
    
    else:
        # If none of the above matches, it's an error for this grammar
        raise SyntaxError(f"Expected <int>, '(', or unary operator, got '{next_token}'")

def parse_int(tokens):
    """
    <int> ::= ? A constant token ?
    Consumes one token and attempts to parse it as an integer.
    """
    token, tokens = take_token(tokens)
    try:
        value = int(token)
        return Constant(value)
    except ValueError:
        raise SyntaxError(f"Expected an integer, got '{token}'")

def take_token(tokens):
    """
    Utility: pop a token from the list (front).
    Raises error if list is empty.
    """
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    token = tokens.pop(0)
    return token, tokens

def expect(expected, tokens):
    """
    Utility: consume the next token if it matches 'expected'.
    Otherwise, raise error.
    """
    token, tokens = take_token(tokens)
    if token != expected:
        sys.exit(1)  # or raise SyntaxError
        raise SyntaxError(f"Expected '{expected}', got '{token}'")
    return tokens
