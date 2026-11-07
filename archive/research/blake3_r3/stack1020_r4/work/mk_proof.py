# mk_proof.py: the r4 proof from the r3 proof of 2c5a749b (stack1020/pkg) with the r4 numbers (not shipped)
SRC = "../../stack1020/pkg/blake3/proof.md"
OUT = "../pkg/blake3/proof.md"
L = open(SRC, encoding="utf-8").read().split("\n")
new = {}

new[1] = "# blake3-r4: plain birthday with 256 bit-sliced lanes, three-addend pair-carry columns, a 32-byte prefix, a quotient-filter table and checkpoint recovery (B3R4s)"
new[3] = ("Credited derivative of mitchuski's 1b7bd746-17fa-429f-84f9-bbecc944ad38 (blake3 round 4, time_log2 124.80193: our b9f7a2bc program at four rounds with a "
          "9-gate pair-carry column for every all-variable a + b + m) and of our own 0ecdfe35-ba7a-4f74-8ba9-779d417974a2 (blake3 round 4, 124.86023: this program "
          "family at four rounds). The program is our round-3 entry 2c5a749b-e0db-4420-85fd-7b9b987efc33 (124.69481: the three-addend column of mitchuski's "
          "10ce9f59-80a1-4304-92cc-ca4dede3bbcc, the prefix, the stage-1 checkpoint, the quotient-filter table, the checkpoint recovery) run at four rounds, with the "
          "changes listed below. From the notes of 10ce9f59 and 1b7bd746 we took the column (the carry pair (u, U) = U ? 1 : 2u, its templates 0 and 1, the choice of "
          "addend order and template by a dry trial, the boundary columns) and re-implemented it in our generator and its C port; we did not use or run any file of "
          "either entry. The pair encoding is the modified double full adder of Demenkov, Kojevnikov, Kulikov and Yaroslavtsev (2010). The rest of the program is ours "
          "(Section 8), with the pivot full adder and the mask walk g = f XOR q of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123, re-implemented from its proof text.")
new[6] = "What changed against 2c5a749b (the same program at three rounds), each item in the program and counted in the ledger:"
new[7] = ("1. Four rounds: the step is 23,479 gates (the 28 all-variable a + b + m are ripples of carry pairs, Section 3.2); the prefix K comes from the same "
          "stated procedure run at four rounds (Section 3.7) and is the same K.")
new[8] = ("2. Stage 1 tests for ones: a point is a DP when its low 32 bits are all ones (and the window test). The 12 lowest planes are ANDed and one conditional "
          "branch on the AND being zero ends the batch, with no comparison (Section 3.3): 12 operations per batch; a passing batch ANDs the other 20 planes, branches "
          "on the hit mask and compares the batch counter with the next limit: 23 more. Passing batches are bounded by a halt at pmax = ceil((1 + 2^-10) B P12) + 64.")
new[9] = ("3. Loop control is the counter increment only (1 operation): the next limit (slice check or the halt at B) is compared on passing batches, so it is acted "
          "on at most 3,000 batches late except with probability below 2^-134 (Section 4, Step 7); the ledger charges B + 3,000 batches.")
new[10] = ("4. Memory: 775 registers (the 773 of the step, the batch counter and the limit); counters 5,248 bytes (the handlers address the planes in their registers, "
           "no plane copy); every instruction that is not a gate is charged 9 bytes (64 of them with a 256-bit immediate at 37 bytes); the trail number has 18 bits. "
           "The table holds 126,121 keys.")
new[11] = ("The plan follows: Tp = 1936, B, c and the table are re-planned. time_log2 124.79179 against our 0ecdfe35's 124.86023 (-0.06844) and against "
           "1b7bd746's 124.80193 (-0.01014). The premises are H1 and H3 of 2c5a749b; H3 here also declares the zero-test branch and the addressable register file (Section 3.1).")

new[21] = ("Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are all ones and the 90-bit number F = (x >> 32) mod 2^90 "
           "is below Tp = 1936. The density is theta = 1936 / 2^122 and L = 1 / theta = 2^111.0811. The key of a DP is the 40 bits of x above bit 121 followed by the "
           "11 low bits of F (F < 1936 <= 2^11, so those 11 bits are F): 51 bits.")
new[24] = ("2. After every batch the stage-1 test (Section 3.3) ANDs the 12 lowest planes. If the AND is zero (no lane has those 12 bits all ones) the batch ends. "
           "Otherwise (a passing batch) it ANDs the other 20 of the 32 low planes; the lanes with all 32 low bits ones are the stage-1 hits; then the batch counter is "
           "compared with the next limit (steps 4 and 5).")
