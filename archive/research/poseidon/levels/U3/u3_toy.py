"""U3 toy experiments over F_q (q with gcd(5,q-1)=1). Exhaustive over all q^2 inputs (and all q^3 states for small q).
Single process, numpy int64."""
import sys, random, itertools, time
import numpy as np
from math import gcd
def out(*a): print(*a); sys.stdout.flush()

def mk_toy(q, seed):
    rng = random.Random(seed)
    while True:
        Mx = [[rng.randrange(1, q) for _ in range(3)] for _ in range(3)]
        # MDS: all square minors nonzero
        ok = all(Mx[i][j] % q for i in range(3) for j in range(3))
        for r1, r2 in itertools.combinations(range(3), 2):
            for c1, c2 in itertools.combinations(range(3), 2):
                ok &= (Mx[r1][c1]*Mx[r2][c2]-Mx[r1][c2]*Mx[r2][c1]) % q != 0
        det = (Mx[0][0]*(Mx[1][1]*Mx[2][2]-Mx[1][2]*Mx[2][1]) - Mx[0][1]*(Mx[1][0]*Mx[2][2]-Mx[1][2]*Mx[2][0]) + Mx[0][2]*(Mx[1][0]*Mx[2][1]-Mx[1][1]*Mx[2][0])) % q
        if ok and det: break
    RC = [[rng.randrange(q) for _ in range(3)] for _ in range(64)]
    return np.array(Mx, dtype=np.int64), np.array(RC, dtype=np.int64)

def pow5(x, q): 
    x2 = x*x % q
    return x2*x2 % q * x % q
def mds(M, s, q):   # s: (3,n)
    return (M @ s) % q
def full(M, RC, idx, s, q):
    s = (s + RC[idx][:, None]) % q
    return mds(M, pow5(s, q), q)
def part(M, RC, idx, s, q):
    s = (s + RC[idx][:, None]) % q
    s = s.copy(); s[0] = pow5(s[0], q)
    return mds(M, s, q)
