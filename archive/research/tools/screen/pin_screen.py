#!/usr/bin/env python3
# pin_screen.py XML...: flags ladder start files that are impossible by construction: a row r whose W difference is
# definitely nonzero (x/u/n) while A and E rows r-4..r are all '-' (zero state difference around a nonzero W difference cannot hold).
import re,sys
for f in sys.argv[1:]:
    rows={}
    for ln in open(f,errors="ignore"):
        m=re.match(r"\s*(-?\d+) A: (\S+) E: (\S+) W: (\S+)",ln)
        if m: rows[int(m.group(1))]=(m.group(2),m.group(3),m.group(4))
    zero=lambda s:set(s)<=set("-01"); nz=lambda s:bool(set(s)&set("xunXUN"))
    bad=[r for r,(a,e,w) in rows.items() if nz(w) and r>=4 and all(k in rows and zero(rows[k][0]) and zero(rows[k][1]) for k in range(r-4,r+1))]
    print(("IMPOSSIBLE rows %s"%bad if bad else "ok")+"\t"+f.split("/")[-1])
