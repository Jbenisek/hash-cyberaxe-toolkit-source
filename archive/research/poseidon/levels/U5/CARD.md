# CARD U5 - the MDS matrix M as an object (level card, filled in)

Date 2026-10-12. Folder `./research/poseidon/levels/U5`. Learning only, no score estimates. Real target = Orchard Pallas, matrix M from `orchard-pallas-constants.json` (read as data, `poseidon_ref.py` imported). Labels: OBSERVED (script + output file named), PROVED, DERIVED, GUESS. Scripts run from this folder with `python3 <script>`; each wrote `<script>_output.txt`. Helper `u5_lib.py` = exact big-int F_p and F_{p^3}=F_p[x]/(charpoly) arithmetic. Packages installed for this work with pip: sympy (unused), gmpy2 (unused), python-flint (used for factoring/primality).

Notation: p = Pallas prime, n = p^3-1, alpha = the class of x in F_{p^3}=F_p[x]/(x^3 - T x^2 + S x - D), T=trace M, S=sum of principal 2x2 minors, D=det M (hex in ATLAS G3). Cauchy form M_ij = 1/(x_i+y_j).

## 1. Eigen-structure (Q1)  [u5_a.py -> u5_a_output.txt]
- OBSERVED: charpoly irreducible, so the three eigenvalues are alpha, alpha^p, alpha^(p^2), pairwise distinct. DERIVED (distinct eigenvalues): M is diagonalisable over F_{p^3} (not over any smaller field), minimal polynomial = charpoly.
- OBSERVED: trace(alpha)=T and norm(alpha)=D checked in F_{p^3}; alpha^(p^3)=alpha. Conjugates printed as coordinates in the basis 1,alpha,alpha^2 (u5_a_output.txt).
- OBSERVED: eigenvector for alpha, normalised first coordinate 1, is (1, v1, v2) with v1,v2 in F_{p^3} (printed as decimal triples in u5_a_output.txt); M v = alpha v verified; the eigenvector for alpha^p is exactly the coordinate-wise Frobenius of the first (verified).
- OBSERVED (null): eigenvector entries are NOT of the form c/(x_i + t) for one t in F_{p^3} (u5_b_output.txt, last line). No simple closed form found.
- OBSERVED: the Cauchy displacement identity X M + M Y = all-ones matrix (X=diag x_i, Y=diag y_j); it is inherited by the inverse: Y M^-1 + M^-1 X = +(M^-1 1)(1^T M^-1) (u5_a_output.txt, u5_f_output.txt). PROVED (one line each: multiply by M^-1).
- Not found / not done: eigenvectors in closed form via x_i; left eigenvectors.

## 2. Exact multiplicative order of M (Q2)  [u5_c.py, u5_fact.py, u5_order.py, u5_f.py]
- OBSERVED: ECM-type factoring (python-flint `fmpz.factor_smooth(90)`, 8 s for C, 626 s for C'') COMPLETES the factorisation of p^3-1. Each factor tested probable prime (flint BPSW; caveat: BPSW is not a proof) and the products were checked (u5_order_output.txt):
  - p - 1 = 2^32 * 3 * 463 * 539204044132271846773 (69 bit) * 8999194758858563409123804352480028797519453 (143 bit)
  - p^2+p+1 = 3 * 73 * 5839 * 12221196943 * 5187662682403 * 487887715480415483992657 (79 bit) * 21186043132281546156793608169660962271252226488966104018788253841360240111557635227669180162173314659 (334 bit)
  - v3(p-1)=1, v3(p^2+p+1)=1, so 3^2 divides n; n = 2^32 * 3^2 * 463 * 73 * 5839 * 12221196943 * 5187662682403 * (the four large primes above).
- OBSERVED: alpha^(n/q) != 1 for EVERY prime q | n (11 primes, u5_order_output.txt). DERIVED: **alpha is a primitive element of F_{p^3}, the multiplicative order of M is exactly p^3-1 (about 2^765)**, and M acts on the nonzero vectors of F_p^3 as a single cycle (Singer cycle): every nonzero vector is carried to every other nonzero vector by exactly one power M^k, k in [0,n). The order of M modulo scalars is p^2+p+1 (alpha^(p^2+p+1) = D, a scalar, OBSERVED; and primitivity gives no smaller scalar power).
- OBSERVED (before the factoring finished, u5_c_output.txt): all known small-prime exponents are the full ones (2^32, 3^2, ...), consistent with the result.
- Subgroup elements, OBSERVED (u5_f_output.txt): M^(n/2) = -I; M^(n/3), M^(n/463) and M^(n/539204044132271846773) are scalars (these primes divide p-1, so the order-q elements lie in F_p); M^(n/q) for q = 73, 5839, 12221196943, 5187662682403, 487887715480415483992657 are NON-scalar matrices of order q, and all of them are MDS. M^(p^2+p+1) = D*I.
- Not done: the cycle structure of x -> x^5 on F_p^* now needs the factorisation of f-1 for the 69-bit and 143-bit primes dividing p-1 (open learning item for the S-box level).

