/* b3final.c -- final stages for the {m2,m3,m4,m6} local collision at the ROOT instance (h = IV, t = 0, b = 64,
 * flags 11, i.e. one 64-byte message): for each K1 solution of a JOINT problem (K2's dm4 = -D of K3), run
 * D3 (rotation DP + compat), D1 (DP + rotation DP), C0 (compat), fill K0 (m0,m1) and D0 (m8,m9), assemble both
 * blocks and verify all 16 output words with the 2-round compression.  Prints COLLISION lines if found.
 * Usage: ./b3final PROBS K1SOLS NCUBE */
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
  return 1;
}
int main(int argc, char **argv){
  if (argc < 4) return 1;
  setvbuf(stdout, NULL, _IOLBF, 0);
  g_rng = 0xF1A1F1A1;
  int ncube = atoi(argv[3]);
  const u32 *h = B3IV; const u32 tlo = 0, thi0 = 0, blen = 64, flags = 11;
  FILE *fp = fopen(argv[1], "r"); char line[512]; int np = 0; static u32 P[200000][10];
  while (fgets(line, sizeof line, fp) && np < 200000){
    u32 *q = P[np];
    if (sscanf(line, "%x %x %x %x %x %x %x %x %x %x", q, q+1, q+2, q+3, q+4, q+5, q+6, q+7, q+8, q+9) == 10) np++;
  }
  fclose(fp);
  FILE *fs = fopen(argv[2], "r");
  long nk1 = 0, d3i = 0, d3ok = 0, d1ok = 0, c0ok = 0, asm_ = 0;
  while (fgets(line, sizeof line, fs)){
    unsigned prob, which; u32 h5, thi, dm2, dv6, A1; unsigned long long ns;
    if (sscanf(line, "%u %x %x %x %x %x %u %llu", &prob, &h5, &thi, &dm2, &dv6, &A1, &which, &ns) != 8) continue;
    if ((int)prob >= np) continue;
    u32 *q = P[prob]; u32 A3 = q[4], delta = q[5], D = q[6], dm4 = q[7], A2 = q[8], d2base = q[9];
    if (dm4 != 0u - D || thi != thi0) { continue; } /* only joint problems at the root */
    nk1++;
    for (int c = 0; c < ncube; c++){
      K3sol s3; if (!k3_try(h[7], flags, A3, delta, &s3, 1)) break;
      K1sol s1; if (!k1_try(h5, thi, A1, dm2, dv6, (int)which, &s1, 1)) break;
      K2sol s2; u32 d2 = d2base;
      if (c){ K2sol tmp; if (!k2_b(h[6], blen, A2, dm4, &tmp)) continue; d2 = tmp.d2; }
      if (!k2_given(h[6], blen, A2, dm4, d2, &s2)) continue;
      if (s2.v6p - s2.v6 != dv6) continue;
      u32 M = s1.v9 - s1.v9p, Ad3;
      if (!rotdp(s2.v14, s2.v14p, D, 16, M, rnd64(), &Ad3, 0)) continue;
      d3i++;
      u32 F3, V3; int ok = 0;
      for (int t = 0; t < 64 && !ok; t++){
        if (t) rotdp(s2.v14, s2.v14p, D, 16, M, rnd64(), &Ad3, 0);
        if (d3_ii(D, s2.v14, s2.v14p, Ad3, &F3, &V3)) ok = 1;
      }
      if (!ok) continue;
      d3ok++;
      u32 Delta1 = s1.Dm + dv6;
      for (int tr = 0; tr < 65536; tr++){
        u32 A = (u32)rnd64(), Ap = A + Delta1, qq; u64 cq; u32 x = ror32(A ^ Ap, 16);
        if (!d1i_sample(s3.v11, s3.v11p, x, s2.v6 ^ s2.v6p, rnd64(), &qq, &cq)) continue;
        u32 d1 = qq, d1p = qq ^ x, c1 = s3.v11 + d1, c1p = s3.v11p + d1p, a2;
        if (!rotdp(d1, d1p, Delta1, 8, c1 - c1p, rnd64(), &a2, 0)) continue;
        d1ok++;
        u32 X12 = ror32(d1 ^ a2, 8), X12p = ror32(d1p ^ (a2 + Delta1), 8), Fc, Vc;
        if (!compat_cube(0u - delta, X12 ^ X12p, &Fc, &Vc)) continue;
        c0ok++;
        /* ===== assemble ===== */
        u32 m[16] = {0}, mp[16];
        u32 v12 = rol32(qq, 16) ^ A;
        u32 a1_0 = h[0] + h[4] + m[0], d1_0 = ror32(tlo ^ a1_0, 16), c1_0 = B3IV[0] + d1_0, b1_0 = ror32(h[4] ^ c1_0, 12);
        u32 a2_0 = rol32(v12, 8) ^ d1_0; m[1] = a2_0 - a1_0 - b1_0;
        u32 c2_0 = c1_0 + v12, v4 = ror32(b1_0 ^ c2_0, 7);
        m[2] = s1.A - h[1] - h[5]; m[3] = s1.m3base;
        m[4] = A2 - h[2] - h[6]; m[5] = s2.m5;
        m[6] = A3 - h[3] - h[7]; m[7] = s3.m7base;
        m[10] = A - s1.v1 - s2.v6; { u32 b1 = ror32(s2.v6 ^ c1, 12); m[11] = a2 - A - b1; }
        m[14] = Ad3 - s3.v3 - v4;
        { u32 d1b = ror32(s2.v14 ^ Ad3, 16), c1b = s1.v9 + d1b, b1b = ror32(v4 ^ c1b, 12);
          u32 a2b = cube_pick(F3, V3, (u32)rnd64()); m[15] = a2b - Ad3 - b1b; }
        { u32 v[16]; for (int i = 0; i < 8; i++) v[i] = h[i]; for (int i = 0; i < 4; i++) v[8 + i] = B3IV[i];
          v[12] = tlo; v[13] = thi; v[14] = blen; v[15] = flags;
          b3_g(v, 0, 4, 8, 12, m[0], m[1]); b3_g(v, 1, 5, 9, 13, m[2], m[3]);
          b3_g(v, 2, 6, 10, 14, m[4], m[5]); b3_g(v, 3, 7, 11, 15, m[6], m[7]);
          u32 a0 = v[0], b0 = v[5], c0 = v[10], dd0 = v[15];
          b3_g(v, 1, 6, 11, 12, m[10], m[11]); b3_g(v, 2, 7, 8, 13, m[12], m[13]); b3_g(v, 3, 4, 9, 14, m[14], m[15]);
          u32 X4 = v[4], u = cube_pick(Fc, Vc, (u32)rnd64()), X0 = u - X4 - m[2];
          u32 a1d = a0 + b0 + m[8], d1d = ror32(dd0 ^ a1d, 16), c1d = c0 + d1d, b1d = ror32(b0 ^ c1d, 12);
          m[9] = X0 - a1d - b1d; }
        memcpy(mp, m, sizeof m);
        mp[2] = m[2] + dm2; mp[3] = m[3] + s1.dm3; mp[4] = m[4] + dm4; mp[6] = m[6] + delta;
        u32 o1[16], o2[16], S1[16], S2[16];
        b3_compress(h, m, ((u64)thi << 32) | tlo, blen, flags, 2, o1, S1);
        b3_compress(h, mp, ((u64)thi << 32) | tlo, blen, flags, 2, o2, S2);
        asm_++;
        int eq = 0; for (int i = 0; i < 16; i++) eq += (o1[i] == o2[i]);
        printf("ASSEMBLED prob %u: output words equal %d/16; state diff words:", prob, eq);
        for (int i = 0; i < 16; i++) if (S1[i] != S2[i]) printf(" %d", i);
        printf("\n");
        if (eq == 16){
          printf("COLLISION m :"); for (int i = 0; i < 16; i++) printf(" %08x", m[i]); printf("\n");
          printf("COLLISION m':"); for (int i = 0; i < 16; i++) printf(" %08x", mp[i]); printf("\n");
          printf("digest:"); for (int i = 0; i < 8; i++) printf(" %08x", o1[i]); printf("\n");
          return 0;
        }
        break;
      }
    }
  }
  printf("b3final: joint K1 solutions %ld; D3(i) %ld; D3 ok %ld; D1 ok %ld; C0 ok %ld; assembled %ld\n", nk1, d3i, d3ok, d1ok, c0ok, asm_);
  return 2;
}
