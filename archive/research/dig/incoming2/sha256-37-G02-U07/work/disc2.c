#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include "consts.h"
typedef uint32_t u32;
static inline u32 ror(u32 x,int n){return (x>>n)|(x<<(32-n));}
static inline u32 S1(u32 x){return ror(x,6)^ror(x,11)^ror(x,25);}
static inline u32 CH(u32 x,u32 y,u32 z){return (x&y)^(~x&z);}
static inline u32 MAJ(u32 x,u32 y,u32 z){return (x&y)^(x&z)^(y&z);}
#define HB 15
typedef struct {u32 key,cnt;} S;           /* pass-1 slot: 8 bytes */
typedef struct {u32 key,first,orx,cnt;} A; /* pass-2 accumulator: 16 bytes */
static int inG(u32 e4,u32*c7o){u32 a0=e4-C4,w=W8C-e4;
 if(!(((w>>29)&1)==1&&((w>>1)&1)!=((w>>12)&1)&&((w>>8)&1)!=((w>>25)&1)&&((w>>14)&1)==((w>>18)&1)))return 0;
 *c7o=E7-A3-(K3C-MAJ(A2,A1,a0))-S1(E6)-CH(E6,E5,e4)-K7;return 1;}
int main(){
 size_t N=1u<<HB; S*t=calloc(N,sizeof(S)); /* key 0 reserved by cnt==0 */
 size_t b1=N*sizeof(S); u32 c7,distinct=0;
 for(u32 e4=0;e4<(1u<<29);e4++){ if(!inG(e4,&c7))continue;
  size_t h=(c7*2654435761u)>>(32-HB);
  while(t[h].cnt&&t[h].key!=c7)h=(h+1)&(N-1);
  if(!t[h].cnt)distinct++; t[h].key=c7;t[h].cnt++;}
 /* keep classes >=3456 */
 A*acc=calloc(300,sizeof(A)); int nc=0;
 for(size_t i=0;i<N;i++)if(t[i].cnt>=3456){acc[nc].key=t[i].key;acc[nc].cnt=0;nc++;}
 size_t b2=300*sizeof(A);
 free(t);
 for(u32 e4=0;e4<(1u<<29);e4++){ if(!inG(e4,&c7))continue;
  for(int k=0;k<nc;k++)if(acc[k].key==c7){u32 a0=e4-C4; if(!acc[k].cnt)acc[k].first=a0; acc[k].orx|=a0^acc[k].first; acc[k].cnt++;break;}}
 fprintf(stderr,"distinct=%u classes=%d pass1_alloc=%zu pass2_alloc=%zu\n",distinct,nc,b1,b2);
 for(int k=0;k<nc;k++)printf("%08x %u %08x %08x\n",acc[k].key,acc[k].cnt,acc[k].first,acc[k].orx);
 return 0;}
