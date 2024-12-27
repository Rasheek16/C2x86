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




# ------------------
# Operand and subclasses
# ------------------

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
    Only AX or R10 are allowed, per grammar.
    """
    def __init__(self, value):
        # We check against the valid enumerations in 'Registers'
        if value not in (Registers.AX, Registers.R10):
            raise TypeError(f"Invalid register value: {value}")
        self.value = value

    def __repr__(self):
        return f"Reg({self.value})"


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
    """
    Base class for assembly instructions.
    """
    pass


class Mov(Instruction):
    """
    mov SRC, DEST
    (Grammar: Mov(operand src, operand dst))
    """
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __repr__(self):
        return f"Mov(src={repr(self.src)}, dest={repr(self.dest)})"


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
    def __init__(self, operator, operand):
        self.operator = operator 
        self.operand = operand
    
    def __repr__(self):
        return f"Unary(operator={self.operator}, operand={self.operand})"
        
        
class AllocateStack(Instruction):
    """
    Allocates stack space for 'value' units.
    (Grammar: AllocateStack(int))
    """
    def __init__(self, value):
        self.value = value 
    
    def __repr__(self):
        return f"AllocateStack(value={self.value})"
    

# ------------------
# Operator Constants
# ------------------

class UnaryOperator:
    """
    Grammar rule: unary_operator = Neg | Not
    """
    NEG = "Neg"  # e.g., unary negation, -x
    NOT = "Not"  # e.g., bitwise not, ~x  (or logical not in some ISAs)


class Registers:
    """
    Grammar rule: reg = AX | R10
    """
    AX = "AX"
    R10 = "R10"
    
    
# ------------------
# Assembly function and program
# ------------------

class AssemblyFunction:
    """
    Represents a function in assembly with a name (identifier)
    and a list of instructions.
    (Grammar: function_definition = Function(identifier, instruction*))
    """
    def __init__(self, name, instructions:list):
        self.name = name
        self.instructions = instructions

    def __repr__(self):
        return (
            "AssemblyFunction("
            f"name={repr(self.name)}, "
            f"instructions={repr(self.instructions)}"
            ")"
        )


class AssemblyProgram:
    """
    A top-level assembly program, typically containing a single assembly function.
    (Grammar: program = Program(function_definition))
    """
    def __init__(self, function_definition):
        self.function_definition = function_definition

    def __repr__(self):
        return (
            f"AssemblyProgram("
            f"function_definition={repr(self.function_definition)})"
        )
