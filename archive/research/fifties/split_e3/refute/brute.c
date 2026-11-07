/* Exhaustive word-level tests on the core model written by export.py (one relation per line as word indices).
   min  K      : does any guess set of size K close every word?   (k = K - DOF)
   mitm a s    : fixed set A (|A| = a), sides P, Q with |P| = |Q| = s (disjoint, outside closure(A));
                 do closure(A+P) and closure(A+Q) cover every word?  (two-list meet in the middle, k = a + 2s - DOF)
   Redundant guesses (already in the closure of the earlier ones) are skipped; this never hides a smaller solution.
   build: gcc -O3 -march=native -fopenmp -o brute brute.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef unsigned __int128 u128;
static int NW, NR; static u128 REL[256]; static u128 ALL;
static inline int pc(u128 x) { return __builtin_popcountll((uint64_t)x) + __builtin_popcountll((uint64_t)(x >> 64)); }
static inline u128 bit(int i) { return ((u128)1) << i; }
static u128 closure(u128 k) {
  int ch = 1;
  while (ch) { ch = 0;
    for (int r = 0; r < NR; r++) { u128 u = REL[r] & ~k; if (u && !(u & (u - 1))) { k |= u; ch = 1; } } }
  return k;
}
static long long found = 0, t1pre = 0; static int K, T1A = -1, T1D = -1;
static void dfs_min(int start, int depth, u128 kn, u128 set) {
  if (depth == K) { if (kn == ALL) { long long f0;
    #pragma omp atomic capture
    f0 = found++;
    if (T1A >= 0) { int pre = 0; for (int i = 0; i < NW && !pre; i++) if (set & bit(i)) { u128 c = closure(set & ~bit(i)); if ((c & bit(T1A)) && (c & bit(T1D))) pre = 1; }
      if (pre) {
        #pragma omp atomic
        t1pre++;
      } }
    if (f0 < 3) { printf("  closing set:"); for (int i = 0; i < NW; i++) if (set & bit(i)) printf(" %d", i); printf("\n"); } } return; }
  if (kn == ALL) {
    #pragma omp atomic
    found++;
    return; }
  for (int w = start; w < NW; w++) { if (kn & bit(w)) continue; dfs_min(w + 1, depth + 1, closure(kn | bit(w)), set | bit(w)); }
}
int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "r"); fscanf(f, "%d %d", &NW, &NR);
  for (int r = 0; r < NR; r++) { int m; fscanf(f, "%d", &m); REL[r] = 0; for (int j = 0; j < m; j++) { int w; fscanf(f, "%d", &w); REL[r] |= bit(w); } }
  ALL = (NW == 128) ? ~(u128)0 : (bit(NW) - 1);
  if (!strcmp(argv[2], "min")) {
    K = atoi(argv[3]); if (argc > 5) { T1A = atoi(argv[4]); T1D = atoi(argv[5]); }
    long long tot = 0;
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:tot)
    for (int w0 = 0; w0 < NW; w0++) {
      long long save;
      #pragma omp critical
      { save = found; }
      /* run each first word separately (found is a shared counter; small races only affect printing) */
      u128 kn = closure(bit(w0));
      long long before = found;
      dfs_min(w0 + 1, 1, kn, bit(w0));
      (void)save; (void)before;
    }
    printf("min K=%d: closing guess sets found %lld; with the counter-high word computable before the last guess: %lld\n", K, found, t1pre);
    return 0;
  }
  /* mitm */
  int a = atoi(argv[3]), s = atoi(argv[4]);
  long long nA = 0, hits = 0;
  /* enumerate A as sorted tuples via an explicit stack (a <= 5) */
  int idx[8];
  /* collect all A first */
  int cap = 1 << 26; int *As = malloc(sizeof(int) * 8 * (size_t)cap); long long na = 0;
  for (int i = 0; i < a; i++) idx[i] = i;
  if (argc > 5) { for (int i = 0; i < a; i++) As[i] = atoi(argv[5 + i]); na = 1; }
  else if (a == 0) { na = 1; }
  else while (1) {
    for (int i = 0; i < a; i++) As[na * 8 + i] = idx[i]; na++;
    int i = a - 1; while (i >= 0 && idx[i] == NW - a + i) i--; if (i < 0) break;
    idx[i]++; for (int j = i + 1; j < a; j++) idx[j] = idx[j - 1] + 1;
  }
  printf("mitm |A|=%d |P|=|Q|=%d: %lld sets A\n", a, s, na); fflush(stdout);
  #pragma omp parallel for schedule(dynamic, 256) reduction(+:nA, hits)
  for (long long t = 0; t < na; t++) {
    u128 A = 0; for (int i = 0; i < a; i++) A |= bit(As[t * 8 + i]);
    u128 cA = closure(A);
    int redundant = 0;            /* skip A with a guess inside the closure of the others (never minimal) */
    for (int i = 0; i < a && !redundant; i++) if (closure(A & ~bit(As[t * 8 + i])) & bit(As[t * 8 + i])) redundant = 1;
    if (redundant) continue;
    nA++;
    /* side closures */
    int nmax = (s == 1) ? NW : NW * NW / 2 + NW; u128 *C = malloc(sizeof(u128) * nmax); u128 *S = malloc(sizeof(u128) * nmax); int nc = 0;
    for (int p = 0; p < NW; p++) {
      if (cA & bit(p)) continue;
      u128 c1 = closure(cA | bit(p));
      if (s == 1) { C[nc] = c1; S[nc] = bit(p); nc++; continue; }
      for (int q = p + 1; q < NW; q++) { if (c1 & bit(q)) continue; C[nc] = closure(c1 | bit(q)); S[nc] = bit(p) | bit(q); nc++; }
    }
    /* order side closures by size (descending) and stop when two sizes cannot reach every word */
    int *ord = malloc(sizeof(int) * (nc + 1)); int *sz = malloc(sizeof(int) * (nc + 1));
    for (int i = 0; i < nc; i++) { ord[i] = i; sz[i] = pc(C[i]); }
    for (int i = 1; i < nc; i++) { int x = ord[i], j = i - 1; while (j >= 0 && sz[ord[j]] < sz[x]) { ord[j + 1] = ord[j]; j--; } ord[j + 1] = x; }
    int need = NW + pc(cA);
    for (int ii = 0; ii < nc; ii++) for (int jj = ii + 1; jj < nc; jj++) {
      int i = ord[ii], j = ord[jj];
      if (sz[i] + sz[j] < need) break;
      if (S[i] & S[j]) continue;
      if ((C[i] | C[j]) == ALL) {
        hits++;
        if (hits <= 3) {
          #pragma omp critical
          { printf("  cover: A"); for (int x = 0; x < NW; x++) if (A & bit(x)) printf(" %d", x);
            printf(" | P"); for (int x = 0; x < NW; x++) if (S[i] & bit(x)) printf(" %d", x);
            printf(" | Q"); for (int x = 0; x < NW; x++) if (S[j] & bit(x)) printf(" %d", x); printf("\n"); }
        }
      }
    }
    free(C); free(S); free(ord); free(sz);
  }
  printf("mitm |A|=%d |P|=|Q|=%d: non-redundant A %lld, covering (A,P,Q) %lld\n", a, s, nA, hits);
  return 0;
}
