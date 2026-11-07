#!/usr/bin/env python3
"""rule_drat_control_h8.py -- negative controls for the proof checker of rule_drat_h8.py.

Written by a reviewing helper agent of this package (lens "construction") as review/construction_drat_control.py and copied to
tools/rule_drat_control_h8.py by the agent that applied the review: the paths, the module names, the name of the output
file and this paragraph were changed, nothing else (SHA-256 of the reviewer's file, with LF line ends:
b69bdac716324bbc8acfa35b24c4720cb5526bed6392eeba713240ccaf068c37). Research helper, not submitted.

For three kept outcomes: the proof of the formula of question 2 must be accepted against that formula, and must be
rejected (a) against the same formula without the clause that says "h1 violates rule A" (that formula is satisfiable:
it is question 1), and (b) when the second half of the proof is cut off.
Runs in WSL: python3 -B tools/rule_drat_control_h8.py. Writes evidence/rule_drat_control_h8.txt.
"""
import os
import subprocess
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rule_drat_h8 as cd  # noqa: E402
import rule_formula3_h8 as cr  # noqa: E402

CASES = ((0x18b0e098, 0x285020a0, 0x6e21be55), (0x18b0e098, 0x385020a0, 0x6e21be55),
         (0x18d0e098, 0x285020a0, 0x6e61be55))


def main():
    os.makedirs(cd.SCRATCH, exist_ok=True)
    out = []
    for i, (beta, tau, eps) in enumerate(CASES):
        text, _ = cr.build(beta, tau, eps, True)
        cnf, proof, half = (os.path.join(cd.SCRATCH, "c%d.%s" % (i, x)) for x in ("cnf", "drat", "half"))
        with open(cnf, "w", encoding="ascii", newline="\n") as f:
            f.write(text)
        subprocess.run(["cadical", "--plain", "--no-binary", "-q", cnf, proof], capture_output=True, text=True)
        deadline = time.time() + 120
        full = cd.check_proof(text, proof, deadline)
        body = text.rstrip("\n").split("\n")
        head = body[0].split()
        weak = "p cnf %s %d\n" % (head[2], int(head[3]) - 1) + "\n".join(body[1:-1]) + "\n"   # without the last clause
        sat = cr.solve("kissat", weak)[0]
        against_weak = cd.check_proof(weak, proof, deadline)
        lemma_lines = open(proof, encoding="ascii").read().split("\n")
        with open(half, "w", encoding="ascii", newline="\n") as f:
            f.write("\n".join(lemma_lines[:len(lemma_lines) // 2]) + "\n")
        cut = cd.check_proof(text, half, deadline)
        out.append("%08x %08x %08x: proof against its formula: %s (%d clauses); last clause of the formula is '%s'; "
                   "formula without it is %s and the same proof against it: %s; first half of the proof: %s"
                   % (beta, tau, eps, full[0], full[1], body[-1], sat, against_weak[0], cut[0]))
        for p in (cnf, proof, half):
            os.remove(p)
    try:
        os.rmdir(cd.SCRATCH)
    except OSError:
        pass
    good = all("proof against its formula: VERIFIED" in o and "is SAT and the same proof against it: NOT VERIFIED" in o
               and "first half of the proof: NOT VERIFIED" in o for o in out)
    out.append("CONTROLS: %s" % ("checker accepts the right proof and rejects both wrong ones in all cases" if good
                                 else "UNEXPECTED, see above"))
    with open(os.path.join(cd.PKG, "evidence", "rule_drat_control_h8.txt"), "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(o[:330] for o in out))


if __name__ == "__main__":
    main()
