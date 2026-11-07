# Lever b3r3: B3R3v2 (42a0c301, filed 124.83986) with the B3R4e levers and kappa 16

Date 2026-10-15, 22:00-22:40 MDT. Ledger and certificate work only. Nothing built, staged or submitted. No filed package was touched: the inputs are copies in this folder.

## Result

| config (all: R800, CMAX 1, two-pass recovery, kappa 16) | entry | key bits | Tp | tmax | certified P_lower | time_log2 | delta vs filed |
|---|---:|---:|---:|---:|---|---:|---:|
| filed 42a0c301 (R1024, CMAX 2, 1 pass, kappa 11), regression | 25 | 64 | 174 | 12,494 | 0.390000006430 | 124.83986 | 0 |
| **A: 10-byte entry (B3R4e design)** | 10 | 64 | 473 | 31,953 | 0.390000003867 | **124.78880** | **-0.05106** |
| **B: 8-byte entry (48-bit key + 16-bit trail number)** | 8 | 48 | 596 | 39,941 | 0.390000003984 | **124.78228** | **-0.05758** |
| C: 7-byte entry (40-bit key + 16-bit trail number) | 7 | 40 | 682 | 45,647 | 0.390000004075 | 124.78243 | -0.05743 |

- The audit's 124.7897 for A is confirmed and slightly improved: 124.78880. The gap comes from CMAX 1 (the audit ran CMAX 2 on this row) and the full 20,000-panel grid.
- The audit's 124.7797 for the 7-byte entry is **not** right. It left out the key false-match term. With 40 key bits, P_key = 1.42e-3 (not 3e-5), so the certified value is 124.78243. An **8-byte entry is the better choice**: P_key = 4.9e-6, giving 124.78228. That is 0.0002 below C and 0.0065 below A.
- Every number in the table is from the program's own Appendix A code: `certify()` uses exact rationals and 60-digit decimals at K = 20,000 panels, and the `2^a * 638^100000` certificate is kept. Only constants were changed (see "What changed").

## Arithmetic

Memory, with code = (17,275 + 1,810) x 36 = 687,060 B, registers 800 x 32 = 25,600 B and counters 16,384 B:
- tmax = floor((1,048,576 - 687,060 - 25,600 - 16,384) / ENTRY) = floor(319,532 / ENTRY), which gives 31,953 (10 B), 39,941 (8 B) and 45,647 (7 B).
- Peak memory = 1,048,574 (A), 1,048,572 (B) and 1,048,573 (C), all <= 2^20, so the memory term is 0. Trail numbers stay below 2^16: at most tmax + 1 cut trail + 256 starts = 46,904 (C).
- Setup phase: unchanged at 981,617 B. The generator is not changed. The idle region is 10 x 31,953 + 25,600 + 16,384 = 361,514 B (A) and 361,512 B (B). Both hold the generator image of 73,440 B plus its scratch of 204,733 B = 278,173 B.

Ledger A (word operations; unit C = 638):
- main loop: B x 17,275 = 1,343,092,466,569e24 x 17,275 = 2.32019224e40 (98.977%)
- recovery: 2 x (c + 2^48) x (603 + 64) + 600 = 2.39924248e38 (1.024%), with c = 179,853,259,471,954,790,414,045,775,598,186,159 = ceil(16 L) and L = 2^122 / 473
- stage-1 hits 4.48e32, slices 6.2e24, finished trails 31,953 x (3,800 + 3 x 31,953) = 3,184,404,027, cut trails 1 x 4,200, setup and generator 11,329,200
- N = 23,441,847,056,420,545,367,473,923,509,617,833,795,037, and log2(N / 638) = 124.7887974. Certificate: 2^12478879 x 638^100000 <= N^100000 < 2^12478880 x 638^100000, so time_log2 = 124.78880.
- q = Q / L = 30,587.75 trails of mean length 2^113.114; Q = 2^128.0150.

