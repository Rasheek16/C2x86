from src.frontend.parser._ast5 import *
from typing import Optional, List
from src.backend.typechecker.type_classes import *
import sys

x =0
def size_compound_init(_type):
   
    if isinstance(_type,(Char,UChar,SChar)):
        return 1 
    elif type(_type)==type(Int()):
        return 4
    elif type(_type)==type(Long()):
        return 8
    elif type(_type)==type(UInt()):
        return 4
    elif type(_type)==type(ULong()):
        return 8
    elif type(_type)==type(Double()):
        return 8
    elif isinstance(_type,Pointer):
        return 8
    elif isinstance(_type,Array):
        if isinstance(_type._type,(Char,SChar,UChar)):
            return 1
        else:
            return _type._type
        
        

def array_size(array_type):
    if isinstance(array_type,Pointer):
        if isinstance(array_type.ref,(Double,Pointer)):
            return 8 
     
        
        return size(array_type.ref)        
    if isinstance(array_type,Double):
        return 8 
    else:
        return size(array_type)



def size1(_type):
    if isinstance(_type,(Int,Char,SChar)):
        return 4
    elif isinstance(_type,Long):
        return 8
    elif isinstance(_type,(UInt,UChar)):
        return 4
    elif isinstance(_type,ULong):
        return 8
    elif isinstance(_type,Double):
        return 16
    elif isinstance(_type,Pointer):
        return array_size(_type.ref)
    elif isinstance(_type,Array):
       
        if isinstance(_type._type,Pointer):
            return 8 * _type._int
        
        print(_type._type)
    
        return array_size(_type._type) * _type._int.value._int 
    
def size(_type):
    print(_type)
    if isinstance(_type,(UChar,Char,SChar)):
        return 1
    elif isinstance(_type,Long):
        return 8
    elif isinstance(_type,(Int,UInt)):
        return 4
    elif isinstance(_type,ULong):
        return 8
    elif isinstance(_type,Double):
        return 16
    elif isinstance(_type,Pointer):
        return 8
    elif isinstance(_type,Array):
        if isinstance(_type._type,Pointer):
            if hasattr(_type._int,'value'):
            
                return 8 * _type._int.value._int
            else:
                return 8 * _type._int
        if hasattr(_type._int,'value'):
        
            return array_size(_type._type) * _type._int.value._int
        else:
            return array_size(_type._type) * _type._int
        # else:
    
def is_null_pointer_constant(c):
    if isinstance(c,Constant):
        if isinstance(c.value,(ConstInt,ConstDouble,ConstUInt,ConstLong,ConstULong)):
            if c.value._int==0:
                return True
    
    return False


def convert_by_assignment(e, target_type):
    print('Inside convert by assignment')
    if isinstance(e.get_type(),type(target_type)):
      
        return e
    if not isinstance(e.get_type(),Pointer) and not isinstance(target_type ,Pointer):
        
        
        return convert_to(e, target_type)
    if is_null_pointer_constant(e) and isinstance(target_type ,Pointer):
        
        
        return convert_to(e, target_type)
    
    if (isinstance(target_type,Pointer) and isinstance(target_type.ref,Void)) and isinstance(e.get_type(),Pointer):
        return convert_to(e,target_type)

    if( isinstance(target_type,Pointer) and  isinstance(e.get_type(),Pointer) )and isinstance(e.get_type().ref,Void):
        return convert_to(e,target_type)
    
    else:
        raise SyntaxError("Cannot convert type for assignment")


def get_ref_type(pointerType):
    if isinstance(pointerType,Pointer) and isinstance(pointerType.ref,Array):
        return get_ref_type(pointerType.ref)
    if isinstance(pointerType,Array):
        return get_ref_type(pointerType._type)
    else:
        # print('Pointer type',pointerType)
        return pointerType





def get_common_pointer_type(e1, e2):

   
    if hasattr(e1,'exp') and isinstance(e1.exp,Cast):
        return e1.exp.target_type
    if hasattr(e2,'exp') and isinstance(e2.exp,Cast):
        return e2.exp.target_type
    
    e1_t = e1.get_type()
    e2_t = e2.get_type()


    if (isinstance(e1_t,Pointer) and isinstance(e1_t.ref,Void)) and isinstance(e2_t,Pointer):
        return Pointer(Void())
    if (isinstance(e2_t,Pointer) and isinstance(e2_t.ref,Void)) and isinstance(e1_t,Pointer):
        return Pointer(Void())    
    if isinstance(e1_t,Pointer) and isinstance(e2_t,Pointer):
        
        if isinstance(e1_t.ref,type(e2_t.ref)):
            return e1_t
        else:
            print(e1_t.ref)
            print(e2_t.ref)
            
            # exit()
            raise SyntaxError("Pointer types are not compatible")
        
    if type(e1_t)==type(e2_t):
        return e1
    if is_null_pointer_constant(e1):
        return e2_t
    elif is_null_pointer_constant(e2):
        return e1_t
    else:
        raise SyntaxError("Expressions have incompatible types")


def isSigned(_type):
    if type(_type)==type(Int()) or type(_type)==type(Long()) or type(_type)==type(Double()) or type(_type)==type(Char()) or type(_type)==type(SChar()):
        return True
    return False
    

def is_scalar(t):
    if isinstance(t,Void):
        return False
    if isinstance(t,Array):
        return False
    if isinstance(t,FunType):
        return False
    if isinstance(t,Structure):
        return False
    return True     

def get_common_type(type1, type2):
    
    if isinstance(type1,(Char,SChar,UChar)):
        type1 = Int()
    if isinstance(type2,(Char,SChar,UChar)):
        type2 = Int()
    
    # if isinstance(type1,(UChar)):
    #     type1 = UInt()
    # if isinstance(type2,(UChar)):
    #     type2 = UInt()


    if type(type1) == type(type2):
        return type1
    if isinstance(type1,Double) or isinstance(type2,Double):
        print('Returning double')
        return Double()
    if size(type1) == size(type2):
        if isSigned(type1):
            return type2 
        else:
            return type1
    if size(type1) > size(type2):
        return type1
    else:
        return type2



def convert_to(e: Exp, t: any):
    # #e.get_type())
    """
    Converts expression 'e' to type 't' by wrapping it in a Cast node, 
    unless 'e' is already that type or is already an identical Cast.
    """
    # If node already has the correct type, no cast needed
    if type(e.get_type()) == type(t):
        return e

    # If it's already a cast to the same type, skip
    if isinstance(type(e), Cast) and type(e.target_type) ==type( t):
        #'here')
        return e

    # Otherwise wrap in a new cast
    cast_exp = Cast(target_type=t, exp=e)
    cast_exp.set_type(t)
    return cast_exp


def typecheck_exp_and_convert(expression,symbols,_type=None,type_table={}):
    
  
    typed_e = typecheck_exp(expression, symbols,_type,type_table=type_table)
   
    
    
    if not isinstance(typed_e,Null) and isinstance(typed_e.get_type(),Array):
        
        validate_type_specifier(typed_e.get_type())
        expression = AddOf(typed_e)
   
        expression.set_type(Pointer(typed_e.get_type()._type))
        return expression
    elif isinstance(typed_e,Structure):
        if typed_e not in type_table:
            raise TypeError('invalid use of incomplete structure type')
        return typed_e
    return typed_e


def flat_val(var_type,val):
    print(var_type)
    decl = var_type
    if isinstance(var_type,Array):
        a=[]
        for i in val:
            i=ord(i)
            x=flat_val(var_type._type,i)
            a.extend(x)
            print(a)
            # exit()
        return a 
        
   
    elif isinstance(var_type,Pointer):
        decl = var_type.ref
    
    if isinstance(decl,Int):
        new_init = Constant(StaticInit.IntInit(Const.constInt(int(val))))
        new_init.set_type(var_type)
    elif isinstance(decl,UInt):
        new_init = Constant(StaticInit.UIntInit(Const.constUInt(int(val))))
        new_init.set_type(var_type)
        
    elif isinstance(decl,Long):
        new_init = Constant(StaticInit.LongInit(Const.constLong(int(val))))
        new_init.set_type(var_type)
        
    elif isinstance(decl,ULong):
        new_init = Constant(StaticInit.ULongInit(Const.constULong(int(val))))
        new_init.set_type(var_type)
        
    elif isinstance(decl,Double):
        new_init = Constant(StaticInit.DouleInit(Const.constDouble(float(val))))
        new_init.set_type(var_type)
    elif isinstance(decl,(Char,SChar)):
        new_init = Constant(StaticInit.charInit(Const.constChar(val)))
        new_init.set_type(var_type)
    elif isinstance(decl,UChar):
        new_init = Constant(StaticInit.uCharInit(Const.constUChar(val)))
        new_init.set_type(var_type)
 
    return [new_init]
    

def get_type(_Type):
    if isinstance(_Type,Array):
        return get_type(_Type._type)
    if isinstance(_Type,Pointer):
        return getattr(_Type.ref)
    return _Type


