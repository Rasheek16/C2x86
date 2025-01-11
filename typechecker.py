
    
from _ast5 import *
from typing import Optional, List
from type_classes import *



def typecheck_file_scope_variable_declaration(decl: VarDecl, symbols: dict):
    """
    Type checks a file-scope variable declaration and updates the symbol table accordingly.
    Ensures linkage consistency and proper initialization handling.
    """
    # Step 1: Derive the "new_init" based on the decl.init:
    if isinstance(decl.init, Constant) and isinstance(decl.init.value, int):
        # e.g. "static int foo = 4;" => real definition
        new_init = Initial(decl.init)
    elif isinstance(decl.init, Null):
        # e.g. "static int foo;" => tentative
        # e.g. "extern int foo;" => no initializer
        if isinstance(decl.storage_class, Extern):
            new_init = NoInitializer()
        else:
            new_init = Tentative()
    else:
        # Non-constant initializer is not allowed at file scope per your spec
        raise SyntaxError("Non-constant initializer!", decl.storage_class)

    # Step 2: Determine linkage based on storage class
    # static => internal linkage => global_scope=False
    # otherwise => external linkage => global_scope=True
    global_scope = not isinstance(decl.storage_class, Static)

    # Step 3: Check if the name already exists in the symbol table
    var_name = decl.name.name
    if var_name in symbols:
        # We already have a declaration for this name
        old_decl = symbols[var_name]

        # Must be the same type
        if not isinstance(old_decl['type'], Int):
            raise TypeError("Function redeclared as variable")

        # Merge linkage
        old_global_scope = old_decl['attrs'].global_scope
        if isinstance(decl.storage_class, Extern):
            # 'extern' after a static => keep the old linkage (internal if it was static)
            final_linkage = old_global_scope
        else:
            # If new is static but old was external (or vice versa), conflict
            if old_global_scope != global_scope:
                raise ValueError("Conflicting variable linkage")
            final_linkage = old_global_scope

        # Now do the initializer merge:
        old_init = old_decl['attrs'].init  # could be Initial(...), Tentative(), NoInitializer()
        new_init = new_init               # from above

        # Helper checks:
        def is_initial(i): return isinstance(i, Initial)
        def is_tentative(i): return isinstance(i, Tentative)
        def is_noinit(i): return isinstance(i, NoInitializer)

        if is_initial(old_init):
            # Old was already a real definition
            if is_initial(new_init):
                # Another real definition => conflict
                raise ValueError("Conflicting file-scope variable definitions")
            else:
                # Keep the old real definition
                final_init = old_init

        elif is_tentative(old_init):
            # Old was 'static int x;' with no init
            if is_initial(new_init):
                # Upgrading from tentative to real
                final_init = new_init
            else:
                # Another 'static int x;' or 'extern int x;' => keep the old tentative
                final_init = old_init

        elif is_noinit(old_init):
            # Old was 'extern int x;'
            if is_initial(new_init) or is_tentative(new_init):
                # Now we have a real or tentative => adopt new
                final_init = new_init
            else:
                # Another extern => no change
                final_init = old_init
        else:
            raise RuntimeError("Unknown initializer type in old declaration")

    else:
        # There's no old symbol => we take the new
        final_linkage = global_scope
        final_init = new_init

    # Step 4: Construct the new attributes
    attrs = StaticAttr(init=final_init, global_scope=final_linkage)

    # Step 5: Update the symbol table
    symbols[var_name] = {
        'type': Int(),
        'attrs': attrs
    }

        # print(symbols)
         
