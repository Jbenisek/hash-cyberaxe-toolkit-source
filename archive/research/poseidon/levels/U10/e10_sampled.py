"""U10: sampled collision ratios at q=65537 (v2=16) and q=1000003 (v2=1), 2e7 random inputs, r=1,2, Cauchy and non-Cauchy."""
import numpy as np, time
from toylib import *
T0=time.time()
rng=np.random.default_rng(11)
def sample(q,r,cau,N=20_000_000,chunk=4_000_000,seed=1):
    t=Toy(q,seed,cauchy=cau)
    k0=[];k01=[];k012=[]
    for _ in range(N//chunk):
        nk=rng.integers(0,q,chunk,dtype=np.int64); rho=rng.integers(0,q,chunk,dtype=np.int64)
        s=t.perm([nk,rho,np.full(chunk,t.cap,dtype=np.int64)],r)
        k0.append(s[0]); k01.append(s[0]*q+s[1]); k012.append((s[0]*q+s[1])*q+s[2])
        # also keep input keys for distinctness
    out={}
    for name,k,space in (("l0",np.concatenate(k0),q),("l0l1",np.concatenate(k01),q*q),("full",np.concatenate(k012),q**3)):
        u,c=np.unique(k,return_counts=True)
        pr=float((c*(c-1)//2).sum()); ex=N*(N-1)/2/space
        out[name]=(pr,ex)
    return out
for q in (65537,1000003):
    for r in (1,2):
        for cau in (True,False):
            o=sample(q,r,cau)
            print(f"q={q} v2={v2(q-1)} r={r} cauchy={cau}: "+" | ".join(f"{k}: pairs {v[0]:.0f} expected {v[1]:.1f} ratio {v[0]/v[1]:.3f}" for k,v in o.items())+f" [{time.time()-T0:.0f}s]",flush=True)
