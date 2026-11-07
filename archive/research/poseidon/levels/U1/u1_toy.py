"""U1 toy-field experiments. Same structure as the target over F_q (gcd(5,q-1)=1), random constants + random MDS (all minors nonzero) or Cauchy.
Exhaustive over all q^2 inputs where stated. Single process. Run: python u1_toy.py > u1_toy_output.txt"""
import sys, random, time
import numpy as np
T0 = time.time()
IDXS = [0, 1, 2, 3, 4, 5, 60, 61, 62, 63]

def isprime(n):
    return n > 1 and all(n % k for k in range(2, int(n ** .5) + 1))
def two_adic(q):
    n = q - 1; k = 0
    while n % 2 == 0: n //= 2; k += 1
    return k

def make_params(q, seed, cauchy=False):
    rng = random.Random(seed * 1000003 + q)
    while True:
        if cauchy:
            xs = [rng.randrange(q) for _ in range(3)]; ys = [rng.randrange(q) for _ in range(3)]
            if len(set(xs)) < 3 or len(set(ys)) < 3 or any((x + y) % q == 0 for x in xs for y in ys): continue
            M = [[pow(x + y, q - 2, q) for y in ys] for x in xs]
        else:
            M = [[rng.randrange(1, q) for _ in range(3)] for _ in range(3)]
        ok = all(M[i][j] for i in range(3) for j in range(3))
        for i in range(3):
            for k in range(i + 1, 3):
                for j in range(3):
                    for l in range(j + 1, 3):
                        if (M[i][j] * M[k][l] - M[i][l] * M[k][j]) % q == 0: ok = False
        det = (M[0][0] * (M[1][1] * M[2][2] - M[1][2] * M[2][1]) - M[0][1] * (M[1][0] * M[2][2] - M[1][2] * M[2][0]) + M[0][2] * (M[1][0] * M[2][1] - M[1][1] * M[2][0])) % q
        if ok and det: break
    rc = {idx: [rng.randrange(q) for _ in range(3)] for idx in IDXS}
    cap = (1 << 65) % q
    return dict(q=q, M=M, rc=rc, cap=cap, seed=seed)

def sched(r): return [0, 1, 2, 3] + list(range(4, 4 + r)) + [60, 61, 62, 63]
def is_full(idx): return idx < 4 or idx >= 60
def rc_for(par, idx):
    # partial rounds beyond 4,5 are never used (r <= 2)
    return par['rc'][idx]

def p5(x, q):
    x2 = x * x % q; x4 = x2 * x2 % q
    return x4 * x % q
def mds(s, M, q):
    return [(M[i][0] * s[0] + M[i][1] * s[1] + M[i][2] * s[2]) % q for i in range(3)]
def rounds(s, par, idxs):
    q = par['q']; M = par['M']
    for idx in idxs:
        c = rc_for(par, idx)
        s = [(s[i] + c[i]) % q for i in range(3)]
        s[0] = p5(s[0], q)
        if is_full(idx):
            s[1] = p5(s[1], q); s[2] = p5(s[2], q)
        s = mds(s, M, q)
    return s

