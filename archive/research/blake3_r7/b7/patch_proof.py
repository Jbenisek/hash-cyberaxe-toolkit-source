p = 'proof_t_b4d.md'
s = open(p, encoding='utf-8').read()


def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)


L = s.split('\n')
assert L[0].startswith('# blake3-r4:')
L[0] = '# blake3-r7: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk, at the full seven rounds'
assert L[2].startswith('Credited derivative of our own 41b32afc')
L[2] = ("Credited derivative of our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (blake3 round 4, 125.06000, filed 10-15: the entry that introduced the supermartingale Lemma 2 of Section 4 and clause (d) of H1, which answer the finding F1-adaptive-finished-trail-conditioning / H4 of the judges on 41b32afc; this entry is that program, proof structure and plan method taken from four rounds to seven, the full round count of BLAKE3), "
        "of our own 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (blake3 round 4, 125.02375, rejected by the judges on that one finding about the success-probability argument), of our own 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (blake3 round 4, 125.35348), of our own 62cfd777-5613-463f-b561-e2340e00e528 (blake3 round 3, 124.8123: this program at three rounds), of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448, two-block mode with a fixed first block; this entry does not use that mode), which are derivatives of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). "
        "It also uses two circuit and walk ideas from jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), whose proof text (3.3, 3.4) we read as data and re-implemented in our own generator without using or running any file of that entry: (1) the pivot full adder, (2) the mask walk g = f XOR q in which the digest planes are fed back exactly as the circuit stores them. Everything else is the program of those entries: relation, trail-and-table search with distinguished points, handlers, recovery walk, ledger method, the register file and the 36-byte instruction charge.")
assert L[3].startswith('The target is the plain one')
L[3] = ("The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. The chain step is {PH} operations for 256 trails ({perlane:.2f} per trail; 24,422 for the four-round step of a6ee439c, 17,238 for the three-round step of 62cfd777). "
        "What seven rounds change against the four-round entry: the straight line has {PH} gates and a program of {instr} instructions of 36 bytes ({codebytes} bytes) is by itself larger than 2^20 bytes, so memory cannot be held at 2^20 as at four rounds. This entry spends {tablebytes} bytes ({tmax} entries of 10 bytes) on the table, counts {mem} bytes of memory, claims memory_log2_bytes = {memlog2}, and pays log2(memory / 2^20) = {memterm:.5f} bit in the lane's scalar time-memory score (`hashsmash-scalar-tm-v1`: time_log2 + max(0, memory_log2_bytes - 20), here {score:.5f}); the table size, and with it Tp, B and c, is the plan that minimises that sum (Section 7). "
        "The circuit generator keeps one byte per node for the use counts (a node is used up to 19 times, which 4 bits cannot hold) and packs signals with 16-bit node numbers (Section 3.6). The experiments and the proof of Section 4 are those of a6ee439c with the new numbers.")
s = '\n'.join(L)
rep("Target `blake3-r4-prefix-v1` (the benchmark's blake3 round-4 profile)", "Target `blake3-r7-prefix-v1` (the benchmark's blake3 round-7 profile, the full seven rounds of BLAKE3)")
rep("4 rounds with the BLAKE3 message permutation", "7 rounds with the BLAKE3 message permutation")
rep("`verifier/blake3.py:blake3(M(x), 4)`", "`verifier/blake3.py:blake3(M(x), 7)`")
rep("first at 3 rounds, then at 4 rounds (the target) and at the full 7 rounds, on {nchk}", "at 3 rounds, at 4 rounds and at 7 rounds (the target, the full round count), on {nchk}")
rep("The bit-sliced step was compared with the organizer reference `blake3(M(x), 4)` on", "The bit-sliced step was compared with the organizer reference `blake3(M(x), 7)` on")
rep("chained for 4 steps, the packed recovery circuit", "chained for 7 steps, the packed recovery circuit")
rep("4,096 lanes chained for 4 steps, the register-allocated", "4,096 lanes chained for 7 steps, the register-allocated")
rep("The organizer's reference count C(r4) = 846 (222, 430, 638 and 846 for 1 to 4 rounds, the value of the organizer's `pareto/targets.py:reference_cost('blake3', r)`) is used only as the unit: Unit = 846 operations.",
    "The organizer's reference count C(r7) = 1,470 (222, 430, 638, 846, 1,054, 1,262 and 1,470 for 1 to 7 rounds, that is 14 + 208 r; the value printed by the lane contract, `pareto_candidate.py --family blake3 --rounds 7 --show-contract`: reference_operation_cost 1470) is used only as the unit: Unit = 1,470 operations.")
rep("N / 846 = ", "N / 1,470 = ")
rep("8,192 lanes and 4,096 lanes chained for 4 steps against", "8,192 lanes and 4,096 lanes chained for 7 steps against")
rep("counts the uses of every node (4 bits per node)", "counts the uses of every node (8 bits per node: a node is used up to 19 times at seven rounds)")
rep("use counts {nodes} nodes x 4 bits = {usesbytes} bytes", "use counts {nodes} nodes x 8 bits = {usesbytes} bytes")
rep("({memspare} bytes to spare under 2^20); the region", "({memspare} bytes to spare under the {memlimit}-byte budget of the plan); the region")
rep("The table size of Section 7 is the largest that fits with this layout.", "The table size of Section 7 is the one the plan chooses; the setup phase fits inside the search-phase memory with this layout.")
rep("which was run under the 1 MiB caps above;", "which was run under the caps shown above;")
rep("complete 4-round digests agree in the low 18 bits", "complete 7-round digests agree in the low 18 bits")
rep("= {mem} bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase.", "= {mem} bytes = 2^{memlog2:.5f}; the preprocessing is inside the setup phase.")
rep("Claim `memory_log2_bytes` = 20.", "Claim `memory_log2_bytes` = {memlog2} (log2 of {mem}, rounded up in the fifth decimal); the scalar policy adds max(0, {memlog2} - 20) = {memterm:.5f} to time_log2 (Section 3.8).")
rep("tmax = floor((2^20 - {sparereq} - {codebytes} - 25,600 - 16,384) / 10) = {tmax} (at least {sparereq} bytes of the search phase are left unused on purpose: {spare} bytes), and Tp",
    "tmax = floor(({memlimit} - {sparereq} - {codebytes} - 25,600 - 16,384) / 10) = {tmax}, where {memlimit} bytes is the memory budget the plan chose: the scan of `plan(256)` over table sizes (it prints time_log2 + log2(memory / 2^20) for each size: {scan}) has its minimum at {tmax} entries; a smaller table needs shorter trails and more time than the memory term it saves, a larger one adds more memory term than it saves. Tp")
marker = "## 4. Success probability"
assert s.count(marker) == 1
s = s.replace(marker, """### 3.8 Memory and the scalar score
The lane's scoring policy is `hashsmash-scalar-tm-v1` (memoryUnitBytes 1,048,576, minimumMemoryUnits 1): score = time_log2 + max(0, memory_log2_bytes - 20). At four rounds the program (954,072 bytes) and its table fit in 2^20 bytes and the memory term is 0. At seven rounds the straight line alone is {codebytes} bytes, so the term is not 0 for this program. The claim states the byte count of the search phase, {mem} bytes (Section 7), as memory_log2_bytes = {memlog2}; the term is {memterm:.5f} and the scalar score is {TL} + {memterm:.5f} = {score:.5f}. A smaller program would need a rolled round body (a loop over the rounds with message-index tables); that is a different machine plan, not part of this entry, and its charges would differ from every count here.

""" + marker)
open('proof_t.md', 'w', encoding='utf-8').write(s)
print("ok")
