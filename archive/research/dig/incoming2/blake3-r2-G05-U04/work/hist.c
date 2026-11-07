#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
int main(){unsigned ds[3]={8,7,15};
 for(int k=0;k<3;k++){unsigned d=ds[k];long long keys[512];unsigned long long cnt[512];int n=0;
  for(unsigned long long a=0;a<(1ULL<<32);a++){long long D=(long long)(uint32_t)((uint32_t)a^d)-(long long)(uint32_t)a;
   int i;for(i=0;i<n;i++)if(keys[i]==D)break; if(i==n){keys[n]=D;cnt[n]=0;n++;} cnt[i]++;}
  printf("delta=%u distinct D=%d (2^popcount=%d):",d,n,1<<__builtin_popcount(d));
  for(int i=0;i<n;i++)printf(" %lld:%llu",keys[i],cnt[i]);printf("\n");}
 return 0;}
