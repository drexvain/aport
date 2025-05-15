#    aport
aport is a fast and simple tcp port scanner built with python. it allows you to scan an ip address or url to find open ports. the scanner is multithreaded, customizable, and easy to use.
# how to use it ? 
```options:
  -h, --help            show this help message and exit
  -ip IP                target ip address
  -url URL              target url (auto resolves ip)
  -p, --ports PORTS     port range to scan ex: 1-65535
  -t, --threads THREADS
                        number of threads (default 100)
  --timeout TIMEOUT     socket timeout (default 0.5s)
  --banner              try to extract service banner
  --top TOP             scan a random number of ports ex: --top 100
  --common              scan most common ports
  --os                  show user's detected os
  --verbose             soon
```

 #usage exemples
 ```python aport.py -ip 192.168.1.1
python aport.py -url https://example.com --top 100
python aport.py -ip 10.0.0.1 -p 1-65535 --banner --threads 200```

