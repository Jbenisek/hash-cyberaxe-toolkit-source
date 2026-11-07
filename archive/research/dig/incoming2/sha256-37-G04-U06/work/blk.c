// own code, G04-U06 scan: CV / first block / padding layout of the ordinary collision (sha256-37).
// uses common.h (own SHA-256 trace + chi37 parser, copied from retest/dense_boring) and chi37.txt (copy).
// modes: val | lens | build | gdist KIND LOG2N SEED | iv | ivcheck
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
// ---- xoshiro-ish rng
typedef struct{u64 s;}Rng; static inline u64 nx(Rng*r){u64 z=(r->s+=0x9e3779b97f4a7c15ull);z=(z^(z>>30))*0xbf58476d1ce4e5b9ull;z=(z^(z>>27))*0x94d049bb133111ebull;return z^(z>>31);}
static inline u32 r32(Rng*r){return (u32)nx(r);}
// ---- published rows
static u32 PA[18],PE[18]; // row i+4
static const u32 d6=0x20000000,t6=0x03c00800,d7=0xfbc00800,t7=0x017f8000;
static inline int fs6(u32 w){return (u32)(s0(w+d6)-s0(w))==t6;}
static inline int fs7(u32 w){return (u32)(s0(w+d7)-s0(w))==t7;}
#define PAr(i) PA[(i)+4]
// reference: words W0..W7 from cv and a0 following the job5 words_from_cv logic (independent of closed forms)
static void ref_words(const u32 cv[8],u32 a0,u32*W){
  u32 A[18],E[18]; memcpy(A,PA,sizeof A); memcpy(E,PE,sizeof E);
  for(int i=0;i<4;i++){A[3-i]=cv[i];E[3-i]=cv[4+i];}
  A[4]=a0; for(int i=0;i<=7;i++)E[i+4]=A[i+4]+A[i]-S0(A[i+3])-MAJ(A[i+3],A[i+2],A[i+1]);
  for(int i=0;i<=7;i++)W[i]=E[i+4]-A[i]-E[i]-S1(E[i+3])-CH(E[i+3],E[i+2],E[i+1])-K[i];
}
static inline u32 c7of(u32 a0){
  u32 A1=PAr(1),A2=PAr(2),A3=PAr(3),A4=PAr(4),A5=PAr(5),A6=PAr(6),A7=PAr(7),E5=PE[5+4],E6=PE[6+4];
  u32 E4=A4+a0-S0(A3)-MAJ(A3,A2,A1);
  return A7-S0(A6)-MAJ(A6,A5,A4)-(A3-S0(A2)-MAJ(A2,A1,a0))-S1(E6)-CH(E6,E5,E4)-K[7];
}
static inline u32 w6of(u32 a0,u32 Am1,u32 Am2){
  u32 A1=PAr(1),A2=PAr(2),A3=PAr(3),A4=PAr(4),A5=PAr(5),A6=PAr(6),E5=PE[5+4];
  u32 E2=A2+Am2-S0(A1)-MAJ(A1,a0,Am1), E3=A3+Am1-S0(A2)-MAJ(A2,A1,a0), E4=A4+a0-S0(A3)-MAJ(A3,A2,A1);
  return A6-S0(A5)-MAJ(A5,A4,A3)-E2-S1(E5)-CH(E5,E4,E3)-K[6];
}
// ---- G build
static u32 *Ga0,*Gc7; static long nG; static u32 *clsStart; static long nCls; static u32 C4g;
static int cmp64(const void*a,const void*b){u64 x=*(u64*)a,y=*(u64*)b;return x<y?-1:x>y;}
static void loadpub(void){
  load_chi("chi37.txt"); Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  for(int i=-4;i<=13;i++){PA[i+4]=AA(&X,i);PE[i+4]=EE(&X,i);}
}
static void build_G(void){
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  u32 A1=AA(&X,1),A2=AA(&X,2),A3=AA(&X,3),A4=AA(&X,4),E5=EE(&X,5),E6=EE(&X,6),E7=EE(&X,7),E8=EE(&X,8);
  u32 C4=A4-S0(A3)-MAJ(A3,A2,A1), W8C=E8-A4-S1(E7)-CH(E7,E6,E5)-K[8]; C4g=C4;
  int nw8=0, wb[8][2]; char wop[8];
  for(int k=0;k<NX2;k++){char op[4];int ia,ba,ib,bb;char na,nb; sscanf(X2[k],"%c%d[%d] %2s %c%d[%d]",&na,&ia,&ba,op,&nb,&ib,&bb); if(na=='W'&&ia==8){wb[nw8][0]=ba;wb[nw8][1]=bb;wop[nw8]=op[0]=='=';nw8++;}}
  u32 dW8=Y.W[8]-X.W[8];
  u64 *tmp=malloc(sizeof(u64)*13000000); long n=0;
  for(u32 E4=0;E4<(1u<<29);E4++){
    u32 w8=W8C-E4,w8y=w8+dW8; if(!wordok(2,8,w8,w8y))continue;
    int two=1; for(int k=0;k<nw8;k++) if((B(w8,wb[k][0])==B(w8,wb[k][1]))!=wop[k]) two=0;
    if(!two)continue; u32 a0=E4-C4; tmp[n++]=((u64)c7of(a0)<<32)|a0; }
  qsort(tmp,n,8,cmp64); nG=n; Ga0=malloc(4*n); Gc7=malloc(4*n);
  for(long i=0;i<n;i++){Ga0[i]=(u32)tmp[i];Gc7[i]=(u32)(tmp[i]>>32);} free(tmp);
  clsStart=malloc(4*(n+2)); long nc=0; for(long i=0;i<n;i++) if(i==0||Gc7[i]!=Gc7[i-1]) clsStart[nc++]=(u32)i; clsStart[nc]=(u32)n; nCls=nc;
  printf("G built: %ld variants, %ld c7 classes (own enumeration, E4[31:29]=000, W8 cell + two-bit conds)\n",nG,nc);
  // cross-check c7of against closed form of f67g.c
  u32 c7c=E7-2*A3+S0(A2)-S1(E6)-K[7]; long bad=0; for(long i=0;i<n;i+=97){u32 a0=Ga0[i],E4=a0+C4; if(Gc7[i]!=c7c+MAJ(A2,A1,a0)-CH(E6,E5,E4)-0) bad++; }
  printf("c7 closed-form cross-check (f67g form) mismatches: %ld\n",bad);
}
static void save_G(void){FILE*f=fopen("G.bin","wb");fwrite(&nG,8,1,f);fwrite(&nCls,8,1,f);fwrite(&C4g,4,1,f);fwrite(Ga0,4,nG,f);fwrite(Gc7,4,nG,f);fwrite(clsStart,4,nCls+1,f);fclose(f);}
static int load_G(void){FILE*f=fopen("G.bin","rb");if(!f)return 0;fread(&nG,8,1,f);fread(&nCls,8,1,f);fread(&C4g,4,1,f);Ga0=malloc(4*nG);Gc7=malloc(4*nG);clsStart=malloc(4*(nCls+1));fread(Ga0,4,nG,f);fread(Gc7,4,nG,f);fread(clsStart,4,nCls+1,f);fclose(f);return 1;}
// ---- gate count for one CV: returns g_all, g_222 (classes with >=3456 variants), nclsPass
static void gate(u32 Am1,u32 Am2,u32*gall,u32*g222,u32*ncp){
  u32 ga=0,g2=0,np=0;
  for(long c=0;c<nCls;c++){ u32 x=Gc7[clsStart[c]]-Am1; if(!fs7(x))continue; np++;
    u32 lo=clsStart[c],hi=clsStart[c+1],big=(hi-lo)>=3456, loc=0;
    for(u32 i=lo;i<hi;i++) loc+=fs6(w6of(Ga0[i],Am1,Am2));
    ga+=loc; if(big)g2+=loc; }
  *gall=ga;*g222=g2;*ncp=np;
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
    // (1) tool check: 64-step chain on a 128-byte message vs python hashlib (printed; compared outside)
    u32 m0[16],m1[16],pb[16],cv[8],cv2[8],o[8]; unsigned char by[128]; for(int i=0;i<128;i++)by[i]=(unsigned char)((i*7+3)&255);
    for(int i=0;i<16;i++){m0[i]=(u32)by[4*i]<<24|by[4*i+1]<<16|by[4*i+2]<<8|by[4*i+3]; m1[i]=(u32)by[64+4*i]<<24|by[64+4*i+1]<<16|by[64+4*i+2]<<8|by[64+4*i+3];}
    padblock(128,pb); compress(IV,m0,64,cv); compress(cv,m1,64,cv2); compress(cv2,pb,64,o); pr("SHA256_64step_128B_own=",o);
    // (2) published pair, 37 steps, block 2 under the printed CV, then equal padding block
    u32 ox[8],oy[8],px[8],py[8]; compress(CV,MX,37,ox); compress(CV,MY,37,oy); pr("blk2 x digest=",ox); pr("blk2 y digest=",oy);
    padblock(128,pb); compress(ox,pb,37,px); compress(oy,pb,37,py); pr("blk3 x digest=",px); pr("blk3 y digest=",py);
    printf("blk2 equal=%d blk3 equal=%d\n",!memcmp(ox,oy,32),!memcmp(px,py,32));
    printf("pad block words: W0=%08x W1..W13=0 W14=%08x W15=%08x\n",pb[0],pb[14],pb[15]);
    printf("published dW (y-x): ");for(int i=0;i<16;i++)printf("%d:%08x ",i,MY[i]-MX[i]);printf("\n");
    return 0; }
  if(!strcmp(mode,"lens")){
    u32 rq14=MY[14]-MX[14], rq15=MY[15]-MX[15]; printf("required dW14=%08x dW15=%08x (nonzero)\n",rq14,rq15);
    // padding inside the colliding block: tail t bytes (0..55) after a data prefix of 64k bytes; W14=bits_hi, W15=bits_lo
    // sweep total lengths L,L' (bytes) of the two members for 1..2 data blocks with padding in the second/first block
    long pairs=0,ok=0,okdw=0;
    for(int L=0;L<=119;L++) for(int Lp=0;Lp<=119;Lp++){
      int blkL=(L+9+63)/64, blkLp=(Lp+9+63)/64; // number of padded blocks
      // the characteristic block is the LAST block of each member; its W14,W15 are the length words only when the member has L%64<=55
      if(L%64>55||Lp%64>55) continue; // padding spills into another block
      pairs++; u32 d14=0,d15=(u32)(8*Lp)-(u32)(8*L); // high words are 0 for L<2^29
      if(d14==rq14&&d15==rq15)okdw++; if(L==Lp)ok++; }
    printf("member length pairs (L,L') in 0..119 bytes with padding inside the final block: %ld ; pairs with dW14,dW15 equal to the required values: %ld ; equal-length pairs (dW14=dW15=0): %ld\n",pairs,okdw,ok);
    printf("max |dW15| reachable by length difference (bytes<=119): %u bits vs required %u\n",8*119,rq15);
    return 0; }
  if(!strcmp(mode,"padcorr")){
    // can the equal padding block (block 3) absorb a small chaining-value difference? XOR weight<=2 and +-1 per-word differences, random CV2
    u32 pb[16]; padblock(128,pb); Rng r={777}; long ntest=0,coll=0; int minw=999; double sumw=0; long nw=0; long hist[257]={0};
    int nsamp=atoi(argv[2]);
    for(int s=0;s<nsamp;s++){ u32 cv[8]; for(int i=0;i<8;i++)cv[i]=r32(&r); u32 o[8]; compress(cv,pb,37,o);
      for(int a=0;a<256;a++) for(int b=a;b<256;b++){ u32 c2[8],o2[8]; memcpy(c2,cv,32); c2[a>>5]^=1u<<(a&31); if(b!=a)c2[b>>5]^=1u<<(b&31);
        compress(c2,pb,37,o2); int w=0; for(int i=0;i<8;i++) w+=__builtin_popcount(o[i]^o2[i]); ntest++; if(w==0)coll++; if(w<minw)minw=w; sumw+=w; nw++; hist[w]++; } 
      for(int i=0;i<8;i++){ for(int sg=0;sg<2;sg++){ u32 c2[8],o2[8]; memcpy(c2,cv,32); c2[i]+= sg?1u:0xffffffffu; compress(c2,pb,37,o2); int w=0; for(int k=0;k<8;k++)w+=__builtin_popcount(o[k]^o2[k]); ntest++; if(w==0)coll++; if(w<minw)minw=w; sumw+=w; nw++; hist[w]++; } } }
    printf("padblock correction test: %ld (CV2,dCV2) tests (XOR weight 1-2: 32896 diffs, +-1 per word: 16 diffs, per CV2 sample), output-equal: %ld, min output XOR weight %d, mean %.2f of 256\n",ntest,coll,minw,sumw/nw);
    return 0; }
  if(!strcmp(mode,"build")){build_G();save_G();return 0;}
  if(!load_G()){printf("no G.bin\n");return 1;}
  if(!strcmp(mode,"ivcheck")){
    // known-answer: closed forms vs reference on published pair and random
    Tr X; trace(CV,MX,&X); u32 W[8]; ref_words(CV,AA(&X,0),W);
    printf("published a0=%08x ref W6=%08x W7=%08x pub W6=%08x W7=%08x ; closed W6=%08x W7=%08x(c7-A_-1)\n",AA(&X,0),W[6],W[7],X.W[6],X.W[7],w6of(AA(&X,0),CV[0],CV[1]),c7of(AA(&X,0))-CV[0]);
    Rng r={12345}; long bad=0,N=2000000; for(long k=0;k<N;k++){u32 cv[8];for(int i=0;i<8;i++)cv[i]=r32(&r);u32 a0=Ga0[nx(&r)%nG];ref_words(cv,a0,W); if(W[6]!=w6of(a0,cv[0],cv[1])||W[7]!=c7of(a0)-cv[0])bad++;}
    printf("closed form vs ref_words on %ld random (cv,a0 in G): mismatches %ld\n",N,bad);
    // other CV words do not matter for the gate
    bad=0; for(long k=0;k<200000;k++){u32 cv[8],cw[8];for(int i=0;i<8;i++)cv[i]=r32(&r);memcpy(cw,cv,32);for(int i=2;i<8;i++)cw[i]=r32(&r);u32 a0=Ga0[nx(&r)%nG],W2[8];ref_words(cv,a0,W);ref_words(cw,a0,W2);if(W[6]!=W2[6]||W[7]!=W2[7])bad++;}
    printf("W6/W7 change when CV words 2..7 are redrawn: %ld of 200000\n",bad);
    return 0; }
  if(!strcmp(mode,"iv")){
    u32 ga,g2,np; gate(IV[0],IV[1],&ga,&g2,&np);
    printf("g(IV): g_all=%u g_222=%u classes passing F7=%u (mean g_all=%.2f mean g_222=%.2f)\n",ga,g2,np,
      (double)nG*(68157440.0/4294967296.0)*(287309824.0/4294967296.0),0.0);
    return 0; }
  if(!strcmp(mode,"gdist")){
    int kind=atoi(argv[2]); int lg=atoi(argv[3]); u64 seed=strtoull(argv[4],0,10); long N=1l<<lg; omp_set_num_threads(2);
    u32*va=malloc(4*N),*v2=malloc(4*N),*vp=malloc(4*N); double t0=omp_get_wtime();
    Rng r0={seed}; u32 m0s[16]; for(int i=0;i<16;i++)m0s[i]=r32(&r0); u32 cv0[8]; compress(IV,m0s,37,cv0);
    #pragma omp parallel for schedule(dynamic,64)
    for(long k=0;k<N;k++){ Rng r={seed*0x100000001b3ull+(u64)k*0x9e3779b97f4a7c15ull+7}; u32 cv[8],m[16];
      if(kind==0){for(int i=0;i<16;i++)m[i]=r32(&r);compress(IV,m,37,cv);}
      else if(kind==1){for(int i=0;i<16;i++)m[i]=r32(&r);compress(cv0,m,37,cv);}
      else {for(int i=0;i<8;i++)cv[i]=r32(&r);}
      u32 a,b,c;gate(cv[0],cv[1],&a,&b,&c);va[k]=a;v2[k]=b;vp[k]=c; }
    printf("kind %d (0=real F37(IV,M0) 1=extra free block F37(F37(IV,M0*),X) 2=uniform A_-1,A_-2) seed %llu 2^%d CVs, %.0fs\n",kind,(unsigned long long)seed,lg,omp_get_wtime()-t0);
    stats("g_all (all 12,103,680 variants)",va,N); stats("g_222 (classes>=3456, 782,800 variants)",v2,N); stats("classes passing F7",vp,N);
    printf("exact E[g_all]=%.3f  exact E[classes passing]=%.3f\n",(double)nG*(68157440.0/4294967296.0)*(287309824.0/4294967296.0),(double)nCls*(68157440.0/4294967296.0));
    // dump for two-sample tests
    char fn[64];sprintf(fn,"gd_k%d_s%llu.bin",kind,(unsigned long long)seed);FILE*f=fopen(fn,"wb");fwrite(va,4,N,f);fclose(f);
    return 0; }
  return 0;
}
