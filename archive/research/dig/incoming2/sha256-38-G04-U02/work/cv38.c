// cv38.c - own code: CV words A_-3, A_-4, E_-4 of the sha256-38 ordinary collision (G04-U02)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
#include <pthread.h>
typedef uint32_t u32; typedef uint64_t u64;
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline u32 S0(u32 x){return ROR(x,2)^ROR(x,13)^ROR(x,22);}
static inline u32 S1(u32 x){return ROR(x,6)^ROR(x,11)^ROR(x,25);}
static inline u32 s0(u32 x){return ROR(x,7)^ROR(x,18)^(x>>3);}
static inline u32 s1(u32 x){return ROR(x,17)^ROR(x,19)^(x>>10);}
static inline u32 CH(u32 e,u32 f,u32 g){return (e&f)^(~e&g);}
static inline u32 MAJ(u32 a,u32 b,u32 c){return (a&b)^(a&c)^(b&c);}
static const u32 K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
static const u32 IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
/* published chi38; a..h = A-1,A-2,A-3,A-4,E-1,E-2,E-3,E-4 */
static const u32 CV[8]={0xcd278980,0x1b12a052,0xb87cc8a6,0xa9e059c5,0xc9c3db85,0x6ca4b5b5,0x63d13ac1,0xc0329f1e};
static const u32 MX[16]={0x48fc271b,0x9fca20cd,0xcc89f96f,0xfc40396f,0x8b328cb4,0x6b91ef78,0x97f9b767,0xc2450045,0x3f416758,0xfe9804cb,0x63a88c0f,0x0ceb1f8d,0xa28cd15a,0x77a1e994,0xd28e48a0,0x9f1f65bb};
static const u32 MY[16]={0x48fc271b,0x9fca20cd,0xcc89f96f,0xfc40396f,0x8b328cb4,0x6b91ef78,0x97f9b767,0xe2450045,0x3b016f58,0xde9804cb,0x66a99ea5,0x0ce30b8d,0xa28cd15a,0x77a1e994,0xd28e48a0,0x9b5f6dbb};
static const u32 DIG[8]={0x5d9ca5f4,0x59ace3a3,0x26c9c26c,0x4252c585,0x4c0803b7,0x1b4d5ccd,0x25c3ccc0,0x90645c4d};
#define NS 38
/* trace: A[i+4], E[i+4] for i=-4..NS-1 */
static void trace(const u32 cv[8], const u32 M[16], u32 *A, u32 *E){
  u32 W[64]; for(int i=0;i<16;i++)W[i]=M[i]; for(int i=16;i<NS;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];
  for(int i=0;i<4;i++){A[3-i]=cv[i];E[3-i]=cv[4+i];}
  for(int i=0;i<NS;i++){u32 a=A[i+3],b=A[i+2],c=A[i+1],d=A[i],e=E[i+3],f=E[i+2],g=E[i+1],h=E[i];
    u32 t1=h+S1(e)+CH(e,f,g)+K[i]+W[i], t2=S0(a)+MAJ(a,b,c); E[i+4]=d+t1; A[i+4]=t1+t2;}
}
static void digest(const u32 cv[8], const u32 *A, const u32 *E, u32 out[8]){
  for(int i=0;i<4;i++){out[i]=cv[i]+A[NS+3-i]; out[4+i]=cv[4+i]+E[NS+3-i];}
}
/* Step-2 map: W0..W7 from CV and variant arrays Av[0..7] (A0..A7) */
static void step2(const u32 cv[8], const u32 Av[8], u32 W[8]){
  u32 A[12],E[12]; for(int i=0;i<4;i++){A[3-i]=cv[i];E[3-i]=cv[4+i];}
  for(int i=0;i<8;i++)A[i+4]=Av[i];
  for(int i=0;i<8;i++) E[i+4]=A[i+4]+A[i]-S0(A[i+3])-MAJ(A[i+3],A[i+2],A[i+1]);
  for(int i=0;i<8;i++) W[i]=E[i+4]-A[i]-E[i]-S1(E[i+3])-CH(E[i+3],E[i+2],E[i+1])-K[i];
}
static u32 PA[48],PE[48],QA[48],QE[48];
static u32 AV[8]; static u32 W9X,W14X;
static u32 DW7,DS07;
static inline int inF7(u32 w){return (u32)(s0(w+DW7)-s0(w))==DS07;}
static const u32 GBASE=0x35f29010, GMASK=(1u<<0)|(1u<<2)|(1u<<10)|(1u<<13)|(1u<<19);
static inline int inG(u32 w){return (w&~GMASK)==(GBASE&~GMASK);}
/* fast W16 (member x) from CV words and the fixed variant: needs W0,W1 only */
static inline u32 w16(const u32 cv[8]){
  u32 a=cv[0],b=cv[1],c=cv[2],d=cv[3],e=cv[4],f=cv[5],g=cv[6],h=cv[7];
  u32 E0=AV[0]+d-S0(a)-MAJ(a,b,c);
  u32 W0=E0-d-h-S1(e)-CH(e,f,g)-K[0];
  u32 E1=AV[1]+c-S0(AV[0])-MAJ(AV[0],a,b);
  u32 W1=E1-c-g-S1(E0)-CH(E0,e,f)-K[1];
  return s1(W14X)+W9X+s0(W1)+W0;
}
static u64 rs=88172645463325252ull; static u64 rnd64(void){rs^=rs<<13;rs^=rs>>7;rs^=rs<<17;return rs;}
static void setup(void){
  trace(CV,MX,PA,PE); trace(CV,MY,QA,QE);
  for(int i=0;i<8;i++)AV[i]=PA[i+4];
  W9X=MX[9];W14X=MX[14]; DW7=MY[7]-MX[7]; DS07=s0(MY[7])-s0(MX[7]);
}
/* ---------- validation */
static int cmd_val(void){
  int bad=0; u32 d1[8],d2[8]; digest(CV,PA,PE,d1); digest(CV,QA,QE,d2);
  for(int i=0;i<8;i++){ if(d1[i]!=DIG[i]||d2[i]!=DIG[i]) bad++; }
  printf("VAL digest x/y equal published: %s\n", bad?"FAIL":"OK");
  int diffAE=0; for(int i=-4;i<=6;i++) if(PA[i+4]!=QA[i+4]||PE[i+4]!=QE[i+4]) diffAE++;
  printf("VAL rows -4..6 A/E equal in both members: %s\n", diffAE?"FAIL":"OK");
  u32 W[8]; step2(CV,AV,W); int wb=0; for(int i=0;i<7;i++) if(W[i]!=MX[i]||W[i]!=MY[i]) wb++; if(W[7]!=MX[7]) wb++;
  printf("VAL Step-2 map reproduces published W0..W7 of x (W0..W6 also y): %s\n", wb?"FAIL":"OK");
  u32 AVy[8]; for(int i=0;i<8;i++)AVy[i]=QA[i+4]; step2(CV,AVy,W); printf("VAL Step-2 map y W7 = %08x (published %08x): %s\n",W[7],MY[7],W[7]==MY[7]?"OK":"FAIL");
  u32 Ws[40]; for(int i=0;i<16;i++)Ws[i]=MX[i]; for(int i=16;i<NS;i++)Ws[i]=s1(Ws[i-2])+Ws[i-7]+s0(Ws[i-15])+Ws[i-16];
  printf("VAL W16(x) published schedule %08x  fast w16() %08x  in G: %d\n",Ws[16],w16(CV),inG(Ws[16]));
  printf("VAL dW7=%08x ds0(W7)=%08x  published W7x in F7: %d\n",DW7,DS07,inF7(MX[7]));
  u32 Wy[40]; for(int i=0;i<16;i++)Wy[i]=MY[i]; for(int i=16;i<NS;i++)Wy[i]=s1(Wy[i-2])+Wy[i-7]+s0(Wy[i-15])+Wy[i-16];
  printf("VAL dW16 = %08x (proof 0xe0000000)\n",Wy[16]-Ws[16]);
  int mm=0; for(int t=0;t<200000;t++){u32 cv[8]; for(int i=0;i<8;i++)cv[i]=(u32)rnd64(); u32 W8[8]; step2(cv,AV,W8);
    u32 w=s1(W14X)+W9X+s0(W8[1])+W8[0]; if(w!=w16(cv))mm++;}
  printf("VAL fast w16 vs generic Step-2 on 2e5 random CV: %d mismatches\n",mm);
  return bad+diffAE+wb;
}
typedef struct{u64 lo,hi,n;}Rng;
static void *th_f7(void*p){Rng*r=p;u64 n=0;for(u64 w=r->lo;w<r->hi;w++)n+=inF7((u32)w);r->n=n;return 0;}
static int NT=3;
static u64 par_count(void*(*fn)(void*),Rng*rr,u64 total){pthread_t t[16];for(int i=0;i<NT;i++){rr[i].lo=total/NT*i;rr[i].hi=(i==NT-1)?total:total/NT*(i+1);rr[i].n=0;pthread_create(&t[i],0,fn,&rr[i]);}u64 s=0;for(int i=0;i<NT;i++){pthread_join(t[i],0);s+=rr[i].n;}return s;}
static void cmd_f7(void){Rng rr[16];u64 n=par_count(th_f7,rr,1ull<<32);printf("F7 count (s0(w+dW7)-s0(w)==ds0) over all 2^32: %llu (proof: 287,309,824) %s\n",(unsigned long long)n,n==287309824ull?"MATCH":"MISMATCH");}
/* ---------- exhaustive count of X with W16 in G */
typedef struct{u64 lo,hi,n;int idx;u32 cv[8];}CRng;
static void *th_cnt(void*p){CRng*r=p;u32 cv[8];memcpy(cv,r->cv,32);u64 n=0;for(u64 x=r->lo;x<r->hi;x++){cv[r->idx]=(u32)x;n+=inG(w16(cv));}r->n=n;return 0;}
static u64 cnt_word(const u32 base[8],int idx){pthread_t t[16];CRng rr[16];for(int i=0;i<NT;i++){rr[i].lo=(1ull<<32)/NT*i;rr[i].hi=(i==NT-1)?(1ull<<32):(1ull<<32)/NT*(i+1);rr[i].idx=idx;memcpy(rr[i].cv,base,32);rr[i].n=0;pthread_create(&t[i],0,th_cnt,&rr[i]);}u64 s=0;for(int i=0;i<NT;i++){pthread_join(t[i],0);s+=rr[i].n;}return s;}
static void cmd_cnt(int N,u64 seed){
  rs=seed; const char*nm[3]={"A_-3","A_-4","E_-4"}; int ix[3]={2,3,7};
  u64 tot[3]={0,0,0}; u64 mn[3]={~0ull,~0ull,~0ull},mx[3]={0,0,0}; int nz[3]={0,0,0};
  for(int s=-1;s<N;s++){u32 cv[8]; if(s<0)memcpy(cv,CV,32); else for(int i=0;i<8;i++)cv[i]=(u32)rnd64();
    printf("CNT setting %d (%s) popcount(A-1^A-2)=%d :",s,s<0?"published CV":"random CV",__builtin_popcount(cv[0]^cv[1]));
    for(int k=0;k<3;k++){u64 c=cnt_word(cv,ix[k]);printf(" %s=%llu",nm[k],(unsigned long long)c);if(s>=0){tot[k]+=c;if(c<mn[k])mn[k]=c;if(c>mx[k])mx[k]=c;nz[k]+=c>0;}}
    printf("\n");fflush(stdout);}
  for(int k=0;k<3;k++)printf("CNTSUM %s over %d random settings: mean hits %.3f, min %llu max %llu, settings with >=1 hit %d\n",nm[k],N,(double)tot[k]/N,(unsigned long long)mn[k],(unsigned long long)mx[k],nz[k]);
}
/* ---------- bijection X -> partner word, exhaustive 2^32 with bitset */
static u32 partner(const u32 base[8],int idx,u32 x,int pw){u32 cv[8];memcpy(cv,base,32);cv[idx]=x;u32 W[8];step2(cv,AV,W);return W[pw];}
static void cmd_bij(void){
  const char*nm[3]={"A_-3","A_-4","E_-4"}; int ix[3]={2,3,7}, pw[3]={5,4,0};
  for(int k=0;k<3;k++){u64 bad=0,tot=0;for(int s=0;s<64;s++){u32 cv[8];for(int i=0;i<8;i++)cv[i]=(u32)rnd64();u32 c0=partner(cv,ix[k],0,pw[k]);
    for(u64 x=0;x<(1ull<<24);x++){u32 xx=(u32)(x*257u+ (u32)rnd64()%257u); u32 w=partner(cv,ix[k],xx,pw[k]); tot++; if((u32)(w+xx)!=c0)bad++;}}
    printf("BIJ %s -> W%d : partner(x)+x == partner(0) (i.e. W = C - X, bijective) holds for %llu of %llu samples (64 random other-7-word settings)\n",nm[k],pw[k],(unsigned long long)(tot-bad),(unsigned long long)tot);fflush(stdout);}
}
/* ---------- dependency matrix */
static void cmd_dep(int N){
  const char*cn[8]={"A_-1","A_-2","A_-3","A_-4","E_-1","E_-2","E_-3","E_-4"}; long ch[8][8]; memset(ch,0,sizeof ch);
  for(int t=0;t<N;t++){u32 cv[8];for(int i=0;i<8;i++)cv[i]=(u32)rnd64();u32 W[8];step2(cv,AV,W);
    for(int k=0;k<8;k++){u32 c2[8];memcpy(c2,cv,32);c2[k]^=(u32)rnd64()|1;u32 V[8];step2(c2,AV,V);for(int j=0;j<8;j++)ch[k][j]+=V[j]!=W[j];}}
  printf("DEP fraction of %d random (CV, redraw one word) where W_j changes (published variant A0..A7 fixed)\n          W0     W1     W2     W3     W4     W5     W6     W7\n",N);
  for(int k=0;k<8;k++){printf("%-5s",cn[k]);for(int j=0;j<8;j++)printf(" %.4f",(double)ch[k][j]/N);printf("\n");}
}
/* ---------- real first blocks */
typedef struct{u64 n;u64 seed;int id;
  u64 hAll[3][256],hLo[3][256],hF7[3][256],hF7p[3][256];u64 bit[3][32],bitF7[3][32];u64 nF7,nF7p;}Real;
