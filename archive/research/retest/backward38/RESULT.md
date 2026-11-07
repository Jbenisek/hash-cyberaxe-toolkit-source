# backward38: chi38 rows 22+ worked backwards to row 16 (2026-10-12, 01:25-03:15 MDT)

Tool: validated traillab (`research/tools/traillab`, 53/53 known answers), plus `wcount.c` here (our code, exact 2^32 counts).
Every sample is a real pair: 16 message words per member, all W16+ from the real expansion, all rows from the real step.
Nothing held fixed, nothing submitted, only my own processes, 6 threads.
Labels: PROVED (exact count or algebra), COMPUTED (sampled), GUESS.

## 1. Where the differences end

**Last message-difference word: W25** (dW25 = +2^29, cell `==n===...`). PROVED (`backward_16_37.txt`, schedule part):

| word | dW | how |
|---|---|---|
| W23 | fe7f8000 | dW16 + ds0(W8) + dW7; ds0(W8) is constant on W8's cell (G). PROVED |
| W24 | 0 | constant. PROVED |
| W25 | 20000000 | **depends on the value of W23**: s1(W23+fe7f8000) - s1(W23) = 50005f30 |
| W26, W28, W29, W33..W37 | 0 | constant. PROVED |
| **W27** | 0 | **depends on the value of W25**: s1(W25+2^29) - s1(W25) = 00081400 |
| W30 | 0 | dW23 + ds0(W15) = 0, constant. PROVED |
| **W31** | 0 | **depends on the value of W16**: s0(W16+e0000000) - s0(W16) = 03bff800 |
| W32 | 0 | dW25 + dW16 = 0, constant. PROVED |

As for dW26 on chi37, the rows after the last difference word are not free. Two later words must cancel: **dW27** (through s1(W25)) and **dW31** (through s0(W16), a row-16 word).

**Live state differences after row 21** (cells): E18 (n18 u4, modular 0003fff0), E19 (n24 n23 n15, 01808000), E21 (u29, e0000000). A21..A18 and E20 carry no difference. They are cancelled as follows:

