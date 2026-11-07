/* Orchard Poseidon (r partial rounds) collision: line model, digest polynomial, odd-part polynomial g. */
#ifndef ATTACK_H
#define ATTACK_H
#include "common.h"

typedef struct {
    int j;                 /* coordinate of the round-1 S-box input that stays constant */
    fp UQ, VQ;             /* point Q on the plane: U,V at tau = 0 */
    fp a, b;               /* direction (U,V) = Q + tau (a,b) */
    fp d[3];               /* S-box input at round 1 = d_i tau (i != j), kappa (i == j) */
    fp kappa;
    fp alpha[3], beta[3];  /* round-2 S-box input = alpha + beta W,  W = tau^5 */
    fp e5inv_unused;
} line_t;

/* exponent e = 5^{-1} mod (p-1), 254 bits */
extern const uint64_t E5INV[4];

void line_setup(line_t *L, int j);                         /* counted */
void tail_eval(fp *out, const line_t *L, const fp *W, int r);   /* F(W): counted, no memory-op charge (caller bounds it) */
size_t poly_degree_m(int r);                               /* m = (5^(6+r) - 1)/2 */

/* random */
void rng_seed(uint64_t s);
void rnd_fp254(fp *a);                                     /* uniform on [0,2^254), canonical; charged as 1 random word + 2 ctl */

/* build the monic odd-part polynomial g (deg m) for centre c; g has room m+1. Counted. */
void build_g(fp *g, const line_t *L, const fp *c, int r);

/* map a pair of roots back to inputs: W -> (nk, rho) */
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);

/* gcd and root finding */
size_t euclid_gcd(fp *out, const fp *a, size_t da, const fp *b, size_t db, size_t *dout); /* classical; out receives gcd (monic) */
int  find_root(fp *root, const fp *G, size_t d);           /* G monic, product of distinct linear factors; returns 1 on success */

/* minor-stage memory charge: 2 loads + 1 store + 1 control op per primitive executed since s0 */
void bound_mem_since(snap_t s0);

/* split.c: root isolation (charged as executed) */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db);       /* classical Euclid; monic gcd; returns degree */
int  split_find_root(fp *root, fp *G, size_t d);                              /* one root of a monic product of distinct linear factors */
size_t split_tries(size_t d);
fp  *taylor_shift(fp *G, size_t d, const fp *a);                              /* G(Z + a), frees G */
void pow_half(fp *S, const fp *G, size_t d);                                  /* Z^((p-1)/2) mod G */
extern uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;
#endif
