"""Summaries of the h1meas runs (data/A, data/B): per run, family and width.
c_hat: the hazard multiplier (MLE of c in P(t > n) = exp(-c n^2 / 2N), from t^2 / 2N ~ Exp(c)), 95% interval (Wilson-Hilferty gamma).
Usage: python3 -B analyze.py [--json out.json]"""
import sys, os, json, glob, math
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
PLAN = {}
sys.path.insert(0, HERE)
import plan_w  # noqa: E402

for w in (24, 28, 32, 36, 40):
    h = w // 2
    p = plan_w.plan(1 << w, 1024 << (w - h), 1 << (h + 3), 1)
    PLAN[w] = p


def gamma_ci(K, s):
    """95% interval for c when s = sum of K Exp(c) variables: c = G / s, G ~ Gamma(K, 1); Wilson-Hilferty quantiles."""
    def q(z):
        return K * (1 - 1 / (9 * K) + z / (3 * math.sqrt(K))) ** 3
    return q(-1.959964) / s, q(1.959964) / s


def wilson(x, n):
    if n == 0:
        return (0, 1)
    z = 1.959964; p = x / n; d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return c - h, c + h


_LOADED = {}


def load(run):
    if run in _LOADED:
        return _LOADED[run]
    rows = defaultdict(list)
    for f in glob.glob(os.path.join(HERE, "data", run, "*.jsonl")):
        tag = os.path.basename(f).split("_w")[0]
        for line in open(f):
            line = line.strip()
            if line:
                d = json.loads(line)
                rows[(tag, d["w"])].append(d)
    _LOADED[run] = rows
    return rows


def summary(L, w):
    N = 1 << w
    K = len(L)
    cens = sum(d["cens"] for d in L)
    s = sum(d["t"] ** 2 / (2 * N) for d in L)
    c = K / s
    lo, hi = gamma_ci(K, s)
    out = {"K": K, "censored": cens, "c_hat": round(c, 4), "c_lo": round(lo, 4), "c_hi": round(hi, 4),
           "mean_t_over_sqrt_piN_2": round(sum(d["t"] for d in L) / K / math.sqrt(math.pi * N / 2), 4)}
    h = w // 2; T = 1024 if w >= 24 else (1 << (h - 4)); theta = T / (1 << h)
    ng = sum(d["ngap"] for d in L); sg = sum(d["sgap"] for d in L)
    out["dp_theta"] = theta
    out["dp_gaps"] = ng
    out["theta_x_mean_gap"] = round(theta * sg / ng, 4) if ng else None
    dl = [d["aprime"] - d["mu"] for d in L if d["aprime"] >= 0 and d["lambda"] > 20 / theta]
    out["theta_x_mean_detection_delay"] = round(theta * sum(dl) / len(dl), 4) if dl else None
    out["max_gap_x_theta"] = round(theta * max(d["maxgap"] for d in L), 2)
    if w in PLAN:
        p = PLAN[w]; n = p["n"]
        st = defaultdict(int)
        for d in L:
            st[d["status"]] += 1
        found = st["found"]
        out.update({"n": n, "S": p["S"], "gmax": p["gmax"], "mcap": p["mcap"], "lemma_bound": round(p["success_lower_bound"], 5),
                    "success": found, "success_frac": round(found / K, 4), "success_ci": [round(x, 4) for x in wilson(found, K)],
                    "pairs_verified": sum(d["pair_ok"] for d in L), "status": dict(st),
                    "frac_t_le_n": round(sum(d["t"] <= n for d in L) / K, 4),
                    "model_t_le_n": round(1 - math.exp(-n * (n + 1) / (2 * N)), 4),
                    "max_gap_vs_gmax": f'{max(d["maxgap"] for d in L)} / {p["gmax"]}'})
    return out


