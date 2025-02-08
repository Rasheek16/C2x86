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
#             | Binary(binary_operator, val src1, val src2, val dst)

# val = Constant(int)
#     | Var(identifier)
#
# unary_operator = Complement
#                | Negate
# binary_operator = Add 
#                 | Subtract 
#                 | Multiply 
#                 | Divide 
#                 | Remainder
# ------------------------------------------------------------------
from typing import List,Optional

class TackyIdentifier:
    """
    Represents an identifier, such as function names or variable names.
    
    Attributes:
        name (str): The name of the identifier.
    """
    def __init__(self, name: str):
        """
        Initializes an Identifier instance.
        
        Args:
            name (str): The name of the identifier.
        """
        self.name = name

    def __repr__(self) :
        """
        Returns a string representation of the Identifier.
        
        Returns:
            str: The string representation.
        """
        return f"Identifier(name={self.name})"

class TackyInstruction:
    """
    Base class for instructions in the function body.
    """
    pass

class TackyFunction:
    """
    function_definition = Function(identifier, [instructions...])
    
    The function has:
    - name: an identifier
    - body: a list of instructions (one or more).
    """
    def __init__(self, identifier,_global:bool,params:List[TackyIdentifier], body:List[TackyInstruction]):
        self._global = _global 
        self.name = identifier  
        self.params=params # An identifier (string or Var)
        self.body = body        # A list of instructions: Return(...) or Unary(...)
    
    def __repr__(self):
        return (
            "TackyFunction(\n"
            f"    identifier={repr(self.name)},\n"
            f'    global={self._global}\n'
            f'    params={repr(self.params)}\n'
            f"    body=[\n        " + 
            ",\n        ".join(repr(instr) for instr in self.body) +
            "\n    ]\n"
            ")"
        )


class TackyStaticVariable:
    def __init__(self,identifier,_global,_type,init):
        self.name = identifier
        self._global =_global
        self.init = init
        self._type=_type
    
    def __repr__(self):
        return f'TackyStaticVariable(name={self.name},_global={self._global},type={self._type},init={self.init})'
        

class TopLevel:
    tack_func=TackyFunction
    static_var = TackyStaticVariable
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
    
    
class TackyProgram:
    """
    program = Program(function_definition)
    """
    def __init__(self, function_definition:List[TopLevel]):
        self.function_definition = function_definition

    def __repr__(self):
        return f"TackyProgram(\n  {repr(self.function_definition)}\n)"





# ------------------
# Instructions
# ------------------


