#!/usr/bin/env python3
"""n3_rule_h8.py -- the E3 side of every outcome counted exactly and split by the rule. One thread. Reads
evidence/pairs_recount_830303cf.txt and the solver files; writes evidence/n3_rule_h8.txt.

Written by a reviewing helper agent of this package (lens "judge") as review/judge_n3_rule.py and copied to
tools/n3_rule_h8.py by the agent that applied the review: the paths, the module names, the name of the output
file and this paragraph were changed, nothing else (SHA-256 of the reviewer's file, with LF line ends:
cd424aa5d121abf69dbf89e0b8a2af40e1c12265142186a8bc66fa09fc45b25a). Research helper, not submitted.

An exact count of the E3 side of every outcome, SPLIT BY THE RULE, with an enumeration written for this review from
the definitions of proof 6.2 (no solver, no sampling, integers only). For an outcome (tau, eps):

  N3      = number of (Y4, h1, Y9, w8), Y4 in the class, with f1^f1' = psi, e2^e2' = eps, g2^g2' = tau
  N3_rule = the same with h1 satisfying the rule (4, 5 or 6 conditions)

Uses: (1) N3 against the calculator's N3 of the same outcome (a check of both programs); (2) the 54 answers
"unsatisfiable" behind the count that the claim uses: an outcome has no violating solution exactly when
N3 = N3_rule; (3) the exact rate r_A under M, which the text says "was not computed".

Method. Variables (Y4, h1, g1 = Y9 + h1, e2 = e1 + f1 + w8), a bijection for fixed Y4. psi = tau ^ ROR(tau,1),
gamma = ROL(psi,12), rho = ROR(eta ^ eps, 8).
  C1  g1' = g1 + dh with dh = eta - 2 (h1 & eta); g1 ^ g1' = gamma  <=>  dh = gamma - 2 (g1 & gamma) mod 2^32.
  C2  e2' = e2 + D, D = DY3 + psi - 2 (f1 & psi), f1 = ROR(Y4 ^ g1, 12); (e2 + D) ^ e2 = eps fixes, when it is
      possible at all, the bits of e2 at the positions i < 31 of eps: e2_i = bit i+1 of D ^ eps.
  C3  h2 = ROR(h1 ^ e2, 8), h2' = h2 ^ rho, g2 = g1 + h2, g2' = (g1 ^ gamma) + (h2 ^ rho); g2 ^ g2' = tau: counted by a
      carry automaton with two carries over the bits, g1 fixed on gamma, h2 fixed where both h1 and e2 are fixed;
      every h2 stands for 2^(32 - |eta or eps_low|) pairs (h1, e2).
"""
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
EV = HERE.parent / "evidence"
M32, LOW = 0xFFFFFFFF, 0x7FFFFFFF
Y3, Y3B, ETA = 0x8127C181, 0x7EDF3E7E, 0x830303CF
DY3 = (Y3B - Y3) & M32
QMASK, QVALUE = 0x03CF8303, 0x030C0303
U = np.uint64
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M32


def rol(v, n):
    return ror(v, 32 - n)


def pop(v):
    return bin(v).count("1")


def subsets(mask):
    bits = [i for i in range(32) if mask >> i & 1]
    idx = np.arange(1 << len(bits), dtype=np.uint64)
    res = np.zeros(1 << len(bits), dtype=np.uint64)
    for j, b in enumerate(bits):
        res |= ((idx >> U(j)) & U(1)) << U(b)
    return res


E1ALL = subsets(~QMASK & M32) | U(QVALUE)
Y4 = (E1ALL - U(Y3)) & U(M32)
P = subsets(ETA).tolist()
dh_map = {}
for p in P:
    dh_map.setdefault((ETA - 2 * p) & M32, []).append(p)
DH_KEYS = np.array(sorted(dh_map), dtype=np.uint64)


def rules(p):
    b = lambda i: p >> i & 1
    r4 = b(0) == 0 and b(1) == 1 and b(16) == 0 and b(17) == 0
    r5 = r4 and (b(2) ^ b(3)) == 1
    r6 = r5 and (b(7) ^ b(8)) == 1
    return r4, r5, r6


def automaton(gamma, rho, tau, q, he, jsrc):
    """Number of (g1, h2): g1 = q on gamma, bit j of h2 = bit (j+8) of jsrc where that position is in he,
    with (g1 + h2) ^ ((g1 ^ gamma) + (h2 ^ rho)) = tau."""
    states = {(0, 0): 1}
    for i in range(32):
        gi, ri = gamma >> i & 1, rho >> i & 1
        need = gi ^ ri ^ (tau >> i & 1)
        gopts = ((q >> i & 1),) if gi else (0, 1)
        s = (i + 8) & 31
        jopts = ((jsrc >> s & 1),) if he >> s & 1 else (0, 1)
        new = {}
        for (c1, c2), n in states.items():
            if c1 ^ c2 != need:
                continue
            for g in gopts:
                for j in jopts:
                    k = ((g + j + c1) >> 1, ((g ^ gi) + (j ^ ri) + c2) >> 1)
                    new[k] = new.get(k, 0) + n
        states = new
        if not states:
            return 0
    return sum(states.values())


