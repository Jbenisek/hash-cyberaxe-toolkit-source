/* Exhaustive minimum guess basis, independent of the SAT encoding.
   Input: rules_<variant>_<length>_<set>.txt from rulesets.py (non-constant words only).
   Closure: an equation with exactly one unknown word gives it; a rule (target; triggers) gives the target once
   all triggers are known.  DFS over guess sets g1<g2<..<gk, skipping a guess already in the closure (such a set is
   never minimal).  Work split: first guess index % nproc == part.
   usage: bf <rulesfile> <kmax> <part> <nproc>        -> prints every covering set of size <= kmax found
          bf <rulesfile> check                        -> reads guess sets (names, one set per line) from stdin,
                                                         prints closure size and parallel layer count  */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXV 128
#define MAXE 256
#define MAXR 200000
typedef struct { uint64_t w[2]; } bs;
static int nv, ne, nr;
static char names[MAXV][32];
static bs emask[MAXE];
static bs rtrig[MAXR];
static int rtgt[MAXR];
static int *vev[MAXV], nvev[MAXV];   /* equations containing var */
static int *vru[MAXV], nvru[MAXV];   /* rules with var in trigger */
static bs full;
static long long found[16];
static int kmax;

static inline int has(const bs *k, int v) { return (k->w[v >> 6] >> (v & 63)) & 1; }
static inline void set(bs *k, int v) { k->w[v >> 6] |= 1ULL << (v & 63); }
static inline int isfull(const bs *k) { return k->w[0] == full.w[0] && k->w[1] == full.w[1]; }

static void closure(bs *K, int g) {
    int q[MAXV], qh = 0, qt = 0;
    if (has(K, g)) return;
    set(K, g); q[qt++] = g;
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nvev[v]; i++) {
            bs *m = &emask[vev[v][i]];
            uint64_t u0 = m->w[0] & ~K->w[0], u1 = m->w[1] & ~K->w[1];
            int c = __builtin_popcountll(u0) + __builtin_popcountll(u1);
            if (c == 1) {
                int t = u0 ? __builtin_ctzll(u0) : 64 + __builtin_ctzll(u1);
                set(K, t); q[qt++] = t;
            }
        }
        for (int i = 0; i < nvru[v]; i++) {
            int r = vru[v][i];
            if (has(K, rtgt[r])) continue;
            if ((rtrig[r].w[0] & ~K->w[0]) || (rtrig[r].w[1] & ~K->w[1])) continue;
            set(K, rtgt[r]); q[qt++] = rtgt[r];
        }
    }
}

/* words derivable from constants alone: equations with a single non-constant word (none exist in the BLAKE3
   systems, every equation there has >= 2 non-constant words; fixed after bf_unit.py exposed it on random systems) */
static void init_closure(bs *K) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int e = 0; e < ne; e++) {
            uint64_t u0 = emask[e].w[0] & ~K->w[0], u1 = emask[e].w[1] & ~K->w[1];
            if (__builtin_popcountll(u0) + __builtin_popcountll(u1) == 1) {
                closure(K, u0 ? __builtin_ctzll(u0) : 64 + __builtin_ctzll(u1)); ch = 1;
            }
        }
    }
}

static int layers(bs K) {   /* parallel propagation rounds from K until fixpoint; returns rounds, K updated */
    int t = 0;
    for (;;) {
        bs N = K;
        for (int e = 0; e < ne; e++) {
            uint64_t u0 = emask[e].w[0] & ~K.w[0], u1 = emask[e].w[1] & ~K.w[1];
            if (__builtin_popcountll(u0) + __builtin_popcountll(u1) == 1) { N.w[0] |= u0; N.w[1] |= u1; }
        }
        for (int r = 0; r < nr; r++)
            if (!((rtrig[r].w[0] & ~K.w[0]) || (rtrig[r].w[1] & ~K.w[1]))) set(&N, rtgt[r]);
        if (N.w[0] == K.w[0] && N.w[1] == K.w[1]) return t;
        K = N; t++;
        if (isfull(&K)) return t;
    }
}

/* optional "look" relaxation (upper bound on any one-word-at-a-time solver): an unknown z is accepted as known when
   guessing it and propagating plainly covers at least as many new equations as it adds words (so one equation is a
   check on z): z is then determined up to a few values, at a per-instance cost the model does not price. */
