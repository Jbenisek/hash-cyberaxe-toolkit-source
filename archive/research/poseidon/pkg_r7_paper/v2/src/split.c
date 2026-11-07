/* Stage tools of the two-family attack: classical Euclid gcd, deflation by a known root,
 * Taylor shift, Z^((p-1)/2) mod G, and the isolation of one root of a monic product of distinct linear factors.
 * Every executed operation is charged as in common.h. */
#include "attack.h"
#include "pallas_consts.h"
#include "hgcd.h"

uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;

#define CL_MAX 152          /* classical Euclid up to this degree, the fast gcd above */
static int deg_of(const fp *a, int top) { while (top >= 0 && fp_is_zero(&a[top])) top--; return top; }

/* ---------- classical Euclid.  da, db are degree upper bounds (arrays hold da+1 and db+1 coefficients, not all zero).
 * Writes the monic gcd to out (room max(da,db)+1) and returns its degree. */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db) {
    size_t cap = (da > db ? da : db) + 1;
    fp *A = NEW_FP(cap), *B = NEW_FP(cap);
    memcpy(A, a, (da + 1) * sizeof(fp)); memcpy(B, b, (db + 1) * sizeof(fp));
    LD(da + db + 2); ST(da + db + 2); loopc(da + db + 2);
    int dA = deg_of(A, (int)da), dB = deg_of(B, (int)db);
    CTL(9 * ((uint64_t)((int)da - dA) + (uint64_t)((int)db - dB) + 2) + 4);   /* degree scans: per test index, four-limb zero test, branch, decrement; the comparison and swap below */
    if (dA < dB) { fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td; }
    while (dB >= 0) {
        CTL(2);                                                  /* outer loop test */
        fp ilc; fp_inv(&ilc, &B[dB]); LD(1); CTL(INV_CTL);
        while (dA >= dB) {
            CTL(3);                                              /* loop test, shift sh = dA - dB */
            fp q; fp_mul(&q, &A[dA], &ilc); LD(1);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            LD(2 * (size_t)dB); ST(dB); loopc(dB); CTL(dB);       /* index sh + i */
            fp_set_zero(&A[dA]); ST(1);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            CTL(9 * (uint64_t)(dA - nd + 1) + 6); LD(dA - nd);
            dA = nd;
            if (dA < 0) break;
        }
        CTL(6);                                                  /* swap of the two arrays and degrees */
        fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td;
    }
    CTL(2);
    int dg = dA;
    if (dg < 0) { fprintf(stderr, "gcd of zero polynomials\n"); exit(8); }
    fp il; fp_inv(&il, &A[dg]); LD(1); CTL(INV_CTL);
    for (int i = 0; i <= dg; i++) fp_mul(&out[i], &A[i], &il);
    LD(dg + 1); ST(dg + 1); loopc(dg + 1);
    xfree(A); xfree(B);
    return (size_t)dg;
}

/* ---------- quotient and remainder by naive division ---------- */
static size_t trimlen(const fp *c, size_t len) {
    size_t it = 1;
    while (len > 0 && fp_is_zero(&c[len - 1])) { len--; it++; }
    CTL(9 * it); LD(it);
    return len;
}
void divrem(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) {
    memcpy(r, a, la * sizeof(fp)); LD(la); ST(la); loopc(la);
    fp inv; fp_inv(&inv, &b[lb - 1]); CTL(INV_CTL); LD(1);
    *lq = la - lb + 1;
    for (size_t i = la - lb + 1; i-- > 0;) {
        fp qi; fp_mul(&qi, &r[i + lb - 1], &inv); LD(1);
        q[i] = qi; ST(1);
        for (size_t j = 0; j + 1 < lb; j++) { fp t; fp_mul(&t, &qi, &b[j]); fp_sub(&r[i + j], &r[i + j], &t); }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(lb - 1);
        CTL(3 + 2 + 2);
    }
    *lr = trimlen(r, lb - 1);
}

/* ---------- deflation: G / (Z - r) for a root r of the monic G (d+1 coefficients); returns d coefficients, frees G */
fp *deflate(fp *G, size_t d, const fp *r) {
    fp *Q = NEW_FP(d);
    fp b = G[d];
    Q[d - 1] = b;
    for (size_t k = d - 1; k >= 1; k--) { fp t; fp_mul(&t, r, &b); fp_add(&b, &G[k], &t); Q[k - 1] = b; }
    fp t; fp_mul(&t, r, &b); fp_add(&t, &G[0], &t);
    LD(d + 1); ST(d); loopc(d - 1); CTL(2 * d);
    CTL(4);
    if (!fp_is_zero(&t)) { fprintf(stderr, "deflate: not a root\n"); exit(79); }
    xfree(G);
    return Q;
}

