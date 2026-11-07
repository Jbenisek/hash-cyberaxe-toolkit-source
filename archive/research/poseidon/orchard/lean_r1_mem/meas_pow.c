#include "common.h"
static uint64_t rs = 88172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
int main(void) {
    ntt_init(15); size_t m = 39062;
    fp *g = NEW_FP(m + 1), *F = NEW_FP(m);
    for (size_t i = 0; i < m; i++) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(&g[i], v); }
    fp_set_one(&g[m]);
    uint64_t E[4] = { 0x123456789abcdefULL, 0, 0, 0 };
    mem_reset_peak();
    powx_lean(F, g, m, E, 2);
    printf("heap_peak=%zu\n", mem_peak);
    return 0;
}
