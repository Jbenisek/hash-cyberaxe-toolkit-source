#!/usr/bin/env python3
"""construction_drat.py -- independent reviewer, lens "construction", part (d): proofs for the 54 answers "no solution".

The count that H1 uses keeps 54 outcomes because solvers answered that the E3 system has no solution that violates
rule A. The package says these answers have no certificate. Here, for each of the 54:

  1. the reviewer's formula (construction_rule.build, question 2) is solved by cadical in plain mode (no
     preprocessing, so every learned clause follows by unit propagation) with a text DRAT proof;
  2. the proof is checked by a forward checker written here: every added clause must give a conflict by unit
     propagation from its negation (RUP), deletions are ignored (sound for RUP), and the empty clause must be reached;
  3. drat-trim is used as well if it is installed.

Before that the encoding itself is tested: for random inputs, unit propagation on the two G calls of the formula must
assign every variable and give the eight values of both calls as plain arithmetic does (so the formula excludes no true
execution on these inputs), and the three clauses of "h1 violates rule A" are checked on all 64 patterns of the six
bits. Runs in WSL: python3 -B construction_drat.py [workers=3] [minutes=8].
"""
import os
import random
import shutil
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import construction_rule as cr  # noqa: E402

SCRATCH = ('temporary-run-output'
           "02bea564-5721-488d-a971-a79b07bad0af/scratchpad/subagent/construction_drat")


class Checker:
    def __init__(self, nvars):
        self.val = [0] * (nvars + 1)
        self.watch = {}
        self.clauses = []
        self.trail = []
        self.qhead = 0
        self.dead = False

    def v(self, lit):
        return self.val[lit] if lit > 0 else -self.val[-lit]

    def enqueue(self, lit):
        self.val[abs(lit)] = 1 if lit > 0 else -1
        self.trail.append(lit)

    def propagate(self):
        val, clauses, watch = self.val, self.clauses, self.watch
        while self.qhead < len(self.trail):
            false_lit = -self.trail[self.qhead]
            self.qhead += 1
            ws = watch.get(false_lit)
            if not ws:
                continue
            i = j = 0
            n = len(ws)
            while i < n:
                ci = ws[i]
                i += 1
                c = clauses[ci]
                if c[0] == false_lit:
                    c[0], c[1] = c[1], c[0]
                first = c[0]
                x = val[first] if first > 0 else -val[-first]
                if x == 1:
                    ws[j] = ci
                    j += 1
                    continue
                for k in range(2, len(c)):
                    lk = c[k]
                    if (val[lk] if lk > 0 else -val[-lk]) != -1:
                        c[1], c[k] = lk, c[1]
                        watch.setdefault(lk, []).append(ci)
                        break
                else:
                    ws[j] = ci
                    j += 1
                    if x == -1:
                        while i < n:
                            ws[j] = ws[i]
                            j += 1
                            i += 1
                        del ws[j:]
                        return False
                    self.enqueue(first)
            del ws[j:]
        return True

    def add(self, lits):
        if self.dead:
            return
        c, seen = [], set()
        for lit in lits:
            if -lit in seen:
                return
            if lit not in seen:
                seen.add(lit)
                c.append(lit)
        c.sort(key=lambda lit: self.v(lit) == -1)
        nonfalse = sum(1 for lit in c if self.v(lit) != -1)
        if nonfalse == 0:
            self.dead = True
            return
        if len(c) >= 2:
            self.clauses.append(c)
            self.watch.setdefault(c[0], []).append(len(self.clauses) - 1)
            self.watch.setdefault(c[1], []).append(len(self.clauses) - 1)
        if nonfalse == 1 and self.v(c[0]) == 0:
            self.enqueue(c[0])
            if not self.propagate():
                self.dead = True

    def backtrack(self, t0):
        for lit in self.trail[t0:]:
            self.val[abs(lit)] = 0
        del self.trail[t0:]
        self.qhead = t0

    def rup(self, lits):
        if self.dead:
            return True
        t0 = len(self.trail)
        ok = False
        for lit in lits:
            x = self.v(lit)
            if x == 1:
                ok = True
                break
            if x == 0:
                self.enqueue(-lit)
        if not ok:
            ok = not self.propagate()
        self.backtrack(t0)
        return ok


