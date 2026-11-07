// Own code (blake3-r3 dig).  Tag-collision test on the 256-bit chain x_{i+1} = digest_r(K || x_i) (identity embedding into m8..m15, K = 8 fixed
// words), as in research/blake3_r3/rho_tag.c, but with ONE initial-state word replaced (v[idx] = val).  Reports mean evaluations / sqrt(pi N/2)
// for an n-bit tag, and for every colliding pair found whether the same two inputs also collide in the tag under the STANDARD state.
// usage: tagtest n runs rounds tagword idx val
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
static void digest(const uint32_t*msg,int rounds,const uint32_t*init,uint32_t*out){
  uint32_t v[16]; memcpy(v,init,64);
  uint32_t m[16]; memcpy(m,msg,64);
  for(int r=0;r<rounds;r++){
    g(v,0,4,8,12,m[0],m[1]); g(v,1,5,9,13,m[2],m[3]); g(v,2,6,10,14,m[4],m[5]); g(v,3,7,11,15,m[6],m[7]);
    g(v,0,5,10,15,m[8],m[9]); g(v,1,6,11,12,m[10],m[11]); g(v,2,7,8,13,m[12],m[13]); g(v,3,4,9,14,m[14],m[15]);
    uint32_t t[16]; for(int i=0;i<16;i++) t[i]=m[PERM[i]]; memcpy(m,t,64);
  }
  for(int i=0;i<8;i++) out[i]=v[i]^v[i+8];
}
static uint64_t rs=88172645463325252ULL; static uint64_t rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
int main(int argc,char**argv){
  int n=atoi(argv[1]); int runs=atoi(argv[2]); int rounds=atoi(argv[3]); int w0=atoi(argv[4]); int idx=atoi(argv[5]); uint32_t val=(uint32_t)strtoul(argv[6],0,0);
  uint32_t std[16]; for(int i=0;i<8;i++) std[i]=IV[i]; for(int i=0;i<4;i++) std[8+i]=IV[i]; std[12]=0;std[13]=0;std[14]=64;std[15]=11;
  uint32_t mod[16]; memcpy(mod,std,64); if(idx>=0) mod[idx]=val;
  uint32_t fixed[8]; for(int i=0;i<8;i++) fixed[i]=0x9E3779B9u*(i+1)^0x1234567u;
  size_t cap=1; while(cap < (size_t)(8.0*sqrt(3.14159*pow(2.0,n)/2))) cap<<=1;
  uint64_t *tab=(uint64_t*)malloc(cap*8); uint8_t*used=(uint8_t*)malloc(cap); uint32_t *inp=(uint32_t*)malloc(cap*32);
  double sum=0,sum2=0; double pred=sqrt(3.14159265358979*pow(2.0,n)/2.0); int pairs=0, alsostd=0;
  for(int r=0;r<runs;r++){
    memset(used,0,cap);
    uint32_t msg[16]; memcpy(msg,fixed,32); for(int i=8;i<16;i++) msg[i]=(uint32_t)rnd();
    uint64_t cnt=0;
    for(;;){
      uint32_t o[8]; digest(msg,rounds,mod,o);
      uint64_t tag=((uint64_t)o[(w0+1)&7]<<32)|o[w0&7]; if(n<64) tag&=((1ULL<<n)-1);
      size_t h=(tag*0x9E3779B97F4A7C15ULL)>>20; h&=cap-1; int hit=0;
      while(used[h]){ if(tab[h]==tag){hit=1;break;} h=(h+1)&(cap-1); }
      cnt++;
      if(hit){
        if(memcmp(&inp[h*8],msg+8,32)!=0){ // distinct inputs, equal modified-state tag
          uint32_t m2[16],a[8],b[8]; memcpy(m2,fixed,32); memcpy(m2+8,&inp[h*8],32); digest(m2,rounds,std,a);
          memcpy(m2+8,msg+8,32); digest(m2,rounds,std,b);
          uint64_t ta=((uint64_t)a[(w0+1)&7]<<32)|a[w0&7], tb=((uint64_t)b[(w0+1)&7]<<32)|b[w0&7];
          if(n<64){ ta&=((1ULL<<n)-1); tb&=((1ULL<<n)-1); }
          pairs++; if(ta==tb) alsostd++;
        }
        break; }
      used[h]=1; tab[h]=tag; memcpy(&inp[h*8],msg+8,32);
      for(int i=0;i<8;i++) msg[8+i]=o[i];
    }
    sum+=cnt; sum2+=(double)cnt*cnt;
  }
  double mean=sum/runs, sd=sqrt(sum2/runs-mean*mean);
  printf("tag n=%d word=%d rounds=%d runs=%d idx=%d val=0x%08x mean=%.1f pred=%.1f ratio=%.4f se=%.4f pairs=%d also_collide_under_standard_state=%d\n",
         n,w0,rounds,runs,idx,val,mean,pred,mean/pred,sd/sqrt(runs)/pred,pairs,alsostd);
  return 0;
}
