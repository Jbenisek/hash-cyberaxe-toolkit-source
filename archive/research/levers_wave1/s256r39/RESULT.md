# Lever s256r39: rolled bit-sliced SHA-256 r39 at 36 B per instruction

Lever wave 1, 10-15. Research and pricing only. Nothing was built into a package, staged or submitted. No filed package, slot or factory row was touched. All files are in this folder. Tests ran on the local PC with Python 3.14.3 at BelowNormal priority, at most 2 processes at a time, and each run took under 5 minutes.

## 1. The new number

**r39: time_log2 = 124.50211** under Lemma 2 v2, against 3c1d7f68 (S256R39V2) at 124.854. That is **-0.352 bit**. Memory is 1,048,566 B, so the memory term is 0.

Arithmetic (`final.py`, exact integers; quadrature at 20,000 panels, the same as the filed code):

| part | ops |
|---|---:|
| main loop: B * 55,638 | 82,160,456,749,238,340,000,000,000,000,000,000,000 |
| slice checks: ceil(B/2^48) * 1,300 | 6.82e24 |
| stage-1 hits: e2max * 2,800 | 4.93e32 |
| finished trails: tmax * (3,800 + 3 tmax) | 91,082,107 |
| cut trails: 2 * 4,200 | 8,400 |
| recovery: capr * 2,278 + 600 (packed 7-lane circuit) | 2,539,597,281,753,193,461,947,308,444,070,632,312,346 |
| setup + generator | 55,475,200 |
| **N** | **84,700,054,523,892,275,374,752,444,422,530,026,839,153** |

- log2(N/2812) = 124.5021058.
- Certificate: 2^12450210 * 2812^100000 <= N^100000 < 2^12450211 * 2812^100000. Claim 124.50211.
- Plan: B = 1.4767e36 batches of 256 lanes, Tp 62, kappa 13, tmax 4,913 entries of 26 B, P_lower 0.390000001 (float; the plan target), theta 0.50470.
- The main loop is 97.0% and recovery 3.0%.
- Memory:
  - code (19,844 + 35 + 3 + 3,421 other) x 36 B = 838,908
  - registers 1,024 x 32 = 32,768
  - counters 16,384
  - W' array 32 words x 1,024 B = 32,768
  - table 4,913 x 26 = 127,738
  - total 1,048,566 <= 2^20.

**Composition (another lever, not part of this one):** 10-byte entries with a 2-pass recovery (the B3R4e recipe) give **124.38993** (-0.464). The table grows to tmax 12,774. Recovery is charged twice.

**r40..r64: yes, the lever applies to every row.** The gain is -0.28 to -0.32 bit (Lemma 2 v2, 26 B entries, 1,024 registers; 2,000-panel quadrature, good to about 1e-4):

| R | design (schedule loop start) | ops / batch of 256 | instructions | tmax | rolled | packed (factory / filed) | gain | with 10 B entries (best design may differ: r40 and r48 use the loop from 24) |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 39 | straight schedule | 55,638 | 19,844 | 4,913 | 124.50211 | 124.854 (3c1d7f68) | -0.352 | 124.38993 |
| 40 | 16 | 64,098 | 15,576 | 9,765 | 124.55419 | 124.86300 (0bcb5aeb, v1) | -0.309 | 124.46771 |
| 41 | 17 | 65,351 | 16,829 | 7,918 | 124.56422 | 124.87235 | -0.308 | 124.50346 |
| 48 | 16 | 80,678 | 15,576 | 8,238 | 124.60335 | 124.92188 | -0.319 | 124.54282 |
| 56 | 16 | 97,258 | 15,576 | 6,705 | 124.65202 | 124.96233 | -0.310 | 124.5777 |
| 63 | 15 | 112,865 | 14,603 | 6,631 | 124.68238 | 124.98835 | -0.306 | 124.60566 |
| 64 | 16 | 113,838 | 15,576 | 5,169 | 124.71496 | 124.99201 (factory v2) | -0.277 | 124.61125 |

Rows 42..47, 49..55 and 57..62 were not computed. They lie between their neighbours, and each takes about 30 s with `v2price.py R 2000 13,14 SF`.

## 2. What changed against EDGE_AUDIT lever #4

The audit's picture does not hold:

- It said rolling frees memory for a bigger table. The rolled bit-sliced program in fact has **more** code than the packed one: 839 KB against 183 KB at r39. Its table shrinks from 34,295 to 4,913 entries.
- The gain comes only from ops per evaluation: **217.3 against 316.1** (packed 2,213/7), which is log2 = -0.54. The smaller table gives part of that back: the 256 in-flight trails waste about 350/tmax, and recovery grows.
- The audit's 8-step body is not the best design.

