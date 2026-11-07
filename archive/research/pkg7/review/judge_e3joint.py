#!/usr/bin/env python3
"""Review helper (lens: judge). Reads only; writes review/judge_e3joint.txt.

The programs for the graphics card print, next to the passes of the four-condition rule on h1, the number of
"listed partial E3 events" whose h1 passes that rule. The comparison file says "no exact expectation computed".
This script computes it, under the seven-word model M (Y4 uniform in the class, h1, Y9, w8 uniform), with an
enumeration of its own, written from the definitions (proof 6.2 and the header of e3partial_h8.c):

  event (psi, eps):  f1 ^ f1' = psi  and  e2 ^ e2' = eps   in E3 = G(Y3 | Y3', Y4, Y9, Y14; 0, w8)
  rule 4: h1 bit 0 = 0, bit 1 = 1, bit 16 = 0, bit 17 = 0; rule 5: and bits 2, 3 differ; rule 6: and bits 7, 8 differ

Change of variables (Y4, h1, Y9, w8) -> (Y4, h1, g1, e2), g1 = Y9 + h1, e2 = e1 + f1 + w8 (a bijection for fixed Y4).
  g1' = g1 + dh, dh = (h1 ^ eta) - h1 = eta - 2 (h1 & eta);    need g1 ^ g1' = gamma = ROL(psi, 12),
      which holds exactly when dh = (g1 ^ gamma) - g1 = gamma - 2 (g1 & gamma)   (mod 2^32)
  f1 = ROR(Y4 ^ g1, 12), f1' = f1 ^ psi, df = psi - 2 (f1 & psi)
  e2' = e2 + DY3 + df;   need (e2 + D) ^ e2 = eps with D = DY3 + df:
      number of e2 = 2^(32 - weight(eps & 7fffffff)) if bit 0 of D ^ eps is 0 and, for every i < 31 with eps_i = 0,
      bit i + 1 of D ^ eps equals bit i of D; otherwise 0.
The count is checked against the participant's own figure for every event (gpu/out/e3p_expected_H8.txt); the two
programs share nothing. Then the real and the model runs are read from the raw files and compared.
"""
import math
import re
import sys
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
H8 = HERE.parent.parent / "h8"
M32 = 0xFFFFFFFF
Y3, Y3B, ETA = 0x8127C181, 0x7EDF3E7E, 0x830303CF
DY3 = (Y3B - Y3) & M32
QMASK, QVALUE = 0x03CF8303, 0x030C0303
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & M32


def subsets(mask):
    bits = [i for i in range(32) if mask >> i & 1]
    n = len(bits)
    idx = np.arange(1 << n, dtype=np.uint64)
    res = np.zeros(1 << n, dtype=np.uint64)
    for j, b in enumerate(bits):
        res |= ((idx >> np.uint64(j)) & np.uint64(1)) << np.uint64(b)
    return res


def popcount(v):
    return bin(v).count("1")


# the class: e1 = Y3 + Y4 with the 13 bits of QMASK fixed
e1 = subsets(~QMASK & M32) | np.uint64(QVALUE)
Y4 = (e1 - np.uint64(Y3)) & np.uint64(M32)
assert len(Y4) == 1 << 19

# h1 patterns on eta: value of dh, and which rules the pattern satisfies
P = subsets(ETA)
DH = (np.uint64(ETA) - 2 * P) & np.uint64(M32)
b = lambda i: (P >> np.uint64(i)) & np.uint64(1)
r4 = (b(0) == 0) & (b(1) == 1) & (b(16) == 0) & (b(17) == 0)
r5 = r4 & ((b(2) ^ b(3)) == 1)
r6 = r5 & ((b(7) ^ b(8)) == 1)
dh_table = {}
for v, a4, a5, a6 in zip(DH.tolist(), r4.tolist(), r5.tolist(), r6.tolist()):
    t = dh_table.setdefault(v, [0, 0, 0, 0])
    t[0] += 1; t[1] += a4; t[2] += a5; t[3] += a6


