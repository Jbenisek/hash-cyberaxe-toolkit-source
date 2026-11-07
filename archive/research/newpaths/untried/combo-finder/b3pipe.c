/* b3pipe.c -- full stage pipeline for the {m2,m3,m4,m6} local collision on 2-round BLAKE3.
 * Input: instance (h[8], t, blen=64, flags), a K3 solution (A3, delta) whose dm4 = -D is K2-solvable,
 * the D2 records file (dm4, A2) for the instance's K2.  Stages: K3 -> K2 -> K1 (2^32 scan) -> D3 (rotation
 * DP) -> D1 (DPs) -> C0 (compat) -> K0/D0 fill -> verify both blocks with the 2-round compression.
 * Usage: ./b3pipe ROOT|H0..H7 TLO THI FLAGS A3 DELTA D2REC [MAXK1SCANSEC]
 * Build: gcc -O3 -march=native -o b3pipe b3pipe.c -lm
 */
#include "b3lc.h"
#include <time.h>
#include <math.h>

static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }

typedef struct { u32 A; int which; u64 nsol; } K1hit;

int main(int argc, char **argv){
  setvbuf(stdout, NULL, _IOLBF, 0);
  if (argc < 8){ fprintf(stderr, "usage: b3pipe root TLO THI FLAGS A3 DELTA D2REC [SEED]\n"); return 1; }
  u32 h[8]; memcpy(h, B3IV, sizeof h);  /* root / block-0 instance: h = IV */
  u32 tlo = (u32)strtoul(argv[2], 0, 0), thi = (u32)strtoul(argv[3], 0, 0), flags = (u32)strtoul(argv[4], 0, 0);
  u32 A3 = (u32)strtoul(argv[5], 0, 0), delta = (u32)strtoul(argv[6], 0, 0);
  const char *d2rec = argv[7];
  g_rng = argc > 8 ? strtoull(argv[8], 0, 0) : 0x5EED;
  const u32 blen = 64;
  double t0 = now();
  /* ---- K3 ---- */
  K3sol k3; if (!k3_try(h[7], flags, A3, delta, &k3, 1)){ printf("K3 not a solution\n"); return 1; }
  u32 dm4 = 0u - k3.D;
  printf("K3 ok: A3=%08x delta=%08x D=%08x nsol=%llu\n", A3, delta, k3.D, (unsigned long long)k3.nsol);
  /* ---- K2: find A2 for dm4 in records ---- */
  FILE *f = fopen(d2rec, "rb"); if (!f){ perror(d2rec); return 1; }
  u32 rec[2]; int nA2 = 0; u32 A2list[64];
  while (fread(rec, sizeof rec, 1, f) == 1) if (rec[0] == dm4 && nA2 < 64) A2list[nA2++] = rec[1];
  fclose(f);
  if (!nA2){ printf("K2: dm4=%08x not in D2 records\n", dm4); return 1; }
  printf("K2: %d base values A2 for dm4=%08x\n", nA2, dm4);
  int attempts = 0, d3_i_any = 0, d3_ok = 0, d1_ok = 0, c0_ok = 0;
  u64 k1_total = 0;
  for (int ia = 0; ia < nA2; ia++){
    u32 A2 = A2list[ia];
    /* K2(b) cube: fix dv6 by choosing one d2, then vary d2 among values giving the same dv6 */
    K2sol k2;
    if (!k2_b(h[6], blen, A2, dm4, &k2)){ printf("K2(b) failed unexpectedly\n"); continue; }
    u32 dv6 = k2.v6p - k2.v6;
    printf("K2 ok: A2=%08x cube=2^%d dv6=%08x\n", A2, (int)log2((double)k2.cube), dv6);
    /* ---- K1 scan over all A1 (both dm3 roots) ---- */
    K1hit *hits = malloc(sizeof(K1hit) * 4096); int nh = 0; double tk = now();
    for (u64 a = 0; a < (1ULL << 32); a++){
      u32 A1 = (u32)a;
      for (int w = 0; w < 2; w++){
        K1sol s;
        if (k1_try(h[5], thi, A1, 0u - delta, dv6, w, &s, 0) && nh < 4096){ hits[nh].A = A1; hits[nh].which = w; hits[nh].nsol = s.nsol; nh++; }
      }
    }
    k1_total += nh;
    printf("K1 scan: %d solutions (A1, root) in %.1f s\n", nh, now() - tk);
    /* ---- for each K1 solution and K2/K3 cube choices: D3, D1, C0 ---- */
    for (int ih = 0; ih < nh; ih++){
      for (int rep = 0; rep < 4096; rep++){
        attempts++;
        /* re-draw K3 cube element (changes v11, v3 value), K2 d2 with same dv6, K1 cube element */
        K3sol s3; if (!k3_try(h[7], flags, A3, delta, &s3, 1)) continue;
        K2sol s2; if (!k2_b(h[6], blen, A2, dm4, &s2)) continue;
        if (s2.v6p - s2.v6 != dv6) continue;           /* keep the K1 problem fixed */
        K1sol s1; if (!k1_try(h[5], thi, hits[ih].A, 0u - delta, dv6, hits[ih].which, &s1, 1)) continue;
        /* D3: inputs v3 (dv3 = D), v9/v9p, v14/v14p */
        u32 dv3 = s3.D, Ad3; u64 c3;
        if (!rotdp(s2.v14, s2.v14p, dv3, 16, s1.v9 - s1.v9p, rnd64(), &Ad3, &c3)) continue;
        d3_i_any++;
        u32 F3, V3;
        if (!d3_ii(dv3, s2.v14, s2.v14p, Ad3, &F3, &V3)) continue;
        d3_ok++;
        /* D1: inputs v1 (diff Dm), v6 (diff), v11 (diff), v12 free.  Delta1 = Dm + dv6 */
        u32 Delta1 = s1.Dm + dv6;
        int got = 0;
        for (int tr = 0; tr < 256 && !got; tr++){
          u32 A = (u32)rnd64(), Ap = A + Delta1, q; u64 cq;
          u32 x = ror32(A ^ Ap, 16);
          if (!d1i_sample(s3.v11, s3.v11p, x, s2.v6 ^ s2.v6p, rnd64(), &q, &cq)) continue;
          u32 d1 = q, d1p = q ^ x;
          u32 c1 = s3.v11 + d1, c1p = s3.v11p + d1p;
          u32 M1 = c1 - c1p, a2; u64 ca;
          if (!rotdp(d1, d1p, Delta1, 8, M1, rnd64(), &a2, &ca)) continue;
          d1_ok++;
          u32 d2 = ror32(d1 ^ a2, 8), d2p = ror32(d1p ^ (a2 + Delta1), 8);
          /* C0: compat(dm2 = -delta, X12 ^ X12') */
          u32 Fc, Vc;
          if (!compat_cube(0u - delta, d2 ^ d2p, &Fc, &Vc)) continue;
          c0_ok++;
          got = 1;
          /* ===== assemble ===== */
          u32 m[16], mp[16];
          for (int i = 0; i < 16; i++) m[i] = 0;
          u32 v12 = rol32(q, 16) ^ A;           /* q = ror(v12 ^ A, 16) */
          /* K0: m0 = 0, choose m1 so that K0.d2 = v12 */
          u32 a1_0 = h[0] + h[4] + m[0], d1_0 = ror32(tlo ^ a1_0, 16), c1_0 = B3IV[0] + d1_0, b1_0 = ror32(h[4] ^ c1_0, 12);
          u32 a2_0 = rol32(v12, 8) ^ d1_0; m[1] = a2_0 - a1_0 - b1_0;
          u32 c2_0 = c1_0 + v12, v4 = ror32(b1_0 ^ c2_0, 7), v0 = a2_0;
          (void)v0;
          /* K1 */
          m[2] = s1.A - h[1] - h[5]; m[3] = s1.m3base;
          /* K2 */
          m[4] = A2 - h[2] - h[6]; m[5] = s2.m5;
          /* K3 */
          m[6] = A3 - h[3] - h[7]; m[7] = s3.m7base;
          /* D1 */
          m[10] = A - s1.v1 - s2.v6;
          { u32 b1 = ror32(s2.v6 ^ c1, 12); m[11] = a2 - A - b1; }
          /* D3 */
          m[14] = Ad3 - s3.v3 - v4;
          { u32 d1b = ror32(s2.v14 ^ Ad3, 16), c1b = s1.v9 + d1b, b1b = ror32(v4 ^ c1b, 12);
            u32 a2b = cube_pick(F3, V3, (u32)rnd64()); m[15] = a2b - Ad3 - b1b; }
          /* D0: m8 = 0, m9 chosen so C0's a1 lands in the compat cube.  Need X4 (D3.b2) and m2: run the
           * real compression on the partial message to read X0.., then solve m9. */
          {
            u32 st[16], out[16];
            /* compute state after round 0 with m9 = 0 to get D0 inputs and X4 */
            u32 v[16]; for (int i = 0; i < 8; i++) v[i] = h[i]; for (int i = 0; i < 4; i++) v[8 + i] = B3IV[i];
            v[12] = tlo; v[13] = thi; v[14] = blen; v[15] = flags;
            b3_g(v, 0, 4, 8, 12, m[0], m[1]); b3_g(v, 1, 5, 9, 13, m[2], m[3]);
            b3_g(v, 2, 6, 10, 14, m[4], m[5]); b3_g(v, 3, 7, 11, 15, m[6], m[7]);
            u32 a0 = v[0], b0 = v[5], c0 = v[10], dd0 = v[15];
            b3_g(v, 1, 6, 11, 12, m[10], m[11]); b3_g(v, 2, 7, 8, 13, m[12], m[13]); b3_g(v, 3, 4, 9, 14, m[14], m[15]);
            u32 X4 = v[4];
            u32 u = cube_pick(Fc, Vc, (u32)rnd64());          /* C0's a1 = X0 + X4 + m2 */
            u32 X0 = u - X4 - m[2];
            u32 a1d = a0 + b0 + m[8], d1d = ror32(dd0 ^ a1d, 16), c1d = c0 + d1d, b1d = ror32(b0 ^ c1d, 12);
            m[9] = X0 - a1d - b1d;
            (void)st; (void)out;
          }
          memcpy(mp, m, sizeof m);
          mp[2] = m[2] - delta; mp[3] = m[3] + s1.dm3; mp[4] = m[4] + dm4; mp[6] = m[6] + delta;
          u32 o1[16], o2[16], S1[16], S2[16];
          u64 counter = ((u64)thi << 32) | tlo;
          b3_compress(h, m, counter, blen, flags, 2, o1, S1);
          b3_compress(h, mp, counter, blen, flags, 2, o2, S2);
          int eq = 0; for (int i = 0; i < 16; i++) eq += (o1[i] == o2[i]);
          int eq8 = 0; for (int i = 0; i < 8; i++) eq8 += (o1[i] == o2[i]);
          printf("ASSEMBLED: output words equal %d/16 (first 8: %d/8)\n", eq, eq8);
          if (eq8 == 8){
            printf("COLLISION m :"); for (int i = 0; i < 16; i++) printf(" %08x", m[i]); printf("\n");
            printf("COLLISION m':"); for (int i = 0; i < 16; i++) printf(" %08x", mp[i]); printf("\n");
            printf("digest:"); for (int i = 0; i < 8; i++) printf(" %08x", o1[i]); printf("\n");
            printf("stats: attempts %d d3_i %d d3_ok %d d1_ok %d c0_ok %d, %.1f s\n", attempts, d3_i_any, d3_ok, d1_ok, c0_ok, now() - t0);
            return 0;
          } else {
            /* diagnose: which state words differ after the full 2 rounds */
            printf("  state diff words:"); for (int i = 0; i < 16; i++) if (S1[i] != S2[i]) printf(" %d", i); printf("\n");
          }
        }
      }
      if (now() - t0 > 1100) break;
    }
    free(hits);
    if (now() - t0 > 1100) break;
  }
  printf("no collision: attempts %d, K1 sols %llu, D3(i) %d, D3 ok %d, D1 ok %d, C0 ok %d, %.1f s\n",
         attempts, (unsigned long long)k1_total, d3_i_any, d3_ok, d1_ok, c0_ok, now() - t0);
  return 2;
}
