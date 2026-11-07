/* k3_general.c -- is the K3 pattern possible at all?  G with input (a,b,c,d) equal for both
 * messages, x differing by dx, y equal; wanted b2 and d2 equal (a2, c2 differing).
 * Necessary and sufficient (given x): z ^ (z + dA) = d1 ^ d1' has a solution z = a2 (d2 test) and
 * w ^ (w + dc) = b1 ^ b1' has a solution w = c2 (b2 test), jointly linked through
 * w = c1 + ROR(d1 ^ z, 8).  Here only the two necessary word tests are counted, over random inputs,
 * to see whether they ever pass together.
 * Usage: k3_general <log2 trials> <seed> [mode]   mode 0: all random; 1: c = IV3 fixed; 2: c = IV3 and dx fixed per 2^20 block
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>
#include <math.h>

typedef uint32_t u32;
typedef uint64_t u64;
static inline u32 ror(u32 v, int n) { return (v >> n) | (v << (32 - n)); }
static inline int compat(u32 delta, u32 D) {
  u32 c = D ^ delta;
  if (c & 1u) return 0;
  u32 eq = ~(delta ^ c);
  return ((((c >> 1) ^ delta) & eq) & 0x7FFFFFFFu) == 0;
}
static u64 s;
static inline u64 rnd(void) { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }

int main(int argc, char **argv) {
  int lg = argc > 1 ? atoi(argv[1]) : 30;
  s = argc > 2 ? strtoull(argv[2], 0, 0) : 88172645463325252ull;
  int mode = argc > 3 ? atoi(argv[3]) : 0;
  u64 n = 1ull << lg, pd = 0, pb = 0, both = 0;
  u32 blockdx = 1u;
  clock_t t0 = clock();
  for (u64 t = 0; t < n; t++) {
    u64 r1 = rnd(), r2 = rnd(), r3 = rnd();
    u32 a = (u32)r1, b = (u32)(r1 >> 32), c = (u32)r2, d = (u32)(r2 >> 32);
    u32 x = (u32)r3, dx = (u32)(r3 >> 32);
    if (!dx) dx = 1u;
    if (mode >= 1) c = 0xA54FF53Au;
    if (mode == 3) d = 11u;
    if (mode == 4) d = 0u;
    if (mode == 2) { if ((t & 0xFFFFFull) == 0) { blockdx = (u32)rnd(); if (!blockdx) blockdx = 1u; } dx = blockdx; }
    u32 xp = x + dx;
    u32 a1 = a + b + x, a1p = a + b + xp;
    u32 d1 = ror(d ^ a1, 16), d1p = ror(d ^ a1p, 16);
    u32 c1 = c + d1, c1p = c + d1p;
    u32 b1 = ror(b ^ c1, 12), b1p = ror(b ^ c1p, 12);
    u32 dA = (a1p + b1p) - (a1 + b1), D = d1 ^ d1p, dc = c1p - c1, B = b1 ^ b1p;
    int okd = compat(dA, D), okb = compat(dc, B);
    pd += (u64)okd; pb += (u64)okb; both += (u64)(okd & okb);
    if (okd && okb && both <= 12) printf("JOINT a=%08x b=%08x c=%08x d=%08x x=%08x dx=%08x a1=%08x lsb(dx)=%d lsb(D)=%d\n", a, b, c, d, x, dx, a1, __builtin_ctz(dx), __builtin_ctz(D));
  }
  double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
  double fd = (double)pd / (double)n, fb = (double)pb / (double)n;
  printf("mode=%d trials=2^%d d2test=%llu (2^%.2f) b2test=%llu (2^%.2f) both=%llu expected-if-independent=%.1f time=%.1fs\n",
         mode, lg, (unsigned long long)pd, log2(fd), (unsigned long long)pb, log2(fb),
         (unsigned long long)both, fd * fb * (double)n, secs);
  return 0;
}