def typecheck_local_vairable_declaration(decl:VarDecl,symbols:dict):
    try:
        if isinstance(decl.storage_class,Extern):
            if not isinstance(decl.init ,Null):
                raise SyntaxError('Initializer on local extern variable declaration')
            
            if decl.name.name in symbols:
                old_decl =  symbols[decl.name.name]
                if not isinstance(old_decl['type'],Int):
                    raise SyntaxError('Function redeclared as variable')
            else:
                # print(initial_value)
                symbols[decl.name.name]={
                    'type':Int(),
                    'attrs':StaticAttr(init=NoInitializer(),global_scope=True)
                }
        elif isinstance(decl.storage_class,Static):
            if isinstance(decl.init,Constant):
                initial_value =Initial(decl.init)
                # print(initial_value)
            elif isinstance(decl.init,Null):
                initial_value = Initial(Constant(0))
                # initial_value = NoInitializer()
            else:
                raise SyntaxError('Non-constant Initializer on local static variable',decl.init)
            # print(initial_value)
           
            symbols[decl.name.name]={
                'type':Int(),
                'attrs':StaticAttr(init=initial_value,global_scope=False)
            }
        else:
            symbols[decl.name.name]={
                'type':Int(),
                'attrs':LocalAttr()
            }
            if not isinstance(decl.init,Null):
                typecheck_exp(decl.init,symbols)
    except Exception as e:
        raise e
        
def typecheck_function_declaration(decl: FunDecl, symbols: dict,is_block_scope):
    # print(decl)
    """
    Type checks a function declaration by adding it to the symbol table,
    ensuring no conflicting declarations, and type checking the function body.
    """
    fun_name = decl.name.name
    fun_type = FunType(param_count=len(decl.params))
    has_body = decl.body is not None and not isinstance(decl.body, Null)
    already_defined = False
    _global = decl.storage_class
    if not isinstance(_global,Static):
        _global=True 
    else:
        _global=False
  
    
    if fun_name in symbols:
        old_decl = symbols[fun_name]
        # return
        # print(f"Function '{fun_name}' already in symbol table: {old_decl}")

        # Ensure the existing declaration is a function
        if 'fun_type' not in old_decl:
            raise SyntaxError(f"Identifier '{fun_name}' previously declared as a variable.")
        already_defined = old_decl['attrs'].defined

        # Compare the number of parameters
        if old_decl['fun_type'].param_count != fun_type.param_count:
            raise SyntaxError(
                f"Incompatible function declarations for '{fun_name}'. "
                f"Expected {old_decl['fun_type'].param_count} parameters, "
                f"got {fun_type.param_count}."
            )
        if already_defined and has_body:
            raise SyntaxError("Function is defined more than once")
 
 
        if old_decl['attrs'].global_scope and isinstance(decl.storage_class,Static):
            raise SyntaxError('Static funtion declarartion follow a non static ')
        
        if is_block_scope:
            if _global and isinstance(decl.storage_class,Static):
                raise SyntaxError('a block-scope function may only have extern storage class')
            
        _global = old_decl['attrs'].global_scope
        print(_global)
        attrs = FunAttr(defined=(already_defined or has_body), global_scope=_global)
        print(attrs)
        symbols[fun_name]={
            'fun_type':FunType(param_count=len(decl.params)),
            'attrs':attrs
        }
        
    
        if has_body:
            # symbols[fun_name]['defined'] = True
            #print(f"Defining function '{fun_name}'.")

            # Add each parameter to the symbol table with type Int
            for param in decl.params:
                param_name = param.name.name
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(),'attrs':None}
                #print(f"Declared parameter '{param_name}' with type Int.")
                
       
        
        # print(decl.body)
        typecheck_statement(decl.body, symbols)
            # Type check the function body
    else:
        print(is_block_scope)
        if is_block_scope:
            if not _global and isinstance(decl.storage_class,Static):
               
                raise SyntaxError('a block-scope function may only have extern storage class')
        
        # Add a new function declaration or definition
        symbols[fun_name] = {'fun_type': FunType(param_count=len(decl.params)),'attrs':FunAttr(defined=has_body,global_scope=_global)}
        #print(f"Declared function '{fun_name}' with type FunType(param_count={fun_type.param_count}).")

        if has_body:
            #print(f"Defining function '{fun_name}'.")

            # Add each parameter to the symbol table with type Int
            for param in decl.params:
                param_name = param.name.name
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(),'attrs':None}
                #print(f"Declared parameter '{param_name}' with type Int.")
            # Type check the function body
            typecheck_statement(decl.body, symbols)

    #print(f"Symbol table after processing function '{fun_name}': {symbols}")

