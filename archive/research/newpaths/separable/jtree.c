/* jtree.c - best multi-level join tree ("join, then propagate") over a full-closure guess set S.
 *
 * For a guess set S (cl(S) = all) and a core C subset of S, every subset U of S' = S \ C defines a region
 * R(U) = cl(C + U) with dimension d(U) = delta(R(U)) - |C| (words, per core value).
 * A list for U is a random subset of the solutions of region R(U), log-size L <= 32 d(U).
 *   leaf:  enumerate 2^e guesses of U (e <= B), keep L = e - 32 i(U), i(U) = |U| - d(U) internal checks.
 *   join:  U = U1 + U2.  k = d(U1) + d(U2) - d(U) conditions in total, kkey = d(U1) + d(U2) - dim(R1 u R2)
 *          of them form the join key (separable), the rest are filters after propagating R1 u R2 -> R(U).
 *          L = L1 + L2 - 32 k, pre-filter size L1 + L2 - 32 kkey <= B.
 * Per-core budget B (log2): every enumeration and list <= B.  Total cost = nu + B + 1, members = nu + L(S') >= 64,
 * nu = log2(number of core values) <= 32|C|.  Reports the minimum total cost over cores |C| <= 3 and trees.
 * Usage: jtree sys setsfile [maxC]      setsfile lines: "FULL k=8: i1 i2 ..." (word indices)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 M;
#define MAXW 128
#define MAXE 256
#define MAXS 14
static int N, E, NM, F;
static char names[MAXW][32];
static M emask[MAXE];
static M mtrig[4096];
static int mtgt[4096];
static M ALL;
static M bit(int i) { return ((M)1) << i; }
static int pc(M x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static M closure(M K) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int e = 0; e < E; e++) { M u = emask[e] & ~K; if (u && !(u & (u - 1))) { K |= u; ch = 1; } }
        for (int m = 0; m < NM; m++) if (!(mtrig[m] & ~K) && !(K & bit(mtgt[m]))) { K |= bit(mtgt[m]); ch = 1; }
    }
    return K;
}
static int delta(M X) { int c = 0; for (int e = 0; e < E; e++) if (!(emask[e] & ~X)) c++; return pc(X) - c; }
static void load(const char *fn) {
    FILE *f = fopen(fn, "r"); if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        char nm[32]; int k; if (fscanf(f, "%31s %d", nm, &k) != 2) exit(4);
        emask[e] = 0; for (int j = 0; j < k; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(5); emask[e] |= bit(x); }
    }
    for (int m = 0; m < NM; m++) {
        int t; if (fscanf(f, "%d", &t) != 1) exit(6);
        mtrig[m] = 0; for (int j = 0; j < t; j++) { int x; if (fscanf(f, "%d", &x) != 1) exit(7); mtrig[m] |= bit(x); }
        if (fscanf(f, "%d", &mtgt[m]) != 1) exit(8);
    }
    fclose(f);
    ALL = 0; for (int i = 0; i < N; i++) ALL |= bit(i);
}

static int s;                 /* |S'| */
static M Rg[1 << MAXS];       /* region per subset */
static int dg[1 << MAXS], ig[1 << MAXS];
static double Lm[1 << MAXS];
static int how[1 << MAXS];    /* 0 leaf, else U1 */

static signed char *kp;       /* kpost per (U, U1), computed by prep() */
static int coreSz;
static void prep(void) {
    int full = (1 << s) - 1;
    for (int U = 1; U <= full; U++) {
        int low = U & -U;
        for (int U1 = (U - 1) & U; U1; U1 = (U1 - 1) & U) {
            if (!(U1 & low)) continue;
            int U2 = U ^ U1;
            int k = dg[U1] + dg[U2] - dg[U];
            int dunion = delta(Rg[U1] | Rg[U2]) - coreSz;
            int kkey = dg[U1] + dg[U2] - dunion;
            int kpost = k - kkey; if (kpost < 0) kpost = 0;
            kp[(size_t)U * (full + 1) + U1] = (signed char)kpost;
        }
    }
}
static double lmax(int B) {
    int full = (1 << s) - 1;
    for (int U = 1; U <= full; U++) {
        double best = -1e9; int hb = 0;
        double leaf = 32.0 * dg[U];
        if (B - 32.0 * ig[U] < leaf) leaf = B - 32.0 * ig[U];
        if (leaf >= 0) { best = leaf; hb = 0; }
        /* splits: U1 contains lowest bit of U */
        int low = U & -U;
        for (int U1 = (U - 1) & U; U1; U1 = (U1 - 1) & U) {
            if (!(U1 & low)) continue;
            int U2 = U ^ U1;
            if (Lm[U1] < 0 || Lm[U2] < 0) continue;
            int k = dg[U1] + dg[U2] - dg[U];
            double L = Lm[U1] + Lm[U2] - 32.0 * k;
            if (L > 32.0 * dg[U]) L = 32.0 * dg[U];
            if (L <= best) continue;
            int kpost = kp[(size_t)U * (full + 1) + U1];
            double cap = B - 32.0 * kpost;
            if (L > cap) L = cap;
            if (L > best) { best = L; hb = U1; }
        }
        Lm[U] = best; how[U] = hb;
    }
    return Lm[full];
}

