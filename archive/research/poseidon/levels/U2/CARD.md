# CARD U2 - the dense block, rounds R1, R2, R3 (levels L2, L3, L4 for r=1 and r=2)

Learning card, no attack scores. Folder `./research/poseidon/levels/U2`. Written 2026-10-12. Labels: OBSERVED (a command in this folder measured it), PROVED, DERIVED, GUESS. Every script is single-process; outputs `*_output.txt` sit next to the scripts. Library: `u2lib.py` (exact (A,B)-polynomials, F_p univariate polys, line polynomials, tracker), `toylib.py` (toy copies, exhaustive over q^2 inputs, rank mod q).

## 1. The card (what the three rounds read, write, need, and how they move)

| field | R1 | R2 | R3 |
|---|---|---|---|
| reads | 3 lanes of P0 (plane `M*(A,B,K)`) | 3 lanes of R1.M | 3 lanes of R2.M |
| writes | 3 lanes, each `sum_j M_ij (l_j + c)^5` | same | same |
| S-box inputs | affine in (A,B): `l_i = M_i0 A + M_i1 B + M_i2 K + c1_i` | degree-5 polys in (A,B) | degree-25 polys in (A,B) |
| (A,B)-degree after M / support | 5 / 21 monomials (full triangle) | 25 / 351 (full) | 125 / 8001 (full) |
| (nk,rho)-degree / monomials | 25 / 301 of 351 | 125 / 7751 of 8001 | 625 / **195001** of 196251 |
| top form in tau=U/V (U=u^5,V=v^5) | degree 5, 6/6 coeffs nonzero | degree 25, 26/26 | degree 125, 126/126 |
| F_p-roots of the top form, lanes 0,1,2 | 1, 1, 0 | 1, 2, 1 | 0, 0, 1 |
| implicit equation of the image surface (after M) | degree **25** (toy q=257) | DERIVED 625; toy saturates | DERIVED 15625 |
| zero locus of an S-box input | a **line** in (A,B), exactly q points on a toy | quintic curve, ~q points | degree-25 curve, ~q points |
| freedom | (A,B) in F^2, all of it | same | same |
| what moves when it changes | every lane moves all 3 outputs; nothing is dropped | same | same |

## 2. Observations by question

**Q1 monomial law, R3 [OBSERVED `q1_support.py`, `q1_support_output.txt`].** Exact expansion of the (A,B) polynomial into (nk,rho) (A=(nk+c00)^5, B=(rho+c01)^5; matrix product of binomial tables mod p). R1 lanes: 301 monomials, R2: 7751, **R3: 195001 per lane for all three lanes**, equal to the prediction. In every round and lane: nonzero coefficients outside the law set = 0, law monomials that are zero = 0. The zero coefficients inside the total-degree triangle are exactly 50 (R1), 250 (R2), **1250 (R3)**, i.e. 2*5^k*... = 50, 250, 1250 (50*5^(k-1)); all structural, not a single accidental zero in 195001 coefficients. (A,B)-supports are full triangles: 21, 351, 8001. Run time 54 s.

