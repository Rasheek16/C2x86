# pseudoregister_replacer.py

from typing import Dict, Tuple
from assembly_ast import (
    AssemblyProgram,
    AssemblyFunction,
    Mov,
    Unary,
    Pseudo,
    Stack,
    Registers,
    AllocateStack,
    Ret
)
import sys

def replace_pseudoregisters(assembly_program: AssemblyProgram) -> Tuple[AssemblyProgram, Dict[str, int]]:
    """
    Replaces all Pseudo operands in the Assembly AST with Stack operands for each function.
    Calculates and returns the stack allocation required for each function.
    
    Args:
        assembly_program (AssemblyProgram): The AssemblyProgram AST to process.
        
    Returns:
        Tuple[AssemblyProgram, Dict[str, int]]: The modified AssemblyProgram and a dictionary
        mapping function names to their total stack allocation in bytes.
    """
    stack_allocations: Dict[str, int] = {}
    
    # Iterate over each AssemblyFunction in the AssemblyProgram
    assembly_func= assembly_program.function_definition
    pseudo_map: Dict[str, int] = {}
    current_offset: int = -4  # Start at -4(%rbp), decrement by 4 for each new Pseudo
        
        # Iterate over each instruction in the function
    for instr in assembly_func.instructions:
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
                print('Insid ethe func dest')
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
        elif isinstance(instr, (AllocateStack, Ret)):
            continue  # No action needed
            
        else:
            print(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_func.name}'.", file=sys.stderr)
            sys.exit(1)
        
        # Calculate total stack allocation for the function
        # Since current_offset starts at -4 and decrements by 4 for each new Pseudo,
        # the total stack allocation is abs(current_offset + 4)
        total_stack_allocation = abs(current_offset + 4)
        stack_allocations[assembly_func.name] = total_stack_allocation
    
    return assembly_program, stack_allocations
