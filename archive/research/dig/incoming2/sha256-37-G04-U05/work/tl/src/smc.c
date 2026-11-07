/* smc.c - prefix-conditioned samples (sequential Monte Carlo over the attack's free coordinates), window counting,
   exact enumeration. Our code; generalises pre_sha256_1/smc_exact.c and rows22_24/automaton/r2224.c. */
#define _GNU_SOURCE
#include "smc.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <pthread.h>

int tl_autolist = 0;
int tl_w16on = 0; u64 tl_stg[64][TL_NR][2];
/* D174: optional co-failure mask over the 13 row-17 conditions.  Bits 0..8
   are the nine E17 cell bits (MSB-to-list order from chi37), bits 9..11
   are the three E17 two-bit relations, and bit 12 is A15[29]=A17[29]. */
int tl_d174on = 0; u64 tl_d174_mask[1u << 13];
static const int W16R[6][3] = {{1,12,1},{20,27,1},{8,25,0},{14,18,0},{4,6,1},{22,31,1}};
typedef struct { u32 pi; u32 val; u64 key; u32 alive; } Rec;
typedef struct { Rec *r; long n, cap; } RecV;
static void rpush(RecV *v, Rec r) { if (v->n == v->cap) { v->cap = v->cap ? v->cap * 2 : 4096; v->r = realloc(v->r, v->cap * sizeof(Rec)); } v->r[v->n++] = r; }

static u32 forced_mask(const TLConds *const *C, int nc, int t, u32 *val) {
  u32 m = 0xffffffffu, v = 0; int first = 1;
  for (int k = 0; k < nc; k++) {
    const TLCell *c = &C[k]->c[KE][t];
    if (first) { m = c->m; v = c->v; first = 0; }
    else { m &= c->m; m &= ~(v ^ c->v); }
  }
  *val = v & m; return m;
}

/* ---------------- stage workers */
typedef struct {
  const TLModel *M; TLPart *P; int t, a, b; u64 seed, stage; long props; u32 fm, fv;
  const TLConds *const *C; int nc; int carrier; RecV *tv; long *tot; const u32 *list; long nlist;
} StageCtx;

static void w_estage(void *vctx, long i, int tid) {
  StageCtx *s = vctx; TLPart *p = &s->P[i]; TLRng r = tl_rng(s->seed, s->stage, (u64)i, 0x45);
  for (long j = 0; j < s->props; j++) {
    u32 e = s->list ? s->list[tl_below(&r, (u64)s->nlist)] : (tl_r32(&r) & ~s->fm) | s->fv;
    tl_edrive_row(s->M, &p->p, s->t, e);
    u32 al = 0;
    for (int k = 0; k < s->nc; k++) if (((p->alive >> k) & 1) && tl_rowok(s->C[k], &p->p, s->t)) al |= 1u << k;
    if (tl_w16on && s->b > 0) { int wm = 0; for (int q = 0; q < 6; q++) { int bit = ((p->p.x.w[16] >> W16R[q][0]) ^ (p->p.x.w[16] >> W16R[q][1])) & 1; if (bit != W16R[q][2]) wm |= 1 << q; }
      __atomic_fetch_add(&tl_stg[wm][s->t][0], 1, __ATOMIC_RELAXED); if (al) __atomic_fetch_add(&tl_stg[wm][s->t][1], 1, __ATOMIC_RELAXED); }
    if (al || s->carrier == 0) { Rec rc = {(u32)i, e, 0, al}; rpush(&s->tv[tid], rc); }
  }
}
static void late_redraw(const TLModel *M, TLCoord *c, u64 seed, u64 stage, u64 i, u64 j) {
  TLRng r = tl_rng(seed, stage, i, j + 0x1000); tl_draw_vars(M, c, &r, 1);
}
static void w_lstage(void *vctx, long i, int tid) {
  StageCtx *s = vctx; const TLModel *M = s->M; TLPart *p = &s->P[i]; TLPair q;
  for (long j = 0; j < s->props; j++) {
    TLCoord c = p->c; late_redraw(M, &c, s->seed, s->stage, (u64)i, (u64)j);
    tl_build(M, &c, &q);
    if (tl_rowsok(s->C[0], &q, M->lorow, s->a - 1)) { Rec rc = {(u32)i, 0, (u64)j, p->alive}; rpush(&s->tv[tid], rc); }
  }
}
static int cmprec(const void *a, const void *b) {
  const Rec *x = a, *y = b;
  if (x->pi != y->pi) return x->pi < y->pi ? -1 : 1;
  if (x->key != y->key) return x->key < y->key ? -1 : 1;
  return x->val < y->val ? -1 : x->val > y->val;
}
static int resample_fast(const TLModel *M, TLPart **P, TLPart **P2, int np, RecV *tv, int nth, int kind, int t, u64 seed, u64 stage, TLRng *R, long *cnt_out) {
  long cnt = 0; for (int i = 0; i < nth; i++) cnt += tv[i].n; *cnt_out = cnt;
  if (!cnt) return 0;
  Rec *all = malloc(cnt * sizeof(Rec)); long o = 0;
  for (int i = 0; i < nth; i++) { memcpy(all + o, tv[i].r, tv[i].n * sizeof(Rec)); o += tv[i].n; tv[i].n = 0; }
  qsort(all, cnt, sizeof(Rec), cmprec);
  for (int i = 0; i < np; i++) {
    Rec *rc = &all[tl_below(R, (u64)cnt)];
    (*P2)[i] = (*P)[rc->pi];
    if (kind == 0) { tl_edrive_row(M, &(*P2)[i].p, t, rc->val); (*P2)[i].c.ex[t] = rc->val; (*P2)[i].alive = rc->alive; }
    else { late_redraw(M, &(*P2)[i].c, seed, stage, rc->pi, rc->key); tl_build(M, &(*P2)[i].c, &(*P2)[i].p); }
  }
  TLPart *tmp = *P; *P = *P2; *P2 = tmp; free(all); return 1;
}