def main():
    res = {}
    for run in ("A", "B"):
        rows = load(run)
        for (tag, w), L in sorted(rows.items()):
            if tag == "ctrlfix":
                continue
            res[f"{run}/{tag}/w{w}"] = summary(L, w)
        # per-function success fractions: control fixed functions and the rho = 0 map
        for w in (24, 28):
            fr = []
            for f in glob.glob(os.path.join(HERE, "data", run, f"ctrlfix_w{w}_f*.jsonl")):
                L = [json.loads(l) for l in open(f) if l.strip()]
                fr.append(sum(d["status"] == "found" for d in L) / len(L))
            if fr:
                m = sum(fr) / len(fr); sd = math.sqrt(sum((x - m) ** 2 for x in fr) / (len(fr) - 1))
                res[f"{run}/ctrlfix/w{w}"] = {"functions": len(fr), "starts_each": 200, "mean_success": round(m, 4),
                                               "sd_success": round(sd, 4), "min": round(min(fr), 3), "max": round(max(fr), 3)}
    # pooled A+B, Orchard ladder, and the width trend of c_hat (weighted least squares on log c)
    pooled = {}
    for tag in ("orch", "ctrl", "orch0"):
        for w in (16, 20, 24, 28, 32, 36, 40):
            L = load("A").get((tag, w), []) + load("B").get((tag, w), [])
            if L:
                pooled[f"{tag}/w{w}"] = summary(L, w)
    res["pooled"] = pooled
    pts = [(int(k.split("w")[1]), v["c_hat"], v["K"]) for k, v in pooled.items() if k.startswith("orch/")]
    if len(pts) >= 3:
        sw = sum(K for _, _, K in pts); mx = sum(w * K for w, _, K in pts) / sw; my = sum(math.log(c) * K for _, c, K in pts) / sw
        sxx = sum(K * (w - mx) ** 2 for w, _, K in pts); sxy = sum(K * (w - mx) * (math.log(c) - my) for w, c, K in pts)
        b = sxy / sxx; se = 1 / math.sqrt(sxx)            # Var(log c_hat) ~ 1/K
        res["trend"] = {"slope_log_c_per_bit": round(b, 5), "se": round(se, 5), "extrapolated_c_at_w254": round(math.exp(my + b * (254 - mx)), 3),
                        "pooled_c_all_widths": round(math.exp(my), 4)}
    # all Orchard ladder trials, both runs: one pooled hazard multiplier; success pooled over the widths with the full search
    allL = [(w, d) for w in (16, 20, 24, 28, 32, 36, 40) for run in ("A", "B") for d in load(run).get(("orch", w), [])]
    K = len(allL); s = sum(d["t"] ** 2 / (2 * (1 << w)) for w, d in allL); lo, hi = gamma_ci(K, s)
    res["c_all"] = {"K": K, "c_hat": round(K / s, 4), "c_lo": round(lo, 4), "c_hi": round(hi, 4),
                    "dt_lo": round(0.5 * math.log2(1 / lo), 4) if lo < 1 else 0.0}
    sl = [(w, d) for w, d in allL if w in PLAN]
    fnd = sum(d["status"] == "found" for _, d in sl)
    res["succ_all"] = {"K": len(sl), "found": fnd, "frac": round(fnd / len(sl), 4), "ci": [round(x, 4) for x in wilson(fnd, len(sl))],
                       "bound_mean": round(sum(PLAN[w]["success_lower_bound"] for w, _ in sl) / len(sl), 5)}
    res["max_evals"] = max(d["t"] for _, d in allL)
    mins = 0
    for run in ("A", "B"):
        try:
            mins += (int(open(os.path.join(HERE, "data", run, "end")).read()) - int(open(os.path.join(HERE, "data", run, "start")).read())) / 60
        except OSError:
            pass
    res["minutes"] = round(mins)
    pf = os.path.join(HERE, "data", "pairs.json")
    res["pairs"] = json.load(open(pf)) if os.path.exists(pf) else {"pairs": 0, "verified_by_organizer_digest": 0}
    res["summary_c"] = f'pooled hazard multiplier {res["c_all"]["c_hat"]:.3f}, 95% interval [{lo:.3f}, {hi:.3f}] over {K} walks; 1 is the random-function value'
    res["summary_s"] = (f'{fnd} successes in {len(sl)} runs of the search at widths 24 to 40, {fnd / len(sl):.3f} against the lemma bound '
                        f'{res["succ_all"]["bound_mean"]:.3f}')
    js = json.dumps(res, indent=1)
    if "--json" in sys.argv:
        open(sys.argv[sys.argv.index("--json") + 1], "w").write(js)
    print(js)


if __name__ == "__main__":
    main()
