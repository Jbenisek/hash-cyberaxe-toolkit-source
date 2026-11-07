# DOOR.d45 D1 at 3 rounds: generic cost of matching k bits of the 3-round first-block CV (flags 1 CHUNK_START, cv=IV, t=0, b=64)
# on digest words 1..7 (word 0 left free, as a 224-bit near-collision would). Known answer first.
import numpy as np
from common import *
from b3own import compress, IV
rng=np.random.default_rng(45)
# known answer: compress(flags=1) vs verifier _compress at 3 rounds and 7 rounds
ok=True
for r in (3,7):
    m=rng.integers(0,2**32,size=(16,50),dtype=np.uint64).astype(np.uint32)
    v,d=compress(list(IV),[m[i] for i in range(16)],0,64,1,r)
    for j in range(50):
        ref=vb._compress(list(IV),[int(x) for x in m[:,j]],0,64,1,r)[:8]
        ok&= tuple(int(x[j]) for x in d)==ref
print('known answer flags=1 b=64 vs verifier _compress, rounds 3 and 7, 50/50 each:',ok)
KS=(32,36,40,44,48)
def keys(n):
    m=rng.integers(0,2**32,size=(16,n),dtype=np.uint64).astype(np.uint32)
    v,d=compress(list(IV),[m[i] for i in range(16)],0,64,1,3)
    res={}
    for k in KS:
        key=np.zeros(n,np.uint64)
        per=[k//7+(1 if i<k%7 else 0) for i in range(7)]
        for w in range(7):
            key=(key<<np.uint64(per[w]))|(d[w+1].astype(np.uint64)&np.uint64((1<<per[w])-1))
        res[k]=key
    return res
NL=22; chunks=4
allk={k:[] for k in KS}
for _ in range(chunks):
    r=keys(1<<NL)
    for k in KS: allk[k].append(r[k])
N=chunks<<NL
for k in KS:
    ks=np.concatenate(allk[k]); u,c=np.unique(ks,return_counts=True)
    pairs=int((c*(c-1)//2).sum()); exp=N*(N-1)/2/2**k
    print('k=%d N=2^%d pairs=%d expected(uniform)=%.2f ratio=%.3f'%(k,int(np.log2(N)),pairs,exp,pairs/exp))
print('generic price of a 224-bit match: 2^112 evaluations; of a 128-bit match: 2^64')
