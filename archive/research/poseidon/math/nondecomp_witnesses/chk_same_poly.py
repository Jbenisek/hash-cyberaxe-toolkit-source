
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

import sys,random,hashlib,time
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/decomp'))
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/lean_r1_fix'))
from decomp import *
import poseidon_ref as ref
D=78125
random.seed(20261012)
for j in (0,1,2):
    path=_hca_public_path_text('__HCA_WORKSPACE__/3rd_openai_workspace/luna3/P3_20_F_j%d_coeffs.bin')%j
    raw=open(path,'rb').read()
    co=[int.from_bytes(raw[i:i+32],'little') for i in range(0,len(raw),32)]
    assert len(co)==D+1
    FL=R(co)
    L=Line(j); F=circuit(s0_line(L),1)
    ok=True
    print('j',j,'sha256',hashlib.sha256(raw).hexdigest())
    print(' degree ours',F.degree(),'luna',FL.degree(),'lead ours',hex(int(F.coeffs()[-1])),'lead luna',hex(co[-1]),'leadmatch',int(F.coeffs()[-1])==co[-1])
    print(' full coefficient equality:',F==FL)
    for t in range(20):
        x=random.randrange(p)
        a=int(F(x)); b=int(FL(x)); c=0
        # Horner independent check of luna coeffs
        if t<3:
            y=0
            for a_ in reversed(co): y=(y*x+a_)%p
            c=y; assert c==b
        if a!=b: ok=False
    print(' 20 random points eval match:',ok)
    # reference hash cross-check
    ok2=True
    for t in range(5):
        tau=random.randrange(1,p)
        nk,rho=L.inputs(tau); W=pow(tau,5,p)
        h=ref.hash_reduced(nk,rho,1)
        if not (h==int(F(W))==int(FL(W))): ok2=False
    print(' reference hash_reduced(r=1) == F(tau^5) == Luna(tau^5) at 5 taus:',ok2)
