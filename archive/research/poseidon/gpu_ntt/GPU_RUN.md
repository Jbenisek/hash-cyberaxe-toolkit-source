# RTX 3090 run

Environment: NVIDIA GeForce RTX 3090, compute capability 8.6, 24,576 MiB;
CUDA 12.4.131 under WSL.  Every transform below passed the inverse-transform
round trip after multiplication by `n^{-1}`.

| n | forward / inverse ms | exact ops per transform (add, sub, mul) | peak bytes (one transform) |
|---:|---:|---:|---:|
| 2^15 | 34.401 / 6.172 | 245,760 / 245,760 / 245,760 | 2,097,216 |
| 2^16 | 1.888 / 1.321 | 524,288 / 524,288 / 524,288 | 4,194,368 |
| 2^17 | 2.505 / 4.437 | 1,114,112 / 1,114,112 / 1,114,112 | 8,388,672 |
| 2^18 | 5.459 / 8.432 | 2,359,296 / 2,359,296 / 2,359,296 | 16,777,280 |
| 2^19 | 11.308 / 12.522 | 4,980,736 / 4,980,736 / 4,980,736 | 33,554,496 |
| 2^20 | 22.954 / 26.924 | 10,485,760 / 10,485,760 / 10,485,760 | 67,108,928 |

Peak bytes are `2*n*sizeof(Fp)+2*sizeof(Ops)` for one transform (data plus
root table and counters).  A polynomial multiply keeps two coefficient arrays
and two root tables at its peak; the conservative allocation is therefore
`4*n*32 + 2*sizeof(Ops)` bytes, 134,217,792 bytes at `n=2^20` (128 MiB plus
the two 32-byte counters).

The required modular-square batches were also run:

```text
n=39,062   time=0.181 ms   4.641 ns/square   exact_sqr=39,062
n=195,312  time=1.296 ms   6.634 ns/square   exact_sqr=195,312
```

The optional `--poly-smoke` run also returned `POLY_GPU_SMOKE status=PASS`
for a degree-2 by degree-1 product at n=2^15.  Its square timings were
0.248 ms and 8.990 ms (6.349 and 46.028 ns/square), respectively; that run
was made immediately after the six large transforms and is retained only as
a clock/cache-variance check, not as a replacement for the clean measurements
above.

The first 2^15 timing includes normal first-use/JIT variance; it does not
change the exact operation counts or any score.
