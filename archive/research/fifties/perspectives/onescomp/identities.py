"""Numerical check of the ones'-complement identities used in RESULT.md (2^22 random words). Writes identities_out.txt."""
import sys
sys.dont_write_bytecode = True
import numpy as np
M = 0xFFFFFFFF
rng = np.random.default_rng(7)
n = 1 << 22
x = rng.integers(0, 2 ** 32, n, dtype=np.uint64)
y = rng.integers(0, 2 ** 32, n, dtype=np.uint64)
oc = lambda v: np.where(v == M, 0, v) % M
lines = []
for r in (16, 12, 8, 7):
    rotr = ((x >> np.uint64(r)) | (x << np.uint64(32 - r))) & np.uint64(M)
    lines.append("ROR(x,%d) == 2^(32-%d) x mod M : %s" % (r, r, bool(np.array_equal(oc(rotr), (oc(x) * pow(2, 32 - r, M)) % M))))
s = (x + y) & np.uint64(M)
c = (x + y) >> np.uint64(32)
lines.append("x+y mod 2^32 == x + y - carry mod M : %s ; carry=1 fraction %.4f" % (
    bool(np.array_equal(oc(s), (oc(x) + oc(y) + M - c) % M)), float(c.mean())))
lines.append("x^y == x + y - 2(x&y) mod M : %s" % bool(np.array_equal(oc(x ^ y), (oc(x) + oc(y) + 2 * M - 2 * oc(x & y)) % M)))
p4 = np.array([k * 0x11111111 for k in range(16)], dtype=np.uint64)
rot4 = lambda v: ((v >> np.uint64(4)) | (v << np.uint64(28))) & np.uint64(M)
lines.append("period-4 words = {k*0x11111111}: rotation-invariant by 4: %s; in Z/M they are the multiples of M/15 (k=15 is 0xFFFFFFFF = 0)"
             % bool(np.array_equal(rot4(p4), p4)))
lines.append("ROR by 16,12,8 is the identity mod 15 (so mod 3 and mod 5): %s; ROR 7 = x2 mod 15 (ROL 7 = x8): %s" % (
    all(pow(2, 32 - r, 15) == 1 for r in (16, 12, 8)), pow(2, 32 - 7, 15) == 2))
lines.append("order of 2 mod p: %s" % {p: next(k for k in range(1, 40) if pow(2, k, p) == 1) for p in (3, 5, 17, 257, 65537)})
lines.append("dA == dB mod M  <=>  dA == dB or {dA,dB} = {0, 0xFFFFFFFF}  (only 0 and 0xFFFFFFFF share a residue)")
open(__file__.replace(".py", "_out.txt"), "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
