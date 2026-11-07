// Fact P scan, own code: pinned X3,X7,X11,X15,W13; count w4 with equal C3 b2,d2 for pair (w4,w4+delta)
#include <stdio.h>
#include <stdint.h>
typedef uint32_t u;
static inline u ror(u x,int r){return (x>>r)|(x<<(32-r));}
static void c3(u w4,u*b,u*d){u X3=0x29d4fa98,X7=0xbee3af28,X11=0x44036000,X15=0x40c58500,W13=0x0007c006;
 u a1=X3+X7+w4,d1=ror(X15^a1,16),c1=X11+d1,b1=ror(X7^c1,12),a2=a1+b1+W13,d2=ror(d1^a2,8),c2=c1+d2;*b=ror(b1^c2,7);*d=d2;}
int main(){int ds[]={8,-8,16,-16,1,-1};
 for(int k=0;k<6;k++){u dl=(u)ds[k];unsigned long cnt=0;u first=0;int ctl=0;
  for(uint64_t w=0;w<(1ULL<<32);w++){u b,d,b2,d2;c3((u)w,&b,&d);c3((u)w+dl,&b2,&d2);
   if(b==b2&&d==d2){cnt++;if(!first)first=(u)w; if((u)w==0x97475638u)ctl=1;}}
  printf("%d %lu first=%08x contains_W4=%d\n",ds[k],cnt,first,ctl);fflush(stdout);}
}
