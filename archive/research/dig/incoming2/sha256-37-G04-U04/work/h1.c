// own code (U04): H1 audit on real first blocks CV1 = IV + F_37(IV,M0). modes: rand | ctr | w15
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <omp.h>
typedef uint32_t u32; typedef uint64_t u64;
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline u32 S0(u32 x){return ROR(x,2)^ROR(x,13)^ROR(x,22);}
static inline u32 S1(u32 x){return ROR(x,6)^ROR(x,11)^ROR(x,25);}
static inline u32 s0(u32 x){return ROR(x,7)^ROR(x,18)^(x>>3);}
static inline u32 s1(u32 x){return ROR(x,17)^ROR(x,19)^(x>>10);}
static const u32 K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85};
static const u32 IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
#define B(w,i) (((w)>>(i))&1u)
static int inF7(u32 w){
  if(!(B(w,1)==B(w,18)&&B(w,0)==B(w,28)&&B(w,9)==B(w,30))) return 0;
  if(B(w,11)==0&&B(w,22)==1&&B(w,26)==1) return 1;
  if(B(w,11)==1&&B(w,12)==0&&B(w,22)==0&&B(w,23)==1&&B(w,26)==0&&B(w,27)==1&&B(w,2)==B(w,19)&&B(w,1)==B(w,29)&&B(w,10)==B(w,31)) return 1;
  return 0;}
static void f37(const u32*m,u32*cv){
  u32 W[37]; for(int i=0;i<16;i++)W[i]=m[i]; for(int i=16;i<37;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];
  u32 a=IV[0],b=IV[1],c=IV[2],d=IV[3],e=IV[4],f=IV[5],g=IV[6],h=IV[7];
  for(int i=0;i<37;i++){u32 T1=h+S1(e)+((e&f)^(~e&g))+K[i]+W[i],T2=S0(a)+((a&b)^(a&c)^(b&c)); h=g;g=f;f=e;e=d+T1;d=c;c=b;b=a;a=T1+T2;}
  cv[0]=IV[0]+a;cv[1]=IV[1]+b;cv[2]=IV[2]+c;cv[3]=IV[3]+d;cv[4]=IV[4]+e;cv[5]=IV[5]+f;cv[6]=IV[6]+g;cv[7]=IV[7]+h;}
