/* Half-GCD / fast Euclid over the Pallas base field (all ops counted through pallas.c and common.h). */
#ifndef HGCD_H
#define HGCD_H
#include "common.h"

/* 2x2 polynomial matrix R = Q_1 ... Q_h, Q_i = [[q_i,1],[1,0]];  e[0]=r11 e[1]=r12 e[2]=r21 e[3]=r22; h counts the factors */
typedef struct { fp *e[4]; size_t len[4]; int h; } mat_t;

/* polynomial a (la coefficients, trimmed), b (lb coefficients, trimmed, lb < la or lb == 0)
 * -> fresh arrays *c (lc), *d (ld) = consecutive Euclid remainders (r_h, r_{h+1}) with deg r_h >= n-k > deg r_{h+1}
 * (n = la-1), (a,b)^T = R (c,d)^T.  want_mat: also return R. */
void hgcd(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own);
void mat_free(mat_t *R);

/* gcd of a (la coefs) and b (lb coefs, lb <= la), monic result in out (room la); returns its number of coefficients (0 if both zero) */
fp *poly_gcd_own(size_t *lg, fp *x, size_t lx, fp *y, size_t ly); /* inputs are xalloc'ed and given away; returns the monic gcd (xalloc'ed) */
extern int hgcd_k1_pct;
size_t poly_gcd_fast(fp *out, const fp *a, size_t la, const fp *b, size_t lb);
/* plain Euclid (reference, counted) */
size_t poly_gcd_naive(fp *out, const fp *a, size_t la, const fp *b, size_t lb);
/* a = q*b + r (naive); q has la-lb+1 coefficients (if la>=lb), r has lb-1 slots; returns trimmed lr; *lq set */
void poly_divrem_naive(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb);
extern int hgcd_base_k;
extern uint64_t hgcd_stat_calls, hgcd_stat_base_steps, hgcd_stat_bigdiv;
void divrem_any_pub(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb);
fp *poly_gcd_keep(size_t *lg, const fp *x, size_t lx, fp *y, size_t ly); /* x borrowed, y given away; monic gcd as a fresh array */
#endif
