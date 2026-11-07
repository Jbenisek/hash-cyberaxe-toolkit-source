#include "common.h"
static uint64_t rs = 99172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(void) {
    ntt_init(17);
    for (int a = 13; a <= 17; a++) {
        for (int rows = 1; rows <= 3; rows += 2) {
            plan_t P = make_plan(rows, a), Q = P;
            Q.big = 0; Q.npass = (a + 3) / 4; { int rem = a; for (int i = Q.npass - 1; i >= 0; i--) { int k = rem >= 4 ? 4 : rem; Q.kk[i] = k; rem -= k; } }
            size_t len = P.N - 5;
            fp *src = NEW_FP(len), *d1 = NEW_FP(P.N), *d2 = NEW_FP(P.N), *e1 = NEW_FP(P.N), *e2 = NEW_FP(P.N);
            for (size_t i = 0; i < len; i++) rnd_fp(&src[i]);
            ntt_fwd(&P, d1, src, 0, len); ntt_fwd(&Q, d2, src, 0, len);
            int bad = 0; for (size_t i = 0; i < P.N; i++) if (!fp_eq(&d1[i], &d2[i])) bad++;
            conv_sq(&P, d1, len, P.N); 
            ntt_fwd(&Q, e2, src, 0, len); conv_sq(&Q, e2, len, P.N);
            int bad2 = 0; for (size_t i = 0; i < P.N; i++) if (!fp_eq(&d1[i], &e2[i])) bad2++;
            fp *c = NEW_FP(P.N); for (size_t i = 0; i < P.N; i++) rnd_fp(&c[i]);
            memcpy(e1, src, len * sizeof(fp)); 
            conv_mulc(&P, d1, src, 0, len, c, P.N); conv_mulc(&Q, e2, src, 0, len, c, P.N);
            int bad3 = 0; for (size_t i = 0; i < P.N; i++) if (!fp_eq(&d1[i], &e2[i])) bad3++;
            fprintf(stderr, "a=%d rows=%d big=%d kk=%d,%d fwd_bad=%d sq_bad=%d mulc_bad=%d\n", a, rows, P.big, P.kk[0], P.kk[1], bad, bad2, bad3);
        }
    }
    return 0;
}
