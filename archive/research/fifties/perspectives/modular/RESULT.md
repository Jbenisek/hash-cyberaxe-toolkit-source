# Modular lens on the front-line residual: RESULT

2026-10-09 20:05. Labels: **COMPUTED** = measured by the code in this folder; **DERIVED** = algebra; **GUESS** = not verified.
Data: `../data` (rand 2^20 rows, ctx 2^18 rows), read-only, plus two fresh GPU runs of 2^39 samples each (`tower.cu`).
Every statistic is compared with a uniform-random CONTROL of the same shape. Anything picked on the TRAIN half
(rand rows [0, 2^19)) is re-measured on the TEST half ([2^19, 2^20)), and on ctx/ as a third set. The two GPU runs
use different seeds and act as train and test.

Notation, for each residual word w in (1,3,4,6): R = digA XOR digB (stored); Rm = digA - digB mod 2^32;
K1/K3 are the XOR E-parts; M1/M3 are the modular E-parts (E1A - E1B and E3A - E3B on the same output words).

## Answer

1. **The modular view does not lower the effective entropy of the residual.**
   - **DERIVED:** R = 0 ⇔ Rm = 0. More generally, the low k bits of R are zero ⇔ Rm ≡ 0 mod 2^k, for every k.
   - **COMPUTED:** both equivalences hold on every rand and ctx row.
   - So P(collision) is the same in every coordinate system. A coordinate can only change how the structure looks or how it is estimated, never the target probability.
2. **In modular coordinates the residual is flatter than in XOR coordinates (COMPUTED).**
   - Single-bit biases almost disappear. Word 3 has XOR bias 0.33 but modular bias 0.029.
   - Per-word collision entropy is higher: 125.3 bits over the four words, against 123.0 for XOR.
   - The low-bit entropy deficits are smaller.
   - The heavy low-weight tail of XOR shrinks under NAF.
3. **The modular parts do not combine (DERIVED + COMPUTED).**
   - Rm − M1 − M3 = −2[(xA & yA) − (xB & yB)].
   - So the modular split holds only mod 2. It is exact on 0 to 5 rows in 2^20.
   - Rm is not a function of (M1, M3): all 88 word-3 rows that share (M1, M3) with another row have a different Rm.
   - XOR is the only one of the three coordinate systems in which the residual splits exactly (R = K1 ⊕ K3), so it stays the coordinate system for matching E1 against E3.
4. **The 2-adic tower measures the effective bits per word (COMPUTED, 2 × 2^39 GPU samples).** The tower is the modular filtration Z/2^k and is coordinate-free. The cost of each full word, as −log2 P(R_w = 0), is:

   | word | bits |
   |---|---:|
   | 1 | 31.76 |
   | 3 | 28.62 |
   | 4 | 31.98 |
   | 6 | 32.20 |

   - The sum is **124.55 bits**, if the words are independent (GUESS).
   - Two exact GF(2) relations hold on every row and are satisfied by R = 0 (§9). They should take about 2 more bits off (GUESS, ~122.5).
   - Pair dependence on the low bits runs from −2.4 to +4.0 bits by k = 18 and is still moving, and the joint of all four words is measured only up to 36 bits. The four-word figure is therefore not pinned: GUESS range 118 to 127.
5. **The strongest structure in this lens is a modular near-cancellation in word 3 (COMPUTED + DERIVED).**
   - E1 receives the constant modular input difference Δc1 = 0xf5f77e75 (A−B). E3 receives Δe1 = 0x02488303.
   - Their sum is 0xf8400178 ≡ **376 (mod 2^20)**. As a fraction of 2^20 that is 0.00036, where a random value would sit at 0.25 on average.
   - Word 3 is the only word whose two outputs both carry these constants additively: c2 = c1 + d2 and e2 = e1 + f1 + w8.
   - The other two terms, Δd2 and Δf1, each sit near 2^19 mod 2^20, so they also cancel mod 2^20.
   - **Result:** Rm3 mod 2^20 lies within 1/16 of 0 with probability 0.403 (train) / 0.403 (test) / 0.408 (ctx), against 0.125 for uniform. The character |E exp(2πi·Rm3/2^20)| is 0.567 (train), 0.569 (test) and 0.574 (ctx), against a control maximum of 0.005.
   - This is the modular mechanism behind the XOR bit-19 bias and behind word 3's 3.4-bit saving. It does not reach beyond bit 20: Δc1 + Δe1 is ordinary mod 2^24 and 2^28.
