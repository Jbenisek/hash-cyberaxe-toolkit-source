# Rotational lens on the front-line residual

2026-10-09, about 20:20. Labels: **COMPUTED** means measured here by the code in this folder. **DERIVED** means algebra from the G steps. **GUESS** means an interpretation that has not been verified.
Data: `../data` (rand 2^20 independent rows; ctx 2^18 rows). In ctx, the 52 repeated input rows are dropped before any statistic, which leaves 262,092 rows.
Train/test: every statistic is computed on half T (the first half of the rows) and half V (the second half). In ctx the halves hold different contexts (0-7 and 8-15).

## Answer

1. **There is no rotational relation between the side-A and side-B digests.** COMPUTED. For r = 1..31, every word pair, and every cross-word pair, none of these three forms beats chance:
   - B = rotl(A,r) XOR small/const
   - B = rotl(A,r) + const
   - B = rotl(A + const, r)

   This holds jointly over the four words too, in both sets. Planted relations on about 2^-14 of the rows were found and confirmed (see below), so the test had the power to see them.
2. **The residual itself has strong rotation-plus-constant structure, but it is the front line's own decomposition (eps, tau, sigma), not a new saving.** DERIVED, and checked on every row of both sets with 0 failures:
   - **Exactly one free bit.** parity(R3) = parity(R6) on every row. So R lies in a 127-dimensional subspace, and the 128-bit check is really 127 independent bits.
   - **U6 = R6 ^ ROR(R3,8) depends on E1 only.** It equals ROR(db1,7) ^ ROR(eta,8) ^ ROR(dc2,7) ^ ROR(dc2,8). U6 = 0 exactly when dc2 is in {6e21be55, 91de41aa}. 6e21be55 is the eps of the filed proof (dossier fa761365, proof lines 1338, 1555, 2540). The second root 91de41aa is effectively unreachable: COMPUTED, its top 6 bits match in fewer than 8 of 2^19 rows.
   - **W3 = R3 ^ ROL(R6,7) depends on E3 only.** It equals db1 ^ ROR(eta,1) ^ de2 ^ ROR(de2,1). W3 = 0 exactly when de2 is in the same {eps, ~eps}.
   - **W4 = R4 ^ ROR(R1,7) mixes the two sides.** It equals ROR(da2,8) ^ ROR(da2,7) ^ ROR(df1,7). W4 = 0 exactly when df1 = da2 ^ ROR(da2,1). This is the proof's sigma_j = tau_j ^ ROR(tau_j,1).
   - **U4 = R4 ^ ROR(R1,8) depends on E3 only,** but it is close to uniform.
   - **The four conditions together.** R = 0 holds exactly when (U6 = 0) and (R3 = 0) and (R1 = 0) and (W4 = 0).
3. **Effective entropy.** Per-coordinate Rényi-2 entropy (COMPUTED, rand, from collision pairs; ctx agrees):

   | coordinate | H2 (bits) |
   |---|---:|
   | R1 | 31.4 |
   | R3 | 29.6 |
   | R4 | 31.6 |
   | R6 | 30.4 |
   | U4 | 31.9 |
   | **U6** | **22.8** |
   | **W3** | **24.6** |
   | **W4** | **22.0** |

   - **Where the deficit sits.** It is concentrated in the rotation-plus-XOR coordinates U6, W3 and W4, not in the digest words.
   - **Shannon upper-bound estimates** (sum of 16-bit chunk entropies):
     - 128 - 5.3 = 122.7 bits in R's own bits.
     - 128 - 7.3 = 120.7 bits in the coordinates (R1, R3, U4, U6).

     Both estimates are loose, because 16-bit chunks cannot see 32-bit structure.
   - **This structure is already priced.** The exact table probability the front line already uses (D5: P_joint = 2^-100.53) accounts for it. GUESS: this lens gives no cheaper route. The only item that may not have been stated before is the free parity bit, and any exact accounting already includes it.
4. **Period-4 classes give no extra leverage.** COMPUTED.
   - **Inside each word:** the period-4 class view sees *less* structure than the contiguous view (deficit 1.565 against 2.758). Bits that are 4 apart are independent beyond their single-bit biases.
   - **Across words:** it helps only because ROR 8 preserves the class. Pairing class c of words (1,4) and (3,6) captures the known ROR-8 links.
   - **Period-4 differences:** they do not occur in this family. R's words are not enriched near period-4 words, and the family's constant differences are far from period-4 (d4 = 9..13).

