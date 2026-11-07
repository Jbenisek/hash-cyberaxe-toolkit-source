s = open('build_all.py', encoding='utf-8').read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)


rep("The organizer's reference count C(r4) = 846 is used only as the unit.", "The organizer's reference count C(r7) = 1470 is used only as the unit.")
rep("emits the identical program in a 1 MiB sandbox, proof 3.6)", "emits the identical program in a memory-capped sandbox, proof 3.6)")
# dependencies: a6ee439c first
i = s.index("deps = [")
new_first = '''deps = [
    {"submissionId": "a6ee439c-5b82-41f2-8acb-9917c8c70756",
     "rationale": "Our own round-4 entry B3R4d (125.06000), filed 10-15: the program, circuit generator, ledger method, experiments and certificates of this entry are those of a6ee439c taken from four rounds to seven (BLAKE3 has seven rounds), and its Section 4 (the supermartingale Lemma 2, clause (d) of H1, the plan method with the Chernoff trail sums) is used unchanged in structure with the new parameters. Changed: the round count and unit (C = 1470), the step (45,974 gates), the generator's use counts (one byte per node) and node packing, the plan (Tp, B, c, table size), and the memory statement: the program no longer fits in 2^20 bytes, so memory is claimed above it and the scalar score pays for it (proof Section 3.8).",
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."},
'''
s = s[:i] + new_first + s[i + len("deps = [\n"):]
rep("Our own round-4 entry B3R4b (125.02375), rejected by the judges (not_evaluable) on one finding about the success-probability step of its Lemma 2. The program, circuit, ledger method, experiments and certificates of this entry are those of 41b32afc. Changed: proof Section 4 (a new Lemma 2 for the random function and clause (d) of H1), the plan constants that the new bound prices (Tp, B, age cap, one cut, table margin) and the numbers that follow; and the memory statement of Section 3.6 (the clause about the Python reference generator's resident set is removed).",
    "Our own round-4 entry B3R4b (125.02375), rejected by the judges (not_evaluable) on one finding about the success-probability step of its Lemma 2 (F1-adaptive-finished-trail-conditioning, H4). The program, circuit, ledger method, experiments and certificates descend from 41b32afc; its finding is answered in a6ee439c and in Section 4 of this entry (the new Lemma 2 and clause (d) of H1).")
rep("proof.md first paragraph and Sections 1, 2, 3.1 to 3.6, 4, 5, 6, 7, 8 and Appendix A.", "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A.", 3)
open('build_all.py', 'w', encoding='utf-8').write(s)
print('ok')