6. **Inside the halves, modular differences are more concentrated for some words, but XOR has more exact structure (COMPUTED).**
   - Collision entropies, modular against XOR:

     | word | modular | XOR |
     |---|---:|---:|
     | M1 word 1 (a2) | 11.00 (exactly 2^11 equally likely values) | 14.24 |
     | M1 word 3 (c2) | 15.78 | 22.76 |
     | M3 word 3 (e2) | 16.86 | 24.64 |

   - Exact linear structure:

     | coordinates | E1 part | E3 part | total |
     |---|---:|---:|---:|
     | XOR (GF(2) relations) | K1: 69 | K3: 35 | 104 |
     | modular (Z/2^32 module index, bits) | M1: 36 | M3: 1 | 37 |

**Exploitable?** The modular lens finds nothing new to exploit in the residual check. Three leads, all GUESS:
- (a) Re-tune the constants. Word 3's saving comes from Δc1 + Δe1 ≡ 376 mod 2^20, and both constants are fixed by the round-2 column-G differential of (W4 → W4', 55 → 63). A constants search that makes this sum agree 2-adically in more bits might lower word 3 further, but its effect on the other words is unknown.
- (b) Filter on b1's signs. Pinning the 11 sign bits of b1 (11 bits of b1A, which are a function of context and j) fixes Δmod a2. About 7.8 bits of carry entropy then remain in K1 word 1 (H(K|M) = 7.80, against H(K) = 15.48). On the test half, P(K1w1 = d | m) gained 2.8 to 5.1 bits for 4 of the 5 most likely keys d, but this rests on about 250 rows per m and is noisy.
- (c) Check the XOR accounting. The two exact XOR relations of §9 give 2 free bits for the zero target. It is worth checking whether the front line's accounting already uses them; that belongs to the XOR lens.

## 1. Identities (COMPUTED on every rand and ctx row; DERIVED where stated)
- **The zero sets agree.**
  - R == 0 ⇔ Rm == 0, per word.
  - The low-k zero sets of R and Rm are equal for every k < 32.
  - lsb(R) = lsb(Rm).
- **The splits.**
  - R = K1 ^ K3 holds exactly.
  - Rm ≡ M1 + M3 (mod 2) holds on every row, and no higher power of 2 holds on every row.
- **M1 word 1 ≡ 0 mod 16 (DERIVED).** Δ⊕b1 = 18b0e098 is constant, so Δmod b1 ≡ ±8 (mod 16). Then Δmod a2 = Δmod b1 + 8.

## 2. Residual per word, XOR against modular against control (`modstats_out.txt` §1-4)

"Max bias" is \|P(bit)−½\|: the bit is chosen on the train half, and the value is re-measured on the test half. "Deficit" is Σ(1−h(p_b)).

| view | word | H2 (pairs) | max bias train→test (bit) | independent-bit deficit |
|---|---|---:|---|---:|
| R | 1 | 31.39 | 0.2037→0.2032 (b0) | 0.185 |
| R | 3 | 29.59 | 0.3300→0.3308 (b19) | 0.784 |
| R | 4 | 31.60 | 0.1526→0.1523 (b25) | 0.125 |
| R | 6 | 30.43 | 0.2506→0.2512 (b11) | 0.474 |
| Rm | 1 | 31.71 | 0.2037→0.2032 (b0) | 0.123 |
| Rm | 3 | 30.25 | 0.0288→0.0276 (b2) | 0.003 |
| Rm | 4 | 31.98 | 0.0223→0.0210 (b4) | 0.001 |
| Rm | 6 | 31.34 | 0.0200→0.0187 (b4) | 0.001 |
| control | 1..6 | 31.86..32.02 | ≤0.0020→≤0.0007 | 0.000 |

