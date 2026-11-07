/* Line model of the Orchard hash with r partial rounds, the digest polynomial F(W) and the map back from W to canonical inputs.  All field arithmetic goes through pallas.c (counted). */
#include "attack.h"
#include "pallas_consts.h"

/* e = 5^{-1} mod (p-1) = (4(p-1)+1)/5; 254 bits, Hamming weight 125 */
const uint64_t E5INV[4] = { 0xe0f0f3f0cccccccdULL, 0x4e9ee0c9a10a60e2ULL, 0x3333333333333333ULL, 0x3333333333333333ULL };

static uint64_t rs_state = 0x9e3779b97f4a7c15ULL;
void rng_seed(uint64_t s) { rs_state = s ? s : 0x9e3779b97f4a7c15ULL; }
/* xorshift64: three statements  x ^= x << a;  each is a shift, an exclusive or and an assignment of a register (3 operations); the word is then returned and stored into the
 * array of limbs (2 operations: the return value move and the store).  One call: 3 * 3 + 2 = 11 operations, charged by the caller below. */
static uint64_t rnd64(void) { rs_state ^= rs_state << 13; rs_state ^= rs_state >> 7; rs_state ^= rs_state << 17; return rs_state; }
void rnd_fp254(fp *a) {
    uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL };
    fp_from_limbs(a, v);                     /* one Montgomery multiplication, charged by pallas.c */
    X.ctl += 4 * 11 + 1 + 2;                 /* four xorshift calls (11 each), the 254-bit mask (one AND), the call of fp_from_limbs with the address of v (2) */
}

void bound_mem_since(snap_t s0) {
    snap_t d = snap_sub(snap(), s0);
    uint64_t ops = snap_arith(d);
    X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops;      /* per field operation: two operand loads, one result store, six control/index operations (loop: 3, index selections, bit tests) */
}

static void mds_apply(fp s[3]) {
    fp o[3], t;
    for (int i = 0; i < 3; i++) {
        fp_mul(&o[i], &POSEIDON_MDS_M[i][0], &s[0]);
        fp_mul(&t, &POSEIDON_MDS_M[i][1], &s[1]); fp_add(&o[i], &o[i], &t);
        fp_mul(&t, &POSEIDON_MDS_M[i][2], &s[2]); fp_add(&o[i], &o[i], &t);
    }
    s[0] = o[0]; s[1] = o[1]; s[2] = o[2];
}

/* Round 0 maps (nk, rho, 2^65) to M (U, V, K), U = (nk + c0_0)^5, V = (rho + c0_1)^5, K = (2^65 + c0_2)^5.
 * Round-1 S-box input x = M (U, V, K) + RC1 = M[:,0] U + M[:,1] V + base,  base_k = M[k][2] K + RC1[k].
 * For the constant coordinate j (others I = {i1, i2}): Q solves x_i1 = x_i2 = 0; direction (a, b) = (M[j][1], -M[j][0])
 * gives d_j = 0.  On (U, V) = Q + tau (a, b): x_i = d_i tau (i in I), x_j = kappa.  Round-1 S-box output = v0 + W v1 with
 * W = tau^5, v0 = kappa^5 e_j, v1 = sum_{i in I} d_i^5 e_i.  After the round-1 MDS: A + W B with A = M v0, B = M v1;
 * the round-2 S-box input (constants of round 2 added) is alpha + beta W, alpha = A + RC2, beta = B. */
