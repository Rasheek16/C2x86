from tacky import *
from assembly_ast import Mov, Ret, Imm, Registers, AssemblyFunction, AssemblyProgram, Reg, Unary, Pseudo , UnaryOperator ,Stack ,AllocateStack
import sys
from typing import Union, List ,Dict

def convert_to_assembly_ast(tacky_ast) -> AssemblyProgram:
    """
    Converts a Tacky AST into an AssemblyProgram AST.
    
    Args:
        tacky_ast: The root of the Tacky AST to be converted.
    
    Returns:
        An AssemblyProgram instance representing the equivalent assembly code.
    """
    # Handle the top-level Program node
    
    if isinstance(tacky_ast, TackyProgram):
        # Recursively convert the function_definition part of the TackyProgram
        assembly_function = convert_to_assembly_ast(tacky_ast.function_definition)
        return AssemblyProgram(
            function_definition=assembly_function
        )
    
    # Handle Function node
    elif isinstance(tacky_ast, TackyFunction):
        instructions = []
        # Iterate over each instruction in the TackyFunction
        # print(instructions)
        for instr in tacky_ast.body[0]:
            # Convert each instruction and collect them
            converted_instrs = convert_to_assembly_ast(instr)
            if isinstance(converted_instrs, list):
                # If conversion returns a list of instructions, extend the list
                instructions.extend(converted_instrs)
            else:
                # Otherwise, append the single instruction
                instructions.append(converted_instrs)
        # Create an AssemblyFunction with the converted instructions
        return AssemblyFunction(
            name=tacky_ast.name,  # Assuming tacky_ast.name is an Identifier
            instructions=instructions
        )
    
    # Handle Return instruction
    elif isinstance(tacky_ast, TackyReturn):
        # Convert a Return by moving the value into AX and issuing a Ret
        return [
            Mov(src=convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.AX)),
            Ret()
        ]
    
    # Handle Unary instruction
    elif isinstance(tacky_ast, TackyUnary):        
        # Convert a Unary operation by moving src to dst and applying the operator
        return [
            Mov(src=convert_to_assembly_ast(tacky_ast.src), dest=convert_to_assembly_ast(tacky_ast.dst)),
            Unary(operator=convert_operator(tacky_ast.operator), operand=convert_to_assembly_ast(tacky_ast.dst))
        ]
    
    # Handle Constant operand
    elif isinstance(tacky_ast, TackyConstant):
        # Convert a constant value into an Imm operand
        return Imm(tacky_ast.value)
    
    # Handle Variable operand
    elif isinstance(tacky_ast, TackyVar):
        # Convert a variable into a Pseudo operand
        # print(tacky_ast)
        return Pseudo(tacky_ast.identifier)
    
    else:
        # Print error message for unsupported AST nodes and exit
        print(f"Unsupported AST node: {type(tacky_ast).__name__}", file=sys.stderr)
        sys.exit(1)

def convert_operator(op: str) -> str:
    """
    Converts a Tacky unary operator to its Assembly equivalent.
    
    Args:
        op: The unary operator from the Tacky AST ('Complement' or 'Negate').
    
    Returns:
        A string representing the corresponding Assembly unary operator.
    
    Raises:
        ValueError: If the operator is unrecognized.
    """
    if op == 'Complement':
        return UnaryOperator.NOT  # e.g., bitwise NOT '~x'
    elif op in ('Negate','Negation'):
        return UnaryOperator.NEG  # e.g., arithmetic negation '-x'
    else:
        # If the operator is not recognized, raise an error
        raise ValueError(f"Unknown unary operator: {op}")




