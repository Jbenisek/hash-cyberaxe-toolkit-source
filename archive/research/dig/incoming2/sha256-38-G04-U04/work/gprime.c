#include <stdio.h>
#include <stdint.h>
static inline uint32_t ror(uint32_t x,int n){return (x>>n)|(x<<(32-n));}
static inline uint32_t s0(uint32_t x){return ror(x,7)^ror(x,18)^(x>>3);}
int main(int argc,char**argv){
  uint32_t m=MM,v=VV,df=DF,D8=DD,T=0xfe7f8000u;
  uint64_t nG=0,nGp=0,nboth=0; FILE*f=fopen("gprime_minus_G.bin","wb");
  for(uint64_t i=0;i<(1ull<<32);i++){uint32_t w=(uint32_t)i,y=w+D8;
    int g=((w&m)==v)&&((w^y)==df)&&(((w^(w>>28))&1))&&(((w>>30)^(w>>9))&1)&&(!(((w>>1)^(w>>18))&1));
    int gp=((s0(y)-s0(w))==T);
    nG+=g;nGp+=gp;nboth+=g&gp; if(gp&&!g)fwrite(&w,4,1,f);}
  fclose(f);
  printf("G=%llu Gprime=%llu G_and_Gprime=%llu Gprime_minus_G=%llu\n",nG,nGp,nboth,nGp-nboth);return 0;}
