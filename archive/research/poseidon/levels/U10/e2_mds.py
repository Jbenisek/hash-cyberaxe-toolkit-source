"""U10 Q2 + Q6: Cauchy vs non-Cauchy MDS; fibre stats; pair counts (lane0), (lane0,lane1) etc.
ratio = collision pairs / random-function expectation. full-state distinct count (X1)."""
import sys, time, math
import numpy as np
from toylib import *
T0=time.time()
def allstats(t,r,upto=None):
    q=t.q; N=q*q
    h0=np.zeros(q,np.int64); h01=np.zeros(q*q,np.int32); h02=np.zeros(q*q,np.int32); h12=np.zeros(q*q,np.int32)
    hfull=set() if q<=1009 else None; allkeys=[]
    for NK,RHO,s in t.run_all(r,upto):
        h0+=np.bincount(s[0],minlength=q)
        h01+=np.bincount(s[0]*q+s[1],minlength=q*q).astype(np.int32)
        h02+=np.bincount(s[0]*q+s[2],minlength=q*q).astype(np.int32)
        h12+=np.bincount(s[1]*q+s[2],minlength=q*q).astype(np.int32)
        if q<=1009: allkeys.append((s[0]*q+s[1])*q+s[2])
    out={}
    out['l0']=stat(h0,N,q)
    p01=pairs(h01); out['p01']=(p01,p01/(N*(N-1)/2/q**2))
    p02=pairs(h02); out['p02']=(p02,p02/(N*(N-1)/2/q**2))
    p12=pairs(h12); out['p12']=(p12,p12/(N*(N-1)/2/q**2))
    if allkeys:
        k=np.concatenate(allkeys); out['fulldistinct']=(len(np.unique(k)),N)
    else:
        out['fulldistinct']=None
    return out
def fmt(o):
    s=f"l0:pairs={o['l0'][0]:.0f} ratio={o['l0'][1]:.4f} var/mean={o['l0'][2]:.3f} img={o['l0'][3]} | p01 {o['p01'][0]:.0f} ({o['p01'][1]:.3f}) p02 {o['p02'][0]:.0f} ({o['p02'][1]:.3f}) p12 {o['p12'][0]:.0f} ({o['p12'][1]:.3f})"
    if o['fulldistinct']: s+=f" | full distinct {o['fulldistinct'][0]}/{o['fulldistinct'][1]}"
    return s
cfg=[(257,range(1,7),(0,1,2,3)),(769,range(1,5),(1,2)),(1009,range(1,5),(1,2)),(4099,range(1,3),(1,2))]
summ={}
for q,seeds,rs in cfg:
    for r in rs:
        for cau in (True,False):
            for sd in seeds:
                t=Toy(q,sd,cauchy=cau)
                assert is_cauchy(t.M,q)==cau and is_mds(t.M,q)
                o=allstats(t,r)
                print(f"q={q} r={r} cauchy={cau} seed={sd}: "+fmt(o),f"[{time.time()-T0:.0f}s]",flush=True)
                summ.setdefault((q,r,cau),[]).append(o)
print("\nSUMMARY mean +- spread of ratio(l0), var/mean, p01 ratio, p12 ratio")
for (q,r,cau),L in summ.items():
    a=lambda f:np.array([f(o) for o in L])
    for name,f in (("l0ratio",lambda o:o['l0'][1]),("var/mean",lambda o:o['l0'][2]),("p01",lambda o:o['p01'][1]),("p02",lambda o:o['p02'][1]),("p12",lambda o:o['p12'][1])):
        x=a(f); print(f"q={q} r={r} cauchy={cau} {name}: mean {x.mean():.4f} sd {x.std():.4f} min {x.min():.4f} max {x.max():.4f}")
# X6 trail check on toys (r=2): d=(0,M02,-M01): lane0 equal after R4.M and R5.M? and non-cauchy
print("\nX6 trail vector check (toy exhaustive on states):")
for q in (257,1009):
  for cau in (True,False):
    t=Toy(q,3,cauchy=cau); M=t.M; d=(0,M[0][2],(-M[0][1])%q)
    # push many random states s and s+d through R4 then R5: lane 0 of second state input difference
    import random; rnd=random.Random(5); good=0;n=2000
    for _ in range(n):
        s=[rnd.randrange(q) for _ in range(3)]; s2=[(s[i]+d[i])%q for i in range(3)]
        # one partial round: input lane0 equal -> w equal -> out diff = M(0,d1,d2); check lane0 diff 0
        def pr(s,idx):
            s=[(s[i]+t.RC[idx][i])%q for i in range(3)]; s[0]=pow(s[0],5,q)
            return [sum(M[i][j]*s[j] for j in range(3))%q for i in range(3)]
        a=pr(s,4);b=pr(s2,4)
        if a[0]==b[0]:
            a2=pr(a,5);b2=pr(b,5)
            diff=[(b[i]-a[i])%q for i in range(3)]
            if (a2[0]-b2[0])%q==0 and diff==[0*0, (M[0][2]*M[1][1]-M[0][1]*M[1][2])%q, 0][:0] or True: good+=1 if (a2[0]-b2[0])%q==0 else 0
    print(f"q={q} cauchy={cau}: states where two partial rounds keep lane0 diff 0 along trail vector: {good}/{n}")
