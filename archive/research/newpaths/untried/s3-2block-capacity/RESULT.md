# SHA3-256-r6 two-block capacity: can block-1-chosen capacity deepen/enlarge block-2's affine field? (2026-10-10)

Scout for the SHA3 blk1 x deg / blk1 x lin grid cells. Labels: COMPUTED (run here), DERIVED (arithmetic),
GUESS. Round function = organizer `_permute_lanes` via `cube_degree.rnd`, VALIDATED (300/300) against
`keccak.py permutation(rounds=6)` on FULL random states (nonzero capacity) -- `validate.py`, `out_validate.txt`.
Embedding: block-2 of a 2-block message = the W40 320-bit source (u0..u4 in lanes 0-4 and 10-14, 0x86 in
lane 16) PLUS a capacity constant on lanes 17-24 set by block 1. Single-block work had capacity = 0.

## Headline
**The capacity IS a genuine lever on affinity at round depth >= 2 -- this overturns the "origin-independent,
so capacity is useless" dismissal and is the genuinely untried axis.** But every in-budget test shows it does
NOT open a 3-round-affine field: random (free, c=0) capacities are closed DEAD with numbers; engineered
(bought) capacities are OPEN (needs a structured search beyond this budget). No number beats a known cost.

## Why capacity is a lever (COMPUTED, `origin_test.py`, `out_origin.txt`)
Round 1 is affine for ANY source direction and ANY capacity (the rows-0/2 copy gives zero column parity).
But a chi1 output `o = x0 + (1+x1)*x2` where neighbour `x1` is a CONSTANT contributes `(1+x1)*linpart(x2)` --
its linear part is GATED by the constant `x1`, and `x1` depends on capacity. So round 1's effective LINEAR
map depends on capacity, hence the round-2+ polarizations (which govern affinity) depend on capacity.
- k=1: second differences of F1 on W40 are 0 and capacity-INdependent (0/60 mismatch vs capacity).
- k=2,3,4: second differences CHANGE with capacity (60/60 pairs differ vs a random capacity); they do NOT
  change when only the 320-bit SOURCE base is varied (0/60) -- matching SOLCLOUD_16 5.2 ("affine on every
  SOURCE translate"), which only ever varied the source and held capacity = 0. Capacity is a new axis.
- Control (random source directions, chi1 already quadratic): F2/F3 second differences are capacity-dependent
  (40/40), F1 is not (0/40).

## Per-round table (COMPUTED unless noted)
| depth k | affine on 320-source? | capacity changes affinity? | field dim, cap 0 | field dim, random cap | obstruction |
|---|---|---|---|---|---|
| 1 | yes, all cosets, all capacities | NO (0/60) | full 320 | full 320 | none |
| 2 | on W40 (cap 0) | YES (W40 breaks 780/780 at random cap) | W40 = 40 | ~40 (a DIFFERENT field; coord-clique 5-10) | chi2 polarization |
| 3 | dim 2 (linstruct3, full-rate special dirs) | YES (forms change) | 2 (linstruct3); 1 inside W40; 1 inside coord 2-round field | 1 inside W40; 1 inside coord 2-round field; 0 coord pairs | theta3 adjacency |
| 4 | no | YES | 0 coord pairs | 0 coord pairs | 2x theta3 |

## The 3-round door stays shut at every tested capacity (COMPUTED, `experiment_D.py`/`out_D.txt`, `experiment_F.py`/`out_F.txt`)
Compatibility graph over the 320 source coordinates, requiring the pair to be affine on 3 random cosets (a
genuine field, not one coset):
- k=2: 7,871-9,324 compatible pairs, 36k-53k triangles, greedy clique 5-10 -- varies with capacity (clique
  5 at cap 0 vs 10 at cap1). A 2-round field exists and is RESHAPED by capacity at every capacity.
- **k=3 and k=4: 0 compatible pairs, 0 triangles, clique 1 -- at cap 0 AND all 4 random capacities.**
- Max 3-round-affine subspace inside W40: **dim 1** at cap 0 and 4 random capacities (780/780 W40 pairs have
  nonzero B3 -- the linstruct3 dim-2 structure is NOT inside W40; it uses special full-rate kernel cycles).
- Max 3-round-affine subspace inside a coordinate 2-round field (clique dim 5-10): **dim 1** at every capacity.
- B2's dependence on capacity is NONLINEAR (`B2_linear_in_capacity: false`), so "c capacity conditions cost
  2^c" is not a clean linear model for shaping the field; conditions to engineer the field are degree >= 2.

## Economics of the prize (DERIVED)
A 3-round-affine field of decent dim would cut the degree at the chi6 inputs from 8 to 4, roughly halving the
FES exponent of option b. GUESS: ~0.3-0.5 bit below the 123.18243 ledger (122.98 score). Each block-1 trial
costs 1 unit, adding 2^c to N = 2^127.993 -- negligible for c < ~115, so a bought capacity would be affordable
IF it produced the field. It does not, in any configuration tested. 2-round fields larger than 40 are
economically moot (option b saturates: score 122.978 at n=21..80).

## What is NOT closed (the honest gap)
1. Only RANDOM capacities were sampled (4 of 2^512). A SEARCHED/engineered capacity -- chosen so that >= 3
   directions' chi2-output forms land together in the theta3 kernel -- was not searched. This is the real
   question ("for SOME affordable capacity condition set") and needs the structured SOLCLOUD/linstruct greedy
   (f=0/g=0/f+g=0 restriction) re-implemented with injected capacity, swept over a condition search. Beyond
   a tight scout budget. STRONG plausibility it fails (DERIVED): theta3 itself is a FIXED dense linear map;
   capacity only moves which columns chi2 outputs occupy, and aligning >= 3 directions into the theta3 kernel
   is the same problem SOLCLOUD_17/ISD closed at cap 0 (dim-186 double-kernel space, min weight 262, random-like).
2. The non-2-round-affine 3-round regime (F2 not affine, F3 affine by degree-4 cancellation -- the
   "non-identity chi transitions" lead of SHA3R6_MAP section 4). Here F3 is degree 4 and its 2nd difference is
   genuinely capacity-dependent, so capacity is the natural enabler -- untested, the real frontier.
3. linstruct3's full-rate special directions re-tested vs capacity in their own parameterization (my
   coordinate/W40 tests are stricter and do not see them).

## Files
`validate.py`/`out_validate.txt`, `origin_test.py`/`out_origin.txt`, `experiment_D.py`/`out_D.txt`,
`experiment_C2.py` (exact polarization form + isotropic/radical helpers), `experiment_F.py`/`out_F.txt`.
`experiment_C.py`/`out_C_zero.txt`, `out_C2_zero.txt` are superseded (random-combo greedy could not reach W40).
