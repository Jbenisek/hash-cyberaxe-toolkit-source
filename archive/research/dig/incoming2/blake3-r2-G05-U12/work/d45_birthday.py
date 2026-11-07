"""door 45 RELABEL (no test given): measure the generic cost of matching k bits of the 2-round first-block CV
(flags CHUNK_START=1, cv=IV, t=0, b=64) on 7 words (word 0 left free, as a 224-bit near-collision would), at toy k.
Known answer first: our compress vs organizer verifier _compress, then birthday count vs N^2/2^(k+1)."""
import sys, os, numpy as np
sys.argv=[sys.argv[0],'20']
import importlib.util
sp=importlib.util.spec_from_file_location('st','sep_test.py'); st=importlib.util.module_from_spec(sp); sp.loader.exec_module(st)
from verifier import blake3 as ref
rng=np.random.default_rng(45)
M=st.rnd(rng,50) if hasattr(st,'rnd') else None
m=rng.integers(0,2**32,size=(16,50),dtype=np.uint64).astype(np.uint32)
out=st.compress(m,flags=1)
ok=True
for j in range(50):
    r=ref._compress(list(st.IV),[int(x) for x in m[:,j]],0,64,1,2)[:8]
    ok&= [int(x) for x in out[:,j]]==list(r)
print("known answer flags=1 vs verifier _compress, 50/50:",ok)
def keys(n,k):
    m=rng.integers(0,2**32,size=(16,n),dtype=np.uint64).astype(np.uint32)
    o=st.compress(m,flags=1)
    # k bits taken round-robin from words 1..7 (low bits)
    key=np.zeros(n,np.uint64); b=0
    per=[k//7+(1 if i<k%7 else 0) for i in range(7)]
    for w in range(7):
        key=(key<<np.uint64(per[w]))|(o[w+1].astype(np.uint64)&np.uint64((1<<per[w])-1))
    return key
N=1<<22
for k in (32,36,40,44):
    ks=keys(N,k); u,c=np.unique(ks,return_counts=True)
    pairs=int((c*(c-1)//2).sum()); exp=N*(N-1)/2/2**k
    print("k=%d N=2^22 pairs=%d expected(uniform)=%.1f ratio=%.3f"%(k,pairs,exp,pairs/exp))
print("extrapolation: generic match of 224 bits = 2^112 evaluations; of 128 bits = 2^64")
