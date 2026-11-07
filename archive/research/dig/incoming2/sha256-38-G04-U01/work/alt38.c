// G04-U01 (sha256-38) A-1 Q4: alternatives for the class gate x. Own code, uses common.h (own trace + chi38 parser).
#include "common.h"
#include <omp.h>
typedef struct { u32 c7,a0; } pr;
static int cmp(const void*a,const void*b){ const pr*x=a,*y=b; if(x->c7!=y->c7) return x->c7<y->c7?-1:1; return x->a0<y->a0?-1:(x->a0>y->a0); }
static u32 A1_,A2_,A3_,A4_,E5_,E6x_,E6y_,E7x_,E7y_,E8x_,C4_,W8C_,DW8_;
static u32 c7of(u32 a0){ u32 e4=a0+C4_; return E7x_ - 2*A3_ + S0(A2_) + MAJ(A2_,A1_,a0) - S1(E6x_) - CH(E6x_,E5_,e4) - K[7]; }
// W7x as a function of (a0,x=A_-1) from the lemma: W7 = E7 - A3 - E3 - S1(E6) - CH(E6,E5,E4) - K7, E3 = A3 + A_-1 - S0(A2) - MAJ(A2,A1,A0)
static u32 w7(u32 E7,u32 E6,u32 a0,u32 x){ u32 e4=a0+C4_; u32 E3=A3_+x-S0(A2_)-MAJ(A2_,A1_,a0); return E7-A3_-E3-S1(E6)-CH(E6,E5_,e4)-K[7]; }
static u64 rs=0x9E3779B97F4A7C15ULL; static inline u32 rnd(){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (u32)(rs>>16);}
static void runs(const char*name,pr*v,u64 n){
  qsort(v,n,sizeof(pr),cmp);
  u64 nr=0,i=0; u32 maxsz=0; u64 hist[8192]; memset(hist,0,sizeof hist); u64 ge1000=0, var_in_ge3840=0;
  while(i<n){u64 j=i; while(j<n&&v[j].c7==v[i].c7)j++; u32 sz=(u32)(j-i); nr++; if(sz<8192)hist[sz]++; if(sz>maxsz)maxsz=sz; i=j;}
  u64 sum_sz2=0; i=0; while(i<n){u64 j=i; while(j<n&&v[j].c7==v[i].c7)j++; u64 sz=j-i; sum_sz2+=sz*sz; i=j;}
  u64 bigs=0,bigvars=0; for(int s=1;s<8192;s++) if(s>=3840){bigs+=hist[s]; bigvars+=hist[s]*(u64)s;}
  printf("%s: members %llu, distinct c7 %llu, max class size %u, classes of size>=3840 %llu (=%llu variants), size 3840: %llu, sum size^2 %llu\n",name,(unsigned long long)n,(unsigned long long)nr,maxsz,(unsigned long long)bigs,(unsigned long long)bigvars,(unsigned long long)hist[3840],(unsigned long long)sum_sz2);
  (void)ge1000;(void)var_in_ge3840;
}
int main(){
  load_chi("./research/tools/traillab/chi/chi38.txt");
  Tr X,Y; trace(CV,MX,&X); trace(CV,MY,&Y);
  A1_=AA(&X,1);A2_=AA(&X,2);A3_=AA(&X,3);A4_=AA(&X,4);E5_=EE(&X,5);E6x_=EE(&X,6);E6y_=EE(&Y,6);E7x_=EE(&X,7);E7y_=EE(&Y,7);E8x_=EE(&X,8);
  u32 a0pub=AA(&X,0);
  C4_=A4_-S0(A3_)-MAJ(A3_,A2_,A1_); W8C_=E8x_-A4_-S1(E7x_)-CH(E7x_,E6x_,E5_)-K[8]; DW8_=MY[8]-MX[8];
  u32 T8=s0(MY[8])-s0(MX[8]);
  printf("pub a0=%08x C4=%08x (E4 check %08x) W8C=%08x (W8x pub %08x) dW8=%08x T8(ds0 W8)=%08x c7(pub)=%08x ; W7x pub + A_-1 pub = %08x\n",a0pub,C4_,EE(&X,4),W8C_,MX[8],DW8_,T8,c7of(a0pub),MX[7]+CV[0]);
  // d7 independence of a0 / A_-1 via the lemma formula, random samples, both members (E4,E5,E6 equal in both members)
  int d7bad=0; u32 d7ref=MY[7]-MX[7]; for(int k=0;k<2000000;k++){ u32 a0=rnd()^(rnd()<<16), x=rnd()^(rnd()<<16); u32 d=w7(E7y_,E6y_,a0,x)-w7(E7x_,E6x_,a0,x); if(d!=d7ref)d7bad++; }
  printf("d7 = W7y-W7x over 2e6 random (a0,A_-1): %08x each time? bad=%d ; E4,E5,E6 equal both members: %d\n",d7ref,d7bad,(EE(&X,4)==EE(&Y,4))&&(E5_==EE(&Y,5))&&(E6x_==E6y_));
  // pass 1: counts
  u64 nG=0,nGp=0,nGp_notG=0,nPub=0;
  #pragma omp parallel for reduction(+:nG,nGp,nGp_notG) schedule(static) num_threads(2)
  for(long long a=0;a<(1LL<<32);a++){ u32 a0=(u32)a, w=W8C_-(a0+C4_), y=w+DW8_;
    int mod=((s0(y)-s0(w))==T8);
    int g=0; if(mod||1){ g=wordok(2,8,w,y)&&(((w>>0)&1)!=((w>>28)&1))&&(((w>>30)&1)!=((w>>9)&1))&&(((w>>1)&1)==((w>>18)&1)); }
    nGp+=mod; nG+=g; nGp_notG+=(mod&&!g);
  }
  (void)nPub;
  printf("|G| (W8 cell + 3 two-bit conds) = %llu (2^26 = %u) ; G' (modular s0(W8y)-s0(W8x)=T8 only) = %llu = %.4f x |G| ; G' minus G = %llu\n",(unsigned long long)nG,1u<<26,(unsigned long long)nGp,(double)nGp/(double)nG,(unsigned long long)nGp_notG);
  pr *vg=malloc(sizeof(pr)*(nG+1)), *vp=malloc(sizeof(pr)*(nGp+1)); u64 ig=0,ip=0;
  for(long long a=0;a<(1LL<<32);a++){ u32 a0=(u32)a, w=W8C_-(a0+C4_), y=w+DW8_;
    int mod=((s0(y)-s0(w))==T8); if(!mod && !(wordok(2,8,w,y))) continue;
    int g=wordok(2,8,w,y)&&(((w>>0)&1)!=((w>>28)&1))&&(((w>>30)&1)!=((w>>9)&1))&&(((w>>1)&1)==((w>>18)&1));
    if(g){ vg[ig].c7=c7of(a0); vg[ig].a0=a0; ig++; }
    if(mod){ vp[ip].c7=c7of(a0); vp[ip].a0=a0; ip++; }
  }
  runs("G ",vg,ig); runs("G'",vp,ip);
  // alternative gate values: histogram of s0(w+d7)-s0(w) over all 2^32 w (t7 is the printed one)
  u32 d7=d7ref; enum{HS=1<<16}; u32 hk[HS]; u64 hc[HS]; memset(hc,0,sizeof hc); int used=0;
  for(long long ww=0;ww<(1LL<<32);ww++){ u32 w=(u32)ww, t=s0(w+d7)-s0(w); u32 h=(t*2654435761u)>>16; while(hc[h]&&hk[h]!=t) h=(h+1)&(HS-1); if(!hc[h]){hk[h]=t;used++;} hc[h]++; }
  printf("alternative t (s0(w+%08x)-s0(w)) histogram over all 2^32 w: %d distinct values; top 8:\n",d7,used);
  for(int r=0;r<8;r++){ int bi=-1; u64 bc=0; for(int h=0;h<HS;h++) if(hc[h]>bc){bc=hc[h];bi=h;} if(bi<0)break; printf("  t=%08x count %llu = 2^%.4f%s\n",hk[bi],(unsigned long long)bc,__builtin_log2((double)bc),hk[bi]==0x03bff800u?"  <== printed t7":""); hc[bi]=0; }
  return 0;}
