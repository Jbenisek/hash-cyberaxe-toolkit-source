#include <stdio.h>
#include <stdint.h>
typedef uint32_t u; typedef uint64_t U;
static inline u ror(u x,int n){return (x>>n)|(x<<(32-n));}
static U s=88172645463325252ULL; static inline u rnd(){s^=s<<13;s^=s>>7;s^=s<<17;return (u)(s>>16);}
static inline void g(u a,u b,u c,u d,u x,u y,u*bo,u*do_){u a1=a+b+x,d1=ror(d^a1,16),c1=c+d1,b1=ror(b^c1,12);u a2=a1+b1+y;*do_=ror(d1^a2,8);u c2=c1+*do_;*bo=ror(b1^c2,7);}
int main(){int sh[2]={8,-8};U N=1ULL<<32;for(int k=0;k<2;k++){U both=0,eb=0,ed=0;for(U i=0;i<N;i++){u a=rnd(),b=rnd(),c=rnd(),d=rnd(),x=rnd(),y=rnd();u b1,d1,b2,d2;g(a,b,c,d,x,y,&b1,&d1);g(a,b,c,d,x+(u)sh[k],y,&b2,&d2);ed+=d1==d2;eb+=b1==b2;both+=(b1==b2)&&(d1==d2);}
printf("shift %+d: random (a,b,c,d,x,y) samples 2^32: d equal %llu, b equal %llu, both equal %llu (density %.3e)\n",sh[k],(unsigned long long)ed,(unsigned long long)eb,(unsigned long long)both,(double)both/(double)N);fflush(stdout);}return 0;}
