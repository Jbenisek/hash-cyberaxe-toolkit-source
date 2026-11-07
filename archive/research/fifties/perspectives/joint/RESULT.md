# Joint lens: the four residual words together

2026-10-09 20:15. Labels: **COMPUTED** = measured by the code in this folder; **DERIVED** = algebra from the G steps,
also checked on every row unless stated; **GUESS** = model or interpretation, not established.
Data: `perspectives/data` (rand 2^20 independent rows, ctx 2^18 rows; DATA.md). Train/test = the two halves of rand
(ctx: contexts 0-7 / 8-15). Every statistic is run on a control of the same size; details are in the `*_out.txt` files.

## Answer

Yes. The residual has well under 128 bits of effective entropy, and the structure is exact, not just statistical.

| measure | bits | label |
|---|---:|---|
| nominal check (words 1,3,4,6) | 128 | - |
| GF(2) affine hull of R over all inputs. It contains 0, so R = 0 stays possible | **126** | COMPUTED + DERIVED |
| Shannon entropy, upper bound (Chow-Liu over bytes, in rotate-by-7 coordinates) | **<= 106.0** (uniform control 127.96) | COMPUTED |
| collision entropy, sum over the 4 words of (R1, R3, R4^ROR(R1,7), R6^ROR(R3,8)) | 105.8 | GUESS (assumes independent words) |
| hull of R inside one (context, member) group, whole 2^21 cube | 116-126, mean 122.0 | COMPUTED |
| -log2 Pr[R = 0] for pkgCG: E1 census x prior E3 table | about 91.3 | GUESS (see 3) |

An Archimedean-spiral view exposes the joint residual structure. Overlay each word on its partner turned by the
G function's last two rotations, 7 and 8 (R4 against ROR(R1,7), R6 against ROR(R3,8)). Viewed that way, two of the
four words collapse to about 22 bits, and the 128-bit check splits into one-sided pieces.

## 1. Two exact linear relations (rank 126)

**COMPUTED.** The affine rank of R is 126 on every set tested:
- rand, all 2^20 rows and each half;
- ctx, all rows and each of the 16 contexts.

Uniform rows give rank 128 (control in `d4joint_out.txt`). Both relations below have constant 0. Output:
`explore0_rank_out.txt`.

- (E-a) `parity(R3) ^ parity(R6) = 0`
- (E-b) `XOR of R3 bits 8..31  ^  R4 bit 25  ^  XOR of R6 bits 1..24 = 0`

**DERIVED.** Both follow from two facts:
- In pkgCG, `dc1 = E1.c1 A^B = 0e09818b` on every row (the Q* cube fixes it; COMPUTED on all rows).
- `dh1 = eta` on every row.

(E-a): R6 ^ ROR(R3,8) ^ ROR(eta,8) = ROR(dc1,19) ^ ROR(dc2 ^ ROR(dc2,1), 7). The term dc2 ^ ROR(dc2,1) has even
parity, and parity(dc1) = parity(eta) = 1.

(E-b): use dh2 = ROR(eta ^ de2, 8), db2 = ROR(ROR(dc1,12) ^ dc2, 7) and da2 bits 0-3 = 0. Then the LSB rule for
addition (dg1[0] = eta[0], dg2[0] = dg1[0] ^ dh2[0], de2[0] = de1[0] ^ dg1[12]) cancels every variable term.

Both relations have high weight (64 and 49 bits), so a low-weight bias search cannot find them. The rank computation
did.

## 2. Spiral coordinates: the check splits into one-sided pieces

**DERIVED, and checked on all 2^20 + 2^18 rows with 0 failures** (`explore4_identities_out.txt`):

| coordinate | equals | side | H2 bits (COMPUTED, uniform control 31.9-32.2) |
|---|---|---|---:|
| U1 = R6 ^ ROR(R3,8) ^ ROR(eta,8) | ROR(dc1,19) ^ ROR(dc2 ^ ROR(dc2,1), 7) | E1 only | 22.76 |
| Q7 = R6 ^ ROR(R3,7) | ROR(dc1,19) ^ ROR(eta,8) ^ ROR(de2 ^ ROR(de2,1), 7) | E3 only | 24.63 |
| U3 = R4 ^ ROR(R1,8) | ROR(dg1,19) ^ ROR(dg2 ^ ROR(dg2,1), 7) | E3 only | 31.85 |
| Z7 = R4 ^ ROR(R1,7) | ROR(da2 ^ ROR(da2,1), 7) ^ ROR(dg1,19) | da2 (E1) and dg1 (E3) | 22.03 |

**DERIVED.** R = 0 is equivalent to four conditions:
- **E1 only, 31 bits:** dc2 is 91de41aa or 6e21be55. These are the two solutions of X ^ ROR(X,1) = ROR(eta,1) ^ ROR(dc1,12).
- **E3 only, 67 bits:** de2 = dc2, U3 = 0 and dg2 bits 0-3 = 0. One of these bits is implied by (E-b).
- **Match, 28 bits:** da2 = dg2.

