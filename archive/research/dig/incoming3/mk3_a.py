from mk3_common import *

# ---------------- U73
U="blake3-r3-U73"
add(U,"blake3-r3|DOOR.d24|DOOR|D1","door 24: force more than 4 digest words by construction",
 "D1 RELABEL at 3 rounds: own bijection check on E1/E3 inputs over a sampled outer step; plus the legal 55/63 length-cancel pair counted at rounds 1/2/3",
 ["Z"],"LOCAL_ONLY",
 "(A) 3 sampled outer steps (b/flags 55/11, 63/3, 64/11) x 2^22 inner words w0 at ROUNDS=3 (20 points per step cross-checked against verifier _compress at 3 rounds): round-0 state X unchanged (0 of 16 words vary); only Y6 (E1 input) and Y14 (E3 input) vary; #Y6 = #Y14 = #(Y6,Y14) pairs = #distinct w0 (4,192,230 / 4,192,266 / 4,192,253 of 4,194,304) against a product of about 1.757e13; closed form Y6 = ROR7(C2.b1 ^ (C2.c1+Y14)) holds on all 3 x 2^22 points; all 16 state words entering the third round vary with w0. Identical to the r2 result: rounds past 2 do not touch the first two rounds. (B) legal pair A (b55, flags 3) vs B (b63, flags 11), only m4..m7 re-signed so the round-0 state is identical (checked, 16 of 16 words): digest words equal in 100 percent of 2^18 pairs: 8 of 8 at 1 round (known answer), 0 of 8 at 2 rounds, 0 of 8 at 3 rounds; digest bits that never differ: 256, 0, 0 of 256. So the round-0 cancellation alone pins nothing once a second round runs; at 3 rounds no digest word is pinned by construction (word-model X1 for D={4,5} says 8 checks at r3, consistent).",
 ev(U,"d24.py","d24.out","b3own.py","common.py","validate.out"),
 KNOWN+" The r2 claim of exactly 4 digest pins needs the round-1 cancellations (message words solved for the E-step); that construction was NOT rebuilt here (the r2 cell did not rebuild it either), so the pin count at 2 and 3 rounds under the full construction stays as the word model X1 states it. Part B is a negative control: round-0 cancellation only.",
 "cv = IV, block counter solved (q = ROL(K0.d1,16)^K0.a1) and w1 solved so K0 outputs and X stay fixed; 3 outer steps with random other words; pair test: random m, only m4,m5,m6,m7 re-signed, 2^18 pairs, block lengths 55/63, flags 3/11",
 "a construction that keeps at least one digest word equal at 3 rounds by solving round-1 and round-2 cancellations, or the r2 4-pin construction rebuilt and carried through round 2 with a pinned-word count above 0",
 topic="b3.door24.bijection")
add(U,"blake3-r3|DOOR.d37|DOOR|D1","door 37: fresh CV / prior block per context (mode lever)",
 "D1 RELABEL at 3 rounds: ledger arithmetic, what does one fresh-CV prior block (638 operations = 1 unit) cost on the filed r3 ledger",
 ["Z"],"COMPUTED",
 "Filed ledger reproduced exactly (2.925843e40 operations = 4.585961e37 units, time_log2 125.10856). One prior block of 638 operations (1 unit) costs: once for the attack 3.1e-38 bit; per trail start (18,432 starts) or per finished trail 5.8e-34 bit; per recovery 3.1e-38 bit; per evaluated point (86.08 ledger operations per evaluated point, so one extra block multiplies the cost by 8.41) 3.07 bit; per batch of 7 lanes sharing one block 1.04 bit. The target fixes the chaining value (0^32 || x is one block, flags 11, standard IV), so a fresh CV is not even available for this target; no measured r3 lever uses CV freedom, so nothing buys the cost back.",
 ev(U,"d37.py","d37.out"),
 "Pure arithmetic on rho.py ledger(256) (exact integers). Unlike the r2 door (many contexts) the r3 line is one birthday search with no context structure, so the penalty is either negligible (once or per trail) or large (per evaluation); there is no middle case. Check first: the base ledger and 125.10856 reproduced.",
 "filed ledger of the r3 birthday entry (rho.py plan/ledger); prior block 638 operations",
 "a r3 lever that needs a different chaining value per trail or per evaluation and saves more than 3.07 bit per evaluation",
 gain_basis="T")

