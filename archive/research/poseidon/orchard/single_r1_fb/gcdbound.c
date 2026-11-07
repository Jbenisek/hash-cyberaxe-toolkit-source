/* Derived worst-case charge of the gcd (hgcd.c).  The recursion below follows the control structure of hgcd() and poly_gcd_own();
 * every kernel is charged at the cost of the executed kernel on nominal operands of the maximal lengths (all coefficients nonzero, so no
 * top-coefficient scan stops early); the data-dependent scans (trimlen) and the plan_invN cache search are added at their worst case.
 * usage: gcdbound d [d ...]   prints  GCDBOUND d value  (the bound for gcd(a, b), deg a = d, deg b <= d - 1). */
#include "hgcd.c"
#include <time.h>
uint64_t div_cost_bound(size_t la, size_t lb);
#define INVA 330
#define PLAN_ALLOW 460            /* plan_invN: search of the 64-entry cache, 7 operations per entry, at most 448 */

static uint64_t rs_ = 88172645463325252ULL;
static uint64_t rnd64_(void) { rs_ ^= rs_ << 13; rs_ ^= rs_ >> 7; rs_ ^= rs_ << 17; return rs_; }
static fp *rarr(size_t n) { fp *a = NEW_FP(n ? n : 1); for (size_t i = 0; i < n; i++) { uint64_t v[4] = { rnd64_() | 1, rnd64_(), rnd64_(), rnd64_() & 0x3fffffffffffffffULL }; fp_from_limbs(&a[i], v); } return a; }
static uint64_t tot(snap_t s0) { return snap_total(snap_sub(snap(), s0)); }

/* ---- memo */
typedef struct { int kind; uint64_t a, b, c; uint64_t v; } memo_t;
static memo_t memo[200000]; static int nmemo;
static int memo_get(int kind, uint64_t a, uint64_t b, uint64_t c, uint64_t *v) {
    for (int i = 0; i < nmemo; i++) if (memo[i].kind == kind && memo[i].a == a && memo[i].b == b && memo[i].c == c) { *v = memo[i].v; return 1; }
    return 0;
}
static void memo_put(int kind, uint64_t a, uint64_t b, uint64_t c, uint64_t v) { memo[nmemo].kind = kind; memo[nmemo].a = a; memo[nmemo].b = b; memo[nmemo].c = c; memo[nmemo++].v = v; }

