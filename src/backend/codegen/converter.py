

import sys
from typing import Union, List ,Dict,Optional
import time 

PARAMETER_REGISTERS = ['DI', 'SI', 'DX', 'CX', 'R8', 'R9']
from src.backend.ir.tacky import * 
from src.backend.codegen.assembly_ast import * 
from src.frontend.parser._ast5 import  Parameter,Double,UInt,Null,ULong,Int,Long,Structure ,Parameter,ConstDouble,ConstInt,ConstLong,ConstUInt,ConstULong,Pointer,Identifier,Null,Array,Char,SChar,UChar,ConstChar,ConstUChar
from src.backend.typechecker.type_classes import * 
from src.backend.codegen.instruction_fixer import is_signed_32_bit
from src.backend.typechecker.typechecker import isSigned 
from src.backend.typechecker.typechecker import is_scalar
from ..ir.tacky_emiter import get_const_label 
current_param_offset={}
t=0

def align_offset(offset, alignment):
            return offset - (offset % alignment) if offset % alignment != 0 else offset

up_temp = 0
def get_upper_bound():
    global up_temp
    up_temp+=1
    return f'_upper_bound.{up_temp}'

end_temp = 0
def get_end_label():
    global end_temp
    end_temp+=1
    return  f'_end.{end_temp}'


i=1

out_of_rng_temp = 0
def get_out_of_rng():
    global out_of_rng_temp
    out_of_rng_temp+=1
    return f'_out_of_range.{out_of_rng_temp}'


class FunEntry():
    def __init__(self, defined,return_on_stack):
        self.defined=defined 
        self.return_on_stack = return_on_stack
    def __repr__(self):
        return f'FunEntry(defined={self.defined},return_on_stack={self.return_on_stack})'    
    
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
        
class ObjEntry():
    def __init__(self,assembly_type,is_static,is_constant):
        self.assembly_type=assembly_type 
        self.is_static = is_static
        self.is_constant = is_constant
        
        
    def __repr__(self):
        return f'ObjEntry(assembly_type={self.assembly_type}, is_static={self.is_static})'    
    