def count_event(psi, eps):
    """(all, rule 4, rule 5, rule 6): numbers of (Y4, h1, Y9, w8), Y4 in the class, with the event; exact integers."""
    gamma = rol(psi, 12)
    Q = subsets(gamma)
    DG = ((np.uint64(gamma) - 2 * Q) & np.uint64(M32)).tolist()
    ypat, ycnt = np.unique(Y4 & np.uint64(gamma), return_counts=True)
    em = eps & 0x7FFFFFFF
    n_e2 = 1 << (32 - popcount(em))
    tot = [0, 0, 0, 0]
    for q, dg in zip(Q.tolist(), DG):
        w = dh_table.get(dg)
        if not w:
            continue
        x = (ypat ^ np.uint64(q)) & np.uint64(gamma)
        f = ((x >> np.uint64(12)) | (x << np.uint64(20))) & np.uint64(M32)          # ROR 12: bits of f1 on psi
        D = (np.uint64(DY3) + np.uint64(psi) - 2 * f) & np.uint64(M32)
        c = D ^ np.uint64(eps)
        ok = ((c & np.uint64(1)) == 0) & ((((c >> np.uint64(1)) ^ D) & np.uint64(~eps & 0x7FFFFFFF)) == 0)
        inner = int(ycnt[ok].sum()) * n_e2
        for k in range(4):
            tot[k] += w[k] * inner
    scale = (1 << 19) * (1 << (32 - popcount(gamma)))            # free bits of h1 and of g1
    return [t * scale for t in tot]


events = []
for line in (H8 / "gpu" / "out" / "e3p_expected_H8.txt").read_text().splitlines():
    f = line.split()
    if f and f[0] == "E3P":
        events.append((int(f[1], 16), int(f[2], 16), int(f[4])))
tot = [0, 0, 0, 0]
same = 0
for psi, eps, theirs in events:
    c = count_event(psi, eps)
    same += c[0] == theirs
    for k in range(4):
        tot[k] += c[k]
say(f"events {len(events)}; own count equal to e3p_expected_H8.txt in {same} of {len(events)}")
say(f"P(listed partial E3 event) per trial under M: 2^{math.log2(tot[0]) - 115:.4f}  (count {tot[0]})")
frac = [tot[k] / tot[0] for k in range(4)]
say(f"exact share of the listed partial E3 events whose h1 satisfies the rule, under M: "
    f"rule 4: {frac[1]:.6f}   rule 5: {frac[2]:.6f}   rule 6: {frac[3]:.6f}")
say(f"   (a uniform h1 independent of the event would give 0.0625, 0.03125, 0.015625)")

# ---- the raw runs
PAT_E = re.compile(r"trials with a listed partial E3 event (\d+)")
PAT_R = re.compile(r"rule on h1 .*?passes (\d+).*?listed partial E3 events that pass it: (\d+)")
PAT_T = re.compile(r"STAT \w+ trials 2\^([\d.]+)")
groups = {
    "real, independent contexts (cited in the text): real40, real42, real45": ["gpu/out/h8_real40.txt", "gpu/out/h8_real42.txt", "gpu/out/h8_real45.txt"],
    "real, layout runs 1..8 (cited)": [f"gpu/out/h8_layout_run{i}.txt" for i in range(1, 9)],
    "real, spread runs 1..8 (not in the text)": [f"gpu/out/h8_spread_run{i}.txt" for i in range(1, 9)],
    "real, layout runs 9..24 (text cites their early test only)": [f"gpu_more/out/h8_layout_run{i}.txt" for i in range(9, 25)],
    "real, independent contexts, 2^45 each, seeds 8201.. as far as finished (not in the text)":
        sorted("gpu_more/out/" + p.name for p in (H8 / "gpu_more" / "out").glob("h8_real45_seed*.txt") if p.stat().st_size > 3000),
    "MODEL draws: model40, model42, model44": ["gpu/out/h8_model40.txt", "gpu/out/h8_model42.txt", "gpu/out/h8_model44.txt"],
}
sums = {}
runs = {}
for name, files in groups.items():
    ev = ps = rule = 0
    trials = 0.0
    per = []
    for rel in files:
        p = H8 / rel
        if not p.exists() or p.stat().st_size == 0:
            say(f"   missing or empty: {rel}")
            continue
        t = p.read_text(errors="replace")
        me, mr, mt = PAT_E.search(t), PAT_R.search(t), PAT_T.search(t)
        if not (me and mr and mt):
            say(f"   no figures in {rel}")
            continue
        ev += int(me.group(1)); rule += int(mr.group(1)); ps += int(mr.group(2)); trials += 2.0 ** float(mt.group(1))
        per.append((rel.split("/")[-1], 2.0 ** float(mt.group(1)), int(mr.group(1)), int(me.group(1)), int(mr.group(2))))
    sums[name] = (trials, rule, ev, ps)
    runs[name] = per


