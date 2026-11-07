/* toyval.c - validate the free-width counting model at toy word size (shape_any agent).
   Reads export_full.py output; builds a toy 2-round BLAKE3 trace (w-bit words, rotations floor(r*w/32)),
   takes the variant's constants from that trace, and for a cluster A (equation names, or whole calls) enumerates
   Sol(A) by guess-and-determine, counting solutions and distinct projections on the boundary B(A).
   Prints log2(count)/w next to the model values delta(W(A)) and rho(A,B(A)).
   Usage: toyval <full.txt> <w> <seed> <item> [item...]     item = equation name (K0:a1) or call name (K0)
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>

#define MAXW 512
#define MAXE 200
static char wname[MAXW][24]; static int nw = 0;
static int isconst[MAXW];
static char ename[MAXE][24]; static int etype[MAXE], erot[MAXE], earg[MAXE][4], ek[MAXE], ne = 0;  /* type 0 ADD3 1 ADD2 2 XROT 3 XOR */
static uint32_t val[MAXW], MASK; static int W;

static int widx(const char *s) {
    for (int i = 0; i < nw; i++) if (!strcmp(wname[i], s)) return i;
    strcpy(wname[nw], s); return nw++;
}
static uint32_t ror(uint32_t x, int r) { r %= W; return r ? ((x >> r) | (x << (W - r))) & MASK : x; }
static uint32_t rol(uint32_t x, int r) { r %= W; return r ? ((x << r) | (x >> (W - r))) & MASK : x; }
static int scaled(int r) { return (r * W) / 32; }

/* value of argument pos given the others (pos 0 = target) */
static uint32_t solve(int e, int pos, uint32_t *v) {
    uint32_t a[4]; for (int j = 0; j < ek[e]; j++) a[j] = v[earg[e][j]];
    switch (etype[e]) {
    case 0: if (pos == 0) return (a[1] + a[2] + a[3]) & MASK;
            if (pos == 1) return (a[0] - a[2] - a[3]) & MASK;
            if (pos == 2) return (a[0] - a[1] - a[3]) & MASK;
            return (a[0] - a[1] - a[2]) & MASK;
    case 1: if (pos == 0) return (a[1] + a[2]) & MASK;
            if (pos == 1) return (a[0] - a[2]) & MASK;
            return (a[0] - a[1]) & MASK;
    case 2: { int r = scaled(erot[e]);
            if (pos == 0) return ror(a[1] ^ a[2], r);
            if (pos == 1) return rol(a[0], r) ^ a[2];
            return rol(a[0], r) ^ a[1]; }
    default: if (pos == 0) return a[1]; return a[0];   /* XOR with constant out: treated as equality (unused) */
    }
}

