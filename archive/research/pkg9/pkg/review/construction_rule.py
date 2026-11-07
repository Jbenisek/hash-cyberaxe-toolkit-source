#!/usr/bin/env python3
"""construction_rule.py -- independent reviewer, lens "construction", part (d): rule A and the count that H1 uses.

Question: can a batch that stage A drops hide a collision that the count of the claim includes? The claim keeps 54
outcomes (beta, tau, eps) for which, it says, no solution of the E3 side violates rule A.

1. Reads the outcome list (evidence/pairs_recount_830303cf.txt), the package's solver file for five conditions and
   the table of kept outcomes printed in blake3-r2/proof.md; checks that the three agree, that no kept outcome lies in
   a beta that holds estimates, and adds the kept parts up as fractions.
2. Puts the two solver questions again with a formula of the reviewer's own, written from proof.md 3.3, 6.1 to 6.3
   alone: unknowns Y4, Y9, Y14, w8; E3 = G(Y3, Y4, Y9, Y14, 0, w8) for message A and G(Y3', ...) for message B as
   two complete G calls; Y4 in the class by the mask form of Lemma Q; and R = 0 written on the four OUTPUT
   differences of E3 that the E1 outcome forces: a: eps, c: tau, b: ROR(tau, 8), d: ROR(beta XOR eps, 7).
   Question 2 adds that h1 (second value of E3 on A) violates rule A as written in 6.3.
   Every model is evaluated again in plain arithmetic.

Runs in WSL: python3 -B construction_rule.py [workers=3]. Writes review/construction_rule_out.txt.
"""
import os
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
M = 0xFFFFFFFF
Y3, Y3P = 0x8127c181, 0x7edf3e7e
ETA, CMASK, CVALUE = 0x830303cf, 0x03cf8303, 0x030c0303


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def g8(A, B, C, D, x, y):
    a1 = (A + B + x) & M
    d1 = ror(D ^ a1, 16)
    c1 = (C + d1) & M
    b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M
    d2 = ror(d1 ^ a2, 8)
    c2 = (c1 + d2) & M
    b2 = ror(b1 ^ c2, 7)
    return (a1, d1, c1, b1, a2, d2, c2, b2)


def rule_a(h1):
    return (h1 & 1) == 0 and (h1 >> 16 & 1) == 0 and (h1 >> 17 & 1) == 0 and (h1 >> 1 & 1) == 1 \
        and (h1 >> 2 & 1) != (h1 >> 3 & 1)


class CNF:
    def __init__(self):
        self.n = 0
        self.cl = []

    def new(self):
        self.n += 1
        return self.n

    def word(self):
        return [self.new() for _ in range(32)]

    def const(self, v):
        w = self.word()
        for i in range(32):
            self.cl.append((w[i] if v >> i & 1 else -w[i],))
        return w

    def xor(self, a, b):
        out = self.word()
        for x, y, o in zip(a, b, out):
            self.cl += [(-x, -y, -o), (x, y, -o), (x, -y, o), (-x, y, o)]
        return out

    def add(self, a, b):
        out = self.word()
        c = None
        for i in range(32):
            x, y, o = a[i], b[i], out[i]
            if c is None:
                self.cl += [(-x, -y, -o), (x, y, -o), (x, -y, o), (-x, y, o)]
                c = self.new()
                self.cl += [(-x, -y, c), (x, -c), (y, -c)]
            else:
                for bx in (0, 1):
                    for by in (0, 1):
                        for bc in (0, 1):
                            self.cl.append((-x if bx else x, -y if by else y, -c if bc else c,
                                            o if (bx ^ by ^ bc) else -o))
                if i < 31:
                    cn = self.new()
                    self.cl += [(-x, -y, cn), (-x, -c, cn), (-y, -c, cn), (x, y, -cn), (x, c, -cn), (y, c, -cn)]
                    c = cn
        return out

    @staticmethod
    def ror(w, n):
        return [w[(i + n) % 32] for i in range(32)]

    def g(self, A, B, C, D, x, y):
        a1 = self.add(self.add(A, B), x)
        d1 = self.ror(self.xor(D, a1), 16)
        c1 = self.add(C, d1)
        b1 = self.ror(self.xor(B, c1), 12)
        a2 = self.add(self.add(a1, b1), y)
        d2 = self.ror(self.xor(d1, a2), 8)
        c2 = self.add(c1, d2)
        b2 = self.ror(self.xor(b1, c2), 7)
        return (a1, d1, c1, b1, a2, d2, c2, b2)

    def diff(self, a, b, v):
        for i in range(32):
            if v >> i & 1:
                self.cl += [(a[i], b[i]), (-a[i], -b[i])]
            else:
                self.cl += [(-a[i], b[i]), (a[i], -b[i])]

    def fix(self, a, mask, value):
        for i in range(32):
            if mask >> i & 1:
                self.cl.append((a[i] if value >> i & 1 else -a[i],))

    def text(self):
        return "p cnf %d %d\n" % (self.n, len(self.cl)) + "".join(" ".join(map(str, c)) + " 0\n" for c in self.cl)


