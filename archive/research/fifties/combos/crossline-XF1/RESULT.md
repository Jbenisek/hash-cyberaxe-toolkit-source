# crossline-XF1 (xf1_window): masked partner walk inside opened clusters — RESULT

2026-10-09, about 19:20 MDT. CPU only, at most 2 processes, every run under 4 minutes. No yukon, no submission, pkgCJ not edited.

**VERDICT: GAIN.** Decision row (every charge a deterministic worst case): **time_log2 63.313775, delta -0.288865 vs 63.602640**
(the CM+CK3 row; the board shows it as UP 63.6027). LOST = 0 over 200 preregistered full contexts (1,468,672 opened clusters,
every member checked). Y9 fills: masked mean 6,789 per context against the 12,466 premise, and **at most today's count in
every cluster (proved, and measured: 0 violations)**, so H_G_cluster still covers the new layout with no new count premise.
Break-even: 63.50 holds for any per-opened-cluster charge up to 309 units; the charge used is 236.

Labels: COMPUTED = run here on the organizer's 2-round instance (frontline_full.py lines and the straight-line co_ref);
DERIVED = algebra or exact counting; GUESS = estimate.

## 1. Step 1: fact rerun (COMPUTED). All facts confirmed.

| check | result | file |
|---|---|---|
| lutcount.py | (bit8=0: 8 of 32 windows alive16; bit8=1: 9 of 32), 104 prefixes each | step1_lutcount.txt |
| hist16.py 100 400 11 | alive16 per opened cluster {8: 7774, 9: 8366}, max 9; one 9-bit prefix per cluster | step1_hist16.txt |
| window14.py 100 400 7 | chain mismatches Y4w/Y12w/X0w/omw/low9 = 0 over 518,752 members | step1_window14.txt |
| sens.py, b = 14 and 16 | sensitivity 0 for omega bits 0..7, and for bits 14 and 15 at b=16 | step1_sens_b14_b16.txt |

Deviations, none of which affects a fact: (a) sens.py also runs b = 24 (2^24 bit-serial calls). It was still running after
6.5 minutes with its output buffered, so I stopped my own PID 10088 and reran the b = 14, 16 part from an unchanged copy,
sens_b16.py. (b) window14 took 172 s, not under 2 min, because the machine was shared with other jobs.
walk_mask.py `facts` confirms the same statements exhaustively over all 2^16 values (facts.json): alive16 ignores bits 14
and 15; given alive9 it equals LW[bit 8][bits 9..13]; it is 0 off alive9; LW popcounts are 8 and 9; T2 != 0 implies
alive16 (200,000 random words).

## 2. Derivations (DERIVED). These hand over to XF2.

**2.1 What is constant inside a cluster.** For members j = 0..31 of cluster g, e1_j = e1_0 + (j << 10), and y = e1 - Y3.
- y bits 0..9 are constant. bin10 (the borrow into y bit 10) is a function of g mod 64.
- e1[15] = 0 (class bit) and Y3[15] = 1, so the borrow out of bit 15 is 1 for every j. Hence y bits 16..31 are constant,
  y[10..14] = j - Y3[10..14] - bin10 (mod 32), and only y bit 15 varies.
- Y8 = rol(y,7) ^ C0.b1: bits 0..16 are constant, so c17 (the carry into Y12 bit 17) is constant.
- Y12 = Y8 - C0.c1: bits 17..21 are the window. The top byte is h = H or H-1, the two borrow candidates of F.prefixes.
- Y0 = rol(Y12,8) ^ C0.d1: bits 8..24 are constant, and so is p8 := Y0[8..15]. Bits 0..7 are h ^ d_lo, which varies.
- X0 = Y0 - A, with A = C0.b1 + w6 + X4 + w2. X0[16..24] and the borrow into bit 25 (c25) depend on Y0[0..24] only
  through b(h) = [256*p8 + (h ^ d_lo) < A mod 2^16].
  - If p8 > A[8..15], then b = 0 for both h.
  - If p8 < A[8..15], then b = 1 for both h.
  - So **b can differ inside a cluster only if p8 = A[8..15]**.
- With b fixed, the following are all cluster-constant: X0[16..24], c25, D0.a1[0..8], c9a, w8[0..8], c9b and omega mod 512.

**2.2 Guard (the wrap condition XF2 also needs).** Fall back to today's 31-partner walk iff
`Y0_rep[8..15] == A[8..15]`. This costs 4 units: extract, compare with a resident constant, branch.
- If the guard is quiet, the window model is exact for every member.
- F.prefixes returning two prefixes is the same as b(H) != b(H-1), so it implies the guard fires.
  COMPUTED: exact_not_cheap = 0.
