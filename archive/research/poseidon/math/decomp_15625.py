
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

import sys,time,random
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/decomp'))
from decomp import *
def test_poly(F,d):
    n=F.degree(); top=from_poly(F,d)
    B=B_from_top(top,n,d)
    nc,tot=digits(F,B)
    return B,nc,tot
def compose(G,H):
    # Horner
    out=R([0])
    for c in reversed([int(x) for x in G.coeffs()]): out=out*H+cst(c)
    return out

random.seed(11); n=5**7; dH=15625; dG=5
Hc=R([0]+[random.randrange(p) for _ in range(dH-1)]+[1]); Gc=R([random.randrange(p) for _ in range(dG)]+[1])
Fp=compose(Gc,Hc); assert Fp.degree()==n
t=time.time(); B,nc,tot=test_poly(Fp,dH)
print('VALID planted inner',dH,'recovered H:',B==Hc,'nonconst digits',nc,'of',tot,round(time.time()-t),flush=True)
Fq=Fp+R([0]*5+[1]); print('  perturbed: nonconst',test_poly(Fq,dH)[1],flush=True)
for j in (0,1,2):
    L=Line(j); F=circuit(s0_line(L),1); assert F.degree()==n
    t=time.time(); B,nc,tot=test_poly(F,dH)
    print('REAL j',j,'inner',dH,'nonconst digits',nc,'of',tot,'decomposes:',nc==0,round(time.time()-t),flush=True)
