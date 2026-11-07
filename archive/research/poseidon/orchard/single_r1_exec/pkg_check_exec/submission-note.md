Orchard Poseidon, r = 1 (poseidon-orchard-r1-prefix-v1): one deterministic run on the fixed target, executed operation count, complete source in the proof.

What this entry is. A collision finder for the reduced Orchard hash (eight full rounds and one partial round). It is a single deterministic procedure with no selection step: it tries the centres c_i = i in the fixed public order i = 1, 2, 3, ..., runs each trial completely, and stops at the first trial that yields a collision. It was executed once from the start on the fixed target; it stopped after 1 trials, at c = 1. The claim is the executed cost of that one run, every trial charged, failed ones included: success probability 1 (deterministic procedure executed on the fixed target, every executed trial charged). There is no worst-case bound, no probability theorem and no heuristic premise; the time is the executed operation count and the memory is the executed peak (the maximum over the trials).

The method in plain terms.
1. After the first full round, the state is an affine image of two free field elements (U, V) and one constant. Along a line in the (U, V) plane where one coordinate of the second round's S-box input stays constant, the second round costs no degree: its S-box output is affine in one parameter W. The digest is then a univariate polynomial F(W) of degree 5^7 = 78125. The line contains exactly p inputs, one for each W in F_p.
2. For a centre c, write F(c + s) - F(c - s) = 2 s g(s^2). The polynomial g has degree 39062 and a leading coefficient that does not depend on c. A root S of g that is a nonzero square gives s = sqrt(S) and two different inputs W1 = c + s and W2 = c - s with the same digest.
3. The program evaluates the digest at 98,304 points (each charged as one full target compression, 237 operations), interpolates g with one inverse transform, computes S^((p-1)/2) mod g with a low-memory transform schedule (238 Barrett squarings on 3 * 2^k transforms), and takes gcd(g, S^((p-1)/2) - 1) with a half-gcd. A trial whose gcd is constant has no useful root and is charged in full; the first trial with a root of g that is a nonzero square has its root isolated, square-rooted, mapped back, and both inputs are checked with the reference hash. The run ends there with the collision.

Numbers. time_log2 25.38622 (the executed run: N = 10,393,435,263 primitive operations = 43,854,157.2 target-compression units at 237 operations per unit), memory 8,830,730 bytes (log2 23.075), normalized cost 28.46122, success probability 1, preprocessing 0 (the twiddle table is built inside the run and counted in N), 1 trials.
One verified collision is included as a certificate; it is the output of this run.

Where the charge comes from (primitive operations, rules in proof.md section 4.2):
| stage | arith | other | total |
|---|---:|---:|---:|
| init: twiddle table (once) | 17,361 | 126,642 | 144,003 |
| setup: the line | 391 | 3,519 | 3,910 |
| A: centre c_i = i (all trials) | 1 | 2 | 3 |
| B: 98304 evaluations (units) + inverse NTT 49152 + normalisation (all trials) | 1,436,260 | 31,273,571 | 32,709,831 |
| C: `S^((p-1)/2) mod g` (m = 39062, 238 steps per trial, all trials) | 3,536,772,942 | 5,315,154,386 | 8,851,927,328 |
| D: half-gcd of (g, R - 1) (all trials) | 389,577,467 | 1,119,024,292 | 1,508,601,759 |
| E: root of G (last trial only) | 2 | 5 | 7 |
| F: square root, back-map (last trial only) | 3,168 | 40,514 | 43,682 |
| G: two reference hashes (last trial only) | 474 | 4,266 | 4,740 |
| total N | | | 10,393,435,263 |

Trials:
| trial | centre c_i | deg G | half-gcd charge |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 1,508,601,747 |

How the accounting works. Every figure is a counter of the same single execution of the shipped source: field operations, 256-bit loads and stores with an address operation each, loop control, and 237 operations for each reduced permutation evaluation. Nothing is bounded or extrapolated, and no other run enters the count. The half-gcd is charged at what it executed (1,508,601,747 operations over all trials). The proof gives the closed derivation of the line, the charging rules, the powering schedule, the half-gcd, the memory accounting, and the complete source, so a referee can recompile and rerun it (about 90 seconds on one core) and reproduce every count and the collision.

Memory. The largest live set is the powering of stage C at degree 39062: the transform buffer (3 x 2^15 elements), one transform row, the Barrett inverse, the modulus and the result, and the twiddle table. Tracked heap peak (the maximum over the trials) 8,468,544 bytes, plus the static image (292,554 bytes), a stack bound of 65,536 bytes (the run was executed under a 64 KiB stack limit) and 4,096 bytes of allocator metadata. Counted: every buffer of the program, the code, constants and tables of the executable, the stack bound and the allocator metadata. Not counted: the dynamically linked C library and loader mappings and kernel structures of the host process; the program uses from the library only malloc, free, memcpy, memset and, in the ledger run only, printing.

What is not included. Nothing was selected beforehand: the centres are 1, 2, 3, ... in that order, the run was made once, and no earlier run of any centre is left out of N. The probability 1 is the statement about this executed run; it says nothing about how many trials another start would need. The organizer did not run the program, so the counts rest on the shipped source; the one structural assumption of the cost model is a register file of 18 words of 256 bits per transform block (16 data words and two working words: the twiddle operand and the butterfly temporary).

Reasoning narrative.
Context. Judged entries on this board for the same line of attack charge the executed run of a deterministic procedure on the fixed target with success probability 1. This entry follows that convention for the r = 1 target.
Approach. Fix the order of the centres, run the procedure once from the first centre until it stops, and report its counters: the powering is the largest term, the half-gcd second, the evaluation of the line third.
Trade-offs. The executed run is much cheaper than a worst-case charge, in exchange for a claim that is the cost of this run rather than a probability, which the proof says in so many words.
Implementation. Reused: the finite-field code, the transform engine, the low-memory powering and the half-gcd of earlier work; new for this entry: the fixed order of centres with every trial charged, and the removal of the bounds and halts that the run does not reach.
Results. The run stopped with a collision that the organizer's hash accepts; the counters are in the table above.
Next steps. A cheaper powering schedule or a lighter loop-control charge in the transforms would lower the executed count directly.
