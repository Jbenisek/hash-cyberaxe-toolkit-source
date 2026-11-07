Model: @@MODEL_NAME@@ / Harness: @@HARNESS_NAME@@

# Orchard Poseidon, r = @@R@@ (poseidon-orchard-r@@R@@-prefix-v1): algebraic collision algorithm, time_log2 @@TIME_LOG2@@, not executed at r = @@R@@

## Credit first

@@CREDIT_LINES@@

A credit is not an endorsement; nobody named here has reviewed this package.

## What this entry is

A collision finder for the reduced Orchard hash (eight full rounds and @@PARTIAL_WORD@@), written as an algorithm with a worst-case cost bound and a success probability that follows from one declared premise. It was not run at r = @@R@@: one trial needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@. The complete C source, the cost model that produces the ledger and the script that recomputes the probability are in proof.md.

The program tries at most K = @@K@@ centres, one after the other, on a single thread. For each centre c (drawn uniformly from the field with the cost model's random words) it builds the odd part g of the line polynomial from @@N2@@ evaluations and one inverse transform, computes S^((p-1)/2) mod g with a low-memory powering, takes the gcd of g with S^((p-1)/2) - 1 by a half-gcd and, when that gcd has between 1 and @@DMAX@@ roots, isolates one root with at most @@Z@@ coin rounds, takes the square root and maps it back to two distinct inputs with equal digests. Both inputs are checked with the reference hash before the program exits with success. If no centre of the K gives a collision the program exits with status 2 and prints nothing.

## The claim

* time_log2 @@TIME_LOG2@@: the worst-case operation count of the shipped source, N_max = @@N_BOUND@@ primitive operations = @@UNITS@@ target-compression units at @@C@@ operations per unit. Every one of the K trials is charged in full, with the root isolation at its cap of @@Z@@ rounds at degree @@DMAX@@; the coin draws, the twiddle table and the output are included. The offline derivation of the literals of the source is bounded by @@OFFLINE_BOUND@@ operations (proof.md section 6.2); that bound is inside N_max and is declared as preprocessing_log2 = @@PREP_LOG2@@.
* memory @@MEM_BYTES@@ bytes (log2 @@MEM_LOG2@@), normalized cost @@SCORE@@, no advice.
* success probability @@P_SUCC@@ (exact bound @@P_SUCC_EXACT@@): 1 - (1 - q)^K - K (eps_coin + eps_iso) with q = @@Q@@ and K = @@K@@, given the premise below. The probability is over the program's own random words for the fixed target. It is not a probability over targets and not a sampled frequency.

## Premise and limits

The premise H-GEOM-w@@W@@ is an assumption about the fixed polynomial F of the line construction at r = @@R@@ (degree 5^@@DEXP@@), not a fact. Its four fields as declared in claim.json:

* Statement. With G(c,t) = (F(c+t) - F(c-t))/(2t) and k(c) the number of nonzero squares S = t^2 with G(c,t) = 0: the plane curve G = 0 has at least one absolutely irreducible component defined over the prime field, and the curve V of triples (c, s1, s2) with G(c,s1) = G(c,s2) = 0 and s1^2 != s2^2 has at most @@W@@ absolutely irreducible components defined over the prime field. Weil's bound with explicit constants then gives E[k] >= 1/2 - e1 and E[k(k-1)] <= @@W@@/4 + e2 with e1 < @@E1@@ and e2 < @@E2@@ for a uniform centre; Cauchy-Schwarz and a Markov cap at k = @@DMAX@@ give q = @@Q@@ for the probability that a centre has between 1 and @@DMAX@@ usable roots (proof.md section 9.2; the arithmetic is recomputed with exact rationals in Appendix D).
* Role. Score-critical.
* Scope. The fixed Poseidon target poseidon-orchard-r@@R@@-prefix-v1, this line construction, centres uniform on the field. The explicit constants apply for r <= 7 only.
* Limitations. An assumption with no proof known to us. It is false for permutation polynomials (for example every pure composition of maps x -> a x^5 + b), and a statement about components over the algebraic closure does not imply it (X^3 over a field with p = 2 mod 3 has none). No test reaches the claimed degree.

Everything else in the success bound is proved in the proof: the centres are independent because the program draws them from independent random words; the isolation lemma bounds the failure of the root isolation (at most @@EPS_ISO@@ per trial) by a character-sum argument and an exact binomial sum; the coin rule has statistical distance at most @@EPS_COIN@@ from uniform. The proof ships a sensitivity table in the parameter w and in the good fraction of centres: with K = @@K@@ the good fraction can be smaller than q by the factor @@Q_RATIO_K@@ (down to @@Q_MIN_K@@) before the bound falls under 0.39, and w = 3 would need K = 3.

## Evidence, and what it cannot show

The proof has a section of evidence, labelled as evidence and kept apart from the bound; all of it is ours and none of it is an organizer execution. We ran the construction at full scale at rounds 3, 4 and 5 with the fixed centres 1, 2, ...: at r = 3 the first centre gave a usable root; at r = 4 the first gave none and the second did; at r = 5 the first did. We also ran the shipped program once at r = 3 with a coin centre; it found a collision on its first centre (a centre with a gcd of degree 2), and its counters agree with the cost model (the model is above the counters by 0.0055 bit). The collisions are listed in the proof. They are single runs, not a sample, and give no lower bound on the good fraction.

One organizer-run experiment is declared, lowbits-birthday: for each organizer trial the program returns two distinct messages whose digests of the target agree in the first 14 bits. @@EXECUTOR_STATUS_SENTENCE@@ It tests a reduced event on the digest; it is not offered as a test of the premise, the cost or the success probability.

Why the premise cannot be proved or run at this round count: one trial at r = @@R@@ needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@, and the degree grows by a factor of five with every round.

## What is in the package

claim.json (one score-critical heuristic H-GEOM-w@@W@@, one supporting heuristic H1-charging-rules), proof.md (the algebra, the algorithm, the worst-case ledger, the offline bound, the premise with its reduction, the success bound with its sensitivity, the isolation lemma, the evidence, and the complete C source with the cost model and scripts), certificates/manifest.json (empty), experiments/manifest.json and the one Python source. Nothing is attached that the rules do not require.

## Reasoning narrative

Context. Our executed entries at r = 3, 4 and 5 settled the success question by running the program once, from fixed centres, and claiming its executed cost with probability 1. That convention stops working when one trial no longer fits the machines we have: at r = 6 a trial takes days on 24 threads and about 31 GB, and at r = @@R@@ it needs @@TRIAL_MEM@@. The question then becomes what to claim, and the honest answer is a worst-case bound for the algorithm plus a probability that is exactly as good as one named assumption.

Approach. Keep the algorithm of the executed entries, but give it coins (a random centre per trial, charged), cap the number of trials, cap every data-dependent loop, run on one thread so that no dispatch or thread control exists to be omitted, and charge all K trials in full. State the one assumption as a statement about two curves attached to the fixed polynomial, reduce the probability to it with explicit constants, prove the rest, and show how the bound moves if the assumption is off.

Trade-offs. Charging K full trials instead of the expected number costs a factor of about K over the executed convention (K = @@K@@ here); a larger K buys robustness against a smaller good fraction at log2(K'/K) bits. Restricting to at most @@DMAX@@ usable roots keeps the isolation step cheap and its cost a provable maximum, at a Markov price of @@TAIL@@ in the good fraction.

Implementation. The finite-field code, the transform engine, the low-memory powering and the half-gcd are those of our r = 3, 4, 5 programs. New for this entry: the coin draw and its charge, the capped trial loop, the capped isolation stage, the single-thread build, the worst-case ledger and the cost model that produces it.

Results. No run at r = @@R@@. The numbers above are bounds; the proof says which part of each is proved, counted or assumed.

Next steps. A cheaper powering schedule lowers the bound directly; a count of rational points of the curves G = 0 and V at a reduced scale would be the first data on the premise.
