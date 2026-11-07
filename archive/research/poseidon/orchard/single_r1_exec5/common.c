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

/* Tracked allocation.  There is no C library and no allocator library: every buffer is a mapping of its own, taken from the kernel with mmap and given
 * back with munmap by xfree.  The mapping holds a 64-byte header (the payload size; it also keeps the payload 64-byte aligned) followed by the payload,
 * rounded up to whole 4 KiB pages.  The memory figure is the footprint: the bytes mapped from the kernel at the moment (headers and page rounding
 * included), checked after every allocation.  mem_cur is the payload alone (informational). */
size_t mem_live = 0, mem_peak_live = 0, mem_peak_pay = 0;
void *sys_map(size_t bytes);
void sys_unmap(void *p, size_t bytes);
static size_t mapped = 0;                              /* bytes currently mapped from the kernel */
static size_t map_size(size_t bytes) { return (bytes + 64 + 4095) & ~(size_t)4095; }
void *xalloc(size_t bytes) {
    size_t m = map_size(bytes);
    char *p = (char *)sys_map(m);
    if (!p) { fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    mapped += m;
    *(size_t *)p = bytes;
    mem_cur += bytes; mem_live++;
    if (mapped > mem_peak) { mem_peak = mapped; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
    return p + 64;
}
void xfree(void *q) {
    if (!q) return;
    char *p = (char *)q - 64; size_t bytes = *(size_t *)p;
    mem_cur -= bytes; mem_live--;
    size_t m = map_size(bytes); sys_unmap(p, m); mapped -= m;
}
void mem_reset_peak(void) { mem_peak = mapped; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
