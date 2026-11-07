/* Worker threads: process thread block (thread-local counters), clone, futex hand-over, chunk scheduling.  See par.h for the accounting rules.
 * No C library: the only system calls are arch_prctl (once, main thread block), clone (once per worker), futex (wait and wake), exit_group at the end.
 * Only the main thread calls xalloc / xfree, printf and the report; workers run the loop bodies handed to them and nothing else. */
#include "par.h"

int par_nt = 1;
__thread int par_in_job;
uint64_t thr_ctl, thr_disp, thr_chunks, thr_woken, thr_extra;

static inline long sys6(long n, long a, long b, long c, long d, long e, long f) {
    long r; register long r10 __asm__("r10") = d; register long r8 __asm__("r8") = e; register long r9 __asm__("r9") = f;
    __asm__ volatile("syscall" : "=a"(r) : "0"(n), "D"(a), "S"(b), "d"(c), "r"(r10), "r"(r8), "r"(r9) : "rcx", "r11", "memory");
    return r;
}
static void futex_wait(uint32_t *a, uint32_t v) { sys6(202, (long)a, 128, (long)v, 0, 0, 0); }      /* FUTEX_WAIT | FUTEX_PRIVATE_FLAG */
static void futex_wake(uint32_t *a, int n) { sys6(202, (long)a, 129, (long)n, 0, 0, 0); }          /* FUTEX_WAKE | FUTEX_PRIVATE_FLAG */

/* ---- thread blocks: the TLS segment of the executable (the counters fp_cnt and X) is laid out below the thread pointer (x86-64 variant II).  The program headers
 * give its size; every thread gets a zeroed block of that size in tlsb[] and its own thread pointer (the first word at the pointer holds the pointer itself). */
typedef struct { unsigned char e_ident[16]; uint16_t e_type, e_machine; uint32_t e_version; uint64_t e_entry, e_phoff, e_shoff; uint32_t e_flags;
                 uint16_t e_ehsize, e_phentsize, e_phnum, e_shentsize, e_shnum, e_shstrndx; } ehdr_t;
typedef struct { uint32_t p_type, p_flags; uint64_t p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align; } phdr_t;
extern const ehdr_t __ehdr_start;
static char tlsb[NT_MAX][TLS_MAXB] __attribute__((aligned(64)));
static char wstack[NT_MAX][WSTACK] __attribute__((aligned(64)));
static size_t tls_span;
static const phdr_t *tls_ph;
static ptrdiff_t off_f, off_x;                 /* offsets of fp_cnt and X from the thread pointer (same in every thread) */

static void tls_prepare(int id) {
    char *base = tlsb[id], *tp = base + tls_span;
    memset(base, 0, TLS_MAXB);
    if (tls_ph->p_filesz) memcpy(base, (const void *)tls_ph->p_vaddr, tls_ph->p_filesz);
    *(void **)tp = tp;
}
void par_tls_boot(void) {                      /* called first by the process entry, before any thread-local variable is touched */
    const ehdr_t *eh = &__ehdr_start;
    const phdr_t *ph = (const phdr_t *)((const char *)eh + eh->e_phoff);
    for (int i = 0; i < eh->e_phnum; i++) if (ph[i].p_type == 7) { tls_ph = &ph[i]; break; }
    if (!tls_ph) exit(11);
    size_t al = tls_ph->p_align ? tls_ph->p_align : 1;
    tls_span = (tls_ph->p_memsz + al - 1) & ~(al - 1);
    if (tls_span + 8 > TLS_MAXB || al > 64) exit(11);
    tls_prepare(0);
    sys6(158, 0x1002, (long)(tlsb[0] + tls_span), 0, 0, 0, 0);       /* arch_prctl(ARCH_SET_FS, thread pointer) */
}

/* ---- job hand-over */
typedef struct { par_fn fn; void *ctx; uint32_t nch; } job_t;
static job_t job[2];
static uint64_t ticket __attribute__((aligned(64)));        /* (sequence number << 32) | next chunk */
static uint32_t epoch __attribute__((aligned(64)));         /* futex word: sequence number of the latest dispatch */
static uint32_t finished __attribute__((aligned(64)));      /* chunks finished in the current dispatch */
static uint32_t main_wait __attribute__((aligned(64)));
static uint32_t seq_main;

