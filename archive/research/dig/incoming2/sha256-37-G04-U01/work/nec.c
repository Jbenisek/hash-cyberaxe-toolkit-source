// G04-U01 Q2: necessity of x in F7 and cb in F6, from the full schedule. Own code. Uses common.h (own SHA-256 trace + chi37 parser).
#include "common.h"
#include <omp.h>
static u64 rs=88172645463325252ULL; static inline u32 rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (u32)(rs>>16);}
static void sched(const u32*m,u32*W){for(int i=0;i<16;i++)W[i]=m[i];for(int i=16;i<25;i++)W[i]=s1(W[i-2])+W[i-7]+s0(W[i-15])+W[i-16];}
int main(int argc,char**argv){
  load_chi("./research/tools/traillab/chi/chi37.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  u32 d6=MY[6]-MX[6], d7=MY[7]-MX[7];
  u32 Wx[25],Wy[25]; sched(MX,Wx); sched(MY,Wy);
  u32 D22=Wy[22]-Wx[22], dW14=MY[14]-MX[14], dW15=MY[15]-MX[15];
  u32 t6=(u32)(0-dW14), t7=D22-dW15-d6;
  printf("pair: d6=%08x d7=%08x D22=%08x dW14=%08x dW15=%08x -> t6=%08x t7=%08x\n",d6,d7,D22,dW14,dW15,t6,t7);
  printf("pair W16..W24 equal? "); for(int i=16;i<25;i++) printf("%d:%08x ",i,Wy[i]-Wx[i]); printf("\n");
  // exhaustive: F6, F7 by definition and by the schedule role
  u64 c6=0,c7=0,mis6=0,mis7=0; 
  // role test: W21 diff as function of W6 (others = pair), W22 diff as function of W7 (others = pair)
  u32 base21x=s1(Wx[19])+MX[14]+MX[5], base21y=s1(Wy[19])+MY[14]+MY[5];
  u32 base22x=s1(Wx[20])+MX[15]+MX[6]+0, base22y=s1(Wy[20])+MY[15];
  (void)base22x;(void)base22y;
  #pragma omp parallel for reduction(+:c6,c7,mis6,mis7) schedule(static) num_threads(2)
  for(long long ww=0; ww<(1LL<<32); ww++){ u32 w=(u32)ww;
    // W21 = s1(W19)+W14+s0(W6)+W5 ; x has W6=w, y has W6=w+d6
    u32 w21x=s1(Wx[19])+MX[14]+s0(w)+MX[5], w21y=s1(Wy[19])+MY[14]+s0(w+d6)+MY[5];
    int a=(w21x==w21y); int a0=((s0(w+d6)-s0(w))==t6);
    // W22 = s1(W20)+W15+s0(W7)+W6 ; W6 pair values
    u32 w22x=s1(Wx[20])+MX[15]+s0(w)+MX[6], w22y=s1(Wy[20])+MY[15]+s0(w+d7)+MY[6];
    int b=((w22y-w22x)==D22); int b0=((s0(w+d7)-s0(w))==t7);
    c6+=a; c7+=b; mis6+=(a!=a0); mis7+=(b!=b0);
  }
  printf("EXH schedule-role: #w with W21x==W21y = %llu (def mismatches %llu) ; #w with dW22==D22 = %llu (def mismatches %llu)\n",(unsigned long long)c6,(unsigned long long)mis6,(unsigned long long)c7,(unsigned long long)mis7);
  // random full-pair sampling: all of W0..W7 uniform, W8..W15 as pair. Verify events vs F-membership and W23.
  long long N=argc>1?atoll(argv[1]):20000000LL;
  u32 mk7=0; // F7 membership by definition
  u64 n=0, ev21=0,ev22d=0,ev22c=0,ev23=0,eq1620=0, in6=0,in7=0, mm21=0,mm22=0, full=0, c22c_notd=0, notin7_ok23=0, notin7=0, notin6=0, notin6_ev21=0, notin7_ev22c=0, in7_ev22d=0;
  for(long long k=0;k<N;k++){
    u32 m[16],my[16]; for(int i=0;i<8;i++) m[i]=rnd()^(rnd()<<16); for(int i=8;i<16;i++) m[i]=MX[i];
    // half the samples: force W6x in F6-ish? no: uniform, tally by membership
    for(int i=0;i<16;i++) my[i]=m[i]; my[6]=m[6]+d6; my[7]=m[7]+d7; for(int i=8;i<16;i++) my[i]=MY[i];
    u32 a[25],b[25]; sched(m,a); sched(my,b);
    int e16=1; for(int i=16;i<21;i++) if(a[i]!=b[i]) e16=0;
    int i6=((s0(m[6]+d6)-s0(m[6]))==t6), i7=((s0(m[7]+d7)-s0(m[7]))==t7);
    int e21=(a[21]==b[21]), e22=((b[22]-a[22])==D22), e23=(a[23]==b[23]);
    // W22 full cell
    int c22=1; for(int bt=0;bt<32;bt++){ if(!cellok(sym(2,22,bt),(a[22]>>bt)&1,(b[22]>>bt)&1)) {c22=0;break;} }
    n++; ev21+=e21; ev22d+=e22; ev22c+=c22; ev23+=e23; eq1620+=e16; in6+=i6; in7+=i7; mm21+=(e21!=i6); mm22+=(e22!=i7);
    if(c22 && !e22) c22c_notd++;
    if(!i7){notin7++; notin7_ev22c+=c22;} else in7_ev22d+=e22;
    if(!i6){notin6++; notin6_ev21+=e21;}
    if(i6&&i7&&c22&&e23&&e21&&e16) full++;
  }
  printf("SAMPLE N=%llu (W0..W7 uniform, W8..W15 = pair): W16..W20 equal %llu ; W23 equal %llu ; in F6 %llu ; in F7 %llu ; W21 equal %llu ; dW22==D22 %llu ; W22 full cell %llu\n",(unsigned long long)n,(unsigned long long)eq1620,(unsigned long long)ev23,(unsigned long long)in6,(unsigned long long)in7,(unsigned long long)ev21,(unsigned long long)ev22d,(unsigned long long)ev22c);
  printf("mismatch (W21 equal != in F6) %llu ; (dW22==D22 != in F7) %llu ; W22 cell holding while dW22!=D22: %llu ; x notin F7 -> W22 cell holds: %llu of %llu ; w6 notin F6 -> W21 equal: %llu of %llu ; in F7 -> dW22 ok %llu of %llu\n",(unsigned long long)mm21,(unsigned long long)mm22,(unsigned long long)c22c_notd,(unsigned long long)notin7_ev22c,(unsigned long long)notin7,(unsigned long long)notin6_ev21,(unsigned long long)notin6,(unsigned long long)in7_ev22d,(unsigned long long)in7);
  printf("both gates and W16..W23 cells (W22 cell, W21, W23, W16..20) hold: %llu of %llu (expected p6*p7*P(W22 cell | dW22 ok))\n",(unsigned long long)full,(unsigned long long)n);
  return 0;}
