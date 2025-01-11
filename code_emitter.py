from assembly_ast import *
import sys

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
        # print(program)
        """Emit the program."""
        if not isinstance(program, AssemblyProgram):
            raise ValueError("The input program is not an instance of Program.")
        for func in program.function_definition:
            if isinstance(func, AssemblyFunction):
                self.emit_function(func)
            elif isinstance(func,AssemblyStaticVariable):
                    # print()
                    self.emit_static_var(func)
            else:
                raise ValueError(f"function_definition is not a valid FunctionAst: {type(program.function_definition)}")
        
        if self.platform == "linux":
            self.emit_line(".section .note.GNU-stack,\"\",@progbits")

    def emit_static_var(self,instruction):
        try:
            # if isinstance()
            long_op = instruction.init.value
            # if isinstance(long_op,Constant):
                
            if instruction.init.value != 0 :
                if instruction._global==True:
                    self.emit_line(f'   .globl {instruction.name}')
                self.emit_line('   .data')
                self.emit_line('   .align 4')
                self.emit_line(f'{instruction.name}:')
                self.emit_line(f'   .long {long_op}')
            else:
                if instruction._global==True:
                    self.emit_line(f'   .globl {instruction.name}')
                self.emit_line('   .bss')
                self.emit_line('   .align 4')
                self.emit_line(f'{instruction.name}:')
                self.emit_line(f'   .zero 4')
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
            src = convertOperandToAssembly(instruction.src)
            # print(src)
            dest = convertOperandToAssembly(instruction.dest)
            self.emit_line(f"   movl {src}, {dest}")
        
        elif isinstance(instruction, Ret):
            self.emit_line('   movq   %rbp, %rsp')
            self.emit_line("   popq   %rbp")
            self.emit_line('   ret')
        
        elif isinstance(instruction, Unary):
            operator = convertOperatorToAssembly(instruction.operator)
            operand = convertOperandToAssembly(instruction.operand)
            self.emit_line(f'   {operator} {operand}')
        
        elif isinstance(instruction, Binary):
            operator = convertOperatorToAssembly(instruction.operator)
            src = convertOperandToAssembly(instruction.src1)
            dest = convertOperandToAssembly(instruction.src2)
            self.emit_line(f'    {operator} {src}, {dest}')

        elif isinstance(instruction,Cmp):
            op1 = convertOperandToAssembly(instruction.operand1)
            op2 = convertOperandToAssembly(instruction.operand2)
        
            self.emit_line(f'   cmpl {op1}, {op2}')
        
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
            # print('label',label)
            # print(label)
            self.emit_line(f'   set{code}    {label}')
        
        
        
        elif isinstance(instruction,Label):
            label = convertOperandToAssembly(instruction.identifier)
            self.emit_line(f'.L{label}:')
        elif isinstance(instruction,DeallocateStack) :
            self.emit_line(f'   addq    ${instruction.value}, %rsp')
        elif isinstance(instruction,Push):
            operand= Convert8BYTEoperand(instruction.operand)
            self.emit_line(f'   pushq {operand}')
        elif isinstance(instruction,Call):
            defined = self.symbols[instruction.identifier]['attrs'].defined
            if defined:
                self.emit_line(f'   call {instruction.identifier}')
            else:
                self.emit_line(f'   call {instruction.identifier}@PLT')
         
        elif isinstance(instruction, Idiv):
            # print(instruction)
            op = convertOperandToAssembly(instruction.operand)
            # self.emit_line(f'   movl {op}, %eax')  # Move operand to %eax
            # self.emit_line('   cdq')  # Sign-extend into %edx:%eax
            self.emit_line(f'   idivl {op}')  # Perform division
            # self.emit_line(f'   movl %eax, {convertOperandToAssembly(instruction.dst)}')  # Store quotient
        elif isinstance(instruction,Cdq):
            self.emit_line('   cdq')  # Sign-extend into %edx:%eax
           
        elif isinstance(instruction, AllocateStack):
            # print()
            self.emit_line(f'   subq    ${instruction.value}, %rsp')  # Allocate stack space
        
        else:
            raise ValueError(f"Unsupported instruction type: {type(instruction)}")

    def save(self):
        """Writes the emitted code to the file."""
        with open(self.file_name, 'w') as f:
            f.write("\n".join(self.output) + "\n")

def convertOperatorToAssembly(operator: str) -> str:
    if operator == 'Neg':
        return 'negl'     # 32-bit negation
    elif operator == 'Not':
        return 'notl'     # 32-bit bitwise NOT
    elif operator == 'Add':
        return 'addl'
    elif operator == 'Sub':
        return 'subl'
    elif operator == 'Mult':
        return 'imull'
    else:
        raise ValueError(f'Invalid operator: {operator}')

def convertOperandToAssembly(operand: Operand) -> str:
    # DEFAULT 4 BYTE 
    # print(operand)
    if isinstance(operand,str):
        return operand
    elif isinstance(operand, Reg):
        # Map to 32-bit registers based on the register type
        operand = operand.value
        # print(operand)
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
            
        else:
            raise ValueError(f"Unsupported register : {operand}")
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f'${operand.value}'
    elif isinstance(operand,Data):
        return f'{operand.identifier}(%rip)'
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")
    
def convertOperandToAssemblySETCC(operand: Operand) -> str:
    # print(operand.value)
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
            
        else:
            raise ValueError(f"Unsupported register: {operand.reg}")
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f'${operand.value}'
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")

    
    
def Convert8BYTEoperand(operand) -> str:
    # print(operand.value)
    if isinstance(operand, Reg):
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
        else:
            raise ValueError(f"Unsupported register: {operand}")
    else:
        return f'${operand.value}'
def convert_code_to_assembly(code:str):
    return code.lower()