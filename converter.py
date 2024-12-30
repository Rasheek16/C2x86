from tacky import *
from assembly_ast import *
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
            name=tacky_ast.name.name,  # Assuming tacky_ast.name is an Identifier
            instructions=instructions
        )
    
    # Handle Return instruction
    elif isinstance(tacky_ast, TackyReturn):
        # print(tacky_ast.val)
        # mov_instr = 
        return [
            Mov(src=convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.AX)),
            Ret()
        ]
    
    # Handle Unary instruction
    elif isinstance(tacky_ast, TackyUnary):        
        # Convert a Unary operation by moving src to dst and applying the operator
        if tacky_ast.operator ==TackyUnaryOperator.NOT:
            print('inside not')
            return [
                Cmp(operand1=Imm(0),operand2=convert_to_assembly_ast(tacky_ast.src)),
                Mov(src=Imm(0),dest=convert_to_assembly_ast(tacky_ast.dst)),
                SetCC(Cond_code=Cond_code.E,operand=convert_to_assembly_ast(tacky_ast.dst))
            ]
        else:
            return [
                Mov(src=convert_to_assembly_ast(tacky_ast.src), dest=convert_to_assembly_ast(tacky_ast.dst)),
                Unary(operator=convert_operator(tacky_ast.operator), operand=convert_to_assembly_ast(tacky_ast.dst))
            ]
        
    # Check if the current AST node is a TackyBinary operation
    elif isinstance(tacky_ast, TackyBinary):
        # print(tacky_ast.operator)
        # print('Binary operations')
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
                Cdq(),
                
                # Perform signed integer division: AX / src2
                Idiv(operand=convert_to_assembly_ast(tacky_ast.src2)),
                
                # Move the quotient from AX to the destination variable
                Mov(src=Reg(Registers.AX), dest=convert_to_assembly_ast(tacky_ast.dst))
            ]
        
        # Handle remainder operations resulting from integer division
        elif tacky_ast.operator == TackyBinaryOperator.REMAINDER:
            # print('Inside remainder')
            # print('Inside ')
            """
            Generate assembly instructions for computing the remainder after integer division.
            
            Assembly Operations:
                1. Move the dividend (src1) into the AX register.
                2. Execute the CDQ instruction to sign-extend AX into DX:AX.
                3. Perform the IDIV operation using the divisor (src2).
                4. Move the remainder from DX to the destination (dst).
            
            This sequence adheres to the x86 assembly convention where the remainder is stored in the DX register after division.
            """
            return [
                # Move the dividend to the AX register
                Mov(src=convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                
                # Convert Doubleword to Quadword: Sign-extend AX into DX:AX
                Cdq(),
                
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
            # if tacky_ast.operator == TackyBinaryOperator.MULTIPLY:
            #     return [
            #     # Move the first operand directly into the destination register
            #     Mov(src=convert_to_assembly_ast(tacky_ast.src1), dest=convert_to_assembly_ast(tacky_ast.dst)),
                
            #     # Perform the binary operation with the second operand and store the result in the destination register
            #     Binary(
            #         operator=convert_operator(tacky_ast.operator),
            #         src2=convert_to_assembly_ast(tacky_ast.src2),
            #         src1=convert_to_assembly_ast(tacky_ast.dst)
            #     ),
            #     # Mov(src=convert_to_assembly_ast(tacky_ast.dst), dest=Reg(Registers.AX))
            # ]
    
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
                ),
                # Mov(src=convert_to_assembly_ast(tacky_ast.dst), dest=Reg(Registers.AX))
            ]
    
        # Handle unsupported binary operators by raising an error
        elif tacky_ast.operator in (TackyBinaryOperator.GREATER_OR_EQUAL,TackyBinaryOperator.LESS_OR_EQUAL,TackyBinaryOperator.LESS_THAN,TackyBinaryOperator.NOT_EQUAL,TackyBinaryOperator.EQUAL,TackyBinaryOperator.OR,TackyBinaryOperator.AND):
            return [Cmp(operand1=convert_to_assembly_ast(tacky_ast.src2),operand2=convert_to_assembly_ast(tacky_ast.src1)),
                    Mov(src=Imm(0),dest=convert_to_assembly_ast(tacky_ast.dst)),
                    SetCC(Cond_code=convert_operator(tacky_ast.operator),operand=convert_to_assembly_ast(tacky_ast.dst))
                    ]
        elif tacky_ast.operator == TackyBinaryOperator.GREATER_THAN:
            return [Cmp(operand1=convert_to_assembly_ast(tacky_ast.src2),operand2=convert_to_assembly_ast(tacky_ast.src1)),
                    Mov(src=Imm(0),dest=convert_to_assembly_ast(tacky_ast.dst)),
                    SetCC(Cond_code=Cond_code.G,operand=convert_to_assembly_ast(tacky_ast.dst))
                    ]
        else:
            """
            Error Handling:
                If the binary operator is not among the supported ones (DIVIDE, REMAINDER, ADD, SUBTRACT, MULTIPLY),
                the compiler raises a TypeError to indicate that the expression type is unsupported.
            """
            raise TypeError(f"Unsupported binary operator: {tacky_ast.operator}")
    elif isinstance(tacky_ast,str):
        return tacky_ast
    # Handle Constant operand
    elif isinstance(tacky_ast, TackyConstant):
        # Convert a constant value into an Imm operand
        return Imm(tacky_ast.value)
    
    # Handle Variable operand
    elif isinstance(tacky_ast, TackyVar):
        # Convert a variable into a Pseudo operand
        # print(tacky_ast)
        return Pseudo(tacky_ast.identifier)
    elif isinstance(tacky_ast,TackyJump):
        return [Jmp(indentifier=tacky_ast.target)]
    elif isinstance(tacky_ast,TackyJumpIfZero):
        return [
            Cmp(operand1=Imm(0),operand2=convert_to_assembly_ast(tacky_ast.condition)),
            JmpCC(Cond_code=Cond_code.E,indentifier=convert_to_assembly_ast(tacky_ast.target))
        ]
    elif isinstance(tacky_ast,TackyJumpIfNotZero):
        return [
            Cmp(operand1=Imm(0),operand2=convert_to_assembly_ast(tacky_ast.condition)),
            JmpCC(Cond_code=Cond_code.NE,indentifier=convert_to_assembly_ast(tacky_ast.target))
        ]
        
    elif isinstance(tacky_ast,TackyCopy):
        return [
            Mov(src=convert_to_assembly_ast(tacky_ast.src),dest=convert_to_assembly_ast(tacky_ast.dst))
        ]
    elif isinstance(tacky_ast,TackyLabel):
        return [
            Label(indentifier=convert_to_assembly_ast(tacky_ast.identifer))
        ]
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
    
    elif op=='GreaterThan':
        return Cond_code.G
    elif op=='LessThan':
        return Cond_code.L
    elif op=='GreaterOrEqual':
        return Cond_code.GE
    elif op=='LessOrEqual':
        return Cond_code.LE
    elif op=='NotEqual':
        return Cond_code.NE
    elif op=='Equal':
        return Cond_code.E
    # If the operator does not match any known unary or binary operators, raise an error
    else:
        # Raises a ValueError with a descriptive message indicating the unsupported operator
        raise ValueError(f"Unknown operator: {op}")







