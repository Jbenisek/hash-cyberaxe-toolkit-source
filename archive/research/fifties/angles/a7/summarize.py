'A7: summarise anf_result.json (degree histograms, low-degree bits with their variable counts, pass-flag support).'
import json, os, collections
HERE = os.path.dirname(os.path.abspath(__file__))
R = json.load(open(os.path.join(HERE, "anf_result.json")))


def summ(name, rows, bits=None):
    h, low, gap = collections.Counter(), collections.Counter(), collections.Counter()
    useful2 = useful3 = n = 0
    for fr in rows:
        for b, (d, nv, nm, mask) in enumerate(fr):
            if bits is not None and b not in bits:
                continue
            n += 1
            h[d] += 1
            if 1 <= d <= 3:
                low[(d, nv)] += 1
            if d >= 1:
                gap[nv - d] += 1
            useful2 += 1 <= d <= 2 and nv >= 10
            useful3 += 1 <= d <= 3 and nv >= 10
    print("%-22s n=%4d deg hist %s" % (name, n, dict(sorted(h.items()))))
    print("%-22s low (deg,nvars):count %s | deg<=2 & nvars>=10: %d | deg<=3 & nvars>=10: %d | nvars-deg hist %s" % (
        "", dict(sorted(low.items())), useful2, useful3, dict(sorted(gap.items()))))


C, Y = R["C"], R["Y"]
summ("C h1 (32 bits)", [f["h1"] for f in C])
summ("C rule-A parities (8)", [f["cond"][:8] for f in C])
summ("C rule-A pass flag", [f["cond"][8:9] for f in C])
summ("C E1 word (32 bits)", [f["word"] for f in C])
summ("C E1 word low 8", [f["word"] for f in C], bits=range(8))
summ("Y omega (32 bits)", [f["omega"] for f in Y])
summ("Y omega low 9", [f["omega"] for f in Y], bits=range(9))
summ("Y Y9 (32 bits)", [f["Y9"] for f in Y])
print("pass flag per frame (passes, deg, support size, support mask over cube-bit index):")
for i, f in enumerate(C):
    d, nv, nm, mask = f["cond"][8]
    print("  frame %2d passes %7d deg %2d support %2d mask %06x monomials %d" % (i, f["passes"], d, nv, mask, nm))
print("rule-A parity supports per frame (nvars of the 8 conditions):")
for i, f in enumerate(C):
    print("  frame %2d %s  union %06x" % (i, [p[1] for p in f["cond"][:8]],
                                         __import__("functools").reduce(lambda a, b: a | b, [p[3] for p in f["cond"][:8]])))
