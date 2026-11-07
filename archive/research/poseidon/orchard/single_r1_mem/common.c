#include "common.h"
xcnt_t X;
size_t mem_cur = 0, mem_peak = 0;

snap_t snap(void) {
    snap_t s; s.add = fp_cnt.add; s.sub = fp_cnt.sub; s.mul = fp_cnt.mul; s.sqr = fp_cnt.sqr;
    s.ld = X.ld; s.st = X.st; s.ctl = X.ctl; s.rnd = X.rnd; s.perm = X.perm; return s;
}
snap_t snap_sub(snap_t a, snap_t b) {
    snap_t s; s.add = a.add - b.add; s.sub = a.sub - b.sub; s.mul = a.mul - b.mul; s.sqr = a.sqr - b.sqr;
    s.ld = a.ld - b.ld; s.st = a.st - b.st; s.ctl = a.ctl - b.ctl; s.rnd = a.rnd - b.rnd; s.perm = a.perm - b.perm; return s;
}
uint64_t snap_arith(snap_t s) { return s.add + s.sub + s.mul + s.sqr; }
uint64_t snap_total(snap_t s) { return snap_arith(s) + s.ld + s.st + s.ctl + s.rnd + s.perm; }
void snap_restore(snap_t s) {
    fp_cnt.add = s.add; fp_cnt.sub = s.sub; fp_cnt.mul = s.mul; fp_cnt.sqr = s.sqr;
    X.ld = s.ld; X.st = s.st; X.ctl = s.ctl; X.rnd = s.rnd; X.perm = s.perm;
}

/* tracked allocation: a 64-byte header holds the size */
#ifdef MEMTRACE
typedef struct { void *p; size_t sz; void *ra; } lv_t;
static lv_t live[4096], snapv[4096]; static int nlive, nsnap; static size_t snap_peak;
#endif
void *xalloc(size_t bytes) {
    void *p = NULL;
    if (posix_memalign(&p, 64, bytes + 64)) { fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    *(size_t *)p = bytes;
    mem_cur += bytes; if (mem_cur > mem_peak) mem_peak = mem_cur;
#ifdef MEMTRACE
    live[nlive].p = (char *)p + 64; live[nlive].sz = bytes; live[nlive].ra = __builtin_return_address(0); nlive++;
    if (mem_cur > snap_peak) { snap_peak = mem_cur; memcpy(snapv, live, nlive * sizeof(lv_t)); nsnap = nlive; }
#endif
    return (char *)p + 64;
}
void xfree(void *q) {
    if (!q) return;
    void *p = (char *)q - 64; mem_cur -= *(size_t *)p;
#ifdef MEMTRACE
    for (int i = 0; i < nlive; i++) if (live[i].p == q) { live[i] = live[--nlive]; break; }
#endif
    free(p);
}
void mem_reset_peak(void) { mem_peak = mem_cur; }

#ifdef MEMTRACE
void mem_report(void) {
    fprintf(stderr, "MEMTRACE snapshot at peak %zu\n", snap_peak);
    for (int i = 0; i < nsnap; i++) fprintf(stderr, "  %10zu B  %9zu el  ra=%p\n", snapv[i].sz, snapv[i].sz / 32, snapv[i].ra);
}
#endif
