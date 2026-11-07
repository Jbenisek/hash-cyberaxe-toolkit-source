/* vfull.c (verify_separable_0) - independent exhaustive check: is there a guess set of <= K words whose
 * one-unknown-equation propagation closure is every word?  Reads vsys_fixed.txt (built by vsys.py from the brief).
 * Canonical enumeration: increasing word index, a word already derived by the prefix is never guessed (if it
 * were, dropping it gives a smaller set with the same closure, which this search also visits).
 * usage: vfull sysfile K part nparts first   (first = -1: all first indices; else only that first index)
 * prints counts of full-closure sets per size and the number of search nodes.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

#define MW 128
#define ME 256
typedef struct { uint64_t lo, hi; } S;
static int N, E, eqk[ME], eqw[ME][4], nocc[MW], occ[MW][16];
static S eqm[ME], FULL;
static int K;
static long long cnt[16], nodes;

static inline int has(S s, int i) { return i < 64 ? (s.lo >> i) & 1 : (s.hi >> (i - 64)) & 1; }
static inline S set(S s, int i) { if (i < 64) s.lo |= 1ULL << i; else s.hi |= 1ULL << (i - 64); return s; }
static inline int full(S s) { return s.lo == FULL.lo && s.hi == FULL.hi; }

static S prop(S s, int w) {
    int st[MW], sp = 0;
    s = set(s, w); st[sp++] = w;
    while (sp) {
        int v = st[--sp];
        for (int t = 0; t < nocc[v]; t++) {
            int e = occ[v][t], unk = -1, nu = 0;
            for (int j = 0; j < eqk[e]; j++) if (!has(s, eqw[e][j])) { nu++; unk = eqw[e][j]; }
            if (nu == 1) { s = set(s, unk); st[sp++] = unk; }
        }
    }
    return s;
}

static void dfs(S s, int depth, int start) {
    nodes++;
    if (full(s)) { cnt[depth]++; return; }
    if (depth == K) return;
    for (int i = start; i < N; i++) {
        if (has(s, i)) continue;
        dfs(prop(s, i), depth + 1, i + 1);
    }
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    K = atoi(argv[2]);
    int part = atoi(argv[3]), np = atoi(argv[4]), first = atoi(argv[5]);
    if (!f || fscanf(f, "%d %d", &N, &E) != 2) return 1;
    char buf[64];
    for (int i = 0; i < N; i++) if (fscanf(f, "%63s", buf) != 1) return 2;
    for (int e = 0; e < E; e++) {
        if (fscanf(f, "%63s %d", buf, &eqk[e]) != 2) return 3;
        for (int j = 0; j < eqk[e]; j++) {
            int x; if (fscanf(f, "%d", &x) != 1) return 4;
            eqw[e][j] = x; occ[x][nocc[x]++] = e;
        }
    }
    FULL.lo = FULL.hi = 0;
    for (int i = 0; i < N; i++) FULL = set(FULL, i);
    S z = {0, 0};
    long long pc = 0;
    for (int i = 0; i < N; i++) {
        if (first >= 0 && i != first) continue;
        S s1 = prop(z, i);
        if (full(s1)) { if (part == 0) cnt[1]++; continue; }
        for (int j = i + 1; j < N; j++) {
            if (has(s1, j)) continue;
            if (pc++ % np != part) continue;
            dfs(prop(s1, j), 2, j + 1);
        }
    }
    printf("vfull K=%d part %d/%d first=%d nodes=%lld full-closure sets by size:", K, part, np, first, nodes);
    for (int k = 1; k <= K; k++) printf(" k%d=%lld", k, cnt[k]);
    printf("\n");
    return 0;
}
