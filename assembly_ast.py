# ---------------------------------------------------------------------------
# Grammar Recap:
#
#program = Program(function_definition)
#
#function_definition = Function(identifier name, instruction* instructions)
#
#instruction = Mov(operand src, operand dst)
#             | Unary(unary_operator, operand)
#             | AllocateStack(int)
#             | Ret
#
#unary_operator = Neg | Not
#
#operand = Imm(int) | Reg(reg) | Pseudo(identifier) | Stack(int)
#
#reg = AX | R10
#
# ---------------------------------------------------------------------------
from enum import Enum
from typing import List,Optional


# ------------------
# Operand and subclasses
# ------------------



class AssemblyType:
    longWord='LongWord'
    quadWord='QuadWord' 
    double='Double'
    
    


class Operand:
    """
    Base class for ASM operands (e.g., immediate values, registers).
    """
    pass


class Imm(Operand):
    """
    An immediate value, e.g. '10' or '0x3F'.
    (Grammar: Imm(int))
    """
    def __init__(self, value):
        # Per grammar, this could be an int or a string representing an int.
        self.value = value

    def __repr__(self):
        return f"Imm({self.value})"


class Pseudo(Operand):
    """
    A pseudo identifier (Grammar: Pseudo(identifier)).
    """
    def __init__(self, name):
        self.identifier = name

    def __repr__(self):
        return f"Pseudo(identifier={self.identifier})"


class Stack(Operand):
    """
    A stack-based operand, e.g., allocating memory or referencing stack offsets.
    (Grammar: Stack(int))
    """
    def __init__(self, value: int):
        self.value = value

    def __repr__(self):
        return f"Stack(value={self.value})"


class Reg(Operand):
    """
    Represents a CPU register operand (Grammar: Reg(reg)).
    Only AX, R10, R11, DX are allowed, per grammar.
    """
    def __init__(self, value):
        # We check against the valid enumerations in 'Registers'
        # if value not in (Registers.AX, Registers.R10,Registers.DX,Registers.R11,Registers.R8,Registers.R9,Registers.CX,Registers.DI,Registers.SI,Registers.SP):
        #     raise TypeError(f"Invalid register value: {value}")
        self.value = value

    def __repr__(self):
        return f"Reg({self.value})"
    
class Data(Operand):
    """
    A pseudo identifier (Grammar: Pseudo(identifier)).
    """
    def __init__(self, name):
        self.identifier = name

    def __repr__(self):
        return f"Data(identifier={self.identifier})"

class Memory(Operand):
    """
    A pseudo identifier (Grammar: Pseudo(identifier)).
    """
    def __init__(self, reg,_int):
        self.reg = reg
        self._int = _int 
        

    def __repr__(self):
        return f"Memory(reg={self.reg},_int={self._int})"

# Optional: If you want a named 'Register' class:
# class Register(Operand):
#     """
#     A CPU register, e.g. '%eax' (not strictly in the grammar).
#     """
#     def __init__(self, name='%eax'):
#         self.name = name
#     def __repr__(self):
#         return f"Register({self.name})"


# ------------------
# Instruction and subclasses
# ------------------

class Instruction:
    
        
    
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
    
    """
    Base class for assembly instructions.
    """
    pass


class MovZeroExtend(Instruction):
    """
    mov SRC, DEST
    (Grammar: Mov(operand src, operand dst))
    """
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest
        # self._type=assembly_type

    def __repr__(self):
        return f"MovZeroExtend(src={repr(self.src)}, dest={repr(self.dest)})"

class Mov(Instruction):
    """
    mov SRC, DEST
    (Grammar: Mov(operand src, operand dst))
    """
    def __init__(self,assembly_type, src, dest):
        self.src = src
        self.dest = dest
        self._type=assembly_type
        
    def get_type(self):
        return self._type
    def __repr__(self):
        return f"Mov(src={repr(self.src)}, dest={repr(self.dest)},type={self._type})"
    
    
class Movsx(Instruction):
    """
    mov SRC, DEST
    (Grammar: Mov(operand src, operand dst))
    """
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __repr__(self):
        return f"Movsx(src={repr(self.src)}, dest={repr(self.dest)})"
    