new[26] = ("4. Slice checks: when the batch counter has passed the next multiple of S = 2^48 (compared on passing batches, so at the first passing batch at or after it), "
           "a lane whose trail has age >= c = 20 L batches is restarted with a new index (a cut trail).")
new[27] = ("5. The search halts (failure) at the first passing batch after B batches, after pmax passing batches, after e2max stage-1 hits, when the table holds "
           "tmax = 126,121 keys, when a second trail would be cut, or if step 6 halts or finds no pair.")
new[29] = ("Constants (computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = 1936, L = 2^122 / 1936, "
           "B = 1324569435497000000000000000000000000, Q = 256 B = 0.99650 * 2^128 evaluations, e2max = 2 B 256 / 2^32 + 64 = 157900981366276741027832031314, "
           "pmax = ceil((1 + 2^-10) B P12) + 64 = 80339480069056697871027175870700129 with P12 = 1 - (1 - 2^-12)^256 = 0.0605941 (the probability that 256 uniform "
           "lanes pass the first 12 planes), c = ceil(20 L) = 54926776685327102186107729763650603 (2^115.4031), c_r = ceil(12.4 L) = "
           "34054601544902803355386792453463374 (2^114.7134), D = 4157055852649267987718114313167, table capacity tmax = 126,121 keys in 126,122 slots of 7 bytes. "
           "The trail numbers t stay below 2^18 (256 starts, at most 126,121 finished trails, at most 1 cut trail: t <= 256 + 126,121 + 1 < 2^18), so the 18-bit field "
           "never overflows (the program asserts LANES + tmax + CMAX < 2^18 in its plan and t < 2^18 when it stores an entry); no length is stored.")

new[36] = ("This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 775 registers (a declared convention, H3, supporting). "
           "Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load and every store of a word, one operation each; "
           "every register move, one operation each. A conditional branch tests one register for zero (branch if zero or if nonzero, as RISC-V beqz and bnez); a "
           "comparison is a separate operation, charged wherever a branch needs one. The register file is memory (it is counted in Section 7) and is addressable: a load "
           "or store may name register j by its address.")
new[37] = ("The main loop has no loads, stores or moves: the generated straight line needs 773 registers (`allocate` assigns them; output plane j is written into the "
           "register that held input plane j, so the next batch reads the same registers); the batch counter and the limit take 2 more: R = 775. Between batches only "
           "registers 0 to 255 (the planes), the counter and the limit are live, so the stage-1 accumulator and the handlers' temporaries use registers 256 to 772, and "
           "the handlers read and write the planes in their registers 0 to 255 by address. The file of 775 registers is counted as memory: 24,800 bytes (Section 7).")
new[38] = ("Constants are immediates. The organizer's reference count C(r4) = 846 (14 + 208 r) is used only as the unit: Unit = 846 operations. Code is memory, and the "
           "cost model does not fix its format; this entry prices it. A gate of the step, of the stage-1 test or of the recovery circuit (XOR, AND or OR of two registers "
           "into a register) is one 40-bit instruction word, charged 5 bytes: an 8-bit opcode and three 10-bit register numbers (775 registers are below 1,024). The "
           "generator writes exactly these records (Section 3.6). Every other instruction (the branches of the stage-1 test, the limit compare and branch, loop control, "
           "handlers, setup, cut and slice, the recovery besides its circuit) is charged 9 bytes: an 8-bit opcode, three 10-bit register numbers and a 32-bit immediate "
           "(70 bits); at most 64 of them carry a 256-bit immediate instead (masks and constants of the handlers and the recovery), charged 37 bytes each. The WebAssembly "
           "image of the generator is charged 36 bytes per wasm instruction. The 5-byte and 9-byte words are prices stated by this entry (H3), not measurements.")
new[40] = "### 3.2 One batch = 23492 operations for 256 trails"
new[43] = ("Three-addend sums (`Gen.add3`, the column of 10ce9f59 and 1b7bd746). BLAKE3 computes a = a + b + m twice per G call. When all 96 planes of a, b and m are "
           "variable (28 times at four rounds; the first half of round 0 and every sum with a prefix word are partly constant and use two two-addend ripples), the three "
           "words are added in one ripple whose carry between columns is a pair of planes (u, U) standing for the value U ? 1 : 2u. Bit 0 is a pivot full adder whose "
           "carry enters as the pair (0, k). A column takes the three addend bits x, y, z and the incoming pair and returns the sum bit and the outgoing pair, "
           "x + y + z + c = s + 2 c':")
