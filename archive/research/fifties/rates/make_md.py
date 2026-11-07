#!/usr/bin/env python3
"""Write RATES.md from rates_analysis.json (analyze.py output)."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = json.load(open(os.path.join(HERE, "rates_analysis.json")))
L = ["# Special frames vs ordinary outer steps: success-relevant partial rates (2026-10-09)", "",
     "Code: gen_tables.py (raw fq/fe automata of impl/outer.py -> tables.h), gen_co.py (impl/outer.py LINES -> co.h),",
     "rates.cu (AV11 exact uniform special-frame sampler, copied inv64/chart from fifties/av11/av11.cu, dflag = outer.py",
     "CTR_FLAGS = 3; ordinary = outer.py whole-class step), verify.py (GPU records == outer.scalar_outer + raw automata),",
     "solver_run.py (impl/solver.py on dumped passing steps), analyze.py, make_md.py. Raw counters: r_*.json; analysis:",
     "rates_analysis.json; solver: solver_counts.json. Modes: spcJ = base (b,h,z,f) and D2.a1 fixed, m fresh j = S4 per",
     "base; spcJA = m fresh (j, D2.a1) per base; fresh = step k = 0 of each base (one step per independent accepted base).",
     "b0 = D2.b1 uniform 32-bit (the outer.py law); bq = D2.b1 = q - W13, q in {0, 80000000} (ordinary restricted alike).",
     "Pre-check: T = X AND VMASK[nu] with C, B drawn uniform per step (their definition is not in the named files);",
     "with uniform C,B nu is uniform, so the pre-check pass is X != 0 times 1/4 and the step-dependent part is the r bit",
     "(Q bit 18 XOR e1 bit 2) reported as pass_and_rbit.", ""]
for k, info in A["runs"].items():
    s = info.get("sampler")
    L.append("- %s: mode %d bdom %d m %d, %d s, steps %.4e, bases %.4e, frame-check fails %d, inverse fails %d%s" % (
        k, info["mode"], info["bdom"], info["m"], info["seconds"], info["steps"], info["bases"],
        info["frame_check_fail"], info["inverse_check_fail"],
        (", rbar %.6f per attempt" % s["mean_R_per_attempt(rbar)"]) if s else ""))
L.append("")
for name, comp in A["comparisons"].items():
    L += ["## " + name, "", "| event | ordinary (se) | spc fresh (se) | ratio | z | spc j-reuse (cluster se) | ratio | z |",
          "|---|---|---|---|---|---|---|---|"]
    for e, d in comp.items():
        if e.startswith("per_outcome"):
            continue
        L.append("| %s | %.6e (%.1e) | %.6e (%.1e) | %.5f | %+.2f | %.6e (%.1e) | %.5f | %+.2f |" % (
            e, d["ord"][0], d["ord"][1], *d["spc_fresh"], *d["spc_jreuse"]))
    zb = comp["per_outcome_bits(ratio,z; naive se)"]
    L.append("")
    L.append("Per-outcome bits (all steps, iid se): " + ", ".join("%s r=%.4f z=%+.2f" % tuple(x) for x in zb))
    L.append("")
L += ["## Intra-base pair correlation rho (ordered distinct-step pairs within a base; se from per-base c(c-1))", "",
      "| run | E3 (1) step rho (se) | filter cond (2) step rho (se) | filter pass rho (se) | pre-check rho (se) | design effect (pass) |",
      "|---|---|---|---|---|---|"]
for k, info in A["runs"].items():
    ev = list(info["events"].values())
    f = lambda e: "%+.2e (%.1e)" % (ev[e]["pair"]["rho"], ev[e]["pair"]["se_rho"])
    L.append("| %s | %s | %s | %s | %s | %.4f |" % (k, f(0), f(1), f(2), f(3), ev[2]["jreuse"]["design_effect"]))
L.append("")
if "solver" in A:
    L += ["## impl/solver.py roots per passing step", "", "| pass dump | n | roots (no G7, no pre-check) | mean (se) | roots (G7 + pre-check, C,B uniform) | mean (se) |",
          "|---|---|---|---|---|---|"]
    for k, d in A["solver"].items():
        a, b = d["nog7_noprecheck"], d["g7_precheck_randomCB"]
        L.append("| %s | %d | %d | %.3e (%.1e) | %d | %.3e (%.1e) |" % (k, a["n"], a["roots"], a["mean"], a["se"], b["roots"], b["mean"], b["se"]))
    L.append("")
open(os.path.join(HERE, "RATES.md"), "w").write("\n".join(L) + "\n")
print("\n".join(L))