def replace_pseudoregisters(assembly_program: AssemblyProgram) -> int:
    """
    Replaces all Pseudo operands in the Assembly AST with Stack operands.
    
    Args:
        assembly_program (AssemblyProgram): The AssemblyProgram AST to process.
        
    Returns:
        int: The total number of bytes to allocate on the stack.
    """
    pseudo_map: Dict[str, int] = {}
    current_offset: int = -4  # Start at -4(%rbp)
    
    # Access the single AssemblyFunction within the AssemblyProgram
    assembly_function: AssemblyFunction = assembly_program.function_definition
    
    for instr in assembly_function.instructions:
        if isinstance(instr, Mov):
            # Replace src if it's a Pseudo
            if isinstance(instr.src, Pseudo):
                pseudo_name = instr.src.identifier
                if pseudo_name not in pseudo_map:
                    pseudo_map[pseudo_name] = current_offset
                    current_offset -= 4
                instr.src = Stack(pseudo_map[pseudo_name])
            
            # Replace dest if it's a Pseudo
            if isinstance(instr.dest, Pseudo):
                pseudo_name = instr.dest.identifier
                if pseudo_name not in pseudo_map:
                    pseudo_map[pseudo_name] = current_offset
                    current_offset -= 4
                instr.dest = Stack(pseudo_map[pseudo_name])
        
        elif isinstance(instr, Unary):
            # Replace operand if it's a Pseudo
            if isinstance(instr.operand, Pseudo):
                pseudo_name = instr.operand.identifier
                if pseudo_name not in pseudo_map:
                    pseudo_map[pseudo_name] = current_offset
                    current_offset -= 4
                instr.operand = Stack(pseudo_map[pseudo_name])
        
        # AllocateStack and Ret do not contain Pseudos to replace
        elif isinstance(instr, AllocateStack):
            # Optionally, handle AllocateStack if needed
            pass
        elif isinstance(instr, Ret):
            # No operands to replace in Ret
            pass
        else:
            print(f"Unsupported instruction type: {type(instr)}")
            sys.exit(1)
    
    # Calculate total stack allocation
    # Since current_offset starts at -4 and decrements by 4 for each new Pseudo,
    # the total allocation is abs(current_offset + 4)
    total_stack_allocation = abs(current_offset + 4)
    
    return total_stack_allocation


def fix_up_instructions(assembly_program: AssemblyProgram, stack_allocation: int) -> None:
    """
    Performs two fixes on the Assembly AST:
    1. Inserts an AllocateStack instruction at the beginning of each function's instruction list.
    2. Rewrites invalid Mov instructions where both src and dest are Stack operands.
    
    Args:
        assembly_program (AssemblyProgram): The AssemblyProgram AST to process.
        stack_allocation (int): The total stack space required based on allocated temporaries.
    
    Returns:
        None. The function modifies the assembly_program in place.
    """
    # Access the single AssemblyFunction within the AssemblyProgram
    assembly_function: AssemblyFunction = assembly_program.function_definition
    
    # 1. Insert AllocateStack at the beginning of the instruction list
    allocate_instr = AllocateStack(value=stack_allocation)
    assembly_function.instructions.insert(0, allocate_instr)
    # Debug Statement
    print(f"Inserted AllocateStack({allocate_instr.value}) at the beginning of function '{assembly_function.name}'.")
    
    # 2. Traverse the instruction list to find and fix invalid Mov instructions
    new_instructions: List = []
    
    for instr in assembly_function.instructions:
        if isinstance(instr, Mov):
            # Check if both src and dest are Stack operands
            if isinstance(instr.src, Stack) and isinstance(instr.dest, Stack):
                # Invalid Mov: both src and dest are Stack operands
                
                # Create a Mov from src Stack to R10D
                mov_to_reg = Mov(src=instr.src, dest=Reg(Registers.R10))
                # Create a Mov from R10D to dest Stack
                mov_to_dest = Mov(src=Reg(Registers.R10), dest=instr.dest)
                
                # Append the two new Mov instructions instead of the invalid one
                new_instructions.extend([mov_to_reg, mov_to_dest])
                
                # Debug Statement
                print(f"Rewrote invalid Mov instruction from {instr.src} to {instr.dest} using {Registers.R10}.")
            else:
                # Valid Mov instruction; keep as-is
                new_instructions.append(instr)
        else:
            # Other instructions; keep as-is
            new_instructions.append(instr)
    
    # Update the function's instruction list with the new instructions
    assembly_function.instructions = new_instructions
    # Debug Statement
    print(f"Completed fixing instructions for function '{assembly_function.name}'.")
