/* bd.c - free-width join trees (branch decompositions) of the gd_order constraint hypergraph.  shape_any agent.

   Model (DERIVED, generic counting, each primitive equation = one 32-bit condition, solvable in any one word):
     cluster A (set of equations), W(A) its words, B(A) = W(A) & W(rest) its boundary.
     list of A  = projection of Sol(A) on B(A); log2 size / 32 = rho(A, B(A)).
     rho(A, Z)  = min_{Z <= Y} |Y| - e_A(Y) = |Z| - (|A| - maxmatching(A, W(A)\Z))      (Hall / Konig)
     join of clusters A1, A2 (hash join on shared words, memory free): output = projection of Sol(A1+A2) on
       B(A1)|B(A2); J = rho(A1+A2, B(A1)|B(A2)).  Single equations are virtual leaves (never materialised).
     width of a tree = max J over its joins (words).  Work ~ (#joins) * 2^(32 width) list entries.

   Modes:
     agg  <sys> <runs> <seed>      : randomized greedy agglomerative merging (any binary tree shape)
     elim <sys> <runs> <seed>      : randomized greedy elimination order (bucket elimination, best binarization)
     exact <sys> <w> <nodelimit>   : DFS over elimination states: is there an elimination tree of width <= w?
     cut  <sys> <k> <iters> <seed> : local search for small rho(A,B(A)) with k <= |A| < 2k (upper bound on LB(k))
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 u128;
#define BIT(i) (((u128)1) << (i))
static int N, E, F;
static char vname[128][24], ename[128][24];
static int ek[128], ev[128][4];
static u128 eqv[128], occ[128], ALLE;

static inline int pc(u128 x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static inline int ctz(u128 x) { uint64_t lo = (uint64_t)x; return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll((uint64_t)(x >> 64)); }

static uint64_t rs = 88172645463325252ULL;
static inline uint64_t rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }

static u128 Wof(u128 A) { u128 w = 0; while (A) { int e = ctz(A); A &= A - 1; w |= eqv[e]; } return w; }
static u128 Bof(u128 A) { return Wof(A) & Wof(ALLE & ~A); }

static int matchV[128], vis[128], stamp;
static u128 avail;
static int aug(int e) {
    for (int j = 0; j < ek[e]; j++) {
        int v = ev[e][j];
        if (!((avail >> v) & 1) || vis[v] == stamp) continue;
        vis[v] = stamp;
        if (matchV[v] < 0 || aug(matchV[v])) { matchV[v] = e; return 1; }
    }
    return 0;
}
static int rho(u128 A, u128 Z) {
    avail = Wof(A) & ~Z;
    for (int v = 0; v < N; v++) matchV[v] = -1;
    int unm = 0;
    u128 a = A;
    while (a) { int e = ctz(a); a &= a - 1; stamp++; if (!aug(e)) unm++; }
    return pc(Z) - unm;
}

static void readsys(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d", &N, &E, &F) != 3) exit(2);
    if (N > 128 || E > 128) { fprintf(stderr, "too big\n"); exit(3); }
    for (int i = 0; i < N; i++) if (fscanf(f, "%23s", vname[i]) != 1) exit(2);
    ALLE = 0;
    for (int e = 0; e < E; e++) {
        if (fscanf(f, "%23s %d", ename[e], &ek[e]) != 2) exit(2);
        eqv[e] = 0;
        for (int j = 0; j < ek[e]; j++) { if (fscanf(f, "%d", &ev[e][j]) != 1) exit(2); eqv[e] |= BIT(ev[e][j]); occ[ev[e][j]] |= BIT(e); }
        ALLE |= BIT(e);
    }
    fclose(f);
}

/* ---------- tree bookkeeping ---------- */
typedef struct { u128 A, B; int r, J, l, rt; } Node;
static Node nd[512];
static int nn;
static Node best_nd[512];
static int best_nn = 0, best_w = 1 << 30, best_sumexp = 1 << 30;

static int leafnode(int e) { nd[nn].A = BIT(e); nd[nn].B = Bof(BIT(e)); nd[nn].r = -1; nd[nn].J = 0; nd[nn].l = nd[nn].rt = -1; return nn++; }
static int mergenode(int a, int b) {
    u128 A = nd[a].A | nd[b].A;
    nd[nn].A = A; nd[nn].B = Bof(A);
    nd[nn].J = rho(A, nd[a].B | nd[b].B);
    nd[nn].r = rho(A, nd[nn].B);
    nd[nn].l = a; nd[nn].rt = b;
    return nn++;
}

static void callsummary(u128 A, char *buf) {
    /* "K1:8 D0:3 ..." : equations per G call */
    char calls[40][8]; int cnt[40], nc = 0;
    buf[0] = 0;
    u128 a = A;
    while (a) {
        int e = ctz(a); a &= a - 1;
        char c[8]; int i = 0;
        while (ename[e][i] && ename[e][i] != ':' && i < 7) { c[i] = ename[e][i]; i++; }
        c[i] = 0;
        int k;
        for (k = 0; k < nc; k++) if (!strcmp(calls[k], c)) break;
        if (k == nc) { strcpy(calls[nc], c); cnt[nc] = 0; nc++; }
        cnt[k]++;
    }
    for (int k = 0; k < nc; k++) { char t[64]; snprintf(t, sizeof t, "%s%.8s%d", k ? " " : "", calls[k], cnt[k]); strcat(buf, t); }
}

