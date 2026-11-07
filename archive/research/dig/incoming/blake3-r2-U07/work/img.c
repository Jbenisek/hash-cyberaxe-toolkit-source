#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
typedef uint32_t u;
static u rol(u x,int n){return (x<<n)|(x>>(32-n));}
static u xs=88172645u; static u rnd(){xs^=xs<<13;xs^=xs>>17;xs^=xs<<5;return xs*2654435761u+12345u;}
int main(){
 const u X7=0xbee3af28u,W13=0x0007c006u,X3=0x29d4fa98u;
 uint8_t *bm=malloc(1u<<29);
 for(int trial=0;trial<2;trial++){
  u b=rnd(),S7=rnd(),c=rnd();
  u X8=rol(X7,7)^b, D2c1=rol(b,12)^S7, X13=X8-D2c1;
  for(size_t i=0;i<(1u<<29);i++)bm[i]=0;
  uint64_t cnt=0; u a=0;
  do{ u X2=a+b+W13; u d1=rol(X13,8)^X2; u s13=rol(d1,16)^a;
      if(!(bm[s13>>3]&(1<<(s13&7)))){bm[s13>>3]|=1<<(s13&7);cnt++;}
      a++; }while(a!=0);
  printf("S13(D2a1): trial %d image size %llu of 2^32\n",trial,(unsigned long long)cnt);fflush(stdout);
  // S9 over X9
  for(size_t i=0;i<(1u<<29);i++)bm[i]=0; cnt=0; u x9=0;
  do{ u X14=x9-c; u d3=rol(X14,8)^X3; u s9=c-d3;
      if(!(bm[s9>>3]&(1<<(s9&7)))){bm[s9>>3]|=1<<(s9&7);cnt++;}
      x9++; }while(x9!=0);
  printf("S9(X9): trial %d image size %llu of 2^32\n",trial,(unsigned long long)cnt);fflush(stdout);
 }
 return 0;}
