#include "common.h"
#include "pallas_consts.h"
#include <time.h>
static uint64_t rs = 88172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    size_t m = argc > 1 ? strtoul(argv[1], 0, 10) : 39062;
    int amax = argc > 2 ? atoi(argv[2]) : 17;
    int rows3 = argc > 3 ? atoi(argv[3]) : 0;
    ntt_init(amax);
    fp *g = NEW_FP(m + 1), *out = NEW_FP(m);
    for (size_t i = 0; i < m; i++) rnd_fp(&g[i]);
    fp_set_one(&g[m]);
    snap_t s0 = snap();
    clock_t t0 = clock();
    powx_mod(out, g, m, PALLAS_PM1H, rows3, 0);
    snap_t s1 = snap_sub(snap(), s0);
    printf("m=%zu time=%.1fs mul=%llu sqr=%llu add=%llu sub=%llu ld=%llu st=%llu ctl=%llu total=%llu arith=%llu peak=%zu\n", m,
        (double)(clock()-t0)/CLOCKS_PER_SEC, (unsigned long long)s1.mul, (unsigned long long)s1.sqr, (unsigned long long)s1.add,
        (unsigned long long)s1.sub, (unsigned long long)s1.ld, (unsigned long long)s1.st, (unsigned long long)s1.ctl,
        (unsigned long long)snap_total(s1), (unsigned long long)snap_arith(s1), mem_peak);
    return 0;
}
