Orchard Poseidon, r = 2 (poseidon-orchard-r2-prefix-v1): two families of inputs, a success probability that is a theorem, exact finite ledger, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and two partial rounds) whose chance of success per run is proved by a counting argument and a character-sum bound, not measured.
An earlier entry of ours relied on a sampled success rate; this one does not use any sample for its probability.

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree:
   its S-box output is affine in one parameter W. The digest is then a univariate polynomial f(W) of degree 5^8 = 390625. We use two such lines (two choices of the constant coordinate). Each line contains exactly p inputs (one for each W in F_p), and the two lines meet in exactly one input.
   So the union has 2p - 1 inputs.
2. Counting. The digest takes at most p values. At most p - 1 of the 2p - 1 inputs can be the only input with their digest (if p of them were isolated they would use up every value and nothing else could exist). So an input drawn uniformly from the union shares its digest with another input of the union with probability at least p/(2p - 1), which is above one half.
   This holds whatever the polynomials look like.
3. The program draws a uniform input x of the union (a rejection sampler on 256-bit words, at most 128 words; the common input is counted once), computes y = digest(x), builds f_0 - y and f_1 - y by evaluating the digest at 393,216 points of each line and one inverse transform,
   computes W^p mod (f - y) with a low-memory transform schedule, and takes the gcd with W^p - W (classical Euclid). The result is the product of the linear factors for all roots in the field: all inputs of that line with digest y.
   The roots that are x itself are divided out; if something is left, one root is isolated and mapped back to a second input with the same digest.
4. Root isolation is a Cantor-Zassenhaus procedure with a bounded number of tries per level. Its failure probability is bounded with a Weil bound for quadratic-character sums (proof.md, Lemma B): a level of degree d fails with probability at most (2^(1-d) + 2^-100)^t, and with t = ceil(40/(d-1)) tries (one try above degree 40) every level fails with probability below 2^-39.99. At most 17 levels occur, because each level halves the degree. The total is below 2^-35.
5. Success probability: at least p/(2p-1) times (1 - 2^-35) minus 2^-127 for the sampler, which exceeds 0.4999999999. The claim is 0.4999999999. It uses independent uniform random words as the model primitive (as the cost model has), and nothing else.

Numbers. time_log2 34.917 (the worst case of one attempt: both lines run to the end, family 1 isolates a root at the worst degrees), memory 75,409,855 bytes (log2 26.169), normalized cost 41.086, success probability 0.4999999999.
Total charge of the worst case 8,368,466,696,052 primitive operations = 32,435,917,426.6 target-compression units (258 primitive operations per unit). A run that finds its root in the first family charges about 2,251,251,203,596 operations; a run through both families without a partner, about 4,502,501,275,879.
2 verified collisions found by this program are included as certificates, each from a separate attempt.

Where the charge comes from (primitive operations, rules in proof.md section 6):
| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table (once) | 132,044 | 929,236 | 1,061,280 | no |
| setup: two lines, the common input I | 1,131 | 12,489 | 13,620 | no |
| A: sampler (128 words) and `y = H(x)`, family 1 | - | - | 5,170 (logged runs: 471, 545) | enumerated |
| driver: 31 per family, 6 (isolation call), 9 (end) | - | - | 77 | enumerated |
| B (per family): 393216 evaluations (units) + inverse NTT 393216 + normalisation | 11,463,423 | 268,227,364 | 279,690,787 | no |
| C (per family): `W^p mod F` (m = 390625) | 34,086,292,492 | 384,765,364,145 | 418,851,656,637 | no |
| D (per family): classical gcd, derived bound for (390625, 390624) | - | - | 1,833,164,065,176 (charged in the run: 1,832,118,752,685) | yes: bound |
| E (per family): copy of G and two deflations at d = 390625 | - | - | 11,328,133 | linear in d |
| F: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | 3,863,852,106,495 | yes: bound |
| map back, two reference hashes, comparisons (success path) | - | - | 27,944 (22,740 + 5,160 + 44) | no |

Why the worst case is large. The probability claim has to hold for every value of the digest, including a value that has very many preimages on a line. Then the product of roots has a large degree, and isolating a root costs a number of modular powerings of that degree.
We charge that case, level by level, at derived bounds although it was never observed; the observed runs isolate a root of degree 1 or 2 at a cost of at most about 29,000 operations. The classical gcd is charged at its derived worst case (a normal remainder sequence, about the square of the degree),
which is what it costs in practice for this input up to a few percent, so that bound is close to the observed charge.

What was run and what was derived.
* Run end to end: the main attempt (sampler, two lines, evaluation and interpolation, powering, gcd, deflation, root isolation, back-map, two reference hashes); the certificates are its outputs.
* Run at the sizes of the worst case: the Taylor shift and the powering with exponent (p-1)/2 at every degree of the level schedule (390625, 195312, ... 5) and at every degree from 3 to 47, by a calibration program; their charge does not depend on the coefficients.
* Run on synthetic inputs: the whole root-isolation stage on products of random linear factors of degree up to 3000, with the program asserting its own gcd and division charges against the derived bounds.
* Derived: the bounds for the gcd and the division (closed forms in proof.md sections 7 and 11), the count of levels and tries, the failure probabilities.
* Assumed: the charging rules of proof.md section 6 describe the program; the charge of a step of the shift and of the powering is nondecreasing in the degree and halves when the degree halves (structure of the code, proof.md section 7), which turns the measured charge at the largest degree of a level into a bound for every smaller degree.

