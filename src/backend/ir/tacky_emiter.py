# emitter.py

from src.frontend.parser._ast5 import *  # Your high-level AST classes
from src.backend.ir.tacky import *
from typing import List, Union
from src.backend.typechecker.type_classes import *
from src.backend.typechecker.typechecker import isSigned
from src.backend.typechecker.typechecker import size,size1,size_compound_init,zero_initializer,array_size

def align_offset(offset, alignment):
            return offset - (offset % alignment) if offset % alignment != 0 else offset




# Initialize label counters
temp_false_label = 0
temp_true_label = 0
temp_end_label = 0
temp_e2_label = 0 
temp_const_label=0
temp_str_label=0
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

def get_string_label()->str:
    global temp_str_label
    
    temp_str_label +=1
    return f'string.{temp_str_label}'

    

def make_temporary_var() -> Var:
    """
    Generate a fresh temporary variable name each time we call it,
    e.g., "tmp.0", "tmp.1", etc.
    """
    global temp_counter
    name = f"tmp.{temp_counter}"
    temp_counter += 1
    return name

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
    
    
# def generate_zero_initializer(array_type):
#     """
#     Recursively generates a ZeroInit for a multi-dimensional array.
#     - Calculates the total size by multiplying dimensions.
#     - Uses ZeroInit(total_size) to initialize all elements.
#     """

#     # Base case: If it's a scalar (e.g., Long), return its size
#     if isinstance(array_type, Long):
#         return size(array_type)

#     # Ensure it's an array
#     if isinstance(array_type, Array):
#         # Compute total size: element count * size of each element
#         total_size = array_type._int.value._int * generate_zero_initializer(array_type._type)
#         return total_size

    # raise ValueError("Unsupported type for ZeroInit")

def get_array_type_size(t):
    if isinstance(t,(Char,UChar,SChar)):
        return 1 
    if isinstance(t,(Long,ULong,Double)):
        return 8 
    if isinstance(t,(Int,UInt)):
        return 4 
    if isinstance(t,Array):
        return get_array_type_size(t._type)
    if isinstance(t,Pointer):
        return 8 

def convert_symbols_to_tacky(symbols:dict):
    # print('Convert symbols to tacky')
    # #symbols)
    ##symbols)
    # print(symbols)
    # exit()
    tacks_defs=[]
    for name,entry in symbols.items():
        if entry['attrs']!=None:
            print(entry['attrs'])
            # exit()
            if isinstance(entry['attrs'],StaticAttr):
                # #entry['attrs'].init)
                if isinstance(entry['attrs'].init,Initial):
                    init = []
                    print(entry['attrs'].init)
                    # exit()
                    for i in entry['attrs'].init.value:
                        if isinstance(i,(StringInit,PointerInit)):
                            if isinstance(i,StringInit):
                               
                                string_val = i.string 
                                decoded_string = i.string.encode().decode('unicode_escape')
                                print(decoded_string)
                                # exit()
                                i.string = decoded_string
                            init.append(i)
                        elif isinstance(i,(ZeroInit)):
                            init.append(i)
                        elif isinstance(i.value,(IntInit,UIntInit)):
                            init.append(IntInit(i.value.value._int))
                        elif isinstance(i.value,DoubleInit):
                            init.append(DoubleInit(i.value.value._int))
                        elif isinstance(i.value,CharInit):
                            init.append(CharInit(i.value.value._int))
                           
                        elif isinstance(i.value,UCharInit):
                            init.append(UCharInit(i.value.value._int))
                        elif isinstance(i.value,LongInit):
                            init.append(LongInit(i.value.value._int))
                        elif isinstance(i.value,ULongInit):
                            init.append(ULongInit(i.value.value._int))
                        else :
                            raise TypeError('UNKNOWN SYMBOL TYPE',i.value)
                            
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
                    
                        _type = get_array_type_size(array._type)
                       
                        ini = no_of_elements(array)
                        print(ini)
                        print(_type)
                        init.append(ZeroInit(ini * _type))
                        print(init)
                        # exit()
                    if type(entry['val_type'])==type(Long):
                        init.append(LongInit(0))
                    else:
                        init.append(IntInit(0))
                    tacks_defs.append(TackyStaticVariable(identifier=name,_type=entry['val_type'],_global =entry['attrs'].global_scope,init=init))
            
            elif isinstance(entry['attrs'],ConstantAttr):
                # exit()
                
                tacks_defs.append(TackyStaticConstant(identifier=name,_type=entry['val_type'],init=entry['attrs'].init))
                
                
     
    return tacks_defs
                
                
                
            
        
