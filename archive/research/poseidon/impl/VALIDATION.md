# Own Poseidon implementation - validation (2026-10-12)

Files (all in research/poseidon/impl): `poseidon_own.py` (perm, hash_prefix, hash_prefix_opt, Counter), `constants_own.py`
(generated), `gen_constants.py`, `test_own.py`, `check_pr_constants.py`, `grain_regen.py`, `upstream/` (raw public files), `*_output.txt`.
Labels: PROVED / COMPUTED (command + output) / DERIVED / GUESS.

## 1. Constants - three independent sources agree (COMPUTED)
- Source A (public): `upstream/fp.rs` = https://raw.githubusercontent.com/zcash/halo2/halo2_poseidon-0.2.0/halo2_poseidon/src/fp.rs
  (header: Sage `generate_parameters_grain.sage 1 0 255 3 8 56 0x4000...0001`, repo daira/pasta-hadeshash). `from_raw` limbs are canonical LE u64.
  `python gen_constants.py` -> `ok 64 rows; MDS*MDS_INV = I` (192 constants, MDS, MDS_INV parsed; MDS*MDS_INV = identity asserted).
- Source B (PR 923 text, parsed as data, not imported): `python check_pr_constants.py` ->
  `round constants equal: True | MDS equal: True | modulus equal: True`.
- Source C (our own Grain-LFSR port, Poseidon v1.1 generator): `python grain_regen.py` ->
  `regenerated round constants match deployed: True` (192/192) and `regenerated MDS ... matches deployed: True`.
  Note: MDS x_i,y_j are 255-bit Grain draws reduced mod p WITHOUT rejection (3 of the 6 draws exceed p); round constants use rejection. Found by experiment, then confirmed on all 9 entries.

## 2. Public test vectors (COMPUTED)
Source: https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/test_vectors.rs, module `fp` (Pallas base),
which cites zcash-test-vectors `orchard_poseidon` (permute/fp.py). 11 permutation + 11 hash vectors, parsed from the raw file.
`python test_own.py` ->
```
permutation vectors 11/11, hash vectors 11/11
hash vector 0: in=(0,1) out=0x062ff1c32bb0ef109d6a1bc9399a083eed83c2a7fb54cdbe389d32a011d75883
hash vector 0 out (LE bytes) = 8358d711a0329d38becd54fba7c283ed3e089a39c91b6a9d10efb02bc3f12f06
negative controls (capacity 3<<64, 63 rounds) differ: ok
```
Hash vector 0 as printed in the upstream file: input [0x00 x32], [0x01,0x00 x31]; output bytes 83 58 d7 11 a0 32 9d 38 be cd 54 fb a7 c2 83 ed 3e 08 9a 39 c9 1b 6a 9d 10 ef b0 2b c3 f1 2f 06 (matches).
Permutation vector 0: state (0,1,2) -> first element bytes 56 a4 ec 4a ... 6a 52 2a (matches). Only full 64-round vectors exist upstream;
prefix rounds r=1,2 have no official vector (correctness of the prefix rests on the same round function, validated by the 64-round vectors plus the r=1 closed form check below).

## 3. Operation counts (COMPUTED, `test_own.py`; instrumented count == analytic count asserted for r in 1..5,10,63,64)
Primitive = one modular add, mult or squaring. S-box x^5 = 2 squarings + 1 mult.
| unit | adds | squarings | other mults | mults total | adds+mults |
|---|---|---|---|---|---|
| full round | 9 | 6 | 12 | 18 | **27** |
| partial round | 9 | 2 | 10 | 12 | 21 |
| 64 rounds | 576 | 160 | 656 | 816 | 1392 (PR: 816 mult + 576 add - agrees) |

Cost per prefix, faithful program (all lanes, full MDS), r=1: 27; r=2: 54 (matches C). Mults-only reading: 18 / 36.
Tighter exact variants (still produce the identical digest, asserted vs faithful on random inputs):
| r | faithful (adds+mults) | last round row 0 only | + constant capacity lane folded | one-time precompute |
|---|---|---|---|---|
| 1 | 27 (mults 18) | 17 (mults 12) | 12 (mults 8) | 7 (mults 6) |
| 2 | 54 (mults 36) | 44 (mults 30) | 34 (mults 24) | 10 (mults 6) |
| 3 | 81 (mults 54) | 71 | 61 | 10 |
Fold = lane 2 of round 0 is the constant K=2^65+RC[0][2]; its S-box and MDS column become hard-coded constants (K^5, M[i][2]*K^5) and the per-row constant is merged into round 1's constants (or, r=1, added once). These are DERIVED savings (code verifies equal digests); whether the organizers' accounting lets a program hard-code derived constants (vs charging the verifier's own reference hash) is unsettled. A verifier that runs the reference `permutation` is charged the faithful 27/54 per hash, so each hash evaluated in the attack plus the two verification hashes would be charged at that rate.

## 4. Extra check of day-one route 1 (COMPUTED)
Fifth-root line: lambda = (-M01/M00)^d with d=(4(p-1)+1)/5 (5d = 1 mod p-1, asserted); messages with m0+c0 = lambda*(m1+c1) give equal r=1 digests: two distinct messages (m1+c1 = 12345 and 99999) collide - `True True` (distinct, equal digest) with `hash_prefix(.,.,1)`.

## 5. Not tested / limits
- No official vector exists for r<64; r=1,2 digests are validated only through the shared round function.
- Counter conventions (squaring = 1 primitive, no free multiplication by small constants, no add-chain tricks) are the PR's proposal, not a ruling.
- Python integers, not constant-time, no Montgomery; counts are of field operations only.
