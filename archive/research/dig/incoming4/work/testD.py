
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

import sys,time,random,ctypes,json
ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(),0x4000)
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/decomp'))
from decomp import *
def test_poly(F,d):
    n=F.degree(); top=from_poly(F,d); B=B_from_top(top,n,d); nc,tot=digits(F,B); return B,nc,tot
def compose(G,H):
    out=R([0])
    for c in reversed([int(x) for x in G.coeffs()]): out=out*H+cst(c)
    return out
n=5**8
mode=sys.argv[1]; ds=[int(x) for x in sys.argv[2].split(',')]
if mode=='real':
    j=int(sys.argv[3]); L=Line(j); s0=s0_line(L); F=circuit(s0,2); assert F.degree()==n
    for dH in ds:
        t=time.time(); B,nc,tot=test_poly(F,dH)
        print(json.dumps(dict(kind='real',r=2,j=j,inner=dH,nonconst=nc,digits=tot,decomposes=(nc==0),secs=round(time.time()-t))),flush=True)
else:
    random.seed(11)
    for dH in ds:
        dG=n//dH
        Hc=R([0]+[random.randrange(p) for _ in range(dH-1)]+[1]); Gc=R([random.randrange(p) for _ in range(dG)]+[1])
        Fp=compose(Gc,Hc); assert Fp.degree()==n
        t=time.time(); B,nc,tot=test_poly(Fp,dH)
        print(json.dumps(dict(kind='planted',inner=dH,recovered=(B==Hc),nonconst=nc,digits=tot,secs=round(time.time()-t))),flush=True)
        Fq=Fp+R([0]*5+[1]); B,nc,tot=test_poly(Fq,dH)
        print(json.dumps(dict(kind='perturbed',inner=dH,nonconst=nc)),flush=True)
