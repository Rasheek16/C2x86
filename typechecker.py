from _ast5 import *
from typing import Optional, List
from type_classes import *
import sys

x=0

def size(_type):
    if type(_type)==type(Int()):
        return 4
    elif type(_type)==type(Long()):
        return 8
    elif type(_type)==type(UInt()):
        return 4
    elif type(_type)==type(ULong()):
        return 8
    elif type(_type)==type(Double()):
        return 16
    
def is_null_pointer_constant(c):
    if isinstance(c,Constant):
        if isinstance(c.value,(ConstInt,ConstDouble,ConstUInt,ConstLong,ConstULong)):
            if c.value._int==0:
                return True
    
    return False


def convert_by_assignment(e, target_type):
    print('Inside convert by assignment')
    if isinstance(e.get_type(),type(target_type)):
        print('Exit convert by assignment')
        
        return e
    if not isinstance(e.get_type(),Pointer) and not isinstance(target_type ,Pointer):
        print('Exit convert by assignment')
        
        return convert_to(e, target_type)
    if is_null_pointer_constant(e) and isinstance(target_type ,Pointer):
        print('Exit convert by assignment')
        
        return convert_to(e, target_type)
    else:
        raise SyntaxError("Cannot convert type for assignment")


def get_ref_type(pointerType):
    if isinstance(pointerType,Pointer) and isinstance(pointerType.ref,Array):
        return get_ref_type(pointerType.ref)
    if isinstance(pointerType,Array):
        return get_ref_type(pointerType._type)
    else:
        # print('Pointer type',pointerType)
        return pointerType





def get_common_pointer_type(e1, e2):
    # print('Inside get common pointer type.')
    
    

   
    if hasattr(e1,'exp') and isinstance(e1.exp,Cast):
        return e1.exp.target_type
    if hasattr(e2,'exp') and isinstance(e2.exp,Cast):
        return e2.exp.target_type
    
    e1_t = e1.get_type()
    e2_t = e2.get_type()

    #
    
        
        # return e2_t
    if isinstance(e1_t,Pointer) and isinstance(e2_t,Pointer):
        
        if isinstance(e1_t.ref,type(e2_t.ref)):
            return e1_t
        else:
            raise SyntaxError("Pointer types are not compatible")

    # 
  
    if type(e1_t)==type(e2_t):
        return e1
    if is_null_pointer_constant(e1):
        return e2_t
    elif is_null_pointer_constant(e2):
        return e1_t
    else:
        raise SyntaxError("Expressions have incompatible types")


def isSigned(_type):
    if type(_type)==type(Int()) or type(_type)==type(Long()) or type(_type)==type(Double()):
        return True
    return False
    


def get_common_type(type1, type2):
    print(type2,type1)
    if type(type1) == type(type2):
        return type1
    if isinstance(type1,Double) or isinstance(type2,Double):
        print('Returning double')
        return Double()
    if size(type1) == size(type2):
        if isSigned(type1):
            return type2 
        else:
            return type1
    if size(type1) > size(type2):
        return type1
    else:
        return type2



def convert_to(e: Exp, t: any):
    # #e.get_type())
    """
    Converts expression 'e' to type 't' by wrapping it in a Cast node, 
    unless 'e' is already that type or is already an identical Cast.
    """
    # If node already has the correct type, no cast needed
    if type(e.get_type()) == type(t):
        return e

    # If it's already a cast to the same type, skip
    if isinstance(type(e), Cast) and type(e.target_type) ==type( t):
        #'here')
        return e

    # Otherwise wrap in a new cast
    cast_exp = Cast(target_type=t, exp=e)
    cast_exp.set_type(t)
    return cast_exp


def typecheck_exp_and_convert(expression,symbols,_type=None):
    
    # print(expression)
    
    typed_e = typecheck_exp(expression, symbols,_type)
   
    
    print('Typed expression',typed_e)
    if not isinstance(typed_e,Null) and isinstance(typed_e.get_type(),Array):
        expression = AddOf(typed_e)
        # print('Add of',addr_exp)
        # print(typed_e.get_type()._type)
        # 
        expression.set_type(Pointer(typed_e.get_type()._type))
        return expression
    print('return Typecheck and convert')
    return typed_e


def flat_val(decl,val):
    if isinstance(decl,Int):
        new_init = Constant(StaticInit.IntInit(Const.constInt(int(val))))
    elif isinstance(decl,UInt):
        new_init = Constant(StaticInit.UIntInit(Const.constUInt(int(val))))
    elif isinstance(decl,Long):
        new_init = Constant(StaticInit.LongInit(Const.constLong(int(val))))
    elif isinstance(decl,ULong):
        new_init = Constant(StaticInit.ULongInit(Const.constULong(int(val))))
    elif isinstance(decl,Double):
        new_init = Constant(StaticInit.DouleInit(Const.constDouble(float(val))))
    
    print('Flat val',new_init)
    return new_init
    



