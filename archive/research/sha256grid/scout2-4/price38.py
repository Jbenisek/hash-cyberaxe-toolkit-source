# price38.py - scout2-4: summarize the SMC campaign logs (campA.log, campB.log) and price the measured q3 gain
# factors on the r38 ledger.  The ledger function and its integer components are copied verbatim from
# research/sha256grid/map-r38/levers_r38.py (c99df2dc ledger, 0ae69bcb allowances); the base row and the q3 x1.3 / x2
# / x4 rows of map-lit/leader_cost_split.txt are reproduced first as a check.
# usage: python -B price38.py
import glob, math, os, re
from decimal import Decimal, getcontext, ROUND_CEILING
from fractions import Fraction
getcontext().prec = 60
LN2 = Decimal(2).ln()
C = 2728
PRE = 466_412_701_031_896_270_852_028
INIT = 1024
ONLINE = 11_938_977_653_196_641_712_347_327
NG = 398_563_284_869_814_990_705
FIN_OPS = 1024
FIN_C = 6
SPLIT = {"block": Fraction(30), "entries": Fraction(5669, 100), "w7": Fraction(2541, 100),
         "deep": Fraction(461, 100), "pro": Fraction(31, 100)}
PER_BLOCK = sum(SPLIT.values())
def log2(n):
    if isinstance(n, Fraction):
        return (Decimal(n.numerator).ln() - Decimal(n.denominator).ln()) / LN2
    return Decimal(n).ln() / LN2
def ceil5(x):
    s = Decimal(10) ** 5
    return (x * s).to_integral_value(rounding=ROUND_CEILING) / s
def total(ac, a_s, dev, ng_scale=Fraction(1), online_scale=Fraction(1), fb_ops=C):
    ng = NG * ng_scale
    online = Fraction(ONLINE) * ng_scale * online_scale
    return C * (ac + a_s + dev + FIN_C) + PRE + INIT + FIN_OPS + ng * fb_ops + online
def score(**kw):
    return log2(Fraction(total(**kw))) - log2(C)
def engine(**chg):
    s = dict(SPLIT); s.update({k: Fraction(v) for k, v in chg.items()})
    return sum(s.values()) / PER_BLOCK
A70, A64 = 1 << 70, 1 << 64
base = score(ac=A70, a_s=A70, dev=A64)
print("leader rebuilt (levers_r38 base): %.6f  (proof.md: 72.633442)" % base)
for g, ref in ((Fraction(13, 10), "72.398"), (Fraction(2), "72.064"), (Fraction(4), "71.665")):
    print("q3 x%s: %.4f  (leader_cost_split: %s)" % (float(g), score(ac=A70, a_s=A70, dev=A64, ng_scale=1 / g), ref))

# ---- campaign summary ----
here = os.path.dirname(os.path.abspath(__file__))
pat = re.compile(r"cut (\d+) seed (\d+) NP (\d+): log2 q3 = (-?[\d.]+)  stages: ([-\d. ]+?)  tail hits (\d+) \(uniform-outside (\d+)\) cellpath (\d+) weightfrac ([\d.]+) bad (\d+)")
runs = {}
fixed = {}
for fn in sorted(glob.glob(os.path.join(here, "camp*.log"))):
    for line in open(fn):
        m = pat.search(line)
        if m and line.startswith("fixvar"):      # campaign D: one fixed variant per run (dispersion check)
            fixed.setdefault((int(m.group(1)), int(line.split()[1])), []).append(float(m.group(4))); continue
        if m and (int(m.group(3)) != 4000 or line.startswith("mask17")):
            # campaign C heavy-tail check (NP 8000, larger streams) -> 1016; campaign E (filed first test kept) -> 2016
            key = (2000 if line.startswith("mask17") else 1000) + int(m.group(1))
            runs.setdefault(key, []).append(dict(seed=int(m.group(2)), l=float(m.group(4)),
                stages=[float(x) for x in m.group(5).split()], hits=int(m.group(6)), out=int(m.group(7)), wf=float(m.group(9)), bad=int(m.group(10))))
            continue
        if m:
            cut = int(m.group(1)); runs.setdefault(cut, []).append(dict(seed=int(m.group(2)), l=float(m.group(4)),
                stages=[float(x) for x in m.group(5).split()], hits=int(m.group(6)), out=int(m.group(7)), wf=float(m.group(9)), bad=int(m.group(10))))
T99 = {1: 31.821, 2: 6.965, 3: 4.541, 4: 3.747, 5: 3.365, 6: 3.143, 7: 2.998, 8: 2.896, 9: 2.821, 10: 2.764, 11: 2.718,
       12: 2.681, 13: 2.650, 14: 2.624, 15: 2.602, 19: 2.539, 23: 2.500, 31: 2.453, 63: 2.387}
