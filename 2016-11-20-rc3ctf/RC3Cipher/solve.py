#!/usr/bin/env python3

from pwn import *

xor_key = 'rc3cipherbestcipher'
flag = '1b65380f084b59016875513c6373131d2a6a327172753a2918243d7b181a051e5f1e104c32331c0842777b375f100113'

def build_smaller_chars(biggest_char):

    smaller_chars = list(range(biggest_char - 1, -1, -1))

    v8 = 0

    for smaller_char_index in range(len(smaller_chars)):
        v3 = smaller_chars[smaller_char_index] + v8
        v8 = ((v3) + ord(xor_key[::-1][smaller_char_index % len(xor_key)])) % biggest_char
        v5 = smaller_chars[smaller_char_index]

        smaller_chars[smaller_char_index] = smaller_chars[v8]
        smaller_chars[v8] = v5

    return smaller_chars

def xor_with_smaller_chars(smaller_chars, flag_chars, biggest_char):
    v6 = 0
    v7 = 0

    for flag_char_index in range(len(flag_chars)):
        v6 = (v6 + 1) % biggest_char
        v7 = (smaller_chars[v6] + v7) % biggest_char
        v4 = smaller_chars[v6]

        smaller_chars[v6] = smaller_chars[v7]
        smaller_chars[v7] = v4

        flag_chars[flag_char_index] ^=  smaller_chars[(smaller_chars[v6] + smaller_chars[v7]) % biggest_char]


    return ''.join(map(chr, flag_chars))


for biggest_char in range(1, 255):

    smaller_chars = build_smaller_chars(biggest_char)
    xored_with_key = list(xor(unhex(flag), xor_key))

    decrypted_flag = xor_with_smaller_chars(smaller_chars, xored_with_key, biggest_char)

    if 'RC3' in decrypted_flag:
        # RC3-2016-Y0UR-KSA-IS-BAD-@ND-Y0U-SH0ULD-F33L-BAD
        print(decrypted_flag)