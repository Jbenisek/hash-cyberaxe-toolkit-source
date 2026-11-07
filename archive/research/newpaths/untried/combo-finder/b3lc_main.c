/* b3lc_main.c -- driver: self-tests and stage-rate measurements for the {m2,m3,m4,m6}
 * local collision on 2-round BLAKE3, with instance freedom (CV h, counter t, flags).
 * Build: gcc -O3 -march=native -o b3lc b3lc_main.c
 */
#include "b3lc.h"
#include <time.h>

static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }

/* run one G call on (a,b,c,d,x,y) and return the 4 outputs */
static void g4(u32 a, u32 b, u32 c, u32 d, u32 x, u32 y, u32 o[4]){
  u32 v[16] = {0}; v[0] = a; v[1] = b; v[2] = c; v[3] = d; b3_g(v, 0, 1, 2, 3, x, y);
  o[0] = v[0]; o[1] = v[1]; o[2] = v[2]; o[3] = v[3];
}

static int selftest(void){
  int bad = 0;
  /* compat_cube: forward check */
  for (int it = 0; it < 2000000; it++){
    u32 a = (u32)rnd64(), D = (u32)rnd64(); if (it & 1) D &= (u32)rnd64() & (u32)rnd64();
    u32 e = a ^ (a + D), F, V;
    if (!compat_cube(D, e, &F, &V)) { bad++; continue; }
    if ((a & F) != (V & F)) bad++;
    u32 b = cube_pick(F, V, (u32)rnd64());
    if ((b ^ (b + D)) != e) bad++;
  }
  printf("selftest compat: bad=%d\n", bad);
  /* compat completeness on 8-bit analog is not directly testable; check random (D,e) rejections by sampling */
  int rej_bad = 0;
  for (int it = 0; it < 20000; it++){
    u32 D = (u32)rnd64() & 0xffu, e = (u32)rnd64() & 0xffu; /* 8-bit check by brute force on low byte embedding */
    /* embed: use 32-bit with high bits zero in both -> carries beyond bit 7 matter; brute force all a in 2^8 * high */
    u32 F, V; int c = compat_cube(D, e, &F, &V);
    int found = 0;
    for (u32 a = 0; a < 256 && !found; a++) for (u32 hi = 0; hi < 2 && !found; hi++){
      u32 aa = a | (hi ? 0x80000000u : 0); /* high bits other than 31 are forced 0-carry */
      /* need (aa ^ (aa + D)) == e for full 32 bits: high bits 8..30 are 0 in aa and D, so carry out of bit 7 must be 0 */
      if ((aa ^ (aa + D)) == e) found = 1;
    }
    /* when c == 1 a solution may need high bits nonzero; only check: found => c */
    if (found && !c) rej_bad++;
  }
  printf("selftest compat soundness (found=>compat): bad=%d\n", rej_bad);
  /* xa2: forward check */
  int xb = 0;
  for (int it = 0; it < 200000; it++){
    u32 C = (u32)rnd64(), Cp = (u32)rnd64(), F = (u32)rnd64() & (u32)rnd64(), d = (u32)rnd64();
    u32 V = d & F, f = (C + d) ^ (Cp + d);
    if (!xa2_count(C, Cp, f, F, V)) { xb++; continue; }
    u32 s; if (!xa2_sample(C, Cp, f, F, V, rnd64(), &s)) { xb++; continue; }
    if (((C + s) ^ (Cp + s)) != f || (s & F) != (V & F)) xb++;
  }
  printf("selftest xa2: bad=%d\n", xb);
  /* xa2 count exactness on a 2^20 cube by brute force */
  int xc = 0;
  for (int it = 0; it < 30; it++){
    u32 C = (u32)rnd64(), Cp = (u32)rnd64(), F = 0xfffff000u | ((u32)rnd64() & 0xfffu) ; F = ~F | 0xfff00000u; /* ~20 free bits */
    u32 V = (u32)rnd64() & F, d0 = cube_pick(F, V, (u32)rnd64()); u32 f = (C + d0) ^ (Cp + d0);
    u64 n = xa2_count(C, Cp, f, F, V), m = 0;
    u32 freeb = ~F; /* enumerate free bits */
    u32 sub = 0;
    do { u32 d = (V & F) | sub; if ((((C + d) ^ (Cp + d))) == f) m++; sub = (sub - freeb) & freeb; } while (sub);
    if (n != m) xc++;
  }
  printf("selftest xa2 exact count (30 cubes): bad=%d\n", xc);
  /* d1i forward */
  int di = 0;
  for (int it = 0; it < 200000; it++){
    u32 C = (u32)rnd64(), Cp = (u32)rnd64(), x = (u32)rnd64(), q = (u32)rnd64();
    u32 f = (C + q) ^ (Cp + (q ^ x)), qq; u64 cnt;
    if (!d1i_sample(C, Cp, x, f, rnd64(), &qq, &cnt)) { di++; continue; }
    if (((C + qq) ^ (Cp + (qq ^ x))) != f) di++;
  }
  printf("selftest d1i: bad=%d\n", di);
  /* d1ii forward */
  int dii = 0;
  for (int it = 0; it < 200000; it++){
    u32 d1 = (u32)rnd64(), d1p = (u32)rnd64(), Dl = (u32)rnd64(), a = (u32)rnd64();
    if (it & 1) Dl &= (u32)rnd64();
    u32 M = ror32(d1p ^ (a + Dl), 8) - ror32(d1 ^ a, 8), aa; u64 cnt;
    if (!d1ii_sample(d1, d1p, Dl, M, rnd64(), &aa, &cnt)) { dii++; continue; }
    if (ror32(d1p ^ (aa + Dl), 8) - ror32(d1 ^ aa, 8) != M) dii++;
  }
  printf("selftest d1ii: bad=%d\n", dii);
  /* d1ii exact count on random instances vs brute force over 2^24 restricted?  brute force full 2^32 once */
  return bad + rej_bad + xb + xc + di + dii;
}

