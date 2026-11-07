import itertools, json, time
from b3h import *
rng=np.random.default_rng(20261012)
def scan(sets,gen,N):
    best_eq=0;best_hw=999;per=[]
    for D in sets:
        m=rand_words(rng,N,range(8,16)) if max(D)<16 and False else None
    return
def run(domain,sizes,delta_kind,N=4096):
    sets=[c for s in sizes for c in itertools.combinations(domain,s)]
    maxeq=0;minhw=999;argmin=None
    for D in sets:
        m=rand_words(rng,N,range(8,16)) if domain[0]==8 else rand_words(rng,N)
        m2=m.copy()
        for w in D:
            if delta_kind=="rand": m2[w]=m[w]^rng.integers(1,2**32,N,dtype=np.uint64).astype(np.uint32)
            elif delta_kind=="msb": m2[w]=m[w]^np.uint32(0x80000000)
            elif delta_kind=="add1": m2[w]=m[w]+np.uint32(1)
            elif delta_kind=="sub1": m2[w]=m[w]-np.uint32(1)
            elif delta_kind=="add_msb": m2[w]=m[w]+np.uint32(0x80000000)
            elif delta_kind=="add_2^16": m2[w]=m[w]+np.uint32(1<<16)
            elif delta_kind=="bit7": m2[w]=m[w]^np.uint32(1<<7)
            elif delta_kind=="bit12": m2[w]=m[w]^np.uint32(1<<12)
        d=compress(m,rounds=3); d2=compress(m2,rounds=3)
        x=d^d2; eq=(x==0).sum(axis=0).max(); h=hw(x).sum(axis=0)
        maxeq=max(maxeq,int(eq))
        if h.min()<minhw: minhw=int(h.min()); argmin=D
    return dict(nsets=len(sets),N=N,max_equal_words=maxeq,min_digest_hw=minhw,argmin=argmin,total=len(sets)*N)
out={}
t=time.time()
# baseline: random pairs, same total as the biggest scan
tot=696*4096
dd=[];
for _ in range(tot//65536):
    m=rand_words(rng,65536);m2=rand_words(rng,65536)
    dd.append(hw(compress(m)^compress(m2)).sum(axis=0).min())
out["baseline_random_pairs"]=dict(total=tot,min_digest_hw=int(min(dd)))
for dom,name in ((list(range(8,16)),"restricted m8..15"),(list(range(16)),"full 16 words")):
    for kind in ("rand","msb"):
        r=run(dom,(1,2,3),kind); out[f"Q2 {name} {kind} |D|<=3"]=r; print(name,kind,r,round(time.time()-t))
# Q4 additive / sparse alternatives, |D|<=2, restricted domain
for kind in ("add1","sub1","add_msb","add_2^16","bit7","bit12"):
    r=run(list(range(8,16)),(1,2),kind,N=1<<14); out[f"Q4 restricted {kind} |D|<=2"]=r; print(kind,r,round(time.time()-t))
json.dump(out,open("exp_diff.json","w"),default=str,indent=1)
