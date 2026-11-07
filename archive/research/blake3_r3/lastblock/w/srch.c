#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
typedef uint32_t u;
static inline u ror(u x,int k){return (x>>k)|(x<<(32-k));}
static const u IV[8]={0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19};
static const int PERM[16]={2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
#define G(a,b,c,d,x,y) v[a]+=v[b]+x;v[d]=ror(v[d]^v[a],16);v[c]+=v[d];v[b]=ror(v[b]^v[c],12);v[a]+=v[b]+y;v[d]=ror(v[d]^v[a],8);v[c]+=v[d];v[b]=ror(v[b]^v[c],7);
static void cv(const u*m0,u*h){u v[16],m[16],t[16];for(int i=0;i<8;i++)v[i]=IV[i];for(int i=0;i<4;i++)v[8+i]=IV[i];v[12]=0;v[13]=0;v[14]=64;v[15]=1;
for(int i=0;i<16;i++)m[i]=m0[i];
for(int r=0;r<3;r++){G(0,4,8,12,m[0],m[1])G(1,5,9,13,m[2],m[3])G(2,6,10,14,m[4],m[5])G(3,7,11,15,m[6],m[7])
G(0,5,10,15,m[8],m[9])G(1,6,11,12,m[10],m[11])G(2,7,8,13,m[12],m[13])G(3,4,9,14,m[14],m[15])
for(int i=0;i<16;i++)t[i]=m[PERM[i]];for(int i=0;i<16;i++)m[i]=t[i];}
for(int i=0;i<8;i++)h[i]=v[i]^v[i+8];}
static void col(int j,u a,u b,u*A,u*B){u c=IV[j],d=(j==2)?64:(j==3)?10:0;u a1=a+b;u d1=ror(d^a1,16);u c1=c+d1;u b1=ror(b^c1,12);u a2=a1+b1;u d2=ror(d1^a2,8);u c2=c1+d2;u b2=ror(b1^c2,7);*A=a2;*B=b2;}
int main(int argc,char**argv){uint64_t lim=strtoull(argv[1],0,10),st=strtoull(argv[2],0,10);u m[16]={0};
if(argc>3){u mm[16]={0};mm[0]=5;u hh[8];cv(mm,hh);for(int k=0;k<8;k++)printf("%u ",hh[k]);printf("\n");return 0;}
for(uint64_t i=st;i<lim;i++){m[0]=(u)i;m[1]=(u)(i>>32);u h[8];cv(m,h);u A,B,A2,B2;col(1,h[1],h[5],&A,&B);col(2,h[2],h[6],&A2,&B2);
 if((u)(A+B2)==0){printf("HIT i=%llu\n",(unsigned long long)i);fflush(stdout);} }
return 0;}
