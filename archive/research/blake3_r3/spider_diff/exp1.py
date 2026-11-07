import numpy as np, itertools, sys, time
from b3 import *
np.seterr(all='ignore')
rng=np.random.default_rng(1)
def pop(x):
    x=x.astype(np.uint64); c=np.zeros(x.shape,dtype=np.int64)
    for i in range(32): c+=((x>>np.uint64(i))&np.uint64(1)).astype(np.int64)
    return c
def run(diffs,S,mode='xor'):
    """diffs: list of dicts {word:delta}; S samples each. returns per-diff stats."""
    D=len(diffs); N=D*S
    base=[np.tile(rng.integers(0,2**32,S,dtype=np.uint64).astype(M),D) for _ in range(16)]
    base=[rng.integers(0,2**32,N,dtype=np.uint64).astype(M) for _ in range(16)]
    alt=[b.copy() for b in base]
    for k,d in enumerate(diffs):
        for w,dl in d.items():
            sl=slice(k*S,(k+1)*S)
            if mode=='xor': alt[w][sl]=base[w][sl]^M(dl)
            else: alt[w][sl]=base[w][sl]+M(dl)
    s1=[];s2=[]
    compress(base,3,64,11,N,s1); compress(alt,3,64,11,N,s2)
    res=[]
    for r in range(3):
        df=np.stack([s1[r][i]^s2[r][i] for i in range(16)])  # 16,N
        act=(df!=0).sum(0).reshape(D,S).mean(1)
        res.append(act)
    dg=np.stack([(s1[2][i]^s1[2][i+8])^(s2[2][i]^s2[2][i+8]) for i in range(8)])
    eq=(dg==0).sum(0).reshape(D,S)
    hw=pop(dg).sum(0).reshape(D,S)
    return res,eq.mean(1),eq.max(1),hw.min(1),hw.mean(1)
if __name__=="__main__":
    S=256
    out=[]
    # single word, xor single bits, and additive +-2^b
    for mode in ('xor','add'):
        diffs=[{w:1<<b} for w in range(16) for b in range(32)]
        res,eqm,eqx,hwmin,hwmean=run(diffs,S,mode)
        for k,d in enumerate(diffs):
            out.append((mode,'1w',list(d.items())[0],res[0][k],res[1][k],res[2][k],eqm[k],eqx[k],hwmin[k],hwmean[k]))
    # two words: all 120 pairs, bits in {0,1,7,8,12,16,24,31} x same set, xor
    bits=[0,1,7,8,12,16,24,31]
    diffs=[{a:1<<x,b:1<<y} for a in range(16) for b in range(a+1,16) for x in bits for y in bits]
    for i in range(0,len(diffs),2000):
        ch=diffs[i:i+2000]
        res,eqm,eqx,hwmin,hwmean=run(ch,64,'xor')
        for k,d in enumerate(ch):
            out.append(('xor','2w',tuple(d.items()),res[0][k],res[1][k],res[2][k],eqm[k],eqx[k],hwmin[k],hwmean[k]))
    import pickle; pickle.dump(out,open('exp1.pkl','wb'))
    for name,key in (('min active after r0',3),('min active after r1',4),('min active after r2',5)):
        o=sorted(out,key=lambda t:t[key])[:6]; print(name); [print(' ',t) for t in o]
    print('best digest eq max'); [print(' ',t) for t in sorted(out,key=lambda t:-t[7])[:6]]
    print('best digest eq mean'); [print(' ',t) for t in sorted(out,key=lambda t:-t[6])[:6]]
    print('best digest hw min'); [print(' ',t) for t in sorted(out,key=lambda t:t[8])[:6]]
