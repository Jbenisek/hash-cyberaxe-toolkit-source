def rd(p): return open(p, encoding="utf-8", newline="").read()
def wr(p, t): open(p, "w", encoding="utf-8", newline="").write(t)
b = rd("build_all.py")
b = b.replace("oldTL='125.29113', oldTp=228, pred='a2e94df7'", "oldTL='125.19806', oldTp=0, pred='77fb5c02'")
b = b.replace("Credited derivative: our own a2e94df7 (B3R7c, the same program with the earlier Section 4), 1cd0dd3b (the same search and plan method, with a straight-line five-round step), a6ee439c",
              "Credited derivative: our own 77fb5c02 (B3R5c, the same program, rolled), 4a9f31b8 (the same search and plan method, with a straight-line five-round step), 616120b2 (the 5-byte gate-instruction convention; re-implemented from its text, none of its files used or run), a2e94df7 (B3R7c), a6ee439c")
i = b.index('    {"submissionId": "a2e94df7'); j = b.index('    {"submissionId": "a6ee439c')
new = '''    {"submissionId": "77fb5c02-839d-4aeb-8b51-2c100c649b9a",
     "rationale": "Our own B3R5c (blake3 round 5, time_log2 125.19806, rolled round body), filed: the program of this entry. Taken from it: the target form, the generator, the search, handlers, recovery, ledger, the 10-byte table entry, the register file, the experiments, and Section 4 Step 1 (lazy sampling), Step 6 (the cut count), Lemma 1 and Appendix A (certification method). Changed: Section 4 is rewritten as a first-collision proof of Lemma 2 (Steps 2 to 5), B and Tp are re-planned on it (time_log2 125.19806 to %s); the step is the straight line of 4a9f31b8 instead of the rolled body, and its gates are charged 5 bytes each." % TL,
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},
    {"submissionId": "616120b2-f777-44a8-bbd2-44f20c56224a",
     "rationale": "re-implemented from its text; none of its files used or run",
     "evidence": "the 5-byte gate-instruction encoding convention"},
    {"submissionId": "4a9f31b8-0ac7-475d-a73d-583a41298226",
     "rationale": "Our own B3R5b (blake3 round 5, time_log2 125.00951, memory 2^20.37855, scalar score 125.38806): the straight-line step, the search, the plan method, clause (d) of H1, the experiments, the generator and the ledger of this entry are those of 4a9f31b8. Changed: the gates of the step, the stage-1 test and the recovery circuit are charged 5 bytes of code each (a 40-bit word with three 10-bit register numbers) instead of 36, so the whole program fits in 2^20 bytes and the memory term (0.37855 bit) is removed; the generator writes the 5-byte records; the table is the largest that fits in 2^20; Section 4 is the first-collision proof.",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},
    {"submissionId": "a2e94df7-bff4-4461-ad40-7f75930cb241",
     "rationale": "Our own B3R7c (blake3 round 7, time_log2 125.29113): the rolled program from which B3R5c was taken, and the generator in C, the register file and the plan method.",
     "evidence": "proof.md Sections 3.1 to 3.8 and 7."},
'''
b = b[:i] + new + b[j:]
b = b.replace("taken from four rounds to seven (BLAKE3 has seven rounds)", "taken from four rounds to five").replace("taken from four rounds to five rounds", "taken from four rounds to five")
open("build_all.py", "w", encoding="utf-8", newline="").write(b)
