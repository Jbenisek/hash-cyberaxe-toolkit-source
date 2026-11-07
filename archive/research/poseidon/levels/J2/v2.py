
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

import sys, random, time
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
p=R.P; F=fmpz_mod_ctx(p); PC=fmpz_mod_poly_ctx(F)
def lane0(rc,mds,s):
    for idx in range(4):
        s=[s[i]+rc[idx][i] for i in range(3)]
        s=[t**5 for t in s]
        s=[sum((mds[i][j]*s[j] for j in range(3)),PC([0])) for i in range(3)]
    return s[0]
def cauchy(r):
    xs=[r.randrange(p) for _ in range(3)]; ys=[r.randrange(p) for _ in range(3)]
    return [[pow((xs[i]+ys[j])%p,-1,p) for j in range(3)] for i in range(3)]
def pat(g):
    c,fac=g.factor(); return sorted([(h.degree(),e) for h,e in fac],reverse=True)
def lev(f,nk0):
    v=f(nk0); h=f-PC([v]); q,rem=divmod(h,PC([-nk0,1])); assert rem.degree()<0; return q
def fmt(pt): return ' '.join('%d%s'%(d,'^%d'%e if e>1 else '') for d,e in pt)
def report(tag,q):
    t=time.time(); pt=pat(q); n=sum(e for d,e in pt); n4=sum(e for d,e in pt if d==4)
    print('%s: nfac %d deg4 %d roots %d | %s (%.0fs)'%(tag,n,n4,sum(1 for d,e in pt if d==1),fmt(pt),time.time()-t),flush=True)
mode=sys.argv[1]; seed=int(sys.argv[2]); N=int(sys.argv[3]); r=random.Random(seed)
RCr=[list(x) for x in R.RC]; M=[list(x) for x in R.MDS]
for k in range(N):
    nk0=r.randrange(p); rho0=r.randrange(p); cap=R.CAPACITY
    rc,mds=RCr,M; 
    if mode=='real': pass
    elif mode=='rc': rc=[[r.randrange(p) for _ in range(3)] for _ in range(4)]
    elif mode=='mds': mds=cauchy(r)
    elif mode=='cap': cap=r.randrange(p)
    elif mode=='slant':
        a=r.randrange(p); b=r.randrange(p)
    elif mode=='randpoly':
        report('randpoly %d'%k,PC([r.randrange(p) for _ in range(624)]+[1])); continue
    elif mode=='randg5':  # random g(u^5) with u=x+c0
        c0=RCr[0][0]; g=PC([r.randrange(p) for _ in range(125)]+[1]); u=PC([c0,1]); f=g(u**5) if False else None
        # compose manually
        u5=u**5; f=PC([0]); 
        for co in reversed(g.coeffs()): f=f*u5+PC([int(co)])
        report('randg5 %d'%k,lev(f,nk0)); continue
    x=PC([0,1])
    s=[x,PC([rho0]),PC([cap])]
    if mode=='slant': s=[x,PC([b,a]),PC([cap])]
    f=lane0(rc,mds,s)
    assert f.degree()==625,f.degree()
    report('%s %d'%(mode,k),lev(f,nk0))