x10=0


# A global counter for generating unique temporary names
temp_counter = 0
# temp_counter1 = 0





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


def emit_tacky_expr_and_convert(e, instructions, symbols,type_table):
    print('conversion got type table', type_table is not None)
    # print(e)
    # if type_table is None:
    #     exit()
    # print(type_table)
    print('expression to convert ',e)
    
    result = emit_tacky_expr(e, instructions,symbols,type_table)
    print('result',result)
    if isinstance(result,PlainOperand):
        return result.val
    elif isinstance(result,DereferencedPointer):
        dst = make_temporary(symbols,e.get_type())
        instructions.append(TackyLoad(result.val, dst))
        # #'Returning pointer def')
        
        return dst
    elif isinstance(result,SubObject):
        dst = make_temporary(symbols,e.get_type())
        instructions.append(TackyCopyFromOffSet(result.base, result.offset, dst))
        return dst
    elif isinstance(result,Null):
        pass 
    else:
        raise ValueError('Invalid operand',result)


def emit_char_Array(exp,instructions,symbols):
    # exit()
    print('EXPRESSION',exp.declaration.init.exp)
    for i in exp.declaration.init.exp.string:
        import ast
        try:
            print('Error in emit char array')
            # Use ast.literal_eval to properly interpret escape sequences
            decoded_string = ast.literal_eval(f'{i}')
        except (ValueError, SyntaxError):
            # Fallback if literal_eval fails
            decoded_string = i.encode().decode('unicode-escape')
        
        val = ord(decoded_string)
        instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(val)),dst = exp.declaration.name.name,offset=1))
    instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(0)),dst = exp.declaration.name.name,offset=1))
 
def is_void(t):
    if isinstance(t,Void):
        return True
    if isinstance(t,Pointer):
        return is_void(t.ref)
    if isinstance(t,Array):
        return is_void(t._type)
    return False
      
