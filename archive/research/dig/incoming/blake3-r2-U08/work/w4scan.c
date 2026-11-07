// U08: exhaustive scans over w4 (C3 pinned word) and w5 (K2 cancelling word). Own code, written from proof.md Sections 1-3.
#include <stdio.h>
#include <stdint.h>
typedef uint32_t u32;
static inline u32 ror(u32 x,int r){return (x>>r)|(x<<(32-r));}
typedef struct{u32 a1,d1,c1,b1,a2,d2,c2,b2;} Gr;
static inline Gr G(u32 A,u32 B,u32 C,u32 D,u32 x,u32 y){Gr r;
 r.a1=A+B+x; r.d1=ror(D^r.a1,16); r.c1=C+r.d1; r.b1=ror(B^r.c1,12);
 r.a2=r.a1+r.b1+y; r.d2=ror(r.d1^r.a2,8); r.c2=r.c1+r.d2; r.b2=ror(r.b1^r.c2,7); return r;}
#define X3 0x29d4fa98u
#define X7 0xbee3af28u
#define X11 0x44036000u
#define X15 0x40c58500u
#define W4 0x97475638u
#define W13 0x0007c006u
#define K (0x3c6ef372u+0x1f83d9abu)
int main(int argc,char**argv){
 // K = IV[2]+IV[6]
 u32 Kc=0x3c6ef372u+0x1f83d9abu; printf("K=%08x (expect 5bf2cd1d)\n",Kc);
 u32 W4p=((Kc+W4)^8u)-Kc; printf("W4'=%08x (expect 97475640)\n",W4p);
 Gr p=G(X3,X7,X11,X15,W4,W13), q=G(X3,X7,X11,X15,W4p,W13);
 printf("control W4 : a2=%08x d2=%08x c2=%08x b2=%08x\n",p.a2,p.d2,p.c2,p.b2);
 printf("control W4': a2=%08x d2=%08x c2=%08x b2=%08x\n",q.a2,q.d2,q.c2,q.b2);
 // (A) w4 over 2^32, w4' derived by K2 cancellation rule
 unsigned long long nd=0,nb=0,nboth=0,nplus=0,nminus=0,nbothplus=0,nbothminus=0;
 FILE*f=fopen("w4_solutions.txt","w");
 for(unsigned long long w=0;w<(1ULL<<32);w++){u32 w4=(u32)w; u32 w4p=((Kc+w4)^8u)-Kc;
   int plus = (u32)(w4p-w4)==8u; if(plus)nplus++; else nminus++;
   Gr a=G(X3,X7,X11,X15,w4,W13), b=G(X3,X7,X11,X15,w4p,W13);
   int ed=a.d2==b.d2, eb=a.b2==b.b2; nd+=ed; nb+=eb;
   if(ed&&eb){nboth++; if(plus)nbothplus++; else nbothminus++;
     fprintf(f,"w4=%08x w4p=%08x delta=%d Y3=%08x Y3p=%08x Y11=%08x Y11p=%08x\n",w4,w4p,plus?8:-8,a.a2,b.a2,a.c2,b.c2);}
 }
 fclose(f);
 printf("A: over all 2^32 w4 (w4' by rule): d2 equal %llu, b2 equal %llu, both %llu; delta=+8 count %llu, -8 count %llu; both&+8 %llu both&-8 %llu\n",nd,nb,nboth,nplus,nminus,nbothplus,nbothminus);
 // (B) w4 = W4 fixed, w4' over all 2^32
 unsigned long long md=0,mb=0,mboth=0; f=fopen("w4prime_solutions.txt","w");
 for(unsigned long long w=0;w<(1ULL<<32);w++){u32 w4p=(u32)w; Gr b=G(X3,X7,X11,X15,w4p,W13);
   int ed=p.d2==b.d2, eb=p.b2==b.b2; md+=ed; mb+=eb; if(ed&&eb){mboth++; fprintf(f,"w4p=%08x\n",w4p);} }
 fclose(f);
 printf("B: w4=W4 fixed, w4' over 2^32: d2 equal %llu, b2 equal %llu, both %llu\n",md,mb,mboth);
 // (C) K2 Lemma L: exhaustive over w5 for w4=W4: state after K2 for n=55 (w4,w5) vs n=63 (w4',w5')
 u32 IV2=0x3c6ef372u, IV6=0x1f83d9abu; unsigned long long bad=0;
 for(unsigned long long w=0;w<(1ULL<<32);w++){u32 w5=(u32)w; u32 w5p=w5+W4-W4p;
   Gr a=G(IV2,IV6,IV2,55,W4,w5), b=G(IV2,IV6,IV2,63,W4p,w5p);
   if(a.a2!=b.a2||a.b2!=b.b2||a.c2!=b.c2||a.d2!=b.d2) bad++; }
 printf("C: K2 Lemma L, w4=W4, all 2^32 w5: mismatches %llu\n",bad);
 // (D) necessity of w5' = w5+W4-W4': fixed w5=0x12345678, w5' over 2^32: count with equal K2 state
 u32 w5=0x12345678u; Gr a=G(IV2,IV6,IV2,55,W4,w5); unsigned long long eq=0,eqone=0;
 for(unsigned long long w=0;w<(1ULL<<32);w++){u32 w5p=(u32)w; Gr b=G(IV2,IV6,IV2,63,W4p,w5p);
   if(a.a2==b.a2&&a.b2==b.b2&&a.c2==b.c2&&a.d2==b.d2){eq++; if(w5p==w5+W4-W4p)eqone++;} }
 printf("D: K2 state equal for %llu of 2^32 w5' (of which the rule value: %llu)\n",eq,eqone);
 // (E) XOR-difference distribution of w5 ^ (w5-8), exact over 2^32
 static unsigned long long hist[40]; 
 for(unsigned long long w=0;w<(1ULL<<32);w++){u32 x=(u32)w; u32 d=x^(x-8u); int k=0; while(k<32 && !((d>>k)&1ULL<<0)){k++;} 
   // identify by top bit of d
   int t=31; while(t>=0&&!((d>>t)&1))t--; hist[t]++;}
 for(int t=0;t<32;t++) if(hist[t]) printf("E: topbit %2d  xor-diff %08x pattern count %llu\n",t,(t==31?0xfffffff8u:(u32)((2ULL<<t)-8)),hist[t]);
 return 0;}