new[47] = ("For each of bits 1 to 30 the generator builds the six addend orders with the three forms as dry trials (the new gates are removed again) and keeps the "
           "first with the fewest new gates; bit 30 builds only U'; bit 31 is s = x ^ y ^ z ^ U (3 gates). At four rounds every such sum costs "
           "5 + 8 + 28 * 9 + 8 + 3 = 276 gates (two two-addend ripples: 308): the census of the 840 columns of bits 1 to 30 is 784 middle columns of 9 gates "
           "(559 template 0, 206 template 1, 19 form 2) and 56 boundary columns of 8 gates (33 template 0, 19 template 1, 4 form 2).")
new[50] = ("The generated line (`python3 bsrho.py --ledger`, `--selftest`): 23479 gates = 19189 XOR + 1798 AND + 2492 OR = **23479 operations**, no complement "
           "operation. Per trail 91.71 operations = 0.1084 unit, against 1 unit for a compression.")
new[54] = ("Loop body = one batch: 23479 + stage-1 test 12 + loop control 1 = 23492 operations. Stage 1 (`stage1`, `stage1_ops`): a DP has its 32 low bits all ones. "
           "The 12 lowest planes of digest word 0 (stored planes, upright: they are the planes of the next point) are ANDed (11 ANDs) into a register, and a conditional "
           "branch on that register being zero ends the batch: 12 operations (the AND is zero exactly when no lane has those 12 bits all ones, so no comparison is "
           "needed). On a passing batch the other 20 planes are ANDed into it (20) and a branch on zero skips the hit handler (1); the result is the hit mask (a lane is "
           "a stage-1 hit when its 32 low bits are all ones), so the handler needs no complement. Then the batch counter is compared with the next limit and a branch "
           "goes to the slice check or the halt (2): 23 more operations. The test loses no event: a DP has all 32 low bits ones, so its batch passes and its lane is a "
           "hit. Passing batches are counted and halt the run beyond pmax = ceil((1 + 2^-10) B P12) + 64 (Lemma 2, Step 7); they are charged at the budget: pmax * 23.")
new[55] = ("Loop control: the batch counter increment, 1 operation; the branch of the stage-1 test is the branch back to the top of the loop. The next limit (the next "
           "multiple of 2^48 or B, whichever is smaller) is compared only on passing batches (the 2 operations above), so a slice check and the halt at B come at the "
           "first passing batch at or after their batch: at most 3,000 batches late except with probability below 2^-134 (Section 4, Step 7). The main row is charged "
           "for B + 3,000 batches and the slice row for ceil((B + 3,000) / 2^48) checks.")
new[57] = ("- Stage-1 hit: per plane, read in place from its register (Section 3.1): load, shift right by the lane number, AND 1, shift left by the plane number, OR "
           "into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps "
           "of 5), window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit. The hit budget "
           "e2max is enforced by a halt.")
new[58] = L[57].replace("insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of "
                        "the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and "
                        "counters (below 200). Total below 3,550;",
                        "insertion of the 256 bits of the new start in the lane, in the plane registers: per plane load, shift, AND 1, shift left by the lane number, "
                        "AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), lane arrays and "
                        "counters (below 200). Total below 3,300;")
assert new[58] != L[57]
new[60] = (L[59].replace("the packed circuit on two lanes (609 operations, the last 8 of them the XORs with q)", "the packed circuit on two lanes (845 operations, the last 8 of them the XORs with q)")
           .replace("the DP test of each of the two lanes (low 32 bits: shift, AND, branch; window: shift, AND, compare, branch; 7 per lane, 14)",
                    "the DP test of each of the two lanes (low 32 bits all ones: shift, AND, compare, branch; window: shift, AND, compare, branch; 8 per lane, 16)")
           .replace("**609 + 36**", "**845 + 38**").replace("**609 + 39**", "**845 + 39**"))
assert new[60].count("845") == 3
new[61] = ("- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; "
           "fixed part charged 813,600. The generator: 688,414 primitive calls (two passes of 344,207 gate-constructor calls each, the dry trials of the three-addend "
           "columns included) and 23479 emitted lines, each charged 200 word operations: 142,378,600. Setup and generator together 143,192,200 operations.")
new[62] = "- Choice of the prefix K (offline, once; Section 3.7): 17,750,836,600 operations, charged in the time bound."
new[63] = ("Code: 24,355 gate words (the step 23479, the 31 ANDs of stage 1, the recovery circuit 845) and 1,335 other instructions (loop control 1, the branches of "
           "stage 1 2, the limit compare and branch 2, handlers 1,060: the plane loops, the event logic and 60 for the table walk; the recovery besides its circuit "
           "110: passes, checkpoints, bisection and moves; setup, cut and slice 160), of which at most 64 carry a 256-bit immediate.")
