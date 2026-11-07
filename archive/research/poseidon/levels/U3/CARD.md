# CARD U3 - Partial rounds (R4, and R5 for r=2)

Learner U3, 2026-10-12. Learning card, no attack scores. Folder `./research/poseidon/levels/U3`.
Labels: OBSERVED (measured; script + output file named), PROVED, DERIVED, GUESS.
Scripts (each single process, exact big ints or numpy int64):
`u3_real.py` -> `u3_real_output.txt` (10 s); `u3_sparse.py` -> `u3_sparse_output.txt`; `u3_toy.py` -> `u3_toy_output.txt` (145 s); `u3_toy_check.py` -> `u3_toy_check_output.txt`.
Real field: Pallas p, `poseidon_ref.py`, seeds fixed in the scripts. Toys: random MDS (all 9 entries and all 9 2x2 minors nonzero, det != 0) and random constants over F_q; gcd(5,q-1)=1 OBSERVED for q = 17, 23, 37, 97, 193, 257, 449, 769, 1009, 12289 and 1,000,003 (q-1 = 2 * 500001; 2-adicity 1). High 2-adicity: 257 (8), 769 (8), 12289 (12); low: 1009 (4), 1,000,003 (1).

## Card: what a partial round is

| field | content |
|---|---|
| reads | all 3 lanes (C adds 3 constants; M reads all 3) |
| S step | x^5 on lane 0 only; lanes 1,2 untouched |
| writes | all 3 lanes (dense M) |
| linear? | affine in (w, s1, s2) where w = (s0 + c0)^5 is the only non-linear scalar |
| condition that removes the non-linearity | S-box input equal in both states of a pair (equal lane 0 after C) |
| freedom | 2 free dims for a difference entering R4 (d0 = 0); 1 free dim through R4 and R5 (d on the trail line); 0 through three partial rounds |
| what moves when it changes | lane 0 value moves w non-linearly; a change in lanes 1,2 moves the output by M(0,d1,d2), nothing else |

## 1. X5 exact (question 1)

