import re
import sys
from typing import List,Tuple
import ast 
from ._ast5 import * 

return_flag = False

def isString(token):
   return re.match(r'^"([^"\\\n]|\\["\'?\\abfnrtv])*"$',token) is not None 

def isKeyword(token):
    '''
    
    '''
    if token in ('int','return','void','int','extern','char','static','signed','unsigned','long','if','else','do','while','for','void','break','continue','double','char'):
        return True 
    return False

def isSpecifier(token):
    if token in ('int','extern','static','long','int','unsigned','signed','char','double','void'):
        return True 
    return False

def isType(token):
    if token in ('int','long','unsigned','signed','double','char','void'):
        return True 
    return False
        

temp_label_counter=1
def get_temp_label():
    global temp_label_counter
    temp_label_counter+=1
    return f'tmp_label.{temp_label_counter}'

def isCharConstant(token):
    return re.match(r"""'(\\[\\'"abfnrtv0]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|[^'\\\n])'""",token) or re.match (r"""'(\\[\\'"?abfnrtv0]|\\x[0-9a-fA-F]{2}|\\[0-7]{1,3}|\\u[0-9a-fA-F]{4}|\\U[0-9a-fA-F]{8}|[^'\\\n])'""",token) is not None

def isIntegerConstant(token: str) -> bool:
    # #(token)
    # #(re.match(r'^\d+(\.\d+)?([eE][+-]?\d+)?$',token) )
    """
    Checks if a token is an integer constant.
    
    Args:
        token (str): The token to check.
    
    Returns:
        bool: True if the token is an integer constant, False otherwise.
    """
    return (re.fullmatch(r"\d+", token) is not None or re.match(r'\b\d+l\b',token) is not None or re.match(r'[0-9]+[1l]\b',token) is not None or re.match(r'[0-9]+[uU]\b',token) is not None or re.match(r'[0-9]+([lL][uU]|[uU][lL])\b',token) is not None 
            or re.match(r'^(\d+\.\d+|\d+\.|\.\d+|\d+)([eE][+-]?\d+)?$',token) is not None) 


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
    try:
        body = parse_declarations(tokens)
        if tokens:
            raise SyntaxError(f"Unexpected tokens after function definition: {tokens}")
        return Program(function_definition=body)
    except Exception as e:
        raise SyntaxError(f"Error parsing program: {e}")

def parse_param_list(tokens)->Tuple[List[Parameter],str]:
    list_params=[]
    next_token = tokens[0]
    
    if next_token =='void':
        specifiers=[]
        while tokens and isSpecifier(tokens[0]):
            specifiers.append(tokens[0])     
            token,tokens=take_token(tokens)
        print('Inside parse param list')
        _type,storage_class=parse_type_and_storage_class(specifiers)
        print('_type',_type)
        print('storage_class',storage_class)
        if not isinstance(storage_class,Null):
            raise SyntaxError('Storage class cannot have specifier.')
        
        next_token=tokens[0]
        print('Next token',next_token)
        if next_token!=')':
            declarator, tokens = parse_declarator(tokens)
        else:
            declarator = Null()
       
            
        if tokens[0] == ")":
            next_token == Null()
            
        list_params.append(Parameter(_type=_type,name=Identifier(next_token),declarator=declarator))
        
        if tokens[0]==')':
            return list_params,tokens
            # exit()
            
       
        while tokens:
            expect(',',tokens)
            next_token=tokens[0]
            # ##next_token)
            if isSpecifier(next_token):
                specifiers=[]
                while tokens and isSpecifier(tokens[0]):
                    specifiers.append(tokens[0])     
                    token,tokens=take_token(tokens)
                _type,storage_class=parse_type_and_storage_class(specifiers)
                next_token=tokens[0]
                if next_token==')':
                    declarator=Null()
                else:
                    declarator, tokens = parse_declarator(tokens)
                next_token=tokens[0]
                
                if tokens[0] == ")":
                    next_token == Null()

                list_params.append(Parameter(_type=_type,name=Identifier(next_token),declarator=declarator))
                if tokens[0] == ")":
                    return list_params,tokens
              
        
        
    elif isSpecifier(next_token):
        specifiers=[]
        while tokens and isSpecifier(tokens[0]):
            specifiers.append(tokens[0])     
            token,tokens=take_token(tokens)
        print('Inside parse param list')
        _type,storage_class=parse_type_and_storage_class(specifiers)
        print('_type',_type)
        print('storage_class',storage_class)
        if not isinstance(storage_class,Null):
            raise SyntaxError('Storage class cannot have specifier.')
        
        next_token=tokens[0]
        print('Next token',next_token)
       
     
        declarator, tokens = parse_declarator(tokens)
        
        next_token=tokens[0]
        print(declarator)
        list_params.append(Parameter(_type=_type,name=Identifier(next_token),declarator=declarator))
        print(list_params)
        # print(tokens)
        # exit()
        if tokens[0] == ")":
                return list_params,tokens
        print(tokens)
        
        while tokens:
            expect(',',tokens)
            next_token=tokens[0]
            # ##next_token)
            if isSpecifier(next_token):
                specifiers=[]
                while tokens and isSpecifier(tokens[0]):
                    specifiers.append(tokens[0])     
                    token,tokens=take_token(tokens)
                _type,storage_class=parse_type_and_storage_class(specifiers)
                next_token=tokens[0]
              
                declarator, tokens = parse_declarator(tokens)
                next_token=tokens[0]
                
                list_params.append(Parameter(_type=_type,name=Identifier(next_token),declarator=declarator))
            
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
        #(tokens)
        arg_body.append(block)
        #(arg_body)
    
    return arg_body,tokens
    

