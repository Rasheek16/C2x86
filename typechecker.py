from _ast5 import *
from typing import Optional, List
from type_classes import *
import sys


def size(_type):
    if type(_type)==Int():
        return 4
    elif type(_type)==Long():
        return 8
    elif type(_type)==UInt():
        return 4
    elif type(_type)==ULong():
        return 8

def isSigned(_type):
    if type(_type)==Int() or type(_type)==Long():
        return True
    return False
    


def get_common_type(type1, type2):
    if type(type1) == type(type2):
        return type1
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

def typecheck_file_scope_variable_declaration(decl: VarDecl, symbols: dict):
    print(decl)
    if not isinstance(decl.init, Null):
        print('here')
        typecheck_exp(decl.init, symbols)

    if isinstance(decl.init, Constant) and isinstance(decl.init.value, (ConstInt, ConstLong)):
        if isinstance(decl.init.get_type(), Long):
            new_init = Initial(Constant(StaticInit.LongInit(decl.init.value)))
        else:
            new_init = Initial(Constant(StaticInit.IntInit(decl.init.value)))
    elif isinstance(decl.init, Constant) and isinstance(decl.init.value, (ConstUInt, ConstULong)):
        if isinstance(decl.init.get_type(), ULong):
            new_init = Initial(Constant(StaticInit.ULongInit(decl.init.value)))
        else:
            new_init = Initial(Constant(StaticInit.UIntInit(decl.init.value)))
    elif isinstance(decl.init, Null):
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
        'ret':decl.var_type
    }

def typecheck_local_vairable_declaration(decl: VarDecl, symbols: dict):
    try:
        # if isinstance(decl.init,FunctionCall):
            # print(decl)
            # exit()
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
                }
            return decl
        elif isinstance(decl.storage_class, Static):
            if isinstance(decl.init, Constant):
                # #decl.init)
                initial_value = Initial(IntInit(decl.init))
                
                
            elif isinstance(decl.init, Null):
                initial_value = Initial(IntInit(Constant(ConstInt(0))))
            else:
                raise SyntaxError('Non-constant Initializer on local static variable', decl.init)

            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': StaticAttr(init=initial_value, global_scope=False),
                'ret': decl.var_type,
                
            }
            return decl
        else:
            # exit()
            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': LocalAttr(),
                'ret': decl.var_type,
                
            }
            # print('vardeclaration',decl)
            # exit()
            if not isinstance(decl.init, Null):
                x = typecheck_exp(decl.init, symbols)
                decl.init=x
                # if isinstance(decl.init,FunctionCall):
                    # print('decl',decl)
                # print(decl)
                # common_type=get_common_type(decl.var_type,decl.init.get_type())
                # print('common_type',common_type)
                decl.init=convert_to(decl.init,decl.var_type)
                    # print('decl',decl)
                    # exit()
            return decl
                
    except Exception as e:
        raise e

