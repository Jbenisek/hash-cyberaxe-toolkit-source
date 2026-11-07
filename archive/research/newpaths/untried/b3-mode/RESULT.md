# b3-mode: tree/chunk-level (mode) variants of the 2-round BLAKE3 collision

Scout result, 2026-10-10 (clock read 00:22 at start, 01:13 at the last run). Our team's research only: nothing was
filed or submitted. No yukon commands, no network, no `.key`. One CPU process at a time, every run under 2 minutes
(WSL gcc for C, Python for the rest). No tool call was refused or stopped.

Files read: research\BLAKE3_2ROUND_MAP.md (summary, section 2 skimmed, section 5), negative_space\AXES.md,
negative_space\GAPS.md sections 2-4, hash-smash\verifier\blake3.py (imported by exact_lemmas.py). records.csv was
not opened, so records M1, X7, X8, K2 and K10 are taken as GAPS.md describes them: "the two messages at different
nodes or types" (GAPS section 4, row E7).

Labels: PROVED (algebra), COMPUTED (I ran it), DERIVED (arithmetic on computed or cited numbers), GUESS.

## Verdict: open

- The parent-node variants are dead. Every one of the 65,535 message-difference patterns needs at least 8 word
  conditions when no message modification is possible. That is the generic 256-bit bound, so the cost is about
  2^129 (section 4).
- The most promising mode variant is a collision inside a non-final block, with an identical suffix. It reduces
  exactly to a message-only route (section 3). An exhaustive word-level search found a message-only local
  collision, words {m2, m3, m4, m6}, whose final step has no conditions at all.
- The cheapest pattern in that search, {m2, m4, m13}, is exactly infeasible.
- Its round-0 stage K3 shows strong clumping. Over 2^37 fixed-instance trials it got 0 joint passes, where about
  1,136 were expected if the passes were independent. K3 is still solvable on rare (h7, flags, difference)
  combinations: 46 and 74 solutions were verified on the real G.
- The price is not pinned. It turns on two rates nobody has measured. One is how often stages K2 and K1 solve when
  their difference is forced. The other is how often the round-0 diagonal D3 solves.
- GUESS range: 2^50 to 2^62 units if those rates are mild, and much worse if they clump like K3.
- The mode adds only one lever: a fresh chaining value per prefix block, which redraws the K-call constants.

## 1. Mode-level variants not covered by M1, X7, X8, K2, K10

All of these place the colliding compression at the same node type and the same position in both messages.

| # | variant | colliding compression: what may differ | status here |
|---|---|---|---|
| V1 | Multi-chunk messages, same tree, colliding at the root parent | Only the message, which is the two child CVs. h = IV, t = 0, b = 64, flags 12 are fixed (COMPUTED, L3) | **dead**: 8 word conditions minimum for every pattern, about 2^129 (section 4) |
| V2 | The same, colliding at a non-root parent, with the rest of the tree identical | As V1, flags 4 | dead, same numbers |
| V3 | Different chunk counts with an equal left subtree (for example 5 vs 6 chunks) | The root parent differs only in the right CV (m8..m15), or the right children must collide across types | Reduces to V1 with pattern {m8..m15}, 8 conditions. The cross-type part is covered by the records |
| V4 | Same-position non-root chunk, different chunk counts | The trees above differ, so a full collision still needs V1/V3 or a cross-type collision | No new route |
| V5 | Non-final block of any chunk (CV collision, identical suffix) | Message only. h, t, b = 64 and flags are equal (COMPUTED, L3) | **most promising, open** (section 3) |
| V6 | Last block of a full non-last chunk (CHUNK_END, b = 64) | As V5 | Same as V5 |
| V7 | Last chunk with a different block count (one block vs two) | h differs in row b (IV4..7 vs a CV), flags differ | Needs a 128-bit row-b match upstream, at least 2^64. This is the closed CV variant (map section 5, item 3) |
| V8 | Multi-block root chunk with an identical prefix | Only the instance (h) changes | Covered by A11/R18 (rate independent of the instance) |
| V9 | Empty message (b = 0) | One fixed digest | Second preimage, 2^256: dead |
| V10 | Trees with more than one compression pair (Opus job 2) | Pairs that meet at a parent hit V1's obstruction. Pairs chained in a chunk are V7 | Overlaps; not closed here |

## 2. Exact facts (exact_lemmas.py, exact_lemmas.out)

