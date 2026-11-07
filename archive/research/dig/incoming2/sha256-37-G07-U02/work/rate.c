#include <stdio.h>
#include <stdint.h>
#include <time.h>
static const uint32_t K[64]={0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};
#define R(x,n) (((x)>>(n))|((x)<<(32-(n))))
static void comp(uint32_t*s,const uint32_t*in){uint32_t w[64],a,b,c,d,e,f,g,h,t1,t2;int i;for(i=0;i<16;i++)w[i]=in[i];for(;i<64;i++){uint32_t s0=R(w[i-15],7)^R(w[i-15],18)^(w[i-15]>>3),s1=R(w[i-2],17)^R(w[i-2],19)^(w[i-2]>>10);w[i]=w[i-16]+s0+w[i-7]+s1;}
a=s[0];b=s[1];c=s[2];d=s[3];e=s[4];f=s[5];g=s[6];h=s[7];
for(i=0;i<64;i++){t1=h+(R(e,6)^R(e,11)^R(e,25))+((e&f)^(~e&g))+K[i]+w[i];t2=(R(a,2)^R(a,13)^R(a,22))+((a&b)^(a&c)^(b&c));h=g;g=f;f=e;e=d+t1;d=c;c=b;b=a;a=t1+t2;}
s[0]+=a;s[1]+=b;s[2]+=c;s[3]+=d;s[4]+=e;s[5]+=f;s[6]+=g;s[7]+=h;}
int main(){uint32_t s[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19},in[16]={0};
 /* known answer: sha256("abc") */
 uint32_t t[8]={0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19},m[16]={0x61626380,0,0,0,0,0,0,0,0,0,0,0,0,0,0,24};comp(t,m);printf("abc: %08x %08x (expect ba7816bf 8f01cfea)\n",t[0],t[1]);
 for(int rep=0;rep<3;rep++){struct timespec a,b;clock_gettime(CLOCK_THREAD_CPUTIME_ID,&a);unsigned long n=0;do{for(int k=0;k<20000;k++){in[0]=n+k;comp(s,in);}n+=20000;clock_gettime(CLOCK_THREAD_CPUTIME_ID,&b);}while((b.tv_sec-a.tv_sec)+(b.tv_nsec-a.tv_nsec)*1e-9<3.0);
  double el=(b.tv_sec-a.tv_sec)+(b.tv_nsec-a.tv_nsec)*1e-9;printf("rep %d: %lu compressions in %.3f cpu-s = %.0f /s (sink %08x)\n",rep,n,el,n/el,s[0]);}
}
