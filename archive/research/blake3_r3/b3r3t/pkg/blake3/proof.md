# blake3-r3: plain birthday with seven packed lanes, a grouped filter and mixed distinguished points

Credited derivative of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (blake3 round 3, score 125.1087, still in review). That entry has no lineage of its own: its
construction (the seven-lane 36-bit packed circuit of 595 operations, distinguished points, the recovery walk, the ledger and the premise tests T1 to T3) is the
base of this one. This entry keeps all of it and changes three things, each priced separately in the ledger: (1) a filter that tests 16 batches at once and replays
the 16 only when it fires, (2) distinguished points of density 400 / 2^122 instead of 2^-114, (3) 25-byte table entries so that more trails fit in 2^20 bytes.
Measured with the program's own ledger, the first gives 0.00435 bit, the second and third together 0.00380 bit, all three 0.00816 bit (125.10856 to 125.10040).
No differential, no structure of the 3-round compression is used. The claim is the price of the birthday attack on the complete 3-round hash when the compression is
evaluated seven instances at a time in 256-bit words and every operation is counted.

## 1. Target and relation

Target `blake3-r3-prefix-v1`. For a 256-bit integer x let M(x) be the 64-byte message `0^32 || x` (x little endian). It is one chunk
with one block, so the complete hash is the root compression of that block: chaining value IV, words m0..m7 = 0, m8..m15 = the eight
little-endian words of x, counter 0, block length 64, flags 11 = CHUNK_START|CHUNK_END|ROOT, rounds 0..2, feed-forward v[i] XOR v[i+8]
for i < 8, digest = the 8 words, little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit
little-endian integer. The attack outputs x != y with f(x) = f(y); then M(x) != M(y) are two distinct messages in the domain with equal
256-bit digests. The scalar digest of the program (`digest_words`, section 1 of the program) was compared outside the shipped experiment with the organizer reference on 2,002
messages (rounds 1..7, 286 each, 0 differences) and with the 7-, 2- and 1-round digests of the 64-byte block in the organizer test vectors (`tests/fixtures/blake3-vectors.json`, 3 of 3); the program's own selftest compares the packed circuit with its scalar digest.

## 2. The attack (program `experiments/rho.py`, sections 3 and 4)

Parameters for n = 256: N = 2^256, seven lanes, groups of U = 16 batches. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is
below Tp = 400. The density is theta = 400 / 2^122 = 2^-113.3561 and L = 1 / theta = 2^113.3561 (the previous entry used theta = 2^-114). The key of a DP is the 55 bits of x above bit 121 followed by the 9 low bits of F (F < 400 < 2^9, so those 9 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. Seven trails run in the seven lanes of the circuit of section 3. A batch is one evaluation of all seven lanes. Batch counter b = 0, 1, ...
2. A group is 16 consecutive batches. During a group only the grouped filter of section 3.3 runs: for each batch one addition on digest word 0 of the seven lanes, and one AND into an accumulator. The 8 input words of the group's first batch are not overwritten during the group.
3. If the accumulator shows that in all 16 batches all seven lanes had word 0 nonzero, the group is done and its last digests are the next inputs. Otherwise the group is replayed from its saved inputs, one batch at a time, each with the per-batch test of word 0 (4 operations, section 3.3):
   in a replayed batch with a lane whose word 0 is zero (a stage-2 event) each such lane is tested for the DP property. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, section 7) and start trail t' = next index in that lane.
