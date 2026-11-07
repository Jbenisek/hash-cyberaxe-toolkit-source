"""Joint lens: rotation ("spiral") scan and windowed mutual information between the residual words.
Data: perspectives/data/rand/res.u32 (2^20 independent rows). Train = first half, test = second half.
Controls: SHUF = the partner word permuted within its half (keeps both marginals, kills the dependence);
          UNIF = uniform random 32-bit words of the same count (numpy PCG64, fixed seed).

Part A (spiral scan): for words i, j and r = 0..31, Z = R_i op ROR(R_j, r) with op in {xor, add, sub}.
  Collision entropy H2(Z) = -log2(collision pairs / C(n,2)) from n = 2^19 rows; uniform 32-bit gives about 32
  (32 expected pairs, sd about 5.7). Deficit = 32 - H2. z = (pairs - pairs_shuf) / sqrt(pairs_shuf + 1).
Part B (windowed MI): 8-bit cyclic windows at start p in R_i and q in R_j, all 6 pairs, all p, q (6144 windows).
  Plug-in MI in bits; the same statistic on SHUF gives the bias; excess = MI_data - MI_shuf.
  Offset profile: mean excess over p for each lag d = (q - p) mod 32.
Run: python spiral_mi.py > spiral_mi_out.txt"""
import sys
sys.dont_write_bytecode = True
import os
import time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
W = ("R1", "R3", "R4", "R6")
res = np.fromfile(os.path.join(DATA, "rand", "res.u32"), dtype="<u4").reshape(-1, 4)
N = len(res)
H = N // 2
rng = np.random.Generator(np.random.PCG64(0x4A4F494E54))
halves = [res[:H], res[H:]]
perm = [rng.permutation(H) for _ in range(2)]
unif = [rng.integers(0, 2**32, size=(H, 4), dtype=np.uint64).astype(np.uint32) for _ in range(2)]
npairs_tot = H * (H - 1) / 2


def ror(x, r):
    r %= 32
    if r == 0:
        return x.copy()
    return ((x >> np.uint32(r)) | (x << np.uint32(32 - r))).astype(np.uint32)


def coll(z):
    _, c = np.unique(z, return_counts=True)
    c = c.astype(np.float64)
    return float((c * (c - 1) / 2).sum())


def h2(p):
    return -np.log2(p / npairs_tot) if p > 0 else float("inf")


t0 = time.time()
print("rows %d (train %d, test %d)" % (N, H, H))
print("\n## Part A0: single words (collision pairs; uniform expectation %.1f)" % (npairs_tot / 2**32))
for i in range(4):
    a = [coll(halves[h][:, i]) for h in range(2)]
    u = [coll(unif[h][:, i]) for h in range(2)]
    print("  %s: pairs train %6.0f test %6.0f  H2 %.2f / %.2f   | UNIF pairs %3.0f %3.0f" % (W[i], a[0], a[1], h2(a[0]), h2(a[1]), u[0], u[1]))

print("\n## Part A: spiral scan Z = R_i op ROR(R_j, r)")
OPS = {"xor": lambda a, b: a ^ b, "add": lambda a, b: (a + b).astype(np.uint32), "sub": lambda a, b: (a - b).astype(np.uint32)}
rows = []
for op, f in OPS.items():
    for i in range(4):
        for j in range(4):
            if i == j or (op in ("xor", "add") and j < i):
                continue
            for r in range(32):
                rec = [op, W[i], W[j], r]
                for h in range(2):
                    a = halves[h][:, i]
                    b = ror(halves[h][:, j], r)
                    rec.append(coll(f(a, b)))
                    rec.append(coll(f(a, b[perm[h]])))
                rows.append(rec)
# unif control: same scan shape on uniform words (one pass, xor and add only, all r) to get the null max
umax = 0.0
for op in ("xor", "add", "sub"):
    for r in range(32):
        a = unif[0][:, 0]
        b = ror(unif[0][:, 1], r)
        umax = max(umax, coll(OPS[op](a, b)))
print("  %d (op, i, j, r) combinations scanned on each half; time %.0f s" % (len(rows), time.time() - t0))
print("  UNIF control: max collision pairs over 96 (op, r) = %.0f (expectation %.1f)" % (umax, npairs_tot / 2**32))


def zsc(p, ps):
    return (p - ps) / np.sqrt(ps + 1)


rows.sort(key=lambda x: -zsc(x[4], x[5]))
print("  top 30 by train z (data vs SHUF):")
print("  op  i  j   r | train pairs  SHUF   H2     z | test pairs  SHUF   H2     z")
for rec in rows[:30]:
    op, a, b, r, p0, s0, p1, s1 = rec
    print("  %s %s %s %2d | %10.0f %6.0f %6.2f %7.1f | %10.0f %6.0f %6.2f %7.1f" % (op, a, b, r, p0, s0, h2(p0), zsc(p0, s0), p1, s1, h2(p1), zsc(p1, s1)))
