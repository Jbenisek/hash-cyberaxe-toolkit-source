/* split.c - search for a two-list (core / side A / side B) structure in the guess-and-determine model.
 *
 * Model (DERIVED, see NOTES.txt): words W (unknowns), equations E (each solvable for any one unknown word),
 * optional table macros (trigger words -> target word).  cl(T) = propagation closure of guess set T.
 * delta(X) = |X| - Ein(X)  (Ein = equations whose words all lie in X) = generic dimension of region X.
 * A split is (C, A, B) with X1 = cl(C+A), X2 = cl(C+B), X1 | X2 = all words.  Then
 *   cross checks cX = delta(X1) + delta(X2) - F - |C|,  side dims a = delta(X1)-|C|, b = delta(X2)-|C|,
 *   internal checks iA = |C+A| - delta(X1), iB likewise.
 * Modes:
 *   split sys stats K            closure-size / delta histogram over all K-sets
 *   split sys pairs c a b [maxprint]   all splits with |C|=c, |A|=a, |B|=b; prints best by cX
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
static int esz[MAXE];
static char ename[MAXE][24];
static M mtrig[4096];
static int mtgt[4096];
static M ALL;

static int pc(M x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static M bit(int i) { return ((M)1) << i; }

static M closure(M K) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int e = 0; e < E; e++) {
            M u = emask[e] & ~K;
            if (u && !(u & (u - 1))) { K |= u; ch = 1; }
        }
        for (int m = 0; m < NM; m++) {
            if (!(mtrig[m] & ~K) && !(K & bit(mtgt[m]))) { K |= bit(mtgt[m]); ch = 1; }
        }
    }
    return K;
}
static int ein(M X) { int c = 0; for (int e = 0; e < E; e++) if (!(emask[e] & ~X)) c++; return c; }
static int delta(M X) { return pc(X) - ein(X); }

static void load(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        int k; if (fscanf(f, "%23s %d", ename[e], &k) != 2) exit(4);
        emask[e] = 0; esz[e] = k;
        for (int j = 0; j < k; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(5); emask[e] |= bit(x); }
    }
    for (int m = 0; m < NM; m++) {
        int t; if (fscanf(f, "%d", &t) != 1) exit(6);
        mtrig[m] = 0;
        for (int j = 0; j < t; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(7); mtrig[m] |= bit(x); }
        if (fscanf(f, "%d", &mtgt[m]) != 1) exit(8);
    }
    fclose(f);
    ALL = 0; for (int i = 0; i < N; i++) ALL |= bit(i);
}

/* ---- dedup list of closures ---- */
typedef struct { M X; M T; int d; } Ent;
typedef struct { Ent *v; int n, cap; M *hk; int hcap; } List;
static uint64_t hh(M x) { uint64_t a = (uint64_t)x, b = (uint64_t)(x >> 64); a ^= b * 0x9E3779B97F4A7C15ULL; a ^= a >> 29; a *= 0xBF58476D1CE4E5B9ULL; a ^= a >> 32; return a; }
static void linit(List *L) { L->n = 0; L->cap = 1024; L->v = malloc(sizeof(Ent) * L->cap); L->hcap = 1 << 16; L->hk = calloc(L->hcap, sizeof(M)); }
static void lfree(List *L) { free(L->v); free(L->hk); }
static void ladd(List *L, M X, M T) {
    if (2 * (L->n + 1) > L->hcap) {
        int nc = L->hcap * 4; M *nk = calloc(nc, sizeof(M));
        for (int i = 0; i < L->hcap; i++) if (L->hk[i]) { uint64_t p = hh(L->hk[i]) & (nc - 1); while (nk[p]) p = (p + 1) & (nc - 1); nk[p] = L->hk[i]; }
        free(L->hk); L->hk = nk; L->hcap = nc;
    }
    uint64_t p = hh(X) & (L->hcap - 1);
    while (L->hk[p]) { if (L->hk[p] == X) return; p = (p + 1) & (L->hcap - 1); }
    L->hk[p] = X;
    if (L->n == L->cap) { L->cap *= 2; L->v = realloc(L->v, sizeof(Ent) * L->cap); }
    L->v[L->n].X = X; L->v[L->n].T = T; L->v[L->n].d = delta(X); L->n++;
}

/* enumerate all k-subsets of 'pool' words (bitmask), add closure of (core | subset) to list */
static int poolidx[MAXW], npool;
static void enum_sets(List *L, M core, int k, int start, M cur) {
    if (k == 0) {
        M T = core | cur;
        M X = closure(T);
        /* independence: skip if some guess of cur is implied by the others */
        for (M r = cur; r; r &= r - 1) {
            M lo = r & (~r + 1);
            if (closure(T & ~lo) & lo) return;
        }
        ladd(L, X, cur);
        return;
    }
    for (int i = start; i <= npool - k; i++) enum_sets(L, core, k - 1, i + 1, cur | bit(poolidx[i]));
}

static void prmask(FILE *o, M T) { for (int i = 0; i < N; i++) if (T & bit(i)) fprintf(o, " %s", names[i]); }

