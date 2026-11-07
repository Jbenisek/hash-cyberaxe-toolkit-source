"""Modular lens, part 4. Output: modrel_out.txt.
 J. the exact GF(2)-affine relations of the 128-bit XOR residual R found in modextra G (rank 126 at k=32):
    find them on rand rows [0,4096), print them, and test them on every rand and ctx row; their constants decide
    whether R = 0 satisfies them (0 -> two residual bits come free; 1 -> R = 0 impossible).
    The same search on the modular residual Rm bits, and on the uniform control.
 K. word 3: the modular input differences of the two halves nearly cancel modulo 2^20.
    dc1 = c1A - c1B (E1, constant) and de1 = e1A - e1B (E3, constant); word 3 = c2 ^ e2 with c2 = c1 + d2,
    e2 = e1 + f1 + w8, so M1.w3 + M3.w3 = (dc1 + de1) + dd2 + df1.
"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
W = ("1", "3", "4", "6")
E1IDX = (0, 2, 3, 1); E3IDX = (2, 0, 1, 3)


def load(name):
    dig = np.fromfile(os.path.join(DATA, name, "dig.u32"), dtype="<u4").reshape(-1, 8)
    eo = np.fromfile(os.path.join(DATA, name, "eout.u32"), dtype="<u4").reshape(-1, 16)
    em = np.fromfile(os.path.join(DATA, name, "emid.u32"), dtype="<u4").reshape(-1, 16)
    d = {"R": dig[:, :4] ^ dig[:, 4:], "Rm": (dig[:, :4] - dig[:, 4:]).astype(np.uint32), "eo": eo, "em": em}
    d["K1"] = np.stack([eo[:, i] ^ eo[:, 4 + i] for i in E1IDX], 1)
    d["K3"] = np.stack([eo[:, 8 + i] ^ eo[:, 12 + i] for i in E3IDX], 1)
    d["M1"] = np.stack([(eo[:, i] - eo[:, 4 + i]).astype(np.uint32) for i in E1IDX], 1)
    d["M3"] = np.stack([(eo[:, 8 + i] - eo[:, 12 + i]).astype(np.uint32) for i in E3IDX], 1)
    return d


X = load("rand"); Cx = load("ctx")
rng = np.random.default_rng(0x4D4F44554C415204)
CT = rng.integers(0, 1 << 32, size=X["R"].shape, dtype=np.uint64).astype(np.uint32)


def sec(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)


def to_int(row):
    v = 0
    for i, w in enumerate(row):
        v |= int(w) << (32 * i)
    return v


def nullspace_relations(arr, rows=4096):
    """affine GF(2) relations c with c.(r ^ r0) = 0 on the first `rows` rows; returns list of (c, const)."""
    nb = 32 * arr.shape[1]
    vecs = [to_int(r) for r in arr[:rows]]
    r0 = vecs[0]
    # row-reduce the difference vectors, tracking nothing; then nullspace via reduced echelon form
    basis = []  # list of (pivot, vec), fully reduced
    for v in vecs[1:]:
        v ^= r0
        for p, b in basis:
            if v >> p & 1:
                v ^= b
        if v:
            p = v.bit_length() - 1
            basis = [(q, (b ^ v) if (b >> p & 1) else b) for q, b in basis]
            basis.append((p, v))
    pivots = {p for p, _ in basis}
    rels = []
    for f in range(nb):
        if f in pivots:
            continue
        # relation vector: free bit f plus every pivot bit whose basis row has bit f
        c = 1 << f
        for p, b in basis:
            if b >> f & 1:
                c |= 1 << p
        rels.append(c)
    return [(c, bin(c & r0).count("1") & 1) for c in rels], len(basis)


def bits_of(c, nw=4):
    out = []
    for i in range(32 * nw):
        if c >> i & 1:
            out.append("w%s.b%d" % (W[i // 32], i % 32))
    return out


def check(arr, c):
    """value of the parity c.r on every row (vectorised)"""
    par = np.zeros(arr.shape[0], np.uint32)
    for i in range(arr.shape[1]):
        m = np.uint32((c >> (32 * i)) & 0xFFFFFFFF)
        x = arr[:, i] & m
        # parity of x
        x ^= x >> 16; x ^= x >> 8; x ^= x >> 4; x ^= x >> 2; x ^= x >> 1
        par ^= x & 1
    return par


sec("J. exact GF(2)-affine relations of the residual bits (128-bit rows; found on rand rows [0,4096))")
for nm in ("R", "Rm", "K1", "K3", "CTRL"):
    arr = CT if nm == "CTRL" else X[nm]
    rels, rk = nullspace_relations(arr)
    print("  %-4s rank %d/128, %d relation(s)" % (nm, rk, len(rels)))
    if nm in ("R", "Rm", "CTRL"):
        for c, k in rels:
            p_all = check(arr, c); p_ctx = None if nm == "CTRL" else check(Cx[nm], c)
            print("     relation: XOR of %s = %d" % (" ^ ".join(bits_of(c)), k))
            print("       holds on rand rows: %d/%d (value %s) ; ctx rows: %s" % (
                int((p_all == k).sum()), len(p_all), np.unique(p_all).tolist(),
                "-" if p_ctx is None else "%d/%d (value %s)" % (int((p_ctx == k).sum()), len(p_ctx), np.unique(p_ctx).tolist())))
            print("       => the zero residual R = 0 %s this relation" % ("SATISFIES" if k == 0 else "VIOLATES"))

sec("K. word 3: near-cancellation of the constant modular input differences modulo 2^20")
em, eo = X["em"], X["eo"]
dc1 = np.unique((em[:, 2] - em[:, 6]).astype(np.uint32)); de1 = np.unique((em[:, 8] - em[:, 12]).astype(np.uint32))
print("  dc1 = E1.c1 A-B values: %s ; de1 = E3.e1 A-B values: %s" % ([hex(v) for v in dc1], [hex(v) for v in de1]))
s = (int(dc1[0]) + int(de1[0])) % (1 << 32)
print("  dc1 + de1 = %08x ; mod 2^20 = %05x (= %d), signed mod 2^32 = %d" % (s, s & 0xFFFFF, s & 0xFFFFF, s - (1 << 32) if s >> 31 else s))
for k in (8, 12, 16, 20, 24, 28, 32):
    r = s % (1 << k); sg = r - (1 << k) if r >= (1 << (k - 1)) else r
    print("    mod 2^%d: residue %d  (|residue| / 2^k = %.5f; uniform expectation 0.25)" % (k, sg, abs(sg) / (1 << k)))
dd2 = (eo[:, 3] - eo[:, 7]).astype(np.uint32); df1 = (em[:, 9] - em[:, 13]).astype(np.uint32)
tot = (X["M1"][:, 1].astype(np.uint64) + X["M3"][:, 1]) & np.uint64(0xFFFFFFFF)
ok = np.array_equal(tot.astype(np.uint32), (np.uint32(s) + dd2 + df1).astype(np.uint32))
print("  identity M1.w3 + M3.w3 == (dc1+de1) + dd2 + df1 on every rand row: %s" % ok)
def sm(x, k):
    r = (x.astype(np.int64) & ((1 << k) - 1)); return np.where(r >= (1 << (k - 1)), r - (1 << k), r)
for k in (12, 16, 20):
    for nm, v in (("dd2", dd2), ("df1", df1), ("dd2+df1", (dd2 + df1).astype(np.uint32)), ("M1.w3+M3.w3", tot.astype(np.uint32)),
                  ("Rm.w3", X["Rm"][:, 1]), ("ctrl", CT[:, 1])):
        a = np.abs(sm(v, k)) / 2.0 ** k
        print("    mod 2^%d  %-12s  median |signed residue|/2^k %.4f   P(< 1/64) %.4f (uniform 0.0312)" % (k, nm, np.median(a), (a < 1 / 64).mean()))
# what the near-cancellation buys: P(low k bits of R word 3 zero) given the modular sum M1+M3 is small mod 2^k
for k in (8, 12, 16):
    m = np.uint32((1 << k) - 1)
    z = (X["R"][:, 1] & m) == 0
    small = np.abs(sm(tot.astype(np.uint32), k)) < (1 << (k - 4))
    print("  k=%d: P(R.w3 low k zero) %.3e (uniform %.3e) ; given |M1+M3 mod 2^k| < 2^(k-4): %.3e (rows %d) ; otherwise %.3e" % (
        k, z.mean(), 2.0 ** -k, z[small].mean(), int(small.sum()), z[~small].mean()))
# the same constants for the other words (where the input differences enter): word1 a2 vs g2, word4 d2 vs f2, word6 b2 vs h2
print("  other words: E1 / E3 input modular differences entering additively (A-B):")
print("    word 1: a2 = a1 + b1 + w5 (da1 = 0, dw5 = +8 for A-B) ; g2 = g1 + h2 ... (no constant)")
print("    word 6, word 4: enter through rotations only (b2 = ROR(b1^c2,7), d2 = ROR(d1^a2,8), f2 = ROR(f1^g2,7), h2 = ROR(h1^e2,8))")
