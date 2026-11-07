#!/usr/bin/env python3
"""analyse_pf.py - statistics of the perframe run (frozen in PREREG.txt before the main run). Standard library only.

  python3 -B analyse_pf.py <run_dir> <out.json> [--prereg]

Unit: the frame. Per arm (0 ctx, 1 ctrl), pooled over G1 and G2 and per generator, for every event:
  step events  T2, P:                         m = G outer steps per frame
  trial events E1a E1L E3P R16 R24 RA:        m = G k trials per frame (t = 0 trials excluded from the counts; m
                                              nominal), SW = within-step ordered pairs, SC = same-c1 cross-step pairs
  N, mean, p = N/(C m), v = 1 + (var - m p (1-p))/mean^2, F = sum n(n-1)/N, E0 = (m-1) p, R = F/E0
  Rw      = (SW/N) / ((k-1) p)                              pairs in one outer step
  Rx_same = (SC/N) / ((G-1) p)                              same c1, different g
  Rx_diff = ((SF-SW-SC)/N) / ((G-1)(k-1) p)                 different c1, different g
  Rx      = 2^-21 Rx_same + (1 - 2^-21) Rx_diff             cross-step factor of the whole frame (2^32 g x 2^21 c1)
  Rx_pool = ((SF-SW)/N) / ((G-1) k p)                       the sampled cross-step pairs unweighted (descriptive)
  rho_x_full = Rx (2^32-1) 2^21 p, rho_w_full = Rw (2^21-1) p   (the frame's factorial ratio for that event)
  SE: delete-one-group jackknife, 128 contiguous groups of the arm's frames (G1 blocks ascending, then G2).
PRIMARY (ctx arm, E1L, E3P, R24): U = (1-2^-21) U_diff + 2^-21 U_same, U_s = Rx_s + 3 SE(Rx_s) when the stratum has
  >= 30 pairs, else its exact 99.865 % Poisson upper limit over its no-clustering expectation. BOUNDED-2 iff U <= 2,
  BOUNDED-16 iff U <= 16; margin = ALLOWED - log2 U with ALLOWED = log2(0.0065 / ((2^32-1) 2^21 p_good)),
  p_good = (5/7) 1033 2^27 / 2^128 (H1prime-rate of 9a9f3b7b). NO-EXCESS iff |Rx(ctx) - Rx(ctrl)| <= 3 SE.
  VERDICT: SUPPORTED iff every primary U <= 16; NOT SUPPORTED iff some primary U > 2^ALLOWED; else WEAK.
"""
import glob
import hashlib
import json
import math
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NREC = 32
NG = 128
EVENTS = ["T2", "P", "E1a", "E1L", "E3P", "R16", "R24", "RA"]
TRIAL = {"E1a": 0, "E1L": 1, "E3P": 2, "R16": 3, "R24": 4, "RA": 5}
STEP = {"T2": 0, "P": 1}
W21 = 2.0 ** -21
P_GOOD = (5 / 7) * 1033 * 2 ** 27 / 2 ** 128
ALLOWED_LOG2 = math.log2(0.0065) - math.log2((2 ** 32 - 1) * 2 ** 21 * P_GOOD)
CTR_SHARE = 20504986129465344
NOMINAL = {"P": CTR_SHARE / 2 ** 64, "E1L": 53 * 2 ** -38}


def read(path):
    b = open(path, "rb").read()
    hdr = struct.unpack("<8I", b[:32])
    assert hdr[0] == 0x46524650 and hdr[7] == NREC
    arm, gen, b0, nb, G, k = hdr[1:7]
    assert len(b) == 32 + 8 * NREC * nb
    rec = struct.unpack("<%dQ" % (NREC * nb), b[32:])
    return dict(arm=arm, gen=gen, b0=b0, nb=nb, G=G, k=k, rows=[rec[NREC * i:NREC * i + NREC] for i in range(nb)],
                sha=hashlib.sha256(b).hexdigest())


