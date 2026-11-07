"""dig-scan-poseidon engine: exact digest polynomial on the skip line, with per-layer variants (flint, Pallas)."""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/lean_r1_fix'))
from poseidon_ref import *
import flint
from flint import fmpz_mod_poly_ctx, fmpz_mod_ctx
FC = fmpz_mod_ctx(P)
PC = fmpz_mod_poly_ctx(FC)
inv = lambda x: pow(x, P-2, P)
I3 = ((1,0,0),(0,1,0),(0,0,1))
Wp = PC([0,1])          # the variable W

def p5(f):
    f2 = f*f; return f2*f2*f

def lincomb(coefs, polys):
    out = PC(0)
    for c, f in zip(coefs, polys):
        if c % P: out = out + f*c
    return out

def mat_apply(Mx, st):
    return [lincomb(Mx[i], st) for i in range(3)]

def default_var():
    # per original round index: arc mask (lanes keeping constant), sbox mask (lanes S-boxed), mds matrix
    return {}

def round_opts(idx, var):
    full = idx < 4 or idx >= 60
    o = dict(arc=(1,1,1), sb=((1,1,1) if full else (1,0,0)), M=MDS)
    o.update(var.get(idx, {}))
    return o

def setup(Mat0, o0, j, o1=None):
    """line for kept coordinate j under round-0 matrix Mat0; returns (a,b,U0,V0) with x = A(U,V)+base."""
    Kp = pow((CAPACITY + (RC[0][2] if o0['arc'][2] else 0)) % P, 5 if o0['sb'][2] else 1, P)
    c1 = RC[1] if (o1 is None or o1['arc']==(1,1,1)) else tuple(RC[1][i] if o1['arc'][i] else 0 for i in range(3))
    base = [(Mat0[i][2]*Kp + c1[i]) % P for i in range(3)]
    a, b = Mat0[j][1] % P, (-Mat0[j][0]) % P
    if a == 0 and b == 0: a, b = 1, 1
    ii = [i for i in range(3) if i != j]
    (p0,q0),(p1,q1) = (Mat0[ii[0]][0],Mat0[ii[0]][1]),(Mat0[ii[1]][0],Mat0[ii[1]][1])
    det = (p0*q1 - p1*q0) % P
    if det == 0: return None
    r0, r1 = (-base[ii[0]]) % P, (-base[ii[1]]) % P
    U0 = (r0*q1 - r1*q0)*inv(det) % P
    V0 = (p0*r1 - p1*r0)*inv(det) % P
    d = [(Mat0[i][0]*a + Mat0[i][1]*b) % P for i in range(3)]
    return a, b, U0, V0, d, base

def run_line(r, j, var=None, verbose=False):
    """Exact digest polynomial in W on line j. Returns dict(deg, lc!=0, poly, state degrees)."""
    var = var or {}
    o0 = round_opts(0, var); o1 = round_opts(1, var)
    Mat0 = o0['M']
    # round 0 S-box on lanes 0,1 only changes the (nk,rho)->(U,V) relabelling; plane in (U,V) is Mat0*(U,V,K)
    s = setup(Mat0, o0, j, o1)
    if s is None: return dict(ok=False, why='line setup singular')
    a, b, U0, V0, d, base = s
    # S-box input of R1 on the line: x_i = d_i*tau (i!=j) ; x_j = base_j + (A U0+..)_j (constant)
    xj = (Mat0[j][0]*U0 + Mat0[j][1]*V0 + base[j]) % P
    # state entering R1 S: x polys in tau; we keep W=tau^5 only if every S-boxed varying lane is S-boxed
    x_const = [xj if i == j else 0 for i in range(3)]
    st = []
    for i in range(3):
        if i == j: st.append(PC(xj))
        else:
            if not o1['sb'][i]:
                return dict(ok=False, why='R1 varying lane %d not S-boxed: state not a polynomial in W' % i)
            st.append(None)
    out = []
    for i in range(3):
        if i == j: out.append(PC(pow(xj,5,P)) if o1['sb'][i] else PC(xj))
        else: out.append(PC(pow(d[i],5,P)) * Wp)
    st = mat_apply(o1['M'], out)
    sched = [i for i in range(2, 4+r)] + list(range(60,64)) if False else None
    idxs = list(range(2,4)) + list(range(4,4+r)) + list(range(60,64))
    degs = []
    for idx in idxs:
        o = round_opts(idx, var)
        st = [st[i] + (RC[idx][i] if o['arc'][i] else 0) for i in range(3)]
        st = [p5(st[i]) if o['sb'][i] else st[i] for i in range(3)]
        st = mat_apply(o['M'], st)
        degs.append(max(f.degree() for f in st))
    y = st[0]
    return dict(ok=True, deg=y.degree(), poly=y, lane_deg=degs, lc=int(y[y.degree()]) if y.degree()>=0 else 0)

def validate():
    """tool check: poseidon_ref vs pinned vectors and flint line digest vs reference hash"""
    import os
    r = 1
    for j in range(3):
        res = run_line(r, j)
        a,b,U0,V0,d,base = setup(MDS, round_opts(0,{}), j)
        for tau in (3, 12345, 987654321987):
            nk = (pow((U0+a*tau)%P, pow(5,-1,P-1), P) - RC[0][0]) % P
            rho = (pow((V0+b*tau)%P, pow(5,-1,P-1), P) - RC[0][1]) % P
            W = pow(tau,5,P)
            assert int(res['poly'](W)) == hash_reduced(nk, rho, r), (j, tau)
        print('validate r=%d j=%d deg=%d ok'%(r,j,res['deg']))

if __name__ == '__main__':
    t=time.time(); validate(); print('t',time.time()-t)
