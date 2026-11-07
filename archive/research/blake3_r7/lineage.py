"""usage: python -B lineage.py R   (after mkround.py and fixround.py): lineage text, dependencies and score constants for round R"""
import sys, os, ast
R = int(sys.argv[1])
W = {5: "five", 6: "six"}[R]
D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blake3_r%d" % R, "b%d" % R))
R7 = ("1cd0dd3b-eb60-4572-a75f-937cd771ec4a", "our B3R7, blake3 round 7, 125.05397 with memory 2^20.86686, filed 10-15")
if R == 6:
    chain = [R7]
else:
    r6 = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blake3_r6", "b6", "id.txt")).read().split()[0] if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "blake3_r6", "b6", "id.txt")) else "R6IDPLACEHOLDER-0000-0000-0000-000000000000"
    chain = [(r6, "our B3R6, blake3 round 6, filed 10-15"), R7]
def rd(p): return open(os.path.join(D, p), encoding="utf-8", newline="").read()
def wr(p, t): open(os.path.join(D, p), "w", encoding="utf-8", newline="").write(t)
# proof credit line
t = rd("proof_t.md")
a = "Credited derivative of our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (blake3 round 4,"
assert t.count(a) == 1
pre = "Credited derivative of " + ", of ".join("our own %s (%s: this program, proof and plan method at a neighbouring round count)" % (u, l) for u, l in chain) + ", of our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (blake3 round 4,"
t = t.replace(a, pre)
wr("proof_t.md", t)
# note
t = rd("note_t.md")
a = "It is our own round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756"
assert t.count(a) == 1
pre = "Direct predecessor%s: %s. The program, proof Section 4 and plan method are the same; the round count, the step, the table and the memory differ. " % ("s" if len(chain) > 1 else "", "; ".join("%s (%s)" % (u, l) for u, l in chain))
t = t.replace(a, pre + "Further back: our own round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756")
wr("note_t.md", t)
# dependencies
t = rd("build_all.py")
a = 'deps = [\n    {"submissionId": "a6ee439c'
assert t.count(a) == 1
new = "deps = [\n"
for u, l in chain:
    new += '    {"submissionId": "%s",\n     "rationale": "%s: the program, circuit generator, ledger method, experiments and Section 4 (supermartingale Lemma 2, clause (d) of H1) of this entry are those of that entry at a neighbouring round count; changed here: the round count and unit, the step, the plan (Tp, B, c, table size) and the memory (above 2^20, claimed at its byte count, proof Section 3.8).",\n     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},\n' % (u, l[0].upper() + l[1:])
t = t.replace(a, new + '    {"submissionId": "a6ee439c')
t = t.replace("Our own round-4 entry B3R4d (125.06000), filed 10-15: the program,", "Our own round-4 entry B3R4d (125.06000), filed 10-15: the program,")
wr("build_all.py", t)
print("ok", [c[0][:8] for c in chain])
