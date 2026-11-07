"""Significance tests for rotscan.c output (out_<set>_scan.tsv, out_<set>_joint.tsv).

For every job (scan, list, src, i, j, r, op, half) the statistics are turned into z-scores against a reference:
  vs0 : the analytic law of a uniform 32-bit V (HW ~ Bin(32,1/2), d4 law exact, bits fair, Poisson tails)
  vsS : AB scan, data D against the shuffle control S (same row's A->B difference law, link to A broken)
  vsC : WW scan, data D against the column-shuffle control C (one-word marginals kept, cross-word links broken)
  vsU : WW scan, against U = uniform words with the same (i, j, r, op) (this is the right null when i == j)
Statistic families: mean HW; bit chi^2 (32 dof, Wilson-Hilferty z); tails HW<=4, HW<=8, HW>=24, d4<=4, d4<=6,
|V|<=256 (signed), V == 0; collision pairs. Discovery threshold |z| >= 5 on T (train half); confirmed if the same
statistic has |z| >= 3 with the same sign on V (test half). Mode multiplicity (maxm) >= 4 is reported separately.
"""
import sys
sys.dont_write_bytecode = True
import os
from math import comb
import numpy as np
from scipy import stats as st

HERE = os.path.dirname(os.path.abspath(__file__))

# ---- analytic uniform laws ----
PHW = np.array([comb(32, k) for k in range(33)], dtype=float) / 2**32
b8 = np.array([comb(8, k) for k in range(9)], dtype=float) / 256
m8 = np.zeros(5)
for c in range(9):
    m8[min(c, 8 - c)] += b8[c]
PD4 = np.array([1.0])
for _ in range(4):
    PD4 = np.convolve(PD4, m8)
PD4 = np.concatenate([PD4, np.zeros(17 - len(PD4))])
TAILS = {"hw<=4": lambda h, d: h[:5].sum(), "hw<=8": lambda h, d: h[:9].sum(), "hw>=24": lambda h, d: h[24:].sum(),
         "d4<=4": lambda h, d: d[:5].sum(), "d4<=6": lambda h, d: d[:7].sum()}
P0 = {"hw<=4": PHW[:5].sum(), "hw<=8": PHW[:9].sum(), "hw>=24": PHW[24:].sum(), "d4<=4": PD4[:5].sum(),
      "d4<=6": PD4[:7].sum(), "msmall": 513 / 2**32, "zero": 2.0**-32}


def zpois(a, lam):
    """z for observing a under Poisson(lam), signed (excess > 0)."""
    if a >= lam:
        p = st.poisson.sf(a - 1, lam)
        return float(min(st.norm.isf(max(p, 1e-300)), 37.0)) if p < 0.5 else 0.0
    p = st.poisson.cdf(a, lam)
    return float(-min(st.norm.isf(max(p, 1e-300)), 37.0)) if p < 0.5 else 0.0


def z2(a, b):
    """two-sample count comparison: a ~ Bin(a+b, 1/2) under equal rates; signed z (a > b positive)."""
    m = a + b
    if m == 0:
        return 0.0
    if a >= b:
        p = st.binom.sf(a - 1, m, 0.5)
        return float(min(st.norm.isf(max(p, 1e-300)), 37.0)) if p < 0.5 else 0.0
    p = st.binom.cdf(a, m, 0.5)
    return float(-min(st.norm.isf(max(p, 1e-300)), 37.0)) if p < 0.5 else 0.0


def wh(chi2, k=32):
    return float(((chi2 / k) ** (1 / 3) - (1 - 2 / (9 * k))) / np.sqrt(2 / (9 * k)))


def parse(path):
    rows = []
    with open(path) as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").split("\t")
            hwh = np.array(p[9].split(","), dtype=float)
            d4h = np.array(p[10].split(","), dtype=float)
            bit = np.array(p[11].split(","), dtype=float)
            rows.append(dict(scan=p[0], list=p[1], src=p[2], i=int(p[3]), j=int(p[4]), r=int(p[5]), op=p[6],
                             half=p[7], n=int(p[8]), hwh=hwh, d4h=d4h, bit=bit, msmall=float(p[12]),
                             zero=float(p[13]), coll=float(p[14]), maxm=int(p[15]), modev=p[16]))
    return rows


