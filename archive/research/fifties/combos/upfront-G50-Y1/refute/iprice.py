"""Own pricing of the pilot screen from the independent rows (irows_s*.json), pkgCJ ledger rebuilt from scratch.

usage: python iprice.py SEED_A SEED_B
Threshold rule preregistered here: t = median pilot of seed A, applied out-of-sample to seed B (and vice versa).
The solver piece is scaled by the calls ratio times the ratio of mean CT[T] per call (proxy; F.solve not run).
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
import sys
from math import log2, sqrt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F  # noqa: E402

SA, SB = int(sys.argv[1]), int(sys.argv[2])


def load(s):
    with open(os.path.join(HERE, "irows_s%d.json" % s)) as fh:
        return json.load(fh)


DA, DB = load(SA), load(SB)
print("checks", SA, DA["checks"], "| ", SB, DB["checks"])
RA, RB = DA["rows"], DB["rows"]

# ---------------- ledger, rebuilt from F's constants (not from analyze.py) ----------------
K = F.RUN_CONTEXTS
assert K == F.TEXT["RUN_CONTEXTS"]
per = {
    "rep": 74 * 2340 + 56,
    "ctx": 600 * (K + 1) / K,
    "open": 368 * (F.A_BUDGET + 1) / K,
    "E": 10 * (F.E_BUDGET + 1) / K,
    "fill": 60 * (F.G_BUDGET + 1) / K,
    "pass": 468 * (F.PASS_BUDGET + 1) / K,
    "solver": F.CREDIT / K,
}
once = F.N - (74 * 2340 + 56) * K - 600 * (K + 1) - 368 * (F.A_BUDGET + 1) - 10 * (F.E_BUDGET + 1) \
    - 60 * (F.G_BUDGET + 1) - 468 * (F.PASS_BUDGET + 1) - F.CREDIT
base = sum(per.values())
N_old = base * K + once
print("N check", F.N, "score", round(log2(F.N / 430), 4), "per-context", round(base), "once share",
      round(once / F.N, 5))
print("shares", {k: round(v / base, 4) for k, v in per.items()})
print("per-context implied: openings %.1f  E %.1f  fills %.1f  passes %.2f  credit %.0f"
      % (per["open"] / 368, per["E"] / 10, per["fill"] / 60, per["pass"] / 468, per["solver"]))
CT = F.CT


def mean(xs):
    return sum(xs) / len(xs)


def sd(xs):
    m = mean(xs)
    return sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def corr(xs, ys):
    mx, my = mean(xs), mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    return num / sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))


def ctmean(rows):
    n = s = 0
    for r in rows:
        for T, c in enumerate(r["Thist"]):
            if c:
                n += c
                s += c * CT[T]
    return s / n


def price(kept, allr, pu, open_flat=False):
    q = len(kept) / len(allr)
    rat = lambda k: mean([r[k] for r in kept]) / mean([r[k] for r in allr])
    R = rat("passes_open")
    kc = per["rep"] + per["ctx"] + per["open"] * (1.0 if open_flat else rat("opened")) + per["E"] * rat("e_lanes") \
        + per["fill"] * rat("fills") + per["pass"] * R + per["solver"] * rat("calls_open") * ctmean(kept) / ctmean(allr)
    screen = 600 + 1024 * pu
    N_new = (kc + screen / q) / R * K + once + 2 ** 20
    return dict(q=q, R=R, gain=log2(N_old / N_new), new=log2(N_new / 430))


def report(name, rows):
    o = [r["opened"] for r in rows]
    pil = [r["pilot"] for r in rows]
    pas = [r["passes_open"] for r in rows]
    print("---", name, "n", len(rows))
    print("opened mean %.1f sd %.1f CV %.4f | passes mean %.1f CV %.4f | CV ratio %.3f"
          % (mean(o), sd(o), sd(o) / mean(o), mean(pas), sd(pas) / mean(pas), (sd(o) / mean(o)) / (sd(pas) / mean(pas))))
    print("corr(opened, pilot) %+.4f  corr(opened, passes) %+.4f  corr(pilot, passes) %.4f"
          % (corr(o, pil), corr(o, pas), corr(pil, pas)))
    print("closed-cluster hits (must be 0):", sum(r["closed_hits"] for r in rows),
          " passes outside opened (must be 0):", sum(r["passes"] - r["passes_open"] for r in rows))
    print("mean fills %.1f (H_G_cluster 12466)  mean e_lanes %.1f  mean calls %.2f  opened share %.5f"
          % (mean([r["fills"] for r in rows]), mean([r["e_lanes"] for r in rows]),
             mean([r["calls_open"] for r in rows]), mean(o) / 16384))


def top_half(rows):
    order = sorted(range(len(rows)), key=lambda i: rows[i]["pilot"])
    k = len(rows) // 2
    top = set(order[len(rows) - k:])
    return [rows[i] for i in top], [rows[i] for i in range(len(rows)) if i not in top]


allr = RA + RB
report("seed %d" % SA, RA)
report("seed %d" % SB, RB)
report("pooled", allr)

print("=== keep top half by pilot within each seed (rank rule, as the claim) ===")
kA, rA = top_half(RA)
kB, rB = top_half(RB)
kept, rej = kA + kB, rA + rB
for pu in (11, 25, 40):
    p = price(kept, allr, pu)
    pf = price(kept, allr, pu, True)
    print("u %2d: q %.3f R %.4f gain %.4f bit (open flat %.4f)  63.6026 -> %.4f" % (pu, p["q"], p["R"], p["gain"],
                                                                                   pf["gain"], p["new"]))
for k in ("opened", "e_lanes", "fills", "passes_open", "calls_open"):
    print("  kept/all %-12s %.4f" % (k, mean([r[k] for r in kept]) / mean([r[k] for r in allr])))

print("=== preregistered threshold: t = median pilot of one seed, applied to the other seed ===")
for (S1, Rtr), (S2, Rte) in (((SA, RA), (SB, RB)), ((SB, RB), (SA, RA))):
    t = sorted(r["pilot"] for r in Rtr)[len(Rtr) // 2]
    kept_te = [r for r in Rte if r["pilot"] >= t]
    for pu in (11, 25):
        p = price(kept_te, Rte, pu)
        print("train %d t=%d -> test %d: q %.3f R %.4f gain(u=%d) %.4f" % (S1, t, S2, p["q"], p["R"], pu, p["gain"]))

# bootstrap se of the rank-rule gain
rs = random.Random(11)
gs = []
for _ in range(300):
    a = [RA[rs.randrange(len(RA))] for _ in RA]
    b = [RB[rs.randrange(len(RB))] for _ in RB]
    ka, _ = top_half(a)
    kb, _ = top_half(b)
    gs.append(price(ka + kb, a + b, 11)["gain"])
print("bootstrap gain(u=11) mean %.4f se %.4f" % (mean(gs), sd(gs)))

# H_S3 probe: T-mix of calls, kept vs rejected
print("=== T mix per call (kept vs rejected half) ===")


def tau_share(rows):
    n, b = 0, [0] * 7
    for r in rows:
        for T, c in enumerate(r["Thist"]):
            if c:
                n += c
                for j in range(7):
                    b[j] += c * (T >> j & 1)
    return n, [x / n for x in b]


nk, bk = tau_share(kept)
nr, br = tau_share(rej)
print("calls kept %d rejected %d" % (nk, nr))
for j in range(7):
    if F.S_MASK >> j & 1:
        se = sqrt(bk[j] * (1 - bk[j]) / nk + br[j] * (1 - br[j]) / nr)
        print("  tau %d (%08x): kept %.4f rejected %.4f  diff %+.4f (%.1f se)" % (j, F.TAUS[j], bk[j], br[j],
                                                                            bk[j] - br[j], (bk[j] - br[j]) / se))
print("mean CT[T] per call kept %.1f rejected %.1f ratio %.4f" % (ctmean(kept), ctmean(rej), ctmean(kept) / ctmean(rej)))
pk = sum(r["calls_open"] for r in kept) / sum(r["passes_open"] for r in kept)
pr = sum(r["calls_open"] for r in rej) / sum(r["passes_open"] for r in rej)
print("calls per pass kept %.5f rejected %.5f ratio %.4f" % (pk, pr, pk / pr))
