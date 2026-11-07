/* r37 dense-part single-word freedom: for k in {0,1,2,3}, count values v of A_k (same in both members, all other
   dense-part A words as in the published Step-1 solution S) for which E4..E13 and W8..W13 of both members still satisfy
   every cell (values, XOR differences, '+' pairs) and the W8 two-bit conditions.  k = 0 must give 12,103,680. */
#include <stdio.h>
#include <stdlib.h>
#include "consts.h"
#define ROR(x,n) (((x) >> (n)) | ((x) << (32 - (n))))
static inline uint32_t S0(uint32_t x){ return ROR(x,2) ^ ROR(x,13) ^ ROR(x,22); }
static inline uint32_t S1(uint32_t x){ return ROR(x,6) ^ ROR(x,11) ^ ROR(x,25); }
static inline uint32_t MAJ(uint32_t x,uint32_t y,uint32_t z){ return (x&y)^(x&z)^(y&z); }
static inline uint32_t CH(uint32_t x,uint32_t y,uint32_t z){ return (x&y)^(~x&z); }
int main(int argc, char **argv){
  int k = atoi(argv[1]);
  uint64_t cnt = 0; uint32_t first[16]; int nf = 0;
  for (uint64_t vv = 0; vv < (1ull << 32); vv++){
    uint32_t v = (uint32_t)vv, A[2][14], E[2][14], W[2][14];
    for (int m = 0; m < 2; m++){ for (int i = 0; i < 14; i++) A[m][i] = m ? SAY[i] : SAX[i]; A[m][k] = v; }
    int ok = 1;
    for (int i = 4; i < 14 && ok; i++){
      for (int m = 0; m < 2; m++)
        E[m][i] = A[m][i] + A[m][i-4] - S0(A[m][i-1]) - MAJ(A[m][i-1], A[m][i-2], A[m][i-3]);
      if ((E[0][i] & EM[i]) != EV[i] || (E[0][i] ^ E[1][i]) != ED[i]) ok = 0;
      if (ok && i > 4){ uint32_t q = EP[i] & EP[i-1]; if (q && ((E[0][i] ^ E[0][i-1]) & q)) ok = 0; }
    }
    for (int i = 8; i < 14 && ok; i++){
      for (int m = 0; m < 2; m++)
        W[m][i] = E[m][i] - A[m][i-4] - E[m][i-4] - S1(E[m][i-1]) - CH(E[m][i-1], E[m][i-2], E[m][i-3]) - KK[i];
      if ((W[0][i] & WM[i]) != WV[i] || (W[0][i] ^ W[1][i]) != WD[i]) ok = 0;
    }
    for (int j = 0; j < NX2 && ok; j++){
      uint32_t b1 = (W[0][8] >> X2B1[j]) & 1, b2 = (W[0][8] >> X2B2[j]) & 1;
      if ((b1 == b2) != X2EQ[j]) ok = 0;
    }
    if (ok){ cnt++; if (nf < 16) first[nf++] = v; }
  }
  printf("k=%d valid=%llu  (published A%d = %08x)\n", k, (unsigned long long)cnt, k, SAX[k]);
  for (int i = 0; i < nf; i++) printf("  e.g. %08x\n", first[i]);
  return 0;
}