def typecheck_array_init(decl, var_type=None):
    """
    Recursively typechecks an array initializer and returns a flattened list of initial values.

    For a SingleInit, returns a flattened value using flat_val().
    For a CompoundInit, processes each initializer recursively:
      - For nested CompoundInit elements, it recurses using the sub-type (var_type._type).
      - For SingleInit elements, it appends the flattened value.
      - For any unexpected element, it appends a ZeroInit(4).

    If a CompoundInit has fewer elements than expected:
      - For a partially initialized row, missing elements are padded with ZeroInit(4) each.
      - For an entirely missing element (i.e. a missing row), a single ZeroInit whose byte
        count equals (expected_inner * 4) is appended.
    
    var_type must be provided.
    """
    print(decl)
    # exit()
    if var_type is None:
        raise ValueError("var_type must be provided for array initialization")
    
    
    # if (isinstance(decl,CompoundInit) and not isinstance(decl.initializer[0],CompoundInit)) and isinstance(var_type._type,Array):
    #     raise ValueError('Multidim Array initializer must be a compound initializer')
    # Base case: SingleInit returns its flattened value.
    if isinstance(decl, SingleInit):
        if isinstance(decl.exp,Cast):
            return flat_val(decl.exp.exp.value._type, decl.exp.exp.value._int)
        return flat_val(decl.exp.value._type, decl.exp.value._int)
    
    # Recursive case: CompoundInit.
    elif isinstance(decl, CompoundInit):
        result = []
        # expected_length: the number of elements at this array level.
        expected_length = var_type._int.value._int

        # For multidimensional arrays, var_type._type gives the type of a subarray.
        # expected_inner is the expected count for each nested (row) initializer.
        if hasattr(var_type, "_type") and hasattr(var_type._type, "_int"):
            expected_inner = var_type._type._int.value._int
        else:
            expected_inner = None

        for i in range(expected_length):
            if i < len(decl.initializer):
                elem = decl.initializer[i]
                # If we expect nested initializers (i.e. an array of arrays)
                if expected_inner is not None:
                    # Recursively flatten the row using the sub-type.
                    flattened = [typecheck_array_init(elem, var_type._type)]
                    # If the row has fewer elements than expected, pad with ZeroInit(4) per element.
                    # print('Flattened',flattened)
                    if len(flattened) < expected_inner:
                        missing = expected_inner - len(flattened)
                        flattened.extend([ZeroInit(4)] * missing)
                    # Append the flattened row to the overall result.
                    result.extend(flattened)
                else:
                    # Scalar element case.
                    if isinstance(elem, CompoundInit):
                        flattened = typecheck_array_init(elem, var_type._type)
                        result.extend(flattened)
                    elif isinstance(elem, SingleInit):
                        result.append(typecheck_array_init(elem, var_type))
                    else:
                        result.append(ZeroInit(4))
            else:
                # If no initializer is provided for this element:
                if expected_inner is not None:
                    # Missing entire row: pad with a single ZeroInit whose size is the row's total bytes.
                    result.append(ZeroInit(expected_inner * 4))
                else:
                    result.append(ZeroInit(4))
        return result

    else:
        return []


def typecheck_file_scope_variable_declaration(decl: VarDecl, symbols: dict):
    print('Inside file scope var decl')
    print(decl)
    if decl.name.name in symbols:
        print(symbols[decl.name.name])
        # 

    
    # First, determine the initializer based on whether decl.init is null.
    if isinstance(decl.init, Null):
        # For a null initializer, extern variables get NoInitializer,
        # while others get a Tentative initializer.
        if isinstance(decl.storage_class, Extern):
            new_init = NoInitializer()
        else:
            new_init = Tentative()
    else:
        # When there is a non-null initializer, typecheck based on variable type.
        if isinstance(decl.var_type, Array):
            # print('Type checking global array',decl)
            # 
            # For arrays, perform an array-specific typecheck.
            if not isinstance(decl.init, CompoundInit):
                raise ValueError("Array initializer must be a CompoundInit")
            new_init = Initial(typecheck_init(decl.var_type,decl.init,symbols))
            # print('fuigshdaufygkhasedlf')
            print('New init',new_init)
        elif isinstance(decl.var_type, Pointer):
            # For pointers, static variables must be initialized with a pointer value.
            if (not isinstance(decl.init, Null) and not isinstance(decl.init, AddOf) and 
                isinstance(decl.storage_class, Static)):
                raise ValueError('Static pointer initialized with non pointer value.')
            # Allow a constant 0 pointer initializer.
            elif ((hasattr(decl.init, 'exp') and hasattr(decl.init.exp, 'exp') and 
                   isinstance(decl.init.exp.exp, Constant) and int(decl.init.exp.exp.value._int) == 0) or
                  (hasattr(decl.init, 'exp') and isinstance(decl.init.exp, Constant) and 
                   int(decl.init.exp.value._int) == 0)):
                new_init = Initial([Constant(StaticInit.ULongInit(Const.constULong(0)))])
            else:
                # For other pointer cases, fall back to the general initializer typecheck.
                new_init = Initial(typecheck_init(decl.var_type, decl.init, symbols))
        elif hasattr(decl.init, 'exp') and isinstance(decl.init.exp, Constant):
            # For scalar constant initializers, select the correct static initializer.
            init_val = decl.init.exp.value._int
            if isinstance(decl.var_type, Int):
                new_init = Initial([Constant(StaticInit.IntInit(Const.constInt(init_val)))])
            elif isinstance(decl.var_type, UInt):
                new_init = Initial([Constant(StaticInit.UIntInit(Const.constUInt(init_val)))])
            elif isinstance(decl.var_type, Long):
                new_init = Initial([Constant(StaticInit.LongInit(Const.constLong(init_val)))])
            elif isinstance(decl.var_type, ULong):
                new_init = Initial([Constant(StaticInit.ULongInit(Const.constULong(init_val)))])
            elif isinstance(decl.var_type, Double):
                new_init = Initial([Constant(StaticInit.DouleInit(Const.constDouble(float(init_val))))])
            else:
                raise SyntaxError("Unsupported type for constant initializer", decl.storage_class)
        else:
            print(decl)
            raise SyntaxError("Non-constant initializer!", decl.storage_class)
    
    # Determine the linkage: globals are those that are not static.
    global_scope = not isinstance(decl.storage_class, Static)
    var_name = decl.name.name

    # Check for redeclarations in the symbol table.
    if var_name in symbols:
        old_decl = symbols[var_name]
        if type(old_decl['val_type']) != type(decl.var_type) and old_decl['attrs'].global_scope and global_scope:
            raise SyntaxError('Cannot redeclare variable with different type')
        if not isinstance(old_decl['type'], Int):
            raise TypeError("Function redeclared as variable")
        if isinstance(old_decl['val_type'],Array) and isinstance(decl.var_type,Array) : 
        
            if old_decl['val_type']._int.value._int != decl.var_type._int.value._int:
                raise TypeError('Array redeclared with different value')
        old_global_scope = old_decl['attrs'].global_scope
        if isinstance(decl.storage_class, Extern):
            final_linkage = old_global_scope
        else:
            if old_global_scope != global_scope:
                raise ValueError("Conflicting variable linkage")
            final_linkage = old_global_scope

        old_init = old_decl['attrs'].init

        def is_initial(i): return isinstance(i, Initial)
        def is_tentative(i): return isinstance(i, Tentative)
        def is_noinit(i): return isinstance(i, NoInitializer)

        if is_initial(old_init):
            if is_initial(new_init):
                raise ValueError("Conflicting file-scope variable definitions")
            else:
                final_init = old_init
        elif is_tentative(old_init):
            if is_initial(new_init):
                final_init = new_init
            else:
                final_init = old_init
        elif is_noinit(old_init):
            if is_initial(new_init) or is_tentative(new_init):
                final_init = new_init
            else:
                final_init = old_init
        else:
            raise RuntimeError("Unknown initializer type in old declaration")
    else:
        final_linkage = global_scope
        final_init = new_init

    attrs = StaticAttr(init=final_init, global_scope=final_linkage)
    symbols[var_name] = {
        'type': Int(),  # placeholder type (adjust as needed)
        'val_type': decl.var_type,
        'attrs': attrs,
        'ret': decl.var_type,
        'Double': decl.var_type,
    }




