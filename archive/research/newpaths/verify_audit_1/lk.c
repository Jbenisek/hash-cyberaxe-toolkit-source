/* verify_audit_1: independent exhaustive search for guess sets that determine every word ("covers"),
   plain or with the optimistic one-word "look" acceptance, optionally with extra rules (target <- triggers).
   Written independently of audit/bf.c; uses a DIFFERENT exploration order (descending indices by default)
   and a different look scan (accept-and-continue instead of accept-and-restart), so an order-dependence
   miss in bf.c would show here.
   usage: lk <sysfile> <kmax> <part> <nproc> <plain|look> <asc|desc> [rulesfile|-]
          lk <sysfile> ordertest <ntrials> <setsize> [rulesfile|-]    (closure order-independence test)
   Output: DONE line with cover counts per k and the largest closure size seen at each depth. */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXV 128
#define MAXE 160
#define MAXR 4096
typedef struct { uint64_t w[2]; } bs;
static int nv, ne, nr;
static char names[MAXV][32];
static bs em[MAXE], rt[MAXR];
static int rg[MAXR];
static bs full;
static int look, desc, kmax;
static long long covers[16], nodes[16];
static int best[16];

static inline int has(const bs *k, int v) { return (k->w[v >> 6] >> (v & 63)) & 1; }
static inline void setb(bs *k, int v) { k->w[v >> 6] |= 1ULL << (v & 63); }
static inline int pc(const bs *k) { return __builtin_popcountll(k->w[0]) + __builtin_popcountll(k->w[1]); }
static inline int sub(const bs *a, const bs *k) { return !((a->w[0] & ~k->w[0]) | (a->w[1] & ~k->w[1])); }

/* plain closure by repeated sweeps (different style from bf.c's queue) */
static void plclose(bs *K) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int e = 0; e < ne; e++) {
            uint64_t u0 = em[e].w[0] & ~K->w[0], u1 = em[e].w[1] & ~K->w[1];
            if (__builtin_popcountll(u0) + __builtin_popcountll(u1) == 1) { K->w[0] |= u0; K->w[1] |= u1; ch = 1; }
        }
        for (int r = 0; r < nr; r++)
            if (!has(K, rg[r]) && sub(&rt[r], K)) { setb(K, rg[r]); ch = 1; }
    }
}
static int ncov(const bs *K) { int c = 0; for (int e = 0; e < ne; e++) c += sub(&em[e], K); return c; }

static int perm[MAXV];   /* scan order for look */
static void lookfix(bs *K) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int i = 0; i < nv; i++) {
            int z = perm[i];
            if (has(K, z)) continue;
            int c0 = ncov(K), n0 = pc(K);
            bs T = *K; setb(&T, z); plclose(&T);
            if (ncov(&T) - c0 >= pc(&T) - n0) { *K = T; ch = 1; }
        }
    }
}
static void fullclose(bs *K) { plclose(K); if (look) lookfix(K); }

static int gs[16];
static void dfs(int d, int lim, bs K) {
    nodes[d]++;
    int p = pc(&K); if (p > best[d]) best[d] = p;
    if (p == nv) {
        covers[d]++;
        printf("FOUND k=%d :", d); for (int i = 0; i < d; i++) printf(" %s", names[gs[i]]); printf("\n"); fflush(stdout);
        return;
    }
    if (d == kmax) return;
    /* desc: next guess index < lim ; asc: next guess index > lim */
    if (desc) {
        for (int g = lim - 1; g >= 0; g--) { if (has(&K, g)) continue; bs K2 = K; setb(&K2, g); fullclose(&K2); gs[d] = g; dfs(d + 1, g, K2); }
    } else {
        for (int g = lim + 1; g < nv; g++) { if (has(&K, g)) continue; bs K2 = K; setb(&K2, g); fullclose(&K2); gs[d] = g; dfs(d + 1, g, K2); }
    }
}

