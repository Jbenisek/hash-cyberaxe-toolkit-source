"""Degrees, dependence and support of the target as functions of (nk, rho). Exact over Fp.
Run: python facts_degree.py  (prints report; ~ a few minutes; single process)
Parts:
 A  generic degree table per step (symbolic, MDS dense)  [DERIVED]
 B  leading-coefficient tracker on random lines nk=a+u t, rho=b+v t, all rounds, r=1,2  [PROVED per line if lc != 0]
 C  exact univariate line polynomials (Kronecker multiplication) up to the deepest round affordable: degree + density
 D  special directions (round-0 top-form cancellation) followed through the rounds exactly
 E  exact bivariate expansion for rounds 0,1,2: monomial counts
 F  forward/reverse mode derivatives: which lanes depend on (nk,rho), Jacobian rank, which lanes influence the output
"""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
P, RC, MDS, CAP = R.P, R.RC, R.MDS, R.CAPACITY
M = [list(r) for r in MDS]
random.seed(20261012)
T0 = time.time()
def log(*a): print(*a, flush=True)
def inv(a): return pow(a, P-2, P)
D5 = pow(5, -1, P-1)

def steps_of(r):
    """list of (round index, kind) in order"""
    return [(i, 'full') for i in range(4)] + [(i, 'partial') for i in range(4, 4+r)] + [(i, 'full') for i in range(60, 64)]

# ---------------------------------------------------------------- A generic degree table
def generic_table(r):
    # total degree in (nk,rho) of each lane after each step. Use deg for the constant lane = 0.
    d = [1, 1, 0]
    rows = [('init', list(d))]
    for idx, kind in steps_of(r):
        rows.append(('R%d C' % idx, list(d)))        # constants do not change degree (deg>=1; deg0 stays const)
        d = [5*x for x in d] if kind == 'full' else [5*d[0], d[1], d[2]]
        rows.append(('R%d S' % idx, list(d)))
        m = max(d)
        d = [m, m, m]                              # dense MDS (all entries nonzero)
        rows.append(('R%d M' % idx, list(d)))
    return rows
log('=== A generic degree per lane (total degree in nk,rho) ===')
for r in (1, 2):
    log('r =', r)
    for lab, d in generic_table(r): log('  %-8s %s' % (lab, d))

# ---------------------------------------------------------------- B leading coefficient tracker
def lc_track(r, u, v):
    """track (deg, leading coeff) of each lane along line nk=a+u t, rho=b+v t (a,b irrelevant to lc unless deg 0)."""
    a = random.randrange(P); b = random.randrange(P)
    lane = [(1, u), (1, v), (0, CAP)]
    hist = []
    for idx, kind in steps_of(r):
        lane = [(d, c) if d > 0 else (0, (c + RC[idx][i]) % P) for i, (d, c) in enumerate(lane)]
        lane = [(5*d, pow(c, 5, P)) if (kind == 'full' or i == 0) else (d, c) for i, (d, c) in enumerate(lane)]
        # careful: a degree-0 lane needs its constant added BEFORE the S-box: handled below
        new = []
        for i in range(3):
            terms = [(lane[j][0], M[i][j]*lane[j][1] % P) for j in range(3)]
            dm = max(t[0] for t in terms)
            c = sum(t[1] for t in terms if t[0] == dm) % P
            new.append((dm if c else None, c))
        if any(n[0] is None for n in new):
            hist.append((idx, 'CANCEL', new)); return hist
        lane = new
        hist.append((idx, [x[0] for x in lane]))
    return hist
