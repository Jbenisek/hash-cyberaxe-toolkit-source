/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 data words in registers, plus 2 working words) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "par.h"
#include "pallas_consts.h"

static fp *tw = NULL;          /* tw[j] = rho_max^j, j < nmax/2 */
static int amax_g = 0;
static size_t nmax_g = 0;
fp ntt_w3;                      /* primitive cube root of unity */
static fp W3[3];                /* 1, w, w^2 */
static fp ZERO;                 /* 0 */
static fp CH, DL;               /* -1/2, (w - w^2)/2 */

static void limbs_sub1(uint64_t r[4], const uint64_t a[4]) {      /* r = a - 1 */
    for (int i = 0; i < 4; i++) r[i] = a[i];
    CTL(4 * 4 + 2);                                    /* copy loop: 4 iterations of (3 + 1), exit 2 */
    uint64_t it = 0;
    for (int i = 0; i < 4; i++) { it++; if (r[i]) { r[i]--; break; } r[i] = ~(uint64_t)0; }
    CTL(6 * it);                                       /* per iteration: loop 3, test 2, decrement or store 1 */
}
static void limbs_shr(uint64_t r[4], const uint64_t a[4], int s) {
    int ws = s >> 6, bs = s & 63;                      /* s is a non-negative constant: word shift and bit shift by shift and mask */
    for (int i = 0; i < 4; i++) {
        uint64_t v = 0;
        if (i + ws < 4) v = a[i + ws] >> bs;
        if (bs && i + ws + 1 < 4) v |= a[i + ws + 1] << (64 - bs);
        r[i] = v;
    }
    CTL(2 + 4 * 21);                                   /* ws, bs; per iteration at most 21: loop 3, v = 0, two index tests (3 each), two loads, shifts, subtraction, or, store, test of bs (2) */
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
    uint64_t pm1[4], e[4]; limbs_sub1(pm1, PALLAS_P);
    fp five; fp_from_u64(&five, 5);
    /* rho_max = 5^((p-1)/2^amax) (5 is a non-residue so this has exact order 2^amax) */
    limbs_shr(e, pm1, amax);
    fp rho; fp_pow(&rho, &five, e);
    /* w = 5^((p-1)/3) */
    limbs_div3(e, pm1); fp_pow(&ntt_w3, &five, e);
    CTL(2 + 8);             /* the test ntt_w3 == 1 (four limb comparisons: 8 operations; compare, branch) */
    fp one; fp_set_one(&one);
    if (fp_eq(&ntt_w3, &one)) { fprintf(stderr, "5 is a cube?\n"); exit(3); }
    fp_set_zero(&ZERO);
    tw = NEW_FP(nmax_g / 2);
    tw[0] = one; ST(1);
    for (size_t j = 1; j < nmax_g / 2; j++) { fp_mul(&tw[j], &tw[j - 1], &rho); LD(1); ST(1); }
    loopc(nmax_g / 2);
    CTL(5 * INV_CTL);       /* control of the bit loops of fp_pow (x2) and fp_inv (x1): at most INV_CTL each; the other setup is a few dozen straight-line operations */
    W3[0] = one; W3[1] = ntt_w3; fp_sqr(&W3[2], &ntt_w3);
    fp two, half; fp_from_u64(&two, 2); fp_inv(&half, &two);
    fp s; fp_add(&s, &W3[1], &W3[2]); fp_mul(&CH, &s, &half);          /* (w+w^2)/2 = -1/2 */
    fp d; fp_sub(&d, &W3[1], &W3[2]); fp_mul(&DL, &d, &half);
}
void ntt_free(void) { if (tw) xfree(tw); tw = NULL; }
size_t ntt_table_bytes(void) { return (nmax_g / 2) * sizeof(fp); }

