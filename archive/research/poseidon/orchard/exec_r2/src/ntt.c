/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 words in registers) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"
/* Accepted ledger rule (tanctl PR 37 proof, sections 4.1 and 5.2): loop/address work is 1/2 unit per butterfly and 1/2 unit per element of every
 * unrolled loop (a radix-8 pass has 3 control units per 12 butterflies, so 1/2 per butterfly is conservative).  The per-block CTL() charges of the
 * earlier engine are replaced by HC() half units on each butterfly / element; only per-call constants remain (CTLK). */
#undef CTL
#define CTLK(n) (X.ctl += (uint64_t)(n))
#define CTL(n) ((void)0)

static fp *tw = NULL;          /* tw[j] = rho_max^j, j < nmax/2 */
static int amax_g = 0;
static size_t nmax_g = 0;
fp ntt_w3;                      /* primitive cube root of unity */
static fp W3[3];                /* 1, w, w^2 */
static fp CH, DL;               /* -1/2, (w - w^2)/2 */

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
static void limbs_div3(uint64_t r[4], const uint64_t a[4]) {
    unsigned __int128 rem = 0;
    for (int i = 3; i >= 0; i--) { unsigned __int128 cur = (rem << 64) | a[i]; r[i] = (uint64_t)(cur / 3); rem = cur % 3; }
}

void ntt_init(int amax) {
    if (tw) ntt_free();
    amax_g = amax; nmax_g = (size_t)1 << amax;
    uint64_t pm1[4], e[4]; limbs_sub1(pm1, PALLAS_P);
    fp five; fp_from_u64(&five, 5);
    /* rho_max = 5^((p-1)/2^amax) (5 is a non-residue so this has exact order 2^amax) */
    limbs_shr(e, pm1, amax);
    fp rho; fp_pow(&rho, &five, e);
    /* w = 5^((p-1)/3) */
    limbs_div3(e, pm1); fp_pow(&ntt_w3, &five, e);
    fp one; fp_set_one(&one);
    if (fp_eq(&ntt_w3, &one)) { fprintf(stderr, "5 is a cube?\n"); exit(3); }
    tw = NEW_FP(nmax_g / 2);
    tw[0] = one; ST(1);
    for (size_t j = 1; j < nmax_g / 2; j++) { fp_mul(&tw[j], &tw[j - 1], &rho); ST(1); }
    loopc(nmax_g / 2);
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
    P.rows = rows; P.a = a; P.n = (size_t)1 << a; P.N = P.n * rows; P.shift = amax_g - a;
    int np = (a + 3) / 4; P.npass = np;
    int rem = a;
    /* last pass gets 4 layers; earlier passes take the rest, first pass smallest */
    for (int i = np - 1; i >= 0; i--) { int k = rem >= 4 ? 4 : rem; P.kk[i] = k; rem -= k; }
    if (rows == 3) {
        size_t n = P.n, beta = 0;
        for (size_t b = 1; b < n; b += 2) if ((3 * b) % n == 1) { beta = b; break; }
        P.c0 = (int)((3 * beta - 1) / n);
    }
    return P;
}
plan_t plan_for_len(size_t len, int allow3) {
    for (int a = 2; a <= amax_g; a++) {
        if (((size_t)1 << a) >= len) return make_plan(1, a);
        if (allow3 && 3 * ((size_t)1 << a) >= len) return make_plan(3, a);
    }
    fprintf(stderr, "length %zu too large for amax=%d\n", len, amax_g); exit(5);
}
static size_t brv(size_t x, int a) { size_t r = 0; for (int i = 0; i < a; i++) { r = (r << 1) | (x & 1); x >>= 1; } return r; }
size_t layout_index(const plan_t *P, size_t k) {
    size_t row = P->rows == 3 ? k % 3 : 0;
    return row * P->n + brv(k % P->n, P->a);
}
void plan_theta(const plan_t *P, fp *theta) {
    fp rho = tw[(size_t)1 << P->shift];
    if (P->rows == 1) { *theta = rho; return; }
    int e = (3 - P->c0 % 3) % 3;              /* omega3^(-c0) */
    fp_mul(theta, &rho, &W3[e]);
}

/* ---------- butterflies: straight-line register blocks (ntt_kern.h) ---------- */
#include "ntt_kern.h"
/* Charging convention of this file: LD/ST = one 256-bit load/store; CTL(n) = n executed integer / comparison / branch / shift / address
 * operations, each counted as 1.  Every statement that executes such operations carries its CTL charge next to it. */