def parse_declarator(tokens: List[str]) -> Tuple[Declarator, List[str]]:
    """
    Parses a declarator.
    <declarator>::= "*" <declarator> | <direct-declarator>
    """
    print('Inside parse declarator',tokens[0])
    if tokens[0] == "*":
        print('Found pointer decl')
        _, tokens = take_token(tokens)
        inner_declarator, tokens = parse_declarator(tokens)
        print('Inner declarator',inner_declarator)
        print('Returning pointer decl')
        return PointerDeclarator(inner_declarator), tokens
    else:
        return parse_direct_declarator(tokens)

def parse_direct_declarator(tokens: List[str]) -> Tuple[Declarator, List[str]]:
    """
    Parses a direct declarator.
    <direct-declarator>::= <simple-declarator> [ <param-list> ]
    """
    print('Inside parse direct decl',tokens[0])
    simple_declarator, tokens = parse_simple_declarator(tokens)
    print('Simple declaration',simple_declarator)
    print(tokens[0])
    print('called fromhere')
    
    return parse_declarator_suffix(tokens,simple_declarator)

import codecs 
def safe_decode(s):
    # Temporarily replace \" with a unique placeholder
    s = s.replace(r'\"', '__ESCAPED_QUOTE__')
    s=s.replace(r'\\','__DOUBLE_ESCAPE__')
    # Decode escape sequences
    s = codecs.decode(s, 'unicode_escape')
    # Restore the escaped quotes
    s = s.replace('__ESCAPED_QUOTE__', r'\"')
    s=s.replace('__DOUBLE_ESCAPE__',r'\\')
    return s

def parse_initializer(tokens,list=None):
    l=[]
    if tokens[0]=='{':
        print('here')
        expect('{',tokens)
        expr,tokens=parse_initializer(tokens,l)
        l.append(expr)
        print('Parsed index 0')
        while tokens and (tokens[0]==',' and tokens[1]!='}'):
            expect(',',tokens)
            exp,tokens=parse_initializer(tokens,l)
            l.append(exp)
        if tokens[0]==',':
            expect(',',tokens)
        expect('}',tokens)
        return CompoundInit(l) ,tokens
    else:
        print('Found expr',tokens[0])
        exp, tokens = parse_exp(tokens)
        print(exp)
        print('NEXT TOKENS',tokens[0])
        
        if isinstance(exp,String):  # Check if the next token is also a string
         
            if exp.string.startswith('"'):
                    exp.string = exp.string
           
            import codecs
            match = re.search(r'"((?:\\.|[^"\\])*)"', exp.string)
            if match:
                # exit()
                c_str = match.group(1)  
                print("Raw captured:", repr(c_str))

                # Now decode using unicode_escape
                decoded = decoded = safe_decode(c_str)
                exp.string = decoded
                # print("Decoded:", repr(decoded))
                print("Ordinals:", [ord(c) for c in decoded])
          
                lis = [decoded] # Start with first parsed string
            
            else:
                lis = [exp.string]
                
           
     
            while tokens and isString(tokens[0]) and not isIdentifier(tokens[0]) and not isKeyword(tokens[0]):  # Keep merging adjacent strings
                expr_new, tokens = parse_exp(tokens)  # Parse next part
                import codecs
                match = re.search(r'"((?:\\.|[^"\\])*)"', expr_new.string)
                if match:
                
                    c_str = match.group(1)  
                    print("Raw captured:", repr(c_str))

                    # Now decode using unicode_escape
                    decoded = decoded = safe_decode(c_str)
                    exp.string = decoded

                  
                if expr_new.string.startswith('"'):
                    expr_new.string = expr_new.string[1:-1]
                lis.append(expr_new.string)  # Append string content
            exp.string = ''.join(lis)
            print(exp.string)
            # exit()
  
            
        print('exp,',exp)
        return SingleInit(exp),tokens