static int grab(uint32_t seq, uint32_t *c) {
    for (;;) {
        uint64_t v = __atomic_load_n(&ticket, __ATOMIC_ACQUIRE);
        if ((uint32_t)(v >> 32) != seq) return 0;
        uint32_t k = (uint32_t)v;
        if (k >= job[seq & 1].nch) return 0;
        if (__atomic_compare_exchange_n(&ticket, &v, v + 1, 0, __ATOMIC_ACQ_REL, __ATOMIC_ACQUIRE)) { *c = k; return 1; }
    }
}
#ifdef PROF
static inline uint64_t prof_rdtsc(void) { uint32_t lo, hi; __asm__ volatile("rdtsc" : "=a"(lo), "=d"(hi)); return ((uint64_t)hi << 32) | lo; }
static uint64_t prof_busy_acc;
#endif
static void run_chunks(uint32_t seq) {
    uint32_t c;
    while (grab(seq, &c)) {
        par_fn fn = job[seq & 1].fn; void *ctx = job[seq & 1].ctx; uint32_t nch = job[seq & 1].nch;
#ifdef PROF
        uint64_t t0_ = prof_rdtsc();
#endif
        par_in_job = 1; fn(ctx, c); par_in_job = 0;
#ifdef PROF
        __atomic_add_fetch(&prof_busy_acc, prof_rdtsc() - t0_, __ATOMIC_RELAXED);
#endif
        uint32_t f = __atomic_add_fetch(&finished, 1, __ATOMIC_SEQ_CST);
        if (f == nch && __atomic_load_n(&main_wait, __ATOMIC_SEQ_CST)) futex_wake(&finished, 1);
    }
}
static void worker_main(void *arg) {
    (void)arg;
    uint32_t seen = 0;
    for (;;) {
        uint32_t e = __atomic_load_n(&epoch, __ATOMIC_ACQUIRE);
        if (e == seen) { futex_wait(&epoch, seen); continue; }
        seen = e;
        run_chunks(e);
    }
}

static long clone_thread(void *stack_top, void *tp, void (*entry)(void *), void *arg) {
    long ret;
    const long flags = 0x100 | 0x200 | 0x400 | 0x800 | 0x10000 | 0x40000 | 0x80000;   /* VM FS FILES SIGHAND THREAD SYSVSEM SETTLS */
    register long r10 __asm__("r10") = 0;
    register long r8 __asm__("r8") = (long)tp;
    register void *r12 __asm__("r12") = (void *)entry;
    register void *r13 __asm__("r13") = arg;
    __asm__ volatile(
        "syscall\n\t"
        "test %%rax, %%rax\n\t"
        "jnz 1f\n\t"
        "xor %%ebp, %%ebp\n\t"
        "mov %%r13, %%rdi\n\t"
        "call *%%r12\n\t"
        "mov $60, %%eax\n\t"
        "xor %%edi, %%edi\n\t"
        "syscall\n"
        "1:\n\t"
        : "=a"(ret)
        : "0"(56L), "D"(flags), "S"(stack_top), "d"(0L), "r"(r10), "r"(r8), "r"(r12), "r"(r13)
        : "rcx", "r11", "memory");
    return ret;
}

void par_init(int nt) {
    if (nt < 1) nt = 1;
    if (nt > NT_MAX) nt = NT_MAX;
    char *tp0 = tlsb[0] + tls_span;
    off_f = (char *)&fp_cnt - tp0; off_x = (char *)&X - tp0;
    if (off_f >= 0 || off_x >= 0 || -off_f > (ptrdiff_t)tls_span || -off_x > (ptrdiff_t)tls_span) exit(11);
    par_nt = nt;
    for (int id = 1; id < nt; id++) {
        tls_prepare(id);
        long r = clone_thread(wstack[id] + WSTACK, tlsb[id] + tls_span, worker_main, (void *)(intptr_t)id);
        if (r < 0) { par_nt = id; break; }
    }
}
void par_charge_setup(void) { if (par_nt > 1) THR_CHARGE((uint64_t)(par_nt - 1) * THR_SETUP_WORKER); }
size_t par_threadmem(int nt) { return (size_t)nt * (WSTACK + TLS_MAXB); }

void par_absorb(void) {
    for (int id = 1; id < par_nt; id++) {
        char *tp = tlsb[id] + tls_span;
        fp_counters *f = (fp_counters *)(tp + off_f); xcnt_t *x = (xcnt_t *)(tp + off_x);
        fp_cnt.add += f->add; fp_cnt.sub += f->sub; fp_cnt.mul += f->mul; fp_cnt.sqr += f->sqr;
        fp_cnt.inv_calls += f->inv_calls; fp_cnt.pow_calls += f->pow_calls; fp_cnt.sqrt_calls += f->sqrt_calls;
        X.ld += x->ld; X.st += x->st; X.ctl += x->ctl; X.rnd += x->rnd; X.perm += x->perm;
        memset(f, 0, sizeof *f); memset(x, 0, sizeof *x);
    }
}

