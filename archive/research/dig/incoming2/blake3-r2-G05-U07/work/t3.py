import json,random
from lines import *
t=json.load(open('lines_table.json'))
T={tuple(r[0]):(r[1],r[2],r[3]) for r in t}
for k in [('b',),('flags',),('b','flags'),('t_lo',),('t_hi',),('t_lo','t_hi'),('t_lo','t_hi','b','flags'),('t_lo','b'),('t_hi','b','flags','t_lo')]:
    k=tuple(sorted(k,key=lambda x:['t_lo','t_hi','b','flags','h0','h1','h2','h3'].index(x))); print(k,T.get(k))
hs=[r for r in t if all(x.startswith('h') for x in r[0])]
print('h-only subsets',len(hs),set((r[2],r[3]) for r in hs))
print('min k over all',min(r[2] for r in t),'count k4',sum(r[2]==4 for r in t),'k8',sum(r[2]==8 for r in t))
print('k=8 subsets sample',[r[0] for r in t if r[2]==8][:6])
# invertibility: pair(alt,host,m')==m
random.seed(3); bad=0
for _ in range(100000):
    sub=random.sample(['t_lo','t_hi','b','flags','h0','h1','h2','h3'],random.randrange(1,9))
    host=([R() for _ in range(8)],R(),R(),random.randrange(65),random.choice([1,3,11])); alt=alt_host(host,sub)
    m=[R() for _ in range(16)]; m2=pair(host,alt,m); back=pair(alt,host,m2)
    bad+= (back!=m)
print('involution failures',bad,'of 100000')
# row-b difference: after matching a1 and d1 via mx shift, is b1 equal? (one-step algebra check)
bad=0
for _ in range(20000):
    h=[R() for _ in range(8)]; h2=list(h); h2[4]=(h[4]+R()+1)&M
    m=[R() for _ in range(16)]
    v=init(h,m,0,0,64,1); v2=init(h2,m,0,0,64,1)
    a1=(v[0]+v[4]+m[0])&M; mx2=(a1-v2[0]-v2[4])&M
    w=list(v); w2=list(v2); G(w,0,4,8,12,m[0],m[1]); G(w2,0,4,8,12,mx2,(m[1])&M)
    bad+= (w[4]!=w2[4])
print('row-b diff: b output differs after a1-fix',bad,'of 20000')
