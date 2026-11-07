#!/usr/bin/env python3
"""A first-stage rule against the E3 system of every outcome, with a second encoder and other solvers than
tools/rule_a_sat.py. Research helper of the sixth package, not submitted. CPU only, at most 4 threads.

    python3 -B tools/rule_a_sat2.py RULE cadical|cryptominisat5 [threads, default 3]     RULE: 4, 5 or 6

Output evidence/rule_a_sat2_<solver>_<eta>_rule<RULE>.txt, read by tools/pkg6_data.py.

Origin. The encoder was written by a reviewing helper agent of the fifth package (lens: a hostile judge) from the
proof text of that package alone. For this package the author of the text changed three things in it and nothing
else: the constants (eta, Y3, Y3' and the class mask and value are taken from tools/pkg6_data.py), the rule (any of
the rules of pkg6_data.RULES, each condition being the XOR of one or two bits of h1 with a wanted value) and the
names of the files. It is therefore a second formula and other solvers, not a review by an independent party.

The formula: unknowns Y4, Y9, Y14, w8; E3 on message A is G(Y3, Y4, Y9, Y14, 0, w8) and on message B is
G(Y3', Y4, Y9, Y14, 0, w8). An outcome (beta, tau, eps) asks for
    h1 XOR h1' = eta                (Y4 in the class)
    g2 XOR g2' = tau                (c output of E3, residual word 1 against E1's a output)
    e2 XOR e2' = eps                (a output of E3, residual word 2 against E1's c output)
    f2 XOR f2' = ROR(tau, 8)        (b output of E3, residual word 3 against E1's d output)
    h2 XOR h2' = ROR(beta XOR eps, 7)   (d output of E3, residual word 4 against E1's b output)
This differs from the encoder of tools/rule_a_sat.py in the unknown (Y14 instead of h1), in the conditions (the
four output differences of the residual instead of the differences of e1, g1, e2, g2) and in the adder clauses.
Questions:
    base     the system                              expected SAT
    violate  the system AND h1 violates the rule     UNSAT means every solution of the outcome satisfies the rule
The outcomes are the OUTX lines of evidence/pairs_recount_<eta>.txt. Every model is evaluated in plain arithmetic.
"""
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
sys.path.insert(0, str(TOOLS))
import pkg6_data as data  # noqa: E402

M = 0xFFFFFFFF
if len(sys.argv) < 3 or not sys.argv[1].isdecimal() or int(sys.argv[1]) not in data.RULES or sys.argv[2] not in ("cadical", "cryptominisat5"):
    raise SystemExit("usage: rule_a_sat2.py RULE cadical|cryptominisat5 [threads]")
N_RULE, SOLVER = int(sys.argv[1]), sys.argv[2]
RULE = data.RULES[N_RULE]
D = data.derive()
ETA, Y3, Y3B, CMASK, CVALUE = data.ETA, D["Y3"], D["Y3B"], D["qmask"], D["qvalue"]
SOURCE = PKG / "evidence" / f"pairs_recount_{ETA:08x}.txt"
FIRST = PKG / "evidence" / f"rule_a_sat_{ETA:08x}_rule{N_RULE}.txt"


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rule_a(h):
    return all(bin(h & mask).count("1") & 1 == value for mask, value in RULE)


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
    if violate:                                    # one clause: some condition of the rule fails
        h, clause = A["h1"], []
        for mask, value in RULE:
            x = -1                                 # the constant false
            for i in range(32):
                if mask >> i & 1:
                    x = c.xor(x, h[i])
            clause.append(x if value == 0 else -x)
        c.cl.append(tuple(clause))
    return c, (y4, y9, y14, w8)


def plain(beta, tau, eps, y4, y9, y14, w8):
    res = []
    for a in (Y3, Y3B):
        e1 = (a + y4) & M; h1 = ror(y14 ^ e1, 16); g1 = (y9 + h1) & M; f1 = ror(y4 ^ g1, 12)
        e2 = (e1 + f1 + w8) & M; h2 = ror(h1 ^ e2, 8); g2 = (g1 + h2) & M; f2 = ror(f1 ^ g2, 7)
        res.append((h1, e2, f2, g2, h2))
    p, q = res
    ok = (p[0] ^ q[0] == ETA and p[3] ^ q[3] == tau and p[1] ^ q[1] == eps and p[2] ^ q[2] == ror(tau, 8)
          and p[4] ^ q[4] == ror(beta ^ eps, 7) and ((Y3 + y4) & CMASK) == CVALUE)
    return ok, p[0]


