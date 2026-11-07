# Lens: ones'-complement (Z/(2^32-1)) view of the front-line residual

2026-10-09, 19:44 to 20:12 MDT. Labels: **COMPUTED** = measured by code in this folder; **DERIVED** = algebra; **GUESS** = not verified.
Data: `../data` (pkgCG front-line pairs, read-only). Fresh pairs come from `oc_stream.c`. It uses the same sampler as `data/gen.c`, and its counts match numpy on rand rows 1..65,536 exactly (0 of 312 count blocks differ).

## Answer

**No, on both counts.** In ones'-complement coordinates the residual does not have less than 128 bits of effective entropy, and it shows no exploitable structure. It actually shows *less* structure than the XOR view does:
- The XOR view's 16 most-biased residual bits give **+8.2 bits** of lean toward zero on a 16-bit condition.
- The best ones'-complement condition, word 3 mod 65537, gives **+0.10 bits** on a 16-bit condition. A shuffled-residual surrogate reproduces that +0.10, so it is the XOR residual's own bias seen through a different map.
- Everything else sits within ±0.002 bit of uniform.

| question | result |
|---|---|
| Does the zero event get likelier in another coordinate system? | **DERIVED: no, never.** dA ≡ dB (mod 2^32-1) holds exactly when dA = dB, or when {dA, dB} = {0, 0xFFFFFFFF}. So the probability that the residual is zero, -log2 P(R=0), is the same number in every coordinate system. Changing coordinates can only help in two ways: (a) give a necessary condition φ(D)=φ(0) that holds more often than chance, a filter; or (b) split D into separately searchable parts, for a meet-in-the-middle. Both are tested below. |
| (a) Does D lean toward 0 in a quotient mod 3, 5, 15, 17, 255 or 257? | **COMPUTED: no.** I compared 2^29 front-line pairs with 2^29 control pairs. Per word and modulus, the zero-residue advantage is between -0.0009 and +0.0011 bits, with s.e. 0.0002 to 0.0014. Over all 4 words jointly: mod 3 -0.0003±0.0008, mod 5 -0.003±0.002, mod 15 +0.015±0.020, mod 17 +0.05±0.026. The mod-17 value is +0.105 on stream 1, but it was **not replicated** on stream 2 (-0.001±0.036). |
| (a) Is there a lean toward 0 mod 65535 or 65537? | **COMPUTED: in word 3 only.** Pooled: +0.092±0.022 (mod 65535) and +0.098±0.022 (mod 65537). The surrogate S gives +0.076 and +0.123, so this is the XOR residual's own word-3 bias. Words 1, 4 and 6 show nothing (\|adv\| < 0.03 ± 0.023). |
| Does the residual concentrate on few residues of 2^32-1 (multiplicative structure)? | **COMPUTED: no.** These all match the control: the divisibility pattern of D by 3·5·17·257·65537, the cosets of <2> and <16> (rotations, and rotations by multiples of 4) in (Z/p)* for p = 17, 257, 65537, and membership in the period-4 and period-8 subgroups. On 2^28 pairs the period-4 counts per word are 0, 2, 0, 1 against 0.94 expected, and the period-8 counts are 12, 28, 21, 19 against 15.9. The one exception is word 3's mod-65537 cosets, which the surrogate explains. |
| (b) Do the E1 and E3 parts combine additively in this view? | **No.** DERIVED: x^y = x + y - 2(x&y), so D = δ(E1 part) + δ(E3 part) + ε with ε = -2[(x&y) - (x'&y')]. COMPUTED: that identity holds on every TRAIN row. The cross term ε carries **28.0 to 29.5 bits** (Rényi-2) per word; P(ε = 0) is about 2^-19 to 2^-20; and ε mod 3, 5, 15, 17 cannot be told apart from control ε. There is no additive split. |
| Are any two residual words on the same rotation ("spiral") orbit, D_j = ±2^r·D_i? | **COMPUTED: no.** 0 hits in 2^20 rows for each of the 6 word pairs, against about 0.016 expected per pair. A positive control proves the test works: inside E1, oc-diff(d2) = 2^-8·oc-diff(a2) holds in 329 of 2^19 rows. The ratio D_j/D_i is also uniform across its <2>/<16> cosets (36 tests, none below Bonferroni). |