Here is what the counting found:

- **Compression loop: 4-step body, no moves.** The state words form two shift registers of length 4 (a, b, c, d and e, f, g, h). A 4-step body therefore renames the registers back to their starting places. W'_i = W_i + K_i is loaded, 32 loads per step. The carried polarity has a fixed point with 0 corrections. The body is 4,976 gates + 128 loads + 4 loop ops = 5,108 per iteration. The loop runs 8 iterations over steps 7..38.
- **K never enters a loop at r39.** At r39 the schedule W16..W38 is straight-line code with constants folded. The constant K is added there, at 2-3 gates per bit, and W' is stored, so the compression loop does a 3-add T1. At r40..r64 the schedule is an 8-word loop. It keeps an 8-word W ring and an 8-word U ring in registers (U_i = W_{i-16} + sigma0(W_{i-15}) is computed 8 steps early), so it needs no moves. K is loaded there, and the stored polarity of each K plane is chosen at setup so that every W' plane comes out upright (a free knob).
- **Ops per batch at r39:**

  | item | ops |
  |---|---:|
  | straight phase | 14,736 |
  | 8 compression iterations | 40,864 |
  | stage-1 test | 35 |
  | batch loop | 3 |
  | **body** | **55,638** |

  The straight phase is made of:
  - 12,656 gates: steps 0..6, W16..W38, the W' adds
  - 456 + 85 polarity NOTs
  - 928 W' stores
  - 128 constant sets
  - 480 feed-forward gates
  - 3 pointer resets

  The unrolled 5 B build/c kernel is 53,413, so the rolled body costs 4.2% more ops.
- **Other designs priced at r39:**

  | design | time_log2 |
  |---|---:|
  | schedule loop from 23 | 124.517 |
  | schedule loop from 15 | 124.562 |
  | full unroll at 36 B | does not fit (2.05 MB of code; table < 0) |

- **Every instruction is 36 B**, the convention of the filed packed r39. Nothing uses the 5 B code convention.
- **Every added operation is counted:**
  - each load, store and NOT is one op;
  - each constant plane set into a loop register is one op;
  - each loop iteration costs 4 ops: two pointer adds, compare, branch;
  - each batch costs 3 ops to reset the pointers.

  The program has no dispatch and no interpreter.

## 3. Checks at the minutes scale (each run twice)

- **Function check.** `verify.py` executes the counted gate networks: straight phase, loop bodies run for their iterations, epilogue. It compares all 256 lanes with the bsha scalar 39-step digest (254 random inputs, all-zero, all-ones).
  - r39, all 4 designs: seed 1 gives 0 mismatches, seed 2 gives 0 mismatches.
  - r41 (4 designs) and r64 (7 designs), seed 1: 0 mismatches.
  - Files: `run_verify_*.out`.
- **Negative controls** (`negctl.py`): one setup-constant bit flipped gives 64/64 mismatches; one W' plane complemented gives 64/64 mismatches.
- **r64 scalar** against hashlib SHA-256 on 200 messages: 0 mismatches. This confirms the extended K table.
- **Known answer for the v2 ledger.** `bsrho_v2.py` is a copy of B3R3V2's pivotv2 code. Run unchanged, it gives 124.83985 against the filed 124.83986 (run 1, `run1_v2check.out`).
- **The v1 build/c ledger** reproduces 124.27485 against the stated 124.27486.
- **Final r39 v2 number** (20,000 panels), two independent runs: 124.50211 / 124.50211 at kappa 13. Kappa 14 gives 124.50238 and kappa 15 gives 124.50401. Files: `run1_` and `run2_v2_R39_p20000.out`.
- **Cross-check with the v1 frame** (build/c ledger, `run1_price_R*.out`): r39 gives 124.46365, against packed v1 124.84811 (368d1718), so -0.384. Lemma 2 v2 costs this design +0.039.

## 4. Premises and sensitivity

**Register file (score-critical).** The best r39 design declares 1,024 registers of 256 bits. The B3R3BS precedent was accepted with this premise (0a9640ed: "1,024-register premise accepted"); 3ff7e687 was refused for a 2,192-register file stated as an unsupported convention.

The need was measured by creation-order liveness, which is an upper bound: 966 including 16 for the search state at r39, and about 561..720 at r40..r64. Spill sensitivity (Belady, under v2, best design per file, `run1_regprice_*.out`):

