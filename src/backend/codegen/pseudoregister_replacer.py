from src.backend.codegen.assembly_ast import * 
from typing import * 
import sys
from src.backend.typechecker.type_classes import *
import logging
from src.frontend.parser._ast5 import Long, Int 

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
                        if name=='tmp.2':
                            print(symbol)
                            # exit()
                        if symbol.is_static:
                            return Data(name)
                        else:
                           
                            if symbol.assembly_type == AssemblyType.longWord:
                              
                                current_offset -= 4
                                current_offset = align_offset(current_offset, 4)
                            elif symbol.assembly_type== AssemblyType.byte:
                                current_offset -= 1
                               
                            else:
                                current_offset -= 8
                                current_offset = align_offset(current_offset, 8)
                                
                            pseudo_map[name] = current_offset
                            
                            
                            return Stack(current_offset)
                    else:
                        raise ValueError(f"Pseudo variable '{name}' not found in backend symbol table.")
                return Stack(pseudo_map[name])

            elif isinstance(operand, PseudoMem):
         
                nonlocal cf
                array_name = operand.identifier
                offset =  operand.size 
     
                if array_name in backend_Symbol_table:
                    print('Array name is pseudo map')
                    symbol = backend_Symbol_table[array_name]
                    if symbol.is_static :
                        if offset == 0:
                            # exit()
                            return Data(array_name)
                        else:
                            raise ValueError(f"Cannot convert PseudoMem('{array_name}', {offset}) using Data operand.")
                    else:
        
                    
                        # If the array's base hasn't been allocated yet, allocate it now.
                        if array_name not in pseudo_map:
                        
                            if isinstance(symbol.assembly_type ,AssemblyType.byteArray):
                                
                                current_offset -= symbol.assembly_type.size # Changed from += to -=
                                current_offset = int(align_offset(current_offset,16))
                            
                            elif symbol.assembly_type == AssemblyType.longWord:
                                current_offset -= 4
                                current_offset = align_offset(current_offset, 4)
                                #
                            elif symbol.assembly_type == AssemblyType.byte:
                                current_offset -= 1
                                
                            else:
                                current_offset -= 8
                                current_offset = align_offset(current_offset, 8)
                            pseudo_map[array_name] = current_offset

                        # print(symbol.assembly_type.size)
                        base_address = pseudo_map[array_name]
                 
                        final_offset = base_address + offset
                        # final_offset = align_offset(final_offset,)

                  
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
            elif isinstance(instr, (AllocateStack, Ret, Cdq, JmpCC, Jmp, Label, Call, DeallocateStack, Imm)):
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
