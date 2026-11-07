Orchard Poseidon, r = 2 (poseidon-orchard-r2-prefix-v1): one deterministic run on the fixed target, executed operation count, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and two partial rounds). It is a single deterministic procedure with no selection step: it tries the centres c_i = i in the fixed public order i = 1, 2, 3, ..., runs each trial completely, and stops at the first trial that yields a collision. It was executed once from the start on the fixed target; it stopped after 1 trials, at c = 1. The claim is the executed cost of that one run, every trial charged, failed ones included: success probability 1 (deterministic procedure executed on the fixed target, every executed trial charged). There is no worst-case bound, no probability theorem and no heuristic premise about the mathematics; the time is the executed operation count and the memory is the executed peak (the maximum over the trials). The one declared premise in the claim file is that the stated charging rules describe the shipped program.

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree: its S-box output is affine in one parameter W. The digest is then a univariate polynomial F(W) of degree 5^8 = 390625. The line contains exactly p inputs, one for each W in F_p. This is the two-round bypass of Bariant, Bouvier, Leurent and Perrin (ToSC 2022/3), used by the earlier entries on this board.
2. For a centre c, write F(c + s) - F(c - s) = 2 s g(s^2). The polynomial g has degree 195312 and a leading coefficient that does not depend on c. A root S of g that is a nonzero square gives s = sqrt(S) and two different inputs W1 = c + s and W2 = c - s with the same digest. Working with g (half the degree of F) halves every transform length compared with working with F itself.
3. The program evaluates the digest at 393,216 points (each charged as one full target compression, 258 operations), interpolates g with one inverse transform of length 196,608, computes S^((p-1)/2) mod g with a low-memory transform schedule (236 Barrett squarings on 3 * 2^k transforms), and takes gcd(g, S^((p-1)/2) - 1) with a half-gcd. A trial whose gcd is constant has no useful root and is charged in full; the first trial with a root of g that is a nonzero square has its root isolated, square-rooted, mapped back, and both inputs are checked with the reference hash. The run ends there with the collision.

Numbers. time_log2 27.05075 (the executed run: N = 35,867,804,181 primitive operations = 139,022,496.8 target-compression units at 258 operations per unit), memory 40,933,715 bytes (log2 25.287), normalized cost 32.33775, success probability 1, preprocessing 0 (the twiddle table is built inside the run and counted in N), 1 trials. One squaring step of the powering costs 120,981,777 operations. One verified collision is included as a certificate; it is the output of this run, and it was checked with an independent big-integer implementation of the reduced hash and with the organizer's digest function.

Where the charge comes from (primitive operations, rules in proof.md section 4.2):
| stage | arith | other | total |
|---|---:|---:|---:|
| init: twiddle table (once) | 66,509 | 104,398 | 170,907 |
| setup: the line | 391 | 3,608 | 3,999 |
| A: centre c_i = i (all trials) | 0 | 1 | 1 |
| B: 393,216 evaluations (258 units each) + inverse NTT 196,608 + normalisation (all trials) | 6,421,153 | 109,612,408 | 116,033,561 |
| C: `S^((p-1)/2) mod g` (m = 195312, 236 steps per trial, all trials) | 16,131,772,597 | 12,598,711,324 | 28,730,483,921 |
| D: half-gcd of (g, R - 1) (all trials) | 3,170,520,527 | 3,850,520,954 | 7,021,041,481 |
| E: root of G (last trial only) | 1 | 4 | 5 |
| F: square root, back-map (last trial only) | 3,066 | 29,661 | 32,727 |
| G: two reference hashes (last trial only) | 516 | 2,064 | 2,580 |
| rounding: half units are rounded up once for the run, not once per stage line | | | -1 |
| total of the counted run | | | 35,867,769,181 |
| uncounted self-checks (section 4.2, stated bound) | | | 35,000 |
| total N | | | 35,867,804,181 |

Trials:
| trial | centre c_i | deg G | charge of the trial (operations) |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 31,882,331,315 |

How the accounting works. Every figure is a counter of the same single execution of the shipped source: field operations, 256-bit loads and stores, control operations, half units of loop and address work, and 258 operations for each reduced permutation evaluation. Nothing is bounded or extrapolated except one stated item: a hardware self-check that runs every 32 squarings with its counters restored; its measured cost is 4,235 operations per execution and a bound of 35,000 operations for the whole run is added to the total. The half-gcd is charged at what it executed (7,021,041,481 operations over all trials). The proof gives the derivation of the line, the charging rules, the powering schedule, the half-gcd, the memory accounting, and the complete source, so a referee can recompile and rerun it and reproduce every count and the collision.

On the loop-control rule. The proofs of the public r = 2 entries charge loop and address work at one half unit per butterfly and one half unit per element of an unrolled loop, and no separate address operation for loads and stores. This entry uses the same two statements. An earlier version of this program charged more (an address operation for every load and store, several control operations per block); those charges were replaced by the stated rule and nothing else in the counters was lowered. The register assumption (a block of 16 data words and two working words held in registers) is disclosed and is the one structural assumption of the model.

Memory. The largest live set is the powering of the stage that computes S^((p-1)/2) mod g, at degree 195312: the transform buffer (3 x 2^17 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table. Tracked heap peak (the maximum over the trials) 40,741,792 bytes, plus the static image (122,291 bytes), a stack bound of 65,536 bytes (the run was executed under a 64 KiB stack limit) and 4,096 bytes of allocator metadata. Counted: every buffer of the program, the code, constants and tables of the executable, the stack bound and the allocator metadata. Not counted: the dynamically linked C library and loader mappings and kernel structures of the host process; the program uses from the library only malloc, free, memcpy, memset and, in the ledger run only, printing.

What is not included. Nothing was selected beforehand: the centres are 1, 2, 3, ... in that order, the run was made once, and no earlier run of any centre is left out of N. The probability 1 is the statement about this executed run; it says nothing about how many trials another sequence of centres would need (each centre has roughly a 39 percent chance of yielding a usable root). The organizer did not run the program, so the counts rest on the shipped source. The half-gcd is the plain half-gcd with product-by-product transforms; shared-transform matrix products and wrapped matrix-vector steps, which shorten it, are not used here.

Reasoning narrative.
Context. Judged entries on this board for the same line of attack charge the executed run of a deterministic procedure on the fixed target with success probability 1. This entry follows that convention for the r = 2 target, with the odd-part variant of the line polynomial, which halves the degree and therefore the transform sizes and the memory.
Approach. Fix the order of the centres, run the procedure once from the first centre until it stops, and report its counters: the powering is the largest term, the half-gcd second, the evaluation of the line third.
Trade-offs. The executed run is much cheaper than a worst-case charge, in exchange for a claim that is the cost of this run rather than a probability, which the proof says in so many words. The powering keeps its spectra out of memory (they are regenerated row by row), which costs time and saves memory.
Implementation. Reused: the finite-field code, the transform engine, the low-memory powering and the half-gcd of earlier work; new for this entry: the fixed order of centres with every trial charged, the removal of the bounds and halts that the run does not reach, and the loop-control rule above.
Results. The run stopped with a collision that the organizer's hash accepts; the counters are in the table above.
Next steps. Shared-transform products inside the half-gcd and a cached transform of the modulus in the powering would lower the executed count directly.
