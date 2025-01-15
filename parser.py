import re
import sys
from typing import List,Tuple

from _ast5 import *

return_flag = False

def isKeyword(token):
    if token in ('int','return','main','void','int','extern','static','signed','unsigned','long','if','else','do','while','for','break','continue'):
        return True 
    return False

def isSpecifier(token):
    if token in ('int','extern','static','long','int','unsigned','signed'):
        return True 
    return False

def isType(token):
    if token in ('int','long','unsigned','signed'):
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
    return (re.fullmatch(r"\d+", token) is not None or re.match(r'\b\d+l\b',token) is not None or re.match(r'[0-9]+[1l]\b',token) is not None or re.match(r'[0-9]+[uU]\b',token) is not None or re.match(r'[0-9]+([lL][uU]|[uU][lL])\b',token) is not None)


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
    # ##tokens)
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
        # print(tokens)
        body = parse_declarations(tokens)
        # print(body)
        
        # The grammar specifies only one function. If there are remaining tokens, it's an error.
        if tokens:
            
            raise SyntaxError("Unexpected tokens after function definition")
        #body)
        return Program(function_definition=body)
    except Exception as e:
        ##f"Syntax Error: {e}")
        sys.exit(1)


def parse_param_list(tokens)->Tuple[List[Parameter],str]:
    list_params=[]
    next_token = tokens[0]
    if next_token=='void':
        _,tokens=take_token(tokens)
        # list_params
        return list_params,tokens
    elif isSpecifier(next_token):
        specifiers=[]
        while tokens and isSpecifier(tokens[0]):
            specifiers.append(tokens[0])     
            token,tokens=take_token(tokens)
        _type,storage_class=parse_type_and_storage_class(specifiers)
        if not isinstance(storage_class,Null):
            raise SyntaxError('Storage class cannot have specifier.')
        # token,tokens=take_token(tokens)
        next_token=tokens[0]
        if isIdentifier(next_token) and not isKeyword(next_token):
            token,tokens =take_token(tokens)
            list_params.append(Parameter(_type,Identifier(token)))
            if tokens[0] == ")":
                return list_params,tokens
        else:
            raise SyntaxError('In parse param list Expected identifier , got',next_token)
        while tokens:
            expect(',',tokens)
            next_token=tokens[0]
            # ##next_token)
            if isSpecifier(next_token):
                specifiers=[]
                ##'here2')
                while tokens and isSpecifier(tokens[0]):
                    specifiers.append(tokens[0])     
                    token,tokens=take_token(tokens)
                _type,storage_class=parse_type_and_storage_class(specifiers)
                next_token=tokens[0]
                if isIdentifier(next_token) and not isKeyword(next_token):
                    token,tokens =take_token(tokens)
                    list_params.append(Parameter(_type,Identifier(next_token)))
                    if tokens[0] == ")":
                        # ##list_params)
                        return list_params,tokens
                    else: 
                        pass 
                else:
                    raise SyntaxError('In parse param Expected identifier , got in loop ',next_token)
            else:
                raise SyntaxError('Unexpected end of input expected an identifier got ',token)
           
                
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
    
        
    

def parse_func_decl(tokens,func_name:Identifier,_type,storage_class)->Tuple[FunDecl,str]:
 try:
    exp=Null()
    expect('(',tokens)
    exp,tokens=parse_param_list(tokens)
    expect(')',tokens)
    next_token  = tokens[0]
    if next_token==';':
        _,tokens=take_token(tokens)
        exp1=FunDecl(name=func_name,params=exp,fun_type=_type,body=Null(),storage_class=storage_class),tokens
        return exp1
    elif next_token=='{':
        list_block_items,tokens=parse_block(tokens)
        # func=FunctionDeclaration(name=func_name,init=exp,body=list_block_items)
      
        return FunDecl(name=func_name,params=exp,fun_type=_type,body=Block(list_block_items),storage_class=storage_class),tokens
 except Exception as e:
    raise SyntaxError('Error in parse_func_decl',e)
        
    
    