## 1. Side A against side B (`rotscan.c` scan AB and scan J; `analyze.py`)

**Statistic.** V = B_j op rotl(A_i, r) for i, j in 0..3 and r = 0..31, with three ops:
- x: B ^ rotl(A,r)
- s: B - rotl(A,r)
- r: ror(B,r) - A

**Statistics computed on V:**
- HW histogram and mean
- per-bit chi-square
- the tails HW<=4, HW<=8, HW>=24
- d4<=4 and d4<=6 (d4 = distance to the nearest period-4 word)
- |V| <= 256
- V == 0
- collision pairs
- the highest multiplicity of a single value (a rotation + constant relation shows up as a repeated V)

**Controls:**
- 0 = the analytic uniform law.
- U = uniform random words, the same count.
- S = shuffle: B' = A ^ (A ^ B) taken from another row. This keeps the difference law and breaks its link to A. Op s uses the modular difference.

**Thresholds.** A finding needs |z| >= 5 on T. It is confirmed if V shows |z| >= 3 with the same sign. Combinations outside "r = 0, i = j": 508 × 3 ops × 10 statistics = 15,240 tests per comparison.

| list (digest words 1,3,4,6) | rand: hits on T / confirmed | ctx: hits on T / confirmed |
|---|---|---|
| D vs 0, rotational/cross-word | 0 / 0 in every statistic | 0 / 0 |
| D vs S, rotational/cross-word | 0 / 0 | 0 / 0 |
| U vs 0 (calibration) | 0 / 0 | 0 / 0 |
| r = 0, i = j (the XOR difference R itself) | mean HW 7 combos, bits 12 combos: R's known bias | same |

**Rotation + constant.** Count of jobs where one V value repeats at least 3 times, over the 3,048 digest D jobs in rand: 4 for D, 3 for S, 5 for U. Chance predicts about 4.0. COMPUTED: no relation B = rotl(A,r) op c.

**Joint test, the same r on all four words.** The statistic is the sum of HW(B_w ^ rotl(A_w, r)).
- rand: for r != 0 the largest |z| is 2.2 on T and nothing is confirmed.
- ctx: the largest |z| is 2.8.
- r = 0 is R itself: mean HW 63.0, and 2^-8.9 of rows have HW <= 44, against 2^-11.9 for uniform words.

**Positive control** (list `plant`: real digest A against a synthetic B; about 25-38 planted rows per half per word, and about 150 for word 6):

| planted relation | how it was found |
|---|---|
| B = rotl(A,5) ^ 12345678 | mode count 37, value 12345678; collision z = 37 |
| B = rotl(A,11) ^ (HW <= 3) | V == 0 at z 11.7 / 9.7 |
| B = rotl(A,7) ^ 33333333 ^ (HW <= 2) | mode 12, value 33333333 |
| B = rotl(A,13) + small | \|V\| <= 256 at z 30 |
| B = rotl(A + 0badcafe, 13) | op r mode 67, value 0badcafe |

All of these were confirmed on V. A relation holding on about 2^-15 of rows or more would have been seen.

**DERIVED, why nothing is expected.** For r != 0:

    B ^ rotl(A,r) = (A ^ rotl(A,r)) ^ R

The map x ^ rotl(x,r) is multiplication by (x^r + 1) = (x+1)^g × (a unit) in GF(2)[x]/(x+1)^32, where g = gcd(r,32). Its image is therefore the subspace of rank 32 - g. When A is uniform and independent of R, V is uniform on a coset that carries only R mod (x+1)^g. For the digest, data against S finds nothing (0 confirmed), so the digest values and R are not linked in any way these statistics can see.

**E1/E3 raw outputs (lists e1, e3).** These show confirmed rotational relations, for example a2_B ^ rotl(d2_A, 8). In e1, 38 of them remain beyond S, for example c2_B ^ d2_A. They are the G-step identities themselves: d2 = ROR(d1 ^ a2, 8) and c2 = c1 + d2, with d1 common and c1 in Q*, which leaves d1 and c1 non-uniform and makes the E1 difference depend on the values. They cancel in the digest, which XORs E1 with E3. The e3 relations at r = 16 come from two things together:
- the low-entropy modular difference of e2 (one value occurs 60 times);
- the map x - rotl(x,16), which takes only about 2^17 values.

