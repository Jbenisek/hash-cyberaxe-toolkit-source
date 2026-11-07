/* scan38.c - G04-U03 for sha256-38: CV words E_-3, E_-2, E_-1 of the ordinary collision (our code; links traillab unchanged).
   Model (R38M proof sections 4-6): CV1 = F_38(IV,M0); a0 in G (2^26, W8 cell + 3 two-bit conds); W7x = c7(a0)-A_-1 in F7 (no F6 gate: W6 free);
   W9..W15 = published S; row 16: E16x = C16 + W0 + s0(W1) in the 32-word set; rows 17.. follow.
   val | dep | exact K NCTX SEED | steer LOG2 SEED [--fix IDX HEX] | real LOG2BLK SEED      (IDX 1=E_-3 2=E_-2 3=E_-1) */
#define _GNU_SOURCE
#include "../../../../tools/traillab/src/traillab.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <pthread.h>
static TLModel *M; static TLPair P0;
static u32 SA[18], SE[18], W8C, C4, C16, RB, RMASK;
static int FIXK = -1; static u32 FIXC = 0;
static const u32 IV[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static u32 pdep32(u32 src, u32 mask) { u32 r = 0; for (u32 m = mask; m; m &= m - 1) { if (src & 1) r |= m & -m; src >>= 1; } return r; }
static inline int f7(u32 w) { return (u32)(ss0(w + 0x20000000u) - ss0(w)) == 0x03bff800u; }
static inline int in16(u32 e) { return ((e - RB) & ~RMASK) == 0; }
static void words_from_cv(u32 *A, u32 *E, u32 a0, u32 *W) {
  A[4] = a0; for (int i = 0; i <= 7; i++) E[i + 4] = A[i + 4] + A[i] - BS0(A[i + 3]) - MAJ(A[i + 3], A[i + 2], A[i + 1]);
  for (int i = 0; i <= 7; i++) W[i] = E[i + 4] - A[i] - E[i] - BS1(E[i + 3]) - CH(E[i + 3], E[i + 2], E[i + 1]) - TL_K[i];
}
/* W0,W1 only (exact scan) */
static inline void w01(const u32 *A, const u32 *E, u32 a0, u32 *w0, u32 *w1) {
  u32 E0 = a0 + A[0] - BS0(A[3]) - MAJ(A[3], A[2], A[1]);
  u32 E1 = SA[5] + A[1] - BS0(a0) - MAJ(a0, A[3], A[2]);
  *w0 = E0 - A[0] - E[0] - BS1(E[3]) - CH(E[3], E[2], E[1]) - TL_K[0];
  *w1 = E1 - A[1] - E[1] - BS1(E0) - CH(E0, E[3], E[2]) - TL_K[1];
}
static void init_fwd(void) {
  for (int i = -4; i <= 13; i++) { SA[i + 4] = TA(&P0.x, i); SE[i + 4] = TE(&P0.x, i); }
  W8C = P0.x.w[8] + TE(&P0.x, 4); C4 = TE(&P0.x, 4) - TA(&P0.x, 0);
  C16 = TE(&P0.x, 16) - P0.x.w[0] - ss0(P0.x.w[1]); RB = M->elist[16][0]; RMASK = 0;
  for (int i = 0; i < M->nelist[16]; i++) RMASK |= M->elist[16][i] - RB;
}
static u32 draw_w8(TLRng *r) {
  const TLCell *c = &M->full.c[KW][8];
  for (;;) { u32 w = (c->v & c->m) | (tl_r32(r) & ~c->m); if (tl_word_cellok(M, KW, 8, w, w + M->dl[8])) return w; }
}
/* forward both members from CV with W0..W7,w8; published W9..W15; returns last ok row 15..21, -1 if S not reproduced, -2 if rows 0..15 fail */
static int fwd_depth(const u32 cv[8], const u32 *W, u32 w8) {
  TLPair q; memset(&q, 0, sizeof q); u32 wx[16];
  for (int i = 0; i < 8; i++) wx[i] = W[i]; wx[8] = w8; for (int i = 9; i < 16; i++) wx[i] = P0.x.w[i];
  for (int i = 0; i < 4; i++) { TA(&q.x, -1 - i) = TA(&q.y, -1 - i) = cv[i]; TE(&q.x, -1 - i) = TE(&q.y, -1 - i) = cv[4 + i]; }
  for (int i = 0; i < 16; i++) { q.x.w[i] = wx[i]; q.y.w[i] = wx[i] + M->dl[i]; }
  for (int i = 16; i <= 21; i++) { q.x.w[i] = ss1(q.x.w[i - 2]) + q.x.w[i - 7] + ss0(q.x.w[i - 15]) + q.x.w[i - 16]; q.y.w[i] = ss1(q.y.w[i - 2]) + q.y.w[i - 7] + ss0(q.y.w[i - 15]) + q.y.w[i - 16]; }
  for (int i = 0; i <= 21; i++) { tl_step(&q.x, i); tl_step(&q.y, i); }
  if (TA(&q.x, 13) != TA(&P0.x, 13) || TE(&q.x, 13) != TE(&P0.x, 13)) return -1;
  if (!tl_rowsok(&M->base, &q, 0, 15)) return -2;
  int d = 15; for (int r = 16; r <= 21; r++) { if (!tl_rowok(&M->base, &q, r)) break; d = r; }
  return d;
}
/* ---- stats */
#define NB 256
#define NW 4
static const char *WN[NW] = {"E_-4", "E_-3", "E_-2", "E_-1"};
static double chi2p(double x, int k) { double z = (cbrt(x / k) - (1 - 2.0 / (9 * k))) / sqrt(2.0 / (9 * k)); return 0.5 * erfc(z / sqrt(2)); }
static void report_unif(const char *nm, u64 *n) {
  double tot = 0; for (int b = 0; b < NB; b++) tot += n[b]; double e = tot / NB, chi = 0, H = 0;
  for (int b = 0; b < NB; b++) { chi += (n[b] - e) * (n[b] - e) / e; if (n[b]) H -= n[b] / tot * log2(n[b] / tot); }
  printf("UNIF %s: n %.0f chi2 %.1f on %d dof p = %.4g | byte entropy %.5f of 8 bits (deficit %.2e; sampling floor ~%.2e)\n", nm, tot, chi, NB - 1, chi2p(chi, NB - 1), H, 8 - H, (NB - 1) / (2 * tot * log(2)));
}
/* ---- val */
typedef struct { u64 g, f7; pthread_mutex_t mu; } VC;
static void w_val(void *v, long i, int tid) {
  VC *s = v; const TLCell *c = &M->full.c[KW][8]; u64 g = 0; int fb = __builtin_popcount(~c->m);
  u64 lo = (u64)i * 65536, tot = 1ull << fb;
  for (u64 k = 0; k < 65536; k++) { u64 id = lo + k; if (id >= tot) break;
    u32 w = (c->v & c->m) | pdep32((u32)id, ~c->m); g += tl_word_cellok(M, KW, 8, w, w + M->dl[8]); }
  pthread_mutex_lock(&s->mu); s->g += g; pthread_mutex_unlock(&s->mu);
}
static void w_f7(void *v, long i, int tid) { VC *s = v; u64 c = 0; u32 lo = (u32)(i << 20); for (u32 k = 0; k < (1u << 20); k++) c += f7(lo + k); pthread_mutex_lock(&s->mu); s->f7 += c; pthread_mutex_unlock(&s->mu); }
static void cmd_val(void) {
  init_fwd();
  u32 d1[8], d2[8]; tl_compress_ref(M->cv, M->mx, 38, d1); tl_compress_ref(M->cv, M->my, 38, d2);
  printf("VAL published pair: digest(x) %s digest(y); equal to printed digest: %s\n", memcmp(d1, d2, 32) ? "!=" : "==", (M->have_digest && !memcmp(d1, M->digest, 32)) ? "yes" : "no");
  { u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); words_from_cv(A, E, TA(&P0.x, 0), W); int bad = 0; for (int i = 0; i < 8; i++) bad += W[i] != P0.x.w[i];
    printf("VAL Lemma 4.1 map on the published CV: W0..W7 %s the published words\n", bad ? "DIFFER FROM" : "equal"); if (bad) exit(6);
    u32 w0, w1; w01(A, E, TA(&P0.x, 0), &w0, &w1); printf("VAL w01 shortcut: %s\n", (w0 == P0.x.w[0] && w1 == P0.x.w[1]) ? "equal" : "DIFFER"); if (w0 != P0.x.w[0] || w1 != P0.x.w[1]) exit(7); }
  printf("VAL C4 %08x W8C %08x C16 %08x (proof: ab1f01f0 a1be17b9 fe314838)  E16 set: %ld words = R16B %08x + subset sums of mask %08x (proof: 481b02f9, 82405)\n", C4, W8C, C16, M->nelist[16], RB, RMASK);
  { u32 cnt = 0; for (u32 sub = RMASK;; sub = (sub - 1) & RMASK) { cnt++; int found = 0; for (int i = 0; i < M->nelist[16]; i++) found |= M->elist[16][i] == RB + sub; if (!found) { printf("VAL elist miss\n"); exit(8); } if (!sub) break; } printf("VAL affine set has %u words, all in elist; elist has %ld\n", cnt, M->nelist[16]); }
  u32 cv[8]; for (int i = 0; i < 4; i++) { cv[i] = TA(&P0.x, -1 - i); cv[4 + i] = TE(&P0.x, -1 - i); } u32 W[8]; for (int i = 0; i < 8; i++) W[i] = P0.x.w[i];
  printf("VAL fwd_depth on the published CV and words: last ok row %d (expect 21)\n", fwd_depth(cv, W, P0.x.w[8]));
  VC s; memset(&s, 0, sizeof s); pthread_mutex_init(&s.mu, NULL); double t0 = time(NULL);
  tl_parfor(1l << 12, 1, w_f7, &s); printf("VAL |F7| = %llu (proof 287,309,824) %.0f s\n", (unsigned long long)s.f7, time(NULL) - t0);
  t0 = time(NULL); int fb = __builtin_popcount(~M->full.c[KW][8].m); long nchunk = fb >= 16 ? (1l << (fb - 16)) : 1;
  tl_parfor(nchunk, 1, w_val, &s); printf("VAL |G| = %llu = 2^%.4f (proof 2^26) from %d free bits of the W8 cell %.0f s\n", (unsigned long long)s.g, log2((double)s.g), fb, time(NULL) - t0);
}
/* ---- dep */
static void cmd_dep(void) {
  init_fwd(); TLRng r = tl_rng(4242, 38, 2, 3); const char *cn[8] = {"A_-4", "A_-3", "A_-2", "A_-1", "E_-4", "E_-3", "E_-2", "E_-1"};
  long chg[8][8]; memset(chg, 0, sizeof chg); long NTR = 200000;
  for (long t = 0; t < NTR; t++) {
    u32 A[18], E[18], W[8], W2[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); u32 a0 = (W8C - draw_w8(&r)) - C4;
    for (int i = 0; i < 4; i++) { A[i] = tl_r32(&r); E[i] = tl_r32(&r); }
    words_from_cv(A, E, a0, W);
    for (int c = 0; c < 8; c++) { u32 A2[18], E2[18]; memcpy(A2, A, sizeof A); memcpy(E2, E, sizeof E); u32 d = tl_r32(&r) | 1; if (c < 4) A2[c] += d; else E2[c - 4] += d; words_from_cv(A2, E2, a0, W2);
      for (int i = 0; i < 8; i++) chg[c][i] += W[i] != W2[i]; }
  }
  printf("DEP: fraction of %ld random (CV, +delta on one word) trials in which W_i changes (a0 in G)\n word  ", NTR); for (int i = 0; i < 8; i++) printf("  W%d   ", i); printf("\n");
  for (int c = 0; c < 8; c++) { printf(" %-5s ", cn[c]); for (int i = 0; i < 8; i++) printf(" %.4f", (double)chg[c][i] / NTR); printf("\n"); }
  int bij = 0; for (int t = 0; t < 1000; t++) { u32 A[18], E[18], W[8], W2[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); u32 a0 = TA(&P0.x, 0);
    for (int i = 0; i < 4; i++) { A[i] = tl_r32(&r); E[i] = tl_r32(&r); } words_from_cv(A, E, a0, W); u32 d = tl_r32(&r) | 1;
    for (int k = 1; k <= 3; k++) { u32 E2[18]; memcpy(E2, E, sizeof E); E2[k] += d; words_from_cv(A, E2, a0, W2); bij += (W2[k] - W[k]) != (u32)(-d); } }
  printf("DEP own-word check (E[k] += delta moves W_k by exactly -delta, k=1..3 = E_-3,E_-2,E_-1 -> W1,W2,W3): %d violations of 3000\n", bij);
}
/* ---- exact: for a fixed context, count the values of one CV word E[k] (all 2^32) for which row 16 passes (E16x in the 32-word set) */
typedef struct { u32 A[4], E[4]; u32 a0; int k; u64 *hit; } XC;
static void w_x(void *v, long ci, int tid) {
  XC *s = v; u32 A[4], E[4]; memcpy(A, s->A, 16); memcpy(E, s->E, 16); u64 h = 0; u32 lo = (u32)(ci << 20);
  for (u32 j = 0; j < (1u << 20); j++) { E[s->k] = lo + j; u32 w0, w1; w01(A, E, s->a0, &w0, &w1); h += in16(C16 + w0 + ss0(w1)); }
  s->hit[ci] = h;
}
static void cmd_exact(int k, int nctx, u64 seed) {
  init_fwd(); TLRng r = tl_rng(seed, 38, k, 11); double sum = 0, sum2 = 0;
  for (int c = 0; c < nctx; c++) {
    XC s; u32 w8 = draw_w8(&r); s.a0 = (W8C - w8) - C4; s.k = k;
    for (;;) { for (int i = 0; i < 4; i++) { s.A[i] = tl_r32(&r); s.E[i] = tl_r32(&r); } u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); for (int i = 0; i < 4; i++) { A[i] = s.A[i]; E[i] = s.E[i]; } words_from_cv(A, E, s.a0, W); if (f7(W[7])) break; }
    s.hit = calloc(4096, 8); double t0 = time(NULL); tl_parfor(4096, 1, w_x, &s); u64 tot = 0; for (int i = 0; i < 4096; i++) tot += s.hit[i]; free(s.hit);
    printf("EXACT %s ctx %d: of 2^32 values of %s, %llu give E16x in the 32-word set (row 16 pass) | %.0f s\n", WN[k], c, WN[k], (unsigned long long)tot, time(NULL) - t0);
    sum += tot; sum2 += (double)tot * tot;
  }
  double mean = sum / nctx, var = nctx > 1 ? (sum2 - nctx * mean * mean) / (nctx - 1) : 0;
  printf("EXACTSUM %s: %d contexts, mean count %.3f, sd %.3f, se %.3f (if each value of %s were uniform for E16x the mean is 32)\n", WN[k], nctx, mean, sqrt(var), sqrt(var / nctx), WN[k]);
}
/* ---- steer: importance sampler, E_-4 solves row 16 for a uniformly chosen element of the 32-word set */
typedef struct { u64 seed; long ndraw; int K; int nt; u64 *acc; u32 fv, fm; u32 restx[64]; } SC;
#define SACC (12 + 2 * NW * NB)   /* [0]draws [1]cheap [2]rows0-17 ok [3]row16 ok ; [4..11]=depth hist 14..21 ; then unif tables */
static void w_steer(void *v, long ti, int tid) {
  SC *s = v; u64 *a = s->acc + (long)ti * SACC; TLRng r = tl_rng(s->seed, 3838, (u64)ti, 5);
  u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E);
  while ((long)a[0] < s->ndraw) {
    u32 w8 = draw_w8(&r), a0 = (W8C - w8) - C4;
    for (int i = 0; i < 4; i++) { A[i] = tl_r32(&r); E[i] = tl_r32(&r); } words_from_cv(A, E, a0, W); if (!f7(W[7])) continue;
    u32 w7 = W[7];
    for (int k = 0; k < s->K; k++) {
      A[2] = tl_r32(&r); A[1] = tl_r32(&r); A[0] = tl_r32(&r); for (int i = 1; i < 4; i++) E[i] = tl_r32(&r); E[0] = 0;
      if (FIXK >= 1) E[FIXK] = FIXC;
      words_from_cv(A, E, a0, W); if (k < 2 && W[7] != w7) { printf("W7 depends on redrawn words!\n"); exit(5); }
      int ent = (int)tl_below(&r, (u64)M->nelist[16]); u32 e16 = M->elist[16][ent]; a[0]++;
      u32 w17 = ss1(P0.x.w[15]) + P0.x.w[10] + ss0(W[2]) + W[1];
      if ((((w17 + s->restx[ent]) ^ s->fv) & s->fm) != 0) continue;
      a[1]++;
      u32 w0 = e16 - C16 - ss0(W[1]); u32 x0 = W[0]; E[0] = x0 - w0; u32 W2[8]; words_from_cv(A, E, a0, W2);
      if (W2[0] != w0 || W2[1] != W[1]) { printf("W0 inversion mismatch\n"); exit(8); }
      u32 cv[8]; for (int i = 0; i < 4; i++) { cv[i] = A[3 - i]; cv[4 + i] = E[3 - i]; }
      int d = fwd_depth(cv, W2, w8); if (d == -1) { printf("S not reproduced\n"); exit(9); }
      if (d < 16) { printf("row16 should pass by construction but depth %d (ent %d)\n", d, ent); exit(10); }
      a[3]++; if (d >= 17) { a[2]++; for (int k2 = 0; k2 < NW; k2++) { a[12 + k2 * NB + (E[k2] >> 24)]++; a[12 + NW * NB + k2 * NB + (E[k2] & 255)]++; } }
      a[4 + (d - 14)]++;
    }
  }
}
static void cmd_steer(int lg, u64 seed) {
  init_fwd(); SC s; memset(&s, 0, sizeof s); s.seed = seed; s.K = 256; s.nt = 48; s.ndraw = (long)((1ull << lg) / s.nt); s.acc = calloc((size_t)s.nt * SACC, 8);
  const TLCell *ce = &M->base.c[KE][17]; s.fm = ce->m; s.fv = ce->v & ce->m;
  for (int i = 0; i < M->nelist[16]; i++) { u32 e = M->elist[16][i]; s.restx[i] = TA(&P0.x, 13) + TE(&P0.x, 13) + BS1(e) + CH(e, TE(&P0.x, 15), TE(&P0.x, 14)) + TL_K[17]; }
  { TLRng rr = tl_rng(seed, 99, 0, 0); int bad = 0; for (int t = 0; t < 64; t++) { int en = (int)tl_below(&rr, M->nelist[16]); TLPair q = P0; tl_edrive_row(M, &q, 16, M->elist[16][en]);
      u32 w17 = tl_r32(&rr); q.x.w[17] = w17; q.y.w[17] = w17; tl_step(&q.x, 17); bad += TE(&q.x, 17) != (w17 + s.restx[en]); } printf("restx identity: %d of 64 mismatches\n", bad); if (bad) exit(11); }
  double t0 = time(NULL); printf("STEER: 2^%d draws, E17 fixed-bit mask has %d bits\n", lg, __builtin_popcount(s.fm));
  if (FIXK >= 1) printf("REPLACE TEST: %s := %08x\n", WN[FIXK], FIXC);
  tl_parfor(s.nt, 1, w_steer, &s);
  u64 *T = calloc(SACC, 8); for (int t = 0; t < s.nt; t++) for (int i = 0; i < SACC; i++) T[i] += s.acc[(long)t * SACC + i];
  double d = T[0], c = T[1], f = T[2], lo, hi; tl_wilson(f, d, &lo, &hi);
  printf("RESULT steer seed %llu fix=%d/%08x: draws %.0f, cheap-filter pass %.0f (2^%.3f), forward-verified rows0..17 %.0f = P(row17 | row16) 2^%.4f [2^%.4f, 2^%.4f] | %.0f s\n",
    (unsigned long long)seed, FIXK, FIXC, d, c, log2(c / d), f, log2(f / d), log2(lo), log2(hi), time(NULL) - t0);
  printf("DEPTH last-ok-row histogram (of %.0f cheap-filter passes): ", (double)T[3]); for (int r = 14; r <= 21; r++) printf("row%d:%llu ", r, (unsigned long long)T[4 + r - 14]); printf("\n");
  for (int k = 0; k < NW; k++) { if (k == FIXK) continue; char nm[64]; snprintf(nm, 64, "row16&17 %s>>24", WN[k]); report_unif(nm, T + 12 + k * NB); snprintf(nm, 64, "row16&17 %s&0xff", WN[k]); report_unif(nm, T + 12 + NW * NB + k * NB); }
}
/* ---- real first blocks: CV1 = F_38(IV,M0); per block, KA random a0 in G tested on the gate and on stage 3a (12 shared low bits of E16x) */
static u32 POOL[1<<16];
typedef struct { u64 seed; long nblk; int KA; int nt; u64 *acc; } RC;
#define RACC (4 + 2 * NW * NB + NW * NB)
static void w_real(void *v, long ti, int tid) {
  RC *s = v; u64 *a = s->acc + (long)ti * RACC; TLRng r = tl_rng(s->seed, 3939, (u64)ti, 6); u32 A[18], E[18], W[8]; u32 m3a = 0x1dbf8u, v3a = RB & 0x1dbf8u;
  for (long b = 0; b < s->nblk; b++) {
    u32 m0[16], cv[8]; for (int i = 0; i < 16; i++) m0[i] = tl_r32(&r); tl_compress_ref(IV, m0, 38, cv); a[0]++;
    memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); for (int i = 0; i < 4; i++) { A[3 - i] = cv[i]; E[3 - i] = cv[4 + i]; }
    for (int k = 0; k < NW; k++) a[4 + 2 * NW * NB + k * NB + (E[k] >> 24)]++;
    for (int j = 0; j < s->KA; j++) {
      u32 a0 = (W8C - POOL[tl_next(&r) >> 48]) - C4; u32 A2[18], E2[18]; memcpy(A2, A, sizeof A); memcpy(E2, E, sizeof E);
      words_from_cv(A2, E2, a0, W); a[1]++; if (!f7(W[7])) continue; a[2]++;
      u32 e16 = C16 + W[0] + ss0(W[1]); if ((e16 & m3a) != v3a) continue; a[3]++;
      for (int k = 0; k < NW; k++) { a[4 + k * NB + (E[k] >> 24)]++; a[4 + NW * NB + k * NB + (E[k] & 255)]++; }
    }
  }
}
static void cmd_real(int lg, u64 seed) {
  init_fwd(); { TLRng pr = tl_rng(seed, 5, 5, 5); for (int i = 0; i < (1<<16); i++) POOL[i] = draw_w8(&pr); } RC s; memset(&s, 0, sizeof s); s.seed = seed; s.KA = 256; s.nt = 48; s.nblk = (long)((1ull << lg) / s.nt); s.acc = calloc((size_t)s.nt * RACC, 8); double t0 = time(NULL);
  tl_parfor(s.nt, 1, w_real, &s); u64 *T = calloc(RACC, 8); for (int t = 0; t < s.nt; t++) for (int i = 0; i < RACC; i++) T[i] += s.acc[(long)t * RACC + i];
  double nb = T[0], ev = T[1], g = T[2], p3 = T[3], lo, hi; tl_wilson(g, ev, &lo, &hi);
  printf("REAL blocks %.0f, (block,a0) evaluations %.0f, gate W7 in F7: %.0f = 2^%.4f [2^%.4f, 2^%.4f] (exact p7 2^-3.90197)\n", nb, ev, g, log2(g / ev), log2(lo), log2(hi));
  tl_wilson(p3, g, &lo, &hi); printf("REAL stage 3a (E16x on the 12 shared bits) given gate: %.0f = 2^%.4f [2^%.4f, 2^%.4f] (exact 2^-12)\n", p3, log2(p3 / g), log2(lo), log2(hi));
  for (int k = 1; k < NW; k++) { char nm[64]; snprintf(nm, 64, "all-block %s>>24", WN[k]); report_unif(nm, T + 4 + 2 * NW * NB + k * NB);
    snprintf(nm, 64, "stage3a-pass %s>>24", WN[k]); report_unif(nm, T + 4 + k * NB); snprintf(nm, 64, "stage3a-pass %s&0xff", WN[k]); report_unif(nm, T + 4 + NW * NB + k * NB); }
  printf("REAL %.0f s\n", time(NULL) - t0);
}
int main(int argc, char **argv) {
  int th = 2; for (int i = 1; i < argc - 1; i++) if (!strcmp(argv[i], "--threads")) th = atoi(argv[i + 1]);
  for (int i = 1; i < argc - 2; i++) if (!strcmp(argv[i], "--fix")) { FIXK = atoi(argv[i + 1]); FIXC = (u32)strtoul(argv[i + 2], NULL, 16); }
  setvbuf(stdout, NULL, _IOLBF, 0); tl_set_threads(th); if (tl_sha256_selftest()) { printf("selftest FAIL\n"); return 9; }
  M = calloc(1, sizeof(TLModel)); if (tl_load("../../../../tools/traillab/chi/chi38.txt", M, NULL, 0)) return 2; P0 = M->pub;
  const char *cmd = argc > 1 ? argv[1] : "";
  if (!strcmp(cmd, "val")) cmd_val(); else if (!strcmp(cmd, "dep")) cmd_dep();
  else if (!strcmp(cmd, "exact")) cmd_exact(atoi(argv[2]), atoi(argv[3]), strtoull(argv[4], NULL, 10));
  else if (!strcmp(cmd, "steer")) cmd_steer(atoi(argv[2]), strtoull(argv[3], NULL, 10));
  else if (!strcmp(cmd, "real")) cmd_real(atoi(argv[2]), strtoull(argv[3], NULL, 10));
  else { printf("usage: val | dep | exact K NCTX SEED | steer LOG2 SEED | real LOG2BLK SEED [--fix IDX HEX]\n"); return 2; }
  return 0;
}
