	.file	"test.c"
	.text
	.globl	patterns
	.section	.rodata
.LC0:
	.string	"static"
.LC1:
	.string	"\\bstatic\\b"
.LC2:
	.string	"extern"
.LC3:
	.string	"\\bextern\\b"
.LC4:
	.string	"long_keyword"
.LC5:
	.string	"\\blong\\b"
.LC6:
	.string	"signed_keyword"
.LC7:
	.string	"\\bsigned\\b"
.LC8:
	.string	"unsigned_keyword"
.LC9:
	.string	"\\bunsigned\\b"
.LC10:
	.string	"struct_keyword"
.LC11:
	.string	"\\bstruct\\b"
.LC12:
	.string	"arrow"
.LC13:
	.string	"->"
.LC14:
	.string	"sizeof_keyword"
.LC15:
	.string	"\\bsizeof\\b"
.LC16:
	.string	"char"
.LC17:
	.string	"\\bchar\\b"
.LC18:
	.string	"string"
.LC19:
	.string	"\\bstring\\b"
.LC20:
	.string	"char_constant"
	.align 8
.LC21:
	.string	"'(\\\\[\\\\'\"?abfnrtv0]|\\\\x[0-9a-fA-F]{2}|\\\\[0-7]{1,3}|\\\\u[0-9a-fA-F]{4}|\\\\U[0-9a-fA-F]{8}|[^'\\\\\\n])'"
.LC22:
	.string	"string_constant"
	.align 8
.LC23:
	.string	"\"([^\"\\\\\\n]|\\\\[\"'\\\\?abfnrtv]|\\\\[0-7]{1,3}|\\\\x[0-9a-fA-F]+)*\""
.LC24:
	.string	"floating_point_constant"
	.align 8
.LC25:
	.string	"(([0-9]*\\.[0-9]+|[0-9]+\\.?)[Ee][+-]?[0-9]+|[0-9]*\\.[0-9]+|[0-9]+\\.)[^\\w.]"
.LC26:
	.string	"double_keyword"
.LC27:
	.string	"\\bdouble\\b"
.LC28:
	.string	"Constant"
.LC29:
	.string	"([0-9]+)[^\\w.]"
.LC30:
	.string	"int_keyword"
.LC31:
	.string	"\\bint\\b"
.LC32:
	.string	"void_keyword"
.LC33:
	.string	"\\bvoid\\b"
.LC34:
	.string	"return_keyword"
.LC35:
	.string	"\\breturn\\b"
.LC36:
	.string	"Open_bracket"
.LC37:
	.string	"\\["
.LC38:
	.string	"Close_bracket"
.LC39:
	.string	"\\]"
.LC40:
	.string	"Open_parenthesis"
.LC41:
	.string	"\\("
.LC42:
	.string	"Close_parenthesis"
.LC43:
	.string	"\\)"
.LC44:
	.string	"open_brace"
.LC45:
	.string	"\\{"
.LC46:
	.string	"close_brace"
.LC47:
	.string	"\\}"
.LC48:
	.string	"Semicolon"
.LC49:
	.string	";"
.LC50:
	.string	"Complement"
.LC51:
	.string	"~"
.LC52:
	.string	"Decrement"
.LC53:
	.string	"--"
.LC54:
	.string	"Negation"
.LC55:
	.string	"-"
.LC56:
	.string	"Multiplication"
.LC57:
	.string	"\\*"
.LC58:
	.string	"Addition"
.LC59:
	.string	"\\+"
.LC60:
	.string	"Division"
.LC61:
	.string	"/"
.LC62:
	.string	"Remainder"
.LC63:
	.string	"%"
.LC64:
	.string	"And"
.LC65:
	.string	"\\&\\&"
.LC66:
	.string	"LessOrEqual"
.LC67:
	.string	"<="
.LC68:
	.string	"GreaterOrEqual"
.LC69:
	.string	">="
.LC70:
	.string	"Or"
.LC71:
	.string	"\\|\\|"
.LC72:
	.string	"Equal"
.LC73:
	.string	"=="
