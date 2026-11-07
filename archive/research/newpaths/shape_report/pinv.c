/* pinv.c - loose end from shape_verify_outlandish_0 (aside, GUESS): the P-invariant family
   (m constant on the two 8-cycles of the message permutation; 2 free words a, b) showed 5 colliding
   pairs on output group (0,1,3,7) at w=8 vs 0.5 expected.  The family is deterministic, so a new seed
   cannot test it.  Here: enumerate the WHOLE family at w = 6, 8, 10, 12 (2^(2w) members), count
   colliding pairs on all 70 four-word output groups (expected 0.5 each, 35 in total), and list the
   (0,1,3,7) pairs at w = 8.  Toy conventions = shape_odd/toy.py: rot floor(r*w/32) of (16,12,8,7),
   IV low w bits, v12..15 = 0, 0, 2w, 11.
   usage: pinv <w> [cv_xor]   (cv_xor: xor into IV words of the chaining value, as an IV-sensitivity control) */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

static const uint32_t IV32[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const int PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static const int COLS[4][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15}};
static const int DIAG[4][4] = {{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};
static int W; static uint32_t MASK; static int R[4];

static uint32_t ror(uint32_t z, int r) { r %= W; if (!r) return z & MASK; return ((z >> r) | (z << (W - r))) & MASK; }
static void G(uint32_t *v, const int *ix, uint32_t x, uint32_t y) {
  uint32_t a = v[ix[0]], b = v[ix[1]], c = v[ix[2]], d = v[ix[3]];
  a = (a + b + x) & MASK; d = ror(d ^ a, R[0]); c = (c + d) & MASK; b = ror(b ^ c, R[1]);
  a = (a + b + y) & MASK; d = ror(d ^ a, R[2]); c = (c + d) & MASK; b = ror(b ^ c, R[3]);
  v[ix[0]] = a; v[ix[1]] = b; v[ix[2]] = c; v[ix[3]] = d;
}
static void compress(const uint32_t *m, uint32_t cvx, uint32_t *out) {
  uint32_t v[16], s[16];
  for (int i = 0; i < 8; i++) v[i] = (IV32[i] ^ cvx) & MASK;
  for (int i = 0; i < 4; i++) v[8 + i] = IV32[i] & MASK;
  v[12] = 0; v[13] = 0; v[14] = (2 * W) & MASK; v[15] = 11 & MASK;
  for (int r = 0; r < 2; r++) {
    for (int i = 0; i < 16; i++) s[i] = r ? m[PERM[i]] : m[i];
    for (int j = 0; j < 4; j++) G(v, COLS[j], s[2 * j], s[2 * j + 1]);
    for (int j = 0; j < 4; j++) G(v, DIAG[j], s[8 + 2 * j], s[9 + 2 * j]);
  }
  for (int i = 0; i < 8; i++) out[i] = v[i] ^ v[i + 8];
}
static int cmpu(const void *p, const void *q) { uint64_t a = *(const uint64_t *)p, b = *(const uint64_t *)q; return a < b ? -1 : a > b; }

int main(int argc, char **argv) {
  W = atoi(argv[1]); uint32_t cvx = argc > 2 ? (uint32_t)strtoul(argv[2], 0, 0) : 0;
  MASK = (W == 32) ? 0xffffffffu : ((1u << W) - 1);
  int base[4] = {16, 12, 8, 7}; for (int i = 0; i < 4; i++) R[i] = base[i] * W / 32;
  /* self-check at w=32 against the hand value used in shape_odd/toy.py */
  { int sw = W; uint32_t sm = MASK; int sr[4] = {R[0],R[1],R[2],R[3]};
    W = 32; MASK = 0xffffffffu; R[0]=16;R[1]=12;R[2]=8;R[3]=7;
    uint32_t v[4] = {0x6A09E667u, 0x510E527Fu, 0x6A09E667u, 0}; int ix[4] = {0,1,2,3};
    G(v, ix, 0, 0);
    if (!(v[0]==0xEB2778D5u && v[1]==0x5A8196B9u && v[2]==0x70C46342u && v[3]==0xCDD3C1C3u)) { printf("G SELFCHECK FAIL\n"); return 1; }
    W = sw; MASK = sm; for (int i=0;i<4;i++) R[i]=sr[i]; }
  int orbA[8] = {0,2,3,10,12,9,11,5};
  uint64_t N = 1ull << (2 * W);
  int SH = (6 * W <= 64) ? 2 * W : 0;  /* keep member index in the key only when it fits */
  uint32_t *out = malloc(N * 8 * sizeof(uint32_t)); uint64_t *key = malloc(N * sizeof(uint64_t));
  if (!out || !key) { printf("alloc fail\n"); return 1; }
  for (uint64_t t = 0; t < N; t++) {
    uint32_t a = (uint32_t)(t & MASK), b = (uint32_t)(t >> W), m[16];
    for (int i = 0; i < 16; i++) m[i] = b;
    for (int i = 0; i < 8; i++) m[orbA[i]] = a;
    compress(m, cvx, out + 8 * t);
  }
  double total = 0, maxr = 0; int maxg[4] = {0};
  printf("# P-invariant family, w=%d, cv_xor=0x%x, members 2^%d; per 4-word group: colliding pairs (expected %.3f)\n",
         W, cvx, 2 * W, (double)N * (N - 1) / 2 / (double)(1ull << (4 * W)));
  for (int g0 = 0; g0 < 8; g0++) for (int g1 = g0 + 1; g1 < 8; g1++) for (int g2 = g1 + 1; g2 < 8; g2++) for (int g3 = g2 + 1; g3 < 8; g3++) {
    int gg[4] = {g0, g1, g2, g3};
    for (uint64_t t = 0; t < N; t++) { uint64_t k = 0; for (int i = 0; i < 4; i++) k |= (uint64_t)out[8 * t + gg[i]] << (i * W); key[t] = SH ? ((k << SH) | t) : k; }
    qsort(key, N, sizeof(uint64_t), cmpu);
    double pairs = 0; uint64_t run = 1;
    for (uint64_t t = 1; t <= N; t++) {
      if (t < N && (key[t] >> SH) == (key[t - 1] >> SH)) { run++; continue; }
      if (run > 1) {
        pairs += (double)run * (run - 1) / 2;
        if (W == 8 && g0 == 0 && g1 == 1 && g2 == 3 && g3 == 7)
          for (uint64_t u = t - run; u < t; u++) printf("   (0,1,3,7) member a=%02x b=%02x\n", (unsigned)(key[u] & MASK), (unsigned)((key[u] >> W) & MASK));
      }
      run = 1;
    }
    total += pairs; if (pairs > maxr) { maxr = pairs; for (int i = 0; i < 4; i++) maxg[i] = gg[i]; }
    if ((g0 == 0 && g1 == 1 && g2 == 3 && g3 == 7) || (g0 == 0 && g1 == 2 && g2 == 5 && g3 == 7) || (g0 == 1 && g1 == 3 && g2 == 4 && g3 == 6))
      printf("group (%d,%d,%d,%d): %.0f pairs\n", g0, g1, g2, g3, pairs);
  }
  printf("w=%d cv_xor=0x%x: total pairs over 70 groups %.0f (expected %.1f); max group (%d,%d,%d,%d) %.0f\n",
         W, cvx, total, 70 * (double)N * (N - 1) / 2 / (double)(1ull << (4 * W)), maxg[0], maxg[1], maxg[2], maxg[3], maxr);
  return 0;
}
