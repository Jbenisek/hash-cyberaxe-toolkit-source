// Premise check (own code): is x -> trunc_n(BLAKE3-r3 digest of (K || x)) a random-mapping-like iterate?
// Birthday prediction: expected number of evaluations until the first repeated point = sqrt(pi*N/2), N = 2^n.
// Message = 64 bytes: m0..m7 fixed constants, m8..m15 = x embedded (low n bits, rest zero); flags 11, len 64, counter 0.
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
  uint32_t v[16]; for(int i=0;i<8;i++){v[i]=IV[i];} for(int i=0;i<4;i++) v[8+i]=IV[i];
  v[12]=0;v[13]=0;v[14]=64;v[15]=11;
  uint32_t m[16]; memcpy(m,msg,64);
  for(int r=0;r<rounds;r++){
    g(v,0,4,8,12,m[0],m[1]); g(v,1,5,9,13,m[2],m[3]); g(v,2,6,10,14,m[4],m[5]); g(v,3,7,11,15,m[6],m[7]);
    g(v,0,5,10,15,m[8],m[9]); g(v,1,6,11,12,m[10],m[11]); g(v,2,7,8,13,m[12],m[13]); g(v,3,4,9,14,m[14],m[15]);
    uint32_t t[16]; for(int i=0;i<16;i++) t[i]=m[PERM[i]]; memcpy(m,t,64);
  }
  for(int i=0;i<8;i++) out[i]=v[i]^v[i+8];
}
static uint64_t kmsg[16];
static uint64_t f(uint64_t x,int n,int rounds,const uint32_t*fixed){
  uint32_t msg[16]; memcpy(msg,fixed,32); for(int i=8;i<16;i++) msg[i]=0;
  msg[8]=(uint32_t)x; msg[9]=(uint32_t)(x>>32);
  uint32_t o[8]; digest(msg,rounds,o);
  uint64_t y=((uint64_t)o[1]<<32)|o[0];
  if(n<64) y&=((1ULL<<n)-1);
  return y;
}
static uint64_t rs=88172645463325252ULL; static uint64_t rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
int main(int argc,char**argv){
  int n=atoi(argv[1]); int runs=atoi(argv[2]); int rounds=atoi(argv[3]);
  uint32_t fixed[8]; for(int i=0;i<8;i++) fixed[i]=0x9E3779B9u*(i+1)^0x1234567u;
  size_t cap=1; while(cap < (size_t)(8.0*sqrt(3.14159*pow(2.0,n)/2))) cap<<=1;
  uint64_t *tab=(uint64_t*)malloc(cap*8); uint8_t*used=(uint8_t*)malloc(cap);
  double sum=0,sum2=0; double pred=sqrt(3.14159265358979*pow(2.0,n)/2.0);
  int under=0; double q39=0.9943*pow(2.0,n/2.0);
  for(int r=0;r<runs;r++){
    memset(used,0,cap);
    uint64_t x=rnd()&(n<64?((1ULL<<n)-1):~0ULL); uint64_t cnt=0;
    for(;;){
      size_t h=(x*0x9E3779B97F4A7C15ULL)>>20; h&=cap-1; int hit=0;
      while(used[h]){ if(tab[h]==x){hit=1;break;} h=(h+1)&(cap-1); }
      if(hit) break; used[h]=1; tab[h]=x; cnt++;
      x=f(x,n,rounds,fixed);
    }
    sum+=cnt; sum2+=(double)cnt*cnt; if(cnt<=q39) under++;
  }
  double mean=sum/runs, sd=sqrt(sum2/runs-mean*mean);
  printf("n=%d rounds=%d runs=%d mean evals=%.1f  predicted sqrt(pi N/2)=%.1f  ratio=%.4f (se %.4f)  frac(first repeat within 0.9943*sqrt(N))=%.3f (iid prediction 0.390)\n",
         n,rounds,runs,mean,pred,mean/pred,sd/sqrt(runs)/pred,(double)under/runs);
  return 0;
}
