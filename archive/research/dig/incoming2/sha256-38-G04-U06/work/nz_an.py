import sys, collections, math
import numpy as np
f = sys.argv[1]
a = np.fromfile(f, dtype=np.uint32).reshape(-1, 9)
n = len(a)
d = a[:, :8]; fl = a[:, 8]
zero = (fl >> 1) & 1; cells = fl & 1
print("records", n, "cells(rows24..36)", int(cells.sum()), "zero output difference", int(zero.sum()),
      "zero but not cells", int(((zero == 1) & (cells == 0)).sum()), "cells but not zero", int(((zero == 0) & (cells == 1)).sum()))
names = ["dA36", "dA35", "dA34", "dA33", "dE36", "dE35", "dE34", "dE33"]
nzmask = (d != 0)
pat = (nzmask * (1 << np.arange(8))).sum(axis=1)
cnt = collections.Counter(pat.tolist())
print("support patterns (bit k = names[k] nonzero), top 12:")
for p, c in cnt.most_common(12):
    print("  %02x %-40s %d  (%.4f)" % (p, ",".join(names[k] for k in range(8) if (p >> k) & 1) or "none", c, c / n))
nw = nzmask.sum(axis=1)
print("number of nonzero words histogram:", dict(sorted(collections.Counter(nw.tolist()).items())))
# absorbable shape: A-words zero, E words arbitrary nonzero
absorb = (pat & 0x0f == 0) & (pat != 0)
print("shape A-words zero, some E word nonzero (the only shape rows 0..3 can absorb):", int(absorb.sum()), "of", n)
nzrows = d[(pat != 0)]
# distinct and collision statistics of full 256-bit difference
keys = [row.tobytes() for row in nzrows]
c = collections.Counter(keys)
m = len(keys)
print("nonzero-difference records", m, "distinct", len(c), "max multiplicity", max(c.values()) if c else 0)
# sampling-based collision estimate of Renyi-2 entropy
s2 = sum(v * (v - 1) for v in c.values())
if s2 > 0:
    print("pairs colliding", s2 // 2, "-> Renyi-2 support estimate 2^%.2f" % math.log2(m * (m - 1) / s2))
else:
    print("no colliding pair among", m, "-> support > 2^%.2f (birthday)" % (math.log2(m * m / 2)))
# per word entropy-ish: distinct values per word
for k in range(8):
    col = nzrows[:, k]
    cc = collections.Counter(col.tolist())
    top = cc.most_common(3)
    print("  %s: distinct %d, zero fraction %.4f, top %s" % (names[k], len(cc), cc.get(0, 0) / max(1, m), [("%08x" % v, w) for v, w in top]))
def pc(x):
    x = x.astype(np.uint64)
    x = x - ((x >> 1) & 0x5555555555555555); x = (x & 0x3333333333333333) + ((x >> 2) & 0x3333333333333333)
    x = (x + (x >> 4)) & 0x0f0f0f0f0f0f0f0f; return (x * 0x0101010101010101 >> 56) & 0xff
hw = sum(pc(nzrows[:, k]) for k in range(8)).astype(np.int64) if m else np.array([0])
print("popcount of the 256-bit difference (nonzero records): min %d, median %d, mean %.1f" % (hw.min(), np.median(hw), hw.mean()))
