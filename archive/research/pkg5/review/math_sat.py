#!/usr/bin/env python3
"""Reviewer check, lens MATHEMATICS AND COST, part (a): rule A against the solutions of the E3 side, per outcome.

Nothing of the package's encoder (research/r2_sat.py) or of tools/rule_a_sat.py is imported. The CNF is written
here, gate by gate, from proof.md 6.2 and Section 10, in a formulation that differs from the package's:

    unknowns Y4, h1, Y9, w8 (h1 = second value of E3 on the 60-byte message A)
    e1 = Y3 + Y4, e1' = Y3' + Y4          (Y3, Y3' computed here with G from the six constants of 3.2)
    class by its definition:  e1 XOR e1' = ROL(eta, 16)
    Y14 = ROL(h1,16) XOR e1,  h1' = ROR(Y14 XOR e1', 16)
    E3 on both messages to all four outputs e2, f2, g2, h2
    R = 0 for an E1 with (beta, tau, eps):   g2^g2' = tau,  e2^e2' = eps,  f2^f2' = ROR(tau,8),
                                             h2^h2' = ROR(beta XOR eps, 7)
(the package forces the first-half difference psi instead of the b and d output differences).

    math_sat.py run MODE SOLVER THREADS [LIMIT]   MODE violate | all | keep ; SOLVER cadical | kissat | cms
                                                  -> review/math_sat_<MODE>_<SOLVER>.txt
    math_sat.py count                             rebuilds the count that the claim uses from my own answers
Outcomes: every OUT line of review/math_calc2_mass.txt (my own run of the calculator binary) with a nonzero E1.
"""
import os
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
TMP = Path(os.path.expanduser("~/hashsmash/pkg5-review-math/sat"))
M = 0xFFFFFFFF
ETA = 0xE7C1815F
PIN = (0xD5D881CA, 0xAA277E35, 0x1F208000, 0x123F2142)
W4, W13 = 0x7FFFFFFF, 0xFFFD6E01
IV2, IV6 = 0x3C6EF372, 0x1F83D9AB


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


K = (IV2 + IV6) & M
W4B = ((((K + W4) & M) ^ 2) - K) & M
Y3 = G(*PIN, W4, W13)[0]
Y3B = G(*PIN, W4B, W13)[0]
assert (Y3, Y3B) == (0x3F52EDA0, 0xC0AC125F)


def rule_a(h1):
    b = lambda i: h1 >> i & 1  # noqa: E731
    return b(16) == 1 and b(0) == b(1) and b(1) == b(2) and b(2) == b(3) and b(3) != b(4) and b(23) != b(24)


RULE = ((16,), 1), ((0, 1), 0), ((1, 2), 0), ((2, 3), 0), ((3, 4), 1), ((23, 24), 1)   # (bits of h1, their XOR)


class Cnf:
    def __init__(self):
        self.n, self.cl = 1, [[1]]                # variable 1 is TRUE

    def new32(self):
        self.n += 32
        return list(range(self.n - 31, self.n + 1))

    def xor(self, a, b):
        self.n += 1
        z = self.n
        self.cl += [[-a, -b, -z], [a, b, -z], [a, -b, z], [-a, b, z]]
        return z

    def maj(self, a, b, c):
        self.n += 1
        m = self.n
        self.cl += [[-a, -b, m], [-a, -c, m], [-b, -c, m], [a, b, -m], [a, c, -m], [b, c, -m]]
        return m

    def add(self, x, y):
        c, out = -1, []
        for i in range(32):
            out.append(self.xor(self.xor(x[i], y[i]), c))
            if i < 31:
                c = self.maj(x[i], y[i], c)
        return out

    def xor32(self, x, y):
        return [self.xor(a, b) for a, b in zip(x, y)]

    def fix(self, bits, value):
        for i, b in enumerate(bits):
            self.cl.append([b if value >> i & 1 else -b])

    def write(self, path):
        with open(path, "w", encoding="ascii", newline="\n") as f:
            f.write("p cnf %d %d\n" % (self.n, len(self.cl)))
            f.write("".join(" ".join(map(str, c)) + " 0\n" for c in self.cl))


def const(v):
    return [1 if v >> i & 1 else -1 for i in range(32)]


def bror(bits, n):
    return [bits[(i + n) % 32] for i in range(32)]


