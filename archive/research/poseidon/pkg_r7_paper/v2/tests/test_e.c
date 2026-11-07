/* Test program of Appendix C.  Measures the counters of split_find_root_capped on synthetic G (product of d distinct linear factors), d = 2..16, and of the coin draw. */
#include "attack.h"
#include "outbuf.h"
int main(int argc, char **argv) {
    (void)argc; (void)argv;
    rng_seed(11);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    { fp c; snap_t s0 = snap(); rnd_fp320(&c); printf("COIN draw total=%llu\n", (unsigned long long)snap_total(snap_sub(snap(), s0))); }
    for (int d = 2; d <= 16; d++) for (int rep = 0; rep < 6; rep++) {
        fp *G = NEW_FP(d + 1);
        for (int i = 0; i <= d; i++) fp_set_zero(&G[i]);
        fp_set_one(&G[0]);
        int deg = 0;
        for (int i = 0; i < d; i++) {
            fp r, nr; rnd_fp320(&r); fp_neg(&nr, &r);
            for (int k = deg + 1; k >= 0; k--) { fp t; fp_mul(&t, &G[k], &nr); if (k) fp_add(&t, &t, &G[k - 1]); G[k] = t; }
            deg++;
        }
        uint64_t t0 = SPL_tries;
        snap_t s0 = snap();
        fp root; int ok = split_find_root_capped(&root, G, (size_t)d);
        uint64_t tot = snap_total(snap_sub(snap(), s0));
        printf("E d=%d rep=%d ok=%d rounds=%llu total=%llu\n", d, rep, ok, (unsigned long long)(SPL_tries - t0), (unsigned long long)tot);
    }
    out_flush();
    return 0;
}
