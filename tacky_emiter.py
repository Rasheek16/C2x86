

from _Ast import Return, Constant, Unary  # Assuming these are your high-level AST classes
from tacky import (
    TackyProgram,
    TackyFunction,
    TackyReturn,
    TackyUnary,
    TackyVar,
    TackyConstant,
    TackyUnaryOperator
)
from typing import List, Union

# A global counter for generating unique temporary names
temp_counter = 0

def make_temporary():
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    return name

def convert_unop(op: str) -> str:
    """
    Map from high-level AST operator to Tacky IR operator constants.
    
    Handles "Negate", "Negation", and "Complement".
    
    Args:
        op (str): The unary operator from the high-level AST.
    
    Returns:
        str: The corresponding Tacky IR unary operator.
    
    Raises:
        ValueError: If the operator is unrecognized.
    """
    if op in ("Negate", "Negation"):
        return TackyUnaryOperator.NEGATE
    elif op == "Complement":
        return TackyUnaryOperator.COMPLEMENT
    else:
        raise ValueError(f"Unknown unary operator: {op}")

def emit_tacky_expr(expr, instructions: list) -> Union[TackyConstant, TackyVar]:
    """
    Generate Tacky IR instructions for a single expression node.
    Returns a 'val' (e.g., TackyConstant or TackyVar) that represents
    the result of the expression in the Tacky IR.
    
    Args:
        expr: The expression node from the high-level AST.
        instructions (list): The list to append Tacky IR instructions to.
    
    Returns:
        Union[TackyConstant, TackyVar]: The resulting value after processing the expression.
    
    Raises:
        TypeError: If the expression type is unsupported.
    """
    if isinstance(expr, Constant):
        return TackyConstant(expr.value)
    
    elif isinstance(expr, Unary):
        # Handle the Unary case recursively
        src_val = emit_tacky_expr(expr.expr, instructions)

        # Allocate a new temporary variable for the result
        dst_name = make_temporary()
        dst_val = TackyVar(dst_name)

        # Convert the AST operator (e.g., 'Negate') to a Tacky IR operator
        tacky_op = convert_unop(expr.operator)

        # Append the TackyUnary instruction to the instructions list
        instructions.append(TackyUnary(tacky_op, src_val, dst_val))

        return dst_val

    else:
        raise TypeError(f"Unsupported expression type: {type(expr)}")

def emit_tacky(program) -> TackyProgram:
    """
    Given a Program node (with one or more Functions), generate and return
    a TackyProgram containing all functions with their corresponding Tacky IR instructions.
    
    Args:
        program: The high-level AST Program node.
    
    Returns:
        TackyProgram: The complete Tacky IR representation of the program.
    
    Raises:
        TypeError: If the program contains unsupported statement types.
    """
    # Initialize the list of TackyFunction instances
    tacky_function: List[TackyFunction] = []
    
    # Extract the function definition
    func_def = program.function_definition
    instructions: List = []
    # print(type(program.function_definition.body))
    # Iterate over each statement in the function's body
    for stmt in func_def.body:
        if isinstance(stmt, Return):
            # Process the return expression using emit_tacky_expr
            ret_expr = stmt.exp
            ret_val = emit_tacky_expr(ret_expr, instructions)

            # Emit the TackyReturn instruction
            instructions.append(TackyReturn(ret_val))
        else:
            raise TypeError(f"Unsupported statement type: {type(stmt)}")

    # Create a TackyFunction with the collected instructions
    tacky_function = TackyFunction(
        name=func_def.name,  # Assuming func_def.name is an Identifier
        body=instructions
    )

    # Create and return the complete TackyProgram
    tacky_program = TackyProgram(function_definition=tacky_function)
    return tacky_program
