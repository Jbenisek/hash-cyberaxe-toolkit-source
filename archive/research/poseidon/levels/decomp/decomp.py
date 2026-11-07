
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
sys.path.insert(0,_hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/math'))
from attack import *
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
ctx = fmpz_mod_ctx(p); R = fmpz_mod_poly_ctx(ctx)
Wp = R([0,1])
def cst(c): return R([c % p])

def circuit(s0, r, red=None):
    """s0: 3 polys (state after round-1 S-box, before round-1 MDS). red: reduce fn (mod B) or None"""
    red = red or (lambda x: x)
    def pw5(x):
        x2 = red(x*x); x4 = red(x2*x2); return red(x4*x)
    s = [sum((s0[k]*MDS[i][k] for k in range(3)), R([0])) for i in range(3)]
    s = [red(x) for x in s]
    for k in [2,3]+list(range(4,4+r))+[60,61,62,63]:
        full = k<4 or k>=60
        s = [s[i]+RC[k][i] for i in range(3)]
        s = [pw5(s[i]) if (full or i==0) else s[i] for i in range(3)]
        s = [red(sum((s[k2]*MDS[i][k2] for k2 in range(3)), R([0]))) for i in range(3)]
    return s[0]

def s0_line(L, Zpoly=None):
    Z = Wp if Zpoly is None else Zpoly
    return [cst(L.v0[k]) + Z*L.v1[k] for k in range(3)]

# ---- truncated reversed-series propagation (top-d coefficients) ----
class Rv:
    def __init__(s, deg, H): s.deg=deg; s.H=H
def mul_t(a,b,d):
    out=[0]*d
    for i,x in enumerate(a):
        if x:
            for j in range(d-i):
                out[i+j]=(out[i+j]+x*b[j])%p
    return out
def from_poly(f, d):
    D=f.degree(); c=[int(x) for x in f.coeffs()]
    return Rv(D,[c[D-i] if D-i>=0 else 0 for i in range(d)])
def radd(a,b,d):
    if a.deg<b.deg: a,b=b,a
    sh=a.deg-b.deg; H=list(a.H)
    for i in range(d-sh): H[i+sh]=(H[i+sh]+b.H[i])%p
    assert H[0]%p, 'leading cancellation'
    return Rv(a.deg,H)
def rscal(a,c,d): return Rv(a.deg,[x*c%p for x in a.H])
def raddc(a,c,d):
    H=list(a.H)
    if a.deg<d: H[a.deg]=(H[a.deg]+c)%p
    return Rv(a.deg,H)
def rmul(a,b,d): return Rv(a.deg+b.deg, mul_t(a.H,b.H,d))
def rpow5(a,d):
    a2=rmul(a,a,d); a4=rmul(a2,a2,d); return rmul(a4,a,d)
def circuit_top(s0, r, d):
    s=[from_poly(x,d) for x in s0]
    def mdsr(s):
        out=[]
        for i in range(3):
            acc=rscal(s[0],MDS[i][0],d)
            for k in (1,2): acc=radd(acc,rscal(s[k],MDS[i][k],d),d)
            out.append(acc)
        return out
    s=mdsr(s)
    for k in [2,3]+list(range(4,4+r))+[60,61,62,63]:
        full = k<4 or k>=60
        s=[raddc(s[i],RC[k][i],d) for i in range(3)]
        s=[rpow5(s[i],d) if (full or i==0) else s[i] for i in range(3)]
        s=mdsr(s)
    return s[0]

def root_series(g, alpha, d):
    """h = g^alpha, g[0]!=0; g[0] must be 1 here"""
    assert g[0]==1
    h=[1]+[0]*(d-1)
    for n in range(1,d):
        acc=0
        for k in range(1,n+1):
            acc+= ((alpha*k-(n-k))%p)*g[k]%p*h[n-k]
        h[n]=acc%p*pow(n,-1,p)%p
    return h
def B_from_top(F_top, n, d):
    m=n//d
    H0=F_top.H[0]; g=[x*pow(H0,-1,p)%p for x in F_top.H]
    h=root_series(g, pow(m,-1,p), d)
    coef=[0]*(d+1); coef[d]=1
    for i in range(1,d): coef[d-i]=h[i]
    coef[0]=0
    return R(coef)

def screen(s0, r, d, n):
    top=circuit_top(s0,r,d)
    assert top.deg==n
    B=B_from_top(top,n,d)
    red=lambda x: x % B
    rem=circuit(s0,r,red)
    return B, rem

def digits(F, B):
    """B-adic digits by divide and conquer; returns (#nonconstant digits, #digits visited)"""
    d=B.degree(); pw=[B]
    while pw[-1].degree()*2 <= F.degree(): pw.append(pw[-1]*pw[-1])
    cnt=[0,0]
    def rec(G,k):
        if G.degree()<0: return
        if k<0:
            cnt[1]+=1
            if G.degree()>0: cnt[0]+=1
            return
        q,rm=divmod(G,pw[k]); rec(rm,k-1); rec(q,k-1)
    rec(F,len(pw)-1)
    return tuple(cnt)
