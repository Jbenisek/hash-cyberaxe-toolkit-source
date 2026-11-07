# U12 toy-field experiments (exhaustive). numpy int64; q <= 257 so products fit. Run: python u12_toy.py
import numpy as np, random, itertools, math, time
from math import gcd

out = []
def log(*a):
    m = ' '.join(str(x) for x in a)
    print(m, flush=True); out.append(m)


class Toy:
    def __init__(self, q, seed):
        rng = random.Random(seed)
        self.q = q
        while True:
            xs = [rng.randrange(q) for _ in range(3)]; ys = [rng.randrange(q) for _ in range(3)]
            if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x + y) % q for x in xs for y in ys): break
        self.M = np.array([[pow(x + y, -1, q) for y in ys] for x in xs], dtype=np.int64)
        self.RC = np.array([[rng.randrange(q) for _ in range(3)] for _ in range(64)], dtype=np.int64)
        self.cap = pow(2, 65, q)
        self.Minv = self.inv()

    def inv(self):
        q = self.q; M = [[int(v) for v in row] for row in self.M]
        a, b, c = M[0]; d, e, f = M[1]; g, h, i = M[2]
        det = (a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)) % q
        di = pow(det, -1, q)
        adj = [[e * i - f * h, c * h - b * i, b * f - c * e], [f * g - d * i, a * i - c * g, c * d - a * f],
               [d * h - e * g, b * g - a * h, a * e - b * d]]
        return np.array([[x * di % q for x in row] for row in adj], dtype=np.int64)

    def pow5(self, x):
        q = self.q; x2 = x * x % q; x4 = x2 * x2 % q
        return x4 * x % q

    def rnd(self, S, idx, full=None):
        if full is None: full = idx < 4 or idx >= 60
        q = self.q
        S = (S + self.RC[idx]) % q
        if full: S = self.pow5(S)
        else: S = S.copy(); S[:, 0] = self.pow5(S[:, 0])
        return S @ self.M.T % q

    def sched(self, r): return [0, 1, 2, 3] + list(range(4, 4 + r)) + [60, 61, 62, 63]

    def run(self, S, idxs):
        for i in idxs: S = self.rnd(S, i)
        return S


def inputs(q):
    nk, rho = np.meshgrid(np.arange(q, dtype=np.int64), np.arange(q, dtype=np.int64), indexing='ij')
    return nk.ravel(), rho.ravel()


def ordered_pairs_same(keys):
    _, cnt = np.unique(keys, return_counts=True)
    return int((cnt * (cnt - 1)).sum())


log('=== T1: injectivity of the full 3-lane state (X1); gcd(5,q-1)=1 vs 5 ===')
for q in (11, 31, 41, 23, 29, 37, 103, 257):
    g = gcd(5, q - 1)
    for r in (1, 2):
        t = Toy(q, 5)
        nk, rho = inputs(q)
        S = np.stack([nk, rho, np.full_like(nk, t.cap)], 1)
        F = t.run(S, t.sched(r))
        key = F[:, 0] * q * q + F[:, 1] * q + F[:, 2]
        d3 = len(np.unique(key)); d0 = len(np.unique(F[:, 0])); d01 = len(np.unique(F[:, 0] * q + F[:, 1]))
        log('OBSERVED q=%d gcd(5,q-1)=%d r=%d: inputs %d, distinct 3-lane outputs %d, distinct lane0 %d (of %d), distinct (lane0,lane1) %d'
            % (q, g, r, q * q, d3, d0, q, d01))