def z_exact(k, n, p):
    return (k - n * p) / math.sqrt(n * p * (1 - p))


say("")
say("group | trials | partial E3 events (exact expectation, z) | of them passing rule 4 | share | z against the exact share")
p_event = tot[0] / 2.0 ** 115
for name, (trials, rule, ev, ps) in sums.items():
    if not ev:
        continue
    say(f"{name} | 2^{math.log2(trials):.2f} | {ev} ({trials * p_event:.1f}, {z_exact(ev, trials, p_event):+.2f}) | {ps} | "
        f"{ps / ev:.4f} | {z_exact(ps, ev, frac[1]):+.2f}")
real_names = [n for n in sums if n.startswith("real")]
T = sum(sums[n][0] for n in real_names); EV = sum(sums[n][2] for n in real_names); PS = sum(sums[n][3] for n in real_names)
say(f"ALL REAL RUNS | 2^{math.log2(T):.2f} | {EV} ({T * p_event:.1f}, {z_exact(EV, T, p_event):+.2f}) | {PS} | {PS / EV:.4f} | "
    f"{z_exact(PS, EV, frac[1]):+.2f}")
cited = [n for n in real_names if "(cited" in n]
T = sum(sums[n][0] for n in cited); EV = sum(sums[n][2] for n in cited); PS = sum(sums[n][3] for n in cited)
say(f"REAL RUNS CITED IN THE TEXT (2^45.49) | 2^{math.log2(T):.2f} | {EV} | {PS} | {PS / EV:.4f} | {z_exact(PS, EV, frac[1]):+.2f}")
mt, mr, me, mp = sums["MODEL draws: model40, model42, model44"]
say(f"real (cited) against the model draws, two-sample: {(PS / EV - mp / me) / math.sqrt((PS + mp) / (EV + me) * (1 - (PS + mp) / (EV + me)) * (1 / EV + 1 / me)):+.2f}")

# ---- the rule on h1 in all 24 layout runs and the 8 spread runs
say("")
for label, names in (("layout runs 1..8", ["real, layout runs 1..8 (cited)"]),
                     ("layout runs 9..24", ["real, layout runs 9..24 (text cites their early test only)"]),
                     ("layout runs 1..24", ["real, layout runs 1..8 (cited)", "real, layout runs 9..24 (text cites their early test only)"]),
                     ("spread runs 1..8", ["real, spread runs 1..8 (not in the text)"])):
    per = [r for n in names for r in runs[n]]
    if not per:
        continue
    counts = np.array([r[2] for r in per], dtype=np.float64)
    n = per[0][1]
    expect = n / 16
    binvar = n * (1 / 16) * (15 / 16)
    rel = (counts - expect) / expect
    k = len(counts)
    var = counts.var(ddof=1)
    pooled_z = (counts.sum() - k * expect) / math.sqrt(k * binvar)
    se_mean = math.sqrt(var / k)
    say(f"rule 4 on h1, {label}: {k} runs; share within {abs(rel).max() * 1e5:.2f} parts in 100,000 of 2^-4; below 2^-4 in "
        f"{int((counts < expect).sum())} runs; variance / binomial {var / binvar:.1f}; pooled {pooled_z:+.2f} binomial s.d.; "
        f"with the spread of these runs themselves: {(counts.mean() - expect) / se_mean:+.2f} standard errors ({k - 1} d.f.); "
        f"with the variance of independent contexts (4,230,272 per context): "
        f"{(counts.sum() - k * expect) / math.sqrt(k * (n / 524288) * 4230271.88):+.2f}")

(HERE / "judge_e3joint.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(out[:4]))
print(f"{len(out)} lines -> judge_e3joint.txt")