void line_setup(line_t *L, int j) {
    const fp (*M)[3] = POSEIDON_MDS_M;
    L->j = j;
    int i1 = j == 0 ? 1 : 0, i2 = j == 2 ? 1 : 2;
    fp cap, K, base[3], t, u;
    memcpy(cap.l, POSEIDON_CAP_M, 32);
    fp_add(&t, &cap, &POSEIDON_RC_M[0][2]);
    fp_pow5(&K, &t);
    for (int k = 0; k < 3; k++) { fp_mul(&t, &M[k][2], &K); fp_add(&base[k], &t, &POSEIDON_RC_M[1][k]); }
    /* 2x2 system  M[i1][0] U + M[i1][1] V = -base[i1],  M[i2][0] U + M[i2][1] V = -base[i2] */
    fp det, idet, e1, e2, n1, n2;
    fp_mul(&t, &M[i1][0], &M[i2][1]); fp_mul(&u, &M[i1][1], &M[i2][0]); fp_sub(&det, &t, &u);
    fp_inv(&idet, &det);
    fp_neg(&n1, &base[i1]); fp_neg(&n2, &base[i2]);
    /* U = (n1 M[i2][1] - M[i1][1] n2)/det ; V = (M[i1][0] n2 - n1 M[i2][0])/det */
    fp_mul(&t, &n1, &M[i2][1]); fp_mul(&u, &M[i1][1], &n2); fp_sub(&e1, &t, &u); fp_mul(&L->UQ, &e1, &idet);
    fp_mul(&t, &M[i1][0], &n2); fp_mul(&u, &n1, &M[i2][0]); fp_sub(&e2, &t, &u); fp_mul(&L->VQ, &e2, &idet);
    L->a = M[j][1]; fp_neg(&L->b, &M[j][0]);
    for (int k = 0; k < 3; k++) { fp_mul(&t, &M[k][0], &L->a); fp_mul(&u, &M[k][1], &L->b); fp_add(&L->d[k], &t, &u); }
    fp_mul(&t, &M[j][0], &L->UQ); fp_mul(&u, &M[j][1], &L->VQ); fp_add(&t, &t, &u); fp_add(&L->kappa, &t, &base[j]);
    fp v0j, v1[3];
    fp_pow5(&v0j, &L->kappa);
    for (int k = 0; k < 3; k++) { if (k == j) fp_set_zero(&v1[k]); else fp_pow5(&v1[k], &L->d[k]); }
    for (int k = 0; k < 3; k++) {
        fp_mul(&t, &M[k][j], &v0j); fp_add(&L->alpha[k], &t, &POSEIDON_RC_M[2][k]);
        fp acc; fp_set_zero(&acc); int first = 1;
        for (int i = 0; i < 3; i++) if (i != j) {
            fp_mul(&t, &M[k][i], &v1[i]);
            if (first) { acc = t; first = 0; } else fp_add(&acc, &acc, &t);
        }
        L->beta[k] = acc;
    }
}

/* F(W): rounds 2 (S-box on alpha + beta W), MDS, 3, r partial rounds, 60..63, digest = row 0 of the last MDS */
void tail_eval(fp *out, const line_t *L, const fp *W, int r) {
    fp x[3], t;
    for (int k = 0; k < 3; k++) { fp_mul(&t, &L->beta[k], W); fp_add(&x[k], &L->alpha[k], &t); }
    for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
    mds_apply(x);
    for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], &POSEIDON_RC_M[3][k]);
    for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
    mds_apply(x);
    for (int i = 0; i < r; i++) {
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], &POSEIDON_RC_M[4 + i][k]);
        fp_pow5(&x[0], &x[0]);
        mds_apply(x);
    }
    for (int idx = 60; idx < 64; idx++) {
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], &POSEIDON_RC_M[idx][k]);
        for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
        if (idx < 63) mds_apply(x);
        else {
            fp o;
            fp_mul(&o, &POSEIDON_MDS_M[0][0], &x[0]);
            fp_mul(&t, &POSEIDON_MDS_M[0][1], &x[1]); fp_add(&o, &o, &t);
            fp_mul(&t, &POSEIDON_MDS_M[0][2], &x[2]); fp_add(&o, &o, &t);
            *out = o;
        }
    }
}

