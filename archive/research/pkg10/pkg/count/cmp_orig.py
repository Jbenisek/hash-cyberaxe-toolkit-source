#!/usr/bin/env python3
"""The original calculator's per-beta parts (origall_NAME.txt, printed with one decimal) against the exact parts of
our integer run (NAME_parts.tsv).   python3 -B cmp_orig.py NAME"""
import os, sys
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__))
name = sys.argv[1]
exact = {}
for ln in open(os.path.join(HERE, name + "_parts.tsv")).read().split("\n")[1:]:
    f = ln.split("\t")
    if len(f) > 3:
        exact[f[0]] = F(f[2])
fin = unfin = same = diff = smp = 0
s_orig = 0.0; s_exact_fin = F(0); s_exact_unfin = F(0); worst = 0.0; lines = []
for ln in open(os.path.join(HERE, "origall_%s.txt" % name)).read().split("\n")[1:]:
    f = ln.split()
    if len(f) < 9:
        continue
    b, part, sampled, ex = f[0], f[2], f[4], f[8]
    e = exact.get(b, F(0))
    if ex != "0" or part == "none":
        unfin += 1; s_exact_unfin += e; lines.append("not finished %s exact part %.6f" % (b, float(e))); continue
    fin += 1; s_orig += float(part); s_exact_fin += e
    d = abs(float(part) - float(e)); worst = max(worst, d)
    if sampled not in ("0", "none"):
        smp += 1; lines.append("sampled %s original %s exact %.6f" % (b, part, float(e)))
    if d <= 0.0500001: same += 1
    else: diff += 1; lines.append("DIFFERENT %s original %s exact %.6f" % (b, part, float(e)))
out = ["%s: betas finished by the original %d (equal to the exact part at the one printed decimal %d, different %d, with a sampled outcome %d), not finished %d"
       % (name, fin, same, diff, smp, unfin),
       "sum of the original's printed parts %.1f; exact sum over the same betas %.6f; largest difference on one beta %.6f; exact part of the betas not finished %.6f"
       % (s_orig, float(s_exact_fin), worst, float(s_exact_unfin))] + lines
open(os.path.join(HERE, "origall_%s_cmp.txt" % name), "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
print("\n".join(x[:240] for x in out[:10]))
