# E8: probability that an S-box input is 0 / a fixed point; toy checks; and AIMED hits on the real field (solve for inputs).
import random, math
from common import *
from toy import *
from sympy.polys.galoistools import gf_factor
from sympy.polys.domains import ZZ
rnd = random.Random(88)
i_ = I_
print("real field: live S-box inputs r=1: 24 (R0 lanes 0,1; R1-R3: 9; R4: 1; R60-63: 12), r=2: 25.  per-input hit prob 5/p:")
for n in (24, 25):
    print(" n=%d: n*5/p = 2^%.3f ; zero only: n/p = 2^%.3f" % (n, math.log2(n*5/P), math.log2(n/P)))
print("\n=== toys: fraction of inputs with at least one live S-box input in {0,+-1,+-i} (5 values; 3 values {0,+-1} if q=3 mod 4) ===")

def trial(q, r, exhaustive, nsamp=4_000_000):
    T = make_toy(q, 4242+q+r, r)
    ii = sqrt_m1(q)
    st = np.array(sorted({0, 1, q-1} | ({ii, q-ii} if ii else set())))
    if exhaustive:
        nk, rho = np.meshgrid(np.arange(q), np.arange(q), indexing='ij')
        nk = nk.ravel(); rho = rho.ravel()
    else:
        g = np.random.default_rng(q+r)
        nk = g.integers(0, q, nsamp); rho = g.integers(0, q, nsamp)
    rec = []
    toy_trace(T, nk, rho, rec)
    anyhit = np.zeros(len(nk), bool); anyzero = np.zeros(len(nk), bool)
    perpos = []; n = 0
    for tag, ri, s in rec:
        if tag != 'sin': continue
        for l in (range(3) if T['full'][ri] else [0]):
            if ri == 0 and l == 2: continue
            h = np.isin(s[l], st)
            anyhit |= h; anyzero |= (s[l] == 0); perpos.append(h.mean()); n += 1
    s_ = len(st)
    return len(nk), anyhit.mean(), 1-(1-s_/q)**n, anyzero.mean(), 1-(1-1/q)**n, n, (min(perpos), max(perpos)), s_/q

for q, ex in ((257, True), (769, True), (1009, True), (4099, False), (12289, False), (65537, False), (786433, False), (1000003, False)):
    for r in (1, 2):
        N, hit, pred, z, zp, n, rng_, sp = trial(q, r, ex)
        print("q=%7d r=%d %s N=%8d live=%d  P(any in set)=%.5f predicted 1-(1-%d/q)^n=%.5f | P(any zero)=%.5f predicted %.5f | per-position hit rate range %.5f..%.5f (set/q=%.5f)" % (q, r, "exh" if ex else "smp", N, n, hit, round(sp*q), pred, z, zp, rng_[0], rng_[1], sp))

print("\n=== real field: AIMED hits. Work in (A,B) = ((nk+c00)^5,(rho+c01)^5); state after R0.M = M*(A,B,K) ===")
K = pow(PR.CAPACITY+PR.RC[0][2], 5, P)
d5 = inv(5, P-1)
def fromAB(A, B): return (pow(A, d5, P)-PR.RC[0][0]) % P, (pow(B, d5, P)-PR.RC[0][1]) % P
def after_round(s, idx, full=True):
    s = [(s[j]+PR.RC[idx][j]) % P for j in range(3)]
    s = [pow(x, 5, P) if (full or j == 0) else x for j, x in enumerate(s)]
    return matvec(PR.MDS, s)
def sbox_inputs(nk, rho, r=1):
    s = [nk, rho, PR.CAPACITY]; out = []
    for idx in PR.schedule(r):
        full = idx < 4 or idx >= 60
        s = [(s[j]+PR.RC[idx][j]) % P for j in range(3)]
        for j in (range(3) if full else [0]):
            if idx == 0 and j == 2: continue
            out.append(("R%d.l%d" % (idx, j), s[j]))
        s = [pow(x, 5, P) if (full or j == 0) else x for j, x in enumerate(s)]
        s = matvec(PR.MDS, s)
    return out
def state_after(A, B, nrounds_after_R0):
    s = matvec(PR.MDS, [A, B, K])
    for idx in range(1, 1+nrounds_after_R0): s = after_round(s, idx)
    return s
