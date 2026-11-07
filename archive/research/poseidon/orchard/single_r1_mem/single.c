/* Orchard Poseidon, r = 1, one centre of the odd-part method.
 * usage: single seed [verbose]
 * One attempt: line j = LINE, one random centre c, g = monic odd part of (F(c+s) - F(c-s))/s in S = s^2 (degree m = 39062),
 * R = S^((p-1)/2) mod g, G = gcd(g, R - 1) (half-gcd), one root S of G (root isolation by random shifts), s = sqrt(S),
 * W1 = c + s, W2 = c - s, back-map, verify with two reference hashes.  Every executed operation is charged (common.h).
 * There is no loop over attempts and no budget check: every data-dependent stage is charged at a derived bound that the program asserts. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include "gcd_bounds.h"
#include <time.h>
#include <math.h>

#ifndef LINE
#define LINE 0
#endif
typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[16]; static int nst;
static snap_t cur; static clock_t tcur; static size_t gpeak;
static void stage_begin(void) { cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

int main(int argc, char **argv) {
    const int r = 1;
    uint64_t seed = argc > 1 ? strtoull(argv[1], 0, 0) : 1;
    int verbose = argc > 2 ? atoi(argv[2]) : 0;
    rng_seed(seed);
    size_t m = poly_degree_m(r);
    printf("r=%d seed=%llu line=%d m=%zu\n", r, (unsigned long long)seed, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_begin(); ntt_init(15); stage_end("init (twiddle table)");
    uint64_t pre = snap_total(st[0].d);
    line_t L;
    stage_begin(); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); } stage_end("line setup");
    fp c;
    stage_begin(); rnd_fp254(&c); stage_end("random centre");
    fp *g = NEW_FP(m + 1);
    stage_begin(); build_g(g, &L, &c, r, 0); stage_end("B: build g");
    fp *F = NEW_FP(m);
    stage_begin(); powx_lean(F, g, m, PALLAS_PM1H, verbose ? 2 : 1); stage_end("C: S^((p-1)/2) mod g");
    fp one; fp_set_one(&one);
#ifdef DUMP_D
    { FILE *fd = fopen(DUMP_D, "wb"); fwrite(g, sizeof(fp), m + 1, fd); fwrite(F, sizeof(fp), m, fd); fwrite(&c, sizeof(fp), 1, fd); fclose(fd); }
#endif
    stage_begin();
    fp_sub(&F[0], &F[0], &one);
    int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
    CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R - 1: executed tests only */
    size_t lG = 0; fp *G = NULL;
    snap_t sg = snap();
    G = poly_gcd_own(&lG, g, m + 1, F, (size_t)dR + 1);
    uint64_t gcd_charged = snap_total(snap_sub(snap(), sg));
    if (gcd_charged > LEVELB[0].gcd) { fprintf(stderr, "gcd charge %llu above its bound %llu\n", (unsigned long long)gcd_charged, (unsigned long long)LEVELB[0].gcd); return 81; }
    stage_end("D: gcd(g, S^h - 1) (half-gcd)");
    size_t dG = lG ? lG - 1 : 0;
    printf("gcd degree %zu, charged %llu, derived bound %llu (within)\n", dG, (unsigned long long)gcd_charged, (unsigned long long)LEVELB[0].gcd);
    int found = 0, success = 0;
    fp S, nk1, rho1, nk2, rho2, dg1, dg2;
#ifdef DEG_CAP
    CTL(2);                                              /* variant with a cap on deg G: a larger G ends the attempt (a failure event of section 8) */
    if (dG > DEG_CAP) { printf("deg G above the cap: attempt ends\n"); xfree(G); G = NULL; dG = 0; }
#endif
    if (dG >= 1) {
        stage_begin(); found = split_find_root(&S, G, dG); stage_end("E: root isolation");
        if (found) {
            stage_begin();
            snap_t s0 = snap();
            fp s; int sq = fp_sqrt(&s, &S);
            CTL(12000);                                  /* Tonelli-Shanks control */
            if (!sq) { printf("root not a square?!\n"); found = 0; }
            fp W1, W2;
            fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
            map_back(&nk1, &rho1, &L, &W1);
            map_back(&nk2, &rho2, &L, &W2);
            bound_mem_since(s0);
            stage_end("F: sqrt + map back");
            stage_begin();
            poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
            poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
            { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
            stage_end("G: verification (2 reference hashes)");
            int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
            success = found && fp_eq(&dg1, &dg2) && !same_in;
        }
    } else if (G) xfree(G);
    uint64_t all = 0, arith = 0; double sec = 0;
    for (int i = 0; i < nst; i++) { all += snap_total(st[i].d); arith += snap_arith(st[i].d); sec += st[i].sec; }
    for (int i = 0; i < nst; i++)
        printf("  %-40s arith=%12llu other=%12llu total=%12llu %7.1fs peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
               (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].sec, st[i].peak);
    printf("RESULT found=%d success=%d roots_degree=%zu\n", found, success, dG);
    printf("SPLIT levels=%llu tries=%llu shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)SPL_shift,
           (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    int C = 216 + 21 * r;
    printf("SUMMARY total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", (unsigned long long)all, (unsigned long long)arith, (double)all / C, log2((double)all / C), gpeak, sec);
    { snap_t tt; memset(&tt, 0, sizeof tt);
      for (int i = 0; i < nst; i++) { tt.add += st[i].d.add; tt.sub += st[i].d.sub; tt.mul += st[i].d.mul; tt.sqr += st[i].d.sqr; tt.ld += st[i].d.ld; tt.st += st[i].d.st; tt.ctl += st[i].d.ctl; tt.rnd += st[i].d.rnd; tt.perm += st[i].d.perm; }
      printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu\n", (unsigned long long)tt.add, (unsigned long long)tt.sub, (unsigned long long)tt.mul, (unsigned long long)tt.sqr,
             (unsigned long long)tt.ld, (unsigned long long)tt.st, (unsigned long long)tt.ctl, (unsigned long long)tt.rnd, (unsigned long long)tt.perm); }
    if (success) {
        phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
        phex("COLLISION digest", &dg1); phex("COLLISION centre", &c);
    }
    return success ? 0 : 1;
}