par_plan_t par_plan(size_t total, int lmin, int lal) {
    par_plan_t p; p.w = 1; p.lcs = 0; p.cs = total ? total : 1; p.nch = 1;
    if (par_nt < 2) return p;
    THR_CHARGE(THR_PLAN);
    size_t cap = total >> lmin; int w = cap < (size_t)par_nt ? (int)cap : par_nt;
    if (w < 2) return p;
    size_t t4 = (size_t)w << 3; int lt = 0; while (((size_t)1 << lt) < t4) lt++;        /* ceil(log2(8 w)) */
    int lg = 0; while (((size_t)2 << lg) <= total) lg++;                                  /* floor(log2(total)) */
    int lcs = lg - lt; if (lcs < lal) lcs = lal;
    p.w = w; p.lcs = lcs; p.cs = (size_t)1 << lcs; p.nch = (total + p.cs - 1) >> lcs;
    if (p.nch < 2) { p.w = 1; p.nch = 1; p.cs = total ? total : 1; p.lcs = 0; }
    return p;
}

#ifdef PROF
static void prof_disp_begin(void);
static void prof_disp_end(int w);
#endif
static void par_run_(size_t nch, int w, par_fn fn, void *ctx);
void par_run(size_t nch, int w, par_fn fn, void *ctx) {
#ifdef PROF
    if (w > par_nt) w = par_nt;
    if (w < 2 || nch < 2) { par_run_(nch, w, fn, ctx); return; }
    prof_disp_begin(); par_run_(nch, w, fn, ctx); prof_disp_end(w);
#else
    par_run_(nch, w, fn, ctx);
#endif
}
static void par_run_(size_t nch, int w, par_fn fn, void *ctx) {
    if (w > par_nt) w = par_nt;
    if (w < 2 || nch < 2) { for (size_t c = 0; c < nch; c++) fn(ctx, c); return; }
    THR_CHARGE(THR_DISP_FIXED + (uint64_t)(w - 1) * THR_DISP_WORKER + (uint64_t)nch * THR_CHUNK + (uint64_t)(par_nt - 1) * THR_ABSORB);
    thr_disp++; thr_chunks += nch; thr_woken += (uint64_t)(w - 1);
    uint32_t seq = ++seq_main;
    job[seq & 1].fn = fn; job[seq & 1].ctx = ctx; job[seq & 1].nch = (uint32_t)nch;
    __atomic_store_n(&finished, 0, __ATOMIC_RELAXED);
    __atomic_store_n(&ticket, (uint64_t)seq << 32, __ATOMIC_RELEASE);
    __atomic_store_n(&epoch, seq, __ATOMIC_SEQ_CST);
    futex_wake(&epoch, w - 1);
    run_chunks(seq);
    for (;;) {
        uint32_t f = __atomic_load_n(&finished, __ATOMIC_ACQUIRE);
        if (f == nch) break;
        __atomic_store_n(&main_wait, 1, __ATOMIC_SEQ_CST);
        f = __atomic_load_n(&finished, __ATOMIC_SEQ_CST);
        if (f != nch) futex_wait(&finished, f);
        __atomic_store_n(&main_wait, 0, __ATOMIC_SEQ_CST);
    }
    par_absorb();
}

typedef struct { int op; fp *dst; const fp *a, *b, *c; size_t n; par_plan_t pl; } plctx_t;
static void pl_body(int op, fp *dst, const fp *a, const fp *b, const fp *c, size_t lo, size_t hi) {
    switch (op) {
    case PL_MULC:    for (size_t i = lo; i < hi; i++) fp_mul(&dst[i], &a[i], c); break;
    case PL_NEG:     for (size_t i = lo; i < hi; i++) fp_neg(&dst[i], &a[i]); break;
    case PL_SUB:     for (size_t i = lo; i < hi; i++) fp_sub(&dst[i], &a[i], &b[i]); break;
    default:         for (size_t i = lo; i < hi; i++) { fp t; fp_mul(&t, &a[i], c); fp_neg(&dst[i], &t); } break;
    }
}
static void job_pl(void *c_, size_t ch) { plctx_t *x = (plctx_t *)c_; pl_body(x->op, x->dst, x->a, x->b, x->c, par_lo(&x->pl, ch), par_hi(&x->pl, ch, x->n)); }
void pl_run(int op, fp *dst, const fp *a, const fp *b, const fp *c, size_t n) {
    if (par_big(n)) {
        par_plan_t pl = par_plan(n, PAR_LMIN_LIN, 3);
        if (pl.w >= 2) { plctx_t x; x.op = op; x.dst = dst; x.a = a; x.b = b; x.c = c; x.n = n; x.pl = pl; par_run(pl.nch, pl.w, job_pl, &x); return; }
    }
    pl_body(op, dst, a, b, c, 0, n);
}


