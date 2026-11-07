/* Classical Euclid gcd (counted; loads/stores charged inside) and root finding for a product of distinct linear factors. */
#include "attack.h"
#include "pallas_consts.h"

static int deg_of(const fp *a, int top) { while (top >= 0 && fp_is_zero(&a[top])) top--; return top; }

/* returns degree of the monic gcd in out[0..deg]; inputs are not modified.  da, db are upper bounds on the degrees. */
size_t euclid_gcd(fp *out, const fp *a, size_t da, const fp *b, size_t db, size_t *dout) {
    size_t cap = (da > db ? da : db) + 1;
    fp *A = NEW_FP(cap), *B = NEW_FP(cap);
    memcpy(A, a, (da + 1) * sizeof(fp)); memcpy(B, b, (db + 1) * sizeof(fp));
    LD(da + db + 2); ST(da + db + 2); loopc(da + db + 2);
    int dA = deg_of(A, (int)da), dB = deg_of(B, (int)db);
    CTL(dA + dB + 2);
    if (dA < dB) { fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td; }
    while (dB >= 0) {
        fp ilc; fp_inv(&ilc, &B[dB]); LD(1);
        while (dA >= dB) {
            fp q; fp_mul(&q, &A[dA], &ilc); LD(1);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            LD(2 * (size_t)dB); ST(dB); loopc(dB);
            fp_set_zero(&A[dA]); ST(1);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            CTL(dA - nd + 1); LD(dA - nd);
            dA = nd;
            if (dA < 0) break;
        }
        fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td;
    }
    /* A is the last nonzero remainder, degree dA (after swap dB<0) */
    int dg = dA;
    if (dg < 0) { fprintf(stderr, "gcd of zero polynomials\n"); exit(8); }
    fp il; fp_inv(&il, &A[dg]);
    for (int i = 0; i <= dg; i++) fp_mul(&out[i], &A[i], &il);
    LD(dg + 1); ST(dg + 1); loopc(dg + 1);
    *dout = (size_t)dg;
    xfree(A); xfree(B);   /* note: A and B may have been swapped; both are valid allocations */
    return (size_t)dg;
}

/* ---- small-degree helpers for root finding (naive) ---- */
/* r = a mod G (G monic degree d, a has length la), result d coefficients */
static void reduce_mod(fp *a, size_t la, const fp *G, size_t d) {
    for (size_t i = la; i-- > d;) {
        fp c = a[i];
        if (fp_is_zero(&c)) continue;
        for (size_t j = 0; j < d; j++) { fp t; fp_mul(&t, &c, &G[j]); fp_sub(&a[i - d + j], &a[i - d + j], &t); }
        fp_set_zero(&a[i]);
    }
}
static void sqr_mod(fp *r, const fp *a, const fp *G, size_t d) {
    fp *t = NEW_FP(2 * d);
    for (size_t i = 0; i < 2 * d; i++) fp_set_zero(&t[i]);
    for (size_t i = 0; i < d; i++) {
        fp x; fp_sqr(&x, &a[i]); fp_add(&t[2 * i], &t[2 * i], &x);
        for (size_t j = i + 1; j < d; j++) { fp y; fp_mul(&y, &a[i], &a[j]); fp_add(&y, &y, &y); fp_add(&t[i + j], &t[i + j], &y); }
    }
    reduce_mod(t, 2 * d - 1, G, d);
    for (size_t i = 0; i < d; i++) r[i] = t[i];
    xfree(t);
}
static void mul_xa_mod(fp *r, const fp *a, const fp *av, const fp *G, size_t d) {   /* r = a * (x + av) mod G */
    fp *t = NEW_FP(d + 1);
    fp_set_zero(&t[0]);
    for (size_t i = 0; i < d; i++) t[i + 1] = a[i];
    for (size_t i = 0; i < d; i++) { fp x; fp_mul(&x, &a[i], av); fp_add(&t[i], &t[i], &x); }
    reduce_mod(t, d + 1, G, d);
    for (size_t i = 0; i < d; i++) r[i] = t[i];
    xfree(t);
}

int find_root(fp *root, const fp *G0, size_t d0) {
    snap_t s0 = snap();
    int ok = 0;
    size_t d = d0;
    fp *G = NEW_FP(d0 + 1); memcpy(G, G0, (d0 + 1) * sizeof(fp));
    for (int tries = 0; tries < 64 && d > 1; tries++) {
        fp av; rnd_fp254(&av);
        fp *B = NEW_FP(d);
        for (size_t i = 0; i < d; i++) fp_set_zero(&B[i]);
        /* start from x + a  (d >= 2 so it is already reduced) */
        B[0] = av; fp_set_one(&B[1]);
        int top = 253; while (top >= 0 && !((PALLAS_PM1H[top / 64] >> (top % 64)) & 1)) top--;
        for (int bit = top - 1; bit >= 0; bit--) {
            sqr_mod(B, B, G, d);
            if ((PALLAS_PM1H[bit / 64] >> (bit % 64)) & 1) mul_xa_mod(B, B, &av, G, d);
        }
        fp one; fp_set_one(&one);
        fp_sub(&B[0], &B[0], &one);
        fp *out = NEW_FP(d + 1); size_t dg;
        if (d >= 1) {
            /* gcd(G, B) where B has degree < d (may be zero) */
            int allz = 1; for (size_t i = 0; i < d; i++) if (!fp_is_zero(&B[i])) allz = 0;
            if (allz) { xfree(out); xfree(B); continue; }
            euclid_gcd(out, G, d, B, d - 1, &dg);
        }
        if (dg > 0 && dg < d) {
            memcpy(G, out, (dg + 1) * sizeof(fp)); d = dg;
        }
        xfree(out); xfree(B);
    }
    if (d == 1) { fp_neg(root, &G[0]); ok = 1; }
    xfree(G);
    bound_mem_since(s0);
    return ok;
}
