#!/usr/bin/env python3
# Cross-checks the C walk against Python, checks halfsearch/movers agree with outer.py on (P, X1, D),
# runs task (1) (is X1 an additive shift of K?), and summarizes ctx_out.json into context.json.

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

import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/movers'))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/impl'))
import movers as mv
import halfsearch as hs
from outer import scalar_outer, CLASS_FREE, MASK

out = json.load(open(os.path.join(HERE, "ctx_out.json")))
ref = json.load(open(os.path.join(HERE, "ref.json")))
cmp = {(r[0], r[1]): r[2:] for r in ref["ref"]}
c_bad = sum(cmp[(c[0], c[1])] != c[2:] for c in out["check"])

# halfsearch (movers, its own 2^17 member numbering) vs outer.py: same 7 words and same Y4 -> same P, X1, D?
# plus the closed forms per context: D = X11 - S11 - (ROL16(C0.d1) ^ P), and Y4 rebuilt from P (movers.invert)
from outer import Y3, CLASS_VALUE, FREE_MASK
rnd = random.Random(7); hs_bad = 0; NH = 2000; cf_bad = 0
for _ in range(NH):
    ow = [rnd.getrandbits(32) for _ in range(7)]; m = rnd.getrandbits(17)
    o = hs.ctr_outer(ow + [m]); c = mv.consts(o)
    e1 = (o["Y4"] + Y3) & MASK
    r = scalar_outer(ow + [e1 & FREE_MASK])
    hs_bad += ((e1 & ~FREE_MASK & MASK) != CLASS_VALUE) or (c["P"], c["X1"], c["D"], o["Y4"]) != (r["C0.a1"], r["X1"], r["D1.d1"], r["Y4"])
    cf_bad += r["D1.d1"] != (hs.X11 - ow[3] - (mv.rol(ow[0], 16) ^ r["C0.a1"])) & MASK
    cf_bad += mv.invert(c, ow[6], ow[3]) != (ow[0], o["Y4"])

# (1) K(g; X1) - K(g; 0): constant in g?
rnd = random.Random(11); N1 = 10000; nonconst = 0; diff_eq_X1 = 0
for _ in range(N1):
    c = {k: rnd.getrandbits(32) for k in mv.NAMES}
    X1 = c["X1"]; c0 = dict(c, X1=0)
    g1, g2 = rnd.getrandbits(32), rnd.getrandbits(32)
    d1 = (mv.K(g1, c) - mv.K(g1, c0)) & MASK; d2 = (mv.K(g2, c) - mv.K(g2, c0)) & MASK
    nonconst += d1 != d2; diff_eq_X1 += d1 == X1
# same on real constants from outer steps (consts of hs.ctr_outer), also checks K == Y1 + w12
rnd = random.Random(12); NR = 2000; nonconst_r = 0; kbad = 0
for _ in range(NR):
    e = [rnd.getrandbits(32) for _ in range(7)] + [rnd.getrandbits(19)]
    o = hs.ctr_outer(e); c = mv.consts(o); kbad += mv.K(e[1], c) != (o["Y1"] + o["w12"]) & MASK
    c0 = dict(c, X1=0); g2 = rnd.getrandbits(32)
    nonconst_r += ((mv.K(e[1], c) - mv.K(e[1], c0)) & MASK) != ((mv.K(g2, c) - mv.K(g2, c0)) & MASK)

cols = out["cols"]; per = out["per_ctx"]
stats = {k: {"min": min(r[i] for r in per), "mean": sum(r[i] for r in per) / len(per), "max": max(r[i] for r in per)}
         for i, k in enumerate(cols)}
res = {"members_per_context": 1 << 19, "contexts": len(per), "seed": ref["seed"],
       "c_vs_python_mismatches": c_bad, "c_vs_python_checked": len(out["check"]),
       "halfsearch_vs_outer_mismatches": hs_bad, "halfsearch_vs_outer_checked": NH, "closed_form_mismatches": cf_bad,
       "task1": {"random_const_cases": N1, "difference_not_constant_in_g": nonconst,
                 "difference_equal_X1": diff_eq_X1, "real_outer_cases": NR,
                 "real_difference_not_constant": nonconst_r, "K_vs_Y1+w12_mismatches": kbad},
       "distinct_counts": stats, "hist_PD_ctx0": out["hist_PD_ctx0"], "per_ctx": per, "cols": cols}
json.dump(res, open(os.path.join(HERE, "context.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in res.items() if k != "per_ctx"}, indent=1))
