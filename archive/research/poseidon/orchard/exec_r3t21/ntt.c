/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 data words in registers, plus 2 working words) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"

static fp *tw = NULL;          /* half table: tw[m] = rho_max^(2m), m < nmax/4 (the odd powers are recomputed: rho_max^(2m+1) = tw[m] * RHO) */
static fp RHO;                  /* rho_max (one stored word) */
static int amax_g = 0;
static size_t nmax_g = 0;
fp ntt_w3;                      /* primitive cube root of unity */
static fp W3[3];                /* 1, w, w^2 */
static fp ZERO;                 /* 0 */
static fp CH, DL;               /* -1/2, (w - w^2)/2 */
static fp GW2, GW2I;            /* primitive 2^(amax+1)-th root of unity and its inverse (rows==2 plans) */

static void limbs_sub1(uint64_t r[4], const uint64_t a[4]) {      /* r = a - 1 */
    for (int i = 0; i < 4; i++) r[i] = a[i];
    for (int i = 0; i < 4; i++) { if (r[i]) { r[i]--; break; } r[i] = ~(uint64_t)0; }
}
static void limbs_shr(uint64_t r[4], const uint64_t a[4], int s) {
    int ws = s / 64, bs = s % 64;
    for (int i = 0; i < 4; i++) {
        uint64_t v = 0;
        if (i + ws < 4) v = a[i + ws] >> bs;
        if (bs && i + ws + 1 < 4) v |= a[i + ws + 1] << (64 - bs);
        r[i] = v;
    }
}
/* r = a / 3 for a multiple of 3, by long division over the 256 bits (no division instruction): rem = 2 rem + bit; if rem >= 3 then rem -= 3 and set the quotient bit */
static void limbs_div3(uint64_t r[4], const uint64_t a[4]) {
    uint64_t rem = 0, taken = 0;
    for (int i = 0; i < 4; i++) r[i] = 0;
    for (int i = 255; i >= 0; i--) {
        rem = (rem << 1) | ((a[i >> 6] >> (i & 63)) & 1);
        if (rem >= 3) { rem -= 3; r[i >> 6] |= (uint64_t)1 << (i & 63); taken++; }
    }
    CTL(4 * 4 + 2 + 12 * 256 + 2 + 7 * taken);         /* clearing loop; per bit: loop 3, i>>6, load, i&63, shift, and, rem<<1, or, compare + branch (2) = 12; per set bit: subtract, i>>6, i&63, shift, load, or, store = 7 */
}

void ntt_init(int amax) {
    if (tw) ntt_free();
    CTL(2);                                        /* the test of tw */
    amax_g = amax; nmax_g = (size_t)1 << amax;
    uint64_t pm1[4], e[4], e2[4]; limbs_sub1(pm1, PALLAS_P);
    fp five; fp_from_u64(&five, 5);
    /* rho_max = 5^((p-1)/2^amax) (5 is a non-residue so this has exact order 2^amax) */
    limbs_shr(e, pm1, amax);
    fp rho; fp_pow(&rho, &five, e);
    limbs_shr(e2, pm1, amax + 1);                  /* rows==2 twist root: 5^((p-1)/2^(amax+1)), exact order 2^(amax+1) */
    fp_pow(&GW2, &five, e2); fp_inv(&GW2I, &GW2); CTL(INV_CTL + 100);
    /* w = 5^((p-1)/3) */
    limbs_div3(e, pm1); fp_pow(&ntt_w3, &five, e);
    CTL(400);               /* limbs_sub1, limbs_shr: at most 4 iterations of at most 20 operations each per call, two calls (limbs_div3 charges itself) */
    CTL(2 + 8);             /* the test ntt_w3 == 1 (four limb comparisons: 8 operations; compare, branch) */
    fp one; fp_set_one(&one);
    if (fp_eq(&ntt_w3, &one)) { fprintf(stderr, "5 is a cube?\n"); exit(3); }
    fp_set_zero(&ZERO);
    tw = NEW_FP(nmax_g / 4);
    RHO = rho; ST(1);
    fp rho2; fp_sqr(&rho2, &rho);
    tw[0] = one; ST(1);
    for (size_t j = 1; j < nmax_g / 4; j++) { fp_mul(&tw[j], &tw[j - 1], &rho2); LD(1); ST(1); }
    loopc(nmax_g / 4);
    CTL(5 * INV_CTL);       /* control of the bit loops of fp_pow (x2) and fp_inv (x1): at most INV_CTL each; the other setup is a few dozen straight-line operations */
    W3[0] = one; W3[1] = ntt_w3; fp_sqr(&W3[2], &ntt_w3);
    fp two, half; fp_from_u64(&two, 2); fp_inv(&half, &two);
    fp s; fp_add(&s, &W3[1], &W3[2]); fp_mul(&CH, &s, &half);          /* (w+w^2)/2 = -1/2 */
    fp d; fp_sub(&d, &W3[1], &W3[2]); fp_mul(&DL, &d, &half);
}
void ntt_free(void) { if (tw) xfree(tw); tw = NULL; }
size_t ntt_table_bytes(void) { return (nmax_g / 4) * sizeof(fp) + sizeof(fp); }