def parse_declarator_suffix(tokens, simple_declarator):
    """
    Parses the suffix of a declarator, handling function and array declarators.
    
    For an array declaration like [5][10], the first bracket (5) becomes nested 
    (i.e. applied to the simple_declarator), and then the next bracket (10) wraps it.
    
    Returns:
        A tuple (declarator, remaining_tokens)
    """
    if tokens and tokens[0] == '(':
        expect('(', tokens)
        print('Parsing parameter list')
        params, tokens = parse_param_list(tokens)
        print('Param List:', params)
        expect(')', tokens)
        print('Exiting parse direct decl')
        # exit()
        return FunDeclarator(params, simple_declarator), tokens

    elif tokens and tokens[0] == '[':
        expect('[', tokens)
        cont, tokens = parse_constant(tokens)
        if isinstance(cont.value, ConstDouble):
            raise ValueError('Expression must have integral type.')
        expect(']', tokens)
        # Build the current array declarator level:
        current = ArrayDeclarator(simple_declarator, cont)
        # If there's another '[' following, recursively process it using the current declarator.
        if tokens and tokens[0] == '[':
            return parse_declarator_suffix(tokens, current)
        else:
            return current, tokens

    else:
        return simple_declarator, tokens


def parse_simple_declarator(tokens: List[str]) -> Tuple[Declarator, List[str]]:
    """
    Parses a simple declarator.
    <simple-declarator>::= <identifier> | "(" <declarator> ")"
    """
    print('Inside parse simple decl',tokens[0])
    if isIdentifier(tokens[0]) and not isKeyword(tokens[0]) :
        identifier_token, tokens = take_token(tokens)
        return Ident(Identifier(identifier_token)), tokens
    elif tokens[0] == '(':
        expect('(', tokens)
        declarator, tokens = parse_declarator(tokens)
        expect(')', tokens)
        
        return declarator, tokens
    else:
        raise SyntaxError(f"Expected identifier or '(', got '{tokens}'")

def process_declarator(declarator: Declarator, base_type: Type) -> Tuple[Identifier, Type, List[Identifier]]:
    print('Inside process declarator',declarator)
    """
    Processes a declarator to derive type and identifier information.
    """
    if isinstance(declarator, Ident):
        print('Exist process declarator , Ident')
        return declarator.identifier, base_type,[]
    
    elif isinstance(declarator, PointerDeclarator):
        derived_type = Pointer(base_type)
        print('Exist process declarator Pointer decl')
        return process_declarator(declarator.declarator, derived_type)
    elif isinstance(declarator, FunDeclarator):
        if not isinstance(declarator.declarator, Ident):
            raise SyntaxError("Can't apply additional type derivations to a function type")
        param_names =[]
        param_types =[]
        for param_info in declarator.params:
            print(param_info)
            param_name, param_type, _ = process_declarator(param_info.declarator, param_info._type)
            if isinstance(param_type, FunType):
                raise SyntaxError("Function pointers in parameters aren't supported")
            param_names.append(Parameter(_type=param_type,declarator=declarator.declarator,name=Identifier(param_name)))
            param_types.append(param_type)
        derived_type = FunType(param_count=len(param_names),params=param_types,base_type=base_type)
        print(derived_type)
        print('Exist process declarator')
        
        return declarator.declarator.identifier, derived_type, param_names
    elif isinstance(declarator,ArrayDeclarator):
        print(declarator)
        # exit()
        print('HERE')
        print('Base type',base_type)
        derived_type = Array(base_type,declarator.size)
        print('Derived type',derived_type)
        print('Sub declarator',declarator.declarator)
        print(process_declarator(declarator.declarator,derived_type))
        # exit()
        
        return process_declarator(declarator.declarator,derived_type)
    elif isinstance(declarator,Null):
        return Null(),Void(),[]
    else:
        print(declarator)
        raise ValueError(f"Unknown declarator type: {type(declarator)}")

