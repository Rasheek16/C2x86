# def isIntegerConstant(token):
#     return re.match(r"[0-9]+\b",token)
    

# def isIdentifier(token):
#     # Matches valid C-like identifier (starts with letter or underscore)
#     # and followed by zero or more word characters (letters, digits, underscore)
#     return re.match(r"^[a-zA-Z_]\w*$", token)

# def parse_program(tokens):
#     """
#     <program> ::= <function>
#     """
#     try:
       
#         function_definition, tokens = parse_function_definition(tokens)
        
#         # The grammar says only one function. If there's anything left, it's junk.
#         if tokens:
#             raise SyntaxError("Unexpected tokens after function definition")
        
#         return Program(function_definition)
#     except Exception as e:
#         print(f"Syntax Error: {e}")
#         sys.exit(1)

# def parse_function_definition(tokens):
#     """
#     <function> ::= "int" <identifier> "(" "void" ")" "{" <statement> "}"
#     """
#     try:
#         # Expect "int"
#         expect("int", tokens)
        
#         # Parse <identifier>
#         identifier_token, tokens = take_token(tokens)
#         if not isIdentifier(identifier_token):
#             raise SyntaxError(f"Invalid identifier: {identifier_token}")
#         func_name = Identifier(identifier_token)
#         # Expect "(" "void" ")" 
#         expect("(", tokens)
#         expect("void", tokens)
#         expect(")", tokens)
        
#         # Expect "{" 
#         expect("{", tokens)
        
#         block_item,tokens  = parse_block(tokens)
#         # Parse <statement>
#         statement, tokens = parse_statement(tokens)
#         # print(statement)
        
#         # Expect "}"
#         expect("}", tokens)
        
#         # Return a Function node
#         return Function(func_name, statement), tokens
#     except Exception as e:
#         print(f"Syntax Error in function definition: {e}")
#         sys.exit(1)

# def parse_block(tokens):
#     if isinstance(tokens[0],Statement):
#         return parse_statement(tokens)
#     elif isinstance(tokens[0],declaration):
        
    

# def parse_statement(tokens):
#     """
#     <statement> ::= "return" <exp> ";"
#     """
#     # Expect "return"
#     expect("return", tokens)
    
#     # Parse <exp> with precedence climbing
#     exp_node, tokens = parse_exp(tokens, min_prec=0)
    
#     # Expect ";"
#     expect(";", tokens)
    

#     return Return(exp_node) ,tokens

# def parse_binop(operator_token):
#     if operator_token=='+':
#         return BinaryOperator.ADD
#     elif operator_token=='-':
#         return BinaryOperator.SUBTRACT
#     elif operator_token=='/':
#         return BinaryOperator.DIVIDE
#     elif operator_token=='*':
#         return BinaryOperator.MULTIPLY
#     elif operator_token=='&&':
#         return BinaryOperator.AND
#     elif operator_token=='||':
#         return BinaryOperator.OR
#     elif operator_token=='==':
#         return BinaryOperator.EQUAL
#     elif operator_token=='!=':
#         return BinaryOperator.NOT_EQUAL
#     elif operator_token=='<':
#         return BinaryOperator.LESS_THAN
#     elif operator_token=='<=':
#         return BinaryOperator.LESS_OR_EQUAL
#     elif operator_token=='>':
#         return BinaryOperator.GREATER_THAN
#     elif operator_token=='>=':
#         return BinaryOperator.GREATER_OR_EQUAL
#     elif operator_token=='%':
#         return BinaryOperator.REMAINDER
# def parse_exp(tokens, min_prec=0):
#     """
#     Implements precedence climbing to parse binary expressions.
    
#     <exp> ::= <factor> ( <binop> <exp> )*
#     """
#     # print('inside parse_Exp')
#     left, tokens = parse_factor(tokens)
#     # print(left)
#     while True:
#         if not tokens:
#             break
#         next_token = tokens[0]
#         # Check if the next token is a binary operator
#         # print(next_token)
#         binop_info = parse_binop_info(next_token)
#         if not binop_info:
#             break  # Not a binary operator
        
#         op_prec, op_assoc = binop_info['precedence'], binop_info['associativity']
        
#         if op_prec < min_prec:
#             break
        
#         # Consume the operator
#         operator_token, tokens = take_token(tokens)
        