plan_t make_plan(int rows, int a) {
    plan_t P; memset(&P, 0, sizeof P);
    if (a < 2 || a > amax_g || (rows != 1 && rows != 2 && rows != 3)) { fprintf(stderr, "bad plan rows=%d a=%d (amax=%d)\n", rows, a, amax_g); exit(4); }
    P.rows = rows; P.a = a; P.n = (size_t)1 << a; P.N = P.n * rows; P.shift = amax_g - a;
    CTL(16);                                       /* validity tests (4 compares, 4 branches) and the assignments above (shift, multiply, subtraction) */
    int np = (a + 3) / 4; P.npass = np;
    int rem = a;
    CTL(3);
    /* last pass gets 4 layers; earlier passes take the rest, first pass smallest */
    for (int i = np - 1; i >= 0; i--) { int k = rem >= 4 ? 4 : rem; P.kk[i] = k; rem -= k; }
    loopc(np); CTL(4 * np);                        /* per pass: compare, select, subtract, store index */
    CTL(2);                                        /* test of rows */
    if (rows == 2) {                               /* N-th root of the twist: GW2 squared (amax - a) times, and the same for the inverse */
        P.w2 = GW2; P.w2i = GW2I;
        for (int s = 0; s < P.shift; s++) { fp_sqr(&P.w2, &P.w2); fp_sqr(&P.w2i, &P.w2i); CTL(3); }
        CTL(4);
    }
    CTL(2);
    if (rows == 3) {
        size_t n = P.n, beta = 0, it = 0;
        for (size_t b = 1; b < n; b += 2) { it++; if ((3 * b) % n == 1) { beta = b; break; } }
        loopc(it); CTL(4 * it);                    /* per iteration: multiply, modulo, compare, branch */
        P.c0 = (int)((3 * beta - 1) / n);
        CTL(4);
    }
    return P;
}
plan_t plan_for_len(size_t len, int allow3) {
    for (int a = 2; a <= amax_g; a++) {
        CTL(3 + 1 + 2 + (allow3 ? 3 : 0));         /* loop (3), shift, compare + branch, [multiply, compare, branch] */
        if (((size_t)1 << a) >= len) return make_plan(1, a);
        if (allow3 && 3 * ((size_t)1 << a) >= len) return make_plan(3, a);
    }
    fprintf(stderr, "length %zu too large for amax=%d\n", len, amax_g); exit(5);
}
static size_t brv(size_t x, int a) {
    size_t r = 0;
    for (int i = 0; i < a; i++) { r = (r << 1) | (x & 1); x >>= 1; }
    CTL(4 * (uint64_t)a);                          /* per iteration: shift, mask, or, shift */
    loopc(a);
    return r;
}
size_t layout_index(const plan_t *P, size_t k) {
    CTL(8);                                        /* call, rows test (compare, branch), k % 3, k % n, row * n, addition */
    size_t row = P->rows == 3 ? k % 3 : 0;
    return row * P->n + brv(k % P->n, P->a);
}
void plan_theta(const plan_t *P, fp *theta) {
    fp rho; CTL(3);                              /* test of shift, index shift */
    if (P->shift == 0) { rho = RHO; } else { rho = tw[(size_t)1 << (P->shift - 1)]; }
    LD(1);
    CTL(2);                                        /* test of rows */
    if (P->rows == 1) { *theta = rho; return; }
    int e = (3 - P->c0 % 3) % 3;              /* omega3^(-c0) */
    CTL(10);
    fp_mul(theta, &rho, &W3[e]);
}

