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
void *xalloc(size_t bytes) {
    void *p = NULL;
    if (posix_memalign(&p, 64, bytes + 64)) { fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    *(size_t *)p = bytes;
    mem_cur += bytes; if (mem_cur > mem_peak) mem_peak = mem_cur;
    return (char *)p + 64;
}
void xfree(void *q) {
    if (!q) return;
    void *p = (char *)q - 64; mem_cur -= *(size_t *)p; free(p);
}
void mem_reset_peak(void) { mem_peak = mem_cur; }

static uint64_t bud_limit = 0; static snap_t bud_start; static const char *bud_stage = ""; static uint64_t bud_last = 0, bud_maxgap = 0;
void budget_arm(uint64_t limit, const char *stage) { bud_limit = limit; bud_start = snap(); bud_stage = stage; bud_last = 0; bud_maxgap = 0; }
uint64_t budget_maxgap(void) { return bud_maxgap; }
void budget_check(void) {
    if (!bud_limit) return;
    X.ctl += 2;
    uint64_t cur = snap_total(snap_sub(snap(), bud_start));
    if (cur - bud_last > bud_maxgap) bud_maxgap = cur - bud_last;
    bud_last = cur;
    if (cur > bud_limit) {
        printf("BUDGET HALT in stage %s: charged work %llu exceeded %llu", bud_stage, (unsigned long long)cur, (unsigned long long)bud_limit);
        putchar(10);
        fflush(stdout); exit(77);
    }
}

/* shrink an xalloc'ed block in place (realloc to a smaller size); accounting follows the new size */
void *xshrink(void *q, size_t bytes) {
    char *p = (char *)q - 64; size_t old = *(size_t *)p;
    if (bytes >= old) return q;
    char *np = realloc(p, bytes + 64);
    if (!np) np = p; else p = np;
    *(size_t *)p = bytes; mem_cur -= old - bytes;
    return p + 64;
}
