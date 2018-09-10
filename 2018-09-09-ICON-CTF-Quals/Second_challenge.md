
# ICON 2018 CTF Quals Crypto Challenge
Author: \_MH\_

## Task material
The task has no description. We are given the following script (not shortened version [here](./assets/wb.py)):

```python
#!/usr/bin/env python3

import base64
import struct
import zlib
import pickle

data = # [I left away 13590 lines of data for the gigantic table here]

tables = pickle.loads(zlib.decompress(base64.decodestring(data)))

def encrypt(pt):
	state = pt[8:] + pt[:8]
	for i in range(32):
		r = 0
		x2 = [0] * 16
		for j in range(16):
			s = 0
			for k in range(16):
				s ^= tables[0][i][j][k][state[k]]
			x2[j] = s
		state = x2
		for j in range(8):
			a = tables[1][i][state[j] * 512 + state[j+8] * 2 + r]
			r = (a & 0x100) >> 8
			state[j] = a & 0xff
		x2 = [0] * 16
		for j in range(16):
			s = 0
			for k in range(16):
				s ^= tables[2][i][j][k][state[k]]
			x2[j] = s
		state = x2
	return bytes(state[8:]+state[:8])

def ror64(x, r):
	return (x >> r) | (x << (64-r)) & 0xffffffffffffffff

def rol64(x, r):
	return (x << r) | (x >> (64-r)) & 0xffffffffffffffff

def r(x, y, k):
	x = ror64(x, 8)
	x += y
	x &= 0xffffffffffffffff
	x ^= k
	y = rol64(y, 3)
	y &= 0xffffffffffffffff
	y ^= x
	return x, y

def encrypt_ref(pt, k):
	y, x = struct.unpack('<2Q', pt)
	b, a = struct.unpack('<2Q', k)
	x, y = r(x, y, b)
	for i in range(31):
		a, b = r(a, b, i)
		x, y = r(x, y, b)

	return struct.pack('<2Q',y, x)

def challenge():
	pt = input('plaintext: ')
	key = input('key: ')
	if len(pt) != 16 or len(key) != 16:
		print('Expecting 16 bytes inputs')
		return
	ct1 = encrypt_ref(bytes(pt, 'utf-8'), bytes(key, 'utf-8'))
	ct2 = encrypt(bytes(pt, 'utf-8'))
	if ct1 == ct2:
		print ("Congratulations ! use", key, "as flag")
	else:
		print ("Please try again !")
if __name__ == '__main__':
	challenge()
``` 

### What is the task?
Let's look at `challenge()`: We're asked to input a plaintext (saved in `pt`) and a key. Then two functions are called, `encrypt_ref()` and `encrypt()`. The produced ciphertexts of the two, `ct1` and `ct2`, have to be the same. 
From that we gather that we have to find the `key` that makes `encrypt_ref()` equivalent to `encrypt()`. Since `encrypt()` does not use `key`, it suggests that it has the key somehow hardcoded in its functionalities. We have to find out what it does and extract that key.

## Solution
Let's first understand how `encrypt_ref()` and `encrypt()` work.

### Encrypt_ref
`encrypt_ref()` applies r() multiple times, to both the key and the plaintext.
```python
def encrypt_ref(pt, k):
	y, x = struct.unpack('<2Q', pt)
	b, a = struct.unpack('<2Q', k)
	x, y = r(x, y, b)
	for i in range(31):
		a, b = r(a, b, i)
		x, y = r(x, y, b)

	return struct.pack('<2Q',y, x)
```
`r()` itself applies a series of simple operations as commented below. This function is really the core of the encryption and will also be key to understand what `encrypt()` does.
```python
def r(x, y, k):
    # Move last byte (calling the lsb in little endain
    # the last byte) to the front
    x = ror64(x, 8)

    # Add other half of plaintext
    x += y

    # Clear overflow (now exactly 8 bytes again)
    x &= 0xffffffffffffffff

    # XOR with k (part of the key)
    x ^= k

    # Move first 3 bits to back
    y = rol64(y, 3)
	y &= 0xffffffffffffffff
    
    # XOR changed x to it
    y ^= x
    
    return x, y
```

### Encrypt
That function is _way more difficult_. After hours of studying, it crystallises that the function really does the same as `encrypt_ref()`, i.e. in each iteration it does basically the same operations as `encrypt()` in `r()`, except that it does them in an obfuscated way using the table, in a slightly different order and one operation is even spread over two iterations of the loop. I try to explain in detail how it works.

