"""Joint lens on the D4 partial records (data/d4/d4_partial.u32, 76 u32 per record; D0..D3 at columns 4..7).
These are formula values on partial constructions (one solved diagonal), NOT residuals of a completed construction.
Statistics: GF(2) affine rank of the 128-bit (D0..D3) rows; single-bit and cross-word bit-pair correlations,
discovery on the even records and confirmation on the odd ones; control = uniform words of the same count.
Run: python d4joint.py > d4joint_out.txt"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np
from explore0_rank import affine_basis

HERE = os.path.dirname(os.path.abspath(__file__))
rec = np.fromfile(os.path.join(HERE, "..", "data", "d4", "d4_partial.u32"), dtype="<u4").reshape(-1, 76)
D = rec[:, 4:8].copy()
n = len(D)
rng = np.random.Generator(np.random.PCG64(0x4434))
U = rng.integers(0, 2**32, size=D.shape, dtype=np.uint64).astype(np.uint32)
print("D4 partial records: %d" % n)
for lab, X in (("D0..D3", D), ("uniform control", U)):
    print("  affine rank of %s: %d" % (lab, affine_basis(X)[0]))


def bits(X):
    return ((X[:, :, None] >> np.arange(32, dtype=np.uint32)) & 1).reshape(len(X), 128).astype(np.int8)


def corr_stats(X, label):
    B = 1 - 2 * bits(X).astype(np.float64)        # +-1
    tr, te = B[0::2], B[1::2]
    s1 = tr.mean(0), te.mean(0)
    sig = 1 / np.sqrt(len(tr))
    z1 = np.abs(s1[0]) / sig
    # cross-word pairs: c_ab - c_a c_b (excess over independence of the two bits)
    ctr = (tr.T @ tr) / len(tr) - np.outer(s1[0], s1[0])
    cte = (te.T @ te) / len(te) - np.outer(s1[1], s1[1])
    iu = np.triu_indices(128, 1)
    cross = (iu[0] // 32) != (iu[1] // 32)
    a, b = iu[0][cross], iu[1][cross]
    z2 = np.abs(ctr[a, b]) / sig
    top = np.argsort(-z2)[:8]
    print("  [%s] train %d / test %d rows, sigma %.4f" % (label, len(tr), len(te), sig))
    print("    single bits: max |z| %.2f ; |z|>4: %d (expected under H0 %.3f) ; confirmed on test (same sign, |z|>2): %d" % (
        z1.max(), (z1 > 4).sum(), 128 * 6.3e-5, sum(1 for i in np.where(z1 > 4)[0] if s1[0][i] * s1[1][i] > 0 and abs(s1[1][i]) / sig > 2)))
    conf = [(a[k], b[k]) for k in np.where(z2 > 4.5)[0] if ctr[a[k], b[k]] * cte[a[k], b[k]] > 0 and abs(cte[a[k], b[k]]) / sig > 2]
    print("    cross-word bit pairs (%d): max |z| %.2f ; |z|>4.5: %d (expected %.2f) ; confirmed: %d" % (
        len(a), z2.max(), (z2 > 4.5).sum(), len(a) * 6.8e-6, len(conf)))
    for k in top[:5]:
        print("      D%d.%d + D%d.%d  excess train %+.4f test %+.4f" % (a[k] // 32, a[k] % 32, b[k] // 32, b[k] % 32, ctr[a[k], b[k]], cte[a[k], b[k]]))


corr_stats(D, "D0..D3")
corr_stats(U, "uniform control")
