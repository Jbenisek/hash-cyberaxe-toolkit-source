
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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as H
P=H.P; M=H.MDS
def mv(v): return [sum(M[i][j]*v[j] for j in range(3)) % P for i in range(3)]
u=[0,M[0][2],(-M[0][1])%P]
v=mv(u); print("u=(0,M02,-M01); (Mu)_0 =",v[0]," (Mu)=",[hex(x)[:12] for x in v])
w=mv(v); print("(M(Mu))_0 = hex", hex(w[0]), "nonzero:", w[0]!=0)
# direction of Mu in lanes 1,2 vs u
print("Mu lanes(1,2) proportional to u(1,2)?", (v[1]*u[2]-v[2]*u[1])%P==0)
