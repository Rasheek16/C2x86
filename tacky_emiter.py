# emitter.py

from _ast5 import *  # Your high-level AST classes
from tacky import *
from typing import List, Union

# Initialize label counters
temp_false_label = 0
temp_true_label = 0
temp_end_label = 0
temp_e2_label = 0 

def get_false_label() -> str:
    global temp_false_label
    temp_false_label += 1
    return f"false_{temp_false_label}"

def get_true_label() -> str:
    global temp_true_label
    temp_true_label += 1
    return f"true_{temp_true_label}"

def get_end_label() -> str:
    global temp_end_label
    temp_end_label += 1
    return f"end_{temp_end_label}"

def get_e2_label() -> str:
    global temp_e2_label
    temp_e2_label += 1
    return f"e2_{temp_e2_label}"

# A global counter for generating unique temporary names
temp_counter = 0

def make_temporary_var() -> Var:
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    return name

def make_temporary() -> TackyVar:
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    return TackyVar(name)

def convert_unop(op: str) -> str:
    """
    Map from high-level AST operator to Tacky IR operator constants.
    Handles "Negate", "Negation", "Complement", and "Not".
    """
    if op in ("Negate", "Negation"):
        return TackyUnaryOperator.NEGATE
    elif op == "Complement":
        return TackyUnaryOperator.COMPLEMENT
    elif op == "Not":
        return TackyUnaryOperator.NOT
    else:
        raise ValueError(f"Unknown unary operator: {op}")

def convert_binop(operator_token: str) -> str:
    """
    Map from high-level AST binary operator to Tacky IR binary operator constants.
    """
    mapping = {
        'Add': TackyBinaryOperator.ADD,
        'Subtract': TackyBinaryOperator.SUBTRACT,
        'Multiply': TackyBinaryOperator.MULTIPLY,
        'Divide': TackyBinaryOperator.DIVIDE,
        'Remainder': TackyBinaryOperator.REMAINDER,
        'Equal': TackyBinaryOperator.EQUAL,
        'NotEqual': TackyBinaryOperator.NOT_EQUAL,
        'LessThan': TackyBinaryOperator.LESS_THAN,
        'LessOrEqual': TackyBinaryOperator.LESS_OR_EQUAL,
        'GreaterThan': TackyBinaryOperator.GREATER_THAN,
        'GreaterOrEqual': TackyBinaryOperator.GREATER_OR_EQUAL,
        'And': TackyBinaryOperator.AND,
        'Or': TackyBinaryOperator.OR,
    }
    if operator_token in mapping:
        return mapping[operator_token]
    else:
        raise ValueError(f"Unknown binary operator: {operator_token}")

def emit_tacky_expr(expr, instructions: list) -> Union[TackyConstant, TackyVar]:
    """
    Generate Tacky IR instructions for a single expression node.
    Returns a 'val' (e.g., TackyConstant or TackyVar) that represents
    the result of the expression in the Tacky IR.
    """
    if isinstance(expr, Constant):
        return TackyConstant(expr.value)
    elif isinstance(expr, Var):
        return TackyVar(expr.identifier.name)
    elif isinstance(expr, Assignment):
        # Process the right-hand side expression
        rhs = emit_tacky_expr(expr.right, instructions)
        
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
        dst_var = make_temporary()

        # Convert the AST operator (e.g., 'Negate') to a Tacky IR operator
        tacky_op = convert_unop(expr.operator)

        # Append the TackyUnary instruction to the instructions list
        instructions.append(TackyUnary(operator=tacky_op, src=src_val, dst=dst_var))

        return dst_var
    elif isinstance(expr, If):
        # The 'If' expression is handled in emit_statement
        raise NotImplementedError("If expressions should be handled in emit_statement.")
    elif isinstance(expr, Conditional):
        # Handle the conditional (ternary) operator
        condition_var = emit_tacky_expr(expr.condition, instructions)
        e2_label = get_e2_label()
        end_label = get_end_label()

        instructions.append(TackyJumpIfZero(condition=condition_var, target=e2_label))

        # True branch
        e1_var = emit_tacky_expr(expr.exp2, instructions)
        tmp_result = make_temporary()
        instructions.append(TackyCopy(source=e1_var, destination=tmp_result))

        instructions.append(TackyJump(target=end_label))
        instructions.append(TackyLabel(e2_label))

        # False branch
        e2_var = emit_tacky_expr(expr.exp3, instructions)
        instructions.append(TackyCopy(source=e2_var, destination=tmp_result))

        instructions.append(TackyLabel(end_label))
        return tmp_result

    elif isinstance(expr, Binary):
        if expr.operator in ('And', 'Or'):
            # Short-circuit evaluation for logical operators
            if expr.operator == 'And':
                return emit_and_expr(expr, instructions)
            elif expr.operator == 'Or':
                return emit_or_expr(expr, instructions)
        else:
            # Handle regular binary operations
            v1 = emit_tacky_expr(expr.left, instructions)
            v2 = emit_tacky_expr(expr.right, instructions)
        
            # Generate a unique temporary variable name to store the result
            dst_var = make_temporary()
        
            # Convert the AST binary operator to its corresponding Tacky binary operator
            tacky_op = convert_binop(expr.operator)
        
            # Create a TackyBinary instruction with the operator, operands, and destination
            instructions.append(TackyBinary(operator=tacky_op, src1=v1, src2=v2, dst=dst_var))
        
            # Return the destination variable that holds the result of the binary operation
            return dst_var

    elif isinstance(expr, FunctionCall):
        # Handle function calls
        # 1. Evaluate each argument
        arg_vals = []
        for arg in expr.args:
            arg_val = emit_tacky_expr(arg, instructions)
            arg_vals.append(arg_val)
        
        # 2. Generate a new temporary to hold the function call's result
        dst_var = make_temporary()
        
        # 3. Emit the TackyFunCall instruction
        instructions.append(TackyFunCall(
            fun_name=expr.identifier.name,  # e.g., "foo"
            args=arg_vals,
            dst=dst_var
        ))
        
        # 4. Return the temporary holding the result
        return dst_var

    else: 
        raise TypeError(f"Unsupported expression type: {type(expr)}")