.LC74:
	.string	"NotEqual"
.LC75:
	.string	"!="
.LC76:
	.string	"Not"
.LC77:
	.string	"!"
.LC78:
	.string	"LessThan"
.LC79:
	.string	"<"
.LC80:
	.string	"GreaterThan"
.LC81:
	.string	">"
.LC82:
	.string	"if_keyword"
.LC83:
	.string	"\\bif\\b"
.LC84:
	.string	"else_keyword"
.LC85:
	.string	"\\belse\\b"
.LC86:
	.string	"question_mark"
.LC87:
	.string	"\\?"
.LC88:
	.string	"colon"
.LC89:
	.string	":"
.LC90:
	.string	"Assignment"
.LC91:
	.string	"="
.LC92:
	.string	"do"
.LC93:
	.string	"\\bdo\\b"
.LC94:
	.string	"while"
.LC95:
	.string	"\\bwhile\\b"
.LC96:
	.string	"for"
.LC97:
	.string	"\\bfor\\b"
.LC98:
	.string	"break"
.LC99:
	.string	"\\bbreak\\b"
.LC100:
	.string	"continue"
.LC101:
	.string	"\\bcontinue\\b"
.LC102:
	.string	"comma"
.LC103:
	.string	","
.LC104:
	.string	"unsigned_int_constant"
.LC105:
	.string	"([0-9]+[uU])[^\\w.]"
.LC106:
	.string	"long_int_constant"
.LC107:
	.string	"([0-9]+[lL])[^\\w.]"
.LC108:
	.string	"signed_long_constant"
	.align 8
.LC109:
	.string	"([0-9]+([lL][uU]|[uU][lL]))[^\\w.]"
.LC110:
	.string	"Identifier"
.LC111:
	.string	"[a-zA-Z_]\\w*\\b"
.LC112:
	.string	"Ampersand"
.LC113:
	.string	"&"
	.section	.data.rel.local,"aw"
	.align 32
	.type	patterns, @object
	.size	patterns, 912
patterns:
	.quad	.LC0
	.quad	.LC1
	.quad	.LC2
	.quad	.LC3
	.quad	.LC4
	.quad	.LC5
	.quad	.LC6
	.quad	.LC7
	.quad	.LC8
	.quad	.LC9
	.quad	.LC10
	.quad	.LC11
	.quad	.LC12
	.quad	.LC13
	.quad	.LC14
	.quad	.LC15
	.quad	.LC16
	.quad	.LC17
	.quad	.LC18
	.quad	.LC19
	.quad	.LC20
	.quad	.LC21
	.quad	.LC22
	.quad	.LC23
	.quad	.LC24
	.quad	.LC25
	.quad	.LC26
	.quad	.LC27
	.quad	.LC28
	.quad	.LC29
	.quad	.LC30
	.quad	.LC31
	.quad	.LC32
	.quad	.LC33
	.quad	.LC34
	.quad	.LC35
	.quad	.LC36
	.quad	.LC37
	.quad	.LC38
	.quad	.LC39
	.quad	.LC40
	.quad	.LC41
	.quad	.LC42
	.quad	.LC43
	.quad	.LC44
	.quad	.LC45
	.quad	.LC46
	.quad	.LC47
	.quad	.LC48
	.quad	.LC49
	.quad	.LC50
	.quad	.LC51
	.quad	.LC52
	.quad	.LC53
	.quad	.LC54
	.quad	.LC55
	.quad	.LC56
	.quad	.LC57
	.quad	.LC58
	.quad	.LC59
	.quad	.LC60
	.quad	.LC61
	.quad	.LC62
	.quad	.LC63
	.quad	.LC64
	.quad	.LC65
	.quad	.LC66
	.quad	.LC67
	.quad	.LC68
	.quad	.LC69
	.quad	.LC70
	.quad	.LC71
	.quad	.LC72
	.quad	.LC73
	.quad	.LC74
	.quad	.LC75
	.quad	.LC76
	.quad	.LC77
	.quad	.LC78
	.quad	.LC79
	.quad	.LC80
	.quad	.LC81
	.quad	.LC82
	.quad	.LC83
	.quad	.LC84
	.quad	.LC85
	.quad	.LC86
	.quad	.LC87
	.quad	.LC88
	.quad	.LC89
	.quad	.LC90
	.quad	.LC91
	.quad	.LC92
	.quad	.LC93
	.quad	.LC94
	.quad	.LC95
	.quad	.LC96
	.quad	.LC97
	.quad	.LC98
	.quad	.LC99
	.quad	.LC100
	.quad	.LC101
	.quad	.LC102
	.quad	.LC103
	.quad	.LC104
	.quad	.LC105
	.quad	.LC106
	.quad	.LC107
	.quad	.LC108
	.quad	.LC109
	.quad	.LC110
	.quad	.LC111
	.quad	.LC112
	.quad	.LC113
	.globl	patterns_count
	.section	.rodata
	.align 4
	.type	patterns_count, @object
	.size	patterns_count, 4
