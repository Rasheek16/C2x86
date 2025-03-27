from typing import List
class InitialValue:
    """Base class for initial values."""
    pass


    
class IntInit():
    def __init__(self, value):
        self.value=value 
    def __repr__(self):
        return f'IntInit(value={self.value})'
    
    
class UIntInit():
    def __init__(self, value):
        self.value=value 
    def __repr__(self):
        return f'UIntInit(value={self.value})'
class LongInit():
    def __init__(self, value):
        self.value=value 
    def __repr__(self):
        return f'LongInit(value={self.value})'
class ULongInit():
    def __init__(self, value):
        self.value=value 
    def __repr__(self):
        return f'ULongInit(value={self.value})'

class DoubleInit():
    def __init__(self, value):
        self.value=value 
    def __repr__(self):
        return f'DoubleInit(value={self.value})'
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
    
class ZeroInit():
    def __init__(self, bytes):
        self.value=bytes 
    def __repr__(self):
        return f'ZeroInit(bytes={self.value})'
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
    
    
class StaticInit:
    IntInit=IntInit 
    LongInit=LongInit
    UIntInit=UIntInit 
    ULongInit=ULongInit
    DouleInit=DoubleInit
    ZeroInit=ZeroInit

class Tentative(InitialValue):
    """Represents a tentative definition without an initializer."""
    
    def __init__(self,value=None):
        self.value=value
        # pass  # No additional attributes needed
    
    def __repr__(self):
        return "Tentative()"


class Initial(InitialValue):
    """Represents an initialized variable with a specific value."""
    
    def __init__(self, value:List[StaticInit]):
        self.value = value  # You can adjust the type based on your needs
    
    def __repr__(self):
        return f"Initial(value={self.value})"


class NoInitializer(InitialValue):
    """Represents a variable without an initializer."""
    
    def __init__(self,value=None):
        self.value=value
        
        # pass  # No additional attributes needed
    
    def __repr__(self):
        return "NoInitializer()"


class IdentifierAttr:
    """Base class for identifier attributes."""
    pass


class FunAttr(IdentifierAttr):
    """Represents function attributes."""
    
    def __init__(self, defined: bool, global_scope: bool):
        self.defined = defined
        self.global_scope = global_scope
    
    def __repr__(self):
        return f"FunAttr(defined={self.defined}, global_scope={self.global_scope})"


class StaticAttr(IdentifierAttr):
    """Represents static variable attributes."""
    
    def __init__(self, init: InitialValue, global_scope: bool):
        self.init = init  # Should be an instance of InitialValue
        self.global_scope = global_scope
    
    def __repr__(self):
        return f"StaticAttr(init={self.init}, global_scope={self.global_scope})"


class LocalAttr(IdentifierAttr):
    """Represents local variables."""
    
    def __init__(self):
        pass  # No additional attributes needed
    
    def __repr__(self):
        return "LocalAttr()"
