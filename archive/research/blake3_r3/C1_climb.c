// C1: stochastic hill-climb on (m,m') minimising Hamming distance of 256-bit digests, CV pair fixed with k differing words.
// usage: C1_climb rounds cvdiffmask evals seed
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
static const int PERM[16]={2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u32 IV[4]={0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A};
static u64 s[2];
static inline u64 rnd(){u64 a=s[0],b=s[1];s[0]=b;a^=a<<23;s[1]=a^b^(a>>17)^(b>>26);return s[1]+b;}
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
#define G(a,b,c,d,mx,my) do{v[a]+=v[b]+(mx);v[d]=ROR(v[d]^v[a],16);v[c]+=v[d];v[b]=ROR(v[b]^v[c],12);v[a]+=v[b]+(my);v[d]=ROR(v[d]^v[a],8);v[c]+=v[d];v[b]=ROR(v[b]^v[c],7);}while(0)
static void comp(const u32*cv,const u32*m0,int rounds,u32*h){
  u32 v[16],m[16],t[16];memcpy(m,m0,64);
  for(int i=0;i<8;i++)v[i]=cv[i];for(int i=0;i<4;i++)v[8+i]=IV[i];v[12]=0;v[13]=0;v[14]=64;v[15]=10;
  for(int r=0;r<rounds;r++){
    G(0,4,8,12,m[0],m[1]);G(1,5,9,13,m[2],m[3]);G(2,6,10,14,m[4],m[5]);G(3,7,11,15,m[6],m[7]);
    G(0,5,10,15,m[8],m[9]);G(1,6,11,12,m[10],m[11]);G(2,7,8,13,m[12],m[13]);G(3,4,9,14,m[14],m[15]);
    for(int i=0;i<16;i++)t[i]=m[PERM[i]];memcpy(m,t,64);}
  for(int i=0;i<8;i++)h[i]=v[i]^v[i+8];
}
static int dist(const u32*cv,const u32*cv2,const u32*ma,const u32*mb,int rounds){
  u32 h1[8],h2[8];comp(cv,ma,rounds,h1);comp(cv2,mb,rounds,h2);int d=0;for(int i=0;i<8;i++)d+=__builtin_popcount(h1[i]^h2[i]);return d;}
int main(int argc,char**argv){
  int rounds=atoi(argv[1]);unsigned mask=strtoul(argv[2],0,0);u64 evals=strtoull(argv[3],0,0);s[0]=atoll(argv[4])*0x9E3779B97F4A7C15ULL+1;s[1]=0xD1B54A32D192ED03ULL;
  u32 cv[8],cv2[8];for(int i=0;i<8;i++){cv[i]=rnd();cv2[i]=((mask>>i)&1)?(u32)rnd():cv[i];}
  int gbest=999;u64 used=0;int restarts=0;long hist[300]={0};
  u32 M[32];
  while(used<evals){
    for(int i=0;i<32;i++)M[i]=rnd();
    int cur=dist(cv,cv2,M,M+16,rounds);used++;int stall=0;
    while(stall<20000&&used<evals){
      u32 old[32];memcpy(old,M,128);
      int w=rnd()%32;int typ=rnd()%3;
      if(typ==0)M[w]^=1u<<(rnd()%32);else if(typ==1)M[w]+=(rnd()&1?1:-1)*(1u<<(rnd()%32));else M[w]=rnd();
      int d=dist(cv,cv2,M,M+16,rounds);used++;
      if(d<=cur){if(d<cur)stall=0;else stall++;cur=d;}else{memcpy(M,old,128);stall++;}
    }
    restarts++;hist[cur]++;if(cur<gbest)gbest=cur;
  }
  printf("rounds=%d mask=0x%x evals=%llu restarts=%d best_bitdiff=%d  (random mean 128, min over 1e8 draws ~82)\n",rounds,mask,(unsigned long long)used,restarts,gbest);
  int lo=0;for(int i=0;i<300;i++)if(hist[i]){printf(" restart-min hist: %d:%ld",i,hist[i]);if(++lo>6)break;}printf("\n");
}
