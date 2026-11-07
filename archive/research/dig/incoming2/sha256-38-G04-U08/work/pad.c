// own code: padding / W14-W15 scan for sha256-38 (G04-U08). modes: hash <hex256> | pub | scan
#include "common.h"
#include <omp.h>
static const u32 IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static void comp38(u32*cv,const u32*m){ Tr t; trace(cv,m,&t); u32 o[8]={AA(&t,37),AA(&t,36),AA(&t,35),AA(&t,34),EE(&t,37),EE(&t,36),EE(&t,35),EE(&t,34)}; for(int k=0;k<8;k++)cv[k]+=o[k]; }
static void step(Tr*t,int i,u32 w){
  u32 a=AA(t,i-1),b=AA(t,i-2),c=AA(t,i-3),d=AA(t,i-4),e=EE(t,i-1),f=EE(t,i-2),g=EE(t,i-3),h=EE(t,i-4);
  u32 T1=h+S1(e)+CH(e,f,g)+K[i]+w; EE(t,i)=d+T1; AA(t,i)=T1+S0(a)+MAJ(a,b,c); t->W[i]=w; }
static int row14(Tr*x,Tr*y,u32 wx,u32 wy){
  step(x,14,wx); step(y,14,wy);
  if(!wordok(0,14,AA(x,14),AA(y,14))) return 0;
  return wordok(1,14,EE(x,14),EE(y,14))&&wordok(2,14,wx,wy)&&plusok(0,13,AA(x,13),AA(x,14))&&plusok(1,13,EE(x,13),EE(x,14))&&plusok(2,13,x->W[13],wx); }
static int row15(Tr*x,Tr*y,u32 wx,u32 wy){
  step(x,15,wx); step(y,15,wy);
  if(!wordok(0,15,AA(x,15),AA(y,15))) return 0;
  return wordok(1,15,EE(x,15),EE(y,15))&&wordok(2,15,wx,wy)&&plusok(0,14,AA(x,14),AA(x,15))&&plusok(1,14,EE(x,14),EE(x,15))&&plusok(2,14,x->W[14],wx); }