- **H2 estimates.** The noise is about ±0.13 bits per word (Poisson on about 130 to 700 colliding pairs).
- **H2 of the low 20 bits (test half):**

  | word | R | Rm | control |
  |---|---:|---:|---:|
  | 1 | 19.58 | 19.64 | 20.00 |
  | 3 | 17.95 | 18.42 | 20.00 |
  | 4 | 19.78 | 19.84 | 20.00 |
  | 6 | 18.89 | 19.32 | 20.00 |

  XOR is the more concentrated of the two on every word.
- **Signed-digit form.**
  - Mean NAF(Rm) per word is 10.80, 10.20, 10.74 and 10.72, against 10.78 for the control. Word 3 is the only one that differs.
  - On the 128-bit total, NAF(Rm) has mean 42.46 and minimum 23, against a control mean of 43.11 and minimum 27.
  - XOR HW(R) has mean 63.01 and minimum 32, against a control mean of 64.01 and minimum 38.
  - Tail ratios against control: P(HW ≤ 40) is 20.6×, while P(NAF ≤ 28) is 6.0×.
  - NAF ≤ HW on every row (DERIVED: the signed XOR difference is itself a signed-digit form of Rm).
- **Signed magnitude.** Word 3 avoids small \|Rm\|: P(\|Rm3\| < 2^28) = 0.085, against 0.125. Words 1, 4 and 6 match uniform at the coarse scale.

## 3. Modular characters (Fourier over Z/2^k) against XOR characters (Walsh) (`modfourier_out.txt`)

- **Single word, low 20 bits.** These spectra are exact.
  - The control maximum over all 2^20 coefficients is about 0.005.
  - In every case the train peak is reproduced on test and on ctx to within about 0.01 (ctx up to 0.03).

  | word | strongest modular character (train / test / ctx) | strongest XOR Walsh coefficient |
  |---|---|---|
  | 3 | exp(2πi x/2^20): 0.567 / 0.569 / 0.574 | bit 19: 0.66 |
  | 1 | parity (bit 0): 0.407 | the same |
  | 6 | exp(2πi x/2^12): 0.396 | 0.50 |
  | 4 | exp(2πi x/2^5): 0.234 | 0.28 |

- **Count of test coefficients above twice the control maximum:**

  | word | modular | XOR |
  |---|---:|---:|
  | 3 | 372 | 359 |
  | 6 | 50 | 100 |
  | 1 | 11 | 9 |
  | 4 | 6 | 4 |

  The two views carry the same structure; neither shows clearly more.
- **Pairs of words**, with (Z/1024)^2 on the low 10 or top 10 bits of each word, and **all four words**, with (Z/32)^4 on 5 bits each:
  - Every peak is reproduced on test and ctx.
  - No pair or 4-word modular character exceeds the strongest single-word one.
  - Top 5 bits of the 4 words: modular has 4 significant coefficients, XOR has 25.
- **Low-frequency characters** (small c, the signed size of x), re-checked exactly on the full 32-bit word:

  | word | c | value |
  |---|---:|---:|
  | 3 | −4096 | 0.569 |
  | 6 | 16384 | 0.172 |
  | 4 | −64 | 0.142 |
  | 1 | −256 | 0.096 |

## 4. Rank of the low k bits; modules (`modextra_out.txt` G, `modfourier_out.txt` F, `modverify_out.txt`)

**GF(2) affine rank of the low k bits.** Each cell is rank / full; the rows are XORed against row 0, on 4,096 rows.

| k | R | Rm (as bits) | K1 | K3 | M1 | M3 | control |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 32/32 | 32/32 | 26/32 | 31/32 | 24/32 | 31/32 | 32/32 |
| 16 | 64/64 | 64/64 | 42/64 | 55/64 | 48/64 | 62/64 | 64/64 |
| 24 | 96/96 | 96/96 | 58/96 | 78/96 | 70/96 | 94/96 | 96/96 |
| 32 | **126/128** | 128/128 | 59/128 | 93/128 | 89/128 | 126/128 | 128/128 |

