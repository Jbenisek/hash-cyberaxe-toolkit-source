#!/usr/bin/env python3
# fix_pins.py OUTDIR XML...: for every row r that pin_screen flags, free the E row r-4 (the only register that can cancel a
# W difference at step r when A rows r-4..r-1 and E rows r-3..r-1 stay zero). Repeats until the screen passes. Writes OUTDIR/<name>_fx.xml.
import re,sys,os
out=sys.argv[1]; os.makedirs(out,exist_ok=True)
pat=re.compile(r"(\s*(-?\d+) A: )(\S+)( E: )(\S+)( W: )(\S+)(.*)")
zero=lambda s:set(s)<=set("-01"); nz=lambda s:bool(set(s)&set("xunXUN"))
for f in sys.argv[2:]:
    L=open(f,errors="ignore").read().split("\n"); idx={}
    for i,ln in enumerate(L):
        m=pat.match(ln)
        if m: idx[int(m.group(2))]=i
    freed=[]
    while True:
        rows={r:pat.match(L[i]).groups() for r,i in idx.items()}
        bad=[r for r,g in rows.items() if nz(g[6]) and r>=4 and all(k in rows and zero(rows[k][2]) and zero(rows[k][4]) for k in range(r-4,r+1))]
        if not bad: break
        r=min(bad); k=r-4; g=list(rows[k]); g[4]="?"*len(g[4]); L[idx[k]]=g[0]+g[2]+g[3]+g[4]+g[5]+g[6]+g[7]; freed.append(k)
    name=os.path.basename(f)[:-4]+"_fx.xml"; open(os.path.join(out,name),"w").write("\n".join(L))
    print("freed E rows %s\t%s"%(freed,name))
