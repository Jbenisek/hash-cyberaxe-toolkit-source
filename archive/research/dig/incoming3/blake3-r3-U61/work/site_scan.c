// Own code (blake3-r3 dig, units U61-U63).  Exhaustive scan over all 2^32 values of ONE initial-state word v_i (i in 0..11),
// every other initial word standard (IV, counter 0, length 64, flags 11) or given by argv.  Round 0 column calls C0..C3 read the
// zero key words m0..m7, so they are pure functions of the initial state; the four diagonal calls D0..D3 then add / xor those
// post-column constants p0..p15 onto variable chain words.  The filed circuit (Tracer) skips an operation exactly when such a
// constant is 0.  The 16 sites (from the Tracer log, verified in site_check.py):
//   D0=G(0,5,10,15): p0+p5 (add into x), p15 (xor), p10 (add), p5 (xor)
//   D1=G(1,6,11,12): p1+p6, p12, p11, p6
//   D2=G(2,7,8,13):  p2+p7, p13, p8, p7
//   D3=G(3,4,9,14):  p3+p4, p14, p9, p4
// For v_i in column j = i mod 4 only p_j, p_{j+4}, p_{j+8}, p_{j+12} change.  Output: for each of the 16 sites the number of
// values of v_i that make the site constant 0, the histogram of the number of zero sites, and the first solutions.
// usage: site_scan i [iflags]   (iflags: initial v15 flags value, default 11)
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
static const uint32_t IV[8] = {0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19};
static inline uint32_t ror(uint32_t v, int n){ return (v>>n)|(v<<(32-n)); }
static inline void g0(uint32_t*a,uint32_t*b,uint32_t*c,uint32_t*d){ // G with x=y=0
  *a=*a+*b; *d=ror(*d^*a,16); *c=*c+*d; *b=ror(*b^*c,12);
  *a=*a+*b; *d=ror(*d^*a,8);  *c=*c+*d; *b=ror(*b^*c,7); }
// sites: index s=0..15 ; D call k=0..3 ; t=0..3 (0 sum,1 d-solo,2 c-solo,3 b-solo)
static const int SA[4]={0,1,2,3}, SB[4]={5,6,7,4}, SC[4]={10,11,8,9}, SD[4]={15,12,13,14};
static void sites(const uint32_t*p, uint32_t*s){
  for(int k=0;k<4;k++){ s[4*k+0]=p[SA[k]]+p[SB[k]]; s[4*k+1]=p[SD[k]]; s[4*k+2]=p[SC[k]]; s[4*k+3]=p[SB[k]]; }
}
int main(int argc,char**argv){
  int wi=atoi(argv[1]); uint32_t fl = argc>2 ? (uint32_t)strtoul(argv[2],0,0) : 11;
  uint32_t v[16]; for(int i=0;i<8;i++) v[i]=IV[i]; for(int i=0;i<4;i++) v[8+i]=IV[i]; v[12]=0;v[13]=0;v[14]=64;v[15]=fl;
  uint32_t p[16]; memcpy(p,v,64); for(int j=0;j<4;j++) g0(&p[j],&p[4+j],&p[8+j],&p[12+j]);
  uint32_t s0[16]; sites(p,s0);
  int nz0=0; for(int s=0;s<16;s++) if(s0[s]==0) nz0++;
  int col=wi&3; int role=wi>>2; // role 0 = a (v0..v3), 1 = b (v4..v7), 2 = c (v8..v11)
  uint64_t cnt[16]; memset(cnt,0,sizeof cnt); uint64_t hist[17]; memset(hist,0,sizeof hist);
  uint32_t first[16][4]; int nfirst[16]; memset(nfirst,0,sizeof nfirst);
  uint32_t bestv=0; int bestn=-1;
  uint64_t multi=0;
  for(uint64_t t=0;t<(1ULL<<32);t++){
    uint32_t q[4]={v[col],v[4+col],v[8+col],v[12+col]};
    q[role]=(uint32_t)t;
    g0(&q[0],&q[1],&q[2],&q[3]);
    // quick reject: only five conditions can change
    uint32_t pp[16]; memcpy(pp,p,64); pp[col]=q[0]; pp[4+col]=q[1]; pp[8+col]=q[2]; pp[12+col]=q[3];
    int hit = (q[0]+p[4+((col+1)&3)]==0) | (q[1]+p[(col+3)&3]==0) | (q[1]==0) | (q[2]==0) | (q[3]==0);
    if(!hit){ hist[0]++; continue; }
    uint32_t s[16]; sites(pp,s); int n=0;
    for(int k=0;k<16;k++) if(s[k]==0){ n++; cnt[k]++; if(nfirst[k]<4) first[k][nfirst[k]++]=(uint32_t)t; }
    hist[n]++; if(n>bestn){bestn=n;bestv=(uint32_t)t;}
  }
  printf("word v%d  column %d role %d  flags %u  standard-state zero sites: %d\n",wi,col,role,fl,nz0);
  printf("histogram of number of zero sites over 2^32 values:");
  for(int n=0;n<=16;n++) if(hist[n]) printf(" [%d]=%llu",n,(unsigned long long)hist[n]); printf("\n");
  for(int k=0;k<16;k++) if(cnt[k]){ printf("site %2d (D%d stmt %s) values making it 0: %llu  first:",k,k/4,(const char*[]){"x-add(p+p)","xor-d","add-c","xor-b"}[k%4],(unsigned long long)cnt[k]);
     for(int u=0;u<nfirst[k];u++) printf(" 0x%08x",first[k][u]); printf("\n"); }
  printf("best: %d zero sites at v%d=0x%08x\n",bestn,wi,bestv);
  return 0;
}
