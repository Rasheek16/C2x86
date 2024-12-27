# ---------------------------------------------------------------------------
# Grammar Recap:
#
# program = Program(function_definition)
#
# function_definition = Function(identifier name, statement body)
#
# statement = Return(exp)
#
# exp = Constant(int)
#     | Unary(unary_operator, exp)
#     | Binary(binary_operator, exp, exp)
#
# unary_operator = Complement
#                | Negate
# binary_operator = Add | Subtract | Multiply | Divide | Remainder
# ---------------------------------------------------------------------------

class Program:
    """
    Represents a top-level program consisting of a single function definition.
    Grammar rule: program = Program(function_definition)
    """
    def __init__(self, function_definition):
        self.function_definition = function_definition

    def __repr__(self):
        return f"Program(\n{repr(self.function_definition)}\n)"


class Function:
    """
    Represents a function definition with a name (identifier) and a single statement body.
    Grammar rule: function_definition = Function(identifier name, statement body)
    """
    def __init__(self, name, body:list):
        # `name` should be an Identifier node (or a string, if you prefer).
        # `body` is a single Statement node (per the grammar).
        self.name = name
        self.body = [body]

    def __repr__(self):
        return (
            "Function(\n"
            f"    name={repr(self.name)},\n"
            f"    body={repr(self.body)}\n"
            "\t)"
        )


class Statement:
    """
    Base class for statements in the AST.
    In this grammar, the only statement is 'Return(exp)'.
    """
    pass


class Return(Statement):
    """
    A 'return' statement containing an expression to return.
    Grammar rule: statement = Return(exp)
    """
    def __init__(self, exp):
        # exp should be an Expression node
        self.exp = exp

    def __repr__(self):
        return f"Return(\n    {repr(self.exp)}\n\t\t)"


class Expression:
    """
    Base class for expressions.
    Grammar rule: exp = Constant(int) | Unary(unary_operator, exp)
    """
    pass


class Constant(Expression):
    """
    An integer literal constant.
    Example: Constant(42)
    Grammar rule: exp = Constant(int)
    """
    def __init__(self, value):
        self.value = value  # integer value

    def __repr__(self):
        return f"Constant({self.value})"


class UnaryOperator:
    """
    Represents the unary operators in the grammar.
    Grammar rule: unary_operator = Complement | Negate
    """
    COMPLEMENT = "Complement"  # e.g., ~x
    NEGATE     = "Negation"      # e.g., -x

class BinaryOperator:
    """
    Represents the binary operators in the grammar.
    Grammar rule: binary_operator = Add | Substract | Multiply | Divide | Remainder (Modulus)
    """
    
    ADD='Add'              # e.g, a + b
    SUBTRACT='Subtract'    # e.g, a - b
    MULTIPLY='Multiply'    # e.g, a * b
    DIVIDE = 'Divide'      # e.g, a / b
    REMAINDER='Remainder'  # e.g, a % b


class Unary(Expression):
    """
    A unary expression (unary_operator applied to a sub-expression).
    Grammar rule: exp = Unary(unary_operator, exp)
    """
    def __init__(self, operator, expr):
        # operator should be one of {UnaryOperator.COMPLEMENT, UnaryOperator.NEGATE}.
        # expr is another Expression node.
        self.operator = operator
        self.expr = expr

    def __repr__(self):
        return (
            "\t\tUnary(\n"
            f"    \t\toperator={repr(self.operator)},\n"
            f"    \t\texpr={repr(self.expr)}\n"
            "\t\t\t)"
        )


class Identifier(Expression):
    """
    An identifier (used for function names, variable names, etc.).
    You can store it as a string internally.
    """
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Identifier({self.name})"
