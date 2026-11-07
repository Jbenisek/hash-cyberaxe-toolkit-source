"""U10 Q4: scan all capacity values at q=257 (r=1,2) and q=769 (r=1)."""
import time, numpy as np
from toylib import *
T0=time.time()
def run(q,r,seed,caps):
    base=Toy(q,seed); res=[]
    for cap in caps:
        t=Toy(q,seed,cap=cap)
        cnt=keycounts(t,r,lambda s:s[0],q)
        cnt3=keycounts(t,r,lambda s:s[0],q,upto=4)
        res.append((cap,)+stat(cnt,q*q,q)+stat(cnt3,q*q,q)[1:3])
    return base,res
for q,r,seed in ((257,1,1),(257,2,1),(257,1,2),(769,1,1)):
    base,res=run(q,r,seed,range(q))
    ratios=np.array([x[2] for x in res]); vm=np.array([x[3] for x in res]); img=np.array([x[4] for x in res])
    r3=np.array([x[5] for x in res])
    print(f"q={q} r={r} seed={seed}: caps scanned {len(res)}; coll-ratio min {ratios.min():.4f} max {ratios.max():.4f} mean {ratios.mean():.4f} sd {ratios.std():.4f}; var/mean min {vm.min():.3f} max {vm.max():.3f}; image size min {img.min()} max {img.max()}; after-R3 lane0 ratio min {r3.min():.4f} max {r3.max():.4f}  [{time.time()-T0:.0f}s]")
    special={'K=0 (cap=-c02)':(-base.RC[0][2])%q,'cap=0':0,'cap=1':1,'cap=-1':q-1,'cap=2^65 mod q':pow(2,65,q),
             'a=cap+c02=1':(1-base.RC[0][2])%q,'a=-1':(-1-base.RC[0][2])%q}
    for nme,c in special.items():
        x=res[c]; print(f"   {nme}: cap={c} ratio={x[2]:.4f} var/mean={x[3]:.3f} image={x[4]} after-R3 ratio={x[5]:.4f}")
    worst=sorted(res,key=lambda x:-abs(x[2]-1))[:3]
    print("   largest |ratio-1| caps:",[(w[0],round(w[2],4)) for w in worst],flush=True)
