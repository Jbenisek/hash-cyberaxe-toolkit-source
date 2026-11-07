# CARD U1 - Input and round 0 (init, R0.C, R0.S, R0.M)

Written 2026-10-12 by learner U1. Learning only: no attack scores anywhere. Folder: `./research/poseidon/levels/U1`.
Labels: OBSERVED (measured; command and output file named), PROVED, DERIVED, GUESS. Empty squares and null results are recorded on purpose.

Reproduce:
- real field: `python u1_real.py > u1_real_output.txt` (3 s; imports `orchard\impl\poseidon_ref.py`, constants as data). Section names `Q1..Q8` below refer to its output.
- toys: `python u1_toy.py > u1_toy_output.txt` (1006 s, one process; sections `T1..T7`).
Toy copies: F_q, q in {257, 769, 1009, 4099, 12289} (exhaustive where stated; 65537 and 1000003 sampled), all have gcd(5,q-1)=1 (checked, output `TOY SETUP`; 1000003: q-1 = 2*3*166667, prime, OK). 2-adicity 8, 8, 4, 1, 12, 16, 1. Random constants, random all-minors-nonzero MDS (and Cauchy MDS for part of T4), seeds recorded in the script; init [nk, rho, 2^65 mod q]; rounds {0-3 full, r partial, 60-63 full}.

## The card

| field | content |
|---|---|
| reads | init lanes (nk, rho, 2^65); round-0 constants c0,0 c0,1 c0,2; MDS M (all 9 entries) |
| writes | state after R0.M = M*(A, B, K)^T with A=(nk+c00)^5, B=(rho+c01)^5, K=(2^65+c02)^5 |
| conditions | none (every canonical nk, rho < p is admitted; no S-box input is excluded) |
| freedom | 2 free scalars (nk, rho) <-> (A, B) free over all of F^2; lane 2 is a constant |
| what moves when it changes | nk moves the state along M column 0 (through A only), rho along column 1 (through B only); the capacity entry moves the whole plane along column 2 |
| linear steps | C (translation), M. Non-linear: S on lanes 0,1 only (lane 2 acts on a constant) |

## 1. X2 bijection and H(A,B) = hash (question 1)

- OBSERVED real (Q1): 1000 random + 144 edge pairs (edge values 0, 1, -1, 2, i, -i, -c00, -c01, 1-c00, 1-c01, 2^65, p-2 in both slots) = 1144 inputs x r in {1,2} = 2288 hash checks: failures **0**. State after R0 equals M*(A,B,K) on 1144/1144; n.s = K on 1144/1144; fifth-root inversion x -> x^d returns (nk,rho) on 1144/1144.
- OBSERVED toy exhaustive (T1): q=257 (4 seeds), 769 (3), 1009 (3), 4099 (1 seed), r=1,2: bijectivity of x -> (x+c)^5 on both axes True in all 22 runs; mismatches between the hash and H(A,B) over every one of the q^2 inputs (66049 / 591361 / 1018081 / 16801801): **0 everywhere**. Sampled 2000 inputs x r=1,2 at q = 12289, 65537, 1000003: 0 mismatches.
- OBSERVED (T1, q=257, r=1,2): the 66049 full 3-lane outputs are all distinct (X1 reconfirmed).
- OBSERVED control (T7): with gcd(5,q-1)=5 (q = 11, 31, 41, 61) the image of x -> (x+c)^5 has exactly (q-1)/5+1 elements (3, 7, 9, 13), i.e. the reparametrisation is 5-to-1 away from 0 and X2/X1 fail. So the exponent condition is the whole reason X2 is a bijection. PROVED (the image size is the number of 5th powers).

## 2. The plane P0 (question 2)

OBSERVED (Q2), all numbers full:
- Normal n = row 2 of M^-1:
  - n0 = `0x2fcbba6f9159a219723a63a0c09dab26aef9112e952fdbb52a418d8d73a7c908`
  - n1 = `0x1ec7372574f3851bb4ddd4b4d6452256c5e4960d7424cd3776efab42d4fba90b`
  - n2 = `0xd0c2efd6472f12a3c26fa4b7d25b1e487a7435d30f8be81adc8933c6f3c72ee`
