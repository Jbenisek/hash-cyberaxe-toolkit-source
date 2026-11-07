// U02 Q2: for each coordinate of the C3 pin (a1,d1,c1,b1,W13), hold the other four at the record values and count the
// 2^32 values of that coordinate that keep Fact P (b2 and d2 equal for w4 and w4'); also d2-only and b2-only counts.
#include <stdio.h>
#include <stdint.h>
typedef uint32_t u;
static inline u ror(u x,int n){return (x>>n)|(x<<(32-n));}
static inline u rol(u x,int n){return (x<<n)|(x>>(32-n));}
static u W4=0x97475638u, W4B=0x97475640u;
static inline void c3(u a1,u b1,u c1,u d1,u w13,u w4,u*d2o,u*b2o,u*a2o,u*c2o){
  u X7=rol(b1,12)^c1, X11=c1-d1, X15=rol(d1,16)^a1, X3=a1-X7-W4;
  u A1=X3+X7+w4; u D1=ror(X15^A1,16); u C1=X11+D1; u B1=ror(X7^C1,12);
  u A2=A1+B1+w13; u D2=ror(D1^A2,8); u C2=C1+D2; u B2=ror(B1^C2,7);
  *d2o=D2;*b2o=B2;*a2o=A2;*c2o=C2;}
int main(){
  // record coordinates from the pins
  u X3=0x29d4fa98u,X7=0xbee3af28u,X11=0x44036000u,X15=0x40c58500u,w13=0x0007c006u;
  u a1=X3+X7+W4, d1=ror(X15^a1,16), c1=X11+d1, b1=ror(X7^c1,12);
  u co[5]={a1,d1,c1,b1,w13}; const char*nm[5]={"a1","d1","c1","b1","w13"};
  for(int ax=0;ax<5;ax++){
    unsigned long long both=0,donly=0,bonly=0; u first[8]; int nf=0;
    for(unsigned long long v=0;v<(1ULL<<32);v++){
      u c[5]={co[0],co[1],co[2],co[3],co[4]}; c[ax]=(u)v;
      u d2,b2,a2,c2,d2b,b2b,a2b,c2b;
      c3(c[0],c[3],c[2],c[1],c[4],W4,&d2,&b2,&a2,&c2);
      c3(c[0],c[3],c[2],c[1],c[4],W4B,&d2b,&b2b,&a2b,&c2b);
      int de=d2==d2b, be=b2==b2b;
      if(de&&be){both++; if(nf<8)first[nf++]=(u)v;} else if(de)donly++; else if(be)bonly++;
    }
    printf("%s both=%llu d2only=%llu b2only=%llu first:",nm[ax],both,donly,bonly);
    for(int i=0;i<nf;i++)printf(" %08x",first[i]); printf("\n"); fflush(stdout);
  }
}
