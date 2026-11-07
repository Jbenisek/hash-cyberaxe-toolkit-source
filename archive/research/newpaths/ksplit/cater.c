/* cater.c - delta-pathwidth upper bound: find a word order (caterpillar join tree, every word a leaf) whose
 * prefixes P_t have small delta(P_t) = |P_t| - Ein(P_t).  Cost lower bound of any tree whose largest region
 * has delta w is 2^(32w - 64) (NOTES.txt section 3); a caterpillar with max delta w is an explicit
 * guess-and-determine order with running (guesses - checks) <= w.
 * usage: cater sys seed iters  -> prints best max-delta and the order
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>

#define MAXW 130
#define MAXE 256
static int N, E, NM, F;
static char names[MAXW][32];
static int ew[MAXE][4], en[MAXE];
static int occ[MAXW][16], nocc[MAXW];

static uint64_t rs = 88172645463325252ULL;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static void load(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        char nm[32]; int k;
        if (fscanf(f, "%31s %d", nm, &k) != 2) exit(4);
        en[e] = k;
        for (int j = 0; j < k; j++) { if (fscanf(f, "%d", &ew[e][j]) != 1) exit(5); occ[ew[e][j]][nocc[ew[e][j]]++] = e; }
    }
    fclose(f);
}

/* profile of an order: delta after each prefix; returns max, fills sumexp */
static int pos[MAXW];
static int eval(const int *ord, double *score) {
    for (int t = 0; t < N; t++) pos[ord[t]] = t;
    /* equation e closes at step max(pos of its words) */
    static int closeat[MAXW];
    memset(closeat, 0, sizeof(closeat));
    for (int e = 0; e < E; e++) {
        int m = -1;
        for (int j = 0; j < en[e]; j++) if (pos[ew[e][j]] > m) m = pos[ew[e][j]];
        if (m >= 0) closeat[m]++;
    }
    int d = 0, mx = 0; double s = 0;
    for (int t = 0; t < N; t++) {
        d += 1 - closeat[t];
        if (d > mx) mx = d;
        s += pow(2.0, d);
    }
    *score = s;
    return mx;
}

int main(int argc, char **argv) {
    load(argv[1]);
    rs ^= (uint64_t)atoll(argv[2]) * 0x9E3779B97F4A7C15ULL;
    long iters = atol(argv[3]);
    int ord[MAXW], best[MAXW], cur[MAXW];
    int bestmx = 999; double bests = 1e300;
    for (int restart = 0; restart < 20; restart++) {
        /* randomized greedy start: next word = one that closes most equations (ties random) */
        int used[MAXW] = {0};
        static int inP[MAXW];
        memset(inP, 0, sizeof(inP));
        for (int t = 0; t < N; t++) {
            int bw = -1, bc = -1;
            for (int w = 0; w < N; w++) {
                if (used[w]) continue;
                int c = 0;
                for (int i = 0; i < nocc[w]; i++) {
                    int e = occ[w][i], all = 1;
                    for (int j = 0; j < en[e]; j++) if (ew[e][j] != w && !inP[ew[e][j]]) { all = 0; break; }
                    c += all;
                }
                int key = c * 1000 + (int)(rnd() % 1000);
                if (key > bc) { bc = key; bw = w; }
            }
            ord[t] = bw; used[bw] = 1; inP[bw] = 1;
        }
        memcpy(cur, ord, sizeof(int) * N);
        double cs; int cm = eval(cur, &cs);
        double T = 2.0;
        for (long it = 0; it < iters; it++) {
            int a = rnd() % N, b = rnd() % N;
            if (a == b) continue;
            int tmp[MAXW];
            memcpy(tmp, cur, sizeof(int) * N);
            /* move word at a to position b */
            int w = tmp[a];
            if (a < b) memmove(tmp + a, tmp + a + 1, sizeof(int) * (b - a)); else memmove(tmp + b + 1, tmp + b, sizeof(int) * (a - b));
            tmp[b] = w;
            double s; int m = eval(tmp, &s);
            double cobj = cm * 1e6 + log2(cs), nobj = m * 1e6 + log2(s);
            if (nobj <= cobj || exp(-(nobj - cobj) / (T * 1e6)) > (double)(rnd() % 1000000) / 1e6) {
                memcpy(cur, tmp, sizeof(int) * N); cm = m; cs = s;
                if (m < bestmx || (m == bestmx && s < bests)) { bestmx = m; bests = s; memcpy(best, cur, sizeof(int) * N); }
            }
            T = 2.0 * (1.0 - (double)it / iters) + 0.01;
        }
    }
    double s; int m = eval(best, &s);
    printf("best max delta %d (sum 2^delta = %.1f)\norder with running delta:\n", m, s);
    for (int t = 0; t < N; t++) pos[best[t]] = t;
    int d = 0;
    for (int t = 0; t < N; t++) {
        int c = 0;
        for (int i = 0; i < nocc[best[t]]; i++) {
            int e = occ[best[t]][i], mxp = -1;
            for (int j = 0; j < en[e]; j++) if (pos[ew[e][j]] > mxp) mxp = pos[ew[e][j]];
            if (mxp == t) c++;
        }
        d += 1 - c;
        printf("%s(%d) ", names[best[t]], d);
    }
    printf("\n");
    return 0;
}
