
import sys
from .assembly_ast import * 
from .instruction_fixer import is_signed_32_bit 
from src.frontend.parser._ast5 import String 
from src.backend.typechecker.type_classes import * 


tracker = 0
class CodeEmitter:
    def __init__(self, file_name, symbols, platform="linux"):
        self.file_name = file_name
        self.platform = platform
        self.symbols = symbols
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
            elif isinstance(func, AssemblyStaticVariable):
                print('self emit static var')
                self.emit_static_var(func)
            elif isinstance(func, AssemblyStaticConstant):
                print('self emit static const')
                
                self.emit_static_const(func)
            else:
                raise ValueError(
                    f"function_definition is not a valid FunctionAst: {type(program.function_definition)}"
                )

        if self.platform == "linux":
            self.emit_line('.section .note.GNU-stack,"",@progbits')

    def emit_static_var(self, instruction):
        print(instruction)
        try:
            if isinstance(instruction, AssemblyStaticVariable):
                # print('here')
                for init in instruction.init:
                    print(init)
                    print(instruction.name)
                    print(instruction.alignment)
                #   
                    # if not isinstance(init,StringInit) and init.value != 0:
                    #     print(init)
                    #     exit()
                    if (isinstance(init,StringInit) and init.string != 0 ) or init.value != '0' or isinstance(
                        init, DoubleInit):
                    # )  or init.value!=0 :
                        global tracker 
                        if tracker == 0:
                            if instruction._global == True:
                                self.emit_line(f"   .globl {instruction.name}")
                            self.emit_line("   .data")
                            self.emit_line(f"   .align {instruction.alignment}")
                            self.emit_line(f"{instruction.name}:")
                        tracker+=1
                        
                        self.emit_line(
                            f"   {convert_static_init(init,instruction.alignment)}"
                        )
                    else:
                     
                        print('emitting')
                        if tracker == 0:
                            if instruction._global == True:
                                self.emit_line(f"   .globl {instruction.name}")
                            self.emit_line("   .bss")
                            self.emit_line(f"   .align {instruction.alignment}")
                            self.emit_line(f"{instruction.name}:")
                        tracker+=1
                        self.emit_line(
                            f"   {convert_static_init(init,instruction.alignment)}"
                        )
                tracker = 0
        except Exception as e:
            raise SyntaxError("Error in static var", e)

    def emit_static_const(self, instruction):
        self.emit_line("   .section .rodata")
        self.emit_line(f"   .align {instruction.alignment}")
        self.emit_line(f"{instruction.name}:")
        self.emit_line(
            f"   {convert_static_init(instruction.init,instruction.alignment)}"
        )

    def emit_function(self, function):
        """Emit a function definition."""
        func_name = function.name
        if self.platform == "macos":
            func_name = f"_{func_name}"  # Add underscore prefix for macOS
        if function._global == True:
            self.emit_line(f"   .globl {func_name}")
        self.emit_line(f"   .text")
        self.emit_line(f"{func_name}:")
        self.emit_line(f"   pushq   %rbp")
        self.emit_line(f"   movq    %rsp, %rbp")
        # self.emit_line(f'   subq    $8{}, %rsp')  # Allocate space for local variables

        for instruction in function.instructions:
            self.emit_instruction(instruction)

    def emit_instruction(self, instruction):
        print('Emitting ',instruction)
        """Emit an assembly instruction."""
        if isinstance(instruction, Mov):
            if isinstance(instruction._type,ByteArray):
                instruction._type  = calculate_type(instruction._type)
        
            if instruction._type == AssemblyType.byte:
                # print(instruction)
                # exit()
                src = convertOperandToAssemblySETCC(instruction.src)
                dest = convertOperandToAssemblySETCC(instruction.dest)
                self.emit_line(f"   mov{convert_type(instruction._type)} {src}, {dest}")
            elif (
                instruction._type == AssemblyType.double
                and isinstance(instruction.dest, Reg)
                and instruction.dest.value == Registers.SP
                
            ):
                # exit()
                self.emit_line(
                    f"   movsd   {Convert8BYTEoperand(instruction.src)}  (%rsp)"
                )
                # self.emit_line(f"   mov{convert_type(instruction._type)} {src}, {dest}")
            elif isinstance(instruction.src, Memory):
                src = Convert8BYTEoperand(instruction.src)
                if isinstance(instruction._type ,ByteArray):
                    instruction._type = calculate_type(instruction._type)
                    
                if (
                    instruction._type == AssemblyType.double
                    or instruction._type == AssemblyType.quadWord
                ):
                    dest = Convert8BYTEoperand(instruction.dest)
                else:
                    dest = convertOperandToAssembly(instruction.dest)

                self.emit_line(
                    f"   mov{convert_type(instruction._type)}  {src} , {dest}"
                )
            elif isinstance(instruction.dest, Memory):
                dest = Convert8BYTEoperand(instruction.dest)
                if isinstance(instruction._type ,ByteArray):
                    instruction._type = calculate_type(instruction._type)
                    
                if (
                    instruction._type == AssemblyType.double
                    or instruction._type == AssemblyType.quadWord
                ):
                    src = Convert8BYTEoperand(instruction.src)
                else:
                    src = convertOperandToAssembly(instruction.src)

                self.emit_line(
                    f"   mov{convert_type(instruction._type)}  {src} , {dest}"
                )

            elif instruction._type == AssemblyType.longWord:
                src = convertOperandToAssembly(instruction.src)
                dest = convertOperandToAssembly(instruction.dest)
                self.emit_line(f"   mov{convert_type(instruction._type)} {src}, {dest}")
            else:
                # exit()
                # print(instruction)
                # exit()
                src = Convert8BYTEoperand(instruction.src)
                dest = Convert8BYTEoperand(instruction.dest)
                self.emit_line(f"   mov{convert_type(instruction._type)} {src}, {dest}")
            # #print('done')

        elif isinstance(instruction,Indexed):
            # exit()
            if instruction._type == AssemblyType.longWord:
                operand1 = convertOperandToAssembly(instruction.base)
                operand2= convertOperandToAssembly(instruction.index)
            else:
                operand1 = Convert8BYTEoperand(instruction.base)
                operand2= Convert8BYTEoperand(instruction.index)
               
            
            self.emit_line(f'({operand1,    operand2,   instruction.scale})')
            
        elif isinstance(instruction, Ret):
            self.emit_line("   movq   %rbp, %rsp")
            self.emit_line("   popq   %rbp")
            self.emit_line("   ret")
        elif isinstance(instruction, Movsx):
        
            if isinstance(instruction.assembly_type_src,ByteArray):
               src_type = calculate_type(instruction.assembly_type_src) 
               src_type = convert_type(src_type)
        
            else:
                src_type = convert_type(instruction.assembly_type_src)
            dst_type = convert_type(instruction.assembly_type_dst)

            src = convertOperandToAssembly(instruction.src)
            dest = Convert8BYTEoperand(instruction.dest)
            
            if src_type=='b':
                src = convertOperandToAssemblySETCC(instruction.src)
            elif src_type == 'l':
                src = convertOperandToAssembly(instruction.src)
            elif src_type == 'q':
              
                src = Convert8BYTEoperand(instruction.src)
                
            if dst_type=='b' or dst_type == AssemblyType.byte:
                dest = convertOperandToAssemblySETCC(instruction.dest)
            elif dst_type == 'l' or dst_type == AssemblyType.longWord:
                dest = convertOperandToAssembly(instruction.dest)
                
            elif dst_type == 'q'or dst_type == AssemblyType.quadWord:
                dest = Convert8BYTEoperand(instruction.dest)
               
            self.emit_line(f"   movs{src_type}{dst_type} {src}, {dest}")

        elif isinstance(instruction, Unary):
            if instruction._type == AssemblyType.longWord:
                operand = convertOperandToAssembly(instruction.operand)
            else:
                operand = Convert8BYTEoperand(instruction.operand)
            if instruction.operator in (UnaryOperator.SHR):
                self.emit_line(f"   {UnaryOperator.SHR}  {operand}")
            else:
                operator = convertOperatorToAssembly(instruction.operator)
                self.emit_line(
                    f"   {operator}{convert_type(instruction._type)} {operand}"
                )

        elif isinstance(instruction, Binary):

            if instruction._type == AssemblyType.longWord:
                src = convertOperandToAssembly(instruction.src1)
                dest = convertOperandToAssembly(instruction.src2)
            elif instruction._type == AssemblyType.byte:
                src = convertOperandToAssemblySETCC(instruction.src1)
                dest = convertOperandToAssemblySETCC(instruction.src2)
            else:
                src = Convert8BYTEoperand(instruction.src1)
                dest = Convert8BYTEoperand(instruction.src2)
            # print(instruction.operator)
            # print(BinaryOperator.SUBTRACT)
            # exit()
            if (
                instruction._type == AssemblyType.double
                and instruction.operator == BinaryOperator.XOR
            ):
                self.emit_line(f"   xorpd {src},   {dest}")

            elif (
                instruction._type == AssemblyType.double
                and instruction.operator == BinaryOperator.MULTIPLY
            ):

                self.emit_line(f"   mulsd   {src},   {dest}")

            elif instruction.operator in (
                BinaryOperator.AND,
                BinaryOperator.OR,
                UnaryOperator.SHR,
                BinaryOperator.XOR,
            ):
                operator = convertOperatorToAssembly(instruction.operator)
                self.emit_line(f"   {operator} {src}, {dest}")
            else:
                operator = convertOperatorToAssembly(instruction.operator)
                self.emit_line(
                    f"   {operator}{convert_type(instruction._type)} {src}, {dest}"
                )

        elif isinstance(instruction, Cmp):
            print(instruction._type)
            # exit()
            if isinstance(instruction._type ,ByteArray):
                    instruction._type = calculate_type(instruction._type)
            if instruction._type == AssemblyType.longWord:
                op1 = convertOperandToAssembly(instruction.operand1)
                op2 = convertOperandToAssembly(instruction.operand2)
            elif instruction._type==AssemblyType.byte:
                op1=convertOperandToAssemblySETCC(instruction.operand1)
                op2=convertOperandToAssemblySETCC(instruction.operand2)
            else:
                op1 = Convert8BYTEoperand(instruction.operand1)
                op2 = Convert8BYTEoperand(instruction.operand2)
            if instruction._type == AssemblyType.double:
                self.emit_line(f"   comisd    {op1}, {op2}")
            else:
              
                self.emit_line(f"   cmp{convert_type(instruction._type)} {op1}, {op2}")

        elif isinstance(instruction, Jmp):
            label = convertOperandToAssembly(instruction.identifier)
            self.emit_line(f"   jmp  .L{label}")

        elif isinstance(instruction, JmpCC):
            label = convertOperandToAssembly(instruction.identifier)
            code = convert_code_to_assembly(instruction.cond_code)
            self.emit_line(f"   j{code}    .L{label}")
        elif isinstance(instruction, SetCC):
            code = convert_code_to_assembly(instruction.cond_code)
            label = convertOperandToAssemblySETCC(instruction.operand)
            # #print('label',label)
            # #print(label)
            self.emit_line(f"   set{code}    {label}")

        elif isinstance(instruction, Lea):
            src = convertOperandToAssembly(instruction.src)
            dst = Convert8BYTEoperand(instruction.dst)
      
            # z+=1
            if isinstance(instruction.src,Indexed):
                # arr = 
                src = Convert8BYTEoperand(instruction.src)
            # print(s)
                self.emit_line(f"   leaq ({src[0]},{src[1]},{src[2]}),  {dst}")
            else:
                print('here')
                self.emit_line(f' leaq {src},{dst}')
        elif isinstance(instruction, Cvtsi2sd):
            # print(instruction._type)
           
            # operator = convertOperatorToAssembly(instruction.)
            if instruction._type == AssemblyType.longWord:
                src = convertOperandToAssembly(instruction.src)
                # dest = convertOperandToAssembly(instruction.dst)
                dest = Convert8BYTEoperand(instruction.dst)
                
            elif instruction._type == AssemblyType.byte:
             
                src = convertOperandToAssemblySETCC(instruction.src)
                dest = Convert8BYTEoperand(instruction.dst)
              
            else:
                src = Convert8BYTEoperand(instruction.src)
                dest = Convert8BYTEoperand(instruction.dst)

            self.emit_line(
                f"   cvtsi2sd{convert_type(instruction._type)}   {src} ,  {dest}"
            )

        elif isinstance(instruction, Cvttsd2si):
            # operator = convertOperatorToAssembly(instruction.)
            if instruction._type == AssemblyType.longWord:
                src = convertOperandToAssembly(instruction.src)
                dest = convertOperandToAssembly(instruction.dst)
            elif instruction._type == AssemblyType.byte:
             
                src = convertOperandToAssemblySETCC(instruction.src)
                dest = convertOperandToAssemblySETCC(instruction.dst)
            else:
                src = Convert8BYTEoperand(instruction.src)
                dest = Convert8BYTEoperand(instruction.dst)

            self.emit_line(
                f"   cvttsd2si{convert_type(instruction._type)}   {src},   {dest}"
            )

        elif isinstance(instruction, Label):
            label = convertOperandToAssembly(instruction.identifier)
            self.emit_line(f".L{label}:")
        elif isinstance(instruction, DeallocateStack):
            self.emit_line(f"   addq    ${instruction.value}, %rsp")
        elif isinstance(instruction, Push):
            operand = Convert8BYTEoperand(instruction.operand)
            print(instruction)
            # exit()
            self.emit_line(f"   pushq {operand}")
        elif isinstance(instruction, Call):
            defined = self.symbols[instruction.identifier]["attrs"].defined
            if defined:
                self.emit_line(f"   call {instruction.identifier}")
            else:
                self.emit_line(f"   call {instruction.identifier}@PLT")

        elif isinstance(instruction, Idiv):
            # #print(instruction)
            if instruction._type == AssemblyType.longWord:
                op = convertOperandToAssembly(instruction.operand)
            else:
                op = Convert8BYTEoperand(instruction.operand)
            self.emit_line(
                f"   idiv{convert_type(instruction._type)} {op}"
            )  # Perform division

        elif isinstance(instruction, Div):
            # #print(instruction)
            if instruction._type == AssemblyType.longWord:
                op = convertOperandToAssembly(instruction.operand)
            else:
                op = Convert8BYTEoperand(instruction.operand)
            # print(op)
            # exit()
            # print('idiv',instruction)
            # exit()
            # self.emit_line(f'   movl {op}, %eax')  # Move operand to %eax
            # self.emit_line('   cdq')  # Sign-extend into %edx:%eax
            self.emit_line(
                f"   div{convert_type(instruction._type)} {op}"
            )  # Perform division
            # self.emit_line(f'   movl %eax, {convertOperandToAssembly(instruction.dst)}')  # Store quotient
        elif isinstance(instruction, Cdq):
            if instruction._type == AssemblyType.longWord:
                self.emit_line("   cdq")  # Sign-extend into %edx:%eax
            elif instruction._type == AssemblyType.quadWord:
                self.emit_line("   cqo")  # Sign-extend into %edx:%eax

        elif isinstance(instruction, AllocateStack):
            # #print()
            self.emit_line(
                f"   subq    ${instruction.value}, %rsp"
            )  # Allocate stack space
        elif isinstance(instruction,MovZeroExtend):
            src_type = convert_type(instruction.assembly_type_src)
            dst_type = convert_type(instruction.assembly_type_dst)
            src = Convert8BYTEoperand(instruction.src)
            dst = Convert8BYTEoperand(instruction.dest)
            
            
            if isinstance(instruction.assembly_type_src,ByteArray):
               src_type = calculate_type(instruction.assembly_type_src) 
               src_type = convert_type(src_type)
        
            else:
                src_type = convert_type(instruction.assembly_type_src)
            dst_type = convert_type(instruction.assembly_type_dst)

            src = convertOperandToAssembly(instruction.src)
            dest = Convert8BYTEoperand(instruction.dest)
            
            if src_type=='b':
                src = convertOperandToAssemblySETCC(instruction.src)
            elif src_type == 'l':
                src = convertOperandToAssembly(instruction.src)
            elif src_type == 'q':
              
                src = Convert8BYTEoperand(instruction.src)
                
            if dst_type=='b' or dst_type == AssemblyType.byte:
                dest = convertOperandToAssemblySETCC(instruction.dest)
            elif dst_type == 'l' or dst_type == AssemblyType.longWord:
                dest = convertOperandToAssembly(instruction.dest)
                
            elif dst_type == 'q'or dst_type == AssemblyType.quadWord:
                dest = Convert8BYTEoperand(instruction.dest)
               
            # self.emit_line(f"   movs{src_type}{dst_type} {src}, {dest}")
            self.emit_line(f'movz{src_type}{dst_type}   {src},{dest}')
            
            
            
            
        else:
            print(isinstance(instruction, Push))
            raise ValueError(f"Unsupported instruction type: {type(instruction)}")

    def save(self):
        """Writes the emitted code to the file."""
        with open(self.file_name, "w") as f:
            f.write("\n".join(self.output) + "\n")


