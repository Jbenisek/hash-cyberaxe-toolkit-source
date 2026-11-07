Model: @@MODEL_NAME@@ / Harness: @@HARNESS_NAME@@

# Orchard Poseidon, r = @@R@@ (poseidon-orchard-r@@R@@-prefix-v1): algebraic collision algorithm, time_log2 @@TIME_LOG2@@

## Credit first

@@CREDIT_LINES@@

A credit is not an endorsement; nobody named here has reviewed this package.

## What this entry is

A collision finder for the reduced Orchard hash (eight full rounds and @@PARTIAL_WORD@@), written as an algorithm with a worst-case cost bound and a success probability that follows from one declared premise. One trial at r = @@R@@ needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@. The script that recomputes the probability is in proof.md.

The algorithm tries at most K = @@K@@ centres, one after the other, on a single thread. For each centre c (drawn uniformly from the field from fresh random words) it builds the odd part g of the line polynomial from @@N2@@ evaluations and one inverse transform, computes S^((p-1)/2) mod g with a low-memory powering, takes the gcd of g with S^((p-1)/2) - 1 by a half-gcd and, when that gcd has between 1 and @@DMAX@@ roots, isolates one root with at most @@Z@@ coin rounds, takes the square root and maps it back to two distinct inputs with equal digests. Both inputs are checked with the reference hash before the algorithm outputs them. If no centre of the K gives a collision the algorithm fails.

## The claim

* time_log2 @@TIME_LOG2@@: the worst-case operation count of the algorithm, N_max = @@N_BOUND@@ primitive operations = @@UNITS@@ target-compression units at @@C@@ operations per unit. Every one of the K trials is charged in full, with the root isolation at its cap of @@Z@@ rounds at degree @@DMAX@@; the coin draws, the twiddle table and the output are included. The offline derivation of the constants is bounded by @@OFFLINE_BOUND@@ operations (proof.md section 6.2); that bound is inside N_max and is declared as preprocessing_log2 = @@PREP_LOG2@@.
* memory @@MEM_BYTES@@ bytes (log2 @@MEM_LOG2@@), normalized cost @@SCORE@@, no advice.
* success probability @@P_SUCC@@ (exact bound @@P_SUCC_EXACT@@): 1 - (1 - q)^K - K (eps_coin + eps_iso) with q = @@Q@@ and K = @@K@@, given the premise below. The probability is over the algorithm's fresh random words for the fixed target. It is not a probability over targets and not a sampled frequency.

## Premise and limits

The premise H-GEOM-w@@W@@ is our theory about the fixed polynomial F of the line construction at r = @@R@@ (degree 5^@@DEXP@@). Its four fields as declared in claim.json:

* Statement. With G(c,t) = (F(c+t) - F(c-t))/(2t) and k(c) the number of nonzero squares S = t^2 with G(c,t) = 0: the plane curve G = 0 has at least one absolutely irreducible component defined over the prime field, and the curve V of triples (c, s1, s2) with G(c,s1) = G(c,s2) = 0 and s1^2 != s2^2 has at most @@W@@ absolutely irreducible components defined over the prime field. Weil's bound with explicit constants then gives E[k] >= 1/2 - e1 and E[k(k-1)] <= @@W@@/4 + e2 with e1 < @@E1@@ and e2 < @@E2@@ for a uniform centre; Cauchy-Schwarz and a Markov cap at k = @@DMAX@@ give q = @@Q@@ for the probability that a centre has between 1 and @@DMAX@@ usable roots (proof.md section 9.2; the arithmetic is recomputed with exact rationals in Appendix D).
* Role. Score-critical.
* Scope. The fixed Poseidon target poseidon-orchard-r@@R@@-prefix-v1, this line construction, centres uniform on the field. The explicit constants apply for r <= 7 only.
* Limitations. It is false for permutation polynomials (for example every pure composition of maps x -> a x^5 + b), and a statement about components over the algebraic closure does not imply it (X^3 over a field with p = 2 mod 3 has none).

Everything else in the success bound is proved in the proof: the centres are independent because each draw uses fresh random words; the isolation lemma bounds the failure of the root isolation (at most @@EPS_ISO@@ per trial) by a character-sum argument and an exact binomial sum; the coin rule has statistical distance at most @@EPS_COIN@@ from uniform. With K = @@K@@ the good fraction can be smaller than q by the factor @@Q_RATIO_K@@ (down to @@Q_MIN_K@@) before the bound falls under 0.39.

