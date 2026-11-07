[DRAFT: remove this line when section 8 of proof.md (success probability) is complete; the claimed probability is provisional until then.]

Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): one centre of the odd-part method on a line, a half-gcd with a derived worst case, root isolation with a proved failure bound, exact finite ledger, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and one partial round) that makes exactly one attempt: one random centre. A per-centre success probability of about 0.39 is enough for a single attempt to be a useful entry, because the cost of one attempt is already below the cost of the two-attempt programs that were needed when the rate was only measured.

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree:
   its S-box output is affine in one parameter W. The digest is then a univariate polynomial F(W) of degree 5^7 = 78125. The line contains exactly p inputs (one for each W in F_p).
2. For a centre c, write F(c + s) - F(c - s) = 2 s g(s^2). The polynomial g has degree 39062 and a leading coefficient that does not depend on c. A root S of g that is a nonzero square gives s = sqrt(S) and two different inputs W1 = c + s and W2 = c - s with the same digest.
3. The program evaluates the digest at 98,304 points (each charged as one full target compression, 237 operations), interpolates g with one inverse transform, computes S^((p-1)/2) mod g with a low-memory transform schedule, and takes gcd(g, S^((p-1)/2) - 1) with a half-gcd.
   The result G is the product of the linear factors of g whose roots are nonzero squares. If G is constant the attempt has no useful root and ends. Otherwise one root of G is isolated by random shifts and quadratic-character splitting, S is square-rooted, and the two inputs are computed and checked with the reference hash.
4. Root isolation is a Cantor-Zassenhaus procedure with a bounded number of tries per level. Its failure probability is bounded with a Weil bound for quadratic-character sums (proof.md, Lemma B): a level of degree d fails with probability at most (2^(1-d) + 2^-100)^t, and with t = ceil(40/(d-1)) tries (one try above degree 40) every level fails with probability below 2^-39.99.
   At most 14 levels occur, because each level halves the degree. The total is below 2^-36.
5. Success probability: it is the probability that g has at least one root that is a nonzero square, times 1 - 2^-36. That probability is proved in section 8 of proof.md (pending at the time of this draft); the claim is 0.3934.

Numbers. time_log2 29.409 (the worst case of one attempt: the half-gcd at its derived bound and the root isolation at the worst degrees), memory 10,526,022 bytes (log2 23.328), normalized cost 32.737, success probability 0.3934 (provisional).
Total charge of the worst case 168,871,420,167 primitive operations = 712,537,637.8 target-compression units (237 primitive operations per unit). A run in which the half-gcd finds no root stops after about 52,002,646,417 operations; a run in which a root is found and isolated charges about 52,002,691,947 operations.
5 verified collisions found by this program are included as certificates, each from a separate attempt.

Where the charge comes from (primitive operations, rules in proof.md section 4.2):
| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table (once) | 17,359 | 126,642 | 144,001 | no |
| setup: the line | 391 | 3,519 | 3,910 | no |
| A: random centre | 0 | 3 | 3 | no |
| B: 98304 evaluations (units) + inverse NTT 49152 + normalisation | 1,436,260 | 41,901,935 | 43,338,195 | no |
| C: `S^((p-1)/2) mod g` (m = 39062, 238 steps) | 3,536,772,927 | 42,030,109,940 | 45,566,882,867 | no |
| D: half-gcd, derived bound for (39062, 39061) plus the degree scan allowance (10 x 39063) | - | - | 11,942,345,981 + 390,630 (charged in the run: 6,392,274,754) | yes: bound |
| E: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | 111,317,914,580 | yes: bound |
| F, G: square root, back-map, two reference hashes (success path) | - | - | 400,000 allowance (observed 48,210) | no |

Why the worst case is larger than a typical run. The probability claim must hold for every centre, including a centre for which g has a very large number of square roots. Then G has a large degree and isolating a root costs a number of modular powerings of that degree.
We charge that case, level by level, at derived bounds although it was never observed; the observed runs end with no root or isolate a root of degree 1 or 2 at a cost of at most about 16,000 operations. The half-gcd is charged at the evaluation of a recursion over its executed kernels at maximal operand lengths (proof.md sections 4.4 and 6), not at the observed charge of the run.