static void printtree(Node *T, int id, int depth, FILE *o) {
    char buf[1024];
    if (T[id].l < 0) {
        int e = ctz(T[id].A);
        fprintf(o, "%*s- %s\n", depth * 2, "", ename[e]);
        return;
    }
    /* compress chains of leaf extensions */
    callsummary(T[id].A, buf);
    fprintf(o, "%*s+ J=%d list=%d |A|=%d |B|=%d  [%s]\n", depth * 2, "", T[id].J, T[id].r, pc(T[id].A), pc(T[id].B), buf);
    int L = T[id].l, R = T[id].rt;
    if (T[L].l < 0 && T[R].l >= 0) { int t = L; L = R; R = t; }
    printtree(T, L, depth + 1, o);
    printtree(T, R, depth + 1, o);
}

static int treewidth_of(Node *T, int n, int *sumexp) {
    int w = 0; long s = 0;
    for (int i = 0; i < n; i++) if (T[i].l >= 0) { if (T[i].J > w) w = T[i].J; }
    for (int i = 0; i < n; i++) if (T[i].l >= 0 && T[i].J == w) s++;
    *sumexp = (int)s;
    return w;
}

static void consider_best(void) {
    int s, w = treewidth_of(nd, nn, &s);
    if (w < best_w || (w == best_w && s < best_sumexp)) {
        best_w = w; best_sumexp = s; best_nn = nn;
        memcpy(best_nd, nd, sizeof(Node) * nn);
    }
}

/* ---------- mode agg ---------- */
static int pJ[512][512], pR[512][512];
static void run_agg(int temp) {
    nn = 0;
    int act[256], na = 0;
    for (int e = 0; e < E; e++) act[na++] = leafnode(e);
    for (int i = 0; i < na; i++) for (int j = i + 1; j < na; j++) {
        int a = act[i], b = act[j];
        if (!(Wof(nd[a].A) & Wof(nd[b].A))) { pJ[a][b] = pJ[b][a] = 9999; continue; }
        u128 A = nd[a].A | nd[b].A;
        pJ[a][b] = pJ[b][a] = rho(A, nd[a].B | nd[b].B);
        pR[a][b] = pR[b][a] = rho(A, Bof(A));
    }
    while (na > 1) {
        long bestkey = 1L << 60; int bi = -1, bj = -1;
        for (int i = 0; i < na; i++) for (int j = i + 1; j < na; j++) {
            int a = act[i], b = act[j];
            if (pJ[a][b] >= 9999) continue;
            int Jm = pJ[a][b];
            /* the merge cost also includes materialising non-leaf inputs (already paid) */
            long key = (long)Jm * 4096 + (long)pR[a][b] * 256 + (long)pc(Bof(nd[a].A | nd[b].A)) * 8;
            if (temp) key += (long)(rnd() % (unsigned)temp);
            if (key < bestkey) { bestkey = key; bi = i; bj = j; }
        }
        if (bi < 0) {   /* disconnected: merge any two */
            bi = 0; bj = 1;
        }
        int a = act[bi], b = act[bj];
        int c = mergenode(a, b);
        act[bi] = c; act[bj] = act[--na];
        for (int i = 0; i < na; i++) {
            int o = act[i];
            if (o == c) continue;
            if (!(Wof(nd[o].A) & Wof(nd[c].A))) { pJ[o][c] = pJ[c][o] = 9999; continue; }
            u128 A = nd[o].A | nd[c].A;
            pJ[o][c] = pJ[c][o] = rho(A, nd[o].B | nd[c].B);
            pR[o][c] = pR[c][o] = rho(A, Bof(A));
        }
    }
}

/* ---------- elimination machinery ---------- */
static int uf[128];
static int findr(int x) { while (uf[x] != x) x = uf[x] = uf[uf[x]]; return x; }
/* clusters of state S (eliminated words): equations joined through eliminated words */
static void clusters_of(u128 S, u128 *cl, int *ncl, int *clof) {
    for (int e = 0; e < E; e++) uf[e] = e;
    u128 s = S;
    while (s) {
        int v = ctz(s); s &= s - 1;
        u128 o = occ[v]; int f = ctz(o); o &= o - 1;
        while (o) { int g = ctz(o); o &= o - 1; int a = findr(f), b = findr(g); if (a != b) uf[a] = b; }
    }
    int map[128]; for (int e = 0; e < E; e++) map[e] = -1;
    *ncl = 0;
    for (int e = 0; e < E; e++) { int r = findr(e); if (map[r] < 0) { map[r] = (*ncl)++; cl[map[r]] = 0; } cl[map[r]] |= BIT(e); clof[e] = map[r]; }
}
/* best binarization of merging m clusters; returns max J; fills order into nd[] if build */
static u128 mg_A[16]; static int mg_m;
static int mg_cost[1 << 12], mg_split[1 << 12];
static u128 mg_union(int T) { u128 u = 0; for (int i = 0; i < mg_m; i++) if (T >> i & 1) u |= mg_A[i]; return u; }
static int mg_solve(void) {
    int full = (1 << mg_m) - 1;
    for (int T = 1; T <= full; T++) {
        if (!(T & (T - 1))) { mg_cost[T] = 0; mg_split[T] = 0; continue; }
        int best = 1 << 30, bs = 0;
        for (int T1 = (T - 1) & T; T1; T1 = (T1 - 1) & T) {
            int T2 = T ^ T1;
            if (T1 < T2) continue;
            int c = mg_cost[T1] > mg_cost[T2] ? mg_cost[T1] : mg_cost[T2];
            if (c >= best) continue;
            u128 A1 = mg_union(T1), A2 = mg_union(T2);
            int J = rho(A1 | A2, Bof(A1) | Bof(A2));
            if (J > c) c = J;
            if (c < best) { best = c; bs = T1; }
        }
        mg_cost[T] = best; mg_split[T] = bs;
    }
    return mg_cost[full];
}
static int mg_nodeid[16];
static int mg_build(int T) {
    if (!(T & (T - 1))) return mg_nodeid[ctz((u128)T)];
    int a = mg_build(mg_split[T]), b = mg_build(T ^ mg_split[T]);
    return mergenode(a, b);
}
/* cost of eliminating v from state S */
static int elim_cost(u128 S, int v, u128 *cl, int ncl, int *clof) {
    (void)S; (void)ncl;
    int seen[128] = {0}; mg_m = 0;
    u128 o = occ[v];
    while (o) { int e = ctz(o); o &= o - 1; int c = clof[e]; if (!seen[c]) { seen[c] = 1; mg_A[mg_m++] = cl[c]; } }
    if (mg_m <= 1) return 0;
    if (mg_m > 12) return 999;
    return mg_solve();
}
/* free closure: words whose equations all lie in one cluster can be eliminated at no cost */
static u128 closeS(u128 S) {
    u128 cl[128]; int ncl, clof[128];
    for (;;) {
        clusters_of(S, cl, &ncl, clof);
        u128 add = 0;
        for (int v = 0; v < N; v++) {
            if (S >> v & 1) continue;
            u128 o = occ[v]; int c0 = clof[ctz(o)], one = 1;
            while (o) { int e = ctz(o); o &= o - 1; if (clof[e] != c0) { one = 0; break; } }
            if (one) add |= BIT(v);
        }
        if (!add) return S;
        S |= add;
    }
}