static void kf_run(int k, int z, fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    CTL(7);   /* call, switch on k (compare, jump table), z test (2), call/return of the kernel (2) */
    switch (k) {
    case 1: if (z) kf1z(x, tw, b, D, sjs); else kf1(x, tw, b, D, sjs); break;
    case 2: if (z) kf2z(x, tw, b, D, sjs); else kf2(x, tw, b, D, sjs); break;
    case 3: if (z) kf3z(x, tw, b, D, sjs); else kf3(x, tw, b, D, sjs); break;
    default: if (z) kf4z(x, tw, b, D, sjs); else kf4(x, tw, b, D, sjs); break;
    }
}
static void ki_run(int k, int z, fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    CTL(7);   /* call, switch on k, z test (2), call/return of the kernel (2) */
    switch (k) {
    case 1: if (z) ki1z(x, tw, b, D, sj, sh, nh); else ki1(x, tw, b, D, sj, sh, nh); break;
    case 2: if (z) ki2z(x, tw, b, D, sj, sh, nh); else ki2(x, tw, b, D, sj, sh, nh); break;
    case 3: if (z) ki3z(x, tw, b, D, sj, sh, nh); else ki3(x, tw, b, D, sj, sh, nh); break;
    default: if (z) ki4z(x, tw, b, D, sj, sh, nh); else ki4(x, tw, b, D, sj, sh, nh); break;
    }
}
/* per-pass tables: sj[j] = l0 + j, sjs[j] = l0 + j + shift, D[j] = s << sjs[j] (twiddle pointer step between consecutive tp of layer j) */
static void pass_tables(int k, int l0, size_t s, int shift, size_t *D, int *sj, int *sjs) {
    for (int j = 0; j < k; j++) { sj[j] = l0 + j; sjs[j] = l0 + j + shift; D[j] = s << sjs[j]; }
    CTL(6 * (uint64_t)k + 4);                            /* per layer: three additions, a shift, a store, loop step */
}
/* One pass of k layers over a row, blocks of G = 2^k elements at stride s.  Charges per block: loop (3: increment, compare, branch),
 * block base (1), b == 0 test (2), element address updates (1 per element load/store when s > 1; none when s == 1: constant displacements),
 * twiddle pointers (inside the kernel).  Per group: loop (3) and base address (2). */
static void load_block(fp *x, const fp *base, size_t s, size_t G) {
    if (s == 1) { for (size_t t = 0; t < G; t++) x[t] = base[t]; }
    else { for (size_t t = 0; t < G; t++) x[t] = base[t * s]; CTL(G); }
    LD(G);
}
static void store_block(fp *base, const fp *x, size_t s, size_t G) {
    if (s == 1) { for (size_t t = 0; t < G; t++) base[t] = x[t]; }
    else { for (size_t t = 0; t < G; t++) base[t * s] = x[t]; CTL(G); }
    ST(G);
}
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    CTLK(18 + 6 * k);                                            /* s, G, Gs, ngrp: shift, shift, mul, shift; call, return */
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        CTL(5);                                        /* group loop + base address */
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            CTL(6);                                    /* block loop (3), base (1), b == 0 test (2) */
            load_block(x, base, s, G);
            kf_run(k, b == 0, x, tw, b, D, sjs);
            store_block(base, x, s, G);
        }
    }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0, nh = P->n >> 1;
    CTLK(19 + 6 * k);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            load_block(x, base, s, G);
            ki_run(k, b == 0, x, tw, b, D, sj, P->shift, nh);
            store_block(base, x, s, G);
        }
    }
}
enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };
/* last forward pass + pointwise + first inverse pass (s == 1): one register block, constant displacements, b == 0 always */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t G = (size_t)1 << k, ngrp = P->n >> k, nh = P->n >> 1;
    CTLK(19 + 6 * k);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, 1, P->shift, D, sj, sjs);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * G;
        CTL(4);                                        /* loop (3), base (1) */
        for (size_t t = 0; t < G; t++) x[t] = base[t];
        LD(G);
        kf_run(k, 1, x, tw, 0, D, sjs);
        HC(G);   /* pointwise: 1/2 unit per element */
        if (mode == M_SQ) { for (size_t t = 0; t < G; t++) fp_sqr(&x[t], &x[t]); }
        else { const fp *cb = C + grp * G; CTL(2); for (size_t t = 0; t < G; t++) fp_mul(&x[t], &x[t], &cb[t]); LD(G); }
        ki_run(k, 1, x, tw, 0, D, sj, P->shift, nh);
        for (size_t t = 0; t < G; t++) base[t] = x[t];
        ST(G);
    }
}

