# Front-line residual samples (perspectives/data)

2026-10-09 19:43. Labels: COMPUTED = measured by the code here; DERIVED = algebra; GUESS = unverified.
Size about 366 MB. All of it can be rebuilt in about 50 s with `build.sh`, because the seeds are fixed.

## Source of the pairs

These are genuine front-line pairs from the pkgCG family (a402a477, 63.9522). They are built by
`research/tools/build_pkg/scratch/pkgCG/pkg/blake3-r2/experiments/frontline.py`. Its sha256 prefix is 5936cfad516e9ede, and
`research/frontline/program/frontline.py` has the same bytes. The pairs come from step CO (its 77 lines) followed by step CT. The algebra is the same as
`pkg13/mitm/check.py` (halfsearch ctr_outer/ctr_trial). One difference: this family's Y4 class has 19 free bits, while halfsearch's sub-class has 17.

- Free inputs: seven outer words (C0.d1 D2.a1 D2.b1 S11 S4 X9 w6), uniform in 32 bits.
- Member k, uniform in [0, 2^19). It sets e1 = 030c0303 | pdep(k, fc307cfc) and Y4 = e1 - Y3.
- Cube index j, uniform in [0, 2^21). It sets E1.c1 = 02008000 | pdep(j, ~0e09818b), which is in Q*.
- Pair: block A is 55 bytes and block B is 63 bytes. Both use counter t (forced by step CT, never 0 here) and flags 3. B differs from A only in w4 (W4' = 97475640) and in w5 (w5 + DELTA5, where DELTA5 = -8).
- These samples are unconditioned members of the family. They are not filtered by the front line's gate, T1/T2 or joint-root tests.
- Residual (D5 section 1): R = (digest A XOR digest B) on words (1,3,4,6), and R = K1 XOR K3.
  - K1 = (Δa2, Δc2, Δd2, Δb2) of E1 = G(Y1,Y6,Y11,Y12; w12,w5).
  - K3 = (Δg2, Δe2, Δf2, Δh2) of E3 = G(Y3,Y4,Y9,Y14; w15=0,w8).
  - Every Δ is an XOR difference A^B.

## Sets

| set | rows | how drawn | seed |
|---|---:|---|---|
| `rand/` | 1,048,576 = 2^20 | independent: fresh outer words, k and j for every row | 0x5045525350310001 |
| `ctx/` | 262,144 = 2^18 | 16 contexts x 16 members x 1,024 j, drawn with replacement. Row order is context-major, then member, then j | 0x5045525350310002 |

`ctx/` holds 52 repeated (context, k, j) rows, which come from drawing j with replacement. The number of distinct residuals equals the number of distinct inputs (262,092). This is COMPUTED.

## Files

Each set has these files. Every value is a little-endian u32, stored row-major. Load one with `np.fromfile(path, '<u4').reshape(-1, cols)`.

| file | cols | columns |
|---|---:|---|
| `inputs.u32` | 12 | ow0..ow6 (C0.d1 D2.a1 D2.b1 S11 S4 X9 w6), k, j, Y4, c1, t |
| `einputs.u32` | 9 | Y1 Y6 Y12 w12 w5, then Y4 Y9 Y14 w8 (side A) |
| `dig.u32` | 8 | digest A words 1,3,4,6, then digest B words 1,3,4,6 |
| `eout.u32` | 16 | E1 A (a2 b2 c2 d2), E1 B, E3 A (e2 f2 g2 h2), E3 B: the round-2 diagonal outputs, raw values |
| `emid.u32` | 16 | E1 A (a1 b1 c1 d1), E1 B, E3 A (e1 f1 g1 h1), E3 B: the values after the first half of G |
| `keys.u32` | 8 | K1 on (1,3,4,6), then K3 on (1,3,4,6) |
| `res.u32` | 4 | R on (1,3,4,6) |

Notes on the columns:
- `einputs.u32`: side B has the same values except Y3' = 7edf3e7e, Y11' = 850000c3, w4' and w5 + DELTA5. Y3 = 8127c181 and Y11 = 7af77f38 on side A. w15 = 0.
- Digest words 0, 2, 5 and 7 are equal on every row. They are not stored.
- The digest words are the XOR of the E outputs:
  - word1 = a2 ^ g2
  - word3 = e2 ^ c2
  - word4 = f2 ^ d2
  - word6 = b2 ^ h2

  For the modular and ones'-complement views, use the raw values in `eout.u32` and `dig.u32`.

The `d4/` folder holds `d4_partial.u32` (76 u32 per record) and `d4_partial.csv`. Their layout is described in the header of `d4export.py`.

## Validation (COMPUTED, 0 failures; logs `rand|ctx/gen_out.txt`, `validate_out.txt`)

**1. Checks inside gen.c, on every row of both sets:**
- The predicted Y state after the round-2 columns matches for A and B.
- Digest words 0, 2, 5 and 7 are equal.
- The E1/E3 outputs agree with the final state.
- E1.c1 = c1, E3.h1 = the predicted value, and ΔE3.h1 = eta (830303cf).
- R = K1 ^ K3.
- Block tail bytes are zero.

**2. Whole-set numpy identities in `validate.py`, on every row:**
- res = digA ^ digB, and res = K1 ^ K3.
- K1 and K3 agree with eout, and digA and digB agree with eout.
- c1 is in Q*, e1 is in the class, and t is nonzero.

**3. Per-row checks in `validate.py`, on 1,000 random rows per set (2,000 in total):**
- The pair is rebuilt from (ow, k, j) by frontline.py `member`, `rebuild` and `step_ct`.
- Both blocks are compressed with the organizer's `hash-smash/verifier/blake3.py` `_compress(IV, words, t, len, 3, rounds=2)`, sha256 prefix bf67aca295b45b06. Digest words 0, 2, 5 and 7 are equal. Stored dig, res, eout, emid and einputs match.
- An organizer `_g` trace matches `_compress`.
- K1 and K3 recomputed from E-inputs only with `pkg13/mitm/check.py` key1 and key3 match the stored keys, and their XOR matches R.
- frontline `chart` returns cons=True, and its compress2 equals the organizer's.

**4. What I could not test.** The pairs are compression-level: the pair at counter t, flags 3. They are not embedded in full messages, because t can be as large as 2^32 chunks. The organizer's `blake3()` on whole messages was therefore not run on them.

## D4 partial constructions (`d4/`)

No completed D4 construction exists (`fifties/d4_local/RESULT.md`). `d4export.py` exports all 1,577 dumped records from `d4_local/dump_*.bin`, and each record has exactly one solved diagonal. For each record it gives:
- D0..D3: the formula from verify_organizer.py. These four values are the D4 residual checks, but they act as that residual only on a completed construction.
- The full 8-word digest XOR.
- Both digests.
- The message words and metadata.

COMPUTED with the organizer's `_g`/`_compress`: the trace matches `_compress` on all records, there are 0 b,c failures and 0 S_k failures on the solved diagonals, and no D word or digest-XOR word is zero.

## Sanity summary only (COMPUTED, `summary.py`, `summary_out.txt`; this is not the analysis)

**`rand/`:**
- All 2^20 residuals are distinct.
- The R words have mean Hamming weight 15.0 to 16.0.
- The largest single-bit biases of R are 0.33 at word 3 bit 19, 0.25 at word 6 bit 11 and 0.20 at word 1 bit 0.

**K1 has visible structure (DERIVED from the G steps; both rotation identities below were also checked on all 2^20 rows with 0 failures):**
- Word 1 (Δa2) has bits 0-3 always 0.
- Δd2 = ROR(Δa2, 8) because d1 is common, so word 4 has bits 24-27 always 0.
- Word 1 has 144,687 distinct values in 2^20 rows.

**K3 structure (DERIVED):**
- Δh2 = ROR(eta ^ Δe2, 8), because ΔE3.h1 = eta always.
- Words 3 and 6 have equal distinct counts.
