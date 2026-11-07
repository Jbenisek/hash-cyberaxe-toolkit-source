/* d3base.c -- baseline solvability of D3(i): exists A with ror(c' ^ (A + D), 16) - ror(c ^ A, 16) == M, for
 * (1) random c, c', D, M with v2(D) = v2(M) = 0; (2) c' = c (eta = 0); (3) eta random, D from the 1,270-value
 * set -D2, M random odd; (4) eta = 0, D random odd, M from K1 solutions.  Exact rotation-DP counts.
 * Usage: ./d3base D2DISTINCT K1SOLS K1PROBS N */
#include "b3lc.h"
int main(int argc, char **argv){
  g_rng = 4242; long N = atol(argv[4]); char line[512];
  u32 D2[2048]; int nd = 0; FILE *fd = fopen(argv[1], "r");
  while (fgets(line, sizeof line, fd) && nd < 2048) { u32 v = 0u - (u32)strtoul(line, 0, 16); if (v & 1) D2[nd++] = v; }
  fclose(fd);
  /* K1 M values */
  static u32 P[200000][10]; int np = 0; FILE *fp = fopen(argv[3], "r");
  while (fgets(line, sizeof line, fp) && np < 200000){ u32 *q = P[np];
    if (sscanf(line, "%x %x %x %x %x %x %x %x %x %x", q, q+1, q+2, q+3, q+4, q+5, q+6, q+7, q+8, q+9) == 10) np++; }
  fclose(fp);
  u32 Ms[4096]; int nm = 0; FILE *fs = fopen(argv[2], "r");
  while (fgets(line, sizeof line, fs) && nm < 4096){
    unsigned prob, which; u32 h5, thi, dm2, dv6, A1; unsigned long long ns;
    if (sscanf(line, "%u %x %x %x %x %x %u %llu", &prob, &h5, &thi, &dm2, &dv6, &A1, &which, &ns) != 8) continue;
    K1sol s1; if (k1_try(h5, thi, A1, dm2, dv6, (int)which, &s1, 1)) Ms[nm++] = s1.v9 - s1.v9p;
  }
  fclose(fs);
  long pos[4] = {0, 0, 0, 0};
  if (argc > 5 && atoi(argv[5]) == 2){
    /* D3(ii) given D3(i): D in -D2 (odd), random eta (c, c'), random odd M; sample up to 64 (i)-solutions, test (ii) */
    long ni = 0, nii = 0, nii_any = 0;
    for (long i = 0; i < N; i++){
      u32 c = (u32)rnd64(), cp = (u32)rnd64(), D = D2[rnd64() % nd], M = (u32)rnd64() | 1u; u64 cnt; u32 A;
      if (!rotdp(c, cp, D, 16, M, rnd64(), &A, &cnt)) continue;
      ni++; int any = 0;
      for (int t = 0; t < 64; t++){
        if (t) rotdp(c, cp, D, 16, M, rnd64(), &A, 0);
        u32 d1 = ror32(c ^ A, 16), d1p = ror32(cp ^ (A + D), 16), F, V;
        if (compat_cube(D, d1 ^ d1p, &F, &V)) { if (!t) nii++; any = 1; }
      }
      nii_any += any;
    }
    printf("D3(ii) given D3(i), D in -D2: (i)-solvable %ld of %ld; first-sample (ii) %ld; any of 64 samples (ii) %ld\n",
           ni, N, nii, nii_any);
    return 0;
  }
  for (long i = 0; i < N; i++){
    u32 c = (u32)rnd64(), cp = (u32)rnd64(), D = (u32)rnd64() | 1u, M = (u32)rnd64() | 1u; u64 cnt;
    if (rotdp(c, cp, D, 16, M, 0, 0, &cnt)) pos[0]++;
    if (rotdp(c, c, D, 16, M, 0, 0, &cnt)) pos[1]++;
    u32 Dz = D2[rnd64() % nd];
    if (rotdp(c, cp, Dz, 16, M, 0, 0, &cnt)) pos[2]++;
    u32 Mk = Ms[rnd64() % nm];
    if (rotdp(c, c, D, 16, Mk, 0, 0, &cnt)) pos[3]++;
  }
  printf("D3(i) solvable, N=%ld each: random %ld (%.4f); eta=0 %ld (%.4f); D in -D2 (odd, %d values) %ld (%.4f); M from K1 (%d values), eta=0 %ld (%.4f)\n",
         N, pos[0], pos[0] / (double)N, pos[1], pos[1] / (double)N, nd, pos[2], pos[2] / (double)N, nm, pos[3], pos[3] / (double)N);
  return 0;
}