log('\n=== T2: X2 exhaustive: (nk,rho)->(A,B) bijection, state after R0.M lies on plane (M^-1 s)_2 = K ===')
for q in (23, 29, 103, 257):
    t = Toy(q, 9)
    nk, rho = inputs(q)
    A = t.pow5((nk + t.RC[0][0]) % q); B = t.pow5((rho + t.RC[0][1]) % q)
    nAB = len(np.unique(A * q + B))
    S0 = t.rnd(np.stack([nk, rho, np.full_like(nk, t.cap)], 1), 0)
    K = int(t.pow5(np.array([(t.cap + t.RC[0][2]) % q]))[0])
    plane = int(((S0 @ t.Minv.T % q)[:, 2] == K).sum())
    # H(A,B): hash computed from rounds 1.. on M*(A,B,K)
    S1 = np.stack([A, B, np.full_like(A, K)], 1) @ t.M.T % q
    ok = all((t.run(S1, t.sched(r)[1:])[:, 0] == t.run(np.stack([nk, rho, np.full_like(nk, t.cap)], 1), t.sched(r))[:, 0]).all() for r in (1, 2))
    log('OBSERVED q=%d: distinct (A,B) %d of %d; plane condition holds for %d of %d inputs; H(A,B)==hash for all inputs r=1,2: %s' % (q, nAB, q * q, plane, q * q, ok))

