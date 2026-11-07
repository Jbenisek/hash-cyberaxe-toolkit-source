import re
def rd(p): return open(p, encoding="utf-8", newline="").read()
def wr(p, t): open(p, "w", encoding="utf-8", newline="").write(t)
def rep(t, a, b, n=None):
    c = t.count(a)
    assert c >= 1 and (n is None or c == n), (a[:80], c)
    return t.replace(a, b)
# ---- appA
t = rd("appA.py")
t = rep(t, "24422, 24422, 34", "17238, 17238, 34"); t = rep(t, "GEN_CALLS = 99448", "GEN_CALLS = 70680"); t = rep(t, "2 x 49,724", "2 x 35,340")
t = rep(t, "PH7, EXTRA, PASSES = 836,", "PH7, EXTRA, PASSES = 603,"); t = rep(t, "24,459 operations", "17,275 operations")
t = rep(t, "(836 + 64)", "(603 + 64)"); t = rep(t, "P, C = 100000, 846", "P, C = 100000, 638")
wr("appA.py", t)
# ---- build_all
b = rd("build_all.py")
b = rep(b, "blake3-r4 entry B3R4u5", "blake3-r3 entry B3R3u5"); b = rep(b, "assert UNIT == 846", "assert UNIT == 638")
b = rep(b, "TLF = 124.93474", "TLF = 124.8123")
b = rep(b, "for _tm in (5245, 10176, 40000, tmax):", "for _tm in (12494, 31946, 60000, tmax):")
b = rep(b, "C(r4) = 846", "C(r3) = 638")
b = rep(b, "blake3-r4-prefix-v1", "blake3-r3-prefix-v1"); b = rep(b, "4 rounds, unkeyed", "3 rounds, unkeyed"); b = rep(b, "of the 4 rounds is used", "of the 3 rounds is used")
b = rep(b, "846 operations (C of blake3-r4)", "638 operations (C of blake3-r3)"); b = rep(b, "complete 4-round digests", "complete 3-round digests")
b = rep(b, '"rounds": 4,', '"rounds": 3,'); b = rep(b, "blake3-r4-nominal-v2", "blake3-r3-nominal-v2")
b = rep(b, "mem7=fm(1912272),", "mem7=fm(1912272), code36=fm((body + b.other_code(st)) * 36), tmax36=fm((b.MEM_LIMIT - b.SPARE - (body + b.other_code(st)) * 36 - b.REGFILE - b.COUNTERS - b.ADVICE) // b.ENTRY),")
b = rep(b, 'Credited derivative: our own eaef120f (B3R4f, the same program, search and proof with 36-byte instructions), a6ee439c (the same program and proof), 41b32afc, 75d5e1f9, 62cfd777 (3 rounds), 0a9640ed and 3356413f (program, search, ledger, register convention),',
        'Credited derivative: our own 62cfd777 (B3R3PV, blake3 round 3, 124.8123, passed the judges: the program), eaef120f (B3R4f, the same program at 4 rounds with the first-collision proof of Section 4), 0ecdfe35 (B3R4u5b, the 5-byte rows with the 17-bit trail number), a6ee439c, 9f69f1cc, 41b32afc, 75d5e1f9, 0a9640ed and 3356413f (program, search, ledger, register convention),')
