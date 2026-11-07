#include "common.h"
static void rep(const char*n, snap_t a){ snap_t d=snap_sub(snap(),a); printf("%-22s arith=%11llu ld=%10llu st=%10llu ctl=%11llu total=%11llu\n",n,(unsigned long long)snap_arith(d),(unsigned long long)d.ld,(unsigned long long)d.st,(unsigned long long)d.ctl,(unsigned long long)snap_total(d));}
int main(){ ntt_init(17); size_t m=195312; plan_t P=plan3_for_len(2*m-1); size_t N=P.N; printf("N=%zu\n",N);
 fp*Y=NEW_FP(N); for(size_t i=0;i<N;i++)fp_from_u64(&Y[i],i+7);
 fp_counters_reset(); memset(&X,0,sizeof X);
 snap_t s;
 s=snap(); ntt_fwd(&P,Y,Y,0,m); rep("fwd N len m",s);
 s=snap(); ntt_inv(&P,Y,2*m-1); rep("inv N out 2m-1",s);
 s=snap(); conv_sq(&P,Y,m,2*m-1); rep("conv_sq",s);
 s=snap(); conv_mulc(&P,Y,Y,0,m-1,Y,m-1); rep("conv_mulc",s);
 return 0;}
