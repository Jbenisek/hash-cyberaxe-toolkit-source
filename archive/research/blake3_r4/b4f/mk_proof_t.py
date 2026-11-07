"""Builds proof_t.md of B3R4f from proof_t_b4e.md (the template of B3R4e) and sec4_t.md."""
import re
t = open("proof_t_b4e.md", encoding="utf-8").read()


def rep(a, b, cnt=1):
    global t
    assert t.count(a) == cnt, (t.count(a), a[:80])
    t = t.replace(a, b)


# 1 credit paragraph
i = t.index("Credited derivative of our own 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (")
j = t.index("of our own 75d5e1f9-8948-4f49-b7a6-5e9475495a7a")
t = t[:i] + ("Credited derivative of our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (B3R4d, blake3 round 4, time_log2 125.06000: the filed version of this program, in review) and of our own 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c (B3R4e, blake3 round 4, 125.06177: the same program with Lemma 2 v2, in review), which derive from our own 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (blake3 round 4, 125.02375, rejected by the judges on one finding about the success-probability argument), "
             + t[j:])
# 2 paragraph two
rep("({tmax} entries of 10 bytes) for the table inside 2^20 bytes (with the declared 800-register file)", "({tmax} entries of 7 bytes) for the table inside 2^20 bytes (with the declared 800-register file)")
rep("a table entry holds only the key and the trail number (10 bytes): the trail lengths are not stored", "a table entry holds only a 40-bit key and the trail number (7 bytes): the trail lengths are not stored")
# 3 revision note
i = t.index("Revision note. This text revises")
j = t.index("## 1. Target and relation")
t = t[:i] + ("What changed against a6ee439c and 9f69f1cc (same target, step, generator and experiments): (1) Section 4: Lemma 2 is proved from the first collision of the run and the detection delay (Steps 2 to 5; the cut count of Step 6 is kept), so B is smaller; (2) the recovery circuit is a rolled program of {CODE7} instructions ({PH7} operations per call, Section 3.3) instead of a straight line of 836 instructions, which leaves a larger table; (3) the table entry is 7 bytes (40-bit key) instead of 10. Tp {Tp} (was 67), kappa {kappa} (was 13), tmax {tmax} (was 5,245), B = {B}, time_log2 {TL} (was 125.06000).\n\n") + t[j:]
# 4 section 2
rep("followed by the {fb} low bits of F (F < {Tp} <= 2^{fb}, so those {fb} bits are F); 64 bits in all.", "followed by the {fb} low bits of F (F < {Tp} <= 2^{fb}, so those {fb} bits are F); {keybits} bits in all.")
rep("(10-byte entry: key and t, no length, Section 7)", "(7-byte entry: key and t, no length, Section 7)")
rep("Both lanes of one packed circuit ({PH7} operations: the compression and one XOR of each of the 8 output words with the 32-bit word of q; used by nothing else) are used.", "Both lanes of one packed circuit (a rolled program of {CODE7} instructions that executes {PH7} operations: four rounds of one loop body, then one XOR of each of the 8 output words with the 32-bit word of q; Section 3.3; used by nothing else) are used.")
rep("table capacity tmax = {tmax} entries of 10 bytes.", "table capacity tmax = {tmax} entries of 7 bytes.")
# 5 handlers
rep("key formation, two read-modify-write field stores of the 10-byte entry,", "key formation, three read-modify-write field stores of the 7-byte entry (low key words, high key bytes, trail numbers),")
rep("The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key.", "The key scan of the table is charged separately: the low-key array holds 8 keys per word, testing a word costs 8 operations (the high key byte is compared only after a match of the low word), charged 3 per key.")
rep("- Recovery batch (both lanes in one packed circuit, {PH7} operations, the last 8 of them the XORs with q)", "- Recovery batch (both lanes in one rolled packed circuit, {PH7} operations executed, the last 16 of them the output XORs, 8 of them with q)")
rep("Code size, instructions: loop body {body} + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery {recov} (the {PH7}-operation circuit, the test, the loop, the call and the moves) + setup, cut and slice 160 = {instr} instructions.",
    "The recovery circuit. 256-bit registers hold 7 lanes of 36 bits (32 data bits and 4 guard bits); the state words are registers 0..15, the 16 message slots registers 16..31, and 3 temporaries; an instruction is one operation (add, AND, OR, XOR, shift by a constant, move, or load of an inline 256-bit immediate), each charged. Program: 24 loads (the IV words and constants of the state, the 8 zero message slots; the 8 input words are in slots 24..31), then 4 times one round, then 16 output instructions. One round is the 8 G calls (30 operations each: 6 additions, 4 XORs and 4 rotations of 5 operations, the rotation by r being ((s >> r) AND mask) OR ((s << (32 - r)) AND mask), which also clears the guard bits) and 8 ANDs that clear the guard bits of the state words 0..3 and 8..11: {RB} instructions. Between rounds the 16 message slots are permuted by the BLAKE3 permutation with {MV} moves (two cycles of 8, one temporary each); the loop control is one instruction to set the counter, then D, C, Z per iteration and J per jump (one operation each). Guard bits: the program tracks, while it builds the circuit, a bound b * 2^32 for the value of every register and asserts b < 16 (a lane holds 16 * 2^32); the sums of one round stay below 9 * 2^32 (the words 0..3, which are masked at the end of the round) and 5 * 2^32 (the words 8..11), so no carry crosses into the next lane. Instructions {CODE7} = 24 + 1 + {RB} + 3 + {MV} + 1 + 16; operations executed {PH7} = 24 + 1 + 4 ({RB} + 3) + 3 ({MV} + 1) + 16. The circuit gives the same g = f XOR q as the scalar compression (selftest; and the packed circuit against the organizer reference on {nref_packed} messages, Section 1).\nCode size, instructions: loop body {body} + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery {recov} (the {CODE7}-instruction rolled circuit, the test, the loop, the call and the moves) + setup, cut and slice 160 = {instr} instructions.")