def t99(df): return T99.get(df, T99[max(k for k in T99 if k <= df)])
stats = {}
print("\ncut  runs  mean log2 q3  rel.sd   99%% lower  99%% upper  bad  mean cell-path weight fraction   stage means")
for cut in sorted(runs, reverse=True):
    rs = runs[cut]; z = [2.0 ** r["l"] for r in rs]; n = len(z); mz = sum(z) / n
    sd = math.sqrt(sum((x - mz) ** 2 for x in z) / (n - 1)) if n > 1 else float("nan")
    lo = mz - t99(n - 1) * sd / math.sqrt(n) if n > 1 else float("nan"); hi = mz + t99(n - 1) * sd / math.sqrt(n) if n > 1 else float("nan")
    st = [sum(r["stages"][k] for r in rs) / n for k in range(len(rs[0]["stages"]))]
    stats[cut] = dict(n=n, mean=mz, lo=lo, hi=hi)
    print("%3d  %4d  %10.4f   %6.4f  %9.4f  %9.4f  %3d  %.4f   %s" % (cut, n, math.log2(mz), sd / mz, math.log2(lo) if lo > 0 else float("nan"),
          math.log2(hi), sum(r["bad"] for r in rs), sum(r["wf"] for r in rs) / n, " ".join("%.3f" % x for x in st)))
print("(cut 1016 = cut 16 with NP 8000 and 2-4x larger proposal streams; cut 2016 = filed first row-17 test kept, i.e. the\n E17^x 10-bit mask, then relaxed rows and the collision test: the event of a program that changes only its deep path)")
if fixed:
    print("\nfixed-variant runs (campaign D): cut, variant index -> log2 q3")
    for (cut, v), ls in sorted(fixed.items()):
        print("  cut %d  variant %3d  %s" % (cut, v, " ".join("%.4f" % x for x in ls)))
    for v in sorted({v for (_, v) in fixed}):
        if (16, v) in fixed and (37, v) in fixed:
            print("  variant %3d: relaxed/cell ratio %.2f" % (v, 2 ** (fixed[(16, v)][0] - fixed[(37, v)][0])))
if 37 in stats:
    c = stats[37]
    print("\ngain factors against the cell replica (cut 37; filed R1 mean 2^-101.0001, bound 2^-101.0101):")
    print("cut  point g   log2 g   conservative g (99%% lower of cut / 99%% upper of cut 37)")
    for cut in sorted(stats, reverse=True):
        if cut == 37: continue
        s = stats[cut]; g = s["mean"] / c["mean"]; gc = s["lo"] / c["hi"] if s["lo"] > 0 else float("nan")
        stats[cut]["g"] = g; stats[cut]["gc"] = gc
        print("%3d  %7.3f  %6.3f   %7.3f" % (cut, g, math.log2(g), gc))
# ---- pricing ----
print("\nr38 pricing (allowances A_C = A_S = 2^70, DEV 2^64 as filed; base %.5f; organizer units, log2 of C-unit total)" % base)
rows = []
def row(label, **kw):
    s = score(**kw); rows.append((label, s)); print("  %-86s %.5f  ceil5 %s  delta %+.4f" % (label, s, ceil5(s), s - base))
for g in (Fraction(118, 100), Fraction(13, 10), Fraction(2), Fraction(4)):
    row("q3 x%s (brief's reference factor)" % float(g), ac=A70, a_s=A70, dev=A64, ng_scale=1 / g)
labels = {22: "tail rows 23..37 relaxed (deep path tests collision after row 22; no other change)",
          18: "rows 19..37 relaxed (deep path only, its ops x2 GUESS; first row-17 test unchanged)",
          17: "rows 18..37 relaxed (deep path only, its ops x2 GUESS; first row-17 test unchanged)",
          16: "rows 17..37 relaxed (first row-17 test relaxed: +10 ops per W7 pass, GUESS)",
          15: "row 16 relaxed too (G' = 80 words; table entries x2.5, GUESS cost)",
          2016: "filed first row-17 test kept, deep path tests collision (deep ops x2 GUESS)"}
for cut in (22, 18, 17, 2016, 16, 15):
    if cut not in stats or "g" not in stats[cut]: continue
    for kind in ("g", "gc"):
        g = Fraction(stats[cut][kind]).limit_denominator(10 ** 9)
        if g <= 0: continue
        osc = Fraction(1)
        if cut in (18, 17, 2016): osc = engine(deep=SPLIT["deep"] * 2)       # deep path runs longer on relaxed rows (GUESS x2)
        if cut == 16: osc = engine(w7=SPLIT["w7"] * Fraction(76, 66))
        if cut == 15: osc = engine(w7=SPLIT["w7"] * Fraction(76, 66) * Fraction(80, 32), entries=SPLIT["entries"] * Fraction(80, 32))
        row("cut %d %s: %s g=%.3f" % (cut, "point" if kind == "g" else "99%-cons", labels[cut], float(g)), ac=A70, a_s=A70, dev=A64, ng_scale=1 / g, online_scale=osc)
# allowance-independent view: the attack proper
att = score(ac=0, a_s=0, dev=0)
print("\nattack proper (no allowances) filed: %.5f" % att)
for cut in (22, 17, 16):
    if cut in stats and "g" in stats[cut]:
        g = Fraction(stats[cut]["g"]).limit_denominator(10 ** 9)
        osc = engine(w7=SPLIT["w7"] * Fraction(76, 66)) if cut == 16 else engine(deep=SPLIT["deep"] * 2) if cut == 17 else Fraction(1)
        print("attack proper, cut %d point g=%.3f: %.5f" % (cut, float(g), score(ac=0, a_s=0, dev=0, ng_scale=1 / g, online_scale=osc)))
        print("  same with the r37 allowance convention A_C 2^60, A_S 2^50, DEV 2^40: %.5f" % score(ac=1 << 60, a_s=1 << 50, dev=1 << 40, ng_scale=1 / g, online_scale=osc))
