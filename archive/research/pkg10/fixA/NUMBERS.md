# fixA: the neighbour path in the program, budgets as halts, upper-bound charge

Files in this folder: halfsearch.py (the merged program, sha256
5d4fe4e088ec1f213f5d97b8fd2cc99aabaa9b3b19cf7edb0c92f3c8f400e09f),
selftest_2000_seed1.out, cluster_selftest_50000_seed1.out, this file.
FACTOR = 92675904, EQUIVALENTS = 4102 and RUN_PAIRS are unchanged.

## 1. Charge and time_log2

Charge per trial-equivalent, an upper bound by construction:
1.647618 (exact fraction in the program), rounded up: **1.65** (was 1.71).

    time_log2 = 123.339 - log2(92,675,904) + log2(1.65 / 34) + 0.012
              = 92.5203, rounded up 92.53 (was 92.58).

No 4 per cent margin is applied, because nothing in the charge is now left
uncounted except the two loop-control rows stated in words (section 4). With
the old margin the charge would be 1.7135, rounded up 1.72, time_log2 92.5803.

## 2. Which entries STAGE_2_BUDGET covers (resolved)

The figures in the task mix units. RUN_PAIRS counts all 2^32 values of X2 of
an outer step; the cluster run walks only the representative values (bits
14, 30, 31 zero), one in eight. Per representative value of X2 there are
16,384 representatives in 2,341 words and, at the measured 0.5625, 9,216
neighbour words. The measured 0.1364 is per REPRESENTATIVE, not per
neighbour word: it is 0.0624630 open gates times 2.183 entered words per
open cluster, and proof.md Section 10 bounds this share by 2^-8 times the
yield, 0.156328, per representative. So at measured rates a representative
value of X2 sends 2,341 * 0.02622 = 61.4 representative words and 16,384 *
0.1364 = 2,234.8 neighbour words into stage 2 (not 1,257).

The old STAGE_2_BUDGET (BATCHES * RUN_PAIRS >> 5) allowed 585.16 entries per
value of X2, that is 4,681.25 per representative value of X2: 2.00 times the
number of representative words of a run. As a budget on representative
words alone it could never be reached; as a budget on all entries it would
have to be charged at 4,681.25 per representative value.

In the merged program each entry into stage 2 is counted by exactly one
budget, through the cell that the part "entry count" of packed_batch()
compares with:

