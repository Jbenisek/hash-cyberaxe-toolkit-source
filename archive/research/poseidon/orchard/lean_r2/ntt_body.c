/* ---------- butterflies: straight-line register blocks (ntt_kern.h) ---------- */
#include "ntt_kern.h"
/* Charging convention of this file: LD/ST = one 256-bit load/store; CTL(n) = n executed integer / comparison / branch / shift / address
 * operations, each counted as 1.  Every statement that executes such operations carries its CTL charge next to it. */

static void kf_run(int k, int z, fp *x, const fp *tw, size_t b, const size_t *to, const int *sj, int sh) {
    switch (k) {
    case 1: if (z) kf1z(x, tw, b, to, sj, sh); else kf1(x, tw, b, to, sj, sh); break;
    case 2: if (z) kf2z(x, tw, b, to, sj, sh); else kf2(x, tw, b, to, sj, sh); break;
    case 3: if (z) kf3z(x, tw, b, to, sj, sh); else kf3(x, tw, b, to, sj, sh); break;
    default: if (z) kf4z(x, tw, b, to, sj, sh); else kf4(x, tw, b, to, sj, sh); break;
    }
}
static void ki_run(int k, int z, fp *x, const fp *tw, size_t b, const size_t *to, const int *sj, int sh, size_t nh) {
    switch (k) {
    case 1: if (z) ki1z(x, tw, b, to, sj, sh, nh); else ki1(x, tw, b, to, sj, sh, nh); break;
    case 2: if (z) ki2z(x, tw, b, to, sj, sh, nh); else ki2(x, tw, b, to, sj, sh, nh); break;
    case 3: if (z) ki3z(x, tw, b, to, sj, sh, nh); else ki3(x, tw, b, to, sj, sh, nh); break;
    default: if (z) ki4z(x, tw, b, to, sj, sh, nh); else ki4(x, tw, b, to, sj, sh, nh); break;
    }
}
/* per-pass tables: sj[j] = l0 + j, to[T] = (tp * s) << (l0 + j) for the T-th twiddle (layer j, position tp) of the block */
static void pass_tables(int k, int l0, size_t s, size_t *to, int *sj) {
    int T = 0;
    for (int j = 0; j < k; j++) {
        sj[j] = l0 + j;
        size_t half = (size_t)1 << (k - 1 - j);
        for (size_t tp = 0; tp < half; tp++) to[T++] = (tp * s) << (l0 + j);
    }
    CTL(5 * (uint64_t)T + 4 * (uint64_t)k + 4);   /* per entry: mul, shift, add, store address, loop step; per layer: add, shift, loop */
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
    CTL(8);                                            /* s, G, Gs, ngrp: shift, shift, mul, shift; call, return */
    size_t to[15]; int sj[4]; pass_tables(k, l0, s, to, sj);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        CTL(5);                                        /* group loop + base address */
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            CTL(6);                                    /* block loop (3), base (1), b == 0 test (2) */
            load_block(x, base, s, G);
            kf_run(k, b == 0, x, tw, b, to, sj, P->shift);
            store_block(base, x, s, G);
        }
    }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0, nh = P->n >> 1;
    CTL(9);
    size_t to[15]; int sj[4]; pass_tables(k, l0, s, to, sj);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        CTL(5);
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            CTL(6);
            load_block(x, base, s, G);
            ki_run(k, b == 0, x, tw, b, to, sj, P->shift, nh);
            store_block(base, x, s, G);
        }
    }
}
enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };
/* last forward pass + pointwise + first inverse pass (s == 1): one register block, constant displacements, b == 0 always */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t G = (size_t)1 << k, ngrp = P->n >> k, nh = P->n >> 1;
    CTL(9);
    size_t to[15]; int sj[4]; pass_tables(k, l0, 1, to, sj);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * G;
        CTL(4);                                        /* loop (3), base (1) */
        for (size_t t = 0; t < G; t++) x[t] = base[t];
        LD(G);
        kf_run(k, 1, x, tw, 0, to, sj, P->shift);
        if (mode == M_SQ) { for (size_t t = 0; t < G; t++) fp_sqr(&x[t], &x[t]); }
        else { const fp *cb = C + grp * G; CTL(2); for (size_t t = 0; t < G; t++) fp_mul(&x[t], &x[t], &cb[t]); LD(G); }
        ki_run(k, 1, x, tw, 0, to, sj, P->shift, nh);
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
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(6);
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        if (dst == src && off == 0) { for (size_t i = len; i < n; i++) dst[i] = z; if (n > len) { ST(n - len); loopc(n - len); } return; }
        for (size_t i = 0; i < n; i++) { if (i < len) { dst[i] = src[off + i]; LD(1); } else dst[i] = z; }
        ST(n); loopc(n); CTL(2 * n); return;
    }
    int c0 = P->c0 % 3, rot = 0;
    for (size_t i0 = 0; i0 < n; i0++) {
        fp u[3], v[3], o[3]; int nz[3];
        CTL(3 + 4);                                     /* loop; rot update: add, compare, branch, subtract */
        rot = rot + c0; if (rot >= 3) rot -= 3;
        for (int t = 0; t < 3; t++) {                   /* per t: position, compare, branch, address */
            size_t pos = i0 + n * (size_t)t;
            nz[t] = pos < len;
            CTL(4);
            if (nz[t]) { u[t] = src[off + pos]; LD(1); }
        }
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; CTL(6); if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }   /* index (add, mod), nz test (2), or (2) */
        CTL(2);
        if (mask == 0) { fp_set_zero(&o[0]); o[1] = o[0]; o[2] = o[0]; }
        else dft3_sel(v, mask, 7, o);
        dst[i0] = o[0]; dst[i0 + n] = o[1]; dst[i0 + 2 * n] = o[2];
        ST(3); CTL(2);
    }
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n; int c0 = P->c0 % 3, rot = 0;
    CTL(6);
    for (size_t i0 = 0; i0 < n; i0++) {
        CTL(3 + 4);
        rot = rot + c0; if (rot >= 3) rot -= 3;
        int need = 0;
        for (int i1 = 0; i1 < 3; i1++) { size_t pos = i0 + n * (size_t)((rot + i1) % 3); CTL(8); if (pos < outlen) need |= 1 << i1; }   /* index, mul, add, compare, or */
        CTL(2);
        if (!need) continue;
        fp A[3], B[3], v[3];
        for (int k = 0; k < 3; k++) A[k] = buf[i0 + n * (size_t)k];
        LD(3); CTL(2);
        B[0] = A[0]; B[1] = A[2]; B[2] = A[1];
        dft3_sel(B, 7, need, v);
        for (int i1 = 0; i1 < 3; i1++) { CTL(8); if ((need >> i1) & 1) { buf[i0 + n * (size_t)((rot + i1) % 3)] = v[i1]; ST(1); } }
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
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N; int c0 = P->c0 % 3, rot = 0;
    CTL(8);
    for (size_t i0 = 0; i0 < n; i0++) {
        fp u[3], v[3], o[3]; int nz[3];
        CTL(3 + 4);
        rot = rot + c0; if (rot >= 3) rot -= 3;
        for (int t = 0; t < 3; t++) {
            size_t pos = i0 + n * (size_t)t, idx = (pos + N - boff) % N;
            int any = 0; fp acc;
            CTL(7);                                     /* pos (mul, add), idx (add, sub, mod), any, loop-entry compare */
            for (; idx < lenB; idx += N) {              /* fold modulo x^N - 1 when lenB > N */
                CTL(5);                                 /* branch, increment, first test (2), compare */
                if (!any) { acc = B[idx]; any = 1; } else fp_add(&acc, &acc, &B[idx]);
                LD(1);
            }
            CTL(2);                                     /* nz assignment, if (any) */
            nz[t] = any; if (any) u[t] = acc;
        }
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; CTL(6); if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }
        CTL(2);
        if (mask == 0) fp_set_zero(&o[r]);
        else dft3_sel(v, mask, 1 << r, o);
        tmp[i0] = o[r]; ST(1); CTL(1);
    }
}
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
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    stageA_inv(P, out, outlen);
}
