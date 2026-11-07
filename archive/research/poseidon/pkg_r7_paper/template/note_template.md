Model: @@MODEL_NAME@@ / Harness: @@HARNESS_NAME@@

# Orchard Poseidon, r = @@R@@ (poseidon-orchard-r@@R@@-prefix-v1): algebraic paper entry, time_log2 @@TIME_LOG2@@, not executed

## Credit first

@@CREDIT_LINES@@

* The two-round bypass on a special line, which makes the digest a univariate polynomial of degree 5^@@DEXP@@, is the method of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3). The odd-part reduction, the half-gcd schedule, the low-memory powering and the ledger are ours, built on the structure of our executed entries at rounds 3, 4 and 5.
* The charging conventions follow the accepted entries of the other tracks (every load, store and control operation priced, no free registers, no free dispatch).

A credit is not an endorsement; nobody named here has reviewed this package.

## What this entry is

A collision finder for the reduced Orchard hash (eight full rounds and @@PARTIAL_WORD@@), written as an algorithm with a worst-case cost bound and a success probability that rests on one declared premise. It was NOT run at r = @@R@@. This is different from our entries at r = 3, 4 and 5, which were single deterministic runs on the fixed target with the claim equal to the executed operation count and success probability 1; here the claim is a worst-case bound for a program that draws its centres from its own coins, and the probability is a bound derived from an assumption. The note says so in the first lines because the two kinds of entry must not be mixed up.

The program tries at most K = @@K@@ centres, one after the other, on a single thread. For each centre c (drawn uniformly from the field with charged coins) it builds the odd part g of the line polynomial from 2 x @@N2_HALF@@ evaluations and one inverse transform, computes S^((p-1)/2) mod g with a low-memory powering, takes the gcd of g with S^((p-1)/2) - 1 by a half-gcd, and, when that gcd has between 1 and @@DMAX@@ roots, isolates one root with at most @@Z@@ charged coin rounds, takes the square root and maps it back to two distinct inputs with equal digests. Both inputs are checked with the reference hash before the program exits with success. If no centre of the K gives a collision the program exits with a failure status and prints nothing; that event has probability bounded in the proof.

## The claim

* time_log2 @@TIME_LOG2@@: the worst-case operation count of the shipped source, N_max = @@N_BOUND@@ primitive operations = @@UNITS@@ target-compression units at @@C@@ operations per unit, every one of the K trials charged in full, coins, twiddle table and output included. The cap on the trial count is tested at the start of every trial; the isolation rounds are capped; every other loop has a length fixed by the degree. There is no case outside the bound.
* memory @@MEM_BYTES@@ bytes (log2 @@MEM_LOG2@@), normalized cost @@SCORE@@, preprocessing 0, no advice.
* success probability @@P_SUCC@@: 1 - (1 - q)^K - K (eps_coin + eps_iso) with q = @@Q@@ and K = @@K@@, given the premise below. The probability is over the algorithm's own coins for the fixed target. It is not a probability over targets and not a sampled frequency.

## Premise and limits

The premise H_root is an assumption about the fixed function, not a fact. Its four fields as declared in claim.json:

* Statement. For the fixed polynomial F of the line construction at r = @@R@@ (degree 5^@@DEXP@@), the fraction of centres c for which the odd part g_c has between 1 and @@DMAX@@ distinct roots in the field that are nonzero squares is at least q = @@Q@@. For a random polynomial the number of usable roots is asymptotically Poisson with mean 1/2, so the random value is 1 - e^(-1/2) = 0.3935 (a root of any kind exists with probability 1 - 1/e = 0.632; half of the roots are squares).
* Role. Score-critical.
* Scope. The fixed Poseidon target poseidon-orchard-r@@R@@-prefix-v1, this line construction, centres uniform on the field.
* Limitations. An assumption with no proof known to us. Nothing in the algebra forces the fixed F to behave like a random polynomial over uniform centres; the odd parts for different centres all come from one F. No test reaches the claimed degree.

Everything else in the success bound is proved in the proof: the centres are independent because the algorithm draws them from independent coins; the isolation lemma bounds the failure of the root isolation (at most @@EPS_ISO@@ per trial) by a character-sum argument; the coin rule has statistical distance at most @@EPS_COIN@@ from uniform. The proof ships a sensitivity table: if the true fraction of good centres were 0.20 the bound at K = 2 would be 0.36; the number of centres that restores 0.39 is 3 at q = 0.20, 4 at 0.15, 10 at 0.05, each at the log2 cost shown there. With the submitted K = @@K@@ the premise can be off by a factor @@Q_RATIO_K@@ (down to q = @@Q_MIN_K@@) before the bound falls under 0.39.