# ---------------- U74
U="blake3-r3-U74"
add(U,"blake3-r3|DOOR.d38|DOOR|D1","door 38: parent/CV separability bias at 3 rounds",
 "D1 RELABEL at 3 rounds: separability bias test (second-order derivative of the parent compression) at N = 2^22 quadruples, two seeds",
 ["Z"],"SAMPLED",
 "Own code sep_test3.py (r2 test with rounds=3), parent compress f(L,R) = compress(IV, L||R, t=0, len 64, flags 12, 3 rounds), self-check 50/50 against verifier blake3(rounds=3) on 2-chunk messages and rounds=7 equal. Seed 20261011, N=2^22: T1 xor max |P-1/2| 0.000856 (3.51 sigma, bit 126); T2 add max 0.000654 (2.68 sigma, bit 90), P(word==0) max 0; T3 64 word-pair cells x 65,536 quads worst 0.00810, flagged 0, confirmed 0; T4 1024 bit-pair cells x 16,384 quads worst 0.01715, flagged 0, confirmed 0. Replicate seed 777, N=2^22: T1 0.000706 (2.89 sigma, bit 15), T2 0.000610 (2.50 sigma, bit 8), T3 worst 0.00771, T4 worst 0.01776, flagged 0 confirmed 0. The 3.51 sigma bit (126) did not recur in the replicate (a different bit, 2.89 sigma): sampling noise (the maximum of 256 normal deviates exceeds 3.5 sigma about 11 percent of the time). No usable biased bit at 3 rounds.",
 ev(U,"sep_test3.py","sep22.out","sep22b.out"),
 "Same code and flag rules as the r2 run (research/dig/incoming2/blake3-r2-G05-U12/work/sep_test.py) with the round count changed 2 to 3 and the verifier path pointed at the pareto_clone verifier. N=2^22, not 2^24 (time limit 5 minutes); at 2 rounds the same test gave 0.000338 at 2^24. The RELAX 2/4 word-level model (trunc_relax.c) is specific to 2 rounds and was NOT rerun at 3 rounds; word-level r3 results are B3R3-X1 (6 checks at best for up to 3 difference words).",
 "cv = IV for the parent node, t = 0, block length 64, flags 12 (PARENT|ROOT), 3 rounds; N = 2^22 quads; seeds 20261011 and 777",
 "a bias above 2^-8 confirmed on fresh samples at 3 rounds, or a RELAX model for 3 rounds with fewer than 8 word conditions",
 gain_basis="count")
add(U,"blake3-r3|DOOR.d45|DOOR|D1","door 45: chaining-value route via a 224-bit near-collision first block",
 "D1 RELABEL at 3 rounds (no test given): is matching k bits of words 1..7 of a 3-round first-block CV cheaper than generic?",
 ["Z"],"LOCAL_ONLY",
 "3-round CHUNK_START block (cv=IV, t=0, b=64, flags 1), N = 2^24 random blocks, k bits taken round-robin from digest words 1..7 (word 0 free): pairs / expected(uniform birthday) = 1.007 (k=32, 33,010 pairs), 1.048 (k=36, 2,147 vs 2,048), 1.102 (k=40, 141 vs 128), 1.375 (k=44, 11 vs 8), 0 vs 0.5 (k=48). All within Poisson noise (largest z about 1.15). No excess over generic; generic price of a 224-bit match is 2^112 evaluations (of a 128-bit match 2^64).",
 ev(U,"d45.py","d45.out"),
 "Known answer first: compress(flags=1, b=64) equals the verifier _compress on 50/50 points at rounds 3 and 7. LOCAL_ONLY: toy k up to 48 and random (unstructured) first blocks; a structured near-collision (difference trail) is not tested, so the claimed 2^64 stays unexplained, not refuted. "+KNOWN,
 "first block of a chunk only (flags 1), cv = IV, t = 0, b = 64, 3 rounds; random blocks; 2^24 samples; toy k 32..48",
 "an excess of pairs above uniform that grows with k at 3 rounds, or a structured difference trail with fewer than 7 word conditions across the 3 rounds",
 gain_basis="count")

