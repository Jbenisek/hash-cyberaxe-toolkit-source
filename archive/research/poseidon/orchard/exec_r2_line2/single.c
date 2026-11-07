/* Orchard Poseidon, r = RR partial rounds: the plain single-line route.  A deterministic search over centres in a fixed public order, executed-outcome
 * accounting.  usage: single [verbose]          (RR is set by the define below)
 * Trial i = 1, 2, 3, ... uses the centre c_i = i (the field element with the integer value i).  Each trial is run completely: line j = LINE (the digest
 * polynomial F(W) of degree D = 5^(6+RR) on the line), q(X) = (F(X) - F(c))/(X - c) made monic (degree D - 1), R = X^p mod q, G = gcd(q, R - X) (half-gcd);
 * every root W of G other than c has F(W) = F(c).  When deg G >= 1, one root W of G is isolated, W1 = c, W2 = W, back-map, verify with two reference
 * hashes.  The program stops at the FIRST trial that yields a collision, then encodes the output in canonical hexadecimal (stage H).  Every operation of
 * every executed trial, failed trials included, is charged (common.h), and every charged operation belongs to exactly one stage, so the stage table, the
 * per-trial table and the counters of the whole run give one and the same total.  The generator (seed 1) is used only by the root isolation, which runs
 * only when deg G >= 2.  No probability bound enters the count; the bounds in it are the stated constants of stage I and the flat statistics charge of the allocator.  Finite guards in the source: MAXTR = 64 trials (more would print a message and exit with status 2, no collision; not reached), and the checks that exit with a message (a vanishing leading coefficient of F, a plan length beyond the table, a non-monic modulus); none is reached in the recorded run.  No odd-part or parity halving is used: the polynomials have the full degree. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include "outbuf.h"

#ifndef RR
#define RR 2
#endif
#ifndef LINE
#define LINE 0
#endif
#define AMAX (RR == 1 ? 16 : 18)          /* 3 * 2^AMAX >= 2m - 1, m = 5^(6+RR) - 1: the largest transform length */
typedef struct { const char *name; snap_t d; size_t peak; } stage_t;
#define MAXTR 64
static stage_t st[16]; static int nst;
static snap_t cur; static size_t gpeak, gpeak_live, gpeak_pay;
static const char *cur_name = NULL; static int cur_trial = 0;          /* the open stage and the trial it belongs to (0: none) */
static uint64_t trial_tot[MAXTR + 1];
static snap_t snap_add(snap_t a, snap_t b) { snap_t r; r.add = a.add + b.add; r.sub = a.sub + b.sub; r.mul = a.mul + b.mul; r.sqr = a.sqr + b.sqr; r.ld = a.ld + b.ld; r.st = a.st + b.st; r.ctl = a.ctl + b.ctl; r.rnd = a.rnd + b.rnd; r.perm = a.perm + b.perm; return r; }
/* close the open stage: its counters are added to the row of its name and to the total of its trial; the peak is the maximum over the visits */
static void stage_close(void) {
    if (!cur_name) return;
    snap_t d = snap_sub(snap(), cur);
    int k = 0; while (k < nst && strcmp(st[k].name, cur_name)) k++;
    if (k == nst) { st[k].name = cur_name; memset(&st[k].d, 0, sizeof st[k].d); st[k].peak = 0; nst++; }
    stage_t *s = &st[k]; s->d = snap_add(s->d, d); if (mem_peak > s->peak) s->peak = mem_peak;
    if (mem_peak > gpeak) { gpeak = mem_peak; gpeak_live = mem_peak_live; gpeak_pay = mem_peak_pay; }
    trial_tot[cur_trial] += snap_total(d);
    cur_name = NULL;
}
/* The stage bookkeeping (reading the nine counters twice, the subtraction, the search of the row by name, the additions into the row, the comparisons of the peaks,
 * the reset of the peak) is itself executed code: each stage_open (which includes the stage_close of the previous stage) is charged STAGE_BK = 1000 operations in
 * the stage it opens (bound: 9 loads + 9 subtractions + 9 additions + 9 stores + a search over at most 16 rows of at most 3 operations each + a name comparison
 * of at most 8 operations per row: under 400). */
#define STAGE_BK 1000
/* open the next stage (closing the previous one first, so no charged operation falls between two stages) */
static void stage_open(const char *name, int trial) { stage_close(); cur = snap(); mem_reset_peak(); cur_name = name; cur_trial = trial; CTL(STAGE_BK); }

