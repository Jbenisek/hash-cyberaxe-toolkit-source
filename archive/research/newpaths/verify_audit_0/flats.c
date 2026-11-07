/* verify_audit_0: independent minimum-guess search, breadth-first over distinct closed sets ("flats").
   Different algorithm from audit/bf.c (DFS over sorted guess sets): level j holds every distinct closure of a
   j-word guess set, deduplicated; level j+1 = { cl(F + g) : F in level j, g not in F }.  Valid because the closure
   is a closure operator (monotone; see notes.txt); the first level containing the full set gives kmin.
   Closure modes:
     plain : an equation with exactly one unknown word gives it
     look  : plain, plus: an unknown z is accepted when guessing it and closing plainly covers at least as many
             new equations as it adds words (one equation is a check on z).  All acceptable z found in one scan are
             added, then the scan repeats until none.
     look1 : like look but adds only the first acceptable z per scan (the literal definition; slower), for testing.
   usage: flats <sysfile> <kmax> <plain|look|look1> [maxstore [part npart]]
          flats <sysfile> check <plain|look|look1>   (reads guess-name sets from stdin, prints closure size) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef struct { uint64_t w[2]; } bs;
static int nv, ne, mode;
static char names[128][32];
static bs em[128];
static int ve[128][128], nve[128];
static bs FULL;

static inline int has(bs k, int v) { return (k.w[v >> 6] >> (v & 63)) & 1; }
static inline void setb(bs *k, int v) { k->w[v >> 6] |= 1ULL << (v & 63); }
static inline int pc(bs k) { return __builtin_popcountll(k.w[0]) + __builtin_popcountll(k.w[1]); }
static inline int eqb(bs a, bs b) { return a.w[0] == b.w[0] && a.w[1] == b.w[1]; }
static inline int unk(bs m, bs k) { return __builtin_popcountll(m.w[0] & ~k.w[0]) + __builtin_popcountll(m.w[1] & ~k.w[1]); }

static int ncov(bs K) { int c = 0; for (int e = 0; e < ne; e++) c += unk(em[e], K) == 0; return c; }

/* plain fixpoint by repeated full scans (deliberately not a queue) */
static bs plain(bs K) {
    int ch = 1;
    while (ch) {
        ch = 0;
        for (int e = 0; e < ne; e++) {
            if (unk(em[e], K) == 1) {
                K.w[0] |= em[e].w[0]; K.w[1] |= em[e].w[1]; ch = 1;
            }
        }
    }
    return K;
}
/* plain closure of K + {z}, K already plain-closed: worklist over equations of newly known words */
static bs plain_add(bs K, int z) {
    int q[128], h = 0, t = 0;
    if (has(K, z)) return K;
    setb(&K, z); q[t++] = z;
    while (h < t) {
        int v = q[h++];
        for (int i = 0; i < nve[v]; i++) {
            bs m = em[ve[v][i]];
            if (unk(m, K) == 1) {
                uint64_t u0 = m.w[0] & ~K.w[0], u1 = m.w[1] & ~K.w[1];
                int x = u0 ? __builtin_ctzll(u0) : 64 + __builtin_ctzll(u1);
                setb(&K, x); q[t++] = x;
            }
        }
    }
    return K;
}
static bs close_set(bs K) {      /* K arbitrary -> closure under the chosen mode */
    K = plain(K);
    if (mode == 0) return K;
    for (;;) {
        int c0 = ncov(K), n0 = pc(K);
        bs acc = {{0, 0}};
        int nacc = 0;
        for (int z = 0; z < nv; z++) {
            if (has(K, z)) continue;
            bs K3 = plain_add(K, z);
            if (ncov(K3) - c0 >= pc(K3) - n0) { setb(&acc, z); nacc++; if (mode == 2) break; }
        }
        if (!nacc) return K;
        for (int z = 0; z < nv; z++) if (has(acc, z)) K = plain_add(K, z);
    }
}

/* hash set of flats */
typedef struct { bs *key; uint8_t *used; size_t cap, n; } hset;
static uint64_t hh(bs k) { uint64_t x = k.w[0] * 0x9E3779B97F4A7C15ULL ^ (k.w[1] + 0x632BE59BD9B4E019ULL) * 0xC2B2AE3D27D4EB4FULL; x ^= x >> 29; return x; }
static void hinit(hset *s, size_t cap) { s->cap = cap; s->n = 0; s->key = malloc(cap * sizeof(bs)); s->used = calloc(cap, 1); if (!s->key || !s->used) { fprintf(stderr, "oom\n"); exit(2); } }
static void hfree(hset *s) { free(s->key); free(s->used); }
static int hadd(hset *s, bs k) {          /* 1 if new */
    if (2 * (s->n + 1) > s->cap) {
        hset t; hinit(&t, s->cap * 2);
        for (size_t i = 0; i < s->cap; i++) if (s->used[i]) hadd(&t, s->key[i]);
        hfree(s); *s = t;
    }
    size_t i = hh(k) & (s->cap - 1);
    while (s->used[i]) { if (eqb(s->key[i], k)) return 0; i = (i + 1) & (s->cap - 1); }
    s->used[i] = 1; s->key[i] = k; s->n++; return 1;
}