new[66] = ("All counts are upper bounds enforced by halts (Section 2, step 5); the halt at B and the slice checks are at most 3,000 batches late outside an event of "
           "probability below 2^-134 that is counted as a failure (Section 4, Step 7). The exact integers are printed by `python3 bsrho.py --ledger`; Appendix A "
           "recomputes them independently.")
new[69] = "| main loop: (B + 3,000) * 23492 | 31,116,785,178,695,524,000,000,000,000,000,070,476,000 (= 3.1117e+40) |"
new[70] = "| stage-1 rest: pmax * 23 | 1.8478e+36 |"
new[71] = "| slice checks: ceil((B + 3,000) / 2^48) * 1,300 | 6.118e+24 |"
new[72] = "| stage-1 hits: e2max * 2,800 | 4.4212e+32 |"
new[73] = "| finished trails: 126,121 * (3,800 + 64 * 126,122) | 1,018,503,756,568 |"
new[75] = "| recovery: c_r (845 + 38) + 8,192 * 80 + 17 D (845 + 39) + 16 * 100 + 600 | 3.0133e+37 |"
new[76] = "| setup and generator | 143,192,200 |"
new[77] = "| choice of the prefix K | 17,750,836,600 |"
new[78] = "N = 31,148,766,114,259,369,035,748,772,084,194,088,839,613 = 3.114877e+40 operations."
new[79] = ("N / 846 = 3.6819e+37 units = 2^124.791785. Claim `time_log2` = 124.79179 (integer power certificate in Appendix A). The main loop is 99.90 percent of N, "
           "the recovery 0.10 percent, the stage-1 rest 0.006 percent.")
new[82] = ("Convention H3: the machine has 775 registers of 256 bits. The generated line needs 773 (`allocate` gives the registers, 0 moves; the selftest executes the "
           "allocated code on a register file and compares it with the step); the batch counter and the limit take the other 2. The claim assumes R >= 775; 775 is "
           "declared and counted as 24,800 bytes of memory. The file is addressable (Section 3.1); the handlers use it to read and write the planes in place.")
new[86] = ("Its scratch (`gen_scratch`): use counts of 23,736 nodes, 23,737 bytes; signal state 2,400 (16 x 32 state words 2,048, two 32-word temporaries 256, the "
           "free-register bitmap 96); constant tables 256 (IV, K, permutation, G-call indices, the four synthesis columns); shadow stack 2,048; result record 68: "
           "28,509 bytes.")
new[87] = ("Layout. The setup phase holds the main code (at its final size, 135,582 bytes; it is written as the generator emits it), the advice K (32), the counters "
           "(5,248), the generator's code image (77,364) and its scratch (28,509): 246,735 bytes. The generator is never called after setup. In the search phase the "
           "same region holds the table (882,854 bytes) and the register file (24,800): main code + advice + counters + register file + table = 1,048,516 bytes. The "
           "memory of the entry is the larger of the two, 1,048,516 bytes.")
new[88] = ("Measured run of the generator (not the machine model, which is the byte account above): `GEN_C` compiled to WebAssembly (clang -Os, 2,048-byte shadow "
           "stack) and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: 23479 instructions, 773 "
           "registers, 23,736 nodes, 688,414 primitive calls (both passes), the same q, and the instruction text equal line by line to the Python generator's "
           "(sha256 b983945c520c59b919dea774097cfb3f691cbe5a2c730441dd0da8335b804177 for both). Its static arrays total 169,083 bytes; the guest uses 3 pages. It "
           "executes 42,533,234 wasm instructions, below the 142,378,600 word operations the ledger charges for the generator.")
new[92] = ("The prefix K is the result of a fixed procedure (`python3 bsrho.py --choose-key`, function `choose_key`): coordinate descent from the zero prefix over the "
           "words m0, ..., m7 in this order, each over the 16 values v * 2^28 (v = 0, ..., 15) in increasing order; a value is kept when the number of gates of the "
           "network (`trace(256, key)`, unused gates dropped) is smaller than the best so far; the sweeps repeat until one keeps nothing. At four rounds it made 241 "
           "evaluations (two sweeps) and returned K = (0x80000000, 0, 0x80000000, 0, 0x70000000, 0, 0, 0) with 23479 gates (the zero prefix: 23500). Each evaluation "
           "is charged as one pass of the generator, 200 operations per primitive call and per node; the sum over the 241 evaluations is 17,750,836,600 operations, a "
           "row of N (3.4). K is a constant of the program and of the generator (`KEY`), held in 32 bytes of memory (Section 7), and it is declared as nonuniform "
           "advice of 32 bytes (nonuniform_advice_log2_bytes = 5). The claim declares preprocessing_log2 = 24.34: log2((143,192,200 + 17,750,836,600) / 846) = "
           "24.3342, the setup and generator row and the choice of K, both inside time_log2. The memory figure covers the preprocessing: the generator runs in the setup "
           "phase (246,735 bytes); the choice of K runs before the attempt and leaves only K.")