S with the modular shuffle reproduces them (D vs S = 0 for op s).

In ctx, the many e3 "bits" hits come from clustering, since there are only 8 contexts per half. The per-bit z-scores assume independent rows, so they are not calibrated in ctx. GUESS: they are cluster artifacts, because rand shows none of them.

## 2. Rotational-XOR relations inside the residual (`rotscan.c` scan WW; `identities.py`; `prefix.py`)

**Statistic.** V = X_j op rotl(X_i, r) inside R, K1, K3, digest A, and RP. RP = (R1, R3, U4, U6).

**Controls:**
- C = column shuffle: one-word marginals kept, cross-word links broken.
- U = uniform words with the same (i, j, r).
- Digest A against U: 0 confirmed. Calibration is good.

**R against C:** 1,163 cross- or self-word relations are confirmed in rand. Every one of the strongest is one of the named coordinates or a rotation of one:

| coordinate | collision pairs per half: data / C / U | H2 | identity |
|---|---|---|---|
| U6 = R6 ^ ROR(R3,8) | 19,233 / 35 / 16 | 22.77 (V 22.76) | E1 only: f(dc2) |
| W4 = R4 ^ ROR(R1,7) | 31,988 / 36 / 36 | 22.03 (V 22.03) | f(da2, df1) |
| W3 = R3 ^ ROL(R6,7) | 5,232 / 19 / 25 | 24.65 (V 24.62) | E3 only: f(de2) |
| U4 = R4 ^ ROR(R1,8) | 30 / 29 / 29 | 32.1 (V 31.5) | E3 only, close to uniform |

All eight identities in the module docstring of `identities.py` hold with 0 failures on rand (1,048,576 rows) and ctx (262,092 rows). The prerequisites also hold: db1 = 18b0e098 and dh1 = eta on every row.

**Zero-prefix profile** (`prefix_out.txt`, rand, T/V). The table gives log2 of the fraction of rows whose low or high m bits are zero. A uniform word gives -m.

| coordinate | measured | uniform |
|---|---|---:|
| W4, low 24 bits | -16.0 | -24 |
| W3, low 20 bits | -15.3 / -15.7 | -20 |
| dc2 ^ eps, high 20 bits | -16.0 | -20 |
| de2 ^ eps, low 21 bits | -15.3 | -21 |
| U6, high 22 bits | -15.7 | -22 |

These tails are where R's deficit lives. Extrapolating to 32 bits would be GUESS. No row has R1, U4, W4, U6 or W3 equal to 0, and no row has dc2 or de2 in {eps, ~eps}. In 2^20 rows, P(each) < about 2^-18.

## 3. Period-4 class decomposition (`classes.py`, `classes_out.txt`)

Class c of a word is its bits c, c+4, ..., c+28. ROR 16, 12 and 8 keep each class. ROR 7 moves class c to class c+1. A carry moves class c to class c+1.

**Rand, T/V. The controls agree:** U gives about 0, and SH = R with columns shuffled.

**Class bytes (8 bits).**
- **R:**
  - Class bytes: deficit 1.565 / 1.570 bits in total.
  - Contiguous bytes: 2.758 / 2.765.
  - The sum of single-bit deficits is 1.565. So inside each word, the class view adds nothing beyond single-bit bias.
- **Per class (summed over the 4 words):**

  | class | deficit (bits) |
  |---:|---:|
  | 0 | 0.58 |
  | 1 | 0.15 |
  | 2 | 0.19 |
  | 3 | 0.65 |

  The largest single cell is word 3, class 3, at 0.385. It includes the known bias at bit 19.

**Class words** (class c over all four words, 32 bits; H2 from collisions; uniform expects 32 pairs per half):

| set | c0 | c1 | c2 | c3 |
|---|---:|---:|---:|---:|
| R | 29.17 | 30.71 | 30.87 | 28.70 |
| SH | 30.93 | 31.68 | 31.51 | 30.96 |
| U | 31.79 | 32.19 | 32.05 | 31.71 |

None is ever zero.

**16-bit partitions** (deficit = 128 - sum of chunk entropies, with the Miller-Madow correction; U baseline 0.018):

