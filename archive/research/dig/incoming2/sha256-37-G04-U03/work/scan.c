/* job5.c - close37 job5 (our code; links the traillab library unchanged). See PREREG.md.
   table               rebuild the row-16 table R16 (u, l, E16x) from chi37 (must give 1,052,672 / 1,042,240)
   bucket LOG2N SEED   cell 22: row-16 pass per E_-4 bucket; forward model (Lemma 4.1 map), a0 walks G, F7/F6 by rejection,
                       K = 256 draws of the other six CV words per good (a0, A_-1, A_-2)
   real LOG2N SEED     cell 22 cross-check: real first blocks CV1 = F_37(IV, M0) (feed-forward)
   r17 N NM SEED       cells 37/31: exact fraction over E17x passing row 17 on N uniform R16 entries, and on NM uniform (E16x, l)
   sens W R [W R ...]  cell 23: single-bit-flip sensitivity of base word W into row R (x = M', the cv of chi37), 37 steps */
#define _GNU_SOURCE
#include "../../../../tools/traillab/src/traillab.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <pthread.h>

static TLModel *M; static TLPair P0; static TLCoord C0;
static TLPair L[32]; static int lok[32];
static int fs(int i, u32 w) { return (u32)(ss0(w + M->dl[i]) - ss0(w)) == M->var[i].T; }
static u32 pdep32(u32 src, u32 mask) { u32 r = 0; for (u32 m = mask; m; m &= m - 1) { if (src & 1) r |= m & -m; src >>= 1; } return r; }
static int valid15(const TLCoord *c, TLPair *p) { int cons = tl_build(M, c, p); return cons && tl_rowsok(&M->base, p, 0, 15) && fs(6, c->wx[6]) && fs(7, c->wx[7]); }
static void variantA0(const TLPair *B, const TLCoord *bc, u32 delta, TLCoord *out) {
  u32 A[18], E[18];
  for (int i = -4; i <= 13; i++) { A[i + 4] = TA(&B->x, i); E[i + 4] = TE(&B->x, i); }
  A[4] += delta;
  for (int i = 4; i <= 13; i++) E[i + 4] = A[i + 4] + A[i] - BS0(A[i + 3]) - MAJ(A[i + 3], A[i + 2], A[i + 1]);
  *out = *bc;
  for (int i = 8; i <= 13; i++) out->wx[i] = E[i + 4] - A[i] - E[i] - BS1(E[i + 3]) - CH(E[i + 3], E[i + 2], E[i + 1]) - TL_K[i];
}
/* ---------------- G (A0 family) on P0, as a1r1617.c */
typedef struct { u32 fm, fv, e0; u32 *out; long n; pthread_mutex_t mu; } GCtx;
static void w_g(void *v, long i, int tid) {
  GCtx *s = v; u32 enew = (s->fv & s->fm) | pdep32((u32)i, ~s->fm), delta = enew - s->e0;
  u32 w8 = P0.x.w[8] - delta; if (!tl_word_cellok(M, KW, 8, w8, w8 + M->dl[8])) return;
  TLCoord c; TLPair p; variantA0(&P0, &C0, delta, &c); if (!valid15(&c, &p)) return;
  pthread_mutex_lock(&s->mu); s->out[s->n++] = c.wx[8]; pthread_mutex_unlock(&s->mu);
}
static int cmpu(const void *a, const void *b) { u32 x = *(const u32 *)a, y = *(const u32 *)b; return x < y ? -1 : x > y; }
static u32 *G; static long nG;
static void enum_G(void) {
  const TLCell *c = &M->full.c[KE][4]; GCtx s; s.fm = c->m; s.fv = c->v; s.e0 = TE(&P0.x, 4); s.out = malloc(sizeof(u32) * (1u << 25)); s.n = 0;
  pthread_mutex_init(&s.mu, NULL); tl_parfor(1l << (32 - __builtin_popcount(c->m)), 1 << 14, w_g, &s);
  qsort(s.out, s.n, 4, cmpu); G = s.out; nG = s.n;
}
/* ---------------- R16 table */
typedef struct { u32 u, e16; int l; } Ent;
static Ent *T16; static long nT; static u32 *idx;   /* idx[u>>8] .. idx[(u>>8)+1] */
typedef struct { pthread_mutex_t mu; long cap; } TCtx;
static void w_tab(void *v, long i, int tid) {
  TCtx *s = v; int l = (int)(i >> 6); long blk = i & 63; if (!lok[l]) return;
  u32 fm = M->base.c[KE][16].m, fv = M->base.c[KE][16].v & fm, fr = ~fm; u64 nf = 1ull << __builtin_popcount(fr), lo = nf * blk / 64, hi = nf * (blk + 1) / 64;
  TLPair q = L[l]; Ent *loc = NULL; long n = 0, cap = 0;
  for (u64 id = lo; id < hi; id++) {
    u32 e = fv | pdep32((u32)id, fr); tl_edrive_row(M, &q, 16, e);
    if (!tl_rowok(&M->base, &q, 16)) continue;
    if (n == cap) { cap = cap ? 2 * cap : 4096; loc = realloc(loc, cap * sizeof(Ent)); }
    loc[n].u = q.x.w[16] - ss1(q.x.w[14]) - q.x.w[9]; loc[n].e16 = e; loc[n].l = l; n++;
  }
  pthread_mutex_lock(&s->mu); if (nT + n > s->cap) { s->cap = (nT + n) * 2; T16 = realloc(T16, s->cap * sizeof(Ent)); } memcpy(T16 + nT, loc, n * sizeof(Ent)); nT += n; pthread_mutex_unlock(&s->mu); free(loc);
}
static int cmpe(const void *a, const void *b) { const Ent *x = a, *y = b; if (x->u != y->u) return x->u < y->u ? -1 : 1; if (x->l != y->l) return x->l - y->l; return x->e16 < y->e16 ? -1 : x->e16 > y->e16; }
static void build_table(void) {
  for (int l = 0; l < 32; l++) { TLCoord c = C0; c.wx[15] = M->var[15].vals[l]; int cons = tl_build(M, &c, &L[l]); lok[l] = cons && tl_rowsok(&M->base, &L[l], M->lorow, 15); }
  TCtx s; pthread_mutex_init(&s.mu, NULL); s.cap = 0; nT = 0; T16 = NULL; double t0 = time(NULL);
  tl_parfor(32 * 64, 1, w_tab, &s); qsort(T16, nT, sizeof(Ent), cmpe);
  idx = malloc(((1ul << 24) + 1) * 4); long j = 0;
  for (u64 h = 0; h <= (1ull << 24); h++) { while (j < nT && (T16[j].u >> 8) < h) j++; idx[h] = (u32)j; }
  long d = nT ? 1 : 0; int per[32] = {0}, ne = 0, nl = 0; for (long i = 0; i < nT; i++) { per[T16[i].l]++; if (i) d += T16[i].u != T16[i - 1].u; }
  for (int l = 0; l < 32; l++) { ne += per[l] > 0; nl += lok[l]; }
  printf("TABLE R16: %ld (u,l) pairs, %ld distinct u, %d of 32 l nonempty, prefix ok for %d l (%.0f s)\n", nT, d, ne, nl, time(NULL) - t0);
  printf("TABLE per-l |R16_l|:"); for (int l = 0; l < 32; l++) printf(" %d", per[l]); printf("\n");
}
static inline u32 lookup(u32 u) { u32 m = 0; for (u32 k = idx[u >> 8]; k < idx[(u >> 8) + 1]; k++) if (T16[k].u == u) m |= 1u << T16[k].l; return m; }