# 9 section 5 H1 text
rep("Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish)", "Lemma 2 now proves the bound for F from the hazard alone (the first collision of the run and the detection delay, no conditioning on which trails finish)")
rep("Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F", "Lemma 1, the lazy-sampling facts, the first-collision bound, the Chernoff bounds and the cut count are proved in Section 4 for F")
# 10 section 7
rep("Table: {tmax} entries * 10 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is the key (8 bytes) and the trail number t (2 bytes), kept in two arrays (keys 4 per word, numbers 16 per word);",
    "Table: {tmax} entries * 7 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is a 40-bit key and the trail number t (2 bytes), kept in three arrays in blocks of 32 entries = 7 words (the low 32 key bits, 8 per word; the high 8 key bits, 32 per word; the numbers, 16 per word);")
rep("tmax = floor((2^20 - {sparereq} - {codebytes} - 25,600 - 16,384) / 10) = {tmax}", "tmax = 32 floor((2^20 - {sparereq} - {codebytes} - 25,600 - 16,384) / 224) = {tmax}")
# 11 section 8
rep("The recovery circuit has 8 more operations than in 0a9640ed (the XOR with q) and the generator is new (Section 3.6), charged.", "The recovery circuit is a rolled program (Section 3.3) and the generator is new (Section 3.6), both charged.")
rep("and H3 (the 800-register machine convention and the 36-byte instruction charge, supporting).", "and H3 (the 800-register machine convention, the 36-byte instruction charge and the charges of the rolled recovery circuit, supporting).")
# 12 section 9 removal
i = t.index("## 9. Response to the findings")
j = t.index("## Appendix A.")
t = t[:i] + t[j:]
# 13 appendix
rep("(the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding)", "(the floating-point bound only selects B and Tp; the printed rows do not depend on rounding)")
# 14 section 4
i = t.index("## 4. Success probability")
j = t.index("## 5.")
sec4 = open("sec4_t.md", encoding="utf-8").read()
t = t[:i] + sec4.rstrip("\n") + "\n\n" + t[j:]
open("proof_t.md", "w", encoding="utf-8", newline="\n").write(t)
print(len(t))
print(sorted(set(re.findall(r"\{[a-zA-Z_0-9:.,]+\}", t))))