Ledger B: B = 1,339,834,324,399e24; main 2.31456380e40 (99.184%); recovery 1.90409680e38 (0.816%); finished trails 4,937,626,243; N = 23,336,048,081,358,559,508,089,839,724,536,741,495,315; log2(N / 638) = 124.7822714, so time_log2 = 124.78228. q = 38,448.36 trails of length 2^112.781.

Key false match = tmax (tmax - 1) / 2 x 2^-(min(KEYBITS - fb, 134) + log2 Tp), with fb = bit length of (Tp - 1):
- A: 2^-(55 + 8.885), which gives 3.0e-11
- B: 2^-(38 + 9.219), which gives 4.87e-6
- C: 2^-(30 + 9.414), which gives 1.42e-3. This is the term the audit left out.

## What changed (against the filed `appA.py`; the same constants must go into `bsrho.py`)
1. KAPPA 11 -> 16. The kappa sweep on A (quick grid) is flat from 15 to 17: k14 124.79045, k15 124.78905, k16 124.78887, k17 124.78907, k18 124.78958. On B: k15 124.78278, k16 124.78235, k17 124.78244.
2. CMAX 2 -> 1. The Lemma 2 v2 code is generic in CMAX; proof line 187 already says "Setting CMAX = 1 gives the text of the later entries". At kappa 16, CMAX 1 is 0.0008 better than CMAX 2 (124.78887 against 124.78968).
3. REGISTERS 1,024 -> 800. The kernel needs 771 (selftest: peak live 771, moves 0), so spill_ops(800) = 0 and the main body stays at 17,275.
4. ENTRY 25 -> 10 (A) or 8 (B). No length is stored. Recovery takes two passes (pass 1 recomputes both lengths), so the recovery row becomes 2 x capr x (603 + 64) + 600. OTHER_CODE stays 1,810: B3R4e's own formula, 1,000 + circuit + 47 + 160, gives 1,000 + 603 + 47 + 160 = 1,810, which is the filed value.
5. B only: key 48 bits (kb = min(48 - fb, 134)) and trail number 16 bits, packed into 8 bytes.
- Tp: kept as the filed code's bisection (the largest Tp that reaches 0.39 at the table's mean). I checked smaller Tp on A and all were worse: 470 gives 124.78907, 465 gives 124.78941, 430 gives 124.79204, 380 gives 124.79662. Time is monotone in Tp up to the boundary, so 473 is the best plan.
- SPARE 64 (B3R4e's margin under 2^20): tmax becomes 31,946 (A) and 39,933 (B), with time_log2 unchanged at 5 decimals (quick grid). It can be adopted for free.

## Minutes-scale checks (all local, nice 10, at most 2 processes)
- **Regression:** `appA_v3.py` with default constants reproduces the filed run exactly: Tp 174, tmax 12,494, P certified 0.390000006430, time_log2 124.83986 (`cert/filed_config_regression.out`). This shows my edit changed only the constants.
- **Two runs each:** A, B and C were each run twice with the full certificate, about 45 s per run (`cert/e*_run1.out`, `cert/e*_run2.out`). The two runs of each config are byte-identical except for the timestamp.
- **Quick grid sweeps:** 1,500 panels, no certify (`sweep/`). These give kappa x CMAX x entry and the Tp checks. The quick grid sits +0.00007 above the certified value (124.78887 against 124.78880).
- I stopped two scan jobs of my own when they hit the 10-minute cap (a generic Tp scan, and the Tp = 620 point on B, which never converged). Neither result is used. The monotone Tp check on A replaces them.

## Premises and sensitivity
- H1 is unchanged: the same random-function premise and clauses (a) to (d); only the numbers in the scope change, for example "about 30,600 trails of mean length 2^113.11" (A).
- H1 (d) hazard-deficit sensitivity was re-planned with Tp re-optimised. This is a plan-only quick grid with the hazard scaled by (1 - eps):

| eps | A: Tp, extra bits | B: Tp, extra bits | filed (for comparison) |
|---:|---|---|---|
| 0.01 | 471, +0.0072 | 593, +0.0073 | +0.0073 |
| 0.05 | 461, +0.0370 | 581, +0.0370 | +0.0372 |
| 0.10 | 449, +0.0760 | 565, +0.0760 | +0.0760 |
| 0.25 | 410, +0.2075 | 516, +0.2075 | +0.2078 |

- H3 (register file) becomes smaller: 800 declared against 771 used, instead of 1,024. This is a less aggressive claim than the filed one.
- **Not run here (more than the minutes budget):** the two-pass recovery for r3 in `bsrho.py` (`--selftest`, the n = 18 experiment) and the rebuilt package. These belong to the rebuild below. B3R4e already runs the identical two-pass code; it is filed and validating, with no ruling yet.

## What a package rebuild needs (variant A or B; B recommended, A is the B3R4e-identical design)
1. In `experiments/bsrho.py` (copy of `blake3_r3/pivotv2/pkg/blake3/experiments/bsrho.py`), apply the r4e diff:
   - CMAX = 1, KAPPA_256 = 16, REGISTERS = 800, ENTRY = 10 or 8, RECOVER_PASSES = 2
   - recovery row x RECOVER_PASSES
   - `trail_lengths()`, two-pass `recover(p, r, t0, t1, f2)`, `pack_entry(key, t)` / `unpack_entry` without the length, and the call site in the search loop (r4e lines 828-908)
   - optional SPARE 64
   - For B, also: `pack_entry` asserts key < 2^48 and stores t << 48; `_plan` kb = min(48 - fb, n - D); and the `_lossq` key term uses 48.
   - Keep the r3 generator, the bisection Tp, OTHER_CODE 1,810 and the comb form of the cut term.
2. In `appA.py`, use exactly the constants of `appA_v3.py` (config A or B): KAPPA 16, CMAX 1, REGFILE 800 x 32, ENTRY 10 or 8, the key bits, and the recovery row "2 * (c + 2^48) * (603 + 64) + 600". Expected output is in `cert/e10_kb64_k16_c1_run1.out` or `cert/e8_kb48_k16_c1_run1.out`.
3. Run `--selftest`, `--ledger`, `--loss` and appA. The ledger must print 124.78880 (A) or 124.78228 (B). Regenerate the experiment outputs and manifest hashes (bsrho-n18 and proj-k0-w256 run the changed recovery and entry code).
4. In `proof.md`, edit:
   - the summary (line 4)
   - algorithm steps 5 and 6 (entry without length, two-pass recovery, halts)
   - 3.3: the pass-1 batch charge inside the 64 extra ops, using B3R4e proof line 54 as the template
   - 3.4: the ledger table
   - 3.5: the register table with an R = 800 row
   - Section 4: CMAX = 1 everywhere (lines 99, 141, 164, 182, 187, 233, 237); kappa 16; n2 = k + 257
   - Section 7: memory, tmax and entry layout
   - Appendix A: the listing
   - the H1 sensitivity numbers above
5. In `claim.json`, set time_log2 and update the restrictions: Tp 473 or 596; 31,953 x 10 B or 39,941 x 8 B; 1 cut trail; 800 registers; memory 1,048,574 or 1,048,572; the recovery wording. Also update H1 scope (trail count and length), the sensitivity, and the `proof:` line ranges in evidence_ids. Credit the levers to our B3R4e (9f69f1cc).
6. Run the intake checks (sources <= 64 KiB, restrictions <= 1,024 chars each). Estimate: about 2-3 h of build plus about 10 min of runs. Filing needs the owner's go.

Files (all in `./research/levers_wave1/b3r3/`):
- `appA_v3.py`: the filed appA with environment-set constants
- `appA_r3_filed.py`, `bsrho_r3_filed.py`, `appA_r4e.py`, `bsrho_r4e.py`: copies
- `cert/`: certified runs
- `sweep/`: quick grid
- `run.sh`, `sweep.sh`, `jobC.sh`, `jobS.sh`, `jobT.sh`, `jobA.sh`, `jobB.sh`: runners
