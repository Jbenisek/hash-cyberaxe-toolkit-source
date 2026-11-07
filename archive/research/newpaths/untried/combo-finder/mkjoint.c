/* mkjoint.c -- JOINT K3xK2 problems for K1.  Reads K3 records "A3 delta D nsol hit" (hit=1 means -D in D2),
 * scans the D2 record file for every (dm4 = -D, A2), samples NCUBE K2 cube elements per A2 and writes one K1 problem
 * per distinct dv6:  h5 thi dm2 dv6 A3 delta D dm4 A2 d2   (h5 = IV5, root instance).
 * Usage: ./mkjoint K3RECS D2REC NCUBE THI OUT */
#include "b3lc.h"
#define MAXJ 4096
int main(int argc, char **argv){
  if (argc < 6) return 1;
  g_rng = 0x1A2B3C;
  FILE *fk = fopen(argv[1], "r"); int ncube = atoi(argv[3]); u32 thi = (u32)strtoul(argv[4], 0, 0);
  u32 A3[MAXJ], dl[MAXJ], D[MAXJ]; int nj = 0; char line[256];
  while (fgets(line, sizeof line, fk) && nj < MAXJ){
    u32 a, d, DD; unsigned long long ns; unsigned hit;
    if (sscanf(line, "%x %x %x %llu %u", &a, &d, &DD, &ns, &hit) == 5 && hit){ A3[nj] = a; dl[nj] = d; D[nj] = DD; nj++; }
  }
  fclose(fk);
  fprintf(stderr, "joint K3 solutions: %d\n", nj);
  FILE *fr = fopen(argv[2], "rb"); FILE *fo = fopen(argv[5], "w");
  u32 r[2]; long found = 0, probs = 0;
  static u32 buf[1 << 20][2];
  size_t got;
  while ((got = fread(buf, sizeof(u32) * 2, 1 << 20, fr)) > 0){
    for (size_t i = 0; i < got; i++){
      u32 dm4 = buf[i][0], A2 = buf[i][1];
      for (int j = 0; j < nj; j++){
        if (dm4 != 0u - D[j]) continue;
        found++;
        u32 seen[256]; int ns = 0;
        for (int c = 0; c < ncube && ns < 256; c++){
          K2sol s; if (!k2_b(B3IV[6], 64, A2, dm4, &s)) break;
          u32 dv6 = s.v6p - s.v6; int dup = 0;
          for (int t = 0; t < ns; t++) if (seen[t] == dv6) { dup = 1; break; }
          if (dup) continue;
          seen[ns++] = dv6; probs++;
          fprintf(fo, "%08x %08x %08x %08x %08x %08x %08x %08x %08x %08x\n", B3IV[5], thi, 0u - dl[j], dv6, A3[j], dl[j], D[j], dm4, A2, s.d2);
        }
        fprintf(stderr, "joint %d: A2=%08x dm4=%08x distinct dv6 %d\n", j, A2, dm4, ns);
      }
    }
  }
  (void)r;
  fprintf(stderr, "K2 bases found %ld, K1 problems %ld\n", found, probs);
  fclose(fr); fclose(fo); return 0;
}