static int lookup(const char *s) { for (int i = 0; i < nv; i++) if (!strcmp(names[i], s)) return i; return -1; }

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); int nr;
    if (!f || fscanf(f, "%d %d %d", &nv, &ne, &nr) != 3) { fprintf(stderr, "bad sys\n"); return 1; }
    for (int i = 0; i < nv; i++) if (fscanf(f, "%31s", names[i]) != 1) return 1;
    char line[4096]; if (!fgets(line, sizeof line, f)) return 1;
    for (int e = 0; e < ne; e++) {
        if (!fgets(line, sizeof line, f)) return 1;
        char *p = line; int v, n;
        while (sscanf(p, "%d%n", &v, &n) == 1) { setb(&em[e], v); ve[v][nve[v]++] = e; p += n; }
    }
    fclose(f);
    for (int v = 0; v < nv; v++) setb(&FULL, v);
    const char *ms = argv[3];
    mode = !strcmp(ms, "plain") ? 0 : !strcmp(ms, "look") ? 1 : !strcmp(ms, "look1") ? 2 : -1;
    if (mode < 0) { fprintf(stderr, "mode?\n"); return 1; }
    if (!strcmp(argv[2], "check")) {
        while (fgets(line, sizeof line, stdin)) {
            bs G = {{0, 0}}; int k = 0;
            for (char *tok = strtok(line, " \t\r\n"); tok; tok = strtok(NULL, " \t\r\n")) {
                int v = lookup(tok); if (v < 0) { printf("unknown %s\n", tok); return 1; } setb(&G, v); k++; }
            bs K = close_set(G);
            printf("guesses=%d closure=%d/%d covered=%d/%d\n", k, pc(K), nv, ncov(K), ne);
        }
        return 0;
    }
    int kmax = atoi(argv[2]);
    size_t maxstore = argc > 4 ? strtoull(argv[4], 0, 10) : 200000000ULL;
    int part = argc > 6 ? atoi(argv[5]) : 0, npart = argc > 6 ? atoi(argv[6]) : 1;   /* last level split */
    int hist[129] = {0};
    bs *cur = malloc(sizeof(bs)); size_t ncur = 1;
    cur[0] = close_set((bs){{0, 0}});
    printf("level 0: 1 flat, size %d, full=%d\n", pc(cur[0]), eqb(cur[0], FULL));
    if (eqb(cur[0], FULL)) { printf("RESULT kmin=0\n"); return 0; }
    for (int k = 1; k <= kmax; k++) {
        hset s; hinit(&s, 1 << 16);
        long long ext = 0; int best = 0, bestcov = 0; int hit = 0; bs hitF = {{0,0}}; int hitg = -1; size_t hiti = 0;
        int last = (k == kmax);
        for (size_t i = 0; i < ncur && !hit; i++) {
            if (last && (int)(i % npart) != part) continue;
            for (int g = 0; g < nv; g++) {
                if (has(cur[i], g)) continue;
                bs K = cur[i]; setb(&K, g);
                K = close_set(K); ext++;
                if (pc(K) > best) { best = pc(K); bestcov = ncov(K); }
                if (last) hist[pc(K)]++;
                if (eqb(K, FULL)) { hit = 1; hitF = cur[i]; hitg = g; hiti = i; break; }
                if (!last) { hadd(&s, K); if (s.n > maxstore) { printf("level %d: store limit hit\n", k); return 3; } }
            }
        }
        printf("level %d: %zu distinct flats, %lld extensions, largest closure %d/%d (covering %d/%d eqs)\n",
               k, last ? (size_t)0 : s.n, ext, best, nv, bestcov, ne);
        fflush(stdout);
        if (last) { printf("last-level closure-size histogram (part %d/%d):", part, npart); for (int s2 = 0; s2 <= nv; s2++) if (hist[s2]) printf(" %d:%d", s2, hist[s2]); printf("\n"); }
        if (hit) {
            printf("RESULT kmin=%d (full closure reached; parent flat #%zu of size %d, last guess %s)\n", k, hiti, pc(hitF), names[hitg]);
            return 0;
        }
        if (last) break;
        free(cur);
        cur = malloc(s.n * sizeof(bs)); ncur = 0;
        for (size_t i = 0; i < s.cap; i++) if (s.used[i]) cur[ncur++] = s.key[i];
        hfree(&s);
    }
    printf("RESULT no cover with <= %d guesses (mode %s)\n", kmax, ms);
    return 0;
}