def check_proof(text, proof_path, deadline):
    lines = text.split("\n")
    nvars = int(lines[0].split()[2])
    ck = Checker(nvars)
    for ln in lines[1:]:
        if ln:
            ck.add([int(t) for t in ln.split()[:-1]])
    lemmas = 0
    with open(proof_path, encoding="ascii") as f:
        for ln in f:
            if ck.dead:
                break
            t = ln.split()
            if not t or t[0] == "d":
                continue
            lits = [int(x) for x in t[:-1]]
            if any(abs(x) > nvars for x in lits):
                return "NOT VERIFIED (new variable)", lemmas
            lemmas += 1
            if not ck.rup(lits):
                return "NOT VERIFIED (a clause is not RUP)", lemmas
            ck.add(lits)
            if time.time() > deadline:
                return "TIMEOUT", lemmas
    return ("VERIFIED" if ck.dead else "NOT VERIFIED (no empty clause)"), lemmas


def encoding_test(samples, rng):
    f = cr.CNF()
    y4, y9, y14, w8 = f.word(), f.word(), f.word(), f.word()
    zero = f.const(0)
    a = f.g(f.const(cr.Y3), y4, y9, y14, zero, w8)
    b = f.g(f.const(cr.Y3P), y4, y9, y14, zero, w8)
    ck = Checker(f.n)
    for c in f.cl:
        ck.add(list(c))
    if ck.dead:
        return 0
    right = 0
    for _ in range(samples):
        vals = [rng.getrandbits(32) for _ in range(4)]
        t0 = len(ck.trail)
        for word, v in zip((y4, y9, y14, w8), vals):
            for i in range(32):
                ck.enqueue(word[i] if v >> i & 1 else -word[i])
        ok = ck.propagate()
        complete = all(x != 0 for x in ck.val[1:])
        got = [tuple(sum(1 << i for i in range(32) if ck.v(w[i]) == 1) for w in call) for call in (a, b)]
        want = [cr.g8(cr.Y3, vals[0], vals[1], vals[2], 0, vals[3]), cr.g8(cr.Y3P, vals[0], vals[1], vals[2], 0, vals[3])]
        right += bool(ok and complete and got == want)
        ck.backtrack(t0)
    return right


def violation_clauses_right():
    """The three clauses of question 2 on all 64 patterns of bits 0, 1, 2, 3, 16, 17 of h1."""
    right = 0
    for p in range(64):
        h = {0: p & 1, 1: p >> 1 & 1, 2: p >> 2 & 1, 3: p >> 3 & 1, 16: p >> 4 & 1, 17: p >> 5 & 1}
        h1 = sum(v << k for k, v in h.items())
        sat = any((not e or not h[2] or h[3]) and (not e or h[2] or not h[3])
                  and (h[0] or h[16] or h[17] or not h[1] or e) for e in (0, 1))
        right += sat == (not cr.rule_a(h1))
    return right


