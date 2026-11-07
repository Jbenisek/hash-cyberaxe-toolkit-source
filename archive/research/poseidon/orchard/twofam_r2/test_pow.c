/* Test of powx_lean on the binomial modulus g = x^m - c, for which x^E mod g = c^(E div m) x^(E mod m) is known.
 * usage: test_pow m E     (E a 64-bit exponent) */
#include "attack.h"
int main(int argc, char **argv) {
    ntt_init(18);
    rng_seed(11);
    size_t m = strtoull(argv[1], 0, 0);
    uint64_t E0 = strtoull(argv[2], 0, 0);
    fp c; rnd_fp254(&c);
    fp *g = NEW_FP(m + 1), *R = NEW_FP(m);
    for (size_t i = 0; i < m; i++) fp_set_zero(&g[i]);
    fp_neg(&g[0], &c); fp_set_one(&g[m]);
    uint64_t E[4] = { E0, 0, 0, 0 };
    powx_lean(R, g, m, E, 1);
    uint64_t q = E0 / m, rem = E0 % m;
    uint64_t qe[4] = { q, 0, 0, 0 };
    fp cq; fp_pow(&cq, &c, qe);
    size_t bad = 0, first = (size_t)-1;
    for (size_t i = 0; i < m; i++) {
        fp want; if (i == rem) want = cq; else fp_set_zero(&want);
        if (!fp_eq(&R[i], &want)) { if (!bad) first = i; bad++; }
    }
    printf("m=%zu E=%llu: %zu coefficients differ (first %zd) -> %s\n", m, (unsigned long long)E0, bad, (ssize_t)first, bad ? "FAIL" : "OK");
    return bad != 0;
}
