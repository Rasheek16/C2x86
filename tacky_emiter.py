# emitter.py

from _ast5 import *  # Your high-level AST classes
from tacky import *
from typing import List, Union
from type_classes import *
from typechecker import size,isSigned
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

def convert_symbols_to_tacky(symbols:dict):
    # #print(symbols)
    tacks_defs=[]
    for name,entry in symbols.items():
        if entry['attrs']!=None:
            if isinstance(entry['attrs'],StaticAttr):
                # exit()
                if isinstance(entry['attrs'].init,Initial):
                    init=entry['attrs'].init.value
                    # print('init',init)
                    # exit()
                    if isinstance(init,IntInit):
                     
                        init = IntInit(init.value.value._int)
                    else:
                        init=LongInit(init.value.value._int)
                        
                    tacks_defs.append(TackyStaticVariable(identifier=name,_global =entry['attrs'].global_scope,_type=entry['val_type'],init=init))
                    # print(init)
                    # exit()
                elif isinstance(entry['attrs'].init,Tentative):
                    
                    if type(entry['val_type']==type(Long)):
                        init = LongInit(0)
                    else:
                        init =IntInit(0)
                    tacks_defs.append(TackyStaticVariable(identifier=name,_type=entry['val_type'],_global =entry['attrs'].global_scope,init=init))
                    print(tacks_defs)
                    # exit()
                else:
                    continue
            else:
                continue
        else:
            continue
    return tacks_defs
                
                
                
            
        
    


# A global counter for generating unique temporary names
temp_counter = 0
# temp_counter1 = 0


def make_temporary_var() -> Var:
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    return name




def make_temporary(symbols,var_type) -> TackyVar:
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    symbols[name]={
        'val_type':var_type,
        'attrs':LocalAttr(),
        'ret': var_type,
        
        
    }
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

