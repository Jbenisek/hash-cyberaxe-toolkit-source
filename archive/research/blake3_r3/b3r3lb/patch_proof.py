import re
P = "pkg/blake3/proof.md"
s = open(P, encoding="utf-8").read()


def rep(a, b, n=1):
    global s
    assert s.count(a) == n, (s.count(a), a[:80])
    s = s.replace(a, b)


# ---- header
i = s.index("Credited derivative")
j = s.index("## 1. Target")
s = s[:i] + """Credited derivative of our own entry cf8b0e92-4302-4813-907a-3c970c102646 (blake3 round 3, 125.10041, itself a derivative of e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca). That chain
supplies the construction: the seven-lane 36-bit packed circuit, the grouped filter, the mixed distinguished points, 25-byte table entries, the recovery walk, the ledger and the premise tests T1 to T3. This entry keeps all of it and changes one thing:
the message has a fixed 64-byte first block P, so the block that the search varies is the last block of a two-block chunk and its chaining value CV = chain_value(P) is a constant that is not the IV.
P was chosen so that one 32-bit sum of two constants of the circuit is zero (Section 8), which removes 2 operations from the 595-operation batch (593). The program derives the table size and the
distinguished-point threshold from the code size, so Tp moves from 400 to 401 and the table from 26,791 to 26,837 entries; the ledger with all of this gives 125.09556 (the base ledger with a 595-operation batch gives 125.10041).
No differential, no structure of the 3-round compression is used in the search. The claim is the price of the birthday attack on the complete 3-round hash of messages that start with P, when the compression is
evaluated seven instances at a time in 256-bit words and every operation is counted.

""" + s[j:]

# ---- section 1
i = s.index("Target `blake3-r3-prefix-v1`.")
j = s.index("## 2. The attack")
s = s[:i] + """Target `blake3-r3-prefix-v1`. Its message domain is quoted from the organizer profile (field `message_domain`): "Finite byte strings of bit length below 2^64." Every 128-byte string is therefore a message of the domain (Heuristic H4 of the claim declares this use of the domain). For a 256-bit integer x let M(x) be the 128-byte message `P || 0^32 || x` (x little endian), where P is the fixed 64-byte string
of Section 8 (`PREFIX` of the program, 16 little-endian words). M(x) is one chunk of two blocks. Block 1 is P: chaining value IV, counter 0, block length 64, flags 1 = CHUNK_START, rounds 0..2, feed-forward v[i] XOR v[i+8] for i < 8, giving the chaining value CV (a non-root block outputs these 8 words).
Block 2 is the last block: chaining value CV, words m0..m7 = 0, m8..m15 = the eight little-endian words of x, counter 0, block length 64, flags 10 = CHUNK_END|ROOT, rounds 0..2, feed-forward v[i] XOR v[i+8], digest = the 8 words, little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit
little-endian integer. The attack outputs x != y with f(x) = f(y); then M(x) != M(y) are two distinct messages in the domain with equal
256-bit digests. The scalar digest of the program (`chain_value` and `digest_words`, section 1 of the program) was compared with the organizer reference `verifier/blake3.py:blake3` on 300 messages M(x) of this form (rounds 3, 0 differences); the same digest code without the prefix was compared on 2,002 64-byte
messages (rounds 1..7, 286 each, 0 differences) and with the 7-, 2- and 1-round digests of the 64-byte block in the organizer test vectors (`tests/fixtures/blake3-vectors.json`, 3 of 3); the program's own selftest compares the packed circuit with its scalar digest.

""" + s[j:]

# ---- section 2
rep("The density is theta = 400 / 2^122 = 2^-113.3561 and L = 1 / theta = 2^113.3561 (the previous entry used theta = 2^-114).",
    "The density is theta = 401 / 2^122 = 2^-113.3525 and L = 1 / theta = 2^113.3525 (the base entry used 400 / 2^122; Tp is the largest value whose table-capacity bound stays below 2^-40, and the smaller code of this entry leaves room for 401).")
rep("below Tp = 400.", "below Tp = 401.")
rep("(F < 400 < 2^9, so those 9 bits are F)", "(F < 401 < 2^9, so those 9 bits are F)")
rep("Tp = 400, L = 332306998946228968225951765070086144 / 25, B = 48,526,160,035,038,520,402,225,153,211,911,276,864",
    "Tp = 401, L = 5316911983139663491615228241121378304 / 401, B = 48,526,027,423,825,563,155,309,147,850,303,017,632")
