// Own code (blake3-r3 dig, U55/U56 Q2).  Small-scale analogue of "pin one chain word": the chain state is ONE 32-bit word (digest word 0 fed into m8),
// all other chain words m9..m15 are pinned constants (so the fed-back state is d = 32 bits), while the collision tag is n = 32 + e bits:
// the 32 state bits plus the low e bits of digest word p (p = 4..7 for m12..m15: the word whose feedback is dropped).  A tag collision of two DIFFERENT
// inputs is the goal (a restart is needed when the state itself repeats).  Random-function theory: every state collision (about sqrt(pi 2^32/2)
// evaluations per trajectory) is a full-tag collision with probability 2^-e, so mean cost ~ 2^e * 1.25 * 2^16 against a 3-round BLAKE3 digest or an ideal function.
// usage: pintest e runs rounds p mode(0 = BLAKE3 digest, 1 = ideal splitmix)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
static const uint32_t IV[8] = {0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19};
static const int PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static inline uint32_t ror(uint32_t v, int n){ return (v>>n)|(v<<(32-n)); }
static inline void g(uint32_t*v,int a,int b,int c,int d,uint32_t x,uint32_t y){
  v[a]=v[a]+v[b]+x; v[d]=ror(v[d]^v[a],16); v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],12);
  v[a]=v[a]+v[b]+y; v[d]=ror(v[d]^v[a],8);  v[c]=v[c]+v[d]; v[b]=ror(v[b]^v[c],7); }
static void digest(const uint32_t*msg,int rounds,uint32_t*out){
  uint32_t v[16]; for(int i=0;i<8;i++){v[i]=IV[i];} for(int i=0;i<4;i++) v[8+i]=IV[i]; v[12]=0;v[13]=0;v[14]=64;v[15]=11;
  uint32_t m[16]; memcpy(m,msg,64);
  for(int r=0;r<rounds;r++){
    g(v,0,4,8,12,m[0],m[1]); g(v,1,5,9,13,m[2],m[3]); g(v,2,6,10,14,m[4],m[5]); g(v,3,7,11,15,m[6],m[7]);
    g(v,0,5,10,15,m[8],m[9]); g(v,1,6,11,12,m[10],m[11]); g(v,2,7,8,13,m[12],m[13]); g(v,3,4,9,14,m[14],m[15]);
    uint32_t t[16]; for(int i=0;i<16;i++) t[i]=m[PERM[i]]; memcpy(m,t,64);
  }
  for(int i=0;i<8;i++) out[i]=v[i]^v[i+8];
}
static inline uint64_t smix(uint64_t z){ z+=0x9E3779B97F4A7C15ULL; z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
static uint64_t rs=88172645463325252ULL; static uint64_t rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
int main(int argc,char**argv){
  int e=atoi(argv[1]); int runs=atoi(argv[2]); int rounds=atoi(argv[3]); int p=atoi(argv[4]); int mode=atoi(argv[5]);
  uint32_t K[16]; for(int i=0;i<16;i++) K[i]=0x9E3779B9u*(i+1)^0x7654321u; for(int i=0;i<8;i++) K[i]=0; // m0..m7 = 0 (target prefix)
  typedef struct { uint64_t tag; uint32_t inp; uint32_t stamp; } ent; size_t cap=1<<20; ent*T=calloc(cap,sizeof(ent)); uint32_t gen=0;
  double sum=0,sum2=0; uint64_t traj=0;
  for(int r=0;r<runs;r++){
    uint64_t cnt=0; int ok=0;
    while(!ok){
      gen++; traj++;
      uint32_t s=(uint32_t)rnd(); uint64_t salt=rnd(); K[9]=0x9E3779B9u*10u^0x7654321u^(uint32_t)salt;   // fresh function per trajectory (a pinned constant is re-drawn)
      for(;;){
        uint32_t o[8]; uint32_t msg[16]; memcpy(msg,K,64); msg[8]=s;
        if(mode==0) digest(msg,rounds,o); else for(int i=0;i<8;i++) o[i]=(uint32_t)(smix(smix(((uint64_t)s<<8)^salt)+(uint64_t)i*0x9E3779B97F4A7C15ULL)>>16);
        uint64_t tag=(uint64_t)o[0] | ((uint64_t)(o[p]&((1u<<e)-1))<<32);
        size_t h=(tag*0x9E3779B97F4A7C15ULL)>>20; h&=cap-1; int hit=0;
        while(T[h].stamp==gen){ if(T[h].tag==tag){hit=1;break;} h=(h+1)&(cap-1); }
        cnt++;
        if(hit){ if(T[h].inp!=s) ok=1; break; }
        T[h].stamp=gen; T[h].tag=tag; T[h].inp=s;
        s=o[0];
      }
    }
    sum+=cnt; sum2+=(double)cnt*cnt;
  }
  double mean=sum/runs, sd=sqrt(sum2/runs-mean*mean);
  double base=sqrt(3.14159265358979*pow(2.0,32)/2.0);
  printf("pin analogue e=%d p=%d mode=%d rounds=%d runs=%d mean_evals=%.0f  ratio_to_2^e*sqrt(pi 2^32/2)=%.4f se=%.4f  trajectories_per_run=%.1f\n",
         e,p,mode,rounds,runs,mean,mean/(pow(2.0,e)*base),sd/sqrt(runs)/(pow(2.0,e)*base),(double)traj/runs);
  return 0;
}
