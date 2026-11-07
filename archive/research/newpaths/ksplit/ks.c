/* ks.c - hierarchical k-list split search over guess sets (ksplit folder).
 *
 * Model (see NOTES.txt): words W, equations E (each solvable for any one unknown), optional table macros.
 * cl(T) propagation closure; delta(X) = |X| - Ein(X).
 * A guess set G is split by a binary tree; each node T (a subset of G) has K_T = cl(T).
 * Join of children T1,T2:  sep  n = delta(K_T1) + delta(K_T2) - delta(K_T1 | K_T2)   (separable 32-bit conditions)
 *                          post p = delta(K_T1 | K_T2) - delta(K_T)                    (non-separable: filter)
 * Leaf T: list of 2^(32*delta(K_T)) valid assignments, enumerated at cost 2^(32*(|T|-delta(K_T))) each.
 * Cost model (log2, units): bound B; every list built and every join's pre-filter list <= 2^B; output list
 *   X(leaf) = min(32*delta, B - 32*l), X(node) = min(X1 + X2 - 32n, B) - 32p, every X >= 0; feasible if X(root) >= 64.
 * Modes:
 *   ks sys enum g proc nprocs [maxB]   : all valid g-sets over class reps (canonical, independent); best B per k
 *   ks sys one w1 w2 ... (word names)  : analyse one guess set, print best tree per k
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 M;
#define MAXW 130
#define MAXE 256
static int N, E, NM, F;
static char names[MAXW][32];
static M emask[MAXE];
static int etype[MAXE];   /* 0 additive, 1 xor(rot) */
static char ename[MAXE][24];
static int LIN = 0;        /* linear-chain refinement of separable checks */
static M mtrig[128];
static int mtgt[128];
static M ALL;
static int occ[MAXW][16], nocc[MAXW];

static int pc(M x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static M bit(int i) { return ((M)1) << i; }

static int mocc[MAXW][16], nmocc[MAXW];
static int bidx(M u) { uint64_t lo = (uint64_t)u; return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll((uint64_t)(u >> 64)); }
/* incremental closure: K already closed except for the words in 'fresh' */
static M closure_from(M K, M fresh) {
    int q[MAXW * 2], qh = 0, qt = 0;
    for (M r = fresh; r; r &= r - 1) q[qt++] = bidx(r & (~r + 1));
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) {
            M u = emask[occ[v][i]] & ~K;
            if (u && !(u & (u - 1))) { K |= u; q[qt++] = bidx(u); }
        }
        for (int i = 0; i < nmocc[v]; i++) {
            int m = mocc[v][i];
            if (!(mtrig[m] & ~K) && !(K & bit(mtgt[m]))) { K |= bit(mtgt[m]); q[qt++] = mtgt[m]; }
        }
    }
    return K;
}
static M closure(M K) { return closure_from(K, K); }
static int ein(M X) { int c = 0; for (int e = 0; e < E; e++) if (!(emask[e] & ~X)) c++; return c; }
static int delta(M X) { return pc(X) - ein(X); }

static void load(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        char nm[32]; int k;
        if (fscanf(f, "%31s %d", nm, &k) != 2) exit(4);
        strncpy(ename[e], nm, 23);
        emask[e] = 0;
        {
            char *c = strchr(nm, ':');
            if (!c) etype[e] = 1;                       /* out_i: xor relation */
            else etype[e] = (c[1] == 'a' || c[1] == 'c') ? 0 : 1;
        }
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
    for (int e = 0; e < E; e++) for (int v = 0; v < N; v++) if (emask[e] >> v & 1) occ[v][nocc[v]++] = e;
    for (int m = 0; m < NM; m++) for (int v = 0; v < N; v++) if (mtrig[m] >> v & 1) mocc[v][nmocc[v]++] = m;
}