# ---------------- U75
U="blake3-r3-U75"
add(U,"blake3-r3|PREM.H1|PREM|R4","H1-random-mapping (score-critical): f(x) = digest(0^32 || x) behaves as a random mapping on 2^256 points",
 "R4 score sensitivity: bits of time per unit deficit of the pair-collision rate, and the slack before the claimed success 0.39 is lost",
 ["N"],"COMPUTED",
 "Exact ledger rerun (rho.py ledger with lambda scaled by 1/(1-eps), success 0.39 restored by more evaluations): eps = 0.001 +0.0007 bit; 0.0046 +0.0033; 0.01 +0.0072; 0.05 +0.0367; 0.10 +0.0755; 0.25 +0.2061; 0.50 +0.4969 (closed form 0.5*log2(1/(1-eps))); slope 0.7213 bit per unit eps. Success 0.39 is lost without repair at eps > 0.0049 (own recount, total losses 1.6e-4) or 0.0050 (losses 1.2e-4); the entry states 0.0046 / 0.0047, so the stated threshold is conservative. A higher true rate would help: +1 percent rate -0.0072 bit, +10 percent -0.0688, x2 -0.5 (not claimed). Required success p moves the time by 0.5*log2(lambda): p=0.30 -0.2374 bit, 0.39 (lambda 0.4943) -0.0039, 0.50 +0.2383, 0.63 +0.4971, 0.90 +1.1003 against the filed lambda 0.497.",
 ev(U,"h12.py","h12.out"),
 "H1 itself is not tested here (cannot be at width 256); this cell prices what a deficit would cost. Basis: exact ledger arithmetic.",
 "ledger of the filed entry (125.10856), plan(256), only lambda varied, all halts/caps at their filed formulas",
 "evidence of a collision-rate deficit above 0.5 percent at the scales the search evaluates (then 0.0036 bit per half percent)",
 gain_basis="T")
add(U,"blake3-r3|PREM.H2|PREM|R2","H2-loss-terms: losses of Section 4 (unfinished and cut trails, repeats, key false matches, aborts)",
 "R2 own recount of every loss term of proof.md Section 4",
 ["N"],"COMPUTED",
 "Recounted from the plan: unfinished-trail sum P(Gamma(7) > 28) = 5.825e-7 (proof 5.8e-7); trails Q/L = 16,365.2, cut-trail mean 0.1006, P(K=0,1,2) = 0.9043 0.0909 0.0046, P(K>=3) = 1.57e-4; success lowered by K=1: 3.53e-4, K=2: 7.97e-4 (proof 3.5e-4, 8.0e-4); cut-trail deficit 9.70e-5 (proof 9.7e-5); pairs inside one trail Q L/N = 2^-14.00; 64-bit key false matches among 18,432 entries 9.2e-12 = 2^-36.7 (proof below 2^-36); table-overflow Chernoff ln P = -125.5 (proof e^-125.5); stage-2 exponent 3.06e28; lambda_eff = U(U-1)/2N = 0.49700, 1 - exp(-0.497) = 0.39165. All reproduced. One finding: the cut-trail deficit 9.7e-5 already contains the K>=3 term (1.5e-4 x 0.3916 = 6.1e-5), and the loss sum then adds 6.1e-5 again (6e-7 + 6.1e-5 + 9.7e-5): that term is counted twice, so the real loss is about 9.8e-5 not 1.6e-4. Conservative, no error against the claim. Margins in the entry: 0.0015 kept margin (worth 0.0032 bit if spent, lambda 0.4948 for p = 0.39 + 1.6e-4), double count 6.1e-5 worth about 0.00015 bit.",
 ev(U,"h12.py","h12.out"),
 "Slack candidates only (total about 0.0034 bit, all of it deliberately kept margin), not a lever: spending the margin would leave the single-attempt success at exactly 0.39 with no room for the unmodelled terms. "+KNOWN,
 "Section 4 formulas of proof.md and plan(256) parameters (7 lanes, d = 114, kappa 12, inflight 28, cut allowance 1.5e-4)",
 "a loss term not in Section 4 (for example dependence between trail ages and DP events at the 2^114 scale), or a recount that gives losses above 1.65e-3",
 gain_basis="T")