def pairs_eq(keys):
    c = np.bincount(keys) if keys.max() < 5_000_000_000 and keys.max() < 2**28 else None
    if c is None:
        _, c = np.unique(keys, return_counts=True)
    c = c.astype(np.int64)
    return int((c*(c-1)//2).sum())
def inputs(q):
    nk, rho = np.meshgrid(np.arange(q, dtype=np.int64), np.arange(q, dtype=np.int64), indexing='ij')
    return nk.ravel(), rho.ravel()

def trajectory(q, seed, rmax=5):
    M, RC = mk_toy(q, seed)
    nk, rho = inputs(q)
    cap = pow(2, 65, q)
    s = np.vstack([nk, rho, np.full_like(nk, cap)])
    lane0 = {}
    for i in range(4):
        s = full(M, RC, i, s, q); lane0[i] = s[0].copy()
    states = {3: s.copy()}
    for k in range(rmax):
        s = part(M, RC, 4+k, s, q); lane0[4+k] = s[0].copy(); states[4+k] = s.copy()
    return M, RC, lane0, states

def final_out(M, RC, q, s_after_partial):
    s = s_after_partial
    for i in range(60, 64): s = full(M, RC, i, s, q)
    return s

def run(q, seeds, label=""):
    n = q*q
    exp = q*q*(q*q-1)/(2*q)
    out("\n--- toy q=%d (q-1=%d 2-adic %d) seeds=%s ---" % (q, q-1, ((q-1) & -(q-1)).bit_length()-1, seeds))
    for seed in seeds:
        M, RC, lane0, states = trajectory(q, seed)
        out(" seed %d" % seed)
        # Q3: equal lane0 pairs after each round, vs exp
        for k in (0,1,2,3,4,5):
            N = pairs_eq(lane0[k]); 
            cnt = np.bincount(lane0[k], minlength=q)
            out("   lane0 after R%d: equal pairs %d ; expected random %.1f ; ratio %.4f ; fibre sizes min/max %d/%d var/mean %.3f" % (k, N, exp, N/exp, cnt.min(), cnt.max(), cnt.var()/cnt.mean()))
        N3 = pairs_eq(lane0[3])
        # joint equalities R3&R4, R3&R4&R5 ...
        keys = lane0[3].copy(); tot = N3
        for k in (4,5,6,7):
            keys = keys*q + lane0[k]
            N = pairs_eq(keys)
            out("   lane0 equal at all of R3..R%d: %d ; N3/q^%d = %.1f ; ratio %.3f" % (k, N, k-3, N3/q**(k-3), N/(N3/q**(k-3))))
        # outputs for r = 0..5 (r=0: straight to R60 after R3)
        for r in range(0, 6):
            s = states[3] if r == 0 else states[3+r]
            o = final_out(M, RC, q, s)
            # pairs with equal lane0 at R3 and equal output lane0
            key = lane0[3]*q + o[0]
            Nj = pairs_eq(key)
            Nout = pairs_eq(o[0])
            out("   r=%d: pairs equal at R3 lane0 AND output lane0: %d (expected N3/q = %.1f, ratio %.3f) ; all output-equal pairs %d (ratio to exp %.4f)" % (r, Nj, N3/q, Nj/(N3/q), Nout, Nout/exp))

def trail_pairs(q, seed):
    """pairs of R3-states whose difference lies on the r=2 trail line (0,M02,-M01); compare output collisions with random."""
    M, RC, lane0, states = trajectory(q, seed, rmax=2)
    s3 = states[3]
    M01, M02 = int(M[0][1]), int(M[0][2])
    d = np.array([0, M02, (-M01) % q], dtype=np.int64)
    n = q*q
    enc = (s3[0]*q + s3[1])*q + s3[2]
    order = np.argsort(enc); encs = enc[order]
    # outputs for r=1 (after R4) and r=2 (after R5)
    o1 = final_out(M, RC, q, states[4])[0]; o2 = final_out(M, RC, q, states[5])[0]
    pairs = 0; eq1 = 0; eq2 = 0; eqR4 = 0; eqR5 = 0
    for t in range(1, q):
        sh = (s3 + (t*d % q)[:, None]) % q
        e2 = (sh[0]*q + sh[1])*q + sh[2]
        pos = np.searchsorted(encs, e2); pos[pos >= n] = n-1
        hit = encs[pos] == e2
        j = order[pos[hit]]; i = np.nonzero(hit)[0]
        pairs += len(i)
        eq1 += int((o1[i] == o1[j]).sum()); eq2 += int((o2[i] == o2[j]).sum())
        eqR4 += int((states[4][0][i] == states[4][0][j]).sum()); eqR5 += int((states[5][0][i] == states[5][0][j]).sum())
    pairs //= 2; eq1//=2; eq2//=2; eqR4//=2; eqR5//=2
    N3 = pairs_eq(lane0[3])
    out("  q=%d seed %d: ordered-by-t trail pairs on the R3 surface: %d (random expectation ~ n*(q-1)/q^3*n/2 = %.1f); lane0 equal after R4 for %d of them, after R5 for %d ; output equal r=1: %d, r=2: %d (random 1/q rate -> %.1f)" % (q, seed, pairs, n*n*(q-1)/q**3/2, eqR4, eqR5, eq1, eq2, pairs/q))
    return pairs

def trail_survival(q, seed):
    """Exhaustive over all q^3 states: for r partial rounds, pairs of distinct states with equal S-box-input lane 0 at every partial round."""
    M, RC = mk_toy(q, seed)
    g = np.arange(q, dtype=np.int64)
    a, b, c = np.meshgrid(g, g, g, indexing='ij')
    s = np.vstack([a.ravel(), b.ravel(), c.ravel()])
    n = q**3
    keys = np.zeros(n, dtype=np.int64)
    res = []
    for r in range(1, 5):
        u = (s[0] + RC[3+r][0]) % q          # lane-0 S-box input of partial round r
        keys = keys*q + u
        s = part(M, RC, 3+r, s, q)
        N = pairs_eq(keys) if q**r < 2**28 else None
        _, cnt = np.unique(keys, return_counts=True); cnt = cnt.astype(np.int64)
        N = int((cnt*(cnt-1)//2).sum())
        pred = n*(q**(3-r)-1)//2 if r <= 3 else 0
        res.append((r, N, pred))
    out("  q=%d seed %d: all-state pairs with equal lane-0 S-box input in every one of r partial rounds: %s   [r, measured, predicted n*(q^(3-r)-1)/2 (r<=3), 0 for r>=3]" % (q, seed, res))

if __name__ == "__main__":
    out("gcd(5, q-1)=1 checks:", {q: gcd(5, q-1) for q in (17, 23, 37, 97, 193, 257, 449, 769, 1009, 1000003, 12289)})
    t0 = time.time()
    for q in (257, 769, 1009):
        run(q, [1, 2, 3] if q == 257 else [1])
    for q in (97, 193, 257, 449):
        for sd in (1, 2, 3):
            trail_pairs(q, sd)
    for q in (17, 23, 37):
        for sd in (1, 2):
            trail_survival(q, sd)
    out("time %.1fs" % (time.time()-t0))
