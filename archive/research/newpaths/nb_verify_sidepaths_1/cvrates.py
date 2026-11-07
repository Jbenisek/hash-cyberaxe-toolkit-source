"""S8 check 2: do partial residual-event rates depend on the chaining value?

Vectorised (numpy) version of twoblock.build.  For each CV (IV/flags 11 = the filed single block, and three random
chained CVs/flags 10) draw N family members (7 uniform free words, y uniform in sub-class C15) and count partial
events of the residual r_i = digestA[i] XOR digestB[i], i = 1, 3, 4, 6.  Then compare across CVs (z-scores against
the pooled rate).  A few samples per CV are cross-checked against the organizer reference.
usage: python cvrates.py LOG2N SEED
"""
import struct
import sys

import numpy as np

import twoblock as tb
from verifier.blake3 import blake3 as ref, _compress

U = np.uint32
M = 0xFFFFFFFF
IV = tb.IV


def ror(x, r):
    return (x >> U(r)) | (x << U(32 - r))


def rol(x, r):
    return (x << U(r)) | (x >> U(32 - r))


def G(a, b, c, d, x, y):
    a = a + b + x; d = ror(d ^ a, 16); c = c + d; b = ror(b ^ c, 12)
    a = a + b + y; d = ror(d ^ a, 8); c = c + d; b = ror(b ^ c, 7)
    return a, b, c, d


