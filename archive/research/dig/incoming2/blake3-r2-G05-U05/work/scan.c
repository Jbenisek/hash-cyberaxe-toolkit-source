#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
static inline u32 ror(u32 x,int n){return (x>>n)|(x<<(32-n));}
static inline void G(u32*a,u32*b,u32*c,u32*d,u32 x,u32 y){
 *a=*a+*b+x; *d=ror(*d^*a,16); *c=*c+*d; *b=ror(*b^*c,12);
 *a=*a+*b+y; *d=ror(*d^*a,8);  *c=*c+*d; *b=ror(*b^*c,7);}
static u64 s;
static u32 rnd(){ u64 z=(s+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return (u32)((z^(z>>31))>>16)^(u32)(z>>40)<<16; }
static u32 rnd32(){ return (rnd()&0xFFFF)|(rnd()<<16); }
#define K 0x5bf2cd1du
static inline u32 w4p(u32 w){ return (((w+K)^8u)-K); }
const u32 X3=0x29d4fa98,X7=0xbee3af28,X11=0x44036000,X15=0x40c58500,W4=0x97475638,W13=0x0007c006;
/* C3 pair outputs */
static inline void c3(u32 x3,u32 x7,u32 x11,u32 x15,u32 w4,u32 w13,u32*o){
 u32 a=x3,b=x7,c=x11,d=x15; G(&a,&b,&c,&d,w4,w13); o[0]=a;o[1]=b;o[2]=c;o[3]=d;}
int popc(u32 x){return __builtin_popcount(x);}
int main(int argc,char**argv){
 int mode=atoi(argv[1]); s=strtoull(argv[2],0,10);
 if(mode==0){ /* pin fibres: scan one word of {X3,X7,X11,X15,w13,w4}; E0/E2 digest words */
  u32 X[16],m[16]; for(int i=0;i<16;i++){X[i]=rnd32();m[i]=rnd32();}
  X[3]=X3;X[7]=X7;X[11]=X11;X[15]=X15;m[4]=W4;m[13]=W13;
  const char*nm[6]={"X3","X7","X11","X15","w13","w4"};
  int mask=argc>3?atoi(argv[3]):63; for(int var=0;var<6;var++){ if(!((mask>>var)&1)) continue;
   u64 nY=0,z0=0,z2=0,z5=0,z7=0,z0y=0,all=0,z0z2=0; u32 sol=0;
   for(u64 vv=0;vv<(1ULL<<32);vv++){ u32 v=(u32)vv;
    u32 x3=X[3],x7=X[7],x11=X[11],x15=X[15],w4=m[4],w13=m[13];
    switch(var){case 0:x3=v;break;case 1:x7=v;break;case 2:x11=v;break;case 3:x15=v;break;case 4:w13=v;break;case 5:w4=v;break;}
    u32 w4b=w4p(w4); u32 A[4],B[4]; c3(x3,x7,x11,x15,w4,w13,A); c3(x3,x7,x11,x15,w4b,w13,B);
    int yeq=(A[1]==B[1])&&(A[3]==B[3]);
    /* E0=G(Y0,Y5,Y10,Y15;m1,m11) ; E2=G(Y2,Y7,Y8,Y13;m9,m14) */
    u32 a=X[0],b=X[5],c=X[10],d=A[3]; G(&a,&b,&c,&d,m[1],m[11]); u32 Z0A=a,Z5A=b,Z10A=c,Z15A=d;
    a=X[0];b=X[5];c=X[10];d=B[3]; G(&a,&b,&c,&d,m[1],m[11]); u32 Z0B=a,Z5B=b,Z10B=c,Z15B=d;
    a=X[2];b=A[1];c=X[8];d=X[13]; G(&a,&b,&c,&d,m[9],m[14]); u32 Z2A=a,Z7A=b,Z8A=c,Z13A=d;
    a=X[2];b=B[1];c=X[8];d=X[13]; G(&a,&b,&c,&d,m[9],m[14]); u32 Z2B=a,Z7B=b,Z8B=c,Z13B=d;
    int f0=((Z0A^Z8A)==(Z0B^Z8B)),f2=((Z2A^Z10A)==(Z2B^Z10B)),f5=((Z5A^Z13A)==(Z5B^Z13B)),f7=((Z7A^Z15A)==(Z7B^Z15B));
    nY+=yeq; z0+=f0; z2+=f2; z5+=f5; z7+=f7; all+=(f0&f2&f5&f7); z0z2+=(f0&f2); z0y+=(f0&&!yeq);
    if(yeq&&sol==0) sol=v;
   }
   printf("{\"mode\":0,\"seed\":%llu,\"var\":\"%s\",\"Yeq\":%llu,\"D0zero\":%llu,\"D2zero\":%llu,\"D5zero\":%llu,\"D7zero\":%llu,\"D0zero_notYeq\":%llu,\"D0D2zero\":%llu,\"all4zero\":%llu,\"firstYeq\":%u}\n",(unsigned long long)s,nm[var],(unsigned long long)nY,(unsigned long long)z0,(unsigned long long)z2,(unsigned long long)z5,(unsigned long long)z7,(unsigned long long)z0y,(unsigned long long)z0z2,(unsigned long long)all,sol);
   fflush(stdout);
  }
 } else if(mode==1){ /* residual scans */
  u32 o[4],oB[4]; c3(X3,X7,X11,X15,W4,W13,o); u32 w4b=w4p(W4); c3(X3,X7,X11,X15,w4b,W13,oB);
  u32 Y3A=o[0],Y11A=o[2],Y3B=oB[0],Y11B=oB[2];
  fprintf(stderr,"Y3 %08x %08x Y11 %08x %08x Y7 %08x %08x Y15 %08x %08x\n",Y3A,Y3B,Y11A,Y11B,o[1],oB[1],o[3],oB[3]);
  u32 Y1=rnd32(),Y6=rnd32(),Y12=rnd32(),Y4=rnd32(),Y9=rnd32(),Y14=rnd32(),w12=rnd32(),w8=rnd32(),w5A=rnd32();
  u32 w5B=w5A+W4-w4b;
  const char*nm[9]={"Y1","Y6","Y12","w12","w5","Y4","Y9","Y14","w8"};
  for(int var=0;var<9;var++){
   u64 zero[4]={0,0,0,0}; u64 hist1[33]={0},hist3[33]={0}; u64 both=0;
   /* cache */
   u32 E1A[4],E1B[4],E3A[4],E3B[4];
   #define E1(Y1_,Y6_,Y11_,Y12_,w12_,w5_,out) {u32 a=Y1_,b=Y6_,c=Y11_,d=Y12_; G(&a,&b,&c,&d,w12_,w5_); out[0]=a;out[1]=b;out[2]=c;out[3]=d;}
   #define E3(Y3_,Y4_,Y9_,Y14_,w15_,w8_,out) {u32 a=Y3_,b=Y4_,c=Y9_,d=Y14_; G(&a,&b,&c,&d,w15_,w8_); out[0]=a;out[1]=b;out[2]=c;out[3]=d;}
   E1(Y1,Y6,Y11A,Y12,w12,w5A,E1A) E1(Y1,Y6,Y11B,Y12,w12,w5B,E1B)
   E3(Y3A,Y4,Y9,Y14,0,w8,E3A) E3(Y3B,Y4,Y9,Y14,0,w8,E3B)
   int e1side=(var<5);
   for(u64 vv=0;vv<(1ULL<<32);vv++){ u32 v=(u32)vv;
    if(e1side){ u32 y1=Y1,y6=Y6,y12=Y12,W12=w12,w5a=w5A,w5b=w5B;
     switch(var){case 0:y1=v;break;case 1:y6=v;break;case 2:y12=v;break;case 3:W12=v;break;case 4:w5a=v;w5b=v+W4-w4b;break;}
     E1(y1,y6,Y11A,y12,W12,w5a,E1A) E1(y1,y6,Y11B,y12,W12,w5b,E1B)
    } else { u32 y4=Y4,y9=Y9,y14=Y14,W8=w8;
     switch(var){case 5:y4=v;break;case 6:y9=v;break;case 7:y14=v;break;case 8:W8=v;break;}
     E3(Y3A,y4,y9,y14,0,W8,E3A) E3(Y3B,y4,y9,y14,0,W8,E3B)
    }
    /* digest words: d1=Z1^Z9 (E1.a ^ E3.c), d3=Z3^Z11 (E3.a ^ E1.c), d4=Z4^Z12 (E3.b ^ E1.d), d6=Z6^Z14 (E1.b ^ E3.d) */
    u32 D1=(E1A[0]^E3A[2])^(E1B[0]^E3B[2]);
    u32 D3=(E3A[0]^E1A[2])^(E3B[0]^E1B[2]);
    u32 D4=(E3A[1]^E1A[3])^(E3B[1]^E1B[3]);
    u32 D6=(E1A[1]^E3A[3])^(E1B[1]^E3B[3]);
    zero[0]+=(D1==0);zero[1]+=(D3==0);zero[2]+=(D4==0);zero[3]+=(D6==0); both+=(D1==0&&D3==0);
    hist1[popc(D1)]++; hist3[popc(D3)]++;
   }
   printf("{\"mode\":1,\"seed\":%llu,\"var\":\"%s\",\"D1zero\":%llu,\"D3zero\":%llu,\"D4zero\":%llu,\"D6zero\":%llu,\"D1D3zero\":%llu,\"hist_d1\":[",(unsigned long long)s,nm[var],(unsigned long long)zero[0],(unsigned long long)zero[1],(unsigned long long)zero[2],(unsigned long long)zero[3],(unsigned long long)both);
   for(int i=0;i<=8;i++)printf("%s%llu",i?",":"",(unsigned long long)hist1[i]);
   printf("],\"hist_d3\":[");
   for(int i=0;i<=8;i++)printf("%s%llu",i?",":"",(unsigned long long)hist3[i]);
   printf("]}\n"); fflush(stdout);
  }
 } else if(mode==2){ /* birthday injectivity test of single-word maps */
  u32 a0=rnd32(),b0=rnd32(),c0=rnd32(),d0=rnd32(),mx=rnd32(),my=rnd32();
  const char*nm[4]={"E0.a<-d(Z0<-Y15)","E2.c<-b(Z8<-Y7)","E2.a<-b(Z2<-Y7)","E0.c<-d(Z10<-Y15)"};
  int n=1<<23; u32*o=malloc(4*n);
  for(int t=0;t<4;t++){
   for(int i=0;i<n;i++){ u32 v=rnd32(),a=a0,b=b0,c=c0,d=d0; if(t==0||t==3) d=v; else b=v;
    G(&a,&b,&c,&d,mx,my); o[i]=(t==0||t==2)?a:c; }
   int cmp(const void*x,const void*y){u32 p=*(u32*)x,q=*(u32*)y;return p<q?-1:p>q;}
   qsort(o,n,4,cmp); long coll=0; for(int i=1;i<n;i++) coll+=(o[i]==o[i-1]);
   printf("{\"mode\":2,\"map\":\"%s\",\"samples\":%d,\"output_collisions\":%ld,\"random_function_expect\":%.0f}\n",nm[t],n,coll,(double)n*n/2/4294967296.0); fflush(stdout);
  }
 }
 return 0;}