# the tracker above adds the constant only to degree-0 lanes; the S-box of a constant lane must use constant+rc: fix by explicit version
def lc_track2(r, u, v):
    lane = [(1, u % P, None), (1, v % P, None), (0, CAP % P, CAP % P)]   # (deg, lc, constant-term if deg 0)
    hist = []
    for idx, kind in steps_of(r):
        lane2 = []
        for i, (d, c, _) in enumerate(lane):
            if d == 0: c = (c + RC[idx][i]) % P
            lane2.append((d, c))
        out = []
        for i, (d, c) in enumerate(lane2):
            if kind == 'full' or i == 0: out.append((5*d, pow(c, 5, P)))
            else: out.append((d, c if d else (c)))        # partial: lanes 1,2 untouched by S-box (their const rc already added if deg 0)
        new = []
        for i in range(3):
            terms = [(out[j][0], M[i][j]*out[j][1] % P) for j in range(3)]
            dm = max(t[0] for t in terms)
            c = sum(t[1] for t in terms if t[0] == dm) % P
            new.append((dm, c))
        lane = [(d, c, None) for d, c in new]
        hist.append((idx, kind, [d for d, c in new], [c == 0 for d, c in new]))
    return hist
log('\n=== B leading-coefficient tracker on random lines (exact; nonzero lc => line degree exactly this) ===')
for r in (1, 2):
    for trial in range(2):
        u, v = random.randrange(1, P), random.randrange(1, P)
        h = lc_track2(r, u, v)
        log('r=%d trial %d: final lane degrees after each round:' % (r, trial))
        for idx, kind, d, z in h: log('   R%-2d %-7s deg %s  lc-zero %s' % (idx, kind, d, z))
        log('   final output degree = %d = 5^%d? %s' % (h[-1][2][0], 8+r, h[-1][2][0] == 5**(8+r)))

# ---------------------------------------------------------------- C exact univariate line polynomials
SB = 70   # bytes per slot (560 bits) >= 2*255 + log2(n)
def pmul(a, b):
    if len(a) < len(b): a, b = b, a
    A = int.from_bytes(b''.join(c.to_bytes(SB, 'little') for c in a), 'little')
    B = int.from_bytes(b''.join(c.to_bytes(SB, 'little') for c in b), 'little')
    C = A*B
    n = len(a)+len(b)-1
    raw = C.to_bytes(n*SB + SB, 'little')
    return [int.from_bytes(raw[i*SB:(i+1)*SB], 'little') % P for i in range(n)]
def ppow5(a):
    a2 = pmul(a, a); a4 = pmul(a2, a2); return pmul(a4, a)
def padd(a, b):
    n = max(len(a), len(b)); r = [0]*n
    for i, x in enumerate(a): r[i] = x
    for i, x in enumerate(b): r[i] = (r[i]+x) % P
    return r
def pscal(a, s): return [x*s % P for x in a]
def ptrim(a):
    while len(a) > 1 and a[-1] == 0: a = a[:-1]
    return a
def pdeg(a): return len(ptrim(a))-1
def pzeros_inside(a):
    a = ptrim(a); return sum(1 for x in a if x == 0)
def line_exact(r, a, b, u, v, maxdeg, label=''):
    """apply rounds to the line polys; stop before a round whose S-box output degree would exceed maxdeg. returns per-round info."""
    lane = [[a % P, u % P], [b % P, v % P], [CAP % P]]
    info = []
    for idx, kind in steps_of(r):
        mx = max(pdeg(l) for l in lane)
        if kind == 'full': need = 5*mx
        else: need = max(5*pdeg(lane[0]), pdeg(lane[1]), pdeg(lane[2]))
        if need > maxdeg:
            info.append((idx, 'STOPPED (would reach deg %d > cap %d)' % (need, maxdeg))); break
        t = time.time()
        lane = [padd(l, [RC[idx][i]]) for i, l in enumerate(lane)]
        lane = [ppow5(l) if (kind == 'full' or i == 0) else l for i, l in enumerate(lane)]
        degs_S = [pdeg(l) for l in lane]
        new = []
        for i in range(3):
            acc = [0]
            for j in range(3): acc = padd(acc, pscal(lane[j], M[i][j]))
            new.append(ptrim(acc))
        lane = new
        info.append((idx, kind, degs_S, [pdeg(l) for l in lane], [pzeros_inside(l) for l in lane], round(time.time()-t, 1)))
        log('   ', label, 'R%d' % idx, kind, 'S-box out deg', degs_S, ' after MDS deg', [pdeg(l) for l in lane], ' zero coeffs inside', [pzeros_inside(l) for l in lane], ' (%.1fs)' % (time.time()-t))
    return info, lane
