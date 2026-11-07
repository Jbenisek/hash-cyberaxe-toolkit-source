# backward37: chi37 rows 21 down to 16, worked backwards from what rows 22+ need

Date 2026-10-12, 01:25 to 03:24 MDT. All code is ours. Nothing was submitted. I stopped only my own processes and used at most 6 threads (machine load was 15 to 43).

Labels: PROVED means algebra, or an exhaustive count over the stated space. COMPUTED means a Monte Carlo or sampled count. GUESS means not tested.

## Verdict

**A NEW LEVER (COMPUTED): the row-16 selector freedom, coupled to the row-18/19 parities.**

- E16[23] no longer needs to be 0. It joins the four-pattern parity group through **E16[23] ^ E19[29] ^ E18[1] ^ E18[5] = 0**.
- The '+' relation **E16[24] = E17[24]** is not needed at all.
- **Measured gain:** q3 = -71.4238 with these freedoms (relaxation `R16x`), against -71.9727 for the four patterns (R1). That is **+0.549 bit over R1** and +2.541 bit over the printed cells (-73.9646).
  - Same traillab pipeline, same 4 seeds, np 8192.
  - Seed sd 0.047 / 0.050, so the 95% interval of the difference is about ±0.07.
- **Row 16 relaxed alone (`R16only`) gives no gain:** -73.9507, i.e. +0.014 ± 0.1. The freedom exists only together with the row-18/19 parities.
- **Real collisions:** leaves that break the printed row-16 cells give real 37-step colliding pairs. They were checked against the independent reference compression (below).

Rows 21, 20, 19 and 17: the exact requirement equals the printed conditions, so the gain is 0. Row 18 reproduces the known four-pattern find exactly.

## The requirement at the end of row 21 (R21) and why it is exact

- dA18 = dA19 = dA20 = dA21 = 0.
- dE19 = dE21 = 0.
- dE18 = -2^24 - 2^23 + 2^15 (modular only).
- E20: the XOR difference is exactly bit 29 and the modular difference is -2^29, which forces E20^x[29] = 1.
- E21^x[29] = 0.

**PROVED (step equations).**

- E18 is read by rows 22+ only as E_{t-4} in row 22, so only its modular difference matters there.
- E20 is read in row 22 through CH(E21,E20,E19), which needs E21 = 0 on the XOR bits of E20. It is read in row 23 through CH(E22,E21,E20), which needs E22 = 1 on those bits. It is read in row 24 as E_{t-4}, modular.
- So any other XOR pattern of E20 would add downstream conditions. R21 keeps the printed one.

The E-driven property is used for pruning, and it is exact. dE_t and dA_t do not depend on E_t^x. For example, dA17 = dE13 + dCH(E16,E15,E14) + dW17 + dS0(A16) + dMaj(A16,A15,A14). So the difference requirements of row t+1 are checked as soon as E_t is set.

**Derived, PROVED necessary:**

- dA17 = 0, from row 21: dA21 = dE21 - dA17 when A18..A20 are equal.
- dA16 = -2^29, from row 20: dA20 = dE20 - dA16.

Rows 16..21 depend only on W15 (one of the 32 l), the anchor and E16..E21. The late words W6/W7/W8 and the solved W0..W5 move only rows ≤ 10 and the chaining value (`tl_build`). So rows 4..10 do not couple to the questions asked here. Rows 22+ do couple, through W20 into W22. That coupling is measured in the q3 runs.

## Method (tool `back37.c`)

S(r) = Pr[cells on rows < r, R21] / Pr[cells on rows < r, printed cells on rows r..21]. Both are counted over the same uniform measure.

- The prefix comes from traillab's SMC, a frozen copy in `lib/`.
- On each base, the relevant bits of E_r..E_21 are enumerated **exhaustively**: cell bits, S1 taps of the difference bits, CH selectors, carry neighbours, and for E16 the whole word.
- The other bits get a uniform random fill.
- The ratio of sums carries a cluster interval over bases.
- The affine hull over GF(2) of all R21 leaves gives the relations that hold on **every** leaf. These are the "exact requirement" lines below.
- A built-in check counts cell leaves that fail R21. It is 0 in every run.

For row 16, E16 is enumerated over all 2^32 values, keeping those with dA17 = 0. The survivors split into two strata:

- A: row-16 cells hold.
- B: row-16 cells fail.

Each stratum is sampled (384 to 1024 per base) and expanded exactly over E17..E21.

## Per row (backwards)

Gain is the step log2 S(r) - log2 S(r+1).

