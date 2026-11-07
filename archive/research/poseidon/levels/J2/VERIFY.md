# J2 verification: the "many small factors" anomaly is FORCED, not real-constant structure
Scripts: v2.py (modes real/rc/mds/cap/slant/randg5/randpoly; outputs out_*.txt), v3.py (exact prediction). Validated impl: poseidon_ref constants P, RC, MDS, CAPACITY (J2's j2_real.py already value-checked the polynomial against round_full; v2 asserts degree 625).

## (1) Reproduction - OBSERVED
Same construction (lane 0 after R0..R3 as polynomial in nk, rho=rho0, cap=2^65; divide (f-f(nk0))/(x-nk0), degree 624). 6 real trials (seed 11): factor counts 8,10,9,9,18,27; degree patterns like [500 36 36 18 12 12 6 4], [124 100 80 60 31 25 20^6 15 12^3 6 4^5 3 1^4]. Every trial has >=1 degree-4 factor. Matches J2's report.

## (2) Controls - OBSERVED (6 each, random nk0, rho0)
| control | factors (range) | deg-4 factors per poly | verdict |
|---|---|---|---|
| real | 8-27 | 1,1,1,4,1,5 | anomaly |
| (a) random round constants | 9-17 | 1,4,3,3,1,7 | SAME |
| (b) random Cauchy MDS | 7-19 | 4,4,3,4,1,3 | SAME |
| (c1) random capacity | 7-14 | 1,1,3,2,4,5 | SAME |
| (c2) generic slanted line rho=a*x+b | 3-8 | 0,0,1,0,0,0 | anomaly GONE (random-like) |
| (d1) random poly deg 624 | 4-10 | 0 in all 4 | random |
| (d2) random g((x+c)^5), deg g=125 | 9-20 | 7,4,5,6,1,1 | SAME as real |
So the anomaly does not depend on the constants, MDS or capacity. It depends only on the line being rho=const (so lanes 1,2 are constant) and disappears on a generic line. Controls (c2) and (d1) can and do fail it, so the instrument discriminates.

## (3) Explanation - PROVED (algebra) + OBSERVED (exact check)
Along a line with rho constant, round 0 sees S-box inputs (x+c0)^5 on lane 0 and constants on lanes 1,2. After the MDS every lane is affine in y=(x+c0)^5. Hence f(x)=g(y), y=u^5, u=x+c0, deg g=125 (verified: Taylor shift of f to u has zero coefficients at all exponents not divisible by 5, all 6 trials). Consequences:
- f(x)-f(x0) = g(u^5)-g(u0^5), divisible by u^5-u0^5. The cofactor (u^5-u0^5)/(u-u0) is a quartic; p mod 5 = 2 has order 4, so it is irreducible over F_p, with roots zeta*u0 (zeta primitive 5th root of unity in F_{p^4}). This is the guaranteed degree-4 factor in every trial (the "2.4 vs 0.25" excess; extra degree-4 factors come from factors of h below).
- The rest is h(y)=(g(y)-g(y0))/(y-y0), degree 124, which behaves like a random polynomial. Substituting y=u^5: an irreducible factor of h of degree d with 4 not dividing d gives pieces of degree d (once) and lcm(d,4) (4d/lcm(d,4) times): d=1 -> 1,4; d=3 -> 3,12; d=5 -> 5,20; d=7 -> 7,28; d=15 -> 15,60. This is the origin of J2's recurring 12, 20, 28, 60 (= 4 x odd d); and of repeated factors such as 28^5, 20^6 when h has several such factors. If 4 | d the lift is 5d or 5 x d (tested directly).
- Exact check (v3.py, 6 real trials): the degree multiset predicted from factoring h(y) (124) plus this lifting rule equals the observed 624-factorisation in 6 of 6. Random g(u^5) controls show the same pattern. J2's GUESS (small monodromy group tied to 5^4) is replaced: only the first round's 5th-power structure matters; the group is a wreath-type product, imprimitive with blocks of 5, and nothing more.
Not 5^4 composition: the other three rounds do not compose in one variable (the state has 3 lanes).

## (4) Use for collisions - DERIVED
- The quartic factor and every lifted piece of degree 4k correspond to u = zeta*u', zeta^5=1, zeta != 1: points in F_{p^4}, not in F_p. Since gcd(5,p-1)=1 the map x->x^5 is a bijection of F_p, so no F_p input pair other than x=x0 is gained: useless for collisions. It is just the statement "(x+c)^5 equal", the trivial factor of round 0 over the extension field.
- The only F_p collisions on the line are the roots of h(y) in F_p: 0-4 per trial (random-like, ~1 expected), i.e. nothing beyond generic count. The decomposition does reduce factoring work (degree 124 instead of 624) but gives no collision in lane 0 after R3 or earlier/later; nothing for the output.
- It could only matter as a bookkeeping fact: level polynomials along rho=const lines in R3 are functions of u^5 (degree 125 in y), which is a free 5x saving for root finding on that line. A generic line loses it.

Labels: OBSERVED = reproduction and control tables; PROVED = f=g(u^5) and the lifting rule; DERIVED = no collision value; GUESS = none left. Residual limits: 6 samples per control (small), factor degrees only (no Galois group computation).
