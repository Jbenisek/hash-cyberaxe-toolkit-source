#!/usr/bin/env python3
"""count-cost reviewer: the first-stage rule against the E3 side of every outcome, with an encoding of my own.

    python3 -B count-cost_sat.py [threads, default 3]          (WSL; cadical and kissat; no numpy)

Nothing of the package's tools or of research/r2_sat.py is imported. Constants are typed from the task text.
Read from the package: evidence/pairs_recount_830303cf.txt (the outcomes and their two factors) and, only for the
comparison at the end, evidence/rule_a_sat_830303cf_rule<n>.txt and blake3-r2/proof.md (the table of kept outcomes).

1. CNF of my own (Tseitin, ripple-carry adders with explicit majority carries, one variable that is true).
   Unknown words Y4, Y9, Y14, w8. E3 = G(Y3, Y4, Y9, Y14; 0, w8) is written out for message A (Y3) and message B
   (Y3'), all eight assignments. Constraints of an outcome (tau, eps), as Section 10 step 3 defines the E3 side:
   h1 XOR h1' = eta, f1 XOR f1' = tau XOR ROR(tau,1), e2 XOR e2' = eps, g2 XOR g2' = tau.
   Question "base": satisfiable? Question "violate": satisfiable with one clause more, "h1 fails a condition"?
   Every model is evaluated again with plain integers (and must also show the two output differences that a zero
   residual needs, ROR(beta XOR eps, 7) at d and ROR(tau, 8) at b, and e1 on the class mask).
   cadical answers everything; where cadical accepts --check, the "violate" questions run with its internal proof
   checker switched on. kissat repeats "violate" for the outcomes that cadical calls unsatisfiable.
2. A proof attempt without a solver. Every solution of the E3 side gives words (Y9, h1, h2) with
       g1 = Y9 + h1, g1' = Y9 + (h1 XOR eta), g1 XOR g1' = ROL(psi, 12),
       g2 = g1 + h2, g2' = g1' + (h2 XOR Q), g2 XOR g2' = tau,        Q = ROR(eta XOR eps, 8),
   because h2 XOR h2' = Q follows from the differences of h1 and e2. These five lines have no rotation, so whether
   they have a solution whose h1 violates the rule is decided exactly by a walk over the 32 bit positions with the
   four carries as state. If there is none, no solution of the outcome violates the rule: a proof for that
   outcome that needs no solver. The walk is compared with brute force for 5-bit words on random cases first.
Output: review/count-cost_sat_rule<n>.txt (one line per outcome) and at most ten summary lines.
"""
import random
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
M = 0xFFFFFFFF
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EVID = PKG / "evidence"
X3, X7, X11, X15, W4, W13 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006
IV2, IV6 = 0x3C6EF372, 0x1F83D9AB
ETA = 0x830303CF
CLASS_MASK, CLASS_VALUE = 0x03CF8303, 0x030C0303
RULES = {4: [(0x1, 0), (0x2, 1), (0x10000, 0), (0x20000, 0)]}
RULES[5] = RULES[4] + [(0xC, 1)]
RULES[6] = RULES[5] + [(0x180, 1)]


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def g_all(a, b, c, d, x, y):
    a1 = (a + b + x) & M; d1 = ror(d ^ a1, 16); c1 = (c + d1) & M; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


KK = (IV2 + IV6) & M
W4B = ((((KK + W4) & M) ^ 8) - KK) & M
PA, PB = g_all(X3, X7, X11, X15, W4, W13), g_all(X3, X7, X11, X15, W4B, W13)
Y3, Y3B, Y11, Y11B = PA[4], PB[4], PA[6], PB[6]
FACT_P = (PA[5] == PB[5] and PA[7] == PB[7] and (Y3, Y3B, Y11, Y11B) == (0x8127C181, 0x7EDF3E7E, 0x7AF77F38, 0x850000C3)
          and W4B == 0x97475640 and (W4 - W4B) & M == 0xFFFFFFF8 and (Y3B - Y3) & M == 0xFDB77CFD
          and (Y11B - Y11) & M == 0x0A08818B)