- an entry of a REPRESENTATIVE word: STAGE_2_BUDGET (cell "stage-2 budget");
- an entry of a NEIGHBOUR word: NEIGHBOUR_2_BUDGET (cell "neighbour stage-2
  budget"), with its own count, stored and loaded at each cluster boundary.

STAGE_2_BUDGET is therefore CHANGED: it is now 1/32 of the representative
words of a run, 73.16 per representative value of X2, 1.19 times the 61.4
above (the same room as before over 0.02622). The share 0.02622 was measured
on batches of consecutive members, not on representative words; that it
holds for representative words is part of the H3 premise.

If the main session keeps the old STAGE_2_BUDGET value instead, it does not
bind below the representative words of a run, every representative word must
be charged with stage 2, and the charge is 2.1032, rounded up 2.11,
time_log2 92.8751.

## 3. The four budgets (exact Python names, formulas, values)

Shared constants: REPRESENTATIVES_PER_X2 = 16,384; REP_WORDS = 2,341;
REPRESENTATIVES = RUN_PAIRS * CLASS_SIZE >> 6 = RUN_PAIRS * 2048
= 44,755,556,569,243,157,464,525,850,624 = 2^95.176.

- STAGE_2_BUDGET = (RUN_PAIRS * REP_WORDS) >> (3 + STAGE_2_LOG2_SHARE)
  = 199,838,176,591,106,856,583,509,476 = 2^87.369 (STAGE_2_LOG2_SHARE = 5)
- GATE_BUDGET = REPRESENTATIVES * 12 * 624630 // 10 ** 8
  = 3,354,679,595,981,562,413,648,013,849 = 2^91.438
- NEIGHBOUR_A_BUDGET = REPRESENTATIVES * 12 * 5625 // (9 * 10 ** 5) * 9
  = 30,210,000,684,239,131,288,554,949,164 = 2^94.609
- NEIGHBOUR_2_BUDGET = REPRESENTATIVES * 12 * 1364 // 10 ** 5
  = 7,325,589,499,253,720,013,793,591,230 = 2^92.565

Shares: 1/32 of the representative words; 0.0749556 = 1.2 * 0.0624630,
0.675 = 1.2 * 0.5625 and 0.16368 = 1.2 * 0.1364 of the representatives.
The old STAGE_2_BUDGET was 12,787,594,555,039,644,218,799,538,466 (2^93.369).

What each one counts. The program keeps one count per budget, advances it
before the work it counts and halts with failure when it equals the budget.

- STAGE_2_BUDGET: representative words that enter stage 2 (counter register,
  part "entry count" of the representative word's batch).
- GATE_BUDGET: open gates, one per open lane, in cluster_entry() (count in
  memory, advanced by one). It also bounds the dispatches and the cluster
  entries and exits, since every dispatched word has an open lane.
- NEIGHBOUR_A_BUDGET: neighbour words that run stage A, in cluster_entry()
  (count in memory, advanced by nine). It is a multiple of nine and above
  9 * GATE_BUDGET, so it can never be reached first; the program checks this.
- NEIGHBOUR_2_BUDGET: neighbour words that enter stage 2 (part "entry count"
  of the neighbour word's batch).

For the success bound: GATE_BUDGET and NEIGHBOUR_2_BUDGET are two new halts
and need an allowance; NEIGHBOUR_A_BUDGET needs none. The present bound
0.39047 leaves 0.00047 above 0.39 for them.

## 4. Derivation of the charge (from the program's counts)

Every row is units (operations + loads + stores counted by the program's
Machine) times an upper bound on how often a run executes it. The walk is
RUN_PAIRS rounded up to whole values of C0.d1: 1,184,670 * 2^64 pairs.

| Row | Count over the run | Units | Per representative |
| --- | --- | ---: | ---: |
| loop control per value of C0.d1 (in words) | 1,184,670 | 16 | 0.000000 |
| loop control per outer step (in words) | 2^52.176 | 8 | 0.000000 |
| outer step | 2^52.176 | 260 | 0.000000 |
| table build, 149,797 words per outer step | 2^69.369 | 74 | 0.000001 |
| group: 8 middle steps, mixed words, loop entry | 2^81.176 | 1,250 | 0.076294 |
| representative word, stage A and store of z | 2^92.369 | 48 | 6.858398 |
| representative word, gate test and load of z | 2^92.369 | 10 | 1.428833 |
| representative word, stage 2 | STAGE_2_BUDGET | 135 | 0.602789 |
| open-gate word: gate word routed, dispatch | GATE_BUDGET | 31 | 2.323623 |
| open gate: cluster entry and exit | GATE_BUDGET | 33 | 2.473534 |
| neighbour word, stage A | NEIGHBOUR_A_BUDGET | 47 | 31.724992 |
| neighbour word, stage 2 | NEIGHBOUR_2_BUDGET | 135 | 22.096795 |
| total | | | 67.585260 |

Charge = total * FACTOR / 2^127 = 67.585260 / 41.02 (to within 3 parts in
10^7) = 1.647618.

Routing (each value that crosses a boundary between pieces is stored and
loaded): z, 2 per representative word; the gate word, 2 per word with an
open gate; per open gate the gate word, the zero, the list position and the
representative stage-2 count stored at entry and loaded at exit (8), and the
neighbour stage-2 count loaded at entry and stored at exit (2). Only RESIDENT
and the two counter registers stay in registers between pieces, and every
piece runs within 16 registers on its own machine (section 5).

Group units: middle step of the representative value 128, of each of the
seven others 122, mixed words 258, class loop entry and list start 10.
Cluster entry 28: route out 3, gate budget test 7, neighbour-A budget test
7, neighbour position 9, j stored 1, neighbour stage-2 count loaded 1.
Cluster exit 5. Dispatch 30 (29 and the load of the gate word).

Conventions and limits: list and table loads at the list position cost one
load with no address arithmetic, as in the filed program; the neighbour
position itself is formed and counted. Stage 2 is charged whole at 135; the
split at the cheap test is not in the program and is not used. The lists U
and V of the cluster layout have 149,797 words each (2,341 representative
words, then nine per representative); computing them once per run is below
2^28 operations, a bound in words, not a count, in place of the 2^24 term.

## 5. Self-test results

- `--selftest 2000 1`: exit 0. Output byte-identical to the submitted
  program's: 14,000 of 14,000 lanes right, stage A 37 + 10, stage 2 105 + 30,
  16 registers, 131,072 members, 128 of 128 and 65,536 of 65,536 patterns.
- Both experiments: outputs byte-identical to the submitted program's on 64
  half-collision seeds and 24 residual-search seeds; the predicted
  observations do not change.
- `--cluster-selftest 50000 1`: exit 0, about 6 seconds. 50,304 trials in
  786 clusters (126 cases): h1 formed from z equals h1 of the compression of
  the real message A in 50,304; rule A agrees in 50,304; the gate on z equals
  the gate on that h1 in 786 of 786 clusters; clearing the six flipped bits
  gives the representative back in 49,518 of 49,518; 786 of 786 clusters have
  64 distinct trials. The whole path ran on the machine for 62 representative
  words: 434 of 434 representative lanes right, 434 of 434 gate lanes, 62 of
  62 dispatches, 386 of 386 clusters right (positions, counts, routed values,
  table words, mixed words), 24,318 of 24,318 neighbour lanes right against
  both real messages and their digests, stored words right in 62 of 62.
  Counts the same in every case; registers: representative word 16,
  neighbour word 16, cluster entry 15, dispatch 14, gate test 13, middle
  steps 13, cluster exit 12, outer step 11, table build 7, mixed words 5; no
  sum leaves its lane. The budget test halts when its count reaches the
  budget.
- The reference of the cluster self-test is now the program's own 2-round
  compression of the real messages, not research/h8/twolevel/tl_ref.py,
  which is not in the package.