i = b.index('deps = json.load('); j = b.index('w(os.path.join(PKG, "dependencies.json")')
new = '''deps = json.load(open(os.path.join(HERE, "..", "..", "blake3_r4", "b4f", "pkg", "dependencies.json")))
deps = [d for d in deps if not d["submissionId"].startswith("62cfd777")]
deps.insert(0, {"submissionId": "62cfd777-5613-463f-b561-e2340e00e528",
     "rationale": "Our own entry for blake3 round 3 (124.8123, passed the judges): the program of this entry. Taken from it: the target form, the straight-line step, the packed recovery circuit, the generator, the search, handlers, ledger, experiments and the register file. Changed: the gates of the step, the stage-1 test and the recovery circuit are charged 5 bytes each (instead of 36), the table entry is 10 bytes (63-bit key, 17-bit trail number; 25 bytes before) and the table is the largest that fits in 2^20 bytes, the generator is a two-pass C program, Section 4 is the first-collision proof of Lemma 2, and Tp, B, c are re-planned (time_log2 124.8123 to %s)." % TL,
     "evidence": "proof.md first paragraph and Sections 1, 2, 3.1 to 3.8, 4, 5, 6, 7, 8 and Appendix A."})
deps.insert(1, {"submissionId": "eaef120f-c690-4978-a31e-a3cde49fd669",
     "rationale": "Our own B3R4f (blake3 round 4, time_log2 124.93474), in review: the same program at 4 rounds; taken from it: Section 4 (first-collision Lemma 2, clause (d) of H1), the generator in C, the ledger and plan method, the experiments' form.",
     "evidence": "proof.md Sections 3.6, 4, 5, 7 and Appendix A."})
deps.insert(2, {"submissionId": "0ecdfe35-ba7a-4f74-8ba9-779d417974a2",
     "rationale": "Our own B3R4u5b (blake3 round 4, 124.86023): the same change at 4 rounds (5-byte gate rows, 10-byte table entry with a 17-bit trail number and a 63-bit key, the fix of the a0398a27 ruling); this entry applies it at 3 rounds with the reachable trail numbers bounded below 2^17 (proof 3.1, 3.8).",
     "evidence": "proof.md Sections 3.1, 3.6, 3.8, 4, 7 and Appendix A."})
deps.append({"submissionId": "616120b2-f777-44a8-bbd2-44f20c56224a",
     "rationale": "re-implemented from its text; none of its files used or run",
     "evidence": "the 5-byte encoding of register-only gate instructions (proof.md Section 3.1)."})
assert deps[0]["submissionId"].startswith("62cfd777") and len({d["submissionId"] for d in deps}) == len(deps) and len(deps) <= 20
'''
b = b[:i] + new + b[j:]
wr("build_all.py", b)
# ---- proof_t
P = rd("proof_t.md").split("\n")
P[0] = "# blake3-r3: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk, at three rounds, straight-line step with 5-byte gate instructions (B3R3u5)"
P[2] = ("Credited derivative of our own 62cfd777-5613-463f-b561-e2340e00e528 (B3R3PV, blake3 round 3, time_log2 124.8123, passed the judges: the program, with every instruction charged 36 bytes, 25-byte table entries and the Section 4 of that entry), "
 "of our own eaef120f-c690-4978-a31e-a3cde49fd669 (B3R4f, blake3 round 4, time_log2 124.93474: the same program at 4 rounds with Section 4 rewritten as the first-collision proof of Lemma 2 and clause (d) of H1, which answers the finding F1-adaptive-finished-trail-conditioning / H4 of the judges on 41b32afc-ed4c-4ef1-b9f2-8c72ab163582), "
 "of our own 0ecdfe35-ba7a-4f74-8ba9-779d417974a2 (B3R4u5b, blake3 round 4, 124.86023: the 5-byte rows with the 17-bit trail number), of our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (B3R4d, 125.06000), 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c (B3R4e, 125.06177) and 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (blake3 round 4, 125.35348), "
 "of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448, two-block mode with a fixed first block; this entry does not use that mode), which are derivatives of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). "
 "It also uses two circuit and walk ideas from jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), whose proof text (3.3, 3.4) we read as data and re-implemented in our own generator without using or running any file of that entry: (1) the pivot full adder, (2) the mask walk g = f XOR q in which the digest planes are fed back exactly as the circuit stores them. "
 "The 5-byte encoding of register-only gate instructions is the convention of 616120b2-f777-44a8-bbd2-44f20c56224a (blake3 round 7), re-implemented from its text; none of its files used or run. Everything else is the program of those entries: relation, trail-and-table search with distinguished points, handlers, recovery walk, ledger method, the register file.")
P[3] = ("The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. The chain step is {PH} operations for 256 trails ({perlane:.2f} per trail). "
 "What this entry changes against 62cfd777: the step is the same straight line ({PH} gates, no loop); the gates, which name only registers (the step, the stage-1 test and the recovery circuit of {PH7} gates), are charged as 40-bit instruction words of 5 bytes (an 8-bit opcode and three 10-bit register numbers; Section 3.1) instead of 36 bytes, so the whole code is {codebytes} bytes (it was 687,060) and the memory of the entry is {mem} bytes = 2^{memlog2:.5f} <= 2^20. "
 "The table entry is 10 bytes (a 63-bit key and a 17-bit trail number; it was 25 bytes) and the table is the largest that fits in 2^20 bytes ({tmax} entries; it was 12,494), and with it Tp, B and c are re-planned (Section 7). "
 "time_log2 {TL} against 124.8123 ({dTLf:+.5f}). Section 4 is the first-collision proof of Lemma 2 of B3R4f, with the Chernoff term exp(-300 + (e^5 - 1) H).")