| row | printed conditions | exact requirement (on the rows-22+ event) | gain | couples to | label |
|---|---|---|---|---|---|
| 21 | E21[29]=0; A21, E21 equal | E21[29]=0, nothing else of E21. Row 21 forces dA17=0 and dE17 + dS1(E20) + dCH(E20,E19,E18) = 0 | 0 (S(21)=1, 8/8 bases) | 17 (dA17, dE17), 18, 19, 20 | PROVED |
| 20 | E20 u29, [24]=1, [23]=0, [15]=1, [11]=0, [10]=0, E20[2]≠E20[16] | Identical: hull = cells hull (7 forced bits plus the parity E20[2]^E20[16]=1). Unique signed solution of the row-21 equation: S1(E20) signs at bits 23, 18, 4 all +, selectors [24]=1, [23]=0, [15]=1, and E19[29]=E18[29] | 0 (S(20)=1, 128/128 leaves) | 16 (dA16=-2^29, dE16), 17, 18, 19, 21 | algebra PROVED; enumeration COMPUTED |
| 19 | E19[29]=1, [24]=0, [23]=0, [18]=1, [15]=0, [4]=1 | Identical given E18. The row-20 CH(E19,E18,E17) must kill every E17/E18 difference: no nonempty subset of {-2^24,-2^23,+2^15,-2^18,-2^4} sums to 0. Only E19[29] is a parity with E18[29] (row-21 CH at bit 29). dA19=0 needs A17[29]=A18[29] (Maj) | 0 (S(19)=1, 64 bases, 32768/32768) | 18 (parity), 20, 21; A16/A17/A18 bit 29 | PROVED (subset sum) / COMPUTED |
| 18 | 9 values, signs 24u 23u 15n, E18[6]≠E18[19], E18[2]=E18[20], A17[29]=A18[29] | The row-19 sign equation dE15 + dS1(E18) + dCH(E18,E17,E16) = 0 has 4 solutions, the **6 parities of R1, exactly** (hull). E18 may also take the XOR patterns {24,23,16,15} (0.74%) and {24,23,17,16,15} (0.01%). E18[2]=E18[20] and E18[6]≠E18[19] stay | **+2.009** (S(18)=4.025 ± 0.227, 1024 bases, [1.93, 2.09] bits) | 19, 21 (E18[29]=E19[29]), 17/16 (row-19 CH) | COMPUTED; reproduces K4 |
| 17 | 7 values, signs 18u 4u, E17[0]≠E17[13], E16[24]=E17[24], E16[15]=E17[15], A15[29]=A17[29] | Given row-16 cells, every printed E17 bit is forced (hull). dA17=0 is necessary | ~0 (S(17)=4.045 on a partial 65 bases, 38 nonzero, vs S(18)=4.025) | 13..16, 18, 19 | COMPUTED |
| 16 | 9 values ([30]=0, [23]=0, [22]=0, [18]=1, [17]=1, [12]=0, [11]=1, [9]=0, [7]=0); '+' relations with E15[4], E17[24], E17[15]; A16 two-bit ×6 | On exact leaves the **only** printed conditions that fail are **E16[23]=0** (54.6% of leaves) and **E16[24]=E17[24]** (51.5%). No A16 two-bit relation ever fails. New hull relation **E16[23] ^ E19[29] ^ E18[1] ^ E18[5] = 0**; E16[24]^E17[24] is free. Rows 16..17 XOR patterns are unchanged (dA16 bit 29, E17 {18,4}). E18 pattern {24,23,16,15} rises to 1.4..4.9% | S(16) = 7.21 ± 2.30 (2.85 bits [2.29, 3.25], 8 bases), i.e. **+0.85 over row 17, wide**. The q3 measurement of the explicit relaxation `R16x`: **+0.549 ± 0.07 over R1** | 17 (E17[24]), 18/19 (parity group), 12..15 | hull and tally COMPUTED; q3 COMPUTED |

Why row 16 couples: row 19's CH(E18,E17,E16) at E18's difference bits 24 and 23 emits ±2^24 / ±2^23 whenever E17 ≠ E16 there. The printed trail blocks this with E16[23]=0=E17[23] and E16[24]=E17[24]. The exact event lets these terms through and absorbs them in the row-19 signed sum, using different S1(E18) sign solutions. The flip of E18[5] in the parity group is that absorption. So the four-pattern find is one case of a larger row-19 solution set, whose selectors sit in rows 16 and 17.

An "empty" l comes back. One base (W15 from the 32 l, `r16_full` base 1) has **no** E16 that satisfies the row-16 cells, yet it reaches R21 with about 4.7M (E16..E21) leaves. Our earlier statement, in ATLAS37 E8, was that 4 l are empty, killed by row-16 conditions. That statement holds for the cells, not for the exact event. This is consistent with ATLAS E7: the A16 two-bit relations are still necessary, because none of them fails here.

