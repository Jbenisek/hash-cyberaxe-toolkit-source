#include "common.h"
int main(){ ntt_init(17); fp_counters_reset(); memset(&X,0,sizeof X);
 snap_t s=snap();
 fp a,b,c; fp_from_u64(&a,123456789ULL); fp_from_u64(&b,987654321ULL); fp_mul(&c,&a,&b);
 plan_t P = plan3_for_len(96); fp *t = NEW_FP(P.N); for (size_t i = 0; i < 96; i++) fp_from_u64(&t[i], i * i + 1);
 ntt_fwd(&P, t, t, 0, 96); ntt_inv(&P, t, 96);
 fp Nf; uint64_t w[4] = { P.N, 0, 0, 0 }; fp_from_limbs(&Nf, w);
 for (size_t i = 0; i < 96; i++) { fp e, f; fp_from_u64(&e, i * i + 1); fp_mul(&f, &e, &Nf); }
 printf("probe total=%llu\n",(unsigned long long)snap_total(snap_sub(snap(),s))); return 0;}