/* ---------- radix-3 stage ---------- */
static void dft3_full(const fp *v, fp *o) {
    fp t1, t2, m1, m2;
    fp_add(&t1, &v[1], &v[2]); fp_sub(&t2, &v[1], &v[2]);
    fp_add(&o[0], &v[0], &t1);
    fp_mul(&m1, &t1, &CH); fp_add(&m1, &m1, &v[0]);
    fp_mul(&m2, &t2, &DL);
    fp_add(&o[1], &m1, &m2); fp_sub(&o[2], &m1, &m2);
}
/* o[k] = sum over inputs flagged in nzmask of v[i] w^(ik); only outputs flagged in need are produced.
 * Each executed test, loop step and index operation is charged where it occurs. */
static void dft3_sel(const fp *v, int nzmask, int need, fp *o) {
    CTL(3);                                             /* call, full-case test (2) */
    if (nzmask == 7 && need == 7) { dft3_full(v, o); return; }
    for (int k = 0; k < 3; k++) {
        CTL(6);                                         /* loop (3), need test: shift, and, branch (3) */
        if (!((need >> k) & 1)) continue;
        int first = 1; fp acc; fp_set_zero(&acc);
        for (int i = 0; i < 3; i++) {
            CTL(6);                                     /* loop (3), nz test (3) */
            if (!((nzmask >> i) & 1)) continue;
            fp term = v[i]; int e = (i * k) % 3;
            CTL(4);                                     /* i*k, mod, e test, branch */
            if (e) fp_mul(&term, &v[i], &W3[e]);
            CTL(2);                                     /* first test */
            if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
        }
        o[k] = acc;
    }
}
/* Radix-3 stage helpers.  Mask tables: for an input pattern nzb (bit t set = position t of the Good-Thomas triple is nonzero) and the
 * rotation rot of the element, bit i1 of the DFT input mask is set when nzb has bit (rot + i1) % 3. */
