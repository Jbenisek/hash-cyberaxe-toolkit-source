// Guess sets built on a small "self-checked" core: every r-set of class representatives whose closure has r-1 checks
// (dimension 1) is extended by exactly E more representatives (canonical order) until the closure is everything.
// Prints "SOL core... extras..." for split.c.   usage: corex model r E
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define MAXR 4096
int n, R, NR, rtype[MAXR], rcnt[MAXR], rv[MAXR][8], occ[128][256], nocc[128], reps[128], neq;
u128 rmask[MAXR], rtrig[MAXR], eqm[MAXR], BASE, ALL;
int PROC = 0, NPROC = 1, E, R0, DIMZ = 1, ext[16], core_[16]; long long nsol = 0;
static inline int single(u128 u) { return u && !(u & (u - 1)); }
static inline int bitidx(u128 u) { unsigned long long lo = (unsigned long long)u, hi = (unsigned long long)(u >> 64); return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi); }
static inline int pc(u128 u) { return __builtin_popcountll((unsigned long long)u) + __builtin_popcountll((unsigned long long)(u >> 64)); }
static u128 prop(u128 known, u128 newb) {
    int q[256], qh = 0, qt = 0;
    for (int v = 0; v < n; v++) if ((newb >> v) & 1) q[qt++] = v;
    while (qh < qt) { int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) { int r = occ[v][i];
            if (rtype[r] == 0) { u128 u = rmask[r] & ~known; if (single(u)) { known |= u; q[qt++] = bitidx(u); } }
            else if (!(rtrig[r] & ~known)) { u128 t = rmask[r] & ~rtrig[r]; if (t & ~known) { known |= t; q[qt++] = bitidx(t); } } } }
    return known;
}
static int dim(u128 s) { int e = 0; for (int i = 0; i < neq; i++) if (!(eqm[i] & ~s)) e++; return pc(s) - e; }
static void dfs(int d, int start, u128 known) {
    if (known == ALL) {
        if (d == E) {
            nsol++;
            printf("SOL");
            for (int i = 0; i < R0; i++) printf(" %d", core_[i]);
            for (int i = 0; i < E; i++) printf(" %d", ext[i]);
            printf("\n");
        }
        return;
    }
    if (d == E) return;
    for (int j = start; j < NR; j++) {
        int v = reps[j];
        if ((known >> v) & 1) continue;
        ext[d] = v;
        dfs(d + 1, j + 1, prop(known | ((u128)1 << v), (u128)1 << v));
    }
}
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); R0 = atoi(argv[2]); E = atoi(argv[3]); if (argc > 4) DIMZ = atoi(argv[4]); if (argc > 6) { PROC = atoi(argv[5]); NPROC = atoi(argv[6]); }
    if (fscanf(f, "%d %d", &n, &R) != 2) return 1;
    for (int r = 0; r < R; r++) { if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return 1;
        for (int i = 0; i < rcnt[r]; i++) { if (fscanf(f, "%d", &rv[r][i]) != 1) return 1; rmask[r] |= (u128)1 << rv[r][i];
            if (rtype[r] == 0 || i < rcnt[r] - 1) occ[rv[r][i]][nocc[rv[r][i]]++] = r;
            if (rtype[r] == 1 && i < rcnt[r] - 1) rtrig[r] |= (u128)1 << rv[r][i]; }
        if (rtype[r] == 0) eqm[neq++] = rmask[r]; }
    char tag[16]; if (fscanf(f, "%15s %d", tag, &NR) != 2) return 1;
    for (int j = 0; j < NR; j++) if (fscanf(f, "%d", &reps[j]) != 1) return 1;
    ALL = (n == 128) ? ~(u128)0 : (((u128)1 << n) - 1);
    u128 b = 0; for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1) b |= rmask[r];
    BASE = prop(b, b);
    int baseD = dim(BASE), idx[16], ncores = 0;
    for (int i = 0; i < R0; i++) idx[i] = i;
    while (1) {
        u128 m = 0; for (int i = 0; i < R0; i++) m |= (u128)1 << reps[idx[i]];
        u128 c = prop(BASE | m, m);
        int ch = R0 - (dim(c) - baseD);
        if (R0 - ch == DIMZ && (ncores++ % NPROC) == PROC) {
            for (int i = 0; i < R0; i++) core_[i] = reps[idx[i]];
            fprintf(stderr, "core");
            for (int i = 0; i < R0; i++) fprintf(stderr, " %d", core_[i]);
            long long before = nsol;
            dfs(0, 0, c);
            fprintf(stderr, "  -> %lld full sets with %d extras\n", nsol - before, E);
        }
        int i = R0 - 1; while (i >= 0 && idx[i] == NR - R0 + i) i--;
        if (i < 0) break; idx[i]++; for (int j = i + 1; j < R0; j++) idx[j] = idx[j - 1] + 1;
    }
    fprintf(stderr, "cores %d, sets %lld\n", ncores, nsol);
    return 0;
}