/* ---------- butterflies: straight-line register blocks and passes (ntt_kern.h, generated by gen_kern.py) ----------
 * Charging convention of this file and of the generated headers: every statement that executes loads, stores, integer, address or
 * branch operations carries its charge on the same line (LD / ST: one 256-bit memory access with its address formation; CTL(n): n integer
 * operations, comparisons or branches, 1 each); field operations are charged by pallas.c.  The block kernels contain no loop and no
 * branch.  Register assumption (disclosed): a block holds 2^k <= 16 data words in registers; the twiddle operand and the butterfly
 * temporary need 2 more words; strides, shift counts and base pointers live in integer registers. */
#include "ntt_kern.h"

/* per-pass constants: sj[j] = l0 + j, sjs[j] = sj[j] + shift, D[j] = s << sjs[j] (twiddle pointer step between consecutive tp of layer j).
 * Executed: a loop over the k layers with three additions, a shift and a store per layer (6 with the loop step 3 + 3). */
static void pass_tables(int k, int l0, size_t s, int shift, size_t *D, int *sj, int *sjs) {
    for (int j = 0; j < k; j++) { sj[j] = l0 + j; sjs[j] = l0 + j + shift; D[j] = s << sjs[j]; CTL(3 + 3 + 3); }
    CTL(2);
}
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), ngrp = (size_t)1 << l0;
    CTL(5);                                              /* s, ngrp: two shifts, an add; call, return */
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    CTL(4);                                              /* switch on k: compare, jump table */
    switch (k) { case 1: pf1(row, s, ngrp, tw, D, sjs); break; case 2: pf2(row, s, ngrp, tw, D, sjs); break;
                 case 3: pf3(row, s, ngrp, tw, D, sjs); break; default: pf4(row, s, ngrp, tw, D, sjs); break; }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), ngrp = (size_t)1 << l0, nh = P->n >> 1;
    CTL(6);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    CTL(4);
    switch (k) { case 1: pi1(row, s, ngrp, tw, D, sj, P->shift, nh); break; case 2: pi2(row, s, ngrp, tw, D, sj, P->shift, nh); break;
                 case 3: pi3(row, s, ngrp, tw, D, sj, P->shift, nh); break; default: pi4(row, s, ngrp, tw, D, sj, P->shift, nh); break; }
}
enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };
/* last forward pass + pointwise + first inverse pass (s == 1) in one register-resident block */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t ngrp = P->n >> k, nh = P->n >> 1;
    CTL(6);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, 1, P->shift, D, sj, sjs);
    CTL(6);                                              /* switch on mode and on k */
    if (mode == M_SQ) {
        switch (k) { case 1: pu1_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break; case 2: pu2_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break;
                     case 3: pu3_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break; default: pu4_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break; }
    } else {
        switch (k) { case 1: pu1_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break; case 2: pu2_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break;
                     case 3: pu3_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break; default: pu4_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break; }
    }
}

/* ---------- radix-3 stage ----------
 * Position kernels (ntt_a3.h) are straight-line code for one (pattern of nonzero inputs, rotation); a region driver runs one kernel
 * variant per position phase over a range of positions (head until the phase is 0, a loop of three positions per iteration, tail).
 * The ranges of constant pattern are found by split_regions below, whose operations are all charged where they are executed. */
typedef void (*rg_t)(fp *, const fp *, ptrdiff_t, ptrdiff_t, ptrdiff_t, size_t, size_t, size_t);
/* the kernel call macros are generated per (pat, rot, phase offset) by the helpers below */
#define KF(pat, rot, off) a3f_##pat##_##rot(dst, S, d0, d1, d2, n, i + (off))
#define KI(pat, rot, off) a3i_##pat##_##rot(dst, n, i + (off))
#define KR(r, pat, rot, off) a3r_##pat##_##rot##_##r(dst, S, d0, d1, d2, i + (off))
#define DRV_F(pat, c0, r0, r1, r2)                                                                                \
    static void rgf_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)d0; (void)d1; (void)d2;                                                                             \
        _DRV(KF(pat, r0, o), KF(pat, r1, o), KF(pat, r2, o)) }
#define DRV_I(pat, c0, r0, r1, r2)                                                                                \
    static void rgi_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)S; (void)d0; (void)d1; (void)d2;                                                                    \
        _DRV(KI(pat, r0, o), KI(pat, r1, o), KI(pat, r2, o)) }
