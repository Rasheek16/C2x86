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
        # print(c.value)
        if isinstance(c.value,(ConstInt,ConstDouble,ConstUInt,ConstLong,ConstULong)):
            if c.value._int==0:
                return True
    return False


def convert_by_assignment(e, target_type):
    print('Expression to be converted',is_null_pointer_constant(e))
    print('Target type',target_type)
    if isinstance(e.get_type(),type(target_type)):
        return e
    if not isinstance(e.get_type(),Pointer) and not isinstance(target_type ,Pointer):
        return convert_to(e, target_type)
    if is_null_pointer_constant(e) and isinstance(target_type ,Pointer):
        return convert_to(e, target_type)
    else:
        raise SyntaxError("Cannot convert type for assignment")

def get_common_pointer_type(e1, e2):
    # print('Inside get common pointer type.')
    
    e1_t = e1.get_type()
    e2_t = e2.get_type()
    print(type(e1_t)==type(e2_t))
    if isinstance(e1_t,Pointer) and isinstance(e2_t,Pointer):
        if type(e1_t.ref)==type(e2_t.ref):
            return e1_t
        else:
            raise SyntaxError("Pointer types are not compatible")
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


def typecheck_exp_and_convert(e,symbols):
    typed_e = typecheck_exp_and_convert(e, symbols)
    
    if isinstance(typed_e.get_type(),Array):
        addr_exp = AddOf(typed_e)
        addr_exp.set_type(Pointer(typed_e._type))
        return addr_exp
    
    return typed_e

def typecheck_file_scope_variable_declaration(decl: VarDecl, symbols: dict):
   
    if not isinstance(decl.init, Null):
        typecheck_exp_and_convert(decl.init, symbols)
    
    # print(decl.init)
    if isinstance(decl.var_type,Pointer):
        if (not isinstance(decl.init,Null) and not isinstance(decl.init,AddOf)) and isinstance(decl.storage_class,Static):
            raise ValueError('Static pointer initialized with non pointer value.')
        elif isinstance(decl.init,Constant) and decl.init.value._int==0:
            new_init = Initial(Constant(StaticInit.ULongInit(Const.constULong(int(0)))))
        
    if isinstance(decl.init,Constant):
        if isinstance(decl.var_type,Int):
            new_init = Initial(Constant(StaticInit.IntInit(Const.constInt(int(decl.init.value._int)))))
        elif isinstance(decl.var_type,UInt):
            new_init = Initial(Constant(StaticInit.UIntInit(Const.constUInt(int(decl.init.value._int)))))
        elif isinstance(decl.var_type,Long):
            new_init = Initial(Constant(StaticInit.LongInit(Const.constLong(int(decl.init.value._int)))))
        elif isinstance(decl.var_type,ULong):
            new_init = Initial(Constant(StaticInit.ULongInit(Const.constULong(int(decl.init.value._int)))))
        elif isinstance(decl.var_type,Double):
            new_init = Initial(Constant(StaticInit.DouleInit(Const.constDouble(float(decl.init.value._int)))))
    elif isinstance(decl.init, Null):
        # print('Pointer')
        if isinstance(decl.storage_class, Extern):
            new_init = NoInitializer()
        else:
            new_init = Tentative()
    else:
        raise SyntaxError("Non-constant initializer!", decl.storage_class)    
    
    global_scope = not isinstance(decl.storage_class, Static)
    var_name = decl.name.name

    if var_name in symbols:
        old_decl = symbols[var_name]

        if type(old_decl['val_type']) != type(decl.var_type) and \
           old_decl['attrs'].global_scope == global_scope == True:
            raise SyntaxError('Cannot redeclare variable with different type')
        if not isinstance(old_decl['type'], Int):
            raise TypeError("Function redeclared as variable")

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
        'type': Int(),
        'val_type': decl.var_type,
        'attrs': attrs,
        'ret':decl.var_type,
        'Double':decl.var_type,
    }


