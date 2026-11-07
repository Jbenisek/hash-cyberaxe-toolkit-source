/* Block-neutrality harness core (C99; also compiles under nvcc with -DHD="__host__ __device__").
 * apply(config, frame, mask): XOR a block of bits into one coordinate frame, re-derive the 14 real inputs of the
 * chunk compression, recompute BOTH blocks' complete 2-round state with the organizer formulas (blake3.py _compress,
 * rounds = 2: G, PERMUTATION, state layout copied verbatim), and report damage / steering against the base config.
 * Frames:  D = split_e3 design (Y4,Y9,w8 | D2.b1,D3.a1,K0.b1,K3.d1,S14,S15 | g=C0.b1 | Y14)        11 words
 *          O = outer basis (C0.d1,D2.a1,D2.b1,S11,S4,X9,w6,Y4 | T1 | c1=E1.c1)                       10 words
 *          R = real inputs (w0,w1,w2,w3,w5,w6,w7,w8,w9,w10,w11,w12 | T0 | T1)                         14 words
 * See HARNESS.md for the field list. */
#pragma once
#include <stdint.h>
#include "derive_gen.h"

enum { FR_D = 0, FR_O = 1, FR_R = 2 };
static const int NCOORD[3] = { 11, 10, 14 };
static const uint32_t IVW[8] = { 0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au,
                                 0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u };
static const uint8_t PERM[16] = { 2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8 };

/* ---- observables (61 words, same order as common.OBS_FIELDS) ---- */
enum { O_R = 0, O_Y3 = 14, O_Y4, O_Y9, O_Y14, O_W8, O_Y3B, O_Y11, O_Y11B, O_DY7, O_DY15,
       O_X3, O_X7, O_X11, O_X15, O_R0DIFF, O_T0, O_T1, O_CLS, O_ETA, O_DD = 33,
       O_Y1 = 41, O_Y6, O_Y11E, O_Y12, O_W12, O_W5, O_K, O_C1, O_K1 = 49, O_K3 = 53, O_RES = 57, NOBS = 61 };
/* ---- damage bits (same order as common.DAMAGE_BITS) ---- */
enum { D_Y3, D_Y4, D_Y9, D_Y14, D_W8, D_Y3B, D_X3, D_X7, D_X11, D_X15, D_Y11, D_Y11B, D_DY7, D_DY15,
       D_T1RANGE, D_CLASS, D_ETA, D_DIG0257, D_K3, D_R0EQ, ND };
enum { I_T1, I_T0, I_CTR0, I_SAME };   /* I_SAME: the 14 real inputs did not change (a null block) */

typedef struct { uint32_t S[16], X[16], Y[16], Z[16], dig[8]; } trace_t;
typedef struct { int id; char pool; uint32_t D[11], O[10], R[14]; uint32_t base[NOBS]; } config_t;
typedef struct { uint32_t damage, info, chk; uint32_t now[NOBS]; } result_t;

/* organizer _g, verbatim */
#define GQ(v, a, b, c, d, x, y) do { \
  v[a] = v[a] + v[b] + (x); v[d] = ROR(v[d] ^ v[a], 16); v[c] = v[c] + v[d]; v[b] = ROR(v[b] ^ v[c], 12); \
  v[a] = v[a] + v[b] + (y); v[d] = ROR(v[d] ^ v[a], 8);  v[c] = v[c] + v[d]; v[b] = ROR(v[b] ^ v[c], 7); } while (0)

