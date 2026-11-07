# D184: Pallas GPU NTT

This directory is an independent implementation; `research/poseidon/orchard/`
is not modified.  `pallas.cuh` is a four-limb, little-endian Montgomery field
with the Pallas prime and the exact `add/sub/mul/sqr` counter.  `ntt.cu` builds
with CUDA 12.4 for `sm_86` and provides radix-2, bit-reversed NTTs, a GPU
pointwise polynomial product (`poly_mul_gpu`), and the two benchmark kernels.
`poly_ref.cpp` is the CPU big-integer/reference path for polynomial product,
Newton reciprocal, quotient remainder, and `S^((p-1)/2) mod g`.

Build/run under WSL (CUDA 12.4):

```text
nvcc -O3 -arch=sm_86 ntt.cu -o ntt_bench
./ntt_bench
g++ -O3 -std=c++17 poly_ref.cpp -o poly_ref
./poly_ref
```

The CUDA counter is per butterfly: one field multiplication, one add, and one
subtraction.  It is accumulated once per thread with 64-bit atomics, not
estimated from elapsed time.  Root-table generation, inverse scaling, and
polynomial pointwise products are counted separately by the same `Ops` type.
