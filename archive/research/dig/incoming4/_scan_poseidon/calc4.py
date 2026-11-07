
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

import sys, time, random, json
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/levels/decomp'))
from decomp import *
t0=time.time()
out={}
def oddpart(F, c):
    Fs = F.compose(R([c,1]))            # F(c+s)
    co = Fs.coeffs()
    odd = [int(co[i]) for i in range(1,len(co),2)]   # coeff of s^(1,3,5..) -> S^0,1,..
    return R(odd)
def test_inner2(g):
    m=g.degree(); co=g.coeffs()
    lead=int(co[m]); inv=pow(lead,-1,p)
    k=m//2
    a=int(co[m-1])*inv%p*pow(k,-1,p)%p        # H=S^2+aS : g_{m-1}/lead = k*a
    sigma=(-a*pow(2,-1,p))%p                   # S -> S - a/2 makes H even  (H=(S+a/2)^2 - a^2/4)
    g2=g.compose(R([(-a*pow(2,-1,p))%p,1]))   # g(S - a/2)
    c2=g2.coeffs()
    nonzero_odd=[i for i in range(1,len(c2),2) if int(c2[i])!=0]
    # top-down: how many of the first odd coeffs vanish
    return len(nonzero_odd), (nonzero_odd[-1] if nonzero_odd else None), m
# control: planted g = G(S^2+aS) with deg g = 39062
random.seed(7)
a0=random.randrange(p)
Gc=R([random.randrange(p) for _ in range(19531)]+[1])
H=R([0,a0,1])
gc=Gc.compose(H)
out['control_planted']=test_inner2(gc)
# negative control: perturb one coefficient
co=[int(x) for x in gc.coeffs()]; co[100]=(co[100]+1)%p
out['control_perturbed']=test_inner2(R(co))
print(out, time.time()-t0, flush=True)
for j in (0,1,2):
    if time.time()-t0>120: out['stopped_before_j']=j; break
    L=Line(j); s0=s0_line(L)
    F=circuit(s0,1)
    assert F.degree()==5**7
    c=random.randrange(p)
    g=oddpart(F,c)
    out['real_j%d'%j]=test_inner2(g)+(g.degree(),)
    print(j,out['real_j%d'%j],time.time()-t0,flush=True)
json.dump(out,open('calc4.json','w'))
