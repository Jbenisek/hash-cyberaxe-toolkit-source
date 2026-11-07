/* Low-memory x^E mod g (g monic, degree m): one transform buffer Y (3*2^a slots), one transform row, g, mu and a fold buffer.
 * No stored spectra: the spectra of mu' and g are regenerated row by row for every multiplication (conv_mulc_otf).
 * State s = a/N as in loop.c (N = size of the big plan), so no scaling of the state is ever needed.
 *   Y := conv_sq(s)                      = T/N                  (T = a^2)
 *   F := T/N folded modulo x^N'-1 (first m coefficients)        saved
 *   Y := T1/N = coefficients m..2m-2 of T/N moved to 0..m-2
 *   Y := conv(T1/N, mu'')                = q/(N N')             mu'' = x^(N-m+2) mu /(N N') (cyclic, window at 0..m-2)
 *   Y := conv_N'(q/(N N'), g)            = (q g mod x^N'-1)/N
 *   Y := F - Y                           = a_new/N              (N' >= m) */
#include "common.h"
#include "par.h"

static int ebit(const uint64_t E[4], int i) { return (int)((E[i >> 6] >> (i & 63)) & 1); }   /* word index by a shift, bit index by a mask; charged 7 at each use: shift, mask, address, load, shift, and, return */

/* ---- the linear loops of one squaring step (and mulx_), split among threads when long.  The control of a loop (for8_ctl, the FOR8 charge) is charged once by the
 * calling thread; the body of an iteration (loads, store, field operations) is charged by the thread that runs it, so the sum is the same as for one thread.
 * mulx_ reads Y[i-1] while writing Y[i] downwards: before the split the main thread saves the value each chunk reads from the next chunk's range
 * (one load and one store each, executed only because the loop is split: tallied in thr_extra and charged). */
enum { LL_FOLD, LL_COPY, LL_SHIFT, LL_SUB, LL_MULX };
typedef struct { int op; fp *F, *Y; const fp *G; size_t Np, m, lim, n; fp c; par_plan_t pl; fp *bsave; } llctx_t;
static void ll_body(const llctx_t *a, size_t lo, size_t hi, const fp *first_prev) {
    fp *F = a->F, *Y = a->Y; const fp *G = a->G; size_t m = a->m;
    switch (a->op) {
    case LL_FOLD:  { size_t Np = a->Np; for (size_t i = lo; i < hi; i++) { fp_add(&F[i], &Y[i], &Y[i + Np]); LD(2); ST(1); } break; }
    case LL_COPY:  { size_t lim = a->lim; for (size_t j = lo; j < hi; j++) { size_t i = lim + j; F[i] = Y[i]; LD(1); ST(1); } break; }
    case LL_SHIFT: for (size_t i = lo; i < hi; i++) { Y[i] = Y[m + i]; LD(1); ST(1); } break;
    case LL_SUB:   for (size_t i = lo; i < hi; i++) { fp_sub(&Y[i], &F[i], &Y[i]); LD(2); ST(1); } break;
    default: {     /* LL_MULX: j = lo .. hi-1 is i = m-1-j downwards; the lowest i of the chunk reads Y[i-1] from first_prev when given */
        fp c = a->c;
        for (size_t j = lo; j < hi; j++) {
            size_t i = m - 1 - j; fp t; fp_mul(&t, &c, &G[i]);
            if (j + 1 == hi && first_prev) fp_sub(&Y[i], first_prev, &t); else fp_sub(&Y[i], &Y[i - 1], &t);
            LD(2); ST(1);
        }
        break; }
    }
}
static void job_ll(void *c_, size_t ch) {
    const llctx_t *a = (const llctx_t *)c_;
    size_t lo = par_lo(&a->pl, ch), hi = par_hi(&a->pl, ch, a->n);
    ll_body(a, lo, hi, a->op == LL_MULX ? &a->bsave[ch] : NULL);
}
static void ll_run(llctx_t *a) {
    for8_ctl(a->n);
    if (par_big(a->n)) {
        par_plan_t pl = par_plan(a->n, PAR_LMIN_LIN, 3);
        if (pl.w >= 2 && pl.nch <= 2048) {
            a->pl = pl;
            if (a->op == LL_MULX) {
                for (size_t ch = 0; ch < pl.nch; ch++) {              /* the value Y[i-1] read by the lowest i of each chunk, taken before any chunk writes */
                    size_t hi = par_hi(&pl, ch, a->n), i = a->m - 1 - (hi - 1);
                    a->bsave[ch] = a->Y[i - 1];
                }
                X.ld += pl.nch; X.st += pl.nch; X.ctl += 2 * pl.nch; thr_extra += 4 * pl.nch;
            }
            par_run(pl.nch, pl.w, job_ll, a);
            return;
        }
    }
    ll_body(a, 0, a->n, NULL);
}
static fp mulx_save[2048];
static void mulx_(fp *Y, const fp *G, size_t m) {
    fp c = Y[m - 1]; LD(1);
    llctx_t a; a.op = LL_MULX; a.F = NULL; a.Y = Y; a.G = G; a.Np = 0; a.m = m; a.lim = 0; a.n = m - 1; a.c = c; a.bsave = mulx_save;
    ll_run(&a);
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&Y[0], &t); LD(1); ST(1);
}

