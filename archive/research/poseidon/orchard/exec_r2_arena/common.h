/* Shared definitions for the Orchard odd-part root finder.  All field arithmetic goes through pallas.c
 * (counted: add, sub, mul, sqr).  Additional charged primitives are counted here: 256-bit loads (ld), stores (st),
 * loop-control / index operations (ctl) and random words (rnd).  The charging rules are in proof.md section 4.2. */
#ifndef COMMON_H
#define COMMON_H
#include "pallas.h"
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct { uint64_t ld, st, ctl, rnd, perm; } xcnt_t;   /* perm: reduced permutation evaluations charged as C(r) primitive operations each */
extern xcnt_t X;
/* Counting rule: every executed operation of the code below is charged where it is written.
 *  - LD(n)/ST(n): n element loads/stores; each is charged together with one address-formation operation (counted as control).
 *  - a loop that runs n iterations: 3n+2 control operations (per iteration the index update, the bound comparison and the
 *    conditional branch; on exit one more comparison and branch).  loopc(n) charges exactly this.
 *  - every other executed shift, mask, add, multiply, modulo, comparison or branch of index and control code: 1 each via CTL(). */
#define LD(n)  do { X.ld  += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
#define ST(n)  do { X.st  += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
#define CTL(n) (X.ctl += (uint64_t)(n))
static inline void loopc(size_t nel) { X.ctl += 3 * (uint64_t)nel + 2; }
/* A loop with its body unrolled 8 times (straight-line, no branch inside the body): one operation for the bound n & ~7, then per pass of the
 * unrolled body the index update, the comparison and the branch (3), on exit one comparison and branch (2); the 0..7 remaining elements run in a
 * plain loop (3 per iteration, 2 on exit).  The statements of the body carry their own load / store charges. */
#define FOR8(I, N, ...) do { size_t n_ = (size_t)(N), n8_ = n_ & ~(size_t)7, i_ = 0; CTL(1);                          for (; i_ < n8_; i_ += 8) {                                                                                         { size_t I = i_;     __VA_ARGS__; } { size_t I = i_ + 1; __VA_ARGS__; } { size_t I = i_ + 2; __VA_ARGS__; } { size_t I = i_ + 3; __VA_ARGS__; }         { size_t I = i_ + 4; __VA_ARGS__; } { size_t I = i_ + 5; __VA_ARGS__; } { size_t I = i_ + 6; __VA_ARGS__; } { size_t I = i_ + 7; __VA_ARGS__; }         CTL(3); }                                                                                                   CTL(2);                                                                                                         for (; i_ < n_; i_++) { size_t I = i_; __VA_ARGS__; CTL(3); }                                                  CTL(2); } while (0)
#define INV_CTL 2310     /* control of fp_inv outside the per-operation stages: 253 iterations x 9 (index update, compare, branch, word and bit selection, bit test) + 3 x 8 for the search of the top bit */

typedef struct { uint64_t add, sub, mul, sqr, ld, st, ctl, rnd, perm; } snap_t;
snap_t snap(void);
snap_t snap_sub(snap_t a, snap_t b);
uint64_t snap_arith(snap_t s);           /* add+sub+mul+sqr */
uint64_t snap_total(snap_t s);           /* everything charged */
void snap_restore(snap_t s);             /* restore counters (used to exclude test/debug-only work) */

/* ---- memory accounting (every buffer goes through xalloc) */
void *xalloc(size_t bytes);
void  xfree(void *p);
void  xshrink(void *p, size_t bytes);   /* shrink a live block in place */
extern size_t mem_cur, mem_peak;        /* mem_peak: peak allocator footprint (see common.c) */
extern size_t mem_live, mem_peak_live, mem_peak_pay;   /* live allocations now; live allocations and live payload bytes at the footprint peak */
void  mem_reset_peak(void);