/* ---------------- init: early + late draws, anchored rows, forward to e0-1 */
typedef struct { const TLModel *M; TLPart *P; u64 seed; int hi; const TLConds *C; long *tries; } InitCtx;
static void w_init(void *vctx, long i, int tid) {
  InitCtx *s = vctx; const TLModel *M = s->M; TLPart *p = &s->P[i]; (void)tid;
  for (long it = 0;; it++) {
    TLRng r = tl_rng(s->seed, 1, (u64)i, (u64)it);
    p->c = M->pubc; tl_draw_vars(M, &p->c, &r, 0); tl_draw_vars(M, &p->c, &r, 1);
    p->alive = 1;
    TLPair *q = &p->p; int K = M->anchor;
    for (int k = 0; k < 16; k++) { q->x.w[k] = p->c.wx[k]; q->y.w[k] = p->c.wx[k] + M->dl[k]; }
    if (K >= 0) {
      for (int j = K - 3; j <= K; j++) { TA(&q->x, j) = TA(&M->pub.x, j); TE(&q->x, j) = TE(&M->pub.x, j); TA(&q->y, j) = TA(&M->pub.y, j); TE(&q->y, j) = TE(&M->pub.y, j); }
      for (int t = K + 1; t < M->e0; t++) {
        if (t >= 16) { q->x.w[t] = tl_wnext(M, &q->x, 0, t); q->y.w[t] = tl_wnext(M, &q->y, 1, t); }
        tl_step(&q->x, t); tl_step(&q->y, t);
      }
    }
    if (tl_rowsok(s->C, q, (K >= 0 ? K + 1 : 0), s->hi)) { __atomic_fetch_add(s->tries, it + 1, __ATOMIC_RELAXED); return; }
    if (it > (1L << 26)) { fprintf(stderr, "init: no particle after 2^26 tries\n"); exit(4); }
  }
}