## Validation

- **Real 37-step collisions from the leaves.** `back37v ... 400000` captures a leaf, rebuilds the pair through the full pipeline (late words redrawn, real expansion) and checks the outputs with the independent `tl_compress_ref`.
  - The leaf failing printed row 16 (E16[23]) and the '+' at E17[24]: 33 collisions in 400,000 late redraws.
  - A cell leaf, same base: 33 collisions in 400,000.
  - A four-pattern leaf: 32 collisions in 400,000.
  - Example, from the row-16-failing leaf. Equal outputs `ac86069b a5f5a876 4f80aa74 c9f45d08 12edd57c 3303c52b 8d1936fe 8341e7e4` from CV `b5b09629 99f8b08f 771d7af8 e7c84e52 82a81a94 99a019b3 3188c5fc da560b04`.
    - Mx `269f46ae 51d5f12e d2c6ea96 2899641a 72ba89ab 8ba11177 8aecf29a 16de5403 bc454716 6d1a90dd faa1d3e0 56aed439 cc2dbbc2 dd2ba0fc bd1d3f7b fdb41a80`
    - My `... aaecf29a 129e5c03 9c454716 681b8277 faa9c7e0 ... b95d377b ddb41a80`
    - The full words are in `out/r16_verify2.txt`.
  - These are semi-free-start pairs: the CV comes from the backward rebuild. They show the relaxed rows are real, not that a full collision exists.
- **Known answers reproduced.**
  - S(18) reproduces the K4 parities line for line.
  - q3 for cells is -73.9646 and for R1 is -71.9727, equal to the README's K7 and K4 values on the same seeds.
  - Cells-imply-R21 failures: 0 in every run.
- **R16x on the published pair.** E16[23]=0, E18[1]=1, E18[5]=0, E19[29]=1 give parity 0, and the rest is R1, so R16x holds (PROVED).

## Limits (not tested or not exact)

- **S(16) estimate.** It rests on 8 bases with sampled strata, and its interval is wide. The q3 number for the explicit `R16x` (+0.549) is the figure to use.
- **What R16x leaves out.** The exact set is not affine. About 1.4..4.9% of leaves use the E18 XOR pattern {24,23,16,15}, which R16x excludes. A further +0.3 bit (S(16) 2.85 against R16x 2.54) is **GUESS** level until measured.
- **Random fill.** E bits outside the enumerated masks, mainly the high bits that carry into A17[29] and A18[29], are random fill, not enumerated. This makes the per-base counts COMPUTED, not PROVED. In the rows-17 run, 27 of the 65 bases were zero.
- **The S(17) run was stopped** at 65 of 512 bases (machine load). The ratio comes from the base lines in `out/r17_partial_seed2.txt`. The hull comes from the 8-base run `out/r17_t.txt`.
- **R21 keeps the printed E20 XOR pattern.** Alternative E20 patterns would cost extra E21/E22 bits downstream and were not counted.
- **Filing work not done.** No package, no proof text and no solver re-run of the full 37-step system with R16x. The W22/W24 coupling to rows 16..21 is included only through q3 (rows 22..36 cells rate), not as a separate exact count.
- **The shared traillab `src/smc.c` was being edited by another job** during this run (W16 statistics). I built from frozen copies:
  - `lib/`: our prefix SMC plus `traillab.c`.
  - `lib_full/` and `tl_snap`: a snapshot that compiles and reproduces K4/K7 on the same seeds.

## Next steps (proposed)

1. Run q3 for R16x on 4 more seeds, plus a check that every R16x prefix is an R21 state (window `--rows 16 21 --event state`).
2. Add the E18 {24,23,16,15} pattern as a `sym` variant and measure it.
3. Work back one row further, to the row-15/W15 choice, with this tool. That is per-l counts with rows 16..21 exact.
4. Record the lever in research/LEVERS.md once the owner agrees.

## Files

All files are in `research/retest/backward37/`:

- `back37.c`, `build.sh`, `dump.c`
- `q3runs.sh`, `lib/`, `lib_full/`
- `out/r18_big.txt`, `out/r16_full.txt`, `out/r16_verify2.txt`, `out/q3runs.txt`, `out/r17_partial_seed2.txt`, `out/r19.txt`, `out/r17_t.txt`
- The rows-20 and rows-21 runs are in this report; they were printed to the terminal and not saved to `out/`.

Usage: `back37 CHI R nbase seed threads noderive v16full K16 stage18 lean verifyN`.