add(U,"blake3-r3|PREM.H2|PREM|R3","H2-loss-terms: losses of Section 4 (unfinished and cut trails, repeats, key false matches, aborts)",
 "R3 control: Monte Carlo of the three loss laws against the closed forms (control thresholds), and the shipped program metered at n = 22 and 32",
 ["N"],"SAMPLED",
 "Laws (3e8 draws, numpy): Gamma(7) > 28: observed 166 vs expected 174.7 (z -0.66); controls Gamma(7) > 14: 284,534 vs 284,558 (z -0.05), > 10: 2,601,992 vs 2,602,828 (z -0.56). Cut-trail count Binomial(16,365, e^-12), 1e8 draws: P(K=0,1,2,3) = 0.90433 0.09094 0.00458 0.00015 vs Poisson law 0.90434 0.09093 0.00457 0.00015. Shipped program (rho.py search/recover unchanged, real 3-round target), n = 32 (d = 8, Q = 72,527, the T3 setting): 747 attempts, DP-rate control finished trails x L / evaluations = 1.0010 (176,815 trails over 45,221,358 evaluations; law 1), 0 cut trails, success 0.423 (316 of 747), halts 3 (0.4 percent); n = 22: 4,000 attempts, success 0.465, halts 272 (6.8 percent, small-width regime where the budgets are tight). Observed success at n = 32 sits below the pure-birthday value 0.458 by the in-flight and cut losses as planned (T3: 0.443 on the target); our 0.423 is -1.9 sigma of 0.458 and -1.1 sigma of the T3 value.",
 ev(U,"mc_h2.py","mc_h2.out")+", "+ev("blake3-r3-U76","ctrl.py","ctrl22.out","ctrl32.out"),
 "Monte Carlo checks the arithmetic of the laws, not H1; the metered runs check the DP-rate law (c) of H1 at n = 32 on the real target at 1 percent precision and nothing at 2^114. Cut trails are too rare to observe at small n (cap 12 L).",
 "laws of proof.md Lemma 2; shipped rho.py at n = 22 and 32, fresh seeds ctrl-r3-a, ctrl-r3-b",
 "a DP-rate ratio away from 1 by more than 2 percent at n >= 32, or a success rate at n = 32 below 0.40 over 2,000 attempts",
 gain_basis="count")
add(U,"blake3-r3|PREM.H2|PREM|R4","H2-loss-terms: losses of Section 4 (unfinished and cut trails, repeats, key false matches, aborts)",
 "R4 score sensitivity of the loss parameters on the exact ledger",
 ["N"],"COMPUTED",
 "In-flight allowance 28 L -> 56 L: +0.00245 bit; -> 14 L: -0.00123 bit. Cut allowance x10: +0.00194; x0: -0.00022. Age cap kappa 12 -> 24: +0.00808 bit; -> 8: -0.00270 bit (a smaller cap saves time but makes K (cut trails, Poisson mean 16,365 e^-kappa) larger: kappa 8 gives mean 5.5 cut trails, which the proof does not cover). Every H2 parameter moves the score by under 0.01 bit over a factor-of-two change.",
 ev(U,"h12.py","h12.out"),
 "Ledger only; the success side of each change is not re-derived (except kappa, remarked).",
 "plan(256) with one parameter changed at a time",
 "a loss term growing by an order of magnitude",
 gain_basis="T")
