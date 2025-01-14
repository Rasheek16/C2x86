from assembly_ast import *
import sys
from type_classes import *
from instruction_fixer import is_signed_32_bit
class CodeEmitter:
    def __init__(self, file_name, symbols,platform="linux"):
        self.file_name = file_name
        self.platform = platform
        self.symbols=symbols
        self.output = []

    def emit_line(self, line=""):
        """Adds a line to the assembly output."""
        self.output.append(line)

    def emit_program(self, program):
        # #print(program)
        """Emit the program."""
        if not isinstance(program, AssemblyProgram):
            raise ValueError("The input program is not an instance of Program.")
        for func in program.function_definition:
            if isinstance(func, AssemblyFunction):
                self.emit_function(func)
            elif isinstance(func,AssemblyStaticVariable):
                    # #print()
                self.emit_static_var(func)
            else:
                raise ValueError(f"function_definition is not a valid FunctionAst: {type(program.function_definition)}")
        
        if self.platform == "linux":
            self.emit_line(".section .note.GNU-stack,\"\",@progbits")

    def emit_static_var(self,instruction):
        try:
            if isinstance(instruction,AssemblyStaticVariable):
                # if isinstance()
                print(instruction.init)
                # exit()
                if instruction.init.value != 0 :
                    print('here')
                    if instruction._global==True:
                        self.emit_line(f'   .globl {instruction.name}')
                    self.emit_line('   .data')
                    self.emit_line(f'   .align {instruction.alignment}')
                    self.emit_line(f'{instruction.name}:')
                    self.emit_line(f'   {convert_static_init(instruction.init,instruction.alignment)}')
                else:
                    if instruction._global==True:
                        self.emit_line(f'   .globl {instruction.name}')
                    self.emit_line('   .bss')
                    self.emit_line(f'   .align {instruction.alignment}')
                    self.emit_line(f'{instruction.name}:')
                    # self.emit_line(f'   .zero 4')
                    self.emit_line(f'   {convert_static_init(instruction.init,instruction.alignment)}')
        except Exception as e:
            raise SyntaxError('Error in static var',e)
      
      
        
    def emit_function(self, function):
        
        """Emit a function definition."""
        func_name = function.name
        if self.platform == "macos":
            func_name = f"_{func_name}"  # Add underscore prefix for macOS
        if function._global==True:
            self.emit_line(f"   .globl {func_name}")
        self.emit_line(f'   .text')
        self.emit_line(f"{func_name}:")
        self.emit_line(f'   pushq   %rbp')
        self.emit_line(f'   movq    %rsp, %rbp')
        # self.emit_line(f'   subq    $8{}, %rsp')  # Allocate space for local variables
        
        
        for instruction in function.instructions:
            self.emit_instruction(instruction)

    def emit_instruction(self, instruction):
        """Emit an assembly instruction."""
        if isinstance(instruction, Mov):
            print(instruction._type)
            if instruction._type==AssemblyType.longWord:
                src = convertOperandToAssembly(instruction.src)
                dest = convertOperandToAssembly(instruction.dest)
            else:
                src = Convert8BYTEoperand(instruction.src)
                dest = Convert8BYTEoperand(instruction.dest)
            # print(src)
           
            self.emit_line(f"   mov{convert_type(instruction._type)} {src}, {dest}")
            # #print('done')
        
        elif isinstance(instruction, Ret):
            self.emit_line('   movq   %rbp, %rsp')
            self.emit_line("   popq   %rbp")
            self.emit_line('   ret')
        elif isinstance(instruction,Movsx):
            src = convertOperandToAssembly(instruction.src)
            # #print(src)
            dest = Convert8BYTEoperand(instruction.dest)
            self.emit_line(f"   movslq {src}, {dest}")
            
            
        elif isinstance(instruction, Unary):
            if instruction._type==AssemblyType.longWord:

                operand = convertOperandToAssembly(instruction.operand)
            else:
                operand = Convert8BYTEoperand(instruction.operand)
            operator = convertOperatorToAssembly(instruction.operator)
            self.emit_line(f'   {operator}{convert_type(instruction._type)} {operand}')
        
        elif isinstance(instruction, Binary):
            operator = convertOperatorToAssembly(instruction.operator)
            if instruction._type==AssemblyType.longWord:
                src = convertOperandToAssembly(instruction.src1)
                dest = convertOperandToAssembly(instruction.src2)
            else:
                src = Convert8BYTEoperand(instruction.src1)
                dest = Convert8BYTEoperand(instruction.src2)
            # src = convertOperandToAssembly(instruction.src1)
            # dest = convertOperandToAssembly(instruction.src2)
            self.emit_line(f'   {operator}{convert_type(instruction._type)} {src}, {dest}')

        elif isinstance(instruction,Cmp):
            # #print(instruction._type)
            if instruction._type==AssemblyType.longWord:
                op1 = convertOperandToAssembly(instruction.operand1)
                op2 = convertOperandToAssembly(instruction.operand2)
            else:
                op1 = Convert8BYTEoperand(instruction.operand1)
                op2 = Convert8BYTEoperand(instruction.operand2)
          
            self.emit_line(f'   cmp{convert_type(instruction._type)} {op1}, {op2}')
        
        elif isinstance(instruction,Jmp):
            label = convertOperandToAssembly(instruction.identifier)
            self.emit_line(f'   jmp  .L{label}')
        
        elif isinstance(instruction,JmpCC):
            label = convertOperandToAssembly(instruction.identifier)
            code =convert_code_to_assembly(instruction.cond_code)
            self.emit_line(f'   j{code}    .L{label}')
        elif isinstance(instruction,SetCC):
            code =convert_code_to_assembly(instruction.cond_code)
            label = convertOperandToAssemblySETCC(instruction.operand)
            # #print('label',label)
            # #print(label)
            self.emit_line(f'   set{code}    {label}')
        
        
        
        elif isinstance(instruction,Label):
            label = convertOperandToAssembly(instruction.identifier)
            self.emit_line(f'.L{label}:')
        elif isinstance(instruction,DeallocateStack) :
            self.emit_line(f'   addq    ${instruction.value}, %rsp')
        elif isinstance(instruction,Push):
            operand= Convert8BYTEoperand(instruction.operand)
            print(instruction)
            # exit()
            self.emit_line(f'   pushq {operand}')
        elif isinstance(instruction,Call):
            defined = self.symbols[instruction.identifier]['attrs'].defined
            if defined:
                self.emit_line(f'   call {instruction.identifier}')
            else:
                self.emit_line(f'   call {instruction.identifier}@PLT')
         
        elif isinstance(instruction, Idiv):
            # #print(instruction)
            if instruction._type==AssemblyType.longWord:
                op = convertOperandToAssembly(instruction.operand)
            else:
                op = Convert8BYTEoperand(instruction.operand)
            # print('idiv',instruction)
            # exit()
            # self.emit_line(f'   movl {op}, %eax')  # Move operand to %eax
            # self.emit_line('   cdq')  # Sign-extend into %edx:%eax
            self.emit_line(f'   idiv{convert_type(instruction._type)} {op}')  # Perform division
            # self.emit_line(f'   movl %eax, {convertOperandToAssembly(instruction.dst)}')  # Store quotient
        elif isinstance(instruction,Cdq):
            if instruction._type==AssemblyType.longWord:
                self.emit_line('   cdq')  # Sign-extend into %edx:%eax
            elif instruction._type==AssemblyType.quadWord:
                self.emit_line('   cqo')  # Sign-extend into %edx:%eax
                
           
        elif isinstance(instruction, AllocateStack):
            # #print()
            self.emit_line(f'   subq    ${instruction.value}, %rsp')  # Allocate stack space
        
        else:
            print(isinstance(instruction,Push))
            raise ValueError(f"Unsupported instruction type: {type(instruction)}")

    def save(self):
        """Writes the emitted code to the file."""
        with open(self.file_name, 'w') as f:
            f.write("\n".join(self.output) + "\n")

