Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): known method, exact finite ledger, low memory.

Method (not new): on a line in the (nk, rho) input plane the first two full rounds cost no degree, so the digest is a polynomial F(W) of degree 5^7 = 78125.
For a random centre c, the odd part of F(c+s) - F(c-s) is a polynomial g in S = s^2 of degree 39062; each nonzero square root S of g gives the collision W = c +- sqrt(S).
g is built by 98,304 line evaluations (charged as target-compression units) and one inverse NTT of size 49,152; S^((p-1)/2) mod g is computed with an in-place
NTT schedule that stores no spectra (row-wise operand transforms); gcd(g, S^((p-1)/2) - 1) by half-gcd; root splitting, sqrt, back-map and two reference hashes.

Numbers: time_log2 25.837 (worst-case budget of at most two independent centres; one centre: 24.838), memory 8,636,079 bytes (log2 23.042), normalized cost 28.879, claimed success probability 0.60
(0.632 under the Poisson root-count heuristic H1, which is the one score-critical heuristic). 16 verified collisions of the target are included as certificates.

What is not shown: the instrumented C source is not shipped (candidate files are limited to declared Python experiments); its executed code is quoted in proof.md section 10.
No Python experiment is declared because the organizer's experiment runner sizes the digest with digest(b"") and the Orchard digest rejects the empty message.

Ledger (primitive operations, C(1) = 237; full table and rules in proof.md sections 4 and 6):

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table `rho^j` (16384 entries), roots of unity (once per run) | 17,359 | 20,480 | 37,839 | no |
| line setup (constants of the line, 1 inversion) | 391 | 1,564 | 1,955 | no |
| random centre | 0 | 3 | 3 | no |
| B: 98304 line evaluations (units) + inverse NTT 49152 + normalisation | 1,436,260 | 24,567,311 | 26,003,571 | no |
| C: S^((p-1)/2) mod g (lean schedule) | 3,536,772,927 | 2,704,810,640 | 6,241,583,567 | no |
| D: gcd(g, R-1) (half-gcd), as observed in this run (includes the scan for the degree of R-1, 78,126 ops) | 355,770,866 | 434,514,508 | 790,285,374 | yes: budget 800,000,000 |
| E: root finding (deg G <= 8), at most 40 shifts per centre | - | - | 5 (one root) to 761,102 (320 planted tests, d <= 8) | yes: budget 10,000,000 in total |
| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | about 18,300 observed | allowance 200,000 for two executions |

Worst case for two centres: init + 2 x (line + random + B + C + D budget + D gap bound + scan) + E budget + E gap bound + F,G allowance = 37,839 + 2 x 7,095,689,096 + 10,000,000 + 1,000,000 + 200,000 = 14,202,616,031 operations = 59,926,649.9 units.

Memory: text 91,703 + data 768 + bss 5,336 = 97,807 bytes plus heap peak 8,468,640, stack bound 65,536 B, allocator slack 4,096 B.

Heuristics declared in claim.json: H1 (score-critical): root count of the odd-part polynomial is Poisson(1/2) (one centre 0.3935, two centres 0.632; claimed 0.60); H2 (supporting): the charging rules describe the executed program; H3 (supporting): the half-gcd stage stays within its implemented budget.

Campaign: 65 complete single-centre executions at the target, 28 successes (rate 0.431, Wilson 95% [0.318, 0.552]); every success verified by a big-integer reference and the organizer's hash; root-count histogram 0 roots: 37, 1 root: 20, 2 roots: 7, 3 roots: 1.

Limits: the C source is not shipped; the per-element address arithmetic is assumed free (specialised pass kernels with constant strides) and registers are charged as 16-element blocks; the success claim rests on H1 and not on the sample.

Implemented halts (all enforced in the executed program; a check adds 2 control operations to the ledger): at most 2 centres; `deg G <= 8` (otherwise the centre is abandoned);
stage D is checked at every entry of the half-gcd recursion, after every matrix application and matrix product, in every iteration of the classical base case and at the end of the stage, and stops the program as soon as the work charged since the stage began exceeds
800,000,000 operations; the largest charged work between two consecutive checks seen in the ledger runs is 21,617,616 operations, and the bound used below is 28,000,000;
stage E (all shifts of the whole run together) is checked before every shift (at most 40 shifts per centre) and stops the program when more than 10,000,000 operations have been charged in total; one shift costs at most 1,000,000 operations (the whole
root finder cost at most 761,102 in 320 planted tests with `d <= 8`). A halt is a failure of the whole run and is included in the probability argument (section 8).


| item | elements | bytes |
|---|---:|---:|
| twiddle table `rho^j`, `j < 2^14` | 16384 | 524288 |
| `Y` (transform buffer, `3 * 2^15`) | 98304 | 3145728 |
| `tmp` (one transform row, `2^15`) | 32768 | 1048576 |
| `MU` | 39061 | 1249952 |
| `g` | 39063 | 1250016 |
| `F` (fold / result) | 39062 | 1249984 |
| scalars, line constants, plans | | 96 |
| tracked heap peak | | 8,468,640 |


