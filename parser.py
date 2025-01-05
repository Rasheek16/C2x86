import re
import sys
from typing import List,Tuple

from _ast5 import *

return_flag = False

def isKeyword(token):
    if token in ('int','return','main','void'):
        return True 
    return False
    
temp_label_counter=1
def get_temp_label():
    global temp_label_counter
    temp_label_counter+=1
    return f'tmp_label.{temp_label_counter}'

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
        
        return Program(function_definition=function_definition)
    except Exception as e:
        print(f"Syntax Error: {e}")
        sys.exit(1)


def parse_param_list(tokens)->Tuple[List[Parameter],str]:
    list_params=[]
    next_token = tokens[0]
    if next_token=='void':
        _,tokens=take_token(tokens)
        # list_params
        return list_params,tokens
    elif next_token=='int':
        token,tokens=take_token(tokens)
        next_token=tokens[0]
        if isIdentifier(next_token) and not isKeyword(next_token):
            token,tokens =take_token(tokens)
            list_params.append(Parameter('int',Identifier(token)))
            if tokens[0] == ")":
                
                # print(list_params)
                return list_params,tokens
        else:
            raise SyntaxError('In parse param list Expected identifier , got',next_token)
        while True:
            expect(',',tokens)
            next_token=='int'
            token,tokens=take_token(tokens)
            next_token=tokens[0]
            if isIdentifier(next_token) and not isKeyword(next_token):
                token,tokens =take_token(tokens)
                list_params.append(Parameter(int,Identifier(next_token)))
                if tokens[0] == ")":
                    return list_params,tokens
                else: 
                    pass 
            else:
                raise SyntaxError('In parse param Expected identifier , got in loop ',next_token)
           
                
def parse_args_list(tokens)->Tuple[List[Exp],str]:
    arg_body = []
    if tokens[0]!=')':
        exp,tokens=parse_exp(tokens)
        arg_body.append(exp)
    while tokens and tokens[0] != ")":
        expect(',',tokens)
        block,tokens = parse_exp(tokens)
        arg_body.append(block)
    
    return arg_body,tokens
    
        
    
def parse_func_declaration(tokens):
    # print(tokens)
    expect("int", tokens)
    # Parse <identifier> for the variable name
    identifier_token, tokens = take_token(tokens)
    if not isIdentifier(identifier_token):
        raise SyntaxError(f"Invalid identifier in parse declaration: '{identifier_token}'")
    func_name = Identifier(identifier_token)
    # print(func_name)
    # func_name =
    next_token= tokens[0]
    # print(next_token)
    if next_token=='(':
         return parse_func_decl(tokens,func_name)
    else:
        raise SyntaxError('Exected ( in function declaration got ',next_token)
def parse_func_decl(tokens,func_name:Identifier)->Tuple[FunDecl,str]:
 try:
    exp=Null()
    expect('(',tokens)
    exp,tokens=parse_param_list(tokens)
   
    expect(')',tokens)
    next_token  = tokens[0]
    
    if next_token==';':
        _,tokens=take_token(tokens)
        exp1=FunDecl(name=func_name,params=exp,body=Null()),tokens
        return exp1
    elif next_token=='{':
        list_block_items,tokens=parse_block(tokens)
        
        # func=FunctionDeclaration(name=func_name,init=exp,body=list_block_items)
        return FunDecl(name=func_name,params=exp,body=Block(list_block_items)),tokens
 except Exception as e:
    raise SyntaxError('Error in parse_func_decl',e)
        
    
    
def parse_function_definition(tokens: List[str]) -> List[FunctionDeclaration]:
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
        function_body=[]
        # Expect "int" keyword
        while tokens:
        # Expect "{" to start the function body
            # print(tokens)
            function,tokens = parse_func_declaration(tokens)
            function_body.append(function)
        # function_body.append(S(Return(Constant(0))))
        # Return the Function AST node
        return function_body
    except Exception as e:
        print(f"Syntax Error in function definition: {e}")
        sys.exit(1)

def parse_block(tokens)->Tuple[List[BlockItem],str]:
    expect("{", tokens)
   
        # Parse zero or more block-items until "}"
    function_body = []
        #* { <block-item> } Curly braces indicate code repetition
    while tokens and tokens[0] != "}":
        block = parse_block_item(tokens)
        # print('block:',block)
        if block:  # Append only if valid
            function_body.append(block)
            # print(block)
        # function_body.append(block)
        # Expect "}" to end the function body
   
        # print('func',function_body)
        
    expect("}", tokens)
    # print(function_body)
    return function_body,tokens
    