def zero_initializer(_type):
 
    if isinstance(_type,Array):
        
        if _type._type and isinstance(_type._type,Array):
            print(_type._type)
            # 
            e=CompoundInit(initialzier=[zero_initializer(_type._type._type)])
            e.set_type(_type._type)
            print(e._type)
            # 
            return e
    if isinstance(_type,Int):
        e= SingleInit(Constant(ConstInt(0),_type=_type))
        e.set_type(_type)
        return SingleInit(Constant(ConstInt(0),_type))
    if isinstance(_type,Long):
        e= SingleInit(Constant(ConstLong(0)))
        e.set_type(_type)
        
        return e
    if isinstance(_type,UInt):
        e= SingleInit(Constant(ConstUInt(0),_type))
        e.set_type(_type)
        
        return e
    if isinstance(_type,ULong):
        e= SingleInit(Constant(ConstULong(0),_type))
        e.set_type(_type)
        
        return e
    if isinstance(_type,Double):
        e= SingleInit(Constant(ConstDouble(0),_type))
        e.set_type(_type)
        
        return e

i=0
def typecheck_init(target_type,init,symbols):
    
    if isinstance(target_type,Array) and isinstance(init,CompoundInit):
        # print('Target type',target_type)
        # print('Init',[init for init in init.initializer])
        # 
        # print('jr')
        if len(init.initializer) > int(target_type._int.value._int):
            # print(target_type._type)
            # print(target_type._int.value._int)  
            # print(len(init.initializer))
            # print(target_type._int.value._int)
            raise TypeError('Wrong no of valus in initializer')
        typechecked_list = []
        for init_elem in init.initializer:
        
            typechecked_elem = typecheck_init(target_type._type,init_elem,symbols)
            typechecked_list.append(typechecked_elem)
        
        print(target_type)
        while len(typechecked_list)<target_type._int.value._int:
            typechecked_list.append(zero_initializer(target_type._type)) 
            init.initializer = typechecked_list
        init.set_type(target_type)
        print('Exit compound init',init)
        return init
    if isinstance(init,SingleInit):
        print('Single init',init)
        typechecked_exp = typecheck_exp_and_convert(init.exp, symbols)
        print('typed elem',typechecked_exp)
      
        cast_exp = convert_by_assignment(typechecked_exp, target_type)
        init.exp=cast_exp
        init.set_type(target_type)
        print('Exit single init',init)
        return init
        # return set_type(SingleInit(cast_exp), target_type)    
    else:
       
        raise TypeError("can't initialize a scalar object with a compound initializer")
    
x1=0

