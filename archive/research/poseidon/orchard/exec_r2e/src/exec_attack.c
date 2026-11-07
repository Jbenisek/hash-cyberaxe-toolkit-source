/* Orchard Poseidon, r = RR partial rounds: a deterministic search over centres in a fixed public order, executed-outcome accounting.
 * usage: exec_attack [verbose]          (RR is set by the define below)
 * Trial i = 1, 2, 3, ... uses the centre c_i = i (the field element with the integer value i).  Each trial is run completely: line j = LINE,
 * g = monic odd part of (F(c+s) - F(c-s))/s in S = s^2 (degree m = (5^(6+RR) - 1)/2), R = S^((p-1)/2) mod g, G = gcd(g, R - 1) (half-gcd), and, when
 * deg G >= 1, one root S of G, s = sqrt(S), W1 = c + s, W2 = c - s, back-map, verify with two reference hashes.  The program stops at the FIRST trial that
 * yields a collision, then encodes the output in canonical hexadecimal (stage H).  Every operation of every executed trial, failed trials included, is
 * charged (common.h), and every charged operation belongs to exactly one stage visit (the stage chain below has no gap), so the stage table, the per-trial
 * table and the counters of the whole run give one and the same total.  The root isolation draws no random word (its shifts are 1, 2, 3, ...).
 * There are no bounds and no caps on the work; a centre whose polynomial g has degree below m (vanishing leading coefficient) is skipped. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include <time.h>
#include <math.h>

#ifndef RR
#define RR 2
#endif
#ifndef LINE
#define LINE 0
#endif
#ifndef DEG_CAP
#define DEG_CAP 16
#endif
#define AMAX (RR == 1 ? 15 : 17)          /* 3 * 2^AMAX >= 2m - 1: the largest transform length */
typedef struct { const char *name; snap_t d; uint64_t tot; double sec; size_t peak; } stage_t;
#define MAXTR 64
static stage_t st[16]; static int nst;
static snap_t cur, vis; static clock_t tcur; static size_t gpeak, gpeak_live, gpeak_pay;
static const char *cur_name = NULL; static int cur_trial = 0;          /* the open stage and the trial it belongs to (0: none) */
static uint64_t trial_tot[MAXTR + 1], vis_hc_up;
static snap_t snap_add(snap_t a, snap_t b) { snap_t r; r.add = a.add + b.add; r.sub = a.sub + b.sub; r.mul = a.mul + b.mul; r.sqr = a.sqr + b.sqr; r.ld = a.ld + b.ld; r.st = a.st + b.st; r.ctl = a.ctl + b.ctl; r.rnd = a.rnd + b.rnd; r.perm = a.perm + b.perm; r.hc = a.hc + b.hc; return r; }
/* close the open stage visit: its charge (half units rounded up to a whole operation) is added to the row of its name and to the total of its trial */
static void stage_close(void) {
    if (!cur_name) return;
    snap_t d = snap_sub(snap(), cur);
    int k = 0; while (k < nst && strcmp(st[k].name, cur_name)) k++;
    if (k == nst) { st[k].name = cur_name; memset(&st[k].d, 0, sizeof st[k].d); st[k].tot = 0; st[k].sec = 0; st[k].peak = 0; nst++; }
    stage_t *s = &st[k]; s->d = snap_add(s->d, d); s->tot += snap_total(d); s->sec += (double)(clock() - tcur) / CLOCKS_PER_SEC; if (mem_peak > s->peak) s->peak = mem_peak;
    if (mem_peak > gpeak) { gpeak = mem_peak; gpeak_live = mem_peak_live; gpeak_pay = mem_peak_pay; }
    trial_tot[cur_trial] += snap_total(d);
    vis = snap_add(vis, d); vis_hc_up += (d.hc + 1) / 2;
    cur_name = NULL;
}
/* open the next stage visit (closing the previous one first, so no charged operation falls between two stages) */
static void stage_open(const char *name, int trial) { stage_close(); cur = snap(); tcur = clock(); mem_reset_peak(); cur_name = name; cur_trial = trial; }