plan_t make_plan(int rows, int a) {
    plan_t P; memset(&P, 0, sizeof P);
    if (a < 2 || a > amax_g || (rows != 1 && rows != 3)) { fprintf(stderr, "bad plan rows=%d a=%d (amax=%d)\n", rows, a, amax_g); exit(4); }
    P.rows = rows; P.a = a; P.n = (size_t)1 << a; P.N = rows == 3 ? (P.n << 1) + P.n : P.n; P.shift = amax_g - a;
    CTL(18);                                       /* validity tests (4 compares, 4 branches) and the assignments above (shift, test of rows, shift and addition, subtraction) */
    int np = (a + 3) >> 2; P.npass = np;
    int rem = a;
    CTL(4);                                        /* a + 3, shift, assignments */
    /* last pass gets 4 layers; earlier passes take the rest, first pass smallest */
    for (int i = np - 1; i >= 0; i--) { int k = rem >= 4 ? 4 : rem; P.kk[i] = k; rem -= k; }
    loopc(np); CTL(4 * np);                        /* per pass: compare, select, subtract, store index */
    CTL(2);                                        /* test of rows */
    if (rows == 3) {
        /* c0 = (3 beta - 1) / n where beta = 3^-1 mod n, n = 2^a.  3 beta = c0 2^a + 1 with 0 < c0 < 3, and 2^a = 1 (a even) or 2 (a odd) modulo 3 forces
         * c0 = 2 (a even) or 1 (a odd): no search, no multiplication, no division. */
        P.c0 = (a & 1) ? 1 : 2;
        CTL(4);                                    /* and, compare, branch, assignment */
    }
    return P;
}
plan_t plan_for_len(size_t len, int allow3) {
    for (int a = 2; a <= amax_g; a++) {
        CTL(3 + 1 + 2 + (allow3 ? 4 : 0));         /* loop (3), shift, compare + branch, [shift, addition, compare, branch] */
        size_t t_ = (size_t)1 << a;
        if (t_ >= len) return make_plan(1, a);
        if (allow3 && (t_ << 1) + t_ >= len) return make_plan(3, a);
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
/* position of exponent k in the layout, with row = k mod 3 supplied by the caller (who keeps the counter): row * n + bitreverse(k mod n).  n is a power of two,
 * so k mod n is a mask, and row * n with row in {0, 1, 2} is a selection among 0, n and n + n. */
size_t layout_index_r(const plan_t *P, size_t row, size_t k) {
    CTL(12);                                       /* call (1), rows test (2), n - 1 and the mask (2), selection of 0 / n / n + n (6), addition (1) */
    size_t off = 0;
    if (P->rows == 3) { if (row == 1) off = P->n; else if (row == 2) off = P->n + P->n; }
    return off + brv(k & (P->n - 1), P->a);
}
void plan_theta(const plan_t *P, fp *theta) {
    fp rho = tw[(size_t)1 << P->shift]; LD(1); CTL(1);
    CTL(2);                                        /* test of rows */
    if (P->rows == 1) { *theta = rho; return; }
    int e = 3 - P->c0;                        /* omega3^(-c0), c0 in {1, 2} */
    CTL(4);                                        /* subtraction, address of W3[e], call and return */
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
/* ---- threads: a pass over one row is split into chunks of blocks (a block = 2^k elements of one butterfly register block).  A chunk lies inside one group
 * (blocks b0 .. b1-1 of the group, kernel pfNb / piNb) or covers whole groups (kernel pfNc / piNc); the charges of the pass call itself (entry, exit, tables,
 * switch) stay with the main thread, the per-block and per-group charges are inside the kernels, so the sum is the same as for one thread.
 * A pass is split only when the row has at least PAR_MIN_N elements; a thread is used per 2^PAR_LMIN_ELEM elements. */
#pragma GCC diagnostic ignored "-Wmaybe-uninitialized"   /* pass_tables fills the first k entries of the 4-entry tables; the copies below read only those */
typedef struct { fp *row; const fp *tw; size_t s, ngrp; int ls, k, inv; size_t D[4]; int sj[4], sjs[4]; int sh; size_t nh; par_plan_t pl; } ppass_t;
static void job_pass(void *c_, size_t c) {
    ppass_t *a = (ppass_t *)c_;
    size_t u = par_lo(&a->pl, c), cs = a->pl.cs, s = a->s;
    size_t g = u >> a->ls;
    fp *rb = a->row + (g << (a->ls + a->k));
    if (cs <= s) {
        size_t b0 = u & (s - 1), b1 = b0 + cs;
        if (!a->inv) { switch (a->k) { case 1: pf1b(rb, s, b0, b1, a->tw, a->D, a->sjs); break; case 2: pf2b(rb, s, b0, b1, a->tw, a->D, a->sjs); break;
                                        case 3: pf3b(rb, s, b0, b1, a->tw, a->D, a->sjs); break; default: pf4b(rb, s, b0, b1, a->tw, a->D, a->sjs); break; } }
        else { switch (a->k) { case 1: pi1b(rb, s, b0, b1, a->tw, a->D, a->sj, a->sh, a->nh); break; case 2: pi2b(rb, s, b0, b1, a->tw, a->D, a->sj, a->sh, a->nh); break;
                               case 3: pi3b(rb, s, b0, b1, a->tw, a->D, a->sj, a->sh, a->nh); break; default: pi4b(rb, s, b0, b1, a->tw, a->D, a->sj, a->sh, a->nh); break; } }
    } else {
        size_t ng = cs >> a->ls;
        if (!a->inv) { switch (a->k) { case 1: pf1c(rb, s, ng, a->tw, a->D, a->sjs); break; case 2: pf2c(rb, s, ng, a->tw, a->D, a->sjs); break;
                                        case 3: pf3c(rb, s, ng, a->tw, a->D, a->sjs); break; default: pf4c(rb, s, ng, a->tw, a->D, a->sjs); break; } }
        else { switch (a->k) { case 1: pi1c(rb, s, ng, a->tw, a->D, a->sj, a->sh, a->nh); break; case 2: pi2c(rb, s, ng, a->tw, a->D, a->sj, a->sh, a->nh); break;
                               case 3: pi3c(rb, s, ng, a->tw, a->D, a->sj, a->sh, a->nh); break; default: pi4c(rb, s, ng, a->tw, a->D, a->sj, a->sh, a->nh); break; } }
    }
}
/* run a pass in parallel if it is big enough; returns 1 if it did (the 4 operations of the entry and exit of the pass call are charged here, as in pfN / piN) */
static int pass_par(fp *row, const plan_t *P, int k, int inv, const size_t *D, const int *sj, const int *sjs, size_t s, size_t ngrp, size_t nh) {
    if (!par_big(P->n)) return 0;
    size_t total = ngrp * s;                         /* n >> k: a product of two powers of two (a shift in the sequential code) */
    par_plan_t pl = par_plan(total, PAR_LMIN_ELEM - k, 0);
    if (pl.w < 2) return 0;
    ppass_t a; a.row = row; a.tw = tw; a.s = s; a.ngrp = ngrp; a.k = k; a.inv = inv; a.pl = pl; a.sh = P->shift; a.nh = nh;
    a.ls = 0; while (((size_t)1 << a.ls) < s) a.ls++;
    for (int j = 0; j < k; j++) { a.D[j] = D[j]; a.sj[j] = sj[j]; a.sjs[j] = sjs[j]; }
    CTL(4);
    par_run(pl.nch, pl.w, job_pass, &a);
    return 1;
}
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), ngrp = (size_t)1 << l0;
    CTL(5);                                              /* s, ngrp: two shifts, an add; call, return */
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    CTL(4);                                              /* switch on k: compare, jump table */
    if (pass_par(row, P, k, 0, D, sj, sjs, s, ngrp, 0)) return;
    switch (k) { case 1: pf1(row, s, ngrp, tw, D, sjs); break; case 2: pf2(row, s, ngrp, tw, D, sjs); break;
                 case 3: pf3(row, s, ngrp, tw, D, sjs); break; default: pf4(row, s, ngrp, tw, D, sjs); break; }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), ngrp = (size_t)1 << l0, nh = P->n >> 1;
    CTL(6);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    CTL(4);
    if (pass_par(row, P, k, 1, D, sj, sjs, s, ngrp, nh)) return;
    switch (k) { case 1: pi1(row, s, ngrp, tw, D, sj, P->shift, nh); break; case 2: pi2(row, s, ngrp, tw, D, sj, P->shift, nh); break;
                 case 3: pi3(row, s, ngrp, tw, D, sj, P->shift, nh); break; default: pi4(row, s, ngrp, tw, D, sj, P->shift, nh); break; }
}
enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };
/* last forward pass + pointwise + first inverse pass (s == 1) in one register-resident block; split into chunks of whole groups (contiguous 2^k elements each) */
typedef struct { fp *row; const fp *C; const fp *tw; int k, mode; size_t D[4]; int sj[4], sjs[4]; int sh; size_t nh; par_plan_t pl; size_t ngrp; } pfuse_t;
static void job_fused(void *c_, size_t c) {
    pfuse_t *a = (pfuse_t *)c_;
    size_t g0 = par_lo(&a->pl, c), g1 = par_hi(&a->pl, c, a->ngrp), ng = g1 - g0, off = g0 << a->k;
    fp *row = a->row + off; const fp *C = a->C ? a->C + off : NULL;
    if (a->mode == M_SQ) {
        switch (a->k) { case 1: pu1c_sq(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh); break; case 2: pu2c_sq(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh); break;
                        case 3: pu3c_sq(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh); break; default: pu4c_sq(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh); break; }
    } else {
        switch (a->k) { case 1: pu1c_mul(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh, C); break; case 2: pu2c_mul(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh, C); break;
                        case 3: pu3c_mul(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh, C); break; default: pu4c_mul(row, ng, a->tw, a->D, a->sjs, a->sj, a->sh, a->nh, C); break; }
    }
}
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t ngrp = P->n >> k, nh = P->n >> 1;
    CTL(6);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, 1, P->shift, D, sj, sjs);
    CTL(6);                                              /* switch on mode and on k */
    if (par_big(P->n)) {
        par_plan_t pl = par_plan(ngrp, PAR_LMIN_ELEM - k, 0);
        if (pl.w >= 2) {
            pfuse_t a; a.row = row; a.C = mode == M_SQ ? NULL : C; a.tw = tw; a.k = k; a.mode = mode; a.sh = P->shift; a.nh = nh; a.pl = pl; a.ngrp = ngrp;
            for (int j = 0; j < k; j++) { a.D[j] = D[j]; a.sj[j] = sj[j]; a.sjs[j] = sjs[j]; }
            CTL(mode == M_SQ ? 3 : 4);                   /* entry and exit of the pass call, as in puN */
            par_run(pl.nch, pl.w, job_fused, &a);
            return;
        }
    }
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
/* Threads: the loop over the groups of three positions in the middle of a driver call is split into chunks of triples (rgXm_*, same kernels and same 4 control
 * operations per triple, charged by whoever runs the triple); the head (up to two positions), the divisions by 3 and the tail stay with the calling thread, which
 * charges them as before, so the sum is the same as for one thread.  A call is split only when it has at least PAR_MIN_TRI triples. */
