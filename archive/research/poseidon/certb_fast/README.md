# certb_fast: GPU Kaltofen-Shoup DDF for the Cert B centres

One fixed job: for the degree-39062 polynomial g_c = H(c, S) over the Pallas base field
(p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001), find the irreducible
factor of degree > 19531 (if any) and its cofactor, with early abort when the residual degree is <= 19531.

Result: **about 39 s per centre (worst case, big factor present) instead of about 29 h with python-flint.**
Own code (`certb_fast.cu`, a copy of `pallas.c/h/consts` for host constants). No yukon commands used.

## Build and run

Run WSL commands through script files (the WSL quoting quirk). Build (gcc for pallas.c, nvcc for the rest, RTX 3090 = sm_86):

    wsl bash ./research/poseidon/certb_fast/build.sh

One centre, from the stored coefficient file (`P3_20_F_j0_coeffs.bin`, copied to `tests/data/F_j0.bin`):

    wsl bash ./research/poseidon/certb_fast/run_center.sh <centre decimal> out/c1
    # = nice -n 10 ./certb_fast ddf --F tests/data/F_j0.bin --center <c> --out out/c1

Output (JSON lines on stdout): stage times, checkpoint gcd degrees, final line `done` with residual degree
and `residual_prime`. If a factor of degree > cutoff survives, `<out>_f.bin` (the leftover factor f) and
`<out>_cofactor.bin` (monic, = product of all irreducible factors of degree <= cutoff) are written as
32-byte little-endian canonical coefficients, constant term first (same format as the luna3 `.bin` files).

Other modes: `ddf --g g.bin` (any monic squarefree g), `center F.bin c out.bin` (build g_c), `xp`, `mulmod`, `compose`.
Options: `--cutoff K` (default d/2), `--l L` (default as in P3_22_bsgs.py: 140), `--check-every B` (default 14 blocks),
`--check-from K` (default 2/5 of cutoff), `--no-abort`, `--no-graph`.

N centres (file with one decimal per line), N at a time on the one GPU, nice 10:

    wsl bash ./research/poseidon/certb_fast/run_many.sh N centres.txt out/many

**Measured: N > 1 does not help.** One process already keeps the 3090 at 100%; 4 centres took 147 s
back to back and 191 s with N=2 (GPU time slicing). Use N = 1 (about 90 centres per hour). Host CPU use of one run is
about 27% of one core (event polling, no spin), about 4.5 GB device memory.

## Method (what is computed)

* g_c from the Taylor shift (same formula as `H_at_center` in P3_20_midpoint_group.py, one NTT convolution of size 2^18).
* x^p mod g: 254 square-and-multiply steps (multiplying by x is a shift plus one reduction).
* All mulmods use NTT (radix-2, two shared-memory passes per transform, size 2^17 for products, 2^16 for q*g) and a
  Newton inverse of rev(g) computed once (fixed modulus g throughout).
* Baby steps x^(p^i), i <= l=140, and giant steps x^(p^(jl)) are modular compositions by Brent-Kung with a **fixed inner
  polynomial** (x^p, then x^(p^l)): the powers h^0..h^197 and the spectra of (h^198)^i are built once per inner
  polynomial (0.28 s); each composition is a 198 x 198 by 198 x 39062 matrix product (26-bit limbs, 64-bit column
  accumulators, Montgomery reduce) plus 198 transforms accumulated in the spectral domain: 69 ms each.
* Interval products: one running product W = prod over k=1..19531 of (x^(p^(jl+l)) - x^(p^i)) mod g, i.e. prod_k (x^(p^k)-x)^(p^i)
  in the flint ordering of P3_22_bsgs.py. Because g is squarefree, gcd(g, W_K) is exactly the product of the irreducible
  factors of degree <= K, so no residual update is needed (the modulus stays g) and the per-block gcds of the flint version
  are replaced by gcds at checkpoints. Leftover degree = d - deg gcd.
* gcd: Euclid with scaled steps (no inversions) in one cooperative kernel (about 0.65-1.1 s each).
* Early abort: gcd checkpoint every 14 blocks once K >= 0.4 * cutoff; abort when d - deg gcd <= 19531.
* f = g / gcd by Newton series inverse + one product; cofactor = gcd.

