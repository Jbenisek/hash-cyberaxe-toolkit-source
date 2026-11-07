
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

import sys,random,struct,math
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/hash-smash')); sys.path.insert(0,'.')
from b3ctr import *
import importlib
V=importlib.import_module('verifier.blake3')
R=random.Random(5)
# ---- T0 validation
bad=0
for _ in range(3000):
    w=[R.getrandbits(32) for _ in range(16)]; ctr=R.getrandbits(50); n=R.randrange(1,65); fl=R.choice([0,1,2,3,8,11,4,12])
    cv=[R.getrandbits(32) for _ in range(8)]
    ref=V._compress(cv,w,ctr,n,fl,2)
    v=cv+IV[:4]+[ctr&M,ctr>>32,n,fl]; s=list(w)
    for r in range(2):
        for i,(a,b,c,d) in enumerate(CALLS): G(v,a,b,c,d,s[2*i],s[2*i+1])
        s=[s[p] for p in P]
    mine=[v[i]^v[i+8] for i in range(8)]+[v[i+8]^cv[i] for i in range(8)]
    bad+= list(ref)[:16]!=mine
print("T0 2-round vs verifier _compress (64-bit counters, random flags/len/cv):",3000-bad,"/3000 equal")
# 7-round known vector: BLAKE3("") = af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262
o=comp([0]*16,0,0,flags=11,rounds=7)
h=b''.join(struct.pack('<I',x) for x in o).hex()
print("T0 7-round empty hash:",h, h=="af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262")
print("verifier blake3(b'') 7 rounds equal:",V.blake3(b'',7).hex()==h)
# ---- construction known answer (t_hi=0)
def rf(hi_bits=0,cube=True,cls=True):
    f=rnd_free(R,1); f['t_hi']=R.getrandbits(hi_bits) if hi_bits else 0
    if cube:
        mask=0x0e09818b; f['c1']=(R.getrandbits(32)&~mask&M)|0x02008000
    return f
def pair(f):
    w,t,L=build(f); wa,wb=messages(w,t); return wa,wb,t,L
def pins(wa,wb,t):
    oa,Xa,_=comp(wa,t,55,trace=True); ob,Xb,_=comp(wb,t,63,trace=True)
    return Xa==Xb, (Xa[3],Xa[7],Xa[11],Xa[15])==(X3,X7,X11,X15), all(oa[i]==ob[i] for i in (0,2,5,7)), oa, ob
for hb,name in ((0,'t_hi=0'),(16,'t_hi<2^16'),(32,'t_hi<2^32')):
    N=3000; c=[0,0,0]; 
    for _ in range(N):
        f=rf(hb); wa,wb,t,L=pair(f); a,b,cc,_,_=pins(wa,wb,t)
        c[0]+=a;c[1]+=b;c[2]+=cc
    print("T1 %s: X equal (Lemma L) %d/%d, pins X3/7/11/15 held %d/%d, digest words 0,2,5,7 equal %d/%d"%(name,c[0],N,c[1],N,c[2],N))
