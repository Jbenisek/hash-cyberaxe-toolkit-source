/* Orchard Poseidon (r partial rounds) two-family collision: line model, digest polynomial, helpers. */
#ifndef ATTACK_H
#define ATTACK_H
#include "common.h"

typedef struct {
    int j;                 /* coordinate of the round-1 S-box input that stays constant on this family */
    fp UQ, VQ;             /* point Q of the family: (U,V) at tau = 0 */
    fp a, b;               /* direction: (U,V) = Q + tau (a,b) */
    fp d[3];               /* round-1 S-box input = d_i tau (i != j), kappa (i == j) */
    fp kappa;
    fp alpha[3], beta[3];  /* round-2 S-box input = alpha + beta W,  W = tau^5 */
    fp e5inv_unused;
} line_t;

extern const uint64_t E5INV[4];                            /* 5^{-1} mod (p-1) */
void line_setup(line_t *L, int j);                         /* counted */
void tail_eval(fp *out, const line_t *L, const fp *W, int r);   /* H on the family at W: counted, no memory-op charge */
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);   /* W -> canonical input (nk, rho) */
void rng_seed(uint64_t s);
void rnd_fp254(fp *a);                                     /* 254-bit random word: 1 random word + 2 ctl */
void rnd_u256(uint64_t w[4]);                              /* 256-bit random word: 1 random word */
void bound_mem_since(snap_t s0);                           /* 2 loads + 1 store + 6 control ops per primitive since s0 */

/* split.c */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db);       /* classical Euclid; monic gcd; returns degree */
uint64_t gcd_cost_bound(size_t da, size_t db);
uint64_t div_cost_bound(size_t la, size_t lb);                                /* derived worst-case charge of gcd_cl */
fp  *deflate(fp *G, size_t d, const fp *r);                                   /* G / (Z - r), frees G; exits if r is not a root */
int  split_find_root(fp *root, fp *G, size_t d);                              /* one root of a monic product of distinct linear factors */
size_t split_tries(size_t d);
fp  *taylor_shift(fp *G, size_t d, const fp *a);                              /* G(Z + a), frees G */
void pow_half(fp *S, const fp *G, size_t d);                                  /* Z^((p-1)/2) mod G */
extern uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;
#endif
