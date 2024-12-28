from tacky import *
from assembly_ast import Mov, Ret, Imm, Registers, AssemblyFunction, AssemblyProgram, Reg, Unary, Pseudo , UnaryOperator ,Stack ,AllocateStack,Cqd,Idiv,Binary,BinaryOperator
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
        
    # Check if the current AST node is a TackyBinary operation
    elif isinstance(tacky_ast, TackyBinary):
        
        # Handle integer division operations
        if tacky_ast.operator == TackyBinaryOperator.DIVIDE:
            """
            Generate assembly instructions for integer division.
            
            Assembly Operations:
                1. Move the dividend (src1) into the AX register.
                2. Execute the CDQ instruction to sign-extend AX into DX:AX.
                3. Perform the IDIV operation using the divisor (src2).
                4. Move the quotient from AX to the destination (dst).
            
            This sequence follows the x86 assembly convention for signed integer division.
            """
            return [
                # Move the dividend to the AX register
                Mov(src=convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                
                # Convert Doubleword to Quadword: Sign-extend AX into DX:AX
                Cqd(),
                
                # Perform signed integer division: AX / src2
                Idiv(operand=convert_to_assembly_ast(tacky_ast.src2)),
                
                # Move the quotient from AX to the destination variable
                Mov(src=Reg(Registers.AX), dest=convert_to_assembly_ast(tacky_ast.dst))
            ]
        
        # Handle remainder operations resulting from integer division
        elif tacky_ast.operator == TackyBinaryOperator.REMAINDER:
            """
            Generate assembly instructions for computing the remainder after integer division.
            
            Assembly Operations:
                1. Move the dividend (src1) into the AX register.
                2. Execute the CDQ instruction to sign-extend AX into DX:AX.
                3. Perform the IDIV operation using the divisor (src2).
                4. Move the remainder from DX to the destination (dst).
            
            This sequence adheres to the x86 assembly convention where the remainder is stored in the DX register after division.
            """
            print(Registers.DX)
            return [
                # Move the dividend to the AX register
                Mov(src=convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                
                # Convert Doubleword to Quadword: Sign-extend AX into DX:AX
                Cqd(),
                
                # Perform signed integer division: AX / src2
                Idiv(operand=convert_to_assembly_ast(tacky_ast.src2)),
                
                # Move the remainder from DX to the destination variable
                Mov(src=Reg(Registers.DX), dest=convert_to_assembly_ast(tacky_ast.dst))
            ]
        
        # Handle addition, subtraction, and multiplication operations
        elif tacky_ast.operator in (
            TackyBinaryOperator.ADD,
            TackyBinaryOperator.SUBTRACT,
            TackyBinaryOperator.MULTIPLY
        ):
            """
            Generate assembly instructions for addition, subtraction, and multiplication.
            
            Assembly Operations:
                1. Move the first operand (src1) directly into the destination register.
                2. Perform the binary operation (ADD, SUBTRACT, MULTIPLY) between the second operand (src2) and the destination register.
            
            This approach optimizes instruction generation by utilizing the destination register to store intermediate results, reducing the need for additional temporary storage.
            """
            return [
                # Move the first operand directly into the destination register
                Mov(src=convert_to_assembly_ast(tacky_ast.src1), dest=convert_to_assembly_ast(tacky_ast.dst)),
                
                # Perform the binary operation with the second operand and store the result in the destination register
                Binary(
                    operator=convert_operator(tacky_ast.operator),
                    src1=convert_to_assembly_ast(tacky_ast.src2),
                    src2=convert_to_assembly_ast(tacky_ast.dst)
                )
            ]
    
        # Handle unsupported binary operators by raising an error
        else:
            """
            Error Handling:
                If the binary operator is not among the supported ones (DIVIDE, REMAINDER, ADD, SUBTRACT, MULTIPLY),
                the compiler raises a TypeError to indicate that the expression type is unsupported.
            """
            raise TypeError(f"Unsupported binary operator: {tacky_ast.operator}")

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
    Converts a Tacky unary or binary operator to its Assembly equivalent.
    
    Args:
        op (str): The operator from the Tacky AST. 
                  - For unary operators: 'Complement' or 'Negate'/'Negation'
                  - For binary operators: 'Add', 'Subtract', 'Multiply'
    
    Returns:
        str: A string representing the corresponding Assembly operator, as defined in the 
             UnaryOperator or BinaryOperator enums.
    
    Raises:
        ValueError: If the operator is unrecognized or not supported.
    """
    # Handle unary bitwise NOT operator
    if op == 'Complement':
        return UnaryOperator.NOT  # Corresponds to the bitwise NOT operation, e.g., '~x'
    
    # Handle unary arithmetic negation operators
    elif op in ('Negate', 'Negation'):
        return UnaryOperator.NEG  # Corresponds to the arithmetic negation operation, e.g., '-x'
    
    # Handle binary addition operator
    elif op == 'Add':
        return BinaryOperator.ADD  # Corresponds to the addition operation, e.g., 'x + y'
    
    # Handle binary subtraction operator
    elif op == 'Subtract':
        return BinaryOperator.SUBTRACT  # Corresponds to the subtraction operation, e.g., 'x - y'
    
    # Handle binary multiplication operator
    elif op == 'Multiply':
        return BinaryOperator.MULTIPLY  # Corresponds to the multiplication operation, e.g., 'x * y'
    
    # If the operator does not match any known unary or binary operators, raise an error
    else:
        # Raises a ValueError with a descriptive message indicating the unsupported operator
        raise ValueError(f"Unknown operator: {op}")








def fix_up_instructions(assembly_program: AssemblyProgram, stack_allocation: int) -> None:
    """
    Performs critical transformations on the Assembly AST to ensure valid and optimized
    instructions before emitting the final assembly program. Specifically, it handles:
    
    1. Inserting an AllocateStack instruction at the beginning of the function's instruction list.
    2. Rewriting invalid Mov instructions where both src and dest are Stack operands.
    3. Fixing up idiv, add, sub, and imul instructions according to assembly conventions.
    
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
    allocate_instr = AllocateStack(value=stack_allocation)
    assembly_function.instructions.insert(0, allocate_instr)
    # Debug Statement: Confirm insertion of AllocateStack
    print(f"Inserted AllocateStack({allocate_instr.value}) at the beginning of function '{assembly_function.name}'.")
    
    # Initialize a new list to hold the updated instructions after transformations
    new_instructions: List = []
    
    # Iterate over each instruction in the function's instruction list
    for instr in assembly_function.instructions:
        # Handle 'Mov' instructions which move data between operands
        if isinstance(instr, Mov):
            # Check if both src and dest are Stack operands, which is invalid in assembly
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
                print(f"Rewrote invalid Mov from {instr.src} to {instr.dest} using {Registers.R10}.")
            else:
                """
                Valid Mov Instruction:
                    At least one of src or dest is not a Stack operand.
                    No replacement needed; keep the instruction as-is.
                """
                new_instructions.append(instr)
        
        # Handle 'Idiv' instructions which perform integer division
        elif isinstance(instr, Idiv):
            # Check if the operand is a constant (immediate value) or a Stack operand
            
            if isinstance(instr.operand, Imm):
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
                print(f"Rewrote Idiv with constant operand {instr.operand} by moving to {Registers.R10} and performing Idiv.")
            elif isinstance(instr.operand, Stack):
                """
                Fixing Up 'idiv' with Stack Operands:
                    The 'idiv' instruction operates on registers, not directly on memory locations.
                    Therefore, we need to move the operand from the Stack to a temporary register before division.
                
                Transformation:
                    Original: idivl -4(%rbp)
                    Rewritten:
                        movl -4(%rbp), %r10d
                        idivl %r10d
                        movl %r10d, -4(%rbp)  # Optionally move the result back if needed
                """
                # Create a Mov from the Stack operand to R10 register
                mov_to_reg = Mov(src=instr.operand, dest=Reg(Registers.R10))
                # Create a new Idiv instruction using R10 register as the operand
                idiv_op = Idiv(operand=Reg(Registers.R10))
                # Optionally, move the result back to the original Stack location
                mov_back = Mov(src=Reg(Registers.R10), dest=instr.operand)
                
                # Append the transformed instructions to the new_instructions list
                new_instructions.extend([mov_to_reg, idiv_op, mov_back])
                
                # Debug Statement: Confirm rewriting of idiv with Stack operand
                print(f"Rewrote Idiv with Stack operand {instr.operand} by moving to {Registers.R10}, performing Idiv, and moving back the result.")
            
            else:
                """
                Idiv Instruction without Stack or Constant Operand:
                    Operand is already a register or another supported type.
                    No replacement needed; keep the instruction as-is.
                """
                new_instructions.append(instr)
        
        # Handle 'Binary' instructions which perform add, subtract, and multiply operations
        elif isinstance(instr, Binary):
            # Handle 'Add' and 'Subtract' instructions
            if instr.operator in (BinaryOperator.ADD.value, BinaryOperator.SUBTRACT.value):
                # Check if src1 (destination) is a Stack operand
                if isinstance(instr.src1, Stack):
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
                        src2=instr.src2
                    )
                    
                    # Append the transformed instructions to the new_instructions list
                    new_instructions.extend([mov_to_reg, binary_op])
                    
                    # Debug Statement: Confirm rewriting of add/sub instruction
                    print(f"Rewrote {instr.operator} from {instr.src1} to {instr.src2} using {Registers.R10}.")
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
                if isinstance(instr.src1, Stack):
                    """
                    Fixing Up 'imul' Instructions with Stack Destination:
                        The 'imul' instruction cannot have a memory address as its destination.
                        Therefore, we perform the multiplication in three steps using a temporary register (R11).
                    
                    Transformation:
                        Original: imull $3, -4(%rbp)
                        Rewritten:
                            movl -4(%rbp), %r11d
                            imull $3, %r11d
                            movl %r11d, -4(%rbp)
                    """
                    # Create a Mov from src1 Stack operand to R11 register
                    mov_to_reg = Mov(src=instr.src1, dest=Reg(Registers.R11))
                    # Create a new Binary operation (imul) using R11 as the source
                    imul_op = Binary(
                        operator=instr.operator,
                        src1=Reg(Registers.R11),
                        src2=instr.src2
                    )
                    # Create a Mov from R11 register back to src1 Stack operand
                    mov_back = Mov(src=Reg(Registers.R11), dest=instr.src1)
                    
                    # Append the transformed instructions to the new_instructions list
                    new_instructions.extend([mov_to_reg, imul_op, mov_back])
                    
                    # Debug Statement: Confirm rewriting of imul instruction
                    print(f"Rewrote imul for dest {instr.src1} using {Registers.R11}.")
                else:
                    """
                    Valid Multiply Instruction:
                        Destination (src1) is not a Stack operand.
                        No replacement needed; keep the instruction as-is.
                    """
                    new_instructions.append(instr)
            else:
                """
                Unsupported Binary Operator:
                    The binary operator is not among the supported ones (Add, Subtract, Multiply).
                    Raise an error or handle accordingly.
                """
                print(f"Unsupported binary operator: {instr.operator}")
                sys.exit(1)
        
        # Handle 'AllocateStack' instructions if necessary
        elif isinstance(instr, AllocateStack):
            """
            AllocateStack Instruction:
                Typically used to reserve space on the stack for local variables or temporaries.
                Since AllocateStack does not contain operands, no replacement is needed.
            """
            new_instructions.append(instr)
        
        # Handle 'Ret' (return) instructions which typically do not contain operands
        elif isinstance(instr, Ret):
            """
            Ret Instruction:
                Represents the return operation from a function.
                As it does not contain operands, no replacement is needed.
            """
            new_instructions.append(instr)
        
        # Handle any unsupported instruction types
        else:
            """
            Unsupported Instruction Type:
                If the instruction type is not recognized or handled above, log an error and exit.
                This ensures that all instruction types are accounted for and handled appropriately.
            """
            print(f"Unsupported instruction type: {type(instr)}")
            sys.exit(1)
    
    # Update the function's instruction list with the new instructions
    assembly_function.instructions = new_instructions
    # Debug Statement: Confirm completion of instruction fixes
    print(f"Completed fixing instructions for function '{assembly_function.name}'.")