log('\n=== C exact univariate line polynomials (random line) ===')
a, b, u, v = [random.randrange(1, P) for _ in range(4)]
log('r=1 (cap deg 15625):')
inf1, lane1 = line_exact(1, a, b, u, v, 15625, 'r1')
log('r=2 (cap deg 15625):')
inf2, lane2 = line_exact(2, a, b, u, v, 15625, 'r2')

# ---------------------------------------------------------------- D special directions
log('\n=== D special directions after round 0 ===')
for i in range(3):
    ratio = (-M[i][1]*inv(M[i][0])) % P
    uv = pow(ratio, D5, P)
    uu, vv = uv, 1
    log('direction making lane %d degree-drop after round 0 (u/v=%s...):' % (i, hex(uv)[:14]))
    info, _ = line_exact(1, a, b, uu, vv, 3125, 'dir%d' % i)
    # round-0 lane degrees directly:
    lane = [[a % P, uu], [b % P, vv], [CAP % P]]
    lane = [padd(l, [RC[0][k]]) for k, l in enumerate(lane)]
    lane = [ppow5(l) for l in lane]
    l0 = [ptrim(padd(padd(pscal(lane[0], M[k][0]), pscal(lane[1], M[k][1])), pscal(lane[2], M[k][2]))) for k in range(3)]
    log('   round-0 output degrees on this line:', [pdeg(x) for x in l0], '(lane %d drops to 4; the next MDS restores the top degree)' % i)

# ---------------------------------------------------------------- E bivariate
log('\n=== E exact bivariate expansion (monomial counts) ===')
def bmul(f, g):
    h = {}
    for (i1, j1), c1 in f.items():
        for (i2, j2), c2 in g.items():
            k = (i1+i2, j1+j2); h[k] = (h.get(k, 0) + c1*c2) % P
    return {k: c for k, c in h.items() if c}
def bpow5(f):
    f2 = bmul(f, f); f4 = bmul(f2, f2); return bmul(f4, f)
def badd(f, g, s=1):
    h = dict(f)
    for k, c in g.items(): h[k] = (h.get(k, 0) + s*c) % P
    return {k: c for k, c in h.items() if c}