## 3. Powers of M and MDS (Q3)  [u5_d.py, u5_e.py]
- OBSERVED real: all 9 entries of M^k and of M^-k are nonzero for every k = 1..200000 (11.7 s), and M^k is fully MDS (entries and all nine 2x2 minors) for every k = 1..1000. No failure.
- PROVED: cofactor(M^k) = det(M^k) (M^-k)^T, so a 2x2 minor of M^k is zero iff the matching entry of M^-k is zero (also checked k=1..59 numerically). So "M^k is MDS" is the same as "all 18 entries of M^k and M^-k are nonzero".
- PROVED: M^k = a0 I + a1 M + a2 M^2 with (a0,a1,a2)=alpha^k (checked k=0..14). Entry (i,j) of M^k is the linear form a0*delta_ij + a1*M_ij + a2*(M^2)_ij, i.e. a projective LINE in the plane P^2(F_p) = F_{p^3}^*/F_p^*; entries of M^-k give 9 CONICS (quadratic in a). Off-diagonal entries do not involve a0: they vanish when a2/a1 = -M_ij/(M^2)_ij (six values printed in u5_d_output.txt). So the "bad" powers are the points where alpha^k lies on 9 lines + 9 conics.
- OBSERVED toy (u5_e_output.txt), random Cauchy M with M primitive (generator of F_q^3), exhaustive over one projective period q^2+q+1: q=257: 4043 bad of 66307 (6.1%, 18/q=7.0%), first bad k=11; q=769: 13749 of 592131 (2.32%, 18/q=2.34%), first bad k=110; q=1009: 18067 of 1019091 (1.77%, 18/q=1.78%), first bad k=37. The number of bad powers in one period equals exactly the number of bad projective points (as it must since alpha^k visits every point once). The equivalence "minor zero <=> entry of M^-k zero" had 0 mismatches over every k. DERIVED: for Pallas the bad fraction is about 18/p (~2^-250), the first bad k is expected near 2^250: "M^k MDS" is effectively true for any k anyone will use; the asked k <= 1000 is a null result. The ~18/q prediction is a good (slightly low for tiny q because lines/conics overlap) description.

## 4. Cauchy parameters (Q4)  [u5_b.py -> u5_b_output.txt]
- OBSERVED: x = (0, x1, x2), y = (y0,y1,y2) as in ATLAS G3 (one gauge: shift x->x+s, y->y-s). Differences: x1-x0 (251 bit), x2-x0 (251), x2-x1 (247), y1-y0 (253), y2-y0 (252), y2-y1 (252): all large. Legendre symbols: x-diffs (-1,+1,+1), y-diffs (-1,-1,+1).
- OBSERVED (null): among all 12 differences/sums/values {x_i-x_j, y_i-y_j, x_i+y_j, x_i, y_j, det, T, S} no ratio is a small rational u/v with |u|,v<=60 (the only hits are artefacts of the gauge choice x0=0). No integer linear relation with |c|<=4 among x1-x0,x2-x0,y1-y0,y2-y0. None of the 192 round constants is a rational u/v (|u|,v<=12) multiple of any Cauchy quantity, or equal to +-one. The Cauchy parameters look unrelated to the constants and to small numbers.
- OBSERVED/PROVED: the Cauchy determinant formula reproduces det M; the closed Cauchy inverse formula (M^-1)_{ji} = prod_k(x_i+y_k) * prod_k(x_k+y_j) / ((x_i+y_j) prod_{k!=i}(x_i-x_k) prod_{k!=j}(y_j-y_k)) matches M^-1 in all 9 entries.
- PROVED (from the det formula, Legendre multiplicative): leg(det M) = prod_{i<j} leg((x_j-x_i)(y_j-y_i)) * prod_ij leg(M_ij). Real: (-1)(+1)... product = -1 = leg(det) (nonresidue), checked also in three toys.
- OBSERVED: M^-1 is not Cauchy (the 1/entry second difference test fails) but has displacement rank 1 (section 1).
- Legendre pattern of M: rows (-,-,+), (-,+,+), (+,-,+); of M^-1: (+,-,-), (-,-,-), (+,-,+).