/* ---- kernels at nominal operands */
static uint64_t K_apply(size_t la, size_t K) {              /* apply_inv with a of la coefficients, b of la - 1, all matrix entries of K + 1 coefficients */
    uint64_t v; if (memo_get(1, la, K, 0, &v)) return v;
    mat_t R; for (int i = 0; i < 4; i++) { R.e[i] = rarr(K + 1); R.len[i] = K + 1; } R.h = 1;
    fp *a = rarr(la), *b = rarr(la - 1), *c, *d; size_t lc, ld;
    snap_t s0 = snap(); apply_inv(&c, &lc, &d, &ld, &R, a, la, b, la - 1, 0); v = tot(s0);
    v += 2 * 10 * (la + 1) + PLAN_ALLOW;                    /* the two trimlen scans at their worst case (10 per entry) */
    xfree(c); xfree(d); xfree(a); xfree(b); mat_free(&R);
    memo_put(1, la, K, 0, v); return v;
}
static uint64_t K_matmul(size_t kA, size_t kB) {            /* mat_mul of matrices with entries of kA + 1 and kB + 1 coefficients */
    uint64_t v; if (memo_get(2, kA, kB, 0, &v)) return v;
    mat_t A, B, O; for (int i = 0; i < 4; i++) { A.e[i] = rarr(kA + 1); A.len[i] = kA + 1; B.e[i] = rarr(kB + 1); B.len[i] = kB + 1; } A.h = 1; B.h = 1;
    snap_t s0 = snap(); mat_mul(&O, &A, &B); v = tot(s0);
    size_t Lmax = kA + kB + 1;
    v += 4 * 10 * (Lmax + 1) + 8 * PLAN_ALLOW;
    mat_free(&A); mat_free(&B); mat_free(&O);
    memo_put(2, kA, kB, 0, v); return v;
}
static uint64_t K_mulQ(size_t sd, size_t dq) {              /* mat_mulQ: R entries of sd + 1 coefficients, q of dq + 1 */
    uint64_t v; if (memo_get(3, sd, dq, 0, &v)) return v;
    mat_t R; for (int i = 0; i < 4; i++) { R.e[i] = rarr(sd + 1); R.len[i] = sd + 1; } R.h = 1;
    fp *q = rarr(dq + 1);
    snap_t s0 = snap(); mat_mulQ(&R, q, dq + 1); v = tot(s0);
    v += 2 * 10 * (sd + dq + 2) + 4 * PLAN_ALLOW;
    mat_free(&R); xfree(q);
    memo_put(3, sd, dq, 0, v); return v;
}
static uint64_t K_mulQ_max(size_t k) {                      /* sd + dq <= k: maximum over the splits (all of them for small k, a grid otherwise) */
    uint64_t v; if (memo_get(4, k, 0, 0, &v)) return v;
    uint64_t best = 0;
    for (size_t dq = 0; dq <= k; dq++) { if (k > 60 && dq % ((k + 59) / 60) && dq != k && dq != 0) continue; uint64_t c = K_mulQ(k - dq, dq); if (c > best) best = c; }
    memo_put(4, k, 0, 0, best); return best;
}
static uint64_t K_divfast(size_t n, size_t kq) {            /* divrem_fast with a of n + 1 coefficients, quotient of kq coefficients */
    uint64_t v; if (memo_get(5, n, kq, 0, &v)) return v;
    size_t la = n + 1, lb = la - kq + 1;
    fp *a = rarr(la), *b = rarr(lb), *q = NEW_FP(kq), *r = NEW_FP(lb); size_t lq, lr;
    snap_t s0 = snap(); divrem_fast(q, &lq, r, &lr, a, la, b, lb); v = tot(s0);
    uint64_t lg = 0; while (((uint64_t)1 << lg) < kq) lg++;
    v += 10 * (lb + 1) + (2 * lg + 6) * PLAN_ALLOW;
    xfree(a); xfree(b); xfree(q); xfree(r);
    memo_put(5, n, kq, 0, v); return v;
}
/* division of a polynomial with at most n + 1 coefficients, quotient length at most kq: worst over the two branches of divrem_any */
static uint64_t B_div(size_t n, size_t kq) {
    uint64_t v; if (memo_get(6, n, kq, 0, &v)) return v;
    uint64_t best = 0;
    size_t kn = kq < DIVFAST_MIN ? kq : DIVFAST_MIN;          /* naive branch with quotient length <= 64 */
    if (kn >= 1) { uint64_t c = div_cost_bound(n + 1, n + 2 - kn); if (c > best) best = c; }
    if (kq >= 1) {                                             /* naive branch with divisor length <= 64 */
        size_t la2 = kq + DIVFAST_MIN - 1 < n + 1 ? kq + DIVFAST_MIN - 1 : n + 1;
        uint64_t c2 = div_cost_bound(la2, DIVFAST_MIN < la2 ? DIVFAST_MIN : la2); if (c2 > best) best = c2;
    }
    if (kq > DIVFAST_MIN) {                                    /* fast branch: a grid of quotient lengths up to kq, and kq itself */
        size_t step = kq / 24 + 1;
        for (size_t t = DIVFAST_MIN + 1; t <= kq; t += step) { uint64_t c = K_divfast(n, t); if (c > best) best = c; }
        uint64_t c = K_divfast(n, kq); if (c > best) best = c;
    }
    best += 40;                                               /* divrem_any test and call */
    memo_put(6, n, kq, 0, best); return best;
}