def bscal(f, s): return {k: c*s % P for k, c in f.items()}
def bdeg(f): return max(i+j for i, j in f)
def bsupp(f): return len(f)
state = [{(1, 0): 1}, {(0, 1): 1}, {(0, 0): CAP % P}]
for idx in range(0, 3):
    state = [badd(s, {(0, 0): RC[idx][i]}) for i, s in enumerate(state)]
    state = [bpow5(s) for s in state]
    sb = [(bdeg(s), bsupp(s), max(i for i, j in s), max(j for i, j in s)) for s in state]
    new = []
    for i in range(3):
        acc = {}
        for j in range(3): acc = badd(acc, bscal(state[j], M[i][j]))
        new.append(acc)
    state = new
    tri = lambda d: (d+1)*(d+2)//2
    log('R%d: after S-box (total deg, #monomials, deg_nk, deg_rho) per lane: %s ; after MDS #monomials %s ; full triangle for deg %d = %d' % (idx, sb, [bsupp(s) for s in state], bdeg(state[0]), tri(bdeg(state[0]))))
    if idx == 0:
        mon = sorted(state[0].keys())
        log('    round-0 lane-0 monomials (nk^i rho^j):', mon)
        log('    mixed monomials (i>0 and j>0) in round-0 output:', [m for m in mon if m[0] and m[1]])
    if idx == 1:
        # structure of support: ceil(i/5)+ceil(j/5) <= 5 ?
        ok = all(-(-i//5) + -(-j//5) <= 5 for i, j in state[0])
        full = sum(1 for i in range(26) for j in range(26) if -(-i//5) + -(-j//5) <= 5)
        log('    round-1 support obeys ceil(i/5)+ceil(j/5)<=5 :', ok, '; number of (i,j) allowed =', full, '; actual monomials', bsupp(state[0]))

# ---------------------------------------------------------------- F derivatives
log('\n=== F forward-mode Jacobian and reverse-mode influence at a random point ===')
def jac_run(r, nk, rho):
    s = [nk, rho, CAP]; J = [[1, 0], [0, 1], [0, 0]]       # d state / d (nk,rho)
    rows = [('init', list(s), [r_[:] for r_ in J])]
    states = []
    for idx, kind in steps_of(r):
        s = [(s[i]+RC[idx][i]) % P for i in range(3)]
        rows.append(('R%d C' % idx, list(s), [r_[:] for r_ in J]))
        if kind == 'full': dS = [5*pow(x, 4, P) % P for x in s]
        else: dS = [5*pow(s[0], 4, P) % P, 1, 1]
        s = [pow(s[i], 5, P) if (kind == 'full' or i == 0) else s[i] for i in range(3)]
        J = [[J[i][k]*dS[i] % P for k in range(2)] for i in range(3)]
        rows.append(('R%d S' % idx, list(s), [r_[:] for r_ in J]))
        s = [sum(M[i][j]*s[j] for j in range(3)) % P for i in range(3)]
        J = [[sum(M[i][j]*J[j][k] for j in range(3)) % P for k in range(2)] for i in range(3)]
        rows.append(('R%d M' % idx, list(s), [r_[:] for r_ in J]))
    return rows
def rank2x(rowsJ):
    # rank of 3x2 matrix over Fp
    nz = [r_ for r_ in rowsJ if any(r_)]
    if not nz: return 0
    for i in range(len(rowsJ)):
        for j in range(i+1, len(rowsJ)):
            if (rowsJ[i][0]*rowsJ[j][1]-rowsJ[i][1]*rowsJ[j][0]) % P: return 2
    return 1
for r in (1, 2):
    nk, rho = random.randrange(P), random.randrange(P)
    rows = jac_run(r, nk, rho)
    log('r=%d  (per step: which of nk/rho influence each lane [dlane/dnk != 0, dlane/drho != 0], Jacobian rank)' % r)
    for lab, s, J in rows:
        dep = ['%s%s' % ('n' if J[i][0] else '.', 'r' if J[i][1] else '.') for i in range(3)]
        log('   %-8s lane0 %s lane1 %s lane2 %s   rank %d' % (lab, dep[0], dep[1], dep[2], rank2x(J)))
    assert rows[-1][1][0] == R.hash_reduced(nk, rho, r)
# reverse mode: gradient of output wrt state after each step
def reverse_influence(r, nk, rho):
    sched = steps_of(r)
    s = [nk, rho, CAP]; trace = []
    for idx, kind in sched:
        sc = [(s[i]+RC[idx][i]) % P for i in range(3)]
        so = [pow(sc[i], 5, P) if (kind == 'full' or i == 0) else sc[i] for i in range(3)]
        trace.append((idx, kind, sc))
        s = [sum(M[i][j]*so[j] for j in range(3)) % P for i in range(3)]
    g = [1, 0, 0]       # d out / d state after last M
    res = []
    for (idx, kind, sc) in reversed(trace):
        res.append((idx, 'after-M', list(g)))
        gs = [sum(M[i][j]*g[i] for i in range(3)) % P for j in range(3)]   # grad wrt S-box outputs
        res.append((idx, 'after-S', list(gs)))
        dS = [5*pow(sc[i], 4, P) % P if (kind == 'full' or i == 0) else 1 for i in range(3)]
        g = [gs[i]*dS[i] % P for i in range(3)]                              # grad wrt after-C (= before-C)
        res.append((idx, 'before-C', list(g)))
    return res
log('reverse-mode: which lanes of the state (at each point) influence the output lane 0 (gradient nonzero?)')
for r in (1, 2):
    res = reverse_influence(r, random.randrange(P), random.randrange(P))
    log('r=%d' % r)
    for idx, lab, g in res:
        log('   R%-2d %-9s influence %s' % (idx, lab, ''.join('X' if x else '.' for x in g)))
log('\ntotal seconds %.1f' % (time.time()-T0))