## 5. Planes where Mv has a zero entry (Q5)  [u5_b.py]
- PROVED/OBSERVED: P_i = {v : (Mv)_i = 0} = plane with normal row i of M (three planes). The pairwise intersections P_i ∩ P_j are exactly the columns of M^-1 (cross(row_i,row_j) = constant * a column of M^-1; constants det M, -det M, det M; verified): the three planes are the "coordinate planes" seen from the image side, M^-1 e_k.
- OBSERVED: X6 trail vector d = (0, M02, -M01) satisfies (Md)_0 = 0 and (Md)_1, (Md)_2 != 0; so the X6 line lies in P_0, and meets P_1, P_2 only at 0 (consistent with MDS: all 2x2 minors nonzero). The three lines L_i = {v_0=0} ∩ P_i = span(0, M_i2, -M_i1) have slopes -(x_i+y_2)/(x_i+y_1): Moebius images of the Cauchy x_i (PROVED from M_ij=1/(x_i+y_j), verified).
- OBSERVED: none of the L_i lies in the direction plane of P0 (n.L_i != 0, all three values printed), and n.d != 0 for d=L_0, as ATLAS X3 said. The ATLAS line u = {v_0=0} ∩ P0dir lies in none of P_0,P_1,P_2 (rows . u all nonzero). The lines P_i ∩ P0dir are printed (u5_b_output.txt); they are three further lines in the 2-dim P0 direction space.

## 6. The plane normal n = row 2 of M^-1 (Q6)  [u5_b.py]
- PROVED/OBSERVED: n.col_j(M) = (0,0,1): n is the dual of column 2; the P0 direction space {n.d=0} = span(col 0, col 1) of M. So the plane of round-0 states is spanned by the columns of M that multiply A and B (ATLAS X2) and its normal is the dual vector of the column that multiplies the constant K.
- OBSERVED: n_j are given by the Cauchy inverse formula of section 4 (so n is a product of Cauchy differences and sums, no extra structure). In the F_{p^3} picture of section 7 the normal's functional is beta_n = alpha^-1 * beta_2 (verified).

## 7. Basis in which M is multiplication by alpha (Q7)  [u5_b.py]
- Construction PROVED + verified on random vectors: Krylov basis e0, M e0, M^2 e0 (Krylov determinant nonzero), phi(c0 e0 + c1 M e0 + c2 M^2 e0) = c0 + c1 alpha + c2 alpha^2. Then phi(Mv) = alpha*phi(v). Every lane is a trace form: v_i = Tr(beta_i * phi(v)) with beta_i determined by the trace Gram matrix.
- OBSERVED values: phi(e0)=1, phi(e1), phi(e2) and beta_0, beta_1, beta_2 printed in u5_b_output.txt (coordinates in 1,alpha,alpha^2); output functional (row 0 of M) = alpha*beta_0; beta_n = alpha^-1 beta_2. All are generic-looking elements: none has zero alpha^2 coefficient or an inverse with zero alpha^2 coefficient; the norms are large with no visible pattern (legendre of norm: phi(e1) -, phi(e2) -, beta_0 -, beta_1 +, beta_2 -, beta_n +, beta_out +). Trivial identities: Tr(beta_i phi(e_j)) = delta_ij, Tr(beta_0)=1, Tr(beta_1)=Tr(beta_2)=0.
- DERIVED consequence: in this picture a partial or full round's linear part is a multiplication by the fixed primitive element alpha followed (before it) by "read/write one lane = a trace form". In a stretch with no S-box the state after k steps is alpha^k * phi(state), and the output lane is Tr(beta_out alpha^(k-1) z).
- Not found: no simpler (e.g. sparse or small) description of lane 0 / e2 / output row; they are generic F_{p^3} elements.