/* ---------------- prefix: rows < a under C[0] */
TLPart *tl_smc_prefix(const TLModel *M, const TLConds *pre, int a, int np, int m, int mt2, u64 seed, double *log2est, int verbose) {
  if (M->e0 < 0 || M->anchor < 0) { fprintf(stderr, "smc needs anchor and edrive in the model\n"); exit(2); }
  if (a < M->e0) { fprintf(stderr, "window must start at or after the first free row %d\n", M->e0); exit(2); }
  int nth = tl_threads(); TLPart *P = malloc((size_t)np * sizeof(TLPart)), *P2 = malloc((size_t)np * sizeof(TLPart));
  RecV *tv = calloc(nth, sizeof(RecV)); TLRng R = tl_rng(seed, 99, 0, 0);
  long tries = 0; InitCtx ic = {M, P, seed, M->e0 - 1, pre, &tries};
  tl_parfor(np, 16, w_init, &ic);
  double est = (double)np / (double)tries;
  if (verbose) printf("  init: %d particles, acceptance %.6f (rows %d..%d)\n", np, est, M->anchor + 1, M->e0 - 1);
  const TLConds *C1[1] = {pre};
  int top = a - 1 < M->e1 ? a - 1 : M->e1;
  if (tl_autolist && !((TLModel *)M)->elist[M->e0]) {
    /* exact set of E_e0 values that pass the prefix row e0 under 'pre' (row e0 depends only on the anchored rows, not on the particle) */
    int t = M->e0; u32 fv, fm = forced_mask(C1, 1, t, &fv); u64 nfree = 1ull << (32 - __builtin_popcount(fm));
    u32 *lst = malloc(sizeof(u32) * 4096); long nl = 0, cap = 4096; TLPair q = P[0].p;
    for (u64 k = 0; k < nfree; k++) {
      u32 e = fv; { u64 kk = k; for (int b = 0; b < 32; b++) if (!((fm >> b) & 1)) { if (kk & 1) e |= 1u << b; kk >>= 1; } }
      tl_edrive_row(M, &q, t, e);
      if (tl_rowok(pre, &q, t)) { if (nl == cap) { cap *= 2; lst = realloc(lst, cap * 4); } lst[nl++] = e; }
    }
    ((TLModel *)M)->elist[t] = lst; ((TLModel *)M)->nelist[t] = nl;
    if (verbose) printf("  E%d set under the prefix conditions: %ld values (enumerated 2^%d candidates)\n", t, nl, 32 - __builtin_popcount(fm));
  }
  for (int t = M->e0; t <= top; t++) {
    u32 fv, fm = forced_mask(C1, 1, t, &fv);
    StageCtx sc = {M, P, t, a, 0, seed, (u64)t + 10, m, fm, fv, C1, 1, 1, tv, NULL, M->elist[t], M->nelist[t]};
    for (int i = 0; i < np; i++) P[i].alive = 1;
    tl_parfor(np, 4, w_estage, &sc);
    long cnt; if (!resample_fast(M, &P, &P2, np, tv, nth, 0, t, seed, (u64)t + 10, &R, &cnt)) { if (verbose) printf("  stage %d: dead\n", t); *log2est = -INFINITY; free(P2); free(tv); return NULL; }
    est *= (M->elist[t] ? (double)M->nelist[t] / 4294967296.0 : ldexp(1.0, -__builtin_popcount(fm))) * (double)cnt / ((double)np * m);
    if (verbose) { if (M->elist[t]) printf("  stage %2d (E-driven, list of %ld): accepted %ld of %ld, log2 est %.4f\n", t, M->nelist[t], cnt, (long)np * m, log2(est));
      else printf("  stage %2d (E-driven): forced %2d bits, accepted %ld of %ld, log2 est %.4f\n", t, __builtin_popcount(fm), cnt, (long)np * m, log2(est)); }
  }
  if (a - 1 > M->e1) {
    StageCtx sc = {M, P, M->e1 + 1, a, 0, seed, 77, mt2, 0, 0, C1, 1, 1, tv, NULL, NULL, 0};
    tl_parfor(np, 2, w_lstage, &sc);
    long cnt; if (!resample_fast(M, &P, &P2, np, tv, nth, 1, 0, seed, 77, &R, &cnt)) { if (verbose) printf("  late stage: dead\n"); *log2est = -INFINITY; free(P2); free(tv); return NULL; }
    est *= (double)cnt / ((double)np * mt2);
    if (verbose) printf("  stage %d..%d (late words redrawn, full rebuild): accepted %ld of %ld, log2 est %.4f\n", M->e1 + 1, a - 1, cnt, (long)np * mt2, log2(est));
  }
  for (int i = 0; i < nth; i++) free(tv[i].r);
  free(tv); free(P2); *log2est = log2(est); return P;
}