## Evidence, and what it cannot show

The proof has a section of evidence, labelled as evidence and kept apart from the bound. We ran the construction at full scale at rounds 3, 4 and 5@@R6_PHRASE@@: at r = 3 the first centre (c = 1) gave a usable root; at r = 4 the first centre gave none and the second (c = 2) did; at r = 5 the first centre did@@R6_NOTE_SENTENCE@@. Each of those is one deterministic run with the fixed centres 1, 2, ... that stops at its first success, so it is not a sample of the centre distribution and gives no lower bound on the fraction; the operation counts, memory and the collisions found are in the proof, and the replay experiment recomputes each recorded pair at its own round count. A second experiment measures, on a toy permutation of the same family over a field of 8,017 elements with degree 125 and 625, the exact fraction of ALL centres with a usable root (3,145 and 3,166 of 8,017, against 3,145 and 3,179 for a random table, expected about 0.3935); this is a measurement on two fixed toy functions, not on the target.

Why the premise cannot be proved or run at this round count: one trial at r = @@R@@ needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@, and the degree grows by a factor of five with every round. Toy experiments cannot reach the claimed degree, so the claim is the premise, supported by every full-scale outcome we have. At r = 1 and r = 2 this line did not need a premise: the degrees were small enough for the success claim to be settled by a proved bound or by the executed run, and we used that.

Other limits, stated plainly. The organizer's experiment kind returns checked output pairs only, infers no probability and no cost, and both of our experiments return no pair for the selected target (their results are in the untrusted observations and in the source text). @@EXECUTOR_STATUS_SENTENCE@@ The worst-case ledger is derived by formula from the shipped source and validated against the counters of the executed runs at smaller r; it has not been measured at r = @@R@@, and the organizer did not run the program, so the counts rest on the shipped source. Word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of the model.

## What is in the package

claim.json (one score-critical heuristic H_root, one supporting heuristic H1-charging-rules), proof.md (the algebra, the algorithm, the worst-case ledger, the premise, the success bound with its sensitivity table, the isolation lemma, the evidence, and the complete C source), certificates/manifest.json (empty), experiments/manifest.json and the two Python sources (together under 64 KiB). Nothing is attached that the rules do not require.

## Reasoning narrative

Context. Our executed entries at r = 3, 4 and 5 settled the success question by running the program once, from fixed centres, and claiming its executed cost with probability 1. That convention stops working when one trial no longer fits the machines we have: at r = 6 a trial takes days on 24 threads and about 31 GB, and at r = @@R@@ it needs @@TRIAL_MEM@@. The question then becomes what to claim, and the honest answer is a worst-case bound for the algorithm plus a probability that is exactly as good as one named assumption.

Approach. Keep the algorithm of the executed entries, but give it coins (a random centre per trial, charged), cap the number of trials, cap every data-dependent loop, run on one thread so that no dispatch or thread control exists to be omitted, and replace the stopping on luck by a bound that charges all K trials in full. State the one assumption as an assumption about the fixed function over those coins, prove everything else, and show how the bound moves if the assumption is off.

Trade-offs. Charging K full trials instead of the expected number costs a factor of about K over the executed convention (K = @@K@@ here), and a larger K buys robustness against a smaller fraction of good centres at log2(K'/K) bits; the sensitivity table is there so the choice can be read off. Restricting to usable roots that number at most @@DMAX@@ keeps the isolation step cheap and its cost a provable maximum.

Implementation. The finite-field code, the transform engine, the low-memory powering and the half-gcd are those of our r = 3, 4, 5 programs. New for this entry: the coin rule and its charge, the capped trial loop, the capped isolation stage, the single-thread build and the worst-case ledger.

Results. No run at r = @@R@@. The numbers above are bounds; the proof says which part of each is proved, counted or assumed.

Next steps. A cheaper powering schedule lowers the bound directly; a measurement of the good-centre fraction at r = 6 (the executed run is under way) would be the first full-scale data point on the premise from a run with centres other than 1 and 2.
