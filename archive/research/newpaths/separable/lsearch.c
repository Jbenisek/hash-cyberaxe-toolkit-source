/* lsearch.c - local search for small full-closure guess sets (heuristic, not exhaustive).
 * Start: random greedy (guess a word in an equation with two unknowns, prefer most such equations).
 * Moves: (1) drop 2 guesses, add 1 word (exhaustive over pairs/words) -> size -1 if closure stays full;
 *        (2) random swap (drop 1, add 1) keeping full closure, to diversify.
 * Usage: lsearch sys seed iters restarts
 */
#include "jtree_core.h"

static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static int greedy(int *S) {
    M K = closure(0); int n = 0;
    while (K != ALL) {
        int cnt[MAXW]; memset(cnt, 0, sizeof cnt);
        int best = 0;
        for (int e = 0; e < E; e++) {
            M u = emask[e] & ~K;
            if (pc(u) == 2) for (int i = 0; i < N; i++) if (u & bit(i)) { cnt[i]++; if (cnt[i] > best) best = cnt[i]; }
        }
        int pool[MAXW], np = 0;
        for (int i = 0; i < N; i++) {
            if (K & bit(i)) continue;
            if (best == 0 || cnt[i] >= best - (int)(rnd() % 2)) pool[np++] = i;
        }
        int g = pool[rnd() % np];
        S[n++] = g; K = closure(K | bit(g));
    }
    return n;
}

static M setmask(int *S, int n) { M T = 0; for (int i = 0; i < n; i++) T |= bit(S[i]); return T; }

int main(int argc, char **argv) {
    load(argv[1]);
    rs = 0x9E3779B97F4A7C15ULL * (uint64_t)(atoi(argv[2]) + 1);
    long iters = atol(argv[3]); int restarts = atoi(argv[4]);
    int printmax = argc > 5 ? atoi(argv[5]) : 0;
    int gbest = 1000;
    static long hist[MAXW];
    for (int r = 0; r < restarts; r++) {
        int S[MAXW]; int n = greedy(S);
        for (long it = 0; it < iters; it++) {
            int improved = 0;
            /* drop 2, add 1 */
            for (int i = 0; i < n && !improved; i++) for (int j = i + 1; j < n && !improved; j++) {
                M base = 0; for (int t = 0; t < n; t++) if (t != i && t != j) base |= bit(S[t]);
                M cb = closure(base);
                if (cb == ALL) { /* already full without both */
                    S[j] = S[n - 1]; n--; S[i] = S[n - 1]; n--; improved = 1; break;
                }
                for (int w = 0; w < N; w++) {
                    if (cb & bit(w)) continue;
                    if (closure(cb | bit(w)) == ALL) {
                        int a = S[i]; (void)a;
                        S[i] = w; S[j] = S[n - 1]; n--; improved = 1; break;
                    }
                }
            }
            if (!improved) {
                /* random swap keeping full closure */
                for (int tries = 0; tries < 200; tries++) {
                    int i = rnd() % n, w = rnd() % N;
                    M base = 0; for (int t = 0; t < n; t++) if (t != i) base |= bit(S[t]);
                    if (base & bit(w)) continue;
                    if (closure(base | bit(w)) == ALL) { S[i] = w; break; }
                }
            }
        }
        hist[n]++;
        if (n <= gbest || n <= printmax) {
            if (n < gbest) gbest = n;
            printf("restart %d size %d:", r, n);
            for (int i = 0; i < n; i++) printf(" %s", names[S[i]]);
            printf("\nFULL k=%d:", n);
            for (int i = 0; i < n; i++) printf(" %d", S[i]);
            printf("\n"); fflush(stdout);
        }
    }
    printf("DONE best %d histogram:", gbest);
    for (int i = 0; i < MAXW; i++) if (hist[i]) printf(" %d:%ld", i, hist[i]);
    printf("\n");
    return 0;
}
