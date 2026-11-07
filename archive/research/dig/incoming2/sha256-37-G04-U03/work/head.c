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
