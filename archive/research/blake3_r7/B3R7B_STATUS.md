# B3R7b: blake3 round 7 with a ROLLED round body - STATUS (2026-10-15, Sonnet agent)

STAGED, NOT SUBMITTED. Needs the owner's go, then `bash research/launch/submit_pareto_b3r7b.sh` (deps guard: 1cd0dd3b first, then a6ee439c, 41b32afc, 75d5e1f9, 62cfd777, 0a9640ed, 3356413f, 6ae36351; refuses if the staged files or dependencies.json changed). Same challenge as 1cd0dd3b (B3R7).

## Result (from the program: `python3 bsrho.py --ledger`, appA.py agrees: N = 76457149232530522272426968132549265867467)
- time_log2 **125.29018** (certificate 2^12529017 * 1470^100000 <= N^100000 < 2^12529018 * 1470^100000), unit C(7) = 1470.
- memory **1,048,510 B = 2^19.99991** (search phase; setup phase 944,908 B). Claim memory_log2_bytes = 20 (log2 of the 2^20 budget; claiming the fractional 19.99991 made the mem-gate flag the 1,048,576-byte sandbox caps). Memory term 0.
- scalar score **125.29018** against 125.92083 for 1cd0dd3b: **-0.63065 bit** (time +0.23621, memory term -0.86686). Gate was >= 0.1: met.
- Plan: Tp 229, B = 1.366476e36, c = 13 L, table 15,989 entries x 10 B (the largest that fits 2^20), P_lower 0.39000 (b4d Lemma 2, `_lossq` / `_b256`, recomputed by the program). Recovery circuit 1,532 ops (q = 0, no XOR with q).

## The rolled program (answer to requirement 1: how the loop is priced)
Step = rounds 1-2 straight line (constants folded: 2,614 + 7,184 = 9,798 gates), 240 complements (planes stored inverted, so the body has equal input/output polarity; the generic body outputs only upright planes, so q = 0), 512 ops setting the message slots of round 3 (256 zero planes, 256 copies of x planes), loop of 5 iterations of ONE generic round (8,416 gates, no constants: the 8 zero message words are real operands, +1,232 gates per round against a folded round), message permutation by REAL register moves (two 8-cycles of the BLAKE3 slot permutation, one temporary word per cycle = 576 moves), executed 4 times (loop leaves before it after iteration 5), loop control 20 ops (counter set 1; decrement, compare, branch 3 x 5; jump back 1 x 4; 5 control instructions of 36 B), 256 digest XORs into registers 0..255. Executed 55,210 ops per step (b7: 45,974, +20.1 percent); static 19,803 instructions (b7: 45,974); total code 22,579 instr x 36 = 812,844 B. Re-indexing instead of moves is NOT used (the instruction names its registers); no zero-cost decode. Door 5 of doors_1015/blake3.md estimated +768 ops for r4; here the counted cost is 576 x 4 + 1,232 x 5 + 512 + 240 + 20 = 9,236 ops over the straight line.
- Registers: the program uses exactly 1,827 (x 256, state 512, message slots 512, loop temporaries 515, from reg 1312), 29 spare as in b7: R = 1,856 declared, 59,392 B counted. Smaller files NOT priced for the rolled program (no spill allocator; stated in proof 3.5 and the note limits).
- Variants tried (ledger only, same program family): prefix of 1 round + 6 iterations: 125.31099; no prefix (7 iterations): 125.46910; prefix 2 (built): 125.29017. Prefix 3 does not fit 2^20 (about 27k instructions).

