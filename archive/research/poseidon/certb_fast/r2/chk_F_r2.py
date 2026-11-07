
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

import sys,random,hashlib
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/decomp'))
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/lean_r1_fix'))
from decomp import *
import poseidon_ref as ref
D=5**8
random.seed(20261013)
path=_hca_public_path_text('__HCA_WORKSPACE__/3rd_openai_workspace/luna3/P3_21_F_j0_coeffs.bin')
raw=open(path,'rb').read()
co=[int.from_bytes(raw[i:i+32],'little') for i in range(0,len(raw),32)]
assert len(co)==D+1 and all(c<p for c in co)
print('sha256',hashlib.sha256(raw).hexdigest(),'lead',hex(co[-1]))
FL=R(co); L=Line(0); ok=True
for t in range(5):
    tau=random.randrange(1,p); nk,rho=L.inputs(tau); W=pow(tau,5,p)
    h=ref.hash_reduced(nk,rho,2); v=int(FL(W)); print(t,h==v); ok&=(h==v)
print('r=2 reference hash == F(tau^5) at 5 taus:',ok)
