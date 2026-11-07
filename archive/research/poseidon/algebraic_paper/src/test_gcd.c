/* Test of poly_gcd_own on x = G*A, y = G*B with deg G = k = 0..20 (not part of the shipped program). */
#include "attack.h"
#include "hgcd.h"
#include "outbuf.h"
static fp *rnd_poly(size_t n, int monic) { fp *p = NEW_FP(n); for (size_t i = 0; i < n; i++) rnd_fp254(&p[i]); if (monic) fp_set_one(&p[n - 1]); return p; }
int main(int argc, char **argv) {
    (void)argc; (void)argv;
    rng_seed(5);
    ntt_init(18);
    size_t LA = argc > 1 ? 40000 : 40000, LB = 39000;
    for (size_t k = 0; k <= 20; k++) {
        fp *G = rnd_poly(k + 1, 1), *A = rnd_poly(LA, 1), *B = rnd_poly(LB, 1);
        size_t lx = k + LA, ly = k + LB;
        fp *x = NEW_FP(lx), *y = NEW_FP(ly);
        poly_mul(x, G, k + 1, A, LA); poly_mul(y, G, k + 1, B, LB);
        size_t lg; fp *g = poly_gcd_own(&lg, x, lx, y, ly);
        int ok = (lg == k + 1); for (size_t i = 0; ok && i < lg; i++) if (!fp_eq(&g[i], &G[i])) ok = 0;
        printf("k=%zu lg=%zu ok=%d\n", k, lg, ok);
        if (g) xfree(g); xfree(G); xfree(A); xfree(B);
    }
    out_flush();
    return 0;
}
