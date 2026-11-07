"""Quick look 2: rotational coordinates of R. U4 = R4 ^ ROR(R1,8) (E3-only), U6 = R6 ^ ROR(R3,8) (E1-only).
Per-word Renyi-2 entropy from collision pairs; hits of the eps targets. Exploratory."""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
U32 = np.uint32


def load(s, f, c):
    return np.fromfile(os.path.join(D, s, f), dtype="<u4").reshape(-1, c)


def ror(x, r):
    x = x.astype(U32)
    return ((x >> U32(r)) | (x << U32(32 - r))).astype(U32)


def h2(x):
    _, c = np.unique(x, return_counts=True)
    n = len(x)
    pairs = (c.astype(np.float64) * (c - 1) / 2).sum()
    return pairs, (-np.log2(pairs / (n * (n - 1) / 2)) if pairs else float("inf"))


def par(x):
    x = x.astype(U32)
    x ^= x >> U32(16); x ^= x >> U32(8); x ^= x >> U32(4); x ^= x >> U32(2); x ^= x >> U32(1)
    return x & U32(1)


for s in ("rand", "ctx"):
    R = load(s, "res.u32", 4)
    K = load(s, "keys.u32", 8)
    em = load(s, "emid.u32", 16)
    n = R.shape[0]
    U4 = R[:, 2] ^ ror(R[:, 0], 8)
    U6 = R[:, 3] ^ ror(R[:, 1], 8)
    print("[%s] n=%d  uniform expectation of collision pairs %.1f" % (s, n, n * (n - 1) / 2 / 2**32))
    for name, x in (("R1", R[:, 0]), ("R3", R[:, 1]), ("R4", R[:, 2]), ("R6", R[:, 3]), ("U4", U4), ("U6", U6),
                    ("K1w1", K[:, 0]), ("K1w3", K[:, 1]), ("K3w1", K[:, 4]), ("K3w3", K[:, 5])):
        p, h = h2(x)
        print("  %-5s collision pairs %10.0f  H2 %.2f" % (name, p, h))
    dc2 = K[:, 1]
    print("  dc2==6e21be55: %d   dc2==91de41aa: %d" % ((dc2 == 0x6e21be55).sum(), (dc2 == 0x91de41aa).sum()))
    df1 = em[:, 8 + 1] ^ em[:, 12 + 1]
    print("  parity(df1) even fraction %.4f" % (1 - par(df1).mean()))
    # U6 check against E1 formula
    C = 0xffb262c2
    u6f = U32(C) ^ ror(dc2, 7) ^ ror(dc2, 8)
    print("  U6 == C ^ ROR7(dc2) ^ ROR8(dc2): %s" % bool((u6f == U6).all()))
