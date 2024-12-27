# instruction_fixer.py

from typing import List, Dict
from assembly_ast import (
    AssemblyProgram,
    AssemblyFunction,
    Instruction,
    Mov,
    Ret,
    Reg,
    Registers,
    AllocateStack,
    Unary,
    Stack
)

def fix_up_instructions(assembly_program: AssemblyProgram, stack_allocations: Dict[str, int]) -> None:
    """
    Performs two fixes on the Assembly AST for each function:
    1. Inserts an AllocateStack instruction at the beginning of the instruction list.
    2. Rewrites invalid Mov instructions where both src and dest are Stack operands.
    
    Args:
        assembly_program (AssemblyProgram): The AssemblyProgram AST to process.
        stack_allocations (Dict[str, int]): A dictionary mapping function names to their total stack allocation in bytes.
    
    Returns:
        None. The function modifies the assembly_program in place.
    """
    # Iterate over each AssemblyFunction in the AssemblyProgram
    assembly_func = assembly_program.function_definition
    stack_allocation = stack_allocations.get(assembly_func.name, 0)
        
        # 1. Insert AllocateStack at the beginning of the instruction list
    allocate_instr = AllocateStack(value=stack_allocation)
    assembly_func.instructions.insert(0, allocate_instr)
    print(f"Inserted AllocateStack({allocate_instr.value}) at the beginning of function '{assembly_func.name}'.")
        
        # 2. Traverse the instruction list to find and fix invalid Mov instructions
    new_instructions: List[Instruction] = []
        
    for instr in assembly_func.instructions:
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
    assembly_func.instructions = new_instructions
        # Debug Statement
    print(f"Completed fixing instructions for function '{assembly_func.name}'.")
