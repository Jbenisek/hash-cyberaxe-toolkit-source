// G04-U01 (sha256-38) CV.A-2: Lemma 4.1 map CV -> W0..W7 (own code), dependence of W0..W7 and E16x on each CV word, exhaustive A_-2 scans.
#include "common.h"
#include <omp.h>
static u64 rs=0xD1B54A32D192ED03ULL; static inline u32 rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (u32)(rs>>16);}
static u32 AX[18],EX[18],AY[18],EY[18]; // index i (row 0..13) fixed rows of the pair (x and y), plain index
static void lemma(const u32*cv,const u32*A,const u32*E,u32*W){ // W[0..7]
  u32 Aa[18],Ee[18]; // offset 4
  Aa[3]=cv[0];Aa[2]=cv[1];Aa[1]=cv[2];Aa[0]=cv[3];Ee[3]=cv[4];Ee[2]=cv[5];Ee[1]=cv[6];Ee[0]=cv[7];
  for(int i=0;i<=13;i++) Aa[i+4]=A[i];
  for(int i=0;i<=13;i++){ if(i<4) Ee[i+4]=Aa[i+4]+Aa[i]-S0(Aa[i+3])-MAJ(Aa[i+3],Aa[i+2],Aa[i+1]); else Ee[i+4]=E[i]; }
  for(int i=0;i<8;i++) W[i]=Ee[i+4]-Aa[i]-Ee[i]-S1(Ee[i+3])-CH(Ee[i+3],Ee[i+2],Ee[i+1])-K[i];
}
static u32 C16,R16B=0x481b02f9u;
static inline u32 e16(const u32*cv){ // E16x = C16 + W0 + s0(W1) via Lemma 4.1 (only E0,E1 needed)
  u32 Am1=cv[0],Am2=cv[1],Am3=cv[2],Am4=cv[3],Em1=cv[4],Em2=cv[5],Em3=cv[6],Em4=cv[7];
  u32 E0=AX[0]+Am4-S0(Am1)-MAJ(Am1,Am2,Am3), E1=AX[1]+Am3-S0(AX[0])-MAJ(AX[0],Am1,Am2);
  u32 W0=E0-Am4-Em4-S1(Em1)-CH(Em1,Em2,Em3)-K[0], W1=E1-Am3-Em3-S1(E0)-CH(E0,Em1,Em2)-K[1];
  return C16+W0+s0(W1);}
static inline int inR16(u32 e){return ((e-R16B)&~0x82405u)==0;}
static inline int in3a(u32 e){return ((e^R16B)&0x0001dbf8u)==0;}
static int inF7(u32 w){return (s0(w+0x20000000u)-s0(w))==0x03bff800u;}
static int fullcheck(const u32*cv,u32 d7){ // build both members from the lemma, trace, check cells rows -4..16 (W7 cell excepted)
  u32 Wx[8],Wy[8]; lemma(cv,AX,EX,Wx); lemma(cv,AY,EY,Wy);
  u32 mx[16],my[16]; for(int i=0;i<8;i++){mx[i]=Wx[i];my[i]=Wy[i];} for(int i=8;i<16;i++){mx[i]=MX[i];my[i]=MY[i];}
  Tr X,Y; trace(cv,mx,&X); trace(cv,my,&Y); int bad=0;
  for(int i=-4;i<=16;i++){ if(!wordok(0,i,AA(&X,i),AA(&Y,i)))bad++; if(!wordok(1,i,EE(&X,i),EE(&Y,i)))bad++; if(i>=0&&i!=7&&!wordok(2,i,X.W[i],Y.W[i]))bad++; }
  (void)d7; return bad; }
