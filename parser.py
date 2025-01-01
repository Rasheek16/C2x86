import re
import sys
from typing import List

from _ast5 import *


def isKeyword(token):
    if token in ('int','return','main','void'):
        return True 
    return False
    

def isIntegerConstant(token: str) -> bool:
    """
    Checks if a token is an integer constant.
    
    Args:
        token (str): The token to check.
    
    Returns:
        bool: True if the token is an integer constant, False otherwise.
    """
    return re.fullmatch(r"\d+", token) is not None


def isIdentifier(token: str) -> bool:
    """
    Checks if a token is a valid identifier.
    
    Args:
        token (str): The token to check.
    
    Returns:
        bool: True if the token is a valid identifier, False otherwise.
    """
    # Matches valid C-like identifier (starts with letter or underscore)
    # and followed by zero or more word characters (letters, digits, underscore)
    return re.fullmatch(r"[a-zA-Z_]\w*", token) is not None


def take_token(tokens: List[str]) :
    """
    Utility function to consume and return the next token from the token list.
    
    Args:
        tokens (List[str]): The list of tokens.
    
    Returns:
        tuple: A tuple containing the consumed token and the remaining tokens.
    
    Raises:
        SyntaxError: If the token list is empty.
    """
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    token = tokens.pop(0)
    return token, tokens


def expect(expected: str, tokens: List[str]):
    """
    Utility function to consume the next token if it matches the expected value.
    
    Args:
        expected (str): The expected token value.
        tokens (List[str]): The list of tokens.
    
    Raises:
        SyntaxError: If the next token does not match the expected value.
    """
    if not tokens:
        raise SyntaxError(f"Expected '{expected}', but reached end of input")
    token = tokens.pop(0)
    if token != expected:
        raise SyntaxError(f"Expected '{expected}', got '{token}'")


def parse_program(tokens: List[str]) -> Program:
    # print(tokens)
    """
    Parses the <program> ::= <function> rule.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        Program: The parsed Program AST node.
    
    Raises:
        SyntaxError: If parsing fails.
    """
    try:
        # Parse the function definition
        function_definition = parse_function_definition(tokens)
        
        # The grammar specifies only one function. If there are remaining tokens, it's an error.
        if tokens:
            raise SyntaxError("Unexpected tokens after function definition")
        
        return Program(function_definition)
    except Exception as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)


def parse_function_definition(tokens: List[str]) -> Function:
    """
    Parses the <function> ::= "int" <identifier> "(" "void" ")" "{" { <block-item> } "}" rule.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        Function: The parsed Function AST node.
    
    Raises:
        SyntaxError: If parsing fails.
    """
    try:
        # Expect "int" keyword
        expect("int", tokens)
        
        # Parse <identifier> for the function name
        identifier_token, tokens = take_token(tokens)
        if not isIdentifier(identifier_token):
            raise SyntaxError(f"Invalid identifier for function name: '{identifier_token}'")
        func_name = Identifier(identifier_token)
        
        # Expect "(" "void" ")"
        expect("(", tokens)
        expect("void", tokens)
        expect(")", tokens)
        
        # Expect "{" to start the function body
        expect("{", tokens)
        
        # Parse zero or more block-items until "}"
        function_body = []
        #* { <block-item> } Curly braces indicate code repetition
        while tokens and tokens[0] != "}":
            # if tokens[0] == "int":
            #     # It's a declaration
            #     declaration = parse_declaration(tokens)
            #     block_item = D(declaration)
            # else:
            #     # It's a statement
            #     statement = parse_statement(tokens)
            #     block_item = S(statement)
            # block_items.append(block_item)
            next_token = parse_block_item(tokens)
            function_body.append(next_token)
        # Expect "}" to end the function body
        if Return in function_body:
            pass
        else:
            function_body.append(S(Return(Constant(0))))
        print(function_body)
        expect("}", tokens)
        
        # Return the Function AST node
        return Function(name=func_name, body=function_body)
    except Exception as e:
        print(f"Syntax Error in function definition: {e}")
        sys.exit(1)


def parse_block_item(tokens):
    # token,tokens = take_token(tokens)
    # print(tokens[0])
    if tokens[0] == "int":
        # print('parse decl')
        
            # It's a declaration
        declaration = parse_declaration(tokens)
        block_item = D(declaration)
        return block_item
    else:
        # print('parse statement')
        # It's a statement
        statement = parse_statement(tokens)
        block_item = S(statement)
        return block_item
        
    # block_items.append(block_item)

