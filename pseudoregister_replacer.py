# from assembly_ast import * 
# from typing import * 
# import sys
# from type_classes import *
# import logging
# from _ast5 import Long,Int 

# # Configure logging
# logging.basicConfig(level=logging.DEBUG)
# #logger = logging.getLogger(__name__)


# def get_type(_type):
#     if type(_type)==type(Long()):
#         return AssemblyType.quadWord
#     elif type(_type)==type(Int()):
#         return AssemblyType.longWord
#     else:
#         print(_type)
#         raise ValueError(f"Unknown type: {_type}")
        
    

# def replace_pseudoregisters(assembly_program: AssemblyProgram, symbols: Dict[str, Any],backend_Symbol_table) -> Tuple[AssemblyProgram, Dict[str, int]]:
#     """
#     Replaces all Pseudo operands in the Assembly AST with Stack operands for each function.
#     Calculates and returns the stack allocation required for each function.

#     Additionally, rewrites 'idiv', 'add', 'sub', and 'imul' instructions to adhere to assembly constraints
#     (especially for 64-bit mode).

#     NOTE: This version uses 8-byte slots for each pseudo register and inserts 'Cdq' before 'idiv'.
#     """
#     stack_allocations: Dict[str, int] = {}
#     # symbols=backend_Symbol_table
#     # Extract static variable names from symbols
#     static_vars = [var for var, _ in symbols.items()]
#     # Debug: Print static variables
#     #print(f"Static Variables: {static_vars}")
    
#     # Iterate over each function in the assembly program
#     for assembly_func in assembly_program.function_definition:
#         # Initialize pseudo register mapping for the current function
#         pseudo_map: Dict[str, int] = {}
        
#         # Initialize stack offset; start at -8(%rbp)
#         current_offset = -8
        
#         # List to hold the new set of instructions after replacement
#         new_instructions: List[Instruction] = []
#         # print(backend_Symbol_table)
#         # exit()
#         def align_offset(offset, alignment):
#                 """Ensure the offset is aligned to the specified byte boundary."""
#                 return offset - (offset % alignment) if offset % alignment != 0 else offset
#         def replace_pseudo_with_operand(operand):
#             nonlocal current_offset  # or 'global current_offset' if it's truly global
            
#             if isinstance(operand, Pseudo):
#                 name = operand.identifier
                
#                 if name not in pseudo_map:
#                     # Check if it's defined in the backend symbol table
#                     if name in backend_Symbol_table:
#                         # If the symbol is static, replace with a Data operand
#                         if backend_Symbol_table[name].is_static:
#                             operand = Data(name)
#                             return operand
#                         else:
#                             print('Name in backend symbol table not static',name)
#                             print(backend_Symbol_table[name].assembly_type)
                        
#                             if backend_Symbol_table[name].assembly_type==AssemblyType.longWord:
#                                 current_offset -= 4  
#                                 pseudo_map[name] = current_offset
#                                 operand = Stack(current_offset)
#                                 return operand
#                             else:
#                                 print('Found here')
#                                 print(name)
#                                 current_offset -= 8  # Adjust offset for next allocation
#                                 current_offset = align_offset(current_offset, 8)
#                                 pseudo_map[name] = current_offset
#                                 operand = Stack(current_offset)
#                                 # e
#                                 return operand
#                     else:
#                         print(name.identifier)
#                         print(name.identifier in backend_Symbol_table)
#                         print(backend_Symbol_table)
#                         exit()
#                             # current_offset -= 8  # Adjust offset for next allocation
#                             # current_offset = align_offset(current_offset, 8)
#                             # pseudo_map[name] = current_offset
#                             # operand = Stack(current_offset)
#                             # operand = Stack(current_offset)
#                             # return operand
#                 else:
#                     # Already mapped, just replace with existing stack offset
#                     operand = Stack(pseudo_map[name])
            
#             return operand