#define DRV_R(r, pat, c0, r0, r1, r2)                                                                             \
    static void rgr##r##_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)n;                                                                                                  \
        _DRV(KR(r, pat, r0, o), KR(r, pat, r1, o), KR(r, pat, r2, o)) }
/* _DRV(K0, K1, K2): K_ph is the kernel call for phase ph with the placeholder offset o */
#define _DRV(K0, K1, K2)                                                                                          \
    size_t i = lo, ph = lo % 3; CTL(3);                                                                           \
    CTL(2); if (ph == 1) {                                                                                        \
        CTL(2); if (i < hi) { _SUB(K1, 0); i++; CTL(1);                                                           \
            CTL(2); if (i < hi) { _SUB(K2, 0); i++; CTL(1); } }                                                   \
    } else { CTL(2); if (ph == 2) { CTL(2); if (i < hi) { _SUB(K2, 0); i++; CTL(1); } } }                         \
    size_t nt = 0; CTL(2); if (hi > i) { nt = (hi - i) / 3; CTL(3); }                                             \
    for (size_t q = 0; q < nt; q++) { _SUB(K0, 0); _SUB(K1, 1); _SUB(K2, 2); i += 3; CTL(1 + 3); }               \
    CTL(2);                                                                                                       \
    CTL(2); if (hi > i) { size_t rem = hi - i; CTL(1);                                                            \
        _SUB(K0, 0); i++; CTL(1);                                                                                 \
        CTL(2); if (rem == 2) { _SUB(K1, 0); } }
#define _SUB(K, off) do { const size_t o = (off); K; } while (0)
#include "ntt_a3.h"

/* Regions of constant pattern.  Position pos = i0 + n*t (t = 0, 1, 2) of the length-N cyclic vector holds B[(pos + N - boff) mod N] when
 * that index is < lenB (lenB <= N), else 0.  bp[] receives the sorted breakpoints (bp[0] = 0, last = n), pat[] the pattern of each range
 * (bit t set: position t of the triple is nonzero).  Returns the number of ranges.  Every executed operation is charged. */
static int split_regions(size_t n, size_t N, size_t boff, size_t lenB, size_t *bp, int *pat, int nrow) {
    if (lenB > N) { fprintf(stderr, "split_regions: lenB %zu > N %zu\n", lenB, N); exit(10); }
    int cnt = 0;
    bp[cnt++] = 0; CTL(3);
    for (int t = 0; t < nrow; t++) {
        size_t st = (n * (size_t)t + N - boff) % N; CTL(3 + 4);                   /* loop, multiply, add, subtract, modulo */
        size_t x;
        CTL(3); if (st < lenB) { x = lenB - st; CTL(1); CTL(3); if (x > 0 && x < n) { bp[cnt++] = x; CTL(1); } }
        CTL(3); if (st > 0) { x = N - st; CTL(1); CTL(3); if (x > 0 && x < n) { bp[cnt++] = x; CTL(1); }
                              x = N + lenB - st; CTL(2); CTL(3); if (x > 0 && x < n) { bp[cnt++] = x; CTL(1); } }
    }
    CTL(2);
    bp[cnt++] = n; CTL(1);
    for (int a = 1; a < cnt; a++) {                                              /* insertion sort */
        size_t key = bp[a]; int b = a - 1; CTL(3 + 2);
        while (b >= 0 && bp[b] > key) { bp[b + 1] = bp[b]; b--; CTL(3 + 3); }
        CTL(3);
        bp[b + 1] = key;
    }
    CTL(2);
    int m = 0;                                                                   /* drop empty ranges */
    for (int a = 0; a + 1 < cnt; a++) {
        CTL(3 + 3);
        if (bp[a + 1] > bp[a]) {
            size_t lo = bp[a]; int p = 0;
            for (int t = 0; t < nrow; t++) { size_t idx = (lo + n * (size_t)t + N - boff) % N; p |= (idx < lenB) << t; CTL(3 + 5 + 3); }
            CTL(2 + 3);
            bp[m] = lo; pat[m] = p; m++; CTL(2);
        }
    }
    CTL(2);
    bp[m] = n; CTL(1);
    return m;
}
/* ---------- radix-2 twisted stage (rows == 2, N = 2n, n = 2^a) ----------
 * Position pos = i + n*t (t = 0, 1) of the cyclic vector c of length N = 2n.  Row 0 = c mod (x^n - 1) = c[i] + c[i+n]; row 1 = c mod (x^n + 1) mapped
 * to x^n - 1 by x -> w x (w^n = -1, w = P->w2): (c[i] - c[i+n]) w^i.  Both rows are then ordinary 2^a rows.  Inverse: c[i] N = r0[i] + r1[i] w^-i,
 * c[i+n] N = r0[i] - r1[i] w^-i (the rows carry the factor n of their own inverse).  The power w^i is a running product started at w^lo by
 * square-and-multiply for every region of constant pattern; every executed operation is charged here or in the field primitives. */
