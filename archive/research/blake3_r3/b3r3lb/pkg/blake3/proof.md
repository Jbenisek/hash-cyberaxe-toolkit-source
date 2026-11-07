# blake3-r3: plain birthday with seven packed lanes, a grouped filter and mixed distinguished points

Credited derivative of our own entry cf8b0e92-4302-4813-907a-3c970c102646 (blake3 round 3, 125.10041, itself a derivative of e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca). That chain
supplies the construction: the seven-lane 36-bit packed circuit, the grouped filter, the mixed distinguished points, 25-byte table entries, the recovery walk, the ledger and the premise tests T1 to T3. This entry keeps all of it and changes one thing:
the message has a fixed 64-byte first block P, so the block that the search varies is the last block of a two-block chunk and its chaining value CV = chain_value(P) is a constant that is not the IV.
P was chosen so that one 32-bit sum of two constants of the circuit is zero (Section 8), which removes 2 operations from the 595-operation batch (593). The program derives the table size and the
distinguished-point threshold from the code size, so Tp moves from 400 to 401 and the table from 26,791 to 26,837 entries; the ledger with all of this gives 125.09556 (the base ledger with a 595-operation batch gives 125.10041).
No differential, no structure of the 3-round compression is used in the search. The claim is the price of the birthday attack on the complete 3-round hash of messages that start with P, when the compression is
evaluated seven instances at a time in 256-bit words and every operation is counted.

## 1. Target and relation

Target `blake3-r3-prefix-v1`. Its message domain is quoted from the organizer profile (field `message_domain`): "Finite byte strings of bit length below 2^64." Every 128-byte string is therefore a message of the domain (Heuristic H4 of the claim declares this use of the domain). For a 256-bit integer x let M(x) be the 128-byte message `P || 0^32 || x` (x little endian), where P is the fixed 64-byte string
of Section 8 (`PREFIX` of the program, 16 little-endian words). M(x) is one chunk of two blocks. Block 1 is P: chaining value IV, counter 0, block length 64, flags 1 = CHUNK_START, rounds 0..2, feed-forward v[i] XOR v[i+8] for i < 8, giving the chaining value CV (a non-root block outputs these 8 words).
Block 2 is the last block: chaining value CV, words m0..m7 = 0, m8..m15 = the eight little-endian words of x, counter 0, block length 64, flags 10 = CHUNK_END|ROOT, rounds 0..2, feed-forward v[i] XOR v[i+8], digest = the 8 words, little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit
little-endian integer. The attack outputs x != y with f(x) = f(y); then M(x) != M(y) are two distinct messages in the domain with equal
256-bit digests. The scalar digest of the program (`chain_value` and `digest_words`, section 1 of the program) was compared with the organizer reference `verifier/blake3.py:blake3` on 300 messages M(x) of this form (rounds 3, 0 differences); the same digest code without the prefix was compared on 2,002 64-byte
messages (rounds 1..7, 286 each, 0 differences) and with the 7-, 2- and 1-round digests of the 64-byte block in the organizer test vectors (`tests/fixtures/blake3-vectors.json`, 3 of 3); the program's own selftest compares the packed circuit with its scalar digest.

## 2. The attack (program `experiments/rho.py`, sections 3 and 4)

Parameters for n = 256: N = 2^256, seven lanes, groups of U = 16 batches. The function is f of Section 1 (last block with chaining value CV). A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is
below Tp = 401. The density is theta = 401 / 2^122 = 2^-113.3525 and L = 1 / theta = 2^113.3525 (the base entry used 400 / 2^122; Tp is the largest value whose table-capacity bound stays below 2^-40, and the smaller code of this entry leaves room for 401). The key of a DP is the 55 bits of x above bit 121 followed by the 9 low bits of F (F < 401 < 2^9, so those 9 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. Seven trails run in the seven lanes of the circuit of section 3. A batch is one evaluation of all seven lanes. Batch counter b = 0, 1, ...
2. A group is 16 consecutive batches. During a group only the grouped filter of section 3.3 runs: for each batch one addition on digest word 0 of the seven lanes, and one AND into an accumulator. The 8 input words of the group's first batch are not overwritten during the group.
3. If the accumulator shows that in all 16 batches all seven lanes had word 0 nonzero, the group is done and its last digests are the next inputs. Otherwise the group is replayed from its saved inputs, one batch at a time, each with the per-batch test of word 0 (4 operations, section 3.3):
   in a replayed batch with a lane whose word 0 is zero (a stage-2 event) each such lane is tested for the DP property. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, section 7) and start trail t' = next index in that lane.