/* closure of J under equations of one group only (no tables): words that are group-linear in J */
static M linclosure(M K, int ty) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int e = 0; e < E; e++) {
            if (etype[e] != ty) continue;
            M u = emask[e] & ~K;
            if (u && !(u & (u - 1))) { K |= u; ch = 1; }
        }
    }
    return K;
}
static int ein_t(M X, int ty) { int c = 0; for (int e = 0; e < E; e++) if (etype[e] == ty && !(emask[e] & ~X)) c++; return c; }
/* number of extra separable (group-linear) checks of the join J beyond those inside J */
static int linchecks(M J) {
    int tot = 0;
    for (int ty = 0; ty < 2; ty++) {
        M L = linclosure(J, ty);
        if (L == J) continue;
        tot += ein_t(L, ty) - ein_t(J, ty) - pc(L & ~J);
    }
    return tot;
}

/* ---------------- analysis of one guess set ---------------- */
#define MAXG 12
#define NEG (-1000000)
static int g;
static M KT[1 << MAXG];
static int dT[1 << MAXG], szT[1 << MAXG];
typedef struct { unsigned short t1; signed char n, p; } Split;
static Split *spl[1 << MAXG];
static int nspl[1 << MAXG];
static Split splbuf[600000];
static int X[1 << MAXG][MAXG + 1];
static int arg[1 << MAXG][MAXG + 1][2];   /* split index, k1 */

static void prep(const int *G) {
    int full = (1 << g) - 1, used = 0;
    for (int T = 1; T <= full; T++) {
        M s = 0;
        for (int i = 0; i < g; i++) if (T >> i & 1) s |= bit(G[i]);
        KT[T] = closure(s); dT[T] = delta(KT[T]); szT[T] = __builtin_popcount(T);
    }
    for (int T = 1; T <= full; T++) {
        spl[T] = splbuf + used; nspl[T] = 0;
        if (szT[T] < 2) continue;
        int low = T & -T;
        for (int a = (T - 1) & T; a > 0; a = (a - 1) & T) {
            if (!(a & low)) continue;
            int b = T ^ a;
            int dU = delta(KT[a] | KT[b]);
            Split s; s.t1 = a; s.n = dT[a] + dT[b] - dU; s.p = dU - dT[T];
            if (LIN && s.p > 0) {
                int lc = linchecks(KT[a] | KT[b]);
                if (lc > s.p) { fprintf(stderr, "lin>post?\n"); lc = s.p; }
                s.n += lc; s.p -= lc;
            }
            spl[T][nspl[T]++] = s;
        }
        used += nspl[T];
    }
}

/* DP at bound B (bits). returns X[full][k] */
static void dp(int B) {
    int full = (1 << g) - 1;
    for (int T = 1; T <= full; T++) {
        for (int k = 0; k <= g; k++) X[T][k] = NEG;
        int l = szT[T] - dT[T];
        int x = 32 * dT[T]; if (B - 32 * l < x) x = B - 32 * l;
        if (x >= 0) X[T][1] = x;
        arg[T][1][0] = -1;
        for (int si = 0; si < nspl[T]; si++) {
            Split s = spl[T][si];
            int a = s.t1, b = T ^ a;
            for (int k1 = 1; k1 <= szT[a]; k1++) {
                if (X[a][k1] == NEG) continue;
                for (int k2 = 1; k2 <= szT[b]; k2++) {
                    if (X[b][k2] == NEG) continue;
                    int pre = X[a][k1] + X[b][k2] - 32 * s.n;
                    if (pre > B) pre = B;
                    int v = pre - 32 * s.p;
                    if (v < 0) continue;
                    if (v > X[T][k1 + k2]) { X[T][k1 + k2] = v; arg[T][k1 + k2][0] = si; arg[T][k1 + k2][1] = k1; }
                }
            }
        }
    }
}

