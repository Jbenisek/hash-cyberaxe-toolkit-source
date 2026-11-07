/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 words in registers) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"

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

/* ---------- butterflies ---------- */
static inline void bf_fwd(fp *u, fp *v, const fp *w) {
    fp t; fp_sub(&t, u, v); fp_add(u, u, v);
    if (w) fp_mul(v, &t, w); else *v = t;
}
static inline void blk_fwd(fp *x, int k, int l0, size_t b, size_t s, int shift) {
    size_t K = (size_t)1 << k;
    for (int j = 0; j < k; j++) {
        size_t half = (size_t)1 << (k - 1 - j);
        for (size_t tp = 0; tp < half; tp++) {
            size_t idx = (b + tp * s) << (l0 + j);
            const fp *w = NULL;
            if (idx) { w = &tw[idx << shift]; LD(1); }
            for (size_t t = tp; t < K; t += 2 * half) bf_fwd(&x[t], &x[t + half], w);
        }
    }
}
/* inverse of the forward butterfly (u,v)->(u+v,(u-v)w), unnormalised: (A,B) -> (A + B w^-1, A - B w^-1),
 * w^-1 = -tw[n/2-idx]  =>  (A - B*wp, A + B*wp) */
static inline void blk_inv(fp *x, int k, int l0, size_t b, size_t s, int shift, size_t nh) {
    size_t K = (size_t)1 << k;
    for (int j = k - 1; j >= 0; j--) {
        size_t half = (size_t)1 << (k - 1 - j);
        for (size_t tp = 0; tp < half; tp++) {
            size_t idx = (b + tp * s) << (l0 + j);
            const fp *wp = NULL;
            if (idx) { wp = &tw[(nh - idx) << shift]; LD(1); }
            for (size_t t = tp; t < K; t += 2 * half) {
                fp *u = &x[t], *v = &x[t + half];
                if (!wp) { fp tt = *v; fp_sub(v, u, &tt); fp_add(u, u, &tt); }
                else { fp tt, A = *u; fp_mul(&tt, v, wp); fp_sub(u, &A, &tt); fp_add(v, &A, &tt); }
            }
        }
    }
}

enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };

static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++)
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            for (size_t t = 0; t < G; t++) x[t] = base[t * s];
            LD(G);
            blk_fwd(x, k, l0, b, s, P->shift);
            for (size_t t = 0; t < G; t++) base[t * s] = x[t];
            ST(G); CTL(4);
        }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++)
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            for (size_t t = 0; t < G; t++) x[t] = base[t * s];
            LD(G);
            blk_inv(x, k, l0, b, s, P->shift, P->n >> 1);
            for (size_t t = 0; t < G; t++) base[t * s] = x[t];
            ST(G); CTL(4);
        }
}
/* last forward pass + pointwise + first inverse pass (s == 1) in one register-resident block */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t G = (size_t)1 << k, ngrp = P->n >> k;
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * G;
        for (size_t t = 0; t < G; t++) x[t] = base[t];
        LD(G);
        blk_fwd(x, k, l0, 0, 1, P->shift);
        if (mode == M_SQ) { for (size_t t = 0; t < G; t++) fp_sqr(&x[t], &x[t]); }
        else { const fp *cb = C + grp * G; for (size_t t = 0; t < G; t++) fp_mul(&x[t], &x[t], &cb[t]); LD(G); }
        blk_inv(x, k, l0, 0, 1, P->shift, P->n >> 1);
        for (size_t t = 0; t < G; t++) base[t] = x[t];
        ST(G); CTL(4);
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
/* o[k] = sum over inputs flagged in nzmask of v[i] w^(ik); only outputs flagged in need are produced */
static void dft3_sel(const fp *v, int nzmask, int need, fp *o) {
    if (nzmask == 7 && need == 7) { dft3_full(v, o); return; }
    for (int k = 0; k < 3; k++) {
        if (!((need >> k) & 1)) continue;
        int first = 1; fp acc; fp_set_zero(&acc);
        for (int i = 0; i < 3; i++) {
            if (!((nzmask >> i) & 1)) continue;
            fp term = v[i]; int e = (i * k) % 3;
            if (e) fp_mul(&term, &v[i], &W3[e]);
            if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
        }
        o[k] = acc;
    }
}
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        if (dst == src && off == 0) { for (size_t i = len; i < n; i++) dst[i] = z; if (n > len) { ST(n - len); loopc(n - len); } return; }
        for (size_t i = 0; i < n; i++) { if (i < len) { dst[i] = src[off + i]; LD(1); } else dst[i] = z; }
        ST(n); loopc(n); return;
    }
    int c0 = P->c0 % 3;
    for (size_t i0 = 0; i0 < n; i0++) {
        int rot = (int)((c0 * (i0 % 3)) % 3);
        fp u[3], v[3], o[3]; int nz[3];
        for (int t = 0; t < 3; t++) {
            size_t pos = i0 + n * (size_t)t;
            nz[t] = pos < len;
            if (nz[t]) { u[t] = src[off + pos]; LD(1); }
        }
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }
        if (mask == 0) { fp_set_zero(&o[0]); o[1] = o[0]; o[2] = o[0]; }
        else dft3_sel(v, mask, 7, o);
        dst[i0] = o[0]; dst[i0 + n] = o[1]; dst[i0 + 2 * n] = o[2];
        ST(3);
    }
    CTL(4 * ((n + 2) / 3));
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n; int c0 = P->c0 % 3;
    for (size_t i0 = 0; i0 < n; i0++) {
        int rot = (int)((c0 * (i0 % 3)) % 3);
        int need = 0;
        for (int i1 = 0; i1 < 3; i1++) { size_t pos = i0 + n * (size_t)((rot + i1) % 3); if (pos < outlen) need |= 1 << i1; }
        if (!need) continue;
        fp A[3], B[3], v[3];
        for (int k = 0; k < 3; k++) A[k] = buf[i0 + n * (size_t)k];
        LD(3);
        B[0] = A[0]; B[1] = A[2]; B[2] = A[1];
        dft3_sel(B, 7, need, v);
        for (int i1 = 0; i1 < 3; i1++) if ((need >> i1) & 1) { buf[i0 + n * (size_t)((rot + i1) % 3)] = v[i1]; ST(1); }
    }
    CTL(4 * ((n + 2) / 3));
}

void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    stageA_fwd(P, dst, src, off, len);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; }
    }
}
void ntt_inv(const plan_t *P, fp *buf, size_t outlen) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = P->a;
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); }
    }
    stageA_inv(P, buf, outlen);
}
static void conv_core(const plan_t *P, fp *buf, int mode, const fp *C) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = 0;
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; }
        pass_fused(row, P, l0, P->kk[P->npass - 1], mode, C ? C + (size_t)r * P->n : NULL);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); }
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