- K = `0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c` (= (2^65+c02)^5, with 2^65+c02 = `0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5f0939d92753cc5dc8`).
- Plane: n0*s0 + n1*s1 + n2*s2 = K. Normalised by n2: s2 = K/n2 - (n0/n2) s0 - (n1/n2) s1 with n0/n2 = `0x84b41798e620e02bc044194036247e5a3f64f561040e9d1e5052189cb2073f7`, n1/n2 = `0x2edf5971df68705154f74403de8f795aaf953c8966aa2a173b3fd87a3853002a`, K/n2 = `0xe6582dfa3c4e7b00d4f42c72a98d9f40810029fc8033ec938a901cebd4a5636`.
- Axis directions: M column 0 (A, i.e. nk) = (`0xab5e5b87...7e11b63`, `0x23316263...d085167c`, `0x2e29dd59...4f84dbe4`), M column 1 (B, i.e. rho) = (`0x31916628...e996ab5e`, `0x25cae259...3e047a2e`, `0x1d1aab4e...43263664`) (full hex in `u1_real_output.txt`). Column 2 (capacity) = (`0x7c045d5f...8e8345d`, `0x22f5b5e1...685f747a`, `0x3bf76308...6e85ef1`). Check n.M_.,j = (0, 0, 1) - PROVED (n is row 2 of M^-1) and OBSERVED.
- Base point (A,B)=(0,0): K*M_.,2 = (`0x1b43dc42131ed88a30b46da8b2a67905376626dc27e7b05ae1d27389256d3372`, `0x11b8fa8315c3ab32de9c6eae34fa3b85493ac16f694bb975ed47d41d25a96e42`, `0x3f5f4a93cc7cf2c95141c69485ed312211872e35264ed14e2b961c182800aae3`); this is the state at nk=-c00, rho=-c01.
- Does K depend on 2^65 in any other way? PROVED: the capacity entry and c02 enter only as the sum cap+c02 (inside lane 2, nothing else touches lane 2 before the S-box). OBSERVED toy (T2): the function with (cap+d, c02-d) equals the function with (cap, c02) pointwise on all q^2 inputs, 18 of 18 runs.