static int look;
static int ncov(const bs *K) {
    int c = 0;
    for (int e = 0; e < ne; e++) if (!((emask[e].w[0] & ~K->w[0]) || (emask[e].w[1] & ~K->w[1]))) c++;
    return c;
}
static void lookahead(bs *K) {
    int changed = 1;
    while (changed) {
        changed = 0;
        int c0 = ncov(K), n0 = __builtin_popcountll(K->w[0]) + __builtin_popcountll(K->w[1]);
        for (int z = 0; z < nv; z++) {
            if (has(K, z)) continue;
            bs K3 = *K; closure(&K3, z);
            int n = __builtin_popcountll(K3.w[0]) + __builtin_popcountll(K3.w[1]) - n0;
            if (ncov(&K3) - c0 >= n) { closure(K, z); changed = 1; break; }
        }
    }
}

static int gs[16];
static void dfs(int d, int start, bs K) {
    if (isfull(&K)) {
        found[d]++;
        bs G = {{0, 0}};
        for (int i = 0; i < d; i++) set(&G, gs[i]);
        int L = layers(G);
        printf("FOUND k=%d layers=%d :", d, L);
        for (int i = 0; i < d; i++) printf(" %s", names[gs[i]]);
        printf("\n");
        fflush(stdout);
        return;
    }
    if (d == kmax) return;
    for (int g = start; g < nv; g++) {
        if (has(&K, g)) continue;
        bs K2 = K;
        closure(&K2, g);
        if (look) lookahead(&K2);
        gs[d] = g;
        dfs(d + 1, g + 1, K2);
    }
}

static int lookup(const char *s) {
    for (int i = 0; i < nv; i++) if (!strcmp(names[i], s)) return i;
    return -1;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    if (!f) { perror("rules"); return 1; }
    if (fscanf(f, "%d %d %d", &nv, &ne, &nr) != 3) return 1;
    for (int i = 0; i < nv; i++) if (fscanf(f, "%31s", names[i]) != 1) return 1;
    char line[4096];
    fgets(line, sizeof line, f);
    for (int e = 0; e < ne; e++) {
        fgets(line, sizeof line, f);
        char *p = line; int v, n;
        while (sscanf(p, "%d%n", &v, &n) == 1) { set(&emask[e], v); p += n; }
    }
    for (int r = 0; r < nr; r++) {
        fgets(line, sizeof line, f);
        char *p = line; int v, n, first = 1;
        while (sscanf(p, "%d%n", &v, &n) == 1) { if (first) { rtgt[r] = v; first = 0; } else set(&rtrig[r], v); p += n; }
    }
    fclose(f);
    for (int v = 0; v < nv; v++) {
        set(&full, v);
        vev[v] = malloc(sizeof(int) * (ne + 1)); vru[v] = malloc(sizeof(int) * (nr + 1));
        for (int e = 0; e < ne; e++) if (has(&emask[e], v)) vev[v][nvev[v]++] = e;
        for (int r = 0; r < nr; r++) if (has(&rtrig[r], v)) vru[v][nvru[v]++] = r;
    }
    if (!strcmp(argv[2], "check")) {
        while (fgets(line, sizeof line, stdin)) {
            bs K = {{0, 0}}, G = {{0, 0}};
            init_closure(&K);
            char *tok = strtok(line, " \t\r\n"); int k = 0;
            while (tok) { int v = lookup(tok); if (v < 0) { printf("unknown %s\n", tok); return 1; }
                          closure(&K, v); set(&G, v); k++; tok = strtok(NULL, " \t\r\n"); }
            int L = layers(G);
            printf("guesses=%d closure=%d/%d layers=%d\n", k,
                   __builtin_popcountll(K.w[0]) + __builtin_popcountll(K.w[1]), nv, L);
        }
        return 0;
    }
    kmax = atoi(argv[2]);
    int part = atoi(argv[3]), np = atoi(argv[4]);
    look = argc > 5 && !strcmp(argv[5], "look");
    bs K0 = {{0, 0}};
    init_closure(&K0);
    if (look) lookahead(&K0);
    if (part == 0 && isfull(&K0)) { found[0]++; printf("FOUND k=0 layers=0 :\n"); }
    for (int g = 0; g < nv; g++) {
        if (g % np != part) continue;
        if (has(&K0, g)) continue;
        bs K = K0; closure(&K, g); if (look) lookahead(&K); gs[0] = g;
        dfs(1, g + 1, K);
    }
    printf("DONE part %d/%d kmax=%d nv=%d ne=%d nr=%d counts:", part, np, kmax, nv, ne, nr);
    for (int k = 0; k <= kmax; k++) printf(" k%d=%lld", k, found[k]);
    printf("\n");
    return 0;
}
