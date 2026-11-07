/* Orchard Poseidon, r = 1: a deterministic search over centres in a fixed public order, executed-outcome accounting.
 * usage: single [verbose]
 * Trial i = 1, 2, 3, ... uses the centre c_i = i (the field element with the integer value i).  Each trial is run completely: line j = LINE,
 * g = monic odd part of (F(c+s) - F(c-s))/s in S = s^2 (degree m = 39062), R = S^((p-1)/2) mod g, G = gcd(g, R - 1) (half-gcd), and, when deg G >= 1,
 * one root S of G, s = sqrt(S), W1 = c + s, W2 = c - s, back-map, verify with two reference hashes.  The program stops at the FIRST trial that
 * yields a collision.  Every operation of every executed trial, failed trials included, is charged (common.h); nothing is selected beforehand.
 * The generator (seed 1) is used only by the root isolation, which runs only when deg G >= 2.  There are no bounds and no caps. */
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
static snap_t snap_add(snap_t a, snap_t b) { snap_t r; r.add = a.add + b.add; r.sub = a.sub + b.sub; r.mul = a.mul + b.mul; r.sqr = a.sqr + b.sqr; r.ld = a.ld + b.ld; r.st = a.st + b.st; r.ctl = a.ctl + b.ctl; r.rnd = a.rnd + b.rnd; r.perm = a.perm + b.perm; r.hc = a.hc + b.hc; return r; }
static void stage_begin(void) { cur = snap(); tcur = clock(); mem_reset_peak(); }
/* stages of the same name are summed over the trials; the peak is the maximum */
static void stage_end(const char *name) {
    int k = 0; while (k < nst && strcmp(st[k].name, name)) k++;
    if (k == nst) { st[k].name = name; memset(&st[k].d, 0, sizeof st[k].d); st[k].sec = 0; st[k].peak = 0; nst++; }
    stage_t *s = &st[k]; s->d = snap_add(s->d, snap_sub(snap(), cur)); s->sec += (double)(clock() - tcur) / CLOCKS_PER_SEC; if (mem_peak > s->peak) s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

int main(int argc, char **argv) {
    const int r = 1;
    int verbose = argc > 1 ? atoi(argv[1]) : 0;
    rng_seed(1);
    size_t m = poly_degree_m(r);
    printf("r=%d line=%d m=%zu\n", r, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_begin(); ntt_init(15); stage_end("init (twiddle table)");
    line_t L;
    stage_begin(); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); } stage_end("line setup");
    fp c, S, nk1, rho1, nk2, rho2, dg1, dg2, one; fp_set_one(&one);
    int found = 0, success = 0, trials = 0; size_t dG = 0;
    for (uint64_t i = 1; !success; i++) {
        trials++;
        stage_begin(); CTL(2); fp_from_u64(&c, i); stage_end("A: centre c_i = i");
        fp *g = NEW_FP(m + 1);
        stage_begin(); build_g(g, &L, &c, r, 0); stage_end("B: build g");
        fp *F = NEW_FP(m);
        stage_begin(); powx_lean(F, g, m, PALLAS_PM1H, (verbose && i == 1) ? 2 : 1); stage_end("C: S^((p-1)/2) mod g");
        stage_begin();
        fp_sub(&F[0], &F[0], &one);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R - 1: executed tests only */
        size_t lG = 0; fp *G = NULL;
        snap_t sg = snap();
        G = poly_gcd_own(&lG, g, m + 1, F, (size_t)dR + 1);
        uint64_t gcd_charged = snap_total(snap_sub(snap(), sg));
        stage_end("D: gcd(g, S^h - 1) (half-gcd)");
        dG = lG ? lG - 1 : 0;
        printf("trial %d centre %llu: gcd degree %zu, charged %llu\n", trials, (unsigned long long)i, dG, (unsigned long long)gcd_charged); fflush(stdout);
        CTL(2);                                              /* the test deg G >= 1 */
        if (dG < 1) { if (G) xfree(G); continue; }
        stage_begin(); found = split_find_root(&S, G, dG); stage_end("E: root isolation");
        CTL(2);
        if (!found) continue;
        stage_begin();
        snap_t s0 = snap();
        fp s; int sq = fp_sqrt(&s, &S);
        CTL(12000);                                  /* Tonelli-Shanks control */
        CTL(2);
        if (!sq) { printf("root not a square?!\n"); found = 0; continue; }
        fp W1, W2;
        fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
        map_back(&nk1, &rho1, &L, &W1);
        map_back(&nk2, &rho2, &L, &W2);
        bound_mem_since(s0);
        stage_end("F: sqrt + map back");
        stage_begin();
        poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
        poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
        { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += ops; }
        stage_end("G: verification (2 reference hashes)");
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
        success = found && fp_eq(&dg1, &dg2) && !same_in;
        CTL(2);                                              /* the test that ends the search */
    }
    printf("TRIALS %d\n", trials);
    uint64_t all = 0, arith = 0; double sec = 0;
    for (int i = 0; i < nst; i++) { all += snap_total(st[i].d); arith += snap_arith(st[i].d); sec += st[i].sec; }
    for (int i = 0; i < nst; i++)
        printf("  %-40s arith=%12llu other=%12llu total=%12llu %7.1fs peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
               (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].sec, st[i].peak);
    printf("RESULT found=%d success=%d roots_degree=%zu\n", found, success, dG, trials);
    printf("SPLIT levels=%llu tries=%llu shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)SPL_shift,
           (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    int C = 216 + 21 * r;
    printf("SUMMARY total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", (unsigned long long)all, (unsigned long long)arith, (double)all / C, log2((double)all / C), gpeak, sec);
    { snap_t tt; memset(&tt, 0, sizeof tt);
      for (int i = 0; i < nst; i++) { tt.add += st[i].d.add; tt.sub += st[i].d.sub; tt.mul += st[i].d.mul; tt.sqr += st[i].d.sqr; tt.ld += st[i].d.ld; tt.st += st[i].d.st; tt.ctl += st[i].d.ctl; tt.rnd += st[i].d.rnd; tt.perm += st[i].d.perm; tt.hc += st[i].d.hc; }
      printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu hc=%llu\n", (unsigned long long)tt.add, (unsigned long long)tt.sub, (unsigned long long)tt.mul, (unsigned long long)tt.sqr,
             (unsigned long long)tt.ld, (unsigned long long)tt.st, (unsigned long long)tt.ctl, (unsigned long long)tt.rnd, (unsigned long long)tt.perm, (unsigned long long)tt.hc); }
    if (success) {
        phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
        phex("COLLISION digest", &dg1); phex("COLLISION centre", &c);
    }
    return success ? 0 : 1;
}