def emit_tacky_expr(expr, instructions: list,symbols:Optional[dict],type_table) -> Union[TackyConstant, TackyVar]:
  
    """
    Generate Tacky IR instructions for a single expression node.
    Returns a 'val' (e.g., TackyConstant or TackyVar) that represents
    the result of the expression in the Tacky IR.
    """
    if isinstance(expr, Constant):
      
        if not isinstance(expr.value,(ConstInt,ConstLong,ConstUInt,ConstULong,ConstDouble,ConstUChar,ConstChar)):
            return PlainOperand(TackyConstant(expr.value._int))
    
        
        return PlainOperand(TackyConstant(expr.value))
    elif isinstance(expr,SingleInit):
        # exit()
      
        return emit_tacky_expr(expr.exp,instructions,symbols,type_table)   
    elif isinstance(expr, Var):
        # #expr)
        # exit()
        return PlainOperand(TackyVar(expr.identifier.name))
    elif isinstance(expr, Assignment):
        # print('assignment',expr)
        print('assignment expression got type table',type_table is not None)
       
        
        if isinstance(expr.right,CompoundInit):
            print('going into assignment compount init')
            compount_init(expr.right,instructions,symbols,[0],expr.left,type_table)
            print('after asignment compount init')
            return 
        else:
            
            rval = emit_tacky_expr_and_convert(expr.right, instructions,symbols,type_table)
            
        lval=emit_tacky_expr(expr.left,instructions,symbols,type_table)
        if isinstance(lval,SubObject):
            instructions.append(TackyCopyToOffSet(rval,lval.base,lval.offset))
            return PlainOperand(rval)
        elif isinstance(lval,PlainOperand):
            
            instructions.append(TackyCopy(rval, lval.val))
            return lval
        elif isinstance(lval,DereferencedPointer): 
   
            instructions.append(TackyStore(rval, lval.val))
            return PlainOperand(rval)
        else:
           
            raise TypeError(f"Unsupported assignment target: {type(expr.left)}")
    elif isinstance(expr, Unary):
        # Handle the Unary case recursively
        src_val = emit_tacky_expr_and_convert(expr.expr, instructions,symbols,type_table)
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
        # The 'If' expression is handled in emit_stateme,type_tablent
        raise NotImplementedError("If expressions should be handled in emit_statement.,type_table",type_table)
    elif isinstance(expr, Conditional):
        # Handle the conditional (ternary) operator
        condition_var = emit_tacky_expr_and_convert(expr.condition, instructions,symbols,type_table)
        e2_label = get_e2_label()
        end_label = get_end_label()

        instructions.append(TackyJumpIfZero(condition=condition_var, target=e2_label))
     
        if isinstance(expr.get_type(),Void):
            
            emit_tacky_expr_and_convert(expr.exp2, instructions, symbols,type_table)
            instructions.extend(
                [ TackyJump(end_label),
                TackyLabel(e2_label) ])
            emit_tacky_expr_and_convert(expr.exp3, instructions, symbols,type_table)
            instructions.append(TackyLabel(end_label))
            return PlainOperand(TackyVar("DUMMY"))
        else:
        # True branch
            e1_var = emit_tacky_expr_and_convert(expr.exp2, instructions,symbols,type_table)
        
            tmp_result = make_temporary(symbols,expr.get_type())
            
            instructions.append(TackyCopy(source=e1_var, destination=tmp_result))

            instructions.append(TackyJump(target=end_label))
            instructions.append(TackyLabel(e2_label))

            # False branch
            e2_var = emit_tacky_expr_and_convert(expr.exp3, instructions,symbols,type_table)
            instructions.append(TackyCopy(source=e2_var, destination=tmp_result))

            instructions.append(TackyLabel(end_label))
            return PlainOperand(tmp_result) 
    elif isinstance(expr,Cast):      
      
        result  = emit_tacky_expr_and_convert(expr.exp,instructions,symbols=symbols,type_table=type_table)
        if isinstance(expr._type,Void):
            return PlainOperand(TackyVar('DUMMY'))
            
        inner_type = expr.exp._type
        
        t = expr.target_type
        
        if isinstance(t,ULong) and isinstance(expr.exp,Constant):
            print(expr)
            # exit()
   
        if isinstance(t,type(inner_type)):
            return PlainOperand(result)
        dst_name = make_temporary(symbols,expr.target_type)
 
        if isinstance(expr.target_type, Array) and isinstance(expr.exp._type, Pointer):
            # if isinstance(expr.target_type._type,type(expr.exp._type.ref)):
                return DereferencedPointer(result)
        if isinstance(expr.target_type,Pointer) and isinstance(expr.exp._type, Array):
            # if isinstance(expr.target_type._type,type(expr.exp._type.ref)):
                return DereferencedPointer(result)
        
        if isinstance(t,Pointer):
            t=ULong()
        if isinstance(inner_type,Pointer):
            inner_type=ULong()
        if size(t)==size(inner_type):
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
   
        return PlainOperand(dst_name) 
    elif isinstance(expr, Binary):
        # exit()
        print('In binary')
        
        if expr.operator in ('And', 'Or'):
            # Short-circuit evaluation for logical operators
            if expr.operator == 'And':
                return emit_and_expr(expr, instructions,symbols,type_table)
            elif expr.operator == 'Or':
                return emit_or_expr(expr, instructions,symbols,type_table)
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
                    pointer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols,type_table)
                    integer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols,type_table)
                    # print(symbols[integer_operand.identifier])
                    # exit()
                    pointer_type = left_type
                else:
                    integer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols,type_table)
                    pointer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols,type_table)
                    pointer_type = right_type

                # if array_size(pointer_type.ref)>8:
                #     _size = 8
                # else:
                _size = array_size(pointer_type.ref,type_table)
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
                    pointer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols,type_table)
                    integer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols,type_table)
                    pointer_type = left_type
                    # _size = size(pointer_type.ref)
                    
                    _size = array_size(pointer_type.ref,type_table)
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
                    pointer_operand1 = emit_tacky_expr_and_convert(expr.left, instructions, symbols,type_table)
                    pointer_operand2 = emit_tacky_expr_and_convert(expr.right, instructions, symbols,type_table)
                    pointer_type = left_type  # Both pointers have the same type (type checker ensured this).
                    
                    _size = array_size(pointer_type.ref,type_table)
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
                

           
            v1 = emit_tacky_expr_and_convert(expr.left, instructions, symbols,type_table)
            
            
            v2 = emit_tacky_expr_and_convert(expr.right, instructions, symbols,type_table)
            dst_var = make_temporary(symbols, expr.get_type(), isDouble=expr.rel_flag)
            tacky_op = convert_binop(expr.operator)
            instructions.append(TackyBinary(operator=tacky_op, src1=v1, src2=v2, dst=dst_var))

          
            return PlainOperand(dst_var) 
    elif isinstance(expr, FunctionCall):
        print('Handling function calls')
        # Handle function calls
        # 1. Evaluate each argument
        arg_vals = []
        for arg in expr.args:
            # print(arg)
           
            arg_val = emit_tacky_expr_and_convert(arg, instructions,symbols,type_table)
            arg_vals.append(arg_val)
        
        # 2. Generate a new temporary to hold the function call's result
        dst_var = Null()
        # print(symbols[expr.identifier.name])
        
        if not isinstance(symbols[expr.identifier.name]['fun_type'].base_type,Void):
        # if not isinstance(expr._type,Void):
            dst_var = make_temporary(symbols,expr.get_type())
            instructions.append(TackyFunCall(
            fun_name=expr.identifier.name,  # e.g., "foo"
            args=arg_vals,
            dst=dst_var
        ))
        
        # #'Here')
        # 4. Return the temporary holding the result
            print('exit function call')
            return PlainOperand(dst_var)
        else:
            instructions.append(TackyFunCall(
            fun_name=expr.identifier.name,  # e.g., "foo"
            args=arg_vals,
            dst=dst_var))
            # exit()
            print('exit function call')
            
            return Null()
     
    elif isinstance(expr,Dereference):
        result = emit_tacky_expr_and_convert(expr.exp, instructions, symbols,type_table)
        #symbols[result.identifier])
        #result)
        # exit()
        return DereferencedPointer(result) 
    elif isinstance(expr,(IntInit,LongInit,DoubleInit)):
        # #'iofdszh;g')
        return Constant(expr.value)
        # pass 
    elif isinstance(expr,AddOf):
        print('Handling address of',expr.exp)
        v = emit_tacky_expr(expr.exp, instructions, symbols,type_table)
        # exit()
        # print(v)
        if isinstance(v,SubObject):
            dst = make_temporary(symbols,expr.get_type())
            instructions.append(TackyGetAddress(v.base, dst))
            instructions.append(TackyAddPtr(ptr=dst,index=TackyConstant(ConstLong(v.offset)),scale=1,dst=dst))
            return PlainOperand(dst)
        elif isinstance(v,PlainOperand):
           
            dst = make_temporary(symbols,expr.get_type())
           
            instructions.append(TackyGetAddress(v.val, dst))
            return PlainOperand(dst)
        elif isinstance(v,DereferencedPointer):
            return PlainOperand(v.val)
        
        
    elif isinstance(expr, Subscript):
        print('subscript expression',type_table is None)
        # 1. Process the base array expression to get its pointer value.
        base_ptr = emit_tacky_expr_and_convert(expr.exp1, instructions, symbols,type_table)

        # 2. Process the index expression to get the index value.
        index_val = emit_tacky_expr_and_convert(expr.exp2, instructions, symbols,type_table)

        # 3. Compute the scale factor based on the size of the element type.  
        
     
        if isinstance(expr.exp1.get_type(),(Pointer)):
            tmp_ptr = make_temporary(symbols, expr.exp1.get_type())
            stride = array_size(expr.exp1.get_type(),type_table)  # Get the size of the element type
            
            print('Stride',stride)
            # exit()
            if isinstance(expr.exp1.get_type(),(Char,UChar,SChar)):
                stride = 1
            instructions.append(TackyAddPtr(ptr=base_ptr, index=index_val, scale=stride, dst=tmp_ptr))
            if not isinstance(symbols[base_ptr.identifier]['val_type'],(Pointer,Array)): 
                
                
                # Lvalue conversion: Load the scalar value from the computed pointer
                tmp_val = make_temporary(symbols,symbols[base_ptr.identifier]['val_type'])
                instructions.append(TackyLoad(src_ptr=tmp_ptr, dst=tmp_val))
                return  PlainOperand(tmp_val)  # Return the loaded value

        else:
            tmp_ptr = make_temporary(symbols, expr.exp2.get_type())
            stride = array_size(expr.exp2.get_type(),type_table)  # Get the size of the element type
            if isinstance(expr.exp1.get_type(),(Char,UChar,SChar)):
                stride = 1
            instructions.append(TackyAddPtr(ptr=index_val, index=base_ptr, scale=stride, dst=tmp_ptr))
            if not isinstance(symbols[index_val.identifier]['val_type'],(Pointer,Array)): 
                # Lvalue conversion: Load the scalar value from the computed pointer
                tmp_val = make_temporary(symbols,symbols[index_val.identifier]['val_type'])
                instructions.append(TackyLoad(src_ptr=tmp_ptr, dst=tmp_val))
                return  PlainOperand(tmp_val)  # Return the loaded value

            
     
        # 7. If it's still an array, return the computed pointer directly.
        return DereferencedPointer(tmp_ptr)  # No need to dereference if it's another array
    elif isinstance(expr,String):
        print(expr._type)
        # exit()
        temp_str = get_string_label()
        # #expr.string)
        import ast
      
            # Use ast.literal_eval to properly interpret escape sequences
        # decoded_string = ast.literal_eval(expr.string)
        
        #     # decoded_string = unescape_c_string(expr.string)
        # decoded_string = expr.string.encode().decode('unicode_escape')
        # # print(decoded_string)
        # # for char in expr.string:
            
        # #    char = char.encode().decode('latin1')
               
        # expr.string = decoded_string
        print('String',expr.string)
        # exit()
        symbols[temp_str] = {
            'val_type':expr._type,
            'attrs':ConstantAttr(StringInit(string=expr.string,null_terminated=True)),
            'isDouble':False,
            'ret':expr._type
        }
        
        # exit()
        temp_dst = make_temporary(symbols,expr._type)
        instructions.append(TackyGetAddress(src=TackyVar(temp_str),dst = temp_dst))
        
        
        #! CAN BE WRONG
        return DereferencedPointer(temp_dst)
    elif isinstance(expr,SizeOf):
        t = expr.exp.get_type()
        print('t',t)        # exit()
        result  = size(t,type_table)
        if isinstance(expr.exp.get_type(),Double):
            result = 8
        # exit()
        return PlainOperand(TackyConstant(ConstULong(result)))
    elif isinstance(expr,SizeOfT):
        
        result  = size(expr.exp,type_table)
        if isinstance(expr.exp,Double):
            result = 8
        print(result)
        print(expr.exp)
        # exit()
        return PlainOperand(TackyConstant(ConstULong(result)))
    elif isinstance(expr,Null):
        return Null() 
    elif isinstance(expr,Dot):
        print('Handling dot expression')
        print('type table in dot',type_table)
        # print(expr.structure._type)
        struct_def:StructEntry = type_table[expr.structure._type.tag]
        
        member_offset = 0
        
        for i in struct_def.members:
            p:MemberEntry=i 
            if p.member_name.name ==expr.member.name:
                member_offset = p.offset 
        inner_object = emit_tacky_expr(expr.structure,instructions,symbols,type_table)        
        if isinstance(inner_object,PlainOperand):
            return SubObject(inner_object.val,member_offset)
        elif isinstance(inner_object,SubObject):
            return SubObject(inner_object.base,inner_object.offset+member_offset)
        elif isinstance(inner_object,DereferencedPointer):
                dst_ptr = make_temporary(symbols,Pointer(expr.get_type()))
                instr = TackyAddPtr(ptr=inner_object.val, index=TackyConstant(ConstLong(member_offset)),scale=1, dst=dst_ptr)
                instructions.append(instr)
                return DereferencedPointer(dst_ptr)
        else:
            raise TypeError('invalid expression in dot')                 
    
    if isinstance(expr,Arrow):
        # e is assumed to be something like Arrow(ptr_expr, member_name)
        ptr_expr, member_name = expr.pointer, expr.member

        # Look up the structure type pointed to
        ptr_type = ptr_expr._type
        
       
        print(ptr_type.ref)
        # exit()
        struct_type = ptr_type.ref  # e.g., struct inner for struct inner*

        # Look up member offset
        struct_def = type_table.get(struct_type.tag)
        for i in struct_def.members :
            if member_name.name == i.member_name.name:
                #  exit()
                member_offset = i.offset

        # Generate code to evaluate the pointer expression
        ptr = emit_tacky_expr_and_convert(ptr_expr, instructions, symbols,type_table)

        # Optimization: skip AddPtr if offset is 0
        if member_offset == 0:
            return DereferencedPointer(ptr)

        dst_ptr = make_temporary(symbols,expr.get_type())
        instructions.append(TackyAddPtr(ptr=ptr,
                                index=TackyConstant(ConstLong(member_offset)),
                                scale=1,
                                dst=dst_ptr))
        return DereferencedPointer(dst_ptr)

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