def parse_abstract_declarator(tokens: List[str]) -> Tuple[AbstractDeclarator, List[str]]:
   
    """
    Parses an abstract declarator.
    <abstract-declarator>::= "*" [ <abstract-declarator> ] | <direct-abstract-declarator>
    """
    print('Inside parse absytacy declarator')
    if tokens[0] == "*":
        print('Inside parse abstract declaration',tokens[0])
        if tokens[0]=='*' or tokens[0]==')':
            _, tokens = take_token(tokens)
     
        if tokens and tokens[0] in ("*", "(",'['):  # Check for inner declarator
            inner_declarator, tokens = parse_abstract_declarator(tokens)
            
            
            return AbstractPointer(inner_declarator), tokens
        
        else:
           
            return AbstractPointer(AbstractBase()), tokens  # No inner declarator
    else:
      
        return parse_direct_abstract_declarator(tokens)


def parse_direct_abstract_declarator(tokens: List[str]) -> Tuple[AbstractDeclarator, List[str]]:
   
    if not tokens:
        return AbstractBase(), tokens  # Handle empty case

    if tokens[0] == '(':
        print('here')
    
        expect('(', tokens)
        abstract_declarator, tokens = parse_abstract_declarator(tokens)
        print(abstract_declarator)
   
        expect(')', tokens)
        
        base_type=None
        while tokens and tokens[0] == '[':
            expect('[', tokens)
            const,tokens = parse_constant(tokens)
            # print(const)
            # exit()
            if isinstance(const.value,ConstDouble):
                raise ValueError('Expression must have integral type.')
            expect(']', tokens)
            if base_type is None:
                base_type = AbstractBase() #if there is no base type set it to constant
            base_type = AbstractArray(base_type, const)  # Create AbstractArray
        if base_type is None: #if there are no array brackets
            return abstract_declarator, tokens
        return base_type, tokens
    
    else:
        base_type: AbstractDeclarator = None #store the base type
        while tokens and tokens[0] == '[':
            expect('[', tokens)
            const,tokens = parse_constant(tokens)
            if isinstance(const.value,ConstDouble):
                raise ValueError('Expression must have integral type.')
            # exit()
            expect(']', tokens)
            if base_type is None:
                base_type = AbstractBase() #if there is no base type set it to constant
            base_type = AbstractArray(base_type, const)  # Create AbstractArray
        if base_type is None: #if there are no array brackets
            print('returning')
            return AbstractBase(),tokens #return base type if there is no array
       
        return base_type, tokens
        

def process_abstract_declarator(abstract_declarator: AbstractDeclarator, base_type: Type) -> Type:
    """
    Processes an abstract declarator to derive a type.
    """
    if isinstance(abstract_declarator, AbstractBase):
        return base_type
    elif isinstance(abstract_declarator, AbstractPointer):
        derived_type = Pointer(base_type)
        return process_abstract_declarator(abstract_declarator.abstract_declarator, derived_type)
    elif isinstance(abstract_declarator,AbstractArray):
        derived_type=Array(base_type,abstract_declarator.size)
        return process_abstract_declarator(abstract_declarator.abstract_declarator,derived_type)
    else:
        raise ValueError(f"Unknown abstract declarator type: {type(abstract_declarator)}")

  
def parse_declarations(tokens):
    try:
        body=[]
        # Expect "int" keyword
        while tokens:
        # Expect "{" to start the function body
            # ##tokens)
            # #(tokens)
            sub,tokens = parse_declaration(tokens)
            # #(sub)
            body.append(sub)
        # Return the Function AST node
        return body
    except Exception as e:
        raise e
        # sys.exit(1)


def parse_block(tokens)->Tuple[List[BlockItem],str]:
    print('inside block')
    expect("{", tokens)
    # #('block')
        # Parse zero or more block-items until "}"
    function_body = []
        #* { <block-item> } Curly braces indicate code repetition
    while tokens and tokens[0] != "}":
        block = parse_block_item(tokens)

        if block:  # Append only if valid
            function_body.append(block)
        
    expect("}", tokens)
    # ##function_body)
    
    # ##function_body)
    return function_body,tokens
    

def parse_block_item(tokens):
    print('parse block item',tokens[0])
    if tokens[0] in ('int','static','extern','long','unsigned','signed','double','char','void'):
        declaration,tokens = parse_declaration(tokens)
        ##'declaration')
        block_item = D(declaration)
       
        return block_item
    else:
   
        statement = parse_statement(tokens)
    
        block_item = S(statement)
        return block_item
        

def parse_specifier(tokens):
    if isSpecifier(tokens[0]):
        specifer,tokens=take_token(tokens)
        return specifer,tokens
    else:
        raise  SyntaxError('Unknown Specifier',tokens[0])
    
    
