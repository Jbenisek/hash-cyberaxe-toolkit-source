/* Short known-answer checks for exec_r6fast (test only; not part of the counted program).
 *   bench_chk 1 T m e1 e2 e3   powx_lean on a random monic g of degree m with E = 2^e1 + 2^e2 + 2^e3 + 1 (a few squaring steps after the window);
 *                              prints a checksum of F = x^E mod g (canonical limbs), the operation counters and the thread control.
 *   bench_chk 2 T m d          L (degree d, random monic), U, V random of degree m - d (U monic): A = L U, B = L V (poly_mul); G = gcd(A, B) by poly_gcd_own;
 *                              prints deg G, a checksum of G and of L (G must equal L) and the counters.
 * The same g / L / U / V for every build (xorshift seed 7).  Build: test/build_chk.sh. */
#include "../attack.h"
#include "../hgcd.h"
#include "../par.h"
#include "../outbuf.h"
#ifndef AMAX
#define AMAX 21
#endif
static unsigned long long ck(const fp *a, size_t n) {
    unsigned long long h = 1469598103934665603ULL;
    for (size_t i = 0; i < n; i++) { uint64_t v[4]; fp_to_limbs(v, &a[i]); for (int j = 0; j < 4; j++) { h ^= v[j]; h *= 1099511628211ULL; } }
    return h;
}
static size_t num(const char *s) { size_t v = 0; while (*s >= '0' && *s <= '9') v = v * 10 + (size_t)(*s++ - '0'); return v; }
int main(int argc, char **argv) {
    if (argc < 4) return 9;
    int mode = (int)num(argv[1]); int T = (int)num(argv[2]); size_t m = num(argv[3]);
    par_init(T); rng_seed(7);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    ntt_init(AMAX);
    if (mode == 1) {
        int e1 = (int)num(argv[4]), e2 = (int)num(argv[5]), e3 = (int)num(argv[6]);
        fp *g = NEW_FP(m + 1); for (size_t i = 0; i < m; i++) rnd_fp254(&g[i]); fp_set_one(&g[m]);
        fp *F = NEW_FP(m);
        uint64_t E[4] = { 0, 0, 0, 0 };
        E[e1 >> 6] |= 1ULL << (e1 & 63); E[e2 >> 6] |= 1ULL << (e2 & 63); E[e3 >> 6] |= 1ULL << (e3 & 63); E[0] |= 1;
        uint64_t t0 = thr_ctl, x0 = thr_extra; snap_t s0 = snap();
        powx_lean(F, g, m, E, 1);
        snap_t d = snap_sub(snap(), s0);
        printf("POW m=%zu E=2^%d+2^%d+2^%d+1 T=%d ck_g=%llx ck_F=%llx ops=%llu thread_control=%llu split_extra=%llu algorithmic=%llu heap_peak=%zu\n", m, e1, e2, e3, par_nt,
               ck(g, m + 1), ck(F, m), (unsigned long long)snap_total(d), (unsigned long long)(thr_ctl - t0), (unsigned long long)(thr_extra - x0),
               (unsigned long long)(snap_total(d) - (thr_ctl - t0) - (thr_extra - x0)), mem_peak);
    } else {
        size_t dg = num(argv[4]), mu = m - dg;
        fp *L = NEW_FP(dg + 1), *U = NEW_FP(mu + 1), *V = NEW_FP(mu + 1);
        for (size_t i = 0; i < dg; i++) rnd_fp254(&L[i]); fp_set_one(&L[dg]);
        for (size_t i = 0; i < mu; i++) rnd_fp254(&U[i]); fp_set_one(&U[mu]);
        for (size_t i = 0; i <= mu; i++) rnd_fp254(&V[i]);
        fp *A = NEW_FP(m + 1), *B = NEW_FP(m + 1);
        poly_mul(A, L, dg + 1, U, mu + 1); poly_mul(B, L, dg + 1, V, mu + 1);
        unsigned long long cA = ck(A, m + 1), cB = ck(B, m + 1);
        uint64_t t0 = thr_ctl, x0 = thr_extra; snap_t s0 = snap();
        size_t lG = 0; fp *G = poly_gcd_own(&lG, A, m + 1, B, m + 1);
        snap_t d = snap_sub(snap(), s0);
        printf("GCD m=%zu d=%zu T=%d ck_A=%llx ck_B=%llx lG=%zu ck_G=%llx ck_L=%llx match=%d ops=%llu thread_control=%llu algorithmic=%llu heap_peak=%zu\n", m, dg, par_nt, cA, cB, lG,
               lG ? ck(G, lG) : 0ULL, ck(L, dg + 1), lG == dg + 1 && ck(G, lG) == ck(L, dg + 1), (unsigned long long)snap_total(d), (unsigned long long)(thr_ctl - t0),
               (unsigned long long)(snap_total(d) - (thr_ctl - t0) - (thr_extra - x0)), mem_peak);
    }
    out_flush();
    return 0;
}
