import numpy as np, sys
from b3 import *
from collections import Counter
np.seterr(all='ignore')
rng=np.random.default_rng(2)
def modefreq(df, mask=None):
    # df: (k,N) uint32 -> most common column & count
    if mask is not None: df=df[:,mask]
    n=df.shape[1]
    if n==0: return None,0,0
    key=np.ascontiguousarray(df.T)
    v=key.view(np.dtype((np.void,key.dtype.itemsize*key.shape[1]))).ravel()
    u,idx,cnt=np.unique(v,return_index=True,return_counts=True)
    j=cnt.argmax(); return df[:,idx[j]],cnt[j],n
def trial(diff,N,mode='xor'):
    base=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
    alt=[b.copy() for b in base]
    for w,dl in diff.items():
        alt[w]= base[w]^M(dl) if mode=='xor' else base[w]+M(dl)
    s1=[];s2=[]
    compress(base,3,64,11,N,s1); compress(alt,3,64,11,N,s2)
    st=[np.stack([s1[r][i]^s2[r][i] for i in range(16)]) for r in range(3)]
    dg=np.stack([(s1[2][i]^s1[2][i+8])^(s2[2][i]^s2[2][i+8]) for i in range(8)])
    return st,dg
def analyze(diff,N=1<<15):
    st,dg=trial(diff,N)
    d0,c0,_=modefreq(st[0])
    m0=(st[0]==d0[:,None]).all(0)
    d1,c1,n1=modefreq(st[1],m0)
    m1=m0.copy(); m1[m0]=(st[1][:,m0]==d1[:,None]).all(0)
    d2,c2,n2=modefreq(st[2],m1)
    _,cd,_=modefreq(dg)
    return c0/N, c1/max(n1,1), c2/max(n2,1), cd/N, n1, int(m1.sum())
if __name__=="__main__":
    rows=[]
    for w in range(16):
        for b in range(32):
            r=analyze({w:1<<b}); rows.append((w,b)+r)
    rows.sort(key=lambda t:-(t[2]*t[3]))
    print("single-bit xor: word,bit,p0,p1|0,p2|01,pdigest,n1,n2")
    for t in rows[:12]: print(t)
    import pickle; pickle.dump(rows,open('exp2.pkl','wb'))