def parse_declaration(tokens: List[str]) -> Declaration:
    """
    Parses the <declaration> ::= "int" <identifier> [ "=" <exp> ] ";" rule.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        Declaration: The parsed Declaration AST node.
    
    Raises:
        SyntaxError: If parsing fails.
    """
    try:
        # Expect "int" keyword
        expect("int", tokens)

        # Parse <identifier> for the variable name
        identifier_token, tokens = take_token(tokens)
        if not isIdentifier(identifier_token):
            raise SyntaxError(f"Invalid identifier in declaration: '{identifier_token}'")
        var_name = Identifier(identifier_token)
        
        # Initialize 'init' to None (optional initializer)
        init = Null()
        
        # Check if the next token is "=" indicating an initializer
        # * [ "=" <exp> ] Square bracket indicate optional code
        if tokens and tokens[0] == "=":
            # Consume "="
            expect("=", tokens)
            
            # Parse <exp> for the initializer
            init, tokens = parse_exp(tokens)
            
        # Expect ";" to end the declaration
        expect(";", tokens)
        
        # Return the Declaration AST node
        return Declaration(name=var_name, init=init)
    except Exception as e:
        print(f"Syntax Error in declaration: {e}")
        sys.exit(1)


def parse_statement(tokens: List[str]) -> Statement:
    """
    Parses the <statement> ::= "return" <exp> ";" | <exp> ";" | ";" rule.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        Statement: The parsed Statement AST node.
    
    Raises:
        SyntaxError: If parsing fails.
    """
    try:
        if not tokens:
            raise SyntaxError("Unexpected end of input when parsing statement.")
        
        next_token = tokens[0]
        
        if next_token == "return":
            # Parse "return" <exp> ";"
            expect("return", tokens)
            exp_node = parse_exp(tokens)[0]
            expect(";", tokens)
            return Return(exp=exp_node)
        elif next_token == ";":
            # Parse ";" as a null statement
            expect(";", tokens)
            return Null()
        else:
            # Parse <exp> ";" as an expression statement
            exp_node = parse_exp(tokens)[0]
            expect(";", tokens)
            return Expression(exp=exp_node)
    except Exception as e:
        print(f"Syntax Error in statement: {e}")
        sys.exit(1)


def parse_exp(tokens: List[str], min_prec: int = 0) :
    """
    Parses an expression using the precedence climbing (Pratt) parsing technique.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
        min_prec (int): The minimum precedence level for operators.
    
    Returns:
        tuple: A tuple containing the parsed Exp AST node and the remaining tokens.
    
    Raises:
        SyntaxError: If parsing fails.
    """
    try:
        # Parse the left-hand side (lhs) as a factor
        lhs, tokens = parse_factor(tokens)
        # print(tokens)
        while True:
            if not tokens:
                break
            op = tokens[0]
            binop_info = parse_binop_info(op)
            if not binop_info:
                break  # Not a binary operator
            
            prec = binop_info['precedence']
            assoc = binop_info['associativity']
            
            if prec < min_prec:
                break  # Current operator precedence is too low
            
            # Consume the operator
            # operator_token, tokens = take_token(tokens)
            # print(operator_token)
            # operator = parse_binop(operator_token)
            
            # Determine the next minimum precedence based on associativity
            if assoc == 'LEFT':
                next_min_prec = prec + 1
            else:  # 'RIGHT'
                next_min_prec = prec
            next_token = tokens[0]
            # print(tokens)
            if next_token =='=':
                # print('found assignment')
                _,tokens = take_token(tokens)
                right,tokens = parse_exp(tokens,next_min_prec)
                lhs = Assignment(lhs,right)
                
            else:
                # print('not assignent')
                token,tokens = take_token(tokens)
                operator = parse_binop(token)
                # print('Parsed operator')
                # Parse the right-hand side (rhs) expression
                rhs, tokens = parse_exp(tokens, next_min_prec)
                
                # Combine lhs and rhs into a Binary AST node
                lhs = Binary(operator=operator, left=lhs, right=rhs)
                
        
        return lhs, tokens
    except Exception as e:
        print(f"Syntax Error in expression: {e}")
        sys.exit(1)


def parse_binop_info(token: str) -> Optional[dict]:
    """
    Returns the precedence and associativity information for a given binary operator token.
    
    Args:
        token (str): The binary operator token.
    
    Returns:
        Optional[dict]: A dictionary with 'precedence' and 'associativity' keys, or None if not a binary operator.
    """
    precedence_table = {
        '*': {'precedence': 50, 'associativity': 'LEFT'},
        '/': {'precedence': 50, 'associativity': 'LEFT'},
        '%': {'precedence': 50, 'associativity': 'LEFT'},
        '+': {'precedence': 45, 'associativity': 'LEFT'},
        '-': {'precedence': 45, 'associativity': 'LEFT'},
        '<': {'precedence': 35, 'associativity': 'LEFT'},
        '<=': {'precedence': 35, 'associativity': 'LEFT'},
        '>': {'precedence': 35, 'associativity': 'LEFT'},
        '>=': {'precedence': 35, 'associativity': 'LEFT'},
        '==': {'precedence': 30, 'associativity': 'LEFT'},
        '!=': {'precedence': 30, 'associativity': 'LEFT'},
        '&&': {'precedence': 10, 'associativity': 'LEFT'},
        '||': {'precedence': 5, 'associativity': 'LEFT'},
        '=': {'precedence':1, 'associativity': 'RIGHT'},  # Assignment operator
    }
    return precedence_table.get(token, None)


