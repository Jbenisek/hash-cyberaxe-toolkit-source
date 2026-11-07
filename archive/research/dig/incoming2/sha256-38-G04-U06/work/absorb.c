/* absorb.c - which chaining-value differences can the first 4 rows of the second block absorb?  Own code.
   Real SHA-256 step function (rows i = 0..3 of the 37-step compression), two members x, y with CV_y = CV_x + delta (modular, per word).
   Test A (free dW): for each subset S of the 8 CV words, random nonzero delta on S, random W0..W3 for x; y gets the W_i that makes E_i^y = E_i^x
        (row by row).  Count trials where also A_i^y = A_i^x for i=0..3 (state after row 3 identical).
   Test B (dW = 0): y uses the same W0..W3; count trials where state rows 0..3 are all identical.
   Validation: delta = 0 must give 100% in both; the SFS published CV/M must reproduce rows (done by traillab check). */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
static u32 ROR(u32 x, int n) { return (x >> n) | (x << (32 - n)); }
static u32 S0(u32 x) { return ROR(x, 2) ^ ROR(x, 13) ^ ROR(x, 22); }
static u32 S1(u32 x) { return ROR(x, 6) ^ ROR(x, 11) ^ ROR(x, 25); }
static u32 CH(u32 x, u32 y, u32 z) { return (x & y) ^ (~x & z); }
static u32 MJ(u32 x, u32 y, u32 z) { return (x & y) ^ (x & z) ^ (y & z); }
static const u32 K[4] = {0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5};
static u64 st = 88172645463325252ull;
static u32 rnd(void) { st ^= st << 13; st ^= st >> 7; st ^= st << 17; return (u32)(st >> 16); }
/* rows: A[-4..3], E[-4..3] stored at index +4; cv order: a b c d e f g h -> A_-1 A_-2 A_-3 A_-4 E_-1 E_-2 E_-3 E_-4 */
static void init(u32 *A, u32 *E, const u32 cv[8]) { for (int i = 0; i < 4; i++) { A[3 - i] = cv[i]; E[3 - i] = cv[4 + i]; } }
/* step row i (0..3) with W; returns nothing, fills A[i+4], E[i+4] */
static void step(u32 *A, u32 *E, int i, u32 W) {
  int p = i + 4;
  E[p] = A[p - 4] + E[p - 4] + S1(E[p - 1]) + CH(E[p - 1], E[p - 2], E[p - 3]) + K[i] + W;
  A[p] = E[p] - A[p - 4] + S0(A[p - 1]) + MJ(A[p - 1], A[p - 2], A[p - 3]);
}
int main(int argc, char **argv) {
  long N = argc > 1 ? atol(argv[1]) : 100000;
  /* sanity: a full-SHA reference of rows against the textbook is done by traillab check; here: delta = 0 identity */
  const char *nm[8] = {"a(A-1)", "b(A-2)", "c(A-3)", "d(A-4)", "e(E-1)", "f(E-2)", "g(E-3)", "h(E-4)"};
  printf("subset(mask over a b c d e f g h, bit0=a) | A: free dW absorbs, rows 0..3 identical | B: dW=0, rows 0..3 identical | trials\n");
  long goodA_in = 0, goodA_out = 0, nA_in = 0, nA_out = 0, goodB_nz = 0, nB_nz = 0;
  for (int S = 0; S < 256; S++) {
    long okA = 0, okB = 0, n = (S == 0) ? N : N;
    for (long t = 0; t < n; t++) {
      u32 cv[8], cvy[8], W[4];
      for (int k = 0; k < 8; k++) cv[k] = rnd();
      for (int k = 0; k < 4; k++) W[k] = rnd();
      for (int k = 0; k < 8; k++) { u32 d = 0; if ((S >> k) & 1) { do d = rnd(); while (!d); } cvy[k] = cv[k] + d; }
      u32 Ax[8], Ex[8], Ay[8], Ey[8], By[8], BEy[8];
      init(Ax, Ex, cv); init(Ay, Ey, cvy); init(By, BEy, cvy);
      for (int i = 0; i < 4; i++) step(Ax, Ex, i, W[i]);
      /* A: choose W_i^y so that E_i^y = E_i^x : E = A_{i-4}+E_{i-4}+S1+CH+K+W  => solve for W */
      for (int i = 0; i < 4; i++) { int p = i + 4;
        u32 base = Ay[p - 4] + Ey[p - 4] + S1(Ey[p - 1]) + CH(Ey[p - 1], Ey[p - 2], Ey[p - 3]) + K[i];
        u32 Wy = Ex[p] - base; step(Ay, Ey, i, Wy); }
      for (int i = 0; i < 4; i++) step(By, BEy, i, W[i]);
      int sameA = 1, sameB = 1;
      for (int i = 0; i < 4; i++) { if (Ax[i + 4] != Ay[i + 4] || Ex[i + 4] != Ey[i + 4]) sameA = 0; if (Ax[i + 4] != By[i + 4] || Ex[i + 4] != BEy[i + 4]) sameB = 0; }
      okA += sameA; okB += sameB;
    }
    int inE = (S & 0x0f) == 0;   /* subset within e f g h */
    if (S) { if (inE) { goodA_in += okA; nA_in += n; } else { goodA_out += okA; nA_out += n; } goodB_nz += okB; nB_nz += n; }
    if (S == 0 || S == 0xf0 || S == 0x10 || S == 0x80 || S == 0x01 || S == 0x08 || S == 0x0f || S == 0xff || okA != 0 && !inE || okB != 0 && S != 0) {
      printf("%02x ", S); for (int k = 0; k < 8; k++) if ((S >> k) & 1) printf("%s ", nm[k]);
      printf("| A %ld/%ld | B %ld/%ld\n", okA, n, okB, n);
    }
  }
  printf("TOTAL nonzero subsets inside {e,f,g,h}: free-dW absorbed %ld of %ld ; subsets touching a,b,c or d: absorbed %ld of %ld\n", goodA_in, nA_in, goodA_out, nA_out);
  printf("TOTAL dW=0 and delta != 0: rows 0..3 identical in %ld of %ld trials\n", goodB_nz, nB_nz);
  return 0;
}
