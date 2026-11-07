"""Joint lens, step 4: check the four rotated-coordinate identities (RESULT.md section 2) on every row of rand and ctx,
and recombine the two E1 censuses (e1filter_hits.txt, e1filter_hits2.txt) with the prior E3 table weights.
  U1 = R6 ^ ROR(R3,8) ^ ROR(eta,8) = ROR(dc1,19) ^ ROR(dc2 ^ ROR(dc2,1), 7)                 (E1 only)
  Q7 = R6 ^ ROR(R3,7)              = ROR(dc1,19) ^ ROR(eta,8) ^ ROR(de2 ^ ROR(de2,1), 7)     (E3 only)
  U3 = R4 ^ ROR(R1,8)              = ROR(dg1,19) ^ ROR(dg2 ^ ROR(dg2,1), 7)                  (E3 only)
  Z7 = R4 ^ ROR(R1,7)              = ROR(da2 ^ ROR(da2,1), 7) ^ ROR(dg1,19)                  (da2 from E1, dg1 from E3)
Run: python explore4_identities.py > explore4_identities_out.txt"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
sys.dont_write_bytecode = True
import os
import math
import collections
from fractions import Fraction as F
import numpy as np
from explore0_rank import load, ror

HERE = os.path.dirname(os.path.abspath(__file__))
ETA = np.uint32(0x830303cf)
rE8 = ror(np.array([ETA]), 8)[0]
for name in ("rand", "ctx"):
    res, keys, emid = load(name, "res.u32", 4), load(name, "keys.u32", 8), load(name, "emid.u32", 16)
    R1, R3, R4, R6 = (res[:, i] for i in range(4))
    da2, dc2 = keys[:, 0], keys[:, 1]
    dg2, de2 = keys[:, 4], keys[:, 5]
    dc1 = emid[:, 2] ^ emid[:, 6]
    dg1 = emid[:, 10] ^ emid[:, 14]
    n = len(res)
    checks = {
        "U1": (R6 ^ ror(R3, 8) ^ rE8, ror(dc1, 19) ^ ror(dc2 ^ ror(dc2, 1), 7)),
        "Q7": (R6 ^ ror(R3, 7), ror(dc1, 19) ^ rE8 ^ ror(de2 ^ ror(de2, 1), 7)),
        "U3": (R4 ^ ror(R1, 8), ror(dg1, 19) ^ ror(dg2 ^ ror(dg2, 1), 7)),
        "Z7": (R4 ^ ror(R1, 7), ror(da2 ^ ror(da2, 1), 7) ^ ror(dg1, 19)),
    }
    print("[%s] %d rows: " % (name, n) + ", ".join("%s holds on %d" % (k, int((a == b).sum())) for k, (a, b) in checks.items()))

N = 2 ** 36
hits = []
for f in ("e1filter_hits.txt", "e1filter_hits2.txt"):
    hits += [l.split() for l in open(os.path.join(HERE, f)) if not l.startswith("#")]
a = collections.Counter(r[3] for r in hits)
print("E1 census, both seeds: %d hits in 2^36 -> log2 P(dc2 = 6e21be55) = %.3f (Poisson sd of log2 %.3f); dc2 values %s" % (
    len(hits), math.log2(len(hits) / N), 1 / (math.sqrt(len(hits)) * math.log(2)), dict(collections.Counter(r[4] for r in hits))))
tab = {}
for l in open(_hca_public_path_text('__HCA_WORKSPACE__/opus_cloud\\Smash-claude-math-help-g3v211\\results\\pairs_453_weights.txt')):
    t, s, w15, w13, p1 = l.split()
    if s == "6e21be55":
        tab[t] = (F(w15), F(w13))
inn = sum(a.get(t, 0) for t in tab)
j15 = sum(F(a.get(t, 0), N) * v[0] for t, v in tab.items())
j13 = sum(F(a.get(t, 0), N) * v[1] for t, v in tab.items())
print("hits whose da2 is one of the 14 table t values for s = 6e21be55: %d of %d" % (inn, len(hits)))
print("indicative pkgCG joint  sum_t P_E1(t) * W15(t, 6e21be55) = 2^%.2f   (with W13: 2^%.2f)" % (math.log2(j15), math.log2(j13)))
print("per t: " + ", ".join("%s:%d" % (t, a.get(t, 0)) for t in sorted(tab)))
