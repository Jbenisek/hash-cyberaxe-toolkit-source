# prereg_HA result (2026-10-09)

Claim tested: Sol's bound that the 1.4 two-borrow gate opens on at most 3339/6400 = 0.52171875 of clusters on average.
Preregistration: PREREG.txt. Its SHA-256 is 97d01e784b44372f2c27374c76336de62c62fbac0dac809948877c7b381eb047, written before any code. The recheck after the run matches (decision.json, hash_match true).

## Verdict: SUPPORTED

| quantity | value |
|---|---|
| clusters n (main, label "prereg_HA 2026-10-09", seed64 304d0e3ea26088a5) | 4,294,967,296 = 2^32, one fresh context each |
| opens k | 1,925,090,990 |
| opening mean | 0.448220174 |
| SE | 7.59e-6 |
| empirical Bernstein upper (delta 0.00135) | 0.448249175 |
| KL upper (delta 0.00135) | 0.448247760 |
| declared bound | 0.52171875 (margin 0.0735 under both bounds) |
| exact value if (a, q, c) were uniform | 940000 / 2^21 = 0.448226929 |

The measured mean is within 1 SE of the uniform-key value, which suggests (a, q, c) behave as close to uniform on real contexts. Sol's bound has 63/128 = 0.4921875 as its base, about 0.044 above the exact uniform value, so the bound holds with room to spare.

## Dry run (step 2: label "dry", 65,536 clusters, seed64 b755cb248c3c4a7d)
- Python reference (numpy over the exc_check.py evaluator) against the CUDA kernel: 0 mismatches in each of a, q, c and OPEN (0 clusters with any mismatch). Both counted 29,559 opens.
- The identity omega = (ROL16(p - A) XOR L) + C held on all 65,536 clusters (0 failures). This checks the p, A, L, C mapping.
- p, A, L, C and omega from outer.scalar_outer matched the reference on the first 2,000 clusters (0 failures).
- After the main run, the count kernel on the dry set returned 29,559, equal to the reference. This checks the reduction path.

## Files
PREREG.txt and PREREG.sha256; gen_cu.py, which generates gate.cu from outer.slice_lines; gate, the binary built for sm_86; ref.py; run_dry.sh; run_main.sh; decide.py; dry_result.json; main_result.json; decision.json; run_dry.log; run_main.log; gpu_dry.bin.

## Limits
- Only the opening mean is measured. Whether the gate is a correct cover for all 32 members (Sol's 1.4 proof) is not tested here.
- The representative is the member with e1 bits 10..14 = 0, as in exc_check. Other representative choices were not measured.
- Contexts are uniform 32-bit outer words and uniform W, as in outer.py draw(). This test does not cover any non-uniform context source.
- The bounds are statistical (delta 0.00135 each), not a proof.
- The main run ran once and took 0.29 s of GPU time.
- Process notes:
  - The brief did not give the mapping of p, A, L, C to step-CO words. It was taken from sol_answer_CI_levers.md lines 15-18 by a narrow grep (p = Y0, A = C0.b1 + w6 + X4 + w2, L = ROL24(X15) XOR S15, C = e1 - S0 - S5, with b, c, d = C0.b1, C0.c1, C0.d1) and then checked by the omega identity above.
  - WSL python3 has no numpy, so the reference and the decision ran on Windows Python 3.14 with numpy 2.4.6. The GPU ran under WSL with nvcc.
