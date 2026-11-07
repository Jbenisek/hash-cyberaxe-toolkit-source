# r=2 CERT B engine: status (stopped by coordinator, 2026-10-13 ~12:52)

No witness found; run stopped (the GPU memory was full and the owner's PC became unusable). No GPU job relaunched.

## F_r2 source and check
- Source: 3rd_openai_workspace/luna3/P3_21_F_j0_coeffs.bin (12,500,032 bytes = 390,626 coefficients, 32-byte LE, constant first), copied to data/F_r2_j0.bin.
  sha256 5a4880b39b9f82ef22055c7e28446224f437ccd529bc59cf0e394e4bbd5882f3.
- Check (chk_F_r2.py): ref.hash_reduced(nk, rho, r=2) == F(tau^5) at 5 random tau (Line 0): all True.

## Engine changes (certb_fast.cu in this folder, r=1 copy untouched)
- LNM 18 -> 20 (Taylor shift needs 2^20; products 2^19).
- certify: Frobenius doubling checkpoints NB = bit length of l (>= 16), so 18 for l > 131071.
- DDF memory: baby[i] freed after its spectrum is made, giant[j-1] freed after use.
- Matmul 64-bit accumulator bound: 9*m1 <= 4096 needs m1 <= 455; m1 = 442 at d = 195312 (ok, analytic).

## Validation
- Small degrees vs python-flint after the change: mulmod, x^p, compose (d=200, 5000) True; DDF natural d=1000 pattern match, leftover irreducible; certify pos101 PASS, 5 negatives FAIL, R_j files match flint.
- Full size d = 195312: g_c from F_r2 at a random centre equals flint Taylor-shift H_at_center (195,313 coefficients, identical; ours 0.17 s vs flint 41 s).
- Full size, g = (8 known linear factors) * random: mulmod, compose f(h) (f with max-limb coefficients), x^p all verified at the 8 roots. Not tested: full-size DDF against flint, NB > 16 certify path, planted test at r=2.

## Timing (one centre, centre #1 of centres_r2.txt, l = 313, 312 blocks, GPU shared with another tenant)
- g_c 0.17 s, setup 0.41 s, x^p 0.68 s, baby steps 880.5 s (312 compositions, 2.82 s each; inner build 2.9 s). Standalone compose measured 1.46 s.
- Giant, interval and gcd stages not measured (run killed). Projection: giants about 880 s, intervals roughly 5-10 min, gcds about 25 s each; so about 35-45 min per centre, over the 30 min limit.
- Memory peak about 23.9 GB total on the 3090 (with the other tenant's 1.8 GB): too tight. Reduce before any retry (smaller PS storage, or l about 250).
- Prime-mass of the window (97656, 195309]: sum 1/l over primes = 0.0584 (not 0.0676, which is the r=1 window); expected about 17 centres, so about 11 hours at 40 min each.

## Files
build.sh, run_r2.sh, centres_r2.txt (60 random centres), tests/ (t_struct.py, t_center_r2.py, logs), out/m1.log.
