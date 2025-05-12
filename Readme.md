
# ⚙️ PCC — x86-64 C Compiler in Python

PCC is a fully-featured C compiler for the **x86-64 architecture**, written entirely in Python. 
Designed for clarity and modularity, it implements the complete C compilation pipeline — from 
source to assembly — without relying on parser generators like Yacc/Lex.

📘 Inspired by *Writing a C Compiler* by Nora Sandler, this project extends it significantly by 
implementing robust semantic analysis, IR generation, optimizations, struct and pointer support, 
and full code generation.

---

## 🚀 What’s Inside

| Stage               | Description                                                        |
|---------------------|--------------------------------------------------------------------|
| `Lexing`            | Custom handwritten lexer with token stream generation              |
| `Parsing`           | Recursive-descent parser producing a complete AST                  |
| `Semantic Analysis` | Type checking, scope resolution, storage class, and promotions     |
| `IR Generation`     | Strongly-typed TACKY intermediate representation                   |
| `Optimization`      | Constant folding, cast simplification, and dead store elimination  |
| `Codegen`           | Converts IR into real x86-64 assembly conforming to SysV ABI       |
| `Register Handling` | Stack allocation + pseudo register resolution                      |
| `Assembly Emission` | GCC-compatible `.s` and `.o` files for final linking               |

---

## ✅ Supported C Features

- Primitive types: `int`, `char`, `unsigned`, `long`,`double` ,`signed` ,`ulong`
- Composite types: `struct`, `array`, `pointer`
- Type system: size/alignment handling, integer promotions, cast expressions
- Memory: stack variables, string literals, global/static storage
- Control flow: `if`, `else`, `for`, `while`,`do while`, `ternary`, `return`
- Expression evaluation: arithmetic, pointer math, logical ops
- Calling conventions: stack frame setup, argument passing (SysV ABI)
- Integration with `gcc` for preprocessing, assembling, and linking

---

## 🗂️ Project Structure

```
.
├── pcc.py             # Entry point — choose stage and compile
├── src/
│   ├── frontend/      # Lexer, parser, type checker, AST
│   └── backend/       # IR emission, optimizer, codegen
├── examples/          # Sample C test cases
```

---
## 💻 Usage
```bash
 pcc [stage] <input_file> [output_file] [libraries...]
```

### Compilation Stages

| Flag         | Purpose                            |
|--------------|------------------------------------|
| `--lex`      | Token stream only                  |
| `--parse`    | Parse and display AST              |
| `--validate` | Run semantic analysis and scoping  |
| `--tacky`    | Emit TACKY IR                      |
| `--codegen`  | Generate Assembly AST              |
| `-S`         | Emit `.s` file only (no link)      |
| `-c`         | Emit object file `.o`              |
| `run`        | Full compilation + linking         |
| `--help`     | View command options               |

---

## ✨ Example Commands

```bash
 pcc --lex examples/hello.c
 pcc --parse examples/loop.c
 pcc --tacky examples/math.c
 pcc run examples/structs.c
```

---

## 🧪 Sample Output

```asm
.globl main
.text
main:
  pushq %rbp
  movq %rsp, %rbp
  ...
  ret
```

## 🛡️ License & Credits

This project is an educational and non-commercial compiler implementation.

### 🔐 Intellectual Property & References

- This project draws foundational inspiration from **Nora Sandler’s** excellent guide:  
  📘 *Writing a C Compiler* — [https://github.com/nlsandler/nqcc2](https://github.com/nlsandler/nqcc2)  
  The original work is © Nora Sandler. All structural credits go to her for the roadmap and pedagogical flow.

- The **System V x86-64 ABI** documentation is referenced for architecture compliance.

- While many concepts are informed by existing compiler design materials, all parsing, semantic logic, intermediate representations, and code generation in this repository were implemented manually, without external compiler toolchains.


---
## 🔗 Repository

Source Code → [github.com/rasheek16/pcc](https://www.github.com/rasheek16/pcc)

---

## 👨‍💻 Author

Created by **Rasheek** — a systems programmer passionate about learning from the ground up. This compiler was written with a focus on low-level correctness, language design, and educational clarity.

---

## 📌 Final Note

This project was built to explore how C programs are translated into machine code — through lexing, parsing, semantic analysis, IR generation, and final assembly. Every stage is handcrafted to provide insight into how real-world compilers operate.

---
