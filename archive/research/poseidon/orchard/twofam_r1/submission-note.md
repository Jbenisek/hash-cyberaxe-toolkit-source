Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): two families of inputs, a success probability that is a theorem, exact finite ledger, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and one partial round) whose chance of success per run is proved by a counting argument and a character-sum bound, not measured.
An earlier entry of ours relied on a sampled success rate; this one does not use any sample for its probability.

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree:
   its S-box output is affine in one parameter W. The digest is then a univariate polynomial f(W) of degree 5^7 = 78125. We use two such lines (two choices of the constant coordinate). Each line contains exactly p inputs (one for each W in F_p), and the two lines meet in exactly one input.
   So the union has 2p - 1 inputs.
2. Counting. The digest takes at most p values. At most p - 1 of the 2p - 1 inputs can be the only input with their digest (if p of them were isolated they would use up every value and nothing else could exist). So an input drawn uniformly from the union shares its digest with another input of the union with probability at least p/(2p - 1), which is above one half.
   This holds whatever the polynomials look like.
3. The program draws a uniform input x of the union (a rejection sampler on 256-bit words, at most 128 words; the common input is counted once), computes y = digest(x), builds f_0 - y and f_1 - y by evaluating the digest at 98,304 points of each line and one inverse transform,
   computes W^p mod (f - y) with a low-memory transform schedule, and takes the gcd with W^p - W (classical Euclid). The result is the product of the linear factors for all roots in the field: all inputs of that line with digest y.
   The roots that are x itself are divided out; if something is left, one root is isolated and mapped back to a second input with the same digest.
4. Root isolation is a Cantor-Zassenhaus procedure with a bounded number of tries per level. Its failure probability is bounded with a Weil bound for quadratic-character sums (proof.md, Lemma B): a level of degree d fails with probability at most (2^(1-d) + 2^-100)^t, and with t = ceil(40/(d-1)) tries (one try above degree 40) every level fails with probability below 2^-39.99. At most 15 levels occur, because each level halves the degree. The total is below 2^-36.
5. Success probability: at least p/(2p-1) times (1 - 2^-36) minus 2^-127 for the sampler, which exceeds 0.4999999999. The claim is 0.4999999999. It uses independent uniform random words as the model primitive (as the cost model has), and nothing else.

Numbers. time_log2 31.331 (the worst case of one attempt: both lines run to the end, family 1 isolates a root at the worst degrees), memory 17,097,311 bytes (log2 24.028), normalized cost 35.359, success probability 0.4999999999.
Total charge of the worst case 640,137,986,844 primitive operations = 2,701,004,163.9 target-compression units (237 primitive operations per unit). A run that finds its root in the first family charges about 166,175,528,585 operations; a run through both families without a partner, about 332,350,650,229.
4 verified collisions found by this program are included as certificates, each from a separate attempt.

Where the charge comes from (primitive operations, rules in proof.md section 6):
| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table (once) | 33,742 | 241,330 | 275,072 | no |
| setup: two lines, the common input I | 1,131 | 12,489 | 13,620 | no |
| A: sampler (at most 128 words) and `y = H(x)` | - | - | 1,900 allowance (observed 279-291) | derived: 128 x 12 + 42 + 237 |
| B (per family): 98304 evaluations (units) + inverse NTT 98304 + normalisation | 2,525,873 | 61,471,246 | 63,997,119 | no |
| C (per family): `W^p mod F` (m = 78125, 238 steps) | 7,533,028,466 | 85,123,176,368 | 92,656,204,834 | no |
| D (per family): classical gcd, derived bound for (78125, 78124) | - | - | 73,664,065,176 (charged in the run: 73,454,999,982) | yes: bound |
| E (per family): copy of G and two deflations at d = 78125 | - | - | 2,265,633 | linear in d |
| F: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | 307,364,430,728 | yes: bound |
| map back and two reference hashes (success path) | - | - | 200,000 allowance (observed 27,480) | no |

Why the worst case is large. The probability claim has to hold for every value of the digest, including a value that has very many preimages on a line. Then the product of roots has a large degree, and isolating a root costs a number of modular powerings of that degree.
We charge that case, level by level, at derived bounds although it was never observed; the observed runs isolate a root of degree 1 or 2 at a cost of at most about 16,000 operations. The classical gcd is charged at its derived worst case (a normal remainder sequence, about the square of the degree),
which is also what it costs in practice for this input, so that bound is within 1 percent of the observed charge.

