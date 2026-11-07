# U10 CARD - toy copies (learning, no attack scores)

Written 2026-10-12 by learner U10. Folder `./research/poseidon/levels/U10`. Labels: OBSERVED (a script here produced it; file named), PROVED, DERIVED, GUESS. Toy = 3 lanes over F_q, x^5, schedule {0-3 full, r partial, 60-63 full} (r partial rounds, each with its own random constants), init [nk, rho, 2^65 mod q], random constants, MDS Cauchy or (non-Cauchy: random, all 1x1/2x2 minors and det nonzero, checked not Cauchy). Library `toylib.py`. "ratio" = colliding pairs / random-function expectation. "Exhaustive" = all q^2 inputs. Real target = `poseidon_ref.py` on Pallas, constants read as data. Nothing in this card estimates a score.

## 0. What this level is

The level is not a round: it is the *calibration* level. A toy is the same machine at a size where every input can be listed, so every statement about the real structure (X1 bijection, X2 plane, X5 carry, X7 linear end form, fibre statistics) can be tested for exact truth, and every "nothing visible" can be tested for really being nothing. Read/writes: reads the atlas structure statements; writes only observations and null results.

| card field | answer |
|---|---|
| what it reads | the atlas items X1, X2, X5, X6, X7, G2, section 6 toys |
| what it writes | pass/fail of those at q=1000003 and on real p, fibre/pair statistics, symmetry cases, the exponent-condition failure |
| conditions | gcd(5,q-1)=1 (all toys except section 7); q prime |
| freedom | q, r (0..3), seed, Cauchy or not, constants (random/zero), capacity (any of q values) |
| what moves when it changes | see section 2 table: only constants+capacity being zero, and the exponent condition, changed anything visible |

## 1. Scripts and logs (all single process, numpy int64, exact)

| script | output | what |
|---|---|---|
| `e1_q1000003.py` | `e1_output.txt` | Q1: q=1000003 sampling, X2/X5/X7 |
| `e8_real.py` | `e8_output.txt` | same on the real field; non-Cauchy MDS on real p; zero-constant symmetry on real p; S fixed points; exponent d |
| `e2_mds.py` | `e2_output.txt` | Q2 + Q6: Cauchy vs non-Cauchy, fibre and pair statistics, q=257..4099, r=0..3 (its last section "X6 trail" is WRONG - see 5.1; superseded by e9) |
| `e9_trail.py` | `e9_output.txt` | corrected X6 trail check, real + toys + brute force |
| `e3_adicity.py` | `e3_output.txt` | Q3: S-box fixed points, cycles, fibre differences (stopped before q=4099 differences: too many pairs, 3.4e10) |
| `e10_sampled.py` | `e10_output.txt` | q=65537, 1000003 sampled (2e7 inputs) |
| `e4_capacity.py` | `e4_output.txt` | Q4: all capacities q=257 (3 runs), q=769 |
| `e5_zero.py` | `e5_output_partial_q257_1009_4099r012.txt`, `e5b_output.txt` | Q5: zero constants (first run for 257, 1009, 4099-r012 was stopped at its cap sweep for 4099 and re-run with fewer caps for q=769, 4099 in e5b) |
| `e7_exp5.py` | `e7_output.txt` | Q7: gcd(5,q-1)=5 |

## 2. Observations by question

### Q1 - toy q = 1,000,003, X2 / X5 / X7

- q = 1000003 prime; q-1 = 1000002 = 2 * 3 * 166667 (v2 = 1, q = 3 mod 4, q = 3 mod 5); gcd(5, q-1) = 1; 5^-1 mod (q-1) = 400001. [OBSERVED e1]
- X2 (state after R0 satisfies (M^-1 s)_2 = K, K = (cap + c02)^5), X5 (state after R4 = M*(w, s1+c, s2+c) with w the 5th power of lane 0), X7 (output = row 0 of M dot the three 5th powers of (state before R63.S + c63)): **20000/20000 inputs each, r=1 and r=2, Cauchy and non-Cauchy MDS** (4 cases). [OBSERVED `e1_output.txt`; command `python e1_q1000003.py`]
- Same three statements on the real field: **2000/2000 each, r=1 and r=2**, with the real Cauchy MDS and with a random non-Cauchy MDS substituted. [OBSERVED `e8_output.txt`]. [PROVED] they use only invertibility of M, never Cauchy form.
- Boring: the "birthday" lane-0 collision count in `e1_output.txt` (18680 vs 20000 expected) is an artifact of my dict overwriting earlier entries; superseded by e10. Not a result.