def parse_declarations(tokens):
    try:
        body=[]
        # Expect "int" keyword
        while tokens:
        # Expect "{" to start the function body
            # ##tokens)
            # print(tokens)
            sub,tokens = parse_declaration(tokens)
            # print(sub)
            body.append(sub)
        # Return the Function AST node
        return body
    except Exception as e:
        ##f"Syntax Error in function definition: {e}")
        sys.exit(1)




def parse_block(tokens)->Tuple[List[BlockItem],str]:
    expect("{", tokens)
    # print('block')
        # Parse zero or more block-items until "}"
    function_body = []
        #* { <block-item> } Curly braces indicate code repetition
    while tokens and tokens[0] != "}":
        block = parse_block_item(tokens)
        # ##'block:',block)
        if block:  # Append only if valid
            function_body.append(block)
            # ##block)
        # function_body.append(block)
        # Expect "}" to end the function body
        # print(function_body)
        # ##'func',function_body)
        
    expect("}", tokens)
    # ##function_body)
    
    # ##function_body)
    return function_body,tokens
    

def parse_block_item(tokens):
    # token,tokens = take_token(tokens)
    print('Block Item',tokens[0])
    if tokens[0] in ('int','static','extern','long','unsigned','signed'):
        declaration,tokens = parse_declaration(tokens)
        ##'declaration')
        block_item = D(declaration)
       
        return block_item
    else:
        # ##'parse statement')
        # It's a statement
        statement = parse_statement(tokens)
        # ##statement)
        block_item = S(statement)
        return block_item
        
    # block_items.append(block_item)

def parse_variable_declaration(tokens:List[str],var_name:str,_type,storage_class)->Tuple[VarDecl,str]:
    try:
        
        # Initialize 'init' to None (optional initializer)
        init = Null()
        # new_token = 
        # Check if the next token is "=" indicating an initializer
        # * [ "=" <exp> ] Square bracket indicate optional code
        if tokens and tokens[0] == "=":
            # Consume "="
            expect("=", tokens)
            # ##tokens)
            # Parse <exp> for the initializer
            # ##tokens)
            # print(tokens)
            init, tokens = parse_exp(tokens)
            # ##tokens)
        # Expect ";" to end the declaration
        expect(";", tokens)
        # ##tokens)
        # Return the Declaration AST node
        # ##'in var decl')
        return VarDecl(name=var_name, init=init,var_type=_type,storage_class=storage_class),tokens
    except Exception as e:
        ##f"Syntax Error in declaration: {e}")
        sys.exit(1)
    
def parse_specifier(tokens):
    if isSpecifier(tokens[0]):
        specifer,tokens=take_token(tokens)
        return specifer,tokens
    else:
        raise SyntaxError('Unknown Specifier',tokens[0])
    
    
def parse_types(types):
   try:
    if len(types)==0:
        raise SyntaxError('No type specifier')
    sorted_types=sorted(types)
    for i in range(len(sorted_types)-1):
        if sorted_types[i]==sorted_types[i+1]:
            raise SyntaxError('Duplicate type specifier')
    if 'signed' in types and 'unsigned' in types:
        raise SyntaxError('Invalid type specifier combination')
    if 'unsigned' in types and 'long' in types:
        return ULong()
    if 'unsigned' in types:
        return UInt()
    if 'long' in types:
        return Long()
    else:
        return Int()
   except Exception as e:
       raise SyntaxError('Invalid specifier type combination')
    

    
        
def parse_type_and_storage_class(specifiers:List):
    try:
        print('Type and Storage Class')
        types=[]
        storage_classes:List[str]=[]
        for specifier in specifiers:
            if specifier in ('int','long','unsigned','signed'):
                types.append(specifier)
            else:
                storage_classes.append(specifier)
        print('Storage Classes:',storage_classes)
        print('Types:',types)
        
        _type = parse_types(types)
        if len(types)==0:
            raise ValueError('Invalid type specifier.')
        if len(storage_classes)>1:
            raise ValueError('Invalid storage classes.')
        ##specifiers)
        # _type=Int()
        # storage_class=storage_class

        if len(storage_classes)==1:
            # ##'here')
            storage_class = parse_storage_class(storage_classes[0])
            # ##'here')
        else:
            storage_class=Null()
        
        return _type,storage_class

    except Exception as e:
        raise ValueError('Invalid storage types / type')

