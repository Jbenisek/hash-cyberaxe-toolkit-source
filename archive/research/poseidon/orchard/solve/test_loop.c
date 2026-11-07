#include "common.h"
#include <time.h>
static uint64_t rs = 1234567891234567ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }

/* a (deg < m) -> a mod g (g monic deg m), naive */
static void polymod_naive(fp *a, size_t la, const fp *g, size_t m) {
    for (size_t i = la; i-- > m;) {
        fp c = a[i];
        if (fp_is_zero(&c)) continue;
        for (size_t j = 0; j <= m; j++) { fp t; fp_mul(&t, &c, &g[j]); fp_sub(&a[i - m + j], &a[i - m + j], &t); }
    }
}
static void mulmod_naive(fp *r, const fp *a, const fp *b, const fp *g, size_t m) {
    fp *t = calloc(2 * m, sizeof(fp));
    for (size_t i = 0; i < m; i++) for (size_t j = 0; j < m; j++) { fp u; fp_mul(&u, &a[i], &b[j]); fp_add(&t[i + j], &t[i + j], &u); }
    polymod_naive(t, 2 * m - 1, g, m);
    memcpy(r, t, m * sizeof(fp)); free(t);
}
static int ebit(const uint64_t E[4], int i) { return (int)((E[i / 64] >> (i % 64)) & 1); }
static void powx_naive(fp *out, const fp *g, size_t m, const uint64_t E[4]) {
    int top = 255; while (top > 0 && !ebit(E, top)) top--;
    fp *acc = calloc(m, sizeof(fp)); fp one; fp_set_one(&one);
    if (m > 1) acc[1] = one; else { /* x = -g0 */ fp_neg(&acc[0], &g[0]); }
    for (int b = top - 1; b >= 0; b--) {
        mulmod_naive(acc, acc, acc, g, m);
        if (ebit(E, b)) {  /* multiply by x */
            fp c = acc[m - 1];
            for (size_t i = m - 1; i >= 1; i--) { fp t; fp_mul(&t, &c, &g[i]); fp_sub(&acc[i], &acc[i - 1], &t); }
            fp t; fp_mul(&t, &c, &g[0]); fp_neg(&acc[0], &t);
        }
    }
    memcpy(out, acc, m * sizeof(fp)); free(acc);
}
int main(void) {
    ntt_init(12);
    int ok = 1;
    /* Newton */
    size_t ms[] = { 9, 50, 301, 1000 };
    for (int t = 0; t < 4; t++) {
        size_t m = ms[t];
        fp *g = NEW_FP(m + 1), *mu = NEW_FP(m - 1);
        for (size_t i = 0; i < m; i++) rnd_fp(&g[i]);
        fp_set_one(&g[m]);
        poly_newton_mu(mu, g, m);
        /* check: x^(2m-2) = mu*g + rho with deg rho < m */
        fp *prod = calloc(2 * m, sizeof(fp));
        poly_mul_naive(prod, mu, m - 1, g, m + 1);   /* degree 2m-2 */
        int good = 1; fp one; fp_set_one(&one);
        if (!fp_eq(&prod[2 * m - 2], &one)) good = 0;
        for (size_t i = m; i < 2 * m - 2 && good; i++) if (!fp_is_zero(&prod[i])) good = 0;
        printf("newton m=%zu: %s\n", m, good ? "ok" : "FAIL"); ok &= good;
        free(prod); xfree(g); xfree(mu);
    }
    /* powx_mod */
    size_t mm[] = { 5, 40, 200, 600 };
    for (int t = 0; t < 4; t++) {
        size_t m = mm[t];
        fp *g = NEW_FP(m + 1), *o1 = NEW_FP(m), *o2 = NEW_FP(m);
        for (size_t i = 0; i < m; i++) rnd_fp(&g[i]);
        fp_set_one(&g[m]);
        uint64_t E[4] = { rnd64(), rnd64() >> 3, 0, 0 };
        for (int variant = 0; variant < 2; variant++) {
            powx_mod(o1, g, m, E, variant, 1);
            powx_naive(o2, g, m, E);
            int good = 1; for (size_t i = 0; i < m; i++) if (!fp_eq(&o1[i], &o2[i])) { good = 0; break; }
            printf("powx m=%zu rows3=%d: %s\n", m, variant, good ? "ok" : "FAIL"); ok &= good;
        }
        xfree(g); xfree(o1); xfree(o2);
    }
    printf(ok ? "LOOP TESTS PASSED\n" : "LOOP TESTS FAILED\n");
    return !ok;
}
