// Largest number of checks inside the closure of any set of r <= rmax guessed words (class representatives).
// checks(T) = |T| - dim(cl T), dim(X) = |X| - #equations inside X.   usage: core model rmax
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define MAXR 4096
int n, R, NR, rtype[MAXR], rcnt[MAXR], rv[MAXR][8], occ[128][256], nocc[128], reps[128], neq;
u128 rmask[MAXR], rtrig[MAXR], eqm[MAXR], BASE;
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
int best[16]; long long cnt[16][16];
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int rmax = atoi(argv[2]);
    if (fscanf(f, "%d %d", &n, &R) != 2) return 1;
    for (int r = 0; r < R; r++) { if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return 1;
        for (int i = 0; i < rcnt[r]; i++) { if (fscanf(f, "%d", &rv[r][i]) != 1) return 1; rmask[r] |= (u128)1 << rv[r][i];
            if (rtype[r] == 0 || i < rcnt[r] - 1) occ[rv[r][i]][nocc[rv[r][i]]++] = r;
            if (rtype[r] == 1 && i < rcnt[r] - 1) rtrig[r] |= (u128)1 << rv[r][i]; }
        if (rtype[r] == 0) eqm[neq++] = rmask[r]; }
    char tag[16]; if (fscanf(f, "%15s %d", tag, &NR) != 2) return 1;
    for (int j = 0; j < NR; j++) if (fscanf(f, "%d", &reps[j]) != 1) return 1;
    u128 b = 0; for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1) b |= rmask[r];
    BASE = prop(b, b);
    int baseD = dim(BASE);
    int idx[16];
    for (int r = 1; r <= rmax; r++) {
        for (int i = 0; i < r; i++) idx[i] = i;
        while (1) {
            u128 m = 0; for (int i = 0; i < r; i++) m |= (u128)1 << reps[idx[i]];
            u128 c = prop(BASE | m, m);
            int ch = r - (dim(c) - baseD);
            if (ch < 0) ch = 0; if (ch > 15) ch = 15;
            cnt[r][ch]++; if (ch > best[r]) best[r] = ch;
            int i = r - 1; while (i >= 0 && idx[i] == NR - r + i) i--;
            if (i < 0) break; idx[i]++; for (int j = i + 1; j < r; j++) idx[j] = idx[j - 1] + 1;
        }
        printf("r=%d max checks %d  counts:", r, best[r]);
        for (int ch = 0; ch < 16; ch++) if (cnt[r][ch]) printf(" %d:%lld", ch, cnt[r][ch]);
        printf("\n"); fflush(stdout);
    }
    return 0;
}