new[95] = ("The scoring policy is `hashsmash-scalar-tm-v1`: score = time_log2 + max(0, memory_log2_bytes - 20). The program, its registers, counters, advice and table "
           "are 1,048,516 bytes (Section 7), not above 2^20 = 1,048,576; the claim states memory_log2_bytes = 20, and the term is 0: the scalar score is 124.79179.")

out = []
for i, l in enumerate(L, 1):
    out.append(new.get(i, l))
t = "\n".join(out)


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:100])
    t = t.replace(a, b)


# Section 1
rep("## 2. The attack (program", "## 2. The search (program")
rep("The attack outputs x != y", "The search outputs x != y")
rep("Target `blake3-r3-prefix-v1` (the benchmark's blake3 profile at 3 rounds)", "Target `blake3-r4-prefix-v1` (the benchmark's blake3 profile at 4 rounds)")
rep("flags 11 = CHUNK_START | CHUNK_END | ROOT, 3 rounds with", "flags 11 = CHUNK_START | CHUNK_END | ROOT, 4 rounds with")
rep("(this is `verifier/blake3.py:blake3(M(x), 3)`)", "(this is `verifier/blake3.py:blake3(M(x), 4)`)")
rep("fixed 256-bit mask (weight 124)", "fixed 256-bit mask (weight 147)")
rep("organizer reference `verifier/blake3.py:blake3(K || x, 3)`", "organizer reference `verifier/blake3.py:blake3(K || x, 4)`")
rep("The packed circuit (609 operations: the compression", "The packed circuit (845 operations: the compression")
# Section 4
rep("equal keys of two DPs differ only if their bits above 162 differ", "equal keys of two DPs differ only if their bits above 161 differ")
rep("The key determines F (F < 1913 <= 2^11", "The key determines F (F < 1936 <= 2^11")
rep("its 16 quotient bits, the slot stores the other 36 (Section 7)", "its 16 quotient bits, the slot stores the other 35 (Section 7)")
rep("The stage-1 test loses no event: a DP has its 32 low bits zero, so its batch passes the first 13 planes and its lane is a hit. A 52-bit key match",
    "The stage-1 test loses no event: a DP has its 32 low bits all ones, so its batch passes the first 12 planes and its lane is a hit. A 51-bit key match")
rep("Q = 256 B = 0.99652 * 2^128 evaluations numbered", "Q = 256 B = 0.99650 * 2^128 evaluations numbered")
rep("c = ceil(20 L) = 55587161350127166666128889086475466, c_r = ceil(12.4 L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 122005.65, tmax = 124,633,",
    "c = ceil(20 L) = 54926776685327102186107729763650603, c_r = ceil(12.4 L), S = 2^48, M = c + S + 3,000 (a slice check is at most 3,000 batches late, Step 7), N' = (1 - theta) N, q = Q / L = 123469.75, tmax = 126,121,")
rep("PP = Q (Q - 1) / (2 N') = 0.49652, H = (Q (Q - 1) / 2 + 2^17 Q) / N' = 0.49652. Let k = 124616 be",
    "PP = Q (Q - 1) / (2 N') = 0.49650, H = (Q (Q - 1) / 2 + 2^18 Q) / N' = 0.49650. Let k = 126096 be")