/* ---------------- forward model state */
static u32 SA[18], SE[18], W8C, C4;
static void init_fwd(void) { for (int i = -4; i <= 13; i++) { SA[i + 4] = TA(&P0.x, i); SE[i + 4] = TE(&P0.x, i); } W8C = P0.x.w[8] + TE(&P0.x, 4); C4 = TE(&P0.x, 4) - TA(&P0.x, 0); }
/* words W0..W7 from A[0..3] = A_-4..A_-1, E[0..3] = E_-4..E_-1, a0 ; returns E/A arrays filled */
static void words_from_cv(u32 *A, u32 *E, u32 a0, u32 *W) {
  A[4] = a0; for (int i = 0; i <= 7; i++) E[i + 4] = A[i + 4] + A[i] - BS0(A[i + 3]) - MAJ(A[i + 3], A[i + 2], A[i + 1]);
  for (int i = 0; i <= 7; i++) W[i] = E[i + 4] - A[i] - E[i] - BS1(E[i + 3]) - CH(E[i + 3], E[i + 2], E[i + 1]) - TL_K[i];
}
/* independent recheck: forward both members from CV with the words, rows 0..16, per l */
static u32 fwd_check(const u32 cv[8], const u32 *W8, u32 w8) {
  u32 mask = 0;
  for (int l = 0; l < 32; l++) {
    TLPair q; memset(&q, 0, sizeof q); u32 wx[16]; for (int i = 0; i < 8; i++) wx[i] = W8[i]; wx[8] = w8; for (int i = 9; i < 16; i++) wx[i] = L[l].x.w[i];
    for (int i = 0; i < 4; i++) { TA(&q.x, -1 - i) = TA(&q.y, -1 - i) = cv[i]; TE(&q.x, -1 - i) = TE(&q.y, -1 - i) = cv[4 + i]; }
    for (int i = 0; i < 16; i++) { q.x.w[i] = wx[i]; q.y.w[i] = wx[i] + M->dl[i]; }
    for (int i = 16; i <= 16; i++) { q.x.w[i] = ss1(q.x.w[i - 2]) + q.x.w[i - 7] + ss0(q.x.w[i - 15]) + q.x.w[i - 16]; q.y.w[i] = ss1(q.y.w[i - 2]) + q.y.w[i - 7] + ss0(q.y.w[i - 15]) + q.y.w[i - 16]; }
    for (int i = 0; i <= 16; i++) { tl_step(&q.x, i); tl_step(&q.y, i); }
    if (TA(&q.x, 13) != TA(&L[l].x, 13) || TE(&q.x, 13) != TE(&L[l].x, 13)) return 0xffffffffu; /* S not reproduced */
    if (tl_rowsok(&M->base, &q, 0, 16)) mask |= 1u << l;
  }
  return mask;
}
/* ===== scan.c additions (our code, G04-U03): E_-1..E_-3 of the ordinary collision ===== */
#define NB 256
#define NW 4   /* index 0..3 = E_-4, E_-3, E_-2, E_-1 */
static int FIXK = -1; static u32 FIXC = 0;   /* replace test: E[FIXK] := FIXC */
typedef struct { u64 good, pass, suml, tot, nT[NW][NB], pT[NW][NB], nL[NW][NB], pL[NW][NB], aT[NW][NB]; } BAcc;
typedef struct { u64 seed; long nper; int K; BAcc *acc; int nt; int real; } BCtx;
static const u32 IV[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static void tally(BAcc *a, const u32 *E, int p) { for (int k = 0; k < NW; k++) { a->nT[k][E[k] >> 24]++; a->pT[k][E[k] >> 24] += p; a->nL[k][E[k] & 255]++; a->pL[k][E[k] & 255] += p; } }
static void w_bucket(void *v, long ti, int tid) {
  BCtx *s = v; BAcc *a = &s->acc[ti]; TLRng r = tl_rng(s->seed, 505, (u64)ti, 3);
  u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E);
  u64 g = tl_below(&r, (u64)nG);
  while ((long)a->good < s->nper) {
    u32 w8 = G[g++ % (u64)nG], e4 = W8C - w8, a0 = e4 - C4;
    if (s->real) {
      u32 m0[16], cv[8]; for (int i = 0; i < 16; i++) m0[i] = tl_r32(&r); tl_compress_ref(IV, m0, 37, cv); a->tot++;
      for (int i = 0; i < 4; i++) { A[3 - i] = cv[i]; E[3 - i] = cv[4 + i]; }
      for (int k = 0; k < NW; k++) a->aT[k][E[k] >> 24]++;
      words_from_cv(A, E, a0, W); if (E[8] != e4) { printf("E4 mismatch\n"); exit(4); }
      if (!fs(7, W[7]) || !fs(6, W[6])) continue;
      a->good++;
      u32 u = W[0] + ss0(W[1]), m = lookup(u); int p = m != 0;
      a->pass += p; a->suml += __builtin_popcount(m); tally(a, E, p);
      continue;
    }
    A[3] = tl_r32(&r); for (int i = 0; i < 3; i++) A[i] = tl_r32(&r); for (int i = 0; i < 4; i++) E[i] = tl_r32(&r);
    words_from_cv(A, E, a0, W); if (!fs(7, W[7])) continue;
    int ok6 = 0; for (int t = 0; t < 4096 && !ok6; t++) { A[2] = tl_r32(&r); words_from_cv(A, E, a0, W); ok6 = fs(6, W[6]); }
    if (!ok6) continue;
    u32 w6 = W[6], w7 = W[7];
    for (int k = 0; k < s->K; k++) {
      A[1] = tl_r32(&r); A[0] = tl_r32(&r); for (int i = 0; i < 4; i++) E[i] = tl_r32(&r);
      if (FIXK >= 0) E[FIXK] = FIXC;
      words_from_cv(A, E, a0, W);
      if (k < 2 && (W[6] != w6 || W[7] != w7)) { printf("W6/W7 depend on the redrawn words!\n"); exit(5); }
      a->good++;
      u32 u = W[0] + ss0(W[1]), m = lookup(u); int p = m != 0;
      a->pass += p; a->suml += __builtin_popcount(m); tally(a, E, p);
    }
  }
}
static double chi2p(double x, int k) { double z = (cbrt(x / k) - (1 - 2.0 / (9 * k))) / sqrt(2.0 / (9 * k)); return 0.5 * erfc(z / sqrt(2)); }
static const char *WN[NW] = {"E_-4", "E_-3", "E_-2", "E_-1"};
/* pass-rate homogeneity over 256 buckets */
static void report_pass(const char *nm, u64 *n, u64 *p, double ph) {
  double chi = 0, mx = 0, mn = 1e9; int imx = 0, imn = 0;
  for (int b = 0; b < NB; b++) { double e = n[b] * ph; if (e > 0) chi += (p[b] - e) * (p[b] - e) / (e * (1 - ph)); double rt = n[b] ? (double)p[b] / n[b] / ph : 1; if (rt > mx) { mx = rt; imx = b; } if (rt < mn) { mn = rt; imn = b; } }
  double lo, hi, lo2, hi2; tl_wilson(p[imx], n[imx], &lo, &hi); tl_wilson(p[imn], n[imn], &lo2, &hi2);
  printf("PASSHOM %s: chi2 %.1f on %d dof, p = %.4g | max bucket %02x ratio %.4f [%.4f, %.4f] (%llu/%llu) | min bucket %02x ratio %.4f [%.4f, %.4f]\n", nm, chi, NB - 1, chi2p(chi, NB - 1),
    imx, mx, lo / ph, hi / ph, (unsigned long long)p[imx], (unsigned long long)n[imx], imn, mn, lo2 / ph, hi2 / ph);
}
/* uniformity of a count vector over 256 buckets; also entropy deficit in bits */
static void report_unif(const char *nm, u64 *n) {
  double tot = 0; for (int b = 0; b < NB; b++) tot += n[b]; double e = tot / NB, chi = 0, H = 0;
  for (int b = 0; b < NB; b++) { chi += (n[b] - e) * (n[b] - e) / e; if (n[b]) H -= n[b] / tot * log2(n[b] / tot); }
  printf("UNIF %s: n %.0f chi2 %.1f on %d dof p = %.4g | byte entropy %.5f of 8 bits (deficit %.2e; sampling floor ~%.2e)\n", nm, tot, chi, NB - 1, chi2p(chi, NB - 1), H, 8 - H, (NB - 1) / (2 * tot * log(2)));
}
static void sum_acc(BCtx *s, BAcc *T) { memset(T, 0, sizeof *T); for (int t = 0; t < s->nt; t++) { BAcc *a = &s->acc[t]; T->good += a->good; T->pass += a->pass; T->suml += a->suml; T->tot += a->tot;
  for (int k = 0; k < NW; k++) for (int b = 0; b < NB; b++) { T->nT[k][b] += a->nT[k][b]; T->pT[k][b] += a->pT[k][b]; T->nL[k][b] += a->nL[k][b]; T->pL[k][b] += a->pL[k][b]; T->aT[k][b] += a->aT[k][b]; } } }