add(U,"blake3-r3|PREM.H3|PREM|R2","H3-machine-convention: ledger counted in the convention of the organizer count C(r3) = 638",
 "R2 own recount of the 595 operations of one 7-lane batch",
 ["N"],"COMPUTED",
 "Counted from the emitted straight-line source (595 lines, one operator each): 100 add + 88 xor + 80 shr + 80 shl + 80 or + 167 and = 595, equal to the tracer. By phase: round 0 116 (four diagonal calls only; the column calls are constants), round 1 232, round 2 235 (includes 3 masks), digest 12. Matches the proof (116 + 232 + 235 + 12). Per lane-step 85.00 operations = 0.1332 unit; one lane alone 595 = 0.9326 unit.",
 ev(U,"h3.py","h3.out","orgcount.py","orgcount.out"),
 KNOWN,
 "fixed key m0..m7 = 0, IV, counter 0, length 64, flags 11, 3 rounds, 7 lanes of 36 bits, greedy mask insertion by the filed tracer",
 "a cheaper correct circuit for the same function (see MACHINE.WIDTH Q4 for the pitch/lane family)",
 gain_basis="count")
add(U,"blake3-r3|PREM.H3|PREM|R3","H3-machine-convention: ledger counted in the convention of the organizer count C(r3) = 638",
 "R3 control: guard-bit scheme on extreme inputs, and the same tracer on the unfolded circuit against the organizer count",
 ["N"],"COMPUTED",
 "Extreme and structured inputs (all pairs of 0, 1, 0x7FFFFFFF, 0x80000000, 0xAAAAAAAA, 0x55555555, 0xFFFFFFFF in all 8 words, plus 2,000 random mixtures): 14,343 lanes, 0 mismatches against the scalar digest; on an all-ones input no non-shift intermediate exceeds 252 bits (machine word 256). Control against the organizer: the organizer's own counter gives 638 for the 3-round compress (145 and, 97 shr, 96 add, 108 xor, 96 shl, 96 or; run on the organizer verifier only); our tracer on the same unfolded compress (IV, counter, length, flags and all 16 message words as variables, 5-operation rotations with guard bits) counts 736 (144 add, 104 xor, 96 shr, 96 shl, 96 or, 200 and). So the organizer reference is 98 operations (13 percent) lighter than our per-operation count of the same circuit; the unit is conservative for us, and the 595 comes from folding the fixed key and constants (141 saved), then 7-lane packing.",
 ev(U,"h3.py","h3.out","orgcount.out"),
 "The organizer counter leaves some first operations uncounted by construction of its Word class (plain-int operands); we did not change it. The gap is disclosed, not used.",
 "same circuit, two counters: organizer Word counter vs filed Tracer",
 "a judge ruling that prices packed operations differently from single operations",
 gain_basis="count")
add(U,"blake3-r3|PREM.H3|PREM|R4","H3-machine-convention: ledger counted in the convention of the organizer count C(r3) = 638",
 "R4 score sensitivity of the machine convention (registers, spills, width)",
 ["N"],"COMPUTED",
 "Per batch operation: +/-1 operation = +/-0.00241 bit; 10 percent of the batch (59.5 operations) = 0.149 bit. Registers: zero loads/stores need 25 simultaneously live values (exact liveness; list scheduling gives 25 too); at 24 registers +0.0048 bit (2 loads), 20 +0.026, 16 +0.072 (31 extra ops/batch), 12 +0.156, 8 +0.246 (emitted order; Belady eviction). The entry's remark that fewer than about 40 registers would cost is too pessimistic: 25 plus a few control registers suffice. Width: a 512-bit word at the same priced op would be -1.0355 bit (15 lanes of 34, 622 ops, 41.47 per step) if priced as one op; as two ops 0. The convention costs the score at most these amounts; none is a saving on the filed entry.",
 ev("blake3-r3-U81","regs.py","regs.out")+", "+ev("blake3-r3-U80","width.py","width.out"),
 "Spill counts use Belady eviction on the emitted order (optimal for loads, heuristic for stores) with one operation per load or store; a register-starved machine is not offered by the organizer text (register count is silent).",
 "straight-line batch of 595 + 4 filter operations, loop-carried digest registers, immediates free",
 "organizer text that fixes a register count below 25 or prices a 512-bit word",
 gain_basis="T")
