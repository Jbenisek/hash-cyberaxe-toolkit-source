"""Quick look (rotational lens): internal XOR differences of E1/E3 vs period-4 / all-ones patterns,
uniformity of digest side A. Exploratory only; the tested claims are in rotscan.c / classes.py."""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
U32 = np.uint32


def load(s, f, c):
    return np.fromfile(os.path.join(D, s, f), dtype="<u4").reshape(-1, c)


def hw(a):
    a = np.ascontiguousarray(a.astype(U32))
    return np.unpackbits(a.view(np.uint8).reshape(-1, 4), axis=1).sum(1)


P4 = np.array([int("%x" % n * 8, 16) for n in range(16)], dtype=U32)  # nibble repeated 8x


def d4(x):
    return np.min(np.stack([hw(x ^ p) for p in P4]), axis=0)


rng = np.random.default_rng(1)
ctrl = rng.integers(0, 2**32, size=1 << 20, dtype=np.uint64).astype(U32)
cd = d4(ctrl)
print("control d4 histogram (0..8):", np.bincount(cd, minlength=12)[:12])

for s in ("rand",):
    emid = load(s, "emid.u32", 16)
    eout = load(s, "eout.u32", 16)
    names_mid = ["E1 a1", "E1 b1", "E1 c1", "E1 d1", "E3 e1", "E3 f1", "E3 g1", "E3 h1"]
    names_out = ["E1 a2", "E1 b2", "E1 c2", "E1 d2", "E3 e2", "E3 f2", "E3 g2", "E3 h2"]
    for arr, names in ((emid, names_mid), (eout, names_out)):
        for blk in range(2):
            A = arr[:, 8 * blk: 8 * blk + 4]
            B = arr[:, 8 * blk + 4: 8 * blk + 8]
            for w in range(4):
                dx = A[:, w] ^ B[:, w]
                u, c = np.unique(dx, return_counts=True)
                top = np.argsort(-c)[:3]
                dd = d4(dx)
                print("%s  dXOR distinct %7d  top %s  meanHW %.2f  d4 hist %s" % (
                    names[4 * blk + w], len(u), ["%08x:%d" % (u[t], c[t]) for t in top], hw(dx).mean(),
                    np.bincount(dd, minlength=9)[:9]))
    dig = load(s, "dig.u32", 8)
    for w in range(8):
        col = dig[:, w]
        bits = ((col[:, None] >> np.arange(32, dtype=U32)) & 1).mean(0)
        print("dig col %d max bit bias %.4f at %d" % (w, np.abs(bits - .5).max(), np.abs(bits - .5).argmax()))
