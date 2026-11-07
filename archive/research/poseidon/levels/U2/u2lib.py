"""U2 library: exact objects for rounds R1..R3 of the reduced Orchard Poseidon. Learning only."""

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

import sys, math, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import numpy as np
import poseidon_ref as pr
P = pr.P; RC = pr.RC; MDS = pr.MDS
CAP = pr.CAPACITY
a0, b0, c02 = RC[0]
K = pow((CAP + c02) % P, 5, P)

# ---------- bivariate polynomials in (A,B): dense object array [i][j] = coeff of A^i B^j
def bz(D):
    return np.zeros((D + 1, D + 1), dtype=object) + 0
def bmul(x, y):
    dx, dy = x.shape[0] - 1, y.shape[0] - 1
    out = bz(dx + dy)
    nzx = [(i, j) for i in range(dx + 1) for j in range(dx + 1 - i) if x[i, j] != 0]
    for i, j in nzx:
        out[i:i + dy + 1, j:j + dy + 1] += x[i, j] * y
    return out % P
def bpow5(x):
    x2 = bmul(x, x); x4 = bmul(x2, x2)
    return bmul(x4, x)
def bshrink(x, D):
    return x[:D + 1, :D + 1].copy()
def badd_const(x, c):
    y = x.copy(); y[0, 0] = (y[0, 0] + c) % P; return y
def lanes_R0():
    """(A,B)-polys of the 3 lanes after R0.M: M_i0 A + M_i1 B + M_i2 K"""
    L = []
    for i in range(3):
        z = bz(1); z[1, 0] = MDS[i][0]; z[0, 1] = MDS[i][1]; z[0, 0] = MDS[i][2] * K % P
        L.append(z)
    return L
def full_round_AB(L, idx, D):
    S = [bshrink(bpow5(badd_const(L[i], RC[idx][i])), 5 * D) for i in range(3)]
    out = []
    for i in range(3):
        acc = bz(5 * D)
        for j in range(3):
            acc = acc + MDS[i][j] * S[j]
        out.append(acc % P)
    return out
def lanes_after(k):
    """lanes after R_k.M in (A,B) coordinates, k=0..3 ; total degree 5^k"""
    L = lanes_R0(); D = 1
    for r in range(1, k + 1):
        L = full_round_AB(L, r, D); D *= 5
    return L, D
def support_AB(x):
    return sum(1 for i in range(x.shape[0]) for j in range(x.shape[0] - i) if x[i, j] != 0)

def expand_nk_rho(C, D):
    """dense (A,B) poly of total degree D -> dense R[u][v] coefficient of nk^u rho^v, A=(nk+a0)^5, B=(rho+b0)^5"""
    U = 5 * D
    def T(alpha):
        t = np.zeros((U + 1, D + 1), dtype=object)
        for i in range(D + 1):
            for u in range(5 * i + 1):
                t[u, i] = math.comb(5 * i, u) % P * pow(alpha, 5 * i - u, P) % P
        return t
    Tn, Tr = T(a0), T(b0)
    X = (Tn.dot(C)) % P
    return (X.dot(Tr.T)) % P
