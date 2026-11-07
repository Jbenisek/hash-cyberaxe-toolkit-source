"""Ones'-complement lens (Z/(2^32-1)) on the front-line residual: shared counting and evaluation.

Counts are built either in numpy (from the stored data) or by oc_stream.c (streaming, fresh samples); both
produce the SAME flat layout (layout() below), so one evaluator serves both.

Quantities, per residual word w in (1,3,4,6) (index 0..3):
  D  = oc(dA) - oc(dB) mod M          the residual read in ones'-complement coordinates (primary)
  R  = oc(dA ^ dB)                     the XOR residual R read as an element of Z/M
  E  = D - oc_diff(x) - oc_diff(y)     epsilon: what is left when D is split as E1 part + E3 part
                                       (digest word = x ^ y, x from one diagonal G, y from the other)
  S  = oc(dA) - oc(dA ^ R_other) mod M surrogate: D rebuilt with a residual from ANOTHER row (keeps R's
                                       distribution, breaks the dA <-> R coupling); a control, never tested
where oc(x) = x mod (2^32-1) (0xFFFFFFFF -> 0) and M = 2^32-1 = 3*5*17*257*65537.
"""
import math
import numpy as np
from scipy import stats

M = 0xFFFFFFFF
PRIMES = (3, 5, 17, 257, 65537)
MODS = (3, 5, 15, 17, 51, 85, 255, 257, 771, 1285, 3855, 4369, 13107, 21845, 65535, 65537)
JMODS = (3, 5, 15, 17)                       # joint 4-word residue vectors
SUBS = (("p4", 0x11111111), ("p8", 0x01010101))  # period-4 / period-8 subgroups: D == 0 mod M/15, M/255
COSETS = ((17, 2), (17, 16), (257, 2), (257, 16), (65537, 2), (65537, 16))  # (p, g): class of D in (Z/p)*/<g>
QS = ("D", "R", "E", "S")
TESTED_QS = ("D", "R", "E")


def ordm(g, p):
    x, k = g % p, 1
    while x != 1:
        x = x * g % p
        k += 1
    return k


def coset_index(p, g):
    return (p - 1) // ordm(g, p)


DLOG = {}
for _p in (17, 257, 65537):
    t = np.zeros(_p, dtype=np.int64)
    x = 1
    for e in range(_p - 1):
        t[x] = e
        x = x * 3 % _p
    DLOG[_p] = t


def layout():
    """Ordered list of (key, length): the flat layout shared with oc_stream.c."""
    L = []
    for q in QS:
        for w in range(4):
            for m in MODS:
                L.append(("%s.w%d.m%d" % (q, w, m), m))
            for name, _ in SUBS:
                L.append(("%s.w%d.%s" % (q, w, name), 1))
            L.append(("%s.w%d.div" % (q, w), 32))
            for p, g in COSETS:
                L.append(("%s.w%d.cos%d_%d" % (q, w, p, g), coset_index(p, g)))
        for m in JMODS:
            L.append(("%s.joint.m%d" % (q, m), m ** 4))
    L.append(("N", 1))
    return L


def split_flat(flat):
    out, o = {}, 0
    for k, n in layout():
        out[k] = flat[o:o + n].astype(np.int64)
        o += n
    assert o == len(flat), (o, len(flat))
    return out


def oc(x):
    x = np.asarray(x).astype(np.int64)
    x[x == M] = 0
    return x


def ocsub(a, b):
    d = oc(a) - oc(b)
    d[d < 0] += M
    return d


def quantities(dA, dB, xA, xB, yA, yB, rng):
    """dA,dB,xA,... : (N,4) uint32. Returns dict Q -> (N,4) int64 in [0,M)."""
    D = ocsub(dA, dB)
    R = oc(dA ^ dB)
    E = (D - ocsub(xA, xB) - ocsub(yA, yB)) % M
    Rx = (dA ^ dB)[rng.permutation(len(dA))]
    S = ocsub(dA, dA ^ Rx)
    return {"D": D, "R": R, "E": E, "S": S}