def convertOperatorToAssembly(operator: str) -> str:
    if operator == "Neg":
        return "neg"  # 32-bit negation
    elif operator == "Not":
        return "not"  # 32-bit bitwise NOT
    elif operator == "Add":
        return "add"
    elif operator == "Sub":
        return "sub"
    elif operator == "Mult":
        return "imul"
    elif operator == "Shr":
        return "shr"
    elif operator == "DivDouble":
        return "div"
    elif operator == "And":
        return "and"
    elif operator == "Or":
        return "or"
    elif operator == "Shr":
        return "shr"
    elif operator == "DivDouble":
        return "div"
    elif operator == "And":
        return "and"
    elif operator == "Or":
        return "or"
    else:
        raise ValueError(f"Invalid operator: {operator}")


def convertOperandToAssembly(operand: Operand) -> str:
    # DEFAULT 4 BYTE
    # #print(operand)
    if isinstance(operand, Reg):
        # Map to 32-bit registers based on the register type
        operand = operand.value
        # #print(operand)
        if operand == Registers.AX:
            return "%eax"
        elif operand == Registers.DX:
            return "%edx"
        elif operand == Registers.CX:
            return "%ecx"
        elif operand == Registers.DI:
            return "%edi"
        elif operand == Registers.SI:
            return "%esi"
        elif operand == Registers.R8:
            return "%r8d"
        elif operand == Registers.R9:
            return "%r9d"
        elif operand == Registers.R10:
            return "%r10d"
        elif operand == Registers.R11:
            return "%r11d"
        elif operand == Registers.SP:
            return "%rsp"
        elif operand == Registers.BP:
            return "%rbp"
        elif isinstance(operand, Memory):
            return f"{operand._int}({Convert8BYTEoperand(operand.reg)})"
        else:
            raise ValueError(f"Unsupported register : {operand}")
    elif isinstance(operand, Memory):
        return f"{operand._int}({Convert8BYTEoperand(operand.reg)})"
    elif isinstance(operand,Indexed):
        # print('Inside indexed')
        # print(type(operand.base))
        operand1 = convertOperandToAssembly(operand.base)
        operand2 = convertOperandToAssembly(operand.index)
        return operand1,    operand2,   operand.scale
        
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # #print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f"${operand.value}"
    elif isinstance(operand, Data):
        return f"{operand.identifier}(%rip)"
    elif isinstance(operand, str):
        if operand.startswith('string'):
            return f'{operand}(%rip)'
       
        return operand
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")


