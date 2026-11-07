// exhaustive scan over all 2^32 x' : count (x',y') in 2^64 with identical G-call outputs (a2,b2,c2,d2) when the initial d differs.
// y' is forced by a2 equality, so the scan is over x' only. Also histogram of D=x'-x over the trivial formula is done in python.
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
typedef uint32_t u;
static inline u ror(u x,int n){return (x>>n)|(x<<(32-n));}
static void G(u A,u B,u C,u D,u x,u y,u*o){u a=A+B+x;u d=ror(D^a,16);u c=C+d;u b=ror(B^c,12);a=a+b+y;d=ror(d^a,8);c=c+d;b=ror(b^c,7);o[0]=a;o[1]=b;o[2]=c;o[3]=d;}
int main(int argc,char**argv){
  u A=strtoul(argv[1],0,16),B=strtoul(argv[2],0,16),C=strtoul(argv[3],0,16);
  u d=strtoul(argv[4],0,10),d2=strtoul(argv[5],0,10);
  u x=strtoul(argv[6],0,16),y=strtoul(argv[7],0,16);
  u o[4];G(A,B,C,d,x,y,o);
  unsigned long long cnt=0; u sx[8],sy[8];
  for(unsigned long long xp=0;xp<(1ULL<<32);xp++){
    u a1=A+B+(u)xp; u dd=ror(d2^a1,16); u c1=C+dd; u b1=ror(B^c1,12);
    u yp=o[0]-a1-b1; u a2=a1+b1+yp; // = o[0]
    u d3=ror(dd^a2,8); if(d3!=o[3])continue;
    u c2=c1+d3; if(c2!=o[2])continue;
    u b2=ror(b1^c2,7); if(b2!=o[1])continue;
    if(cnt<8){sx[cnt]=(u)xp;sy[cnt]=yp;} cnt++;
  }
  printf("A=%08x B=%08x C=%08x d=%u d'=%u x=%08x y=%08x -> solutions (x',y'): %llu\n",A,B,C,d,d2,x,y,cnt);
  for(unsigned long long i=0;i<cnt&&i<8;i++)printf("  x'=%08x y'=%08x\n",sx[i],sy[i]);
  return 0;}
