"""TEST T3 (toy, COMPUTED): initial-state difference sources of a single BLAKE3 compression, LX09-style
absorption in round 0 (LX09 cancel IV differences h0,h2 with m0,m2; GKNWW14 sec. 6 note that BLAKE2 allows no
difference in v8..v11, v14, v15).  In BLAKE3 the only words of the initial state that two colliding root
compressions can differ in are v14 (block length) and v15 (flags: 11 for a one-block message, 12 for a parent
root).  Path F (new): one-block 64-byte message M versus a two-chunk message whose root parent compression has
message R = CV0||CV1; M copies R except m6, m7, which absorb dv15 = 11^12 in K3.  Control path L: the 55/63-type
length difference absorbed in K2 by m4, m5 (unpinned).
For random R (w = 8, 12, 16) we check that round 0 collides exactly and record which round-1 column outputs
differ; and per-output-word equality rates.  Toy: rotations floor(r*w/32), IV = low w bits, blen 2w.
Usage: python -B toy_flags.py N"""
import sys
import numpy as np
sys.dont_write_bytecode = True
U = np.uint64
IV32 = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]
COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def rots(w):
    return tuple((r * w) // 32 for r in (16, 12, 8, 7))


def vrotr(z, r, w):
    m = U((1 << w) - 1)
    return ((z >> U(r)) | (z << U(w - r))) & m if r % w else z & m


def vG(a, b, c, d, x, y, w):
    R = rots(w)
    m = U((1 << w) - 1)
    a = (a + b + x) & m; d = vrotr(d ^ a, R[0], w); c = (c + d) & m; b = vrotr(b ^ c, R[1], w)
    a = (a + b + y) & m; d = vrotr(d ^ a, R[2], w); c = (c + d) & m; b = vrotr(b ^ c, R[3], w)
    return a, b, c, d


def trace(M, w, blen, flags):
    N = M.shape[1]
    mk = (1 << w) - 1
    init = [x & mk for x in IV32] + [x & mk for x in IV32[:4]] + [0, 0, blen & mk, flags & mk]
    v = [np.full(N, s, dtype=U) for s in init]
    res = {}
    for r in range(2):
        s = [M[i] for i in range(16)] if r == 0 else [M[PERM[i]] for i in range(16)]
        for j, idx in enumerate(COLS):
            o = vG(*(v[i] for i in idx), s[2 * j], s[2 * j + 1], w)
            for i, t in zip(idx, o):
                v[i] = t
        if r == 1:
            res["Y"] = list(v)
        for j, idx in enumerate(DIAG):
            o = vG(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j], w)
            for i, t in zip(idx, o):
                v[i] = t
        if r == 0:
            res["X"] = list(v)
    res["out"] = [v[i] ^ v[i + 8] for i in range(8)]
    return res


def absorb(R, w, col, d_side, d_other):
    """Return M = R with words (2col, 2col+1) changed so that column call K_col of (M, d_other) equals that of
    (R, d_side): a1' = a1 ^ d_side ^ d_other keeps d^a1; y absorbs a1 - a1'."""
    mk = U((1 << w) - 1)
    ivw = [x & ((1 << w) - 1) for x in IV32]
    a, b = U(ivw[col]), U(ivw[col + 4])
    x, y = R[2 * col], R[2 * col + 1]
    a1 = (a + b + x) & mk
    a1p = a1 ^ U(d_side ^ d_other)
    M = R.copy()
    M[2 * col] = (a1p - a - b) & mk
    M[2 * col + 1] = (y + a1 - a1p) & mk
    return M


def run(w, N, rng):
    mk = (1 << w) - 1
    R = rng.integers(0, 1 << w, size=(16, N), dtype=np.int64).astype(U)
    out = []
    blen = (2 * w) & mk
    # path F: root parent (flags 12, blen 2w) vs one-block (flags 11, blen 2w); absorb dv15 in K3 (col 3)
    M = absorb(R, w, 3, 12, 11)
    tR = trace(R, w, blen, 12)
    tM = trace(M, w, blen, 11)
    # path L: lengths L1 = blen-9 (toy analog of 55) vs L2 = (L1 ^ 8); absorb dv14 in K2 (col 2)
    L1 = (blen - 9) & mk
    L2 = L1 ^ 8
    M2 = absorb(R, w, 2, L1, L2)
    tR2 = trace(R, w, L1, 11)
    tM2 = trace(M2, w, L2, 11)
    for name, a, b in (("F_flags_11v12", tR, tM), ("L_len_xor8", tR2, tM2)):
        xeq = all(bool(np.all(a["X"][i] == b["X"][i])) for i in range(16))
        dY = [(a["Y"][i] != b["Y"][i]) for i in range(16)]
        rate_nonzero = [float(np.mean(d)) for d in dY]
        halfA_inputs_zero = np.ones(N, dtype=bool)
        for i in (0, 5, 10, 15, 2, 7, 8, 13):
            halfA_inputs_zero &= ~dY[i]
        halfB_inputs_zero = np.ones(N, dtype=bool)
        for i in (1, 6, 11, 12, 3, 4, 9, 14):
            halfB_inputs_zero &= ~dY[i]
        weq = [float(np.mean(a["out"][i] == b["out"][i])) * (1 << w) for i in range(8)]
        out.append(f"w={w:2d} N={N} {name:14s} round0 state equal for all: {xeq}\n"
                   f"   P[dY_i != 0] i=0..15: " + " ".join(f"{r:.3f}" for r in rate_nonzero) + "\n"
                   f"   P[E0,E2 inputs Y0,Y5,Y10,Y15,Y2,Y7,Y8,Y13 all equal] = {np.mean(halfA_inputs_zero):.3e}   "
                   f"P[E1,E3 state inputs all equal] = {np.mean(halfB_inputs_zero):.3e}\n"
                   f"   P[out_i equal] x 2^w, i=0..7: " + " ".join(f"{x:.2f}" for x in weq))
    return out


if __name__ == "__main__":
    N = int(sys.argv[1])
    rng = np.random.default_rng(7)
    lines = []
    for w in (8, 12, 16):
        lines += run(w, N, rng)
        print(lines[-2]); print(lines[-1])
    with open("toy_flags.txt", "w") as fh:
        fh.write(__doc__ + "\n" + "\n".join(lines) + "\n")
