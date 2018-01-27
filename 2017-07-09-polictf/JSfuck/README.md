# JSfuck (Grab Bag 117)
Author: jokker

> I was writing some valid ECMAScript to print your flag but my fingers slipped and I added several unwanted characters. Could you please fix it for me?

We get a challenge.js in which the code is obfuscated with [jsfuck.com](https://www.jsfuck.com) and additionally has some typos in it, so it can't be run.

```
[][(![]+[])[+[]]+([![]]+[][[]])[+!+[]+[+[]]]+(![]+[])[!+[]+!+[]]+(!![]+[])[+[]]+(!![]+[])[!+[]+!+[]+!+[]]+(!![]+[])[+!+[]]][([][(![]+[])
...
```

There are some obvious types, a '"' and a '{', which have both nothing to do with JSfuck, so we delete them. Sadly, there are more typos in the code, which aren't that easy to find.

So to find the typos and make the code run we can first replace all findings with there corresponding char ([JSfuck on GitHub](https://github.com/aemkei/jsfuck/blob/master/jsfuck.js)).

```
[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](a+l+e+r+t+(+"+f+l+a+(+![]+[![]]+([]+[])[c+(!![]+[][f+i+l+t+e+r])[+]!+[]+[+[]]]+n+s+t+r+u+c+t+o+r])[!+[]+!+[]+[+[]]]+{+I+ +f+[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](r+e+t+u+r+n+ +u+n+e+s+c+a+(+(!+[]+!+[]+[+!+[]]+[+!+[]]))[t+(!![]+[][f+i+(![]+[])[!+[]+!+[[]]+t+e+r])[+!+[]+[+[]]]+(+![]+([]+[])[c+o+n+s+t+r+u+c+t+o+r])[+!+[]+[+[]]]+t+r+i+n+g](!+[]+!+[]+!+[]+[+!+[]])[+!+[]]+e)()(%+[!+[]+!+[]]+a)+*+[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](r+e+t+u+r+n+ +u)+n+e+s+c+a+p+e)()(%+[!+[]+!+[]]+a)+e+d+ +m+y+ +b+r+a+i+n+ +s+o+ +h+a+r+d+ +i+ +e+n+j+o+y+e+d+ +i+t+}+([]+[])[f+o+n+t+c+o+l+(!![]+[][f+([![]]]+[][[]])[+!+[]+[+[]]]+l+t+e+r])[+!+[]+[+[]]]+r]()[+!+[]+[!+[]+!+[]]]+))()
```

Well, we already see a good portion of the text, but we need to do some more manual work to get the flag.

Let's focus on the different spots which fail to convert. Let's begin with this one at the end of the code:

```
[f+([![]]]+[][[]])[+!+[]+[+[]]]+l+t+e+r]
```

This must be an 'i', so we check what it should look like when obfuscated with JSfuck (don't forget to turn eval off on JSfuck).

```
in code:   ([![]]]+[][[]])[+!+[]+[+[]]]
on jsfuck: ([![]]+[][[]])[+!+[]+[+[]]]
```

There we have it, there's an additional ']', so we get rid of that. Let's see what the conversion looks like now.

```
[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](a+l+e+r+t+(+"+f+l+a+(+![]+[![]]+([]+[])[c+(!![]+[][f+i+l+t+e+r])[+]!+[]+[+[]]]+n+s+t+r+u+c+t+o+r])[!+[]+!+[]+[+[]]]+{+I+ +f+[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](r+e+t+u+r+n+ +u+n+e+s+c+a+(+(!+[]+!+[]+[+!+[]]+[+!+[]]))[t+(!![]+[][f+i+(![]+[])[!+[]+!+[[]]+t+e+r])[+!+[]+[+[]]]+(+![]+([]+[])[c+o+n+s+t+r+u+c+t+o+r])[+!+[]+[+[]]]+t+r+i+n+g](!+[]+!+[]+!+[]+[+!+[]])[+!+[]]+e)()(%+[!+[]+!+[]]+a)+*+[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](r+e+t+u+r+n+ +u)+n+e+s+c+a+p+e)()(%+[!+[]+!+[]]+a)+e+d+ +m+y+ +b+r+a+i+n+ +s+o+ +h+a+r+d+ +i+ +e+n+j+o+y+e+d+ +i+t+}+"+))()
```

As we can see, this fixed 'i' leaded to an nice representation of a '"' at the end. So we continue this procedure to find all typos in the code. This are the spots which need to be fixed additionally.

```
[+]!+[]+[+[]]]         # typo in o
(![]+[])[!+[]+!+[[]]   # typo in l
```

This gives us the almost correct code.

```
[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](a+l+e+r+t+(+"+f+l+a+g+{+I+ +f+*+*+[][f+i+l+t+e+r][c+o+n+s+t+r+u+c+t+o+r](r+e+t+u+r+n+ +u)+n+e+s+c+a+p+e)()(%+[!+[]+!+[]]+a)+e+d+ +m+y+ +b+r+a+i+n+ +s+o+ +h+a+r+d+ +i+ +e+n+j+o+y+e+d+ +i+t+}+"+))()
```

As the attentive reader can see, there's an additional ')' after "return u", which doesn't belong there. So to find this last typo in the original code, one can obfuscate this 'u' with JSfuck and add an additional ')' to it and search for that.

Now that all typos are fixed, the code can be executed and gives us the flag:

**flag{I f\*\*\*ed my brain so hard i enjoyed it}**