/* matching-based rho over unknown words */
static int inA[MAXE], mv[MAXW], vis[MAXW], stamp, availw[MAXW];
static int aug(int e) {
    for (int j = 0; j < ek[e]; j++) { int x = earg[e][j]; if (isconst[x] || !availw[x] || vis[x] == stamp) continue; vis[x] = stamp;
        if (mv[x] < 0 || aug(mv[x])) { mv[x] = e; return 1; } }
    return 0;
}

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r"); char line[1024];
    W = atoi(argv[2]); MASK = (W == 32) ? 0xffffffffu : ((1u << W) - 1);
    srand(atoi(argv[3]));
    char constline[8192] = "";
    while (fgets(line, sizeof line, f)) {
        if (!strncmp(line, "CONST ", 6)) { strcpy(constline, line + 6); continue; }
        char nm[24], ty[8], a0[24], a1[24], a2[24], a3[24]; int rot;
        int n = sscanf(line, "%23s %7s %d %23s %23s %23s %23s", nm, ty, &rot, a0, a1, a2, a3);
        strcpy(ename[ne], nm); erot[ne] = rot;
        etype[ne] = !strcmp(ty, "ADD3") ? 0 : !strcmp(ty, "ADD2") ? 1 : !strcmp(ty, "XROT") ? 2 : 3;
        ek[ne] = n - 3; earg[ne][0] = widx(a0); earg[ne][1] = widx(a1); if (n > 5) earg[ne][2] = widx(a2); if (n > 6) earg[ne][3] = widx(a3);
        ne++;
    }
    fclose(f);
    for (char *t = strtok(constline, " \n"); t; t = strtok(NULL, " \n")) isconst[widx(t)] = 1;
    /* reference trace: inputs are words never a target */
    uint32_t IV[8] = {0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19};
    for (int i = 0; i < nw; i++) {
        if (!strncmp(wname[i], "init", 4)) { int k = atoi(wname[i] + 4); val[i] = k < 8 ? IV[k] & MASK : k < 12 ? IV[k - 8] & MASK : k < 14 ? 0 : k == 14 ? (2 * W) & MASK : 11 & MASK; }
        else if (wname[i][0] == 'm') val[i] = ((uint32_t)rand() * 2654435761u ^ (uint32_t)rand()) & MASK;
    }
    for (int e = 0; e < ne; e++) if (etype[e] != 3) val[earg[e][0]] = solve(e, 0, val);
    /* cluster */
    memset(inA, 0, sizeof inA);
    for (int a = 4; a < argc; a++) {
        int hit = 0;
        for (int e = 0; e < ne; e++) {
            char call[24]; strcpy(call, ename[e]); char *c = strchr(call, ':'); if (c) *c = 0;
            if (!strcmp(ename[e], argv[a]) || !strcmp(call, argv[a])) { inA[e] = 1; hit = 1; }
        }
        if (!hit) fprintf(stderr, "no match %s\n", argv[a]);
    }
    int inW[MAXW] = {0}, inB[MAXW] = {0};
    for (int e = 0; e < ne; e++) if (inA[e]) for (int j = 0; j < ek[e]; j++) if (!isconst[earg[e][j]]) inW[earg[e][j]] = 1;
    for (int e = 0; e < ne; e++) if (!inA[e]) for (int j = 0; j < ek[e]; j++) if (inW[earg[e][j]]) inB[earg[e][j]] = 1;
    int nW = 0, nB = 0, nAe = 0, Bl[64];
    for (int i = 0; i < nw; i++) { if (inW[i]) nW++; if (inB[i]) { Bl[nB++] = i; } }
    for (int e = 0; e < ne; e++) nAe += inA[e];
    /* model: delta = |W| - e_A(W), rho(A,B) = |B| - unmatched(A, W\B) */
    for (int i = 0; i < nw; i++) { mv[i] = -1; availw[i] = inW[i] && !inB[i]; }
    int unm = 0; for (int e = 0; e < ne; e++) if (inA[e]) { stamp++; if (!aug(e)) unm++; }
    int rho = nB - unm;
    for (int i = 0; i < nw; i++) { mv[i] = -1; availw[i] = inW[i]; }
    int unm2 = 0; for (int e = 0; e < ne; e++) if (inA[e]) { stamp++; if (!aug(e)) unm2++; }
    int dimsol = nW - nAe + unm2;          /* generic dim of Sol(A) (equations all independent if unm2 = 0) */
    /* guess set by greedy closure */
    int known[MAXW]; for (int i = 0; i < nw; i++) known[i] = isconst[i] || !inW[i];
    int guess[16], ng = 0, sched_e[MAXE], sched_p[MAXE], ns = 0, chk[MAXE], nc = 0, used[MAXE] = {0};
    for (;;) {
        /* propagate */
        for (int ch = 1; ch;) {
            ch = 0;
            for (int e = 0; e < ne; e++) if (inA[e] && !used[e]) {
                int unk = -1, cnt = 0;
                for (int j = 0; j < ek[e]; j++) if (!known[earg[e][j]]) { cnt++; unk = j; }
                if (cnt == 1) { known[earg[e][unk]] = 1; used[e] = 1; sched_e[ns] = e; sched_p[ns++] = unk; ch = 1; }
                else if (cnt == 0) { used[e] = 1; chk[nc++] = ns; sched_e[ns] = e; sched_p[ns++] = -1; ch = 1; }
            }
        }
        int done = 1; for (int i = 0; i < nw; i++) if (!known[i]) done = 0;
        if (done) break;
        /* choose the unknown word appearing in most equations with exactly 2 unknowns */
        int best = -1, bs = -1;
        for (int i = 0; i < nw; i++) if (!known[i]) {
            int s = 0;
            for (int e = 0; e < ne; e++) if (inA[e] && !used[e]) {
                int cnt = 0, has = 0;
                for (int j = 0; j < ek[e]; j++) if (!known[earg[e][j]]) { cnt++; if (earg[e][j] == i) has = 1; }
                if (has && cnt == 2) s++;
            }
            if (s > bs) { bs = s; best = i; }
        }
        known[best] = 1; guess[ng++] = best;
        sched_e[ns] = -1; sched_p[ns++] = best;    /* marker */
        if (ng > 4) { printf("needs > 4 guesses, skip\n"); return 0; }
    }
    printf("cluster |A|=%d |W|=%d |B|=%d  model: dim Sol = %d, rho(A,B) = %d ; guesses %d checks %d\n", nAe, nW, nB, dimsol, rho, ng, nc);
    if ((long)ng * W > 34) { printf("too big to enumerate at w=%d\n", W); return 0; }
    /* enumerate */
    long HS = 1L << 27; uint64_t *H = calloc(HS, 8); long distinct = 0, total = 0;
    uint64_t lim = 1ULL << (ng * W);
    for (uint64_t g = 0; g < lim; g++) {
        int gi = 0, ok = 1;
        for (int s = 0; s < ns && ok; s++) {
            if (sched_e[s] < 0) { val[sched_p[s]] = (g >> (W * gi)) & MASK; gi++; continue; }
            int e = sched_e[s];
            if (sched_p[s] >= 0) val[earg[e][sched_p[s]]] = solve(e, sched_p[s], val);
            else if (val[earg[e][0]] != solve(e, 0, val)) ok = 0;
        }
        if (!ok) continue;
        total++;
        uint64_t h = 0x9E3779B97F4A7C15ULL;
        for (int b = 0; b < nB; b++) { h ^= val[Bl[b]]; h *= 0xBF58476D1CE4E5B9ULL; h ^= h >> 31; }
        if (!h) h = 1;
        for (long i = (long)(h & (HS - 1));; i = (i + 1) & (HS - 1)) {
            if (!H[i]) { H[i] = h; distinct++; break; }
            if (H[i] == h) break;
        }
    }
    printf("  measured at w=%d: log2(|Sol(A)|)/w = %.3f (model %d)   log2(distinct on B)/w = %.3f (model %d)\n",
           W, log2((double)total) / W, dimsol, log2((double)distinct) / W, rho);
    return 0;
}