def counts_from(Qv):
    C = {}
    N = None
    for q in QS:
        V = Qv[q]
        N = V.shape[0]
        for w in range(4):
            v = V[:, w]
            for m in MODS:
                C["%s.w%d.m%d" % (q, w, m)] = np.bincount(v % m, minlength=m).astype(np.int64)
            for name, s in SUBS:
                C["%s.w%d.%s" % (q, w, name)] = np.array([np.count_nonzero(v % s == 0)], dtype=np.int64)
            pat = np.zeros(len(v), dtype=np.int64)
            for i, p in enumerate(PRIMES):
                pat |= (v % p == 0).astype(np.int64) << i
            C["%s.w%d.div" % (q, w)] = np.bincount(pat, minlength=32).astype(np.int64)
            for p, g in COSETS:
                r = v % p
                u = r[r != 0]
                C["%s.w%d.cos%d_%d" % (q, w, p, g)] = np.bincount(DLOG[p][u] % coset_index(p, g),
                                                                   minlength=coset_index(p, g)).astype(np.int64)
        for m in JMODS:
            idx = np.zeros(N, dtype=np.int64)
            for w in range(4):
                idx = idx * m + V[:, w] % m
            C["%s.joint.m%d" % (q, m)] = np.bincount(idx, minlength=m ** 4).astype(np.int64)
    C["N"] = np.array([N], dtype=np.int64)
    return C


def to_flat(C):
    return np.concatenate([C[k] for k, _ in layout()]).astype(np.uint64)


def _div_expect():
    e = np.zeros(32)
    for pat in range(32):
        pr = 1.0
        for i, p in enumerate(PRIMES):
            pr *= (1.0 / p) if (pat >> i & 1) else (1.0 - 1.0 / p)
        e[pat] = pr
    return e


DIVEXP = _div_expect()


def chi2_uniform(h):
    n = h.sum()
    e = n / len(h)
    c = float(((h - e) ** 2).sum() / e)
    return c, float(stats.chi2.sf(c, len(h) - 1)), len(h) - 1


def zero_test(c0, n, prob):
    mu = n * prob
    if mu < 30:   # Poisson, two-sided via doubling the smaller tail
        lo = stats.poisson.cdf(c0, mu)
        hi = stats.poisson.sf(c0 - 1, mu)
        p = min(1.0, 2 * min(lo, hi))
        z = (c0 - mu) / math.sqrt(mu) if mu > 0 else 0.0
    else:
        z = (c0 - mu) / math.sqrt(mu * (1 - prob))
        p = float(2 * stats.norm.sf(abs(z)))
    adv = math.log2(c0 / mu) if c0 > 0 else float("-inf")
    return z, p, adv


