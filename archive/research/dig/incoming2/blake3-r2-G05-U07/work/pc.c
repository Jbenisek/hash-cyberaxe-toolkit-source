#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
static const u32 IV[4]={0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A};
static const u32 IVF[8]={0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19};
static const int PI[16]={2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline void G(u32*v,int a,int b,int c,int d,u32 mx,u32 my){
 v[a]+=v[b]+mx; v[d]=ROR(v[d]^v[a],16); v[c]+=v[d]; v[b]=ROR(v[b]^v[c],12);
 v[a]+=v[b]+my; v[d]=ROR(v[d]^v[a],8); v[c]+=v[d]; v[b]=ROR(v[b]^v[c],7);}
static void comp(const u32*m0,u32 tl,u32 th,u32 b,u32 d,int rounds,u32*out){
 u32 v[16],m[16],t[16]; memcpy(m,m0,64);
 for(int i=0;i<8;i++)v[i]=IVF[i]; for(int i=0;i<4;i++)v[8+i]=IV[i]; v[12]=tl;v[13]=th;v[14]=b;v[15]=d;
 for(int r=0;r<rounds;r++){
  G(v,0,4,8,12,m[0],m[1]);G(v,1,5,9,13,m[2],m[3]);G(v,2,6,10,14,m[4],m[5]);G(v,3,7,11,15,m[6],m[7]);
  G(v,0,5,10,15,m[8],m[9]);G(v,1,6,11,12,m[10],m[11]);G(v,2,7,8,13,m[12],m[13]);G(v,3,4,9,14,m[14],m[15]);
  for(int i=0;i<16;i++)t[i]=m[PI[i]]; memcpy(m,t,64);}
 for(int i=0;i<8;i++)out[i]=v[i]^v[i+8];}
static u64 sm; static inline u64 rnd(){u64 z=(sm+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
static int cmp(const void*a,const void*b){u64 x=*(u64*)a,y=*(u64*)b;return x<y?-1:x>y;}
int main(int argc,char**argv){
 int lg=atoi(argv[1]); int mode=atoi(argv[2]); sm=atoll(argv[3]); int rounds=argc>4?atoi(argv[4]):2;
 u64 N=1ULL<<lg;
 const char*names[5]={"w0,w2,w5.lo8 (E0/E2 half)","w1,w3,w4.lo8 (E1/E3 half)","w0,w1,w2.lo8","w6,w7,w5.lo8","control rng"};
 u64*K[5]; for(int k=0;k<5;k++)K[k]=malloc(N*8);
 u32 m[16],o[8];
 for(u64 i=0;i<N;i++){
  for(int j=0;j<16;j++)m[j]=(u32)rnd();
  u32 tl=0,th=0,b=64,d=1;
  if(mode==1){b=55;d=11;m[13]&=0x00ffffff;m[14]=0;m[15]=0;}
  comp(m,tl,th,b,d,rounds,o);
  const u64 M8=0xff;
  K[0][i]=((u64)o[0]<<8)|(o[2]&0xff); // 40 bits: w0 + low8 of w2
  K[1][i]=((u64)o[1]<<8)|(o[3]&0xff);
  K[2][i]=((u64)o[0]<<8)|(o[1]&0xff);
  K[3][i]=((u64)o[6]<<8)|(o[7]&0xff);
  K[4][i]=rnd()&0xffffffffffULL;
 }
 double exp=(double)N*(double)(N-1)/2.0/1099511627776.0;
 printf("mode %d rounds %d N=2^%d expected pairs at 40 bits %.1f (sd %.1f)\n",mode,rounds,lg,exp,__builtin_sqrt(exp));
 for(int k=0;k<5;k++){
  qsort(K[k],N,8,cmp); double pairs=0; u64 i=0;
  while(i<N){u64 j=i+1; while(j<N&&K[k][j]==K[k][i])j++; double r=j-i; pairs+=r*(r-1)/2; i=j;}
  printf("  key %-28s pairs %.0f  ratio %.4f  z %.2f\n",names[k],pairs,pairs/exp,(pairs-exp)/__builtin_sqrt(exp));
 }
 return 0;}
