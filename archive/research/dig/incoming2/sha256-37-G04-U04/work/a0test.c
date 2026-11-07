// own code (U04): Lemma 4.1 bijection and necessity of the G conditions, full two-member trace check of rows -4..13
#include "common.h"
#define B(w,i) (((w)>>(i))&1u)
static u64 st[4]; static u64 rotl(u64 x,int k){return (x<<k)|(x>>(64-k));}
static u64 nx(void){u64 res=rotl(st[1]*5,7)*9,t=st[1]<<17;st[2]^=st[0];st[3]^=st[1];st[1]^=st[2];st[0]^=st[3];st[2]^=t;st[3]=rotl(st[3],45);return res;}
static int inF6(u32 w){u32 common=(B(w,14)^B(w,18))|(1^(B(w,8)^B(w,25)))|(B(w,1)^B(w,12));u32 bc=(B(w,15)^B(w,19))|(1^(B(w,9)^B(w,26)))|(B(w,2)^B(w,13));u32 X=(B(w,16)^B(w,20)^B(w,31))|(1^(B(w,10)^B(w,27)^B(w,31)))|(B(w,3)^B(w,14)^B(w,31));return !(common|(B(w,29)&(bc|(B(w,30)&X))));}
static int inF7(u32 w){if(!(B(w,1)==B(w,18)&&B(w,0)==B(w,28)&&B(w,9)==B(w,30)))return 0;if(B(w,11)==0&&B(w,22)==1&&B(w,26)==1)return 1;if(B(w,11)==1&&B(w,12)==0&&B(w,22)==0&&B(w,23)==1&&B(w,26)==0&&B(w,27)==1&&B(w,2)==B(w,19)&&B(w,1)==B(w,29)&&B(w,10)==B(w,31))return 1;return 0;}
static Tr Xp,Yp; static u32 C4,W8C,c7c,C6,K3C,d6,t6,d7,dS8;
static int nx2; static char xna[64],xnb[64],xop[64]; static int xia[64],xba[64],xib[64],xbb[64];
// build member from cv and a0 using member template T (published rows); returns W0..W13 by Lemma 4.1 definition and the trace
static void build(const u32*cv,u32 a0,const Tr*T,Tr*out){
  u32 A[18],E[18],W[16]; // index i+4
  for(int k=0;k<4;k++){A[3-k]=cv[k];E[3-k]=cv[4+k];} // A[3]=A_-1 ...
  A[4]=a0; for(int i=1;i<=13;i++)A[i+4]=T->A[i+4];
  for(int i=4;i<=13;i++)E[i+4]=T->E[i+4];
  // E_i = A_i + A_{i-4} - S0(A_{i-1}) - MAJ(A_{i-1},A_{i-2},A_{i-3}) for i=0..3 (E_i also for i>=4 equals T's by Lemma 4.2; E4 depends on a0 : recompute)
  for(int i=0;i<=4;i++){ E[i+4]=A[i+4]+A[i]-S0(A[i+3])-MAJ(A[i+3],A[i+2],A[i+1]); }
  for(int i=0;i<=13;i++){ W[i]=E[i+4]-A[i]-E[i]-S1(E[i+3])-CH(E[i+3],E[i+2],E[i+1])-K[i]; }
  W[14]=T->W[14]; W[15]=T->W[15];
  trace(cv,W,out);
}
static int cell_rows(const Tr*x,const Tr*y,int*firstbad){
  for(int i=-4;i<=13;i++){ if(!wordok(0,i,AA(x,i),AA(y,i))){*firstbad=i;return 1;} if(!wordok(1,i,EE(x,i),EE(y,i))){*firstbad=i;return 2;} }
  for(int i=0;i<=13;i++){ if(i==6||i==7) continue; if(!wordok(2,i,x->W[i],y->W[i])){*firstbad=i;return 3;} }
  *firstbad=-9; return 0; }
static int twobit(const Tr*x){ for(int k=0;k<nx2;k++){ u32 va,vb; if(xia[k]>13||xib[k]>13) continue;
    u32 a=xna[k]=='A'?AA(x,xia[k]):xna[k]=='E'?EE(x,xia[k]):x->W[xia[k]]; u32 b=xnb[k]=='A'?AA(x,xib[k]):xnb[k]=='E'?EE(x,xib[k]):x->W[xib[k]];
    int eq=((a>>xba[k])&1)==((b>>xbb[k])&1); if(eq!=(xop[k]=='=')) return 1; (void)va;(void)vb;} return 0; }