def convertOperatorToAssembly(operator: str) -> str:
    if operator == 'Neg':
        return 'neg'     # 32-bit negation
    elif operator == 'Not':
        return 'not'     # 32-bit bitwise NOT
    elif operator == 'Add':
        return 'add'
    elif operator == 'Sub':
        return 'sub'
    elif operator == 'Mult':
        return 'imul'
    else:
        raise ValueError(f'Invalid operator: {operator}')

def convertOperandToAssembly(operand: Operand) -> str:
    # DEFAULT 4 BYTE 
    # #print(operand)
    if isinstance(operand,str):
        return operand
    elif isinstance(operand, Reg):
        # Map to 32-bit registers based on the register type
        operand = operand.value
        # #print(operand)
        if operand == Registers.AX:
            return '%eax'
        elif operand == Registers.DX:
            return '%edx'
        elif operand == Registers.CX:
            return '%ecx'
        elif operand == Registers.DI:
            return '%edi'
        elif operand == Registers.SI:
            return '%esi'
        elif operand == Registers.R8:
            return '%r8d'
        elif operand == Registers.R9:
            return '%r9d'
        elif operand == Registers.R10:
            return '%r10d'
        elif operand == Registers.R11:
            return '%r11d'
        elif operand == Registers.SP:
            return '%rsp'
        else:
            raise ValueError(f"Unsupported register : {operand}")
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # #print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f'${operand.value}'
    elif isinstance(operand,Data):
        return f'{operand.identifier}(%rip)'
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")
    
