```markdown 
# ⚙️ PCC — The Ultimate x86-64 C Compiler in Python

> “They said building a C compiler is hard. I said: hold my stack frame.”

Welcome to **PCC** — a fully-featured C compiler targeting the **x86-64 architecture**, written entirely in Python. From tokens to typed IR, all the way to raw, optimized assembly — this beast speaks fluent C. No toy project. No shortcuts. Just pure systems sorcery.

📚 Inspired by *Nora Sandler’s Writing a C Compiler*, then taken 10 levels further with full semantic analysis, struct support, pointer arithmetic, memory allocation, optimizations, and custom code emission.

---

## 🚀 What It Does

**This isn’t just a parser. This is a pipeline.**

| Stage                  | Capability                                                        |
|------------------------|-------------------------------------------------------------------|
| `Lexing`               | Tokenizes raw C using a handcrafted lexer                         |
| `Parsing`              | Constructs a full AST with recursive descent techniques           |
| `Semantic Analysis`    | Type checking, scoping, storage class resolution, promotions      |
| `IR Generation`        | Emits a typed, strongly-structured TACKY IR                       |
| `Optimization`         | Includes constant folding, dead store elimination, cast reduction |
| `Assembly Emission`    | Converts IR into real, platform-compliant x86-64                  |
| `Pseudoreg Allocation` | Allocates stack space & resolves abstract registers               |
| `Final Codegen`        | Emits and links GCC-ready `.s` / `.o` / executables               |

---

## 🧠 Supported Features

- 🔒 **All major C types**: `int`, `char`, `unsigned`, `long`, `float`, `double`, structs, arrays, pointers
- 📐 **Correct type system** with integer promotion and size/align semantics
- 🧠 **Symbol table**: full variable scope resolution, extern/static/auto class handling
- 💡 **Static + dynamic memory** support (e.g., string literals, stack vars, heap pointers)
- 🧰 **TACKY IR**: A custom intermediate representation designed for register-agnostic optimization
- 💣 **Real Codegen**: Final `.s` files are optimized, comment-rich, and conform to `System V ABI`
- 🎯 **Fully integrated** with `GCC` for preprocessing, assembling, and linking
- 🧼 **Temporary file cleanup** on success
- 🔍 **Modular frontend/backend split** for easy hacking and compiler passes

---

## 🗂️ Project Structure

```
.
├── pcc.py          # 🚀 Entry point — run any compilation stage
├── src/
│   ├── frontend/        # Lexer, parser, type checker, resolver
│   └── backend/         # IR generator, optimizer, assembly emitter
├── test/            # ✅ C test cases for every supported feature
```

---

## 💻 How to Run

```bash
python pcc.py [stage] <input_file> [<output_file>] [<libraries>]
```

### ✅ Compilation Stages

| Flag         | Description                        |
|--------------|------------------------------------|
| `--lex`      | Print tokens                       |
| `--parse`    | Parse and print AST                |
| `--validate` | Semantic check & symbol resolution |
| `--tacky`    | Emit intermediate TACKY IR         |
| `--codegen`  | Generate assembly AST              |
| `-S`         | Emit `.s` (assembly) and stop      |
| `-c`         | Emit `.o` (object file)            |
| `run`        | Full compile → link → executable   |
| `--help`     | Show command usage                 |

### 🔥 Examples

```bash
python compiler.py --lex examples/hello.c
python compiler.py --parse examples/hello.c
python compiler.py --tacky examples/math.c
python compiler.py --codegen examples/nested.c
python compiler.py -S examples/main.c main.s
python compiler.py run examples/main.c
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

Yes. That's real assembly code. You wrote C. You got x86-64. No middleman.

---

Absolutely! Here's a clean, professional, and respectful **"References & Credits"** section you can drop into your `README.md`:

---

## 📚 References & Credits

This compiler was built as a hands-on learning project inspired by the incredible book:

> 📘 **Writing a C Compiler** by Nora Sandler  
> GitHub: [https://github.com/nsandler/writing-a-c-compiler](https://github.com/nsandler/writing-a-c-compiler)

### Special Thanks
- Nora Sandler, for the step-by-step breakdown of real-world compiler internals.
- The **System V x86-64 ABI** documentation for helping structure calling conventions and stack discipline.
- The **open-source community**, whose blog posts, GitHub discussions, and compiler designs served as inspiration.
- All compiler devs who turned “segfaults” into “structure.”

> This project is educational, personal, and written with a deep passion for low-level systems.  
> All intellectual credit belongs to original authors and references where applicable.

---

## 🔗 GitHub

Source Code: [github.com/rasheek16/pcc](https://www.github.com/rasheek16/pcc)

---

## 👑 Who Built This?

Made with love, rage, and no void keywords.  
By [@rasheek16](https://github.com/rasheek16) — systems nerd, Python whisperer, and a systems programmer obsessed with how things *really* work.  
This project was an attempt to not just read a compiler book... but to *live* it.  
From parsing and typechecking to register allocation and codegen, this was built with intention, curiosity, and plenty of debug printouts.

---

## 💬 Final Words

> “This isn't just a compiler. It's a flex.”

---

```

