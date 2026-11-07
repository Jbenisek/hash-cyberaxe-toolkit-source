/* vs.c - independent checks of separable/ claims (my own code; plain model only, no table macros).
 *  vs sys stats K            : exhaustive over all K-sets: max closure size, histogram of closure size
 *  vs sys full K part np     : exhaustive search for full-closure sets of size <= K, guesses in DECREASING index
 *                              order (the separable code uses increasing order), counter-based propagation
 *  vs sys rand n seed        : n random minimal full-closure sets (random order greedy + random minimisation);
 *                              size histogram; every size-8 set goes through the key scan below
 *  key scan of a set S       : for every core C subset of S with |C| <= 2 and delta(cl(C)) = |C|, every pair of
 *                              disjoint nonempty U1, U2 of S\C: kkey = d(U1) + d(U2) - (delta(R1 u R2) - |C|),
 *                              d(U) = delta(cl(C+U)) - |C|.  Also internal checks i(U) = |U| - d(U) of proper U.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 M;
#define MAXW 128
#define MAXE 256
static int N, E, F;
static char names[MAXW][32];
static M emask[MAXE];
static int esz[MAXE];
static int occ[MAXW][16], nocc[MAXW];
static M ALL;
static M bit(int i) { return ((M)1) << i; }
static int pc(M x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static int lowbit(M u) { return (uint64_t)u ? __builtin_ctzll((uint64_t)u) : 64 + __builtin_ctzll((uint64_t)(u >> 64)); }

static void load(const char *fn) {
    FILE *f = fopen(fn, "r"); if (!f) { perror(fn); exit(1); }
    int NM; if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        char nm[32]; int k; if (fscanf(f, "%31s %d", nm, &k) != 2) exit(4);
        emask[e] = 0; esz[e] = k;
        for (int j = 0; j < k; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(5); emask[e] |= bit(x); occ[x][nocc[x]++] = e; }
    }
    fclose(f);
    ALL = 0; for (int i = 0; i < N; i++) ALL |= bit(i);
}

/* plain fixpoint closure by full rescans (slow, simple; used for stats and key scans) */
static M cl(M K) {
    for (;;) {
        M K0 = K;
        for (int e = 0; e < E; e++) { M u = emask[e] & ~K; if (u && !(u & (u - 1))) K |= u; }
        if (K == K0) return K;
    }
}
static int delta(M X) { int c = 0; for (int e = 0; e < E; e++) if (!(emask[e] & ~X)) c++; return pc(X) - c; }

/* counter-based incremental propagation: cnt[e] = unknown words of e */
typedef struct { M K; unsigned char cnt[MAXE]; } St;
static void addw(St *s, int w) {
    int q[MAXW], qh = 0, qt = 0;
    s->K |= bit(w); q[qt++] = w;
    while (qh < qt) {
        int v = q[qh++];
        for (int j = 0; j < nocc[v]; j++) {
            int e = occ[v][j];
            if (--s->cnt[e] == 1) {
                M u = emask[e] & ~s->K;
                if (u) { int t = lowbit(u); s->K |= u; q[qt++] = t; }
            }
        }
    }
}
static void initst(St *s) { s->K = 0; for (int e = 0; e < E; e++) s->cnt[e] = (unsigned char)esz[e]; }

static long nodes, found[16];
static int Kmax, stk[16];
static void dfs(St *s, int depth, int below) {   /* next guess index < below */
    nodes++;
    if (s->K == ALL) { found[depth]++; printf("FULL k=%d:", depth); for (int i = 0; i < depth; i++) printf(" %d", stk[i]); printf("\n"); fflush(stdout); return; }
    if (depth == Kmax) return;
    for (int i = below - 1; i >= 0; i--) {
        if (s->K & bit(i)) continue;
        St t = *s; stk[depth] = i; addw(&t, i); dfs(&t, depth + 1, i);
    }
}

/* ---- key scan ---- */
static long hist_kkey[8], hist_int[8], nscanned;
static void keyscan(const int *S, int n, int verbose) {
    int bestk = 0, besti = 0; int bc = -1, b1 = 0, b2 = 0;
    for (int cm = 0; cm < (1 << n); cm++) {
        int csz = __builtin_popcount(cm); if (csz > 2) continue;
        M core = 0; int sp[16], s = 0;
        for (int j = 0; j < n; j++) { if (cm & (1 << j)) core |= bit(S[j]); else sp[s++] = S[j]; }
        if (delta(cl(core)) != csz) continue;
        int full = (1 << s) - 1;
        static M R[1 << 14]; static int d[1 << 14];
        for (int U = 0; U <= full; U++) {
            M T = core; for (int j = 0; j < s; j++) if (U & (1 << j)) T |= bit(sp[j]);
            R[U] = cl(T); d[U] = delta(R[U]) - csz;
            int iu = __builtin_popcount(U) - d[U];
            if (U != full && U && iu > besti) besti = iu;
        }
        for (int U1 = 1; U1 <= full; U1++)
            for (int U2 = (full ^ U1); U2; U2 = (U2 - 1) & (full ^ U1)) {
                if (U2 < U1) continue;
                int kk = d[U1] + d[U2] - (delta(R[U1] | R[U2]) - csz);
                if (kk > bestk) { bestk = kk; bc = cm; b1 = U1; b2 = U2; }
            }
    }
    nscanned++; hist_kkey[bestk > 7 ? 7 : bestk]++; hist_int[besti > 7 ? 7 : besti]++;
    if (verbose || bestk > 0 || besti > 0) {
        printf("SET"); for (int j = 0; j < n; j++) printf(" %s", names[S[j]]);
        printf("  max_kkey=%d max_internal_checks(proper U)=%d", bestk, besti);
        if (bestk > 0) printf(" core_mask=%d U1=%d U2=%d", bc, b1, b2);
        printf("\n"); fflush(stdout);
    }
}

