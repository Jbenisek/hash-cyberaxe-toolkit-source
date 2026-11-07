// a2r0.c - variant population of a 38-step dense part S (scout2-1, research only): the A2 list (exhaustive over
// 2^32), the A0-free valid (A1, A2) count N_free and |R(A0)| (sampled), and a hill-climb for the top A0 on the
// sample.  Validity is the pkgR38a proof.md 4.1 definition: E cells of rows 4..8 with the '+' pairs and
// (dW_i, ds0 W_i) equal to the published values for i = 8..11 (modular; XOR cells of W8..W10 not required).
// usage: a2r0 A0 .. A15 (member x, hex) [log2 total samples] [seed] [restarts]
// build: gcc -O3 -march=native -o a2r0 a2r0.c -lm      (single thread)
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <math.h>
typedef uint32_t u32;
#include "cells.h"
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline u32 S0(u32 x){return ROR(x,2)^ROR(x,13)^ROR(x,22);}
static inline u32 S1(u32 x){return ROR(x,6)^ROR(x,11)^ROR(x,25);}
static inline u32 s0(u32 x){return ROR(x,7)^ROR(x,18)^(x>>3);}
static inline u32 CH(u32 x,u32 y,u32 z){return (x&y)^(~x&z);}
static inline u32 MAJ(u32 x,u32 y,u32 z){return (x&y)^(x&z)^(y&z);}
static uint64_t rs = 88172645463325252ULL;
static inline u32 rnd(void){ rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (u32)(rs >> 17); }
static u32 *F; static long nF;
static long eval(u32 a0, long n){ long c = 0; for (long i = 0; i < n; i++){ u32 wx = F[i] - a0, wy = wx - DW8; c += (s0(wx) - s0(wy) == DS8); } return c; }