def typecheck_local_vairable_declaration(decl: VarDecl, symbols: dict):
    try:
        # print(decl)
        print('Variable declaration',decl.name)
        if isinstance(decl.storage_class, Extern):
            if not isinstance(decl.init, Null):
                raise SyntaxError('Initializer on local extern variable declaration')
            if decl.name.name in symbols:
                old_decl = symbols[decl.name.name]
                if type(old_decl['val_type']) != type(decl.var_type):
                    raise SyntaxError('Cannot redeclare variable with different type')
                if not isinstance(old_decl['type'], Int):
                    raise SyntaxError('Function redeclared as variable')
            else:
                symbols[decl.name.name] = {
                    'type': Int(),
                    'val_type': decl.var_type,
                    'attrs': StaticAttr(init=NoInitializer(), global_scope=True),
                    'ret': decl.var_type,
                    'Double': decl.var_type,
                    
                }
            print('Exit var decl',decl.name)
            return decl
        # TODO CHECK THIS CONDITION
        
        elif isinstance(decl.storage_class, Static):
            print('Static init',decl)
            # 
            # 
        #     if isinstance(decl.var_type,Pointer) :
        # if not isinstance(decl.init,AddOf):
        #     raise ValueError('Static pointer initialized with non pointer value.')
        # new_
            if isinstance(decl.init, SingleInit) and isinstance(decl.var_type,Array):
                    raise ValueError("Array initializer must be a CompoundInit")
            if isinstance(decl.init,CompoundInit):
                print('static var found',decl)
                
                typecheck_init(decl.var_type,decl.init,symbols)
                print('After typecheck init')
                # print(decl)
                initial_value=Initial(typecheck_array_init(decl.init,decl.var_type))
                print('Initial value',initial_value)
                
                # print(initial_value)
                # 
            elif isinstance(decl.init, Null):
                initial_value = Initial([Constant(IntInit(ConstInt(0)))])
            elif isinstance(decl.init.exp, Constant):
                if isinstance(decl.init.exp.value,ConstInt):
                    initial_value = Initial([Constant(IntInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstLong):
                    initial_value = Initial([Constant(LongInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstDouble):
                    initial_value = Initial([Constant(DoubleInit(decl.init.exp.value))])
                 
            else:
                raise SyntaxError('Non-constant Initializer on local static variable', decl.init)

            
            # 
            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': StaticAttr(init=initial_value, global_scope=False),
                'ret': decl.var_type,
                'Double':decl.var_type
                
            }
            print('Exit var decl',decl.name)
            
            return decl
        else:
            
            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': LocalAttr(),
                'ret': decl.var_type,
                'Double':decl.var_type
            }
            
            if not isinstance(decl.init, Null):
                print('Type checking init of local var')
                # print(decl)
                if isinstance(decl.var_type,Array) and isinstance(decl.init,SingleInit):
                    raise ValueError('Array initializer must be a compound initializer')
               
                    
                if isinstance(decl.var_type,Pointer) and isinstance(decl.var_type.ref,Array):
                    # exit()
                    if isinstance(decl.init.exp,AddOf):
                        if decl.init.exp.exp.identifier.name in symbols:
                            if decl.var_type.ref._int.value._int != symbols[decl.init.exp.exp.identifier.name]['val_type']._int.value._int:
                                raise TypeError('Array redeclared with different value')
                
                if isinstance(decl.var_type,Pointer) and isinstance(decl.init.exp,Constant):
                    if isinstance(decl.init.exp.value._type,Double):
                        
                        raise ValueError('Pointer initialized with double value')
                    
                
                x = typecheck_init(decl.var_type,decl.init, symbols)
                if isinstance(decl.var_type,Pointer) and (
                    (isinstance(x,Constant) or isinstance(x,Var)) and
                    not isinstance(x.get_type(),Pointer)):
                
                    if (not isinstance(x.get_type(),Int)) and (not isinstance(decl.var_type.ref,type(x.get_type()))):
                        raise ValueError('Invalid pointer init')
                    if isinstance(x.get_type(),Int) and isinstance(x,Var):
                        raise ValueError('Invalid pointer init')
                        
                if isinstance(decl.init,AddOf) and not isinstance(decl.init.exp,Var):
                    raise ValueError('Invalid l value')
                
                
                decl.init=x
                decl.init=convert_to(decl.init,decl.var_type)
            print('Exit var decl',decl.name)
            
            return decl
                
    except Exception as e:
        raise e


# def check_fun_decl_compatibility(decl, old_decl):
#     """
#     Compares the new function declaration (decl) against the previously seen
#     function declaration (old_decl) and raises SyntaxError if there are any
#     mismatches in parameter types.
    
#     Expected differences:
#       - If a parameter in the new declaration is given as an array type,
#         then the corresponding parameter in the old declaration should be a
#         pointer to an array. In that case, we compare the sizes of the arrays.
#     """
#     new_fun_type = decl.fun_type
#     old_fun_type = old_decl['fun_type']
#     # First, check that the parameter counts match.
#     if new_fun_type.param_count != old_fun_type.param_count:
#         raise SyntaxError("Function parameter count mismatch: "
#                           f"{new_fun_type.param_count} vs {old_fun_type.param_count}")
    
#     # For each parameter, compare the types.
#     # (We assume new_fun_type.params may contain either Array types or Parameter objects.)
#     for new_param, old_param in zip(new_fun_type.params, old_fun_type.params):
#         # Case 1: New parameter is given as an Array type.
#         if isinstance(new_param, Array):
#             # We expect the corresponding old parameter to be a Parameter
#             # whose type is a Pointer to an Array.
#             if not (isinstance(old_param, Parameter) and isinstance(old_param._type, Pointer)):
#                 raise SyntaxError("Function parameter mismatch: expected old parameter to be a pointer type.")
            
#             # Extract the array types.
#             new_array = new_param
#             old_array = old_decl['fun_type'].params
#             print('New array',new_array)
#             print(old_array)
#             # Compare the expected sizes (assuming the .int field holds a Constant with _int).
#             new_size = new_array._int.value._int
#             # print(new_size)
#             print(old_decl)
#             # exit()
#             old_size = len(old_array)
            
#             # if new_size != old_size:
#             #     raise SyntaxError("Function is defined with different array parameter sizes: "
#             #                       f"new size {new_size} vs old size {old_size}")
#         # Case 2: New parameter is a Parameter (not declared as an array).
#         elif isinstance(new_param, Parameter):
#             # For a non-array parameter, we can perform a direct type comparison.
#             if new_param._type != old_param._type:
#                 raise SyntaxError("Function parameter type mismatch: "
#                                   f"new type {new_param._type} vs old type {old_param._type}")
#         # else:
#     # print('reraefaf')
#         #     raise SyntaxError("Unrecognized parameter type in new function declaration.")

def check_fun_decl_compatibility(decl, old_decl):

    """
    Compares the new function declaration (decl) against the previous declaration (old_decl)
    and raises SyntaxError if there are mismatches in parameter types.
    
    Redeclaration rules:
      - For an array parameter, the outermost dimension is ignored (adjusted to a pointer).
      - For one-dimensional array parameters, any difference in the outer size is ignored.
      - For multi-dimensional arrays, the inner dimensions must match.
    
    Example:
      int array_param(int a[5]);         // adjusted to int (*a)[ ]
      int array_param(int a[2]);         // OK: outer dimension ignored
      
      int nested_array_param(int a[2][3]);    // adjusted to int (*a)[3]
      int nested_array_param(int (*a)[3]);      // must match inner dimension (3)
    """
    new_fun_type = decl.fun_type
    old_fun_type = old_decl['fun_type']
    
    if new_fun_type.param_count != old_fun_type.param_count:
        raise SyntaxError("Function parameter count mismatch: "
                          f"{new_fun_type.param_count} vs {old_fun_type.param_count}")
    
    for new_param, old_param in zip(new_fun_type.params, old_fun_type.params):
        # If the new parameter is declared as an Array, its outer dimension is ignored.
        if isinstance(new_param, Array):
            # Adjust the new parameter: the effective type is the element type.
            new_adjusted = new_param._type  # For a parameter declared as int a[5],
                                            # new_adjusted is Int (or, in the multidimensional case, Array(...))
            # The old parameter should be a Parameter whose type is a Pointer.
            if not (isinstance(old_param, Parameter) and isinstance(old_param._type, Pointer)):
                raise SyntaxError("Function parameter mismatch: expected old parameter to be a pointer type.")
            old_adjusted = old_param._type.ref  # This is what the pointer points to.
            
            # For one-dimensional arrays, we ignore any size differences.
            if not isinstance(new_adjusted, Array):
                # Compare element types.
                if not isinstance(new_adjusted,type(old_adjusted)):
                    raise SyntaxError("Function parameter type mismatch: "
                                      f"new element type {new_adjusted} vs old element type {old_adjusted}")
            else:
                # For multi-dimensional arrays, compare the inner array sizes.
                new_inner_size = new_adjusted._int.value._int
                if not isinstance(old_adjusted, Array):
                    raise SyntaxError("Function parameter mismatch: new parameter is multi-dimensional but old parameter is not.")
                old_inner_size = old_adjusted._int.value._int
                if new_inner_size != old_inner_size:
                    raise SyntaxError("Function is defined with different inner array parameter sizes: "
                                      f"new inner size {new_inner_size} vs old inner size {old_inner_size}")
        # If the new parameter is already a Parameter (not declared as an array)
        elif isinstance(new_param, Parameter):
            print(new_param._type)
            print(old_param._type)
            if not isinstance(new_param._type,type( old_param._type)):
                raise SyntaxError("Function parameter type mismatch: "
                                  f"new type {new_param._type} vs old type {old_param._type}")
      

def typecheck_function_declaration(decl: FunDecl, symbols: dict, is_block_scope):
    if isinstance(decl.fun_type,FunType) and isinstance(decl.fun_type.base_type,Array):
    
        raise TypeError('Function type cannot be an array')
    adjusted_params = []

    for param in decl.params:
        # print(param)
        param_name = param.name.name

        if isinstance(param._type,Array):
            adjusted_type = Pointer(param._type._type)
            
            adjusted_params.append(Parameter(adjusted_type,name=Identifier(param_name)))
        else:
            adjusted_params.append(param)
    decl.params=adjusted_params

    fun_name = decl.name.name
    fun_type = FunType(param_count=len(decl.params), params=decl.params, base_type=decl.fun_type.base_type)
    has_body = decl.body is not None and not isinstance(decl.body, Null)
    already_defined = False
    _global = decl.storage_class
    if not isinstance(_global, Static):
        _global = True
    else:
        _global = False

    print('Inside fundecl')
    if fun_name in symbols:
        old_decl = symbols[fun_name]
        check_fun_decl_compatibility(decl, old_decl)
           
        
        if 'fun_type' not in old_decl:
            raise SyntaxError(f"Identifier '{fun_name}' previously declared as a variable.")
        already_defined = old_decl['attrs'].defined

        if old_decl['fun_type'].param_count != fun_type.param_count:
            raise SyntaxError(
                f"Incompatible function declarations for '{fun_name}'. "
                f"Expected {old_decl['fun_type'].param_count} parameters, got {fun_type.param_count}."
            )
            
    
        # 
        if type(old_decl['fun_type'].base_type) != type(fun_type.base_type):
            raise SyntaxError(f"Function '{fun_name}' has conflicting return types.")
        old_decl_params = [param._type for param in old_decl['fun_type'].params]
        new_decl_params = [param._type for param in decl.params]
        for i in range(len(old_decl_params)):
            if not (type(old_decl_params[i]) == type(new_decl_params[i])):
                raise SyntaxError("Function is defined with diff params")

        if already_defined and has_body:
            raise SyntaxError("Function is defined more than once")

        if old_decl['attrs'].global_scope and isinstance(decl.storage_class, Static):
            raise SyntaxError('Static funtion declaration follow a non static ')

        if is_block_scope:
            if _global and isinstance(decl.storage_class, Static):
                raise SyntaxError('a block-scope function may only have extern storage class')

        _global = old_decl['attrs'].global_scope
        attrs = FunAttr(defined=(already_defined or has_body), global_scope=_global)
        symbols[fun_name] = {
            'fun_type': FunType(param_count=len(decl.params), params=decl.params, base_type=decl.fun_type.base_type),
            'attrs': attrs
        }

        if has_body:
            for param in decl.params:
                param_name = param.name.name
                # print(param_name)
                # 
                # if isinstance(param._type,Array):
                #     adjusted_type = Pointer(ref=param._type._int)
                #     adjusted_params.append(Parameter(adjusted_type,name=param_name))
                # else:
                #     adjusted_params.append(param)
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(),'val_type':param._type,'ret':fun_type.base_type,'attrs':None}
            # decl.params=adjusted_params
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                    print(fun_type)
                    typecheck_statement(decl.body, symbols, fun_type.base_type)
                    
                else:
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp_and_convert(stmt.exp, symbols, fun_type.base_type) 
                        convert_to(typed_return, decl.fun_type)
    else:
      
        if is_block_scope:
            if not _global and isinstance(decl.storage_class, Static):
                raise SyntaxError('a block-scope function may only have extern storage class')
        
        symbols[fun_name] = {
            'fun_type': FunType(param_count=len(decl.params), params=decl.params, base_type=decl.fun_type.base_type),
            'attrs': FunAttr(defined=has_body, global_scope=_global)
        }

        if has_body:
            
            # adjusted_params = []
            # print(decl.params)
            # 
            for param in decl.params:
                print(param.name)
                # 
                param_name = param.name.name

                # if isinstance(param._type,Array):
                #     adjusted_type = Pointer(param._type._type)
                    
                #     adjusted_params.append(Parameter(adjusted_type,name=param_name))
                # else:
                #     adjusted_params.append(param)
                # print(param_name)
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(), 'val_type':param._type,'ret': decl.fun_type,'attrs':None,'Double':param._type}
            # decl.params=adjusted_params
            stmts=[]
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                    print('\nType checking statement',stmt,decl.fun_type.base_type)  
                    typecheck_statement(stmt, symbols, decl.fun_type.base_type)
                    print('\nType checking statement end',stmt,decl.fun_type.base_type)  
                 
                  
                else:
                    print('Found return')
                 
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp_and_convert(stmt.exp, symbols, decl.fun_type.base_type)
                        cast=convert_to(typed_return, decl.fun_type)
                        stmts.append(cast)
    
    