def build(beta, tau, eps, violate):
    f = CNF()
    y4, y9, y14, w8 = f.word(), f.word(), f.word(), f.word()
    zero = f.const(0)
    a = f.g(f.const(Y3), y4, y9, y14, zero, w8)
    b = f.g(f.const(Y3P), y4, y9, y14, zero, w8)
    f.fix(a[0], CMASK, CVALUE)                 # Y4 in the class, Lemma Q: bits of e1 = Y3 + Y4
    f.diff(a[4], b[4], eps)                    # digest word 3: E3 a output against E1 c output
    f.diff(a[6], b[6], tau)                    # digest word 1: E3 c output against E1 a output
    f.diff(a[7], b[7], ror(tau, 8))            # digest word 4: E3 b output against E1 d output
    f.diff(a[5], b[5], ror(beta ^ eps, 7))     # digest word 6: E3 d output against E1 b output
    if violate:
        h = a[1]
        e = f.new()                            # e implies bit 2 = bit 3
        f.cl += [(-e, -h[2], h[3]), (-e, h[2], -h[3]), (h[0], h[16], h[17], -h[1], e)]
    return f.text(), (y4, y9, y14, w8)


def solve(solver, text):
    name = os.path.basename(solver)
    args = [solver, "-q"] + (["--time=600"] if name == "kissat" else ["-t", "600"])
    r = subprocess.run(args, input=text, capture_output=True, text=True)
    if "s SATISFIABLE" in r.stdout:
        true = set()
        for line in r.stdout.splitlines():
            if line.startswith("v"):
                true.update(int(t) for t in line.split()[1:] if int(t) > 0)
        return "SAT", true
    return ("UNSAT" if "s UNSATISFIABLE" in r.stdout else "UNKNOWN"), None


def value(word, true):
    return sum(1 << i for i, v in enumerate(word) if v in true)


def evaluate(beta, tau, eps, y4, y9, y14, w8):
    a, b = g8(Y3, y4, y9, y14, 0, w8), g8(Y3P, y4, y9, y14, 0, w8)
    outputs = ((a[4] ^ b[4]) == eps and (a[6] ^ b[6]) == tau and (a[7] ^ b[7]) == ror(tau, 8)
               and (a[5] ^ b[5]) == ror(beta ^ eps, 7))
    in_class = (a[1] ^ b[1]) == ETA                       # definition of the class: h1 xor h1' = eta
    interior = (a[3] ^ b[3]) == tau ^ ror(tau, 1)         # psi, the form of "How r is counted"
    return outputs and in_class, interior, rule_a(a[1]), a[1]