/* ---- field helpers */
#define NEW_FP(n) ((fp *)xalloc((size_t)(n) * sizeof(fp)))
void  xmove_down(void **pp);             /* relocate a live block to the lowest gap below it (counted copy) */
void *xalloc_t(size_t bytes);          /* temporary buffer, placed from the top of the arena */
#ifndef ROLE
#define ROLE 0
#endif
#if ROLE
#define NEW_FPT(n) ((fp *)xalloc_t((size_t)(n) * sizeof(fp)))
#else
#define NEW_FPT(n) NEW_FP(n)
#endif

/* ---- NTT engine (ntt.c) */
typedef struct {
    int rows;          /* 1: plain 2^a transform; 3: Good-Thomas radix-3 x 2^a */
    int a;             /* log2 of row length */
    size_t n, N;       /* row length, total length */
    int shift;         /* amax - a (twiddle table stride shift) */
    int npass, kk[8];  /* layers per pass; last pass is the one fused with pointwise ops */
    int c0;            /* radix-3 rotation constant (rows==3) */
} plan_t;

void   ntt_init(int amax);               /* roots of unity + twiddle table (counted) */
void   ntt_free(void);
void   ntt_shrink(int amax);             /* keep only the table of 2^amax (amax < current): in-place compaction (counted) */
int    ntt_amax(void);
plan_t make_plan(int rows, int a);
plan_t plan_for_len(size_t len, int allow3); /* smallest {2^a, 3*2^a} >= len */
size_t ntt_table_bytes(void);

/* forward transform: src[off .. off+len) (zero beyond) -> dst (layout order); dst may equal src when off==0 */
void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len);
/* inverse (unnormalised: result = N * coefficients), in place; only positions < outlen are produced */
void ntt_inv(const plan_t *P, fp *buf, size_t outlen);
/* fused convolution kernels (unnormalised cyclic convolution of length N, result = N * (x*y mod x^N-1)) */
void conv_sq (const plan_t *P, fp *buf, size_t len, size_t outlen);
void conv_mulc(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, const fp *C, size_t outlen);
/* point of layout position (row, pos) i.e. exponent k -> index in dst */
size_t layout_index(const plan_t *P, size_t k);
void   plan_theta(const plan_t *P, fp *theta);      /* theta such that the transform evaluates at theta^k (counted-free, uses table) */

extern fp ntt_w3, ntt_invN_cache;
/* lean variant: second operand B (compact, lenB coefficients, cyclic offset boff) transformed row by row into tmp (P->n entries) */
void   conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                     const fp *B, size_t lenB, size_t boff, size_t outlen);
void   conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                    const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen);
void   ntt_fwd_shifted(const plan_t *P, fp *dst, const fp *B, size_t lenB, size_t boff);   /* cached spectrum of B placed at cyclic offset boff */
typedef struct { int nh, ns; const fp *H[2]; size_t lH[2]; const fp *S[2]; size_t lS[2]; signed char o[2][2]; signed char sg[2][2]; } bilin_grp_t;
void   conv_bilin_otf(const plan_t *P, int nout, fp *const *out, const size_t *outlen, int ng, const bilin_grp_t *G, fp *tH0, fp *tH1, fp *tS, int *eps);   /* shared-transform sums of products, row by row (rows==3 plans) */
plan_t plan3_for_len(size_t len);                    /* smallest 3*2^a >= len */

/* ---- polynomial tools (poly.c) */
typedef struct { fp *c; size_t len; } pv;   /* view: len coefficients, len==0 -> zero polynomial; c[len-1] != 0 when normalised */
void poly_mul(fp *r, const fp *a, size_t la, const fp *b, size_t lb);  /* r has la+lb-1 entries, counted */
void poly_mul_naive(fp *r, const fp *a, size_t la, const fp *b, size_t lb);
void plan_invN(const plan_t *P, fp *out);              /* 1/N as a field element (cached, counted once) */

/* ---- modular exponentiation x^E mod g (lean.c) */
void powx_lean(fp *F, const fp *g, size_t m, const uint64_t E[4], int quiet);


#endif
