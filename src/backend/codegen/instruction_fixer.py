# instuction_fixer.py

from typing import List, Dict
from src.backend.codegen.assembly_ast import *
import sys 
import logging
from src.frontend.parser._ast5 import Double


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

count=0
def is_signed_32_bit(value: int) -> bool:
    """
    Checks if a given integer fits in a signed 32-bit integer.

    Args:
        value (int): The integer to check.

    Returns:
        bool: True if the value fits in signed 32 bits, False otherwise.
    """
    return -2**31 <= value <= 2**31 - 1
def round_up_to_multiple_of_16(value: int) :
    """
    Rounds up the given value to the nearest multiple of 16.
    
    Args:
        value (int): The value to round up.
    
    Returns:
        int: The rounded value.
    """
    return (value + 15) & ~0xF

def fix_up_instructions(assembly_program: AssemblyProgram, stack_allocation: int,symbols) -> None:
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
    assembly_functions: AssemblyFunction = assembly_program.function_definition
    # 1. Insert AllocateStack at the beginning of the instruction list
    for assembly_function in assembly_functions:
        
        # #stack_allocation)
        allocation = round_up_to_multiple_of_16(stack_allocation[assembly_function.name]+8)
        # #allocation)
        allocate_instr = AllocateStack(value=allocation)
        assembly_function.instructions.insert(0, allocate_instr)
        # #assembly_function.instructions)
    
        # logger.debug(f"Inserted AllocateStack({allocate_instr.value}) at the beginning of function '{assembly_function.name}'.")
        
        # Initialize a new list to hold the updated instructions after transformations
        new_instructions: List[Instruction] = []
        i=0
        # Iterate over each instruction in the function's instruction list
        if isinstance(assembly_function,AssemblyStaticVariable):
            pass
            # #assembly_function)
            
            # new_instructions=fix_instr(assembly_function.init,new_instructions,assembly_function)
            # #assembly_function.init)
            # assembly_function.init=new_instructions[0]
        elif isinstance(assembly_function,AssemblyFunction):
            # #assembly_function)
            for instr in assembly_function.instructions:
                # #instr)
                # Handle 'Mov' instructions which move data between operands
                new_instructions=fix_instr(instr,new_instructions)
                # #new_instructions)
            assembly_function.instructions = new_instructions
        # else:
            # print('Invalid func in ',assembly_function)
            # raise ValueError(f'Invalid func in {assembly_function}')
    
        # Debug Statement: Confirm completion of instruction fixes
        # logger.debug(f"Completed fixing instructions for function '{assembly_function.name}'.")
        


