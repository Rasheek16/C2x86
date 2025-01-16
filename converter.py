from tacky import *
from assembly_ast import *
from _ast5 import Int , Long,ConstInt,ConstLong,ConstUInt,ConstULong,UInt,ULong
import sys
from typing import Union, List ,Dict,Optional
from type_classes import *
PARAMETER_REGISTERS = ['DI', 'SI', 'DX', 'CX', 'R8', 'R9']
from instruction_fixer import is_signed_32_bit
from typechecker import isSigned
current_param_offset={}


class FunEntry():
    def __init__(self, defined):
        self.defined=defined 
    def __repr__(self):
        return f'FunEntry(defined={self.defined})'    
    
        # super(CLASS_NAME, self).__init__(*args, **kwargs)
        
class ObjEntry():
    def __init__(self,assembly_type,is_static):
        self.assembly_type=assembly_type 
        self.is_static = is_static
        
    def __repr__(self):
        return f'ObjEntry(assembly_type={self.assembly_type}, is_static=True)'    
    

class Converter():
    def __init__(self,symbols):
        self.symbols=symbols
        
        
    def convert_symbol_table(self):
        backend_symbol_table={}
        for name,defn in self.symbols.items():
            if 'fun_type' in defn:
                # pass
                # print(self.symbols[name]['attrs'].defined)
                backend_symbol_table[name]=FunEntry(defined=self.symbols[name]['attrs'].defined)
            elif 'val_type' in defn:
                # print(self.symbols[name])
                static = False
                if isinstance(self.symbols[name]['attrs'],StaticAttr):
                    static=True
                backend_symbol_table[name] = ObjEntry(assembly_type=self.get_param_type(self.symbols[name]['val_type']),is_static=static)
                    # print('True')
        return backend_symbol_table
    
    def get_param_type(self,_type):
        if isinstance(_type,Long):
            return AssemblyType.quadWord
        # elif isinstance(_type,Int) or isinstance(_type,UInt):
        #     return AssemblyType.longWord
            
        elif  isinstance(_type,ULong):
            return AssemblyType.quadWord
            
        return AssemblyType.longWord
        
        
    def get_type(self, src):
        if isinstance(src, TackyConstant):
            if isinstance(src.value, (ConstInt,ConstUInt)):
                return AssemblyType.longWord
            elif isinstance(src.value, (ConstLong,ConstULong)):
                return AssemblyType.quadWord
            else:
                print(src)
                raise TypeError(f"Unsupported constant type: {type(src.value)}")

        elif isinstance(src, TackyVar):
            var_name = src.identifier
            # print(self.symbols)
            # exit()
            if var_name not in self.symbols:
                # print(var_name)
                # print(self.symbols)
                raise NameError(f"Variable '{var_name}' not found in symbols")
            # print(self.symbols[var_name])
            val_type = self.symbols[var_name]['val_type']
            # print(self.symbols[var_name])
            # Direct type check
            if isinstance(val_type,( Int,UInt)) or isinstance(val_type, type(Int)) or isinstance(val_type, type(UInt)):
               
                return AssemblyType.longWord
            elif isinstance(val_type, (Long,ULong)):
                return AssemblyType.quadWord
            else:
               
                raise TypeError(f"Unsupported variable type '{val_type}' for '{var_name}'")
        else:
            raise TypeError(f"Unsupported source type: {type(src)}")
                    
                
    def get_assembly_arg_type(val:int):
        if is_signed_32_bit(val):
            return AssemblyType.longWord
        else:
            return AssemblyType.quadWord
            
        

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
                    # print(func.name)
                    assembly_function = self.convert_to_assembly_ast(defn)
                    assembly_functions.append(assembly_function)
                    # print('here')
                elif isinstance(defn,TackyStaticVariable):
                    if isinstance(type(defn._type),type(Int())):
                        
                        alignment = 4
                    else:
                        alignment = 8

                    static_var = TopLevel.static_var(identifier=defn.name,_global = defn._global,alignment=alignment,init=defn.init)
                    # print(static_var)
                    assembly_functions.append(static_var)
                    
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
            stack_offset=0
            # func_stack_offset
            body=[]
            # Iterate over each instruction in the TackyFunction
            # print(instructions)
                # Convert each instruction and collect them
            # print(tacky_ast.params)
            num_params = len(tacky_ast.params)  # Assuming 'parameters' is a list of function parameters
            for i, param in enumerate(tacky_ast.params):
                # print(self.get_param_type(param._type))
                # exit()
                # global func_stack_offset
                if i < len(PARAMETER_REGISTERS): 
                    print(param._type)
                    self.get_param_type(param._type)
                    print(self.get_param_type(param._type))
                    # if i==1:
                    #     # exit()
                    src_reg = PARAMETER_REGISTERS[i]
             
                    
                    params.append(
                        
                        Mov(assembly_type=self.get_param_type(param._type),src=Reg(src_reg), dest=Pseudo(param.name.name))
                    )
                    # func_stack_offset=
                    stack_offset=8
                else:
                    # Parameters passed on the stack
                    stack_offset =( 16 + (8 * (i - len(PARAMETER_REGISTERS))) ) # 16(%rbp) is the first stack parameter
                    # print('param',param)
                    # print(param._type)
                    # exit()
                    params.append(
                        Mov(
                            assembly_type=self.get_param_type(param._type),
                            src=Stack(stack_offset),
                            dest=Pseudo(param.name.name)
                        )
                    )
            
            func_stack_offset = stack_offset
            # current_param_offset[tacky_ast.name]=-func_stack_offset
            # print(params)
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
        
        elif isinstance(tacky_ast,TackyFunCall):
            instructions=[]
            arg_regsiters = ['DI','SI','DX','CX','R8','R9']
            register_args = tacky_ast.args[:6]
            stack_args=tacky_ast.args[6:]
            # print('registerargs ',register_args)
            # print('stackargs',stack_args)
            # total_pushed_bytes = 8 * len(stack_args)
            # stack_padding = 0
            # if (total_pushed_bytes % 16) != 0:
            #     stack_padding = 8
            #     instructions.append(AllocateStack(stack_padding))
            # print(len(stack_args))
            stack_padding = 8 if len(stack_args) % 2 == 1 else 0
            # print('Stack padding',stack_padding)
            if stack_padding != 0:
                # print('Adding stack allocation')
                instructions.append(AllocateStack(stack_padding))

                
            reg_index=0
            for tacky_arg in register_args:
                r= arg_regsiters[reg_index]
                assembly_arg = self.convert_to_assembly_ast(tacky_arg)
                # print(self.symbols[tacky_arg.identifier])
                # exit(self.get_type(tacky_arg))
                instructions.append(Mov(assembly_type=self.get_type(tacky_arg),src=assembly_arg,dest=Reg(r)))
                reg_index +=1
                
            for tacky_arg in stack_args[::-1]:
                assembly_arg=self.convert_to_assembly_ast(tacky_arg)
                # print(assembly_arg)
                # exit()
                if isinstance(assembly_arg,Reg) or isinstance(assembly_arg,Imm) or self.get_type(tacky_arg)==AssemblyType.quadWord:
                    
                    ## TODO DIKKAT VERY MUCH
                    instructions.append(Push(assembly_arg,_type=AssemblyType.quadWord))
                else:
                    instructions.append(Mov(assembly_type=AssemblyType.longWord,src=assembly_arg,dest=Reg(Registers.AX)))
                    instructions.append(Push(Reg(Registers.AX),_type=AssemblyType.longWord))
                    
            instructions.append(Call(indentifier=tacky_ast.fun_name))
            
            bytes_to_remove = 8 * len(stack_args)+ stack_padding
            if bytes_to_remove !=0:
                # print('Bytes to remove',bytes_to_remove)
                instructions.append(DeallocateStack(value=bytes_to_remove))
                
            assembly_dst = self.convert_to_assembly_ast(tacky_ast.dst)
            # print(assembly_dst)
            print(tacky_ast.dst)
    
            instructions.append(Mov(assembly_type=self.get_type(tacky_ast.dst),src=Reg(Registers.AX),dest=assembly_dst))
            return instructions
        # Handle Return instruction
        elif isinstance(tacky_ast, TackyReturn):
            print(tacky_ast)
            if isinstance(tacky_ast.val , TackyVar):
                _type=self.get_param_type(self.symbols[tacky_ast.val.identifier]['ret'])
            else:
                _type=self.get_type(tacky_ast.val)
            # print(_type)
            # exit(0)
            # mov_instr = 
            src=self.convert_to_assembly_ast(tacky_ast.val)
            # print(src)
            # exit()
            return [
                Mov(assembly_type=_type,src=src, dest=Reg(Registers.AX)),
                Ret()
            ]
        
        # Handle Unary instruction
        elif isinstance(tacky_ast, TackyUnary):        
            # Convert a Unary operation by moving src to dst and applying the operator
            if tacky_ast.operator ==TackyUnaryOperator.NOT:
                # print('inside not')
                src=self.convert_to_assembly_ast(tacky_ast.src)
                dest=self.convert_to_assembly_ast(tacky_ast.dst)
                
                return [
                    Cmp(assembly_type=self.get_type(tacky_ast.src),operand1=Imm(0),operand2=src),
                    Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=dest),
                    SetCC(Cond_code=Cond_code.E,operand=self.convert_to_assembly_ast(tacky_ast.dst))
                ]
            else:
                src=self.convert_to_assembly_ast(tacky_ast.src)
                return [
                    Mov(assembly_type=self.get_type(tacky_ast.src),src=self.convert_to_assembly_ast(tacky_ast.src), dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                    Unary(operator=self.convert_operator(tacky_ast.operator,False),assembly_type=self.get_type(tacky_ast.src), operand=self.convert_to_assembly_ast(tacky_ast.dst))
                    
                ]
            
        # Check if the current AST node is a TackyBinary operation
        elif isinstance(tacky_ast, TackyBinary):
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
                # dest=self.convert_to_assembly_ast(tacky_ast.dst)
                # print(dest)
                # exit()
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
                # if tacky_ast.operator == TackyBinaryOperator.DIVIDE:
                    # print(self.symbols[tacky_ast.src1.identifier])
                    # print(isSigned(t))
                if isSigned(t):
                    # print('here')
                    # exit()
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
                else:
                    # exit()
                    # print('here')
                    # exit()
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
                # print(tacky_ast.src1)
                
                # print(self.symbols[tacky_ast.src1.identifier])
                # exit()
                
                # print(self.get_type(tacky_ast.src1))
                # print('src',)
                # print(tacky_ast.src2)
                # if isSigned(type(tacky_ast.src1)):
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
                # if tacky_ast.operator == TackyBinaryOperator.LESS_OR_EQUAL:
                    # print(self.symbols[tacky_ast.src1.identifier]['val_type'])
                    # print(isSigned(t))
                    
                    # exit()
             
                if isSigned(t)==True:
                # if tacky_ast.operator == TackyBinaryOperator.NOT_EQUAL:
                    # exit()
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src2),operand1=self.convert_to_assembly_ast(tacky_ast.src2),operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,True),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                else:
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src2),operand1=self.convert_to_assembly_ast(tacky_ast.src2),operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
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
                
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src1),operand1=self.convert_to_assembly_ast(tacky_ast.src2),operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
                            Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            SetCC(Cond_code=self.convert_operator(tacky_ast.operator,True),operand=self.convert_to_assembly_ast(tacky_ast.dst))
                            ]
                else:
                    return [Cmp(assembly_type=self.get_type(tacky_ast.src1),operand1=self.convert_to_assembly_ast(tacky_ast.src2),operand2=self.convert_to_assembly_ast(tacky_ast.src1)),
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
        # Handle Constant operand
        elif isinstance(tacky_ast, TackyConstant):
            if isinstance(tacky_ast.value,(ConstInt,ConstLong,ConstUInt,ConstULong)):
                return Imm(tacky_ast.value._int)
            return Imm(tacky_ast.value)
            # Convert a constant value into an Imm operand
        
        # elif isinstance(tacky_ast,AssemblyStaticVariable):
        # Handle Variable operand
        elif isinstance(tacky_ast, TackyVar):
            # Convert a variable into a Pseudo operand
            # print(tacky_ast)
            return Pseudo(tacky_ast.identifier)
        elif isinstance(tacky_ast,TackyJump):
            return [Jmp(indentifier=tacky_ast.target)]
        elif isinstance(tacky_ast,TackyJumpIfZero):
            return [
                Cmp(assembly_type=self.get_type(tacky_ast.condition),operand1=Imm(0),operand2=self.convert_to_assembly_ast(tacky_ast.condition)),
                JmpCC(Cond_code=Cond_code.E,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
            ]
        elif isinstance(tacky_ast,TackyJumpIfNotZero):
            return [
                Cmp(assembly_type=self.get_type(tacky_ast.condition),operand1=Imm(0),operand2=self.convert_to_assembly_ast(tacky_ast.condition)),
                JmpCC(Cond_code=Cond_code.NE,indentifier=self.convert_to_assembly_ast(tacky_ast.target))
            ]
            
        elif isinstance(tacky_ast,TackyCopy):
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
            print(tacky_ast)
            print(
                 Mov(assembly_type=AssemblyType.longWord,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            
            )
            # exit()
            return [
                Mov(assembly_type=AssemblyType.longWord,src=self.convert_to_assembly_ast(tacky_ast.src),dest=self.convert_to_assembly_ast(tacky_ast.dst))
            ]
        else:
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

