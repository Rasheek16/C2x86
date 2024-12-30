from assembly_ast import *
import sys

class CodeEmitter:
    def __init__(self, file_name, platform="linux"):
        self.file_name = file_name
        self.platform = platform
        self.output = []

    def emit_line(self, line=""):
        """Adds a line to the assembly output."""
        self.output.append(line)

    def emit_program(self, program):
        print(program)
        """Emit the program."""
        if not isinstance(program, AssemblyProgram):
            raise ValueError("The input program is not an instance of Program.")
        
        if isinstance(program.function_definition, AssemblyFunction):
            self.emit_function(program.function_definition)
        else:
            raise ValueError(f"function_definition is not a valid FunctionAst: {type(program.function_definition)}")
        
        if self.platform == "linux":
            self.emit_line(".section .note.GNU-stack,\"\",@progbits")

    def emit_function(self, function):
        """Emit a function definition."""
        func_name = function.name
        if self.platform == "macos":
            func_name = f"_{func_name}"  # Add underscore prefix for macOS
        
        self.emit_line(f"   .globl {func_name}")
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
            self.emit_line('    movq   %rbp, %rsp')
            self.emit_line("    popq   %rbp")
            self.emit_line('    ret')
        
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
            self.emit_line(f'   j{instruction.cond_code}    .L{label}')
        elif isinstance(instruction,SetCC):
            
            label = convertOperandToAssemblySETCC(instruction.operand)
            # print(label)
            self.emit_line(f'   set{instruction.cond_code}    {label}')
        
        elif isinstance(instruction,Label):
            label = convertOperandToAssembly(instruction.identifier)
            self.emit_line(f'.L{label}:')
        
        

        elif isinstance(instruction, Idiv):
            print(instruction)
            op = convertOperandToAssembly(instruction.operand)
            # self.emit_line(f'   movl {op}, %eax')  # Move operand to %eax
            # self.emit_line('   cdq')  # Sign-extend into %edx:%eax
            self.emit_line(f'   idivl {op}')  # Perform division
            # self.emit_line(f'   movl %eax, {convertOperandToAssembly(instruction.dst)}')  # Store quotient
        elif isinstance(instruction,Cdq):
            self.emit_line('   cdq')  # Sign-extend into %edx:%eax
           
        elif isinstance(instruction, AllocateStack):
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
    # print(operand)
    if isinstance(operand,str):
        return operand
    elif isinstance(operand, Reg):
        # Map to 32-bit registers based on the register type
        operand = operand.value
        print(operand)
        if operand == Registers.AX:
            return '%eax'
            

        elif operand == Registers.DX:
            return '%edx'
            
        elif operand == Registers.R10:
            return '%r10d'
            
        elif operand == Registers.R11:
            return '%r11d'
            
        else:
            raise ValueError(f"Unsupported register: {operand.reg}")
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f'${operand.value}'
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")
    
def convertOperandToAssemblySETCC(operand: Operand) -> str:
    print(operand.value)
    if isinstance(operand, Reg):
        operand = operand.value
        if operand == Registers.AX:
            return '%al'
        elif operand == Registers.DX:
            return '%dl'
            
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

    
def convert_code_to_assembly(code:str):
    return code.lower()