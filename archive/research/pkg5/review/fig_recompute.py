#!/usr/bin/env python3
# lens EVERY FIGURE: independent recomputation of the new and changed figures of pkg5.
# Reads files only. Uses nothing of tools/pkg5_data.py. Output: review/fig_recompute.out

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

import json, math, re, sys, os, random
from fractions import Fraction

B = _hca_public_path_text('__HCA_WORKSPACE__/research')
P5 = B + "/pkg5"
EV = P5 + "/evidence"
OUT = open(P5 + "/review/fig_recompute.out", "w")
bad = []


def say(*a):
    print(*a, file=OUT)


def chk(name, got, want):
    ok = (got == want)
    say(("ok   " if ok else "DIFF ") + name + ": " + str(got) + ("" if ok else "   TEXT HAS: " + str(want)))
    if not ok:
        bad.append(name)


M = 0xFFFFFFFF
ror = lambda v, n: ((v >> n) | (v << (32 - n))) & M
rol = lambda v, n: ror(v, 32 - n)
wt = lambda x: bin(x).count("1")
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)


def G(A, Bq, C, D, x, y):
    a1 = (A + Bq + x) & M; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M; b1 = ror(Bq ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)


X3, X7, X11, X15, W4, W13 = 0xD5D881CA, 0xAA277E35, 0x1F208000, 0x123F2142, 0x7FFFFFFF, 0xFFFD6E01
K = (IV[2] + IV[6]) & M
W4B = ((((K + W4) & M) ^ 2) - K) & M
ca, cb = G(X3, X7, X11, X15, W4, W13), G(X3, X7, X11, X15, W4B, W13)
Y3, Y3B, Y11, Y11B = ca["a2"], cb["a2"], ca["c2"], cb["c2"]
DELTA = (W4 - W4B) & M
ETA = 0xE7C1815F
say("== A. constants: Y3 %08x Y3' %08x Y11 %08x Y11' %08x delta %08x factP %s" % (Y3, Y3B, Y11, Y11B, DELTA, ca["d2"] == cb["d2"] and ca["b2"] == cb["b2"]))
x = rol(ETA, 16); s = ((Y3B - Y3) + x) & M
QM = x & 0x7FFFFFFF; QV = ~(s >> 1) & QM & M
chk("Lemma Q mask", "%08x" % QM, "015fe7c1"); chk("Lemma Q value", "%08x" % QV, "00036181")

