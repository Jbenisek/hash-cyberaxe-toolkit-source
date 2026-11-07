import re
from eng import *
ops,by,src,want,outs=trace(Cfg(),dce=False)
for ln in src.splitlines():
    for mm in re.finditer(r"[+^](\d{12,})", ln):
        n=int(mm.group(1))
        if n % REP==0 and n//REP not in (0,): 
            if (n//REP)!=M32: print(ln.strip()[:60], hex(n//REP))