HD static inline void compress_trace(const uint32_t m0[16], uint32_t t0, uint32_t t1, uint32_t len, uint32_t flags, trace_t *tr) {
  uint32_t v[16], m[16], t[16];
  for (int i = 0; i < 8; i++) v[i] = IVW[i];
  for (int i = 0; i < 4; i++) v[8 + i] = IVW[i];
  v[12] = t0; v[13] = t1; v[14] = len; v[15] = flags;
  for (int i = 0; i < 16; i++) m[i] = m0[i];
  for (int r = 0; r < 2; r++) {
    GQ(v, 0, 4, 8, 12, m[0], m[1]); GQ(v, 1, 5, 9, 13, m[2], m[3]); GQ(v, 2, 6, 10, 14, m[4], m[5]); GQ(v, 3, 7, 11, 15, m[6], m[7]);
    for (int i = 0; i < 16; i++) (r ? tr->Y : tr->S)[i] = v[i];
    GQ(v, 0, 5, 10, 15, m[8], m[9]); GQ(v, 1, 6, 11, 12, m[10], m[11]); GQ(v, 2, 7, 8, 13, m[12], m[13]); GQ(v, 3, 4, 9, 14, m[14], m[15]);
    for (int i = 0; i < 16; i++) (r ? tr->Z : tr->X)[i] = v[i];
    for (int i = 0; i < 16; i++) t[i] = m[PERM[i]];
    for (int i = 0; i < 16; i++) m[i] = t[i];
  }
  for (int i = 0; i < 8; i++) tr->dig[i] = v[i] ^ v[i + 8];
}

/* the starred (trial) lines of halfsearch.ctr_trial for E1.c1 = c1 */
HD static inline void trial_c1(uint32_t *v, uint32_t c1) {
  v[W_E1_c1] = c1; v[W_E1_d1] = c1 - Y11C; v[W_E1_a1] = ROL(v[W_E1_d1], 16) ^ v[W_Y12];
  v[W_Y6] = v[W_E1_a1] - v[W_Y1] - v[W_w12]; v[W_Y10] = ROL(v[W_Y6], 7) ^ v[W_C2_b1]; v[W_Y14] = v[W_Y10] - v[W_C2_c1];
  v[W_Y2] = ROL(v[W_Y14], 8) ^ v[W_C2_d1]; v[W_w0] = v[W_Y2] - v[W_C2_a1] - v[W_C2_b1];
  v[W_K0_a1] = IV0 + IV4 + v[W_w0]; v[W_T0] = ROL(v[W_K0_d1], 16) ^ v[W_K0_a1]; v[W_w1] = v[W_S0] - v[W_K0_a1] - v[W_K0_b1];
}
#define OPS_TRIAL 17
/* split_e3 ev.c1_from_y14: the E1.c1 that makes the trial reproduce Y14 */
HD static inline uint32_t c1_from_y14(const uint32_t *v, uint32_t y14) {
  uint32_t y10 = y14 + v[W_C2_c1], y6 = ROR(y10 ^ v[W_C2_b1], 7), a1 = y6 + v[W_Y1] + v[W_w12];
  return ROR(v[W_Y12] ^ a1, 16) + Y11C;
}
#define OPS_C1Y14 8

/* coordinates of a frame -> 14 real inputs; v (NW words) receives every derived word (frames D, O). Returns the
   frame-D check residual (0 when the 21-equation loop's check Y9 = C1.c1 + Y13 holds), 0 for frames O, R. */
HD static inline uint32_t derive(int frame, const uint32_t *c, uint32_t r[14], uint32_t *v) {
  uint32_t chk = 0;
  if (frame == FR_R) { for (int i = 0; i < 14; i++) r[i] = c[i]; return 0; }
  if (frame == FR_D) { chk = derive_D_outer(c, v); trial_c1(v, c1_from_y14(v, c[10])); }
  else { derive_O_outer(c, v); trial_c1(v, c[9]); }
  r[0] = v[W_w0]; r[1] = v[W_w1]; r[2] = v[W_w2]; r[3] = v[W_w3]; r[4] = v[W_w5]; r[5] = v[W_w6]; r[6] = v[W_w7];
  r[7] = v[W_w8]; r[8] = v[W_w9]; r[9] = v[W_w10]; r[10] = v[W_w11]; r[11] = v[W_w12]; r[12] = v[W_T0]; r[13] = v[W_T1];
  return chk;
}

HD static inline void messages(const uint32_t r[14], uint32_t wa[16], uint32_t wb[16]) {
  wa[0] = r[0]; wa[1] = r[1]; wa[2] = r[2]; wa[3] = r[3]; wa[4] = W4C; wa[5] = r[4]; wa[6] = r[5]; wa[7] = r[6];
  wa[8] = r[7]; wa[9] = r[8]; wa[10] = r[9]; wa[11] = r[10]; wa[12] = r[11]; wa[13] = W13C; wa[14] = 0; wa[15] = 0;
  for (int i = 0; i < 16; i++) wb[i] = wa[i];
  wb[4] = W4BC; wb[5] = wa[5] + DELTA5C;
}

