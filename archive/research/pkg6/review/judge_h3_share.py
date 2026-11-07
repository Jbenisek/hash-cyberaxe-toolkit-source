#!/usr/bin/env python3
"""Review helper (lens: judge). One thread, processor only. Reads proof text only; writes review/judge_h3_share.txt.

Question (H3 and the limits of the text): the share of the trials that satisfy rule A is measured in the package
only for independent random contexts (2,048 on the processor for all five conditions). A run of the algorithm is
different in three ways: all its contexts share the four seed words S11, S4, X13, w0; vd is below 2^19; and the
contexts of one pair (vc, vd) differ in X14 only. This script measures the share, with all members of the class,
for (a) independent random contexts, (b) the same with vd < 2^19, (c) contexts that share their seed words, with
vc random, vd < 2^19 and X14 random (several seed sets), (d) contexts that share seed words and the pair (vc, vd),
with X14 random (several pairs).

The context (step S1), the trial (step T) and h1 are written here from proof.md Sections 1, 4 and 6 alone, not
from the package's program or the reference. They are checked first on real messages with the organizer's
reference hash (verifier/blake3.py, 2 rounds): lengths 55 and 63, zero bytes 55..63, digest words 0, 2, 5, 7
equal, Y4 = y, and h1 of the vector code equal to h1 of a forward compression.
"""
import math
import sys
import time
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
WORK = HERE.parent.parent.parent
sys.path.insert(0, str(WORK / "hash-smash"))
from verifier.blake3 import blake3 as organizer_blake3      # noqa: E402

M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
X3, X7, X11, X15, W4, W13 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006
K = (IV[2] + IV[6]) & M
W4B = (((K + W4) ^ 8) - K) & M
Y3 = 0x8127C181
QMASK, QVALUE = 0x03CF8303, 0x030C0303
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))
    print(out[-1][:200], flush=True) if len(out) <= 3 else None


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def step_s1(vc, vd, S11, S4, X13, X14, w0):
    """proof.md, Step S1, line by line (scalars)."""
    ka = (IV[0] + IV[4] + w0) & M; kd = ror(ka, 16); kc = (IV[0] + kd) & M
    kb = ror(IV[4] ^ kc, 12)
    S8 = rol(S4, 7) ^ kb; S12 = (S8 - kc) & M; S0 = rol(S12, 8) ^ kd
    w1 = (S0 - ka - kb) & M
    X8 = (vc - vd) & M; tc = (X8 - X13) & M; td = (tc - S8) & M; tb = rol(X7, 7) ^ X8
    S7 = rol(tb, 12) ^ tc; X2 = rol(X13, 8) ^ td
    ta = (X2 - tb - W13) & M; S13 = rol(td, 16) ^ ta
    mb = rol(S7, 7) ^ S11; mc = rol(mb, 12) ^ IV[7]; md = (mc - IV[3]) & M
    S15 = (S11 - mc) & M; S3 = rol(S15, 8) ^ md; ma = rol(md, 16) ^ 11
    w6 = (ma - IV[3] - IV[7]) & M; w7 = (S3 - ma - mb) & M
    p = (K + W4) & M; q = ror(p ^ 55, 16); r = (IV[2] + q) & M
    u = ror(IV[6] ^ r, 12)
    ea = (S3 + S4) & M; eb = (X3 - ea) & M; ec = rol(eb, 12) ^ S4
    ed = rol(X14, 8) ^ X3; S9 = (ec - ed) & M; S14 = rol(ed, 16) ^ ea
    X9 = (ec + X14) & M; X4 = ror(eb ^ X9, 7)
    S10 = (r + S14) & M; S6 = ror(u ^ S10, 7); S2 = rol(S14, 8) ^ q
    w5 = (S2 - p - u) & M
    w12 = (ta - S2 - S7) & M
    nc = (S9 - S13) & M; nd = (nc - IV[1]) & M; na = rol(nd, 16)
    nb = ror(IV[5] ^ nc, 12); S1 = rol(S13, 8) ^ nd
    S5 = ror(nb ^ S9, 7); w2 = (na - IV[1] - IV[5]) & M; w3 = (S1 - na - nb) & M
    vb = ror(X4 ^ vc, 12)
    return dict(vc=vc, vd=vd, S11=S11, S4=S4, X13=X13, X14=X14, w0=w0, w1=w1, w2=w2, w3=w3, w5=w5, w6=w6, w7=w7,
                w12=w12, S0=S0, S1=S1, S5=S5, S6=S6, S10=S10, S12=S12, S15=S15, X2=X2, X4=X4, vb=vb)


