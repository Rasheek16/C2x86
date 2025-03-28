from tacky import *
from assembly_ast import *
from _ast5 import Parameter,Double,UInt,ULong,Int,Long ,Parameter,ConstDouble,ConstInt,ConstLong,ConstUInt,ConstULong,Pointer,Identifier,Null,Array
import sys
from typing import Union, List ,Dict,Optional
from type_classes import *
PARAMETER_REGISTERS = ['DI', 'SI', 'DX', 'CX', 'R8', 'R9']
from instruction_fixer import is_signed_32_bit
from typechecker import isSigned
from tacky_emiter import get_const_label
# from conv.unary import convert_unary
current_param_offset={}
t=0

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
    def __init__(self, defined):
        self.defined=defined 
    def __repr__(self):
        return f'FunEntry(defined={self.defined})'    
    
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
        
class ObjEntry():
    def __init__(self,assembly_type,is_static,is_constant):
        self.assembly_type=assembly_type 
        self.is_static = is_static
        self.is_constant = is_constant
        
        
    def __repr__(self):
        return f'ObjEntry(assembly_type={self.assembly_type}, is_static=True)'    
    

class Converter():
    def __init__(self,symbols):
        self.symbols=symbols
        self.temp={}
        self.static_const=[]
        
    def classify_parameters(self,values:List[Parameter]):
        reg_args=[]
        double_args=[]
        stack_args=[]
        for operand in values:
            type_operand = self.get_param_type(operand._type)
        
            if type_operand == AssemblyType.double:
                if len(double_args)<8:
                    double_args.append(operand)
                else:
                    stack_args.append(operand)
            else:
                if len(reg_args)<6:
                    reg_args.append(operand)
                else:
                    stack_args.append(operand)
        # print('Register arguments',reg_args)
        # print('Double arguments',double_args)
        # print(reg_args)
        # exit()
        return (reg_args,double_args,stack_args)
            
    
    def classify_arguments(self,values):
        reg_args=[]
        double_args=[]
        stack_args=[]
    
        for operand in values:
            print(operand)
            if isinstance(operand,TackyConstant):       
                type_operand = self.get_param_type(operand.value._type)
            else:
                type_operand = self.get_param_type(self.symbols[operand.identifier]['val_type'])
               
            # print(type_operand)
            if type_operand == AssemblyType.double:
                if len(double_args)<8:
                    double_args.append(operand)
                else:
                    stack_args.append(operand)
            else:
                if len(reg_args)<6:
                    reg_args.append(operand)
                else:
                    stack_args.append(operand)
        # print(reg_args)
        # exit()
        return reg_args,double_args,stack_args
            
             
        
        
    def convert_symbol_table(self):
        backend_symbol_table={}
        for name,defn in self.symbols.items():
            if 'fun_type' in defn:                
                backend_symbol_table[name]=FunEntry(defined=self.symbols[name]['attrs'].defined)
            elif 'val_type' in defn:
                static = False
                if isinstance(self.symbols[name]['attrs'],StaticAttr):
                    static=True
                backend_symbol_table[name] = ObjEntry(assembly_type=self.get_param_type(self.symbols[name]['val_type']),is_static=static,is_constant =True)
        
                
        return backend_symbol_table
    
    def get_param_type(self, _type):
        if isinstance(_type, Long):
            return AssemblyType.quadWord
        elif isinstance(_type, ULong) or isinstance(_type, Pointer):
            return AssemblyType.quadWord
        elif isinstance(_type, Int) or isinstance(_type, UInt):
            return AssemblyType.longWord
        elif isinstance(_type, Array):
            element_size = self.get_element_size(_type._type)  # Recursively get base element size
            total_size = element_size * _type._int.value._int # Compute total array size
            new_type = AssemblyType.byteArray(size=total_size,alignment=element_size )
            print(_type)
            print(total_size)
            print(new_type)
            # exit()
            global i
            if i==2:
                print(total_size,element_size)
                # exit()
            i+=1
            # size = self.getembly_size(_type._int.value._int)
            if element_size>16:
                element_size = 16 
            print(element_size)
            # exit()
            return AssemblyType.byteArray(size=total_size,alignment=element_size )  # Return correctly computed ByteArray
        elif isinstance(_type,Pointer):
            # print('Here')
            # exit()
            return self.get_param_type(_type.ref)
        else:
            return AssemblyType.double

    def get_element_size(self, _type):
        """ Recursively fetch the base element size for nested arrays. """
        if isinstance(_type, Double):
            return 8  # Size of Double
        elif isinstance(_type, Int) or isinstance(_type, UInt):
            return 4
        elif isinstance(_type, Long) or isinstance(_type, ULong):
            return 8
        elif isinstance(_type, Pointer):
            return 8
        elif isinstance(_type, Array):
            return self.get_element_size(_type._type) * _type._int.value._int   # Recursive call
        else:
            raise ValueError(f"Unknown type: {_type}")

            

        
    def get_type(self, src):
       
        if isinstance(src, TackyConstant):
            if isinstance(src.value, (ConstInt,ConstUInt)):
                return AssemblyType.longWord
            elif isinstance(src.value,(ConstLong,ConstULong,Pointer)):
                return AssemblyType.quadWord
            
            else:
                return AssemblyType.double
              

        elif isinstance(src, TackyVar):
            var_name = src.identifier
           
            if var_name not in self.symbols:
              
                raise NameError(f"Variable '{var_name}' not found in symbols")
            
            val_type = self.symbols[var_name]['val_type']
           
            if isinstance(val_type,( Int,UInt)) or isinstance(val_type, type(Int)) or isinstance(val_type, type(UInt)):
                return AssemblyType.longWord
            elif isinstance(val_type, (Long,ULong,Pointer)):
                
                return AssemblyType.quadWord
            elif isinstance(val_type, Array):
                _type = val_type
                element_size = self.get_element_size(_type._type)  # Recursively get base element size
                total_size = element_size * _type._int.value._int  # Compute total array size
                new_type = AssemblyType.byteArray(size=total_size,alignment=element_size )
                # print(new_type)
                # exit()
                return AssemblyType.byteArray(size=total_size,alignment=_type._int.value._int ) 
            else:
                return AssemblyType.double
               
                # raise TypeError(f"Unsupported variable type '{val_type}' for '{var_name}'")
        else:
            raise TypeError(f"Unsupported source type: {type(src)}")
                    
                
    def get_assembly_arg_type(val:int):
        if is_signed_32_bit(val):
            return AssemblyType.longWord
        else:
            return AssemblyType.quadWord
            
    def setup_parametes(self,parameters,instr):
        reg_params,double_param,stakc_params = self.classify_parameters(values=parameters)
        
        # print(double_param)
        # exit()
        print(reg_params)
        # exit()
        regsiters = ['DI','SI','DX','CX','R8','R9']
        
        reg_index= 0
        
        if len(reg_params)>0:
            for param in reg_params:
                print(param._type)
                print(self.get_param_type(param._type))  
                # exit()
                
                r = regsiters[reg_index]
              
                instr.append(Mov(assembly_type=self.get_param_type(param._type),src=Reg(r), dest=Pseudo(param.name.name)))
                reg_index+=1
            
        double_regs = [ 'XMM0', 'XMM1', 'XMM2', 'XMM3', 'XMM4', 'XMM5', 'XMM6', 'XMM7' ]
        reg_index = 0
        for param in double_param:
            print('param')  
            
            # exit()
            r = double_regs[reg_index]
            instr.append(Mov(AssemblyType.double, Reg(r), Pseudo(param.name.name)))
         
            reg_index += 1
        offset = 16
        for param in stakc_params:
            print('param')  
            instr.append(Mov(self.get_param_type(param._type), Memory(Reg(Registers.BP),offset), Pseudo(param.name.name)))
            offset += 8
        print(instr)
        # exit()
        return instr

    def convert_to_assembly_ast(self,tacky_ast) :
        # print(self.symbols)
        # exit()
        """
        Converts a Tacky AST into an AssemblyProgram AST.
        
        Args:
            tacky_ast: The root of the Tacky AST to be converted.
        
        Returns:
            An AssemblyProgram instance representing the equivalent assembly code.
        """
        # Handle the top-level Program node
        
        if isinstance(tacky_ast, TackyProgram):
            
            # Recursively convert the function_definition part of the TackyProgram
            assembly_functions = []
            
            for defn in tacky_ast.function_definition:
                
                if isinstance(defn,TackyFunction):
                   
                    assembly_function = self.convert_to_assembly_ast(defn)
                    
                    assembly_functions.append(assembly_function)
                 
                if isinstance(defn,TackyStaticVariable):
                    if isinstance(type(defn._type),type(Int())):
                        alignment = 4
                    else:
                        alignment = 8
                    
                  
                        
                    
                    if isinstance(defn.init,DoubleInit):
                        static_var = TopLevel.static_const(identifier=defn.name,alignment=alignment,init=defn.init)
                    else:
                        static_var = TopLevel.static_var(identifier=defn.name,_global = defn._global,alignment=alignment,init=defn.init)
                    
                  
                    assembly_functions.append(static_var)
                    
            # for i in self.static_const:
            print(self.static_const)
          
            assembly_functions.extend(self.static_const)
            
            backend_Symbol_table=self.convert_symbol_table()
            # exit()
            return AssemblyProgram(
                function_definition=assembly_functions
            ),backend_Symbol_table
            # ,current_param_offset
        
    
        # Handle Function node
        elif isinstance(tacky_ast, TackyFunction):
            params = []
            instructions=[]
            # stack_offset=0
            # # func_stack_offset
            # body=[]
            # # Iterate over each instruction in the TackyFunction
            # # print(instructions)
            #     # Convert each instruction and collect them
            # # print(tacky_ast.params)
            # num_params = len(tacky_ast.params)  # Assuming 'parameters' is a list of function parameters
            # for i, param in enumerate(tacky_ast.params):
            #     # print(self.get_param_type(param._type))
            #     # exit()
            #     # global func_stack_offset
            #     if i < len(PARAMETER_REGISTERS): 
            #         print(param._type)
            #         self.get_param_type(param._type)
            #         print(self.get_param_type(param._type))
            #         # if i==1:
            #         #     # exit()
            #         src_reg = PARAMETER_REGISTERS[i]
             
                    
            #         params.append(
                        
            #             Mov(assembly_type=self.get_param_type(param._type),src=Reg(src_reg), dest=Pseudo(param.name.name))
            #         )
            #         # func_stack_offset=
            #         stack_offset=8
            #     else:
            #         # Parameters passed on the stack
            #         stack_offset =( 16 + (8 * (i - len(PARAMETER_REGISTERS))) ) # 16(%rbp) is the first stack parameter
                  
            #         params.append(
            #             Mov(
            #                 assembly_type=self.get_param_type(param._type),
            #                 src=Stack(stack_offset),
            #                 dest=Pseudo(param.name.name)
            #             )
            #         )
            
            # func_stack_offset = stack_offset
            # # current_param_offset[tacky_ast.name]=-func_stack_offset
            # # print(params)
            params = self.setup_parametes(tacky_ast.params,params)
            print(tacky_ast.params)
            # exit()
            instructions.extend(params)
            
            for instr in tacky_ast.body:
                
                converted_instrs = self.convert_to_assembly_ast(instr)
                
                if isinstance(converted_instrs, list):
                    
                    # If conversion returns a list of instructions, extend the list
                    instructions.extend(converted_instrs)
                else:
                    # Otherwise, append the single instruction
                    instructions.append(converted_instrs)
            # Create an AssemblyFunction with the converted instructions
            
            return TopLevel.assembly_func(
                name=tacky_ast.name,  # Assuming tacky_ast.name is an Identifier
                _global=tacky_ast._global,
                instructions=instructions
            )
        
        elif isinstance(tacky_ast,Identifier):
            return tacky_ast.name
        elif isinstance(tacky_ast,TackyFunCall):
            instructions=[]
            arg_regsiters = ['DI','SI','DX','CX','R8','R9']
            double_regs = [ 'XMM0', 'XMM1', 'XMM2', 'XMM3', 'XMM4', 'XMM5', 'XMM6', 'XMM7' ]
            
            reg_arg,dub_arg,stack_arg=self.classify_arguments(tacky_ast.args)
            stack_padding = 8 if len(stack_arg) % 2 == 1 else 0
            if stack_padding != 0:
                instructions.append(AllocateStack(stack_padding))

                
            reg_index=0
            for tacky_arg in reg_arg:
                r= arg_regsiters[reg_index]
                assembly_arg = self.convert_to_assembly_ast(tacky_arg)
                print(assembly_arg)
                # exit()
                instructions.append(Mov(assembly_type=self.get_type(tacky_arg),src=assembly_arg,dest=Reg(r)))
                reg_index +=1
            reg_index=0
            for tacky_arg in dub_arg:
                r= double_regs[reg_index]
                assembly_arg = self.convert_to_assembly_ast(tacky_arg)
                instructions.append(Mov(assembly_type=AssemblyType.double,src=assembly_arg,dest=Reg(r)))
                reg_index +=1
                
            for tacky_arg in stack_arg[::-1]:
                assembly_arg=self.convert_to_assembly_ast(tacky_arg)
              
                if isinstance(assembly_arg,Reg) or isinstance(assembly_arg,Imm) or self.get_type(tacky_arg)==AssemblyType.quadWord or self.get_type(tacky_arg)==AssemblyType.double :
                    instructions.append(Push(assembly_arg,_type=self.get_type(tacky_arg)))
                else:
                    instructions.append(Mov(assembly_type=self.get_type(tacky_arg),src=assembly_arg,dest=Reg(Registers.AX)))
                    instructions.append(Push(Reg(Registers.AX),_type=AssemblyType.longWord))
                    
            instructions.append(Call(indentifier=tacky_ast.fun_name))
            
            bytes_to_remove = 8 * len(stack_arg)+ stack_padding
            if bytes_to_remove !=0:
                # print('Bytes to remove',bytes_to_remove)
                instructions.append(DeallocateStack(value=bytes_to_remove))
                
            assembly_dst = self.convert_to_assembly_ast(tacky_ast.dst)
            print(self.symbols[tacky_ast.fun_name]['fun_type'].base_type,)
            # exit()
            if isinstance(self.symbols[tacky_ast.fun_name]['fun_type'].base_type, Double):
                # exit()
                instructions.append(Mov(assembly_type=AssemblyType.double,src=Reg(Registers.XMM0),dest=assembly_dst))
            else:
                instructions.append(Mov(assembly_type=self.get_type(tacky_ast.dst),src=Reg(Registers.AX),dest=assembly_dst))
            return instructions
        # Handle Return instruction
        elif isinstance(tacky_ast, TackyReturn):
            #TODO MOFIFICATION OVER HERE
            # if isinstance(tacky_ast)
            tacky_ast.val=tacky_ast.val
            #* Get type of value of a variable        
            if isinstance(tacky_ast.val , TackyVar):
                _type=self.get_type(tacky_ast.val)
            else:
                #* Type of a constant
                _type=self.get_type(tacky_ast.val)
            # print(self.get_param_type(tacky_ast.val))
            # print(_type)
            # exit()
            
            # src=self.convert_to_assembly_ast(tacky_ast.val)
           
            #* CONVERSION OF DOUBLE TYPE TO RETURN 
            if isinstance(tacky_ast.val,TackyConstant) and isinstance(tacky_ast.val.value,ConstDouble):
                    return [
                    Mov(assembly_type=AssemblyType.double,src=self.convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.XMM0)),
                    Ret()
                ]    
           
            #* CONVERT RETURN TO MOV AND RETURN STATEMENT 
            elif _type ==AssemblyType.double:
                 return [
                    Mov(assembly_type=AssemblyType.double,src=self.convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.XMM0)),
                    Ret()
                ]    
            return [
                Mov(assembly_type=_type,src=self.convert_to_assembly_ast(tacky_ast.val), dest=Reg(Registers.AX)),
                Ret()
            ]
    
        # Handle Unary instruction
        elif isinstance(tacky_ast, TackyUnary):        
            # Convert a Unary operation by moving src to dst and applying the operator
            # return convert_unary(self=self,tacky_ast=tacky_ast)
            #* Converison of unary NOT
            if tacky_ast.operator ==TackyUnaryOperator.NOT:
                print('Unary Not')
                src=self.convert_to_assembly_ast(tacky_ast.src)
                dest=self.convert_to_assembly_ast(tacky_ast.dst)
              
                
                #* Converion of double by taking XOR with Register
                if self.get_type(tacky_ast.src) == AssemblyType.double:
                    # exit()
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
                                    # print(value)
                                    # exit()
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
                            print(const_label)
                            # exit()
                            return[ 
                                #* Move instruction 
                                Mov(assembly_type=AssemblyType.double,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                                
                                #* Binary instruction
                                Binary(assembly_type=AssemblyType.double,operator=BinaryOperator.XOR,src1=Data(const_label),src2=self.convert_to_assembly_ast(tacky_ast.dst)),
                                
                                
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
            print(tacky_ast)
            # exit()
            # print(tacky_ast.operator)
            # print('Binary operations')
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

                print(self.convert_to_assembly_ast(tacky_ast.src2))
                # exit()
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
                    # print(tacky_ast,self.get_type(tacky_ast.src1))
                    if self.get_type(tacky_ast.src1)==AssemblyType.double:
                        # exit()
                    
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
                # print('Inside remainder')
                # print('Inside ')
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
                    # print(self.symbols[tacky_ast.src1.identifier])
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
                    # exit()
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
                # print(self.get_type(tacky_ast.src1))
                # exit()
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
                    if type(self.symbols[tacky_ast.src1.identifier]['val_type']) in (Int, Long):
                        t=Int()  
                    else:
                        t=UInt()
                else:
                    if isinstance(tacky_ast.src1,TackyConstant) and isinstance(tacky_ast.src1.value,(ConstInt,ConstLong)):
                        t=Int()
                    else:
                        t=UInt()
             
                     
                  
                if isSigned(t)==True:
                    
                    # exit()
                    # print(self.symbols[tacky_ast.dst.identifier])
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src2),operand1=self.convert_to_assembly_ast(tacky_ast.src2),
                                operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,True),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                else:
                    # print(self.convert_operator(tacky_ast.operator,False))
                    # exit()
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src2),operand1=self.convert_to_assembly_ast(tacky_ast.src2),
                                operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            #* CHNAGED THE ASSEMBLY TYPE FROM QUAD WORD TO DST
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,False),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                    
            elif tacky_ast.operator == TackyBinaryOperator.GREATER_THAN:
                # print(self.symbols[tacky_ast.src1.identifier])
                
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
                    # exit()
                    
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
            if isinstance(tacky_ast.value,(ConstInt,ConstLong,ConstUInt,ConstULong)):
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
                    # print(self.temp)
                    # exit()
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
    
                return Data(name=const_label)
                
                # raise ValueError('Found Double const value')
            return Imm(tacky_ast.value)
            # Convert a constant value into an Imm operand
        
        # elif isinstance(tacky_ast,)
        # elif isinstance(tacky_ast,AssemblyStaticVariable):
        # Handle Variable operand
        elif isinstance(tacky_ast, TackyVar):
            # Convert a variable into a Pseudo operand
            # print(tacky_ast)
            # print(self.symbols[tacky_ast.identifier])
            # exit()
            # print('here',self.symbols[tacky_ast.identifier])
            if isinstance(self.symbols[tacky_ast.identifier]['val_type'],Array):
                return PseudoMem(tacky_ast.identifier,0)
            # exit()
            return Pseudo(tacky_ast.identifier)
        elif isinstance(tacky_ast,TackyJump):
            return [Jmp(indentifier=tacky_ast.target)]
        elif isinstance(tacky_ast,TackyJumpIfZero):
            # print(self.symbols[tacky_ast.condition.identifier])
            # print(self.symbols[tacky_ast.condition.identifier])
            # exit()
            # exit()
            if isinstance(tacky_ast.condition,TackyVar) and (isinstance(self.symbols[tacky_ast.condition.identifier]['Double'],Double) or isinstance(self.symbols[tacky_ast.condition.identifier]['val_type'],Double)):
                # print('Double')
                # exit()
                return [
                    Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                    Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.condition),operand2=Reg(Registers.XMM0)),
                    JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
                    ]
            elif self.get_type(tacky_ast.condition) == AssemblyType.double:
                     return [
                        Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                        Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.condition),operand2=Reg(Registers.XMM0)),
                        JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
                        ]
            
                
            return [
                Cmp(assembly_type=self.get_type(tacky_ast.condition),operand1=Imm(0),operand2=self.convert_to_assembly_ast(tacky_ast.condition)),
                JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
            ]
        elif isinstance(tacky_ast,TackyJumpIfNotZero):
            if isinstance(tacky_ast.condition,TackyVar) and isinstance(self.symbols[tacky_ast.condition.identifier]['Double'],Double):
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
            # print(tacky_ast)
            # print(self.symbols[tacky_ast.src.identifier]['attrs'].init.value.value.value._int)
            # exit()
            # print( self.symbols[tacky_ast.src.identifier]['attrs'])
            if isinstance(tacky_ast.src,TackyVar) and isinstance(self.symbols[tacky_ast.src.identifier]['Double'],Double) and not isinstance(self.symbols[tacky_ast.src.identifier]['attrs'],(StaticAttr,LocalAttr)):
                const_label=''
                value = self.symbols[tacky_ast.src.identifier]['attrs'].init.value.value.value._int
                found = False
                
                for i in self.temp:
                    if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(value)==0):
                        print('Exist')   
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
                    # print(init)
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
            
    
                return[ 
                    Mov(assembly_type=AssemblyType.double,src=Data(self.convert_to_assembly_ast(const_label)),dest=self.convert_to_assembly_ast(tacky_ast.dst)),   
                ]
                
                
            if isinstance(tacky_ast.src,TackyConstant) and isinstance(tacky_ast.src.value,ConstDouble): 
                const_label=''
                value = tacky_ast.src.value._int
                found = False

                for i in self.temp:
                    if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(value)==0):
                        print('Exist')   
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
                    # print(init)
                    self.temp[const_label] = {
                        'identifier':const_label,
                        'alignment':8,
                        'value':value,
                        
                    }
            
    
                return[ 
                    Mov(assembly_type=AssemblyType.double,src=Data(self.convert_to_assembly_ast(const_label)),dest=self.convert_to_assembly_ast(tacky_ast.dst)),   
                ]
            else:
                return [
                    Mov(assembly_type=self.get_type(tacky_ast.src),src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
                ]
        elif isinstance(tacky_ast,TackyLabel):
            # print(tacky_ast.identifer)
            return [
                Label(indentifier=self.convert_to_assembly_ast(tacky_ast.identifer))
            ]
        elif isinstance(tacky_ast,TackySignExtend):
            return [
                Movsx(src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyZeroExtend):
            return [
                MovZeroExtend(src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyTruncate):
        
            # print(
            #      Mov(assembly_type=AssemblyType.longWord,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            
            # )
            # exit()
            return [
                Mov(assembly_type=AssemblyType.longWord,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]  
        elif isinstance(tacky_ast,TackyIntToDouble):
            # exit()
            
            return Cvtsi2sd(
                src_type=self.get_type(tacky_ast.src),
                src=self.convert_to_assembly_ast(tacky_ast.src),
                dst=self.convert_to_assembly_ast(tacky_ast.dst),
            )
        elif isinstance(tacky_ast,TackyDoubleToInt):
            return Cvttsd2si(
                dst_type=self.get_type(tacky_ast.dst),
                src=self.convert_to_assembly_ast(tacky_ast.src),
                dst=self.convert_to_assembly_ast(tacky_ast.dst),
            )     
        elif isinstance(tacky_ast,TackyUIntToDouble):
            print(tacky_ast)
            if isinstance(tacky_ast.src,TackyVar):
                _type =self.symbols[tacky_ast.src.identifier]['val_type']
                print(_type)
            elif isinstance(tacky_ast.src,TackyConstant):
                _type = tacky_ast.src.value._type
                # print(_type)
                # exit()
            
                # exit()
            if isinstance(_type ,UInt):
                # print('here')
                # exit()
                return [
                    MovZeroExtend(
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
                # print('returned')
                # exit()
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
                raise SyntaxError('Invalid instr',tacky_ast)
                sys.exit(1)     
        elif isinstance(tacky_ast,TackyDoubleToUInt):
            if isinstance(tacky_ast.src,TackyVar):
                _type =self.symbols[tacky_ast.src.identifier]['val_type']
                # print(_type)
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
                            Cmp(assembly_type=AssemblyType.double, operand1=Data(const_label), operand2=self.convert_to_assembly_ast(tacky_ast.src)),
                            JmpCC(Cond_code.AE, const_label),
                            Cvttsd2si(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.src), self.convert_to_assembly_ast(tacky_ast.dst)),
                            Jmp(end_label),
                            Label(const_label),
                            Mov(AssemblyType.double, self.convert_to_assembly_ast(tacky_ast.src), Reg(Registers.XMM1)),
                            Binary(BinaryOperator.SUBTRACT, AssemblyType.double, Data(const_label),
                            Reg(Registers.XMM1)),
                            Cvttsd2si(AssemblyType.quadWord, Reg(Registers.XMM1), self.convert_to_assembly_ast(tacky_ast.dst)),
                            Mov(AssemblyType.quadWord, Imm(9223372036854775808), Reg(Registers.AX)),
                            Binary(BinaryOperator.ADD, AssemblyType.quadWord, Reg(Registers.AX), self.convert_to_assembly_ast(tacky_ast.dst)),
                            Label(end_label),
                ]
            else:
                
                 return [
                    Cvttsd2si(dst_type=AssemblyType.quadWord, src=self.convert_to_assembly_ast(tacky_ast.src), dst=Reg(Registers.R10)),
                    Mov(assembly_type=AssemblyType.quadWord,src= Reg(Registers.R10), dest=self.convert_to_assembly_ast(tacky_ast.dst))
                 ]
        elif isinstance(tacky_ast,TackyLoad):
            return [
                Mov(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.src_ptr), Reg(Registers.AX)),
                Mov(self.get_type(tacky_ast.dst), Memory(Reg(Registers.AX), 0),self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyStore):
            return [
                Mov(AssemblyType.quadWord, self.convert_to_assembly_ast(tacky_ast.dst_ptr), Reg(Registers.AX)),
                Mov(self.get_type(tacky_ast.src),self.convert_to_assembly_ast(tacky_ast.src), Memory(Reg(Registers.AX), 0))
            ]       
        elif isinstance(tacky_ast,TackyGetAddress):
            return [
                Lea(src=self.convert_to_assembly_ast(tacky_ast.src),
                    dst=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        elif isinstance(tacky_ast,TackyCopyToOffSet):
            return [
                Mov(self.get_type(tacky_ast.src), self.convert_to_assembly_ast(tacky_ast.src), PseudoMem(name=self.convert_to_assembly_ast(tacky_ast.dst),size=tacky_ast.offset)),
            ]   
        elif isinstance(tacky_ast, TackyAddPtr):
            ptr = self.convert_to_assembly_ast(tacky_ast.ptr)
            index = self.convert_to_assembly_ast(tacky_ast.index)
            dst = self.convert_to_assembly_ast(tacky_ast.dst)
            scale = tacky_ast.scale
            # print(tacky_ast.index)
            print(scale)
            # exit()
            if isinstance(index, Imm):  # Constant index case\
                return [
                    Mov(AssemblyType.quadWord, ptr, Reg(Registers.AX)),
                    Lea(Memory(Reg(Registers.AX), index.value * scale), dst)
                ]

            elif scale in (1, 2, 4, 8):  # Variable index with valid scale
              
                return [
                    Mov(AssemblyType.quadWord, ptr, Reg(Registers.AX)),
                    Mov(AssemblyType.quadWord, index, Reg(Registers.DX)),
                    Lea(Indexed(Reg(Registers.AX), Reg(Registers.DX), scale), dst)
                ]

            else:  # Variable index with arbitrary scale (requires multiplication)
                print(scale)
                # exit()
                return [
                    Mov(AssemblyType.quadWord, ptr, Reg(Registers.AX)),
                    Mov(AssemblyType.quadWord, index, Reg(Registers.DX)),
                    Binary(BinaryOperator.MULTIPLY, AssemblyType.quadWord, Imm(scale), Reg(Registers.DX)),
                    Lea(Indexed(Reg(Registers.AX), Reg(Registers.DX), 1), dst)
                ]
        elif isinstance(tacky_ast,int):
            return tacky_ast
        else:
            # print(tacky_ast)
            # Print error message for unsupported AST nodes and exit
            print(f"Unsupported AST node: {type(tacky_ast).__name__}", file=sys.stderr)
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