class Ret(Instruction):
    """
    ret (Grammar: Ret)
    """
    def __repr__(self):
        return "Ret()"


class Unary(Instruction):
    """
    Unary instruction:
    unary_operator, operand
    (Grammar: Unary(unary_operator, operand))
    """
    def __init__(self, operator,assembly_type, operand):
        self.operator = operator 
        self.operand = operand
        self._type=assembly_type
    def get_type(self):
        return self._type
        
    
    def __repr__(self):
        return f"Unary(operator={self.operator},assembly_type={self._type} operand={self.operand})"
        
        
class Binary(Instruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, operator: str,assembly_type,src1, src2,rel_flag=Optional):
        self.operator = operator  # e.g., '+', '-', '*', '/', '%'
        self.src1 = src1          # Left operand (expression)
        self.src2 = src2        # Right operand (expression)
        self._type=assembly_type
    def get_type(self):
        return self._type
    def __repr__(self):
        return f"Binary(operator='{self.operator}', assembly_type={self._type},left={self.src1}, right={self.src2})"
  
  
class Div(Instruction):
    """
    Represents an integer division instruction in the intermediate representation.
    
    The Idiv instruction performs signed integer division between two operands.
    It typically divides the value in a specific register (e.g., EAX) by the provided operand,
    storing the quotient and remainder in designated registers.
    """
    
    def __init__(self, assembly_type,operand):
        self._type=assembly_type
        self.operand=operand
    def get_type(self):
        return self._type
        """
        Initializes the Idiv instruction with the specified operand.
        
        Parameters:
            operand (Operand): The operand by which the current value will be divided.
        """
        self.operand = operand  # Operand to divide by

    def __repr__(self):
        """
        Returns a string representation of the Idiv instruction.
        
        This method is useful for debugging and logging purposes, providing a clear
        textual representation of the instruction and its operand.
        
        Returns:
            str: A string representing the Idiv instruction.
        """
        return f'Div(assembly_type={self._type},operand={self.operand})'  # Corrected to use self.operand
    
class Idiv(Instruction):
    """
    Represents an integer division instruction in the intermediate representation.
    
    The Idiv instruction performs signed integer division between two operands.
    It typically divides the value in a specific register (e.g., EAX) by the provided operand,
    storing the quotient and remainder in designated registers.
    """
    
    def __init__(self, assembly_type,operand):
        self._type=assembly_type
        self.operand=operand
    def get_type(self):
        return self._type
        """
        Initializes the Idiv instruction with the specified operand.
        
        Parameters:
            operand (Operand): The operand by which the current value will be divided.
        """
        self.operand = operand  # Operand to divide by

    def __repr__(self):
        """
        Returns a string representation of the Idiv instruction.
        
        This method is useful for debugging and logging purposes, providing a clear
        textual representation of the instruction and its operand.
        
        Returns:
            str: A string representing the Idiv instruction.
        """
        return f'Idiv(assembly_type={self._type},operand={self.operand})'  # Corrected to use self.operand

    
class Cdq(Instruction):
    """
    Represents the CDQ (Convert Doubleword to Quadword) instruction in the intermediate representation.
    
    The CDQ instruction is specific to x86 architecture and is used to sign-extend the value
    in the EAX register into the EDX:EAX register pair. This is typically used before performing
    a division operation to prepare the registers for signed division.
    """
    
    def __init__(self,assembly_type):
        self._type=assembly_type
        
    def get_type(self):
        return self._type
        """
        Initializes the Cqd instruction.
        
        Since the CDQ instruction operates on predefined registers (EAX and EDX) and does not
        require any operands, the initializer does not take any parameters.
        """
          # No operands needed for CDQ as it operates on specific registers

    def __repr__(self):
        """
        Returns a string representation of the Cqd instruction.
        
        This method is useful for debugging and logging purposes, providing a clear
        textual representation of the instruction.
        
        Returns:
            str: A string representing the Cqd instruction.
        """
        return f'Cqd(assembly_type={self._type})'  # Represents the CDQ instruction with no operands