def emit_tacky_expr(expr, instructions: list,symbols:Optional[dict]) -> Union[TackyConstant, TackyVar]:
    """
    Generate Tacky IR instructions for a single expression node.
    Returns a 'val' (e.g., TackyConstant or TackyVar) that represents
    the result of the expression in the Tacky IR.
    """
    if isinstance(expr, Constant):
        # print(expr)
        if not isinstance(expr.value,(ConstInt,ConstLong,ConstUInt,ConstULong)):
            return TackyConstant(expr.value._int)
        return TackyConstant(expr.value)
    elif isinstance(expr, Var):
        # print(expr)
        # exit()
        return TackyVar(expr.identifier.name)
    elif isinstance(expr, Assignment):
        #print(symbols)
        #print('in assignment',expr)
        #print('RHS IN ASSIGNMENT',expr.right)
        
        # Process the right-hand side expression
        rhs = emit_tacky_expr(expr.right, instructions,symbols)
        #print('rhs')
        # Ensure the left-hand side is a variable
        if isinstance(expr.left, Var):
            lhs = TackyVar(expr.left.identifier.name)
            instructions.append(TackyCopy(source=rhs, destination=lhs))
            return lhs  # Return the assigned variable
        else:
            raise TypeError(f"Unsupported assignment target: {type(expr.left)}")
    elif isinstance(expr, Unary):
        # Handle the Unary case recursively
        src_val = emit_tacky_expr(expr.expr, instructions,symbols)
        # print(expr)
        # Allocate a new temporary variable for the result
        
        dst_var = make_temporary(symbols,expr.get_type())
        
        # print(expr.get_type())
        # exit()

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
        condition_var = emit_tacky_expr(expr.condition, instructions,symbols)
        e2_label = get_e2_label()
        end_label = get_end_label()

        instructions.append(TackyJumpIfZero(condition=condition_var, target=e2_label))

        # True branch
        e1_var = emit_tacky_expr(expr.exp2, instructions,symbols)
        tmp_result = make_temporary(symbols,expr.get_type())
        
        instructions.append(TackyCopy(source=e1_var, destination=tmp_result))

        instructions.append(TackyJump(target=end_label))
        instructions.append(TackyLabel(e2_label))

        # False branch
        e2_var = emit_tacky_expr(expr.exp3, instructions,symbols)
        instructions.append(TackyCopy(source=e2_var, destination=tmp_result))

        instructions.append(TackyLabel(end_label))
        return tmp_result
    elif isinstance(expr,Cast):      
        result  = emit_tacky_expr(expr.exp,instructions,symbols=symbols)
        inner_type = expr.exp._type
        t = expr.target_type
        if t==inner_type:
            return result
        dst_name = make_temporary(symbols,expr.target_type)
        print(expr)
        # exit()
        if size(t)==size(inner_type):
            instructions.append(TackyCopy(result,dst_name))
        elif size(t)<size(inner_type):
            instructions.append(TackyTruncate(result,dst_name))
        elif isSigned(inner_type):
            instructions.append(TackySignExtend(result,dst_name))
        else:
            instructions.append(TackyZeroExtend(result,dst_name))
            
        return dst_name
  
    elif isinstance(expr, Binary):
        if expr.operator in ('And', 'Or'):
            # Short-circuit evaluation for logical operators
            if expr.operator == 'And':
                return emit_and_expr(expr, instructions,symbols)
            elif expr.operator == 'Or':
                return emit_or_expr(expr, instructions,symbols)
        else:
            # print(expr)
            # exit()
            
            # Handle regular binary operations
            v1 = emit_tacky_expr(expr.left, instructions,symbols)
            v2 = emit_tacky_expr(expr.right, instructions,symbols)
            # print(v1)
            # exit()
            # Generate a unique temporary variable name to store the result
            # print(expr.get_type())
            dst_var = make_temporary(symbols,expr.get_type())
            # if expr.operator == TackyBinaryOperator.EQUAL:
                # print(dst_var)
                # print(symbols[dst_var.identifier])
                # exit()
            # Convert the AST binary operator to its corresponding Tacky binary operator
            tacky_op = convert_binop(expr.operator)
            # if tacky_op==BinaryOperator.LESS_OR_EQUAL:
                # print(v1)
                # exit()
                # print(symbols[v2.identifier])
                
                # exit()
            # print(tacky_op)
            # exit()
            # Create a TackyBinary instruction with the operator, operands, and destination
            instructions.append(TackyBinary(operator=tacky_op, src1=v1, src2=v2, dst=dst_var))
        
            # Return the destination variable that holds the result of the binary operation
            
            return dst_var
        
        

    elif isinstance(expr, FunctionCall):
        # Handle function calls
        # 1. Evaluate each argument
        arg_vals = []
        for arg in expr.args:
            arg_val = emit_tacky_expr(arg, instructions,symbols)
            arg_vals.append(arg_val)
        
        # 2. Generate a new temporary to hold the function call's result
        dst_var = make_temporary(symbols,expr.get_type())
        print('result of funcall',symbols[dst_var.identifier])
        print(symbols)
        # exit()
        # 3. Emit the TackyFunCall instruction
        instructions.append(TackyFunCall(
            fun_name=expr.identifier.name,  # e.g., "foo"
            args=arg_vals,
            dst=dst_var
        ))
        
        # 4. Return the temporary holding the result
        return dst_var
    elif isinstance(expr,(IntInit,LongInit)):
        # print('iofdszh;g')
        return Constant(expr.value)
        # pass 
    else: 
        #print(expr)
        raise TypeError(f"Unsupported expression type: {type(expr)}")

def emit_and_expr(expr: Binary, instructions: list,symbols) -> TackyVar:
    """
    Emits Tacky instructions for logical 'And' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr(expr.left, instructions,symbols)
    false_label = get_false_label()
    end_label = get_end_label()

    # If v1 is zero, jump to false_label
    instructions.append(TackyJumpIfZero(condition=v1, target=false_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr(expr.right, instructions,symbols)

    # If v2 is zero, jump to false_label
    instructions.append(TackyJumpIfZero(condition=v2, target=false_label))

    # Both operands are non-zero, result is 1
    result_var = make_temporary(symbols,expr.get_type())
    
    instructions.append(TackyCopy(source=TackyConstant(ConstInt(1)), destination=result_var))
    instructions.append(TackyJump(target=end_label))

    # False label: result is 0
    instructions.append(TackyLabel(false_label))
    instructions.append(TackyCopy(source=TackyConstant(ConstInt(0)), destination=result_var))

    # End label
    instructions.append(TackyLabel(end_label))

    return result_var

def emit_or_expr(expr: Binary, instructions: list,symbols) -> TackyVar:
    """
    Emits Tacky instructions for logical 'Or' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr(expr.left, instructions,symbols)
    true_label = get_true_label()
    end_label = get_end_label()

    # If v1 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v1, target=true_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr(expr.right, instructions,symbols)

    # If v2 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v2, target=true_label))

    # Both operands are zero, result is 0
    result_var = make_temporary(symbols,expr.get_type())
    
    instructions.append(TackyCopy(source=TackyConstant(ConstInt(0)), destination=result_var))
    instructions.append(TackyJump(target=end_label))

    # True label: result is 1
    instructions.append(TackyLabel(true_label))
    instructions.append(TackyCopy(source=TackyConstant(ConstInt(1)), destination=result_var))

    # End label
    instructions.append(TackyLabel(end_label))

    return result_var

