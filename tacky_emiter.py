# emitter.py

from _ast5 import *  # Your high-level AST classes
from tacky import *
from typing import List, Union
from type_classes import *
from typechecker import isSigned
from typechecker import size,size_compound_init,zero_initializer,array_size

def align_offset(offset, alignment):
            return offset - (offset % alignment) if offset % alignment != 0 else offset


# Initialize label counters
temp_false_label = 0
temp_true_label = 0
temp_end_label = 0
temp_e2_label = 0 
temp_const_label=0
def get_const_label()->str:
    global temp_const_label 
    temp_const_label+=1
    return f"const_label.{temp_const_label}"
    
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



    
def no_of_elements(array_type, count=1):    
    """
    Recursively calculates the total number of elements in a multi-dimensional array.
    - Traverses nested arrays to compute total element count.
    - Multiplies dimensions instead of adding them.
    """
    if isinstance(array_type._type, Array):
        return array_type._int.value._int * no_of_elements(array_type._type, count)
    else:
        return array_type._int.value._int 
    
    
def generate_zero_initializer(array_type):
    """
    Recursively generates a ZeroInit for a multi-dimensional array.
    - Calculates the total size by multiplying dimensions.
    - Uses ZeroInit(total_size) to initialize all elements.
    """

    # Base case: If it's a scalar (e.g., Long), return its size
    if isinstance(array_type, Long):
        return size(array_type)

    # Ensure it's an array
    if isinstance(array_type, Array):
        # Compute total size: element count * size of each element
        total_size = array_type._int.value._int * generate_zero_initializer(array_type._type)
        return total_size

    raise ValueError("Unsupported type for ZeroInit")

def convert_symbols_to_tacky(symbols:dict):
    print('Convert symbols to tacky')
    # #symbols)
    # ##symbols)
    tacks_defs=[]
    for name,entry in symbols.items():
        if entry['attrs']!=None:
            if isinstance(entry['attrs'],StaticAttr):
                # #entry['attrs'].init)
                if isinstance(entry['attrs'].init,Initial):
                   
                    init = []
                    for i in entry['attrs'].init.value:
                        if isinstance(i,ZeroInit):
                            init.append(i)
                        elif isinstance(i.value,(IntInit,UIntInit)):
                            init.append(IntInit(i.value.value._int))
                        elif isinstance(i.value,DoubleInit):
                            init.append(DoubleInit(i.value.value._int))
                        else:
                            init.append(LongInit(i.value.value._int))
                            
                    tacks_defs.append(TackyStaticVariable(identifier=name,_global =entry['attrs'].global_scope,_type=entry['val_type'],init=init))
                    # print('after loop')
                    # print(init)
                elif isinstance(entry['attrs'].init,Tentative):
                    init  = []
                    # print('hfuiawhg')
                    if isinstance(entry['val_type'],Array):
                        # print(entry['val_type'])
                        # print(init)
                        array = entry['val_type']
                    
                        _type = size(array._type)
                       
                        ini = no_of_elements(array)
                        
                        init.append(ZeroInit(ini * _type))
                        print(init)
                        # exit()
                    if type(entry['val_type']==type(Long)):
                        init.append(LongInit(0))
                    else:
                        init.append(IntInit(0))
                    tacks_defs.append(TackyStaticVariable(identifier=name,_type=entry['val_type'],_global =entry['attrs'].global_scope,init=init))
                    #tacks_defs)
                  
                else:
                    continue
            else:
                continue
        else:
            continue
    return tacks_defs
                
                
                
            
        
x10=0


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


def is_pointer(_type):
    return isinstance(_type, Pointer)
    


def make_temporary(symbols,var_type,isDouble=None) -> TackyVar:
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    #'Making temp var')
    
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    symbols[name]={
        'val_type':var_type,
        'attrs':LocalAttr(),
        'ret': var_type,
        'Double':isDouble
        
        
    }
    #'Returning temp var')
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


def emit_tacky_expr_and_convert(e, instructions, symbols):
  
    result = emit_tacky_expr(e, instructions,symbols)
    print(result)
    # #'Result :',result)
    if isinstance(result,PlainOperand):
        # exit()
        # #'Returning',result.val)
        return result.val
    elif isinstance(result,DereferencedPointer):
        dst = make_temporary(symbols,e.get_type())
        instructions.append(TackyLoad(result.val, dst))
        # #'Returning pointer def')
        
        return dst
   
    else:
        raise ValueError('Invalid operand',result)