def poisson_upper(n, conf):
    lo, hi = 0.0, 10.0 * n + 50.0
    for _ in range(200):
        mid = (lo + hi) / 2
        s, t = 0.0, math.exp(-mid)
        for i in range(n + 1):
            s += t
            t *= mid / (i + 1)
        if s > 1 - conf:
            lo = mid
        else:
            hi = mid
    return hi


def sums(rows, ev):
    s = dict(C=0, S1=0, S2=0, SW=0, SC=0, Z=0)
    trial = ev in TRIAL
    idx = 2 + TRIAL[ev] if trial else STEP[ev]
    for r in rows:
        n = r[idx]
        s["C"] += 1; s["S1"] += n; s["S2"] += n * n; s["Z"] += n == 0
        if trial:
            s["SW"] += r[idx + 6]; s["SC"] += r[idx + 12]
    return s


def stats(s, G, k, trial):
    C, S1, S2 = s["C"], s["S1"], s["S2"]
    if S1 == 0 or C < 2:
        return None
    m = G * k if trial else G
    mean, p = S1 / C, S1 / (C * m)
    var = (S2 - S1 * S1 / C) / (C - 1)
    binom = m * p * (1 - p)
    SF = S2 - S1
    o = {"mean": mean, "p": p, "var_binom": var / binom, "v": 1 + (var - binom) / mean ** 2,
         "F": SF / S1, "E0": (m - 1) * p}
    o["R"] = o["F"] / o["E0"]
    if trial:
        SW, SC = s["SW"], s["SC"]
        o["Rw"] = (SW / S1) / ((k - 1) * p)
        o["Rx_same"] = (SC / S1) / ((G - 1) * p)
        o["Rx_diff"] = ((SF - SW - SC) / S1) / ((G - 1) * (k - 1) * p)
        o["Rx"] = W21 * o["Rx_same"] + (1 - W21) * o["Rx_diff"]
        o["Rx_pool"] = ((SF - SW) / S1) / ((G - 1) * k * p)
        o["rho_w_full"] = o["Rw"] * (2 ** 21 - 1) * p
        o["rho_x_full"] = o["Rx"] * (2 ** 32 - 1) * 2 ** 21 * p
    return o


def jackknife(rows, ev, G, k, keys):
    C = len(rows)
    gsz = C // NG
    gs = [sums(rows[g * gsz:(g + 1) * gsz], ev) for g in range(NG)]
    tot = {q: sum(x[q] for x in gs) for q in gs[0]}
    th = {q: [] for q in keys}
    for g in range(NG):
        st = stats({q: tot[q] - gs[g][q] for q in tot}, G, k, ev in TRIAL)
        for q in keys:
            th[q].append(st[q] if st else float("nan"))
    se = {}
    for q in keys:
        a = th[q]
        mu = sum(a) / NG
        se[q] = math.sqrt((NG - 1) / NG * sum((x - mu) ** 2 for x in a))
    return se


