/* d3test.c -- stage D3 (and D1, C0) on realistic upstream outputs.
 * Inputs: K1 problems file (mkk1prob format: h5 thi dm2 dv6 A3 delta D dm4 A2 d2) and k1gpu solutions
 * (prob h5 thi dm2 dv6 A1 which nsol).  For each K1 solution: rebuild K3 (A3,delta), K2 (dm4,A2) with cube elements
 * that keep dv6, and K1 (A1, which); then D3: (i) rotation DP (R=16) over m14, (ii) compat(D, d1^d1') over m15.
 * If D3 passes: D1 (DP for v12, rotation DP R=8 for m11) and C0 compat(-delta, X12^X12').
 * Stage-marginal: K2's dm4 is not -D unless the K1 problem came from a joint K3xK2 solution.
 * Usage: ./d3test PROBS K1SOLS NCUBE */
#include "b3lc.h"
#include <math.h>
static int k2_given(u32 h6, u32 blen, u32 A, u32 dm4, u32 d2, K2sol *o){
  u32 Ap = A + dm4, d1 = ror32(blen ^ A, 16), d1p = ror32(blen ^ Ap, 16), c1 = B3IV[2] + d1, c1p = B3IV[2] + d1p;
  u32 b1 = ror32(h6 ^ c1, 12), b1p = ror32(h6 ^ c1p, 12);
  if (A + b1 != Ap + b1p) return 0;
  u32 eta = ror32(d1 ^ d1p, 8), M = c1 - c1p, F, V;
  if (!compat_cube(M, eta, &F, &V)) return 0;
  if ((d2 & F) != (V & F)) return 0;
  u32 a2 = rol32(d2, 8) ^ d1, c2 = c1 + d2;
  o->A = A; o->dm4 = dm4; o->a2 = a2; o->d2 = d2; o->d2p = d2 ^ eta; o->m5 = a2 - A - b1;
  o->v2 = a2; o->v10 = c2; o->v14 = d2; o->v14p = d2 ^ eta; o->v6 = ror32(b1 ^ c2, 7); o->v6p = ror32(b1p ^ c2, 7);
  o->cube = 1ULL << (32 - __builtin_popcount(F));
  return 1;
}
int main(int argc, char **argv){
  if (argc < 4) return 1;
  setvbuf(stdout, NULL, _IOLBF, 0);
  g_rng = 0x3D3D3D;
  int ncube = atoi(argv[3]);
  /* load problems */
  FILE *fp = fopen(argv[1], "r"); char line[512]; int np = 0; static u32 P[200000][10];
  while (fgets(line, sizeof line, fp) && np < 200000){
    u32 *q = P[np];
    if (sscanf(line, "%x %x %x %x %x %x %x %x %x %x", q, q+1, q+2, q+3, q+4, q+5, q+6, q+7, q+8, q+9) == 10) np++;
  }
  fclose(fp);
  FILE *fs = fopen(argv[2], "r");
  long nk1 = 0, k2try = 0, k2same = 0, d3i_runs = 0, d3i_pos = 0, d3_ok = 0, d1_ok = 0, c0_ok = 0; double d3i_sum = 0;
  while (fgets(line, sizeof line, fs)){
    unsigned prob, which; u32 h5, thi, dm2, dv6, A1; unsigned long long ns;
    if (sscanf(line, "%u %x %x %x %x %x %u %llu", &prob, &h5, &thi, &dm2, &dv6, &A1, &which, &ns) != 8) continue;
    if ((int)prob >= np) continue;
    u32 *q = P[prob]; u32 A3 = q[4], delta = q[5], D = q[6], dm4 = q[7], A2 = q[8], d2base = q[9];
    if (argc > 4 && atoi(argv[4]) == 1) D = 0u - dm4;   /* consistent mode: D3 sees the D that K2's dm4 implies */
    nk1++;
    K3sol s3; if (!k3_try(B3IV[7], 11, A3, delta, &s3, 1)) { printf("K3 rebuild failed\n"); continue; }
    K1sol s1; if (!k1_try(h5, thi, A1, dm2, dv6, (int)which, &s1, 1)) { printf("K1 rebuild failed\n"); continue; }
    u32 M = s1.v9 - s1.v9p;
    for (int c = 0; c < ncube; c++){
      /* K2 cube element: flip random free bits of d2base, keep dv6 */
      K2sol s2; u32 d2 = d2base;
      if (c){ K2sol tmp; if (!k2_b(B3IV[6], 64, A2, dm4, &tmp)) continue; d2 = tmp.d2; }
      k2try++;
      if (!k2_given(B3IV[6], 64, A2, dm4, d2, &s2)) continue;
      if (s2.v6p - s2.v6 != dv6) continue;
      k2same++;
      u32 Ad3; u64 cnt;
      d3i_runs++;
      if (!rotdp(s2.v14, s2.v14p, D, 16, M, rnd64(), &Ad3, &cnt)) continue;
      d3i_pos++; d3i_sum += (double)cnt;
      /* (ii) over several sampled (i) solutions */
      int ok = 0; u32 F3, V3;
      for (int t = 0; t < 64 && !ok; t++){
        if (t) rotdp(s2.v14, s2.v14p, D, 16, M, rnd64(), &Ad3, 0);
        if (d3_ii(D, s2.v14, s2.v14p, Ad3, &F3, &V3)) ok = 1;
      }
      if (!ok) continue;
      d3_ok++;
      /* D1 + C0 */
      u32 Delta1 = s1.Dm + dv6; int got = 0;
      for (int tr = 0; tr < 4096 && !got; tr++){
        u32 A = (u32)rnd64(), Ap = A + Delta1, qq; u64 cq; u32 x = ror32(A ^ Ap, 16);
        if (!d1i_sample(s3.v11, s3.v11p, x, s2.v6 ^ s2.v6p, rnd64(), &qq, &cq)) continue;
        u32 d1 = qq, d1p = qq ^ x, c1 = s3.v11 + d1, c1p = s3.v11p + d1p, a2;
        if (!rotdp(d1, d1p, Delta1, 8, c1 - c1p, rnd64(), &a2, 0)) continue;
        if (!got) d1_ok++;
        u32 d2x = ror32(d1 ^ a2, 8), d2xp = ror32(d1p ^ (a2 + Delta1), 8), Fc, Vc;
        if (compat_cube(0u - delta, d2x ^ d2xp, &Fc, &Vc)) { got = 1; c0_ok++; }
      }
    }
  }
  printf("d3test: K1 solutions %ld; K2 cube tries %ld, same dv6 %ld; D3(i) runs %ld, with >=1 solution %ld (mean count %.2f);"
         " D3(i)&(ii) %ld; D1 ok %ld; C0 ok %ld\n", nk1, k2try, k2same, d3i_runs, d3i_pos, d3i_pos ? d3i_sum / d3i_pos : 0.0, d3_ok, d1_ok, c0_ok);
  return 0;
}
