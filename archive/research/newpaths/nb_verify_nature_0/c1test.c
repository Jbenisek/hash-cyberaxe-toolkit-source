/* nb_verify_nature_0: recheck the c1 cheap test that the only remaining
   "staged discrimination" step (split of stage 2) rests on.
   (1) exact count over all 2^32 c1: x = c1 ^ (c1 + D), D = Y11' - Y11,
       pass = (x & 0xcbfffff9) == 0x0a098189. Claim: 27525120 = 105/16384 * 2^32,
       18 distinct passing x.
   (2) on real E1 arithmetic (Lemma N of the filed proof): free words d1, Y6, t=a1+w5;
       n = eps ^ ROL(beta ^ eps,1) ^ eta. Measure P(n=0), and the share of n=0 events
       whose c1 passes the cheap test (does the cheap stage throw away E1-test mass?).
   Build: gcc -O3 -march=native -o c1test c1test.c */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
static inline uint32_t ror(uint32_t x, int r){ return (x>>r)|(x<<(32-r)); }
static inline uint32_t rol(uint32_t x, int r){ return (x<<r)|(x>>(32-r)); }
static uint64_t s;
static inline uint64_t sm(void){ uint64_t z=(s+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
#define Y11  0x7af77f38u
#define Y11B 0x850000c3u
#define ETA  0x830303cfu
#define DELTA 0xfffffff8u
#define MASK 0xcbfffff9u
#define VAL  0x0a098189u
static inline int cheap(uint32_t d1){ uint32_t x=(Y11+d1)^(Y11B+d1); return (x&MASK)==VAL; }
static inline uint32_t ntest(uint32_t d1, uint32_t y6, uint32_t t){
  uint32_t c1=Y11+d1, c1b=Y11B+d1;
  uint32_t b1=ror(y6^c1,12), b1b=ror(y6^c1b,12);
  uint32_t a2=t+b1, a2b=t+DELTA+b1b;           /* a2 = a1 + b1 + w5 ; B uses w5+delta */
  uint32_t d2=ror(d1^a2,8), d2b=ror(d1^a2b,8);
  uint32_t c2=c1+d2, c2b=c1b+d2b;
  uint32_t beta=b1^b1b, eps=c2^c2b;
  return eps ^ rol(beta^eps,1) ^ ETA;
}
int main(int argc, char**argv){
  long long nsamp = argc>1 ? atoll(argv[1]) : (1LL<<30);
  s = argc>2 ? strtoull(argv[2],0,10) : 12345;
  /* (1) exact */
  uint64_t pass=0; uint32_t xs[64]; int nx=0;
  uint32_t *passlist = malloc(sizeof(uint32_t)*28000000u);
  uint32_t d1=0;
  do { if(cheap(d1)){ uint32_t x=(Y11+d1)^(Y11B+d1);
         if(pass<28000000u) passlist[pass]=d1; pass++;
         int f=0; for(int i=0;i<nx;i++) if(xs[i]==x){f=1;break;}
         if(!f && nx<64) xs[nx++]=x; }
       d1++; } while(d1!=0);
  printf("EXACT pass count over 2^32 c1: %llu  (claim 27525120 = 105/16384*2^32 -> %s)\n",
         (unsigned long long)pass, pass==27525120ULL?"MATCH":"DIFFERENT");
  printf("EXACT distinct passing x: %d (claim 18)\n", nx);
  /* (2a) uniform sampling: P(n=0), share of n=0 that pass the cheap test */
  long long hit=0, hitpass=0;
  for(long long i=0;i<nsamp;i++){ uint64_t r=sm(); uint32_t dd=(uint32_t)r, y6=(uint32_t)(r>>32), t=(uint32_t)sm();
    if(ntest(dd,y6,t)==0){ hit++; if(cheap(dd)) hitpass++; } }
  printf("UNIFORM %lld samples: n=0 hits %lld (rate 2^%.3f), of which cheap-pass %lld\n",
         nsamp, hit, hit? __builtin_log2((double)hit/nsamp):0.0, hitpass);
  /* (2b) conditional: d1 drawn from the pass set */
  long long hc=0;
  for(long long i=0;i<nsamp;i++){ uint64_t r=sm(); uint32_t dd=passlist[(uint32_t)r % (uint32_t)pass];
    uint32_t y6=(uint32_t)(r>>32), t=(uint32_t)sm(); if(ntest(dd,y6,t)==0) hc++; }
  double ppass=(double)pass/4294967296.0;
  printf("PASS-SET %lld samples: n=0 hits %lld -> P(n=0|pass)=%.6e, P(n=0 & pass)=%.6e\n",
         nsamp, hc, (double)hc/nsamp, (double)hc/nsamp*ppass);
  return 0;
}