_i = 0 
class Converter():
    def __init__(self,symbols,type_table):
        self.symbols=symbols
        self.type_table=type_table
        self.temp={}
        self.static_const=[]
        self.ret_in_memory={}
        self.func_name = None 

        
    def get_structure(self,val:TackyVar)->Structure:
        struct = self.symbols[val.identifier]['val_type']
        if not isinstance(struct,Structure):
     
            raise SyntaxError(f'expected a structure got {struct}')
        
        return self.type_table[struct.tag]
        
    def classify_parameters(self,values:List[Parameter],return_in_memory):
        #'inside classify params')
        reg_args=[]
        double_args=[]
        stack_args=[]
        
        # #return_in_memory)
        
        if return_in_memory!=False:
            int_reg_available = 5 
        else:
            int_reg_available = 6

        
        
        for operand in values:
            # #values)
            type_operand = self.get_param_type(operand._type)
           
            if type_operand == AssemblyType.double:
                if len(double_args)<8:
                    double_args.append(operand)
                else:
                    stack_args.append((type_operand,operand))
            elif is_scalar(operand._type):
                if len(reg_args)<int_reg_available:
                    reg_args.append((operand._type,operand))
                else:
                    stack_args.append((operand._type,operand))

            
            
            else:
                # 
                type_operand =operand._type
                type_operand = self.type_table[type_operand.tag]
                classes  = self.classify_structures(type_operand)
                use_stack = True 
                struct_size = type_operand.size 
          
                if classes[0]!=StructMemory.MEMORY:
                    tentative_ints = []
                    tentative_doubles = []
                    offset = 0 
                    for _class in classes:
                        #'Operand',operand)
                        if isinstance(operand,PseudoMem):
                            operand = PseudoMem(operand.identifier,offset)
                        else:
                            operand = PseudoMem(operand.name,offset)
                        if _class == StructMemory.SSE:
                            tentative_doubles.append(operand)
                        else:
                            eightbyte_type = self.get_eightbyte_type(offset,struct_size)
                            # #'uihlaseiuhfgaieu')
                            
                            tentative_ints.append((eightbyte_type, operand))
                        offset += 8
                    if ((len(tentative_doubles) + len(double_args)) <= 8 and
                        (len(tentative_ints) + len(reg_args)) <= int_reg_available): 
                        double_args.extend(tentative_doubles)
                        reg_args.extend(tentative_ints)
                        use_stack = False
                
                if use_stack:
                    offset = 0
                    for _class in classes:
                        if isinstance(operand,PseudoMem):
                            operand = PseudoMem(operand.identifier,offset)
                        else:
                            operand = PseudoMem(operand.name,offset)
                        # operand = PseudoMem(operand.name, offset)
                        eightbyte_type = self.get_eightbyte_type(offset, struct_size)
                        stack_args.append((eightbyte_type, operand)) 
                        offset += 8
                
        #'reg args',reg_args)
        #'double args',double_args)
        #'stack args',stack_args)  
        # 
        return (reg_args,double_args,stack_args)
    
    
    
    def classify_return_val(self,retval):
        # #'classify ret vale')
        # #retval)
        # #self.symbols[retval.identifier])
        # # 
        t = self.get_type(retval)
        
        if isinstance(retval,TackyVar):
            scalar = self.symbols[retval.identifier]['val_type']
            if isinstance(scalar,Array) and isinstance(scalar._type,(Char,UChar,SChar)):
                scalar = Pointer(scalar)
        else:
            scalar = Int()
       
        if t=='Double' or isinstance(t,Double):
            operand = self.convert_to_assembly_ast(retval)
            return ([],[operand],False)
        elif is_scalar(scalar):
            
            typed_operand = self.convert_to_assembly_ast(retval)
        
           
            return ([(t,typed_operand)],[],False)
        else:
            # #self.symbols[retval.identifier])
         
            
            struct = self.get_structure(retval)
            struct_size = struct.size
            classes = self.classify_structures(struct)
            #classes)
            # #
            if classes[0]==StructMemory.MEMORY:
                # #'dobuple')
                return ([()],[],True)
            
            else:
                
                #classes)
                int_retval =[]
                double_retval = []
                offset = 0
                # #int_retval)
                #retval)
                for _class in classes:
                    if isinstance(retval,TackyVar):
                        operand = PseudoMem(retval.identifier,offset)
                    elif isinstance(retval,(PseudoMem,Pseudo)):
                        operand = PseudoMem(retval.identifier,offset)
                    else:
                        operand = PseudoMem(retval.name,offset)
                    #'operand',operand)
                    if _class == StructMemory.SSE:
                        double_retval.append(operand)
                    elif _class == StructMemory.INTEGER:
                        eightbyte_type = self.get_eightbyte_type(offset,struct_size)
                        int_retval.append((eightbyte_type,operand))

                    elif _class == StructMemory.MEMORY:
                        raise MemoryError('internal error')
                    offset+=8
                # #
                # #int_retval)
                # #
                return (int_retval,double_retval,False)
                
            
            
    
    
    def get_eightbyte_type(self,offset,struct_size):
        #'get eight byte type')
        #offset)
        #struct_size)
        # #
        bytes_from_end = struct_size - offset
        if bytes_from_end>=8:
            return AssemblyType.quadWord
        if bytes_from_end==4:
            return AssemblyType.longWord 
        if bytes_from_end==1:
            return AssemblyType.byte 
        return ByteArray(bytes_from_end,8)
        
    def classify_structures(self,struct:StructEntry):
        size = struct.size 
        # #'size',size)
        if size > 16:
            result = []
            while size > 0:
                result.append(StructMemory.MEMORY)
                size -=8 
            return result
        
        scalar_types = [member.member_type for member in struct.members]
        for _type in scalar_types:
            # #_type)
            if isinstance(_type,Array):
                scalar_types.remove(_type)
                cnt = _type._int.value._int
                while cnt>0:
                    
                    scalar_types.append(_type._type)
                    cnt-=1
        
        #scalar_types)
        # #
        if size>8:
            if isinstance(scalar_types[0],Double) and isinstance(scalar_types[-1],Double):
                return [StructMemory.SSE,StructMemory.SSE]
            if isinstance(scalar_types[0],Double):
                return [StructMemory.SSE,StructMemory.INTEGER]
        
            if isinstance(scalar_types[-1],Double):
                return [StructMemory.INTEGER,StructMemory.SSE]
            return [StructMemory.INTEGER,StructMemory.INTEGER]
        if isinstance(scalar_types[0],Double):
                return [StructMemory.SSE]
        
        else:
            return [StructMemory.INTEGER]
                
                

    
    # def classify_arguments(self,values):
    #     reg_args=[]
    #     double_args=[]
    #     stack_args=[]
    
    #     for operand in values:
    #         #operand)
    #         if isinstance(operand,TackyConstant):       
    #             type_operand = self.get_param_type(operand.value._type)
    #         else:
    #             type_operand = self.get_param_type(self.symbols[operand.identifier]['val_type'])
               
           
    #         if type_operand == AssemblyType.double:
    #             if len(double_args)<8:
    #                 double_args.append(operand)
    #             else:
    #                 stack_args.append(operand)
    #         else:
    #             if len(reg_args)<6:
    #                 reg_args.append(operand)
    #             else:
    #                 stack_args.append(operand)
   
    #     return reg_args,double_args,stack_args
            
             
            
    def classify_arguments(self,values,return_in_memory):
        reg_args=[]
        double_args=[]
        stack_args=[]
        # 
        if return_in_memory is not None and return_in_memory == True:
            int_reg_available = 5 
        else:
            int_reg_available = 6
        
        #values)
        # 
        for operand in values:
            
            if isinstance(operand,TackyConstant):       
                type_operand = self.get_param_type(operand.value._type)
            else:
                type_operand = self.symbols[operand.identifier]['val_type']
                if isinstance(type_operand,Array):
                    type_operand = Pointer(type_operand._type)
               
            # #type_operand)
            # if not isinstance(type_operand,TackyConstant):
                #f'found {operand} {type_operand}')
                #values)
                # 
            if isinstance(type_operand,Double) or type_operand == AssemblyType.double:
                if len(double_args)<8:
                    double_args.append(operand)
                else:
                    stack_args.append((type_operand,operand))
            elif is_scalar(type_operand):
                if len(reg_args)<int_reg_available:
                    reg_args.append((type_operand,operand))
                else:
                    stack_args.append((type_operand,operand))

            
            
            else:   
                struct = self.get_structure(operand)
                type_operand = struct
                classes  = self.classify_structures(type_operand)
                use_stack = True 
                struct_size = type_operand.size 
                
                # if isinstance(operand,TackyVar):
                if classes[0]!=StructMemory.MEMORY:
                    tentative_ints = []
                    tentative_doubles = []
                    offset = 0 
                    for _class in classes:
                        if isinstance(operand,TackyVar):
                            operand = PseudoMem(operand.identifier,offset)
                        elif isinstance(operand,PseudoMem):
                            operand = PseudoMem(operand.identifier,offset)
                        else:
                            operand = PseudoMem(operand.name,offset)
                        if _class == StructMemory.SSE:
                            tentative_doubles.append(operand)
                        else:
                            
                            eightbyte_type = self.get_eightbyte_type(offset,struct_size)
                            tentative_ints.append((eightbyte_type, operand))
                        offset += 8
                    if ((len(tentative_doubles) + len(double_args)) <= 8 and
                        (len(tentative_ints) + len(reg_args)) <= int_reg_available): 
                        double_args.extend(tentative_doubles)
                        reg_args.extend(tentative_ints)
                        use_stack = False
                
                if use_stack:
                    offset = 0
                    for _class in classes:
                        if isinstance(operand,TackyVar):
                            operand = PseudoMem(operand.identifier,offset)
                        elif isinstance(operand,PseudoMem):
                            operand = PseudoMem(operand.identifier,offset)
                        else:
                            operand = PseudoMem(operand.name, offset)
                        eightbyte_type = self.get_eightbyte_type(offset, struct_size)
                        # #'uihlaseiuhfgaieu')
                        stack_args.append((eightbyte_type, operand)) 
                        # #'stack arguments', stac)
                        # 
                        offset += 8
                
        
        #stack_args)
        # 
        return (reg_args,double_args,stack_args)
            
             
        
        
    def convert_symbol_table(self):
        #'Convetring symbol table')
        backend_symbol_table={}
        for name,defn in self.symbols.items():
            # #name,defn)
            if 'fun_type' in defn:    
                #self.ret_in_memory)
                return_on_stack = False
                if name in self.ret_in_memory and self.ret_in_memory[name]==True:
                    return_on_stack = True 
                backend_symbol_table[name]=FunEntry(defined=self.symbols[name]['attrs'].defined,return_on_stack =return_on_stack)
            elif 'val_type' in defn:
                static = False
                # #name)
                #self.symbols[name]['attrs'])
                
                if isinstance(self.symbols[name]['attrs'],(StaticAttr,ConstantAttr)):
                    static=True
                # #'jee')

                backend_symbol_table[name] = ObjEntry(assembly_type=self.get_param_type(self.symbols[name]['val_type']),is_static=static,is_constant =True)
        
        # #'# symbol tabe')
        # #backend_symbol_table)
        # #
        return backend_symbol_table
    
    def get_param_type(self, _type):
        # #'inside get param type')
     
        if isinstance(_type, Long):
            return AssemblyType.quadWord
        elif isinstance(_type, ULong) or isinstance(_type, Pointer):
            return AssemblyType.quadWord
        elif isinstance(_type, Int) or isinstance(_type, UInt):
            return AssemblyType.longWord
        elif isinstance(_type,(Char,UChar,SChar)):
            return AssemblyType.byte
        elif isinstance(_type, Array):
       
            element_size = self.get_element_size(_type._type)  # Recursively get base element size
            if isinstance(_type._int,int):
                total_size  = element_size * _type._int 
            else:
                total_size = element_size * _type._int.value._int # Compute total array size
    
            new_type = AssemblyType.byteArray(size=total_size,alignment=element_size )
            
            if element_size>16:
                element_size = 16 
         
            return AssemblyType.byteArray(size=total_size,alignment=element_size )  # Return correctly computed ByteArray
        elif isinstance(_type,Pointer):
           
            return self.get_param_type(_type.ref)
        
        elif isinstance(_type,Structure):
            # #_type)
            # #self.type_table)
            if _type.tag in self.type_table:
                s:StructEntry=self.type_table[_type.tag]
                return AssemblyType.byteArray(size=s.size,alignment=s.alignment)
            else:
                return StructEntry(0,0,[])
        else:
            return AssemblyType.double

    def get_element_size(self, _type):
        """ Recursively fetch the base element size for nested arrays. """
        if isinstance(_type, Double):
            return 16  # Size of Double
        elif isinstance(_type,(Char,UChar,SChar)):
            return 1
        elif isinstance(_type, Int) or isinstance(_type, UInt):
            return 4
        elif isinstance(_type, Long) or isinstance(_type, ULong):
            return 8
        elif isinstance(_type, Pointer):
            return 8
        elif isinstance(_type,Structure):
            s:StructEntry=self.type_table[_type.tag]
            return s.size
            # return AssemblyType.byteArray(size=s.size,alignment=s.alignment)
        elif isinstance(_type, Array):
            return self.get_element_size(_type._type) * _type._int.value._int   # Recursive call
        else:
            raise ValueError(f"Unknown type: {_type}")

            

        
    def get_type(self, src):
        # #'Inside get type')
        # #src)
        
        if isinstance(src, TackyConstant):
            # #'tacky constant')
            if isinstance(src.value, (ConstInt,ConstUInt)):
                return AssemblyType.longWord
            elif isinstance(src.value,(ConstLong,ConstULong,Pointer)):
                return AssemblyType.quadWord
            elif isinstance(src.value,Double):
                return AssemblyType.double
            elif isinstance(src.value,(SChar,UChar,Char,ConstUChar,ConstChar)):
                return AssemblyType.byte
            elif isinstance(src.value,Structure):
                s:StructEntry=self.type_table[src.value.tag]
          
                return AssemblyType.byteArray(size=s.size,alignment=s.alignment)
           
            else:
                #src.value)      
                return AssemblyType.double
              

        elif isinstance(src, TackyVar):
            
            # #'tackcy var')
            var_name = src.identifier
           
            if var_name not in self.symbols:
              
                raise NameError(f"Variable '{var_name}' not found in symbols")
            
            val_type = self.symbols[var_name]['val_type']
         
           
            if isinstance(val_type,( Int,UInt)) or isinstance(val_type, type(Int)) or isinstance(val_type, type(UInt)):
                return AssemblyType.longWord
            elif isinstance(val_type, (Long,ULong,Pointer)):
                
                return AssemblyType.quadWord
            elif isinstance(val_type, Array):
                if isinstance(val_type._type,Char):
                    return AssemblyType.byteArray(size=1* val_type._int,alignment=1)
                _type = val_type
                element_size = self.get_element_size(_type._type)  # Recursively get base element size
                total_size = element_size * _type._int.value._int  # Compute total array size
         
                return AssemblyType.byteArray(size=total_size,alignment=_type._int.value._int ) 
            elif isinstance(val_type,(SChar,UChar,Char)):
                return AssemblyType.byte
            elif isinstance(val_type,Structure):
                s:StructEntry=self.type_table[val_type.tag]
            # #
                return AssemblyType.byteArray(size=s.size,alignment=s.alignment)
            elif isinstance(val_type,Double):
                return AssemblyType.double
            else:
                raise TypeError(f"Unsupported variable type '{val_type}' for '{var_name}'")
               
                # raise TypeError(f"Unsupported variable type '{val_type}' for '{var_name}'")
        elif src == AssemblyType.byte or src == AssemblyType.longWord or src == AssemblyType.quadWord:
                return src 
        elif src == AssemblyType.double or src == AssemblyType.byteArray:
            return src
        elif isinstance(src,ByteArray):
            return src 
        elif isinstance(src,(Pointer,Long,ULong)):
            return AssemblyType.quadWord
        elif isinstance(src,(Int,UInt)):
            return AssemblyType.longWord
        elif isinstance(src,(Char,SChar,UChar)):
            return AssemblyType.byte
        elif isinstance(src,Double):
            return AssemblyType.double
        elif isinstance(src,Structure):
                s:StructEntry=self.type_table[src.tag]
            # #
                return AssemblyType.byteArray(size=s.size,alignment=s.alignment)
        elif isinstance(src, Array):
                if isinstance(src._type,Char):
                    return AssemblyType.byteArray(size=1* src._int,alignment=1)
                _type = src
                element_size = self.get_element_size(_type._type)  # Recursively get base element size
                total_size = element_size * _type._int.value._int  # Compute total array size
         
                return AssemblyType.byteArray(size=total_size,alignment=_type._int.value._int ) 
        else:
            raise TypeError(f"Unsupported source type: {type(src)}")
                    
                
    def get_assembly_arg_type(val:int):
        if is_signed_32_bit(val):
            return AssemblyType.longWord
        else:
            return AssemblyType.quadWord
       
    def add_offset(self,src_op,offset):
        if isinstance(src_op,PseudoMem):
           
            e = PseudoMem(src_op.identifier,size=src_op.size+offset)
            return e
        else:
            
            raise SystemError(f'invalid operand in add_offset {src_op}')
    def copy_bytes_to_reg(self, src_op, dst_reg, byte_count, instructions):
        offset = byte_count-1 
        while offset >= 0:
            src_byte = self.add_offset(src_op, offset)
            
            # Load the current byte into the register
            instructions.append(Mov(AssemblyType.byte, src_byte, Reg(dst_reg)))
            
            # Shift left ONLY if this isn't the last byte (offset > 0)
            if offset > 0:
                instructions.append(Binary(BinaryOperator.SHL, AssemblyType.quadWord, Imm(8), Reg(dst_reg)))
            
            offset -= 1
   
        
        # return instructions

    def copy_bytes_from_reg(self,src_reg,dst_op,byte_count,instructions):
        #f'copy_bytes_from_reg(self,{src_reg,dst_op,byte_count,instructions})')
        # instructions.append(Mov(AssemblyType.quadWord, Reg(src_reg), dst_op))
        # 
        offset = 0
        while offset < byte_count:
            #'while loop')
            dst_byte = self.add_offset(dst_op, offset)
            instructions.append(Mov(AssemblyType.byte, Reg(src_reg), dst_byte))
            if offset < byte_count - 1:
                instructions.append(Binary(BinaryOperator.ShrTwoOp, AssemblyType.quadWord, Imm(8), Reg(src_reg)))
            offset += 1
       
             
    def setup_parametes(self,parameters,instr,return_in_memory):
        reg_params,double_param,stakc_params = self.classify_parameters(parameters,return_in_memory)
        regsiters = ['DI','SI','DX','CX','R8','R9']
        
        reg_index= 0
        #return_in_memory)
        #self.func_name)
        
        if return_in_memory==True:
            instr.append(Mov(AssemblyType.quadWord,Reg(Registers.DI),Memory(Reg(Registers.BP),-8)))
            reg_index+=1
        #(parameters)
        #(reg_params)
        # exit()
        # 
        if len(reg_params)>0:
            for (i,t) in reg_params:
                
              
                r = regsiters[reg_index]
              
                i = self.get_type(i)
                # 
                if isinstance(i,ByteArray):
                 
                    # 
                    if hasattr(t.identifier,'name'):
                       
                        t.identifier = t.identifier.name
                   
                        struct = self.type_table[self.symbols[t.identifier]['val_type'].tag]
                    else:
                        struct = self.type_table[self.symbols[t.identifier]['val_type'].tag]
                    
                    s= i.size
                  
                    self.copy_bytes_from_reg(r,t,s,instr)
                 
                else:
                   
                    if isinstance(t,PseudoMem):
                        dest = PseudoMem(t.identifier.name,t.size)
                    else:
                        dest = Pseudo(t.name.name)
                    instr.append(Mov(assembly_type=i,src=Reg(r), dest=dest))
                reg_index+=1
        # #instr)
        # #()
        
        #'double_param')
        # 
        double_regs = [ 'XMM0', 'XMM1', 'XMM2', 'XMM3', 'XMM4', 'XMM5', 'XMM6', 'XMM7' ]
        reg_index = 0
        for param in double_param:
          
            #param)
            if isinstance(param,Parameter):
                param = Pseudo(param.name.name)
            elif isinstance(param,PseudoMem):
                param = PseudoMem(param.identifier.name,param.size)
            else:
                param = Pseudo(param.name.name)
                
            r = double_regs[reg_index]
            instr.append(Mov(AssemblyType.double, Reg(r), param ))
         
            reg_index += 1
       
      
        offset = 16  # stack params start from BP+16
        #(stakc_params)
        # exit()
        for (i, op) in stakc_params:
            param_type = self.get_type(i)

            # Normalize param to an assembly AST form
            if isinstance(op, Pseudo):
                param = Pseudo(op.identifier.name if hasattr(op.identifier, 'name') else op.identifier)
            elif isinstance(op, PseudoMem):
                param = PseudoMem(op.identifier.name if hasattr(op.identifier, 'name') else op.identifier, op.size)
            elif isinstance(op, Imm):
                param = op
            elif isinstance(op, Parameter):
                param = Pseudo(op.name.name)
            else:
                param = self.convert_to_assembly_ast(op)

            # _offset = offset
            if isinstance(param_type, ByteArray):
                #! DO NOT change pleaseee
                
                struct_size = param_type.size
             
                _offset = offset 
              
                while struct_size >= 8:
                    instr.append(Mov(
                        assembly_type=AssemblyType.quadWord,
                        src=Memory(Reg(Registers.BP),  _offset ),
                        dest=PseudoMem(param.identifier,param.size )
                    ))
                    param.size += 8  
                    _offset += 8
                    struct_size -= 8

                while struct_size >= 4:
                    instr.append(Mov(
                        assembly_type=AssemblyType.longWord,
                        src=Memory(Reg(Registers.BP), _offset),
                        dest=PseudoMem(param.identifier, param.size )
                    ))
                    param.size += 4
                    
                    _offset += 4
                    struct_size -= 4

                while struct_size >= 1:
                    instr.append(Mov(
                        assembly_type=AssemblyType.byte,
                        src=Memory(Reg(Registers.BP), _offset),
                        dest=PseudoMem(param.identifier, param.size )
                    ))
                    param.size +=1
                    _offset += 1
                    struct_size -= 1

                offset = _offset
                offset = ((offset+7)//8)*8
            else:
                instr.append(Mov(
                    assembly_type=self.get_type(i),
                    src=Memory(Reg(Registers.BP), offset),
                    dest=param
                ))
                offset += 8
        
      
        return instr
    
    def convert_struct(self,sd):
        if isinstance(sd,StructEntry):
            #self.type_table)
            # #
            return ByteArray()
            
        
    def convert_return_value(self,ret:TackyReturn,instructions):
        #'convert return value')
        if isinstance(ret.val,Null) or (isinstance(ret.val,TackyVar) and ret.val.identifier == 'DUMMY'):
            instructions.append(Ret())
            
            return instructions
        if isinstance(ret.val,TackyVar) and ret.val.identifier=='NO_RET_VAL':
            instructions.append(Ret())
            return instructions
        
        
        int_retvals, double_retvals, return_in_memory = self.classify_return_val(ret.val)
        #(return_in_memory)
        # exit()
        if return_in_memory == True:
            
            
      
                
                self.ret_in_memory[self.func_name] = True
              
                instructions.append(Mov(AssemblyType.quadWord, Memory(Reg(Registers.BP), -8), Reg(Registers.AX)))
                ret_operand = self.convert_to_assembly_ast(ret.val)
           
                
                struct = self.type_table[self.symbols[ret.val.identifier]['val_type'].tag]
                struct_size = struct.size 
                offset = 0
               
             
                while struct_size >= 8:
                  
                    instructions.append(Mov(assembly_type=AssemblyType.quadWord,
                                            src=ret_operand,
                                            dest=Memory(Reg(Registers.AX), offset)))
                    ret_operand = self.add_offset(ret_operand, 8)
                    offset += 8
                    struct_size -= 8
                  
                    
                while struct_size >= 4:
           
                    
                    instructions.append(Mov(assembly_type=AssemblyType.longWord,
                                            src=ret_operand,
                                            dest=Memory(Reg(Registers.AX), offset)))
                    ret_operand = self.add_offset(ret_operand, 4)
                    offset += 4
                    
          
                    
                    struct_size -= 4
                    
                while struct_size >= 1:
                 
                    
                    
                    instructions.append(Mov(assembly_type=AssemblyType.byte,
                                            src=ret_operand,
                                            dest=Memory(Reg(Registers.AX), offset)))
                    
                    ret_operand = self.add_offset(ret_operand, 1)
                    offset += 1
                    struct_size -= 1
            
                        
               
                instructions.append(Ret())              
              
        else:
            int_return_registers = [ 'AX','DX']
            double_return_registers = [ 'XMM0', 'XMM1' ]
            reg_index = 0
            index = 0 
            # #int_retvals)
            for (i,op) in int_retvals:
                r = int_return_registers[reg_index]
          
                i = self.get_type(i)
                
                if isinstance(i,ByteArray):
                     
                    # t = self.type_table[self.symbols[op.identifier]['val_type'].tag]
         
                    # # reg_index+=1
                    
                    r = int_return_registers[reg_index]
                    # #(t.size)
                    # #(i)
                    # exit()
                    self.copy_bytes_to_reg(op, r, i.size,instructions)
                    #(instructions)
                    # exit()
                else:
                    # 
                    instructions.append(Mov(i, op, Reg(r)))
                reg_index += 1
                
                
                
            reg_index = 0
            for op in double_retvals: 
                r = double_return_registers[reg_index]
                instructions.append(Mov(AssemblyType.double, op, Reg(r)))
                reg_index += 1
            instructions.append(Ret())
     
        # #instructions)
        # #
        return instructions
    
    def convert_to_assembly_ast(self,tacky_ast) :
        # #self.symbols)
        # #
        """
        Converts a Tacky AST into an AssemblyProgram AST.
        
        Args:
            tacky_ast: The root of the Tacky AST to be converted.
        
        Returns:
            An AssemblyProgram instance representing the equivalent assembly code.
        """
        # Handle the top-level Program node
        #tacky_ast)
        if isinstance(tacky_ast, TackyProgram):
            
            
            # Recursively convert the function_definition part of the TackyProgram
            assembly_functions = []
            
            for defn in tacky_ast.function_definition:
                
                if isinstance(defn,TackyFunction):
                    #'converting tacky func')
                    # #defn)
                    # self.ret_in_memory[defn.name] = False

                    assembly_function = self.convert_to_assembly_ast(defn)
                    
                    assembly_functions.append(assembly_function)
                 
                if isinstance(defn,TackyStaticVariable):
                    #'Converting tacky var')
                    if isinstance(type(defn._type),type(Int())):
                        alignment = 4
                    elif isinstance(type(defn),(Char,SChar,UChar)):
                        alignment = 1
                    else:
                        alignment = 8
                    
                  
                        
                    
                    if isinstance(defn.init,DoubleInit):
                        static_var = TopLevel.static_const(identifier=defn.name,alignment=alignment,init=defn.init)
                    else:
                        static_var = TopLevel.static_var(identifier=defn.name,_global = defn._global,alignment=alignment,init=defn.init)
                    
                    assembly_functions.append(static_var)
                    
                elif isinstance(defn,TackyStaticConstant):
                    #'Converting tacky const')
                    
                    if isinstance(type(defn._type),type(Int())):
                        alignment = 4
                    elif isinstance(type(defn),(Char,SChar,UChar)):
                        alignment = 1
                    else:
                        alignment = 8
                        
                    static_var = TopLevel.static_const(identifier=defn.name,alignment=alignment,init=defn.init)
                    
                  
                    assembly_functions.append(static_var)
                    
            # for i in self.static_const:
            # #self.static_const)
          
            assembly_functions.extend(self.static_const)
            
            backend_Symbol_table=self.convert_symbol_table()
            # #
            return AssemblyProgram(
                function_definition=assembly_functions
            ),backend_Symbol_table
           
        
    
        # Handle Function node
        elif isinstance(tacky_ast, TackyFunction):
            params = []
            instructions=[]
            return_in_memory = False

            # if isinstance(self.symbols[tacky_ast.name]['fun_type'].base_type,Structure):
            #     return_in_memory = True
            # # 
            # params = self.setup_parametes(tacky_ast.params,params,return_in_memory)
            # #tacky_ast.params)
            # #
            self.func_name = tacky_ast.name
            self.ret_in_memory[self.func_name] = False
            # instructions.extend(params)
            for instr in tacky_ast.body:
                
                converted_instrs = self.convert_to_assembly_ast(instr)
                
                if isinstance(converted_instrs, list):
                    
                    # If conversion returns a list of instructions, extend the list
                    instructions.extend(converted_instrs)
                else:
                    # Otherwise, append the single instruction
                    instructions.append(converted_instrs)
            # Create an AssemblyFunction with the converted instructions
        
        
            return_in_memory = False 
            
            
            if self.ret_in_memory[tacky_ast.name] == True:
                return_in_memory = True
           
            if self.symbols[tacky_ast.name]:
                if isinstance(self.symbols[tacky_ast.name]['fun_type'].base_type,Structure):
                    s = self.symbols[tacky_ast.name]['fun_type'].base_type
                    struct = self.type_table[s.tag]
                    size = struct.size 
                    if size > 16:
                        self.ret_in_memory[tacky_ast.name] = True
                        return_in_memory = True
            params = []
            if len(tacky_ast.params)>0:
                params = self.setup_parametes(tacky_ast.params,params,return_in_memory)
            # instructions.insert(params)
            instructions = params + instructions
            return TopLevel.assembly_func(
                name=tacky_ast.name,  # Assuming tacky_ast.name is an Identifier
                _global=tacky_ast._global,
                instructions=instructions
            )
        
        elif isinstance(tacky_ast,Identifier):
            return tacky_ast.name
        
        elif isinstance(tacky_ast,TackyFunCall):
            # #'fin call')
            # #self.symbols[tacky_ast.args[0].identifier])
            # 
            instructions=[]
            arg_regsiters = ['DI','SI','DX','CX','R8','R9']
            double_regs = [ 'XMM0', 'XMM1', 'XMM2', 'XMM3', 'XMM4', 'XMM5', 'XMM6', 'XMM7' ]
            
            
            return_in_memory = False 
            int_dests = []
            double_dests = [] 
            reg_index = 0 
            
            self.ret_in_memory[tacky_ast.fun_name] = False
    
            if not isinstance(tacky_ast.dst,Null):
                #'going into classify ret value')
                int_dests , double_dests , return_in_memory =self.classify_return_val(tacky_ast.dst)
                #'after classify ret value')
                #int_dests)
                #double_dests)
                #return_in_memory)
                # 
            if return_in_memory==True:
                # 
                self.ret_in_memory[tacky_ast.fun_name] = True
                dst_operand = self.convert_to_assembly_ast(tacky_ast.dst)
                instructions.append(Lea(dst_operand,Reg(Registers.DI)))
                reg_index +=1
            
            #int_dests)
            #double_dests)
            #'ret',return_in_memory)
            #tacky_ast.args)
            reg_arg,dub_arg,stack_arg=self.classify_arguments(tacky_ast.args,return_in_memory)
            #reg_arg)
            # 
            #'reg args',reg_arg)
            #'double args',dub_arg)
            #'stack args',stack_arg)
            #'afgter classify args')
            # #()
            # 
            # #(return_in_memory)
            #(reg_arg)
            #(stack_arg)
            # exit()
            stack_padding = 8 if len(stack_arg) % 2 == 1 else 0
            if stack_padding != 0:
                instructions.append(AllocateStack(stack_padding))

            # reg_index=0
            for (i,t) in reg_arg:
                #'in reg args')
                r = arg_regsiters[reg_index]
                tacky_arg = t 
                # 
                i = self.get_type(i)
                
                
                if isinstance(tacky_arg,TackyVar):
                    
                    tacky_arg = Pseudo(tacky_arg.identifier)
                #'tacky arg',tacky_arg)
                assembly_arg = tacky_arg
                if isinstance(i, ByteArray):
                    struct = i.size
                    s = struct
                    
                   
                    self.copy_bytes_to_reg(assembly_arg,r,s,instructions)
                    # 
                  
                else:
                    if not isinstance(tacky_arg,(Pseudo,PseudoMem,Imm)):
                        assembly_arg = self.convert_to_assembly_ast(tacky_arg)
                
                    instructions.append(Mov(assembly_type=self.get_type(i),src=assembly_arg,dest=Reg(r)))
                    
                reg_index+=1
           
          
            reg_index=0
            for tacky_arg in dub_arg:
                r= double_regs[reg_index]
                assembly_arg = tacky_arg
                if not isinstance(tacky_arg,(Pseudo,PseudoMem,Imm)):
                        assembly_arg = self.convert_to_assembly_ast(tacky_arg)
                instructions.append(Mov(assembly_type=AssemblyType.double,src=assembly_arg,dest=Reg(r)))
                reg_index +=1
                
            # offset = 0
            
            # offset = 0
            for (i, t) in stack_arg[::-1]:
                tacky_arg = t 
                if not isinstance(tacky_arg, (Pseudo, PseudoMem, Imm)):
                    assembly_arg = self.convert_to_assembly_ast(tacky_arg)
                else:
                    assembly_arg = tacky_arg

                if isinstance(self.get_type(i), ByteArray):
                    #! DO NOT change pleaseee
                    offset = 0 
                    struct_size = self.get_type(i).size

                    # Align struct size to nearest multiple of 8 for stack usage
                    # aligned_size = ((struct_size + 7) // 8) * 8
                    aligned_size = struct_size
                    instructions.append(Binary(
                        assembly_type=AssemblyType.quadWord,
                        operator=BinaryOperator.SUBTRACT,
                        src1=Imm(8),
                        src2=Reg(Registers.SP)
                    ))

                    remaining = aligned_size
                    
                    # Copy byte-by-byte (you can improve this to copy word-sized chunks if needed)
                    # operand_size = assembly_arg.size
                    while remaining >= 8:
                        # operand_size = assembly_arg.size
                        
                        instructions.append(Mov(
                            assembly_type=AssemblyType.quadWord,
                            src=PseudoMem(assembly_arg.identifier, assembly_arg.size),
                            
                            dest=Memory(Reg(Registers.SP), offset)
                        ))
                        assembly_arg.size +=8
                        offset += 8
                        remaining -= 8
                    while remaining >=4:
                        # operand_size = assembly_arg.size
                        
                        instructions.append(Mov(
                            assembly_type=AssemblyType.longWord,
                            src=PseudoMem(assembly_arg.identifier,assembly_arg.size),
                            dest=Memory(Reg(Registers.SP), offset)
                        ))
                        assembly_arg.size +=4
                        
                        offset += 4
                        remaining -= 4
                    while remaining >=1 :
                        # operand_size = assembly_arg.size
                        
                        instructions.append(Mov(
                            assembly_type=AssemblyType.byte,
                            src=PseudoMem(assembly_arg.identifier,assembly_arg.size),
                            dest=Memory(Reg(Registers.SP), offset)
                        ))
                        assembly_arg.size += 1 
                        
                        offset += 1
                        remaining -= 1
                elif isinstance(assembly_arg,Reg) or isinstance(assembly_arg,Imm) or self.get_type(i)==AssemblyType.quadWord or self.get_type(i)==AssemblyType.double :
                    #'Moving quad / double')
                    instructions.append(Push(assembly_arg,_type=self.get_type(i)))
                else:
                    instructions.append(Mov(assembly_type=self.get_type(i),src=assembly_arg,dest=Reg(Registers.AX)))
                    instructions.append(Push(Reg(Registers.AX),_type=AssemblyType.longWord))
                    
            
            instructions.append(Call(indentifier=tacky_ast.fun_name))
            bytes_to_remove = 8 * len(stack_arg)+ stack_padding
            if bytes_to_remove !=0:
              
                instructions.append(DeallocateStack(value=bytes_to_remove))
      
            if not isinstance(tacky_ast.dst,Null) and  return_in_memory==False:
                int_return_registers = ["AX","DX"]
                double_return_regiters = ["XMM0","XMM1"]
                
                reg_index = 0 
             
                
                for (i,op) in int_dests:
                    
                    t= self.get_type(i)
                    
                    r = int_return_registers[reg_index]
                    if isinstance(t,ByteArray) and isinstance(self.symbols[op.identifier]['val_type'],Structure):
                        self.copy_bytes_from_reg(r,op,t.size,instructions)
                     
                    else:
                        
                         
                        instructions.append(Mov(assembly_type=t,src=Reg(r),dest=op))
                    reg_index+=1
                
             
                reg_index = 0
                for op in double_dests:
                    r = double_return_regiters[reg_index]
                    instructions.append(Mov(assembly_type=AssemblyType.double,src=Reg(r),dest=op))
                    reg_index+=1
            #'# the funcall')
            #instructions)
            # 
            return instructions
        
        
        # elif isinstance(tacky_ast,TackyFunCall):
        #     instructions=[]
        #     arg_regsiters = ['DI','SI','DX','CX','R8','R9']
        #     double_regs = [ 'XMM0', 'XMM1', 'XMM2', 'XMM3', 'XMM4', 'XMM5', 'XMM6', 'XMM7' ]
            
        #     reg_arg,dub_arg,stack_arg=self.classify_arguments(tacky_ast.args,False)
        #     stack_padding = 8 if len(stack_arg) % 2 == 1 else 0
        #     if stack_padding != 0:
        #         instructions.append(AllocateStack(stack_padding))

                
        #     reg_index=0
        #     for tacky_arg in reg_arg:
        #         r= arg_regsiters[reg_index]
        #         assembly_arg = self.convert_to_assembly_ast(tacky_arg)
        #         #assembly_arg)
        #         # #
        #         instructions.append(Mov(assembly_type=self.get_type(tacky_arg),src=assembly_arg,dest=Reg(r)))
        #         reg_index +=1
        #     reg_index=0
        #     for tacky_arg in dub_arg:
        #         r= double_regs[reg_index]
        #         assembly_arg = self.convert_to_assembly_ast(tacky_arg)
        #         instructions.append(Mov(assembly_type=AssemblyType.double,src=assembly_arg,dest=Reg(r)))
        #         reg_index +=1
                
        #     for tacky_arg in stack_arg[::-1]:
        #         assembly_arg=self.convert_to_assembly_ast(tacky_arg)
              
        #         if isinstance(assembly_arg,Reg) or isinstance(assembly_arg,Imm) or self.get_type(tacky_arg)==AssemblyType.quadWord or self.get_type(tacky_arg)==AssemblyType.double :
        #             instructions.append(Push(assembly_arg,_type=self.get_type(tacky_arg)))
        #         else:
        #             instructions.append(Mov(assembly_type=self.get_type(tacky_arg),src=assembly_arg,dest=Reg(Registers.AX)))
        #             instructions.append(Push(Reg(Registers.AX),_type=AssemblyType.longWord))
                    
        #     instructions.append(Call(indentifier=tacky_ast.fun_name))
            
        #     bytes_to_remove = 8 * len(stack_arg)+ stack_padding
        #     if bytes_to_remove !=0:
        #         # #'Bytes to remove',bytes_to_remove)
        #         instructions.append(DeallocateStack(value=bytes_to_remove))
        #     # #
        #     if not isinstance(tacky_ast.dst,Null):
        #         # #
        #         # #tacky_ast.dst)
        #         assembly_dst = self.convert_to_assembly_ast(tacky_ast.dst)
        #         # #
        #         if isinstance(self.symbols[tacky_ast.fun_name]['fun_type'].base_type, Double):
        #             # #
        #             instructions.append(Mov(assembly_type=AssemblyType.double,src=Reg(Registers.XMM0),dest=assembly_dst))
        #         else:
        #             instructions.append(Mov(assembly_type=self.get_type(tacky_ast.dst),src=Reg(Registers.AX),dest=assembly_dst))
        #     return instructions
        
        
        # Handle Return instruction
        elif isinstance(tacky_ast, TackyReturn):
            # #tacky_ast.val)
            # #self.symbols[tacky_ast.val.identifier])
            # #'symbols')
            # #self.symbols[tacky_ast.val.identifier])
            #self.func_name)
            #self.ret_in_memory[self.func_name])
            # 
            instr =[]
            i= self.convert_return_value(tacky_ast,instr)
            #i)
            # #
            return i
            # if isinstance(tacky_ast.val,TackyVar) and tacky_ast.val.identifier == 'DUMMY':
            #     # #
            #     return [Ret()]
            # tacky_ast.val=tacky_ast.val
            # #* Get type of value of a variable        
            # if isinstance(tacky_ast.val , TackyVar):
            #     _type=self.get_type(tacky_ast.val)
            # else:
            #     #* Type of a constant
            #     _type=self.get_type(tacky_ast.val)
          
            # #* CONVERSION OF DOUBLE TYPE TO RETURN 
            # if isinstance(tacky_ast.val,TackyConstant) and isinstance(tacky_ast.val.value,ConstDouble):
            #         return [
            #         Mov(assembly_type=AssemblyType.double,src=self.convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.XMM0)),
            #         Ret()
            #     ]    
           
            # #* CONVERT RETURN TO MOV AND RETURN STATEMENT 
            # elif _type ==AssemblyType.double:
            #      return [
            #         Mov(assembly_type=AssemblyType.double,src=self.convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.XMM0)),
            #         Ret()
            #     ]    
            # return [
            #     Mov(assembly_type=_type,src=self.convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.AX)),
            #     Ret()
            # ]
    
        # Handle Unary instruction
        elif isinstance(tacky_ast, TackyUnary):        
            # Convert a Unary operation by moving src to dst and applying the operator
            # return convert_unary(self=self,tacky_ast=tacky_ast)
            #* Converison of unary NOT
            if tacky_ast.operator ==TackyUnaryOperator.NOT:
                #'Unary Not')
                src=self.convert_to_assembly_ast(tacky_ast.src)
                dest=self.convert_to_assembly_ast(tacky_ast.dst)
              
                
                #* Converion of double by taking XOR with Register
                if self.get_type(tacky_ast.src) == AssemblyType.double:
                    # #
                    return [
                        #* Take XOR
                        Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                        
                        #* Compare instruction
                        Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.src),operand2=Reg(Registers.XMM0)),
                        
                        #* Move Instruction
                        Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=dest),
                        
                        #* Set Code = Equal
                        SetCC(Cond_code=Cond_code.E,operand=self.convert_to_assembly_ast(tacky_ast.dst))
                        ]
                
                else:
                  
                    #* Converion of types other than Double   
                    return [
                        #* Compare
                        Cmp(assembly_type=self.get_type(tacky_ast.src),operand1=Imm(0),operand2=self.convert_to_assembly_ast(tacky_ast.src)),
                        
                        #* Move
                        Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=dest),
                        
                        #* Set Code
                        SetCC(Cond_code=Cond_code.E,operand=self.convert_to_assembly_ast(tacky_ast.dst))
                ]
            else:
                #* Negation for double
             
                if tacky_ast.operator == TackyUnaryOperator.NEGATE  and self.get_type(tacky_ast.src)==AssemblyType.double:
                    
                    #* Create temporary label
                        #* Set value
                        # if isinstance(tacky_ast.src,TackyConstant):
                            const_label=''
                            value = '-0.0'
                       
                           
                        
                            #* set boolean flag found
                            found =False
                            
                            #* Check for existing static const with same alignment and value in table
                            for i in self.temp:
                                if self.temp[i]['alignment'] == 16 and (float(self.temp[i]['value']) - float(value)==0):
                                    # #value)
                                    # #
                                    const_label = self.temp[i]['identifier']
                                    value = self.temp[i]['value']
                                    found=True 
                                else:
                                    continue 
                            
                            #* Check condition based oh flag , if not found , insert a static character in symbol table and temp table
                            if not found:
                                const_label = get_const_label()
                                self.static_const.append(TopLevel.static_const(
                                    identifier=const_label,
                                    alignment=16,
                                    init=DoubleInit(-0.0),
                                ))
                                self.temp[const_label] = {
                                    'identifier':const_label,
                                    'alignment':16,
                                    'value':'-0.0',
                                    
                            }
                            
                        #* Return rest of the binary and move condition for negation 
                            #const_label)
                            # #
                            return[ 
                                #* Move instruction 
                                Mov(assembly_type=AssemblyType.double,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                                
                                #* Binary instruction
                                Binary(assembly_type=AssemblyType.double,operator=BinaryOperator.XOR,src1=Data(const_label,0),src2=self.convert_to_assembly_ast(tacky_ast.dst)),
                                
                                
                            ]
                             
                # src=self.convert_to_assembly_ast(tacky_ast.src)
                #* Return instrcutions for other datatypes
                
                return [
                    #* Move instructions from src -> dst
                    Mov(assembly_type=self.get_type(tacky_ast.src),src=self.convert_to_assembly_ast(tacky_ast.src), dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                    
                    #* Binary Negation
                    #* Operator to use is unsiged by default 
                    Unary(operator=self.convert_operator(tacky_ast.operator,False),assembly_type=self.get_type(tacky_ast.src), operand=self.convert_to_assembly_ast(tacky_ast.dst))
                    
                ]
            
        # Check if the current AST node is a TackyBinary operation
        elif isinstance(tacky_ast, TackyBinary):
            #tacky_ast)
            # #
            # #tacky_ast.operator)
            # #'Binary operations')
            # Handle integer division operations
            if tacky_ast.operator == TackyBinaryOperator.DIVIDE:
                """
                Generate assembly instructions for integer division.
                
                Assembly Operations:
                    1. Move the dividend (src1) into the AX register.
                    2. Execute the CDQ instruction to sign-extend AX into DX:AX.
                    3. Perform the IDIV operation using the divisor (src2).
                    4. Move the quotient from AX to the destination (dst).
                
                This sequence follows the x86 assembly convention for signed integer division.
                """
              
              #* Check if the variable is signed.
                if isinstance(tacky_ast.src1,TackyVar) :
                    if type(self.symbols[tacky_ast.src1.identifier]['val_type']) in (Int, Long):
                        t=Int()  
                    else:
                        t=UInt()
              #* Check if the constant is signed.
                else:
                    if isinstance(tacky_ast.src1,TackyConstant) and isinstance(tacky_ast.src1.value,(ConstInt,ConstLong)):
                        t=Int()
                    else:
                        t=UInt()

                # #self.convert_to_assembly_ast(tacky_ast.src2))
                # #
                if isSigned(t):
                #* 
                        return [
                            # Move the dividend to the AX register
                            Mov(assembly_type=self.get_type(tacky_ast.src1),src=self.convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                            
                            # Convert Doubleword to Quadword: Sign-extend AX into DX:AX
                            Cdq(assembly_type=self.get_type(tacky_ast.src1)),
                            
                            # Perform signed integer division: AX / src2
                            Idiv(assembly_type=self.get_type(tacky_ast.src1),operand=self.convert_to_assembly_ast(tacky_ast.src2)),
                            
                            # Move the quotient from AX to the destination variable
                            Mov(assembly_type=self.get_type(tacky_ast.src1),src=Reg(Registers.AX), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                        ]
                    #* If it is signed we check if the type is double and emit a double division
                   
                else:
                    # #tacky_ast,self.get_type(tacky_ast.src1))
                    if self.get_type(tacky_ast.src1)==AssemblyType.double:
                        # #
                    
                        #* Convert operands to assembly types
                        src=self.convert_to_assembly_ast(tacky_ast.src1)
                        dest=self.convert_to_assembly_ast(tacky_ast.dst)
                        src1=self.convert_to_assembly_ast(tacky_ast.src2)
                        src2=self.convert_to_assembly_ast(tacky_ast.dst)
                        
                        #* Return statements
                        return [            
                            Mov(assembly_type=self.get_type(tacky_ast.src1),src=self.convert_to_assembly_ast(tacky_ast.src1),dest=dest ),
                            Binary(operator=BinaryOperator.DIVDOUBLE,assembly_type=AssemblyType.double,src1=src1,src2=src2)
                        ]
                        
                    #* If signed and type != Double
                
                    #* If Unsigned
                    return [
                        # Move the dividend to the AX register
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=self.convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                        
                        # Zero-extend AX into EAX
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=Imm(0), dest=Reg(Registers.DX)),
                        
                        # Perform unsigned integer division: EAX / src2
                        Div(assembly_type=self.get_type(tacky_ast.src1),operand=self.convert_to_assembly_ast(tacky_ast.src2)),
                        
                        # Move the quotient from AX to the destination variable
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=Reg(Registers.AX), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                    ]
                    
            
            # Handle remainder operations resulting from integer division
            elif tacky_ast.operator == TackyBinaryOperator.REMAINDER:
                # #'Inside remainder')
                # #'Inside ')
                """
                Generate assembly instructions for computing the remainder after integer division.
                
                Assembly Operations:
                    1. Move the dividend (src1) into the AX register.
                    2. Execute the CDQ instruction to sign-extend AX into DX:AX.
                    3. Perform the IDIV operation using the divisor (src2).
                    4. Move the remainder from DX to the destination (dst).
                
                This sequence adheres to the x86 assembly convention where the remainder is stored in the DX register after division.
                """
                if isinstance(tacky_ast.src1,TackyVar) :
                    # #self.symbols[tacky_ast.src1.identifier])
                    if type(self.symbols[tacky_ast.src1.identifier]['val_type']) in (Int, Long):
                        t=Int()  
                    else:
                        t=UInt()
                else:
                    if isinstance(tacky_ast.src1,TackyConstant) and isinstance(tacky_ast.src1.value,(ConstInt,ConstLong)):
                        t=Int()
                    else:
                        t=UInt()
              
                if isSigned(t):
                # if isSigned(type(tacky_ast.src1)):
                
                    return [
                        # Move the dividend to the AX register
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=self.convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                        
                        # Convert Doubleword to Quadword: Sign-extend AX into DX:AX
                        Cdq(assembly_type=self.get_type(tacky_ast.src1)),
                        
                        # Perform signed integer division: AX / src2
                        Idiv(assembly_type=self.get_type(tacky_ast.src1),operand=self.convert_to_assembly_ast(tacky_ast.src2)),
                        
                        # Move the remainder from DX to the destination variable
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=Reg(Registers.DX), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                    ]
                else:
                    # #
                    return [
                        # Move the dividend to the AX register
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=self.convert_to_assembly_ast(tacky_ast.src1), dest=Reg(Registers.AX)),
                        
                        # Zero-extend AX into EAX
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=Imm(0), dest=Reg(Registers.DX)),
                        
                        # Perform unsigned integer division: EAX / src2
                        Div(assembly_type=self.get_type(tacky_ast.src1),operand=self.convert_to_assembly_ast(tacky_ast.src2)),
                        
                        # Move the remainder from DX to the destination variable
                        Mov(assembly_type=self.get_type(tacky_ast.src1),src=Reg(Registers.DX), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                    ]
                
            # Handle addition, subtraction, and multiplication operations
            elif tacky_ast.operator in (
                TackyBinaryOperator.ADD,
                TackyBinaryOperator.SUBTRACT,
                TackyBinaryOperator.MULTIPLY
            ):
                # if tacky_ast.operator == TackyBinaryOperator.MULTIPLY:
                #     return [
                #     # Move the first operand directly into the destination register
                #     Mov(src=self.convert_to_assembly_ast(tacky_ast.src1), dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                    
                #     # Perform the binary operation with the second operand and store the result in the destination register
                #     Binary(
                #         operator=self.convert_operator(tacky_ast.operator),
                #         src2=self.convert_to_assembly_ast(tacky_ast.src2),
                #         src1=self.convert_to_assembly_ast(tacky_ast.dst)
                #     ),
                #     # Mov(src=self.convert_to_assembly_ast(tacky_ast.dst), dest=Reg(Registers.AX))
                # ]
        
                """
                Generate assembly instructions for addition, subtraction, and multiplication.
                
                Assembly Operations:
                    1. Move the first operand (src1) directly into the destination register.
                    2. Perform the binary operation (ADD, SUBTRACT, MULTIPLY) between the second operand (src2) and the destination register.
                
                This approach optimizes instruction generation by utilizing the destination register to store intermediate results, reducing the need for additional temporary storage.
                """
                # #self.get_type(tacky_ast.src1))
                # #
                return [
                    # Move the first operand directly into the destination register
                    Mov(assembly_type=self.get_type(tacky_ast.src1),src=self.convert_to_assembly_ast(tacky_ast.src1), dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                    
                    # Perform the binary operation with the second operand and store the result in the destination register
                    Binary(
                        operator=self.convert_operator(tacky_ast.operator,False),
                        src1=self.convert_to_assembly_ast(tacky_ast.src2),
                        assembly_type=self.get_type(tacky_ast.src1),
                        src2=self.convert_to_assembly_ast(tacky_ast.dst)
                    ),
                    # Mov(src=self.convert_to_assembly_ast(tacky_ast.dst), dest=Reg(Registers.AX))
                ]
        
            # Handle unsupported binary operators by raising an error
            elif tacky_ast.operator in (TackyBinaryOperator.GREATER_OR_EQUAL,TackyBinaryOperator.LESS_OR_EQUAL,TackyBinaryOperator.LESS_THAN,TackyBinaryOperator.NOT_EQUAL,TackyBinaryOperator.EQUAL,TackyBinaryOperator.OR,TackyBinaryOperator.AND):
              
              
                if isinstance(tacky_ast.src1,TackyVar) :                    
                    if type(self.symbols[tacky_ast.src1.identifier]['val_type']) in (Int, Long,Char,SChar):
                        t=Int()  
                    else:
                        t=UInt()
                else:
                    if isinstance(tacky_ast.src1,TackyConstant) and isinstance(tacky_ast.src1.value,(ConstInt,ConstLong,ConstChar)):
                        t=Int()
                    else:
                        t=UInt()
             
              
                if isSigned(t)==True:
                    
                    
                    # #
                    # #self.symbols[tacky_ast.dst.identifier])
                    # #'returning')
                    # #'serc1',tacky_ast.src1)
                    # #self.symbols[tacky_ast.src1.identifier])
                    # #'src2',tacky_ast.src2)
                    # #'src',tacky_ast.src2)
                    # # #self.get_type(tacky_ast.src2)) 
                    # # # #
                    # #tacky_ast)
                    # #
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src2),operand1=self.convert_to_assembly_ast(tacky_ast.src2),
                                operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,True),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                else:
          
                    
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src2),operand1=self.convert_to_assembly_ast(tacky_ast.src2),
                                operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                        
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,False),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                    
            elif tacky_ast.operator == TackyBinaryOperator.GREATER_THAN:
                # #self.symbols[tacky_ast.src1.identifier])
                
                if isinstance(tacky_ast.src1,TackyVar) :
                    if type(self.symbols[tacky_ast.src1.identifier]['val_type']) in (Int,Long):
                        t=Int()  
                    else:
                        t=UInt()
                else:
                    if isinstance(tacky_ast.src1,TackyConstant) and isinstance(tacky_ast.src1.value,(ConstInt,ConstLong)):
                        t=Int()
                    else:
                        t=UInt()
                if isSigned(t):
                    
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src1),operand1=self.convert_to_assembly_ast(tacky_ast.src2),
                                operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,True),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                else:
                    # #
                    
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src1),operand1=self.convert_to_assembly_ast(tacky_ast.src2),
                                operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            #* CHNAGED THE ASSEMBLY TYPE FROM QUAD WORD TO DST
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,False),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                    
            else:
                """
                Error Handling:
                    If the binary operator is not among the supported ones (DIVIDE, REMAINDER, ADD, SUBTRACT, MULTIPLY),
                    the compiler raises a TypeError to indicate that the expression type is unsupported.
                """
                raise TypeError(f"Unsupported binary operator: {tacky_ast.operator}")
        elif isinstance(tacky_ast,str):
            return tacky_ast
        elif isinstance(tacky_ast,int):
               return Imm(tacky_ast)
            
        # Handle Constant operand
        elif isinstance(tacky_ast, TackyConstant):
            # #
            # #tacky_ast.value)
            #'ENTER TAKCY CONST',tacky_ast)
            if isinstance(tacky_ast,TackyConstant) and isinstance(tacky_ast.value,(ConstInt,ConstUInt)):
                #'RETURNING CONST')
                return Imm(tacky_ast.value._int)
                
            elif isinstance(tacky_ast.value,(ConstInt,ConstLong,ConstUInt,ConstULong,ConstChar,ConstUChar)):
                #'RETURNING CONST')
            
                return Imm(tacky_ast.value._int)
            elif isinstance(tacky_ast.value,ConstDouble):
                const_label=''
                value = tacky_ast.value._int
                found =False
                for i in self.temp:
                    
                    if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(value)==0):
                       
                        const_label = self.temp[i]['identifier']
                        value = self.temp[i]['value']
                        found=True 
                    else:
                        
                        continue 
                
                if not found:
                    const_label=get_const_label()
                    self.static_const.append(TopLevel.static_const(
                    identifier=const_label,
                    alignment=8 ,
                    init=DoubleInit(tacky_ast.value._int))
                    
                        )
                    # #self.temp)
                    # #
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
                    #'RETURNING CONST')

                return Data(name=const_label,val=0)
                
                # raise ValueError('Found Double const value')
            #'RETURNING CONST')
                
            return Imm(tacky_ast.value)
            # Convert a constant value into an Imm operand
        
        # elif isinstance(tacky_ast,)
        # elif isinstance(tacky_ast,AssemblyStaticVariable):
        # Handle Variable operand
        elif isinstance(tacky_ast, TackyVar):
            #'Tacky var')
            # Convert a variable into a Pseudo operand
            # #tacky_ast)
            # #self.symbols[tacky_ast.identifier])
            # #
            # #'here',self.symbols[tacky_ast.identifier])
            if isinstance(self.symbols[tacky_ast.identifier]['val_type'],(Array,Structure)):
              
                return PseudoMem(tacky_ast.identifier,0)
            
            return Pseudo(tacky_ast.identifier)
        elif isinstance(tacky_ast,TackyJump):
            return [Jmp(indentifier=tacky_ast.target)]
        elif isinstance(tacky_ast,TackyJumpIfZero):
            # #self.get_type(tacky_ast.condition))
            # #self.symbols[tacky_ast.condition.identifier])
            # #tacky_ast)
            # #self.symbols[tacky_ast.condition.identifier])
            if isinstance(tacky_ast.condition,TackyVar) and (isinstance(self.symbols[tacky_ast.condition.identifier]['val_type'],Double) or isinstance(self.symbols[tacky_ast.condition.identifier]['val_type'],Double)):
                # #'Double')
                # #
                #'# jump if zero')
                # #
                return [
                    Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                    Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.condition),operand2=Reg(Registers.XMM0)),
                    JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
                    ]
                
            elif self.get_type(tacky_ast.condition) == AssemblyType.double:
                    #'# jump if zero')
                    # #
                
                    return [
                    Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                    Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.condition),operand2=Reg(Registers.XMM0)),
                    JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
                    ]
            
            #'# jump if zero')
            # #
            return [
                Cmp(assembly_type=self.get_type(tacky_ast.condition),operand1=Imm(0),operand2=self.convert_to_assembly_ast(tacky_ast.condition)),
                JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
            ]
        elif isinstance(tacky_ast,TackyJumpIfNotZero):
            if isinstance(tacky_ast.condition,TackyVar) and  isinstance(self.symbols[tacky_ast.condition.identifier]['Double'],Double):
                    return [
                        Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                        Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.condition),operand2=Reg(Registers.XMM0)),
                        JmpCC(Cond_code=Cond_code.NE,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
                        ]
            elif  self.get_type(tacky_ast.condition) == AssemblyType.double:
                     return [
                        Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                        Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.condition),operand2=Reg(Registers.XMM0)),
                        JmpCC(Cond_code=Cond_code.NE,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
                        ]
            return [
            Cmp(assembly_type=self.get_type(tacky_ast.condition),operand1=Imm(0),operand2=self.convert_to_assembly_ast(tacky_ast.condition)),
            JmpCC(Cond_code=Cond_code.NE,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
        ]
            
        elif isinstance(tacky_ast,TackyCopy):
            # #self.symbols[tacky_ast.src.identifier])
            # #tacky_ast)
            # 
            if isinstance(tacky_ast.src,TackyVar) and (
                isinstance(self.symbols[tacky_ast.src.identifier]['val_type'],Structure) ):
                # 
                struct = self.get_structure(tacky_ast.src)
                struct_size =struct.size
                copy_instrs= []
                offset = 0
               
                while struct_size >= 8:
                    copy_instrs.append(Mov(assembly_type=AssemblyType.quadWord,
                                           src=PseudoMem(tacky_ast.src.identifier,offset),
                                           dest=PseudoMem(tacky_ast.dst.identifier,offset)))
                    offset+=8 
                    struct_size -= 8
                
                while struct_size >= 4:
                    copy_instrs.append(Mov(assembly_type=AssemblyType.longWord,
                                           src=PseudoMem(tacky_ast.src.identifier,offset),
                                           dest=PseudoMem(tacky_ast.dst.identifier,offset)))
                    offset+=4
                    struct_size -= 4

                while struct_size >= 1:
                    copy_instrs.append(Mov(assembly_type=AssemblyType.byte,
                                           src=PseudoMem(tacky_ast.src.identifier,offset),
                                           dest=PseudoMem(tacky_ast.dst.identifier,offset)))
                    offset+=1
                    struct_size -= 1
                # #
                #struct.size)
                #copy_instrs)
                # 
                return copy_instrs

                    
                
            
            
            if isinstance(tacky_ast.src,TackyVar) and hasattr(self.symbols[tacky_ast.src.identifier],'Double') and isinstance(self.symbols[tacky_ast.src.identifier]['Double'],Double) and not isinstance(self.symbols[tacky_ast.src.identifier]['attrs'],(StaticAttr,LocalAttr)):
                const_label=''
                value = self.symbols[tacky_ast.src.identifier]['attrs'].init.value.value.value._int
                found = False
                
                for i in self.temp:
                    if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(value)==0):
                        #'Exist')   
                        const_label = self.temp[i]['identifier']
                        value = self.temp[i]['value']
                        found=True 
                 
                        
                 
                 
                if not found:
                    const_label = get_const_label()
                    self.static_const.append( TopLevel.static_const(
                    identifier=const_label,
                    alignment=8 ,
                    init=DoubleInit(value))
                    )
                    # #init)
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
            
           
                return[ 
                    Mov(assembly_type=AssemblyType.double,src=Data(self.convert_to_assembly_ast(const_label),0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),   
                ]
                
                
            if isinstance(tacky_ast.src,TackyConstant) and isinstance(tacky_ast.src.value,ConstDouble): 
                const_label=''
                value = tacky_ast.src.value._int
                found = False

                for i in self.temp:
                    if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(value)==0):
                        #'Exist')   
                        const_label = self.temp[i]['identifier']
                        value = self.temp[i]['value']
                        found=True 
                 
                        
                 
                 
                if not found:
                    const_label = get_const_label()
                    self.static_const.append( TopLevel.static_const(
                    identifier=const_label,
                    alignment=8 ,
                    init=DoubleInit(tacky_ast.src.value._int))
                    )
                    # #init)
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
            
    
                return[ 
                    Mov(assembly_type=AssemblyType.double,src=Data(self.convert_to_assembly_ast(const_label),0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),   
                ]
            else:
                #self.get_type(tacky_ast.dst))
                #self.get_type(tacky_ast.src))
                #self.get_type(tacky_ast.src))
                # 
                # #
                return [
                    Mov(assembly_type=self.get_type(tacky_ast.src),src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
                ]
        elif isinstance(tacky_ast,TackyLabel):
            return [
                Label(indentifier=self.convert_to_assembly_ast(tacky_ast.identifer))
            ]
        elif isinstance(tacky_ast,TackySignExtend):
            # #'here')
            # # tacky_ast)
            # #
            return [
                Movsx(
                    assembly_type_src=self.get_type(tacky_ast.src),
                            assembly_type_dst=self.get_type(tacky_ast.dst) ,
                    
                    src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyZeroExtend):
            # #'tacky zero extend')
            # #self.symbols[tacky_ast.src.identifier])
            # #self.get_type(tacky_ast.src))
            # #self.get_type(tacky_ast.dst))
            # #self.symbols[tacky_ast.dst.identifier])
            # #self.convert_to_assembly_ast(tacky_ast.src))
            # #()
            return [
                MovZeroExtend(assembly_type_src=self.get_type(tacky_ast.src),
                             assembly_type_dst=self.get_type(tacky_ast.dst) 
                            ,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyTruncate):
        
            # #'Truncate')
            # src=self.convert_to_assembly_ast(tacky_ast.src)
            # dest=self.convert_to_assembly_ast(tacky_ast.dst)
            # #src,dest)
            # #
            return [
                Mov(assembly_type=self.get_type(tacky_ast.dst),src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]  
        elif isinstance(tacky_ast,TackyIntToDouble):
            #'tacky int to double')
            
            if isinstance(tacky_ast.src,TackyVar):
                _type =self.symbols[tacky_ast.src.identifier]['val_type']
                # #_type)
            elif isinstance(tacky_ast.src,TackyConstant):
                _type = tacky_ast.src.value._type
            if isinstance(_type,(Char,SChar)):
                # #
                return  [
                    Movsx(
                        assembly_type_src=AssemblyType.byte,
                        assembly_type_dst = AssemblyType.longWord,
                        src=self.convert_to_assembly_ast(tacky_ast.src),
                        dest=Reg(Registers.R10)
                    )
                    , Cvtsi2sd(
                        src_type=AssemblyType.longWord,
                        src=Reg(Registers.R10),
                        dst=self.convert_to_assembly_ast(tacky_ast.dst)
                    )
                    
                ]
            # #
            return Cvtsi2sd(
                src_type=self.get_type(tacky_ast.src),
                src=self.convert_to_assembly_ast(tacky_ast.src),
                dst=self.convert_to_assembly_ast(tacky_ast.dst),
            )
        elif isinstance(tacky_ast,TackyDoubleToInt):
            #'tacky double to int')
            
            if isinstance(tacky_ast.dst,TackyVar):
                _type =self.symbols[tacky_ast.dst.identifier]['val_type']
                #_type)
            elif isinstance(tacky_ast.dst,TackyConstant):
                _type = tacky_ast.dst.value._type
            #_type)
            # #
            if isinstance(_type,(Char,SChar)):
                return  [
                     Cvttsd2si(
                        dst_type=AssemblyType.longWord,
                        src=self.convert_to_assembly_ast(tacky_ast.src),
                        dst=Reg(Registers.R10),
                    ),
                    Mov(
                        assembly_type=AssemblyType.byte,
                        src=Reg(Registers.R10),
                        dest=self.convert_to_assembly_ast(tacky_ast.dst),
                    )
                    
                ]
            
            return Cvttsd2si(
                dst_type=self.get_type(tacky_ast.dst),
                src=self.convert_to_assembly_ast(tacky_ast.src),
                dst=self.convert_to_assembly_ast(tacky_ast.dst),
            )     
        
        elif isinstance(tacky_ast,TackyUIntToDouble):
            #'uint to double')
            # #
            # #tacky_ast)
            if isinstance(tacky_ast.src,TackyVar):
                _type =self.symbols[tacky_ast.src.identifier]['val_type']
                #_type)
                # #
            elif isinstance(tacky_ast.src,TackyConstant):
                
                _type = tacky_ast.src.value._type

           
            if isinstance(_type,UChar):
                #'insizefhauidsi')
                return [
                    MovZeroExtend(
                        assembly_type_src=AssemblyType.byte,
                        assembly_type_dst = AssemblyType.longWord,
                        src=self.convert_to_assembly_ast(tacky_ast.src),
                        dest=Reg(Registers.R10)
                    )
                    , Cvtsi2sd(
                        src_type=AssemblyType.longWord,
                        src=Reg(Registers.R10),
                        dst=self.convert_to_assembly_ast(tacky_ast.dst)
                    )
                    
                ]
            elif isinstance(_type ,UInt):
                return [
                    MovZeroExtend(
                        assembly_type_src=self.get_type(tacky_ast.src),
                        assembly_type_dst=self.get_type(tacky_ast.dst),
                        src=self.convert_to_assembly_ast(tacky_ast.src),
                        dest=Reg(Registers.R10)
                    )
                    , Cvtsi2sd(
                        src_type=AssemblyType.quadWord,
                        src=Reg(Registers.R10),
                        dst=self.convert_to_assembly_ast(tacky_ast.dst)
                    )
                    
                ]
                    
            elif isinstance(_type,  (ULong,Pointer )):
          
                of_label= get_out_of_rng()
                end_label_1 = get_end_label()
                # #'returned')
                # #
                return [
                    Cmp(assembly_type=AssemblyType.quadWord, operand1=Imm(0), operand2=self.convert_to_assembly_ast(tacky_ast.src)),
                    JmpCC(Cond_code=Cond_code.L,indentifier=of_label),
                    Cvtsi2sd(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.src), self.convert_to_assembly_ast(tacky_ast.dst)),
                    Jmp(indentifier=end_label_1),
                    Label(indentifier=of_label),
                    Mov(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.src), Reg(Registers.R10)),
                    Mov(AssemblyType.quadWord, Reg(Registers.R10), Reg(Registers.R11)),
                    Unary(UnaryOperator.SHR, AssemblyType.quadWord, Reg(Registers.R11)),
                    Binary(BinaryOperator.AND, AssemblyType.quadWord, Imm(1), Reg(Registers.R10)),
                    Binary(BinaryOperator.OR, AssemblyType.quadWord, Reg(Registers.R10), Reg(Registers.R11)),
                    Cvtsi2sd(AssemblyType.quadWord, Reg(Registers.R11), self.convert_to_assembly_ast(tacky_ast.dst)),
                    Binary(BinaryOperator.ADD, AssemblyType.double, self.convert_to_assembly_ast(tacky_ast.dst), self.convert_to_assembly_ast(tacky_ast.dst)),
                    Label(indentifier=end_label_1),
                ] 
            else:
                #'not double')
                raise SyntaxError('Invalid instr',tacky_ast)
                
        elif isinstance(tacky_ast,TackyDoubleToUInt):
            #'tacky double to u int')
            
            if isinstance(tacky_ast.src,TackyVar):
                _type =self.symbols[tacky_ast.src.identifier]['val_type']
               
            elif isinstance(tacky_ast.src,TackyConstant):
                _type = tacky_ast.src.value._type
                
            if isinstance(_type,(ULong,Pointer)):
                #* Create temporary label
                const_label = get_upper_bound()
                
                #* Set value
                
                value = 9223372036854775808.0

                
                #* set boolean flag found
                found =False
                
                #* Check for existing static const with same alignment and value in table
                for i in self.temp:
                    if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(value)==0):
                        const_label = self.temp[i]['identifier']
                        value =self.temp[i]['value']
                        found=True 
                    else:
                        continue 
                
                #* Check condition based oh flag , if not found , insert a static character in symbol table and temp table
                if not found:
                    self.static_const.append(TopLevel.static_const(
                        identifier=const_label,
                        alignment=8,
                        init=value,
                    ))
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
                end_label = get_end_label()
                return [
                            Cmp(assembly_type=AssemblyType.double, operand1=Data(const_label,0), operand2=self.convert_to_assembly_ast(tacky_ast.src)),
                            JmpCC(Cond_code.AE, const_label),
                            Cvttsd2si(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.src), self.convert_to_assembly_ast(tacky_ast.dst)),
                            Jmp(end_label),
                            Label(const_label),
                            Mov(AssemblyType.double, self.convert_to_assembly_ast(tacky_ast.src), Reg(Registers.XMM1)),
                            Binary(BinaryOperator.SUBTRACT, AssemblyType.double, Data(const_label,0),
                            Reg(Registers.XMM1)),
                            Cvttsd2si(AssemblyType.quadWord, Reg(Registers.XMM1), self.convert_to_assembly_ast(tacky_ast.dst)),
                            Mov(AssemblyType.quadWord, Imm(9223372036854775808), Reg(Registers.AX)),
                            Binary(BinaryOperator.ADD, AssemblyType.quadWord, Reg(Registers.AX), self.convert_to_assembly_ast(tacky_ast.dst)),
                            Label(end_label),
                ]
            
            
            elif isinstance(_type,UChar):
                return [
                    Cvttsd2si(dst_type=AssemblyType.longWord, src=self.convert_to_assembly_ast(tacky_ast.src), dst=Reg(Registers.R10)),
                    Mov(assembly_type=AssemblyType.byte,src= Reg(Registers.R10), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                 ] 
            else:
                
                 return [
                    Cvttsd2si(dst_type=AssemblyType.quadWord, src=self.convert_to_assembly_ast(tacky_ast.src), dst=Reg(Registers.R10)),
                    Mov(assembly_type=AssemblyType.quadWord,src= Reg(Registers.R10), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                 ]
        elif isinstance(tacky_ast,TackyLoad):
            #tacky_ast.src_ptr,self.symbols[tacky_ast.src_ptr.identifier])
            #tacky_ast.dst,self.symbols[tacky_ast.dst.identifier])
            
            # #()
            if (isinstance(tacky_ast.src_ptr,TackyVar) and isinstance(tacky_ast.dst,TackyVar)) and (
                isinstance(self.symbols[tacky_ast.dst.identifier]['val_type'],Structure)):
                # #('here')
                struct = self.get_structure(tacky_ast.dst)
                struct_size =struct.size
               
                offset = 0 
               
                load_instrs = []
                if struct_size>=8:
                    load_instrs.append(Mov(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.src_ptr), Reg(Registers.AX)))
                    
                elif struct_size>=4:
                    load_instrs.append(Mov(AssemblyType.longWord, self.convert_to_assembly_ast(tacky_ast.src_ptr), Reg(Registers.AX)))
                else:
                    load_instrs.append(Mov(AssemblyType.byte, self.convert_to_assembly_ast(tacky_ast.src_ptr), Reg(Registers.AX)))
                    
                    
                    
                
                while struct_size >= 8:
                    load_instrs.append(Mov(assembly_type=AssemblyType.quadWord,
                                           src=Memory(Reg(Registers.AX),offset),
                                           dest=PseudoMem(tacky_ast.dst.identifier,offset))),
                    offset+=8 
                    struct_size -= 8
                
                while struct_size >= 4:
                    load_instrs.append(Mov(assembly_type=AssemblyType.longWord,
                                           src=Memory(Reg(Registers.AX),offset),
                                           dest=PseudoMem(tacky_ast.dst.identifier,offset))),
                    offset+=4
                    struct_size -= 4

                while struct_size >= 1:
                    load_instrs.append(Mov(assembly_type=AssemblyType.byte,
                                           src=Memory(Reg(Registers.AX),offset),
                                           dest=PseudoMem(tacky_ast.dst.identifier,offset))),
                    offset+=1
                    struct_size -= 1
                #struct.size)
                #load_instrs)
                # 
                return load_instrs
            
            return [
                Mov(self.get_type(tacky_ast.src_ptr), self.convert_to_assembly_ast(tacky_ast.src_ptr), Reg(Registers.AX)),
                Mov(self.get_type(tacky_ast.dst), Memory(Reg(Registers.AX), 0), self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyStore):
            
            # #self.symbols[tacky_ast.src.identifier])
            # #self.symbols[tacky_ast.dst_ptr.identifier])
            
            # 
            if isinstance(tacky_ast.dst_ptr,TackyVar) and isinstance(tacky_ast.src,TackyVar)  and (
                isinstance(self.symbols[tacky_ast.src.identifier]['val_type'],Structure)):
                struct = self.get_structure(tacky_ast.src)
                struct_size =struct.size
                offset = 0
             
                
                load_instrs = []
                if struct_size>=8:
                    load_instrs.append(Mov(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.dst_ptr), Reg(Registers.AX)))
                    
                elif struct_size>=4:
                    load_instrs.append(Mov(AssemblyType.longWord, self.convert_to_assembly_ast(tacky_ast.dst_ptr), Reg(Registers.AX)))
                else:
                    load_instrs.append(Mov(AssemblyType.byte, self.convert_to_assembly_ast(tacky_ast.dst_ptr), Reg(Registers.AX)))
                    
                      
                    
                
                while struct_size >= 8:
                    load_instrs.append(Mov(assembly_type=AssemblyType.quadWord,
                                           src=PseudoMem(tacky_ast.src.identifier,offset),
                                           dest=Memory(Reg(Registers.AX),offset)),
                                           )
                    offset+=8 
                    struct_size -= 8
                
                while struct_size >= 4:
                    load_instrs.append(Mov(assembly_type=AssemblyType.longWord,
                                           src=PseudoMem(tacky_ast.src.identifier,offset),
                                           dest=Memory(Reg(Registers.AX),offset)),
                                           )
                    offset+=4
                    struct_size -= 4

                while struct_size >= 1:
                    load_instrs.append(Mov(assembly_type=AssemblyType.byte,
                                           src=PseudoMem(tacky_ast.src.identifier,offset),
                                           dest=Memory(Reg(Registers.AX),offset)),
                                           )
                    offset+=1
                    struct_size -= 1
          
                return load_instrs
            return [
                Mov(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.dst_ptr), Reg(Registers.AX)),
                Mov(self.get_type(tacky_ast.src),self.convert_to_assembly_ast(tacky_ast.src), Memory(Reg(Registers.AX), 0))
            ]       
        elif isinstance(tacky_ast,TackyGetAddress):
            #self.convert_to_assembly_ast(tacky_ast.src)
                #   )
            # #
            return [
                Lea(src=self.convert_to_assembly_ast(tacky_ast.src),
                    dst=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        # elif isinstance(tacky_ast,TackyCopyToOffSet):
        #     # #self.symbols[tacky_ast.src.identifier])
        #     # #
        #     if (isinstance(tacky_ast.dst,TackyVar)) and (
        #         isinstance(self.symbols[tacky_ast.dst.identifier]['val_type'],Structure)):
        #         element_size = self.get_type(tacky_ast.src)
        #         if element_size == AssemblyType.double:
        #             element_size = 16
        #         elif element_size == AssemblyType.longWord:
        #             element_size = 4 
        #         elif element_size == AssemblyType.quadWord:
        #             element_size = 8
        #         elif element_size == AssemblyType.byte:
        #             element_size = 1
        #         load_instrs = []
              
        #         offset = tacky_ast.offset
        #         offset = tacky_ast.offset
        #         while element_size>=8:
                    
        #             load_instrs.append(Mov(assembly_type=AssemblyType.quadWord,
        #                                    src=self.convert_to_assembly_ast(tacky_ast.src),
        #                                    dest=PseudoMem(tacky_ast.dst.identifier,offset)))
        #             offset+=8 
        #             element_size-=8 
                
        #         while element_size >= 4:
        #             load_instrs.append(Mov(assembly_type=AssemblyType.longWord,
                                       
        #                                    src=self.convert_to_assembly_ast(tacky_ast.src),
                                           
        #                                    dest=PseudoMem(tacky_ast.dst.identifier,offset)))
        #             offset+=4
        #             element_size-=4
                    
                   

        #         while element_size >= 1:
        #             load_instrs.append(Mov(assembly_type=AssemblyType.byte,
        #                                    src=self.convert_to_assembly_ast(tacky_ast.src),
        #                                    dest=PseudoMem(tacky_ast.dst.identifier,offset)))
        #             offset+=1
        #             element_size-=1
                    
        #         # #
        #         return load_instrs
 
        #     return [
        #         Mov(self.get_type(tacky_ast.src), self.convert_to_assembly_ast(tacky_ast.src), PseudoMem(name=tacky_ast.dst.identifier,size=tacky_ast.offset)),
        #     ]  
        
        
        elif isinstance(tacky_ast, TackyCopyToOffSet):
            # #self.symbols[tacky_ast.src.identifier])
            # # if isinstance(tacky_ast.src, TackyVar):
            # #self.symbols[tacky_ast.src.identifier])
            # #self.symbols[tacky_ast.dst.identifier])
            #     # #
            
            # 
            if (isinstance(tacky_ast.src,TackyVar )and 
                isinstance(self.symbols[tacky_ast.src.identifier]['val_type'],Structure) ):
                # element_size = self.get_type(tacky_ast.src)
                # #('aas')
                
                struct = self.get_structure(tacky_ast.src)
                element_size = struct.size 
       
           

                load_instrs = []

                src_offset = 0  # source offset starts from 0
                dst_offset = tacky_ast.offset  # destination offset is provided
               

                while element_size >= 8:
                        load_instrs.append(Mov(
                            assembly_type=AssemblyType.quadWord,
                            src=PseudoMem(tacky_ast.src.identifier, src_offset),
                            dest=PseudoMem(tacky_ast.dst.identifier, dst_offset)
                        ))
                        src_offset += 8
                        dst_offset += 8
                        element_size -= 8

                while element_size >= 4:
                        load_instrs.append(Mov(
                            assembly_type=AssemblyType.longWord,
                            src=PseudoMem(tacky_ast.src.identifier, src_offset),
                            dest=PseudoMem(tacky_ast.dst.identifier, dst_offset)
                        ))
                        src_offset += 4
                        dst_offset += 4
                        element_size -= 4

                while element_size >= 1:
                        load_instrs.append(Mov(
                            assembly_type=AssemblyType.byte,
                            src=PseudoMem(tacky_ast.src.identifier, src_offset),
                            dest=PseudoMem(tacky_ast.dst.identifier, dst_offset)
                        ))
                        src_offset += 1
                        dst_offset += 1
                        element_size -= 1

                return load_instrs
           
    
            return [
                Mov(
                    self.get_type(tacky_ast.src),
                    self.convert_to_assembly_ast(tacky_ast.src),
                    dest=PseudoMem(name=tacky_ast.dst.identifier,size=tacky_ast.offset)
                ),
            ]

        # elif isinstance(tacky_ast,TackyCopyFromOffSet):
        #     #tacky_ast)
        #     # #
        #     if (isinstance(tacky_ast.src,TackyVar) and isinstance(tacky_ast.dst,TackyVar)) and (
        #         isinstance(self.symbols[tacky_ast.src.identifier]['val_type'],Structure)):
        #         struct = self.get_structure(tacky_ast.src)
        #         struct_size =struct.size
        #         # offset = tacky_ast.offset
        #         load_instrs = []
        #         # struct_size +=tacky_ast.offset    
        #         element_size = self.get_type(tacky_ast.dst)
        #         if element_size == AssemblyType.double:
        #             element_size = 16 
        #         elif element_size == AssemblyType.longWord:
        #             element_size = 4 
        #         elif element_size == AssemblyType.quadWord:
        #             element_size = 8
        #         elif element_size == AssemblyType.byte:
        #             element_size = 1
        #         elif isinstance(element_size,AssemblyType.byteArray):
        #             element_size = element_size.size
        #         load_instrs = []
        #         offset = tacky_ast.offset
            
                
        #         while element_size >= 8:
        #             load_instrs.append(Mov(assembly_type=AssemblyType.quadWord,
        #                                    src=PseudoMem(tacky_ast.src.identifier,offset), 
        #                                    dest=self.convert_to_assembly_ast(tacky_ast.dst)))
        #             offset-=8 
        #             element_size -= 8
                
        #         while element_size >= 4:
        #             load_instrs.append(Mov(assembly_type=AssemblyType.longWord,
        #                                     src=PseudoMem(tacky_ast.src.identifier,offset), 
        #                                    dest=self.convert_to_assembly_ast(tacky_ast.dst)))
        #             offset-=4
        #             element_size -= 4


        #         while element_size >= 1:
        #             load_instrs.append(Mov(assembly_type=AssemblyType.byte,
        #                                     src=PseudoMem(tacky_ast.src.identifier,offset), 
        #                                    dest=self.convert_to_assembly_ast(tacky_ast.dst)))
        #             offset-=1
        #             element_size -= 1
        #         #load_instrs)                      
        #         # #
        #         return load_instrs
        #     #'# from ')
        #     # #
        #     return [
        #         Mov(self.get_type(tacky_ast.src), self.convert_to_assembly_ast(tacky_ast.src),
        #                                    dest=PseudoMem(tacky_ast.dst.identifier,tacky_ast.offset))
                    
        #     ]   
        elif isinstance(tacky_ast, TackyCopyFromOffSet):
            #self.symbols[tacky_ast.dst.identifier])
            # 
            if (isinstance(tacky_ast.dst, TackyVar) and 
                isinstance(self.symbols[tacky_ast.dst.identifier]['val_type'], Structure)):
                 
                # #('aas')
                
                struct = self.get_structure(tacky_ast.dst)
                struct_size = struct.size
                element_size = struct_size
                load_instrs = []
                # element_size = self.get_type(tacky_ast.dst)

                # if element_size == AssemblyType.double:
                #     element_size = 16 
                # elif element_size == AssemblyType.longWord:
                #     element_size = 4 
                # elif element_size == AssemblyType.quadWord:
                #     element_size = 8
                # elif element_size == AssemblyType.byte:
                #     element_size = 1
                # elif isinstance(element_size, AssemblyType.byteArray):
                #     element_size = element_size.size

                src_offset = tacky_ast.offset
                dst_offset = 0  # Start copying into destination from offset 0

                #f"Start copying: src_offset={src_offset}, total element_size={element_size}")

                while element_size >= 8:
                    load_instrs.append(Mov(
                        assembly_type=AssemblyType.quadWord,
                        src=PseudoMem(tacky_ast.src.identifier, src_offset),
                        dest=PseudoMem(tacky_ast.dst.identifier, dst_offset)
                    ))
                    src_offset += 8
                    dst_offset += 8
                    element_size -= 8

                while element_size >= 4:
                    load_instrs.append(Mov(
                        assembly_type=AssemblyType.longWord,
                        src=PseudoMem(tacky_ast.src.identifier, src_offset),
                        dest=PseudoMem(tacky_ast.dst.identifier, dst_offset)
                    ))
                    src_offset += 4
                    dst_offset += 4
                    element_size -= 4

                while element_size >= 1:
                    load_instrs.append(Mov(
                        assembly_type=AssemblyType.byte,
                        src=PseudoMem(tacky_ast.src.identifier, src_offset),
                        dest=PseudoMem(tacky_ast.dst.identifier, dst_offset)
                    ))
                    src_offset += 1
                    dst_offset += 1
                    element_size -= 1

                #"Generated MOVs:")
                # for instr in load_instrs:
                    #instr)

                return load_instrs

          
            return [
                Mov(
                    self.get_type(tacky_ast.dst),
                    src=PseudoMem(tacky_ast.src.identifier, tacky_ast.offset),
                    dest=self.convert_to_assembly_ast(tacky_ast.dst),
                )
            ]

        elif isinstance(tacky_ast, TackyAddPtr):
            ptr = self.convert_to_assembly_ast(tacky_ast.ptr)
            index = self.convert_to_assembly_ast(tacky_ast.index)
            dst = self.convert_to_assembly_ast(tacky_ast.dst)
            scale = tacky_ast.scale
            #tacky_ast.index)
            #index)
            #ptr)
            # 
            # #
            if isinstance(index, Imm):  # Constant index case\
                return [
                    Mov(AssemblyType.quadWord, ptr, Reg(Registers.AX)),
                    Lea(Memory(Reg(Registers.AX), index.value * scale), dst,AssemblyType.quadWord)
                ]

            elif scale in (1, 2, 4, 8):  # Variable index with valid scale
              
                return [
                    Mov(AssemblyType.quadWord, ptr, Reg(Registers.AX)),
                    Mov(AssemblyType.quadWord, index, Reg(Registers.DX)),
                    Lea(Indexed(Reg(Registers.AX), Reg(Registers.DX), scale), dst,AssemblyType.quadWord)
                ]

            else:  # Variable index with arbitrary scale (requires multiplication)
                #scale)
                # #
                return [
                    Mov(AssemblyType.quadWord, ptr, Reg(Registers.AX)),
                    Mov(AssemblyType.quadWord, index, Reg(Registers.DX)),
                    Binary(BinaryOperator.MULTIPLY, AssemblyType.quadWord, Imm(scale), Reg(Registers.DX)),
                    Lea(Indexed(Reg(Registers.AX), Reg(Registers.DX), 1), dst,AssemblyType.quadWord)
                ]
        elif isinstance(tacky_ast,int):
            return tacky_ast
        else:
            # #tacky_ast)
            # # error message for unsupported AST nodes and #
            #f"Unsupported AST node: {type(tacky_ast).__name__}", file=sys.stderr)
            sys.exit(1)


    def convert_operator(self,op: str,isSigned) -> str:
        """
        Converts a Tacky unary or binary operator to its Assembly equivalent.
        
        Args:
            op (str): The operator from the Tacky AST. 
                    - For unary operators: 'Complement' or 'Negate'/'Negation'
                    - For binary operators: 'Add', 'Subtract', 'Multiply'
        
        Returns:
            str: A string representing the corresponding Assembly operator, as defined in the 
                UnaryOperator or BinaryOperator enums.
        
        Raises:
            ValueError: If the operator is unrecognized or not supported.
        """
        # Handle unary bitwise NOT operator
        if op == 'Complement':
            return UnaryOperator.NOT  # Corresponds to the bitwise NOT operation, e.g., '~x'
        
        # Handle unary arithmetic negation operators
        elif op in ('Negate', 'Negation'):
            return UnaryOperator.NEG  # Corresponds to the arithmetic negation operation, e.g., '-x'
        
        # Handle binary addition operator
        elif op == 'Add':
            return BinaryOperator.ADD  # Corresponds to the addition operation, e.g., 'x + y'
        
        # Handle binary subtraction operator
        elif op == 'Subtract':
            return BinaryOperator.SUBTRACT  # Corresponds to the subtraction operation, e.g., 'x - y'
        
        # Handle binary multiplication operator
        elif op == 'Multiply':
            return BinaryOperator.MULTIPLY  # Corresponds to the multiplication operation, e.g., 'x * y'
        
        if isSigned:
            if op=='GreaterThan':
                return Cond_code.G
            elif op=='LessThan':
                return Cond_code.L
            elif op=='GreaterOrEqual':
                return Cond_code.GE
            elif op=='LessOrEqual':
                return Cond_code.LE
            elif op=='NotEqual':
                return Cond_code.NE
            elif op=='Equal':
                return Cond_code.E
        elif not isSigned:
            if op=='GreaterThan':
                return Cond_code.A
            elif op=='LessThan':
                return Cond_code.B
            elif op=='GreaterOrEqual':
                return Cond_code.AE
            elif op=='LessOrEqual':
                return Cond_code.BE
            elif op=='NotEqual':
                return Cond_code.NE
            elif op=='Equal':
                return Cond_code.E
        # If the operator does not match any known unary or binary operators, raise an error
        else:
            # Raises a ValueError with a descriptive message indicating the unsupported operator
            raise ValueError(f"Unknown operator: {op}")

