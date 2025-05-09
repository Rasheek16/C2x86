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

def convert_symbols_to_tacky(symbols:dict,type_table):
    # #'Convert symbols to tacky')
    # #symbols)
    ##symbols)
    # #symbols)
    # 
    tacks_defs=[]
    for name,entry in symbols.items():
        # #'error here') 
        if entry['attrs']!=None:
            #entry['attrs'])
            if isinstance(entry['attrs'],StaticAttr):
                # #entry['attrs'].init)
                #entry)
                # 
                init = []
                # #('here')
                #( entry['attrs'].init)
                if isinstance(entry['val_type'],Structure) and not isinstance(entry['attrs'].init,Tentative) and isinstance(entry['attrs'].init,Initial) and len(entry['attrs'].init.value) == 0:
                        # #struct)
                        # 
                        # 
                        struct = type_table[entry['val_type'].tag]
                        # #struct.size)
                        # 
                        # init.append(ZeroInit())
                        if struct.size % 8 != 0 :
                            struct.size = align_offset(struct.size+8,8)
                        init.append(ZeroInit(struct.size))
                    
                        tacks_defs.append(TackyStaticVariable(identifier=name,_global =entry['attrs'].global_scope,_type=entry['val_type'],init=init))

                elif isinstance(entry['attrs'].init,Initial):
                    # init = []
                    # 
                    #
                    for i in entry['attrs'].init.value:
                        # 
                        if isinstance(i,Structure):
                            
                          
                            struct = type_table[entry['val_type'].tag]
                            # struct.size
                            # struct
                            # 
                            # init.append(ZeroInit(struct.size))
                            
                        #     member_list_type =[member for member in struct.members]
                    
                            # size1 = 0
                            # if len(member_list_type) > 0:
                            #     for member in member_list_type:
                            #         size1 += size(member.member_type,type_table)
                            #         i = member.member_type
                            #         if isinstance(i,Array):
                                        
                            #             array = i
                                    
                            #             _type = get_array_type_size(array._type)
                                    
                            #             ini = no_of_elements(array)
                                        
                            #             init.append(ZeroInit(ini * _type))
                                        
                            #         elif isinstance(i,(Long,ULong)):
                            #             init.append(LongInit(0))
                            #         elif isinstance(i,Double):
                                    
                            #             init.append(DoubleInit(0))
                            #         elif isinstance(i,(Char,UChar,SChar)):  
                            #             init.append(CharInit(0))
                            #         else:
                            #             init.append(IntInit(0))
                            # else:
                                
                            init.append(ZeroInit(struct.size))
                            # init.append(ZeroInit(struct.size))
                        
                        elif isinstance(i,(StringInit,PointerInit)):
                            if isinstance(i,StringInit):
                            
                                string_val = i.string 
                                decoded_string = i.string.encode().decode('unicode_escape')
                               
                                # 
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
                        elif isinstance(i,StringInit):
                            init.append(i)
                        else:
                            raise TypeError('UNKNOWN SYMBOL TYPE',i.value)
                    
                    if isinstance(entry['val_type'],Structure):
                        struct_decl = type_table[entry['val_type'].tag]
                        old_struct_size = struct_decl.size 
                        struct_size = ((old_struct_size + 7) // 8) * 8
                        if struct_size>old_struct_size:
                            init.append(ZeroInit(struct_size-old_struct_size))
                        
                        # 
                    
                    tacks_defs.append(TackyStaticVariable(identifier=name,_global =entry['attrs'].global_scope,_type=entry['val_type'],init=init))
                    # #'after loop')
                    # #init)
                elif isinstance(entry['attrs'].init,Tentative):
                    #entry['val_type'])
                    init  = []
                    if isinstance(entry['val_type'],Structure):
                        struct = type_table[entry['val_type'].tag]
                        struct.size
                        init.append(ZeroInit(struct.size))
                        
                        member_list_type =[member for member in struct.members]
                  
                        size1 = 0
                        if len(member_list_type) > 0:
                            for member in member_list_type:
                                size1 += size(member.member_type,type_table)
                                i = member.member_type
                                if isinstance(i,Array):
                                    
                                    array = i
                                
                                    _type = get_array_type_size(array._type)
                                
                                    ini = no_of_elements(array)
                                    
                                    init.append(ZeroInit(ini * _type))
                                    
                                elif isinstance(i,(Long,ULong)):
                                    init.append(LongInit(0))
                                elif isinstance(i,Double):
                                
                                    init.append(DoubleInit(0))
                                elif isinstance(i,(Char,UChar,SChar)):  
                                    init.append(CharInit(0))
                                else:
                                    init.append(IntInit(0))
                        else:
                            
                            init.append(ZeroInit(struct.size))
                        # entry['val_type']=entry['val_type'].members[0].member_type
                    # #'hfuiawhg')
                    elif isinstance(entry['val_type'],Array):
                        # #entry['val_type'])
                        # #init)
                        array = entry['val_type']
                    
                        _type = get_array_type_size(array._type)
                       
                        ini = no_of_elements(array)
                        
                        init.append(ZeroInit(ini * _type))
                        
                    elif type(entry['val_type'])==type(Long):
                        init.append(LongInit(0))
                    else:
                        init.append(IntInit(0))
                    tacks_defs.append(TackyStaticVariable(identifier=name,_type=entry['val_type'],_global =entry['attrs'].global_scope,init=init))
            
            elif isinstance(entry['attrs'],ConstantAttr):
                # 
                
                tacks_defs.append(TackyStaticConstant(identifier=name,_type=entry['val_type'],init=entry['attrs'].init))
                
    #tacks_defs)     
    #(tacks_defs)
    # 
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
    #'conversion got type table', type_table is not None)
    # #e)
    # if type_table is None:
    #     
    # #type_table)
    #'expression to convert ',e)
    # if isinstance(e.get_type(),Structure):
    #     
    result = emit_tacky_expr(e, instructions,symbols,type_table)
    #'result',result)
    if isinstance(result,PlainOperand):
        return result.val
    elif isinstance(result,DereferencedPointer):
        dst = make_temporary(symbols,e.get_type())
        # if isinstance(e.get_type(),Structure):
        #     
        instructions.append(TackyLoad(result.val, dst))
        # #'Returning pointer def')
        
        return dst
    elif isinstance(result,SubObject):
        
        dst = make_temporary(symbols,e.get_type())
        # #e)
        # #e.get_type())
        # #dst)
        # 
        instructions.append(TackyCopyFromOffSet(result.base, result.offset, dst))
        return dst
    elif isinstance(result,Null):
        pass 
    else:
        raise ValueError('Invalid operand',result)



 
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
        # 
      
        return emit_tacky_expr(expr.exp,instructions,symbols,type_table)   
    elif isinstance(expr, Var):
        # #expr)
        # 
        return PlainOperand(TackyVar(expr.identifier.name))
    elif isinstance(expr, Assignment):
        # #'assignment',expr)
        #'assignment expression got type table',type_table is not None)
       
        
        if isinstance(expr.right,CompoundInit):
            #'going into assignment compount init')
            compound_init(expr.right,instructions,symbols,[0],expr.left,type_table)
            #'after asignment compount init')
            return 
        else:
            
            rval = emit_tacky_expr_and_convert(expr.right, instructions,symbols,type_table)
            
        lval=emit_tacky_expr(expr.left,instructions,symbols,type_table)
        if isinstance(lval,SubObject):
            # 
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
        # 
        dst_var = make_temporary(symbols,expr.get_type())
        
        # #expr.get_type())
        # 

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
        
        # if isinstance(t,ULong) and isinstance(expr.exp,Constant):
            #expr)
            # 
   
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
        # 
        #'In binary')
        
        if expr.operator in ('And', 'Or'):
            # Short-circuit evaluation for logical operators
            if expr.operator == 'And':
                return emit_and_expr(expr, instructions,symbols,type_table)
            elif expr.operator == 'Or':
                return emit_or_expr(expr, instructions,symbols,type_table)
        else:
            #'Other operator')
            
            #'here')
            # 
    # Determine the types of the left and right operands.
            left_type = expr.left.get_type()
            right_type = expr.right.get_type()
            is_left_ptr = is_pointer(left_type)
            is_right_ptr = is_pointer(right_type)
            # Handle pointer arithmetic: either addition or subtraction
        
            if expr.operator == BinaryOperator.ADD and (is_left_ptr or is_right_ptr):
                #'Here')
                #is_left_ptr)
                #expr.right)
                # 
                # Ensure the pointer is the first operand.
                if is_left_ptr:
                    pointer_operand = emit_tacky_expr_and_convert(expr.left, instructions, symbols,type_table)
                    integer_operand = emit_tacky_expr_and_convert(expr.right, instructions, symbols,type_table)
                    # #symbols[integer_operand.identifier])
                    # 
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
               
                # 
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
        #'Handling function calls')
        # Handle function calls
        # 1. Evaluate each argument
        arg_vals = []
        for arg in expr.args:
            # #arg)
           
            arg_val = emit_tacky_expr_and_convert(arg, instructions,symbols,type_table)
            arg_vals.append(arg_val)
        
        # 2. Generate a new temporary to hold the function call's result
        dst_var = Null()
        # #symbols[expr.identifier.name])
        
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
            #' function call')
            return PlainOperand(dst_var)
        else:
            instructions.append(TackyFunCall(
            fun_name=expr.identifier.name,  # e.g., "foo"
            args=arg_vals,
            dst=dst_var))
            # 
            #' function call')
            
            return Null()
     
    elif isinstance(expr,Dereference):
        result = emit_tacky_expr_and_convert(expr.exp, instructions, symbols,type_table)
        #symbols[result.identifier])
        #result)
        # 
        return DereferencedPointer(result) 
    elif isinstance(expr,(IntInit,LongInit,DoubleInit)):
        # #'iofdszh;g')
        return Constant(expr.value)
        # pass 
    elif isinstance(expr,AddOf):
        #expr)
        #'Handling address of',expr.exp)
        v = emit_tacky_expr(expr.exp, instructions, symbols,type_table)
     
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
        #'subscript expression',type_table is None)
        # 1. Process the base array expression to get its pointer value.
        base_ptr = emit_tacky_expr_and_convert(expr.exp1, instructions, symbols,type_table)

        # 2. Process the index expression to get the index value.
        index_val = emit_tacky_expr_and_convert(expr.exp2, instructions, symbols,type_table)

        # 3. Compute the scale factor based on the size of the element type.  
        #expr)
        #base_ptr)
        #index_val)
        # 
     
        if isinstance(expr.exp1.get_type(),(Pointer)):
            tmp_ptr = make_temporary(symbols, expr.exp1.get_type())
            stride = array_size(expr.exp1.get_type(),type_table)  # Get the size of the element type
            
            # #'Stride',stride)
            # 
            # 
            if isinstance(expr.exp1.get_type(),(Char,UChar,SChar)):
                stride = 1
            #(expr.exp1.get_type())
            #(stride)
            # 
            instructions.append(TackyAddPtr(ptr=base_ptr, index=index_val, scale=stride, dst=tmp_ptr))
            if not isinstance(symbols[base_ptr.identifier]['val_type'],(Pointer,Array)): 
                
                
                # Lvalue conversion: Load the scalar value from the computed pointer
                tmp_val = make_temporary(symbols,symbols[base_ptr.identifier]['val_type'])
                # if isinstance(symbols[base_ptr.identifier]['val_type'],Structure):
                #     #tmp_val)
                #     #expr)
                #     
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
                # if isinstance(symbols[index_val.identifier]['val_type'],Structure):
                #     
                instructions.append(TackyLoad(src_ptr=tmp_ptr, dst=tmp_val))
                return  PlainOperand(tmp_val)  # Return the loaded value

            
     
        # 7. If it's still an array, return the computed pointer directly.
        return DereferencedPointer(tmp_ptr)  # No need to dereference if it's another array
    elif isinstance(expr,String):
        #expr._type)
        # 
        temp_str = get_string_label()
        # #expr.string)
        import ast
      
            # Use ast.literal_eval to properly interpret escape sequences
        # decoded_string = ast.literal_eval(expr.string)
        
        #     # decoded_string = unescape_c_string(expr.string)
        # decoded_string = expr.string.encode().decode('unicode_escape')
        # # #decoded_string)
        # # for char in expr.string:
            
        # #    char = char.encode().decode('latin1')
               
        # expr.string = decoded_string
        #'String',expr.string)
        # 
        symbols[temp_str] = {
            'val_type':expr._type,
            'attrs':ConstantAttr(StringInit(string=expr.string,null_terminated=True)),
            'isDouble':False,
            'ret':expr._type
        }
        
        # 
        temp_dst = make_temporary(symbols,expr._type)
        #temp_dst)
        #expr)
        # if isinstance(expr._type,Array):
        #     expr_type = Pointer(expr._type)
            # instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(0)),dst = temp_str,offset=1))
        # 
        instructions.append(TackyGetAddress(src=TackyVar(temp_str),dst = temp_dst))
        
        
        #! CAN BE WRONG
        return DereferencedPointer(temp_dst)
    elif isinstance(expr,SizeOf):
        t = expr.exp.get_type()
        #'t',t)        # 
        result  = size(t,type_table)
        if isinstance(expr.exp.get_type(),Double):
            result = 8
        # 
        return PlainOperand(TackyConstant(ConstULong(result)))
    elif isinstance(expr,SizeOfT):
        
        result  = size(expr.exp,type_table)
        if isinstance(expr.exp,Double):
            result = 8
        #result)
        #expr.exp)
        # 
        return PlainOperand(TackyConstant(ConstULong(result)))
    elif isinstance(expr,Null):
        return Null() 
    elif isinstance(expr,Dot):
        # 
        #'Handling dot expression')
        #'type table in dot',type_table)
        #expr)
        # 
        # #expr.structure._type)
        struct_def:StructEntry = type_table[expr.structure._type.tag]
        
        member_offset = 0
        
        for i in struct_def.members:
            p:MemberEntry=i 
            if p.member_name.name ==expr.member.name:
                member_offset = p.offset 
        inner_object = emit_tacky_expr(expr.structure,instructions,symbols,type_table)        
        # #symbols[inner_object.val.identifier])
        #inner_object)
        #member_offset)
        #struct_def)
        # 
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
        #expr)
        # Look up the structure type pointed to
        ptr_type = ptr_expr._type
        
       
        # #ptr_type.ref)
        # 
        # 
        struct_type = ptr_type.ref  # e.g., struct inner for struct inner*

        # Look up member offset
        struct_def = type_table.get(struct_type.tag)
        for i in struct_def.members :
            if member_name.name == i.member_name.name:
                #  
                member_offset = i.offset

        # Generate code to evaluate the pointer expression
        ptr = emit_tacky_expr_and_convert(ptr_expr, instructions, symbols,type_table)

        # Optimization: skip AddPtr if offset is 0
        if member_offset == 0:
            return DereferencedPointer(ptr)

        # #expr.get_type())
        # #ptr_type.ref)
        # 
        dst_ptr = make_temporary(symbols,ptr_type)
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
    # 
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
            # 
            
            ret_val = emit_tacky_expr_and_convert(stmt.exp, instructions,symbols,type_table)
            instructions.append(TackyReturn(val=ret_val))
            
    elif isinstance(stmt, (DoWhile, While, For)):
        ##'In Loop')
        ##stmt )
        emit_loop_statement(stmt, instructions,symbols,type_table)
        ##'After Loop')
        
    elif isinstance(stmt, D):  # Variable Declaration
        # Handle variable declarations, possibly with initialization
        
        #'D got type table',type_table is not None)
        #stmt.declaration)
        # 
        # #type_table)
        
        # var_name = stmt.declaration.name.name
        if isinstance(stmt.declaration,FunDecl):
            convert_fun_decl_to_tacky(stmt.declaration,symbols,type_table)
        else:
            if isinstance(stmt.declaration,StructDecl):
                return 
            if stmt.declaration.init is not None and not isinstance(stmt.declaration.init, Null) and not isinstance(stmt.declaration.storage_class,Static):
             
                if isinstance(stmt.declaration.init,SingleInit) and isinstance(stmt.declaration.init._type,(Array)) :
                    
                    compound_init(stmt.declaration.init,instructions,symbols,[0],stmt.declaration.name,type_table)
                    
                    return
                elif isinstance(stmt.declaration.init,CompoundInit):
                       
                    compound_init(stmt.declaration.init,instructions,symbols,[0],stmt.declaration.name,type_table)
                  
                
                else:
                 
                # Emit assignment to initialize the variable
                    assign_expr = Assignment(
                        left=Var(stmt.declaration.name),
                        right=stmt.declaration.init
                    )
                    # #type_table)
                    
                    emit_tacky_expr_and_convert(assign_expr, instructions,symbols,type_table=type_table)
            elif isinstance(stmt.declaration.var_type,Structure) and not isinstance(stmt.declaration.init,Null) and not isinstance(stmt.declaration.storage_class,Static):
                compound_init(stmt.declaration.init,instructions,symbols,[0],stmt.declaration.name,type_table)
                
                
            
                   
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
    # #stmt)
    # 
    #'Inside if')
    """
    Emits Tacky instructions for an If statement.
    """
    condition_var = emit_tacky_expr_and_convert(stmt.exp, instructions,symbols,type_table)
    else_label = get_false_label()
    end_label = get_end_label()
    # #condition_var)
    # 

    # If condition is zero, jump to else_label
    # #stmt.exp)
    # #symbols[condition_var.identifier])
    # 
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
            # 
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
        # 
        if isinstance(node.exp,Null):
            instructions.append(TackyReturn(TackyVar("DUMMY")))
        else:
            # #)
            ret_val = emit_tacky_expr_and_convert(node.exp, instructions,symbols,type_table)
            # #node.exp)
            # #ret_val)
            # 
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




# def compound_init(expr, instructions, symbols, offset, name, type_table):
#     # #('inside compound initi')
#     if isinstance(expr, CompoundInit):
#         #expr._type)
#         # 
#         if isinstance(expr._type, Array) and isinstance(expr._type._type, Structure):
#             struct_type = expr._type._type
#             struct_size = size_compound_init(struct_type, type_table)
#             members = type_table[struct_type.tag].members

#             for i, element in enumerate(expr.initializer):
#                 base_offset = offset[0] + i * struct_size  # compute per-element offset

#                 if isinstance(element, CompoundInit):
#                     for mem_init, member in zip(element.initializer, members):
#                         field_offset = base_offset + member.offset
#                         saved_offset = offset[0]
#                         offset[0] = field_offset
#                         mem_init._type = member.member_type
#                         compound_init(mem_init, instructions, symbols, offset, name, type_table)
#                         offset[0] = saved_offset
#                 else:
#                     saved_offset = offset[0]
#                     offset[0] = base_offset
#                     compound_init(element, instructions, symbols, offset, name, type_table)
#                     offset[0] = saved_offset

                    
#                     # compound_init()
                

#         elif isinstance(expr._type, Structure):
#             # 
#             # Single struct
#             struct_type = expr._type
#             members = type_table[struct_type.tag].members
#             base_offset = offset[0]

#             for mem_init, member in zip(expr.initializer, members):
#                 field_offset = base_offset + member.offset
#                 saved_offset = offset[0]
#                 offset[0] = field_offset
#                 mem_init._type = member.member_type
#                 compound_init(mem_init, instructions, symbols, offset, name, type_table)
#                 offset[0] = saved_offset
#             # #(instructions)
#             # 
        
#         else:
#             # General compound init (array, nested structure, or initializer list)
#             #(expr)
#             for element in expr.initializer:
#                 if isinstance(element, SingleInit) and isinstance(element.exp, String):
#                     count = 0
#                     for i in element.exp.string:
#                         if isinstance(i, CompoundInit):
#                             compound_init(i, instructions, symbols, offset, name, type_table)
#                             continue

#                         import ast
#                         try:
#                             decoded_string = ast.literal_eval(f'{i}')
#                         except (ValueError, SyntaxError):
#                             decoded_string = i.encode().decode('unicode-escape')

#                         val = ord(str(decoded_string))
#                         instructions.append(
#                             TackyCopyToOffSet(TackyConstant(ConstChar(val)), dst=TackyVar(name.name), offset=offset[0])
#                         )
#                         offset[0] += 1
#                         count += 1

#                     # Pad with nulls if the string is shorter
#                     while count < element._type._int.value._int:
#                         instructions.append(
#                             TackyCopyToOffSet(TackyConstant(ConstChar(0)), dst=TackyVar(name.name), offset=offset[0])
#                         )
#                         offset[0] += 1
#                         count += 1

#                 elif isinstance(element, SingleInit):
#                     scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols, type_table)
#                     elem_type = element.exp._type
#                     elem_size = size_compound_init(elem_type, type_table)
#                     instructions.append(
#                         TackyCopyToOffSet(src=scalar_val, dst=TackyVar(name.name), offset=offset[0])
#                     )
#                     if not isinstance(element._type, Structure):
#                         offset[0] += min(elem_size, 8)
#                 elif isinstance(expr._type, Structure):
#                     # Single struct
#                     struct_type = expr._type
#                     members = type_table[struct_type.tag].members
#                     base_offset = offset[0]

#                     for mem_init, member in zip(expr.initializer, members):
#                         field_offset = base_offset + member.offset
#                         saved_offset = offset[0]
#                         offset[0] = field_offset
#                         mem_init._type = member.member_type
#                         compound_init(mem_init, instructions, symbols, offset, name, type_table)
#                         offset[0] = saved_offset
#                 elif isinstance(element, CompoundInit):
#                     compound_init(element, instructions, symbols, offset, name, type_table)

#                 else:
#                     raise SyntaxError('Unsupported element in CompoundInit')
          
                
#     elif isinstance(expr, SingleInit) and isinstance(expr.exp, String):
#         count = 0
#         for element in expr.exp.string:
            
#             if isinstance(element, CompoundInit):
#                 compound_init(element, instructions, symbols, offset, name, type_table)
#             else:
#                 import ast
#                 try:
#                     decoded_string = ast.literal_eval(f'{element}')
#                 except (ValueError, SyntaxError):
#                     decoded_string = element.encode().decode('unicode-escape')
#                 val = ord(str(decoded_string))
#                 instructions.append(
#                     TackyCopyToOffSet(TackyConstant(ConstChar(val)), dst=TackyVar(name.name), offset=offset[0])
#                 )
#                 offset[0] += 1
                
#                 count += 1

#                     # Pad with nulls if the string is shorter
#         while count < expr._type._int.value._int:
#             instructions.append(
#                 TackyCopyToOffSet(TackyConstant(ConstChar(0)), dst=TackyVar(name.name), offset=offset[0])
#             )
#             offset[0] += 1
#             count += 1

#         #expr._type)
#         # 
#         # Add terminating null character
#         # if not expr.exp.string[-1]=='\0':
#         #     instructions.append(
#         #         TackyCopyToOffSet(TackyConstant(ConstInt(0)), dst=TackyVar(name.name), offset=offset[0])
#         #     )

#     elif isinstance(expr, SingleInit):
#         # 
#         scalar_val = emit_tacky_expr_and_convert(expr.exp, instructions, symbols, type_table)
#         elem_type = expr.exp._type
#         elem_size = size_compound_init(elem_type, type_table)
#         instructions.append(
#             TackyCopyToOffSet(src=scalar_val, dst=TackyVar(name.name), offset=offset[0])
#         )
#         if not isinstance(expr._type, Structure):
#             offset[0] += min(elem_size, 8)

#     else:
        
#         raise ValueError(f'Invalid expression in compound initializer {expr}')

def compound_init(expr, instructions, symbols, offset, name, type_table):
    """
    Recursively emit initialization instructions for CompoundInit and SingleInit.

    - Handles:
      * Arrays of structures
      * Single structures
      * String initializers
      * Scalar initializers
      * Nested compound initializers
    """
    # CASE 1: CompoundInit (arrays, structs, or initializer lists)
    if isinstance(expr, CompoundInit):
        typ = expr._type

        # 1a. Array of structures
        if isinstance(typ, Array) and isinstance(typ._type, Structure):
            struct_t    = typ._type
            struct_size = size_compound_init(struct_t, type_table)
            members     = type_table[struct_t.tag].members

            for idx, element in enumerate(expr.initializer):
                base = offset[0] + idx * struct_size
                if isinstance(element, CompoundInit):
                    # explicit member initializers
                    for mem_init, member in zip(element.initializer, members):
                        saved = offset[0]
                        offset[0] = base + member.offset
                        mem_init._type = member.member_type
                        compound_init(mem_init, instructions, symbols, offset, name, type_table)
                        offset[0] = saved
                    # zero-fill any omitted members
                    for member in members[len(element.initializer):]:
                        saved = offset[0]
                        offset[0] = base + member.offset
                        instructions.append(
                            TackyCopyToOffSet(
                                src=TackyConstant(ConstInt(0)),
                                dst=TackyVar(name.name),
                                offset=offset[0]
                            )
                        )
                        offset[0] = saved
                else:
                    # scalar or string within struct array
                    saved = offset[0]
                    offset[0] = base
                    compound_init(element, instructions, symbols, offset, name, type_table)
                    offset[0] = saved

        # 1b. Single structure
        elif isinstance(typ, Structure):
            struct_t = typ
            members  = type_table[struct_t.tag].members
            base = offset[0]

            # explicit member initializers
            for mem_init, member in zip(expr.initializer, members):
                saved = offset[0]
                offset[0] = base + member.offset
                mem_init._type = member.member_type
                compound_init(mem_init, instructions, symbols, offset, name, type_table)
                offset[0] = saved
            # zero-fill any omitted members
            for member in members[len(expr.initializer):]:
                saved = offset[0]
                offset[0] = base + member.offset
                instructions.append(
                    TackyCopyToOffSet(
                        src=TackyConstant(ConstInt(0)),
                        dst=TackyVar(name.name),
                        offset=offset[0]
                    )
                )
                offset[0] = saved

        # 1c. Other compound inits (arrays of scalars, nested lists)
        else:
            for element in expr.initializer:
                # String literal initializer
                if isinstance(element, SingleInit) and isinstance(element.exp, String):
                    count = 0
                    for ch in element.exp.string:
                        if isinstance(ch, CompoundInit):
                            compound_init(ch, instructions, symbols, offset, name, type_table)
                            continue
                        import ast
                        try:
                            decoded = ast.literal_eval(f'{ch}')
                        except Exception:
                            decoded = ch.encode().decode('unicode-escape')
                        val = ord(str(decoded))
                        instructions.append(
                            TackyCopyToOffSet(
                                TackyConstant(ConstChar(val)),
                                dst=TackyVar(name.name),
                                offset=offset[0]
                            )
                        )
                        offset[0] += 1
                        count += 1
                    # pad with nulls
                    length = element._type._int.value._int
                    while count < length:
                        instructions.append(
                            TackyCopyToOffSet(
                                TackyConstant(ConstChar(0)),
                                dst=TackyVar(name.name),
                                offset=offset[0]
                            )
                        )
                        offset[0] += 1
                        count += 1

                # Scalar initializer
                elif isinstance(element, SingleInit):
                    scalar = emit_tacky_expr_and_convert(element.exp, instructions, symbols, type_table)
                    elem_type = element.exp._type
                    size = size_compound_init(elem_type, type_table)
                    instructions.append(
                        TackyCopyToOffSet(
                            src=scalar,
                            dst=TackyVar(name.name),
                            offset=offset[0]
                        )
                    )
                    if not isinstance(elem_type, Structure):
                        offset[0] += min(size, 8)

                # Nested compound initializer
                elif isinstance(element, CompoundInit):
                    compound_init(element, instructions, symbols, offset, name, type_table)

                else:
                    raise SyntaxError(f'Unsupported initializer element: {element}')

    # CASE 2: SingleInit with a String literal
    elif isinstance(expr, SingleInit) and isinstance(expr.exp, String):
        count = 0
        for ch in expr.exp.string:
            if isinstance(ch, CompoundInit):
                compound_init(ch, instructions, symbols, offset, name, type_table)
            else:
                import ast
                try:
                    decoded = ast.literal_eval(f'{ch}')
                except Exception:
                    decoded = ch.encode().decode('unicode-escape')
                val = ord(str(decoded))
                instructions.append(
                    TackyCopyToOffSet(
                        TackyConstant(ConstChar(val)),
                        dst=TackyVar(name.name),
                        offset=offset[0]
                    )
                )
                offset[0] += 1
                count += 1
        # pad with nulls
        length = expr._type._int.value._int
        while count < length:
            instructions.append(
                TackyCopyToOffSet(
                    TackyConstant(ConstChar(0)),
                    dst=TackyVar(name.name),
                    offset=offset[0]
                )
            )
            offset[0] += 1
            count += 1

    # CASE 3: Single scalar initializer
    elif isinstance(expr, SingleInit):
        scalar = emit_tacky_expr_and_convert(expr.exp, instructions, symbols, type_table)
        elem_type = expr.exp._type
        size = size_compound_init(elem_type, type_table)
        instructions.append(
            TackyCopyToOffSet(
                src=scalar,
                dst=TackyVar(name.name),
                offset=offset[0]
            )
        )
        if not isinstance(elem_type, Structure):
            offset[0] += min(size, 8)

    else:
        raise ValueError(f'Invalid expression in compound initializer: {expr}')


# def compound_init(expr, instructions, symbols, offset, name,type_table):
#     # 
    
#     if isinstance(expr,CompoundInit) and isinstance(expr._type,Array) and isinstance(expr._type._type,Structure):
#         # #expr)
#         # 
#         for element in expr.initializer:
#             #'Element')
#             #element)
#             # 
        
#             # return struct_init(element,instructions,symbols,offset,name,type_table)
#             members = type_table[expr._type._type.tag].members
        
           
#             for mem_init , member in zip(element.initializer,members):
#                 offset[0] = offset[0]+member.offset
#                 # old_offset = offset[0]
                
#                 mem_init._type = expr._type._type
#                 compound_init(mem_init,instructions,symbols,offset,name,type_table)

                
#                 # offset[0] = old_offset + member.offset 

                    
#     elif isinstance(expr, CompoundInit):
       
#         for element in expr.initializer:
            
#             if isinstance(element,SingleInit) and isinstance(element.exp,String):
              
#                 count = 0
#                 for i in element.exp.string:
#                     if isinstance(i,CompoundInit):
                        
#                         compound_init(i, instructions, symbols, offset, name,type_table)
                
#                     import ast
#                     try:
#                         #'Error in compound init')
#                         # Use ast.literal_eval to properly interpret escape sequences
#                         decoded_string = ast.literal_eval(f'{i}')
#                     except (ValueError, SyntaxError):
#                         # Fallback if literal_eval fails
#                         decoded_string = i.encode().decode('unicode-escape')
#                         #decoded_string)
#                     val = ord(str(decoded_string))
#                     instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(val)),dst =TackyVar(name.name),offset=offset[0]))
#                     # i+=1
#                     count+=1
#                     elem_size = 1
#                     offset[0] += elem_size
#                     #element)
#                     # 
#                 while count < element._type._int.value._int:
                    
#                     instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(0)),dst =TackyVar(name.name),offset=offset[0]))
#                     elem_size = 1
                    
#                     offset[0] += elem_size
#                     count+=1
                
#             # if isinstance(element,CompoundInit) and isinstance(expr._type,Array) and isinstance(expr._type._type,Structure):
                
#             #     # return struct_init(element,instructions,symbols,offset,name,type_table)
#             #     members = type_table[expr._type._type.tag].members
            
#             #     # #members)
#             #     # #expr.initializer[1])
#             #     # 
#             #     for mem_init , member in zip(element.initializer,members):
#             #         offset[0] = offset[0]+member.offset
#             #         old_offset = offset[0]
                   
#             #         mem_init._type = member.member_type
#             #         compound_init(mem_init,instructions,symbols,offset,name,type_table)
#             #         #mem_init)
                   
#             #         offset[0] = old_offset + member.offset 
#             # elif isinstance(element,CompoundInit) and isinstance(expr._type,Structure):
              
#             #     members = type_table[expr._type.tag].members
             
#             #     for mem_init , member in zip(element.initializer,members):
#             #         # mem_of = size(member.member_type,type_table)
#             #         offset[0] = offset[0]+member.offset
                  
#             #         old_offset = offset[0]
#             #         mem_init._type = member.member_type
                   
#             #         compound_init(mem_init,instructions,symbols,offset,name,type_table)
                    
#             #         offset[0] = old_offset + member.offset 
                   
#                 # #instructions)
#                 # 
        
#             elif isinstance(element, SingleInit):
#                 #expr)
#                 #element)
#                 # 
#                 # Evaluate the scalar expression
#                 scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols,type_table)
              
         
#                 elem_type = element.exp._type
#                 elem_size = size_compound_init(elem_type,type_table)
          
#                 if elem_size>8:
#                     elem_size = 8
#                 instructions.append(TackyCopyToOffSet(src=scalar_val, dst=TackyVar(name.name), offset=offset[0]))
#                 if not isinstance(element._type,Structure):
#                     offset[0] += elem_size
               
              
          
                
                
#             elif isinstance(element, CompoundInit):
#                 # Recursively process nested compound initializer
#                 compound_init(element, instructions, symbols, offset, name,type_table)
#             else:
#                 raise SyntaxError('abfhfahfhdsl;f')
#     elif isinstance(expr,SingleInit) and isinstance(expr.exp,String):
#             for element in expr.exp.string:
#                 if isinstance(element,CompoundInit):
#                     # elif isinstance(element, CompoundInit):
#                     # Recursively process nested compound initializer
#                     compound_init(element, instructions, symbols, offset, name,type_table)
#                     #'element',element)
#                 else:
                
#                     import ast
#                     try:
#                         #'error in compount -> single inint')
#                         # Use ast.literal_eval to properly interpret escape sequences
#                         decoded_string = ast.literal_eval(f'{element}')
#                     except (ValueError, SyntaxError):
#                         # Fallback if literal_eval fails
#                         decoded_string = element.encode().decode('unicode-escape')
                    
#                     val = ord(decoded_string)
#                     instructions.append(TackyCopyToOffSet(TackyConstant(ConstChar(val)),dst =TackyVar(name.name),offset=offset[0]))
#                     elem_size = 1
#                     #'error here')
                    
#                     offset[0] += elem_size
#             instructions.append(TackyCopyToOffSet(TackyConstant(ConstInt(0)),dst =TackyVar(name.name),offset=offset[0]))
#     elif isinstance(expr, SingleInit):
#                 element = expr
#                 # 
#                 # Evaluate the scalar expression
#                 scalar_val = emit_tacky_expr_and_convert(element.exp, instructions, symbols,type_table)
                
#                 elem_type = element.exp._type
#                 elem_size = size_compound_init(elem_type,type_table)
          
                
                
#                 instructions.append(TackyCopyToOffSet(src=scalar_val, dst=TackyVar(name.name), offset=offset[0]))
               
                
#                 if not isinstance(element._type,Structure):
#                     offset[0] += elem_size
#                 # offset[0] += elem_size
                
          
#     else:
#         raise ValueError('invalid expression')        
 
        
  




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

    if len(instructions) > 0 and not (isinstance(instructions[-1],TackyReturn) or isinstance(instructions[-1],TackyStore)):
    # if not isinstance(instructions[-1],TackyReturn):
        # If the last instruction is a return, we don't need to add an extra return 0.
        # pass
          #isinstance(instructions[-1],TackyStore))
        #   
          instructions.append(TackyReturn(val=TackyConstant(ConstInt(0,exp_type=Int()))))
    elif len(instructions) == 0 :
          instructions.append(TackyReturn(val=TackyConstant(ConstInt(0,exp_type=Int()))))
    elif isinstance(instructions[-1],TackyStore):
          instructions.append(TackyReturn(val=TackyVar('NO_RET_VAL')))
        
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
                # 
                t_func = convert_fun_decl_to_tacky(fun_decl,symbols,type_table)
                t_func._global=symbols[t_func.name]['attrs'].global_scope
                tacky_funcs.append(t_func)
            # Else, discard declarations that have no body
        else:
            pass 

    symbols_new = convert_symbols_to_tacky(symbols,type_table)

    tacky_funcs.extend(symbols_new)
  
    return TackyProgram(function_definition=tacky_funcs)

def emit_tacky(program_ast: Program,symbols,type_table) :
    """
    High-level function that converts a full AST 'Program' node into a TackyProgram.
    """
    # n_symbols={}
    # #symbols)
    # 
    # (program_ast)
    return emit_tacky_program(program_ast,symbols,type_table),symbols,type_table