**Z/2^32 module of the affine row differences.**

| vectors | module | relations |
|---|---|---|
| Rm | full: no affine relation over Z/2^32 (5 rows suffice; same on ctx) | none |
| M1 | index 36 bits | M1.w1 ≡ 0 (mod 16); M1.w3 − M1.w4 = 0xf5f77e75 = Δc1 (DERIVED: c2 = c1 + d2) |
| M3 | index 1 bit | lsb(Δg2) ⊕ lsb(Δh2) = 1 (DERIVED: g1 = Y9 + h1, so lsb Δg1 = lsb eta = 1) |

All three relations were found on at most 4,096 rows and then hold on every rand and ctx row (COMPUTED).

## 5. Do modular residuals of the E1 and E3 parts combine more simply than XOR? No.

- **DERIVED:** x ^ y = x + y − 2(x & y), so Rm_w = M1_w + M3_w − 2[(xA & yA) − (xB & yB)].
- **COMPUTED (`modstats_out.txt` §6):**

  | word | P(Rm == M1 + M3) | mean 2-adic valuation of the error (control 2.66) |
  |---|---:|---:|
  | 1 | 0 | 3.25 |
  | 3 | 9.5e-7 | 2.34 |
  | 4 | 1.9e-6 | 3.11 |
  | 6 | 0 | 2.71 |

- P(Rm == M1 − M3) is at most 4.8e-6.
- The 88 word-3 rows that share (M1, M3) with another row all have a different Rm.
- There is therefore no modular MITM key. The meet-in-the-middle has to stay in XOR, on K1 = K3.

## 6. The E-part differences in three coordinates (`modstats_out.txt` §7)

H2 in bits on all rand rows; "const" means one value on every row. BSD = signed bit difference, that is, the XOR pattern plus the signs.

| value | XOR | MOD | BSD |
|---|---|---|---|
| E1.b1 | const 18b0e098 | 11.00 (2^11 equally likely) | 11.00 |
| E1.c1 | const 0e09818b | const f5f77e75 | const |
| E3.e1 | const 03cf8303 | const 02488303 | const |
| E3.h1 | const 830303cf (eta) | 12.00 | 13.00 |
| E3.f1 / g1 | 14.30 / 14.30 | 16.86 / 12.00 | 23.31 / 22.55 |
| a2 (w1) | 14.24 | **11.00** | 21.04 |
| c2 (w3) | 22.76 | **15.78** | 29.18 |
| d2 (w4) | **14.24** | 15.78 | 22.35 |
| b2 (w6) | **22.76** | 26.59 | 35.68 |
| e2 (w3) | 24.64 | **16.86** | 30.93 |
| f2 (w4) | 31.75 | 31.76 | — |
| g2 (w1) | 31.30 | 30.93 | 39.0 |
| h2 (w6) | **24.64** | 29.50 | 39.0 |

Plug-in conditional entropies on the test half:

| word | H(K) | H(M) | H(K\|M) | H(M\|K) |
|---|---:|---:|---:|---:|
| E1 word 1 | 15.48 | 11.00 | 7.80 | 3.32 |
| E1 word 3 | — | — | 2.07 | — |
| E3 word 3 | — | — | 1.56 | — |

Word 6 and E3 words 1 and 4 are essentially in one-to-one correspondence between the two views, with less than 0.1 bit either way.

## 7. The 2-adic tower (GPU, `tower.cu`, `tower_analyze_out.txt`)