## Validation (all against python-flint 0.9.0, coefficient by coefficient where stated)

| check | result |
|---|---|
| mulmod, d = 200, 777, 1000, 5000, and d = 39062 (g_c) | identical |
| x^p mod g, d = 200, 777, 1000, 5000 | identical |
| compose f(h) mod g, d = 200, 777, 1000, 5000 | identical |
| **g_c at c = 1610209...6367 from F_j0** (center mode) vs `H_at_center` | identical (39063 coefficients); 0.26 s vs 9.8 s |
| **d = 39062: x^p mod g_c** | identical (flint 114.3 s, ours 0.16 s) |
| **d = 39062: compose_mod(f, x^p) mod g_c**, random f | identical (flint 330.1 s, ours 0.068 s) |
| DDF degree pattern, random squarefree d = 200 (4 seeds), 1000 (3 seeds), 5000 (1 seed): cumulative removed degree at every block checkpoint vs the factor degrees from flint `factor()` | exact match in all 8 |
| planted irreducible degree 521 in d = 1000 (found by random search + `is_irreducible`): leftover f and cofactor | f == u, cofactor == v exactly |
| leftover factor and cofactor on random polys (d = 200, 1000, 5000) | f * cofactor == g, f irreducible (flint) |
| cross-check with `ks_strip_small_factors` of P3_22_bsgs.py (d = 1000, 2 polys) | same residual degree and same cumulative removed degree per block |
| **d = 39062 planted**: g = f * v, f = the degree-36091 leftover found by the engine for a real centre, v random degree 2971 (flint factored v: degrees 1,2,4,126,387,2451); gcd checkpoint at all 140 blocks | masses match the flint factor degrees exactly; leftover == f and cofactor == v exactly |
| independence of the split: same centre with l = 100, 140, 175 (different baby/giant sets and compositions) | identical gcd degrees at all common K (1400 ... 19531) |

Test scripts: `tests/t_basic.py`, `t_center.py`, `t_full_ours.py` + `t_full_flint.py`, `t_ddf.py`, `t_luna.py`, `t_full_planted.py`, `mm_full.py`, `lindep.sh`.

Not tested (limits): irreducibility of a full-size leftover f is not checked independently (it follows from the degree argument:
once all irreducible factors of degree <= d/2 are removed, at most one factor remains); we have no way to run flint's own DDF at
degree 39062 in reasonable time, so the full-size DDF is validated through the planted test, the split-independence test and the
flint-identical building blocks. The sm_86 binary and the cooperative-launch gcd were only run on the one RTX 3090 (shared with
another process using about 1.9 GB and a few percent).

## Timing (one centre, honestly measured, 1 process nice 10 + GPU, GPU shared with another idle-ish tenant)

Baseline (python-flint, measured in this session where marked): x^p 114 s, one compose_mod 330 s, one mulmod 0.67 s, shift 9.8 s,
140 baby + 139 giant compositions + 19531 interval mulmods + 140 gcds: about 29 h per centre (figure from the task).

Worst case, big factor present (centre #2 of `tests/centres.txt`, residual 27468 > cutoff, all 140 blocks, 7 checkpoint gcds), wall 39.7 s:

| stage | seconds |
|---|---|
| process start, g_c (Taylor shift), Newton inverse, spectra | 0.15 |
| x^p mod g | 0.18 |
| baby steps (139 compositions + inner build 0.29) | 9.6 |
| giant steps (139 compositions + inner build 0.27) | 9.7 |
| interval products, 19531 terms (0.59 ms each) | 11.5 |
| gcds (7 x ~1 s) | 7.1 |
| **total** | **38.9 (wall 39.7)** |

With early abort (centres #4 and #6 of the 8-centre set: no factor > 19531, abort at block 97): 29.1 and 29.3 s.
Eight centres: residual degrees 36091, 27468, 22696, abort, 25853, abort, 22803, 25535; none had a prime residual degree.

Per-centre before vs after: 29 h -> 39 s (about 2700x); goal was < 3 h.

## Files

`certb_fast.cu` (engine), `build.sh`, `run_center.sh`, `run_many.sh`, `pallas.c/h`, `pallas_consts.h` (copies from orchard/single_r1, host constants only),
`tests/` (validation), `out/` (logs and factor files of the runs above).
