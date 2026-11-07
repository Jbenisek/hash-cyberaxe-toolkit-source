/* Test of split_find_root_capped on synthetic G = prod (Z - r_i), d = 1..DMAX (not part of the shipped program). */
#include "attack.h"
#include "outbuf.h"
int main(int argc, char **argv) {
    (void)argc; (void)argv;
    rng_seed(7);
    for (int d = 1; d <= 16; d++) for (int rep = 0; rep < 3; rep++) {
        fp r[16]; fp *G = NEW_FP(d + 1);
        for (int i = 0; i <= d; i++) fp_set_zero(&G[i]);
        fp_set_one(&G[0]);
        int deg = 0;
        for (int i = 0; i < d; i++) {
            rnd_fp254(&r[i]);
            fp nr; fp_neg(&nr, &r[i]);
            for (int k = deg + 1; k >= 0; k--) { fp t; fp_mul(&t, &G[k], &nr); if (k) fp_add(&t, &t, &G[k - 1]); G[k] = t; }
            deg++;
        }
        /* only roots that are squares are in the real use; here any distinct roots */
        fp root; int ok = split_find_root_capped(&root, G, (size_t)d);
        int hit = 0; for (int i = 0; i < d; i++) if (fp_eq(&root, &r[i])) hit = 1;
        printf("d=%d rep=%d ok=%d hit=%d rounds_total=%llu\n", d, rep, ok, hit, (unsigned long long)SPL_tries);
    }
    out_flush();
    return 0;
}