int main(int argc, char **argv){
  if (argc < 17){ fprintf(stderr, "usage\n"); return 1; }
  u32 Ax[16], Ay[16];
  for (int i = 0; i < 16; i++){ Ax[i] = (u32)strtoul(argv[1+i], 0, 16); Ay[i] = Ax[i] ^ DA[i]; }
  int lg = argc > 17 ? atoi(argv[17]) : 24; if (argc > 18) rs = strtoull(argv[18], 0, 10) * 2654435761ULL + 1;
  int restarts = argc > 19 ? atoi(argv[19]) : 48;
  if (DA[3] | DA[4] | DA[5] | DA[6] | DA[0] | DA[1] | DA[2]) { fprintf(stderr, "unexpected A diff in rows 0..6\n"); return 1; }
  if (PLUS6 != 0xE0000000u) { fprintf(stderr, "unexpected PLUS6\n"); return 1; }
  u32 Ex[11], Ey[11];
  for (int i = 7; i <= 10; i++){
    Ex[i] = Ax[i] + Ax[i-4] - S0(Ax[i-1]) - MAJ(Ax[i-1],Ax[i-2],Ax[i-3]);
    Ey[i] = Ay[i] + Ay[i-4] - S0(Ay[i-1]) - MAJ(Ay[i-1],Ay[i-2],Ay[i-3]);
  }
  u32 c6 = Ax[6] - S0(Ax[5]) - MAJ(Ax[5],Ax[4],Ax[3]);
  u32 w10x0 = Ex[10] - Ax[6] - S1(Ex[9]) - CH(Ex[9],Ex[8],Ex[7]) - KK[10];
  u32 w10y0 = Ey[10] - Ay[6] - S1(Ey[9]) - CH(Ey[9],Ey[8],Ey[7]) - KK[10];
  printf("dW10 core %08x (need %08x)\n", w10x0 - w10y0, DW10);
  long cap = 1 << 16, n768 = 0, nl = 0; u32 *list = malloc(cap * sizeof(u32));
  for (uint64_t a = 0; a < (1ull << 32); a++){
    u32 a2 = (u32)a, e6 = c6 + a2;
    if ((e6 & M6) != V6) continue;
    if ((Ex[7] ^ e6) & PLUS7) continue;
    u32 w10x = w10x0 - e6, w10y = w10y0 - e6;
    if (w10x - w10y != DW10 || s0(w10x) - s0(w10y) != DS10) continue;
    n768++;
    if ((Ex[9] - S1(Ex[8]) - CH(Ex[8],Ex[7],e6)) - (Ey[9] - S1(Ey[8]) - CH(Ey[8],Ey[7],e6)) != DW9) continue;
    if (nl == cap){ cap *= 2; list = realloc(list, cap * sizeof(u32)); }
    list[nl++] = a2;
  }
  printf("A2 list (proof 4.2 conditions) %ld; with dW9 %ld\n", n768, nl);
  if (!nl) return 0;
  long NS = (1L << lg) / nl; if (NS < 1) NS = 1;
  long capF = 1 << 20; F = malloc(capF * sizeof(u32)); nF = 0; long tried = 0;
  for (long j = 0; j < nl; j++){
    u32 a2 = list[j], e6 = c6 + a2, top = e6 & 0xE0000000u;
    u32 ka1 = - Ax[5] + S0(Ax[4]) + MAJ(Ax[4],Ax[3],a2);
    u32 k9x = Ex[9] - Ax[5] - S1(Ex[8]) - CH(Ex[8],Ex[7],e6) - KK[9];
    u32 k9y = Ey[9] - Ay[5] - S1(Ey[8]) - CH(Ey[8],Ey[7],e6) - KK[9];
    for (long s = 0; s < NS; s++){
      u32 e5 = top | (rnd() & 0x1FFFFFFFu), a1 = e5 + ka1; tried++;
      u32 w9x = k9x - e5, w9y = k9y - e5;
      if (w9x - w9y != DW9 || s0(w9x) - s0(w9y) != DS9) continue;
      u32 fx = Ex[8] - 2*Ax[4] + S0(Ax[3]) + MAJ(Ax[3],a2,a1) - S1(Ex[7]) - CH(Ex[7],e6,e5) - KK[8];
      u32 fy = Ey[8] - 2*Ay[4] + S0(Ay[3]) + MAJ(Ay[3],a2,a1) - S1(Ey[7]) - CH(Ey[7],e6,e5) - KK[8];
      if (fx - fy != DW8) continue;
      if (nF == capF){ capF *= 2; F = realloc(F, capF * sizeof(u32)); }
      F[nF++] = fx;
    }
  }
  double wgt = (double)(1u << 29) / NS;   // pairs represented by one sample
  printf("samples %ld (NS %ld per A2), A0-free valid hits %ld: N_free ~ 2^%.3f\n", tried, NS, nF, log2(nF * wgt));
  // shuffle F so prefixes are uniform subsamples
  for (long i = nF - 1; i > 0; i--){ long k = ((uint64_t)rnd() << 32 | rnd()) % (i + 1); u32 t = F[i]; F[i] = F[k]; F[k] = t; }
  long own = eval(Ax[0], nF), pub = eval(PUBA[0], nF);
  printf("|R(own A0 %08x)| ~ 2^%.3f (%ld hits); |R(published A0 %08x)| ~ 2^%.3f (%ld hits)\n",
         Ax[0], log2(own * wgt + 1e-9), own, PUBA[0], log2(pub * wgt + 1e-9), pub);
  double avg = 0; for (int r = 0; r < 64; r++) avg += eval(rnd(), nF > 65536 ? 65536 : nF); avg /= 64;
  long nsub = nF > 65536 ? 65536 : nF;
  printf("mean |R(A0)| over 64 random A0 ~ 2^%.3f\n", log2(avg * wgt * nF / nsub + 1e-9));
  long sub = nF > (1 << 17) ? (1 << 17) : nF; u32 besta = 0; long bestv = -1;
  for (int r = 0; r < restarts; r++){
    u32 a0 = rnd(); long v = eval(a0, sub); int imp = 1;
    while (imp){ imp = 0;
      for (int b = 0; b < 32; b++){ u32 c = a0 ^ (1u << b); long w = eval(c, sub); if (w > v){ v = w; a0 = c; imp = 1; } }
      for (int t = 0; t < 64; t++){ u32 c = a0 ^ (1u << (rnd() & 31)) ^ (1u << (rnd() & 31)); long w = eval(c, sub); if (w > v){ v = w; a0 = c; imp = 1; } }
    }
    long full = eval(a0, nF);
    if (full > bestv){ bestv = full; besta = a0; }
  }
  printf("top A0 by hill-climb (%d restarts): %08x |R| ~ 2^%.3f (%ld hits)\n", restarts, besta, log2(bestv * wgt + 1e-9), bestv);
  return 0;
}