static int Sidx[MAXS + 4], Sp[MAXS + 4];

static int feasible(int Bt, int csz) {
    int numin = 64 - 32 * (F - csz); if (numin < 0) numin = 0;
    for (int nu = numin; nu <= 32 * csz && nu <= Bt - 64; nu += 2) {
        double L = lmax(Bt - nu);
        if (nu + L >= 64) return nu + 1;
    }
    return 0;
}

static void prtree(int U, int depth, FILE *o) {
    for (int i = 0; i < depth; i++) fprintf(o, "  ");
    fprintf(o, "[d=%d L=%.0f |R|=%d]", dg[U], Lm[U], pc(Rg[U]));
    if (!how[U]) {
        fprintf(o, " leaf i=%d:", ig[U]);
        for (int j = 0; j < s; j++) if (U & (1 << j)) fprintf(o, " %s", names[Sp[j]]);
        fprintf(o, "\n");
    } else {
        int U1 = how[U], U2 = U ^ U1;
        int k = dg[U1] + dg[U2] - dg[U];
        fprintf(o, " join k=%d\n", k);
        prtree(U1, depth + 1, o); prtree(U2, depth + 1, o);
    }
}

static void setup(int n, int cm, M *corep) {
    M core = 0; s = 0; int csz = __builtin_popcount(cm); coreSz = csz;
    for (int j = 0; j < n; j++) { if (cm & (1 << j)) core |= bit(Sidx[j]); else Sp[s++] = Sidx[j]; }
    int full = (1 << s) - 1;
    for (int U = 0; U <= full; U++) {
        M T = core; int nu = 0;
        for (int j = 0; j < s; j++) if (U & (1 << j)) { T |= bit(Sp[j]); nu++; }
        Rg[U] = closure(T); dg[U] = delta(Rg[U]) - csz; ig[U] = nu - dg[U];
    }
    dg[0] = 0;
    *corep = core;
}

int main(int argc, char **argv) {
    load(argv[1]);
    FILE *f = fopen(argv[2], "r"); if (!f) { perror(argv[2]); return 1; }
    int maxC = argc > 3 ? atoi(argv[3]) : 3;
    double printbelow = argc > 4 ? atof(argv[4]) : 90;
    kp = malloc((size_t)1 << (2 * 12));
    char line[4096];
    double gbest = 1e9; long nsets = 0;
    static long hist[200];
    while (fgets(line, sizeof line, f)) {
        if (strncmp(line, "FULL", 4)) continue;
        char *p = strchr(line, ':'); if (!p) continue; p++;
        int n = 0; char *tok = strtok(p, " \n");
        while (tok) { Sidx[n++] = atoi(tok); tok = strtok(NULL, " \n"); }
        if (n - 0 > 12 + maxC) continue;
        nsets++;
        int sbest = 1000; int bestC = -1;
        for (int cm = 0; cm < (1 << n); cm++) {
            int csz = __builtin_popcount(cm); if (csz > maxC || n - csz > 12) continue;
            M core;
            setup(n, cm, &core);
            if (delta(closure(core)) != csz) continue;      /* core not independent */
            if (Rg[(1 << s) - 1] != ALL) continue;
            prep();
            int hi = sbest - 2; if (hi > 200) hi = 200;
            if (hi < 64 || !feasible(hi, csz)) continue;
            int lo = 63;                                   /* infeasible */
            while (hi - lo > 1) { int mid = (lo + hi) / 2; if (feasible(mid, csz)) hi = mid; else lo = mid; }
            sbest = hi + 1; bestC = cm;
        }
        if (sbest < 200) hist[sbest]++; else hist[199]++;
        if (sbest < gbest || sbest < printbelow) {
            if (sbest < gbest) gbest = sbest;
            printf("set %ld cost %d core:", nsets, sbest);
            for (int j = 0; j < n; j++) if (bestC >= 0 && (bestC & (1 << j))) printf(" %s", names[Sidx[j]]);
            printf("  S:"); for (int j = 0; j < n; j++) printf(" %s", names[Sidx[j]]); printf("\n");
            if (bestC >= 0) {
                M core; setup(n, bestC, &core); prep();
                int csz = coreSz;
                int nu = feasible(sbest - 1, csz) - 1;
                if (nu >= 0) {
                    lmax(sbest - 1 - nu);
                    printf("  nu=%d per-core budget %d\n", nu, sbest - 1 - nu);
                    prtree((1 << s) - 1, 1, stdout);
                }
            }
            fflush(stdout);
        }
    }
    printf("DONE sets=%ld best=%.0f\ncost histogram:", nsets, gbest);
    for (int i = 0; i < 200; i++) if (hist[i]) printf(" %d:%ld", i, hist[i]);
    printf("\n");
    return 0;
}