def step_t(c, y):
    """proof.md, Step T, line by line (scalars): the four words w8..w11."""
    Y8 = rol(y, 7) ^ c["vb"]; Y12 = (Y8 - c["vc"]) & M; Y0 = rol(Y12, 8) ^ c["vd"]
    va = (Y0 - c["vb"] - c["w6"]) & M; X0 = (va - c["X4"] - c["w2"]) & M; X12 = rol(c["vd"], 16) ^ va
    fd = rol(X15, 8) ^ X0; fc = (c["S10"] + fd) & M; X10 = (fc + X15) & M
    fb = ror(c["S5"] ^ fc, 12)
    fa = rol(fd, 16) ^ c["S15"]; w8 = (fa - c["S0"] - c["S5"]) & M; w9 = (X0 - fa - fb) & M
    gc = (X11 - X12) & M; gb = ror(c["S6"] ^ gc, 12)
    gd = (gc - c["S11"]) & M; X1 = rol(X12, 8) ^ gd
    ga = rol(gd, 16) ^ c["S12"]; w10 = (ga - c["S1"] - c["S6"]) & M; w11 = (X1 - ga - gb) & M
    return w8, w9, w10, w11


def g(v, a, b, c, d, x, y):
    v[a] = (v[a] + v[b] + x) & M; v[d] = ror(v[d] ^ v[a], 16)
    v[c] = (v[c] + v[d]) & M; v[b] = ror(v[b] ^ v[c], 12)
    v[a] = (v[a] + v[b] + y) & M; v[d] = ror(v[d] ^ v[a], 8)
    v[c] = (v[c] + v[d]) & M; v[b] = ror(v[b] ^ v[c], 7)


def forward(w, n):
    """Section 1: the 2-round compression of one block of length n; returns (digest words, Y4, h1 of E3)."""
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    g(v, 0, 4, 8, 12, w[0], w[1]); g(v, 1, 5, 9, 13, w[2], w[3]); g(v, 2, 6, 10, 14, w[4], w[5]); g(v, 3, 7, 11, 15, w[6], w[7])
    g(v, 0, 5, 10, 15, w[8], w[9]); g(v, 1, 6, 11, 12, w[10], w[11]); g(v, 2, 7, 8, 13, w[12], w[13]); g(v, 3, 4, 9, 14, w[14], w[15])
    x_state = list(v)
    g(v, 0, 4, 8, 12, w[2], w[6]); g(v, 1, 5, 9, 13, w[3], w[10]); g(v, 2, 6, 10, 14, w[7], w[0]); g(v, 3, 7, 11, 15, w[4], w[13])
    y4 = v[4]
    h1 = ror(v[14] ^ ((v[3] + v[4] + w[15]) & M), 16)
    g(v, 0, 5, 10, 15, w[1], w[11]); g(v, 1, 6, 11, 12, w[12], w[5]); g(v, 2, 7, 8, 13, w[9], w[14]); g(v, 3, 4, 9, 14, w[15], w[8])
    return [v[i] ^ v[i + 8] for i in range(8)], y4, h1, x_state


def rules(h1):
    b = lambda i: (h1 >> i) & 1
    r4 = (b(0) == 0) & (b(1) == 1) & (b(16) == 0) & (b(17) == 0)
    r5 = r4 & ((b(2) ^ b(3)) == 1)
    r6 = r5 & ((b(7) ^ b(8)) == 1)
    return r4, r5, r6


