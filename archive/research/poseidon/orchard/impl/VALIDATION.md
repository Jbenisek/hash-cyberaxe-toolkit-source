# Orchard Poseidon implementation: validation (2026-10-12)

Folder: `research/poseidon/orchard/impl`. Labels: PROVED / COMPUTED (command + output file) / DERIVED / GUESS.
Written fresh here (the older `research/poseidon/impl` code was not imported or reused; only the public upstream files were re-fetched).

## Files
| file | role |
|---|---|
| `poseidon_ref.py` | big-int reference: `hash_reduced(nk,rho,r)`, `hash_full(nk,rho)` (separate straight 64-round loop), `digest_bytes`, `perm`, `schedule(r)`; constants read as data from `../../pareto_clone/pareto/orchard-pallas-constants.json` (override with env `ORCHARD_CONSTANTS_JSON`) |
| `test_ref.py` -> `test_ref_output.txt` | public-vector validation of the reference |
| `check_constants_vs_fp_rs.py` -> `check_constants_vs_fp_rs_output.txt` | JSON constants and MDS vs upstream `fp.rs` |
| `gen_c_consts.py` | writes `pallas_consts.h` (Montgomery constants, Z = 5^q, p-2, q, (q+1)/2, (p-1)/2) and the vector files `poseidon_vectors.txt` (3155 lines), `field_vectors.txt` (506 lines) |
| `pallas.h`, `pallas.c` | C library: 4x64 Montgomery field (`fp_add/sub/neg/dbl/mul/sqr/pow5/pow/inv/sqrt/legendre`), exact global op counters `fp_cnt`, `poseidon_perm_r`, `poseidon_hash_r`, `poseidon_hash_r_fp`, `poseidon_C` |
| `test_pallas.c`, `build_test.sh`, `build_sanitize.sh` -> `test_pallas_output.txt`, `test_pallas_sanitize_output.txt` | C test vs Python vectors and counter checks (normal build and ASan+UBSan build) |
| `verify_skip.py` -> `verify_skip_output.txt` | small-scale check of the coordinator's skip-two-rounds line parametrisation |
| `known_answers_reduced.txt` | reduced-target digests (r=0,1,2) for three inputs, as hex integer and as 32-byte LE digest, for later comparison with the organizer verifier |
| `upstream/test_vectors.rs`, `upstream/fp.rs` | raw public files (fetched 2026-10-12) |

Reproduce: `python3 gen_c_consts.py; python3 test_ref.py; python3 check_constants_vs_fp_rs.py; python3 verify_skip.py`, then in WSL `wsl bash ./research/poseidon/orchard/impl/build_test.sh`.

## 1. Constants (COMPUTED)
- `upstream/fp.rs` is https://raw.githubusercontent.com/zcash/halo2/halo2_poseidon-0.2.0/halo2_poseidon/src/fp.rs, SHA-256 `b19d4e50867e67af232db34f88d2bf8629d6d7ee2496458a8e37ae758772acd5`, equal to the `source_sha256` recorded in the organizer JSON.
- `python3 check_constants_vs_fp_rs.py`: `round constants equal JSON: True`, `MDS equal JSON: True` (192 constants, 9 MDS entries, parsed independently from the Rust limbs).

## 2. Public test vectors (COMPUTED)
Source: https://github.com/zcash/halo2/blob/halo2_poseidon-0.2.0/halo2_poseidon/src/test_vectors.rs (raw: https://raw.githubusercontent.com/zcash/halo2/halo2_poseidon-0.2.0/halo2_poseidon/src/test_vectors.rs, SHA-256 `22ec104e0da48530dc6489b61bcd621eae74985b4f68294fee92b8fa91ae09ca`, fetched fresh and byte-identical to an earlier copy). Module `fp` (Pallas base) has 11 permutation vectors (from zcash-hackworks/zcash-test-vectors `orchard_poseidon/permute/fp.py`) and 11 `ConstantLength<2>` hash vectors.

