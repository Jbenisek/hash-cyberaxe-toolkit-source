#!/usr/bin/env python3
# lens EVERY FIGURE: the ApproxMC paragraph (30 outcomes, share 0.8866, mean, largest difference), from the follow-up's file and OUTX

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

import re, math
from fractions import Fraction
B = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg5/evidence')
outx = {}
for m in re.finditer(r"^OUTX e7c1815f ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) E1 (\d+) N3 (\d+)$", open(B + "/pairs_recount_e7c1815f.txt").read(), re.M):
    outx[(m.group(1), m.group(2), m.group(3))] = (int(m.group(4)), int(m.group(5)))
old = {l.split()[0] for l in open(B + "/snapshot/pinB_e7c1815f.total").read().split("\n") if l.split()}
short = {k: Fraction(e * n, 2 ** 80) for k, (e, n) in outx.items() if k[0] in old}
tot = sum(short.values())
amc = re.findall(r"^AMC ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) exact log2 ([\d.]+) approxmc ([\d.]+)", open(B + "/followup/pinB3_sat.txt").read(), re.M)
keys = [(b, t, e) for t, e, b, _, _ in amc]
top30 = sorted(short, key=lambda k: -short[k])[:30]
diffs = [float(x) - float(a) for _, _, _, x, a in amc]
exact_ok = all(abs(math.log2(outx[k][1]) - float(x)) < 0.006 for k, (_, _, _, x, _) in zip(keys, amc))
print("AMC lines %d; all in the short list %s; same set as the 30 largest exact products %s; share of the short-list sum %.5f (text 0.8866); "
      "'exact log2' equals log2 N3 of OUTX %s; mean of printed differences %+.4f (text -0.002), largest %.2f (text 0.10); short-list sum %.1f; 30th and 31st products %.0f %.0f" % (
          len(amc), all(k in short for k in keys), set(keys) == set(top30), float(sum(short[k] for k in keys) / tot), exact_ok,
          sum(diffs) / len(diffs), max(abs(d) for d in diffs), float(tot), float(short[top30[-1]]), float(sorted(short.values(), reverse=True)[30])))
