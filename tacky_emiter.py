

from _ast5 import * # Assuming these are your high-level AST classes
from tacky import *

from typing import List, Union
import uuid

temp_false_label= 0
temp_true_label= 0
temp_end_label= 0
temp_e2_label =0 
def get_false_label() -> str:
    global temp_false_label
    temp_false_label += 1
    return str(temp_false_label)

def get_true_label() -> str:
    global temp_true_label
    temp_true_label += 1
    return str(temp_true_label)

def get_end_label() -> str:
    global temp_end_label
    temp_end_label += 1
    return str(temp_end_label)

def get_e2_label() -> str:
    global temp_e2_label
    temp_e2_label += 1
    return str(temp_e2_label)

def get_false_label() -> str:
    global temp_false_label
    temp_false_label+=1
    """
    Generates a unique identifier string.
    
    Returns:
        str: A unique identifier.
    """
    return str(temp_false_label)  # Remove hyphens for a cleaner ID


def get_true_label() -> str:
    global temp_true_label
    temp_true_label+=1
    """
    Generates a unique identifier string.
    
    Returns:
        str: A unique identifier.
    """
    return str(temp_true_label) 
def get_end_label() -> str:
    global temp_end_label
    temp_end_label+=1
    """
    Generates a unique identifier string.
    
    Returns:
        str: A unique identifier.
    """
    return str(temp_end_label) 

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
    # print(expr)
    if isinstance(expr, Constant):
        return TackyConstant(expr.value)
    elif isinstance(expr, Var):
        return TackyVar(expr.identifier.name)
    elif isinstance(expr, Assignment):
        # Process the right-hand side expression
        rhs = emit_tacky_expr(expr=expr.right, instructions=instructions)
        
        # Ensure the left-hand side is a variable
        if isinstance(expr.left, Var):
            lhs = TackyVar(expr.left.identifier.name)
            instructions.append(TackyCopy(source=rhs, destination=lhs))
            return lhs  # Return the assigned variable
        else:
            raise TypeError(f"Unsupported assignment target: {type(expr.left)}")
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
    elif isinstance(expr, If):
        condition_var = emit_tacky_expr(expr.exp, instructions)
        else_label = f"false_{get_false_label()}"
        end_label = f"end_{get_end_label()}"

        instructions.append(TackyJumpIfZero(condition=condition_var, target=else_label))

        # 'then' branch
        emit_statement(expr.then, instructions)
        # instructions.append(TackyJump(target=end_label))

        # 'else' branch
        if expr._else:
            instructions.append(TackyJump(target=end_label))
            instructions.append(TackyLabel(else_label))
            emit_statement(expr._else, instructions)
        else:
            # If no else part, still create the else_label
            instructions.append(TackyLabel(else_label))

        instructions.append(TackyLabel(end_label))
        # Typically doesn't return a value in Tacky
        return TackyConstant(0)

    # 6) Conditional (ternary) ?:
    elif isinstance(expr, Conditional):
        condition_var = emit_tacky_expr(expr.condition, instructions)
        e2_label = f"e2_{get_e2_label()}"
        end_label = f"end_{get_end_label()}"

        instructions.append(TackyJumpIfZero(condition=condition_var, target=e2_label))

        # True branch
        e1_var = emit_tacky_expr(expr.exp2, instructions)
        tmp_result = make_temporary()
        instructions.append(TackyCopy(source=e1_var, destination=TackyVar(tmp_result)))

        instructions.append(TackyJump(target=end_label))
        instructions.append(TackyLabel(e2_label))

        # False branch
        e2_var = emit_tacky_expr(expr.exp3, instructions)
        instructions.append(TackyCopy(source=e2_var, destination=TackyVar(tmp_result)))

        instructions.append(TackyLabel(end_label))
        return TackyVar(tmp_result)

    elif isinstance(expr, Binary):
        # Recursively emit instructions for the left operand of the binary expression
        v1 = emit_tacky_expr(expr.left, instructions)

        # Create unique labels for short-circuiting and the end label
        false_label = f"false_{get_false_label()}"
        true_label = f"true_{get_true_label()}"
        end_label = f"end_{get_end_label()}"
        
        if expr.operator == 'And':
            # Implement && (AND) using JumpIfZero (short-circuit if v1 is 0)
            instructions.append(TackyJumpIfZero(condition=v1, target=false_label))
            # print(expr.operator)
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

            # **Corrected:** Set result to 0 if both v1 and v2 are zero
            instructions.append(TackyCopy(source=TackyConstant(0), destination=result_var))
            
            # Jump to end to avoid overwriting result
            instructions.append(TackyJump(target=end_label))

            # Label for true (if v1 or v2 is non-zero)
            instructions.append(TackyLabel(true_label))
            instructions.append(TackyCopy(source=TackyConstant(1), destination=result_var))
            instructions.append(TackyJump(target=end_label))  # Ensure jump to end after true case

            # **Removed:** The false_label and its associated instructions as they're now redundant

            # Label for end
            instructions.append(TackyLabel(end_label))
            print('returning',result_var)

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
    # print(operator_token)
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