/* MU[0..m-2] = floor(x^(2m-2)/g); GR (>= m-1 slots) and Y, tmp are scratch */
static void newton_lean(fp *MU, const fp *g, size_t m, fp *GR, fp *Y, fp *tmp) {
    size_t L = m - 1;
    for (size_t i = 0; i < L; i++) GR[i] = g[m - i];
    LD(L); ST(L); loopc(L); CTL(L);              /* index m - i */
    fp one; fp_set_one(&one);
    CTL(4 + 8);                                  /* fp_eq: four limb comparisons (8 operations), compare, branch; setup */
    if (!fp_eq(&GR[0], &one)) { fprintf(stderr, "newton: g not monic\n"); exit(6); }
    MU[0] = one; ST(1);
    size_t l = 1;
    while (l < L) {
        size_t l2 = 2 * l < L ? 2 * l : L;
        CTL(3 + 3 + 2);                          /* loop test, 2*l, compare, select */
        plan_t P1 = plan3_for_len(l2 + l - 1);
        conv_mulc_otf(&P1, Y, MU, 0, l, tmp, GR, l2, 0, l2);
        fp inv1; plan_invN(&P1, &inv1);
        pl_run(PL_MULC, Y, Y + l, NULL, &inv1, l2 - l);
        LD(l2 - l); ST(l2 - l); loopc(l2 - l); CTL(l2 - l);          /* index l + i */
        plan_t P2 = plan3_for_len(l2 - 1);
        conv_mulc_otf(&P2, Y, Y, 0, l2 - l, tmp, MU, l, 0, l2 - l);
        fp inv2; plan_invN(&P2, &inv2);
        pl_run(PL_NEGMULC, MU + l, Y, NULL, &inv2, l2 - l);
        LD(l2 - l); ST(l2 - l); loopc(l2 - l); CTL(l2 - l);          /* index l + i */
        l = l2;
    }
    for (size_t i = 0; i < L / 2; i++) { fp t = MU[i]; MU[i] = MU[L - 1 - i]; MU[L - 1 - i] = t; }
    LD(L); ST(L); loopc(L / 2); CTL(2 * (L / 2));       /* L/2 iterations; index L - 1 - i twice (two operations each) */
}