#ifdef PROF
/* ---- wall-clock profile (profile builds only) */
static const char *prof_name[PR_N] = { "outside", "init", "line", "B points", "B ntt_inv", "B rest", "C newton", "C prefix", "C conv_sq", "C fold/copy/shift",
    "C otf mu (N)", "C otf g (N')", "C sub", "C mulx", "C rest", "D top (gcd loop)", "D hgcd own", "D base case", "D apply_inv", "D mat_mul", "D mat_mulQ", "D divrem", "E-I" };
typedef struct { uint64_t ser, wall, busy, capw, nd; } pacc_t;
static pacc_t pacc[PR_N][33];
static int pstk[512], pdep, astk[512], adep;
static uint64_t pseg, pdisp0;
static int pinit;
static uint64_t pt_wall0; static long pt_ns0;
static long prof_ns(void) { struct { long s, ns; } ts; sys6(228, 1, (long)&ts, 0, 0, 0, 0); return ts.s * 1000000000L + ts.ns; }
static void prof_boot(void) { if (pinit) return; pinit = 1; pseg = prof_rdtsc(); pt_wall0 = pseg; pt_ns0 = prof_ns(); pstk[0] = PR_OUT; pdep = 1; astk[0] = 0; adep = 1; }
static inline pacc_t *pcur(void) { return &pacc[pstk[pdep - 1]][astk[adep - 1]]; }
static void pseg_close(void) { uint64_t t = prof_rdtsc(); pcur()->ser += t - pseg; pseg = t; }
void prof_push(int r) { prof_boot(); pseg_close(); if (pdep < 512) pstk[pdep++] = r; }
void prof_pop(void) { prof_boot(); pseg_close(); if (pdep > 1) pdep--; }
void prof_apush(int a) { prof_boot(); pseg_close(); if (adep < 512) astk[adep++] = a; }
void prof_apop(void) { prof_boot(); pseg_close(); if (adep > 1) adep--; }
void prof_stage(int r) { prof_boot(); pseg_close(); pstk[0] = r; pdep = 1; adep = 1; }
static void prof_disp_begin(void) { prof_boot(); pseg_close(); pdisp0 = pseg; __atomic_store_n(&prof_busy_acc, 0, __ATOMIC_RELAXED); }
static void prof_disp_end(int w) {
    uint64_t t = prof_rdtsc(), d = t - pdisp0; pacc_t *a = pcur();
    a->wall += d; a->busy += __atomic_load_n(&prof_busy_acc, __ATOMIC_RELAXED); a->capw += d * (uint64_t)w; a->nd++; pseg = t;
}
static void pr_u(const char *s, uint64_t v) { fprintf(stderr, "%s%llu", s, (unsigned long long)v); }
void prof_report(const char *tag) {
    prof_boot(); pseg_close();
    uint64_t tsc = prof_rdtsc() - pt_wall0; long ns = prof_ns() - pt_ns0;
    uint64_t mhz = ns > 0 ? (uint64_t)((tsc / 1000) * 1000000ULL / (uint64_t)(ns / 1000 > 0 ? ns / 1000 : 1)) / 1000 : 0;   /* cycles per microsecond */
    fprintf(stderr, "PROF %s threads=%d tsc_mhz=%llu wall_ms=%llu\n", tag, par_nt, (unsigned long long)mhz, (unsigned long long)(ns / 1000000));
    fprintf(stderr, "PROF cols: region a ser_ms disp_ms busy_ms capw_ms ndisp\n");
    for (int r = 0; r < PR_N; r++) for (int a = 0; a < 33; a++) {
        pacc_t *p = &pacc[r][a]; if (!p->ser && !p->wall) continue;
        uint64_t k = mhz ? mhz * 1000 : 1;    /* cycles per ms */
        fprintf(stderr, "PROFROW %s|%d", prof_name[r], a);
        pr_u("|", p->ser / k); pr_u("|", p->wall / k); pr_u("|", p->busy / k); pr_u("|", p->capw / k); pr_u("|", p->nd); fprintf(stderr, "\n");
    }
}
#endif
