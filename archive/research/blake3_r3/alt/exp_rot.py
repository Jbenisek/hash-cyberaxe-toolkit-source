import json, math, time
from b3h import *
rng=np.random.default_rng(5)
def rotl(x,k): k=k%32; return x if k==0 else (x<<U(k))|(x>>U(32-k))
out={}
t=time.time()
N=1<<18
# Q1: actual constants. m' = rotl_k(m) on all words (prefix zeros are rotation-invariant). digest relation d(m') == rotl_k d(m)?
q1={}
init=lambda n: init_state(n)
def init_state(n,zero=False):
    return init(IV,0,64,11,n) if not zero else np.zeros((16,n),dtype=np.uint32)
from b3h import init as _init
def st(n,zero):
    return np.zeros((16,n),dtype=np.uint32) if zero else _init(IV,0,64,11,n)
def rot_test(k,zero,rounds=3,N=N,words=range(8,16)):
    m=rand_words(rng,N,words); m2=np.array([rotl(m[i],k) for i in range(16)])
    s=st(N,zero); s2=np.array([rotl(s[i],k) for i in range(16)])   # rotated initial state (what the relation needs)
    a=run_rounds(s,m,rounds); b=run_rounds(s2,m2,rounds)
    res=[]
    for r in range(rounds):
        x=b[r]^np.array([rotl(a[r][i],k) for i in range(16)])
        res.append((float((x==0).all(axis=0).mean()), float((x==0).mean()), float(hw(x).mean())))
    return res
# actual-constants variant: true state init is NOT rotated (constants are IV); relation with message rotation only
def actual(k,N=N):
    m=rand_words(rng,N,range(8,16)); m2=np.array([rotl(m[i],k) for i in range(16)])
    d=compress(m,rounds=3); d2=compress(m2,rounds=3)
    x=d2^np.array([rotl(d[i],k) for i in range(8)])
    return int((x==0).sum(axis=0).max()), float((x==0).mean()), float(hw(x).sum(axis=0).min()), float(hw(x).sum(axis=0).mean())
q1={}
for k in range(1,32):
    q1[k]=actual(k)
print("Q1 actual constants, max equal-rotated words over 2^18 samples, per k:",{k:v[0] for k,v in q1.items()}, "min HW of d'^rotl d:",min(v[2] for v in q1.values()),"mean HW ~",round(np.mean([v[3] for v in q1.values()]),1))
# init-state rotational distance exact (constants): HW(rotl_k S0 ^ S0) with S0 incl. zero message-state
S0=_init(IV,0,64,11,1)[:,0]
dist={k:int(sum(bin(int(rotl(S0[i:i+1],k)[0])^int(S0[i])).count('1') for i in range(16))) for k in range(1,32)}
print("init state rotational distance HW per k (0 would be symmetric):",dist)
out["Q1"]=dict(max_equal_words={k:v[0] for k,v in q1.items()},min_hw=min(v[2] for v in q1.values()),init_dist=dist)
# Q2: symmetric constants (all-zero state init) -> per-round full-state rotational equality
q2={}
for k in (1,2,4,8,16,24,31):
    q2[k]=rot_test(k,True,3,1<<20)
    print("Q2 zero-const k=%d"%k,[(r+1,"P(all16)=%.2e"%v[0],"frac words equal=%.3f"%v[1]) for r,v in enumerate(q2[k])])
out["Q2"]=q2
# Q3 table bits needed for digest = rotated digest: 8*(32-gcd(k,32))
out["Q3_bits_required"]={k:8*(32-math.gcd(k,32)) for k in range(1,32)}
print("Q3 min bits required over k:",min(out["Q3_bits_required"].values()),"at k=16")
# Q4: RX persistence: modal frequency of (s' ^ rotl s) per state word after round r with actual constants (state not rotated), m'=rotl m
def modal(k,N=1<<17):
    m=rand_words(rng,N,range(8,16)); m2=np.array([rotl(m[i],k) for i in range(16)])
    s=st(N,False); a=run_rounds(s,m,3); b=run_rounds(s,m2,3)
    best=[]
    for r in range(3):
        mx=0
        for i in range(16):
            x=b[r][i]^rotl(a[r][i],k)
            vals,c=np.unique(x,return_counts=True); mx=max(mx,int(c.max()))
        best.append(mx/N)
    return best
q4={k:modal(k) for k in (1,3,7,8,12,16,24,31)}
print("Q4 RX modal freq per round (max over 16 words):",q4)
out["Q4"]=q4
json.dump(out,open("exp_rot.json","w"),default=str)
print(round(time.time()-t))