rep("P_coll = Pi_Q / (1 - k Q / N') = 0.608642804", "P_coll = Pi_Q / (1 - k Q / N') = 0.608656366")
rep("of [0, Q] of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.001272", "of [0, Q] of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.001257")
rep("P_own = Q L / N' = 8.139e-06", "P_own = Q L / N' = 8.042e-06")
rep("P_long = M Q p (q + 256) / ((1 - p) N') = 4.102e-08", "P_long = M Q p (q + 256) / ((1 - p) N') = 4.102e-08")
rep("P_age = PP p2 = 2.149e-08", "P_age = PP p2 = 2.149e-08")
rep("P_rec = 2 PP p2(12.4 L) = 5.481e-05", "P_rec = 2 PP p2(12.4 L) = 5.480e-05")
rep("P_dist = PP L (Q + 2^17) / N' = 4.041e-06", "P_dist = PP L (Q + 2^18) / N' = 3.993e-06")
rep("(Step 6) = 1.631e-05, with E_S", "(Step 6) = 1.611e-05, with E_S")
rep("E_J2a = Q L H / N' + (Q + 2^17) L PP / N'", "E_J2a = Q L H / N' + (Q + 2^18) L PP / N'")
rep("P_key = C(tmax, 2) / (2^kb Tp) = 1.846e-06, kb = 41,", "P_key = C(tmax, 2) / (2^kb Tp) = 3.736e-06, kb = 40,")
rep("P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 2.2e-12,", "P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 1.8e-12,")
rep("P_tiny = Q 2^17 / N + k^2 L / N' + 255 Q / N' + exp(-300 + (e^5 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q and 240 M <= 2^13 B P13, which hold here).",
    "P_tiny = Q 2^18 / N + k^2 L / N' + 255 Q / N' + exp(-300 + (e^5 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q and 2 M / 2^12 + 3,001 P12 <= 2^-11 B P12, which hold here).")
rep("P_F >= 0.39000000100041 >= 0.39 (the program's float value", "P_F >= 0.39000000100097 >= 0.39 (the program's float value")
rep("The starts r + t' (t' < 2^17) differ from every value the run produces except with probability Q 2^17 / N",
    "The starts r + t' (t' < 2^18) differ from every value the run produces except with probability Q 2^18 / N")
rep("the event that a start equals a value of the run (Q 2^17 / N)", "the event that a start equals a value of the run (Q 2^18 / N)")
rep("each a collision with conditional probability at most (Q + 2^17) / N' given the history", "each a collision with conditional probability at most (Q + 2^18) / N' given the history")
rep("PP L (Q + 2^17) / N' = P_dist.", "PP L (Q + 2^18) / N' = P_dist.")
rep("A long trail has at most M evaluations (it is cut at the first slice check at age >= c, or finishes before)",
    "A long trail has at most M evaluations (it is cut at the first slice check at age >= c, at most S + 3,000 batches after it reaches age c, or finishes before)")
rep("so E_S <= Q L / N' = 8.139e-06.", "so E_S <= Q L / N' = 8.042e-06.")
rep("E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 2.962e-08.", "E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 2.952e-08.")
rep("each such position is a collision with probability at most (Q + 2^17) / N': E_J2a2 <= (Q + 2^17) L Q (Q - 1) / (2 N'^2). E_J2a = 8.083e-06.",
    "each such position is a collision with probability at most (Q + 2^18) / N': E_J2a2 <= (Q + 2^18) L Q (Q - 1) / (2 N'^2). E_J2a = 7.986e-06.")
rep("E_J2b <= PP (1 - theta) p2 = 2.149e-08.", "E_J2b <= PP (1 - theta) p2 = 2.149e-08.")
rep("E_Y <= e^(-(c-1)/L) H = 1.023e-09.", "E_Y <= e^(-(c-1)/L) H = 1.023e-09.")
rep("P(Binomial(n2, p) >= 2) = 3.312e-08 and P_cut = 1.631e-05", "P(Binomial(n2, p) >= 2) = 3.391e-08 and P_cut = 1.611e-05")
# Step 7
rep("the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 2.2e-12); a key false match (P_key = 1.846e-06: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^41 * 1913 = 2^51.90);",
    "the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 1.8e-12); a key false match (P_key = 3.736e-06: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^40 * 1936 = 2^50.92);")
rep("the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 7.895e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2);",
    "the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 7.895e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t all ones] over the at most Q + 768,000 evaluations of the run (B + 3,000 batches, below), dominated by Binomial(Q + 768,000, 2^-32), above 1.5 (mu2 + 1) with probability at most e^(-0.108 mu2);")
rep("so with 240 M <= Q (checked: M = 5.559e+34, Q = 3.391e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000;",
    "so with 240 M <= Q (checked: M = 5.493e+34, Q = 3.391e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000;")