temp=0                                            
def typecheck_exp(e: Exp, symbols: dict, func_type=Optional):
    # print(e)
    # 
    """
    Type checks an expression node 'e', possibly skipping if we've visited it already.
    """
    # -------------------------------------------------------------------------
    # 1) If we've already typed this node in the same pass, skip re-check
    # -------------------------------------------------------------------------
  

    # -------------------------------------------------------------------------
    # 2) Actual type-checking logic
    # -------------------------------------------------------------------------
    if isinstance(e, FunctionCall):
            
        fun_name = e.identifier.name
        if fun_name not in symbols:
            raise NameError(f"Function '{fun_name}' is not defined.")
        fun_entry = symbols[fun_name]
        for arg, param in zip(e.args, symbols[e.identifier.name]['fun_type'].params):
            print('Here')
            if isinstance(arg, AddOf) and isinstance(symbols[arg.exp.identifier.name]['val_type'], Array):
                # print(param.)
                # exit()
                if isinstance(param._type, Pointer) and isinstance(param._type.ref, Pointer):
                    # print(symbols[arg.exp.identifier.name]['val_type'])
                    if not isinstance(param._type.ref, type(symbols[arg.exp.identifier.name]['val_type'])):
                        # print('here')
                        raise ValueError('Invalid pointer type')


        # if isinstance(symbols[e.args[0].exp.identifier.name]['val_type'],Array) and isinstance(symbols[e.identifier.name]['fun_type'].params[0],Pointer):
        # # print(symbols[e.args[0].exp.identifier.name]['val_type'])
        # # print(symbols[e.identifier.name]['fun_type'].params)
        # # print(e.args)
        # # for param in symbols print([e.identifier.name]['fun_type'].params) and for arg in :
            
        # exit()
        if not isinstance(fun_entry.get('fun_type'), FunType):
            raise SyntaxError(f"Variable '{fun_name}' used as a function.")

        f_type: FunType = fun_entry['fun_type']
        if f_type.param_count != len(e.args):
            raise SyntaxError(
                f"Function '{fun_name}' called with wrong number of arguments. "
                f"Expected {f_type.param_count}, got {len(e.args)}."
            )

        converted_args = []
        params = [val._type for val in f_type.params]
        for (arg, paramType) in zip(e.args, params):
            typed_arg = typecheck_exp_and_convert(arg, symbols)  
            print('Typed arg',typed_arg)
            print('Param type',paramType)
            if isinstance(paramType,Pointer):
                converted_args.append(convert_by_assignment(typed_arg, paramType))
            else:
                converted_args.append(convert_by_assignment(typed_arg, paramType))
                
            print('Converted args',converted_args)
        e.args = converted_args
        e.set_type(f_type.base_type)
        print('Type checked function call')
        return e

    elif isinstance(e, Var):
        var_name = e.identifier.name

        if var_name not in symbols:
            raise NameError(f"Variable '{var_name}' is not defined.")
        var_entry = symbols[var_name]
       
        if 'type' not in var_entry:
            raise SyntaxError(f"Function '{var_name}' used as a variable.")

        var_type = var_entry['type']
        if not isinstance(var_type, Int):
            raise SyntaxError(f"Identifier '{var_name}' does not have type Int.")
        e.set_type(var_entry['val_type'])
       
        return e

    elif isinstance(e, Return):
        # 
        global x
        if x==1:
            print('\nReturn Expression',e,func_type)
        x+=1
        if e.exp is not None and not isinstance(e.exp, Null):
            if func_type is not None:
                # print('Here')
                e.exp=typecheck_exp_and_convert(e.exp, symbols, func_type) 
                # print(e.exp)   
                # 
                e.exp=convert_by_assignment(e.exp, func_type)
                
                return e
   
        return e

    elif isinstance(e, Constant):
        if isinstance(e.value, ConstInt):
            # e.set_type(Int())
            e.set_type(Int())
            return e
        elif isinstance(e.value, ConstLong):
            # e.set_type(Long())
            e.set_type(Long())
            return e
        elif isinstance(e.value, ConstULong):
            # e.set_type(Long())
            e.set_type(ULong())
            return e
        elif isinstance(e.value, ConstUInt):
            e.set_type(UInt())
            return e 
        elif isinstance(e.value,ConstDouble):
            e.set_type(Double())
            return e
        else:
            raise SyntaxError('Invalid value const')

    elif isinstance(e, Cast):
        # print('Inside cast')
        # if isinstance(e.target_type,Array):
        #     raise ValueError('Cant type cast to arry')
        
        typed_inner = typecheck_exp_and_convert(e.exp, symbols)
        e.exp = typed_inner
        
        if( isinstance(e.target_type,Pointer) and isinstance(typed_inner.get_type(),Double))or ( 
            isinstance(e.target_type,Double) and isinstance(typed_inner.get_type(),Pointer)):
            raise SyntaxError('Cannot cast pointer to double / double to a pointer')
          
        e.set_type(e.target_type)
        return e

    elif isinstance(e, Assignment):
        
        
        type_left = typecheck_exp_and_convert(e.left, symbols)
        type_right = typecheck_exp_and_convert(e.right, symbols)
        
       
        left_type = type_left.get_type()
        
        if isinstance(type_left,AddOf) and isinstance(type_left.exp._type,Array) :
            raise ValueError('Cannot assign to array')
            
      
        print('Type Left',type_left)
        print('Type Right',type_right)
        
        print(left_type)
        
        if  isinstance(type_left.get_type(),Pointer) and isinstance(type_right.get_type(),Pointer):
            if type(type_left.get_type().ref)!=type(type_right.get_type().ref):
                raise SyntaxError('Cannot assign one pointer type to another')
    
        converted_right = convert_by_assignment(type_right, left_type)
        e.left = type_left
        e.right = converted_right
        e.set_type(left_type)
        return e

    elif isinstance(e, Binary):
        print('Type check binary statement')
        if e.operator in (BinaryOperator.EQUAL,BinaryOperator.NOT_EQUAL):
            typed_e1 = typecheck_exp_and_convert(e.left, symbols)
            typed_e2 = typecheck_exp_and_convert(e.right, symbols)
            t1 = typed_e1.get_type()
            t2 = typed_e2.get_type()
            print('In Binary')
            print('Type of exp 1',t1)
            print('Type of exp 2',t2)
            # 
            global temp
           
            if isinstance(t1,Pointer) or isinstance(t2,Pointer):
                print(t1)
                print(t2)
                common_type = get_common_pointer_type(typed_e1, typed_e2)
                print('Common type',common_type)
                #  
            else:
                common_type = get_common_type(t1, t2)
            converted_e1 = convert_to(typed_e1, common_type)
            converted_e2 = convert_to(typed_e2, common_type)

            e.left=converted_e1
            e.right=converted_e2
          
            e.set_type(Int())
            
            return e
      
        else:
           
            typed_e1 = typecheck_exp_and_convert(e.left, symbols)
            typed_e2 = typecheck_exp_and_convert(e.right, symbols)
            
            
            
            if e.operator in (BinaryOperator.MULTIPLY, BinaryOperator.DIVIDE, BinaryOperator.REMAINDER):
                if isinstance(typed_e1.get_type(),Pointer) or isinstance(typed_e2.get_type(),Pointer):
                    raise SyntaxError('Cannot perform mul, divide , modulo arithmetic operations on pointers')
            if e.operator in (BinaryOperator.EQUAL,BinaryOperator.GREATER_OR_EQUAL,
                                   BinaryOperator.GREATER_THAN,
                                   BinaryOperator.LESS_OR_EQUAL,
                                   BinaryOperator.LESS_THAN,BinaryOperator.NOT_EQUAL):
                if (isinstance(typed_e1.get_type(),Pointer) and not 
                    isinstance(typed_e2.get_type(),Pointer)) or (
                    isinstance(typed_e2.get_type(),Pointer) and 
                    not isinstance(typed_e1.get_type(),Pointer)):
                    raise SyntaxError('Cannot perform comparison between on pointer and non pointer')
                
                
            if e.operator in (BinaryOperator.AND, BinaryOperator.OR):
                e.left = typed_e1
                e.right = typed_e2
                e.set_type(Int())
                e.rel_flag = Int()
                
                return e
                
        
            t1 = typed_e1.get_type()
            t2 = typed_e2.get_type()
            
            if (isinstance(t1,Pointer) and isinstance(t2,Pointer)) and e.operator in (BinaryOperator.GREATER_OR_EQUAL,
                                                                                       BinaryOperator.GREATER_THAN,
                                                                                       BinaryOperator.LESS_OR_EQUAL,
                                                                                       BinaryOperator.LESS_THAN):
                # print('fgualfjhaglf')
                if isinstance(t1.ref,type(t2.ref)):
                    
                    e.set_type(Int())
                    e.rel_flag=Int()
                    return e 
                else:
                    raise ValueError('Pointer of two different types cannot be used for relational op')
            
            
            if (isinstance(t1,Pointer) and not isinstance(t2,Pointer) and e.operator in (BinaryOperator.ADD,BinaryOperator.SUBTRACT)):
                if isinstance(t2,Double):
                    raise ValueError('Cannot add / substract double form a pointer')
               
                converted_e2 = convert_to(typed_e2, Long())
                e=Binary(e.operator,typed_e1,converted_e2)
                e.set_type(t1)
                e.rel_flag=Long()
                return e
            elif (not isinstance(t1,Pointer) and  isinstance(t2,Pointer) and e.operator == BinaryOperator.ADD):
                converted_e1 = convert_to(typed_e1, Long())
                e=Binary(e.operator,converted_e1,typed_e2)
                e.rel_flag=Long()
                e.set_type(t2)
                return e
            elif ((isinstance(t1,Pointer) and  isinstance(t1.ref,type(t2.ref))) and e.operator == BinaryOperator.SUBTRACT):
                print(t1)
                print(isinstance(t2.ref,type(t2.ref)))
            
                print('Subtract')
                
                e=Binary(operator=e.operator,left=typed_e1,right=typed_e2)
                e.set_type(Long())
                e.rel_flag=Long()
                return e           
            elif not isinstance(t1,Pointer) and not isinstance(t2,Pointer):
                if e.operator==BinaryOperator.REMAINDER :
                    if isinstance(t1,Double) or isinstance(t2,Double):
                        raise ValueError('Cannot apply modulo to a double')
        
                
                common_type = get_common_type(t1, t2)
                
                converted_e1 = convert_to(typed_e1, common_type)
                converted_e2 = convert_to(typed_e2, common_type)
                e.left = converted_e1
                e.right = converted_e2

                if e.operator in (BinaryOperator.ADD, BinaryOperator.DIVIDE,
                                BinaryOperator.MULTIPLY, BinaryOperator.SUBTRACT,
                                BinaryOperator.REMAINDER):
                    e.rel_flag = common_type
                    e.set_type(common_type)
                
                    return e 
                else:
                    if isinstance(e.left.get_type(),Double):
                        e.rel_flag =Int()
                        print(e)
                        
                        e.set_type(Int())
                    else:
                        e.rel_flag = Int()
                        e.set_type(Int())
                    return e
            else:
                raise ValueError('Invalid value for operands')

                
    elif isinstance(e, Unary):
        inner = typecheck_exp_and_convert(e.expr, symbols)
        e.expr = inner
        if e.operator == UnaryOperator.NOT:
            e.set_type(Int())
            return e
        if e.operator==UnaryOperator.COMPLEMENT :
            if isinstance(e.expr.get_type(),(Double,Pointer)):
                raise SyntaxError('Cannot complement of double')
            e.set_type(inner.get_type())
        elif e.operator == UnaryOperator.NEGATE:
            if isinstance(e.expr.get_type(),Pointer):
                raise SyntaxError('Cannot negate a pointer')
            e.set_type(inner.get_type())
        else:
            if isinstance(inner.get_type(),Pointer):
                e.set_type(inner.get_type().ref)
            else:
                e.set_type(inner.get_type())
        return e

    elif isinstance(e, Conditional):
        typed_condition = typecheck_exp_and_convert(e.condition, symbols) if e.condition else None
        typed_exp2 = typecheck_exp_and_convert(e.exp2, symbols) if e.exp2 else None
        typed_exp3 = typecheck_exp_and_convert(e.exp3, symbols) if e.exp3 else None

        if typed_exp2 is None or typed_exp3 is None:
            raise SyntaxError("Malformed Conditional expression")

        t2 = typed_exp2.get_type()
        t3 = typed_exp3.get_type()
        if isinstance(t2,Pointer) or isinstance(t3,Pointer):
            common_type = get_common_pointer_type(typed_exp2, typed_exp3)
        else:
            common_type = get_common_type(t2, t3)
            
        # common_type = get_common_type(t2, t3)
        converted_e2 = convert_to(typed_exp2, common_type)
        converted_e3 = convert_to(typed_exp3, common_type)

        e.condition = typed_condition
        e.exp2 = converted_e2
        e.exp3 = converted_e3
        e.set_type(common_type)
        return e

    elif isinstance(e,Dereference):
        typed_inner = typecheck_exp_and_convert(e.exp, symbols)
        print(typed_inner)
        # 
        if not isinstance(typed_inner.get_type(), Pointer):
            raise SyntaxError("Dereference operator applied to non-pointer type")
        e.exp=typed_inner
        # deref_exp = Dereference(typed_inner)
        e.set_type(typed_inner.get_type().ref)
        # print(deref_exp)
        
        # 
        return e
    
    elif isinstance(e, AddOf):
        print('Add of expr')
        if not isinstance(e.exp, Constant) and isinstance(e.exp, (Var,Subscript,Dereference)):
           
            typed_inner = typecheck_exp(e.exp, symbols)
            
            # print(typed_inner.get_type()._type)
            # exit()
            referenced_t = typed_inner.get_type()
            # if isinstance(referenced_t,Array):
            #     referenced_t = referenced_t._type
            e.exp= typed_inner
            e.exp.set_type(Pointer(referenced_t))
            e.set_type(Pointer(referenced_t))
            if func_type is not None and isinstance(func_type,Pointer):
                if type(e.get_type().ref) != type(func_type.ref):
                    raise ValueError('Invalid return value')
            return e
        else:
            raise SyntaxError("Address-of operator applied to non-variable")

    elif isinstance(e,Pointer):
        e.set_type(Pointer(e.ref))
        return e
    
    elif isinstance(e, Null):
        return e

    elif isinstance(e,Identifier):
        return typecheck_statement(e.name,symbols)
    
    elif isinstance(e,Subscript):
        
        typed_e1 = typecheck_exp_and_convert(e.exp1, symbols)
        typed_e2 = typecheck_exp_and_convert(e.exp2, symbols)
        t1 = typed_e1.get_type()
        t2 = typed_e2.get_type()
        if isinstance(t1,Double) or isinstance(t2,Double):
            raise TypeError("Subscript must have integral type.")
    
        if isinstance(t1,Pointer) and not isinstance(t2,Pointer):
        # 1 if t1 is a pointer type and t2 is an integer type:
            ptr_type = t1
            typed_e2 = convert_to(typed_e2, Long())
        elif not isinstance(t1,Pointer) and isinstance(t2,Pointer):
            ptr_type = t2
            typed_e1 = convert_to(typed_e1, Long())
        else:
            raise ValueError("Subscript must have integer and pointer operands")
        e.exp1 = typed_e1
        e.exp2=typed_e2
        e.set_type(ptr_type.ref)
        return e
    else:
        raise TypeError(f"Unsupported expression type for type checking: {type(e)}")