class Cnf:
    def __init__(self):
        self.n, self.T, self.cl = 1, 1, [[1]]

    def new(self):
        self.n += 1
        return self.n

    def word(self):
        return [self.new() for _ in range(32)]

    def const(self, v):
        return [self.T if v >> i & 1 else -self.T for i in range(32)]

    def xor(self, a, b):
        if abs(a) == self.T:
            return -b if a > 0 else b
        if abs(b) == self.T:
            return -a if b > 0 else a
        if a == b:
            return -self.T
        if a == -b:
            return self.T
        o = self.new()
        self.cl += [[-a, -b, -o], [a, b, -o], [a, -b, o], [-a, b, o]]
        return o

    def maj(self, a, b, c):
        o = self.new()
        self.cl += [[-a, -b, o], [-a, -c, o], [-b, -c, o], [a, b, -o], [a, c, -o], [b, c, -o]]
        return o

    def add(self, x, y):
        out, c = [], -self.T
        for i in range(32):
            out.append(self.xor(self.xor(x[i], y[i]), c))
            if i < 31:
                c = self.maj(x[i], y[i], c)
        return out

    def xorw(self, x, y):
        return [self.xor(a, b) for a, b in zip(x, y)]

    def text(self):
        return "p cnf %d %d\n" % (self.n, len(self.cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in self.cl)


def rot(w, n):
    """ROR of a word of literals: bit i of the result is bit i + n of w."""
    return [w[(i + n) % 32] for i in range(32)]


def build(tau, eps, rule=None):
    c = Cnf()
    y4, y9, y14, w8 = c.word(), c.word(), c.word(), c.word()
    sides = []
    for y3 in (Y3, Y3B):
        e1 = c.add(c.const(y3), y4)
        h1 = rot(c.xorw(y14, e1), 16)
        g1 = c.add(y9, h1)
        f1 = rot(c.xorw(y4, g1), 12)
        e2 = c.add(c.add(e1, f1), w8)
        h2 = rot(c.xorw(h1, e2), 8)
        g2 = c.add(g1, h2)
        sides.append((h1, f1, e2, g2))
    a, b = sides
    for k, want in enumerate((ETA, tau ^ ror(tau, 1), eps, tau)):
        for i in range(32):
            x = c.xor(a[k][i], b[k][i])
            c.cl.append([x if want >> i & 1 else -x])
    if rule is not None:
        lits = []
        for mask, value in rule:
            p = -c.T
            for i in range(32):
                if mask >> i & 1:
                    p = c.xor(p, a[0][i])
            lits.append(p if value == 0 else -p)
        c.cl.append(lits)
    return c, (y4, y9, y14, w8)


def e3(y3, y4, y9, y14, w8):
    e1 = (y3 + y4) & M; h1 = ror(y14 ^ e1, 16); g1 = (y9 + h1) & M; f1 = ror(y4 ^ g1, 12)
    e2 = (e1 + f1 + w8) & M; h2 = ror(h1 ^ e2, 8); g2 = (g1 + h2) & M; f2 = ror(f1 ^ g2, 7)
    return e1, h1, g1, f1, e2, h2, g2, f2


def plain(beta, tau, eps, y4, y9, y14, w8):
    a, b = e3(Y3, y4, y9, y14, w8), e3(Y3B, y4, y9, y14, w8)
    ok = ((a[1] ^ b[1]) == ETA and (a[3] ^ b[3]) == tau ^ ror(tau, 1) and (a[4] ^ b[4]) == eps and (a[6] ^ b[6]) == tau
          and (a[5] ^ b[5]) == ror(beta ^ eps, 7) and (a[7] ^ b[7]) == ror(tau, 8) and (a[0] & CLASS_MASK) == CLASS_VALUE)
    return ok, a[1]


def passes(h1, rule):
    return all(bin(h1 & m).count("1") & 1 == v for m, v in rule)


def solve(cmd, text):
    r = subprocess.run(cmd, input=text, capture_output=True, text=True, timeout=1200)
    ans, model = "?", set()
    for line in r.stdout.splitlines():
        if line.startswith("s "):
            ans = {"SATISFIABLE": "SAT", "UNSATISFIABLE": "UNSAT"}.get(line[2:].strip(), "?")
        elif line.startswith("v "):
            model.update(int(t) for t in line[2:].split() if int(t) > 0)
    return ans, model


def value(model, bits):
    return sum(1 << i for i, b in enumerate(bits) if b in model)


def job(args):
    key, n, cmd = args
    beta, tau, eps = key
    c, words = build(tau, eps, None if n == 0 else RULES[n])
    ans, model = solve(cmd, c.text())
    res = {"key": key, "n": n, "ans": ans}
    if ans == "SAT":
        vals = [value(model, w) for w in words]
        res["ok"], res["h1"] = plain(beta, tau, eps, *vals)
        res["vals"] = vals
    return res


def maj(a, b, c):
    return (a & b) | (a & c) | (b & c)


def walk(eta, p, q, tau, rule, w=32, second=True):
    """The five lines of the docstring on w-bit words: (has a solution, one that satisfies the rule, one that violates it)."""
    top = [max(i for i in range(w) if mask >> i & 1) for mask, _ in rule]
    states = {(0, 0, 0, 0, 0, 0)}
    for i in range(w):
        e, pi, qi, ti = eta >> i & 1, p >> i & 1, q >> i & 1, tau >> i & 1
        nxt = set()
        for c1, c1p, c2, c2p, viol, par in states:
            for y9 in (0, 1):
                for h in (0, 1):
                    hb = h ^ e
                    ga, gb = y9 ^ h ^ c1, y9 ^ hb ^ c1p
                    if ga ^ gb != pi:
                        continue
                    n1, n1p = maj(y9, h, c1), maj(y9, hb, c1p)
                    v, pr = viol, par
                    for k, (mask, val) in enumerate(rule):
                        if mask >> i & 1:
                            pr ^= h << k
                            if i == top[k]:
                                if (pr >> k & 1) != val:
                                    v = 1
                                pr &= ~(1 << k)
                    if not second:
                        nxt.add((n1, n1p, 0, 0, v, pr))
                        continue
                    for h2 in (0, 1):
                        h2b = h2 ^ qi
                        if ga ^ h2 ^ c2 ^ gb ^ h2b ^ c2p != ti:
                            continue
                        nxt.add((n1, n1p, maj(ga, h2, c2), maj(gb, h2b, c2p), v, pr))
        states = nxt
        if not states:
            break
    return bool(states), any(s[4] == 0 for s in states), any(s[4] == 1 for s in states)


def brute(eta, p, q, tau, rule, w, second=True):
    mask = (1 << w) - 1
    feas = sat = vio = False
    for y9 in range(1 << w):
        for h in range(1 << w):
            g1, g1b = (y9 + h) & mask, (y9 + (h ^ eta)) & mask
            if g1 ^ g1b != p:
                continue
            good = second is False or any(((g1 + h2) & mask) ^ ((g1b + (h2 ^ q)) & mask) == tau for h2 in range(1 << w))
            if good:
                feas = True
                if all(bin(h & m).count("1") & 1 == v for m, v in rule):
                    sat = True
                else:
                    vio = True
    return feas, sat, vio


def walk_selftest(cases=400, w=5):
    rng = random.Random(77106)
    same = feasible = with_violation = without = 0
    for case in range(cases):
        mask = (1 << w) - 1
        eta, q = rng.randrange(1 << w), rng.randrange(1 << w)
        if case % 4:
            y9, h, h2 = (rng.randrange(1 << w) for _ in range(3))
            g1, g1b = (y9 + h) & mask, (y9 + (h ^ eta)) & mask
            p, tau = g1 ^ g1b, ((g1 + h2) & mask) ^ ((g1b + (h2 ^ q)) & mask)
        else:
            p, tau = rng.randrange(1 << w), rng.randrange(1 << w)
        rule, used = [], 0
        for _ in range(rng.randrange(1, 4)):
            i = rng.randrange(w - 1)
            m = (3 << i) if rng.random() < 0.4 else (1 << i)
            if m & used:
                continue
            used |= m
            rule.append((m, rng.randrange(2)))
        second = case % 3 != 0
        a, b = walk(eta, p, q, tau, rule, w, second), brute(eta, p, q, tau, rule, w, second)
        same += int(a == b)
        feasible += int(b[0])
        with_violation += int(b[2])
        without += int(b[0] and not b[2])
    return cases, same, feasible, with_violation, without


def main():
    threads = min(int(sys.argv[1]) if len(sys.argv) > 1 else 3, 3)
    start = time.time()
    prod, sampled, order = {}, {}, []
    for line in (EVID / "pairs_recount_830303cf.txt").read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) > 2 and f[0] == "PAIR":
            sampled[int(f[2], 16)] = int(f[f.index("sampled") + 1])
        elif len(f) > 8 and f[0] == "OUTX":
            key = (int(f[2], 16), int(f[3], 16), int(f[4], 16))
            prod[key] = Fraction(int(f[6]) * int(f[8]), 2 ** 83)
            order.append(key)
    estimated = {b for b, n in sampled.items() if n}
    belongs = sum(int(eps ^ rol(beta ^ eps, 1) == ETA) for beta, tau, eps in order)
    cases, same, feasible, with_violation, without = walk_selftest()
    print(f"constants: Fact P and the differences of the task text hold {FACT_P}; outcomes {len(order)} in {len({k[0] for k in order})} betas, "
          f"eta = eps XOR ROL(beta XOR eps, 1) in {belongs}; betas with estimates {len(estimated)} ({sum(k[0] in estimated for k in order)} outcomes)")
    print(f"bit walk against brute force, 5-bit words: {same} of {cases} cases equal ({feasible} with a solution, {with_violation} with a "
          f"violating one, {without} with solutions and none violating)")
    probe = subprocess.run(["cadical", "-q", "--check"], input="p cnf 1 2\n1 0\n-1 0\n", capture_output=True, text=True)
    checked = probe.returncode == 20
    cad, cad_v = ["cadical", "-q"], ["cadical", "-q"] + (["--check"] if checked else [])
    jobs = [(k, 0, cad) for k in order] + [(k, n, cad_v) for n in (5, 4, 6) for k in order]
    with ThreadPoolExecutor(threads) as pool:
        res = list(pool.map(job, jobs))
    base = {r["key"]: r for r in res if r["n"] == 0}
    base_sat = sum(r["ans"] == "SAT" and r["ok"] for r in base.values())
    print(f"own CNF, cadical: base satisfiable with a model that holds in plain arithmetic {base_sat} of {len(base)}; "
          f"internal proof checker for the second question: {'on (--check)' if checked else 'NOT available'}")
    proof_text = (PKG / "blake3-r2" / "proof.md").read_text(encoding="ascii")
    all_good = FACT_P and same == cases and base_sat == len(base) and belongs == len(order)
    for n in (5, 4, 6):
        rule = RULES[n]
        vio = {r["key"]: r for r in res if r["n"] == n}
        unsat = [k for k in order if vio[k]["ans"] == "UNSAT"]
        sat_ok = sum(vio[k]["ans"] == "SAT" and vio[k]["ok"] and not passes(vio[k]["h1"], rule) for k in order)
        undecided = sum(vio[k]["ans"] == "?" for k in order)
        with ThreadPoolExecutor(threads) as pool:
            again = list(pool.map(job, [(k, n, ["kissat", "-q"]) for k in unsat]))
        kissat_unsat = sum(r["ans"] == "UNSAT" for r in again)
        pkg = {}
        for line in (EVID / f"rule_a_sat_830303cf_rule{n}.txt").read_text(encoding="ascii").split("\n"):
            f = line.split()
            if len(f) >= 5 and f[0] == "VIOLATE":
                pkg[(int(f[1], 16), int(f[2], 16), int(f[3], 16))] = f[4]
        equal = sum(pkg.get(k) == vio[k]["ans"] for k in order)
        kept = [k for k in unsat if k[0] not in estimated]
        count = sum(prod[k] for k in kept)
        full = sum(v for k, v in prod.items() if k[0] not in estimated)
        w1 = {k: walk(ETA, rol(k[1] ^ ror(k[1], 1), 12), ror(ETA ^ k[2], 8), k[1], rule, 32, False) for k in order}
        w2 = {k: walk(ETA, rol(k[1] ^ ror(k[1], 1), 12), ror(ETA ^ k[2], 8), k[1], rule, 32, True) for k in order}
        proved1 = [k for k in order if w1[k][0] and not w1[k][2]]
        proved2 = [k for k in order if w2[k][0] and not w2[k][2]]
        clash = [k for k in proved2 if vio[k]["ans"] != "UNSAT"] + [k for k in order if not w2[k][0]]
        proved_count = sum(prod[k] for k in proved2 if k[0] not in estimated)
        lines = [f"# count-cost_sat.py rule {n}: beta tau eps | base | violate (cadical{' --check' if checked else ''}) | package kissat | "
                 f"walk first addition alone: violating solution possible | walk both additions: violating solution possible | adds"]
        for k in order:
            lines.append(f"{k[0]:08x} {k[1]:08x} {k[2]:08x} | {base[k]['ans']} | {vio[k]['ans']} | {pkg.get(k, '-')} | {int(w1[k][2])} | "
                         f"{int(w2[k][2])} | {float(prod[k]):.4f}{' (beta with estimates)' if k[0] in estimated else ''}")
        (HERE / f"count-cost_sat_rule{n}.txt").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
        note = ""
        if n == 5:
            m = [l.split("|") for l in proof_text.split("The 54 outcomes that are kept")[1].split("| sum |")[0].split("\n") if l.startswith("| 1")]
            table = {(int(r[1], 16), int(r[2], 16), int(r[3], 16)) for r in m}
            note = f"; the proof's table of kept outcomes has {len(table)} lines, the same set as mine: {table == set(kept)}"
        print(f"RULE {n}: violate unsatisfiable {len(unsat)} (kissat on the same formulas: {kissat_unsat}), satisfiable with a checked violating model "
              f"{sat_ok}, undecided {undecided}; equal to the package's answers in {equal} of {len(order)}{note}")
        print(f"RULE {n}: conservative count from my answers {count.numerator} / {count.denominator} = {float(count):,.4f} "
              f"({100 * float(1 - count / full):.4f}% of {float(full):,.4f} left out); / 2^25 = {float(count) / 2 ** 25:.4f}, / 2^26 = {float(count) / 2 ** 26:.4f}")
        print(f"RULE {n}: proved without a solver (no violating solution of the two additions): {len(proved2)} outcomes, of them "
              f"{sum(k in set(unsat) for k in proved2)} among the {len(unsat)} unsatisfiable ones; by the first addition alone {len(proved1)}; "
              f"count of the outcomes proved this way {float(proved_count):,.4f}; contradictions with the solver {len(clash)}")
        all_good = all_good and undecided == 0 and equal == len(order) and not clash and kissat_unsat == len(unsat) and sat_ok == len(order) - len(unsat)
    print(f"RESULT: {'all of my answers agree with the package' if all_good else 'DIFFERENCES, see above'}; {time.time() - start:.0f} s")
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