# def emit_tacky(program) -> TackyProgram:
#     """
#     emit_tacky(e, instructions):
#         match e with
#         | Constant(c) ->
#             return  Constant(c)
#         | Unary(op, inner) ->
#             src = emit_tacky(inner, instructions)
#             dst_name = make_temporary()
#             dst = Var(dst_name)
#             tacky_op = convert_unop(op)
#             instructions.append(Unary(tacky_op, src, dst))
#             return dst
#         | Binary(op, e1, e2) ->
#             v1 = emit_tacky(e1, instructions)
#             v2 = emit_tacky(e2, instructions)
#             dst_name = make_temporary()
#             dst = Var(dst_name)
#             tacky_op = convert_binop(op)
#             instructions.append(Binary(tacky_op, v1, v2, dst))
#             return dst
#     Given a Program node (with one or more Functions), generate and return
#     a TackyProgram containing all functions with their corresponding Tacky IR instructions.
    
#     Args:
#         program: The high-level AST Program node.
    
#     Returns:
#         TackyProgram: The complete Tacky IR representation of the program.
    
#     Raises:
#         TypeError: If the program contains unsupported statement types.
#     """
#     # Initialize the list of TackyFunction instances
#     tacky_function: List[TackyFunction] = []
    
#     # Extract the function definition
#     func_def = program.function_definition
#     instructions: List = []
#     # print(type(program.function_definition.body))
#     # Iterate over each statement in the function's body
#     for stmt in func_def.body:
#         print(stmt)
#         if isinstance(stmt, D):
#             if not isinstance(stmt.declaration.init,Null):
#                 assign_expr = Assignment(left=Var(stmt.declaration.name), right=stmt.declaration.init)
#                 emit_tacky_expr(assign_expr, instructions)
#         elif isinstance(stmt, S):
#             if isinstance(stmt.statement, Expression):
#                  emit_tacky_expr(stmt.statement.exp, instructions)
#             elif isinstance(stmt.statement, Return):
#                 print(stmt)
#                 ret_val=emit_tacky_expr(stmt.statement.exp, instructions)
#                 instructions.append(TackyReturn(ret_val))
#             elif isinstance(stmt.statement, Null):
#                 # instructions.append(TackyReturn(TackyConstant(0)))  # Null statements are ignored
#                 pass
#             else:
#                 raise TypeError(f"Unsupported statement type: {type(stmt.statement)}")
#         else:
#             raise TypeError(f"Unsupported block item type: {type(stmt)}")

#     # Ensure a Return instruction exists
#     # if not any(isinstance(ins, TackyReturn) for ins in instructions):
#     #     instructions.append(TackyReturn(TackyConstant(0)))

#     return TackyProgram(function_definition=TackyFunction(name=func_def.name, body=instructions))

def emit_statement(stmt, instructions: List):
    if isinstance(stmt, If):
        emit_tacky_expr(stmt, instructions)

    # elif isinstance(stmt,Compound):
    #     for block_item in stmt.block.block_items:
    #         if isinstance(block_item,Compound):
    #             ret = emit_statement(block_item.block)
    #         else:
    #             ret_val = emit_tacky_expr(block_item,instructions)
            
    elif isinstance(stmt, Return):
        ret_val = emit_tacky_expr(stmt.exp, instructions)
        instructions.append(TackyReturn(ret_val))

    elif isinstance(stmt, D):
        # Declarations
        if not isinstance(stmt.declaration.init, Null):
            assign_expr = Assignment(
                left=Var(stmt.declaration.name),
                right=stmt.declaration.init
            )
            emit_tacky_expr(assign_expr, instructions)
        else:
            pass
    elif isinstance(stmt, Expression):
        emit_tacky_expr(stmt.exp, instructions)

    elif isinstance(stmt, Null):
        pass

    elif isinstance(stmt,Compound):
            for expr in stmt.block:
                emit_statement(expr,instructions)
                
    elif isinstance(stmt, S):
        # FIX #2: Ensure we do not double-emit
        node = stmt.statement
        # print('node',node)
        if isinstance(node, Expression):
            emit_tacky_expr(node.exp, instructions)
        elif isinstance(node, If):
            emit_tacky_expr(node, instructions)
        elif isinstance(node, Return):
            ret_val = emit_tacky_expr(node.exp, instructions)
            instructions.append(TackyReturn(ret_val))
        elif isinstance(node,Compound):
            # print(node.block)
            for expr in node.block:
                emit_statement(expr,instructions)
        elif isinstance(node, Null):
            pass
        else:
            raise TypeError(f"Unsupported statement type: {type(node)}")

    else:
        raise TypeError(f"Unsupported statement type: {type(stmt)}")

def emit_function_body(body: List, instructions: List):
    for stmt in body:
        # print(stmt)
        emit_statement(stmt, instructions)

def emit_tacky(program) -> TackyProgram:
    instructions: List = []
    func_def = program.function_definition
    emit_function_body(func_def.body, instructions)
    return TackyProgram(
        function_definition=TackyFunction(name=func_def.name, body=instructions)
    )