def brol(bits, n):
    return bror(bits, 32 - n)


def build(beta, tau, eps, mode):
    c = Cnf()
    y4, h1, y9, w8 = c.new32(), c.new32(), c.new32(), c.new32()
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
    c.fix(c.xor32(ga, gb), tau)
    c.fix(c.xor32(ea, eb), eps)
    c.fix(c.xor32(fa, fb), ror(tau, 8))
    c.fix(c.xor32(ha, hb), ror(beta ^ eps, 7))
    fails = []
    for bits, value in RULE:
        p = h1[bits[0]]
        for i in bits[1:]:
            p = c.xor(p, h1[i])
        fails.append(p if value == 0 else -p)      # true when the condition fails
    if mode == "violate":
        c.cl.append(fails)
    elif mode == "keep":
        c.cl += [[-f] for f in fails]
    return c, (y4, h1, y9, w8)


def plain(beta, tau, eps, y4, h1, y9, w8):
    """The model in 32-bit arithmetic: E3 of 6.2 on both messages from Y14, and the four digest-word conditions."""
    y14 = rol(h1, 16) ^ ((Y3 + y4) & M)
    a, b = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
    h1a = ror(y14 ^ ((Y3 + y4) & M), 16)
    eta = ror(((Y3 + y4) & M) ^ ((Y3B + y4) & M), 16)
    return (h1a == h1 and eta == ETA and ((Y3 + y4) & 0x015FE7C1) == 0x00036181
            and a[2] ^ b[2] == tau and a[0] ^ b[0] == eps and a[1] ^ b[1] == ror(tau, 8) and a[3] ^ b[3] == ror(beta ^ eps, 7))


SOLVERS = {"cadical": ["cadical", "-q", "-t", "3000"], "kissat": ["kissat", "-q", "--time=3000"],
           "cms": ["cryptominisat5", "--verb", "0", "--maxtime", "3000"]}


def solve(args):
    mode, solver, (beta, tau, eps) = args
    c, words = build(beta, tau, eps, mode)
    path = TMP / ("%s_%s_%08x_%08x_%08x.cnf" % (mode, solver, beta, tau, eps))
    c.write(path)
    t0 = time.time()
    r = subprocess.run(SOLVERS[solver] + [str(path)], capture_output=True, text=True)
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
    line = "%s %08x %08x %08x %s vars %d clauses %d sec %.0f" % (mode.upper(), beta, tau, eps, sat, c.n, len(c.cl), time.time() - t0)
    if sat == "SAT":
        vals = [sum(1 << i for i, b in enumerate(bits) if model.get(b, False)) for bits in words]
        line += " Y4 %08x h1 %08x Y9 %08x w8 %08x solution %d rule_A %d" % (*vals, int(plain(beta, tau, eps, *vals)), int(rule_a(vals[1])))
    return line


def outcomes():
    out = []
    for line in (HERE / "math_calc2_mass.txt").read_text(encoding="ascii").splitlines():
        f = line.split()
        if f and f[0] == "OUT" and float(f[5]) > -900.0:
            beta, tau, eps = int(f[1], 16), int(f[2], 16), int(f[3], 16)
            if eps ^ rol(beta ^ eps, 1) != ETA:
                raise SystemExit("an outcome does not satisfy eta = eps XOR ROL(beta XOR eps, 1)")
            out.append((beta, tau, eps, float(f[5]), float(f[7])))
    return out


def run(mode, solver, threads, limit):
    TMP.mkdir(parents=True, exist_ok=True)
    keys = sorted(outcomes(), key=lambda o: -(o[3] + o[4] - bin(rol(o[0], 12) & 0x7FFFFFFF).count("1")))[:limit]
    with ThreadPoolExecutor(threads) as pool:
        lines = list(pool.map(solve, [(mode, solver, k[:3]) for k in keys]))
    out = HERE / ("math_sat_%s_%s.txt" % (mode, solver))
    old = out.read_text(encoding="ascii").splitlines() if out.exists() else []
    have = {tuple(l.split()[1:4]) for l in lines}
    lines += [l for l in old if tuple(l.split()[1:4]) not in have]
    out.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    n = lambda s: sum(1 for l in lines if l.split()[4] == s)  # noqa: E731
    print("%s %s: %d outcomes, SAT %d, UNSAT %d, undecided %d; SAT models that are not solutions %d; longest %s s" % (
        mode, solver, len(lines), n("SAT"), n("UNSAT"), n("?"), sum(1 for l in lines if " solution 0" in l),
        max(float(l.split()[10]) for l in lines)))


