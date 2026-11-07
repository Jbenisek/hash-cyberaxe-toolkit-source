"""The sweep: statements that the merged program and the new budgets made false. Exact-once replacements."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
K = _hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/pkg/')
PROOF, NOTE = K + "blake3-r2/proof.md", K + "submission-note-r2.md"
OLD_PROG = (
"*The program that executes and counts the procedure.* The program of this package\n"
"counts stage A and stage 2 (6.5) and does not contain the neighbour path. A helper\n")
P = [
 ("that set the cost of a trial. The program the organizer runs also contains the\nfour counted pieces of the search (outer step, table build, middle step, packed\ntwo-stage batch), a machine that counts their operations, loads and stores, and\na self-test of that count (Section 6.5).",
  "that set the cost of a trial. The program the organizer runs also contains the\ncounted pieces of the search (outer step, table build, middle step, packed\ntwo-stage batch, and the neighbour path of 6.7 with its budgets), a machine that\ncounts their operations, loads and stores, and self-tests of those counts\n(Sections 6.5 and 10)."),
 ("experiments, experiments/halfsearch.py, contains the four pieces and the\nmachine that counts them,",
  "experiments, experiments/halfsearch.py, contains the four pieces, the\nneighbour path of 6.7 with its budgets, and the machine that counts them,"),
 ("- The cluster layout, seven planes of 133,413 words in the other model's audit,\n  is about eight times the five lists and table of 6.4, about 30 megabytes,",
  "- The cluster layout, seven planes of 149,797 words, is about eight times the\n  five lists and table of 6.4, about 34 megabytes,"),
 ("the count; the form of its three heuristics H1, H2 and H3 and of the two\nbudgets (H4 and H5 are new and are listed below);",
  "the count; the form of its three heuristics H1, H2 and H3 and of the two\nbudgets (H4, H5 and H6 and the budgets of the neighbour path are new);"),
 ("collisions; the neighbour path added to a copy of the program with its\n  machine counts and its self-test;",
  "collisions; the neighbour path, first added to a copy of the program and now\n  merged into the submitted program, with its machine counts and self-test;"),
]
N = [
 ("and the neighbour path added to a copy of the program, with its machine\n  counts and its self-test.",
  "and the neighbour path, first added to a copy of the program and now merged\n  into the submitted program, with its machine counts and its self-test."),
]
NEW_PROG = """*The program that executes and counts the procedure.* The submitted program
counts stage A and stage 2 (6.5) and the neighbour path of 6.7 with its four
budgets. A helper agent first wrote the path below the program's own code; it is
now part of the submitted program. The self-test of 6.5 gives byte-identical
output (2,000 cases, 14,000 of 14,000 lanes right, stage A 47, stage 2 135, 16
registers), and so do both declared experiments. A self-test of the neighbour
path, `--cluster-selftest 50000 1`, checks it against the program's own 2-round
compression of the real messages on 50,304 trials in 786 clusters: h1 built from
z equals the reference in 50,304 of 50,304 and so does every decision of rule A;
the gate agrees with the four conditions on the reference h1 in 786 of 786
clusters; clearing the six bits returns the representative in 49,518 of 49,518
neighbours; all 786 clusters hold 64 distinct trials. The whole path ran on the
machine for 62 representative words: 434 of 434 representative and gate lanes
right, 62 of 62 dispatches, 386 of 386 clusters right, and **24,318 of 24,318
neighbour lanes** right against both real messages and their digests. Every
piece runs within the 16 registers (representative word 16, neighbour word 16,
cluster entry 15, dispatch 14, gate test 13), and a budget test halts the run
when its count reaches the budget. A neighbour word costs the same as a
representative word, stage A 47 and stage 2 135, although its lanes may carry
two values of X2, because the words of X2 the batch reads are loaded per word
and not kept in registers. The charge of Section 8, 1.65 per trial-equivalent,
is an upper bound that includes the routing of representative word, gate,
dispatch, neighbour words and both stages through the 16 registers. The lists
of the cluster layout hold 149,797 words each against the 18,725 of 6.4, about
eight times the memory, and their cost per trial is below 2 * 10^-6 operations.
"""
t = open(PROOF, encoding="utf-8", newline="\n").read(); n = open(NOTE, encoding="utf-8", newline="\n").read(); bad = []
s = t.find(OLD_PROG)
e = t.find("below 2 * 10^-6 operations.\n", s) if s >= 0 else -1
if s < 0 or e < 0 or t.count(OLD_PROG) != 1: bad.append("program paragraph not found exactly once")
for a, b in P:
    if t.count(a) != 1: bad.append(f"proof x{t.count(a)}: {a[:70]!r}")
for a, b in N:
    if n.count(a) != 1: bad.append(f"note x{n.count(a)}: {a[:70]!r}")
if bad:
    print("STOP:"); print("\n".join(bad)); sys.exit(1)
t = t[:s] + NEW_PROG + t[e + len("below 2 * 10^-6 operations.\n"):]
for a, b in P: t = t.replace(a, b)
for a, b in N: n = n.replace(a, b)
open(PROOF, "w", encoding="utf-8", newline="\n").write(t); open(NOTE, "w", encoding="utf-8", newline="\n").write(n)
print("sweep applied: program paragraph rewritten, 5 proof passages, 1 note passage")
