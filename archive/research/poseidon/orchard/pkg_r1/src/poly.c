/* Generic polynomial multiplication (NTT based, counted), Newton reciprocal for Barrett reduction. */
#include "common.h"

/* cache of 1/N per plan size */
static struct { size_t N; fp inv; int used; } invcache[64];
void plan_invN(const plan_t *P, fp *out) {
    for (int i = 0; i < 64; i++) if (invcache[i].used && invcache[i].N == P->N) { *out = invcache[i].inv; return; }
    fp Nf; uint64_t v[4] = { P->N, 0, 0, 0 }; fp_from_limbs(&Nf, v);
    fp inv; fp_inv(&inv, &Nf);
    for (int i = 0; i < 64; i++) if (!invcache[i].used) { invcache[i].used = 1; invcache[i].N = P->N; invcache[i].inv = inv; break; }
    *out = inv;
}

void poly_mul_naive(fp *r, const fp *a, size_t la, const fp *b, size_t lb) {
    if (!la || !lb) return;
    for (size_t k = 0; k < la + lb - 1; k++) {
        size_t lo = k >= lb ? k - lb + 1 : 0, hi = k < la ? k : la - 1;
        fp acc; fp_set_zero(&acc); int first = 1;
        for (size_t i = lo; i <= hi; i++) {
            fp t; fp_mul(&t, &a[i], &b[k - i]);
            if (first) { acc = t; first = 0; } else fp_add(&acc, &acc, &t);
            LD(2);
        }
        r[k] = acc; ST(1);
    }
    loopc(la * lb);
}

void poly_mul(fp *r, const fp *a, size_t la, const fp *b, size_t lb) {
    if (!la || !lb) return;
    size_t len = la + lb - 1;
    if (la <= 24 || lb <= 24) { poly_mul_naive(r, a, la, b, lb); return; }
    plan_t P = plan_for_len(len, 1);
    fp *tA = NEW_FP(P.N), *tB = NEW_FP(P.N);
    ntt_fwd(&P, tA, a, 0, la);
    ntt_fwd(&P, tB, b, 0, lb);
    for (size_t i = 0; i < P.N; i++) fp_mul(&tA[i], &tA[i], &tB[i]);
    LD(2 * P.N); ST(P.N); loopc(P.N);
    ntt_inv(&P, tA, len);
    fp inv; plan_invN(&P, &inv);
    for (size_t i = 0; i < len; i++) fp_mul(&r[i], &tA[i], &inv);
    LD(len); ST(len); loopc(len);
    xfree(tA); xfree(tB);
}

/* mu = floor(x^(2m-2)/g), g monic degree m; mu has m-1 coefficients mu[0..m-2].
 * rev(g) mod x^(m-1) is inverted by Newton iteration (nu_{2l} = nu_l - x^l (nu_l * mid(rev(g) nu_l)) ), then mu_i = nu_{m-2-i}. */
void poly_newton_mu(fp *mu, const fp *g, size_t m) {
    size_t L = m - 1;
    fp *gr = NEW_FP(L), *nu = NEW_FP(L);
    for (size_t i = 0; i < L; i++) gr[i] = g[m - i];
    LD(L); ST(L); loopc(L);
    fp one; fp_set_one(&one);
    if (!fp_eq(&gr[0], &one)) { fprintf(stderr, "newton: g not monic\n"); exit(6); }
    nu[0] = one; ST(1);
    size_t l = 1;
    while (l < L) {
        size_t l2 = 2 * l < L ? 2 * l : L;
        fp *e = NEW_FP(l2 + l - 1);
        poly_mul(e, gr, l2, nu, l);                /* low l coefficients are 1,0,..,0 */
        fp *f = NEW_FP(2 * (l2 - l) + l);
        poly_mul(f, nu, l, e + l, l2 - l);         /* (nu * mid) , need first l2-l coefficients */
        for (size_t i = 0; i < l2 - l; i++) fp_neg(&nu[l + i], &f[i]);
        LD(l2 - l); ST(l2 - l); loopc(l2 - l);
        xfree(e); xfree(f);
        l = l2;
    }
    for (size_t i = 0; i < L; i++) mu[i] = nu[L - 1 - i];
    LD(L); ST(L); loopc(L);
    xfree(gr); xfree(nu);
}
