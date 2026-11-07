/* not shipped: checks of the rows==2 (twisted radix-2) stage against a naive cyclic convolution, for rows 2 and 3 plans, and a powx_lean comparison.
   build (WSL): gcc -O2 -DNO_R2 or not -o t_r2 test/t_r2.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c   (normal libc) */
#include "../attack.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static int bad = 0;
static void expect(int ok, const char *what) { if (!ok) { bad++; printf("FAIL %s\n", what); } }

/* naive N * (src * c mod x^N-1), c[pos] = B[(pos + N - boff) % N] if < lenB */
static void naive_cyc(fp *out, const fp *src, size_t len, const fp *B, size_t lenB, size_t boff, size_t N) {
    for (size_t i = 0; i < N; i++) fp_set_zero(&out[i]);
    for (size_t j = 0; j < len; j++) for (size_t t = 0; t < lenB; t++) {
        size_t pos = (t + boff) % N, k = (j + pos) % N; fp x; fp_mul(&x, &src[j], &B[t]); fp_add(&out[k], &out[k], &x);
    }
    fp Nf; uint64_t v[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, v);
    for (size_t i = 0; i < N; i++) fp_mul(&out[i], &out[i], &Nf);
}
static int eqv(const fp *a, const fp *b, size_t n) { for (size_t i = 0; i < n; i++) if (memcmp(&a[i], &b[i], sizeof(fp))) return 0; return 1; }

static void run_plan(int rows, int a, size_t len, size_t lenB, size_t boff, size_t outlen) {
    plan_t P = make_plan(rows, a); size_t N = P.N, n = P.n;
    if (len > N || lenB > N) return;
    fp *src = NEW_FP(len), *B = NEW_FP(lenB), *Y = NEW_FP(N), *tmp = NEW_FP(n), *ref = NEW_FP(N), *Y2 = NEW_FP(N);
    for (size_t i = 0; i < len; i++) rnd_fp254(&src[i]);
    for (size_t i = 0; i < lenB; i++) rnd_fp254(&B[i]);
    naive_cyc(ref, src, len, B, lenB, boff, N);
    char msg[160];
    /* conv_mulc_otf (in place) */
    memcpy(Y, src, len * sizeof(fp));
    conv_mulc_otf(&P, Y, Y, 0, len, tmp, B, lenB, boff, outlen);
    snprintf(msg, sizeof msg, "mulc_otf rows=%d a=%d len=%zu lenB=%zu boff=%zu outlen=%zu", rows, a, len, lenB, boff, outlen);
    expect(eqv(Y, ref, outlen), msg);
    /* cached spectrum variant: conv_mulc with ntt_fwd_shifted */
    fp *H = NEW_FP(N); ntt_fwd_shifted(&P, H, B, lenB, boff);
    conv_mulc(&P, Y2, src, 0, len, H, outlen);
    snprintf(msg, sizeof msg, "mulc(cached) rows=%d a=%d len=%zu lenB=%zu boff=%zu outlen=%zu", rows, a, len, lenB, boff, outlen);
    expect(eqv(Y2, ref, outlen), msg);
    /* round trip */
    ntt_fwd(&P, Y2, src, 0, len); ntt_inv(&P, Y2, N);
    fp Nf; uint64_t v[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, v);
    int okrt = 1; for (size_t i = 0; i < N; i++) { fp e; if (i < len) fp_mul(&e, &src[i], &Nf); else fp_set_zero(&e); if (memcmp(&e, &Y2[i], sizeof e)) { okrt = 0; break; } }
    snprintf(msg, sizeof msg, "roundtrip rows=%d a=%d len=%zu", rows, a, len); expect(okrt, msg);
    /* square */
    naive_cyc(ref, src, len, src, len, 0, N);
    memcpy(Y, src, len * sizeof(fp)); conv_sq(&P, Y, len, N);
    snprintf(msg, sizeof msg, "sq rows=%d a=%d len=%zu", rows, a, len); expect(eqv(Y, ref, N), msg);
    xfree(Y2); xfree(H); xfree(ref); xfree(tmp); xfree(Y); xfree(B); xfree(src);
}

int main(void) {
    ntt_init(8);
    rng_seed(77);
    int cases = 0;
    for (int rows = 2; rows <= 3; rows++) for (int a = 2; a <= 6; a++) {
        size_t N = (size_t)rows << a;
        size_t lens[4] = { 1, N / 3 + 1, N / 2, N };
        for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++) {
            size_t len = lens[i], lenB = lens[j]; if (len > N || lenB > N || !len || !lenB) continue;
            size_t bo[3] = { 0, N / 3, N - lenB + 1 > N ? 0 : N - lenB + 1 };
            for (int b = 0; b < 3; b++) { run_plan(rows, a, len, lenB, bo[b] % N, N); cases++; }
            run_plan(rows, a, len, lenB, 0, len + lenB - 1 < N ? len + lenB - 1 : N); cases++;
        }
    }
    /* polynomial product through poly_mul (conv_sum_otf) against the naive product, lengths where plan3_for_len picks rows 2 and rows 3 */
    for (size_t la = 25; la <= 300; la += 37) for (size_t lb = 25; lb <= 300; lb += 53) {
        fp *A = NEW_FP(la), *B = NEW_FP(lb), *R1 = NEW_FP(la + lb), *R2 = NEW_FP(la + lb);
        for (size_t i = 0; i < la; i++) rnd_fp254(&A[i]);
        for (size_t i = 0; i < lb; i++) rnd_fp254(&B[i]);
        poly_mul(R1, A, la, B, lb); poly_mul_naive(R2, A, la, B, lb);
        char msg[80]; snprintf(msg, sizeof msg, "poly_mul %zu x %zu (rows %d)", la, lb, plan3_for_len(la + lb - 1).rows); expect(eqv(R1, R2, la + lb - 1), msg);
        xfree(R2); xfree(R1); xfree(B); xfree(A); cases++;
    }
    printf("t_r2: %d cases, %d failures\n", cases, bad);
    return bad != 0;
}
