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

class TackyProgram:
    """
    program = Program(function_definition)
    """
    def __init__(self, function_definition):
        self.function_definition = function_definition

    def __repr__(self):
        return f"Program(\n  {repr(self.function_definition)}\n)"


class TackyFunction:
    """
    function_definition = Function(identifier, [instructions...])
    
    The function has:
    - name: an identifier
    - body: a list of instructions (one or more).
    """
    def __init__(self, name, body:list):
        self.name = name          # An identifier (string or Var)
        self.body = [body]        # A list of instructions: Return(...) or Unary(...)
    
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

class TackyInstruction:
    """
    Base class for instructions in the function body.
    """
    pass


class TackyReturn(TackyInstruction):
    """
    instruction = Return(val)
    """
    def __init__(self, val):
        super().__init__()
        self.val = val  # A val, i.e., Constant(...) or Var(...)
    
    def __repr__(self):
        return f"Return({repr(self.val)})"


class TackyUnary(TackyInstruction):
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

class TackyVal:
    """
    Base class for values.
    """
    pass


class TackyConstant(TackyVal):
    """
    val = Constant(int)
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"Constant({self.value})"


class TackyVar(TackyVal):
    """
    val = Var(identifier)
    """
    def __init__(self, identifier):
        super().__init__()
        self.identifier = identifier

    def __repr__(self):
        return f"Var({self.identifier})"
        


# ------------------
# Operator Constants
# ------------------

class TackyUnaryOperator:
    """
    unary_operator = Complement | Negate
    We store them simply as string constants or you could use an enum.
    """
    COMPLEMENT = "Complement"  # e.g. ~
    NEGATE     = "Negation"      # e.g. -

class TackyBinaryOperator:
    """
    Represents the binary operators in the grammar.
    Grammar rule: binary_operator = Add | Substract | Multiply | Divide | Remainder (Modulus)
    """
    
    ADD='Add'              # e.g, a + b
    SUBTRACT='Subtract'    # e.g, a - b
    MULTIPLY='Multiply'    # e.g, a * b
    DIVIDE = 'Divide'      # e.g, a / b
    REMAINDER='Remainder'  # e.g, a % b