#         # def replace_pseudo_with_operand(operand):
#             # nonlocal current_offset
#             # if isinstance(operand, Pseudo):
#             #     name = operand.identifier
#             #     #print(f"Processing Pseudo Operand: {name}")
#             #     if name not in pseudo_map:
#             #         if name in backend_Symbol_table:
#             #             if backend_Symbol_table[name].is_static:
                            
#             #                 operand = Data(name)
#             #             else:
#             #                 if backend_Symbol_table[name].assembly_type==AssemblyType.longWord:
#             #                     print(operand)
#             #                     print(pseudo_map)
                                
#             #                     current_offset -= 4  # Adjust offset for next allocation
#             #                     pseudo_map[name] = current_offset
#             #                     operand = Stack(current_offset)
#             #                 else:
#             #                     current_offset -= 8  # Adjust offset for next allocation
#             #                     current_offset = align_offset(current_offset, 8)
#             #                     pseudo_map[name] = current_offset
#             #                     operand = Stack(current_offset)
                                    
#             #     else:
#             #         # Replace with existing Stack operand
                   
#             #         operand = Stack(pseudo_map[name])
                
#             # return operand 
        
     
#         # Function to process instructions based on their type
#         def process_instruction(instr: Instruction) -> Optional[Instruction]:
#             if isinstance(instr, Mov):
#                 instr.src = replace_pseudo_with_operand(instr.src)
#                 instr.dest = replace_pseudo_with_operand(instr.dest)
#             elif isinstance(instr, Unary):
#                 instr.operand = replace_pseudo_with_operand(instr.operand)
#             elif isinstance(instr, Binary):
#                 print(instr)
#                 # exit()
#                 instr.src1 = replace_pseudo_with_operand(instr.src1)
#                 instr.src2 = replace_pseudo_with_operand(instr.src2)
#             elif isinstance(instr, Idiv):
#                 instr.operand = replace_pseudo_with_operand(instr.operand)
#             elif isinstance(instr, Cmp):
#                 instr.operand1 = replace_pseudo_with_operand(instr.operand1)
#                 instr.operand2 = replace_pseudo_with_operand(instr.operand2)
#             elif isinstance(instr, SetCC):
#                 instr.operand = replace_pseudo_with_operand(instr.operand)
#             elif isinstance(instr, Push):
#                 instr.operand = replace_pseudo_with_operand(instr.operand)
#             elif isinstance(instr,Movsx):
#                 instr.dest=replace_pseudo_with_operand(instr.dest)
#                 instr.src=replace_pseudo_with_operand(instr.src)
#             elif isinstance(instr, MovZeroExtend):
#                 instr.dest = replace_pseudo_with_operand(instr.dest)
#                 instr.src = replace_pseudo_with_operand(instr.src)
#             elif isinstance(instr,  (Div,Idiv)):
#                 instr.operand = replace_pseudo_with_operand(instr.operand)
#             elif isinstance(instr,Cvtsi2sd):
#                 instr.src=replace_pseudo_with_operand(instr.src)
#                 instr.dst=replace_pseudo_with_operand(instr.dst)
#             elif isinstance(instr,Cvttsd2si):
#                 instr.src=replace_pseudo_with_operand(instr.src)
#                 instr.dst=replace_pseudo_with_operand(instr.dst)
#             elif isinstance(instr,Lea):
#                 instr.src=replace_pseudo_with_operand(instr.src)
#                 instr.dst=replace_pseudo_with_operand(instr.dst)

                
#             elif isinstance(instr, (AllocateStack, Ret, Cdq, JmpCC, Jmp, Label, Call, DeallocateStack, Imm)):
#                 # These instructions do not contain Pseudo operands; no action needed
#                 pass
#             else:
#                 # Unsupported instruction type encountered
#                 print(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_func.name}'.", file=sys.stderr)
#                 sys.exit(1)
            
#             # After processing, add the instruction to new_instructions
#             new_instructions.append(instr)
#             return instr
        
