# Poseidon executed-outcome program: profile, faster build, validation, r6/r7 estimates, speculative centres

2026-10-15, written by a subagent. Sources: `exec_r6fast/` (new; `exec_r6mt/` and the running cloud run `/root/hs/mt/run_r6_T24` were not touched). Nothing was submitted.
Machine: local WSL (Ryzen 9 7900X, 22 vCPU), nice 10, under heavy load from other jobs (load average 12 to 29 during the day), so all wall-clock figures are noisy; CPU-time, serial-time and operation counts are the reliable numbers.

## Summary

- Profile (r3, 8 threads): stage C is 90 % of the work and runs on 7.2 of 8 threads; stage D is 9 % of the work but 28.5 % of the wall: the Euclid base case and the half-gcd levels with rows up to 2^10 are serial, rows of 2^15 are serial by a threshold gap, rows 2^11..2^18 use 2 to 5 threads. Scaled to r6 that is about 15 h per trial that more threads cannot shorten.
- exec_r6fast: task mode and sub-tree mode for the half-gcd and all transforms, lower split thresholds, and the plain 2^(a+1) ("rows 2") plan. Same algorithmic counts for the unchanged plans (checked at RR=2 full runs and at RR=3/RR=4-size benches); with rows 2 about -31 % operations at the r3/r6 shape, -4.3 GB at r6 (26.75 GB live).
- Model for r6 per trial at T=24: 34 h -> 22 h; at T=96: 20 h -> 12 h; remaining floor about 6 h. Speculative centres (k = 2 or 3 processes) pay from about 32 threads up.
- The local machine corrupts results at random under load (section 0): full RR=3/RR=4 validation could not be done here. Verdict: keep the running r6 run; restart with exec_r6fast only after a clean RR=3/RR=4 validation, an r6-size smoke run and the proof text, and only if that is done early (section 7).

## 0. Read first: the local machine computes wrong results at random under load

While validating, identical binaries gave different results on this machine. This is not a code bug and it is not specific to the new build:

- `exec_r6mt` sources, unchanged except for checksum prints, RR=1, one thread, ASLR off, 64 runs at 64 stack offsets: 47 gave the correct `x^E mod g` (checksum `ea2ea8d8...`), 17 gave 17 different wrong values. In each wrong run the per-step checksums agree with the correct run up to a random powering step (s3, s40, s44, s66, s87, s141, s155, s197, s214, ...) and differ from there on.
- Re-running the same binary at the same stack offset passes or fails at random (offset 64: failed at s66, then passed, then failed at s141; offset 16: passed, then failed at s3, then passed). Pinning to one vCPU with `taskset`: 5 failures in 30 runs, on vCPUs 8, 20 and 21, and passes on the same vCPUs on repeat. One run at a time (no other process of mine): 4 failures in 6. A build without AVX-512 (`-mno-avx512f`) fails too. g, mu and the twiddle table were always correct; the corruption happens inside the squaring loop.
- Effect on runs: a corrupted trial reports "gcd degree 0" for a centre that succeeds (RR=1 centre 1, RR=2 centre 1, RR=3 centre 1), and the run then goes on to the next genuine success (RR=1 centre 5, RR=2 centre 3, RR=3 centre 4). The first local RR=3 run of the day (8 threads, plain exec_r6mt code) reported centres 1, 2 and 3 as failed and succeeded at centre 4; centre 1 succeeds in every clean run.
- What it is not: not the stack layout (re-runs at a fixed offset differ), not one vCPU, not AVX-512 state, not page migration (`pgmigrate_success 0`, `compact_stall 0`), not memory pressure (39 GB free). Windows logs two "fatal hardware error" WHEA events (2026-02-04, 2026-02-12), nothing recent. Leading hypothesis: CPU or memory instability under sustained all-core load (non-ECC desktop; an undervolt or memory overclock would fit). Not proven.
- The cloud runs look clean: r4 (centre 1 genuinely fails: two independent runs agree on its charge 398,228,799,447) and r5 (centre 1 succeeds) are consistent. The running r6 run is on that box.