/* ---------- Taylor shift: returns G(Z + a), frees G (monic, d+1 coefficients).
 * out_k = (1/k!) sum_i (i! g_i) (a^(i-k)/(i-k)!): one convolution of A'_(d-i) = i! g_i with B_j = a^j/j!. */
fp *taylor_shift(fp *G, size_t d, const fp *a) {
    size_t n = d + 1;
    fp one; fp_set_one(&one);
    fp *A = NEW_FP(n), *B = NEW_FP(n);
    fp fct = one, ii; fp_set_zero(&ii);
    for (size_t i = 0; i < n; i++) {
        if (i) { fp_add(&ii, &ii, &one); fp_mul(&fct, &fct, &ii); }
        fp_mul(&A[d - i], &G[i], &fct);
    }
    LD(n); ST(n); loopc(n); CTL(2 * n + 1);                         /* the branch i != 0, index d - i */
    xfree(G);
    fp ifd, ainv, pw, inf, jj;
    fp_inv(&ifd, &fct); CTL(INV_CTL);
    uint64_t ev[4] = { (uint64_t)d, 0, 0, 0 };
    fp_pow(&pw, a, ev); CTL(80);                                    /* a^d: bit tests */
    fp_inv(&ainv, a); CTL(INV_CTL);
    inf = ifd; fp_from_limbs(&jj, ev);
    for (size_t j = n; j-- > 0;) {
        fp_mul(&B[j], &pw, &inf);
        fp_mul(&inf, &inf, &jj); fp_sub(&jj, &jj, &one);
        fp_mul(&pw, &pw, &ainv);
    }
    ST(n); loopc(n); CTL(n);
    fp *res = A;                                                     /* the result goes into A once the product is formed */
    CTL(2);                                                          /* the test n <= 48 */
    if (n <= 48) {
        fp *C = NEW_FP(2 * n - 1);
        poly_mul(C, A, n, B, n);
        inf = ifd; fp_from_limbs(&jj, ev);
        for (size_t k = n; k-- > 0;) {
            fp_mul(&res[k], &C[d - k], &inf);
            fp_mul(&inf, &inf, &jj); fp_sub(&jj, &jj, &one);
        }
        LD(n); ST(n); loopc(n); CTL(n);
        xfree(C); xfree(B);
        return res;
    }
    plan_t P = plan3_for_len(2 * n - 1);
    fp *out = NEW_FP(P.N), *tA = NEW_FP(P.n), *tB = NEW_FP(P.n);
    const fp *As[1] = { A }, *Bs[1] = { B }; size_t lA[1] = { n }, lB[1] = { n }; int sg[1] = { 1 };
    conv_sum_otf(&P, out, 1, As, lA, Bs, lB, sg, tA, tB, n);
    fp invN; plan_invN(&P, &invN);
    inf = ifd; fp_mul(&inf, &inf, &invN); fp_from_limbs(&jj, ev);
    for (size_t k = n; k-- > 0;) {
        fp_mul(&res[k], &out[d - k], &inf);
        fp_mul(&inf, &inf, &jj); fp_sub(&jj, &jj, &one);
    }
    LD(n); ST(n); loopc(n); CTL(2 * n);
    xfree(out); xfree(tA); xfree(tB); xfree(B);
    return res;
}

