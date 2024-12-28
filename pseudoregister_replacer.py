# pseudoregister_replacer.py

from typing import Dict, Tuple, List
from assembly_ast import (
    AssemblyProgram,
    AssemblyFunction,
    Mov,
    Unary,
    Pseudo,
    Stack,
    Registers,
    AllocateStack,
    Ret,
    Idiv,
    Binary,Reg,Instruction,Imm,BinaryOperator,Cqd
)
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def replace_pseudoregisters(assembly_program: AssemblyProgram) -> Tuple[AssemblyProgram, Dict[str, int]]:
    """
    Replaces all Pseudo operands in the Assembly AST with Stack operands for each function.
    Calculates and returns the stack allocation required for each function.
    
    Additionally, rewrites 'idiv', 'add', 'sub', and 'imul' instructions to adhere to assembly constraints
    by introducing temporary registers as necessary.
    
    Args:
        assembly_program (AssemblyProgram): The AssemblyProgram AST to process.
        
    Returns:
        Tuple[AssemblyProgram, Dict[str, int]]: The modified AssemblyProgram and a dictionary
        mapping function names to their total stack allocation in bytes.
    """
    stack_allocations: Dict[str, int] = {}
    
    # Iterate over each AssemblyFunction in the AssemblyProgram
    assembly_func = assembly_program.function_definition  # Assuming a single function
    pseudo_map: Dict[str, int] = {}
    current_offset: int = -4  # Start at -4(%rbp), decrement by 4 for each new Pseudo
    
    # Initialize a new list to hold the updated instructions after transformations
    new_instructions: List[Instruction] = []
    
    # Iterate over each instruction in the function's instruction list
    for instr in assembly_func.instructions:
        if isinstance(instr, Mov):
            # Replace src if it's a Pseudo operand
            if isinstance(instr.src, Pseudo):
                pseudo_name = instr.src.identifier
                if pseudo_name not in pseudo_map:
                    pseudo_map[pseudo_name] = current_offset
                    current_offset -= 4
                instr.src = Stack(pseudo_map[pseudo_name])
                logger.debug(f"Replaced Mov src Pseudo '{pseudo_name}' with Stack(offset={pseudo_map[pseudo_name]}).")
            
            # Replace dest if it's a Pseudo operand
            if isinstance(instr.dest, Pseudo):
                pseudo_name = instr.dest.identifier
                if pseudo_name not in pseudo_map:
                    pseudo_map[pseudo_name] = current_offset
                    current_offset -= 4
                instr.dest = Stack(pseudo_map[pseudo_name])
                logger.debug(f"Replaced Mov dest Pseudo '{pseudo_name}' with Stack(offset={pseudo_map[pseudo_name]}).")
            
            # Append the modified Mov instruction
            new_instructions.append(instr)
        
        elif isinstance(instr, Unary):
            # Replace operand if it's a Pseudo operand
            if isinstance(instr.operand, Pseudo):
                pseudo_name = instr.operand.identifier
                if pseudo_name not in pseudo_map:
                    pseudo_map[pseudo_name] = current_offset
                    current_offset -= 4
                instr.operand = Stack(pseudo_map[pseudo_name])
                logger.debug(f"Replaced Unary operand Pseudo '{pseudo_name}' with Stack(offset={pseudo_map[pseudo_name]}).")
            
            # Append the modified Unary instruction
            new_instructions.append(instr)
        
        elif isinstance(instr, Binary):
            # Handle Binary Operators: add, sub, imul
            operator = instr.operator
            if operator in(BinaryOperator.ADD,BinaryOperator.SUBTRACT,BinaryOperator.MULTIPLY):
                if isinstance(instr.src1, Stack) and isinstance(instr.dest, Stack):
                    if operator in (BinaryOperator.ADD,BinaryOperator.SUBTRACT):
                        # Rewrite add/sub: move src1 to R10, perform add/sub with R10 and dest
                        mov_to_reg = Mov(src=instr.src1, dest=Reg(Registers.R10))
                        if operator == instr.operator:
                            binary_op = Binary(operator=instr.operator, src1=Reg(Registers.R10), src2=instr.dest)
                        else:
                            binary_op = Binary(operator=instr.operator, src1=Reg(Registers.R10), src2=instr.dest)
                        new_instructions.extend([mov_to_reg, binary_op])
                        logger.debug(f"Rewrote {operator} instruction with src1 and dest as Stack using R10.")
                    elif operator == BinaryOperator.MULTIPLY:
                        # Rewrite imul: move dest to R11, perform imul with src2 and R11, move back
                        mov_to_reg = Mov(src=instr.dest, dest=Reg(Registers.R11))
                        imul_op = Binary(operator=BinaryOperator.MULTIPLY, src1=Reg(Registers.R11), src2=instr.src2)
                        mov_back = Mov(src=Reg(Registers.R11), dest=instr.dest)
                        new_instructions.extend([mov_to_reg, imul_op, mov_back])
                        logger.debug(f"Rewrote imul instruction with dest as Stack using R11.")
                else:
                    # If not both src1 and dest are Stack, proceed normally
                    new_instructions.append(instr)
            else:
                logger.error(f"Unsupported binary operator: {instr.operator}")
                sys.exit(1)
        
        elif isinstance(instr, Idiv):
            # Handle Idiv Instructions
            operand = instr.operand
            if isinstance(operand, Imm):
                # Rewrite idiv with constant operand: move constant to R10, then idiv R10
                mov_to_reg = Mov(src=operand, dest=Reg(Registers.R10))
                idiv_op = Idiv(operand=Reg(Registers.R10))
                new_instructions.extend([mov_to_reg, idiv_op])
                logger.debug(f"Rewrote Idiv with constant operand by moving to R10 and performing Idiv.")
            elif isinstance(operand, Stack):
                # Rewrite idiv with Stack operand: move operand to R10, perform idiv, move back
                mov_to_reg = Mov(src=operand, dest=Reg(Registers.R10))
                idiv_op = Idiv(operand=Reg(Registers.R10))
                mov_back = Mov(src=Reg(Registers.R10), dest=operand)
                new_instructions.extend([mov_to_reg, idiv_op, mov_back])
                logger.debug(f"Rewrote Idiv with Stack operand by moving to R10, performing Idiv, and moving back.")
            else:
                # Operand is already a register; no replacement needed
                new_instructions.append(instr)
        
        elif isinstance(instr, AllocateStack) or isinstance(instr, Ret) or isinstance(instr,Cqd):
            # No Pseudos to replace; append as-is
            new_instructions.append(instr)
        
        else:
            # Unsupported instruction type; log the error and exit
            logger.error(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_func.name}'.")
            sys.exit(1)
    
    # Calculate total stack allocation required for all replaced pseudoregisters
    # Since current_offset starts at -4 and decrements by 4 for each new Pseudo,
    # the total allocation is abs(current_offset + 4)
    total_stack_allocation = abs(current_offset + 4)
    stack_allocations[assembly_func.name] = total_stack_allocation
    logger.debug(f"Total stack allocation for function '{assembly_func.name}': {total_stack_allocation} bytes.")
    
    return assembly_program, stack_allocations  # Return the modified AssemblyProgram and stack allocations