rep("e2max = 158,177,279,050,121,848,851,244,930,467, c = 159,507,359,494,189,904,748,456,847,233,641,350 (= 2^116.94), table capacity tmax = 26,791 entries",
    "e2max = 158,176,846,786,764,889,064,786,972,054, c = 159,109,585,530,363,994,761,552,964,821,587,381 (= 2^116.94), table capacity tmax = 26,837 entries")
rep("finished trails <= 26,791, cut trails <= Q / c + 7 = 2,136", "finished trails <= 26,837, cut trails <= Q / c + 7 = 2,141")
rep("The key determines F (F < 400 < 2^9", "The key determines F (F < 401 < 2^9")
rep("Parameters for n = 256: N = 2^256, seven lanes, groups of U = 16 batches.", "Parameters for n = 256: N = 2^256, seven lanes, groups of U = 16 batches. The function is f of Section 1 (last block with chaining value CV).")

# ---- section 3
rep("### 3.2 One batch = 595 operations", "### 3.2 One batch = 593 operations")
i = s.index("Constants (same in every lane) are folded")
j = s.index("Cost per instance:")
s = s[:i] + """Constants (same in every lane) are folded at build time and cost nothing: the four column calls of round 0 depend only on m0..m7 = 0, CV and the IV, so only the four diagonal calls of round 0 and
all calls of rounds 1 and 2 contain variable words. Sums of constants are folded; a XOR with the constant 0 is dropped; an addition whose constants sum to 0 is dropped.
Hand count: a call whose state words are constants and whose two message words are variable costs 5 adds, 4 XORs and 4 rotations of 5 = 29. Round 0, diagonal call 5 adds v1 + v6 + m10 where v1 and v6 are the constants A1 and B2 of Section 8 with A1 + B2 = 0 mod 2^32:
the sum of the constants is zero, so the call starts from m10 alone and costs 28 (the other three cost 29): round 0 = 29 + 28 + 29 + 29 = 115.
A call with variable state costs 6 adds, 4 XORs, 20 = 30, and a zero message word (words m0..m7) saves its add: round 1 = 8 x 30 - 8 = 232, round 2 = 232 plus 2 masks (the tracer inserts an AND before a sum that
could reach 2^36; with a generic chaining value it inserts 3) = 234; the 8 digest XORs and 4 masks (words that are not clean) = 12. The tracer (`build_hash`, printed by `python3 rho.py --selftest`) emits exactly these: 115 + 232 + 234 + 12 =
593 = 99 add + 88 xor + 80 shr + 80 shl + 80 or + 166 and. The packed circuit agrees with the scalar digest (selftest, 70 inputs, and in every run of the experiment and of T3 below).
""" + s[j:]
rep("Cost per instance: 595/7 = 85 operations = 0.1332 unit", "Cost per instance: 593/7 = 84.7 operations = 0.1328 unit")
rep("One loop body = 16 * 595 + 34 + 3 + 1 = 9,558 operations (the previous entry: 9,587 per 16 batches).",
    "One loop body = 16 * 593 + 34 + 3 + 1 = 9,526 operations (the base entry: 9,558 with 595 per batch).")
rep("Charged per replayed batch: 595, call and return 2, per-batch test of w0 4 (add, and, compare, branch), 8 moves of the digest into the input registers, loop 3 = 612; plus 8 operations at the start, which is 16 * 612 + 8 = 9,800 = 16 * 595 + 280, charged as 16 * 595 + 300.",
    "Charged per replayed batch: 593, call and return 2, per-batch test of w0 4 (add, and, compare, branch), 8 moves of the digest into the input registers, loop 3 = 610; plus 8 operations at the start, which is 16 * 610 + 8 = 9,768 = 16 * 593 + 280, charged as 16 * 593 + 300.")
rep("each event is charged 300 + 16 * 595 + 300 = 10,120 operations.", "each event is charged 300 + 16 * 593 + 300 = 10,088 operations.")
rep("(both lanes run in one circuit, 595 operations)", "(both lanes run in one circuit, 593 operations)")
rep("charged as 64 per recovery batch (659 per batch).", "charged as 64 per recovery batch (657 per batch).")
rep("need no test (595 + 13), also inside the 659.", "need no test (593 + 13), also inside the 657.")
rep("| main loop: B * 9,558 / 16 | 28,988,314,850,931,136,125,279,250,899,965,499,016,632 (= 2.8988e40) |",
    "| main loop: B * 9,526 / 16 | 28,891,183,577,460,144,663,592,183,901,374,159,122,652 (= 2.8891e40) |")
