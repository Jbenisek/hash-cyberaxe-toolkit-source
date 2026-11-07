"""Joint lens, step 2: the rotated ("spiral") coordinates of R and what R = 0 forces.
DERIVED (RESULT.md section 2): with dc1 = E1.c1 A^B = C = 0e09818b constant,
  U1 := R6 ^ ROR(R3,8) ^ ROR(eta,8) = K1[6] ^ ROR(K1[3],8) = ROR(C,19) ^ ROR(dc2,7) ^ ROR(dc2,8)   (E1 only)
  U3 := R4 ^ ROR(R1,8)                = K3[4] ^ ROR(K3[1],8)                                         (E3 only)
R = 0  <=>  dc2 in {X0, ~X0} (X0 ^ ROR(X0,1) = ROR(eta,1) ^ ROR(C,12)),  de2 = dc2,  U3 = 0,  da2 = dg2.
This script solves X0, checks the identities on every row and measures how often each one-sided condition holds.
Run: python explore2_split.py > explore2_split_out.txt"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from explore0_rank import load, ror, parity32

ETA = 0x830303cf
C = 0x0e09818b


def ror_i(x, r):
    return ((x >> r) | (x << (32 - r))) & 0xffffffff


tgt = ror_i(ETA, 1) ^ ror_i(C, 12)
sols = []
for x0bit in (0, 1):
    # X ^ ROR(X,1) = tgt: bit i of tgt = X_i ^ X_{i+1}; choose X_0 and propagate
    x = x0bit
    bits = [x0bit]
    for i in range(31):
        bits.append(bits[i] ^ ((tgt >> i) & 1))
    X = sum(b << i for i, b in enumerate(bits))
    if X ^ ror_i(X, 1) == tgt:
        sols.append(X)
print("target T = ROR(eta,1)^ROR(C,12) = %08x, parity %d" % (tgt, bin(tgt).count("1") & 1))
print("solutions X with X^ROR(X,1)=T:", ["%08x" % s for s in sols])
U1target = ror_i(ETA, 8)
for name in ("rand", "ctx"):
    res = load(name, "res.u32", 4)
    keys = load(name, "keys.u32", 8)
    n = len(res)
    K1, K3 = keys[:, :4], keys[:, 4:]
    dc2 = K1[:, 1]
    U1 = (ror(np.uint32(C), 19) ^ ror(dc2, 7) ^ ror(dc2, 8)).astype(np.uint32)
    U1k = K1[:, 3] ^ ror(K1[:, 1], 8)
    print("[%s] rows %d" % (name, n))
    print("  U1 formula ROR(C,19)^ROR(dc2,7)^ROR(dc2,8) = K1[6]^ROR(K1[3],8): %d of %d" % (int((U1 == U1k).sum()), n))
    for s in sols:
        print("  K1[3] = dc2 == %08x : %d rows ; K3[3] = de2 == %08x : %d rows" % (s, int((dc2 == s).sum()), s, int((K3[:, 1] == s).sum())))
    U3 = K3[:, 2] ^ ror(K3[:, 0], 8)
    u, cnt = np.unique(U3, return_counts=True)
    print("  U3 = K3[4]^ROR(K3[1],8): distinct %d ; U3 == 0 on %d rows ; top values %s" % (
        len(u), int((U3 == 0).sum()), ", ".join("%08x:%d" % (a, b) for a, b in sorted(zip(u, cnt), key=lambda z: -z[1])[:5])))
    for lab, col in (("K1[1]=da2", K1[:, 0]), ("K1[3]=dc2", K1[:, 1]), ("K3[1]=dg2", K3[:, 0]), ("K3[3]=de2", K3[:, 1]), ("U3", U3), ("U1", U1k)):
        u, cnt = np.unique(col, return_counts=True)
        pairs = (cnt.astype(np.float64) * (cnt - 1) / 2).sum()
        tot = n * (n - 1) / 2
        h2 = -np.log2(pairs / tot) if pairs > 0 else float("inf")
        print("  %-10s distinct %8d  collision pairs %12d  Renyi-2 estimate %.2f bits  max count %d (%08x)" % (
            lab, len(u), pairs, h2, cnt.max(), u[cnt.argmax()]))