def emit_statement(stmt, instructions: List[TackyInstruction],symbols:Optional[dict]):
    # #print(stmt)
    # #print(symbols)
    # #print('here')
    
    """
    Emits Tacky instructions for a given statement.
    """
    if isinstance(stmt,list):
        emit_s_statement(stmt,instructions)
    elif isinstance(stmt, If):
        emit_if_statement(stmt, instructions,symbols)
    
    elif isinstance(stmt, Return):
        ret_val = emit_tacky_expr(stmt.exp, instructions,symbols)
        instructions.append(TackyReturn(val=ret_val))
    elif isinstance(stmt, (DoWhile, While, For)):
        #print('In Loop')
        #print(stmt )
        emit_loop_statement(stmt, instructions,symbols)
        #print('After Loop')
        
    elif isinstance(stmt, D):  # Variable Declaration
        # Handle variable declarations, possibly with initialization
        var_name = stmt.declaration.name.name
        if isinstance(stmt.declaration,FunDecl):
            convert_fun_decl_to_tacky(stmt.declaration,symbols)
        else:
            if stmt.declaration.init is not None and not isinstance(stmt.declaration.init, Null) and not isinstance(stmt.declaration.storage_class,Static):
                # Emit assignment to initialize the variable
                assign_expr = Assignment(
                    left=Var(stmt.declaration.name),
                    right=stmt.declaration.init
                )
                emit_tacky_expr(assign_expr, instructions,symbols)
        # Else, no initialization needed
    elif isinstance(stmt, Expression):
        emit_tacky_expr(stmt.exp, instructions,symbols)
    elif isinstance(stmt, Compound):
        #print('In compund')
        for inner_stmt in stmt.block:
            emit_statement(inner_stmt, instructions,symbols)
        #print('after compount')
    elif isinstance(stmt, Break):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(stmt, Continue):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(stmt, S):
        #print('Found s statements')
        emit_s_statement(stmt, instructions,symbols)
        #print('After s statements')
        
    elif isinstance(stmt, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type: {type(stmt)}")

def emit_if_statement(stmt: If, instructions: List[TackyInstruction],symbols):
    """
    Emits Tacky instructions for an If statement.
    """
    condition_var = emit_tacky_expr(stmt.exp, instructions,symbols)
    else_label = get_false_label()
    end_label = get_end_label()

    # If condition is zero, jump to else_label
    instructions.append(TackyJumpIfZero(condition=condition_var, target=else_label))

    # Then branch
    emit_statement(stmt.then, instructions,symbols)
    instructions.append(TackyJump(target=end_label))

    # Else branch
    instructions.append(TackyLabel(else_label))
    if stmt._else and not isinstance(stmt._else, Null):
        emit_statement(stmt._else, instructions,symbols)

    # End label
    instructions.append(TackyLabel(end_label))

def emit_loop_statement(stmt, instructions: List[TackyInstruction],symbols:Optional[dict]):
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
        emit_statement(stmt.body, instructions,symbols)
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr(stmt._condition, instructions,symbols)
        instructions.append(TackyJumpIfNotZero(condition=condition_var, target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, While):
        # While Loop: Evaluate condition first
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr(stmt._condition, instructions,symbols)
        instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions,symbols)
        instructions.append(TackyJump(target=continue_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, For):
        # For Loop: Initialization; condition; post; body
        if stmt.init and not isinstance(stmt.init, Null):
            # #print(stmt.init)
            if isinstance(stmt.init,InitDecl):
                emit_statement(stmt.init.declaration, instructions,symbols)
            elif isinstance(stmt.init,InitExp):
                emit_tacky_expr(stmt.init.exp.exp,instructions,symbols)

        instructions.append(TackyLabel(start_label))
        # print(stmt.condition)
        if stmt.condition and not isinstance(stmt.condition, Null):
            condition_var = emit_tacky_expr(stmt.condition, instructions,symbols)
            # print('cv',condition_var)
            # exit()
            instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions,symbols)
        instructions.append(TackyLabel(continue_label))
        if stmt.post and not isinstance(stmt.post, Null):
            emit_tacky_expr(stmt.post, instructions,symbols)
        instructions.append(TackyJump(target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt,Null):
        pass
def emit_s_statement(stmt: S, instructions: List[TackyInstruction],symbols):
    """
    Handles the S statement, which acts as a wrapper for other statements.
    """
    node = stmt.statement
    # #print(node)

    if isinstance(node, Expression):
        #print(node.exp)
        # #print(symbols)
        emit_tacky_expr(node.exp, instructions,symbols)
    elif isinstance(node, If):
        emit_if_statement(node, instructions,symbols)
    elif isinstance(node, Return):
        ret_val = emit_tacky_expr(node.exp, instructions,symbols)
        instructions.append(TackyReturn(val=ret_val))
    elif isinstance(node, Compound):
        for inner_stmt in node.block:
            emit_statement(inner_stmt, instructions,symbols)
    elif isinstance(node, Break):
        loop_id = node.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(node, Continue):
        loop_id = node.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(node, (DoWhile, While, For)):
        emit_loop_statement(node, instructions,symbols)
    elif isinstance(node, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type in S: {type(node)}")

def convert_fun_decl_to_tacky(fun_decl: FunDecl,symbols) -> TackyFunction:

    """
    Converts a single FunDecl AST node (with a body) into a TackyFunction.
    """
    instructions: List[TackyInstruction] = []

    # Gather parameter names
    param_names = [param.name.name for param in fun_decl.params]

    # Convert the function body into TACKY instructions
    # if isinstance(fun_decl.body, Block):
    #     #print(fun_decl.body.block_items)
    if isinstance(fun_decl.body,Null):
        pass
    else: 
        for stmt in fun_decl.body:
            emit_statement(stmt, instructions,symbols)
    # else:
    #     #print('here')
    #     emit_statement(fun_decl.body, instructions)

    # Ensure the function ends with Return(0) if no return statement is present
    # has_return = any(isinstance(instr, TackyReturn) for instr in instructions)
    # if not has_return:
    
    # if fun_decl.name.name=='main':
    instructions.append(TackyReturn(val=TackyConstant(ConstInt(0,exp_type=Int()))))
    
    return TopLevel.tack_func(
        identifier=fun_decl.name.name,
        _global=False,# Function name
        params=fun_decl.params,           # Function parameters
        body=instructions             # Function body instructions
    )

def emit_tacky_program(ast_program: Program,symbols) -> TackyProgram:
    """
    Converts the entire AST Program (which may have multiple functions)
    into a TackyProgram containing multiple TackyFunction definitions.
    """
    tacky_funcs = []

    for fun_decl in ast_program.function_definition:
        if isinstance(fun_decl, FunDecl):
            # Only process if the function has a body (i.e., it's a definition)
            if fun_decl.body is not None and not isinstance(fun_decl.body, Null):
                print(fun_decl)
                # exit()
                t_func = convert_fun_decl_to_tacky(fun_decl,symbols)
                t_func._global=symbols[t_func.name]['attrs'].global_scope
                tacky_funcs.append(t_func)
            # Else, discard declarations that have no body
        else:
            pass 
            # raise TypeError(f"Unsupported top-level node: {type(fun_decl)}")
    # tacky_funcs.append(TackyReturn(0))
    
    instructions=[]
    tacky_symbols=[]
    symbols_new = convert_symbols_to_tacky(symbols)
    # print(symbols_new)
    # exit()
    # for i in symbols_new:
    #     #print(i.init)
    #     i.init=emit_tacky_expr(i.init,instructions,symbols)
    #     tacky_symbols.append(i)
    
    # print(symbols)
    # exit(0)
    # output=emit_tacky_expr(s,instructions)
    # tack_symbols.extend(output)
    # print(symbols)
    # exit()
    tacky_funcs.extend(symbols_new)
    # print('tacky symbols received',symbols)
    # exit()
    return TackyProgram(function_definition=tacky_funcs)

def emit_tacky(program_ast: Program,symbols) :
    """
    High-level function that converts a full AST 'Program' node into a TackyProgram.
    """
    # n_symbols={}
    # print(symbols)
    # exit()
    # exit(program_ast)
    return emit_tacky_program(program_ast,symbols),symbols
