/* Fork-join worker threads for the counted program (no C library: raw clone / futex system calls, nolibc.c / par.c).
 *
 * What the threads change and what they do not.  The program is the same algorithm executing the same charged operations; the charged operations of a loop
 * that is split among threads are executed, and counted, by the thread that executes them (every thread has its own private counters: pallas.h, common.h),
 * and the main thread adds the counters of all threads into its own after every dispatch, so the counters of the program are always the exact sum over all
 * threads.  A loop is split so that its charges are the same as when one thread runs it (the control charges of the whole loop are charged once, by the main
 * thread, before the split; the charges of one iteration stay with the iteration).  With one thread (the second argument of the program is 1, or absent)
 * nothing below executes and the program is the single-thread program.
 *
 * Thread control is charged as executed, in addition (common.h THR_*): creating a worker (one clone system call and the setup of its stack and thread block),
 * and per dispatch the system calls of the hand-over (a worker returns from one futex wait system call, the main thread makes one wake call and at most one wait
 * call, the last finishing worker at most one wake call; one system call = 10000 operations as everywhere in this program) and the control operations of the
 * hand-over and of the chunk scheduling.  Only the main thread allocates or frees memory; the workers allocate nothing (their stacks and thread blocks are
 * static, reported as THREADMEM).  These charges are tallied separately (thr_ctl) and are part of the control count of the stage in which they are executed. */
#ifndef PAR_H
#define PAR_H
#include "common.h"

#define NT_MAX 96
#define WSTACK 16384                 /* bytes of stack of each worker (static, in .bss); the deepest use measured in a full run is under 2,048 bytes */
#define TLS_MAXB 512                 /* bytes reserved for the thread block of each thread (counters, 128 bytes used) */

extern int par_nt;
extern __thread int par_in_job;       /* 1 while this thread runs a chunk of a dispatch: nothing is split further */                   /* number of threads including the main thread (1: single-thread program) */
extern uint64_t thr_ctl;             /* operations charged as thread control (inside X.ctl) */
extern uint64_t thr_disp, thr_chunks, thr_woken, thr_extra;   /* dispatches, chunks run, workers woken (bound), operations executed only because the work is split (inside the counters) */

void par_init(int nt);               /* create nt - 1 workers (not charged here: call par_charge_setup after the counters are reset) */
void par_charge_setup(void);         /* charge the creation of the workers */
size_t par_threadmem(int nt);

typedef void (*par_fn)(void *ctx, size_t chunk);
/* run chunks 0 .. nch-1 of fn(ctx, chunk) on up to w threads (the main thread included); returns when all are done and the counters are summed */
void par_run(size_t nch, int w, par_fn fn, void *ctx);

typedef struct { int w; int lcs; size_t cs, nch; } par_plan_t;
/* plan a loop of `total` items: a thread is used for every 2^lmin items (w = min(par_nt, total >> lmin)); chunks are 2^lcs items (lcs >= lal), 8 to 16 per thread.
 * w < 2: the caller runs the loop itself.  The planning is a few shifts and comparisons, charged as thread control when more than one thread exists. */
par_plan_t par_plan(size_t total, int lmin, int lal);
static inline size_t par_lo(const par_plan_t *p, size_t c) { return c << p->lcs; }
static inline size_t par_hi(const par_plan_t *p, size_t c, size_t total) { size_t h = (c + 1) << p->lcs; return h < total ? h : total; }

/* A loop or pass is split only when it has at least PAR_MIN_N elements, and one thread is used per 2^PAR_LMIN_ELEM elements (the cost of one dispatch is then a small
 * fraction of the work of every thread that joins).  The test is 2 operations of thread control. */
#ifndef PAR_MIN_N
#define PAR_MIN_N ((size_t)1 << 14)
#endif
#ifndef PAR_LMIN_ELEM
#define PAR_LMIN_ELEM 13          /* butterfly passes (about 15 operations per element and pass): one thread per 2^13 elements of a row (exec_r6mt: 2^15) */
#endif
#ifndef PAR_LMIN_LIN
#define PAR_LMIN_LIN 15           /* linear loops (3 to 10 operations per element): one thread per 2^15 elements (exec_r6mt: 2^17) */
#endif
/* the control charge of a FOR8 loop over n elements (common.h FOR8), charged once; the bodies are charged by whoever runs them */
static inline void for8_ctl(size_t n) { size_t n8 = n & ~(size_t)7; CTL(1 + 3 * (n8 >> 3) + 2 + 3 * (n - n8) + 2); }