/* greedy elimination with tree construction */
static int elim_ord[128], elim_len;
static void run_elim(int temp) {
    nn = 0; elim_len = 0;
    int cur[128];                         /* cluster id (by min equation) -> node id */
    for (int e = 0; e < E; e++) cur[e] = leafnode(e);
    int nodeof[128]; for (int e = 0; e < E; e++) nodeof[e] = cur[e];
    u128 S = 0;
    u128 ALLV = (N == 128) ? ~(u128)0 : (BIT(N) - 1);
    while (S != ALLV) {
        u128 cl[128]; int ncl, clof[128];
        clusters_of(S, cl, &ncl, clof);
        long bestkey = 1L << 60; int bv = -1;
        for (int v = 0; v < N; v++) {
            if (S >> v & 1) continue;
            int c = elim_cost(S, v, cl, ncl, clof);
            /* secondary: size of merged list */
            u128 U = 0; u128 o = occ[v];
            while (o) { int e = ctz(o); o &= o - 1; U |= cl[clof[e]]; }
            int r = rho(U, Bof(U));
            long key = (long)c * 4096 + (long)r * 64 + pc(Bof(U));
            if (temp) key += (long)(rnd() % (unsigned)temp);
            if (key < bestkey) { bestkey = key; bv = v; }
        }
        /* build the merge for bv */
        int seen[128] = {0}; mg_m = 0;
        u128 o = occ[bv];
        while (o) { int e = ctz(o); o &= o - 1; int c = clof[e]; if (!seen[c]) { seen[c] = 1; mg_A[mg_m] = cl[c]; mg_nodeid[mg_m] = nodeof[ctz(cl[c])]; mg_m++; } }
        if (mg_m > 1) {
            mg_solve();
            int id = mg_build((1 << mg_m) - 1);
            u128 A = nd[id].A, a = A;
            while (a) { int e = ctz(a); a &= a - 1; nodeof[e] = id; }
        }
        S |= BIT(bv);
        elim_ord[elim_len++] = bv;
    }
    /* join leftover components (disconnected parts) */
    u128 cl[128]; int ncl, clof[128];
    clusters_of(S, cl, &ncl, clof);
    int id = nodeof[ctz(cl[0])];
    for (int c = 1; c < ncl; c++) id = mergenode(id, nodeof[ctz(cl[c])]);
}

/* ---------- exact DFS over elimination states ---------- */
#define HS (1 << 22)
static u128 *hset; static unsigned char *hused; static long hcount, nodes_visited, nodelimit;
static int hput(u128 S) {
    uint64_t h = ((uint64_t)S * 0x9E3779B97F4A7C15ULL) ^ ((uint64_t)(S >> 64) * 0xC2B2AE3D27D4EB4FULL);
    h ^= h >> 29;
    if (hcount > HS - HS / 8) { fprintf(stderr, "hash full\n"); exit(4); }
    for (uint64_t i = h & (HS - 1);; i = (i + 1) & (HS - 1)) {
        if (!hused[i]) { hused[i] = 1; hset[i] = S; hcount++; return 1; }
        if (hset[i] == S) return 0;
    }
}
static u128 ALLVm; static int Wmax; static u128 path[200]; static int pathv[200], plen;
static int dfs(u128 S) {
    if (S == ALLVm) return 1;
    if (++nodes_visited > nodelimit) return -1;
    if (!hput(S)) return 0;
    u128 cl[128]; int ncl, clof[128];
    clusters_of(S, cl, &ncl, clof);
    /* candidate words ordered by cost */
    int cand[128], cc[128], nc = 0;
    for (int v = 0; v < N; v++) {
        if (S >> v & 1) continue;
        int c = elim_cost(S, v, cl, ncl, clof);
        if (c <= Wmax) { cand[nc] = v; cc[nc] = c; nc++; }
    }
    /* insertion sort by cost */
    for (int i = 1; i < nc; i++) for (int j = i; j > 0 && cc[j] < cc[j - 1]; j--) { int t = cc[j]; cc[j] = cc[j - 1]; cc[j - 1] = t; t = cand[j]; cand[j] = cand[j - 1]; cand[j - 1] = t; }
    for (int i = 0; i < nc; i++) {
        int r = dfs(closeS(S | BIT(cand[i])));
        if (r) { if (r > 0) { pathv[plen++] = cand[i]; } return r; }
    }
    return 0;
}