static u32 rnd32(void){return (u32)nx();}
static u32 pickF(int w){ for(;;){u32 v=rnd32(); if(w==7?inF7(v):inF6(v)) return v;} }
int main(int argc,char**argv){
  long NS=atol(argv[1]); st[0]=0x1234abcd;st[1]=0x9e3779b9;st[2]=0xdeadbeef;st[3]=0x31415926;
  load_chi("../../../../tools/traillab/chi/chi37.txt"); trace(CV,MX,&Xp); trace(CV,MY,&Yp);
  u32 A1=AA(&Xp,1),A2=AA(&Xp,2),A3=AA(&Xp,3),A4=AA(&Xp,4),E5=EE(&Xp,5),E6=EE(&Xp,6),E7=EE(&Xp,7),E8=EE(&Xp,8);
  C4=A4-S0(A3)-MAJ(A3,A2,A1); W8C=E8-A4-S1(E7)-CH(E7,E6,E5)-K[8]; c7c=E7-2*A3+S0(A2)-S1(E6)-K[7];
  C6=E6-2*A2+S0(A1)-S1(E5)-K[6]; K3C=A3-S0(A2); d6=Yp.W[6]-Xp.W[6]; d7=Yp.W[7]-Xp.W[7]; dS8=s0(Yp.W[8])-s0(Xp.W[8]); u32 dW8=Yp.W[8]-Xp.W[8];
  printf("derived C4 %08x W8C %08x c7c %08x C6 %08x K3C %08x d6 %08x d7 %08x dS0(W8) %08x\n",C4,W8C,c7c,C6,K3C,d6,d7,dS8);
  for(int k=0;k<NX2;k++){char op[4];int ia,ba,ib,bb;char na,nb; sscanf(X2[k],"%c%d[%d] %2s %c%d[%d]",&na,&ia,&ba,op,&nb,&ib,&bb); xna[nx2]=na;xnb[nx2]=nb;xop[nx2]=op[0]=='='?'=':'!';xia[nx2]=ia;xba[nx2]=ba;xib[nx2]=ib;xbb[nx2]=bb;nx2++;}
  // sanity: the published pair through build() with its own cv and a0
  { Tr x,y; build(CV,AA(&Xp,0),&Xp,&x); build(CV,AA(&Xp,0),&Yp,&y); int fb; int r=cell_rows(&x,&y,&fb); int same=1; for(int i=0;i<=13;i++) if(AA(&x,i)!=AA(&Xp,i)||EE(&x,i)!=EE(&Xp,i)||x.W[i]!=Xp.W[i]) same=0;
    printf("published pair via Lemma 4.1 rebuild: cells %s (r=%d), x W0..W13 equal published: %d, twobit viol %d\n",r?"FAIL":"ok",r,same,twobit(&x)); }
  if(argc>2){ // H1 Q2 identity: gate depends on (A_-1, A_-2) only; other six CV words feed only W0..W5
    long mism=0,mw05=0,same_after=0,n=0; u32 gs[2000]; int ng=0; { FILE*f=fopen("gset.bin","rb"); u32 p[2]; while(ng<2000&&fread(p,4,2,f)==2){ if(nx()%6000==0) gs[ng++]=p[1]; } fclose(f);} 
    long N2=atol(argv[2]); long gate=0,gate2=0;
    for(long t=0;t<N2;t++){ u32 a0=gs[nx()%ng]; u32 cv[8],cw[8]; for(int k=0;k<8;k++)cv[k]=rnd32();
      for(int k=0;k<8;k++)cw[k]=cv[k]; for(int k=2;k<8;k++)cw[k]=rnd32(); // same x, A_-2, other six re-randomised
      Tr tx,tw; build(cv,a0,&Xp,&tx); build(cw,a0,&Xp,&tw);
      u32 E4=a0+C4; u32 w7f=c7c+MAJ(A2,A1,a0)-CH(E6,E5,E4)-cv[0]; u32 E3=K3C-MAJ(A2,A1,a0)+cv[0]; u32 w6f=C6-cv[1]+MAJ(A1,a0,cv[0])-CH(E5,a0+C4,E3);
      if(tx.W[7]!=w7f||tx.W[6]!=w6f||tw.W[7]!=w7f||tw.W[6]!=w6f) mism++;
      int g1=inF7(tx.W[7])&&inF6(tx.W[6]), g2=inF7(tw.W[7])&&inF6(tw.W[6]); gate+=g1; gate2+=g2; if(g1!=g2) same_after++;
      int d=0; for(int i=0;i<=5;i++) if(tx.W[i]!=tw.W[i]) d=1; mw05+=d; n++; }
    printf("H1-Q2 identity over %ld random (CV1,a0 in G): W6x,W7x != formula(x,A_-2) : %ld ; gate indicator changed when the other 6 CV words are re-drawn: %ld ; W0..W5 changed by that re-draw: %ld of %ld ; gate hits %ld/%ld",N2,mism,same_after,mw05,n,gate,gate2);putchar(10);
    return 0; }
  const char*nm[6]={"valid a0 in G","drop E4[31:29]=000","drop W8x[29]=1","drop W8x[1]!=W8x[12]","drop W8x[8]!=W8x[25]","drop W8x[14]=W8x[18]"};
  for(int mode=0;mode<6;mode++){
    long ok=0,n=0,cnt_fail_cell=0,cnt_d6=0,cnt_d7=0,cnt_dS=0,cnt_two=0,cnt_cons=0,cnt_dW8=0,cnt_rowsfail[20]={0};
    while(n<NS){
      u32 E4,a0; 
      for(;;){ E4=rnd32(); if(mode==0) E4&=0x1fffffff; else if(mode==1){ E4=(E4&0x1fffffff)|((rnd32()%7+1)<<29);} 
        u32 w8=W8C-E4; int c0=(E4>>29)==0, c1=B(w8,29)==1, c2=B(w8,1)!=B(w8,12), c3=B(w8,8)!=B(w8,25), c4=B(w8,14)==B(w8,18);
        int need[5]={1,1,1,1,1}; if(mode>=1) need[mode-1]=0;
        int ok1=1; int c[5]={c0,c1,c2,c3,c4};
        for(int k=0;k<5;k++){ if(mode==0){ if(!c[k]) ok1=0;} else { if(k==mode-1){ if(c[k]) ok1=0; } else if(!c[k]) ok1=0; } }
        if(ok1) break; }
      a0=E4-C4;
      u32 w7=pickF(7), w6=pickF(6);
      u32 x=c7c+MAJ(A2,A1,a0)-CH(E6,E5,E4)-w7; // A_-1 : W7x = c7(a0)-A_-1
      u32 E3=K3C-MAJ(A2,A1,a0)+x;
      u32 cm2=C6+MAJ(A1,a0,x)-CH(E5,a0+C4,E3)-w6; // A_-2
      u32 cv[8]; cv[0]=x; cv[1]=cm2; for(int k=2;k<8;k++)cv[k]=rnd32();
      Tr tx,ty; build(cv,a0,&Xp,&tx); build(cv,a0,&Yp,&ty); n++;
      // consistency: trace reproduces intended rows (Lemma 4.1) for x member
      int cons=1; for(int i=0;i<=13;i++){ if(AA(&tx,i)!=(i==0?a0:AA(&Xp,i))) cons=0; }
      if(!cons) cnt_cons++;
      int fb; int r=cell_rows(&tx,&ty,&fb); int viol=0;
      if(r){cnt_fail_cell++; viol=1; cnt_rowsfail[fb<0?0:fb>19?19:fb]++;}
      if((ty.W[6]-tx.W[6])!=d6){cnt_d6++;viol=1;}
      if((ty.W[7]-tx.W[7])!=d7){cnt_d7++;viol=1;}
      if((ty.W[8]-tx.W[8])!=dW8){cnt_dW8++;viol=1;}
      if((s0(ty.W[8])-s0(tx.W[8]))!=dS8){cnt_dS++;viol=1;}
      if(twobit(&tx)){cnt_two++;viol=1;}
      if(!viol) ok++;
    }
    printf("%-26s n=%ld pass_all=%ld (%.4f) | trace!=rows(cons) %ld, cell fail %ld, dW6!=d6 %ld, dW7!=d7 %ld, dW8!=pub %ld, dS0(W8)!=043ff800 %ld, twobit viol %ld\n",nm[mode],n,ok,(double)ok/n,cnt_cons,cnt_fail_cell,cnt_d6,cnt_d7,cnt_dW8,cnt_dS,cnt_two);
  }
  return 0;}