**Method.**
- `tower.cu` evaluates the same algebra as `../data/gen.c`: step CO, then step CT, then the E1 and E3 diagonal G of both blocks, starting from the predicted Y state.
- The predicted Y state is what gen.c checks against the full compression on every row.
- **Exactness (COMPUTED).** The host path and the GPU path both reproduce t, both digests and R on all 1,048,576 rand rows and all 262,144 ctx rows, with 0 mismatches.
- **Samples.** Each run draws fresh uniform outer words, k and j for every sample, from a counter-based splitmix: 2^39 per seed, two seeds, about 110 s each on the RTX 3090. Only 120 and 148 samples had t = 0.

**Per word**, −log2 P(R_w ≡ 0 mod 2^k), shown as A / B:

| k | w1 | w3 | w4 | w6 |
|---:|---|---|---|---|
| 8 | 8.75/8.75 | 7.14/7.14 | 7.25/7.25 | 9.10/9.10 |
| 16 | 16.05/16.05 | 14.55/14.55 | 15.25/15.25 | 16.19/16.19 |
| 20 | 20.05/20.05 | 16.58/16.58 | 19.26/19.26 | 19.65/19.65 |
| 24 | 23.77/23.76 | 20.58/20.58 | 23.25/23.27 | 23.97/23.96 |
| 28 | 27.77/27.75 | 23.93/23.93 | 27.84/27.89 | 28.27/28.32 |
| 32 (zero word) | 31.69/31.83 | 28.64/28.61 | 31.83/32.14 | 32.22/32.18 |

Pooled full-word costs, with 95% intervals:

| word | bits | 95% interval | zeros in 2^40 |
|---|---:|---|---:|
| 1 | 31.76 | 31.60..31.93 | 303 |
| 3 | 28.62 | 28.57..28.68 | 2,663 |
| 4 | 31.98 | 31.81..32.16 | 260 |
| 6 | 32.20 | 32.02..32.40 | 223 |

**Cost per 2-adic level.** The cost of one level is −log2 P(bit k = 0 | bits < k are 0), and is 1.00 for uniform bits. Most levels cost exactly 1.00. The cheap ones are:
- Word 3: levels 2 (0.46), 4 (0.43), 11 (0.59), 12 (0.21), 17 (0.74), 18 (0.22), **19 (0.06)** and 25 (0.34).
- Word 6: levels 11 (0.09) and 17 (0.46).
- Word 1: levels 11 (0.30), 23 (0.72) and 30 (0.83).
- Word 4: level 4 (0.25).

The expensive ones are:
- Word 1: level 0 (1.75).
- Word 3: levels 3 (1.25), 10 (1.28), 15 (1.33) and 31 (1.71).
- Word 4: level 25 (1.63).
- Word 6: levels 4 (2.21), 23 (1.32) and 24 (1.35).

**Joint behaviour.**
- **All four words ≡ 0 mod 2^k** match the product of the per-word marginals to within 0.05 bits for k ≤ 7, and to within 0.3 to 0.44 bits at k = 8 (89 and 80 events). Beyond 36 bits there are too few events.
- **Pairs.** Each entry is the excess in bits over the product of marginals, A/B; a positive excess means the pair helps.

  | pair | k = 16 | k = 18 |
  |---|---|---|
  | w1, w4 | +2.70/+2.71 | +3.94/+3.97 |
  | w1, w6 | +0.85/+0.96 | — |
  | w4, w6 | +1.05/+1.00 | — |
  | w1, w3 | +0.29/+0.40 | — |
  | w3, w4 | +0.08/+0.04 | — |
  | w3, w6 | **−2.30/−2.40** | — |

  The pair dependence grows with k, so the full-word joint cannot be pinned from these runs.
- **The capped joint tz vector** is far from a product (χ² z ≈ 3.8e6 in both runs). The words are dependent in detail, even where the all-zero tails match.

## 8. Word 3, the modular mechanism (`modrel_out.txt` K)

- **The input constants.** Δc1 + Δe1 = 0xf8400178. Reduced mod 2^k this gives:

  | modulus | residue |
  |---|---:|
  | 2^12 | +376 |
  | 2^16 | +376 |
  | 2^20 | +376 |
  | 2^24 | 4,194,680 (ordinary) |
  | 2^32 | −130,023,048 |