/* ---------- local search for balanced cuts ---------- */
static int run_cut(int k, long iters) {
    /* random connected start of size k..2k-1, then moves keeping the size window */
    u128 A = BIT(rnd() % E);
    int tgt = k + (int)(rnd() % (unsigned)k);
    while (pc(A) < tgt) {
        u128 nb = 0, w = Wof(A);
        for (int e = 0; e < E; e++) if (!(A >> e & 1) && (eqv[e] & w)) nb |= BIT(e);
        int cnt = pc(nb), pick = (int)(rnd() % (unsigned)cnt);
        u128 t = nb; while (pick--) t &= t - 1;
        A |= BIT(ctz(t));
    }
    int cur = rho(A, Bof(A)), best = cur;
    for (long it = 0; it < iters; it++) {
        int e = (int)(rnd() % (unsigned)E);
        u128 A2 = A ^ BIT(e);
        int s = pc(A2);
        if (s < k || s >= 2 * k) {
            /* swap move */
            int f = (int)(rnd() % (unsigned)E);
            if (((A >> e) & 1) == ((A >> f) & 1)) continue;
            A2 ^= BIT(f);
        }
        int c = rho(A2, Bof(A2));
        if (c <= cur || (rnd() % 1000) < 5) { A = A2; cur = c; if (c < best) best = c; }
    }
    return best;
}

/* ---------- fixed-order elimination (for annealing) ---------- */
static int eo_uf[128]; static u128 eo_cl[128];
static int eo_find(int x) { while (eo_uf[x] != x) x = eo_uf[x] = eo_uf[eo_uf[x]]; return x; }
/* returns width; *score = sum 8^J; builds the tree into nd[] if build */
static int eval_order(const int *ord, double *score, int build) {
    int nodeof[128];
    for (int e = 0; e < E; e++) { eo_uf[e] = e; eo_cl[e] = BIT(e); }
    if (build) { nn = 0; for (int e = 0; e < E; e++) nodeof[e] = leafnode(e); }
    int w = 0; double sc = 0;
    for (int i = 0; i < N; i++) {
        int v = ord[i];
        int roots[16]; mg_m = 0;
        u128 o = occ[v];
        while (o) {
            int e = ctz(o); o &= o - 1; int r = eo_find(e), k;
            for (k = 0; k < mg_m; k++) if (roots[k] == r) break;
            if (k == mg_m && mg_m < 12) { roots[mg_m] = r; mg_A[mg_m] = eo_cl[r]; if (build) mg_nodeid[mg_m] = nodeof[r]; mg_m++; }
        }
        if (mg_m <= 1) continue;
        int c = mg_solve();
        if (c > w) w = c;
        sc += __builtin_pow(8.0, c);
        int id = -1;
        if (build) id = mg_build((1 << mg_m) - 1);
        int r0 = roots[0];
        for (int k = 1; k < mg_m; k++) { eo_uf[roots[k]] = r0; eo_cl[r0] |= eo_cl[roots[k]]; }
        if (build) nodeof[r0] = id;
    }
    /* components left over */
    int r0 = eo_find(0);
    for (int e = 1; e < E; e++) {
        int r = eo_find(e);
        if (r != r0) {
            u128 A1 = eo_cl[r0], A2 = eo_cl[r];
            int J = rho(A1 | A2, Bof(A1) | Bof(A2));
            if (J > w) w = J;
            sc += __builtin_pow(8.0, J);
            if (build) nodeof[r0] = mergenode(nodeof[r0], nodeof[r]);
            eo_uf[r] = r0; eo_cl[r0] |= A2;
        }
    }
    *score = sc;
    return w;
}

static void run_sa(long iters, int *bestord, int *bw, double *bscore) {
    int ord[128];
    /* start from a randomized greedy elimination order */
    run_elim((int)(rnd() % 3000));
    for (int i = 0; i < N; i++) ord[i] = elim_ord[i];
    double sc; int w = eval_order(ord, &sc, 0);
    double cur = __builtin_log(sc);
    *bw = w; *bscore = sc; memcpy(bestord, ord, sizeof(int) * N);
    for (long it = 0; it < iters; it++) {
        double T = 1.0 * (1.0 - (double)it / iters) + 0.02;
        int i = (int)(rnd() % (unsigned)N), j = (int)(rnd() % (unsigned)N);
        if (i == j) continue;
        int tmp[128]; memcpy(tmp, ord, sizeof(int) * N);
        if (rnd() & 1) { int t = tmp[i]; tmp[i] = tmp[j]; tmp[j] = t; }
        else { int t = tmp[i]; if (i < j) { memmove(tmp + i, tmp + i + 1, sizeof(int) * (j - i)); } else { memmove(tmp + j + 1, tmp + j, sizeof(int) * (i - j)); } tmp[j] = t; }
        double s2; int w2 = eval_order(tmp, &s2, 0);
        double c2 = __builtin_log(s2);
        if (c2 <= cur || (double)(rnd() % 1000000) / 1e6 < __builtin_exp((cur - c2) / T)) {
            memcpy(ord, tmp, sizeof(int) * N); cur = c2;
            if (w2 < *bw || (w2 == *bw && s2 < *bscore)) { *bw = w2; *bscore = s2; memcpy(bestord, ord, sizeof(int) * N); }
        }
    }
}

/* ---------- caterpillar (one growing list, equations added one at a time; checks absorbed at once) ---------- */
static int cat_J[256], cat_e[256], cat_n;
static int eval_cat(const int *ord, double *score) {
    u128 A = 0; int w = 0; double sc = 0; cat_n = 0;
    for (int i = 0; i < E; i++) {
        int e = ord[i];
        if (A >> e & 1) continue;
        int J = 0;
        if (A) { J = rho(A | BIT(e), Bof(A) | Bof(BIT(e))); }
        A |= BIT(e); cat_J[cat_n] = J; cat_e[cat_n++] = e;
        if (J > w) w = J;
        sc += __builtin_pow(8.0, J);
        /* absorb checks: equations whose words are all present */
        for (int changed = 1; changed;) {
            changed = 0; u128 W = Wof(A);
            for (int f = 0; f < E; f++) if (!(A >> f & 1) && !(eqv[f] & ~W)) {
                int J2 = rho(A | BIT(f), Bof(A) | Bof(BIT(f)));
                A |= BIT(f); cat_J[cat_n] = J2; cat_e[cat_n++] = f; changed = 1;
                if (J2 > w) w = J2;
                sc += __builtin_pow(8.0, J2);
            }
        }
    }
    *score = sc;
    return w;
}
static int name2eq(const char *s) { for (int e = 0; e < E; e++) if (!strcmp(ename[e], s)) return e; return -1; }