def parse_types(types):
   try:
        
        if len(types)==0:
            raise SyntaxError('No type specifier')
        sorted_types=sorted(types)
        for i in range(len(sorted_types)-1):
            if sorted_types[i]==sorted_types[i+1]:
                raise SyntaxError('Duplicate type specifier')
        if types == ['double']:
            return Double() 
        if 'void' in types:
            # print('void in types',len(types))
            if len(types)>1:
                raise SyntaxError('Invalid type specifier combination')
            # print('here')
            return Void()
                
            
        if 'char' in types:
            if 'signed' in types and 'char' in types:
                return SChar()
            if 'unsigned' in types and 'char' in types:
                return UChar()
            if types == ['char']:
                return Char()
            else:
                raise SyntaxError('Invalid type specifier combination with char')
                
        if 'double' in types:
            raise SyntaxError('Invalid type specifier combination with double')
        if 'signed' in types and 'unsigned' in types:
            raise SyntaxError('Invalid type specifier combination with unsigned')
        
        if 'unsigned' in types and 'long' in types:
            return ULong()
        if 'unsigned' in types:
            return UInt()
        if 'long' in types:
            return Long()
        if 'void' in types:
            return Void()
        else:
            return Int()
   except Exception as e:
       raise  SyntaxError('Invalid specifier type combination',e)
    
        
def parse_type_and_storage_class(specifiers:List):
    print('Inside parse type and storage class')
    try:
        types=[]
        storage_classes:List[str]=[]
        for specifier in specifiers:
            if specifier in ('int','long','unsigned','signed','double','char','void'):
                types.append(specifier)
            else:
                storage_classes.append(specifier)
    
       
        print(types)
        # exit()
        _type = parse_types(types)
        print('types')
        # exit()
        # print(storage_class)
        if len(types)==0 or _type==None:
            raise ValueError('Invalid type specifier.')
        if len(storage_classes)>1:
            raise ValueError('Invalid storage classes.')
        if len(storage_classes)==1:
            storage_class = parse_storage_class(storage_classes[0])
        else:
            storage_class=Null()
       
        print(('Exit parse types and storage class'))
        # exit()
        return _type,storage_class
    except Exception as e:
        raise ValueError('Invalid storage types / type',e)

def parse_storage_class(storage_class):
    # ##storage_class)
    if storage_class=='static':
       return Static()
    elif storage_class=='extern':
       return Extern()
    else:
       raise ValueError('Invalid storage class')
    

def parse_declaration(tokens: List[str]):
    """Parses a declaration (variable or function)."""
    print('Tokens',tokens)
    specifiers =[]
    while tokens and isSpecifier(tokens[0]): #checks if token exists and if it is a specifier
        specifier, tokens = take_token(tokens)
        specifiers.append(specifier)
    print('Specifier_list',specifiers)
    base_type, storage_class = parse_type_and_storage_class(specifiers)
    print('Base type',base_type)
    declarator, tokens = parse_declarator(tokens)
    print('declarator',declarator)
    identifier, decl_type, params = process_declarator(declarator, base_type)
    # exit()
    print('decl_type',decl_type)
    print('Tokens',tokens)
    if isinstance(decl_type, FunType):  # Function declaration
        if tokens and tokens[0] == ';': #checks if token exists and if it is;
            _, tokens = take_token(tokens)
            return FunDecl(name=identifier, params=params, fun_type=decl_type, body=Null(), storage_class=storage_class), tokens
        elif tokens and tokens[0] == '{':#checks if token exists and if it is {
            print('Found function body')
            print(params)
            # exit()
            list_block_items, tokens = parse_block(tokens)
            return FunDecl(name=identifier, params=params, fun_type=decl_type, body=Block(list_block_items), storage_class=storage_class), tokens
        else:
            raise SyntaxError(f"Expected ';' or '{{' after function declarator, got '{tokens if tokens else 'end of input'}'") #more informative error message

    else:  # Variable declaration
        print('Variable declaration')
        init = Null()
        print("Tokens",tokens)
        if tokens and tokens[0] == "=": #checks if token exists and if it is =
            expect("=", tokens)
            print('Found init',tokens)
            init, tokens = parse_initializer(tokens)
            print('INIT',init )
        expect(";", tokens)
        return VarDecl(name=identifier, init=init, var_type=decl_type, storage_class=storage_class), tokens