nz = sum(1 for rec in rows if zsc(rec[4], rec[5]) > 6)
nzc = sum(1 for rec in rows if zsc(rec[4], rec[5]) > 6 and zsc(rec[6], rec[7]) > 3)
print("  combinations with train z > 6: %d ; confirmed on test (z > 3): %d" % (nz, nzc))
print("  SHUF-vs-SHUF null: max train z over all combos with the partner shuffled twice is not run; the UNIF line above is the null for raw pairs.")
# exclude the explained ones: (R1,R4) and (R3,R6) at r in {7,8} (xor) — any other combo with z > 6?
expl = {("R1", "R4"), ("R3", "R6"), ("R4", "R1"), ("R6", "R3")}
others = [rec for rec in rows if (rec[1], rec[2]) not in expl and zsc(rec[4], rec[5]) > 4]
print("  combos outside the pairs (R1,R4) and (R3,R6) with train z > 4: %d" % len(others))
for rec in others[:15]:
    op, a, b, r, p0, s0, p1, s1 = rec
    print("    %s %s %s %2d | train %6.0f vs %6.0f z %5.1f | test %6.0f vs %6.0f z %5.1f" % (op, a, b, r, p0, s0, zsc(p0, s0), p1, s1, zsc(p1, s1)))
print("  time %.0f s" % (time.time() - t0))

print("\n## Part B: windowed MI (8-bit windows), excess over SHUF")


def win(x, p):
    return (ror(x, p) & np.uint32(0xff)).astype(np.int64)


def ent(c):
    c = c[c > 0].astype(np.float64)
    pr = c / c.sum()
    return float(-(pr * np.log2(pr)).sum())


mi = {}
for h in range(2):
    xs = [[win(halves[h][:, i], p) for p in range(32)] for i in range(4)]
    xsS = [[x[perm[h]] for x in xs[i]] for i in range(4)]
    hx = [[ent(np.bincount(xs[i][p], minlength=256)) for p in range(32)] for i in range(4)]
    for i in range(4):
        for j in range(i + 1, 4):
            for p in range(32):
                for q in range(32):
                    jd = ent(np.bincount(xs[i][p] * 256 + xs[j][q], minlength=65536))
                    js = ent(np.bincount(xs[i][p] * 256 + xsS[j][q], minlength=65536))
                    mi[(h, i, j, p, q)] = (hx[i][p] + hx[j][q] - jd, hx[i][p] + hx[j][q] - js)
    print("  half %d done, time %.0f s" % (h, time.time() - t0))
ex = {k: v[0] - v[1] for k, v in mi.items()}
# null spread of the excess: sd of excess over windows of pairs/lags that carry no derived structure is not known
# a priori, so use the SHUF statistic's own spread: two halves give independent bias estimates
bias_sd = np.std([mi[(0, i, j, p, q)][1] - mi[(1, i, j, p, q)][1] for i in range(4) for j in range(i + 1, 4) for p in range(32) for q in range(32)]) / np.sqrt(2)
print("  sd of the SHUF MI (noise scale of one window's excess) = %.5f bits; mean SHUF MI (plug-in bias) = %.5f bits" % (
    bias_sd, np.mean([v[1] for v in mi.values()])))
print("  per pair: max excess (train) and its window, test excess there; windows with train excess > 10 sd and test > 5 sd")
for i in range(4):
    for j in range(i + 1, 4):
        ks = [(p, q) for p in range(32) for q in range(32)]
        best = max(ks, key=lambda k: ex[(0, i, j) + k])
        n10 = sum(1 for k in ks if ex[(0, i, j) + k] > 10 * bias_sd)
        n10c = sum(1 for k in ks if ex[(0, i, j) + k] > 10 * bias_sd and ex[(1, i, j) + k] > 5 * bias_sd)
        print("    %s-%s: max %.4f bits at p=%2d q=%2d (lag %2d), test %.4f ; strong windows %4d of 1024, confirmed %4d" % (
            W[i], W[j], ex[(0, i, j) + best], best[0], best[1], (best[1] - best[0]) % 32, ex[(1, i, j) + best], n10, n10c))
print("  lag profile: mean excess MI over p (train | test), lags with train mean > 5 sd/sqrt(32) listed")
for i in range(4):
    for j in range(i + 1, 4):
        prof = []
        for d in range(32):
            a = np.mean([ex[(0, i, j, p, (p + d) % 32)] for p in range(32)])
            b = np.mean([ex[(1, i, j, p, (p + d) % 32)] for p in range(32)])
            prof.append((d, a, b))
        strong = [(d, a, b) for d, a, b in prof if a > 5 * bias_sd / np.sqrt(32)]
        print("    %s-%s: %s" % (W[i], W[j], ", ".join("lag %d: %.4f|%.4f" % s for s in sorted(strong, key=lambda s: -s[1])[:8]) or "none"))
print("  time %.0f s" % (time.time() - t0))