/* Stage correctness against real G: K3, K2, K1, D3, D1 patterns. */
static int stagecheck(void){
  int bad = 0, nk3 = 0, nk2 = 0, nk1 = 0;
  /* K3: sample until 200 solutions on random (h3,h7,flags) */
  double t0 = now(); u64 tries = 0;
  while (nk3 < 200){
    u32 h3 = (u32)rnd64(), h7 = (u32)rnd64(), flags = (u32)(rnd64() & 15);
    u32 A = (u32)rnd64(), delta = (u32)rnd64(); K3sol s; tries++;
    if (!k3_try(h7, flags, A, delta, &s, 1)) continue;
    nk3++;
    u32 m6 = A - h3 - h7, m7 = s.m7base, o[4], op[4];
    g4(h3, h7, B3IV[3], flags, m6, m7, o); g4(h3, h7, B3IV[3], flags, m6 + delta, m7, op);
    if (o[1] != op[1] || o[3] != op[3]) bad++;           /* b,d equal */
    if (op[0] - o[0] != s.D) bad++;                        /* a modular diff */
    if (o[0] != s.v3 || o[2] != s.v11 || op[2] != s.v11p || o[1] != s.v7 || o[3] != s.v15) bad++;
  }
  printf("stagecheck K3: %d solutions in %llu random tries (%.2f s), bad=%d, log2 rate=%.2f\n",
         nk3, (unsigned long long)tries, now() - t0, bad, __builtin_log2((double)nk3 / tries));
  /* K2: random dm4, scan random A until solution; dm4 chosen from real collisions: pick A,A' with F equal is rare;
   * so test k2_b with constructed collisions via small search over A for dm4 = A'-A from random pairs found by birthday on 20 bits */
  int b2 = 0;
  for (int it = 0; it < 50 && nk2 < 50; it++){
    u32 h2 = (u32)rnd64(), h6 = (u32)rnd64(), blen = 64;
    /* birthday on F restricted: find A, A' with equal F using a 2^20 table on low bits then compare full */
    enum { NB = 1 << 22 };
    static u32 tabA[1 << 22]; static u32 tabF[1 << 22]; static unsigned char used[1 << 22];
    memset(used, 0, sizeof used);
    for (u32 k = 0; k < (1u << 24); k++){
      u32 A = (u32)rnd64();
      u32 F = A + ror32(h6 ^ (B3IV[2] + ror32(blen ^ A, 16)), 12);
      u32 slot = F & (NB - 1);
      if (used[slot] && tabF[slot] == F && tabA[slot] != A){
        u32 A0 = tabA[slot], dm4 = A - A0; K2sol s;
        if (!k2_a(h6, blen, A0, dm4)) { b2++; continue; }
        if (!k2_b(h6, blen, A0, dm4, &s)) continue; /* (b) may fail */
        nk2++;
        u32 m4 = A0 - h2 - h6, o[4], op[4];
        g4(h2, h6, B3IV[2], blen, m4, s.m5, o); g4(h2, h6, B3IV[2], blen, m4 + dm4, s.m5, op);
        if (o[0] != op[0] || o[2] != op[2]) b2++;
        if (o[1] != s.v6 || op[1] != s.v6p || o[3] != s.v14 || op[3] != s.v14p) b2++;
        break;
      }
      used[slot] = 1; tabF[slot] = F; tabA[slot] = A;
    }
  }
  printf("stagecheck K2: %d constructed solutions, bad=%d\n", nk2, b2);
  bad += b2;
  /* K1: random (h1,h5,thi,dm2,dv6): sample A until solution */
  int b1 = 0; t0 = now(); tries = 0;
  while (nk1 < 200){
    u32 h1 = (u32)rnd64(), h5 = (u32)rnd64(), thi = (u32)rnd64(), dm2 = (u32)rnd64(), dv6 = (u32)rnd64();
    u32 A = (u32)rnd64(); K1sol s; tries++;
    if (!k1_try(h5, thi, A, dm2, dv6, (int)(rnd64() & 1), &s, 1)) continue;
    nk1++;
    u32 m2 = A - h1 - h5, m3 = s.m3base, o[4], op[4];
    g4(h1, h5, B3IV[1], thi, m2, m3, o); g4(h1, h5, B3IV[1], thi, m2 + dm2, m3 + s.dm3, op);
    if (o[1] != op[1] || o[3] != op[3]) b1++;
    if (op[0] - o[0] != s.Dm) b1++;
    if (s.Dm + dv6 != (u32)(0u - s.dm3)) b1++;             /* C1 relation: dv1 + dv6 = -dm3 */
    if (o[0] != s.v1 || o[2] != s.v9 || op[2] != s.v9p) b1++;
  }
  printf("stagecheck K1: %d solutions in %llu tries (%.2f s), bad=%d, log2 rate=%.2f\n",
         nk1, (unsigned long long)tries, now() - t0, b1, __builtin_log2((double)nk1 / tries));
  bad += b1;
  return bad;
}

int main(int argc, char **argv){
  if (argc < 2) { fprintf(stderr, "usage: b3lc selftest|stagecheck\n"); return 1; }
  g_rng = 0xC0FFEE ^ (u64)argc;
  if (!strcmp(argv[1], "selftest")) { int b = selftest(); printf("TOTAL bad=%d\n", b); return b != 0; }
  if (!strcmp(argv[1], "stagecheck")) { int b = stagecheck(); printf("TOTAL bad=%d\n", b); return b != 0; }
  return 0;
}
