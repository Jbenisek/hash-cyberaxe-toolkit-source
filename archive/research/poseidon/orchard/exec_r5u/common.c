#include "common.h"
__thread xcnt_t X;
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

/* Allocation from ONE static arena in .bss (no mmap, no munmap, no other system call).  The arena is ARENA bytes (a multiple of 64, set in common.h; it is part of the
 * executable image, so the memory figure is the whole image from `size`; the run reports the highest end address of any block, `extent`).  It is a sequence
 * of blocks laid end to end; every block starts with a 64-byte header { size = the block's bytes including the header, prev = size of the block before it
 * (0 for the first), used = 0 or 1 } and the payload follows (64-byte aligned; the block size is 64 + the payload rounded up to a multiple of 64).
 * xalloc: a large block (more than SMALL_BLOCK bytes, header included) takes the first fit in address order and is cut from the bottom of that free block; a small block takes the last fit and is cut from the top of that free block (this keeps the large buffers together and leaves less unusable space between them than plain first fit); a block is split when the remainder is at least 128 bytes.  xfree: the block is marked free and merged with a free
 * neighbour on either side.  Every executed operation of both functions is charged where it is written, with the rule of common.h: ldz / stz = one load /
 * store plus one address operation; CTL(2) = one comparison plus its branch; CTL(1) = one add / sub / and / assignment of a register.  The statistics lines
 * (bytes in use, live blocks, peaks, extent) are charged a flat ALLOC_STATS = 64 per call (they are at most 6 loads, 6 stores, 8 adds and 4 compare-branch
 * pairs = 6*2 + 6*2 + 8 + 8 = 40 operations).  The first call also writes the header of the single initial free block (charged). */
size_t mem_live = 0, mem_peak_live = 0, mem_peak_pay = 0, mem_used = 0, arena_hwm = 0;
typedef struct { size_t size, prev, used; char pad[40]; } bhdr_t;
static char arena[ARENA] __attribute__((aligned(64)));
static int arena_ready = 0;
#define ALLOC_STATS 64
#define SMALL_BLOCK 134217728          /* blocks of at most this many bytes (header included) are placed from the top of the free space, larger ones from the bottom */
static inline size_t ldz(const size_t *p) { X.ld++; X.ctl++; return *p; }
static inline void stz(size_t *p, size_t v) { X.st++; X.ctl++; *p = v; }
void *xalloc(size_t bytes) {
    CTL(2); if (!arena_ready) { bhdr_t *h0 = (bhdr_t *)arena; stz(&h0->size, ARENA); stz(&h0->prev, 0); stz(&h0->used, 0); arena_ready = 1; X.st++; X.ctl++; }
    size_t need = 64 + ((bytes + 63) & ~(size_t)63); CTL(4);
    int small = need <= SMALL_BLOCK; CTL(2);         /* comparison with the small-block limit, assignment */
    char *p = arena, *cand = NULL; size_t csz = 0; CTL(3);
    for (;;) {                                        /* walk the blocks in address order */
        CTL(2); if (p >= arena + ARENA) break;
        bhdr_t *h = (bhdr_t *)p;
        size_t b = ldz(&h->size), u = ldz(&h->used);
        CTL(4); if (!u && b >= need) { cand = p; csz = b; CTL(2); if (!small) break; }   /* fits: remember it; a large block takes the first fit, a small block the last */
        p += b; CTL(3);                               /* advance, loop back */
    }
    CTL(2); if (!cand) {
        fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    p = cand; size_t sz = csz;
    bhdr_t *h = (bhdr_t *)p;
    size_t rem = sz - need; CTL(3);                   /* subtraction, comparison, branch */
    if (rem >= 128) {
        char *nn = p + sz; CTL(3);                    /* end of the block, comparison with the arena end, branch */
        if (small) {                                  /* small block: carved from the TOP of the free block; the free part keeps the header h */
            bhdr_t *n = (bhdr_t *)(p + rem); CTL(1);
            stz(&h->size, rem);
            stz(&n->size, need); stz(&n->prev, rem); stz(&n->used, 0);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, need);
            p = (char *)n; h = n; sz = need;
        } else {                                      /* large block: carved from the BOTTOM of the free block */
            bhdr_t *n = (bhdr_t *)(p + need); CTL(1);
            stz(&n->size, rem); stz(&n->prev, need); stz(&n->used, 0);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, rem);
            stz(&h->size, need); sz = need;
        }
    }
    stz(&h->used, 1);
    mem_cur += sz - 64; mem_live++; mem_used += sz;
    size_t ext = (size_t)(p - arena) + sz;
    if (ext > arena_hwm) arena_hwm = ext;
    if (mem_used > mem_peak) { mem_peak = mem_used; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
    CTL(ALLOC_STATS);
    return p + 64;
}
void xfree(void *q) {
    CTL(2); if (!q) return;
    char *p = (char *)q - 64; CTL(1);
    bhdr_t *h = (bhdr_t *)p;
    size_t sz = ldz(&h->size), prev = ldz(&h->prev);
    stz(&h->used, 0);
    mem_cur -= sz - 64; mem_live--; mem_used -= sz;   /* (payload bytes are tracked by block: informational) */
    CTL(ALLOC_STATS);
    char *n = p + sz; CTL(3);
    if (n < arena + ARENA) {
        bhdr_t *nh = (bhdr_t *)n;
        size_t nu = ldz(&nh->used); CTL(2);
        if (!nu) {
            sz += ldz(&nh->size); CTL(1); stz(&h->size, sz);
            char *nn = p + sz; CTL(3);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, sz);
        }
    }
    CTL(2);
    if (prev) {
        bhdr_t *ph = (bhdr_t *)(p - prev); CTL(1);
        size_t pu = ldz(&ph->used); CTL(2);
        if (!pu) {
            size_t psz = prev + sz; CTL(1); stz(&ph->size, psz);
            char *nn = (char *)ph + psz; CTL(3);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, psz);
        }
    }
}
void mem_reset_peak(void) { mem_peak = mem_used; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