static uint64_t rs;
static uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

int main(int argc, char **argv) {
    load(argv[1]);
    const char *mode = argv[2];
    if (!strcmp(mode, "stats")) {
        int K = atoi(argv[3]); static long h[MAXW + 1]; long sets = 0; int idx[8];
        for (int i = 0; i < K; i++) idx[i] = i;
        for (;;) {
            M T = 0; for (int i = 0; i < K; i++) T |= bit(idx[i]);
            h[pc(cl(T))]++; sets++;
            int p = K - 1; while (p >= 0 && idx[p] == N - K + p) p--;
            if (p < 0) break;
            idx[p]++; for (int i = p + 1; i < K; i++) idx[i] = idx[i - 1] + 1;
        }
        int mx = 0; for (int i = 0; i <= N; i++) if (h[i]) mx = i;
        printf("K=%d sets=%ld max_closure=%d\nhist:", K, sets, mx);
        for (int i = 0; i <= N; i++) if (h[i]) printf(" %d:%ld", i, h[i]);
        printf("\n");
    } else if (!strcmp(mode, "full")) {
        Kmax = atoi(argv[3]); int part = atoi(argv[4]), np = atoi(argv[5]); long pi = 0;
        for (int i = N - 1; i >= 0; i--) {
            St a; initst(&a); addw(&a, i); stk[0] = i;
            if (a.K == ALL) { if (!part) { found[1]++; printf("FULL k=1: %d\n", i); } continue; }
            for (int j = i - 1; j >= 0; j--) {
                if (a.K & bit(j)) continue;
                if ((pi++ % np) != part) continue;
                St b = a; stk[1] = j; addw(&b, j); dfs(&b, 2, j);
            }
        }
        printf("DONE part %d/%d K=%d nodes=%ld found:", part, np, Kmax, nodes);
        for (int i = 0; i <= Kmax; i++) printf(" k%d=%ld", i, found[i]);
        printf("\n");
    } else if (!strcmp(mode, "rand")) {
        long n = atol(argv[3]); rs = 0x9E3779B97F4A7C15ULL ^ (uint64_t)atol(argv[4]) * 0x2545F4914F6CDD1DULL;
        static long hs[MAXW + 1]; int maxscan = argc > 5 ? atoi(argv[5]) : 1000000; int scanned = 0;
        for (long t = 0; t < n; t++) {
            int perm[MAXW]; for (int i = 0; i < N; i++) perm[i] = i;
            for (int i = N - 1; i > 0; i--) { int j = rnd() % (i + 1); int x = perm[i]; perm[i] = perm[j]; perm[j] = x; }
            int S[MAXW], k = 0; St s; initst(&s);
            for (int i = 0; i < N && s.K != ALL; i++) if (!(s.K & bit(perm[i]))) { S[k++] = perm[i]; addw(&s, perm[i]); }
            /* random minimisation */
            int changed = 1;
            while (changed) {
                changed = 0;
                int ord[MAXW]; for (int i = 0; i < k; i++) ord[i] = i;
                for (int i = k - 1; i > 0; i--) { int j = rnd() % (i + 1); int x = ord[i]; ord[i] = ord[j]; ord[j] = x; }
                for (int r = 0; r < k; r++) {
                    int drop = ord[r]; M T = 0;
                    for (int i = 0; i < k; i++) if (i != drop) T |= bit(S[i]);
                    if (cl(T) == ALL) { S[drop] = S[k - 1]; k--; changed = 1; break; }
                }
            }
            hs[k]++;
            if (k == 8 && scanned < maxscan) { keyscan(S, k, 0); scanned++; }
        }
        printf("minimal-set size histogram:"); for (int i = 0; i <= N; i++) if (hs[i]) printf(" %d:%ld", i, hs[i]);
        printf("\nkey-scanned 8-sets: %ld  max_kkey histogram:", nscanned);
        for (int i = 0; i < 8; i++) if (hist_kkey[i]) printf(" %d:%ld", i, hist_kkey[i]);
        printf("  max internal-check histogram:");
        for (int i = 0; i < 8; i++) if (hist_int[i]) printf(" %d:%ld", i, hist_int[i]);
        printf("\n");
    }
    return 0;
}
