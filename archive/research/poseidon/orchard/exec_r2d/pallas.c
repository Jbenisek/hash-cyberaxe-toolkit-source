#include "pallas.h"
#include "pallas_consts.h"
#include <string.h>
#include <stdio.h>

typedef unsigned __int128 u128;
fp_counters fp_cnt;
void fp_counters_reset(void) { memset(&fp_cnt, 0, sizeof fp_cnt); }
uint64_t fp_prim_total(void) { return fp_cnt.add + fp_cnt.sub + fp_cnt.mul + fp_cnt.sqr; }

/* ---------- raw limb helpers (every counted operation below increments its counter, then calls these) ---------- */
static int geq_p(const uint64_t a[4]) {
    for (int i = 3; i >= 0; i--) { if (a[i] > PALLAS_P[i]) return 1; if (a[i] < PALLAS_P[i]) return 0; }
    return 1;
}
static void sub_p(uint64_t a[4]) {
    uint64_t b = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a[i] - PALLAS_P[i] - b; a[i] = (uint64_t)d; b = (uint64_t)(d >> 64) & 1; }
}
static void mont_mul_raw(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) {
    uint64_t t[6] = {0, 0, 0, 0, 0, 0};
    for (int i = 0; i < 4; i++) {
        uint64_t carry = 0;
        for (int j = 0; j < 4; j++) { u128 s = (u128)a[i] * b[j] + t[j] + carry; t[j] = (uint64_t)s; carry = (uint64_t)(s >> 64); }
        u128 s = (u128)t[4] + carry; t[4] = (uint64_t)s; t[5] = (uint64_t)(s >> 64);
        uint64_t m = t[0] * PALLAS_INV;
        s = (u128)m * PALLAS_P[0] + t[0]; carry = (uint64_t)(s >> 64);
        for (int j = 1; j < 4; j++) { s = (u128)m * PALLAS_P[j] + t[j] + carry; t[j - 1] = (uint64_t)s; carry = (uint64_t)(s >> 64); }
        s = (u128)t[4] + carry; t[3] = (uint64_t)s; carry = (uint64_t)(s >> 64);
        t[4] = t[5] + carry;
    }
    /* t < 2p here; t[4] is 0 because p < 2^255 */
    r[0] = t[0]; r[1] = t[1]; r[2] = t[2]; r[3] = t[3];
    if (t[4] || geq_p(r)) sub_p(r);
}

/* ---------- conversions ---------- */
int fp_limbs_canonical(const uint64_t v[4]) { return !geq_p(v); }
void fp_from_limbs(fp *r, const uint64_t v[4]) { fp_cnt.mul++; /* a conversion is one Montgomery multiplication: charged as one field multiplication */ uint64_t t[4]; mont_mul_raw(t, v, PALLAS_R2); memcpy(r->l, t, 32); }
void fp_to_limbs(uint64_t v[4], const fp *a) { fp_cnt.mul++; /* charged as one field multiplication */ static const uint64_t one[4] = {1, 0, 0, 0}; uint64_t t[4]; mont_mul_raw(t, a->l, one); memcpy(v, t, 32); }
void fp_from_u64(fp *r, uint64_t x) { uint64_t v[4] = {x, 0, 0, 0}; fp_from_limbs(r, v); }
int fp_from_hex(fp *r, const char *hex) {
    uint64_t v[4] = {0, 0, 0, 0};
    for (int i = 0; i < 64; i++) {
        char c = hex[i]; int d;
        if (c >= '0' && c <= '9') d = c - '0'; else if (c >= 'a' && c <= 'f') d = c - 'a' + 10; else if (c >= 'A' && c <= 'F') d = c - 'A' + 10; else return -1;
        int pos = 63 - i;                       /* nibble index from least significant */
        v[pos / 16] |= (uint64_t)d << (4 * (pos % 16));
    }
    if (!fp_limbs_canonical(v)) return -1;
    fp_from_limbs(r, v); return 0;
}
void fp_to_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    snprintf(out, 65, "%016llx%016llx%016llx%016llx", (unsigned long long)v[3], (unsigned long long)v[2], (unsigned long long)v[1], (unsigned long long)v[0]);
}

/* ---------- counted field ops ---------- */
void fp_add(fp *r, const fp *a, const fp *b) {
    fp_cnt.add++;
    uint64_t t[4], c = 0;
    for (int i = 0; i < 4; i++) { u128 s = (u128)a->l[i] + b->l[i] + c; t[i] = (uint64_t)s; c = (uint64_t)(s >> 64); }
    if (c || geq_p(t)) sub_p(t);
    memcpy(r->l, t, 32);
}
void fp_dbl(fp *r, const fp *a) { fp_add(r, a, a); }
void fp_sub(fp *r, const fp *a, const fp *b) {
    fp_cnt.sub++;
    uint64_t t[4], br = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a->l[i] - b->l[i] - br; t[i] = (uint64_t)d; br = (uint64_t)(d >> 64) & 1; }
    if (br) { uint64_t c = 0; for (int i = 0; i < 4; i++) { u128 s = (u128)t[i] + PALLAS_P[i] + c; t[i] = (uint64_t)s; c = (uint64_t)(s >> 64); } }
    memcpy(r->l, t, 32);
}
void fp_neg(fp *r, const fp *a) { fp z; fp_set_zero(&z); fp_sub(r, &z, a); }
void fp_mul(fp *r, const fp *a, const fp *b) { fp_cnt.mul++; uint64_t t[4]; mont_mul_raw(t, a->l, b->l); memcpy(r->l, t, 32); }
void fp_sqr(fp *r, const fp *a) { fp_cnt.sqr++; uint64_t t[4]; mont_mul_raw(t, a->l, a->l); memcpy(r->l, t, 32); }
void fp_pow5(fp *r, const fp *a) { fp t; fp_sqr(&t, a); fp_sqr(&t, &t); fp_mul(r, &t, a); }