## Why the ones'-complement view hides structure instead of revealing it (DERIVED, checked by the surrogate)

D = dA - dB = Σ over bits k with R_k = 1 of (2·dA_k - 1)·2^k.

Each flipped bit enters with a sign set by the data bit dA_k, which is close to a fair coin. For a character of Z/p this gives |E χ(D)| ≤ E Π_{k∈R} |cos(2π t 2^k / p)|. With residual weights of 15 to 16:
- For p = 3, 5 and 17 the product is at most about 2^-10 to 2^-15. The XOR bit biases (up to 0.33) are washed out.
- Only for p = 257 and 65537 do the low bits of each 8-bit or 16-bit lane barely move the residue (2^k/p ≈ 0 for small k mod 16). That is why the only D signal is in the mod-65535 and mod-65537 components.

COMPUTED check: the surrogate S keeps R's exact joint distribution but takes dA from another row. It reproduces the word-3 mod-65535/65537 KL (0.00479 vs 0.00498 bits per row, the same on both streams). The remaining 0.0002 bits per row is the only coupling between dA and R visible in this view. It reproduces on both streams, and it is negligible.

## Which coordinates are cheapest for each G output (COMPUTED, Rényi-2 bits of the A-B difference, 2^19 rows; TEST agrees to 0.1)

| value | XOR | mod 2^32 | ones' mod 2^32-1 |
|---|---:|---:|---:|
| E1 b1 (half G) | const 18b0e098 | 11.00 | 11.00 |
| E1 c1 | const | const f5f77e75 | const f5f77e74 |
| E3 f1 | 14.29 | 16.86 | 16.94 |
| E3 g1 | 14.29 | 12.00 | 13.00 |
| E3 h1 | const (eta) | 12.00 | 13.00 |
| E1 a2 (word 1 part) | 14.24 | **11.00** | 11.18 |
| E1 c2 (word 3 part) | 22.77 | **15.79** | 16.15 |
| E1 d2 (word 4 part) | **14.24** | 15.79 | 16.52 |
| E1 b2 (word 6 part) | **22.77** | 26.56 | 26.60 |
| E3 e2 (word 3 part) | 24.65 | **16.86** | 17.12 |
| E3 h2 (word 6 part) | **24.65** | 29.39 | 29.72 |
| E3 f2, g2 | about 31.5 | about 31.5 | about 31.5 |
| residual words 1/3/4/6 | 31.5 / 29.6 / 32.2 / 30.5 | 31.9 / 30.2 / 31.9 / 31.5 | 32.0 / 30.2 / 31.9 / 31.6 |

Reading the table:
- **Ones'-complement is never cheaper than mod 2^32.** The end-around carry adds 0 to 1 bit (exactly 1 bit on E3 g1 and h1, 4,096 → 8,192 values). DERIVED: x ⊞ y ≡ x + y - carry (mod 2^32-1), and the carry is close to a fair coin (COMPUTED 0.5001).
- **Where a sum is cheaper than XOR, the plain modular view gets there first.** Word 3's two parts cost 15.8 and 16.9 bits in the modular view, against 22.8 and 24.7 in XOR, but they still combine by XOR.
- **The XOR combination re-injects about 28 bits per word.** The residual is 30 to 32 bits in all three views.

GUESS, pointer for the modular lens, not followed here: the word-3 gap of about 7 bits per side is the only place a non-XOR view is much cheaper.

## Period-4 and the "spiral" perspective (DERIVED, numerically checked in `identities_out.txt`)

- ROR by r is exactly multiplication by 2^(32-r) mod 2^32-1.
- The period-4 words k·0x11111111 are the subgroup of order 15. Quotienting by them gives x mod 15, which is the sum of nibbles mod 15. In that coordinate, ROR 16, 12 and 8 are the identity and ROR 7 is ×2.
- So "period-4 invariance" is exactly the ones'-complement quotient mod 15 (with mod 3 and mod 5 inside it). COMPUTED: the residual is flat there, per word and jointly.
- The spiral picture fits this view:
  - Rotation moves a word along a geometric orbit x·2^r. That is a logarithmic spiral, a constant ratio per step.
  - Repeated modular addition x + k·c is the Archimedean spiral, a constant step.
  - XOR follows neither spiral. Each XOR adds a full-width cross term -2(x&y), and that cross term is the ε measured above.
  - The residual words do not share spiral orbits (no rows with D_j = ±2^r·D_i).

