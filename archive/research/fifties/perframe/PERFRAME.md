# perframe: per-frame clustering of the deep trial events of the 9a9f3b7b frame search, preregistered (2026-10-09, local, nothing submitted)

**Verdict (preregistered rule): SUPPORTED.**
- At every deepest reachable event, the upper limit on the per-frame cross-step factor is at most 1.92.
- The premise H7prime-ak-cluster allows a factor of 2^31.207, so the margin is at least 30.26 bits.
- What this does not cover: the run measures partial events, not listed good trials. The step from these events to the joint event is still the premise (see Limits).

## 1. The premise and the ruling
- **Ruling (MEASURED).**
  - `fetch_ruling.sh 9a9f3b7b` printed "no run found": the run is no longer among the last 100 GitHub runs.
  - The dossier had already been downloaded to `research/dossiers/9a9f3b7b/review/`.
  - Status: `not_evaluable`. All four lane reasons are `heuristic/H7prime-ak-cluster`.
  - lane_cost: "No experiment, implementation, or scaled model measures the frame-level factorial-moment bound asserted by H7prime-ak-cluster."
  - lane_cryptanalysis: "has no supporting proof or experiment at frame scale ... absence of a known clustering mechanism does not establish the numerical bound 0.0065."
- **Premise.** Source: `research/pkg16/pkg/blake3-r2/claim.json`, H7prime-ak-cluster, score-critical. The text is verbatim apart from line wrapping:
  > For a frame of the search of proof.md Section 9 (the six outer words C0.d1, D2.b1, S11, S4, X9, w6 and a member y of
  > the sub-class, drawn uniformly), let W count all listed good valid trials over all 2^32 values of D2.a1 and all 2^21
  > members of Q* (t != 0, R = 0, rule A, an E1 outcome among the seven of beta*). Assume E[W (W - 1)] <= 0.0065 E[W].
  > With H1' and the independence of the frames, Lemma S8 then bounds by exp(-0.6 * (1 - 0.0065 / 2)) = exp(-0.59805)
  > < 0.549883 the probability that no frame of the run has W > 0.
- **Unit.** The frame: six outer words and the member y.
  - Each frame has 2^32 outer steps, g = D2.a1.
  - Each outer step has 2^21 trials, one per c1 in Q*.
  - So a frame has 2^53 trials. Y4, Y12 and w5 are shared across the whole frame (Lemma AK (a)).
- **Claimed bound.** rho = E[W(W-1)]/E[W] <= 0.0065. This gives the success bound 0.40. At rho = 1 the success bound falls to 0.209 (claim limitations).
- **Margin it needs (DERIVED).**
  - p_good = (5/7) 1033 2^27 / 2^128 = 2^-91.473 per trial, so E[W] = 2^-38.47 per frame.
  - Under independence, rho = (2^53 - 1) p_good ≈ 2^-38.47.
  - The premise therefore allows a cross-step clustering factor over independence of 0.0065 / ((2^32-1) 2^21 p_good) = **2^31.207**.
  - The within-step part is negligible unless the within-step factor Rw exceeds about 2^63.

## 2. Design (PREREG.txt, sha256 `f88f375d...334e5073`, hashed before any main-kind step)
- **Code base.**
  - Step CO is `halfsearch.ctr_outer` of the filed 9a9f3b7b program (sha256 `7078cf8a...`). `gen_consts.py` translates it line by line into `pf_consts.cuh`.
  - The constants, the seven taus, rule A and the filter automata are also read from halfsearch.
- **Frame and trials.**
  - A frame is drawn as in step 1 of 9.1.
  - Per frame, the run walks G = 2^19 values of g: a random affine GF(2) subspace, so every pair of distinct g is equally likely.
  - It evaluates the same k = 512 values of c1 (a random affine subspace of Q*) in every outer step.
  - That gives 2^28 trials per frame. E1 and E3 of both messages are evaluated exactly, and t = 0 trials are excluded.
- **Strata.** Cross-step pairs are split into same-c1 and different-c1 pairs and weighted back to the full frame: Rx = 2^-21 Rx_same + (1 - 2^-21) Rx_diff.
- **Arms.**
  - ctx: one frame per block.
  - ctrl: the same g walk and c1 set, with fresh frame words for every outer step.
- **Generators.** Philox4x32-10 (G1) and SHA-256 counter mode (G2). Keys come from a new label; a freshness scan of research/ found no prior use.
- **Events.**

  | event | definition | level |
  |---|---|---|
  | E1L | the E1-listed outcome: tau in T7, eps*, beta*. These are exactly the roots of the frame search. | trial |
  | E3P | (J1) and (J2) of the E3 side | trial |
  | R24, R16 | the low 24 or 16 bits of r are zero | trial |
  | E1a | tau in T7 | trial |
  | RA | rule A | trial |
  | P | filter pass | outer step |
  | T2 | test (2) | outer step |

- **Primary statistic.** For E1L, E3P and R24 in the ctx arm:
  - U = (1-2^-21) U_diff + 2^-21 U_same.
  - Each U_s is Rx_s + 3 jackknife SE when its stratum has at least 30 pairs, otherwise the exact 99.865 % Poisson limit.
