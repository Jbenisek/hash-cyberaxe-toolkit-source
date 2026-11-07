"""Builds proof_t9.md and note_t9.md of B3R7d from proof_t8.md / note_t8.md (B3R7c) and sec4_t9.md (exact-match edits)."""
import re


def edit(src, dst, steps):
    t = open(src, encoding="utf-8", newline="").read()
    assert "\r" not in t and not t.startswith("﻿")

    def rep(a, b, cnt=1):
        nonlocal t
        assert t.count(a) == cnt, (t.count(a), a[:90])
        t = t.replace(a, b)
    steps(t, rep, lambda: t)
    return rep


# ---------------------------------------------------------------- proof
t = open("proof_t8.md", encoding="utf-8", newline="").read()
assert "\r" not in t and not t.startswith("﻿")


def rep(a, b, cnt=1):
    global t
    assert t.count(a) == cnt, (t.count(a), a[:90])
    t = t.replace(a, b)


rep("with a rolled round body (B3R7b)", "with a rolled round body (B3R7d)")
# credit paragraph
rep("Credited derivative of our own 1cd0dd3b-eb60-4572-a75f-937cd771ec4a (B3R7, blake3 round 7, time_log2 125.05397, memory_log2_bytes 20.86686, scalar score 125.92083, filed 10-15: the same search, plan method, success proof (Section 4) and experiments;",
    "Credited derivative of our own a2e94df7-bff4-4461-ad40-7f75930cb241 (B3R7c, blake3 round 7, time_log2 125.29113: the filed version of this program; this entry rewrites its Section 4), of our own 1cd0dd3b-eb60-4572-a75f-937cd771ec4a (B3R7, blake3 round 7, time_log2 125.05397, memory_log2_bytes 20.86686, scalar score 125.92083, filed 10-15: the same search, plan method and experiments;")
rep("the entry that introduced the supermartingale Lemma 2 of Section 4 and clause (d) of H1, which answer the finding", "the entry that introduced clause (d) of H1, which answers the finding")
rep("The experiments and the proof of Section 4 are those of 1cd0dd3b and a6ee439c with the new numbers.", "The experiments are those of 1cd0dd3b and a6ee439c with the new numbers; Section 4 is the first-collision proof of Lemma 2.")
# revision note -> one 'what changed' line
i = t.index("Revision note. This text revises")
j = t.index("## 1. Target and relation")
t = t[:i] + ("What changed against B3R7c (a2e94df7): Section 4 is rewritten as a first-collision proof of Lemma 2 (Steps 2 to 5; the cut count of Step 6 is kept), B and Tp are re-planned (Tp {Tp} against 228, age cap {kappa} L against 13 L, B = {B}), time_log2 {TL} against 125.29113. The target, step, rolled round body, generator, recovery circuit, 10-byte table entry, registers and experiments are unchanged.\n\n") + t[j:]
# section 5
rep("Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish)", "Lemma 2 now proves the bound for F from the hazard alone (the first collision of the run and the detection delay, no conditioning on which trails finish)")
rep("Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F", "Lemma 1, the lazy-sampling facts, the first-collision bound, the Chernoff bounds and the cut count are proved in Section 4 for F")
# section 9 removal
i = t.index("## 9. Response to the findings")
j = t.index("## Appendix A.")
t = t[:i] + t[j:]
rep("(the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding)", "(the floating-point bound only selects B and Tp; the printed rows do not depend on rounding)")
# section 4
i = t.index("## 4. Success probability")
j = t.index("## 5. Premise H1")
sec4 = open("sec4_t9.md", encoding="utf-8").read()
t = t[:i] + sec4.rstrip("\n") + "\n\n" + t[j:]
open("proof_t9.md", "w", encoding="utf-8", newline="\n").write(t)
print("proof template", len(t))
print(sorted(set(re.findall(r"\{[a-zA-Z_0-9:.,+]+\}", t))))

# ---------------------------------------------------------------- note
t = open("note_t8.md", encoding="utf-8", newline="").read()
assert "\r" not in t and not t.startswith("﻿")
rep("rolled round body (B3R7b)", "rolled round body (B3R7d)")
rep("Our second entry for BLAKE3 at seven rounds,", "Our entry for BLAKE3 at seven rounds,")
rep("It is our own B3R7, 1cd0dd3b-eb60-4572-a75f-937cd771ec4a (time_log2 125.05397, memory 2^20.86686, scalar score 125.92083, filed 10-15), with the machine plan of the step changed so that the program fits in 2^20 bytes; the search, the plan method, the proof of the success bound (Section 4, the supermartingale Lemma 2 of a6ee439c) and the experiments are those of 1cd0dd3b. We do not yet know how the judges rate 1cd0dd3b or a6ee439c; this entry carries the same Section 4 and is exposed to the same reading.",
    "It is our own B3R7c, a2e94df7-bff4-4461-ad40-7f75930cb241 (time_log2 125.29113), with the proof of the success bound (Section 4) rewritten as a first-collision proof and B and Tp re-planned; the target, the rolled step, the search, the recovery, the ledger and the experiments are those of a2e94df7. Its lineage starts at our B3R7, 1cd0dd3b-eb60-4572-a75f-937cd771ec4a (time_log2 125.05397, memory 2^20.86686, scalar score 125.92083), whose machine plan of the step was changed so that the program fits in 2^20 bytes.")
rep("The lineage: 1cd0dd3b is our round-4 entry", "The lineage continued: 1cd0dd3b is our round-4 entry")
rep("## What changed against 1cd0dd3b (B3R7), and why\n", "## What changed against B3R7c (a2e94df7)\n\nSection 4 is rewritten as a first-collision proof of Lemma 2 (Steps 2 to 5; the cut count of Step 6 is kept), B and Tp are re-planned (Tp {Tp} against 228, age cap {kappa} L against 13 L, B = {B}), time_log2 {TL} against 125.29113; nothing else changed.\n\n## What changed against 1cd0dd3b (B3R7), and why\n")
rep("(a supermartingale over the evaluations, with no conditioning on which trails finish and no random U)", "(the first collision of the run and the detection delay, with no conditioning on which trails finish and no random U)")
i = t.index("## Response to the findings of the judges' rulings (8fbecd8a and 1cd0dd3b)")
j = t.index("## Numbers")
t = t[:i] + t[j:]
rep("Lemma 2 v2 proves P_F >= {Pcert} (exact certificate of Appendix A) for the random function with no premise besides H1; the cut-count heuristic H2 of the filed entry is withdrawn.", "Lemma 2 proves P_F >= {Pcert} (exact certificate of Appendix A) for the random function with no premise besides H1.")
open("note_t9.md", "w", encoding="utf-8", newline="\n").write(t)
print("note template", len(t))
print(sorted(set(re.findall(r"\{[a-zA-Z_0-9:.,+]+\}", t))))