**Q2 top forms [OBSERVED `q2_forms.py`, `q2_forms_output.txt`, `q2_forms.json`].** Recurrence PROVED: top form `F_{k+1,j} = sum_i M_ji F_{k,i}^5`, `F_{0,j} = M_j0 U + M_j1 V`; the (nk,rho) top form is `F(nk^5,rho^5)`. Each F_p root tau0 of F_k gives exactly one linear factor of the (nk,rho)-form (unique fifth root); the direction v=0 would add one more if the tau-degree dropped (never did). All 12 forms squarefree, all coefficients nonzero.
- R0: 1 linear factor per lane (known). R1: lane0 {1+4} (one linear + one irreducible quartic), lane1 {1+4}, lane2 irreducible quintic (0 linear). R2: lane0 {1,5,19}, lane1 {2 linear, 2 quadratics, 1 quartic, 1 quintic, 1 of degree 10}, lane2 {1,2,5,17} (factor-degree pattern, see file). R3 (degree 125): roots 0, 0, 1 (full factor pattern not computed).
- gcds between all 66 pairs of forms R0..R3 (12 forms): all coprime (degree 0 gcd) [OBSERVED]. PROVED consequence: no direction (even over an extension field) makes two of the 12 lane forms vanish; and since `F_k = M * (F_{k-1})^5` with M invertible and x->x^5 injective, the top vector is never 0: **on every line at least one lane keeps full degree, at every round**.
- Every R2 lane has an irreducible degree-5 factor. Checked whether this is structural (`q2b_patterns.py`, 60 random Cauchy-MDS over primes 2 mod 5, 180 lanes): fraction of lanes with a degree-5 factor 0.27 (MDS) vs 0.19 (random polynomials); R1 patterns match random quintics (quartic+root 0.23 vs 0.22). Verdict: no sign of structure; coincidence (three of three lanes at 0.27 each ~ 2%).

**Q3 implicit equation [OBSERVED `q3_implicit.py`].** Toy q=257, all 66049 points of R1.M: no nonzero polynomial of degree <=24 (rank 2925 = full on 2985 sampled points, PROVES none on the whole set); at degree 25 nullity 1, and that polynomial vanishes on all 66049 points: **least degree 25, unique** (`q3_q257_R1_output.txt`, 25 min). DERIVED: surface = image of the plane under `(l1^5,l2^5,l3^5)` with an affine relation among the l's; two generic planes give two quintics in (A,B) with 25 common points, none at infinity, map injective -> degree 25. Same argument gives degree (5^k)^2 = 25^k for R_k (R2: 625, R3: 15625) - GUESS/DERIVED, not testable at q=257 (counting bound for 66049 points is degree 72 < 625). Small q (`q3_small_output.txt`): least degree R1 = 9, 9, 13, 16, 17, 19 for q = 17, 23, 29, 37, 43, 53 (below the counting bound 11,13,16,19,21,24, reduction mod x^q-x); **R2 = counting bound exactly (11, 13, 16, 19, 21 for q=17..43)**: the R2 surface shows no low-degree equation at toy scale. R0 plane: degree 1 in every toy.

**Q4 zero loci [OBSERVED `q4_zero_loci.py` (q=257, 30 seeds), `q4_real_zero_loci.py` (real field)].**
- Toy q=257: R1 loci have exactly 257 points in all 30 seeds (lines in (A,B), PROVED); R2/R3 loci 217..296, mean ~255 (about q). Pair intersections: R1xR1 always exactly 1 (PROVED: lines, minors nonzero); other types mean 0.78-1.13, histograms Poisson-like (max 7). Three lanes of one round zero at once: 0 of 30 seeds, each round. Triples among all 9 curves: 8 (expected ~10 by chance).
- Real field: R1 lines concurrent iff `(M^-1 c1)_2 = -K`; **not equal** (values in `q4_real_zero_loci_output.txt`), so the three R1 curves never share a point; each pair meets in exactly 1 point (verified with the reference by recomputing S-box inputs). All 33 pairs except R3xR3 solved exactly (resultant, degree = Bezout bound every time: 5, 25, 125; roots by gcd with x^p - x): number of F_p points per pair 0..3 (31 total), every point re-verified; **0 of 30 points lies on a third curve**.

