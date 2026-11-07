## 9. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter; `CTL(n)` adds `n` to the control counter; `HC(n)` and `loopc(n)` add `n` half units; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters. Buffers are obtained from the tracked allocator (`NEW_FP`).
The program is built as `gcc -O3 -march=native -o exec_attack lean_attack.c common.c ntt.c poly.c loop.c lean.c line.c euclid.c hgcd.c pallas.c -lm`, and the counted run is `ulimit -s 64; ./exec_attack 2 8 1 0 1 0 0 1` (r = 2, at most 8 centres, seed 1 unused, line 0 fixed, verbose printing, no budgets, fixed line). Unused parts of the files (`powx_mod` in `loop.c`, `build_g`'s debug flag, budget tables in `budgets.h`) are not executed by this run.
The files are shown in full, in the order: @@FILE_ORDER@@.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs.

@@APPENDIX@@
