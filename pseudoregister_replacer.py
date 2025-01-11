from assembly_ast import * 
from typing import * 
import sys
from type_classes import *

def replace_pseudoregisters(assembly_program: AssemblyProgram, symbols: Dict[str, Any]) -> Tuple[AssemblyProgram, Dict[str, int]]:
    """
    Replaces all Pseudo operands in the Assembly AST with Stack operands for each function.
    Calculates and returns the stack allocation required for each function.

    Additionally, rewrites 'idiv', 'add', 'sub', and 'imul' instructions to adhere to assembly constraints
    (especially for 64-bit mode).

    NOTE: This version uses 8-byte slots for each pseudo register and inserts 'Cdq' before 'idiv'.
    """
    stack_allocations: Dict[str, int] = {}
    
    # Extract static variable names from symbols
    static_vars = [var for var, _ in symbols.items()]
    # Debug: Print static variables
    #print(f"Static Variables: {static_vars}")
    
    # Iterate over each function in the assembly program
    for assembly_func in assembly_program.function_definition:
        # Initialize pseudo register mapping for the current function
        pseudo_map: Dict[str, int] = {}
        
        # Initialize stack offset; start at -8(%rbp)
        current_offset = -8
        
        # List to hold the new set of instructions after replacement
        new_instructions: List[Instruction] = []
        
        def replace_pseudo_with_operand(operand):
            nonlocal current_offset
            if isinstance(operand, Pseudo):
                name = operand.identifier
                #print(f"Processing Pseudo Operand: {name}")
                
                if name not in pseudo_map:
                    #print(f"'{name}' not in pseudo_map. Determining replacement type.")
                    if name in static_vars and isinstance(symbols.get(name, {}).get('attrs'), StaticAttr):
                        #print(f"'{name}' is a static variable. Replacing with Data operand.")
                        operand = Data(name)
                    else:
                        #print(f"'{name}' is a dynamic variable. Assigning Stack offset {current_offset}.")
                        pseudo_map[name] = current_offset
                        operand = Stack(current_offset)
                        current_offset -= 8  # Adjust offset for next allocation
                else:
                    # Replace with existing Stack operand
                    #print(f"'{name}' already in pseudo_map with offset {pseudo_map[name]}. Replacing with Stack operand.")
                    operand = Stack(pseudo_map[name])
                
                #print(f"Replaced Operand: {operand}")
            return operand 
        
        # Function to process instructions based on their type
        def process_instruction(instr: Instruction) -> Optional[Instruction]:
            if isinstance(instr, Mov):
                instr.src = replace_pseudo_with_operand(instr.src)
                instr.dest = replace_pseudo_with_operand(instr.dest)
            elif isinstance(instr, Unary):
                instr.operand = replace_pseudo_with_operand(instr.operand)
            elif isinstance(instr, Binary):
                instr.src1 = replace_pseudo_with_operand(instr.src1)
                instr.src2 = replace_pseudo_with_operand(instr.src2)
            elif isinstance(instr, Idiv):
                instr.operand = replace_pseudo_with_operand(instr.operand)
            elif isinstance(instr, Cmp):
                instr.operand1 = replace_pseudo_with_operand(instr.operand1)
                instr.operand2 = replace_pseudo_with_operand(instr.operand2)
            elif isinstance(instr, SetCC):
                instr.operand = replace_pseudo_with_operand(instr.operand)
            elif isinstance(instr, Push):
                instr.operand = replace_pseudo_with_operand(instr.operand)
            elif isinstance(instr, (AllocateStack, Ret, Cdq, JmpCC, Jmp, Label, Call, DeallocateStack, Imm)):
                # These instructions do not contain Pseudo operands; no action needed
                pass
            else:
                # Unsupported instruction type encountered
                #print(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_func.name}'.", file=sys.stderr)
                sys.exit(1)
            
            # After processing, add the instruction to new_instructions
            new_instructions.append(instr)
            return instr
        
        # Process instructions for AssemblyFunction
        if isinstance(assembly_func, AssemblyFunction):
            #print(f"Processing AssemblyFunction: {assembly_func.name}")
            for instr in assembly_func.instructions:
                process_instruction(instr)
        
        # Process instructions for AssemblyStaticVariable
        elif isinstance(assembly_func, AssemblyStaticVariable):
            #print(f"Processing AssemblyStaticVariable: {assembly_func.name}")
            instr = assembly_func.init
            process_instruction(instr)
        
        else:
            #print(f"Unsupported assembly function type: {type(assembly_func).__name__} in program.", file=sys.stderr)
            sys.exit(1)
        
        # Update the function's instructions with the new set of instructions
        assembly_func.instructions = new_instructions
        
        # Calculate total stack allocation required for all replaced pseudoregisters
        # Since current_offset started at -8 and decremented by 8 for each Pseudo
        # The total allocation is the absolute value of (current_offset + 8)
        total_stack_allocation = abs(current_offset + 8)
        stack_allocations[assembly_func.name] = total_stack_allocation
        
        # Debug: Print stack allocation for the function
        #print(f"Stack Allocation for '{assembly_func.name}': {total_stack_allocation} bytes")
    
    return assembly_program, stack_allocations