The total is 31 + 67 + 28 = 126, which agrees with section 1. In (t, s) language this is the event Z of the prior
REPORT (`opus_cloud/Smash-claude-math-help-g3v211/REPORT.md`, R1). The new point is what pkgCG fixes, below.

**COMPUTED** (`e1filter.c`). Two censuses with independent seeds, each covering 2^14 contexts x the full 2^21 cube:
- **Pr[dc2 = 6e21be55] = 2^-25.98** (1,038 hits in 2^36; the seeds gave 489 and 549).
- 91de41aa never occurs (0 in 2^36).
- The hits are spread evenly over contexts. Seed 1: 465 contexts with one hit and 12 with two, close to Poisson.
  Choosing a context does not make this filter cheaper.
- The checker reproduces da2, dc2 and c1 on all 2^20 stored rows.

## 3. Consequence for the D5 / 453-pair numbers (please check)

DERIVED, given REPORT.md line 14 (s = dc2, beta = db1). The prior table's model leaves dc1 free and charges for it
inside P1avg. In pkgCG, dc1 is fixed, so beta = 18b0e098 and only s = 6e21be55 can contribute.

COMPUTED on the table: that is 14 of the 453 pairs. The table has 60 distinct s values. Its best pair,
(189060a0, 6e203e55) with beta* = 18b1a098, needs dc1 = 1a09818b, which pkgCG cannot reach.

GUESS: replace P1avg with the measured E1 census. Then sum_t P_E1(t) * W15(t, 6e21be55) = **2^-91.3** (W13: 2^-91.2).
- Only 20 of the 1,038 hits have a da2 among the 14 table t values, with 0-3 hits per t, so this figure is noisy
  to about 1 bit.
- W15 comes from the prior DP. I have not checked that its E3 model matches pkgCG's 19-bit e1 class.
- How the front line's 63.9522 already accounts for any of this is not checked here.

## 4. Statistical scans (train/test, controls)

**Walsh coefficients, every mask of weight 1-4** (10,668,000 at weight 4). Run in three coordinate systems: raw,
rotate-by-8 and rotate-by-7. Source `walsh.c`; outputs `walsh_{raw,spiral,spiral7}_out.txt`.
- **COMPUTED.** At weight 4 in raw coordinates, 30,246 masks have |z| > 6, and 30,203 of them confirm on test. The
  uniform control has 0.
- **COMPUTED.** The excess over per-word shuffles is 20,970 masks (0 in a shuffle-vs-shuffle control).
- The largest correlations are bit pairs R1.i with R4.(i-7) (c up to 0.954) and R3.i with R6.(i-8)/(i-7). These are
  the section 2 identities.

**Coupling of K1 and K3**, measured by re-pairing K1 with the K3 of another row. Outputs `walsh_k*_out.txt`.
- **COMPUTED.** No mask of weight 1-4, in any of the three coordinate systems, differs from the re-paired null.
  At weight 4 the largest |z| is 5.36-5.43, against 5.52 in the control, with 0 masks above 6.
- Averaged over contexts, then, K1 and K3 are independent at |c| < about 0.008. That supports
  Pr[R=0] = sum_v P1(v) P3(v).

**Inside a fixed (context, member) group** (ctx; the group is the statistical unit; `coupling_ctx_out.txt`):
- **COMPUTED.** The average coupling is zero: max |t| = 3.06, and 0 bits confirm.
- **COMPUTED.** The per-group coupling is real. On 19 bits, all in R3 and R6, the spread of the within-group
  covariance is more than 2 times the null on both halves; for R3.20 it is 10.7 times (11.0 on test).
- The sign of this coupling changes from group to group.
- An earlier row-level z for this test was overstated because of clustering. `coupling_ctx_se_out.txt` shows the
  correction.

**Rotation scan.** For all i, j and r, `R_i op ROR(R_j, r)` with op = xor, add or sub, judged by collisions
(`spiral_mi_out.txt`). **COMPUTED.**

| combination | H2 (bits) | z (train / test) |
|---|---:|---:|
| R1 ^ ROL(R4,7) | 22.03 | 5563 / 5508 |
| U1 | 22.77 | 2829 / 3096 |
| R4 - ROR(R1,7), modular | 23.8 | - |
| Q7 | 24.65 | - |

- The uniform control's maximum is 45 collision pairs against an expected 32.
- No other pair confirms: 9 combinations reach z > 4 on train, and 0 reach z > 3 on test, apart from one
  marginal case (add R1 R6 r=0, test z = 3.1).

**Windowed mutual information** (8-bit windows, every p and q, 6,144 per half). **COMPUTED.** The noise sd per window
is 0.0005 bits; the shuffle bias of 0.093 bits is subtracted.

