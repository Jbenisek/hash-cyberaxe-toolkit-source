// Test: for fixed (b,f,h), is z -> y(b,h,z,f) a permutation of 2^32? (explains p_land = 2^-rho exactly)
// Also tests fixed (b,h,z): f -> y, and fixed (b,z,f): h -> y (known non-permutation).
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint32_t u32;
static u32 rol(u32 x,int r){r&=31;return r?(x<<r)|(x>>(32-r)):x;}
static u32 ror(u32 x,int r){return rol(x,32-(r&31));}
#define IV3 0xa54ff53au
#define IV7 0x5be0cd19u
static u32 X7c=0xbee3af28u,X11c=0x44036000u,W13c=0x0007c006u;
static u32 yf(u32 b,u32 h,u32 z,u32 f,u32 dflag){
  u32 X8=rol(X7c,7)^b,S7=X8^rol(b,12);
  u32 a1=IV3+IV7+f,d1=ror(a1^dflag,16),c1=IV3+d1,b1=ror(IV7^c1,12),S11=rol(S7,7)^b1;
  u32 K=X11c-S11,Y0=(rol(h,16)^K)+z+f,Y12=ror(Y0^h,8);
  return ror((Y12+X8+h)^z,7);
}
int main(int argc,char**argv){
  int mode=atoi(argv[1]); unsigned seed=atoi(argv[2]); srand(seed);
  u32 b=(argc>3?0x80000000u:0)-W13c;
  u32 r1=((u32)rand()<<16)^rand(), r2=((u32)rand()<<16)^rand();
  uint8_t *bm=calloc(1u<<29,1); unsigned long long coll=0, in13=0;
  for(unsigned long long x=0;x<(1ull<<32);x++){
    u32 y = mode==0? yf(b,r1,(u32)x,r2,11) : mode==1? yf(b,r1,r2,(u32)x,11) : yf(b,(u32)x,r1,r2,11);
    if(bm[y>>3]&(1<<(y&7))) coll++; else bm[y>>3]|=1<<(y&7);
    in13 += (((0x8127c181u+y)&0x03cf8303u)==0x030c0303u);
  }
  printf("mode=%d (0:z free,1:f free,2:h free) seed=%u collisions=%llu inC13=%llu (2^19=%u)\n",mode,seed,coll,in13,1u<<19);
  return 0;
}
