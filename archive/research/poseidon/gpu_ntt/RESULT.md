# D184 result

Status: COMPUTED / VALIDATED.  No submission or package was made.

## Field and roots

The implementation uses the Pallas base-field modulus

`p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`.

The field has `v_2(p-1)=32`.  A primitive 2^32-th root is obtained from
`5^((p-1)/2^32)` and stored in Montgomery form.  All four 64-bit limbs are
little-endian and every Montgomery add, subtract, multiply, and square is
counted exactly.  The field implementation was checked on 128 random pairs
against `cpp_int`; the polynomial remainder and Newton inverse identities also
pass (`CPU_VALIDATION.md`).

## GPU NTT

`ntt.cu` was compiled with `nvcc 12.4.131 -O3 -arch=sm_86` and run on the
RTX 3090.  Radix-2 transforms at every requested size 2^15 through 2^20 pass
the inverse round trip.  A transform of length n has exactly

`(n/2) log2(n)` butterflies, hence that many adds, subtracts, and multiplies.

Root setup costs `(32-log2(n))` squarings and `n-1` multiplies per direction.
Inverse scaling costs n multiplies plus 256 squarings and 77 multiplies for
the fixed-exponent inverse of n.  The full timing/counter table is in
`GPU_RUN.md`; its largest transform has 10,485,760 of each primitive per
direction.

The GPU pointwise kernel and the `poly_mul_gpu` orchestration are present in
`ntt.cu`.  Polynomial Newton reciprocal, quotient remainder, and
`S^((p-1)/2) mod g` are implemented in `poly_ref.cpp`, using the same exact
field operations; this is the independent CPU oracle for the GPU path.

The one-transform device peak is conservatively `2*n*32 + sizeof(Ops)` bytes.
The multiply wrapper
reuses the forward buffers and allocates the inverse transform only after the
pointwise product, so its conservative peak is `4*n*32 + 2*sizeof(Ops)` bytes
(134,217,792 bytes at n=2^20).

## Required square timings

The square kernel reports exact counters and measured batches:

* n = 39,062: 0.181 ms, 4.641 ns/square, exact_sqr = 39,062.
* n = 195,312: 1.296 ms, 6.634 ns/square, exact_sqr = 195,312.

The optional post-transform `--poly-smoke` run returned `POLY_GPU_SMOKE PASS`
for a degree-2 by degree-1 product at n=2^15.  Its square timings (0.248 ms
and 8.990 ms) show ordinary clock/cache variance and are not used for the
clean benchmark row.

The different per-square timings are launch/cache/load variance; they do not
alter the exact operation charge.