def count():
    """The count the claim uses, from my answers; and my answers against the package's file."""
    mine = {}
    for solver in ("cadical", "kissat", "cms"):
        p = HERE / ("math_sat_violate_%s.txt" % solver)
        if p.exists():
            for l in p.read_text(encoding="ascii").splitlines():
                f = l.split()
                mine.setdefault(tuple(f[1:4]), {})[solver] = f[4] + ("" if f[4] != "SAT" else ":%s%s" % (l.split(" solution ")[1][0], l.split(" rule_A ")[1][0]))
    theirs, exact = {}, {}
    for l in (PKG / "evidence" / "rule_a_sat_e7c1815f.txt").read_text(encoding="ascii").splitlines():
        f = l.split()
        if f and f[0] == "VIOLATE":
            theirs[tuple(f[1:4])] = f[4]
    for l in (PKG / "evidence" / "pairs_recount_e7c1815f.txt").read_text(encoding="ascii").splitlines():
        f = l.split()
        if f and f[0] == "OUTX":
            exact[(f[2], f[3], f[4])] = (int(f[6]), int(f[8]))
    logs = {("%08x" % b, "%08x" % t, "%08x" % e): (lp, ln) for b, t, e, lp, ln in outcomes()}
    import math
    worst = 0.0
    for key, (n1, n3) in exact.items():
        k = bin(rol(int(key[0], 16), 12) & 0x7FFFFFFF).count("1")
        lp, ln = logs[key]
        worst = max(worst, abs(math.log2(n1) - (96 - k) - lp), abs(math.log2(n3) - ln))
    print("outcomes: mine (calculator run) %d, package OUTX %d, package VIOLATE %d, same sets %s; largest |log2| difference of N1, N3 "
          "between OUTX and my run's two decimals %.4f" % (len(logs), len(exact), len(theirs), set(logs) == set(exact) == set(theirs), worst))
    total = sum(n1 * n3 for n1, n3 in exact.values()) / 2 ** 80
    answered = [k for k in exact if k in mine]
    disagree = [k for k in answered if len({v.split(":")[0] for v in mine[k].values()} | {theirs[k]}) != 1]
    badmodel = [k for k in answered if any(v.startswith("SAT") and v != "SAT:10" for v in mine[k].values())]
    unsat = [k for k in answered if all(v == "UNSAT" for v in mine[k].values())]
    sat = [k for k in answered if all(v.startswith("SAT") for v in mine[k].values())]
    drop = sum(exact[k][0] * exact[k][1] for k in sat) / 2 ** 80
    kept = sum(exact[k][0] * exact[k][1] for k in unsat) / 2 ** 80
    print("sum of all %d products %.1f; answered by me %d: UNSAT %d carrying %.1f, SAT %d carrying %.1f; disagreements with the "
          "package %d; SAT models that are not violating solutions %d" % (len(exact), total, len(answered), len(unsat), kept, len(sat), drop,
                                                                          len(disagree), len(badmodel)))
    by_solver = {}
    for k in answered:
        for s, v in mine[k].items():
            by_solver.setdefault(s, [0, 0, 0])[("UNSAT", "SAT", "?").index(v.split(":")[0])] += 1
    print("per solver (UNSAT, SAT, undecided):", by_solver)
    heavy = ("481c6852", "58146852", "481c5852", "58145852")
    for b in heavy:
        ks = [k for k in exact if k[0] == b]
        print("beta %s: %d outcomes, part %.1f; answered %d, UNSAT %d (part kept %.1f), SAT %d" % (
            b, len(ks), sum(exact[k][0] * exact[k][1] for k in ks) / 2 ** 80, sum(k in mine for k in ks),
            sum(k in unsat for k in ks), sum(exact[k][0] * exact[k][1] for k in ks if k in unsat) / 2 ** 80, sum(k in sat for k in ks)))


if __name__ == "__main__":
    if sys.argv[1] == "run":
        run(sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5]) if len(sys.argv) > 5 else 10 ** 9)
    else:
        count()