static void w2pow(fp *out, const fp *w, size_t e) {
    fp r; fp_set_one(&r); fp b = *w; size_t it = 1;
    while (e) { if (e & 1) fp_mul(&r, &r, &b); e >>= 1; if (e) fp_sqr(&b, &b); it++; }
    CTL(6 * it + 4); *out = r;
}
/* forward stage over positions lo <= i < hi: o0 / o1 (either may be NULL) receive row 0 / row 1; S0[i] = c[i], S1[i] = c[i+n]; pat bit 0 / bit 1: that input is nonzero */
static void a2_range(fp *o0, fp *o1, const fp *S0, const fp *S1, const fp *w, size_t lo, size_t hi, int pat) {
    size_t cnt = hi - lo; CTL(8);
    fp pw;
    if (pat == 0) {
        fp z; fp_set_zero(&z);
        if (o0) { FOR8(ix, cnt, o0[lo + ix] = z; ST(1)); }
        if (o1) { FOR8(ix, cnt, o1[lo + ix] = z; ST(1)); }
        return;
    }
    if (o1) w2pow(&pw, w, lo);
#define A2M(BOTH, ONLY0, ONLY1) \
    if (o0 && o1) { FOR8(ix, cnt, size_t k = lo + ix; BOTH); } else if (o0) { FOR8(ix, cnt, size_t k = lo + ix; ONLY0); } else { FOR8(ix, cnt, size_t k = lo + ix; ONLY1); }
    if (pat == 3) {
        A2M(fp u = S0[k]; fp v = S1[k]; fp s; fp t; LD(2); fp_add(&s, &u, &v); fp_sub(&t, &u, &v); fp_mul(&t, &t, &pw); fp_mul(&pw, &pw, w); o0[k] = s; o1[k] = t; ST(2),
            fp u = S0[k]; fp v = S1[k]; fp s; LD(2); fp_add(&s, &u, &v); o0[k] = s; ST(1),
            fp u = S0[k]; fp v = S1[k]; fp t; LD(2); fp_sub(&t, &u, &v); fp_mul(&t, &t, &pw); fp_mul(&pw, &pw, w); o1[k] = t; ST(1));
    } else if (pat == 1) {
        A2M(fp u = S0[k]; fp t; LD(1); fp_mul(&t, &u, &pw); fp_mul(&pw, &pw, w); o0[k] = u; o1[k] = t; ST(2),
            fp u = S0[k]; LD(1); o0[k] = u; ST(1),
            fp u = S0[k]; fp t; LD(1); fp_mul(&t, &u, &pw); fp_mul(&pw, &pw, w); o1[k] = t; ST(1));
    } else {
        A2M(fp v = S1[k]; fp t; LD(1); fp_neg(&t, &v); fp_mul(&t, &t, &pw); fp_mul(&pw, &pw, w); o0[k] = v; o1[k] = t; ST(2),
            fp v = S1[k]; LD(1); o0[k] = v; ST(1),
            fp v = S1[k]; fp t; LD(1); fp_neg(&t, &v); fp_mul(&t, &t, &pw); fp_mul(&pw, &pw, w); o1[k] = t; ST(1));
    }
#undef A2M
}
/* inverse stage over lo <= i < hi: pat bit 0: produce c[i] N, bit 1: produce c[i+n] N (in place in buf, row 0 = buf, row 1 = buf + n) */
static void a2_inv_range(fp *buf, size_t n, const fp *wi, size_t lo, size_t hi, int pat) {
    size_t cnt = hi - lo; CTL(8);
    fp pw; w2pow(&pw, wi, lo);
    if (pat == 3) { FOR8(ix, cnt, size_t k = lo + ix; fp a = buf[k]; fp b = buf[k + n]; fp t; LD(2); fp_mul(&t, &b, &pw); fp_mul(&pw, &pw, wi); fp_add(&buf[k], &a, &t); fp_sub(&buf[k + n], &a, &t); ST(2)); }
    else if (pat == 1) { FOR8(ix, cnt, size_t k = lo + ix; fp a = buf[k]; fp b = buf[k + n]; fp t; LD(2); fp_mul(&t, &b, &pw); fp_mul(&pw, &pw, wi); fp_add(&buf[k], &a, &t); ST(1)); }
    else { FOR8(ix, cnt, size_t k = lo + ix; fp a = buf[k]; fp b = buf[k + n]; fp t; LD(2); fp_mul(&t, &b, &pw); fp_mul(&pw, &pw, wi); fp_sub(&buf[k + n], &a, &t); ST(1)); }
}

