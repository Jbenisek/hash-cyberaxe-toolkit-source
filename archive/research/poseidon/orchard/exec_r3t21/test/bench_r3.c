/* not shipped: counters and memory of stage C (a few loop steps) and stage D at the real r = 3 size, on random inputs (data-independent operation counts).
   usage: bench_r3 c [bits]   powx_lean(F, g, m, E, 2) with E of 20 + steps bits: prints the newton / prefix / step totals of the program's own counters
          bench_r3 d          poly_gcd_own(g, R - 1) for random g (m + 1 coefficients, monic) and R - 1 (m coefficients): total ops and peak */
#include "attack.h"
#include "hgcd.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#ifndef AMAXB
#define AMAXB 20
#endif
int main(int argc, char **argv) {
    char mode = argc > 1 ? argv[1][0] : 'c';
    int steps = argc > 2 ? atoi(argv[2]) : 2;
    size_t m = poly_degree_m(3);
    rng_seed(5);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    ntt_init(AMAXB);
    fp *g = NEW_FP(m + 1);
    for (size_t i = 0; i < m; i++) rnd_fp254(&g[i]);
    fp_set_one(&g[m]);
    mem_reset_peak();
    snap_t s0 = snap();
    if (mode == 'c') {
        fp *F = NEW_FP(m);
        uint64_t E[4] = { ((uint64_t)0x80000 << steps) | (((uint64_t)1 << steps) - 1), 0, 0, 0 };
        powx_lean(F, g, m, E, 2);
        { uint64_t h = 1469598103934665603ULL; for (size_t i = 0; i < m; i++) for (int l = 0; l < 4; l++) { h ^= F[i].l[l]; h *= 1099511628211ULL; } printf("checksum F %016llx\n", (unsigned long long)h); }
        printf("bench c steps=%d total=%llu\n", steps, (unsigned long long)snap_total(snap_sub(snap(), s0)));
    } else {
        fp *R = NEW_FP(m);
        for (size_t i = 0; i < m; i++) rnd_fp254(&R[i]);
        size_t lG = 0;
        fp *G = poly_gcd_own(&lG, g, m + 1, R, m);
        printf("bench d gcd_len=%zu total=%llu\n", lG, (unsigned long long)snap_total(snap_sub(snap(), s0)));
        (void)G;
    }
    printf("mem_peak=%zu bytes (%.4f M slots) arena_hwm=%zu live_at_peak=%zu\n", mem_peak, mem_peak / 32.0 / 1e6, arena_hwm, mem_peak_live);
    return 0;
}