def job(args):
    beta, tau, eps, weight, deadline, idx = args
    if time.time() > deadline:
        return (beta, tau, eps, weight, "TIMEOUT (not started)", 0, None, 0.0)
    text, _ = cr.build(beta, tau, eps, True)
    cnf, proof = os.path.join(SCRATCH, "q%d.cnf" % idx), os.path.join(SCRATCH, "q%d.drat" % idx)
    with open(cnf, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    t0 = time.time()
    r = subprocess.run(["cadical", "--plain", "--no-binary", "-q", cnf, proof], capture_output=True, text=True)
    if "s UNSATISFIABLE" not in r.stdout:
        return (beta, tau, eps, weight, "solver did not answer UNSATISFIABLE in plain mode", 0, None, time.time() - t0)
    status, lemmas = check_proof(text, proof, deadline)
    trim = None
    if shutil.which("drat-trim"):
        d = subprocess.run(["drat-trim", cnf, proof], capture_output=True, text=True)
        trim = "s VERIFIED" in d.stdout
    for p in (cnf, proof):
        try:
            os.remove(p)
        except OSError:
            pass
    return (beta, tau, eps, weight, status, lemmas, trim, time.time() - t0)


def main():
    workers = min(3, int(sys.argv[1])) if len(sys.argv) > 1 else 3
    minutes = float(sys.argv[2]) if len(sys.argv) > 2 else 8.0
    start = time.time()
    deadline = start + 60 * minutes
    os.makedirs(SCRATCH, exist_ok=True)
    rng = random.Random(20261006)
    lines = ["construction_drat.py: DRAT proofs (cadical --plain, text) for the reviewer's formula of question 2, "
             "checked by the reviewer's forward RUP checker"]
    enc = encoding_test(300, rng)
    lines.append("ENCODING: unit propagation on the two G calls gives every variable and the 16 values of plain "
                 "arithmetic for %d of 300 random inputs; the three clauses of 'h1 violates rule A' are right on %d "
                 "of 64 bit patterns" % (enc, violation_clauses_right()))
    adds, est = {}, set()
    for line in open(os.path.join(PKG, "evidence", "pairs_recount_830303cf.txt"), encoding="ascii"):
        t = line.split()
        if t[:1] == ["PAIR"] and int(t[t.index("sampled") + 1]) > 0:
            est.add(t[2])
        if t[:1] == ["OUTX"]:
            adds[(t[2], t[3], t[4])] = Fraction(t[6]) * Fraction(t[8]) / 2 ** 83
    kept = []
    for line in open(os.path.join(PKG, "evidence", "rule_a_sat_830303cf_rule5.txt"), encoding="ascii"):
        t = line.split()
        if t[:1] == ["VIOLATE"] and t[4] == "UNSAT":
            kept.append((t[1], t[2], t[3]))
    kept.sort(key=lambda k: -adds[k])
    jobs = [(int(b, 16), int(t, 16), int(e, 16), float(adds[(b, t, e)]), deadline, i)
            for i, (b, t, e) in enumerate(kept)]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        results = list(pool.map(job, jobs))
    ok = [r for r in results if r[4] == "VERIFIED"]
    lines.append("PROOFS: kept outcomes %d (sum %.4f); proofs verified by the reviewer's checker %d, carrying %.4f "
                 "of the count that the claim uses; not verified %d; clauses checked in all %d; largest proof %d"
                 % (len(results), sum(r[3] for r in results), len(ok), sum(r[3] for r in ok),
                    len(results) - len(ok), sum(r[5] for r in results), max(r[5] for r in results)))
    trims = [r[6] for r in results if r[6] is not None]
    lines.append("PROOFS: drat-trim %s" % ("verified %d of %d" % (sum(trims), len(trims)) if trims
                                           else "is not installed; only the reviewer's checker was used"))
    bad = [r for r in results if r[4] != "VERIFIED"]
    for r in bad[:6]:
        lines.append("NOT VERIFIED %08x %08x %08x %.4f: %s after %d clauses" % (r[0], r[1], r[2], r[3], r[4], r[5]))
    lines.append("seconds %.0f, workers %d" % (time.time() - start, workers))
    with open(os.path.join(HERE, "construction_drat_out.txt"), "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
        for r in results:
            f.write("PROOF %08x %08x %08x adds %.4f %s clauses %d drat-trim %s seconds %.1f\n" % r)
    try:
        os.rmdir(SCRATCH)
    except OSError:
        pass
    print("\n".join(line[:400] for line in lines[1:]))


if __name__ == "__main__":
    main()