## What was built (b8/)
- `rolled_ref.py` (dev reference), `patch_b8.py` -> `bsrho_b8_stage3.py` -> `pkg/blake3/experiments/bsrho.py` (+ `embed_gen.py`, comment trims, REGISTERS 1856). bsrho.py 62,059 B + manifest 3,400 B = 65,459 B (<= 64 KiB, 77 B spare).
- C generator `gen_c/gen.c` (two passes per segment, pinned outputs, no node table): compiled to wasm (2,249 instr), emits the listing byte-identical to the Python reference (sha256 856ce844..., 19,803 instr, 1,827 regs, 74,552 calls), runs in a 16-page (1,048,576 B) VM (14 pages, 14.2M wasm ops); native static binary also identical, runs under `prlimit --as=1048576` (fails at 1,007,616).
- `appA.py` (Appendix A, equals the program ledger), `patch_text8.py` -> proof_t8.md / note_t8.md, `patch_build8.py` -> `build_all8.py` -> package `pkg/` (claim.json, proof.md 63 KB, certificates, experiments, submission-note.md 13.3 KB, dependencies.json: 1cd0dd3b first + b7's list).

## Verification (requirement 3)
- selftest True (step vs scalar 4,096 lanes, 7 chained steps, flat-listing interpreter incl. loop control vs compiled step, hits 0 / dead 0).
- Rolled vs straight-line b7 step: 16,384 lanes (random, small-input, sparse/dense), 0 differences; interpreter vs compiled: equal (`ext/rolled_vs_straight.py`).
- vs organizer blake3(M,7): one step 8,192 lanes, 7 chained steps 4,096 lanes, packed circuit 448, scalar 300: 0 differences; rounds 3/4/7 digest 2,000 msgs each: 0; vs blake3 library 1.0.11 (pip target /tmp/b3lib): digest 2,000 and rolled step 8,192 lanes: 0 differences (`ext/ref_regress.out`).
- Intake in the organizer pipeline (Docker, 20 s / 128 MB limits): mechanically_valid, both experiments completed, wall 32 s total incl. container; local: bsrho-n18 5.1 s / proj-k0-w256 7.0 s per 256 trials, peak RSS 30 / 32 MB (b7: 51 / 64). Organizer: 162 of 256 and 176 of 256 trials with a verified pair (report `organizer_report_b8.json`, deterministic across two runs). Chunked compile kept (2,000-line chunks).
- rulecheck: mem-gate PASS (38 stage peaks <= 2^20), 13+ PASS, 4 N/A, 3 EXPOSED (R05, R07, R19: the same three as b7). prefile_check: ALL PASS (note 13.3 KB; known-good line for bsrho.py appended to launch/KNOWN_GOOD_PROGRAMS.txt).

## Slot / files
`~/hashsmash/yukon/pos_b3r7b/pareto` (base pos_b3r4d): STAGED.sha256 4227505b24d8c9264e81a6b0c7933f7e07e3fd96ba908d02aa10f6f3dcec4dc8 (file hash), dependencies.json sha256 d64e2dc7e448e81e30a72be2a5a02659276c2fa1827308a1747fc0baf2165346. Package: research/blake3_r7/b8/pkg. Submit script (NOT run): research/launch/submit_pareto_b3r7b.sh. Scratch slot pos_b3r7bpre deleted. The slotstage-generated launch/slotstage/out/submit_B3R7B.sh is NOT the one to use (no deps guard).

## Not tested / risks (plain)
- Judges may price the loop differently (loop control, moves, setup of message slots are this entry's counted reading); the register file of 1,856 x 256-bit is a declared convention (H3) and smaller files are not priced.
- Section 4 (Lemma 2) is b4d's, checked by its author only; the same reading as B3R7 applies. Python tooling was not run under the claimed memory cap; only the generator was (wasm 16 pages, native --as=2^20).
- Memory is 66 B under 2^20 in the byte account, claimed as 20: a judge recounting code (36 B/instr, 22,579 instr) or registers differently could exceed 2^20 and incur a small term (each extra 1 percent of memory costs about 0.014 bit).
- Not squeezed (about 0.01 bit each): in-place half-round updates (fewer registers), a rolled recovery circuit (1,532 instr), a double-buffered two-round body. Not run: yukon submit, GPU.
