# instruction_fixer.py

from typing import List, Dict
from assembly_ast import *
import sys 
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def fix_up_instructions(assembly_program: AssemblyProgram, stack_allocation: int) -> None:
    """
    Performs critical transformations on the Assembly AST to ensure valid and optimized
    instructions before emitting the final assembly program. Specifically, it handles:
    
    1. Inserting an AllocateStack instruction at the beginning of the function's instruction list.
    2. Rewriting invalid Mov instructions where both src and dest are Stack operands.
    3. Fixing up idiv, add, sub, imul, and unary instructions according to assembly conventions.
    
    These transformations ensure that the generated assembly adheres to correct syntax and
    operational semantics, facilitating accurate execution of arithmetic operations.
    
    Args:
        assembly_program (AssemblyProgram): The AssemblyProgram AST to process.
        stack_allocation (int): The total stack space required based on allocated temporaries.
    
    Returns:
        None. The function modifies the assembly_program in place.
    """
    # Access the single AssemblyFunction within the AssemblyProgram
    # Assumes that the program contains exactly one function. If multiple functions are present,
    # additional handling would be required.
    assembly_function: AssemblyFunction = assembly_program.function_definition
    # 1. Insert AllocateStack at the beginning of the instruction list
    allocate_instr = AllocateStack(value=stack_allocation[assembly_function.name])
    assembly_function.instructions.insert(0, allocate_instr)
    print(assembly_function.instructions)
   
    # logger.debug(f"Inserted AllocateStack({allocate_instr.value}) at the beginning of function '{assembly_function.name}'.")
    
    # Initialize a new list to hold the updated instructions after transformations
    new_instructions: List[Instruction] = []
    i=0
    # Iterate over each instruction in the function's instruction list
    for instr in assembly_function.instructions:
        i=i+1
        # Handle 'Mov' instructions which move data between operands
        if isinstance(instr, Mov):
            print('in mov',instr)
            
            # print(instr.dest, instr.src)
            # Check if both src and dest are Stack operands
            if isinstance(instr.src, Stack) and isinstance(instr.dest, Stack):
                """
                Invalid Mov Instruction:
                    Both source and destination are Stack operands, which is not allowed in assembly.
                    You cannot move data directly from one memory location to another without using a register.
                
                Fix:
                    Introduce a temporary register (R10) to hold the data during the move.
                    Steps:
                        a. Move the data from src Stack to R10.
                        b. Move the data from R10 to dest Stack.
                """
                # Create a Mov from src Stack to R10 register
                mov_to_reg = Mov(src=instr.src, dest=Reg(Registers.R10))
                # Create a Mov from R10 register to dest Stack
                mov_to_dest = Mov(src=Reg(Registers.R10), dest=instr.dest)
                
                # Append the two new Mov instructions to the new_instructions list
                new_instructions.extend([mov_to_reg, mov_to_dest])
                
                # Debug Statement: Confirm rewriting of invalid Mov instruction
                # logger.debug(f"Rewrote invalid Mov from {instr.src} to {instr.dest} using {Registers.R10}.")
            else:
                """
                Valid Mov Instruction:
                    At least one of src or dest is not a Stack operand.
                    No replacement needed; keep the instruction as-is.
                """
                new_instructions.append(instr)
        
        # Handle 'Idiv' instructions which perform integer division
        elif isinstance(instr, Idiv):
            print('in  idviv',instr)
            
            # Check if the operand is a constant (immediate value) or a Stack operand
            
            if isinstance(instr.operand, Imm) :
                """
                Fixing Up 'idiv' with Constant Operands:
                    The 'idiv' instruction cannot directly operate on immediate (constant) values.
                    Therefore, we need to move the constant into a temporary register before performing the division.
                
                Transformation:
                    Original: idivl $3
                    Rewritten:
                        movl $3, %r10d
                        idivl %r10d
                """
                # Create a Mov from the constant operand to R10 register
                mov_to_reg = Mov(src=instr.operand, dest=Reg(Registers.R10))
                # Create a new Idiv instruction using R10 register as the operand
                idiv_op = Idiv(operand=Reg(Registers.R10))
                
                # Append the transformed instructions to the new_instructions list
                new_instructions.extend([mov_to_reg, idiv_op])
                
                # Debug Statement: Confirm rewriting of idiv with constant operand
                # logger.debug(f"Rewrote Idiv with constant operand {instr.operand} by moving to {Registers.R10} and performing Idiv.")
            # elif isinstance(instr.operand, Stack):
            #     """
            #     Fixing Up 'idiv' with Stack Operands:
            #         The 'idiv' instruction operates on registers, not directly on memory locations.
            #         Therefore, we need to move the operand from the Stack to a temporary register before division.
                
            #     Transformation:
            #         Original: idivl -4(%rbp)
            #         Rewritten:
            #             movl -4(%rbp), %r10d
            #             idivl %r10d
            #             movl %r10d, -4(%rbp)  # Optionally move the result back if needed
            #     """
            #     # Create a Mov from the Stack operand to R10 register
            #     mov_to_reg = Mov(src=instr.operand, dest=Reg(Registers.R10))
            #     # Create a new Idiv instruction using R10 register as the operand
            #     idiv_op = Idiv(operand=Reg(Registers.R10))
            #     # Optionally, move the result back to the original Stack location
            #     mov_back = Mov(src=Reg(Registers.R10), dest=instr.operand)
                
            #     # Append the transformed instructions to the new_instructions list
            #     new_instructions.extend([mov_to_reg, idiv_op, mov_back])
                
                # Debug Statement: Confirm rewriting of idiv with Stack operand
                # logger.debug(f"Rewrote Idiv with Stack operand {instr.operand} by moving to {Registers.R10}, performing Idiv, and moving back the result.")
            
            else:
                """
                Idiv Instruction without Stack or Constant Operand:
                    Operand is already a register or another supported type.
                    No replacement needed; keep the instruction as-is.
                """
                new_instructions.append(instr)
        
        # Handle 'Binary' instructions which perform add, subtract, and multiply operations
        elif isinstance(instr, Binary):
            print('in bin',instr)
            
            # Handle 'Add' and 'Subtract' instructions
            if instr.operator in (BinaryOperator.ADD, BinaryOperator.SUBTRACT):
                print('in add',instr)
                
                # Check if src1 (destination) is a Stack operand
                # print(instr)
                if isinstance(instr.src1, Stack)  and isinstance(instr.src2,Stack):
                
                    """
                    Fixing Up 'add' and 'sub' Instructions with Stack Destination:
                        The 'add' and 'sub' instructions cannot have a memory address as both source and destination.
                        Therefore, if src1 is a Stack operand, we perform the operation in two steps using a temporary register (R10).
                    
                    Transformation:
                        Original: addl -4(%rbp), -8(%rbp)
                        Rewritten:
                            movl -4(%rbp), %r10d
                            addl %r10d, -8(%rbp)
                    """
                    # Create a Mov from src1 Stack operand to R10 register
                    mov_to_reg = Mov(src=instr.src1, dest=Reg(Registers.R10))
                    # Create a new Binary operation using R10 as the source and src2 as the original source2
                    binary_op = Binary(
                        operator=instr.operator,
                        src1=Reg(Registers.R10),
                        src2=instr.src2,
                    )
                    # print(mov_to_reg,binary_op)
                
                    # Append the transformed instructions to the new_instructions list
                    new_instructions.extend([mov_to_reg, binary_op])
                    
                    # Debug Statement: Confirm rewriting of add/sub instruction
                    # logger.debug(f"Rewrote {instr.operator} from {instr.src2} to {instr.src1} using {Registers.R10}.")
                else:
                    """
                    Valid Add/Sub Instruction:
                        Destination (src1) is not a Stack operand.
                        No replacement needed; keep the instruction as-is.
                    """
                    new_instructions.append(instr)
            
            # Handle 'Multiply' instructions
            elif instr.operator == BinaryOperator.MULTIPLY:

                
                # Check if src1 (destination) is a Stack operand
                 # Create a Mov from src1 Stack operand to R11 register
                    mov_to_reg = Mov(src=instr.src2, dest=Reg(Registers.R11))
                    # Create a new Binary operation (imul) using R11 as the source
                    imul_op = Binary(
                        operator=instr.operator,
                        src1=instr.src1,
                        src2=Reg(Registers.R11)
                    )
                    # Create a Mov from R11 register back to src1 Stack operand
                    mov_back = Mov(src=Reg(Registers.R11), dest=instr.src2)
                    
                    # Append the transformed instructions to the new_instructions list
                    new_instructions.extend([mov_to_reg, imul_op, mov_back])
            #     if isinstance(instr.src1, Stack):
            #         """
            #         Fixing Up 'imul' Instructions with Stack Destination:
            #             The 'imul' instruction cannot have a memory address as its destination.
            #             Therefore, we perform the multiplication in three steps using a temporary register (R11).
                    
            #         Transformation:
            #             Original: imull $3, -4(%rbp)
            #             Rewritten:
            #                 movl -4(%rbp), %r11d
            #                 imull $3, %r11d
            #                 movl %r11d, -4(%rbp)
            #         """
            #         # Create a Mov from src1 Stack operand to R11 register
            #         mov_to_reg = Mov(src=instr.src1, dest=Reg(Registers.R11))
            #         # Create a new Binary operation (imul) using R11 as the source
            #         imul_op = Binary(
            #             operator=instr.operator,
            #             src1=Reg(Registers.R11),
            #             src2=instr.src2
            #         )
            #         # Create a Mov from R11 register back to src1 Stack operand
            #         mov_back = Mov(src=Reg(Registers.R11), dest=instr.src1)
                    
            #         # Append the transformed instructions to the new_instructions list
            #         new_instructions.extend([mov_to_reg, imul_op, mov_back])
                    
            #         # Debug Statement: Confirm rewriting of imul instruction
            #         # logger.debug(f"Rewrote {instr.operator} for dest {instr.src1} using {Registers.R11}.")
            #     else:
            #         """
            #         Valid Multiply Instruction:
            #             Destination (src1) is not a Stack operand.
            #             No replacement needed; keep the instruction as-is.
            #         """
            #         new_instructions.append(instr)
            # else:
            #     """
            #     Unsupported Binary Operator:
            #         The binary operator is not among the supported ones (Add, Subtract, Multiply).
            #         Raise an error or handle accordingly.
            #     """
            #     # logger.error(f"Unsupported binary operator: {instr.operator}")
            #     sys.exit(1)
        
        # Handle 'Unary' instructions which perform operations on a single operand
        elif isinstance(instr, Unary):
            # Check if the operand is a Stack operand
            if isinstance(instr.operand, Stack):
                """
                Fixing Up 'Unary' Instructions with Stack Operand:
                    The 'Unary' instruction operates on a memory location, which is not allowed in some assembly syntaxes.
                    Therefore, we need to move the operand from the Stack to a temporary register, perform the Unary operation,
                    and then move the result back to the Stack location.
                
                Transformation:
                    Original: notl -4(%rbp)
                    Rewritten:
                        movl -4(%rbp), %r10d
                        notl %r10d
                        movl %r10d, -4(%rbp)
                """
                # Create a Mov from the Stack operand to R10 register
                mov_to_reg = Mov(src=instr.operand, dest=Reg(Registers.R10))
                # Create a new Unary operation using R10 as the operand
                unary_op = Unary(
                    operator=instr.operator,
                    operand=Reg(Registers.R10)
                )
                # Create a Mov from R10 register back to the Stack operand
                mov_back = Mov(src=Reg(Registers.R10), dest=instr.operand)
                
                # Append the transformed instructions to the new_instructions list
                new_instructions.extend([mov_to_reg, unary_op, mov_back])
                
                # Debug Statement: Confirm rewriting of Unary instruction
                # logger.debug(f"Rewrote {instr.operator} on {instr.operand} using {Registers.R10}.")
            else:
                """
                Valid Unary Instruction:
                    Operand is not a Stack operand.
                    No replacement needed; keep the instruction as-is.
                """
                new_instructions.append(instr)
        
        # Handle 'AllocateStack' instructions if necessary
        elif isinstance(instr, AllocateStack):
            """
            AllocateStack Instruction:
                Typically used to reserve space on the stack for local variables or temporaries.
                Since AllocateStack does not contain operands, no replacement is needed.
            """
            new_instructions.append(instr)
            
        elif isinstance(instr, Cmp):
            """
            AllocateStack Instruction:
                Typically used to reserve space on the stack for local variables or temporaries.
                Since AllocateStack does not contain operands, no replacement is needed.
            """
            if isinstance(instr.operand1,Stack) and isinstance(instr.operand2,Stack):
                mov = Mov(
                    src=instr.operand1, dest=Reg(Registers.R10),
                )
                compl = Cmp(operand1=Reg(Registers.R10),operand2=instr.operand2)
                if not isinstance(compl.operand2,Stack):
                    mov2 = Mov(
                    src=instr.operand2, dest=Reg(Registers.R11),
                )
                    compl2 = Cmp(operand1=instr.operand1,operand2=Reg(Registers.R11))
                
                    new_instructions.append([mov,mov2,compl2])
        
                else:
                        new_instructions.append([mov,compl])
            else:
                new_instructions.append(instr)
        
        # Handle 'Ret' (return) instructions which typically do not contain operands
        elif isinstance(instr, Ret):
            """
            Ret Instruction:
                Represents the return operation from a function.
                As it does not contain operands, no replacement is needed.
            """
            new_instructions.append(instr)
        
        # Handle 'Cdq' (Convert Quadword to Doubleword) instructions
        elif isinstance(instr, (Cdq,JmpCC,Jmp,Label)):
            """
            Cdq Instruction:
                Sign-extends the AX register into the DX:AX register pair.
                Typically used before division operations.
                No operand replacement needed as it operates on fixed registers.
            """
            new_instructions.append(instr)
        
        # Handle any unsupported instruction types
        else:
            """
            Unsupported Instruction Type:
                If the instruction type is not recognized or handled above, log an error and exit.
                This ensures that all instruction types are accounted for and handled appropriately.
            """
            logger.error(f"Unsupported instruction type: {type(instr).__name__} in function '{assembly_function.name}'.")
            sys.exit(1)
    # print(new_instructions)
    # Update the function's instruction list with the new instructions
    assembly_function.instructions = new_instructions
    # Debug Statement: Confirm completion of instruction fixes
    # logger.debug(f"Completed fixing instructions for function '{assembly_function.name}'.")