#         # Process instructions for AssemblyFunction
#         if isinstance(assembly_func, AssemblyFunction):
#             #print(f"Processing AssemblyFunction: {assembly_func.name}")
#             for instr in assembly_func.instructions:
#                 process_instruction(instr)
        
#         # Process instructions for AssemblyStaticVariable
#         elif isinstance(assembly_func, (AssemblyStaticVariable,AssemblyStaticConstant)):
#             pass 
#             #print(f"Processing AssemblyStaticVariable: {assembly_func.name}")
#             # instr = assembly_func.init
#             # process_instruction(instr._int)
        
#         else:
#             #print(f"Unsupported assembly function type: {type(assembly_func).__name__} in program.", file=sys.stderr)
#             sys.exit(1)
        
#         # Update the function's instructions with the new set of instructions
#         assembly_func.instructions = new_instructions
        
#         # Calculate total stack allocation required for all replaced pseudoregisters
#         # Since current_offset started at -8 and decremented by 8 for each Pseudo
#         # The total allocation is the absolute value of (current_offset + 8)
#         total_stack_allocation = abs(current_offset + 8)
#         stack_allocations[assembly_func.name] = total_stack_allocation
        
#         # Debug: Print stack allocation for the function
#         #print(f"Stack Allocation for '{assembly_func.name}': {total_stack_allocation} bytes")
    
#     return assembly_program, stack_allocations,backend_Symbol_table

from assembly_ast import * 
from typing import * 
import sys
from type_classes import *
import logging
from _ast5 import Long, Int 

# Configure logging
logging.basicConfig(level=logging.DEBUG)

def get_type(_type):
    if isinstance(_type, Long):
        return AssemblyType.quadWord
    elif isinstance(_type, Int):
        return AssemblyType.longWord
    else:
        raise ValueError(f"Unknown type: {_type}")