def one(job):
    kissat, cadical, beta, tau, eps, kept = job
    out = {"key": (beta, tau, eps)}
    text, words = build(beta, tau, eps, False)
    st, true = solve(kissat, text)
    out["base"] = st
    if st == "SAT":
        vals = [value(w, true) for w in words]
        out["base_eval"] = evaluate(beta, tau, eps, *vals)
    text, words = build(beta, tau, eps, True)
    st, true = solve(kissat, text)
    out["violate"] = st
    if st == "SAT":
        vals = [value(w, true) for w in words]
        out["violate_eval"] = evaluate(beta, tau, eps, *vals)
        out["violate_model"] = vals
    if kept and cadical:
        out["violate_cadical"] = solve(cadical, text)[0]
    return out


def main():
    workers = min(3, int(sys.argv[1])) if len(sys.argv) > 1 else 3
    lines = []
    # ---- 1. the files
    est, adds, order = set(), {}, []
    for line in open(os.path.join(PKG, "evidence", "pairs_recount_830303cf.txt"), encoding="ascii"):
        t = line.split()
        if t[:1] == ["PAIR"] and int(t[t.index("sampled") + 1]) > 0:
            est.add(t[2])
        if t[:1] == ["OUTX"]:
            key = (t[2], t[3], t[4])
            adds[key] = Fraction(t[6]) * Fraction(t[8]) / 2 ** 83
            order.append(key)
    pk_base, pk_viol = {}, {}
    for line in open(os.path.join(PKG, "evidence", "rule_a_sat_830303cf_rule5.txt"), encoding="ascii"):
        t = line.split()
        if t[:1] == ["ALL"]:
            pk_base[(t[1], t[2], t[3])] = t[4]
        if t[:1] == ["VIOLATE"]:
            pk_viol[(t[1], t[2], t[3])] = t[4]
    proof_kept, inside = {}, False
    for line in open(os.path.join(PKG, "blake3-r2", "proof.md"), encoding="ascii"):
        if line.startswith("| beta | tau | eps | Adds |"):
            inside = True
        elif inside and line.startswith("| sum"):
            inside = False
        elif inside and not line.startswith("| ---"):
            t = [c.strip() for c in line.strip().strip("|").split("|")]
            proof_kept[(t[0], t[1], t[2])] = t[3]
    kept_pkg = {k for k, v in pk_viol.items() if v == "UNSAT"}
    total = sum(adds.values())
    kept_sum = sum(adds[k] for k in kept_pkg if k[0] not in est)
    lines.append("FILES: outcomes %d in %d betas; betas with estimates %d (%d outcomes, %.6f); package solver file: "
                 "base %d, second question %d, UNSAT %d" % (
                     len(adds), len({k[0] for k in adds}), len(est), sum(k[0] in est for k in adds),
                     float(sum(v for k, v in adds.items() if k[0] in est)), len(pk_base), len(pk_viol), len(kept_pkg)))
    lines.append("FILES: sum of all outcomes %.4f; kept outcomes in betas with estimates: %d; sum of the kept "
                 "outcomes %s = %.4f; equals 135295336110358535/1073741824: %s" % (
                     float(total), sum(k[0] in est for k in kept_pkg), kept_sum, float(kept_sum),
                     kept_sum == Fraction(135295336110358535, 1073741824)))
    rounded = all(abs(float(adds[k]) - float(v.replace(",", ""))) < 0.00006 for k, v in proof_kept.items()
                  if k in adds)
    lines.append("FILES: kept table of proof.md has %d rows; same set as the package's 54 UNSAT answers: %s; every "
                 "printed 'Adds' equals E1*N3/2^83 to the printed digits: %s; same outcome set in all three files: %s"
                 % (len(proof_kept), set(proof_kept) == kept_pkg, rounded,
                    set(adds) == set(pk_base) == set(pk_viol)))
    # (tau, eps) fixes the E3 side: the same pair under two betas must not get two answers in the package's file
    by_pair = {}
    for k, v in pk_viol.items():
        by_pair.setdefault(k[1:], set()).add(v.split()[0])
    lines.append("FILES: distinct pairs (tau, eps) %d; pairs with two different answers in the package's file: %d"
                 % (len(by_pair), sum(len(v) > 1 for v in by_pair.values())))
    # ---- 2. the reviewer's formula
    kissat = shutil.which("kissat") or os.path.expanduser("~/hashsmash/bin/kissat")
    cadical = shutil.which("cadical")
    if not (kissat and os.path.exists(kissat)):
        lines.append("SOLVER: kissat not found; part 2 not run")
        results = []
    else:
        t0 = time.time()
        jobs = [(kissat, cadical, int(b, 16), int(t, 16), int(e, 16), (b, t, e) in kept_pkg) for b, t, e in order]
        with ThreadPoolExecutor(max_workers=workers) as pool:
            results = list(pool.map(one, jobs))
        secs = time.time() - t0
        base_sat = sum(r["base"] == "SAT" for r in results)
        base_ok = sum(r.get("base_eval", (False,))[0] for r in results)
        interior = sum(r["base_eval"][1] for r in results if "base_eval" in r) + \
            sum(r["violate_eval"][1] for r in results if "violate_eval" in r)
        models = sum("base_eval" in r for r in results) + sum("violate_eval" in r for r in results)
        v_unsat = [r for r in results if r["violate"] == "UNSAT"]
        v_sat = [r for r in results if r["violate"] == "SAT"]
        v_unknown = [r for r in results if r["violate"] == "UNKNOWN"]
        v_ok = sum(r["violate_eval"][0] and not r["violate_eval"][2] for r in v_sat)
        mine = {("%08x" % r["key"][0], "%08x" % r["key"][1], "%08x" % r["key"][2]): r["violate"] for r in results}
        agree = sum(mine[k] == pk_viol[k].split()[0] for k in mine)
        my_kept = {k for k, v in mine.items() if v == "UNSAT"}
        lines.append("SAT (reviewer's formula, kissat, %d workers, %.0f s): base satisfiable %d of %d, models that "
                     "are solutions with Y4 in the class %d, base models that satisfy rule A %d" % (
                         workers, secs, base_sat, len(results), base_ok,
                         sum(r["base_eval"][2] for r in results if "base_eval" in r)))
        lines.append("SAT second question (system AND h1 violates rule A): UNSAT %d, SAT %d (models that are "
                     "solutions and violate rule A: %d), undecided %d; answers equal to the package's: %d of %d; "
                     "reviewer's kept set = package's kept set: %s" % (
                         len(v_unsat), len(v_sat), v_ok, len(v_unknown), agree, len(mine), my_kept == kept_pkg))
        lines.append("SAT: models in which the interior difference psi = tau xor ROR(tau,1) holds: %d of %d "
                     "(output form of the reviewer = interior form of the text on every model)" % (interior, models))
        if cadical:
            cad = [r.get("violate_cadical") for r in results if "violate_cadical" in r]
            lines.append("SAT: cadical on the reviewer's second question for the package's kept outcomes: UNSAT %d "
                         "of %d" % (cad.count("UNSAT"), len(cad)))
        else:
            lines.append("SAT: cadical not on the path; only kissat was used")
        kept_mine = sum(adds[k] for k in my_kept if k[0] not in est)
        lines.append("SAT: sum of the outcomes without a violating solution by the reviewer's answers, betas with "
                     "estimates left out: %.4f" % float(kept_mine))
    with open(os.path.join(HERE, "construction_rule_out.txt"), "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
        for r in results:
            f.write("OUT %08x %08x %08x base %s violate %s%s%s\n" % (
                r["key"] + (r["base"], r["violate"],
                            " cadical " + r["violate_cadical"] if "violate_cadical" in r else "",
                            " model Y4 %08x Y9 %08x Y14 %08x w8 %08x h1 %08x" % (
                                tuple(r["violate_model"]) + (r["violate_eval"][3],))
                            if "violate_model" in r else "")))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
