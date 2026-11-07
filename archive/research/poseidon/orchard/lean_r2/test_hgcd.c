#include "common.h"
#include "hgcd.h"
#include <time.h>
static uint64_t rs = 99172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    size_t n = argc > 1 ? strtoul(argv[1], 0, 10) : 3000;    /* degree of a */
    size_t d = argc > 2 ? strtoul(argv[2], 0, 10) : 3;       /* degree of the planted gcd */
    int naive = argc > 3 ? atoi(argv[3]) : 1;
    ntt_init(15);
    if (argc > 4) hgcd_k1_pct = atoi(argv[4]);
    if (argc > 5) hgcd_base_k = atoi(argv[5]);
    if (argc > 6) budget_arm((uint64_t)strtoull(argv[6], 0, 10), "test-gcd");
    size_t la = n + 1, lb = n;                                /* b has degree n-1 */
    /* a = f*u, b = f*v with deg f = d, deg u = n-d, deg v = n-1-d */
    fp *f = NEW_FP(d + 1), *u = NEW_FP(n - d + 1), *v = NEW_FP(n - d);
    for (size_t i = 0; i <= d; i++) rnd_fp(&f[i]);
    for (size_t i = 0; i <= n - d; i++) rnd_fp(&u[i]);
    for (size_t i = 0; i < n - d; i++) rnd_fp(&v[i]);
    fp *a = NEW_FP(la), *b = NEW_FP(lb);
    snap_t keep = snap();
    poly_mul(a, f, d + 1, u, n - d + 1);
    poly_mul(b, f, d + 1, v, n - d);
    snap_restore(keep);
    fp *o1 = NEW_FP(la), *o2 = NEW_FP(la);
    size_t base = mem_cur; mem_reset_peak();
    snap_t s0 = snap(); clock_t c0 = clock();
    size_t g1 = poly_gcd_fast(o1, a, la, b, lb);
    snap_t d1 = snap_sub(snap(), s0); double t1 = (double)(clock() - c0) / CLOCKS_PER_SEC; size_t pk = mem_peak - base;
    printf("hgcd: deg gcd = %zu (planted %zu) arith=%llu total=%llu extra peak=%zu bytes, %.1fs\n", g1 - 1, d, (unsigned long long)snap_arith(d1), (unsigned long long)snap_total(d1), pk, t1);
    int good = (g1 == d + 1);
    if (naive) {
        s0 = snap(); c0 = clock();
        size_t g2 = poly_gcd_naive(o2, a, la, b, lb);
        snap_t d2 = snap_sub(snap(), s0);
        printf("naive: deg gcd = %zu arith=%llu total=%llu %.1fs\n", g2 - 1, (unsigned long long)snap_arith(d2), (unsigned long long)snap_total(d2), (double)(clock() - c0) / CLOCKS_PER_SEC);
        good &= (g2 == g1); for (size_t i = 0; i < g1 && good; i++) if (!fp_eq(&o1[i], &o2[i])) good = 0;
    }
    /* planted gcd must equal f monic */
    { fp inv; fp_inv(&inv, &f[d]); for (size_t i = 0; i <= d && good; i++) { fp t; fp_mul(&t, &f[i], &inv); if (!fp_eq(&t, &o1[i])) good = 0; } }
    printf("mem_cur after gcd (leak check): %zu\n", mem_cur - base);
    printf(good ? "HGCD OK\n" : "HGCD FAIL\n");
    return !good;
}
