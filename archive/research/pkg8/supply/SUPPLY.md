# SUPPLY: is the (u=Y12, v=w5) rate gain usable, and certifying the 8.4%

Agent: SUPPLY. Date 2026-10-07. Nothing here is filed, staged, or submitted. No `yukon`, no network,
`.key` never read. All figures below are marked MEASURED / COUNTED / DERIVED / ESTIMATE.

---

## 1. The question

Another model (cloud Opus, relayed) proposes raising the collision rate by fixing two words that are set
within an outer step: **u = Y12** (a word of the member table) and **v = w5** (an outer word). It reports:

- **+8.4 % in the sub-class**, confirmed on real messages (this is certified in section 4 below).
- **+101 %** on a "2^17 cube" with the top six betas, and **+93 %** on a "2^18 cube" — marked by it as
  *heuristic lower bounds, not certified*.
- It **withdrew** the earlier claim that only 3 bits of u and the low 24 bits of v matter: for two beta
  groups the **low 27 bits of v** matter.

The supply worry: fixing bits of u and v restricts the outer words a run may draw (its trial supply), and
u is a *member* word, so a condition on u restricts the MEMBERS, not only the outer words.

## 2. What a run can draw (COUNTED from proof 6.4 + tools/pkg7_data.py)

A run fixes four words from step 1 (C0.c1, D3.d1, S15, S9 — 128 bits) and then loops:

| Loop word | Range in the filed run | Full range | Headroom |
|---|---|---|---|
| C0.d1 | 1,424,469 = 2^20.442 | 2^32 | **+11.558 bits** |
| w5 (= v) | 2^32 | 2^32 | 0 (already full) |
| X2 | 2^32 | 2^32 | 0 (already full) |
| member k (= carries u=Y12) | 131,072 = 2^17 (sub-class) | 2^17 | 0 (already full) |

- Trials needed: 2^127 / FACTOR, FACTOR = 49,400,000 = 2^25.558 → **2^101.442** (COUNTED).
- Filed run supplies 2^20.442 x 2^32 x 2^32 x 2^17 = **2^101.442** — i.e. essentially *exactly* the need,
  with slack < one C0.d1 value (rounding only).
