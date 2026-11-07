"""Joint lens: K1-K3 coupling INSIDE a (context, member) group (ctx set: 16 contexts x 16 members x 1024 cube points).
For every residual bit b (R_b = K1_b ^ K3_b) and every group g: Cov_g = within-group covariance of (+-1) K1_b and K3_b.
Two questions, both with the group (not the row) as the unit, train = contexts 0-7, test = contexts 8-15:
  (1) AVERAGE coupling: mean over groups of Cov_g, t = mean / (group SD / sqrt(groups)).
  (2) PER-GROUP coupling: SD over groups of Cov_g against its null SD, the same statistic after re-pairing K3 with
      another row of the same group (control). Ratio >> 1 means K1_b and K3_b move together inside a group.
(An earlier version of this script used row-level sigma; rows inside one group are not independent, so that z was
overstated. coupling_ctx_se_out.txt shows the correction for the two bits it had flagged.)
Run: python coupling_ctx.py > coupling_ctx_out.txt"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from explore0_rank import load

keys = load("ctx", "keys.u32", 8)
n = len(keys)
rng = np.random.Generator(np.random.PCG64(0x435458))
perm = (np.stack([rng.permutation(1024) for _ in range(256)]) + (np.arange(256) * 1024)[:, None]).ravel()


def pm(X):
    b = ((X[:, :, None] >> np.arange(32, dtype=np.uint32)) & 1).reshape(len(X), 128)
    return (1 - 2 * b.astype(np.float32)).reshape(256, 1024, 128)


A = pm(keys[:, :4])
C = pm(keys[:, 4:])
Cn = pm(keys[perm, 4:])


def gcov(a, c):
    return (a * c).mean(1) - a.mean(1) * c.mean(1)        # (256 groups, 128 bits)


cov = gcov(A, C)
cov0 = gcov(A, Cn)
print("ctx set: 256 groups x 1024 rows; unit = group; train = groups of contexts 0-7 (128), test = contexts 8-15 (128)")
res = []
for b in range(128):
    row = [b]
    for sl in (slice(0, 128), slice(128, 256)):
        x, x0 = cov[sl, b], cov0[sl, b]
        t = x.mean() / (x.std(ddof=1) / np.sqrt(len(x)) + 1e-12)
        ratio = x.std(ddof=1) / (x0.std(ddof=1) + 1e-12)
        row += [x.mean(), t, x.std(ddof=1), x0.std(ddof=1), ratio]
    res.append(row)
res = np.array(res)
print("(1) average coupling: max |t| train %.2f ; bits with |t|>4 on train: %d ; confirmed (same sign, |t|>2 on test): %d" % (
    np.abs(res[:, 2]).max(), int((np.abs(res[:, 2]) > 4).sum()),
    int(((np.abs(res[:, 2]) > 4) & (np.sign(res[:, 2]) == np.sign(res[:, 7])) & (np.abs(res[:, 7]) > 2)).sum())))
print("(2) per-group coupling: SD ratio (data / re-paired control) per bit; bits with ratio > 2 on train: %d, confirmed on test (> 2): %d" % (
    int((res[:, 5] > 2).sum()), int(((res[:, 5] > 2) & (res[:, 10] > 2)).sum())))
print("    control spread: re-paired SD ranges %.4f .. %.4f (binomial noise of a 1024-row covariance)" % (res[:, 4].min(), res[:, 4].max()))
order = np.argsort(-res[:, 5])
print("    top bits by train ratio:  bit   ratio_train ratio_test   SD_train  SD_null   mean_train  t_train  mean_test t_test")
for b in order[:16]:
    r = res[b]
    print("      R%s.%-2d  %7.2f   %7.2f   %.4f  %.4f   %+.4f  %+5.1f   %+.4f %+5.1f" % ("1346"[int(r[0]) // 32], int(r[0]) % 32, r[5], r[10], r[3], r[4], r[1], r[2], r[6], r[7]))
per_word = [(w, int(((res[w * 32:(w + 1) * 32, 5] > 2) & (res[w * 32:(w + 1) * 32, 10] > 2)).sum())) for w in range(4)]
print("    confirmed per-group-coupled bits per residual word: " + ", ".join("R%s %d/32" % ("1346"[w], c) for w, c in per_word))
