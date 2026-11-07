Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): known method, exact finite ledger, low memory, complete source in the proof.

Method (not new): on a line in the (nk, rho) input plane the first two full rounds cost no degree, so the digest is a polynomial F(W) of degree 5^7 = 78125.
For a random centre c, the odd part of F(c+s) - F(c-s) is a polynomial g in S = s^2 of degree 39062; each nonzero square root S of g gives the collision W = c +- sqrt(S).
g is built by 98,304 line evaluations (charged as target-compression units) and one inverse NTT of size 49,152; S^((p-1)/2) mod g is computed with an in-place
NTT schedule that stores no spectra (row-wise operand transforms); gcd(g, S^((p-1)/2) - 1) by half-gcd; root splitting, sqrt, back-map and two reference hashes.

Numbers: time_log2 28.781 (worst-case of at most two independent centres with the full half-gcd budget charged for each; one centre: 27.781), memory 8,638,495 bytes (log2 23.043), normalized cost 31.824,
claimed success probability 0.53 (per-centre sample rate lower bound 0.318, two centres: 1 - (1 - 0.318)^2 = 0.534). 16 verified collisions of the target are included as certificates.

The complete C source of the instrumented program is in proof.md section 10; its counting rules are in proof.md section 4.1.
No Python experiment is declared because the organizer's experiment runner sizes the digest with digest(b"") and the Orchard digest rejects the empty message.

Ledger (primitive operations, C(1) = 237; full table and rules in proof.md sections 4 and 6):

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table `rho^j` (16384 entries), roots of unity (once per run) | 17,359 | 126,238 | 143,597 | no |
| line setup (constants of the line, 1 inversion) | 391 | 3,519 | 3,910 | no |
| random centre | 0 | 3 | 3 | no |
| B: 98304 line evaluations (units) + inverse NTT 49152 + normalisation | 1,436,260 | 41,901,929 | 43,338,189 | no |
| C: S^((p-1)/2) mod g (lean schedule) | 3,536,772,927 | 42,022,748,610 | 45,559,521,537 | no |
| D: gcd(g, R-1) (half-gcd), as observed in this run (includes the scan for the degree of R-1) | 355,770,866 | 5,494,709,464 | 5,850,480,330 | yes: budget 8,800,000,000 |
| E: root finding (deg G <= 8), at most 40 shifts per centre | - | - | 12 in the ledger run, at most 1,541,920 in 320 planted tests | yes: budget 10,000,000 in total |
| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | 36,680 observed | allowance 200,000 for two executions |

Worst case for two centres: init + 2 x (line + random + B + C + D budget + D gap bound + scan) + E budget + E gap bound + F,G allowance = 143,597 + 2 x 54,617,263,639 + 10,000,000 + 2,500,000 + 200,000 = 109,247,370,875 operations = 460,959,370.8 units.

Memory: text 94,119 + data 768 + bss 5,336 = 100,223 bytes plus heap peak 8,468,640, stack bound 65,536 B, allocator slack 4,096 B.

Heuristics declared in claim.json: H1 (score-critical): the per-centre success rate is at least the Wilson lower bound 0.318 of the target sample (28 of 65); H2 (supporting): the charging rules describe the executed program; H3 (supporting): the half-gcd stage stays within its implemented budget.

Limits: the counts are produced by the instrumentation in the source of proof.md section 10, which the organizer did not run; the register file of 16 words per transform block is the one structural assumption; the success claim rests on the lower end of a 95% interval of the sample.

Implemented halts (all enforced in the executed program; a check adds 2 control operations to the ledger): at most 2 centres; `deg G <= 8` (otherwise the centre is abandoned);
stage D is checked at every entry of the half-gcd recursion, after every matrix application and matrix product, in every iteration of the classical base case and at the end of the stage, and stops the program as soon as the work charged since the stage began exceeds
8,800,000,000 operations; the largest charged work between two consecutive checks seen in the ledger runs is 170,599,074 operations, and the bound used below is 214,000,000;
stage E (all shifts of the whole run together) is checked before every shift (at most 40 shifts per centre) and stops the program when more than 10,000,000 operations have been charged in total; one shift costs at most 2,500,000 operations (the whole
root finder cost at most 1,541,920 in 320 planted tests with `d <= 8`). A halt is a failure of the whole run and is included in the probability argument (section 8).


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


Reasoning narrative (context, approach, implementation, results, caveats, next steps):

Goal. Produce an ordinary collision of the reduced Orchard Poseidon permutation at one partial round plus the eight fixed full rounds, with an exact finite operation ledger and a low memory footprint, scored as time_log2 + max(0, log2 bytes - 20).

Environment and baseline. The target profile is poseidon-orchard-r1-prefix-v1 over the Pallas base field (t = 3, x^5, Cauchy MDS, state [nk, rho, 2^65], digest lane 0). The method is the standard two-free-round line of Bariant, Bouvier, Leurent and Perrin (ToSC 2022): on a line in the input plane the first two full rounds contribute no degree, so the digest restricted to the line is univariate of degree 5^7, and collisions reduce to root finding on its odd part of degree 39062 via S^((p-1)/2) - 1.

Approach and tradeoffs. Root finding is done with an in-place transform schedule that stores no spectra, trading a few percent of operations for a smaller memory peak, because the memory term is charged in bits above 2^20. The half-gcd recovers the roots. A single degree-8 remainder is split, square-rooted and mapped back, then verified by two independent reference hashes.

Implementation and files. The instrumented C program is reproduced in full in proof.md section 10 (fourteen files). Every primitive operation is counted by the program itself, including loop index updates, comparisons, branches and address calculations; the counting rules and a quoted butterfly loop are in proof.md section 4.1. Sixteen verified collisions of the real target are included as certificates.

Course corrections. An earlier version of this entry charged loop control coarsely, as a fixed number of operations per block. That understated the work the shown code performs. The ledger here charges every executed control operation, which raised the operation total by a factor of about 7.3 and the time score accordingly; control operations now dominate the count. The success probability was also moved off a distributional model and onto the lower end of a confidence interval of the measured sample.

Measured results. Over 65 single-centre runs at the real target, 28 succeeded; the 95% lower bound on the per-centre rate is 0.318, so two independent centres give at least 0.534, claimed as 0.53. The worst-case two-centre ledger charges the full half-gcd budget for both centres and the full root-finder budget once.

Caveats. The organizer did not execute the program, so the counts rest on the shipped source; the one structural assumption is a sixteen-word register file per transform block; no Python experiment is declared because the organizer runner sizes the digest with the empty message, which the Orchard digest rejects.

Next steps. A straight-line, constant-stride kernel in place of the generic loops would cut the control-operation share several-fold; that is a separate future entry because it is new code that must be shipped and measured.
