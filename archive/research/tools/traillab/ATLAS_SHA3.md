# ATLAS_SHA3 - printed conditions vs the event, SHA3-256 r5 and r6 (2026-10-12)

Question (the SHA-256 lesson, ATLAS37.md): where does an attack print conditions STRICTER than the event
(zero difference on the 256 digest bits / equal digests)? Every real SHA-256 gain came from such a step.
Scripts: `research/tools/traillab/sha3_atlas/` (own Keccak, validated: P45 = 55/2^19 reproduced exactly;
6-round KAT of the r6 package matches). 1 thread, seconds each.

## Bottom line

Neither SHA3 line has the SHA-256 kind of gap. r5 prints exactly the event from round 2 on (exact count below).
r6's filter is a distinguished-point restriction of an event-implied predicate, already at its cost optimum.
Also: in r5 the trail-probability part is a small share of the total (online 2^29.98 of 2^32.85; E stage 1 is
2^26.91), so no trail-side gap can be worth more than 0.21 bit (whole online removed) and the E filter more than 0.024 bit.

## r5 row atlas (pkgR5L 32.85434; trail of proof.md Section 3)

| Round | Printed conditions | What the event needs | Status |
|---|---|---|---|
| 0 (beta0 -> alpha1) | connector: fixed bits F (520), E_D zero rows, linearised row masks (M2/M3) | any alpha1 that reaches alpha2 | deterministic in V (costs DF, not probability); DF 33 needed, 45-60 typical |
| 1 (beta1' -> alpha2, 59 rows) | 127 linear round-1 conditions (M4) | alpha2 such that rounds 2+ collide | deterministic in V (Lemma 2); probability 1, so nothing lost |
| 2 (beta2 -> alpha3, 10 rows) | 24 equations tested by FES stage 1 (w2 = 24) | any alpha3' with nonzero P45 | **EXACT: no other alpha3' contributes** (count below) |
| 3 (beta3 -> alpha4) | none printed | - | P45 already sums all 2^19 alpha4 (clustered) |
| 4 (digest) | DDT[q][0]+DDT[q][16]: 4 of 5 bits per plane-0 row | lanes 0..3 only | already event-exact (bit x=4 free) |
| stage 2 | full 256-bit digest compare | the event | exact |

### Round-2 cluster count (the rows 18/19 analog), exact

All 2^24 alpha3' compatible with beta2 (row output sets 4,4,16,4,4,4,4,4,8,8; chi DDT output sets are affine and
uniform, checked for all 31 inputs). P45(alpha3') computed EXACTLY by branching over the 10 allowed digest-row
values {0,16,20,21,24,26,28,29,30,31} with Gaussian elimination on alpha4's affine parameter space (ex.py; reproduces
55/2^19 for the trail's alpha3 in 0.3 s).

- The 10 rows pair up in 5 columns (z = 0, 2, 17, 21, 61); alpha3' stays in the CP kernel iff both rows of a pair have
  equal outputs: 512 in-kernel variants, all with the same w2 = 24. Exact P45: nonzero for 1 (the trail), 0 for the other 511.
- The 50 single-row changes (off kernel, alpha4 space dimension 33-87): P45 = 0 for all 50.
- 4,000 uniform random alpha3' of the 2^24: P45 = 0 for all.
- Cluster / trail = 1.000 exactly over everything counted. The 24 printed equations are what the event needs; this is
  the zero-digest "forced bit" effect (CLOSED_DOORS SHA3 row 3) acting in round 4 on every neighbour.
- What a looser filter would have bought, had it worked: per kernel pair, "equal outputs" is 2-4 affine equations
  instead of 4-6 (z=17 and z=61 pairs: 2 instead of 4). It buys nothing because the extra alpha3' never collide.

## r6 filter atlas (S6K 121.72219, base 909b6453 121.8701)

| Test | Event | Status |
|---|---|---|
| 8 filter bits = 0 (digest z = 0,1, lanes 0..3; Lemma 11) | equal digests imply equal filter bits | event-IMPLIED, value-restricted (distinguished point) |
| key 140 bits (132 free on survivors) | 256 bits | proof uses 132 free bits correctly (Section 9 (b), (c)); key width closed (CLOSED_DOORS SHA3 18) |
| verification, 256-bit compare | event | exact |

- Filter width k (derived, per-point FES 19.06/19.25 ops per form per 256 lanes + 13 per point; survivor 148.2 kernel
  + 6 probe + 10 extraction + 2.5 generator = 167; cost per unit lambda f(k) = 2^(k/2) [(19.15k + 13)/256 + 167 2^-k]):
  k=7 21.25, **k=8 20.80**, k=9 23.77 -> k=8 is the optimum (k=7 +0.03 bit, k=9 +0.19 bit). Closed by derivation.
- Target values: each slice target has a 2-row preimage, always an affine line, so any target gives 4 XOR-forms of the
  same cost. Closed.
- Form degree (the "dependent values" check, LEVERS w7_blk1_planerank in part): 24 random cosets x random 8-dim
  subspaces of span(W40): every one of the 8 forms and the 10 planes has a nonzero 8th derivative (6-18 of 24);
  9-dim control all zero. All forms have degree exactly 8: no cheaper FES. Closed (deg6.py, 3 s).

## Ranked candidate gaps (what is left)

1. **r5 round-2 equations dependent on V** (dependent-values lesson): some of the 24 FES equations may be constant or
   linearly dependent on a connector space V. Test: ANF of the 24 equations over each of the K = 50 spaces (fes_setup
   already computes it), count constant/dependent ones. Ceiling 0.024 bit (E stage 1 share). Not run (needs the spaces).
2. **r5 rounds 3-4 Markov premise**: P45 = 2^-13.2186 assumes independent rows; the event probability on the real
   values is only checked through the R7 success study. Test: on stage-1 passers of real spaces, count digest
   collisions vs 2^-13.2 (needs E runs). Affects success, not cost; ceiling small.
3. **r5 connector relaxation** (rounds 0-1 printed 127 + linearisation, event needs only alpha2 reachable): would buy DF,
   and DF is not binding (33 needed). Ceiling 0.21 bit (whole online part); realistic 0. Low prior.
4. **r6 alternative filter predicates of lower cost**: any 8-bit digest-determined predicate with probability 2^-8 works;
   all XOR-form choices tested are degree 8; a predicate on other slices z or mixed lanes is untested but has the same
   degree by the same 3-chi-round bound. Low prior.
5. **r6 key/filter joint**: survivor keys spend 8 constant bits (z = 0,1) in the 140-bit word; dropping them from the
   kernel's computation (not from the table address) saves kernel work only if the kernel computes them; check K_BUD
   network for the z = 0,1 cone rows. The S6K note says the kernel computes "its 132 bits that the filter leaves free",
   so this is probably already taken. Ceiling under 0.01 bit. Not checked in the generated programs.

Closed here (add to CLOSED_DOORS SHA3): r5 round-2 clustering (exact, 0 of 2^24 by full in-kernel + single-row count and
4,000 samples); r6 filter width (k = 8 optimal); r6 form degree (all exactly 8).
