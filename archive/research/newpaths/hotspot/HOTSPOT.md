# HOTSPOT: where the partial events of the counter arrangement concentrate (folder newpaths\hotspot)

Written 2026-10-08. Research only: no yukon, nothing submitted or posted, trace untouched, pkg11 untouched, nothing
written outside this folder. Tags: COMPUTED = run here (file named); DERIVED = follows from a stated argument;
GUESS = judgement.

## 0. Answer

There is a hot spot beyond the known class and sub-class. It is confirmed on held-out data. It sits in three cheap
coordinates:
- the inner word c1 (a sub-cube);
- the outer word Y9;
- the outer pair (Y12, KY).

The first two are necessary conditions of R = 0, so they carry to the full event exactly. COMPUTED on partial events;
DERIVED for R = 0.

| hot spot | kept | gain, held-out partial event | carries to R = 0 | status |
|---|---|---|---|---|
| H-A: c1[11] != c1[12] and c1[20] != c1[22] | 1/4 of the cube | listed E1 outcome x4.01 | x4 (R = 0 implies a listed E1 outcome) | x2 exact (DP); x2 holds in 11,427 of 11,427 outcomes |
| H-B: Y9 = 0 mod 4, Y9[16] != Y9[17], Y9[24] = Y9[25] | 1/16 of outer steps | eps* partial E3 x16.2 | x16 (R = 0 implies the eps* partial E3 event) | x4 exact (DP); x4 holds in 1,126 of 1,126 events (307 outer steps; sub-class only for 24/25) |
| H-C: Y12[16] != KY[16] and KY[15:12] = 0 | 1/32 of outer steps | listed E1 outcome x2.03 (whole class x2.25) | x2.0 if E3 is independent of KY (same kind as H1') | measured |

- **Combined:** 4 x 16 x 2.03 = 2^7.0 per trial (DERIVED). The outer filter costs 2^9 outer steps (under 400 units
  each) per kept step. That is set against 2^19 kept trials x 6.5 units, so it adds +6% cost (0.08 bit).
- **Net:** about +6.9 bits on the VALUE.md ledger, 84.96 -> about 78.0. This is DERIVED and was not run through
  value_calc.py. The DP-proven part alone is x8 (3 bits), giving 82.0.
- **Measured jointly** in region H-A + H-B (1/64 of trials): E1 outcome x4.20, eps* partial E3 x14.7. No coupling
  between the two sides (section 2).

## 1. What was run (COMPUTED)

- **Program.** hotspot.cu is ctr_gpu.cu in "real" mode (same arrangement, same events, same code). It adds T0 (the
  counter t) and logs records. Each record holds:
  - the 8 outer basis words, the 11 outer words the inner trial reads, c1, the inner index and t;
  - the internal words and the event flags.
  - It also logs a uniform null sample (one random trial per selected outer step).
- **Runs.** One bounded GPU run (run_main.sh, GPU idle before it):
  - sub-class: 2^44.81 trials, seed 201, 1,128 s;
  - whole class: 2^43.00 trials, seed 202, 329 s.
  - Before that, two seconds-long smoke and timing runs.
- **Rates agree with VALUE.md:** E1 outcome 8,915 against 8,904 exact; listed tau 2^-10.696; beta != beta* 0;
  t = 0 7,241 (2^-32.0). See out\h_sub.txt and out\h_all.txt.
- **Record check.** 9,594 records were recomputed by ref.py with 0 mismatches. ref.py ports the outer step from the
  text of ctr_gen.cuh and parses the lists from h8_deep.inc (out\ref_check.txt).
- **Split, fixed before looking:** even thread id = discovery, odd = held-out.
- **Hot spot criterion:**
  - cluster-robust |z| >= 5 on discovery (clusters are outer steps);
  - the same sign with |z| >= 3 on held-out;
  - and 780 parameter bits per event.
- **Analysis.** analyze_hot.py covers bits, bit pairs, greedy conjunctions, an outer-step score and value maps
  (out\an_sub.txt, out\an_all.txt). followup.py covers GF(2) relations that hold for every event, fixed regions
  with robust z, and an exact per-Y9 DP (out\fu_sub.txt, out\fu_all.txt).

## 2. Map results

- **Controls (positive).** Each event shows its own internal conditions at |z| 12-190, for example:
  - listed tau: y6[15] = 0, y6[16] = 1 (the sign of beta* bits 3 and 4);
  - rule A: h1 bits 0, 1, 16, 17.
- **No hot spot (COMPUTED):**
  - the inner index (E1 outcome chi2 9 on 15) and the counter t (chi2 15 on 9);
  - the basis words, w5, C2*, K0d and w8 (on top of Y9, w8[22] = 0 adds x1.0-1.3 at most);
  - the Y4 member beyond the class. The maps do not re-find the sub-class either: its exact effect on partial E3
    is x1.2, which is below what clustered events resolve.
- **H-A.** Both parities appear as GF(2) relations of every E1 outcome in both runs.
  - dp_proof.py (exact carry DP over every c1 in the cube and every d2) shows that no c1 with c1[11] = c1[12] can
    give eps* for any of the 14 listed taus.
  - c1[20] != c1[22] comes from the tau-eps coupling through d2 and is not proven.
  - The E1 outcome density also varies over high c1 bits: keeping the best 1/4 of 64 cells gives x1.66 more
    (held-out). An exact eps-only score per cube member keeps 1/16 of the cube at x5.24 on real outcomes
    (out\subcube_sub.txt).
- **H-B.** Here h1b = h1 ^ ETA (the class), so Delta g1 depends only on (Y9, h1). Exact DP (dp_proof.py,
  followup.py; checked against 2^24 samples per Y9):
  - Y9 = 0 mod 4 is necessary for Delta f1 to be any of tau ^ ror(tau, 1).
  - 93.7% of Y9 values give probability 0.
  - Ranking the rest gives, on that condition: best 1/64 x46, 1/256 x89, 1/1024 x139.
  - Y9[16] != Y9[17] holds for every partial E3 event of every eps in both runs.
  - Y9[24] = Y9[25] holds only in the sub-class. These two act jointly with eps3 = eps*: the 4-condition set holds
    84% of the Delta f1 mass, but 100% of the events.
- **H-C.** Every listed tau needs y6[16] = 1. In the arrangement:
  - a1[16] = Y12[16] (d1[0] = 0 in the cube), so y6[16] = Y12[16] ^ KY[16] ^ borrow;
  - KY[15:12] = 0 makes the borrow rare. Y12[16] != KY[16] alone gives x1.51.
- **Near-misses** (one R word zero, HW(R) <= 23):
  - Mostly internal rule-A bits; only x1.0-1.8 inside the hot spots.
  - No eps* partial E3 event has Delta g2 on target. The closest is 5 bits off (2 events; out\e3depth_sub.txt).
- **Coupling between the sides:**
  - E1 outcome inside H-B: x1.05 (z +1.2).
  - eps* partial E3 inside H-A: x0.92 (sub-class, z -0.7) and x0.81 (whole class, z -1.2).
  - Pooled that is about 0.89, which is not significant. GUESS: at most 0.2 bit if real.

## 3. Limits and next steps

- R = 0 is unobservable at 32 bits. The carry-over rests on necessity, plus H1' for H-C.
  - "Necessary" takes the 14 listed outcomes of beta* (H8_recount_k14) as the only ones with positive mass.
  - It also uses R = 0 => Delta f1 = tau ^ ror(tau, 1) and eps3 = eps. Both are DERIVED from the trial code
    (rr2 = 0 and rr1 = 0).
- Toy support, read-only, from the other agent's collision_pattern\results.txt: real W = 8 collisions are strongly
  biased in Y9 bit 0 (filed layout) and in w8. The bias vanishes against the exact model that includes w8. Different
  word size, so this supports the result only qualitatively.
- Not done:
  - an exact recount (h8 counter) restricted to H-A/H-B/H-C;
  - a toy end-to-end run with the analogues;
  - joint DP proofs of c1[20] != c1[22], Y9[16] != Y9[17] and Y9[24] = Y9[25];
  - checking whether the outer basis can prescribe the Y9/KY bits instead of filtering;
  - y6[15] = 0 forcing (it needs a c1[31] sub-cube);
  - Y9 ranking inside the support (x8.7 more at 1/1024, under a premise).
- Blocked: nothing.

## 4. Files (this folder)

- Programs: hotspot.cu, build_smoke.sh, timing.sh, run_main.sh, ref.py, analyze_hot.py, followup.py, dp_proof.py,
  subcube.py, e3depth.py.
- Copied read-only from counter\value: ctr_gen.cuh, h8_deep.inc.
- Outputs: out\h_sub.bin and out\h_all.bin (40-word records), with *.txt counters and the analysis outputs.
- my_pids.txt: all jobs finished.