rep("| stage-2 events: e2max * (300 + 16 * 595 + 300) | 1.6008e33 |", "| stage-2 events: e2max * (300 + 16 * 593 + 300) | 1.5957e33 |")
rep("| finished trails: 26,791 * (700 + 3 * 26,791) | 2,172,026,743 |", "| finished trails: 26,837 * (700 + 3 * 26,837) | 2,179,459,607 |")
rep("| recovery: (c + 2^48) * 659 + 600, c + 2^48 = 2^116.94 | 1.0512e38 |", "| recovery: (c + 2^48) * 657 + 600, c + 2^48 = 2^116.94 | 1.0453e38 |")
rep("| total N | 29,093,431,801,591,888,499,697,033,443,257,678,941,569 = 2.909343e40 operations |",
    "| total N | 28,995,720,170,841,641,432,943,050,661,225,930,338,820 = 2.899572e40 operations |")
rep("N / 638 = 4.5601e37 units = 2^125.100405. Claim `time_log2` = 125.10041 (integer power certificate in Appendix A, rounded up with 4.5e-6 of slack).",
    "N / 638 = 4.5448e37 units = 2^125.095551. Claim `time_log2` = 125.09556 (integer power certificate in Appendix A, rounded up with 4.5e-6 of slack).")
i = s.index("The three changes against the base")
j = s.index("### 3.5")
s = s[:i] + "Against the base entry (the same program with the 595-operation batch, CV = IV and flags 11: ledger 125.10041): the 593-operation batch with the re-selected Tp = 401 and a table of 26,837 entries gives 125.09556, a change of -0.00485 bit. The two-block message adds no operation to the loop: the chaining value is a constant of the circuit.\n\n" + s[j:]
rep("time_log2 = 125.1136 for R = 24, 125.1444 for R = 20 and 125.1973 for R = 16.", "time_log2 = 125.1088 for R = 24, 125.1397 for R = 20 and 125.1927 for R = 16.")

# ---- section 4
rep("(Q / L) e^-12 = 25,555 e^-12 = 0.157 (P(K=0,1,2) = 0.8547, 0.1342, 0.0105; P(K>=3) = 5.7e-4)",
    "(Q / L) e^-12 = 25,619 e^-12 = 0.1574 (P(K=0,1,2) = 0.8544, 0.1345, 0.0106; P(K>=3) = 5.8e-4)")
rep("0.1342 * 1.9e-4 + 0.0105 * 4.8e-4 + 5.7e-4 * 0.3916 = 2.56e-4", "0.1345 * 1.9e-4 + 0.0106 * 4.8e-4 + 5.8e-4 * 0.3916 = 2.57e-4")
rep("the key space is 2^55 * 400 = 2^63.6) is below 26,791^2 / 2 / 2^63.6 = 2.5e-11", "the key space is 2^55 * 401 = 2^63.65) is below 26,837^2 / 2 / 2^63.65 = 2.5e-11")
rep("mean Q / L = 25,555 (and", "mean Q / L = 25,619 (and")
rep("the abort needs 26,792 or more, probability at most exp(-mean) (e mean / 26,792)^26,792 = 2^-42.5 = 1.6e-13 (Chernoff bound)",
    "the abort needs 26,838 or more, probability at most exp(-mean) (e mean / 26,838)^26,838 = 2^-41.2 = 3.9e-13 (Chernoff bound)")
rep("6e-7 + 3.9e-5 + 2.56e-4 + 2.5e-11 + 1.6e-13 + 7.9e-31 < 2.96e-4, so P(success) >= 1 - e^-0.497 - 2.96e-4 = 0.3913 >= 0.39.",
    "6e-7 + 3.9e-5 + 2.57e-4 + 2.5e-11 + 3.9e-13 + 7.9e-31 < 2.97e-4, so P(success) >= 1 - e^-0.497 - 2.97e-4 = 0.3913 >= 0.39.")

# ---- section 5
rep("Heuristic H1 (premise, section 5): f behaves", "Heuristic H1 (premise, section 5): f (Section 1, last block with chaining value CV) behaves")
rep("Run on this entry's program: the 256 trials of the organizer experiment (section 6), and a check at n = 22 of 1,500 fresh attempts with the shipped search (a script outside the package): success 0.511 (the base program at its own n = 22 setting: 0.463), 62 halts. These show the construction works; they are not evidence about the premise at width 256.",
    "T1 to T3 and the other participant runs concern the function with chaining value IV (messages 0^32 || x). The function of this entry differs from it only in the 8 constant words of the chaining value and in v15 (10 instead of 11); H1 is declared for it as well and no participant run of T1 to T3 was made on it. The 256 trials of the organizer experiment (section 6) check the construction on this function; they are not evidence about the premise at width 256.")
