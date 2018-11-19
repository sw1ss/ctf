# Music.png 300

## Description

```
Name that tune

Author: 1cysw0rdk0 and oneNutW0nder
```
This challenge was updated during the ctf.  
I solved the initial one featuring music.txt.  
Later on it was changed to music.png. 

## Solution

Upon opening music.txt I found this:

```
(t<<3)*[8/9,1,9/8,6/5,4/3,3/2,0]
[[0xd2d2c7,0xce4087,0xca32c7,0x8e4008]
[t>>14&3.1]>>(0x3dbe4687>>((t>>10&15)>9?18:t>>10&15)*3&7.1)*3&7.1]

Wrap your answer in RS{}
```

When searching only for the first line "(t<<3)*[8/9,1,9/8,6/5,4/3,3/2,0]" I found https://gist.github.com/djcsdy/2875542.
It describes that the code is so called "Music SoftSynth", so I searched for an interpreter.

I found this one: http://wry.me/bytebeat/

When entering the code it played "Never Gonna Give You Up - Rick Astley".

Flag: RITSEC{never_gonna_give_you_up}
