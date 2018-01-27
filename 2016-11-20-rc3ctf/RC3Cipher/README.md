# RC3Cipher (Reversing 350)
Author: muffinx

In this task we get a binary [rc3_cipher](rc3_cipher) which we have to break it's encryption cycle.

```
rc3_cipher: ELF 64-bit LSB executable, x86-64, version 1 (SYSV),
dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2,
for GNU/Linux 2.6.24, BuildID[sha1]=2be167e9bcde8cfa3e906c83a0f9fe866c7ca8f7, not stripped
```

If we start it without arguments we'll be welcomed with a nice memory error.

When looking quickly at the entrypoint of the program we see clear references to argv[1].

So we'll try some input:

```
./rc3_cipher aaaaaa
Your ciphertext is: 4625622e3735
Generic response one.
```


So we have a small program, which only shows the encrypted value of argv[1] with this cipher called "rc3cipher".
We have to find somewhere the flag, so let's take a look at the strings in the application:

```
.rodata:0000000000400BD8   1b65380f084b59016875513c6373131d2a6a327172753a2918243d7b181a051e5f1e104c32331c0842777b375f100113
.rodata:0000000000400C39   rc3cipherbestcipher
.rodata:0000000000400C4D   %s%02x
.rodata:0000000000400C54   Your ciphertext is: %s\n
.rodata:0000000000400C6C   Generic response two.
.rodata:0000000000400C82   Generic response one.
.eh_frame:0000000000400D4F ;*3$\"
```



"1b65380f084b59016875513c6373131d2a6a327172753a2918243d7b181a051e5f1e104c32331c0842777b375f100113" looks like our flag.
So we have to reverse the binary, to write a decryption subroutine by analyzing the encryption routine.


So we generate some pseudocode and look closely at the application entrypoint:


```c
arguments_number = argc;
arguments = argv;
v15 = (__int64 *)&strlen_plus_one_mult2_2;
argv1 = (char *)argv[1];
xor_key = "rc3cipherbestcipher";
strlen_plus_one_mult2 = 2 * strlen(argv1) + 1;
v24 = strlen_plus_one_mult2 - 1;
v13 = strlen_plus_one_mult2;
v14 = 0LL;
strlen_plus_one_mult2_2 = strlen_plus_one_mult2;
v12 = 0LL;
v4 = alloca(16 * ((strlen_plus_one_mult2 + 15) / 0x10));
hex_encrypted_text = (char *)&strlen_plus_one_mult2_2;
biggest_char = (char)get_biggest_char(argv1) + 1; // get the biggest character of argv1
argv_strlen = strlen(argv1);
biggest_char_minus_1 = biggest_char - 1LL;
v5 = alloca(16 * ((biggest_char + 15LL) / 16uLL));
smaller_chars = (__int64 *)&strlen_plus_one_mult2_2;
```


We first see here a big block of variable initializations.
There's a function which we can rename ot "get_biggest_char", why?
Because it's function code is quite clear:

```c
__int64 __fastcall get_biggest_char(const char *argv1)
{
  char biggest_char; // [sp+1Bh] [bp-15h]@1
  int curr_index; // [sp+1Ch] [bp-14h]@1

  biggest_char = -1;
  for ( curr_index = 0; curr_index < strlen(argv1); ++curr_index )
  {
    if ( argv1[curr_index] > biggest_char )
      biggest_char = argv1[curr_index];
  }
  return (unsigned __int8)biggest_char;
}
```

Sets a char (biggest_char) to -1 and loops trough each character of argv1, if this argv character is bigger than
the biggest_char character, biggest_char will take it's value.

Back into the main function we see a small loop:

```c

for ( curr_index = 0; (signed int)curr_index < (signed int)argv_strlen; ++curr_index )// first xor input with "rc3cipherbestcipher"
{
  argv1_char = &argv1[curr_index];
  old_argv1_char = *argv1_char;
  xor_key_index = (signed int)curr_index;
  xor_key_length = strlen(xor_key);
  *argv1_char = old_argv1_char ^ xor_key[xor_key_index % xor_key_length];
}
```

This xors argv[1] with "rc3cipherbestcipher".


Next we have got 2 crazy functions which do some black magic:

```c
builder_smaller_chars((__int64)smaller_chars, xor_key, biggest_char);// builds_smaller chars
functiontwo((__int64)smaller_chars, (__int64)argv1, biggest_char, argv_strlen);// encryption operation 2
```

