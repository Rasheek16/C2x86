from _ast5 import *
from tacky_emiter import make_temporary , convert_binop , convert_unop


def resolve_declaration(declaration: Declaration, variable_map: dict) -> Declaration:
    if not isinstance(declaration.name, Identifier):
        raise TypeError(f"Declaration name must be an Identifier, got {type(declaration.name)}")

    original_name = declaration.name.name
    if original_name in variable_map:
        raise ValueError(f"Duplicate variable declaration: '{original_name}'")

    unique_name = make_temporary()
    variable_map[original_name] = unique_name

    init = resolve_exp(declaration.init,variable_map)
    # if init is not None and not isinstance(init, Null):
    #     init = resolve_exp(init, variable_map)
    #     if not isinstance(init, Exp):
    #         raise TypeError(f"Initializer must be an Exp, got {type(init)}")

    return Declaration(name=Identifier(unique_name), init=init)


def resolve_exp(expression: Exp, variable_map: dict) -> Exp:
    # print(f"DEBUG: Resolving expression: {expression}")
    # print(f"DEBUG: Type of expression: {type(expression)}")

    if isinstance(expression, Assignment):
        # print(expression)
        if not isinstance(expression.left, Var):
            raise ValueError(f"Invalid lvalue in assignment: {expression.left}")
        # if not isinstance(expression.right, Exp):
        #     raise ValueError(f"Invalid rvalue in assignment: {expression.right}")
        resolved_right = resolve_exp(expression.right, variable_map)
        resolved_left = resolve_exp(expression.left, variable_map)
        return Assignment(left=resolved_left, right=resolved_right)
    elif isinstance(expression,Conditional):
        # print('inside conditional')
        resolved_condition = resolve_exp(expression.condition,variable_map)
        # print(resolved_condition)
        resolved_exp2= resolve_exp(expression.exp2,variable_map)
        
        resolved_exp3 = resolve_exp(expression.exp3,variable_map)
        # print(resolved_exp3)
        return Conditional(condition=resolved_condition,exp2=resolved_exp2,exp3=resolved_exp3)
    elif isinstance(expression, Var):
        if not isinstance(expression.identifier, Identifier):
            raise TypeError(f"Expected Identifier, got {type(expression.identifier)}")
        original_identifier = expression.identifier.name
        print(original_identifier)
        if original_identifier in variable_map:
            unique_identifier = variable_map[original_identifier]
            print(unique_identifier)
            return Var(identifier=Identifier(unique_identifier))
        else:
            raise ValueError(f"Undeclared variable usage: '{original_identifier}'")

    elif isinstance(expression, Unary):
        resolved_expr = resolve_exp(expression.expr, variable_map)
        return Unary(operator=expression.operator, expr=resolved_expr)

    elif isinstance(expression, Binary):
        if not isinstance(expression.left, Exp) or not isinstance(expression.right, Exp):
            raise ValueError("Both left and right must be Exp instances.")
        resolved_left = resolve_exp(expression.left, variable_map)
        resolved_right = resolve_exp(expression.right, variable_map)
        return Binary(operator=expression.operator, left=resolved_left, right=resolved_right)

    elif isinstance(expression, (Constant,Null)):
        return expression

    else:
        raise SyntaxError(f"Unknown expression type: {type(expression)}")


def resolve_block_items(block_items: List[BlockItem], variable_map: dict) -> List[BlockItem]:
    resolved_body = []
    for block_item in block_items:
        # print(block_item)
        if isinstance(block_item, D):
            print(block_item)
            resolved_declaration = resolve_declaration(block_item.declaration, variable_map)
            resolved_body.append(D(declaration=resolved_declaration))
        elif isinstance(block_item, S):
            resolved_statement = resolve_statement(block_item.statement, variable_map)
            resolved_body.append(S(statement=resolved_statement))
        else:
            raise SyntaxError(f"Unknown block item type: {type(block_item)}")
    return resolved_body


def resolve_statement(statement, variable_map) :
    # print('Statement spotted')
    # print(statement)
    if isinstance(statement, Return):
        # print('Found return')
        resolved_exp = resolve_exp(statement.exp, variable_map)
        return Return(exp=resolved_exp)
    elif isinstance(statement, Expression):
        resolved_exp = resolve_exp(statement.exp, variable_map)
        return Expression(exp=resolved_exp)
    elif isinstance(statement,If):
        resolved_exp = resolve_exp(statement.exp,variable_map)
        
        resolved_then = resolve_statement(statement.then,variable_map)
        if statement._else is not None:
            resolved_else = resolve_statement(statement._else,variable_map)
            return If(exp=resolved_exp,then=resolved_then,_else=resolved_else)
        else:
            return If(exp=resolved_exp,then=resolved_then)

    elif isinstance(statement, Null):
        return Null()
    else:
        raise SyntaxError(f"Invalid statement type: {type(statement)}")


def resolve_function(function: Function, variable_map: dict) -> Function:
    resolved_body = resolve_block_items(function.body, variable_map)
    return Function(name=function.name, body=resolved_body)


def variable_resolution_pass(program: Program) -> Program:
    variable_map = {}
    resolved_function = resolve_function(program.function_definition, variable_map)
    return Program(function_definition=resolved_function)