def typecheck_exp(e: Expression, symbols: dict):
    """
    Type checks an expression by ensuring correct usage of variables and functions.
    """
    
    if isinstance(e, FunctionCall):
        fun_name = e.identifier.name
        
        if fun_name not in symbols:
            raise NameError(f"Function '{fun_name}' is not defined.")
        
        fun_entry = symbols[fun_name]
   
        
        # Ensure that the identifier is a function
        if  not isinstance(fun_entry['fun_type'],FunType):
            raise SyntaxError(f"Variable '{fun_name}' used as a function.")
        
        f_type = fun_entry['fun_type']
        
        # Check if the number of arguments matches the function's parameter count
        if f_type.param_count != len(e.args):
            raise SyntaxError(f"Function '{fun_name}' called with wrong number of arguments. Expected {f_type.param_count}, got {len(e.args)}.")
        
        #print(f"Calling function '{fun_name}' with {len(e.args)} arguments.")
        
        # Recursively type check each argument
        for arg in e.args:
            typecheck_exp(arg, symbols)
    
    elif isinstance(e, Var):
        var_name = e.identifier.name
     
        if var_name not in symbols:
            raise NameError(f"Variable '{var_name}' is not defined.")
        
        var_entry = symbols[var_name]
        
        # Ensure that the identifier is a variable, not a function
        if 'type' not in var_entry:
            raise SyntaxError(f"Function '{var_name}' used as a variable.")
        var_type = var_entry['type']
        if not isinstance(var_type, Int):
            raise SyntaxError(f"Identifier '{var_name}' does not have type Int.")
        
        #print(f"Using variable '{var_name}' of type Int.")
    
    elif isinstance(e, Return):
        # Type check the return expression if present
        if e.exp is not None and not isinstance(e.exp, Null):
            typecheck_exp(e.exp, symbols)
    
    elif isinstance(e, Constant):
        pass
        # Assuming all constants are of type Int for simplicity
        #print(f"Constant value '{e.value}' is of type Int.")
    
    elif isinstance(e, (Assignment, Binary, Unary)):
        # Type check sub-expressions
        if isinstance(e, Assignment):
            typecheck_exp(e.left, symbols)
            typecheck_exp(e.right, symbols)
            #print(f"Assignment operation between '{e.left}' and '{e.right}'.")
        elif isinstance(e, Binary):
            typecheck_exp(e.left, symbols)
            typecheck_exp(e.right, symbols)
            #print(f"Binary operation between '{e.left}' and '{e.right}'.")
        elif isinstance(e, Unary):
            typecheck_exp(e.expr, symbols)
            #print(f"Unary operation on '{e.expr}'.")
    elif isinstance(e,Null):
        
        pass
    elif isinstance(e,Conditional):
        typecheck_statement(e,symbols)
    else:
        raise TypeError(f"Unsupported expression type for type checking: {type(e)}")