# ---- the class as an array, and the vector form of what rule A needs
def subsets(mask):
    bits = [i for i in range(32) if mask >> i & 1]
    idx = np.arange(1 << len(bits), dtype=np.uint32)
    res = np.zeros(1 << len(bits), dtype=np.uint32)
    for j, b in enumerate(bits):
        res |= ((idx >> np.uint32(j)) & np.uint32(1)) << np.uint32(b)
    return res


E1 = subsets(~QMASK & M) | np.uint32(QVALUE)
YS = E1 - np.uint32(Y3)                       # members of the class (wraps modulo 2^32)
U32 = np.uint32


def vror(v, n):
    return (v >> U32(n)) | (v << U32(32 - n))


def vrol(v, n):
    return vror(v, 32 - n)


def h1_vector(c):
    """h1 of every member for one context: steps T and C2 as far as needed, then h1 = ROR(Y14 XOR e1, 16)."""
    Y8 = vrol(YS, 7) ^ U32(c["vb"]); Y12 = Y8 - U32(c["vc"]); Y0 = vrol(Y12, 8) ^ U32(c["vd"])
    va = Y0 - U32((c["vb"] + c["w6"]) & M); X0 = va - U32((c["X4"] + c["w2"]) & M); X12 = U32(rol(c["vd"], 16)) ^ va
    fd = U32(rol(X15, 8)) ^ X0; fc = U32(c["S10"]) + fd; X10 = fc + U32(X15)
    gc = U32(X11) - X12; gb = vror(U32(c["S6"]) ^ gc, 12); X6 = vror(gb ^ U32(X11), 7)
    a1 = U32(c["X2"]) + X6 + U32(c["w7"]); d1 = vror(U32(c["X14"]) ^ a1, 16); c1 = X10 + d1
    b1 = vror(X6 ^ c1, 12); a2 = a1 + b1 + U32(c["w0"]); Y14 = vror(d1 ^ a2, 8)
    return vror(Y14 ^ E1, 16)


def chi2_sf(x, k):
    """P(chi-square with k degrees of freedom > x), by the series of the lower incomplete gamma function."""
    if x <= 0:
        return 1.0
    a, s, term, n = k / 2.0, 0.0, 1.0 / (k / 2.0), 0
    xx = x / 2.0
    while True:
        s += term
        n += 1
        term *= xx / (a + n)
        if term < 1e-17 * s or n > 100000:
            break
    return max(0.0, 1.0 - s * math.exp(-xx + a * math.log(xx) - math.lgamma(a)))


rng = np.random.default_rng(20261006)
word = lambda: int(rng.integers(0, 1 << 32))

# ---- 0. the construction from the text, on real messages
t0 = time.time()
checks = dict(trials=0, lengths=0, zero=0, half=0, y4=0, h1=0, own=0, pin=0, eta=0)
idx_test = rng.integers(0, 1 << 19, size=3)
for i in range(400):
    c = step_s1(*(word() for _ in range(7)))
    hv = h1_vector(c) if i < 60 else None
    for j in range(3):
        outside = (i % 4 == 3)
        y = word() if outside else int(YS[idx_test[j]])
        w8, w9, w10, w11 = step_t(c, y)
        w = [c["w0"], c["w1"], c["w2"], c["w3"], W4, c["w5"], c["w6"], c["w7"], w8, w9, w10, w11, c["w12"], W13, 0, 0]
        wb = list(w); wb[4] = W4B; wb[5] = (c["w5"] + W4 - W4B) & M
        enc_a = b"".join(x.to_bytes(4, "little") for x in w)
        enc_b = b"".join(x.to_bytes(4, "little") for x in wb)
        A, B = enc_a[:55], enc_b[:63]
        da, db = organizer_blake3(A, 2), organizer_blake3(B, 2)
        wa = [int.from_bytes(da[4 * k:4 * k + 4], "little") for k in range(8)]
        wbd = [int.from_bytes(db[4 * k:4 * k + 4], "little") for k in range(8)]
        oa, y4a, h1a, xa = forward(w, 55)
        ob, y4b, h1b, xb = forward(wb, 63)
        checks["trials"] += 1
        checks["lengths"] += len(A) == 55 and len(B) == 63 and A != B
        checks["zero"] += enc_a[55:] == bytes(9) and enc_b[55:] == bytes(9) and B[55:] == bytes(8)
        checks["half"] += all(wa[k] == wbd[k] for k in (0, 2, 5, 7))
        checks["own"] += oa == wa and ob == wbd
        checks["y4"] += y4a == y and y4b == y
        checks["pin"] += xa == xb and (xa[3], xa[7], xa[11], xa[15]) == (X3, X7, X11, X15)
        if not outside:
            checks["eta"] += (h1a ^ h1b) == 0x830303CF
            if hv is not None:
                checks["h1"] += int(hv[idx_test[j]]) == h1a