| partition | R, T/V | SH, T/V |
|---|---|---|
| class c of words (1,4) and (3,6) | **5.14 / 5.15** | 1.61 |
| class c of words (1,3) and (4,6) | 1.62 | 1.60 |
| contiguous halfwords | 2.84 / 2.85 | 2.85 |
| 24 random partitions | mean 3.28, sd 0.71, max 5.25 (V 5.26) | 1.77 |
| RP coordinates, contiguous halfwords | **7.26 / 7.26** | |

- **Why the class pairing wins.** Pairing words (1,4) and (3,6) wins because ROR 8 keeps the class, and R4 relates to ROR(R1,8) and R6 to ROR(R3,8). In this one respect the period-4 view is the right alignment.
- **Rotation filtration** w mod (x+1)^m, the quotients that commute with every rotation and with XOR:
  - Per word, the deficit is 0 up to m = 13.
  - Jointly over the four words, the deficit is exactly 1.000 bit at m = 1. That bit is the parity relation.
  - Nothing else up to m = 4 (16 bits).
- **Period-4 words** (d4 <= 4):
  - R's counts per word and half are 73-95, against 72-96 for U.
  - Word 6's mean d4 is lower by 0.035 (z -10). SH reproduces this shift, so it is a single-word marginal effect.
- **Period-4 in the differences** (`identities_out.txt`):
  - The constant differences of this family are db1 18b0e098, dc1 0e09818b, de1 03cf8303, eta 830303cf and eps 6e21be55. Their d4 values are 9, 9, 13, 13 and 13.
  - Only the input differences Y3^Y3' = fff8ffff and Y11^Y11' = fff77ffb are close to a period-4 word: they are close to all-ones, at d4 = 3.
  - GUESS: the near-complement inputs fit the ones'-complement lens, where ~x = -x.

## 4. On "a different perspective, like an Archimedean spiral"

A spiral step is a rotation followed by a shift, r -> r + b·theta. The ARX analogue is "rotate, then add or XOR a constant".
- **Between the two sides:** all three forms (rotate then XOR, rotate then add, add then rotate) were tested between A and B for every r. They are absent (section 1).
- **Inside the residual:** the spiral-like structure that does exist is there: rotate by 7 or 8, then XOR a constant (U6, W3, W4). That is exactly the front line's eps/tau/sigma decomposition. GUESS: this view does not yield a further saving. It does make the free parity bit visible.

## Not tested / limits

- **Joint 128-bit entropy and P(R = 0)** cannot be measured from 2^20 rows. Every entropy figure here is a per-coordinate H2 or a chunk-sum estimate.
- **The probability of the eps target** was not measured: P(dc2 = eps) and P(de2 = eps). They need an exact carry calculation, which D5 holds as tables.
- **ctx per-bit z-scores** are not calibrated, because the rows are clustered. The claims rest on rand. ctx is used only to cross-check collision, mode and identity results.
- **Not used:** the d4/ partial constructions, the ones'-complement and modular lenses (other agents), and rotational input pairs (RX pairs into the compression). The front line fixes the pair, so the last of these does not apply.
- **Run note.** Two scan runs overlapped once by mistake. The published `out_*.tsv` files come from a clean single run (`run_out.txt`) of rotscan.c with sha256 prefix 0dd9fefdf3351073.
  - `detcheck.sh` reran ctx, and the two outputs are identical bit for bit. The sha256 prefixes are:

    | file | sha256 prefix |
    |---|---|
    | rand scan | 94ebe3c31ea0ce54 |
    | rand joint | 5b9db49ab1c76528 |
    | ctx scan | fe3e9d51c7b527f5 |
    | ctx joint | 02c6995105ca9a39 |

  - `analyze_out.txt` was regenerated from these files. It matches the earlier analysis line for line.

## Files

- `rotscan.c`, `run.sh`: scans AB, WW and J, run in WSL with gcc -O3 -fopenmp. Output: `out_{rand,ctx}_scan.tsv`, `out_*_joint.tsv`, `run_out.txt`. `detcheck.sh` is the determinism check.
- `analyze.py` -> `analyze_out.txt`: z-scores, the train/test confirmation, mode multiplicities, named coordinates and the joint test.
- `classes.py` -> `classes_out.txt`: period-4 classes, partitions, the filtration and d4.
- `identities.py` -> `identities_out.txt`: exact identities on every row, the eps roots and d4 of the constants.
- `prefix.py` -> `prefix_out.txt`: zero-prefix profiles.
- `explore.py`, `explore2.py`: the first look. They are superseded by the scripts above.