def typecheck_local_vairable_declaration(decl: VarDecl, symbols: dict):
   
    try:
     
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
            return decl
        # TODO CHECK THIS CONDITION
        
        elif isinstance(decl.storage_class, Static):
        #     if isinstance(decl.var_type,Pointer) :
        # if not isinstance(decl.init,AddOf):
        #     raise ValueError('Static pointer initialized with non pointer value.')
        # new_
            if isinstance(decl.init, Constant):
                if isinstance(decl.init.value,ConstInt):
                    initial_value = Initial(Constant(IntInit(decl.init.value)))
                elif isinstance(decl.init.value,ConstLong):
                    initial_value = Initial(Constant(LongInit(decl.init.value)))
                elif isinstance(decl.init.value,ConstDouble):
                    initial_value = Initial(Constant(DoubleInit(decl.init.value)))
                    print(initial_value)
                    # exit()
            elif isinstance(decl.init, Null):
                initial_value = Initial(Constant(IntInit(ConstInt(0))))
            else:
                raise SyntaxError('Non-constant Initializer on local static variable', decl.init)

            
            # exit()
            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': StaticAttr(init=initial_value, global_scope=False),
                'ret': decl.var_type,
                'Double':decl.var_type
                
            }
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
                x = typecheck_exp_and_convert(decl.init, symbols)
                if isinstance(decl.var_type,Pointer) and ((isinstance(x,Constant) or isinstance(x,Var)) and not isinstance(x.get_type(),Pointer)):
                    print(decl.var_type)
                    print(isinstance(x.get_type(),Int))
                    if (not isinstance(x.get_type(),Int)) and (not isinstance(decl.var_type.ref,type(x.get_type()))):
                        raise ValueError('Invalid pointer init')
                    if isinstance(x.get_type(),Int) and isinstance(x,Var):
                        raise ValueError('Invalid pointer init')
                        
                if isinstance(decl.init,AddOf) and not isinstance(decl.init.exp,Var):
                    raise ValueError('Invalid l value')
                
                
                

                # x1+=1
                decl.init=x
                decl.init=convert_to(decl.init,decl.var_type)
            
            return decl
                
    except Exception as e:
        raise e

def typecheck_function_declaration(decl: FunDecl, symbols: dict, is_block_scope):
    if isinstance(decl.fun_type,FunType) and isinstance(decl.fun_type.base_type,Array):
        raise TypeError('Function type cannot be an array')
    for param in decl.params:
        param_name = param.name.name
        adjusted_params = []

        if isinstance(param._type,Array):
            adjusted_type = Pointer(param._type._type)
            
            adjusted_params.append(Parameter(adjusted_type,name=param_name))
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

    if fun_name in symbols:
        old_decl = symbols[fun_name]
        if 'fun_type' not in old_decl:
            raise SyntaxError(f"Identifier '{fun_name}' previously declared as a variable.")
        already_defined = old_decl['attrs'].defined

        if old_decl['fun_type'].param_count != fun_type.param_count:
            raise SyntaxError(
                f"Incompatible function declarations for '{fun_name}'. "
                f"Expected {old_decl['fun_type'].param_count} parameters, got {fun_type.param_count}."
            )
            
    
        # exit()
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
                if isinstance(param._type,Array):
                    adjusted_type = Pointer(ref=param._type._int)
                    adjusted_params.append(Parameter(adjusted_type,name=param_name))
                else:
                    adjusted_params.append(param)
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(),'val_type':param._type,'ret':fun_type.base_type,'attrs':None}
            decl.params=adjusted_params
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
            
            for param in decl.params:
                param_name = param.name.name
                adjusted_params = []

                if isinstance(param._type,Array):
                    adjusted_type = Pointer(param._type._type)
                    
                    adjusted_params.append(Parameter(adjusted_type,name=param_name))
                else:
                    adjusted_params.append(param)

                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(), 'val_type':param._type,'ret': decl.fun_type,'attrs':None,'Double':param._type}
            decl.params=adjusted_params
            stmts=[]
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                    print('\nType checking statement',stmt,decl.fun_type.base_type)  
                    typecheck_statement(stmt, symbols, decl.fun_type.base_type)
                    print('\nType checking statement end',stmt,decl.fun_type.base_type)  
                    # exit()
                  
                else:
                    print('Found return')
                    # exit()
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp_and_convert(stmt.exp, symbols, decl.fun_type.base_type)
                        cast=convert_to(typed_return, decl.fun_type)
                        stmts.append(cast)
                        
                        