/* cost (log2) of the two-list attack; see NOTES.txt. members needed 2^64 */
static double cost(int c, int dA, int dB, int tA, int tB, int cX) {
    /* tA,tB = guesses per side beyond core; a=dA-c, b=dB-c side dims; iA = tA - a etc. */
    int a = dA - c, b = dB - c, iA = tA - a, iB = tB - b;
    double best = 1e9;
    for (double nu = 0; nu <= 32.0 * c; nu += 1) {
        for (double x = 0; x <= 32.0 * a; x += 1) {
            double y = 64 + 32.0 * cX - nu - x;   /* members = nu + x + y - 32cX = 64 */
            if (y < 0) y = 0;
            if (y > 32.0 * b) continue;
            double cA = nu + x + 32.0 * iA, cB = nu + y + 32.0 * iB;
            double m = cA > cB ? cA : cB;
            if (m < 64) m = 64;
            m += 1;
            if (m < best) best = m;
        }
    }
    return best;
}

int main(int argc, char **argv) {
    load(argv[1]);
    if (!strcmp(argv[2], "stats")) {
        int K = atoi(argv[3]);
        static long hs[MAXW + 1], hd[MAXW + 1];
        int idx[8];
        for (int i = 0; i < K; i++) idx[i] = i;
        long cnt = 0;
        while (1) {
            M T = 0; for (int i = 0; i < K; i++) T |= bit(idx[i]);
            M X = closure(T);
            hs[pc(X)]++; hd[delta(X)]++; cnt++;
            int j = K - 1; while (j >= 0 && idx[j] == N - K + j) j--;
            if (j < 0) break;
            idx[j]++; for (int i = j + 1; i < K; i++) idx[i] = idx[i - 1] + 1;
        }
        printf("K=%d sets=%ld\nclosure size histogram:", K, cnt);
        for (int i = 0; i <= N; i++) if (hs[i]) printf(" %d:%ld", i, hs[i]);
        printf("\ndelta histogram:");
        for (int i = 0; i <= N; i++) if (hd[i]) printf(" %d:%ld", i, hd[i]);
        printf("\n");
        return 0;
    }
    if (!strcmp(argv[2], "pairs")) {
        int c = atoi(argv[3]), a = atoi(argv[4]), b = atoi(argv[5]);
        int maxprint = argc > 6 ? atoi(argv[6]) : 20;
        int cidx[8]; for (int i = 0; i < c; i++) cidx[i] = i;
        long ncore = 0, npairs = 0, nhits = 0;
        int bestcX = 1 << 30; double bestcost = 1e9; int printed = 0;
        static long hcx[64];
        while (1) {
            M core = 0; for (int i = 0; i < c; i++) core |= bit(cidx[i]);
            int ok = 1;
            for (int i = 0; i < c && ok; i++) if (closure(core & ~bit(cidx[i])) & bit(cidx[i])) ok = 0;
            if (ok) {
                ncore++;
                M cc = closure(core);
                npool = 0; for (int i = 0; i < N; i++) if (!(cc & bit(i))) poolidx[npool++] = i;
                List LA, LB; linit(&LA); enum_sets(&LA, core, a, 0, 0);
                if (b != a) { linit(&LB); enum_sets(&LB, core, b, 0, 0); } else LB = LA;
                for (int i = 0; i < LA.n; i++) {
                    M U = ALL & ~LA.v[i].X;
                    int j0 = (b == a) ? i : 0;
                    for (int j = j0; j < LB.n; j++) {
                        if (U & ~LB.v[j].X) continue;
                        npairs++;
                        int dA = LA.v[i].d, dB = LB.v[j].d;
                        int cX = dA + dB - F - c;
                        if (cX < 0) cX = 0;
                        hcx[cX < 63 ? cX : 63]++;
                        nhits++;
                        double cs = cost(c, dA, dB, a, b, cX);
                        if (cX < bestcX) bestcX = cX;
                        if (cs < bestcost - 1e-9 || (printed < maxprint && cs <= bestcost + 1e-9)) {
                            if (cs < bestcost - 1e-9) printed = 0;
                            bestcost = cs;
                            printed++;
                            printf("cX=%d cost=%.1f c=%d dA=%d dB=%d |X1|=%d |X2|=%d |X1&X2|=%d  core:", cX, cs, c, dA, dB,
                                   pc(LA.v[i].X), pc(LB.v[j].X), pc(LA.v[i].X & LB.v[j].X));
                            prmask(stdout, core); printf("  A:"); prmask(stdout, LA.v[i].T);
                            printf("  B:"); prmask(stdout, LB.v[j].T); printf("\n");
                            fflush(stdout);
                        }
                    }
                }
                lfree(&LA); if (b != a) lfree(&LB);
            }
            if (c == 0) break;
            int j = c - 1; while (j >= 0 && cidx[j] == N - c + j) j--;
            if (j < 0) break;
            cidx[j]++; for (int i = j + 1; i < c; i++) cidx[i] = cidx[i - 1] + 1;
        }
        printf("DONE c=%d a=%d b=%d cores=%ld covering pairs=%ld bestcX=%d bestcost=%.1f\ncX histogram:", c, a, b, ncore, npairs,
               bestcX == (1 << 30) ? -1 : bestcX, bestcost);
        for (int i = 0; i < 64; i++) if (hcx[i]) printf(" %d:%ld", i, hcx[i]);
        printf("\n");
        return 0;
    }
    return 1;
}
