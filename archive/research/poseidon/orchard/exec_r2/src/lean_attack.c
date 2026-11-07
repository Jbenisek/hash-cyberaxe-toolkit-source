/* Orchard Poseidon, r partial rounds: odd-part collision attack, lean schedule.
 * usage: lean_attack r ncentres seed [j0] [verbose] [budget_gcd budget_root] [fixed_line]
 * Per centre: build g by evaluation + inverse NTT, S^((p-1)/2) mod g (lean in-place schedule), gcd(g, S^h-1) by half-gcd,
 * root splitting, back-map, verification by two reference hashes.  Stops after the first verified collision or after
 * ncentres failed centres.  Every field operation, 256-bit load/store, loop-control op and random word is counted. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include "budgets.h"
#include <time.h>
#include <math.h>

#ifndef BUDGET_GCD
#define BUDGET_GCD 0ULL   /* 0: use the table budget_table() below */
#endif
#ifndef BUDGET_ROOT
#define BUDGET_ROOT 0ULL
#endif
#ifndef BUDGET_FIN
#define BUDGET_FIN 100000ULL
#endif
#ifndef DEG_CAP
#define DEG_CAP 16
#endif
/* budgets per target (operations of the run's cost model); derivation in proof.md section 4.4 (computed by bound_gcd.c) */
static void budget_table(int r, uint64_t *gcd, uint64_t *root) {
    switch (r) {
    case 1: *gcd = BUDGET_R1_GCD; *root = BUDGET_R1_ROOT; break;
    case 2: *gcd = BUDGET_R2_GCD; *root = BUDGET_R2_ROOT; break;
    default: *gcd = 0; *root = 0;
    }
}
typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[16]; static int nst;
static snap_t cur; static clock_t tcur; static size_t gpeak;
static void stage_begin(void) { nst = nst; cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

int main(int argc, char **argv) {
    int r = argc > 1 ? atoi(argv[1]) : 1;
    int ncen = argc > 2 ? atoi(argv[2]) : 1;
    uint64_t seed = argc > 3 ? strtoull(argv[3], 0, 0) : 1;
    int j0 = argc > 4 ? atoi(argv[4]) : 0;
    int verbose = argc > 5 ? atoi(argv[5]) : 0;
    rng_seed(seed);
    size_t m = poly_degree_m(r);
    uint64_t bgcd = BUDGET_GCD, broot = BUDGET_ROOT;
    /* executed-outcome form: no budget halts (a halt is not an executed-outcome event); budgets only if given on the command line */
    if (argc > 6 && strtoull(argv[6], 0, 0)) bgcd = strtoull(argv[6], 0, 0);
    if (argc > 7 && strtoull(argv[7], 0, 0)) broot = strtoull(argv[7], 0, 0);
    int fixed_line = argc > 8 ? atoi(argv[8]) : 0;   /* 1: every centre uses line j0 */
    int amax = 2; while (3 * ((size_t)1 << amax) < 2 * m - 1) amax++;
    printf("r=%d ncentres=%d seed=%llu m=%zu\n", r, ncen, (unsigned long long)seed, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    uint64_t tot_all = 0, tot_arith = 0; double tot_sec = 0; snap_t tot_t; memset(&tot_t, 0, sizeof tot_t);
    int success = 0, centres_done = 0; uint64_t root_spent = 0, gcd_gap = 0, max_gcd_gap = 0, max_root_gap = 0;
    stage_begin(); ntt_init(amax); stage_end("ntt_init");
    printf("INIT arith=%llu other=%llu total=%llu", (unsigned long long)snap_arith(st[0].d), (unsigned long long)(snap_total(st[0].d) - snap_arith(st[0].d)), (unsigned long long)snap_total(st[0].d)); putchar(10);
    uint64_t tot_hc = st[0].d.hc; uint64_t pre_all = snap_total(st[0].d) - (st[0].d.hc + 1) / 2; tot_all += pre_all; tot_arith += snap_arith(st[0].d); nst = 0;
    tot_t.add += st[0].d.add; tot_t.sub += st[0].d.sub; tot_t.mul += st[0].d.mul; tot_t.sqr += st[0].d.sqr; tot_t.ld += st[0].d.ld; tot_t.st += st[0].d.st; tot_t.ctl += st[0].d.ctl;
    for (int ci = 0; ci < ncen && !success; ci++) {
        int j = fixed_line ? j0 % 3 : (j0 + ci) % 3;
        nst = 0;
        line_t L;
        stage_begin(); { snap_t s0 = snap(); line_setup(&L, j); bound_mem_since(s0); } stage_end("line_setup");
        fp c;
        stage_begin(); fp_from_u64(&c, (uint64_t)ci + 1); CTL(1); stage_end("centre c_i = i (i = 1, 2, 3, ...)");
        fp *g = NEW_FP(m + 1);
        stage_begin(); build_g(g, &L, &c, r, 0); stage_end("build g");
        fp *F = NEW_FP(m);
        stage_begin(); powx_lean(F, g, m, PALLAS_PM1H, verbose ? 2 : 1); stage_end("S^((p-1)/2) mod g");
        fp one; fp_set_one(&one);
        stage_begin();
        fp_sub(&F[0], &F[0], &one);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(4 * m); LD(m + 1);
        fp G[DEG_CAP + 1]; size_t lG = 0;
        if (bgcd) budget_arm(bgcd, "gcd");
        if (dR >= 0) lG = poly_gcd_fast_own(G, DEG_CAP + 1, g, m + 1, F, (size_t)dR + 1);
        else { xfree(g); xfree(F); }
        budget_check(); gcd_gap = budget_maxgap(); if (gcd_gap > max_gcd_gap) max_gcd_gap = gcd_gap;
        budget_arm(0, "");
        stage_end("gcd(g, S^h-1) (half-gcd)");
        size_t dG = lG == (size_t)-1 ? 0 : (lG ? lG - 1 : 0);
        fp nk1, rho1, nk2, rho2, dg1, dg2, cS;
        int found = 0;
        if (lG == (size_t)-1) printf("centre %d: gcd degree above 8: trial abandoned\n", ci);
        if (dG >= 1) {
            fp S;
            stage_begin(); if (broot) budget_arm(broot - root_spent > 0 ? broot - root_spent : 1, "root"); found = find_root(&S, G, dG); budget_check(); if (budget_maxgap() > max_root_gap) max_root_gap = budget_maxgap(); budget_arm(0, ""); stage_end("root finding"); root_spent += snap_total(st[nst - 1].d);
            if (found) {
                stage_begin();
                snap_t s0 = snap();
                fp s; int sq = fp_sqrt(&s, &S);
                if (!sq) { printf("root not a square?!\n"); found = 0; }
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
                success = found && fp_eq(&dg1, &dg2) && !same_in;
            }
        }
        uint64_t all = 0, arith = 0; double sec = 0;
        for (int i = 0; i < nst; i++) { tot_hc += st[i].d.hc; all += snap_total(st[i].d) - (st[i].d.hc + 1) / 2; arith += snap_arith(st[i].d); sec += st[i].sec; }
        tot_all += all; tot_arith += arith; tot_sec += sec; centres_done++;
        for (int i = 0; i < nst; i++) { tot_t.add += st[i].d.add; tot_t.sub += st[i].d.sub; tot_t.mul += st[i].d.mul; tot_t.sqr += st[i].d.sqr; tot_t.ld += st[i].d.ld; tot_t.st += st[i].d.st; tot_t.ctl += st[i].d.ctl; tot_t.rnd += st[i].d.rnd; tot_t.perm += st[i].d.perm; }
        printf("CENTRE %d j=%d degG=%zu success=%d arith=%llu all=%llu sec=%.1f\n", ci, j, dG, success,
               (unsigned long long)arith, (unsigned long long)all, sec);
        if (verbose || success) {
            for (int i = 0; i < nst; i++)
                printf("  %-40s arith=%12llu other=%12llu total=%12llu %7.1fs peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
                       (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].sec, st[i].peak);
        }
        fflush(stdout);
        if (success) {
            phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
            phex("COLLISION digest", &dg1); phex("COLLISION centre", &c); (void)cS;
        }
    }
    tot_all += (tot_hc + 1) / 2;   /* half units summed over the whole run, rounded up once */
    extern int fault_count; printf("FAULTS detected=%d\n", fault_count);
    printf("HALFUNITS hc=%llu\n", (unsigned long long)tot_hc);
    int C = 216 + 21 * r;
    printf("SUMMARY r=%d centres=%d success=%d total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", r, centres_done, success,
           (unsigned long long)tot_all, (unsigned long long)tot_arith, (double)tot_all / C, log2((double)tot_all / C), gpeak, tot_sec);
    printf("GAPS gcd=%llu root=%llu", (unsigned long long)max_gcd_gap, (unsigned long long)max_root_gap); putchar(10);
    printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu", (unsigned long long)tot_t.add, (unsigned long long)tot_t.sub, (unsigned long long)tot_t.mul, (unsigned long long)tot_t.sqr, (unsigned long long)tot_t.ld, (unsigned long long)tot_t.st, (unsigned long long)tot_t.ctl, (unsigned long long)tot_t.rnd, (unsigned long long)tot_t.perm);
    putchar(10);
    return success ? 0 : 1;
}
