/* vmaxcl.c (verify_separable_0) - largest propagation closure of any k-set of guesses, k = 1..4 (all subsets). */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#define MW 128
#define ME 256
typedef struct { uint64_t lo, hi; } S;
static int N, E, eqk[ME], eqw[ME][4], nocc[MW], occ[MW][16];
static inline int has(S s, int i) { return i < 64 ? (s.lo >> i) & 1 : (s.hi >> (i - 64)) & 1; }
static inline S set(S s, int i) { if (i < 64) s.lo |= 1ULL << i; else s.hi |= 1ULL << (i - 64); return s; }
static S prop(S s, int w) {
    int st[MW], sp = 0; s = set(s, w); st[sp++] = w;
    while (sp) { int v = st[--sp];
        for (int t = 0; t < nocc[v]; t++) { int e = occ[v][t], unk = -1, nu = 0;
            for (int j = 0; j < eqk[e]; j++) if (!has(s, eqw[e][j])) { nu++; unk = eqw[e][j]; }
            if (nu == 1) { s = set(s, unk); st[sp++] = unk; } } }
    return s;
}
static int pc(S s) { return __builtin_popcountll(s.lo) + __builtin_popcountll(s.hi); }
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); char buf[64];
    if (!f || fscanf(f, "%d %d", &N, &E) != 2) return 1;
    for (int i = 0; i < N; i++) if (fscanf(f, "%63s", buf) != 1) return 2;
    for (int e = 0; e < E; e++) { if (fscanf(f, "%63s %d", buf, &eqk[e]) != 2) return 3;
        for (int j = 0; j < eqk[e]; j++) { int x; if (fscanf(f, "%d", &x) != 1) return 4; eqw[e][j] = x; occ[x][nocc[x]++] = e; } }
    int best[5] = {0}; S z = {0, 0};
    for (int a = 0; a < N; a++) { S s1 = prop(z, a); if (pc(s1) > best[1]) best[1] = pc(s1);
      for (int b = a + 1; b < N; b++) { S s2 = prop(s1, b); if (pc(s2) > best[2]) best[2] = pc(s2);
        for (int c = b + 1; c < N; c++) { S s3 = prop(s2, c); if (pc(s3) > best[3]) best[3] = pc(s3);
          for (int d = c + 1; d < N; d++) { S s4 = prop(s3, d); if (pc(s4) > best[4]) best[4] = pc(s4); } } } }
    printf("max closure (words of %d) k=1: %d  k=2: %d  k=3: %d  k=4: %d\n", N, best[1], best[2], best[3], best[4]);
    return 0;
}