Capacity variants (OBSERVED, Q2; n.s = K checked on a test point for each): cap = 0: K = `0x9c7f277036bd7911c4f72ff3c564ea06bb717782cd836bfa811817410e17c3d`; cap = 1: K = `0x31bb8d1dad3598351e34288dac458b96978f2e1db820fd34ad59e80fe3ce5097`; cap = -1: K = `0xd57edf66fd260a13dea040990e69b5a5d87ff50ea23ec5ea69fd2455c7a54e`. "Fixed point" version: choosing cap with cap+c02 in {0, 1, -1, i, -i} gives K = that same value (S-box is the identity on lane 2); the cap values are (hex in output): `0x2af36c01...33a239` (K=0), `...33a23a` (K=1), `...33a238` (K=-1), `0x21b1387c...5015913` (K=i), `0x34359f85...365eb5f` (K=-i). Also the special capacity cap* = `0x2f18e3619011f341bbaffc389afdb4d64e7829a8c52189d869d4c65eefdb9d4e` (254 bits) is the one for which P0 contains the point s = -c1 (all three R1.S inputs zero); n.(-c1) - K = `0x26d17073e4d19f59dec3c37bdb12fc30afde85b105bd61f3a184c94ae820d8d2` != 0 for the real capacity.
What changes with the capacity: PROVED only the offset K; n and both axes stay; the planes for different K are parallel translates by (K'-K)*M_.,2. With K=0 the plane is a linear subspace through the origin and (nk,rho)=(-c00,-c01) sends the state to 0, so R1 sees exactly c1.
OBSERVED toy (T3, null result): scanning ALL K in F_257 (3 seeds, r=1,2) the collision-pair ratio against a random function ranges over 0.9988-1.0014 (mean 1.0000), variance/mean 0.70-1.35, image covers all 257 outputs for every K; the special K (0, 1, -1, i, -i) are not outliers (ratio 0.9993-1.0007). At q=769 (16 K values incl. the special ones, 2 seeds): ratio 0.9999-1.0001. No K, including K=0, shows anything at fibre-statistics level. (Statistics of the fibre counts only; structure beyond that is not tested.)

## 3. Do c00, c01 matter? (question 3)

- OBSERVED toy (T2): q = 257, 769, 1009 x 3 seeds x r = 1,2 (18 runs), changing both c00,c01 (and c00 alone): the complete per-output fibre-size array (count of inputs per output value, all q entries, not just the multiset) is **identical** in 18/18, and H'(nk,rho) = H(nk+d0, rho+d1) pointwise in 18/18. PROVED: (nk+c00)^5 is a re-labelling of the input domain. Controls: changing c02 changes the arrays (and even the sorted multiset) in 18/18; changing c1,0 changes the arrays in 18/18. So the null result is meaningful: the test can see changes.
- Consequence DERIVED: c00, c01 matter for the labels of the input (which nk, rho produce which state) and for nothing else; every statement about fibres, collisions and surface shape can be made in (A,B).

## 4. S-box special inputs (question 4)

OBSERVED (Q4), values mod p (all canonical, all < p; no wrap needed):

| a = S-box input | nk = a - c00 | rho = a - c01 | capacity value cap = a - c02 |
|---|---|---|---|
| 0 | `0x9f28b8f9ee1b8c2cac09d70892eef0cd3d582ccd84cbdab41d9a4c769bd9cfe` | `0x14546b2851ddd2eca23c393a014055ced93decccf66118abdb75eed9409ce776` | `0x2af36c0109ad04e3d40fc1e5d65578e032ceb124d2d68cbe8ff357c5ac33a239` |
| 1 | `...bd9cff` (nk(0)+1) | `...9ce777` | `...33a23a` |
| -1 | `...bd9cfd` | `...9ce775` | `...33a238` |
| i | `0xb0580aae0a6ea1fc34ed27ac5571aab1270a0b14f8b08088f46863028b53d8` | `0xb1237a3610688cbd3b088f12466d86cb68f740b330d0b812290b274d96a9e50` | `0x21b1387c18d5bac30584119cf97bfb7e102038630f827f93d70e1b6145015913` |
| -i | `0x1334bf148fb902e3994c4db966086c6ef683fb8e9ba0cad5fabee12bd0efe624` | `0x1d969ead42b51d0d70c7e982de19d330fbec658eb9b525d6945b2b3da7cf309c` | `0x34359f85fa844f04a29b722eb32ef642557d29e6962a99e948d8942a1365eb5f` |

(i = `0x36bdcc7b0f28b5df31744fb72326829dff98203a45f8ebf0e047f48898cdb6db`; its square is p-1, checked.) Boring facts: none of these values is small or "nice" (all are 252-254 bit numbers except the +-1 neighbours of -c00 which differ by 1); the real lane-2 input 2^65+c02 is none of 0, +-1, +-i (False); so the capacity lane never hits the identity/zero case. At a=0 the derivative is 0 (first-order dead point); the a=0 and b=0 sets are the lines nk=-c00 and rho=-c01 (see 7).

## 5. Degree-drop directions (question 5)

- OBSERVED toy (T4): for each of 35 configurations (q in {257, 769, 1009, 4099, 12289}, 5 seeds random MDS + 2 seeds Cauchy MDS at the first two seeds of each q), ALL q+1 directions (u:v) were tested (degree in t of each lane after R0.M on the line (a+ut, b+vt) from a random base point, exact finite differences): **exactly one direction per lane loses its top degree (5 -> 4), never two lanes in the same direction, and it equals u/v = (-M_i1/M_i0)^(1/5)** in 35/35 configs including q = 4099 (q = 3 mod 4) and Cauchy matrices. On each drop line the degrees after R1.M are [25,25,25] in all 105 drop lines (the drop is gone after one MDS).
- OBSERVED real (Q5): the three directions u/v (v=1): lane 0 `0x171bfeac856e5e7dcee70afd00e457a3e654cb49c74d822788485012522646e1`, lane 1 `0x38eb3b938273ed52c9a30bef357f3dc8b1c42b81580876f06e069ab16e5e48bc`, lane 2 `0x25ad56736388155dcf81c8af6f02c6b5dd04aacd07adf82444e076c8b371a940`; M_i0 u^5 + M_i1 = 0 exactly; distinct. Exact line degrees (finite differences over F_p): generic line [5,5,5] [25,25,25] [125,125,125] [625,625,625] after R0..R3 .M; lane-i drop line: lane i has degree **4** after R0.M and [25,25,25], [125,125,125], [625,625,625] afterwards; pure nk and pure rho directions show no drop.
- OBSERVED control (T4): with gcd(5,q-1)=5 (q = 11,31,41,61,71,101, 3 seeds) the number of drop directions per lane is 0 or 5 (counts seen: 0 and 5 only). PROVED: number of 5th roots of -M_i1/M_i0.
- Why exactly one: PROVED (bijection of x^5 on F_p gives one solution).

## 6. Inverse S-box x^(1/5) = x^d (question 6)

- OBSERVED (Q6): d = `0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd`, 254 bits, **Hamming weight 125** (almost exactly half; no sparsity). 100 random x: (x^d)^5 = x and (x^5)^d = x both 100/100.
- Structure noticed: the top 126 bits are the nibble pattern 0x33..3 = (2^128-1)/5 (PROVED: 5d = 1 mod (p-1) and p-1 has the factor 2^32; checked `hi == (2^128-1)//5` True). So x^hi can be built by doubling the repeating 0011 pattern.
- Costs (OBSERVED, counted by executing the chain and comparing to pow()):
  - plain binary: 253 squarings + 124 multiplications = 377;
  - sliding window k=2..7: totals 322, 318, 316, **306 (k=5)**, 312, 344;
  - structured chain (nibble-pattern doubling for the top half: 125 squarings + 6 mults, then window k on the low 128 bits): totals 320, 297, 293, **291 (k=4: 253 squarings + 38 multiplications)**, 295, 307; all verified against pow().
  - Squarings 253 are forced for a chain on a 254-bit exponent (GUESS: a true shortest addition chain would not go much below ~290; none searched). Forward S-box x^5 = 3 multiplications, so backward/forward is about 97:1 in multiplications (291/3). Python timing pow(x,d,p)/pow(x,5,p) is only 31 (call overhead), not a field-multiplication ratio.
- Empty square: a search for a genuinely shorter addition chain (e.g. via Bos-Coster / continued-fraction chains) was not run.

## 7. The 25 fixed-point pairs (question 7)

OBSERVED (Q7): for a, b in {0, 1, -1, i, -i} (nk = a - c00, rho = b - c01); here A=a, B=b so the state is M(a, b, K).
- Nothing looks special in size: lane bit lengths 245-254 (min 245), none small; no lane of M(a,b,K) is itself in {0,+-1,+-i} (0 of 75) and no R1.C input lane is (0 of 75); no lane value repeats among the 25 states (0 repeats); the 25 hash outputs are distinct for r=1 and r=2.
- They form a 5x5 grid inside P0 (affine image of the grid {0,+-1,+-i}^2 in (A,B)): **172 collinear triples of 2300** (100 axis-parallel, 72 diagonal-type), PROVED to be a consequence of the grid, nothing about the hash.
- What IS special is the Jacobian (OBSERVED, forward-mode tangent through the real rounds, r=1 and r=2 identical): the rank of d(state)/d(nk,rho) is **0 at (a,b)=(0,0)**, **1 at the 8 other pairs with a=0 or b=0**, and 2 at the other 16 pairs. The rank never recovers in later rounds (rank 0 stays 0, rank 1 stays 1 at every level up to the final state; listed per pair in output; DERIVED: later steps multiply the tangent by invertible diagonal * M while no S-box input is 0). The gradient of the output w.r.t. (nk,rho) is exactly zero at (0,0) for r=1 and r=2 and nonzero elsewhere on the 25.
- So the hash map has critical points: the lines nk=-c00 and rho=-c01 (rank 1, the whole map there is an image of a 1-parameter family) and the point (-c00,-c01) (rank 0) - all of these are the places where the S-box derivative 5a^4 vanishes. DERIVED. In (A,B) coordinates there is nothing critical (x -> x^5 is the only source).
- Toy (T6, q=257, 3 seeds): lanes in the fixed set 0, 1, 3 of 75 (random expectation 1.5); repeated lane values among the 25 states 0, 12, 0 (seed 1 has a small-field coincidence, the real field has 0); hash collisions among the 25: 4, 1, 0 (random expectation ~1.2). Null result: no toy shows systematic structure.

## 8. Two zero lanes at R1.C on the plane (question 8)

- PROVED: the condition lane_i(R1.C input) = 0 and lane_j = 0 are two LINEAR equations in (A,B) (the R0 output is affine in (A,B)); because all 2x2 minors of M are nonzero they have a unique solution. So there is exactly one such point per lane pair, three in all (pairs 01, 02, 12). In (nk,rho) each condition is the quintic curve M_i0 a^5 + M_i1 b^5 = const; two quintics meet in 25 points over the algebraic closure, exactly 1 is F_p-rational (Phi_5 irreducible gives one 5th root). DERIVED. All three lanes zero would need n.(-c1) = K; difference nonzero, so impossible with the real capacity (OBSERVED).
- OBSERVED toy (T5, exhaustive, q = 257, 769, 1009 x 3 seeds): each lane's zero locus has exactly q points; (A,B) with exactly two zero lanes: **3** in 9/9 runs (never other); three zero lanes: 0 in 9/9; exactly one zero lane: 765/2301/3021 (= 3q minus the overlaps).
- OBSERVED real (Q8): the three points (A, B; nk; rho; full hex in output):
  - lanes (0,1): nk = `0x22fdda23a1ed8ba205a9acbf2953e1eb648ecb0244e5ac6a2ad0445785d8555d`, rho = `0x86ec112fcea07a0fb8fc8d82c6a716630d9a4f9a0b964decf428cd33aae1069`; R1.C input (0, 0, `0x9b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210`).
  - lanes (0,2): nk = `0x30333438102d881c76f5f60f9a752b12d2897a481f5f580e1446c04e42158ba4`, rho = `0x1891445539491447d56d610627875c0dd01f4d7b48fd5846939ece3aa7aab781`; R1.C input (0, `0x56ca88352495e3b531f6639906f2a46f1123cf5ea8ca2ead4467a8cc69282fa`, 0).
  - lanes (1,2): nk = `0x151d98c790e33dad04edaef22c236ffda4e05e6376b519ed16f06c4fe5e9c17b`, rho = `0x42a0778c4db041191ca688588f82884e352d600cea1ee778898ba0e8d00c97b`; R1.C input (`0x2a78890d8503b228bfa6bd9b312401c7af4e02a6376ceebb003ef1138f67c72c`, 0, 0).
  Each was re-verified by running the real round 0 on the (nk,rho): both lanes are exactly 0.
- OBSERVED (surprise): at each of these three points the Jacobian of the state w.r.t. (nk,rho) has rank 2 after R0.M but **rank 1 from R1.M to the very end**, for r=1 and r=2 (listed per round). So they are persistent critical points of the whole map (two S-box derivatives vanish at once, the tangent plane collapses onto one M column, and later rounds never re-expand it). The output gradient is nonzero there (rank 1 of the 1x2). Hash values are in the output file.

## 9. Everything else recorded (boring details)

- 2 free scalars and lane-2 constant => the init set is the plane {s2 = 2^65}; round 0 moves it to P0 and makes it exactly the set {n.s = K} (every point of the plane is reached, X2).
- Real capacity 2^65 is a 66-bit number, tiny compared with the 253-bit lane-2 input 2^65+c02 because c02 is a big constant; the S-box does not see "small" capacity.
- Toy exhaustive sizes: 66049, 591361, 1018081, 16801801 inputs; the q=4099 run took most of the 1006 s.
- Not done: no factoring/structure of the constants (U6); no non-Cauchy vs Cauchy fibre comparison beyond T4; the degree-drop test used the degree in t on lines only, not the full 2-variable surface; no cusp-type classification of the three critical points of section 8; no search for shorter inverse chains; toy copies were not run at 2-adicity 32.

## 10. The 5 most surprising / useful observations

1. **Persistent critical points.** The rank drop of the Jacobian at S-box zeros never heals: (a,b)=(0,0) has rank 0 and zero output gradient; the lines nk=-c00 and rho=-c01 have rank 1; and the three F_p points where two R1.C lanes vanish simultaneously (one per lane pair, 1 of 25 geometric intersections) have rank 1 from R1 to the output for r=1 and r=2. Unlike the degree-drop directions (transient, gone after one MDS) these are permanent features of the map.
2. **Round 0 is exactly an input relabelling plus one number.** X2 holds with 0 failures on 1144 real inputs and exhaustively on 4 toy sizes; c00 and c01 change nothing but the labels (18/18 identical full fibre arrays, pointwise shift identity, with controls that do change), and the capacity matters only through K, a pure translation of P0 along M column 2. Toy fibre statistics are flat in K over all of F_257 (ratio 0.9988-1.0014) including K=0.
3. **Exactly one degree-drop direction per lane, always, and the exponent condition is why.** 35 toy configurations x all q+1 directions: one direction per lane, never shared, equal to (-M_i1/M_i0)^(1/5), gone after R1.M; with gcd(5,q-1)=5 the count is 0 or 5 and the round-0 reparametrisation is 5-to-1.
4. **x^(1/5) has hidden structure.** d = ((2^128-1)/5)*2^128 + lo: the top half is the repeating 0011 pattern, so a pattern-doubling chain plus a 4-bit window gives 253 squarings + 38 multiplications = 291 (vs 377 plain binary, 306 best generic window), about 97 x the cost of x^5.
5. **The fixed-point grid is dull in value, special only in derivative.** The 25 states are a 5x5 affine grid in P0 (172 collinear triples, all grid consequences); no lane is small, repeats, or lands on a fixed point; the 25 outputs are distinct. Only the Jacobian sees them (rank 0 / 1 / 2 pattern).

## 11. Questions this raised

- Q-a. Are the critical points of the full map a small, fully listable set? Beyond the lines a=0, b=0 and the three two-zero points of R1, each later round adds one zero-locus curve per lane in (A,B) (degree up to 5^k) and their rational pairwise intersections (two zero lanes at R2.C, R3.C, ...). How many F_p-rational double points exist at each level (toys can count exhaustively), and do all of them persist to the output as rank-1 points?
- Q-b. What do the fibres of the final hash look like at the critical values? The output curve H = y is singular where the gradient vanishes: at (0,0) exactly (zero gradient), and the order of vanishing there is 5 in a and b separately (H - H(0,0) lies in the ideal (a^5, b^5) since H is smooth in (A,B)); is the fibre through (0,0) an ordinary 5-fold point? Measure on toys (count points of the fibre through (0,0), compare with q).
- Q-c. Is there a capacity value where P0 (parallel family K) is special for deeper levels, e.g. K = cap* which makes all three R1.S inputs zero (254-bit value, not reachable by the real 2^65, but is the hash with cap* markedly different in toy fibre statistics)? The toy T3 scan over all K saw nothing, but only collision counts were measured.
- Q-d. A genuinely shorter addition chain for d (below 291)? And does the pattern 0x33..3 recur in the d of other quintic fields (it is (2^128-1)/5 because 5 | 2^4-1 times ...), i.e. is it a property of 5d = 1 mod 2^k only?
- Q-e. The persistent rank drop means the 3-lane map is not a local diffeomorphism of the plane onto a smooth surface: what do the surfaces S_k = image of P0 after round k look like at the critical points (cusp, fold)? Needs the local expansion in (A,B) at (A,B) with two lanes zero.
- Q-f. The toy repeated-lane-value coincidence (seed 1, 12 repeats) shows small-field coincidences exist; for the real field zero repeated values were found among 75 coordinates, but the prior for a repeat is the ratio M_i1/M_i0 being a ratio of small grid differences; check this ratio for all three lanes against {(x-x')/(y'-y)}, x,y in grid differences, and record it (not done).
