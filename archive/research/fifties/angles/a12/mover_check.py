"""A12: is the ANGLES angle-1 chunk-index mover the counter construction's trial?
Imports the package program halfsearch.py read-only. CPU, seconds.
For 64 bases (outer steps of Section 8) x 2^10 movers each:
  (a) post-round-0 state of the mover block (counter t', flags 3) equals the base's;
  (b) the mover (w0', w1', t') equals ctr_trial(o, c1') for c1' read back through C2/E1 (Lemma IP);
  (c) the per-base filter inputs Y4, Y9, omega, C2.b1, C2.c1, and Y1, Y12 (read by E1) do not change;
  (d) c1' in Q* exactly when E1's b XOR-difference A vs B is beta* (Theorem C (iv)), and the share in Q*.
"""

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

import hashlib, struct, sys, os
sys.dont_write_bytecode = True  # never leave __pycache__ in the package folder
PKG = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCD/pkg/blake3-r2/experiments')
sys.path.insert(0, PKG)
import halfsearch as H

M = H.MASK
def round0(block_words, counter, n, flags):
    v = list(H.IV) + list(H.IV[:4]) + [counter & M, counter >> 32, n, flags]
    s = block_words
    for (a, b, c, d), i in zip(H.G_CALLS, range(8)):
        v[a], v[b], v[c], v[d] = H.g(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
    return v
def words_of(block):
    return list(struct.unpack("<16I", block))
def inv_c1(o, w0):
    y2 = (w0 + o["C2.a1"] + o["C2.b1"]) & M
    y14 = H.ror(y2 ^ o["C2.d1"], 8)
    y10 = (y14 + o["C2.c1"]) & M
    y6 = H.ror(y10 ^ o["C2.b1"], 7)
    a1 = (y6 + o["Y1"] + o["w12"]) & M
    d1 = H.ror(a1 ^ o["Y12"], 16)
    return (d1 + H.Y11) & M
def e1_b(y, w):
    a1 = (y[1] + y[6] + w[12]) & M
    c1 = (y[11] + H.ror(y[12] ^ a1, 16)) & M
    return H.ror(y[6] ^ c1, 12)

def rnd(tag, i, n=4):
    return struct.unpack("<%dI" % n, hashlib.shake_256(("a12 %s %d" % (tag, i)).encode()).digest(4 * n))

BASES, MOVERS = 64, 1 << 10
stats = dict(post0_same=0, trial_same=0, base_inv_same=0, inQ=0, beta_iff=0, movers=0, skipped_t0=0)
for b in range(BASES):
    eight = list(rnd("base", b, 8))
    o = H.ctr_outer(eight)
    # a base trial at a random c1 with t != 0
    k = 0
    while True:
        c1 = rnd("c1", b * 1000 + k, 1)[0]; k += 1
        r = H.ctr_trial(o, c1)
        if r is not None:
            break
    A, B, t, v = r
    wA = words_of(A)
    X = round0(wA, t, H.LEN_A, H.CTR_FLAGS)
    omega = (H.Y3 + o["Y4"] + o["w8"]) & M
    base_inv = (o["Y4"], o["Y9"], omega, o["C2.b1"], o["C2.c1"], o["Y1"], o["Y12"])
    for j in range(MOVERS):
        t2 = rnd("t", b * MOVERS + j, 1)[0]
        if t2 == 0:
            stats["skipped_t0"] += 1; continue
        stats["movers"] += 1
        a1 = v["K0.a1"]; a1p = a1 ^ t ^ t2
        w = list(wA)
        w[0] = (a1p - H.IV[0] - H.IV[4]) & M
        w[1] = (w[1] + a1 - a1p) & M
        X2 = round0(w, t2, H.LEN_A, H.CTR_FLAGS)
        stats["post0_same"] += int(X2 == X)
        c1p = inv_c1(o, w[0])
        r2 = H.ctr_trial(o, c1p)
        stats["trial_same"] += int(r2 is not None and r2[2] == t2 and words_of(r2[0]) == w)
        # full compressions of the mover's A and B blocks
        Ab = struct.pack("<16I", *w)
        wb = list(w); wb[4], wb[5] = H.W4B, (w[5] + H.DELTA5) & M
        Bb = struct.pack("<16I", *wb)
        (wa, da, ya), (wbb, db, yb) = H.compress2(Ab[:H.LEN_A], t2, H.CTR_FLAGS), H.compress2(Bb[:H.LEN_B], t2, H.CTR_FLAGS)
        # C2 first half from X (reads X2,X6,X10,X14,w7 only)
        ca = (X[2] + X[6] + w[7]) & M; cd = H.ror(X[14] ^ ca, 16); cc = (X[10] + cd) & M; cb = H.ror(X[6] ^ cc, 12)
        om2 = (H.Y3 + ya[4] + w[8]) & M
        stats["base_inv_same"] += int((ya[4], ya[9], om2, cb, cc, ya[1], ya[12]) == base_inv)
        inq = (c1p & H.CTR_MASK) == H.CTR_VALUE
        stats["inQ"] += int(inq)
        is_beta = (e1_b(ya, wa) ^ e1_b(yb, wbb)) == H.CTR_BETA
        stats["beta_iff"] += int(inq == is_beta)
print(stats)
n = stats["movers"]
print("expected in Q* at 2^-11: %.1f, seen %d" % (n / 2048, stats["inQ"]))
