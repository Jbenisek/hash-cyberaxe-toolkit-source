/* trunc_search.c -- word-level (truncated) difference search over the 2-round BLAKE3 compression.
 *
 * Every state word and message word is either inactive (zero difference) or active.
 * G is modelled operation by operation (a1, d1, c1, b1, a2, d2, c2, b2): an add/xor with no
 * active input is inactive, with exactly one active input is active, with two or more active
 * inputs may be either; the inactive outcome is a cancellation = one 32-bit word condition.
 * Output fold: digest word i = Z[i] ^ Z[i+8]; a collision needs all 8 inactive (both inactive,
 * or both active and cancelling = one condition).
 *
 * Steps: K (round-0 columns), D (round-0 diagonals), C (round-1 columns), E (round-1 diagonals).
 * Cost models (which word conditions are counted):
 *   A: E-step + fold only (the four-checks metric; K, D and C conditions taken as free)
 *   B: C + E + fold (round 1 counted, round 0 free)
 *   C: every step (no message modification at all, e.g. a parent whose words are child CVs)
 *
 * Usage: trunc_search <init_word | -1> <eLo> <eHi> <out.bin>
 *   init_word -1: message-only (no state difference; M = 0 skipped)
 *   init_word 14: block-length line (v14), 15 flags, 12 counter low, 0..3 CV row a.
 *   eLo..eHi: range of the 256 activity patterns of the round-1 diagonal message words.
 * Output: 65536 records x 10 bytes, record M (bit j = message word m_j active):
 *   A, B, C, A@X0, B@X0, C@X0, A_halfA, A_halfB, B_halfA, B_halfB   (200 = impossible / not run)
 *   X0 = the state after round 0 has no active word (the four-checks family).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

typedef uint8_t u8;
typedef uint16_t u16;
#define INF 200
#define N 65536
#define NREC 10

static u8 T[16][4][16];          /* [in][msg][out] min cancellations, INF impossible */
static u8 TF[2][4][16][16];      /* forward  [w][msg][src=in ][dst=out] */
static u8 TB[2][4][16][16];      /* backward [w][msg][src=out][dst=in ] */


static const int COLW[4][4] = {{0,4,8,12},{1,5,9,13},{2,6,10,14},{3,7,11,15}};
static const int DIAW[4][4] = {{0,5,10,15},{1,6,11,12},{2,7,8,13},{3,4,9,14}};
static const int PERM[16] = {2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};

static u16 GRP[2][N];
static u16 P_sc_gd[N], P_sd_sc[N], P_gd_gc[N];

static inline u16 swp(u16 x) { return (u16)((x >> 8) | ((x & 0xFF) << 8)); }
static inline int msgact(int M, int wx, int wy) { return ((M >> wx) & 1) | (((M >> wy) & 1) << 1); }

static void build_T(void) {
  memset(T, INF, sizeof T);
  for (int in = 0; in < 16; in++) for (int m = 0; m < 4; m++) {
    int a = in & 1, b = (in >> 1) & 1, c = (in >> 2) & 1, d = (in >> 3) & 1;
    int x = m & 1, y = (m >> 1) & 1;
    for (int ch = 0; ch < 256; ch++) {
      int cost = 0, ok = 1, v[8], n;
#define OP(k, expr) do { n = (expr); int cn = (ch >> (k)) & 1; \
        if (n <= 1) { if (cn) ok = 0; v[k] = n; } \
        else { v[k] = cn ? 0 : 1; cost += cn; } } while (0)
      OP(0, a + b + x);          /* a1 = a + b + x        */
      OP(1, d + v[0]);           /* d1 = (d ^ a1) >>> 16  */
      OP(2, c + v[1]);           /* c1 = c + d1           */
      OP(3, b + v[2]);           /* b1 = (b ^ c1) >>> 12  */
      OP(4, v[0] + v[3] + y);    /* a2 = a1 + b1 + y      */
      OP(5, v[1] + v[4]);        /* d2 = (d1 ^ a2) >>> 8  */
      OP(6, v[2] + v[5]);        /* c2 = c1 + d2          */
      OP(7, v[3] + v[6]);        /* b2 = (b1 ^ c2) >>> 7  */
      if (!ok) continue;
      int out = v[4] | (v[7] << 1) | (v[6] << 2) | (v[5] << 3);
      if (cost < T[in][m][out]) T[in][m][out] = (u8)cost;
    }
  }
  for (int w = 0; w < 2; w++) for (int m = 0; m < 4; m++)
    for (int i = 0; i < 16; i++) for (int o = 0; o < 16; o++) {
      u8 t = T[i][m][o];
      u8 tw = (t >= INF) ? INF : (u8)(w ? t : 0);
      TF[w][m][i][o] = tw;
      TB[w][m][o][i] = tw;
    }
}

static int pi4(int o) { return ((o & 3) << 2) | ((o >> 2) & 3); }