/* Plain line route: q(X) = (F(X) - F(c)) / (X - c), made monic.  F has degree D = 5^(6+r) on the line.  F is interpolated from its values at the H-th
 * roots of unity (H = 3*2^a >= D+1; one inverse transform gives H*f_k), F(c) is one more evaluation, and the division by (X - c) is synthetic division
 * (one multiplication and one addition per coefficient); the monic scaling is one multiplication per coefficient.  q has degree D - 1 and room D slots. */
size_t poly_degree_q(int r) { size_t D = 1; for (int i = 0; i < 6 + r; i++) D = (D << 2) + D; CTL(1 + (6 + r) * (3 + 2) + 2 + 1); return D - 1; }   /* D = 5 D by a shift and an addition; loop 3 per iteration (and 2 for the shift and the addition), 2 on exit; the initial assignment, the subtraction and the return */
void build_q(fp *q, const line_t *L, const fp *c, int r) {
    size_t M = poly_degree_q(r), D = M + 1;
    plan_t P = plan_for_len(D + 1, 1);
    size_t H = P.N;
    fp *buf = NEW_FP(H);
    fp theta, s, one;
    fp_set_one(&one);
    plan_theta(&P, &theta);
    s = one;
    size_t row = 0; int rows3 = P.rows == 3;     /* row = k mod 3, kept by a counter */
    for (size_t k = 0; k < H; k++) {
        fp F1;
        snap_t e0 = snap();
        tail_eval(&F1, L, &s, r);
        snap_restore(e0);
        X.perm += (uint64_t)poseidon_C(r);          /* the reduced permutation F(W): one target-compression unit, C(r) primitive operations */
        buf[layout_index_r(&P, row, k)] = F1;
        if (rows3) { row++; if (row == 3) row = 0; }
        fp_mul(&s, &s, &theta);
        CTL(2 + 4 + 4);            /* the call of the evaluation, the call of layout_index_r (arguments), and the update of the counter row: test of rows3, increment, comparison and branch, assignment */
    }
    ST(H); loopc(H);
    ntt_inv(&P, buf, D + 1);                 /* buf[k] = H * f_k */
    fp Fc, Hf, t;
    { snap_t e0 = snap(); tail_eval(&Fc, L, c, r); snap_restore(e0); X.perm += (uint64_t)poseidon_C(r); }   /* F(c), one more evaluation */
    { uint64_t hv[4] = { H, 0, 0, 0 }; fp_from_limbs(&Hf, hv); }
    fp_mul(&t, &Fc, &Hf); fp_sub(&buf[0], &buf[0], &t); LD(1); ST(1);        /* H*(F(c)) removed from H*f_0 */
    CTL(5); if (fp_is_zero(&buf[D])) { fprintf(stderr, "leading coefficient of F vanishes\n"); exit(7); }
    fp il, acc;
    fp_inv(&il, &buf[D]); CTL(INV_CTL);
    acc = buf[D]; LD(1);
    fp_set_one(&q[M]); ST(1);
    for (size_t k = D - 1; k >= 1; k--) {            /* acc = b_k + c * acc  (b_k = H f_k, acc = H q_{k-1} before the scaling);  q_{k-1} = acc / b_D */
        fp_mul(&t, &acc, c); fp_add(&acc, &buf[k], &t);
        fp_mul(&q[k - 1], &acc, &il);
    }
    LD(D - 1); ST(D - 1); loopc(D - 1);
    xfree(buf);
}

void map_back(fp *nk, fp *rho, const line_t *L, const fp *W) {
    fp tau, tt, U, V, t;
    fp_pow(&tau, W, E5INV);
    fp_mul(&t, &tau, &L->a); fp_add(&U, &L->UQ, &t);
    fp_mul(&t, &tau, &L->b); fp_add(&V, &L->VQ, &t);
    fp_pow(&tt, &U, E5INV); fp_sub(nk, &tt, &POSEIDON_RC_M[0][0]);
    fp_pow(&tt, &V, E5INV); fp_sub(rho, &tt, &POSEIDON_RC_M[0][1]);
}