- **Verdict rule.** SUPPORTED iff every U <= 16; NOT SUPPORTED iff any U > 2^31.207; otherwise WEAK.
- **Validation (MEASURED, before PREREG).**
  - GPU against Python on 1,376,256 trials: **0 mismatches**. The Python side used halfsearch `ctr_outer`/`ctr_trial`, both real 2-round compressions with counter t and flags 3, and `ctr_lane` on every trial.
  - The comparison covered 160 frames and 74,880 outer steps, with k = 16, 64 and 1,024 and G up to 8,192, in both arms and with both generators.
  - Production records equal the validation-kernel records (4 of 4).
  - Full-size hits recomputed by real compressions: 1,203 + 61 = 1,264, all OK. These include 49 E1L and 14 E3P.
  - The KATs pass.
- **Run (MEASURED).**
  - All 32 segments ran: **262,144 frames per arm** (2^17 per generator), 2^46 trials per arm, 1,610 s.
  - The task used about 28 minutes of GPU in all.
- **Checks after the run (MEASURED).**
  - `sha256sum -c PREREG.sha256`: OK. All 27 listed files match, and run_out.json carries the PREREG hash.
  - beta = beta* on every valid trial. No E3P falls outside a pass carrying the bit of its tau.
  - The per-c1 totals equal n in every frame.
  - **33,091 of 33,091** main E1L and E3P hits were recomputed OK by real compressions.
  - 32,817 trials had t = 0 and were excluded, as expected (about 2^-32 per trial).

## 3. Results (MEASURED; ± is one jackknife SE over 128 groups of frames; pairs are unordered, with the no-clustering expectation in brackets)

| event (log2 p) | arm | Rx (whole frame) | Rx_diff | Rx_same | Rw (within step) | pairs within / same-c1 / diff-c1 |
|---|---|---:|---:|---:|---:|---|
| **E1L** (-32.26) | ctx | **1.146 ± 0.055** | 1.146 ± 0.055 | 793 ± 35 | — (0 pairs, exp. 0.0007) | 0 / **557 (0.70)** / 411 (358.8) |
| | ctrl | 0.973 ± 0.058 | 0.973 ± 0.058 | 2.9 ± 2.1 | — | 0 / 2 (0.69) / 341 (350.4) |
| **E3P** (-34.47) | ctx | **0.96 ± 0.24** | 0.96 ± 0.24 | 0 pairs | 6.9e5 ± 1.7e5 | 22 (3e-5) / 0 (0.033) / 16 (16.7) |
| | ctrl | 0.59 ± 0.19 | 0.59 ± 0.19 | 0 pairs | 8.6e5 ± 1.8e5 | 25 / 0 (0.030) / 9 (15.3) |
| **R24** (-23.76) | ctx | **1.0019 ± 0.0002** | 1.0019 ± 0.0002 | 1.008 ± 0.003 | 4.31 ± 0.21 | 386 / 92,540 (91,804) / 47.0e6 (46.9e6) |
| | ctrl | 0.9999 ± 0.0002 | 0.9999 ± 0.0002 | 1.000 ± 0.003 | 4.05 ± 0.19 | 362 / 91,819 / 46.9e6 |
| R16 (-16.05) | ctx / ctrl | 1.0001 / 1.0000 | | 1.003 / 1.000 | 2.16 / 2.16 | |
| E1a (-11.70) | ctx / ctrl | 1.0001 / 1.0000 | | **2.927 / 1.000** (±0.001) | 2.26 / 2.26 | |
| RA (-8.00) | ctx / ctrl | 1.0000 / 1.0000 | | 1.000 / 1.000 | 2.43 / 2.43 | |
| P (-9.81 per step) | ctx / ctrl | R = 1.0000 ± 0.0000 in both arms | | | | |

**Primary (ctx arm).**

| event | U (how computed) | log2 U | margin to 2^31.207 | BOUNDED-2 | BOUNDED-16 | NO-EXCESS (ctx - ctrl Rx) |
|---|---|---:|---:|---|---|---|
| E1L | **1.310** (Rx_diff + 3 SE; same-c1 stratum Rx_same + 3 SE = 900, at weight 2^-21) | 0.39 | **30.82 bits** | yes | yes | yes, +0.17 ± 0.08 (2.2 SE) |
| E3P | **1.922** (Poisson 99.865 % limit, 16 diff-c1 pairs; same-c1: 0 pairs, limit 202, at weight 2^-21) | 0.94 | **30.26 bits** | yes | yes | yes, +0.37 ± 0.31 |
| R24 | **1.0023** (Rx + 3 SE) | 0.003 | 31.20 bits | yes | yes | **no**: +0.0020 ± 0.0002 (9 SE) |

**Generators separately (ctx Rx).** E1L: 1.15 ± 0.08 (G1) and 1.14 ± 0.08 (G2). E3P: 1.41 ± 0.40 and 0.56 ± 0.25. R24: 1.0017 and 1.0021.

