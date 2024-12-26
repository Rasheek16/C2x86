class Program:
    """
    Represents a top-level program consisting of a single function definition.
    """
    def __init__(self, function_definition):
        self.function_definition = function_definition

    def __repr__(self):
        return f"Program(\n{repr(self.function_definition)}\n)"


class Function:
    """
    Represents a function definition with a name and a body (list of statements).
    """
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self):
        return (
            "Function(\n"
            f"    name={repr(self.name)},\n"
            f"    body={repr(self.body)}\n"
            ")"
        )


class Statement:
    """
    Base class for statements in the AST (e.g., return statements).
    """
    def __init__(self, expression):
        self.expression = expression


class Return(Statement):
    """
    A 'return' statement containing an expression to return.
    """
    def __init__(self, exp):
        super().__init__(exp)
        self.exp = exp  # Redundant but clear; same as self.expression

    def __repr__(self):
        return f"Return(\n    {repr(self.exp)}\n)"


class Expression:
    """
    Base class for expressions, e.g., constants, identifiers, function calls.
    """
    def __init__(self, value):
        self.value = value


class Constant(Expression):
    """
    An integer or other literal constant.
    """
    def __init__(self, value):
        super().__init__(value)

    def __repr__(self):
        return f"Constant({self.value})"


class Identifier(Expression):
    """
    An identifier (variable name, function name, etc.).
    """
    def __init__(self, name):
        super().__init__(name)

    def __repr__(self):
        return f"Identifier({self.value})"