def digest(cv, w, n, flags):
    N = w[0].shape[0]
    v = [np.full(N, cv[i], dtype=U) for i in range(8)] + [np.full(N, IV[i], dtype=U) for i in range(4)] + \
        [np.zeros(N, U), np.zeros(N, U), np.full(N, n, dtype=U), np.full(N, flags, dtype=U)]
    s = list(w)
    for _ in range(2):
        for (a, b, c, d), i in zip(((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
                                    (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)), range(8)):
            v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
        s = [s[p] for p in tb.PERM]
    return [v[i] ^ v[i + 8] for i in range(8)]


def build(cv, flags, Cc1, Cd1, D3d1, S15, S9, w5, X2, y):
    c = lambda x: U(x & M)  # noqa: E731
    K = (cv[2] + cv[6]) & M
    X3 = c(tb.T - tb.X7 + K); W4 = c(tb.Q - K); X7, X11, X15, W13 = c(tb.X7), c(tb.X11), c(tb.X15), c(tb.W13)
    k2d1 = tb.ror(55 ^ tb.Q, 16); k2c1 = (IV[2] + k2d1) & M; k2b1 = tb.ror(cv[6] ^ k2c1, 12)
    K2a1, K2d1, K2c1, K2b1 = c(tb.Q), c(k2d1), c(k2c1), c(k2b1)
    S2 = K2a1 + K2b1 + w5; S14 = ror(K2d1 ^ S2, 8)
    S10 = K2c1 + S14; S6 = ror(K2b1 ^ S10, 7)
    D3a1 = rol(D3d1, 16) ^ S14; D3c1 = S9 + D3d1
    D3b1 = X3 - D3a1; S4 = rol(D3b1, 12) ^ D3c1
    S3 = D3a1 - S4; X14 = ror(D3d1 ^ X3, 8)
    X9 = D3c1 + X14; X4 = ror(D3b1 ^ X9, 7)
    K3d1 = rol(S15, 8) ^ S3; K3c1 = c(IV[3]) + K3d1
    K3b1 = ror(c(cv[7]) ^ K3c1, 12); S11 = K3c1 + S15
    S7 = ror(K3b1 ^ S11, 7); K3a1 = rol(K3d1, 16) ^ c(flags)
    w6 = K3a1 - c(cv[3]) - c(cv[7]); w7 = S3 - K3a1 - K3b1
    X8 = Cc1 - Cd1; C0b1 = ror(X4 ^ Cc1, 12)
    D2b1 = rol(np.full_like(Cc1, X7), 7) ^ X8; D2c1 = rol(D2b1, 12) ^ S7
    X13 = X8 - D2c1
    D2a1 = X2 - D2b1 - W13; D2d1 = rol(X13, 8) ^ X2
    S13 = rol(D2d1, 16) ^ D2a1; S8 = D2c1 - D2d1
    w12 = D2a1 - S2 - S7
    K1c1 = S9 - S13; K1d1 = K1c1 - c(IV[1])
    K1a1 = rol(K1d1, 16); K1b1 = ror(c(cv[5]) ^ K1c1, 12)
    S1 = rol(S13, 8) ^ K1d1; S5 = ror(K1b1 ^ S9, 7)
    w2 = K1a1 - c(cv[1]) - c(cv[5]); w3 = S1 - K1a1 - K1b1
    K0b1 = rol(S4, 7) ^ S8; K0c1 = rol(K0b1, 12) ^ c(cv[4])
    K0d1 = K0c1 - c(IV[0]); K0a1 = rol(K0d1, 16)
    S12 = S8 - K0c1; S0 = rol(S12, 8) ^ K0d1
    w0 = K0a1 - c(cv[0]) - c(cv[4]); w1 = S0 - K0a1 - K0b1
    Y8 = rol(y, 7) ^ C0b1; Y12 = Y8 - Cc1
    Y0 = rol(Y12, 8) ^ Cd1; C0a1 = Y0 - C0b1 - w6
    X12 = rol(Cd1, 16) ^ C0a1
    D1c1 = X11 - X12; D1b1 = ror(S6 ^ D1c1, 12)
    D1d1 = D1c1 - S11
    X1 = rol(X12, 8) ^ D1d1
    X0 = C0a1 - X4 - w2
    D0d1 = rol(np.full_like(Cc1, X15), 8) ^ X0; D0c1 = S10 + D0d1
    D0b1 = ror(S5 ^ D0c1, 12)
    D0a1 = rol(D0d1, 16) ^ S15
    w8 = D0a1 - S0 - S5; w9 = X0 - D0a1 - D0b1
    D1a1 = rol(D1d1, 16) ^ S12; w10 = D1a1 - S1 - S6
    w11 = X1 - D1a1 - D1b1
    z = np.zeros_like(Cc1)
    wa = [w0, w1, w2, w3, np.full_like(Cc1, W4), w5, w6, w7, w8, w9, w10, w11, w12, np.full_like(Cc1, W13), z, z]
    W4B = c(((tb.Q ^ 8) - K) & M)
    wb = list(wa)
    wb[4] = np.full_like(Cc1, W4B)
    wb[5] = w5 + W4 - W4B
    return wa, wb, Y12


def members(rng, n):
    free = [i for i in range(32) if not tb.SUB_AND >> i & 1]
    k = rng.integers(0, 1 << 17, size=n, dtype=np.uint64)
    e1 = np.full(n, tb.CLASS_VAL, dtype=np.uint64)
    for j, p in enumerate(free):
        e1 |= ((k >> np.uint64(j)) & np.uint64(1)) << np.uint64(p)
    return ((e1 - np.uint64(tb.Y3A)) & np.uint64(M)).astype(U)


EVENTS = [
    ("r1 low8 = 0", lambda r: (r[1] & U(0xff)) == 0),
    ("r3 low8 = 0", lambda r: (r[3] & U(0xff)) == 0),
    ("r4 low8 = 0", lambda r: (r[4] & U(0xff)) == 0),
    ("r6 low8 = 0", lambda r: (r[6] & U(0xff)) == 0),
    ("r1,r3,r4,r6 low3 = 0 (12 bits)", lambda r: ((r[1] | r[3] | r[4] | r[6]) & U(7)) == 0),
    ("r1 top8 = 0", lambda r: (r[1] >> U(24)) == 0),
    ("r4 top8 = 0", lambda r: (r[4] >> U(24)) == 0),
]


def run(cv, flags, log2n, seed, b0=None, chunk=1 << 20):
    rng = np.random.default_rng(seed)
    n = 1 << log2n
    counts = np.zeros(len(EVENTS), dtype=np.int64)
    done = 0
    checked = 0
    while done < n:
        m = min(chunk, n - done)
        free = [rng.integers(0, 1 << 32, size=m, dtype=np.uint64).astype(U) for _ in range(7)] + [members(rng, m)]
        wa, wb, _ = build(cv, flags, *free)
        dA = digest(cv, wa, 55, flags)
        dB = digest(cv, wb, 63, flags)
        r = {i: dA[i] ^ dB[i] for i in range(8)}
        assert all(not np.any(r[i]) for i in (0, 2, 5, 7))
        for j, (_, f) in enumerate(EVENTS):
            counts[j] += int(np.count_nonzero(f(r)))
        if checked < 3:                         # cross-check against the organizer reference
            for t in range(3):
                A = struct.pack("<16I", *(int(w[t]) for w in wa))[:55]
                B = struct.pack("<16I", *(int(w[t]) for w in wb))[:63]
                mA = A if b0 is None else b0 + A
                mB = B if b0 is None else b0 + B
                assert struct.unpack("<8I", ref(mA, 2)) == tuple(int(x[t]) for x in dA)
                assert struct.unpack("<8I", ref(mB, 2)) == tuple(int(x[t]) for x in dB)
            checked += 1
        done += m
    return counts, n


def main():
    log2n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    prng = np.random.default_rng(seed + 1000)
    cvs = [("IV, flags 11 (filed single block)", IV, 11, None)]
    for t in range(3):
        b0 = bytes(int(x) for x in prng.integers(0, 256, size=64))
        cv = _compress(IV, struct.unpack("<16I", b0), 0, 64, 1, 2)[:8]
        cvs.append((f"chained CV {t + 1} ({cv[0]:08x}..), flags 10", cv, 10, b0))
    res = []
    for name, cv, flags, b0 in cvs:
        cnt, n = run(cv, flags, log2n, seed, b0)
        res.append(cnt)
        print(f"{name}: N = 2^{log2n}: " + ", ".join(f"{c}" for c in cnt), flush=True)
    res = np.array(res, dtype=float)
    pooled = res.sum(axis=0) / (len(cvs) * n)
    print("\nevent | pooled rate | per-CV z-scores against pooled (binomial)")
    for j, (ename, _) in enumerate(EVENTS):
        p = pooled[j]
        sd = np.sqrt(n * p * (1 - p)) if p > 0 else 1.0
        z = [(res[i, j] - n * p) / sd for i in range(len(cvs))]
        print(f"{ename:32s} | {p:.6e} (2^{np.log2(p) if p > 0 else float('-inf'):.3f}) | "
              + " ".join(f"{x:+.2f}" for x in z))


if __name__ == "__main__":
    main()
