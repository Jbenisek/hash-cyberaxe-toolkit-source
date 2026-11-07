#include "common.h"
#include <omp.h>
#include <math.h>
#define B(w,i) (((w)>>(i))&1u)
static int inF6(u32 w){ return (s0(w+0x20000000u)-s0(w))==0x03c00800u; } // by definition
static int inF7bit(u32 w){ // bitwise form (equal to the definition on all 2^32 words, see f67g)
  if(!(B(w,1)==B(w,18)&&B(w,0)==B(w,28)&&B(w,9)==B(w,30))) return 0;
  if(B(w,11)==0&&B(w,22)==1&&B(w,26)==1) return 1;
  if(B(w,11)==1&&B(w,12)==0&&B(w,22)==0&&B(w,23)==1&&B(w,26)==0&&B(w,27)==1&&B(w,2)==B(w,19)&&B(w,1)==B(w,29)&&B(w,10)==B(w,31)) return 1;
  return 0; }
typedef struct { u32 c7,a0; } V;
static int cmpv(const void*a,const void*b){u32 x=((V*)a)->c7,y=((V*)b)->c7;return x<y?-1:x>y;}
static u64 rs[2][4];
static inline u64 rotl(u64 x,int k){return (x<<k)|(x>>(64-k));}
static u64 rnd(int t){u64*s=rs[t];u64 r=rotl(s[1]*5,7)*9,tt=s[1]<<17;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=tt;s[3]=rotl(s[3],45);return r;}
static u64 sm(u64*x){u64 z=(*x+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
static double TLIM=900;
int main(int argc,char**argv){ if(argc>2) TLIM=atof(argv[2]);
  long long N = argc>1? atoll(argv[1]) : 100000; // x samples per thread
  omp_set_num_threads(2);
  load_chi("./research/tools/traillab/chi/chi37.txt");
  Tr X; trace(CV,MX,&X);
  u32 A1=AA(&X,1),A2=AA(&X,2),A3=AA(&X,3),A4=AA(&X,4),E5=EE(&X,5),E6=EE(&X,6),E7=EE(&X,7),E8=EE(&X,8);
  u32 C4=A4-S0(A3)-MAJ(A3,A2,A1), W8C=E8-A4-S1(E7)-CH(E7,E6,E5)-K[8], c7c=E7-2*A3+S0(A2)-S1(E6)-K[7], K3C=A3-S0(A2), C6=EE(&X,6)-2*A2+S0(A1)-S1(E5)-K[6];
  V*g=malloc(sizeof(V)*12200000); long long nG=0;
  for(u32 E4=0;E4<(1u<<29);E4++){ u32 w8=W8C-E4;
    if(B(w8,29)&&(B(w8,1)!=B(w8,12))&&(B(w8,8)!=B(w8,25))&&(B(w8,14)==B(w8,18))){ u32 a0=E4-C4; g[nG].a0=a0; g[nG].c7=c7c+MAJ(A2,A1,a0)-CH(E6,E5,E4); nG++; } }
  qsort(g,nG,sizeof(V),cmpv);
  long long ncls=0; static u32 cs[23000],cc[23000]; static u32 cv[23000];
  for(long long i=0;i<nG;){long long j=i;while(j<nG&&g[j].c7==g[i].c7)j++;cs[ncls]=i;cc[ncls]=j-i;cv[ncls]=g[i].c7;ncls++;i=j;}
  printf("G=%lld classes=%lld\n",nG,ncls); fflush(stdout);
  const int NT=5; int th[5]={16,32,40,64,100};
  double S1k[2][5]={{0}},S2k[2][5]={{0}},Sf[2][5]={{0}},Sg[2][5]={{0}},Sgs[2][5]={{0}},Spv[2]={0},Sfib[2][5]={{0}};
  long long cnt[2]={0};
  #pragma omp parallel
  {
    int t=omp_get_thread_num(); u64 sd=0x5CA1AB1E0000ULL+t*7919; for(int k=0;k<4;k++)rs[t][k]=sm(&sd);
    u32*ph=malloc(4*3000000),*tmp=malloc(4*3000000);
    double t0=omp_get_wtime(); for(long long it=0; it<N; it++){ if((it&63)==0 && omp_get_wtime()-t0>TLIM) break;
      u32 x=(u32)rnd(t), cb=(u32)(rnd(t)>>32);
      long long m=0;
      for(long long c=0;c<ncls;c++){ if(!inF7bit(cv[c]-x)) continue;
        for(u32 q=0;q<cc[c];q++){ u32 a0=g[cs[c]+q].a0; u32 E3=K3C-MAJ(A2,A1,a0)+x; ph[m++]=MAJ(A1,a0,x)-CH(E5,a0+C4,E3); } }
      // radix sort 3 x 11 bits
      for(int pass=0;pass<3;pass++){ int sh=pass*11; static __thread unsigned cntb[2048]; memset(cntb,0,sizeof(cntb));
        for(long long i=0;i<m;i++)cntb[(ph[i]>>sh)&2047]++; unsigned s=0; for(int b=0;b<2048;b++){unsigned c2=cntb[b];cntb[b]=s;s+=c2;}
        for(long long i=0;i<m;i++)tmp[cntb[(ph[i]>>sh)&2047]++]=ph[i]; u32*sw=ph;ph=tmp;tmp=sw; }
      double kv[5]={0},kf[5]={0},gp[5]={0};
      for(long long i=0;i<m;){ long long j=i; while(j<m&&ph[j]==ph[i])j++; long long sz=j-i; int pass6 = inF6(cb+ph[i]);
        for(int k=0;k<NT;k++) if(sz>=th[k]){kv[k]+=sz;kf[k]+=1;if(pass6)gp[k]+=sz;} i=j; }
      for(int k=0;k<NT;k++){S1k[t][k]+=kv[k];S2k[t][k]+=kv[k]*kv[k];Sf[t][k]+=kf[k];Sg[t][k]+=gp[k];Sgs[t][k]+=gp[k]*gp[k];}
      Spv[t]+=m; cnt[t]++;
    }
  }
  double n=cnt[0]+cnt[1];
  printf("samples (x, cb): %.0f ; mean variants in passing classes %.0f (exact expectation 192075.0)\n",n,(Spv[0]+Spv[1])/n);
  for(int k=0;k<NT;k++){ double mk=(S1k[0][k]+S1k[1][k])/n, v=(S2k[0][k]+S2k[1][k])/n-mk*mk, se=sqrt(v/n);
    double mg=(Sg[0][k]+Sg[1][k])/n, vg=(Sgs[0][k]+Sgs[1][k])/n-mg*mg;
    double m0=S1k[0][k]/cnt[0], m1=S1k[1][k]/cnt[1];
    printf("THETA %3d: kept fibres %.1f ; kept variants %.0f +- %.0f (1 se; %.2f%%; thread means %.0f %.0f) ; good pairs g (sampled cb) %.0f +- %.0f ; p6*kept = %.0f ; p6*kept/1.006 = %.0f\n",
      th[k],(Sf[0][k]+Sf[1][k])/n,mk,se,100*se/mk,m0,m1,mg,sqrt(vg/n),(287309824.0/4294967296.0)*mk,(287309824.0/4294967296.0)*mk/1.006); }
  for(int k=0;k<NT;k++){ double m1=(Sg[0][k]+Sg[1][k])/n, m2=(Sgs[0][k]+Sgs[1][k])/n; double a1=Sg[0][k]/cnt[0],a2=Sgs[0][k]/cnt[0],b1=Sg[1][k]/cnt[1],b2=Sgs[1][k]/cnt[1];
    double k1=(S1k[0][k]+S1k[1][k])/n,k2=(S2k[0][k]+S2k[1][k])/n;
    printf("SB THETA %3d: n=%.0f E[g]=%.1f E[g^2]/E[g]=%.0f (thread0 %.0f thread1 %.0f) ; E[kept^2]/E[kept]=%.0f\n",th[k],n,m1,m2/m1,a2/a1,b2/b1,k2/k1);}
  return 0;}