/* ---- hgcd node */
static uint64_t B_base(size_t n, size_t k, int wm) {
    uint64_t steps = k, quo = 2 * (uint64_t)k;                /* steps <= k; the sum of (dq + 1) over the steps <= 2k */
    uint64_t v = quo * (14 + 12 * (uint64_t)n) + steps * (7 * ((uint64_t)n + 1) + 2 + INVA + 2 + INV_CTL + 11 * ((uint64_t)n + 1)) + steps * 30;
    if (wm) v += steps * K_mulQ_max(k);
    v += 14 * ((uint64_t)n + 1) + 8 + 20 + 100;               /* dupv of the inputs, identity matrix, loop exit */
    return v;
}
static uint64_t B_hgcd(size_t n, size_t k, int wm) {
    uint64_t v; if (memo_get(7, n, k, wm, &v)) return v;
    if (k <= (size_t)hgcd_base_k) { v = B_base(n, k, wm); memo_put(7, n, k, wm, v); return v; }
    size_t k1 = (k * (size_t)hgcd_k1_pct + 99) / 100;
    if (2 * k1 > n) k1 = n / 2;
    uint64_t c = 28 * ((uint64_t)n + 1) + 200;                 /* call overhead, copies on the early exits */
    c += B_hgcd(2 * k1, k1, 1);                                /* first call: top parts, matrix wanted */
    uint64_t ap = K_apply(n + 1, k1); uint64_t dp = 14 * ((uint64_t)n + 1) + 8; c += ap > dp ? ap : dp;
    size_t kq = (k < n ? k : n) + 1;                           /* quotient length <= k2 + 1 <= k + 1 */
    c += B_div(n, kq);
    if (k > k1 + 1) c += B_hgcd(n > k1 + 1 ? n - k1 - 1 : 1, k - k1 - 1, wm);   /* second call: parameter <= k - k1 - 1 and degree <= n - k1 - 1 (sumdeg + dq > k1) */
    if (wm) { c += K_mulQ_max(k) + K_matmul(k / 2, k - k / 2) + 80; }
    memo_put(7, n, k, wm, c); return c;
}

/* ---- gcd */
static uint64_t B_gcd(size_t n) {                              /* deg a = n, deg b <= n - 1 */
    uint64_t v; if (memo_get(8, n, 0, 0, &v)) return v;
    uint64_t c = div_cost_bound(n + 1, n + 1) + 100;           /* the equal-length step (not needed when deg b < deg a, harmless) */
    size_t m = n;
    while (1) {
        c += 20;
        if (m <= 2 * (size_t)hgcd_base_k) {                    /* classical Euclid to the end: at most m steps, sum of (dq + 1) <= 2 m */
            c += 2 * (uint64_t)m * (14 + 12 * (uint64_t)m) + (uint64_t)m * (7 * ((uint64_t)m + 1) + 2 + INVA + 2 + INV_CTL + 11 * ((uint64_t)m + 1)) + (uint64_t)m * 20;
            break;
        }
        c += B_hgcd(m, (m + 1) / 2, 0);
        c += B_div(m, m + 1) + 40;                             /* the division of c by d (quotient up to m) */
        m = m / 2;                                             /* next degree <= floor(m/2) - 1 */
    }
    c += INVA + 2 + INV_CTL + 8 + 10 * ((uint64_t)n + 1) + 100; /* monic scaling */
    memo_put(8, n, 0, 0, c); return c;
}
int main(int argc, char **argv) {
    ntt_init(15);
    if (argc > 1 && argv[1][0] == 'H') {              /* emit gcd_bounds.h for the level schedule 39062, 19531, ... (> 76) */
        size_t lv[16]; int nl = 0;
        for (size_t d = 39062; d > 76; d /= 2) lv[nl++] = d;
        printf("/* generated by gcdbound H: worst-case charges of the fast gcd (deg a = d, deg b < d) and of the division of a degree-d polynomial by a factor of degree > d/2 */\n");
        printf("#define NLEVELB %d\nstruct lvl_ { size_t d; unsigned long long gcd, div; };\nstatic const struct lvl_ LEVELB[NLEVELB] = {\n", nl);
        for (int i = 0; i < nl; i++) {
            size_t d = lv[i];
            uint64_t g = B_gcd(d), dv = B_div(d, d / 2 + 1);
            /* monotonicity checks on intermediate degrees */
            size_t xs[6] = { d - 1, d * 9 / 10, d * 3 / 4, d * 5 / 8, d * 9 / 16, d / 2 + 1 };
            for (int t = 0; t < 6; t++) { size_t x = xs[t]; if (x <= 152 || getenv("NOMONO")) continue; uint64_t gx = B_gcd(x), dx = B_div(x, x / 2 + 1);
                fprintf(stderr, "MONO d=%zu x=%zu gcd ratio %.5f div ratio %.5f\n", d, x, (double)gx / g, (double)dx / dv); }
            printf("    { %zu, %lluULL, %lluULL },\n", d, (unsigned long long)g, (unsigned long long)dv);
        }
        printf("};\n");
        return 0;
    }
    for (int i = 1; i < argc; i++) {
        size_t d = strtoull(argv[i], 0, 10);
        uint64_t b = B_gcd(d);
        printf("GCDBOUND %zu %llu\n", d, (unsigned long long)b); fflush(stdout);
    }
    return 0;
}