/* F (m slots, caller-owned) receives x^E mod g; it is also used as scratch.  Allocates Y, tmp, MU through xalloc. */
void powx_lean(fp *F, const fp *g, size_t m, const uint64_t E[4], int quiet) {
    plan_t PN = plan3_for_len(2 * m - 1), PNp = plan3_for_len(m + 1);
    size_t N = PN.N, Np = PNp.N;
    fp *Y = NEW_FP(N), *tmp = NEW_FP(PN.n), *MU = NEW_FP(m - 1);
    snap_t sA = snap();
    PROF_PUSH(PR_C_NEWTON); newton_lean(MU, g, m, F, Y, tmp); PROF_POP(); PROF_PUSH(PR_C_PREFIX);
    snap_t sB = snap();
    {
        fp i1, i2, sc; plan_invN(&PN, &i1); plan_invN(&PNp, &i2); fp_mul(&sc, &i1, &i2);
        pl_run(PL_MULC, MU, MU, NULL, &sc, m - 1);
        LD(m - 1); ST(m - 1); loopc(m - 1);
    }
    size_t gamma = N - (m - 2);
#ifdef CACHED_POW
    /* cached spectra: of mu'' (window at offset gamma, N slots) and of g (N' slots); the compact mu and the transform row are then released */
    fp *MUH = NEW_FP(N), *GH = NEW_FP(Np);
    ntt_fwd_shifted(&PN, MUH, MU, m - 1, gamma);
    ntt_fwd(&PNp, GH, g, 0, m + 1);
    xfree(MU); MU = NULL; xfree(tmp); tmp = NULL;
#endif
    int top = 255; while (top > 0 && !ebit(E, top)) { top--; CTL(3 + 7 + 2); }      /* loop, ebit (7: shift, mask, address, load, shift, and, return), test */
    size_t v = 1; int bit = top;
    while (bit >= 1 && ((v << 1) | (size_t)ebit(E, bit - 1)) < m) { v = (v << 1) | (size_t)ebit(E, bit - 1); bit--; CTL(3 + 2 * 7 + 2 + 2 + 3 + 1); }   /* loop, ebit twice, two shifts/ors, compare with m, branch, bit-- */
    for (size_t i = 0; i < m; i++) fp_set_zero(&Y[i]);
    ST(m); loopc(m);
    { fp invN; plan_invN(&PN, &invN); Y[v] = invN; ST(1); }
    snap_t sC = snap();
    PROF_POP();
    int steps = 0;
    for (int b = bit - 1; b >= 0; b--) {
        PROF_PUSH(PR_C_SQ); conv_sq(&PN, Y, m, 2 * m - 1); PROF_POP();
        PROF_PUSH(PR_C_LL);
        size_t lim = 2 * m - 2 >= Np ? 2 * m - 2 - Np + 1 : 0; if (lim > m) lim = m; CTL(8);   /* positions i < lim fold Y[i + Np]; the rest are copies */
        { llctx_t a; a.F = F; a.Y = Y; a.G = NULL; a.Np = Np; a.m = m; a.lim = lim; a.bsave = NULL;
          a.op = LL_FOLD; a.n = lim; ll_run(&a);
          a.op = LL_COPY; a.n = m - lim; ll_run(&a);
          a.op = LL_SHIFT; a.n = m - 1; ll_run(&a); }
        PROF_POP();
#ifdef CACHED_POW
        conv_mulc(&PN, Y, Y, 0, m - 1, MUH, m - 1);
        conv_mulc(&PNp, Y, Y, 0, m - 1, GH, m);
#else
        PROF_PUSH(PR_C_MU); conv_mulc_otf(&PN, Y, Y, 0, m - 1, tmp, MU, m - 1, gamma, m - 1); PROF_POP();
        PROF_PUSH(PR_C_G); conv_mulc_otf(&PNp, Y, Y, 0, m - 1, tmp, g, m + 1, 0, m); PROF_POP();
#endif
        PROF_PUSH(PR_C_SUB); { llctx_t a; a.F = F; a.Y = Y; a.G = NULL; a.Np = Np; a.m = m; a.lim = 0; a.bsave = NULL; a.op = LL_SUB; a.n = m; ll_run(&a); } PROF_POP();
        PROF_PUSH(PR_C_MULX); if (ebit(E, b)) mulx_(Y, g, m); PROF_POP();
        CTL(3 + 7 + 2 + 2);                  /* loop, ebit (7), if, steps++ and the quiet test */
        steps++;
        CTL(6);
        if (!quiet && (steps & 31) == 0) fprintf(stderr, "  lean step %d/%d\n", steps, bit);
    }
    { fp Nf; uint64_t vv[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, vv);
      pl_run(PL_MULC, F, Y, NULL, &Nf, m);
      LD(m); ST(m); loopc(m); }
    CTL(2);                                      /* test of quiet */
    if (quiet == 2) {
        snap_t n_ = snap_sub(sB, sA), l_ = snap_sub(snap(), sC), p_ = snap_sub(sC, sB);
        printf("lean-pow breakdown: newton total=%llu arith=%llu | prefix+scale total=%llu | loop steps=%d total=%llu arith=%llu",
               (unsigned long long)snap_total(n_), (unsigned long long)snap_arith(n_), (unsigned long long)snap_total(p_), steps,
               (unsigned long long)snap_total(l_), (unsigned long long)snap_arith(l_));
        putchar(10);
    }
    CTL(500);                                    /* the four snapshots of the counters (sA, sB, sC and the one in the report branch) and the report branch: bound 500 (4 x 9 loads, 3 subtractions of 9) */
#ifdef CACHED_POW
    xfree(MUH); xfree(GH); xfree(Y);
#else
    xfree(Y); xfree(tmp); xfree(MU);
#endif
}
