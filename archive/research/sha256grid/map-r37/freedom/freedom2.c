/* Joint (A0, A1) family on r37.  Step 1: N1 = #A1 (A2, A3 at S) whose own conditions hold: E5 cell, the '+' pair of
   rows 5/6, W9 cell (both members).  Step 2: for a sample of those A1, |G(A1)| = #A0 with E4 cell, W8 cell and the W8
   two-bit conditions (exact count over all 2^32 A0).  k=0 at S's A1 reproduces 12,103,680. */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include "consts.h"
#define ROR(x,n) (((x) >> (n)) | ((x) << (32 - (n))))
static inline uint32_t S0(uint32_t x){ return ROR(x,2) ^ ROR(x,13) ^ ROR(x,22); }
static inline uint32_t S1(uint32_t x){ return ROR(x,6) ^ ROR(x,11) ^ ROR(x,25); }
static inline uint32_t MAJ(uint32_t x,uint32_t y,uint32_t z){ return (x&y)^(x&z)^(y&z); }
static inline uint32_t CH(uint32_t x,uint32_t y,uint32_t z){ return (x&y)^(~x&z); }
static uint32_t E[2][14];
static void base_E(void){ for (int m=0;m<2;m++){ const uint32_t *A = m?SAY:SAX;
  for (int i=4;i<14;i++) E[m][i] = A[i]+A[i-4]-S0(A[i-1])-MAJ(A[i-1],A[i-2],A[i-3]); } }
static int a1_ok(uint32_t a1){
  uint32_t e5[2], w9[2];
  for (int m=0;m<2;m++){ const uint32_t *A = m?SAY:SAX;
    e5[m] = A[5]+a1-S0(A[4])-MAJ(A[4],A[3],A[2]);
    w9[m] = E[m][9]-A[5]-e5[m]-S1(E[m][8])-CH(E[m][8],E[m][7],E[m][6])-KK[9]; }
  if ((e5[0]&EM[5])!=EV[5] || (e5[0]^e5[1])!=ED[5]) return 0;
  uint32_t q = EP[6]&EP[5]; if (q && ((E[0][6]^e5[0])&q)) return 0;
  q = EP[5]&EP[4]; if (q) return -1;                      /* would involve E4 (none expected) */
  if ((w9[0]&WM[9])!=WV[9] || (w9[0]^w9[1])!=WD[9]) return 0;
  return 1; }
static uint64_t countG(uint32_t a1){
  uint32_t e5[2], C4[2], W8C[2]; uint64_t n = 0;
  for (int m=0;m<2;m++){ const uint32_t *A = m?SAY:SAX;
    e5[m] = A[5]+a1-S0(A[4])-MAJ(A[4],A[3],A[2]);
    C4[m] = A[4]-S0(A[3])-MAJ(A[3],A[2],a1);
    W8C[m] = E[m][8]-A[4]-S1(E[m][7])-CH(E[m][7],E[m][6],e5[m])-KK[8]; }
  for (uint64_t vv=0; vv<(1ull<<32); vv++){ uint32_t a0=(uint32_t)vv;
    uint32_t e4x=a0+C4[0], e4y=a0+C4[1];
    if ((e4x&EM[4])!=EV[4] || (e4x^e4y)!=ED[4]) continue;
    uint32_t wx=W8C[0]-e4x, wy=W8C[1]-e4y;
    if ((wx&WM[8])!=WV[8] || (wx^wy)!=WD[8]) continue;
    int ok=1; for (int j=0;j<NX2;j++){ uint32_t b1=(wx>>X2B1[j])&1, b2=(wx>>X2B2[j])&1; if ((b1==b2)!=X2EQ[j]) ok=0; }
    n += ok; }
  return n; }
int main(int argc,char**argv){
  int nsamp = atoi(argv[1]); base_E();
  static uint32_t L[1<<20]; uint64_t n1=0;
  for (uint64_t vv=0; vv<(1ull<<32); vv++){ int r=a1_ok((uint32_t)vv); if (r<0){printf("unexpected + pair\n");return 1;}
    if (r){ if (n1<(1u<<20)) L[n1]=(uint32_t)vv; n1++; } }
  printf("N1 = %llu A1 values pass their own conditions (published A1 %08x)\n",(unsigned long long)n1,SAX[1]);
  printf("|G(A1)| at published A1 = %llu\n",(unsigned long long)countG(SAX[1]));
  double tot=0; uint64_t mn=~0ull,mx=0; int ns = nsamp < (int)n1 ? nsamp : (int)n1;
  for (int s=0;s<ns;s++){ uint32_t a1 = L[(uint64_t)s*n1/ns]; uint64_t g=countG(a1); tot+=g; if(g<mn)mn=g; if(g>mx)mx=g;
    printf("  A1=%08x |G|=%llu\n",a1,(unsigned long long)g); fflush(stdout); }
  if (ns) printf("sample of %d: mean |G| = %.0f, min %llu, max %llu; joint family estimate N1*mean = %.4g (2^%.2f)\n",
     ns, tot/ns,(unsigned long long)mn,(unsigned long long)mx, n1*tot/ns, log2(n1*tot/ns));
  return 0; }
