from _ast5 import *
# from tacky_emiter import , convert_binop, convert_unop
from typing import List, Dict, Any, Optional
import copy
from typechecker import typecheck_program
from tacky_emiter import temp_counter,make_temporary_var

# -------------------------------------------------------------------------
# 1) Global Labeling Variables
# -------------------------------------------------------------------------
temp_loop_label = 0




def get_label():
    """
    Increments and returns a global loop label 
    to annotate loops for break/continue statements.
    """
    global temp_loop_label
    temp_loop_label += 1
    return f'loop.{temp_loop_label}'


# -------------------------------------------------------------------------
# 2) Resolve Declarations (VarDecl / FunDecl)
# -------------------------------------------------------------------------

def resole_file_scope_var(decl:VarDecl,identifier_map) -> VarDecl:
    identifier_map[decl.name.name]={'unique_name':decl.name.name,'from_current_scope':True,'has_linkage':True}
    return decl
    

def resolve_declaration(declaration, identifier_map: dict,is_file_scope=False)-> VarDecl:
    # print(declaration,is_file_scope)
    """
    Resolves a single declaration (either VarDecl or FunDecl).
    - VarDecl => create a unique name for local variables.
    - FunDecl => preserve the original name (has_linkage=True).
    """
    if isinstance(declaration, VarDecl):
        # print(is_file_scope)
        if is_file_scope:
            return resole_file_scope_var(declaration,identifier_map)
        # Ensure we have an Identifier for the name 
        else:
            # print(is_file_scope)
            if not isinstance(declaration.name, Identifier):
                raise TypeError(f"Declaration name must be an Identifier, got {type(declaration.name)}")

            original_name = declaration.name.name
            print(original_name)
            # exit()
            # print()
            # Check for duplicates in the current scope
            if original_name in identifier_map and identifier_map[original_name]['from_current_scope']==True:
                # print(original_name)
                # print(identifier_map[original_name])
                # print(declaration.storage_class)
                # print(isinstance(declaration.storage_class,Extern))
                if not (identifier_map[original_name]['has_linkage'] and  isinstance(declaration.storage_class,Extern)):
                    raise ValueError(f"Duplicate variable declaration: '{original_name}' / Conflicting local declarations.")

            if isinstance(declaration.storage_class,Extern):
                identifier_map[original_name] = {
                'unique_name': original_name,
                'from_current_scope': True,
                'has_linkage': True
            }
                return declaration
            
            else:
                # Generate a unique name for the variable
                unique_name = make_temporary_var()
                identifier_map[original_name] = {
                    'unique_name': unique_name,
                    'from_current_scope': True,
                    'has_linkage': False
                }

                # Resolve the initialization if present
                init = None
                if declaration.init is not None:
                    init = resolve_exp(declaration.init, identifier_map)

                # Return a VarDecl with the new unique name
                return VarDecl(name=Identifier(unique_name),var_type=declaration.var_type, init=init,storage_class=declaration.storage_class)

    elif isinstance(declaration, FunDecl):
        # If there's no body, raise an error or handle differently as needed
        if isinstance(declaration.body, Null) and not declaration.storage_class=='static':
            return resolve_function_declaration(declaration, identifier_map)
        else:
            raise SyntaxError("Nested Functions are not supported")
        # Otherwise, handle a function declaration

    else:
        raise SyntaxError(f"Unknown declaration type: {type(declaration)}")