def typecheck_statement(statement: Statement, symbols: dict, fun_type=Optional[str]):
    print(statement)
    # #fun_type)
    if isinstance(statement, list):
        for stmt in statement:
            typecheck_statement(stmt, symbols, fun_type)
        return statement

    if isinstance(statement, VarDecl):
        typecheck_local_vairable_declaration(statement, symbols)

    elif isinstance(statement, InitDecl):
        typecheck_statement(statement.declaration.declaration, symbols, fun_type)

    elif isinstance(statement, InitExp):
        typecheck_statement(statement.exp, symbols, fun_type)

    elif isinstance(statement, FunDecl):
        typecheck_function_declaration(statement, symbols, is_block_scope=True)

    elif isinstance(statement, (Break, Continue)):
        pass

    elif isinstance(statement, Expression):
        typecheck_exp_and_convert(statement.exp, symbols, fun_type)

    elif isinstance(statement, (While, For, DoWhile)):
        if isinstance(statement, While):
            typecheck_exp_and_convert(statement._condition, symbols, fun_type)
            typecheck_statement(statement.body, symbols, fun_type)
        elif isinstance(statement, For):
            if isinstance(statement.init, InitDecl):
                if statement.init and not isinstance(statement.init, Null):
                    if isinstance(statement.init.declaration.declaration, VarDecl):
                        if isinstance(statement.init.declaration.declaration.storage_class, (Extern, Static)):
                            raise SyntaxError('Loop initializer cannot have storage class')
                        else:
                            typecheck_statement(statement.init, symbols, fun_type)
                            # print(s)
                            # 
            else:
                typecheck_statement(statement.init, symbols, fun_type)

            if statement.condition:
                typecheck_exp_and_convert(statement.condition, symbols, fun_type)
            if statement.post:
                typecheck_exp_and_convert(statement.post, symbols, fun_type)
            typecheck_statement(statement.body, symbols, fun_type)

        elif isinstance(statement, DoWhile):
            typecheck_statement(statement.body, symbols, fun_type)
            typecheck_exp_and_convert(statement._condition, symbols, fun_type)

    elif isinstance(statement, Compound):
        for stmt in statement.block:
            typecheck_statement(stmt, symbols, fun_type)

    elif isinstance(statement, S):
        typecheck_statement(statement.statement, symbols, fun_type)

    elif isinstance(statement, D):
        if isinstance(statement.declaration, FunDecl):
            typecheck_function_declaration(statement.declaration, symbols, is_block_scope=True)
        elif isinstance(statement.declaration, VarDecl):
            typecheck_local_vairable_declaration(statement.declaration, symbols)
        else:
            raise TypeError(f"Unsupported declaration type in D: {type(statement.declaration)}")

    elif isinstance(statement, Conditional):
        typecheck_exp_and_convert(statement, symbols, fun_type)

    elif isinstance(statement, If):
        typecheck_exp_and_convert(statement.exp, symbols, fun_type)
        typecheck_statement(statement.then, symbols, fun_type)
        if statement._else:
            typecheck_statement(statement._else, symbols, fun_type)

    elif isinstance(statement, FunctionCall):
        typecheck_exp_and_convert(statement, symbols, fun_type)

    elif isinstance(statement, Return):
            typecheck_exp(statement, symbols,fun_type)

    elif isinstance(statement, (Expression, Assignment, Binary, Unary)):
        typecheck_exp_and_convert(statement, symbols, fun_type)

    elif isinstance(statement, Cast):
        typecheck_exp_and_convert(statement, symbols, fun_type)

    elif isinstance(statement, Var):
        typecheck_exp_and_convert(statement, symbols, fun_type)

    elif isinstance(statement, Constant):
        typecheck_exp_and_convert(statement, symbols, fun_type)

    elif isinstance(statement, Null):
        pass

    else:
        raise TypeError(f"Unsupported statement type for type checking: {type(statement)}")

    return statement

def typecheck_program(program: Program):
    """
    Initiates the type checking process for the entire program.
    """
    symbols = {}
    for stmt in program.function_definition:
        print('Type checking',stmt)
        if isinstance(stmt, VarDecl):
          
            typecheck_file_scope_variable_declaration(stmt, symbols)
        elif isinstance(stmt, FunDecl):
            print('Fun decl')
            print(stmt)
            
            typecheck_function_declaration(stmt, symbols, False)
        else:
           
            typecheck_statement(stmt, symbols)
    return program, symbols
