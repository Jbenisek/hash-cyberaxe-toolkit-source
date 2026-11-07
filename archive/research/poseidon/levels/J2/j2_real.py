"""J2 real: level polynomial of lane 0 after R3 along the line rho=rho0 (degree 625 in nk); factor pattern of (L3(x)-L3(P))/(x-nk0).
Validate against poseidon_ref (value check) first. Control: random degree-624 polys; single process."""

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

import sys, time, random
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
p=R.P; F=fmpz_mod_ctx(p); PC=fmpz_mod_poly_ctx(F)
def mds_poly(s):
    return [sum((R.MDS[i][j]*s[j] for j in range(3)),PC([0])) for i in range(3)]
def l3_poly(rho0):
    x=PC([0,1]); s=[x,PC([rho0]),PC([R.CAPACITY])]
    for idx in range(4):
        s=[s[i]+R.RC[idx][i] for i in range(3)]
        s=[t**5 for t in s]
        s=mds_poly(s)
    return s[0]
def l3_val(nk,rho):
    s=[nk,rho,R.CAPACITY]
    for idx in range(4): s=R.round_full(s,idx)
    return s[0]
rnd=random.Random(int(sys.argv[1]) if len(sys.argv)>1 else 1)
ntr=int(sys.argv[2]) if len(sys.argv)>2 else 8
t0=time.time()
rho0=rnd.randrange(p); f=l3_poly(rho0)
print('degree',f.degree(),'built in %.1fs'%(time.time()-t0))
for _ in range(3):
    x=rnd.randrange(p); assert int(f(x))==l3_val(x,rho0)
print('VALUE CHECK vs poseidon_ref.round_full: ok (3 points)')
def pattern(g):
    c,fac=g.factor()
    return sorted([(h.degree(),e) for h,e in fac]),
res=[]
for tr in range(ntr):
    nk0=rnd.randrange(p); v=l3_val(nk0,rho0)
    g=(f-v)//PC([-nk0,1]) if False else None
    h=f-PC([v]); q_,rem=divmod(h,PC([-nk0,1])); assert rem.degree()<0
    t=time.time(); pat=pattern(q_)[0]; dt=time.time()-t
    roots=sum(1 for d,e in pat if d==1)
    print('trial %d: deg %d factors %d roots %d degs(sorted desc) %s  (%.1fs)'%(tr,q_.degree(),sum(e for d,e in pat),roots,[d for d,e in sorted(pat,reverse=True)][:40],dt),flush=True)
    res.append(pat)
print('--- control random degree-624 polys')
for tr in range(min(ntr,4)):
    g=PC([rnd.randrange(p) for _ in range(624)]+[1]); t=time.time(); pat=pattern(g)[0]
    print('rand %d: factors %d roots %d degs %s (%.1fs)'%(tr,sum(e for d,e in pat),sum(1 for d,e in pat if d==1),[d for d,e in sorted(pat,reverse=True)][:40],time.time()-t),flush=True)
