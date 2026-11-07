"""Joint lens, step 0: exact GF(2) structure of the 128-bit residual R.
- affine rank of R (rand: whole set and each half; ctx: whole set, each context, each (context, member) group)
- the left null space (every exact affine relation a.R = const), printed as masks
- distinct values of dc1 = E1.c1 A^B and dg1 = E3.g1 A^B, and the word-parity identities derived in RESULT.md
Run: python explore0_rank.py > explore0_rank_out.txt"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
W = ("1", "3", "4", "6")


def load(name, f, cols):
    return np.fromfile(os.path.join(DATA, name, f), dtype="<u4").reshape(-1, cols)


def to_int_rows(res):
    # 128-bit row as python int: bit 32*w + b = bit b of word index w (order 1,3,4,6)
    r = res.astype(np.uint64)
    lo = r[:, 0] | (r[:, 1] << np.uint64(32))
    hi = r[:, 2] | (r[:, 3] << np.uint64(32))
    return lo, hi


def affine_basis(res):
    """Row-reduce {R_i ^ R_0} over GF(2); returns (rank, pivot basis as python ints)."""
    lo, hi = to_int_rows(res)
    base = (int(hi[0]) << 64) | int(lo[0])
    piv = {}  # top bit -> vector
    # process in chunks of python ints; stop early once rank 128
    for a, b in zip(lo.tolist(), hi.tolist()):
        v = ((b << 64) | a) ^ base
        while v:
            t = v.bit_length() - 1
            if t in piv:
                v ^= piv[t]
            else:
                piv[t] = v
                break
        if len(piv) == 128:
            break
    return len(piv), base, piv


def null_space(piv, base):
    """All masks a with a.(v) = 0 for every basis vector v; return list of (mask, const=a.base)."""
    # build reduced basis matrix and solve for orthogonal complement
    vecs = list(piv.values())
    # Gaussian elimination to reduced row echelon form
    rows = []
    for v in vecs:
        for r in rows:
            if v >> (r.bit_length() - 1) & 1:
                v ^= r
        if v:
            # reduce existing rows by v
            t = v.bit_length() - 1
            rows = [r ^ v if (r >> t) & 1 else r for r in rows]
            rows.append(v)
    pivots = {r.bit_length() - 1: r for r in rows}
    free = [b for b in range(128) if b not in pivots]
    out = []
    for f in free:
        a = 1 << f
        for t, r in pivots.items():
            if (r >> f) & 1:
                a |= 1 << t
        const = bin(a & base).count("1") & 1
        out.append((a, const))
    return out


def fmt_mask(a):
    return " ".join("w%s:%08x" % (W[w], (a >> (32 * w)) & 0xffffffff) for w in range(4))


def parity32(x):
    x = x.astype(np.uint32)
    x ^= x >> 16
    x ^= x >> 8
    x ^= x >> 4
    x ^= x >> 2
    x ^= x >> 1
    return x & 1


def ror(x, r):
    x = x.astype(np.uint32)
    return ((x >> np.uint32(r)) | (x << np.uint32((32 - r) % 32))).astype(np.uint32)


ETA = np.uint32(0x830303cf)


def main():
  for name in ("rand", "ctx"):
    res = load(name, "res.u32", 4)
    keys = load(name, "keys.u32", 8)
    emid = load(name, "emid.u32", 16)
    n = len(res)
    print("[%s] rows %d" % (name, n))
    groups = [("all", res), ("half0", res[: n // 2]), ("half1", res[n // 2:])]
    for g, sub in groups:
        rk, base, piv = affine_basis(sub)
        print("  affine rank of R (%s, %d rows): %d" % (g, len(sub), rk))
        if rk < 128:
            for a, c in null_space(piv, base):
                print("    relation: %s  = %d" % (fmt_mask(a), c))
    if name == "ctx":
        # 16 contexts x 16 members x 1024 rows
        rks = []
        for c in range(16):
            sub = res[c * 16384:(c + 1) * 16384]
            rks.append(affine_basis(sub)[0])
        print("  affine rank per context (16384 rows each):", rks)
        mrk = []
        for g in range(256):
            sub = res[g * 1024:(g + 1) * 1024]
            mrk.append(affine_basis(sub)[0])
        u, cnt = np.unique(mrk, return_counts=True)
        print("  affine rank per (context, member) group of 1024 rows: values", dict(zip(u.tolist(), cnt.tolist())))
    # dc1 and dg1 (E1.c1 is emid col 2 (A) and 6 (B); E3.g1 is emid col 10 (A) and 14 (B))
    dc1 = emid[:, 2] ^ emid[:, 6]
    dg1 = emid[:, 10] ^ emid[:, 14]
    dh1 = emid[:, 11] ^ emid[:, 15]
    u, cnt = np.unique(dc1, return_counts=True)
    print("  dc1 distinct %d; top:" % len(u), ", ".join("%08x:%d" % (a, b) for a, b in sorted(zip(u, cnt), key=lambda z: -z[1])[:6]))
    print("  dh1 distinct %d (expect 1, eta)" % len(np.unique(dh1)), "%08x" % dh1[0])
    print("  parity(dc1)=1 fraction %.6f   parity(dg1)=1 fraction %.6f" % (parity32(dc1).mean(), parity32(dg1).mean()))
    R1, R3, R4, R6 = (res[:, i] for i in range(4))
    pa = parity32(R3) ^ parity32(R6)
    pb = parity32(R1) ^ parity32(R4)
    print("  DERIVED parity(R3)^parity(R6) = parity(dc1)^1: holds on %d of %d" % (int((pa == (parity32(dc1) ^ 1)).sum()), n))
    print("  DERIVED parity(R1)^parity(R4) = parity(dg1):   holds on %d of %d" % (int((pb == parity32(dg1)).sum()), n))
    U1 = R6 ^ ror(R3, 8) ^ ror(np.array([ETA]), 8)[0]
    U3 = R4 ^ ror(R1, 8)
    K1, K3 = keys[:, :4], keys[:, 4:]
    U1k = K1[:, 3] ^ ror(K1[:, 1], 8)
    U3k = K3[:, 2] ^ ror(K3[:, 0], 8)
    print("  DERIVED R6^ROR(R3,8)^ROR(eta,8) = K1[6]^ROR(K1[3],8): %d of %d" % (int((U1 == U1k).sum()), n))
    print("  DERIVED R4^ROR(R1,8) = K3[4]^ROR(K3[1],8):            %d of %d" % (int((U3 == U3k).sum()), n))
    print("  P(R3,R6 word-parity sum = 0) = %.6f ; P(R1,R4 word-parity sum = 0) = %.6f" % ((pa == 0).mean(), (pb == 0).mean()))


if __name__ == "__main__":
    main()
