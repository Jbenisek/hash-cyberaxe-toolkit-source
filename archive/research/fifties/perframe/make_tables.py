#!/usr/bin/env python3
"""make_tables.py - markdown tables from main_out.json (descriptive formatting only). python3 -B make_tables.py <in> <out.md>"""
import json
import math
import sys


def f(x, se=None, d=4):
    if x is None:
        return "-"
    s = ("%." + str(d) + "f") % x if abs(x) < 1e5 else "%.3g" % x
    if se is not None:
        s += " ± " + (("%." + str(d) + "f") % se if abs(se) < 1e5 else "%.2g" % se)
    return s


def main():
    r = json.load(open(sys.argv[1]))
    L = ["G = %d outer steps per frame, k = %d c1 per frame; ALLOWED = 2^%.3f; E[W] per frame 2^%.2f" % (
        r["G"], r["k"], r["allowed_factor_log2"], r["EW_frame_log2"]), ""]
    L.append("| event | arm | frames | N | log2 p | v | R | Rw (within step) | Rx_same | Rx_diff | Rx (frame) |"
             " pairs within / same-c1 / diff-c1 (expected) |")
    L.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|")
    for ev in ("T2", "P", "RA", "E1a", "R16", "R24", "E1L", "E3P"):
        for arm in ("arm0", "arm1"):
            a = r[arm][ev]
            if "p" not in a:
                L.append("| %s | %s | %d | %d | - | - | - | - | - | - | - | - |" % (ev, r[arm]["label"], r[arm]["frames"], a["N"]))
                continue
            trial = "Rx" in a
            pairs = "-"
            if trial:
                pairs = "%d (%.4g) / %d (%.4g) / %d (%.4g)" % (a["pairs_within"], a["pairs_within_expected"],
                                                            a["pairs_same_c1"], a["pairs_same_c1_expected"],
                                                            a["pairs_diff_c1"], a["pairs_diff_c1_expected"])
            else:
                pairs = "%d (%.6g)" % (a["pairs"], a["pairs_expected"])
            L.append("| %s | %s | %d | %d | %.3f | %s | %s | %s | %s | %s | %s | %s |" % (
                ev, r[arm]["label"], r[arm]["frames"], a["N"], a["log2_p"], f(a["v"], a["v_se"]), f(a["R"], a["R_se"]),
                f(a.get("Rw"), a.get("Rw_se"), 3) if trial else "-",
                f(a.get("Rx_same"), a.get("Rx_same_se"), 3) if trial else "-",
                f(a.get("Rx_diff"), a.get("Rx_diff_se")) if trial else "-",
                f(a.get("Rx"), a.get("Rx_se")) if trial else "-", pairs))
    L += ["", "| event | ctx - ctrl: R | Rx | Rx_same | Rx_diff | Rw | v |", "|---|---:|---:|---:|---:|---:|---:|"]
    for ev in ("T2", "P", "RA", "E1a", "R16", "R24", "E1L", "E3P"):
        d = r["ctx_minus_ctrl"][ev]
        L.append("| %s | %s | %s | %s | %s | %s | %s |" % (ev, *[f(d.get(q), d.get(q + "_se"), 4) if q in d else "-"
                                                               for q in ("R", "Rx", "Rx_same", "Rx_diff", "Rw", "v")]))
    L += ["", "| event | gen | ctx Rx | ctrl Rx | ctx Rx_same | ctrl Rx_same |", "|---|---|---:|---:|---:|---:|"]
    for ev in ("E1a", "R24", "E1L", "E3P", "RA"):
        for g in (1, 2):
            a, b = r["arm0_G%d" % g][ev], r["arm1_G%d" % g][ev]
            L.append("| %s | G%d | %s | %s | %s | %s |" % (ev, g, f(a.get("Rx"), a.get("Rx_se")), f(b.get("Rx"), b.get("Rx_se")),
                                                          f(a.get("Rx_same"), a.get("Rx_same_se"), 3),
                                                          f(b.get("Rx_same"), b.get("Rx_same_se"), 3)))
    L += ["", "| primary (ctx) | Rx ± SE | U_diff (method) | U_same (method) | U | log2 U | margin to 2^%.3f | BOUNDED-2 | BOUNDED-16 | NO-EXCESS |"
          % r["allowed_factor_log2"], "|---|---:|---|---|---:|---:|---:|---|---|---|"]
    for ev, p in r["primary"].items():
        L.append("| %s | %s | %.4f (%s) | %.4g (%s) | %.4f | %.3f | %.2f bits | %s | %s | %s |" % (
            ev, f(p["Rx"], p["Rx_se"]), p["U_diff"], p["U_diff_method"], p["U_same"], p["U_same_method"], p["U"],
            p["log2_U"], p["margin_to_allowed_log2"], p["BOUNDED_2"], p["BOUNDED_16"], p["NO_EXCESS"]))
    L += ["", "VERDICT: " + r["verdict"], "", "checks: " + json.dumps({q: v for q, v in r["checks"].items() if q != "file_sha256"})]
    if "prereg_check" in r:
        pc = r["prereg_check"]
        L.append("prereg: sha256 %s matches %s; listed files all match %s; run_out carries it %s" % (
            pc["prereg_sha256"][:16], pc["prereg_matches"], pc["listed_all_match"], pc.get("run_out_prereg_sha256_matches")))
    for ev in ("E1L", "E3P", "R24", "RA", "P"):
        for arm in ("arm0", "arm1"):
            a = r[arm][ev]
            if "rho_x_full" in a:
                L.append("%s %s: rho_x_full %.4g, rho_w_full %.4g, mean/nominal %s" % (
                    ev, r[arm]["label"], a["rho_x_full"], a["rho_w_full"],
                    f(a.get("mean_over_nominal"), a.get("mean_over_nominal_se"))))
            elif "mean_over_nominal" in a:
                L.append("%s %s: mean/nominal %s" % (ev, r[arm]["label"], f(a["mean_over_nominal"], a["mean_over_nominal_se"])))
    open(sys.argv[2], "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
