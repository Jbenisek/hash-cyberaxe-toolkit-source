#!/usr/bin/env python3
# lens EVERY FIGURE: the tables of proof.md against the files (39 betas, 16 outcomes, dropped parts), and pkg4's tables

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
B = _hca_public_path_text('__HCA_WORKSPACE__/research')
out = open(B + "/pkg5/review/fig_tables.out", "w")
def say(*a): print(*a, file=out)
proof = open(B + "/pkg5/blake3-r2/proof.md").read()
p4 = open(B + "/pkg4/blake3-r2/proof.md").read()
EV = B + "/pkg5/evidence"
tot = {}
for l in open(EV + "/pinB_e7c1815f.total").read().split("\n"):
    t = l.split()
    if len(t) == 4:
        tot[t[0]] = (int(t[1]), float(t[3]))
outx = {}
for m in re.finditer(r"^OUTX e7c1815f ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) E1 (\d+) N3 (\d+)$", open(EV + "/pairs_recount_e7c1815f.txt").read(), re.M):
    outx[(m.group(1), m.group(2), m.group(3))] = (int(m.group(4)), int(m.group(5)))
num = lambda s: float(s.replace(",", ""))
rows = re.findall(r"^\| ([0-9a-f]{8}) \| (\d+) \| (\d+) \| ([\d,]+) \|(.*)\|$", proof, re.M)
bad = 0
seen = []
for beta, k, no, part, rest in rows:
    if beta not in tot or rest.count("|") != 2:
        continue
    seen.append(beta)
    mine = (tot[beta][0], sum(1 for q in outx if q[0] == beta), int(round(tot[beta][1])))
    if mine != (int(k), int(no), int(num(part))):
        bad += 1; say("ROW DIFF", beta, (k, no, part), mine)
say("first table: rows %d, rows that differ %d, sum of the Outcomes column %d, sum of printed parts %d, order by part descending %s" % (
    len(seen), bad, sum(int(r[2]) for r in rows if r[0] in seen), sum(int(num(r[3])) for r in rows if r[0] in seen),
    [tot[b][1] for b in seen] == sorted([tot[b][1] for b in seen], reverse=True)))
# 16 outcomes of the heaviest beta
def odd(s):
    s = s.strip()
    m = re.match(r"(?:(\d+) \* )?2\^(\d+)$", s)
    return int(m.group(1) or 1) * 2 ** int(m.group(2))
orow = re.findall(r"^\| ([0-9a-f]{8}) \| ([0-9a-f]{8}) \| ([^|]+) \| ([^|]+) \| ([\d,]+) \|$", proof, re.M)
bad2 = 0; s2 = 0
for tau, eps, n1, n3, adds in orow:
    key = ("481c6852", tau, eps)
    e, n = outx[key]
    if abs(odd(n1) / e - 1) > 1e-12 or odd(n3) != n or abs(odd(n1) * odd(n3) / 2 ** 80 - num(adds)) > 0.5:
        bad2 += 1; say("OUTCOME DIFF", tau, eps, n1, n3, adds, e, n)
    s2 += num(adds)
say("outcome table: rows %d, differ %d, sum %d (text 14,038,016); sum of N1 * 2^-47 over the 16 = %.2f (2^39 draws of d1 with this beta, b1, a2: predicted hits; text 628.75)" % (
    len(orow), bad2, s2, sum(outx[("481c6852", t, e)][0] for t, e, *_ in orow) / 2.0 ** 86 * 2 ** 39))
# tables shared with pkg4 must be the same lines
def tab(text): return [l for l in text.split("\n") if l.startswith("|")]
a, b = tab(p4), tab(proof)
say("table lines: pkg4 %d, pkg5 %d; pkg4 table lines missing in pkg5: %d" % (len(a), len(b), sum(1 for l in a if l not in b)))
for l in a:
    if l not in b:
        say("   pkg4 only:", l[:110])
out.close()
print("written")