static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(4);                                                                       /* test of rows, dispatch */
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        CTL(4);                                                                   /* test dst == src && off == 0 */
        if (dst == src && off == 0) { if (n > len) { FOR8(i, n - len, dst[len + i] = z; ST(1)); } return; }
        { size_t c = len < n ? len : n; FOR8(i, c, dst[i] = src[off + i]; LD(1); ST(1)); if (n > c) { FOR8(i, n - c, dst[c + i] = z; ST(1)); } }
        return;
    }
    if (P->rows == 2) {
        size_t bp2[12]; int pat2[12];
        int nr2 = split_regions(n, P->N, 0, len, bp2, pat2, 2);
        for (int q = 0; q < nr2; q++) { CTL(4); a2_range(dst, dst + n, src + off, src + off + n, &P->w2, bp2[q], bp2[q + 1], pat2[q]); CTL(3); }
        CTL(2);
        return;
    }
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, P->N, 0, len, bp, pat, P->rows);
    int c0 = P->c0 % 3; CTL(2);
    for (int q = 0; q < nr; q++) {
        CTL(4);                                                                   /* table lookup of the driver, indirect call */
        RGF[c0][pat[q]](dst, src + off, (ptrdiff_t)0, (ptrdiff_t)n, (ptrdiff_t)(2 * n), n, bp[q], bp[q + 1]);
        CTL(3);
    }
    CTL(2);
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n;
    CTL(2);
    if (P->rows == 2) {
        size_t bp2[12]; int pat2[12];
        int nr2 = split_regions(n, P->N, 0, outlen, bp2, pat2, 2);
        for (int q = 0; q < nr2; q++) {
            CTL(2); if (pat2[q] == 0) { CTL(3); continue; }
            CTL(4); a2_inv_range(buf, n, &P->w2i, bp2[q], bp2[q + 1], pat2[q]); CTL(3);
        }
        CTL(2);
        return;
    }
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, P->N, 0, outlen, bp, pat, P->rows);
    int c0 = P->c0 % 3; CTL(2);
    for (int q = 0; q < nr; q++) {
        CTL(2); if (pat[q] == 0) { CTL(3); continue; }
        CTL(4);
        RGI[c0][pat[q]](buf, NULL, 0, 0, 0, n, bp[q], bp[q + 1]);
        CTL(3);
    }
    CTL(2);
}

/* Row r of the Good-Thomas stage for the compact vector B (see split_regions for the layout of B at the cyclic offset boff) */
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N;
    if (P->rows == 2) {
        size_t bp2[12]; int pat2[12];
        int nr2 = split_regions(n, N, boff, lenB, bp2, pat2, 2);
        for (int q = 0; q < nr2; q++) {
            size_t lo = bp2[q]; ptrdiff_t d[2];
            for (int t = 0; t < 2; t++) { size_t idx = (lo + n * (size_t)t + N - boff) % N; d[t] = (ptrdiff_t)idx - (ptrdiff_t)lo; CTL(3 + 6); }
            CTL(4); a2_range(r == 0 ? tmp : NULL, r == 1 ? tmp : NULL, B + d[0], B + d[1], &P->w2, lo, bp2[q + 1], pat2[q]); CTL(3);
        }
        CTL(2);
        return;
    }
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, N, boff, lenB, bp, pat, P->rows);
    int c0 = P->c0 % 3; CTL(2);
    for (int q = 0; q < nr; q++) {
        size_t lo = bp[q];
        ptrdiff_t d[3];
        for (int t = 0; t < 3; t++) { size_t idx = (lo + n * (size_t)t + N - boff) % N; d[t] = (ptrdiff_t)idx - (ptrdiff_t)lo; CTL(3 + 6); }
        CTL(2);
        CTL(4);
        RGR[r][c0][pat[q]](tmp, B, d[0], d[1], d[2], n, lo, bp[q + 1]);
        CTL(3);
    }
    CTL(2);
}