- **The identity.** M1.w3 + M3.w3 = (Δc1 + Δe1) + Δd2 + Δf1. This is DERIVED, and COMPUTED to hold on every row.
- **Δd2 and Δf1 mod 2^20.** Each sits near the half point, with median \|signed residue\|/2^20 of 0.46 and 0.49. Their sum sits near 0, with median 0.039 and P(< 1/64) = 0.150, against 0.031 for uniform.
- **Effect on the zero probability of word 3:**

  | event | probability |
  |---|---:|
  | R3 ≡ 0 mod 2^16, given \|M1+M3 mod 2^16\| < 2^12 | 1.11e-4 |
  | R3 ≡ 0 mod 2^16, otherwise | 3.13e-5 |
  | R3 ≡ 0 mod 2^16, uniform | 1.53e-5 |

## 9. Side finding (XOR, exact): two GF(2) relations of R, both satisfied by R = 0 (`modrel_out.txt` J)
- **The relations.**
  - Relation 1: parity(R3 bits 0-7) ⊕ R4.b25 ⊕ R6.b0 ⊕ parity(R6 bits 25-31) = 0.
  - Relation 2: parity(R3 bits 8-31) ⊕ R4.b25 ⊕ parity(R6 bits 1-24) = 0.
- **COMPUTED:** they were found on 4,096 rows and then hold on all 1,048,576 rand rows and all 262,144 ctx rows. Rm has no such relation.
- **DERIVED:** their sum is parity(R3) ⊕ parity(R6) = 0.
  - R6 = ROR(Δb1 ⊕ K1_3, 7) ⊕ ROR(eta ⊕ K3_3, 8), where HW(Δb1 = 18b0e098) = 11 and HW(eta = 830303cf) = 13.
  - The two odd weights cancel, which gives the sum.
  - The split into two relations is COMPUTED only.
- **Consequence:** R lives in a 126-dimensional GF(2) subspace that contains 0.

## 10. What was not tested
- **Compression level only.** All pairs are compression-level, as stated in `../data/DATA.md` §4. The organizer's whole-message `blake3()` was not run.
- **Unconditioned members.** The front line's gate, T1/T2 and joint-root conditioning were not applied, so the numbers are for unconditioned members of the family. They are not the D5 table's (t,s)-conditioned P_joint of 2^-100.5, and the two should not be compared directly.
- **Joint probabilities.** The full-word joint of two or more words was not measured: about 2^60 or more would be needed. The four-word joint is measured only up to 36 bits, so the four-word effective-bit figure rests on the independence GUESS.
- **Plug-in entropies** in `modextra` I are biased low near saturation, and the pinning gains in lead (b) rest on about 250 test rows per modular value.
- **Other lenses.** The ones'-complement and rotation-period-4 views are other lenses and were not covered here.

## Files (all in this folder)

| file | role |
|---|---|
| `modstats.py` → `modstats_out.txt` | identities, per-word bias and entropy, NAF, magnitude, low/top-k entropy, split test, E-parts in three coordinates |
| `modfourier.py` → `modfourier_out.txt` | modular and Walsh spectra (single word, pairs, 4 words), low-frequency exact check, Z/2^32 module |
| `modextra.py` → `modextra_out.txt` | GF(2) rank of the low k bits, location of the strongest character, sign against carry |
| `modrel.py` → `modrel_out.txt` | the two exact XOR relations; the word-3 near-cancellation |
| `modverify.py` → `modverify_out.txt` | module relations checked on every row |
| `tower.cu`, `build_tower.sh`, `run_tower.sh`, `run_tower_big.sh` | GPU 2-adic tower, with exactness check against the stored rows |
| `tower_trainA.txt`, `tower_testB.txt`, `tower_t30.txt` | raw tower counts |
| `tower_analyze.py` → `tower_analyze_out.txt` | tower analysis |

**Rebuild:** `wsl -d Ubuntu -- bash build_tower.sh`, then `run_tower_big.sh` (about 4 minutes), then the Python scripts (each under 2 minutes).