Owner actions (not done by me): treat every local result (this file's local wall times, other teams' local SAT runs) as unverified until the machine passes a stress test with known answers (e.g. memtest86+, or prime95 blend/large FFT for an hour); consider resetting PBO / Curve Optimizer / EXPO to defaults. A cheap self-check in the counted program is possible (section 8).

Consequence for this work: results are compared by majority over repeated short runs and by the operation counts that do not depend on the data (section 4); runs with a fault are kept, not hidden (`exec_r6fast/val_out/`, `prof_out/`, `test/out/fault_scan*.txt`, `test/out/bench_chk_all.txt`). The rate today was about one fault per 15-30 G operations, which rules out a clean full RR=3 or RR=4 run here.

## 1. Profile: where the serial time goes (r3, one trial, 8 threads, `exec_r6mt` code)

Built from `exec_r6fast` with `-DNO_R2 -DNO_TK -DNO_ST -DPAR_LMIN_ELEM=15 -DPAR_LMIN_LIN=17` (= `exec_r6mt` behaviour) plus `-DPROF` (rdtsc timers, 8.7 ns each; nothing counted). Main-thread wall split into serial segments (only the main thread runs) and dispatch segments; "busy" is the summed time of all chunks on all threads. File `exec_r6fast/prof_out/r3_base1_T8_err.txt`, summarised by `prof_table.py`.

Whole trial: wall 1,219.6 s; serial 227.4 s (18.6 % of wall); dispatch wall 992.2 s; busy 6,467.5 thread-s (inflated by preemption, user CPU was 5,094 s).