def parse_block_item(tokens):
    # token,tokens = take_token(tokens)
   
    if tokens[0] == "int":
    
        declaration,tokens = parse_declaration(tokens)
       
        block_item = D(declaration)
       
        return block_item
    else:
        # print('parse statement')
        # It's a statement
        statement = parse_statement(tokens)
        block_item = S(statement)
        return block_item
        
    # block_items.append(block_item)

def parse_variable_declaration(tokens:List[str],var_name:str)->Tuple[VarDecl,str]:
    try:
        
        # Initialize 'init' to None (optional initializer)
        init = Null()
        # new_token = 
        # Check if the next token is "=" indicating an initializer
        # * [ "=" <exp> ] Square bracket indicate optional code
        if tokens and tokens[0] == "=":
            # Consume "="
            expect("=", tokens)
            # print(tokens)
            # Parse <exp> for the initializer
            init, tokens = parse_exp(tokens)
            # print(tokens)
        # Expect ";" to end the declaration
        expect(";", tokens)
        # print(tokens)
        # Return the Declaration AST node
        return VarDecl(name=var_name, init=init),tokens
    except Exception as e:
        print(f"Syntax Error in declaration: {e}")
        sys.exit(1)
    

def parse_declaration(tokens: List[str]):
     
    # Expect "int" keyword
        expect("int", tokens)
        # Parse <identifier> for the variable name
        identifier_token, tokens = take_token(tokens)
        if not isIdentifier(identifier_token):
            raise SyntaxError(f"Invalid identifier in parse declaration: '{identifier_token}'")
        var_name = Identifier(identifier_token)
        func_name = Identifier(identifier_token)
        # func_name =
        next_token= tokens[0]
        if next_token =='(':
            func_decl,tokens=parse_func_decl(tokens,func_name)
            return func_decl,tokens
        elif next_token in ('=',';'):
     
            var_dec,tokens = parse_variable_declaration(tokens,var_name)
            return var_dec,tokens
        else:
            # print('inside decleration',tokens)
            raise SyntaxError('Invalid token expected = or ( for',next_token)


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
            exp_node,tokens = parse_exp(tokens)
            expect(";", tokens)
            global return_flag
            return_flag =True
            return Return(exp=exp_node)
        elif next_token == ";":
            # Parse ";" as a null statement
            expect(";", tokens)
            return Null()
        elif next_token =='if':
            # print('inside if')
            token,tokens=take_token(tokens)
            expect('(',tokens)
            exp_node,tokens = parse_exp(tokens)
            expect(')',tokens)
            statement = parse_statement(tokens)
            # print(statement)
            # print(statement)
            # print(tokens[0])
            # el_statement=None
            if tokens and tokens[0]=='else':
                token,tokens=take_token(tokens)
                el_statement =parse_statement(tokens)
                return If(exp=exp_node,then=statement,_else = el_statement)
                # el_statement=parse_statement(['return','0',';'])
            return If(exp=exp_node,then=statement,_else=Null())
            # print('outside if')
        elif next_token=='{':
            block,tokens=parse_block(tokens)
            return Compound(block=block)
        elif next_token=='break':
            _,tokens=take_token(tokens)
            expect(';',tokens)
            temp_label= get_temp_label()
            return Break()
        elif next_token=='continue':
            _,tokens=take_token(tokens)
            temp_label= get_temp_label()
            expect(';',tokens)
            return Continue()
        elif next_token=='while':
            _,tokens=take_token(tokens)
            expect('(',tokens)
            exp,tokens=parse_exp(tokens)
            expect(')',tokens)
            # exp2,tokens=parse_exp(tokens)
            statement=parse_statement(tokens)
            temp_label=get_temp_label()
            return While(exp,statement)
        elif next_token=='do':
            # print('here')
            _,tokens=take_token(tokens)
           
            statement=parse_statement(tokens)
            # print(statement)
            expect('while',tokens)
            expect('(',tokens)
            exp,tokens=parse_exp(tokens)
            # print(exp)
            expect(')',tokens)
            expect(';',tokens)
            # exp2,tokens=parse_exp(tokens)
            temp_label=get_temp_label()
            return DoWhile(statement,exp)
        # --------------------------
        # Fixed FOR Loop Branch
        # --------------------------
        elif next_token == "for":
            _, tokens = take_token(tokens)  # consume 'for'
            expect("(", tokens)
            
            # Parse initialization
            init, tokens = parse_for_init(tokens)
            
            # Expect and consume first semicolon if it's not a declaration
            if not isinstance(init, InitDecl):
                expect(";", tokens)
            
            # Parse condition
            condition, tokens = parse_optional_parameter(tokens)
            
            # Expect and consume second semicolon
            expect(";", tokens)
            
            # Parse post-expression
            post, tokens = parse_optional_parameter(tokens)
            
            # Expect closing parenthesis
            expect(")", tokens)
            # print(tokens)
            # Parse loop body
            body = parse_statement(tokens)
            # optional get_temp_label() or other side-effect
            
            # Just return the For node (NOT a tuple!)
            return For(init=init, condition=condition, post=post, body=body)
        
        else:
            # Parse expression statement
            exp_node, tokens = parse_exp(tokens)
            expect(";", tokens)
            return Expression(exp_node)
    
    except Exception as e:
        print(f"Syntax Error in statement: {e}")
        sys.exit(1)