def parse_storage_class(storage_class):
    # ##storage_class)
    if storage_class=='static':
       return Static()
    elif storage_class=='extern':
       return Extern()
    else:
       raise ValueError('Invalid storage class')
    

def parse_declaration(tokens: List[str]):
    print('Declaration')
    # print(tokens)
    # Expect "int" keyword
    specifiers=[]
    while isSpecifier(tokens[0]):
        # ##tokens[0])
        specifier,tokens=parse_specifier(tokens)
        specifiers.append(specifier)
    print('Specifiers:',specifiers)
    _type,storage_class= parse_type_and_storage_class(specifiers)
    print('Type:',_type)
    print('Storage Class:',storage_class)
    identifier_token, tokens = take_token(tokens)
    # print(identifier_token)
    # ##identifier_token)
    print('Identifier:',identifier_token)
    if not isIdentifier(identifier_token):
        raise SyntaxError(f"Invalid identifier in parse declaration: '{identifier_token}'")
    var_name = Identifier(identifier_token)
    func_name = Identifier(identifier_token)
    # func_name =
    next_token= tokens[0]
    # print(next_token)
    if next_token =='(':
        print('func declaration')
        
        # ##'here in func decl')
        func_decl,tokens=parse_func_decl(tokens,func_name,_type,storage_class)
        return func_decl,tokens
    elif next_token in ('=',';'):
        print('variable declaration')
        # ##next_token)
        var_dec,tokens = parse_variable_declaration(tokens,var_name,_type=_type,storage_class=storage_class)
        # print(var_dec)
        # ##var_dec)
        return var_dec,tokens
    else:
        # ##'inside decleration',tokens)
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
    ##tokens[0])
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
            ##'in stmt')
            
            # ##'inside if')
            token,tokens=take_token(tokens)
            expect('(',tokens)
            exp_node,tokens = parse_exp(tokens)
            expect(')',tokens)
            statement = parse_statement(tokens)
            # ##statement)
            # ##statement)
            # ##tokens[0])
            # el_statement=None
            if tokens and tokens[0]=='else':
                token,tokens=take_token(tokens)
                el_statement =parse_statement(tokens)
                return If(exp=exp_node,then=statement,_else = el_statement)
                # el_statement=parse_statement(['return','0',';'])
            return If(exp=exp_node,then=statement,_else=Null())
            # ##'outside if')
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
            # ##'here')
            _,tokens=take_token(tokens)
           
            statement=parse_statement(tokens)
            # ##statement)
            expect('while',tokens)
            expect('(',tokens)
            exp,tokens=parse_exp(tokens)
            # ##exp)
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
                ##init)
                expect(";", tokens)
            
            # Parse condition
            condition, tokens = parse_optional_parameter(tokens)
            
            # Expect and consume second semicolon
            expect(";", tokens)
            
            # Parse post-expression
            post, tokens = parse_optional_parameter(tokens)
            
            # Expect closing parenthesis
            expect(")", tokens)
            # ##tokens)
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
        ##f"Syntax Error in statement: {e}")
        sys.exit(1)