def typecheck_array_init(decl, var_type=None):


    """
    Recursively typechecks an array initializer and returns a flattened list of initial values.

    For a SingleInit, returns a flattened value using flat_val().
    For a CompoundInit, processes each initializer recursively:
      - For nested CompoundInit elements, it recurses using the sub-type (var_type._type).
      - For SingleInit elements, it appends the flattened value.
      - For any unexpected element, it appends a ZeroInit(4).

    If a CompoundInit has fewer elements than expected:
      - For a partially initialized row, missing elements are padded with ZeroInit(4) each.
      - For an entirely missing element (i.e. a missing row), a single ZeroInit whose byte
        count equals (expected_inner * 4) is appended.
    
    var_type must be provided.
    """
    # print(decl)
    # exit()
    if var_type is None:
        raise ValueError("var_type must be provided for array initialization")
    
    
    # if (isinstance(decl,CompoundInit) and not isinstance(decl.initializer[0],CompoundInit)) and isinstance(var_type._type,Array):
    #     raise ValueError('Multidim Array initializer must be a compound initializer')
    # Base case: SingleInit returns its flattened value.
    if isinstance(decl, SingleInit):
        if isinstance(decl.exp,Cast):
            decl.exp.exp.set_type(var_type)
            return flat_val(var_type, decl.exp.exp.value._int)
        decl.exp.set_type(var_type)
      
        if isinstance(decl.exp,String):
            print('here')
            decl.exp.set_type(var_type)
            return flat_val(var_type,decl.exp.string)
        decl.exp.set_type(var_type)
        return flat_val(var_type, decl.exp.value._int)
    
    # Recursive case: CompoundInit.
    elif isinstance(decl, CompoundInit):
       
        result = []
        # expected_length: the number of elements at this array level.
            
        expected_length = var_type._int.value._int
        
        if hasattr(var_type, "_type") and hasattr(var_type._type, "_int"):
            expected_inner = var_type._type._int.value._int
        else:
            expected_inner = None

        # For multidimensional arrays, var_type._type gives the type of a subarray.
        # expected_inner is the expected count for each nested (row) initializer.

        for i in range(expected_length):
            if i < len(decl.initializer):
                elem = decl.initializer[i]
                # If we expect nested initializers (i.e. an array of arrays)
                if expected_inner is not None:
                    # Recursively flatten the row using the sub-type.
                    flattened = typecheck_array_init(elem, var_type._type)
                    # If the row has fewer elements than expected, pad with ZeroInit(4) per element.
                  
                    if len(flattened) < expected_inner:
                        print('sub 1')
                        missing = expected_inner - len(flattened)
                        print(missing)
                        if isinstance(get_type(var_type),(Char,SChar,UChar)):
                            flattened.extend([Constant(CharInit(ConstChar(0)))])
                            if missing>1:
                                flattened.extend([Constant(CharInit(ConstChar(0)))]*(missing -1 ))
                                
                        else:
                            flattened.extend([ZeroInit(4)]*missing)
                           
                    # Append the flattened row to the overall result.
                    result.extend(flattened)
                else:
                    # Scalar element case.
                    if isinstance(elem, CompoundInit):
                        flattened = typecheck_array_init(elem, var_type._type)
                        result.extend(flattened)
                    elif isinstance(elem, SingleInit):
                        result.extend(typecheck_array_init(elem, var_type._type))
                    else:
                        if isinstance(get_type(var_type),(Char,SChar,UChar)):
                            result.extend([Constant(CharInit(ConstChar(0)))])
                                   
                        else:
                            result.extend([ZeroInit(4)]*missing)
                        
                        result.append(ZeroInit(4))
            else:
                # If no initializer is provided for this element:
                if expected_inner is not None:
                    # Missing entire row: pad with a single ZeroInit whose size is the row's total bytes.
                    result.append(ZeroInit(expected_inner * 4))
                else:
                    if isinstance(get_type(var_type),(Char,SChar,UChar)):
                        result.extend([Constant(CharInit(ConstChar(0)))])
                    else:
                            result.extend([ZeroInit(4)]*missing)
                    # result.append(ZeroInit(4))
        return result

    else:
        return []

def validate_struct_definition(struct_decl:StructDecl,type_table):
    print('inside validate struct defn')
    # Step 1: Check for redefinition of struct tag in current scope
    if struct_decl.tag in type_table:
        raise TypeError("Redefinition of struct '" + struct_decl.tag + "'")

    # Step 2: Validate members
    seen_names = {}
    for member in struct_decl.members:
        print(member)
        # exit()
        name = member.member_name.name
        _type = member.member_type
        if name in type_table:
            raise TypeError("Duplicate member name '" + name + "' in struct '" + struct_decl.tag + "'")
        seen_names[name]=True

        if not is_complete(_type, type_table):
            raise TypeError("Member '" + name + "' has incomplete type in struct '" + struct_decl.tag + "'")
       
        if isinstance(_type,Array) and not is_complete(_type._type, type_table):
            raise TypeError("Member '" + name + "' is array of incomplete type in struct '" + struct_decl.tag + "'")
        
        if isinstance(_type,FunDecl):
            raise TypeError("Member '" + name + "' has function type in struct '" + struct_decl.tag + "'")
        print(member)
    return 

def alignment(t,type_table:dict):
    if isinstance(t,Structure):
        struct_def = type_table.get(t.tag)
        return struct_def.alignment
    
    elif isinstance(t,Array):
        return alignment(t._type,type_table)
    
    elif isinstance(t,(Int,UInt)):
        return 4 
    
    elif isinstance(t,(Double,Long,ULong,Pointer)):
        return 8 
    elif isinstance(t,(Char,UChar,SChar)):
        return 1
    
    else:
        raise TypeError(f'unknown type for alignment, {repr(t)}')
    
