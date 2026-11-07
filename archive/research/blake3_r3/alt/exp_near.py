import json, time, math
from b3h import *
rng=np.random.default_rng(31)
t=time.time(); out={}
N=1<<18
def rcv(n): return rng.integers(0,2**32,(8,n),dtype=np.uint64).astype(np.uint32)
base_min=[]
for _ in range(32):
    a=rcv(N);m=rand_words(rng,N);b=rcv(N);m2=rand_words(rng,N)
    base_min.append(int(hw(compress(m,a,0,64,10)^compress(m2,b,0,64,10)).sum(axis=0).min()))
out["baseline_min_hw_over_%d"%(32*N)]=min(base_min); print("baseline random pairs min HW over",32*N,":",min(base_min))
# (i) same block, cv differs in word j
res={}
for kind in ("rand","bit31"):
    for j in range(8):
        mn=999;eq=0
        for _ in range(8):
            cv=rcv(N); cv2=cv.copy()
            cv2[j]^= rng.integers(1,2**32,N,dtype=np.uint64).astype(np.uint32) if kind=="rand" else U(0x80000000)
            m=rand_words(rng,N)
            x=compress(m,cv,0,64,10)^compress(m,cv2,0,64,10)
            mn=min(mn,int(hw(x).sum(axis=0).min())); eq=max(eq,int((x==0).sum(axis=0).max()))
        res[f"{kind}_j{j}"]=(mn,eq)
    print("(i) same block, cv word j differs,",kind,{k:v for k,v in res.items() if k.startswith(kind)})
out["i"]=res
# (ii) cv differs in word j AND block differs in one word w (random delta)
res2={}; mn_all=999
for j in (0,3,4,7):
    for w in (0,5,8,12,15):
        cv=rcv(N); cv2=cv.copy(); cv2[j]^=rng.integers(1,2**32,N,dtype=np.uint64).astype(np.uint32)
        m=rand_words(rng,N); m2=m.copy(); m2[w]^=rng.integers(1,2**32,N,dtype=np.uint64).astype(np.uint32)
        x=compress(m,cv,0,64,10)^compress(m2,cv2,0,64,10)
        res2[f"j{j}_w{w}"]=(int(hw(x).sum(axis=0).min()),int((x==0).sum(axis=0).max()))
print("(ii)",res2); out["ii"]=res2
# exact stage-A count: evaluations for near-collision in >=7 of 8 words (any one word may differ)
n=math.log2(math.sqrt(2*2**224/8)); out["stageA_log2_evals"]=n; print("stage A log2 evals (birthday, one word free of 8):",n)
json.dump(out,open("exp_near.json","w"),default=str)
print(round(time.time()-t))
