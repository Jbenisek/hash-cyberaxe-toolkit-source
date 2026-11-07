'A7 side check: per frame, which of the 21 cube bits are neutral for the rule-A pass flag (exact, all 2^21 members).'
import sys, collections
sys.dont_write_bytecode = True
import numpy as np
import anf_degree as A

n = int(sys.argv[1]) if len(sys.argv) > 1 else 256
j = np.arange(1 << A.NC, dtype=np.int64)
cnt_neutral, cnt_nonempty, val2, bitfreq, pcs = collections.Counter(), 0, collections.Counter(), collections.Counter(), []
for f in range(n):
    o = A.H.ctr_outer(A.words("neutral", f, 8))
    h1, cond, word = A.lanes_c(A.key_of(o))
    p = (cond >> 8 & 1).astype(bool)
    k = int(p.sum())
    if k == 0:
        continue
    cnt_nonempty += 1
    neu = [i for i in range(A.NC) if np.array_equal(p, p[j ^ (1 << i)])]
    cnt_neutral[len(neu)] += 1
    for i in neu:
        bitfreq[i] += 1
    val2[(k & -k).bit_length() - 1] += 1
    pcs.append(k)
print("frames %d, non-empty %d" % (n, cnt_nonempty))
print("neutral cube bits per non-empty frame (count: frames):", dict(sorted(cnt_neutral.items())))
print("which cube-bit index is neutral (index: frames), c1 position = CTR_FREE[index]:",
      {i: (A.H.CTR_FREE[i], c) for i, c in sorted(bitfreq.items())})
print("2-adic valuation of the pass count (v: frames):", dict(sorted(val2.items())))
print("mean passes over non-empty %.1f, over all %.1f" % (sum(pcs) / max(1, len(pcs)), sum(pcs) / n))
