# door 21 RELABEL test: word-level simulation of delta 7 (flags 11 vs 12) through round 1; count active G calls

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import numpy as np, collections, json
from b3own import *
rng=np.random.default_rng(2112)
N=1<<20
cv=list(IV); 
mA=[rng.integers(0,2**32,N,dtype=np.uint64).astype(U) for _ in range(16)]
a=U(cv[3]); b=U(cv[7])     # K3 = G(3,7,11,15): a=v3=cv3, b=v7=cv7, c=IV3, d=flags
a1A=a+b+mA[6]
a1B=a1A^U(11^12)
mB=list(mA)
mB[6]=a1B-a-b                      # m6'
mB[7]=mA[7]-(a1B-a1A)              # m7' re-absorbs
snap={}
def mk(tag):
    def hook(r,k,v,mm):
        if r==0 and k==8: snap[(tag,'X')]=[x.copy() for x in v]
        if r==1 and k<8:
            snap[(tag,k)]=([x.copy() for x in v],[mm[2*k].copy(),mm[2*k+1].copy()])
    return hook
vA,dA=compress(cv,mA,0,64,11,2,mk('A'))
vB,dB=compress(cv,mB,0,64,12,2,mk('B'))
# check against organizer reference on a few
import importlib.util
spec=importlib.util.spec_from_file_location('vb3',_hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier/blake3.py')); vb=importlib.util.module_from_spec(spec); spec.loader.exec_module(vb)
for i in range(50):
    assert tuple(int(x[i]) for x in dA)==vb._compress(cv,[int(x[i]) for x in mA],0,64,11,2)[:8]
    assert tuple(int(x[i]) for x in dB)==vb._compress(cv,[int(x[i]) for x in mB],0,64,12,2)[:8]
print('50 pairs match organizer _compress at flags 11 / 12')
XA,XB=snap[('A','X')],snap[('B','X')]
print('X (state after round 0) identical in all 16 words, trials:',all((XA[i]==XB[i]).all() for i in range(16)),'of',N)
print('words of X equal count per word:',[int((XA[i]==XB[i]).sum()) for i in range(16)])
# delta set of m6 diff
d6=(mB[6]-mA[6]).astype(np.int64); d6=np.where(d6>2**31,d6-2**32,d6)
print('arith diff m6B-m6A distribution:',dict(sorted(collections.Counter(d6.tolist()).items())))
print('m7B-m7A = -(m6 diff): ',bool(((mB[7]-mA[7])==(np.uint32(0)-(mB[6]-mA[6]))).all()))
print('other message words differ?',[i for i in range(16) if i not in (6,7) and (mA[i]!=mB[i]).any()])
# active calls in round 1
act=[]
for k in range(8):
    (vk,mk_)=snap[('A',k)]; (wk,nk)=snap[('B',k)]
    ins=[CALLS[k][j] for j in range(4)]
    di=[(vk[i]!=wk[i]) for i in ins]+[(mk_[0]!=nk[0]),(mk_[1]!=nk[1])]
    anyd=np.logical_or.reduce(di)
    act.append(anyd.mean())
    print(NAMES[8+k],'input words differing (a,b,c,d,x,y) fraction:',[round(float(x.mean()),4) for x in di],'call active frac',round(float(anyd.mean()),4))
print('active round-1 calls (frac==1):',[NAMES[8+k] for k in range(8) if act[k]==1.0], ' count',sum(1 for x in act if x==1.0))
# round 0 active calls : none expected since B differs only in v15 and m6,m7 consumed in K3
# digest words
nz=[int((dA[i]!=dB[i]).sum()) for i in range(8)]
print('digest words with nonzero difference (count of',N,'trials):',nz)
print('trials with all 8 digest words differing:',int(np.logical_and.reduce([dA[i]!=dB[i] for i in range(8)]).sum()))
# final state words differing
print('final v words differing counts:',[int((vA[i]!=vB[i]).sum()) for i in range(16)])
# distance: min hamming weight of digest xor diff per word
for i in range(8):
    x=(dA[i]^dB[i]); hw=np.array([bin(int(t)).count('1') for t in x[:20000]])
    print('digest word',i,'min HW of xor diff over 20000:',int(hw.min()),'mean',round(float(hw.mean()),2))