- **Per-run maximum** (push C0.d1 to its full 2^32, everything else already full): 2^(32+32+32+17) = **2^113**.
- So the only slack inside one run is the C0.d1 loop: **2^113 / 2^101.442 = 2^11.558** (DERIVED).
- The whole *family* (all four fixed words free, full 2^19 class) is 2^(7*32+19) = **2^243** (DERIVED,
  matches the brief's "about 2^243") — but a family draw means a *different run*, outside one run's coins.

## 3. What the condition costs, and whether 2^101.4 still fits (COUNTED masks, DERIVED supply)

Masks of the confirmed good/bad settings (from `research/h8/layout_rule/out/pred.txt`, verified by popcount):

- v = w5: mask `0x07ffffff` → **27 bits of the outer word fixed** (earlier thought 24; the withdrawal is
  real — bits 24,25,26 are in the mask). Leaves 2^5 = 32 values of w5 per outer step.
- u = Y12: mask `0x07c10000` (bits 16,22,23,24,25,26) → **6 bits fixed**; the Opus says ~3 carry the effect.

**Effect on members (the u point).** Y12 = (ROL(y,7) XOR C0.b1) - C0.c1, and C0.b1 depends on w5
(proof 6.4, "Y8 and Y12 ... from C0.c1, D3.d1, S9, w5 and y"). So fixing 6 bits of Y12 is a 6-bit condition
on the member y: the member list **shrinks 2^17 -> ~2^11 (131,072 -> ~2,048, factor ~64)** (ESTIMATE,
balanced map). Because C0.b1 carries w5, the "good-Y12" member set is **different for every w5** — it is not
a fixed shortened list; it must be regenerated (or filtered) per outer step. Shrinking members cuts the
kept mass per outer step by ~2^6/g, so a run needs ~2^6/g times more outer steps.

**Does 2^101.442 still fit?** (DERIVED, script reproduced)

| Case | gain g | bits fixed (v+u) | max restricted supply | trials needed /g | shortfall |
|---|---|---|---|---|---|
| 8.4 % good setting | 1.0848 | 27 + 6 = 33 | 2^80 | 2^101.33 | **2^21.3 short** |
| only the bits that "matter" (3u + 27v) | 1.0848 | 30 | 2^83 | 2^101.33 | **2^18.3 short** |
| +101 % cube | 2.01 | 33 | 2^80 | 2^100.44 | **2^20.4 short** |
| +93 % cube | 1.93 | 33 | 2^80 | 2^100.49 | **2^20.5 short** |

Even pushing C0.d1 to the full 2^32 and crediting the rate gain, **a single run falls 18-21 bits short of
the trials it needs.** The usable budget per run is `bits(v)+bits(u) <= 11.558 + log2(g)`; for every case
log2(g) <= 1.01 bit while the condition costs 30-33 bits. The outer word w5 is the killer on its own: it is
already enumerated fully, so fixing 27 of its 32 bits removes 27 bits of supply for which there is no
reservoir inside a run.

**Cost-model trap if you "filter" instead of generate.** If you keep the full 2^17 member list and test the
Y12 bits in stage A (dropping the ~63/64 that fail), you still pay stage A for all 2^17 members while only
~2^11 are useful: per-useful-trial stage-A cost (the dominant `words*batch/members` term in
`tools/pkg7_data.py:per_trial`) rises ~2^6 = **6 bits**, dwarfing the 0.12-bit gain. Avoiding this needs a
*cheap per-outer-step generator* of good-Y12 members (bit-fixing on y that is independent of the sub-class's
e1 free bits — unproven here).

## 4. Certifying the confirmed +8.4 % against an exact count (COUNTED)

The +8.4 % is already an **exact-count** result, not only a measurement. Chain verified here:

1. **Aggregation reproduced exactly.** From the per-outcome exact counts in
   `research/h8/layout_rule/out/cell_weights.txt` (L = side-1 count, J15 = side-3 count, per-cell rate
   ratios as exact rationals), recomputing R/mu over the 67 cells with the class weights gives
   (`scratchpad/subagent/recount.py`, fractions.Fraction, no float error):
   - **C15 GOOD = 1.084819** (pred.txt 1.084819) — the +8.48 %.
   - **C15 BAD  = 0.915181** (pred.txt 0.915181) — the -8.48 %.
   - C13 GOOD = 1.013064, C13 BAD = 0.986936 — all match pred.txt to 6 decimals.
   - Per heavy beta (GOOD): 18b1a098 x1.497, 18d1a098 x1.327, 18d0e098 x0.717, 18b0e098 x1.000 — match.
2. **Mass totals reproduced exactly.** sum L*J15/2^81 over the 67 cells = **183,119,872.000** (pred.txt
   183119872.000); per heavy beta 18b0e098 67,698,688 / 18d0e098 50,790,400 / 18b1a098 51,384,320 /
   18d1a098 13,246,464 — all exact-integer matches.
3. **Underlying per-outcome counts cross-checked by the project's own exact counter.**
   `research/h8/counts/cmp_gpt_sol.txt`: the project EXACT-E1 counter agrees with the GPT-Sol exact counts
   on **43 of 43** shared betas to the printed decimal; totals 162,266,567.0 vs 162,266,763.66 (agree to
   ~1e-6; the gap is 31 tiny betas Sol reached and ours did not). So L, J are exact, not sampled.
4. **Measurement confirms the exact model on real messages** (MEASURED): listed-tau tally W
   `research/task7_layout_gpu/out/collect.txt` good W = 1.0980 +- 0.0155, bad W = 0.9115 +- 0.0050;
   `research/h8/layout_rule/out/collect_test/collect.txt` good 1.0777 +- 0.0040, bad 0.9178 +- 0.0021 —
   both bracket the exact model 1.0848 / 0.9152.

**Certified:** the +8.48 % good / -8.48 % bad factor for the stated 33-bit (u,v) settings is correct as an
exact count and is confirmed on real messages. The +93 %/+101 % cube numbers are **not** certified here
(no exact-count file for them in the tree; the Opus itself marks them heuristic).

## 5. Verdict

**Not usable as a gain in the filed claim; at most a tiny, speculative gain in a different package.**

- **In the filed single-run structure: NOT USABLE.** The condition costs 27 bits of the outer word w5 and
  ~6 bits of the member word Y12 (30-33 bits total). One run has only 11.558 bits of slack (the C0.d1 loop);
  every other loop is already full. Even maxing C0.d1 and crediting the rate, a run comes **18-21 bits short**
  of 2^101.442 trials. The <=1-bit rate gain cannot pay for a >=30-bit supply cut.
- **The +93 %/+101 % cubes: NOT USABLE and uncertified.** Their value comes from selecting the heavy betas.
  Beta is a function of E1's first-half d; holding it is exactly backlog **row 6 ("hold a word of E1"),
  BLOCKED** — no cheap generator, a per-trial ARX solve of up to 2^32 would consume any gain. They are
  heuristic lower bounds only.
- **The +8.4 % could at best become a small gain (~0.12 bit) in a *future* package**, and only if ALL of:
  (a) a cheap per-outer-step generator emits good-Y12 members directly (no filtering tax) with y-bits
  independent of the sub-class e1 bits; (b) the search is re-cast across ~2^21 independent runs
  (varying the four fixed words) with Section 7 re-proved for the multi-run success probability;
  (c) the ratio holds across runs, not only the measured constants. The reward is 0.12 bit and sits inside
  today's measurement noise (W spread 1.045-1.107). **Not worth blocking the 93.5 submission.** Fit for a
  "next-step idea / research" note in the 93.5 package, not a cost change.

## 6. What a later package would need

1. A proven cheap generator for good-Y12 members per outer step (y bit-fix independent of the e1 free bits),
   so the Y12 condition costs member supply but **not** per-trial stage-A time.
2. A multi-run reformulation (vary C0.c1/D3.d1/S15/S9) with an exact count of how many runs and a re-proof
   of Section 7 across runs — because one run cannot hold 2^101.4 of the restricted trials.
3. Exact counts (not heuristic) for the 2^17/2^18 cube and the top-six-beta claim, and a solution to the
   blocked E1/beta handle (row 6) if the +93 %/+101 % is to be real rather than a lower bound.
4. Confirmation that the 8.48 % ratio is stable across runs/constants, at the precision the plain rate used
   (~4,200 positive outcomes for ~12 % s.e.).
