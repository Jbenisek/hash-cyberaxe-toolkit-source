// G04-U01 Q4: alternative gates. E4[31:29]=v != 000 changes d7 (the W7 difference). Exhaustive over all 2^32 E4 (a0=E4-C4 bijective).
#include "common.h"
#include <omp.h>
static u64 rs=0x9E3779B97F4A7C15ULL; static inline u32 rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (u32)(rs>>16);}
int main(int argc,char**argv){
  load_chi("./research/tools/traillab/chi/chi37.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  u32 A1=AA(&X,1),A2=AA(&X,2),A3=AA(&X,3),A4=AA(&X,4),E5=EE(&X,5),E6x=EE(&X,6),E6y=EE(&Y,6),E7x=EE(&X,7),E7y=EE(&Y,7),E8=EE(&X,8);
  if(EE(&Y,5)!=E5||AA(&Y,4)!=A4) {printf("unexpected: members differ at E5/A4\n");}
  u32 C4=A4-S0(A3)-MAJ(A3,A2,A1), W8C=E8-A4-S1(E7x)-CH(E7x,EE(&X,6),E5)-K[8];
  u32 dW8=MY[8]-MX[8]; u32 t7=0x017f8000, d6=MY[6]-MX[6];
  // d7(E4) = dE7 - dS1(E6) - dCH(E6,E5,E4)   (E3, A3, K7 cancel)
  #define D7(E4) ((E7y-E7x)-(S1(E6y)-S1(E6x))-(CH(E6y,E5,(E4))-CH(E6x,E5,(E4))))
  printf("check d7(E4=pair) = %08x vs pair %08x ; C4=%08x W8C=%08x dW8=%08x\n",D7(EE(&X,4)),MY[7]-MX[7],C4,W8C,dW8);
  u64 cnt[8]={0},cntcell[8]={0},cntb29[8]={0}; u32 d7v[8]; for(u32 v=0;v<8;v++) d7v[v]=D7(v<<29);
  for(u32 v=0;v<8;v++) printf("v=%u d7_v=%08x (depends only on v: %s)\n",v,d7v[v],(D7((v<<29)|0x1fffffff)==d7v[v])?"yes":"NO");
  // validated against the printed G' (v=0 modular-only) and G (cell + 3 two-bit conds)
  u64 c0[8]={0},cc[8]={0},cb[8]={0};
  #pragma omp parallel for reduction(+:c0[:8],cc[:8],cb[:8]) schedule(static) num_threads(2)
  for(long long ee=0; ee<(1LL<<32); ee++){ u32 E4=(u32)ee, v=E4>>29; u32 w8=W8C-E4, w8y=w8+dW8;
    int mod=((s0(w8y)-s0(w8))==(u32)(0-d7v[v]));
    c0[v]+=mod;
    if(mod){ cb[v]+=((w8>>29)&1); cc[v]+= wordok(2,8,w8,w8y); }
  }
  printf("v : #E4 with ds0(W8)=-d7_v (modular W23 condition) | of which W8x[29]=1 | of which W8 XOR cell (wordok row 8) holds\n");
  u64 tot=0; for(u32 v=0;v<8;v++){ printf("%u : %llu | %llu | %llu\n",v,(unsigned long long)c0[v],(unsigned long long)cb[v],(unsigned long long)cc[v]); tot+=c0[v]; }
  printf("total over all E4: %llu\n",(unsigned long long)tot);
  // |F7_v|
  for(u32 v=0;v<8;v++){ if(!c0[v]) continue; u64 f=0; u32 dv=d7v[v];
    #pragma omp parallel for reduction(+:f) schedule(static) num_threads(2)
    for(long long ww=0;ww<(1LL<<32);ww++){u32 w=(u32)ww; f+=((s0(w+dv)-s0(w))==t7);}
    printf("|F7_v| for v=%u : %llu (= 2^%.4f of 2^32)\n",v,(unsigned long long)f,__builtin_log2((double)f)); }
  return 0;}
