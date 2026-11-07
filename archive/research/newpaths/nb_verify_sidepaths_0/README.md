# nb_verify_sidepaths_0 - skeptic check of S8 (two blocks, chosen chaining value)

Written 2026-10-08. Research only: no yukon, nothing submitted, no trace, no credential file opened; only my own
processes, each under `timeout`. Tags: COMPUTED (a program here produced it), DERIVED (argument from stated facts),
GUESS.

Claim checked (`..\sidepaths\SIDEPATHS.md` S8, section 6): "Two blocks with a chosen chaining value: dead. The
55/63 trick works in a last block (flags 10, K = cv2 + cv6); the pins are internal values. Under model M the rate
depends only on C3's outputs and the w5 difference, not on the CV; the realizable deviation (the certified
outer-word effect) is about +-8 %." Scoreboard: "<= 0.12 bit". Projected exponent given to me: 92.41.

## Verdict

- **S8 is dead: confirmed, and more strongly than claimed.** The best case is no gain at all: 92.53 (the filed
  64c075ac figure), or 92.54 if the 2^85 preprocessing is actually spent. It is not 92.41.
- First half of the TEST (rate under M does not depend on the CV): **confirmed**, COMPUTED.
- Second half ("realizable deviation is the certified +-8.4 % outer-word effect"): **wrongly cited**. It does not
  change the verdict, but the 0.12 bit has no source. See section 3.

## 1. The 55/63 family in the last block of a two-block message (COMPUTED, `s8_check.py`, `s8_check.txt`)

`build_cv(cv, flags, ...)` is `fam55.build` with v0..v7 = CV, flags 10 (CHUNK_END | ROOT), v8..v11 = IV0..IV3
unchanged, and the pins re-expressed with delta = (cv2 + cv6) - (IV2 + IV6) as X3' = X3 + delta, W4' = W4 - delta.
Then C3's first value is X3' + X7 + W4' = X3 + X7 + W4, and K2's a1 is Q = K + W4' = IV2 + IV6 + W4, as for one block.

| check | result |
|---|---|
| build_cv(IV, 11) == fam55.build | 200/200 |
| two-block pairs (119 / 127 bytes; random 64-byte first block, CV from the 2-round compression with flags 1), digest words 0,2,5,7 equal under the organizer's `verifier/blake3.py` at 2 rounds | **2000/2000** (40 CVs x 50) |
| C3 outputs Y3A Y3B Y7 Y11A Y11B Y15 and dw5 equal to the single-block values (8127c181, 7edf3e7e, 76f7aefd, 7af77f38, 850000c3, bbfbdffe, fffffff8); Y4 = y | **2000/2000** |
| residual (digest XOR on words 1,3,4,6) == F(d1, b1, a2 of E1; Y4, Y9, w8, h1 of E3; Y3A, Y3B, Y11A, Y11B, dw5) - one fixed function with the single-block constants | **2000/2000**, single-block control 500/500 |

So the residual is the same function of the same seven words for every CV. Under M (six words uniform, Y4 uniform
in the sub-class) the rate is the same count, 185,377,197.55 x 2^-128, for every CV. Also DERIVED: every pin
condition depends on (T, Q, X7, X11, X15, W13) only (T = X3 + X7 - K, Q = K + W4), so a CV does not change which
pins exist either. Under M the CV is worth exactly 0.

## 2. Does the CV move anything that can be measured? (COMPUTED, `cvrate.c`, `out\*.txt`)

All eight free words uniform (Y4 uniform in C15), 2^33 trials per configuration: the filed single block (IV,
flags 11), four random CVs (flags 10), and model M itself. The C residual matches the organizer reference on
20/20 printed trials (`check_dbg.py`, `build_out.txt`).

Counts out of 2^33 = 8,589,934,592 trials each (`summary.txt`, from `summarize.py`):