def parse_for_init(tokens: List[str]) -> Tuple[Statement, List[str]]:
    """
    Parses the initialization part of a for loop.

    Args:
        tokens (List[str]): The list of tokens to parse.

    Returns:
        Tuple[Statement, List[str]]: The initialization statement and the remaining tokens.
    """
  
    if tokens[0] in ('int','extern','static','long','unsigned','signed'):
        # ##'here')
        # Parse declaration (e.g., int i = 0)
        if tokens[2]=='(':
            raise SyntaxError('Function not permitted in loop headers')
        decl, tokens = parse_declaration(tokens)
        # #print
        init_decl = InitDecl(declaration=decl)
        # ##init_decl)
        return init_decl, tokens
    
    elif isIdentifier(tokens[0]) and not isKeyword(tokens[0]):
        if tokens[1]=='(':
            raise SyntaxError('Function not permitted in loop headers')
        # Parse expression (e.g., i = 0)
        exp, tokens = parse_exp(tokens)
        init_exp = InitExp(exp)
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
        # ##'exp',tokens[0])
        # print(tokens)
        lhs, tokens = parse_factor(tokens)
        print('lhs:',lhs)
        print('tokens:',tokens)
        # ##)
        # ##tokens)
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
            # ##operator_token)
            # operator = parse_binop(operator_token)
            
            # Determine the next minimum precedence based on associativity
            if assoc == 'LEFT':
                next_min_prec = prec + 1
            else:  # 'RIGHT'
                next_min_prec = prec
            next_token = tokens[0]
            # ##tokens)
            if next_token =='=':
                # ##'found assignment')
                _,tokens = take_token(tokens)
                right,tokens = parse_exp(tokens,next_min_prec)
                # ##right)
                lhs = Assignment(lhs,right)
            elif next_token =='?':
                middle,tokens = parse_conditional_middle(tokens)
                right,token = parse_exp(tokens,next_min_prec)
                lhs  = Conditional(condition=lhs,exp2=middle,exp3=right)
            else:
                # ##'not assignent')
                token,tokens = take_token(tokens)
                operator = parse_binop(token)
                # ##'Parsed operator')
                # Parse the right-hand side (rhs) expression
                rhs, tokens = parse_exp(tokens, next_min_prec)
                
                # Combine lhs and rhs into a Binary AST node
                lhs = Binary(operator=operator, left=lhs, right=rhs)
                
        return lhs, tokens
    except Exception as e:
        ##f"Syntax Error in expression: {e}")
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
    # ##tokens)
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
    # ##next_token)
    # ##next_token)
    # 1. If it's an integer literal, parse_int.
    if isIntegerConstant(next_token):
        
            # ##'heresa')
        # vals=parse_constant
        val=parse_constant(tokens)
        print('value',val)
        return val
    
    # 2. If it's one of the unary operators
    elif next_token in ("-", "~", "!"):
        operator_token, tokens = take_token(tokens)
        operator = parse_unop(operator_token)
        # Parse the sub-expression after the unary operator
        expr, tokens = parse_factor(tokens)
        return Unary(operator=operator, expr=expr), tokens
    elif isIdentifier(next_token) and  not isKeyword(next_token) and tokens[1]=='(':
        # ##'inside func')
        identifier_token, tokens = take_token(tokens)
        identifier = Identifier(name=identifier_token)
        # ##identifier)
        expect('(',tokens)
    
        arg_list,tokens=parse_args_list(tokens)
    
        
        expect(')',tokens)    
        return FunctionCall(identifier,arg_list),tokens
    
    elif next_token[0]=='(' and isSpecifier(tokens[1]):
        expect('(',tokens)
        specifiers=[]
        while tokens and isSpecifier(tokens[0]):
            specifiers.append(tokens[0])
            _,tokens=take_token(tokens)
            
        # _type,storage_class=parse_type_and_storage_class(specifiers)
        cast_type, storage_class = parse_type_and_storage_class(specifiers)
        if not isinstance(storage_class,Null):
            raise SyntaxError('a storage class cannot be specified while type conversion')
            
            
        expect(')',tokens)
        cast_expr, tokens = parse_factor(tokens)
        
        return Cast(target_type=cast_type,exp=cast_expr),tokens
            
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
        # ##tokens)
        # If none of the above matches, it's an error for this grammar
        raise SyntaxError(f"Expected <int>, <identifier>, '(', or unary operator, got '{next_token}'")


# def parse_constant(tokens: List[str]):
#     """
#     Parses an <int> ::= ? A constant token ? rule.
    
#     Args:
#         tokens (List[str]): The list of tokens to parse.
    
#     Returns:
#         tuple: A tuple containing the parsed Constant AST node and the remaining tokens.
    
