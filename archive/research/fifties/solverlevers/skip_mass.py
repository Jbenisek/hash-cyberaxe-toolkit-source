#!/usr/bin/env python3
"""skip_mass.py (research only) - kept root mass m at kept share s for the Y9-score skip of the solver.
Reads scores_pc.txt (PC steps) and scores_rootsteps.txt (root steps); columns: Y9 hot scoreS scoreT cap nroots nrows.
hot = J1 count summed over the 14 hotspot taus (followup.py dp_y9, R = 0 targets); S = over the six solver rows;
T = over the rows the step searches. Threshold from the PC distribution (ties split pro rata).
Break-even (HOTSPOT_STATUS 5): m > 0.758 + 0.2415 s; s taken as the kept credit (cap-weighted) share."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    rows = []
    for ln in open(os.path.join(HERE, name)):
        p = ln.split()
        rows.append((int(p[1]), int(p[2]), int(p[3]), int(p[4]), int(p[5]), int(p[6])))
    return rows


def kept(scores_pc, weights_pc, s):
    """threshold t and tie fraction f so that the count share kept is s"""
    n = len(scores_pc)
    srt = sorted(scores_pc, reverse=True)
    k = s * n
    t = srt[min(int(k), n - 1)]
    above = sum(1 for x in scores_pc if x > t)
    eq = sum(1 for x in scores_pc if x == t)
    f = (k - above) / eq if eq else 0.0
    f = min(max(f, 0.0), 1.0)
    wt = sum(weights_pc)
    w_kept = sum(w for x, w in zip(scores_pc, weights_pc) if x > t) + f * sum(w for x, w in zip(scores_pc, weights_pc) if x == t)
    return t, f, w_kept / wt


def main():
    pc = load("scores_pc.txt")
    rs = load("scores_rootsteps.txt")
    out = {"pc_steps": len(pc), "root_steps": len(rs), "roots": sum(r[4] for r in rs)}
    for ci, name in ((0, "hot14"), (1, "S6"), (2, "T_rows")):
        sp = [r[ci] for r in pc]
        cap = [r[3] for r in pc]
        sr = [r[ci] for r in rs]
        nr = [r[4] for r in rs]
        res = {"pc_zero_share": sum(1 for x in sp if x == 0) / len(sp),
               "rootstep_zero_share": sum(1 for x in sr if x == 0) / len(sr)}
        for s in (1 / 4, 1 / 16, 1 / 64):
            t, f, s_cap = kept(sp, cap, s)
            m = (sum(1 for x in sr if x > t) + f * sum(1 for x in sr if x == t)) / len(sr)
            mr = (sum(n for x, n in zip(sr, nr) if x > t) + f * sum(n for x, n in zip(sr, nr) if x == t)) / sum(nr)
            se = math.sqrt(m * (1 - m) / len(sr))
            be = 0.758 + 0.2415 * s_cap
            res["1/%d" % round(1 / s)] = dict(threshold=t, tie_frac=round(f, 4), s_count=s, s_cap=round(s_cap, 5),
                                              m_rootsteps=round(m, 5), m_se=round(se, 5), m_roots=round(mr, 5),
                                              breakeven=round(be, 5), gain_x=round(m / s, 3),
                                              dbit=round(math.log2(be / m), 4) if m > 0 else None)
        out[name] = res
    # ratio of mean scores, root steps vs PC steps
    for ci, name in ((0, "hot14"), (1, "S6"), (2, "T_rows")):
        a = sum(r[ci] for r in rs) / len(rs)
        b = sum(r[ci] for r in pc) / len(pc)
        out[name]["mean_root_over_mean_pc"] = round(a / b, 4)
    json.dump(out, open(os.path.join(HERE, "skip_mass.json"), "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