static unsigned long long rs = 88172645463325252ULL;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }
static void shuffle(int *a, int n) { for (int i = n - 1; i > 0; i--) { int j = rnd() % (i + 1); int t = a[i]; a[i] = a[j]; a[j] = t; } }

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); if (!f) { perror("sys"); return 1; }
    if (fscanf(f, "%d %d %d", &nv, &ne, &nr) != 3) return 1;
    for (int i = 0; i < nv; i++) if (fscanf(f, "%31s", names[i]) != 1) return 1;
    char line[8192]; if (!fgets(line, sizeof line, f)) return 1;
    for (int e = 0; e < ne; e++) { if (!fgets(line, sizeof line, f)) return 1; char *q = line; int v, n; while (sscanf(q, "%d%n", &v, &n) == 1) { setb(&em[e], v); q += n; } }
    fclose(f);
    nr = 0;
    const char *rf = NULL;
    int ordertest = !strcmp(argv[2], "ordertest");
    if (ordertest && argc > 5 && strcmp(argv[5], "-")) rf = argv[5];
    if (!ordertest && argc > 7 && strcmp(argv[7], "-")) rf = argv[7];
    if (rf) {   /* rules file in bf.c format: header nv ne nr, names, ne eq lines, nr rule lines 'tgt trig...' */
        FILE *g = fopen(rf, "r"); int nv2, ne2, nr2; if (!g || fscanf(g, "%d %d %d", &nv2, &ne2, &nr2) != 3) return 1;
        for (int i = 0; i < nv2; i++) { char s[32]; if (fscanf(g, "%31s", s) != 1 || strcmp(s, names[i])) { printf("name mismatch at %d\n", i); return 1; } }
        if (!fgets(line, sizeof line, g)) return 1;
        for (int e = 0; e < ne2; e++) if (!fgets(line, sizeof line, g)) return 1;
        for (int r = 0; r < nr2; r++) { if (!fgets(line, sizeof line, g)) return 1; char *q = line; int v, n, first = 1;
            while (sscanf(q, "%d%n", &v, &n) == 1) { if (first) { rg[nr] = v; first = 0; } else setb(&rt[nr], v); q += n; } nr++; }
        fclose(g);
    }
    for (int v = 0; v < nv; v++) setb(&full, v);
    if (!strcmp(argv[2], "check")) {   /* lk sys check <plain|look> [rules]: guess-name sets from stdin */
        look = !strcmp(argv[3], "look");
        for (int i = 0; i < nv; i++) perm[i] = i;
        while (fgets(line, sizeof line, stdin)) {
            bs K = {{0, 0}}; fullclose(&K); int k = 0;
            for (char *tok = strtok(line, " \t\r\n"); tok; tok = strtok(NULL, " \t\r\n")) {
                int v = -1; for (int i = 0; i < nv; i++) if (!strcmp(names[i], tok)) v = i;
                if (v < 0) { printf("unknown %s\n", tok); return 1; }
                setb(&K, v); fullclose(&K); k++;
            }
            printf("guesses=%d closure=%d/%d covered_eqs=%d\n", k, pc(&K), nv, ncov(&K));
        }
        return 0;
    }
    if (ordertest) {
        int nt = atoi(argv[3]), ss = atoi(argv[4]); look = 1;
        int diff = 0, fulls = 0;
        for (int t = 0; t < nt; t++) {
            int set[MAXV]; for (int i = 0; i < nv; i++) set[i] = i; shuffle(set, nv);
            int sz[6];
            for (int o = 0; o < 6; o++) {
                for (int i = 0; i < nv; i++) perm[i] = i; shuffle(perm, nv);
                int ord[16]; memcpy(ord, set, sizeof(int) * ss); shuffle(ord, ss);
                bs K = {{0, 0}}; plclose(&K); lookfix(&K);
                for (int i = 0; i < ss; i++) { setb(&K, ord[i]); fullclose(&K); }
                sz[o] = pc(&K);
            }
            int d = 0; for (int o = 1; o < 6; o++) if (sz[o] != sz[0]) d = 1;
            diff += d; fulls += (sz[0] == nv);
            if (d) { printf("ORDER-DEPENDENT set:"); for (int i = 0; i < ss; i++) printf(" %s", names[set[i]]); printf(" sizes"); for (int o = 0; o < 6; o++) printf(" %d", sz[o]); printf("\n"); }
        }
        printf("ordertest nrules=%d trials=%d setsize=%d order-dependent=%d full=%d\n", nr, nt, ss, diff, fulls);
        return 0;
    }
    kmax = atoi(argv[2]); int part = atoi(argv[3]), np = atoi(argv[4]);
    look = !strcmp(argv[5], "look"); desc = !strcmp(argv[6], "desc");
    for (int i = 0; i < nv; i++) perm[i] = desc ? nv - 1 - i : i;
    bs K0 = {{0, 0}}; fullclose(&K0);
    nodes[0] = 1; best[0] = pc(&K0);
    if (pc(&K0) == nv) covers[0]++;
    int cnt = 0;
    if (desc) {
        for (int g = nv - 1; g >= 0; g--) { if (has(&K0, g)) continue; if ((cnt++) % np != part) continue;
            bs K = K0; setb(&K, g); fullclose(&K); gs[0] = g; dfs(1, g, K); }
    } else {
        for (int g = 0; g < nv; g++) { if (has(&K0, g)) continue; if ((cnt++) % np != part) continue;
            bs K = K0; setb(&K, g); fullclose(&K); gs[0] = g; dfs(1, g, K); }
    }
    printf("DONE part %d/%d kmax=%d mode=%s order=%s nv=%d ne=%d nr=%d covers:", part, np, kmax, look ? "look" : "plain", desc ? "desc" : "asc", nv, ne, nr);
    for (int k = 0; k <= kmax; k++) printf(" k%d=%lld", k, covers[k]);
    printf(" | nodes:"); for (int k = 0; k <= kmax; k++) printf(" %lld", nodes[k]);
    printf(" | best closure size per depth:"); for (int k = 0; k <= kmax; k++) printf(" %d", best[k]);
    printf("\n");
    return 0;
}
