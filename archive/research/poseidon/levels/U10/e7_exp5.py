"""U10 Q7: gcd(5,q-1)=5. Full-state collisions and image-size progression, vs gcd=1 control primes."""
import numpy as np, math, time
from toylib import *
def run(q,seed,r):
    t=Toy(q,seed) if True else None
    N=q*q; M=t.M; RC=t.RC
    s=[np.repeat(np.arange(q,dtype=np.int64),q),np.tile(np.arange(q,dtype=np.int64),q),np.full(N,t.cap,dtype=np.int64)]
    sizes=[]
    for idx,full in t.sched(r):
        s=[(s[i]+RC[idx][i])%q for i in range(3)]
        for i in (range(3) if full else range(1)):
            x2=s[i]*s[i]%q;x4=x2*x2%q;s[i]=x4*s[i]%q
        s=[(M[i][0]*s[0]+M[i][1]*s[1]+M[i][2]*s[2])%q for i in range(3)]
        sizes.append(len(np.unique((s[0]*q+s[1])*q+s[2])))
    key=(s[0]*q+s[1])*q+s[2]
    u,c=np.unique(key,return_counts=True)
    pairs_full=float((c*(c-1)//2).sum())
    p0=pairs(np.bincount(s[0],minlength=q))
    return sizes,len(u),pairs_full,p0
print("per prime: distinct full states / q^2, colliding full-state pairs (random fn q^2->q^3 would give ~q/2), lane0 pair ratio, image sizes after each round")
for q in (11,31,41,61,71,101,131,151,181,191,211,1051, 13,17,19,23,29,37,43,47,53,59,67,73,79,83,89,97,103,107,109,113,127,137,139,1009):
    if not is_prime(q): continue
    g=math.gcd(5,q-1)
    for r in (1,2):
        for seed in (1,2):
            sizes,d,pf,p0=run(q,seed,r)
            ratio=p0/((q*q)*(q*q-1)/2/q)
            print(f"q={q} g={g} r={r} s={seed}: distinct {d}/{q*q} full-pairs {pf:.0f} (rand {q/2:.1f}) lane0 ratio {ratio:.3f} sizes {sizes}",flush=True)