def typecheck_exp(e: Exp, symbols: dict, func_type=Optional):
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
        global x
        if x==1:
            print('\nReturn Expression',e,func_type)
            # exit()
        # x+=1
        if e.exp is not None and not isinstance(e.exp, Null):
            if func_type is not None:
                e.exp=typecheck_exp_and_convert(e.exp, symbols, func_type)    
                e.exp=convert_by_assignment(e.exp, func_type)
                if x==1:            
                    print(e)
                    # exit()
                x+=1
                return e
        x+=1
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
        if isinstance(e.target_type,Array):
            raise ValueError('Cant type cast to arry')
        
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
        print('Type Left',type_left)
        print('Type Right',type_right)
        
        if  isinstance(type_left.get_type(),Pointer) and isinstance(type_right.get_type(),Pointer):
            if type(type_left.get_type().ref)!=type(type_right.get_type().ref):
                raise SyntaxError('Cannot assign one pointer type to another')
    
        converted_right = convert_by_assignment(type_right, left_type)
        e.left = type_left
        e.right = converted_right
        e.set_type(left_type)
        return e

    elif isinstance(e, Binary):
        
        if e.operator in (BinaryOperator.EQUAL,BinaryOperator.NOT_EQUAL):
            typed_e1 = typecheck_exp_and_convert(e.left, symbols)
            typed_e2 = typecheck_exp_and_convert(e.right, symbols)
            t1 = typed_e1.get_type()
            t2 = typed_e2.get_type()
            print('In Binary')
            print('Type of exp 1',t1)
            print('Type of exp 2',t2)
          
            if isinstance(t1,Pointer) or isinstance(t2,Pointer):
                common_type = get_common_pointer_type(typed_e1, typed_e2)
                print('Common type',common_type)
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
                                                                                       BinaryOperator.GREATER,
                                                                                       BinaryOperator.LESS_OR_EQUAL,
                                                                                       BinaryOperator.LESS):
                if isinstance(t1.ref,type(t2.ref)):
                    e.set_type(Int())
                    e.rel_flag(Int())
                    return e 
                else:
                    raise ValueError('Pointer of two different types cannot be used for relational op')
            
            
            if (isinstance(t1,Pointer) and not isinstance(t2,Pointer) and e.operator in (BinaryOperator.ADD,BinaryOperator.SUBTRACT)):
                converted_e2 = convert_to(typed_e2, Long())
                e=Binary(e.operator,typed_e1,converted_e2)
                e.set_type(t1)
                e.rel_flag(Long())
                return e
            elif (not isinstance(t1,Pointer) and  isinstance(t2,Pointer) and e.operator == BinaryOperator.ADD):
                converted_e1 = convert_to(typed_e1, Long())
                e=Binary(e.operator,converted_e1,typed_e2)
                e.rel_flag(Long())
                e.set_type(t2)
                return e
            elif (isinstance(t1,Pointer) and  isinstance(t2.ref,type(t2.ref)) and e.operator == BinaryOperator.SUBTRACT):
                e=Binary(operator=e.operator,left=typed_e1,right=typed_e2)
                e.set_type(Long())
                e.rel_flag(Long())
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
        # exit()
        if not isinstance(typed_inner.get_type(), Pointer):
            raise SyntaxError("Dereference operator applied to non-pointer type")
        e.exp=typed_inner
        # deref_exp = Dereference(typed_inner)
        e.set_type(typed_inner.get_type().ref)
        # print(deref_exp)
        
        # exit()
        return e
    
    elif isinstance(e, AddOf):
        
        if not isinstance(e.exp, Constant):
            typed_inner = typecheck_exp(e.exp, symbols)
            referenced_t = typed_inner.get_type()
            e.exp= typed_inner
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

    elif isinstance(e,Subscript):
        typed_e1 = typecheck_exp_and_convert(e.exp1, symbols)
        typed_e2 = typecheck_exp_and_convert(e.exp2, symbols)
        t1 = typed_e1.get_type()
        t2 = typed_e2.get_type()
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
                            # exit()
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
            
            

           
            typecheck_exp_and_convert(statement, symbols,fun_type)

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
        if isinstance(stmt, VarDecl):
          
            typecheck_file_scope_variable_declaration(stmt, symbols)
        elif isinstance(stmt, FunDecl):
            print('Fun decl')
            print(stmt)
            
            typecheck_function_declaration(stmt, symbols, False)
        else:
           
            typecheck_statement(stmt, symbols)
    return program, symbols
