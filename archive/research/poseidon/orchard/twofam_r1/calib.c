/* Calibration of the data-independent stage charges used by the worst-case bound of the root-isolation stage.
 * usage: calib d [reps]   prints: LEVEL d shift_charge pow_charge  and the heap peaks of the two stages.
 * The charges do not depend on the coefficients (fixed loop counts), so random monic input is used. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(16);
    rng_seed(5);
    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == 'r') {           /* "rD": the stage that copies a gcd of degree D and removes two roots of x (worst case) */
            size_t d = strtoull(argv[i] + 1, 0, 10);
            fp *G = NEW_FP(d + 1), *Gb = NEW_FP(d + 1); fp rt; rnd_fp254(&rt);
            fp_set_one(&G[d]); for (size_t k = 0; k < d; k++) fp_set_zero(&G[k]);
            /* G = (Z - rt) * Z^(d-1) so that rt is a root of G and of the deflated polynomial (rt is a root only of the first factor): use Z^(d-1) (Z - rt) and root 0 */
            fp_neg(&G[d - 1], &rt);
            fp zero; fp_set_zero(&zero);
            snap_t s0 = snap();
            memcpy(Gb, G, (d + 1) * sizeof(fp)); LD(d + 1); ST(d + 1); loopc(d + 1);
            fp *H = deflate(Gb, d, &zero); fp *H2 = deflate(H, d - 1, &zero);
            printf("REMOVE d=%zu charged=%llu\n", d, (unsigned long long)snap_total(snap_sub(snap(), s0)));
            xfree(H2); xfree(G);
            continue;
        }
        size_t d = strtoull(argv[i], 0, 10);
        fp *G = NEW_FP(d + 1);
        for (size_t k = 0; k < d; k++) rnd_fp254(&G[k]);
        fp_set_one(&G[d]);
        fp a; rnd_fp254(&a);
        size_t base = mem_cur; mem_reset_peak();
        snap_t s0 = snap(); clock_t c0 = clock();
        G = taylor_shift(G, d, &a);
        uint64_t sh = snap_total(snap_sub(snap(), s0)); size_t pk1 = mem_peak; double t1 = (double)(clock() - c0) / CLOCKS_PER_SEC;
        fp *S = NEW_FP(d);
        base = mem_cur; mem_reset_peak();
        s0 = snap(); c0 = clock();
        pow_half(S, G, d);
        uint64_t pw = snap_total(snap_sub(snap(), s0)); size_t pk2 = mem_peak; double t2 = (double)(clock() - c0) / CLOCKS_PER_SEC;
        printf("LEVEL d=%zu shift=%llu pow=%llu shift_abs_peak=%zu pow_abs_peak=%zu live_before=%zu secs %.1f %.1f\n", d, (unsigned long long)sh, (unsigned long long)pw, pk1, pk2, mem_cur, t1, t2);
        fflush(stdout);
        xfree(S); xfree(G);
    }
    return 0;
}