## Method and controls

- **Quantities**, per residual word:
  - D = oc(dA) - oc(dB) mod 2^32-1, the primary one.
  - R read as an element of Z/M.
  - ε, the split remainder.
  - S, the surrogate (R from another row). S is never tested on its own; it is used for comparison.
- **Test family:** 516 two-sample tests (`oclib.py`), run against a **control stream** of 2^28 pairs whose 16 final-state words are uniform. The control goes through the same code path. This control is needed because ε is not uniform even for uniform words. My first run tested against an exact uniform distribution, and it flagged 16 ε tests on pure random data. The control fixes that.
- **Calibration:** 2^19 numpy-uniform rows against the control stream: 6 tests below 0.01 (5.2 expected) and 1 below Bonferroni. That one is E word 6's 32-cell divisibility pattern at p = 6.4e-6. I GUESS the cause is sparse cells, where the chi-square approximation is loose.
- **Train/test:**
  - Hypotheses were picked on TRAIN only: rand rows 0 to 2^19, 20 flagged.
  - They were re-tested on TEST (the other half), CTX and STREAM 1 (2^28 fresh pairs). 18 of 20 confirmed everywhere; 2 failed only on CTX (2^18 rows) and are significant on the stream.
  - All 96 tests that are Bonferroni-significant on STREAM 1 replicate on STREAM 2 (another 2^28 pairs, against a second control).
  - Of the 96, 78 are ε structure, 13 are R's XOR bits read mod 65537, and 5 are D word 3, which the surrogate explains.
- **Pre-registration (`prereg.json`) and my mistake:**
  - The two joint-zero leans pre-registered from stream 1 (mod 15, mod 17) did **not** replicate.
  - The word-3 entries in `prereg.json` used the wrong key: index w3, which is word 6, instead of w1, which is word 3. So the word-6 tests pre-registered there correctly came out null.
  - The intended word-3 tests were run afterwards on stream 2: mod 65537 one-sided p = 1.6e-5, replicated; mod 65535 p = 0.043. These are not formally pre-registered. The surrogate shows the same effect.

## Not tested / limits

- The D4 partial records (`data/d4`) were not analysed. They are not the front-line residual, and 1,577 rows cannot detect effects the size of those seen here (at most 0.1 bit).
- Joint 4-word distributions are measured only for moduli 3, 5, 15 and 17. Larger joint quotients, such as 255^4 cells, are out of reach of 2^29 pairs.
- ε was characterised only by its residues and entropy. It was not modelled as a function of a few input bits.
- The pairs are compression-level only, as in DATA.md.
- The GPU was not used. Each 2^28-pair stream took 2 to 11 minutes on 4 CPU threads, and the work is histogram-bound.

## Files (all in this folder)

- `oclib.py`: shared code. It defines the quantities, the count layout, the two-sample test family and the dlog/coset tables.
- `oc_stream.c`: the streaming sampler plus counts (modes `real` and `ctrl`; OpenMP).
- `build_check.sh`: builds the sampler and runs the reproduction check.
- `run_stream.sh`, `run_stream2.sh`: the two stream runs.
- `analyze.py` → `analyze_out.txt`: the train/test/ctx/stream analysis, sections 1 to 6. It also writes `flagged.json` and `counts_*.npz`.
- `replicate.py` → `replicate_out.txt`: the stream-2 replication, the pooled leans toward zero, and the prereg key error.
- `identities.py` → `identities_out.txt`: numeric checks of the DERIVED identities.
- `prereg.json`.
- `stream*_2p28.bin` and `check_real_65536.bin`: raw counts, 28 MB each. Rebuild them with the `.sh` scripts in about 2 to 11 minutes (seeds are fixed).