patterns_count:
	.long	57
	.text
	.type	lstrip, @function
lstrip:
.LFB6:
	.cfi_startproc
	endbr64
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$16, %rsp
	movq	%rdi, -8(%rbp)
	jmp	.L2
.L4:
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	leaq	1(%rax), %rdx
	movq	-8(%rbp), %rax
	movq	%rdx, (%rax)
.L2:
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movzbl	(%rax), %eax
	testb	%al, %al
	je	.L5
	call	__ctype_b_loc@PLT
	movq	(%rax), %rdx
	movq	-8(%rbp), %rax
	movq	(%rax), %rax
	movzbl	(%rax), %eax
	movzbl	%al, %eax
	addq	%rax, %rax
	addq	%rdx, %rax
	movzwl	(%rax), %eax
	movzwl	%ax, %eax
	andl	$8192, %eax
	testl	%eax, %eax
	jne	.L4
.L5:
	nop
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE6:
	.size	lstrip, .-lstrip
	.section	.rodata
.LC114:
	.string	"strdup"
.LC115:
	.string	"Failed to compile regex: %s\n"
.LC116:
	.string	"strndup"
.LC117:
	.string	"Invalid identifier: '%s'\n"
	.align 8
.LC118:
	.string	"Invalid character '%c' after constant '%s'\n"
.LC119:
	.string	"Unexpected input: %s\n"
	.text
	.globl	lex
	.type	lex, @function
lex:
.LFB7:
	.cfi_startproc
	endbr64
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$272, %rsp
	movq	%rdi, -264(%rbp)
	movq	%rsi, -272(%rbp)
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	xorl	%eax, %eax
	leaq	.LC28(%rip), %rax
	movq	%rax, -96(%rbp)
	leaq	.LC104(%rip), %rax
	movq	%rax, -88(%rbp)
	leaq	.LC106(%rip), %rax
	movq	%rax, -80(%rbp)
	leaq	.LC108(%rip), %rax
	movq	%rax, -72(%rbp)
	leaq	.LC24(%rip), %rax
	movq	%rax, -64(%rbp)
	movl	$5, -232(%rbp)
	movabsq	$9041865928820203579, %rax
	movabsq	$4484526558868548907, %rdx
	movq	%rax, -48(%rbp)
	movq	%rdx, -40(%rbp)
	movabsq	$7295613884138530337, %rax
	movabsq	$6583512153913110085, %rdx
	movq	%rax, -32(%rbp)
	movq	%rdx, -24(%rbp)
	movl	$32, -228(%rbp)
	movq	-264(%rbp), %rax
	movq	%rax, %rdi
	call	strdup@PLT
	movq	%rax, -192(%rbp)
	cmpq	$0, -192(%rbp)
	jne	.L7
	leaq	.LC114(%rip), %rax
	movq	%rax, %rdi
	call	perror@PLT
	movl	$1, %edi
	call	exit@PLT
.L7:
	movq	-192(%rbp), %rax
	movq	%rax, -224(%rbp)
	movq	$0, -216(%rbp)
	movq	$0, -208(%rbp)
	jmp	.L8