def emit_and_expr(expr: Binary, instructions: list) -> TackyVar:
    """
    Emits Tacky instructions for logical 'And' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr(expr.left, instructions)
    false_label = get_false_label()
    end_label = get_end_label()

    # If v1 is zero, jump to false_label
    instructions.append(TackyJumpIfZero(condition=v1, target=false_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr(expr.right, instructions)

    # If v2 is zero, jump to false_label
    instructions.append(TackyJumpIfZero(condition=v2, target=false_label))

    # Both operands are non-zero, result is 1
    result_var = make_temporary()
    instructions.append(TackyCopy(source=TackyConstant(1), destination=result_var))
    instructions.append(TackyJump(target=end_label))

    # False label: result is 0
    instructions.append(TackyLabel(false_label))
    instructions.append(TackyCopy(source=TackyConstant(0), destination=result_var))

    # End label
    instructions.append(TackyLabel(end_label))

    return result_var

def emit_or_expr(expr: Binary, instructions: list) -> TackyVar:
    """
    Emits Tacky instructions for logical 'Or' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr(expr.left, instructions)
    true_label = get_true_label()
    end_label = get_end_label()

    # If v1 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v1, target=true_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr(expr.right, instructions)

    # If v2 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v2, target=true_label))

    # Both operands are zero, result is 0
    result_var = make_temporary()
    instructions.append(TackyCopy(source=TackyConstant(0), destination=result_var))
    instructions.append(TackyJump(target=end_label))

    # True label: result is 1
    instructions.append(TackyLabel(true_label))
    instructions.append(TackyCopy(source=TackyConstant(1), destination=result_var))

    # End label
    instructions.append(TackyLabel(end_label))

    return result_var

