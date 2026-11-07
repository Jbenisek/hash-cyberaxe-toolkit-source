# Is the real Orchard skip-line polynomial F_j(W) functionally decomposable?  (2026-10-12)

Answer: NO, for every (r, j, d) finished (r=2, j=2 still running at hand-off). No remainder was constant; no inner factor B of degree 5, 25 or 125 exists
for r = 0, 1, 2 and j = 0, 1, 2. So the round-1 factor t^5 is the only inner factor; no new collisions of the B(W) kind.

Code: decomp.py (circuit over flint fmpz_mod_poly, truncated reversed-series propagation, m-th root series for B,
quotient-ring evaluation, divide-and-conquer B-adic digits), run1.py (controls), run2.py (real runs), run2.log (raw).
Line model and constants reused from orchard/math/attack.py (validated 11/11 vectors, digest = line model).

## Method as run
1. Screen (SOL6 method): top d coefficients of F via truncated reversed series H(t) = t^deg s(1/t) mod t^d pushed through
   the circuit (round 1 MDS onward, rounds 2,3, r partial, 60..63); B = polynomial part of F_monic^(1/m), m = n/d, B(0)=0;
   then the same circuit evaluated in F_p[W]/(B). Remainder nonconstant => no degree-d decomposition.
2. Cross-check (stronger, since fully expanding is cheap with flint): F expanded in full, then the complete B-adic digit
   test (F = sum c_i B^i, all c_i must be constant), divide and conquer.

## Controls (run1.py, run2.py)
* Decomposable by construction: round-1 output made affine in Z = Bc(W), Bc random monic, Bc(0)=0, deg 5 and deg 25
  (F = G(Bc(W)), degree 5^7 resp. 25*5^6). Screen recovers B == Bc exactly and the remainder is constant (degree 0), both d.
  Full digit test on the d=5 control: 0 nonconstant digits of 15626.
* Same controls tested with the wrong d (d=25 on the 5-composition, d=5 on the 25-composition): remainder degree 20 / 4,
  i.e. nonconstant, as it must be (the screen is one-sided, here it correctly rejects).
* SOL6's toy counterexample: NOT reconstructed (I do not have its statement); the two controls above stand in for it.

## Results (remainder degree of F mod B; constant would be degree <= 0; d-1 means a generic full-size remainder)
| r | j | d=5 | d=25 | d=125 |
|---|---|---|---|---|
| 0 (deg 5^6) | 0,1,2 | degree 4, nonconstant | degree 24, nonconstant | degree 124, nonconstant |
| 1 (deg 5^7) | 0,1,2 | degree 4, nonconstant | degree 24, nonconstant | degree 124, nonconstant |
| 2 (deg 5^8) | 0,1,2 | degree 4, nonconstant | degree 24, nonconstant | degree 124, nonconstant |

Full B-adic digit test (number of nonconstant digits; decomposable would be 0):
r=0 (all j): d=5: 3124 of 3125 positions, d=25: 624, d=125: 124 (i.e. every digit except the leading one is nonconstant).
r=1 (all j): d=5: 15624, d=25: 3121, d=125: 624.
r=2 (j=0,1,2): d=5: 78124 of 78125, d=25: 15621, d=125: 3121.

STATUS update: `run2.log` now contains the completed r=2,j=2 full digit test: d=5 has 78124/78125 nonconstant digits, d=25 has 15621/15625, and d=125 has 3121/3125. Thus the screened degree set d=5,25,125 is complete for r=0,1,2 and j=0,1,2. The larger d=15625 and d=78125 candidates are separate; d=78125 is the D352 timeout.

Since no case had a constant remainder, no "is B a permutation of F_p" question arises.
Caveats: d = 5, 25, 125 only (d | n only for powers of 5; other d are impossible by degree anyway as n is a prime power
5^k, a decomposition degrees must divide it). Real constants only, no toy counterexample.

## UPDATE 10-12 17:40 (historical coordinator note)
The original hand-off said the r=2,j=2 digit test was still running. This is
superseded by the later `run2.log` completion recorded above: r=2,j=2 now has
the exact d=5,25,125 counts 78124/78125, 15621/15625, and 3121/3125.
