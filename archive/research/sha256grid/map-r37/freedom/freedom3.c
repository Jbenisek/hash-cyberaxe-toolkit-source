/* |G(A1)| (number of valid A0) for each A1 listed on stdin; same checks as freedom2.c countG. */
#include <stdio.h>
#include <stdlib.h>
#include "consts.h"
#define ROR(x,n) (((x) >> (n)) | ((x) << (32 - (n))))
static inline uint32_t S0(uint32_t x){ return ROR(x,2) ^ ROR(x,13) ^ ROR(x,22); }
static inline uint32_t S1(uint32_t x){ return ROR(x,6) ^ ROR(x,11) ^ ROR(x,25); }
static inline uint32_t MAJ(uint32_t x,uint32_t y,uint32_t z){ return (x&y)^(x&z)^(y&z); }
static inline uint32_t CH(uint32_t x,uint32_t y,uint32_t z){ return (x&y)^(~x&z); }
int main(void){ uint32_t E[2][14]; unsigned a1; double tot=0; int n=0;
  for (int m=0;m<2;m++){ const uint32_t *A=m?SAY:SAX; for (int i=4;i<14;i++) E[m][i]=A[i]+A[i-4]-S0(A[i-1])-MAJ(A[i-1],A[i-2],A[i-3]); }
  while (scanf("%x",&a1)==1){ uint32_t e5[2],C4[2],W8C[2]; unsigned long long g=0;
    for (int m=0;m<2;m++){ const uint32_t *A=m?SAY:SAX; e5[m]=A[5]+a1-S0(A[4])-MAJ(A[4],A[3],A[2]);
      C4[m]=A[4]-S0(A[3])-MAJ(A[3],A[2],a1); W8C[m]=E[m][8]-A[4]-S1(E[m][7])-CH(E[m][7],E[m][6],e5[m])-KK[8]; }
    for (unsigned long long vv=0; vv<(1ull<<32); vv++){ uint32_t a0=(uint32_t)vv, ex=a0+C4[0], ey=a0+C4[1];
      if ((ex&EM[4])!=EV[4]||(ex^ey)!=ED[4]) continue; uint32_t wx=W8C[0]-ex, wy=W8C[1]-ey;
      if ((wx&WM[8])!=WV[8]||(wx^wy)!=WD[8]) continue; int ok=1;
      for (int j=0;j<NX2;j++){ uint32_t b1=(wx>>X2B1[j])&1,b2=(wx>>X2B2[j])&1; if((b1==b2)!=X2EQ[j]) ok=0; } g+=ok; }
    printf("A1=%08x |G|=%llu%s\n",a1,g,a1==SAX[1]?"  (published)":""); tot+=g; n++; }
  printf("total joint (A0,A1) variants over %d A1 values: %.0f\n",n,tot); return 0; }