- OBSERVED `u3_real.py` Q1: state after R4 = M*(w, s1+c41, s2+c42), w = (s0+c40)^5: **0 mismatches on 1000 random inputs** (state after R3 of random (nk,rho)).
- OBSERVED: carried-constant version (drop lane 1,2 constants of R4, add M(0,c41,c42) after M): 0 mismatches / 1000.
- OBSERVED: full hash through the carried-constants pipeline (lane-0 constant kept, lanes 1,2 constants carried forward through M into the next round's constant vector): r=1 and r=2, **0 mismatches / 1000 each**.

## 2. Difference spaces on the real field (question 2)

- OBSERVED: r=1, 200 hand-built pairs (s, s+(0,d1,d2)) with random s in F^3 (not from the hash) through R4: output difference == M(0,d1,d2) in 200/200 (0 mismatches).
- OBSERVED: r=2 trail vector (0, M02, -M01) = (0, 0x7c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d, 0xe6e99d71a75a544d6c0f0f2779386abfe394e7f49d9a1e50a62db56166954a3). 200 hand-built pairs with difference t*trail: lane 0 equal after R4, the R5 S-box input equal (w equal), difference after R5 = M(0,e1,e2) with e = lanes 1,2 of M*d: 0 failures / 200.
- OBSERVED: M*d = (0, 0x1b1c7e8f4e01c987011af7a328c3aeb466d5b810b3849e30c251c22a2773a5fc, 0x14e50e88550bc9c3846eb9c41c765ed1462766c0d778b7d677b1f997ee84d578) (lane 0 is 0). Difference after R5 for unit t = M^2 d = (0x3141e9b5..5747, 0x1978ec47..120e, 0x167d4c4f..389f); its lane 0 is nonzero, so the trail pair is visible in lane 0 after R5 (this is the output of the partial block).
- OBSERVED negative controls: generic d with d0=0 (not on the line): lane 0 equal after R4 in 0/200 (as it should: lane-0 diff = M01 d1 + M02 d2 != 0); random d: 0/200.
- DERIVED (follows from X5): with equal S-box inputs the pair difference passes through linearly and independent of the base state s. The 200 base states differ; so the difference is a property of the pair difference, not of the position. (If an S-box input differs, the output difference depends on s.)

## 3. Pairs with equal lane 0 after R3 (question 3)

Real field:
- OBSERVED (finite differences on lines, 2 random lines): lane 0 after R3 has (nk,rho)-line degree exactly 625 (Delta^625 != 0, Delta^626 = Delta^627 = 0); lane 1 after R3 also 625; lane 0 after R4 exactly 3125 (2 lines); lane 0 after R5 exactly 15625 (1 line); in (A,B) coordinates lane 0 after R3 is exactly 125 on a line. (`u3_real_output.txt` Q3.)
- DERIVED: the pair set {(P,Q): f(P)=f(Q)}, f = lane 0 after R3, is a hypersurface (dimension 3) in F^4 of (nk,rho)-degree 625 in each point; it contains the diagonal P=Q (dimension 2) as a trivial component. For a fixed P the partner set is the level curve {f = f(P)} of degree 625 (125 in (A,B) coordinates), a curve through P. Total pairs: about p^3/2 unordered, so the "equal lane 0 after R3" pairs are as many as the pairs of a random function F^2 -> F.
- GUESS: the level curve is irreducible and smooth at a generic P (not tested; the degree-625 curve was not decomposed).

Toy (exhaustive over all q^2 inputs, `u3_toy_output.txt`): unordered pairs with equal lane 0 after R3 divided by q^2(q^2-1)/(2q):
- q=257 seeds 1,2,3: 1.0001, 0.9996, 0.9994 (counts 8487647, 8483685, 8482459 vs 8487168); q=769: 1.0000; q=1009: 1.0000. Fibre var/mean 0.85 - 1.2 (Poisson = 1), min/max about q -/+ 50 (257), 880..1160 (1009).
- OBSERVED for comparison, same quantity after each round: **after R0 every fibre has exactly q points** (min = max = q, var 0), pair ratio q/(q+1) (0.9961 at 257, 0.9987 at 769, 0.9990 at 1009; this is the exact value: lane 0 after R0 is a nonconstant linear form in (A,B) and (A,B) is a bijection). After R1 the fibres are already wide (var/mean 0.77 - 1.17) with ratio within 0.001 of 1; R2, R3, R4, R5: all within 0.0007 of 1. So "random-function" statistics are reached by R1; nothing in the lane 0 pair count sees the partial rounds.

## 4. r=3 and the largest r with a trail (question 4)

- OBSERVED (real field): rank of [e0; e0 M; ... ; e0 M^(r-1)] = 1, 2, 3, 3, 3 for r = 1..5, so the surviving trail direction dimension is 2, 1, 0, 0, 0; det[e0;e0M;e0M^2] = 0xebe164ab9dff92f6f90c296e3b831a7221b9f7429d21e01d7dc2ebf46e8a8ba (nonzero). **Largest r with a trail direction is r = 2.**
- PROVED: for a pair with equal S-box input in every partial round the differences propagate linearly (d_{k+1} = M d_k with lane 0 of d_k forced to 0 at the next S-box), so the pairs with all r S-box inputs equal are exactly the pairs whose difference d satisfies e0 M^k d = 0, k=0..r-1, i.e. d in the kernel of the observability matrix, dimension 3-r (r<=3) when lane 0 is a cyclic vector.
- OBSERVED exhaustive toy (`trail_survival`, all q^3 states): pairs of distinct states with equal lane-0 S-box input in all r partial rounds = n(q^(3-r)-1)/2 exactly: q=17: 707472, 39304, 0, 0; q=23 (seed 2): 3212088, 133837, 0, 0; q=37: 34646652, 911754, 0, 0 for r = 1,2,3,4 (matches formula in every cell).
- **OBSERVED boring detail: MDS does not imply the trail dies at r=3.** Toy q=23 seed 1 is a valid MDS (all minors nonzero) but det[e0;e0M;e0M^2] = 0 mod 23 (`u3_toy_check_output.txt`); its exhaustive count is 133837 pairs for r=2, 3 and 4, i.e. a 1-dim trail that **persists for every r**. The real M has det = 0xeb..a ba != 0, which is a separate fact to verify for any matrix (M^k MDS for k<=8 does not say it).
- OBSERVED toy (lane-0 values themselves, after-M lane 0): number of unordered input pairs whose R3 states have equal lane 0 after R3, R4, R5 simultaneously: **exactly 0 for all q and seeds** (257 x3 seeds, 769, 1009), where a random function would give N3/q^2 = 128 (257), 384 (769), 504 (1009). After R3 and R4 only: 33025 / 33269 / 32679 (q=257, 3 seeds), 296271 (769), 508104 (1009) = N3/q within 1%. This is the r-dependent structural quantity (question 7).
- OBSERVED toy: the pairs of R3 states whose difference is a multiple of the trail vector (0,M02,-M01): counted with a sorted-key lookup for q = 97, 193, 257, 449 (3 seeds each). Their number equals **exactly** the number of input pairs with equal lane 0 after both R3 and R4 (e.g. q=257 seed 1: 33025 = 33025; seed 2: 33269; seed 3: 32679), and **none** of them keeps lane 0 equal after R5 (0 in every row). They are close to the random expectation n^2(q-1)/(2q^3) (ratio 0.98 - 1.01).

## 5. Sparse equivalent partial rounds (question 5)

- PROVED: lane-0-fixing matrices Q = diag(1, A) commute with the partial S-layer (S acts only on lane 0): M S0(z) = (M Q) S0(Q^-1 z). Choose Q so that M Q has identity as its lower-right 2x2 block: A = Mhat^-1 with Mhat = M[1:,1:]. Exists iff Mhat is invertible, which is an MDS 2x2 minor (OBSERVED det Mhat = 0x34f8311e..507e8d != 0). Then M Q = [[m00, v^T Mhat^-1],[w, I]], v = M[0,1:], w = M[1:,0].
- Chain for r rounds: round k uses Q_k = diag(1, Mhat^-(r-k+1)), Q_(r+1) = I; round-k matrix M_k = Q_(k+1)^-1 M Q_k = [[m00, v^T A_k],[A_(k+1)^-1 w, I]]; constants hat c_k = (c_k0, A_k^-1 (c_k1,c_k2)); front factor Q_1^-1 absorbed into R3's dense M (still dense, same cost); the last sparse matrix goes straight into R60's constant addition (no extra matrix).
- OBSERVED `u3_sparse.py`: the sparse block equals the original block on 300 random states after R3 for **r = 1, 2, 3, 4** (0 mismatches), and the whole hash through the sparse block matches on 100 inputs for each r (0 mismatches). Also M == diag(1,Mhat) * [[m00,v],[Mhat^-1 w, I]] verified (the M = M'M'' form of the question).
- OBSERVED: sparse entries are generic: no entry in {0,1,-1}, col0 != col1, row0 != row1, col1/col0 = 0xb151ef40..3273 (last round) / 0xa6363bdb..621 (round 1 of r=2). The last round's sparse matrix is the same for r=1 and for round 2 of r=2 (A_(r+1)=I): column = w = M[1:,0], row = v Mhat^-1. m00 = M00 unchanged.
- Multiplication count (DERIVED; exclude constant additions): original partial round 3 (S-box) + 9 (dense M) = 12 field multiplications; sparse 3 + (3 for lane 0 + 2 for lanes 1,2) = 8. **Saved 4 per partial round: r=1 saves 4 (12 -> 8), r=2 saves 8 (24 -> 16).** Lane-1,2 constants of all partial rounds can be pushed forward to R60's constant vector (additions only; DERIVED, the pushing by the sparse matrix was not run, the unsparsed version was run in section 1).
- OBSERVED dull facts: w is not an eigenvector of Mhat (collinear(w, Mhat w) false); Mhat has eigenvalues in F_p (trace^2-4det is a square).

## 6. Effective carried constants (question 6)

- OBSERVED `u3_real_output.txt` Q6. r=1: R60 effective constants = c60 + M(0,c41,c42) = (0x2b6546a2..6811, 0xa57eba6..968f9, 0x965901..0161): equals the atlas value; bits 254, 252, 252; none is 0, +-1; lane 0 non-residue, lane 1 non-residue, lane 2 non-residue.
- r=2: **lane 0 of R5 gets the extra M01 c41 + M02 c42 = 0xbfbc9f62..f663** (this is the lane-0 entry of M(0,c41,c42)); R5 effective lane-0 constant 0x39dce27cdb109e337d6bac3c569fcf95265c4c444535cce6bbdc7a7b456637ee (254 bits, original 0x2de11886..418b). R60 effective (all three lanes changed): (0x316d25f0..4d0e, 0x2c284cc1..4c83, 0x36c5e753..6831), carry into R60 = (0x1203a943..db60, 0x5add7b21..d5a, 0x2a33e8a8..f8cc). Lane 1 effective is a quadratic residue, lanes 0,2 are not. Nothing special (no zero, +-1, small, equal to an original lane-0 constant).
- DERIVED: in r=1 the carried M(0,c41,c42) enters **R60 on all three lanes** (lane 0 included); in r=2 R4's carry enters lanes of R5 (lane 0 shifts the R5 S-box input; lanes 1,2 pass through) and R5's total carry (its own lanes 1,2 constants plus R4's carry through M) enters R60 on all three lanes. The lane-0 constants of R4/R5 stay at the S-box and are never moved.

## 7. Toy quantity that depends on r (question 7)

- OBSERVED: the fibre statistics of the output do not depend on r at any visible level: pairs equal at R3 lane 0 and equal output lane 0 divided by N3/q for r = 0..5: 0.997, 0.999, 0.999, 1.005, 0.989, 0.995 (q=257 seed 1); 0.994 ... 1.007, and 0.985 ... 1.008 for seeds 2, 3 (spread about +-1%, std of a count of 33000 is about 0.55%); q=769: 0.997 .. 1.004; q=1009: 0.998 .. 1.003. All output-equal pairs ratio 0.9995 - 1.0006 for every r. **Null result: the counts of the output collisions do not know r.**
- What does depend on r is the stacked lane-0 equality of section 4 (PROVED + OBSERVED): equal lane 0 after R3, R4, ..., R(3+k): counts ~ q^3/2, ~q^2/2, **0**, 0 for k = 0, 1, 2, 3, so the first impossible depth is k=2 (needs the S-box inputs of R4 and R5 equal and the lane 0 after R5 equal too, i.e. 3 conditions on a 2-dim difference space).
- GUESS: collisions of the final output are not sensitive to the trail count because the trail pairs are only about q^2/2 of the q^3/2 R3-equal pairs and their later behaviour (output equal for 139/116/137/130 pairs against 128.5 random at q=257) is not distinguishable; a distinguishing statistic would need q larger than the exhaustive range.

## 8. Minimal arithmetic for lanes 1,2 (question 8)

- DERIVED (from the sparse form): lane i (i=1,2) of the new state = old lane i + w_i * x0 where x0 = S-box output; that is **1 multiplication and 1 addition per lane** (2 mults total), against 3 mults per lane in the dense M. The nonlinear scalar x0 is the only product that must be formed besides the lane-0 row.
- DERIVED: lane 0 new = m00 x0 + v'^T (old lanes 1,2) costs 3 mults. These 5 are what a general (non-special) M needs. No entry of the sparse matrices is 0, 1 or equal to another (OBSERVED, section 5), so no further saving is visible from the values.
- GUESS: 5 per partial round is a lower bound for a generic M in this form because the lane-1,2 update vector w has two independent entries and the lane-0 row has three; a different basis (non-I lower block) was not explored.
- Lanes 1,2 are never inputs to an S-box inside the partial block, so they are only read at the end of the block (by R60.S) and by lane 0's row.

## Five most surprising or useful observations

1. Equal lane 0 after R3, R4 and R5 simultaneously never happens (count exactly 0 for every toy and seed; random would give 128 to 504); equal after R3 and R4 is as common as chance (N3/q). The partial rounds create an exact zero, not a bias. PROVED by the observability argument and OBSERVED exhaustively.
2. The r=2 trail pairs are in exact bijection with the pairs with equal lane 0 after R3 and R4 (33025 = 33025 etc.), the difference passes through R4 and R5 with the proven formulas on the real field, but they are not special at the output (collision counts equal the random rate).
3. Largest r with a surviving trail direction is 2 on the real M; but MDS alone does not guarantee that: a valid MDS toy matrix (q=23 seed 1) has det[e0;e0M;e0M^2] = 0 and keeps a 1-dim trail for every r. The real matrix passes only because det = 0xebe164ab...86ba != 0.
4. The sparse equivalent block exists for every r tested (1..4) and verifies on 300 states and the full hash; it saves exactly 4 multiplications per partial round (r=1: 12 -> 8; r=2: 24 -> 16), and the front factor is absorbed into R3's dense M at no cost. The last sparse matrix has column w = M[1:,0] and row v Mhat^-1, identical for r=1 and r=2.
5. After R0 every output fibre has exactly q points (var 0), and from R1 on the lane-0 pair statistics are already within 0.1% of a random function; the partial rounds change nothing in this statistic. Degrees along lines are exact: 625 (R3), 3125 (R4), 15625 (R5).

## Questions raised

- Is the persistent trail of an MDS matrix with det[e0;e0M;e0M^2]=0 the reason the real parameters check this? Does the organizer's M family have a general proof that det != 0, or is it just luck for this M (the toy rate: 1 of 6 random MDS toys had it zero, about 1/q expected)?
- The R3-equal pairs with difference on the r=2 trail line form a set of about q^2/2 in a toy; on the real field what is the structure (number of points) of the curve in (nk,rho) pairs where lane 0 after R3 AND after R4 agree? It is a dimension-2 subset of the 4-dim pair space; its degree and whether it is irreducible were not computed.
- Does the one-dimensional trail difference after R5 (fixed direction M^2 d) give any information to the R60-R63 tail (a pair difference of known direction but unknown scale t)? Not tested on the real field; toys show only the random collision rate.
- Can the lane 1,2 updates of consecutive partial rounds be merged (w1 and w2 are not collinear in this M, so no) - is there a non-identity lower block giving fewer than 5 mults per round?
- What is the relation of the trail vector (0, M02, -M01) to the plane P0 of R0 (X3 says it is not in P0's difference space) and to the degree-drop directions (X10)? Not computed here.
- Pushing the lane 1,2 constants through the sparse matrices to the end of the block (additions only) was not executed on the real field (only DERIVED).
