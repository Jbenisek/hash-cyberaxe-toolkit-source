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

/* random: the coin tape (line.c), read at run time from standard input by single.c; no generator, no seed */
#ifndef MAXTR
#define MAXTR 2                                            /* K: the number of centres tried (algebraic paper 4.1); compile-time define */
#endif
#ifndef DMAX
#define DMAX 16
#endif
#ifndef ZCAP
#define ZCAP 64
#endif
#ifndef COIN_WORDS
#define COIN_WORDS (MAXTR * (1 + ZCAP) * 5)                /* at most one centre draw and ZCAP shift draws per trial, five words per draw */
#endif
#define COIN_BYTES ((size_t)COIN_WORDS * 8)
extern uint64_t coin_tape[COIN_WORDS]; extern size_t coin_pos;
int coin_read(void *buf, size_t n);                        /* nolibc.c: one read(0, buf, n); 1 iff all n bytes arrived */
void rnd_fp320(fp *a);                                     /* coin draw (algebraic paper 4.1.1): five tape words = a 320-bit integer, reduced mod p; charged as executed */

/* build the monic odd-part polynomial g (deg m) for centre c; g has room m+1. Counted. */
void build_g(fp *g, const line_t *L, const fp *c, int r);

/* map a pair of roots back to inputs: W -> (nk, rho) */
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);

/* gcd and root finding */
size_t euclid_gcd(fp *out, const fp *a, size_t da, const fp *b, size_t db, size_t *dout); /* classical; out receives gcd (monic) */

/* minor-stage memory charge: 2 loads + 1 store + 1 control op per primitive executed since s0 */
void bound_mem_since(snap_t s0);

/* split.c: root isolation (charged as executed) */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db);       /* classical Euclid; monic gcd; returns degree */
int  split_find_root_capped(fp *root, fp *G, size_t d);                       /* algebraic paper 4.1.2: at most Z rounds, 1 <= d <= DMAX */
fp  *taylor_shift(fp *G, size_t d, const fp *a);                              /* G(Z + a), frees G */
void pow_half(fp *S, const fp *G, size_t d);                                  /* Z^((p-1)/2) mod G */
extern uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;
#endif
