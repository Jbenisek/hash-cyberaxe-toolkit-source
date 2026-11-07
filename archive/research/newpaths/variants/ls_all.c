// Randomized local search for small guess sets (upper bounds) on models of any size (n <= 1024).
// Construction: greedy (candidate words in rules with exactly one other unknown, random tie-break), then
// improvement: drop two guesses and try every single replacement (k -> k-1); plateau moves: swap one guess.
// usage: ls model seconds seed      prints improving solutions "BEST k: v1 v2 ..."
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#define MAXN 1024
#define MAXR 4096
int n, R, NR;
int rtype[MAXR], rcnt[MAXR], rv[MAXR][8];
int occ[MAXN][160], nocc[MAXN], reps[MAXN];
unsigned char base[MAXN];
static unsigned long long rs = 88172645463325252ULL;
static inline unsigned long long rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static int close_from(unsigned char *K, int *q, int qt) {
    int qh = 0, cnt = 0;
    while (qh < qt) {
        int v = q[qh++]; cnt++;
        for (int i = 0; i < nocc[v]; i++) {
            int r = occ[v][i], unk = -1, nu = 0;
            if (rtype[r] == 0) {
                for (int j = 0; j < rcnt[r]; j++) if (!K[rv[r][j]]) { nu++; unk = rv[r][j]; }
                if (nu == 1) { K[unk] = 1; q[qt++] = unk; }
            } else {
                int ok = 1;
                for (int j = 0; j < rcnt[r] - 1; j++) if (!K[rv[r][j]]) { ok = 0; break; }
                int t = rv[r][rcnt[r] - 1];
                if (ok && !K[t]) { K[t] = 1; q[qt++] = t; }
            }
        }
    }
    return cnt;
}
// returns number of known words after closure of base + guesses
static int closure(const int *g, int k, unsigned char *K) {
    static int q[MAXN * 2];
    memcpy(K, base, n);
    int qt = 0;
    for (int i = 0; i < k; i++) if (!K[g[i]]) { K[g[i]] = 1; q[qt++] = g[i]; }
    close_from(K, q, qt);
    int c = 0; for (int v = 0; v < n; v++) c += K[v];
    return c;
}
static int greedy(int *g) {
    static unsigned char K[MAXN];
    int k = 0;
    while (closure(g, k, K) < n) {
        static int score[MAXN];
        memset(score, 0, sizeof(int) * n);
        for (int r = 0; r < R; r++) {
            int nu = 0, u[8];
            if (rtype[r] == 0) {
                for (int j = 0; j < rcnt[r]; j++) if (!K[rv[r][j]]) u[nu++] = rv[r][j];
                if (nu == 2) { score[u[0]]++; score[u[1]]++; }
            } else {
                int t = rv[r][rcnt[r] - 1];
                if (K[t]) continue;
                for (int j = 0; j < rcnt[r] - 1; j++) if (!K[rv[r][j]]) u[nu++] = rv[r][j];
                if (nu == 1) score[u[0]]++;
            }
        }
        int best = 0; for (int v = 0; v < n; v++) if (!K[v] && score[v] > best) best = score[v];
        int slack = (rnd() % 3 == 0) ? 1 : 0, cands[MAXN], nc = 0;
        for (int v = 0; v < n; v++) if (!K[v] && score[v] >= best - slack && (best > 0 || 1)) cands[nc++] = v;
        g[k++] = cands[rnd() % nc];
    }
    return k;
}
static int improve(int *g, int k) {
    static unsigned char K[MAXN];
    int h[MAXN];
    for (int a = 0; a < k; a++) for (int b = a + 1; b < k; b++) {
        int m = 0;
        for (int i = 0; i < k; i++) if (i != a && i != b) h[m++] = g[i];
        closure(h, m, K);
        // candidates: unknown reps
        for (int j = 0; j < NR; j++) {
            int w = reps[j];
            if (K[w]) continue;
            h[m] = w;
            static unsigned char K2[MAXN];
            if (closure(h, m + 1, K2) == n) { memcpy(g, h, sizeof(int) * (m + 1)); return m + 1; }
        }
    }
    return k;
}
static void plateau(int *g, int k, int tries) {
    static unsigned char K[MAXN];
    int h[MAXN];
    for (int t = 0; t < tries; t++) {
        int a = rnd() % k, w = reps[rnd() % NR];
        memcpy(h, g, sizeof(int) * k);
        h[a] = w;
        if (closure(h, k, K) == n) { memcpy(g, h, sizeof(int) * k); }
    }
}
int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    double secs = atof(argv[2]); rs ^= (unsigned long long)atoll(argv[3]) * 0x9E3779B97F4A7C15ULL;
    if (fscanf(f, "%d %d", &n, &R) != 2) return 1;
    for (int r = 0; r < R; r++) {
        if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return 1;
        for (int i = 0; i < rcnt[r]; i++) {
            if (fscanf(f, "%d", &rv[r][i]) != 1) return 1;
            if (rtype[r] == 0 || i < rcnt[r] - 1) occ[rv[r][i]][nocc[rv[r][i]]++] = r;
        }
    }
    char tag[16];
    if (fscanf(f, "%15s %d", tag, &NR) != 2) return 1;
    for (int j = 0; j < NR; j++) if (fscanf(f, "%d", &reps[j]) != 1) return 1;
    int q[MAXN * 2], qt = 0;
    for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1 && !base[rv[r][0]]) { base[rv[r][0]] = 1; q[qt++] = rv[r][0]; }
    close_from(base, q, qt);
    clock_t st = clock();
    int bestk = 1 << 30, g[MAXN];
    long iters = 0;
    while ((double)(clock() - st) / CLOCKS_PER_SEC < secs) {
        int k = greedy(g);
        for (int round = 0; round < 6; round++) {
            int k2;
            while ((k2 = improve(g, k)) < k) k = k2;
            plateau(g, k, 200);
        }
        iters++;
        if (k <= bestk) {
            if (k == bestk) { printf("SOL"); for (int i = 0; i < k; i++) printf(" %d", g[i]); printf("\n"); fflush(stdout); continue; }
            bestk = k;
            printf("BEST %d:", k);
            for (int i = 0; i < k; i++) printf(" %d", g[i]);
            printf("   (iter %ld, %.0fs)\n", iters, (double)(clock() - st) / CLOCKS_PER_SEC);
            fflush(stdout);
        }
    }
    printf("END best %d iters %ld\n", bestk, iters);
    return 0;
}
