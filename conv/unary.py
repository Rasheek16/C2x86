from tacky import *
from assembly_ast import *
from tacky_emiter import *

def convert_unary(self,tacky_ast:TackyUnary)-> list[Instruction]:
    
     #* Converison of unary NOT
            if tacky_ast.operator ==TackyUnaryOperator.NOT:
                
                src=self.convert_to_assembly_ast(tacky_ast.src)
                dest=self.convert_to_assembly_ast(tacky_ast.dst)
                
                
                #* Converion of double by taking XOR with Register
                if self.get_type(tacky_ast.src) == AssemblyType.double:
                    return [
                        #* Take XOR
                        Binary(operator=BinaryOperator.XOR,assembly_type=AssemblyType.double,src1=Reg(Registers.XMM0),src2=Reg(Registers.XMM0)),
                        
                        #* Compare instruction
                        Cmp(assembly_type=AssemblyType.double,operand1=self.convert_to_assembly_ast(tacky_ast.dst),operand2=Reg(Registers.XMM0)),
                        
                        #* Move Instruction
                        Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=dest),
                        
                        #* Set Code = Equal
                        SetCC(Cond_code=Cond_code.E,operand=self.convert_to_assembly_ast(tacky_ast.dst))
                        ]
                
              
             
                #* Converion of types other than Double   
                return [
                    #* Compare
                    Cmp(assembly_type=self.get_type(tacky_ast.src),operand1=Imm(0),operand2=src),
                    
                    #* Move
                    Mov(assembly_type=self.get_type(tacky_ast.dst),src=Imm(0),dest=dest),
                    
                    #* Set Code
                    SetCC(Cond_code=Cond_code.E,operand=self.convert_to_assembly_ast(tacky_ast.dst))
                ]
            else:
                #* Negation for double
                if tacky_ast.operator == TackyUnaryOperator.NEGATE  and self.get_type(tacky_ast.src)==AssemblyType.double:
                    
                    #* Create temporary label
                        const_label = get_const_label()
                        
                        #* Set value
                        value = tacky_ast.src.value._int
                        
                        #* set boolean flag found
                        found =False
                        
                        #* Check for existing static const with same alignment and value in table
                        for i in self.temp:
                            if self.temp[i]['alignment'] == 8 and (float(self.temp[i]['value']) - float(tacky_ast.src.value._int==0)):
                                const_label = self.symbols[i].identifier
                                value = self.temp.value
                                found=True 
                            else:
                                continue 
                        
                        #* Check condition based oh flag , if not found , insert a static character in symbol table and temp table
                        if not found:
                            self.symbols[const_label]=TopLevel.static_const(
                                identifier=const_label,
                                alignment=8,
                                init=value,
                            )
                            self.temp[const_label] = {
                                'identifier':const_label,
                                'alignment':8,
                                'value':value,
                                
                            }
            
                        #* Return rest of the binary and move condition for negation 
                        return[ 
                               #* Move instruction 
                            Mov(assembly_type=AssemblyType.double,src=self.convert_symbol_table(src),dest=self.convert_to_assembly_ast(tacky_ast.dst)),
                            
                            #* Binary instruction
                            Binary(assembly_type=AssemblyType.double,operator=BinaryOperator.XOR,src1=Data(const_label),src2=Pseudo(tacky_ast.dst)),
                            
                            
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
    
    