def analyse_arm(rows, G, k, label):
    res = {"frames": len(rows), "label": label}
    for ev in EVENTS:
        trial = ev in TRIAL
        s = sums(rows, ev)
        st = stats(s, G, k, trial)
        m = G * k if trial else G
        d = {"N": s["S1"], "m": m, "zero_frames": s["Z"]}
        if st is None:
            res[ev] = d
            continue
        d.update(st)
        d["log2_p"] = math.log2(st["p"])
        d["zero_expected"] = len(rows) * math.exp(m * math.log1p(-st["p"]))
        keys = ["mean", "v", "var_binom", "R"] + (["Rw", "Rx_same", "Rx_diff", "Rx", "Rx_pool"] if trial else [])
        se = jackknife(rows, ev, G, k, keys)
        for q in keys:
            d[q + "_se"] = se[q]
        SF = s["S2"] - s["S1"]
        d["pairs"] = SF / 2
        d["pairs_expected"] = st["E0"] * s["S1"] / 2
        if trial:
            p = st["p"]
            parts = {"within": (s["SW"], (k - 1) * p), "same_c1": (s["SC"], (G - 1) * p),
                     "diff_c1": (SF - s["SW"] - s["SC"], (G - 1) * (k - 1) * p)}
            for name, (W, per) in parts.items():
                d["pairs_" + name] = W / 2
                d["pairs_" + name + "_expected"] = per * s["S1"] / 2
                n = int(round(W / 2))
                e = per * s["S1"] / 2
                if n < 30 and e > 0:
                    d["poisson_upper95_" + name] = poisson_upper(n, 0.95) / e
                    d["poisson_upper99865_" + name] = poisson_upper(n, 0.99865) / e
        nom = NOMINAL.get(ev)
        if nom:
            d["mean_over_nominal"] = st["p"] / nom
            d["mean_over_nominal_se"] = d["mean_se"] / (m * nom)
        res[ev] = d
    return res


def stratum_upper(a, name, key):
    if a["pairs_" + name] >= 30:
        return a[key] + 3 * a[key + "_se"], "+3SE"
    return a.get("poisson_upper99865_" + name, float("inf")), "Poisson 99.865%"


def check_prereg(run_dir):
    txt = open(os.path.join(HERE, "PREREG.txt"), "rb").read()
    want = open(os.path.join(HERE, "PREREG.sha256")).read().split()[0]
    out = {"prereg_sha256": hashlib.sha256(txt).hexdigest(), "prereg_matches": hashlib.sha256(txt).hexdigest() == want}
    root = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
    files = {}
    for line in txt.decode().splitlines():
        mm = re.match(r"\s+([0-9a-f]{64})\s+(research/\S+)$", line)
        if mm:
            p = os.path.join(root, *mm.group(2).split("/"))
            files[mm.group(2)] = os.path.exists(p) and hashlib.sha256(open(p, "rb").read()).hexdigest() == mm.group(1)
    out["listed_files"] = files
    out["listed_all_match"] = bool(files) and all(files.values())
    ro = os.path.join(run_dir, "run_out.json")
    if os.path.exists(ro):
        out["run_out_prereg_sha256_matches"] = json.load(open(ro)).get("prereg_sha256") == want
    return out


