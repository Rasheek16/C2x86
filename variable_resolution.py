# Fixed Code

from _ast5 import *
from tacky_emiter import make_temporary, convert_binop, convert_unop
from typing import List, Dict, Any
import copy


def resolve_declaration(declaration: Declaration, variable_map: dict) -> Declaration:
    """
    Resolves a variable declaration by ensuring no duplicate declarations
    in the current block and mapping the variable to a unique name.

    Args:
        declaration (Declaration): The variable declaration with a name and optional initialization.
        variable_map (dict): A mapping of variable names to their unique names and block metadata.

    Returns:
        Declaration: The resolved declaration with a unique name and resolved initialization.

    Raises:
        TypeError: If the declaration name is not an Identifier.
        ValueError: If the variable is already declared in the current block.
    """
    if not isinstance(declaration.name, Identifier):
        raise TypeError(f"Declaration name must be an Identifier, got {type(declaration.name)}")

    original_name = declaration.name.name

    # Check for duplicate declarations in the same block
    if original_name in variable_map and variable_map[original_name]['from_current_block']:
        raise ValueError(f"Duplicate variable declaration: '{original_name}'")

    # Generate a unique name for the variable
    unique_name = make_temporary()

    # Update the variable map with the new unique name and metadata
    variable_map[original_name] = {'unique_name': unique_name, 'from_current_block': True}

    # Resolve the initialization expression if present
    init = None  # Initialize to None
    if declaration.init is not None:
        init = resolve_exp(declaration.init, variable_map)

    # Return the new declaration with the unique name and resolved initialization
    return Declaration(name=Identifier(unique_name), init=init)


def resolve_exp(expression: Exp, variable_map: dict) -> Exp:
    """
    Resolves expressions by mapping variable identifiers to their unique names.

    Args:
        expression (Exp): The expression to resolve.
        variable_map (dict): The current variable mapping.

    Returns:
        Exp: The resolved expression.

    Raises:
        ValueError: If there's an undeclared variable usage or invalid assignment.
        TypeError: If expected types are not met.
        SyntaxError: If an unknown expression type is encountered.
    """
def resolve_exp(expression: Exp, variable_map: dict) -> Exp:
    if isinstance(expression, Assignment):
        if not isinstance(expression.left, Var):
            raise ValueError(f"Invalid lvalue in assignment: {expression.left}")
        resolved_left = resolve_exp(expression.left, variable_map)
        resolved_right = resolve_exp(expression.right, variable_map)
        return Assignment(left=resolved_left, right=resolved_right)

    elif isinstance(expression, Conditional):
        # --- NEW CHECK HERE ---
        # If your grammar doesn't allow assignment expressions inside the ternary branches,
        # raise an error if either branch is an Assignment node.
        # if isinstance(expression.exp2, Assignment) or isinstance(expression.exp3, Assignment):
            # Or you can do deeper checks if the assignment is nested inside something else
            # raise ValueError("Invalid assignment in ternary expression according to the grammar.")
        resolved_condition = resolve_exp(expression.condition, variable_map)
        resolved_exp2 = resolve_exp(expression.exp2, variable_map)
        resolved_exp3 = resolve_exp(expression.exp3, variable_map)
        return Conditional(condition=resolved_condition, exp2=resolved_exp2, exp3=resolved_exp3)
    elif isinstance(expression, Var):
        if not isinstance(expression.identifier, Identifier):
            raise TypeError(f"Expected Identifier, got {type(expression.identifier)}")
        original_identifier = expression.identifier.name
        if original_identifier in variable_map:
            unique_name = variable_map[original_identifier]['unique_name']
            return Var(identifier=Identifier(unique_name))
        else:
            raise ValueError(f"Undeclared variable usage: '{original_identifier}'")

    elif isinstance(expression, Unary):
        resolved_expr = resolve_exp(expression.expr, variable_map)
        return Unary(operator=expression.operator, expr=resolved_expr)

    elif isinstance(expression, Binary):
        resolved_left = resolve_exp(expression.left, variable_map)
        resolved_right = resolve_exp(expression.right, variable_map)
        return Binary(operator=expression.operator, left=resolved_left, right=resolved_right)

    elif isinstance(expression, (Constant, Null)):
        return expression

    else:
        raise SyntaxError(f"Unknown expression type: {type(expression)}")