def emit_and_expr(expr: Binary, instructions: list,symbols,type_table) -> TackyVar:
    """
    Emits Tacky instructions for logical 'And' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr_and_convert(expr.left, instructions,symbols,type_table)
    false_label = get_false_label()
    end_label = get_end_label()

    # If v1 is zero, jump to false_label
    instructions.append(TackyJumpIfZero(condition=v1, target=false_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr_and_convert(expr.right, instructions,symbols,type_table)

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

def emit_or_expr(expr: Binary, instructions: list,symbols,type_table) -> TackyVar:
    """
    Emits Tacky instructions for logical 'Or' expressions with short-circuit evaluation.
    """
    v1 = emit_tacky_expr_and_convert(expr.left, instructions,symbols,type_table)
    true_label = get_true_label()
    end_label = get_end_label()

    # If v1 is non-zero, jump to true_label
    instructions.append(TackyJumpIfNotZero(condition=v1, target=true_label))

    # Evaluate the second operand
    v2 = emit_tacky_expr_and_convert(expr.right, instructions,symbols,type_table)

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

def emit_statement(stmt, instructions: List[TackyInstruction],symbols:Optional[dict],type_table):
    # ##stmt)
    # ##symbols)
    # ##'here')
    
    """
    Emits Tacky instructions for a given statement.
    """
    if isinstance(stmt,list):
        emit_s_statement(stmt,instructions,type_table)
    elif isinstance(stmt, If):
        emit_if_statement(stmt, instructions,symbols,type_table)
    
    elif isinstance(stmt, Return):
      
        if isinstance(stmt.exp,Null):
          
            instructions.append(TackyReturn(val=Null()))
        else:
            # exit()
            ret_val = emit_tacky_expr_and_convert(stmt.exp, instructions,symbols,type_table)
            instructions.append(TackyReturn(val=ret_val))
            
    elif isinstance(stmt, (DoWhile, While, For)):
        ##'In Loop')
        ##stmt )
        emit_loop_statement(stmt, instructions,symbols,type_table)
        ##'After Loop')
        
    elif isinstance(stmt, D):  # Variable Declaration
        # Handle variable declarations, possibly with initialization
        
        print('D got type table',type_table is not None)
        print(stmt.declaration)
        # print(type_table)
        
        # var_name = stmt.declaration.name.name
        if isinstance(stmt.declaration,FunDecl):
            convert_fun_decl_to_tacky(stmt.declaration,symbols,type_table)
        else:
            if isinstance(stmt.declaration,StructDecl):
                return 
            if stmt.declaration.init is not None and not isinstance(stmt.declaration.init, Null) and not isinstance(stmt.declaration.storage_class,Static):
                # exit()
                if isinstance(stmt.declaration.init,SingleInit) and isinstance(stmt.declaration.init._type,(Array)) :
                  
                    compount_init(stmt.declaration.init,instructions,symbols,[0],stmt.declaration.name,type_table)
                    
                    return
                elif isinstance(stmt.declaration.init,CompoundInit):
                    
                    compount_init(stmt.declaration.init,instructions,symbols,[0],stmt.declaration.name,type_table)
                  
                
                else:
                 
                # Emit assignment to initialize the variable
                    assign_expr = Assignment(
                        left=Var(stmt.declaration.name),
                        right=stmt.declaration.init
                    )
                    # print(type_table)
                    
                    emit_tacky_expr_and_convert(assign_expr, instructions,symbols,type_table=type_table)
                   
        # Else, no initialization needed
    elif isinstance(stmt, Expression):
        emit_tacky_expr(stmt.exp, instructions,symbols,type_table)
    elif isinstance(stmt, Compound):
        ##'In compund')
        for inner_stmt in stmt.block:
            emit_statement(inner_stmt, instructions,symbols,type_table)
        ##'after compount')
    elif isinstance(stmt, Break):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(stmt, Continue):
        loop_id = stmt.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(stmt, S):
        ##'Found s statements')
        emit_s_statement(stmt, instructions,symbols,type_table)
        ##'After s statements')
    elif isinstance(stmt, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type: {type(stmt)}")

def emit_if_statement(stmt: If, instructions: List[TackyInstruction],symbols,type_table):
    # print(stmt)
    # exit()
    #'Inside if')
    """
    Emits Tacky instructions for an If statement.
    """
    condition_var = emit_tacky_expr_and_convert(stmt.exp, instructions,symbols,type_table)
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
    emit_statement(stmt.then, instructions,symbols,type_table)
    instructions.append(TackyJump(target=end_label))

    # Else branch
    instructions.append(TackyLabel(else_label))
    if stmt._else and not isinstance(stmt._else, Null):
        emit_statement(stmt._else, instructions,symbols,type_table)

    # End label
    #'Exit if',stmt)
    instructions.append(TackyLabel(end_label))

def emit_loop_statement(stmt, instructions: List[TackyInstruction],symbols:Optional[dict],type_table):
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
        emit_statement(stmt.body, instructions,symbols,type_table)
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr_and_convert(stmt._condition, instructions,symbols,type_table)
        instructions.append(TackyJumpIfNotZero(condition=condition_var, target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, While):
        # While Loop: Evaluate condition first
        instructions.append(TackyLabel(continue_label))
        condition_var = emit_tacky_expr_and_convert(stmt._condition, instructions,symbols,type_table)
        instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions,symbols,type_table)
        instructions.append(TackyJump(target=continue_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt, For):
        # For Loop: Initialization; condition; post; body
        if stmt.init and not isinstance(stmt.init, Null):
            # ##stmt.init)
            if isinstance(stmt.init,InitDecl):
                emit_statement(stmt.init.declaration, instructions,symbols,type_table)
            elif isinstance(stmt.init,InitExp):
                emit_tacky_expr(stmt.init.exp.exp,instructions,symbols,type_table)

        instructions.append(TackyLabel(start_label))
        # #stmt.condition)
        if stmt.condition and not isinstance(stmt.condition, Null):
            condition_var = emit_tacky_expr_and_convert(stmt.condition, instructions,symbols,type_table)
            # #'cv',condition_var)
            # exit()
            instructions.append(TackyJumpIfZero(condition=condition_var, target=break_label))
        emit_statement(stmt.body, instructions,symbols,type_table)
        instructions.append(TackyLabel(continue_label))
        if stmt.post and not isinstance(stmt.post, Null):
            emit_tacky_expr(stmt.post, instructions,symbols,type_table)
        instructions.append(TackyJump(target=start_label))
        instructions.append(TackyLabel(break_label))
    elif isinstance(stmt,Null):
        pass

def emit_s_statement(stmt: S, instructions: List[TackyInstruction],symbols,type_table):
    """
    Handles the S statement, which acts as a wrapper for other statements.
    """
    node = stmt.statement
    # ##node)

    if isinstance(node, Expression):
        ##node.exp)
        # ##symbols)
        emit_tacky_expr(node.exp, instructions,symbols,type_table)
    elif isinstance(node, If):
        #node)
        emit_if_statement(node, instructions,symbols,type_table)
    elif isinstance(node, Return):
        if isinstance(node.exp,Null):
            instructions.append(TackyReturn(TackyVar("DUMMY")))
        else:
            ret_val = emit_tacky_expr_and_convert(node.exp, instructions,symbols,type_table)
            # print(node.exp)
            # print(ret_val)
            # exit()
            instructions.append(TackyReturn(val=ret_val))
    elif isinstance(node, Compound):
        for inner_stmt in node.block:
            emit_statement(inner_stmt, instructions,symbols,type_table)
    elif isinstance(node, Break):
        loop_id = node.label
        instructions.append(TackyJump(target=f"break_{loop_id}"))
    elif isinstance(node, Continue):
        loop_id = node.label
        instructions.append(TackyJump(target=f"continue_{loop_id}"))
    elif isinstance(node, (DoWhile, While, For)):
        emit_loop_statement(node, instructions,symbols,type_table)
    elif isinstance(node, Null):
        pass  # No operation for Null statements
    else:
        raise TypeError(f"Unsupported statement type in S: {type(node)}")



def compount_init(expr, instructions, symbols, offset, name,type_table):
  
    if isinstance(expr, CompoundInit):
        for element in expr.initializer:
            # exit()
            if isinstance(element,SingleInit) and isinstance(element.exp,String):
              
                count = 0
                for i in element.exp.string:
                    if isinstance(i,CompoundInit):
                        
                        compount_init(i, instructions, symbols, offset, name,type_table)
                
                    import ast
                    try:
                        print('Error in compound init')
                        # Use ast.literal_eval to properly interpret escape sequences
                        decoded_string = ast.literal_eval(f'{i}')
                    except (ValueError, SyntaxError):
                        # Fallback if literal_eval fails
                        decoded_string = i.encode().decode('unicode-escape')
                        print(decoded_string)
                    val = ord(str(decoded_string))
                    instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(val)),dst =name,offset=offset[0]))
                    # i+=1
                    count+=1
                    elem_size = 1
                    offset[0] += elem_size
                    print(element)
                    # exit()
                while count < element._type._int.value._int:
                    
                    instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(0)),dst =name,offset=offset[0]))
                    elem_size = 1
                    
                    offset[0] += elem_size
                    count+=1
                
            elif isinstance(element, SingleInit):
                # exit
                # Evaluate the scalar expression
                scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols,type_table)
                
         
                elem_type = element.exp._type
                elem_size = size_compound_init(elem_type,type_table)
          
                # exit()
                instructions.append(TackyCopyToOffSet(src=scalar_val, dst=name, offset=offset[0]))
               
                
                offset[0] += elem_size
          
                
            elif isinstance(element,CompoundInit) and isinstance(element._type,Structure):
                # exit()
                members = type_table[expr._type.tag].members
                mem_offset=[0]
                for mem_init , member in zip(element.initializer,members):
                    mem_offset[0] = offset[0]+member.offset 
                    compount_init(mem_init,instructions,symbols,mem_offset,name,type_table)
                
            elif isinstance(element, CompoundInit):
                # Recursively process nested compound initializer
                compount_init(element, instructions, symbols, offset, name,type_table)
    
    elif isinstance(expr,SingleInit) and isinstance(expr.exp,String):
            for element in expr.exp.string:
                if isinstance(element,CompoundInit):
                    # elif isinstance(element, CompoundInit):
                    # Recursively process nested compound initializer
                    compount_init(element, instructions, symbols, offset, name,type_table)
                    print('element',element)
                else:
                
                    import ast
                    try:
                        print('error in compount -> single inint')
                        # Use ast.literal_eval to properly interpret escape sequences
                        decoded_string = ast.literal_eval(f'{element}')
                    except (ValueError, SyntaxError):
                        # Fallback if literal_eval fails
                        decoded_string = element.encode().decode('unicode-escape')
                    
                    val = ord(decoded_string)
                    instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(val)),dst =name,offset=offset[0]))
                    elem_size = 1
                    print('error here')
                    
                    offset[0] += elem_size
            instructions.append(TackyCopyToOffSet(TackyConstant(ConstInt(0)),dst =name,offset=offset[0]))
    elif isinstance(expr, SingleInit):
                element = expr
                # exit
                # Evaluate the scalar expression
                scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols,type_table)
                
                elem_type = element.exp._type
                elem_size = size_compound_init(elem_type,type_table)
          
                # exit()
                # print('jere')
                # print(offset[0])
                instructions.append(TackyCopyToOffSet(src=scalar_val, dst=name, offset=offset[0]))
               
                # print('error here')
                
                offset[0] += elem_size
          
                
    elif isinstance(expr,CompoundInit) and isinstance(expr._type,Structure):
        # exit()
        members = type_table[expr._type.tag].members
        mem_offset=offset
        for mem_init , member in zip(element.initializer,members):
            mem_offset = offset[0]+member.offset 
            compount_init(mem_init,instructions,symbols,mem_offset,name,type_table)
        
  




def convert_fun_decl_to_tacky(fun_decl: FunDecl,symbols,type_table) -> TackyFunction:

    """
    Converts a single FunDecl AST node (with a body) into a TackyFunction.
    """
    instructions: List[TackyInstruction] = []

    # Gather parameter names
    param_names = [param.name.name for param in fun_decl.params]

    # Convert the function body into TACKY instructions
    # if isinstance(fun_decl.body, Block):
    #     ##fun_decl.body.block_items)
    i = 0
    if isinstance(fun_decl.body,Null):
        pass
    else: 
        for stmt in fun_decl.body:
            
            emit_statement(stmt, instructions,symbols,type_table)

    instructions.append(TackyReturn(val=TackyConstant(ConstInt(0,exp_type=Int()))))
    
    return TopLevel.tack_func(
        identifier=fun_decl.name.name,
        _global=False,# Function name
        params=fun_decl.params,           # Function parameters
        body=instructions             # Function body instructions
    )

def emit_tacky_program(ast_program: Program,symbols,type_table) -> TackyProgram:
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
                t_func = convert_fun_decl_to_tacky(fun_decl,symbols,type_table)
                t_func._global=symbols[t_func.name]['attrs'].global_scope
                tacky_funcs.append(t_func)
            # Else, discard declarations that have no body
        else:
            pass 

    symbols_new = convert_symbols_to_tacky(symbols)

    tacky_funcs.extend(symbols_new)
  
    return TackyProgram(function_definition=tacky_funcs)

def emit_tacky(program_ast: Program,symbols,type_table) :
    """
    High-level function that converts a full AST 'Program' node into a TackyProgram.
    """
    # n_symbols={}
    # #symbols)
    # exit()
    # exit(program_ast)
    return emit_tacky_program(program_ast,symbols,type_table),symbols,type_table
