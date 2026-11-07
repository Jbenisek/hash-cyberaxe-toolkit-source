# The cluster lever, made exact (middle level of LEVERS_REAPPLY, 2026-10-09)

Local only (`research/fifties/cluster/`). No staging. Builds on the omega-first batch of
pkgCA 9.8 / `research/frontline/ca/CA.md` (67 units per 7 members) and automaton (2), the
first filter on omega (`research/impl/outer.py`). Labels: PROVED, MEASURED, DERIVED, GUESS.

Idea (LEVERS_REAPPLY "Middle level"): the 32 members of an `e1`-bits-10..14 cluster share
`omega` bits 0..8 (the rotations on the omega side add 7+8+16=31 bits, so flipping `e1`
bit k leaves omega bits 0..k-2 fixed; bit 10 fixes bits 0..8). Automaton (2) reads omega
low-bit up; its verdict on bits 0..8 is shared by all 32. Skip the 31 partners of a
representative whose `omega mod 2^9` is dead.

## Alive shares of automaton (2) — PROVED
Exact DP over the bit-level automaton (`prep.py`), S-restricted, validated two ways:
reproduces `E_COUNT = 233,715,456` at 32 bits, and the 9-bit value equals 208/512 of the
prefixes checked against the authoritative `outer.look` (0 disagreements in 300,000 words).

* **alive after omega mod 2^9 = 13/32 = 0.40625; dead = 19/32 = 0.59375.** (PROVED)
* alive share by bits read b=1..32: 1 (b≤5) · 0.8125 (6-7) · **0.40625 (8-13)** · 0.2158 (14) ·
  0.1079 (15-22) · 0.0645 (23-28) · 0.0544 (29-32). (PROVED; = LEVERS table, labelled +1 in b.)

## (1) Exception rate and the DEAD claim — MEASURED (GPU, RTX 3090)
`cluster.cu`: step CO omega codegen'd from `outer.LINES`, SplitMix64 contexts/members,
automaton (2) from the flattened T2 table, alive bit from a 512-entry table. GPU vs
`outer.scalar_outer` on an identical stream: **0 mismatches** on every counter (20,000
clusters). Two independent seeds, 2^31 clusters each → **2^36.95 = 133,143,986,176 partner
pairs** (>> the 2^30 asked), ~17 s each.

* **Exceptions** (partner's omega bits 0..8 differ from the representative's): **1,383,368**.
  **Rate = 1.039e-5 = 2^-16.55.** 95% upper bound 1.041e-5 = 2^-16.55 (binomial), 1.047e-5 =
  2^-16.54 (conservative, within-cluster design effect ≤ 31). Two seeds: 1.032e-5, 1.047e-5.
* Dead share measured **0.5937434** vs PROVED 19/32 = 0.59375 (matches to 5 decimals).
* **DEAD-representative claim CONFIRMED:** of the 7,683 partners of dead representatives that
  pass test (2), **0 are non-exceptions** — every partner of a dead representative fails
  test (2) except the counted exceptions (0 violations in 2^36.95 pairs). Structural reason:
  a partner sharing omega bits 0..8 with a dead representative reaches the same absorbing
  dead state of automaton (2), so its mask of (2) is 0.
* **Loss of the lever (the skip):** skipped partners are those of dead representatives; only
  **9.72e-8 = 2^-23.3** of them even pass test (2), and each would still need the full filter
  and solver (~2^-91). So the lever is not exactly lossless (exceptions exist at 2^-16.55),
  but the lost-success rate is bounded far below H1's 5/7 margin. (MEASURED)

## (2) The exact cluster batch listing and its count — DERIVED
Layout (one-time): U/E lists reordered so each 32-member cluster is contiguous (member =
32·cluster + pattern, pattern = `e1` bits 10..14); a representative list (pattern 0, 2^14
per context) and, per cluster, its 31 partners pre-packed into 5 words (7,7,7,7,3). Still
fits the 2^27 list-build charge.

* **Representative batch, 95 units / 7 reps** = 67 (the 9.8 omega-first batch: 4 loads+addr,
  19 omega side, 41 lane tests, 3 cursor) + 7×4 for the alive bit per lane (AND omega with
  0x1ff; + alive9 base; load the alive bit; branch to dispatch). Representatives are real
  members: the 41-unit T2 test still catches a representative that itself passes.
* **Alive-bit lookup:** `alive9[omega mod 2^9]`, a 512-entry table (dead = 19/32 PROVED).
* **Partner batches, 311 units / alive cluster** = the 31 partners in 5 omega-first batches,
  4×67 + 43, where 43 is the 3-lane last batch (4 + 19 + (5+6+6) + 3). Dead clusters: 0.
* **Exact expected units per member (alive share 13/32):**
  `(95·2341 + 311·6656)/2^19 = 2,292,411 / 524,288 = 4.3724` — against **9.5715 now**
  (67/7 batch row), a factor **0.4569**. (DERIVED; LEVERS's 4.3 used a lighter +2/lane bit.)

## (3) Price — replace the Section 11 batch row — DERIVED, exact integers
Only the batch row changes: the Q-path, passing-lane, credit, context and one-time rows are
untouched because the set of outer steps that pass automaton (2) is unchanged (dead-cluster
partners never pass; Lemma F). The partner batches are data-dependent, so they ride a new
**H4'-type budget on the alive-cluster count** (as LEVERS noted), set at the usual 17/16
margin: `ALIVE_BUDGET = (17/16)(13/32)·2^14·RUN_CONTEXTS = 7072·RUN_CONTEXTS` (exact).

    batch row old = 67·RUN_BATCHES − 30·RUN_CONTEXTS = 7,797,818,548,046,984,199,417  (51.52% of the row sum)
    batch row new = 95·2341·RUN_CONTEXTS + 311·(ALIVE_BUDGET+1)
                  = 345,581,048,832,203,290,905 + 3,417,649,651,085,488,704,599
                  = 3,763,230,699,917,691,995,504
    S_old = 15,136,396,605,699,096,622,327  →  S_new = 11,101,808,757,569,804,418,414
    T = (S + 2^70)/430 + 2^38

* **log2 T: 65.04060 → 64.63082.  Δ time_log2 = −0.4098 bit.** (DERIVED)
* With LEVERS's lighter +2/lane alive bit (rep batch 81): 64.62482, Δ = −0.4158 bit.
* Budgeted units per member = 2,421,787/524,288 = 4.619 (the 17/16 margin lifts the mean 4.372).

## Scope / limits
* The exactness of the shared omega prefix is **measured, not proved**: exceptions exist at
  2^-16.55 (LEVERS guessed 2^-17); an exact-build proof of the carry/borrow-wrap condition is
  still open (a Sol question). The lever's loss is bounded by the measurement, not eliminated.
* The schedule (Δrep = 4/lane, 5 packed partner batches, 17/16 budget) is one concrete choice;
  ±a few units per batch moves the result by ~0.006 bit. The alive shares it rests on are PROVED.
* This is pkgCA's 65.0406 ledger; on pkgCB's 64.87 the same −0.41 would give ≈ 64.46 (DERIVED by
  analogy, the batch share is larger there — not recomputed here).

Files: `prep.py` (automaton DP + codegen), `prep.json`, `cluster.cu`/`cluster`, `verify.py`
(GPU vs scalar cross-check), `pricing.py`, `big_seed7.json`, `big_seed99.json`.
