/* k2check.c -- verify K2 solutions from the D2 record file on the real G call (root instance h = IV, blen 64):
 * outputs a,c equal; b,d differ and equal the model's values.  Also the 2-adic valuation histogram of dm4 over the
 * first N records and the density of v2(dm4) in {0,1}.  Usage: ./k2check D2REC N */
#include "b3lc.h"
int main(int argc, char **argv){
  FILE *f = fopen(argv[1], "rb"); long N = atol(argv[2]); u32 r[2]; long n = 0, bad = 0; long vh[33] = {0};
  g_rng = 99;
  while (n < N && fread(r, sizeof r, 1, f) == 1){
    u32 dm4 = r[0], A2 = r[1]; K2sol s;
    vh[dm4 ? __builtin_ctz(dm4) : 32]++;
    if (!k2_b(B3IV[6], 64, A2, dm4, &s)) { bad++; n++; continue; }
    u32 m4 = A2 - B3IV[2] - B3IV[6];
    u32 v[16] = {0}, w[16] = {0};
    v[0] = B3IV[2]; v[1] = B3IV[6]; v[2] = B3IV[2]; v[3] = 64; memcpy(w, v, sizeof v);
    b3_g(v, 0, 1, 2, 3, m4, s.m5); b3_g(w, 0, 1, 2, 3, m4 + dm4, s.m5);
    if (v[0] != w[0] || v[2] != w[2] || v[1] == w[1] || v[3] == w[3]) bad++;
    if (v[1] != s.v6 || w[1] != s.v6p || v[3] != s.v14 || w[3] != s.v14p) bad++;
    n++;
  }
  printf("k2check: %ld records, bad %ld\n  v2(dm4):", n, bad);
  for (int i = 0; i <= 32; i++) if (vh[i]) printf(" %d:%ld", i, vh[i]);
  printf("\n");
  return 0;
}
