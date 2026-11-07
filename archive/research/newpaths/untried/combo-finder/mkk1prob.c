/* mkk1prob.c -- build K1 test problems with provenance.
 * For each K3 solution line "A3 delta D nsol hit" and NPER random K2 solutions from the D2 records whose
 * v2(dm4) equals v2(D) (the valuation the joint route forces), draw one K2 cube element (d2) and write:
 *   h5 thi dm2 dv6  A3 delta D  dm4 A2 d2      (dm2 = -delta; dv6 = K2's b-output modular difference)
 * Stage-marginal: the K2 solution is not required to have dm4 = -D (that joint event is measured separately).
 * Usage: ./mkk1prob K3RECS D2REC NPER THI OUT */
#include "b3lc.h"
int main(int argc, char **argv){
  if (argc < 6) return 1;
  g_rng = 0xABCDEF;
  FILE *fk = fopen(argv[1], "r"); FILE *fr = fopen(argv[2], "rb"); int nper = atoi(argv[3]);
  u32 thi = (u32)strtoul(argv[4], 0, 0); FILE *fo = fopen(argv[5], "w");
  size_t cap = 1 << 24; u32 *recs[2]; size_t n[2] = {0, 0};
  recs[0] = malloc(sizeof(u32) * 2 * cap); recs[1] = malloc(sizeof(u32) * 2 * cap);
  u32 r[2];
  cap = 1 << 22;
  while (fread(r, sizeof r, 1, fr) == 1){
    if (!r[0]) continue; int v = __builtin_ctz(r[0]); if (v > 1) continue;
    if (n[v] < cap){ recs[v][2*n[v]] = r[0]; recs[v][2*n[v]+1] = r[1]; n[v]++; }
    if (n[0] >= cap && n[1] >= cap) break;
  }
  fprintf(stderr, "D2 records v2=0: %zu, v2=1: %zu\n", n[0], n[1]);
  char line[256]; int vh[33] = {0}, tot = 0;
  while (fgets(line, sizeof line, fk)){
    u32 A3, delta, D; unsigned long long ns; unsigned hit;
    if (sscanf(line, "%x %x %x %llu %u", &A3, &delta, &D, &ns, &hit) < 3) continue;
    int v = __builtin_ctz(D); if (v > 1 || !n[v]) continue;
    for (int k = 0; k < nper; k++){
      size_t j = rnd64() % n[v]; u32 dm4 = recs[v][2*j], A2 = recs[v][2*j+1]; K2sol s;
      if (!k2_b(B3IV[6], 64, A2, dm4, &s)) continue;
      u32 dv6 = s.v6p - s.v6; vh[dv6 ? __builtin_ctz(dv6) : 32]++; tot++;
      fprintf(fo, "%08x %08x %08x %08x %08x %08x %08x %08x %08x %08x\n", B3IV[5], thi, 0u - delta, dv6, A3, delta, D, dm4, A2, s.d2);
    }
  }
  fprintf(stderr, "problems %d; v2(dv6) hist:", tot); for (int i = 0; i <= 32; i++) if (vh[i]) fprintf(stderr, " %d:%d", i, vh[i]); fprintf(stderr, "\n");
  fclose(fo); return 0;
}
