#include "common.h"
#include "pallas_consts.h"
#include <time.h>
static uint64_t rs = 88172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    size_t m = argc > 1 ? atoi(argv[1]) : 39062;
    ntt_init(15);
    fp *g = NEW_FP(m + 1), *o = NEW_FP(m);
    for (size_t i = 0; i < m; i++) rnd_fp(&g[i]);
    fp_set_one(&g[m]);
    snap_t s0 = snap(); mem_reset_peak();
    clock_t t0 = clock();
    powx_mod(o, g, m, PALLAS_PM1H, 0, 0);
    snap_t s1 = snap_sub(snap(), s0);
    printf("m=%zu time %.1fs add %llu sub %llu mul %llu sqr %llu ld %llu st %llu ctl %llu  arith %llu total %llu peakmem %zu\n", m, (double)(clock()-t0)/CLOCKS_PER_SEC,
      (unsigned long long)s1.add,(unsigned long long)s1.sub,(unsigned long long)s1.mul,(unsigned long long)s1.sqr,(unsigned long long)s1.ld,(unsigned long long)s1.st,(unsigned long long)s1.ctl,
      (unsigned long long)snap_arith(s1),(unsigned long long)snap_total(s1), mem_peak);
    return 0;
}