**Q5 degree-drop lines [OBSERVED `q5_q7_lines.py`, `q5_q7_lines_output.txt`].** Exact line polynomials, random offsets.
- R0 drop directions (3): after R0 degrees [4,5,5]/[5,4,5]/[5,5,4]; after R1, R2, R3 back to full 25,125,625 in all lanes (transient, one MDS).
- Roots of every top form with F_p roots (9 directions: R1 lanes 0,1; R2 lanes 0,1,1,2; R3 lane 2): exactly one lane loses exactly one degree (24, 124, 624) in exactly that round, and the next round is full again. Nothing persists. Empty families (recorded): both lanes dropping at once (gcds coprime, PROVED over closure); R3 lane 0 and lane 1 have no F_p root (so no F_p direction touches the lane that feeds the partial S-box at R4 - hand-off to U3, DERIVED); horizontal, vertical, U=V, U=-V lines: no drop.
- Offsets: through a=0 only: dense. Through a=b=0 (S-box inputs of R0 both zero): the polynomials are in t^5 only (exponents = 0 mod 5), 6/26, 26/126, 126/626 nonzero coefficients, i.e. the (A,B)-line through the origin. Offsets a=b=1 and (i,-i): dense, nothing special.

**Q6 affine relations [OBSERVED `q6_relations.py`, q=257].** Affine span dimension of the point set: init, R0.C, R0.S, R0.M, R1.C = 2 (planes; lane 2 constant before R0.M, plane P0 after); **R1.S, R1.M and everything later = 3** (the surface is not planar). Between lane sets of different steps: R1.M with R2.M (and R1.S/R2.S/R3.M combinations): 0 affine relations (affine dim 6 of 6). Within a round: S output vs M output 3 relations (M is linear). Polynomial relations between the 6 lanes (R1.M, R2.M): none of degree <=4 (provably), **exactly 3 independent of degree 5** (the known `M^-1 R2.M = (R1.M + c)^5`), all vanish on all 66049 points.

**Q7 tracker vs exact [OBSERVED].** 20 random lines x R1..R3 x 3 lanes = 180 exact polynomials: tracker equals the exact top coefficient everywhere; every degree exactly 5^(k+1); **0 zero coefficients** among exponents 0..deg in all 180 (also on the 7 special direction/offset families except a=b=0, structural).

**Q8 cost table [OBSERVED `q8_cost_table.py`].** Counting field class: x^5 = 3 mult, M = 9 mult. Full round 18 mult / 3 S-boxes, partial 12 / 1. Cum. through R3: 12 S-boxes, 72 mult, degree 5^4 (r=1 and r=2). Totals: r=1: 25 S-boxes, 156 mult (144 with R0 lane 2 constant and R63 dead rows folded), degree 5^9; r=2: 26 S-boxes, 168 mult (156 folded), degree 5^10. A full round buys one factor 5 in degree for 18 mult; a partial round buys one factor 5 for 12; degree exponent = number of rounds, not S-boxes.

## 3. Boring details worth keeping
- Support law cost nothing: coefficients are never accidentally zero in 195001 R3 values, 180 line polynomials, 12 top forms.
- Resultant degrees hit the Bezout bound exactly (5, 25, 125): no intersection at infinity or hidden common component.
- R1 is the only round where zero loci are lines; this makes R1 the only round with exact closed-form two-lane-zero points.
- Toy degree saturation: R1 equation degree 25 only visible when q is large enough (q>=257); at q<=53 reduction dominates.

## 4. Questions raised
1. Is the implicit degree of the R2 surface really 625 (and R3 15625)? Needs q ~ 1000+ and a smarter method than dense linear algebra (points on a curve rather than the surface, or interpolation along lines).
2. Do the factor patterns of R3 forms (degree 125; only roots known) show anything? Full DDF needs ~minutes per lane.
3. Why 1250 = 50*5^(k-1) structural zeros: closed form of the support law and does it extend to the partial rounds R4/R5?
4. The F_p points where two S-box inputs are zero (31 found): do any have useful structure after R4 (S-box derivative zero in two lanes of one round never happens: 0 triple points)?
5. Lines in (A,B) coordinates through the origin are sparse in t; do sparse curves exist for other S-box-input zero points (a=0 line with b free was dense)?
6. Does the missing F_p root of R3 lane 0 stay missing for other Cauchy matrices (probability ~37% each), i.e. is it luck of this M?