#ifndef PAR_MIN_TRI
#define PAR_MIN_TRI ((size_t)1 << 15)
#endif
#ifndef PAR_LMIN_TRI
#define PAR_LMIN_TRI 14
#endif
typedef struct { fp *dst; const fp *S; ptrdiff_t d0, d1, d2; size_t n, i0, nt; par_plan_t pl; } drvctx_t;
#define DRV_F(pat, c0, r0, r1, r2)                                                                                \
    static void rgfm_##pat##_##c0(void *c_, size_t ch) {                                                          \
        drvctx_t *a_ = (drvctx_t *)c_; fp *dst = a_->dst; const fp *S = a_->S; ptrdiff_t d0 = a_->d0, d1 = a_->d1, d2 = a_->d2; size_t n = a_->n; \
        size_t q0 = par_lo(&a_->pl, ch), q1 = par_hi(&a_->pl, ch, a_->nt), i = a_->i0 + 3 * q0;                    \
        _MIDW(KF(pat, r0, o), KF(pat, r1, o), KF(pat, r2, o)) }                                                   \
    static void rgf_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)d0; (void)d1; (void)d2;                                                                             \
        _DRV(rgfm_##pat##_##c0, KF(pat, r0, o), KF(pat, r1, o), KF(pat, r2, o)) }
#define DRV_I(pat, c0, r0, r1, r2)                                                                                \
    static void rgim_##pat##_##c0(void *c_, size_t ch) {                                                          \
        drvctx_t *a_ = (drvctx_t *)c_; fp *dst = a_->dst; size_t n = a_->n;                                       \
        size_t q0 = par_lo(&a_->pl, ch), q1 = par_hi(&a_->pl, ch, a_->nt), i = a_->i0 + 3 * q0;                    \
        _MIDW(KI(pat, r0, o), KI(pat, r1, o), KI(pat, r2, o)) }                                                   \
    static void rgi_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)S; (void)d0; (void)d1; (void)d2;                                                                    \
        _DRV(rgim_##pat##_##c0, KI(pat, r0, o), KI(pat, r1, o), KI(pat, r2, o)) }
#define DRV_R(r, pat, c0, r0, r1, r2)                                                                             \
    static void rgr##r##m_##pat##_##c0(void *c_, size_t ch) {                                                     \
        drvctx_t *a_ = (drvctx_t *)c_; fp *dst = a_->dst; const fp *S = a_->S; ptrdiff_t d0 = a_->d0, d1 = a_->d1, d2 = a_->d2; \
        size_t q0 = par_lo(&a_->pl, ch), q1 = par_hi(&a_->pl, ch, a_->nt), i = a_->i0 + 3 * q0;                    \
        _MIDW(KR(r, pat, r0, o), KR(r, pat, r1, o), KR(r, pat, r2, o)) }                                          \
    static void rgr##r##_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)n;                                                                                                  \
        _DRV(rgr##r##m_##pat##_##c0, KR(r, pat, r0, o), KR(r, pat, r1, o), KR(r, pat, r2, o)) }
/* the middle loop of a chunk: triples q0 .. q1-1, 4 control operations each (index update, loop test, branch: the same as in the sequential loop) */
#define _MIDW(K0, K1, K2) for (size_t q = q0; q < q1; q++) { _SUB(K0, 0); _SUB(K1, 1); _SUB(K2, 2); i += 3; CTL(1 + 3); }
/* in a driver: split the middle loop among threads when it is big enough (the 2 operations of the test and the planning are thread control); evaluates to 1 if it did */
#define _MIDPAR(MFN) (par_nt > 1 && !par_in_job && ({ THR_CHARGE(2); nt >= PAR_MIN_TRI; }) && ({                                   \
        par_plan_t pl_ = par_plan(nt, PAR_LMIN_TRI, 0); int ok_ = pl_.w >= 2;                                      \
        if (ok_) { drvctx_t c_; c_.dst = dst; c_.S = S; c_.d0 = d0; c_.d1 = d1; c_.d2 = d2; c_.n = n; c_.i0 = i; c_.nt = nt; c_.pl = pl_;       \
                   par_run(pl_.nch, pl_.w, MFN, &c_); i += 3 * nt; }                                              \
        ok_; }))
