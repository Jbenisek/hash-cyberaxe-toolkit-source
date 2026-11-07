#include "common.h"
#include <math.h>
// Independent sequential Monte Carlo for q3 (own code, from the characteristic): stage means for rows 16..22 and the tail rows 23..36.
// usage: smc seed NP M MT22 MT reps useGprime
typedef struct { u32 z,o,n,u,eq; } Msk;
static Msk MK[3][64]; // [kind][row+4]
static u32 PL[3][64]; // plus mask between row r and r+1
typedef struct { int ka,ra,ba,kb,rb,bb,eq,mr; } XCnd;
static XCnd XC[64]; static int nXC;
static void compile(){
  for(int k=0;k<3;k++)for(int r=-4;r<=36;r++){ Msk*m=&MK[k][r+4]; memset(m,0,sizeof(*m)); u32 pm=0;
    for(int b=0;b<32;b++){ char s=sym(k,r,b); u32 bt=1u<<b;
      if(s=='='||s=='+')m->eq|=bt; else if(s=='0')m->z|=bt; else if(s=='1')m->o|=bt; else if(s=='n')m->n|=bt; else if(s=='u')m->u|=bt;
      if(s=='+'&&sym(k,r+1,b)=='+')pm|=bt; }
    PL[k][r+4]=pm; }
  for(int i=0;i<NX2;i++){ char op[4],na,nb; XCnd*c=&XC[nXC++]; sscanf(X2[i],"%c%d[%d] %2s %c%d[%d]",&na,&c->ra,&c->ba,op,&nb,&c->rb,&c->bb);
    c->ka=na=='A'?0:na=='E'?1:2; c->kb=nb=='A'?0:nb=='E'?1:2; c->eq=op[0]=='='; c->mr=c->ra>c->rb?c->ra:c->rb; }
}
static inline int okm(const Msk*m,u32 x,u32 y){ return !((x^y)&m->eq)&&!((x|y)&m->z)&&((x&y&m->o)==m->o)&&((~x&y&m->n)==m->n)&&((x&~y&m->u)==m->u); }
static inline u32 gv(const Tr*t,int k,int r){ return k==0?AA(t,r):k==1?EE(t,r):t->W[r]; }
static int x2ok(const Tr*t,int row){ for(int i=0;i<nXC;i++){XCnd*c=&XC[i]; if(c->mr!=row)continue; if((((gv(t,c->ka,c->ra)>>c->ba)^(gv(t,c->kb,c->rb)>>c->bb))&1)==(u32)c->eq) return 0;} return 1; }
static int rowok(const Tr*x,const Tr*y,int r){
  if(!okm(&MK[0][r+4],AA(x,r),AA(y,r))||!okm(&MK[1][r+4],EE(x,r),EE(y,r))||!okm(&MK[2][r+4],x->W[r],y->W[r])) return 0;
  if((AA(x,r-1)^AA(x,r))&PL[0][r-1+4]) return 0; if((EE(x,r-1)^EE(x,r))&PL[1][r-1+4]) return 0; if((x->W[r-1]^x->W[r])&PL[2][r-1+4]) return 0;
  return x2ok(x,r); }
static void step(Tr*t,int i,u32 w){
  u32 a=AA(t,i-1),b=AA(t,i-2),c=AA(t,i-3),d=AA(t,i-4),e=EE(t,i-1),f=EE(t,i-2),g=EE(t,i-3),h=EE(t,i-4);
  u32 T1=h+S1(e)+CH(e,f,g)+K[i]+w; EE(t,i)=d+T1; AA(t,i)=T1+S0(a)+MAJ(a,b,c); t->W[i]=w; }