## Evidence

The proof has a section of evidence, kept apart from the bound. (1) We ran the construction at full scale at rounds 3, 4 and 5 with the fixed centres 1, 2, ...: at r = 3 the first centre gave a usable root; at r = 4 the first gave none and the second did; at r = 5 the first did. The collisions are listed in the proof. (2) One organizer-run experiment is declared, lowbits-birthday: for each organizer trial the program returns two distinct messages whose digests of the target agree in the first 14 bits. @@EXECUTOR_STATUS_SENTENCE@@ (3) Grok job 135, computed exactly over the Pallas field for a toy permutation on a generic line: the hypothesis of the premise holds with w = 1 at one full round (Theorem A), and at two full rounds the curve G = 0 is absolutely irreducible with a reduced pair scheme of pure dimension 1 (Theorem B); the degree is exactly 5^N (Theorem D). Our line is generic in this sense: the polynomial it produces is dense in our miniature runs. All of this is supporting evidence for our theory (proof.md section 10).

One trial at r = @@R@@ needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@, so the claim is the premise with its reduction.

## Answers to the ruling on eed8c9e1 (the entry this one replaces)

* F-EVAL-001 (probability space): the coins are the cost model's independent uniform 256-bit words, one word per draw, reduced modulo p (proof.md 4.1.1); the statistical distance is S3 (1/p - 3/2^256) = @@EPS_COIN@@, and the draw costs @@COIN_DRAW_COST@@ operations (section 4.2); sections 9.2 and 9.4 and Appendix D are recomputed with it.
* F-EXP-01 (no organizer execution): the organizer experiment lowbits-birthday is declared (experiments/manifest.json, proof.md 10.2).
* F-EVAL-002, F-EXP-02, F-EXP-03, F-COST-03, LC-F1 (evidence for H-GEOM-w2): proof.md 10.2 and 10.3 (the organizer experiment on the digest, and the exact computations for the generic line at one and two rounds).
* F-COST-01 (stage C and D literals): proof.md Appendix E expands both from the transform sizes, Newton levels, squaring steps and half-gcd levels and asserts them.
* F-COST-02, F-EVAL-003, F-EXP-04 (arena at r = 7, normal Euclidean sequences): unchanged; both are declared in H1-charging-rules (A1, A2) with the rules of section 7.

## What is in the package

claim.json (one score-critical heuristic H-GEOM-w@@W@@, one supporting heuristic H1-charging-rules), proof.md (the algebra, the algorithm, the worst-case ledger, the offline bound, the premise with its reduction, the success bound, the isolation lemma, the evidence, the premise arithmetic and the stage C and D expansion), certificates/manifest.json (empty), experiments/manifest.json and the one Python source of the experiment. Nothing is attached that the rules do not require.

## Reasoning narrative

Context. Our executed entries at r = 3, 4 and 5 settled the success question by running the program once, from fixed centres, and claiming its executed cost with probability 1. That convention stops working when one trial no longer fits the machines we have: at r = 6 a trial takes days on 24 threads and about 31 GB, and at r = @@R@@ it needs @@TRIAL_MEM@@. The question then becomes what to claim, and the honest answer is a worst-case bound for the algorithm plus a probability that is exactly as good as one named assumption.

Approach. Keep the algorithm of the executed entries, but give it coins (a random centre per trial, charged), cap the number of trials, cap every data-dependent loop, run on one thread so that no dispatch exists to be omitted, and charge all K trials in full. State the one assumption as a statement about two curves attached to the fixed polynomial, reduce the probability to it with explicit constants, and prove the rest.

Trade-offs. Charging K full trials instead of the expected number costs a factor of about K over the executed convention (K = @@K@@ here); a larger K buys robustness against a smaller good fraction at log2(K'/K) bits. Restricting to at most @@DMAX@@ usable roots keeps the isolation step cheap and its cost a provable maximum, at a Markov price of @@TAIL@@ in the good fraction.

Implementation. The finite-field arithmetic, the transform engine, the low-memory powering and the half-gcd are those of our r = 3, 4, 5 programs. New for this entry: the coin draw and its charge, the capped trial loop, the capped isolation stage, the worst-case ledger.

Results. The numbers above are bounds; the proof says which part of each is proved or counted and which part is the premise.

Next steps. A cheaper powering schedule lowers the bound directly; the same exact computation for the explicit F at higher round counts would extend the evidence for the premise.