/* ---- W16-relaxation statistics (r38_w16_relax, 2026-10-12): per violation mask of the six W16 relations */
u64 tl_w16_N[64], tl_w16_EX[64], tl_w16_FALSE, tl_w16_EXN, tl_w16_HLOST;
u64 tl_death[64][TL_NR][4];
u64 tl_cne[64][TL_NR];
typedef struct { u64 key, n; } HE;
#define HSZ 16384
static HE *g_hist[64];
static void hist_add(int tid, int mask, int ex, int widx, u32 val) {
  if (!g_hist[tid]) g_hist[tid] = calloc(HSZ, sizeof(HE));
  u64 key = ((((u64)mask * 2 + ex) * 4 + widx) << 32 | val) + 1; u32 h = (u32)(tl_mix(key) & (HSZ - 1));
  for (int k = 0; k < 64; k++, h = (h + 1) & (HSZ - 1)) { if (g_hist[tid][h].key == key) { g_hist[tid][h].n++; return; } if (!g_hist[tid][h].key) { g_hist[tid][h].key = key; g_hist[tid][h].n = 1; return; } }
  __atomic_fetch_add(&tl_w16_HLOST, 1, __ATOMIC_RELAXED);
}
void tl_w16_hist_dump(FILE *f) {
  /* merge */
  HE *m = calloc(1 << 20, sizeof(HE)); long nm = 0;
  for (int t = 0; t < 64; t++) if (g_hist[t]) for (int h = 0; h < HSZ; h++) if (g_hist[t][h].key) {
    u64 key = g_hist[t][h].key; long i; for (i = 0; i < nm; i++) if (m[i].key == key) break;
    if (i == nm) { if (nm >= (1 << 20)) continue; m[nm].key = key; m[nm].n = 0; nm++; } m[i].n += g_hist[t][h].n; }
  for (long i = 0; i < nm; i++) { u64 k = m[i].key - 1; fprintf(f, "HIST mask %02x ex %d w %d val %08x n %llu\n", (unsigned)(k >> 32) / 8, (int)((k >> 32) / 4) & 1, (int)((k >> 32) & 3), (unsigned)(k & 0xffffffffu), (unsigned long long)m[i].n); }
  free(m);
}