def emit_statement(stmt, instructions: List[TackyInstruction]):
    # print('here')
    
    """
    Emits Tacky instructions for a given statement.
    """
    if isinstance(stmt,list):
        emit_s_statement(stmt,instructions)
    elif isinstance(stmt, If):
        emit_if_statement(stmt, instructions)
    
    elif isinstance(stmt, Return):
        ret_val = emit_tacky_expr(stmt.exp, instructions)
        instructions.append(TackyReturn(val=ret_val))
    elif isinstance(stmt, (DoWhile, While, For)):
        emit_loop_statement(stmt, instructions)
    elif isinstance(stmt, D):  # Variable Declaration
        # Handle variable declarations, possibly with initialization
        var_name = stmt.declaration.name.name
        if isinstance(stmt.declaration,FunDecl):
            convert_fun_decl_to_tacky(stmt.declaration)
        else:
            if stmt.declaration.init is not None and not isinstance(stmt.declaration.init, Null):
                # Emit assignment to initialize the variable
                assign_expr = Assignment(
                    left=Var(stmt.declaration.name),
                    right=stmt.declaration.init
                )
                emit_tacky_expr(assign_expr, instructions)
        # Else, no initialization needed
    elif isinstance(stmt, Expression):
        emit_tacky_expr(stmt.exp, instructions)
    elif isinstance(stmt, Compound):
        for inner_stmt in stmt.block:
            emit_statement(inner_stmt, instructions)
    elif isinstance(stmt, Break):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(stmt, Continue):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(stmt, S):
        emit_s_statement(stmt, instructions)
    elif isinstance(stmt, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type: {type(stmt)}")

def emit_if_statement(stmt: If, instructions: List[TackyInstruction]):
    """
    Emits Tacky instructions for an If statement.
    """
    condition_var = emit_tacky_expr(stmt.exp, instructions)
    else_label = get_false_label()
    end_label = get_end_label()

    # If condition is zero, jump to else_label
    instructions.append(TackyJumpIfZero(condition=condition_var, target=else_label))

    # Then branch
    emit_statement(stmt.then, instructions)
    instructions.append(TackyJump(target=end_label))

    # Else branch
    instructions.append(TackyLabel(else_label))
    if stmt._else and not isinstance(stmt._else, Null):
        emit_statement(stmt._else, instructions)

    # End label
    instructions.append(TackyLabel(end_label))

def emit_loop_statement(stmt, instructions: List[TackyInstruction]):
    """
    Handles DoWhile, While, and For loops by emitting Tacky instructions.
    """
    loop_id = stmt.label  # Assuming each loop has a unique label identifier
    start_label = f"start_{loop_id}"
    continue_label = f"continue_{loop_id}"
    break_label = f"break_{loop_id}"

    if isinstance(stmt, DoWhile):
        # DoWhile Loop: Execute body first, then condition
        instructions.append(TackyLabel(start_label))
        emit_statement(stmt.body, instructions)
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr(stmt._condition, instructions)
        instructions.append(TackyJumpIfNotZero(condition=condition_var, target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, While):
        # While Loop: Evaluate condition first
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr(stmt._condition, instructions)
        instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions)
        instructions.append(TackyJump(target=continue_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, For):
        # For Loop: Initialization; condition; post; body
        if stmt.init and not isinstance(stmt.init, Null):
            # print(stmt.init)
            if isinstance(stmt.init,InitDecl):
                emit_statement(stmt.init.declaration, instructions)
            elif isinstance(stmt.init,InitExp):
                emit_tacky_expr(stmt.init.exp.exp,instructions)

        instructions.append(TackyLabel(start_label))
        if stmt.condition and not isinstance(stmt.condition, Null):
            condition_var = emit_tacky_expr(stmt.condition, instructions)
            instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions)
        instructions.append(TackyLabel(continue_label))
        if stmt.post and not isinstance(stmt.post, Null):
            emit_tacky_expr(stmt.post, instructions)
        instructions.append(TackyJump(target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt,Null):
        pass
def emit_s_statement(stmt: S, instructions: List[TackyInstruction]):
    """
    Handles the S statement, which acts as a wrapper for other statements.
    """
    node = stmt.statement

    if isinstance(node, Expression):
        emit_tacky_expr(node.exp, instructions)
    elif isinstance(node, If):
        emit_if_statement(node, instructions)
    elif isinstance(node, Return):
        ret_val = emit_tacky_expr(node.exp, instructions)
        instructions.append(TackyReturn(val=ret_val))
    elif isinstance(node, Compound):
        for inner_stmt in node.block:
            emit_statement(inner_stmt, instructions)
    elif isinstance(node, Break):
        loop_id = node.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(node, Continue):
        loop_id = node.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(node, (DoWhile, While, For)):
        emit_loop_statement(node, instructions)
    elif isinstance(node, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type in S: {type(node)}")

def convert_fun_decl_to_tacky(fun_decl: FunDecl) -> TackyFunction:
    """
    Converts a single FunDecl AST node (with a body) into a TackyFunction.
    """
    instructions: List[TackyInstruction] = []

    # Gather parameter names
    param_names = [param.name.name for param in fun_decl.params]

    # Convert the function body into TACKY instructions
    # if isinstance(fun_decl.body, Block):
    #     print(fun_decl.body.block_items)
    if isinstance(fun_decl.body,Null):
        pass
    else: 
        for stmt in fun_decl.body:
            emit_statement(stmt, instructions)
    # else:
    #     print('here')
    #     emit_statement(fun_decl.body, instructions)

    # Ensure the function ends with Return(0) if no return statement is present
    # has_return = any(isinstance(instr, TackyReturn) for instr in instructions)
    # if not has_return:
    instructions.append(TackyReturn(val=TackyConstant(0)))

    return TackyFunction(
        identifier=fun_decl.name.name,      # Function name
        params=param_names,           # Function parameters
        body=instructions             # Function body instructions
    )

def emit_tacky_program(ast_program: Program) -> TackyProgram:
    """
    Converts the entire AST Program (which may have multiple functions)
    into a TackyProgram containing multiple TackyFunction definitions.
    """
    tacky_funcs = []

    for fun_decl in ast_program.function_definition:
        if isinstance(fun_decl, FunDecl):
            # Only process if the function has a body (i.e., it's a definition)
            if fun_decl.body is not None and not isinstance(fun_decl.body, Null):
                t_func = convert_fun_decl_to_tacky(fun_decl)
                tacky_funcs.append(t_func)
            # Else, discard declarations that have no body
        else:
            raise TypeError(f"Unsupported top-level node: {type(fun_decl)}")
    # tacky_funcs.append(TackyReturn(0))
    return TackyProgram(function_definition=tacky_funcs)

def emit_tacky(program_ast: Program) -> TackyProgram:
    """
    High-level function that converts a full AST 'Program' node into a TackyProgram.
    """
    return emit_tacky_program(program_ast)