def typecheck_function_declaration(decl: FunDecl, symbols: dict, is_block_scope):
    fun_name = decl.name.name
    fun_type = FunType(param_count=len(decl.params), params=decl.params, ret=decl.fun_type)
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
        if type(old_decl['fun_type'].ret) != type(fun_type.ret):
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
            'fun_type': FunType(param_count=len(decl.params), params=decl.params, ret=decl.fun_type),
            'attrs': attrs
        }

        if has_body:
            for param in decl.params:
                param_name = param.name.name
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(),'val_type':param._type,'ret':decl.fun_type,'attrs':None}
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                    typecheck_statement(decl.body, symbols, fun_type)
                else:
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp(stmt.exp, symbols, fun_type)
                        convert_to(typed_return, decl.fun_type)
    else:
        if is_block_scope:
            if not _global and isinstance(decl.storage_class, Static):
                raise SyntaxError('a block-scope function may only have extern storage class')

        symbols[fun_name] = {
            'fun_type': FunType(param_count=len(decl.params), params=decl.params, ret=decl.fun_type),
            'attrs': FunAttr(defined=has_body, global_scope=_global)
        }

        if has_body:
            for param in decl.params:
                param_name = param.name.name
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(), 'val_type':param._type,'ret': decl.fun_type,'attrs':None}
            stmts=[]
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                    # #decl.fun_type)
                    stmt=typecheck_statement(decl.body, symbols, decl.fun_type)
                    stmts.extend(stmt)
                    # if decl.name.name=='truncate_on_assignment':
                            # print('here')
                            # print(stmts)
                        # print(e)
                            # exit()
            
                    # #stmt)
                    # convert_to(stmt, decl.fun_type)
                    
                    # #'here')
                    # exit()
                else:
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp(stmt.exp, symbols, fun_type)
                        # #typed_return)
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
        # print(e)
        # if e.identifier.name=='truncate_on_assignment':
            # print('here')
            # print(e)
            # exit()
            
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
            typed_arg = typecheck_exp(arg, symbols)  # paramType known
            converted_args.append(convert_to(typed_arg, paramType))

        e.args = converted_args
        e.set_type(f_type.ret)
        # if e.identifier.name=='truncate_on_assignment':
            # print('here')
            # print(e)
            # exit()
            
        # print(e)
        # exit()
        
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
        #'type set of variable')
        # #e)
        # exit()
        return e

    elif isinstance(e, Return):
        # #func_type)
        # #symbols)
        if e.exp is not None and not isinstance(e.exp, Null):
            if func_type is not None:
                e.exp=typecheck_exp(e.exp, symbols, func_type)    
                # #func_type)
                #'e',e)
                #func_type)
                e.exp=convert_to(e.exp, func_type)
                #'expr',e)
                # exit()
                # exit()
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
            # e.set_type(Long())
            e.set_type(UInt())
            return e
        else:
            raise SyntaxError('Invalid value const')

    elif isinstance(e, Cast):
        # #'inside cast')
        typed_inner = typecheck_exp(e.exp, symbols)
        e.exp = typed_inner
        e.set_type(e.target_type)
        #'set cast type')
        #e)
        # e.exp.set_type(e.target_type)
        return e

    elif isinstance(e, Assignment):
        type_left = typecheck_exp(e.left, symbols)
        type_right = typecheck_exp(e.right, symbols)
        #type_left)
        left_type = type_left.get_type()
        # print(e)
        # if isinstance(e.right,FunctionCall):
                    # print(decl)
                    # print(symbols)
                    # exit()
        converted_right = convert_to(type_right, left_type)
        e.left = type_left
        e.right = converted_right
        e.set_type(left_type)
        #'evkjghl',e)
        # if e.right.identifier == 'return_truncated_long':
        #     exit()
        # exit()
        return e

    elif isinstance(e, Binary):
        typed_e1 = typecheck_exp(e.left, symbols)
        typed_e2 = typecheck_exp(e.right, symbols)

        if e.operator in (BinaryOperator.AND, BinaryOperator.OR):
            e.left = typed_e1
            e.right = typed_e2
            e.set_type(Int())
            return e
        #typed_e1)
        # exit()
        t1 = typed_e1.get_type()
        t2 = typed_e2.get_type()
        # #type(typed_e1))
        #t1)
        common_type = get_common_type(t1, t2)

        converted_e1 = convert_to(typed_e1, common_type)
        converted_e2 = convert_to(typed_e2, common_type)
        e.left = converted_e1
        e.right = converted_e2

        if e.operator in (BinaryOperator.ADD, BinaryOperator.DIVIDE,
                          BinaryOperator.MULTIPLY, BinaryOperator.SUBTRACT,
                          BinaryOperator.REMAINDER):
            #'commone_type',common_type)
            e.set_type(common_type)
            #e)
            # exit()
            return e 
        else:
            e.set_type(Int())
            return e
      

    elif isinstance(e, Unary):
        inner = typecheck_exp(e.expr, symbols)
        e.expr = inner
        if e.operator == UnaryOperator.NOT:
            e.set_type(Int())
        else:
            e.set_type(inner.get_type())
            # #e.expr.get_type())
            # exit()
        return e

    elif isinstance(e, Conditional):
        typed_condition = typecheck_exp(e.condition, symbols) if e.condition else None
        typed_exp2 = typecheck_exp(e.exp2, symbols) if e.exp2 else None
        typed_exp3 = typecheck_exp(e.exp3, symbols) if e.exp3 else None

        if typed_exp2 is None or typed_exp3 is None:
            raise SyntaxError("Malformed Conditional expression")

        t2 = typed_exp2.get_type()
        t3 = typed_exp3.get_type()
        common_type = get_common_type(t2, t3)
        converted_e2 = convert_to(typed_exp2, common_type)
        converted_e3 = convert_to(typed_exp3, common_type)

        e.condition = typed_condition
        e.exp2 = converted_e2
        e.exp3 = converted_e3
        e.set_type(common_type)
        return e

    elif isinstance(e, Null):
        return e

    else:
        raise TypeError(f"Unsupported expression type for type checking: {type(e)}")