`python3 test_ref.py`:
```
permutation vectors 11/11, hash vectors 11/11, byte-level digest 11/11
hash vector 0: nk=0 rho=1 out=0x062ff1c32bb0ef109d6a1bc9399a083eed83c2a7fb54cdbe389d32a011d75883
hash vector 0 out LE bytes: 8358d711a0329d38becd54fba7c283ed3e089a39c91b6a9d10efb02bc3f12f06
negative controls differ: ok        (capacity 3<<64, 55 partial rounds, swapped inputs each break vector 0)
hash_reduced(r=56) == hash_full on 20 random inputs
schedule(1) = [0, 1, 2, 3, 4, 60, 61, 62, 63]  schedule(2) = [0, 1, 2, 3, 4, 5, 60, 61, 62, 63]
noncanonical inputs rejected: ok
```
So the reference (state `[nk, rho, 2^65]`, x^5, dense MDS, S-box on lane 0 in partial rounds, output lane 0) reproduces the complete Orchard `ConstantLength<2>` hash on all 11 public vectors, which exercises all 64 round-constant rows and the MDS. The C library reproduces the same 11 hash vectors at r=56 (they are lines of `poseidon_vectors.txt`).

## 3. Reduced hash r = 1, 2 (what is and is not established)
- COMPUTED: C == Python on 1008 inputs each for r=0, 1, 2 (8 edge inputs incl. `(0,0)`, `(p-1,p-1)`, `(1<<253, (1<<254)-1)` plus 1000 random), and on 20 random each for r=3,5,10,30,55, and on 31 inputs at r=56 (11 public + 20 random). `ALL CHECKS PASSED` in both the `-O2` and the ASan+UBSan builds.
- No official vector exists for r < 56 (upstream has only full 64-round vectors). Correctness of the prefix rests on: the round function validated at 64 rounds, plus the schedule (constants of the ORIGINAL index 0..3, 4..4+r-1, 60..63) matching the organizer text and `verifier/poseidon.py` as read below. Not independently testable beyond that.
- Cross-check against the organizer's `verifier/poseidon.py` by READING (not imported, not run), line by line:
  - modulus `P` identical hex; constants from the same `pareto/orchard-pallas-constants.json` (`round_constants` 64x3, `mds` 3x3, row-major, `int(x,16)`);
  - loop `for index in (*range(4), *range(4, 4+rounds), *range(60, 64))` = our `schedule(r)`;
  - per round: `(x + c) % P` with `constants[index]`, then `pow(x,5,P)` on `range(3)` if `index<4 or index>=60` else `range(1)`, then `state[i] = sum(c*x for c,x in zip(row, state))` over MDS rows = our `mds_apply` (new_i = sum_j M[i][j] s_j);
  - `digest`: 64 bytes = two 32-byte LE integers, rejects `>= P`, state `(nk, rho, 1<<65)`, returns `permute(...)[0].to_bytes(32,'little')` = our `digest_bytes`; `rounds` allowed 0..56 = our `r` range.
  - Organizer check to run later (not done here): in the live clone, `digest(bytes, r)` on the inputs in `known_answers_reduced.txt` must equal the listed `32-byte LE digest` column.

## 4. C library field arithmetic (COMPUTED, `test_pallas_output.txt`)
- 506 field vectors from Python big-ints (edge cases 0, 1, p-1 plus random): add, sub, mul, sqr, inverse, Legendre symbol, sqrt (flag and `root^2 == a`), hex round trip: all equal.
- 2000 random distributivity/commutativity/inverse/negation identities; sqrt of 2000 squares returns a root, of 987 non-residues returns 0.
- Tonelli-Shanks uses p-1 = 2^32 * q (q odd), z = 5^q (5 is a non-residue: asserted in the generator and C test; `z^(2^31) = -1` asserted in C). 64 additional squares built with deep 2-adic components all pass.
- Montgomery `-p^-1 mod 2^64` asserted in C.