#         operator = parse_binop(operator_token)
        
#         # Determine the next minimum precedence
#         if op_assoc == 'LEFT':
#             next_min_prec = op_prec + 1
#         else:  # 'RIGHT'
#             next_min_prec = op_prec
        
#         # Parse the right-hand side expression
#         right, tokens = parse_exp(tokens, next_min_prec)
        
#         # Combine left and right into a Binary AST node
#         left = Binary(operator, left, right)
    
#     return left, tokens


# def parse_binop_info(token):
#     """
#     Returns a dictionary with precedence and associativity for a given binary operator token.
#     Returns None if the token is not a recognized binary operator.
    
#     Precedence levels (higher number means higher precedence):
#     - *, /, % : precedence 2, left-associative
#     - +, -    : precedence 1, left-associative
#     """
#     precedence_table = {
#         '*': {'precedence': 50, 'associativity': 'LEFT'},
#         '/': {'precedence': 50,'associativity': 'LEFT'},
#         '%': {'precedence': 50, 'associativity': 'LEFT'},
#         '+': {'precedence': 45, 'associativity': 'LEFT'},
#         '-': {'precedence': 45, 'associativity': 'LEFT'},
#         '<': {'precedence': 35, 'associativity': 'LEFT'},
#         '<=': {'precedence': 35, 'associativity': 'LEFT'},
#         '>': {'precedence': 35, 'associativity': 'LEFT'},
#         '>=': {'precedence': 35, 'associativity': 'LEFT'},
#         '==': {'precedence': 30, 'associativity': 'LEFT'},
#         '!=': {'precedence': 30, 'associativity': 'LEFT'},
#         '&&': {'precedence': 10, 'associativity': 'LEFT'},
#         '||': {'precedence': 5, 'associativity': 'LEFT'},
        
        
        
        
#     }
#     return precedence_table.get(token, None)


# def parse_factor(tokens):
#     """
#     <factor> ::= <int> | <unop> <factor> | "(" <exp> ")"
#     """
#     if not tokens:
#         raise SyntaxError("Unexpected end of input in factor.")
    
#     next_token = tokens[0]
    
#     # 1. If it's an integer literal, parse_int.
#     if isIntegerConstant(next_token):
#         return parse_int(tokens), tokens
    
#     # 2. If it's one of the unary operators
#     elif next_token in ("-","~","!"):
#         operator_token, tokens = take_token(tokens)
#         if operator_token == "-":
#             operator= UnaryOperator.NEGATE
#         elif operator_token =='!':
#             operator=  UnaryOperator.NOT
#         else:
#             operator=  UnaryOperator.COMPLEMENT
            
#         # Parse the sub-expression after the unary operator
#         subexpr, tokens = parse_factor(tokens)
#         return Unary(operator, subexpr), tokens
    
#     # 3. If it's "(" then parse a parenthesized expression: "(" <exp> ")"
#     elif next_token == "(":
#         _,tokens=take_token(tokens)  # Consume "("
#         subexpr, tokens = parse_exp(tokens, min_prec=0)
#         expect(")", tokens)
#         return subexpr, tokens
    
#     else:
#         # If none of the above matches, it's an error for this grammar
#         raise SyntaxError(f"Expected <int>, '(', or unary operator, got '{next_token}'")
    
# def parse_int(tokens):
#     """
#     <int> ::= ? A constant token ?
#     Consumes one token and attempts to parse it as an integer.
#     """
#     token, tokens = take_token(tokens)
   
#     try:
#         value = int(token)
#         return Constant(value)
#     except ValueError:
#         raise SyntaxError(f"Expected an integer, got '{token}'")

# def take_token(tokens):
#     """
#     Utility: pop a token from the list (front).
#     Raises error if list is empty.
#     """
#     if not tokens:
#         raise SyntaxError("Unexpected end of input")
#     token = tokens.pop(0)
#     return token, tokens

# def expect(expected, tokens):
#     """
#     Utility: consume the next token if it matches 'expected'.
#     Otherwise, raise error.
#     """
#     if not tokens:
#         raise SyntaxError(f"Expected '{expected}', but reached end of input")
#     token = tokens.pop(0)
#     if token != expected:
#         raise SyntaxError(f"Expected '{expected}', got '{token}'")