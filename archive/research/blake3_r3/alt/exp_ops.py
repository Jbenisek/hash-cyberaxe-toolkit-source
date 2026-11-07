import random, json, itertools
from opcount import *
M=0xFFFFFFFF
def rol(x,n): return ((x<<n)|(x>>(32-n)))&M
def ror(x,n): return ((x>>n)|(x<<(32-n)))&M
base=trace()[0]; print("base",base)
out={}
# (A) flags/blen/counter scan, zero prefix, cv=IV
res={}
for fl in range(16):
    for bl in range(0,65):
        for ctr in (0,1,2,3,255,2**32,2**40+5):
            res[(fl,bl,ctr)]=trace(flags=fl,blen=bl,ctr=ctr)[0]
vals=sorted(set(res.values())); print("A all (flags,blen,ctr) combos",len(res),"op counts seen",vals)
leg=[k for k in res if k[2]==0 and k[0] in (11,10) and 1<=k[1]<=64]
print("A legal single-chunk root (flags 11 or 10, blen1..64, ctr0):",len(leg),"min ops",min(res[k] for k in leg),"max",max(res[k] for k in leg))
print("A flags 12 (PARENT|ROOT) blen64 ctr0:",res[(12,64,0)])
best=min(res,key=res.get); print("A best anywhere (illegal included):",best,res[best])
out["A"]=dict(n=len(res),vals=vals,legal_min=min(res[k] for k in leg),legal_max=max(res[k] for k in leg),flags12=res[(12,64,0)],best=[best,res[best]])
# (B) multi-block: random cv (fixed first-block output), zero m0..7
random.seed(7)
rb=[trace(cv=tuple(random.getrandbits(32) for _ in range(8)),flags=10)[0] for _ in range(300)]
print("B random cv, flags10, zero msg prefix: ops min/max",min(rb),max(rb)); out["B"]=[min(rb),max(rb)]
# (C) nonzero constant m0..7 (random): cost
rc=[trace(mconst=tuple(random.getrandbits(32) for _ in range(8)))[0] for _ in range(300)]
print("C random nonzero m0..7: min/max",min(rc),max(rc)); out["C"]=[min(rc),max(rc)]
# (D) constructed prefix zeroing post-column c' and d' words (8 immediates), per column count
def construct(cols):
    mc=[0]*8
    for i in cols:
        a,b,c=IV[i],IV[i+4],IV[i]; d=[0,0,64,11][i]
        d1=(-c)&M; a1=rol(d1,16)^d; x=(a1-a-b)&M; b1=ror(b^0,12); a2=d1; y=(a2-a1-b1)&M
        mc[2*i]=x; mc[2*i+1]=y
    return tuple(mc)
def col_scalar(mc):
    v=list(IV)+list(IV[:4])+[0,0,64,11]
    for j,(a,b,c,d) in enumerate(GCALLS[:4]):
        x,y=mc[2*j],mc[2*j+1]
        v[a]=(v[a]+v[b]+x)&M; v[d]=ror(v[d]^v[a],16); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],12)
        v[a]=(v[a]+v[b]+y)&M; v[d]=ror(v[d]^v[a],8); v[c]=(v[c]+v[d])&M; v[b]=ror(v[b]^v[c],7)
    return v
mc=construct(range(4)); v=col_scalar(mc); print("D post-column v8..15:",[hex(t) for t in v[8:]])
print("D ops with all 4 columns constructed:",trace(mconst=mc)[0])
for cols in [(0,),(0,1),(0,1,2),(0,1,2,3)]:
    print("D cols",cols,"ops",trace(mconst=construct(cols))[0])
out["D"]={str(c):trace(mconst=construct(c))[0] for c in [(0,),(0,1),(0,1,2),(0,1,2,3)]}
# (E) two-compress chains: chunk (flags3, ctr1) then parent (flags12, left cv L)
chunk=trace(flags=3,ctr=1)[0]; par0=trace(flags=12,ctr=0)[0]
parL=[trace(flags=12,mconst=tuple(random.getrandbits(32) for _ in range(8)))[0] for _ in range(100)]
print("E chunk compress",chunk,"parent L=0",par0,"parent L random min/max",min(parL),max(parL))
import math
for name,tot in (("L=0",chunk+par0),("L random min",chunk+min(parL)),("L random max",chunk+max(parL))):
    print("E",name,"total",tot,"delta time_log2 vs 595 (main loop share 0.9944): %.4f"%(math.log2(tot/595)))
out["E"]=dict(chunk=chunk,par0=par0,parL=[min(parL),max(parL)])
json.dump(out,open("exp_ops.json","w"))
