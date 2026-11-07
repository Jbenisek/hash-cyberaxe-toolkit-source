"""Toy copies of the reduced Poseidon over F_q (gcd(5,q-1)=1), exhaustive over all q^2 inputs. Random Cauchy MDS, random constants."""
import numpy as np, random, itertools

def is_prime(n):
    if n < 2: return False
    i = 2
    while i * i <= n:
        if n % i == 0: return False
        i += 1
    return True
def admissible(q):
    return is_prime(q) and (q - 1) % 5 != 0

class Toy:
    def __init__(self, q, seed, nrounds_labels=(0, 1, 2, 3)):
        assert admissible(q)
        self.q = q; rng = random.Random(seed); self.seed = seed
        while True:
            xs = [rng.randrange(q) for _ in range(3)]; ys = [rng.randrange(q) for _ in range(3)]
            if len(set(xs)) == 3 and len(set(ys)) == 3 and all((x + y) % q for x in xs for y in ys): break
        self.M = [[pow(x + y, q - 2, q) for y in ys] for x in xs]
        self.RC = [[rng.randrange(q) for _ in range(3)] for _ in range(8)]   # rounds 0..3 and spare rows
        self.cap = (1 << 65) % q
        n = np.arange(q, dtype=np.int64)
        self.nk = np.repeat(n, q); self.rho = np.tile(n, q)
    def pow5(self, x):
        q = self.q; x2 = x * x % q; x4 = x2 * x2 % q; return x4 * x % q
    def mds(self, s):
        q = self.q; M = self.M
        return [(M[i][0] * s[0] + M[i][1] * s[1] + M[i][2] * s[2]) % q for i in range(3)]
    def steps(self, nfull=4):
        """list of (name, [lane0,lane1,lane2]) for init, then C,S,M of rounds 0..nfull-1 (full rounds)"""
        q = self.q
        s = [self.nk.copy(), self.rho.copy(), np.full_like(self.nk, self.cap)]
        out = [('init', s)]
        for r in range(nfull):
            s = [(s[i] + self.RC[r][i]) % q for i in range(3)]; out.append((f'R{r}.C', s))
            s = [self.pow5(x) for x in s]; out.append((f'R{r}.S', s))
            s = self.mds(s); out.append((f'R{r}.M', s))
        return out

def rank_mod(Mx, q):
    """rank of integer matrix mod prime q (numpy int64)"""
    A = Mx.copy() % q; nr, nc = A.shape; r = 0
    for c in range(nc):
        if r >= nr: break
        nzr = np.nonzero(A[r:, c])[0]
        if nzr.size == 0: continue
        p = r + nzr[0]
        if p != r: A[[r, p]] = A[[p, r]]
        inv = pow(int(A[r, c]), q - 2, q)
        A[r, c:] = A[r, c:] * inv % q
        rows = r + 1 + np.nonzero(A[r + 1:, c])[0]
        if rows.size:
            A[rows, c:] = (A[rows, c:] - np.outer(A[rows, c], A[r, c:])) % q
        r += 1
    return r

def kernel_mod(Mx, q):
    """a basis of the right kernel of Mx mod prime q (list of vectors), via RREF"""
    A = Mx.copy() % q; nr, nc = A.shape; r = 0; piv = []
    for c in range(nc):
        if r >= nr: break
        nzr = np.nonzero(A[r:, c])[0]
        if nzr.size == 0: continue
        p = r + nzr[0]
        if p != r: A[[r, p]] = A[[p, r]]
        inv = pow(int(A[r, c]), q - 2, q)
        A[r] = A[r] * inv % q
        rows = np.nonzero(A[:, c])[0]; rows = rows[rows != r]
        if rows.size:
            A[rows] = (A[rows] - np.outer(A[rows, c], A[r])) % q
        piv.append(c); r += 1
    free = [c for c in range(nc) if c not in set(piv)]
    ker = []
    for f in free:
        v = np.zeros(nc, dtype=np.int64); v[f] = 1
        for i, c in enumerate(piv): v[c] = (-A[i, f]) % q
        ker.append(v)
    return ker

def monomials(maxdeg, q):
    """exponent triples (e0,e1,e2) with e0+e1+e2 <= maxdeg and each e < q, ordered by total degree"""
    mons = []
    for d in range(maxdeg + 1):
        for e0 in range(min(d, q - 1), -1, -1):
            for e1 in range(min(d - e0, q - 1), -1, -1):
                e2 = d - e0 - e1
                if e2 < q: mons.append((e0, e1, e2))
    return mons

def eval_monomials(pts, mons, q, rows):
    """matrix [len(rows) x len(mons)] of monomial values at selected points (pts = list of 3 arrays)"""
    x = [p[rows] % q for p in pts]
    maxe = max(max(m) for m in mons)
    pw = [[np.ones_like(x[i])] for i in range(3)]
    for i in range(3):
        for e in range(1, maxe + 1): pw[i].append(pw[i][-1] * x[i] % q)
    out = np.empty((len(rows), len(mons)), dtype=np.int64)
    for j, (e0, e1, e2) in enumerate(mons):
        out[:, j] = pw[0][e0] * pw[1][e1] % q * pw[2][e2] % q
    return out