void fp_set_zero(fp *r) { memset(r, 0, sizeof *r); }
void fp_set_one(fp *r) { memcpy(r->l, PALLAS_ONE_M, 32); }
int fp_eq(const fp *a, const fp *b) { return memcmp(a->l, b->l, 32) == 0; }
int fp_is_zero(const fp *a) { return (a->l[0] | a->l[1] | a->l[2] | a->l[3]) == 0; }

void fp_pow(fp *r, const fp *a, const uint64_t e[4]) {
    fp_cnt.pow_calls++;
    int top = -1;
    for (int i = 255; i >= 0; i--) if ((e[i / 64] >> (i % 64)) & 1) { top = i; break; }
    if (top < 0) { fp_set_one(r); return; }
    fp base = *a, acc = *a;                    /* leading 1 bit: acc = a, no operation */
    for (int i = top - 1; i >= 0; i--) {
        fp_sqr(&acc, &acc);
        if ((e[i / 64] >> (i % 64)) & 1) fp_mul(&acc, &acc, &base);
    }
    *r = acc;
}
void fp_inv(fp *r, const fp *a) { fp_cnt.inv_calls++; fp_pow(r, a, PALLAS_PM2); }
int fp_legendre(const fp *a) {
    if (fp_is_zero(a)) return 0;
    fp t, one; fp_pow(&t, a, PALLAS_PM1H); fp_set_one(&one);
    return fp_eq(&t, &one) ? 1 : -1;
}
/* Tonelli-Shanks with p-1 = 2^32 * q. Invariant: x^2 = a*t, z has order 2^m, t has order dividing 2^(m-1) iff a is a square. */
int fp_sqrt(fp *r, const fp *a) {
    fp_cnt.sqrt_calls++;
    if (fp_is_zero(a)) { fp_set_zero(r); return 1; }
    fp one; fp_set_one(&one);
    fp z, t, x, b;
    memcpy(z.l, PALLAS_Z_M, 32);                /* z = 5^q, order 2^32 */
    fp_pow(&t, a, PALLAS_Q);                    /* t = a^q   */
    fp_pow(&x, a, PALLAS_QP1H);                 /* x = a^((q+1)/2) */
    unsigned m = 32;
    while (!fp_eq(&t, &one)) {
        unsigned i = 0; fp u = t;
        while (!fp_eq(&u, &one)) { fp_sqr(&u, &u); i++; if (i >= m) return 0; }   /* i == m: t has order 2^m => non-residue */
        b = z;
        for (unsigned k = 0; k + i + 1 < m; k++) fp_sqr(&b, &b);                  /* b = z^(2^(m-i-1)) */
        fp_mul(&x, &x, &b);
        fp_sqr(&z, &b);
        fp_mul(&t, &t, &z);
        m = i;
    }
    *r = x; return 1;
}

/* ---------- Poseidon ---------- */
int poseidon_C(int r) { return 216 + 21 * r; }
static void mds_mul(fp s[3]) {
    fp o[3], t;
    for (int i = 0; i < 3; i++) {
        fp_mul(&o[i], &POSEIDON_MDS_M[i][0], &s[0]);
        fp_mul(&t, &POSEIDON_MDS_M[i][1], &s[1]); fp_add(&o[i], &o[i], &t);
        fp_mul(&t, &POSEIDON_MDS_M[i][2], &s[2]); fp_add(&o[i], &o[i], &t);
    }
    s[0] = o[0]; s[1] = o[1]; s[2] = o[2];
}
static void round_fn(fp s[3], int idx, int full) {
    for (int i = 0; i < 3; i++) fp_add(&s[i], &s[i], &POSEIDON_RC_M[idx][i]);
    if (full) for (int i = 0; i < 3; i++) fp_pow5(&s[i], &s[i]); else fp_pow5(&s[0], &s[0]);
    mds_mul(s);
}
void poseidon_perm_r(fp s[3], int r) {
    for (int i = 0; i < 4; i++) round_fn(s, i, 1);
    for (int i = 0; i < r; i++) round_fn(s, 4 + i, 0);
    for (int i = 60; i < 64; i++) round_fn(s, i, 1);
}
void poseidon_hash_r_fp(fp *out, const fp *nk, const fp *rho, int r) {
    fp s[3]; s[0] = *nk; s[1] = *rho; memcpy(s[2].l, POSEIDON_CAP_M, 32);
    poseidon_perm_r(s, r);
    *out = s[0];
}
int poseidon_hash_r(const uint64_t nk[4], const uint64_t rho[4], int r, uint64_t out[4]) {
    if (r < 0 || r > 56 || !fp_limbs_canonical(nk) || !fp_limbs_canonical(rho)) return -1;
    fp a, b, o; fp_from_limbs(&a, nk); fp_from_limbs(&b, rho);
    poseidon_hash_r_fp(&o, &a, &b, r); fp_to_limbs(out, &o); return 0;
}