u32 *nz_buf; u64 nz_n, nz_max; u64 nz_total, nz_cells, nz_zero;
/* ---------------- window */
typedef struct {
  const TLModel *M; TLPart *P; const TLWinCfg *cfg; int latefree, mtf;
  u64 *pc; /* per particle counters [np][NCNT] */ int ncnt;
} FinCtx;
static void w_final(void *vctx, long i, int tid) {
  FinCtx *s = vctx; const TLModel *M = s->M; const TLWinCfg *g = s->cfg; TLPart *p = &s->P[i];
  u64 *cnt = s->pc + (size_t)i * s->ncnt; int nc = g->nc;
  /* replay check: the incremental rows of this particle equal a full rebuild from its own coordinates */
  { TLPair q; tl_build(M, &p->c, &q); int top = g->a - 1; if (top > M->nr - 1) top = M->nr - 1; int bad = 0;
    for (int t = M->anchor - 3; t <= top; t++) if (TA(&q.x, t) != TA(&p->p.x, t) || TE(&q.x, t) != TE(&p->p.x, t) || TA(&q.y, t) != TA(&p->p.y, t) || TE(&q.y, t) != TE(&p->p.y, t)) bad = 1;
    cnt[CN_REPLAYBAD] += bad; }
  for (int j = 0; j < s->mtf; j++) {
    TLPair q; const TLPair *use = &p->p;
    if (s->latefree) {
      TLCoord c = p->c; late_redraw(M, &c, g->seed, 500, (u64)i, (u64)j);
      int cons = tl_build(M, &c, &q); use = &q;
      if (!cons) cnt[CN_INCONS]++;
      if (!tl_rowsok(g->pre, &q, M->lorow, g->a - 1)) { cnt[CN_BROKEN]++; continue; }
    }
    cnt[CN_N]++;
    { int L=M->nr-1; u32 d8[8]; for(int q=0;q<4;q++){ d8[q]=TA(&use->y,L-q)-TA(&use->x,L-q); d8[4+q]=TE(&use->y,L-q)-TE(&use->x,L-q);} 
      int z=1; for(int q=0;q<8;q++) if(d8[q]) z=0;
      int okc = tl_rowsok(g->C[0], use, g->a, g->b);
      __atomic_fetch_add(&nz_total,1,__ATOMIC_RELAXED); if(okc) __atomic_fetch_add(&nz_cells,1,__ATOMIC_RELAXED); if(z) __atomic_fetch_add(&nz_zero,1,__ATOMIC_RELAXED);
      if(nz_buf){ u64 k=__atomic_fetch_add(&nz_n,1,__ATOMIC_RELAXED); if(k<nz_max){ memcpy(nz_buf+k*9,d8,32); nz_buf[k*9+8]=okc|(z<<1);} } }
    if (tl_d174on) {
      const TLCell *ce = &g->C[0]->c[KE][17];
      u32 ex = TE(&use->x, 17), ey = TE(&use->y, 17);
      const int eb[9] = {30,23,22,18,17,12,9,5,4}; int dm = 0;
      for (int z = 0; z < 9; z++) {
        int b = eb[z]; int good;
        if ((ce->m >> b) & 1) good = ((ex >> b) & 1) == ((ce->v >> b) & 1);
        else if ((ce->dm >> b) & 1) good = (((ex ^ ey) >> b) & 1) == ((ce->d >> b) & 1);
        else good = 1;
        if (!good) dm |= 1 << z;
      }
      if ((((ex >> 0) ^ (ex >> 13)) & 1) != 1) dm |= 1 << 9;
      if ((((TE(&use->x, 16) >> 24) ^ (ex >> 24)) & 1) != 0) dm |= 1 << 10;
      if ((((TE(&use->x, 16) >> 15) ^ (ex >> 15)) & 1) != 0) dm |= 1 << 11;
      if ((((TA(&use->x, 15) >> 29) ^ (TA(&use->x, 17) >> 29)) & 1) != 0) dm |= 1 << 12;
      __atomic_fetch_add(&tl_d174_mask[dm], 1, __ATOMIC_RELAXED);
    }
    int ok[TL_MAXREL + 2]; int any = 0;
    for (int k = 0; k < nc; k++) { ok[k] = tl_rowsok(g->C[k], use, g->a, g->b); cnt[CN_EV0 + k] += ok[k]; }
    int wmask = 0;
    if (tl_w16on) {
      for (int r = 0; r < 6; r++) { int bit = ((use->x.w[16] >> W16R[r][0]) ^ (use->x.w[16] >> W16R[r][1])) & 1; if (bit != W16R[r][2]) wmask |= 1 << r; }
      __atomic_fetch_add(&tl_w16_N[wmask], 1, __ATOMIC_RELAXED);
      if (!ok[0]) { char why[512]; for (int t = g->a; t <= g->b; t++) if (!tl_rowok(g->C[0], use, t)) { tl_row_fail(g->C[0], use, t, why, sizeof why); int kd = why[1] == 'A' ? 0 : why[1] == 'E' ? 1 : why[1] == 'W' ? 2 : 3; __atomic_fetch_add(&tl_death[wmask][t][kd], 1, __ATOMIC_RELAXED); break; } }
      hist_add(tid, wmask, 0, 0, use->y.w[16] - use->x.w[16]); hist_add(tid, wmask, 0, 1, use->y.w[18] - use->x.w[18]); hist_add(tid, wmask, 0, 2, use->y.w[23] - use->x.w[23]); if (ok[0]) hist_add(tid, wmask, 0, 3, use->y.w[31] - use->x.w[31]);
    }
    int ex = g->event == 0 ? tl_state_eq(use, g->b) : tl_state_eq(use, M->nr - 1);
    if (g->carrier && g->a <= M->e1) {
      int hi = g->b < M->e1 ? g->b : M->e1; any = 0;
      for (int k = 0; k < nc; k++) if (tl_rowsok(g->C[k], use, g->a, hi)) any = 1;
      ex = ex && any;
    }
    cnt[CN_EXACT] += ex;
    if (tl_w16on && ok[0] && !ex) {
      int fa = -1, fe = -1, fw = -1; for (int t = 26; t < M->nr; t++) { if (fa < 0 && TA(&use->x, t) != TA(&use->y, t)) fa = t; if (fe < 0 && TE(&use->x, t) != TE(&use->y, t)) fe = t; if (fw < 0 && use->x.w[t] != use->y.w[t]) fw = t; }
      __atomic_fetch_add(&tl_cne[wmask][fw < 0 ? 0 : fw], 1, __ATOMIC_RELAXED);
    }
    if (tl_w16on && ex) {
      __atomic_fetch_add(&tl_w16_EX[wmask], 1, __ATOMIC_RELAXED);
      hist_add(tid, wmask, 1, 0, use->y.w[16] - use->x.w[16]); hist_add(tid, wmask, 1, 1, use->y.w[18] - use->x.w[18]); hist_add(tid, wmask, 1, 2, use->y.w[23] - use->x.w[23]);
      /* independent full-path hash of both members: rebuild from the 16 message words and the chaining value */
      u32 cv[8], ox[8], oy[8], wx[16], wy[16]; for (int i = 0; i < 4; i++) { cv[i] = TA(&use->x, -1 - i); cv[4 + i] = TE(&use->x, -1 - i); }
      for (int i = 0; i < 16; i++) { wx[i] = use->x.w[i]; wy[i] = use->y.w[i]; }
      tl_compress_ref(cv, wx, M->nr, ox); tl_compress_ref(cv, wy, M->nr, oy);
      if (memcmp(ox, oy, 32)) __atomic_fetch_add(&tl_w16_FALSE, 1, __ATOMIC_RELAXED);
      __atomic_fetch_add(&tl_w16_EXN, 1, __ATOMIC_RELAXED);
    }
    for (int k = 0; k < nc; k++) cnt[CN_JOINT0 + k] += (ex && ok[k]);
    if (g->eqrow > 0) {
      int pr = tl_state_eq(use, g->eqrow);
      for (int j = 0; j < g->neqw && pr; j++) if (use->x.w[g->eqw[j]] != use->y.w[g->eqw[j]]) pr = 0;
      cnt[CN_EQ_EX] += pr && ex; cnt[CN_EQ_NEX] += pr && !ex; cnt[CN_NEQ_EX] += !pr && ex;
    }
  }
}
static void ratio_ci(const u64 *pc, int np, int ncnt, int inum, int iden, int lo, int hi, double *R, double *h) {
  double se = 0, sn = 0, n = 0;
  for (int i = lo; i < hi; i++) { sn += (double)pc[(size_t)i * ncnt + inum]; se += (double)pc[(size_t)i * ncnt + iden]; n++; }
  (void)np;
  if (se == 0) { *R = NAN; *h = NAN; return; }
  double r = sn / se, v = 0;
  for (int i = lo; i < hi; i++) { double d = (double)pc[(size_t)i * ncnt + inum] - r * (double)pc[(size_t)i * ncnt + iden]; v += d * d; }
  v = v * n / (n > 1 ? n - 1 : 1) / (se * se);
  *R = r; *h = 1.96 * sqrt(v);
}
int tl_window(const TLModel *M, const TLWinCfg *g, TLWinRes *res) {
  memset(res, 0, sizeof *res);
  double l2; TLPart *P = tl_smc_prefix(M, g->pre, g->a, g->np, g->m, g->mt2, g->seed, &l2, g->verbose);
  res->log2prefix = l2; if (!P) return -1;
  int np = g->np, nth = tl_threads(); RecV *tv = calloc(nth, sizeof(RecV)); TLRng R = tl_rng(g->seed, 98, 0, 0);
  TLPart *P2 = malloc((size_t)np * sizeof(TLPart));
  double west = 1.0;
  int nc = g->nc;
  for (int i = 0; i < np; i++) P[i].alive = (1u << nc) - 1;
  int hiE = g->b < M->e1 ? g->b : M->e1;
  for (int t = g->a; t <= hiE; t++) {
    u32 fv = 0, fm = g->carrier ? forced_mask(g->C, nc, t, &fv) : 0;
    StageCtx sc = {M, P, t, g->a, g->b, g->seed, (u64)t + 200, g->mw, fm, fv, g->C, nc, g->carrier, tv, NULL, NULL, 0};
    tl_parfor(np, 4, w_estage, &sc);
    long cnt; if (!resample_fast(M, &P, &P2, np, tv, nth, 0, t, g->seed, (u64)t + 200, &R, &cnt)) { if (g->verbose) printf("  window stage %d: dead\n", t); free(P); free(P2); free(tv); return -1; }
    west *= ldexp(1.0, -__builtin_popcount(fm)) * (double)cnt / ((double)np * g->mw);
    if (g->verbose) printf("  window stage %2d (carrier %s): forced %2d bits, accepted %ld of %ld, log2 carrier %.4f\n", t, g->carrier ? "union" : "none", __builtin_popcount(fm), cnt, (long)np * g->mw, log2(west));
  }
  res->log2carrier = log2(west);
  /* FIX 2026-10-12: late words are redrawn for every final proposal whenever the model has late words. Before, a window starting
     after row e1+1 kept the late words of the prefix (one sample per particle, --mt ignored), so chi38 rows 23.. got 1024 samples.
     A redraw that breaks a prefix row is rejected (CN_BROKEN), which samples the late words from their law given the prefix. */
  int latefree = 0; for (int i = 0; i < 16; i++) if (M->var[i].type != V_FIXED && M->var[i].late) latefree = 1;
  FinCtx fc = {M, P, g, latefree, latefree ? g->mt : 1, calloc((size_t)np * CN_COUNT, sizeof(u64)), CN_COUNT};
  tl_parfor(np, 2, w_final, &fc);
  for (int i = 0; i < np; i++) for (int k = 0; k < CN_COUNT; k++) res->cnt[k] += fc.pc[(size_t)i * CN_COUNT + k];
  for (int k = 1; k < nc; k++) {
    ratio_ci(fc.pc, np, CN_COUNT, CN_EV0 + k, CN_EV0, 0, np, &res->rat[k], &res->rath[k]);
    ratio_ci(fc.pc, np, CN_COUNT, CN_EV0 + k, CN_EV0, 0, np / 2, &res->ratA[k], &res->rathA[k]);
    ratio_ci(fc.pc, np, CN_COUNT, CN_EV0 + k, CN_EV0, np / 2, np, &res->ratB[k], &res->rathB[k]);
  }
  ratio_ci(fc.pc, np, CN_COUNT, CN_EXACT, CN_EV0, 0, np, &res->rat[0], &res->rath[0]);
  ratio_ci(fc.pc, np, CN_COUNT, CN_EXACT, CN_EV0, 0, np / 2, &res->ratA[0], &res->rathA[0]);
  ratio_ci(fc.pc, np, CN_COUNT, CN_EXACT, CN_EV0, np / 2, np, &res->ratB[0], &res->rathB[0]);
  res->latefree = latefree;
  free(fc.pc); free(P); free(P2); for (int i = 0; i < nth; i++) free(tv[i].r); free(tv);
  return 0;
}