def parse_func_decl(tokens, func_name: Identifier, _type, storage_class) -> Tuple[FunDecl, List[str]]:
    """Parses a function declaration (including parameters and body)."""
    try:
        expect('(', tokens)
        params, tokens = parse_param_list(tokens)
        expect(')', tokens)

        next_token = tokens if tokens else None  # Look ahead to determine if there's a function body or just a declaration

        if next_token == ';':
            _, tokens = take_token(tokens)
            return FunDecl(name=func_name, params=params, fun_type=_type, body=Null(), storage_class=storage_class), tokens  # Function prototype

        elif next_token == '{':
            print(params)
            # exit()
            body, tokens = parse_block(tokens)
            return FunDecl(name=func_name, params=params, fun_type=_type, body=body, storage_class=storage_class), tokens  # Function definition

        else:
            raise SyntaxError(f"Expected '{{' or ';' after parameter list, got '{next_token if next_token else 'end of input'}'")

    except Exception as e:
        raise SyntaxError(f"Error in parse_func_decl: {e}")


def parse_variable_declaration(tokens: List[str], var_name: Identifier, _type, storage_class) -> Tuple[VarDecl, List[str]]:
    """Parses a variable declaration (with optional initializer)."""

    init = Null()
    if tokens and tokens == "=": #checks if token exists and if it is =
        expect("=", tokens)
        init, tokens = parse_initializer(tokens)

    expect(";", tokens)
    return VarDecl(name=var_name, init=init, var_type=_type, storage_class=storage_class), tokens

def parse_statement(tokens: List[str]) -> Statement:
    print('parse statement',tokens[0])
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
            print('found return ')
            # Parse "return" <exp> ";"
            expect("return", tokens)
            exp_node = Null()
            if tokens[0]!=';':
                exp_node,tokens = parse_exp(tokens)
            expect(";", tokens)
            print('returning return')
            
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
            # print('for statewmnt')
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
            print('before parsestatewment')
            body = parse_statement(tokens)
            print('jere')
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
    # print(tokens)
    if tokens[0] in ('int','extern','static','long','unsigned','signed','double','char','void'):
   
        if tokens[2]=='(':
            raise SyntaxError('Function not permitted in loop headers')
        decl, tokens = parse_declaration(tokens)
        
        # ##
        init_decl = InitDecl(declaration=decl)
    
        return init_decl, tokens
    
    elif isIdentifier(tokens[0]) and not isKeyword(tokens[0]):
      
        if tokens[1]=='(' and not tokens[2]==')':
            raise SyntaxError('Function not permitted in loop headers')
       
        exp, tokens = parse_exp(tokens)
        init_exp = InitExp(exp)
        print('here')
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


def parse_unary_exp(tokens: List[str]) -> Tuple[Exp, List[str]]:
    try:
        
        next_token = tokens[0]
        print('Parsinf unary expre', next_token)
        print(tokens)

        # exit()
        if next_token in ("-", "~", "!", '*', '&') or next_token.startswith('&') or next_token.startswith('*'):
            print('Found unary operator', tokens[0])
            operator_token, tokens = take_token(tokens)
            operator = parse_unop(operator_token)
            # Parse the sub-expression after the unary operator
            expr, tokens = parse_cast_expr(tokens)
            if operator == UnaryOperator.AMPERSAND:
                return AddOf(expr), tokens
            elif operator == UnaryOperator.DEREFERENCE:
                return Dereference(expr), tokens
            return Unary(operator=operator, expr=expr), tokens
        elif next_token == 'sizeof' and tokens[1]=='(' and isType(tokens[2]):
            print('found size of')
            _,tokens=take_token(tokens)
            if tokens and tokens[0] =='(':
                expect('(',tokens)
            _type,tokens=parse_type_name(tokens)
            if tokens and tokens[0] ==')':
                expect(')',tokens)
            print(tokens)
            # exit()
            return SizeOfT(_type),tokens
        elif next_token=='sizeof':
            _,tokens=take_token(tokens)
            exp,tokens=parse_unary_exp(tokens)    
            return SizeOf(exp),tokens
        else:
            print('Found postfix expr')
            expr, tokens = parse_postfix_expr(tokens)
            print('POstfix expr', expr)
            print(expr)
            return expr, tokens
    except Exception as e:
        raise e
     
def parse_postfix_expr(tokens):
    print('Inside parse posftfix expr',tokens[0])
    expr=Null()
    if tokens[0]=='[':
        expr,tokens=parse_primary_expr(tokens)
    else:
        print('Going to parse primary expr')
        expr,tokens=parse_primary_expr(tokens)
        

        while tokens and tokens[0] == '[':  
            print('Subscript')
            expect('[', tokens)
            exp, tokens = parse_exp(tokens)
        
            expr = Subscript(expr, exp)
            
            expect(']', tokens)
 
    return expr,tokens
   