static inline u64 rotl(u64 x,int k){return (x<<k)|(x>>(64-k));}
typedef struct{u64 s[4];}Rng;
static u64 sm(u64*x){u64 z=(*x+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
static void seedr(Rng*r,u64 s){for(int i=0;i<4;i++)r->s[i]=sm(&s);}
static inline u64 nx(Rng*r){u64*s=r->s;u64 res=rotl(s[1]*5,7)*9,t=s[1]<<17;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rotl(s[3],45);return res;}
#define NT 4
#define MH 20   // marginal: top 20 bits and low 20 bits
#define PJ 12   // pair tables 12+12 bits
int main(int argc,char**argv){
  const char*mode=argv[1]; u64 N=1ULL<<atoi(argv[2]); u64 seed=strtoull(argv[3],0,10);
  u32 c7[300]; int nc=0; { FILE*f=fopen("classes.txt","r"); unsigned v; unsigned long long s; while(fscanf(f,"%x %llu",&v,&s)==2) if(s>=3456) c7[nc++]=v; fclose(f);}
  fprintf(stderr,"classes %d\n",nc);
  const u32 C6=0xf538a8f7;
  u32 *mh=calloc((size_t)16<<MH,4); // 8 words x (hi,lo)
  u32 *pj=calloc((size_t)8<<(2*PJ),4); // pairs (x, word k) k=1..7 -> idx 0..6 ; idx 7: (x, cb=C6-y) hi bits  (same as 1 up to bijection; skipped)
  u64 npc[64]={0}; u64 sumpc=0,sumpc2=0,cx7=0;
  u32 fixedm[16]; { Rng r; seedr(&r,seed*7919+1); for(int i=0;i<16;i++)fixedm[i]=(u32)nx(&r); }
  double t0=omp_get_wtime();
  #pragma omp parallel num_threads(NT)
  {
    int tid=omp_get_thread_num(); Rng r; seedr(&r,seed+1000003ULL*(tid+1));
    u32 *lmh=calloc((size_t)16<<MH,4); u32 *lpj=calloc((size_t)7<<(2*PJ),4);
    u64 lnpc[64]={0}; u64 ls=0,ls2=0,lx=0;
    u64 lo=N/NT*tid, hi=N/NT*(tid+1);
    for(u64 i=lo;i<hi;i++){
      u32 m[16], cv[8];
      if(!strcmp(mode,"rand")){ for(int k=0;k<16;k+=2){u64 v=nx(&r);m[k]=(u32)v;m[k+1]=(u32)(v>>32);} }
      else if(!strcmp(mode,"ctr")){ for(int k=0;k<16;k++)m[k]=0; m[0]=(u32)i; m[1]=(u32)(i>>32); }
      else { memcpy(m,fixedm,64); m[15]=(u32)(nx(&r)); }
      f37(m,cv);
      for(int w=0;w<8;w++){ lmh[(size_t)(2*w)<<MH|(cv[w]>>(32-MH))]++; lmh[(size_t)(2*w+1)<<MH|(cv[w]&((1u<<MH)-1))]++; }
      u32 xh=cv[0]>>(32-PJ);
      for(int k=1;k<8;k++) lpj[((size_t)(k-1)<<(2*PJ))|((size_t)xh<<PJ)|(cv[k]>>(32-PJ))]++;
      int pc=0; for(int k=0;k<nc;k++) pc+=inF7(c7[k]-cv[0]);
      lnpc[pc>63?63:pc]++; ls+=pc; ls2+=(u64)pc*pc; lx+=inF7(cv[0]);
    }
    #pragma omp critical
    { for(size_t j=0;j<((size_t)16<<MH);j++)mh[j]+=lmh[j]; for(size_t j=0;j<((size_t)7<<(2*PJ));j++)pj[j]+=lpj[j];
      for(int j=0;j<64;j++)npc[j]+=lnpc[j]; sumpc+=ls; sumpc2+=ls2; cx7+=lx; }
    free(lmh); free(lpj);
  }
  double p7=68157440.0/4294967296.0;
  printf("mode %s N=2^%s seed %llu time %.0fs\n",mode,argv[2],(unsigned long long)seed,omp_get_wtime()-t0);
  double mean=(double)sumpc/N, var=(double)sumpc2/N-mean*mean;
  printf("passing classes (of %d): mean %.5f exact %.5f ; var/mean %.2f ; se(mean, indep-block) %.5f\n",nc,mean,nc*p7,var/mean,sqrt(var/N));
  printf("x in F7 directly: %llu of %llu = %.6e exact p7 %.6e z(binomial) %.2f\n",(unsigned long long)cx7,(unsigned long long)N,(double)cx7/N,p7,((double)cx7-N*p7)/sqrt(N*p7*(1-p7)));
  printf("npc hist:");for(int j=0;j<20;j++)printf(" %llu",(unsigned long long)npc[j]);printf("\n");
  for(int w=0;w<8;w++)for(int h=0;h<2;h++){ double lam=(double)N/(1<<MH),chi=0; u32*t=mh+((size_t)(2*w+h)<<MH);
    for(u32 j=0;j<(1u<<MH);j++){double d=t[j]-lam;chi+=d*d/lam;} double dof=(1<<MH)-1; printf("marg word%d %s20: chi2 %.0f dof %.0f z %.2f\n",w,h?"low":"top",chi,dof,(chi-dof)/sqrt(2*dof)); }
  for(int k=1;k<8;k++){ double cells=(double)(1ULL<<(2*PJ)),lam=N/cells,chi=0; u32*t=pj+((size_t)(k-1)<<(2*PJ));
    for(size_t j=0;j<(1ULL<<(2*PJ));j++){double d=t[j]-lam;chi+=d*d/lam;} double dof=cells-1; printf("pair x12 x word%d top12: chi2 %.0f dof %.0f z %.2f  (excess entropy deficit <= %.3e bit)\n",k,chi,dof,(chi-dof)/sqrt(2*dof),(chi-dof)/(2*(double)N*log(2))); }
  return 0;}