say(f"0. construction from the text on real messages (organizer's 2-round hash): {checks}")

# ---- the measurements
def share(c):
    r4, r5, r6 = rules(h1_vector(c))
    return int(r4.sum()), int(r5.sum()), int(r6.sum())


def block(name, contexts):
    a = np.array([share(c) for c in contexts], dtype=np.float64)
    n = len(a)
    res = []
    for k, (cond, p) in enumerate(((4, 1 / 16), (5, 1 / 32), (6, 1 / 64))):
        x = a[:, k] / 524288 / p
        res.append(f"rule {cond}: mean {x.mean():.5f} +- {x.std(ddof=1) / math.sqrt(n):.5f} of 2^-{cond} "
                   f"(s.d. of one context {x.std(ddof=1):.4f}, min {x.min():.3f}, max {x.max():.3f})")
    say(f"{name}: {n} contexts | " + " | ".join(res))
    return a


NA = int(sys.argv[1]) if len(sys.argv) > 1 else 1536
NS, PER = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (12, 256)
A = block("a. independent random contexts", [step_s1(*(word() for _ in range(7))) for _ in range(NA)])
Bq = block("b. independent, vd < 2^19", [step_s1(word(), int(rng.integers(0, 1 << 19)), word(), word(), word(), word(), word())
                                         for _ in range(NA)])
for label, fixed_pair in (("c. shared seed words (S11, S4, X13, w0); vc random, vd < 2^19, X14 random", False),
                          ("d. shared seed words and one pair (vc, vd < 2^19); X14 random", True)):
    means, within = [], []
    allc = []
    for s in range(NS):
        S11, S4, X13, w0 = word(), word(), word(), word()
        vc, vd = word(), int(rng.integers(0, 1 << 19))
        ctxs = [step_s1(vc if fixed_pair else word(), vd if fixed_pair else int(rng.integers(0, 1 << 19)), S11, S4, X13, word(), w0)
                for _ in range(PER)]
        a = np.array([share(c) for c in ctxs], dtype=np.float64)
        allc.append(a)
        means.append(a.mean(axis=0)); within.append(a.var(axis=0, ddof=1))
    means, within = np.array(means), np.array(within)
    for k, (cond, p) in enumerate(((4, 1 / 16), (5, 1 / 32), (6, 1 / 64))):
        rel = means[:, k] / 524288 / p
        se = math.sqrt(within[:, k].mean() / PER) / 524288 / p
        chi = float(((rel - rel.mean()) ** 2).sum() / se ** 2)
        say(f"{label} | rule {cond}: {NS} sets x {PER} contexts; mean over all {rel.mean():.5f} of 2^-{cond}; "
            f"set means from {rel.min():.5f} to {rel.max():.5f} (standard error of one set mean {se:.5f}); "
            f"homogeneity chi-square {chi:.1f} on {NS - 1}, p {chi2_sf(chi, NS - 1):.3f}; "
            f"largest set mean against the budget 1.142: {rel.max():.4f}")
say(f"budget of H3: 74,899 * 2^81 / 2^102 = {74899 / 2 ** 21 * 32:.5f} times 2^-5; seconds {time.time() - t0:.0f}")
(HERE / "judge_h3_share.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{len(out)} lines -> judge_h3_share.txt")
