"""Joint lens: upper bounds on the Shannon entropy of R in several coordinate systems (all are linear bijections of R).
Chow-Liu bound over the 16 aligned bytes: H(R) <= sum_i H(b_i) - sum_{edges of a spanning tree} I(b_i; b_j)
(chain rule with each byte conditioned only on its tree parent). The tree is the maximum-MI spanning tree chosen on the
TRAIN half; the bound is evaluated on the TEST half. Entropies are plug-in with the Miller-Madow correction.
Also: collision entropy H2 of each 32-bit coordinate word from the full 2^20 rows (single words; sums are a GUESS
of the joint H2 under independence of the words).
Coordinates:  raw     (R1, R3, R4, R6)
              spiral8 (R1, R3, U3 = R4^ROR(R1,8), U1 = R6^ROR(R3,8)^ROR(eta,8))
              spiral7 (R1, R3, Z7 = R4^ROR(R1,7), Q7 = R6^ROR(R3,7))
              mixed   (R1, R3, Z7, U1)
Control: uniform words, same count (raw coordinates).
Run: python entropy_bound.py > entropy_bound_out.txt"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
res = np.fromfile(os.path.join(HERE, "..", "data", "rand", "res.u32"), dtype="<u4").reshape(-1, 4)
N = len(res)
H = N // 2
ETA = np.uint32(0x830303cf)
LN2 = np.log(2)


def ror(x, r):
    return ((x >> np.uint32(r)) | (x << np.uint32(32 - r))).astype(np.uint32)


R1, R3, R4, R6 = (res[:, i] for i in range(4))
U3 = R4 ^ ror(R1, 8)
U1 = R6 ^ ror(R3, 8) ^ ror(np.array([ETA]), 8)[0]
Z7 = R4 ^ ror(R1, 7)
Q7 = R6 ^ ror(R3, 7)
rng = np.random.Generator(np.random.PCG64(0x454E54))
UN = rng.integers(0, 2**32, size=(N, 4), dtype=np.uint64).astype(np.uint32)
COORDS = {
    "raw": (("R1", R1), ("R3", R3), ("R4", R4), ("R6", R6)),
    "spiral8": (("R1", R1), ("R3", R3), ("U3", U3), ("U1", U1)),
    "spiral7": (("R1", R1), ("R3", R3), ("Z7", Z7), ("Q7", Q7)),
    "mixed": (("R1", R1), ("R3", R3), ("Z7", Z7), ("U1", U1)),
    "UNIFORM control": (("u0", UN[:, 0]), ("u1", UN[:, 1]), ("u2", UN[:, 2]), ("u3", UN[:, 3])),
}


def h_mm(counts, n):
    c = counts[counts > 0].astype(np.float64)
    p = c / n
    return float(-(p * np.log2(p)).sum() + (len(c) - 1) / (2 * n * LN2))


def h2_word(x):
    _, c = np.unique(x, return_counts=True)
    c = c.astype(np.float64)
    pairs = (c * (c - 1) / 2).sum()
    return -np.log2(pairs / (len(x) * (len(x) - 1) / 2)) if pairs else float("inf"), pairs


def stats(bytes_, n):
    hb = [h_mm(np.bincount(b, minlength=256), n) for b in bytes_]
    mi = np.zeros((16, 16))
    for i in range(16):
        for j in range(i + 1, 16):
            hij = h_mm(np.bincount(bytes_[i] * 256 + bytes_[j], minlength=65536), n)
            mi[i, j] = mi[j, i] = hb[i] + hb[j] - hij
    return np.array(hb), mi


def max_tree(mi):
    """Prim's algorithm, maximum spanning tree; returns list of edges (parent, child)."""
    inT = [0]
    edges = []
    while len(inT) < 16:
        best = None
        for a in inT:
            for b in range(16):
                if b in inT:
                    continue
                if best is None or mi[a, b] > mi[best[0], best[1]]:
                    best = (a, b)
        edges.append(best)
        inT.append(best[1])
    return edges


print("rows %d (train %d, test %d); 16 aligned bytes per coordinate system" % (N, H, H))
for name, words in COORDS.items():
    byts = [[((w[1][h * H:(h + 1) * H] >> np.uint32(8 * k)) & np.uint32(0xff)).astype(np.int64) for w in words for k in range(4)] for h in range(2)]
    hb_tr, mi_tr = stats(byts[0], H)
    hb_te, mi_te = stats(byts[1], H)
    T = max_tree(mi_tr)
    bound_te = hb_te.sum() - sum(mi_te[a, b] for a, b in T)
    bound_tr = hb_tr.sum() - sum(mi_tr[a, b] for a, b in T)
    lab = [w[0] + "b" + str(k) for w in words for k in range(4)]
    h2s = [h2_word(w[1]) for w in words]
    print("\n[%s]" % name)
    print("  sum of byte entropies: train %.3f  test %.3f bits" % (hb_tr.sum(), hb_te.sum()))
    print("  Chow-Liu bound (tree from train): train %.3f  TEST %.3f bits" % (bound_tr, bound_te))
    print("  strongest tree edges (test MI): " + ", ".join("%s-%s %.3f" % (lab[a], lab[b], mi_te[a, b]) for a, b in sorted(T, key=lambda e: -mi_te[e[0], e[1]])[:6]))
    print("  H2 per 32-bit word (all rows): " + ", ".join("%s %.2f" % (w[0], h[0]) for w, h in zip(words, h2s)) + "  ; sum %.2f (GUESS: joint H2 if the words were independent)" % sum(h[0] for h in h2s))