/* exact brick-level width (same as mode calldp, no printing); groups = G calls, out* merged; returns width,
   *score = sum over optimal-tree joins of 8^J (tie-break) */
static int bw_best[1 << 16], bw_spl[1 << 16], brick_maxg = 16;
static u128 bw_SA[1 << 16], bw_SB[1 << 16];
static int brick_width(double *score) {
    char gname[32][16]; int ng = 0; u128 gA[32];
    for (int e = 0; e < E; e++) {
        char c[16]; int i = 0; while (ename[e][i] && ename[e][i] != ':' && i < 15) { c[i] = ename[e][i]; i++; } c[i] = 0;
        if (!strncmp(c, "out", 3)) strcpy(c, "out");
        int g; for (g = 0; g < ng; g++) if (!strcmp(gname[g], c)) break;
        if (g == ng) { if (ng == 16) return 999; strcpy(gname[ng], c); gA[ng] = 0; ng++; }
        gA[g] |= BIT(e);
    }
    if (ng > brick_maxg) return 999;
    int inner[32];
    static int ib[1 << 8];
    for (int g = 0; g < ng; g++) {
        int idx[16], m = 0; u128 a = gA[g]; while (a) { idx[m++] = ctz(a); a &= a - 1; }
        if (m > 8) return 999;
        for (int T = 1; T < (1 << m); T++) {
            if (!(T & (T - 1))) { ib[T] = 0; continue; }
            u128 AT = 0; for (int i = 0; i < m; i++) if (T >> i & 1) AT |= BIT(idx[i]);
            int best = 1 << 30;
            for (int T1 = (T - 1) & T; T1; T1 = (T1 - 1) & T) {
                int T2 = T ^ T1; if (T1 < T2) continue;
                int c = ib[T1] > ib[T2] ? ib[T1] : ib[T2]; if (c >= best) continue;
                u128 A1 = 0, A2 = 0; for (int i = 0; i < m; i++) { if (T1 >> i & 1) A1 |= BIT(idx[i]); if (T2 >> i & 1) A2 |= BIT(idx[i]); }
                int J = rho(AT, Bof(A1) | Bof(A2)); if (J > c) c = J;
                if (c < best) best = c;
            }
            ib[T] = best;
        }
        inner[g] = ib[(1 << m) - 1];
    }
    int full = (1 << ng) - 1;
    for (int S = 1; S <= full; S++) { bw_SA[S] = 0; for (int g = 0; g < ng; g++) if (S >> g & 1) bw_SA[S] |= gA[g]; bw_SB[S] = Bof(bw_SA[S]); }
    for (int S = 1; S <= full; S++) {
        if (!(S & (S - 1))) { bw_best[S] = inner[ctz((u128)S)]; bw_spl[S] = 0; continue; }
        int b = 1 << 30, bs = 0;
        for (int S1 = (S - 1) & S; S1; S1 = (S1 - 1) & S) {
            int S2 = S ^ S1; if (S1 < S2) continue;
            int c = bw_best[S1] > bw_best[S2] ? bw_best[S1] : bw_best[S2]; if (c >= b) continue;
            int J = rho(bw_SA[S], bw_SB[S1] | bw_SB[S2]); if (J > c) c = J;
            if (c < b) { b = c; bs = S1; }
        }
        bw_best[S] = b; bw_spl[S] = bs;
    }
    /* score: count joins of the optimal tree at each width */
    double sc = 0; int st[64], sp = 0; st[sp++] = full;
    while (sp) { int S = st[--sp]; if (!(S & (S - 1))) { sc += __builtin_pow(8.0, inner[ctz((u128)S)]); continue; }
        int S1 = bw_spl[S]; sc += __builtin_pow(8.0, rho(bw_SA[S], bw_SB[S1] | bw_SB[S ^ S1])); st[sp++] = S1; st[sp++] = S ^ S1; }
    *score = sc;
    return bw_best[full];
}

