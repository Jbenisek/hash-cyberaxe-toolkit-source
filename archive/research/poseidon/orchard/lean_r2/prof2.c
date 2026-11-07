#include "common.h"
static void rep(const char*n, snap_t a){ snap_t d=snap_sub(snap(),a); printf("%-28s arith=%12llu ld=%11llu st=%11llu ctl=%12llu\n",n,(unsigned long long)snap_arith(d),(unsigned long long)d.ld,(unsigned long long)d.st,(unsigned long long)d.ctl);}
int main(){ ntt_init(15); plan_t P=plan3_for_len(78123); size_t N=P.N, m=39062; plan_t Pp=plan3_for_len(m+1);
 fp*Y=NEW_FP(N), *tmp=NEW_FP(P.n), *B=NEW_FP(m); for(size_t i=0;i<N;i++)fp_from_u64(&Y[i],i+7); for(size_t i=0;i<m;i++)fp_from_u64(&B[i],i+3);
 snap_t s;
 s=snap(); conv_sq(&P,Y,m,2*m-1); rep("conv_sq N",s);
 s=snap(); conv_mulc_otf(&P,Y,Y,0,m-1,tmp,B,m-1,N-(m-2),m-1); rep("mulc_otf MU",s);
 s=snap(); conv_mulc_otf(&Pp,Y,Y,0,m-1,tmp,B,m+1>m?m:m,0,m); rep("mulc_otf g (Np)",s);
 return 0;}
