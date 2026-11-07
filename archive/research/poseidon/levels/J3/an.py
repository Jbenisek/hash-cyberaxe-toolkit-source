import json,sys,math
f=sys.argv[1]; d=json.load(open(f)); N2=None
print(f, 'p lanes:'); 
for i in range(3): print(i,[round(x*d['q'],3) for x in d['p%d'%i]],'(p*q)')
rows=[]
for k,(c,e) in d['cells'].items():
    lane,s=k.split('|'); n=s.count(',')+1
    z=(c-e)/math.sqrt(max(e,1e-9)) if e>=1 else None
    rows.append((lane,s,n,c,e,z))
print('single:'); [print(r[0],r[1],r[3],round(r[4],1)) for r in rows if r[2]==1]
bad=[r for r in rows if r[2]>=2 and ((r[5] is not None and abs(r[5])>5) or (r[4]<0.5 and r[3]>=3) )]
bad.sort(key=lambda r:-abs(r[5] or 99))
print('non-random cells (|z|>5 where E>=1, or E<0.5 and obs>=3):',len(bad))
for r in bad[:60]: print(r[0],r[1],'obs',r[3],'exp',round(r[4],2),'z',None if r[5] is None else round(r[5],1))
print('total pair-cells n>=2:',sum(1 for r in rows if r[2]>=2),' with E>=1:',sum(1 for r in rows if r[2]>=2 and r[4]>=1))
