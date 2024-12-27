from assembly_ast import *

class CodeEmitter:
    def __init__(self, file_name, platform="linux"):
        self.file_name = file_name
        self.platform = platform
        self.output = []

    def emit_line(self, line=""):
        """Adds a line to the assembly output."""
        self.output.append(line)

    def emit_program(self,program):
        # print('Inside emit_program')
        # self.emit_function(program.function_definition)
        """Emit the program."""
        if not isinstance(program, AssemblyProgram):
            raise ValueError("The input program is not an instance of Program.")
        
        # Ensure function_definition is a valid FunctionAst instance
        if isinstance(program.function_definition, AssemblyFunction):
            self.emit_function(program.function_definition)
        else:
            raise ValueError(f"function_definition is not a valid FunctionAst: {type(program.function_definition)}")
        
        if self.platform == "linux":
            self.emit_line(".section .note.GNU-stack,\"\",@progbits")

    def emit_function(self, function):
        """Emit a function definition."""
        if not isinstance(function, AssemblyFunction):
            raise ValueError(f"Expected a FunctionAst, got {type(function)}")
        
        func_name = function.name.name

        if self.platform == "macos":
            func_name = f"_{func_name}"  # Add underscore prefix for macOS
        
        self.emit_line(f"   .globl {func_name}")
        self.emit_line(f"{func_name}:")
        self.emit_line(f'   pushq    %rbp')
        self.emit_line(f'   movq   %rsp,   %rbp')
        
        
        if not isinstance(function.instructions, list):
            raise ValueError(f"Expected instructions to be a list, got {type(function.instructions)}")
        
        for instruction in function.instructions:
            self.emit_instruction(instruction)

    def emit_instruction(self, instruction):
        print('Inside instruction')
        """Emit an assembly instruction."""
        if isinstance(instruction, Mov):
            src = convertOperandToAssembly(instruction.src)
            dest = convertOperandToAssembly(instruction.dest)
            self.emit_line(f"   movl {src}, {dest}")
        elif isinstance(instruction,Ret):
            self.emit_line('    movq   %rbp, %rsp')
            self.emit_line("    popq   %rbp")
            self.emit_line('    ret')
        elif isinstance(instruction,Unary):
            operator = convertOperatorToAssembly(instruction.operator)
            operand = convertOperandToAssembly(instruction.operand)
            self.emit_line(f'   {operator} {operand}')
        elif isinstance(instruction,AllocateStack):
            self.emit_line(f'   subq    ${instruction.value},%rsp')
        else:
            raise ValueError(f"Unsupported instruction type: {type(instruction)}")

    def format_operand(self, operand):
        print(operand)
        """Format the operand for assembly."""
        if isinstance(operand,Stack):
            return f'operand.value'
        return operand.value 
    
    def save(self):
        """Writes the emitted code to the file."""
        
        # Ensure self.file_name is a valid string or path-like object
        if not self.file_name:
            raise ValueError("File name is not provided or is invalid.")

        # Ensure self.output is a list and not None
        if not isinstance(self.output, list):
            raise TypeError("Output must be a list of strings.")
        
        # Debugging: print the output before writing to file
        print(self.output)

        try:
            # Write the output to the file
            with open(self.file_name, 'w') as f:
                string = "\n".join(self.output)
                f.write(string + "\n")  # Write the joined output with a newline at the end
        except Exception as e:
            # Catch any file-related errors
            print(f"Error writing to file: {e}")
            
            

def convertOperatorToAssembly(operator):
    if operator =='Neg':
        return 'negl'
    elif operator =='Not':
        return 'notl'
    else:
        raise ValueError('Invalid operator',operator)
    
    
def convertOperandToAssembly(operand):
    if isinstance(operand,Reg):
        return '%eax'
    elif operand==Registers.R10:
        return '%r10d'
    elif isinstance(operand,Stack):
        return f'{operand.value}(%rbp)'
    elif isinstance(operand,Imm):
        return f'${operand.value}'
    else:
        raise ValueError('Invalid operator',operand)
    