#!/usr/bin/env python3
"""Appends/replaces a Pareto-row section in ../COVERAGE.md (markers). Re-run after coverage.py."""
import json,re,collections,os
H=os.path.dirname(os.path.abspath(__file__));D=os.path.dirname(H)
B,E='<!-- PARETO-COVERAGE BEGIN -->','<!-- PARETO-COVERAGE END -->'
recs=[json.loads(l) for l in open(os.path.join(D,'CELLS.jsonl'),encoding='utf-8') if l.strip()]
fam=collections.defaultdict(dict)
for r in recs:
    m=re.match(r'PR-(poseidon-generic|poseidon-algebraic|blake3|sha256|sha3)-r(\d+)-Q(\d+)$',r['id'])
    if m: fam[m.group(1)][(int(m.group(2)),int(m.group(3)))]=r['status']
mk=lambda st:'.' if st=='OPEN' else ('X' if st=='EXCLUDED' else 'S')
out=[B,'','## Pareto-row sites (merged 2026-10-17; ids PR-<family>-r<R>-Q<n>)','','Marks: S scanned, X excluded, . unscanned (OPEN).','']
tot=[0,0,0,0]
for f,cells in fam.items():
    qs=sorted({q for _,q in cells});rows=sorted({r for r,_ in cells})
    out+=['### pareto-%s'%f,'','| question | universe | scanned | excluded | unscanned |','|---|---|---|---|---|']
    T=[0,0,0,0]
    for q in qs:
        v=[mk(st) for (r,qq),st in cells.items() if qq==q]
        u,s_,x,d=len(v),v.count('S'),v.count('X'),v.count('.')
        out.append('| Q%d | %d | %d | %d | %d |'%(q,u,s_,x,d))
        for i,z in enumerate((u,s_,x,d)):T[i]+=z
    out.append('| **all** | %d | %d | %d | %d |'%tuple(T))
    for i in range(4):tot[i]+=T[i]
    out+=['','Per-row state (%s; S scanned, X excluded, . unscanned):'%' '.join('Q%d'%q for q in qs),'','| row | state |','|---|---|']
    for r in rows:
        out.append('| %d | %s |'%(r,''.join(mk(cells[(r,q)]) if (r,q) in cells else '.' for q in qs)))
    out.append('')
out+=['### Pareto totals','','| universe | scanned | excluded | unscanned |','|---|---|---|---|','| %d | %d | %d | %d |'%tuple(tot),'']
out.append(E)
p=os.path.join(D,'COVERAGE.md');s=open(p,encoding='utf-8').read()
if B in s: s=s[:s.index(B)]+s[s.index(E)+len(E):]
open(p,'w',encoding='utf-8',newline='\n').write(s.rstrip('\n')+'\n\n'+'\n'.join(out)+'\n')
print('\n'.join(out))
