NewConfigParser
===============

An extension to the ConfigParser module in python standard library. This extension allows shell-style back-referencing for resolving dependant variable names in the config file. 

Extends the ConfigParser.SafeConfigParser class from python standard library, for providing additional features like - 
	1. define-anywhere-use-anywhere freedom while defining dependant options
	2. caching of resolved options
	3. any amount of depth in dependancies (only restricted by recursion limi)
	4. detection of circular dependancies
	5. same coding semantics as ConfigParser.SafeConfigParser
	6. no section specification resolves into current section


More Info
=========

Blog: http://pyarabola.blogspot.in


Examples
========
```
shreyas@tochukasui:~/devel/python$ cat config.ini
[server]
host = blogspot
tld = in
subdomain = pyarabola
website = ${subdomain}.${host}.${tld}
protocol = http
url = ${protocol}://${website}

[request]
request_type = get
request = ${request_type} ${server.url}
form_request = falseshreyas@tochukasui:~/devel/python$ 

shreyas@tochukasui:~/devel/python$ python
Python 2.7.3 (default, Aug  1 2012, 05:16:07) 
[GCC 4.6.3] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> from newconfigparser import SafeConfigParser as NewSafeConfigParser
>>> from ConfigParser import SafeConfigParser
>>> newparser = NewSafeConfigParser()
>>> origparser = SafeConfigParser()
>>> newparser.read("config.ini")
['config.ini']
>>> origparser.read("config.ini")
['config.ini']

>>> newparser.get("request", "request_type")
'get'
>>> origparser.get("request", "request_type")
'get'

>>> newparser.get("request", "request");
'get http://pyarabola.blogspot.in'
>>> origparser.get("request", "request");
'${request_type} ${server.url}'

>>> newparser.get("server", "url");
'http://pyarabola.blogspot.in'
>>> origparser.get("server", "url");
'${protocol}://${website}'

>>> origparser.get("server", "protocol");
'http'

>>> origparser.get("server", "website");
'${subdomain}.${host}.${tld}'
>>> newparser.get("server", "website");
'pyarabola.blogspot.in'
>>> 
```

Circular Dependancy Detection 
============================
```
shreyas@tochukasui:~/devel/python$ cat circdep.ini
[humans]
drinking_water = ${govt.pipeline}

[animals]
drinking_water = ${natural.reservoire}

[govt]
pipeline = ${natural.reservoire}

[natural]
reservoire = ${river}
river = ${heavens.rains}

[heavens]
rains = ${clouds}
clouds = ${vapor}
vapor = ${natural.reservoire}
</quote>
</div>
```
```python
shreyas@tochukasui:~/devel/python$ cat cdep.py
#!/usr/bin/python

import newconfigparser

p = newconfigparser.SafeConfigParser()
p.read("circdep.ini")

try: 
    p.get("humans", "drinking_water")
except Exception as e:
    print e

shreyas@tochukasui:~/devel/python$ ./cdep.py
Cicrular dependancy detected while resolving parameter 'natural.reservoire': natural.reservoire -> natural.river -> heavens.rains -> heavens.clouds -> heavens.vapor -> natural.reservoire
shreyas@tochukasui:~/devel/python$ 
```