def feats(o):
    n = o["n"]; h = o["hwh"]; d = o["d4h"]; k = np.arange(33)
    m = (h * k).sum() / n
    v = (h * k * k).sum() / n - m * m
    f = dict(mean=m, var=v, n=n, bit=o["bit"] / n, coll=o["coll"], msmall=o["msmall"], zero=o["zero"])
    for t, fn in TAILS.items():
        f[t] = fn(h, d)
    return f


def zs_vs0(f):
    n = f["n"]; z = {}
    z["meanHW"] = (f["mean"] - 16) / np.sqrt(8 / n)
    z["bits"] = wh((((f["bit"] - 0.5) ** 2) / (0.25 / n)).sum())
    for t in list(TAILS) + ["msmall", "zero"]:
        z[t] = zpois(f[t], n * P0[t])
    z["coll"] = zpois(f["coll"], n * (n - 1) / 2 / 2**32)
    return z


def zs_two(f, g):
    n = f["n"]; z = {}
    z["meanHW"] = (f["mean"] - g["mean"]) / np.sqrt((f["var"] + g["var"]) / n + 1e-300)
    pb = (f["bit"] + g["bit"]) / 2
    den = pb * (1 - pb) * 2 / n
    ok = den > 0
    z["bits"] = wh((((f["bit"] - g["bit"]) ** 2)[ok] / den[ok]).sum()) if ok.any() else 0.0
    for t in list(TAILS) + ["msmall", "zero"]:
        z[t] = z2(f[t], g[t])
    z["coll"] = z2(f["coll"], g["coll"])
    return z


STATS = ["meanHW", "bits", "hw<=4", "hw<=8", "hw>=24", "d4<=4", "d4<=6", "msmall", "zero", "coll"]