| pair | max MI per byte pair (bits) | lag | what the lag means |
|---|---:|---:|---|
| R1-R4 | 2.83 | 25 | rotate by 7 |
| R3-R6 | 2.47 | 24 | rotate by 8 |
| R4-R6 | 0.44 | 8 | cross-block |
| R1-R6 | 0.41 | 0 | cross-block |
| R3-R4 | 0.06 | 17 | - |
| R1-R3 | 0.05 | 9 | - |

Every one of the 6 pairs has hundreds of windows that confirm on test. The coupling null above rules out K1-K3
terms, so the cross-block dependence comes from inside K1 or inside K3. GUESS: the route is da2 driving dc2 through
d2.

**Shannon bound** (`entropy_bound_out.txt`). Chow-Liu tree over the 16 bytes, with the tree chosen on train and
evaluated on test. **COMPUTED.**

| coordinates | bound (bits) |
|---|---:|
| raw | 109.9 |
| rotate-by-8 | 109.6 |
| rotate-by-7 | **106.0** |
| mixed (R1, R3, Z7, U1) | 107.1 |
| uniform control | 127.96 |

**D4 partial records** (1,577; `d4joint_out.txt`). **COMPUTED.** Rank 128, and no single bit or cross-word pair
confirms, the same as the uniform control. The test can only detect |c| >= about 0.16, and these values are not
residuals of a completed construction.

## 5. Conditional structure: most (context, member) groups can never reach R = 0

**COMPUTED** (`grouphull.c`; 64 groups plus 256 groups with a fresh seed, each over the whole 2^21 cube; checker
reproduces K1/K3 on all 2^20 stored rows):
- With the outer words and k fixed, R(j) lies in an affine space of rank 116-126 (mean 122.0).
- **Only 92 of 320 groups (28.8%) contain 0 in that space.** In the other 71%, R != 0 for every cube index j, by an
  exact linear obstruction.
- The hull is fixed by 2^14 cube points in 320 of 320 groups, and by 2^10 points in 313 of 320.

**COMPUTED** (ctx, `explore3_grouprel_out.txt`). Each of the 476 obstructing relations splits into a global E1
constant plus a group-specific E3 constant. Feasibility is therefore a property of the E3 side of
(outer words, member).

**GUESS (exploitable):** an attack that walks the cube inside groups can drop dead groups after at most 2^14 E1/E3
half-G evaluations each. That saves log2(320/92) = 1.8 bits of trials. Cheap early aborts also exist:
- the E3 group test above;
- the E1-only test dc2 = 6e21be55, which costs about 20 word operations per j and passes at 2^-26.

Whether the front line's gate, T1/T2 or joint-root steps already filter the same thing is not tested; the samples
are unfiltered.

## 6. Not tested

- Whole-message `blake3()` was not run: the pairs are compression-level (DATA.md).
- The E3-only 67-bit probability for pkgCG was not measured. Section 3 uses the prior table.
- The bias search stops at weight 4, in three coordinate systems. Higher-weight masks were seen only through the
  rank computation.
- Whether 91de41aa is impossible was not established; it is only absent from 2^36 samples.

## Files

All in `research/fifties/perspectives/joint/`.

| purpose | code | output |
|---|---|---|
| exact rank, relations, parity identities | `explore0_rank.py` | `explore0_rank_out.txt` |
| K1/K3 hulls, per-group ranks | `explore1_groups.py` | `explore1_groups_out.txt` |
| solve X0, one-sided H2 values | `explore2_split.py` | `explore2_split_out.txt` |
| split of the per-group relations | `explore3_grouprel.py` | `explore3_grouprel_out.txt` |
| 4 identities, combined census | `explore4_identities.py` | `explore4_identities_out.txt` |
| Walsh search | `walsh.c` (`run_walsh.sh`, `run_coupling.sh`) | `walsh_*_out.txt` |
| E1 census | `e1filter.c` (`run_e1filter.sh`, `run_confirm.sh`) | `e1filter_out*.txt`, `e1filter_hits*.txt`, `e1filter_check_out.txt` |
| group hull | `grouphull.c` (`run_grouphull.sh`, `run_confirm.sh`) | `grouphull_out*.txt`, `grouphull_check_out.txt` |
| rotation scan and windowed MI | `spiral_mi.py` | `spiral_mi_out.txt` |
| Shannon bounds | `entropy_bound.py` | `entropy_bound_out.txt` |
| coupling inside groups | `coupling_ctx.py` | `coupling_ctx_out.txt`, `coupling_ctx_se_out.txt`, `coupling_ctx_decomp_out.txt` |
| D4 records | `d4joint.py` | `d4joint_out.txt` |

The C programs reuse `../data/gen.c` through `#include`. They build with gcc -O3 -fopenmp in WSL Ubuntu, and each
run took at most 2.5 minutes. `spiral_mi.py` took 7.4 minutes. No yukon, no submission, and no GPU was needed.