# -------------------------------------------------------------------------
# 3) Resolve Expressions
# -------------------------------------------------------------------------
def resolve_exp(expression, identifier_map: dict):
    print(expression)
    """
    Resolves an expression by mapping variable/function identifiers
    to their unique names. Preserves names for items with has_linkage=True.
    """
    if isinstance(expression, Assignment):
        if not isinstance(expression.left,(Var,Dereference,Subscript)):
            raise ValueError(f"Invalid lvalue in assignment: {expression.left}")
        if isinstance(expression.left,Unary):
            resolved_left = resolve_exp(expression.left.expr,identifier_map)
        else:
            resolved_left = resolve_exp(expression.left, identifier_map)
        resolved_right = resolve_exp(expression.right, identifier_map)
        return Assignment(left=resolved_left, right=resolved_right)
    elif isinstance(expression,Cast):
        resolved_exp=resolve_exp(expression.exp,identifier_map)
        return Cast(target_type=expression.target_type,exp = resolved_exp)      
    elif isinstance(expression, Conditional):
        # Resolve condition and both branches
        resolved_condition = resolve_exp(expression.condition, identifier_map)
        resolved_exp2 = resolve_exp(expression.exp2, identifier_map)
        resolved_exp3 = resolve_exp(expression.exp3, identifier_map)
        return Conditional(condition=resolved_condition, exp2=resolved_exp2, exp3=resolved_exp3)
    elif isinstance(expression, Var):
        # A variable usage => check the identifier_map
        # print(expression)
        
        if not isinstance(expression.identifier, Identifier):
            raise TypeError(f"Expected Identifier, got {type(expression.identifier)}")
        original_identifier = expression.identifier.name

        if original_identifier in identifier_map:
            unique_name = identifier_map[original_identifier]['unique_name']
            return Var(identifier=Identifier(unique_name))
        else:
            raise ValueError(f"Undeclared variable usage: '{original_identifier}'")
    elif isinstance(expression, Unary):
        if expression.operator == UnaryOperator.DEREFERENCE and isinstance(expression.expr,Constant):
            raise SyntaxError("Invalid dereference of a constant")
            
            
        resolved_expr = resolve_exp(expression.expr, identifier_map)
        return Unary(operator=expression.operator, expr=resolved_expr)

    elif isinstance(expression, Binary):
        # if expression.operator in (BinaryOperator.MULTIPLY,BinaryOperator.DIVIDE):
            
            # TODO: Check for pointer arithmetic again
            # if isinstance(expression.left,Dereference) and isinstance(expression.right,Dereference):
                # raise SyntaxError("Invalid binary operation on pointers")
        
        # if expression.operator in (BinaryOperator.EQUAL,BinaryOperator.GREATER_OR_EQUAL,
        #                            BinaryOperator.GREATER_THAN,
        #                            BinaryOperator.LESS_OR_EQUAL,
        #                            BinaryOperator.LESS_THAN,BinaryOperator.NOT_EQUAL):
        #     # print(expression)
            # exit()
            # if (isinstance(expression.left,AddOf) and not isinstance(expression.right,AddOf)) or (
            #     not isinstance(expression.left,AddOf) and isinstance(expression.right,AddOf)):
            #     raise SyntaxError("Invalid binary operation on pointers")
            
            
        print('Binary')
        resolved_left = resolve_exp(expression.left, identifier_map)
        resolved_right = resolve_exp(expression.right, identifier_map)
        return Binary(operator=expression.operator, left=resolved_left, right=resolved_right)

    elif isinstance(expression, FunctionCall):
        # Resolve function name
        # print(expression.identifier.name)
        # print(identifier_map)
        # exit()
        func_name = expression.identifier.name
        if func_name in identifier_map:
            new_func_name = identifier_map[func_name]['unique_name']
            # Resolve arguments
            new_args = [resolve_exp(arg, identifier_map) for arg in expression.args]
            # arg_type = [arg for arg in expression.args]
            return FunctionCall(Identifier(new_func_name), new_args)
        else:
            raise SyntaxError(f"Function '{func_name}' is not declared")

    elif isinstance(expression, (Constant, Null)):
        return expression
    # elif isinstance(expression,Identifier):
    #     # print('Here')
    #     resolved_expr = resolve_exp(expression.name,identifier_map)
    #     return Identifier(resolved_expr)
    elif isinstance(expression, AddOf):
        resolved_expr = resolve_exp(expression.exp, identifier_map)
        return AddOf(resolved_expr)
    elif isinstance(expression, Dereference):
        resolved_expr = resolve_exp(expression.exp, identifier_map)
        return Dereference(resolved_expr)
    elif isinstance(expression,CompoundInit):
        i=0
        l=[]
        while (i<len(expression.initializer)):
            resolved_exp = resolve_exp(expression.initializer[i],identifier_map)
            l.append(resolved_exp)
            i+=1
        return CompoundInit(l)
    elif isinstance(expression,SingleInit):
        resolved_exp=resolve_exp(expression.exp,identifier_map)
        return SingleInit(resolved_exp)
            
        
    elif isinstance(expression,Subscript):
        print('Subscript')
        resolved_exp1 = resolve_exp(expression.exp1,identifier_map)
        resolved_exp2 = resolve_exp(expression.exp2,identifier_map)
        return Subscript(exp1=resolved_exp1,exp2=resolved_exp2)
   
    else:
        raise SyntaxError(f"Unknown expression type: {type(expression)}")