def hash_grid_nk_rho(par, r, c00=None, c01=None, cap=None, c02=None, c1_0=None, chunk=1 << 21):
    """returns array H[nk, rho] (int32) over the whole q x q grid."""
    q = par['q']; out = np.zeros((q, q), dtype=np.int32)
    rc = {k: list(v) for k, v in par['rc'].items()}
    if c00 is not None: rc[0][0] = c00
    if c01 is not None: rc[0][1] = c01
    if c02 is not None: rc[0][2] = c02
    if c1_0 is not None: rc[1][0] = c1_0
    p2 = dict(par); p2['rc'] = rc
    cp = par['cap'] if cap is None else cap
    rows = max(1, chunk // q)
    rho = np.arange(q, dtype=np.int64)[None, :]
    for lo in range(0, q, rows):
        hi = min(q, lo + rows)
        nk = np.arange(lo, hi, dtype=np.int64)[:, None]
        s = [np.broadcast_to(nk, (hi - lo, q)).copy(), np.broadcast_to(rho, (hi - lo, q)).copy(), np.full((hi - lo, q), cp, dtype=np.int64)]
        out[lo:hi] = rounds(s, p2, sched(r))[0]
    return out

def hash_grid_AB(par, r, K, rows_subset=None):
    """H_K(A,B) = rounds 1.. applied to M*(A,B,K); returns q x q array over (A,B)."""
    q = par['q']; M = par['M']
    A = np.arange(q, dtype=np.int64)[:, None]; B = np.arange(q, dtype=np.int64)[None, :]
    s = [(M[i][0] * A + M[i][1] * B + M[i][2] * K) % q for i in range(3)]
    s = [np.broadcast_to(x, (q, q)).copy() for x in s]
    return rounds(s, par, sched(r)[1:])[0]

def stats(counts, q):
    n = q * q
    pairs = int((counts.astype(np.int64) * (counts - 1)).sum() // 2)
    exp = n * (n - 1) / 2 / q
    return pairs / exp, counts.var() / counts.mean(), int((counts > 0).sum())

print('=== TOY SETUP ===')
for q in (257, 769, 1009, 4099, 12289, 65537, 1000003):
    print(' q=%d prime=%s gcd(5,q-1)=%d q mod 4=%d 2-adicity=%d' % (q, isprime(q), np.gcd(5, q - 1), q % 4, two_adic(q)))

print('\n=== T1 (Q1): X2 exhaustively: (nk,rho)->(A,B) bijection and H(A,B) == hash ===')
for q, seeds in ((257, 4), (769, 3), (1009, 3), (4099, 1)):
    for seed in range(seeds):
        par = make_params(q, seed)
        c0 = par['rc'][0]
        a = (np.arange(q, dtype=np.int64) + c0[0]) % q; b = (np.arange(q, dtype=np.int64) + c0[1]) % q
        Aax = p5(a, q); Bax = p5(b, q)
        bij = len(np.unique(Aax)) == q and len(np.unique(Bax)) == q
        K = p5((par['cap'] + c0[2]) % q, q)
        for r in (1, 2):
            Hn = hash_grid_nk_rho(par, r)
            HAB = hash_grid_AB(par, r, K)
            # compare: Hn[nk, rho] == HAB[A(nk), B(rho)]
            comp = HAB[Aax[:, None], Bax[None, :]]
            bad = int((comp != Hn).sum())
            # 3-lane output distinct (X1)? only on q=257 (cheap) - done below
            print(' q=%d seed=%d r=%d: x->(x+c)^5 bijective on both axes: %s ; mismatches H(A,B) vs hash over all %d inputs: %d' % (q, seed, r, bij, q * q, bad))
# X1 on 257
par = make_params(257, 0)
for r in (1, 2):
    q = 257
    nk = np.repeat(np.arange(q, dtype=np.int64), q); rho = np.tile(np.arange(q, dtype=np.int64), q)
    s = rounds([nk, rho, np.full(q * q, par['cap'], dtype=np.int64)], par, sched(r))
    key = (s[0] * q + s[1]) * q + s[2]
    print(' q=257 r=%d: distinct full 3-lane outputs %d of %d (X1: bijection of the state)' % (r, len(np.unique(key)), q * q))
# sampled for bigger q (pure python)
for q in (12289, 65537, 1000003):
    par = make_params(q, 0); rng = random.Random(7); c0 = par['rc'][0]; bad = 0; N = 2000
    K = pow((par['cap'] + c0[2]) % q, 5, q)
    for _ in range(N):
        nk, rho = rng.randrange(q), rng.randrange(q)
        for r in (1, 2):
            full = rounds([nk, rho, par['cap']], par, sched(r))[0]
            A = pow((nk + c0[0]) % q, 5, q); B = pow((rho + c0[1]) % q, 5, q)
            via = rounds(mds([A, B, K], par['M'], q), par, sched(r)[1:])[0]
            bad += (full != via)
    print(' q=%d sampled %d inputs x r=1,2: mismatches %d' % (q, N, bad))

print('\n=== T2 (Q3): do c00,c01 matter? complete fibre (count-per-output) arrays after changing them ===')
for q in (257, 769, 1009):
    for seed in range(3):
        par = make_params(q, seed); rng = random.Random(seed + 99)
        for r in (1, 2):
            H0 = hash_grid_nk_rho(par, r); n0 = np.bincount(H0.ravel(), minlength=q)
            d0, d1 = rng.randrange(1, q), rng.randrange(1, q)
            c00n = (par['rc'][0][0] + d0) % q; c01n = (par['rc'][0][1] + d1) % q
            H1 = hash_grid_nk_rho(par, r, c00=c00n, c01=c01n)
            n1 = np.bincount(H1.ravel(), minlength=q)
            shifted = np.roll(np.roll(H0, -d0, axis=0), -d1, axis=1)   # H0[nk+d0, rho+d1] at [nk,rho]
            ptwise = bool((shifted == H1).all())
            # change only c00
            H2 = hash_grid_nk_rho(par, r, c00=c00n); n2 = np.bincount(H2.ravel(), minlength=q)
            # change c02 and c1,0 (controls: expected to change)
            H3 = hash_grid_nk_rho(par, r, c02=(par['rc'][0][2] + d0) % q); n3 = np.bincount(H3.ravel(), minlength=q)
            H4 = hash_grid_nk_rho(par, r, c1_0=(par['rc'][1][0] + d0) % q); n4 = np.bincount(H4.ravel(), minlength=q)
            # capacity <-> c02 equivalence
            H5 = hash_grid_nk_rho(par, r, cap=(par['cap'] + d1) % q, c02=(par['rc'][0][2] - d1) % q)
            print(' q=%d seed=%d r=%d: per-output counts identical after changing (c00,c01): %s ; after c00 only: %s ; pointwise H1(x)=H0(x+d): %s | controls: change c02 -> identical %s (sorted-multiset identical %s); change c10 -> identical %s | cap+d & c02-d gives the same function: %s' % (
                q, seed, r, bool((n0 == n1).all()), bool((n0 == n2).all()), ptwise, bool((n0 == n3).all()), bool((np.sort(n0) == np.sort(n3)).all()), bool((n0 == n4).all()), bool((H0 == H5).all())))

print('\n=== T3 (Q2 toy): capacity scan. K = (cap+c02)^5 runs over all of F_q; fibre statistics of H_K(A,B) ===')
def char_i(q):
    return [x for x in range(q) if x * x % q == q - 1]
for q, allK in ((257, True), (769, False)):
    for seed in range(3 if q == 257 else 2):
        par = make_params(q, seed)
        fp = [0, 1, q - 1] + (char_i(q) if q % 4 == 1 else [])
        Ks = list(range(q)) if allK else sorted(set(fp + random.Random(5).sample(range(q), 12)))
        for r in (1, 2):
            res = {}
            for K in Ks:
                H = hash_grid_AB(par, r, K)
                res[K] = stats(np.bincount(H.ravel(), minlength=q), q)
            cr = np.array([v[0] for v in res.values()]); vr = np.array([v[1] for v in res.values()])
            cov = all(v[2] == q for v in res.values())
            print(' q=%d seed=%d r=%d: %d K values; collision ratio min %.4f max %.4f mean %.4f; var/mean min %.3f max %.3f; image covers all q for every K: %s' % (q, seed, r, len(Ks), cr.min(), cr.max(), cr.mean(), vr.min(), vr.max(), cov))
            print('     special K: ' + ', '.join('K=%s ratio %.4f' % (('0' if K == 0 else '1' if K == 1 else '-1' if K == q - 1 else 'i-ish%d' % K), res[K][0]) for K in fp if K in res))
            worst = max(res, key=lambda k: abs(res[k][0] - 1))
            print('     most deviating K=%d ratio %.4f (spread of the ratio over K is %s)' % (worst, res[worst][0], 'within a few sigma of a random function' if abs(res[worst][0] - 1) < 0.01 else 'LARGE'))

print('\n=== T4 (Q5): degree-drop directions: brute force over all q+1 directions (u:v) ===')
def deg_poly(vals):
    # vals at t=0..n; q large enough
    q = None
    v = vals[:]
    for k in range(len(vals)):
        if all(x == v[0] for x in v): return k if (v[0] != 0 or k == 0) else -1
        v = [(v[j + 1] - v[j]) for j in range(len(v) - 1)]
    return None
def deg_line(par, u, v, a, b, upto, npts):
    q = par['q']; vals = [[], [], []]
    for t in range(npts):
        s = rounds([(a + u * t) % q, (b + v * t) % q, par['cap']], par, list(range(upto + 1)))
        for i in range(3): vals[i].append(s[i])
    q_ = par['q']
    res = []
    for i in range(3):
        v_ = vals[i]
        d = None
        for k in range(len(v_)):
            if all(x % q_ == v_[0] % q_ for x in v_): d = k if (v_[0] % q_ != 0 or k == 0) else -1; break
            v_ = [(v_[j + 1] - v_[j]) % q_ for j in range(len(v_) - 1)]
        res.append(d)
    return res
tot = 0
for q in (257, 769, 1009, 4099, 12289):
    for seed in range(5):
        for cauchy in (False, True) if seed < 2 else (False,):
            par = make_params(q, seed, cauchy)
            rng = random.Random(seed + 5)
            a, b = rng.randrange(q), rng.randrange(q)
            dirs = [(1, v) for v in range(q)] + [(0, 1)]
            drops = [[], [], []]
            for (u, v) in dirs:
                dg = deg_line(par, u, v, a, b, 0, 9)
                for i in range(3):
                    if dg[i] < 5: drops[i].append(((u, v), dg[i]))
            # R1.M degrees on the drop lines
            r1 = []
            for i in range(3):
                for (dr, dgv) in drops[i]:
                    r1.append(deg_line(par, dr[0], dr[1], a, b, 1, 28))
            both = len(set(d_[0] for d_ in drops[0]) & set(d_[0] for d_ in drops[1])) + len(set(d_[0] for d_ in drops[0]) & set(d_[0] for d_ in drops[2])) + len(set(d_[0] for d_ in drops[1]) & set(d_[0] for d_ in drops[2]))
            # predicted direction
            M = par['M']; pred = []
            for i in range(3):
                # solve M_i0 u^5 + M_i1 v^5 = 0 : take v=1, u^5 = -M_i1/M_i0
                target = (-M[i][1] * pow(M[i][0], q - 2, q)) % q
                pred.append([u for u in range(q) if pow(u, 5, q) == target])
            ok = all(len(drops[i]) == 1 and (drops[i][0][0][0] * pow(drops[i][0][0][1], q - 2, q)) % q in pred[i] for i in range(3))
            tot += 1
            print(' q=%d seed=%d %s: drop directions per lane %s (u:v, degree after R0.M) ; directions shared by two lanes: %d ; predicted u=(-M_i1/M_i0)^(1/5): %s match=%s ; degrees after R1.M on drop lines %s' % (
                q, seed, 'cauchy' if cauchy else 'random', [[(d_[0], d_[1]) for d_ in drops[i]] for i in range(3)], both, [p_ for p_ in pred], ok, r1))
print(' (total configurations: %d)' % tot)
print(' control with gcd(5,q-1)=5 (x^5 NOT a bijection): number of drop directions per lane = number of 5th roots of -M_i1/M_i0 in F_q (0 or 5):')
for q in (11, 31, 41, 61, 71, 101):
    for seed in range(3):
        par = make_params(q, seed); M = par['M']
        cnt = []
        for i in range(3):
            target = (-M[i][1] * pow(M[i][0], q - 2, q)) % q
            cnt.append(sum(1 for u in range(q) if pow(u, 5, q) == target))
        print('   q=%d seed=%d: directions with u/v at which lane i drops (v=1) counts %s' % (q, seed, cnt))

print('\n=== T5 (Q8 toy): R1.C-zero loci on P0, exhaustive ===')
for q in (257, 769, 1009):
    for seed in range(3):
        par = make_params(q, seed); M = par['M']; c1 = par['rc'][1]; c0 = par['rc'][0]
        K = pow((par['cap'] + c0[2]) % q, 5, q)
        A = np.arange(q, dtype=np.int64)[:, None]; B = np.arange(q, dtype=np.int64)[None, :]
        z = [((M[i][0] * A + M[i][1] * B + M[i][2] * K + c1[i]) % q == 0) for i in range(3)]
        z = [np.broadcast_to(x, (q, q)) for x in z]
        nz = z[0].astype(int) + z[1].astype(int) + z[2].astype(int)
        print(' q=%d seed=%d: #(A,B) with exactly one zero lane %d (expect 3q=%d minus overlaps), exactly two zero lanes %d (expect 3), three %d; per-lane zero locus size %s (expect q each)' % (q, seed, int((nz == 1).sum()), 3 * q, int((nz == 2).sum()), int((nz == 3).sum()), [int(x.sum()) for x in z]))

print('\n=== T6 (Q7 toy): the 25 fixed-point pairs, q=257 (5 fixed points) ===')
q = 257
for seed in range(3):
    par = make_params(q, seed); M = par['M']; c0 = par['rc'][0]; c1 = par['rc'][1]
    fixed = [x for x in range(q) if pow(x, 5, q) == x]
    K = pow((par['cap'] + c0[2]) % q, 5, q)
    st = {(al, be): mds([al, be, K], M, q) for al in fixed for be in fixed}
    hs = {k: rounds(v, par, sched(1)[1:])[0] for k, v in st.items()}
    # lanes that land in the fixed set
    inset = sum(1 for v in st.values() for x in v if x in fixed)
    inset1 = sum(1 for v in st.values() for i in range(3) if (v[i] + c1[i]) % q in fixed)
    zero_r1 = sum(1 for v in st.values() for i in range(3) if (v[i] + c1[i]) % q == 0)
    # collisions among the 25
    from collections import Counter
    cc = Counter(hs.values())
    print(' seed=%d: fixed points %s ; lanes of R0.M-out in the fixed set: %d of 75 (random expectation 75*5/257=%.1f) ; R1.C-in lanes in the fixed set %d ; zero %d ; hash collisions among the 25: %d ; repeated lane values among the 25 states: %d' % (
        seed, fixed, inset, 75 * 5 / 257, inset1, zero_r1, sum(1 for v in cc.values() if v > 1), 75 - len({(i, v[i]) for v in st.values() for i in range(3)})))

print('\n=== T7: gcd(5,q-1)=5 control: round-0 reparametrisation stops being a bijection ===')
for q in (11, 31, 41, 61):
    par = make_params(q, 0); c0 = par['rc'][0]
    A = {pow((x + c0[0]) % q, 5, q) for x in range(q)}
    print(' q=%d: |image of x->(x+c)^5| = %d of %d (expected (q-1)/5+1 = %d) -> (nk,rho)->(A,B) is %d-to-1 away from 0' % (q, len(A), q, (q - 1) // 5 + 1, 5))

print('\ntotal time %.1f s' % (time.time() - T0))
