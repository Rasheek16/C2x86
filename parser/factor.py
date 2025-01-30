from parser import * 

def parse_factor(tokens: List[str]):
    try:
        if not tokens:
            raise SyntaxError("Unexpected end of input when parsing factor.")
        
        next_token = tokens[0]

        if isIntegerConstant(next_token):
            return parse_constant(tokens)
        elif next_token in ("-", "~", "!", '*', '&') or next_token.startswith('&') or next_token.startswith('*'):
            if next_token.startswith('&'):
                operator = parse_unop('&')
                if len(tokens[0]) > 1:
                    tokens[0] = tokens[0][1:]
                else:
                    _, tokens = take_token(tokens)
            elif next_token.startswith('*'):
                operator = parse_unop('*')
                if len(tokens[0]) > 1:
                    tokens[0] = tokens[0][1:]
                else:
                    _, tokens = take_token(tokens)
            else:
                operator_token, tokens = take_token(tokens)
                operator = parse_unop(operator_token)
            expr, tokens = parse_factor(tokens)
            return Unary(operator=operator, expr=expr), tokens
        elif isIdentifier(next_token) and not isKeyword(next_token) and tokens[1] == '(':
            identifier_token, tokens = take_token(tokens)
            identifier = Identifier(name=identifier_token)
            expect('(', tokens)
            arg_list, tokens = parse_args_list(tokens)
            expect(')', tokens)
            return FunctionCall(identifier, arg_list), tokens
        elif next_token == "(":
            _, tokens = take_token(tokens)
            if tokens and isSpecifier(tokens[0]):
                specifiers = []
                while tokens and isSpecifier(tokens[0]):
                    specifier, tokens = take_token(tokens)
                    specifiers.append(specifier)
                cast_type, storage_class = parse_type_and_storage_class(specifiers)
                if not isinstance(storage_class, Null):
                    raise SyntaxError('A storage class cannot be specified while type conversion')
                while tokens and tokens[0] == '(':
                    expect('(', tokens)
                if tokens and tokens[0] == '*':
                    abstract_declarator, tokens = parse_abstract_declarator(tokens)
                    cast_type = process_abstract_declarator(abstract_declarator, cast_type)
                while tokens and tokens[0] == ')':
                    expect(')', tokens)
                cast_expr, tokens = parse_factor(tokens)
                return Cast(target_type=cast_type, exp=cast_expr), tokens
            else:
                expr, tokens = parse_exp(tokens)
                expect(")", tokens)
                return expr, tokens
        elif isIdentifier(next_token) and not isKeyword(next_token):
            identifier_token, tokens = take_token(tokens)
            identifier = Identifier(name=identifier_token)
            return Var(identifier=identifier), tokens
        else:
            raise SyntaxError(f"Expected <int>, <identifier>, '(', or unary operator, got '{next_token}'")
    except SyntaxError as e:
        raise e