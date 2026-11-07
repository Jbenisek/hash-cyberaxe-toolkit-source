# b3-misc: four leftover cells of the 2-round BLAKE3 grid (2026-10-10)

Our own team's research. Nothing filed, submitted or posted. Read only the files named in the brief:
BLAKE3_2ROUND_MAP.md (summary, sections 1-2, 5, 6), negative_space\AXES.md, negative_space\GAPS.md, and
verifier\blake3.py (imported). One CPU process at a time, each run under one minute. No kissat, no yukon, no network.
Labels: COMPUTED (run here), DERIVED (arithmetic on computed or cited numbers), GUESS. "cited" names the source;
the label it carries there is kept.

**Blocked: nothing was refused or stopped.**

## Verdicts

| cell | verdict | number or obstruction |
|---|---|---|
| const x join (GAPS item 5) | **dead (real test)** | Exact ILP over all extra-constant sets and all crossed relations: best split quality q = min(d_U,d_V) - c = **0**, proved optimal (dual bound 0) at the root, with t_lo free, and with t free. That means at least **2^129** list entries per 128-bit match (DERIVED), against the front line's 2^62.95. One extra pin (d_S <= 1): **infeasible**. Constants alone: no split leaves both sides varying; the best is fix-E3 (d_U=4, d_V=0, d_S=4), which is map 5.6 (84.61). All COMPUTED. |
| gen x class | dead (no run) | No round-0 cancellation means no 4-check floor. The best known nonzero-state route has 13 word conditions, and its round-0 stages are not free (cited, map 5.3). On the front line, class selection gained 36.87 bits over 4 conditions (2^-128 to 2^-91.126; DERIVED). The same gain per condition would still leave 13 x 32 - 13 x 9.22 = **296 bits** (DERIVED; the transfer is a GUESS), against a generic 128. Differential trails cost at least 2^185 (cited, GAPS 1.3, C8). |
| r0 x cost | **dead for the one structural lever; micro-savings open** | The per-context round-0 lines are charged in the contexts row, 2^59.344 of 2^71.935, so removing them saves at most **0.000234 bit** (DERIVED). The per-member round-0 lines are 3 of the 8 omega lines and 9 of the 17 Y9-only lines (COMPUTED; both counts reproduce the map). Ceiling if all of them were free: **0.485 bit** (GUESS: uniform cost per line). The lever that would remove them from the omega test, making w8 an outer word, is **infeasible**: no choice of outer words is solvable one assignment at a time (exact ILP; the front-line control is feasible; COMPUTED). |
| all x canc | dead (no run) | This cell is the D4 family, local collisions across the round boundary (cited, map 5.7): independence projection 2^-63.7, about **2^65** compression-equivalents, not proved; 0 of 8,000,000 choices per arm; 0 completions in 2^34.7 adaptive tries. Periodic and spiral differences: 0 of 1,048,575 routes (cited, map 5.8). A one-word difference cannot cancel across both rounds (DERIVED, below). |

Overall: **dead**. No route found that beats or materially changes a known cost.

## 1. const x join: the real test (split.py, split2.py)

**Model** (COMPUTED). The reference 2-round compression is traced into word relations, 8 per G call. Each relation can
be solved for any one of its words. The trace matches `blake3._compress` on **300 random inputs with 0
mismatches** and 0 failed relations. The system is round 0 plus the round-1 columns. Fixed: the init state, w4, w13,
w14, w15, and the pins X3, X7, X11, X15. Forced words are propagated, so C3 comes out constant (as in the map) and
K2's first half too.

**Terminals.** E1 inputs are Y1, Y6, Y12, w12, w5. E3 inputs are Y4, Y9, Y14, w8. Y3, Y11 and w15 are constants.

**Dimensions.** Structural dimension 8 words at the root (92 free words, 84 relations), matching the map's 2^256.
With t_lo free it is 9, and with t free it is 10.

**Search** (exact, scipy milp / HiGHS). Every word is labelled U (E1 side), V (E3 side) or S (constant or
separator). Every relation is labelled U, V, S or X, where X means crossed and matched as a 32-bit list key; every
add or xor-rotate relation can be separated that way. Structural d_side is words minus relations on that side.
Allowing any set S covers "one more pinned word" and every larger set of constants.

- Constants only (c = 0), at all three dimensions: **no labelling has both d_U >= 1 and d_V >= 1** (infeasible).
  This includes d_S <= 1, the GAPS item-5 test. The max-min is 0. The best labelling is d_U = 4, 5, 6 with d_V = 0
  and d_S = 4, which is "fix E3, search E1" (map 5.6).