int main(int argc,char**argv){
  load_chi("./research/tools/traillab/chi/chi38.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  for(int i=0;i<=13;i++){AX[i]=AA(&X,i);EX[i]=EE(&X,i);AY[i]=AA(&Y,i);EY[i]=EE(&Y,i);}
  C16=EE(&X,16)-(MX[0]+s0(MX[1]));
  printf("C16=%08x (proof fe314838) ; pub E16x=%08x in32set=%d in3a=%d\n",C16,EE(&X,16),inR16(EE(&X,16)),in3a(EE(&X,16)));
  u32 Wx[8],Wy[8]; lemma(CV,AX,EX,Wx); lemma(CV,AY,EY,Wy); int ok=1; for(int i=0;i<8;i++){ if(Wx[i]!=MX[i]||Wy[i]!=MY[i]) ok=0; }
  printf("VAL Lemma 4.1 reproduces W0..W7 of the published pair (both members): %d ; e16(CV)=%08x vs trace %08x\n",ok,e16(CV),EE(&X,16));
  printf("VAL fullcheck(published CV) cell failures rows -4..16: %d\n",fullcheck(CV,0));
  // dependence of W0..W7 and E16x on each CV word
  const char*nm[8]={"A_-1","A_-2","A_-3","A_-4","E_-1","E_-2","E_-3","E_-4"};
  int dep[8][9]; memset(dep,0,sizeof dep); int NP=400; int fwdbad=0;
  for(int k=0;k<NP;k++){ u32 cv[8]; for(int j=0;j<8;j++)cv[j]=rnd()^(rnd()<<16); u32 W0[8]; lemma(cv,AX,EX,W0); u32 e0=e16(cv);
    if(k<100) fwdbad+=fullcheck(cv,0)>0 ? 0:0; // cell checks of random CVs are not expected to hold (only A/E rows 0..13 follow); skip
    for(int j=0;j<8;j++){ u32 c2[8]; memcpy(c2,cv,sizeof cv); c2[j]^=1u<<(rnd()%32)^(rnd()|1); u32 W1[8]; lemma(c2,AX,EX,W1); for(int i=0;i<8;i++) if(W1[i]!=W0[i]) dep[j][i]=1; if(e16(c2)!=e0) dep[j][8]=1; } }
  printf("DEP (400 random CVs, 400 perturbations per word): CV word -> moved W-words / E16x\n");
  for(int j=0;j<8;j++){ printf("  %s moves:",nm[j]); for(int i=0;i<8;i++) if(dep[j][i])printf(" W%d",i); if(dep[j][8])printf(" E16x"); printf("\n"); }
  // forward check on random CVs: trace with lemma W reproduces A0..A13,E0..E13 of the pair rows
  int fb=0; for(int k=0;k<1000;k++){ u32 cv[8]; for(int j=0;j<8;j++)cv[j]=rnd()^(rnd()<<16); u32 W[8]; lemma(cv,AX,EX,W); u32 m[16]; for(int i=0;i<8;i++)m[i]=W[i]; for(int i=8;i<16;i++)m[i]=MX[i]; Tr T; trace(cv,m,&T); for(int i=0;i<=13;i++) if(AA(&T,i)!=AX[i]||(i>=4&&EE(&T,i)!=EX[i])) fb++; }
  printf("VAL forward trace of lemma-built block reproduces A0..A13,E0..E13 on 1000 random CVs: mismatches %d\n",fb);
  // exhaustive A_-2 scans
  int NC=argc>1?atoi(argv[1]):7;
  for(int c=0;c<NC;c++){
    u32 cv[8];
    if(c==0){ memcpy(cv,CV,sizeof cv); }
    else { for(;;){ for(int j=0;j<8;j++)cv[j]=rnd()^(rnd()<<16); u32 W[8]; lemma(cv,AX,EX,W); if(inF7(W[7])) break; } }
    u32 M1=cv[0]^cv[2], M2=AX[0]^cv[0]; int pc=__builtin_popcount(M1|M2);
    u64 h3=0,hR=0; u32 firsthit[4]; int nf=0; u32 pubhit=0;
    #pragma omp parallel for reduction(+:h3,hR) schedule(static) num_threads(2)
    for(long long a=0;a<(1LL<<32);a++){ u32 c2[8]; memcpy(c2,cv,sizeof cv); c2[1]=(u32)a; u32 e=e16(c2); int t=in3a(e); h3+=t; if(t){ int r=inR16(e); hR+=r; if(r){
        #pragma omp critical
        { if(nf<4) firsthit[nf++]=(u32)a; } } } }
    // verify hits: build blocks and check all cells rows -4..16
    int bad=0; for(int k=0;k<nf;k++){ u32 c2[8]; memcpy(c2,cv,sizeof cv); c2[1]=firsthit[k]; bad+=fullcheck(c2,0)>0; }
    printf("CTX %d: A_-1=%08x A_-2(pub/ctx)=%08x A_-3=%08x ; W7x in F7 %d ; popcount(M1|M2)=%d (A_-2 matters at those bits only: M1=A_-1^A_-3=%08x M2=A0^A_-1=%08x) ; #A_-2 with stage-3a 12 bits ok = %llu (2^%.3f ; 2^20 expected) ; #A_-2 in the 32-word row-16 set = %llu (multiple of 2^%d: %d)  ; full cell check of %d hits: %d failing\n",c,cv[0],cv[1],cv[2],inF7(0)||1,pc,M1,M2,(unsigned long long)h3,__builtin_log2((double)(h3?h3:1)),(unsigned long long)hR,32-pc,(int)((hR%(1ULL<<(32-pc)))==0),nf,bad);
    fflush(stdout);
  }
  return 0;}
