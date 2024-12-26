class Operand:
    """
    Base class for ASM operands (e.g., immediate values, registers).
    """
    pass


class Imm(Operand):
    """
    An immediate value, e.g. '10' or '0x3F'.
    """
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"Imm({self.value})"


class Register(Operand):
    """
    A CPU register, e.g. '%eax'.
    """
    def __init__(self, name='%eax'):
        self.name = name

    def __repr__(self):
        return f"Register({self.name})"


class Instruction:
    """
    Base class for assembly instructions.
    """
    pass


class Mov(Instruction):
    """
    mov SRC, DEST
    """
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

    def __repr__(self):
        return f"Mov(src={repr(self.src)}, dest={repr(self.dest)})"


class Ret(Instruction):
    """
    ret
    """
    def __repr__(self):
        return "Ret()"


class AssemblyFunction:
    """
    Represents a function in assembly with a label (name) and a list of instructions.
    """
    def __init__(self, name, instructions):
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
    """
    def __init__(self, function_definition):
        self.function_definition = function_definition

    def __repr__(self):
        return f"AssemblyProgram(function_definition={repr(self.function_definition)})"
