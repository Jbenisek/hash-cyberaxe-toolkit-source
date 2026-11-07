/* verify_audit_1: can a 7-guess look-mode cover (3 residual checks) be run as the balanced two-list join that the
   "2^81" projection assumes?  Same closure/look semantics as lk.c (plain one-unknown propagation + optional rules;
   look = accept z when plain closure of K+z covers >= as many new equations as new words).
   usage: split <sysfile> greedy <runs> <seed> <maxsize>   -> random greedy look covers, redundancy-pruned, printed
          split <sysfile> split                            -> guess-name sets from stdin; for every assignment of the
                guesses to core/A/B: KA = look(core+A), KB = look(core+B), J = KA u KB;
                j = equations fully inside J but inside neither KA nor KB (join conditions, 32 bits each);
                then look(J) must be full.  Reports the best j for |A|,|B| >= 3 (each list can reach 2^80)
                and for any split; the 2^81 rule needs j = 3 with |A|,|B| >= 3 (2.5 words = 80 bits per side). */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define MAXV 128
#define MAXE 160
typedef struct { uint64_t w[2]; } bs;
static int nv, ne;
static char names[MAXV][32];
static bs em[MAXE];
static inline int has(const bs *k, int v) { return (k->w[v >> 6] >> (v & 63)) & 1; }
static inline void setb(bs *k, int v) { k->w[v >> 6] |= 1ULL << (v & 63); }
static inline int pc(const bs *k) { return __builtin_popcountll(k->w[0]) + __builtin_popcountll(k->w[1]); }
static inline int sub(const bs *a, const bs *k) { return !((a->w[0] & ~k->w[0]) | (a->w[1] & ~k->w[1])); }
static void plc(bs *K) {
    int ch = 1;
    while (ch) { ch = 0;
        for (int e = 0; e < ne; e++) { uint64_t u0 = em[e].w[0] & ~K->w[0], u1 = em[e].w[1] & ~K->w[1];
            if (__builtin_popcountll(u0) + __builtin_popcountll(u1) == 1) { K->w[0] |= u0; K->w[1] |= u1; ch = 1; } } }
}
static int ncov(const bs *K) { int c = 0; for (int e = 0; e < ne; e++) c += sub(&em[e], K); return c; }
static int nacc;
static void lookfix(bs *K) {
    int ch = 1;
    while (ch) { ch = 0;
        for (int z = 0; z < nv; z++) { if (has(K, z)) continue;
            int c0 = ncov(K), n0 = pc(K); bs T = *K; setb(&T, z); plc(&T);
            if (ncov(&T) - c0 >= pc(&T) - n0) { *K = T; ch = 1; nacc++; } } }
}
static int LOOK = 1;
static void lclose(bs *K) { plc(K); if (LOOK) lookfix(K); }
static unsigned long long rs = 88172645463325252ULL;
static unsigned rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (unsigned)(rs >> 11); }

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int nr; char line[8192];
    if (!f || fscanf(f, "%d %d %d", &nv, &ne, &nr) != 3) return 1;
    for (int i = 0; i < nv; i++) if (fscanf(f, "%31s", names[i]) != 1) return 1;
    if (!fgets(line, sizeof line, f)) return 1;
    for (int e = 0; e < ne; e++) { if (!fgets(line, sizeof line, f)) return 1; char *q = line; int v, n; while (sscanf(q, "%d%n", &v, &n) == 1) { setb(&em[e], v); q += n; } }
    fclose(f);
    if (getenv("PLAIN")) LOOK = 0;
    if (!strcmp(argv[2], "greedy")) {
        int runs = atoi(argv[3]); rs ^= (unsigned long long)atoll(argv[4]) * 0x9E3779B97F4A7C15ULL; int maxs = atoi(argv[5]);
        int hist[64] = {0};
        for (int r = 0; r < runs; r++) {
            bs K = {{0, 0}}; lclose(&K); int G[64], g = 0;
            while (pc(&K) < nv) {
                int bestv = -1, cand[MAXV], nc = 0, sc[MAXV];
                int noise = getenv("NOISE") ? atoi(getenv("NOISE")) : 0;
                for (int z = 0; z < nv; z++) { sc[z] = -1; if (has(&K, z)) continue; bs T = K; setb(&T, z);
                    /* cheap score: plain closure size (look only after the pick) */ plc(&T); sc[z] = pc(&T);
                    if (sc[z] > bestv) bestv = sc[z]; }
                for (int z = 0; z < nv; z++) if (sc[z] >= 0 && sc[z] >= bestv - noise) cand[nc++] = z;
                int z = cand[rnd() % nc]; G[g++] = z; setb(&K, z); lclose(&K);
            }
            /* drop redundant guesses (random order) */
            for (int t = 0; t < g; t++) { int i = rnd() % g; int tmp = G[i]; G[i] = G[t]; G[t] = tmp; }
            for (int i = 0; i < g; ) {
                bs K2 = {{0, 0}}; lclose(&K2);
                for (int j = 0; j < g; j++) if (j != i) { setb(&K2, G[j]); lclose(&K2); }
                if (pc(&K2) == nv) { G[i] = G[--g]; } else i++;
            }
            hist[g]++;
            if (g <= maxs) { for (int i = 0; i < g; i++) printf("%s%s", i ? " " : "", names[G[i]]); printf("\n"); }
        }
        fprintf(stderr, "greedy look covers size histogram:"); for (int i = 0; i < 64; i++) if (hist[i]) fprintf(stderr, " %d:%d", i, hist[i]); fprintf(stderr, "\n");
        return 0;
    }
    /* split mode */
    int nsets = 0, bal3 = 0;
    int jhist_bal[8] = {0}, jhist_any[8] = {0};
    while (fgets(line, sizeof line, stdin)) {
        int G[16], g = 0;
        for (char *tok = strtok(line, " \t\r\n"); tok; tok = strtok(NULL, " \t\r\n")) {
            int v = -1; for (int i = 0; i < nv; i++) if (!strcmp(names[i], tok)) v = i;
            if (v < 0) { printf("unknown %s\n", tok); return 1; } G[g++] = v; }
        if (!g) continue;
        bs K = {{0, 0}}; lclose(&K); for (int i = 0; i < g; i++) { setb(&K, G[i]); lclose(&K); }
        if (pc(&K) != nv) { printf("not a look cover (%d/%d)\n", pc(&K), nv); continue; }
        nsets++;
        int pw = 1; for (int i = 0; i < g; i++) pw *= 3;
        int bestbal = -1, bestany = -1; char desc[512] = "";
        for (int a = 0; a < pw; a++) {
            int x = a, role[16], na = 0, nb = 0, ncore = 0;
            for (int i = 0; i < g; i++) { role[i] = x % 3; x /= 3; if (role[i] == 1) na++; else if (role[i] == 2) nb++; else ncore++; }
            if (na == 0 || nb == 0 || na > nb) continue;
            bs KA = {{0, 0}}, KB = {{0, 0}}; lclose(&KA); lclose(&KB);
            nacc = 0;
            for (int i = 0; i < g; i++) { if (role[i] != 2) { setb(&KA, G[i]); lclose(&KA); } }
            int accA = nacc; nacc = 0;
            for (int i = 0; i < g; i++) { if (role[i] != 1) { setb(&KB, G[i]); lclose(&KB); } }
            int accB = nacc;
            bs J = {{KA.w[0] | KB.w[0], KA.w[1] | KB.w[1]}};
            int j = 0;
            for (int e = 0; e < ne; e++) if (sub(&em[e], &J) && !sub(&em[e], &KA) && !sub(&em[e], &KB)) j++;
            bs P = J; nacc = 0; lclose(&P); int accP = nacc;
            if (pc(&P) != nv) continue;
            if (j > bestany) bestany = j;
            if (na >= 3 && nb >= 3 && j > bestbal) {
                bestbal = j;
                int o = 0; o += sprintf(desc + o, "core{");
                for (int i = 0; i < g; i++) if (role[i] == 0) o += sprintf(desc + o, " %s", names[G[i]]);
                o += sprintf(desc + o, " } A{"); for (int i = 0; i < g; i++) if (role[i] == 1) o += sprintf(desc + o, " %s", names[G[i]]);
                o += sprintf(desc + o, " } B{"); for (int i = 0; i < g; i++) if (role[i] == 2) o += sprintf(desc + o, " %s", names[G[i]]);
                sprintf(desc + o, " } |KA|=%d |KB|=%d |J|=%d accA=%d accB=%d accPost=%d", pc(&KA), pc(&KB), pc(&J), accA, accB, accP);
            }
        }
        if (bestbal >= 0) jhist_bal[bestbal]++; if (bestany >= 0) jhist_any[bestany]++;
        if (bestbal >= 3) bal3++;
        printf("set%d g=%d best j (|A|,|B|>=3) = %d ; best j any split = %d ; %s\n", nsets, g, bestbal, bestany, desc);
        fflush(stdout);
    }
    printf("SUMMARY sets=%d ; histogram of best balanced j:", nsets); for (int i = 0; i < 8; i++) printf(" %d:%d", i, jhist_bal[i]);
    printf(" ; histogram of best any-split j:"); for (int i = 0; i < 8; i++) printf(" %d:%d", i, jhist_any[i]);
    printf(" ; sets with a balanced j>=3 split: %d\n", bal3);
    return 0;
}