- **L1 (PROVED; COMPUTED 200,000/200,000 each).** For a fixed G input, (x, y) -> (a2, d2) and (x, y) -> (b2, c2)
  are bijections. A message difference with equal G inputs always changes a row-a/d output and a row-b/c output
  (100,000/100,000 one-bit pairs). So a message-only difference can never cancel inside round 0. Every V1-V6 route
  lies outside the four-checks family (map section 5, item 3).
- **L2 (PROVED; COMPUTED 200,000/200,000).** G's inputs b and c are functions of its output alone, so a row-b or
  row-c difference is never absorbed by one call.
- **L3 (COMPUTED by instrumenting the reference)** for lengths 1, 55, 63, 64, 65, 1024, 1025, 2048, 3136 and 4097:
  every parent is (IV, t = 0, len 64, flags 4 or 12), and every non-final block has length 64.

## 3. V5 (internal block): the message-only problem

Truncated word-level model (trunc_search.c, an independent numpy copy in analyze.py; G table identical, 12/12 random
patterns agree, check_test.out):

- Each word is active or inactive.
- G is modelled operation by operation. An add or xor with two or more active inputs may cancel, at one 32-bit
  condition.
- The fold needs Z[i] and Z[i+8] to be equal.

The search is exhaustive over all 2^16 message-activity patterns. Cost models:

- A counts only the final-step conditions (the four-checks metric).
- B counts round 1.
- C counts everything.

| run | A | B | C | A, state after round 0 equal |
|---|---|---|---|---|
| message only (res_msgonly.bin) | 0 (51 patterns) | **3 (only {m2, m4, m13})**; 4: {m0,m2,m4}, {m2,m3,m4,m6}; 5: 15 patterns | 8 (all 65,535) | impossible for all (matches L1) |
| calibration, block-length difference v14 (res_len14.bin) | 0 | 3 | 8 | **4, only {m4, m5}** |

The calibration reproduces the four-checks theorem: k = 4, attained by the front line's own w4/w5 cancellation.
That anchors the model (COMPUTED).

**{m2, m4, m13} is exactly infeasible (PROVED).**

1. D2 absorbs its row-a/d input with y = w13, so dw13 = -dS2.
2. C3 absorbs X15 with (w4, w13), so dw13 = -dw4.
3. Together, dS2 = dw4. But in K2 (w5 equal), dS2 = dw4 + db1.
4. So db1 = 0, and b1 is injective in a1. That forces dw4 = 0, a contradiction.

**Linear-consistency filter (exact_routes.py, exact_all_low.out).** Every word carries its modular difference as a
linear form, with the same message variable in both rounds. Additions are exact; xor-rotates give fresh variables.
Routes whose constraints force an active word to 0 are dropped. The search is exhaustive (uncapped) over the 18
patterns with B <= 5:

- {m2, m4, m13} has no consistent route.
- The best consistent routes have 3 genuine round-1 conditions: {m2,m3,m4,m6} and {m0,m2,m4,m6,m7}.

**The {m2, m3, m4, m6} route (DERIVED from the route and exact G algebra).**

Calls involved:

- K1 (w2, w3 both active) outputs a and c.
- K2 (w4 active) outputs b and d.
- K3 (w6 active) outputs a and c.
- D1 maps abc to ad; D3 maps acd to a.
- C0 absorbs X12 with (w2, w6); C1 absorbs X1 with w3; C3 absorbs X3 with w4.
- The final step is clean: no E-step message word is active.

Conditions:

