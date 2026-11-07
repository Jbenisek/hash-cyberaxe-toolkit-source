"""analyse_arms.py - found vs predicted and clustering for the toy8 t_hi-walk arms of PLAN.txt (research only)."""
import math
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
# the rig's ledger (PREREG.txt section 3): mass_D, n, |D|
LEDGER = {0: (2097152, 16, 4), 1: (3670016, 16, 16), 2: (3670016, 16, 16), 3: (4456448, 16, 16),
          4: (1048576, 8, 32), 5: (5767168, 16, 16), 6: (2097152, 16, 4), 7: (2097152, 16, 4)}
PS = {s: m / (n * d * 2 ** 40) for s, (m, n, d) in LEDGER.items()}
NOUT = {"C": [2048, 1170, 1170, 964, 4096, 745, 2048, 2048], "W32": [64, 37, 37, 30, 128, 23, 64, 64],
        "W256": [8, 5, 5, 4, 16, 3, 8, 8]}
NT = {"C": 1, "W32": 32, "W256": 256}


def chi2_quantile(p, k):
    # Wilson-Hilferty
    z = {0.023: -1.9954}[p]
    return k * (1 - 2 / (9 * k) + z * math.sqrt(2 / (9 * k))) ** 3


def parse(arm):
    runs, hits, parts = [], [], []
    for s in range(8):
        fn = os.path.join(OUT, "%s_set%d.txt" % (arm, s))
        if not os.path.exists(fn):
            return None
        for line in open(fn):
            f = line.split()
            if not f:
                continue
            if f[0] == "RUN":
                d = {key: f[f.index(key) + 1] for key in ("run", "trials", "tzero", "bad", "coll", "listed")}
                runs.append((s, int(d["run"]), int(d["trials"]), int(d["tzero"]), int(d["bad"]), int(d["coll"]), int(d["listed"])))
            elif f[0] == "HIT":
                d = dict(zip(f[1::2], f[2::2]))
                hits.append(dict(set=s, run=int(d["run"]), g=int(d["g"]), k=int(d["k"]), thi=int(d["thi"]), d1=d["d1"],
                                 t=int(d["t"]), fwd=int(d["fwd"]), cv=int(d["cv"]), tree=int(d["tree"])))
            elif f[0] == "PART":
                parts.append(line.strip())
    return runs, hits, parts


def main():
    res = {}
    for arm in ("C", "W32", "W256"):
        p = parse(arm)
        if p is None:
            print("arm %s: incomplete" % arm)
            continue
        runs, hits, parts = p
        found = sum(1 for h in hits if h["fwd"] and h["cv"])
        bogus = sum(1 for h in hits if not (h["fwd"] and h["cv"]))
        trials = sum(r[2] for r in runs)
        bad = sum(r[4] for r in runs)
        coll = sum(r[5] for r in runs)
        listed = sum(r[6] for r in runs)
        pred = sum(r[2] * PS[r[0]] for r in runs)
        tree_ok = sum(1 for h in hits if h["tree"] == 1)
        tree_try = sum(1 for h in hits if h["tree"] >= 0)
        ratio, se = found / pred, math.sqrt(found) / pred
        lb = chi2_quantile(0.023, 2 * found) / 2 / pred
        res[arm] = (found, pred)
        print("ARM %s: trials %d, bad %d, GPU coll %d, listed %d, FOUND %d (bogus %d), PREDICTED %.2f, ratio %.5f +- %.5f, "
              "97.7%% lower bound %.5f (>= 10/11 = 0.90909: %s); complete-message tree hashes %d/%d"
              % (arm, trials, bad, coll, listed, found, bogus, pred, ratio, se, lb, lb >= 10 / 11, tree_ok, tree_try))
        per = defaultdict(lambda: [0, 0.0])
        for r in runs:
            per[r[0]][1] += r[2] * PS[r[0]]
        for h in hits:
            if h["fwd"] and h["cv"]:
                per[h["set"]][0] += 1
        print("   per set found/pred: " + "  ".join("%d:%d/%.1f=%.3f" % (s, a, b, a / b) for s, (a, b) in sorted(per.items())))
        chi = sum((a - b) ** 2 / b for a, b in per.values())
        print("   chi-square over 8 sets %.2f on 8 df" % chi)
        # run dispersion
        cnt = Counter((h["set"], h["run"]) for h in hits if h["fwd"] and h["cv"])
        disp = sum((cnt.get((r[0], r[1]), 0) - r[2] * PS[r[0]]) ** 2 / (r[2] * PS[r[0]]) for r in runs) / len(runs)
        print("   hits per run: dispersion sum((N-lam)^2/lam)/runs = %.4f (Poisson 1; %d runs)" % (disp, len(runs)))
        # group clustering: (set, run, g, k) = all words but thi fixed; (set, run, g)
        gk = Counter((h["set"], h["run"], h["g"], h["k"]) for h in hits if h["fwd"] and h["cv"])
        rg = Counter((h["set"], h["run"], h["g"]) for h in hits if h["fwd"] and h["cv"])
        e_gk = e_rg = 0.0
        for s in range(8):
            m, n, d = LEDGER[s]
            nruns = sum(1 for r in runs if r[0] == s)
            ngroups = nruns * NOUT[arm][s] * 256 * n
            lam_g = NT[arm] * d * PS[s]
            e_gk += ngroups * lam_g ** 2 / 2
            nrg = nruns * NOUT[arm][s] * 256
            lam_rg = NT[arm] * n * d * PS[s]
            e_rg += nrg * lam_rg ** 2 / 2
        m_gk = sum(1 for v in gk.values() if v >= 2)
        m_rg = sum(1 for v in rg.values() if v >= 2)
        print("   groups (set,run,g,member) with >= 2 hits: %d (Poisson expectation %.3f); (set,run,g) with >= 2 hits: %d (expectation %.3f)"
              % (m_gk, e_gk, m_rg, e_rg))
        if NT[arm] > 1:
            th = Counter(h["thi"] for h in hits if h["fwd"] and h["cv"])
            exp = found / NT[arm]
            chi_t = sum((th.get(i, 0) - exp) ** 2 / exp for i in range(NT[arm]))
            print("   hits by thi: chi-square %.1f on %d df (uniform); thi = 0 hits %d; max t %d"
                  % (chi_t, NT[arm] - 1, th.get(0, 0), max(h["t"] for h in hits)))
    if "C" in res:
        fc, pc = res["C"]
        for arm in ("W32", "W256"):
            if arm in res:
                fw, pw = res[arm]
                r = (fw / pw) / (fc / pc)
                se = r * math.sqrt(1 / fw + 1 / fc)
                print("walk/control %s: %.4f +- %.4f (z = %+.2f)" % (arm, r, se, (r - 1) / se))
        allw = [res[a] for a in ("W32", "W256") if a in res]
        if allw:
            fw, pw = sum(a for a, b in allw), sum(b for a, b in allw)
            lb = chi2_quantile(0.023, 2 * fw) / 2 / pw
            print("walk arms pooled: FOUND %d PREDICTED %.2f ratio %.5f +- %.5f, 97.7%% lower bound %.5f"
                  % (fw, pw, fw / pw, math.sqrt(fw) / pw, lb))


if __name__ == "__main__":
    main()
