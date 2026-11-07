# BLAKE3 r3 (Pareto) wave 1: time-memory trade-offs and cheaper chain steps

Date 2026-10-13. Scope: score = time_log2 + max(0, log2(mem bytes) - 20). Labels: SEEN (read in a named file), COMPUTED (ran our own code here), INFERRED (reasoned, not run).
Read: paths_blake3_r3.md, b3r3_defense.md, LEVER_CELLS blake3-r3 rows, ATLAS_BLAKE3.md (a 2-round file, no r3 content used), sol_answer D207/D215/D220/D231, plus (for facts only) candidate_blake3\experiments\rho.py lines 186-230, proof.md memory/recovery lines, levers_step_count.md, levers_machine.md, swar_count.py. No other participant's code. Compute: 1 process, a few seconds each.
Scratch tools (own code, scratchpad `...\02bea564-...\scratchpad\`): `bs.py` (bit-sliced BLAKE3 gate tracer, validated), `spill.py` (load/store simulator), `led.py`/`scen2.py`/`dsweep.py` (ledger copies).

## 0. Baseline reproduced (COMPUTED)
`led.py` is a copy of rho.py plan()/ledger(). With PH=595, 7 lanes, U=16, stage1=4, d=114, tmax=18432, lambda=0.497 it returns time_log2 = 125.10856374888911, identical to D215/D220. All scores below use this same formula; only the named parameters change. Main loop is 99.44% of the total, recovery 0.56%, in-flight and cut losses about 0.2%.

## 1. Headline: bit-slicing (256 lanes) removes the rotation cost  (NEW, COMPUTED op count)
Idea. Put bit j of 256 independent chain states in 256-bit word "plane j". A 32-bit word is 32 planes. Rotations are renaming (0 ops), XOR is 32 ops for 256 lanes, an add is a ripple of full adders (5 gates per bit: x=a^c, y=b^c, s=x^b, carry=(x&y)^c; constant operands fold to 2 gates or 0). The digest planes are the next input planes (chain feed is renaming, no packing/unpacking). Only AND, OR, XOR are used. In the filed circuit 400 of 595 ops are the 80 variable rotations at 5 ops (levers_step_count.md c) and each 7 lanes; bit-slicing deletes that and carries 256 lanes.

Measured (COMPUTED, bs.py, constants folded, dead gates removed, hash-consed, polarity tracked, validated against the scalar 3-round digest on 64 random lanes; rounds 1/2/3 all True):
| rounds | gates per 256-lane batch | xor | and | or |
|---|---:|---:|---:|---:|
| 1 | 3,397 | 2,787 | 533 | 77 |
| 2 | 11,205 | 9,355 | 1,541 | 309 |
| 3 | **19,022** | 15,932 | 2,518 | 572 |
(129 output planes come out inverted: up to +129 NOT-fixes if the loop needs positive polarity, giving 19,151 as the upper bound.)
Per lane-step: bit-sliced 19,022 + 34 (filter: 31 OR + compare + branch + counter) + 3 loop = 74.4 ops; packed filed (595+4)/7 + 3/112 = 85.6 ops. Ratio 1.150 = 0.20 bit.

Score (COMPUTED with the filed ledger formula; changes: lanes 256, U=1, PH as stated, stage-2 charge 3000, DP event 2000, recovery run on the existing packed 595+64 circuit because a 2-lane recovery through a 19k-op batch would cost about 20% of the run; code 36 B/op as in D215 (10,400 ops x 36 B); table size and d refitted to fill 2^20 B, tail model tmax = 1.125 x 2^(128-d) which reproduces 18,432 at d=114):
| variant | register assumption | PH (ops/batch) | code B | table entries | d | score |
|---|---|---:|---:|---:|---:|---:|
| filed | 64 regs, no spills | 595 | 374,400 | 18,432 | 114 | 125.10856 |
| packed, fractional d (same model) | | 595 | 374,292 | 21,007 | 113.81 | 125.10727 |
| **bit-sliced, 32 B entries** | no spills (R >= about 1,000 words) | 19,022 | 715,284 | 10,351 | 114.83 | **124.9176** |
| bit-sliced + 129 NOT fixes | same | 19,151 | 719,928 | 10,206 | 114.85 | 124.9275 |
| bit-sliced, 25 B entries | same | 19,022 | 715,284 | 13,249 | 114.48 | 124.9130 |
| bit-sliced, R=1024 (spill sim) | 1024 regs counted as 32 KiB memory | 19,534 | 733,716 | 8,751 | 115.08 | 124.9591 |
| bit-sliced, R=512 | 512 regs = 16 KiB | 20,978 | 785,700 | 7,638 | 115.27 | 125.0639 |
| bit-sliced, R=256 | | 24,328 | 906,300 | 4,126 | 116.16 | 125.294 (worse than filed) |
| bit-sliced, R=64 | | about 30,100 by program order (lower bound about 26,000) | > 1,000,000 | none left | | not feasible; per-lane >= 98 ops vs 85.6 |
Spill numbers: Belady simulation over the straight-line program order (spill.py); program order is a poor schedule, so R=64..512 rows are upper bounds on the spill cost, but the R=64 lower bound is still above the packed per-lane cost because every G call needs its 128 state planes loaded and stored (about 256 memory ops per G call on top of about 790 gates).
Read this correctly: the 0.19 bit gain exists only if the judge accepts a declared register file of about 1,000 256-bit words (b3r3_defense W1/W2: the cost model fixes no register count; our own declaration is the only basis; an accepted precedent declared 64 or 16 registers). At 64 registers bit-slicing loses. This is a different technology, not a variant of the filed line.
What each piece needs: (1) generator that emits the 19k-op straight line at run time (source stays under the 64 KiB intake limit; code is still charged 36 B/op = 715 KB, which is 68% of 2^20 and pushes the DP table from 21k to about 10k entries, already priced in the table above); (2) lane insert/extract for DP events and restarts (about 512 to 2,000 ops per event, 2^14 events: negligible, charged 2000); (3) stage-2 check of the other 82 planes for a hit lane (about 100 ops per hit, 2^-24 per batch: negligible); (4) packed 595-op circuit kept for recovery (+23 KB code, included as 810 fixed ops); (5) restated Lemma 2 for density 2^-114.8 and 256 trails per body; (6) register-file declaration and a tracer live-word count under a real schedule.
Composition: additive with the D220 levers that do not touch the circuit (margin removal -0.0036, 25-B entries already in row 3). Not additive with grouped filter (the filter is 34 of 19,059 ops here) or PH=590 tuned CV (bit planes: each zero constant bit saves gates, not counted). Best stack estimate: about 124.91 (INFERRED sum).
Cost-model risk (SEEN levers_machine.md): the text says nothing on vector ops; this uses only AND/OR/XOR, the cheapest primitives.

## 2. Hybrids around bit-slicing (INFERRED unless stated)
- Chunk-slicing (k-bit chunks, pitch k+1, native add for chunk plus carry): per chunk-add about add, add(cin), and, shr, and = 5 ops for 256/(k+1) lanes. Per lane-bit k=1: 5/128; full bit-slice: 5/256. Full slicing dominates; k=4 gives 5/(4x51). Worse.
- Full adder through the native 256-bit ADD on pitch-2 planes (sum bit0, carry bit1): needs shift and mask per stage, 128 lanes: no better than 5 gates for 256 lanes.
- 8 lanes at pitch 32 (packed SWAR): needs a carry-killing add (about 6 ops per add: levers_step_count.md c, "far worse"). Rough count: 100 adds x 5 extra = +500 on 595: about 1,100 per 8 lanes = 137 per lane. Worse than 85.6.
- Pitch-64 duplicated lanes (2-op rotation): 4 lanes, re-duplication after each add; worse (GUESS, same source).
- 7 guarded lanes + unguarded top lane: 7p+32 <= 256 needs p <= 32; with a guard (p >= 33) at most 6 guarded + 1 = 7 lanes: no gain.

## 3. Packed line: code size versus loop unrolling versus table (COMPUTED, small new lever)
Memory is code + table + counters; code is 36 B per op, so U (batches per unrolled body) trades loop overhead (3 ops per body) against table room (which sets d, hence recovery + in-flight loss). Same model, fractional d, 32-B entries, 810 fixed ops (recovery + handlers):
| U | code B | entries | d | score |
|---:|---:|---:|---:|---:|
| 1 | 50,832 | 31,115 | 113.25 | 125.11099 |
| 2 | 72,396 | 30,441 | 113.28 | 125.10754 |
| 4 | 115,524 | 29,093 | 113.34 | 125.10604 |
| **8** | 201,780 | 26,398 | 113.48 | **125.10583** |
| 16 (filed) | 374,292 | 21,007 | 113.81 | 125.10727 |
| 32 | 719,316 | 10,225 | 114.85 | 125.11679 |
Optimum U=8: -0.0014 bit vs U=16 at fractional d, -0.0027 vs the filed integer-d row. Needs: nothing but U=8 and the D220 fractional-DP restatement. Not listed in LEVER_CELLS (checked rows); candidate cell. Stacks with D220 fractional/25-B (those already assume U=16, so the combined win is less than the sum).

## 4. Memory knee and what more memory buys (COMPUTED, packed U=16, 32-B entries)
| d | entries | mem B | time_log2 | mem penalty | score |
|---:|---:|---:|---:|---:|---:|
| 110 | 294,912 | 9.8e6 | 125.09864 | 3.226 | 128.32 |
| 112 | 73,728 | 2.7e6 | 125.10063 | 1.383 | 126.48 |
| 113 | 36,864 | 1.56e6 | 125.10328 | 0.569 | 125.67 |
| **114** | 18,432 | 966,164 | 125.10856 | 0 | **125.10856** |
| 115 | 9,216 | 671,252 | 125.11908 | 0 | 125.11908 |
| 116 | 4,608 | 523,796 | 125.13988 | 0 | 125.13988 |
| 118 | 1,152 | 413,204 | 125.25877 | 0 | 125.25877 |
Result: infinite memory would buy at most 0.0100 bit (limit about 125.0986), while one extra doubling above 2^20 costs about 1 bit. Memory below 2^20 earns nothing, so the filed point is at the knee. Time-memory trade-off is exhausted on the Pareto axes; the only memory-side gains are the D220 ones (fractional d, 25-B entries, smaller code) worth 0.002 to 0.009 in total. This also means van Oorschot-Wiener "w vs time" curves do not apply to a plain collision of one function: DP work is already sqrt(pi N/2)-class plus 2^d-proportional overhead, no w^-1/2 term.

## 5. Other time-memory families (each recorded; all NULL or worse)
- Memoryless cycle finding (Floyd, Brent): about 3.09 sqrt(N) and 1.98 sqrt(N) function evaluations (INFERRED, recalled literature constants, not rechecked) against our 0.9945 sqrt(N) at P=0.39. At least +0.99 bit. Worse; memory is free below 2^20 anyway.
- Parallel / multi-processor vOW: the model charges total operations, not wall time (SEEN D220/rho.py ledger). Parallelism earns 0.
- Hellman / rainbow / precomputation: a collision has no fixed target. Precomputation up to 2^86 evaluations (cost about 0.005 bit by the board convention, memory file) gives P x Q / N = 2^(86+128-256) = 2^-42 expected extra cross collisions. NULL (COMPUTED arithmetic).
- Multi-target: the event is any pair among Q points; the birthday already uses all Q^2/2 pairs. Joux-style multicollision needs a Merkle-Damgard chain of compressions (full-hash r3 on one 64-byte block: the digest is the final CV, no iteration to exploit). NULL.
- Success probability axis (SEEN claim.json success_probability 0.39, rho.py LAMBDA): time shift 0.5 log2(lambda/0.497): P=0.2 -0.578, 0.3 -0.239, 0.5 +0.240, 0.63 +0.500, 0.9 +1.106 (COMPUTED). If the organizer floor were not 0.39, lowering P would pay 1.4 bits per unit lambda; the floor itself is not read here (INFERRED floor). If scoring were expected time with restarts, the optimum lambda is 1.256 (P=0.715): 0.200 bit better than lambda 0.497 (COMPUTED minimization of sqrt(l)/(1-e^-l)); NOT claimed: needs the rule text, which says P >= 0.39 in the filed claim.

## 6. Cheaper chain steps: early abort, truncated digest, partial evaluation
- Early-abort on a truncated digest (INFERRED, blocked): the chain function must be f itself, because the next input is all 256 digest bits and a truncating map phi would make chain collisions phi(f(x)) = phi(f(y)), which are full collisions only with probability |im phi| / 2^256. So every output plane/word is needed each step. The only dead work is zero: levers_step_count.md (b) shows 0 of 595 lines dead; the b and d outputs of the last diagonal round (about 24 ops) are needed by the digest xor and by the next input. If a 128-bit truncated chain were a legal target it would save about 24 ops (0.059 bit), but it is not: it finds 128-bit collisions only. Cost to collide 256 bits through 128-bit partials is 2^192. NULL.
- DP test cost: already 4 ops per 7 lanes (stage 1 filter tests 32 bits, replays 300 ops on a hit with probability 2^-29 per batch). Bit-sliced version: 34 ops per 256 lanes. Nothing left (0.0045 bit grouped-filter gain in LEVER_CELLS is the packed-line residue).
- Partial evaluation of constants: columns of round 1 are constant (SEEN levers_step_count a); the placement of the 8 variable message words was brute-forced over C(16,8) subsets (subsets.py, SEEN file; result not re-read here). In the bit-sliced circuit the same folding is included in 19,022.
- Tuned CV / free first block (LEVER_CELLS 0.0024, D220 PH=590): additive to the packed line only; in bit-sliced form each constant bit that vanishes saves 1 to 4 gates, not counted.
- Other SIMD packings (section 2): none beats 7 x 36 except full bit-slicing, which needs the large register file.

## 7. Ranked list of what this wave found
| # | technique | best estimate | label | needs |
|---|---|---:|---|---|
| 1 | 256-lane bit-slicing, packed circuit kept for recovery | 124.918 (about 124.91 with margin removal) | COMPUTED ops, ledger formula; judge/register premise open | declared register file about 1,000 words (or R=512: 125.064), generator, event/lane code, restated lemma, 36-B/op code charge 715 KB |
| 2 | Packed U=8 with fractional d | 125.10583 | COMPUTED | the D220 fractional-DP lemma restatement; U=8 code |
| 3 | Bit-sliced with R=512 and spills | 125.064 | COMPUTED upper bound (poor schedule) | register file 512 words counted as 16 KiB |
| 4 | Memory above 2^20 (any amount) | worse (+0.57 at 1.56 MB) | COMPUTED | nothing: closed |
| 5 | Memoryless / Hellman / parallel / multi-target | worse or NULL | INFERRED + COMPUTED arithmetic | nothing |
| 6 | Truncated-digest early abort | blocked | INFERRED | none possible |
| 7 | 8-lane pitch 32 / hybrid slicing / duplicated lanes | worse (about 137 ops per lane vs 85.6) | INFERRED | none |
| 8 | Success-probability shifts | -0.24 at P=0.3 etc. | COMPUTED arithmetic; rule text unread | organizer floor on P |

Open checks worth one agent each (not run): a real scheduler for the bit-sliced straight line to get the true load/store count at R=64, 128, 256 (could show a lower spill bound than the Belady program order); a bit-sliced adder with fewer than 5 gates per bit via carry-save sharing across the a+b+m double add (the 10-gate-per-bit double add may drop); a ledger check of U=8 with the real tmax tail rule in proof.md Lemma 2 instead of the 1.125 model.