| part | serial s | dispatch wall s | busy thread-s | threads used | share of wall | share of work |
|---|---:|---:|---:|---:|---:|---:|
| B build g | 0.0 | 4.8 | 36.8 | 7.7 | 0.4 % | 0.5 % |
| C Newton | 0.5 | 4.2 | 21.7 | 5.2 | 0.4 % | 0.3 % |
| C conv_sq | 0.2 | 268.1 | 1,918.9 | 7.2 | 22.0 % | 28.7 % |
| C otf mu (N) | 0.3 | 387.3 | 2,768.8 | 7.2 | 31.8 % | 41.4 % |
| C otf g (N') | 3.7 | 199.3 | 1,333.5 | 6.7 | 16.7 % | 20.0 % |
| C linear loops, mulx | 0.0 | 2.9 | 11.1 | 3-6 | 0.2 % | 0.2 % |
| D base case (Euclid, k <= 96) | 66.3 | 0 | 0 | 1 | 5.4 % | 1.0 % |
| D mat_mulQ + divrem | 15.5 | 0 | 0 | 1 | 1.3 % | 0.2 % |
| D apply_inv + mat_mul, rows <= 2^10 | 70.3 | 0 | 0 | 1 | 5.8 % | 1.1 % |
| D rows 2^11..2^14 (3 rows in parallel) | 4.4 | 88.5 | 151.5 | 2.6 | 7.6 % | 2.3 % |
| D rows 2^15 (passes not split: n >> 15 = 1) | 56.0 | 0 | 0 | 1 | 4.6 % | 0.8 % |
| D rows 2^16 / 2^17 / 2^18 | 8.3 | 57.4 / 39.0 | 54.9 / 67.2 / 97.4 | 1.9 / 3.3 / 5.3 | 6.7 % | 3.3 % |

Reading: stage C (90 % of the work) is parallel at 7.2 of 8 threads. Stage D is 9 % of the work but 28.5 % of the wall: the base case and the half-gcd levels with rows up to 2^10 are fully serial (152 s), rows of 2^15 fall into a gap where neither the row-parallel mode (a <= 14) nor pass splitting (needs n >> 15 >= 2) applies (56 s serial), and rows 2^11..2^18 run on 2 to 5 threads. Newton (0.4 %), the stage-B build (0.4 %), the linear loops of a step (0.2 %) and the radix-3 stages (inside the convolution rows, already split) are negligible; allocation is inside each region's serial time and does not show up as a cost of its own.

Scaling to r6: stage C grows with its operation count (x174 from r3 with the 3*2^27 plan); every half-gcd level and the base case grow with m (x125), and r6 has 8 more parallel levels on top. At T=24 the model of section 5 puts the serial and 2-to-5-thread parts of stage D at about 15 of 34 hours per trial (44 %), which is what the cloud's Amdahl fit (s = 0.08 to 0.105, worse at higher T) showed.

## 2. Changes (exec_r6fast)

Every counted operation is charged as before; the splits change only who executes a charged operation. The control charges of a loop that is split are charged once by the main thread exactly as the sequential code charges them; what executes only because of a split is thread control (`thread_control`) or `split_extra`, both outside `algorithmic_total`.

1. Task mode (TK, `ntt.c`, `-DNO_TK` turns it off): `conv_bilin_otf` (half-gcd `apply_inv`, `mat_mul`) and `conv_sum_otf` (`poly_mul`) on rows 2^8..2^14: dispatch 1 = one chunk per (row, operand) forward transform, dispatch 2 = one chunk per (row, output) for the products (same order and sign rule) and the inverse transform. Up to 24 + 12 chunks instead of the 3 rows of the row-parallel mode. Operand spectra in a static array of 24 rows x 2^14 slots (12.6 MB, in the image). Threads woken: one per 2^12 transform elements (`TK_LMIN`), so rows below 2^11 stay serial (parallelising them costs more thread control than they cost work).
2. Sub-tree mode (ST, `ntt.c`, `-DNO_ST`): for rows of 2^14 and more, after the first g passes (g = first count giving at least 2^5 sub-trees and 16 per usable thread) every later forward pass, the fused pass and the inverse passes but the last g act inside independent sub-trees; they run in ONE dispatch over ranges of sub-trees instead of one dispatch per pass. The products that follow a forward transform in `sum_row` / `bilin_row` run in the same chunks. Used by every row function (`ntt_fwd/inv`, `conv_sq`, `conv_mulc(_otf)`, `ntt_fwd_shifted`, `conv_sum_otf`, `conv_bilin_otf`). Fewer barriers at every size, and rows of 2^15..2^18 get T threads.
3. Thresholds (`par.h`): passes split from one thread per 2^13 elements (was 2^15, which left rows of 2^15 serial), linear loops from 2^15 (was 2^17).
4. Plain-2^(a+1) plan, rows == 2 (`ntt.c`, `common.h`, `-DNO_R2` turns it off): the r3t21 design ported to the threaded lineage. The first DIF layer becomes a twisted stage: row 0 = c[i] + c[i+n], row 1 = (c[i] - c[i+n]) w^i with w^n = -1; inverse N c[i] = r0 + r1 w^-i, N c[i+n] = r0 - r1 w^-i; then two ordinary 2^a rows through the same kernels, OTF operands, row-parallel, task and sub-tree modes. The twist w^i is a running product started by square-and-multiply per region; a long region is split into chunks whose start powers are `split_extra`. Twists W2T[a] = 5^((p-1)/2^(a+1)) and inverses are computed once in `ntt_init` (counted). `plan3_for_len` now returns the smallest of 2^(a+1) and 3*2^a; `plan_for_len` (stage B) is unchanged. `-DNO_R3` forces rows 2 everywhere (test only).
5. Speculative-run arguments (`single.c`): `single verbose T first_centre trial_cap`. The counted run passes neither (parsed before the counters start, inside PROLOGUE); with them a process runs centres c, c+1, ... and reports after the cap. Used by section 6 and by the validation (cap = known first success, so a corrupted run stops early).
6. Profile hooks (`-DPROF` only; empty macros otherwise). For a package they should be stripped (`ntt.c` grew from 42.3 to 74.0 KB, sources from 286 to 328 KB; the judge-evidence budget must be rechecked).

## 3. Plain 2^(a+1) plan at r6: exactness per stage

m = 122,070,312 = 0.909 x 2^27 (r3: 0.931 x 2^20, the same shape). Every caller passes the length it needs and `plan3_for_len` returns N >= that length, so no product wraps.

| stage / product | length needed | exec_r6mt plan | exec_r6fast plan | slack |
|---|---:|---|---|---:|
| B build g (`plan_for_len(m+1,1)`, unchanged) | 122,070,313 | 3*2^26 = 201,326,592 | same | |
| C conv_sq of h (deg m-1) | 2m-1 = 244,140,623 | 3*2^27 = 402,653,184 | 2^28 = 268,435,456 (rows 2, a=27) | 24,294,833 |
| C T1 x mu'' (window at N-(m-2), needs N > 2m-4) | 244,140,620 | 3*2^27 | 2^28 | fits |
| C q x g mod x^N'-1 (low m terms) | m+1 = 122,070,313 | 3*2^26 | 2^27 (rows 2, a=26) | 12,147,415 |
| C fold limit lim = 2m-2-N'+1 (must be <= m) | | 42,814,031 (N' = 201,326,592) | 109,922,895 (N' = 134,217,728) | |
| C Newton P1 (up to ~1.5 m) | 183,105,466 at the top | 3*2^26 | 3*2^26 (rows 3 still smallest) | 18,221,126 |
| C Newton P2 (l2 - 1 <= m - 2) | 122,070,309 | 3*2^26 | 2^27 | 12,147,419 |
| D apply_inv top (la <= m+1) | 122,070,313 | 3*2^26 | 2^27 | 12,147,415 |
| D lower levels (la ~ m/2^j + 1, 0.909 x 2^(27-j)) | | 3*2^(26-j) | 2^(27-j) | ~9 % each |
| tmp row (must hold every row used) | max n = 2^27 | 2^27 | 2^27 | |
| twiddle table (rows up to 2^27) | | 2^26 entries | 2^26 entries (AMAX 27 unchanged) | |

Memory (formula of R6_PLAN section 2, verified at r3 and r5): stage C live peak 2,147,483,648 (twiddles) + 8,589,934,592 (Y = 2^28 slots) + 4,294,967,296 (tmp) + 11,718,749,952 (mu, F, g) = **26,751,135,488 B** (was 31,046,102,784: -4.29 GB, -0.214 bit). Stage D peak: equal to the stage C peak + 448 B at r3 with rows 2 (section 4), as at r5. ARENA at the r5 ratio 1.176: about 31.46e9 B (was 36.5e9); claimed memory about 31.5e9 B = 2^14.87 MiB (was 2^15.087).
r4, r5, r7: the chooser keeps 3*2^a at the top (rows 2 would be larger: m = 1.16 / 1.46 / 1.14 x 2^k); only some Newton and half-gcd intermediate lengths change.

## 4. Validation

Because of section 0, a full RR=3 or RR=4 run cannot be trusted on this machine today, so the checks are split into (a) full runs at RR=1/2, (b) known-answer benches at RR=3 and RR=4 sizes that are short enough to finish clean in most runs and are repeated (`exec_r6fast/test/bench_chk.c`, `test/build_chk.sh`), and (c) the stage counts that do not depend on the data (B and C count the same whatever the values, so even a run with a fault gives them exactly). Builds: base = exec_r6fast with `-DNO_R2 -DNO_TK -DNO_ST -DPAR_LMIN_ELEM=15 -DPAR_LMIN_LIN=17` (the exec_r6mt program); split = `-DNO_R2` (unchanged plans, new splits); fast = default.

| check | result |
|---|---|
| RR=1 full program, T=1: base, rows 2, rows 2 forced everywhere (`-DNO_R3`, AMAX+1) | identical COLLISION lines (md5 2bbd623b..., the mt-lineage r1 reference); algorithmic 10,077,233,799 (= exec_r6mt) / 10,022,876,098 / 12,710,422,254 |
| RR=2 full program, T=1: same three builds | identical COLLISION lines (md5 2be4869b...); 50,573,431,327 / 49,523,183,913 / 63,664,068,175 |
| RR=2 full program, new splits at T=3 against T=1 | split: 50,573,431,327 at T=3 = T=1; fast: 49,523,183,913 at T=3 = T=1; same collisions; thread control 1.19 / 1.16 G (2.3 %, small rows) |
| RR=3-size powering (m = 976,562, E = 2^26+2^24+2^21+1: Newton + 7 squaring steps with a mulx), T=6 | base: algorithmic 11,538,596,279, F checksum e70518a8919198f6 (2 of 3 runs; the third had a fault). split: 11,538,596,279 (identical), F identical. fast: 7,893,641,424 (-31.6 %), F identical (1 of 3 runs; two had faults). Heap peak 261.5 -> 228.0 MB. Thread control 103 / 77 / 61 M (the sub-tree mode removes dispatches) |
| half-gcd known answer (m = 250,000, A = L U, B = L V, L monic of degree 3), T=6 | gcd = L in every run (base 3/3, split 2/2, fast 3/3). algorithmic: base 12,395,163,287 = split (identical); fast 10,372,165,204 (-16.3 %). Thread control 89 / 289 / 240 M (task mode on small rows costs dispatches) |
| RR=3 full program, fast, T=6, 2 runs | both lost trial 1 (centre 1, which succeeds in clean runs) to a fault: "gcd degree 0", and the two runs' D counts differ (53,875,029,784 and 53,622,772,418), which a deterministic program cannot do. Data-independent counts: B 1,265,997,026; C 228,993,119,529 (exec_r6mt clean r3 run: 344,571,920,769; -33.5 %); heap peak 211,191,360 = C formula 211,190,464 + 896 B of headers, stage D peak = stage C peak + 448 B (the same tie as at r5) |
| RR=4-size powering (m = 4,882,812, E = 2^29+2^27+2^24+1: Newton + 7 steps), T=6 | algorithmic: base 65,208,292,891 = split (identical); fast 64,256,523,810 (-1.5 %: at r4 rows 2 only replaces some Newton lengths). F could not be compared: the four runs (65 G operations each) gave four different checksums, so at least three had faults. Heap peak 1,139,839,040 in all three builds |
| RR=3 and RR=4 full programs: COLLISION lines identical to exec_r3f / exec_r4mt and algorithmic_total 409,369,056,359 / 3,977,289,295,772 for the split build | NOT DONE: at today's fault rate (roughly one fault per 15-30 G operations, section 0) a 280-410 G-op RR=3 trial or the 4.0e12-op RR=4 run does not finish clean here. Run them first on a clean machine: `exec_r6fast/val_run.sh 3 T tag [-DNO_R2]` and `val_run.sh 4 T tag [-DNO_R2]` (they stop at the known first success and retry). |

Measured operation ratio, fast / exec_r6mt, at the r3 shape (the same shape as r6, section 3): powering 0.684, half-gcd 0.837 (at m = 250,000), whole trial about 0.687 (B unchanged, C 0.665, D about 0.81); at r6 the expected ratio is about 0.69 (-0.54 bit on the time term).

## 5. Estimates for r6 and r7 (model; `exec_r6fast/estimate.py`)

Model: the r3 profile split into buckets of work (thread-seconds) with the number of threads each bucket can use; stage C scaled by its operation count, every half-gcd level and the base case by m (x125 to r6, x625 to r7), plus the levels above rows of 2^18 that r3 does not have (8 at r6, 10 at r7, fully parallel). Local thread-seconds are converted to the cloud box with the factor 1.29 that makes the model reproduce the measured r5 run (21,946 s at T=16). Memory bandwidth at 64+ threads is not modelled (stage C efficiency is held at the measured 0.89), so the 64/96-thread rows are optimistic for both builds.

Wall per trial (hours, cloud scale):

| T | r6 exec_r6mt (running build) | r6 exec_r6fast | r6 fast: serial floor | r7 exec_r6mt | r7 exec_r6fast | r7 fast: serial floor |
|---|---:|---:|---:|---:|---:|---:|
| 24 | 34.0 | 21.7 | 6.2 | 159 | 129 | 31 |
| 32 | 29.3 | 18.5 | 6.2 | 138 | 107 | 31 |
| 64 | 22.1 | 13.6 | 6.2 | 107 | 76 | 31 |
| 96 | 19.7 | 12.0 | 6.2 | 96 | 65 | 31 |

- exec_r6mt has about 15 h per r6 trial that does not shrink with T (9.3 h fully serial, the rest on 2 to 5 threads); that is why R6_PLAN saw only +15-20 % from 30 to 90 threads. exec_r6fast leaves 6.2 h (the Euclid base case with its mat_mulQ/divrem, 2.9 h, and the half-gcd levels with rows of at most 2^10, 3.3 h; parallelising those levels costs more thread control than they cost work: TK_LMIN=10 would move ~1.3 h of it for about +0.8 % operations).
- Operations per trial: r6 exec_r6mt 8.4e13 (R6_PLAN); exec_r6fast 8.4e13 x 0.69 (the r3 ratio, section 4) = about 5.8e13. r7: 3.7e14 in both (rows 2 does not fit at the top: m = 1.14 x 2^29).
- Expected trials 1/p = 2.56 (p = 0.39). Expected wall to the first success at T=24: exec_r6mt 87 h, exec_r6fast 56 h.
- In Amdahl terms (fit of the model at T=24 and T=96): exec_r6mt s = 0.036 of a 434-hour one-thread trial, exec_r6fast s = 0.030 of a 301-hour one. The cloud fit of R6_PLAN (s = 0.08 to 0.105) used user CPU time, which preemption on the shared box inflates; the absolute floor is the clearer figure (about 15 h -> 6 h per r6 trial).
- Memory per trial (live peak / touched / claimed arena): r6 exec_r6mt 31.05 / ~35.2 / 36.5 GB; r6 exec_r6fast 26.75 / ~30.4 / ~31.5 GB (stage D peak: section 4); r7 135.9 / ~154 / ~160 GB (both builds), which needs a box with >= 192 GB, or the out-of-core variant of section 6.

## 6. Speculative parallel centres

The trials are independent and deterministic: trial i is a function of the centre c_i = i only (B, C and D of a trial read nothing another trial wrote; the only shared state is the twiddle table, the line constants and the 1/N cache, which do not change values). So k processes can run centres 1..k at the same time without changing any trial's result or counts.

Procedure (to state in the proof exactly like this, as the same procedure as the sequential program):
1. The counted procedure is the sequential loop of `single.c`: for i = 1, 2, 3, ...: run trial i completely; stop at the first trial that yields a verified collision; K = its index.
2. Its cost is the operations of init and line setup once, of trials 1..K in full (failed trials included), and of the output stages once. Nothing else.
3. Execution schedule (wall clock only): trials run in waves of k separate processes of the same binary, `single 1 T/k j 1` for j = 1..k, then j = k+1..2k, ... (first centre j, one trial; the arguments are parsed before the counters start). A wave starts only when the previous wave has ended. The ledger of trial j is the per-trial ledger of process j and equals the sequential program's (the counts are deterministic; the only difference is that each process fills its own 1/N cache, a few thousand operations, which makes the composed ledger slightly larger than the sequential one, never smaller).
4. K is fixed by the order and the stopping rule only: the smallest j whose trial succeeded. The reported ledger is init + trials 1..K + output, all as executed. Every trial with index < K is charged although it failed.
5. Trials with index > K that ran in the last wave are not part of the procedure, whatever their outcome (a success at j > K is discarded, not used). They are disclosed as development runs with their count, binary hash and peak memory (each equals the per-trial peak, so the development-run memory rule holds).
6. Never: choosing which trials to charge, re-ordering centres, or stopping at a later success. The charged set is always the prefix 1..K.

Wording to avoid: "we ran k trials and kept the successful one" (a selection). Wording to use: "the sequential procedure, executed with up to k trials in flight; the charged prefix 1..K is fixed by the order and the stopping rule; trials > K are disclosed development runs".
Judge risk: a ledger composed from several processes has not been ruled on; the per-trial ledgers, the binary hash and the determinism argument must be in the package. A safer, costlier alternative: charge every executed trial (k x waves); at k = 3 that is about +0.2 bit in expectation.

Expected wall to the first success (exec_r6fast model; expected waves E = 1/(1 - q^k), q = 0.61: 2.564 / 1.593 / 1.294 for k = 1 / 2 / 3):

| threads in total | r6 k=1 | r6 k=2 | r6 k=3 | r7 k=1 | r7 k=2 | r7 k=3 |
|---|---:|---:|---:|---:|---:|---:|
| 24 | 56 h | 56 h | 63 h | 330 h | 342 h | 392 h |
| 32 | 47 h | 45 h | 52 h | 275 h | 273 h | 323 h |
| 64 | 35 h | 29 h | 31 h | 194 h | 171 h | 182 h |
| 96 | 31 h | 24 h | 24 h | 167 h | 137 h | 139 h |

Speculation pays from about 32 threads up, because each process carries its own serial floor; on the 32-vCPU box it is a wash.

Memory for k processes (each process = one trial's peak; touched = 1.135 x live, the r5 ratio):

| | per process (touched) | k = 2 | k = 3 | fits the 128 GB box (~114 GB free when idle)? |
|---|---:|---:|---:|---|
| r6 exec_r6mt | 35.2 GB | 70 GB | 106 GB | k=2 yes; k=3 only with nothing else running |
| r6 exec_r6fast | 30.4 GB | 61 GB | 91 GB | k=2 and k=3 yes |
| r7 in core | ~154 GB | ~308 GB | ~463 GB | no; one process needs >= 192 GB |
| r7 out of core (estimate only) | ~88 GB RAM + ~59 GB NVMe | ~176 GB | ~264 GB | k=1 yes |

r7 out of core (not built): keep g, mu and F (3 x 19.5 GB) on NVMe and stream them; Y (51.5 GB), tmp (17.2 GB) and the twiddles (8.6 GB) stay in RAM. Per squaring step the operand rows read mu and g three times each (one per row) and F once each way: about 156 GB per step, 26 s at 6 GB/s against roughly 250-600 s of arithmetic per step at 64-96 threads (+5 to 10 %). The half-gcd top level needs the same treatment for its inputs (its outputs c, d, 25.8 GB each, stay in RAM). Whether NVMe bytes count as memory for the score is a rules question; the conservative claim counts them.

## 7. Recommendation for the r6 run

Verdict: keep the running r6 run for now; restart with exec_r6fast only when its validation is complete, and only early.

- exec_r6fast is better on both axes at r6: about -31 % operations per trial (time term about -0.54 bit, from the r3 ratio 0.687), -4.3 GB memory (memory term about -0.21 bit with ARENA ~31.5e9), and about -36 % wall per trial at T=24 (34 -> 22 h in the model; the measured part is the profile and the r3 CPU time, -28 %).
- Missing before a restart: (1) a clean RR=3 and RR=4 run of the final sources on a machine that does not corrupt results (section 0), (2) a short r6-size smoke run (one powering step and one top-level apply_inv at a = 27 rows 2, about 1-2 h and 27 GB), (3) the stage D peak at r6 (or the r3 ratio, section 4) to set ARENA, (4) proof and note text for the rows-2 stage, the task and sub-tree modes and the new thread-control charges. Distance: about a day of work plus the validation runs.
- Timing: the current run started 2026-10-15 18:53 UTC. A restart saves wall time only if it happens early: at hour h of the current run the remaining expected wall is about 87 - h h (exec_r6mt model) against about 56 h plus preparation for exec_r6fast. Past roughly hour 20 the time gain is gone; the score gain (~0.75 bit) remains, so the choice becomes score against another 2-5 days of box time.
- On the 32-vCPU box: one process, T = free cores (k = 2 does not help there). On a 64-96 core box: k = 2 speculative processes of exec_r6fast (61 GB), with the wording of section 6.

## 8. Not tested / risks

- No run at r6 size of exec_r6fast (built only; `size`: text 431,408, bss 36,517,453,180 with the unchanged 36.5e9 arena). Rows 2 at a = 27 (2^28 points), the twist stage at that length and the sub-tree mode on 2^27 rows were never executed.
- RR=3 and RR=4 full-program validation (collisions, algorithmic_total) not done because of section 0; the substitutes are the known-answer benches and the data-independent counts of section 4.
- Wall-clock gains were measured on an overloaded, faulty machine; the r6/r7 table is a model calibrated on one cloud run. Memory bandwidth at 64-96 threads is not modelled.
- Thread control grows with the new splits (RR=2, T=3: 2.3 % of the total, small rows); at r6 its share is expected well under 1 %, not measured.
- The judges have not seen a task mode, a sub-tree mode or a rows-2 stage; each needs its charging argument in the proof (the source comments have it).
- Silent corruption (section 0) costs a whole trial in a counted run. A cheap guard: once per squaring step evaluate h_new, q and T = h^2 at a random point z and check h_new(z) = T(z) z^bit - q(z) g(z) (about 6m operations per step, +0.3 % of the step, +0.004 bit); on a mismatch redo the step. Not implemented.

## 9. Grok 127c "short-product" design (the coordinator's question)

Not measured here: the local machine corrupts runs of this length at random (section 0), so a bit-identity check of a new squaring schedule would need repeated runs, and the analysis below shows that the time model does not hold.
- The time model counts each of the four products of a squaring step (low half of h^2, high half of h^2, A x mu, q x g) as one cyclic convolution of length N_m >= m. Two of them cannot be done at that length: (a) the low and the high half of h^2 from length-N_m convolutions need two different convolutions (mod x^N - 1 and mod x^N + 1, or two weightings), the same work as one of length 2 N_m, which is exactly the rows-2 split of this build; (b) q = coefficients m-2 .. 2m-4 of A x mu is a middle product, which needs a cyclic length >= 2m-3 (the current window at gamma = N - (m-2) already is that middle product). Only q x g (low m coefficients) works at length >= m, and the current code already does it at N' >= m+1. With the right lengths the step costs what it costs now: time about 1.0x, not 0.75x.
- Memory: Grok's own table gives the short-product half-gcd 0.940x at k = 12 and 1.074x at k = 11 (5,114,209,760 against 4,759,669,056 B). At k = 12 the rows-2 plan of this build gives 0.862x (26.75 against 31.05 GB) with about 0.69x operations, so it dominates. The measured k = 9 prototype (chunked two-row, Grok's run) was 0.827x memory and 1.71x wall: log2(0.827 x 1.71) = +0.50 bit, worse.
- Verdict: it would not lower the r5 score (memory +0.10 bit, no time gain); at r6 the rows-2 build is the better route.

## Files

- `exec_r6fast/` sources (20 files as exec_r6mt plus the changes of section 2); `prof_run.sh` (profile build and run), `prof_table.py` (profile tables), `val_run.sh` (full-program validation with the trial cap and retries), `test_small.sh` / `test_mt.sh` (RR=1/2 checks), `test/bench_chk.c` + `test/build_chk.sh` (known-answer benches), `estimate.py` (section 5 model).
- Evidence: `exec_r6fast/prof_out/` (profiles: `r3_base1_T8` = exec_r6mt behaviour, `r3_split1_T8`, `r3_fast1_T8`), `val_out/` (the two RR=3 runs with a fault), `test/out/bench_chk_all.txt`, `test/out/fault_scan*.txt`.
- Build of the r6 binary (not run): the exec_r6mt flags on the exec_r6fast sources; ARENA must be set to about 31.46e9 in `common.h` once the r6 stage D peak is confirmed (it is still 36.5e9).
