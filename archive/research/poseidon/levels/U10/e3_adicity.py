"""U10 Q3: 2-adicity high vs low. S-box layer fixed points, x->x^5 cycle structure, fibre differences."""
import time, math, numpy as np
from toylib import *
T0=time.time()
print("q, v2(q-1), q mod 4, #x with x^5=x, fixed triples of S layer, #cycles of x->x^5 on F_q^*, max cycle len, cycle len spectrum (len:count)")
for q in (257,769,12289,65537,1009,4099,1000003):
    x=np.arange(q,dtype=np.int64); y=x*x%q; y=y*y%q*x%q
    fp=int((y==x).sum())
    seen=np.zeros(q,bool); spec={}
    f=y
    for s0 in range(1,q):
        if seen[s0]: continue
        c=0;z=s0
        while not seen[z]:
            seen[z]=True; z=int(f[z]); c+=1
        spec[c]=spec.get(c,0)+1
    print(q,v2(q-1),q%4,fp,fp**3,sum(spec.values()),max(spec),dict(sorted(spec.items())),flush=True)
print("\nFibre differences (r=1): pairs of inputs in the same lane-0 fibre; unordered difference multiplicity vs shuffled-output null")
def diffstats(q,seed,r,shuffle,rng):
    t=Toy(q,seed)
    outs=[]
    for NK,RHO,s in t.run_all(r): outs.append(s[0])
    y=np.concatenate(outs)
    if shuffle: y=rng.permutation(y)
    order=np.argsort(y,kind='stable'); ys=y[order]
    cuts=np.flatnonzero(np.diff(ys))+1; groups=np.split(order,cuts)
    D=np.zeros(q*q,np.int32)
    for g in groups:
        n=len(g)
        if n<2: continue
        gn=g//q; gr=g%q
        i,j=np.triu_indices(n,1)
        dn=(gn[j]-gn[i])%q; dr=(gr[j]-gr[i])%q
        k1=dn*q+dr; k2=((q-dn)%q)*q+(q-dr)%q
        D+=np.bincount(np.minimum(k1,k2),minlength=q*q).astype(np.int32)
    tot=int(D.sum()); mx=int(D.max())
    Dm=D.reshape(q,q)
    axis=int(Dm[0,:].sum()+Dm[:,0].sum()-D[0])
    return tot,mx,int((D>0).sum()),axis
rng=np.random.default_rng(7)
for q in (257,769,1009,4099):
  for seed in (1,2):
    for r in (1,):
        real=diffstats(q,seed,r,False,rng)
        null=diffstats(q,seed,r,True,rng)
        print(f"q={q} seed={seed} r={r} v2={v2(q-1)}: REAL pairs={real[0]} max-multiplicity={real[1]} distinct diffs={real[2]} axis-aligned pairs={real[3]} || NULL pairs={null[0]} max={null[1]} distinct={null[2]} axis={null[3]}  [{time.time()-T0:.0f}s]",flush=True)
