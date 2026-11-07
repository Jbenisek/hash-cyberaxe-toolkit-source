/* cvrate: does the chaining value change the residual statistics of the 55/63 family?
   mode "iv"  : single block, v0..v7 = IV, flags 11 (the filed family)
   mode "cv S": last block of a two-block message, CV = 2-round compression of a random first block
                (seed S, flags CHUNK_START = 1, length 64, counter 0), flags 10, pins re-expressed
                X3' = X3 + delta, W4' = W4 - delta, delta = (cv2+cv6) - (IV2+IV6)
   mode "m"   : model M: the six words d1, b1, a2, Y9, w8, h1 uniform, Y4 uniform in sub-class C15
   All 8 free words uniform (Y4 from C15).  Residual R = XOR of digest words 1,3,4,6, computed by F from the
   seven words and the single-block constants (checked equal to the real digests by s8_check.py, 2500/2500).
   Counts: low 16 bits zero per word; whole word zero; low 8 bits of all four zero; low 4 bits of all four
   zero; weight histogram.   usage: cvrate MODE SEED LOG2N RNGSEED */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
static inline u32 ror(u32 x, int r){ return (x>>r)|(x<<(32-r)); }
static inline u32 rol(u32 x, int r){ return (x<<r)|(x>>(32-r)); }
static const u32 IV[8]={0x6A09E667,0xBB67AE85,0x3C6EF372,0xA54FF53A,0x510E527F,0x9B05688C,0x1F83D9AB,0x5BE0CD19};
static const int PERM[16]={2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const u32 X3=0x29d4fa98,X7=0xbee3af28,X11=0x44036000,X15=0x40c58500,W4=0x97475638,W13=0x0007c006;
static const u32 Y3A=0x8127c181,Y3B=0x7edf3e7e,Y11A=0x7af77f38,Y11B=0x850000c3,DW5=0xfffffff8;
static const u32 CLASS_VAL=0x030c0303, SUB_AND=0x07ef8303;
static u64 st;
static inline u64 sm(void){ u64 z=(st+=0x9E3779B97F4A7C15ULL); z=(z^(z>>30))*0xBF58476D1CE4E5B9ULL; z=(z^(z>>27))*0x94D049BB133111EBULL; return z^(z>>31); }
#define GG(a,b,c,d,x,y) do{ a=a+b+(x); d=ror(d^a,16); c=c+d; b=ror(b^c,12); a=a+b+(y); d=ror(d^a,8); c=c+d; b=ror(b^c,7);}while(0)
static int freepos[17];
static u32 member(u32 k){ u32 e1=CLASS_VAL; for(int j=0;j<17;j++) if(k>>j&1) e1|=1u<<freepos[j]; return e1-Y3A; }

static void compress2(const u32 cv[8], const u32 w[16], u32 n, u32 fl, u32 out[8]){
  u32 v[16]; for(int i=0;i<8;i++) v[i]=cv[i]; for(int i=0;i<4;i++) v[8+i]=IV[i]; v[12]=0; v[13]=0; v[14]=n; v[15]=fl;
  u32 s[16], t[16]; memcpy(s,w,64);
  for(int r=0;r<2;r++){
    GG(v[0],v[4],v[8],v[12],s[0],s[1]); GG(v[1],v[5],v[9],v[13],s[2],s[3]);
    GG(v[2],v[6],v[10],v[14],s[4],s[5]); GG(v[3],v[7],v[11],v[15],s[6],s[7]);
    GG(v[0],v[5],v[10],v[15],s[8],s[9]); GG(v[1],v[6],v[11],v[12],s[10],s[11]);
    GG(v[2],v[7],v[8],v[13],s[12],s[13]); GG(v[3],v[4],v[9],v[14],s[14],s[15]);
    for(int i=0;i<16;i++) t[i]=s[PERM[i]]; memcpy(s,t,64);
  }
  for(int i=0;i<8;i++) out[i]=v[i]^v[i+8];
}

/* residual from the seven words (same F as s8_check.py) */
static inline void Fres(u32 d1,u32 b1,u32 a2,u32 Y4,u32 Y9,u32 w8,u32 h1,u32 R[4]){
  u32 c1A=Y11A+d1, Y6=rol(b1,12)^c1A, c1B=Y11B+d1, b1B=ror(Y6^c1B,12), a2B=a2+b1B-b1+DW5;
  u32 d2A=ror(d1^a2,8), c2A=c1A+d2A, b2A=ror(b1^c2A,7);
  u32 d2B=ror(d1^a2B,8), c2B=c1B+d2B, b2B=ror(b1B^c2B,7);
  u32 e1A=Y3A+Y4, Y14=rol(h1,16)^e1A;
  u32 g1A=Y9+h1, f1A=ror(Y4^g1A,12), e2A=e1A+f1A+w8, h2A=ror(h1^e2A,8), g2A=g1A+h2A, f2A=ror(f1A^g2A,7);
  u32 e1B=Y3B+Y4, hB=ror(Y14^e1B,16), g1B=Y9+hB, f1B=ror(Y4^g1B,12), e2B=e1B+f1B+w8, h2B=ror(hB^e2B,8), g2B=g1B+h2B, f2B=ror(f1B^g2B,7);
  R[0]=(a2^g2A)^(a2B^g2B); R[1]=(e2A^c2A)^(e2B^c2B); R[2]=(f2A^d2A)^(f2B^d2B); R[3]=(b2A^h2A)^(b2B^h2B);
}

int main(int argc,char**argv){
  if(argc<5){fprintf(stderr,"usage\n");return 1;}
  const char*mode=argv[1]; u64 seed=strtoull(argv[2],0,0); int lg=atoi(argv[3]); st=strtoull(argv[4],0,0)*0x1234567ULL+77;
  {int j=0; for(int i=0;i<32;i++) if(!(SUB_AND>>i&1)) freepos[j++]=i;}
  u32 cv[8]; u32 fl=11; int model=0;
  if(!strcmp(mode,"iv")){ memcpy(cv,IV,32); }
  else if(!strcmp(mode,"m")){ model=1; memcpy(cv,IV,32); }
  else { /* cv: first block from seed */
    u64 s0=st; st=seed*0xD1B54A32D192ED03ULL+12345; u32 b1w[16]; for(int i=0;i<16;i++) b1w[i]=(u32)sm(); st=s0;
    compress2(IV,b1w,64,1,cv); fl=10;
    printf("first block:"); for(int i=0;i<16;i++) printf(" %08x",b1w[i]); printf("\n");
  }
  printf("mode %s seed %llu log2N %d cv:",mode,(unsigned long long)seed,lg); for(int i=0;i<8;i++) printf(" %08x",cv[i]); printf(" flags %u\n",fl);
  u32 KIV=IV[2]+IV[6], K=cv[2]+cv[6], delta=K-KIV, x3=X3+delta, w4=W4-delta;
  u64 N=1ULL<<lg, z16[4]={0}, z32[4]={0}, lo8=0, lo4=0, hist[129]={0}, z16pair[6]={0};
  for(u64 t=0;t<N;t++){
    u64 r1=sm(), r2=sm(), r3=sm(), r4=sm();
    u32 y=member((u32)(r4>>40)&0x1ffff), R[4];
    if(model){
      Fres((u32)r1,(u32)(r1>>32),(u32)r2,y,(u32)(r2>>32),(u32)r3,(u32)(r3>>32),R);
    } else {
      u32 Cc1=(u32)r1, Cd1=(u32)(r1>>32), D3d1=(u32)r2, S15=(u32)(r2>>32), S9=(u32)r3, w5=(u32)(r3>>32), X2=(u32)r4;
      u32 K2a1=K+w4, K2d1=ror(55^K2a1,16), K2c1=IV[2]+K2d1, K2b1=ror(cv[6]^K2c1,12);
      u32 S2=K2a1+K2b1+w5, S14=ror(K2d1^S2,8), S10=K2c1+S14, S6=ror(K2b1^S10,7);
      u32 D3a1=rol(D3d1,16)^S14, D3c1=S9+D3d1, D3b1=x3-D3a1, S4=rol(D3b1,12)^D3c1;
      u32 S3=D3a1-S4, X14=ror(D3d1^x3,8), X9=D3c1+X14, X4=ror(D3b1^X9,7);
      u32 K3d1=rol(S15,8)^S3, K3c1=IV[3]+K3d1, K3b1=ror(cv[7]^K3c1,12), S11=K3c1+S15;
      u32 S7=ror(K3b1^S11,7), K3a1=rol(K3d1,16)^fl, w6=K3a1-cv[3]-cv[7], w7=S3-K3a1-K3b1;
      u32 X8=Cc1-Cd1, C0b1=ror(X4^Cc1,12), D2b1=rol(X7,7)^X8, D2c1=rol(D2b1,12)^S7, X13=X8-D2c1;
      u32 D2a1=X2-D2b1-W13, D2d1=rol(X13,8)^X2, S13=rol(D2d1,16)^D2a1, S8=D2c1-D2d1, w12=D2a1-S2-S7;
      u32 K1c1=S9-S13, K1d1=K1c1-IV[1], K1a1=rol(K1d1,16), K1b1=ror(cv[5]^K1c1,12);
      u32 S1=rol(S13,8)^K1d1, S5=ror(K1b1^S9,7), w2=K1a1-cv[1]-cv[5], w3=S1-K1a1-K1b1;
      u32 K0b1=rol(S4,7)^S8, K0c1=rol(K0b1,12)^cv[4], K0d1=K0c1-IV[0], K0a1=rol(K0d1,16);
      u32 S12=S8-K0c1, S0=rol(S12,8)^K0d1, w0=K0a1-cv[0]-cv[4]; (void)w0;
      u32 Y8=rol(y,7)^C0b1, Y12=Y8-Cc1, Y0=rol(Y12,8)^Cd1, C0a1=Y0-C0b1-w6, X12=rol(Cd1,16)^C0a1;
      u32 D1c1=X11-X12, D1b1=ror(S6^D1c1,12), X6=ror(D1b1^X11,7), D1d1=D1c1-S11, X1=rol(X12,8)^D1d1;
      u32 X0=C0a1-X4-w2, D0d1=rol(X15,8)^X0, D0c1=S10+D0d1, X10=D0c1+X15, D0b1=ror(S5^D0c1,12);
      u32 X5=ror(D0b1^X10,7), D0a1=rol(D0d1,16)^S15, w8=D0a1-S0-S5;
      u32 D1a1=rol(D1d1,16)^S12, w10=D1a1-S1-S6;
      /* round 1 columns C1 = G(X1,X5,X9,X13; w3,w10), C2 = G(X2,X6,X10,X14; w7,w0) */
      u32 a=X1,b=X5,c=X9,d=X13; GG(a,b,c,d,w3,w10); u32 Y1=a, Y9=c;
      u32 w0b=K0a1-cv[0]-cv[4];
      a=X2;b=X6;c=X10;d=X14; GG(a,b,c,d,w7,w0b); u32 Y6=b, Y14=d;
      u32 a1=Y1+Y6+w12, d1=ror(Y12^a1,16), c1=Y11A+d1, b1=ror(Y6^c1,12), a2=a1+b1+w5;
      u32 e1=Y3A+y, h1=ror(Y14^e1,16);
      Fres(d1,b1,a2,y,Y9,w8,h1,R);
      if(t<5) printf("DBG %08x %08x %08x %08x %08x %08x %08x %08x R %08x %08x %08x %08x\n",Cc1,Cd1,D3d1,S15,S9,w5,X2,y,R[0],R[1],R[2],R[3]);
    }
    int hw=0; for(int j=0;j<4;j++){ hw+=__builtin_popcount(R[j]); if(!(R[j]&0xffff)) z16[j]++; if(!R[j]) z32[j]++; }
    hist[hw]++;
    if(!((R[0]|R[1]|R[2]|R[3])&0xff)) lo8++;
    if(!((R[0]|R[1]|R[2]|R[3])&0xf)) lo4++;
    int p=0; for(int i=0;i<4;i++) for(int j=i+1;j<4;j++){ if(!((R[i]|R[j])&0xff)) z16pair[p]++; p++; }
  }
  printf("N %llu\n",(unsigned long long)N);
  printf("low16zero r1 r3 r4 r6: %llu %llu %llu %llu\n",(unsigned long long)z16[0],(unsigned long long)z16[1],(unsigned long long)z16[2],(unsigned long long)z16[3]);
  printf("wordzero  r1 r3 r4 r6: %llu %llu %llu %llu\n",(unsigned long long)z32[0],(unsigned long long)z32[1],(unsigned long long)z32[2],(unsigned long long)z32[3]);
  printf("pairs low8 zero (13 14 16 34 36 46): "); for(int p=0;p<6;p++) printf("%llu ",(unsigned long long)z16pair[p]); printf("\n");
  printf("all four low8 zero: %llu   all four low4 zero: %llu\n",(unsigned long long)lo8,(unsigned long long)lo4);
  double m=0,v=0; for(int i=0;i<=128;i++){ m+=(double)i*hist[i]; } m/=N; for(int i=0;i<=128;i++) v+=(i-m)*(i-m)*hist[i]; v/=N;
  u64 le40=0; for(int i=0;i<=40;i++) le40+=hist[i];
  printf("weight mean %.5f var %.4f  weight<=40: %llu\n",m,v,(unsigned long long)le40);
  printf("hist:"); for(int i=0;i<=128;i++) if(hist[i]) printf(" %d:%llu",i,(unsigned long long)hist[i]); printf("\n");
  return 0;
}