/* canonical encoding of a field element as 64 hexadecimal digits (big-endian): one conversion out of the Montgomery representation (counted as one field
 * multiplication in pallas.c), then one pass over the 64 digits.  Per digit 12 operations: the loop (index update, comparison, branch), pos = 63 - i, the word
 * index pos >> 4, the shift count (pos & 15) << 2 (mask, shift), the shift, the mask, the load of the digit from the table and the store of the byte;
 * 5 more for the entry of the call and the terminator. */
static const char HEXD[] = "0123456789abcdef";
static void enc_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    for (int i = 0; i < 64; i++) { int pos = 63 - i; out[i] = HEXD[(v[pos >> 4] >> ((pos & 15) << 2)) & 15]; }
    out[64] = 0;
    CTL(64 * 12 + 5);
}

/* statements of main executed before the counters start: the argument test, rng_seed(1), poly_degree_q (6 + r iterations of a shift, an addition and a loop test),
 * the call of printf for the first report line (its bytes are inside the output buffer, charged in stage I), the reset of the counters: PROLOGUE = 500 (bound, under 100 operations) */
#define PROLOGUE 500
int main(int argc, char **argv) {
    const int r = RR;
    int verbose = argc > 1 ? (argv[1][0] - '0') : 0;
    rng_seed(1);
    size_t m = poly_degree_q(r);
    printf("r=%d line=%d m=%zu\n", r, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_open("init (twiddle table)", 0); CTL(PROLOGUE); ntt_init(AMAX);
    line_t L;
    stage_open("line setup", 0); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); }
    fp c, S, nk1, rho1, nk2, rho2, dg1, dg2, one; fp_set_one(&one);
    int found = 0, success = 0, trials = 0; size_t dG = 0;
    uint64_t t_centre[MAXTR + 1]; size_t t_deg[MAXTR + 1]; uint64_t t_gcd[MAXTR + 1];
    for (uint64_t i = 1; !success; i++) {
        trials++;
        if (trials > MAXTR) { fprintf(stderr, "too many trials\n"); return 2; }
        stage_open("A: centre c_i = i", trials); CTL(3 + 2 + 2); fp_from_u64(&c, i);   /* loop test and index update of the trial loop (3), the test trials > MAXTR with its branch (2), the assignment of the trial row (2); the conversion is one counted multiplication */
        t_centre[trials] = i; t_deg[trials] = 0; t_gcd[trials] = 0;
        fp *g = NEW_FP(m + 1);
        stage_open("B: build q", trials); build_q(g, &L, &c, r);
        fp *F = NEW_FP(m);
        stage_open("C: X^p mod q", trials); powx_lean(F, g, m, PALLAS_P, (verbose && i == 1) ? 2 : 1);
        stage_open("D: gcd(q, X^p - X) (half-gcd)", trials);
        fp_sub(&F[1], &F[1], &one); LD(1); ST(1);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R - 1: executed tests only */
        size_t lG = 0; fp *G = NULL;
        snap_t sg = snap();
        G = poly_gcd_own(&lG, g, m + 1, F, (size_t)dR + 1);
        t_gcd[trials] = snap_total(snap_sub(snap(), sg));
        dG = lG ? lG - 1 : 0; t_deg[trials] = dG;
        CTL(2);                                              /* the test deg G >= 1 */
        printf("trial %d centre %llu: gcd degree %zu, charged %llu\n", trials, (unsigned long long)i, dG, (unsigned long long)t_gcd[trials]); fflush(stdout);
        if (dG < 1) { if (G) xfree(G); continue; }
        stage_open("E: root isolation", trials); found = split_find_root(&S, G, dG);
        CTL(2);
        if (!found) continue;
        stage_open("F: map back", trials);
        snap_t s0 = snap();
        fp W1 = c, W2 = S;                           /* the root S of G is the second line parameter */
        map_back(&nk1, &rho1, &L, &W1);
        map_back(&nk2, &rho2, &L, &W2);
        bound_mem_since(s0);
        stage_open("G: verification (2 reference hashes)", trials);
        poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
        poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
        { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
        int same_dg = fp_eq(&dg1, &dg2);
        CTL(3 * 8 + 2 * 3 + 2);                              /* three four-limb equality tests (8 operations each), the two tests combined, the test that ends the search */
        success = found && same_dg && !same_in;
    }
    /* stage H: the output of the program, the two canonical pairs (and the digest and the centre), encoded in canonical hexadecimal */
    char hx[6][65];
    stage_open("H: canonical encoding of the output", 0);
    enc_hex(hx[0], &nk1); enc_hex(hx[1], &rho1); enc_hex(hx[2], &nk2); enc_hex(hx[3], &rho2); enc_hex(hx[4], &dg1); enc_hex(hx[5], &c);
    /* stage I: everything the program does after the last charged algorithm step is charged here, BEFORE the report is formatted, so that the one total printed
     * includes it.  All of it executes; none of it is left outside the total:
     *  - the stage bookkeeping of the closing of stage I (STAGE_BK);
     *  - the formatting and the copy of the whole report: every byte of the report is produced by the small printf of nolibc.c (vfmt) into the output buffer.
     *    The printf has no integer division, modulo or floating point: a decimal number is formed by comparing with the powers of ten and subtracting them (at most
     *    about 44 operations per digit produced, and at most about 100 for the scan for the leading power), the format scan, padding and copy loops cost at most about
     *    10 operations per byte, and the parse of a conversion specification and the fetch of its argument at most about 150 per conversion; a conversion produces at least
     *    one byte.  A byte therefore costs at most FMT_PER_BYTE = 400 operations, and the buffer holds at most OUTCAP bytes (the program exits with status 3 at the
     *    check below if it were fuller), so the formatting of the whole report is charged FMT_PER_BYTE * OUTCAP, whatever the report contains;
     *  - the loops of the report over the stages and trials and the sums: REPORT_LOOPS = 20000;
     *  - the process entry (_start, c_start: under 20 instructions) and the check of the buffer length: ENTRY_CHECK = 100;
     *  - the single write system call: SYS_WRITE = 10000 + 8 * OUTCAP (the instruction work of the call is about 10 instructions; the 8 per byte stands for the
     *    kernel copy of the buffer), and the single exit_group system call: SYS_EXIT = 10000.
     * There is no other system call in the run (no mmap, munmap, clock_gettime, or second write). */
#define FMT_PER_BYTE 400
#define REPORT_LOOPS 20000
#define ENTRY_CHECK 100
#define SYS_WRITE (10000 + (OUTCAP << 3))
#define SYS_EXIT 10000
    stage_open("I: report formatting, single write, exit", 0);
    CTL(STAGE_BK + (uint64_t)FMT_PER_BYTE * OUTCAP + REPORT_LOOPS + ENTRY_CHECK + SYS_WRITE + SYS_EXIT);
    stage_close();                                           /* from here on only the report of the counters is formatted into the buffer */
    printf("TRIALS %d\n", trials);
    uint64_t all = 0, arith = 0, trs = 0;
    for (int i = 0; i < nst; i++) { all += snap_total(st[i].d); arith += snap_arith(st[i].d); }
    for (int t = 0; t <= trials; t++) trs += trial_tot[t];
    uint64_t counters = snap_total(snap());
    for (int i = 0; i < nst; i++)
        printf("  %-40s arith=%12llu other=%12llu total=%12llu peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
               (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].peak);
    for (int t = 1; t <= trials; t++)
        printf("TRIALROW %d centre %llu degG %zu gcd %llu total %llu\n", t, (unsigned long long)t_centre[t], t_deg[t], (unsigned long long)t_gcd[t], (unsigned long long)trial_tot[t]);
    printf("TRIALROW 0 outside the trials (init, line setup, output encoding, report and write) total %llu\n", (unsigned long long)trial_tot[0]);
    printf("RECONCILE stages=%llu trials=%llu counters=%llu ok=%d\n", (unsigned long long)all, (unsigned long long)trs, (unsigned long long)counters, all == trs && trs == counters);
    printf("RESULT found=%d success=%d roots_degree=%zu\n", found, success, dG);
    printf("SPLIT levels=%llu tries=%llu shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)SPL_shift,
           (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    printf("SUMMARY total_all=%llu total_arith=%llu heap_peak=%zu\n", (unsigned long long)counters, (unsigned long long)arith, gpeak);
    printf("ARENA size=%zu extent=%zu\n", (size_t)ARENA, arena_hwm);
    printf("PEAKLIVE allocations=%zu payload=%zu headers=%zu\n", gpeak_live, gpeak_pay, gpeak_live * 64);
    { snap_t tt = snap();
      printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu\n", (unsigned long long)tt.add, (unsigned long long)tt.sub, (unsigned long long)tt.mul, (unsigned long long)tt.sqr,
             (unsigned long long)tt.ld, (unsigned long long)tt.st, (unsigned long long)tt.ctl, (unsigned long long)tt.rnd, (unsigned long long)tt.perm); }
    if (success) {
        printf("COLLISION nk1  0x%s\nCOLLISION rho1 0x%s\nCOLLISION nk2  0x%s\nCOLLISION rho2 0x%s\nCOLLISION digest 0x%s\nCOLLISION centre 0x%s\n", hx[0], hx[1], hx[2], hx[3], hx[4], hx[5]);
    }
    if (out_len > OUTCAP) return 3;
    out_flush();                                             /* the single write */
    return success ? 0 : 1;
}
