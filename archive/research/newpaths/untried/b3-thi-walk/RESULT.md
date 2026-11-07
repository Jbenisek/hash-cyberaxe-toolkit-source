# b3-thi-walk: walking the high counter word on the front line. Scout result, 2026-10-10

Cell: r1c x cost, the t_hi walk (follow-up of wave 1's b3-r1c lead). This is our own research. Nothing was filed or
submitted. One CPU process ran at a time and one GPU job at a time. The longest run took 374 s. No kissat.
Labels: COMPUTED (I ran it), DERIVED (arithmetic on computed or cited numbers, or my own written schedule), GUESS.

## Verdict: alive. About 61.50 on pkgCM's ledger, a saving of 1.30 bits (DERIVED)

Walking t_hi inside each (context, member) removes four of pkgCM's rows: the representative batches, the opened
clusters, the E lanes and the fills. Together they are **70.85%** of its machine units. The only new cost is a packed
Y9 lane over the steps that pass test (2).

On pkgCM's own ledger (N = 3,436,742,575,482,187,376,270, unit 430), the walk gives **N' =
1,399,921,808,280,670,031,287**, so **time_log2 = 61.4976**, against 62.7934: **-1.2957 bit** (DERIVED).

That figure already pays the long messages: two complete evaluations of 2^61-byte messages, 2^56.1 units, cost
+0.034 bit. Every stage I could reach was tested:

- the reference hash at t >= 2^32;
- the exact law of test (2) on a walk block;
- the real 32-bit shares and E1 rate on the walk distribution;
- end-to-end toy collisions on the front line's scaled rig.

**What is not established:**
- my lane schedule (written out, not executed and counted);
- H5_exec on the walk;
- the dependence clause, restated for walk contexts;
- whether the judge accepts messages of up to 2^61 bytes.

## Per-stage table

| stage | test | result | label |
|---|---|---|---|
| S1 construction at t_hi != 0 | `walk_model.py` C1 and `legal.py` P3: reference `_compress` at t = t_hi * 2^32 + t_lo; half-collision, state consistency, E1.c1 = c1, beta* | **512/512** (largest t 2,251,799,739,717,328, just below 2^51), **50/50** at t_hi = 2^19 - 1 | COMPUTED |
| S2 what moves | C2, C6: C0 and D1 values constant along the walk | **0** mismatches (64 x 8 x 17 names). 24 names move: K1.a1 w2 w3 X0, all of D0, w8 w9 X5 X10, all of C1, C2.c1 C2.b1, Y1 Y5 Y9 Y13, omega | COMPUTED |
| S3 omega blocks | C4 and the GPU shares run | X0 runs an interval of exactly 2^19; omega mod 2^16 is constant per X0 block (9 blocks per walk, 7 full ones). **0 bad** over 3.0e10 GPU steps | COMPUTED |
| S4 test (2) on a block (exact) | `n2_states.py`: automaton state after 16 bits | **7 states**; **7,072 of 65,536** low halves live (10.79%); a live block passes in **32,832 or 33,696** of its 65,536 steps (about half); total 233,715,456 = E_COUNT | COMPUTED |
| S5 list method and lane formulas | C5, `lane_check.py` L1 to L3 | listed omegas give exactly the passing steps (27 blocks, 0 mismatches); X0 from the listed omega and the 13-line Y9 path from per-context constants: **3000/3000**; 19 (state, mask) lists per live state | COMPUTED |
| S6 legality and long-message cost | `legal.py` | t <= 2^51 - 1, so every t_hi < 2^19 is legal; **17t + 1** compressions per message (0 mismatches, t <= 1023) | COMPUTED |
| S7 shares on the walk (real 32-bit) | `walk32 shares`: 2^16 contexts walked, 3.0e10 steps; `walk32 eshare`: exact per-context E from block low halves | **E share 0.999994 +- 0.000020** of pi_E (2^34 contexts); walked 1.0047 +- 0.0102; **pass share 1.0044 +- 0.0102** of pi; P(pass given E) 0.018214 vs 0.018220 independent; share of (1) 0.0276826 vs exact 0.0276829 | COMPUTED |
| S8 E1 outcome rate (real 32-bit, 2^45 trials per arm) | seven TAUS and eps (Lemma N), against the exact model 53 * 2^-38 | walk **0.9943 +- 0.0122**; control at t_hi = 0 **1.0053 +- 0.0122**; walk-dense 1.0018 +- 0.0296 (clustered); context-dense 1.0081 +- 0.0123 | COMPUTED |
| S9 end-to-end, scaled rig (toy8, W = 8) | `toy/ctr_walk.cu`, plan fixed in `toy/PLAN.txt` | control **10,279 / 10,200.2 = 1.0077 +- 0.0099**; walk over 32 high words **10,179 / 10,248.8 = 0.9932 +- 0.0098**; walk over 256 **10,635 / 10,599.8 = 1.0033 +- 0.0097**; walks pooled **0.9983 +- 0.0069**, 97.7% lower bound **0.9846 >= 10/11**; **0 bad** in 1.65e12 walk trials | COMPUTED |
| S10 clustering | real and toy | 84.7% of walk contexts have no live block. Pass count per context var/mean 3,067 (factor E[N^2]/E[N]^2 = **7.7**). Per-context E1 rate: walk var/mean **5.93** (relative variance 0.19, from Y12 being fixed) vs front-line contexts 1.02. Toy: run dispersion 1.092 (walk 256), groups with >= 2 hits 2 vs 0.25 expected | COMPUTED |
| S11 ledger | `ledger.py` | **61.4976** (-1.2957 bit). With premise factors 1.03: 61.5133. Lean final step (writing only): 61.4632 | DERIVED |

Round depth: the lever is specific to the 2-round counter search. The 1-round paths are deterministic and have no
counter search, so they were not tested. The toy (W = 8) is the scaled stage, and S9 ran the walk on it.

## (1) Do the omega test, the gate and Lemma F read only omega and words fixed per member?

Partly. I read pkgCM proof.md 8, 9.8, 9.9 and 11, and `frontline.py` LINES, T1/T2 and Y9_PATH.

- **Test (2), the omega test (T2' at omega, 9.8 and Lemma DT): yes.** It reads omega alone.
  - On the walk, omega = e1 - S0 - S5 + (ROR(X0,16) XOR S15'), and X0 = Cc - K1.a1 runs a 2^19 interval.
  - So omega mod 2^16 is fixed per X0 block, and the high half runs over all 2^16 values (S3).
  - The automaton's state after 16 bits decides the whole block exactly (S4): 89.2% of blocks are dead and cost one
    state test; a live block passes in about half its steps, and those steps can be listed from 6 x 19 small lists.
  - This replaces the omega side, the lane tests, the gate and the masked partner walk. Lossless: the list method
    equals enumeration, 0 mismatches.
- **The cluster gate (9.9, the 2^30-entry table; the old 2^21-key table P is only kept in the once row): no.**
  - Its key reads omega mod 128 (fixed per block), Y0[8..15] and e[20..21] (fixed per member).
  - It also reads A[8..15] and Hbad, with A = C0.b1 + w6 + X4 + w2. **w2 moves at every walk step.**
  - The gate is not needed: it is a device across members, and the block state test above is exact and finer.
- **Lemma F: no.**
  - It reads omega (test (2)) and **Y9** (test (1)).
  - Y9 moves at every step: C1 reads X5 (through D0) and w3 = X0 + c3.
  - So test (1) stays a per-step test. It now runs on the listed (2)-passing steps only, 7 to a packed word with no
    wasted lanes, through a 13-line Y9 path checked in S5.

Wave 1's assumption that "the omega rows vanish" holds for the omega rows. The Y9 work does not vanish; it is
re-priced below.

## (2) Is t >= 2^32 legal, and what does a long message cost?

**Legal.**
- The profile says: "Finite byte strings of bit length below 2^64", and the tree has "64-bit zero-based chunk
  counters".
- `blake3.py` rejects len >= 2^61 bytes and loads v12 = t mod 2^32, v13 = t >> 32.
- F || B has 1024 t + 63 bytes, so the largest legal t is 2^51 - 1 and the largest t_hi is 2^19 - 1.
- Every t_hi of the walk is legal. The reference gives the half-collision at t_hi = 2^19 - 1 in 50 of 50 trials
  (COMPUTED).

**Cost.**
- The search never compresses F: by Lemma TR only the last chunk's CV matters.
- The organizer's tree code makes **17t + 1** compressions per message: 16 per full chunk, 1 for the last chunk,
  and t parents including the root. This was counted on the reference for t = 1..64 and up to 1023, with 0
  mismatches (COMPUTED).
- At t = 2^51 - 1 that is 2^55.0875 per message. Two complete evaluations cost **2^56.0875 units**. Writing the
  two messages (2^62 bytes, 2^57 stores) adds 2^48.25 units. pkgCM charged its final step at 2^38.
- Charged at 2^56.1 units of time, this adds 0.034 bit to the walk total (DERIVED).
- If the final evaluations are not charged (writing only), the walk is 61.4632.
- Memory is not scored, but the messages are up to 2^61 bytes each. pkgCM declares 2^44 bytes "covering the
  messages", so that declaration would become about 2^62.

## (3) The rate on the walk distribution, and the rows that change

**Rate.** H1'(i), the first moment, holds on the walk wherever I could measure it:
- the toy end-to-end on the scaled rig (S9: walks 0.9983 +- 0.0069, control 1.0077);
- the real 32-bit E1 outcome rate (S8: walk 0.9943 +- 0.0122, control 1.0053);
- the real shares (S7).

**Rows on pkgCM's ledger**, machine units (DERIVED; my schedule is in the `ledger.py` docstring):

| row | pkgCM | walk | per outer step |
|---|---:|---:|---|
| context | 112,519 x (RC+1) = 137,150,669,488,596,985,144 | walk context, 1,024 x (RCW+1) = 1,426,474,366,171,283,456 | 0.2146 -> 0.0022 |
| representative batch | 168,337,731,491,771,799,375 | removed | 0.2634 -> 0 |
| opened cluster | 1,168,517,254,413,134,797,632 | removed | 1.8285 -> 0 |
| E lane | 243,433,090,603,453,661,778 | removed | 0.3809 -> 0 |
| fill | 850,917,555,121,445,528,808 | removed | 1.3315 -> 0 |
| blocks (new) | | 7 x 2,048 x RCW = 19,970,641,126,397,954,048 | 0.0313 |
| walk-lane words (new) | | 96 per 7 listed steps = 476,930,085,422,256,209,568 | 0.7463 |
| passing lane | 33,589,842,598,613,164,283 | 33,589,644,460,558,134,896 | 0.0526 |
| solver credit | 829,308,674,569,081,960,042 | 829,308,674,569,082,045,087 | 1.2977 |
| once | 1,128,752,545,267,752 | + 2^26 | 0 |
| SEL | 5,486,510,246,044,225,536 | unchanged | |
| final step | 430 x 2^38 | 430 x 2^56.1 | |
| **N (430 T)** | **3,436,742,575,482,187,376,270 (62.7934)** | **1,399,921,808,280,670,031,287 (61.4976)** | 5.369 -> 2.130 |

Notes on the rows:
- RCW = 1,393,041,373,214,143 walk contexts, each one fresh draw of 7 outer words and a member, walking its 7 full
  X0 blocks: 458,752 outer steps, the same total 2^69.1145 as pkgCM.
- A walk-lane word costs, per 7 listed steps: load 1 + X0 lanes 4 + Y9 path 39 + seven T1 lane tests 41 + loop
  3 + W 1 = 89, charged 96. That is 13.7 per (2)-passing step, against about 74 upstream units per E lane in pkgCM.
- Sensitivity: if the lane cost doubled, the saving is still about 0.9 bit (61.92) (DERIVED). The solver credit is now 61%
  of the total, so it is the next row to attack.

## Risks and what I could not test

1. **The lane schedule is mine.** It is written out and its formulas are checked (S5), but no program executed and
   counted it the way pkgCM's units were counted.
2. **H5_exec on the walk is not measured.** The solver credit is 61% of the new total. Y9, omega and the pass
   shares match on the walk, but the solver ledger mean was not run on walk outer steps.
3. **The dependence clause (H1'(ii)) must be restated for walk contexts.** The measured clustering is
   modest: a factor of about 7.7 on passes from block liveness, and a relative variance of 0.19 on the E1 rate
   from fixing Y12. pkgCM quotes a margin of about 2^44.
4. **The judge on messages of up to 2^61 bytes.** The domain allows them, and pkgCM already uses 2^42-byte
   messages, but the size is new.
5. **The pass-share premise is measured only to 1%** (1.0044 +- 0.0102). Its row is small; a factor of 1.03 costs
   0.016 bit.

## Next test

1. Put the walk into a counted copy of `frontline.py`: walk contexts, block state, (state, mask) lists, packed Y9
   lanes and its straight-line cross-check. Meter the lane units.
2. Run its passing outer steps through the shipped solver to measure H5_exec on the walk.
3. Then re-optimise the outcome set S under the walk's ledger. Test (2) is now nearly free and the solver dominates,
   so the 6-of-7 choice of pkgCM may no longer be optimal. This is a combination lever, not assumed dead.

## Files (all in this folder)

- **Python:** `walk_model.py` (out: `walk_model_out.txt`), `n2_states.py`, `lane_check.py`, `legal.py`, `ledger.py`
  (each with an `_out.txt`).
- **Real 32-bit GPU** (`real/`): `walk32.cu`, with `co_lines.inc` and `tables.inc` generated by `gen_cuda.py` from
  the shipped program. Cross-check: `check_probe.py`, 24/24 equal. Outputs in `out/`: `shares.txt`,
  `e1_arms.stdout`, `eshare_*.txt`.
- **Toy rig** (`toy/`): `ctr_walk.cu`, `PLAN.txt`, `run_arms.sh`, `analyse_arms.py`, `analysis_out.txt`, and
  `out/*`. The control reproduces the rig's validation at its old base line for line: 133,694,335 trials, the same
  2 hits.

## Refusals or stops

None. No tool call was refused or stopped. A foreground `sleep` was blocked by the harness's rule against chained
sleeps, and I waited with a monitor instead. Each run ended on its own.
