/* Stage tools of the two-family attack: classical Euclid gcd with a derived worst-case charge, deflation by a known root,
 * Taylor shift, Z^((p-1)/2) mod G, and the isolation of one root of a monic product of distinct linear factors.
 * Every executed operation is charged as in common.h. */
#include "attack.h"
#include "pallas_consts.h"

uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;

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

/* Derived worst-case charge of gcd_cl(da, db).  Let S0 = da + db.  Each elimination step lowers dA + dB by at least 1 and its inner loop
 * runs dB <= (dA + dB)/2 times, so the inner iterations total at most floor(S0^2/4); eliminations E <= S0 + 1; passes <= E; the
 * degree scans lower dA by S0 + 1 in total.  Constants: inner iteration 2 arith + 2 ld + 1 st + 7 ctl = 12; elimination 25 + 11 (dA - nd);
 * pass: one inversion (330) + 1 ld + 1 address + INV_CTL + 8 ctl.  INVA is the arithmetic of fp_inv (254 squarings + 76 multiplications for the exponent p - 2). */
#define INVA 330
uint64_t gcd_cost_bound(size_t da, size_t db) {
    uint64_t S0 = da + db, cap = (da > db ? da : db) + 1;
    uint64_t inner = (S0 * S0) / 4, E = S0 + 1;
    uint64_t setup = 5 * (S0 + 2) + 2 + 2 * (S0 + 2) + 9 * (S0 + 2) + 4;
    uint64_t elim = 25 * E + 11 * (S0 + 1);
    uint64_t pass = E * (INVA + 2 + INV_CTL + 8);
    uint64_t fin = INVA + 2 + INV_CTL + 8 * cap + 4;
    return 12 * inner + elim + pass + setup + fin;
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

/* Derived worst-case charge of divrem(la, lb): per quotient coefficient 14 + 12 (lb - 1) operations (1 + 2(lb-1) arithmetic, 1 + 2(lb-1) loads,
 * 1 + (lb-1) stores, 11 + 7(lb-1) control), plus the copy of the dividend (7 la + 2), one inversion, and the trimming of the remainder (11 per test). */
uint64_t div_cost_bound(size_t la, size_t lb) {
    return (uint64_t)(la - lb + 1) * (14 + 12 * (uint64_t)(lb - 1)) + 7 * (uint64_t)la + 2 + INVA + 2 + INV_CTL + 11 * ((uint64_t)lb + 1);
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
size_t split_tries(size_t d) { return d > 40 ? 1 : (40 + d - 2) / (d - 1); }

/* Root isolation.  G: monic, d >= 1, product of d distinct linear factors over F_p, d+1 coefficients (consumed).
 * Level: shift by a random c (G(Z - c), roots r + c), S = Z^((p-1)/2) mod G, A = gcd(G, S - 1) = the roots whose shifted value is a
 * nonzero square; the split is proper if 1 <= deg A <= d - 1; continue with the piece of smaller degree (A, or G / A).
 * Returns 0 if a level has no proper split after split_tries(d) tries. */
int split_find_root(fp *root, fp *G, size_t d) {
    fp shift; fp_set_zero(&shift);
    snap_t t0;
    while (d >= 3) {
        size_t t = split_tries(d); int proper = 0;
        CTL(3 + 3 + 6);                                              /* loop test, call of split_tries (two compares, branch, subtract, add, divide) */
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
            fp *Ap = NEW_FP(d + 1);
            snap_t tg = snap();
            size_t a = gcd_cl(Ap, G, d, S, d - 1);
            uint64_t gch = snap_total(snap_sub(snap(), tg));
            xfree(S);
            SPL_gcd += snap_total(snap_sub(snap(), t0));
            if (gch > gcd_cost_bound(d, d - 1)) { fprintf(stderr, "gcd charge above its bound\n"); exit(81); }
            CTL(4);
            if (a >= 1 && a <= d - 1) {
                size_t b = d - a;
                CTL(3);
                if (a <= b) { xfree(G); G = Ap; d = a; }
                else {
                    t0 = snap();
                    size_t dold = d; fp *q = NEW_FP(b + 1), *rem = NEW_FP(d + 1); size_t lq, lr;
                    divrem(q, &lq, rem, &lr, G, d + 1, Ap, a + 1);
                    CTL(4);                                                  /* the test of the remainder and the quotient length */
                    if (lr != 0 || lq != b + 1) { fprintf(stderr, "split: division left a remainder\n"); exit(80); }
                    xfree(rem); xfree(Ap); xfree(G); G = q; d = b;
                    SPL_div += snap_total(snap_sub(snap(), t0));
                    if (snap_total(snap_sub(snap(), t0)) > div_cost_bound(dold + 1, a + 1)) { fprintf(stderr, "division charge %llu above its bound %llu (la=%zu lb=%zu)\n", (unsigned long long)snap_total(snap_sub(snap(), t0)), (unsigned long long)div_cost_bound(dold + 1, a + 1), dold + 1, a + 1); exit(82); }
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