def solve(text):
    cmd = {"cadical": ["cadical", "-q"], "cryptominisat5": ["cryptominisat5", "--verb", "0"]}[SOLVER]
    r = subprocess.run(cmd, input=text, capture_output=True, text=True)
    status, model = "?", set()
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            status = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT"}.get(line[2:].strip(), "?")
        elif line.startswith("v "):
            model.update(int(t) for t in line[2:].split() if int(t) > 0)
    return status, model


def job(args):
    mode, (beta, tau, eps) = args
    c, words = build(beta, tau, eps, mode == "violate")
    status, model = solve(c.text())
    tail = ""
    if status == "SAT":
        vals = [sum(1 << i for i, b in enumerate(w) if b in model) for w in words]
        ok, h1 = plain(beta, tau, eps, *vals)
        tail = " solution %d rule_A %d h1 %08x" % (ok, rule_a(h1), h1)
    return "%s %08x %08x %08x %s%s" % (mode.upper(), beta, tau, eps, status, tail)


def main():
    threads = min(int(sys.argv[3]) if len(sys.argv) > 3 else 3, 4)
    keys = []
    for line in SOURCE.read_text().split("\n"):
        f = line.split()
        if f and f[0] == "OUTX":
            keys.append((int(f[2], 16), int(f[3], 16), int(f[4], 16)))
    jobs = [(mode, k) for mode in ("base", "violate") for k in keys]
    with ThreadPoolExecutor(threads) as pool:
        lines = list(pool.map(job, jobs))
    theirs = {}
    for line in FIRST.read_text().split("\n"):
        f = line.split()
        if f and f[0] == "VIOLATE":
            theirs[(f[1], f[2], f[3])] = f[4]
    mine = {tuple(l.split()[1:4]): l.split()[4] for l in lines if l.startswith("VIOLATE")}
    base = [l for l in lines if l.startswith("BASE")]
    vio = [l for l in lines if l.startswith("VIOLATE")]
    version = subprocess.run([SOLVER, "--version"], capture_output=True, text=True).stdout.strip().split("\n")[0][:80]
    head = [
        "# rule_a_sat2.py %d %s: %d outcomes" % (N_RULE, SOLVER, len(keys)),
        "# solver version: %s" % version,
        "# constants: eta %08x Y3 %08x Y3' %08x class mask %08x value %08x; the rule with %d conditions on h1 (mask:value): %s" % (
            ETA, Y3, Y3B, CMASK, CVALUE, N_RULE, ",".join("%08x:%d" % c for c in RULE)),
        "SUMMARY base: SAT %d, UNSAT %d, undecided %d; models that are solutions in plain arithmetic %d" % (
            sum(" SAT" in l for l in base), sum(" UNSAT" in l for l in base), sum(l.endswith("?") for l in base),
            sum("solution 1" in l for l in base)),
        "SUMMARY violate: UNSAT %d, SAT %d, undecided %d; SAT models that are solutions %d and violate the rule %d" % (
            sum(" UNSAT" in l for l in vio), sum(" SAT" in l for l in vio), sum(l.endswith("?") for l in vio),
            sum("solution 1" in l for l in vio), sum("solution 1 rule_A 0" in l for l in vio)),
        "SUMMARY against evidence/%s: same outcomes %s, answers equal %d of %d, different %d" % (
            FIRST.name, set(mine) == set(theirs), sum(mine[k] == theirs.get(k) for k in mine), len(mine),
            sum(mine[k] != theirs.get(k) for k in mine)),
    ]
    (PKG / "evidence" / ("rule_a_sat2_%s_%08x_rule%d.txt" % (SOLVER, ETA, N_RULE))).write_text("\n".join(head + lines) + "\n", encoding="ascii")
    for h in head[3:]:
        print(h[:230])


if __name__ == "__main__":
    main()
