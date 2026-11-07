import sys,json,time; sys.path.insert(0,'.')
import numpy as np
from kk6 import *
rng=np.random.default_rng(9)
NB=64; L0=leader_state(rng,NB)
def f(zm,r):
    L=L0.copy(); L[4]^=np.uint64(zm); L[14]^=np.uint64(zm); return perm(L,r)
F0={r:f(0,r) for r in (2,3)}
def rv(w):
    v=0
    for b in rng.choice(32,size=w,replace=False): v|=1<<int(b)
    return v
tot={2:0,3:0}; passes={2:0,3:0}; n=0; t0=time.time()
while time.time()-t0<60:
    u=rv(int(rng.integers(1,9))); v=rv(int(rng.integers(1,9)))
    if u==v or u==0 or v==0: continue
    n+=1
    for r in (2,3):
        d=f(u^v,r)^f(u,r)^f(v,r)^F0[r]
        ok=(~d.any(axis=0)); tot[r]+=NB; passes[r]+=int(ok.sum())
print("random z-space pairs tested:",n,"x",NB,"bases")
for r in (2,3): print(f" {r} rounds: pair-on-base passes {passes[r]}/{tot[r]}")
json.dump(dict(pairs=n,bases=NB,passes2=passes[2],passes3=passes[3],total=tot[2]),open('t5b_out.json','w'))
