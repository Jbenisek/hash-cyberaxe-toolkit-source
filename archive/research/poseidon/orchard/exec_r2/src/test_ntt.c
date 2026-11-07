#include "common.h"
#include <time.h>

static uint64_t rs = 88172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }

static void horner(fp *r, const fp *x, size_t len, const fp *pt) {
    fp acc; fp_set_zero(&acc);
    for (size_t i = len; i-- > 0;) { fp_mul(&acc, &acc, pt); fp_add(&acc, &acc, &x[i]); }
    *r = acc;
}
static int test_plan(int rows, int a, size_t len) {
    plan_t P = make_plan(rows, a);
    size_t N = P.N;
    fp *x = NEW_FP(N), *y = NEW_FP(N);
    for (size_t i = 0; i < len; i++) rnd_fp(&x[i]);
    for (size_t i = len; i < N; i++) rnd_fp(&x[i]);   /* garbage beyond len must be ignored */
    ntt_fwd(&P, y, x, 0, len);
    fp theta; plan_theta(&P, &theta);
    int ok = 1;
    fp pt; fp_set_one(&pt);
    size_t step = N > 4096 ? N / 997 + 1 : 1;
    for (size_t k = 0; k < N; k += step) {
        fp_pow(&pt, &theta, (uint64_t[4]){ k, 0, 0, 0 });
        fp ev; horner(&ev, x, len, &pt);
        if (!fp_eq(&ev, &y[layout_index(&P, k)])) { ok = 0; printf("  eval mismatch rows=%d a=%d k=%zu\n", rows, a, k); break; }
    }
    /* inverse */
    ntt_inv(&P, y, len);
    fp Nf; { uint64_t v[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, v); }
    for (size_t i = 0; i < len && ok; i++) { fp t; fp_mul(&t, &x[i], &Nf); if (!fp_eq(&t, &y[i])) { ok = 0; printf("  roundtrip mismatch i=%zu\n", i); } }
    xfree(x); xfree(y);
    printf("plan rows=%d a=%d N=%zu len=%zu: %s\n", rows, a, N, len, ok ? "ok" : "FAIL");
    return ok;
}
/* cyclic convolution test of conv_sq and conv_mulc against schoolbook */
static int test_conv(int rows, int a, size_t len) {
    plan_t P = make_plan(rows, a); size_t N = P.N;
    fp *x = NEW_FP(N), *y = NEW_FP(N), *z = NEW_FP(N), *c = NEW_FP(N), *cc = NEW_FP(N);
    for (size_t i = 0; i < N; i++) { rnd_fp(&x[i]); rnd_fp(&c[i]); }
    /* conv_sq */
    memcpy(y, x, N * sizeof(fp));
    conv_sq(&P, y, len, N);
    fp *ref = NEW_FP(N); fp_cnt.add += 0;
    for (size_t i = 0; i < N; i++) fp_set_zero(&ref[i]);
    size_t lim = len < 600 ? len : 600; /* naive test on first part only when large */
    int ok = 1;
    if (len <= 700) {
        for (size_t i = 0; i < len; i++) for (size_t j = 0; j < len; j++) { fp t; fp_mul(&t, &x[i], &x[j]); fp_add(&ref[(i + j) % N], &ref[(i + j) % N], &t); }
        fp Nf; { uint64_t v[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, v); }
        for (size_t i = 0; i < N && ok; i++) { fp t; fp_mul(&t, &ref[i], &Nf); if (!fp_eq(&t, &y[i])) { ok = 0; printf("  conv_sq mismatch i=%zu\n", i); } }
    }
    (void)lim;
    /* conv_mulc: C = fwd(cpoly), z = conv_mulc(x[off..off+len), C) */
    ntt_fwd(&P, cc, c, 0, N);
    size_t off = 3;
    conv_mulc(&P, z, x, off, len, cc, N);
    if (len <= 700) {
        for (size_t i = 0; i < N; i++) fp_set_zero(&ref[i]);
        for (size_t i = 0; i < len; i++) for (size_t j = 0; j < N; j++) { fp t; fp_mul(&t, &x[off + i], &c[j]); fp_add(&ref[(i + j) % N], &ref[(i + j) % N], &t); }
        fp Nf; { uint64_t v[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, v); }
        for (size_t i = 0; i < N && ok; i++) { fp t; fp_mul(&t, &ref[i], &Nf); if (!fp_eq(&t, &z[i])) { ok = 0; printf("  conv_mulc mismatch i=%zu\n", i); } }
    }
    xfree(x); xfree(y); xfree(z); xfree(c); xfree(cc); xfree(ref);
    printf("conv rows=%d a=%d N=%zu len=%zu: %s\n", rows, a, N, len, ok ? "ok" : "FAIL");
    return ok;
}
int main(void) {
    ntt_init(12);
    int ok = 1;
    int as[] = { 2, 3, 4, 5, 6, 7, 8, 9, 11 };
    for (int i = 0; i < 9; i++) {
        int a = as[i];
        ok &= test_plan(1, a, ((size_t)1 << a) * 3 / 5 + 1);
        ok &= test_plan(3, a, 3 * ((size_t)1 << a) * 2 / 5 + 1);
        ok &= test_plan(3, a, 3 * ((size_t)1 << a));
    }
    ok &= test_conv(1, 6, 40); ok &= test_conv(3, 5, 60); ok &= test_conv(3, 7, 200); ok &= test_conv(1, 9, 300);
    ok &= test_conv(3, 8, 600);
    printf(ok ? "NTT TESTS PASSED\n" : "NTT TESTS FAILED\n");
    return !ok;
}
