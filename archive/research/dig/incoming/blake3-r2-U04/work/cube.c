#include <stdio.h>
#include <stdint.h>
int main(){
  uint32_t D=0x0a08818bu;
  uint32_t X1=0x0e09818bu, X2=0x0e09818du;  // ROL(beta,12) for beta*, beta2
  // beta=ror(X,12) -> X=rol(beta,12)
  uint32_t b1=0x18b0e098u,b2=0x18d0e098u;
  uint32_t T1=(b1<<12)|(b1>>20), T2=(b2<<12)|(b2>>20);
  uint64_t n1=0,n2=0,mm1=0,mm2=0;
  for(uint64_t c64=0;c64<(1ULL<<32);c64++){
    uint32_t c=(uint32_t)c64; uint32_t x=c^(c+D);
    int e1=(x==T1), e2=(x==T2);
    int m1=((c&0x0e09818bu)==0x02008000u), m2=((c&0x0e09818du)==0x02008001u);
    n1+=e1; n2+=e2; mm1+=(e1!=m1); mm2+=(e2!=m2);
  }
  printf("T1=%08x T2=%08x\nbeta* count=%llu (2^21=%llu) mismatch_vs_cube=%llu\nbeta2 count=%llu mismatch_vs_cube=%llu\n",T1,T2,(unsigned long long)n1,(unsigned long long)(1ULL<<21),(unsigned long long)mm1,(unsigned long long)n2,(unsigned long long)mm2);
}
