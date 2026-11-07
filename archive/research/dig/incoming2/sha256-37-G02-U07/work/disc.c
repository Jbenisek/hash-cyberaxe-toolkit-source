#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "consts.h"
typedef uint32_t u32;
static inline u32 ror(u32 x,int n){return (x>>n)|(x<<(32-n));}
static inline u32 S1(u32 x){return ror(x,6)^ror(x,11)^ror(x,25);}
static inline u32 CH(u32 x,u32 y,u32 z){return (x&y)^(~x&z);}
static inline u32 MAJ(u32 x,u32 y,u32 z){return (x&y)^(x&z)^(y&z);}
#define HB 25
int main(){
  size_t N=1u<<HB; u32*key=calloc(N,4),*cnt=calloc(N,4); char*used=calloc(N,1);
  uint64_t g=0,distinct=0;
  for(u32 e4=0;e4<(1u<<29);e4++){
    u32 a0=e4-C4; u32 w=W8C-e4;
    if(!(((w>>29)&1)==1 && ((w>>1)&1)!=((w>>12)&1) && ((w>>8)&1)!=((w>>25)&1) && ((w>>14)&1)==((w>>18)&1))) continue;
    g++;
    u32 k3=K3C-MAJ(A2,A1,a0);
    u32 c7=E7-A3-k3-S1(E6)-CH(E6,E5,e4)-K7;
    size_t h=(c7*2654435761u)>>(32-HB);
    while(used[h]&&key[h]!=c7)h=(h+1)&(N-1);
    if(!used[h]){used[h]=1;key[h]=c7;distinct++;}
    cnt[h]++;
  }
  uint64_t ge=0,cls=0,mem=0,mx=0; 
  for(size_t i=0;i<N;i++) if(used[i]){ if(cnt[i]>=3456){cls++;mem+=cnt[i];} if(cnt[i]>mx)mx=cnt[i]; }
  printf("G=%llu distinct_c7=%llu classes>=3456=%llu members_in_classes=%llu max_class=%llu\n",(unsigned long long)g,(unsigned long long)distinct,(unsigned long long)cls,(unsigned long long)mem,(unsigned long long)mx);
  return 0;}
