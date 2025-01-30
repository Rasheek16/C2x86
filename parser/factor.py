from typing import List
from parser import * 

def parse_factor(tokens: List[str]):
   try:
        print('Parsing Factors',tokens)
        print(tokens[0])
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

        if isIntegerConstant(next_token):
            print('Found integer',tokens[0])
            val=parse_constant(tokens)
            print('Returning integer',val)
    
            return val
        
        
        # 2. If it's one of the unary operators
        elif next_token in ("-", "~", "!",'*','&') or next_token.startswith('&') or next_token.startswith('*'):
            print('Found unary operator',tokens[0])
            # exit()
            
            operator_token, tokens = take_token(tokens)
            operator = parse_unop(operator_token)
            # Parse the sub-expression after the unary operator
            expr, tokens = parse_factor(tokens)
            # print(expr)
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
        
      
        elif next_token == "(":  # Parenthesized expression or Cast
            # parse_factor(tokens)
            _, tokens = take_token(tokens)
            print('Found parenthesized expression',tokens[0])
            if tokens and isSpecifier(tokens[0]):  # Cast expression
                print('Found casting expr')
                specifiers =[]
                while tokens and isSpecifier(tokens[0]):
                    specifier, tokens = take_token(tokens)
                    specifiers.append(specifier)
                cast_type, storage_class = parse_type_and_storage_class(specifiers)  # Get the type for the cast
                if not isinstance(storage_class,Null):
                    raise SyntaxError('a storage class cannot be specified while type conversion')
        
                print('cast_type',cast_type)
                while tokens and tokens[0] == '(':
                    expect('(', tokens)
                # print(tokens[0])
                if tokens and tokens[0] == '*':  # Check for abstract declarator
                    abstract_declarator, tokens = parse_abstract_declarator(tokens)
                    print('abstract_declarator',abstract_declarator)
                    cast_type = process_abstract_declarator(abstract_declarator, cast_type)
                    print('Cast Type',cast_type)
                print(tokens)
                while tokens and tokens[0] == ')':
                    expect(')', tokens)
                # expect(')', tokens)
                cast_expr, tokens = parse_factor(tokens)
                return Cast(target_type=cast_type, exp=cast_expr), tokens

            else:  # Parenthesized expression
                expr, tokens = parse_exp(tokens)
                expect(")", tokens)
                return expr, tokens
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
            raise SyntaxError(f"Expected <int>, <identifier>, '(', or unary operator, got '{next_token}'")
            # raise SyntaxError(f"Expected <int>, <identifier>, '(', or unary operator, got '{next_token}'")

   except SyntaxError as e:
    raise e