To be clear, with _iteration_ I refer to one pass of the outermost loop `for i in range(32)`.

The table has the following dimensions:
```
tables[0] :: 32 x 16 x 16 x 256
tables[1] :: 32 x 131072
tables[2] :: 32 x 16 x 16 x 256
```
 
Before reporting what I found what the code does, maybe it makes sense to make an intermezzo about how I tried to find out and in the end also got what the code does with the table. (If your only interested in the solution to this task, you can skip the intermezzo if you like).

#### Intermezzo: Analysis and connection of sequences & XOR
I looked at the entries of the table for the first iteration. Specifically first for `i = 0, j = 0, k = 0..15, s = 0..255` (for the last I test all possible entries for `state[k]`, from `0` to `255` (incl.), because we don't know which value we'll have there). 
I was sure that there has to be a pattern, so I wanted to express it as a sequence. The idea was to build a mathematical formula of how the x and y change after the first iteration. I hoped to be able to reduce that formula to a shorter, simpler version that tells me what the iteration actually does.

For example one sequence looked like this (for `state[k] = 0..11`):
```
28 29 30 31
24 25 26 27
20 21 22 23
...
```
Which I found to be the following sequence:
```
seq(28, n) := 28 + n - (n//4)*8 + (n//32)*64
```
Which actually caused a lot of problems. The issue is that the integer divisions (`//` in python) _floor_ the number, making it a real pain to work with the sequences, not to mention to reduce them to a simpler form.

Some hours later, I finally noticed that this sequence is actually *equivalent* to a simple `^ 28` (XOR). I never realised this connection before and I also don't think you were expected to know or even realise this to solve the challenge. I rather think you should have seen/guessed that the values in the table were just XORs with a certain value.

Nevertheless, after first realising that connection, I looked into it a bit more and found the following rules to turn an XOR with a number (looking at the number in binary) to a sequence as the one above:

 - For every change from 0 to 1 or 1 to 0, there is a term in the sequence
 - If at pos `i` we have the first time a 0 after having 1's (or vice versa) then the sequence has the term `(n//(1 << i) )*(1 << (i+1))`
 - The sign of the term is positive iff the change is from 1's to 0's
 - The lsb is a 0, then it is `+ n`, otherwise `- n`

Example:
`def seq(n): return 28 + n - (n//4)*8 + (n//32)*64`
is actually `XOR 28` because 
`bin(28) = 0b11100`
so we have the following:
 - The lsb is a zero, so `+ n` 

and at pos 2 a change from 0 to 1, which means:
 - Negative sign
 - `(n//4)*8`

and at pos 5 a change from 1's to 0's:
 - Positive sign
 - `(n//32)*64`

Of course this is not necessary to find out what XOR a sequence represents. The first entry is `k XOR 0 = k` so you can just read of that the sequence is equivalent to an `XOR k` (that is if you know that the sequence represents some XOR).

#### Encrypt - Loop 1
Back to the `encrypt()` function. Let's start with the first loop.
```python
for j in range(16):
    s = 0

    for k in range(16):
        s ^= tables[0][i][j][k][state[k]]
    x2[j] = s
    
state = x2
```