(We'll ignore them to get a better overview)


```c
*hex_encrypted_text = 0;                      // convert encrypted_text to hex
for ( argv1_index = 0; (signed int)argv1_index < (signed int)argv_strlen; ++argv1_index )
  sprintf(
    hex_encrypted_text,
    "%s%02x",
    hex_encrypted_text,
    (unsigned int)argv1[argv1_index],
    strlen_plus_one_mult2_2,
    v12,
    v13,
    v14);
printf("Your ciphertext is: %s\n", hex_encrypted_text, strlen_plus_one_mult2_2, v12, v13, v14);
if ( !strcmp(functionfour, hex_encrypted_text) )// compare with encrypted flag
  puts("Generic response two.");
else
  puts("Generic response one.");
return 0;
```

After those two functions the encrypted argv[1] will be converted to hex character by character, and
the messages will be displayed.

We can see
```c
strcmp(functionfour, hex_encrypted_text)
```

which compares the encrypted argv[1] with the encrypted flag.
If that's correct we get

```c
puts("Generic response two."); (goodboy)
```

else

```c
puts("Generic response one."); (badboy)
```


So what the application does:


1. gets argv[1]
2. get the biggest char of argv[1]
3. xors argv[1]
4. black magic
5. convert to hex
6. compare with encrypted flag
7. goodboy / badboy


So let's dive into those black magic functions, to see whats happening in there:

---

```c


__int64 __fastcall builder_smaller_chars(__int64 smaller_chars, const char *xor_key, signed int biggest_char)
{
  int v3; // er13@5
  size_t xor_key_strlen; // rbx@5
  char v5; // ST2C_1@5
  __int64 result; // rax@6
  signed int biggest_character; // [sp+Ch] [bp-44h]@1
  int v8; // [sp+20h] [bp-30h]@1
  int curr_smaller_char; // [sp+24h] [bp-2Ch]@1
  unsigned int smaller_chars_index; // [sp+28h] [bp-28h]@4

  biggest_character = biggest_char;
  v8 = 0;
  for ( curr_smaller_char = biggest_char - 1; curr_smaller_char >= 0; --curr_smaller_char )// build all characters before the biggest character
    *(_BYTE *)(smaller_chars + biggest_char - curr_smaller_char - 1LL) = curr_smaller_char;
  for ( smaller_chars_index = 0; ; ++smaller_chars_index )
  {
    result = smaller_chars_index;
    if ( (signed int)smaller_chars_index >= biggest_character )
      break;                                    // loop through all smaller chars
    v3 = *(_BYTE *)((signed int)smaller_chars_index + smaller_chars) + v8;
    xor_key_strlen = strlen(xor_key);
    v8 = (v3 + xor_key[xor_key_strlen - (signed int)smaller_chars_index % strlen(xor_key) - 1]) % biggest_character;
    v5 = *(_BYTE *)((signed int)smaller_chars_index + smaller_chars);
    *(_BYTE *)(smaller_chars + (signed int)smaller_chars_index) = *(_BYTE *)(v8 + smaller_chars);
    *(_BYTE *)(smaller_chars + v8) = v5;
  }
  return result;
}
```


As we can see builder_smaller_chars(__int64 smaller_chars, const char *xor_key, signed int biggest_char) takes a pointer to smaller_chars,
a pointer to xor_key ("rc3cipherbestcipher") , and biggest_character as signed int.

Let's go through that pseudocode:

```c
for ( curr_smaller_char = biggest_char - 1; curr_smaller_char >= 0; --curr_smaller_char )// build all characters before the biggest character
  *(_BYTE *)(smaller_chars + biggest_char - curr_smaller_char - 1LL) = curr_smaller_char;
```


Loops from (biggest_char - 1) to 0.
Then it writes one byte to:
smaller_chars[biggest_char - curr_smaller_char - 1] = curr_smaller_char

The first value of curr_smaller_char is (biggest_char -1), so for example if
biggest_char = 'a' (0x61)
curr_smaller_char = '`' (0x60)

so:

```
smaller_chars[0x61 - 0x60 - 1] = ` (0x60)
smaller_chars[0] = ` (0x60)
```

next step:

```
smaller_chars[0x61 - 0x5F - 1] = _ (0x5F)
smaller_chars[1] = _ (0x5F)
```



So that means, that we have in the end an array of smaller characters of the biggest char.
So for 'a' that would be:

`_^]\[ZYXWVUT(...)

So first there is a buffer with a lenght of biggest_char-1 being constructed.
We can call that buffer "smaller_chars".

Next we loop through that buffer.



```c

biggest_character = biggest_char;
v8 = 0;

for ( smaller_chars_index = 0; ; ++smaller_chars_index )
{
  result = smaller_chars_index;
  if ( (signed int)smaller_chars_index >= biggest_character )
    break;                                    // loop through all smaller chars
  v3 = *(_BYTE *)((signed int)smaller_chars_index + smaller_chars) + v8;
  xor_key_strlen = strlen(xor_key);
  v8 = (v3 + xor_key[xor_key_strlen - (signed int)smaller_chars_index % strlen(xor_key) - 1]) % biggest_character;
  v5 = *(_BYTE *)((signed int)smaller_chars_index + smaller_chars);
  *(_BYTE *)(smaller_chars + (signed int)smaller_chars_index) = *(_BYTE *)(v8 + smaller_chars);
  *(_BYTE *)(smaller_chars + v8) = v5;
}
```


Simply said, the value of v3, v8 and v5 is being calculated.
v3 is only used in v8, so we can put that together:

```c
v8 = (*(_BYTE *)((signed int)smaller_chars_index + smaller_chars) + v8; + xor_key[xor_key_strlen - (signed int)smaller_chars_index % strlen(xor_key) - 1]) % biggest_character;
```

to write that simpler:

```c
v8 = (smaller_chars[smaller_chars_index] + v8 + xor_key[len(xor_key) - (smaller_chars_index) % len(xor_key) - 1]) % biggest_character
```

So it takes the current smaller_char smaller_chars[smaller_chars_index] adds v8 to it (at the beginning 0) and adds a xor character to it.

**ATTENTION:** Here the xor string is actually reversed.

Because:

```c
xor_key[len(xor_key) - (smaller_chars_index) % len(xor_key) - 1]

for index 0:

xor_key[len("rc3cipherbestcipher") - (0) % len("rc3cipherbestcipher") - 1] | simplify
xor_key[19 - 0 % 19 - 1] | simplify
xor_key[19 - 1]
xor_key[18]
```



In the end it calculates modulus biggest_character to ensure that the value doesn't exceed the size of smaller_chars (because the value will be used as an index).

```c
v5 = *(_BYTE *)((signed int)smaller_chars_index + smaller_chars);
*(_BYTE *)(smaller_chars + (signed int)smaller_chars_index) = *(_BYTE *)(v8 + smaller_chars);
*(_BYTE *)(smaller_chars + v8) = v5;
```

Simpler:

```c
v5 = smaller_chars[smaller_chars_index]
smaller_chars[smaller_chars_index] = smaller_chars[v8]
smaller_chars[v8] = v5
```

So in two sentences what builder_smaller_chars does:

Builds smaller_chars, loops through them and switches each time the current small_char with the small_char at v8.
v8 is a variable which is the current small_char added to the old v8 and a character of the reversed xor key.

So because the only "dynamic" variable is biggest_character which has 256 possibilities, so builder_smaller_chars also
has only 256 possibilities of results, we should keep this in our minds.

---


```c

__int64 __fastcall functiontwo(__int64 smaller_chars, __int64 argv1, signed int biggest_character, unsigned int argv1_strlen)
{
  char v4; // ST24_1@2
  __int64 result; // rax@3
  int v6; // [sp+18h] [bp-10h]@1
  int v7; // [sp+1Ch] [bp-Ch]@1
  signed int argv1_chr_index; // [sp+20h] [bp-8h]@1

  v6 = 0;
  v7 = 0;
  for ( argv1_chr_index = 0; ; ++argv1_chr_index )
  {
    result = (unsigned int)argv1_chr_index;
    if ( argv1_chr_index >= (signed int)argv1_strlen ) // loops through all argv1 characters
      break;
    v6 = (v6 + 1) % biggest_character;
    v7 = (*(_BYTE *)(v6 + smaller_chars) + v7) % biggest_character;
    v4 = *(_BYTE *)(v6 + smaller_chars);
    *(_BYTE *)(smaller_chars + v6) = *(_BYTE *)(v7 + smaller_chars);
    *(_BYTE *)(smaller_chars + v7) = v4;
    *(_BYTE *)(argv1_chr_index + argv1) ^= *(_BYTE *)((*(_BYTE *)(v6 + smaller_chars) + *(_BYTE *)(v7 + smaller_chars))
                                                    % biggest_character
                                                    + smaller_chars);
  }
  return result;
}
```

Let's analyze functiontwo.
What we can see is now that also argv1 is passed.
We can see that argv1[argv1_chr_index] is being xored with some value.
This algorithm is close to builder_smaller_chars:

```c
v6 = (v6 + 1) % biggest_character;
v7 = (*(_BYTE *)(v6 + smaller_chars) + v7) % biggest_character;
v4 = *(_BYTE *)(v6 + smaller_chars);
*(_BYTE *)(smaller_chars + v6) = *(_BYTE *)(v7 + smaller_chars);
*(_BYTE *)(smaller_chars + v7) = v4;
```

Again switches chars.

```c
*(_BYTE *)(argv1_chr_index + argv1) ^= *(_BYTE *)((*(_BYTE *)(v6 + smaller_chars) + *(_BYTE *)(v7 + smaller_chars)) % biggest_character + smaller_chars);
```

Xores argv1[argv1_chr_index] with smaller_chars[(smaller_chars[v6] + smaller_chars[v7]) % biggest_character].

---

## Solution

So I wrote a python script which implements the whole cycle to bruteforce biggest_char and to decrypt the encryted flag with it: [solve.py](solve.py)

FLAG = RC3-2016-Y0UR-KSA-IS-BAD-@ND-Y0U-SH0ULD-F33L-BAD

## Conclusion

In the end I have to say, I have solved this challenge in a too complex way.
The decryption cycle is exactly the same as the encryption cycle.

So it's also solveable by calling the binary with the encrypted flag as param,
like Inndy did:

https://gist.github.com/Inndy/eca85d80f9e03260d35bff5c1c22b6b1

Credits to Inndy, nice solution!

I hope that this small writeup anyway showed how to breakdown the code of rc3cipher so
we understand the functionality to 100%.