P[5] = "The generator of the setup writes the 5-byte records; the program it emits is byte-identical to the Python reference (sha256 equal) and to the program of 62cfd777 (same gates, same registers, same q)."
T = "\n".join(P)
T = rep(T, "blake3-r4-prefix-v1` (the benchmark's blake3 round-4 profile, BLAKE3 reduced to four rounds)", "blake3-r3-prefix-v1` (the benchmark's blake3 round-3 profile, BLAKE3 reduced to three rounds)")
T = rep(T, "4 rounds with the BLAKE3 message permutation", "3 rounds with the BLAKE3 message permutation")
T = rep(T, "at 3 rounds, at 4 rounds (the target) and at 7 rounds (the full round count)", "at 3 rounds (the target), at 4 rounds and at 7 rounds (the full round count)")
T = T.replace("blake3(M(x), 4)", "blake3(M(x), 3)").replace("chained for 4 steps", "chained for 3 steps")
T = rep(T, "C(r4) = 846 (222, 430, 638 and 846 for 1 to 4 rounds", "C(r3) = 638 (222, 430 and 638 for 1 to 3 rounds")
T = T.replace("--rounds 4 --show-contract`: reference_operation_cost 846) is used only as the unit: Unit = 846 operations", "--rounds 3 --show-contract`: reference_operation_cost 638) is used only as the unit: Unit = 638 operations")
T = T.replace("N / 846", "N / 638").replace("suffice at four rounds", "suffice at three rounds")
T = rep(T, "this program would be 954,072 bytes of code and leave a table of 5,245 entries", "this program would be {code36} bytes of code and leave a table of {tmax36} entries")
T = rep(T, "Credited to our own B3R4f (eaef120f): the straight-line step, the search, the plan method, the experiments' form and the generator's use-count and packing changes; this entry changes the instruction price of the gates, the record format of the generator, and Section 4.",
        "Credited to our own 62cfd777 (the program) and B3R4f (eaef120f, Section 4 and the generator's use-count and packing changes); this entry changes the instruction price of the gates, the table entry, the record format of the generator, and Section 4.")
wr("proof_t.md", T)
# ---- note_t
N = rd("note_t.md").split("\n")
N[0] = "# BLAKE3, 3 rounds: bit-sliced 256-lane search, straight-line step, 5-byte gate instructions (B3R3u5)"
N[6] = ("Our entry for BLAKE3 reduced to 3 rounds (blake3-r3-prefix-v1), a plain birthday collision search on the complete 256-bit digest, run as cheaply as the cost model allows; it uses no differential and no structure of the rounds. It is our own B3R3PV, 62cfd777-5613-463f-b561-e2340e00e528 (time_log2 124.8123, passed the judges), with each register-only gate charged as a 40-bit instruction word of 5 bytes (an 8-bit opcode and three 10-bit register numbers; proof Section 3.1; the convention of 616120b2-f777-44a8-bbd2-44f20c56224a, re-implemented from its text, none of its files used or run), 10-byte table entries with a 17-bit trail number and a larger table, and the first-collision proof of Section 4.")
N[7] = ("The lineage: 62cfd777 is a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), bit-sliced 256-lane searches with a declared register file, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took the pivot full adder and the mask walk g = f XOR q and re-implemented both in our own generator. We did not use or run any file of that entry. The Section 4 proof and the 5-byte rows with the 17-bit trail number come from our round-4 entries eaef120f-c690-4978-a31e-a3cde49fd669 (B3R4f, 124.93474) and 0ecdfe35-ba7a-4f74-8ba9-779d417974a2 (B3R4u5b, 124.86023), which descend from a6ee439c-5b82-41f2-8acb-9917c8c70756, 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c, 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (125.02375, rejected as not evaluable; answered below) and 75d5e1f9-8948-4f49-b7a6-5e9475495a7a. Our program is also derived from cf8b0e92-4302-4813-907a-3c970c102646 and Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.")
i = next(k for k, l in enumerate(N) if l.startswith("## What changed against B3R4f"))
j = next(k for k, l in enumerate(N) if l.startswith("## Response to the 41b32afc"))
N[i:j] = ["## What changed against 62cfd777", "",
 "The gates of the step ({PH} operations a batch), the stage-1 test and the recovery circuit ({PH7} gates) are charged 5 bytes of code instead of 36; all other instructions stay at 36 bytes. The code is {codebytes} bytes (687,060 before) and the memory of the search phase {mem} bytes = 2^{memlog2b:.5f}, not above 2^20; memory_log2_bytes stays 20. The table entry is 10 bytes, a 63-bit key and a 17-bit trail number (62cfd777: 25 bytes); the trail numbers stay below 256 + {tmax} + 1 + 1 < 2^17 (proof 3.1, 3.8). The table holds {tmax} entries (62cfd777: 12,494), and Tp ({Tp}), B, the age cap ({kappa} L) and c are re-planned. The generator of the setup writes the 5-byte records (the program it emits is byte-identical to the Python reference, sha256 equal). Section 4 is the first-collision proof of B3R4f, with the P_tiny term exp(-300 + (e^5 - 1) H). time_log2 {TL} against 124.8123 ({dTLf:+.5f}); no new premise.", ""]
T = "\n".join(N)
T = T.replace("blake3-r4-prefix-v1", "blake3-r3-prefix-v1")
T = rep(T, "`blake3(M, 4)` on 8,192 messages and on 4,096 lanes chained for 4 steps", "`blake3(M, 3)` on 8,192 messages and on 4,096 lanes chained for 3 steps")
T = rep(T, "a judge who charges 36 bytes per gate gets 954,072 bytes of code and a table of 5,245 entries", "a judge who charges 36 bytes per gate gets {code36} bytes of code and a table of {tmax36} entries")
wr("note_t.md", T)
print("ok")