def round_up(offset, alignment):
    return ( (offset + alignment - 1) // alignment ) * alignment

def typecheck_structure_decl(struct_decl:StructDecl,type_table):
    # print(struct_decl.tag)
    # print(str_table)
    # exit()
    # struct_decl.tag =
    if struct_decl.members is None:
        return 
    validate_struct_definition(struct_decl,type_table)
    print('exit valid struct defn')
    member_entries = []
    
    struct_size = 0 
    struct_alignment = 1 
    for member in struct_decl.members:
        print(member)
        # exit()
        member_alignment = alignment(member.member_type, type_table)
        member_offset = round_up(struct_size, member_alignment)
        m = MemberEntry(member.member_name, member.member_type,member_offset)
        member_entries.append(m)
        print('here')
        struct_alignment = max(struct_alignment, member_alignment)
        struct_size = member_offset + size(member.member_type)
    struct_size = round_up(struct_size,struct_alignment)
    struct_def = StructEntry(struct_alignment,struct_size,member_entries)
    type_table[struct_decl.tag]=struct_def
    print('return func')
    return 

def to_signed_8bit(x) :
    return ((x + 128) % 256) - 128

def create_static_init_list(init_type, initializer, type_table):
  
    if isinstance(init_type, Structure) and isinstance(initializer, CompoundInit):
        struct_def = type_table.get(init_type.tag)
        init_list = initializer.init_list

        if len(init_list) > len(struct_def.members):
            raise Exception("Too many elements in structure initializer")

        current_offset = 0
        static_inits = []
        i = 0

        for init_elem in init_list:
            member = struct_def.members[i]

            # Step 2: Insert padding zeroes if needed
            if member.offset != current_offset:
                static_inits.append(ZeroInit(member.offset - current_offset))

            # Step 3: Recursively build the init list for this member
            more_static_inits = create_static_init_list(member.type, init_elem, type_table)
            static_inits.extend(more_static_inits)

            current_offset = member.offset + size(member.type, type_table)
            i += 1

        # Step 4: Pad to full struct size if necessary
        if struct_def.size != current_offset:
            static_inits.append(ZeroInit(struct_def.size - current_offset))

        return static_inits

def typecheck_file_scope_variable_declaration(decl: VarDecl, symbols: dict,type_table:dict):
    if isinstance(decl.var_type,Void):
        raise TypeError('cant declare void variables')
    # First, determine the initializer based on whether decl.init is null.
    validate_type_specifier(decl.var_type)
    
    if isinstance(decl.init, Null):
        
        # For a null initializer, extern variables get NoInitializer,
        # while others get a Tentative initializer.
        if isinstance(decl.storage_class, Extern):
            new_init = NoInitializer()
           
        else:
            if not isinstance(decl.var_type,Structure) or decl.var_type.tag in type_table:
                new_init = Tentative()
            else:
                raise TypeError('Cannot declare tentative declaraion of incomplete structure var')
            
    else:
        if isinstance(decl.var_type,Structure) and  decl.var_type.tag not in type_table:
            raise TypeError('cannot initialize incomplete structures')
        
        if isinstance(decl.var_type,Void):
            raise TypeError('cannot declare void variables')
        # When there is a non-null initializer, typecheck based on variable type.
        if isinstance(decl.var_type, Array):
            validate_type_specifier(decl.var_type)
            # Handle array initialization (including string literals)
            if isinstance(decl.init, SingleInit) and isinstance(decl.init.exp, String):
            
                # Handle string literal initialization for global arrays
                
                string_val = decl.init.exp.string
                array_size = decl.var_type._int.value._int
                char_type = decl.var_type._type
                
                # Validate character type
                if not isinstance(char_type, (Char, SChar, UChar)):
                    raise TypeError('String literal can only initialize character arrays')
                
                # Check array size vs string length
                
                str_len = len(string_val)
                
                needs_null_term = array_size > str_len
                print('sub 2')
                pad_bytes = array_size - (str_len + 1) if needs_null_term else array_size - str_len
                
                if str_len > array_size:
                    raise ValueError('String literal too long for array')
                
                # Create initializer
                init_list = [StringInit(string_val, needs_null_term)]
               
                if pad_bytes > 0:
                    init_list.append(ZeroInit(pad_bytes))

                new_init = Initial(init_list)
            elif not isinstance(decl.init, CompoundInit):
                raise ValueError("Array initializer must be a CompoundInit or StringLiteral")
            else:
            
                typecheck_init(decl.var_type, decl.init, symbols,type_table)
                # print(init)
                new_init = Initial(typecheck_array_init(decl.init, decl.var_type))
                # print(new_init)
                # exit()
                # exit
        
        elif isinstance(decl.var_type, Pointer):
            if ((hasattr(decl.init, 'exp') and hasattr(decl.init.exp, 'exp') and 
                   isinstance(decl.init.exp.exp, Constant) and int(decl.init.exp.exp.value._int) == 0) or
                  (hasattr(decl.init, 'exp') and isinstance(decl.init.exp, Constant) and 
                   int(decl.init.exp.value._int) == 0)):
                new_init = Initial([Constant(StaticInit.ULongInit(Const.constULong(0)))])
                
            elif not isinstance(decl.init, (Null, AddOf)):
                new_init = Initial(typecheck_init(decl.var_type, decl.init, symbols))
                print('ERROR HERE')
                
                # Check for char* to signed char* conversion
                if (isinstance(decl.var_type.ref, (SChar, UChar)) and 
                    isinstance(new_init.value.exp.get_type().ref, Char)):
                    raise TypeError(
                        f"Cannot implicitly convert char* to {decl.var_type.ref.__class__.__name__}*"
                    )
                
                # General pointer type mismatch check
                if (not isinstance(new_init.value.exp.get_type(), Pointer) or
                    not isinstance(decl.var_type.ref, type(new_init.value.exp.get_type().ref))):
                    raise TypeError(
                        f"Cannot convert {new_init.value.exp.get_type()} to {decl.var_type}"
                    )
            # Handle pointer initialization (including string literals)
            elif isinstance(decl.init, SingleInit) and isinstance(decl.init.exp, String):
                # Handle string literal initialization for global pointers
                if not isinstance(decl.var_type.ref, Char):
                    raise TypeError('String literal can only initialize char*')
                
                # Generate unique name for the string constant
                string_id = f"string.{len([k for k in symbols if k.startswith('string.')])}"
                string_val = decl.init.exp.string
                
                # Add string constant to symbol table
                symbols[string_id] = {
                    'type': Array(Char(), len(string_val) + 1),
                    'val_type': Array(Char(), len(string_val) + 1),
                    'attrs': ConstantAttr(StringInit(string_val, True)),
                    'ret': None,
                    'Double': None
                }
                
                # Create pointer initializer pointing to the string constant
                new_init = Initial([PointerInit(string_id)])
            elif isinstance(decl.var_type, Pointer) and isinstance(decl.var_type.ref, Array):
                validate_type_specifier(decl.var_type.ref)
                # Handle pointer-to-array initialization
                if isinstance(decl.init, AddOf) and isinstance(decl.init.exp, String):
                    string_length = len(decl.init.exp.value) + 1  # +1 for null terminator
                    array_size = decl.var_type.ref._int.value._int
                    
                    if string_length != array_size:
                        raise TypeError(
                            f'String length {string_length} does not match array size {array_size} '
                            f'for pointer to array of type {decl.var_type}'
                        )
            elif (not isinstance(decl.init, Null) and (not isinstance(decl.init, AddOf) and 
                  isinstance(decl.storage_class, Static))):
                raise ValueError('Static pointer initialized with non-pointer value.')
            # Allow a constant 0 pointer initializer
            elif ((hasattr(decl.init, 'exp') and hasattr(decl.init.exp, 'exp') and 
                  isinstance(decl.init.exp.exp, Constant) and int(decl.init.exp.exp.value._int) == 0) or
                 (hasattr(decl.init, 'exp') and isinstance(decl.init.exp, Constant) and 
                  int(decl.init.exp.value._int) == 0)):
                new_init = Initial([Constant(StaticInit.ULongInit(Const.constULong(0)))])
            else:
                # For other pointer cases, fall back to the general initializer typecheck
                new_init = Initial(typecheck_init(decl.var_type, decl.init, symbols,type_table))
        
        elif isinstance(decl.var_type,Structure):
            new_init = Initial(create_static_init_list(decl.var_type,decl.init,type_table))
        
        elif hasattr(decl.init, 'exp') and isinstance(decl.init.exp, Constant):
           
            # Handle scalar constant initializers
            init_val = decl.init.exp.value._int
            if isinstance(decl.var_type, Int):
                new_init = Initial([Constant(StaticInit.IntInit(Const.constInt(int(init_val))))])
            elif isinstance(decl.var_type, (Char, SChar)):
                decl.init.exp.value._int = int( decl.init.exp.value._int)
                if decl.init.exp.value._int > 127:
                    decl.init.exp.value._int = to_signed_8bit(int(decl.init.exp.value._int))
                if decl.init.exp.value._int < -127:
                    decl.init.exp.value._int = int(decl.init.exp.value._int) % -127
                print('iNIT;',decl.init)
                new_init = Initial([Constant(CharInit(decl.init.exp.value))])
              
            elif isinstance(decl.var_type, UChar):
                decl.init.exp.value._int = int( decl.init.exp.value._int)
                
                if decl.init.exp.value._int >255:
                    decl.init.exp.value._int = decl.init.exp.value._int % 256
                new_init = Initial([Constant(UCharInit(decl.init.exp.value))])
            elif isinstance(decl.var_type, UInt):
                new_init = Initial([Constant(StaticInit.UIntInit(Const.constUInt(int(init_val))))])
            elif isinstance(decl.var_type, Long):
                new_init = Initial([Constant(StaticInit.LongInit(Const.constLong(int(init_val))))])
            elif isinstance(decl.var_type, ULong):
                new_init = Initial([Constant(StaticInit.ULongInit(Const.constULong(int(init_val))))])
            elif isinstance(decl.var_type, Double):
                new_init = Initial([Constant(StaticInit.DouleInit(Const.constDouble(float(init_val))))])
            else:
                raise SyntaxError("Unsupported type for constant initializer", decl.storage_class)
        else:
            raise SyntaxError("Non-constant initializer!", decl.storage_class)
       
    # Determine the linkage: globals are those that are not static
    global_scope = not isinstance(decl.storage_class, Static)
    var_name = decl.name.name

    # Check for redeclarations in the symbol table
    if var_name in symbols:
        old_decl = symbols[var_name]
        if type(old_decl['val_type']) != type(decl.var_type) and old_decl['attrs'].global_scope and global_scope:
            raise SyntaxError('Cannot redeclare variable with different type')
        if not isinstance(old_decl['type'], Int):
            raise TypeError("Function redeclared as variable")
        if isinstance(old_decl['val_type'], Array) and isinstance(decl.var_type, Array): 
            validate_type_specifier(decl.var_type)
            if old_decl['val_type']._int.value._int != decl.var_type._int.value._int:
                raise TypeError('Array redeclared with different value')
        
        old_global_scope = old_decl['attrs'].global_scope
        if isinstance(decl.storage_class, Extern):
            final_linkage = old_global_scope
        else:
            if old_global_scope != global_scope:
                raise ValueError("Conflicting variable linkage")
            final_linkage = old_global_scope

        old_init = old_decl['attrs'].init

        def is_initial(i): return isinstance(i, Initial)
        def is_tentative(i): return isinstance(i, Tentative)
        def is_noinit(i): return isinstance(i, NoInitializer)

        if is_initial(old_init):
            if is_initial(new_init):
                raise ValueError("Conflicting file-scope variable definitions")
            else:
                final_init = old_init
        elif is_tentative(old_init):
            if is_initial(new_init):
                final_init = new_init
            else:
                final_init = old_init
        elif is_noinit(old_init):
            if is_initial(new_init) or is_tentative(new_init):
                final_init = new_init
            else:
                final_init = old_init
        else:
            raise RuntimeError("Unknown initializer type in old declaration")
    else:
        final_linkage = global_scope
        final_init = new_init

    attrs = StaticAttr(init=final_init, global_scope=final_linkage)
    symbols[var_name] = {
        'type': Int(),  # placeholder type
        'val_type': decl.var_type,
        'attrs': attrs,
        'ret': decl.var_type,
        'Double': decl.var_type,
    }
    return decl


def zero_initializer(_type):
    if isinstance(_type, Array):
        
        if isinstance(_type._type,(Char,UChar,SChar)):
            # For character arrays, create a string literal with null terminator
            e = SingleInit(String('\0'))
            e.set_type(_type)
            return e
        # For arrays, create compound initializer with proper number of zero elements
        zero_inits = []
        for _ in range(int(_type._int.value._int)):
            zero_inits.append(zero_initializer(_type._type))
            e= CompoundInit(zero_inits)
            e.set_type(_type._type)
        return e
    
    
    elif isinstance(_type,UChar):
        e= SingleInit(Constant(ConstUChar(0),_type=_type))
        e.set_type(_type)
        e.exp.set_type(_type)
        return e 
    elif isinstance(_type,(SChar,Char)):
        e= SingleInit(Constant(ConstChar(0),_type=_type))
        e.set_type(_type)
        e.exp.set_type(_type)
        return e 
        
    elif isinstance(_type,Int):
        e= SingleInit(Constant(ConstInt(0),_type=_type))
        e.set_type(_type)
        e.exp.set_type(_type)
        
        return SingleInit(Constant(ConstInt(0),_type))
    elif isinstance(_type,Long):
        e= SingleInit(Constant(ConstLong(0)))
        e.set_type(_type)
        
        e.exp.set_type(_type)
        
        return e
    elif isinstance(_type,UInt):
        e= SingleInit(Constant(ConstUInt(0),_type))
        e.set_type(_type)
        e.exp.set_type(_type)
        
        return e
    elif isinstance(_type,ULong):
        e= SingleInit(Constant(ConstULong(0),_type))
        e.set_type(_type)
        e.exp.set_type(_type)
        
        return e
    elif isinstance(_type,Double):
        e= SingleInit(Constant(ConstDouble(0),_type))
        e.set_type(_type)
        e.exp.set_type(_type)
        
        return e
    
    elif isinstance(_type,Pointer):
       e = zero_initializer(Long())
    #    e = AddOf(e.exp)
       e.exp.set_type(_type.ref)
       e.set_type(_type)
       print(e)
    #    exit()
       return e
   
    else:
        raise TypeError(f"Unsupported type for zero initialization: {_type}")

x__=0 

def typecheck_init(target_type,init,symbols,type_table):
    if isinstance(target_type,Structure) and isinstance(init,CompoundInit):
        struct_def = type_table.get(target_type.tag) 
        if len(init.initializer) > len(struct_def.members): 
            raise TypeError("Too many elements in structure initializer")
        i = 0
        typechecked_list = []
        init_list = init.initializer
        for init_elem in init_list: 
            t = struct_def.members[i].member_type
            typechecked_elem = typecheck_init(t, init_elem, symbols, type_table)
            typechecked_list.append(typechecked_elem)
            i += 1
        while i < len(struct_def.members): 
            t = struct_def.members[i].member_type
            typechecked_list.append(zero_initializer(t))
            i += 1
        exp = CompoundInit(typechecked_list)
        exp.set_type(target_type)
        return exp 
    if isinstance(target_type,Array) and isinstance(init,SingleInit) and isinstance(init.exp,String):
        validate_type_specifier(target_type)
        if not isinstance(target_type._type,(Char,UChar,SChar)):
            raise TypeError("Can't initialize a non-character type with a string literal")
       
       
     
   
        if init.exp.string.startswith('"'):
            init.exp.string=init.exp.string[1:-1]
     

        if len(init.exp.string)>target_type._int.value._int:
            raise TypeError("Too many characters in string literal")
        print('sub 1')
        init.exp.string= init.exp.string+''.join(['\0'*(target_type._int.value._int - len(init.exp.string) -1)])
        init.exp.set_type(target_type._type)
        init.set_type(target_type)
   
        return init
    if isinstance(target_type,Array) and isinstance(init,CompoundInit):
        validate_type_specifier(target_type)
        if len(init.initializer) > int(target_type._int.value._int):
            
            raise TypeError('Wrong no of valus in initializer')
        typechecked_list = []
        for init_elem in init.initializer:
        
            typechecked_elem = typecheck_init(target_type._type,init_elem,symbols,type_table)
            typechecked_list.append(typechecked_elem)
        
        # print('ERROR HERE 2')
        while len(typechecked_list)<target_type._int.value._int:
            typechecked_list.append(zero_initializer(target_type._type)) 
            init.initializer = typechecked_list
          
        print(len(typechecked_list),target_type._int.value._int)
        print(typechecked_list)
        # exit()
        init.set_type(target_type)
        return init
    if isinstance(init,SingleInit):
        typechecked_exp = typecheck_exp_and_convert(init.exp, symbols,None,type_table=type_table)
        # print(typechecked_exp)
        cast_exp = convert_by_assignment(typechecked_exp, target_type)
        init.exp=cast_exp
        init.exp.set_type(target_type)
        init.set_type(target_type)
        print(init)
        # exit()
       
        return init
      
    else:
       
        raise TypeError("can't initialize a scalar object with a compound initializer")
    

def typecheck_local_variable_declaration(decl: VarDecl, symbols: dict,type_table):
    try:
        
        if isinstance(decl.var_type,Void):
            raise TypeError('cannot declare void variables')
        validate_type_specifier(decl.var_type)
        
        if isinstance(decl.var_type,Structure) and decl.var_type.tag not in type_table:
            if not isinstance(decl.init,Null):
                raise TypeError('cannot init incomplete struct var')
            
        
        # Handle extern declarations
        if isinstance(decl.storage_class, Extern):
            if not isinstance(decl.init, Null):
                raise SyntaxError('Initializer on local extern variable declaration')
            if decl.name.name in symbols:
                old_decl = symbols[decl.name.name]
                if type(old_decl['val_type']) != type(decl.var_type):
                    raise SyntaxError('Cannot redeclare variable with different type')
                if not isinstance(old_decl['type'], Int):
                    raise SyntaxError('Function redeclared as variable')
            else:
                symbols[decl.name.name] = {
                    'type': Int(),
                    'val_type': decl.var_type,
                    'attrs': StaticAttr(init=NoInitializer(), global_scope=True),
                    'ret': decl.var_type,
                    'Double': decl.var_type,
                }
            return decl
      
        # Handle static declarations
        elif isinstance(decl.storage_class, Static):
            if isinstance(decl.var_type, Array) and isinstance(decl.init, SingleInit):
                validate_type_specifier(decl.var_type)
               
                if isinstance(decl.init.exp, String):
                    
                    # Handle string literal initialization for static arrays
                    string_val = decl.init.exp.string
                    array_size = decl.var_type._int.value._int
                    char_type = decl.var_type._type
                    
                    # Validate character type
                    if not isinstance(char_type, (Char, SChar, UChar)):
                        raise TypeError('String literal can only initialize character arrays')
                    
                    if string_val.startswith('"'):
                        string_val = string_val[1:-1]
                
                    # Check array size vs string length
                    str_len = len(string_val)
                    needs_null_term = array_size > str_len
                    print('sub 3')
                    pad_bytes = array_size - (str_len + 1) if needs_null_term else array_size - str_len
                    
                    if str_len > array_size:
                        raise ValueError('String literal too long for array')
                    
                    # Create initializer
                    init_list = [StringInit(string_val, needs_null_term)]
                    if pad_bytes > 0:
                        init_list.append(ZeroInit(pad_bytes))
                    
                    initial_value = Initial(init_list)
                
                    
                else:
                    raise ValueError("Array initializer must be a CompoundInit or StringLiteral")
            
            elif isinstance(decl.var_type, Pointer) and isinstance(decl.init, SingleInit) and isinstance(decl.init.exp,String):
                if isinstance(decl.init.exp, String):
                    # exit()
                    # Handle string literal initialization for static pointers
                    if not isinstance(decl.var_type.ref, Char):
                        raise TypeError('String literal can only initialize char*')
                    
                    # Generate unique name for the string constant
                    string_id = f"string.{len([k for k in symbols if k.startswith('string.')])}"
                    string_val = decl.init.exp.string
                    if string_val.startswith('"'):
                        string_val = string_val[1:-1]
              
                    # Add string constant to symbol table
                    symbols[string_id] = {
                        'type': Array(Char(), len(string_val) + 1),
                        'val_type': Array(Char(), len(string_val) + 1),
                        'attrs': ConstantAttr(StringInit(string_val, True)),
                        'ret': None,
                        'Double': None
                    }
                    
                    # Create pointer initializer pointing to the string constant
                    initial_value = Initial([PointerInit(string_id)])
                
            
            elif isinstance(decl.init, CompoundInit):
                typecheck_init(decl.var_type, decl.init, symbols,type_table)
            
                initial_value = Initial(typecheck_array_init(decl.init, decl.var_type))
                print(initial_value)
             
                    
              
            elif isinstance(decl.init, Null):
                if isinstance(decl.var_type, Array):
                    initial_value = Initial([ZeroInit(decl.var_type._int.value._int * size(decl.var_type._type))])
                
                else:
                    initial_value = Initial([Constant(IntInit(ConstInt(0)))])
            elif isinstance(decl.init,Structure):
                initial_value = Initial(create_static_init_list(decl.var_type,decl.init,type_table))
            elif isinstance(decl.init.exp, Constant):
                print('DECL',decl.init.exp)
                if isinstance(decl.var_type,(Char,SChar)):
                    if decl.init.exp.value._int > 127:
                        
                         decl.init.exp.value._int =  decl.init.exp.value._int % 128
                    if decl.init.exp.value._int < -127:
                         decl.init.exp.value._int =  decl.init.exp.value._int % -127
                  
                    initial_value = Initial([Constant(CharInit(decl.init.exp.value))])
                elif isinstance(decl.var_type,UChar):
                    if decl.init.exp.value._int > 254: 
                         decl.init.exp.value._int =  decl.init.exp.value._int % 254
                    initial_value = Initial([Constant(UCharInit(decl.init.exp.value))])
                elif isinstance(decl.var_type,Int):
                    initial_value = Initial([Constant(IntInit(decl.init.exp.value))])
                elif isinstance(decl.var_type,Long):
                    initial_value = Initial([Constant(LongInit(decl.init.exp.value))])
                elif isinstance(decl.var_type,Double):
                    initial_value = Initial([Constant(DoubleInit(decl.init.exp.value))])
                elif isinstance(decl.var_type,UInt):
                    initial_value = Initial([Constant(UIntInit(decl.init.exp.value))])
                elif isinstance(decl.var_type,ULong):
                    initial_value = Initial([Constant(ULongInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstInt):
                    initial_value = Initial([Constant(IntInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstLong):
                    initial_value = Initial([Constant(LongInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstDouble):
                    initial_value = Initial([Constant(DoubleInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstUInt):
                    initial_value = Initial([Constant(UIntInit(decl.init.exp.value))])
                elif isinstance(decl.init.exp.value,ConstULong):
                    initial_value = Initial([Constant(ULongInit(decl.init.exp.value))])
            
            else:
                raise SyntaxError('Non-constant Initializer on local static variable', decl.init)

            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': StaticAttr(init=initial_value, global_scope=False),
                'ret': decl.var_type,
                'Double': decl.var_type
            }
            return decl
        
        # Handle non-static (local) declarations
        else:
            symbols[decl.name.name] = {
                'type': Int(),
                'val_type': decl.var_type,
                'attrs': LocalAttr(),
                'ret': decl.var_type,
                'Double': decl.var_type
            }
            # print('jere')
            if not isinstance(decl.init, Null):
               
                if isinstance(decl.var_type, Pointer) and isinstance(decl.init, SingleInit):
                    if isinstance(decl.init.exp, String):
                        if not isinstance(decl.var_type.ref, Char):
                            raise TypeError(
                                'String literal can only initialize char* pointers, '
                                f'not {decl.var_type.ref.__class__.__name__}* in local scope'
                            )
                            
           
                if isinstance(decl.var_type, Pointer) and isinstance(decl.var_type.ref, Array) and isinstance(decl.init,SingleInit):
                    validate_type_specifier(decl.var_type.ref)
                    # Handle pointer-to-array initialization
                    if isinstance(decl.init.exp, AddOf) and isinstance(decl.init.exp.exp, String):
                        string_val = decl.init.exp.exp.string
                    
                        if string_val.startswith('"'):
                            string_val = string_val[1:-1]

                        # Calculate the actual length in memory (escape sequences count as single chars)
                        # First decode escape sequences to get the real length
                        import ast
                        try:
                            # Use ast.literal_eval to properly interpret escape sequences
                            decoded_string = ast.literal_eval(f'{string_val}')
                            string_length = len(decoded_string) + 1  # +1 for null terminator
                        except (ValueError, SyntaxError):
                            # Fallback if literal_eval fails
                            decoded_string = string_val.encode().decode('unicode-escape')
                            string_length = len(decoded_string) + 1

                        # Get the array size from type definition
                        # string_length = len(string_val)
                        print(string_val)
                        print(string_length)
                        array_size = decl.var_type.ref._int.value._int
                        # exit()
                        if string_length != array_size:
                            raise TypeError('Invalid string length')
                if isinstance(decl.var_type, Pointer) and isinstance(decl.var_type.ref, Array):
                    validate_type_specifier(decl.var_type.ref)
                    if isinstance(decl.init.exp, AddOf):
                        if isinstance(decl.init.exp.exp,Var):
                            if decl.init.exp.exp.identifier.name in symbols:
                                if decl.var_type.ref._int.value._int != symbols[decl.init.exp.exp.identifier.name]['val_type']._int.value._int:
                                    raise TypeError('Array redeclared with different value')
                
                if isinstance(decl.var_type, Pointer) and isinstance(decl.init.exp, Constant):
                    if isinstance(decl.init.exp.value._type, Double):
                        raise ValueError('Pointer initialized with double value')
                    
                if isinstance(decl.var_type,Array) and isinstance(decl.init,SingleInit) and not isinstance(decl.init.exp,String):
                    raise TypeError("can't initialize an array with a scalar expression.")
           
                if isinstance(decl.var_type,Pointer) and isinstance(decl.var_type.ref,SChar):
                    if isinstance(decl.init.exp,Var):
                        val_type = symbols[decl.init.exp.identifier.name]['val_type']
                        if isinstance(val_type,Pointer) and not isinstance(decl.var_type.ref,type(val_type.ref)):
                            raise TypeError("cannot convert char * to a signed char *")
                x = typecheck_init(decl.var_type, decl.init, symbols,type_table)
               
                if isinstance(decl.var_type, Pointer) and (
                    (isinstance(x, Constant) or isinstance(x, Var)) and
                    not isinstance(x.get_type(), Pointer)):
                    if (not isinstance(x.get_type(), Int)) and (not isinstance(decl.var_type.ref, type(x.get_type()))):
                        raise ValueError('Invalid pointer init')
                    if isinstance(x.get_type(), Int) and isinstance(x, Var):
                        raise ValueError('Invalid pointer init')
                        
                if isinstance(decl.init, AddOf) and not isinstance(decl.init.exp, Var):
                    raise ValueError('Invalid l value')
                decl.init = x
                decl.init = convert_to(decl.init, decl.var_type)
               
            return decl
                
    except Exception as e:
        raise e


def is_complete(t, type_table=None):
    # if type_table is not None:
    if isinstance(t,Structure):
        if  type_table is None :
            raise TypeError('did not get typetable')
        elif t.tag in type_table:
            return True
        else:
            return False
    else:    
        return not isinstance(t,Void)

def is_pointer_to_complete(t):
    if isinstance(t,Pointer):
        return is_complete(t.ref)
    return False

def check_fun_decl_compatibility(decl, old_decl):

    """
    Compares the new function declaration (decl) against the previous declaration (old_decl)
    and raises SyntaxError if there are mismatches in parameter types.
    
    Redeclaration rules:
      - For an array parameter, the outermost dimension is ignored (adjusted to a pointer).
      - For one-dimensional array parameters, any difference in the outer size is ignored.
      - For multi-dimensional arrays, the inner dimensions must match.
    
    Example:
      int array_param(int a[5]);         // adjusted to int (*a)[ ]
      int array_param(int a[2]);         // OK: outer dimension ignored
      
      int nested_array_param(int a[2][3]);    // adjusted to int (*a)[3]
      int nested_array_param(int (*a)[3]);      // must match inner dimension (3)
    """
    new_fun_type = decl.fun_type
    old_fun_type = old_decl['fun_type']
    
    if new_fun_type.param_count != old_fun_type.param_count:
        raise SyntaxError("Function parameter count mismatch: "
                          f"{new_fun_type.param_count} vs {old_fun_type.param_count}")
    
    for new_param, old_param in zip(new_fun_type.params, old_fun_type.params):
        # If the new parameter is declared as an Array, its outer dimension is ignored.
        if isinstance(new_param, Array):
            
            validate_type_specifier(new_param)
            # Adjust the new parameter: the effective type is the element type.
            new_adjusted = new_param._type  # For a parameter declared as int a[5],
                                            # new_adjusted is Int (or, in the multidimensional case, Array(...))
            # The old parameter should be a Parameter whose type is a Pointer.
            if not (isinstance(old_param, Parameter) and isinstance(old_param._type, Pointer)):
                raise SyntaxError("Function parameter mismatch: expected old parameter to be a pointer type.")
            old_adjusted = old_param._type.ref  # This is what the pointer points to.
            
            # For one-dimensional arrays, we ignore any size differences.
            if not isinstance(new_adjusted, Array):
                
                # Compare element types.
                if not isinstance(new_adjusted,type(old_adjusted)):
                    raise SyntaxError("Function parameter type mismatch: "
                                      f"new element type {new_adjusted} vs old element type {old_adjusted}")
            else:
                # For multi-dimensional arrays, compare the inner array sizes.
                new_inner_size = new_adjusted._int.value._int
                if not isinstance(old_adjusted, Array):
                    raise SyntaxError("Function parameter mismatch: new parameter is multi-dimensional but old parameter is not.")
                old_inner_size = old_adjusted._int.value._int
                if new_inner_size != old_inner_size:
                    raise SyntaxError("Function is defined with different inner array parameter sizes: "
                                      f"new inner size {new_inner_size} vs old inner size {old_inner_size}")
        # If the new parameter is already a Parameter (not declared as an array)
        elif isinstance(new_param, Parameter):
            print(new_param._type)
            print(old_param._type)
            if not isinstance(new_param._type,type( old_param._type)):
                raise SyntaxError("Function parameter type mismatch: "
                                  f"new type {new_param._type} vs old type {old_param._type}")
      

def typecheck_function_declaration(decl: FunDecl, symbols: dict, is_block_scope,type_table:dict):
    if isinstance(decl.fun_type,FunType) and isinstance(decl.fun_type.base_type,Array):
    
        raise TypeError('Function type cannot be an array')
    if isinstance(decl.fun_type,Structure):
        if decl.fun_type.tag not in type_table:
            if not isinstance(decl.body,Null):
                print(decl.fun_type)
                exit()
                raise TypeError('Function with incomplete structure type cannot return a value')
            
    
    adjusted_params = []
 
    for param in decl.params:
  
        param_name = param.name.name
        if isinstance(param._type,Structure):
            if param._type.tag not in type_table:
                if not isinstance(decl.body,Null):
                    print(decl.fun_type)
                    # exit()
                    raise TypeError('Function with incomplete structure as params type cannot return a value')
                    
            adjusted_params.append(Parameter(adjusted_type,name=Identifier(param_name)))

            
        elif isinstance(param._type,Array):
            
            validate_type_specifier(param._type)
            
            adjusted_type = Pointer(param._type._type)
        
            adjusted_params.append(Parameter(adjusted_type,name=Identifier(param_name)))
            
        elif isinstance(param._type,Pointer):
            
                validate_type_specifier(param._type)
             
                adjusted_params.append(param)

        else:
            
            if isinstance(param._type,Void):
                
                raise TypeError('Void type parameter not allowed.')
            
            adjusted_params.append(param)
            
       
    decl.params=adjusted_params

    fun_name = decl.name.name
    
    fun_type = FunType(param_count=len(decl.params), params=decl.params, base_type=decl.fun_type.base_type)
    
    has_body = decl.body is not None and not isinstance(decl.body, Null)
    
    already_defined = False
    
    _global = decl.storage_class
    
    if not isinstance(_global, Static):
        
        _global = True
        
    else:
        
        _global = False


    if fun_name in symbols:
        
        old_decl = symbols[fun_name]
        
        check_fun_decl_compatibility(decl, old_decl)
           
        if 'fun_type' not in old_decl:
            
            raise SyntaxError(f"Identifier '{fun_name}' previously declared as a variable.")
        
        already_defined = old_decl['attrs'].defined

        if old_decl['fun_type'].param_count != fun_type.param_count:
            
            raise SyntaxError(
                
                f"Incompatible function declarations for '{fun_name}'. "
                f"Expected {old_decl['fun_type'].param_count} parameters, got {fun_type.param_count}."
                
            )
            

        if type(old_decl['fun_type'].base_type) != type(fun_type.base_type):
            raise SyntaxError(f"Function '{fun_name}' has conflicting return types.")
        old_decl_params = [param._type for param in old_decl['fun_type'].params]
        new_decl_params = [param._type for param in decl.params]
        for i in range(len(old_decl_params)):
            if not (type(old_decl_params[i]) == type(new_decl_params[i])):
                raise SyntaxError("Function is defined with diff params")

        if already_defined and has_body:
            raise SyntaxError("Function is defined more than once")

        if old_decl['attrs'].global_scope and isinstance(decl.storage_class, Static):
            raise SyntaxError('Static funtion declaration follow a non static ')

        if is_block_scope:
            if _global and isinstance(decl.storage_class, Static):
                raise SyntaxError('a block-scope function may only have extern storage class')

        _global = old_decl['attrs'].global_scope
        attrs = FunAttr(defined=(already_defined or has_body), global_scope=_global)
        symbols[fun_name] = {
            'fun_type': FunType(param_count=len(decl.params), params=decl.params, base_type=decl.fun_type.base_type),
            'attrs': attrs
        }

        if has_body:
            for param in decl.params:
                param_name = param.name.name
               
                if param_name in symbols:
                    
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                
                symbols[param_name] = {'type': Int(),'val_type':param._type,'ret':fun_type.base_type,'attrs':None}
                
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                  
                    typecheck_statement(decl.body, symbols, fun_type.base_type,type_table)
                    
                else:
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp_and_convert(stmt.exp, symbols, fun_type.base_type,type_table) 
                        convert_to(typed_return, decl.fun_type)
    else:
      
        if is_block_scope:
            if not _global and isinstance(decl.storage_class, Static):
                raise SyntaxError('a block-scope function may only have extern storage class')
        
        symbols[fun_name] = {
            'fun_type': FunType(param_count=len(decl.params), params=decl.params, base_type=decl.fun_type.base_type),
            'attrs': FunAttr(defined=has_body, global_scope=_global)
        }

        if has_body:
            
           
            for param in decl.params:
                print(param.name)
                #
                param_name = param.name.name

             
                if param_name in symbols:
                    raise SyntaxError(f"Parameter '{param_name}' is already declared.")
                symbols[param_name] = {'type': Int(), 'val_type':param._type,'ret': decl.fun_type,'attrs':None,'Double':param._type}
            # decl.params=adjusted_params
            stmts=[]
            for stmt in decl.body:
                if not isinstance(stmt, Return):
                    print('\nType checking statement',stmt,decl.fun_type.base_type)  
                    typecheck_statement(stmt, symbols, decl.fun_type.base_type,type_table)
                    print('\nType checking statement end',stmt,decl.fun_type.base_type)  
                 
                  
                else:
                    print('Found return')
                 
                    if stmt.exp is not None and not isinstance(stmt.exp, Null):
                        typed_return = typecheck_exp_and_convert(stmt.exp, symbols, decl.fun_type.base_type,type_table)
                        cast=convert_to(typed_return, decl.fun_type)
                        stmts.append(cast)
    
def validate_type_specifier(t):
    if isinstance(t,Array):
        if not is_complete(t._type):
            raise TypeError('Illegal array declaration of incomplete type')
        validate_type_specifier(t._type)
    if isinstance(t,Pointer):
        validate_type_specifier(t.ref)
    
    if isinstance(t,FunType):
        for param in t.params:
            validate_type_specifier(param._type)
        validate_type_specifier(t.base_type)        
    return                 
def typecheck_exp(e: Exp, symbols: dict, func_type=Optional,type_table=None):
    # print(e)
    # 
    """
    Type checks an expression node 'e', possibly skipping if we've visited it already.
    """
    # -------------------------------------------------------------------------
    # 1) If we've already typed this node in the same pass, skip re-check
    # -------------------------------------------------------------------------
  

    # -------------------------------------------------------------------------
    # 2) Actual type-checking logic
    # -------------------------------------------------------------------------
    if isinstance(e, FunctionCall):
            
        fun_name = e.identifier.name
        if fun_name not in symbols:
            raise NameError(f"Function '{fun_name}' is not defined.")
        fun_entry = symbols[fun_name]
        for arg, param in zip(e.args, symbols[e.identifier.name]['fun_type'].params):
            print('Here')
            if isinstance(arg, AddOf) and isinstance(symbols[arg.exp.identifier.name]['val_type'], Array):
                validate_type_specifier(symbols[arg.exp.identifier.name]['val_type'])
                # print(param.)
                # exit()
                if isinstance(param._type, Pointer) and isinstance(param._type.ref, Pointer):
                    # print(symbols[arg.exp.identifier.name]['val_type'])
                    if not isinstance(param._type.ref, type(symbols[arg.exp.identifier.name]['val_type'])):
                        # print('here')
                        raise ValueError('Invalid pointer type')


      
        if not isinstance(fun_entry.get('fun_type'), FunType):
            raise SyntaxError(f"Variable '{fun_name}' used as a function.")

        f_type: FunType = fun_entry['fun_type']
       
        if f_type.param_count != len(e.args):
            raise SyntaxError(
                f"Function '{fun_name}' called with wrong number of arguments. "
                f"Expected {f_type.param_count}, got {len(e.args)}."
            )

        converted_args = []
        params = [val._type for val in f_type.params]
        for (arg, paramType) in zip(e.args, params):
            typed_arg = typecheck_exp_and_convert(arg, symbols,func_type,type_table)  
            print('Typed arg',typed_arg)
            print('Param type',paramType)
            if isinstance(paramType,Pointer):
                converted_args.append(convert_by_assignment(typed_arg, paramType))
            else:
                converted_args.append(convert_by_assignment(typed_arg, paramType))
                
            print('Converted args',converted_args)
        e.args = converted_args
        e.set_type(f_type.base_type)
        print('Type checked function call')
        return e
    elif isinstance(e,String):
        if e.string.startswith('"'):
            e.string = e.string[1:-1]
        e.set_type(Array(_type=Char(),_int=len(e.string)+1))
        return e 
    elif isinstance(e, Var):
        var_name = e.identifier.name
        # print(var_name)
        # print(symbols[e.identifier.name])
        if var_name not in symbols:
            raise NameError(f"Variable '{var_name}' is not defined.")
        var_entry = symbols[var_name]
       
        if 'type' not in var_entry:
            raise SyntaxError(f"Function '{var_name}' used as a variable.")

        var_type = var_entry['type']
        if not isinstance(var_type, Int):
            raise SyntaxError(f"Identifier '{var_name}' does not have type Int.")
        e.set_type(var_entry['val_type'])
       
        return e

    elif isinstance(e, Return):
        # 
        global x
        if x==1:
            print('\nReturn Expression',e,func_type)
        x+=1
        if not isinstance(func_type,Void) and isinstance(e.exp,Null):
            raise TypeError('none Void function must return a value')
            
        
        if not isinstance(e.exp,Null) and isinstance(func_type,Void):
            raise TypeError('Void function cannot return a value')
        if e.exp is not None and not isinstance(e.exp, Null):
            if func_type is not None:
               
                e.exp=typecheck_exp_and_convert(e.exp, symbols, func_type,type_table) 
              
                e.exp=convert_by_assignment(e.exp, func_type)
                
                return e

        return e

    elif isinstance(e, Constant):
        if isinstance(e.value, ConstInt):
            e.set_type(Int())
            
            return e
        elif isinstance(e.value, ConstLong):
         
            e.set_type(Long())
            return e
        elif isinstance(e.value, ConstULong):
            
            e.set_type(ULong())
            return e
        elif isinstance(e.value, ConstUInt):
            e.set_type(UInt())
            return e 
        elif isinstance(e.value,ConstDouble):
            e.set_type(Double())
            return e
        else:
            raise SyntaxError('Invalid value const')

    elif isinstance(e, Cast):
        # print(e.exp)
        validate_type_specifier(e.target_type)
        # exit()
        typed_inner = typecheck_exp_and_convert(e.exp, symbols)
        e.exp = typed_inner
        
        
        if( isinstance(e.target_type,Pointer) and isinstance(typed_inner.get_type(),Double))or ( 
            isinstance(e.target_type,Double) and isinstance(typed_inner.get_type(),Pointer)):
            raise SyntaxError('Cannot cast pointer to double / double to a pointer')
        
        if isinstance(e.target_type,Void):
            e.set_type(Void())
            
            return e 
        
        if not is_scalar(e._type):
            # print(e.target_type)
            # print(e.exp.get_type())
            raise TypeError('Can only cast to scalar type or void')
        if not is_scalar(e.exp.get_type()):
            raise TypeError('Cannot cast non-scalar expression to scalar type')

          
        e.set_type(e.target_type)
        return e

    elif isinstance(e, Assignment):
        # exit()
        
        type_left = typecheck_exp_and_convert(e.left, symbols,func_type,type_table)
        type_right = typecheck_exp_and_convert(e.right, symbols,func_type,type_table)
        
       
        left_type = type_left.get_type()
        if isinstance(type_right.get_type(),Void) and not isinstance(left_type,Void):
            raise TypeError('cannot assign void type to scalar')
        if isinstance(type_left,AddOf) and isinstance(type_left.exp._type,Array) :
            raise ValueError('Cannot assign to array')    
        
        if  isinstance(type_left.get_type(),Pointer) and isinstance(type_right.get_type(),Pointer):
            print()
            if (type(type_left.get_type().ref)!=type(type_right.get_type().ref)) and (not isinstance(type_left.get_type().ref,Void) and not isinstance(type_right.get_type().ref,Void)):
                print(type_left.get_type().ref)
                print(type_right.get_type().ref)
                raise SyntaxError('Cannot assign one pointer type to another')
    
        converted_right = convert_by_assignment(type_right, left_type)
        e.left = type_left
        e.right = converted_right
        e.set_type(left_type)
        return e

    elif isinstance(e, Binary):
  
        if e.operator in (BinaryOperator.EQUAL,BinaryOperator.NOT_EQUAL):
            typed_e1 = typecheck_exp_and_convert(e.left, symbols,func_type,type_table)
            typed_e2 = typecheck_exp_and_convert(e.right, symbols,func_type,type_table)
            t1 = typed_e1.get_type()
            t2 = typed_e2.get_type()
         
           
            if isinstance(t1,Pointer) or isinstance(t2,Pointer):
              
                common_type = get_common_pointer_type(typed_e1, typed_e2)
            
            elif is_scalar(t1) and is_scalar(t2):
                common_type = get_common_type(t1, t2)
            else:
                raise TypeError("Invalid operands to equality expression")
            converted_e1 = convert_to(typed_e1, common_type)
            converted_e2 = convert_to(typed_e2, common_type)

            e.left=converted_e1
            e.right=converted_e2
          
            e.set_type(Int())
            
            return e
      
        else:
           
            typed_e1 = typecheck_exp_and_convert(e.left, symbols,func_type,type_table)
            typed_e2 = typecheck_exp_and_convert(e.right, symbols,func_type,type_table)
            
            if not is_scalar(typed_e1.get_type()) or not is_scalar(typed_e2.get_type()):
                    raise TypeError("Invalid operands to equality expression")
            
            if e.operator in (BinaryOperator.MULTIPLY, BinaryOperator.DIVIDE, BinaryOperator.REMAINDER):
                if not is_scalar(typed_e1.get_type()) or not is_scalar(typed_e2.get_type()):
                    raise TypeError("Invalid operands to equality expression")
                if isinstance(typed_e1.get_type(),Pointer) or isinstance(typed_e2.get_type(),Pointer):
                    raise SyntaxError('Cannot perform mul, divide , modulo arithmetic operations on pointers')
            if e.operator in (BinaryOperator.EQUAL,BinaryOperator.GREATER_OR_EQUAL,
                                   BinaryOperator.GREATER_THAN,
                                   BinaryOperator.LESS_OR_EQUAL,
                                   BinaryOperator.LESS_THAN,BinaryOperator.NOT_EQUAL):
                if (isinstance(typed_e1.get_type(),Pointer) and not 
                    isinstance(typed_e2.get_type(),Pointer)) or (
                    isinstance(typed_e2.get_type(),Pointer) and 
                    not isinstance(typed_e1.get_type(),Pointer)):
                    raise SyntaxError('Cannot perform comparison between on pointer and non pointer')
                
                
            if e.operator in (BinaryOperator.AND, BinaryOperator.OR):
                e.left = typed_e1
                e.right = typed_e2
                e.set_type(Int())
                e.rel_flag = Int()
                
                return e
                
        
            t1 = typed_e1.get_type()
            t2 = typed_e2.get_type()
            
            if (isinstance(t1,Pointer) and isinstance(t2,Pointer)) and e.operator in (BinaryOperator.GREATER_OR_EQUAL,
                                                                                       BinaryOperator.GREATER_THAN,
                                                                                       BinaryOperator.LESS_OR_EQUAL,
                                                                                       BinaryOperator.LESS_THAN):
                    if isinstance(t1.ref,type(t2.ref)):
                        
                        e.set_type(Int())
                        e.rel_flag=Int()
                        return e 
                    else:
                        raise ValueError('Pointer of two different types cannot be used for relational op')
                
            
            if (((isinstance(t1,Pointer) and is_pointer_to_complete(t1)) and not isinstance(t2,Pointer)) and e.operator in (BinaryOperator.ADD,BinaryOperator.SUBTRACT)):
                if isinstance(t2,Double):
                    raise ValueError('Cannot add / substract double form a pointer')
               
                converted_e2 = convert_to(typed_e2, Long())
                e=Binary(e.operator,typed_e1,converted_e2)
                e.set_type(t1)
                e.rel_flag=Long()
                return e
            elif ((not isinstance(t1,Pointer) and  (isinstance(t2,Pointer) and is_pointer_to_complete(t2))) and e.operator == BinaryOperator.ADD):
                converted_e1 = convert_to(typed_e1, Long())
                e=Binary(e.operator,converted_e1,typed_e2)
                e.rel_flag=Long()
                e.set_type(t2)
                return e
            elif (((isinstance(t1,Pointer) and is_pointer_to_complete(t1)) and isinstance(t1.ref,type(t2.ref))) and e.operator == BinaryOperator.SUBTRACT):
                
                print(isinstance(t2.ref,type(t2.ref)))
            
             
                
                e=Binary(operator=e.operator,left=typed_e1,right=typed_e2)
                e.set_type(Long())
                e.rel_flag=Long()
                return e           
            elif not isinstance(t1,Pointer) and not isinstance(t2,Pointer):
                if e.operator==BinaryOperator.REMAINDER :
                    if isinstance(t1,Double) or isinstance(t2,Double):
                        raise ValueError('Cannot apply modulo to a double')
        
                
                common_type = get_common_type(t1, t2)
                
                converted_e1 = convert_to(typed_e1, common_type)
                converted_e2 = convert_to(typed_e2, common_type)
                e.left = converted_e1
                e.right = converted_e2

                if e.operator in (BinaryOperator.ADD, BinaryOperator.DIVIDE,
                                BinaryOperator.MULTIPLY, BinaryOperator.SUBTRACT,
                                BinaryOperator.REMAINDER):
                    e.rel_flag = common_type
                    e.set_type(common_type)
                
                    return e 
                else:
                    if isinstance(e.left.get_type(),Double):
                        e.rel_flag =Int()
                        print(e)
                        
                        e.set_type(Int())
                    else:
                        e.rel_flag = Int()
                        e.set_type(Int())
                    return e
            else:
                raise ValueError('Invalid value for operands')
    
    elif isinstance(e, Unary):
        inner = typecheck_exp_and_convert(e.expr, symbols,func_type,type_table)
        if not is_scalar(inner.get_type()):
            raise TypeError("Logical operators can only be applied to scalar expressions")
        e.expr = inner
        if e.operator == UnaryOperator.NOT:
            e.set_type(Int())
            return e
        if e.operator==UnaryOperator.COMPLEMENT :
            if isinstance(e.expr.get_type(),(Double,Pointer)):
                raise SyntaxError('Cannot complement of double')
            if isinstance(e.expr.get_type(),(Char,SChar,UChar)):
                e.expr = convert_to(e.expr,Int())
            e.set_type(e.expr.get_type())
        elif e.operator == UnaryOperator.NEGATE:
            if isinstance(e.expr.get_type(),Pointer):
                raise SyntaxError('Cannot negate a pointer')
            if isinstance(e.expr.get_type(),(Char,SChar,UChar)):
                e.expr = convert_to(e.expr,Int())
            e.set_type(e.expr.get_type())
        else:
            if isinstance(inner.get_type(),Pointer):
                e.set_type(inner.get_type().ref)
            else:
                e.set_type(inner.get_type())
        return e

    elif isinstance(e, Conditional):
        typed_condition = typecheck_exp_and_convert(e.condition, symbols,func_type,type_table) if e.condition else None
        typed_exp2 = typecheck_exp_and_convert(e.exp2, symbols,func_type,type_table) if e.exp2 else None
        typed_exp3 = typecheck_exp_and_convert(e.exp3, symbols,func_type,type_table) if e.exp3 else None
        if not is_scalar(typed_condition.get_type()):
            raise TypeError('Condition in conditional operator must be scalar')
        if typed_exp2 is None or typed_exp3 is None:
            raise SyntaxError("Malformed Conditional expression")

        t2 = typed_exp2.get_type()
        t3 = typed_exp3.get_type()
        # exit()
        if isinstance(t2,Void) and isinstance(t3,Void):
            common_type = Void()
        elif isinstance(t2,Void) or isinstance(t3,Void):
            raise TypeError("Cannot convert branches of conditional to a common type")
            
        elif isinstance(t2,Pointer) or isinstance(t3,Pointer):
            common_type = get_common_pointer_type(typed_exp2, typed_exp3)
        elif not isinstance(t2,Pointer) and not isinstance(t3,Pointer):
            common_type = get_common_type(t2, t3)
        else:
            raise TypeError("Cannot convert branches of conditional to a common type")
        # common_type = get_common_type(t2, t3)
        converted_e2 = convert_to(typed_exp2, common_type)
        converted_e3 = convert_to(typed_exp3, common_type)

        e.condition = typed_condition
        e.exp2 = converted_e2
        e.exp3 = converted_e3
        e.set_type(common_type)
        return e

    elif isinstance(e,Dereference):
        typed_inner = typecheck_exp_and_convert(e.exp, symbols,func_type,type_table)
        print(typed_inner)
        # 
        if not isinstance(typed_inner.get_type(), Pointer):
            raise SyntaxError("Dereference operator applied to non-pointer type")
        if isinstance(typed_inner.get_type().ref,Void):
            raise TypeError('Cannot derefence to void.')
        e.exp=typed_inner
        e.set_type(typed_inner.get_type().ref)
    
        return e
    
    elif isinstance(e, AddOf):
     
        if not isinstance(e.exp, Constant) and isinstance(e.exp, (Var,Subscript,Dereference,String)):
           
            typed_inner = typecheck_exp(e.exp, symbols,func_type,type_table=type_table)
            
       
            referenced_t = typed_inner.get_type()
       
            e.exp= typed_inner
            e.exp.set_type(Pointer(referenced_t))
            e.set_type(Pointer(referenced_t))
            global y_ 
         
            if func_type is not None and isinstance(func_type,Pointer):
                if type(e.get_type().ref) != type(func_type.ref):
                    raise ValueError('Invalid return value')
            return e
        else:
            raise SyntaxError("Address-of operator applied to non-variable")

    elif isinstance(e,Pointer):
        e.set_type(Pointer(e.ref))
        return e
    
    elif isinstance(e, Null):
        return e

    elif isinstance(e,Identifier):
        return typecheck_statement(e.name,symbols,func_type,type_table)
    
    elif isinstance(e,Subscript):
        print('\n',e,'\n')
        typed_e1 = typecheck_exp_and_convert(e.exp1, symbols,func_type,type_table)
        typed_e2 = typecheck_exp_and_convert(e.exp2, symbols,func_type,type_table)
        t1 = typed_e1.get_type()
        t2 = typed_e2.get_type()
        
        if isinstance(t1,Double) or isinstance(t2,Double) :
            raise TypeError("Subscript must have integral type.")

        if isinstance(t1,Void) or isinstance(t2,Void) :
            raise TypeError("Subscript must have integral type.")
        
        if (isinstance(t1,Pointer) and is_pointer_to_complete(t1)) and not isinstance(t2,Pointer):
        # 1 if t1 is a pointer type and t2 is an integer type:
            ptr_type = t1
            typed_e2 = convert_to(typed_e2, Long())
        elif not isinstance(t1,Pointer) and (isinstance(t2,Pointer))and is_pointer_to_complete(t2):
            ptr_type = t2
            typed_e1 = convert_to(typed_e1, Long())
        else:
            raise ValueError("Subscript must have integer and pointer operands")
        e.exp1 = typed_e1
        e.exp2=typed_e2
        e.set_type(ptr_type.ref)
        return e
    
    elif isinstance(e,SizeOf):
     
        typed_inner =typecheck_exp(e.exp,symbols,func_type,type_table)
        if not is_complete(typed_inner.get_type()):
            raise TypeError("Can't get the size of an incomplete type")
        e.exp = typed_inner 
        e.set_type(ULong())
        return e 
    elif isinstance(e,SizeOfT):
        # typecheck_exp(e.exp,symbols)
        validate_type_specifier(e.exp)
        # typed_inner =typecheck_exp(e.exp,symbols,func_type)
        if not is_complete(e.exp):
            raise TypeError("Can't get the size of an incomplete type")
        # e.exp = typed_inner 
        e.set_type(ULong())
        return e

    elif isinstance(e,Dot):
        print('dot expr')
        typed_structure = typecheck_exp_and_convert(e.structure,symbols,func_type,type_table)
        print(typed_structure)
        print(type_table)
        type_s = typed_structure.get_type()
        # exit()
        if isinstance(type_s,Structure):
            # print(type_s.tag)
            # print(type_table)
            # exit()
            print(e.member)
            struct_def:StructEntry = type_table[type_s.tag]
            member_def = None 
            found = False
            for i in struct_def.members:
                if e.member.name == i.member_name.name:
                    member_def = i
                    found = True 
            if found==False :
                raise TypeError('Member not found with the same name')
            member_exp = Dot(typed_structure,e.member)
            member_exp.set_type(member_def.member_type)
            return member_exp
        else:
            raise TypeError("Tried to get member of non-structure")
    elif isinstance(e,Arrow):
        # typed_structure = typecheck_exp_and_convert(e)
        typed_pointer = typecheck_exp_and_convert(e.pointer,symbols,func_type,type_table)
        type_s = typed_pointer.get_type().ref
        if isinstance(type_s,Pointer):
            struct_def:StructEntry = type_table[type_s.tag]
            member_def = None 
            found = False
            for i in struct_def.members:
                if e.member.name == i.member_name.name:
                    member_def = i
                    found = True 
            if found==False :
                raise TypeError('Member not found with the same name')
            member_exp = Arrow(typed_structure,e.member)
            member_exp.set_type(member_def.member_type)
            return member_exp
        else:
            raise TypeError("Tried to get member of non-structure")
        
        
        
        
            
            
    else:
        raise TypeError(f"Unsupported expression type for type checking: {type(e)}, {e}")

def typecheck_statement(statement: Statement, symbols: dict, fun_type=Optional[str],type_table={}):
 
    if isinstance(statement, list):
        for stmt in statement:
            typecheck_statement(stmt, symbols, fun_type,type_table)
        return statement

    if isinstance(statement, VarDecl):
        typecheck_local_variable_declaration(statement, symbols,type_table)

    elif isinstance(statement, InitDecl):
        typecheck_statement(statement.declaration.declaration, symbols, fun_type,type_table)

    elif isinstance(statement, InitExp):
        typecheck_statement(statement.exp, symbols, fun_type,type_table)

    elif isinstance(statement, FunDecl):
        typecheck_function_declaration(statement, symbols, is_block_scope=True,type_table=type_table)

    elif isinstance(statement, (Break, Continue)):
        pass

    elif isinstance(statement, Expression):
        typecheck_exp_and_convert(statement.exp, symbols, fun_type,type_table)

    elif isinstance(statement, (While, For, DoWhile)):
        if isinstance(statement, While):
            typecheck_exp_and_convert(statement._condition, symbols, fun_type,type_table)
            if isinstance(statement._condition.get_type(),Void):
            
                raise TypeError('cannot use void in while conditon exp')
            typecheck_statement(statement.body, symbols, fun_type)
        elif isinstance(statement, For):
            if isinstance(statement.init, InitDecl):
                if statement.init and not isinstance(statement.init, Null):
                    if isinstance(statement.init.declaration.declaration, VarDecl):
                        if isinstance(statement.init.declaration.declaration.storage_class, (Extern, Static)):
                            raise SyntaxError('Loop initializer cannot have storage class')
                        else:
                            typecheck_statement(statement.init, symbols, fun_type,type_table)
                            # if isinstance(statement.init.get_type(),Void):
            
                                    # raise TypeError('cannot use void in if conditon exp')
                            # print(s)
                            # 
            else:
                if not isinstance(statement.init,Null):
                  
                    typecheck_statement(statement.init, symbols, fun_type,type_table)

            if not isinstance(statement.condition,Null):
            
                typecheck_exp_and_convert(statement.condition, symbols, fun_type,type_table)
                if isinstance(statement.condition.get_type(),Void):
                    raise TypeError('cannot use void in for conditon exp')
            if not isinstance(statement.post,Null):
                typecheck_exp_and_convert(statement.post, symbols, fun_type,type_table)
                # if isinstance(statement.post.get_type(),Void):
            
                #     raise TypeError('cannot use void in  conditon exp')
            typecheck_statement(statement.body, symbols, fun_type,type_table)

        elif isinstance(statement, DoWhile):
            typecheck_statement(statement.body, symbols, fun_type,type_table)
            typecheck_exp_and_convert(statement._condition, symbols, fun_type,type_table)
            
            if isinstance(statement._condition.get_type(),Void):
            
                    raise TypeError('cannot use void in do while conditon exp')

    elif isinstance(statement, Compound):
        for stmt in statement.block:
            typecheck_statement(stmt, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, S):
        typecheck_statement(statement.statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, D):
        if isinstance(statement.declaration, FunDecl):
            typecheck_function_declaration(statement.declaration, symbols, is_block_scope=True)
        elif isinstance(statement.declaration, VarDecl):
            typecheck_local_variable_declaration(statement.declaration, symbols,type_table)
        else:
            raise TypeError(f"Unsupported declaration type in D: {type(statement.declaration)}")

    elif isinstance(statement, Conditional):
        typecheck_exp_and_convert(statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, If):
        # print(statement.exp)
        typecheck_exp_and_convert(statement.exp, symbols, fun_type,type_table=type_table)
        if isinstance(statement.exp.get_type(),Void):
            
            raise TypeError('cannot use void in if conditon exp')
        typecheck_statement(statement.then, symbols, fun_type,type_table=type_table)
        if statement._else:
            typecheck_statement(statement._else, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, FunctionCall):
        typecheck_exp_and_convert(statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, Return):
            typecheck_exp(statement, symbols,fun_type,type_table=type_table)

    elif isinstance(statement, (Expression, Assignment, Binary, Unary)):
        typecheck_exp_and_convert(statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, Cast):
        typecheck_exp_and_convert(statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, Var):
        typecheck_exp_and_convert(statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, Constant):
        typecheck_exp_and_convert(statement, symbols, fun_type,type_table=type_table)

    elif isinstance(statement, Null):
        pass

    else:
        raise TypeError(f"Unsupported statement type for type checking: {type(statement)}")

    return statement

def typecheck_program(program: Program):
    # print(structure_map)
    # exit()
    """
    Initiates the type checking process for the entire program.
    """
    symbols = {}
    type_table={}
    for stmt in program.function_definition:
        print('Type checking',stmt)
        if isinstance(stmt, VarDecl):
            print(stmt)
            typecheck_file_scope_variable_declaration(stmt, symbols,type_table)
        elif isinstance(stmt, FunDecl):
            print('Fun decl')
            print(stmt)
            
            typecheck_function_declaration(stmt, symbols, False,type_table)
        elif isinstance(stmt,StructDecl):
            typecheck_structure_decl(stmt,type_table)
            print('after struct decl')
        else:
            typecheck_statement(stmt, symbols,type_table=type_table)
    print('exiting')
    return program, symbols,type_table
