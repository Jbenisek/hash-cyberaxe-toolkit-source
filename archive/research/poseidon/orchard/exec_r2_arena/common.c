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

/* Tracked allocation from one static arena in .bss (no heap calls).  Each block = a 64-byte header (payload size) + the payload rounded up to 32
 * bytes.  Placement: lowest-address first fit among the gaps between live blocks.  mem_peak = arena high-water mark (end of the highest live block). */
#ifndef ARENA
#define ARENA 67108864
#endif
static char arena[ARENA] __attribute__((aligned(64)));
#define MAXB 512
static size_t boff[MAXB], blen[MAXB]; static int nb = 0;      /* live blocks sorted by offset */
size_t mem_live = 0, mem_peak_live = 0, mem_peak_pay = 0;
static size_t top(void) { return nb ? boff[nb - 1] + blen[nb - 1] : 0; }
static FILE *trf = NULL; static int trinit = 0;
static void tr(char op, size_t bytes, size_t off) {
#ifndef ATR
    (void)op; (void)bytes; (void)off; (void)trf; (void)trinit; return;
#endif
    if (!trinit) { trinit = 1; const char *e = getenv("ATRACE"); if (e) trf = fopen(e, "w"); }
    if (trf) fprintf(trf, "%c %zu %zu\n", op, bytes, off);
}
void *xalloc(size_t bytes) {
    size_t need = 64 + ((bytes + 31) & ~(size_t)31), at = 0; int k;
    for (k = 0; k < nb; k++) { if (boff[k] - at >= need) break; at = boff[k] + blen[k]; }
    if (at + need > ARENA || nb >= MAXB) { fprintf(stderr, "arena full (%zu)\n", bytes); exit(2); }
    for (int j = nb; j > k; j--) { boff[j] = boff[j - 1]; blen[j] = blen[j - 1]; }
    boff[k] = at; blen[k] = need; nb++;
    char *p = arena + at; *(size_t *)p = bytes;
    mem_cur += bytes; mem_live++;
    if (top() > mem_peak) { mem_peak = top(); mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
    tr('A', bytes, at);
    return p + 64;
}
/* move a live block to the lowest gap that holds it if that is below its place (memmove, counted per element); *pp is updated */
void xmove_down(void **pp) {
    if (!*pp) return;
    size_t old = (size_t)((char *)*pp - 64 - arena); int k;
    for (k = 0; k < nb && boff[k] != old; k++) ;
    if (k == nb) { fprintf(stderr, "bad move\n"); exit(2); }
    size_t need = blen[k], at = 0; int j;
    for (j = 0; j < nb; j++) { if (j == k) continue; if (boff[j] >= at + need) break; at = boff[j] + blen[j]; }   /* first fit, own block counted free */
    CTL(4);
    if (at >= old) return;
    size_t bytes = *(size_t *)(arena + old), nel = (bytes + sizeof(fp) - 1) / sizeof(fp);
    memmove(arena + at, arena + old, 64 + bytes);
    LD(nel); ST(nel); loopc(nel);
    boff[k] = at;          /* order is kept: the new place lies above block k-1's end only if no lower gap; re-sort to be safe */
    for (int a = k; a > 0 && boff[a - 1] > boff[a]; a--) { size_t t = boff[a]; boff[a] = boff[a - 1]; boff[a - 1] = t; t = blen[a]; blen[a] = blen[a - 1]; blen[a - 1] = t; }
    *pp = arena + at + 64;
    tr('M', bytes, at); tr('m', 0, old);
}
/* temporary buffer: placed at the high end of the highest gap that fits (the arena end counts as the top of the last gap) */
void *xalloc_t(size_t bytes) {
    size_t need = 64 + ((bytes + 31) & ~(size_t)31), at = ARENA; int k = nb, ok = 0;
    for (k = nb; k >= 0; k--) {
        size_t lo = k ? boff[k - 1] + blen[k - 1] : 0, hi = k < nb ? boff[k] : ARENA;
        if (hi - lo >= need) { at = hi - need; ok = 1; break; }
    }
    if (!ok || nb >= MAXB) { fprintf(stderr, "arena full (%zu)\n", bytes); exit(2); }
    for (int j = nb; j > k; j--) { boff[j] = boff[j - 1]; blen[j] = blen[j - 1]; }
    boff[k] = at; blen[k] = need; nb++;
    char *p = arena + at; *(size_t *)p = bytes;
    mem_cur += bytes; mem_live++;
    tr('T', bytes, at);
    return p + 64;
}
void xfree(void *q) {
    if (!q) return;
    size_t at = (size_t)((char *)q - 64 - arena); int k;
    for (k = 0; k < nb && boff[k] != at; k++) ;
    if (k == nb) { fprintf(stderr, "bad free\n"); exit(2); }
    mem_cur -= *(size_t *)(arena + at); mem_live--;
#ifdef POISON
    memset(arena + at, 0xA5, blen[k]);
#endif
    for (; k < nb - 1; k++) { boff[k] = boff[k + 1]; blen[k] = blen[k + 1]; }
    nb--; tr('F', 0, at);
}
/* shrink a live block in place to bytes (<= its size); the freed tail becomes a gap */
void xshrink(void *q, size_t bytes) {
    size_t at = (size_t)((char *)q - 64 - arena); int k;
    for (k = 0; k < nb && boff[k] != at; k++) ;
    if (k == nb) { fprintf(stderr, "bad shrink\n"); exit(2); }
    size_t old = *(size_t *)(arena + at); if (bytes > old) { fprintf(stderr, "bad shrink\n"); exit(2); }
    mem_cur -= old - bytes; *(size_t *)(arena + at) = bytes; blen[k] = 64 + ((bytes + 31) & ~(size_t)31);
    tr('S', bytes, at);
}
void mem_reset_peak(void) { mem_peak = top(); mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