4. At every multiple of S = 2^48 batches (always a group boundary): a lane whose trail has age >= c = 12 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-2 events, when the table holds 26,837 keys, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps, then step both together; at the first step
   with f(a) = f(b) and a != b output (a, b). Both lanes of one circuit are used. At most capr = c + S batches are run.
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 rho.py --ledger`): Tp = 401, L = 5316911983139663491615228241121378304 / 401, B = 48,526,027,423,825,563,155,309,147,850,303,017,632 (a multiple of 16; Q = 7B = 0.99824 * 2^128 evaluations),
e2max = 158,176,846,786,764,889,064,786,972,054, c = 159,109,585,530,363,994,761,552,964,821,587,381 (= 2^116.94), table capacity tmax = 26,837 entries of 25 bytes. The trail numbers t stay below 2^15 (finished trails <= 26,837, cut trails <= Q / c + 7 = 2,141, plus the 7 starts) and every length is below c + S < 2^117, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision, no advice (K = 0).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry (the benchmark profile fixes 256-bit words and charges loads and stores, and does not fix a register count): a load/store machine with 256-bit words, 256-bit immediates and R registers. Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each (one move per loop body is needed and charged, section 3.3). The main loop keeps its working set in registers, so it has no loads or stores. The tracer reports the high-water mark of live words (`python3 rho.py --selftest`): 25 values in one batch, and 34 with the group's 8 saved input words and the filter accumulator, so R >= 34 is sufficient for the main loop. Table lookups, the recovery and the events are charged with their loads and stores (section 3.4). Constants are immediates. The memory total of section 7 counts a file of 64 registers (2,048 bytes) as memory as well.
The organizer's reference count C(r3) = 638 (`scripts/reference_operation_costs.py` extended to 3 rounds; 222, 430 and 638 for 1, 2 and 3 rounds) is used only as the unit: Unit = 638 operations. It is not claimed to define the register file. A smaller register file is priced in section 3.5.

### 3.2 One batch = 593 operations
Lane layout: 36-bit lanes (32 data bits, 4 guard bits), 7 lanes per word. A lane value stays below 2^36 (the tracer keeps the bound of every value
and inserts an AND with 0xFFFFFFFF per lane before any sum that could reach 2^36). Sums of packed words are exact because no lane carries out of 36 bits.
XOR is bitwise. Rotation of a lane by r (valid for lane values below 2^36, guard bits arbitrary): ((t >> r) AND A_r) OR ((t << (32-r)) AND B_r), A_r keeping bits
0..31-r and B_r keeping bits 32-r..31 of every lane. Check: the right shift brings bits r..35 of a lane down to 0..35-r and bits 0..r-1 of the next lane to
36-r..35, outside A_r; the left shift puts bit j of a lane at j+32-r, bits j < r land in 32-r..31 (kept) and bits j >= r land at 32 or above, in a position that is
either above bit 31 of the same lane or at 28-r..31-r of the next lane, below 32-r (not kept). So 5 operations (shr, and, shl, and, or) and no mask before the XOR is needed.
Constants (same in every lane) are folded at build time and cost nothing: the four column calls of round 0 depend only on m0..m7 = 0, CV and the IV, so only the four diagonal calls of round 0 and
all calls of rounds 1 and 2 contain variable words. Sums of constants are folded; a XOR with the constant 0 is dropped; an addition whose constants sum to 0 is dropped.
Hand count: a call whose state words are constants and whose two message words are variable costs 5 adds, 4 XORs and 4 rotations of 5 = 29. Round 0, diagonal call 5 adds v1 + v6 + m10 where v1 and v6 are the constants A1 and B2 of Section 8 with A1 + B2 = 0 mod 2^32:
the sum of the constants is zero, so the call starts from m10 alone and costs 28 (the other three cost 29): round 0 = 29 + 28 + 29 + 29 = 115.
A call with variable state costs 6 adds, 4 XORs, 20 = 30, and a zero message word (words m0..m7) saves its add: round 1 = 8 x 30 - 8 = 232, round 2 = 232 plus 2 masks (the tracer inserts an AND before a sum that
could reach 2^36; with a generic chaining value it inserts 3) = 234; the 8 digest XORs and 4 masks (words that are not clean) = 12. The tracer (`build_hash`, printed by `python3 rho.py --selftest`) emits exactly these: 115 + 232 + 234 + 12 =
593 = 99 add + 88 xor + 80 shr + 80 shl + 80 or + 166 and. The packed circuit agrees with the scalar digest (selftest, 70 inputs, and in every run of the experiment and of T3 below).
Cost per instance: 593/7 = 84.7 operations = 0.1328 unit, against 1 unit for a compression. The tracer is shipped in the program; the organizer experiment does not meter cost.

### 3.3 Grouped filter, loop, replay and the other events
Grouped filter (replaces the per-batch filter of 4 operations): after each batch, u = w0 + 0xFFFFFFFF in every lane (1 add; w0 is digest word 0 of the seven lanes, clean, so each lane of u is below 2^33 and bit 32 of a lane is set iff that lane's w0 is nonzero);
the first batch's u starts the accumulator, each later batch does acc = acc AND u (1 operation, 15 in all). After the 16th batch: t = acc AND (bit 32 of every lane) (1), compare t with that pattern (1), branch (1). Bit 32 of a lane of acc is set iff the lane's w0 was nonzero in all 16 batches.
Count: 16 + 15 + 3 = 34 operations per group, against 64 for 16 per-batch filters. The program executes exactly this (`search`, accumulator `acc`) and its selftest checks that the grouped search and the per-batch search (group size 1) return the same pair and the same counters on 24 starts at n = 22.
Registers: the 8 input words of the group's first batch stay in place for the whole group (every batch writes its results to other registers). After the branch of the 16th batch, the digest words 1..7 of that batch are formed directly in those 8 registers; word 0 was needed earlier for the filter and costs one move.
So one register move is charged per group. Loop control (counter increment, compare, branch) is 3 operations. One loop body = 16 * 593 + 34 + 3 + 1 = 9,526 operations (the base entry: 9,558 with 595 per batch).
Replay: when the test fails, the group is run again from its saved inputs through the batch circuit, as a subroutine, 16 times. Charged per replayed batch: 593, call and return 2, per-batch test of w0 4 (add, and, compare, branch), 8 moves of the digest into the input registers, loop 3 = 610; plus 8 operations at the start, which is 16 * 610 + 8 = 9,768 = 16 * 593 + 280, charged as 16 * 593 + 300. The stage-2 event itself (a replayed batch with a zero lane: shift, AND, compare, branch, the tests of the window F < Tp and of bits 32..121 for the hit lane) is charged 300.
Every replayed group contains at least one stage-2 event, so the number of replays is at most the number of stage-2 events; each event is charged 300 + 16 * 593 + 300 = 10,088 operations.
Window test of a hit lane: F is formed from digest words 1, 2 and the low 26 bits of word 3; F < 401 holds iff word 2 = 0, word 3 AND (2^26 - 1) = 0 and word 1 < 401: 3 extractions and at most 12 further operations, inside the 300.
Upper bounds charged per event: finished trail 700 (extract 8 words, key, write the entry: three read-modify-write field stores, new start: add, 8 word splits and 8 lane insertions; the scan of at most 26,837 table keys is charged separately below), slice check (every 2^48 batches) 100.
The key array holds 4 keys per 256-bit word. Testing a word costs 1 load, 1 XOR with the key repeated 4 times and a zero-lane test (subtract, XOR with all ones, AND, AND with the lane high bits, compare, branch = 6): 8 operations per 4 keys; the ledger charges 3 per key.
Recovery batch (both lanes run in one circuit, 593 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts (lane 1 down to lane 0), 8 XORs, 7 ORs
combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch (657 per batch).
The first l1 - l2 steps move one lane only and need no test (593 + 13), also inside the 657.
Setup 2,000 charged: 1 random word; the 7 starts r + t (7 adds, 8 word splits at 2 operations and 8 lane insertions at 3 operations each: at most 7 * 41 = 287); loop and limit
counters at most 25; the constants of the circuit folded at build time (one operation per folded sum or XOR of constants, at most 3 rounds * 8 calls * 14 = 336); the total is below 800.

### 3.4 Total
All counts are upper bounds enforced by halts (section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 9,526 / 16 | 28,891,183,577,460,144,663,592,183,901,374,159,122,652 (= 2.8891e40) |
| slice checks: ceil(B / 2^48) * 100 | 1.724e25 |
| stage-2 events: e2max * (300 + 16 * 593 + 300) | 1.5957e33 |
| finished trails: 26,837 * (700 + 3 * 26,837) | 2,179,459,607 |
| recovery: (c + 2^48) * 657 + 600, c + 2^48 = 2^116.94 | 1.0453e38 |
| setup | 2,000 |
| total N | 28,995,720,170,841,641,432,943,050,661,225,930,338,820 = 2.899572e40 operations |
N / 638 = 4.5448e37 units = 2^125.095551. Claim `time_log2` = 125.09556 (integer power certificate in Appendix A, rounded up with 4.5e-6 of slack). The main loop is 99.64 percent of it, recovery 0.36 percent.
Against the base entry (the same program with the 595-operation batch, CV = IV and flags 11: ledger 125.10041): the 593-operation batch with the re-selected Tp = 401 and a table of 26,837 entries gives 125.09556, a change of -0.00485 bit. The two-block message adds no operation to the loop: the chaining value is a constant of the circuit.

### 3.5 A smaller register file
If the machine has only R registers, the batch circuit needs loads and stores. With farthest-next-use allocation of the tracer's straight-line code (`python3 rho.py --spill`) the extra loads plus stores per batch are 3 for R = 24, 16 for R = 20 and 39 for R = 16, and none for R >= 28.
Adding them to every batch (main loop, replay, recovery) and 40 operations per loop body (the 8 saved input words, stored once per group and loaded at a replay, and the accumulator, one load and one store per batch) gives time_log2 = 125.1088 for R = 24, 125.1397 for R = 20 and 125.1927 for R = 16. The claim assumes R >= 34.

## 4. Success probability

Heuristic H1 (premise, section 5): f (Section 1, last block with chaining value CV) behaves as a random mapping on N = 2^256 points for the points the search evaluates: for every set of distinct inputs, the outputs are
uniform and independent, and whether a value is a DP is an independent event of probability theta = 401 / 2^122. Then (sub-claims proved here, Lemma 2 is a computation under H1; the numbers below are printed by `python3 rho.py --loss`):

Lemma 1. A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and
the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut once its age is >= c, and ages grow by at most S between checks).
The key determines F (F < 401 < 2^9 and the key holds its 9 low bits), so equal keys of two DPs differ only if their bits above 176 differ. The grouped filter loses no event: a group with no flag has no lane with word 0 zero, hence no DP, in any of its batches, and a flagged group is replayed with the full bookkeeping, so the trails, the table and the counters are those of the per-batch search (checked by the selftest).
A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2. Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 7B = 0.99824 * 2^128. The unfinished trails hold at most 7 ages, each
exponential with mean L (memoryless DP), so their sum exceeds 28 L with probability e^-28 * sum_{j<7} 28^j/j! = 5.8e-7. Cut trails cost at most c = 12 L = 4.70e-4 Q each; the number K of cut trails is Poisson with mean (Q / L) e^-12 = 25,619 e^-12 = 0.1574 (P(K=0,1,2) = 0.8544, 0.1345, 0.0106; P(K>=3) = 5.8e-4).
The allowance 1.5e-4 Q already in U covers 0.32 of one cut trail; for K = 1 and K = 2 the remaining loss lowers the success probability by 1.9e-4 and 4.8e-4 (the slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss), and K >= 3 is charged as failure, so the cut-trail deficit is 0.1345 * 1.9e-4 + 0.0106 * 4.8e-4 + 5.8e-4 * 0.3916 = 2.57e-4. Hence U >= 0.99985 Q - 28 L - 1 = 0.99700 * 2^128 when K = 0, except with probability 6e-7. For U distinct inputs the probability of no colliding pair is
prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^-14.65 = 3.9e-5. The expected number of key false matches (two different DP ends with the same 64-bit key: the key space is 2^55 * 401 = 2^63.65) is below 26,837^2 / 2 / 2^63.65 = 2.5e-11.
Programmed aborts. Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations, binomial with mean Q / L = 25,619 (and no more than a Poisson count of the same mean in the Chernoff bound); the abort needs 26,838 or more, probability at most exp(-mean) (e mean / 26,838)^26,838 = 2^-41.2 = 3.9e-13 (Chernoff bound). Stage-2 budget: the number of stage-2 events is at most binomial with
mean mu2 = 7B/2^32 = 7.9e28 and the abort needs 2 mu2 + 65, probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.1e28). A recovery that finds no pair needs a key false match or a start lying on another trail (at most 2.5e-11 + 2^-100).
The losses add to 6e-7 + 3.9e-5 + 2.57e-4 + 2.5e-11 + 3.9e-13 + 7.9e-31 < 2.97e-4, so P(success) >= 1 - e^-0.497 - 2.97e-4 = 0.3913 >= 0.39. The 0.0013 left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0044, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 has three parts: (a) for the inputs the search evaluates, the 256-bit outputs behave as uniform and independent values, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t
have the first-collision law of a random mapping; (c) the DP indicator is independent of the collision events. Parts (a) and (b) are premises on the fixed function f, K = 0, and cannot be tested at width 256. They are declared and not proved.
The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Section 4 and in the note.
What was run (frozen protocol written before the runs (sources and outputs kept with the base entry), no run repeated), on the base entry's program:
T1 (family law, 3 rounds, fresh random 256-bit K per run, chain truncated to n bits): n = 32, 2000 runs: mean first-repeat time / sqrt(pi N/2) = 1.0075 (z 0.64), E[T^2]/2N = 1.020 (z 0.88), KS 0.78; n = 40, 300 runs: ratio 0.9712 (z -0.95), E[T^2]/2N = 0.977 (z -0.41), KS 1.36 (0.1 percent critical value 1.949). Pass.
T2 (the fixed K = 0 function at full width 256, 2^26 points per statistic, observed equal pairs of a projection against C(2^26,2)/2^bits; sources: iterates of f from a random start, inputs r + i, uniform inputs; 14 projections each): 42 statistics (3 sources x 14 projections): observed/expected between 0.9546 and 1.0342, z between -2.29 and 1.55 (largest |z| 2.29 against the bound 4.5), mean z -0.46. Pass.
T3 (the base entry's search, plan(n), one attempt per fresh r, on the target chain K = 0 and on an ideal function of the same width): n = 32 (d = 8, Q = 72,527 evaluations, pure-birthday value 0.458), 4000 attempts each: target 1772 successes (0.443), ideal 1814 (0.4535), two-proportion z = -0.94; n = 40 (d = 12, Q = 1,160,292, 0.458), 480 attempts each: target 211 (0.440), ideal 226 (0.471), z = -0.97; every returned pair re-checked (0 bad pairs); 3 to 6 attempts per 1000 halted in both conditions. Pass.
T1 to T3 are participant-run on the older program (integer DP, per-batch filter, 32-byte entries); they were not repeated for this entry. This entry's program differs from the base in the filter (grouped, with replay, shown equal to the per-batch search by the selftest), in the DP predicate (a threshold on a 90-bit window instead of zeros) and in the entry packing; the n = 32 and n = 40 settings of the program are unchanged integer-DP settings.
T1 to T3 and the other participant runs concern the function with chaining value IV (messages 0^32 || x). The function of this entry differs from it only in the 8 constant words of the chaining value and in v15 (10 instead of 11); H1 is declared for it as well and no participant run of T1 to T3 was made on it. The 256 trials of the organizer experiment (section 6) check the construction on this function; they are not evidence about the premise at width 256.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; T3 for the mixed predicate at widths above 22. Fixed-K first-repeat times from random starts are not independent samples (one functional graph); they were seen
to deviate from the law by 0.70 to 1.65 for n = 16..36 in unrecorded smoke runs and are not evidence either way. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of section 4.

## 6. Experiment `rho-n22`

The organizer runs the same program at n = 22 (section 5 of the program): DP = low 4 bits zero and the next 4 bits below 12 (density 12/256), groups of 2 batches, 7 lanes, budgets from `plan(22)`, up to 60 fresh attempts per trial (success amplification is used only by the experiment),
and returns the two 128-byte messages P || 0^32 || x and P || 0^32 || y (P as in Section 8). The organizer recomputes the 3-round digests and checks that they agree in the low 22 bits and the messages are distinct. This checks the circuit, the grouped filter and its replay, the mixed DP predicate, the 25-byte entry packing, the trail
bookkeeping, the table, the recovery and the two-block message construction on the real target; it does not measure the cost or the success probability at width 256, and the observation counters are the program's own.

## 7. Memory

Table: 26,837 entries * 25 bytes = 670,925 bytes. An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 10,376 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 373,536 bytes (main body 9,526, batch subroutine with the recovery 640, handlers 170, replay control 40).
Counters and ages: 2,048 bytes. The 64 registers, counted as memory: 2,048 bytes. Total 1,048,557 bytes <= 2^20 = 1,048,576. Claim `memory_log2_bytes` = 20. `python3 rho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 373,536 - 4,096) / 25) = 26,837, and Tp = 401 is the largest integer for which the table-capacity bound of section 4 stays below 2^-40 (Appendix A computes both).