# -------------------------------------------------------------------------
# 4) Resolve Block Items
# -------------------------------------------------------------------------
def resolve_block_items(block_items: List[BlockItem], identifier_map: dict) -> List[BlockItem]:
    """
    Resolves a list of block items (D, S, Compound) in a given scope.
    """
    resolved_body = []
    for block_item in block_items:
        if isinstance(block_item, D):
            # print('here')
            # Declaration node: could be VarDecl or FunDecl
            resolved_decl = resolve_declaration(block_item.declaration, identifier_map)
            resolved_body.append(D(declaration=resolved_decl))

        elif isinstance(block_item, S):
            # Statement node
            resolved_stmt = resolve_statement(block_item.statement, identifier_map)
            resolved_body.append(S(statement=resolved_stmt))

        elif isinstance(block_item, Compound):
            # Nested block => create a new scope
            new_map = copy_identifier_map(identifier_map)
            resolved_compound = Compound(
                block=resolve_block_items(block_item.block, new_map)
            )
            resolved_body.append(resolved_compound)

        else:
            raise SyntaxError(f"Unknown block item type: {type(block_item)}")

    return resolved_body


# -------------------------------------------------------------------------
# 5) Copy Identifier Map (New Scope)
# -------------------------------------------------------------------------
def copy_identifier_map(identifier_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Creates a copy of the identifier map, setting 'from_current_scope' to False 
    so that new declarations won't conflict with older ones in outer scopes.
    """
    new_map = copy.deepcopy(identifier_map)
    for var_info in new_map.values():
        var_info['from_current_scope'] = False
    return new_map


# -------------------------------------------------------------------------
# 6) Resolve Statements
# -------------------------------------------------------------------------
def resolve_statement(statement: Statement, identifier_map: dict):
    """
    Resolves variables and sub-statements within a given Statement.
    """
    if isinstance(statement, Return):
        resolved_exp = resolve_exp(statement.exp, identifier_map)
        return Return(exp=resolved_exp)

    elif isinstance(statement, For):
        new_map = copy_identifier_map(identifier_map)
        init = resolve_for_init(statement.init, new_map)
        condition = resolve_optional_exp(statement.condition, new_map)
        post = resolve_optional_exp(statement.post, new_map)
        body = resolve_statement(statement.body, new_map)
        # Label the loop
        labeled_for = label_statement(For(init, condition, post, body))
        return labeled_for

    elif isinstance(statement, Expression):
        resolved_exp = resolve_exp(statement.exp, identifier_map)
        return Expression(exp=resolved_exp)

    elif isinstance(statement, Compound):
        new_map = copy_identifier_map(identifier_map)
        resolved_block = resolve_block_items(statement.block, new_map)
        return Compound(block=resolved_block)

    elif isinstance(statement, While):
        resolved_condition = resolve_exp(statement._condition, identifier_map)
        resolved_body = resolve_statement(statement.body, identifier_map)
        labeled_while = label_statement(While(_condition=resolved_condition, body=resolved_body))
        return labeled_while

    elif isinstance(statement, DoWhile):
        resolved_condition = resolve_exp(statement._condition, identifier_map)
        resolved_body = resolve_statement(statement.body, identifier_map)
        labeled_do = label_statement(DoWhile(body=resolved_body, _condition=resolved_condition))
        return labeled_do

    elif isinstance(statement, Break):
        return Break()

    elif isinstance(statement, Continue):
        return Continue()

    elif isinstance(statement, If):
        resolved_exp = resolve_exp(statement.exp, identifier_map)
        resolved_then = resolve_statement(statement.then, identifier_map)
        if statement._else is not None:
            resolved_else = resolve_statement(statement._else, identifier_map)
            return If(exp=resolved_exp, then=resolved_then, _else=resolved_else)
        else:
            return If(exp=resolved_exp, then=resolved_then)

    elif isinstance(statement, Null):
        return Null()

    else:
        raise SyntaxError(f"Invalid statement type: {type(statement)}")


# -------------------------------------------------------------------------
# 7) Annotate (Helper)
# -------------------------------------------------------------------------
def annotate(statement: Statement, label: int) -> Statement:
    """
    Annotates a given statement with the provided label.
    Typically used for loops (While, For, DoWhile).
    """
    statement.label = label
    return statement


# -------------------------------------------------------------------------
# 8) Label Statement (Loop Labeling)
# -------------------------------------------------------------------------
def label_statement(statement: Statement, current_label: Optional[str] = None) -> Statement:
    """
    Recursively annotates loops and handles 'break'/'continue' with the proper label.
    """
    if isinstance(statement, list):
        for stmt in statement:
            label_statement(stmt, current_label)
        return statement

    if isinstance(statement, Break):
        if current_label is None:
            raise ValueError("Error: 'break' outside of loop")
        statement.label = current_label

    elif isinstance(statement, Continue):
        if current_label is None:
            raise ValueError("Error: 'continue' outside of loop")
        statement.label = current_label

    elif isinstance(statement, While):
        new_label = get_label()
        annotate(statement, new_label)
        label_statement(statement.body, new_label)

    elif isinstance(statement, For):
        new_label = get_label()
        annotate(statement, new_label)
        if statement.body:
            label_statement(statement.body, new_label)

    elif isinstance(statement, DoWhile):
        new_label = get_label()
        annotate(statement, new_label)
        label_statement(statement.body, new_label)

    elif isinstance(statement, Compound):
        for block_item in statement.block:
            label_statement(block_item, current_label)

    elif isinstance(statement, S):
        label_statement(statement.statement, current_label)

    elif isinstance(statement, D):
        if isinstance(statement.declaration,InitDecl):
            label_statement(statement.declaration.declaration,current_label)
    
        elif isinstance(statement.declaration,VarDecl):
            label_statement(statement.declaration.init, current_label)

    elif isinstance(statement, Conditional):
        label_statement(statement.exp2, current_label)
        label_statement(statement.exp3, current_label)

    elif isinstance(statement, If):
        label_statement(statement._else, current_label)
        label_statement(statement.then, current_label)
        
    elif isinstance(statement, FunctionCall):
        pass  # no label needed
    
    elif isinstance(statement, (Return, Var, Constant)):
        pass  # no label needed

    elif isinstance(statement, (Expression, Assignment, Binary, Unary,Cast,AddOf,Dereference,SingleInit,CompoundInit)):
        pass  # no label needed

    elif isinstance(statement, Null):
        pass  # no label needed

    else:
        raise TypeError(f"Unsupported statement type for labeling: {type(statement)}")

    return statement


# -------------------------------------------------------------------------
# 9a) Resolve For-Init
# -------------------------------------------------------------------------
def resolve_for_init(stmt, identifier_map):
    """
    Resolves either an InitDecl or an InitExp in a for-loop initializer.
    """
    if isinstance(stmt, InitDecl):
        new_decl = resolve_declaration(stmt.declaration, identifier_map)
        return InitDecl(D(new_decl))
    elif isinstance(stmt, InitExp):
        resolved_expr = resolve_exp(stmt.exp, identifier_map)
        return InitExp(Expression(resolved_expr))
    elif isinstance(stmt, Null):
        return stmt
    else:
        raise TypeError("Invalid init condition for 'for'", stmt)


# -------------------------------------------------------------------------
# 9b) Resolve Optional Expression
# -------------------------------------------------------------------------
def resolve_optional_exp(stmt, identifier_map):
    """
    If stmt exists, resolve it as an expression. Otherwise, do nothing.
    """
    if stmt is not None:
        return resolve_exp(stmt, identifier_map)
    else:
        return None


# -------------------------------------------------------------------------
# 10) Label the Entire Program
# -------------------------------------------------------------------------
def label_program(program: Program):
    """
    Labels all loops in each function of the program. If your AST
    supports multiple functions, you can label each function body.
    """
    # If program.function_definition is a single function, label it
    # If it's a list of functions, label each.
    for decl in program.function_definition:
        if isinstance(decl, FunDecl):
            label_statement(decl.body, None)
        elif isinstance(decl,VarDecl):
            pass 
        else:
            pass
    return program


# -------------------------------------------------------------------------
# 11) Resolve a Function Declaration
# -------------------------------------------------------------------------
def resolve_function_declaration(decl: FunDecl, identifier_map: dict) -> FunDecl:
    # print(decl.name.identifier.name)
    # exit()
    """
    Resolves a function declaration (parameters + body).
    - We record the function name in identifier_map with has_linkage=True.
    - Then copy the map for parameters, rename them, and resolve the body.
    """
    
    # print(func_name)
    # print(decl.name)
    func_name = decl.name.name
    # exit()
    

    # exit()
    # Check for a conflicting local variable
    if func_name in identifier_map:
        prev_entry = identifier_map[func_name]
        # If it was declared in the same scope with no linkage, conflict
        if prev_entry['from_current_scope'] and not (prev_entry['has_linkage'] is True):
            raise SyntaxError("Duplicate declaration for a function name in current scope")

    # Add or override the function name with has_linkage=True
    identifier_map[func_name] = {
        'unique_name': func_name,
        'from_current_scope': True,
        'has_linkage': True
    }

    # Create an inner map for parameters & function body
    inner_map = copy_identifier_map(identifier_map)

    # Resolve parameters
    new_params = []
    # print([name.name.name for name in decl.params])
    # exit()
    for param in decl.params:
      
        new_params.append(resolve_param(param, inner_map))
    # Resolve the function body (if it's a Block) => block_items
    if isinstance(decl.body, Block):
        # print('here')
        new_body = resolve_block_items(decl.body.block_items, inner_map)
    else:
        new_body = decl.body  # or raise error if needed

    return FunDecl(name=decl.name, params=new_params, fun_type=decl.fun_type,body=new_body,storage_class=decl.storage_class)


def resolve_param(param: Parameter, identifier_map: dict) -> Parameter:
    """
    Resolves a function parameter. Generates a unique name for it (local variable).
    """
   
    if not isinstance(param.name, Identifier):
        raise TypeError(f"Parameter name must be an Identifier, got {type(param.name)}")

    # print('Here')
    print(param.name.name.name)
    # exit()
    original_name = param.name.name.name
    print(param._type)
    # exit()
    print(original_name)
    # exit()
    # Check duplicate param in the same scope
    if (original_name in identifier_map 
        and identifier_map[original_name]['from_current_scope']):
        raise ValueError(f"Duplicate parameter name: '{original_name}'")

    # Generate a unique name for the parameter
    unique_name = make_temporary_var()
    identifier_map[original_name] = {
        'unique_name': unique_name,
        'from_current_scope': True,
        'has_linkage': False
    }

    # Return a new Parameter node with the unique name
    return Parameter(name=Identifier(unique_name), _type=param._type)


# -------------------------------------------------------------------------
# 12) The Top-Level Variable Resolution Pass
# -------------------------------------------------------------------------
def variable_resolution_pass(program: Program) :
    """
    Perform the variable resolution pass on each function in the program.
    1) Create an empty identifier_map.
    2) Resolve each function declaration (parameters, body).
    3) Label loops if desired.
    """
    identifier_map = {}
    resolved_funcs = []
    # program.function_definition might be a list of FunDecl or a single FunDecl
    for decl in program.function_definition:
        if isinstance(decl,FunDecl):
            # print('New func')
            new = resolve_function_declaration(decl, identifier_map)
        elif isinstance(decl,VarDecl):
            # print('New var')
            new = resolve_declaration(decl, identifier_map,is_file_scope=True)
            
            
        resolved_funcs.append(new)

    new_program = Program(function_definition=resolved_funcs)
    labeled_program,symbols = typecheck_program(label_program(new_program))
  
    return labeled_program ,symbols


    