/* ---------- top-down recursive bisection ---------- */
static long td_iters;
static double split_key(u128 A1, u128 A2, int *Jo) {
    u128 B1 = Bof(A1), B2 = Bof(A2);
    int J = rho(A1 | A2, B1 | B2);
    int r1 = pc(A1) > 1 ? rho(A1, B1) : 0, r2 = pc(A2) > 1 ? rho(A2, B2) : 0;
    int m = J; if (r1 > m) m = r1; if (r2 > m) m = r2;
    *Jo = J;
    return m * 1000.0 + __builtin_pow(4.0, J) * 0.001 + __builtin_pow(4.0, r1) * 0.001 + __builtin_pow(4.0, r2) * 0.001;
}
static int td_build(u128 A) {
    if (pc(A) == 1) return leafnode(ctz(A));
    int n = pc(A), idx[128], k = 0;
    { u128 a = A; while (a) { idx[k++] = ctz(a); a &= a - 1; } }
    /* start: random half, grown connected */
    u128 A1 = BIT(idx[rnd() % (unsigned)n]);
    int tgt = 1 + (int)(rnd() % (unsigned)(n - 1));
    while (pc(A1) < tgt) {
        u128 W1 = Wof(A1), cand = 0;
        for (int i = 0; i < n; i++) if (!(A1 >> idx[i] & 1) && (eqv[idx[i]] & W1)) cand |= BIT(idx[i]);
        if (!cand) for (int i = 0; i < n; i++) if (!(A1 >> idx[i] & 1)) cand |= BIT(idx[i]);
        int c = pc(cand), pick = (int)(rnd() % (unsigned)c); u128 t = cand; while (pick--) t &= t - 1;
        A1 |= BIT(ctz(t));
    }
    int J; double cur = split_key(A1, A & ~A1, &J), best = cur; u128 bA1 = A1;
    long iters = td_iters * (n > 8 ? 1 : 0) + (n <= 8 ? 200 : 0);
    for (long it = 0; it < iters; it++) {
        double T = 600.0 * (1.0 - (double)it / iters) + 1;
        int e = idx[rnd() % (unsigned)n];
        u128 C1 = A1 ^ BIT(e);
        if (!C1 || C1 == A) continue;
        double c = split_key(C1, A & ~C1, &J);
        if (c <= cur || (double)(rnd() % 1000000) / 1e6 < __builtin_exp((cur - c) / T)) {
            A1 = C1; cur = c;
            if (c < best) { best = c; bA1 = A1; }
        }
    }
    int l = td_build(bA1), r = td_build(A & ~bA1);
    return mergenode(l, r);
}

#ifndef NOMAIN
static void run_td(long iters) { td_iters = iters; nn = 0; td_build(ALLE); }
#endif

