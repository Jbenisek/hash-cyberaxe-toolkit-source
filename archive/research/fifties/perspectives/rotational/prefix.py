"""Zero-prefix profile of the rotational coordinates of R: for m = 1..32, the fraction of rows whose low m bits are
all zero (and, separately, whose high m bits are all zero). Uniform 32-bit word: 2^-m. Train/test halves.
Coordinates (identities.py): R1, R3, R4, R6, U4 = R4^ROR(R1,8), U6 = R6^ROR(R3,8) (E1 only),
W3 = R3^ROL(R6,7) (E3 only), W4 = R4^ROR(R1,7).
Also dc2 ^ eps and de2 ^ eps for both solutions eps of x ^ ROR(x,1) = db1 ^ ROR(eta,1)."""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
U32 = np.uint32
EPS = (0x6E21BE55, 0x91DE41AA)


def load(s, f, c):
    return np.fromfile(os.path.join(D, s, f), dtype="<u4").reshape(-1, c)


def ror(x, r):
    x = x.astype(U32)
    return ((x >> U32(r)) | (x << U32(32 - r))).astype(U32)


def profile(x, low=True):
    out = []
    for m in range(1, 33):
        mask = ((1 << m) - 1) if low else (((1 << m) - 1) << (32 - m)) & 0xFFFFFFFF
        out.append(int(((x & U32(mask)) == 0).sum()))
    return out


for s in ("rand", "ctx"):
    inp = np.ascontiguousarray(load(s, "inputs.u32", 12))
    _, first = np.unique(inp.view(np.dtype((np.void, 48))).ravel(), return_index=True)
    keep = np.sort(first)
    R = load(s, "res.u32", 4)[keep]
    K = load(s, "keys.u32", 8)[keep]
    n = len(keep); h = n // 2
    R1, R3, R4, R6 = R[:, 0], R[:, 1], R[:, 2], R[:, 3]
    co = {"R1": R1, "R3": R3, "R4": R4, "R6": R6, "U4": R4 ^ ror(R1, 8), "U6": R6 ^ ror(R3, 8),
          "W3": R3 ^ ror(R6, 25), "W4": R4 ^ ror(R1, 7),
          "dc2^6e21be55": K[:, 1] ^ U32(EPS[0]), "dc2^91de41aa": K[:, 1] ^ U32(EPS[1]),
          "de2^6e21be55": K[:, 5] ^ U32(EPS[0]), "de2^91de41aa": K[:, 5] ^ U32(EPS[1]),
          "dg2^da2 (=R1 K-part)": K[:, 4] ^ K[:, 0]}
    print("=" * 100)
    print("[%s] rows %d; each cell = log2(fraction of rows with the m low bits zero) on T / V; uniform = -m;"
          " '.' when fewer than 8 rows" % (s, n))
    for low in (True, False):
        print("  %s bits" % ("LOW" if low else "HIGH"))
        print("  %-22s" % "m" + "".join("%11d" % m for m in (4, 8, 12, 16, 20, 24)) + "   last m with >=8 rows (T): log2 frac")
        for nm, x in co.items():
            pt = profile(x[:h], low); pv = profile(x[h:], low)
            cells = []
            for m in (4, 8, 12, 16, 20, 24):
                a, b = pt[m - 1], pv[m - 1]
                f = lambda c, N: ("%5.1f" % np.log2(c / N)) if c >= 8 else "    ."
                cells.append("%s/%s" % (f(a, h), f(b, n - h)))
            last = max([m for m in range(1, 33) if pt[m - 1] >= 8] or [0])
            tail = ("m=%d: %.2f (V %.2f)" % (last, np.log2(pt[last - 1] / h),
                                              np.log2(max(pv[last - 1], 0.5) / (n - h)))) if last else "-"
            print("  %-22s" % nm + "".join("%11s" % c for c in cells) + "   " + tail)