def law_set(D_k, U):
    return {(u, v) for u in range(U + 1) for v in range(U + 1) if -(-u // 5) + -(-v // 5) <= D_k}

# ---------- univariate polynomials over F_p, lists low->high
def pnorm(a):
    while a and a[-1] == 0: a.pop()
    return a
def padd(a, b):
    n = max(len(a), len(b)); return pnorm([((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % P for i in range(n)])
def psub(a, b):
    n = max(len(a), len(b)); return pnorm([((a[i] if i < len(a) else 0) - (b[i] if i < len(b) else 0)) % P for i in range(n)])
def pmul(a, b):
    if not a or not b: return []
    r = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b): r[i + j] += x * y
    return pnorm([c % P for c in r])
def pdivmod(a, b):
    a = a[:]; db = len(b) - 1; inv = pow(b[-1], P - 2, P)
    q = [0] * max(0, len(a) - db)
    for i in range(len(a) - 1, db - 1, -1):
        c = a[i] * inv % P
        if c:
            q[i - db] = c
            for j in range(db + 1): a[i - db + j] = (a[i - db + j] - c * b[j]) % P
    return pnorm(q), pnorm(a[:db])
def pmod(a, b): return pdivmod(a, b)[1]
def pgcd(a, b):
    a, b = pnorm(a[:]), pnorm(b[:])
    while b: a, b = b, pmod(a, b)
    if a:
        inv = pow(a[-1], P - 2, P); a = [x * inv % P for x in a]
    return a
def pderiv(a): return pnorm([i * a[i] % P for i in range(1, len(a))])
def ppowmod(base, e, m):
    r = [1]; b = pmod(base, m)
    while e:
        if e & 1: r = pmod(pmul(r, b), m)
        b = pmod(pmul(b, b), m); e >>= 1
    return r
def peval(a, x):
    r = 0
    for c in reversed(a): r = (r * x + c) % P
    return r
def ddf(f, kmax=None):
    """distinct-degree pattern of squarefree f: {k: total degree of irreducible factors of degree k}"""
    res = {}; g = f[:]; h = [0, 1]; k = 0
    while len(g) - 1 >= 2 * (k + 1) and (kmax is None or k < kmax):
        k += 1
        h = ppowmod(h, P, g)
        d = pgcd(g, psub(h, [0, 1]))
        if len(d) > 1:
            res[k] = len(d) - 1
            g, _ = pdivmod(g, d); h = pmod(h, g) if len(g) > 1 else h
    if len(g) > 1 and kmax is None:
        res[len(g) - 1] = len(g) - 1
    return res
def roots_Fp(f):
    h = ppowmod([0, 1], P, f)
    g = pgcd(f, psub(h, [0, 1]))
    out = []
    def split(g):
        if len(g) <= 1: return
        if len(g) == 2: out.append((-g[0]) * pow(g[1], P - 2, P) % P); return
        while True:
            a = random.randrange(P)
            t = ppowmod([a, 1], (P - 1) // 2, g)
            d = pgcd(g, psub(t, [1]))
            if 1 < len(d) < len(g):
                split(d); split(pdivmod(g, d)[0]); return
    split(g)
    return sorted(out)

# ---------- line polynomials: nk = a+u t, rho = b+v t
def line_state_R0(a, b, u, v):
    pa = [1]; base = [(a + a0) % P, u % P]
    for _ in range(5): pa = pmul(pa, base)
    pb = [1]; base = [(b + b0) % P, v % P]
    for _ in range(5): pb = pmul(pb, base)
    L = []
    for i in range(3):
        poly = padd(padd([MDS[i][0] * c % P for c in pa], [MDS[i][1] * c % P for c in pb]), [MDS[i][2] * K % P])
        L.append(poly)
    return L
def p5(a):
    a2 = pmul(a, a); a4 = pmul(a2, a2); return pmul(a4, a)
def line_round(L, idx):
    S = [p5(padd(L[i], [RC[idx][i]])) for i in range(3)]
    out = []
    for i in range(3):
        acc = []
        for j in range(3): acc = padd(acc, [MDS[i][j] * c % P for c in S[j]])
        out.append(acc)
    return out
def line_lanes_after(a, b, u, v, k):
    L = line_state_R0(a, b, u, v)
    for r in range(1, k + 1): L = line_round(L, r)
    return L
def tracker(u, v, k):
    """leading-coefficient tracker: top coefficient (t^(5^(k+1))) of each lane after R_k"""
    U, V = pow(u, 5, P), pow(v, 5, P)
    F = [(MDS[i][0] * U + MDS[i][1] * V) % P for i in range(3)]
    for _ in range(k):
        F5 = [pow(x, 5, P) for x in F]
        F = [sum(MDS[i][j] * F5[j] for j in range(3)) % P for i in range(3)]
    return F
