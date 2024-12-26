from _Ast import Program,Return,Constant, Function
from assembly_ast import Mov , Ret, Imm, Register ,AssemblyFunction , AssemblyProgram
import sys 
def convert_to_assembly_ast(parser_ast) -> AssemblyProgram:
    if isinstance(parser_ast, Program):
        return AssemblyProgram(
            function_definition=convert_to_assembly_ast(parser_ast.function_definition)
        )
    elif isinstance(parser_ast, Function):
        instructions = convert_to_assembly_ast(parser_ast.body)
        return AssemblyFunction(
            name=parser_ast.name,
            instructions=instructions
        )
    elif isinstance(parser_ast, Return):
        return [
            Mov(src=convert_to_assembly_ast(parser_ast.exp), dest=Register().name),
            Ret()
        ]
    elif isinstance(parser_ast, Constant):
        return Imm(parser_ast.value)
    else:
        sys.exit(1) 
        raise ValueError(f"Unsupported AST node: {type(parser_ast)}")