/* _DRV(MFN, K0, K1, K2): K_ph is the kernel call for phase ph with the placeholder offset o; MFN the chunk function of the middle loop */
#define _DRV(MFN, K0, K1, K2)                                                                                     \
    size_t i = lo, ph; (void)udivmod(lo, 3, &ph); CTL(1);                                                         \
    CTL(2); if (ph == 1) {                                                                                        \
        CTL(2); if (i < hi) { _SUB(K1, 0); i++; CTL(1);                                                           \
            CTL(2); if (i < hi) { _SUB(K2, 0); i++; CTL(1); } }                                                   \
    } else { CTL(2); if (ph == 2) { CTL(2); if (i < hi) { _SUB(K2, 0); i++; CTL(1); } } }                         \
    size_t nt = 0; CTL(2); if (hi > i) { size_t r3_; nt = udivmod(hi - i, 3, &r3_); CTL(2); }                      \
    if (!_MIDPAR(MFN)) { size_t q0 = 0, q1 = nt; _MIDW(K0, K1, K2) }                                                                      \
    CTL(2);                                                                                                       \
    CTL(2); if (hi > i) { size_t rem = hi - i; CTL(1);                                                            \
        _SUB(K0, 0); i++; CTL(1);                                                                                 \
        CTL(2); if (rem == 2) { _SUB(K1, 0); } }