def resolve_block_items(block_items: List[BlockItem], variable_map: dict) -> List[BlockItem]:
    """
    Resolves a list of block items (declarations and statements) within a block.

    Args:
        block_items (List[BlockItem]): The list of block items to resolve.
        variable_map (dict): The current variable mapping.

    Returns:
        List[BlockItem]: The list of resolved block items.

    Raises:
        SyntaxError: If an unknown block item type is encountered.
    """
    resolved_body = []
    for block_item in block_items:
        if isinstance(block_item, D):
            resolved_declaration = resolve_declaration(block_item.declaration, variable_map)
            resolved_body.append(D(declaration=resolved_declaration))
        elif isinstance(block_item, S):
            resolved_statement = resolve_statement(block_item.statement, variable_map)
            resolved_body.append(S(statement=resolved_statement))
        elif isinstance(block_item, Compound):
            # Handle nested blocks by creating a new scope
            new_variable_map = copy_variable_map(variable_map)
            resolved_compound = Compound(block=resolve_block_items(block_items=block_item.block, variable_map=new_variable_map))
            resolved_body.append(resolved_compound)
        else:
            raise SyntaxError(f"Unknown block item type: {type(block_item)}")
    return resolved_body


def copy_variable_map(variable_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Creates a copy of the variable map with 'from_current_block' set to False for every entry.

    Args:
        variable_map (Dict[str, Dict[str, Any]]): The original variable map.

    Returns:
        Dict[str, Dict[str, Any]]: A new variable map with updated 'from_current_block' flags.
    """
    new_map = copy.deepcopy(variable_map)
    for var_info in new_map.values():
        var_info['from_current_block'] = False
    return new_map


def resolve_statement(statement, variable_map: dict) -> Any:
    """
    Resolves a single statement by mapping variable identifiers to their unique names.

    Args:
        statement: The statement to resolve.
        variable_map (dict): The current variable mapping.

    Returns:
        The resolved statement.

    Raises:
        SyntaxError: If an invalid statement type is encountered.
    """
    if isinstance(statement, Return):
        resolved_exp = resolve_exp(statement.exp, variable_map)
        return Return(exp=resolved_exp)

    elif isinstance(statement, Expression):
        resolved_exp = resolve_exp(statement.exp, variable_map)
        return Expression(exp=resolved_exp)

    elif isinstance(statement, Compound):
        # Handle nested blocks by creating a new scope
        new_variable_map = copy_variable_map(variable_map)
        resolved_block = resolve_block_items(block_items=statement.block, variable_map=new_variable_map)
        return Compound(block=resolved_block)

    elif isinstance(statement, If):
        resolved_exp = resolve_exp(statement.exp, variable_map)
        resolved_then = resolve_statement(statement.then, variable_map)
        if statement._else is not None:
            resolved_else = resolve_statement(statement._else, variable_map)
            return If(exp=resolved_exp, then=resolved_then, _else=resolved_else)
        else:
            return If(exp=resolved_exp, then=resolved_then)

    elif isinstance(statement, Null):
        return Null()

    else:
        raise SyntaxError(f"Invalid statement type: {type(statement)}")


def resolve_function(function: Function, variable_map: dict) -> Function:
    """
    Resolves all block items within a function.

    Args:
        function (Function): The function to resolve.
        variable_map (dict): The current variable mapping.

    Returns:
        Function: The resolved function with all variables uniquely named.
    """
    resolved_body = resolve_block_items(block_items=function.body, variable_map=variable_map)
    return Function(name=function.name, body=resolved_body)


def variable_resolution_pass(program: Program) -> Program:
    """
    Performs the variable resolution pass on the entire program.

    Args:
        program (Program): The program to resolve.

    Returns:
        Program: The resolved program with all variables uniquely named.
    """
    variable_map = {}
    resolved_function = resolve_function(program.function_definition, variable_map)
    return Program(function_definition=resolved_function)
