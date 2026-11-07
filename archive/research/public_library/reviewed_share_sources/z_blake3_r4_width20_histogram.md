# Archived BLAKE3 r4 width-20 occupancy measurement

Reviewed from the complete mapped-share record on 2026-10-29. This is a curated scientific note, not a newly executed experiment.

Original filename: `independent_blake3_r4_width20_hist_2026-10-25.json`.
Original SHA-256: `40ab4def3125578a3df7d54bc758f26dd7b384d0ed4420ec690a5f23104b71e3`.

The record gives four BLAKE3 rounds, N = 1,048,576, seed 0xB3A4 and two input modes. The nonempty bucket histogram lists pairs (bucket occupancy, number of buckets):

| Occupancy | Counter mode | Random mode |
|---:|---:|---:|
| 1 | 385689 | 385899 |
| 2 | 192905 | 193195 |
| 3 | 64277 | 64216 |
| 4 | 16151 | 15953 |
| 5 | 3196 | 3217 |
| 6 | 514 | 533 |
| 7 | 70 | 72 |
| 8 | 11 | 5 |

Reported counter totals: 662,813 occupied buckets, 524,090 colliding unordered pairs, maximum bucket 8, chi-square 1,048,180. Reported random totals: 663,090 occupied buckets, 523,378 pairs, maximum bucket 8, chi-square 1,046,756. Original elapsed seconds were 46.0170 and 46.5773; these are historical wall-clock observations, not contest work charges.

Review arithmetic independently recomputed sum(k*h[k]) = N, sum(h[k]) = occupied and sum(k*(k-1)/2*h[k]) = pairs in each mode. If the intended comparison is N independent uniform outputs into N buckets, expected pairs are (N-1)/2 = 524,287.5; the observed/expected ratios are 0.9996232983 and 0.9982652648. Empty buckets derived as N minus occupied are 385,763 and 385,486. No new hash evaluations were run.

Scope limitation: the compact original does not include a generator digest, exact message encoding, output projection, dependency model, or confidence procedure. The filename identifies width 20, but the record alone cannot bind it to a complete fixed-target probability claim. The two small occupancy comparisons do not establish a random-function hazard over 2^128 adaptive evaluations or a full 256-bit collision.