/* full observables from the organizer compression of both blocks */
HD static inline void evaluate(const uint32_t r[14], uint32_t *o) {
  uint32_t wa[16], wb[16]; trace_t A, B;
  messages(r, wa, wb);
  compress_trace(wa, r[12], r[13], LEN_A_C, FLAGS_C, &A);
  compress_trace(wb, r[12], r[13], LEN_B_C, FLAGS_C, &B);
  const uint32_t *ya = A.Y, *yb = B.Y, *za = A.Z, *zb = B.Z;
  uint32_t e3a = ya[3] + ya[4] + wa[15], e3b = yb[3] + yb[4] + wb[15], r0 = 0;
  for (int i = 0; i < 14; i++) o[O_R + i] = r[i];
  o[O_Y3] = ya[3]; o[O_Y4] = ya[4]; o[O_Y9] = ya[9]; o[O_Y14] = ya[14]; o[O_W8] = wa[8]; o[O_Y3B] = yb[3];
  o[O_Y11] = ya[11]; o[O_Y11B] = yb[11]; o[O_DY7] = ya[7] ^ yb[7]; o[O_DY15] = ya[15] ^ yb[15];
  o[O_X3] = A.X[3]; o[O_X7] = A.X[7]; o[O_X11] = A.X[11]; o[O_X15] = A.X[15];
  for (int i = 0; i < 16; i++) r0 |= A.X[i] ^ B.X[i];
  o[O_R0DIFF] = r0; o[O_T0] = r[12]; o[O_T1] = r[13];
  o[O_CLS] = (e3a & CLASS_MASK_C) == CLASS_VALUE_C; o[O_ETA] = ROR(e3a ^ e3b, 16) == ETA_C;
  for (int i = 0; i < 8; i++) o[O_DD + i] = A.dig[i] ^ B.dig[i];
  o[O_Y1] = ya[1]; o[O_Y6] = ya[6]; o[O_Y11E] = ya[11]; o[O_Y12] = ya[12]; o[O_W12] = wa[12]; o[O_W5] = wa[5];
  o[O_K] = ya[1] + wa[12]; o[O_C1] = ya[11] + ROR(ya[12] ^ (ya[1] + ya[6] + wa[12]), 16);
  o[O_K1 + 0] = za[1] ^ zb[1]; o[O_K1 + 1] = za[11] ^ zb[11]; o[O_K1 + 2] = za[12] ^ zb[12]; o[O_K1 + 3] = za[6] ^ zb[6];
  o[O_K3 + 0] = za[9] ^ zb[9]; o[O_K3 + 1] = za[3] ^ zb[3]; o[O_K3 + 2] = za[4] ^ zb[4]; o[O_K3 + 3] = za[14] ^ zb[14];
  o[O_RES + 0] = o[O_DD + 1]; o[O_RES + 1] = o[O_DD + 3]; o[O_RES + 2] = o[O_DD + 4]; o[O_RES + 3] = o[O_DD + 6];
}
#define OPS_EVALUATE (2 * 16 * 14)

HD static inline int t1_ok(uint32_t t1) { return t1 >= 1u && t1 < (1u << 19); }

