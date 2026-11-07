# B3R7e: BLAKE3 r7, straight-line kernel + 5-byte gate instructions + first-collision Lemma 2 (10-16, STAGED, NOT SUBMITTED)

Package: research\blake3_r7\compact\pkg (blake3\{claim.json, proof.md 75 KB, experiments\{bsrho.py 62,130 B + manifest 3,400 B}}, submission-note.md 10 KB, dependencies.json: a2e94df7 first, then 1cd0dd3b, a6ee439c, 41b32afc, 75d5e1f9, 62cfd777, 0a9640ed, 3356413f, 6ae36351).
Slot: ~/hashsmash/yukon/pos_b3r7e/pareto (new slot; STAGED.sha256 673039383766f256..., dependencies.json sha256 91f65afe4383f3af...). Submit script (NOT run): research\launch\submit_pareto_pos_b3r7e.sh (deps guard, a2e94df7 first, refuses if staged files changed).

## Result
- time_log2 **124.97458** (certificate 2^12497457 * 1470^100000 <= N^100000 < 2^12497458 * 1470^100000; N = 61434525477062968827559999725385940266784; appA.py and bsrho.py agree). Memory 1,048,504 B = 2^19.99990, claimed 20, memory term 0, scalar score 124.97458.
- vs rival 616120b2 125.18448: -0.210. vs our staged/filed rolled B3R7c a2e94df7 125.29113: -0.317; vs B3R7d 9f8ff0a0 125.26917: -0.295; vs the owner's estimate "about 125.054" (1cd0dd3b time): -0.080 (the rest comes from the first-collision Lemma 2 and the larger table, see below).
- Plan: Tp 1101, table 72,522 entries x 10 B (largest that fits 2^20), age cap 14 L, B = 1.3305e36, 46,011 ops per batch (45,974 gates + 34 + 3). Exact certified P_lower = 0.390000001000 (appA.out, exact rationals). Time is monotone decreasing in Tp up to 1101 (scan: Tp 300 124.998, 600 124.980, 1000 124.9749, 1101 124.9746), so "largest Tp" is the optimum.

## The convention, stated as a cost-model price (proof 3.1, H3)
A register-only gate (step, stage-1 test, recovery circuit: XOR/AND/OR) is one 40-bit word, 5 B = 8-bit opcode + three 10-bit register numbers (800 registers < 1024). All other instructions (handlers 1,000, setup/cut/slice 160, recovery extras 47, loop control 3, spill code, generator image 1,445 wasm instr) stay at 36 B. Code = 47,548 gate words x 5 + 1,210 x 36 = 281,300 B. The C generator writes the 5-byte records (gen_c/gen.c, REC 5). A judge charging 36 B per gate gets 1cd0dd3b's memory term back (stated in the note limits).

## Two deviations from the filed lineage (both in proof/appA/bsrho, needed by the larger table)
1. The P_tiny collision-count Chernoff term used lambda = 5, threshold 60 (exp(-300 + (e^5-1)H)); it is vacuous once H > 2 (table above ~25k entries). Changed to lambda = 2 (exp(-120 + (e^2-1)H)), valid for H < 9, in Section 4 Steps 7 and the statement, bsrho `_lossq`, appA.py. Tp search range 400 -> 1500; exp argument clamped at 700 (overflow).
2. Section 4 is the first-collision proof of B3R7d (sec4_t9), generated through build_all.py.

## Checks run
- Cloud (108.61.192.253, /root/b3e, nice 10, own PIDs): organizer verifier blake3(M,7): one step 8,192 lanes 0 diffs; 7 chained steps 4,096 lanes 0; packed recovery 448 msgs 0; scalar 300 0; digest_words rounds 3/4/7 x 2,000 msgs 0; vs blake3 library 1.0.11 2,000 msgs 0 and step 8,192 lanes 0; **5-byte records decoded from the C generator's output and executed: 8,192 lanes vs organizer blake3(M,7): 0 differences**; selftest True. Outputs: compact\ext\*.out.
- Generator: wasm in a 16-page (1 MiB) VM emits the program byte-identical to the Python reference (sha256 e2666815..., 45,974 records, 771 regs, q equal); static x86-64 binary identical, runs with address space capped at 499,712 B (fails at 495,616), `--data=1048576`.
- Intake (organizer pipeline, Docker, slot pos_b3r7e): mechanically_valid, both experiments completed (256/256 each; 171 and 172 verified pairs); local 3.1 s / 4.4 s per 256 trials.
- prefile_check ALL PASS. rulecheck: mem-gate PASS, 15 PASS, 3 EXPOSED (R05, R07, R19: the same three as B3R7b), 4 N/A. Known-good line for bsrho.py appended to launch\KNOWN_GOOD_PROGRAMS.txt.

## Not tested
No cold-read of the new proof text; Section 4's lambda = 2 change is new (author-checked, exact certificate in Appendix A recomputed it). Python tooling not run under the memory cap (same as lineage). 5-byte word and 800-register file are declared conventions.

## Do r3..r6 gain from the same encoding? (DERIVED from each program's ledger via the compact bsrho with ROUNDS = r; not built or filed)
| row | staged/filed now | with 5-byte gates | note |
|---|---|---|---|
| r4 | B3R4f 124.93474 (code 935 KB at 36 B, table 10,176 x 7 B) | **about 124.894** (code 167 KB, table 119,872 x 7 B, best Tp about 500 of a scan; plan() must pick the best Tp, the 40-bit key false-match term binds above 1,000) | -0.041; needs b4f patch + plan fix |
| r3 | 62cfd777 124.8123 | 124.766 (compact bsrho straight, same program shape; 36 B version of the same code gives 124.777) | encoding alone -0.011, rest is lemma/table; r3 already fits at 36 B |
| r5 | B3R5c 125.19806 (rolled, 1,856 regs) | **124.914** if the kernel is UNROLLED (31,606 gates, code 207 KB, table 79,940) | -0.284 |
| r6 | B3R6d 125.23090 (rolled) | **124.950** if UNROLLED (38,790 gates, code 244 KB, table 76,231) | -0.281 |
r5/r6 gain comes from dropping the rolled body (its extra ops) because the straight line fits 2^20 at 5 B; the same rolled programs priced at 5 B alone (kept rolled) give a smaller gain (table only), not computed. Builds needed: a straight bsrho at ROUNDS 5/6 (the generator, KAT and selftest at those rounds have not been run).
