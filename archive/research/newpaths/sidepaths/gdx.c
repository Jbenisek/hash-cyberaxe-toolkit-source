// Exact minimum guess set by exhaustive DFS over guess sets (canonical increasing order over class representatives).
// Model file (from export_model.py):  n r   then r lines "type cnt v1..vcnt" (type 0: equation, any single unknown
// is solved; type 1: table macro, last var is the target, others the trigger)   then "reps cnt r1..rcnt".
// usage: gdx model k proc nprocs maxprint     prints every guess set of size k whose closure is everything
// (only canonical ones: each guess not in the closure of the earlier ones), then a count line.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define MAXR 4096
int n, R, NR;
int rtype[MAXR], rcnt[MAXR], rv[MAXR][8];
u128 rmask[MAXR], rtrig[MAXR];
int occ[128][256], nocc[128];
int reps[128];
int K, proc, nprocs, maxprint;
long long found = 0, nodes = 0;
u128 ALL;
int guess[64];

static inline int single(u128 u) { return u && !(u & (u - 1)); }
static inline int bitidx(u128 u) {
    unsigned long long lo = (unsigned long long)u, hi = (unsigned long long)(u >> 64);
    return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi);
}

static u128 propagate(u128 known, int start) {
    int q[256], qh = 0, qt = 0;
    q[qt++] = start;
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) {
            int r = occ[v][i];
            if (rtype[r] == 0) {
                u128 u = rmask[r] & ~known;
                if (single(u)) { known |= u; q[qt++] = bitidx(u); }
            } else {
                if (!(rtrig[r] & ~known)) {
                    u128 t = rmask[r] & ~rtrig[r];
                    if (t & ~known) { known |= t; q[qt++] = bitidx(t); }
                }
            }
        }
    }
    return known;
}

static void dfs(int depth, int startrep, u128 known) {
    nodes++;
    if (known == ALL) {
        if (depth == K) {
            found++;
            if (found <= maxprint) {
                printf("SOL");
                for (int i = 0; i < depth; i++) printf(" %d", guess[i]);
                printf("\n");
                fflush(stdout);
            }
        }
        return;
    }
    if (depth == K) return;
    for (int j = startrep; j < NR; j++) {
        int v = reps[j];
        if ((known >> v) & 1) continue;
        if (depth == 1 && ((guess[0] * 131 + j) % nprocs) != proc) continue;
        guess[depth] = v;
        dfs(depth + 1, j + 1, propagate(known | ((u128)1 << v), v));
    }
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    K = atoi(argv[2]); proc = atoi(argv[3]); nprocs = atoi(argv[4]); maxprint = atoi(argv[5]);
    if (fscanf(f, "%d %d", &n, &R) != 2) return 1;
    for (int r = 0; r < R; r++) {
        if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return 1;
        rmask[r] = 0; rtrig[r] = 0;
        for (int i = 0; i < rcnt[r]; i++) {
            if (fscanf(f, "%d", &rv[r][i]) != 1) return 1;
            rmask[r] |= (u128)1 << rv[r][i];
            if (rtype[r] == 0 || i < rcnt[r] - 1) {
                int v = rv[r][i];
                occ[v][nocc[v]++] = r;
            }
            if (rtype[r] == 1 && i < rcnt[r] - 1) rtrig[r] |= (u128)1 << rv[r][i];
        }
    }
    char tag[16];
    if (fscanf(f, "%15s %d", tag, &NR) != 2) return 1;
    for (int j = 0; j < NR; j++) if (fscanf(f, "%d", &reps[j]) != 1) return 1;
    ALL = (n == 128) ? ~(u128)0 : (((u128)1 << n) - 1);
    // initial closure from constants: rules with a single var
    u128 known = 0;
    for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1) known |= rmask[r];
    for (int v = 0; v < n; v++) if ((known >> v) & 1) known = propagate(known, v);
    // depth 0 handled here so that work splits on (first, second) pairs
    for (int j = 0; j < NR; j++) {
        int v = reps[j];
        if ((known >> v) & 1) continue;
        guess[0] = v;
        u128 k1 = propagate(known | ((u128)1 << v), v);
        if (K == 1) { if (proc == 0) dfs(1, j + 1, k1); continue; }
        dfs(1, j + 1, k1);
    }
    printf("DONE k=%d proc=%d/%d found=%lld nodes=%lld\n", K, proc, nprocs, found, nodes);
    return 0;
}