static int bestB[MAXG + 1];
static const int BGRID[] = {64, 66, 68, 70, 72, 74, 76, 78, 80, 82, 85, 88, 92, 96, 100, 110, 128, 160, 192, 224, 256};
#define NBG ((int)(sizeof(BGRID) / sizeof(BGRID[0])))
static int anysep;     /* some split anywhere has n > 0 */
static int FASTGATE = 0;   /* if set: first test B = FASTGATE; if nothing feasible, stop (bestB = 999) */
static void solve_all(int maxB) {
    int full = (1 << g) - 1;
    for (int k = 1; k <= g; k++) bestB[k] = 999;
    int need = g;
    if (FASTGATE) {
        dp(FASTGATE);
        int any = 0;
        for (int k = 1; k <= g; k++) if (X[full][k] >= 64) any = 1;
        if (!any) return;
    }
    for (int bi = 0; bi < NBG && need > 0; bi++) {
        int B = BGRID[bi];
        if (B > maxB) break;
        dp(B);
        for (int k = 1; k <= g; k++)
            if (bestB[k] == 999 && X[full][k] >= 64) { bestB[k] = B; need--; }
    }
}
static const int *curG;
static void prtree(FILE *o, int T, int k, int B) {
    if (k == 1) {
        fprintf(o, "{");
        int first = 1;
        for (int i = 0; i < g; i++) if (T >> i & 1) { fprintf(o, first ? "%s" : " %s", names[curG[i]]); first = 0; }
        fprintf(o, "|d%d", dT[T]);
        fprintf(o, "}");
        return;
    }
    int si = arg[T][k][0], k1 = arg[T][k][1];
    Split s = spl[T][si];
    fprintf(o, "(");
    prtree(o, s.t1, k1, B);
    fprintf(o, " + ");
    prtree(o, T ^ s.t1, k - k1, B);
    fprintf(o, ")[n%d p%d X%d]", s.n, s.p, X[T][k]);
}

/* ---------------- enumeration ---------------- */
static int reps[MAXW], NR;
static int G[MAXG];
static long long nfound = 0;
static int proc = 0, nprocs = 1, MAXB = 100;
static long long histB[MAXG + 1][300];
static int globbest[MAXG + 1];
static int depthG;

static long long histP[64], histNP[64][64], nsepsets = 0;
static int bestP = 99;
static int EXTRA = 0;
static void analyze(const int *Gs, int gg) {
    g = gg; curG = Gs;
    prep(Gs);
    int full = (1 << g) - 1, mp = 99, mn = 99;
    for (int si = 0; si < nspl[full]; si++) {
        Split s = spl[full][si];
        if (s.p < mp || (s.p == mp && s.n < mn)) { mp = s.p; mn = s.n; }
    }
    histP[mp]++; histNP[mp][mn]++;
    anysep = 0;
    for (int T = 1; T <= full && !anysep; T++) for (int si = 0; si < nspl[T]; si++) if (spl[T][si].n > 0) { anysep = 1; break; }
    if (mp < bestP) {
        bestP = mp;
        printf("new best rootpost=%d n=%d set:", mp, mn);
        for (int i = 0; i < g; i++) printf(" %s", names[Gs[i]]);
        printf("\n");
    }
    if (!anysep) {
        for (int k = 1; k <= g; k++) histB[k][299]++;
        return;
    }
    nsepsets++;
    solve_all(MAXB);
    for (int k = 1; k <= g; k++) {
        int b = bestB[k];
        histB[k][b > 298 ? 298 : b]++;
        if (b <= MAXB && b < globbest[k]) {
            globbest[k] = b;
            dp(b);
            printf("k=%d B=%d set:", k, b);
            for (int i = 0; i < g; i++) printf(" %s", names[Gs[i]]);
            printf("\n   tree: ");
            prtree(stdout, (1 << g) - 1, k, b);
            printf("\n");
            fflush(stdout);
        }
    }
}
static int G9[MAXG];
/* WHY mode: for every bipartition (A,B) of the set, U = cl(A) | cl(B); count round-1 C-call equations inside U,
 * C calls with all 8 equations inside U, and |U|.  Histograms of the per-set maxima. */
