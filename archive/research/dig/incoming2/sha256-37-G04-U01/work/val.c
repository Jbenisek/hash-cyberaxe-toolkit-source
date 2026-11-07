// G04-U01: build pairs from CV words with Lemma 4.1 (own code), check gate dependence, cells rows -4..15, schedule diffs; published a0 and G' (borrow) a0.
#include "common.h"
static u64 rs=0xD1B54A32D192ED03ULL; static inline u32 rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (u32)(rs>>16)^((u32)(rs>>40)<<16);}
static u32 t6=0x03c00800,t7=0x017f8000,d6,d7;
static int inF6(u32 w){return (s0(w+d6)-s0(w))==t6;} static int inF7(u32 w){return (s0(w+d7)-s0(w))==t7;}
// words from CV1 and state rows (Lemma 4.1) for one member; st = state trace of that member from the published pair, a0 replaces A0
static void words(const u32*cv,const Tr*st,u32 a0,u32*W){
  u32 A[18],E[18]; // index i+4
  A[3]=cv[0];A[2]=cv[1];A[1]=cv[2];A[0]=cv[3];E[3]=cv[4];E[2]=cv[5];E[1]=cv[6];E[0]=cv[7];
  for(int i=0;i<=13;i++) A[i+4]=(i==0)?a0:AA(st,i);
  for(int i=0;i<=13;i++){ E[i+4]=A[i+4]+A[i]-S0(A[i+3])-MAJ(A[i+3],A[i+2],A[i+1]);
    W[i]=E[i+4]-A[i]-E[i]-S1(E[i+3])-CH(E[i+3],E[i+2],E[i+1])-K[i]; }
}
static void sched(const u32*m,u32*W){for(int i=0;i<16;i++)W[i]=m[i];for(int i=16;i<25;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];}
int main(){
  load_chi("./research/tools/traillab/chi/chi37.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y); d6=MY[6]-MX[6]; d7=MY[7]-MX[7];
  u32 A1=AA(&X,1),A2=AA(&X,2),A3=AA(&X,3),A4=AA(&X,4),E5=EE(&X,5),E7x=EE(&X,7),E6x=EE(&X,6),E8=EE(&X,8);
  u32 C4=A4-S0(A3)-MAJ(A3,A2,A1), W8C=E8-A4-S1(E7x)-CH(E7x,E6x,E5)-K[8];
  u32 pubA0=AA(&X,0);
  // dependence of (W6x,W7x) on each CV word: perturb one word, see which of W6x,W7x move
  { u32 cv[8],W0[16],W1[16]; for(int i=0;i<8;i++)cv[i]=rnd(); words(cv,&X,pubA0,W0);
    const char*nm[8]={"A_-1","A_-2","A_-3","A_-4","E_-1","E_-2","E_-3","E_-4"};
    for(int k=0;k<8;k++){ int mv6=0,mv7=0,mvlow=0; for(int rep=0;rep<50;rep++){ for(int i=0;i<8;i++)cv[i]=rnd(); words(cv,&X,pubA0,W0); cv[k]^=1u<<(rnd()&31)|1; words(cv,&X,pubA0,W1); mv6|=(W0[6]!=W1[6]); mv7|=(W0[7]!=W1[7]); for(int i=0;i<6;i++) mvlow|=(W0[i]!=W1[i]); }
      printf("perturb %s: W6x moves %d, W7x moves %d, any of W0..W5 moves %d\n",nm[k],mv6,mv7,mvlow); } }
  // pair construction with gate hits; a0 = published, and a0 from G' with W8x[29]=0 (borrow)
  for(int mode=0;mode<2;mode++){
    long long ok=0,tried=0, rowfail[64]={0}; long long gate7=0,gate6=0,schedok=0,w24mod=0,w24cell=0,cellsAB=0;
    for(int it=0;it<3000;it++){
      u32 a0; 
      if(mode==0) a0=pubA0; else { for(;;){ u32 E4=rnd()&0x1fffffff; u32 w8=W8C-E4,w8y=w8+MY[8]-MX[8]; if(((w8>>29)&1)==0 && (s0(w8y)-s0(w8))==(u32)(0-d7)){a0=E4-C4;break;} } }
      u32 cv[8]; for(int i=0;i<8;i++)cv[i]=rnd();
      u32 Wx[16],Wy[16];
      // search A_-1 (cv[0]) with W7x in F7, then A_-2 (cv[1]) with W6x in F6
      for(;;){ cv[0]=rnd(); words(cv,&X,a0,Wx); if(inF7(Wx[7])) break; }
      for(;;){ cv[1]=rnd(); words(cv,&X,a0,Wx); if(inF6(Wx[6])) break; }
      words(cv,&Y,a0,Wy);
      u32 mx[16],my[16]; for(int i=0;i<14;i++){mx[i]=Wx[i];my[i]=Wy[i];} mx[14]=MX[14];mx[15]=MX[15];my[14]=MY[14];my[15]=MY[15];
      Tr P,Q; trace(cv,mx,&P); trace(cv,my,&Q);
      tried++; gate7+=inF7(mx[7]); gate6+=inF6(mx[6]);
      int bad=0; // cells rows -4..15 (A,E,W) excluding row4 E (cell 000 may differ? report), W6/W7/W8 XOR cells
      for(int r=0;r<=15;r++){ if(!wordok(0,r,AA(&P,r),AA(&Q,r))) {rowfail[r+4]++;bad=1;} if(!wordok(1,r,EE(&P,r),EE(&Q,r))) {rowfail[r+4+20]++;bad=1;} }
      cellsAB+= !bad;
      u32 a[25],b[25]; sched(mx,a); sched(my,b);
      int s=1; for(int i=16;i<24;i++){ if(i==22){ if(b[22]-a[22]!=0x017f8000) s=0;} else if(a[i]!=b[i]) s=0; }
      schedok+=s; w24mod+=((b[24]-a[24])==0x20000000);
      int c24=1; for(int bt=0;bt<32;bt++) if(!cellok(sym(2,24,bt),(a[24]>>bt)&1,(b[24]>>bt)&1)) {c24=0;break;}
      w24cell+=c24;
    }
    printf("mode %d (%s): pairs %lld ; W6x in F6 %lld ; W7x in F7 %lld ; A/E cells rows 0..15 all hold %lld ; W16..W23 diffs as pair (W22 = 017f8000, others 0) %lld ; dW24 = 20000000 %lld ; W24 XOR cell holds %lld\n",mode,mode==0?"published a0":"G' borrow a0 (W8x[29]=0)",tried,gate6,gate7,cellsAB,schedok,w24mod,w24cell);
    printf("  A/E row failures (rows 0..15 A then E):"); for(int r=0;r<40;r++) if(rowfail[r]) printf(" %s%d:%lld",r<20?"A":"E",(r%20)-4,rowfail[r]); printf("\n");
  }
  return 0;}
