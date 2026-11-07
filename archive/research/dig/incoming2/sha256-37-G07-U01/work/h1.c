// own code: H1 test. CV1 = IV + F_n(IV, M0) over random 512-bit first blocks M0.
// tests: 256 single bits, 32640 XOR-of-two-bit parities (all CV bit pairs); z = (ones - N/2)/(sqrt(N)/2).
// usage: h1 steps log2N seed [plant]   |   h1 check   (SHA-256("abc") known answer, 64 steps)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
typedef uint32_t u32; typedef uint64_t u64;
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static const u32 K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static const u32 IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static void comp(int steps,const u32*m,u32*out){
  u32 W[64]; for(int i=0;i<16;i++)W[i]=m[i];
  for(int i=16;i<steps;i++){u32 a=W[i-15],b=W[i-2]; W[i]=(ROR(b,17)^ROR(b,19)^(b>>10))+W[i-7]+(ROR(a,7)^ROR(a,18)^(a>>3))+W[i-16];}
  u32 a=IV[0],b=IV[1],c=IV[2],d=IV[3],e=IV[4],f=IV[5],g=IV[6],h=IV[7];
  for(int i=0;i<steps;i++){
    u32 T1=h+(ROR(e,6)^ROR(e,11)^ROR(e,25))+((e&f)^(~e&g))+K[i]+W[i], T2=(ROR(a,2)^ROR(a,13)^ROR(a,22))+((a&b)^(a&c)^(b&c));
    h=g;g=f;f=e;e=d+T1;d=c;c=b;b=a;a=T1+T2; }
  out[0]=IV[0]+a;out[1]=IV[1]+b;out[2]=IV[2]+c;out[3]=IV[3]+d;out[4]=IV[4]+e;out[5]=IV[5]+f;out[6]=IV[6]+g;out[7]=IV[7]+h;
}
static u64 s[4];
static inline u64 rotl(u64 x,int k){return (x<<k)|(x>>(64-k));}
static u64 rnd(void){u64 r=rotl(s[1]*5,7)*9,t=s[1]<<17;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=t;s[3]=rotl(s[3],45);return r;}
static u64 sm(u64*x){u64 z=(*x+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
static u32 pc[256*255/2]; static u32 one[256];
int main(int argc,char**argv){
  if(argc>1&&!strcmp(argv[1],"check")){ u32 m[16]={0x61626380,0,0,0,0,0,0,0,0,0,0,0,0,0,0,24}; u32 o[8]; comp(64,m,o);
    for(int i=0;i<8;i++)printf("%08x",o[i]); printf("\nexpect ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad\n"); return 0; }
  int steps=atoi(argv[1]), lg=atoi(argv[2]); u64 seed=strtoull(argv[3],0,0); int plant=argc>4?atoi(argv[4]):0;
  u64 sd=seed; for(int k=0;k<4;k++)s[k]=sm(&sd);
  u64 N=1ull<<lg, nb=N/64; u64 col[256]; u32 cv[64][8];
  for(u64 bt=0;bt<nb;bt++){
    for(int k=0;k<64;k++){ u32 m[16]; for(int i=0;i<16;i+=2){u64 r=rnd();m[i]=(u32)r;m[i+1]=(u32)(r>>32);} comp(steps,m,cv[k]);
      if(plant && (rnd()&1023)==0){ u32 b17=(cv[k][0]>>17)&1; cv[k][2]=(cv[k][2]&~(1u<<3))|(b17<<3); } }
    for(int w=0;w<8;w++)for(int i=0;i<32;i++){ u64 c=0; for(int k=0;k<64;k++)c|=(u64)((cv[k][w]>>i)&1)<<k; col[w*32+i]=c; one[w*32+i]+=__builtin_popcountll(c); }
    int p=0; for(int i=0;i<256;i++)for(int j=i+1;j<256;j++)pc[p++]+=__builtin_popcountll(col[i]^col[j]);
  }
  double sq=sqrt((double)N)/2, mx1=0,mx2=0,ss1=0,ss2=0,ssx=0; int n2=0,nx=0,i1=0,p1=0; int p=0;
  for(int i=0;i<256;i++){double z=((double)one[i]-N/2.0)/sq; if(fabs(z)>mx1){mx1=fabs(z);i1=i;} ss1+=z*z;}
  int ib=0,jb=0;
  for(int i=0;i<256;i++)for(int j=i+1;j<256;j++,p++){double z=((double)pc[p]-N/2.0)/sq; ss2+=z*z; n2++; if(fabs(z)>mx2){mx2=fabs(z);ib=i;jb=j;}
     if(i<32&&j>=32){ssx+=z*z;nx++;} }
  printf("steps %d N=2^%d seed %llu plant %d\n",steps,lg,(unsigned long long)seed,plant);
  printf("single bits: 256 tests max|z| %.2f (bit %d) mean z^2 %.4f\n",mx1,i1,ss1/256);
  printf("pair parities: %d tests max|z| %.2f (bits %d,%d) mean z^2 %.4f (null 1 +- %.4f)\n",n2,mx2,ib,jb,ss2/n2,sqrt(2.0/n2));
  printf("x=A_-1 (word0) vs the other 7 words: %d tests mean z^2 %.4f (null 1 +- %.4f)\n",nx,ssx/nx,sqrt(2.0/nx));
  // null max |z| over 32896 tests: P(|z|>t)=erfc(t/sqrt2); report t where expected count =1
  double lo=3,hi=8; for(int it=0;it<60;it++){double mid=(lo+hi)/2; if(erfc(mid/sqrt(2.0))*32896>1)lo=mid; else hi=mid;}
  printf("null: expected max|z| over 32896 tests ~ %.2f; P(max>=observed) = %.3g\n",lo,1-pow(1-erfc(((mx1>mx2?mx1:mx2))/sqrt(2.0)),32896));
  return 0;
}
