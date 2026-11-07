"""dig-scan-poseidon library (2026-10-12): exact top-term (Laurent at infinity) degree tracker + W-line model
for Orchard P128Pow5T3 over Pallas.  Reads constants via research/poseidon/orchard/impl/poseidon_ref.py (validated 11/11).
Own code only."""
import sys, os, random, json
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, '..'))
IMPL = os.path.normpath(os.path.join(HERE, '..', '..', '..', 'poseidon', 'orchard', 'impl'))
sys.path.insert(0, IMPL)
import poseidon_ref as PR
from poseidon_ref import P, RC, MDS, CAPACITY, round_full, round_partial, hash_reduced
from gmpy2 import mpz
NEG = -10**30
K = 24
INV5 = pow(5, -1, P - 1)
root5 = lambda x: pow(x, INV5, P)
inv = lambda x: pow(x, P - 2, P)


class Unknown(Exception):
    pass


class S:
    """sum_k c[k] * W^(e-k); coefficients exact for all powers >= low (low = NEG means a finite exact polynomial)."""
    __slots__ = ('e', 'c', 'low')

    def __init__(s, e, c, low=NEG):
        s.e, s.c, s.low = e, c, low


def norm(x):
    c, e, low = x.c, x.e, x.low
    if len(c) > K:
        c = c[:K]
        low = max(low, e - K + 1)
    while c and c[0] == 0:
        c = c[1:]
        e -= 1
    if not c:
        if low <= NEG // 2:
            return None
        raise Unknown('precision exhausted')
    return S(e, c, low)


def const(v):
    v %= P
    return None if v == 0 else S(0, [mpz(v)], NEG)


def coef(x, t):
    k = x.e - t
    return x.c[k] if 0 <= k < len(x.c) else 0


def add(a, b):
    if a is None:
        return b
    if b is None:
        return a
    E = max(a.e, b.e)
    low = max(a.low, b.low)
    la = a.e - len(a.c) + 1
    lb = b.e - len(b.c) + 1
    bottom = max(min(la, lb), low, E - K + 1)
    c = [(coef(a, t) + coef(b, t)) % P for t in range(E, bottom - 1, -1)]
    if bottom > min(la, lb):
        low = max(low, bottom)
    return norm(S(E, [mpz(v) for v in c], low))


def scale(a, k):
    if a is None or k % P == 0:
        return None
    return S(a.e, [mpz(v * k % P) for v in a.c], a.low)


def mul(a, b):
    if a is None or b is None:
        return None
    e = a.e + b.e
    la = a.low + b.e if a.low > NEG // 2 else NEG
    lb = b.low + a.e if b.low > NEG // 2 else NEG
    low = max(la, lb)
    n = min(len(a.c) + len(b.c) - 1, K)
    if low > NEG // 2:
        n = min(n, e - low + 1)
    n = max(n, 1)
    c = []
    for k in range(n):
        s = 0
        for i in range(max(0, k - len(b.c) + 1), min(k, len(a.c) - 1) + 1):
            s += a.c[i] * b.c[k - i]
        c.append(s % P)
    if len(a.c) + len(b.c) - 1 > K:
        low = max(low, e - K + 1)
    return norm(S(e, [mpz(v) for v in c], low))


def pow5(a):
    if a is None:
        return None
    a2 = mul(a, a)
    a4 = mul(a2, a2)
    return mul(a4, a)


def lin(row, lanes):
    r = None
    for m, x in zip(row, lanes):
        r = add(r, scale(x, m))
    return r


def rounds_spec(r):
    out = []
    for idx in PR.schedule(r):
        full = idx < 4 or idx >= 60
        out.append(dict(idx=idx, c=list(RC[idx]), sb=[True, True, True] if full else [True, False, False],
                        M=[list(row) for row in MDS]))
    return out


def run_round(lanes, rd):
    xs = [add(l, const(rd['c'][i])) for i, l in enumerate(lanes)]
    ss = [pow5(x) if rd['sb'][i] else x for i, x in enumerate(xs)]
    return [lin(rd['M'][i], ss) for i in range(3)]


def run_rounds(lanes, specs):
    for rd in specs:
        lanes = run_round(lanes, rd)
    return lanes