void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    stageA_fwd(P, dst, src, off, len);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(3);
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(2);
    }
    CTL(2);
}
void ntt_inv(const plan_t *P, fp *buf, size_t outlen) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = P->a;
        CTL(3);
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(2);
    }
    CTL(2);
    stageA_inv(P, buf, outlen);
}
static void conv_core(const plan_t *P, fp *buf, int mode, const fp *C) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = 0;
        CTL(3 + 5);
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(4);                                    /* C ? ... : NULL: compare, branch, multiply, add */
        pass_fused(row, P, l0, P->kk[P->npass - 1], mode, C ? C + (size_t)r * P->n : NULL);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(4);
    }
    CTL(2);
}
void conv_sq(const plan_t *P, fp *buf, size_t len, size_t outlen) {
    stageA_fwd(P, buf, buf, 0, len);
    conv_core(P, buf, M_SQ, NULL);
    stageA_inv(P, buf, outlen);
}
void conv_mulc(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, const fp *C, size_t outlen) {
    stageA_fwd(P, dst, src, off, len);
    conv_core(P, dst, M_MULC, C);
    stageA_inv(P, dst, outlen);
}

/* ---------- lean variant: the spectrum of the second operand is generated one row at a time (rows==3 plans only) ----------
 * Row r of the Good-Thomas stage for the compact vector B: position pos (0 <= pos < N) holds B[(pos + N - boff) % N] if that
 * index is < lenB, else 0.  The row is then transformed with the forward passes, giving exactly row r of ntt_fwd(B). */
void conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                   const fp *B, size_t lenB, size_t boff, size_t outlen) {
    CTL(2);                                        /* validity test of rows */
    if (P->rows == 1) { fprintf(stderr, "conv_mulc_otf needs a rows>=2 plan\n"); exit(9); }
    stageA_fwd(P, dst, src, off, len);
    CTL(4);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(2 + 2 + 2 + 5);
        stageA_row(P, tmp, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmp, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(2);
        l0 = 0;
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        pass_fused(row, P, l0, P->kk[P->npass - 1], M_MULC, tmp);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(4);
    }
    CTL(2);
    stageA_inv(P, dst, outlen);
}

/* spectrum of the compact vector B (lenB coefficients, cyclic offset boff) of a rows==3 plan, generated row by row straight into dst (P->N slots) */
void ntt_fwd_shifted(const plan_t *P, fp *dst, const fp *B, size_t lenB, size_t boff) {
    CTL(4);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(2 + 2);
        stageA_row(P, row, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
    }
}
plan_t plan3_for_len(size_t len) {            /* smallest N >= len among 2^(a+1) (rows 2, n = 2^a) and 3 * 2^a (rows 3), ascending */
    for (int a = 2; a <= amax_g; a++) {
        CTL(3 + 1 + 1 + 2);                    /* loop, shift, compare, branch */
#ifndef NO_R2
        if (2 * ((size_t)1 << a) >= len) return make_plan(2, a);
#endif
        CTL(3 + 1 + 2);                        /* shift, multiply, compare, branch */
#ifndef NO_R3
        if (3 * ((size_t)1 << a) >= len) return make_plan(3, a);
#endif
    }
    fprintf(stderr, "plan3: length %zu too large\n", len); exit(5);
}

/* out (P->N slots) = sum_t sign[t] * (A_t * B_t mod x^N - 1) * N, all operands compact (folded modulo x^N-1 if longer than N);
 * the first term must have sign +1.  tmpA, tmpB: P->n slots each.  Only positions < outlen of out are produced. */
void conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                  const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen) {
    CTL(2);                                        /* validity test of rows */
    if (P->rows == 1) { fprintf(stderr, "conv_sum_otf needs a rows>=2 plan\n"); exit(9); }
    size_t n = P->n;
    CTL(2);
    for (int r = 0; r < P->rows; r++) {
        fp *row = out + (size_t)r * n; CTL(2 + 2);
        for (int t = 0; t < nt; t++) {
            int l0 = 0; CTL(3 + 6);                /* loop; the array selections A[t], lenA[t], B[t], lenB[t] and the argument setups */
            stageA_row(P, tmpA, r, A[t], lenA[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpA, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
            CTL(2);
            l0 = 0;
            stageA_row(P, tmpB, r, B[t], lenB[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpB, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
            CTL(2 + 4);                            /* loop exit; the tests t == 0 and sign[t] > 0 */
            if (t == 0) { FOR8(i, n, fp_mul(&row[i], &tmpA[i], &tmpB[i]); LD(2); ST(1)); }
            else if (sign[t] > 0) { FOR8(i, n, fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_add(&row[i], &row[i], &x); LD(3); ST(1)); }
            else { FOR8(i, n, fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_sub(&row[i], &row[i], &x); LD(3); ST(1)); }
        }
        CTL(2);
        int l0 = P->a;
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(2);
    }
    CTL(2);
    stageA_inv(P, out, outlen);
}

/* ---------- shared-transform bilinear sums (rows==3 plans only) ----------
 * out_k = eps_k * (sum of signed products of operand spectra), computed row by row of the Good-Thomas layout.  A group has nh held operands
 * (transformed once per row into tH[h]) and ns streamed operands (each transformed once per row into tS and multiplied with the held ones);
 * the product of streamed s and held h is accumulated into output o[s][h] (-1: no product) with sign sg[s][h].  The first product of an output
 * is assigned, its sign is returned as eps_k (0: output has no product); the caller applies eps_k with the 1/N scale.  Every operand
 * spectrum is formed once per row, every output row is inverse transformed once. */
void conv_bilin_otf(const plan_t *P, int nout, fp *const *out, const size_t *outlen, int ng, const bilin_grp_t *G, fp *tH0, fp *tH1, fp *tS, int *eps) {
    CTL(2);
    if (P->rows == 1) { fprintf(stderr, "conv_bilin_otf needs a rows>=2 plan\n"); exit(9); }
    size_t n = P->n;
    fp *tH[2] = { tH0, tH1 };
    for (int k = 0; k < nout; k++) eps[k] = 0;
    CTL(2 + 3 * nout);
    for (int g = 0; g < ng; g++) for (int s = 0; s < G[g].ns; s++) for (int h = 0; h < G[g].nh; h++) {
        int o = G[g].o[s][h]; CTL(6);
        if (o >= 0 && !eps[o]) eps[o] = G[g].sg[s][h];
    }
    for (int r = 0; r < P->rows; r++) {
        int done[4] = { 0, 0, 0, 0 }; CTL(2 + 2 + nout);
        for (int g = 0; g < ng; g++) {
            const bilin_grp_t *gp = &G[g]; int l0; CTL(3 + 4);
            for (int h = 0; h < gp->nh; h++) {
                l0 = 0; CTL(3 + 3);
                stageA_row(P, tH[h], r, gp->H[h], gp->lH[h], 0);
                for (int p = 0; p < P->npass; p++) { pass_fwd(tH[h], P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
            }
            for (int s = 0; s < gp->ns; s++) {
                l0 = 0; CTL(3 + 3);
                stageA_row(P, tS, r, gp->S[s], gp->lS[s], 0);
                for (int p = 0; p < P->npass; p++) { pass_fwd(tS, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
                for (int h = 0; h < gp->nh; h++) {
                    int o = gp->o[s][h]; CTL(3 + 5);                /* loop, o test, done[] test, sign test */
                    if (o < 0) continue;
                    fp *row = out[o] + (size_t)r * n; const fp *hh = tH[h];
                    if (!done[o]) { done[o] = 1; FOR8(i, n, fp_mul(&row[i], &tS[i], &hh[i]); LD(2); ST(1)); }
                    else if (gp->sg[s][h] == eps[o]) { FOR8(i, n, fp x; fp_mul(&x, &tS[i], &hh[i]); fp_add(&row[i], &row[i], &x); LD(3); ST(1)); }
                    else { FOR8(i, n, fp x; fp_mul(&x, &tS[i], &hh[i]); fp_sub(&row[i], &row[i], &x); LD(3); ST(1)); }
                }
            }
        }
        for (int k = 0; k < nout; k++) {
            CTL(3);
            if (!eps[k]) continue;
            fp *row = out[k] + (size_t)r * n; int l0 = P->a;
            for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        }
        CTL(2);
    }
    for (int k = 0; k < nout; k++) { CTL(3); if (eps[k]) stageA_inv(P, out[k], outlen[k]); }
}
