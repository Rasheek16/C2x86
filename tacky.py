# ------------------------------------------------------------------
# Grammar (as given):
#
# program = Program(function_definition)
#
# function_definition = Function(identifier, 1 instruction* body)
#    (i.e., a function has a name and one or more instructions)
#
# instruction = Return(val)
#             | Unary(unary_operator, val src, val dst)
#
# val = Constant(int)
#     | Var(identifier)
#
# unary_operator = Complement
#                | Negate
# ------------------------------------------------------------------

class Program:
    """
    program = Program(function_definition)
    """
    def __init__(self, function_definition):
        self.function_definition = function_definition

    def __repr__(self):
        return f"Program(\n  {repr(self.function_definition)}\n)"


class Function:
    """
    function_definition = Function(identifier, [instructions...])
    
    The function has:
    - name: an identifier
    - body: a list of instructions (one or more).
    """
    def __init__(self, name, body):
        self.name = name          # An identifier (string or Var)
        self.body = body          # A list of instructions: Return(...) or Unary(...)
    
    def __repr__(self):
        return (
            "Function(\n"
            f"    name={repr(self.name)},\n"
            f"    body=[\n        " + 
            ",\n        ".join(repr(instr) for instr in self.body) +
            "\n    ]\n"
            ")"
        )


# ------------------
# Instructions
# ------------------

class Instruction:
    """
    Base class for instructions in the function body.
    """
    pass


class Return(Instruction):
    """
    instruction = Return(val)
    """
    def __init__(self, val):
        super().__init__()
        self.val = val  # A val, i.e., Constant(...) or Var(...)
    
    def __repr__(self):
        return f"Return({repr(self.val)})"


class Unary(Instruction):
    """
    instruction = Unary(unary_operator, val src, val dst)
    """
    def __init__(self, operator, src, dst):
        super().__init__()
        self.operator = operator  # 'Complement' or 'Negate'
        self.src = src            # A val
        self.dst = dst            # Another val
                                  
    def __repr__(self):
        return (
            "Unary(\n"
            f"  operator={repr(self.operator)},\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )

# ------------------
# Val = Constant(int) | Var(identifier)
# ------------------

class Val:
    """
    Base class for values.
    """
    pass


class Constant(Val):
    """
    val = Constant(int)
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"


class Var(Val):
    """
    val = Var(identifier)
    """
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"Var({self.name})"


# ------------------
# Operator Constants
# ------------------

class UnaryOperator:
    """
    unary_operator = Complement | Negate
    We store them simply as string constants or you could use an enum.
    """
    COMPLEMENT = "Complement"  # e.g. ~
    NEGATE     = "Negation"      # e.g. -