def emit_tacky_expr(expr, instructions: list,symbols:Optional[dict],offset=None) -> Union[TackyConstant, TackyVar]:
    print('EMITTIING EXPR\n', expr,'\n')
    print('Instructions\n',instructions,'\n')
    """
    Generate Tacky IR instructions for a single expression node.
    Returns a 'val' (e.g., TackyConstant or TackyVar) that represents
    the result of the expression in the Tacky IR.
    """
    if isinstance(expr, Constant):
        # #expr)
        if not isinstance(expr.value,(ConstInt,ConstLong,ConstUInt,ConstULong,ConstDouble)):
            return PlainOperand(TackyConstant(expr.value._int))
        return PlainOperand(TackyConstant(expr.value))
    elif isinstance(expr,SingleInit):
        return emit_tacky_expr(expr.exp,instructions,symbols)
    elif isinstance(expr, Var):
        # #expr)
        # exit()
        return PlainOperand(TackyVar(expr.identifier.name))
    elif isinstance(expr, Assignment):
        if isinstance(expr.right,CompoundInit):
            compount_init(expr.right,instructions,symbols,[0],expr.left)
            return 
        else:
            rval = emit_tacky_expr_and_convert(expr.right, instructions,symbols)
        lval=emit_tacky_expr(expr.left,instructions,symbols)
        if isinstance(lval,PlainOperand):
            
            instructions.append(TackyCopy(rval, lval.val))
            return lval
        elif isinstance(lval,DereferencedPointer): 
            instructions.append(TackyStore(rval, lval.val))
            return PlainOperand(rval)
        else:
            # #'Here')
            raise TypeError(f"Unsupported assignment target: {type(expr.left)}")
    elif isinstance(expr, Unary):
        # Handle the Unary case recursively
        src_val = emit_tacky_expr_and_convert(expr.expr, instructions,symbols)
        # #expr)
        # Allocate a new temporary variable for the result
        #expr)
        # exit()
        dst_var = make_temporary(symbols,expr.get_type())
        
        # #expr.get_type())
        # exit()

        # Convert the AST operator (e.g., 'Negate') to a Tacky IR operator
        tacky_op = convert_unop(expr.operator)

        # Append the TackyUnary instruction to the instructions list
        instructions.append(TackyUnary(operator=tacky_op, src=src_val, dst=dst_var))

        return PlainOperand(dst_var)
    elif isinstance(expr, If):
        # The 'If' expression is handled in emit_statement
        raise NotImplementedError("If expressions should be handled in emit_statement.")
    elif isinstance(expr, Conditional):
        # Handle the conditional (ternary) operator
        condition_var = emit_tacky_expr_and_convert(expr.condition, instructions,symbols)
        e2_label = get_e2_label()
        end_label = get_end_label()

        instructions.append(TackyJumpIfZero(condition=condition_var, target=e2_label))

        # True branch
        e1_var = emit_tacky_expr_and_convert(expr.exp2, instructions,symbols)
      
        tmp_result = make_temporary(symbols,expr.get_type())
        
        instructions.append(TackyCopy(source=e1_var, destination=tmp_result))

        instructions.append(TackyJump(target=end_label))
        instructions.append(TackyLabel(e2_label))

        # False branch
        e2_var = emit_tacky_expr_and_convert(expr.exp3, instructions,symbols)
        instructions.append(TackyCopy(source=e2_var, destination=tmp_result))

        instructions.append(TackyLabel(end_label))
        return PlainOperand(tmp_result)
    
    elif isinstance(expr,Cast):      
        print('Inside cast')
        # print(expr)
        # exit()
        result  = emit_tacky_expr_and_convert(expr.exp,instructions,symbols=symbols)
        inner_type = expr.exp._type
        t = expr.target_type
        if isinstance(t,type(inner_type)):
            return PlainOperand(result)
        dst_name = make_temporary(symbols,expr.target_type)
        # #size(Long()))
        # #'Over here',t) 
        # if isinstance(expr.target_type, Pointer) and isinstance(expr.exp._type, Pointer):
        #     dst_name = make_temporary(symbols,expr.target_type)
        #     instructions.append(TackyCopy(result, dst_name))
        #     return PlainOperand(dst_name)
        if isinstance(t,Pointer):
            t=ULong()
        if isinstance(inner_type,Pointer):
            inner_type=ULong()
        if size(t)==size(inner_type):
            print(t)
            print(inner_type)
            # exit()
            instructions.append(TackyCopy(result,dst_name))
        elif size(t) < size(inner_type) and isinstance(inner_type,Double):
            if isSigned(t):
                instructions.append(TackyDoubleToInt(result,dst_name))
            else:
                instructions.append(TackyDoubleToUInt(result,dst_name))
        elif size(t) > size(inner_type) and isinstance(t,Double):
            if isSigned(inner_type):
                instructions.append(TackyIntToDouble(result,dst_name))
            else:
                instructions.append(TackyUIntToDouble(result,dst_name))
        elif size(t)<size(inner_type):
      
            instructions.append(TackyTruncate(result,dst_name))
        elif isSigned(inner_type):
            instructions.append(TackySignExtend(result,dst_name))
        else:
            instructions.append(TackyZeroExtend(result,dst_name))
        #'Returning from cast')
        print('exit cast')
        return PlainOperand(dst_name)
  
    elif isinstance(expr, Binary):
        # exit()
        print('In binary')
        
        if expr.operator in ('And', 'Or'):
            # Short-circuit evaluation for logical operators
            if expr.operator == 'And':
                return emit_and_expr(expr, instructions,symbols)
            elif expr.operator == 'Or':
                return emit_or_expr(expr, instructions,symbols)
        else:
            print('Other operator')
            
            #'here')
            # exit()
    # Determine the types of the left and right operands.
            left_type = expr.left.get_type()
            right_type = expr.right.get_type()
            is_left_ptr = is_pointer(left_type)
            is_right_ptr = is_pointer(right_type)
            # Handle pointer arithmetic: either addition or subtraction
        
            if expr.operator == BinaryOperator.ADD and (is_left_ptr or is_right_ptr):
                print('Here')
                print(is_left_ptr)
                print(expr.right)
                # exit()
                # Ensure the pointer is the first operand.
                if is_left_ptr:
                    pointer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols)
                    integer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols)
                    # print(symbols[integer_operand.identifier])
                    # exit()
                    pointer_type = left_type
                else:
                    integer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols)
                    pointer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols)
                    pointer_type = right_type

                # if array_size(pointer_type.ref)>8:
                #     _size = 8
                # else:
                _size = array_size(pointer_type.ref)
                    # compile-time constant
                # exit()
                dst_var = make_temporary(symbols, expr.get_type(), isDouble=expr.rel_flag)
                instructions.append(TackyAddPtr(ptr=pointer_operand, 
                                            index=integer_operand, 
                                            scale=_size, 
                                            dst=dst_var))
                return PlainOperand(dst_var)

            elif expr.operator == BinaryOperator.SUBTRACT and (is_left_ptr or is_right_ptr):
                # Pointer subtraction cases.
                if is_left_ptr and not is_right_ptr:
                    # Pointer minus integer: negate the integer and use AddPtr.
                    pointer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols)
                    integer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols)
                    pointer_type = left_type
                    # _size = size(pointer_type.ref)
                    
                    _size = array_size(pointer_type.ref)
                    dst_var = make_temporary(symbols, expr.get_type(), isDouble=expr.rel_flag)
                    tmp_neg = make_temporary(symbols, expr.right.get_type())
                    instructions.append(TackyUnary(operator=UnaryOperator.NEGATE, src=integer_operand, dst=tmp_neg))
                    instructions.append(TackyAddPtr(ptr=pointer_operand, 
                                                index=tmp_neg, 
                                                scale=_size, 
                                                dst=dst_var))
                    return PlainOperand(dst_var)

                elif is_left_ptr and is_right_ptr:
                    # Pointer minus pointer: subtract to get byte difference then divide by size.
                    pointer_operand1 = emit_tacky_expr_and_convert(expr.left, instructions, symbols)
                    pointer_operand2 = emit_tacky_expr_and_convert(expr.right, instructions, symbols)
                    pointer_type = left_type  # Both pointers have the same type (type checker ensured this).
                    
                    _size = array_size(pointer_type.ref)
                    dst_var = make_temporary(symbols, expr.get_type(), isDouble=expr.rel_flag)
                    tmp_diff = make_temporary(symbols, expr.get_type())  # temporary for the byte difference
                    instructions.append(TackyBinary(operator=BinaryOperator.SUBTRACT, 
                                                    src1=pointer_operand1, 
                                                    src2=pointer_operand2, 
                                                    dst=tmp_diff))
                    instructions.append(TackyBinary(operator=BinaryOperator.DIVIDE, 
                                                    src1=tmp_diff, 
                                                    src2=_size, 
                                                    dst=dst_var))
                    return PlainOperand(dst_var)

                else:
                    # If an invalid pointer arithmetic case arises, you might raise an error.
                    raise Exception("Invalid pointer arithmetic operation.")
                

            # Fallback: regular binary arithmetic/comparison
            # print(expr.left)
            v1 = emit_tacky_expr_and_convert(expr.left, instructions, symbols)
            # print(v1)
            # exit()
            v2 = emit_tacky_expr_and_convert(expr.right, instructions, symbols)
            dst_var = make_temporary(symbols, expr.get_type(), isDouble=expr.rel_flag)
            tacky_op = convert_binop(expr.operator)
            instructions.append(TackyBinary(operator=tacky_op, src1=v1, src2=v2, dst=dst_var))
          
            return PlainOperand(dst_var)
      
    elif isinstance(expr, FunctionCall):
        # Handle function calls
        # 1. Evaluate each argument
        arg_vals = []
        for arg in expr.args:
            arg_val = emit_tacky_expr_and_convert(arg, instructions,symbols)
            arg_vals.append(arg_val)
        
        # 2. Generate a new temporary to hold the function call's result
        dst_var = make_temporary(symbols,expr.get_type())
        #symbols[dst_var.identifier])
        # exit()
        # #'result of funcall',symbols[dst_var.identifier])
        # #symbols)
        # exit()
        # 3. Emit the TackyFunCall instruction
        instructions.append(TackyFunCall(
            fun_name=expr.identifier.name,  # e.g., "foo"
            args=arg_vals,
            dst=dst_var
        ))
        
        # #'Here')
        # 4. Return the temporary holding the result
        return PlainOperand(dst_var)
    elif isinstance(expr,Dereference):
        result = emit_tacky_expr_and_convert(expr.exp, instructions, symbols)
        #symbols[result.identifier])
        #result)
        # exit()
        return DereferencedPointer(result)
    
    elif isinstance(expr,(IntInit,LongInit,DoubleInit)):
        # #'iofdszh;g')
        return Constant(expr.value)
        # pass 
    elif isinstance(expr,AddOf):
        v = emit_tacky_expr(expr.exp, instructions, symbols)
        if isinstance(v,PlainOperand):
           
            dst = make_temporary(symbols,expr.get_type())
            print(expr)
            # exit()
            instructions.append(TackyGetAddress(v.val, dst))
            return PlainOperand(dst)
        elif isinstance(v,DereferencedPointer):
            return PlainOperand(v.val)
    
    # elif isinstance(expr, Subscript):
    #     # Generate TACKY for a subscript expression: <ptr>[<int>] is equivalent to *(<ptr> + <int>)
        
    #     # 1. Process the array expression to get its pointer value.
    #     base_ptr = emit_tacky_expr_and_convert(expr.exp1, instructions, symbols)
        
    #     # 2. Process the index expression.
    #     # #expr.exp2)
    #     index_val = emit_tacky_expr_and_convert(expr.exp2, instructions, symbols)
    #     # exit()
        
    #     # 3. Compute the scale: the size of the type pointed to by the base pointer.
    #     # This must be computed at compile time.
    #     # #expr.exp1.get_type().ref)
    #     # exit()
    #     scale = size(expr.exp1.get_type())
    #     if scale>8:
    #         scale = 8
    #     else:
    #         scale = scale
    #     # 4. Create a temporary variable to hold the result of the pointer arithmetic.
    #     tmp_ptr = make_temporary(symbols, expr.exp1.get_type())
        
    #     # 5. Emit the AddPtr instruction.
    #     #    This computes: tmp_ptr = base_ptr + index_val * scale
    #     instructions.append(TackyAddPtr(ptr=base_ptr, index=index_val, scale=scale, dst=tmp_ptr))
        
    #     # 6. Return a DereferencedPointer wrapping the pointer computed.
    #     #    If this subscript expression is used as an rvalue (for example, in a Return statement),
    #     #    later code will perform the necessary lvalue conversion (i.e. emit a Load instruction).
    #     return DereferencedPointer(tmp_ptr)
    elif isinstance(expr, Subscript):
        # Generate TACKY for a subscript expression: <ptr>[<int>] is equivalent to *(<ptr> + <int>)
        # print('Subscript expr',expr)
        # print(symbols[expr.exp2.exp.identifier.name])
        # exit()
        # 1. Process the base array expression to get its pointer value.
        base_ptr = emit_tacky_expr_and_convert(expr.exp1, instructions, symbols)

        # 2. Process the index expression to get the index value.
        index_val = emit_tacky_expr_and_convert(expr.exp2, instructions, symbols)

        # 3. Compute the scale factor based on the size of the element type.
        scale = array_size(expr.exp1.get_type())  # Get the size of the element type
        # print(expr._type._int.value._int)
        # exit()
        stride = scale
        print(expr.exp1.get_type())
        print(stride)
        # exit()
        # if stride==8:
        #     print(expr.exp1)
        #     # exit()
        # if isinstance(expr._type,UInt):
        #     exit()
        # exit()
        
        # if isinstance(expr.exp2._type,Array):
        #     stride =scale * expr.exp2._int.value._int  # Ensure correct memory stride for row-major order
       
        # stride = scale 
        # print(expr)
        # print(stride)
        # exit()
        # align_offset(stride,scale)
        # print('\nLeft expression',expr.exp1,'\n')
        # print('\n right expression',expr,'\n')
        
        # print(symbols[base_ptr.identifier])
        # print(symbols[index_val.identifier])
        # print(expr.exp2)
        # print(scale)
        # print(stride)
        # exit()
        # 4. Create a temporary variable for the computed pointer.
        tmp_ptr = make_temporary(symbols, expr.exp1.get_type())
        # exit()
        # 5. Emit the AddPtr instruction to compute the address of arr[index]
        instructions.append(TackyAddPtr(ptr=base_ptr, index=index_val, scale=stride, dst=tmp_ptr))

        # 6. Check if this subscript results in a scalar type.
        # print(symbols[base_ptr.identifier])
        # exit()
        if not isinstance(symbols[base_ptr.identifier]['val_type'],Pointer): 
            # exit() 
            # Lvalue conversion: Load the scalar value from the computed pointer
            tmp_val = make_temporary(symbols,symbols[base_ptr.identifier]['val_type'])
            instructions.append(TackyLoad(src_ptr=tmp_ptr, dst=tmp_val))
            return  PlainOperand(tmp_val)  # Return the loaded value

        # 7. If it's still an array, return the computed pointer directly.
        return DereferencedPointer(tmp_ptr)  # No need to dereference if it's another array

    
    

    else: 
        ##expr)
        raise TypeError(f"Unsupported expression type: {type(expr)}")

