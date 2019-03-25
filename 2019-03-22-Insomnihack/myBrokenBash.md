# myBrokenBash

## About
In this challenge we were provided with a simple echo service.
You could connect to it:

```bash
nc mybrokenbash.insomni.hack 1337
```
And afterwards send some text which got repeated.

## Step 1: Prison break
I was able to break out of the jail by providing the following input:

```bash
exec > /dev/tty
```
Now we spawned a regular bash shell.

## Step 2: Deeply hidden
When listing the files I found one called flag:

```bash
ls
bin   dev  flag  lib	media  opt   root  sbin  sys  usr
boot  etc  home  lib64	mnt    proc  run   srv	 tmp  var
```

But it didn't reveal everything yet:
```bash
cat flag
almost there ;-)_1t_s_n0t_so_ea4y}
```

Now I only needed to print the 'full' file not only the characters after the carriage return:

```bash
cat -A flag
INS{c@t_th3_Flag_1t_s_n0t_so_ea4y}^Malmost there ;-)$
```

Flag: INS{c@t_th3_Flag_1t_s_n0t_so_ea4y}


## Bonus

Here's the binary I extracted :

```bash
[0x000008c0]> pdf @ main
/ (fcn) main 116
|   main (int argc, char **argv, char **envp);
|           ; var int canary @ rbp-0x8
|           ; DATA XREF from entry0 (0x8dd)
|           0x00000ab4      55             push rbp
|           0x00000ab5      4889e5         mov rbp, rsp
|           0x00000ab8      4883ec10       sub rsp, 0x10
|           0x00000abc      64488b042528.  mov rax, qword fs:[0x28]    ; [0x28:8]=0x1138 ; '('
|           0x00000ac5      488945f8       mov qword [canary], rax
|           0x00000ac9      31c0           xor eax, eax
|           0x00000acb      b800000000     mov eax, 0
|           0x00000ad0      e84bffffff     call sub.dev_urandom_a20
|           0x00000ad5      488d3dec0000.  lea rdi, str.Welcome_to__INS19 ; 0xbc8 ; "*** Welcome to #INS19!! ***\n" ; const char *s
|           0x00000adc      e86ffdffff     call sym.imp.puts           ; int puts(const char *s)
|           0x00000ae1      488d3dfd0000.  lea rdi, str.cat_the_flag_here_please ; 0xbe5 ; "cat the flag here please ;-)" ; const char *s
|           0x00000ae8      e863fdffff     call sym.imp.puts           ; int puts(const char *s)
|           0x00000aed      bf01000000     mov edi, 1                  ; int fildes
|           0x00000af2      e879fdffff     call sym.imp.close          ; int close(int fildes)
|           0x00000af7      bf02000000     mov edi, 2                  ; int fildes
|           0x00000afc      e86ffdffff     call sym.imp.close          ; int close(int fildes)
|           0x00000b01      488d3dfa0000.  lea rdi, str.bin_sh         ; 0xc02 ; "/bin/sh" ; const char *string
|           0x00000b08      e853fdffff     call sym.imp.system         ; int system(const char *string)
|           0x00000b0d      b800000000     mov eax, 0
|           0x00000b12      488b55f8       mov rdx, qword [canary]
|           0x00000b16      644833142528.  xor rdx, qword fs:[0x28]
|       ,=< 0x00000b1f      7405           je 0xb26
|       |   0x00000b21      e832fdffff     call sym.imp.__stack_chk_fail ; void __stack_chk_fail(void)
|       |   ; CODE XREF from main (0xb1f)
|       `-> 0x00000b26      c9             leave
\           0x00000b27      c3             ret
```