/* RELAX (env, bitmask over digest words 0..3): those words may differ (block-1 near-collision whose CV
 * difference a later block absorbs in row a).  Half A pairs: first.a~second.c = h0, first.c~second.a = h2;
 * half B pairs: first.a~second.c = h1, first.c~second.a = h3.  b/d pairs (h5,h7 / h6,h4) are never relaxed. */
static u8 HA[16][16][4][4], HB[16][16][4][4];
static void build_H1(u8 (*Hx)[16][4][4], int relax_ac, int relax_ca) {
  for (int i0 = 0; i0 < 16; i0++) for (int i2 = 0; i2 < 16; i2++)
    for (int m0 = 0; m0 < 4; m0++) for (int m2 = 0; m2 < 4; m2++) {
      int best = INF;
      for (int o = 0; o < 16; o++) for (int o2 = 0; o2 < 16; o2++) {
        int want = pi4(o), mask = 0xF;
        if (relax_ac) mask &= ~0x4;   /* second.c (bit 2) paired with first.a (bit 0) */
        if (relax_ca) mask &= ~0x1;   /* second.a (bit 0) paired with first.c (bit 2) */
        if ((o2 & mask) != (want & mask)) continue;
        int t0 = T[i0][m0][o], t2 = T[i2][m2][o2];
        if (t0 >= INF || t2 >= INF) continue;
        int act = o & 0xA;                       /* b, d pairs always paired */
        if (!relax_ac) act |= o & 0x1;
        if (!relax_ca) act |= o & 0x4;
        int c = t0 + t2 + __builtin_popcount((unsigned)act);
        if (c < best) best = c;
      }
      Hx[i0][i2][m0][m2] = (u8)best;
    }
}
static void build_H(void) {
  const char *e = getenv("RELAX"); int R = e ? atoi(e) : 0;
  fprintf(stderr, "RELAX mask %d (words%s%s%s%s may differ)\n", R, R&1?" h0":"", R&2?" h1":"", R&4?" h2":"", R&8?" h3":"");
  build_H1(HA, R & 1, (R >> 2) & 1);
  build_H1(HB, (R >> 1) & 1, (R >> 3) & 1);
}

static void build_layouts(void) {
  for (int st = 0; st < 2; st++) {
    const int (*W)[4] = st ? DIAW : COLW;
    for (int s = 0; s < N; s++) {
      int idx = 0;
      for (int g = 0; g < 4; g++) for (int k = 0; k < 4; k++)
        if ((s >> W[g][k]) & 1) idx |= 1 << (4 * g + k);
      GRP[st][s] = (u16)idx;
    }
  }
  for (int s = 0; s < N; s++) {
    P_sc_gd[swp(GRP[0][s])] = GRP[1][s];
    P_sd_sc[swp(GRP[1][s])] = swp(GRP[0][s]);
    P_gd_gc[GRP[1][s]] = GRP[0][s];
  }
}

static void contract(const u8 *restrict src, u8 *restrict dst, int p, u8 (*Tm)[16]) {
  const int lo = 1 << (4 * p), hi = 1 << (4 * (3 - p));
  for (int h = 0; h < hi; h++) {
    const u8 *S = src + (size_t)h * lo * 16;
    u8 *D = dst + (size_t)h * lo * 16;
    for (int o = 0; o < 16; o++) {
      u8 *restrict Do = D + (size_t)o * lo;
      memset(Do, INF, (size_t)lo);
      for (int i = 0; i < 16; i++) {
        const u8 t = Tm[i][o];
        if (t >= INF) continue;
        const u8 *restrict Si = S + (size_t)i * lo;
        for (int r = 0; r < lo; r++) { u8 v = (u8)(Si[r] + t); Do[r] = v < Do[r] ? v : Do[r]; }
      }
    }
  }
}

static u8 sb1[N], sb2[N], sb3[N];
/* in: grouped layout (call g nibble at bits 4g..4g+3); out: swapped grouped layout */
static void step(const u8 *in, u8 *out, u8 (*t0)[16], u8 (*t1)[16],
                 u8 (*t2)[16], u8 (*t3)[16]) {
  contract(in, sb1, 3, t3);
  contract(sb1, sb2, 2, t2);
  for (int i = 0; i < N; i++) sb3[swp((u16)i)] = sb2[i];
  contract(sb3, sb1, 3, t1);
  contract(sb1, out, 2, t0);
}

