#include "hgcd.h"
#include "pallas_consts.h"
static uint64_t rs = 0x9e3779b97f4a7c15ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
static void rnd_poly(fp *c, size_t len) { for (size_t i = 0; i < len; i++) rnd_fp(&c[i]); }
static int polyeq(const fp *a, size_t la, const fp *b, size_t lb) {
    if (la != lb) return 0; for (size_t i = 0; i < la; i++) if (!fp_eq(&a[i], &b[i])) return 0; return 1; }
static size_t trim(const fp *c, size_t l) { while (l && fp_is_zero(&c[l-1])) l--; return l; }
/* build a poly with prescribed quotient degrees: product of Q matrices -> (a,b) = Q1..Qh (r_h, r_{h+1}) */
int main(int argc, char **argv) {
    ntt_init(13);
    int ok = 1;
    int bases[] = { 2, 5, 24 };
    size_t sizes[] = { 10, 30, 64, 100, 257, 600, 1500, 3000 };
    for (int bi = 0; bi < 3; bi++) {
        hgcd_base_k = bases[bi];
        for (int si = 0; si < 8; si++) for (int mode = 0; mode < 4; mode++) {
            size_t n = sizes[si];
            size_t la = n + 1, lb;
            fp *a = NEW_FP(la + 5), *b = NEW_FP(la + 5);
            rnd_poly(a, la); size_t common = 0;
            if (mode == 0) { lb = n; rnd_poly(b, lb); }             /* generic */
            else if (mode == 1) { lb = n / 2 + 1; rnd_poly(b, lb); } /* big first quotient */
            else if (mode == 2) {                                    /* common factor */
                common = n / 3 + 1;
                fp *f = NEW_FP(common + 1), *u = NEW_FP(la), *v = NEW_FP(la);
                rnd_poly(f, common + 1);
                size_t lu = la - common, lv = n - common;
                rnd_poly(u, lu); rnd_poly(v, lv);
                poly_mul(a, f, common + 1, u, lu); la = common + 1 + lu - 1;
                poly_mul(b, f, common + 1, v, lv); lb = common + 1 + lv - 1;
                xfree(f); xfree(u); xfree(v);
            } else {                                                 /* b = random, a = b*q + small: deg a - deg b large */
                lb = n / 5 + 2; rnd_poly(b, lb);
            }
            la = trim(a, la); lb = trim(b, lb);
            if (lb >= la) continue;
            /* gcd */
            fp *g1 = NEW_FP(la), *g2 = NEW_FP(la);
            size_t l1 = poly_gcd_naive(g1, a, la, b, lb);
            size_t l2 = poly_gcd_fast(g2, a, la, b, lb);
            int g_ok = polyeq(g1, l1, g2, l2);
            /* hgcd versus the naive remainder sequence */
            size_t nn = la - 1, k = (nn + 1) / 2;
            mat_t R; fp *c, *d; size_t lc, ld;
            hgcd(&R, &c, &lc, &d, &ld, a, la, b, lb, k, 1);
            /* naive sequence */
            fp *x = NEW_FP(la), *y = NEW_FP(la); memcpy(x, a, la * sizeof(fp)); memcpy(y, b, lb * sizeof(fp)); size_t lx = la, ly = lb, sum = 0;
            while (ly) { size_t dq = lx - ly; if (dq > k - sum) break;
                fp *q = NEW_FP(dq + 1), *r = NEW_FP(lx); size_t lq, lr; poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
                sum += dq; memcpy(x, y, ly * sizeof(fp)); lx = ly; memcpy(y, r, (lr ? lr : 1) * sizeof(fp)); ly = lr; xfree(q); xfree(r); }
            int h_ok = polyeq(c, lc, x, lx) && polyeq(d, ld, y, ly);
            /* R (c,d) = (a,b) */
            int m_ok = 1;
            {
                fp *t1 = NEW_FP(la + lc + 2), *t2 = NEW_FP(la + lc + 2);
                size_t lt[2];
                for (int row = 0; row < 2; row++) {
                    size_t lo = la + 5; fp *o = calloc(lo, sizeof(fp));
                    for (int t = 0; t < 2; t++) {
                        const fp *e = R.e[2 * row + t]; size_t le = R.len[2 * row + t];
                        const fp *v = t == 0 ? c : d; size_t lv = t == 0 ? lc : ld;
                        if (!le || !lv) continue;
                        fp *p = NEW_FP(le + lv); poly_mul_naive(p, e, le, v, lv);
                        for (size_t u = 0; u < le + lv - 1; u++) fp_add(&o[u], &o[u], &p[u]);
                        xfree(p);
                    }
                    size_t lo2 = trim(o, lo);
                    m_ok &= row == 0 ? polyeq(o, lo2, a, la) : polyeq(o, lo2, b, lb);
                    free(o);
                }
                xfree(t1); xfree(t2);
            }
            printf("base=%d n=%zu mode=%d lb=%zu: gcd %s hgcd %s matrix %s (h=%d, ld=%zu)\n", bases[bi], n, mode, lb, g_ok ? "ok" : "FAIL", h_ok ? "ok" : "FAIL", m_ok ? "ok" : "FAIL", R.h, ld);
            ok &= g_ok && h_ok && m_ok;
            mat_free(&R); xfree(c); xfree(d); xfree(a); xfree(b); xfree(g1); xfree(g2); xfree(x); xfree(y);
        }
    }
    printf(ok ? "HGCD TESTS PASSED\n" : "HGCD TESTS FAILED\n");
    return !ok;
}
