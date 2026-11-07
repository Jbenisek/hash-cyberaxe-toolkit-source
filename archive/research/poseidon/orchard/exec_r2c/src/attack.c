/* End-to-end driver: one attempt of the odd-part collision attack on Orchard Poseidon with r partial rounds. */
#include "attack.h"
#include "pallas_consts.h"
#include <time.h>
#include <math.h>

typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[16]; static int nst = 0;
static snap_t cur; static clock_t tcur; static size_t peak_cur;
static void stage_begin(void) { cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); }

int main(int argc, char **argv) {
    int r = argc > 1 ? atoi(argv[1]) : 0;
    int j = argc > 2 ? atoi(argv[2]) : 0;
    uint64_t seed = argc > 3 ? strtoull(argv[3], 0, 0) : 1;
    int debug = argc > 4 ? atoi(argv[4]) : 0;
    int quiet = argc > 5 ? atoi(argv[5]) : 0;
    rng_seed(seed);
    size_t m = poly_degree_m(r);
    printf("r=%d j=%d seed=%llu m=%zu\n", r, j, (unsigned long long)seed, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);

    stage_begin(); ntt_init(15); stage_end("ntt_init (twiddle table, roots)");
    line_t L;
    stage_begin(); { snap_t s0 = snap(); line_setup(&L, j); bound_mem_since(s0); } stage_end("line_setup");
    fp c;
    stage_begin(); rnd_fp254(&c); stage_end("random centre");
    phex("centre c =", &c);
    fp *g = NEW_FP(m + 1);
    stage_begin(); build_g(g, &L, &c, r, debug); stage_end("build g (2H evaluations of F + inverse NTT)");
    fp *R = NEW_FP(m);
    stage_begin(); powx_mod(R, g, m, PALLAS_PM1H, 0, quiet); stage_end("S^((p-1)/2) mod g");
    fp one; fp_set_one(&one);
    stage_begin();
    fp_sub(&R[0], &R[0], &one);
    int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&R[dR])) dR--;
    CTL(m); LD(m);
    fp *G = NEW_FP(m + 1); size_t dG = 0;
    if (dR < 0) { printf("R-1 == 0: degenerate\n"); return 3; }
    euclid_gcd(G, g, m, R, (size_t)dR, &dG);
    stage_end("gcd(g, R-1)");
    printf("deg gcd = %zu\n", dG);
    int success = 0; fp nk1, rho1, nk2, rho2, dg1, dg2;
    if (dG >= 1) {
        fp S;
        stage_begin();
        int ok = find_root(&S, G, dG);
        stage_end("root finding");
        if (ok) {
            stage_begin();
            snap_t s0 = snap();
            fp s;
            int sq = fp_sqrt(&s, &S);
            if (!sq) { printf("root not a square?!\n"); }
            fp W1, W2;
            fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
            map_back(&nk1, &rho1, &L, &W1);
            map_back(&nk2, &rho2, &L, &W2);
            bound_mem_since(s0);
            stage_end("sqrt + map back");
            stage_begin();
            poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
            poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
            { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += ops; }
            stage_end("verification (2 reference hashes)");
            int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
            int eq = fp_eq(&dg1, &dg2);
            printf("collision: digests equal=%d inputs distinct=%d\n", eq, !same_in);
            phex("nk1 ", &nk1); phex("rho1", &rho1); phex("nk2 ", &nk2); phex("rho2", &rho2); phex("digest", &dg1);
            success = eq && !same_in;
        }
    }
    printf("SUCCESS=%d\n", success);
    snap_t tot; memset(&tot, 0, sizeof tot);
    uint64_t all = 0, arith = 0;
    printf("%-52s %14s %14s %14s %9s %10s\n", "stage", "arith", "ld+st+ctl+rnd", "total", "sec", "peak B");
    for (int i = 0; i < nst; i++) {
        uint64_t a = snap_arith(st[i].d), t = snap_total(st[i].d);
        printf("%-52s %14llu %14llu %14llu %9.1f %10zu\n", st[i].name, (unsigned long long)a, (unsigned long long)(t - a), (unsigned long long)t, st[i].sec, st[i].peak);
        all += t; arith += a;
    }
    int C = 216 + 21 * r;
    printf("TOTAL arith %llu  all-charged %llu   units = %.1f   log2(all/C) = %.4f   log2(arith/C) = %.4f\n", (unsigned long long)arith, (unsigned long long)all, (double)all / C, log2((double)all / C), log2((double)arith / C));
    return success ? 0 : 1;
}
