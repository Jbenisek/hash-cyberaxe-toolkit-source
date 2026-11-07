"""Toy copies of the target: same structure (3 lanes, x^5, full/partial rounds, rounds 0-3 | 4.. | 60-63 schedule,
init [nk, rho, 2^65 mod q], Cauchy MDS, random constants) over small primes q with gcd(5, q-1) = 1.
Everything is enumerated exhaustively over all q^2 inputs. Run: python facts_toy.py  (single process, numpy)"""
import sys, time, random, math
import numpy as np
T0 = time.time()
def log(*a): print(*a, flush=True)
def is_prime(n):
    if n < 2: return False
    i = 2
    while i*i <= n:
        if n % i == 0: return False
        i += 1
    return True
def two_adicity(n):
    k = 0
    while n % 2 == 0: n //= 2; k += 1
    return k

class Toy:
    def __init__(self, q, seed):
        assert is_prime(q) and math.gcd(5, q-1) == 1
        self.q = q; rnd = random.Random(seed*1000003 + q)
        self.cap = pow(2, 65, q)
        while True:   # Cauchy MDS with random xs, ys (as the real one is Cauchy, see facts_basic)
            xs = rnd.sample(range(q), 3); ys = rnd.sample(range(q), 3)
            if all((x+y) % q for x in xs for y in ys): break
        self.M = [[pow(x+y, -1, q) for y in ys] for x in xs]
        self.RC = [[rnd.randrange(q) for _ in range(3)] for _ in range(64)]
    def sched(self, r): return [(i, True) for i in range(4)] + [(i, False) for i in range(4, 4+r)] + [(i, True) for i in range(60, 64)]
    def perm_np(self, s, r):
        q, M, RC = self.q, self.M, self.RC
        for idx, full in self.sched(r):
            s = [(s[i] + RC[idx][i]) % q for i in range(3)]
            for i in (range(3) if full else range(1)):
                x2 = s[i]*s[i] % q; x4 = x2*x2 % q; s[i] = x4*s[i] % q
            s = [(M[i][0]*s[0] + M[i][1]*s[1] + M[i][2]*s[2]) % q for i in range(3)]
        return s
    def perm_int(self, s, r):
        q, M, RC = self.q, self.M, self.RC
        s = list(s)
        for idx, full in self.sched(r):
            s = [(s[i] + RC[idx][i]) % q for i in range(3)]
            for i in (range(3) if full else range(1)): s[i] = pow(s[i], 5, q)
            s = [sum(M[i][j]*s[j] for j in range(3)) % q for i in range(3)]
        return s

def fibers(toy, r, chunk_rows):
    q = toy.q
    cnt = np.zeros(q, dtype=np.int64)
    rho = np.arange(q, dtype=np.int64)
    for start in range(0, q, chunk_rows):
        nks = np.arange(start, min(q, start+chunk_rows), dtype=np.int64)
        NK = np.repeat(nks, q); RHO = np.tile(rho, len(nks))
        s = [NK, RHO, np.full_like(NK, toy.cap)]
        out = toy.perm_np(s, r)[0]
        cnt += np.bincount(out, minlength=q)
    return cnt