static int mask_of(int nzb, int rot) {
    int m = 0;
    for (int i1 = 0; i1 < 3; i1++) if ((nzb >> ((rot + i1) % 3)) & 1) m |= 1 << i1;
    return m;
}
/* All three outputs from the inputs flagged in mask (switch on the mask: 3 operations, then straight-line field operations). */
static void dft3_masked(const fp *v, int mask, fp *o) {
    CTL(3);
    fp t;
    switch (mask) {
    case 1: o[0] = o[1] = o[2] = v[0]; break;
    case 2: o[0] = v[1]; fp_mul(&o[1], &v[1], &W3[1]); fp_mul(&o[2], &v[1], &W3[2]); break;
    case 4: o[0] = v[2]; fp_mul(&o[1], &v[2], &W3[2]); fp_mul(&o[2], &v[2], &W3[1]); break;
    case 3: fp_add(&o[0], &v[0], &v[1]); fp_mul(&t, &v[1], &W3[1]); fp_add(&o[1], &v[0], &t); fp_mul(&t, &v[1], &W3[2]); fp_add(&o[2], &v[0], &t); break;
    case 5: fp_add(&o[0], &v[0], &v[2]); fp_mul(&t, &v[2], &W3[2]); fp_add(&o[1], &v[0], &t); fp_mul(&t, &v[2], &W3[1]); fp_add(&o[2], &v[0], &t); break;
    case 6: { fp a, b; fp_add(&o[0], &v[1], &v[2]);
              fp_mul(&a, &v[1], &W3[1]); fp_mul(&b, &v[2], &W3[2]); fp_add(&o[1], &a, &b);
              fp_mul(&a, &v[1], &W3[2]); fp_mul(&b, &v[2], &W3[1]); fp_add(&o[2], &a, &b); break; }
    default: dft3_full(v, o); break;
    }
}
/* output k only, inputs flagged in mask: o = sum_i v[i] w^(ik).  Per input: presence test (2), first test (2), exponent selection by the switch on k (2 per call). */
static void dft3_one(const fp *v, int mask, int k, fp *o) {
    CTL(3);
    int first = 1; fp acc;
    for (int i = 0; i < 3; i++) {
        CTL(4);
        if (!((mask >> i) & 1)) continue;
        fp term = v[i]; int e = (i * k) % 3;
        if (e) fp_mul(&term, &v[i], &W3[e]);
        if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
    }
    CTL(2);
    *o = acc;
}
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(6);
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        if (dst == src && off == 0) { for (size_t i = len; i < n; i++) dst[i] = z; if (n > len) { ST(n - len); loopc(n - len); } return; }
        for (size_t i = 0; i < n; i++) { if (i < len) { dst[i] = src[off + i]; LD(1); } else dst[i] = z; }
        ST(n); loopc(n); CTL(2 * n); return;
    }
    /* regions of constant nonzero pattern: [0,b1) all three positions, [b1,b2) positions 0,1, [b2,b3) position 0, [b3,n) none */
    size_t b1 = len > 2 * n ? len - 2 * n : 0, b2 = len > n ? len - n : 0, b3 = len;
    if (b1 > n) b1 = n;
    if (b2 > n) b2 = n;
    if (b3 > n) b3 = n;
    size_t bnd[5] = { 0, b1, b2, b3, n }; static const int NZB[4] = { 7, 3, 1, 0 };
    CTLK(25);
    int c0 = P->c0 % 3;
    for (int q = 0; q < 4; q++) {
        int nzb = NZB[q], MT[3];
        for (int r = 0; r < 3; r++) MT[r] = mask_of(nzb, r);
        CTLK(30);                                        /* region loop, mask table (3 entries x 9 operations) */
        int rot = (int)((c0 * (bnd[q] % 3)) % 3);
        rot = (rot + 3 - c0) % 3; CTL(6);
        for (size_t i0 = bnd[q]; i0 < bnd[q + 1]; i0++) {
            fp u[3], v[3], o[3];
            HC(3);   /* Good-Thomas triple: 1/2 unit per element, loop unrolled by 3 so the rotation is constant */                             /* loop; rot update: add, compare, branch, subtract; mask lookup */
            rot = rot + c0; if (rot >= 3) rot -= 3;
            int mask = MT[rot];
            CTL(2);
            if (mask == 0) { fp_set_zero(&o[0]); o[1] = o[0]; o[2] = o[0]; }
            else {
                for (int t = 0; t < 3; t++) { CTL(3); if ((nzb >> t) & 1) { u[t] = src[off + i0 + n * (size_t)t]; LD(1); CTL(2); } }
                CTL(3);                                 /* switch on rot: constant permutation */
                switch (rot) { case 0: v[0] = u[0]; v[1] = u[1]; v[2] = u[2]; break; case 1: v[0] = u[1]; v[1] = u[2]; v[2] = u[0]; break; default: v[0] = u[2]; v[1] = u[0]; v[2] = u[1]; break; }
                dft3_masked(v, mask, o);
            }
            dst[i0] = o[0]; dst[i0 + n] = o[1]; dst[i0 + 2 * n] = o[2];
            ST(3); CTL(2);
        }
    }
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n; int c0 = P->c0 % 3;
    CTL(6);
    /* regions of constant needed pattern: position i0 + n*t is needed iff i0 < outlen - n*t */
    size_t r0 = outlen < n ? outlen : n, r1 = outlen > n ? (outlen - n < n ? outlen - n : n) : 0, r2 = outlen > 2 * n ? (outlen - 2 * n < n ? outlen - 2 * n : n) : 0;
    size_t bnd[4] = { 0, r2, r1, r0 }; static const int TSET[3] = { 7, 3, 1 };
    CTLK(25);
    for (int q = 0; q < 3; q++) {
        int tset = TSET[q], NT[3];
        for (int r = 0; r < 3; r++) NT[r] = mask_of(tset, r);
        CTLK(30);
        int rot = (int)((c0 * (bnd[q] % 3)) % 3);
        rot = (rot + 3 - c0) % 3; CTL(6);
        for (size_t i0 = bnd[q]; i0 < bnd[q + 1]; i0++) {
            CTL(3 + 4 + 2);
            rot = rot + c0; if (rot >= 3) rot -= 3;
            int need = NT[rot];
            HC(3);
            fp A[3], B[3], v[3];
            for (int k = 0; k < 3; k++) A[k] = buf[i0 + n * (size_t)k];
            LD(3); CTL(2);
            B[0] = A[0]; B[1] = A[2]; B[2] = A[1];
            CTL(2);
            if (need == 7) dft3_full(B, v); else dft3_sel(B, 7, need, v);
            CTL(3);                                     /* switch on rot for the destination permutation */
            int dd[3];
            if (rot == 0) { dd[0] = 0; dd[1] = 1; dd[2] = 2; } else if (rot == 1) { dd[0] = 1; dd[1] = 2; dd[2] = 0; } else { dd[0] = 2; dd[1] = 0; dd[2] = 1; }
            for (int i1 = 0; i1 < 3; i1++) { CTL(3); if ((need >> i1) & 1) { buf[i0 + n * (size_t)dd[i1]] = v[i1]; ST(1); CTL(2); } }
        }
    }
}
/* lean variant: row r of the Good-Thomas stage for the compact vector B */
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N; int c0 = P->c0 % 3, rot = (3 - P->c0 % 3) % 3;
    size_t nb = N - boff;                               /* boff < N or boff = 0 */
    CTL(10);
    for (size_t i0 = 0; i0 < n; i0++) {
        fp u[3], v[3]; int nz[3], nzb = 0; fp o;
        HC(3);
        rot = rot + c0; if (rot >= 3) rot -= 3;
        for (int t = 0; t < 3; t++) {
            size_t idx = i0 + n * (size_t)t + nb;       /* position + N - boff */
            int any = 0; fp acc;
            CTL(2 + 3 + 2);                             /* idx (2: add, add), reduction mod N (compare, branch, subtract), any, loop-entry compare */
            if (idx >= N) idx -= N;
            for (; idx < lenB; idx += N) {              /* fold modulo x^N - 1 when lenB > N */
                CTL(2 + 2 + 1);                         /* compare, branch, first test (2), increment */
                if (!any) { acc = B[idx]; any = 1; } else fp_add(&acc, &acc, &B[idx]);
                LD(1);
            }
            CTL(3);                                     /* nz assignment, if (any), nzb bit */
            nz[t] = any; if (any) { u[t] = acc; nzb |= 1 << t; }
        }
        CTL(3);                                         /* switch on rot for the permutation */
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }
        CTL(4);                                         /* mask from nzb: table lookup (2), mask == 0 test (2) */
        if (mask == 0) fp_set_zero(&o);
        else dft3_one(v, mask, r, &o);
        tmp[i0] = o; ST(1); CTL(1);
    }
}