def parse_primary_expr(tokens):
    print('inside parse primary expr',tokens[0])
    print('Is identifier ',isIdentifier(tokens[0]))
    print('Is char constant ',isCharConstant(tokens[0]))
    print(tokens[0])
    # exit()
    if not tokens:
            raise SyntaxError("Unexpected end of input when parsing factor.")
        
    next_token = tokens[0]
  
    if next_token=='(':
        expect('(',tokens)
        expr,tokens=parse_exp(tokens)
        expect(')',tokens)
        return expr,tokens
    
    if isIdentifier(next_token) and tokens[1]=='(':
        token,tokens=take_token(tokens)
        ident=Identifier(token)
        expect('(',tokens)
        args=[]
        if tokens[0] != ')':
            args,tokens=parse_args_list(tokens)
        expect(')',tokens)
        return FunctionCall(identifier=ident,args=args),tokens
    
    if isIntegerConstant(next_token) or isCharConstant(next_token):
        print('Found integer',tokens[0])
        val,tokens=parse_constant(tokens)
        print('Returning integer',val)
        return val,tokens
        
    if isIdentifier(next_token) and not isKeyword(next_token):
        print('here')
        token,tokens=take_token(tokens)
        return Var(Identifier(token)),tokens
    
    if isString(next_token) and not isKeyword(next_token):
        print('Found string')
        token,tokens = take_token(tokens)
        print('Returning string')
        return String(token),tokens
    else:
        raise SyntaxError('Invalid token in primary expression',tokens[0])

def parse_exp(tokens: List[str], min_prec: int = 0) -> Tuple[Exp,List[str]]:
    print('parse expr')
    
    
    #(
        # 'Inside parse expression'
    # )
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

        # if tokens[0] in (UnaryOperator.NEGATE,UnaryOperator.NOT,UnaryOperator.DEREFERENCE,UnaryOperator.AMPERSAND,UnaryOperator.COMPLEMENT):
       
        # lhs,tokens = parse_unary_exp(tokens)
        
        #! MAJOR MODIFICATION 
        lhs , tokens = parse_cast_expr(tokens)
        
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
            # Determine the next minimum precedence based on associativity
            if assoc == 'LEFT':
                next_min_prec = prec + 1
            else:  # 'RIGHT'
                next_min_prec = prec
            next_token = tokens[0]
        
            if next_token =='=':
           
                _,tokens = take_token(tokens)
                right,tokens = parse_exp(tokens,next_min_prec)
                
                lhs = Assignment(lhs,right)
            elif next_token =='?':
                middle,tokens = parse_conditional_middle(tokens)
                right,token = parse_exp(tokens,next_min_prec)
                lhs  = Conditional(condition=lhs,exp2=middle,exp3=right)
            else:
               
                token,tokens = take_token(tokens)
                operator = parse_binop(token)
              
                # Parse the right-hand side (rhs) expression
                rhs, tokens = parse_exp(tokens, next_min_prec)
                
                # Combine lhs and rhs into a Binary AST node
                lhs = Binary(operator=operator, left=lhs, right=rhs)
        print('Exist parse exp',tokens)
        print(lhs)
        return lhs, tokens
    except Exception as e:
        # sys.exit(1)
        raise e

def parse_cast_expr(tokens:List[str])->Tuple[Exp,List[str]]:
    print('parse cast expr',tokens[0])
    print('next token',tokens[1])
    print('is specifier',isSpecifier(tokens[1]))
    next_token=tokens[0]
  
    if next_token=='(' and isSpecifier(tokens[1]):
        print('found cast')
        expect('(',tokens)
        # print('tokens',tokens[1])
        print('before typename')
        print(tokens)
        _type,tokens=parse_type_name(tokens)
        print('after typename')
        print(tokens)
        # if tokens[0]==')':
        expect(')',tokens)
        exp,tokens=parse_cast_expr(tokens)
        return Cast(target_type=_type,exp=exp),tokens
    else:
        print('found unary')
        return parse_unary_exp(tokens)

