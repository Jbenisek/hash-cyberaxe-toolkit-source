// Two-block "CV list" staged search (variant e).  The chaining value words (init0..init7) are unknowns that come
// from a precomputed list of first blocks.  Phase 1: guesses B (non-CV words) propagate WITHOUT any equation that
// contains a CV word.  Keys: CV equations whose non-CV words are all known after phase 1 (each a 32-bit lookup key
// on the CV list).  Phase 2: all CV words known (list entry), full propagation must reach everything.
// checks c = |B| - Ffixed; keys J <= c; post-filter checks c - J.
// Model file as for gdx plus a line "cv cnt i1..icnt" (indices of the CV words) after the reps line; reps must not
// contain CV words.   usage: gdcv model k Ffixed proc nprocs maxprint [slack: also count leaves with J >= c - slack]
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define MAXR 4096
int n, R, NR, K, Ff, proc, nprocs, maxprint, SLACK = 0;
int rtype[MAXR], rcnt[MAXR], rv[MAXR][8], rcv[MAXR];
u128 rmask[MAXR], rtrig[MAXR], CVM, ALL;
int occ[128][256], nocc[128], reps[128], guess[64];
long long nodes = 0, hist[64][64];

static inline int single(u128 u) { return u && !(u & (u - 1)); }
static inline int bitidx(u128 u) {
    unsigned long long lo = (unsigned long long)u, hi = (unsigned long long)(u >> 64);
    return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi);
}
static u128 prop(u128 known, u128 newbits, int phase) {
    int q[256], qh = 0, qt = 0;
    for (int v = 0; v < n; v++) if ((newbits >> v) & 1) q[qt++] = v;
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) {
            int r = occ[v][i];
            if (phase == 1 && rcv[r]) continue;
            if (rtype[r] == 0) {
                u128 u = rmask[r] & ~known;
                if (single(u)) { known |= u; q[qt++] = bitidx(u); }
            } else if (!(rtrig[r] & ~known)) {
                u128 t = rmask[r] & ~rtrig[r];
                if (t & ~known) { known |= t; q[qt++] = bitidx(t); }
            }
        }
    }
    return known;
}
static void leaf(u128 known) {
    int J = 0;
    for (int r = 0; r < R; r++)
        if (rcv[r] && rtype[r] == 0 && !((rmask[r] & ~CVM) & ~known)) J++;
    int c = K - Ff;
    if (J < c - SLACK) return;                 // too few keys: skip the phase-2 closure
    u128 k2 = prop(known | CVM, CVM, 2);
    if (k2 != ALL) return;
    hist[c < 0 ? 0 : c][J]++;
    if (J >= c && hist[c][J] <= maxprint) {
        printf("SOL J=%d c=%d", J, c);
        for (int i = 0; i < K; i++) printf(" %d", guess[i]);
        printf("\n");
    }
}
static void dfs(int depth, int start, u128 known) {
    nodes++;
    if (depth == K) { leaf(known); return; }
    for (int j = start; j < NR; j++) {
        int v = reps[j];
        if ((known >> v) & 1) continue;
        if (depth == 1 && ((guess[0] * 131 + j) % nprocs) != proc) continue;
        guess[depth] = v;
        dfs(depth + 1, j + 1, prop(known | ((u128)1 << v), (u128)1 << v, 1));
    }
}
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    K = atoi(argv[2]); Ff = atoi(argv[3]); proc = atoi(argv[4]); nprocs = atoi(argv[5]); maxprint = atoi(argv[6]); if (argc > 7) SLACK = atoi(argv[7]);
    if (fscanf(f, "%d %d", &n, &R) != 2) return 1;
    for (int r = 0; r < R; r++) {
        if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return 1;
        for (int i = 0; i < rcnt[r]; i++) {
            if (fscanf(f, "%d", &rv[r][i]) != 1) return 1;
            rmask[r] |= (u128)1 << rv[r][i];
            if (rtype[r] == 0 || i < rcnt[r] - 1) occ[rv[r][i]][nocc[rv[r][i]]++] = r;
            if (rtype[r] == 1 && i < rcnt[r] - 1) rtrig[r] |= (u128)1 << rv[r][i];
        }
    }
    char tag[16]; int ncv;
    if (fscanf(f, "%15s %d", tag, &NR) != 2) return 1;
    for (int j = 0; j < NR; j++) if (fscanf(f, "%d", &reps[j]) != 1) return 1;
    if (fscanf(f, "%15s %d", tag, &ncv) != 2) return 1;
    for (int j = 0; j < ncv; j++) { int v; if (fscanf(f, "%d", &v) != 1) return 1; CVM |= (u128)1 << v; }
    for (int r = 0; r < R; r++) rcv[r] = (rmask[r] & CVM) != 0;
    ALL = (n == 128) ? ~(u128)0 : (((u128)1 << n) - 1);
    u128 known = 0;
    for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1 && !rcv[r]) known |= rmask[r];
    known = prop(known, known, 1);
    for (int j = 0; j < NR; j++) {
        int v = reps[j];
        if ((known >> v) & 1) continue;
        guess[0] = v;
        dfs(1, j + 1, prop(known | ((u128)1 << v), (u128)1 << v, 1));
    }
    printf("DONE k=%d proc=%d/%d nodes=%lld\nHIST(c,J,count)", K, proc, nprocs, nodes);
    for (int c = 0; c < 64; c++) for (int J = 0; J < 64; J++) if (hist[c][J]) printf(" (%d,%d,%lld)", c, J, hist[c][J]);
    printf("\n");
    return 0;
}
