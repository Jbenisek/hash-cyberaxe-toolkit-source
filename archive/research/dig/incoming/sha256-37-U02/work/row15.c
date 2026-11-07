// row-15 local scan for chi37 (own code). Enumerates W15x over a mask (base pub) or all 2^32.
// E15y = E15x + dE15 (rows 11..14 held by the anchor => constant), W15y = W15x + dW15.
// levels: L0 = row-15 cells (E+W); L1 = L0 + dW17,dW30 schedule requirements; L2 = L1 + row-16 local requirement
// (X_E16 = dS1(E15)+dCh(E15,E14,E13) = e7affd56 and X_A16 = dMaj(A15,A14,A13) = 0, from rows 12..14 held).
// usage: row15 MASKHEX [print]   (ffffffff = full 2^32)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>
typedef uint32_t u32; typedef uint64_t u64;
static inline u32 rr(u32 x,int n){return (x>>n)|(x<<(32-n));}
static inline u32 s0f(u32 x){return rr(x,7)^rr(x,18)^(x>>3);}
static inline u32 s1f(u32 x){return rr(x,17)^rr(x,19)^(x>>10);}
static inline u32 S1f(u32 x){return rr(x,6)^rr(x,11)^rr(x,25);}
static inline u32 Chf(u32 e,u32 f,u32 g){return (e&f)^(~e&g);}
static inline u32 Majf(u32 a,u32 b,u32 c){return (a&b)^(a&c)^(b&c);}
static const char *ECELL="=u==01===n=011n01==u0=u=1==+====";
static const char *WCELL="==u=============================";
#define KA 0x99480455u
#define E14X 0xc81ed28au
#define E13X 0x66f25d89u
#define E14Y 0xc81eda0au
#define E13Y 0x6eeedd89u
#define A14X 0xd7100429u
#define A13X 0x9992b350u
#define A14Y 0xd5908429u
#define A13Y 0x919033c0u
typedef struct{u64 base[3],one[32][3],w29[3],wall[3];} Cnt;
static void add(u64*a,int lvl){ for(int i=0;i<=lvl;i++) a[i]++; }
int main(int argc,char**argv){
  const u32 c=0x69d87d38, dE=0xc041ee00, dW=0xe0000000, W0=0x7dd43a81;
  u32 mask=strtoul(argv[1],0,16);
  u32 m0=0,m1=0,mn=0,mu=0,me=0,w_eq=0,w_u=0;
  for(int b=0;b<32;b++){char s=ECELL[31-b]; u32 bit=1u<<b; if(s=='0')m0|=bit; else if(s=='1')m1|=bit; else if(s=='n')mn|=bit; else if(s=='u')mu|=bit; else if(s=='='||s=='+')me|=bit;
    char t=WCELL[31-b]; if(t=='=')w_eq|=bit; else if(t=='u')w_u|=bit;}
  u64 N = (mask==0xffffffffu)? (1ull<<32) : (1ull<<__builtin_popcount(mask));
  int nt=omp_get_max_threads(); Cnt *C=calloc(nt,sizeof(Cnt));
  u32 sols[64]; int nsol=0;
  #pragma omp parallel for schedule(static)
  for(long long i=0;i<(long long)N;i++){
    u32 wx; if(mask==0xffffffffu) wx=(u32)i; else { u32 v=0; int k=0; for(int b=0;b<32;b++) if(mask>>b&1){ if((i>>k)&1) v|=1u<<b; k++; } wx=(W0&~mask)|v; }
    u32 wy=wx+dW, ex=wx+c, ey=ex+dE;
    u32 failE=((ex|ey)&m0)|(~(ex&ey)&m1)|((ex|~ey)&mn)|((~ex|ey)&mu)|((ex^ey)&me);
    u32 failW=((wx^wy)&w_eq)|(~(wx&~wy)&w_u);
    int pe=__builtin_popcount(failE); if(pe>1) continue;
    Cnt *c_=&C[omp_get_thread_num()];
    int lvl=0;
    if((s1f(wy)-s1f(wx))==0xfff80c00u && (s0f(wy)-s0f(wx))==0x03c00800u){ lvl=1;
      u32 ax=ex+KA; u32 XE=(S1f(ey)-S1f(ex))+(Chf(ey,E14Y,E13Y)-Chf(ex,E14X,E13X)); u32 XA=Majf(ax,A14Y,A13Y)-Majf(ax,A14X,A13X);
      if(XE==0xe7affd56u && XA==0) lvl=2; }
    if(failE==0){
      add(c_->wall,lvl);
      if((failW&~(1u<<29))==0) add(c_->w29,lvl);
      if(failW==0){ add(c_->base,lvl);
        if(lvl==2){
        #pragma omp critical
        { if(nsol<64) sols[nsol++]=wx; } } }
    } else if(failW==0){ add(c_->one[__builtin_ctz(failE)],lvl); }
  }
  Cnt T; memset(&T,0,sizeof T);
  for(int t=0;t<nt;t++) for(int l=0;l<3;l++){T.base[l]+=C[t].base[l];T.w29[l]+=C[t].w29[l];T.wall[l]+=C[t].wall[l];for(int b=0;b<32;b++)T.one[b][l]+=C[t].one[b][l];}
  #define P(x) (unsigned long long)(x)
  printf("enumerated %llu\n",P(N));
  printf("BASE rows15 cells (E+W): L0 %llu | L1 (+dW17,dW30) %llu | L2 (+row16 local) %llu\n",P(T.base[0]),P(T.base[1]),P(T.base[2]));
  for(int b=31;b>=0;b--){ char s=ECELL[31-b]; if(s=='?')continue; printf("dropE bit %2d sym %c : L0 %llu | L1 %llu | L2 %llu\n",b,s,P(T.base[0]+T.one[b][0]),P(T.base[1]+T.one[b][1]),P(T.base[2]+T.one[b][2]));}
  printf("drop W15[29] cell bit: L0 %llu | L1 %llu | L2 %llu\n",P(T.w29[0]),P(T.w29[1]),P(T.w29[2]));
  printf("drop whole W15 cell: L0 %llu | L1 %llu | L2 %llu\n",P(T.wall[0]),P(T.wall[1]),P(T.wall[2]));
  if(argc>2) for(int i=0;i<nsol;i++) printf("SOL %08x\n",sols[i]);
  return 0;}
