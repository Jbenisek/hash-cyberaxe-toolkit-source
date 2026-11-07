// exhaustive 2^32 enumeration of w13 for the pinned call C3=G(3,7,11,15,w4,w13) on (X3,X7,X11,X15), w4=W4 vs W4'
#include <stdio.h>
#include <stdint.h>
typedef uint32_t u;
static u ror(u x,int r){return (x>>r)|(x<<(32-r));}
typedef struct{u a1,d1,c1,b1,a2,d2,c2,b2;} R;
static R g(u A,u B,u C,u D,u x,u y){R r;r.a1=A+B+x;r.d1=ror(D^r.a1,16);r.c1=C+r.d1;r.b1=ror(B^r.c1,12);r.a2=r.a1+r.b1+y;r.d2=ror(r.d1^r.a2,8);r.c2=r.c1+r.d2;r.b2=ror(r.b1^r.c2,7);return r;}
int main(){
 u X3=0x29d4fa98,X7=0xbee3af28,X11=0x44036000,X15=0x40c58500,W4=0x97475638,W4p=0x97475640,W13=0x0007c006;
 R t=g(X3,X7,X11,X15,W4,W13), s=g(X3,X7,X11,X15,W4p,W13);
 printf("check W13: A a2=%08x d2=%08x c2=%08x b2=%08x | B a2=%08x d2=%08x c2=%08x b2=%08x\n",t.a2,t.d2,t.c2,t.b2,s.a2,s.d2,s.c2,s.b2);
 unsigned long long nd=0,nb=0,ndb=0,ndb_top0=0,nd_top0=0,nb_top0=0,top0=0,ndb_ac_same=0;
 // list of first members of d&b set
 int listed=0;
 for(unsigned long long k=0;k<(1ULL<<32);k++){
  u w=(u)k; R p=g(X3,X7,X11,X15,W4,w), q=g(X3,X7,X11,X15,W4p,w);
  int d=(p.d2==q.d2), b=(p.b2==q.b2); int t0=((w>>24)==0);
  top0+=t0; nd+=d; nb+=b; ndb+=d&&b; if(d||b) printf("SET w13=%08x d=%d b=%d top0=%d\n",w,d,b,t0);
  if(t0){nd_top0+=d;nb_top0+=b;ndb_top0+=d&&b;}
  if(d&&b){ if(listed<64){printf("DB w13=%08x top0=%d  dA2=%08x dC2=%08x\n",w,t0,p.a2^q.a2,p.c2^q.c2);listed++;} if(p.a2==q.a2&&p.c2==q.c2)ndb_ac_same++; }
 }
 printf("TOTAL 2^32; d-equal=%llu b-equal=%llu both=%llu | top byte zero: %llu; d=%llu b=%llu both=%llu | both with a,c also equal(no diff)=%llu\n",nd,nb,ndb,top0,nd_top0,nb_top0,ndb_top0,ndb_ac_same);
 return 0;}