def typecheck_statement(statement: Statement, symbols: dict, fun_type=Optional[str]):
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
        typecheck_exp(statement.exp, symbols, fun_type)

    elif isinstance(statement, (While, For, DoWhile)):
        if isinstance(statement, While):
            typecheck_exp(statement._condition, symbols, fun_type)
            typecheck_statement(statement.body, symbols, fun_type)
        elif isinstance(statement, For):
            if isinstance(statement.init, InitDecl):
                if statement.init and not isinstance(statement.init, Null):
                    if isinstance(statement.init.declaration.declaration, VarDecl):
                        if isinstance(statement.init.declaration.declaration.storage_class, (Extern, Static)):
                            raise SyntaxError('Loop initializer cannot have storage class')
                        else:
                            typecheck_statement(statement.init, symbols, fun_type)
            else:
                typecheck_statement(statement.init, symbols, fun_type)

            if statement.condition:
                typecheck_exp(statement.condition, symbols, fun_type)
            if statement.post:
                typecheck_exp(statement.post, symbols, fun_type)
            typecheck_statement(statement.body, symbols, fun_type)

        elif isinstance(statement, DoWhile):
            typecheck_statement(statement.body, symbols, fun_type)
            typecheck_exp(statement._condition, symbols, fun_type)

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
        typecheck_exp(statement, symbols, fun_type)

    elif isinstance(statement, If):
        typecheck_exp(statement.exp, symbols, fun_type)
        typecheck_statement(statement.then, symbols, fun_type)
        if statement._else:
            typecheck_statement(statement._else, symbols, fun_type)

    elif isinstance(statement, FunctionCall):
        typecheck_exp(statement, symbols, fun_type)

    elif isinstance(statement, Return):
        
        # if isinstance(statement, Statement):
        #     if fun_type is not None:
        #         typecheck_statement(statement.exp, symbols, fun_type)
        #     else:
        #         typecheck_statement(statement.exp, symbols)
        # else:
            if fun_type is not None:
                #fun_type)
                typecheck_exp(statement, symbols, fun_type)
            else:
                typecheck_exp(statement.exp, symbols,fun_type)

    elif isinstance(statement, (Expression, Assignment, Binary, Unary)):
        typecheck_exp(statement, symbols, fun_type)

    elif isinstance(statement, Cast):
        typecheck_exp(statement, symbols, fun_type)

    elif isinstance(statement, Var):
        typecheck_exp(statement, symbols, fun_type)

    elif isinstance(statement, Constant):
        typecheck_exp(statement, symbols, fun_type)

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
            print(stmt)
            # exit()
            typecheck_file_scope_variable_declaration(stmt, symbols)
        elif isinstance(stmt, FunDecl):
            typecheck_function_declaration(stmt, symbols, False)
        else:
            typecheck_statement(stmt, symbols)
    return program, symbols
