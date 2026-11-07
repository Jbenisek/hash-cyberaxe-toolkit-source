#include "common.h"
int main(){ ntt_init(16); plan_t P=plan3_for_len(98304); size_t N=P.N; fp*Y=NEW_FP(N); for(size_t i=0;i<N;i++){fp_from_u64(&Y[i],i+1);} 
 fp_counters_reset(); memset(&X,0,sizeof X);
 snap_t s0=snap(); ntt_fwd(&P,Y,Y,0,39062); snap_t d=snap_sub(snap(),s0);
 printf("fwd(len 39062): arith=%llu ld=%llu st=%llu ctl=%llu\n",(unsigned long long)snap_arith(d),(unsigned long long)d.ld,(unsigned long long)d.st,(unsigned long long)d.ctl);
 s0=snap(); ntt_inv(&P,Y,77000); d=snap_sub(snap(),s0);
 printf("inv(out 77000): arith=%llu ld=%llu st=%llu ctl=%llu\n",(unsigned long long)snap_arith(d),(unsigned long long)d.ld,(unsigned long long)d.st,(unsigned long long)d.ctl);
 return 0;}