4. At every multiple of S = 2^48 batches (always a group boundary): a lane whose trail has age >= c = 12 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-2 events, when the table holds 26,791 keys, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps, then step both together; at the first step
   with f(a) = f(b) and a != b output (a, b). Both lanes of one circuit are used. At most capr = c + S batches are run.
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 rho.py --ledger`): Tp = 400, L = 332306998946228968225951765070086144 / 25, B = 48,526,160,035,038,520,402,225,153,211,911,276,864 (a multiple of 16; Q = 7B = 0.99824 * 2^128 evaluations),
e2max = 158,177,279,050,121,848,851,244,930,467, c = 159,507,359,494,189,904,748,456,847,233,641,350 (= 2^116.94), table capacity tmax = 26,791 entries of 25 bytes. The trail numbers t stay below 2^15 (finished trails <= 26,791, cut trails <= Q / c + 7 = 2,136, plus the 7 starts) and every length is below c + S < 2^117, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision, no advice (K = 0).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry (the benchmark profile fixes 256-bit words and charges loads and stores, and does not fix a register count): a load/store machine with 256-bit words, 256-bit immediates and R registers. Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each (one move per loop body is needed and charged, section 3.3). The main loop keeps its working set in registers, so it has no loads or stores. The tracer reports the high-water mark of live words (`python3 rho.py --selftest`): 25 values in one batch, and 34 with the group's 8 saved input words and the filter accumulator, so R >= 34 is sufficient for the main loop. Table lookups, the recovery and the events are charged with their loads and stores (section 3.4). Constants are immediates. The memory total of section 7 counts a file of 64 registers (2,048 bytes) as memory as well.
The organizer's reference count C(r3) = 638 (`scripts/reference_operation_costs.py` extended to 3 rounds; 222, 430 and 638 for 1, 2 and 3 rounds) is used only as the unit: Unit = 638 operations. It is not claimed to define the register file. A smaller register file is priced in section 3.5.

### 3.2 One batch = 595 operations
Lane layout: 36-bit lanes (32 data bits, 4 guard bits), 7 lanes per word. A lane value stays below 2^36 (the tracer keeps the bound of every value
and inserts an AND with 0xFFFFFFFF per lane before any sum that could reach 2^36). Sums of packed words are exact because no lane carries out of 36 bits.
XOR is bitwise. Rotation of a lane by r (valid for lane values below 2^36, guard bits arbitrary): ((t >> r) AND A_r) OR ((t << (32-r)) AND B_r), A_r keeping bits
0..31-r and B_r keeping bits 32-r..31 of every lane. Check: the right shift brings bits r..35 of a lane down to 0..35-r and bits 0..r-1 of the next lane to
36-r..35, outside A_r; the left shift puts bit j of a lane at j+32-r, bits j < r land in 32-r..31 (kept) and bits j >= r land at 32 or above, in a position that is
either above bit 31 of the same lane or at 28-r..31-r of the next lane, below 32-r (not kept). So 5 operations (shr, and, shl, and, or) and no mask before the XOR is needed.
Constants (same in every lane) are folded at build time and cost nothing: the four column calls of round 0 depend only on m0..m7 = 0 and IV, so only the four diagonal calls of round 0 and
all calls of rounds 1 and 2 contain variable words. Sums of constants are folded; a XOR with the constant 0 is dropped.
Hand count: a call whose state words are constants and whose two message words are variable costs 5 adds, 4 XORs and 4 rotations of 5 = 29 (round 0, diagonal calls: 4 x 29 = 116);
a call with variable state costs 6 adds, 4 XORs, 20 = 30, and a zero message word (words m0..m7) saves its add: round 1 = 8 x 30 - 8 = 232, round 2 = 232 plus 3 masks (the tracer inserts an AND before a sum that
could reach 2^36) = 235; the 8 digest XORs and 4 masks (words that are not clean) = 12. The tracer (`build_hash`, printed by `python3 rho.py --selftest`) emits exactly these: 116 + 232 + 235 + 12 =
595 = 100 add + 88 xor + 80 shr + 80 shl + 80 or + 167 and. The packed circuit agrees with the scalar digest (selftest, 70 inputs, and in every run of the experiment and of T3 below).
Cost per instance: 595/7 = 85 operations = 0.1332 unit, against 1 unit for a compression. The tracer is shipped in the program; the organizer experiment does not meter cost.

### 3.3 Grouped filter, loop, replay and the other events
Grouped filter (replaces the per-batch filter of 4 operations): after each batch, u = w0 + 0xFFFFFFFF in every lane (1 add; w0 is digest word 0 of the seven lanes, clean, so each lane of u is below 2^33 and bit 32 of a lane is set iff that lane's w0 is nonzero);
the first batch's u starts the accumulator, each later batch does acc = acc AND u (1 operation, 15 in all). After the 16th batch: t = acc AND (bit 32 of every lane) (1), compare t with that pattern (1), branch (1). Bit 32 of a lane of acc is set iff the lane's w0 was nonzero in all 16 batches.
Count: 16 + 15 + 3 = 34 operations per group, against 64 for 16 per-batch filters. The program executes exactly this (`search`, accumulator `acc`) and its selftest checks that the grouped search and the per-batch search (group size 1) return the same pair and the same counters on 24 starts at n = 22.
Registers: the 8 input words of the group's first batch stay in place for the whole group (every batch writes its results to other registers). After the branch of the 16th batch, the digest words 1..7 of that batch are formed directly in those 8 registers; word 0 was needed earlier for the filter and costs one move.
So one register move is charged per group. Loop control (counter increment, compare, branch) is 3 operations. One loop body = 16 * 595 + 34 + 3 + 1 = 9,558 operations (the previous entry: 9,587 per 16 batches).
Replay: when the test fails, the group is run again from its saved inputs through the batch circuit, as a subroutine, 16 times. Charged per replayed batch: 595, call and return 2, per-batch test of w0 4 (add, and, compare, branch), 8 moves of the digest into the input registers, loop 3 = 612; plus 8 operations at the start, which is 16 * 612 + 8 = 9,800 = 16 * 595 + 280, charged as 16 * 595 + 300. The stage-2 event itself (a replayed batch with a zero lane: shift, AND, compare, branch, the tests of the window F < Tp and of bits 32..121 for the hit lane) is charged 300.
Every replayed group contains at least one stage-2 event, so the number of replays is at most the number of stage-2 events; each event is charged 300 + 16 * 595 + 300 = 10,120 operations.
Window test of a hit lane: F is formed from digest words 1, 2 and the low 26 bits of word 3; F < 400 holds iff word 2 = 0, word 3 AND (2^26 - 1) = 0 and word 1 < 400: 3 extractions and at most 12 further operations, inside the 300.
Upper bounds charged per event: finished trail 700 (extract 8 words, key, write the entry: three read-modify-write field stores, new start: add, 8 word splits and 8 lane insertions; the scan of at most 26,791 table keys is charged separately below), slice check (every 2^48 batches) 100.
The key array holds 4 keys per 256-bit word. Testing a word costs 1 load, 1 XOR with the key repeated 4 times and a zero-lane test (subtract, XOR with all ones, AND, AND with the lane high bits, compare, branch = 6): 8 operations per 4 keys; the ledger charges 3 per key.
Recovery batch (both lanes run in one circuit, 595 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts (lane 1 down to lane 0), 8 XORs, 7 ORs
combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch (659 per batch).
The first l1 - l2 steps move one lane only and need no test (595 + 13), also inside the 659.
Setup 2,000 charged: 1 random word; the 7 starts r + t (7 adds, 8 word splits at 2 operations and 8 lane insertions at 3 operations each: at most 7 * 41 = 287); loop and limit
counters at most 25; the constants of the circuit folded at build time (one operation per folded sum or XOR of constants, at most 3 rounds * 8 calls * 14 = 336); the total is below 800.

### 3.4 Total
All counts are upper bounds enforced by halts (section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 9,558 / 16 | 28,988,314,850,931,136,125,279,250,899,965,499,016,632 (= 2.8988e40) |
| slice checks: ceil(B / 2^48) * 100 | 1.724e25 |
| stage-2 events: e2max * (300 + 16 * 595 + 300) | 1.6008e33 |
| finished trails: 26,791 * (700 + 3 * 26,791) | 2,172,026,743 |
| recovery: (c + 2^48) * 659 + 600, c + 2^48 = 2^116.94 | 1.0512e38 |
| setup | 2,000 |
| total N | 29,093,431,801,591,888,499,697,033,443,257,678,941,569 = 2.909343e40 operations |
N / 638 = 4.5601e37 units = 2^125.100405. Claim `time_log2` = 125.10041 (integer power certificate in Appendix A, rounded up with 4.5e-6 of slack). The main loop is 99.64 percent of it, recovery 0.36 percent.
The three changes against the base, each from the same ledger with only that change: grouped filter 125.10856 to 125.10422 (-0.00435); mixed DP density and 25-byte entries 125.10856 to 125.10476 (-0.00380); both 125.10040 (-0.00816).

### 3.5 A smaller register file
If the machine has only R registers, the batch circuit needs loads and stores. With farthest-next-use allocation of the tracer's straight-line code (`python3 rho.py --spill`) the extra loads plus stores per batch are 3 for R = 24, 16 for R = 20 and 39 for R = 16, and none for R >= 28.
Adding them to every batch (main loop, replay, recovery) and 40 operations per loop body (the 8 saved input words, stored once per group and loaded at a replay, and the accumulator, one load and one store per batch) gives time_log2 = 125.1136 for R = 24, 125.1444 for R = 20 and 125.1973 for R = 16. The claim assumes R >= 34.

## 4. Success probability

Heuristic H1 (premise, section 5): f behaves as a random mapping on N = 2^256 points for the points the search evaluates: for every set of distinct inputs, the outputs are
uniform and independent, and whether a value is a DP is an independent event of probability theta = 400 / 2^122. Then (sub-claims proved here, Lemma 2 is a computation under H1; the numbers below are printed by `python3 rho.py --loss`):

Lemma 1. A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and
the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut once its age is >= c, and ages grow by at most S between checks).
The key determines F (F < 400 < 2^9 and the key holds its 9 low bits), so equal keys of two DPs differ only if their bits above 176 differ. The grouped filter loses no event: a group with no flag has no lane with word 0 zero, hence no DP, in any of its batches, and a flagged group is replayed with the full bookkeeping, so the trails, the table and the counters are those of the per-batch search (checked by the selftest).
A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2. Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 7B = 0.99824 * 2^128. The unfinished trails hold at most 7 ages, each
exponential with mean L (memoryless DP), so their sum exceeds 28 L with probability e^-28 * sum_{j<7} 28^j/j! = 5.8e-7. Cut trails cost at most c = 12 L = 4.70e-4 Q each; the number K of cut trails is Poisson with mean (Q / L) e^-12 = 25,555 e^-12 = 0.157 (P(K=0,1,2) = 0.8547, 0.1342, 0.0105; P(K>=3) = 5.7e-4).
The allowance 1.5e-4 Q already in U covers 0.32 of one cut trail; for K = 1 and K = 2 the remaining loss lowers the success probability by 1.9e-4 and 4.8e-4 (the slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss), and K >= 3 is charged as failure, so the cut-trail deficit is 0.1342 * 1.9e-4 + 0.0105 * 4.8e-4 + 5.7e-4 * 0.3916 = 2.56e-4. Hence U >= 0.99985 Q - 28 L - 1 = 0.99700 * 2^128 when K = 0, except with probability 6e-7. For U distinct inputs the probability of no colliding pair is
prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^-14.65 = 3.9e-5. The expected number of key false matches (two different DP ends with the same 64-bit key: the key space is 2^55 * 400 = 2^63.6) is below 26,791^2 / 2 / 2^63.6 = 2.5e-11.
Programmed aborts. Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations, binomial with mean Q / L = 25,555 (and no more than a Poisson count of the same mean in the Chernoff bound); the abort needs 26,792 or more, probability at most exp(-mean) (e mean / 26,792)^26,792 = 2^-42.5 = 1.6e-13 (Chernoff bound). Stage-2 budget: the number of stage-2 events is at most binomial with
mean mu2 = 7B/2^32 = 7.9e28 and the abort needs 2 mu2 + 65, probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.1e28). A recovery that finds no pair needs a key false match or a start lying on another trail (at most 2.5e-11 + 2^-100).
The losses add to 6e-7 + 3.9e-5 + 2.56e-4 + 2.5e-11 + 1.6e-13 + 7.9e-31 < 2.96e-4, so P(success) >= 1 - e^-0.497 - 2.96e-4 = 0.3913 >= 0.39. The 0.0013 left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0044, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 has three parts: (a) for the inputs the search evaluates, the 256-bit outputs behave as uniform and independent values, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t
have the first-collision law of a random mapping; (c) the DP indicator is independent of the collision events. Parts (a) and (b) are premises on the fixed function f, K = 0, and cannot be tested at width 256. They are declared and not proved.
The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Section 4 and in the note.
What was run (frozen protocol written before the runs (sources and outputs kept with the base entry), no run repeated), on the base entry's program:
T1 (family law, 3 rounds, fresh random 256-bit K per run, chain truncated to n bits): n = 32, 2000 runs: mean first-repeat time / sqrt(pi N/2) = 1.0075 (z 0.64), E[T^2]/2N = 1.020 (z 0.88), KS 0.78; n = 40, 300 runs: ratio 0.9712 (z -0.95), E[T^2]/2N = 0.977 (z -0.41), KS 1.36 (0.1 percent critical value 1.949). Pass.
T2 (the fixed K = 0 function at full width 256, 2^26 points per statistic, observed equal pairs of a projection against C(2^26,2)/2^bits; sources: iterates of f from a random start, inputs r + i, uniform inputs; 14 projections each): 42 statistics (3 sources x 14 projections): observed/expected between 0.9546 and 1.0342, z between -2.29 and 1.55 (largest |z| 2.29 against the bound 4.5), mean z -0.46. Pass.
T3 (the base entry's search, plan(n), one attempt per fresh r, on the target chain K = 0 and on an ideal function of the same width): n = 32 (d = 8, Q = 72,527 evaluations, pure-birthday value 0.458), 4000 attempts each: target 1772 successes (0.443), ideal 1814 (0.4535), two-proportion z = -0.94; n = 40 (d = 12, Q = 1,160,292, 0.458), 480 attempts each: target 211 (0.440), ideal 226 (0.471), z = -0.97; every returned pair re-checked (0 bad pairs); 3 to 6 attempts per 1000 halted in both conditions. Pass.
T1 to T3 above are participant-run on the base entry's program (integer DP, per-batch filter, 32-byte entries). T3 is repeated on this entry's own program by the organizer experiments `rho-n32-a` to `rho-n32-c` and `rho-n40-a` to `rho-n40-d` (section 6); T1 and T2 are not repeated. This entry's program differs from the base in the filter (grouped, with replay, shown equal to the per-batch search by the selftest), in the DP predicate (a threshold on a 90-bit window instead of zeros) and in the entry packing; the organizer experiments use the mixed predicate at both widths (the settings "32m" and "40m" of the program: low s1 = 8 resp. 12 bits zero and the 4 bits above them below 12, groups of 16 batches as in the claim, 25-byte entries); the zeros-only n = 32 and n = 40 settings of the base T3 stay in the program unchanged.
Run on this entry's program: the 256 trials of the organizer experiment (section 6), and a check at n = 22 of 1,500 fresh attempts with the shipped search (a script outside the package): success 0.511 (the base program at its own n = 22 setting: 0.463), 62 halts. These show the construction works; they are not evidence about the premise at width 256.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; T1 and T2 on this entry's program; T3 beyond the 72 attempts at width 32 and 8 at width 40 that fit the organizer's time limit (section 6 states their power). Fixed-K first-repeat times from random starts are not independent samples (one functional graph); they were seen
to deviate from the law by 0.70 to 1.65 for n = 16..36 in unrecorded smoke runs and are not evidence either way. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of section 4.

## 6. Experiments `rho-n22`, `rho-n32-a` to `rho-n40-d`

The organizer runs the same program at n = 22 (section 5 of the program): DP = low 4 bits zero and the next 4 bits below 12 (density 12/256), groups of 2 batches, 7 lanes, budgets from `plan(22)`, up to 60 fresh attempts per trial (success amplification is used only by the experiment),
and returns the two messages 0^32 || x, 0^32 || y. The organizer recomputes the 3-round digests and checks that they agree in the low 22 bits and the messages are distinct. This checks the circuit, the grouped filter and its replay, the mixed DP predicate, the 25-byte entry packing, the trail
bookkeeping, the table, the recovery and the message construction on the real target; it does not measure the cost or the success probability at width 256, and the observation counters are the program's own.

Experiments `rho-n32-a` to `rho-n32-c` (width 32) and `rho-n40-a` to `rho-n40-d` (width 40): the premise test T3 on this entry's own program, run by the organizer. In each experiment the first 24 trials (width 32) or the first 2 trials (width 40) run one attempt of the shipped search (`run_attempt` of the program) from the organizer's trial seed, with the budgets of `plan(n, "32m")` or `plan(n, "40m")`: the mixed distinguished-point predicate (low 8 resp. 12 bits zero and the 4 bits above them below 12), groups of 16 batches with replay, 7 lanes, 25-byte entries, the table limit and the halts of Section 2, Q = 74,928 resp. 1,198,624 evaluations. A trial whose attempt halts or ends without a pair returns two nulls, and so do the remaining trials, which do not run: the runner gives 20 seconds to an experiment of 256 trials, and one attempt takes 0.3 s (width 32) or 3 s (width 40), measured 6 to 9 seconds per experiment on one quiet core.
The organizer recomputes the digests of each returned pair and checks that the two messages differ and the digests agree on the low 32 (resp. 40) bits; the number of pairs is the trusted result. For a random mapping the success probability of one attempt lies between the design value 0.39 (1 - exp(-0.497)) and 0.48 (every one of the Q evaluations counted as a distinct input), so 28 to 35 pairs are expected over the 72 attempts at width 32 (9.4 to 11.5 per experiment) and 3.1 to 3.8 over the 8 attempts at width 40. `python3 rho.py --h1` runs the same code path on its own seeds and prints the pairs found with the register count and the memory layout of section 7: n = 32: 60 attempts, 27 successes (0.450), 0 halts; n = 40: 6 attempts, 1 successes (0.167), 0 halts.
Power: the standard deviation of the pair rate over 72 attempts is 0.058, so a deficit of the collision rate is visible at two standard deviations only when it exceeds about 27 percent; 8 attempts at width 40 show only a gross failure (no pair at all has probability about 0.02 at a rate of 0.4). Section 4 prices a deficit eps at 0.5 * log2(1/(1-eps)) bits. These runs test that the program's own search, with its grouped filter and replay, mixed predicate, 25-byte entries, table and halts, finds collisions on the real target at the rate of a random mapping at widths 32 and 40; they do not test fresh keys (T1), the 2^26-point projections (T2), width 256 or trails above 2^40, and the organizer's frequency is not an independent-trial probability estimate.

## 7. Memory

Table: 26,791 entries * 25 bytes = 669,775 bytes. An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 10,408 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 374,688 bytes (main body 9,558, batch subroutine with the recovery 640, handlers 170, replay control 40).
Counters and ages: 2,048 bytes. The 64 registers, counted as memory: 2,048 bytes. Total 1,048,559 bytes <= 2^20 = 1,048,576. Claim `memory_log2_bytes` = 20. `python3 rho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 374,688 - 4,096) / 25) = 26,791, and Tp = 400 is the largest integer for which the table-capacity bound of section 4 stays below 2^-40 (Appendix A computes both).