What was run and what was derived.
* Run end to end: the main attempt (line setup, evaluation and interpolation, powering, half-gcd, root isolation, back-map, two reference hashes); the certificates are its outputs. The program asserts its half-gcd charge against the derived bound at every execution.
* Run at the sizes of the worst case: the Taylor shift and the powering with exponent (p-1)/2 at every degree of the level schedule (39062, 19531, ... 4), by a calibration program; their charge does not depend on the coefficients.
* Run on synthetic inputs: the half-gcd against classical Euclid on planted gcds with normal and abnormal remainder sequences, and the whole root-isolation stage on products of random linear factors, with the program asserting its own gcd and division charges against the derived bounds.
* Derived: the bounds for the half-gcd and the division (a recursion over the control structure of the executed code, proof.md sections 4.4 and 6), the count of levels and tries, the failure probabilities.
* Assumed: the charging rules of proof.md section 4.2 describe the program; the cost of a level is at most 1.02 times the cost measured at the largest degree of that level.

Memory. The largest live set is the half-gcd stage at degree 39062 (two inputs, the matrices and the transform rows) and the powering at the same degree: the transform buffer (3 x 2^15 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table; tracked peak 10,353,984 bytes, plus the static image (102,406 bytes), a stack bound of 65,536 bytes and 4,096 bytes of allocator metadata.

Reasoning narrative.
Context. Earlier entries of this family either used two centres (so that a measured rate was needed) or a classical gcd with a larger worst case. A proved per-centre rate of about 0.39 makes one centre enough.
Approach. Make one attempt, and make everything in it either an executed count or a derived bound: the half-gcd, the division and the root isolation are charged at bounds that the program checks against its own counters.
Trade-offs. A single centre has a smaller success probability than two, in exchange for roughly half the time of the two-centre program. The derived worst case of the half-gcd is about twice its observed charge; a tighter derivation would lower the claimed time slightly.
Implementation. Reused: the finite-field code, the transform engine, the low-memory powering and the root isolation of earlier entries; new: the fast division for long quotients, the half-gcd that gives up its inputs, the recursion that derives its worst-case charge, and the single-attempt driver.
Results. The attempts that were run found collisions; the stage charges agree with the derived bounds (the program asserts this).
Caveats. The organizer did not run the program, so the counts rest on the shipped source; the one structural assumption is a sixteen-word register file per transform block; the worst-case root isolation is charged at a derived bound and not observed; the success-probability proof is the section of the proof that was still open when this note was drafted.
Next steps. A sharper handling of centres with very many square roots would cut the root-isolation bound, which is the largest term of the worst case; a half-gcd with cached spectra would cut the typical charge at a cost in memory.

Worst case sum: init + setup + A + B + C + D bound + scan + E bound + final allowance = 144,001 + 3,910 + 3 + 43,338,195 + 45,566,882,867 + 11,942,345,981 + 390,630 + 111,317,914,580 + 400,000 = 168,871,420,167 operations.

Root isolation (stage E) worst case by level:

| d | tries t(d) | shift(d) | pow(d) | gcd bound | div bound | t(d) x (1.02 (shift + pow) + gcd + div + 100) |
|---:|---:|---:|---:|---:|---:|---:|
| 39,062 | 1 | 101,431,198 | 45,566,840,428 | 12,181,192,901 | 256,881,730 | 59,019,711,790 |
| 19,531 | 1 | 50,014,440 | 22,481,193,667 | 5,080,504,035 | 123,518,384 | 28,185,854,789 |
| 9,765 | 1 | 24,572,201 | 10,767,609,193 | 2,088,683,126 | 56,782,138 | 13,153,490,386 |
| 4,882 | 1 | 10,869,940 | 4,809,106,672 | 842,985,017 | 27,681,761 | 5,787,043,023 |
| 2,441 | 1 | 5,345,826 | 2,366,250,900 | 329,787,572 | 13,309,481 | 2,762,125,814 |
| 1,220 | 1 | 2,633,333 | 1,162,898,377 | 123,244,676 | 6,314,071 | 1,318,401,192 |
| 610 | 1 | 1,293,839 | 550,923,249 | 43,140,639 | 2,811,730 | 609,213,899 |
| 305 | 1 | 562,631 | 238,724,294 | 13,740,037 | 1,326,324 | 259,139,125 |
| 152 | 1 | 279,902 | 116,896,951 | 1,100,724 | 570,515 | 121,191,730 |
| 76 | 1 | 141,754 | 57,207,270 | 482,388 | 21,950 | 59,000,443 |
| 38 | 2 | 74,440 | 12,680,407 | 225,204 | 7,985 | 26,486,466 |
| 19 | 3 | 11,225 | 3,145,447 | 109,608 | 4,256 | 10,001,310 |
| 9 | 5 | 7,093 | 694,997 | 52,248 | 3,161 | 3,858,205 |
| 4 | 14 | 5,926 | 133,897 | 24,468 | 2,834 | 2,380,308 |
| quadratic end (d = 2) and level control | | | | | | 16,100 |
| total | 34 | | | | | 111,317,914,580 |