def evaluate(C, qs=QS):
    """All tests on one count set. Returns dict id -> dict(stat, p, eff, kind)."""
    N = int(C["N"][0])
    T = {}
    for q in qs:
        for w in range(4):
            for m in MODS:
                h = C["%s.w%d.m%d" % (q, w, m)]
                c, p, df = chi2_uniform(h)
                T["%s.w%d.m%d.chi" % (q, w, m)] = dict(kind="chi", stat=c, df=df, p=p,
                                                       eff=(c - df) / N)   # ~ 2*ln2*KL bits-ish per row
                z, p0, adv = zero_test(int(h[0]), N, 1.0 / m)
                T["%s.w%d.m%d.zero" % (q, w, m)] = dict(kind="zero", stat=z, p=p0, eff=adv, c0=int(h[0]), mu=N / m)
            for name, s in SUBS:
                c0 = int(C["%s.w%d.%s" % (q, w, name)][0])
                prob = (M // s) / M
                z, p0, adv = zero_test(c0, N, prob)
                T["%s.w%d.%s" % (q, w, name)] = dict(kind="sub", stat=z, p=p0, eff=adv, c0=c0, mu=N * prob)
            h = C["%s.w%d.div" % (q, w)]
            e = DIVEXP * N
            keep = e > 5
            c = float((((h - e) ** 2 / e)[keep]).sum())
            df = int(keep.sum()) - 1
            T["%s.w%d.div" % (q, w)] = dict(kind="chi", stat=c, df=df, p=float(stats.chi2.sf(c, df)), eff=(c - df) / N)
            for p_, g in COSETS:
                h = C["%s.w%d.cos%d_%d" % (q, w, p_, g)]
                c, p, df = chi2_uniform(h)
                T["%s.w%d.cos%d_%d" % (q, w, p_, g)] = dict(kind="chi", stat=c, df=df, p=p, eff=(c - df) / N)
        for m in JMODS:
            h = C["%s.joint.m%d" % (q, m)]
            c, p, df = chi2_uniform(h)
            T["%s.joint.m%d.chi" % (q, m)] = dict(kind="chi", stat=c, df=df, p=p, eff=(c - df) / N)
            z, p0, adv = zero_test(int(h[0]), N, 1.0 / m ** 4)
            T["%s.joint.m%d.zero" % (q, m)] = dict(kind="zero", stat=z, p=p0, eff=adv, c0=int(h[0]), mu=N / m ** 4)
    return T


def chi2_two(a, b):
    """Two-sample chi-square homogeneity test of histograms a (tested) and b (reference/control)."""
    a = a.astype(np.float64)
    b = b.astype(np.float64)
    Na, Nb = a.sum(), b.sum()
    s = a + b
    keep = s > 0
    k1, k2 = math.sqrt(Nb / Na), math.sqrt(Na / Nb)
    c = float((((k1 * a - k2 * b) ** 2)[keep] / s[keep]).sum())
    df = int(keep.sum()) - 1
    p = float(stats.chi2.sf(c, df)) if df > 0 else 1.0
    neff = Na * Nb / (Na + Nb)
    kl = max(0.0, c - df) / (2 * math.log(2) * neff)   # ~ KL(tested || reference) in bits per row
    return c, p, df, kl


def zero_two(a0, Na, b0, Nb):
    """Cell-0 frequency of the tested set vs the reference. Returns (z, p, adv bits, se of adv)."""
    n = a0 + b0
    if n == 0:
        return 0.0, 1.0, 0.0, float("inf")
    if n <= 100000:
        p = float(stats.binomtest(int(a0), int(n), Na / (Na + Nb)).pvalue)
    else:
        pp = n / (Na + Nb)
        z = (a0 / Na - b0 / Nb) / math.sqrt(pp * (1 - pp) * (1 / Na + 1 / Nb))
        p = float(2 * stats.norm.sf(abs(z)))
    pa, pb = a0 / Na, b0 / Nb
    z = (pa - pb) / math.sqrt(max(n / (Na + Nb) * (1 - n / (Na + Nb)), 1e-300) * (1 / Na + 1 / Nb))
    if a0 > 0 and b0 > 0:
        adv, se = math.log2(pa / pb), math.sqrt(1 / a0 + 1 / b0) / math.log(2)
    else:
        adv, se = (float("-inf") if a0 == 0 else float("inf")), float("inf")
    return z, p, adv, se


def evaluate2(C, Cref, qs=QS):
    """All tests of one count set against a reference count set (the control stream). id -> dict."""
    N, Nr = int(C["N"][0]), int(Cref["N"][0])
    T = {}
    for q in qs:
        for w in range(4):
            for m in MODS:
                k = "%s.w%d.m%d" % (q, w, m)
                c, p, df, kl = chi2_two(C[k], Cref[k])
                T[k + ".chi"] = dict(kind="chi", stat=c, df=df, p=p, eff=kl)
                z, p0, adv, se = zero_two(int(C[k][0]), N, int(Cref[k][0]), Nr)
                T[k + ".zero"] = dict(kind="zero", stat=z, p=p0, eff=adv, se=se, c0=int(C[k][0]), mu=N * Cref[k][0] / Nr)
            for name, s in SUBS:
                k = "%s.w%d.%s" % (q, w, name)
                a0, b0 = int(C[k][0]), int(Cref[k][0])
                if b0 == 0:   # reference saw none: compare with the exact uniform rate (M // s)/M
                    prob = (M // s) / M
                    z, p0, adv = zero_test(a0, N, prob)
                    se = float("inf")
                    mu = N * prob
                else:
                    z, p0, adv, se = zero_two(a0, N, b0, Nr)
                    mu = N * b0 / Nr
                T[k] = dict(kind="sub", stat=z, p=p0, eff=adv, se=se, c0=a0, mu=mu)
            for suffix in ["div"] + ["cos%d_%d" % pg for pg in COSETS]:
                k = "%s.w%d.%s" % (q, w, suffix)
                c, p, df, kl = chi2_two(C[k], Cref[k])
                T[k] = dict(kind="chi", stat=c, df=df, p=p, eff=kl)
        for m in JMODS:
            k = "%s.joint.m%d" % (q, m)
            c, p, df, kl = chi2_two(C[k], Cref[k])
            T[k + ".chi"] = dict(kind="chi", stat=c, df=df, p=p, eff=kl)
            z, p0, adv, se = zero_two(int(C[k][0]), N, int(Cref[k][0]), Nr)
            T[k + ".zero"] = dict(kind="zero", stat=z, p=p0, eff=adv, se=se, c0=int(C[k][0]), mu=N * Cref[k][0] / Nr)
    return T


def h2(v):
    """Renyi-2 entropy estimate from collisions; returns (H2 or None, distinct, top value, top freq)."""
    u, c = np.unique(v, return_counts=True)
    n = len(v)
    pairs = float((c.astype(np.float64) * (c - 1)).sum())
    i = int(np.argmax(c))
    H = -math.log2(pairs / (n * (n - 1.0))) if pairs > 0 else None
    return H, len(u), int(u[i]), int(c[i]) / n