def convertOperandToAssemblySETCC(operand: Operand) -> str:
    # #print(operand.value)
    if isinstance(operand, Reg):
        operand = operand.value
        if operand == Registers.AX:
            return '%al'
        elif operand == Registers.DX:
            return '%dl'
        elif operand == Registers.CX:
            return '%cl'
        elif operand == Registers.DI:
            return '%dil'
        elif operand == Registers.SI:
            return '%sil'
        elif operand == Registers.R8:
            return '%r8b'
        elif operand == Registers.R9:
            return '%r9b'
        elif operand == Registers.R10:
            return '%r10b'
            
        elif operand == Registers.R11:
            return '%r11b'
        elif operand == Registers.SP:
            return '%rsp'
            
        else:
            raise ValueError(f"Unsupported register: {operand.reg}")
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # #print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f'${operand.value}'
    elif isinstance(operand,Data):
        return f'{operand.identifier}(%rip)'
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")

    
    
def Convert8BYTEoperand(operand) -> str:
    # print(operand)
    # exit()
    # #print(operand.value)
    if isinstance(operand, Reg):
        #print(operand)
        operand = operand.value
        if operand == Registers.AX:
            return '%rax'
        elif operand == Registers.DX:
            return '%rdx'
        elif operand == Registers.CX:
            return '%rcx'
        elif operand == Registers.DI:
            return '%rdi'
        elif operand == Registers.SI:
            return '%rsi'
        elif operand == Registers.R8:
            return '%r8'
        elif operand == Registers.R9:
            return '%r9'
        elif operand == Registers.R10:
            return '%r10'
            
        elif operand == Registers.R11:
            return '%r11'
        elif operand == Registers.SP:
            return '%rsp'
        else:
            raise ValueError(f"Unsupported register: {operand}")
    elif isinstance(operand,str):
        print(operand)
        # exit()
        return operand
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # #print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f'${operand.value}'
    elif isinstance(operand,Data):
        return f'{operand.identifier}(%rip)'
    else:
        print(operand)
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")
def convert_code_to_assembly(code:str):
    return code.lower()

def convert_static_init(instr,alignment):
    print(instr.value)
    # exit()
    if isinstance(instr,IntInit):
        if instr.value==0:
            return f'.zero 4'
        else:
            return f'.long {instr.value}'
    elif isinstance(instr,LongInit):
        if instr.value==0:
            return f'.zero 8'
        else:
            return f'.quad {instr.value}'
    elif alignment==4:
        if instr.value.value==0:
            return f'.zero 4'
        else:
            return f'.long {instr.value}'
    elif alignment==8:
        if instr.value.value==0:
            return f'.zero 8'
        else:
            return f'.quad {instr.value}'
    else:
        ValueError('Invalid value',instr)
    
    # elif isinstance(instr,)

def convert_type(_type):
    if _type == AssemblyType.longWord:
        return 'l'
    elif _type ==AssemblyType.quadWord:
        return 'q'
    else:
        raise ValueError('Invalid mov type')




def get_push_suffix(value):
    if is_signed_32_bit(value):
        return 'q'
    else:
        return 'l'