class Cmp(Instruction):
    def __init__(self, operand1 ,assembly_type, operand2):
        # super().__init__(assembly_type)
        self.operand1=operand1
        self.operand2=operand2
        self._type=assembly_type
    def get_type(self):
        return self._type
    def __repr__(self):
        return f'Cmp(Operand1={self.operand1},assemby_type={self._type},Operand2 ={self.operand2})'
    
class Jmp(Instruction):
    def __init__(self,indentifier):
        self.identifier= indentifier
    def __repr__(self):
        return f'Jmp(Indentifier={self.identifier})'
    
class JmpCC(Instruction):
    def __init__(self,Cond_code,indentifier):
        self.identifier= indentifier
        self.cond_code = Cond_code
    def __repr__(self):
        return f'JmpCC(Cond_code ={self.cond_code} Indentifier={self.identifier})'
    
class SetCC(Instruction):
    def __init__(self,Cond_code,operand):
        self.operand= operand
        self.cond_code = Cond_code
    def __repr__(self):
        return f'SetCC(Cond_code ={self.cond_code} Indentifier={self.operand})'

class Label(Instruction):
    def __init__(self,indentifier):
        self.identifier= indentifier
    def __repr__(self):
        return f'Label(Indentifier={self.identifier})'
    
class AllocateStack(Instruction):
    """
    Allocates stack space for 'value' units.
    (Grammar: AllocateStack(int))
    """
    def __init__(self, value):
        self.value = value 
    
    def __repr__(self):
        return f"AllocateStack(value={self.value})"

class DeallocateStack(Instruction):
    """
    Allocates stack space for 'value' units.
    (Grammar: AllocateStack(int))
    """
    def __init__(self, value):
        self.value = value 
    
    def __repr__(self):
        return f"DeallocateStack(value={self.value})"

class Push(Instruction):
    def __init__(self,operand:Operand,_type):
        self.operand= operand
        self._type=_type
    def __repr__(self):
        return f'Push(operand={self.operand})'


class Call(Instruction):
    def __init__(self,indentifier):
        self.identifier= indentifier
    def __repr__(self):
        return f'Call(Indentifier={self.identifier})'


class Cvttsd2si(Instruction):
    def __init__(self, dst_type, src , dst):
        # super().__init__(assembly_type)
        self._type=dst_type
        self.src=src
        self.dst=dst
    def get_type(self):
        return self._type
    def __repr__(self):
        return f'Cvttsd2si(Operand1={self.src},assemby_type={self._type},Operand2 ={self.dst})'
class Cvtsi2sd(Instruction):
    def __init__(self, src_type, src , dst):
        # super().__init__(assembly_type)
        self._type=src_type
        self.src=src
        self.dst=dst
    def get_type(self):
        return self._type
    def __repr__(self):
        return f'Cvtsi2sd(Operand1={self.src},assemby_type={self._type},Operand2 ={self.dst})'
class Lea(Instruction):
    def __init__(self, src , dst):
        # super().__init__(assembly_type)
        # self._type=src_type
        self.src=src
        self.dst=dst

    def __repr__(self):
        return f'Lea(src={self.src},dst ={self.dst})'

# ------------------
# Operator Constants
# ------------------

class UnaryOperator():
    """
    Represents unary operators in the grammar.

    Grammar rule:
        unary_operator = Neg | Not

    This class defines the supported unary operators, mapping each operator to its
    corresponding string representation used within the compiler's intermediate
    representation (IR) or abstract syntax tree (AST).
    """

    NEG = "Neg"  # Represents unary negation, e.g., -x
    NOT = "Not"  # Represents bitwise NOT, e.g., ~x (or logical NOT in some Instruction Set Architectures)
    SHR='Shr'

    # Additional unary operators can be added here as needed
    # For example:
    # INC = "Inc"  # Represents increment, e.g., ++x
    # DEC = "Dec"  # Represents decrement, e.g., --x


