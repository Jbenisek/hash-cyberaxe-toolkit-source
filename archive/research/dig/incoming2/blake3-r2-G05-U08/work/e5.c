#include <stdio.h>
#include <stdint.h>
typedef uint32_t u;
static inline u ror(u x,int n){return (x>>n)|(x<<(32-n));}
static const u X3=0x29d4fa98,X7=0xbee3af28,X11=0x44036000,X15=0x40c58500,W13=0x0007c006;
static inline void c3(u x,u*b2,u*d2){u a=X3,b=X7,c=X11,d=X15;u a1=a+b+x,d1=ror(d^a1,16),c1=c+d1,b1=ror(b^c1,12);u a2=a1+b1+W13;*d2=ror(d1^a2,8);u c2=c1+*d2;*b2=ror(b1^c2,7);}
int main(){int sh[2]={8,-8};for(int k=0;k<2;k++){unsigned long long cnt=0;u first[6];int nf=0;u s=(u)sh[k];
 for(unsigned long long w=0;w<(1ULL<<32);w++){u b1,d1,b2,d2;c3((u)w,&b1,&d1);c3((u)w+s,&b2,&d2);if(b1==b2&&d1==d2){cnt++;if(nf<6)first[nf++]=(u)w;}}
 printf("shift %+d: w4 with equal (b,d) outputs of 2^32: %llu first:",sh[k],cnt);for(int i=0;i<nf;i++)printf(" %08x",first[i]);printf("\n");fflush(stdout);}
 return 0;}