## 8. The prefix P and the message mode

Message mode (premise, declared as Heuristic H4): the attack uses messages of two blocks, P || 0^32 || x, instead of one block. The profile's message domain is any byte string shorter than 2^64 bits; the standard chunk rules apply to 128 bytes (one chunk, blocks of 64 bytes, flags 1 on the first block and 10 on the last), and Section 1 states the compression calls used. No other mode feature is used: no tree, no key, no counter other than 0.

P (the program's `PREFIX`) is the 64-byte string of 16 little-endian words w0 = i mod 2^32, w1 = floor(i / 2^32), w2..w15 = 0 with i = 10,768,619,076 (so w0 = 2,178,684,484 mod 2^32 and w1 = 2; the program computes them from `PREFIX_I`). Its chaining value is CV = chain_value(P) = (3205528875, 411291139, 60262883, 489927237, 809493467, 642014741, 3157960105, 1883752943) (printed by `python3 rho.py --selftest`).
The condition: in the last block, the column calls 1 and 2 of round 0 start from (CV[j], CV[j+4], IV[j], D[j]) with D = (0, 0, 64, 10) and message words 0; A1 is the value of v1 after call 1 and B2 the value of v6 after call 2. The first addition of diagonal call 5 of round 0 is v1 + v6 + m10 = (A1 + B2) + m10. The program function `prefix_condition()` computes (A1 + B2) mod 2^32; it is 0 for P, and `python3 rho.py --selftest` prints it.

Selection procedure (a bounded search done once, before the attack): scan i = 0, 1, 2, ... in order, form P(i) as above, compute CV(i) = chain_value(P(i)) and test (A1 + B2) mod 2^32 = 0; stop at the first success. A random CV passes with probability 2^-32 (heuristic: A1 + B2 is uniform); the first success was i = 10,768,619,076, after 10,768,619,077 first-block compressions (2^33.33), done with a C program of the same arithmetic (not shipped; its first-block output for i = 5 equals `chain_value` of the shipped program, checked) in two ranges, [0, 6 * 10^9) with no success and then from 6 * 10^9 up to the success; no earlier i passes. Anyone can verify the single claim (that P(i) passes) with the shipped program; that no smaller i passes is the result of the scan and costs the same scan to repeat. The claim's `preprocessing_log2` is 33.4; it is the cost of this scan in compressions and is not part of the attack's operation count.
The choice of P does not enter the attack (it fixes the constants of the circuit); it uses the one condition above only to remove two operations. Each further condition of the same kind would remove more operations and multiply the scan by 2^32; none was searched.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bound only selects Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 rho.py --ledger`.

```python
from fractions import Fraction
from math import isqrt, log, log2

PH, LANES, U = 593, 7, 16                     # operations per batch (tracer), lanes, batches per loop body
N_BITS, S1, W = 256, 32, 90                   # width, filter bits, window bits; D = S1 + W = 122
KAPPA, INFLIGHT = 12, 28
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
EVENT, STAGE2, REPLAY, EXTRA = 700, 300, 300, 64
ENTRY, INSTR, CODE_OTHER, FIXED = 25, 36, 640 + 170 + 40, 2048 + 2048
C = 638                                       # operations of the 3-round reference compression

body = U * PH + (U + (U - 1) + 1 + 2) + 3 + 1                 # batches + grouped filter + loop control + one move = 9,526
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
rows = [("main loop: B * 9526 / 16", Fraction(body, U) * B),
        ("slice checks: ceil(B / 2^48) * 100", -(-B // SB) * 100),
        ("stage-2 events: e2max * (300 + 16 * 593 + 300)", e2max * (STAGE2 + U * PH + REPLAY)),
        ("finished trails: tmax * (700 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("recovery: (c + 2^48) * (593 + 64) + 600", (c + SB) * (PH + EXTRA) + 600),
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
Tp = 401  tmax = 26837  B = 48526027423825563155309147850303017632  e2max = 158176846786764889064786972054  c = 159109585530363994761552964821587381
memory bytes = 1048557
main loop: B * 9526 / 16                             28891183577460144663592183901374159122652
slice checks: ceil(B / 2^48) * 100                   17239908140647331135862900
stage-2 events: e2max * (300 + 16 * 593 + 300)       1595688030384884200885570974080752
finished trails: tmax * (700 + 3 * tmax)             2179459607
recovery: (c + 2^48) * (593 + 64) + 600              104534997693449144558525226947481810909
setup                                                2000
N = 28995720170841641432943050661225930338820
certificate: 2^12509555 * 638^100000 <= N^100000 < 2^12509556 * 638^100000
log2(N/C) = 125.0955511529
time_log2 = 125.09556
```