for j in range(3):
    B = rnd.randrange(P); m = PR.MDS[j]
    A = (-(m[1]*B+m[2]*K+PR.RC[1][j])*inv(m[0])) % P
    nk, rho = fromAB(A, B)
    vals = dict(sbox_inputs(nk, rho))
    print("R1 lane %d input zero by solving a linear equation: S-box input at R1.l%d = %d ; hash computed: %s" % (j, j, vals["R1.l%d" % j], hex(PR.hash_reduced(nk, rho, 1))[:12]))
def lagrange(xs, ys):
    n = len(xs); coef = [0]*n
    for i in range(n):
        num = [1]; den = 1
        for j in range(n):
            if j == i: continue
            new = [0]*(len(num)+1)
            for k, c in enumerate(num):
                new[k+1] = (new[k+1]+c) % P
                new[k] = (new[k]-xs[j]*c) % P
            num = new
            den = den*(xs[i]-xs[j]) % P
        f = ys[i]*inv(den % P) % P
        for k in range(n): coef[k] = (coef[k]+f*num[k]) % P
    return coef
def roots_in_B(A, lane, level, target):
    deg = 5 if level == 2 else 25
    xs = list(range(1, deg+2)); ys = []
    for B in xs:
        s = state_after(A, B, level-1)
        ys.append((s[lane]+PR.RC[level][lane]-target) % P)
    co = lagrange(xs, ys)
    while co and co[-1] == 0: co.pop()
    hi = list(reversed(co))
    lc, fl = gf_factor(hi, P, ZZ)
    return [(-f[1]) % P for f, e in fl if len(f) == 2]
for level, lane, name in ((2, 0, "R2.l0"), (2, 2, "R2.l2"), (3, 1, "R3.l1")):
    for target, tn in ((0, "0"), (1, "1"), (i_, "i")):
        found = []; tries = 0
        while not found and tries < 60:
            tries += 1; A = rnd.randrange(P); found = [(A, B) for B in roots_in_B(A, lane, level, target)]
        A, B = found[0]; nk, rho = fromAB(A, B); v = dict(sbox_inputs(nk, rho))[name]
        print("%s input = %s : found on try %d, check via implementation path: S-box input == target: %s" % (name, tn, tries, v == target % P))
cnts = []
for _ in range(40):
    A = rnd.randrange(P); cnts.append(len(roots_in_B(A, 0, 2, 0)))
print("R2.l0 = 0: number of roots B for 40 random A:", sorted(cnts), "mean", sum(cnts)/len(cnts))
cnts = []
for _ in range(12):
    A = rnd.randrange(P); cnts.append(len(roots_in_B(A, 0, 3, 0)))
print("R3.l0 = 0: number of roots B (degree-25 poly) for 12 random A:", sorted(cnts), "mean", sum(cnts)/len(cnts))
def jac(nk, rho, r=1):
    s = [nk, rho, PR.CAPACITY]; t = [[1, 0], [0, 1], [0, 0]]; snaps = []
    for idx in PR.schedule(r):
        full = idx < 4 or idx >= 60
        s = [(s[j]+PR.RC[idx][j]) % P for j in range(3)]
        for j in (range(3) if full else [0]):
            d = 5*pow(s[j], 4, P) % P
            t[j] = [d*t[j][0] % P, d*t[j][1] % P]; s[j] = pow(s[j], 5, P)
        s = matvec(PR.MDS, s)
        t = [[sum(PR.MDS[a][b]*t[b][c] for b in range(3)) % P for c in range(2)] for a in range(3)]
        snaps.append((idx, [row[:] for row in t]))
    return s, t, snaps
def rank2(t):
    mins = [(t[a][0]*t[b][1]-t[a][1]*t[b][0]) % P for a in range(3) for b in range(a+1, 3)]
    if any(mins): return 2
    return 1 if any(any(r) for r in t) else 0
A = None
while A is None:
    A = rnd.randrange(P); rts = roots_in_B(A, 0, 2, 0)
    if not rts: A = None
B = rts[0]; nk, rho = fromAB(A, B)
s, t, snaps = jac(nk, rho)
print("\nJacobian (state wrt nk,rho) rank after each round at a point where R2.l0 S-box input = 0:", [(idx, rank2(tt)) for idx, tt in snaps])
print("gradient of hash output wrt (nk,rho) at that point is zero?", all(x == 0 for x in t[0]))
print("(the S-box derivative at that lane is 5*0^4 = 0; the other two lanes still carry derivative.)")