## 8. Is M special among Cauchy matrices? (Q8)  [u5_d.py, 1000 random Cauchy over F_p, seed 20261012]
- OBSERVED: 1000 random Cauchy matrices: residue count among 9 entries (0..8): 2,24,59,154,238,260,179,67,17; real = 5 (typical, mode). Among 9 minors, real = 6 (random mode 4-5). leg(det) = -1 in 50.6% (real -1). Same exact 9-entry Legendre pattern as real: 1 of 1000 (expected 1.95); same M^-1 pattern: 1; both: 0.
- OBSERVED: charpoly irreducible in 31.3% (expected 1/3; real: irreducible). Among irreducible ones, "full smooth part of the order" (alpha^(n/q) != 1 for the 7 smallest primes) 94 of 313 (30.0%); real is full, and by section 2 real is fully primitive. Joint (irreducible, det nonresidue, full smooth order): 9.4% of random matrices (real has all three).
- OBSERVED: min bit length of the nine entries: real 251, random mode 251, spread 242..253. M^2 MDS in all 1000.
- DERIVED: nothing about the real M is outside the ordinary range of random Cauchy matrices on these statistics. Being primitive has probability phi(n)/n = 0.328 for a random element of F_{p^3}^* (computed from the factorisation, one line above), so irreducible + primitive is a roughly 1-in-9 coincidence (1/3 * 0.33), not evidence of design. GUESS: M came from the Grain-LFSR generator of the halo2 source (random x,y) with no special selection.

## 9. What this card means for the other levels (interaction notes)
- Every round uses the same M, so every statement above holds at all 9-10 levels at once (ATLAS cards R0..R63, step M).
- Singer-cycle fact (section 2): M has no invariant subspace and no short orbits; in particular there is no vector with M^k v = v for small k, and no round structure can recur with period < p^3-1 (DERIVED).
- The three planes P_i (section 5) are where, after an M step, one lane is zero; if a later step is a partial round whose S-box is on lane 0, the plane P_0 is where S(0)=0 (zero point of that S-box input before constants). That connects the partial-round levels R4/R5 to the plane P_0 and its intersections with the P0 direction space (section 5 lines).
- The M^k = a0 I + a1 M + a2 M^2 form lets a stretch of rounds with no S-box (none exists inside the reduced hash, but the linear parts between S-boxes compose differently when constants are carried, ATLAS X5) be written with three F_p coefficients.

## Top 5 observations
1. p^3-1 is now fully factored (the two "unfactored" cofactors split into 69+143-bit and 79+334-bit primes) and M is a primitive element: order exactly p^3-1, Singer cycle on F_p^3 \ {0}, projective order p^2+p+1.
2. M^k is MDS for all k tested (200000, both signs); the criterion is linear/quadratic: bad k = alpha^k on 9 lines + 9 conics of P^2(F_p); toys at q=257,769,1009 reproduce the 18/q count exactly (bad powers = bad points).
3. The three planes {(Mv)_i=0} intersect pairwise in the columns of M^-1; the X6 line lies in P_0 and misses P_1,P_2; the three lines {v_0=0}∩P_i have slopes that are Moebius images of the Cauchy x_i.
4. Cauchy parameters, constants and small numbers: no relation at all (null result); M^-1 is not Cauchy but inherits displacement rank 1; M has no statistic outside the random-Cauchy range.
5. In the basis where M = multiplication by alpha every lane is a trace form Tr(beta_i z) with beta_n = alpha^-1 beta_2; all are generic elements (no sparse description found).

## Questions raised
- With M primitive: does the whole reduced hash have a useful description in F_{p^3} coordinates between S-boxes (alpha^k * phi(state)), e.g. the r=1 and r=2 partial blocks, where the constants c_{r,1}, c_{r,2} can be carried forward (ATLAS X5)?
- The pairs (P_i, S-box zero set): is there a state in P0 whose lane after M is simultaneously on P_0 for two consecutive rounds (partial block r=2 uses (M d)_0 = 0)? Counting this needs the lines P_i ∩ P0dir (section 5).
- Cycle structure of x -> x^5 on F_p^*: needs factoring f-1 for the 69-bit and 143-bit primes dividing p-1 (p-1 itself is now known).
- Is the primitivity of M an accident (random chance ~ phi(n)/n, not computed) or selection? Same question for the other matrices of the Grain-generation family if any are available as data.
- Why do the 9 conics (minors) not give any simple relation with the Cauchy parameters? (Null result: worth a second look with a CAS.)
- The Frobenius twist: M^p is similar to M (conjugate eigenvalues), and is MDS here; is the whole hash symmetric under a field-automorphism-like action? Not tested.

## Boring details kept
- All 192 round constants are unrelated to the Cauchy quantities (section 4). The gauge x0=0 makes x0+y_j = y_j and x_i = x_i-x_0 trivially (the only "small ratio" hits).
- v3(p-1) = v3(p^2+p+1) = 1, so 9 | n exactly.
- pip installed sympy, gmpy2, python-flint into the system Python for this task.
- Heavy runs: one at a time; 626 s flint factoring (C''), 60 s random-Cauchy statistics, 12 s for 200000 powers.