def fix_instr(instr,new_instructions:list):
    #instr)
    if isinstance(instr, Mov):
        # Handle large immediate values that need truncation
        if isinstance(instr.src, Imm):
            # If this is a long to int conversion (moving to a 32-bit register/memory)
            if instr._type == AssemblyType.longWord and int(instr.src.value) >= 2147483647 :
                #'here')
                # Properly truncate the value to 32 bits
                truncated_value = int(instr.src.value) & 0xFFFFFFFF
                # If value is too large for direct move, use intermediate register
                if truncated_value >= 2147483647 :
                    # First move to r10 as quadword
                    mov_to_reg = Mov(
                        assembly_type=AssemblyType.quadWord,
                        src=Imm(truncated_value),
                        dest=Reg(Registers.R10)
                    )
                    # Then move to destination as longword (32-bit) causing proper truncation
                    mov_to_dest = Mov(
                        assembly_type=AssemblyType.longWord,
                        src=Reg(Registers.R10),
                        dest=instr.dest
                    )
                    new_instructions.extend([mov_to_reg, mov_to_dest])
                else:
                    # Can move directly if value fits in 32 bits
                    new_mov = Mov(
                        assembly_type=AssemblyType.longWord,
                        src=Imm(truncated_value),
                        dest=instr.dest
                    )
                    new_instructions.append(new_mov)
                    
         
               
            elif ( isinstance(instr.src,Imm) and instr.src.value!='\0') and int(instr.src.value)>=2147483647  and isinstance(instr.dest,(Stack,Data,Memory)):
                Mov1=Mov(assembly_type=instr._type,src=instr.src,dest=Reg(Registers.R10))
                Mov2=Mov(assembly_type=instr._type,src=Reg(Registers.R10),dest=instr.dest)
                new_instructions.extend([Mov1,Mov2])
            
                
                
            
            else:
                
                if isinstance(instr.src, (Stack, Data)) and isinstance(instr.dest, (Stack, Data)):
                    mov_to_reg = Mov(
                        assembly_type=instr._type,
                        src=instr.src,
                        dest=Reg(Registers.R10)
                    )
                    mov_to_dest = Mov(
                        assembly_type=instr._type,
                        src=Reg(Registers.R10),
                        dest=instr.dest
                    )
                    new_instructions.extend([mov_to_reg, mov_to_dest])
                else:
                   
                    new_instructions.append(instr)
      
            
        else:
       
            # For other move operations maintain existing behavior
            if isinstance(instr.src, (Stack, Data,Memory)) and isinstance(instr.dest, (Stack, Data,Memory)):
                if instr._type == AssemblyType.double:
                    dest = Reg(Registers.XMM14)
                else:
                    dest=Reg(Registers.R10)
                    
                
                mov_to_reg = Mov(
                    assembly_type=instr._type,
                    src=instr.src,
                    dest=dest
                )
                mov_to_dest = Mov(
                    assembly_type=instr._type,
                    src=dest,
                    dest=instr.dest
                )
                new_instructions.extend([mov_to_reg, mov_to_dest])
            else:
                new_instructions.append(instr)
        

    # Handle 'Idiv' instructions which perform integer division
    elif isinstance(instr, (Idiv,Div)):
        # #instr)
        # exit()
        
        # #'in  idviv',instr)
        
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
            if isinstance(instr,Idiv):
            #     mov_to_reg = Mov(assembly_type=instr._type,src=instr.operand, dest=Reg(Registers.XMM15))
                idiv_op = Idiv(assembly_type=instr._type,operand=Reg(Registers.R10))
        
            #     idiv_op = Div(assembly_type=instr._type,operand=Reg(Registers.XMM15))
            else:
                idiv_op =Div(assembly_type=instr._type,operand=Reg(Registers.R10))
                
            mov_to_reg = Mov(assembly_type=instr._type,src=instr.operand, dest=Reg(Registers.R10))
                
            # Create a new Idiv instruction using R10 register as the operand
            mov_to_reg = Mov(assembly_type=instr._type,src=instr.operand, dest=Reg(Registers.R10))
            
            # Append the transformed instructions to the new_instructions list
            new_instructions.extend([mov_to_reg, idiv_op])
            
        
        else:
            #'here')
            new_instructions.append(instr)
            # print
            # exit()
            """
            Idiv Instruction without Stack or Constant Operand:
                Operand is already a register or another supported type.
                No replacement needed; keep the instruction as-is.
            """
    
    # Handle 'Binary' instructions which perform add, subtract, and multiply operations
    elif isinstance(instr, Binary):
        
        # #'in bin',instr)
        
        if instr.operator == BinaryOperator.XOR and not isinstance(instr.src2,Reg):
            mov = Mov(
                assembly_type=AssemblyType.double,
                src = instr.src2,
                dest= Reg(Registers.XMM15)
            )
            
            binary_op = Binary(
                assembly_type=AssemblyType.double,
                operator=BinaryOperator.XOR,
                src1=instr.src1,
                src2=Reg(Registers.XMM15)
            )
            mov_back = Mov(
                assembly_type=AssemblyType.double,
                src= Reg(Registers.XMM15),
                dest = instr.src2
            )
            new_instructions.extend([mov,binary_op, mov_back])
            
        
        # Handle 'Add' and 'Subtract' instructions
        elif instr.operator in (BinaryOperator.ADD, BinaryOperator.SUBTRACT):
            
            # Check if src1 (destination) is a Stack operand
            
            if instr._type==AssemblyType.double and not isinstance(instr.src2,Reg):
                movl = Mov(
                        assembly_type=AssemblyType.double,
                        src=instr.src2, 
                        dest=Reg(Registers.XMM15),
                    )
                op = Binary(
                assembly_type=AssemblyType.double,
                operator=instr.operator,
                src1=instr.src1,
                src2=Reg(Registers.XMM15)
                )
                
                mov_back = Mov(
                        assembly_type=AssemblyType.double,
                        dest=instr.src2, 
                        src=Reg(Registers.XMM15),
                    )
                new_instructions.extend([movl,op,mov_back])
                
                
            
            elif isinstance(instr.src1, (Stack,Data))  and isinstance(instr.src2,(Stack,Data)):
                
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
                
                
                
                mov_to_reg = Mov(assembly_type=instr._type,src=instr.src1, dest=Reg(Registers.R10))
                # Create a new Binary operation using R10 as the source and src2 as the original source2
                binary_op = Binary(
                    assembly_type=instr._type,
                    operator=instr.operator,
                    src1=Reg(Registers.R10),
                    src2=instr.src2,
                )
                # #mov_to_reg,binary_op)
            
                # Append the transformed instructions to the new_instructions list
                new_instructions.extend([mov_to_reg, binary_op])
                
                # Debug Statement: Confirm rewriting of add/sub instruction
                # logger.debug(f"Rewrote {instr.operator} from {instr.src2} to {instr.src1} using {Registers.R10}.")
            elif  isinstance(instr.src1,Imm) and int(instr.src1.value) >= 2147483647 and isinstance(instr.src2,Stack):
                    movl = Mov(
                        assembly_type=instr._type,
                        src=instr.src1, 
                        dest=Reg(Registers.R10),
                    )
                    binary_op = Binary(
                    assembly_type=instr._type,
                    operator=instr.operator,
                    src1=Reg(Registers.R10),
                    src2=instr.src2,
                    )   
                    new_instructions.extend([movl, binary_op])
            else:
                    # new_instructions.extend([movl, binary_op])
                    new_instructions.append(instr)
        
        # Handle 'Multiply' instructions
        elif instr.operator == BinaryOperator.MULTIPLY:
                # Check if src1 (destination) is a Stack operand
                # Create a Mov from src1 Stack operand to R11 register
                # Create a new Binary operation (imul) using R11 as the source
                if instr._type==AssemblyType.double :
                    #instr)
                    
                    if not isinstance(instr.src2,Reg): 
                        movl = Mov(
                                assembly_type=AssemblyType.double,
                                src=instr.src2, 
                                dest=Reg(Registers.XMM15),
                            )
                        op = Binary(
                        assembly_type=AssemblyType.double,
                        operator=instr.operator,
                        src1=instr.src1,
                        src2=Reg(Registers.XMM15)
                        )
                        mov_back = Mov(assembly_type=AssemblyType.double,src=Reg(Registers.XMM15), dest=instr.src2)
                        
                        new_instructions.extend([movl,op,mov_back])
                    else:
                        new_instructions.extend(instr)
                        
                        
                    
                
                elif isinstance(instr.src1,Imm) and int(instr.src1.value) >=2147483647 :
                    mov_to_reg = Mov(assembly_type=AssemblyType.quadWord,src=instr.src2, dest=Reg(Registers.R11))
                    movl = Mov(
                        assembly_type=AssemblyType.quadWord,
                        src=instr.src1, 
                        dest=Reg(Registers.R10),
                    )
                    imul_op = Binary(
                    assembly_type=AssemblyType.quadWord,
                    operator=instr.operator,
                    src1=Reg(Registers.R10),
                    src2=Reg(Registers.R11)
                    )
                    # Create a Mov from R11 register back to src1 Stack operand
                    mov_back = Mov(assembly_type=AssemblyType.quadWord,src=Reg(Registers.R11), dest=instr.src2)
                    
                    # Append the transformed instructions to the new_instructions list
                    new_instructions.extend([mov_to_reg,movl, imul_op, mov_back])
                     
                else:
                    mov_to_reg = Mov(assembly_type=instr._type,src=instr.src2, dest=Reg(Registers.R11))
                    imul_op = Binary(
                        assembly_type=instr._type,
                        operator=instr.operator,
                        src1=instr.src1,
                        src2=Reg(Registers.R11)
                    )
                    # Create a Mov from R11 register back to src1 Stack operand
                    mov_back = Mov(assembly_type=instr._type,src=Reg(Registers.R11), dest=instr.src2)
                    
                    # Append the transformed instructions to the new_instructions list
                    new_instructions.extend([mov_to_reg, imul_op, mov_back])
       
        elif instr.operator == BinaryOperator.DIVDOUBLE :
            if instr._type==AssemblyType.double and not isinstance(instr.src2,Reg):
                movl = Mov(
                        assembly_type=AssemblyType.double,
                        src=instr.src2, 
                        dest=Reg(Registers.XMM15),
                    )
                op = Binary(
                assembly_type=AssemblyType.double,
                operator=instr.operator,
                src1=instr.src1,
                src2=Reg(Registers.XMM15)
                )
                mov_back = Mov(
                        assembly_type=AssemblyType.double,
                        dest=instr.src2, 
                        src=Reg(Registers.XMM15),
                    )
                new_instructions.extend([movl,op,mov_back])
            else:
                new_instructions.append(instr)
        else:
                new_instructions.append(instr)

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
            mov_to_reg = Mov(assembly_type=instr._type,src=instr.operand, dest=Reg(Registers.R10))
            # Create a new Unary operation using R10 as the operand
            unary_op = Unary(
                assembly_type=instr._type,
                operator=instr.operator,
                operand=Reg(Registers.R10)
            )
            # Create a Mov from R10 register back to the Stack operand
            mov_back = Mov(
                assembly_type=instr._type,
                src=Reg(Registers.R10), dest=instr.operand)
            
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
        # #instr.value)
        # exit()
        
        new_instructions.append(Binary(operator=BinaryOperator.SUBTRACT,assembly_type=AssemblyType.quadWord,src1=Imm(instr.value),src2=Reg(Registers.SP)))
        #'in allocate')
        
        # global count
   
    elif isinstance(instr, Cmp):
       
   
        """
        AllocateStack Instruction:
            Typically used to reserve space on the stack for local variables or temporaries.
            Since AllocateStack does not contain operands, no replacement is needed.
        """
        # nonlocal count=
        # count+=1
        # #instr)
        # if count ==2:
        #     exit()
        if instr._type == AssemblyType.double and not isinstance(instr.operand2,Reg):
            #instr)
            # exit()
            mov = Mov(
                assembly_type=instr._type,
                src=instr.operand2, 
                dest=Reg(Registers.XMM14),
            )
            compl = Cmp(
                assembly_type=instr._type,
                operand1=instr.operand1,
                operand2=Reg(Registers.XMM14),
                )
            new_instructions.extend([mov,compl])
            
        elif isinstance(instr.operand1,(Stack,Data,Memory)) and isinstance(instr.operand2,(Data,Stack,Memory)):
            mov = Mov(
                assembly_type=instr._type,
                src=instr.operand1, 
                dest=Reg(Registers.R10),
            )
            compl = Cmp(
                assembly_type=instr._type,
                operand1=Reg(Registers.R10),
                operand2=instr.operand2)
            if not isinstance(compl.operand2,(Stack,Memory)):
                mov2 = Mov(
                    assembly_type=instr._type,
                    src=instr.operand2,
                    dest=Reg(Registers.R11)
            )
                compl2 = Cmp(
                    assembly_type=instr._type,
                    operand1=Reg(Registers.R10),
                    operand2=Reg(Registers.R11))
            
                new_instructions.extend([mov,mov2,compl2])
    
            else:
                # #'Skipped')
                # exit()
                
                new_instructions.extend([mov,compl])
        
        elif isinstance(instr.operand1,Imm):

                if instr._type == AssemblyType.double:
                    dest  = Reg(Registers.XMM15)
                    dest_1=Reg(Registers.XMM14)
                else:
                    dest=Reg(Registers.R10)
                    dest_1= Reg(Registers.R11)
                    
                
                movl = Mov(
                        assembly_type=instr._type,
                        src=instr.operand1, 
                        dest= dest,
                    )
                compl = Cmp(
                    assembly_type=instr._type,
                    operand1=dest,
                    operand2=instr.operand2,
                    )
                if not isinstance(compl.operand2,(Stack,Data,Memory)):
                    mov2 = Mov(
                        assembly_type=instr._type,
                        src=instr.operand2,
                        dest=dest_1
                )
                    compl2 = Cmp(
                        assembly_type=instr._type,
                        operand1=dest,
                        operand2=dest_1
                        )
            
                    new_instructions.extend([movl,mov2,compl2])
                else:
                    new_instructions.extend([movl,compl])
            
        elif not isinstance(instr.operand2,(Stack,Data,Memory)) and instr._type!= AssemblyType.double:

                if instr._type == AssemblyType.double:
                    dest = Reg(Registers.XMM15)
                else:
                    dest=Reg(Registers.R11)
                    
                movl = Mov(
                    assembly_type=instr._type,
                    src=instr.operand2, 
                    dest=dest,
                )
    
                compl = Cmp(
                    assembly_type=instr._type,
                    operand1=instr.operand1,
                    operand2=dest
                    )
            
                new_instructions.extend([movl,compl])
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
 
    elif isinstance(instr,Push):
        if instr._type==AssemblyType.double and isinstance(instr.operand,Reg):
            sub=Binary(operator=BinaryOperator.SUBTRACT,
                       assembly_type=AssemblyType.double,
                       src1=Imm(8),
                       src2=Reg(Registers.SP))
            mov = Mov(assembly_type=AssemblyType.double,
                      src=instr.operand,
                      dest=Reg(Registers.SP))
            
            new_instructions.extend([sub,mov])
        
        if isinstance(instr.operand,Imm) and int(instr.operand.value)>=2147483647:
            movl = Mov(
                    assembly_type=AssemblyType.quadWord,
                    src=instr.operand, 
                    dest=Reg(Registers.R11),
                )
            push=Push(operand=Reg(Registers.R11),_type=AssemblyType.quadWord)
            new_instructions.extend([movl,push])
        else:
            
            new_instructions.append(instr)
    # Handle 'Cdq' (Convert Quadword to Doubleword) instructions
    elif isinstance(instr, (Cdq,JmpCC,Jmp,Label,SetCC,Call,DeallocateStack,Imm)):
        """
        Cdq Instruction:
            Sign-extends the AX register into the DX:AX register pair.
            Typically used before division operations.
            No operand replacement needed as it operates on fixed registers.
        """
        new_instructions.append(instr)
    elif isinstance(instr,MovZeroExtend):
        if instr.assembly_type_src == AssemblyType.byte and (isinstance(instr.src, Imm) or not isinstance(instr.dest, Reg)):
            # Step 1: Move immediate to temporary register if source is immediate
            if isinstance(instr.src, Imm):
                # Handle byte overflow if needed
                if isinstance(instr.src.value, int) and instr.src.value > 255:
                    fixed_value = instr.src.value % 256
                    mov1 = Mov(
                        assembly_type=AssemblyType.byte,
                        src=Imm(fixed_value),
                        dest=Reg(Registers.R10))
                else:
                    mov1 = Mov(
                        assembly_type=AssemblyType.byte,
                        src=instr.src,
                        dest=Reg(Registers.R10))
                new_instructions.append(mov1)
                actual_src = Reg(Registers.R10)
            else:
                actual_src = instr.src
            
            # Step 2: Perform the zero extension to temporary register
            movz = MovZeroExtend(
                assembly_type_src=AssemblyType.byte,
                assembly_type_dst=instr.assembly_type_dst,
                src=actual_src,
                dest=Reg(Registers.R11))
            new_instructions.append(movz)
            
            # Step 3: Move result to final destination if not register
            if not isinstance(instr.dest, Reg):
                mov_final = Mov(
                    assembly_type=instr.assembly_type_dst,#! fghwaeuyfghkuiaserhkgufi
                    src=Reg(Registers.R11),
                    dest=instr.dest)
                new_instructions.append(mov_final)
        
        # Case 2: Source is longword - replace with mov instructions
            elif instr.assembly_type_src == AssemblyType.longWord:
                if isinstance(instr.dest, Reg):
                    new_instructions.append(
                        Mov(
                            assembly_type=AssemblyType.longWord,
                            src=instr.src,
                            dest=instr.dest
                        )
                    )
                elif isinstance(instr.dest, (Stack, Memory)):
                    mov1 = Mov(
                        assembly_type=AssemblyType.longWord,
                        src=instr.src,
                        dest=Reg(Registers.R11))
                    mov2 = Mov(
                        assembly_type=AssemblyType.longWord,
                        src=Reg(Registers.R11),
                        dest=instr.dest)
                    new_instructions.extend([mov1, mov2])
            
       
        elif isinstance(instr.dest,Reg):
            new_instructions.append(
                Mov(
                    assembly_type=instr.assembly_type_src,
                    src=instr.src,
                    dest=instr.dest
                )
            ) 
        elif isinstance(instr.dest,Stack)  or isinstance(instr.dest,Memory):
            mov = Mov(
                assembly_type=AssemblyType.longWord,
                src=instr.src,
                dest=Reg(Registers.R11)
            )
            mov2=Mov(
                assembly_type=AssemblyType.quadWord,
                src=Reg(Registers.R11),
                dest=instr.dest
            )
            new_instructions.extend([mov,mov2])
        else:
            new_instructions.append(instr)
    elif isinstance(instr,Movsx):
        if isinstance(instr.dest,Stack) and isinstance(instr.src,Imm):
            mov = Mov(
                assembly_type=instr.assembly_type_src,
                src=instr.src,
                dest=Reg(Registers.R10),
            )
            movsx=Movsx(
                assembly_type_src=instr.assembly_type_src,
                assembly_type_dst=instr.assembly_type_dst,
                src=Reg(Registers.R10),
                dest=Reg(Registers.R11)
            )
            mov2=Mov(
                assembly_type=instr.assembly_type_dst,
                src=Reg(Registers.R11),
                dest=instr.dest
            )
            new_instructions.extend([mov,movsx,mov2])
        elif isinstance(instr.src,Imm):
            mov = Mov(
                assembly_type=instr.assembly_type_src,
                src=instr.src,
                dest=Reg(Registers.R10),
            )
            movsx=Movsx(
                 assembly_type_src=instr.assembly_type_src,
                assembly_type_dst=instr.assembly_type_dst,
                src=Reg(Registers.R10),
                dest=instr.dest
            )
            new_instructions.extend([mov,movsx])
        elif isinstance(instr.dest,Stack):
            movsx=Movsx(
                 assembly_type_src=instr.assembly_type_src,
                assembly_type_dst=instr.assembly_type_dst,
                src=instr.src,
                dest=Reg(Registers.R11)
            )
            mov2=Mov(
                assembly_type=instr.assembly_type_dst, #! MAJOR CHANGE
                src=Reg(Registers.R11),
                dest=instr.dest
            )
            
            new_instructions.extend([movsx,mov2])
        else:
            new_instructions.append(instr)
    elif isinstance(instr,Cvttsd2si):
        #instr)
        if not isinstance(instr.dst,Reg):
            # exit()
            # if instr._type == AssemblyType.byte:
                # exit()
            c_1=Cvttsd2si(
                dst_type=instr._type,
                src=instr.src,
                dst=Reg(Registers.R11)
                
            )
            m_1= Mov(
                assembly_type=instr._type,
                src=Reg(Registers.R11),
                dest=instr.dst
            )
            new_instructions.extend([c_1,m_1])
        else:
            new_instructions.append(instr)
    elif isinstance(instr,Cvtsi2sd):
    
        if isinstance(instr.src,Imm) and not isinstance(instr.dst,Reg):
            m_0= Mov(
                assembly_type=instr._type,
                src=instr.src,
                dest=Reg(Registers.R10)
            )
            c_1=Cvtsi2sd(
                src_type=instr._type,
                src=Reg(Registers.R10),
                dst=Reg(Registers.XMM15),
                
            )
            m_1= Mov(
                assembly_type=AssemblyType.double,
                src=Reg(Registers.XMM15),
                dest=instr.dst
            )
            new_instructions.extend([m_0,c_1,m_1])
            
        elif isinstance(instr.src,Imm):
            m_0= Mov(
                assembly_type=instr._type,
                src=instr.src,
                dest=Reg(Registers.R10)
            )
            c_1=Cvtsi2sd(
                src_type=instr._type,
                src=Reg(Registers.R10),
                dst=instr.dst,
                
            )
            new_instructions.extend([m_0,c_1])
        elif not isinstance(instr.dst,Reg):
            c_1=Cvtsi2sd(
                src_type=instr._type,
                src=instr.src,
                dst=Reg(Registers.XMM15)
                
            )
            m_1= Mov(
                assembly_type=AssemblyType.double,
                src=Reg(Registers.XMM15),
                dest=instr.dst
            )
            
            new_instructions.extend([c_1,m_1])
        else:
            new_instructions.append(instr)
    elif isinstance(instr,Lea):
        if not isinstance(instr.dst,Reg):
            lea=Lea(
                dst=Reg(Registers.R10),
                src=instr.src,
                _type = instr._type
                
            )
            mv_back = Mov(
                assembly_type=AssemblyType.quadWord,
                dest = instr.dst,
                src=Reg(Registers.R10)
            )
            new_instructions.extend([lea,mv_back])
        else:
            new_instructions.append(instr)
    # Handle any unsupported instruction types
    else:
        """
        Unsupported Instruction Type:
            If the instruction type is not recognized or handled above, log an error and exit.
            This ensures that all instruction types are accounted for and handled appropriately.
        """
        logger.error(f"Unsupported instruction type: {type(instr).__name__} in function' ")
        sys.exit(1)
    return new_instructions