/* ---------- Z^((p-1)/2) mod G.  d <= 40: schoolbook square-and-multiply; otherwise the lean NTT schedule ---------- */
static void sqr_mod(fp *r, const fp *a, const fp *G, size_t d) {
    fp *t = NEW_FP(2 * d);
    for (size_t i = 0; i < 2 * d; i++) fp_set_zero(&t[i]);
    for (size_t i = 0; i < d; i++) {
        fp x; fp_sqr(&x, &a[i]); fp_add(&t[2 * i], &t[2 * i], &x);
        for (size_t j = i + 1; j < d; j++) { fp y; fp_mul(&y, &a[i], &a[j]); fp_add(&y, &y, &y); fp_add(&t[i + j], &t[i + j], &y); }
    }
    for (size_t i = 2 * d - 1; i-- > d;) {
        fp c = t[i];
        for (size_t j = 0; j < d; j++) { fp u; fp_mul(&u, &c, &G[j]); fp_sub(&t[i - d + j], &t[i - d + j], &u); }
        fp_set_zero(&t[i]);
    }
    for (size_t i = 0; i < d; i++) r[i] = t[i];
    xfree(t);
}
static void mulx_mod(fp *r, const fp *G, size_t d) {         /* r := Z r mod G */
    fp c = r[d - 1];
    for (size_t i = d - 1; i >= 1; i--) { fp t; fp_mul(&t, &c, &G[i]); fp_sub(&r[i], &r[i - 1], &t); }
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&r[0], &t);
}
void pow_half(fp *S, const fp *G, size_t d) {
    CTL(2);                                                          /* the test d > 40 */
    if (d > 40) { powx_lean(S, G, d, PALLAS_PM1H, 1); return; }
    snap_t s0 = snap();
    for (size_t i = 0; i < d; i++) fp_set_zero(&S[i]);
    fp_set_one(&S[1]);
    int top = 253; while (top >= 0 && !((PALLAS_PM1H[top / 64] >> (top % 64)) & 1)) { top--; CTL(12); }
    for (int bit = top - 1; bit >= 0; bit--) {
        sqr_mod(S, S, G, d);
        if ((PALLAS_PM1H[bit / 64] >> (bit % 64)) & 1) mulx_mod(S, G, d);
        CTL(3 + 7 + 2 + 3);
    }
    bound_mem_since(s0);
}

/* ---------- number of tries per level: ceil(40/(d-1)) for d <= 40, one try above ---------- */
size_t split_tries(size_t d) { size_t r_; return d > 40 ? 1 : udivmod(40 + d - 2, d - 1, &r_); }   /* the division goes through udivmod (charged there) */

/* Root isolation.  G: monic, d >= 1, product of d distinct linear factors over F_p, d+1 coefficients (consumed).
 * Level: shift by a random c (G(Z - c), roots r + c), S = Z^((p-1)/2) mod G, A = gcd(G, S - 1) = the roots whose shifted value is a
 * nonzero square; the split is proper if 1 <= deg A <= d - 1; continue with the piece of smaller degree (A, or G / A).
 * Returns 0 if a level has no proper split after split_tries(d) tries. */
int split_find_root(fp *root, fp *G, size_t d) {
    fp shift; fp_set_zero(&shift);
    snap_t t0;
    while (d >= 3) {
        size_t t = split_tries(d); int proper = 0;
        CTL(3 + 3 + 5);                                              /* loop test, call of split_tries (two compares, branch, subtract, add; the division is charged inside udivmod) */
        SPL_levels++;
        for (size_t tr = 0; tr < t && !proper; tr++) {
            CTL(3 + 2);
            SPL_tries++;
            fp c, mc; rnd_fp254(&c); fp_neg(&mc, &c);
            t0 = snap();
            G = taylor_shift(G, d, &mc);
            fp_add(&shift, &shift, &c);
            SPL_shift += snap_total(snap_sub(snap(), t0));
            t0 = snap();
            fp *S = NEW_FP(d);
            pow_half(S, G, d);
            SPL_pow += snap_total(snap_sub(snap(), t0));
            t0 = snap();
            fp one; fp_set_one(&one); fp_sub(&S[0], &S[0], &one); LD(1); ST(1);
            fp *Ap; size_t a;
            CTL(2);                                                  /* the test d <= CL_MAX */
            if (d <= CL_MAX) {
                Ap = NEW_FP(d + 1);
                a = gcd_cl(Ap, G, d, S, d - 1);
                xfree(S);
            } else {
                size_t ly = d; while (ly > 0 && fp_is_zero(&S[ly - 1])) ly--;
                CTL(9 * (uint64_t)(d - ly + 1)); LD(d - ly + 1);
                size_t lg;
                Ap = poly_gcd_keep(&lg, G, d + 1, S, ly);
                a = lg - 1;
            }
                        SPL_gcd += snap_total(snap_sub(snap(), t0));
            CTL(4);
            if (a >= 1 && a <= d - 1) {
                size_t b = d - a;
                CTL(3);
                if (a <= b) { xfree(G); G = Ap; d = a; }
                else {
                    t0 = snap();
                    size_t dold = d; fp *q = NEW_FP(b + 1), *rem = NEW_FP(d + 1); size_t lq, lr;
                    divrem_any_pub(q, &lq, rem, &lr, G, d + 1, Ap, a + 1);
                    CTL(4);                                                  /* the test of the remainder and the quotient length */
                    if (lr != 0 || lq != b + 1) { fprintf(stderr, "split: division left a remainder\n"); exit(80); }
                    xfree(rem); xfree(Ap); xfree(G); G = q; d = b;
                    SPL_div += snap_total(snap_sub(snap(), t0));
                }
                proper = 1;
            } else xfree(Ap);
        }
        if (!proper) { xfree(G); return 0; }
    }
    fp r;
    CTL(3);
    if (d == 2) {
        fp b2, disc, four, s, two, itwo, nb;
        fp_sqr(&b2, &G[1]); fp_add(&four, &G[0], &G[0]); fp_add(&four, &four, &four); fp_sub(&disc, &b2, &four);
        LD(2);
        CTL(2);
        if (!fp_sqrt(&s, &disc)) { xfree(G); return 0; }
        CTL(12000);
        fp one; fp_set_one(&one); fp_add(&two, &one, &one); fp_inv(&itwo, &two); CTL(INV_CTL);
        fp_sub(&nb, &s, &G[1]); fp_mul(&r, &nb, &itwo);
    } else {
        fp_neg(&r, &G[0]); LD(1);
    }
    fp_sub(root, &r, &shift);
    xfree(G);
    return 1;
}