### Q2 - non-Cauchy random MDS: is Cauchy visible?

- Exhaustive, q = 257 (6 seeds, r = 0,1,2,3), 769 (4 seeds, r=1,2), 1009 (4 seeds, r=1,2), 4099 (2 seeds, r=1,2); both families. Fibre statistic ratio of lane 0: mean 0.9998-1.0001, sd about 0.0003 at 257, both families; var/mean of fibre sizes 0.94-1.03 (Poisson 1; sd of the estimate about 0.09 at q=257) in both families; pair counts (lane0,lane1), (lane0,lane2), (lane1,lane2) same in both. Differences between families are inside seed-to-seed noise everywhere. [OBSERVED `e2_output.txt` SUMMARY]
- Sampled q = 65537 and 1000003 (2e7 inputs): lane-0 ratio 1.000 for both families, r=1,2. [OBSERVED `e10_output.txt`]
- Full-state: all 3-lane outputs distinct (q^2 of q^2) for every exhaustive toy with q <= 1009, both families. [OBSERVED]
- X6 trail vector d = (0, M02, -M01) works the same: lane 0 equal after R4.M, and difference after R5 equals M*(0,d1',d2'), 500/500 on real p (Cauchy and not), q=257, q=1000003, both families; and for generic d with d0=0 the lane 0 is equal after R4,R5 in 0-4 of 500 (chance). Brute force q=257, 3 states: exactly the 256 nonzero points of the line c*(M02,-M01) keep lane 0 equal after R4.M, all other (d1,d2) do not. [OBSERVED `e9_output.txt`]
- Conclusion (null): **the Cauchy structure is not visible in fibres, pair counts, plane/carry/end-form identities or the 2-round trail.** Not tested: powers/inverses of M (M^-1 is Cauchy too), anything that uses the Cauchy parameters x_i, y_j directly.

### Q3 - high vs low 2-adicity

- Fixed points of x -> x^5: 5 for q = 1 mod 4 (257, 769, 12289, 65537, 1009), 3 for q = 3 mod 4 (4099, 1000003). The S layer therefore has 125 fixed triples (q = 1 mod 4) or 27 (q = 3 mod 4). [OBSERVED `e3_output.txt`; PROVED G2]. On real p: 0, 1, -1, i, -i all satisfy x^5=x (5 solutions), 125 triples. [OBSERVED e8]. The fixed-point count depends on q mod 4 only, **not** on the size of the 2-adicity (v2 = 4 at 1009 behaves like v2 = 16).
- Cycle structure of x -> x^5 on F_q^*: the 2-adicity shows directly: 257: cycle lengths 1(x4),2,4,...,64 (x2 each, 16 cycles, longest 64); 769: 1(x4),2(x10), then 4..64 (x6 each); 12289 (v2 = 12): up to 1024 (x6), 68 cycles; 65537 (v2 = 16): lengths 2^k up to 16384, two of each, 32 cycles; 1009 (v2 = 4): 1(x4),2(x10),4(x6),6(x80),12(x40) (3-part 3^... of 1008 = 16*63); 4099 and 1000003 (v2 = 1): only 1(x2), 2(x2), and six cycles of length 682 / 166666 = (q-1)/6 minus a bit. [OBSERVED]. Link to real p: ord of 5 mod 2^32 is 2^30 (atlas G1), so the 2-power part of the real cycle structure is a long ladder like 257/65537's, the odd part unknown (212-bit cofactor unfactored).
- Fibre statistics (r=1,2) at v2 = 8, 4, 1 are all random-looking, exhaustive and sampled: ratios 1.000; no trend with 2-adicity. [OBSERVED e2, e3, e10]
- Fibre differences (r=1, lane 0 fibres): for each pair of inputs in one fibre, multiplicity of the difference (dn, dr) (up to sign), compared with the same count after shuffling the outputs (null). q=257 (2 seeds), 769 (2), 1009 (2): REAL and NULL agree on max multiplicity (320 vs 339, 325 vs 326, 898 vs 893, 903 vs 884, 1167 vs 1157, 1164 vs 1171), on the number of distinct differences, and on the number of axis-aligned (dn=0 or dr=0) pairs. **No preferred difference in any fibre.** [OBSERVED `e3_output.txt`] Not done: q=4099 differences (3.4e10 pairs, stopped), q=12289, 65537 fibre differences (too big).

### Q4 - capacity scan