void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    stageA_fwd(P, dst, src, off, len);
    CTL(4);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(4);
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
    }
}
void ntt_inv(const plan_t *P, fp *buf, size_t outlen) {
    CTL(4);
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = P->a;
        CTL(4);
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    stageA_inv(P, buf, outlen);
}
static void conv_core(const plan_t *P, fp *buf, int mode, const fp *C) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = 0;
        CTL(6);
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
        pass_fused(row, P, l0, P->kk[P->npass - 1], mode, C ? C + (size_t)r * P->n : NULL);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
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

/* ---------- lean variant: the spectrum of the second operand is generated one row at a time (rows==3 plans only) ---------- */
void conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                   const fp *B, size_t lenB, size_t boff, size_t outlen) {
    if (P->rows != 3) { fprintf(stderr, "conv_mulc_otf needs a rows==3 plan\n"); exit(9); }
    stageA_fwd(P, dst, src, off, len);
    for (int r = 0; r < 3; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(8);
        stageA_row(P, tmp, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmp, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
        l0 = 0;
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
        pass_fused(row, P, l0, P->kk[P->npass - 1], M_MULC, tmp);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    stageA_inv(P, dst, outlen);
}
plan_t plan3_for_len(size_t len) {
    for (int a = 2; a <= amax_g; a++) if (3 * ((size_t)1 << a) >= len) return make_plan(3, a);
    fprintf(stderr, "plan3: length %zu too large\n", len); exit(5);
}

/* out (P->N slots) = sum_t sign[t] * (A_t * B_t mod x^N - 1) * N, all operands compact (folded modulo x^N-1 if longer than N);
 * the first term must have sign +1.  tmpA, tmpB: P->n slots each.  Only positions < outlen of out are produced. */
void conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                  const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen) {
    if (P->rows != 3) { fprintf(stderr, "conv_sum_otf needs a rows==3 plan\n"); exit(9); }
    size_t n = P->n;
    for (int r = 0; r < 3; r++) {
        fp *row = out + (size_t)r * n;
        CTL(8);
        for (int t = 0; t < nt; t++) {
            int l0 = 0;
            budget_check();
            CTL(8);
            stageA_row(P, tmpA, r, A[t], lenA[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpA, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
            l0 = 0;
            stageA_row(P, tmpB, r, B[t], lenB[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpB, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
            if (t == 0) { for (size_t i = 0; i < n; i++) fp_mul(&row[i], &tmpA[i], &tmpB[i]); LD(2 * n); ST(n); }
            else if (sign[t] > 0) { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_add(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            else { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_sub(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            loopc(n);
        }
        int l0 = P->a;
        budget_check();
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    budget_check();
    stageA_inv(P, out, outlen);
}
