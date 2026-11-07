"""U9 Q5: top homogeneous forms in (A,B)-coordinates (the (nk,rho) top form is Phi(X^5,Y^5)), dehomogenised z=U/V, roots over F_q.
Recursion: lanes f_i(z) of formal homogeneous degree d. full round: f_i <- sum_j M_ij f_j^5. partial round: f_i <- M_i0 f_0^5 (lanes 1,2 have lower degree and drop out of the top form).
usage: python u9_topform.py real <r> <maxdeg>          (roots counted by flint on lane 0 after each round, while formal degree <= maxdeg)
       python u9_topform.py toy <q> <seed> <r> [enumerate]   (also pointwise enumeration over all q+1 projective points)"""
import sys, time
from u9lib import Ring, log, T0
mode = sys.argv[1]
if mode == 'real':
    from u9lib import P, M, RC, CAP, schedule, kind
    q = P; r = int(sys.argv[2]); maxdeg = int(sys.argv[3]); Mx = M; sch = schedule(r)
else:
    from u9toy import *
    q = int(sys.argv[2]); seed = int(sys.argv[3]); r = int(sys.argv[4]); maxdeg = 10**9
    Mx, RCx, cap = toy_params(q, seed); sch = sched(r)
    en = len(sys.argv) > 5
ring = Ring(q)
z = ring.x()
f = [z*Mx[i][0] + Mx[i][1] for i in range(3)]
d = 1
def analyse(fp, d, label):
    deg = fp.degree()
    cs = None
    low = 0
    # multiplicity of z=0
    cs = fp.coeffs()
    while low < len(cs) and cs[low] == 0: low += 1
    t = time.time()
    rts = fp.roots()
    return deg, low, rts, time.time()-t
res = []
for idx in sch[1:]:
    kd = kind(idx)
    if d*5 > maxdeg: break
    if kd == 'full':
        g = [ring.pow5(x) for x in f]; f = [ring.lin(Mx[i], g) for i in range(3)]
    else:
        g0 = ring.pow5(f[0]); f = [g0*Mx[i][0] for i in range(3)]
    d *= 5
    deg, low, rts, tt = analyse(f[0], d, '')
    nr = len(rts)
    gap = d - deg
    log('after R%-2d (%s) formal degree 5^%d=%d: lane0 poly degree %d (root at infinity multiplicity %d), multiplicity of root z=0 is %d, distinct roots in F_q: %d (%.0fs)%s' % (idx, kd, len(str(d)) and round(__import__('math').log(d, 5)), d, deg, gap, low, nr, tt, ' multiplicities %s' % [m for _, m in rts] if nr else ''))
    res.append((idx, d, nr, gap, low))
    if mode == 'real' and nr: log('   roots (first): %s' % [hex(int(a))[:20] for a, _ in rts[:3]])
if mode != 'real' and en:
    import numpy as np
    u = np.arange(q, dtype=np.int64)
    def p5(x): x2 = x*x % q; x4 = x2*x2 % q; return x4*x % q
    def run(U, V):
        fl = [(Mx[i][0]*U + Mx[i][1]*V) % q for i in range(3)]
        for idx in sch[1:]:
            if kind(idx) == 'full': g = [p5(x) for x in fl]; fl = [sum(Mx[i][j]*g[j] for j in range(3)) % q for i in range(3)]
            else: g0 = p5(fl[0]); fl = [Mx[i][0]*g0 % q for i in range(3)]
        return fl[0]
    val = run(u, np.ones(q, dtype=np.int64))
    inf = int(run(np.array([1]), np.array([0]))[0])
    zs = int((val == 0).sum()) + (1 if inf == 0 else 0)
    log('pointwise enumeration over the q+1 projective points: zeros of the output top form = %d (finite %d, at infinity %d)' % (zs, int((val == 0).sum()), 1 if inf == 0 else 0))
