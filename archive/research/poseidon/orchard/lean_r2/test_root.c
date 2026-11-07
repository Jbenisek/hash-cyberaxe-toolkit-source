#include "attack.h"
#include "pallas_consts.h"
int main(int argc, char **argv) {
    ntt_init(12); rng_seed(7);
    int tot_fail = 0; uint64_t worst = 0, sum = 0; int n = 0;
    for (size_t d = 1; d <= 8; d++) for (int rep = 0; rep < 40; rep++) {
        fp roots[8]; for (size_t i = 0; i < d; i++) rnd_fp254(&roots[i]);
        fp G[9]; fp_set_one(&G[0]); size_t deg = 0;           /* product of (x - r_i), ascending coefficients */
        G[0] = roots[0]; fp_neg(&G[0], &G[0]); fp_set_one(&G[1]); deg = 1;
        for (size_t i = 1; i < d; i++) {
            fp nr; fp_neg(&nr, &roots[i]); fp H[9]; fp_set_zero(&H[0]);
            for (size_t k = 0; k <= deg; k++) { H[k + 1] = G[k]; }
            fp_set_zero(&H[0]);
            for (size_t k = 0; k <= deg; k++) { fp t; fp_mul(&t, &G[k], &nr); if (k == 0) H[0] = t; else fp_add(&H[k], &H[k], &t); }
            deg++; for (size_t k = 0; k <= deg; k++) G[k] = H[k];
        }
        snap_t s0 = snap(); fp S; int ok = find_root(&S, G, d); snap_t dd = snap_sub(snap(), s0);
        uint64_t t = snap_total(dd); sum += t; n++; if (t > worst) worst = t;
        if (!ok) tot_fail++;
        else { int found = 0; for (size_t i = 0; i < d; i++) if (fp_eq(&S, &roots[i])) found = 1; if (!found) { printf("wrong root\n"); return 1; } }
        if (rep == 0 && d == 8) printf("d=8 sample cost %llu\n", (unsigned long long)t);
    }
    printf("runs=%d fails=%d mean=%llu worst=%llu\n", n, tot_fail, (unsigned long long)(sum / n), (unsigned long long)worst);
    return 0;
}