- There are 13 value conditions: 2 each on K1, K2, K3, D1 and D3, plus C0, C1 and C3.
- The C1 and C3 conditions pull back into round-0 couplings: dS1 + dS6 + dw3 = 0 and dS3 + dw4 = 0.
- Taking dw6 = -dw2 is a free choice of differences.
- D1 is under-determined, because S12 is free through K0.
- C0 needs an xor/additive compatibility, which is solvable through X0 (D0's free word w9).
- D3 is tight: 2 conditions on w14 and w15.

**Stage tests:**

- **Compatibility rates (compat_rates.py; 8-bit brute force 65,536/65,536):**
  - random: 2^-13.68
  - D3 second condition, structured as in the route: 2^-14.11
  - C0 condition: 2^-13.92
  - (COMPUTED, n = 4,000,000.)
- **K3 clumping (k3_scan.c, about 9 s per 2^32 scan):**
  - 32 full scans at fixed (h7, flags, dx) gave 0 joint passes of the two necessary tests: 16 at the root
    (h7 = IV7, flags 11) and 16 with random h7.
  - The rate on random combinations is 2^-26.85 (71 in 2^33, k3_general.out), so about 1,136 were expected
    (DERIVED).
  - Example: dx = 6b8b4567 gave 3,041,382 and 3,749,130 single passes and 0 joint, where 2,655 were expected.
- **K3 is still solvable on rare combinations (COMPUTED):**
  - With real flags 0 or 11 the joint passes still occur, 30 and 34 per 2^33.
  - All 36 printed joint passes have lsb(dx) = 1.
  - Rescans of 7 joint combinations gave 240 to 175,665 joint passes each.
  - Three of the 7 gave verified K3 solutions on the real G (S7 and S15 equal, S3 and S11 differ): 4, 74 (h7
    c4b82ebb, flags 0) and 46 (h7 acd3ec14, flags 11). Files: k3_rescan_*.out.
- **Numbered obstruction:** stages K2 and K1 have their differences forced (dw4 = -dS3 and dw2 = -dw6). Each solves
  only if the forced difference lands on a rare good combination, the same clumping the D4 study reported (map
  section 5, item 7). Whether {m2,m3,m4,m6} is D4's pattern is unknown; sol_answer_D4_local.md was not read.
- **Price (GUESS).** The pieces:
  - Attempt cost: (K3 scans per good combination + 2) x 2^28.3 units per scan. The 2^28.3 is DERIVED from about 30
    word operations per x / 430.
  - Success per attempt: P(K2) x P(K1) x P(D3), with P(D3) about 0.6 x 2^-14.11.
  - Assumed ranges: 2^5..2^9 scans, P(K2) x P(K1) in 2^-10..2^-2.

  That gives 2^50..2^62 units. Every factor except the scan time and P(D3)'s compatibility part is a GUESS.

**The mode lever.** At the root the K constants are fixed (h = IV), but dx is free. At an internal block, each
prefix redraws h1..h7, and with them every K-call constant, for one extra compression. That buys retries for the
forced stages; it does not change any per-instance rate.

## 4. V1-V3 (parents): the number

There is no message modification at a parent, because its words are child CVs. Model C (every condition paid)
gives 8 conditions for every one of the 65,535 patterns (COMPUTED). The pinned 55/63 child pairs, pattern
{m9, m11, m12, m14}, are included. 8 conditions is the trivial bound (256 bits), so nothing beats the generic
birthday attack: 2^128 parent outputs x 2 compressions (last-chunk block + parent) = **2^129** (DERIVED). V3 is the
pattern {m8..m15}, also 8.

## 5. Limits (what was not tested)

- The truncated and linear models ignore xor-difference relations, so they are optimistic. Their minima are lower
  bounds, not prices.
- P(K2 solves with a forced dx), P(K1 solves with a forced dx and coupling (ii)), and P(D3a has a root) on real
  K-triples were not measured. No K2 or K1 scanner was written, and no complete pair was built.
- {m0,m2,m4,m6,m7} (also 3 genuine round-1 conditions) was not examined.
- The arithmetic over GF(2^61-1) is only a proxy for mod 2^32: even coefficients could hide solutions such as 2^31.

## 6. Next test (more than this budget)

1. Write K2 and K1 scanners in the k3_scan.c style (carry-automaton word test, then a 32-step DFS, then verify on
   the real G).
2. From the verified K3 solutions (and new ones at h = IV with lsb(dx) = 1), run K2 with dw4 = -dS3, then K1 with
   dw2 and coupling (ii). Count the success rates: about 2^7 scans each, roughly 20 minutes per stage on one core.
3. On every K-triple, test D3 exactly.
4. If P(K2) x P(K1) >= 2^-6, build a full pair, root block at h = IV, 64 bytes. The expected cost would be below
   2^56 units by the formula in section 3.

## Files

Code:
- exact_lemmas.py
- trunc_search.c, build.sh, run_range.sh
- analyze.py, list_low.py
- exact_routes.py, exact_all_low.py
- compat_rates.py
- k3_scan.c, k3_run.sh, k3_multi.sh, k3_pairs.sh
- k3_general.c, k3_general.sh

Data and outputs:
- res_msgonly.bin, res_len14.bin, test_msg_e0-4.bin, Tdump.bin
- *.out (one per run named above)
