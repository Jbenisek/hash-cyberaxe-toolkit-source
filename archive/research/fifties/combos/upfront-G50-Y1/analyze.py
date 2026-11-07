"""upfront-G50-Y1 analysis: (a) real CK2 openings vs pilot, (b) solver side kept vs rejected, (c) pricing.

usage: python analyze.py MAIN_SEEDS [EXT_SEEDS]     e.g.  python analyze.py 101,202 303,404
Reads rows_s<seed>.json written by screen_ck2.py.  Pricing uses the pkgCJ ledger constants imported from
frontline_full (the same N formula, lines 134-143), the same pieces as work/ledger_split.py.
"""

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

import json
import os
import random
import re
import sys
from math import log2, sqrt, atanh, tanh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F  # noqa: E402

MAIN = [int(s) for s in sys.argv[1].split(",")]
EXT = [int(s) for s in sys.argv[2].split(",")] if len(sys.argv) > 2 else []


def load(seed):
    with open(os.path.join(HERE, "rows_s%d.json" % seed)) as fh:
        return json.load(fh)


def mean(xs):
    return sum(xs) / len(xs)


def sd(xs):
    m = mean(xs)
    return sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def corr(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    dx = sqrt(sum((a - mx) ** 2 for a in xs))
    dy = sqrt(sum((b - my) ** 2 for b in ys))
    return num / (dx * dy) if dx and dy else float("nan")


def corr_ci(r, n):
    z, se = atanh(r), 1 / sqrt(n - 3)
    return tanh(z - 1.96 * se), tanh(z + 1.96 * se)


def keep_sets(rows_by_seed, q):
    'Top-q by pilot within each seed (stable ascending sort, as yield4_seed.py ranks). Returns (kept, rejected).'
    kept, rej = [], []
    for rows in rows_by_seed:
        order = sorted(range(len(rows)), key=lambda i: rows[i]["pilot"])
        k = max(1, int(len(rows) * q))
        top = set(order[len(rows) - k:])
        kept += [rows[i] for i in range(len(rows)) if i in top]
        rej += [rows[i] for i in range(len(rows)) if i not in top]
    return kept, rej


# ---------------------------------------------------------------- ledger (pkgCJ, frontline_full lines 134-143)
K = F.RUN_CONTEXTS
P_STAR = 246621675 / 2 ** 29
ONCE_TOTAL = F.ONCE + 16 * 2 ** 20 + 2 ** 27 + 2 ** 34 + F.S_OLD + 430 * 2 ** 38
PIECES = dict(
    rep=(F.U_REP * (F.REP_BATCHES - 1) + F.U_REP_TAIL) * K,
    ctx=F.U_CONTEXT * (K + 1),
    open=F.U_OPEN * (F.A_BUDGET + 1),
    E=F.U_E * (F.E_BUDGET + 1),
    fill=F.U_FILL * (F.G_BUDGET + 1),
    pass_=F.U_PASS * (F.PASS_BUDGET + 1),
    solver=F.CREDIT,
)
assert sum(PIECES.values()) + ONCE_TOTAL == F.N == F.TEXT["N"]


def ledger(variant):
    'Per-context charge of each piece (budget / K) for variant "i" (today) or "ii" (XF1+XF2 opening row).'
    pc = {k: v / K for k, v in PIECES.items()}
    if variant == "ii":
        pc["open"] = 218 * 16384 * 0.409 * (F.A_BUDGET / K) / (16384 * P_STAR)   # 218 units, share 0.409
    return pc


STAT = dict(open="opened", E="hits", fill="fills", pass_="passes", solver="units")


def price(kept, allrows, variant, pilot_units, open_scale=None):
    'Screened N / unscreened N for keeping `kept` out of `allrows`, success held fixed through the pass count.'
    pc = ledger(variant)
    base = sum(pc.values())                                        # per context, unscreened (incl. ctx 600)
    q = len(kept) / len(allrows)
    R = mean([r["passes"] for r in kept]) / mean([r["passes"] for r in allrows])
    kc = pc["rep"]
    for piece, stat in STAT.items():
        ratio = mean([r[stat] for r in kept]) / mean([r[stat] for r in allrows])
        if piece == "open" and open_scale is not None:
            ratio = open_scale
        kc += pc[piece] * ratio
    screen = 600 + 1024 * pilot_units                              # per screened context (setup + pilot)
    per_success_new = (kc + screen / q) / R
    N_old = base * K + ONCE_TOTAL
    N_new = per_success_new * K + ONCE_TOTAL + 2 ** 20             # + code/pilot-list reserve
    fixed_share = (pc["rep"] + pc["ctx"] + pc["open"]) / base
    return dict(q=q, R=R, bits=log2(N_old / N_new), fixed_share=fixed_share,
                score_old=log2(N_old / 430), score_new=log2(N_new / 430))


def boot(kept_fn, rows_by_seed, fn, n=2000, seed=7):
    'Bootstrap over contexts within each seed; returns (mean, sd) of fn(kept, rej, all).'
    rs = random.Random(seed)
    vals = []
    for _ in range(n):
        res = [[rows[rs.randrange(len(rows))] for _ in rows] for rows in rows_by_seed]
        kept, rej = kept_fn(res)
        allr = [r for rows in res for r in rows]
        v = fn(kept, rej, allr)
        if v == v:
            vals.append(v)
    if len(vals) < 2:
        return float("nan"), float("nan")
    return mean(vals), sd(vals)


def section(seeds, label, do_baseline):
    data = [load(s) for s in seeds]
    rows_by_seed = [d["rows"] for d in data]
    allr = [r for rows in rows_by_seed for r in rows]
    n = len(allr)
    print("=" * 100)
    print(label, "seeds", seeds, "contexts", n)
    chk = {}
    for d in data:
        for k, v in d["checks"].items():
            chk[k] = chk.get(k, 0) + v
    print("checks (summed):", chk)

    if do_baseline:
        mm = 0
        for s, rows in zip(seeds, rows_by_seed):
            base = os.path.join(HERE, "baseline_run_s%d.txt" % s)
            got = {}
            for line in open(base):
                m = re.match(r"c (\d+) hits (\d+) prefix_reps \d+ passes (\d+) pilot (\d+)", line)
                if m:
                    got[int(m.group(1))] = tuple(int(m.group(i)) for i in (2, 3, 4))
            for r in rows:
                mm += got[r["c"]] != (r["hits"], r["spass"], r["pilot"])
        print("baseline columns (hits, sample passes, pilot) mismatches vs check/run_s*.txt:", mm, "of", n)

    # ------------------------------------------------------------------ (a)
    o = [r["opened"] for r in allr]
    pil = [r["pilot"] for r in allr]
    hit = [r["hits"] for r in allr]
    pas = [r["passes"] for r in allr]
    spa = [r["spass"] for r in allr]
    fil = [r["fills"] for r in allr]
    cal = [r["calls"] for r in allr]
    s7 = [r["s7_low7_reps"] for r in allr]
    print("--- (a) openings, real CK2 gate ---")
    print("opened mean %.2f sd %.2f CV %.5f min %d max %d   (charged A_B/K = %.2f, p* = %.6f; measured share %.6f)"
          % (mean(o), sd(o), sd(o) / mean(o), min(o), max(o), F.A_BUDGET / K, P_STAR, mean(o) / 16384))
    for name, xs in (("hits", hit), ("passes(full class)", pas), ("passes(2^15 sample)", spa), ("fills G", fil),
                     ("solver calls", cal), ("pilot", pil)):
        print("%-22s mean %10.2f sd %10.2f CV %.4f" % (name, mean(xs), sd(xs), sd(xs) / mean(xs)))
    print("CV(open)/CV(passes full) = %.5f ; CV(open)/CV(passes sample) = %.5f"
          % ((sd(o) / mean(o)) / (sd(pas) / mean(pas)), (sd(o) / mean(o)) / (sd(spa) / mean(spa))))
    for name, xs in (("pilot", pil), ("hits", hit), ("passes", pas), ("sample passes", spa)):
        r_ = corr(o, xs)
        print("corr(openings, %-14s) = %+.4f  95%% CI %s" % (name, r_, tuple(round(v, 3) for v in corr_ci(r_, n))))
    print("corr(pilot, passes) %.4f  corr(pilot, hits) %.4f  corr(hits, passes) %.4f  corr(fills, hits) %.4f"
          % (corr(pil, pas), corr(pil, hit), corr(hit, pas), corr(fil, hit)))
    print("8-bit proxy reps (omega mod 128 in S7, rep only): mean %.2f sd %.2f" % (mean(s7), sd(s7)))
    for q in (0.5, 0.25, 0.125):
        kept, rej = keep_sets(rows_by_seed, q)
        print("keep %.3f: opened kept/all %.4f  hits %.4f  passes %.4f  fills %.4f  calls %.4f  units %.4f"
              % (q, *(mean([r[s] for r in kept]) / mean([r[s] for r in allr])
                      for s in ("opened", "hits", "passes", "fills", "calls", "units"))))

    # ------------------------------------------------------------------ (b)
    print("--- (b) solver side per pass, pilot-kept half vs rejected half ---")
    kept, rej = keep_sets(rows_by_seed, 0.5)

    def per_pass(rs_, key):
        p = sum(r["passes"] for r in rs_)
        return sum(r[key] for r in rs_) / p if p else float("nan")

    for key in ("calls", "leaves", "roots", "units", "p_full"):
        a_, b_ = per_pass(kept, key), per_pass(rej, key)
        ratio = a_ / b_ if b_ else float("nan")
        m_, s_ = boot(lambda res: keep_sets(res, 0.5), rows_by_seed,
                      lambda k_, r_, al: (per_pass(k_, key) / per_pass(r_, key)) if per_pass(r_, key) else float("nan"),
                      n=1000)
        print("%-7s per pass: kept %.6g  rejected %.6g  ratio %.4f  boot se %.4f  (totals kept %d / rejected %d)"
              % (key, a_, b_, ratio, s_, sum(r[key] for r in kept), sum(r[key] for r in rej)))
    print("passes kept %d rejected %d ; calls kept %d rejected %d"
          % (sum(r["passes"] for r in kept), sum(r["passes"] for r in rej),
             sum(r["calls"] for r in kept), sum(r["calls"] for r in rej)))

    # ------------------------------------------------------------------ (c)
    print("--- (c) pricing (pkgCJ ledger; success held fixed by the exact full-class pass count) ---")
    for variant in ("i", "ii"):
        pc = ledger(variant)
        base = sum(pc.values())
        print("variant", variant, "per-context charge %.0f; shares:" % base,
              {k: round(v / base, 4) for k, v in pc.items()})
        for pu in (11, 25):
            for q in (0.5, 0.25, 0.125):
                kept, rej = keep_sets(rows_by_seed, q)
                r_ = price(kept, allr, variant, pu)
                r1 = price(kept, allr, variant, pu, open_scale=1.0)
                m_, s_ = boot(lambda res, q=q: keep_sets(res, q), rows_by_seed,
                              lambda k_, r__, al, variant=variant, pu=pu: price(k_, al, variant, pu)["bits"], n=500)
                print("  pilot %2d u/member keep %.3f: R %.4f fixed_share %.4f  gain %.4f bit (boot %.4f +- %.4f)"
                      "  [opening held flat: %.4f]  score %.4f -> %.4f"
                      % (pu, q, r_["R"], r_["fixed_share"], r_["bits"], m_, s_, r1["bits"],
                         r_["score_old"], r_["score_new"]))
    # ------------------------------------------------------------------ fixed pilot threshold (what a run would declare)
    print("--- fixed pilot thresholds t (keep iff pilot >= t): keep rate, R, gains, per-kept-context means ---")
    for t in (30, 40, 50, 58, 65, 75, 85):
        kept = [r for r in allr if r["pilot"] >= t]
        if len(kept) < 8:
            continue
        g = [price(kept, allr, v, pu)["bits"] for v in ("i", "ii") for pu in (11, 25)]
        km = {s: mean([r[s] for r in kept]) for s in ("hits", "passes", "opened", "fills", "calls", "units")}
        ks = {s: sd([r[s] for r in kept]) / sqrt(len(kept)) for s in km}
        print("t %3d q %.4f n %4d R %.4f gain(i) %.4f/%.4f gain(ii) %.4f/%.4f (pilot 11/25 u)"
              % (t, len(kept) / n, len(kept), km["passes"] / mean(pas), *g))
        print("        per kept context: " + "  ".join("%s %.1f+-%.1f" % (s, km[s], ks[s]) for s in km))
    print("unscreened means: " + "  ".join("%s %.1f" % (s, mean([r[s] for r in allr]))
                                          for s in ("hits", "passes", "opened", "fills", "calls", "units")))
    return allr


section(MAIN, "MAIN (the contexts of check/run_s101.txt and run_s202.txt)", True)
if EXT:
    section(EXT, "EXTENSION (independent seeds, out-of-sample)", False)
