
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

import sys
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/math'))
from pos import *
import json
e0=[1,0,0]
def vm(v,M): return [sum(v[i]*M[i][j] for i in range(3))%p for j in range(3)]
r1=vm(e0,MDS); r2=vm(r1,MDS)
def det3(a,b,c):
    return (a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))%p
d=det3(e0,r1,r2)
u=[0,MDS[0][2],(-MDS[0][1])%p]
Mu=[sum(MDS[i][j]*u[j] for j in range(3))%p for i in range(3)]
M2u=[sum(MDS[i][j]*Mu[j] for j in range(3))%p for i in range(3)]
out=dict(det_hex=hex(d),det_nonzero=d!=0,Mu0=Mu[0],M2u0_nonzero=M2u[0]!=0)
print(out); json.dump(out,open('testF.json','w'))
