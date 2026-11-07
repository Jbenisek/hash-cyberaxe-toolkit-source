"""Parts (2),(3): turn meas_<tag>_q*_d*.json counts into p_land, R law, charged costs."""
import json, glob, math, os, sys
here = os.path.dirname(os.path.abspath(__file__))
TAG = sys.argv[1] if len(sys.argv) > 1 else "main"
BUDGET = 2221.10846
rows, out = [], {}

def stats(hist):
    N = sum(hist); m1 = sum(r * c for r, c in enumerate(hist)) / N
    m2 = sum(r * r * c for r, c in enumerate(hist)) / N
    p0 = hist[0] / N; mx = max(r for r, c in enumerate(hist) if c)
    return N, m1, m2, p0, mx

def costs(hist):
    N, m1, m2, p0, mx = stats(hist)
    att = 2048 + 64 + 256 * m1                       # mean charged attempt (11.3 inverse + 64 select)
    return {"mean_attempt_units": att,
            "uniform_sampler_units_per_base": 64 * att / m1,      # 11.3/11.4 exact sampler (accept R/64)
            "sol_bound_formula": 64 * (2048 + 64) / m1 + 64 * 256,
            "attempts_per_base_uniform": 64 / m1,
            "any_root_units_per_base": att / (1 - p0),            # keep one root if R>0 (not uniform)
            "all_roots_units_per_frame": att / m1}                # every root used (not uniform)

files = sorted(glob.glob(os.path.join(here, f"meas_{TAG}_q*_d*.json")))
agg = None
for fn in files:
    d = json.load(open(fn)); n = d["n"]
    key = f"q{d['q']}_d{d['dflag']}"
    r = {"q": d["q"], "dflag": d["dflag"], "n": n, "seconds": d["seconds"]}
    for cl, rho, hk, fk in (("C13", 13, "hist_R_C13", "fwd_hits_C13"), ("C15", 15, "hist_R_C15", "fwd_hits_C15")):
        hits = d[fk]; p = hits / n; se = math.sqrt(p * (1 - p) / n)
        N, m1, m2, p0, mx = stats(d[hk]); sdm = math.sqrt((m2 - m1 * m1) / N)
        r[cl] = {"p_land_direct": p, "p_land_direct_se": se, "log2_p_land": math.log2(p),
                 "rbar_inverse": m1, "rbar_se": sdm, "p_land_via_rbar": m1 * 2 ** -rho,
                 "bound_2^(6-rho)": 2 ** (6 - rho), "p_land/bound": p / 2 ** (6 - rho),
                 "p_land*2^rho": p * 2 ** rho,
                 "inverse_samples": N, "P(R=0)": p0, "E[R^2]": m2, "maxR": mx,
                 "R_dist": [c / N for c in d[hk]][:mx + 1], "R_counts": d[hk][:mx + 1],
                 "costs": costs(d[hk])}
        r[cl]["direct_chart_tries_per_landing"] = 1 / p
        r[cl]["direct_chart_units_lower_bound_u1"] = 1 / p
    out[key] = r
    if d["dflag"] == 11:
        if agg is None: agg = {k: [0] * 65 for k in ("hist_R_C13", "hist_R_C15")}; agg.update(n=0, f13=0, f15=0)
        for k in ("hist_R_C13", "hist_R_C15"): agg[k] = [a + b for a, b in zip(agg[k], d[k])]
        agg["n"] += n; agg["f13"] += d["fwd_hits_C13"]; agg["f15"] += d["fwd_hits_C15"]

if agg:
    comb = {"n": agg["n"]}
    for cl, rho, hk, fk in (("C13", 13, "hist_R_C13", "f13"), ("C15", 15, "hist_R_C15", "f15")):
        p = agg[fk] / agg["n"]; c = costs(agg[hk]); N, m1, m2, p0, mx = stats(agg[hk])
        base = c["uniform_sampler_units_per_base"]
        comb[cl] = {"p_land": p, "se": math.sqrt(p / agg["n"]), "log2": math.log2(p), "rbar": m1,
                    "p_land/bound": p / 2 ** (6 - rho), "P(R=0)": p0, "maxR": mx, "costs": c,
                    "j_reuse_landing_units_per_iteration": base / 2 ** 32,
                    "direct_tries_units_u1_per_iteration_no_reuse": 1 / p,
                    "budget": BUDGET}
    out["combined_two_q_dflag11"] = comb
json.dump(out, open(os.path.join(here, f"results_{TAG}.json"), "w"), indent=1)

L = [f"AV11 measurement ({TAG}); n = samples (h,z,f) direct AND (z,f,y in C13) inverse, per q",
     "q        dfl  n          class p_land(direct)  log2    rbar     p_land/2^(6-rho)  P(R=0)  maxR  units/base(uniform)"]
for k, r in out.items():
    if not k.startswith("q"): continue
    for cl in ("C13", "C15"):
        x = r[cl]
        L.append(f"{r['q']} {r['dflag']:>3} {r['n']:.3e} {cl}   {x['p_land_direct']:.6e}   {x['log2_p_land']:.4f} "
                 f"{x['rbar_inverse']:.5f}  {x['p_land/bound']:.5f}           {x['P(R=0)']:.4f}  {x['maxR']:>3}   "
                 f"{x['costs']['uniform_sampler_units_per_base']:.0f}")
if agg:
    c = out["combined_two_q_dflag11"]["C13"]
    L.append(f"combined dflag11 C13: p_land={c['p_land']:.6e} (2^{c['log2']:.4f}), rbar={c['rbar']:.5f}, "
             f"uniform sampler {c['costs']['uniform_sampler_units_per_base']:.0f} u/base "
             f"({c['costs']['attempts_per_base_uniform']:.1f} attempts), any-root {c['costs']['any_root_units_per_base']:.0f}, "
             f"all-roots {c['costs']['all_roots_units_per_frame']:.0f} u/frame; j-reuse landing share "
             f"{c['j_reuse_landing_units_per_iteration']:.3e} u/iter vs budget {BUDGET}")
open(os.path.join(here, f"results_{TAG}_table.txt"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
