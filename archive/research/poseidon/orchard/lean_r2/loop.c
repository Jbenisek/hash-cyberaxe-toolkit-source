/* x^E mod g by left-to-right square-and-multiply with Barrett reduction in the transform domain.
 *
 * State s = a / N (N = size of the big cyclic transform) so that no explicit scaling is ever needed:
 *   Y := conv_sq(s) = N*(s*s) = a^2/N = T/N                               (T = a^2, degree <= 2m-2)
 *   Z := conv(T1/N, mu') = q                      T1 = coefficients m..2m-2 of T, mu' = x^(N-m+2)*mu  (window lands at 0..m-2)
 *   Z := conv_{N'}(q, g)/(N N') = (q g mod x^N'-1)/N
 *   Y_i := Y_i + Y_{i+N'} - Z_i  (i < m)  = (T mod (x^N'-1) - q g mod (x^N'-1))/N = (T - q g)/N = a_new / N   (N' >= m)
 * Barrett quotient: q = floor(T1 * mu / x^(m-2)), mu = floor(x^(2m-2)/g), T1 = floor(T / x^m)  (exact for polynomials).
 * "x * s mod g" (when the exponent bit is 1) is a streaming shift with subtraction of lead * g. */
#include "common.h"
#include <time.h>

static int ebit(const uint64_t E[4], int i) { return (int)((E[i / 64] >> (i % 64)) & 1); }

static void mulx(fp *Y, const fp *G, size_t m) {
    fp c = Y[m - 1]; LD(1);
    for (size_t i = m - 1; i >= 1; i--) {
        fp t; fp_mul(&t, &c, &G[i]); fp_sub(&Y[i], &Y[i - 1], &t);
    }
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&Y[0], &t);
    LD(2 * m); ST(m); loopc(m);
}

static void combine(fp *Y, const fp *Z, size_t m, size_t Np) {
    for (size_t i = 0; i < m; i++) {
        fp y = Y[i];
        if (i + Np <= 2 * m - 2) { fp_add(&y, &y, &Y[i + Np]); LD(1); }
        fp_sub(&y, &y, &Z[i]);
        Y[i] = y;
    }
    LD(2 * m); ST(m); loopc(m);
}

void powx_mod(fp *out, const fp *g, size_t m, const uint64_t E[4], int force_rows3, int quiet) {
    plan_t PN, PNp;
    if (force_rows3) {
        int a = 2; while (3 * ((size_t)1 << a) < 2 * m - 1) a++; PN = make_plan(3, a);
        a = 2; while (3 * ((size_t)1 << a) < m + 1) a++; PNp = make_plan(3, a);
    } else { PN = plan_for_len(2 * m - 1, 1); PNp = plan_for_len(m + 1, 1); }
    size_t N = PN.N, Np = PNp.N;
    fp *Y = NEW_FP(N), *Z = NEW_FP(N), *CM = NEW_FP(N), *CG = NEW_FP(Np);
    /* Barrett data */
    {
        fp *mu = NEW_FP(m - 1);
        poly_newton_mu(mu, g, m);
        size_t gamma = N - (m - 2);
        for (size_t i = 0; i < N; i++) fp_set_zero(&CM[i]);
        ST(N); loopc(N);
        for (size_t i = 0; i < m - 1; i++) { CM[(i + gamma) % N] = mu[i]; }
        LD(m - 1); ST(m - 1); loopc(m - 1);
        xfree(mu);
        ntt_fwd(&PN, CM, CM, 0, N);
        /* g transform at size N', scaled by 1/(N N') */
        memcpy(CG, g, (m + 1) * sizeof(fp)); LD(m + 1); ST(m + 1); loopc(m + 1);
        ntt_fwd(&PNp, CG, CG, 0, m + 1);
        fp i1, i2, sc; plan_invN(&PN, &i1); plan_invN(&PNp, &i2); fp_mul(&sc, &i1, &i2);
        for (size_t i = 0; i < Np; i++) fp_mul(&CG[i], &CG[i], &sc);
        LD(Np); ST(Np); loopc(Np);
    }
    /* exponent prefix: start from the monomial x^v with v < m */
    int top = 255; while (top > 0 && !ebit(E, top)) top--;
    size_t v = 1; int bit = top;
    while (bit >= 1 && ((v << 1) | (size_t)ebit(E, bit - 1)) < m) { v = (v << 1) | (size_t)ebit(E, bit - 1); bit--; CTL(2); }
    for (size_t i = 0; i < m; i++) fp_set_zero(&Y[i]);
    ST(m); loopc(m);
    { fp invN; plan_invN(&PN, &invN); Y[v] = invN; ST(1); }
    clock_t t0 = clock(); int steps = 0;
    for (int b = bit - 1; b >= 0; b--) {
        conv_sq(&PN, Y, m, 2 * m - 1);
        conv_mulc(&PN, Z, Y, m, m - 1, CM, m - 1);
        conv_mulc(&PNp, Z, Z, 0, m - 1, CG, m);
        combine(Y, Z, m, Np);
        if (ebit(E, b)) mulx(Y, g, m);
        CTL(3);
        steps++;
        if (!quiet && steps % 32 == 0) fprintf(stderr, "  step %d/%d  %.1fs\n", steps, bit, (double)(clock() - t0) / CLOCKS_PER_SEC);
    }
    { fp Nf; uint64_t vv[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, vv);
      for (size_t i = 0; i < m; i++) fp_mul(&out[i], &Y[i], &Nf);
      LD(m); ST(m); loopc(m); }
    xfree(Y); xfree(Z); xfree(CM); xfree(CG);
}