Registers used: the main loop keeps R = 34 words resident: 25 live values in one batch (the peak of the traced circuit), the group's 8 saved input words and the filter accumulator (`python3 rho.py --selftest` prints 25 and 34), with no load or store in the main loop. The file of 64 registers counted as memory above leaves 30 registers for the loop counters and the temporaries of events, which are charged with their loads and stores. Fewer than 34 registers are priced in 3.5.
Table layout (the memory total counted in whole 256-bit words; `python3 rho.py --h1` prints the numbers): one block of 20,931 words = 669,792 bytes holds the 669,775 bytes of the table and leaves 17 bytes unused. It is byte-contiguous from a word boundary: the keys, 8 bytes each, from byte 0 (6,698 words, 4 keys per word); the trail numbers, 2 bytes each, from byte 214,328 (an even offset, so a number never straddles a word); the lengths, 15 bytes each, from byte 267,910 (a length that straddles a word takes 2 loads or 2 stores and at most 12 further operations). The last key word holds 3 keys and the first 8 bytes of the numbers, so the scan of that word takes one extra AND to ignore the other lanes. Total: code 374,688 + counters 2,048 + registers 2,048 + table block 669,792 = 1,048,576 bytes = 2^20 exactly, so the margin under `memory_log2_bytes` = 20 is 0 bytes counted in whole words and 17 bytes unpadded; nothing exceeds 2^20.
Operations added by the layout: at most 13 per finished trail (12 for the straddling length, 1 for the extra AND) and at most 24 once at the recovery, 348,307 in all, 1.2e-35 of N; the claim's `time_log2` is rounded up by 4.5e-6 bit, which is about 9e34 operations, so the ledger is unchanged.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bound only selects Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 rho.py --ledger`.