def report(q, r, seeds, chunk_rows):
    N = q*q
    log('q=%d (q-1=2^%d*%d, q mod 4=%d, q^2=%d inputs), r=%d' % (q, two_adicity(q-1), (q-1) >> two_adicity(q-1), q % 4, N, r))
    exp_pairs = N*(N-1)/2/q
    for seed in seeds:
        toy = Toy(q, seed)
        # cross-check numpy vs scalar on a few inputs
        rr = random.Random(seed)
        for _ in range(5):
            a, b = rr.randrange(q), rr.randrange(q)
            assert toy.perm_np([np.array([a]), np.array([b]), np.array([toy.cap])], r)[0][0] == toy.perm_int([a, b, toy.cap], r)[0]
        t = time.time()
        cnt = fibers(toy, r, chunk_rows)
        assert cnt.sum() == N
        pairs = int((cnt*(cnt-1)//2).sum())
        log('   seed %d: image size %d/%d, fiber mean %.1f var %.1f (Poisson var would be %.1f), min %d max %d, colliding input pairs %d = %.4f x random-function expectation %.0f  (%.1fs)' %
            (seed, int((cnt > 0).sum()), q, cnt.mean(), cnt.var(), cnt.mean(), cnt.min(), cnt.max(), pairs, pairs/exp_pairs, exp_pairs, time.time()-t))

# ---------- list admissible q ----------
log('=== candidate toy primes (gcd(5,q-1)=1) ===')
log('1000003 prime?', is_prime(1000003), ' gcd(5,1000002)=', math.gcd(5, 1000002), ' 1000002 = 2*3*166667 -> 2-adicity 1, q mod 4 = 3')
for q in (257, 769, 1009, 4099, 12289, 65537):
    log(' q=%d prime %s gcd(5,q-1)=%d 2-adicity %d q mod 4 = %d q mod 5 = %d' % (q, is_prime(q), math.gcd(5, q-1), two_adicity(q-1), q % 4, q % 5))
log('real p: 2-adicity 32, p mod 4 = 1, p mod 5 = 2')

# ---------- x^5 on the toy fields ----------
log('\n=== x -> x^5 on F_q ===')
for q in (257, 769, 1009, 4099):
    fx = [x for x in range(q) if pow(x, 5, q) == x]
    perm = [pow(x, 5, q) for x in range(q)]
    assert sorted(perm) == list(range(q))
    seen = [False]*q; cyc = {}
    for x in range(q):
        if seen[x]: continue
        l = 0; y = x
        while not seen[y]: seen[y] = True; y = perm[y]; l += 1
        cyc[l] = cyc.get(l, 0)+1
    # number of solutions of (x+a)^5 - x^5 = b (differential spectrum)
    spec = {}
    for a in (1, 2, 3):
        c = [0]*q
        for x in range(q): c[(pow(x+a, 5, q) - pow(x, 5, q)) % q] += 1
        h = {}
        for v in c: h[v] = h.get(v, 0)+1
        spec[a] = dict(sorted(h.items()))
    log(' q=%d: fixed points of x^5: %d %s ; cycle lengths {len:count} %s' % (q, len(fx), fx, dict(sorted(cyc.items()))))
    log('       differential spectrum for a=1,2,3: #b with k solutions  %s  (max %d; at most 4 proved, pairs +-y because even in y=x+a/2)' % (spec, max(max(s) for s in spec.values())))

# ---------- structure facts exhaustively on q=257 ----------
log('\n=== q=257 exhaustive structure checks (seed 1) ===')
toy = Toy(257, 1); q = 257
# (1) full permutation on F^3 for r=1 is a bijection (all q^3 states)
import itertools
A = np.arange(q, dtype=np.int64)
S0 = np.repeat(A, q*q); S1 = np.tile(np.repeat(A, q), q); S2 = np.tile(A, q*q)
out = toy.perm_np([S0, S1, S2], 1)
code = out[0]*q*q + out[1]*q + out[2]
log(' r=1: permutation of all %d states is injective: %s' % (q**3, len(np.unique(code)) == q**3))
# (2) round 0 maps the (nk,rho) square onto the plane Minv[2].s = K
M = toy.M; qq = q
def inv3(m):
    det = lambda a, b, c, d: (a*d-b*c) % qq
    d = (m[0][0]*det(m[1][1], m[1][2], m[2][1], m[2][2]) - m[0][1]*det(m[1][0], m[1][2], m[2][0], m[2][2]) + m[0][2]*det(m[1][0], m[1][1], m[2][0], m[2][1])) % qq
    di = pow(d, -1, qq)
    cof = [[((-1)**(i+j) * det(*[m[a][b] for a in range(3) if a != i for b in range(3) if b != j])) % qq for j in range(3)] for i in range(3)]
    return [[cof[j][i]*di % qq for j in range(3)] for i in range(3)]
Mi = inv3(M)
K = pow((toy.cap + toy.RC[0][2]) % q, 5, q)
NK = np.repeat(A, q); RHO = np.tile(A, q)
s = [(NK+toy.RC[0][0]) % q, (RHO+toy.RC[0][1]) % q, np.full_like(NK, (toy.cap+toy.RC[0][2]) % q)]
s = [x**5 % q for x in s]
s = [(M[i][0]*s[0]+M[i][1]*s[1]+M[i][2]*s[2]) % q for i in range(3)]
plane = (Mi[2][0]*s[0] + Mi[2][1]*s[1] + Mi[2][2]*s[2]) % q
log(' round-0 outputs all lie on the plane Minv[2].s = K : %s ; distinct states %d of %d' % (bool((plane == K).all()), len(np.unique(s[0]*q*q+s[1]*q+s[2])), q*q))
# (3) distinct inputs never collide on the full 3-lane state, only on lane 0 after truncation
for r in (1, 2):
    out = toy.perm_np([NK.copy(), RHO.copy(), np.full_like(NK, toy.cap)], r)
    full = out[0]*q*q + out[1]*q + out[2]
    log(' r=%d: %d inputs -> %d distinct full 3-lane output states (injective: %s); lane-0-only distinct values %d' % (r, q*q, len(np.unique(full)), len(np.unique(full)) == q*q, len(np.unique(out[0]))))
    # (lane0,lane1) projection collisions  vs (lane 0 only)
    l01 = out[0]*q + out[1]
    log('       (lane0,lane1) pair injective? %s (distinct %d of %d)' % (len(np.unique(l01)) == q*q, len(np.unique(l01)), q*q))

# ---------- fiber statistics ----------
log('\n=== output fibre statistics (lane 0 of output) over ALL q^2 inputs ===')
for q, rs, seeds, ch in ((257, (0, 1, 2, 3), (1, 2, 3, 4, 5), 257), (769, (1, 2), (1, 2, 3), 200), (1009, (1, 2), (1, 2, 3), 200), (4099, (1, 2), (1, 2), 100), (12289, (1, 2), (1,), 50)):
    for r in rs: report(q, r, seeds, ch)
log('total seconds %.1f' % (time.time()-T0))
