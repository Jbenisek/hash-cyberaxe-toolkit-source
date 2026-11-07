// own code, G04-U07 scan (sha256-38): CV / first block / padding layout of the ordinary collision.
// uses common.h (own SHA-256 trace + chi38 parser) and chi38.txt (copy). modes: val | lens | padcorr N | build | check | iv | gdist KIND LOG2N SEED
#include "common.h"
#include <omp.h>
#include <math.h>
#define B(w,i) (((w)>>(i))&1u)
static const u32 IV[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static void compress(const u32 cv[8], const u32 m[16], int steps, u32 out[8]){
  u32 W[64]; for(int i=0;i<16;i++)W[i]=m[i]; for(int i=16;i<steps;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];
  u32 a=cv[0],b=cv[1],c=cv[2],d=cv[3],e=cv[4],f=cv[5],g=cv[6],h=cv[7];
  for(int i=0;i<steps;i++){u32 T1=h+S1(e)+CH(e,f,g)+K[i]+W[i],T2=S0(a)+MAJ(a,b,c); h=g;g=f;f=e;e=d+T1;d=c;c=b;b=a;a=T1+T2;}
  out[0]=cv[0]+a;out[1]=cv[1]+b;out[2]=cv[2]+c;out[3]=cv[3]+d;out[4]=cv[4]+e;out[5]=cv[5]+f;out[6]=cv[6]+g;out[7]=cv[7]+h;
}
static void padblock(u64 lenbytes,u32 m[16]){ memset(m,0,64); m[0]=0x80000000u; u64 bits=lenbytes*8; m[14]=(u32)(bits>>32); m[15]=(u32)bits; }
static void pr(const char*t,const u32*v){printf("%s",t);for(int i=0;i<8;i++)printf("%08x",v[i]);printf("\n");}
typedef struct{u64 s;}Rng; static inline u64 nx(Rng*r){u64 z=(r->s+=0x9e3779b97f4a7c15ull);z=(z^(z>>30))*0xbf58476d1ce4e5b9ull;z=(z^(z>>27))*0x94d049bb133111ebull;return z^(z>>31);}
static inline u32 r32(Rng*r){return (u32)nx(r);}
static u32 PA[18],PE[18];
#define PAr(i) PA[(i)+4]
static const u32 D7=0x20000000,T7=0x03bff800; // W7y=W7x+D7, filter F7 (no W6 filter at 38 steps; dW6=0)
static inline int fs7(u32 w){return (u32)(s0(w+D7)-s0(w))==T7;}
static u32 C4,W8C,D8,C16; static const u32 R16B=0x481b02f9,R16F=0x82405;
static inline int r16ok(u32 e){return ((e-R16B)&~R16F)==0;}
static void ref_words(const u32 cv[8],u32 a0,u32*W){ // W0..W13 of member x connecting cv to published rows with A0:=a0
  u32 A[18],E[18]; memcpy(A,PA,sizeof A); memcpy(E,PE,sizeof E);
  for(int i=0;i<4;i++){A[3-i]=cv[i];E[3-i]=cv[4+i];}
  A[4]=a0; for(int i=0;i<=13;i++)E[i+4]=A[i+4]+A[i]-S0(A[i+3])-MAJ(A[i+3],A[i+2],A[i+1]);
  for(int i=0;i<=13;i++)W[i]=E[i+4]-A[i]-E[i]-S1(E[i+3])-CH(E[i+3],E[i+2],E[i+1])-K[i];
}
static inline u32 c7of(u32 a0){
  u32 A1=PAr(1),A2=PAr(2),A3=PAr(3),E5=PE[5+4],E6=PE[6+4],E7=PE[7+4];
  u32 e4=a0+C4; return E7-2*A3+S0(A2)+MAJ(A2,A1,a0)-S1(E6)-CH(E6,E5,e4)-K[7];
}
static inline u32 e16x(const u32 cv[8],u32 a0){ u32 W[14]; ref_words(cv,a0,W); return C16+W[0]+s0(W[1]); }
static u32 *Ga0,*Gc7; static long nG; static u32 *clsStart; static long nCls; static unsigned char *is90;
static int cmp64(const void*a,const void*b){u64 x=*(u64*)a,y=*(u64*)b;return x<y?-1:x>y;}
static void loadpub(void){
  load_chi("chi38.txt"); Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  for(int i=-4;i<=13;i++){PA[i+4]=AA(&X,i);PE[i+4]=EE(&X,i);}
  u32 A1=AA(&X,1),A2=AA(&X,2),A3=AA(&X,3),A4=AA(&X,4),E5=EE(&X,5),E6=EE(&X,6),E7=EE(&X,7),E8=EE(&X,8);
  C4=A4-S0(A3)-MAJ(A3,A2,A1); W8C=E8-A4-S1(E7)-CH(E7,E6,E5)-K[8]; D8=MY[8]-MX[8];
  C16=AA(&X,12)+EE(&X,12)+S1(EE(&X,15))+CH(EE(&X,15),EE(&X,14),EE(&X,13))+K[16]+s1(MX[14])+MX[9];
}
static inline int inG_w(u32 w){ u32 y=w+D8; if(!wordok(2,8,w,y))return 0; return (B(w,0)!=B(w,28))&&(B(w,30)!=B(w,9))&&(B(w,1)==B(w,18)); }
static void build_G(void){
  u64 *tmp=NULL; long n=0,cap=0;
  #pragma omp parallel num_threads(2)
  { long lc=4000000; u64*loc=malloc(8*lc); long ln=0;
    #pragma omp for schedule(static)
    for(long long ww=0;ww<(1LL<<32);ww++){ u32 w=(u32)ww; if(!inG_w(w))continue; u32 a0=W8C-w-C4;
      if(ln==lc){lc*=2;loc=realloc(loc,8*lc);} loc[ln++]=((u64)c7of(a0)<<32)|a0; }
    #pragma omp critical
    { if(n+ln>cap){cap=(n+ln)*3/2+1;tmp=realloc(tmp,8*cap);} memcpy(tmp+n,loc,8*ln); n+=ln; }
    free(loc); }
  qsort(tmp,n,8,cmp64); nG=n; Ga0=malloc(4*n); Gc7=malloc(4*n);
  for(long i=0;i<n;i++){Ga0[i]=(u32)tmp[i];Gc7[i]=(u32)(tmp[i]>>32);} free(tmp);
  clsStart=malloc(4*(n+2)); long nc=0; for(long i=0;i<n;i++) if(i==0||Gc7[i]!=Gc7[i-1]) clsStart[nc++]=(u32)i; clsStart[nc]=(u32)n; nCls=nc;
  printf("G built: %ld variants (a0), %ld distinct c7 classes (exhaustive over W8x in 2^32: W8 cell + 3 two-bit conditions)\n",nG,nc);
  long hist_max=0; for(long c=0;c<nc;c++){long s=clsStart[c+1]-clsStart[c]; if(s>hist_max)hist_max=s;} printf("largest class %ld\n",hist_max);
}
static void save_G(void){FILE*f=fopen("G.bin","wb");fwrite(&nG,8,1,f);fwrite(&nCls,8,1,f);fwrite(Ga0,4,nG,f);fwrite(Gc7,4,nG,f);fwrite(clsStart,4,nCls+1,f);fclose(f);}
static int load_G(void){FILE*f=fopen("G.bin","rb");if(!f)return 0;fread(&nG,8,1,f);fread(&nCls,8,1,f);Ga0=malloc(4*nG);Gc7=malloc(4*nG);clsStart=malloc(4*(nCls+1));fread(Ga0,4,nG,f);fread(Gc7,4,nG,f);fread(clsStart,4,nCls+1,f);fclose(f);
  is90=calloc(nCls,1); FILE*g=fopen("c90.txt","r"); unsigned c,b,m; int found=0,tot=0; while(g&&fscanf(g,"%x %x %x",&c,&b,&m)==3){tot++; long lo=0,hi=nCls-1; while(lo<=hi){long mid=(lo+hi)/2; u32 v=Gc7[clsStart[mid]]; if(v==c){is90[mid]=1;found++;break;} if(v<c)lo=mid+1; else hi=mid-1;}} if(g)fclose(g);
  fprintf(stderr,"loaded G %ld variants %ld classes; 90-class list: %d of %d found in G\n",nG,nCls,found,tot); return 1;}
static void gate(u32 Am1,u32*gall,u32*g90,u32*np,u32*np90){
  u32 ga=0,g9=0,n=0,n9=0;
  for(long c=0;c<nCls;c++){ u32 x=Gc7[clsStart[c]]-Am1; if(!fs7(x))continue; u32 sz=clsStart[c+1]-clsStart[c]; ga+=sz; n++; if(is90[c]){g9+=sz;n9++;} }
  *gall=ga;*g90=g9;*np=n;*np90=n9;
}
static int cmpu32(const void*a,const void*b){u32 x=*(u32*)a,y=*(u32*)b;return x<y?-1:x>y;}
static void stats(const char*nm,u32*v,long n){
  double s=0,s2=0; u32 mx=0,mn=~0u; long z=0; for(long i=0;i<n;i++){s+=v[i];s2+=(double)v[i]*v[i];if(v[i]>mx)mx=v[i];if(v[i]<mn)mn=v[i];z+=v[i]==0;}
  double m=s/n,var=s2/n-m*m; u32*c=malloc(4*n);memcpy(c,v,4*n);qsort(c,n,4,cmpu32);
  printf("%s: N=%ld mean=%.2f (se %.2f) sd=%.2f cv=%.4f min=%u max=%u P(g=0)=%.5f q05=%u q25=%u q50=%u q75=%u q95=%u\n",nm,n,m,sqrt(var/n),sqrt(var),sqrt(var)/m,mn,mx,(double)z/n,c[n/20],c[n/4],c[n/2],c[3*n/4],c[n-n/20-1]);
  free(c);
}
int main(int argc,char**argv){
  const char*mode=argc>1?argv[1]:"val";
  loadpub();
  if(!strcmp(mode,"val")){
    u32 m0[16],m1[16],pb[16],cv[8],cv2[8],o[8]; unsigned char by[128]; for(int i=0;i<128;i++)by[i]=(unsigned char)((i*7+3)&255);
    for(int i=0;i<16;i++){m0[i]=(u32)by[4*i]<<24|by[4*i+1]<<16|by[4*i+2]<<8|by[4*i+3]; m1[i]=(u32)by[64+4*i]<<24|by[64+4*i+1]<<16|by[64+4*i+2]<<8|by[64+4*i+3];}
    padblock(128,pb); compress(IV,m0,64,cv); compress(cv,m1,64,cv2); compress(cv2,pb,64,o); pr("SHA256_64step_128B_own=",o);
    compress(IV,m0,38,cv); compress(cv,m1,38,cv2); compress(cv2,pb,38,o); pr("SHA256_38step_128B_own=",o);
    u32 ox[8],oy[8],px[8],py[8]; compress(CV,MX,38,ox); compress(CV,MY,38,oy); pr("blk2 x digest=",ox); pr("blk2 y digest=",oy);
    padblock(128,pb); compress(ox,pb,38,px); compress(oy,pb,38,py); pr("blk3 x digest=",px); pr("blk3 y digest=",py);
    printf("printed digest="); for(int i=0;i<8;i++)printf("%08x",DIG[i]); printf("\n");
    printf("blk2 equal=%d blk2==printed=%d blk3 equal=%d\n",!memcmp(ox,oy,32),!memcmp(ox,DIG,32),!memcmp(px,py,32));
    printf("pad block words: W0=%08x W1..W13=0 W14=%08x W15=%08x\n",pb[0],pb[14],pb[15]);
    printf("published dW (y-x): ");for(int i=0;i<16;i++)printf("%d:%08x ",i,MY[i]-MX[i]);printf("\n");
    return 0; }
  if(!strcmp(mode,"lens")){
    u32 rq14=MY[14]-MX[14], rq15=MY[15]-MX[15]; printf("required dW14=%08x dW15=%08x\n",rq14,rq15);
    long pairs=0,ok=0,okdw=0,okd15=0;
    for(int L=0;L<=119;L++) for(int Lp=0;Lp<=119;Lp++){
      if(L%64>55||Lp%64>55) continue; pairs++; u32 d14=0,d15=(u32)(8*Lp)-(u32)(8*L);
      if(d14==rq14&&d15==rq15)okdw++; if(d15==rq15)okd15++; if(L==Lp)ok++; }
    printf("member length pairs (L,L') in 0..119 bytes with padding inside the final block: %ld ; pairs with dW14,dW15 equal to the required values: %ld ; pairs with dW15 alone equal: %ld ; equal-length pairs (dW14=dW15=0): %ld\n",pairs,okdw,okd15,ok);
    printf("max |dW15| reachable by length difference (bytes<=119): %u bits vs required (y-x mod 2^32) %u\n",8*119,rq15);
    u64 dl=((u64)rq15)>>3; printf("rq15 divisible by 8: %d ; smallest L'-L>0 bytes with 8(L'-L) = rq15 mod 2^32: %llu (2^%.2f)\n",(rq15&7)==0,(unsigned long long)dl,log2((double)dl));
    return 0; }
  if(!strcmp(mode,"padcorr")){
    u32 pb[16]; padblock(128,pb); Rng r={777}; long ntest=0,coll=0; int minw=999; double sumw=0; long nw=0;
    int nsamp=atoi(argv[2]);
    for(int s=0;s<nsamp;s++){ u32 cv[8]; for(int i=0;i<8;i++)cv[i]=r32(&r); u32 o[8]; compress(cv,pb,38,o);
      for(int a=0;a<256;a++) for(int b=a;b<256;b++){ u32 c2[8],o2[8]; memcpy(c2,cv,32); c2[a>>5]^=1u<<(a&31); if(b!=a)c2[b>>5]^=1u<<(b&31);
        compress(c2,pb,38,o2); int w=0; for(int i=0;i<8;i++) w+=__builtin_popcount(o[i]^o2[i]); ntest++; if(w==0)coll++; if(w<minw)minw=w; sumw+=w; nw++; }
      for(int i=0;i<8;i++){ for(int sg=0;sg<2;sg++){ u32 c2[8],o2[8]; memcpy(c2,cv,32); c2[i]+= sg?1u:0xffffffffu; compress(c2,pb,38,o2); int w=0; for(int k=0;k<8;k++)w+=__builtin_popcount(o[k]^o2[k]); ntest++; if(w==0)coll++; if(w<minw)minw=w; sumw+=w; nw++; } } }
    printf("padblock correction test: %ld (CV2,dCV2) tests (XOR weight 1-2: 32896 diffs, +-1 per word: 16 diffs, per CV2 sample), output-equal: %ld, min output XOR weight %d, mean %.2f of 256\n",ntest,coll,minw,sumw/nw);
    return 0; }
  if(!strcmp(mode,"build")){build_G();save_G();return 0;}
  if(!load_G()){printf("no G.bin\n");return 1;}
  double pF7=287309824.0/4294967296.0;
  if(!strcmp(mode,"check")){
    Tr X; trace(CV,MX,&X); u32 W[14]; ref_words(CV,AA(&X,0),W); int ok=1; for(int i=0;i<14;i++) if(W[i]!=MX[i]) ok=0;
    printf("ref_words(published CV, published a0) reproduces W0..W13 of x: %d ; c7 closed W7=%08x pub W7=%08x\n",ok,c7of(AA(&X,0))-CV[0],MX[7]);
    printf("published a0=%08x in G: %d ; its W7 in F7: %d ; E16x(pub)=%08x r16ok=%d\n",AA(&X,0),inG_w(W8C-(AA(&X,0)+C4)),fs7(MX[7]),e16x(CV,AA(&X,0)),r16ok(e16x(CV,AA(&X,0))));
    Rng r={12345}; long bad=0,N=2000000,bad2=0; for(long k=0;k<N;k++){u32 cv[8];for(int i=0;i<8;i++)cv[i]=r32(&r);u32 a0=Ga0[nx(&r)%nG];ref_words(cv,a0,W); if(W[7]!=c7of(a0)-cv[0])bad++; if(!inG_w(W8C-(a0+C4)))bad2++;}
    printf("closed form W7=c7-A_-1 vs ref_words on %ld random (cv,a0 in G): mismatches %ld ; sampled a0 not in G: %ld\n",N,bad,bad2);
    long b3=0,b6=0,n=200000,chg16=0; for(long k=0;k<n;k++){u32 cv[8],cw[8];for(int i=0;i<8;i++)cv[i]=r32(&r);memcpy(cw,cv,32);for(int i=2;i<8;i++)cw[i]=r32(&r);u32 a0=Ga0[nx(&r)%nG],W2[14];ref_words(cv,a0,W);ref_words(cw,a0,W2);if(W[7]!=W2[7])b3++; if(W[6]!=W2[6])b6++; if(e16x(cv,a0)!=e16x(cw,a0))chg16++;}
    printf("redraw CV words 2..7 (A_-1,A_-2 kept): W7 changed in %ld of %ld ; W6 changed %ld ; E16x changed %ld\n",b3,n,b6,chg16);
    long b4=0,b5=0; for(long k=0;k<n;k++){u32 cv[8],cw[8];for(int i=0;i<8;i++)cv[i]=r32(&r);memcpy(cw,cv,32);cw[1]=r32(&r);u32 a0=Ga0[nx(&r)%nG],W2[14];ref_words(cv,a0,W);ref_words(cw,a0,W2);if(W[7]!=W2[7])b4++; if(W[6]!=W2[6])b5++;}
    printf("redraw A_-2 only: W7 changed in %ld of %ld ; W6 changed in %ld\n",b4,n,b5);
    printf("sizes: nG=%ld nCls=%ld, mean class size %.2f\n",nG,nCls,(double)nG/nCls);
    long n90=0,v90=0; for(long c=0;c<nCls;c++) if(is90[c]){n90++;v90+=clsStart[c+1]-clsStart[c];} printf("90-class set: %ld classes, %ld variants\n",n90,v90);
    return 0; }
  if(!strcmp(mode,"iv")){
    u32 ga,g9,np,n9; gate(IV[0],&ga,&g9,&np,&n9);
    printf("g(IV): A_-1=%08x g_all=%u (%u classes) g_90=%u (%u of 90 classes) ; expected at a random CV: g_all=%.2f classes=%.2f\n",IV[0],ga,np,g9,n9,(double)nG*pF7,(double)nCls*pF7);
    return 0; }
  if(!strcmp(mode,"gdist")){
    int kind=atoi(argv[2]); int lg=atoi(argv[3]); u64 seed=strtoull(argv[4],0,10); long N=1l<<lg; omp_set_num_threads(2);
    u32*va=malloc(4*N),*v9=malloc(4*N),*vp=malloc(4*N),*vq=malloc(4*N); double t0=omp_get_wtime();
    Rng r0={seed}; u32 m0s[16]; for(int i=0;i<16;i++)m0s[i]=r32(&r0); u32 cv0[8]; compress(IV,m0s,38,cv0);
    #pragma omp parallel for schedule(dynamic,16)
    for(long k=0;k<N;k++){ Rng r={seed*0x100000001b3ull+(u64)k*0x9e3779b97f4a7c15ull+7}; u32 cv[8],m[16];
      if(kind==0){for(int i=0;i<16;i++)m[i]=r32(&r);compress(IV,m,38,cv);}
      else if(kind==1){for(int i=0;i<16;i++)m[i]=r32(&r);compress(cv0,m,38,cv);}
      else {for(int i=0;i<8;i++)cv[i]=r32(&r);}
      u32 a,b,c,d;gate(cv[0],&a,&b,&c,&d);va[k]=a;v9[k]=b;vp[k]=c;vq[k]=d; }
    printf("kind %d (0=real F38(IV,M0) 1=extra free block F38(F38(IV,M0*),X) 2=uniform A_-1) seed %llu 2^%d CVs, %.0fs\n",kind,(unsigned long long)seed,lg,omp_get_wtime()-t0);
    stats("g_all (all G variants)",va,N); stats("g_90 (variants of the 90 filed classes)",v9,N); stats("classes passing F7",vp,N); stats("of the 90 classes passing F7",vq,N);
    printf("exact E[g_all]=%.3f  E[classes passing]=%.3f (|F7|/2^32=%.6f)\n",(double)nG*pF7,(double)nCls*pF7,pF7);
    char fn[64];sprintf(fn,"gd_k%d_s%llu.bin",kind,(unsigned long long)seed);FILE*f=fopen(fn,"wb");fwrite(va,4,N,f);fclose(f);
    return 0; }
  return 0;
}