Memory. The largest live set is the powering at degree 390625: the transform buffer (3 x 2^18 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table; tracked peak 75,248,736 bytes, plus the static image (91,487 bytes), a stack bound of 65,536 bytes and 4,096 bytes of allocator metadata.

Reasoning narrative.
Context. The previous filing of this family computed the roots of an odd-part polynomial for a random centre on one line and rested its probability on a measured success rate; that is not a bound.
Approach. Replace the random centre by a uniform point of a set larger than the digest range, so that the existence of a partner is a counting fact. That needs a set of 2p - 1 inputs on which the digest is cheap to evaluate as a polynomial in one variable: two lines do.
Trade-offs. The polynomial now has degree 390625 instead of 195312 (no odd-part halving), so the powering is about 2.4 times larger and there are two of them; in exchange the success probability is a theorem. Classical Euclid replaces the half-gcd because its worst case is a closed form.
Implementation. Reused: the finite-field code, the transform engine and the low-memory powering of the earlier entry; new: the two-line setup and their common input, the sampler, the classical gcd with its derived charge, the deflation, the Taylor shift, the root isolation and its tests.
Results. The attempts that were run found collisions; the stage charges agree with the derived bounds (the program asserts this).
Caveats. The organizer did not run the program, so the counts rest on the shipped source; the one structural assumption is a sixteen-word register file per transform block; the worst-case root isolation is charged at a derived bound and not observed.
Next steps. The half-gcd with a derived worst case would cut the gcd charge; a sharper handling of values with very many preimages would cut the root-isolation bound, which is the largest term.

Worst case sum: init + setup + sampler + 2 x (driver + B + C + D bound + E) + isolation call + end + F + final = 1,061,280 + 13,620 + 5,170 + 2 x (31 + 279,690,787 + 418,851,656,637 + 1,833,164,065,176 + 11,328,133) + 6 + 9 + 3,863,852,106,495 + 27,944 = 8,368,466,696,052 operations.

Root isolation (stage F) worst case by level:

| d | tries t(d) | shift(d) | pow(d) measured | pow bound used | gcd bound | div bound | level charge |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 390,625 | 1 | 945,095,972 | 417,085,021,140 | 421,508,848,240 | 1,833,164,065,176 | 457,773,635,501 | 2,713,391,644,919 |
| 195,312 | 1 | 465,518,508 | 201,242,989,680 | 203,388,631,698 | 458,816,015,604 | 114,445,315,175 | 777,115,481,015 |
| 97,656 | 1 | 210,033,853 | 91,649,201,665 | 92,644,184,295 | 114,967,677,108 | 28,612,575,923 | 236,434,471,209 |
| 48,828 | 1 | 103,521,148 | 45,255,721,491 | 45,747,472,249 | 28,873,756,884 | 7,153,768,553 | 81,878,518,864 |
| 24,414 | 1 | 51,059,427 | 22,324,959,602 | 22,567,848,970 | 7,284,359,028 | 1,788,755,432 | 31,692,022,887 |
| 12,207 | 1 | 25,094,814 | 10,689,139,158 | 10,806,443,492 | 1,854,050,664 | 447,346,514 | 13,132,935,514 |
| 6,103 | 1 | 11,131,252 | 4,769,703,145 | 4,823,490,575 | 479,918,184 | 111,898,142 | 5,426,438,183 |
| 3,051 | 1 | 5,476,364 | 2,346,482,537 | 2,373,017,829 | 128,181,288 | 28,006,292 | 2,534,681,803 |
| 1,525 | 1 | 2,698,600 | 1,152,972,826 | 1,166,054,280 | 36,145,176 | 7,018,451 | 1,211,916,537 |
| 762 | 1 | 1,326,356 | 545,955,029 | 552,237,183 | 11,085,204 | 1,764,050 | 566,412,823 |
| 381 | 1 | 578,871 | 236,231,146 | 239,069,164 | 3,802,008 | 447,887 | 243,897,960 |
| 190 | 1 | 288,009 | 115,645,908 | 117,042,636 | 1,461,876 | 115,832 | 118,908,383 |
| 95 | 1 | 145,800 | 56,567,709 | 57,255,701 | 623,976 | 32,186 | 58,057,693 |
| 47 | 1 | 71,028 | 26,402,250 | 26,402,250 | 282,984 | 10,514 | 28,738,804 |
| 23 | 2 | 13,507 | 4,621,507 | 4,621,507 | 133,224 | 4,862 | 10,849,750 |
| 11 | 4 | 7,678 | 1,043,407 | 1,043,407 | 63,528 | 3,332 | 4,631,179 |
| 5 | 10 | 6,055 | 210,697 | 210,697 | 29,976 | 2,891 | 2,470,318 |
| quadratic end (d = 2) | | | | | | | 28,654 |
| total (30 tries) | | | | | | | 3,863,852,106,495 |