static u64 rs[4]; static inline u64 rotl(u64 x,int k){return (x<<k)|(x>>(64-k));}
static u64 rnd(){u64*s=rs;u64 r=rotl(s[1]*5,7)*9,tt=s[1]<<17;s[2]^=s[0];s[3]^=s[1];s[1]^=s[2];s[0]^=s[3];s[2]^=tt;s[3]=rotl(s[3],45);return r;}
static u64 sm(u64*x){u64 z=(*x+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;return z^(z>>31);}
#define B(w,i) (((w)>>(i))&1u)
static int inF6(u32 w){ return (s0(w+0x20000000u)-s0(w))==0x03c00800u; }
static int inF7(u32 w){
  if(!(B(w,1)==B(w,18)&&B(w,0)==B(w,28)&&B(w,9)==B(w,30))) return 0;
  if(B(w,11)==0&&B(w,22)==1&&B(w,26)==1) return 1;
  if(B(w,11)==1&&B(w,12)==0&&B(w,22)==0&&B(w,23)==1&&B(w,26)==0&&B(w,27)==1&&B(w,2)==B(w,19)&&B(w,1)==B(w,29)&&B(w,10)==B(w,31)) return 1;
  return 0; }
typedef struct { Tr x,y; int l; u32 w7; } P;
static Tr X0,Y0;
static u32 fixedval(int kind,int row,u32*fm){u32 v=0,m=0;for(int b=0;b<32;b++){char s=sym(kind,row,b);if(s=='1'||s=='u')v|=1u<<b; if(s=='='||s=='+')m|=1u<<b;}*fm=m;return v;}
int main(int argc,char**argv){
  u64 seed=argc>1?atoll(argv[1]):1; int NP=argc>2?atoi(argv[2]):4096, M=argc>3?atoi(argv[3]):512, MT22=argc>4?atoi(argv[4]):4096, MT=argc>5?atoi(argv[5]):1024, reps=argc>6?atoi(argv[6]):4, gp=argc>7?atoi(argv[7]):0;
  u64 sd=seed*1000003ULL+17; for(int k=0;k<4;k++)rs[k]=sm(&sd);
  load_chi("./research/tools/traillab/chi/chi37.txt"); compile(); trace(CV,MX,&X0); trace(CV,MY,&Y0);
  u32 dW[37]; for(int t=0;t<37;t++)dW[t]=Y0.W[t]-X0.W[t];
  u32 xm14=0,xm15=0; for(int b=0;b<32;b++){ if(sym(2,14,b)=='n'||sym(2,14,b)=='u')xm14|=1u<<b; if(sym(2,15,b)=='n'||sym(2,15,b)=='u')xm15|=1u<<b; }
  // L* (hard-coded from the l16 result, re-verified below by the row-16 enumeration: dE16,dA16 equal the characteristic's)
  u32 W15L[32]={0x7dd41680,0x7dd41681,0x7dd416a0,0x7dd416a1,0x7dd41a80,0x7dd41a81,0x7dd41aa0,0x7dd41aa1,0x7dd43680,0x7dd43681,0x7dd436a0,0x7dd436a1,0x7dd43a80,0x7dd43a81,0x7dd43aa0,0x7dd43aa1,0xfdb41680,0xfdb41681,0xfdb416a0,0xfdb416a1,0xfdb41a80,0xfdb41a81,0xfdb41aa0,0xfdb41aa1,0xfdb43680,0xfdb43681,0xfdb436a0,0xfdb436a1,0xfdb43a80,0xfdb43a81,0xfdb43aa0,0xfdb43aa1};
  u32 W14=0xbd1d3f7b;
  Tr XL[32],YL[32];
  for(int l=0;l<32;l++){ XL[l]=X0;YL[l]=Y0; step(&XL[l],14,W14);step(&YL[l],14,W14^xm14);step(&XL[l],15,W15L[l]);step(&YL[l],15,W15L[l]^xm15); }
  // initial particle pool: all (l,E16x) passing row 16
  u32 em; u32 ev=fixedval(1,16,&em);
  u32 *pl=malloc(4*1100000),*pe=malloc(4*1100000); long long npool=0;
  for(int l=0;l<32;l++){ u32 w16b=s1(W14)+X0.W[9]; u32 dw16=(s1(W14^xm14)+Y0.W[9])-w16b; if(dw16)continue;
    Tr x0=XL[l]; step(&x0,16,w16b); u32 C16=EE(&x0,16);
    for(u32 s=0;;s=(s-em)&em){ u32 e16=ev|s; u32 w16x=w16b+(e16-C16); Tr xx=XL[l],yy=YL[l]; step(&xx,16,w16x); step(&yy,16,w16x);
      if(rowok(&xx,&yy,16)){ pl[npool]=l; pe[npool]=e16; npool++; }
      if(s==em)break; } }
  printf("row 16 pool: %lld pairs ; stage mean 2^%.4f\n",npool,log2(npool/(32.0*4294967296.0)));
  // G list (E4 values)
  u32 A1=AA(&X0,1),A2=AA(&X0,2),A3=AA(&X0,3),A4=AA(&X0,4),E5=EE(&X0,5),E6=EE(&X0,6),E7=EE(&X0,7),E8=EE(&X0,8);
  u32 C4=A4-S0(A3)-MAJ(A3,A2,A1), W8C=E8-A4-S1(E7)-CH(E7,E6,E5)-K[8]; (void)C4;
  u32 *G=malloc(4*20000000); long long nG=0; u32 need=s0(Y0.W[8])-s0(X0.W[8]);
  for(u32 E4=0;E4<(1u<<29);E4++){ u32 w8=W8C-E4; int ok;
    if(gp) ok=((s0(w8+dW[8])-s0(w8))==need); else ok=B(w8,29)&&(B(w8,1)!=B(w8,12))&&(B(w8,8)!=B(w8,25))&&(B(w8,14)==B(w8,18));
    if(ok)G[nG++]=E4; }
  printf("G list (%s): %lld\n",gp?"G' modular-only":"G",nG); fflush(stdout);
  P*pa=malloc(sizeof(P)*NP),*pb=malloc(sizeof(P)*NP);
  // children records
  long long cap=(long long)NP*M+1000; u32 *cpar=malloc(4*cap),*ce1=malloc(4*cap),*ce2=malloc(4*cap);
  double sum_log[9]={0}, sum2[9]={0}; double tot_sum=0,tot2=0; int nrep=0;
  for(int rep=0;rep<reps;rep++){
    double lg[9]; int fail=0;
    // stage 16
    for(int i=0;i<NP;i++){ long long k=rnd()%npool; int l=pl[k]; P*p=&pa[i]; p->x=XL[l];p->y=YL[l];p->l=l; u32 w16b=s1(W14)+X0.W[9]; Tr x0=XL[l]; step(&x0,16,w16b); u32 w16x=w16b+(pe[k]-EE(&x0,16)); step(&p->x,16,w16x); step(&p->y,16,w16x); }
    lg[0]=log2(npool/(32.0*4294967296.0));
    int cur=NP;
    for(int t=17;t<=21&&!fail;t++){
      u32 fm; u32 fv=fixedval(1,t,&fm); int f=32-__builtin_popcount(fm); long long nc=0;
      for(int i=0;i<cur;i++){ P*p=&pa[i];
        for(int c=0;c<M;c++){ u32 e=fv|((u32)rnd()&fm);
          u32 wx=e-AA(&p->x,t-4)-EE(&p->x,t-4)-S1(EE(&p->x,t-1))-CH(EE(&p->x,t-1),EE(&p->x,t-2),EE(&p->x,t-3))-K[t];
          Tr tx,ty; /* copy only needed */ tx=p->x; ty=p->y; step(&tx,t,wx); step(&ty,t,wx+dW[t]);
          if(rowok(&tx,&ty,t)&&nc<cap){ cpar[nc]=i; ce1[nc]=wx; nc++; } } }
      double mean=(double)nc*pow(2.0,-f)/((double)cur*M); if(nc==0){fail=1;break;} lg[t-16]=log2(mean);
      for(int i=0;i<NP;i++){ long long k=rnd()%nc; P*p=&pb[i]; *p=pa[cpar[k]]; step(&p->x,t,ce1[k]); step(&p->y,t,ce1[k]+dW[t]); }
      P*sw=pa;pa=pb;pb=sw; cur=NP; }
    if(fail){printf("rep %d failed\n",rep);continue;}
    // stage 22 : (W6,W7) from F6 x F7
    { long long nc=0; for(int i=0;i<cur;i++){ P*p=&pa[i];
        for(int c=0;c<MT22;c++){ u32 w6,w7; do w6=(u32)rnd(); while(!inF6(w6)); do w7=(u32)rnd(); while(!inF7(w7));
          u32 w15=p->x.W[15]; u32 wx=s1(p->x.W[20])+w15+s0(w7)+w6; Tr tx=p->x,ty=p->y; step(&tx,22,wx); step(&ty,22,wx+dW[22]);
          if(rowok(&tx,&ty,22)&&nc<cap){ cpar[nc]=i; ce1[nc]=wx; ce2[nc]=w7; nc++; } } }
      if(nc==0){printf("rep %d failed at 22\n",rep);continue;} lg[6]=log2((double)nc/((double)cur*MT22));
      for(int i=0;i<NP;i++){ long long k=rnd()%nc; P*p=&pb[i]; *p=pa[cpar[k]]; step(&p->x,22,ce1[k]); step(&p->y,22,ce1[k]+dW[22]); p->w7=ce2[k]; }
      P*sw=pa;pa=pb;pb=sw; cur=NP; }
    // tail: W8 from G, rows 23..36
    { long long pass=0,tot=0; long long rowpass[40]={0};
      for(int i=0;i<cur;i++){ P*p=&pa[i];
        for(int c=0;c<MT;c++){ u32 E4=G[rnd()%nG]; u32 w8x=W8C-E4, w8y=w8x+dW[8]; tot++;
          Tr tx=p->x,ty=p->y; int ok=1;
          u32 w7x=p->w7, w7y=p->w7+dW[7];
          for(int t=23;t<=36&&ok;t++){
            u32 wx,wy;
            #define WX(tr,j,w7,w8) ((j)==7?(w7):(j)==8?(w8):(tr)->W[j])
            wx=s1(WX(&tx,t-2,w7x,w8x))+WX(&tx,t-7,w7x,w8x)+s0(WX(&tx,t-15,w7x,w8x))+WX(&tx,t-16,w7x,w8x);
            wy=s1(WX(&ty,t-2,w7y,w8y))+WX(&ty,t-7,w7y,w8y)+s0(WX(&ty,t-15,w7y,w8y))+WX(&ty,t-16,w7y,w8y);
            step(&tx,t,wx); step(&ty,t,wy);
            if(!rowok(&tx,&ty,t)) ok=0; else rowpass[t]++; }
          if(ok)pass++; } }
      lg[7]=log2((double)(pass?pass:1)/(double)tot);
      printf("  tail row survivors:"); for(int t=23;t<=36;t++)printf(" %d:%lld",t,rowpass[t]); printf("\n"); }
    double s=0; for(int k=0;k<8;k++)s+=lg[k];
    printf("rep %d: stage log2 means:",rep); for(int k=0;k<8;k++)printf(" %.3f",lg[k]); printf(" | log2 q3 = %.3f\n",s); fflush(stdout);
    for(int k=0;k<8;k++){sum_log[k]+=lg[k];} tot_sum+=s; tot2+=s*s; nrep++;
  }
  if(nrep){ double m=tot_sum/nrep; printf("SUMMARY seed %llu: reps %d mean log2 q3 = %.4f ; sd %.4f\n",(unsigned long long)seed,nrep,m,nrep>1?sqrt((tot2-nrep*m*m)/(nrep-1)):0.0);
    printf("mean stage log2:"); for(int k=0;k<8;k++)printf(" %.3f",sum_log[k]/nrep); printf("\n"); }
  return 0; }
