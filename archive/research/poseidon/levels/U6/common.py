
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

import sys,math,time,random
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as pr
from sympy.polys.matrices import DomainMatrix
from sympy import ZZ
P=pr.P; RC=pr.RC; M=pr.MDS
inv=lambda a:pow(a%P,P-2,P)
def matvec(A,v): return [sum(A[i][j]*v[j] for j in range(3))%P for i in range(3)]
def lll_relations(vals,W=1<<40,mod=P):
    k=len(vals)
    rows=[[1 if j==i else 0 for j in range(k)]+[W*(vals[i]%mod)] for i in range(k)]
    rows.append([0]*k+[W*mod])
    dm=DomainMatrix([[ZZ(x) for x in r] for r in rows],(k+1,k+1),ZZ)
    red=dm.lll().to_Matrix().tolist()
    out=[]
    for r in red:
        if r[-1]==0:
            out.append([int(x) for x in r[:-1]])
    out.sort(key=lambda v:sum(x*x for x in v))
    return out
def norm(v): return math.sqrt(sum(x*x for x in v))
def l2(x): return math.log2(x) if x>0 else float('-inf')
def gh(k,mod=P):  # expected shortest relation norm (Gaussian heuristic) for k numbers mod p
    return math.sqrt(k/(2*math.pi*math.e))*2**(math.log2(mod)/k)
