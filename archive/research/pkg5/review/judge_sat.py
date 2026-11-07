#!/usr/bin/env python3
"""Hostile-judge lens: rule A against the E3 system of every outcome, with an encoder and a solver that are not
the package's. Read-only for the package; output review/judge_sat_<solver>.out. CPU only, at most 5 threads.

    python3 -B judge_sat.py cadical|cryptominisat5 [threads]

Written from proof.md alone (6.2, 6.3, Section 10 "How r is counted"): unknowns Y4, Y9, Y14, w8; E3 on message A is
G(Y3, Y4, Y9, Y14, 0, w8) and on message B is G(Y3', Y4, Y9, Y14, 0, w8). An outcome (beta, tau, eps) asks for
    h1 XOR h1' = eta                (Y4 in the class)
    g2 XOR g2' = tau                (c output of E3, residual word 1 against E1's a output)
    e2 XOR e2' = eps                (a output of E3, residual word 2 against E1's c output)
    f2 XOR f2' = ROR(tau, 8)        (b output of E3, residual word 3 against E1's d output)
    h2 XOR h2' = ROR(beta XOR eps, 7)   (d output of E3, residual word 4 against E1's b output)
This differs from the package's encoder in the unknown (Y14 instead of h1), in the conditions (the four output
differences of the residual instead of the differences of e1, g1, e2, g2) and in the adder clauses. Questions:
    base     the system                              expected SAT
    violate  the system AND h1 violates rule A       UNSAT means every solution of the outcome satisfies rule A
The outcomes are the OUTX lines of evidence/pairs_recount_e7c1815f.txt. Every model is evaluated in plain arithmetic.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
M = 0xFFFFFFFF
ETA, Y3, Y3B = 0xE7C1815F, 0x3F52EDA0, 0xC0AC125F


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rule_a(h):
    b = lambda i: h >> i & 1  # noqa: E731
    return b(16) == 1 and b(0) == b(1) and b(1) == b(2) and b(2) == b(3) and b(3) != b(4) and b(23) != b(24)


class Cnf:
    def __init__(self):
        self.n, self.cl = 1, [(1,)]          # variable 1 is the constant true

    def new(self):
        self.n += 1
        return self.n

    def word(self):
        return [self.new() for _ in range(32)]

    def const(self, v):
        return [1 if v >> i & 1 else -1 for i in range(32)]

    def xor(self, a, b):
        if abs(a) == 1:
            return b if a == -1 else -b
        if abs(b) == 1:
            return a if b == -1 else -a
        c = self.new()
        self.cl += [(-a, -b, -c), (a, b, -c), (a, -b, c), (-a, b, c)]
        return c

    def maj(self, a, b, c):
        m = self.new()
        self.cl += [(-a, -b, m), (-a, -c, m), (-b, -c, m), (a, b, -m), (a, c, -m), (b, c, -m)]
        return m

    def xorw(self, a, b):
        return [self.xor(x, y) for x, y in zip(a, b)]

    def add(self, a, b):
        out, carry = [], -1
        for x, y in zip(a, b):
            out.append(self.xor(self.xor(x, y), carry))
            carry = self.maj(x, y, carry)
        return out

    def fix(self, w, v):
        for i, bit in enumerate(w):
            self.cl.append((bit,) if v >> i & 1 else (-bit,))

    def text(self):
        return "p cnf %d %d\n" % (self.n, len(self.cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in self.cl)


def rorw(w, n):
    return [w[(i + n) % 32] for i in range(32)]


def build(beta, tau, eps, violate):
    c = Cnf()
    y4, y9, y14, w8 = c.word(), c.word(), c.word(), c.word()
    sides = []
    for a in (Y3, Y3B):
        e1 = c.add(c.const(a), y4)                 # w15 = 0
        h1 = rorw(c.xorw(y14, e1), 16)
        g1 = c.add(y9, h1)
        f1 = rorw(c.xorw(y4, g1), 12)
        e2 = c.add(c.add(e1, f1), w8)
        h2 = rorw(c.xorw(h1, e2), 8)
        g2 = c.add(g1, h2)
        f2 = rorw(c.xorw(f1, g2), 7)
        sides.append(dict(h1=h1, e2=e2, f2=f2, g2=g2, h2=h2))
    A, B = sides
    c.fix(c.xorw(A["h1"], B["h1"]), ETA)
    c.fix(c.xorw(A["g2"], B["g2"]), tau)
    c.fix(c.xorw(A["e2"], B["e2"]), eps)
    c.fix(c.xorw(A["f2"], B["f2"]), ror(tau, 8))
    c.fix(c.xorw(A["h2"], B["h2"]), ror(beta ^ eps, 7))
    if violate:
        h = A["h1"]
        c.cl.append((-h[16], c.xor(h[0], h[1]), c.xor(h[1], h[2]), c.xor(h[2], h[3]), -c.xor(h[3], h[4]), -c.xor(h[23], h[24])))
    return c, (y4, y9, y14, w8)


def plain(beta, tau, eps, y4, y9, y14, w8):
    res = []
    for a in (Y3, Y3B):
        e1 = (a + y4) & M; h1 = ror(y14 ^ e1, 16); g1 = (y9 + h1) & M; f1 = ror(y4 ^ g1, 12)
        e2 = (e1 + f1 + w8) & M; h2 = ror(h1 ^ e2, 8); g2 = (g1 + h2) & M; f2 = ror(f1 ^ g2, 7)
        res.append((h1, e2, f2, g2, h2))
    p, q = res
    ok = (p[0] ^ q[0] == ETA and p[3] ^ q[3] == tau and p[1] ^ q[1] == eps and p[2] ^ q[2] == ror(tau, 8)
          and p[4] ^ q[4] == ror(beta ^ eps, 7) and ((Y3 + y4) & 0x015FE7C1) == 0x00036181)
    return ok, p[0]


def solve(solver, text):
    cmd = {"cadical": ["cadical", "-q"], "cryptominisat5": ["cryptominisat5", "--verb", "0"]}[solver]
    r = subprocess.run(cmd, input=text, capture_output=True, text=True)
    status, model = "?", set()
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            status = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT"}.get(line[2:].strip(), "?")
        elif line.startswith("v "):
            model.update(int(t) for t in line[2:].split() if int(t) > 0)
    return status, model


def job(args):
    solver, mode, (beta, tau, eps) = args
    c, words = build(beta, tau, eps, mode == "violate")
    status, model = solve(solver, c.text())
    tail = ""
    if status == "SAT":
        vals = [sum(1 << i for i, b in enumerate(w) if b in model) for w in words]
        ok, h1 = plain(beta, tau, eps, *vals)
        tail = " solution %d rule_A %d h1 %08x" % (ok, rule_a(h1), h1)
    return "%s %08x %08x %08x %s%s" % (mode.upper(), beta, tau, eps, status, tail)


def main():
    solver = sys.argv[1]
    threads = min(int(sys.argv[2]) if len(sys.argv) > 2 else 5, 5)
    keys = []
    for line in (PKG / "evidence" / "pairs_recount_e7c1815f.txt").read_text().split("\n"):
        f = line.split()
        if f and f[0] == "OUTX":
            keys.append((int(f[2], 16), int(f[3], 16), int(f[4], 16)))
    jobs = [(solver, mode, k) for mode in ("base", "violate") for k in keys]
    with ThreadPoolExecutor(threads) as pool:
        lines = list(pool.map(job, jobs))
    theirs = {}
    for line in (PKG / "evidence" / "rule_a_sat_e7c1815f.txt").read_text().split("\n"):
        f = line.split()
        if f and f[0] == "VIOLATE":
            theirs[(f[1], f[2], f[3])] = f[4]
    mine = {tuple(l.split()[1:4]): l.split()[4] for l in lines if l.startswith("VIOLATE")}
    base = [l for l in lines if l.startswith("BASE")]
    vio = [l for l in lines if l.startswith("VIOLATE")]
    head = [
        "# judge_sat.py %s: %d outcomes" % (solver, len(keys)),
        "SUMMARY base: SAT %d, UNSAT %d, undecided %d; models that are solutions in plain arithmetic %d" % (
            sum(" SAT" in l for l in base), sum(" UNSAT" in l for l in base), sum(l.endswith("?") for l in base),
            sum("solution 1" in l for l in base)),
        "SUMMARY violate: UNSAT %d, SAT %d, undecided %d; SAT models that are solutions %d and violate rule A %d" % (
            sum(" UNSAT" in l for l in vio), sum(" SAT" in l for l in vio), sum(l.endswith("?") for l in vio),
            sum("solution 1" in l for l in vio), sum("solution 1 rule_A 0" in l for l in vio)),
        "SUMMARY against evidence/rule_a_sat_e7c1815f.txt: same outcomes %s, answers equal %d of %d, different %d" % (
            set(mine) == set(theirs), sum(mine[k] == theirs.get(k) for k in mine), len(mine),
            sum(mine[k] != theirs.get(k) for k in mine)),
    ]
    (PKG / "review" / ("judge_sat_%s.out" % solver)).write_text("\n".join(head + lines) + "\n", encoding="ascii")
    for h in head[1:]:
        print(h)


if __name__ == "__main__":
    main()
