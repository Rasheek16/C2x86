

from _Ast import Return, Constant, Unary ,Binary # Assuming these are your high-level AST classes
from tacky import *

from typing import List, Union
import uuid

def get_unique_id() -> str:
    """
    Generates a unique identifier string.
    
    Returns:
        str: A unique identifier.
    """
    return str(uuid.uuid4()).replace("-", "")  # Remove hyphens for a cleaner ID


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
    elif op == "Not":
        return TackyUnaryOperator.NOT
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
    print(expr)
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
    
    elif isinstance(expr, Binary):
        # Recursively emit instructions for the left operand of the binary expression
        v1 = emit_tacky_expr(expr.left, instructions)

        # Create unique labels for short-circuiting and the end label
        false_label = f"false_{get_unique_id()}"
        true_label = f"true_{get_unique_id()}"
        end_label = f"end_{get_unique_id()}"
        
        if expr.operator == 'And':
            # Implement && (AND) using JumpIfZero (short-circuit if v1 is 0)
            instructions.append(TackyJumpIfZero(condition=v1, target=false_label))
            print(expr.operator)
            # Recursively emit instructions for the right operand of the binary expression
            v2 = emit_tacky_expr(expr.right, instructions)

            # If the operator is &&, check v2 as well
            instructions.append(TackyJumpIfZero(condition=v2, target=false_label))

            # Allocate a temporary variable to store the result
            result_name = make_temporary()
            result_var = TackyVar(result_name)

            # Set result to 1 if both v1 and v2 are non-zero
            instructions.append(TackyCopy(source=TackyConstant(1), destination=result_var))
            
            # Jump to end to avoid setting result to 0
            instructions.append(TackyJump(target=end_label))

            # Label for false (if v1 or v2 is zero)
            instructions.append(TackyLabel(false_label))
            instructions.append(TackyCopy(source=TackyConstant(0), destination=result_var))

            # Label for end
            instructions.append(TackyLabel(end_label))

            return result_var

        elif expr.operator == 'Or':
            # Implement || (OR) using JumpIfNotZero (short-circuit if v1 is non-zero)
            instructions.append(TackyJumpIfNotZero(condition=v1, target=true_label))

            # Recursively emit instructions for the right operand of the binary expression
            v2 = emit_tacky_expr(expr.right, instructions)

            # If v1 was zero, check v2
            instructions.append(TackyJumpIfNotZero(condition=v2, target=true_label))

            # Allocate a temporary variable to store the result
            result_name = make_temporary()
            result_var = TackyVar(result_name)

            # Set result to 1 if v1 or v2 is non-zero
            instructions.append(TackyCopy(source=TackyConstant(1), destination=result_var))
            
            # Jump to end to avoid overwriting result
            instructions.append(TackyJump(target=end_label))

            # Label for true (if v1 or v2 is non-zero)
            instructions.append(TackyLabel(true_label))
            instructions.append(TackyCopy(source=TackyConstant(1), destination=result_var))

            # Label for end
            instructions.append(TackyLabel(end_label))

            return result_var
        else:
            # Recursively emit instructions for the left operand of the binary expression
            v1 = emit_tacky_expr(expr.left, instructions)
            # Recursively emit instructions for the right operand of the binary expression
            v2 = emit_tacky_expr(expr.right, instructions)
         
            # Generate  unique temporary variable name to store the result of the binary operation
            dst_name = make_temporary()
        
            # Create a TackyVar instance representing the destination variable
            dst = TackyVar(dst_name)
        
            # Convert the AST binary operator to its corresponding Tacky binary operator
            tacky_op = convert_binop(expr.operator)
            # Create a TackyBinary instruction with the operator, operands, and destination
            # This instruction represents the binary operation in the intermediate representation
            instructions.append(TackyBinary(tacky_op, v1, v2, dst))
        
            # Return the destination variable that holds the result of the binary operation
            return dst

        # Handle unsupported expression types by raising a TypeError
   
    else: 
        raise TypeError(f"Unsupported expression type: {type(expr)}")


def convert_binop(operator_token):
    print(operator_token)
    if operator_token=='Add':
        return TackyBinaryOperator.ADD
    elif operator_token=='Subtract':
        return TackyBinaryOperator.SUBTRACT
    elif operator_token=='Divide':
        return TackyBinaryOperator.DIVIDE
    elif operator_token=='Multiply':
        return TackyBinaryOperator.MULTIPLY
    elif operator_token=='Remainder':
        return TackyBinaryOperator.REMAINDER
    elif operator_token=='Or':
        return TackyBinaryOperator.OR
    elif operator_token=='Equal':
        return TackyBinaryOperator.EQUAL
    elif operator_token=='NotEqual':
        return TackyBinaryOperator.NOT_EQUAL
    elif operator_token=='And':
        return TackyBinaryOperator.AND
    elif operator_token=='LessOrEqual':
        return TackyBinaryOperator.LESS_OR_EQUAL
    elif operator_token=='LessThan':
        return TackyBinaryOperator.LESS_THAN
    elif operator_token=='GreaterOrEqual':
        return TackyBinaryOperator.GREATER_OR_EQUAL
    elif operator_token=='GreaterThan':
        return TackyBinaryOperator.GREATER_THAN

def emit_tacky(program) -> TackyProgram:
    """
    emit_tacky(e, instructions):
        match e with
        | Constant(c) ->
            return  Constant(c)
        | Unary(op, inner) ->
            src = emit_tacky(inner, instructions)
            dst_name = make_temporary()
            dst = Var(dst_name)
            tacky_op = convert_unop(op)
            instructions.append(Unary(tacky_op, src, dst))
            return dst
        | Binary(op, e1, e2) ->
            v1 = emit_tacky(e1, instructions)
            v2 = emit_tacky(e2, instructions)
            dst_name = make_temporary()
            dst = Var(dst_name)
            tacky_op = convert_binop(op)
            instructions.append(Binary(tacky_op, v1, v2, dst))
            return dst
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
    # print(type(func_def.name.name))
    # Create a TackyFunction with the collected instructions
    tacky_function = TackyFunction(
        name=func_def.name,  # Assuming func_def.name is an Identifier
        body=instructions
    )

    # Create and return the complete TackyProgram
    tacky_program = TackyProgram(function_definition=tacky_function)
    return tacky_program
