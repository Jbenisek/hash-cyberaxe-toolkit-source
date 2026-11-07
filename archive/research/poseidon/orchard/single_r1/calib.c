/* Calibration of the data-independent stage charges used by the worst-case bound of the root-isolation stage.
 * usage: calib d [d ...]   prints:  LEVEL d shift=<charge> pow=<charge> ...  and the heap peaks of the two stages.
 * The charges do not depend on the coefficients (fixed loop counts), so random monic input is used. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(15);
    rng_seed(5);
    for (int i = 1; i < argc; i++) {
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