| declared file | best design | ops / eval | time_log2 | gain vs 124.854 |
|---:|---|---:|---:|---:|
| 1,024 | straight schedule | 217.3 | 124.50211 | -0.352 |
| 512 | schedule loop from 23 | 233.3 | 124.51451 | -0.339 |
| 256 | schedule loop from 23 | 249.2 | 124.63780 | -0.216 |
| 128 | schedule loop from 15 | 293.8 | 124.83339 | -0.021 |
| 64 (as filed packed) | schedule loop from 15 | 334.6 | 125.07031 | +0.216 |

The lever needs at least about 256 registers. Spill counts are approximate: the loop-carried layout is assumed to match between iterations.

**Lemma 2 v2 port.** The plan and loss are B3R3V2's. They are generic in the 256-lane DP search (s1 32, W 90, Sb 2^48, CMAX 2, EPS 1e-3). Two things were not run:
- Appendix A, the exact-rational certification of P_lower >= 0.39. P_lower is the float plan target.
- The 7-byte key's false-match term for the 10 B entry row (about 1e-7, negligible).

**Inherited constants.** The handler and event charges, the recovery circuit (2,214 + 64 per recovery batch), the generator cost and the setup cost are those of r39 build/c (bsha.py). build/c is our unfiled bit-sliced 5 B line, so these constants have never been reviewed. The q mask of the rolled network differs from build/c's, which changes at most 8 XORs per recovery batch.

**Generator memory.** The setup phase fits on paper: code 839 KB + counters + build/c's generator image and scratch (about 127 KB) = about 982 KB. The rolled generator has not been ported to C or measured in the 1 MiB VM.

**Quadrature.** Rows at 2,000 panels differ from 20,000 panels by about 1e-4 (r39 kappa 14: 124.50241 against 124.50238).

**Not built:** the actual 36 B encoding, register allocation with pinned loop-carried registers, the shipped experiment program, organizer intake and toy runs.

**Small levers left (not priced):**
- A majority polarity per W' bit instead of upright would remove part of the 541 NOTs (at most -0.01).
- Rolling the packed recovery circuit would free about 1,100 instructions (40 KB, +1,500 table entries): about -0.03 (estimate).

## 5. What a package rebuild needs (per row; r39 first)

1. **Program.** Port the `rolled.py` builder into a shipped `bsha`-style experiment:
   - the straight phase, the 4-step compression loop and (r40+) the 8-word schedule loop;
   - the K plane polarities for the knob;
   - an allocator that pins the loop-carried rings;
   - a selftest that executes the allocated 36 B code against the scalar digest and the organizer reference (as `verify.py`, plus the organizer digest).
2. **Ledger.** Replace build/c's v1 plan and loss with the v2 functions of B3R3V2, which `v2price.py` already wires in. Use kappa 13 at r39 and 13..14 elsewhere, with the machine constants of section 2. Then add the integer certificate (`final.py`) and the Appendix A exact-rational P_lower >= 0.39 certification.
3. **Generator.** Port the generator to C, measure it in the 1 MiB wasm VM (pages, ops, scratch), and charge the measured cost.
4. **Proof text.** State the machine as cost-model prices:
   - 36 B instructions;
   - 1,024 registers declared, with the spill table above;
   - every load, store, NOT, set and loop op charged.

   Also include the register-file sensitivity table, the H1 premise as in 3c1d7f68, and credit for the build/c bit-sliced work and B3R3V2's Lemma 2 v2.
5. **Checks and filing.** Organizer intake in Docker at n=18, plus toy runs at width 30..40. Prefile and rulecheck. Then a new slot, because this is a new line and must not overwrite 3c1d7f68. Then the owner's go.

Estimated effort: r39 about 3-4 h for the first row. Factory rows 40..64 then about 10 min each, since only R and the schedule-loop start change.

## 6. Tool call refused

A PowerShell call was blocked with "Remove-Item on system path '*' is blocked". It was a here-string edit of `rolled.py` whose Python text contained `del KNOBS[:]`. Nothing was deleted, and the file was unchanged by that call. I made the same edits with the Edit tool and used `KNOBS.clear()` instead.

## Files (./research/levers_wave1/s256r39/)

- `rolled.py`: counter and builder.
- `verify.py`: function check.
- `negctl.py`: negative controls.
- `price.py`, `price2.py`: v1 ledger.
- `v2price.py`: v2 ledger.
- `regprice.py`, `spill.py`: register sensitivity.
- `final.py`: exact ledger and certificate.
- `bsha.py`: copy of r39 build/c.
- `bsrho_v2.py`: copy of blake3_r3/pivotv2.
- Outputs: `run*_*.out`, `price_R*.json`, `v2_R*_p*.json`.
