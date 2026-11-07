"""Exact rotational-XOR identities of the residual, checked on every row of rand/ and ctx/.

Notation (XOR differences A^B): K1 = (da2, dc2, dd2, db2), K3 = (dg2, de2, df2, dh2) on digest words (1,3,4,6);
R = K1 ^ K3.  From the G steps (DERIVED): dd2 = ROR(da2,8) (d1 common), db2 = ROR(db1 ^ dc2, 7),
dh2 = ROR(eta ^ de2, 8) (dh1 = eta), df2 = ROR(df1 ^ dg2, 7); db1 = 18b0e098 and eta = 830303cf are constants here.
Rotational coordinates of R:
  U6 = R6 ^ ROR(R3,8) = ROR(db1,7) ^ ROR(eta,8) ^ ROR(dc2,7) ^ ROR(dc2,8)      (E1 only)
  W3 = R3 ^ ROL(R6,7) = db1 ^ ROR(eta,1) ^ de2 ^ ROR(de2,1)                     (E3 only)
  U4 = R4 ^ ROR(R1,8) = ROR(df1 ^ dg2 ^ ROR(dg2,1), 7)                          (E3 only)
  W4 = R4 ^ ROR(R1,7) = ROR(da2,8) ^ ROR(da2,7) ^ ROR(df1,7)                    (da2 from E1, df1 from E3)
Consequences: parity(R3) = parity(R6) on every row (parity(U6) = parity(db1) ^ parity(eta) = 0), so R lies in a
127-dimensional subspace; U6 = 0 <=> dc2 in {eps, ~eps}; W3 = 0 <=> de2 in {eps, ~eps}; W4 = 0 <=> df1 = da2 ^ ROR(da2,1).
"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np

D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
U32 = np.uint32
M = 0xFFFFFFFF
DB1, ETA = 0x18B0E098, 0x830303CF


def load(s, f, c):
    return np.fromfile(os.path.join(D, s, f), dtype="<u4").reshape(-1, c)


def ror(x, r):
    x = x.astype(U32)
    return ((x >> U32(r)) | (x << U32(32 - r))).astype(U32)


def rol(x, r):
    return ror(x, 32 - r)


def iror(x, r):
    return ((x >> r) | (x << (32 - r))) & M


def par(x):
    x = x.astype(U32).copy()
    for s in (16, 8, 4, 2, 1):
        x ^= x >> U32(s)
    return x & U32(1)


def h2(x):
    _, c = np.unique(x, return_counts=True)
    n = len(x)
    p = float((c.astype(np.float64) * (c - 1) / 2).sum())
    return p, (-np.log2(p / (n * (n - 1) / 2)) if p else float("inf"))


def solve_sigma(s):
    """all x with x ^ ROR(x,1) = s (bit i of s = x_i ^ x_{i+1}); empty if parity(s) = 1."""
    if bin(s).count("1") & 1:
        return []
    bits = [0] * 32
    for i in range(31):
        bits[i + 1] = bits[i] ^ ((s >> i) & 1)
    x = sum(b << i for i, b in enumerate(bits))
    return [x, x ^ M]


def d4(x):
    return sum(min(c, 8 - c) for c in (bin(x & (0x11111111 << b)).count("1") for b in range(4)))


sigma0 = DB1 ^ iror(ETA, 1)
EPS = solve_sigma(sigma0)
print("sigma0 = db1 ^ ROR(eta,1) = %08x; solutions of x ^ ROR(x,1) = sigma0: %s" % (sigma0, ["%08x" % e for e in EPS]))
print("constant differences and their distance d4 to the nearest period-4 word (uniform word: mean 11.6):")
for nm, v in (("db1", DB1), ("dc1", 0x0E09818B), ("de1", 0x03CF8303), ("eta=dh1", ETA), ("Y3^Y3'", 0x8127C181 ^ 0x7EDF3E7E),
              ("Y11^Y11'", 0x7AF77F38 ^ 0x850000C3), ("eps", EPS[0]), ("~eps", EPS[1])):
    print("   %-9s %08x  HW %2d  d4 %d" % (nm, v, bin(v).count("1"), d4(v)))

for s in ("rand", "ctx"):
    inp = np.ascontiguousarray(load(s, "inputs.u32", 12))
    _, first = np.unique(inp.view(np.dtype((np.void, 48))).ravel(), return_index=True)
    keep = np.sort(first)
    R = load(s, "res.u32", 4)[keep]
    K = load(s, "keys.u32", 8)[keep]
    em = load(s, "emid.u32", 16)[keep]
    n = len(keep)
    da2, dc2, dd2, db2 = K[:, 0], K[:, 1], K[:, 2], K[:, 3]
    dg2, de2, df2, dh2 = K[:, 4], K[:, 5], K[:, 6], K[:, 7]
    db1 = em[:, 1] ^ em[:, 5]
    dh1 = em[:, 11] ^ em[:, 15]
    df1 = em[:, 9] ^ em[:, 13]
    R1, R3, R4, R6 = R[:, 0], R[:, 1], R[:, 2], R[:, 3]
    U6 = R6 ^ ror(R3, 8); W3 = R3 ^ rol(R6, 7); U4 = R4 ^ ror(R1, 8); W4 = R4 ^ ror(R1, 7)
    checks = {
        "db1 == 18b0e098": db1 == U32(DB1),
        "dh1 == eta": dh1 == U32(ETA),
        "dd2 == ROR(da2,8)": dd2 == ror(da2, 8),
        "db2 == ROR(db1^dc2,7)": db2 == ror(db1 ^ dc2, 7),
        "dh2 == ROR(eta^de2,8)": dh2 == ror(U32(ETA) ^ de2, 8),
        "df2 == ROR(df1^dg2,7)": df2 == ror(df1 ^ dg2, 7),
        "U6 == ROR(db1,7)^ROR(eta,8)^ROR(dc2,7)^ROR(dc2,8)": U6 == (U32(iror(DB1, 7) ^ iror(ETA, 8)) ^ ror(dc2, 7) ^ ror(dc2, 8)),
        "W3 == db1^ROR(eta,1)^de2^ROR(de2,1)": W3 == (U32(sigma0) ^ de2 ^ ror(de2, 1)),
        "U4 == ROR(df1^dg2^ROR(dg2,1),7)": U4 == ror(df1 ^ dg2 ^ ror(dg2, 1), 7),
        "W4 == ROR(da2,8)^ROR(da2,7)^ROR(df1,7)": W4 == (ror(da2, 8) ^ ror(da2, 7) ^ ror(df1, 7)),
        "parity(R3) == parity(R6)": par(R3) == par(R6),
        "parity(U6) == 0": par(U6) == 0,
    }
    print("\n[%s] %d rows (repeated input rows dropped)" % (s, n))
    for k, v in checks.items():
        print("   %-55s failures %d" % (k, int((~v).sum())))
    print("   parity(df1) = 0 fraction %.4f   parity(R1)==parity(R4) fraction %.4f" % (
        float((par(df1) == 0).mean()), float((par(R1) == par(R4)).mean())))
    print("   hits: dc2 in {eps,~eps} %d   de2 in {eps,~eps} %d   W4 == 0 %d   U4 == 0 %d   R1 == 0 %d" % (
        int(np.isin(dc2, np.array(EPS, dtype=U32)).sum()), int(np.isin(de2, np.array(EPS, dtype=U32)).sum()),
        int((W4 == 0).sum()), int((U4 == 0).sum()), int((R1 == 0).sum())))
    print("   per-word Renyi-2 entropy from collision pairs (uniform 32-bit word: %.1f pairs expected):" % (
        n * (n - 1) / 2 / 2**32))
    for nm, x in (("R1", R1), ("R3", R3), ("R4", R4), ("R6", R6), ("U4", U4), ("U6", U6), ("W3", W3), ("W4", W4),
                  ("da2", da2), ("dc2", dc2), ("de2", de2), ("df1", df1), ("dg2", dg2)):
        p, h = h2(x)
        print("      %-4s pairs %10.0f  H2 %6.2f" % (nm, p, h))
