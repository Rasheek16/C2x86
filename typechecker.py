# from _ast5 import *

# def typecheck_variable_declaration(decl,symbols:dict):
#     if isinstance(decl,VarDecl):
#         symbols[decl.name]['type']==Int()
#         if not isinstance(decl.init,Null):
#             typecheck_exp(decl.inti,symbols)
            
    


# def typecheck_funciton_declaration(decl,symbols):
#     if isinstance(decl,FunDecl):
#         fun_name = decl.name
#         fun_type = FunType(param_count=len(decl.params))
#         if isinstance(decl.body,Null):
#             raise ValueError('Body is Null')
#         has_body =True
#         already_defined = False
        
#         if fun_name in symbols:
#             old_decl = symbols[fun_name]
#             if old_decl != fun_type:
#                 raise SyntaxError('Incompatiple Function declaration')
#             already_defined = old_decl['defined']
            
#             if old_decl and has_body:
#                 raise SyntaxError('Funtion defined more than once')
            
#         symbols[fun_name]={
#             'fun_type':fun_type,
#             'defined':already_defined or has_body
#         }
        
#         if has_body:
#             for param in decl.params:
#                 symbols[param]=Int()
            
#             typecheck_block(decl.body)
            
        
    
# def typecheck_exp(e,symbols):
#     if isinstance(e,FunctionCall):
#         f_type = symbols[e.identifier]['fun_type']
#         if f_type == Int():
#             raise SyntaxError('VARIABLE USED AS FUNCTION')
#         if isinstance(f_type,FunType):
#             if f_type.param_count != len(e.args):
#                 raise SyntaxError('Wrong no of parameters')
        
#         for arg  in e.args:
#             typecheck_exp(arg,symbols)
            
#     elif isinstance(e,Var):
#         _type=symbols[e.identifier]['type']
#         if not isinstance(_type,Int):
#             raise SyntaxError('Function name being used as a variable')
    
    
from _ast5 import *
from typing import Optional, List

# Assuming Int and FunType are classes defined in _ast5
# and that Null represents the absence of a value.

def typecheck_variable_declaration(decl: VarDecl, symbols: dict):
    """
    Type checks a variable declaration by adding it to the symbol table
    and type checking its initializer if present.
    """
    if decl.name.name in symbols:
        raise SyntaxError(f"Variable '{decl.name.name}' is already declared.")
    
    # Assign the type Int to the variable in the symbol table
    symbols[decl.name.name] = {'type': Int()}
    #print(f"Declared variable '{decl.name.name}' with type Int.")
    
    # Type check the initializer if it exists
    if decl.init is not None and not isinstance(decl.init, Null):
        if isinstance(decl.init,Exp):
            typecheck_exp(decl.init,symbols)
        else:
            typecheck_statement(decl.init, symbols)


    
def typecheck_function_declaration(decl: FunDecl, symbols: dict):
    """
    Type checks a function declaration by adding it to the symbol table,
    ensuring no conflicting declarations, and type checking the function body.
    """
    fun_name = decl.name.name
    fun_type = FunType(param_count=len(decl.params))
    has_body = decl.body is not None and not isinstance(decl.body, Null)
    #print(f"\nProcessing function '{fun_name}'. Has body: {has_body}")

    if fun_name in symbols:
        old_decl = symbols[fun_name]
        #print(f"Function '{fun_name}' already in symbol table: {old_decl}")

        # Ensure the existing declaration is a function
        if 'fun_type' not in old_decl:
            raise SyntaxError(f"Identifier '{fun_name}' previously declared as a variable.")

        # Compare the number of parameters
        if old_decl['fun_type'].param_count != fun_type.param_count:
            raise SyntaxError(
                f"Incompatible function declarations for '{fun_name}'. "
                f"Expected {old_decl['fun_type'].param_count} parameters, "
                f"got {fun_type.param_count}."
            )

        already_defined = old_decl.get('defined', False)
        #print(f"Function '{fun_name}' already defined: {already_defined}")

        # Check if the function is being defined more than once
        if already_defined and has_body:
            raise SyntaxError(f"Function '{fun_name}' is defined more than once.")

        # If current declaration has a body, mark as defined
        if has_body:
            symbols[fun_name]['defined'] = True
            #print(f"Defining function '{fun_name}'.")

            # Add each parameter to the symbol table with type Int
            for param in decl.params:
                param_name = param.name.name
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int()}
                #print(f"Declared parameter '{param_name}' with type Int.")

            # Type check the function body
            typecheck_statement(decl.body, symbols)
    else:
        # Add a new function declaration or definition
        symbols[fun_name] = {'fun_type': fun_type, 'defined': has_body}
        #print(f"Declared function '{fun_name}' with type FunType(param_count={fun_type.param_count}).")

        if has_body:
            #print(f"Defining function '{fun_name}'.")

            # Add each parameter to the symbol table with type Int
            for param in decl.params:
                param_name = param.name.name
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int()}
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
        if 'fun_type' not in fun_entry:
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
        typecheck_variable_declaration(statement, symbols)
    
    elif isinstance(statement,InitDecl):
        typecheck_statement(statement.declaration.declaration,symbols)
    
    elif isinstance(statement,InitExp):
        typecheck_statement(statement.exp,symbols)
    elif isinstance(statement, FunDecl):
        typecheck_function_declaration(statement, symbols)
    
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
            if statement.init:
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
            typecheck_function_declaration(statement.declaration, symbols)
        elif isinstance(statement.declaration, VarDecl):
            typecheck_variable_declaration(statement.declaration, symbols)
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
    symbols = {}  # Single symbol table dictionary
    #print("Starting type checking of the program.")
    for stmt in program.function_definition:
        #print(stmt)
        typecheck_statement(stmt, symbols)
    
    #print("Type checking completed successfully.")
    return program