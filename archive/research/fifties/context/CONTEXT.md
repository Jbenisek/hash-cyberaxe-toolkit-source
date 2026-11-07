# CONTEXT - (P, X1, D) over the member walk of one context (2026-10-09)

Files: gen.py (writes ctx_gen.h from memberloop.CTX_LINES / DEP_LINES, and ref.json), ctx.c (exact walk, gcc -O3 -fopenmp, run.sh),
analyze.py (cross-checks + task 1 + summary), ctx_out.json (raw), context.json (summary + per-context counts).
P = C0.a1, X1 = X1, D = D1.d1 (movers.consts). Context = the seven outer words; members = all 2^19 of memberloop's class.

## Checks
- C walk vs Python full step CO (outer.scalar_outer): 18/18 sample values equal (3 contexts x 6 members).
- halfsearch.ctr_outer (movers) vs outer.py: 2,000/2,000 equal on (P, X1, D, Y4) when matched by Y4. halfsearch numbers its
  members differently (2^17 counter class, a subset of the 2^19 class), so the two codes agree on the lines but not on the member index.
- K(g) == Y1 + w12 on 2,000 real outer steps; closed forms below: 0 mismatches in 2,000 (4,000 checks).

## (1) Is X1 an additive shift of K? No.
Algebra: X1 enters F directly AND through A1 = X1 + x + S1 - a - b, and B1 = ROR12(x ^ (X9 + ROR16(X13 ^ A1))), so
K(g;X1) - K(g;0) = X1 + B1(g;X1) - B1(g;0), which depends on g through x, S1, a, b.
Numbers: 10,000 random constant sets with two random g: the difference changed with g in 10,000/10,000; it equalled X1 in 0.
On 2,000 real outer-step constant sets: changed with g in 2,000/2,000.

## (2) Distinct values over all 2^19 members, 256 contexts (seed 20261009)
| key | min | mean | max |
|---|---|---|---|
| P | 524,288 | 524,288 | 524,288 |
| D | 524,288 | 524,288 | 524,288 |
| X1 | 421,792 | 516,727.1 | 524,288 |
| (P, D) | 524,288 | 524,288 | 524,288 |
| (P, X1), (X1, D), (P, X1, D) | 524,288 | 524,288 | 524,288 |

Why (proof, checked): inside one context C0.d1, S11, X8, X4 (= Q4), w6 are fixed, and
- D = X11 - S11 - (ROL16(C0.d1) ^ P), so D is a bijection of P;
- Y4 = ROR7(((Y12 + C0.c1) ^ C0.b1)) with Y12 = ROR8((P + C0.b1 + w6) ^ C0.d1) (movers.invert), so Y4 is a bijection of P.
So every member has its own P and its own D: the 2^19 (P, D) pairs never repeat, and adding X1 cannot merge anything.
X1 alone does repeat (mean about 1.4% collisions, worst context 19.5%).

## (3) Multiplicity of (P, D) classes, context 0
All 524,288 classes have size 1 (histogram {1: 524288}). By the proof this holds in every context.

## Independent recheck (2026-10-09, recheck.py: own walk + movers.consts black box) - AGREE
- 5 fresh contexts (seed 0x50C0FFEE), all 2^19 members through outer.scalar_outer + movers.consts: distinct P, D, (P,D) = 524,288 each in 5/5; own numpy P/D derivation matched consts on all 2,621,440 members (0 mismatches); K(D2.a1) == Y1 + w12 on 40,960 sampled members, 0 failures.
- Additive X1, 10,000 fresh cases (5,000 random constant sets, 5,000 from real outer steps; two random g each): K(g;X1)-K(g;0) changed with g in 10,000/10,000, equalled X1 in 0. CPU only, about 55 s per context in parallel.
