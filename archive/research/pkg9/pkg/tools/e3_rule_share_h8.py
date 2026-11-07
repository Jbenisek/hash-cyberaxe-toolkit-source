#!/usr/bin/env python3
"""e3_rule_share_h8.py -- the exact share, under M, of the listed partial E3 events whose h1 satisfies the rule.
Writes evidence/e3_rule_share_h8.txt.

Written by a reviewing helper agent of this package (lens "judge") as review/judge_e3joint.py and copied to
tools/e3_rule_share_h8.py by the agent that applied the review: the paths, the module names, the name of the output
file and this paragraph were changed, nothing else (SHA-256 of the reviewer's file, with LF line ends:
1f0606356080957f739d4999591b2c7280b22af9cfa04a1d90d6b64726ae2e9b). Research helper, not submitted.

Of the reviewer's file only the enumeration is kept (everything before its part on the run files; the run files
are pooled by pkg6_data.read_runs). The last sentence of the paragraph below is therefore not done here.

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
H8 = HERE.parent / "evidence" / "h8"
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
for line in (H8 / "e3p_expected_H8.txt").read_text().splitlines():
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

import hashlib  # noqa: E402
HEAD = "INPUT evidence/h8/e3p_expected_H8.txt sha256 " + hashlib.sha256((H8 / "e3p_expected_H8.txt").read_bytes()).hexdigest()
say(f"SHARE events {len(events)} equal {same} count {tot[0]} rule4 {tot[1]} rule5 {tot[2]} rule6 {tot[3]}")
(HERE.parent / "evidence" / "e3_rule_share_h8.txt").write_text("\n".join([HEAD] + out) + "\n", encoding="ascii", newline="\n")
print("\n".join(x[:200] for x in out[:3]))