int main(int argc,char**argv){
  load_chi("./research/tools/traillab/chi/chi38.txt");
  if(argc>2&&!strcmp(argv[1],"hash")){
    u32 cv[8]; memcpy(cv,IV,32); u32 m[16]; const char*h=argv[2];
    for(int b=0;b<2;b++){ for(int i=0;i<16;i++){ char s[9]; memcpy(s,h+b*128+i*8,8); s[8]=0; m[i]=strtoul(s,0,16);} comp38(cv,m);}
    u32 p[16]={0}; p[0]=0x80000000u; p[15]=1024; comp38(cv,p);
    for(int k=0;k<8;k++)printf("%08x",cv[k]); printf("\n"); return 0; }
  if(argc>1&&!strcmp(argv[1],"pub")){
    u32 cx[8],cy[8]; memcpy(cx,CV,32); memcpy(cy,CV,32); comp38(cx,MX); comp38(cy,MY);
    printf("CV2 x:"); for(int k=0;k<8;k++)printf(" %08x",cx[k]); printf("\nCV2 y:"); for(int k=0;k<8;k++)printf(" %08x",cy[k]); printf("\n");
    printf("CV2 equal: %d\n",!memcmp(cx,cy,32));
    u32 p[16]={0}; p[0]=0x80000000u; p[15]=1024; comp38(cx,p); comp38(cy,p);
    printf("digests equal after padding block: %d\n",!memcmp(cx,cy,32));
    printf("MX[14]=%08x MY[14]=%08x dW14(xor)=%08x ; MX[15]=%08x MY[15]=%08x dW15(xor)=%08x dW15(mod y-x)=%08x\n",MX[14],MY[14],MX[14]^MY[14],MX[15],MY[15],MX[15]^MY[15],MY[15]-MX[15]);
    for(int r=14;r<=15;r++){ int cnt[128]={0}; for(int b=0;b<32;b++)cnt[(int)sym(2,r,b)]++; printf("W%d cells: n=%d u=%d 0=%d 1=%d '='=%d '+'=%d\n",r,cnt['n'],cnt['u'],cnt['0'],cnt['1'],cnt['='],cnt['+']); }
    return 0; }
  if(argc>1&&!strcmp(argv[1],"scan")){
    // stage 1: all W14 (2^32), row-14 pass, with dW14 = published pattern xm14 (xor)
    Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
    u32 xm14=0,xm15=0; for(int b=0;b<32;b++){char s=sym(2,14,b); if(s=='n'||s=='u')xm14|=1u<<b; s=sym(2,15,b); if(s=='n'||s=='u')xm15|=1u<<b;}
    printf("published-pattern xor masks: W14 %08x W15 %08x\n",xm14,xm15);
    static u32 P14[1<<20]; long long n14=0, nA=0;
    #pragma omp parallel for num_threads(2) reduction(+:nA) schedule(static)
    for(long long w=0; w<(1LL<<32); w++){
      Tr x=X,y=Y; u32 wx=(u32)w, wy=wx^xm14;
      step(&x,14,wx); step(&y,14,wy);
      if(!wordok(0,14,AA(&x,14),AA(&y,14))) continue; nA++;
      if(wordok(1,14,EE(&x,14),EE(&y,14))&&wordok(2,14,wx,wy)&&plusok(0,13,AA(&x,13),AA(&x,14))&&plusok(1,13,EE(&x,13),EE(&x,14))&&plusok(2,13,x.W[13],wx)){
        #pragma omp critical
        { if(n14<(1<<20)) P14[n14]=wx; n14++; } } }
    printf("stage1 (dW14=published pattern xor %08x): A14-cell pass %lld ; full row-14 pass %lld of 2^32\n",xm14,nA,n14);
    int pubfound=0; for(long long k=0;k<n14;k++){ printf("P14 %08x%s\n",P14[k],P14[k]==MX[14]?" (published)":""); if(P14[k]==MX[14])pubfound=1; }
    printf("published W14 among row-14 passers: %d\n",pubfound); fflush(stdout);
    // stage 2: for each row-14 passer, scan all W15 under dW15 = 0 (mode0) and published pattern (mode1)
    for(int mode=0;mode<2;mode++){
      long long tot=0, totA=0, totW16=0;
      for(long long k=0;k<n14;k++){
        Tr xa=X,ya=Y; u32 w14=P14[k]; if(!row14(&xa,&ya,w14,w14^xm14)){printf("BUG\n");}
        long long c=0,cA=0; 
        #pragma omp parallel for num_threads(2) reduction(+:c,cA) schedule(static)
        for(long long w=0; w<(1LL<<32); w++){
          Tr x=xa,y=ya; u32 wx=(u32)w, wy= mode? wx^xm15 : wx;
          step(&x,15,wx); step(&y,15,wy);
          if(!wordok(0,15,AA(&x,15),AA(&y,15))) continue; cA++;
          if(wordok(1,15,EE(&x,15),EE(&y,15))&&wordok(2,15,wx,wy)&&plusok(0,14,AA(&x,14),AA(&x,15))&&plusok(1,14,EE(&x,14),EE(&x,15))&&plusok(2,14,w14,wx)){c++; if(mode==0||wx==MX[15]) {
            #pragma omp critical
            printf("PASS mode%d w14=%08x w15=%08x%s\n",mode,w14,wx,(wx==MX[15]&&w14==MX[14])?" (published)":"");} } }
        tot+=c; totA+=cA; }
      printf("stage2 mode %d (%s): over %lld row-14 passers: A15-cell pass %lld ; full row-15 pass %lld ; (W14,W15) pairs of 2^64\n",mode,mode?"dW15=published pattern":"dW15=0",n14,totA,tot); fflush(stdout); }
    return 0; }

  if(argc>2&&!strcmp(argv[1],"scan2")){ // stage 2 fast: P14 list from file argv[2]
    Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
    u32 xm15=0; for(int b=0;b<32;b++){char s=sym(2,15,b); if(s=='n'||s=='u')xm15|=1u<<b;}
    u32 eq[3]={0},z0[3]={0},o1[3]={0},nm[3]={0},um[3]={0};
    for(int k=0;k<3;k++)for(int b=0;b<32;b++){char s=sym(k,15,b); u32 bit=1u<<b; if(s=='='||s=='+')eq[k]|=bit; else if(s=='0')z0[k]|=bit; else if(s=='1')o1[k]|=bit; else if(s=='n')nm[k]|=bit; else if(s=='u')um[k]|=bit;}
    u32 pl[3]={0}; // plus mask: bits where row15 is '+' and row16 is '+'
    for(int k=0;k<3;k++)for(int b=0;b<32;b++) if(sym(k,14,b)=='+'&&sym(k,15,b)=='+')pl[k]|=1u<<b;
    FILE*f=fopen(argv[2],"r"); char line[256]; static u32 P[4096]; int n=0;
    while(fgets(line,256,f)) if(!strncmp(line,"P14 ",4)) P[n++]=strtoul(line+4,0,16);
    printf("read %d row-14 passers\n",n);
    #define BAD(k,x,y) ((((x)^(y))&eq[k]) | (((x)|(y))&z0[k]) | (~((x)&(y))&o1[k]) | ((x)|~(y))&nm[k] | (~(x)|(y))&um[k])
    for(int mode=0;mode<2;mode++){
      long long tot=0,totA=0; int pubok=0;
      for(int k=0;k<n;k++){
        Tr xa=X,ya=Y; u32 w14=P[k]; row14(&xa,&ya,w14,w14);
        Tr x0=xa,y0=ya; step(&x0,15,0); step(&y0,15,0);
        u32 Ax=AA(&x0,15),Ay=AA(&y0,15),Ex=EE(&x0,15),Ey=EE(&y0,15);
        u32 a14=AA(&xa,14),e14=EE(&xa,14);
        long long c=0,cA=0;
        #pragma omp parallel for num_threads(2) reduction(+:c,cA) schedule(static)
        for(long long w=0; w<(1LL<<32); w++){
          u32 wx=(u32)w, wy= mode? wx^xm15 : wx;
          u32 ax=Ax+wx, ay=Ay+wy; if(BAD(0,ax,ay)) continue; cA++;
          u32 ex=Ex+wx, ey=Ey+wy; if(BAD(1,ex,ey)) continue;
          if(BAD(2,wx,wy)) continue;
          if(((ax^a14)&0)) continue;
          // plus: row14/row15 '+' cells: x-member bits equal between row14 and row15
          if((a14^ax)&pl[0]) continue; if((e14^ex)&pl[1]) continue; if((w14^wx)&pl[2]) continue;
          c++;
          #pragma omp critical
          printf("PASS mode%d w14=%08x w15=%08x%s\n",mode,w14,wx,(wx==MX[15]&&w14==MX[14])?" (published)":"");
          if(wx==MX[15]&&w14==MX[14]) pubok=1;
        }
        tot+=c; totA+=cA; fflush(stdout); }
      printf("stage2 mode %d (%s): %d row-14 passers: A15-cell pass %lld ; full row-15 pass %lld; published pair found %d\n",mode,mode?"dW15=published pattern":"dW15=0",n,totA,tot,pubok); fflush(stdout); }
    return 0; }
  return 0; }