#     Raises:
#         SyntaxError: If the token is not a valid integer.
#     """
#     token, tokens = take_token(tokens)
#     ##token)
#     try:
#         value=token
#         print('value:',value)
#         ##value)
#         if re.match(r'[0-9]+([lL][uU]|[uU][lL] [ul][uL] )\b',value) is not None:
#             return Constant(Const.constULong(value))
#         elif  2**31-1<=int(value) < 2**31-1:
#                 return Constant(Const.constInt(value))
#         elif  -2**62-1<=int(value)<=2**63-1:
#             return Constant(Const.constLong(value))
#         elif value.endswith('l'):
#             return Constant(Const.constLong(value.replace('l','')))
#         elif value.endswith('U') or value.endswith('u'):
#             if  0<=int(value) < 2**32-1:
#                 return Constant(Const.constUInt(value.replace('u','').replace('U','')))
#             elif 0<=int(value)<= 2**64-1:
#                 # return Constant(Const.constULong(value))
#                 return Constant(Const.constULong(value.replace('u','').replace('U','')))
#         else:
#             raise ValueError('Constant is too large to represent as an int or long')
#             value=int(value)
            
            
#         # # value = Loj(token,base=10)
#         # if value>2**63 -1:
        
#         # if isinstance(value,int) and -2**31-1<=value <=2**31-1:
#         #     return Constant(Const.constInt(value))
#         # elif isinstance(value,int) and -2**63-1<=value <0:
#         #     return Constant(Const.constLong(value))
#         # elif isinstance(value,int) and 0<=value <= 2**63-1:
#         #     return Constant(Const.constULong(value))
#         # return Constant(Const.constLong(value))
#         # # return Constant(value=value), tokens
#     except ValueError:
#         raise SyntaxError(f"Expected an integer, got '{token}'")
def parse_constant(tokens: List[str]) -> Tuple[Constant, List[str]]:
    """
    Parses a <const> token according to the grammar:
    <const> ::= <int> | <long> | <uint> | <ulong>
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        tuple: A tuple containing the parsed Constant AST node and the remaining tokens.
    
    Raises:
        SyntaxError: If the token is not a valid constant.
    """
    token, tokens = take_token(tokens)
    print('value:', token)
    try:
        value_str = token

        # Define regex patterns for different constant types
        patterns = {
            'ulong': re.compile(r'^(\d+)(?:[uU][lL]|[lL][uU])$'),  # e.g., 123UL, 456Lu
            'uint': re.compile(r'^(\d+)[uU]$'),                 # e.g., 789U, 101u
            'long': re.compile(r'^(\d+)[lL]$'),                 # e.g., 1123L, 1314l
            'int': re.compile(r'^(\d+)$'),                      # e.g., 15, 1617
        }

        # 1. Check for 'ulong' with 'ul' or 'lu' suffix
        match = patterns['ulong'].fullmatch(value_str)
        if match:
            number = int(match.group(1))
            if number > 2**64 - 1:
                raise ValueError('Constant is too large to represent as ulong')
            return Constant(Const.constULong(number)), tokens

        # 2. Check for 'uint' with 'u' or 'U' suffix
        match = patterns['uint'].fullmatch(value_str)
        if match:
            number = int(match.group(1))
            if number <= 2**32 - 1:
                return Constant(Const.constUInt(number)), tokens
            elif number <= 2**64 - 1:
                # If 'u' suffix but value exceeds 'uint', treat as 'ulong'
                return Constant(Const.constULong(number)), tokens
            else:
                raise ValueError('Constant is too large to represent as uint or ulong')

        # 3. Check for 'long' with 'l' or 'L' suffix
        match = patterns['long'].fullmatch(value_str)
        if match:
            number = int(match.group(1))
            if number > 2**63 - 1:
                raise ValueError('Constant is too large to represent as long')
            return Constant(Const.constLong(number)), tokens

        # 4. Check for 'int' without any suffix
        match = patterns['int'].fullmatch(value_str)
        if match:
            number = int(match.group(1))
            if number <= 2**31 - 1:
                return Constant(Const.constInt(number)), tokens
            elif number <= 2**63 - 1:
                # If no suffix but value exceeds 'int', treat as 'long'
                return Constant(Const.constLong(number)), tokens
            else:
                raise ValueError('Constant is too large to represent as int or long')

        # If none of the patterns match, raise a SyntaxError
        raise SyntaxError(f"Expected a constant (int, long, uint, ulong), got '{token}'")

    except ValueError as e:
        raise SyntaxError(str(e))