def main():
    run_dir, outp = sys.argv[1], sys.argv[2]
    files = sorted(glob.glob(os.path.join(run_dir, "s*_a*_g*.bin")))
    data = [read(f) for f in files]
    G, k = data[0]["G"], data[0]["k"]
    assert all(d["G"] == G and d["k"] == k for d in data)
    checks = {"files": len(files), "beta_bad": 0, "e3p_nomask": 0, "t0_trials": 0, "g_redraws": 0, "c_redraws": 0,
              "pc_mismatch": 0, "row_shape_ok": True, "e1l_and_ra": [0, 0], "e3p_and_ra": [0, 0],
              "file_sha256": {os.path.basename(f): d["sha"] for f, d in zip(files, data)}}
    arm_rows = {}
    for arm in (0, 1):
        for gen in (1, 2):
            ds = sorted([d for d in data if d["arm"] == arm and d["gen"] == gen], key=lambda d: d["b0"])
            nxt = 0
            for d in ds:
                assert d["b0"] == nxt, "non-contiguous blocks"
                nxt += d["nb"]
                for r in d["rows"]:
                    checks["beta_bad"] += r[20]; checks["e3p_nomask"] += r[21]; checks["t0_trials"] += r[22]
                    checks["g_redraws"] += r[23]; checks["c_redraws"] += r[24]; checks["pc_mismatch"] += r[29]
                    checks["e1l_and_ra"][arm] += r[27]; checks["e3p_and_ra"][arm] += r[28]
                    if r[25] != G * k or r[26] != G or any(r[30:32]):
                        checks["row_shape_ok"] = False
                arm_rows.setdefault((arm, gen), []).extend(d["rows"])
    res = {"G": G, "k": k, "checks": checks, "allowed_factor_log2": ALLOWED_LOG2, "p_good_log2": math.log2(P_GOOD),
           "EW_frame_log2": math.log2((2 ** 32) * (2 ** 21 - 1) * P_GOOD)}
    for arm in (0, 1):
        rows = arm_rows.get((arm, 1), []) + arm_rows.get((arm, 2), [])
        res["arm%d" % arm] = analyse_arm(rows, G, k, "ctx" if arm == 0 else "ctrl")
        for gen in (1, 2):
            if arm_rows.get((arm, gen)):
                res["arm%d_G%d" % (arm, gen)] = analyse_arm(arm_rows[(arm, gen)], G, k, "gen %d" % gen)
    diff = {}
    for ev in EVENTS:
        a, b = res["arm0"].get(ev, {}), res["arm1"].get(ev, {})
        dd = {}
        for q in ("R", "Rx", "Rx_same", "Rx_diff", "Rw", "v"):
            if q in a and q in b:
                se = math.hypot(a[q + "_se"], b[q + "_se"])
                dd[q], dd[q + "_se"] = a[q] - b[q], se
                dd[q + "_z"] = (a[q] - b[q]) / se if se > 0 else float("nan")
        diff[ev] = dd
    res["ctx_minus_ctrl"] = diff
    prim = {}
    for ev in ("E1L", "E3P", "R24"):
        a = res["arm0"].get(ev, {})
        if "Rx" not in a:
            prim[ev] = {"note": "no events"}
            continue
        Ud, hd = stratum_upper(a, "diff_c1", "Rx_diff")
        Us, hs = stratum_upper(a, "same_c1", "Rx_same")
        U = (1 - W21) * Ud + W21 * Us
        d = diff[ev]
        prim[ev] = {"Rx": a["Rx"], "Rx_se": a["Rx_se"], "Rx_diff": a["Rx_diff"], "Rx_diff_se": a["Rx_diff_se"],
                    "Rx_same": a["Rx_same"], "Rx_same_se": a["Rx_same_se"], "U": U, "U_diff": Ud, "U_diff_method": hd,
                    "U_same": Us, "U_same_method": hs, "BOUNDED_2": U <= 2, "BOUNDED_16": U <= 16,
                    "pairs_diff_c1": a["pairs_diff_c1"], "pairs_diff_c1_expected": a["pairs_diff_c1_expected"],
                    "pairs_same_c1": a["pairs_same_c1"], "pairs_same_c1_expected": a["pairs_same_c1_expected"],
                    "log2_U": math.log2(U) if U > 0 else None,
                    "margin_to_allowed_log2": ALLOWED_LOG2 - math.log2(U) if U > 0 else None,
                    "excess_Rx": d.get("Rx"), "excess_Rx_se": d.get("Rx_se"),
                    "NO_EXCESS": abs(d.get("Rx", 0)) <= 3 * d.get("Rx_se", 0)}
    us = [prim[e].get("U", float("inf")) for e in prim]
    verdict = "SUPPORTED" if all(u <= 16 for u in us) else (
        "NOT SUPPORTED" if any(math.log2(u) > ALLOWED_LOG2 for u in us if u > 0) or any(u == float("inf") for u in us)
        else "WEAK")
    res["primary"], res["verdict"] = prim, verdict
    if "--prereg" in sys.argv:
        res["prereg_check"] = check_prereg(run_dir)
    json.dump(res, open(outp, "w"), indent=1)
    print(json.dumps({"verdict": verdict, "primary": prim, "allowed_log2": ALLOWED_LOG2,
                      "checks": {q: checks[q] for q in checks if q != "file_sha256"}}))


if __name__ == "__main__":
    main()
