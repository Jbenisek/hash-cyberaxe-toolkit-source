/* gcd_cl on A = P (x - a), B = Q (x - a) with random P, Q: the gcd must be x - a.  usage: test_gcd d */
#include "attack.h"
static fp *mullin(const fp *P, size_t dp, const fp *a) {      /* P (x - a), P has dp+1 coefficients */
    fp *R = NEW_FP(dp + 2); fp na; fp_neg(&na, a);
    for (size_t i = 0; i <= dp + 1; i++) {
        fp t, u; fp_set_zero(&t); fp_set_zero(&u);
        if (i >= 1) t = P[i - 1];
        if (i <= dp) fp_mul(&u, &P[i], &na);
        fp_add(&R[i], &t, &u);
    }
    return R;
}
int main(int argc, char **argv) {
    ntt_init(18); rng_seed(3);
    size_t d = strtoull(argv[1], 0, 0);
    fp a; rnd_fp254(&a);
    fp *P = NEW_FP(d), *Q = NEW_FP(d - 1);
    for (size_t i = 0; i < d; i++) rnd_fp254(&P[i]);
    for (size_t i = 0; i + 1 < d; i++) rnd_fp254(&Q[i]);
    fp *A = mullin(P, d - 1, &a), *B = mullin(Q, d - 2, &a);     /* degrees d and d-1 */
    fp *out = NEW_FP(d + 1);
    size_t dg = gcd_cl(out, A, d, B, d - 1);
    fp na; fp_neg(&na, &a);
    printf("d=%zu gcd degree %zu, root ok: %d\n", d, dg, dg == 1 && fp_eq(&out[0], &na));
    return !(dg == 1 && fp_eq(&out[0], &na));
}
