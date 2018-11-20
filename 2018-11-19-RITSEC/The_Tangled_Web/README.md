# Description
```
fun.ritsec.club:8007

Author: jok3r
```
The website was made out of multiple HTML files, which were linking to each other, completely tangled like a big bowl of spaghetti. 

# Solution
To find the flag I downloaded all those pages using httrack (a website copier) and then went through the source code of those files manually.

Stars.html contained the following base64 string, which gave the flag.
```
UklUU0VDe0FSM19ZMFVfRjMzNzFOR18xVF9OMFdfTVJfS1I0QjU/IX0=
```
```
RITSEC{AR3_Y0U_F3371NG_1T_N0W_MR_KR4B5?!} 
```

