000001 | # blake3-r3: plain birthday with seven packed lanes and distinguished points
000002 | 
000003 | No differential, no structure of the 3-round compression is used. The claim is the price of the birthday attack on the complete
000004 | 3-round hash when the compression is evaluated seven instances at a time in 256-bit words and every operation is counted.
000005 | 
000006 | ## 1. Target and relation
000007 | 
000008 | Target `blake3-r3-prefix-v1`. For a 256-bit integer x let M(x) be the 64-byte message `0^32 || x` (x little endian). It is one chunk
000009 | with one block, so the complete hash is the root compression of that block: chaining value IV, words m0..m7 = 0, m8..m15 = the eight
000010 | little-endian words of x, counter 0, block length 64, flags 11 = CHUNK_START|CHUNK_END|ROOT, rounds 0..2, feed-forward v[i] XOR v[i+8]
000011 | for i < 8, digest = the 8 words, little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit
000012 | little-endian integer. The attack outputs x != y with f(x) = f(y); then M(x) != M(y) are two distinct messages in the domain with equal
000013 | 256-bit digests. The program checks the scalar digest `f_scalar` (section 1 of the program) against the organizer reference on 2000
000014 | messages and rounds 1..7, and the 7-, 2- and 1-round digests of the 64-byte block against the organizer test vectors (`tests/fixtures/blake3-vectors.json`).
000015 | 
000016 | ## 2. The attack (program `experiments/rho.py`, sections 3 and 4)
000017 | 
000018 | Parameters for n = 256: theta = 2^-114, N = 2^256, L = 2^114, seven lanes. One fresh uniform 256-bit word r (one operation).
000019 | Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a distinguished point (DP): a value whose low 114 bits are zero.
000020 | 1. Seven trails run in the seven lanes of the circuit of section 3. A batch is one evaluation of all seven lanes. Batch counter b = 0, 1, ...
000021 | 2. After each batch: filter on digest word 0 of all seven lanes (4 operations, section 3.3). If no lane has word 0 = 0, continue with the digests as the next inputs.
000022 | 3. If some lane has word 0 = 0 (a stage-2 event): for each lane test the other 82 bits. A lane at a DP ends its trail: key = (value >> 114) mod 2^64,
000023 |    length = batches since the trail started. If the key is in the table, go to 5. Otherwise store (t, length) under the key, start trail t' = next index in that lane.
000024 | 4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 12 * 2^114 batches is restarted with a new index (a cut trail).
000025 |    The search halts (failure) after B batches, after E2 stage-2 events, when the table holds 18,432 keys, or if step 5 finds no pair.
000026 | 5. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps, then step both together; at the first step
000027 |    with f(a) = f(b) and a != b output (a, b). Both lanes of one circuit are used. At most capr = c + S batches are run.
000028 | Constants: B = 48,556,072,151,761,189,409,716,612,589,674,249,048 (= 0.99885 * 2^128 / 7, rounded up), E2 = 158,274,781,453,576,090,684,168,174,986,
000029 | table capacity 18,432 entries of 32 bytes. Every one of these is computed by `plan(256)` of the program from the stated formulas.
000030 | Per attempt: one fresh r; no restart, no amplification, no stored collision, no advice (K = 0).
000031 | 
000032 | ## 3. Operation ledger
000033 | 
000034 | ### 3.1 Machine
000035 | Classical load/store machine with 256-bit words and 64 registers, as in the cost model's word RAM; constants are immediates. Charged: every
000036 | addition, AND, OR, XOR, shift, comparison, conditional branch, and the one random word. Memory traffic would be charged too, but the inner loop has none:
000037 | the 16 state words, the 8 message words and at most 8 temporaries are registers (the digest registers of a batch are the input registers of the next copy of
000038 | the unrolled body). The organizer's own count of the reference compression, C(r3) = 638 (`scripts/reference_operation_costs.py` extended to 3 rounds; 222, 430 and 638 for 1, 2
000039 | and 3 rounds) also excludes loads and stores. Unit = 638 operations.
000040 | 
000041 | ### 3.2 One batch = 595 operations
000042 | Lane layout: 36-bit lanes (32 data bits, 4 guard bits), 7 lanes per word. A lane value stays below 2^36 (the tracer keeps the bound of every value
000043 | and inserts an AND with 0xFFFFFFFF per lane before any sum that could reach 2^36). Sums of packed words are exact because no lane carries out of 36 bits.
000044 | XOR is bitwise. Rotation of a lane by r (valid for lane values below 2^36, guard bits arbitrary): ((t >> r) AND A_r) OR ((t << (32-r)) AND B_r), A_r keeping bits
000045 | 0..31-r and B_r keeping bits 32-r..31 of every lane. Check: the right shift brings bits r..35 of a lane down to 0..35-r and bits 0..r-1 of the next lane to
000046 | 36-r..35, outside A_r; the left shift puts bit j of a lane at j+32-r, bits j < r land in 32-r..31 (kept) and bits j >= r land at 32 or above, in a position that is
000047 | either above bit 31 of the same lane or at 28-r..31-r of the next lane, below 32-r (not kept). So 5 operations (shr, and, shl, and, or) and no mask before the XOR is needed.
000048 | Constants (same in every lane) are folded at build time and cost nothing: the four column calls of round 0 depend only on m0..m7 = 0 and IV, so only the four diagonal calls of round 0 and
000049 | all calls of rounds 1 and 2 contain variable words. Sums of constants are folded; a XOR with the constant 0 is dropped.
000050 | Hand count: a call whose state words are constants and whose two message words are variable costs 5 adds, 4 XORs and 4 rotations of 5 = 29 (round 0, diagonal calls: 4 x 29 = 116);
000051 | a call with variable state costs 6 adds, 4 XORs, 20 = 30, and a zero message word (words m0..m7) saves its add: round 1 = 8 x 30 - 8 = 232, round 2 = 232 plus 3 masks (the tracer inserts an AND before a sum that
000052 | could reach 2^36) = 235; the 8 digest XORs and 4 masks (words that are not clean) = 12. The tracer (`build_hash`, printed by `python3 rho.py --selftest`) emits exactly these: 116 + 232 + 235 + 12 =
000053 | 595 = 100 add + 88 xor + 80 shr + 80 shl + 80 or + 167 and. The packed circuit agrees with the scalar digest (selftest, 70 inputs, and in every run of the experiment and of T3 below).
000054 | Cost per instance: 595/7 = 85 operations = 0.1332 unit, against 1 unit for a compression.
000055 | 
000056 | ### 3.3 Filter, loop, and the other events
000057 | Filter on digest word 0 of the seven lanes (clean values): t = w0 + 0xFFFFFFFF in every lane (add); u = t AND (bit 32 of every lane) (and); compare u with the all-lanes pattern (compare); branch.
000058 | Bit 32 of a lane is set iff the lane's word 0 is nonzero, and sums stay below 2^33. 4 operations per batch. The loop body is the batch repeated 16 times (unrolled, 16 * (595 + 4) = 9,584) plus
000059 | counter increment, compare and branch (3): 9,587 operations per 16 batches.
000060 | Upper bounds charged per event: stage-2 event 300 operations (7 lanes: shift, AND, compare, branch, plus the word 1..3 tests of a hit lane), finished trail 700 (extract 8 words, key,
000061 | scan of at most 18,432 table keys at 3 operations each is charged separately below, write entry, new start: add, 8 word splits and 8 lane insertions), slice check (every 2^48 batches) 100, recovery batch 595 + 24 + 1.
000062 | Initial constant folding and setup 2,000.
000063 | 
000064 | ### 3.4 Total
000065 | All counts are upper bounds enforced by halts (section 2, step 4).
000066 | | item | bound (operations) |
000067 | | --- | --- |
000068 | | main loop: B * 9,587 / 16 | 58,188,382,964,866,815,358,869,145,612,150,878,202,897 / 2 (= 2.909419e40) |
000069 | | slice checks: ceil(B / 2^48) * 100 | 1.725e25 |
000070 | | stage-2 events: E2 * 300 (E2 = twice the expected number + 64) | 4.748e31 |
000071 | | finished trails: 18,432 * (700 + 3 * 18,432) | 1,032,118,272 |
000072 | | recovery: capr * 620 + 600, capr = 12 * 2^114 + 2^48 = 2^117.585 | 1.5452e38 |
000073 | | setup | 2,000 |
000074 | | total | 2.924871e40 operations |
000075 | Total / 638 = 4.58444e37 units = 2^125.10808. Claim `time_log2` = 125.1081 (rounded up). The main loop is 99.47 percent of it, recovery 0.53 percent.
000076 | `python3 rho.py --ledger` prints the exact integers. The random word counts 1 operation and is inside the setup bound.
000077 | 
000078 | ## 4. Success probability
000079 | 
000080 | Heuristic H1 (premise, section 5): f behaves as a random mapping on N = 2^256 points for the points the search evaluates: for every set of distinct inputs, the outputs are
000081 | uniform and independent, and whether a value is a DP is an independent event of probability 2^-114. Then (sub-claims proved here, Lemma 2 is a computation under H1):
000082 | 
000083 | Lemma 1. A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and
000084 | the stored lengths let step 5 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut once its age is >= c, and ages grow by at most S between checks).
000085 | A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).
000086 | 
000087 | Lemma 2. Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 7B = 0.99885 * 2^128. The unfinished trails hold at most 7 ages, each
000088 | exponential with mean L (memoryless DP), so their sum exceeds 28 L with probability e^-28 * sum_{j<7} 28^j/j! = 5.8e-7. Cut trails cost at most c = 12 L each; their expected loss is
000089 | below 7.4e-5 Q, charged as 1.5e-4 Q. Hence U >= 0.99985 Q - 28 L - 1 = 0.99700 * 2^128 except with probability 6e-7 (plus about 4.5e-5 from the discrete number of cut trails). For U distinct inputs the probability of no colliding pair is
000090 | prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^-14.0. The expected number of 64-bit key false matches is below 2^-36.
000091 | The losses add to 6e-7 + 6.1e-5 + 4.5e-5 + 3e-11 < 1.2e-4, so P(success) >= 1 - e^-0.497 - 1.2e-4 = 0.3915 >= 0.39. The 0.0015 left over is kept as margin.
000092 | If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0047, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.
000093 | 
000094 | ## 5. Premise H1 and its evidence
000095 | 
000096 | H1 has three parts: (a) f has no collision structure at the scales used (the pair-collision rate of the evaluated inputs is 2^-256 per pair); (b) the iterates of f from the starts r + t
000097 | have the first-collision law of a random mapping; (c) the DP indicator is independent of the collision events. Parts (a) and (b) are premises on the fixed function f, K = 0, and cannot be tested at width 256. What was run (frozen
000098 | protocol written before the runs (sources and outputs kept with the entry), no run repeated):
000099 | T1 (family law, 3 rounds, fresh random 256-bit K per run, chain truncated to n bits): n = 32, 2000 runs: mean first-repeat time / sqrt(pi N/2) = 1.0075 (z 0.64), E[T^2]/2N = 1.020 (z 0.88), KS 0.78; n = 40, 300 runs: ratio 0.9712 (z -0.95), E[T^2]/2N = 0.977 (z -0.41), KS 1.36 (0.1 percent critical value 1.949). Pass.
000100 | T2 (the fixed K = 0 function at full width 256, 2^26 points per statistic, observed equal pairs of a projection against C(2^26,2)/2^bits; sources: iterates of f from a random start, inputs r + i, uniform inputs; 14 projections each): 42 statistics (3 sources x 14 projections): observed/expected between 0.9546 and 1.0342, z between -2.29 and 1.55 (largest |z| 2.29 against the bound 4.5), mean z -0.46. Pass.
000101 | T3 (the shipped search, plan(n), one attempt per fresh r, on the target chain K = 0 and on an ideal function of the same width): n = 32 (d = 8, Q = 72,527 evaluations, pure-birthday value 0.458), 4000 attempts each: target 1772 successes (0.443), ideal 1814 (0.4535), two-proportion z = -0.94; n = 40 (d = 12, Q = 1,160,292, 0.458), 480 attempts each: target 211 (0.440), ideal 226 (0.471), z = -0.97; every returned pair re-checked (0 bad pairs); 3 to 6 attempts per 1000 halted in both conditions. Pass. The observed rates sit below the pure-birthday value by the in-flight and cut losses of section 4, as planned.
000102 | Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K. Fixed-K first-repeat times from random starts are not independent samples (one functional graph); they were seen
000103 | to deviate from the law by 0.70 to 1.65 for n = 16..36 in unrecorded smoke runs and are not evidence either way. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of section 4.
000104 | 
000105 | ## 6. Experiment `rho-n22`
000106 | 
000107 | The organizer runs the same program at n = 22 (section 5 of the program): DP bits 4, 7 lanes, budgets from `plan(22)`, up to 60 fresh attempts per trial (success amplification is used only by the experiment),
000108 | and returns the two messages 0^32 || x, 0^32 || y. The organizer recomputes the 3-round digests and checks that they agree in the low 22 bits and the messages are distinct. This checks the circuit, the trail
000109 | bookkeeping, the table, the recovery and the message construction on the real target; it does not measure the cost or the success probability at width 256, and the observation counters are the program's own.
000110 | 
000111 | ## 7. Memory
000112 | 
000113 | Table: 18,432 entries * 32 bytes = 589,824 bytes (key 8, index 8, length 16). Code: at most 10,400 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 374,400 bytes
000114 | (main body 9,587, recovery 640, handlers about 170). Counters and ages: below 2,048 bytes. Total 966,272 bytes = 2^19.88 <= 2^20. Claim `memory_log2_bytes` = 20.