def get_type_size(t):
    if isinstance(t, Array):
        return size(t._type) * t._int
    # elif isinstance(t, StructType):
    #     return sum(get_type_size(m) for m in t.members)
    else:  # Primitive types
        return 8 if isinstance(t,Long) else 4  # Example implementation

def emit_and_expr(expr: Binary, instructions: list,symbols) -> TackyVar:
    """
    Emits Tacky instructions for logical 'And' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr_and_convert(expr.left, instructions,symbols)
    false_label = get_false_label()
    end_label = get_end_label()

    # If v1 is zero, jump to false_label
    instructions.append(TackyJumpIfZero(condition=v1, target=false_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr_and_convert(expr.right, instructions,symbols)

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

    return PlainOperand(result_var)

def emit_or_expr(expr: Binary, instructions: list,symbols) -> TackyVar:
    """
    Emits Tacky instructions for logical 'Or' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr_and_convert(expr.left, instructions,symbols)
    true_label = get_true_label()
    end_label = get_end_label()

    # If v1 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v1, target=true_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr_and_convert(expr.right, instructions,symbols)

    # If v2 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v2, target=true_label))

    # Both operands are zero, result is 0
    result_var = make_temporary(symbols,expr.get_type())
    # #result_var)
    # exit()
    instructions.append(TackyCopy(source=TackyConstant(ConstInt(0)), destination=result_var))
    instructions.append(TackyJump(target=end_label))

    # True label: result is 1
    instructions.append(TackyLabel(true_label))
    instructions.append(TackyCopy(source=TackyConstant(ConstInt(1)), destination=result_var))

    # End label
    instructions.append(TackyLabel(end_label))

    return PlainOperand(result_var)