def convertOperandToAssemblySETCC(operand: Operand) -> str:
    
    # #print(operand.value)
    if isinstance(operand, Reg):
        operand = operand.value
        if operand == Registers.AX:
            return "%al"
        elif operand == Registers.DX:
            return "%dl"
        elif operand == Registers.CX:
            return "%cl"
        elif operand == Registers.DI:
            return "%dil"
        elif operand == Registers.SI:
            return "%sil"
        elif operand == Registers.R8:
            return "%r8b"
        elif operand == Registers.R9:
            return "%r9b"
        elif operand == Registers.R10:
            return "%r10b"
        elif operand == Registers.R11:
            return "%r11b"
        elif operand == Registers.SP:
            return "%rsp"
        elif operand == Registers.BP:
            return "%rbp"
        elif operand == Registers.XMM0:
            return "%xmm0"
        else:
            raise ValueError(f"Unsupported register: {operand.reg}")
    elif isinstance(operand, Memory):
        return f"{operand._int}({Convert8BYTEoperand(operand.reg)})"
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # #print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f"${operand.value}"
    elif isinstance(operand, Data):
        return f"{operand.identifier}(%rip)"
    else:
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")

def Convert8BYTEoperand(operand) -> str:
    # global i 
    # if i==2:
    #     print(operand)
    #     exit()
    # i+=1
    # #print(operand.value)
    if isinstance(operand, Reg):
        # print(operand)
        operand = operand.value
        if operand == Registers.AX:
            return "%rax"
        elif operand == Registers.DX:
            return "%rdx"
        elif operand == Registers.CX:
            return "%rcx"
        elif operand == Registers.DI:
            return "%rdi"
        elif operand == Registers.SI:
            return "%rsi"
        elif operand == Registers.R8:
            return "%r8"
        elif operand == Registers.R9:
            return "%r9"
        elif operand == Registers.R10:
            return "%r10"
        elif operand == Registers.R11:
            return "%r11"
        elif operand == Registers.SP:
            return "%rsp"
        elif operand == Registers.XMM0:
            return "%xmm0"
        elif operand == Registers.XMM1:
            return "%xmm1"
        elif operand == Registers.XMM2:
            return "%xmm2"
        elif operand == Registers.XMM3:
            return "%xmm3"
        elif operand == Registers.XMM4:
            return "%xmm4"
        elif operand == Registers.XMM5:
            return "%xmm5"
        elif operand == Registers.XMM6:
            return "%xmm6"
        elif operand == Registers.XMM7:
            return "%xmm7"
        elif operand == Registers.XMM14:
            return "%xmm14"
        elif operand == Registers.XMM15:
            return "%xmm15"
        elif operand == Registers.BP:
            return "%rbp"
        elif isinstance(operand, Memory):
            return f"{operand._int}(%{Convert8BYTEoperand(operand.reg)})"
        else:
            raise ValueError(f"Unsupported register: {operand}")
    elif isinstance(operand, Memory):
        return f"{operand._int}({Convert8BYTEoperand(operand.reg)})"
    elif isinstance(operand,Indexed):
        operand1 = Convert8BYTEoperand(operand.base)
        operand2 = Convert8BYTEoperand(operand.index)
        return [operand1,    operand2,   operand.scale]
    elif isinstance(operand, Stack):
        # Stack operands with 4-byte alignment
        # #print(operand.value)
        return f"{operand.value}(%rbp)"
    elif isinstance(operand, Imm):
        # Immediate values
        return f"${operand.value}"
    elif isinstance(operand, Data):
        return f"{operand.identifier}(%rip)"
    elif isinstance(operand, str):
        print(operand)
        # exit()
        return operand
    else:
        print(operand)
        raise ValueError(f"Invalid operand type: {type(operand).__name__}")