def n3_split(tau, eps):
    psi = tau ^ ror(tau, 1)
    gamma = rol(psi, 12)
    rho = ror(ETA ^ eps, 8)
    E = eps & LOW
    he = ETA & E
    mult = 1 << (32 - pop(ETA | E))
    Q = subsets(gamma)
    DG = (U(gamma) - 2 * Q) & U(M32)
    hit = np.isin(DG, DH_KEYS)
    if not hit.any():
        return [0, 0, 0, 0]
    ypat, ycnt = np.unique(Y4 & U(gamma), return_counts=True)
    tot = [0, 0, 0, 0]
    memo = {}
    for q, dg in zip(Q[hit].tolist(), DG[hit].tolist()):
        x = (ypat ^ U(q)) & U(gamma)
        f = ((x >> U(12)) | (x << U(20))) & U(M32)
        D = (U(DY3) + U(psi) - 2 * f) & U(M32)
        c = D ^ U(eps)
        ok = ((c & U(1)) == 0) & ((((c >> U(1)) ^ D) & U(~eps & LOW)) == 0)
        if not ok.any():
            continue
        for cc, cnt in zip(c[ok].tolist(), ycnt[ok].tolist()):
            e2fix = (cc >> 1) & E
            for p in dh_map[dg]:
                jsrc = (p ^ e2fix) & he
                key = (q, jsrc)
                n = memo.get(key)
                if n is None:
                    n = memo[key] = automaton(gamma, rho, tau, q, he, jsrc)
                if n:
                    w = cnt * mult * n
                    r4, r5, r6 = rules(p)
                    tot[0] += w; tot[1] += w * r4; tot[2] += w * r5; tot[3] += w * r6
    return tot


# ---- the outcomes and the solver answers
outcomes, sampled = {}, {}
for line in (EV / "pairs_recount_830303cf.txt").read_text().splitlines():
    f = line.split()
    if f and f[0] == "PAIR":
        sampled[f[2]] = int(f[f.index("sampled") + 1])
    elif f and f[0] == "OUTX":
        outcomes[(f[2], f[3], f[4])] = (int(f[6]), int(f[8]))
est = {b for b, s in sampled.items() if s > 0}
unsat = {}
for n in (4, 5, 6):
    unsat[n] = set()
    for line in (EV / f"rule_a_sat_830303cf_rule{n}.txt").read_text().splitlines():
        f = line.split()
        if f and f[0] == "VIOLATE" and f[4] == "UNSAT":
            unsat[n].add((f[1], f[2], f[3]))

t0 = time.time()
res = {}
for key in outcomes:
    res[key] = n3_split(int(key[1], 16), int(key[2], 16))
say(f"outcomes {len(outcomes)}; seconds {time.time() - t0:.0f}")
full = [k for k in outcomes if k[0] not in est]
same_full = sum(res[k][0] == outcomes[k][1] for k in full)
same_est = sum(res[k][0] == outcomes[k][1] for k in outcomes if k[0] in est)
say(f"N3 of this enumeration equal to the calculator's N3: {same_full} of {len(full)} outcomes of the betas counted in full; "
    f"{same_est} of {len(outcomes) - len(full)} outcomes of the betas that hold estimates")
diff = [(k, res[k][0], outcomes[k][1]) for k in full if res[k][0] != outcomes[k][1]][:5]
for k, a, b in diff:
    say(f"   differs: {k} here {a} calculator {b}")
for n, col in ((4, 1), (5, 2), (6, 3)):
    none_viol = {k for k in outcomes if res[k][0] > 0 and res[k][0] == res[k][col]}
    say(f"rule {n}: outcomes whose every solution satisfies the rule (N3 = N3_rule), by this count: {len(none_viol)}; "
        f"the solver files say UNSAT for {len(unsat[n])}; the two sets are equal: {none_viol == unsat[n]}; "
        f"of them in betas with estimates: {sum(1 for k in none_viol if k[0] in est)}")
    cons = sum(Fraction(outcomes[k][0] * res[k][0], 2 ** 83) for k in none_viol if k[0] not in est)
    exact_full = sum(Fraction(outcomes[k][0] * res[k][col], 2 ** 83) for k in full)
    exact_all = sum(Fraction(outcomes[k][0] * res[k][col], 2 ** 83) for k in outcomes)
    say(f"   conservative count (kept outcomes, betas in full): {float(cons):,.4f}; exact rate of the solutions that satisfy the rule "
        f"under M, r_A: betas in full {float(exact_full):,.4f}, all 60 betas {float(exact_all):,.4f} "
        f"(/ 2^25 = {float(exact_all) / 2 ** 25:.4f}, / 2^26 = {float(exact_all) / 2 ** 26:.4f}); "
        f"conservative / exact = {float(cons / exact_all):.4f}")
tot_all = sum(Fraction(outcomes[k][0] * res[k][0], 2 ** 83) for k in outcomes)
say(f"count of all solutions with this enumeration's N3 and the calculator's E1: {float(tot_all):,.6f} "
    f"(calculator 162,266,763.6579; the other model's recount 162,266,763.6588); the betas with estimates here: "
    f"{float(sum(Fraction(outcomes[k][0] * res[k][0], 2 ** 83) for k in outcomes if k[0] in est)):.6f}")
worst = sorted(((Fraction(outcomes[k][0] * (res[k][0] - res[k][2]), 2 ** 83), k) for k in outcomes), reverse=True)[:5]
say("rule 5, the outcomes that lose most to the rule (exact, lost part / part): " + "; ".join(
    f"{k[0]} {k[1]} {k[2]} {float(v):,.1f} / {float(Fraction(outcomes[k][0] * res[k][0], 2 ** 83)):,.1f}" for v, k in worst))
import hashlib  # noqa: E402
HEAD = "INPUT evidence/pairs_recount_830303cf.txt sha256 " + hashlib.sha256((EV / "pairs_recount_830303cf.txt").read_bytes()).hexdigest()
(EV / "n3_rule_h8.txt").write_text("\n".join([HEAD] + out) + "\n", encoding="ascii", newline="\n")
print("\n".join(x[:400] for x in out))