HD static inline void damage_of(const uint32_t *b, const uint32_t *n, uint32_t *dmg, uint32_t *info) {
  uint32_t d = 0;
  d |= (uint32_t)(n[O_Y3] != b[O_Y3]) << D_Y3;   d |= (uint32_t)(n[O_Y4] != b[O_Y4]) << D_Y4;
  d |= (uint32_t)(n[O_Y9] != b[O_Y9]) << D_Y9;   d |= (uint32_t)(n[O_Y14] != b[O_Y14]) << D_Y14;
  d |= (uint32_t)(n[O_W8] != b[O_W8]) << D_W8;   d |= (uint32_t)(n[O_Y3B] != b[O_Y3B]) << D_Y3B;
  d |= (uint32_t)(n[O_X3] != b[O_X3]) << D_X3;   d |= (uint32_t)(n[O_X7] != b[O_X7]) << D_X7;
  d |= (uint32_t)(n[O_X11] != b[O_X11]) << D_X11; d |= (uint32_t)(n[O_X15] != b[O_X15]) << D_X15;
  d |= (uint32_t)(n[O_Y11] != b[O_Y11]) << D_Y11; d |= (uint32_t)(n[O_Y11B] != b[O_Y11B]) << D_Y11B;
  d |= (uint32_t)(n[O_DY7] != 0) << D_DY7;        d |= (uint32_t)(n[O_DY15] != 0) << D_DY15;
  d |= (uint32_t)(t1_ok(b[O_T1]) && !t1_ok(n[O_T1])) << D_T1RANGE;
  d |= (uint32_t)(n[O_CLS] != 1) << D_CLASS;      d |= (uint32_t)(n[O_ETA] != 1) << D_ETA;
  d |= (uint32_t)((n[O_DD + 0] | n[O_DD + 2] | n[O_DD + 5] | n[O_DD + 7]) != 0) << D_DIG0257;
  d |= (uint32_t)((n[O_K3] ^ b[O_K3]) | (n[O_K3 + 1] ^ b[O_K3 + 1]) | (n[O_K3 + 2] ^ b[O_K3 + 2]) | (n[O_K3 + 3] ^ b[O_K3 + 3])) != 0 ? 1u << D_K3 : 0;
  d |= (uint32_t)(n[O_R0DIFF] != 0) << D_R0EQ;
  *dmg = d;
  uint32_t moved = 0;
  for (int i = 0; i < 14; i++) moved |= n[O_R + i] ^ b[O_R + i];
  *info = (uint32_t)(n[O_T1] != b[O_T1]) << I_T1 | (uint32_t)(n[O_T0] != b[O_T0]) << I_T0 |
          (uint32_t)(n[O_T0] == 0 && n[O_T1] == 0) << I_CTR0 | (uint32_t)(moved == 0) << I_SAME;
}

HD static inline const uint32_t *coords_of(const config_t *cf, int frame) {
  return frame == FR_D ? cf->D : frame == FR_O ? cf->O : cf->R;
}

/* THE apply(): full recomputation through the organizer compression */
HD static inline void apply(const config_t *cf, int frame, const uint32_t *mask, result_t *res) {
  uint32_t c[14], r[14], v[NW];
  const uint32_t *src = coords_of(cf, frame);
  for (int i = 0; i < NCOORD[frame]; i++) c[i] = src[i] ^ mask[i];
  res->chk = derive(frame, c, r, v);
  evaluate(r, res->now);
  damage_of(cf->base, res->now, &res->damage, &res->info);
}

/* E1 key (Δa2, Δc2, Δd2, Δb2) of E1 = G(Y1,Y6,Y11,Y12; w12,w5) for blocks A (Y11, w5) and B (Y11B, w5+DELTA5) */
HD static inline void e1key(uint32_t y1, uint32_t y6, uint32_t y12, uint32_t w12, uint32_t w5, uint32_t k[4]) {
  uint32_t a1 = y1 + y6 + w12, d1 = ROR(y12 ^ a1, 16);
  uint32_t cA = Y11C + d1, bA = ROR(y6 ^ cA, 12), aA = a1 + bA + w5, dA = ROR(d1 ^ aA, 8), c2A = cA + dA, b2A = ROR(bA ^ c2A, 7);
  uint32_t cB = Y11BC + d1, bB = ROR(y6 ^ cB, 12), aB = a1 + bB + w5 + DELTA5C, dB = ROR(d1 ^ aB, 8), c2B = cB + dB, b2B = ROR(bB ^ c2B, 7);
  k[0] = aA ^ aB; k[1] = c2A ^ c2B; k[2] = dA ^ dB; k[3] = b2A ^ b2B;
}
#define OPS_E1KEY 29   /* shared a1,d1: 4; block A: 10; block B: 11 (w5+DELTA5); 4 XORs */

