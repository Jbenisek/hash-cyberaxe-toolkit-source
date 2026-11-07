"""Period-4 class decomposition and rotation-adapted coordinates of the front-line residual (rotational lens).

Sets (each n x 4 u32, word order = digest words 1,3,4,6):
  R   residual (data/res.u32)
  RP  rotational coordinates (R1, R3, U4 = R4 ^ ROR(R1,8), U6 = R6 ^ ROR(R3,8)); a bijective GF(2)-linear map of R
  SH  control: R with each word column independently permuted (keeps one-word marginals, breaks cross-word links)
  U   control: uniform random words
Every number is computed separately on half T (train, first half of rows) and half V (test, second half).

Measures:
 1. Class bytes: word w, class c = bits {c, c+4, ..., c+28} packed into 8 bits. Plug-in Shannon entropy with the
    Miller-Madow correction, and P(byte = 0); the same for contiguous bytes.
 2. 16-bit chunk partitions of the 128 bits (8 chunks): sum of chunk entropies = an estimate of an upper bound on
    H(R) (subadditivity); deficit = 128 - sum. Class-based, contiguous and 24 random partitions (selection control).
 3. Class words: class c over all four words (32 bits): Renyi-2 entropy from collision pairs; zero count.
 4. Rotation filtration: per word, w mod (x+1)^m (m = 1..16) in the Pascal basis a_k = parity(w & S_k),
    S_k = {i : i AND k == k}; these quotients commute with every rotation and with XOR. Compared with the m low bits.
 5. Period-4 distance d4 (distance to the nearest nibble-repeated word) per word.
"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "data")
U32 = np.uint32
LN2 = np.log(2.0)


def load(s, f, c):
    return np.fromfile(os.path.join(D, s, f), dtype="<u4").reshape(-1, c)


def ror(x, r):
    x = x.astype(U32)
    return ((x >> U32(r)) | (x << U32(32 - r))).astype(U32)


def bits128(X):
    """n x 4 u32 -> n x 128 uint8, column 32*w + b = bit b of word w."""
    return np.unpackbits(np.ascontiguousarray(X.astype("<u4")).view(np.uint8).reshape(-1, 16), axis=1,
                         bitorder="little")


def ent_mm(vals, nb):
    c = np.bincount(vals, minlength=nb)
    n = c.sum()
    p = c[c > 0] / n
    return float(-(p * np.log2(p)).sum() + (len(p) - 1) / (2 * n * LN2)), int(c[0])


def chunk_vals(B, idx):
    w = (1 << np.arange(len(idx))).astype(np.int64)
    return (B[:, idx].astype(np.int64) @ w)


def collide(v):
    _, c = np.unique(v, return_counts=True)
    return float((c.astype(np.float64) * (c - 1) / 2).sum())


def cls_idx(w, c):
    return [32 * w + c + 4 * k for k in range(8)]


def byte_idx(w, b):
    return [32 * w + 8 * b + k for k in range(8)]


# ---- partitions (8 chunks of 16 bits) ----
PART = {}
PART["contig halfwords"] = [[32 * w + 16 * h + k for k in range(16)] for w in range(4) for h in range(2)]
PART["contig bytes {0,2}{1,3}"] = [byte_idx(w, b) + byte_idx(w, b + 2) for w in range(4) for b in range(2)]
PART["class {0,2}{1,3} in word"] = [cls_idx(w, c) + cls_idx(w, c + 2) for w in range(4) for c in range(2)]
PART["class {0,1}{2,3} in word"] = [cls_idx(w, c) + cls_idx(w, c + 1) for w in range(4) for c in (0, 2)]
for nm, prs in (("13|46", ((0, 1), (2, 3))), ("14|36", ((0, 2), (1, 3))), ("16|34", ((0, 3), (1, 2)))):
    PART["class c x words " + nm] = [cls_idx(a, c) + cls_idx(b, c) for (a, b) in prs for c in range(4)]
    PART["byte b x words " + nm] = [byte_idx(a, b) + byte_idx(bb, b) for (a, bb) in prs for b in range(4)]
rng = np.random.default_rng(0x524F54)
NRAND = 24
for q in range(NRAND):
    p = rng.permutation(128)
    PART["random %02d" % q] = [list(p[16 * k:16 * k + 16]) for k in range(8)]

# Pascal (Moebius) masks: a_k = parity(w & S_k)
SMASK = np.array([sum(1 << i for i in range(32) if (i & k) == k) for k in range(32)], dtype=np.uint64)


def parity32(x):
    x = x.astype(U32).copy()
    for s in (16, 8, 4, 2, 1):
        x ^= x >> U32(s)
    return (x & U32(1)).astype(np.int64)


def pascal(w, m):
    v = np.zeros(len(w), dtype=np.int64)
    for k in range(m):
        v |= parity32(w & U32(int(SMASK[k]))) << k
    return v


P4 = [int(("%x" % nb) * 8, 16) for nb in range(16)]


def d4(x):
    x = x.astype(U32)
    d = np.zeros(len(x), dtype=np.int64)
    for b in range(4):
        c = np.unpackbits((x & U32(0x11111111 << b)).view(np.uint8).reshape(-1, 4), axis=1).sum(1).astype(np.int64)
        d += np.minimum(c, 8 - c)
    return d


def keep_rows(name):
    """indices of the first copy of each distinct input row, in row order (ctx/ repeats 52 rows)."""
    inp = np.ascontiguousarray(load(name, "inputs.u32", 12))
    _, first = np.unique(inp.view(np.dtype((np.void, 48))).ravel(), return_index=True)
    return np.sort(first)


def sets_for(name):
    keep = keep_rows(name)
    R = load(name, "res.u32", 4)
    print("[%s] %d rows, %d after dropping repeated input rows" % (name, R.shape[0], len(keep)))
    R = R[keep]
    n = R.shape[0]
    RP = R.copy()
    RP[:, 2] = R[:, 2] ^ ror(R[:, 0], 8)
    RP[:, 3] = R[:, 3] ^ ror(R[:, 1], 8)
    g = np.random.default_rng(0x5348 + n)
    SH = np.stack([R[g.permutation(n), w] for w in range(4)], axis=1)
    U = g.integers(0, 2**32, size=(n, 4), dtype=np.uint64).astype(U32)
    return {"R": R, "RP": RP, "SH": SH, "U": U}


def main():
    for name in ("rand", "ctx"):
        S = sets_for(name)
        n = S["R"].shape[0]
        h = n // 2
        print("=" * 100)
        print("[%s] rows %d, halves T = rows [0,%d), V = rows [%d,%d)" % (name, n, h, h, n))
        res = {}
        for sn, X in S.items():
            for half, sl in (("T", slice(0, h)), ("V", slice(h, n))):
                Xh = X[sl]
                B = bits128(Xh)
                out = {}
                # 1. bytes
                cb = np.zeros((4, 4)); cz = np.zeros((4, 4)); kb = np.zeros((4, 4)); kz = np.zeros((4, 4))
                for w in range(4):
                    for c in range(4):
                        cb[w, c], cz[w, c] = ent_mm(chunk_vals(B, cls_idx(w, c)), 256)
                        kb[w, c], kz[w, c] = ent_mm(chunk_vals(B, byte_idx(w, c)), 256)
                out["cls_byte_H"] = cb; out["cls_byte_zero"] = cz; out["con_byte_H"] = kb; out["con_byte_zero"] = kz
                # per-bit
                pb = B.mean(0)
                out["bit_p1"] = pb
                # 2. partitions
                ph = {}; pz = {}
                for pn, chunks in PART.items():
                    hs = 0.0; zs = []
                    for idx in chunks:
                        hh, z = ent_mm(chunk_vals(B, idx), 1 << 16)
                        hs += hh; zs.append(z)
                    ph[pn] = 128 - hs; pz[pn] = zs
                out["part_def"] = ph; out["part_zero"] = pz
                # 3. class words (32 bits)
                cw = []
                for c in range(4):
                    v = chunk_vals(B, sum((cls_idx(w, c) for w in range(4)), []))
                    cw.append((collide(v), int((v == 0).sum())))
                out["cls_word"] = cw
                # 4. filtration per word
                fil = np.zeros((4, 17)); low = np.zeros((4, 17))
                for w in range(4):
                    x = Xh[:, w]
                    v = np.zeros(len(x), dtype=np.int64)
                    for m in range(1, 17):
                        v |= parity32(x & U32(int(SMASK[m - 1]))) << (m - 1)
                        fil[w, m] = m - ent_mm(v, 1 << m)[0]
                        low[w, m] = m - ent_mm((x & U32((1 << m) - 1)).astype(np.int64), 1 << m)[0]
                out["fil_def"] = fil; out["low_def"] = low
                jf = []
                for m in range(1, 5):
                    v = np.zeros(len(Xh), dtype=np.int64)
                    for w in range(4):
                        v |= pascal(Xh[:, w], m) << (m * w)
                    jf.append(4 * m - ent_mm(v, 1 << (4 * m))[0])
                out["fil_joint_def"] = jf
                # 5. d4
                out["d4"] = [d4(Xh[:, w]) for w in range(4)]
                res[(sn, half)] = out
        report(name, res, h)


def report(name, res, h):
    sets = ("R", "RP", "SH", "U")
    ph = lambda s, half: res[(s, half)]
    print("\n-- 1. per-bit: sum of single-bit entropy deficits (bits), and independent-bit log2 P(word = 0)")
    for s in sets:
        for half in ("T", "V"):
            p1 = ph(s, half)["bit_p1"]
            hb = -(p1 * np.log2(np.clip(p1, 1e-12, 1)) + (1 - p1) * np.log2(np.clip(1 - p1, 1e-12, 1)))
            lz = np.log2(np.clip(1 - p1, 1e-12, 1)).reshape(4, 32).sum(1)
            print("  %-3s %s  bit deficit total %7.3f  per word %s   indep-bit log2P(word=0) %s  total %.2f" % (
                s, half, 128 - hb.sum(), np.round(32 - hb.reshape(4, 32).sum(1), 3), np.round(lz, 2), lz.sum()))
    print("\n-- 1b. bytes: entropy deficit (8 - H_MM) per word; class bytes (bits = c mod 4) vs contiguous bytes")
    for s in sets:
        for half in ("T", "V"):
            o = ph(s, half)
            cd = 8 - o["cls_byte_H"]; kd = 8 - o["con_byte_H"]
            print("  %-3s %s  class-byte deficit per word %s total %.4f | contiguous-byte deficit per word %s total %.4f" % (
                s, half, np.round(cd.sum(1), 4), cd.sum(), np.round(kd.sum(1), 4), kd.sum()))
    print("    class-byte deficit matrix (rows words 1,3,4,6; cols class 0..3), set R, half T / V:")
    for half in ("T", "V"):
        print("     ", half, np.round(8 - ph("R", half)["cls_byte_H"], 4).tolist())
    print("    class-byte deficit matrix, set RP, half T / V:")
    for half in ("T", "V"):
        print("     ", half, np.round(8 - ph("RP", half)["cls_byte_H"], 4).tolist())
    print("    byte zero model: sum over 16 bytes of log2 P(byte = 0) (class bytes | contiguous bytes); uniform = -128")
    for s in sets:
        for half in ("T", "V"):
            o = ph(s, half)
            lc = np.log2(np.maximum(o["cls_byte_zero"], 0.5) / h).sum()
            lk = np.log2(np.maximum(o["con_byte_zero"], 0.5) / h).sum()
            print("  %-3s %s  class %.2f | contiguous %.2f" % (s, half, lc, lk))
    print("\n-- 2. 16-bit partitions: deficit = 128 - sum of chunk entropies (Miller-Madow). Larger = more structure seen.")
    names = [p for p in PART if not p.startswith("random")]
    for s in sets:
        T = ph(s, "T")["part_def"]; V = ph(s, "V")["part_def"]
        rT = np.array([T[p] for p in PART if p.startswith("random")])
        rV = np.array([V[p] for p in PART if p.startswith("random")])
        print("  set %s   random partitions: T mean %.3f sd %.3f max %.3f | V mean %.3f sd %.3f max %.3f" % (
            s, rT.mean(), rT.std(), rT.max(), rV.mean(), rV.std(), rV.max()))
        for p in names:
            print("     %-30s T %8.3f   V %8.3f" % (p, T[p], V[p]))
        best = max(PART, key=lambda p: T[p])
        print("     best on T: %s (T %.3f) -> V %.3f" % (best, T[best], V[best]))
    print("    16-bit zero counts per chunk (expected n/65536 = %.1f for uniform), set R and RP, half T / V:" % (h / 65536))
    for s in ("R", "RP", "U"):
        for p in ("contig halfwords", "class {0,2}{1,3} in word", "class c x words 13|46"):
            print("     %-3s %-26s T %s  V %s" % (s, p, ph(s, "T")["part_zero"][p], ph(s, "V")["part_zero"][p]))
    print("\n-- 3. class words (class c over all four words, 32 bits): collision pairs (uniform expects %.1f), H2, zeros" % (
        h * (h - 1) / 2 / 2**32))
    for s in sets:
        for half in ("T", "V"):
            cw = ph(s, half)["cls_word"]
            print("  %-3s %s  %s" % (s, half, "  ".join("c%d: %8.0f (H2 %.2f) z%d" % (
                c, cw[c][0], -np.log2(cw[c][0] / (h * (h - 1) / 2)) if cw[c][0] else 99, cw[c][1]) for c in range(4))))
    print("\n-- 4. rotation filtration: per-word deficit of w mod (x+1)^m (Pascal coords) vs the m low bits, m = 1..16")
    for s in sets:
        for half in ("T", "V"):
            o = ph(s, half)
            for w in range(4):
                print("  %-3s %s word %d  filt %s" % (s, half, (1, 3, 4, 6)[w], np.round(o["fil_def"][w, 1:], 3).tolist()))
                print("  %-3s %s word %d  low  %s" % (s, half, (1, 3, 4, 6)[w], np.round(o["low_def"][w, 1:], 3).tolist()))
            print("  %-3s %s joint 4 words, m=1..4 (4m bits): %s" % (s, half, np.round(o["fil_joint_def"], 4).tolist()))
    print("\n-- 5. d4 (distance to nearest period-4 word): mean per word, count d4<=4, two-sample z vs U")
    for s in sets:
        for half in ("T", "V"):
            o = ph(s, half); u = ph("U", half)
            row = []
            for w in range(4):
                a = o["d4"][w]; b = u["d4"][w]
                z = (a.mean() - b.mean()) / np.sqrt(a.var() / len(a) + b.var() / len(b))
                row.append("w%d mean %.4f le4 %d z %+.2f" % ((1, 3, 4, 6)[w], a.mean(), (a <= 4).sum(), z))
            print("  %-3s %s  %s" % (s, half, " | ".join(row)))


if __name__ == "__main__":
    main()