# ---------------------------------------------------------------- B. cost
say("== B. cost")
members = 65536; lw = -(-members // 7)
chk("list words", lw, 9363)
A_ops, A_ld, S2_ops, S2_ld = 64, 36, 96, 42
tabA = [(3, 1), (9, 7), (27, 14), (16, 8), (9, 6)]
tab2 = [(3, 1), (12, 4), (9, 6), (17, 9), (40, 15), (15, 7)]
chk("stage A table sums", (sum(a for a, _ in tabA), sum(b for _, b in tabA)), (64, 36))
chk("stage 2 table sums", (sum(a for a, _ in tab2), sum(b for _, b in tab2)), (96, 42))
alpha = Fraction(lw * 100) + Fraction(lw * 138, 8) + 256
chk("per alpha budgeted", float(alpha), 1098067.75)
say("   per trial budgeted %.6f (text: less than 16.756)" % float(alpha / members))
exp = Fraction(lw * 100) + Fraction(lw * 138 * 7, 64) + 256
say("   per trial expected %.6f (text: at most 16.448)" % float(exp / members))
charged = Fraction(174, 10) * members
chk("charged per alpha", float(charged), 1140326.4)
say("   margin %.4f%% of the bound (text 3.8%%); margin in operations %.1f" % (100 * float(charged / alpha - 1), float(charged - alpha)))
lc, lu = math.log2(17.4), math.log2(430)
say("   log2 17.4 = %.7f  log2 430 = %.7f  main exponent %.7f (text 4.12102, 8.74819, 99.37282)" % (lc, lu, 104 + lc - lu))
rest = 2.0 ** 98 + 2.0 ** 67 + 2.0 ** 60 + 2.0 ** 22 + 2.0 ** 11 + 1
say("   log2 rest %.9f (text <98.01); 17.4*2^104*2^-7 = 2^%.5f (text 101.121); log2(1+2^-7) = %.7f (text <0.01123)" % (math.log2(rest), 104 + lc - 7, math.log2(1 + 2.0 ** -7)))
true_total = math.log2((17.4 * 2.0 ** 104 + rest) / 430 + 2 + 2.0 ** 63)
say("   true total exponent %.7f ; text chain 99.3841, 99.39, 99.4 ; factor to 99.4: %.4f (text about 1.01)" % (true_total, 2 ** (99.4 - 99.3841)))
say("   pass share: 17.4*2^104/2^98 = 2^%.5f (text: share below 2^-10.12)" % (6 + lc))
say("   uniform: 127+lc-lu = %.5f (text 122.37282 -> 122.4); with 1+2^-7: %.5f" % (127 + lc - lu, 127 + lc - lu + math.log2(1 + 2.0 ** -7)))
say("   f_min = %.3f (text 8,375,631)" % (2.0 ** 24 * -math.log(0.607)))
say("   1-exp(-1/2) = %.6f ; minus 0.003 = %.6f" % (1 - math.exp(-0.5), 1 - math.exp(-0.5) - 0.003))
say("   log2(34/17.4) = %.5f (text has both 2^0.96 and 0.97 bits)" % math.log2(34 / 17.4))
say("   filed 112.4: 116+log2(34)-lu+0.01123 = %.5f ; pkg5 %.5f ; difference %.5f (text: 13.0 = 12 + 0.97 + rounding)" % (116 + math.log2(34) - lu + 0.01123, 104 + lc - lu + 0.01123, 12 + math.log2(34 / 17.4)))
say("   stage-2 budget as share of trials: 2^%.5f (text 2^-5.81); ratio to 2^-6: %.5f ; (1/8)/(7/64) = %.5f (text 1.142)" % (math.log2(lw) + 85 - 104, lw / 8192, 8 / 7))
dw = -(-(lw + 256) // 1024) * 1024
say("   data words %d bytes %d ; 2^19 + bytes = %d < 2^20 %s" % (dw, 32 * dw, 2 ** 19 + 32 * dw, 2 ** 19 + 32 * dw < 2 ** 20))

# ---------------------------------------------------------------- C. the count
say("== C. count")
rows = []
for line in open(EV + "/pinB_e7c1815f.total").read().split("\n"):
    t = line.split()
    if len(t) == 4:
        rows.append((t[0], int(t[1]), int(t[2]), float(t[3])))
    elif len(t) == 2:
        rows.append((t[0], int(t[1]), None, None))
ev = [r for r in rows if r[3] is not None]
par = lambda b: wt(int(b, 16) ^ ror(ETA, 1)) & 1
chk("betas in list", len(rows), 4272)
chk("no eps (file) / odd parity (own)", (len(rows) - len(ev), sum(par(r[0]) for r in rows)), (2110, 2110))
chk("evaluated", len(ev), 2162)
withpart = sorted([r for r in ev if r[3] > 0], key=lambda r: -r[3])
chk("betas with a part", len(withpart), 39)
total = sum(r[3] for r in withpart)
say("   sum of parts %.1f (text 29,977,922); log2 %.4f (text 24.84); 128-log2 %.4f (text 103.16)" % (total, math.log2(total), 128 - math.log2(total)))
say("   k range %d..%d ; k recomputed equal to file: %s" % (min(r[1] for r in rows), max(r[1] for r in rows), all(wt(rol(int(r[0], 16), 12) & 0x7FFFFFFF) == r[1] for r in rows)))
say("   heaviest %s %.1f share %.4f ; two heaviest %.4f ; four sampled %.4f" % (withpart[0][0], withpart[0][3], withpart[0][3] / total, (withpart[0][3] + withpart[1][3]) / total,
    sum(r[3] for r in withpart if r[0] in ("481c6852", "58146852", "481c5852", "58145852")) / total))
say("   prob that a uniform d1 has a beta of the list: %.4f (text 0.469)" % sum(2.0 ** -r[1] for r in rows))

# OUTX
outx = {}
for m in re.finditer(r"^OUTX e7c1815f ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) E1 (\d+) N3 (\d+)$", open(EV + "/pairs_recount_e7c1815f.txt").read(), re.M):
    outx[(m.group(1), m.group(2), m.group(3))] = (int(m.group(4)), int(m.group(5)))
chk("outcomes with nonzero product (OUTX)", len(outx), 287)
prod = {k: Fraction(e * n, 2 ** 80) for k, (e, n) in outx.items()}
byb = {}
for k, v in prod.items():
    byb[k[0]] = byb.get(k[0], 0) + v
partof = {r[0]: r[3] for r in withpart}
kof = {r[0]: r[1] for r in rows}
say("   OUTX betas == betas with a part: %s ; largest |OUTX sum - part| %.4f ; OUTX total %.3f" % (set(byb) == set(partof), max(abs(float(byb[b]) - partof[b]) for b in partof), float(sum(prod.values()))))
posnz = sum(int(m.group(1)) for m in re.finditer(r"^PAIR e7c1815f [0-9a-f]{8} .*? positive (\d+) sampled", open(EV + "/pairs_recount_e7c1815f.txt").read(), re.M))
say("   outcomes with a nonzero E3 count over the 39 betas (PAIR lines): %d (text 508)" % posnz)

# ---------------------------------------------------------------- D. rule A and the SAT file
say("== D. rule A")
RULE = ((0x00010000, 1), (0x00000003, 0), (0x00000006, 0), (0x0000000C, 0), (0x00000018, 1), (0x01800000, 1))
ruleA = lambda h: all(wt(h & m) & 1 == v for m, v in RULE)


def e3_ok(beta, tau, eps, y4, h1, y9, w8):
    """own check: E3 on A and B from G; differences the outcome needs; Y4 in the class"""
    e1 = (Y3 + y4) & M
    y14 = rol(h1, 16) ^ e1                      # h1 = ROR(Y14 XOR e1, 16)
    a, b = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
    return (a["d1"] == h1 and (a["d1"] ^ b["d1"]) == ETA and (a["c2"] ^ b["c2"]) == tau and (a["a2"] ^ b["a2"]) == eps
            and (a["b1"] ^ b["b1"]) == (tau ^ ror(tau, 1)) and (a["b2"] ^ b["b2"]) == ror(tau, 8)
            and (a["d2"] ^ b["d2"]) == ror(beta ^ eps, 7) and (e1 & QM) == QV and (eps ^ rol(beta ^ eps, 1)) == ETA)


sat = {}
txt = open(EV + "/rule_a_sat_e7c1815f.txt").read()
nmodel = nmodel_ok = 0
for line in txt.split("\n"):
    f = line.split()
    if not f or f[0] not in ("ALL", "VIOLATE"):
        continue
    key = (f[1], f[2], f[3])
    rec = {"ans": f[4]}
    if f[4] == "SAT":
        y4, h1, y9, w8 = (int(f[i], 16) for i in (6, 8, 10, 12))
        rec["h1"] = h1
        rec["ok"] = e3_ok(int(f[1], 16), int(f[2], 16), int(f[3], 16), y4, h1, y9, w8)
        nmodel += 1; nmodel_ok += rec["ok"]
    sat.setdefault(key, {})[f[0]] = rec
chk("SAT file keys == OUTX keys", set(sat) == set(outx), True)
chk("ALL: satisfiable", sum(v["ALL"]["ans"] == "SAT" for v in sat.values()), 287)
chk("ALL models that satisfy rule A (own rule)", sum(ruleA(v["ALL"]["h1"]) for v in sat.values()), 270)
chk("VIOLATE: UNSAT", sum(v["VIOLATE"]["ans"] == "UNSAT" for v in sat.values()), 247)
badk = sorted(k for k, v in sat.items() if v["VIOLATE"]["ans"] == "SAT")
chk("VIOLATE: SAT", len(badk), 40)
chk("every model is a solution by own G code", (nmodel_ok, nmodel), (327, 327))
chk("violating models violate rule A (own rule)", sum(not ruleA(sat[k]["VIOLATE"]["h1"]) for k in badk), 40)
chk("betas with a dropped outcome", len({k[0] for k in badk}), 14)
lost = sum(prod[k] for k in badk)
say("   lost exactly %.4f (text 12,039.8 / 12,040) ; share %.6f%% (text 0.041%%) ; kept %.7f (text 0.999598)" % (float(lost), 100 * float(lost / sum(prod.values())), float(1 - lost / sum(prod.values()))))
say("   count minus lost: %.2f (text 29,965,882) ; /2^23 %.4f ; /2^22 %.4f ; /2^24 %.4f ; /f_min %.4f" % (total - float(lost), 29965882 / 2 ** 23, 29965882 / 2 ** 22, 29965882 / 2 ** 24, 29965882 / 8375631))
say("   full count: /2^23 %.4f ; /2^24 %.4f ; e74181df 36358944: /2^23 %.4f /2^24 %.4f" % (29977922 / 2 ** 23, 29977922 / 2 ** 24, 36358944 / 2 ** 23, 36358944 / 2 ** 24))
table = [("f8342852", 13, 8, 8, 8448, 8448.0), ("78346852", 13, 12, 4, 53520, 1296.0), ("f87c2852", 14, 6, 6, 720, 720.0), ("78343852", 13, 10, 4, 13320, 648.0),
         ("c81c39b3", 14, 2, 2, 384, 384.0), ("78345852", 13, 8, 2, 21648, 144.0), ("787c5852", 14, 1, 1, 128, 128.0), ("787c6852", 14, 1, 1, 128, 128.0),
         ("787c3852", 14, 1, 1, 64, 64.0), ("58743852", 13, 16, 3, 5138, 27.6), ("d81428d3", 13, 2, 2, 16, 16.0), ("d81428b3", 13, 2, 2, 14, 14.0),
         ("d8142873", 13, 2, 2, 12, 12.0), ("58fc3852", 14, 2, 2, 10, 10.2)]
tb = 0
for b, k, no, nd, part, drop in table:
    mine = (kof[b], sum(1 for q in outx if q[0] == b), sum(1 for q in badk if q[0] == b), partof[b], float(sum(prod[q] for q in badk if q[0] == b)))
    if not (mine[0] == k and mine[1] == no and mine[2] == nd and abs(mine[3] - part) < 0.51 and abs(mine[4] - drop) < 0.051):
        tb += 1
    if b in ("58fc3852", "58743852"):
        say("   row %s: part in .total %.1f, OUTX sum %.4f, dropped %.4f" % (b, partof[b], float(byb[b]), mine[4]))
chk("rows of the dropped table that differ", tb, 0)
worst = max(badk, key=lambda q: prod[q])
say("   largest dropped outcome: beta %s tau %s eps %s %.1f (text f8342852 17d4e830 f298b0a9 4,096.0)" % (worst + (float(prod[worst]),)))
old_list = {l.split()[0] for l in open(EV + "/snapshot/pinB_e7c1815f.total").read().split("\n") if l.split()}
bad_old = [q for q in badk if q[0] in old_list]
say("   dropped outcomes inside the 1,500 list: %d carrying %.2f ; outside: %d carrying %.2f ; outcomes of the 1,500 list in OUTX: %d" % (
    len(bad_old), float(sum(prod[q] for q in bad_old)), len(badk) - len(bad_old), float(sum(prod[q] for q in badk if q[0] not in old_list)), sum(1 for q in outx if q[0] in old_list)))

# follow-up's SAT file
ft = open(EV + "/followup/pinB3_sat.txt").read()
fa = {(m.group(3), m.group(1), m.group(2)): m.group(4) for m in re.finditer(r"^A6 ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) (SAT|UNSAT)", ft, re.M)}
say("   follow-up A6 answers: %d (UNSAT %d, SAT %d); all equal to rule_a_sat: %s ; keys inside OUTX: %s" % (len(fa), sum(v == "UNSAT" for v in fa.values()), sum(v == "SAT" for v in fa.values()),
    all(sat[k]["VIOLATE"]["ans"] == v for k, v in fa.items() if k in sat), all(k in sat for k in fa)))
amc = [l for l in ft.split("\n") if l.startswith("AMC ") or l.startswith("amc ")]
say("   follow-up approxmc lines: %d ; first: %s" % (len(amc), amc[0][:150] if amc else "-"))

# ---------------------------------------------------------------- E. exact share kept by rule A from the D lines (1,500 list)
say("== E. share kept by rule A, own sum from the follow-up's D lines with the exact N1 of OUTX")
NC = B + "/night/cheaper"


def split_share(tag, rules, eta, weights_exact=None):
    p1 = {}
    for line in open("%s/%s_outcomes.txt" % (NC, tag)):
        f = line.split()
        p1[(f[1], f[2], f[3])] = float(f[5])
    we = wt(rol(eta, 16) & 0x7FFFFFFF)
    keyw, keyn = {}, {}
    for line in open("%s/%s_dh.txt" % (NC, tag)):
        f = line.split()
        if f[0] != "M":
            continue
        idx, tau, eps, beta, n = int(f[1]), f[2], f[3], f[5], float(f[6])
        if weights_exact is not None:
            if (beta, tau, eps) not in weights_exact:
                continue                                    # E1 count zero
            keyw[idx] = Fraction(weights_exact[(beta, tau, eps)][0], 2 ** 80)
        else:
            if p1[(beta, tau, eps)] < -900:
                continue
            keyw[idx] = 2.0 ** (we - wt(rol(int(beta, 16), 12) & 0x7FFFFFFF) + p1[(beta, tau, eps)])
        keyn[idx] = n
    tot = 0.0; res = {name: 0.0 for name in rules}; viol = {name: set() for name in rules}; pats = set()
    for line in open("%s/%s_dh.d" % (NC, tag)):
        f = line.split()
        idx, hv, mass = int(f[1]), int(f[4], 16), float(f[5])
        if idx not in keyw:
            continue
        w = float(keyw[idx]) * mass
        tot += w; pats.add(hv)
        for name, rule in rules.items():
            if all(wt(hv & m) & 1 == v for m, v in rule):
                res[name] += w
            else:
                viol[name].add(idx)
    return tot, res, viol, len(keyw), len(pats)


tot, res, viol, nk, npat = split_share("pinB3", {"A6": RULE, "A5": RULE[:5], "A2": RULE[3:5]}, ETA, outx)
say("   e7c1815f, exact N1: outcomes %d, patterns %d, total %.1f ; A6 keeps %.8f (text 0.999839), outcomes with violating mass %d (SAT said 27) ; A5 keeps %.8f (%d) ; A2 keeps %.10f (%d)" % (
    nk, npat, tot, res["A6"] / tot, len(viol["A6"]), res["A5"] / tot, len(viol["A5"]), res["A2"] / tot, len(viol["A2"])))
tot2, res2, viol2, nk2, npat2 = split_share("pinB3", {"A6": RULE}, ETA, None)
say("   e7c1815f, two-decimal P1 (as the follow-up): total %.1f ; A6 keeps %.8f" % (tot2, res2["A6"] / tot2))
R4 = ((0x0000000C, 0), (0x00000018, 1), (0x00000006, 0), (0x01400000, 1), (0x00000003, 0))
tot4, res4, viol4, nk4, npat4 = split_share("pinB4", {"five": R4, "four": R4[:4], "three": R4[:3], "two": R4[:2]}, 0xE74181DF, None)
say("   e74181df: outcomes %d, patterns %d, total %.1f ; five conditions keep %.10f (outcomes with violating mass %d) ; four %.10f (%d) ; three %.10f (%d) ; two %.10f (%d)" % (
    nk4, npat4, tot4, res4["five"] / tot4, len(viol4["five"]), res4["four"] / tot4, len(viol4["four"]), res4["three"] / tot4, len(viol4["three"]), res4["two"] / tot4, len(viol4["two"])))
say("   e74181df: mass lost by the five conditions %.4f of %.1f" % (tot4 - res4["five"], tot4))

# ---------------------------------------------------------------- F. the two printed solutions
say("== F. printed solutions")


def seven(Y1, Y6, Y12, w12, w5, Y4, Y9, Y14, w8):
    ea, eb = G(Y1, Y6, Y11, Y12, w12, w5), G(Y1, Y6, Y11B, Y12, w12, (w5 + DELTA) & M)
    fa_, fb = G(Y3, Y4, Y9, Y14, 0, w8), G(Y3B, Y4, Y9, Y14, 0, w8)
    R = (ea["a2"] ^ fa_["c2"] ^ eb["a2"] ^ fb["c2"], fa_["a2"] ^ ea["c2"] ^ fb["a2"] ^ eb["c2"],
         fa_["b2"] ^ ea["d2"] ^ fb["b2"] ^ eb["d2"], ea["b2"] ^ fa_["d2"] ^ eb["b2"] ^ fb["d2"])
    return R, fa_["d1"], ea["b1"] ^ eb["b1"], ea["a2"] ^ eb["a2"], ea["c2"] ^ eb["c2"], ((Y3 + Y4) & QM) == QV, fa_["d1"] ^ fb["d1"]


for name, v, want in (("violating", (0x052CE267, 0xFAD31D99, 0x69DA227B, 0, 0x57D7DFEF, 0xC0D07BF1, 0xFCDE77B6, 0xA48CB1EE, 0x5141CE8C), ("d87fa4af", "f8342852", "17d4e830", "f298b0a9")),
                      ("in class", (0, 0x7E1401E5, 0x5A538AB4, 0, 0x234E3245, 0x0AD073E5, 0x61E4852D, 0xDDCC82F4, 0xA2EE086C), ("e37197ef", "481c6852", "481c2830", "2d5730a9"))):
    R, h1, beta, tau, eps, inclass, eta = seven(*v)
    fails = [i for i, (m, val) in enumerate(RULE) if wt(h1 & m) & 1 != val]
    say("   %s: R %s ; h1 %08x beta %08x tau %08x eps %08x (text %s) ; in class %s ; eta %08x ; rule A %s ; failing conditions (index in 16,0-1,1-2,2-3,3-4,23-24): %s" % (
        name, "zero" if not any(R) else "NOT ZERO", h1, beta, tau, eps, " ".join(want), inclass, eta, ruleA(h1), fails))
    if any(R) or ("%08x" % h1, "%08x" % beta, "%08x" % tau, "%08x" % eps) != want or not inclass:
        bad.append("solution " + name)

# ---------------------------------------------------------------- G. Lemma A
say("== G. Lemma A")
S = ALL = V = 0
zc = []
for m, val in RULE:
    hb = [i for i in range(32) if m >> i & 1]
    for i in hb:
        e = (i + 16) % 32
        assert QM >> e & 1, "rule reads a free bit of e1"
        val ^= QV >> e & 1
    lo = sorted((i + 24) % 32 for i in hb)
    if len(lo) == 2:
        assert lo[1] == lo[0] + 1
        S |= 1 << lo[0]
    ALL |= 1 << lo[0]; V |= val << lo[0]
    zc.append((lo, val))
chk("S ALL V", ("%08x" % S, "%08x" % ALL, "%08x" % V), ("0f008000", "0f008100", "0a008000"))
say("   conditions on z (bits, wanted XOR): %s" % zc)
say("   text: bit 8 = 0; 24,25 equal; 25,26 differ; 26,27 equal; 27,28 differ; 15,16 differ")
say("   e1 bits used: %s ; values in 00036181: %s" % (sorted({(i + 16) % 32 for m, _ in RULE for i in range(32) if m >> i & 1}), [(e, QV >> e & 1) for e in sorted({(i + 16) % 32 for m, _ in RULE for i in range(32) if m >> i & 1})]))
rng = random.Random(5)
free = [i for i in range(32) if not QM >> i & 1]
wrong = 0
for _ in range(400000):
    z = rng.getrandbits(32)
    e1 = QV | sum(((rng.getrandbits(1)) << i) for i in free)
    h1 = ror(ror(z, 8) ^ e1, 16)
    word = ((z ^ ((z >> 1) & S)) & ALL) ^ V
    wrong += (word == 0) != ruleA(h1)
    # (a): ROL(h1,24) = z XOR ROL(e1,8)
    wrong += rol(h1, 24) != (z ^ rol(e1, 8))
chk("Lemma A (a),(c) on 400,000 random (z, member): disagreements", wrong, 0)

# ---------------------------------------------------------------- H. real runs with rule A
say("== H. real runs")
rt = open(EV + "/followup/real32_pinB3.txt").read()
a6 = [int(v) for v in re.findall(r"pass A6: (\d+)", rt)]
e1p = [int(v) for v in re.findall(r"E1 requires the eta of Y4: (\d+)", rt)]
early = [int(v) for v in re.findall(r"early test passes: (\d+)", rt)]
per = 2 ** 38; p = 1 / 64; sd = math.sqrt(per * p * (1 - p))
say("   A6 counts %s sum %d ; z %s ; total z %.2f ; max rel %.3e ; log2 share %.6f ; 7*share %.7f ; (1/8)/(7*share) %.5f" % (a6, sum(a6), ["%+.2f" % ((c - per * p) / sd) for c in a6],
    (sum(a6) - 4 * per * p) / (2 * sd), max(abs(c / (per * p) - 1) for c in a6), math.log2(sum(a6) / 2 ** 40), 7 * sum(a6) / 2 ** 40, 0.125 / (7 * sum(a6) / 2 ** 40)))
say("   E1 passes %s sum %d log2 share %.4f ; early %s sum %d" % (e1p, sum(e1p), math.log2(sum(e1p) / 2 ** 40), early, sum(early)))
say("   1521 in 2^40: 2^%.4f ; 104 minus: %.4f ; budget factor %.4f" % (math.log2(1521) - 40, 104 + math.log2(1521) - 40, 88 - (104 + math.log2(1521) - 40)))
lay = [1462, 1494, 1486, 1472, 1432, 1468, 1471, 1527]
mean = sum(lay) / 8
say("   eight layout runs: mean %.2f log2 rate %.4f ; budget 2^-16 over mean: 2^%.4f (text 13.47) ; chi2 %.2f (text 3.6)" % (mean, math.log2(mean) - 40, -16 - (math.log2(mean) - 40), sum((v - mean) ** 2 / mean for v in lay)))

# ---------------------------------------------------------------- I. self-tests
say("== I. self-test files")
js = []
for sd_ in ("61", "62"):
    lines = open(EV + "/selftest_1200000_%s.json" % sd_).read().split("\n")
    js.append((lines[0], json.loads(lines[1])))
lanes = sum(j["lanes_checked"] for _, j in js); right = sum(j["lanes_right"] for _, j in js)
pa = sum(j["lanes_passing_rule_a"] for _, j in js); en = sum(j["batches_entering_stage_2"] for _, j in js); cs = sum(j["cases"] for _, j in js)
say("   lanes %d right %d ; pass A %d = 2^%.4f ; entered %d of %d = %.5f ; largest lane %.5f * 2^32 ; registers %d ; zero words %d" % (lanes, right, pa, math.log2(pa / lanes), en, cs, en / cs,
    max(j["largest_lane"] for _, j in js) / 2 ** 32, max(j["registers"] for _, j in js), sum(j["zero_test_words"] for _, j in js)))
import hashlib
now = hashlib.sha256(open(P5 + "/blake3-r2/experiments/halfsearch.py", "rb").read()).hexdigest()
say("   program sha now %s ; in both self-test files: %s" % (now[:16], all(now in h for h, _ in js)))
fb = json.loads(open(EV + "/followup/batch4_two_class_filed_1200000_s51.json").read())
say("   research batch: lanes %d ; A %d+%d ; rest %d+%d ; pass A %d ; entered %d of %d" % (fb["lanes_checked"], fb["stage_A"]["operations"], fb["stage_A"]["loads"],
    fb["stage_B"]["operations"] + fb["stage_C"]["operations"], fb["stage_B"]["loads"] + fb["stage_C"]["loads"], fb["lanes_passing"]["A"], fb["batches_entering"]["stage_B"], fb["cases"]))

# ---------------------------------------------------------------- J. whole-list recount
say("== J. calc2 files")
got = {}
for line in open(EV + "/calc2_total_e7c1815f.txt").read().split("\n"):
    f = line.split()
    if len(f) >= 4:
        got[f[0]] = (float(f[3]), f[4:] )
    elif f:
        got[f[0]] = (None, f[2:])
lst = {r[0]: r[3] for r in rows}
diff = [b for b in lst if b not in got or (got[b][0] is None) != (lst[b] is None) or (lst[b] is not None and abs(got[b][0] - lst[b]) > 0.06)]
flag = sorted(b for b, (pp, fl) in got.items() if fl)
say("   betas %d ; differ from .total %d ; with a part %d ; sum %.1f ; flagged %s" % (len(got), len(diff), sum(1 for v in got.values() if v[0]), sum(v[0] for v in got.values() if v[0]), [(b, got[b][1]) for b in flag]))
ct = open(EV + "/calc2_recount_e7c1815f.txt").read()
cp = {m.group(1): float(m.group(2)) for m in re.finditer(r"^EXACT-E1 e7c1815f ([0-9a-f]{8}) .*class-rate part ([\d.]+) ", ct, re.M)}
co = re.findall(r"^OUT ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) log2P1 (-?[\d.]+) log2N3 (-?[\d.]+)$", ct, re.M)
nz = {(a, b_, c) for a, b_, c, lp, ln in co if float(lp) > -900}
say("   mass recount: betas %d sum %.1f equal parts %s ; outcome lines %d nonzero %d == OUTX keys %s ; sampled/fallback lines %d ; sha %s" % (
    len(cp), sum(cp.values()), all(abs(cp[b] - partof[b]) < 0.06 for b in partof) and set(cp) == set(partof), len(co), len(nz), nz == set(outx),
    len(re.findall(r"sampled [1-9]|formula fallbacks [1-9]", ct)), re.search(r"sha256 ([0-9a-f]{16})", ct).group(1)))

say("== RESULT: %d named checks differ: %s" % (len(bad), bad))
OUT.close()
print("differ:", len(bad), bad[:6])