- The guard is not vacuous. In one fallback cluster the representative's mask would have disagreed with alive16
  (fallback_wouldmis = 1). That member had T2 = 0, so even there nothing would have been lost.

**2.3 How many clusters can fire.** p8 is a bijective function of the Y8 low byte, which is (y[25..31] | y[0] << 7) ^ C0.b1.
- y[0] = 0 always. y[25..31] = e1[25..31] - Y3[25..31] - beta, where beta = [e1[21] = 0]. (Bits 22..24 equal Y3's,
  Y3[21] = 1, and for e1[21] = 1 the comparison is won at bit 20 or bit 19.)
- e1[25] = 1 is fixed, so for any target only one beta has the right parity. That fixes e1[26..31] and e1[21] and leaves
  e1[2..7] and e1[20] free.
- **So the guard fires on 0 or exactly 128 of a context's 16,384 clusters.** COMPUTED: the values seen over 200 contexts
  are exactly {0, 128}.
- Charge: 128 x (388 - 236) = 19,456 units per context, a bound, not a mean.

**2.4 The survivor count is exactly 8 or 9.** omega[9..13] = T(j) + 2j + const (mod 32).
- T is a composition of "add a constant" and "xor a constant", so it is an invertible T-function: bit i of T(j) is j_i
  XOR f(lower bits).
- Adding 2j keeps that form, because bit i of 2j is j_{i-1}. So j -> omega[9..13] is a bijection for every context and
  carry value. COMPUTED: 64 of 64 test contexts.
- So the survivors are exactly the preimage of the alive window: 8 if bit 8 = 0, 9 if bit 8 = 1, and 0 if the shared
  prefix fails alive9.
- Losslessness: alive16 = 0 implies alive32 = 0, which implies T2 = 0, because a prefix automaton never revives a dead
  state.

**2.5 Group chunking keeps fills at or below today's in every cluster.** With S <= 9 partner survivors spread over today's
5 partner batches (j 1-7, 8-14, 15-21, 22-28, 29-31), the batch with the most survivors holds n_max survivors, with
S-7 <= n_max <= 7: pigeonhole gives n_max >= 2 when S >= 6, and a batch holds at most 7.
- Chunk A = that batch's survivors. Chunk B = all other survivors (at most 7).
- Each chunk is a union of whole old batches, so a chunk with an E lane contains an old batch with an E lane, and the two
  chunks map to distinct old batches. Hence **G_mask(C) <= G_cluster(C) for every context**, and E[G_mask] <= 12,466
  under the existing H_G_cluster.
- The G_BUDGET halt tail is unchanged: the unhalted total is pointwise smaller.
- Range: 2,341 + 2 x 16,384 + 3 x 128 = 35,493, below the 84,261 the reserve was sized for.
- COMPUTED: fill_dom_viol = 0 clusters, and 0 of 200 contexts with masked fills above old fills.
- The plain split (first 7 survivors, then the rest) does **not** dominate pointwise. Its results are kept as
  plainchunk_*.json for reference.

## 3. Build: walk_mask.py

Per context, it builds a 128-entry table indexed by (bin10, c17, c25, c9a, c9b, omega bit 8, alive9) and holding the
survivor mask plus at most 2 chunks.
- Each chunk stores precomputed packed lane offsets JU = sum (j<<17)<<36t and JE = sum (j<<10)<<36t.
- The packed U and E of a chunk are then rol(y_rep,7)*ONES + JU and e1_rep*ONES + JE. This relies on 2.1: rol(y_j,7) =
  rol(y_rep,7) + (j<<17) with no carry. COMPUTED: pack_bad = 0.

The carry index comes from the representative batch's packed words: c17 = bit 17 of Y12^Y8^nC0c1, c25 = bit 25 of
X0^Y0^Ap, c9a = bit 9 of w8^D0a1^nS0S5, c9b = bit 9 of om^E^w8.

Machine-unit charges (DERIVED from explicit operation lists in the code; **not audited by a Sol/CJ-style native-ledger
proof**):

| item | units |
|---|---|
| opened cluster, masked | rep T2 6 + nesting 56 + index 16 + guard 4 + broadcast 6 + 2 x (partner batch 66 + chunk 8) = **236** (was 368) |
| opened cluster, guard fired | 368 + 16 + 4 = 388 |
| per context, table | <= 34,484 (counted: max 33,940 measured) |
| per context, carry index | 19 x 2,341 representative batches = 44,479 |
| per context, fallback bound | 128 x 152 = 19,456 |
| once | 2^20 code reserve |

The second chunk (1 or 2 lanes) is charged as a full 7-lane batch.

## 4. Measurements (COMPUTED; seeds preregistered in seeds_prereg.txt before the runs)