static void compress38(const u32 M[16],u32 cv[8]){
  u32 A[48],E[48];trace(IV,M,A,E);for(int i=0;i<4;i++){cv[i]=IV[i]+A[NS+3-i];cv[4+i]=IV[4+i]+E[NS+3-i];}
}
static void *th_real(void*p){Real*r=p;u64 s=(r->seed+r->id)*0x9E3779B97F4A7C15ull+0x1234567;
  for(u64 t=0;t<r->n;t++){u32 M[16];for(int i=0;i<16;i+=2){s^=s<<13;s^=s>>7;s^=s<<17;M[i]=(u32)s;M[i+1]=(u32)(s>>32);}
    u32 cv[8];compress38(M,cv);u32 w[8];step2(cv,AV,w);int f7=inF7(w[7]);u32 W16=w16(cv);int pre=(W16>>22)==(GBASE>>22);
    static const int ix[3]={2,3,7};
    for(int k=0;k<3;k++){u32 x=cv[ix[k]];r->hAll[k][x>>24]++;r->hLo[k][x&255]++;for(int b=0;b<32;b++)r->bit[k][b]+=(x>>b)&1;
      if(f7){r->hF7[k][x>>24]++;for(int b=0;b<32;b++)r->bitF7[k][b]+=(x>>b)&1;}
      if(f7&&pre)r->hF7p[k][x>>24]++;}
    r->nF7+=f7;r->nF7p+=f7&&pre;}
  return 0;}
