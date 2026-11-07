# b3r4: B3R4e (9f69f1cc) with a 7-byte table entry (40-bit key), 2026-10-15

## Number
**time_log2 = 124.99287** (kappa 14, Tp 101, tmax 7,488, P_key included, Appendix A `certify` passed: P_F >= 0.390000004596). The memory term stays 0 (1,048,472 B <= 2^20).
Base: 125.06177 (filed ledger of 9f69f1cc, reproduced here byte for byte). **Delta -0.06890 bit.** EDGE_AUDIT predicted 124.99285 without P_key. P_key costs 0.00007 bit, so the forecast holds.

Arithmetic (run1_s_k14_t7488.out):
- Memory available to the table: 2^20 - 64 (spare) - 954,072 (code, 26,502 x 36) - 25,600 (800 registers) - 16,384 (counters) = 52,456 B.
- Entry is 7 B: key low 32 bits (8 per word) + key high 8 bits (32 per word) + 2-byte trail number (16 per word). 32 entries fill exactly 4 + 1 + 2 = 7 words = 224 B. floor(52,456 / 224) = 234 blocks, so **tmax = 7,488** and the table is 52,416 B word-aligned. Search-phase peak is 996,056 + 52,416 = **1,048,472 B**.
- Key = the 33 bits of x above bit 121 followed by the 7 low bits of F (F < Tp = 101 <= 2^7), so kb = 40 - 7 = 33. P_key = C(7488, 2) / (2^33 * 101) = 28,031,328 / 867,583,393,792 = **3.231e-05**.
- Plan (the same appA code with only ENTRY, KEYBITS, KAPPA and tmax changed): Tp = 101, L = 2^122/101, B = 1409734332861 x 10^24, c = ceil(14 L) = 736997700633220682006071241343557389, q = Q/L ~ 6,856 trails.
- N = main 24,459 B = 3.44807e40 + recovery 2 (c + 2^48)(836 + 64) + 600 = 1.32660e39 + stage-1 4.705e32 + slices 6.5e24 + finished trails 196,664,832 + cut 4,200 + setup 25,587,600 = **35807288379136601910480891848615323682832**.
- log2(N / 846) = 124.9928632125. Certificate: 2^12499286 * 846^100000 <= N^100000 < 2^12499287 * 846^100000, so time_log2 = **124.99287**.
- Why it pays: tmax goes from 5,245 to 7,488 (+43%). That lets Tp go from 67 to 101: shorter trails, recovery falls from 4.94% to 3.70% of N, and the lanes-over-trails loss shrinks (q 4,709 -> 6,856). B falls 3.4%.

## What changed (only these constants; every formula is untouched)
| | filed b4e | b3r4 |
|---|---|---|
| ENTRY | 10 B (key 8 + t 2) | 7 B (key 5 + t 2) |
| key bits / kb | 64 / 57 | 40 / 33 |
| KAPPA_256 | 13 | 14 (re-optimised) |
| tmax | 5,245 (floor(52,456/10)) | 7,488 (word-aligned 224-B blocks) |
| Tp | 67 | 101 |
| P_key | 1.4e-12 | 3.23e-05 |
| memory | 1,048,506 | 1,048,472 |
| time_log2 | 125.06177 | 124.99287 |

## Minutes-scale checks (local Windows python 3.14, BelowNormal priority, at most 2 processes, each run about 40 s)
| run | file | result | run 2 |
|---|---|---|---|
| filed appA, unchanged | run1_base.out / run2_base.out | 125.06177, certified 0.390000005436 (= filed appA.out) | identical (diff empty) |
| ENTRY 7, kb 40, kappa 13, tmax 7,493 | run1_e7k13 / run2_e7k13 | 124.99379, cert 0.390000005036, Tp 100 | identical |
| ENTRY 7, kb 40, kappa 14, tmax 7,493 | run1_e7k14 / run2_e7k14 | 124.99287, cert 0.390000004596, Tp 101 | identical |
| ENTRY 7, kb 40, kappa 14, **tmax 7,488 (word-aligned)** | run1_s_k14_t7488 / run2_s_k14_t7488 | **124.99287**, cert 0.390000004596, mem 1,048,472 | identical |
| kappa 12 / 15 (tmax 7,493) | run1_e7k12 / run1_e7k15 | 124.99675 / 124.99471 | single run (sensitivity only) |

