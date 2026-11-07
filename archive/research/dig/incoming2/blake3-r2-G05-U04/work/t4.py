import random, json, collections
from b3 import *
random.seed(77)
K3=(IV[3]+IV[7])&M
res={}
for f2 in (10,12,9,3,15):
    act=collections.Counter(); N=1000
    for _ in range(N):
        w=[random.getrandbits(32) for _ in range(16)]
        a1=(K3+w[6])&M; a1p=a1^11^f2; w2=list(w); w2[6]=(a1p-K3)&M; w2[7]=(w[7]+w[6]-w2[6])&M
        t1=[];t2=[]; run(IV,w,0,64,11,2,t1); run(IV,w2,0,64,f2,2,t2)
        r1=[t for t in t1 if t[0]==1]; r2=[t for t in t2 if t[0]==1]
        assert all(r1[k][2:6]==r2[k][2:6] for k in range(4))
        act[sum(1 for k in range(8) if r1[k]!=r2[k])]+=1
    res[f2]=dict(delta=11^f2,active_hist=dict(act))
print(res); json.dump(res,open('t4_out.json','w'))
