from assembly_ast import * 
from typing import * 
import sys

def replace_pseudoregisters(assembly_program: AssemblyProgram,current_param_offset:dict=None) -> Tuple[AssemblyProgram, Dict[str, int]]:
    """
    Replaces all Pseudo operands in the Assembly AST with Stack operands for each function.
    Calculates and returns the stack allocation required for each function.

    Additionally, rewrites 'idiv', 'add', 'sub', and 'imul' instructions to adhere to assembly constraints
    (especially for 64-bit mode).

    NOTE: This version uses 8-byte slots for each pseudo register and inserts 'Cdq' before 'idiv'.
    """
    stack_allocations: Dict[str, int] = {}
    # global current_offset

    # Assume a single function for simplicity
    for assembly_func in assembly_program.function_definition:
        # print(assembly_func.name)

        # Maps pseudo register names to stack offsets
        pseudo_map: Dict[str, int] = {}

        # Initialize stack offset; start at -8(%rbp)
        # current_offset=-current_param_offset[assembly_func.name]+8
        # print(current_offset)
        current_offset=-8
        # List to hold the new set of instructions after replacement
        new_instructions: List[Instruction] = []
        def replace_pseudo_with_stack(operand):
            """
            If the operand is a Pseudo, replace it with a Stack operand at the next available offset.
            """
            nonlocal current_offset
            if isinstance(operand, Pseudo):
                name = operand.identifier
                if name not in pseudo_map:
                    pseudo_map[name] = current_offset
                    current_offset -= 8  # Allocate 8 bytes for each pseudo register
                return Stack(pseudo_map[name])
            return operand
        
        for instr in assembly_func.instructions :

            if isinstance(instr, Mov):
                # Replace source and destination if they are Pseudo
                instr.src = replace_pseudo_with_stack(instr.src)
                instr.dest = replace_pseudo_with_stack(instr.dest)
                new_instructions.append(instr)
            
            elif isinstance(instr, Unary):
                # Replace the operand if it's a Pseudo
                instr.operand = replace_pseudo_with_stack(instr.operand)
                new_instructions.append(instr)
            
            elif isinstance(instr, Binary):
                # Replace src1 and src2 if they are Pseudo
                instr.src1 = replace_pseudo_with_stack(instr.src1)
                instr.src2 = replace_pseudo_with_stack(instr.src2)
                new_instructions.append(instr)
            
            elif isinstance(instr, Idiv):
                # Replace the operand if it's a Pseudo
                instr.operand = replace_pseudo_with_stack(instr.operand)
                new_instructions.append(instr)
            
            elif isinstance(instr, Cmp):
                # Replace the operand if it's a Pseudo
                instr.operand1 = replace_pseudo_with_stack(instr.operand1)
                instr.operand2 = replace_pseudo_with_stack(instr.operand2)
                new_instructions.append(instr)
            elif isinstance(instr, SetCC):
                # Replace the operand if it's a Pseudo
                # print('STECC',instr)
                instr.operand = replace_pseudo_with_stack(instr.operand)
                new_instructions.append(instr)
                # instr.operand2 = replace_pseudo_with_stack(instr.operand2)
            elif isinstance(instr,Push):
                instr.operand=replace_pseudo_with_stack(instr.operand)
                new_instructions.append(instr)
            elif isinstance(instr, (AllocateStack, Ret, Cdq,JmpCC,Jmp,Label,Call,DeallocateStack)):
                # These instructions do not contain Pseudo operands; add them directly
                new_instructions.append(instr)
            
            else:
                

                # Unsupported instruction type encountered
                print(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_func.name}'.", file=sys.stderr)
                sys.exit(1)

        # Update the function's instructions with the new set of instructions
        assembly_func.instructions =new_instructions
        
        # Calculate total stack allocation required for all replaced pseudoregisters
        # Since current_offset started at -8 and decremented by 8 for each Pseudo
        # The total allocation is the absolute value of (current_offset + 8)
        total_stack_allocation = abs(current_offset + 8)
        stack_allocations[assembly_func.name] = total_stack_allocation

    return assembly_program, stack_allocations