# ---------- W-line model ----------
def setup_line(j):
    Kp = pow((CAPACITY + RC[0][2]) % P, 5, P)
    base = [(MDS[i][2] * Kp + RC[1][i]) % P for i in range(3)]
    a, b = MDS[j][1], (-MDS[j][0]) % P
    d = [(MDS[i][0] * a + MDS[i][1] * b) % P for i in range(3)]
    ii = [i for i in range(3) if i != j]
    (p0, q0), (p1, q1) = (MDS[ii[0]][0], MDS[ii[0]][1]), (MDS[ii[1]][0], MDS[ii[1]][1])
    det = (p0 * q1 - p1 * q0) % P
    r0, r1 = (-base[ii[0]]) % P, (-base[ii[1]]) % P
    U0 = (r0 * q1 - r1 * q0) * inv(det) % P
    V0 = (p0 * r1 - p1 * r0) * inv(det) % P
    return a, b, U0, V0, d


def inputs_for_tau(tau, line):
    a, b, U0, V0, d = line
    U = (U0 + a * tau) % P
    V = (V0 + b * tau) % P
    return (root5(U) - RC[0][0]) % P, (root5(V) - RC[0][1]) % P


def state_after_r1(nk, rho):
    return round_full(round_full([nk, rho, CAPACITY], 0), 1)


def line_affine(j):
    """alpha, beta (state after round 1 = alpha + beta*W) from the reference rounds; checked at a third point."""
    line = setup_line(j)
    s0 = state_after_r1(*inputs_for_tau(0, line))
    s1 = state_after_r1(*inputs_for_tau(1, line))
    beta = [(s1[i] - s0[i]) % P for i in range(3)]
    alpha = s0
    W = random.randrange(1, P)
    sw = state_after_r1(*inputs_for_tau(root5(W), line))
    assert all((alpha[i] + beta[i] * W - sw[i]) % P == 0 for i in range(3)), 'line model not affine'
    return alpha, beta, line


def W_start(alpha, beta):
    return [add(const(alpha[i]), scale(S(1, [mpz(1)], NEG), beta[i])) for i in range(3)]


def W_deg(alpha, beta, specs):
    """exact degree in W of digest lane 0 after `specs` (rounds 2..) from state alpha + beta W; (degree, certified)"""
    lanes = run_rounds(W_start(alpha, beta), specs)
    y = lanes[0]
    if y is None:
        return None
    return y.e, (y.low <= y.e)


def specs_from_2(r):
    return [d for d in rounds_spec(r) if d['idx'] >= 2]


def F_eval(alpha, beta, specs, W):
    s = [(alpha[i] + beta[i] * W) % P for i in range(3)]
    for rd in specs:
        s = [(s[i] + rd['c'][i]) % P for i in range(3)]
        s = [pow(s[i], 5, P) if rd['sb'][i] else s[i] for i in range(3)]
        s = [sum(rd['M'][i][k] * s[k] for k in range(3)) % P for i in range(3)]
    return s[0]


def root_of_unity(n):
    T = (P - 1) >> 32
    z = 5
    while pow(z, (P - 1) // 2, P) == 1:
        z += 1
    w = pow(z, T, P)
    assert pow(w, 1 << 31, P) != 1
    return pow(w, (1 << 32) // n, P)


def ntt(a, w):
    n = len(a)
    a = [mpz(x) for x in a]
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]
    length = 2
    while length <= n:
        wl = pow(w, n // length, P)
        half = length >> 1
        ws = [mpz(1)]
        for _ in range(half - 1):
            ws.append(ws[-1] * wl % P)
        for i in range(0, n, length):
            for k in range(half):
                u = a[i + k]
                v = a[i + k + half] * ws[k] % P
                a[i + k] = (u + v) % P
                a[i + k + half] = (u - v) % P
        length <<= 1
    return a


def intt(vals, w):
    n = len(vals)
    a = ntt(vals, pow(w, P - 2, P))
    ni = pow(n, P - 2, P)
    return [x * ni % P for x in a]


def poly_degree(coefs):
    for i in range(len(coefs) - 1, -1, -1):
        if coefs[i] != 0:
            return i
    return -1


def write_cell(unit, cell_id, rec):
    d = os.path.join(OUT, unit)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, cell_id.replace('|', '_') + '.json')
    with open(path, 'w', encoding='utf8') as f:
        json.dump(rec, f, indent=1)
    return path
