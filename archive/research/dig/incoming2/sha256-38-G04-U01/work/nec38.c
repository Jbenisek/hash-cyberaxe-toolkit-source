// G04-U01 (sha256-38) validation + A-1 Q2 + A-2 W6-gate test. Own code.
#include "common.h"
#include <omp.h>
static u64 rs=88172645463325252ULL; static inline u32 rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (u32)(rs>>16);}
static void sched(const u32*m,u32*W){for(int i=0;i<16;i++)W[i]=m[i];for(int i=16;i<38;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];}
int main(int argc,char**argv){
  load_chi("./research/tools/traillab/chi/chi38.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  // VALIDATION on the published pair: digest, all A/E/W cells rows -4..37, W7 in F7
  int dg=1; u32 fin[8]={AA(&X,37),AA(&X,36),AA(&X,35),AA(&X,34),EE(&X,37),EE(&X,36),EE(&X,35),EE(&X,34)}, finy[8]={AA(&Y,37),AA(&Y,36),AA(&Y,35),AA(&Y,34),EE(&Y,37),EE(&Y,36),EE(&Y,35),EE(&Y,34)};
  for(int k=0;k<8;k++){ if(CV[k]+fin[k]!=DIG[k]||CV[k]+finy[k]!=DIG[k]) dg=0; }
  printf("VAL digest x==y==printed: %d\n",dg);
  int badcell=0; for(int i=-4;i<38;i++){ if(!wordok(0,i,AA(&X,i),AA(&Y,i)))badcell++; if(!wordok(1,i,EE(&X,i),EE(&Y,i)))badcell++; if(i>=0&&!wordok(2,i,X.W[i],Y.W[i]))badcell++; }
  printf("VAL cell failures over A,E rows -4..37, W rows 0..37 (W7 cell included): %d\n",badcell);
  u32 d6=MY[6]-MX[6], d7=MY[7]-MX[7];
  u32 Wx[38],Wy[38]; sched(MX,Wx); sched(MY,Wy);
  u32 dW15=MY[15]-MX[15], D22=Wy[22]-Wx[22];
  u32 t7=D22-dW15-d6;   // required s0(W7+d7)-s0(W7) given dW20=0, dW6=d6
  printf("pair: d6=%08x d7=%08x dW14=%08x dW15=%08x dW22=%08x -> t7=%08x ; W16..W23 diffs:",d6,d7,MY[14]-MX[14],dW15,D22,t7);
  for(int i=16;i<24;i++)printf(" %08x",Wy[i]-Wx[i]); printf("\n");
  int pin=((s0(MX[7]+d7)-s0(MX[7]))==t7); printf("VAL published W7x in F7: %d ; W7x=%08x W7[29]=%d\n",pin,MX[7],(MX[7]>>29)&1);
  // exhaustive over w=W7x: schedule role of W22 (W6 equal both: d6=0)
  u64 cdef=0,crole=0,mis=0,cdef29=0;
  #pragma omp parallel for reduction(+:cdef,crole,mis,cdef29) schedule(static) num_threads(2)
  for(long long ww=0; ww<(1LL<<32); ww++){ u32 w=(u32)ww;
    int a=((s0(w+d7)-s0(w))==t7);
    u32 w22x=s1(Wx[20])+MX[15]+s0(w)+MX[6], w22y=s1(Wy[20])+MY[15]+s0(w+d7)+MY[6];
    int b=(w22x==w22y);
    cdef+=a; crole+=b; mis+=(a!=b); cdef29+=(a&&!((w>>29)&1));
  }
  printf("EXH |F7| by definition %llu ; #w with W22x==W22y (pair W20,W15,W6) %llu ; mismatches %llu ; F7 with w29=0 (W7 cell n at bit 29) %llu\n",(unsigned long long)cdef,(unsigned long long)crole,(unsigned long long)mis,(unsigned long long)cdef29);
  // exhaustive over w=W6x: W21 and W22 equality (A_-2 gate analogue): d6=0
  u64 e21=0,e22=0;
  #pragma omp parallel for reduction(+:e21,e22) schedule(static) num_threads(2)
  for(long long ww=0; ww<(1LL<<32); ww++){ u32 w=(u32)ww;
    u32 w21x=s1(Wx[19])+MX[14]+s0(w)+MX[5], w21y=s1(Wy[19])+MY[14]+s0(w+d6)+MY[5];
    u32 w22x=s1(Wx[20])+MX[15]+s0(MX[7])+w, w22y=s1(Wy[20])+MY[15]+s0(MY[7])+w+d6;
    e21+=(w21x==w21y); e22+=(w22x==w22y);
  }
  printf("EXH over all 2^32 W6 (both members W6, W6+d6 with d6=%08x): W21x==W21y %llu ; W22x==W22y %llu\n",d6,(unsigned long long)e21,(unsigned long long)e22);
  // sample: W16..W21 = pair's x values (inverse expansion for W0..W5), W6,W7 uniform, W8..W15 pair
  long long N=argc>1?atoll(argv[1]):20000000LL;
  u64 n=0,in7=0,w22d=0,w22c=0,allc=0,notin7_c22=0,notin7=0,in7_c22=0,in7_allc=0,in7_w7cell=0,notin7_allc=0,w16_21eq=0, w23c=0,in7_w23c=0;
  for(long long k=0;k<N;k++){
    u32 m[16],my[16]; m[6]=rnd()^(rnd()<<16); m[7]=rnd()^(rnd()<<16); for(int i=8;i<16;i++)m[i]=MX[i];
    // inverse expansion
    m[5]=Wx[21]-s1(Wx[19])-m[14]-s0(m[6]);
    m[4]=Wx[20]-s1(Wx[18])-m[13]-s0(m[5]);
    m[3]=Wx[19]-s1(Wx[17])-m[12]-s0(m[4]);
    m[2]=Wx[18]-s1(Wx[16])-m[11]-s0(m[3]);
    m[1]=Wx[17]-s1(m[15])-m[10]-s0(m[2]);
    m[0]=Wx[16]-s1(m[14])-m[9]-s0(m[1]);
    for(int i=0;i<16;i++)my[i]=m[i]; my[6]=m[6]+d6; my[7]=m[7]+d7; for(int i=8;i<16;i++)my[i]=MY[i];
    u32 a[38],b[38]; sched(m,a); sched(my,b);
    int e=1; for(int i=16;i<22;i++) if(a[i]!=Wx[i]||b[i]!=Wy[i]) e=0; w16_21eq+=e;
    int i7=((s0(m[7]+d7)-s0(m[7]))==t7);
    int d22=((b[22]-a[22])==D22);
    int c22=wordok(2,22,a[22],b[22]);
    int c16_22=1; for(int i=16;i<=22;i++) if(!wordok(2,i,a[i],b[i])) c16_22=0;
    int c23=wordok(2,23,a[23],b[23]);
    n++; in7+=i7; w22d+=d22; w22c+=c22; allc+=c16_22; w23c+=c23;
    if(!i7){notin7++; notin7_c22+=c22; notin7_allc+=c16_22;} else {in7_c22+=c22; in7_allc+=c16_22; in7_w7cell+=wordok(2,7,m[7],my[7]); in7_w23c+=c23;}
  }
  printf("SAMPLE N=%llu (W6,W7 uniform; W16..W21 forced to the pair's values through W0..W5; W8..W15 pair; schedule W16..W37 recomputed forward from W0..W15 for both members): W16..W21 reproduce pair %llu ; W7x in F7 %llu ; dW22==pair %llu ; W22 cell %llu ; cells W16..W22 all %llu ; W23 cell %llu\n",(unsigned long long)n,(unsigned long long)w16_21eq,(unsigned long long)in7,(unsigned long long)w22d,(unsigned long long)w22c,(unsigned long long)allc,(unsigned long long)w23c);
  printf("not in F7: %llu samples -> W22 cell holds %llu, cells W16..W22 all hold %llu ; in F7: %llu samples -> W22 cell holds %llu, cells W16..W22 all hold %llu, W7 XOR cell holds %llu, W23 cell holds %llu\n",(unsigned long long)notin7,(unsigned long long)notin7_c22,(unsigned long long)notin7_allc,(unsigned long long)in7,(unsigned long long)in7_c22,(unsigned long long)in7_allc,(unsigned long long)in7_w7cell,(unsigned long long)in7_w23c);
  return 0;}