def replace_pseudoregisters(
    assembly_program: AssemblyProgram, 
    symbols: Dict[str, Any], 
    backend_Symbol_table
) -> Tuple[AssemblyProgram, Dict[str, int]]:
    """
    Replaces Pseudo and PseudoMem operands in the Assembly AST with stack or memory references.
    Returns modified AssemblyProgram and stack allocations per function.
    """
    stack_allocations: Dict[str, int] = {}
    static_vars = [var for var, _ in symbols.items()]

    for assembly_func in assembly_program.function_definition:
        pseudo_map: Dict[str, int] = {}
        current_offset = -8  # Stack starts from -8(%rbp)
        cf = 0
        new_instructions: List[Instruction] = []

        def align_offset(offset, alignment):
            return offset - (offset % alignment) if offset % alignment != 0 else offset

        def replace_pseudo_with_operand(operand):
            nonlocal current_offset

            if isinstance(operand, Pseudo):
                name = operand.identifier
                # exit()
                if name not in pseudo_map:
                    if name in backend_Symbol_table:
                        symbol = backend_Symbol_table[name]
                        if symbol.is_static:
                            return Data(name)
                        else:
                           
                            if symbol.assembly_type == AssemblyType.longWord:
                                current_offset -= 4
                                # current_offset = align_offset(current_offset, 4)
                            else :
                                current_offset -= 8
                                current_offset = align_offset(current_offset, 8)
                            # else:
                            #     current_offset -= operand.size 
                            pseudo_map[name] = current_offset
                            return Stack(current_offset)
                    else:
                        raise ValueError(f"Pseudo variable '{name}' not found in backend symbol table.")
                return Stack(pseudo_map[name])

            elif isinstance(operand, PseudoMem):
                # print(operand.identifier)
                # print(operand.size)
                # print(symbols[operand.identifier])
                nonlocal cf
                array_name = operand.identifier
                offset =  operand.size  # Offset in bytes from the start of the array
                # if offset > 4:
                #     print(offset)
                #     exit()
                if array_name in backend_Symbol_table:
                    print('Array name is pseudo map')
                    symbol = backend_Symbol_table[array_name]
                    if symbol.is_static:
                        if offset == 0:
                            return Data(array_name)
                        else:
                            raise ValueError(f"Cannot convert PseudoMem('{array_name}', {offset}) using Data operand.")
                    else:
                        # print('Array is not static')
                        # print('Pseudo map',pseudo_map)
                        # If the array's base hasn't been allocated yet, allocate it now.
                        if array_name not in pseudo_map:
                            # print('Array not in pseudo map',isinstance(symbol.assembly_type,AssemblyType.byteArray))
                            # print('Alignment', symbol.assembly_type.alignment)
                            # print('Size', symbol.assembly_type.size)
                            # exit()
                            if isinstance(symbol.assembly_type ,AssemblyType.byteArray):
                                current_offset -= symbol.assembly_type.size # Changed from += to -=
                                # print(symbol.assembly_type.size)
                                # print(current_offset)
                                current_offset = int (align_offset(current_offset,16))
                                # if symbol.assembly_type.size>=40:
                                #     print(current_offset)
                                #     exit()
                            elif symbol.assembly_type == AssemblyType.longWord:
                                current_offset -= 4
                                # current_offset = align_offset(current_offset, 4)
                            else:
                                current_offset -= 8
                                current_offset = align_offset(current_offset, 8)
                            pseudo_map[array_name] = current_offset

                        # print(symbol.assembly_type.size)
                        base_address = pseudo_map[array_name]
                        # print(pseudo_map)
                        # print(base_address)
                        # exit()
                        # Remove the -4 adjustment to make indexing zero based.
                        # current_offset 
                        final_offset = base_address + offset

                  
                        return Memory(Reg(Registers.BP), final_offset)
                else:
                    raise ValueError(f"PseudoMem array '{array_name}' not found in backend symbol table.")

            return operand

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
            elif isinstance(instr, Movsx):
                instr.dest = replace_pseudo_with_operand(instr.dest)
                instr.src = replace_pseudo_with_operand(instr.src)
            elif isinstance(instr, MovZeroExtend):
                instr.dest = replace_pseudo_with_operand(instr.dest)
                instr.src = replace_pseudo_with_operand(instr.src)
            elif isinstance(instr, (Div, Idiv)):
                instr.operand = replace_pseudo_with_operand(instr.operand)
            elif isinstance(instr, Cvtsi2sd):
                instr.src = replace_pseudo_with_operand(instr.src)
                instr.dst = replace_pseudo_with_operand(instr.dst)
            elif isinstance(instr, Cvttsd2si):
                instr.src = replace_pseudo_with_operand(instr.src)
                instr.dst = replace_pseudo_with_operand(instr.dst)
            elif isinstance(instr, Lea):
                instr.src = replace_pseudo_with_operand(instr.src)
                instr.dst = replace_pseudo_with_operand(instr.dst)
            elif isinstance(instr, Memory):
                instr.address = replace_pseudo_with_operand(instr.address)
            elif isinstance(instr, (AllocateStack, Ret, Cdq, JmpCC, Jmp, Label, Call, DeallocateStack, Imm,MovZeroExtend)):
                pass  # No changes required
            else:
                print(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_func.name}'.", file=sys.stderr)
                sys.exit(1)

            new_instructions.append(instr)
            return instr

        if isinstance(assembly_func, AssemblyFunction):
            for instr in assembly_func.instructions:
                process_instruction(instr)
        elif isinstance(assembly_func, (AssemblyStaticVariable, AssemblyStaticConstant)):
            pass
        else:
            sys.exit(1)

        assembly_func.instructions = new_instructions
        total_stack_allocation = abs(current_offset + 8) 
        stack_allocations[assembly_func.name] = total_stack_allocation

    return assembly_program, stack_allocations, backend_Symbol_table
