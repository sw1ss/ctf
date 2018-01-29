# random to win (Crypto)
Author: MH

In this challenge I had to break an encryption based on modular arithmetics.

## Challenge description and material
The text was simply:
> Download in: [Link](https://drive.google.com/open?id=176uh1IgyA8Kt5Mt4JKyAdFNPyFjVDWU8)
> Service: nc random2win.acebear.site 33337

### The service
When we connect to the service, we see the following:
```text
********************Menu********************
* 1 - Test                                 *
* 2 - Submit                               *
********************************************
Your choice:
```
When we choose `1`, we can send two messages, and get their cipher text back. After two messages the connection is closed.
```text
Your choice: 1
Message: some message
Ciphertext: 1564552006508669667564127612034763595999452081288572539869892029772571219426403885663317190197278165781496601557944708701
Message: another message
Ciphertext: 1564552006508669667564127612034763595999452081288572539869892029772571219426403885663823082852239469818512019448463306333
```

When we choose `2`, we are presented with a cipher text. We are expected to answer with the clear text, if it is not correct, the connection is closed immediately. 
```text 
Your choice: 2
Ciphertext: 996660017562247680971542590546880209061115949188248581803031239449227981297561093703132462444965218158391992414010827685
test123
```

### The code
Fortunately the download contains the full code of the server (except `h`, `p` and `flag`). It's even prepared to run locally, which was nice, because it was very convenient to test the attack locally.
The functions `test` and `submit` are where the important stuff happens.
```python
import os
import socket
import threading
from hashlib import *
import SocketServer
import random
from Secret import flag, p, h
host, port = '0.0.0.0', 33337
BUFF_SIZE = 1024
assert len(str(p)) == 121

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    allow_reuse_address = True

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def test(self):
        r = random.randint(0,222222)
        i = 2
        while i>0:
            self.request.sendall("Message: ")
            m = self.request.recv(BUFF_SIZE).strip()
            m = int(m.encode('hex'),16)            
            c = (r*h+m)%p
            self.request.sendall("Ciphertext: %s\n" %c)
            i -=1
        
        
    def submit(self):
        m = random.randint(10**10,10**12)
        r = random.randint(10**10,10**12)
        c = (r*h+m)%p
        print m, r
        self.request.sendall("Ciphertext: %s\n" %c)
        x = self.request.recv(BUFF_SIZE).strip()
        if(m == int(x)):
            self.request.sendall(flag)

    def view(self):
        while True:
            self.request.sendall("********************Menu********************\n")
            self.request.sendall("* 1 - Test                                 *\n")
            self.request.sendall("* 2 - Submit                               *\n")
            self.request.sendall("********************************************\n")
            self.request.sendall("Your choice: ")
            try:
                choice = int(self.request.recv(BUFF_SIZE).strip())
            except:
                choice = 0
            if choice == 1:
                self.test()
                break
            elif choice == 2:
                self.submit()
                break
            else:
                self.request.sendall("Invalid choice!\n")
	   
    def handle(self):
        self.request.settimeout(10)        
        self.view()
    

def main():
	server = ThreadedTCPServer((host, port), ThreadedTCPRequestHandler)
	server_thread = threading.Thread(target=server.serve_forever)
	server_thread.daemon = True
	server_thread.start()
	print "Server loop running in thread:", server_thread.name
	server_thread.join()

if __name__=='__main__':
    main()
```

## Solution
### Master plan
My master plan to solve this challenge was to recover `h` and `p` with the `test` option of the service and then use that knowledge to decrypt the cipher text of the `submit` option. I didn't know in advance how to solve those steps, but it meets the eye that in the `test` function, the random number `r` is in the range `[0, 222222]` which seems "bruteforceable". Also we can submit two messages for the same `r`. And `h` and `p` are constant for all requests. Therefore I was pretty sure that we must calculate them first.

### Step 1: Calculate `p`
First one needs to notice on line 10 of the provided code `assert len(str(p)) == 121`, i.e. `p` has 121 digits.
In general this step is about the following part of the provided code:
```python
def test(self):
    r = random.randint(0,222222)
    i = 2
    while i>0:
        self.request.sendall("Message: ")
        m = self.request.recv(BUFF_SIZE).strip()
        m = int(m.encode('hex'),16)            
        c = (r*h+m)%p
        self.request.sendall("Ciphertext: %s\n" %c)
        i -=1
```
Since we can send two messages for the same random `r`, we know that `r*h` is the same for both messages we send, while we can control the offset `m`. We also know `c`.
To take advantage of that, I derived the following:
```text
c1 = (r*h + m1) % p
c2 = (r*h + m2) % p
=> c1 - c2 = (r*h + m1) % p - (r*h + m2) % p
```
Using the modulo rule `(a - b) % p <=> (a % p - b % p) % p` backwards:
```text
(c1 - c2) % p = ((r*h + m1) % p - (r*h + m2) % p) % p
(c1 - c2) % p = ((r*h + m1) - (r*h + m2)) % p
(c1 - c2) % p = (m1 - m2) % p
```
That means that gives us a condition (`(c1 - c2) % p = (m1 - m2) % p`) that the correct `p` will fulfill for every two messages `m1`, `m2` we send.

Since we know that `p` has `121` digits, the idea was basically to start with `10**120` as the first guess for `p`. Then I choose `m1` and `m2` in a way, that we have a wrap around, i.e. that `c2 < c1`. The reason for that intuitive decision was, that in that case, the modulo `p` has an effect, while with two numbers `m1,m2 < p` it doesn't and so that condition holds whenever `(c1 - c2) % p` is the same as the difference of the two messages. To be precise, I chose `m1 = 0, m2 = 10**120`. Since I don't know what `p` is, I had to check in a loop that `c2 < c1`, slightly modifying `m2` every iteration (but it also depends on which random number `r` is chosen, so multiple tries have a good chance to be successful). 
Then if `c2 < c1` I changed `p` the following way, so that this condition is fulfilled. (I'm not sure if it is possible to miss the right `p` this way, but it worked locally as well as on their server)
```python
while diffM != diffC:
	p += abs(diffM - diffC)
```
So the full code for this part was:
```python
lower = 0
upper = 10**120
p = 10**120
reCheck = 0
maxCheck = 1

def toStr(i):
    asStr = hex(i)[2:]
    if len(asStr) % 2 == 1:
        asStr = '0' + asStr

    return asStr.decode('hex')

while True:
    rem = remote(ip, 33337)
    rem.recvuntil('Your choice: ')
    rem.sendline('1')
	
    rem.recvuntil('Message:')
    rem.sendline(toStr(lower))
    rem.recvuntil('Ciphertext: ')
    c1 = int(rem.recvline())
	
    rem.recvuntil('Message: ')
    rem.sendline(toStr(upper))
    rem.recvuntil('Ciphertext: ')
    c2 = int(rem.recvline())

    rem.close()

    if c2 < c1:
        diffC = (c1 - c2) % p
        diffM = (lower - upper) % p

        if reCheck > 0 and diffM == diffC:
            reCheck += 1
        else:
            reCheck = 1
            while diffM != diffC:
                p += abs(diffM - diffC)
                if(len(str(p)) > 121):
                    p = 10**120

                diffC = (c1 - c2) % p
                diffM = (lower - upper) % p
     
        if(reCheck == maxCheck):
            break
        upper += 1
```
Which gave me the following number `p`:
`2129236650498506197214865121017813676962270980934541379925587741818174020229784960110052122450619093813474017151250421361`

### Step 2: Calculate `h`
My plan here was to send the message `0` multiple times (only once for the same `r`, because they are identical anyways). This gives me equations of the form:

`c = (r * h) % p`

Where we don't know either `r` or `h`. But we know that `r` is in the range `[0, 222222]`, so we bruteforce every `r` and check with other tries (which have different `r`, but must have the same `h`!), until only one choice of `h` remains. That was very fast, since `p` is so large and `h` was significantly smaller, there were seldom more than 3 tries necessary.
For a fixed `r = r1`, we can calculate 

`c = (r1 * h) % p`

simply by computing the modular inverse using the extended euclidean algorithm `rInv = modinv(r, p)`, and then computing:

`h = (c * rInv) % p`

This is done in the following code:
```python
maxRandInteger = 222222

def getC():
    rem = remote(ip, 33337)
    rem.recvuntil('Your choice: ')
    rem.sendline('1')
	
    rem.recvuntil('Message:')
    rem.sendline(toStr(0))
    rem.recvuntil('Ciphertext: ')
    c = int(rem.recvline())
    
    rem.close()
    return c

# functions to calculat modular inverse

def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m

def gcd_iter(u, v):
    while v:
        u, v = v, u % v
    return abs(u)

# init first list of possible (h, r) pairs
print('\t- Make first list of possible pairs (h,r)')
c = getC()
possibleHs = []
possibleRs = []
for i in range(0,maxRandInteger+1):
    if(gcd_iter(i,p) == 1):
        inv = modinv(i,p)
        h = (c * inv) % p
        possibleHs.append(h)
        possibleRs.append(i)

# sort out pairs until only the right one is left

print('\t- Reduce list of pairs (h,r) to one')
while len(possibleHs) > 1:
    possibleHsNew = list()
    possibleRsNew = list()
    c = getC()
        
    for r in possibleRs:
        inv = modinv(r,p)
        hNew = (c * inv) % p

        possibleHsNew.append(hNew)
        possibleRsNew.append(r)

	# This takes the intersection of the two lists
    possibleHs = list(set(possibleHs) & set(possibleHsNew))
    possibleRs = list(set(possibleRs) & set(possibleRsNew))

if len(possibleHs) > 1:
    print('Still %d possible pairs...' % len(possibleHs))
    exit(-1)
elif len(possibleHs) == 0:
    print('No pairs left, error')
    exit(-1)

h = possibleHs.pop()
```

That gave me the following `h`:
`11305546770736405378819894875529407145124231011999396912086973074056791191623579252993880901245430834195596982773094`

### Step 3: Finally calculate `m`
Now we can finally worry about breaking the encryption of the `submit` part. Remember that that looked like the following:
```python
def submit(self):
	 m = random.randint(10**10,10**12)
	 r = random.randint(10**10,10**12)
	 c = (r*h+m)%p
	 print m, r
	 self.request.sendall("Ciphertext: %s\n" %c)
	 x = self.request.recv(BUFF_SIZE).strip()
	 if(m == int(x)):
	     self.request.sendall(flag)
```
Now the problem here is, that `m` as well as `r` are random. Also their range is now `[10**10, 10**12]` and we only have one equation:

`c = (r * h + m) % p`

Where we know know `c, h, p`.

To calculate that, I used the following derivations:
```test
c = (r * h + m) % p
c + n * p = (r * h + m) for some n
So taking mod h on both sides:
(c + n * p) % h = (r * h + m) % h = m % h = m
```
Where we know `m % h = m`, because `m <= 10**12 < h`. Since `h << p`, and `r` is not so big either, we hope that `n` is not so big, and start with the initial guess:
`m = c % h`
And then add `p` until `m` is in the range `[10**10, 10**12]`. That works good, because the range `[10**10, 10**12]` is quite small compared to the size of `p`.

This I realized in the following code:
```python
rem = remote(ip, 33337)
rem.recvuntil('Your choice: ')
rem.sendline('2')
	
rem.recvuntil('Ciphertext: ')
cEnc = int(rem.recvline())

# reverse encryption
m = cEnc % h
while m < 10**10 or m > 10**12:
    m = (m + p) % h

print('Recovered m: %d' % m)
# send solution, get flag
rem.sendline(str(m))
print(rem.recvuntil('}'))
```

Together this solves the challenge and gives the flag: 

> AceBear{r4nd0m_is_fun_in_my_g4m3}

The full code of my solution is:
```python
#!/usr/bin/python2

from pwn import *

#ip = '0.0.0.0'
ip = 'random2win.acebear.site'

print('Calculate prim number')
lower = 0
upper = 10**120
p = 10**120
reCheck = 0
maxCheck = 1

def toStr(i):
    asStr = hex(i)[2:]
    if len(asStr) % 2 == 1:
        asStr = '0' + asStr

    return asStr.decode('hex')

while True:
    rem = remote(ip, 33337)
    rem.recvuntil('Your choice: ')
    rem.sendline('1')
	
    rem.recvuntil('Message:')
    rem.sendline(toStr(lower))
    rem.recvuntil('Ciphertext: ')
    c1 = int(rem.recvline())
	
    rem.recvuntil('Message: ')
    rem.sendline(toStr(upper))
    rem.recvuntil('Ciphertext: ')
    c2 = int(rem.recvline())

    rem.close()

    if c2 < c1:
        diffC = (c1 - c2) % p
        diffM = (lower - upper) % p

        if reCheck > 0 and diffM == diffC:
            reCheck += 1
        else:
            reCheck = 1
            while diffM != diffC:
                p += abs(diffM - diffC)
                if(len(str(p)) > 121):
                    p = 10**120

                diffC = (c1 - c2) % p
                diffM = (lower - upper) % p
     
        if(reCheck == maxCheck):
            break
        upper += 1

print('Recovered prim: %d' % p)
print('-'*50)

print('\nRecover h')

# Plan: get a c for c = (hr + 0)%p
# then use the extended eucledean algo to calculate modular inverses
# and solve the equations c = (hr)%p for all possible r's
# check with other products c, to get the right pair (h,r)
maxRandInteger = 222222

def getC():
    rem = remote(ip, 33337)
    rem.recvuntil('Your choice: ')
    rem.sendline('1')
	
    rem.recvuntil('Message:')
    rem.sendline(toStr(0))
    rem.recvuntil('Ciphertext: ')
    c = int(rem.recvline())
    
    rem.close()
    return c

# functions to calculate modular inverse

def extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)

def modinv(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise ValueError
    return x % m

def gcd_iter(u, v):
    while v:
        u, v = v, u % v
    return abs(u)

# init first list of possible (h, r) pairs
print('\t- Make first list of possible pairs (h,r)')
c = getC()
possibleHs = []
possibleRs = []
for i in range(0,maxRandInteger+1):
    if(gcd_iter(i,p) == 1):
        inv = modinv(i,p)
        h = (c * inv) % p
        possibleHs.append(h)
        possibleRs.append(i)

# sort out pairs until only the right one is left

print('\t- Reduce list of pairs (h,r) to one')
while len(possibleHs) > 1:
    possibleHsNew = list()
    possibleRsNew = list()
    c = getC()
        
    for r in possibleRs:
        inv = modinv(r,p)
        hNew = (c * inv) % p

        possibleHsNew.append(hNew)
        possibleRsNew.append(r)

    # This takes the intersection of the two lists
    possibleHs = list(set(possibleHs) & set(possibleHsNew))
    possibleRs = list(set(possibleRs) & set(possibleRsNew))

if len(possibleHs) > 1:
    print('Still %d possible pairs...' % len(possibleHs))
    exit(-1)
elif len(possibleHs) == 0:
    print('No pairs left, error')
    exit(-1)

h = possibleHs.pop()

print('Recovered h: %d' % h)
print('-'*50)
print('\nNow crack their encryption')

rem = remote(ip, 33337)
rem.recvuntil('Your choice: ')
rem.sendline('2')
	
rem.recvuntil('Ciphertext: ')
cEnc = int(rem.recvline())

# reverse encryption
m = cEnc % h
while m < 10**10 or m > 10**12:
    m = (m + p) % h

print('Recovered m: %d' % m)
# send solution, get flag
rem.sendline(str(m))
print(rem.recvuntil('}'))
```