rep("the passing-batch budget pmax = 2 mu3 + 64, mu3 = B P13 = 4.076e+34, P13 = 1 - (1 - 2^-13)^256: a batch passes the first 13 planes only if one of its evaluations returns a value with the 13 low bits zero; for the fresh evaluations the batch indicator of some index t of the batch with the 13 low bits of V_t zero is exactly Bernoulli(P13), independent over batches (the V_t are independent and uniform on 256-bit values), so these batches are Binomial(B, P13), above 1.5 mu3 with probability at most e^(-0.108 mu3); the repeated evaluations are the at most 60 windows above, which hold more than 2 M / 2^13 values with the 13 low bits zero with probability at most e^(-0.386 M / 2^13), so with 240 M <= 2^13 mu3 (checked: 1.334e+37 <= 3.339e+38) the passing batches are below 2 mu3 except with probability below e^-1000;",
    "the passing-batch budget pmax = ceil((1 + 2^-10) mu3) + 64, mu3 = B P12 = 8.026e+34, P12 = 1 - (1 - 2^-12)^256: a batch passes the first 12 planes only if one of its evaluations returns a value with the 12 low bits all ones; given the history, a batch has such a fresh evaluation with probability at most P12 (at most 256 fresh evaluations, each uniform on 256-bit values and independent of the history), so these batches among the at most B + 3,000 batches are dominated by Binomial(B + 3,000, P12), above (1 + 2^-11)(mu3 + 3,000 P12) with probability at most exp(-2^-22 mu3 / 3) (Chernoff); the repeated evaluations are the at most 60 windows above, which hold more than 2 M / 2^12 values with the 12 low bits all ones with probability at most e^(-0.386 M / 2^12), so with 2 M / 2^12 + 3,001 P12 <= 2^-11 mu3 (checked: 2.682e+31 <= 3.919e+31) the passing batches are at most pmax except with probability below e^-1000; the late limits: the batch counter is compared with the next limit (the next multiple of S, or B) only on passing batches; outside 60 or more collisions and E1 at most 60 lanes of a batch evaluate a non-fresh input (a non-fresh evaluation follows a collision on its trail), so a batch has at least 196 fresh evaluations, each uniform and independent of the history, and fails to pass with conditional probability at most (1 - 2^-12)^196; 3,000 consecutive batches without a passing batch have probability at most (1 - 2^-12)^588,000 < 2^-207, and with at most ceil((B + 3,000) / S) + 1 < 2^73 limits every slice check and the halt come at most 3,000 batches after their batch except with probability below 2^-134 (the time bound N, which charges B + 3,000 batches, holds outside this event, counted as a failure; a late slice check cuts only trails of age >= c, so Step 3 is unchanged, and M = c + S + 3,000 bounds every length);")
rep("and 2^-90 for everything else of this step (the stage-1 and passing-batch budgets, the recovery with no pair)",
    "and 2^-90 for everything else of this step (the stage-1 and passing-batch budgets, the late limits, the recovery with no pair)")
rep("= 1 - 0.608642804 - 0.001272 - 8.139e-06 - 4.102e-08 - 2.149e-08 - 5.481e-05 - 4.041e-06 - 1.631e-05 - 9.1e-13 - 1.846e-06 - 2.2e-12 - P_tiny = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact evaluation of Appendix A is 0.39000000100041 >= 0.39",
    "= 1 - 0.608656366 - 0.001257 - 8.042e-06 - 4.102e-08 - 2.149e-08 - 5.480e-05 - 3.993e-06 - 1.611e-05 - 9.1e-13 - 3.736e-06 - 1.8e-12 - P_tiny = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact evaluation of Appendix A is 0.39000000100097 >= 0.39")
rep("0.0073 bit for eps = 0.01 (Tp 1903); 0.0370 bit for eps = 0.05 (Tp 1864); 0.0760 bit for eps = 0.10 (Tp 1815); 0.2075 bit for eps = 0.25 (Tp 1656).",
    "0.0073 bit for eps = 0.01 (Tp 1926); 0.0370 bit for eps = 0.05 (Tp 1887); 0.0760 bit for eps = 0.10 (Tp 1837); 0.2075 bit for eps = 0.25 (Tp 1676).")
# Section 5
rep("(c) whether an iterate is a DP is independent of the collision events and has probability 1913 / 2^122;", "(c) whether an iterate is a DP is independent of the collision events and has probability 1936 / 2^122;")
# Section 6
rep("(DP = low 2 bits zero, plan(18): 8 batches,", "(DP = low 2 bits all ones, plan(18): 8 batches,")
rep("The checked event is that the complete 3-round digests agree in the low 18 bits", "The checked event is that the complete 4-round digests agree in the low 18 bits")
rep("Running times on the development machine for 256 trials: 3.5 s and 5.1 s.", "Running time on the development machine for 256 trials of each: 9.3 s for the two.")
# Section 7
rep("Table: 124,634 slots * 7 bytes = 872,438 bytes", "Table: 126,122 slots * 7 bytes = 882,854 bytes")
rep("S = tmax + 1 = 124,634 slots, l = floor(log2 S) = 16. The 52-bit key is split into the quotient (its top 16 bits), which is the home slot, and the remainder (36 bits). A slot holds 56 bits: the remainder, the 17-bit trail number t",
    "S = tmax + 1 = 126,122 slots, l = floor(log2 S) = 16. The 51-bit key is split into the quotient (its top 16 bits), which is the home slot, and the remainder (35 bits). A slot holds 56 bits: the remainder, the 18-bit trail number t")
