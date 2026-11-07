import sys,json,time; sys.path.insert(0,'.')
import numpy as np
from kk6 import *
rng=np.random.default_rng(5)
NB=512
L0=leader_state(rng,NB)
def f(zmask,rounds):
    L=L0.copy(); L[4]^=np.uint64(zmask); L[14]^=np.uint64(zmask); return perm(L,rounds)
out={}
for rounds in (2,3):
    t0=time.time()
    F0=f(0,rounds); Fi=[f(1<<i,rounds) for i in range(32)]
    ok=np.zeros((32,32,NB),bool)  # pair passes (second derivative zero) on base s
    for i in range(32):
        for j in range(i+1,32):
            d=f((1<<i)|(1<<j),rounds)^Fi[i]^Fi[j]^F0
            z=~d.any(axis=0)
            ok[i,j]=ok[j,i]=z
    pp=ok[np.triu_indices(32,1)].mean(axis=0) if False else None
    frac=np.array([[ok[i,j].mean() for j in range(32)] for i in range(32)])
    iu=np.triu_indices(32,1)
    print(f"rounds={rounds}: mean pair-pass rate over 496 pairs {frac[iu].mean():.4f}, min {frac[iu].min():.4f}, max {frac[iu].max():.4f}  ({time.time()-t0:.1f}s)")
    # per-base max clique of coordinate z-directions
    sizes=[]
    import itertools
    for s in range(NB if rounds==3 else 8):
        adj=[[bool(ok[i,j,s]) for j in range(32)] for i in range(32)]
        best=[0]
        def bk(R,P,X):
            if not P and not X:
                best[0]=max(best[0],R); return
            for v in list(P):
                bk(R+1,[u for u in P if adj[v][u]],[u for u in X if adj[v][u]])
                P.remove(v);X.append(v)
        bk(0,list(range(32)),[])
        sizes.append(best[0])
    sizes=np.array(sizes)
    hist={int(k):int((sizes==k).sum()) for k in np.unique(sizes)}
    print(f"  max coordinate-clique size per base (max z-directions jointly affine through {rounds} rounds): hist {hist}")
    out[str(rounds)]=dict(pair_pass_mean=float(frac[iu].mean()),pair_pass_min=float(frac[iu].min()),pair_pass_max=float(frac[iu].max()),clique_hist=hist,bases=NB)
json.dump(out,open('t5_3round_out.json','w'),indent=1)