| event | cv_1 | cv_2 | cv_3 | cv_4 | iv (filed) | model M |
|---|---:|---:|---:|---:|---:|---:|
| r1 low 16 bits 0 | 130,089 | 129,523 | 129,281 | 129,652 | 129,637 | 129,828 |
| r3 low 16 bits 0 | 330,422 | 330,396 | 330,155 | 330,835 | 330,656 | 331,245 |
| r4 low 16 bits 0 | 204,710 | 204,932 | 205,493 | 205,700 | 204,693 | 205,296 |
| r6 low 16 bits 0 | 99,725 | 100,500 | 100,298 | 100,038 | 100,547 | 100,085 |
| all four words, low 4 bits 0 | 108,236 | 108,331 | 107,579 | 107,769 | 107,919 | 108,007 |
| six pairs, low 8 bits 0 (e.g. r3 r4) | 351,340 | 352,464 | 351,178 | 351,503 | 352,056 | 350,925 |
| residual weight <= 40 | 700,188 | 699,997 | 701,301 | 700,950 | 699,811 | 701,250 |
| whole word 0 (r1 / r3 / r4 / r6) | 2/7/1/0 | 2/16/3/2 | 3/9/4/2 | 3/10/3/1 | 3/12/4/1 | 1/10/0/2 |
| mean residual weight | 63.65993 | 63.66000 | 63.65992 | 63.65993 | 63.66010 | 63.65992 |

- Each real configuration was compared with the pooled others on 17 events. The largest |z| is 2.45, and that
  comes from a count of 0 to 2, where the normal z is unreliable. On the 2^-16 events it is at most 1.96 (13
  events x 5 configurations). That is noise. Any CV effect on these partial events is below about 1 % (one
  standard error is 0.2-0.3 %).
- Model M agrees with the real messages at the same depth (|z| <= 1.3 on the 2^-16 events). The one "z = -3.9"
  in `summary.txt` is a count of 0 against a mean of 3 (Poisson probability 0.05), an artefact of the z formula.
- The per-word rates are far from uniform (r3 low 16 zero is 2.5 times 2^-16) and identical for every CV. The
  structure comes from the class and C3, not from the CV.

## 3. The "+-8.4 %" in the claim

- The +8.389 % / -8.386 % are the certified extremes of the rate over the 64 settings of a 6-bit cube of u = Y12
  plus all values of v = w5 (`opus_cloud\...\REPORT.md` section 5.2). END_OF_LINE 3.5 and `pkg8\supply\SUPPLY.md`
  say they are **not realizable**: the setting fixes 27 bits of w5 and 6 bits of Y12, and a run then falls 18 to 21
  bits short of the trials it needs. The best realizable target is +0.0495 % (0.0007 bit), and only if v can be
  chosen after the outer step.
- The CV does not touch that channel (DERIVED). u = Y12 = (ROL(Y4, 7) XOR C0.b1) - C0.c1 is fixed by the shape of
  G inside round-1 call C0 (b2 = ROR(b1 XOR c2, 7), c2 = c1 + d2), and v = w5 is a free word in both layouts.
  With any CV, the same bits of u stay constant over the members of an outer step, and in the same share of
  outer steps.
- The 6-bit-cube extreme is also not a bound on deviations in general: the single point u = 0, v = 0 is already
  +27.4 % (0.35 bit; REPORT 4.1: 236,205,900.93 against 185,377,197.55). So "+-8.4 %" is neither what the CV can
  realize nor a ceiling. It is just a number from a different mechanism.
- Arithmetic: log2(1.083888) = 0.1162, so 92.53 - 0.116 = 92.414 is the "92.41". The figure only means something
  if the CV realized the full non-realizable cube extreme, and section 1 shows it realizes nothing under M.

## 4. Other two-block angles tried (DERIVED)

- Different first blocks (A and B with different CVs): a CV difference can be absorbed in round 0 only in K2's a
  input (cv2, by w4), so the CVs would need to agree on 7 of 8 words. Both first blocks are full 64-byte blocks
  (no length difference), and equal-length free half-collisions do not exist (S7/S10). That is a 224-bit
  near-collision: far above 2^92.
- A CV picked to make some E1/E3 input constant: S1's exhaustive word-level search (no residual-side word can
  be a free coordinate) uses only the dependency structure, which the CV does not change. So it holds for every CV.
- Selecting a CV by a proxy: needs a proxy that varies with the CV. Section 2 found none at 2^-16 (and 2^-32
  where counts allow). GUESS: none exists, because the residual is the same function of the seven words.

## 5. Limits

- Nothing here measures anything at 2^-100.5. Section 2 is a 2^-16 / 2^-32 check over the whole free space, not
  over the algorithm's structured run (outer steps, X2, members).
- M is assumed, not shown (as in every entry). "CV worth 0" is exact under M. Beyond M it is measured only as
  far as section 2 goes.

## Files

`s8_check.py` + `s8_check.txt` (two-block family, organizer reference), `cvrate.c` + `build.sh` + `runs.sh`
(statistics), `check_dbg.py` + `build_out.txt` (C vs reference), `out\` (run outputs).