#define _SUB(K, off) do { const size_t o = (off); K; } while (0)
#include "ntt_a3.h"

/* Regions of constant pattern.  Position pos = i0 + n*t (t = 0, 1, 2) of the length-N cyclic vector holds B[(pos + N - boff) mod N] when
 * that index is < lenB (lenB <= N), else 0.  bp[] receives the sorted breakpoints (bp[0] = 0, last = n), pat[] the pattern of each range
 * (bit t set: position t of the triple is nonzero).  Returns the number of ranges.  Every executed operation is charged. */
static int split_regions(size_t n, size_t N, size_t boff, size_t lenB, size_t *bp, int *pat) {
    if (lenB > N) { fprintf(stderr, "split_regions: lenB %zu > N %zu\n", lenB, N); exit(10); }
    int cnt = 0;
    bp[cnt++] = 0; CTL(3);
    size_t nt0 = 0;                                                              /* n * t by repeated addition; n t + N - boff < 2N, so one conditional subtraction is the modulo */
    for (int t = 0; t < 3; t++) {
        size_t st = nt0 + N - boff; if (st >= N) st -= N; nt0 += n; CTL(3 + 6);   /* loop, add, subtract, compare, branch, conditional subtraction, running sum */
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
            size_t nt1 = 0;
            for (int t = 0; t < 3; t++) { size_t idx = lo + nt1 + N - boff; if (idx >= N) idx -= N; p |= (idx < lenB) << t; nt1 += n; CTL(3 + 3 + 3 + 4); }   /* lo + n t + N - boff < 2N: one conditional subtraction */
            CTL(2 + 3);
            bp[m] = lo; pat[m] = p; m++; CTL(2);
        }
    }
    CTL(2);
    bp[m] = n; CTL(1);
    return m;
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
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, P->N, 0, len, bp, pat);
    int c0 = P->c0; CTL(2);                                                       /* c0 is 1 or 2 */
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
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, P->N, 0, outlen, bp, pat);
    int c0 = P->c0; CTL(2);
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
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, N, boff, lenB, bp, pat);
    int c0 = P->c0; CTL(2);
    for (int q = 0; q < nr; q++) {
        size_t lo = bp[q];
        ptrdiff_t d[3];
        size_t nt_ = 0;                                                           /* n * t by repeated addition */
        for (int t = 0; t < 3; t++) { size_t idx = lo + nt_ + N - boff; if (idx >= N) idx -= N; d[t] = (ptrdiff_t)idx - (ptrdiff_t)lo; nt_ += n; CTL(3 + 8); }   /* idx < 2N, so one conditional subtraction is the modulo */
        CTL(2);
        CTL(4);
        RGR[r][c0][pat[q]](tmp, B, d[0], d[1], d[2], n, lo, bp[q + 1]);
        CTL(3);
    }
    CTL(2);
}

/* ---- threads, row-parallel mode.  A plan with 3 rows of a medium length n (2^RP_MIN_LOG <= n <= 2^RP_MAX_LOG, below the lengths at which the passes of one row are split
 * among threads) has three independent row pipelines.  They are run as the 3 chunks of one dispatch, chunk r = row r; each row has its own scratch row(s): row 0 the
 * caller's, rows 1 and 2 the static array rp_scr (3 rows of 2^RP_MAX_LOG slots each, 3 MiB for RP_MAX_LOG = 14).  The body of a row is the sequential body, with its
 * own charges; the charges that belong to the whole call stay with the main thread.  Inside a dispatched chunk nothing is split further (par_in_job). */