static void cmd_bucket(int lg, u64 seed, int real, int th) {
  enum_G(); init_fwd(); printf("G = %ld A0 variants\n", nG);
  { u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); words_from_cv(A, E, TA(&P0.x, 0), W); int bad = 0; for (int i = 0; i < 8; i++) bad += W[i] != P0.x.w[i];
    printf("Lemma 4.1 map on the published CV: W0..W7 %s the published words\n", bad ? "DIFFER FROM" : "equal"); if (bad) exit(6); }
  BCtx s; memset(&s, 0, sizeof s); s.seed = seed; s.K = 256; s.nt = 96; s.real = real; s.acc = calloc(s.nt, sizeof(BAcc));
  if (real) s.nper = (long)(ldexp(1.0, lg) * pow(2, -9.8796) / s.nt); else s.nper = (long)((1ull << lg) / s.nt);
  double t0 = time(NULL);
  if (FIXK >= 0) printf("REPLACE TEST: %s := %08x for every draw\n", WN[FIXK], FIXC);
  tl_parfor(s.nt, 1, w_bucket, &s);
  BAcc *T = calloc(1, sizeof(BAcc)); sum_acc(&s, T);
  double ph = (double)T->pass / T->good, lo, hi; tl_wilson(T->pass, T->good, &lo, &hi);
  if (real) { double gl, gh; tl_wilson(T->good, T->tot, &gl, &gh); printf("REAL first blocks %llu, good %llu = 2^%.4f [2^%.4f, 2^%.4f] (exact p7*p6 2^-9.8796)\n", (unsigned long long)T->tot, (unsigned long long)T->good, log2((double)T->good / T->tot), log2(gl), log2(gh)); }
  printf("RESULT %s seed %llu fix=%d/%08x: good pairs %llu | row16 any-l %llu = 2^%.4f [2^%.4f, 2^%.4f] (table 2^%.4f) | (pair,l) %llu = 2^%.4f per (pair,l) (exact 2^%.4f) | %.0f s\n",
    real ? "real" : "bucket", (unsigned long long)seed, FIXK, FIXC, (unsigned long long)T->good, (unsigned long long)T->pass, log2(ph), log2(lo), log2(hi), log2(1042240.0 / 4294967296.0),
    (unsigned long long)T->suml, log2((double)T->suml / T->good / 32), log2((double)nT / 32 / 4294967296.0), time(NULL) - t0);
  for (int k = 0; k < NW; k++) { if (k == FIXK) continue; char nm[64];
    snprintf(nm, 64, "%s>>24", WN[k]); report_pass(nm, T->nT[k], T->pT[k], ph); snprintf(nm, 64, "%s&0xff", WN[k]); report_pass(nm, T->nL[k], T->pL[k], ph);
    snprintf(nm, 64, "good-pair %s>>24", WN[k]); report_unif(nm, T->nT[k]); snprintf(nm, 64, "good-pair %s&0xff", WN[k]); report_unif(nm, T->nL[k]);
    if (real) { snprintf(nm, 64, "all-block %s>>24", WN[k]); report_unif(nm, T->aT[k]); } }
}
/* ---------------- w17: W-space importance sampler for rows 16 and 17 */
typedef struct { u64 seed; long ndraw; int K; int nt; u64 *acc; u32 *restx; u32 *recs; long nrec; pthread_mutex_t mu; u32 fv, fm; } WCtx;
/* acc per thread: [0]=draws [1]=cheap-pass [2]=final-pass [3..] = top-byte counts [NW][NB], low-byte counts [NW][NB] */
#define WACC (3 + 2 * NW * NB)
static u32 fwd_check17(const u32 cv[8], const u32 *W8, u32 w8, int l) {
  TLPair q; memset(&q, 0, sizeof q); u32 wx[16]; for (int i = 0; i < 8; i++) wx[i] = W8[i]; wx[8] = w8; for (int i = 9; i < 16; i++) wx[i] = L[l].x.w[i];
  for (int i = 0; i < 4; i++) { TA(&q.x, -1 - i) = TA(&q.y, -1 - i) = cv[i]; TE(&q.x, -1 - i) = TE(&q.y, -1 - i) = cv[4 + i]; }
  for (int i = 0; i < 16; i++) { q.x.w[i] = wx[i]; q.y.w[i] = wx[i] + M->dl[i]; }
  for (int i = 16; i <= 17; i++) { q.x.w[i] = ss1(q.x.w[i - 2]) + q.x.w[i - 7] + ss0(q.x.w[i - 15]) + q.x.w[i - 16]; q.y.w[i] = ss1(q.y.w[i - 2]) + q.y.w[i - 7] + ss0(q.y.w[i - 15]) + q.y.w[i - 16]; }
  for (int i = 0; i <= 17; i++) { tl_step(&q.x, i); tl_step(&q.y, i); }
  if (TA(&q.x, 13) != TA(&L[l].x, 13) || TE(&q.x, 13) != TE(&L[l].x, 13)) return 2;
  return tl_rowsok(&M->base, &q, 0, 17) ? 1 : 0;
}
static void w_w17(void *v, long ti, int tid) {
  WCtx *s = v; u64 *a = s->acc + (long)ti * WACC; TLRng r = tl_rng(s->seed, 1717, (u64)ti, 5);
  u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E);
  u64 g = tl_below(&r, (u64)nG);
  while ((long)a[0] < s->ndraw) {
    u32 w8 = G[g++ % (u64)nG], e4 = W8C - w8, a0 = e4 - C4;
    A[3] = tl_r32(&r); for (int i = 0; i < 3; i++) A[i] = tl_r32(&r); for (int i = 0; i < 4; i++) E[i] = tl_r32(&r);
    words_from_cv(A, E, a0, W); if (!fs(7, W[7])) continue;
    int ok6 = 0; for (int t = 0; t < 4096 && !ok6; t++) { A[2] = tl_r32(&r); words_from_cv(A, E, a0, W); ok6 = fs(6, W[6]); }
    if (!ok6) continue;
    for (int k = 0; k < s->K; k++) {
      A[1] = tl_r32(&r); A[0] = tl_r32(&r); for (int i = 1; i < 4; i++) E[i] = tl_r32(&r); E[0] = 0;
      if (FIXK >= 1) E[FIXK] = FIXC;
      words_from_cv(A, E, a0, W);
      long ent = (long)tl_below(&r, (u64)nT); int l = T16[ent].l; a[0]++;
      u32 w17 = ss1(L[l].x.w[15]) + L[l].x.w[10] + ss0(W[2]) + W[1];
      if ((((w17 + s->restx[ent]) ^ s->fv) & s->fm) != 0) continue;
      a[1]++;
      u32 w0 = T16[ent].u - ss0(W[1]); u32 x0 = W[0];       /* W[0] computed with E_-4 = 0, so W0 = x0 - E_-4 */
      E[0] = x0 - w0; u32 W2[8]; words_from_cv(A, E, a0, W2); if (W2[0] != w0 || W2[1] != W[1]) { printf("W0 inversion mismatch\n"); exit(8); }
      u32 cv[8]; for (int i = 0; i < 4; i++) { cv[i] = A[3 - i]; cv[4 + i] = E[3 - i]; }
      int ok = fwd_check17(cv, W2, w8, l); if (ok == 2) { printf("S not reproduced\n"); exit(9); }
      if (!ok) continue;
      a[2]++;
      for (int k2 = 0; k2 < NW; k2++) { a[3 + k2 * NB + (E[k2] >> 24)]++; a[3 + NW * NB + k2 * NB + (E[k2] & 255)]++; }
      pthread_mutex_lock(&s->mu); if (s->nrec < 4096) { u32 *rp = s->recs + s->nrec * 12; for (int i = 0; i < 8; i++) rp[i] = cv[i]; rp[8] = w8; rp[9] = l; rp[10] = (u32)ent; rp[11] = 0; s->nrec++; } pthread_mutex_unlock(&s->mu);
    }
  }
}
static void cmd_w17(int lg, u64 seed, int th) {
  enum_G(); init_fwd(); printf("G = %ld A0 variants\n", nG);
  WCtx s; memset(&s, 0, sizeof s); s.seed = seed; s.K = 256; s.nt = 48; s.ndraw = (long)((1ull << lg) / s.nt);
  s.acc = calloc((size_t)s.nt * WACC, 8); pthread_mutex_init(&s.mu, NULL); s.recs = calloc(4096 * 12, 4);
  s.restx = malloc(nT * 4);
  const TLCell *ce = &M->base.c[KE][17]; s.fm = ce->m; s.fv = ce->v & ce->m;
  for (long i = 0; i < nT; i++) { int l = T16[i].l; s.restx[i] = TA(&L[l].x, 13) + TE(&L[l].x, 13) + BS1(T16[i].e16) + CH(T16[i].e16, TE(&L[l].x, 15), TE(&L[l].x, 14)) + TL_K[17]; }
  { TLRng rr = tl_rng(seed, 99, 0, 0); int bad = 0; for (int t = 0; t < 64; t++) { long e = (long)tl_below(&rr, (u64)nT); int l = T16[e].l; TLPair q = L[l]; tl_edrive_row(M, &q, 16, T16[e].e16);
      u32 w17 = tl_r32(&rr); q.x.w[17] = w17; q.y.w[17] = w17; tl_step(&q.x, 17); bad += TE(&q.x, 17) != (w17 + s.restx[e]); } printf("restx identity: %d of 64 mismatches\n", bad); if (bad) exit(10); }
  double t0 = time(NULL); printf("W17 SAMPLER: 2^%d draws (entry, partial CV), fixed-bit mask of E17 has %d bits\n", lg, __builtin_popcount(s.fm));
  if (FIXK >= 1) printf("REPLACE TEST: %s := %08x\n", WN[FIXK], FIXC);
  tl_parfor(s.nt, 1, w_w17, &s);
  u64 *T = calloc(WACC, 8); for (int t = 0; t < s.nt; t++) for (int i = 0; i < WACC; i++) T[i] += s.acc[(long)t * WACC + i];
  double d = T[0], c = T[1], f = T[2], lo, hi; tl_wilson(f, d, &lo, &hi);
  printf("RESULT w17 seed %llu fix=%d/%08x: draws %.0f, cheap-filter pass %.0f (2^%.3f), forward-verified row16&row17 %.0f = P(row17 | row16) 2^%.4f [2^%.4f, 2^%.4f] (SMC stage 2^-13.000) | %.0f s\n",
    (unsigned long long)seed, FIXK, FIXC, d, c, log2(c / d), f, log2(f / d), log2(lo), log2(hi), time(NULL) - t0);
  for (int k = 0; k < NW; k++) { if (k == FIXK) continue; char nm[64]; snprintf(nm, 64, "row16&17 %s>>24", WN[k]); report_unif(nm, T + 3 + k * NB); snprintf(nm, 64, "row16&17 %s&0xff", WN[k]); report_unif(nm, T + 3 + NW * NB + k * NB); }
  int okc = 0, badc = 0; for (long i = 0; i < s.nrec && i < 512; i++) { u32 *rp = s.recs + i * 12; u32 cv[8]; for (int j = 0; j < 8; j++) cv[j] = rp[j];
    u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); for (int j = 0; j < 4; j++) { A[3 - j] = cv[j]; E[3 - j] = cv[4 + j]; } u32 a0 = (W8C - rp[8]) - C4; words_from_cv(A, E, a0, W);
    int r2 = fwd_check17(cv, W, rp[8], (int)rp[9]); if (r2 == 1) okc++; else badc++; }
  printf("RECHECK %d recorded passes re-verified from CV1 by forward stepping rows 0..17 (both members): %d ok, %d fail\n", okc + badc, okc, badc);
}
/* ---------------- dep: dependency map of the CV words */
static void cmd_dep(void) {
  enum_G(); init_fwd(); TLRng r = tl_rng(4242, 1, 2, 3); const char *cn[8] = {"A_-4", "A_-3", "A_-2", "A_-1", "E_-4", "E_-3", "E_-2", "E_-1"};
  long chg[8][8]; memset(chg, 0, sizeof chg); long NTR = 200000;
  for (long t = 0; t < NTR; t++) {
    u32 A[18], E[18], W[8], W2[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); u32 a0 = (W8C - G[tl_below(&r, nG)]) - C4;
    for (int i = 0; i < 4; i++) { A[i] = tl_r32(&r); E[i] = tl_r32(&r); }
    words_from_cv(A, E, a0, W);
    for (int c = 0; c < 8; c++) { u32 A2[18], E2[18]; memcpy(A2, A, sizeof A); memcpy(E2, E, sizeof E); u32 d = tl_r32(&r) | 1; if (c < 4) A2[c] += d; else E2[c - 4] += d; words_from_cv(A2, E2, a0, W2);
      for (int i = 0; i < 8; i++) chg[c][i] += W[i] != W2[i]; }
  }
  printf("DEP: fraction of %ld random (CV, +delta on one word) trials in which W_i changes\n word  ", NTR); for (int i = 0; i < 8; i++) printf("  W%d   ", i); printf("\n");
  for (int c = 0; c < 8; c++) { printf(" %-5s ", cn[c]); for (int i = 0; i < 8; i++) printf(" %.4f", (double)chg[c][i] / NTR); printf("\n"); }
  int bij = 0; for (int t = 0; t < 1000; t++) { u32 A[18], E[18], W[8], W2[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); u32 a0 = TA(&P0.x, 0);
    for (int i = 0; i < 4; i++) { A[i] = tl_r32(&r); E[i] = tl_r32(&r); } words_from_cv(A, E, a0, W); u32 d = tl_r32(&r) | 1;
    for (int k = 1; k <= 3; k++) { u32 E2[18]; memcpy(E2, E, sizeof E); E2[k] += d; words_from_cv(A, E2, a0, W2); bij += (W2[k] - W[k]) != (u32)(-d); } }
  printf("DEP own-word check (E[k] += delta moves W_k by exactly -delta, k=1..3 = E_-3,E_-2,E_-1 -> W1,W2,W3): %d violations of 3000\n", bij);
}
int main(int argc, char **argv) {
  const char *chi = "../../../../tools/traillab/chi/chi37.txt"; int th = 2;
  for (int i = 1; i < argc - 1; i++) if (!strcmp(argv[i], "--threads")) th = atoi(argv[i + 1]);
  for (int i = 1; i < argc - 2; i++) if (!strcmp(argv[i], "--fix")) { FIXK = atoi(argv[i + 1]); FIXC = (u32)strtoul(argv[i + 2], NULL, 16); }
  setvbuf(stdout, NULL, _IOLBF, 0); tl_set_threads(th); if (tl_sha256_selftest()) { printf("selftest FAIL\n"); return 9; }
  M = calloc(1, sizeof(TLModel)); if (tl_load(chi, M, NULL, 0)) return 2;
  P0 = M->pub; C0 = M->pubc;
  { TLPair q; int cons = tl_build(M, &C0, &q); if (!cons || memcmp(&q.x.w, &P0.x.w, 64)) { printf("P0 rebuild mismatch\n"); return 3; } }
  const char *cmd = argc > 1 ? argv[1] : "";
  if (!strcmp(cmd, "dep")) { cmd_dep(); return 0; }
  build_table();
  if (!strcmp(cmd, "table")) return 0;
  if (!strcmp(cmd, "bucket")) cmd_bucket(atoi(argv[2]), strtoull(argv[3], NULL, 10), 0, th);
  else if (!strcmp(cmd, "real")) cmd_bucket(atoi(argv[2]), strtoull(argv[3], NULL, 10), 1, th);
  else if (!strcmp(cmd, "w17")) cmd_w17(atoi(argv[2]), strtoull(argv[3], NULL, 10), th);
  else { printf("usage: table | dep | bucket LOG2N SEED | real LOG2N SEED | w17 LOG2DRAWS SEED  [--fix IDX HEXVAL] (IDX 1=E_-3 2=E_-2 3=E_-1)\n"); return 2; }
  return 0;
}
