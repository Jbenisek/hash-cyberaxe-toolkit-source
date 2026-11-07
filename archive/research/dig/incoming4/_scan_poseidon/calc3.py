
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

import sys, time, random, json, itertools
from math import lgamma, log, log2
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/lean_r1_fix'))
import poseidon_ref as ref
P=ref.P
out={}
# 1. P3.9 recompute
def lb(n,k): return (lgamma(n+1)-lgamma(k+1)-lgamma(n-k+1))/log(2)
for r in (1,2):
    m=52+6*r; q=48+2*r; d=1+4*q
    logN=lb(m+d,d); 
    # R = q*C(m+d-5,d-5) + (m-q)*C(m+d-1,d-1)
    a=log2(q)+lb(m+d-5,d-5); b=log2(m-q)+lb(m+d-1,d-1)
    logR=max(a,b)+log2(1+2**(-abs(a-b)))
    mn=min(logN,logR)
    ops=log2(2)+logR+logN+mn  # 2*R*N*min
    mem=5+logR+logN  # 32*R*N bytes -> log2 bytes = 5+logR+logN?? P3.9 stores R*N dense
    out['p39_r%d'%r]=dict(m=m,q=q,d=d,logN=logN,logR=logR,logops=ops,logbytes=5+logR+logN)
# 2. mu4 symmetry
import random
rng=random.Random(5)
g=pow(5,(P-1)//4,P)  # element; find 4th root of unity
z=None
for a in range(2,50):
    c=pow(a,(P-1)//4,P)
    if pow(c,2,P)!=1: z=c;break
assert pow(z,4,P)==1 and pow(z,2,P)!=1
res=[]
for _ in range(5):
    nk,rho=rng.randrange(P),rng.randrange(P)
    h=ref.hash_reduced(nk,rho,1)
    h2=ref.hash_reduced(z*nk%P,z*rho%P,1)
    res.append((h2==z*h%P, h2==h))
out['mu4']=res
# S-box equivariance
x=rng.randrange(P); out['sbox_mu4_equivariant']=pow(z*x%P,5,P)==z*pow(x,5,P)%P
# 3. MDS minors
M=ref.MDS
nz1=all(M[i][j]%P for i in range(3) for j in range(3))
def minor2(r0,r1,c0,c1): return (M[r0][c0]*M[r1][c1]-M[r0][c1]*M[r1][c0])%P
nz2=all(minor2(a,b,c,d) for a,b in itertools.combinations(range(3),2) for c,d in itertools.combinations(range(3),2))
det=(M[0][0]*minor2(1,2,1,2)-M[0][1]*minor2(1,2,0,2)+M[0][2]*minor2(1,2,0,1))%P
out['mds']=dict(entries_nonzero=nz1,minors2_nonzero=nz2,det_nonzero=det!=0)
json.dump(out,open('calc3a.json','w'),indent=1); print(json.dumps(out,indent=1))