#ifndef RP_MIN_LOG
#define RP_MIN_LOG 11
#endif
#ifndef RP_MAX_LOG
#define RP_MAX_LOG 14
#endif
static fp rp_scr[2][3][(size_t)1 << RP_MAX_LOG];
static inline int rp_on(const plan_t *P) {
    if (par_nt < 2 || par_in_job) return 0;
    THR_CHARGE(3);                                  /* the test of the thread count, of the plan and of the length */
    return P->rows == 3 && P->a >= RP_MIN_LOG && P->a <= RP_MAX_LOG && P->a <= PAR_LMIN_ELEM;
}
static inline int rp_w(void) { return par_nt < 3 ? par_nt : 3; }
static inline fp *rp_s(fp *own, int r, int k) { return r == 0 ? own : rp_scr[r - 1][k]; }   /* scratch row k of row r */

typedef struct { const plan_t *P; fp *buf; int inv; } rp_t1;
static void ntt_fwd_row(const plan_t *P, fp *dst, int r) {
    fp *row = dst + (size_t)r * P->n; int l0 = 0;
    CTL(4);
    for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
    CTL(2);
}
static void ntt_inv_row(const plan_t *P, fp *buf, int r) {
    fp *row = buf + (size_t)r * P->n; int l0 = P->a;
    CTL(4);
    for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
    CTL(2);
}
static void job_t1(void *c_, size_t r) { rp_t1 *a = (rp_t1 *)c_; if (a->inv) ntt_inv_row(a->P, a->buf, (int)r); else ntt_fwd_row(a->P, a->buf, (int)r); }
void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    stageA_fwd(P, dst, src, off, len);
    if (rp_on(P)) { rp_t1 a = { P, dst, 0 }; par_run(3, rp_w(), job_t1, &a); }
    else for (int r = 0; r < P->rows; r++) ntt_fwd_row(P, dst, r);
    CTL(2);
}
void ntt_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (rp_on(P)) { rp_t1 a = { P, buf, 1 }; par_run(3, rp_w(), job_t1, &a); }
    else for (int r = 0; r < P->rows; r++) ntt_inv_row(P, buf, r);
    CTL(2);
    stageA_inv(P, buf, outlen);
}
typedef struct { const plan_t *P; fp *buf; int mode; const fp *C; } rp_core_t;
static void conv_core_row(const plan_t *P, fp *buf, int mode, const fp *C, int r) {
    size_t ro = (size_t)r * P->n; fp *row = buf + ro; int l0 = 0;
    CTL(3 + 5 + 1);
    for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
    CTL(4);                                    /* C ? ... : NULL: compare, branch, add, running offset */
    pass_fused(row, P, l0, P->kk[P->npass - 1], mode, C ? C + ro : NULL);
    for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
    CTL(4);
}
static void job_core(void *c_, size_t r) { rp_core_t *a = (rp_core_t *)c_; conv_core_row(a->P, a->buf, a->mode, a->C, (int)r); }
static void conv_core(const plan_t *P, fp *buf, int mode, const fp *C) {
    if (rp_on(P)) { rp_core_t a = { P, buf, mode, C }; par_run(3, rp_w(), job_core, &a); }
    else for (int r = 0; r < P->rows; r++) conv_core_row(P, buf, mode, C, r);
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
typedef struct { const plan_t *P; fp *dst, *tmp; const fp *B; size_t lenB, boff; } rp_mulc_t;
static void mulc_otf_row(const plan_t *P, fp *dst, fp *tmp, const fp *B, size_t lenB, size_t boff, int r) {
    fp *row = dst + (size_t)r * P->n; int l0 = 0;
    CTL(2 + 2 + 2 + 5 + 1);
    stageA_row(P, tmp, r, B, lenB, boff);
    for (int p = 0; p < P->npass; p++) { pass_fwd(tmp, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
    CTL(2);
    l0 = 0;
    for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
    pass_fused(row, P, l0, P->kk[P->npass - 1], M_MULC, tmp);
    for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
    CTL(4);
}
static void job_mulc(void *c_, size_t r) { rp_mulc_t *a = (rp_mulc_t *)c_; mulc_otf_row(a->P, a->dst, rp_s(a->tmp, (int)r, 0), a->B, a->lenB, a->boff, (int)r); }
void conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                   const fp *B, size_t lenB, size_t boff, size_t outlen) {
    CTL(2);                                        /* validity test of rows */
    if (P->rows != 3) { fprintf(stderr, "conv_mulc_otf needs a rows==3 plan\n"); exit(9); }
    stageA_fwd(P, dst, src, off, len);
    CTL(4);
    if (rp_on(P)) { rp_mulc_t a = { P, dst, tmp, B, lenB, boff }; par_run(3, rp_w(), job_mulc, &a); }
    else for (int r = 0; r < 3; r++) mulc_otf_row(P, dst, tmp, B, lenB, boff, r);
    CTL(2);
    stageA_inv(P, dst, outlen);
}

/* spectrum of the compact vector B (lenB coefficients, cyclic offset boff) of a rows==3 plan, generated row by row straight into dst (P->N slots) */
typedef struct { const plan_t *P; fp *dst; const fp *B; size_t lenB, boff; } rp_shift_t;
static void shifted_row(const plan_t *P, fp *dst, const fp *B, size_t lenB, size_t boff, int r) {
    fp *row = dst + (size_t)r * P->n; int l0 = 0;
    CTL(2 + 2 + 1);
    stageA_row(P, row, r, B, lenB, boff);
    for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
}
static void job_shift(void *c_, size_t r) { rp_shift_t *a = (rp_shift_t *)c_; shifted_row(a->P, a->dst, a->B, a->lenB, a->boff, (int)r); }
void ntt_fwd_shifted(const plan_t *P, fp *dst, const fp *B, size_t lenB, size_t boff) {
    CTL(4);
    if (rp_on(P)) { rp_shift_t a = { P, dst, B, lenB, boff }; par_run(3, rp_w(), job_shift, &a); }
    else for (int r = 0; r < 3; r++) shifted_row(P, dst, B, lenB, boff, r);
}
plan_t plan3_for_len(size_t len) {
    for (int a = 2; a <= amax_g; a++) { CTL(3 + 1 + 2 + 2); size_t t_ = (size_t)1 << a; if ((t_ << 1) + t_ >= len) return make_plan(3, a); }   /* loop, shift, shift and addition, compare, branch */
    fprintf(stderr, "plan3: length %zu too large\n", len); exit(5);
}

/* ---------- pointwise product loops (conv_sum_otf, conv_bilin_otf) ----------
 * mode 0: dst = a * b; 1: dst += a * b; 2: dst -= a * b, over n elements.  The control of the whole loop is the FOR8 charge, computed and charged once;
 * the body of an iteration (2 or 3 loads, 1 store, the field operations) is charged by the thread that runs it. */
typedef struct { fp *dst; const fp *a, *b; int mode; size_t n; par_plan_t pl; } pwctx_t;
static void pw_body(fp *dst, const fp *a, const fp *b, int mode, size_t lo, size_t hi) {
    if (mode == 0) { for (size_t i = lo; i < hi; i++) { fp_mul(&dst[i], &a[i], &b[i]); LD(2); ST(1); } }
    else if (mode == 1) { for (size_t i = lo; i < hi; i++) { fp x; fp_mul(&x, &a[i], &b[i]); fp_add(&dst[i], &dst[i], &x); LD(3); ST(1); } }
    else { for (size_t i = lo; i < hi; i++) { fp x; fp_mul(&x, &a[i], &b[i]); fp_sub(&dst[i], &dst[i], &x); LD(3); ST(1); } }
}
static void job_pw(void *c_, size_t c) { pwctx_t *a = (pwctx_t *)c_; pw_body(a->dst, a->a, a->b, a->mode, par_lo(&a->pl, c), par_hi(&a->pl, c, a->n)); }
static void pw_loop(fp *dst, const fp *a, const fp *b, int mode, size_t n) {
    size_t n8 = n & ~(size_t)7;
    CTL(1 + 3 * (n8 >> 3) + 2 + 3 * (n - n8) + 2);     /* the control of FOR8 over n elements */
    if (par_big(n)) {
        par_plan_t pl = par_plan(n, PAR_LMIN_LIN, 3);
        if (pl.w >= 2) { pwctx_t c; c.dst = dst; c.a = a; c.b = b; c.mode = mode; c.n = n; c.pl = pl; par_run(pl.nch, pl.w, job_pw, &c); return; }
    }
    pw_body(dst, a, b, mode, 0, n);
}

/* out (P->N slots) = sum_t sign[t] * (A_t * B_t mod x^N - 1) * N, all operands compact (folded modulo x^N-1 if longer than N);
 * the first term must have sign +1.  tmpA, tmpB: P->n slots each.  Only positions < outlen of out are produced. */
typedef struct { const plan_t *P; fp *out; int nt; const fp *const *A; const size_t *lenA; const fp *const *B; const size_t *lenB; const int *sign; fp *tmpA, *tmpB; } rp_sum_t;
static void sum_row(const rp_sum_t *a, fp *tmpA, fp *tmpB, int r) {
    const plan_t *P = a->P; size_t n = P->n;
    fp *row = a->out + (size_t)r * n; CTL(2 + 2 + 1);
    for (int t = 0; t < a->nt; t++) {
        int l0 = 0; CTL(3 + 6);                /* loop; the array selections A[t], lenA[t], B[t], lenB[t] and the argument setups */
        stageA_row(P, tmpA, r, a->A[t], a->lenA[t], 0);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmpA, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(2);
        l0 = 0;
        stageA_row(P, tmpB, r, a->B[t], a->lenB[t], 0);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmpB, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(2 + 4);                            /* loop exit; the tests t == 0 and sign[t] > 0 */
        if (t == 0) pw_loop(row, tmpA, tmpB, 0, n);
        else if (a->sign[t] > 0) pw_loop(row, tmpA, tmpB, 1, n);
        else pw_loop(row, tmpA, tmpB, 2, n);
    }
    CTL(2);
    int l0 = P->a;
    for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
    CTL(2);
}
static void job_sum(void *c_, size_t r) { const rp_sum_t *a = (const rp_sum_t *)c_; sum_row(a, rp_s(a->tmpA, (int)r, 0), rp_s(a->tmpB, (int)r, 1), (int)r); }
void conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                  const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen) {
    CTL(2);                                        /* validity test of rows */
    if (P->rows != 3) { fprintf(stderr, "conv_sum_otf needs a rows==3 plan\n"); exit(9); }
    CTL(2);
    rp_sum_t a = { P, out, nt, A, lenA, B, lenB, sign, tmpA, tmpB };
    if (rp_on(P)) par_run(3, rp_w(), job_sum, &a);
    else for (int r = 0; r < 3; r++) sum_row(&a, tmpA, tmpB, r);
    CTL(2);
    stageA_inv(P, out, outlen);
}

/* ---------- shared-transform bilinear sums (rows==3 plans only) ----------
 * out_k = eps_k * (sum of signed products of operand spectra), computed row by row of the Good-Thomas layout.  A group has nh held operands
 * (transformed once per row into tH[h]) and ns streamed operands (each transformed once per row into tS and multiplied with the held ones);
 * the product of streamed s and held h is accumulated into output o[s][h] (-1: no product) with sign sg[s][h].  The first product of an output
 * is assigned, its sign is returned as eps_k (0: output has no product); the caller applies eps_k with the 1/N scale.  Every operand
 * spectrum is formed once per row, every output row is inverse transformed once. */
typedef struct { const plan_t *P; int nout; fp *const *out; int ng; const bilin_grp_t *G; fp *tH0, *tH1, *tS; const int *eps; } rp_bil_t;
static void bilin_row(const rp_bil_t *a, fp *tH0, fp *tH1, fp *tS, int r) {
    const plan_t *P = a->P; size_t n = P->n; int nout = a->nout, ng = a->ng; const bilin_grp_t *G = a->G; const int *eps = a->eps;
    fp *tH[2] = { tH0, tH1 };
    size_t ro = (size_t)r * n;
    int done[4] = { 0, 0, 0, 0 }; CTL(2 + 2 + nout + 1);
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
                fp *row = a->out[o] + ro; const fp *hh = tH[h];
                if (!done[o]) { done[o] = 1; pw_loop(row, tS, hh, 0, n); }
                else if (gp->sg[s][h] == eps[o]) pw_loop(row, tS, hh, 1, n);
                else pw_loop(row, tS, hh, 2, n);
            }
        }
    }
    for (int k = 0; k < nout; k++) {
        CTL(3);
        if (!eps[k]) continue;
        fp *row = a->out[k] + ro; int l0 = P->a;
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
    }
    CTL(2);                                                           /* counted with the row setup above (the running row offset) */
}
static void job_bil(void *c_, size_t r) { const rp_bil_t *a = (const rp_bil_t *)c_; bilin_row(a, rp_s(a->tH0, (int)r, 0), rp_s(a->tH1, (int)r, 1), rp_s(a->tS, (int)r, 2), (int)r); }
void conv_bilin_otf(const plan_t *P, int nout, fp *const *out, const size_t *outlen, int ng, const bilin_grp_t *G, fp *tH0, fp *tH1, fp *tS, int *eps) {
    CTL(2);
    if (P->rows != 3) { fprintf(stderr, "conv_bilin_otf needs a rows==3 plan\n"); exit(9); }
    for (int k = 0; k < nout; k++) eps[k] = 0;
    CTL(2 + 3 * nout);
    for (int g = 0; g < ng; g++) for (int s = 0; s < G[g].ns; s++) for (int h = 0; h < G[g].nh; h++) {
        int o = G[g].o[s][h]; CTL(6);
        if (o >= 0 && !eps[o]) eps[o] = G[g].sg[s][h];
    }
    rp_bil_t a = { P, nout, out, ng, G, tH0, tH1, tS, eps };
    if (rp_on(P)) par_run(3, rp_w(), job_bil, &a);
    else for (int r = 0; r < 3; r++) bilin_row(&a, tH0, tH1, tS, r);
    for (int k = 0; k < nout; k++) { CTL(3); if (eps[k]) stageA_inv(P, out[k], outlen[k]); }
}