def convert_code_to_assembly(code: str):
    return code.lower()


def convert_static_init(instr, alignment):
 
    if isinstance(instr, DoubleInit):
        if instr.value == float("inf"):
            return ".double Inf"
        # exit()
        val = f".double {instr.value}"
        
        return val
    elif isinstance(instr,CharInit):
        # print(instr.value)
        # exit()
        if instr.value == 0:
            return '.zero 1'
        else:
            return f'.byte {instr.value}'
    elif isinstance(instr,UCharInit):
        print(instr.value)
        # exit()
        if instr.value == 0:
            return '.zero 1'
        else:
            return f'.byte {instr.value}'
    elif isinstance(instr,(StringInit,String)):
        import codecs
        st=escape_for_gas(instr.string)
        st = codecs.decode(st, 'unicode_escape')
        print(st)
        # exit()
        


        if instr.string == 'NULL':
            instr.string= ''
            return '.asciz'
        if instr.null_terminated == False:
            return f'.asciz "{instr.string.replace("\\", "\\\\").replace("\"", "\\\"")}"'
        else:
                # if instr.string
            return  f'.asciz "{st}"'
                
    elif isinstance(instr,PointerInit):
        return f'.quad {instr.name}'
    elif isinstance(instr,ZeroInit):
        return f' .zero {instr.value}'
    elif isinstance(instr, UIntInit):
        if instr.value == 0:
            return f".zero 4"
        else:
            return f".long {instr.value}"
    elif isinstance(instr, ULongInit):
        if instr.value == 0:
            return f".zero 8"
        else:
            return f".quad {instr.value}"
    elif isinstance(instr, IntInit):
        if instr.value == 0:
            return f".zero 4"
        else:
            return f".long {instr.value}"
    elif isinstance(instr, LongInit):
        # exit()
        if instr.value == 0:
            return f".zero 8"
        else:
            return f".quad {instr.value}"
    else:
        ValueError("Invalid value", instr)



import re

def escape_for_gas(s):
    # Only match actual control characters, then backslash at the end
    return re.sub(
        r'["\n\r\t\0]|\\',
        lambda m: {
            '"': r'\"',
            '\n': r'\n',
            '\r': r'\r',
            '\t': r'\t',
            '\0': r'\0',
            '\\': r'\\',
        }[m.group(0)],
        s
    )

def convert_type(_type):
    if _type == AssemblyType.longWord  :
        return "l"
    elif _type == AssemblyType.quadWord :
        return "q"
    elif _type == AssemblyType.double :
        return "sd"
    elif _type == AssemblyType.byte:
        return 'b'
    else:
        raise ValueError("Invalid operand type", _type)


def get_push_suffix(value):
    if is_signed_32_bit(value):
        return "q"
    else:
        return "l"

def calculate_type(_type):
    if isinstance(_type,ByteArray):
        size =  _type.alignment
        if size== 4:
            return AssemblyType.longWord
        else :
            return AssemblyType.quadWord
      