class TackyZeroExtend(TackyInstruction):
    """
    instruction = Unary(unary_operator, val src, val dst)
    """
    def __init__(self, src, dst):
 # 'Complement' or 'Negate'
        self.src = src            # A val
        self.dst = dst            # Another val
                                  
    def __repr__(self):
        return (
            "TackyZeroExtend(\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )


class TackyDoubleToUInt(TackyInstruction):
    """
    instruction = Unary(unary_operator, val src, val dst)
    """
    def __init__(self, src, dst):
 # 'Complement' or 'Negate'
        self.src = src            # A val
        self.dst = dst            # Another val
                                  
    def __repr__(self):
        return (
            "TackyDoubleToUInt(\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )

class TackyDoubleToInt(TackyInstruction):
    """
    instruction = Unary(unary_operator, val src, val dst)
    """
    def __init__(self, src, dst):
 # 'Complement' or 'Negate'
        self.src = src            # A val
        self.dst = dst            # Another val
                                  
    def __repr__(self):
        return (
            "TackyDoubleToInt(\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )

class TackyUIntToDouble(TackyInstruction):
    """
    instruction = Unary(unary_operator, val src, val dst)
    """
    def __init__(self, src, dst):
 # 'Complement' or 'Negate'
        self.src = src            # A val
        self.dst = dst            # Another val
                                  
    def __repr__(self):
        return (
            "TackyUIntToDouble(\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )

class TackyIntToDouble(TackyInstruction):
    """
    instruction = Unary(unary_operator, val src, val dst)
    """
    def __init__(self, src, dst):
 # 'Complement' or 'Negate'
        self.src = src            # A val
        self.dst = dst            # Another val
                                  
    def __repr__(self):
        return (
            "TackyIntToDouble(\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )





class TackyReturn(TackyInstruction):
    """
    instruction = Return(val)
    """
    def __init__(self, val):
        super().__init__()
        self.val = val  # A val, i.e., Constant(...) or Var(...)
    
    def __repr__(self):
        return f"TackyReturn({repr(self.val)})"


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
            "TackyUnary(\n"
            f"  operator={repr(self.operator)},\n"
            f"  src={repr(self.src)},\n"
            f"  dst={repr(self.dst)}\n"
            ")"
        )

class TackyBinary(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, operator: str, src1, src2 ,dst,rel_type=Optional):
        self.operator = operator  # e.g., '+', '-', '*', '/', '%'
        self.src1 = src1          # Left operand (expression)
        self.src2 = src2        # Right operand (expression)
        self.dst = dst            # temporary dest variable
        self.rel_type = rel_type

    def __repr__(self):
        return f"TackyBinary(operator='{self.operator}', left={self.src1}, right={self.src2}, dst={self.dst},rel_type={self.rel_type})"

class TackyCopy(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, source,destination):
        
        self.src = source        # Left operand (expression)
        self.dst = destination        # temporary dest variable

    def __repr__(self):
        return f"TackyCopy(src={self.src}, dst={self.dst})"

class TackyJump(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, target):
      self.target = target          # temporary dest variable

    def __repr__(self):
        return f"TackyJump(identifier={self.target})"
    
class TackyJumpIfZero(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, condition,target,_type=Optional):
        self.condition = condition
        self.target = target          # temporary dest variable
        self._type = _type

    def __repr__(self):
        return f"TackyJumpIfZero(condition={self.condition},target={self.target},_type={self._type})"

class TackyJumpIfNotZero(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, condition,target,_type=Optional):
        self.condition = condition
        self.target = target          # temporary dest variable
        self._type = _type 

    def __repr__(self):
        return f"TackyJumpIfNotZero(condition={self.condition},identifier={self.target},type={self._type})"


class TackyLabel(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self,identifer):
        self.identifer = identifer   # temporary dest variable

    def __repr__(self):
        return f"TackyLabel(identifier={self.identifer})"


class TackySignExtend(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, source,destination):
        
        self.src = source        # Left operand (expression)
        self.dst = destination        # temporary dest variable

    def __repr__(self):
        return f"TackySignExtend(src={self.src}, dst={self.dst})"


class TackyTruncate(TackyInstruction):
    """
    Represents a binary operation in the AST.
    """
    def __init__(self, source,destination):
        
        self.src = source        # Left operand (expression)
        self.dst = destination        # temporary dest variable

    def __repr__(self):
        return f"TackyTruncate(src={self.src}, dst={self.dst})"

class TackyGetAddress(TackyInstruction):
    def __init__(self,src,dst):
        self.src = src
        self.dst = dst
         
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return f'TackyGetAddress(source={self.src} , destination = {self.dst})'
        
class TackyLoad(TackyInstruction):
    def __init__(self,src_ptr,dst):
        self.src_ptr = src_ptr
        self.dst = dst
         
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return f'TackyLoad(source={self.src_ptr} , destination = {self.dst})'


class TackyStore(TackyInstruction):
    def __init__(self,src,dst_ptr):
        self.src = src
        self.dst_ptr = dst_ptr
         
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return f'TackyStore(source={self.src} , destination = {self.dst_ptr})'
    
    
class PlainOperand():
    def __init__(self, val):
        self.val=val
    def __repr__(self):
        return f'PlainOperand(val={self.val})'
        super(CLASS_NAME, self).__init__(*args, **kwargs)

class DereferencedPointer():
    def __init__(self, val):
        self.val=val
    def __repr__(self):
        return f'DereferencedPointer(val={self.val})'

class TackyExpResult():
    PlainOperand=PlainOperand
    DereferencedOperand=DereferencedPointer

# ------------------
# Val = Constant(int) | Var(identifier)
# ------------------

class TackyVal:
    """
    Base class for values.
    """
    pass




class TackyFunCall(TackyInstruction):
    def __init__(self,fun_name:TackyIdentifier,args :List[TackyVal],dst:TackyVal):
        self.fun_name= fun_name
        self.args=args
        self.dst=dst 
    
    def __repr__(self):
        return f'TackyFunCall(fun_name={self.fun_name},args:{self.args},dst={self.dst})'

   
    


class TackyConstant(TackyVal):
    """
    val = Constant(int)
    """
    def __init__(self, value):
        super().__init__()
        self.value = value

    def __repr__(self):
        return f"TackyConstant({self.value})"


class TackyVar(TackyVal):
    """
    val = Var(identifier)
    """
    def __init__(self, identifier):
        super().__init__()
        self.identifier = identifier

    def __repr__(self):
        return f"TackyVar({self.identifier})"
        


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
    NOT = 'Not'


# TODO REPLACE OPERATOR NAME WITH SYMBOLS
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
    AND ='And'
    OR='Or'
    EQUAL='Equal'
    NOT_EQUAL='NotEqual'
    LESS_THAN='LessThan'
    LESS_OR_EQUAL='LessOrEqual'
    GREATER_THAN='GreaterThan'
    GREATER_OR_EQUAL='GreaterOrEqual'
    ASSIGNMENT='Assignment'