/* ---------------- exact enumeration */
static u32 pdep32(u64 idx, u32 mask) { u32 r = 0; for (int b = 0; b < 32; b++) if ((mask >> b) & 1) { if (idx & 1) r |= 1u << b; idx >>= 1; } return r; }
int tl_spec_parse(const TLModel *M, const char *s, TLEnumSpec *e) {
  memset(e, 0, sizeof *e);
  int n = tl_parse_word(s, &e->k, &e->row); if (n < 0) return -1;
  if (e->k == KA) { fprintf(stderr, "enumerate W<i> (i<16) or E<t> (E-driven rows)\n"); return -1; }
  if (e->k == KW && e->row > 15) { fprintf(stderr, "W%d is an expanded word, not free; enumerate E%d (E-driven) or the base words it depends on\n", e->row, e->row); return -1; }
  if (e->k == KE && (M->e0 < 0 || e->row < M->e0 || e->row > M->e1)) { fprintf(stderr, "E%d is not an E-driven row of this model\n", e->row); return -1; }
  if (e->k == KW && M->e0 >= 0 && e->row <= M->e1 - 16) { fprintf(stderr, "W%d is solved by the E-driven rows; enumerate E%d instead\n", e->row, e->row + 16); return -1; }
  const char *p = s + n; if (*p == ':') p++;
  if (!*p || !strcmp(p, "all")) { e->kind = ES_ALL; e->n = 1ull << 32; }
  else if (!strncmp(p, "mask:", 5)) { e->kind = ES_MASK; e->mask = (u32)strtoul(p + 5, NULL, 16); e->n = 1ull << __builtin_popcount(e->mask); }
  else if (!strcmp(p, "cell")) { const TLCell *c = &M->full.c[e->k][e->row]; e->kind = ES_CELL; e->mask = ~c->m; e->fix = c->v; e->n = 1ull << __builtin_popcount(e->mask); }
  else if (!strcmp(p, "set")) { if (e->k != KW) return -1; const TLVar *v = &M->var[e->row];
    if (v->type == V_LIST) { e->kind = ES_LIST; e->n = (u64)v->nvals; }
    else if (v->type == V_CELL || (v->type == V_FSET && v->cell)) { const TLCell *c = &M->full.c[KW][e->row]; e->kind = ES_SETCELL; e->mask = ~c->m; e->fix = c->v; e->n = 1ull << __builtin_popcount(e->mask); }
    else { e->kind = ES_SET; e->n = 1ull << 32; } }
  else { fprintf(stderr, "spec '%s': use :all :mask:HEX :cell :set\n", p); return -1; }
  return 0;
}
static int spec_value(const TLModel *M, const TLEnumSpec *e, u64 idx, u32 base, u32 *out) {
  switch (e->kind) {
    case ES_ALL: *out = (u32)idx; return 1;
    case ES_MASK: *out = (base & ~e->mask) | pdep32(idx, e->mask); return 1;
    case ES_CELL: *out = e->fix | pdep32(idx, e->mask); return 1;
    case ES_LIST: *out = M->var[e->row].vals[idx]; return 1;
    case ES_SET: *out = (u32)idx; return tl_var_member(M, e->row, *out);
    case ES_SETCELL: *out = e->fix | pdep32(idx, e->mask); return tl_var_member(M, e->row, *out);
  }
  return 0;
}
typedef struct { const TLModel *M; const TLExactCfg *g; const TLPair *bp; const TLCoord *bc; u64 n1, n2, per; u64 (*acc)[EX_COUNT]; int incr, tmin; u64 *hist; } ExCtx;
static void w_exact(void *vctx, long blk, int tid) {
  ExCtx *s = vctx; const TLModel *M = s->M; const TLExactCfg *g = s->g; u64 *A = s->acc[tid];
  u64 tot = s->n1 * s->n2, lo = (u64)blk * s->per, hi = lo + s->per; if (hi > tot) hi = tot;
  TLPair q; TLCoord c; int pre0 = -1;
  if (s->incr) { q = *s->bp; if (s->tmin >= g->a) pre0 = tl_rowsok(g->pre, &q, M->lorow, g->a - 1); }
  for (u64 id = lo; id < hi; id++) {
    u64 i1 = id % s->n1, i2 = id / s->n1; c = *s->bc; u32 v;
    const TLEnumSpec *e = &g->sp[0];
    if (!spec_value(M, e, i1, e->k == KW ? c.wx[e->row] : c.ex[e->row], &v)) continue;
    if (e->k == KW) c.wx[e->row] = v; else c.ex[e->row] = v;
    if (g->nsp > 1) { e = &g->sp[1]; if (!spec_value(M, e, i2, e->k == KW ? c.wx[e->row] : c.ex[e->row], &v)) continue; if (e->k == KW) c.wx[e->row] = v; else c.ex[e->row] = v; }
    A[EX_MEMBER]++;
    if (s->incr) tl_build_from(M, &c, &q, s->tmin, g->event == 0 ? g->b : M->nr - 1);   /* rows < tmin of q never change */
    else { if (!tl_build(M, &c, &q)) A[EX_INCONS]++; }
    int pre = pre0 >= 0 ? pre0 : tl_rowsok(g->pre, &q, M->lorow, g->a - 1);
    int ok[TL_MAXREL + 2]; for (int k = 0; k < g->nc; k++) ok[k] = tl_rowsok(g->C[k], &q, g->a, g->b);
    int ex = g->event == 0 ? tl_state_eq(&q, g->b) : tl_state_eq(&q, M->nr - 1);
    A[EX_PRE] += pre; A[EX_EXACT] += ex; A[EX_PEXACT] += pre && ex;
    for (int k = 0; k < g->nc; k++) { A[EX_EV0 + k] += ok[k]; A[EX_PEV0 + k] += pre && ok[k]; A[EX_PXEV0 + k] += pre && ex && ok[k]; }
    if (s->hist && pre && ok[g->hist - 1]) __atomic_fetch_add(&s->hist[id], 1, __ATOMIC_RELAXED);
  }
}
int tl_exact(const TLModel *M, const TLExactCfg *g, const TLCoord *bc, TLExactRes *r) {
  memset(r, 0, sizeof *r);
  u64 n1 = g->sp[0].n, n2 = g->nsp > 1 ? g->sp[1].n : 1;
  if (n1 * n2 > (1ull << 38) || (n2 > 1 && n1 > (1ull << 32) / 1)) { if (n1 > 0 && n2 > (1ull << 38) / n1) { fprintf(stderr, "enumeration too large\n"); return -1; } }
  TLPair bp; tl_build(M, bc, &bp);
  int incr = 1, tmin = TL_NR;
  for (int i = 0; i < g->nsp; i++) { if (g->sp[i].k != KE) incr = 0; else if (g->sp[i].row < tmin) tmin = g->sp[i].row; }
  int nth = tl_threads(); u64 (*acc)[EX_COUNT] = calloc(nth, sizeof *acc);
  u64 tot = n1 * n2, per = 1ull << 16; long nblk = (long)((tot + per - 1) / per);
  ExCtx x = {M, g, &bp, bc, n1, n2, per, acc, incr, tmin, NULL};
  r->hist = NULL; if (g->hist > 0 && g->hist <= g->nc && tot <= (1ull << 16)) { r->hist = calloc(tot, 8); x.hist = r->hist; }
  tl_parfor(nblk, 1, w_exact, &x);
  for (int t = 0; t < nth; t++) for (int k = 0; k < EX_COUNT; k++) r->c[k] += acc[t][k];
  r->total = tot; free(acc); return 0;
}