def typecheck_statement(statement: Statement, symbols: dict):
    """
    Recursively traverses the AST and performs type checking for variable and function declarations.
    For other statements, it traverses their child statements or expressions.
    """
    #print(statement)
    if isinstance(statement, list):
        for stmt in statement:
            typecheck_statement(stmt, symbols)
        return statement

    if isinstance(statement, VarDecl):
        # print(symbols)
        typecheck_local_vairable_declaration(statement, symbols)
    
    elif isinstance(statement,InitDecl):
        typecheck_statement(statement.declaration.declaration,symbols)
    
    elif isinstance(statement,InitExp):
        typecheck_statement(statement.exp,symbols)
    elif isinstance(statement, FunDecl):
        typecheck_function_declaration(statement, symbols,is_block_scope=True)
    
    elif isinstance(statement, (Break, Continue)):
        # Assuming labeling is handled elsewhere; no type checking needed
        pass
    
    elif isinstance(statement,Expression):
        typecheck_statement(statement.exp,symbols)
    
    elif isinstance(statement, (While, For, DoWhile)):
        # Type check the loop condition and traverse the loop body
        if isinstance(statement, While):
            typecheck_exp(statement._condition, symbols)
            typecheck_statement(statement.body, symbols)
            #print("Type checked a 'while' loop.")
        
        elif isinstance(statement, For):
            if isinstance(statement.init,InitDecl):
                if statement.init and not isinstance(statement.init,Null):
                    if isinstance(statement.init.declaration.declaration,VarDecl):
                        if isinstance(statement.init.declaration.declaration.storage_class,(Extern,Static)):
                            print('here')
                            raise SyntaxError('Loop initializer cannot have storage class')
                        else: 
                            typecheck_statement(statement.init, symbols)
                        
            else:
                typecheck_statement(statement.init, symbols)
            if statement.condition:
                typecheck_exp(statement.condition, symbols)
            if statement.post:
                typecheck_exp(statement.post, symbols)
            #print(type(statement.body))
            typecheck_statement(statement.body, symbols)
            #print("Type checked a 'for' loop.")
        
        elif isinstance(statement, DoWhile):
            typecheck_statement(statement.body, symbols)
            typecheck_exp(statement._condition, symbols)
            #print("Type checked a 'do-while' loop.")
    
    elif isinstance(statement, Compound):
        # Traverse each statement in the compound block
        for stmt in statement.block:
            #print("Type checked a compound statement.")
            typecheck_statement(stmt, symbols)

    elif isinstance(statement, S):
        # Assuming S wraps another statement
        typecheck_statement(statement.statement, symbols)
    
    elif isinstance(statement, D):
        # Handle different types of declarations within D
        if isinstance(statement.declaration, FunDecl):
            print(statement.declaration)
            typecheck_function_declaration(statement.declaration, symbols,is_block_scope=True)
        elif isinstance(statement.declaration, VarDecl):
            typecheck_local_vairable_declaration(statement.declaration, symbols)
        else:
            raise TypeError(f"Unsupported declaration type in D: {type(statement.declaration)}")
    
    elif isinstance(statement, Conditional):
        # Type check expressions and traverse corresponding statements
        if statement.condition:
            typecheck_statement(statement.condition, symbols)
        if statement.exp2:
            typecheck_statement(statement.exp2, symbols)
        if statement.exp3:
            typecheck_statement(statement.exp3, symbols)
        #print("Type checked a conditional statement.")
    
    elif isinstance(statement, If):
        # Type check the condition and traverse 'then' and 'else' branches
        typecheck_exp(statement.exp, symbols)
        typecheck_statement(statement.then, symbols)
        if statement._else:
            typecheck_statement(statement._else, symbols)
        #print("Type checked an 'if' statement.")
    
    elif isinstance(statement, FunctionCall):
        # Function calls as standalone statements
        typecheck_exp(statement, symbols)
    
    elif isinstance(statement, Return):
        # Type check return expressions
        if isinstance(statement,Statement):
            typecheck_statement(statement.exp,symbols)
        else:
            typecheck_exp(statement, symbols)
    
    elif isinstance(statement, (Expression, Assignment, Binary, Unary)):
        if isinstance(statement,Assignment):
            typecheck_statement(statement.left,symbols)
            typecheck_statement(statement.right,symbols)
        else:
            # Type check expressions
            typecheck_exp(statement, symbols)
    
    elif isinstance(statement, Var):
        # Type check variable usage
        typecheck_exp(statement, symbols)
    
    elif isinstance(statement, Constant):
        # Type check constant usage
        typecheck_exp(statement, symbols)
    
    elif isinstance(statement, Null):
        # No action needed for Null statements
        pass
    
    else:
        raise TypeError(f"Unsupported statement type for type checking: {type(statement)}")

def typecheck_program(program:Program):
    """
    Initiates the type checking process for the entire program.
    """
      # Single symbol table dictionary
    symbols = {}
    #print("Starting type checking of the program.")
    for stmt in program.function_definition:
        if isinstance(stmt,VarDecl):
            
            typecheck_file_scope_variable_declaration(stmt,symbols)
        elif isinstance(stmt,FunDecl):
        
            typecheck_function_declaration(stmt, symbols,False)
        else:
            typecheck_statement(stmt,symbols)
    #print("Type checking completed successfully.")
    return program,symbols