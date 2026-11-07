#!/usr/bin/env python3
"""Reviewer check, lens MATHEMATICS AND COST, part (a), second route: rule A against the WHOLE seven-word system
of one beta, without the calculator's list of outcomes.

For a beta the CNF holds, with the encoder of math_sat.py: E1 on both messages (unknowns d1, b1 and s = a1 + w5;
c1 = Y11 + d1, c1' = Y11' + d1, c1 XOR c1' = ROL(beta,12), b1' = b1 XOR beta, a2 = s + b1, a2' = s + b1' + delta,
then d2, c2, b2 as in G), E3 on both messages (unknowns Y4, h1, Y9, w8, Y4 in the class), and R = 0 as the four
digest-word equations of proof.md 3.3 between the outputs of E1 and E3. No tau and no eps is prescribed.

    any       is there a solution with this beta at all?
    violate   is there a solution with this beta whose h1 violates rule A?
              UNSAT says: every solution of the seven-word system with Y4 in the class and this beta satisfies
              rule A, whatever its outcome (tau, eps) is, listed by the calculator or not.

    math_seven.py MODE SOLVER THREADS SECONDS [betas ...]   default betas: the 39 with a part and the three flagged
    -> review/math_seven_<MODE>_<SOLVER>.txt
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import math_sat as ms  # noqa: E402
from math_sat import G, M, Y3, Y3B, ETA, ror, rol, const, bror, brol  # noqa: E402

TMP = Path(os.path.expanduser("~/hashsmash/pkg5-review-math/seven"))
Y11, Y11B = G(*ms.PIN, ms.W4, ms.W13)[2], G(*ms.PIN, ms.W4B, ms.W13)[2]
assert (Y11, Y11B) == (0x5EBF5BC0, 0xA144803F)
DELTA = (ms.W4 - ms.W4B) & M
assert DELTA == 0xFFFFFFFE
FLAGGED = ("c81cd8b3", "f81c2873", "f81c28b3")


def build(beta, mode):
    c = ms.Cnf()
    y4, h1, y9, w8, d1, b1, s = (c.new32() for _ in range(7))
    # E1
    c1, c1b = c.add(const(Y11), d1), c.add(const(Y11B), d1)
    c.fix(c.xor32(c1, c1b), rol(beta, 12))
    b1b = c.xor32(b1, const(beta))
    a2, a2b = c.add(s, b1), c.add(c.add(s, b1b), const(DELTA))
    d2, d2b = bror(c.xor32(d1, a2), 8), bror(c.xor32(d1, a2b), 8)
    c2, c2b = c.add(c1, d2), c.add(c1b, d2b)
    b2, b2b = bror(c.xor32(b1, c2), 7), bror(c.xor32(b1b, c2b), 7)
    # E3
    e1a, e1b = c.add(const(Y3), y4), c.add(const(Y3B), y4)
    c.fix(c.xor32(e1a, e1b), rol(ETA, 16))
    y14 = c.xor32(brol(h1, 16), e1a)
    h1b = bror(c.xor32(y14, e1b), 16)
    outs = []
    for e1, h in ((e1a, h1), (e1b, h1b)):
        g1 = c.add(y9, h)
        f1 = bror(c.xor32(y4, g1), 12)
        e2 = c.add(c.add(e1, f1), w8)
        h2 = bror(c.xor32(h, e2), 8)
        g2 = c.add(g1, h2)
        f2 = bror(c.xor32(f1, g2), 7)
        outs.append((e2, f2, g2, h2))
    (ea, fa, ga, ha), (eb, fb, gb, hb) = outs
    # R = 0: digest words 1, 3, 4, 6 are Z1^Z9, Z3^Z11, Z4^Z12, Z6^Z14 = E1.a^E3.c, E3.a^E1.c, E3.b^E1.d, E1.b^E3.d
    for p, q in ((c.xor32(a2, a2b), c.xor32(ga, gb)), (c.xor32(ea, eb), c.xor32(c2, c2b)),
                 (c.xor32(fa, fb), c.xor32(d2, d2b)), (c.xor32(b2, b2b), c.xor32(ha, hb))):
        c.fix(c.xor32(p, q), 0)
    fails = []
    for bits, value in ms.RULE:
        p = h1[bits[0]]
        for i in bits[1:]:
            p = c.xor(p, h1[i])
        fails.append(p if value == 0 else -p)
    if mode == "violate":
        c.cl.append(fails)
    if mode == "other":                # a solution whose outcome (tau, eps) is none of the calculator's for this beta
        taub, epsb = c.xor32(a2, a2b), c.xor32(c2, c2b)
        for tau, eps in LISTED.get(beta, []):
            c.cl.append([(-v if tau >> i & 1 else v) for i, v in enumerate(taub)] + [(-v if eps >> i & 1 else v) for i, v in enumerate(epsb)])
    return c, (y4, h1, y9, w8, d1, b1, s)


def listed_outcomes():
    """{beta: [(tau, eps)]}: the outcomes with a nonzero product in my own run of the calculator binary."""
    out = {}
    for l in (HERE / "math_calc2_mass.txt").read_text(encoding="ascii").splitlines():
        f = l.split()
        if f and f[0] == "OUT" and float(f[5]) > -900.0:
            out.setdefault(int(f[1], 16), []).append((int(f[2], 16), int(f[3], 16)))
    return out


LISTED = listed_outcomes()


def plain(beta, y4, h1, y9, w8, d1, b1, s):
    """The model as inputs of E1 and E3 in the names of proof.md 6.2 (a1 = 0, w12 = 0), evaluated with G alone."""
    Y12 = rol(d1, 16)
    Y6 = rol(b1, 12) ^ ((Y11 + d1) & M)
    Y1 = (0 - Y6) & M
    w5 = s
    Y14 = rol(h1, 16) ^ ((Y3 + y4) & M)
    ea, eb = G(Y1, Y6, Y11, Y12, 0, w5), G(Y1, Y6, Y11B, Y12, 0, (w5 + DELTA) & M)
    fa, fb = G(Y3, y4, y9, Y14, 0, w8), G(Y3B, y4, y9, Y14, 0, w8)
    R = (ea[0] ^ fa[2] ^ eb[0] ^ fb[2], fa[0] ^ ea[2] ^ fb[0] ^ eb[2], fa[1] ^ ea[3] ^ fb[1] ^ eb[3], ea[1] ^ fa[3] ^ eb[1] ^ fb[3])
    b1a = ror(Y6 ^ ((Y11 + ror(Y12, 16)) & M), 12)
    b1bb = ror(Y6 ^ ((Y11B + ror(Y12, 16)) & M), 12)
    good = (R == (0, 0, 0, 0) and b1a ^ b1bb == beta and ((Y3 + y4) & 0x015FE7C1) == 0x00036181
            and ror(Y14 ^ ((Y3 + y4) & M), 16) == h1)
    return good, ea[0] ^ eb[0], ea[2] ^ eb[2]


def solve(args):
    mode, solver, seconds, beta = args
    c, words = build(beta, mode)
    path = TMP / ("%s_%s_%08x.cnf" % (mode, solver, beta))
    c.write(path)
    cmd = {"cadical": ["cadical", "-q", "-t", str(seconds)], "kissat": ["kissat", "-q", "--time=%d" % seconds],
           "cms": ["cryptominisat5", "--verb", "0", "--maxtime", str(seconds)]}[solver]
    t0 = time.time()
    r = subprocess.run(cmd + [str(path)], capture_output=True, text=True)
    sat, model = "?", {}
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            sat = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT"}.get(line[2:].strip(), "?")
        elif line.startswith("v "):
            for tok in line[2:].split():
                v = int(tok)
                if v:
                    model[abs(v)] = v > 0
    path.unlink()
    line = "%s %08x %s vars %d clauses %d sec %.0f" % (mode.upper(), beta, sat, c.n, len(c.cl), time.time() - t0)
    if sat == "SAT":
        vals = [sum(1 << i for i, b in enumerate(bits) if model.get(b, False)) for bits in words]
        good, tau, eps = plain(beta, *vals)
        line += " tau %08x eps %08x h1 %08x solution %d rule_A %d" % (tau, eps, vals[1], int(good), int(ms.rule_a(vals[1])))
    return line


def main():
    mode, solver, threads, seconds = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
    betas = sys.argv[5:]
    if not betas:
        betas = sorted({l.split()[1] for l in (HERE / "math_calc2_mass.txt").read_text(encoding="ascii").splitlines()
                        if l.startswith("OUT ")}) + list(FLAGGED)
    TMP.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(threads) as pool:
        lines = list(pool.map(solve, [(mode, solver, seconds, int(b, 16)) for b in betas]))
    out = HERE / ("math_seven_%s_%s.txt" % (mode, solver))
    old = out.read_text(encoding="ascii").splitlines() if out.exists() else []
    have = {l.split()[1] for l in lines}
    lines += [l for l in old if l.split()[1] not in have]
    out.write_text("\n".join(sorted(lines)) + "\n", encoding="ascii", newline="\n")
    n = lambda s: sum(1 for l in lines if l.split()[2] == s)  # noqa: E731
    print("%s %s: betas %d, SAT %d, UNSAT %d, undecided %d; models that are not solutions %d; longest %.0f s" % (
        mode, solver, len(lines), n("SAT"), n("UNSAT"), n("?"), sum(" solution 0" in l for l in lines),
        max(float(l.split()[8]) for l in lines)))


if __name__ == "__main__":
    main()