def parse_binop(operator_token: str) -> BinaryOperator:
    """
    Maps operator tokens to BinaryOperator enums.
    
    Args:
        operator_token (str): The operator token.
    
    Returns:
        BinaryOperator: The corresponding BinaryOperator enum member.
    
    Raises:
        SyntaxError: If the operator token is not recognized.
    """
    binop_mapping = {
        '+': BinaryOperator.ADD,
        '-': BinaryOperator.SUBTRACT,
        '*': BinaryOperator.MULTIPLY,
        '/': BinaryOperator.DIVIDE,
        '%': BinaryOperator.REMAINDER,
        '&&': BinaryOperator.AND,
        '||': BinaryOperator.OR,
        '==': BinaryOperator.EQUAL,
        '!=': BinaryOperator.NOT_EQUAL,
        '<': BinaryOperator.LESS_THAN,
        '<=': BinaryOperator.LESS_OR_EQUAL,
        '>': BinaryOperator.GREATER_THAN,
        '>=': BinaryOperator.GREATER_OR_EQUAL,
        '=': BinaryOperator.ASSIGNMENT,
    }
    if operator_token not in binop_mapping:
        raise SyntaxError(f"Unknown binary operator: '{operator_token}'")
    return binop_mapping[operator_token]


def parse_unop(operator_token: str) -> UnaryOperator:
    """
    Maps operator tokens to UnaryOperator enums.
    
    Args:
        operator_token (str): The operator token.
    
    Returns:
        UnaryOperator: The corresponding UnaryOperator enum member.
    
    Raises:
        SyntaxError: If the operator token is not recognized.
    """
    unop_mapping = {
        '-': UnaryOperator.NEGATE,
        '~': UnaryOperator.COMPLEMENT,
        '!': UnaryOperator.NOT,
    }
    if operator_token not in unop_mapping:
        raise SyntaxError(f"Unknown unary operator: '{operator_token}'")
    return unop_mapping[operator_token]


def parse_factor(tokens: List[str]):
    """
    Parses a <factor> ::= <int> | <identifier> | <unop> <factor> | "(" <exp> ")" rule.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        tuple: A tuple containing the parsed Exp AST node and the remaining tokens.
    
    Raises:
        SyntaxError: If parsing fails.
    """
    if not tokens:
        raise SyntaxError("Unexpected end of input when parsing factor.")
    
    next_token = tokens[0]
    # print(next_token)
    # 1. If it's an integer literal, parse_int.
    if isIntegerConstant(next_token):
        return parse_int(tokens)
    
    # 2. If it's one of the unary operators
    elif next_token in ("-", "~", "!"):
        operator_token, tokens = take_token(tokens)
        operator = parse_unop(operator_token)
        # Parse the sub-expression after the unary operator
        expr, tokens = parse_factor(tokens)
        return Unary(operator=operator, expr=expr), tokens
    
    # 3. If it's an identifier, parse_var.
    elif isIdentifier(next_token) and  not isKeyword(next_token):
        identifier_token, tokens = take_token(tokens)
        identifier = Identifier(name=identifier_token)
        return Var(identifier=identifier), tokens
    
    # 4. If it's "(", parse a parenthesized expression: "(" <exp> ")"
    elif next_token == "(":
        # Consume "("
        _, tokens = take_token(tokens)
        # Parse <exp>
        expr, tokens = parse_exp(tokens)
        # Expect ")"
        expect(")", tokens)
        return expr, tokens
    
    else:
        # If none of the above matches, it's an error for this grammar
        raise SyntaxError(f"Expected <int>, <identifier>, '(', or unary operator, got '{next_token}'")


def parse_int(tokens: List[str]):
    """
    Parses an <int> ::= ? A constant token ? rule.
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        tuple: A tuple containing the parsed Constant AST node and the remaining tokens.
    
    Raises:
        SyntaxError: If the token is not a valid integer.
    """
    token, tokens = take_token(tokens)
    try:
        value = int(token)
        return Constant(value=value), tokens
    except ValueError:
        raise SyntaxError(f"Expected an integer, got '{token}'")