def run(setname):
    rows = parse(os.path.join(HERE, "out_%s_scan.tsv" % setname))
    idx = {}
    for o in rows:
        idx[(o["scan"], o["list"], o["src"], o["i"], o["j"], o["r"], o["op"], o["half"])] = o
    F = {k: feats(o) for k, o in idx.items()}
    print("=" * 110)
    print("[%s] jobs %d, rows per half %d" % (setname, len(rows), rows[0]["n"]))

    cache = {}

    def zfor(key, refkey):
        ck = (key, refkey)
        if ck not in cache:
            cache[ck] = zs_vs0(F[key]) if refkey is None else zs_two(F[key], F[refkey])
        return cache[ck]

    def table(scan, lists, comps, label):
        print("\n" + label)
        print("  each cell: (#combos |z|>=5 on T) / (#of those confirmed on V: same sign, |z|>=3); combos per cell = "
              "4x4 word pairs x 32 r x ops (AB: x,s,r = 3; WW: x,s = 2), split by subset")
        hdr = "  %-6s %-10s %-9s" % ("list", "compare", "subset") + "".join("%9s" % s for s in STATS)
        print(hdr)
        confirmed = []
        subsets = ("r=0,i=j", "other") if scan == "AB" else ("i=j", "i!=j")
        for l in lists:
            for (cname, src0, ref) in comps:
                if l == "U":
                    if ref != "0":
                        continue
                    src = "U"; cname = "U vs 0"
                else:
                    src = src0
                for subset in subsets:
                    cells = []
                    for s in STATS:
                        nt = nv = 0
                        for i in range(4):
                            for j in range(4):
                                for r in range(32):
                                    if scan == "WW" and i == j and r == 0:
                                        continue
                                    if scan == "AB":
                                        if (subset == "r=0,i=j") != (i == j and r == 0):
                                            continue
                                    elif (subset == "i=j") != (i == j):
                                        continue
                                    for op in ("xsr" if scan == "AB" else "xs"):
                                        zz = []
                                        for half in "TV":
                                            ka = (scan, l, src, i, j, r, op, half)
                                            if ka not in F:
                                                break
                                            if ref == "0":
                                                zz.append(zfor(ka, None)[s])
                                            else:
                                                rl = "U" if ref == "U" else l
                                                kb = (scan, rl, ref, i, j, r, op, half)
                                                if kb not in F:
                                                    break
                                                zz.append(zfor(ka, kb)[s])
                                        if len(zz) < 2:
                                            continue
                                        if abs(zz[0]) >= 5:
                                            nt += 1
                                            if abs(zz[1]) >= 3 and np.sign(zz[1]) == np.sign(zz[0]):
                                                nv += 1
                                                confirmed.append((abs(zz[0]), l, cname, s, i, j, r, op, zz[0], zz[1]))
                        cells.append("%4d/%-4d" % (nt, nv))
                    print("  %-6s %-10s %-9s" % (l, cname, subset) + "".join("%9s" % c for c in cells))
        return confirmed

    confAB = table("AB", ["dig", "e1", "e3", "plant", "U"],
                   [("D vs 0", "D", "0"), ("D vs S", "D", "S"), ("S vs 0", "S", "0")],
                   "-- AB scan: V = B_j op rotl(A_i, r).  'r=0,i=j' is the XOR/modular difference itself; 'other' is "
                   "every rotational or cross-word relation")
    print("\n  top confirmed AB findings outside 'r=0,i=j' (list, comparison, statistic, i, j, r, op, zT, zV); "
          "word index 0..3 = digest words 1,3,4,6 / outputs (a2 b2 c2 d2) / (e2 f2 g2 h2):")
    other = [c for c in confAB if not (c[4] == c[5] and c[6] == 0)]
    for l in ("dig", "e1", "e3", "plant", "U"):
        for cname in ("D vs 0", "D vs S", "S vs 0", "U vs 0"):
            sel = sorted([c for c in other if c[1] == l and c[2] == cname], reverse=True)
            print("   %s / %s: %d confirmed" % (l, cname, len(sel)))
            for c in sel[:8]:
                print("      %-7s i%d j%d r%2d op %s  zT %+7.2f zV %+7.2f" % (c[3], c[4], c[5], c[6], c[7], c[8], c[9]))
    print("\n  mode multiplicity >= 4 (rotation + constant relations, B_j = rotl(A_i,r) op const), AB scan:")
    cnt = 0
    for k, o in idx.items():
        if k[0] == "AB" and o["maxm"] >= 4:
            cnt += 1
            if cnt <= 40:
                print("     ", k, "maxm", o["maxm"], "value", o["modev"])
    print("     total AB jobs with maxm >= 4: %d" % cnt)

    confWW = table("WW", ["R", "K1", "K3", "DA", "RP", "U"],
                   [("D vs C", "D", "C"), ("D vs U", "D", "U"), ("C vs U", "C", "U"), ("D vs 0", "D", "0")],
                   "-- WW scan: V = X_j op rotl(X_i, r) inside one 4-word set")
    print("\n  top confirmed WW findings (set, comparison, statistic, i, j, r, op, zT, zV):")
    for l in ("R", "K1", "K3", "DA", "RP", "U"):
        for cname in ("D vs C", "D vs U", "C vs U", "U vs 0"):
            sel = sorted([c for c in confWW if c[1] == l and c[2] == cname], reverse=True)
            print("   %s / %s: %d confirmed" % (l, cname, len(sel)))
            for c in sel[:10]:
                print("      %-7s i%d j%d r%2d op %s  zT %+7.2f zV %+7.2f" % (c[3], c[4], c[5], c[6], c[7], c[8], c[9]))
    print("\n  Named rotational-XOR coordinates of R (op x): collision pairs D / C / U and H2 of D, T | V")
    named = (("U4 = R4 ^ ROR(R1,8)", 0, 2, 24), ("U6 = R6 ^ ROR(R3,8)", 1, 3, 24),
             ("W4 = R4 ^ ROR(R1,7)", 0, 2, 25), ("W3 = R3 ^ ROL(R6,7)", 3, 1, 7),
             ("R1 ^ ROR(R4,24)=R1^ROL(R4,8)", 2, 0, 8), ("R3 ^ ROL(R6,8)", 3, 1, 8))
    for nm, i, j, r in named:
        vals = []
        for half in "TV":
            d, c, u = (F[("WW", ll, ss, i, j, r, "x", half)] for ll, ss in (("R", "D"), ("R", "C"), ("U", "U")))
            nn = d["n"]
            h2 = -np.log2(d["coll"] / (nn * (nn - 1) / 2)) if d["coll"] else 99
            vals.append("D %8.0f C %6.0f U %6.0f H2 %.2f mode %d" % (d["coll"], c["coll"], u["coll"], h2,
                                                                     idx[("WW", "R", "D", i, j, r, "x", half)]["maxm"]))
        print("     %-30s %s" % (nm, " | ".join(vals)))
    print("\n  mode multiplicity >= 4 in WW scan (X_j = rotl(X_i, r) op const), data only, by set:")
    for l in ("R", "K1", "K3", "DA", "RP"):
        hits = [(o["maxm"], k, o["modev"]) for k, o in idx.items() if k[0] == "WW" and k[1] == l and k[2] == "D"
                and o["maxm"] >= 4]
        hits.sort(reverse=True)
        print("    %s: %d jobs; top: %s" % (l, len(hits), [(h[0], h[1][3:8], h[2]) for h in hits[:6]]))
    hits = [(o["maxm"], k) for k, o in idx.items() if k[0] == "WW" and k[2] in ("C", "U") and o["maxm"] >= 4]
    print("    controls C/U with maxm >= 4: %d jobs; top %s" % (len(hits), sorted(hits, reverse=True)[:6]))


