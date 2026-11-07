// exhaustive 2^32 sweep of w12 through E1=G(1,6,11,12,w12,w5) for a real A/B pair context (Y11 and w5 differ)
#include <stdio.h>
#include <stdint.h>
typedef uint32_t u;
static u ror(u x,int r){return (x>>r)|(x<<(32-r));}
typedef struct{u a2,b2,c2,d2;} R;
static R g(u A,u B,u C,u D,u x,u y){u a1=A+B+x,d1=ror(D^a1,16),c1=C+d1,b1=ror(B^c1,12),a2=a1+b1+y,d2=ror(d1^a2,8),c2=c1+d2,b2=ror(b1^c2,7);R r={a2,b2,c2,d2};return r;}
int main(){
 u Y1=2841903418u,Y6=1337158305u,Y12=1791106488u,YA=2063040312u,YB=2231369923u,w5A=520360405u,w5B=520360397u;
 unsigned long long z[4]={0,0,0,0},zany=0,z2=0; int minhw=999; u minw=0; unsigned long long hwhist[129]={0}; unsigned long long dsame=0;
 for(unsigned long long k=0;k<(1ULL<<32);k++){
  u w=(u)k; R p=g(Y1,Y6,YA,Y12,w,w5A), q=g(Y1,Y6,YB,Y12,w,w5B);
  u d[4]={p.a2^q.a2,p.b2^q.b2,p.c2^q.c2,p.d2^q.d2}; int hw=0,nz=0;
  for(int i=0;i<4;i++){hw+=__builtin_popcount(d[i]); if(!d[i]){z[i]++;nz++;}}
  if(nz)zany++; if(nz>=2)z2++; hwhist[hw]++;
  if(hw<minhw){minhw=hw;minw=w;}
 }
 printf("zero dA2=%llu dB2=%llu dC2=%llu dD2=%llu any=%llu two_or_more=%llu  minHW=%d at w12=%08x\n",z[0],z[1],z[2],z[3],zany,z2,minhw,minw);
 double s=0,t=0; for(int h=0;h<=128;h++){s+=h*(double)hwhist[h];t+=hwhist[h];} printf("mean HW of the 128-bit XOR diff after E1 = %.3f\n",s/t);
 for(int h=0;h<=128;h++) if(hwhist[h]&&h<=30) printf("hw %d: %llu\n",h,hwhist[h]);
 return 0;}
