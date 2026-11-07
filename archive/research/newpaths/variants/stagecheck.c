// Exact staged (CV-list) check over all class-expanded minimum solutions.  B = 8 words must be a minimum guess set
// of the fixed-CV model, so it suffices to expand the canonical solutions by class members.
// usage: stagecheck cvmodel prepfile Ffixed      prints histogram of keys J over expanded sets with phase 2 complete
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define MAXR 4096
int n, R, rtype[MAXR], rcnt[MAXR], rv[MAXR][8], rcv[MAXR], occ[128][256], nocc[128];
u128 rmask[MAXR], rtrig[MAXR], CVM, ALL, BASE1;
static inline int single(u128 u) { return u && !(u & (u - 1)); }
static inline int bitidx(u128 u) { unsigned long long lo = (unsigned long long)u, hi = (unsigned long long)(u >> 64); return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi); }
static u128 prop(u128 known, u128 newb, int phase) {
    int q[256], qh = 0, qt = 0;
    for (int v = 0; v < n; v++) if ((newb >> v) & 1) q[qt++] = v;
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) {
            int r = occ[v][i];
            if (phase == 1 && rcv[r]) continue;
            if (rtype[r] == 0) { u128 u = rmask[r] & ~known; if (single(u)) { known |= u; q[qt++] = bitidx(u); } }
            else if (!(rtrig[r] & ~known)) { u128 t = rmask[r] & ~rtrig[r]; if (t & ~known) { known |= t; q[qt++] = bitidx(t); } }
        }
    }
    return known;
}
int ncls, csz[256], cmem[256][16], nsol, sol[200000][16], K = 8;
long long hist[16][2], total = 0;
int pick[16]; int bestJ = -1;
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int F = atoi(argv[3]);
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
    char tag[16]; int nr, ncv;
    if (fscanf(f, "%15s %d", tag, &nr) != 2) return 1;
    for (int j = 0; j < nr; j++) { int x; if (fscanf(f, "%d", &x) != 1) return 1; }
    if (fscanf(f, "%15s %d", tag, &ncv) != 2) return 1;
    for (int j = 0; j < ncv; j++) { int v; if (fscanf(f, "%d", &v) != 1) return 1; CVM |= (u128)1 << v; }
    fclose(f);
    for (int r = 0; r < R; r++) rcv[r] = (rmask[r] & CVM) != 0;
    ALL = (n == 128) ? ~(u128)0 : (((u128)1 << n) - 1);
    u128 b = 0; for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1 && !rcv[r]) b |= rmask[r];
    BASE1 = prop(b, b, 1);
    FILE *g = fopen(argv[2], "r");
    if (fscanf(g, "%15s %d", tag, &ncls) != 2) return 1;
    for (int c = 0; c < ncls; c++) { if (fscanf(g, "%d", &csz[c]) != 1) return 1; for (int i = 0; i < csz[c]; i++) if (fscanf(g, "%d", &cmem[c][i]) != 1) return 1; }
    if (fscanf(g, "%15s %d", tag, &nsol) != 2) return 1;
    for (int s = 0; s < nsol; s++) for (int i = 0; i < K; i++) if (fscanf(g, "%d", &sol[s][i]) != 1) return 1;
    int c = K - F;
    for (int s = 0; s < nsol; s++) {
        int idx[16] = {0};
        while (1) {
            u128 m = 0;
            for (int i = 0; i < K; i++) m |= (u128)1 << cmem[sol[s][i]][idx[i]];
            u128 k1 = prop(BASE1 | m, BASE1 | m, 1);
            int J = 0;
            for (int r = 0; r < R; r++) if (rcv[r] && rtype[r] == 0 && !((rmask[r] & ~CVM) & ~k1)) J++;
            u128 k2 = prop(k1 | CVM, k1 | CVM, 2);
            int ok = (k2 == ALL);
            hist[J][ok]++; total++;
            if (ok && J > bestJ) {
                bestJ = J; printf("best J=%d (c=%d) set:", J, c);
                for (int i = 0; i < K; i++) printf(" %d", cmem[sol[s][i]][idx[i]]);
                printf("\n"); fflush(stdout);
            }
            int i = 0;
            while (i < K && ++idx[i] == csz[sol[s][i]]) { idx[i] = 0; i++; }
            if (i == K) break;
        }
    }
    printf("expanded sets %lld; histogram J:(phase2 incomplete, complete)", total);
    for (int J = 0; J < 16; J++) if (hist[J][0] || hist[J][1]) printf(" %d:(%lld,%lld)", J, hist[J][0], hist[J][1]);
    printf("\nchecks c=%d; staged with no post checks needs J>=c\n", c);
    return 0;
}
