#include "common.h"
#include "pallas_consts.h"
#include <time.h>
static uint64_t rs = 1234567891234567ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    ntt_init(15);
    int ok = 1;
    size_t ms[] = { 5, 40, 200, 601, 3000, 0 };
    if (argc > 1) { ms[0] = strtoul(argv[1], 0, 10); ms[1] = 0; }
    for (int t = 0; ms[t]; t++) {
        size_t m = ms[t];
        fp *g = NEW_FP(m + 1), *o1 = NEW_FP(m), *o2 = NEW_FP(m);
        for (size_t i = 0; i < m; i++) rnd_fp(&g[i]);
        fp_set_one(&g[m]);
        uint64_t E[4] = { rnd64(), rnd64() >> 3, 0, 0 };
        if (argc > 1) { E[0]=PALLAS_PM1H[0];E[1]=PALLAS_PM1H[1];E[2]=PALLAS_PM1H[2];E[3]=PALLAS_PM1H[3]; }
        snap_t s0 = snap(); mem_reset_peak(); size_t base = mem_cur; clock_t c0 = clock();
        powx_lean(o1, g, m, E, argc > 2 ? 2 : 1);
        snap_t d1 = snap_sub(snap(), s0); size_t pk = mem_peak - base; double sec = (double)(clock()-c0)/CLOCKS_PER_SEC;
        s0 = snap(); c0 = clock();
        powx_mod(o2, g, m, E, 1, 1);
        snap_t d2 = snap_sub(snap(), s0); double sec2 = (double)(clock()-c0)/CLOCKS_PER_SEC;
        int good = 1; for (size_t i = 0; i < m; i++) if (!fp_eq(&o1[i], &o2[i])) { good = 0; break; }
        printf("lean m=%zu: %s   lean arith=%llu total=%llu peak(extra)=%zu %.1fs | cached arith=%llu total=%llu %.1fs\n", m, good ? "ok" : "FAIL",
            (unsigned long long)snap_arith(d1), (unsigned long long)snap_total(d1), pk, sec,
            (unsigned long long)snap_arith(d2), (unsigned long long)snap_total(d2), sec2);
        ok &= good;
        xfree(g); xfree(o1); xfree(o2);
    }
    printf(ok ? "LEAN TESTS PASSED\n" : "LEAN TESTS FAILED\n");
    return !ok;
}
