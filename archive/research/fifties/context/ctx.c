// Exact member walk: for each context, all 2^19 class members -> (P=C0.a1, X1, D=D1.d1); distinct counts.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "ctx_gen.h"
#define NM (1u << 19)
typedef unsigned long long u64;
typedef struct { u64 k; u32 z; } T3;
static int c64(const void *a, const void *b){ u64 x=*(const u64*)a, y=*(const u64*)b; return x<y?-1:x>y; }
static int c3(const void *a, const void *b){ const T3 *x=a,*y=b; if(x->k!=y->k) return x->k<y->k?-1:1; return x->z<y->z?-1:x->z>y->z; }
static u32 distinct64(u64 *a, u32 n){ qsort(a,n,8,c64); u32 c=1; for(u32 i=1;i<n;i++) c += a[i]!=a[i-1]; return c; }
int main(void){
  static u32 res[NCTX][7];
  static u32 hist[NM + 1];
  #pragma omp parallel for schedule(dynamic)
  for(int ci=0; ci<NCTX; ci++){
    Ctx C; context_pre(CTXS[ci], &C);
    u32 *P=malloc(NM*4), *X=malloc(NM*4), *D=malloc(NM*4); u64 *a=malloc(NM*8); T3 *t=malloc(NM*sizeof(T3));
    for(u32 m=0;m<NM;m++) member_eval(&C, member_y(m), &P[m], &X[m], &D[m]);
    for(u32 m=0;m<NM;m++) a[m]=P[m]; res[ci][0]=distinct64(a,NM);
    for(u32 m=0;m<NM;m++) a[m]=D[m]; res[ci][1]=distinct64(a,NM);
    for(u32 m=0;m<NM;m++) a[m]=X[m]; res[ci][2]=distinct64(a,NM);
    for(u32 m=0;m<NM;m++) a[m]=((u64)P[m]<<32)|X[m]; res[ci][4]=distinct64(a,NM);
    for(u32 m=0;m<NM;m++) a[m]=((u64)X[m]<<32)|D[m]; res[ci][5]=distinct64(a,NM);
    for(u32 m=0;m<NM;m++) a[m]=((u64)P[m]<<32)|D[m]; res[ci][3]=distinct64(a,NM);
    if(ci==0){ // multiplicity distribution of (P,D) classes (a is sorted)
      u32 run=1; for(u32 i=1;i<=NM;i++){ if(i<NM && a[i]==a[i-1]) run++; else { hist[run]++; run=1; } }
    }
    for(u32 m=0;m<NM;m++){ t[m].k=((u64)P[m]<<32)|D[m]; t[m].z=X[m]; }
    qsort(t,NM,sizeof(T3),c3); u32 c=1; for(u32 i=1;i<NM;i++) c += (t[i].k!=t[i-1].k)||(t[i].z!=t[i-1].z); res[ci][6]=c;
    free(P);free(X);free(D);free(a);free(t);
  }
  // cross-check values (context, member) -> Y4 P X1 D
  int cs[3]={0,1,NCTX-1}; u32 ms[6]={0,1,2,3,12345,NM-1};
  printf("{\"check\":[");
  for(int i=0;i<3;i++) for(int j=0;j<6;j++){ Ctx C; context_pre(CTXS[cs[i]],&C); u32 y=member_y(ms[j]),p,x,d; member_eval(&C,y,&p,&x,&d);
    printf("%s[%d,%u,%u,%u,%u,%u]", (i||j)?",":"", cs[i], ms[j], y, p, x, d); }
  printf("],\n\"cols\":[\"P\",\"D\",\"X1\",\"PD\",\"PX1\",\"X1D\",\"PX1D\"],\n\"per_ctx\":[");
  for(int ci=0;ci<NCTX;ci++){ printf("%s[", ci?",":""); for(int k=0;k<7;k++) printf("%s%u",k?",":"",res[ci][k]); printf("]"); }
  printf("],\n\"hist_PD_ctx0\":{");
  int first=1; for(u32 s=1;s<=NM;s++) if(hist[s]){ printf("%s\"%u\":%u", first?"":",", s, hist[s]); first=0; }
  printf("}}\n");
  return 0;
}
