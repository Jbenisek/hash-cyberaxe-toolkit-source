/* k3_scan.c -- stage K3 of the {m2,m3,m4,m6} message-only local collision, fixed IV (exact).
 *
 * K3 = G(v3=h3, v7=h7, v11=IV3, v15=flags; x=m6, y=m7), message pair (x, y) / (x+dx, y).
 * Wanted: b2 and d2 equal for the pair (S7, S15 equal), a2 and c2 differ.
 * For each x: with z = a2 = A + y, the d2 condition is z ^ (z + dA) = d1 ^ d1' and the b2 condition
 * is w ^ (w + dc) = b1 ^ b1' with w = c1 + ROR(d1 ^ z, 8); both are carry-automaton sets, so a
 * word test rejects almost every x and a 32-step DFS enumerates the rest.  Every hit is verified
 * on the real G.
 * Usage: k3_scan <flags> <dx hex> [x_lo hex] [x_hi hex] [h7 hex]   (h7 default IV7: the root block)
 */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

typedef uint32_t u32;
static const u32 IV[8] = {0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au,
                          0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u};
static inline u32 ror(u32 v, int n) { return (v >> n) | (v << (32 - n)); }
static inline int compat(u32 delta, u32 D) {
  u32 c = D ^ delta;
  if (c & 1u) return 0;
  u32 eq = ~(delta ^ c);
  return ((((c >> 1) ^ delta) & eq) & 0x7FFFFFFFu) == 0;
}
static void g(u32 *a, u32 *b, u32 *c, u32 *d, u32 x, u32 y) {
  *a = *a + *b + x; *d = ror(*d ^ *a, 16); *c = *c + *d; *b = ror(*b ^ *c, 12);
  *a = *a + *b + y; *d = ror(*d ^ *a, 8);  *c = *c + *d; *b = ror(*b ^ *c, 7);
}

static int nsol;
static u32 zs[256];
static u32 g_c1, g_d1, g_zm, g_zv, g_wm, g_wv;
static void dfs(int j, u32 z, int carry) {
  if (j == 32) { if (nsol < 256) zs[nsol] = z; nsol++; return; }
  int i = (j + 8) & 31;
  for (int zb = 0; zb < 2; zb++) {
    if (((g_zm >> i) & 1u) && (u32)zb != ((g_zv >> i) & 1u)) continue;
    int tj = (int)((g_d1 >> i) & 1u) ^ zb;
    int cj = (int)((g_c1 >> j) & 1u);
    int wj = cj ^ tj ^ carry;
    if (((g_wm >> j) & 1u) && (u32)wj != ((g_wv >> j) & 1u)) continue;
    int nc = (cj & tj) | (cj & carry) | (tj & carry);
    dfs(j + 1, z | ((u32)zb << i), nc);
  }
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: k3_scan flags dx [xlo xhi]\n"); return 1; }
  u32 flags = (u32)strtoul(argv[1], 0, 0);
  u32 dx = (u32)strtoul(argv[2], 0, 16);
  unsigned long long xlo = argc > 3 ? strtoull(argv[3], 0, 16) : 0ull;
  unsigned long long xhi = argc > 4 ? strtoull(argv[4], 0, 16) : 0x100000000ull;
  const u32 h3 = IV[3], c0 = IV[3];
  const u32 h7 = argc > 5 ? (u32)strtoul(argv[5], 0, 16) : IV[7];
  unsigned long long pass1 = 0, pass2 = 0, passb = 0, hits = 0, verified = 0;
  clock_t t0 = clock();
  for (unsigned long long xx = xlo; xx < xhi; xx++) {
    u32 x = (u32)xx, xp = x + dx;
    u32 a1 = h3 + h7 + x, a1p = h3 + h7 + xp;
    u32 d1 = ror(flags ^ a1, 16), d1p = ror(flags ^ a1p, 16);
    u32 c1 = c0 + d1, c1p = c0 + d1p;
    u32 b1 = ror(h7 ^ c1, 12), b1p = ror(h7 ^ c1p, 12);
    u32 A = a1 + b1, Ap = a1p + b1p, dA = Ap - A, D = d1 ^ d1p;
    u32 dc = c1p - c1, B = b1 ^ b1p;
    int okb = compat(dc, B);
    passb += (unsigned long long)okb;
    if (!compat(dA, D)) continue;
    pass1++;
    if (!okb) continue;
    pass2++;
    u32 cz = D ^ dA, cw = B ^ dc;
    g_zm = (dA ^ cz) & 0x7FFFFFFFu; g_zv = (cz >> 1) & g_zm;
    g_wm = (dc ^ cw) & 0x7FFFFFFFu; g_wv = (cw >> 1) & g_wm;
    g_c1 = c1; g_d1 = d1; nsol = 0;
    dfs(0, 0u, 0);
    for (int k = 0; k < nsol && k < 256; k++) {
      u32 y = zs[k] - A;
      u32 a = h3, b = h7, c = c0, d = flags, ap = h3, bp = h7, cc = c0, dp = flags;
      g(&a, &b, &c, &d, x, y);
      g(&ap, &bp, &cc, &dp, xp, y);
      hits++;
      if (b == bp && d == dp && a != ap && c != cc) {
        verified++;
        if (verified <= 8)
          printf("HIT x=%08x y=%08x  S3=%08x/%08x  dS3=%08x  S11=%08x/%08x  S7=%08x S15=%08x\n",
                 x, y, a, ap, ap - a, c, cc, b, d);
      }
    }
  }
  double secs = (double)(clock() - t0) / CLOCKS_PER_SEC;
  printf("h7=%08x flags=%u dx=%08x x-range=[%llx,%llx) pass_d2test=%llu pass_b2test_alone=%llu pass_both=%llu candidates=%llu verified=%llu time=%.1fs\n",
         h7, flags, dx, xlo, xhi, pass1, passb, pass2, hits, verified, secs);
  return 0;
}