/* ---------- Root isolation of the algebraic-paper program (proof 4.1.2).
 * G: monic, product of d distinct linear factors, 1 <= d <= DMAX (d+1 coefficients, consumed).  While d >= 2, at most ZCAP rounds: draw a (coin draw, rnd_fp320), move to the
 * roots r + a (Taylor shift by -a), S = Z^((p-1)/2) mod G, G+ = gcd(G, S - 1), G- = gcd(G, S + 1); G = G+ G- Z^e0 (e0 = 1 iff the root 0 is present); keep the part of smaller
 * nonzero degree (ties: G+); if both are constant the only root is 0 (G = Z).  Returns 0 if deg G >= 2 remains after ZCAP rounds.  The accumulated shift is subtracted at the end. */
int split_find_root_capped(fp *root, fp *G, size_t d) {
    fp shift, one; fp_set_zero(&shift); fp_set_one(&one);
    size_t rd = 0; CTL(3);
    while (d >= 2) {
        CTL(3 + 3);                                                  /* loop test d >= 2, the round counter: increment, comparison with ZCAP, branch */
        if (rd >= ZCAP) { xfree(G); return 0; }
        rd++; SPL_tries++;
        fp a, ma; rnd_fp320(&a); fp_neg(&ma, &a);
        G = taylor_shift(G, d, &ma);                                 /* G(Z - a): roots r + a */
        fp_add(&shift, &shift, &a);
        fp *S = NEW_FP(d), *Sm = NEW_FP(d);
        pow_half(S, G, d);
        memcpy(Sm, S, d * sizeof(fp)); LD(d); ST(d); loopc(d);
        fp_sub(&S[0], &S[0], &one); fp_add(&Sm[0], &Sm[0], &one); LD(2); ST(2);
        fp *Gp = NEW_FP(d + 1), *Gm = NEW_FP(d + 1);
        size_t dp = gcd_cl(Gp, G, d, S, d - 1);
        size_t dm = gcd_cl(Gm, G, d, Sm, d - 1);
        xfree(S); xfree(Sm);
        CTL(3 + 3 + 2);                                              /* the tests dp >= 1, dm >= 1, dp <= dm */
        if (dp >= 1 && (dm < 1 || dp <= dm)) { xfree(G); xfree(Gm); G = Gp; d = dp; }
        else if (dm >= 1) { xfree(G); xfree(Gp); G = Gm; d = dm; }
        else { xfree(G); xfree(Gp); xfree(Gm); G = NEW_FP(2); fp_set_zero(&G[0]); fp_set_one(&G[1]); ST(2); d = 1; }
    }
    fp r; CTL(3);
    fp_neg(&r, &G[0]); LD(1);
    fp_sub(root, &r, &shift);
    xfree(G);
    return 1;
}