static u8 res[N][NREC];
static u8 KC[2][256][N];
static u8 B3[3][N], B3c[3][N], B2[6][N], F2[2][N], F2c[2][N];
static u8 start[N], tmp[N];

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: trunc_search init eLo eHi out.bin [Tdump]\n"); return 1; }
  int init = atoi(argv[1]), eLo = atoi(argv[2]), eHi = atoi(argv[3]);
  const char *outp = argv[4];
  build_T(); build_H(); build_layouts();
  if (argc >= 6) {   /* dump the G table for cross-checking */
    FILE *f = fopen(argv[5], "wb"); fwrite(T, 1, sizeof T, f); fclose(f);
  }
  memset(res, INF, sizeof res);
  memset(start, INF, N);
  u16 s0 = init >= 0 ? (u16)(1u << init) : 0;
  start[GRP[0][s0]] = 0;
  for (int w = 0; w < 2; w++) for (int mk = 0; mk < 256; mk++) {
    step(start, tmp, TF[w][msgact(mk, 0, 1)], TF[w][msgact(mk, 2, 3)],
         TF[w][msgact(mk, 4, 5)], TF[w][msgact(mk, 6, 7)]);
    for (int i = 0; i < N; i++) KC[w][mk][P_sc_gd[i]] = tmp[i];
  }
  static const int EW[8] = {1, 11, 12, 5, 9, 14, 15, 8};   /* PERM[8..15] */
  static const int CW[8] = {2, 6, 3, 10, 7, 0, 4, 13};     /* PERM[0..7]  */
  clock_t c0 = clock();
  for (int e = eLo; e < eHi; e++) {
    int ME = 0;
    for (int k = 0; k < 8; k++) if ((e >> k) & 1) ME |= 1 << EW[k];
    int me0 = msgact(ME, PERM[8], PERM[9]), me1 = msgact(ME, PERM[10], PERM[11]);
    int me2 = msgact(ME, PERM[12], PERM[13]), me3 = msgact(ME, PERM[14], PERM[15]);
    for (int idx = 0; idx < N; idx++) {
      int n0 = idx & 15, n1 = (idx >> 4) & 15, n2 = (idx >> 8) & 15, n3 = (idx >> 12) & 15;
      int ha = HA[n0][n2][me0][me2], hb = HB[n1][n3][me1][me3];
      int full = ha + hb; if (full > INF) full = INF;
      B3[0][idx] = (u8)full; B3[1][idx] = (u8)ha; B3[2][idx] = (u8)hb;
    }
    for (int v = 0; v < 3; v++) for (int idx = 0; idx < N; idx++) B3c[v][P_gd_gc[idx]] = B3[v][idx];
    for (int c = 0; c < 256; c++) {
      int MC = 0;
      for (int k = 0; k < 8; k++) if ((c >> k) & 1) MC |= 1 << CW[k];
      int M = ME | MC;
      if (init < 0 && M == 0) continue;
      int mc0 = msgact(M, PERM[0], PERM[1]), mc1 = msgact(M, PERM[2], PERM[3]);
      int mc2 = msgact(M, PERM[4], PERM[5]), mc3 = msgact(M, PERM[6], PERM[7]);
      for (int v = 0; v < 6; v++) {
        int w = v >= 3, b = v % 3;
        step(B3c[b], B2[v], TB[w][mc0], TB[w][mc1], TB[w][mc2], TB[w][mc3]);
      }
      int md0 = msgact(M, 8, 9), md1 = msgact(M, 10, 11), md2 = msgact(M, 12, 13), md3 = msgact(M, 14, 15);
      for (int w = 0; w < 2; w++) {
        step(KC[w][M & 0xFF], F2[w], TF[w][md0], TF[w][md1], TF[w][md2], TF[w][md3]);
        for (int i = 0; i < N; i++) F2c[w][P_sd_sc[i]] = F2[w][i];
      }
      int r[NREC];
      for (int k = 0; k < NREC; k++) r[k] = INF;
      for (int i = 0; i < N; i++) {
        int f0 = F2c[0][i], f1 = F2c[1][i], s;
        if (f0 < INF) {
          s = f0 + B2[0][i]; if (s < r[0]) r[0] = s;
          s = f0 + B2[3][i]; if (s < r[1]) r[1] = s;
          s = f0 + B2[1][i]; if (s < r[6]) r[6] = s;
          s = f0 + B2[2][i]; if (s < r[7]) r[7] = s;
          s = f0 + B2[4][i]; if (s < r[8]) r[8] = s;
          s = f0 + B2[5][i]; if (s < r[9]) r[9] = s;
        }
        if (f1 < INF) { s = f1 + B2[3][i]; if (s < r[2]) r[2] = s; }
      }
      int s;
      s = F2c[0][0] + B2[0][0]; r[3] = s < INF ? s : INF;
      s = F2c[0][0] + B2[3][0]; r[4] = s < INF ? s : INF;
      s = F2c[1][0] + B2[3][0]; r[5] = s < INF ? s : INF;
      for (int k = 0; k < NREC; k++) res[M][k] = (u8)(r[k] < INF ? r[k] : INF);
    }
    if (((e - eLo) & 15) == 15 || e == eHi - 1)
      fprintf(stderr, "e=%d done, %.1f s\n", e, (double)(clock() - c0) / CLOCKS_PER_SEC);
  }
  FILE *f = fopen(outp, "wb");
  if (!f) { perror("open"); return 1; }
  fwrite(res, 1, sizeof res, f);
  fclose(f);
  return 0;
}
