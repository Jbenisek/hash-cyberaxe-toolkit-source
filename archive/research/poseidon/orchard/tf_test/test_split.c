/* Tests of split.c on synthetic products of linear factors: root isolation, gcd charge against its derived bound, Taylor shift, division. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(18);
    rng_seed(argc > 1 ? strtoull(argv[1], 0, 0) : 7);
    size_t ds[] = { 1, 2, 3, 4, 5, 9, 17, 40, 41, 64, 200, 1000, 3000, 0 };
    int ok = 1;
    for (int t = 0; ds[t]; t++) {
        size_t d = ds[t];
        fp *roots = NEW_FP(d), *G = NEW_FP(d + 1);
        for (size_t i = 0; i < d; i++) rnd_fp254(&roots[i]);
        fp_set_one(&G[0]);
        size_t deg = 0;
        for (size_t i = 0; i < d; i++) {          /* multiply by (Z - r_i) */
            fp nr; fp_neg(&nr, &roots[i]);
            G[deg + 1] = G[deg];
            for (size_t k = deg; k >= 1; k--) { fp tm; fp_mul(&tm, &G[k], &nr); fp_add(&G[k], &G[k - 1], &tm); }
            fp tm; fp_mul(&tm, &G[0], &nr); G[0] = tm;
            deg++;
        }
        fp *Gc = NEW_FP(d + 1); memcpy(Gc, G, (d + 1) * sizeof(fp));
        snap_t s0 = snap(); clock_t c0 = clock();
        SPL_levels = SPL_tries = SPL_divs = SPL_shift = SPL_pow = SPL_gcd = SPL_div = 0;
        fp root; int res = split_find_root(&root, Gc, d);
        snap_t dd = snap_sub(snap(), s0);
        int isroot = 0;
        if (res) for (size_t i = 0; i < d; i++) if (fp_eq(&roots[i], &root)) isroot = 1;
        printf("d=%zu: found=%d is_root=%d levels=%llu tries=%llu charged=%llu %.1fs\n", d, res, isroot, (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)snap_total(dd), (double)(clock() - c0) / CLOCKS_PER_SEC);
        printf("   parts: shift=%llu pow=%llu gcd=%llu div=%llu (divisions %llu) misc=%lld\n",(unsigned long long)SPL_shift, (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div, (unsigned long long)SPL_divs,
               (long long)(snap_total(dd) - SPL_shift - SPL_pow - SPL_gcd - SPL_div));
        ok &= res && isroot;
        /* taylor shift check: (G shifted by a)(z) == G(z + a) */
        fp a, z, e1, e2; rnd_fp254(&a); rnd_fp254(&z);
        fp *Gs = NEW_FP(d + 1); memcpy(Gs, G, (d + 1) * sizeof(fp));
        Gs = taylor_shift(Gs, d, &a);
        fp_set_zero(&e1); for (size_t k = d + 1; k-- > 0;) { fp_mul(&e1, &e1, &z); fp_add(&e1, &e1, &Gs[k]); }
        fp za; fp_add(&za, &z, &a); fp_set_zero(&e2); for (size_t k = d + 1; k-- > 0;) { fp_mul(&e2, &e2, &za); fp_add(&e2, &e2, &G[k]); }
        printf("   taylor shift ok: %d\n", fp_eq(&e1, &e2)); ok &= fp_eq(&e1, &e2);
        /* gcd charge vs bound: gcd(G, G') style random pair of degrees d, d-1 */
        if (d >= 2) {
            fp *B = NEW_FP(d); for (size_t i = 0; i < d; i++) rnd_fp254(&B[i]);
            fp *out = NEW_FP(d + 1);
            snap_t g0 = snap(); size_t dg = gcd_cl(out, G, d, B, d - 1); uint64_t ch = snap_total(snap_sub(snap(), g0));
            uint64_t bd = gcd_cost_bound(d, d - 1);
            printf("   gcd degree %zu charged %llu bound %llu ratio %.4f %s\n", dg, (unsigned long long)ch, (unsigned long long)bd, (double)ch / bd, ch <= bd ? "ok" : "EXCEEDED");
            ok &= ch <= bd;
            /* gcd with a known factor */
            fp *Hh = NEW_FP(d); fp_set_zero(&Hh[0]);
            xfree(B); xfree(out); xfree(Hh);
        }
        xfree(Gs); xfree(G); xfree(roots);
    }
    printf(ok ? "ALL OK\n" : "FAILURES\n");
    return !ok;
}
