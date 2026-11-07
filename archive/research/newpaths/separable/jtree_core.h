/* shared model code: load a system file, closure, delta */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

typedef unsigned __int128 M;
#define MAXW 128
#define MAXE 256
static int N, E, NM, F;
static char names[MAXW][32];
static char enames[MAXE][24];
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
static int ein(M X) { int c = 0; for (int e = 0; e < E; e++) if (!(emask[e] & ~X)) c++; return c; }
static int delta(M X) { return pc(X) - ein(X); }
static void load(const char *fn) {
    FILE *f = fopen(fn, "r"); if (!f) { perror(fn); exit(1); }
    if (fscanf(f, "%d %d %d %d", &N, &E, &NM, &F) != 4) exit(2);
    for (int i = 0; i < N; i++) if (fscanf(f, "%31s", names[i]) != 1) exit(3);
    for (int e = 0; e < E; e++) {
        int k; if (fscanf(f, "%23s %d", enames[e], &k) != 2) exit(4);
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
