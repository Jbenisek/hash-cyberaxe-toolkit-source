# upfront-G50-Y1: pilot screen of contexts, decided with the real CK2 gate

**Verdict: GAIN. It depends on a new selection premise and is not a certified row.** The fork is settled. Under the real CK2 gate the opening count does not depend on context yield: corr(openings, pilot) = -0.004 and CV(openings) = 0.06, against CV(passes) = 0.37. Openings are therefore a fixed cost per context. Priced on the pkgCJ ledger, keeping half the contexts gains **0.199 to 0.214 bit** under row (i) and **0.145 to 0.157 bit** under row (ii). Keeping a quarter gains 0.276 to 0.299 bit under (i) and 0.198 to 0.217 bit under (ii). All four numbers clear the GAIN thresholds of 0.10 and 0.05. The per-pass rates on the solver side match between kept and rejected contexts as far as they can be measured. Root-level success could not be measured (see "Not tested").

Labels: **COMPUTED** means this folder ran it. **DERIVED** means arithmetic on computed numbers and the ledger constants. **GUESS** means not measured.

Folder: the brief named two output folders, `combos\upfront_screen\` and `combos\upfront-G50-Y1\`. Everything was written here, in `upfront-G50-Y1\` only.

## What was run (COMPUTED)

- `screen_ck2.py SEED CTX` uses the same rng consumption as `yield4_seed.py`, so seeds 101 and 202 give the same 256 contexts as `check/run_s101.txt` and `run_s202.txt`. For every context the script evaluates the whole 2^19-member class with numpy, using step CO compiled from `frontline_full.LINES` and the flat T1/T2 tables. It computes the following per context:
  - opened clusters under the real gate `F.gate(q<<14 | c<<7 | a)`, with the key built as `walk()` builds it (lines 1171-1174, 1254 and 1261);
  - E lanes (T2 hits);
  - exact joint passes;
  - T-nonzero solver calls;
  - G_cluster fills, counted as 2341 representative batches plus 5 partner batches per opened cluster;
  - pilot hits and passes on the 2^15 sample.
- The script then runs `F.solve(rebuild, rows_of(T), G15)` on **every** T-nonzero call. It records roots, leaves, ledger U and metered debit, and the CF 6 predicate pieces of each root.
- Checks, all with 0 mismatches:
  - vector omega/Y9/C2/Y0 against `F.rebuild` (73,728 members);
  - vector T1/T2 against `F.T1`/`F.T2`;
  - vector gate against scalar `F.gate` (655,360 representatives);
  - closed cluster implies no T2-positive member, checked over all 2304 contexts;
  - hits, sample passes and pilot match `check/run_s*.txt` on 256 of 256 contexts;
  - `check_walk.py`: `frontline_full.walk()` itself on 6 contexts. Its opened, e_lanes, passes, solver_calls and fills equal the vector counts exactly.
- The prefix test "either 9-bit prefix mod 128 in S7" is **not** the same as the gate. The gate opens a strict superset: 21,001 representatives have both prefixes dead but the gate open, and none are the other way round. This is consistent with the walk's own reference check. The charged predicate is the gate, so the gate is what was counted.
- Seeds 101 and 202 (128 contexts each) are the decision sample. Seeds 303 and 404 (1024 contexts each) are an independent out-of-sample replication.

## (a) Openings vs yield (COMPUTED)

| | main 256 (s101+s202) | ext 2048 (s303+s404) |
|---|---:|---:|
| opened per context: mean / sd / CV | 7303.1 / 440.9 / **0.0604** | 7335.6 / 466.5 / **0.0636** |
| passes, full class: mean / CV | 541.9 / **0.371** | 524.8 / **0.396** |
| passes, 2^15 sample: CV | 0.409 | 0.428 |
| hits CV / fills CV / calls CV | 0.358 / 0.400 / 0.388 | 0.381 / 0.423 / 0.411 |
| CV(open) / CV(passes) | **0.163** | **0.161** |
| corr(openings, pilot) | **-0.004** (95% CI -0.13..0.12) | **+0.005** (-0.04..0.05) |
| corr(openings, hits) / (openings, passes) | +0.017 / +0.038 | +0.003 / +0.010 |
| corr(pilot, passes) | 0.925 | 0.933 |
| opened ratio, kept/all: keep 1/2, 1/4, 1/8 | 1.002, 0.997, 0.991 | 1.000, 1.000, 0.993 |

The opening count does vary across contexts: it ranges from 6656 to 8960, while the 8-bit proxy is constant at 6656. That variation does not track yield.

## (b) Solver side per pass, pilot-kept half vs rejected half (COMPUTED)

| per pass | main: ratio ± boot se | ext: ratio ± boot se | ext totals, kept / rejected |
|---|---:|---:|---|
| T-nonzero calls | 1.0012 ± 0.0158 | **0.9973 ± 0.0054** | 174,726 / 93,015 |
| ledger U units | 1.0012 ± 0.0158 | 0.9968 ± 0.0055 | |
| leaves reached | 0.774 ± 0.220 | 0.953 ± 0.084 | 1174 / 654 |
| joint roots | n/a | n/a | 1 / 0 |
| certified (t, Q*, A, C) | n/a | n/a | 0 / 0 |

None of the measurable ratios is below 0.95 at 2 sigma. Roots per pass and certified roots per pass cannot be compared: there is 1 root in 302,663 calls in total.

## (c) Pricing (DERIVED from COMPUTED kept/all ratios; pkgCJ constants via `frontline_full`)

**Model.** The model uses the same pieces as `work/ledger_split.py`. The script rebuilds them from F's N formula and asserts that their sum equals N = 6022417582191478187278 (log2(N/430) = 63.6026).

- Kept contexts pay:
  - representatives at 173,216;
  - openings, scaled by the measured opened ratio;
  - E, fills, passes and solver credit, each scaled by its own measured kept/all ratio.
- Success is held fixed through the exact full-class pass count: kept contexts K' = K/R.
- Every screened context pays 600 + 1024·u, with u = 11 (as briefed) or 25 (chain plus T2 walk, conservative), times 1/q redraws.
- Once costs are unchanged, plus 2^20.

**Fixed share.** The fixed share of a context is 0.598 under (i). Under (ii) it is **0.452**, with openings at 218 units and an opened share of 0.409.

| keep (rank by pilot) | R main / ext | (i) gain u=11 main / ext | (i) u=25 ext | (ii) gain u=11 main / ext | (ii) u=25 ext |
|---|---:|---:|---:|---:|---:|
| 1/2 | 1.289 / 1.306 | **0.199 / 0.214** | 0.206 | **0.145 / 0.157** | 0.147 |
| 1/4 | 1.428 / 1.468 | **0.276 / 0.299** | 0.285 | **0.198 / 0.217** | 0.199 |
| 1/8 | 1.571 / 1.619 | 0.345 / 0.365 | 0.339 | 0.246 / 0.260 | 0.226 |

Bootstrap se of the gain is 0.004 to 0.008 bit on the extension sample and 0.01 to 0.02 bit on the main sample. Holding openings exactly flat changes the gains by less than 0.005 bit.

**Thresholds a run would declare (ext sample).**

| keep rule | q | R | (i) gain | (ii) gain |
|---|---:|---:|---:|---:|
| pilot ≥ 58 | 0.476 | 1.324 | 0.224 | 0.164 |
| pilot ≥ 75 | 0.213 | 1.503 | 0.315 | 0.228 |
| pilot ≥ 85 | 0.114 | 1.636 | 0.369 | 0.262 |

The briefed DERIVED expectation for (ii) was a fixed share of about 0.47 and a keep-1/2 gain of about 0.165. The measured values are 0.452 and 0.145 to 0.157.

## Decision against the brief's rules

| rule | measured | outcome |
|---|---|---|
| corr(openings, pilot) ≥ 0.5 → NO_GAIN | -0.004 / +0.005 | not triggered |
| CV(openings) within a factor 2 of CV(passes) → NO_GAIN | ratio 0.16 | not triggered |
| (b) ratio below 0.95 at 2 sigma → NO_GAIN | calls 0.997 ± 0.005; leaves 0.95 ± 0.08 | not triggered |
| net gain ≥ 0.10 under (i) **and** ≥ 0.05 under (ii) → GAIN | 0.199 to 0.214 and 0.145 to 0.157 at keep 1/2 | met |

## Items Sol needs (DERIVED; the means are COMPUTED on the ext sample, ± one se)

| per context | unscreened | kept, pilot ≥ 58 (q = 0.4756) | kept, pilot ≥ 75 (q = 0.2129) |
|---|---:|---:|---:|
| E lanes (→ E_B) | 28,827.7 | 38,042.1 ± 210.5 (×1.320) | 42,897.1 ± 280.9 (×1.488) |
| passes (→ P_B; also success) | 524.8 | 694.9 ± 4.3 (×1.324) | 788.6 ± 5.8 (×1.503) |
| opened (→ A_B) | 7,335.6 | 7,335.6 ± 15.2 (×1.000) | 7,321.1 ± 22.4 (×0.998) |
| fills G_cluster (→ G_B) | 12,508.7 | 16,443.3 ± 133.3 (×1.315) | 18,351.2 ± 206.3 (×1.467) |
| solver calls | 130.7 | 172.9 ± 1.2 | 197.2 ± 1.6 |
| ledger U (→ CREDIT) | 685,347 | 906,164 ± 6,342 (×1.322) | 1,035,601 ± 8,801 (×1.511) |

Sol also needs the following:

- **Screen cost per screened context.** The context setup is 600, already in today's row. The pilot is 1024 members, each one 11-op omega chain plus a T2 test with count and compare; we priced it at 11 and at 25 units per member. A fixed list of 1024 member numbers spread over clusters needs a 4 KB Y4 list built once. The threshold is one integer fixed in advance.
- **Redraws.** The number of screened contexts is K'/q. It needs its own budget and tail, either a binomial lower tail on kept contexts out of a fixed screened count, or a halt-on-screen budget.
- **Declared premises.**
  - **H_S1 (keep rate):** for a fresh uniform context, Pr[pilot ≥ t] ≥ q_min.
  - **H_S2 (screened yield):** E[passes | kept] ≥ R_min · E[passes].
  - **H_S3 (screened per-pass success):** the per-pass success law H1' is unchanged on kept contexts. This is measured at T-call level (0.997 ± 0.005) and at leaf level (0.95 ± 0.08). It cannot be measured at root level.
  - **Screened mean premises:** each of E_B, P_B, A_B, G_B and CREDIT becomes a screened-mean premise, the way H_G_cluster was supported by 16.7M contexts. Every budget changes. K becomes ceil(K / R_min).
- **Supporting sample.** A preregistered sample at H_G_cluster scale needs about 2^43 member evaluations. That fits the 3090. The numpy pipeline here does about 0.35 s per context including the solver, so it is too slow for 16M contexts.

**Judge risk.** This is a selection premise: contexts are kept or dropped on a statistic that correlates with success. The judge has refused top-unit and selection-style clauses before. H_S3 is the weakest clause, because the deep solver success rate is asserted, not measured.

## Not tested / limits

- Root-level and certified per-pass success under the screen was not tested. There was 1 root in 302,663 calls and 0 certified, so it is unmeasurable at this scale. H_S3 rests on the T-call and leaf ratios only.
- The gains are ledger-model prices on 256 + 2048 contexts, not a Sol-certified integer row. Hoeffding tails on the new budgets were not recomputed; they are small at this K.
- The cost of 11 units per pilot member is the brief's figure. A real T2 walk costs more. At 25 units per member the gain drops by about 0.01 bit at keep 1/2.
- Row (ii) uses the briefed XF1/XF2 numbers (218 units, share 0.409) and assumes the XF gate's opened count is as flat in yield as the CK2 gate's. That gate was not available to test. The 8-bit proxy is exactly flat, which supports the assumption but does not prove it.
- HANDOFF.md and MASTER_PLAN.md were **not** checked for an earlier context-screen entry. A grep of EDGES_FIBRE.md and LEVERS_REAPPLY.md found no screen, pilot or context-drop item.

## Side observations (COMPUTED, outside the question)

- The measured opened share is 0.44751 ± 0.0006 (2304 contexts). The charged opening budget uses p* = 0.45937 (A_B/K = 7526.3, against a measured mean of 7332 ± 10). If p* is a model value rather than a proved bound, a measured-mean premise would be worth about 0.02 bit. This was not pursued.
- Mean G_cluster on the extension sample is 12,509 ± 117, consistent with the H_G_cluster premise of 12,466.
- 19 of 2304 contexts (0.8%) have zero T2 hits across the whole class. Any screen drops them.

## Reproduce (Windows python 3.14 + numpy 2.4)

```
python screen_ck2.py 101 128 16 ; python screen_ck2.py 202 128 16     # ~35 s each
python screen_ck2.py 303 1024 4 ; python screen_ck2.py 404 1024 4     # ~6 min each
python check_walk.py 6
python analyze.py 101,202 303,404 > analysis.txt
```

Files in this folder:

- `screen_ck2.py`, `analyze.py`, `check_walk.py`
- `rows_s{101,202,303,404}.json`
- `run_s*.txt`, `analysis.txt`, `check_walk_out.txt`
- `yield4_seed.py` and `outer.py`, copied unchanged for reference
- `baseline_run_s*.txt`, copies of `check/run_s*.txt`