/* FAST path for search loops (validated against apply() in validate.py): returns the damage bits it can see without
   the full compression — Y4, Y9, Y14, w8, the four pins (frame R only; frames D/O keep them by construction), T1RANGE —
   plus T1 and the E1 key. Frames D/O read the derived words; in frame D the real Y9 is C1.c1 + Y13 (the check). */
HD static inline uint32_t apply_fast(const config_t *cf, int frame, const uint32_t *mask, uint32_t *t1, uint32_t k[4]) {
  uint32_t c[14], d = 0;
  const uint32_t *src = coords_of(cf, frame), *b = cf->base;
  for (int i = 0; i < NCOORD[frame]; i++) c[i] = src[i] ^ mask[i];
  if (frame == FR_R) {
    uint32_t v[16], wa[16], wb[16];
    messages(c, wa, wb);
    for (int i = 0; i < 8; i++) v[i] = IVW[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IVW[i];
    v[12] = c[12]; v[13] = c[13]; v[14] = LEN_A_C; v[15] = FLAGS_C;
    GQ(v, 0, 4, 8, 12, wa[0], wa[1]); GQ(v, 1, 5, 9, 13, wa[2], wa[3]); GQ(v, 2, 6, 10, 14, wa[4], wa[5]); GQ(v, 3, 7, 11, 15, wa[6], wa[7]);
    GQ(v, 0, 5, 10, 15, wa[8], wa[9]); GQ(v, 1, 6, 11, 12, wa[10], wa[11]); GQ(v, 2, 7, 8, 13, wa[12], wa[13]); GQ(v, 3, 4, 9, 14, wa[14], wa[15]);
    d |= (uint32_t)(v[3] != b[O_X3]) << D_X3; d |= (uint32_t)(v[7] != b[O_X7]) << D_X7;
    d |= (uint32_t)(v[11] != b[O_X11]) << D_X11; d |= (uint32_t)(v[15] != b[O_X15]) << D_X15;
    /* round-2 columns 0..2 (message schedule after one PERMUTATION: s = w2,w6,w3,w10,w7,w0 ...) */
    GQ(v, 0, 4, 8, 12, wa[2], wa[6]); GQ(v, 1, 5, 9, 13, wa[3], wa[10]); GQ(v, 2, 6, 10, 14, wa[7], wa[0]);
    d |= (uint32_t)(v[4] != b[O_Y4]) << D_Y4; d |= (uint32_t)(v[9] != b[O_Y9]) << D_Y9; d |= (uint32_t)(v[14] != b[O_Y14]) << D_Y14;
    d |= (uint32_t)(wa[8] != b[O_W8]) << D_W8;
    *t1 = c[13];
    e1key(v[1], v[6], v[12], wa[12], wa[5], k);
  } else {
    uint32_t v[NW], y9;
    if (frame == FR_D) { derive_D_outer(c, v); trial_c1(v, c1_from_y14(v, c[10])); y9 = v[W_C1_c1] + v[W_Y13]; }
    else { derive_O_outer(c, v); trial_c1(v, c[9]); y9 = v[W_Y9]; }
    d |= (uint32_t)(v[W_Y4] != b[O_Y4]) << D_Y4; d |= (uint32_t)(y9 != b[O_Y9]) << D_Y9;
    d |= (uint32_t)(v[W_Y14] != b[O_Y14]) << D_Y14; d |= (uint32_t)(v[W_w8] != b[O_W8]) << D_W8;
    *t1 = v[W_T1];
    e1key(v[W_Y1], v[W_Y6], v[W_Y12], v[W_w12], v[W_w5], k);
  }
  d |= (uint32_t)(t1_ok(b[O_T1]) && !t1_ok(*t1)) << D_T1RANGE;
  return d;
}
#define FAST_MASK ((1u << D_Y4) | (1u << D_Y9) | (1u << D_Y14) | (1u << D_W8) | (1u << D_X3) | (1u << D_X7) | (1u << D_X11) | (1u << D_X15) | (1u << D_T1RANGE))

HD static inline void base_obs(config_t *cf) { evaluate(cf->R, cf->base); }