What was run and what was derived.
* Run end to end: the main attempt (sampler, two lines, evaluation and interpolation, powering, gcd, deflation, root isolation, back-map, two reference hashes); the certificates are its outputs.
* Run at the sizes of the worst case: the Taylor shift and the powering with exponent (p-1)/2 at every degree of the level schedule (78125, 39062, ... 4), by a calibration program; their charge does not depend on the coefficients.
* Run on synthetic inputs: the whole root-isolation stage on products of random linear factors of degree up to 3000, with the program asserting its own gcd and division charges against the derived bounds.
* Derived: the bounds for the gcd and the division (closed forms in proof.md sections 7 and 11), the count of levels and tries, the failure probabilities.
* Assumed: the charging rules of proof.md section 6 describe the program; the cost of a level is at most 1.02 times the cost measured at the largest degree of that level.

Memory. The largest live set is the powering at degree 78125: the transform buffer (3 x 2^16 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table; tracked peak 16,937,184 bytes, plus the static image (90,495 bytes), a stack bound of 65,536 bytes and 4,096 bytes of allocator metadata.

Reasoning narrative.
Context. The previous filing of this family computed the roots of an odd-part polynomial for a random centre on one line and rested its probability on a measured success rate; that is not a bound.
Approach. Replace the random centre by a uniform point of a set larger than the digest range, so that the existence of a partner is a counting fact. That needs a set of 2p - 1 inputs on which the digest is cheap to evaluate as a polynomial in one variable: two lines do.
Trade-offs. The polynomial now has degree 78125 instead of 39062 (no odd-part halving), so the powering is about 2.4 times larger and there are two of them; in exchange the success probability is a theorem. Classical Euclid replaces the half-gcd because its worst case is a closed form.
Implementation. Reused: the finite-field code, the transform engine and the low-memory powering of the earlier entry; new: the two-line setup and their common input, the sampler, the classical gcd with its derived charge, the deflation, the Taylor shift, the root isolation and its tests.
Results. The attempts that were run found collisions; the stage charges agree with the derived bounds (the program asserts this).
Caveats. The organizer did not run the program, so the counts rest on the shipped source; the one structural assumption is a sixteen-word register file per transform block; the worst-case root isolation is charged at a derived bound and not observed.
Next steps. The half-gcd with a derived worst case would cut the gcd charge; a sharper handling of values with very many preimages would cut the root-isolation bound, which is the largest term.

Worst case sum: init + setup + sampler allowance + 2 x (B + C + D bound + E) + F bound + final allowance = 275,072 + 13,620 + 1,900 + 2 x (63,997,119 + 92,656,204,834 + 73,664,065,176 + 2,265,633) + 307,364,430,728 + 200,000 = 640,137,986,844 operations.

Root isolation (stage F) worst case by level:

| d | tries t(d) | shift(d) | pow(d) | gcd bound | div bound | t(d) x (1.02 (shift + pow) + gcd + div + 100) |
|---:|---:|---:|---:|---:|---:|---:|
| 78,125 | 1 | 205,854,187 | 92,268,713,832 | 73,664,065,176 | 18,312,541,751 | 186,300,666,407 |
| 39,062 | 1 | 101,431,198 | 45,566,840,428 | 18,521,015,604 | 4,578,518,297 | 69,681,171,060 |
| 19,531 | 1 | 50,014,440 | 22,481,193,667 | 4,682,989,608 | 1,144,880,612 | 28,809,702,590 |
| 9,765 | 1 | 24,572,201 | 10,767,609,193 | 1,196,996,376 | 286,317,371 | 12,491,338,869 |
| 4,882 | 1 | 10,869,940 | 4,809,106,672 | 312,372,564 | 71,628,947 | 5,300,377,756 |
| 2,441 | 1 | 5,345,826 | 2,366,250,900 | 84,685,848 | 17,940,377 | 2,521,654,986 |
| 1,220 | 1 | 2,633,333 | 1,162,898,377 | 24,451,476 | 4,498,994 | 1,217,792,915 |
| 610 | 1 | 1,293,839 | 550,923,249 | 7,761,876 | 1,134,539 | 572,157,945 |
| 305 | 1 | 562,631 | 238,724,294 | 2,765,976 | 289,541 | 247,128,281 |
| 152 | 1 | 279,902 | 116,896,951 | 1,100,724 | 75,872 | 120,697,087 |
| 76 | 1 | 141,754 | 57,207,270 | 482,388 | 21,950 | 59,000,443 |
| 38 | 2 | 74,440 | 12,680,407 | 225,204 | 7,985 | 26,486,466 |
| 19 | 3 | 11,225 | 3,145,447 | 109,608 | 4,256 | 10,001,310 |
| 9 | 5 | 7,093 | 694,997 | 52,248 | 3,161 | 3,858,205 |
| 4 | 14 | 5,926 | 133,897 | 24,468 | 2,834 | 2,380,308 |
| quadratic end (d = 2) and level control | | | | | | 16,100 |
| total | 35 | | | | | 307,364,430,728 |
