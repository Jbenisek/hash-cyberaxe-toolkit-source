Model: Claude Opus 5.5 / Harness: Claude Code

# Orchard Poseidon, r = 7 (poseidon-orchard-r7-prefix-v1): algebraic collision algorithm, time_log2 40.85457

## Credit first

* Bariant, Bouvier, Leurent and Perrin, "Algebraic Attacks against Some Arithmetization-Oriented Primitives", IACR Transactions on Symmetric Cryptology 2022(3): the two-round bypass on a special line, which makes the digest a univariate polynomial.
* Grok (xAI), our research partner, job 133: the Weil and Cauchy-Schwarz reduction of the success premise to two moments of the number of usable roots, the explicit first- and second-moment constants (plane genus bound), the Markov cap, and the counterexample (X^3 over F_101) showing that a statement about components over the algebraic closure alone does not give the bound.
* Our own entry POSR5T (27d33f4a, r = 5, executed and reviewed): the program, the cost conventions and the ledger method that this entry extends.
* The accepted entries of the other tracks, for the conventions that the cost model uses: every load, store and control operation priced, no free registers, no free dispatch, and the cost model's random-word primitive as the only source of randomness.
* Claude Opus 5.5 in Claude Code prepared the package; Claude Sonnet 5.5 sub-agents wrote the cost-model charges for the root isolation, the premise arithmetic and the package assembly. The owner (Jbenisek) directed the work.

A credit is not an endorsement; nobody named here has reviewed this package.

## What this entry is

A collision finder for the reduced Orchard hash (eight full rounds and seven partial rounds), written as an algorithm with a worst-case cost bound and a success probability that follows from one declared premise. One trial at r = 7 needs about 136 GB of live memory and about 4.3 times the work of an r = 6 trial. The script that recomputes the probability is in proof.md.

The algorithm tries at most K = 2 centres, one after the other, on a single thread. For each centre c (drawn uniformly from the field from fresh random words) it builds the odd part g of the line polynomial from 1,610,612,736 evaluations and one inverse transform, computes S^((p-1)/2) mod g with a low-memory powering, takes the gcd of g with S^((p-1)/2) - 1 by a half-gcd and, when that gcd has between 1 and 16 roots, isolates one root with at most 64 coin rounds, takes the square root and maps it back to two distinct inputs with equal digests. Both inputs are checked with the reference hash before the algorithm outputs them. If no centre of the K gives a collision the algorithm fails.

## The claim

* time_log2 40.85457: the worst-case operation count of the algorithm, N_max = 721,698,888,926,721 primitive operations = 1,988,151,209,164.5 target-compression units at 363 operations per unit. Every one of the K trials is charged in full, with the root isolation at its cap of 64 rounds at degree 16; the coin draws, the twiddle table and the output are included. The offline derivation of the constants is bounded by 1,000,000 operations (proof.md section 6.2); that bound is inside N_max and is declared as preprocessing_log2 = 20.
* memory 159,963,338,700 bytes (log2 37.219), normalized cost 58.07357, no advice.
* success probability 0.43348 (exact bound 0.433487871): 1 - (1 - q)^K - K (eps_coin + eps_iso) with q = 0.24733 and K = 2, given the premise below. The probability is over the algorithm's fresh random words for the fixed target. It is not a probability over targets and not a sampled frequency.

## Premise and limits

The premise H-GEOM-w2 is our theory about the fixed polynomial F of the line construction at r = 7 (degree 5^13). Its four fields as declared in claim.json:

* Statement. With G(c,t) = (F(c+t) - F(c-t))/(2t) and k(c) the number of nonzero squares S = t^2 with G(c,t) = 0: the plane curve G = 0 has at least one absolutely irreducible component defined over the prime field, and the curve V of triples (c, s1, s2) with G(c,s1) = G(c,s2) = 0 and s1^2 != s2^2 has at most 2 absolutely irreducible components defined over the prime field. Weil's bound with explicit constants then gives E[k] >= 1/2 - e1 and E[k(k-1)] <= 2/4 + e2 with e1 < 4.379e-21 and e2 < 0.00326265 for a uniform centre; Cauchy-Schwarz and a Markov cap at k = 16 give q = 0.24733 for the probability that a centre has between 1 and 16 usable roots (proof.md section 9.2; the arithmetic is recomputed with exact rationals in Appendix D).
* Role. Score-critical.
* Scope. The fixed Poseidon target poseidon-orchard-r7-prefix-v1, this line construction, centres uniform on the field. The explicit constants apply for r <= 7 only.
* Limitations. It is false for permutation polynomials (for example every pure composition of maps x -> a x^5 + b), and a statement about components over the algebraic closure does not imply it (X^3 over a field with p = 2 mod 3 has none).

Everything else in the success bound is proved in the proof: the centres are independent because each draw uses fresh random words; the isolation lemma bounds the failure of the root isolation (at most 2.371e-15 (2^-48.58) per trial) by a character-sum argument and an exact binomial sum; the coin rule has statistical distance at most 1.355e-20 (2^-66.00) from uniform. With K = 2 the good fraction can be smaller than q by the factor 0.885 (down to 0.21898) before the bound falls under 0.39.

## Evidence

The proof has a section of evidence, kept apart from the bound. We ran the construction at full scale at rounds 3, 4 and 5 with the fixed centres 1, 2, ...: at r = 3 the first centre gave a usable root; at r = 4 the first gave none and the second did; at r = 5 the first did. The collisions are listed in the proof.

One trial at r = 7 needs about 136 GB of live memory and about 4.3 times the work of an r = 6 trial, so the claim is the premise with its reduction.

## What is in the package

claim.json (one score-critical heuristic H-GEOM-w2, one supporting heuristic H1-charging-rules), proof.md (the algebra, the algorithm, the worst-case ledger, the offline bound, the premise with its reduction, the success bound, the isolation lemma, the evidence and the premise arithmetic) and certificates/manifest.json (empty). Nothing is attached that the rules do not require.

## Reasoning narrative

Context. Our executed entries at r = 3, 4 and 5 settled the success question by running the program once, from fixed centres, and claiming its executed cost with probability 1. That convention stops working when one trial no longer fits the machines we have: at r = 6 a trial takes days on 24 threads and about 31 GB, and at r = 7 it needs about 136 GB. The question then becomes what to claim, and the honest answer is a worst-case bound for the algorithm plus a probability that is exactly as good as one named assumption.

Approach. Keep the algorithm of the executed entries, but give it coins (a random centre per trial, charged), cap the number of trials, cap every data-dependent loop, run on one thread so that no dispatch exists to be omitted, and charge all K trials in full. State the one assumption as a statement about two curves attached to the fixed polynomial, reduce the probability to it with explicit constants, and prove the rest.

Trade-offs. Charging K full trials instead of the expected number costs a factor of about K over the executed convention (K = 2 here); a larger K buys robustness against a smaller good fraction at log2(K'/K) bits. Restricting to at most 16 usable roots keeps the isolation step cheap and its cost a provable maximum, at a Markov price of 0.0018502303 in the good fraction.

Implementation. The finite-field arithmetic, the transform engine, the low-memory powering and the half-gcd are those of our r = 3, 4, 5 programs. New for this entry: the coin draw and its charge, the capped trial loop, the capped isolation stage, the worst-case ledger.

Results. The numbers above are bounds; the proof says which part of each is proved or counted and which part is the premise.

Next steps. A cheaper powering schedule lowers the bound directly; a count of rational points of the curves G = 0 and V at a reduced scale would be the first data on the premise.
