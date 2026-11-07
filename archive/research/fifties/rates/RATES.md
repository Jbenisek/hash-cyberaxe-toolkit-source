
## Independent check 2026-10-09 (own CUDA, fresh seeds 2026100911-14; step CO matches outer.py scalar_outer on 1000 vectors, 0 mismatches; exact fq/fe counts 118897152/233715456 reproduced)
- Ordinary filter pass share: 106570625 / 1.0748e11 = 0.00099155 (se 9.6e-8); exact SHARE/2^64 = 0.00099146, z = +0.94; claimed ord jreuse 0.00099121 (se 2.0e-7), difference z = -1.5.
- Special frame (X13 = D1.d1 = 0, uniform over solutions, Y4 in class at 2^-13; first 150 frames all confirmed as roots by av11 verify, dflag 3): b uniform 3996123 / 4.030e9 = 0.00099148 (se 5.0e-7), ratio to ordinary 0.99993, z = -0.13; b fixed at q=0 and q=80000000 (1.0e9 each): 0.00099085 / 0.00099091 (se 9.9e-7), z = -0.70 / -0.64.
- Filter condition (2) fe&S != 0 on special frames: 0.0544168 (se 3.6e-6) vs ordinary 0.0544160 and exact 0.0544161; the claimed spc fresh 0.0544630 (z = +2.69 against ord) does not reproduce (z = +2.67 against this count), so it reads as chance.
- Verdict AGREE: the special-frame law leaves the filter pass share unchanged within 0.1% (b uniform) and 0.2% (b fixed). Not tested: j-reuse correlation (all draws here are fresh), and the av11 binary itself is too slow to brute-force 1e7 frames (7 ms per frame), so the frames came from a rejection sampler and av11 only confirmed a sample of them.

## Main measurement summary (main thread, from t_analysis.json and t_solver.json; 2026-10-09)
Runs: t_ord (ordinary whole-class outer steps, impl/outer.py law), t_spc (AV11 special frames, uniform accepted bases, j-reuse), t_spa (special, alternate seed).
| event | ordinary fresh | special fresh | special j-reuse | j-reuse design effect | intra-base z_rho |
|---|---|---|---|---|---|
| E3 cond (1) per step (fq&S!=0) | 0.0276844 | 0.0276860 / 0.0276989 | 0.0276813 / 0.0276824 | 0.99996 / 1.00012 | -0.30 / 0.97 |
| filter cond (2) per step (fe&S!=0) | 0.0544197 | 0.0544630 / 0.0544219 | 0.0544186 / 0.0544265 | 1.00005 / 0.99998 | 0.38 / -0.11 |
| filter pass (fq&fe&S!=0) | 0.0009916 | 0.0009940 / 0.0009910 | 0.0009920 / 0.0009922 | 1.00014 / 0.99997 | 1.31 / -0.26 |
| pre-check pass | 0.0002481 | 0.0002482 / 0.0002463 | 0.0002481 / 0.0002479 | 1.00011 / 1.00012 | 1.08 / 1.10 |
| solver roots per pass (1e5 passes, no G7/pre-check) | 5 | 5 | - | - | - |
| solver roots per pass (G7 + pre-check) | 1 | 1 | - | - | - |
Sampler rbar 1.0000066 / 0.9999983. Reading: no detectable difference between the special-frame law and the ordinary law in any success-relevant partial event, and no intra-base clustering under j-reuse (design effects 1.0000 +- 2e-4). Evidence only: the joint ~2^-91 success event itself is not observable.
