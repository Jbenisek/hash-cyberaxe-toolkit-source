Orchard Poseidon, r = 2 (poseidon-orchard-r2-prefix-v1): known method, finite ledger from the shipped source, low memory.

Method (not new). On a line in the (nk, rho) input plane the first two full rounds cost no degree, so the digest is a polynomial F(W) of degree 5^8 = 390625.
For a random centre c, the odd part of F(c+s) - F(c-s) is a polynomial g in S = s^2 of degree 195312; each nonzero square root S of g gives the collision W = c +- sqrt(S).
g is built by 393,216 line evaluations (each charged as one target-compression unit of 258 operations) and one inverse NTT of size 196,608; S^((p-1)/2) mod g is computed with an in-place
NTT schedule that stores no spectra (row-wise operand transforms); gcd(g, S^((p-1)/2) - 1) by half-gcd; root finding on the gcd of degree at most 16; square root, back-map and two reference hashes.

Numbers. time_log2 30.133 (a run of at most 4 centres charged at its halt budgets; one centre: 28.133), memory 40,934,171 bytes (log2 25.287), normalized cost 35.420,
claimed success probability 0.00. 0 verified collisions of the target are included as certificates.

Success probability. Per line, the success fractions of the program with all halts active, and their Wilson lower limits (z = 2.576), are in proof.md section 8 (smallest limit 0.0000, line 0).
4 independent centres give at least 1 - (1 - 0.0000)^4 = 0.0000. No model of the number of roots of g enters the claim or any budget.

Per-line sample (proof.md section 8):

| line j | successes | executions | success fraction | lower limit, z = 1.96 | lower limit, z = 2.576 (used) |
|---:|---:|---:|---:|---:|---:|
| 0 | 0 | 3 | 0.000 | 0.0000 | 0.0000 |

Samples: 3 executions of this build (one centre each, seeds in the logs, line j given by the seed; only the first centre of an execution is counted). Every counted success was verified by a big-integer reference of the hash and by the organizer's hash implementation.

Budgets. Stage D (half-gcd) and stage E (root finding) are halts: the program stops when their charged work exceeds 21,108,000,000 and 187,665,120 operations. The stage D budget is the cost of the normal-case recursion tree
(19,187,264,087 operations, computed by bound_gcd.c from the shipped node procedures at the sizes of each node) plus the scan, plus 10 percent. Stage E: 4 x 40 shifts x 1,172,907 operations per shift (bound_root.c).
The work between two checks is at most 21,000,000 (stage D) and 1,172,907 (stage E). A halt is a failure and is counted inside the per-line fractions.

Ledger (primitive operations, C(2) = 258; full table and rules in proof.md sections 4 and 6):

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table `rho^j` (65,536 entries), roots of unity (once per run) | 66,509 | 595,918 | 662,427 | no |
| line setup (constants of the line, 1 inversion) | 391 | 3,608 | 3,999 | no |
| random centre | 0 | 3 | 3 | no |
| B: 393,216 line evaluations (units) + inverse NTT 196,608 + normalisation | 6,421,153 | 115,051,923 | 121,473,076 | no |
| C: S^((p-1)/2) mod g (lean schedule) | 16,131,772,597 | 38,506,857,907 | 54,638,630,504 | no |
| D: gcd(g, R-1) (half-gcd), as observed in the ledger run (includes the scan for the degree of R-1) | 3,170,520,858 | 15,865,414,186 | 19,035,935,044 | yes: halt budget 21,108,000,000 |
| E: root finding (deg G <= 16), at most 40 shifts per centre | - | - | one shift costs at most 1,172,907 | yes: halt budget 187,665,120 in total |
| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | about 40,000 observed | allowance 200,000 |

Worst case for 4 centres: init + 4 x (line + random + B + C + D budget + D gap bound) + E budget + E gap + F,G allowance = 662,427 + 4 x 75,889,107,582 + 187,665,120 + 1,172,907 + 200,000 = 303,746,130,782 operations = 1,177,310,584.4 units.

Memory: text 116,643 + data 768 + bss 5,336 = 122,747 bytes plus heap peak 40,741,792, stack bound 65,536 B (the run was executed with a 64 KiB stack limit), allocator slack 4,096 B.

| item | elements | bytes |
|---|---:|---:|
| twiddle table `rho^j`, `j < 2^16` | 65536 | 2097152 |
| `Y` (transform buffer, `3 * 2^17`) | 393216 | 12582912 |
| `tmp` (one transform row, `2^17`) | 131072 | 4194304 |
| `MU` | 195311 | 6249952 |
| `g` | 195313 | 6250016 |
| `F` (fold / result) | 195312 | 6249984 |

Charging rules. Field operations, 256-bit loads and stores, and every executed integer, comparison, branch, shift and address operation are charged 1 each, next to the statement that executes them.
The transform passes are blocks of up to four butterfly layers in a 16-element register block; straight loops are charged 8 per element; the radix-3 stage is charged per element for the loop, the rotation
update, the mask lookup and the addresses. The complete source of the executed program (section 10 of proof.md) is shipped, including the generator of the kernel header.

Heuristics declared in claim.json: H1 (score-critical): per-line success fractions bound the per-line success probability, centres independent; H2 (supporting): the charging rules describe the executed program;
H3 (supporting): the stage budgets of proof.md section 4.4 are enforced halts.

Limits. The success claim is a statistical lower limit from about 20 executions per line, not a proof; the leading coefficient of the digest polynomial, the interpolation and the collision criterion are exact and
verified by the executed program (collisions produced and checked by the organizer's hash). No Python experiment is declared because the organizer's experiment runner sizes the digest with digest(b"") and the Orchard
digest rejects the empty message. Cache and bandwidth effects are outside the cost model.