def parse_type_name(tokens:List[str]):
    
    next_token=tokens[0]
   
  
    
    types=[]
    while next_token and isSpecifier(next_token) and isType(next_token):
        print('inside while loop')
        types.append(next_token)
        _,tokens=take_token(tokens)
        next_token=tokens[0]
    print(types)
    _type=Null()
    storage_class = Null()
    if len(types)>0:
        _type,storage_class=parse_type_and_storage_class(types)
  
 
    if tokens[0] in ('*','(','['):
        while tokens and tokens[0] == '(' and tokens[1] == '(':
                expect('(', tokens)
      
        if not isinstance(storage_class, Null):
            raise SyntaxError('a storage class cannot be specified while type conversion')
        print('going into parse abs decl')
        abstract_declarator,tokens=parse_abstract_declarator(tokens)
        print('after decl')
        if tokens[0] == ')' and tokens[1]==')':
           
            expect(')', tokens)
        print('process decalrator')
        _type=process_abstract_declarator(abstract_declarator,_type)
        print('after process deccalrator')
        while tokens and tokens[0] == ')' and tokens[1]==")" :
            expect(')', tokens)
    else:
        abstract_declarator=Null()
        
    return _type,tokens
        

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
        '&': UnaryOperator.AMPERSAND,
        '*': UnaryOperator.DEREFERENCE,
    }
    if operator_token not in unop_mapping:
        raise SyntaxError(f"Unknown unary operator: '{operator_token}'")
    return unop_mapping[operator_token]

    
def parse_constant(tokens: List[str]) -> Tuple[Constant, List[str]]:
    print('Inside parse contant',tokens[0])
    """
    Parses a <const> token according to the grammar:
    <const> ::= <int> | <long> | <uint> | <ulong> | <double>
    
    Args:
        tokens (List[str]): The list of tokens to parse.
    
    Returns:
        tuple: A tuple containing the parsed Constant AST node and the remaining tokens.
    
    Raises:
        SyntaxError: If the token is not a valid constant.
    """
    token, tokens = take_token(tokens)

    try:
        value_str = token

        # Define regex patterns for different constant types
        patterns = {
            'ulong': re.compile(r'^(\d+)(?:[uU][lL]|[lL][uU])$'),
            'uint': re.compile(r'^(\d+)[uU]$'),
            'long': re.compile(r'^(\d+)[lL]$'),
            'int': re.compile(r'^(\d+)$'),
            'double': re.compile(r'^(\d+\.\d+|\d+\.|\.\d+|\d+)([eE][+-]?\d+)?$'),
            'char': re.compile(
                r"^'("
                r"[^'\\\n]"               # Any single character except `'`, `\`, newline
                r"|\\[\\'\"abfnrtv?]"     # Standard escape sequences (note the ? is now at end)
                r"|\\x[0-9A-Fa-f]{2}"     # Hex escape: '\x41'
                r"|\\[0-7]{1,3}"          # Octal escape: '\123'
                r"|\\u[0-9A-Fa-f]{4}"     # Unicode escape: '\u00A9'
                r"|\\U[0-9A-Fa-f]{8}"     # Unicode escape: '\U0001F600'
                r")'$"
            )
        }
        # #(token)

        # 1. Check for 'double'
        match = patterns['char'].match(value_str)
        
        if match:
            
            char_repr = match.group(1)  # Extract character content
          
            if char_repr == r'\?':
                ascii_value = ord('?')  # ASCII 63
            else:
                char = char_repr.encode().decode('unicode_escape')
                ascii_value = ord(char)
            # print(char_repr)
            # char = char_repr.encode().decode('unicode_escape')  # Decode escape sequences
            # print(char)
            # ascii_value = ord(char)  # Convert character to ASCII / Unicode value
            # print(r"\\ascii_value")

            # print(f"Character: {char}, ASCII/Unicode: {ascii_value}")
            ret =  Constant(Const.constInt(ascii_value)),tokens 
            return ret # Return processed character constant
        
          
        match = patterns['ulong'].fullmatch(value_str)
        if match:
            number = int(match.group(1))
            if number > 2**64 - 1:
                raise ValueError('Constant is too large to represent as ulong')
            return Constant(Const.constULong(number)), tokens

        # 3. Check for 'uint' with 'u' or 'U' suffix
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

        # 4. Check for 'long' with 'l' or 'L' suffix
        match = patterns['long'].fullmatch(value_str)
        if match:
            number = int(match.group(1))
            if number > 2**63 - 1:
                raise ValueError('Constant is too large to represent as long')
            return Constant(Const.constLong(number)), tokens

        # 5. Check for 'int' without any suffix
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
        match = patterns['double'].fullmatch(value_str)
        #(match)
        if match:
            #('Inside double')
            number = match.group(0)  # Convert to float
            # #( Constant(Const.constDouble(number)), tokens)
            print(number)
            # exit()
            return Constant(Const.constDouble(float(number))), tokens

        # If none of the patterns match, raise a SyntaxError
        raise SyntaxError(f"Expected a constant (int, long, uint, ulong, double), got '{token}'")

    except ValueError as e:
        raise SyntaxError(str(e)) from e