rep("At most tmax = 124,633 keys are stored", "At most tmax = 126,121 keys are stored")
rep("Code: 17,186 gate words * 5 bytes (the step 16546, the 31 ORs of stage 1, the recovery circuit 609) + 1,337 other instructions * 36 bytes (loop control 3, the stage-1 compares and branches 4, handlers 1,060, recovery besides its circuit 110, setup, cut and slice 160) = 85,930 + 48,132 = 134,062 bytes.",
    "Code: 24,355 gate words * 5 bytes (the step 23479, the 31 ANDs of stage 1, the recovery circuit 845) + 1,335 other instructions * 9 bytes (loop control 1, the stage-1 branches 2, the limit compare and branch 2, handlers 1,060, recovery besides its circuit 110, setup, cut and slice 160) + 64 * 28 bytes (at most 64 of them with a 256-bit immediate, 37 bytes each) = 121,775 + 12,015 + 1,792 = 135,582 bytes.")
rep("Counters and copies: 16,384 bytes (trail numbers, birth batches, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 800 registers: 25,600 bytes. Advice K: 32 bytes. Memory peak = max(setup phase 249,418, search phase 1,048,516)",
    "Counters: 5,248 bytes (trail numbers 256 x 4, birth batches 256 x 16, counters 128; the handlers read and write the planes in their registers, so there is no plane copy). The 775 registers: 24,800 bytes. Advice K: 32 bytes. Memory peak = max(setup phase 246,735, search phase 1,048,516)")
rep("tmax = floor((1,048,576 - 64 - 134,062 - 25,600 - 16,384 - 32) / 7) = 124,633, and the extra slot comes out of the 64 bytes. Tp = 1913 is the largest integer",
    "tmax = floor((1,048,576 - 64 - 135,582 - 24,800 - 5,248 - 32) / 7) = 126,121, and the extra slot comes out of the 64 bytes. Tp = 1936 is the largest integer")
# Section 8
rep("H3 (the 800-register machine convention and the instruction charges, 5 bytes per register-only gate and 36 bytes per other instruction, supporting).",
    "H3 (the 775-register machine convention with the zero-test branch and the addressable register file, and the instruction charges, 5 bytes per register-only gate and 9 bytes per other instruction, 37 for at most 64 with a 256-bit immediate, supporting).")
rep("Credited to mitchuski's 10ce9f59: the three-addend column with the carry pair, its templates 0 and 1, the boundary columns and the choice of order and template by a dry trial (Section 3.2), re-implemented from its note;",
    "Credited to mitchuski's 10ce9f59 (round 3) and 1b7bd746 (round 4, the round-4 entry this one is compared with): the three-addend column with the carry pair, its templates 0 and 1, the boundary columns and the choice of order and template by a dry trial (Section 3.2), re-implemented from their notes;")
rep("Ours: 3c2d1220 (this program at three rounds with 10-byte entries; the search, handlers, recovery passes, ledger method, experiments and Section 4), b9f7a2bc (the same program at seven rounds), and their lineage",
    "Ours: 2c5a749b (this program at three rounds), 0ecdfe35 (our round-4 entry of this family), 3c2d1220 (the search, handlers, recovery passes, ledger method, experiments and Section 4), b9f7a2bc (the same program at seven rounds), and their lineage")
rep("New here: the stage-1 checkpoint, the quotient-filter table, the checkpoint recovery with its cap and the prefix choice, each charged.",
    "New here: the stage-1 test for ones with the zero-test branch, the loop control of one operation with the limits on passing batches, and the memory account of Section 7, each charged.")
assert t.count("2^17") == 5
t = t.replace("2^17", "2^18")
# Appendix A
i0 = t.index("The ledger was recomputed by a separate program")
t = t[:i0] + open("appendix_a.md", encoding="utf-8").read()
open(OUT, "w", encoding="utf-8", newline="\n").write(t if t.endswith("\n") else t + "\n")
for bad in ("16546", "16563", "124.69481", "1913", "124,633", "609 ", "638", "2^17", "800 registers", "R = 800", "13 low", "P13", "low 32 bits zero", "3 rounds", "blake3-r3"):
    print("left:", bad, t.count(bad))
print("ok", len(t))
