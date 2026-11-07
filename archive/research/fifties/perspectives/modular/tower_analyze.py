"""Analyse the GPU 2-adic tower runs (tower_trainA.txt = train, tower_testB.txt = test, independent seeds).
P_w(k) = P(R_w == 0 mod 2^k) = P(Rm_w == 0 mod 2^k): coordinate-free (XOR and modular zero sets agree at every k).
Output: tower_analyze_out.txt.
"""
import sys
sys.dont_write_bytecode = True
import os
import math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
W = ("1", "3", "4", "6")
PAIRS = [(a, b) for a in range(4) for b in range(a + 1, 4)]


def read(fn):
    d = {}
    for line in open(os.path.join(HERE, fn)):
        p = line.split()
        if p[0] == "drawn":
            d["drawn"] = int(p[1]); d["skip"] = int(p[5])
        else:
            d[p[0]] = np.array([int(x) for x in p[1:]], dtype=np.float64)
    return d


def tail(h):  # P(tz >= k) counts, k = 0..32
    return np.cumsum(h[::-1])[::-1]


def lg(c, n):
    return -math.log2(c / n) if c > 0 else float("inf")


A, B = read("tower_trainA.txt"), read("tower_testB.txt")
for nm, d in (("train A", A), ("test B", B)):
    n = d["drawn"] - d["skip"]
    print("%s: drawn %d (2^%.2f), t==0 skipped %d, used %d" % (nm, d["drawn"], math.log2(d["drawn"]), d["skip"], n))
nA, nB = A["drawn"] - A["skip"], B["drawn"] - B["skip"]

print("\n1. per word: -log2 P(R_w == 0 mod 2^k)  [train A / test B]  (uniform = k); counts at k=32 = exact zeros of the word")
print("   k   " + "".join("        word %s        " % w for w in W))
for k in list(range(0, 33, 4)) + [30, 31]:
    if k in (30, 31) or k % 4 == 0:
        row = "  %2d  " % k
        for i in range(4):
            ta, tb = tail(A["tzw%d" % i])[k], tail(B["tzw%d" % i])[k]
            row += "  %6.2f / %6.2f (%5d)" % (lg(ta, nA), lg(tb, nB), int(min(ta, 1e5 - 1)) if k >= 24 else 0)
        print(row)
print("   full words (k=32):")
eff = []
for i in range(4):
    ca, cb = tail(A["tzw%d" % i])[32], tail(B["tzw%d" % i])[32]
    pooled = (ca + cb) / (nA + nB)
    # 95% Poisson interval on the pooled count
    c = ca + cb
    lo = max(c - 1.96 * math.sqrt(c), 0.5); hi = c + 1.96 * math.sqrt(c) + 1
    eff.append(-math.log2(pooled))
    print("   word %s: zeros train %d, test %d ; -log2 P = %.2f / %.2f ; pooled %.2f  [95%%: %.2f .. %.2f]" % (
        W[i], ca, cb, lg(ca, nA), lg(cb, nB), -math.log2(pooled), -math.log2(hi / (nA + nB)), -math.log2(lo / (nA + nB))))
print("   sum over the four words (independence model): %.2f bits" % sum(eff))

print("\n2. conditional cost per 2-adic level, word w: c_w(k) = -log2 P(tz >= k+1 | tz >= k) (uniform 1.00), pooled A+B")
for i in range(4):
    t = tail(A["tzw%d" % i]) + tail(B["tzw%d" % i])
    cs = [(-math.log2(t[k + 1] / t[k]) if t[k + 1] > 0 else float("nan")) for k in range(32)]
    print("   word %s: " % W[i] + " ".join("%.2f" % c for c in cs))

print("\n3. joint levels: all four words == 0 mod 2^k, against the product of the per-word marginals  [train A / test B]")
for k in range(0, 12):
    out = "  k=%2d (%2d bits): " % (k, 4 * k)
    for d, n in ((A, nA), (B, nB)):
        j = tail(d["min4"])[k]
        prod = np.prod([tail(d["tzw%d" % i])[k] / n for i in range(4)])
        out += "  -log2 P %6.2f vs product %6.2f (excess %+.2f, count %d)" % (lg(j, n), -math.log2(prod), -math.log2(prod) - lg(j, n), int(j))
    print(out)

print("\n4. pairs: -log2 P(both == 0 mod 2^k) minus the product of marginals (positive = pair helps)  [A / B], selected k")
for p, (a, b) in enumerate(PAIRS):
    out = "  w%s,w%s:" % (W[a], W[b])
    for k in (4, 8, 12, 14, 16, 18):
        vals = []
        for d, n in ((A, nA), (B, nB)):
            j = tail(d["pair%d" % p])[k]
            prod = tail(d["tzw%d" % a])[k] / n * tail(d["tzw%d" % b])[k] / n
            vals.append((-math.log2(prod) - lg(j, n)) if j > 0 else float("nan"))
        cnt = tail(A["pair%d" % p])[k]
        out += "  k%d %+.2f/%+.2f (n=%d)" % (k, vals[0], vals[1], int(cnt))
    print(out)

print("\n5. joint capped tz vector (cap 7): chi-square of the 4-word joint against the product of marginals, A and B")
for d, n, nm in ((A, nA, "A"), (B, nB, "B")):
    J = d["joint"].reshape(8, 8, 8, 8) / n
    marg = [J.sum(axis=tuple(x for x in range(4) if x != i)) for i in range(4)]
    prod = np.einsum("a,b,c,d->abcd", *marg)
    chi = ((J - prod) ** 2 / prod).sum() * n
    dof = 8 ** 4 - 1 - 4 * 7
    big = np.unravel_index(np.argmax(np.abs(np.log2(J / prod))), J.shape)
    print("  %s: chi2 %.3g on %d dof (z = %.1f) ; largest |log2 ratio| at tz=%s: %.3f" % (
        nm, chi, dof, (chi - dof) / math.sqrt(2 * dof), tuple(int(x) for x in big), float(np.log2(J / prod)[big])))
