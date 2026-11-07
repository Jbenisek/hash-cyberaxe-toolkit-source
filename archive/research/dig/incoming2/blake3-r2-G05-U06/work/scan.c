#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <time.h>
typedef uint32_t u32; typedef uint64_t u64;
static inline u32 ror(u32 x,int n){return (x>>n)|(x<<(32-n));}
static inline void G(u32*a,u32*b,u32*c,u32*d,u32 x,u32 y){
 *a=*a+*b+x;*d=ror(*d^*a,16);*c+=*d;*b=ror(*b^*c,12);
 *a=*a+*b+y;*d=ror(*d^*a,8);*c+=*d;*b=ror(*b^*c,7);}
static u64 s[2]={0x9E3779B97F4A7C15ULL,0xD1B54A32D192ED03ULL};
static u64 rnd(){u64 s1=s[0],s0=s[1];s[0]=s0;s1^=s1<<23;s[1]=s1^s0^(s1>>18)^(s0>>5);return s[1]+s0;}
static u32 r32(){return (u32)(rnd()>>16);}
/* E: inputs a,b,c,d ; returns out in o[0..3]=a,b,c,d */
static inline void E(u32 a,u32 b,u32 c,u32 d,u32 x,u32 y,u32*o){G(&a,&b,&c,&d,x,y);o[0]=a;o[1]=b;o[2]=c;o[3]=d;}
static time_t T0; static int LIMIT=2100;
static int timeup(){return (int)(time(0)-T0)>LIMIT;}
int main(int argc,char**argv){
 u64 seed=argc>1?strtoull(argv[1],0,10):1; s[0]^=seed*0x2545F4914F6CDD1DULL; for(int i=0;i<20;i++)rnd();
 T0=time(0);
 const u32 X3=0x29d4fa98,X7=0xbee3af28,X11=0x44036000,X15=0x40c58500,W4=0x97475638,W13=0x0007c006;
 const u32 Y7=0x76f7aefd,Y15=0xbbfbdffe,Y3A=0x8127c181,Y3B=0x7edf3e7e,Y11A=0x7af77f38,Y11B=0x850000c3;
 /* ---- T0 known answer: C3 pair ---- */
 {u32 o[4],p[4]; E(X3,X7,X11,X15,W4,W13,o);E(X3,X7,X11,X15,W4+8,W13,p);
  printf("T0 C3 A %08x %08x %08x %08x B %08x %08x %08x %08x\n",o[0],o[1],o[2],o[3],p[0],p[1],p[2],p[3]);
  if(o[0]!=Y3A||o[1]!=Y7||o[2]!=Y11A||o[3]!=Y15||p[0]!=Y3B||p[1]!=Y7||p[2]!=Y11B||p[3]!=Y15){printf("KNOWN ANSWER FAIL\n");return 1;}}
 /* ---- T1: pin multiplicity, scan X3 and X11 (others pinned) ---- */
 for(int which=0;which<2;which++){
  u64 nb=0,nd=0,nboth=0; u32 firstboth=0; int nfound=0;
  for(u64 x=0;x<(1ULL<<32);x++){
   u32 a=which==0?(u32)x:X3, c=which==1?(u32)x:X11; u32 o[4],p[4];
   E(a,X7,c,X15,W4,W13,o);E(a,X7,c,X15,W4+8,W13,p);
   int b=(o[1]==p[1]), d=(o[3]==p[3]); nb+=b; nd+=d; if(b&&d){nboth++;}
  }
  printf("T1 scan %s (others pinned): #(Y7 equal)=%llu #(Y15 equal)=%llu #(both)=%llu\n",which?"X11":"X3",(unsigned long long)nb,(unsigned long long)nd,(unsigned long long)nboth);fflush(stdout);
  if(timeup())return 0;
 }
 /* ---- T2: relaxation of pins, E0/E2 scans ---- */
 for(int inst=0;inst<2;inst++){
  u32 Y0=r32(),Y5=r32(),Y10=r32(),Y2=r32(),Y8=r32(),Y13=r32(),w1=r32(),w11=r32(),w9=r32(),w14=r32();
  u32 o[4]; 
  /* scan Y7' (E2 b input): d5 equality needs Z13 same; d7 needs Z7 same (E0 fixed) */
  E(Y2,Y7,Y8,Y13,w9,w14,o); u32 Z7=o[1],Z13=o[3];
  u64 n13=0,n7=0,nb=0;
  for(u64 x=0;x<(1ULL<<32);x++){u32 q[4];E(Y2,(u32)x,Y8,Y13,w9,w14,q);int e13=q[3]==Z13,e7=q[1]==Z7;n13+=e13;n7+=e7;nb+=(e13&&e7);}
  printf("T2.%d scan Y7' (E2 b-in, E0 fixed): #(d5 eq: Z13 same)=%llu #(d7 eq: Z7 same)=%llu #(both)=%llu\n",inst,(unsigned long long)n13,(unsigned long long)n7,(unsigned long long)nb);fflush(stdout);
  if(timeup())return 0;
  E(Y0,Y5,Y10,Y15,w1,w11,o); u32 Z5=o[1],Z15=o[3];
  u64 n5=0,n15=0; nb=0;
  for(u64 x=0;x<(1ULL<<32);x++){u32 q[4];E(Y0,Y5,Y10,(u32)x,w1,w11,q);int e5=q[1]==Z5,e15=q[3]==Z15;n5+=e5;n15+=e15;nb+=(e5&&e15);}
  printf("T2.%d scan Y15' (E0 d-in, E2 fixed): #(d5 eq: Z5 same)=%llu #(d7 eq: Z15 same)=%llu #(both)=%llu\n",inst,(unsigned long long)n5,(unsigned long long)n15,(unsigned long long)nb);fflush(stdout);
  if(timeup())return 0;
 }
 /* ---- T3: d4 / d6 ---- */
 for(int inst=0;inst<3;inst++){
  u32 Y1=r32(),Y4=r32(),Y6=r32(),Y9=r32(),Y12=r32(),Y14=r32(),w12=r32(),w5=r32(),w8=r32(),w15=0;
  u32 e1A[4],e1B[4],e3A[4],e3B[4];
  E(Y1,Y6,Y11A,Y12,w12,w5,e1A);E(Y1,Y6,Y11B,Y12,w12,w5-8,e1B);
  /* A side: E1 out: a=Z1,b=Z6,c=Z11,d=Z12 ; E3 out: a=Z3,b=Z4,c=Z9,d=Z14 */
  u32 t4=e1A[3]^e1B[3], t6=e1A[1]^e1B[1];
  u64 n4=0,n6=0,nb=0,a4=0,a6=0;
  for(u64 x=0;x<(1ULL<<32);x++){u32 p[4],q[4];
   E(Y3A,(u32)x,Y9,Y14,w15,w8,p);E(Y3B,(u32)x,Y9,Y14,w15,w8,q);
   u32 d4=p[1]^q[1], d6=p[3]^q[3];
   int h4=d4==t4,h6=d6==t6; n4+=h4;n6+=h6;nb+=(h4&&h6);a4+=(d4==0);a6+=(d6==0);}
  printf("T3.%d scan Y4 (E3 b-in; E1 side fixed, true pair): #(d4 eq)=%llu #(d6 eq)=%llu #(both)=%llu | E3-alone: #(dZ4=0)=%llu #(dZ14=0)=%llu\n",inst,(unsigned long long)n4,(unsigned long long)n6,(unsigned long long)nb,(unsigned long long)a4,(unsigned long long)a6);fflush(stdout);
  if(timeup())return 0;
  E(Y3A,Y4,Y9,Y14,w15,w8,e3A);E(Y3B,Y4,Y9,Y14,w15,w8,e3B);
  u32 s4=e3A[1]^e3B[1], s6=e3A[3]^e3B[3];
  n4=n6=nb=a4=a6=0;
  for(u64 x=0;x<(1ULL<<32);x++){u32 p[4],q[4];
   E(Y1,Y6,Y11A,(u32)x,w12,w5,p);E(Y1,Y6,Y11B,(u32)x,w12,w5-8,q);
   u32 d4=p[3]^q[3], d6=p[1]^q[1];
   int h4=d4==s4,h6=d6==s6; n4+=h4;n6+=h6;nb+=(h4&&h6);a4+=(d4==0);a6+=(d6==0);}
  printf("T3.%d scan Y12 (E1 d-in; E3 side fixed, true pair): #(d4 eq)=%llu #(d6 eq)=%llu #(both)=%llu | E1-alone: #(dZ12=0)=%llu #(dZ6=0)=%llu\n",inst,(unsigned long long)n4,(unsigned long long)n6,(unsigned long long)nb,(unsigned long long)a4,(unsigned long long)a6);fflush(stdout);
  if(timeup())return 0;
 }
 printf("DONE %ld s\n",(long)(time(0)-T0));
 return 0;}
