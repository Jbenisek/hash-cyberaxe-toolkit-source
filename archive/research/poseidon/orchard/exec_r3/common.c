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

/* Tracked allocation.  Every buffer comes from xalloc: a 64-byte header (it holds the payload size and keeps the payload 64-byte aligned) is placed
 * in front of the payload.  The memory figure is the footprint of the C allocator, read with mallinfo2() right after every allocation: the bytes the
 * allocator holds from the system (arena = brk heap, hblkhd = mmapped blocks).  It therefore contains the 64-byte headers, the allocator's own chunk
 * headers, alignment padding, page rounding and the unreleased top of the heap.  mem_cur is the payload alone (informational). */
#include <malloc.h>
size_t mem_live = 0, mem_peak_live = 0, mem_peak_pay = 0;
static size_t foot(void) { struct mallinfo2 mi = mallinfo2(); return (size_t)mi.arena + (size_t)mi.hblkhd; }
void *xalloc(size_t bytes) {
    void *p = NULL;
    if (posix_memalign(&p, 64, bytes + 64)) { fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    *(size_t *)p = bytes;
    mem_cur += bytes; mem_live++;
    size_t f = foot();
    if (f > mem_peak) { mem_peak = f; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
    return (char *)p + 64;
}
void xfree(void *q) {
    if (!q) return;
    void *p = (char *)q - 64; mem_cur -= *(size_t *)p; mem_live--; free(p);
}
void mem_reset_peak(void) { mem_peak = foot(); mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