def parse_for_init(tokens: List[str]) -> Tuple[Statement, List[str]]:
    """
    Parses the initialization part of a for loop.

    Args:
        tokens (List[str]): The list of tokens to parse.

    Returns:
        Tuple[Statement, List[str]]: The initialization statement and the remaining tokens.
    """
    if tokens[0] == 'int':
        # Parse declaration (e.g., int i = 0)
        if tokens[2]=='(':
            raise SyntaxError('Function not permitted in loop headers')
        decl, tokens = parse_declaration(tokens)
        init_decl = InitDecl(declaration=decl)
        # print(init_decl)
        return init_decl, tokens
    
    elif isIdentifier(tokens[0]) and not isKeyword(tokens[0]):
        if tokens[1]=='(':
            raise SyntaxError('Function not permitted in loop headers')
        # Parse expression (e.g., i = 0)
        exp, tokens = parse_exp(tokens)
        init_exp = InitExp(Expression(exp))
        return init_exp, tokens
    
    else:
        # No initialization; do not consume any tokens
        return Null(), tokens

def parse_optional_parameter(tokens: List[str]) -> Tuple[Statement, List[str]]:
    """
    Parses an optional parameter (condition or post-expression) in a for loop.

    Args:
        tokens (List[str]): The list of tokens to parse.

    Returns:
        Tuple[Statement, List[str]]: The parsed statement or Null, and the remaining tokens.
    """
    if not tokens or tokens[0] in (';', ')'):
        return Null(), tokens
    else:
        exp, tokens = parse_exp(tokens)
        return exp, tokens

def parse_exp(tokens: List[str], min_prec: int = 0) -> Tuple[Exp,List[str]]:
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
        # print('exp',tokens)
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
                # print(right)
                lhs = Assignment(lhs,right)
            elif next_token =='?':
                middle,tokens = parse_conditional_middle(tokens)
                right,token = parse_exp(tokens,next_min_prec)
                lhs  = Conditional(condition=lhs,exp2=middle,exp3=right)
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


def parse_conditional_middle(tokens):
    token,tokens = take_token(tokens)
    exp,tokens=parse_exp(tokens,min_prec=0)
    expect(':',tokens)
    return exp,tokens
    
    
    
    

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
        '?': {'precedence':3, 'associativity': 'RIGHT'},  # Assignment operator
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
    # print(tokens)
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
    elif isIdentifier(next_token) and  not isKeyword(next_token) and tokens[1]=='(':
        # print('inside func')
        identifier_token, tokens = take_token(tokens)
        identifier = Identifier(name=identifier_token)
        # print(identifier)
        expect('(',tokens)
        # print(tokens)
        # if isIdentifier(tokens[0]) and not isKeyword(tokens[0]):
        arg_list,tokens=parse_args_list(tokens)
        # print('arg_list')
        # print('Arguments=',arg_list)
        
        
        expect(')',tokens)    
        return FunctionCall(identifier,arg_list),tokens
    
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
        # print(tokens)
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
