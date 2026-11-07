#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <stddef.h>
/* stand-in for the counters so that common.h's udivmod can be tested alone */
typedef struct { uint64_t ctl; } xc_t; static xc_t X;
static inline size_t udivmod(size_t a, size_t b, size_t *rem) {
    size_t nb = 0, q = 0, r = 0, set = 0;
    for (size_t t = a; t; t >>= 1) nb++;
    for (size_t i = nb; i-- > 0;) { r = (r << 1) | ((a >> i) & 1); q <<= 1; if (r >= b) { r -= b; q |= 1; set++; } }
    *rem = r;
    X.ctl += 4 * (uint64_t)nb + 2 + 10 * (uint64_t)nb + 2 * (uint64_t)set + 4;
    return q;
}
int main(void) {
    uint64_t s = 88172645463325252ULL; long bad = 0;
    for (long i = 0; i < 3000000; i++) {
        s ^= s << 13; s ^= s >> 7; s ^= s << 17;
        size_t a = s >> (i % 60), b = (i % 7 == 0) ? 3 : ((s >> 17) % 1000000) + 1;
        size_t r, q = udivmod(a, b, &r);
        if (q != a / b || r != a % b) bad++;
    }
    for (size_t d = 2; d <= 300; d++) { size_t r; size_t v = d > 40 ? 1 : udivmod(40 + d - 2, d - 1, &r); size_t w = d > 40 ? 1 : (40 + d - 2) / (d - 1); if (v != w) bad++; }
    for (size_t a = 0; a < 5000; a++) { size_t r; if (udivmod(a, 3, &r) != a / 3 || r != a % 3) bad++; }
    /* hgcd k1 */
    for (size_t k = 1; k < 100000; k++) if (((k + 1) >> 1) != (k * 50 + 99) / 100) bad++;
    /* region index: lo + n t + N - boff < 2N, conditional subtraction == mod N */
    for (int a = 2; a <= 18; a++) { size_t n = (size_t)1 << a, N = 3 * n; size_t bofs[3] = { 0, N - 1, N - (N / 2 - 5) };
        for (int bi = 0; bi < 3; bi++) for (size_t lo = 0; lo < n; lo += (n / 61 + 1)) for (int t = 0; t < 3; t++) {
            size_t v = lo + n * t + N - bofs[bi]; size_t w = v >= N ? v - N : v; if (w != v % N) bad++; } }
    printf("unit tests bad=%ld ctl=%llu\n", bad, (unsigned long long)X.ctl);
    return bad != 0;
}
