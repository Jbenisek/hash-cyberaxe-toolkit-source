/* Memory of the gcd stage of the root isolation at the top degree: poly_gcd_keep(G borrowed, S - 1 given away) on random operands of degrees d and d - 1.
 * usage: test_keep d */
#include "common.h"
#include "hgcd.h"
static uint64_t rs = 99172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    size_t d = argc > 1 ? strtoul(argv[1], 0, 10) : 39062;
    ntt_init(15);
    fp *G = NEW_FP(d + 1), *S = NEW_FP(d);
    for (size_t i = 0; i <= d; i++) rnd_fp(&G[i]);
    for (size_t i = 0; i < d; i++) rnd_fp(&S[i]);
    size_t base = mem_cur; mem_reset_peak();
    snap_t s0 = snap();
    size_t lg; fp *A = poly_gcd_keep(&lg, G, d + 1, S, d);
    uint64_t ch = snap_total(snap_sub(snap(), s0));
    printf("poly_gcd_keep d=%zu: gcd degree %zu charged %llu, peak above the live inputs %zu, absolute peak %zu bytes (inputs %zu)\n", d, lg - 1, (unsigned long long)ch, mem_peak - base, mem_peak, base);
    xfree(A); xfree(G);
    return 0;
}
