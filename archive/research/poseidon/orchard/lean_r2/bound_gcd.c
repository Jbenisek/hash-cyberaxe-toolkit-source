/* Derived cost of stage D (gcd of two polynomials of degree m and m-1 by the half-gcd of hgcd.c) for the normal remainder sequence
 * (every quotient of degree 1).  The tree of recursive calls is enumerated from the recursion of hgcd():
 *   hgcd(n, k, W):   k1 = ceil(k/2);  child 1 = hgcd(2 k1, k1, mat);  apply_inv(R1 of degree k1; operands of degree n, n-1);  one division step;
 *                    child 2 = hgcd(n - k1 - 1, k - k1 - 1, W);  if W: mat_mulQ and mat_mul with matrices of degree <= k1 and <= k - k1 - 1.
 *   k <= hgcd_base_k:  hgcd_base on a pair of degree (n, n-1).
 *   driver:          n -> n - ceil((n+1)/2) - 1 per outer iteration until n <= 2 hgcd_base_k, then classical Euclid.
 * Every node cost is the counted cost of executing the shipped node procedures (apply_inv, mat_mulQ, mat_mul, poly_divrem_naive, hgcd_base)
 * on operands of exactly these degrees; the node results are memoised by (n, k, W).
 * usage: bound_gcd m   -> prints the derived total and the largest work between two budget checks. */
#include "hgcd.c"
#include "pallas_consts.h"
#include "attack.h"

typedef struct { size_t n, k; int w; uint64_t cost; int used; } memo_t;
static memo_t memo[4096];

static fp *rnd_poly(size_t len) { fp *p = NEW_FP(len ? len : 1); for (size_t i = 0; i < len; i++) rnd_fp254(&p[i]); return p; }
static uint64_t tot(void) { return snap_total(snap()); }

static uint64_t node(size_t n, size_t k, int w) {
    for (int i = 0; i < 4096; i++) if (memo[i].used && memo[i].n == n && memo[i].k == k && memo[i].w == w) return memo[i].cost;
    uint64_t c0 = tot(), res = 0;
    if (k <= (size_t)hgcd_base_k) {
        fp *a = rnd_poly(n + 1), *b = rnd_poly(n); mat_t R; fp *c, *d; size_t lc, ld;
        hgcd_base(&R, &c, &lc, &d, &ld, a, n + 1, b, n, k, w, 0);
        xfree(a); xfree(b); xfree(c); xfree(d); if (w) mat_free(&R);
        res = tot() - c0;
    } else {
        size_t k1 = (k * 50 + 99) / 100; if (2 * k1 > n) k1 = n / 2;
        res = node(2 * k1, k1, 1) + 6;                 /* entry check etc. */
        c0 = tot();
        mat_t R1; for (int i = 0; i < 4; i++) { R1.e[i] = rnd_poly(k1 + 1); R1.len[i] = k1 + 1; } R1.h = (int)k1;
        fp *a = rnd_poly(n + 1), *b = rnd_poly(n), *cc, *dd; size_t lcc, ldd;
        apply_inv(&cc, &lcc, &dd, &ldd, &R1, a, n + 1, b, n);
        xfree(a); xfree(b);
        size_t lc2 = n + 1 - k1, ld2 = lc2 - 1;            /* normal case: degree n - k1, then n - k1 - 1 */
        fp *x = rnd_poly(lc2), *y = rnd_poly(ld2), *q = NEW_FP(2), *r = NEW_FP(lc2); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lc2, y, ld2);
        xfree(x); xfree(y); xfree(q); xfree(r); xfree(cc); xfree(dd);
        size_t k3 = k - k1 - 1, n2 = n - k1 - 1;
        if (w) {
            mat_t R2; for (int i = 0; i < 4; i++) { R2.e[i] = rnd_poly(k3 + 1); R2.len[i] = k3 + 1; } R2.h = (int)k3;
            fp *qq = rnd_poly(2); mat_mulQ(&R1, qq, 2); xfree(qq);
            mat_t Rout; mat_mul(&Rout, &R1, &R2);
            mat_free(&R2); mat_free(&Rout);
        }
        mat_free(&R1);
        res += tot() - c0;
        res += node(n2, k3, w);
    }
    for (int i = 0; i < 4096; i++) if (!memo[i].used) { memo[i] = (memo_t){ n, k, w, res, 1 }; break; }
    return res;
}

int main(int argc, char **argv) {
    int r = argc > 1 ? atoi(argv[1]) : 1;
    size_t m = poly_degree_m(r);
    rng_seed(5);
    int amax = 2; while (3 * ((size_t)1 << amax) < 2 * m - 1) amax++;
    ntt_init(amax);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    budget_arm(~0ULL >> 1, "bound");
    uint64_t total = 0; size_t n = m; int outer = 0;
    while (n > 2 * (size_t)hgcd_base_k) {
        size_t k = (n + 1) / 2;
        uint64_t c = node(n, k, 0);
        /* driver: allocation-free division step after hgcd: lc = n - k + 1, ld = lc - 1 */
        uint64_t c0 = tot();
        { size_t lc = n - k + 1, ld = lc - 1; fp *x = rnd_poly(lc), *y = rnd_poly(ld), *q = NEW_FP(2), *rr = NEW_FP(lc); size_t lq, lr;
          poly_divrem_naive(q, &lq, rr, &lr, x, lc, y, ld); xfree(x); xfree(y); xfree(q); xfree(rr);
          n = lc - 2; }
        c += tot() - c0;
        printf("outer %d: hgcd+division cost %llu\n", outer++, (unsigned long long)c);
        total += c;
    }
    { uint64_t c0 = tot(); fp *a = rnd_poly(n + 2), *b = rnd_poly(n + 1), *o = NEW_FP(n + 3); poly_gcd_naive(o, a, n + 2, b, n + 1); total += tot() - c0; }
    /* remaining driver terms: scan of the degree of R - 1 (5 per position), copy/monic of the result (small), initial checks */
    uint64_t extra = 5 * (m + 1) + 100000;
    printf("BOUND_D r=%d m=%zu derived_total=%llu extra=%llu maxgap=%llu\n", r, m, (unsigned long long)total, (unsigned long long)extra, (unsigned long long)budget_maxgap());
    return 0;
}