This loops does multiple steps:

 - (all i): XOR the x's and y's all with the same value (for the y's this is written as a sequence, as explained)
 - (all i): Does the ror64(x, 8), i.e. transforms `[x[0], x[1], ..., x[7]]` to `[x[1], ..., x[7], x[0]]`
 - (i > 0): XOR the x's with the second part of the key
 - (i > 0): XOR also the y's, because they were XORed with the half finished x's in loop 3 of the previous iteration (see below)

#### Encrypt - Loop 2
Note that for this loop the table has different dimensions than for the other two loops.
```python
for j in range(8):
	 a = tables[1][i][state[j] * 512 + state[j+8] * 2 + r]

	 # I guess r is for when the addition overflows. But
	 # depending on the plaintext you choose it's never used.
	 r = (a & 0x100) >> 8

	 # cut off overflow
	 state[j] = a & 0xff
```

The entries of the table follow the same schema for all `i`, but with different sequences/xors.

I explain it using the example for `i = 0`:

For the following sequence:
`seq(start, n) := start + n - (n//4)*8 + (n//32)*64`
The entries in the table are built using a nested sequence:
`tables[1][0][s1 * 512 + s2*2] = seq(seq(56, s1), s2)`

That is actually equivalent to: `(s1 ^ 28) + (s2 ^ 28)`
Proof:
```
  seq(seq(56, s1), s2) 
= seq(seq(28+28, s1), s2)
= seq(28 + seq(28, s1), s2)    (see def. of seq)
= seq(28 + (28 ^ s1), s2)      (see the intermezzo above)
= (28 ^ s1) + seq(28, s2)      (def. of seq again)
= (28 ^ s1) + (28 ^ s2)
```

Because the x's and y's are always XORed with that value in the first loop (or the value they are XORed with has an XOR with that value taken into account), this *always* (i.e. in all iterations) simplifies to `x += y` which is equivalent to the `x += y` of `r()` (also in the sense that the added x's and y's are at this point the same as in `r()`, this will be important to recover the key).

#### Encrypt - Loop 3
```python
x2 = [0] * 16
for j in range(16):
    s = 0
    for k in range(16):
        s ^= tables[2][i][j][k][state[k]]
    x2[j] = s
state = x2
```
This loop does the following:
- XOR the x's with the first part of the key
- Do the `rol64(y, 3)` on the y's, which involves two XORs, e.g. `(y[0] << 3) ^ (y[7] >> 5)`
- Also do `y ^= x` (where x is the x that is XORed with part 1 of the key)

### Reversing `encrypt_ref()`
After understanding `encrypt()` and `encrypt_ref()` I can now explain my solution. I actually reversed `encrypt_ref()` somewhere during analysing `encrypt()`, because I hoped it gives me a clearer idea what to look for. Which it did, because instead of reversing the function to decrypt a ciphertext (which would need the key and is therefore not useful to us) I wrote `rev_encrypt_ref()` that recovers the key itself. For that it becomes apparent, that we need all intermediate x's and y's, i.e. those of the start (the plaintext), those after each iteration (after each call to `r()`) and those of the ciphertext in the end. 

`rev_encrypt_ref()` uses some helper functions:
- `revR()` reverses `r()` and is very easy, with `ror64` and `rol64` the inverse functions are already provided for us. The rest is obvious.
- `calcK()` calculates the `k` which was XORed to the `x` in `r()`. This is not to be confused with the `key`, since in `encrypt_ref()` in each iteration we also apply `r()` to the `key`. But we need to recover all intermediate versions of `k`. This is also why we need all versions of the x's and y's, because then we can do the operations of `r()` for the old x up to the last change, which is `x_old' ^= k` and then just recover `k = x_old' ^ x_new`.
- `calcXNew()` just as easy as `calcK()`

In the end this looks like this:
```python
'''
    Reverses the effect of r()
'''
def revR(x, y, k):
    y ^= x
    y = ror64(y, 3)
    y &= 0xffffffffffffffff
    x ^= k
    x -= y
    x = rol64(x, 8)
    x &= 0xffffffffffffffff
    return x, y
    
'''
    Calculate the k of 
        xNew, yNew = r(xOld, yOld, k) 
'''
def calcK(xNew, xOld, yOld):
    xOld = ror64(xOld, 8)
    xOld += yOld
    xOld &= 0xffffffffffffffff
    k = xNew ^ xOld

    return k

'''
    Calculate the xNew of
        xNew, yNew = r(xOld, yOld, k) 
'''
def calcXNew(yOld, yNew):
    yOld = rol64(yOld, 3)
    yOld &= 0xffffffffffffffff
    x = yNew ^ yOld
    
    return x

'''
    Reverse encrypt to get back the key

    Input: 	List of all x's and y's of the 
			intermediate iterations of encrypt_ref
	Output:	Original key
'''
def rev_encrypt_ref(xList, yList):
    xPlain, yPlain = xList[31], yList[31]
    xEnc, yEnc = xList[32], yList[32]
    
    bEnc = calcK(xEnc, xPlain, yPlain)

    for i in reversed(range(31)):
        xEnc, yEnc = xPlain, yPlain
        xPlain, yPlain = xList[i], yList[i]
        bPlain = calcK(xEnc, xPlain, yPlain)

        aEnc = calcXNew(bPlain, bEnc)

        aPlain, bPlain = revR(aEnc, bEnc, i)
        bEnc = bPlain
```

But we still need all intermediate x's and y's. After analysing the for loops in `encrypt_ref()`, we know that we can't take the x's and y's at the end of each iteration, because they are not finished then. We actually need to take those after the first loop. But we need to do two things:
- XOR again with the value that the first loop XORed all x's and y's for obfuscation (remember that XOR is removed again by the second loop).
- Reverse the effect of `ror64(x, 8)`, because that is already done in the first loop for the next iteration of `r()`

In the first iteration this gives us the original, plaintext x and y, after that we get the x's and y's of the iterations of `encrypt_ref()`. The last values of x and y, those of the ciphertext have to be added as a special case (they don't have a next iteration with a first loop).

All together this was my final solution (unshortened [here](./assets/wb-sol1.py)):
```python
#!/usr/bin/env python3

import base64
import struct
import zlib
import pickle

data = # [I left away 13590 lines of data for the gigantic table here]

'''
    The table has the dimension: 
    tables[0] :: 32 x 16 x 16 x 256
    tables[1] :: 32 x 131072
    tables[2] :: 32 x 16 x 16 x 256
'''
tables = pickle.loads(zlib.decompress(base64.decodestring(data)))

'''
    helper function to convert encrypt array to encrypt_ref longs
'''
def convXY(state):
    ct = bytes(state[8:]+state[:8])
    y, x = struct.unpack('<2Q', ct)

    return x, y

def encrypt(pt, debug = False):
    state = pt[8:] + pt[:8]

    '''
    	Save all intermediate values of x's and y's
    	(the values that are the same as in r()).
    	And use them then to recover the key with 
    	the reversed encrypt_ref.
    '''
    xList, yList = [0]*33, [0]*33
    
    if debug:
	    xp, yp = convXY(state)
	    print("Initial: \tx = {0}, y = {1}".format(hex(xp), hex(yp)))

    for i in range(32):
        r = 0
        x2 = [0] * 16

        for j in range(16):
            s = 0

            for k in range(16):
                s ^= tables[0][i][j][k][state[k]]
            x2[j] = s
        
        state = x2

        x3 = x2.copy()
        for k in range(16):
            x3[k] ^= tables[0][i][0][0][0]
        xp, yp = convXY(x3)

        xList[i] = rol64(xp, 8) & 0xffffffffffffffff
        yList[i] = yp

        if debug:
        	print("encrypt after 1. loop (xor rev): \tx = {0}, y = {1}".format(xList[i], yList[i]))

        for j in range(8):
            a = tables[1][i][state[j] * 512 + state[j+8] * 2 + r]

            # Overflow
            r = (a & 0x100) >> 8

            # Cut off overflow
            state[j] = a & 0xff

        if debug:
	        xp, yp = convXY(state)
	        print("encrypt after 2. loop: \tx = {0}, y = {1}".format(hex(xp), hex(yp)))

        x2 = [0] * 16
        for j in range(16):
            s = 0
            for k in range(16):
                s ^= tables[2][i][j][k][state[k]]
            x2[j] = s
        state = x2

        if debug:
        	xp, yp = convXY(state)
        	print("encrypt after 3. loop: \tx = {0}, y = {1}".format(hex(xp), hex(yp)))
    
    xp, yp = convXY(state)
    yList[32], xList[32] = convXY(state)

    # Switch the 8 byte blocks back
    return bytes(state[8:]+state[:8]), xList, yList

'''
    Put the lowest (little endian) r bits to the front. E.g.
    XX....XYY..Y is transformed to 
    YY..YXX....X
    for r Y's and 64-r X's, Y's are put to the front
'''
def ror64(x, r):
    return (x >> r) | (x << (64-r)) & 0xffffffffffffffff

'''
    Put the highest r bits (little endian) to the back. E.g.
    YY..YXX....X is transformed to 
    XX....XYY..Y
    for r Y's and 64-r X's, again Y's are moved.
'''
def rol64(x, r):
    return (x << r) | (x >> (64-r)) & 0xffffffffffffffff

def r(x, y, k):
    # Move last byte to front
    x = ror64(x, 8)

    # Add other half of plaintext
    x += y

    # Clear overflow
    x &= 0xffffffffffffffff

    # XOR with k (part of the key)
    x ^= k

    # Move first 3 bits to back
    y = rol64(y, 3)
	y &= 0xffffffffffffffff
    
    # XOR changed x to it
    y ^= x
    
    return x, y

'''
    Calculate the k of 
        xNew, yNew = r(xOld, yOld, k) 
'''
def calcK(xNew, xOld, yOld):
    xOld = ror64(xOld, 8)
    xOld += yOld
    xOld &= 0xffffffffffffffff
    k = xNew ^ xOld

    return k

'''
    Calculate the xNew of
        xNew, yNew = r(xOld, yOld, k) 
'''
def calcXNew(yOld, yNew):
    yOld = rol64(yOld, 3)
    yOld &= 0xffffffffffffffff
    x = yNew ^ yOld
    
    return x

'''
    Reverses the effect of r()
'''
def revR(x, y, k):
    y ^= x
    y = ror64(y, 3)
    y &= 0xffffffffffffffff
    x ^= k
    x -= y
    x = rol64(x, 8)
    x &= 0xffffffffffffffff
    return x, y

'''
    Reverse encrypt to get back the key

    Input: 	List of all x's and y's of the 
			intermediate iterations of encrypt_ref
	Output:	Original key
'''
def rev_encrypt_ref(xList, yList):
    xPlain, yPlain = xList[31], yList[31]
    xEnc, yEnc = xList[32], yList[32]
    
    bEnc = calcK(xEnc, xPlain, yPlain)

    for i in reversed(range(31)):
        xEnc, yEnc = xPlain, yPlain
        xPlain, yPlain = xList[i], yList[i]
        bPlain = calcK(xEnc, xPlain, yPlain)

        aEnc = calcXNew(bPlain, bEnc)

        aPlain, bPlain = revR(aEnc, bEnc, i)
        bEnc = bPlain

    return struct.pack('<2Q', bPlain, aPlain)

def encrypt_ref(pt, k, debug = False):
    # Interpret the plaintext and the key as two unsigned long long
    y, x = struct.unpack('<2Q', pt)
    b, a = struct.unpack('<2Q', k)

    '''
        Apply r() multiple times. To both the key and the plaintext.
        If we had x, y from before and after an application of r()
        we could easily calculate the k from 
        xNew, yNew = r(xOld, yOld, k)
    '''

    if debug:
    	print("x, y = {}, {}".format(hex(x),hex(y)))

    x, y = r(x, y, b)

    for i in range(31):
    	if debug:
        	print("x, y = {}, {}".format(hex(x),hex(y)))

        a, b = r(a, b, i)
        x, y = r(x, y, b)
    
    return struct.pack('<2Q',y, x)

'''
    Call two encryption methods, "encrypt_ref()" and "encrypt()".
    The goal is that they create the same ciphertext.
    Interestingly, "encrypt" does not use the "key" that you provide
    instead it uses the gigantic table from above.
'''
def challenge():
	'''
		Commented out, because it goes faster.
		also you calculate the key and the pt
		is irrelevant, so you can choose a good
		fixed one like all \x00
	'''
	# pt = input('plaintext: ')
	# key = input('key: ')
	# if len(pt) != 16 or len(key) != 16:
	#      print('Expecting 16 bytes inputs')
	#      return
	# ptBytes = bytes(pt, 'utf-8')

	# Choose fixed pt
    ptBytes = b'\x00'*16

    # Call encrypt to get the list with all
    # intermediate values of x and y
    ct2, xList, yList = encrypt(ptBytes)

    print("Recovered the following key: ")
    keyBytes = rev_encrypt_ref(xList, yList)
    key = str(keyBytes, 'utf-8')
    print(key)

    ct1 = encrypt_ref(ptBytes, bytes(key, 'utf-8'))

    if ct1 == ct2:
        print ("Congratulations ! use", key, "as flag")
    else:
        print ("Please try again !")
if __name__ == '__main__':
    challenge()

```

## Solution 2
I actually have another solution which I could't get to work before the first solution. I had the right characters, but they were mixed up and only after I saw the flag using the first solution I could fix the two indices that were off (only two and I wasted so much time...).
Anyways I quickly present that solution, because it is shorter and nicer in my opinion.

We exploit that we can decide which plaintext we encrypt and also look what values x and y have after the first iteration of `encrypt()` and not only at the end.
The idea is to use all zero bytes as input. Remember the core function `r()`:

```python
def r(x, y, k):
	x = ror64(x, 8)
	x += y
	x &= 0xffffffffffffffff
	x ^= k
	y = rol64(y, 3)
	y &= 0xffffffffffffffff
	y ^= x
	return x, y
```

If `x = 0` and `y = 0` then `x += y` is also zero, so `x ^= k` is actually just `k`, which is half the key.
The only problem is that `encrypt()` does that a bit different, as already described in detail above. 
In `encrypt()` after the first iteration, `x` is only part of `k`. The second part is added in the first loop of the next iteration. To get that, we need to execute the first loop. But this loop also XORs the distraction value (lets say `D`) that is removed in the second loop. So instead of executing the first loop of the second iteration also on all zero bytes, we execute it with values `D` for all x's. This way the distraction XOR cancels out and what remains is the second part of the key.
We have to be careful though, because the first loop already does the `ror64()` shifting, we must take that into account when combining the parts of the key. This gives us half the key, the first `b` from 
```python
def encrypt_ref(pt, k):
	y, x = struct.unpack('<2Q', pt)
	b, a = struct.unpack('<2Q', k)

	x, y = r(x, y, b)
	for i in range(31):
		a, b = r(a, b, i)
		x, y = r(x, y, b)

	return struct.pack('<2Q',y, x)
```

Since `a` is only used to encrypt the key and therefore actually never appears in `encrypt()` (because the keys of each step are hardcoded in the table) we calculate the next `b` and then use the functions from the previous solutions to recover `a`.

The masterplan is this:
- Recover first `b` of the key
- Recover `b'` of `a', b' = r(a, b, 0)`
- With `b`, `b'` recover `a'`
- With `revR()` recover `a, b = revR(a', b', 0)`
- `b, a` is the key! 

This solution looks like this (unshortened [here](./assets/wb-sol2.py)):
```python
#!/usr/bin/env python3

import base64
import struct
import zlib
import pickle

data = # [I left away 13590 lines of data for gigantic table here]

'''
    The table has the dimension: 
    tables[0] :: 32 x 16 x 16 x 256
    tables[1] :: 32 x 131072
    tables[2] :: 32 x 16 x 16 x 256
'''
tables = pickle.loads(zlib.decompress(base64.decodestring(data)))

'''
    helper function to convert encrypt list to encrypt_ref longs
'''
def convXY(state):
    ct = bytes(state[8:]+state[:8])
    y, x = struct.unpack('<2Q', ct)

    return x, y

def encrypt_fst_loop(i, state):
    if i == 0:
        state = state[8:] + state[:8]

    r = 0
    x2 = [0] * 16
    for j in range(16):
        s = 0
        for k in range(16):
            s ^= tables[0][i][j][k][state[k]]
        x2[j] = s
    state = x2

    return state

def encrypt_1_it(i, state):
    if i == 0:
        state = state[8:] + state[:8]

    r = 0
    x2 = [0] * 16
    for j in range(16):
        s = 0
        for k in range(16):
            s ^= tables[0][i][j][k][state[k]]
        x2[j] = s
    state = x2

    for j in range(8):
        a = tables[1][i][state[j] * 512 + state[j+8] * 2 + r]
        r = (a & 0x100) >> 8
        state[j] = a & 0xff

    x2 = [0] * 16
    for j in range(16):
        s = 0
        for k in range(16):
            s ^= tables[2][i][j][k][state[k]]
        x2[j] = s
    state = x2

    return state

def encrypt(pt):
	state = pt[8:] + pt[:8]

	for i in range(32):
		r = 0
		x2 = [0] * 16
		for j in range(16):
			s = 0
			for k in range(16):
				s ^= tables[0][i][j][k][state[k]]
			x2[j] = s
		state = x2

		for j in range(8):
			a = tables[1][i][state[j] * 512 + state[j+8] * 2 + r]
			r = (a & 0x100) >> 8
			state[j] = a & 0xff


		x2 = [0] * 16
		for j in range(16):
			s = 0
			for k in range(16):
				s ^= tables[2][i][j][k][state[k]]
			x2[j] = s
		state = x2
	return bytes(state[8:]+state[:8])

'''
    Put the lowest (little endian) r bits to the front. E.g.
    XX....XYY..Y is transformed to 
    YY..YXX....X
    for r Y's and 64-r X's, Y's are put to the front
'''
def ror64(x, r):
	return (x >> r) | (x << (64-r)) & 0xffffffffffffffff

'''
    Put the highest r bits (little endian) to the back. E.g.
    YY..YXX....X is transformed to 
    XX....XYY..Y
    for r Y's and 64-r X's, again Y's are moved.
'''
def rol64(x, r):
	return (x << r) | (x >> (64-r)) & 0xffffffffffffffff

'''
    Calculate the xNew of
        xNew, yNew = r(xOld, yOld, k) 
'''
def calcXNew(yOld, yNew):
    yOld = rol64(yOld, 3)
    yOld &= 0xffffffffffffffff
    x = yNew ^ yOld
    
    return x

'''
    Reverses the effect of r().
'''
def revR(x, y, k):
    y ^= x
    y = ror64(y, 3)
    y &= 0xffffffffffffffff
    x ^= k
    x -= y
    x = rol64(x, 8)
    x &= 0xffffffffffffffff
    return x, y

def r(x, y, k):
	x = ror64(x, 8)
	x += y
	x &= 0xffffffffffffffff
	x ^= k
	y = rol64(y, 3)
	y &= 0xffffffffffffffff
	y ^= x
	return x, y

def encrypt_ref(pt, k):
	y, x = struct.unpack('<2Q', pt)
	b, a = struct.unpack('<2Q', k)

	x, y = r(x, y, b)
	for i in range(31):
		a, b = r(a, b, i)
		x, y = r(x, y, b)

	return struct.pack('<2Q',y, x)

def challenge():
    ptBytes = bytes([0]*16)

    '''
            The key is distributed over two iterations. 
    In the fist iteration, the x's are xored with some value (part1 
    of the key). Then that is xored to the y's for the new y's.
    Then in the next iteration, before doing anything else, we
    xor again stuff to the x's (part 2 of the key). As well as to the y's,
    which is necessary, since we xored the y's with x's that weren't "finished".
    It's also confusing, since the x's are first shifted (ror64), before xoring,
    but it all works out, in the end of the 2nd loop in the 2nd iteration, the 
    x's are x + y of the second iteration of r().

    Masterplan:
        - Recover first b of the key
        - Recover b' of a', b' = r(a, b, 0)
        - With b, b' recover a'
        - With revR recover a, b = revR(a', b', 0)
        - b, a is the key! 
    '''

    # Run encryption on all zero bytes -> gives you part of b
    # The other part is hidden at the start of the next iteration
    # XORed together they give the b of the first key.

    encZeros = encrypt_1_it(0, b'\x00'*16)
    b1_part1 = encZeros[:8]

    # Execute only the first loop to get the rest of the key.
    # Execute on [157, ..., 157, 0, ..., 0] because all x's
    # are xored with 157 (for later ops)
    b1_part2 = encrypt_fst_loop(1, [157]*8 + [0]*8)

    # XOR the two parts togethers. Don't forget ror64(8, x)
    # i.e. that b1_part1[0] is shifted to the end, so the
    # XOR is skewed (like it is done below)
    # Pay attention to assign the value to the right position
    # in b1.
    b1 = [0]*8
    for i in range(8):
        b1[(i+1)%8] = b1_part1[(i+1)%8] ^ b1_part2[i]

    # Run the second loop iteration the input that makes
    # x+y zero again. This can be done the simplest by using
    # b1_part2 for the x's and for the y's xor b1_part2 with 157
    # then after the first loop, the state will be [157,..., 157]
    # which gives an addition of 0 --> after the 3rd loop, the
    # x's are again the first part of b2
    zeros2 = [0]*16
    for i in range(16):
        if(i < 8):
            zeros2[i] = b1_part2[(i-1)%8]
        else:
            zeros2[i] = b1_part2[i] ^ 157

    encZeros2 = encrypt_1_it(1, zeros2)
    b2_part1 = encZeros2[:8]

    # For the second part of b2 proceed as before for b1
    b2_part2 = encrypt_fst_loop(2, [127]*8 + [0]*8)

    b2 = [0]*8
    for i in range(8):
        b2[(i+1)%8] = b2_part1[(i+1)%8] ^ b2_part2[i]

	# Calculate a2 from a2, b2 = r(a1, b1, 0) first,
	# then recover a1.
    b2, b1 = struct.unpack('<2Q', bytes(b2 + b1))
    a2 = calcXNew(b1, b2)
    a1, b1 = revR(a2, b2, 0)

	# The key is b1, a1 (was switched in encrypt_ref)
    key = str(struct.pack('<2Q', b1, a1), 'utf-8')

    ct1 = encrypt_ref(ptBytes, bytes(key, 'utf-8'))
    ct2 = encrypt(ptBytes)

    if ct1 == ct2:
        print ("Congratulations ! use", key, "as flag")
    else:
        print ("Please try again !")


if __name__ == '__main__':
    challenge()
```