/* canonical encoding of a field element as 64 hexadecimal digits (big-endian): one conversion out of the Montgomery representation (counted as one field
 * multiplication in pallas.c), then one pass over the 64 digits.  Per digit 12 operations: the loop (index update, comparison, branch), pos = 63 - i, the word
 * index pos >> 4, the shift count 4 * (pos & 15) (mask, multiply), the shift, the mask, the load of the digit from the table and the store of the byte;
 * 5 more for the entry of the call and the terminator. */
static const char HEXD[] = "0123456789abcdef";
static void enc_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    for (int i = 0; i < 64; i++) { int pos = 63 - i; out[i] = HEXD[(v[pos >> 4] >> (4 * (pos & 15))) & 15]; }
    out[64] = 0;
    CTL(64 * 12 + 5);
}

int main(int argc, char **argv) {
    const int r = RR;
    int verbose = argc > 1 ? atoi(argv[1]) : 0;
    size_t m = poly_degree_m(r);
    printf("r=%d line=%d m=%zu\n", r, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_open("init (twiddle table)", 0); ntt_init(AMAX);
    line_t L;
    stage_open("line setup", 0); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); }
    fp c, S, nk1, rho1, nk2, rho2, dg1, dg2, one; fp_set_one(&one);
    int found = 0, success = 0, trials = 0; size_t dG = 0;
    uint64_t t_centre[MAXTR + 1]; size_t t_deg[MAXTR + 1]; uint64_t t_gcd[MAXTR + 1]; int t_skip[MAXTR + 1];
    for (uint64_t i = 1; !success; i++) {
        trials++;
        if (trials > MAXTR) { fprintf(stderr, "too many trials\n"); return 2; }
        stage_open("A: centre c_i = i", trials); CTL(3); fp_from_u64(&c, i);       /* index update, comparison and branch of the trial loop; the conversion is one counted multiplication */
        t_centre[trials] = i; t_deg[trials] = 0; t_gcd[trials] = 0; t_skip[trials] = 0;
        fp *g = NEW_FP(m + 1);
        stage_open("B: build g", trials); int okg = build_g(g, &L, &c, r); CTL(2);
        if (!okg) { xfree(g); t_skip[trials] = 1; continue; }                      /* leading coefficient zero: the centre is skipped */
        fp *F = NEW_FP(m);
        stage_open("C: S^((p-1)/2) mod g", trials); powx_lean(F, g, m, PALLAS_PM1H, (verbose && i == 1) ? 2 : 1);
        stage_open("D: gcd(g, S^h - 1) (half-gcd)", trials);
        fp_sub(&F[0], &F[0], &one);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(4 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R - 1: executed tests only */
        size_t lG = 0; fp G[DEG_CAP + 1];
        snap_t sg = snap();
        if (dR >= 0) lG = poly_gcd_fast_own(G, DEG_CAP + 1, g, m + 1, F, (size_t)dR + 1);
        else { xfree(g); xfree(F); }
        t_gcd[trials] = snap_total(snap_sub(snap(), sg));
        CTL(4);                                              /* the test lG == cap + 1 and the test deg G >= 1 */
        if (lG == (size_t)-1) { printf("trial %d centre %llu: gcd degree above %d: trial abandoned\n", trials, (unsigned long long)i, DEG_CAP - 1); continue; }
        dG = lG ? lG - 1 : 0; t_deg[trials] = dG;
        printf("trial %d centre %llu: gcd degree %zu, charged %llu\n", trials, (unsigned long long)i, dG, (unsigned long long)t_gcd[trials]); fflush(stdout);
        if (dG < 1) continue;
        stage_open("E: root isolation", trials); found = find_root(&S, G, dG);
        CTL(2);
        if (!found) continue;
        stage_open("F: sqrt + map back", trials);
        snap_t s0 = snap();
        fp s; int sq = fp_sqrt(&s, &S);
        CTL(2);
        if (!sq) { printf("root not a square?!\n"); found = 0; continue; }
        fp W1, W2;
        fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
        map_back(&nk1, &rho1, &L, &W1);
        map_back(&nk2, &rho2, &L, &W2);
        bound_mem_since(s0);
        stage_open("G: verification (2 reference hashes)", trials);
        poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
        poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
        { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += ops; }
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
        int same_dg = fp_eq(&dg1, &dg2);
        CTL(3 * 8 + 2 * 3 + 2);                              /* three four-limb equality tests (8 operations each), the two tests combined, the test that ends the search */
        success = found && same_dg && !same_in;
    }
    /* stage H: the output of the program, the two canonical pairs (and the digest and the centre), encoded in canonical hexadecimal */
    char hx[6][65];
    stage_open("H: canonical encoding of the output", 0);
    enc_hex(hx[0], &nk1); enc_hex(hx[1], &rho1); enc_hex(hx[2], &nk2); enc_hex(hx[3], &rho2); enc_hex(hx[4], &dg1); enc_hex(hx[5], &c);
    stage_close();                                           /* from here on only the report of the counters is printed */
    printf("TRIALS %d\n", trials);
    uint64_t all = 0, arith = 0, trs = 0; double sec = 0;
    for (int i = 0; i < nst; i++) { all += st[i].tot; arith += snap_arith(st[i].d); sec += st[i].sec; }
    for (int t = 0; t <= trials; t++) trs += trial_tot[t];
    snap_t run = snap();
    int same = run.add == vis.add && run.sub == vis.sub && run.mul == vis.mul && run.sqr == vis.sqr && run.ld == vis.ld && run.st == vis.st && run.ctl == vis.ctl && run.rnd == vis.rnd && run.perm == vis.perm && run.hc == vis.hc;
    uint64_t counters = snap_arith(run) + run.ld + run.st + run.ctl + run.rnd + run.perm + vis_hc_up;   /* counters of the whole run, half units rounded up per stage visit */
    for (int i = 0; i < nst; i++)
        printf("  %-40s arith=%12llu other=%12llu total=%12llu %7.1fs peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
               (unsigned long long)(st[i].tot - snap_arith(st[i].d)), (unsigned long long)st[i].tot, st[i].sec, st[i].peak);
    for (int t = 1; t <= trials; t++)
        printf("TRIALROW %d centre %llu degG %zu gcd %llu total %llu skipped %d\n", t, (unsigned long long)t_centre[t], t_deg[t], (unsigned long long)t_gcd[t], (unsigned long long)trial_tot[t], t_skip[t]);
    printf("TRIALROW 0 outside the trials (init, line setup, output encoding) total %llu\n", (unsigned long long)trial_tot[0]);
    printf("RECONCILE stages=%llu trials=%llu counters=%llu ok=%d\n", (unsigned long long)all, (unsigned long long)trs, (unsigned long long)counters, same && all == trs && trs == counters);
    printf("RESULT found=%d success=%d roots_degree=%zu\n", found, success, dG);
    int C = 216 + 21 * r;
    printf("SUMMARY total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", (unsigned long long)counters, (unsigned long long)arith, (double)counters / C, log2((double)counters / C), gpeak, sec);
    printf("PEAKLIVE allocations=%zu payload=%zu headers=%zu\n", gpeak_live, gpeak_pay, gpeak_live * 64);
    printf("HALFUNITS hc=%llu\n", (unsigned long long)run.hc);
    printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu\n", (unsigned long long)run.add, (unsigned long long)run.sub, (unsigned long long)run.mul, (unsigned long long)run.sqr,
           (unsigned long long)run.ld, (unsigned long long)run.st, (unsigned long long)run.ctl, (unsigned long long)run.rnd, (unsigned long long)run.perm);
    if (success) {
        printf("COLLISION nk1  0x%s\nCOLLISION rho1 0x%s\nCOLLISION nk2  0x%s\nCOLLISION rho2 0x%s\nCOLLISION digest 0x%s\nCOLLISION centre 0x%s\n", hx[0], hx[1], hx[2], hx[3], hx[4], hx[5]);
    }
    return success ? 0 : 1;
}