def joint(setname):
    path = os.path.join(HERE, "out_%s_joint.tsv" % setname)
    P128 = np.array([comb(128, k) for k in range(129)], dtype=float) / 2.0**128
    print("\n-- joint over 4 words, same r: sum HW(B_w ^ rotl(A_w, r)); z of mean vs Bin(128,1/2) and vs S; "
          "count sumHW<=44 (uniform P %.2e)" % P128[:45].sum())
    data = {}
    with open(path) as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").split("\t")
            data[(p[0], p[1], int(p[2]), p[3])] = (int(p[4]), np.array(p[5].split(","), dtype=float))
    k = np.arange(129)
    for l in ("dig", "e1", "e3", "plant", "U"):
        worst = []
        for r in range(32):
            zz = []
            for half in "TV":
                n, h = data[(l, "U" if l == "U" else "D", r, half)]
                m = (h * k).sum() / n; v = (h * k * k).sum() / n - m * m
                z0 = (m - 64) / np.sqrt(32 / n)
                t44 = h[:45].sum(); z44 = zpois(t44, n * P128[:45].sum())
                if l != "U":
                    n2, g = data[(l, "S", r, half)]
                    m2 = (g * k).sum() / n2; v2 = (g * k * k).sum() / n2 - m2 * m2
                    zS = (m - m2) / np.sqrt((v + v2) / n)
                else:
                    zS = 0.0
                zz.append((z0, zS, z44, m, t44))
            worst.append((max(abs(zz[0][0]), abs(zz[0][1])), r, zz))
        worst.sort(reverse=True)
        print("  %-5s (largest |z| on T first)" % l)
        for w in worst[:4]:
            r, zz = w[1], w[2]
            print("     r=%2d  T: mean %.3f z0 %+.2f zS %+.2f n44 %d z44 %+.2f | V: mean %.3f z0 %+.2f zS %+.2f n44 %d z44 %+.2f" % (
                r, zz[0][3], zz[0][0], zz[0][1], zz[0][4], zz[0][2], zz[1][3], zz[1][0], zz[1][1], zz[1][4], zz[1][2]))


if __name__ == "__main__":
    for s in sys.argv[1:] or ("rand", "ctx"):
        run(s)
        joint(s)
