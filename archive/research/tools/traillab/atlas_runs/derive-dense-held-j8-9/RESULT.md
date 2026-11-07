# derive-dense-held-j8-9 - atlas cells (4,8) (5,8) (6,8) (7,8) (8,8) (5,9) (6,9) (7,9) (8,9) (9,9) (chi37)

Date 2026-10-12. Tool: traillab (make test 53/53), chi/chi37.txt, `--threads 2` on every call, each call under `timeout 1200`.
Consistent messages only (real expansion, no held expanded words; `--hold-from` never used). Scripts: run.sh, run2.sh, run3.sh. Raw outputs in this folder.
chi37_W8fset.txt = chi/chi37.txt with ONE line changed: `var W8 fset s0 043ff800 late` (the W8 cell and E4-back are taken out of the
enumerated SET only; they are still checked as conditions, so `cells` is unchanged). Used to enumerate the whole s0 F-set of W8.

## Model facts used (PROVED by construction, tool source traillab.c tl_build)

- Anchor 14: x rows 11..14 = published; W9..W14 are fixed words (not free); x rows 10..5 = step inversion with fixed W14..W9 -> constants.
  y is run forward from the common CV; a sample is y-consistent iff y lands on its published rows 11..14, and then y rows 5..10 are the published ones.
- The only free word that touches rows 4..9 is W8: unstepping step 8 gives A4 independent of W8 and E4^x = c - W8 (linear). dE4 (mod) = 0 always.
- `exact` counts EXACT (zero output difference after step 36) on every built pair, consistent or not: an EXACT hit is a real 37-step pair from one CV.

## Verdict table

| cell | label | number | status | evidence |
|---|---|---|---|---|
| (4,8) | Z | E4[31:29]=000 is exactly the y-consistency condition: of 2^32 W8, 2^29 consistent (all with E4 cell), 3,758,096,384 inconsistent with 0 collisions; relaxation `noE4` adds 0 candidates and 0 collisions (12,103,680 / 1,507,328 = cells). Gain 0 | COMPUTED (exhaustive 2^32 W8, pub base) | exact_r4_9_W8all_pub_out.txt, exact_r4_9_W8fset_pub_out.txt |
| (5,8) | 0 | rows 5..7 are constants of every consistent sample; cell-model view of row 8: X_E Pr 1/4 (4 free bits, exact), X_A Pr 2^-14.0 (sampled 2^24) - paid inside the held dense part, not in q | PROVED (anchor + inversion) + COMPUTED (cells hold 12,103,680 / 12,103,680) | backward_8_9.txt, exact_r4_9_W8set_pub_out.txt |
| (6,8) | 0 | as (5,8) | PROVED + COMPUTED | same |
| (7,8) | 0 | as (5,8) | PROVED + COMPUTED | same |
| **(8,8)** | **E** (GOLD by the rule, see caveat) | W8 signed cell `==u` (XOR 20000000) is stricter than the exact event: the other signings of the same modular dW8 = e0000000 (`=un`, `nnn`, `unn`) inside the s0 F-set give real collisions too. Pub base, exhaustive: EXACT 1,548,288 vs EXACT and cells 1,507,328 -> x189/184 = 1.027174 = **+0.0387 bit**. W8 two-bit conditions are implied (dropping them adds 0); only the bit-31..29 signing matters (`xorW8` = `noW8`) | COMPUTED (exact integers, 2^32 W8, ONE base: the published coordinates) | exact_r4_9_W8all_pub_out.txt, exact_r4_9_W8fset_pub_out.txt, exact_r4_9_W8fset_pub_split.txt |
| (5,9) | 0 | rows 5..8 constants; row 9 cell-model: X_E Pr 1/4 (exact), X_A Pr 1/64 (exact); only the printed W9 signing of 512 has Pr>0 - all inside the held dense part | PROVED + COMPUTED | backward_8_9.txt, exact_r4_9_W8set_pub_out.txt |
| (6,9) | 0 | as (5,9) | PROVED + COMPUTED | same |
| (7,9) | 0 | as (5,9) | PROVED + COMPUTED | same |
| (8,9) | 0 | row 8 constant; W8 does not enter step 9 | PROVED + COMPUTED | same |
| (9,9) | 0 | W9 is a fixed word and E9 a constant: nothing varies | PROVED | same |

## The (8,8) find - numbers (pub base, W8 over its whole s0 F-set, exact integers)

| W8 class (y-consistent, s0 F-set) | candidates | collisions (EXACT) | rate |
|---|---|---|---|
| printed signing `==u` (= cells = the 12,103,680 A0-variants) | 12,103,680 | 1,507,328 | 0.124535 (2^-3.005) |
| other signings of e0000000 (`=un`, `nnn`, `unn`) | 6,875,136 | 40,960 | 0.005958 (2^-7.391) |
| union (`noW8` = `xorW8` = `xorx2W8`) | 18,978,816 | 1,548,288 | 0.081580 (2^-3.616) |
| F-set but y-inconsistent | 268,331,008 | 0 | 0 |
| outside the F-set (2^32 - 287,309,824) | 4,007,657,472 | 0 | 0 |

EXACT / (EXACT and cells) = 1,548,288 / 1,507,328 = 189/184 -> +0.0387 bit on the same samples. This is the E definition (exact event looser than cells, > 0.01 bit): **GOLD flag raised.**

**Caveat (read before crediting):** the extra collisions come with 6,875,136 extra candidates at 1/21 of the cell rate. As a per-candidate probability the union is WORSE (2^-3.616 vs 2^-3.005). The +0.0387 bit is a +2.7% enlargement of the W8 pool's collision count, worth something only where the attack is limited by the number of W8 candidates per base (degrees of freedom), and only if trying the extras costs the same per candidate. Not established beyond the published base.

## Not tested / limits

- One base only. SMC bases (rows 22..36, np 64, 4 particles, exact_r22_36_W8fset_smc4.txt) gave 0 collisions in every class (no base passes row 22 for any W8), so they say nothing either way; prefix rows < 22 held for 12,103,680 W8 per base (= the `==u` class, the extras fail the W8 cell in the prefix, as expected).
- `window` is refused for rows < 16 ("window must start at or after the first free row 16"), so no SMC ratio with error bars exists for these cells.
- Dense part out of traillab scope: rows 5..14 are held at published values; changing them (e.g. zoneD-rows4-5/joint.out: E4[31:29] x E5[31:29] has 4 joint patterns with published low bits) is not modelled here. The labels 0 are "0 in the held model".
- Whether the 6,875,136 extra W8 are reachable in the real attack's A0-variant generation (allg_classes lists only the `==u` 12,103,680) was not checked.