.L36:
	leaq	-224(%rbp), %rax
	movq	%rax, %rdi
	call	lstrip
	movq	-224(%rbp), %rax
	movzbl	(%rax), %eax
	testb	%al, %al
	je	.L39
	movb	$0, -255(%rbp)
	movl	$0, -252(%rbp)
	jmp	.L11
.L33:
	movl	-252(%rbp), %eax
	cltq
	salq	$4, %rax
	movq	%rax, %rdx
	leaq	8+patterns(%rip), %rax
	movq	(%rdx,%rax), %rcx
	leaq	-176(%rbp), %rax
	movl	$1, %edx
	movq	%rcx, %rsi
	movq	%rax, %rdi
	call	regcomp@PLT
	testl	%eax, %eax
	je	.L12
	movl	-252(%rbp), %eax
	cltq
	salq	$4, %rax
	movq	%rax, %rdx
	leaq	8+patterns(%rip), %rax
	movq	(%rdx,%rax), %rdx
	movq	stderr(%rip), %rax
	leaq	.LC115(%rip), %rcx
	movq	%rcx, %rsi
	movq	%rax, %rdi
	movl	$0, %eax
	call	fprintf@PLT
	movq	-192(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movl	$0, %eax
	jmp	.L37
.L12:
	movq	-224(%rbp), %rsi
	leaq	-104(%rbp), %rdx
	leaq	-176(%rbp), %rax
	movl	$0, %r8d
	movq	%rdx, %rcx
	movl	$1, %edx
	movq	%rax, %rdi
	call	regexec@PLT
	testl	%eax, %eax
	jne	.L14
	movl	-104(%rbp), %eax
	testl	%eax, %eax
	jne	.L14
	movl	-100(%rbp), %eax
	movl	%eax, -248(%rbp)
	movl	-248(%rbp), %eax
	movslq	%eax, %rdx
	movq	-224(%rbp), %rax
	movq	%rdx, %rsi
	movq	%rax, %rdi
	call	strndup@PLT
	movq	%rax, -184(%rbp)
	cmpq	$0, -184(%rbp)
	jne	.L15
	leaq	.LC116(%rip), %rax
	movq	%rax, %rdi
	call	perror@PLT
	movl	$1, %edi
	call	exit@PLT
.L15:
	movl	-252(%rbp), %eax
	cltq
	salq	$4, %rax
	movq	%rax, %rdx
	leaq	patterns(%rip), %rax
	movq	(%rdx,%rax), %rax
	leaq	.LC110(%rip), %rdx
	movq	%rdx, %rsi
	movq	%rax, %rdi
	call	strcmp@PLT
	testl	%eax, %eax
	jne	.L16
	call	__ctype_b_loc@PLT
	movq	(%rax), %rdx
	movq	-184(%rbp), %rax
	movzbl	(%rax), %eax
	movzbl	%al, %eax
	addq	%rax, %rax
	addq	%rdx, %rax
	movzwl	(%rax), %eax
	movzwl	%ax, %eax
	andl	$2048, %eax
	testl	%eax, %eax
	je	.L16
	movq	stderr(%rip), %rax
	movq	-184(%rbp), %rdx
	leaq	.LC117(%rip), %rcx
	movq	%rcx, %rsi
	movq	%rax, %rdi
	movl	$0, %eax
	call	fprintf@PLT
	movq	-184(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movq	-192(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movl	$0, %eax
	jmp	.L37
.L16:
	movl	$0, -244(%rbp)
	jmp	.L17
.L29:
	movl	-244(%rbp), %eax
	cltq
	movq	-96(%rbp,%rax,8), %rdx
	movl	-252(%rbp), %eax
	cltq
	salq	$4, %rax
	movq	%rax, %rcx
	leaq	patterns(%rip), %rax
	movq	(%rcx,%rax), %rax
	movq	%rdx, %rsi
	movq	%rax, %rdi
	call	strcmp@PLT
	testl	%eax, %eax
	jne	.L18
	movl	$0, -240(%rbp)
	jmp	.L19
.L27:
	movl	-240(%rbp), %eax
	movslq	%eax, %rdx
	movq	-184(%rbp), %rax
	addq	%rdx, %rax
	movzbl	(%rax), %eax
	movb	%al, -253(%rbp)
	call	__ctype_b_loc@PLT
	movq	(%rax), %rax
	movzbl	-253(%rbp), %edx
	movzbl	%dl, %edx
	addq	%rdx, %rdx
	addq	%rdx, %rax
	movzwl	(%rax), %eax
	movzwl	%ax, %eax
	andl	$2048, %eax
	testl	%eax, %eax
	jne	.L20
	movb	$0, -254(%rbp)
	movl	$0, -236(%rbp)
	jmp	.L21
.L24:
	movl	-236(%rbp), %eax
	cltq
	movzbl	-48(%rbp,%rax), %eax
	cmpb	%al, -253(%rbp)
	jne	.L22
	movb	$1, -254(%rbp)
	jmp	.L23
.L22:
	addl	$1, -236(%rbp)
.L21:
	movl	-236(%rbp), %eax
	cmpl	-228(%rbp), %eax
	jl	.L24
.L23:
	movzbl	-254(%rbp), %eax
	xorl	$1, %eax
	testb	%al, %al
	je	.L25
	movsbl	-253(%rbp), %edx
	movq	stderr(%rip), %rax
	movq	-184(%rbp), %rcx
	leaq	.LC118(%rip), %rsi
	movq	%rax, %rdi
	movl	$0, %eax
	call	fprintf@PLT
	movq	-184(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movq	-192(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movl	$0, %eax
	jmp	.L37
.L25:
	movl	-240(%rbp), %eax
	movslq	%eax, %rdx
	movq	-184(%rbp), %rax
	addq	%rdx, %rax
	movb	$0, (%rax)
	movl	-240(%rbp), %eax
	movl	%eax, -248(%rbp)
	nop
	jmp	.L28
.L20:
	addl	$1, -240(%rbp)
.L19:
	movl	-240(%rbp), %eax
	cmpl	-248(%rbp), %eax
	jl	.L27
	jmp	.L28
.L18:
	addl	$1, -244(%rbp)
.L17:
	movl	-244(%rbp), %eax
	cmpl	-232(%rbp), %eax
	jl	.L29
.L28:
	movq	-208(%rbp), %rax
	addq	$1, %rax
	salq	$4, %rax
	movq	%rax, %rdx
	movq	-216(%rbp), %rax
	movq	%rdx, %rsi
	movq	%rax, %rdi
	call	realloc@PLT
	movq	%rax, -216(%rbp)
	movq	-208(%rbp), %rax
	salq	$4, %rax
	movq	%rax, %rdx
	movq	-216(%rbp), %rax
	addq	%rax, %rdx
	movl	-252(%rbp), %eax
	cltq
	salq	$4, %rax
	movq	%rax, %rcx
	leaq	patterns(%rip), %rax
	movq	(%rcx,%rax), %rax
	movq	%rax, (%rdx)
	movq	-208(%rbp), %rax
	salq	$4, %rax
	movq	%rax, %rdx
	movq	-216(%rbp), %rax
	addq	%rax, %rdx
	movq	-184(%rbp), %rax
	movq	%rax, 8(%rdx)
	addq	$1, -208(%rbp)
	movq	-224(%rbp), %rdx
	movl	-248(%rbp), %eax
	cltq
	addq	%rdx, %rax
	movq	%rax, -224(%rbp)
	movb	$1, -255(%rbp)
	leaq	-176(%rbp), %rax
	movq	%rax, %rdi
	call	regfree@PLT
	jmp	.L32
.L14:
	leaq	-176(%rbp), %rax
	movq	%rax, %rdi
	call	regfree@PLT
	addl	$1, -252(%rbp)
.L11:
	movl	$57, %eax
	cmpl	%eax, -252(%rbp)
	jl	.L33
.L32:
	movzbl	-255(%rbp), %eax
	xorl	$1, %eax
	testb	%al, %al
	je	.L8
	movq	-224(%rbp), %rdx
	movq	stderr(%rip), %rax
	leaq	.LC119(%rip), %rcx
	movq	%rcx, %rsi
	movq	%rax, %rdi
	movl	$0, %eax
	call	fprintf@PLT
	movq	-192(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movq	$0, -200(%rbp)
	jmp	.L34
.L35:
	movq	-200(%rbp), %rax
	salq	$4, %rax
	movq	%rax, %rdx
	movq	-216(%rbp), %rax
	addq	%rdx, %rax
	movq	8(%rax), %rax
	movq	%rax, %rdi
	call	free@PLT
	addq	$1, -200(%rbp)
.L34:
	movq	-200(%rbp), %rax
	cmpq	-208(%rbp), %rax
	jb	.L35
	movq	-216(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movl	$0, %eax
	jmp	.L37
.L8:
	movq	-224(%rbp), %rax
	movzbl	(%rax), %eax
	testb	%al, %al
	jne	.L36
	jmp	.L10
.L39:
	nop
.L10:
	movq	-192(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
	movq	-272(%rbp), %rax
	movq	-208(%rbp), %rdx
	movq	%rdx, (%rax)
	movq	-216(%rbp), %rax
.L37:
	movq	-8(%rbp), %rdx
	subq	%fs:40, %rdx
	je	.L38
	call	__stack_chk_fail@PLT
.L38:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE7:
	.size	lex, .-lex
	.section	.rodata
.LC120:
	.string	"int main() { a=1+1;} ;"
.LC121:
	.string	"(%s, '%s')\n"
	.text
	.globl	main
	.type	main, @function
main:
.LFB8:
	.cfi_startproc
	endbr64
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	subq	$32, %rsp
	movq	%fs:40, %rax
	movq	%rax, -8(%rbp)
	xorl	%eax, %eax
	leaq	-32(%rbp), %rax
	movq	%rax, %rsi
	leaq	.LC120(%rip), %rax
	movq	%rax, %rdi
	call	lex
	movq	%rax, -16(%rbp)
	cmpq	$0, -16(%rbp)
	je	.L41
	movq	$0, -24(%rbp)
	jmp	.L42
.L43:
	movq	-24(%rbp), %rax
	salq	$4, %rax
	movq	%rax, %rdx
	movq	-16(%rbp), %rax
	addq	%rdx, %rax
	movq	8(%rax), %rdx
	movq	-24(%rbp), %rax
	salq	$4, %rax
	movq	%rax, %rcx
	movq	-16(%rbp), %rax
	addq	%rcx, %rax
	movq	(%rax), %rax
	movq	%rax, %rsi
	leaq	.LC121(%rip), %rax
	movq	%rax, %rdi
	movl	$0, %eax
	call	printf@PLT
	movq	-24(%rbp), %rax
	salq	$4, %rax
	movq	%rax, %rdx
	movq	-16(%rbp), %rax
	addq	%rdx, %rax
	movq	8(%rax), %rax
	movq	%rax, %rdi
	call	free@PLT
	addq	$1, -24(%rbp)
.L42:
	movq	-32(%rbp), %rax
	cmpq	%rax, -24(%rbp)
	jb	.L43
	movq	-16(%rbp), %rax
	movq	%rax, %rdi
	call	free@PLT
.L41:
	movl	$0, %eax
	movq	-8(%rbp), %rdx
	subq	%fs:40, %rdx
	je	.L45
	call	__stack_chk_fail@PLT
.L45:
	leave
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE8:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 13.3.0-6ubuntu2~24.04) 13.3.0"
	.section	.note.GNU-stack,"",@progbits
	.section	.note.gnu.property,"a"
	.align 8
	.long	1f - 0f
	.long	4f - 1f
	.long	5
0:
	.string	"GNU"
1:
	.align 8
	.long	0xc0000002
	.long	3f - 2f
2:
	.long	0x3
3:
	.align 8
4:
