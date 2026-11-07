/* d3val.c -- why D3(i) fails: for each K1 solution, v2(M) with M = v9 - v9' (K1's c1 difference), versus v2(D)
 * for the D values D3 sees; and the exact D3(i) count when D is drawn from the 1,270-value set -D2 with matching
 * valuation.  Usage: ./d3val PROBS K1SOLS D2DISTINCT */
#include "b3lc.h"
int main(int argc, char **argv){
  g_rng = 77;
  static u32 P[200000][10]; int np = 0; char line[512];
  FILE *fp = fopen(argv[1], "r");
  while (fgets(line, sizeof line, fp) && np < 200000){ u32 *q = P[np];
    if (sscanf(line, "%x %x %x %x %x %x %x %x %x %x", q, q+1, q+2, q+3, q+4, q+5, q+6, q+7, q+8, q+9) == 10) np++; }
  fclose(fp);
  u32 D2[2048]; int nd = 0; FILE *fd = fopen(argv[3], "r");
  while (fgets(line, sizeof line, fd) && nd < 2048) D2[nd++] = (u32)strtoul(line, 0, 16);
  fclose(fd);
  FILE *fs = fopen(argv[2], "r"); int vm[33] = {0}, n = 0; long tried = 0, pos = 0;
  while (fgets(line, sizeof line, fs)){
    unsigned prob, which; u32 h5, thi, dm2, dv6, A1; unsigned long long ns;
    if (sscanf(line, "%u %x %x %x %x %x %u %llu", &prob, &h5, &thi, &dm2, &dv6, &A1, &which, &ns) != 8) continue;
    K1sol s1; if (!k1_try(h5, thi, A1, dm2, dv6, (int)which, &s1, 1)) continue;
    u32 M = s1.v9 - s1.v9p; int v = M ? __builtin_ctz(M) : 32; vm[v]++; n++;
    /* D3(i) exact counts against every D in -D2 with v2(D) == v2(M), v14 pair from a random 32-bit v14 and the K2
     * eta of that dm4 is unknown here, so use eta = 0 (v14 == v14'): pure test of the A-chain */
    for (int j = 0; j < nd; j++){
      u32 D = 0u - D2[j]; if (!D || __builtin_ctz(D) != v) continue;
      u32 v14 = (u32)rnd64(); u64 cnt; tried++;
      if (rotdp(v14, v14, D, 16, M, 0, 0, &cnt)) pos++;
    }
  }
  printf("K1 solutions %d; v2(M) histogram:", n); for (int i = 0; i <= 32; i++) if (vm[i]) printf(" %d:%d", i, vm[i]); printf("\n");
  printf("D3(i) with eta = 0 and D in -D2 of matching valuation: %ld tried, %ld solvable\n", tried, pos);
  return 0;
}