- All q capacities, same constants/MDS: q=257, r=1, seed 1: lane-0 ratio over 257 capacities min 0.9992, max 1.0011, mean 1.0000, sd 0.0003; var/mean 0.79-1.28; image size always 257. r=2: ratio 0.9991-1.0008. seed 2 r=1: 0.9992-1.0010. q=769, r=1: all 769 capacities, ratio 0.9998-1.0002, var/mean 0.86-1.17. After-R3 lane-0 ratio the same band. The sd of var/mean from sampling is about 0.09 at q=257, so the range is about +-3 sd. [OBSERVED `e4_output.txt`]
- Special capacities (cap = 0, 1, -1, 2^65 mod q, cap with K = (cap+c02)^5 = 0, cap+c02 = +-1): all inside the band; nothing special at K = 0 (where the post-R0 plane passes through the span of M's columns 0 and 1). **Null result.**
- [PROVED] the hash depends on the capacity only through K = (cap + c02)^5, and cap <-> K is a bijection; so scanning all caps is scanning all K.
- Exact scaling law (zero constants only, see Q5): H_{lam*cap}(lam*x) = lam^e H_cap(x), so for r = 0 the whole fibre-size multiset is the same for **every nonzero capacity**. [OBSERVED 38/38 caps at q=257, 769, 1009 (first 38 shown), 6/6 at 4099; PROVED]. With random constants this symmetry is gone, and the real constants are not zero.

### Q5 - all constants zero

- Zero constants and cap = 0 make the map homogeneous. Full rounds only (r = 0): y(lam x) = lam^(5^8) y(x) for every lam (OBSERVED q=257, 769, 4099 for lam = 2,3,5,7; real p 20/20). Consequence [OBSERVED]: fibre of 0 has 1 + k(q-1) points (k = number of zeros of the output as a projective form) and **all nonzero fibres have exactly the same size (q^2 - fibre0)/(q-1)**: q=257: fibre0 = 1, all 256 other fibres = 258; q=769: 1 and 770; q=1009: 2017 and 1008 (k=2); q=4099: 12295 and 4097 (k=3). The aggregate collision ratio stays 1.000 here, but the variance of fibre sizes is not random-like: var/mean is 1.00 at q=257 (one tiny fibre, 256 equal ones) and 4.00 at q=4099 (3 zero-lines make fibre 0 huge), where a random function would give about 1.
- With partial rounds (r = 1,2) the scaling survives only for lam with lam^4 = 1 (S commutes with lam in mu4; in a partial round lanes 1,2 scale by lam and lane 0 by lam^5): y(lam x) = lam y(x), lam in mu4. [OBSERVED exhaustive q=257, 769, 4099 (mu4 = {1,-1} there) and real p (i): 40/40 at r=0,1,2; fails 0/40 with the real constants or the real capacity]. Fibre sizes are then constant on mu4-orbits (True at q=257, 1009, 769, 4099) and the number of distinct nonzero fibre sizes drops (257: 39 vs 72; 1009: 108 vs 153; 4099: 311 vs 349). The fibre-of-0 size and the collision-pair ratio stay at random-function values (ratio 1.000-1.001, fibre0 253, 1057, 745, 4117 against about q).
- With r = 1 and zero constants, fibre-size multisets for different capacities agree exactly for cap in the orbit of cap=1 under mu4 and for no other tested cap (q=257: 1 of 38 other caps, namely cap = 16 = i; q=769: 0 of 38 because 62 is outside the range tested; 4099: 0 of 6): the orbit law is what the symmetry predicts. [OBSERVED `e5_output_partial...`, `e5b_output.txt`]
- So the "trivial" collisions are: for the symmetric (all zero) toy, the structure sits entirely in the sizes of fibres on orbits, not in the number of colliding pairs. For the actual hash the symmetry is broken by the constants and by cap = 2^65 != 0: real p, 0/40 at every r. [OBSERVED e8]

### Q6 - pairs equal in lane 0 and lane 1 (and other lane pairs)

- Random-function expectation for (l0, l1) is N(N-1)/2 / q^2 (about q^2/2). Observed ratio (exhaustive) 0.994-1.000 at q=257, 0.998-1.000 at 769, 0.998-1.001 at 1009, 1.000 at 4099; the same for (l0,l2) and (l1,l2). [OBSERVED `e2_output.txt`]
- The small systematic deficit is explained by X1: the 3-lane map is injective, so any two outputs differ in the full state; the chance that two distinct states agree in two given lanes is (q-1)/(q^3-1) = 1/(q^2+q+1), giving expected ratio q^2/(q^2+q+1) = 0.9961 (q=257), 0.9987 (769), 0.9990 (1009). Observed means over seeds: 0.9956 at 257, 0.9987 at 769, 0.9985 at 1009. [DERIVED, matches OBSERVED]. For lane 0 alone the correction is 1 - about q^-2: invisible, which is why lane-0 ratios sit at 1.000.
- Sampled (2e7 draws with replacement) q = 65537, 1000003: the raw (l0,l1) and "full" pair counts are inflated by duplicate draws of the same input (expected N^2/(2q^2) = 46565 at 65537, 200 at 1000003, and "full" pairs equal exactly that duplicates number: 46765, 46474, 46592, 46455; 197, 198, 189, 231). Subtracting duplicates gives genuine (l0,l1) pairs 46492 / 46140 / 46837 / 46376 (expected 46565) at 65537; 156/225/208/198 (expected 200) at 1000003. [OBSERVED `e10_output.txt`]. Full-state collisions beyond duplicates: **none**, 8 of 8 runs.
- The pair counts do not depend on r (0..3) or Cauchy-ness within noise. Lane-0 pairs after R3 only (same for every r): ratio 1.000 band.

### Q7 - exponent condition gcd(5,q-1) = 5

- Primes q = 1 mod 5 (11, 31, 41, 61, 71, 101, 131, 151, 181, 191, 211, 1051), r=1,2, 2 seeds, exhaustive. After R0 the image of the (nk,rho) square is exactly ((q-1)/5 + 1)^2 states: 9 (q=11), 49 (31), 81 (41), 169, 225, 441, 729, 961, 1369, 1521, 1849, 44521 (1051) in every run. [OBSERVED `e7_output.txt`; PROVED: x^5 has (q-1)/5 + 1 values, the plane is 2-dimensional].
- Later rounds shrink the image only slightly (q=1051, r=1: 44521, 44427, 44315, 44202, 44200, 44109, 44019, 43921, 43831 after rounds 1-9; the partial round (R4) removes 2 states). Final distinct full states: 43831 of 1104601 inputs (r=1), i.e. each full state is hit about 25 times. Colliding full-state pairs: 13.66 million at q=1051 against 525 for a random function to F_q^3. [OBSERVED]. At q=11 the image collapses to 2-5 states.
- Lane-0 pair ratio is above 1 and falls toward 1 as q grows: 5.5, 2.5 (q=11), 2.55 (31), 2.2 (41), 1.45 (61), 1.34 (71), 1.28 (101), 1.22 (131), 1.16 (151), 1.15 (181), 1.13 (191), 1.14 (211), 1.024 (1051). Roughly excess = 25/q. [OBSERVED; the 25/q fit is a GUESS: it matches the 25-fold compression of the (nk,rho) square].
- Controls, gcd(5,q-1)=1 primes 13..139 and 1009 (r=1,2, 2 seeds): full-state pairs exactly 0 (all q^2 states distinct), lane-0 ratio 0.97-1.01 (noise). [OBSERVED]. Sharp difference: the exponent condition is what makes the three-lane map injective; without it the lossy part happens in **round 0** (most of the loss), because x^5 is 5-to-1 there on both input lanes.

## 3. The 5 most surprising / useful observations

1. **Exact X1 fingerprint in pair counts**: with injective 3-lane maps the (lane0,lane1) pair counts are *not* q^2/2 but q^2/2 * q^2/(q^2+q+1); predicted and observed match (0.9961 vs 0.9956 at q=257). Genuine (l0,l1) collisions at q=65537 and 1000003 are at the same rate and there are zero full-state collisions in 8/8 sampled runs and in all exhaustive runs. [DERIVED + OBSERVED]
2. **Everything that looked like structure is invisible to fibre statistics.** Cauchy vs non-Cauchy, 2-adicity 1 to 16, any of the 257/769 capacities, r = 0..3: all give random-function ratios. The only structure seen at the statistic level appears when constants and capacity are made zero (Q5) or the exponent condition is dropped (Q7). So fibre-count statistics are a blind instrument here; look for structure with identities (X2, X5, X6, X7) and symmetries, not with fibre counts. [OBSERVED]
3. **Zero constants + cap 0 gives an exact scaling symmetry**: full rounds only (r=0): y(lam x) = lam^(5^8) y(x), all nonzero fibres the same size q+1 (257), 1008 at 1009; with partial rounds only the 4th roots of unity survive (mu4), with fibre sizes constant on mu4-orbits and the capacity family orbit {cap, i*cap, ...}. The real hash breaks this twice (constants, cap = 2^65). Verified on the real field: y(i x) = i y(x) 40/40 with zero constants and cap 0, 0/40 otherwise. [OBSERVED + PROVED]
4. **gcd(5,q-1)=5 fails in round 0**: the image after R0 is exactly ((q-1)/5+1)^2 (25-fold compression), later rounds add only about 1% loss each. Without the exponent condition the hash would lose its (nk,rho) square in the first round. [OBSERVED + PROVED]
5. **The trail vector of X6 is exact and Cauchy-independent**: at q=257 brute force over all 66049 (d1,d2) shows exactly the 256 nonzero points c*(M02,-M01) keep lane 0 equal after R4.M, so the R5 S-box sees no difference; the same line works on real p for both Cauchy and non-Cauchy M. The first version of this check in `e2_mds.py` asked for the wrong thing (lane 0 equal after R5.M) and reported 0/2000; corrected in `e9_trail.py`. [OBSERVED]

## 4. Dull and null results (kept on purpose)

- Real-field 5th-root exponent d: 254 bits, popcount 125. A plain square-and-multiply costs 253 squarings plus 124 multiplications (about 377 field mults) against 3 for x^5. [OBSERVED popcount; DERIVED cost].
- Capacity scan at q=257, 769: no capacity stands out; K=0 and a=+-1 are ordinary. Fibre differences: none preferred at 257, 769, 1009. Cauchy: not visible. 2-adicity: not visible in fibres.
- x^5 cycle structure (Q3) is a visible footprint of 2-adicity (lengths 2^k) but no hash statistic saw it.
- Lane-0 pair counts after R3 are independent of r (trivial: same rounds).
- Toy q = 65537 and 1000003 were sampled only; exhaustive q^2 = 4.3e9 / 1e12 not attempted.

## 5. Corrections to my own earlier steps

5.1 `e2_mds.py` final section ("X6 trail check") tested lane 0 equal after R5.M, which X6 does not claim (it claims the R5 S-box sees equal lane 0, and the output difference is M(0,d1',d2')). Result "0/2000" there is meaningless. Superseded by `e9_trail.py` (correct, passes).
5.2 `e1_output.txt` last line (lane-0 birthday 18680 vs 20000) is a dict-overwrite artifact. Superseded by `e10_output.txt`.
5.3 Sampling with replacement at large q inflates pair counts by duplicate inputs (Q6). Always subtract the duplicate count (equal to the 'full' pair count).

## 6. Questions this raised (open)

1. If fibre statistics are blind, what instrument does see the structure of the real levels? Candidate: counts of *pairs with equal lane 0 after R3 that also keep a property after the tail* (the Q-list "partial collisions"), still untested on toys; also exhaustive enumeration of the surface sizes in the implicit-equation sense (U2.3).
2. Does the q^2/(q^2+q+1) deficit (an X1 signature) have a counterpart for the pair (lane0 after R3, ...) at intermediate levels? I.e. does injectivity of each round leave a computable fingerprint in the number of pairs agreeing on 1 or 2 lanes at each level?
3. With zero constants the orbit symmetry mu4 survives partial rounds. Do the real constants retain a *residual* symmetry on some sub-piece (e.g. two rounds' constants being related by a scalar from mu4)? The atlas checked c_(r+1) = M c_r only; relations c_s = lam * c_r with lam in mu4 were not searched (U6.6).
4. Why do 2-adic cycle lengths of x^5 (powers of 2 up to 2^30 on the real field) not show in any statistic? Is there an observable that does (e.g. iterate the S layer with zero constants and cap = 0 on the real field)?
5. The 25/q law for lane-0 excess at gcd = 5: exact form? (Number of preimages per state = 25 at R0, plus later merges.) Would an exact formula (sum of squared fibre sizes of x -> x^5 on the plane) reproduce 1.024 at q=1051?
6. Is the number k of projective zeros of the full-round-only form (k = 0 at 257, 769; 2 at 1009; 3 at 4099) predictable? It is the number of rational points of a curve; for the real p what is it (r = 0, cap 0, zero constants)?
7. The effect of a *non-MDS* matrix (zero entry / zero minor) was not tested; Cauchy being invisible says nothing about MDS-ness being unneeded. Which statistic (if any) changes when a 2x2 minor is made zero?