static double chi2(const u64*h,int nb,u64*ntot){u64 n=0;for(int i=0;i<nb;i++)n+=h[i];double e=(double)n/nb,c=0;for(int i=0;i<nb;i++){double d=h[i]-e;c+=d*d/e;}*ntot=n;return c;}
static double chi2p(double c,int k){double z=(pow(c/k,1.0/3)-(1-2.0/(9*k)))/sqrt(2.0/(9*k));return 0.5*erfc(z/sqrt(2));}
static void cmd_real(int lg,u64 seed){
  u64 per=(1ull<<lg)/NT;pthread_t t[16];Real*R=calloc(NT,sizeof(Real));
  for(int i=0;i<NT;i++){R[i].n=per;R[i].seed=seed;R[i].id=i;pthread_create(&t[i],0,th_real,&R[i]);}
  Real*T=calloc(1,sizeof(Real));for(int i=0;i<NT;i++){pthread_join(t[i],0);for(int k=0;k<3;k++){for(int b=0;b<256;b++){T->hAll[k][b]+=R[i].hAll[k][b];T->hLo[k][b]+=R[i].hLo[k][b];T->hF7[k][b]+=R[i].hF7[k][b];T->hF7p[k][b]+=R[i].hF7p[k][b];}for(int b=0;b<32;b++){T->bit[k][b]+=R[i].bit[k][b];T->bitF7[k][b]+=R[i].bitF7[k][b];}}T->nF7+=R[i].nF7;T->nF7p+=R[i].nF7p;}
  u64 N=per*NT;const char*nm[3]={"A_-3","A_-4","E_-4"};
  printf("REAL first blocks: %llu random M0, CV1 = F38(IV,M0) with feed-forward, seed %llu\n",(unsigned long long)N,(unsigned long long)seed);
  printf("REAL W7 in F7 gate: %llu = %.6f of blocks (|F7|/2^32 = %.6f)\n",(unsigned long long)T->nF7,(double)T->nF7/N,287309824.0/4294967296.0);
  printf("REAL W7 in F7 and top-10 bits of W16 equal G prefix: %llu (expect %.1f)\n",(unsigned long long)T->nF7p,(double)T->nF7/1024);
  for(int k=0;k<3;k++){u64 n;double c1=chi2(T->hAll[k],256,&n),c2=chi2(T->hLo[k],256,&n),c3=chi2(T->hF7[k],256,&n),c4=chi2(T->hF7p[k],256,&n);
    double zmax=0,zf=0;for(int b=0;b<32;b++){double z=((double)T->bit[k][b]-N/2.0)/sqrt(N/4.0);if(fabs(z)>zmax)zmax=fabs(z);double z2=((double)T->bitF7[k][b]-T->nF7/2.0)/sqrt(T->nF7/4.0);if(fabs(z2)>zf)zf=fabs(z2);}
    printf("REAL %s: top8 chi2 %.1f (255 dof, p %.3f) | low8 chi2 %.1f (p %.3f) | top8 given F7 chi2 %.1f (p %.3f) | top8 given F7+W16prefix chi2 %.1f (p %.3f) | max |z| over 32 bits %.2f, given F7 %.2f\n",
      nm[k],c1,chi2p(c1,255),c2,chi2p(c2,255),c3,chi2p(c3,255),c4,chi2p(c4,255),zmax,zf);}
}
/* ---------- nonzero dCV: digest effect */
static void cmd_dcv(void){
  const char*nm[3]={"A_-3","A_-4","E_-4"}; int ix[3]={2,3,7};
  for(int k=0;k<3;k++){ u32 cvy[8];memcpy(cvy,CV,32);cvy[ix[k]]+=1;
    u32 My[16];memcpy(My,MX,64);
    if(k==2){ My[0]=MX[0]-1; }
    u32 A[48],E[48],A2[48],E2[48];
    trace(CV,MX,A,E);trace(cvy,My,A2,E2);
    int diffrows=0;for(int i=0;i<NS;i++) if(A[i+4]!=A2[i+4]||E[i+4]!=E2[i+4])diffrows++;
    u32 d1[8],d2[8];digest(CV,A,E,d1);digest(cvy,A2,E2,d2);int dd=0;for(int i=0;i<8;i++)dd+=d1[i]!=d2[i];
    printf("DCV %s +1 in member y (message adjusted: %s): state rows 0..37 differing: %d ; digest words differing: %d",nm[k],k==2?"W0-=1":"none",diffrows,dd);
    for(int i=0;i<8;i++)if(d1[i]!=d2[i])printf(" (digest word %d differs by %u)",i,d2[i]-d1[i]);
    printf("\n");}
}
int main(int argc,char**argv){
  for(int i=1;i<argc-1;i++)if(!strcmp(argv[i],"--threads"))NT=atoi(argv[i+1]);
  setup(); const char*c=argc>1?argv[1]:"val";
  if(!strcmp(c,"val")){return cmd_val();}
  if(!strcmp(c,"f7"))cmd_f7();
  else if(!strcmp(c,"cnt"))cmd_cnt(atoi(argv[2]),strtoull(argv[3],0,10));
  else if(!strcmp(c,"bij"))cmd_bij();
  else if(!strcmp(c,"dep"))cmd_dep(atoi(argv[2]));
  else if(!strcmp(c,"real"))cmd_real(atoi(argv[2]),strtoull(argv[3],0,10));
  else if(!strcmp(c,"dcv"))cmd_dcv();
  return 0;}