/* Element loops with a field operation per element (the charges of the loop control, loads and stores stay with the caller, as in the sequential code; only the
 * field operations are executed, and counted, here): PL_MULC: dst[i] = a[i] * (*c); PL_NEG: dst[i] = -a[i]; PL_SUB: dst[i] = a[i] - b[i];
 * PL_NEGMULC: dst[i] = -(a[i] * (*c)).  dst may be a (same index only).  Split among threads when n is large. */
enum { PL_MULC = 0, PL_NEG = 1, PL_SUB = 2, PL_NEGMULC = 3 };
void pl_run(int op, fp *dst, const fp *a, const fp *b, const fp *c, size_t n);

/* the counters of a worker, summed into the main thread's after a dispatch */
void par_absorb(void);

/* charges of the thread control (operations; one system call is 10000 as for the write and exit_group of the report, nolibc.c / single.c stage I).
 * A dispatch: the main thread makes one futex wake call, at most one futex wait call, and the last finishing worker at most one wake call (3 system calls); every
 * worker that is woken returns from one futex wait call (1 system call) and takes about 150 control operations (read of the job, loop, call, atomic add, test);
 * the kernel work of waking and scheduling a worker is charged THR_KWAKE = 1000 more.  Every chunk costs the thread that runs it THR_CHUNK = 14 control
 * operations (load of the ticket, two tests, compare-and-swap, call, atomic increment, test).  After every dispatch the main thread adds the counters of the
 * other threads into its own: THR_ABSORB = 45 operations per other thread (14 loads, 14 additions, 14 stores of zero, 3 of loop control). */
#define THR_SYSCALL 10000
#define THR_KWAKE 1000
#define THR_DISP_FIXED (3 * THR_SYSCALL + 300)
#define THR_DISP_WORKER (THR_SYSCALL + THR_KWAKE + 150)
#define THR_CHUNK 14
#define THR_ABSORB 45
#define THR_PLAN 200       /* par_plan: two bit-scan loops of at most 64 + 8 iterations of about 3 operations, and about 20 more */
#define THR_SETUP_WORKER (THR_SYSCALL + 1000)   /* creating one worker: one clone system call, the setup of its stack, thread block and counters */
/* thread-control charge (also into thr_ctl) */
#define THR_CHARGE(n) do { uint64_t n_ = (uint64_t)(n); X.ctl += n_; thr_ctl += n_; } while (0)
static inline int par_big(size_t n) { if (par_nt < 2 || par_in_job) return 0; THR_CHARGE(2); return n >= PAR_MIN_N; }

/* Wall-clock profile (profile builds only, -DPROF; the counted build compiles none of it: every macro below is empty).  Main-thread time is split into serial
 * segments and dispatch segments, by region and by transform row length (log2). */
#ifdef PROF
enum { PR_OUT, PR_INIT, PR_LINE, PR_B_PTS, PR_B_NTT, PR_B_REST, PR_C_NEWTON, PR_C_PREFIX, PR_C_SQ, PR_C_LL, PR_C_MU, PR_C_G, PR_C_SUB, PR_C_MULX, PR_C_REST,
       PR_D_TOP, PR_D_HGCD, PR_D_BASE, PR_D_APPLY, PR_D_MATMUL, PR_D_MULQ, PR_D_DIV, PR_E_I, PR_N };
void prof_push(int r); void prof_pop(void); void prof_apush(int a); void prof_apop(void); void prof_stage(int r); void prof_report(const char *tag);
#define PROF_PUSH(r) do { if (!par_in_job) prof_push(r); } while (0)
#define PROF_POP() do { if (!par_in_job) prof_pop(); } while (0)
#define PROF_A(a) do { if (!par_in_job) prof_apush(a); } while (0)
#define PROF_AEND() do { if (!par_in_job) prof_apop(); } while (0)
#define PROF_STAGE(r) prof_stage(r)
#define PROF_REPORT(t) prof_report(t)
#else
#define PROF_PUSH(r) ((void)0)
#define PROF_POP() ((void)0)
#define PROF_A(a) ((void)0)
#define PROF_AEND() ((void)0)
#define PROF_STAGE(r) ((void)0)
#define PROF_REPORT(t) ((void)0)
#endif
#endif