## 5. Exact operation counters (COMPUTED)
Primitive = one field add, sub, mul or sqr executed (`fp_prim_total() = add+sub+mul+sqr`). Convention: a squaring is one multiplication-class primitive; negation is one sub; doubling is one add; `inv_calls/pow_calls/sqrt_calls` are informational and never charged on top (their sqr/mul are already in the counters, so nothing is double counted).
- `fp_pow5` = 2 sqr + 1 mul = 3. Test: 2 add, 2 sub, 2 mul, 3 sqr after the unit-test sequence, as expected.
- Poseidon, faithful reference arithmetic (3 constant adds + S-box + 3x3 MDS = 3 mul + 2 add per row): full round 9 add + 18 mul-class = 27; partial round 9 add + 12 mul-class = 21. Asserted on EVERY one of the 3155 vector hashes: adds = 72+9r, mul+sqr = 144+12r, subs = 0, total = `poseidon_C(r)` = 216+21r. So one `poseidon_hash_r` call is exactly C(r) = 237 primitives at r=1 and 258 at r=2, i.e. exactly 1 target-compression unit, matching `orchard-cost-v2.json` and `ORCHARD_ACCOUNTING.md` (C = 156 mul + 81 add at r=1; 168 mul + 90 add at r=2).
- `fp_inv` (a^(p-2), left-to-right square-and-multiply, no operation on the leading bit or on zero bits): bitlen(p-2)=255, popcount 77, so 254 sqr + 76 mul = **330** primitives (asserted equal to bitlen-1 and popcount-1). One inverse = 330/C(r) units (1.39 units at r=1, 1.28 at r=2).
- `fp_legendre` (a^((p-1)/2)): 253 sqr + 45 mul = 298 primitives.
- `fp_sqrt` (Tonelli-Shanks, two exponentiations plus loop): data dependent; 831 primitives on one random square, maximum 992 over 64 random squares. Non-residue detection costs about the same. A cheaper charge, if an algorithm only needs a Legendre test, is 298.
- DERIVED (not implemented here): addition chains shorter than plain square-and-multiply for p-2 would cut the 330; the library implements the plain chain, a conservative upper bound.

## 6. Conversions and what is not counted
- Montgomery <-> canonical conversions (`fp_from_limbs`, `fp_to_limbs`, hex I/O) are NOT counted: they are an I/O encoding; constants are stored pre-converted in `pallas_consts.h` (generated, so no run-time conversion cost). An accounting that charges them is more expensive by 2 mul-class primitives per conversion.
- Comparisons (`fp_eq`, `fp_is_zero`), branches, loads/stores, loop control and randomness are NOT counted by the library; an attack program must charge them itself (the cost model prices each as 1/C).
- Single-threaded global counters; not constant time; not an optimized code path (`-O2` plain C: 10.2 us per r=1 hash, 53 ns per mul on this machine; information only, not part of the score).

## 7. Skip-two-rounds line structure, small scale (COMPUTED, `verify_skip_output.txt`)
`python3 verify_skip.py` for r=1,2 and each kept lane j in {0,1,2}:
- U=(nk+c0)^5, V=(rho+c1)^5 is a bijection (gcd(5,p-1)=1; p = 2 mod 5, root map is x^((5^-1) mod (p-1))), so rounds 0 inputs are a bijective parametrisation; the round-1 S-box input is affine in (U,V).
- With d = M[j,1]*M[:,0] - M[j,0]*M[:,1] (d_j = 0) and Q chosen so both other lanes vanish, on the line (U,V) = (U0,V0) + tau*(a,b) the S-box outputs are exactly `d_i^5 * W` (i != j) and a constant (lane j), W = tau^5: asserted exactly on sample points, and the state after round 1 has finite-difference degree 1 in W (affine).
- Degree in W of the state after round 3 and after each partial round is exactly 5^(2+k) (k = partial rounds done), by finite differences on 5^(2+k)+3 equally spaced W points: [25, 125] for r=1 and [25, 125, 625] for r=2, all three lanes, all three j.
- The map back from W to (nk, rho) is injective (distinct W give distinct inputs; 129 resp. 629 distinct pairs checked, and a W -> (nk,rho) -> W round trip), F(W) := hash(nk(W), rho(W)) is therefore a well-defined function of W, and h(s)=F(c+s)-F(c-s) is odd (checked on samples).
- DERIVED, not computed: the four final full rounds multiply the degree by 5 each, giving deg F <= 5^(6+r) (5^7 = 78125 at r=1, 5^8 = 390625 at r=2). The upper bound is PROVED from the round structure (each S-box composes a degree-d polynomial with x^5); exactness of the top coefficient was verified only up to the state before round 60 (above). The full-degree finite-difference check at 78127 points was not run.
- Not tested here: the odd-part root distribution (success ~ 1 - e^(-1/2)), the polynomial arithmetic/gcd/splitting cost, and any total-cost claim. This section only confirms the algebraic parametrisation.

## 8. Limits
- No official reduced-round vector; r=1,2 correctness rests on sections 2-3 as stated.
- The organizer verifier was read, not executed (per instruction); the known-answer file is prepared for that check.
- Operation conventions (squaring = 1 primitive, Montgomery conversions free, plain square-and-multiply for inversion) are mine, stated so a different convention can be applied; none is an organizer ruling.
