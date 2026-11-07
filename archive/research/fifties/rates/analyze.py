#!/usr/bin/env python3
"""Rates, standard errors, special/ordinary ratios and z, intra-base pair correlations from rates.cu counters.
Usage: analyze.py out.json ord.json spc1.json [spc2.json ...] [--solver solver.json]"""
import json, math, os, sys

C_STEPS, C_BASES, C_ATT, C_SUMR, C_INVFAIL, C_FRAMEFAIL = range(6)
C_BITQ, C_BITE, C_FBITQ, C_FBITE = 6, 13, 20, 27
NE = 7
C_S1 = 34; C_S2 = C_S1 + NE; C_B2 = C_S2 + NE; C_B4 = C_B2 + NE; C_F1 = C_B4 + NE; C_F2 = C_F1 + NE
EV = ["E3_cond1_step (fq&S!=0)", "filter_cond2_step (fe&S!=0)", "filter_pass (fq&fe&S!=0)",
      "precheck_pass (X&VMASK[nu]!=0, C,B uniform)", "pass_and_rbit (Q18^e1_2=1)",
      "E3_cond1_per_outcome (mean of 7 fq bits)", "filter_cond2_per_outcome (mean of 7 fe bits)"]
BINARY = [True, True, True, True, True, False, False]
SCALE = [1, 1, 1, 1, 1, 7, 7]

def ev_stats(c, m):
    B, n = c[C_BASES], c[C_STEPS]
    assert n == B * m
    out = []
    for e in range(NE):
        s = SCALE[e]
        # fresh: step k=0 of each base (independent bases)
        f1, f2 = c[C_F1 + e], c[C_F2 + e]
        mu_f = f1 / B
        se_f = math.sqrt(max(f2 / B - mu_f ** 2, 0) / B)
        # all steps (j-reuse), cluster-robust se from base totals
        S1, S2, B2, B4 = c[C_S1 + e], c[C_S2 + e], c[C_B2 + e], c[C_B4 + e]
        mu = S1 / n
        var_c = (B2 - S1 * S1 / B) / (B - 1)
        se_cl = math.sqrt(var_c / B) / m
        var_x = S2 / n - mu ** 2
        se_naive = math.sqrt(var_x / n)
        d = {"fresh": {"n": B, "rate": mu_f / s, "se": se_f / s},
             "jreuse": {"n": n, "bases": B, "m": m, "rate": mu / s, "se_cluster": se_cl / s, "se_naive_iid": se_naive / s,
                        "design_effect": (se_cl / se_naive) ** 2 if se_naive else None}}
        if m > 1:
            cross = (B2 - S2) / (B * m * (m - 1))           # E[x x'] over ordered pairs of distinct steps in a base
            rho = (cross - mu ** 2) / var_x if var_x else None
            pair = {"E_xx'": cross, "mu^2": mu ** 2, "rho": rho}
            if BINARY[e]:
                mean_pp = (B2 - S1) / B                      # E[c(c-1)]
                var_pp = B4 / B - mean_pp ** 2
                se_cross = math.sqrt(max(var_pp, 0) / B) / (m * (m - 1))
                pair["se_rho"] = se_cross / var_x if var_x else None
                pair["z_rho"] = rho / pair["se_rho"] if pair["se_rho"] else None
                pair["P(both|one) / p"] = cross / mu ** 2 if mu else None
            d["pair"] = pair
        out.append(d)
    return out

def cmp(a, sa, b, sb):
    return {"ratio": a / b if b else None, "z": (a - b) / math.hypot(sa, sb) if (sa or sb) else None}

def bit_rates(c, base, nn):
    return [(c[base + j] / nn, math.sqrt(c[base + j] / nn * (1 - c[base + j] / nn) / nn)) for j in range(7)]

def run(paths, solver_path=None):
    runs = {os.path.basename(p): json.load(open(p)) for p in paths}
    ordname = os.path.basename(paths[0])
    res = {"runs": {}}
    for name, r in runs.items():
        c, m = r["cnt"], r["m"]
        st = ev_stats(c, m)
        info = {"mode": r["mode"], "bdom": r["bdom"], "m": m, "seconds": r["seconds"], "steps": c[C_STEPS],
                "bases": c[C_BASES], "events": dict(zip(EV, st)),
                "frame_check_fail": c[C_FRAMEFAIL], "inverse_check_fail": c[C_INVFAIL]}
        if r["mode"]:
            info["sampler"] = {"attempts": c[C_ATT], "attempts_per_accepted_base": c[C_ATT] / max(1, c[C_BASES]),
                               "mean_R_per_attempt(rbar)": c[C_SUMR] / max(1, c[C_ATT])}
        info["bits_fq_all"] = bit_rates(c, C_BITQ, c[C_STEPS])
        info["bits_fe_all"] = bit_rates(c, C_BITE, c[C_STEPS])
        res["runs"][name] = info
    o = res["runs"][ordname]
    res["comparisons"] = {}
    for name, info in res["runs"].items():
        if name == ordname:
            continue
        comp = {}
        for e in EV:
            od = o["events"][e]["jreuse"]          # ordinary: all steps independent
            ov, ose = od["rate"], od["se_cluster"]
            sf = info["events"][e]["fresh"]
            sj = info["events"][e]["jreuse"]
            comp[e] = {"ord": [ov, ose],
                       "spc_fresh": [sf["rate"], sf["se"]] + list(cmp(sf["rate"], sf["se"], ov, ose).values()),
                       "spc_jreuse": [sj["rate"], sj["se_cluster"]] + list(cmp(sj["rate"], sj["se_cluster"], ov, ose).values())}
        zb = []
        for key in ("bits_fq_all", "bits_fe_all"):
            for j in range(7):
                a, sa = info[key][j]; b, sb = o[key][j]
                zb.append((key[5:7] + str(j + 1), a / b, (a - b) / math.hypot(sa, sb)))
        comp["per_outcome_bits(ratio,z; naive se)"] = zb
        res["comparisons"][name + " vs " + ordname] = comp
    if solver_path and os.path.exists(solver_path):
        res["solver"] = json.load(open(solver_path))
    return res

if __name__ == "__main__":
    args = sys.argv[1:]
    sp = None
    if "--solver" in args:
        i = args.index("--solver"); sp = args[i + 1]; del args[i:i + 2]
    out = run(args[1:], sp)
    with open(args[0], "w") as f:
        json.dump(out, f, indent=1)
    for k, comp in out["comparisons"].items():
        print("==", k)
        for e, d in comp.items():
            if e.startswith("per_outcome"):
                print("  per-outcome bits max|z| %.2f" % max(abs(x[2]) for x in d))
                continue
            print("  %-46s ord %.6e(%.1e) fresh %.6e(%.1e) r=%.5f z=%+.2f | jreuse %.6e(%.1e) r=%.5f z=%+.2f" % (
                e, d["ord"][0], d["ord"][1], *d["spc_fresh"], *d["spc_jreuse"]))
    for k, info in out["runs"].items():
        pr = {e[:22]: (round(v["pair"]["rho"], 6), round(v["pair"].get("se_rho") or 0, 6)) for e, v in info["events"].items() if "pair" in v}
        print(k, "steps %.3e bases %.3e" % (info["steps"], info["bases"]), info.get("sampler"), "fails", info["frame_check_fail"], info["inverse_check_fail"])
        print("   pair rho(se):", pr)
