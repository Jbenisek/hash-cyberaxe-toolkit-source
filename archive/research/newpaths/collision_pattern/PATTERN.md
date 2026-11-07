# Do the found collisions follow a curve? (research only, 2026-10-08)

**No. Nothing in the search coordinates predicts where the next collision is.** The collisions do have structure,
but all of it is the collision condition that the exact model already counts and that the levers already use.

## Data
- **Collected:** 9,300 distinct real collision pairs. Every one was re-hashed by an independent Python tree hash
  (`counter/toy/verify_tree.py`): 0 failures.
  - Server task 5 (W8: 6,276; W10: 1,832) and its local runs (411 new pairs; 62 duplicates of server runs dropped).
  - Counter toy (W8: 67 filed, 251 ctrH, 54 ctrAll).
  - Filed layout with X14 (409 pairs). Only its search order was tested, because its construction is not in `feat.c`.
  - The 826-collision GPU run (`~/hashsmash/toy/gpu8_172817.txt`) saved only per-seed counts. It has no pairs.
- **Parameters recovered:** for 8,891 pairs the parameters were rebuilt with the runs' own code (task-5 `toy.h` and
  `tl_lines.inc`). These are seed words, outer step, X2, member, E1.d1 and t. The rebuilt words equal the saved
  message A in 8,891 of 8,891 cases, and every rebuilt trial collides.
- **Null sets:** 20 random trials from each collision's own run, built by the same construction and with the same
  t ≠ 0 filter (N0). A second set, N1, is weighted by the exact model's `mass[member][E1.d1]`. A third set, N2, is
  weighted by the exact model given (member, E1.d1, w8), computed by `feat` P mode; the self-check against the mass
  table is exact. A pseudo-hit sample taken from the null gives the multiple-test spread (CAL).

## Results (`results.txt`)
| Test | Result |
|---|---|
| Search coordinates (w5, S9, X2, member) vs N1 | max \|z\| 1.65 over 29 bits; 2.94 over 406 bit-XORs; Bonferroni p = 1. The same holds at W10 vs N0 (p = 0.3) and in the counter toy (p = 1). |
| GF(2) rank (search coordinates and message bits) | hits = null in every set (29/29, 88/88, 35/35, 110/110). No exact linear relation. |
| Message words except w8, vs N1 | max \|z\| 2.54 over 80 bits (p = 0.88). Modular a±b and a^b: Bonferroni ≥ 0.02 without w8 and y4. |
| Run seeds (C0.c1, C0.d1, D3.d1, S15) vs per-run counts | W8: Bonferroni p = 0.29. W10: p = 0.8. Dispersion 0.99 and 0.95. |
| Position in run, same outer step, gaps | position uniform (KS p 0.77, 0.64, 0.81). 0 pairs share an outer step (0.01 expected). Close pairs z +0.7. |
| Two-parameter relations (u, X2, member, S9, t, d1) | rho z within ±1.7. Quadratic R² beyond the null at most 0.001 (filed sets) and 0.012 (counter toy, 305 hits). One counter-toy 2-D p of 0.004 (8 pairs tested, so ≈ 0.03); it does not appear in the 6,754 filed hits. |
| Score on search coordinates | held-out AUC 0.493 ± 0.012 vs N1 (W8) and 0.506 ± 0.024 (W10). |

**What IS structured is the known collision condition:**
- **Exact-model cell.** All 6,754 W8 filed hits and all 305 counter hits lie in (member, E1.d1) cells of nonzero
  mass. Only 6.5% of random trials do.
- **Agreement with the model.** The member split matches N1 (χ² p = 0.28) and the cell-mass distribution matches
  N1 (KS p = 0.93).
- **The w8 bias.** w8 (E3's message word) is biased: bit 1 has z = +11 vs N1, and w8±y4 has p ≈ 1e-60. Against N2
  the bias vanishes: max \|z\| 2.6 over 88 bits, modular tests p ≥ 0.008. The model accounts for it completely.
- **Internal words.** h1, Y9, Y14 and a2 are biased (z up to 52). They are the inputs of the condition itself.

**One weak, unexplained signal.** In the W8 server runs, two hits of the same run fall in the same quarter of the
run about 10% more often than chance (z +3.7 and +2.7 for the two series; hit span z −2.6 and −1.9). It does not
appear at fixed 2^12 to 2^16 blocks, not in the W8 local runs (z −0.2), not in the counter toy and not at W10
(z +0.1).

## What it would buy at 32 bits
- **Search-order or "curve" filter: factor 1.** The measured AUC bounds any such filter to about 1.05× at 8 bits.
- **Within-run clustering: nothing.** It helps only to find a second hit near a first one, and the entry needs one
  collision. Even then it is at most about 1.1× at W8, and it is gone at W10.
- **Known structure: not a new gain.** The (member, E1.d1) table is the counter lever (toy 10.9×; the 32-bit
  905× claim was not re-derived here). The w8/E3 side is part of the exact model's count. A w8-only rule keeps
  about 1.4–1.5× more collisions per trial at toy size (keep 10% or 3%). Whether it adds anything beside the h1
  rule at 32 bits can only be settled by the 32-bit exact count, not by these collisions.

## Not done
- No new runs. Nothing on Yukon.
- N1 and N2 exist only at W8: a W10 mass table needs 2^30-entry tables.
- The N2 null is effectively small (488 at W8 filed, 308 for the counter toy).
- The quarter-run effect would need a fresh W8 run that logs near-collisions per block to confirm or explain it.

## Files
- **Scripts:** `collect.py`, `feat.c`, `build.sh`, `run_feat.sh`, `p3prep.py`, `run_p3.sh`, `check.py`, `analyse.py`.
- **Outputs:** `results.txt`, `hits.tsv`.
- **Regenerable:** `feat_out*.txt` (37 MB) is rebuilt in seconds by `run_feat.sh`.
