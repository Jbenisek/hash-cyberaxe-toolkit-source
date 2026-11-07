// own code: SHA-256 trace + characteristic parser (chi37.txt). Row index i -> arrays offset +4.
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
typedef uint32_t u32; typedef uint64_t u64;
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline u32 S0(u32 x){return ROR(x,2)^ROR(x,13)^ROR(x,22);}
static inline u32 S1(u32 x){return ROR(x,6)^ROR(x,11)^ROR(x,25);}
static inline u32 s0(u32 x){return ROR(x,7)^ROR(x,18)^(x>>3);}
static inline u32 s1(u32 x){return ROR(x,17)^ROR(x,19)^(x>>10);}
static inline u32 CH(u32 e,u32 f,u32 g){return (e&f)^(~e&g);}
static inline u32 MAJ(u32 a,u32 b,u32 c){return (a&b)^(a&c)^(b&c);}
static const u32 K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
typedef struct { u32 A[46], E[46], W[38]; } Tr; // A[i+4]
static void trace(const u32*cv,const u32*m,Tr*t){
  u32 W[38]; for(int i=0;i<16;i++)W[i]=m[i]; for(int i=16;i<38;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];
  t->A[3]=cv[0];t->A[2]=cv[1];t->A[1]=cv[2];t->A[0]=cv[3];t->E[3]=cv[4];t->E[2]=cv[5];t->E[1]=cv[6];t->E[0]=cv[7];
  for(int i=0;i<38;i++){u32 a=t->A[i+3],b=t->A[i+2],c=t->A[i+1],d=t->A[i],e=t->E[i+3],f=t->E[i+2],g=t->E[i+1],h=t->E[i];
    u32 T1=h+S1(e)+CH(e,f,g)+K[i]+W[i], T2=S0(a)+MAJ(a,b,c); t->E[i+4]=d+T1; t->A[i+4]=T1+T2; t->W[i]=W[i];}
}
#define AA(t,i) ((t)->A[(i)+4])
#define EE(t,i) ((t)->E[(i)+4])
// characteristic
typedef struct { char r[3][40]; int has; } Row;
static Row ROWS[64]; static u32 CV[8],MX[16],MY[16];
static u32 DIG[8]; static char X2[64][80]; static int NX2=0;
static void load_chi(const char*fn){
  FILE*f=fopen(fn,"r"); if(!f){perror(fn);exit(1);} char line[512];
  while(fgets(line,512,f)){
    if(!strncmp(line,"row ",4)){int i;char a[40],e[40],w[40];sscanf(line+4,"%d %s %s %s",&i,a,e,w);strcpy(ROWS[i+4].r[0],a);strcpy(ROWS[i+4].r[1],e);strcpy(ROWS[i+4].r[2],w);ROWS[i+4].has=1;}
    else if(!strncmp(line,"cv ",3)){sscanf(line+3,"%x %x %x %x %x %x %x %x",CV,CV+1,CV+2,CV+3,CV+4,CV+5,CV+6,CV+7);}
    else if(!strncmp(line,"mx ",3)){
      sscanf(line+3,"%x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x",MX,MX+1,MX+2,MX+3,MX+4,MX+5,MX+6,MX+7,MX+8,MX+9,MX+10,MX+11,MX+12,MX+13,MX+14,MX+15);}
    else if(!strncmp(line,"my ",3)){sscanf(line+3,"%x %x %x %x %x %x %x %x %x %x %x %x %x %x %x %x",MY,MY+1,MY+2,MY+3,MY+4,MY+5,MY+6,MY+7,MY+8,MY+9,MY+10,MY+11,MY+12,MY+13,MY+14,MY+15);}
    else if(!strncmp(line,"digest ",7)){sscanf(line+7,"%x %x %x %x %x %x %x %x",DIG,DIG+1,DIG+2,DIG+3,DIG+4,DIG+5,DIG+6,DIG+7);}
    else if(!strncmp(line,"x2 ",3)){char*p=line+3;char*nl=strchr(p,'\n');if(nl)*nl=0;strcpy(X2[NX2++],p);}
  }
  fclose(f);
}
// symbol at (kind 0=A,1=E,2=W; row i; bit b); row absent -> '='
static char sym(int kind,int i,int b){ if(i+4<0||i+4>=64||!ROWS[i+4].has) return '='; return ROWS[i+4].r[kind][31-b]; }
static int cellok(char s,int x,int y){
  switch(s){case '=':case '+':return x==y; case '0':return !x&&!y; case '1':return x&&y; case 'n':return !x&&y; case 'u':return x&&!y; default:return 1;}
}
static int wordok(int kind,int i,u32 x,u32 y){ for(int b=0;b<32;b++) if(!cellok(sym(kind,i,b),(x>>b)&1,(y>>b)&1)) return 0; return 1; }
static int plusok(int kind,int i,u32 p,u32 q){ for(int b=0;b<32;b++) if(sym(kind,i,b)=='+'&&sym(kind,i+1,b)=='+'&&(((p^q)>>b)&1)) return 0; return 1; }