**Means against nominal values.**
- E1L: 1.012 ± 0.009 (ctx) and 1.000 ± 0.009 (ctrl) of 53 · 2^-38.
- P: 1.0000 ± 0.0001 of CTR_SHARE / 2^64.

## 4. Reading
- **Bound against margin.**
  - Across outer steps, the deepest events of the frame search are within a factor of 2 of independence. E1L is exactly the set of roots the search forms, at 2^-32.26. E3P is the E3 half, at 2^-34.47.
  - The upper limits are 1.31 and 1.92, against an allowed 2^31.207 (MEASURED and DERIVED).
  - The premise would fail only if clustering grew by a factor of about 2^30 between these events and the joint event (DERIVED).
- **The frame mechanism the judge suspected exists, but only in the same-c1 stratum (MEASURED).**
  - Two trials with the same c1 in one frame share u + w5, so they share the conditional E1 law.
  - Measured same-c1 factors in ctx against ctrl:

    | event | ctx | ctrl |
    |---|---:|---:|
    | E1a | 2.93 | 1.00 |
    | E1L | 793 ± 35 (2^9.6), from 557 pairs against 0.70 expected | 2.9 (2 pairs) |

  - Pairing by K shows these pairs are not K collisions (Lemma AK): 0 of the 557 share K_O(g). They come from the frame's Y12 and w5.
  - In a full frame this stratum carries weight 2^-21, so it adds 793 · 2^-21 = 0.0004 to Rx (DERIVED).
  - It would break the premise only if the same-c1 factor of listed good trials exceeded 2^52.2 (DERIVED).
  - Given one E1L, a frame holds about 793 · 2^32 · 2^-32.26 ≈ 660 same-c1 E1L partners (DERIVED). For the premise to break, the E3 sides of those partners would have to be correlated far beyond anything seen. E3P shows no cross-step clustering, and its same-c1 stratum has 0 pairs against 0.03 expected (GUESS that this carries over to the joint event).
- **Small, real frame excess at R24 (MEASURED).**
  - Rx = 1.0019 against ctrl 0.9999, 9 SE, and present in both generators.
  - The E1L different-c1 excess is +0.17 ± 0.08 (2.2 SE, inside the preregistered 3 SE).
  - Both are far below the margin.
- **No frame clustering at the filter or rule-A level (MEASURED).**
  - P: R = 1.0000 in both arms.
  - RA: Rx = 1.0000.
  - Within-step clustering is identical in both arms (RA Rw 2.43, E1a 2.26, R24 about 4.2, E3P about 7e5, rho_w_full(E3P) about 61–72). It is a property of single outer steps, as in prereg8.
- **Side note (MEASURED).**
  - Rule A is enriched on E3P trials: 91 of 2,960, against 11.6 expected at 2^-8.
  - On E1L trials it is not: 58 of 13,728, against 53.6 expected.

## 5. Limits
- **No listed good trial is measured** (2^-91.47 per trial).
  - E1L and E3P are its two halves, measured separately.
  - Moving from factors of about 1 at these depths to rho for the joint event is still the premise. The run bounds that extrapolation empirically at the deepest reachable events; it does not prove it.
- **E3P precision is low.** There are 16 different-c1 pairs. U = 1.92 is a Poisson bound and cannot separate 1.0 from 1.5.
- **Within-step pairs of E1L are unmeasured** (0 pairs, 0.0007 expected).
- **Sampling.**
  - G = 2^19 of the 2^32 values of g per frame, and k = 512 of the 2^21 values of c1.
  - These are random affine subspaces, so pair-uniformity is exact. The g of one frame are not a contiguous range.
- **Generators.** Pseudo-random generators stand for uniform words.
- **Instance.** Counter instance (flags 3) only.
- **Multiplicity.** Eight events and two arms are reported with no multiplicity correction.
- **GPU sharing.** The GPU was shared during the run. This affects only throughput; the outputs are deterministic.
- **Not checked.** H8prime (root count per frame) and the cost-lane findings of the ruling are not addressed here.

## 6. Files (this folder)
- **Code:** `perframe.cu`, `pf_consts.cuh` (generated), `gen_consts.py`, `ref_pf.py`, `analyse_pf.py`, `pairs_pf.py`, `make_tables.py`, `run_main.py`, `seeds.py`.
- **Scripts:** `build.sh`, `validate.sh`, `validate2.sh`, `start_main.sh`, `post.sh`.
- **Preregistration:** `PREREG.txt`, `PREREG.sha256`, `SIZING_RULE.txt`, `timing.json`.
- **Validation:** `val/VALIDATION.json`, `val/VALIDATION2.json`, and the checks in `val/`.
- **Run:** `main/` (128 `.bin` and 128 `.hits` files, `run_out.json`, `run_log.jsonl`).
- **Results:** `main_out.json` (all numbers), `main_tables.md`, `main_hits_check.json`, `main_pairs.json`, `post_prereg_check.txt`.
- **Not evidence:** `dry/` and `dbg/` are code tests only.