def emit_statement(stmt, instructions: List[TackyInstruction],symbols:Optional[dict]):
    # ##stmt)
    # ##symbols)
    # ##'here')
    
    """
    Emits Tacky instructions for a given statement.
    """
    if isinstance(stmt,list):
        emit_s_statement(stmt,instructions)
    elif isinstance(stmt, If):
        emit_if_statement(stmt, instructions,symbols)
    
    elif isinstance(stmt, Return):
        ret_val = emit_tacky_expr_and_convert(stmt.exp, instructions,symbols)
        instructions.append(TackyReturn(val=ret_val))
    elif isinstance(stmt, (DoWhile, While, For)):
        ##'In Loop')
        ##stmt )
        emit_loop_statement(stmt, instructions,symbols)
        ##'After Loop')
        
    elif isinstance(stmt, D):  # Variable Declaration
        # Handle variable declarations, possibly with initialization
        var_name = stmt.declaration.name.name
        if isinstance(stmt.declaration,FunDecl):
            convert_fun_decl_to_tacky(stmt.declaration,symbols)
        else:
        
            if stmt.declaration.init is not None and not isinstance(stmt.declaration.init, Null) and not isinstance(stmt.declaration.storage_class,Static):
                if isinstance(stmt.declaration.init,CompoundInit):
                    print(stmt.declaration.name)
                    # exit()
                    compount_init(stmt.declaration.init,instructions,symbols,[0],stmt.declaration.name)
                    print('exit compound init')
                    # return
                else:
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
        ##'In compund')
        for inner_stmt in stmt.block:
            emit_statement(inner_stmt, instructions,symbols)
        ##'after compount')
    elif isinstance(stmt, Break):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(stmt, Continue):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(stmt, S):
        ##'Found s statements')
        emit_s_statement(stmt, instructions,symbols)
        ##'After s statements')

    elif isinstance(stmt, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type: {type(stmt)}")

def emit_if_statement(stmt: If, instructions: List[TackyInstruction],symbols):
    #'Inside if')
    """
    Emits Tacky instructions for an If statement.
    """
    condition_var = emit_tacky_expr_and_convert(stmt.exp, instructions,symbols)
    else_label = get_false_label()
    end_label = get_end_label()
    # #condition_var)
    # exit()

    # If condition is zero, jump to else_label
    # #stmt.exp)
    # #symbols[condition_var.identifier])
    # exit()
    instructions.append(TackyJumpIfZero(condition=condition_var, target=else_label))

    # Then branch
    emit_statement(stmt.then, instructions,symbols)
    instructions.append(TackyJump(target=end_label))

    # Else branch
    instructions.append(TackyLabel(else_label))
    if stmt._else and not isinstance(stmt._else, Null):
        emit_statement(stmt._else, instructions,symbols)

    # End label
    #'Exit if',stmt)
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
        condition_var = emit_tacky_expr_and_convert(stmt._condition, instructions,symbols)
        instructions.append(TackyJumpIfNotZero(condition=condition_var, target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, While):
        # While Loop: Evaluate condition first
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr_and_convert(stmt._condition, instructions,symbols)
        instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions,symbols)
        instructions.append(TackyJump(target=continue_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, For):
        # For Loop: Initialization; condition; post; body
        if stmt.init and not isinstance(stmt.init, Null):
            # ##stmt.init)
            if isinstance(stmt.init,InitDecl):
                emit_statement(stmt.init.declaration, instructions,symbols)
            elif isinstance(stmt.init,InitExp):
                emit_tacky_expr(stmt.init.exp.exp,instructions,symbols)

        instructions.append(TackyLabel(start_label))
        # #stmt.condition)
        if stmt.condition and not isinstance(stmt.condition, Null):
            condition_var = emit_tacky_expr_and_convert(stmt.condition, instructions,symbols)
            # #'cv',condition_var)
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
    # ##node)

    if isinstance(node, Expression):
        ##node.exp)
        # ##symbols)
        emit_tacky_expr(node.exp, instructions,symbols)
    elif isinstance(node, If):
        #node)
        emit_if_statement(node, instructions,symbols)
    elif isinstance(node, Return):
        ret_val = emit_tacky_expr_and_convert(node.exp, instructions,symbols)
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


# def compount_init(expr, instructions, symbols,offset,name):
#     # print('inside compound init')
#     if isinstance(expr, CompoundInit):
          
#             # Generate TACKY for a compound initializer.
#             # Each scalar expression in the initializer is evaluated and copied to the appropriate memory location with a CopyToOffset instruction.
            
#             # 1. Initialize the offset to zero.
#             for element in expr.initializer:
#                 #element)
#                 # exit()
#                 # # 2a. Check if the element is a scalar expression.
#                 if isinstance(element,SingleInit):
                 
#                     # 2a.i. Evaluate the scalar expression.
#                     scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols)
                    
#                     # 2a.ii. Compute the size of the scalar's type (in bytes) at compile time.
#                     # print(element.exp._type)
#                     # exit()
#                     print('ERROR HERE')
#                     print('ELEMENT:',element)
#                     # 2a.iii. Emit a CopyToOffset instruction.
#                     # This copies the evaluated scalar to the destination memory at the current offset.
#                     # if not isinstance(elem_size,):
#                     elem_size =size_compound_init(element.exp._type)
                    
#                     offset[0] =  align_offset(offset[0], elem_size) 
#                     offset[0] +=  elem_size
                        
#                     instructions.append(TackyCopyToOffSet(src=scalar_val, dst=name, offset=offset[0]))
                    
#                     # if not isinstance(elem_size,(Pointer,Array)):
#                     # 2a.iv. Update the offset for the next element.
                
#                 # 2b. Otherwise, if the element is itself a compound initializer (e.g., for multidimensional arrays),
#                 # recursively process its elements.
#                 elif isinstance(element,CompoundInit):
#                     # process_compound_initializer is assumed to recursively handle nested initializers.
#                     compount_init(element, instructions, symbols,offset,name)
           
     
    
def compount_init(expr, instructions, symbols, offset, name):
    if isinstance(expr, CompoundInit):
        for element in expr.initializer:
            if isinstance(element, SingleInit):
                # Evaluate the scalar expression
                scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols)
                
                # Get element type, size, and alignment
                elem_type = element.exp._type
                elem_size = size_compound_init(elem_type)
                # elem_alignment = get_alignment(elem_type)  # Replace with your alignment logic
                
                # Align the current offset to the element's alignment requirement
                # offset[0] = align_offset(offset[0], elem_size)
                
                # Emit CopyToOffset at the aligned offset
                instructions.append(TackyCopyToOffSet(src=scalar_val, dst=name, offset=offset[0]))
                offset[0] += elem_size
                
                # Increment offset by the element's size
                print(offset)
               
                
                
            elif isinstance(element, CompoundInit):
                # Recursively process nested compound initializer
                compount_init(element, instructions, symbols, offset, name)




def convert_fun_decl_to_tacky(fun_decl: FunDecl,symbols) -> TackyFunction:

    """
    Converts a single FunDecl AST node (with a body) into a TackyFunction.
    """
    instructions: List[TackyInstruction] = []

    # Gather parameter names
    param_names = [param.name.name for param in fun_decl.params]

    # Convert the function body into TACKY instructions
    # if isinstance(fun_decl.body, Block):
    #     ##fun_decl.body.block_items)
    if isinstance(fun_decl.body,Null):
        pass
    else: 
        for stmt in fun_decl.body:
            print('Statment being processed',stmt)
            emit_statement(stmt, instructions,symbols)
    # else:
    #     ##'here')
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
                #fun_decl)
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
    #symbols)
    # exit()
    # for i in symbols_new:
    #     ##i.init)
    #     i.init=emit_tacky_expr(i.init,instructions,symbols)
    #     tacky_symbols.append(i)
    
    # #symbols)
    # exit(0)
    # output=emit_tacky_expr(s,instructions)
    # tack_symbols.extend(output)
    # #symbols)
    # exit()
    tacky_funcs.extend(symbols_new)
    # #'tacky symbols received',symbols)
    # exit()
    return TackyProgram(function_definition=tacky_funcs)

def emit_tacky(program_ast: Program,symbols) :
    """
    High-level function that converts a full AST 'Program' node into a TackyProgram.
    """
    # n_symbols={}
    # #symbols)
    # exit()
    # exit(program_ast)
    return emit_tacky_program(program_ast,symbols),symbols
