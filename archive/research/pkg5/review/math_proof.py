#!/usr/bin/env python3
"""Reviewer check, lens MATHEMATICS AND COST, part (a): certificates for the answers "no solution violates rule A".

For every outcome that math_sat_violate_cadical.txt lists as UNSAT, the CNF of math_sat.py (system AND rule A
violated) is written again and

  1. cadical --check --checkproof=3 solves it with its internal DRAT and LRAT checkers switched on
     (exit status 20 = unsatisfiable, and no checker abort);
  2. cadical --plain writes a text DRAT proof (no preprocessing, so every lemma is a learned clause), and the
     forward RUP checker BELOW, written for this review, checks every lemma of that proof by unit propagation
     and that the empty clause follows. Deletion lines are ignored (that can only make a wrong lemma harder to
     reject never easier to accept... it keeps more clauses, all of them implied, so the check stays sound).

    math_proof.py THREADS [LIMIT]      -> review/math_proof.txt
"""
import os
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import math_sat as ms  # noqa: E402

TMP = Path(os.path.expanduser("~/hashsmash/pkg5-review-math/proof"))


class Rup:
    """Forward RUP checker with two watched literals. Top-level assignments are permanent."""

    def __init__(self, n):
        self.val = bytearray(2 * n + 2)
        self.watch = [[] for _ in range(2 * n + 2)]
        self.db, self.trail, self.refuted = [], [], False

    @staticmethod
    def ix(l):
        return 2 * l if l > 0 else 1 - 2 * l

    def propagate(self, q):
        val, ix, db, trail, watch = self.val, self.ix, self.db, self.trail, self.watch
        while q < len(trail):
            fl = -trail[q]
            q += 1
            ws = watch[ix(fl)]
            i = 0
            while i < len(ws):
                cl = db[ws[i]]
                if cl[0] == fl:
                    cl[0], cl[1] = cl[1], cl[0]
                if val[ix(cl[0])]:
                    i += 1
                    continue
                for k in range(2, len(cl)):
                    if not val[ix(-cl[k])]:
                        cl[1], cl[k] = cl[k], cl[1]
                        watch[ix(cl[1])].append(ws[i])
                        ws[i] = ws[-1]
                        ws.pop()
                        break
                else:
                    if val[ix(-cl[0])]:
                        return True
                    val[ix(cl[0])] = 1
                    trail.append(cl[0])
                    i += 1
        return False

    def add(self, clause):
        """Add a clause at top level (simplified by the permanent assignment)."""
        if self.refuted:
            return
        val, ix = self.val, self.ix
        lits = []
        for l in dict.fromkeys(clause):
            if val[ix(l)]:
                return
            if not val[ix(-l)]:
                lits.append(l)
        if any(-l in lits for l in lits):
            return
        if not lits:
            self.refuted = True
        elif len(lits) == 1:
            val[ix(lits[0])] = 1
            self.trail.append(lits[0])
            self.refuted = self.propagate(len(self.trail) - 1)
        else:
            self.db.append(lits)
            self.watch[ix(lits[0])].append(len(self.db) - 1)
            self.watch[ix(lits[1])].append(len(self.db) - 1)

    def implied(self, lemma):
        """Is the lemma a RUP consequence of the clauses so far?"""
        if self.refuted:
            return True
        val, ix, top = self.val, self.ix, len(self.trail)
        conflict = False
        for l in lemma:
            if val[ix(l)]:
                conflict = True
                break
            if not val[ix(-l)]:
                val[ix(-l)] = 1
                self.trail.append(-l)
        conflict = conflict or self.propagate(top)
        for l in self.trail[top:]:
            val[ix(l)] = 0
        del self.trail[top:]
        return conflict


def one(key):
    beta, tau, eps = key
    c, _ = ms.build(beta, tau, eps, "violate")
    stem = TMP / ("%08x_%08x_%08x" % key)
    cnf, proof = str(stem) + ".cnf", str(stem) + ".drat"
    c.write(cnf)
    r1 = subprocess.run(["cadical", "--check", "--checkproof=3", "-q", cnf], capture_output=True, text=True)
    r2 = subprocess.run(["cadical", "--plain", "--no-binary", "-q", cnf, proof], capture_output=True, text=True)
    lemmas = []
    if r2.returncode == 20:
        with open(proof, encoding="ascii") as f:
            for line in f:
                t = line.split()
                if t and t[0] != "d":
                    lemmas.append([int(x) for x in t[:-1]])
    rup = Rup(c.n)
    for cl in c.cl:
        rup.add(cl)
    by_propagation = rup.refuted
    bad = used = 0
    for lemma in lemmas:
        if rup.refuted:
            break
        used += 1
        if not rup.implied(lemma):
            bad += 1
            continue                      # a lemma that is not RUP is NOT added
        rup.add(lemma)
    if not rup.refuted and rup.implied([]):
        rup.refuted = True
    # control: the same proof against the formula WITHOUT its last clause ("rule A violated"). That formula is
    # satisfiable (math_sat_all_cadical.txt), so a sound checker must not refute it.
    ctl = Rup(c.n)
    for cl in c.cl[:-1]:
        ctl.add(cl)
    ctl_bad = 0
    for lemma in lemmas:
        if ctl.refuted:
            break
        if not ctl.implied(lemma):
            ctl_bad += 1
            continue
        ctl.add(lemma)
    for p in (cnf, proof):
        try:
            os.unlink(p)
        except OSError:
            pass
    return ("PROOF %08x %08x %08x cadical_checked_exit %d checker_abort %d plain_exit %d lemmas %d not_rup %d refuted_by_my_checker %d "
            "by_unit_propagation_alone %d lemmas_used %d control_refuted %d control_not_rup %d" % (
                beta, tau, eps, r1.returncode, int("atal" in r1.stderr or "atal" in r1.stdout), r2.returncode, len(lemmas), bad,
                int(rup.refuted), int(by_propagation), used, int(ctl.refuted), ctl_bad))


def main():
    threads = int(sys.argv[1])
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
    TMP.mkdir(parents=True, exist_ok=True)
    keys = []
    for l in (HERE / "math_sat_violate_cadical.txt").read_text(encoding="ascii").splitlines():
        f = l.split()
        if f[4] == "UNSAT":
            keys.append((int(f[1], 16), int(f[2], 16), int(f[3], 16)))
    keys = keys[:limit]
    with ProcessPoolExecutor(threads) as pool:
        lines = list(pool.map(one, keys))
    (HERE / "math_proof.txt").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    f = [l.split() for l in lines]
    print("outcomes %d; cadical with internal proof checking: exit 20 for %d, checker aborts %d; plain proofs: exit 20 for %d, "
          "lemmas %d in all (largest %d), lemmas that are not RUP %d; refuted by my checker %d, of them by unit propagation alone %d; "
          "lemmas read until the refutation %d (largest %d); control (satisfiable formula, same proof): refuted %d, lemmas rejected %d" % (
              len(f), sum(x[5] == "20" for x in f), sum(x[7] == "1" for x in f), sum(x[9] == "20" for x in f),
              sum(int(x[11]) for x in f), max(int(x[11]) for x in f), sum(int(x[13]) for x in f), sum(x[15] == "1" for x in f),
              sum(x[17] == "1" for x in f), sum(int(x[19]) for x in f), max(int(x[19]) for x in f), sum(x[21] == "1" for x in f),
              sum(int(x[23]) for x in f)))


if __name__ == "__main__":
    main()