- **Row 22.** E18 leaves through X_E = dS1(E21) + dCH(E21,E20,E19). Without two-bit conditions the model gives Pr 1/2. The deciding bit is the sign of S1 output bit 23, which is set by E21[2] xor E21[16], i.e. the printed two-bit condition **E21[2] = E21[16]**. The coin is therefore paid at row 21. COMPUTED: dropping that condition from the prefix halves the EXACT hits (10347 -> 5292) and leaves P(prefix and EXACT) unchanged (-99.626 vs -99.659).
- **Row 23.** E19 is cancelled by dW23. This needs **E22[29] = 0** (CH would pass E21's bit-29 difference). PROVED necessary: otherwise dE23 = ±2^29 != 0, because dW23 and dE19 are fixed.
- **Row 24.** Needs **E23[29] = 1** (CH would pass E21[29]). PROVED necessary the same way: otherwise dE24 != 0 with dW24 = dE20 = dA20 = 0.
- **Row 25.** E21 is cancelled by dW25 = +2^29, which needs the W23 value requirement. After row 25 the state is equal.

**Corrected reduction:** collision after 38 steps <=> (state equal after row 25) AND dW27 = 0 AND dW31 = 0.

- Forward direction PROVED: every later dW is then 0, and the step is invertible.
- Reverse direction COMPUTED: 84,730 EXACT samples (8 seeds x 2^28), 0 with the predicate but not EXACT, 0 with EXACT but not the predicate (`run_main22.txt`, `--equiv 25,27,31`). The gauge run gave the same with `--equiv 25,27` (342/0/0).
- dW31 = 0 holds whenever W16 is in its cell: the cell's two-bit conditions W16[1]!=W16[12], W16[8]=W16[25] and W16[14]=W16[18] are exactly the s0 output signs. That cost is already paid in the prefix, at row 16. On this head the 32-word row-16 list fixes W16, so `dropx2 W16` changes no sample (COMPUTED, identical counts).

## 2. Exact counts per word (PROVED, `wcount.c` -> `wcount.txt`, 2^32 each, x = member printed second)

| word | requirement | exact set | printed cell | cell inside exact | exact/cell |
|---|---|---|---|---|---|
| W23 | dW25 = 2^29 | 9,830,400 = 75 * 2^17 | 4,194,304 = 2^22 | yes | **75/32 = 2.34375** |
| W25 | dW27 = 0 | 293,601,280 = 35 * 2^23 | 268,435,456 = 2^28 | yes | **35/32 = 1.09375** |
| W16 | dW18 = 0 alone | 293,601,280 | 33,554,432 = 2^25 | | 8.75 |
| W16 | dW31 = 0 alone | 287,309,824 | 2^25 | | 8.5625 |
| W16 | **both** | 33,832,960 | 2^25 | yes | **1.0083** (+0.012 bit) |
| W8 | dW23 (s0) | 68,157,440 | 2^26 (= G) | yes | 1.015625 (more variants, not more probability) |

- The W25 two-bit conditions W25[4]=W25[6], W25[22]=W25[31] and W25[20]=W25[27] are exactly the signs of the three s1 output bits 19, 12 and 10. They are needed for dW27 = 0 and are not decoration.
- The W23 numbers are the same integers as chi37's W22 (75 * 2^17). The W25 number is 35 * 2^23, where chi37's W24 has 17 * 2^24.

**Uniform model, rows 22..37 (PROVED under the model):** take W23 and W25 independent and uniform (W25 = s1(W23) + W18 + const with W18 uniform), take E22[29] and E23[29] uniform, and take rows <= 21 as in the cells.

- q_cell = 2^-1 (E22[29]) * 2^-1 (E23[29]) * 2^-10 (W23 cell) * 2^-4 (W25 cell) = **2^-16**.
- q_event = 2^-2 * (75*2^17/2^32) * (35*2^23/2^32) = 2625 * 2^-26 = **2^-14.6416**.
- **q_event/q_cell = 2625/1024 = 2.56348 (+1.3581 bits).** Integer identity: 9830400 * 293601280 * 1024 = 4194304 * 268435456 * 2625.

## 3. Real pipeline (COMPUTED; R38M model: W6 random, W7 in F7, W8 in G, E16 from the 32-word list, E17..E21 E-driven)

| run | samples | EXACT/cells (95%) | log2 |
|---|---|---|---|
| `run_main22.txt` seeds 31..38, np 8192, mt 32768 | 8 x 2^28 | 2.58733 +- 0.02576 | +1.371 |
| `confirm/base.txt` seeds 51..58, same size | 8 x 2^28 | 2.56836 +- 0.02465 | +1.361 |

- Both runs contain the uniform 2.56348. Combined, about **2.578 (+1.366 bits)**.
- The real-pipeline q_cell for rows 22..37 is 2^-16.0, as the model predicts. log2 P(rows 6..37, cells) = -101.006 and -100.994, which matches the quoted R38M q3 of 2^-101.05.
- The split by word (run_main22, pooled):
  - noW23/cells = 2.3541, the W23 factor (uniform 2.34375);
  - EXACT/noW23 = 2.5873/2.3541 = 1.099, the W25 factor (uniform 1.09375);
  - W25x2/cells = 8.025, so the three W25 two-bit conditions behave as 3 fair bits on the real pipeline.
- E22v/cells, E23v/cells and W23x2/cells are all exactly 1.00000 (gauge run). Those conditions are implied by the other cells.
- Earlier small readings (README: 2.85 +- 0.44 for rows 22..37, 2.27 +- 0.41 for rows 23..37) are consistent with this.

**Lever for r38: the exact event over the cells, x2.56 (uniform, PROVED) / x2.578 (real, COMPUTED), +1.36 bits on q3. It is the chi38 counterpart of chi37's 1275/512.**

Note: HANDOFF records "D165 r38 EX x1.118" and a W25-carry factor of 1.0655. Those numbers are much smaller than this ratio. They probably measure a different reference event, such as a partial relaxation already counted elsewhere (GUESS). Before any stacking, compare the definitions. Section 4 says what this run measures.

## 4. Working backwards, rows 21 -> 16

Method. The window stays at rows 22..37 with the true event (zero output difference after step 37). Only the prefix conditions are relaxed (`--prefix-relax`). The quantity compared is log2 P(prefix_R and EXACT) = log2 P(rows 6..21 under R) + log2 rate(EXACT). A relaxation is a gain only if this rises. The script is `sweep.sh`, with 4 seeds x 2^26 per line and np 4096, giving `sweep/*.txt`; `parse.sh` makes the table.

| prefix relaxation | log2 P(prefix & EXACT) | vs base | reading |
|---|---|---|---|
| base (cells) | -99.659 (sd 0.053) | 0 | |
| E21 value bits (01808c00) | -99.645 (sd 0.32) | 0 | needed (EXACT hits 332 of 10k) |
| E21[2]=E21[16] dropped | -99.626 | 0 | needed: the row-22 coin |
| E20 value bits (21848010) | -99.700 (sd 0.21) | 0 | needed |
| **E19 value bits (E19coset, 30040e32)** | **-98.382 (sd 0.17)** | **+1.28** | **not all needed** |
| E18 value bits (40c21220) | -99.807 (sd 0.43) | 0 | needed |
| E17 value bits (40c21a80) | -99.762 (sd 0.42) | 0 | needed |
| E16 values, E16/E17 two-bit, W16 two-bit, A15 two-bit | identical to base | n/a | fixed by the 32-word list or duplicated by '+' relations, so not testable this way |
| E18 / E19 / A16 / A17 / A18 / A19 two-bit | -99.62 .. -99.68 | 0 (within 0.04) | needed |

**E19 coset confirmation:** 8 fresh seeds at 2^28 (`confirm/E19c.txt`) gave -98.660 (sd 0.245) against base -99.633 (sd 0.032), so **+0.97**. Over all 12 seeds: E19 relaxed -98.567, base -99.642, so **+1.07 +- 0.08 bits** (seed se).

- The relaxed prefix has 7x the seed spread, so this log-mean is biased low. The true value is probably nearer the 4-seed reading, but that is not shown.
- It agrees with job104's E19 coset: point estimate 2.342 (+1.23), credited 8/5 (+0.68). Here it is measured to the real 38-step collision, on random heads (SMC prefixes), not only the published head. That closes job104's "not established: other prefixes" for the probability side.
- It stacks with the rows-22+ lever on the same samples: cells -100.99 -> EXACT -99.64 -> EXACT with the E19 coset -98.57, i.e. **about +2.4 bits total over the quoted q3** (COMPUTED).

### E19 and E20 together: the chi38 "four patterns" (COMPUTED, new)

E20 values alone give no gain, and E19 alone gives about +1.0. Relaxing both gives about twice that:

| prefix relaxation | seeds | log2 P(prefix & EXACT) | vs base (-99.64) |
|---|---|---|---|
| E19 + E20 values (`dropv E19 30040e32 ; dropv E20 21848010`) | 41..44 | -97.270 (sd 0.33) | +2.37 |
| same, default size (np 2048, mt 4096) | 61..64 | -97.718 (sd 0.19); base on the same seeds -99.639 | +1.92 |
| same | 71..78 | -97.555 (sd 0.31) | +2.09 |
| **E19 values dropped, E20[29] replaced by the tie E20[29] = E19[29]** (`dropv E19 30040e32 ; dropv E20 20000000 ; lin E20[29]^E19[29]=0`) | 71..78 | **-97.713 (sd 0.25)**, 2x the EXACT hits | **+1.93** |
| E18 + E19 + E20 values | 61..64 | -98.185 (sd 0.40) | +1.45 (E18 values are needed) |

**Mechanism.** It combines job104's patterns with an exact enumeration (`hist_E19E20.txt`: 64 SMC prefixes, E19's 9 value bits x E20's 6 value bits, every other coordinate held).

- Rows 19..21 relaxed pass for exactly 8 combinations: the 4 E19 patterns (job104's 470, 307, 103, 130) x E20[29] in {0,1}. E20 bits 18 and 4 are always 1, and bits 24, 23 and 15 are always 0.
- job104's dying coset {103, 130} has E19[29] = 0. It dies at row 22 only because the printed E20[29] = 1 makes CH(E21, E20, E19) pass E21's bit-29 difference when E20[29] != E19[29].
- With **E20[29] = E19[29]** all four E19 patterns go through, against 1 printed. That is up to 2 bits, and **+1.93 is measured** to the real 38-step collision.
- This is the exact counterpart of chi37's four patterns (E18/E19 8 bits -> 6 parities, +1.99).

The derivation "dies at row 22 <=> E20[29] != E19[29]" is GUESS + COMPUTED. It fits the CH selection at bit 29 and the measured 2x. It is not written as a proof here.

**Stack, all COMPUTED on the same pipeline, exact event at step 37:**

- q3 under the cells: 2^-101.00
- with the exact event over rows 22..37: 2^-99.64 (**+1.36**)
- with the E19 four patterns and the E20[29] tie in the prefix as well: 2^-97.71 (**+1.93**), or 2^-97.56 with every E20 value dropped
- **total about +3.3 bits over the quoted q3 2^-101.05**

## 5. What is new, what is old

- New, PROVED: dW31 depends on W16 (s0); the exact counts 35 * 2^23 for W25 and 1.0083 for W16 jointly; the uniform ratio 2625/1024; the necessity of E22[29] and E23[29]; the reduction with dW27 and dW31.
- New, COMPUTED: real-pipeline EXACT/cells 2.578 in two independent 8-seed runs; the equivalence 84,730/0/0; the backward sweep (only E19, and E20[29] through it, carry slack); **the E20[29] = E19[29] tie that revives job104's dying coset (+1.93 over base, vs about +1.0 for the E19 coset alone)**; stack EX x four patterns about +3.3 bits.
- Old, re-confirmed: W23 bits 13,17,26 are not free (W23x2 and W23 value relaxations give 1.00000); job104's E19 coset.
- Not a lever: W16 relaxation (+0.012 bit at most, PROVED); W8 beyond G (+1.6% variants, no probability).

## 6. Limits / not done

- All sampled numbers are SMC estimates. Seed spread is the honest error; per-seed cluster intervals are narrower.
- The E19 relaxation adds conditions-free patterns at row 19. The attack must then sample row 19 without the 9 value bits (or with the 2-of-4 coset test as in job104). Its cost per candidate is not priced here.
- Row 16 cannot be relaxed in this model (32-word list on this head). The A-row two-bit conditions were tested by dropping them, not by replacing them with an exact requirement.
- The E19/E20 lever has 4..8 seeds per line and seed sd 0.25..0.33 bit. A filing needs a larger preregistered run (e.g. 32 seeds x 2^28) and a priced row-19/20 test (the 4 patterns as 6 parities plus the E20[29] tie).
- The 8-seed 2^28 E19E20 confirm run was stopped by me after 1 seed (too slow at this load); replaced by the 4- and 8-seed lines above.
- Not tested: rows 17/18 with an exact requirement in place of value drops (dropping their values loses EXACT, so they are needed as a block), and A-row conditions as requirements.
- Not checked against D165 (x1.118) or the 1.0655 W25-carry factor; compare definitions before stacking.
