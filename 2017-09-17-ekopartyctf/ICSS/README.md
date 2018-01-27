# ICSS (MISC)
Author: MH

This challenge was about reversing the encryption of an "Irreversible Cipher Stream Service".
## Challenge description
```text
The Irreversible Cipher Stream Service was used by someone to encrypt a secret, luckily we have found a freeware version of this weird service that could be used to get the secret.

This is the base64-encoded encrypted secret: 
ypovStywDFkNEotWNc3AxtlL2IwWKuJA1qawdvYynITDDIpknntQR1gB+Nzl

nc icss.ctf.site 40112
```

## Solution
This is an example session when you connect to this address:
```bash
$ nc icss.ctf.site 40112
Welcome to Irreversible Cipher Stream Service
	Freeware version 0.0.1 alpha (up to 6 chars)

Type you plain text: aaaa
B64 cipher output: oGOipII=
```

So we can test this ICSS with up to 6 characters. When I tested it for some time, it was obvious that depending on the position of the character, it is encoded differently. For example with the letter "a":
```
a	=>	oA==
aa	=>	oGM=
aaa	=>	oGOi
aaaa	=>	oGOipA==
aaaaa	=>	oGOipOk=
aaaaaa	=>	oGOipOks
```
That also means, that it is a problem that this "freeware version" only encrypts 6 chars, because otherwise we could bruteforce the flag. However before realising that I tried bruteforcing, which gave me the start of the flag: `EKO{Mr`

What brought me on the right track was the idea of a friend to try the following command:
`printf '\x00\x00\x00\x00\x00\x00'| nc icss.ctf.site 40112`
That plaintext is encrypted to `AQECAwUI` which is after base64 decoding and translating to binary: `1 1 10 11 101 1000`. That are the starting numbers of the [Fibonacci](https://en.wikipedia.org/wiki/Fibonacci_number) sequence: `1, 1, 2, 3, 5`

However for example `printf '\x61\x00\x00\x00\x00\x00'| nc icss.ctf.site 40112` was `10100000 10 11000011 11000101 10001000 1001101` in binary, which is not exactly a part of the Fibonacci sequence. 
On the other hand `printf '\x00\x00\x00\x00\x00\x61'| nc icss.ctf.site 40112` is encrypted to `1 1 10 11 101 1101001` which makes much more sense (the start is still Fibonacci). So apparently the first character messes up our Fibonacci sequence. When trying plaintexts like '\x01\x00\x00\x00\x00\x00'  (encrypts to `0 10 11 101 1000 1101`) it became clear that the **first number decides where we start in the sequence**. In this case zero is some sort of special case where we start with `fib[1] = 1`, when the first byte is `\x01` the sequence starts from the second character with `fib[3] = 2` (The first characters encoding is different from the others, but that doesn't matter since we know that one already). Generally it holds that when `i` is the order of the first character, the sequence starts at `fib[i+2]`.

With a low number for the first byte (for example `\x00`) it is easy to see that the ciphertext is the XOR of the order of the plaintext character and the fibonacci number at that place.

But we still have a problem: The Fibonacci numbers grow bigger very fast:
```
2: 0b1
3: 0b10
4: 0b11
5: 0b101
6: 0b1000
7: 0b1101
8: 0b10101
9: 0b100010
10: 0b110111
11: 0b1011001
12: 0b10010000
13: 0b11101001
14: 0b101111001
15: 0b1001100010
```
Which means already `fib[14]` has more than 8 bits.  The easiest solution is to XOR the plaintext character at position `j` with `fib[j+2]%128`. And indeed that's what the ICSS does.

So finally I wrote the following little script to generate the Fibonacci numbers and directly decrypt the flag. I knew that the first letter was `E` because of the bruteforce attempt, of course that would have been easy to guess.

This produced the flag: `EKO{Mr_Leon4rd0_PisAno_Big0770_AKA_Fib@nacc!}`

```python
#!/usr/bin/python

from base64 import b64decode

fib = [0]*128

# generate Fibonacci numbers
fib[0] = 0
fib[1] = 1
i = 2
while i < 128:
    fib[i] = fib[i-1] + fib[i-2]
    i += 1

# decode the flag
flag = 'E'
cipher = b64decode('ypovStywDFkNEotWNc3AxtlL2IwWKuJA1qawdvYynITDDIpknntQR1gB+Nzl')

fibSequenceStart = ord(flag[0]) + 1

cipherIndex = 1
while cipherIndex < len(cipher):
    flag += chr((ord(cipher[cipherIndex]) ^ fib[fibSequenceStart + cipherIndex])%128)
    cipherIndex += 1

print(flag)
```