class BinaryOperator():
    """
    Represents binary operators in the grammar and their corresponding identifiers in the compiler's intermediate representation (IR).
    
    Grammar rule:
        binary_operator = ADD | SUBTRACT | MULTIPLY
    
    This enumeration maps each binary operator to a unique string identifier used within the compiler's IR or abstract syntax tree (AST).
    These identifiers are essential for generating the correct assembly or machine instructions during the code generation phase.
    """
    
    ADD = 'Add'        # Represents the addition operation, e.g., x + y
    SUBTRACT = 'Sub'   # Represents the subtraction operation, e.g., x - y
    MULTIPLY = 'Mult'  # Represents the multiplication operation, e.g., x * y
    DIVDOUBLE='DivDouble' 
    AND='And'
    OR='Or'
    SHR='Shr'
    XOR='Xor'
    # Additional binary operators can be defined here as needed.
    # For example:
    # DIVIDE = 'Divide'      # Represents the division operation, e.g., x / y
    # REMAINDER = 'Remainder' # Represents the modulo operation, e.g., x % y


class Registers:
    """
    Represents the set of CPU registers used in the compiler's intermediate representation.

    Grammar rule:
        reg = AX | DX | R10 | R11

    This class defines the supported registers that the compiler can utilize for
    generating machine instructions or managing temporary storage during code generation.
    Each register is mapped to its string representation corresponding to the target
    machine's architecture (e.g., x86, x64).
    """

    AX = "AX"   # Accumulator Register: commonly used for arithmetic operations
    CX='CX'
    DX = "DX"   # Data Register: often used for I/O operations and extended precision
    DI='DI'     
    SI='SI'
    R8='R8'
    R9='R9'
    R10 = "R10" # General-Purpose Register: available for various operations
    R11 = "R11" # General-Purpose Register: available for various operations
    SP='SP'
    BP='BP'
    XMM0 ='XMM0'
    XMM1 ='XMM1'
    XMM2 ='XMM2'
    XMM3  ='XMM3'
    XMM4 ='XMM4'
    XMM5 ='XMM5'
    XMM6 ='XMM6'
    XMM7  ='XMM7'
    XMM14 ='XMM14'
    XMM15='XMM15'

    # Additional registers can be defined here based on the target architecture
    # For example:
    # RBX = "RBX"  # Base Register: often used to hold base addresses
    # RCX = "RCX"  # Counter Register: used in loop operations
    # RDX = "RDX"  # Data Register: used in I/O operations and extended precision

    # Note:
    # The choice of registers (e.g., AX, DX, R10, R11) should align with the
    # target machine's architecture and calling conventions to ensure correct
    # code generation and execution.

    
# ------------------
# Assembly function and program
# ------------------

class AssemblyFunction:
    """
    Represents a function in assembly with a name (identifier)
    and a list of instructions.
    (Grammar: function_definition = Function(identifier, instruction*))
    """
    def __init__(self, name,_global, instructions:list):
        self.name = name
        self._global=_global
        self.instructions = instructions

    def __repr__(self):
        return (
            "AssemblyFunction("
            f"name={repr(self.name)},"
            f"global={self._global},"
            f"instructions=[\n        " + 
            ",\n        ".join(repr(instr) for instr in self.instructions) +
            "\n    ]\n"
            ")"
        )



class AssemblyStaticConstant:
    def __init__(self,identifier,alignment,init):
        self.name = identifier
        # self._global =_global
        self.alignment=alignment
        self.init = init
    
    def __repr__(self):
        return f'StaticConstant(name={self.name},,alignment={self.alignment},init={self.init})'

class AssemblyStaticVariable:
    def __init__(self,identifier,_global,alignment,init):
        self.name = identifier
        self._global =_global
        self.alignment=alignment
        self.init = init
    
    def __repr__(self):
        return f'StaticVariable(name={self.name},_global={self._global},alignment={self.alignment},init={self.init})'
    
    
class TopLevel:
    assembly_func=AssemblyFunction
    static_var = AssemblyStaticVariable
    static_const = AssemblyStaticConstant

class AssemblyProgram:
    """
    A top-level assembly program, typically containing a single assembly function.
    (Grammar: program = Program(function_definition))
    """
    def __init__(self, function_definition:List[TopLevel]):
        self.function_definition = function_definition

    def __repr__(self):
        return (
            f"AssemblyProgram("
            f"function_definition={repr(self.function_definition)})"
        )



class Cond_code:
    E='E'
    NE='NE'
    G='G'
    GE='GE'
    L='L'
    LE='LE'
    A='A'
    AE='AE'
    B='B'
    BE='BE'