static int WHY = 0;
static long long whyC[40], whyFull[5], whyU[MAXW + 1], whyAny[40];
static M cmask[4][8]; static int ncm[4];
static void why_set(void) {
    static int init = 0;
    if (!init) {
        init = 1;
        /* equation names are not kept; rebuild C-call masks from word names: an equation belongs to call Cj if
           it contains a word named "Cj." -- every C-call equation contains at least one internal word */
    }
    int full = (1 << g) - 1;
    M Ks[1 << MAXG];
    for (int T = 1; T <= full; T++) { M s = 0; for (int i = 0; i < g; i++) if (T >> i & 1) s |= bit(G[i]); Ks[T] = closure(s); }
    int bestC = 0, bestFull = 0, bestU = 0;
    for (int a = 1; a < full; a++) {
        if (!(a & 1)) continue;
        M U = Ks[a] | Ks[full ^ a];
        int c = 0, fc = 0;
        for (int j = 0; j < 4; j++) {
            int in = 0;
            for (int q = 0; q < ncm[j]; q++) if (!(cmask[j][q] & ~U)) in++;
            c += in; if (in == ncm[j]) fc++;
        }
        if (c > bestC) bestC = c;
        if (fc > bestFull) bestFull = fc;
        if (pc(U) > bestU) bestU = pc(U);
    }
    whyC[bestC]++; whyFull[bestFull]++; whyU[bestU]++;
}
static void report_set(void) {
    int g0 = g;
    if (WHY) { why_set(); return; }
    if (!EXTRA) { analyze(G, g0); return; }
    for (int w = 0; w < N; w++) {
        int dup = 0;
        for (int i = 0; i < g0; i++) { G9[i] = G[i]; if (G[i] == w) dup = 1; }
        if (dup) continue;
        G9[g0] = w;
        analyze(G9, g0 + 1);
    }
    g = g0;
}

