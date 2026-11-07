/* fullsets.c - exhaustive search for guess sets S (|S| <= K) whose propagation closure is every word.
 * Same model as split.c (one-unknown equations + optional table macros).  Exact: no depth bound.
 * Guesses taken in increasing index order; a guess already in the current closure is skipped
 * (such a set is not minimal); a set whose closure is already full is reported and not extended.
 * Usage: fullsets sys K part nparts     (work split on the first two guess indices)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 M;
#define MAXW 128
#define MAXE 256
static int N, E, NM, F;
static char names[MAXW][32];
static M emask[MAXE];
static M mtrig[4096];
static int mtgt[4096];
static int occ[MAXW][32], nocc[MAXW];      /* equations containing word */
static int mocc[MAXW][1024], nmocc[MAXW];    /* macros whose trigger contains word */
static M ALL;
static int K;
static long found[16], nodes;
static int stk[16];

static M bit(int i) { return ((M)1) << i; }

static void load(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        char nm[32]; int k; if (fscanf(f, "%31s %d", nm, &k) != 2) exit(4);
        emask[e] = 0;
        for (int j = 0; j < k; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(5); emask[e] |= bit(x); occ[x][nocc[x]++] = e; }
    }
    for (int m = 0; m < NM; m++) {
        int t; if (fscanf(f, "%d", &t) != 1) exit(6);
        mtrig[m] = 0;
        for (int j = 0; j < t; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(7); mtrig[m] |= bit(x); mocc[x][nmocc[x]++] = m; }
        if (fscanf(f, "%d", &mtgt[m]) != 1) exit(8);
    }
    fclose(f);
    ALL = 0; for (int i = 0; i < N; i++) ALL |= bit(i);
}

/* add word w to known set K and propagate (worklist) */
static M addprop(M Kn, int w) {
    int q[MAXW], qh = 0, qt = 0;
    Kn |= bit(w); q[qt++] = w;
    while (qh < qt) {
        int v = q[qh++];
        for (int j = 0; j < nocc[v]; j++) {
            M u = emask[occ[v][j]] & ~Kn;
            if (u && !(u & (u - 1))) {
                int t = (uint64_t)u ? __builtin_ctzll((uint64_t)u) : 64 + __builtin_ctzll((uint64_t)(u >> 64));
                Kn |= u; q[qt++] = t;
            }
        }
        for (int j = 0; j < nmocc[v]; j++) {
            int m = mocc[v][j];
            if (!(mtrig[m] & ~Kn) && !(Kn & bit(mtgt[m]))) { Kn |= bit(mtgt[m]); q[qt++] = mtgt[m]; }
        }
    }
    return Kn;
}

static void dfs(M Kn, int depth, int start) {
    nodes++;
    if (Kn == ALL) {
        found[depth]++;
        printf("FULL k=%d:", depth);
        for (int i = 0; i < depth; i++) printf(" %d", stk[i]);
        printf("\n"); fflush(stdout);
        return;
    }
    if (depth == K) return;
    for (int i = start; i < N; i++) {
        if (Kn & bit(i)) continue;
        stk[depth] = i;
        dfs(addprop(Kn, i), depth + 1, i + 1);
    }
}

int main(int argc, char **argv) {
    load(argv[1]);
    K = atoi(argv[2]);
    int part = atoi(argv[3]), np = atoi(argv[4]);
    long pairidx = 0;
    for (int i = 0; i < N; i++) {
        M K1 = addprop(0, i);
        stk[0] = i;
        if (K1 == ALL) { if (part == 0) { found[1]++; printf("FULL k=1: %s\n", names[i]); } continue; }
        for (int j = i + 1; j < N; j++) {
            if (K1 & bit(j)) continue;
            if ((pairidx++ % np) != part) continue;
            stk[1] = j;
            dfs(addprop(K1, j), 2, j + 1);
        }
    }
    printf("DONE part %d/%d K=%d nodes=%ld found:", part, np, K, nodes);
    for (int i = 0; i <= K; i++) printf(" k%d=%ld", i, found[i]);
    printf("\n");
    return 0;
}