```python
from fractions import Fraction
from math import isqrt, log, log2

PH, LANES, U = 595, 7, 16                     # operations per batch (tracer), lanes, batches per loop body
N_BITS, S1, W = 256, 32, 90                   # width, filter bits, window bits; D = S1 + W = 122
KAPPA, INFLIGHT = 12, 28
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
EVENT, STAGE2, REPLAY, EXTRA = 700, 300, 300, 64
ENTRY, INSTR, CODE_OTHER, FIXED = 25, 36, 640 + 170 + 40, 2048 + 2048
C = 638                                       # operations of the 3-round reference compression

body = U * PH + (U + (U - 1) + 1 + 2) + 3 + 1                 # batches + grouped filter + loop control + one move = 9,558
code_bytes = (body + CODE_OTHER) * INSTR
tmax = ((1 << 20) - code_bytes - FIXED) // ENTRY               # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def plan(Tp):
    L = Fraction(1 << D, Tp)                                   # trail length scale 1/theta, theta = Tp / 2^D
    ureq = isqrt(2 * Nn * LAM.numerator // LAM.denominator) + 2
    num, den = ureq + INFLIGHT * L + 1, CUT.denominator
    q = -(-(num * den) // (den - CUT.numerator))
    b = -(-q // LANES)
    b = -(-b // U) * U
    c = -(-KAPPA * L.numerator // L.denominator)
    return L, b, c


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


Tp = max(t for t in range(1, 2049)
         if float(plan(t)[1] * LANES / plan(t)[0]) < tmax + 1
         and tail_log2(float(plan(t)[1] * LANES / plan(t)[0]), tmax + 1) <= -40)
L, B, c = plan(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
rows = [("main loop: B * 9558 / 16", Fraction(body, U) * B),
        ("slice checks: ceil(B / 2^48) * 100", -(-B // SB) * 100),
        ("stage-2 events: e2max * (300 + 16 * 595 + 300)", e2max * (STAGE2 + U * PH + REPLAY)),
        ("finished trails: tmax * (700 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("recovery: (c + 2^48) * (595 + 64) + 600", (c + SB) * (PH + EXTRA) + 600),
        ("setup", 2000)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + FIXED)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P = 100000
a = (N ** P // C ** P).bit_length() - 1                        # 2^a * C^P <= N^P < 2^(a+1) * C^P
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
```

Output:

```
Tp = 400  tmax = 26791  B = 48526160035038520402225153211911276864  e2max = 158177279050121848851244930467  c = 159507359494189904748456847233641350
memory bytes = 1048559
main loop: B * 9558 / 16                             28988314850931136125279250899965499016632
slice checks: ceil(B / 2^48) * 100                   17239955253614354689597600
stage-2 events: e2max * (300 + 16 * 595 + 300)       1600754063987233110374598696326040
finished trails: tmax * (700 + 3 * tmax)             2172026743
recovery: (c + 2^48) * (595 + 64) + 600              105115349906671147229418554336621972554
setup                                                2000
N = 29093431801591888499697033443257678941569
certificate: 2^12510040 * 638^100000 <= N^100000 < 2^12510041 * 638^100000
log2(N/C) = 125.1004046656
time_log2 = 125.10041
```