log('\n=== T3: pairs of STATES (all q^3) staying lane-0-equal through partial rounds (X6, exhaustive), q=23, 3 seeds ===')
for q in (23, 29):
    for seed in (1, 2, 3):
        t = Toy(q, seed)
        a, b, c = np.meshgrid(*[np.arange(q, dtype=np.int64)] * 3, indexing='ij')
        S = np.stack([a.ravel(), b.ravel(), c.ravel()], 1)
        N = len(S)
        s0 = S[:, 0]
        Y4 = t.rnd(t.run(S, [0, 1, 2, 3]), 4) if False else None
        # entering R4: take the state itself (any state), push through partial rounds 4,5,6 with those round constants
        Y = S; hist = []
        for k, idx in enumerate((4, 5, 6)):
            Y = t.rnd(Y, idx, full=False)
            tot = ordered_pairs_same(Y[:, 0])
            # pairs with equal entering lane 0 and equal all previous lane0s
            keyfull = s0.copy()
            hist.append((idx, tot))
        # classify: ordered pairs with equal entry lane0 (d0=0) that are equal after round k
        Y = S; res = []
        key0 = s0.copy()
        for k, idx in enumerate((4, 5, 6)):
            Y = t.rnd(Y, idx, full=False)
            key = key0 * q + Y[:, 0]
            n_d0zero = ordered_pairs_same(key)       # d0 = 0 AND lane0 equal after this round
            n_all = ordered_pairs_same(Y[:, 0])      # lane0 equal after this round (any entry d0)
            res.append((idx, n_d0zero, n_all))
        pred_d0 = [N * (q - 1), 0, 0]
        log('OBSERVED q=%d seed=%d (N=%d states): ordered pairs, entry lane0 equal & lane0 equal after R4/R5/R6: %s ; predicted from trail algebra %s ; (generic expectation for pairs of any entry ~ N^2/q = %d)'
            % (q, seed, N, [r_[1] for r_ in res], pred_d0, N * N // q))
        # chain: equal after R4 AND R5 among d0=0 pairs, compare with all pairs equal after both
        Y4 = t.rnd(S, 4, full=False); Y5 = t.rnd(Y4, 5, full=False)
        n_chain_all = ordered_pairs_same(Y4[:, 0] * q + Y5[:, 0])
        n_chain_d0 = ordered_pairs_same(s0 * q * q + Y4[:, 0] * q + Y5[:, 0])
        log('   chained: lane0 equal after R4 and after R5: any entry %d (random ~ N^2/q^2 = %d); entry lane0 equal too: %d' % (n_chain_all, N * N // q // q, n_chain_d0))

log('\n=== T4: Jacobian rank-drop points of (nk,rho)->state, exhaustive q=103 ===')
q = 103
t = Toy(q, 4)
nk, rho = inputs(q)
for r in (1, 2):
    S = np.stack([nk, rho, np.full_like(nk, t.cap)], 1)
    J = np.zeros((len(nk), 3, 2), dtype=np.int64); J[:, 0, 0] = 1; J[:, 1, 1] = 1
    rows = []
    def rank_def(J):
        m01 = (J[:, 0, 0] * J[:, 1, 1] - J[:, 0, 1] * J[:, 1, 0]) % q
        m02 = (J[:, 0, 0] * J[:, 2, 1] - J[:, 0, 1] * J[:, 2, 0]) % q
        m12 = (J[:, 1, 0] * J[:, 2, 1] - J[:, 1, 1] * J[:, 2, 0]) % q
        return int(((m01 == 0) & (m02 == 0) & (m12 == 0)).sum())
    rows.append(('init', rank_def(J)))
    for idx in t.sched(r):
        full = idx < 4 or idx >= 60
        S = (S + t.RC[idx]) % q
        x4 = (S * S % q) ** 2 % q
        dg = 5 * x4 % q
        lanes = (0, 1, 2) if full else (0,)
        for l in lanes:
            J[:, l, :] = J[:, l, :] * dg[:, l:l + 1] % q
        S = t.pow5(S) if full else np.concatenate([t.pow5(S[:, :1]), S[:, 1:]], 1)
        J = np.einsum('ij,njk->nik', t.M, J) % q
        S = S @ t.M.T % q
        rows.append(('R%d' % idx, rank_def(J)))
    log('OBSERVED q=103 r=%d: number of inputs (of %d) where the 3x2 Jacobian has rank < 2, after each round: %s ; round-0 prediction a=0 or b=0: %d'
        % (r, q * q, rows, 2 * q - 1))

log('\n=== T5: do the lane-0 collision pairs of r=1 and r=2 coincide? q=103, 3 seeds (same constants, schedules differ by R5) ===')
q = 103
for seed in (1, 2, 3):
    t = Toy(q, seed)
    nk, rho = inputs(q)
    S = np.stack([nk, rho, np.full_like(nk, t.cap)], 1)
    h = {r: t.run(S, t.sched(r))[:, 0] for r in (1, 2)}
    N = len(nk)
    def pairs(hh):
        order = np.argsort(hh, kind='stable'); hs = hh[order]
        res = set()
        i = 0
        while i < N:
            j = i
            while j < N and hs[j] == hs[i]: j += 1
            grp = order[i:j]
            for a in range(len(grp)):
                for b_ in range(a + 1, len(grp)):
                    x, y = sorted((int(grp[a]), int(grp[b_]))); res.add(x * N + y)
            i = j
        return res
    p1 = pairs(h[1]); p2 = pairs(h[2])
    inter = len(p1 & p2); tot = N * (N - 1) // 2
    log('OBSERVED seed=%d: collision pairs r=1: %d, r=2: %d, in both: %d; independent-random expectation %.1f' % (seed, len(p1), len(p2), inter, len(p1) * len(p2) / tot))
    # same for pairs that collide after R4 (i.e. in a lane 0 of the state after R4.M) and then in r=1/r=2
    S4 = t.run(S, [0, 1, 2, 3, 4])
    p4 = pairs(S4[:, 0])
    log('   pairs with equal lane0 after R4.M: %d; of them colliding at r=1 output: %d, at r=2 output: %d (random expectation %.1f each)' % (len(p4), len(p4 & p1), len(p4 & p2), len(p4) * len(p1) / tot))

log('\n=== T6: degree-drop directions of round 0 (X10), exhaustive over all q+1 directions of P^1 ===')
for q in (23, 29, 37, 103, 257, 11, 31):
    t = Toy(q, 3)
    counts = []
    for i in range(3):
        n = 0
        dirs = [(1, v) for v in range(q)] + [(0, 1)]
        for (u, v) in dirs:
            if (int(t.M[i][0]) * pow(u, 5, q) + int(t.M[i][1]) * pow(v, 5, q)) % q == 0: n += 1
        counts.append(n)
    log('OBSERVED q=%d gcd(5,q-1)=%d: directions (u:v) with M_i0 u^5 + M_i1 v^5 = 0, lanes 0,1,2: %s (PROVED 1 each when gcd=1; 5 or 0 when gcd=5)' % (q, gcd(5, q - 1), counts))

open('u12_toy_output.txt', 'w').write('\n'.join(out))