- General word-level MITM: **max q = 0**, proved optimal (dual bound 0.0) in all three variants. The root profile
  (c <= k gives q, d_U, d_V, d_S, c) is (0,0,0,8,0), (1,0,1,1,7,1), (2,0,2,2,6,2), (4,0,2,2,6,2), (8,0,2,4,4,2).
  Each crossed relation buys exactly one word on each side and costs one 32-bit key.
- Cost floor (DERIVED). With lists L <= 2^(32 min(d_U,d_V)) and a key of 128 + 32c bits, a match needs at least
  2^(129+32c)/L >= 2^(129 - 32q) = **2^129 entries**.
- Solver check (COMPUTED): two toy systems with known answers both pass. A separable system gives (1,1,1); a
  chained system gives infeasible.

**Limits.** This is the word-level, generic-count model. Bit-level splits are not modelled here; map 5.2 (bit-serial,
2^128 per split point) covers them. Within that model the answer is exact, and it agrees with map 5.1 and 5.4.

## 2. r0 x cost: reconstruction and lever test (r0cost.py, r0swap.py, r0tri.py)

**Reconstruction** (COMPUTED). The free set is the map 2.5 list: C0.d1, D2.a1, D2.b1, S11, S4, X9, w6, the member
y = Y4, the trial word c1 = E1.c1, and t_lo solved. With it, all 99 relations (round 0, round-1 columns, E1's first
half) resolve one assignment at a time, with no loops. The line counts:

| class | round 0 | round 1 | notes |
|---|---:|---:|---|
| context-level | 41 | 2 | map: "39 member-free lines" |
| member-level | 16 | 18 | |
| trial-level | 3 (K0.a1, t, w1) | 4 (C2's second half, w0) | plus 3 E1 lines |

- **w8's member ancestry is 8 lines.** This equals the map's "8 lines leading to omega". 3 of the 8 are round 0:
  D0.d1, D0.a1 and w8.
- **Y9-only lines are 17.** This equals the map's 17. 9 of them are round 0 (D1 x5, D0 x4).

**Bounds.**
- Contexts row: at most 0.000234 bit (DERIVED).
- Making every member-level round-0 line free: at most 0.485 bit (GUESS). This uses a uniform cost per line, an
  omega share of 238 of an opened cluster's 267 units, 52 of 61 units in representative batches, and 9 of 17 lines in
  fills.

**Lever: w8 as an outer word.** omega would then be one add per member, with no round-0 line before the omega filter.
- Single swaps into the outer set: 0 of 7 resolve.
- Double swaps: 0 resolve.
- Exact ILP (matching plus levels): with w8, Y4 and E1.c1 free, **infeasible** for every choice of the 6 other outer
  words. The control, with the front-line set forced, is feasible. All COMPUTED.

**What is left (GUESS, unpriced).** By algebra (DERIVED), w8 = (ROL(X0,16) XOR Ka) - Kb, where Ka = ROL(X15,24) XOR S15
and Kb = S0 + S5 are per-context constants. So omega = y + (ROL(X0,16) XOR Ka) + (Y3 - Kb), which is one rotate,
one xor and two adds per member. If frontline.py does not already fold these constants, the saving is a few units out
of 52 per batch, about 0.05 bit or less (GUESS). Checking needs frontline.py's omega lines, which were not in my
reading list.

**Discrepancy to flag.** In this reconstruction, Y4, Y9 and w8 are outer-step values, but Y14 depends on c1 (c1 to E1
to Y6 to C2's second half to w0 to t). GAPS item 2 says all of E3's inputs are outer-step values. The map's joint
E1/E3 solver fits my reading (GUESS). I could not settle it without the proof.

## 3. Derived note for all x canc

Take a one-word message difference with fixed message words; each G call is then a bijection of its 4 state words.
- If the difference enters at y, a2 and then d2 change.
- If it enters at x, a1, d1, c1 and b1 all change, and the 8 steps leave at least 2 of the 4 outputs changed.

So at least 2 words change. Outputs of one call go to different calls of the next half-round. The word is used once
per round, so it can act again in only one of them. This rules out one-word cancellation across the round boundary
(DERIVED, word level). Multi-word versions are the D4 family, with the numbers in the table.

## Files

`split.py`, `split_out.txt` / `.json` (constants-only split); `split2.py`, `split2_out.txt` / `.json` (toy tests and
the crossed-relation MITM); `r0cost.py`, `r0cost_out.txt` / `.json` (line classes, ancestry, bounds); `r0swap.py`,
`r0swap_out.txt` / `.json` (swap search); `r0tri.py`, `r0tri_out.txt` / `.json` (exact w8-outer test); `*_stdout.txt`
and `*_stderr.txt` (raw run logs).