static void dfs(int depth, int start, M known) {
    if (depth == g) {
        if (known == ALL) { nfound++; report_set(); if (nfound % 1000 == 0) { fprintf(stderr, "progress %lld sets\n", nfound); } }
        return;
    }
    for (int j = start; j < NR; j++) {
        int v = reps[j];
        if ((known >> v) & 1) continue;
        if (depth == 1 && ((G[0] * 131 + j) % nprocs) != proc) continue;
        G[depth] = v;
        dfs(depth + 1, j + 1, closure_from(known | bit(v), bit(v)));
    }
}

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage\n"); return 1; }
    load(argv[1]);
    if (getenv("KS_LIN")) LIN = atoi(getenv("KS_LIN"));
    if (getenv("KS_WHY")) WHY = atoi(getenv("KS_WHY"));
    for (int e = 0; e < E; e++)
        if (ename[e][0] == 'C' && ename[e][2] == ':') { int j = ename[e][1] - '0'; cmask[j][ncm[j]++] = emask[e]; }
    /* class representatives: distinct singleton closures */
    {
        M seen[MAXW]; int ns = 0;
        for (int v = 0; v < N; v++) {
            M c = closure(bit(v)); int dup = 0;
            for (int i = 0; i < ns; i++) if (seen[i] == c) { dup = 1; break; }
            if (!dup) { seen[ns++] = c; reps[NR++] = v; }
        }
    }
    if (!strcmp(argv[2], "enum")) {
        g = atoi(argv[3]); proc = atoi(argv[4]); nprocs = atoi(argv[5]);
        if (argc > 6) MAXB = atoi(argv[6]);
        if (getenv("KS_EXTRA")) EXTRA = atoi(getenv("KS_EXTRA"));
        if (getenv("KS_GATE")) FASTGATE = atoi(getenv("KS_GATE"));
        for (int k = 0; k <= MAXG; k++) globbest[k] = MAXB + 1;
        printf("N=%d E=%d F=%d macros=%d reps=%d g=%d proc=%d/%d maxB=%d\n", N, E, F, NM, NR, g, proc, nprocs, MAXB);
        dfs(0, 0, 0);
        printf("DONE valid_sets=%lld (extra=%d) sets_with_any_separable_condition=%lld\n", nfound, EXTRA, nsepsets);
        if (WHY) {
            printf("WHY per-set max over bipartitions of C-call equations inside cl(A)|cl(B) (of 32):");
            for (int i = 0; i < 40; i++) if (whyC[i]) printf(" %d:%lld", i, whyC[i]);
            printf("\nWHY per-set max number of C calls with all 8 equations inside:");
            for (int i = 0; i < 5; i++) if (whyFull[i]) printf(" %d:%lld", i, whyFull[i]);
            printf("\nWHY per-set max |cl(A)|cl(B)| (of %d words):", N);
            for (int i = 0; i <= N; i++) if (whyU[i]) printf(" %d:%lld", i, whyU[i]);
            printf("\n");
            return 0;
        }
        g = g + EXTRA;
        printf("min root post histogram (p:n count):");
        for (int p = 0; p < 64; p++) for (int n = 0; n < 64; n++) if (histNP[p][n]) printf(" p%d:n%d:%lld", p, n, histNP[p][n]);
        printf("\n");
        for (int k = 1; k <= g; k++) {
            printf("k=%d histogram of best B (298 = none <= maxB, 299 = no separable condition anywhere):", k);
            for (int b = 0; b < 300; b++) if (histB[k][b]) printf(" %d:%lld", b, histB[k][b]);
            printf("\n");
        }
        return 0;
    }
    if (!strcmp(argv[2], "glob")) {
        /* glob <file of index lists, one set per line, first token = count>: cheap structure stats for large sets */
        FILE *f = fopen(argv[3], "r");
        if (!f) { perror(argv[3]); return 1; }
        int gg, cnt = 0, nglobal = 0;
        static M Kc[1 << 20];
        static int dK[1 << 20];
        while (fscanf(f, "%d", &gg) == 1) {
            int Gs[24];
            for (int i = 0; i < gg; i++) if (fscanf(f, "%d", &Gs[i]) != 1) return 2;
            if (gg > 20) continue;
            int full = (1 << gg) - 1;
            M s = 0; for (int i = 0; i < gg; i++) s |= bit(Gs[i]);
            int covers = closure(s) == ALL;
            /* closures of all subsets, incremental from subset minus top bit */
            Kc[0] = 0; dK[0] = 0;
            for (int T = 1; T <= full; T++) {
                int hb = 31 - __builtin_clz(T);
                Kc[T] = closure_from(Kc[T ^ (1 << hb)] | bit(Gs[hb]), bit(Gs[hb]));
                dK[T] = delta(Kc[T]);
            }
            /* smallest subset carrying an internal condition */
            int minsz = 99;
            for (int T = 1; T < full; T++) if (dK[T] < __builtin_popcount(T) && __builtin_popcount(T) < minsz) minsz = __builtin_popcount(T);
            /* root bipartitions */
            int maxn = -99, minp = 99, bestnp_n = 0, nsplitsep = 0;
            for (int a = 1; a < full; a++) {
                if (!(a & 1)) continue;
                int b = full ^ a;
                int dU = delta(Kc[a] | Kc[b]);
                int n = dK[a] + dK[b] - dU, p = dU - dK[full];
                if (LIN && p > 0) { int lc = linchecks(Kc[a] | Kc[b]); if (lc > p) lc = p; n += lc; p -= lc; }
                if (n > maxn) maxn = n;
                if (n > 0) nsplitsep++;
                if (p < minp || (p == minp && n > bestnp_n)) { minp = p; bestnp_n = n; }
            }
            int glob = (minsz == 99 && maxn <= 0);
            nglobal += glob;
            cnt++;
            printf("set %d g=%d covers=%d full=%d smallest_subset_with_condition=%d root: max_n=%d splits_with_n>0=%d min_p=%d (n=%d) %s\n",
                   cnt, gg, covers, gg - dK[full], minsz == 99 ? 0 : minsz, maxn, nsplitsep, minp, bestnp_n, glob ? "GLOBAL" : "");
        }
        printf("DONE sets=%d global=%d\n", cnt, nglobal);
        return 0;
    }
    if (!strcmp(argv[2], "one")) {
        g = argc - 3;
        for (int i = 0; i < g; i++) {
            G[i] = -1;
            for (int v = 0; v < N; v++) if (!strcmp(names[v], argv[3 + i])) G[i] = v;
            if (G[i] < 0) { fprintf(stderr, "unknown word %s\n", argv[3 + i]); return 1; }
        }
        M s = 0; for (int i = 0; i < g; i++) s |= bit(G[i]);
        printf("closure covers all: %d (|cl|=%d of %d)\n", closure(s) == ALL, pc(closure(s)), N);
        MAXB = 256;
        curG = G; prep(G); solve_all(MAXB);
        for (int k = 1; k <= g; k++) {
            printf("k=%d bestB=%d ", k, bestB[k]);
            if (bestB[k] <= MAXB) { dp(bestB[k]); prtree(stdout, (1 << g) - 1, k, bestB[k]); }
            printf("\n");
        }
        return 0;
    }
    return 0;
}