#ifndef NOMAIN
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage\n"); return 1; }
    readsys(argv[2]);
    u128 W = Wof(ALLE);
    fprintf(stdout, "system %s: N=%d E=%d F=%d  rho(all,{})=%d  covered words=%d\n", argv[2], N, E, F, rho(ALLE, 0), pc(W));
    if (!strcmp(argv[1], "agg") || !strcmp(argv[1], "elim") || !strcmp(argv[1], "td")) {
        int runs = atoi(argv[3]); rs ^= (uint64_t)atoll(argv[4]) * 0x9E3779B97F4A7C15ULL;
        long tdi = argc > 5 ? atol(argv[5]) : 3000;
        int hist[64] = {0};
        for (int r = 0; r < runs; r++) {
            int temp = r == 0 ? 0 : (int)(rnd() % 6000);
            if (argv[1][0] == 'a') run_agg(temp); else if (argv[1][0] == 'e') run_elim(temp); else run_td(tdi);
            int s, w = treewidth_of(nd, nn, &s);
            if (w >= 0 && w < 64) hist[w]++;
            consider_best();
        }
        printf("width histogram:");
        for (int w = 0; w < 64; w++) if (hist[w]) printf(" %d:%d", w, hist[w]);
        printf("\nbest width %d (joins at that width: %d)\n", best_w, best_sumexp);
        int jh[64] = {0};
        for (int i = 0; i < best_nn; i++) if (best_nd[i].l >= 0 && best_nd[i].J >= 0 && best_nd[i].J < 64) jh[best_nd[i].J]++;
        printf("best tree join-width histogram:");
        for (int w = 0; w < 64; w++) if (jh[w]) printf(" J%d:%d", w, jh[w]);
        printf("\n");
        printtree(best_nd, best_nn - 1, 0, stdout);
    } else if (!strcmp(argv[1], "exact")) {
        Wmax = atoi(argv[3]); nodelimit = atol(argv[4]);
        hset = calloc(HS, sizeof(u128)); hused = calloc(HS, 1);
        ALLVm = (N == 128) ? ~(u128)0 : (BIT(N) - 1);
        plen = 0;
        int r = dfs(closeS(0));
        printf("exact elimination search width<=%d: %s  (states %ld, visited %ld)\n", Wmax,
               r > 0 ? "FOUND" : r < 0 ? "NODE LIMIT (undecided)" : "NONE (proved within elimination trees)", hcount, nodes_visited);
        if (r > 0) { printf("order (reverse):"); for (int i = 0; i < plen; i++) printf(" %s", vname[pathv[i]]); printf("\n"); }
    } else if (!strcmp(argv[1], "sa")) {
        long iters = atol(argv[3]); int restarts = atoi(argv[4]); rs ^= (uint64_t)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL;
        int bo[128], gbo[128], gbw = 1 << 30; double gbs = 1e300;
        for (int r = 0; r < restarts; r++) {
            int bw; double bs;
            run_sa(iters, bo, &bw, &bs);
            printf("restart %d: width %d score %.0f\n", r, bw, bs); fflush(stdout);
            if (bw < gbw || (bw == gbw && bs < gbs)) { gbw = bw; gbs = bs; memcpy(gbo, bo, sizeof(int) * N); }
        }
        double sc; eval_order(gbo, &sc, 1);
        int s; int w = treewidth_of(nd, nn, &s);
        printf("best SA width %d (joins at that width %d)\norder:", w, s);
        for (int i = 0; i < N; i++) printf(" %s", vname[gbo[i]]);
        printf("\n");
        int jh[64] = {0};
        for (int i = 0; i < nn; i++) if (nd[i].l >= 0 && nd[i].J >= 0 && nd[i].J < 64) jh[nd[i].J]++;
        printf("join-width histogram:");
        for (int x = 0; x < 64; x++) if (jh[x]) printf(" J%d:%d", x, jh[x]);
        printf("\n");
        printtree(nd, nn - 1, 0, stdout);
    } else if (!strcmp(argv[1], "catgd") || !strcmp(argv[1], "catsa")) {
        /* catgd <sys> <gd_best file>        : caterpillar width of a guess-and-determine order
           catsa <sys> <iters> <restarts> <seed> : annealing over caterpillar equation orders */
        int ord[128], n = 0, used[128] = {0};
        if (argv[1][3] == 'g') {
            FILE *f = fopen(argv[3], "r"); char a[64], b[64], c[64], line[256];
            while (fgets(line, sizeof line, f)) {
                if (sscanf(line, "%63s %63s %63s", a, b, c) == 3 && !strcmp(a, "solve")) {
                    int e = name2eq(b); if (e >= 0 && !used[e]) { used[e] = 1; ord[n++] = e; }
                }
            }
            fclose(f);
            for (int e = 0; e < E; e++) if (!used[e]) ord[n++] = e;
            double sc; int w = eval_cat(ord, &sc);
            printf("caterpillar of GD order: width %d\nsteps:", w);
            for (int i = 0; i < cat_n; i++) printf(" %s:%d", ename[cat_e[i]], cat_J[i]);
            printf("\n");
        } else {
            long iters = atol(argv[3]); int restarts = atoi(argv[4]); rs ^= (uint64_t)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL;
            int gbest[128], gw = 1 << 30; double gs = 1e300;
            for (int r = 0; r < restarts; r++) {
                for (int i = 0; i < E; i++) ord[i] = i;
                for (int i = E - 1; i > 0; i--) { int j = (int)(rnd() % (unsigned)(i + 1)); int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
                double sc; int w = eval_cat(ord, &sc); double cur = __builtin_log(sc);
                int bw = w; double bs = sc; int bo[128]; memcpy(bo, ord, sizeof ord);
                for (long it = 0; it < iters; it++) {
                    double T = 1.0 * (1.0 - (double)it / iters) + 0.02;
                    int i = (int)(rnd() % (unsigned)E), j = (int)(rnd() % (unsigned)E);
                    if (i == j) continue;
                    int tmp[128]; memcpy(tmp, ord, sizeof ord);
                    if (rnd() & 1) { int t = tmp[i]; tmp[i] = tmp[j]; tmp[j] = t; }
                    else { int t = tmp[i]; if (i < j) memmove(tmp + i, tmp + i + 1, sizeof(int) * (j - i)); else memmove(tmp + j + 1, tmp + j, sizeof(int) * (i - j)); tmp[j] = t; }
                    double s2; int w2 = eval_cat(tmp, &s2); double c2 = __builtin_log(s2);
                    if (c2 <= cur || (double)(rnd() % 1000000) / 1e6 < __builtin_exp((cur - c2) / T)) {
                        memcpy(ord, tmp, sizeof ord); cur = c2;
                        if (w2 < bw || (w2 == bw && s2 < bs)) { bw = w2; bs = s2; memcpy(bo, ord, sizeof ord); }
                    }
                }
                printf("restart %d: caterpillar width %d score %.0f\n", r, bw, bs); fflush(stdout);
                if (bw < gw || (bw == gw && bs < gs)) { gw = bw; gs = bs; memcpy(gbest, bo, sizeof bo); }
            }
            double sc; int w = eval_cat(gbest, &sc);
            printf("best caterpillar width %d\nsteps:", w);
            for (int i = 0; i < cat_n; i++) printf(" %s:%d", ename[cat_e[i]], cat_J[i]);
            printf("\n");
        }
    } else if (!strcmp(argv[1], "calldp")) {
        /* calldp <sys> [mergeout]: EXACT minimum width over all trees whose nodes are unions of whole groups
           (group = one G call; 'out*' equations form one group if mergeout); inside a group the best binary tree
           over its equations is found exactly by subset DP. */
        int mergeout = argc > 3;
        char gname[32][16]; int ng = 0, gof[128]; u128 gA[32];
        for (int e = 0; e < E; e++) {
            char c[16]; int i = 0; while (ename[e][i] && ename[e][i] != ':' && i < 15) { c[i] = ename[e][i]; i++; } c[i] = 0;
            if (mergeout && !strncmp(c, "out", 3)) strcpy(c, "out");
            int g; for (g = 0; g < ng; g++) if (!strcmp(gname[g], c)) break;
            if (g == ng) { strcpy(gname[ng], c); gA[ng] = 0; ng++; }
            gof[e] = g; gA[g] |= BIT(e);
        }
        /* internal best per group */
        int inner[32];
        for (int g = 0; g < ng; g++) {
            int idx[16], m = 0; u128 a = gA[g]; while (a) { idx[m++] = ctz(a); a &= a - 1; }
            static int ib[1 << 16];
            for (int T = 1; T < (1 << m); T++) {
                if (!(T & (T - 1))) { ib[T] = 0; continue; }
                u128 AT = 0; for (int i = 0; i < m; i++) if (T >> i & 1) AT |= BIT(idx[i]);
                int best = 1 << 30;
                for (int T1 = (T - 1) & T; T1; T1 = (T1 - 1) & T) {
                    int T2 = T ^ T1; if (T1 < T2) continue;
                    int c = ib[T1] > ib[T2] ? ib[T1] : ib[T2]; if (c >= best) continue;
                    u128 A1 = 0, A2 = 0; for (int i = 0; i < m; i++) { if (T1 >> i & 1) A1 |= BIT(idx[i]); if (T2 >> i & 1) A2 |= BIT(idx[i]); }
                    int J = rho(AT, Bof(A1) | Bof(A2)); if (J > c) c = J;
                    if (c < best) best = c;
                }
                ib[T] = best;
            }
            inner[g] = ib[(1 << m) - 1];
            printf("group %-5s |eqs|=%d  inner width %d  list %d\n", gname[g], m, inner[g], m > 1 ? rho(gA[g], Bof(gA[g])) : 0);
        }
        int full = (1 << ng) - 1;
        int *best = malloc(sizeof(int) * (full + 1)), *spl = malloc(sizeof(int) * (full + 1));
        u128 *SA = malloc(sizeof(u128) * (full + 1)), *SB = malloc(sizeof(u128) * (full + 1));
        for (int S = 1; S <= full; S++) { int g = ctz((u128)S); SA[S] = SA[S & (S - 1)] | gA[g]; }
        SA[0] = 0;
        for (int S = 1; S <= full; S++) { SA[S] = 0; for (int g = 0; g < ng; g++) if (S >> g & 1) SA[S] |= gA[g]; SB[S] = Bof(SA[S]); }
        for (int S = 1; S <= full; S++) {
            if (!(S & (S - 1))) { best[S] = inner[ctz((u128)S)]; spl[S] = 0; continue; }
            int b = 1 << 30, bs = 0;
            for (int S1 = (S - 1) & S; S1; S1 = (S1 - 1) & S) {
                int S2 = S ^ S1; if (S1 < S2) continue;
                int c = best[S1] > best[S2] ? best[S1] : best[S2]; if (c >= b) continue;
                int J = rho(SA[S], SB[S1] | SB[S2]); if (J > c) c = J;
                if (c < b) { b = c; bs = S1; }
            }
            best[S] = b; spl[S] = bs;
        }
        printf("EXACT brick-level optimum (%d groups): width %d\n", ng, best[full]);
        /* print the optimal brick tree */
        int stack[64], depth[64], sp = 0; stack[sp] = full; depth[sp++] = 0;
        while (sp) {
            int S = stack[--sp], d = depth[sp];
            printf("%*s", 2 * d, "");
            if (!(S & (S - 1))) { printf("[%s] inner %d\n", gname[ctz((u128)S)], best[S]); continue; }
            int S1 = spl[S], S2 = S ^ S1;
            printf("JOIN J=%d list=%d :", rho(SA[S], SB[S1] | SB[S2]), rho(SA[S], SB[S]));
            for (int g = 0; g < ng; g++) if (S >> g & 1) printf(" %s", gname[g]);
            printf("\n");
            stack[sp] = S2; depth[sp++] = d + 1; stack[sp] = S1; depth[sp++] = d + 1;
        }
    } else if (!strcmp(argv[1], "order")) {
        /* order <sys> <file of word names, one per line or space separated> : width of that elimination order */
        FILE *f = fopen(argv[3], "r"); char tok[64]; int ord[128], n = 0, used[128] = {0};
        while (fscanf(f, "%63s", tok) == 1) {
            int v; for (v = 0; v < N; v++) if (!strcmp(vname[v], tok)) break;
            if (v < N && !used[v]) { used[v] = 1; ord[n++] = v; }
        }
        fclose(f);
        for (int v = 0; v < N; v++) if (!used[v]) ord[n++] = v;     /* words not listed go last */
        double sc; eval_order(ord, &sc, 1);
        int s, w = treewidth_of(nd, nn, &s);
        int jh[64] = {0};
        for (int i = 0; i < nn; i++) if (nd[i].l >= 0 && nd[i].J < 64) jh[nd[i].J]++;
        printf("order %s: width %d (joins at width %d); histogram:", argv[3], w, s);
        for (int x = 0; x < 64; x++) if (jh[x]) printf(" J%d:%d", x, jh[x]);
        printf("\n");
        if (argc > 4) printtree(nd, nn - 1, 0, stdout);
    } else if (!strcmp(argv[1], "shrink")) {
        /* shrink <sys> <tries> <seed>: random connected clusters with rho(A,B(A)) < dim Sol(A) and dim <= 4 */
        long tries = atol(argv[3]); rs ^= (uint64_t)atoll(argv[4]) * 0x9E3779B97F4A7C15ULL;
        int shown = 0;
        for (long t = 0; t < tries && shown < 12; t++) {
            u128 A = BIT(rnd() % E); int tgt = 2 + (int)(rnd() % 14);
            while (pc(A) < tgt) {
                u128 W1 = Wof(A), cand = 0;
                for (int e = 0; e < E; e++) if (!(A >> e & 1) && (eqv[e] & W1)) cand |= BIT(e);
                int c = pc(cand), pick = (int)(rnd() % (unsigned)c); u128 x = cand; while (pick--) x &= x - 1;
                A |= BIT(ctz(x));
            }
            int dim = pc(Wof(A)) - pc(A) - rho(A, 0);   /* |W| - matched = generic dim Sol(A) */
            int r = rho(A, Bof(A));
            if (r < dim && dim <= 4) {
                printf("dim %d rho %d :", dim, r);
                u128 a = A; while (a) { int e = ctz(a); a &= a - 1; printf(" %s", ename[e]); }
                printf("\n"); shown++;
            }
        }
    } else if (!strcmp(argv[1], "check")) {
        /* check <sys> <kissat.out> : decode x_e (first E variables), print |A|, rho(A,B(A)) */
        FILE *f = fopen(argv[3], "r"); char tok[64]; u128 A = 0;
        while (fscanf(f, "%63s", tok) == 1) { long v = atol(tok); if (v > 0 && v <= E) A |= BIT(v - 1); }
        fclose(f);
        char buf[1024]; callsummary(A, buf);
        printf("witness: |A|=%d |B(A)|=%d rho(A,B(A))=%d  [%s]\n", pc(A), pc(Bof(A)), rho(A, Bof(A)), buf);
        printf("boundary:"); u128 b = Bof(A); while (b) { int v = ctz(b); b &= b - 1; printf(" %s", vname[v]); } printf("\n");
    } else if (!strcmp(argv[1], "cut")) {
        int k = atoi(argv[3]); long iters = atol(argv[4]); rs ^= (uint64_t)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL;
        int best = 999;
        for (int r = 0; r < 20; r++) { int b = run_cut(k, iters); if (b < best) best = b; }
        printf("cut k=%d: smallest rho(A,B(A)) found with %d<=|A|<%d : %d\n", k, k, 2 * k, best);
    }
    return 0;
}
#endif