Each run is the full appA: plan, float bound, exact `certify` (K = 20,000, 60-digit decimals, outward rounding), and the integer certificate. The `assert pc >= 39/100` passed in every run. Scripts: appA_base.py (copy of the filed one), appA_e7.py (argv: kappa), appA_sens.py (argv: kappa, entry, keybits, [tmax]).

## Premises and sensitivity
No new premise. P_key is a counted failure term of Lemma 2 for the random function F, like the rest of the lemma. H1 (model) and H3 (800 registers, 36 B/instr) are as filed.
| variant | time_log2 | vs b3r4 |
|---|---|---|
| kappa 12 / 13 / **14** / 15 | 124.99675 / 124.99379 / **124.99287** / 124.99471 | +0.0039 / +0.0009 / 0 / +0.0018 |
| P_key removed (64-bit key at 7 B; not realisable, isolates the term) | 124.99280 | -0.00007 |
| 6-byte entry (32-bit key, kb 25, P_key 9.6e-3, Tp 118) | 124.99378 | +0.0009 (worse) |
| tmax 7,493 (unaligned) vs 7,488 | 124.99287 both | 0 |
| key-scan charge 3 -> 10 ops/key | +7488^2 x 7 = 3.9e8 ops of 3.6e40 | 0 |
Not covered: entry packing below 7 B (quotient the key through a slot index), an ESTIMATE of another -0.01 that was not run. Memory above 2^20 was not stacked here.

## What a package rebuild needs (work on a copy; 9f69f1cc is still validating and its 10 B / 2-pass design has no ruling yet)
1. `experiments/bsrho.py` (61,944 B now, so about 3.5 KB under the 64 KiB limit; the edits are about +/- 100 B):
   - `ENTRY = 7` and its comment: key 5 B (low 32 bits + high 8 bits arrays) + t 2 B. `KAPPA_256 = 14`.
   - `pack_entry`: `assert key < 1 << 40`, `key | (t << 40)`. `unpack_entry`: mask `(1 << 40) - 1`, `>> 40`.
   - `_plan`: `kb=min(40 - fb, n - D)`. `_lossq` key_false_match: `min(40 - (Tp - 1).bit_length(), 134)`.
   - `machine_constants`: `tmax = ((MEM_LIMIT - SPARE - code - R*32 - COUNTERS - ADVICE) // (ENTRY*32)) * 32`, which gives 7,488 and a word-aligned table. Use the same formula in appA.
   - Rerun `--selftest`, `--ledger`, `--loss`, and the two organizer experiments (`bsrho-n18`, `proj-k0-w256`; 2.5 s and 4.1 s), twice each. n = 18 is unaffected (kb = min(40, 16) = 16).
2. `appA.py` / proof Appendix A: the same four constant changes, then rerun (40 s) and paste appA.out.
3. `proof.md`:
   - Section 2: Tp 101, L = 2^122/101 = 2^115.342, key 33 + 7 bits, and the new constants B, Q = 256 B, e2max, c, tmax 7,488; the t < 2^16 sentence (7,488 + 1 + 256).
   - Section 3: the ledger table rows and N, the certificate, and the handler text. There are now three field stores (low key, high byte, t) instead of two; check that the handler total stays below the 3,800 charge (filed: below 3,550). Key scan: 8 low keys per word, 8 ops per word, high byte only on a low match; keep the charge at 3 per key.
   - Section 3.5: the R-sweep table is regenerated by the program.
   - Lemma 1: "bits above 154" and "A 40-bit key match without a merge ends the run".
   - Lemma 2: q, k, z*, w, kap0, theta and the P_F line from `--loss`; P_key kb = 33.
   - Section 7 memory: 7,488 x 7 = 52,416 B in three arrays; peak 1,048,472; setup phase unchanged at 1,042,104.
4. `claim.json` (score 124.99287, memory), `submission-note.md`, and `experiments/manifest.json` (hash and size of bsrho.py).
5. Estimate: 2-3 h of editing plus about 5 min of checks. No new lemma.