**Full-context sweep**: seeds xf1-0000..0199, all 16,384 clusters per context, no halts.
Files: sweep_000_100.json and sweep_100_200.json (summary in reprice_out.txt).
- (i) **LOST = 0**, and the mask matched alive16 on every member of every non-fallback opened cluster (mismatch = 0).
  - Opened clusters: 1,468,672 (7,343 per context).
  - Further checks, all 0: prefix_split, pack_bad, and coref_bad (735,712 members checked against the straight-line
    co_ref).
- (ii) Guard: 64.6 clusters per context (0 or 128); fallback = 0.393% of opened clusters (5,778).
  - The exact two-prefix condition held in 114 of those clusters.
- (iii) Units per opened cluster: old 368; new mean 203.3 (fallback included); worst-case charge 236.
  - Survivors: {8: 687,884; 9: 638,064; 0: 136,946}.
  - The 0s are clusters the gate table opened through the other borrow candidate while the true prefix fails alive9.
    That is 9.4% of opened clusters, and their partners are now skipped for free.
- (iv) Table: at most 33,940 counted units per context (bound 34,484). Carry index: 44,479 per context.
- (v) Y9 fills per context: old layout 12,273.1 (min 392, max 28,758). This is consistent with CM's 16.8M-context
  sample mean of 12,427.3, which checks the re-implementation. Masked layout: **6,789.2** (min 392, max 13,331), which is
  0.545 x 12,466 and well inside the 2% rule.

**Faithful walk copy (walk_x = F.walk with the opened branch replaced, all in-run references kept)**:
- Preregistered 40 trials (nr = 5, the organizer shape): 40 of 40 identical to F.walk on e_lanes, passes, solver_calls,
  roots, opened, closed, halted and the first passing member. Mismatches 0, lost 0.
- Supplementary, not preregistered, all reported: 40 trials with nr = 120 (15,000 opened clusters).
  - Identical on e_lanes 54,185, passes 1,011 and solver_calls 257. Mismatches 0, lost 0. 56 fallbacks were exercised.
  - One trial (#33) returns a different first passing member in the same cluster (g = 287, j = 28 instead of j = 18).
    Group chunking changes the visiting order inside a cluster. Both are passing members, and every count is unchanged.
- Trial-shape units go up (5.7k to 34k) because the 34k table is spread over only 35 clusters. The run walks full
  contexts, and the reprice charges the table once per context.
- Files: trial_000_040.json, supp_trial_nr120_*.json, trial_summary.txt.

## 5. Reprice (price.py's formula; reprice.py, reprice_out.txt)

n = N - 368*A + 236*A + 98,419*(K+1) + 2^20, with A = A_BUDGET+1 and K = RUN_CONTEXTS.

| row | time_log2 |
|---|---|
| **decision row** | **63.313775 (delta -0.288865)** |
| stress: +40 units per opened cluster and +50,000 per context | 63.434 (still passes) |
| measured mean 203.3 units instead of 236 (information) | 63.2231 |

Unchanged budgets:
- E, pass and credit: the same T2-positive members are walked (LOST = 0 is proved in 2.4 and measured).
- Opening (A): the gate is unchanged.
- G: dominated pointwise (2.5).

Information only, not booked: a separate fill premise for the masked layout under CM's Hoeffding test (e^-7, range 35,493).
- This sample (n = 200) supports 11,485, which would give 63.2926.
- A large preregistered sample nearer the measured 6,789 could give about 63.19. GUESS target 7,000; it needs its own
  preregistered run (GPU-sized).

## 6. Not tested / open

- **No native implementation.** The unit charges in section 3 are explicit operation lists, not a CJ/CM-audited ledger.
  Not audited: register liveness and spills for the new resident words (table base, A[8..15], packed Ap, IX word, JU/JE).
  The 73-unit margin (309 vs 236) is the room for such corrections.
- Source size (64 KiB intake) of a modified frontline was not checked. pkgCJ was not edited.
- Full contexts were measured by a re-implementation of walk's batch and fill structure without budget halts. Only the
  faithful walk copy runs the solver/pass/E paths, and it ran on 80 trials (35 to 840 clusters each).
- Coverage, H1/H4/H5_exec and the other declared premises are unchanged and were not re-examined.

Files: walk_mask.py, reprice.py, sens_b16.py, diag_jsets.py (+ diag_jsets_out.txt), seeds_prereg.txt, facts.json,
step1_*.txt, sweep_*.json/log, plainchunk_*.json/log, trial_*.json/log, supp_trial_*.json/log, trial_summary.txt,
reprice_out.txt. Test runs on seeds outside the preregistered list: test_*.json.
