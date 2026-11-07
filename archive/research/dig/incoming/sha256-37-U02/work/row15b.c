// row-15 local scan for chi37 (own code). Enumerates W15x over a mask (base pub) or all 2^32.
// E15y = E15x + dE15 (state rows 11..14 held by the anchor => constant), W15y = W15x + dW15.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
static inline u32 rr(u32 x,int n){return (x>>n)|(x<<(32-n));}
static inline u32 s0f(u32 x){return rr(x,7)^rr(x,18)^(x>>3);}
static inline u32 s1f(u32 x){return rr(x,17)^rr(x,19)^(x>>10);}
static const char *ECELL="=u==01===n=011n01==u0=u=1==+====";
static const char *WCELL="==u=============================";
// bit b <-> string index 31-b
static int ok_sym(char s,int xb,int yb){
  switch(s){case '=':case '+':return xb==yb; case '0':return xb==0&&yb==0; case '1':return xb==1&&yb==1;
   case 'n':return xb==0&&yb==1; case 'u':return xb==1&&yb==0; default:return 1;}}
int main(int argc,char**argv){
  u32 c=0x69d87d38, dE=0xc041ee00, dW=0xe0000000, W0=0x7dd43a81, mask=0xffffffffu;
  if(argc>1) mask=strtoul(argv[1],0,16);
  int nb=0; // enumerate submasks of mask on base W0 with those bits cleared
  u32 base=W0&~mask; u32 sub=0; u64 total=0;
  // counters: [0]=base, [1..32] drop E bit b-1, [33] drop W15[29], [34] drop E bit 4 value (none), 
  u64 cnt[40], cntS[40], cntW[40]; memset(cnt,0,sizeof cnt);memset(cntS,0,sizeof cntS);memset(cntW,0,sizeof cntW);
  u32 wl[32]; int nl=0;
  u32 m0=0,m1=0,mn=0,mu=0,me=0,w_eq=0,w_u=0;
  for(int b=0;b<32;b++){char s=ECELL[31-b]; u32 bit=1u<<b; if(s=='0')m0|=bit; else if(s=='1')m1|=bit; else if(s=='n')mn|=bit; else if(s=='u')mu|=bit; else if(s=='='||s=='+')me|=bit;
    char t=WCELL[31-b]; if(t=='=')w_eq|=bit; else if(t=='u')w_u|=bit;}
  u64 N=(mask==0xffffffffu)?(1ull<<32):0; // full enumeration indexes
  #define DO(wx) { u32 wy=(wx)+dW, ex=(wx)+c, ey=ex+dE; total++;     u32 failE=((ex|ey)&m0)|(~(ex&ey)&m1)|((ex|~ey)&mn)|((~ex|ey)&mu)|((ex^ey)&me);     u32 failW=((wx^wy)&w_eq)|(~(wx&~wy)&w_u);     int pe=__builtin_popcount(failE);     if(pe<=1 && (failW&~(1u<<29))==0){       int sch=-1;       #define SCH() (sch<0?(sch=(((s1f(wy)-s1f(wx))==0xfff80c00u)&&((s0f(wy)-s0f(wx))==0x03c00800u))):sch)       if(failE==0&&failW==0){cnt[0]++; if(SCH())cntS[0]++; if(nl<64) wl[nl++]=wx;}       if(failW==0&&pe==1){int bb=__builtin_ctz(failE); cnt[1+bb]++; if(SCH())cntS[1+bb]++;}       if(failW==0&&pe==0){ for(int bb=0;bb<32;bb++){} }       if(failE==0&&(failW&(1u<<29))){cnt[33]++; if(SCH())cntS[33]++;}       if(failE==0&&failW==0){cnt[33]++; if(SCH())cntS[33]++;}     }     if(pe==0 && failW==0){}   }
  if(mask==0xffffffffu){ u32 x=0; do{ DO(x); x++; }while(x!=0); }
  else { do{ u32 wx=base|sub; DO(wx); sub=(sub-mask)&mask; }while(sub!=0); }
  printf("enumerated %llu\n",(unsigned long long)total);
  printf("BASE rows15 cells (E+W): %llu ; with schedule dW17/dW30 ok: %llu\n",(unsigned long long)cnt[0],(unsigned long long)cntS[0]);
  for(int b=31;b>=0;b--){ char s=ECELL[31-b]; if(s=='?'||s=='=') ; printf("dropE bit %2d sym %c : %llu ; sched %llu\n",b,s,(unsigned long long)cnt[1+b],(unsigned long long)cntS[1+b]);}
  printf("drop W15[29]: %llu ; sched %llu\n",(unsigned long long)cnt[33],(unsigned long long)cntS[33]);
  printf("drop whole W cell: %llu ; sched %llu\n",(unsigned long long)cnt[34],(unsigned long long)cntS[34]);
  if(argc>2){ for(int i=0;i<nl;i++) printf("SOL %08x\n",wl[i]); }
  return 0;}