rep("T1 to T3 are participant-run on the base entry's program", "T1 to T3 are participant-run on the older program")

# ---- section 6
rep("and returns the two messages 0^32 || x, 0^32 || y.", "and returns the two 128-byte messages P || 0^32 || x and P || 0^32 || y (P as in Section 8).")
rep("the table, the recovery and the message construction on the real target;", "the table, the recovery and the two-block message construction on the real target;")

# ---- section 7
rep("Table: 26,791 entries * 25 bytes = 669,775 bytes.", "Table: 26,837 entries * 25 bytes = 670,925 bytes.")
rep("Code: 10,408 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 374,688 bytes (main body 9,558,",
    "Code: 10,376 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 373,536 bytes (main body 9,526,")
rep("Total 1,048,559 bytes <= 2^20 = 1,048,576.", "Total 1,048,557 bytes <= 2^20 = 1,048,576.")
rep("tmax = floor((2^20 - 374,688 - 4,096) / 25) = 26,791, and Tp = 400 is the largest", "tmax = floor((2^20 - 373,536 - 4,096) / 25) = 26,837, and Tp = 401 is the largest")

# ---- section 8 (new), before Appendix A
i = s.index("## Appendix A.")
sec8 = """## 8. The prefix P and the message mode

Message mode (premise, declared as Heuristic H4): the attack uses messages of two blocks, P || 0^32 || x, instead of one block. The profile's message domain is any byte string shorter than 2^64 bits; the standard chunk rules apply to 128 bytes (one chunk, blocks of 64 bytes, flags 1 on the first block and 10 on the last), and Section 1 states the compression calls used. No other mode feature is used: no tree, no key, no counter other than 0.

P (the program's `PREFIX`) is the 64-byte string of 16 little-endian words w0 = i mod 2^32, w1 = floor(i / 2^32), w2..w15 = 0 with i = 10,768,619,076 (so w0 = 2,178,684,484 mod 2^32 and w1 = 2; the program computes them from `PREFIX_I`). Its chaining value is CV = chain_value(P) = (3205528875, 411291139, 60262883, 489927237, 809493467, 642014741, 3157960105, 1883752943) (printed by `python3 rho.py --selftest`).
The condition: in the last block, the column calls 1 and 2 of round 0 start from (CV[j], CV[j+4], IV[j], D[j]) with D = (0, 0, 64, 10) and message words 0; A1 is the value of v1 after call 1 and B2 the value of v6 after call 2. The first addition of diagonal call 5 of round 0 is v1 + v6 + m10 = (A1 + B2) + m10. The program function `prefix_condition()` computes (A1 + B2) mod 2^32; it is 0 for P, and `python3 rho.py --selftest` prints it.

Selection procedure (a bounded search done once, before the attack): scan i = 0, 1, 2, ... in order, form P(i) as above, compute CV(i) = chain_value(P(i)) and test (A1 + B2) mod 2^32 = 0; stop at the first success. A random CV passes with probability 2^-32 (heuristic: A1 + B2 is uniform); the first success was i = 10,768,619,076, after 10,768,619,077 first-block compressions (2^33.33), done with a C program of the same arithmetic (not shipped; its first-block output for i = 5 equals `chain_value` of the shipped program, checked) in two ranges, [0, 6 * 10^9) with no success and then from 6 * 10^9 up to the success; no earlier i passes. Anyone can verify the single claim (that P(i) passes) with the shipped program; that no smaller i passes is the result of the scan and costs the same scan to repeat. The claim's `preprocessing_log2` is 33.4; it is the cost of this scan in compressions and is not part of the attack's operation count.
The choice of P does not enter the attack (it fixes the constants of the circuit); it uses the one condition above only to remove two operations. Each further condition of the same kind would remove more operations and multiply the scan by 2^32; none was searched.

"""
s = s[:i] + sec8 + s[i:]

# ---- appendix
code = open("appA.py", encoding="utf-8").read().replace("B * 9558 / 16", "B * 9526 / 16")
out = open("appA.out", encoding="utf-8").read().replace("B * 9558 / 16", "B * 9526 / 16").replace("\r\n", "\n")
a = s.index("```python\n") + 10
b = s.index("```", a)
s = s[:a] + code + s[b:]
a = s.index("Output:\n\n```\n") + len("Output:\n\n```\n")
b = s.index("```", a)
s = s[:a] + out + s[b:]
open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok", len(s))
