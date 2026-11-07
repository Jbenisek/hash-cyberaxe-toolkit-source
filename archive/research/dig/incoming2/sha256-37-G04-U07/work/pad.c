// own code: padding/W14-W15 scan for sha256-37 (G04-U07). modes: hash <hex128bytes> | pub | scan
#include "common.h"
#include <omp.h>
static const u32 IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
// compress with feed-forward, 37 steps; cv order a..h = A_-1,A_-2,A_-3,A_-4,E_-1..  (trace uses cv[0]=A_-1 ... as in chi file: cv words = a,b,c,d,e,f,g,h)
static void comp37(u32*cv,const u32*m){ Tr t; trace(cv,m,&t); u32 o[8]={AA(&t,36),AA(&t,35),AA(&t,34),AA(&t,33),EE(&t,36),EE(&t,35),EE(&t,34),EE(&t,33)}; for(int k=0;k<8;k++)cv[k]+=o[k]; }
static void step(Tr*t,int i,u32 w){
  u32 a=AA(t,i-1),b=AA(t,i-2),c=AA(t,i-3),d=AA(t,i-4),e=EE(t,i-1),f=EE(t,i-2),g=EE(t,i-3),h=EE(t,i-4);
  u32 T1=h+S1(e)+CH(e,f,g)+K[i]+w; EE(t,i)=d+T1; AA(t,i)=T1+S0(a)+MAJ(a,b,c); t->W[i]=w; }
int main(int argc,char**argv){
  load_chi("./research/tools/traillab/chi/chi37.txt");
  if(argc>2&&!strcmp(argv[1],"hash")){ // hex of 128 bytes
    u32 cv[8]; memcpy(cv,IV,32); u32 m[16]; const char*h=argv[2];
    for(int b=0;b<2;b++){ for(int i=0;i<16;i++){ char s[9]; memcpy(s,h+b*128+i*8,8); s[8]=0; m[i]=strtoul(s,0,16);} comp37(cv,m);} 
    u32 p[16]={0}; p[0]=0x80000000u; p[15]=1024; comp37(cv,p);
    for(int k=0;k<8;k++)printf("%08x",cv[k]); printf("\n"); return 0; }
  if(argc>1&&!strcmp(argv[1],"pub")){
    u32 cx[8],cy[8]; memcpy(cx,CV,32); memcpy(cy,CV,32); comp37(cx,MX); comp37(cy,MY);
    printf("CV2 x:"); for(int k=0;k<8;k++)printf(" %08x",cx[k]); printf("\nCV2 y:"); for(int k=0;k<8;k++)printf(" %08x",cy[k]); printf("\n");
    int eq=!memcmp(cx,cy,32); printf("CV2 equal: %d\n",eq);
    u32 p[16]={0}; p[0]=0x80000000u; p[15]=1024; comp37(cx,p); comp37(cy,p);
    printf("digest x:"); for(int k=0;k<8;k++)printf(" %08x",cx[k]); printf("\ndigest y:"); for(int k=0;k<8;k++)printf(" %08x",cy[k]); printf("\ndigests equal: %d\n",!memcmp(cx,cy,32));
    printf("dW14 = %08x dW15 = %08x (modular y-x); xor %08x %08x\n",MY[14]-MX[14],MY[15]-MX[15],MY[14]^MX[14],MY[15]^MX[15]);
    for(int r=14;r<=15;r++){ int nn=0,nu=0,n0=0,n1=0,neq=0,nplus=0,nq=0; for(int b=0;b<32;b++){char s=sym(2,r,b); if(s=='n')nn++; else if(s=='u')nu++; else if(s=='0')n0++; else if(s=='1')n1++; else if(s=='=')neq++; else if(s=='+')nplus++; else nq++;}
      printf("W%d cells: n=%d u=%d (forced differences) 0=%d 1=%d '='=%d '+'=%d other=%d\n",r,nn,nu,n0,n1,neq,nplus,nq);}
    // padding block as the 3rd block: words
    return 0; }
  if(argc>1&&!strcmp(argv[1],"scan")){ // all W14 with dW14=0 on the published rows<=13: row-14 cells
    Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
    int mode = argc>2?atoi(argv[2]):0; // 0: dW=0 ; 1: dW = published xor pattern (validation, expect 8)
    u32 xm=0; for(int b=0;b<32;b++){char s=sym(2,14,b); if(s=='n'||s=='u')xm|=1u<<b;}
    long long cnt=0, cntA=0; 
    #pragma omp parallel for num_threads(2) reduction(+:cnt,cntA) schedule(static)
    for(long long w=0; w<(1LL<<32); w++){
      Tr x=X,y=Y; u32 wx=(u32)w, wy = mode? wx^xm : wx;
      step(&x,14,wx); step(&y,14,wy);
      if(!wordok(0,14,AA(&x,14),AA(&y,14))) continue; cntA++;
      if(wordok(1,14,EE(&x,14),EE(&y,14))&&wordok(2,14,wx,wy)&&plusok(0,13,AA(&x,13),AA(&x,14))&&plusok(1,13,EE(&x,13),EE(&x,14))&&plusok(2,13,x.W[13],wx)){cnt++; if(mode==0) printf("PASS w14=%08x\n",wx);} }
    printf("mode %d: A14-cell pass %lld ; full row-14 pass %lld of 2^32\n",mode,cntA,cnt); return 0; }
  return 0; }
