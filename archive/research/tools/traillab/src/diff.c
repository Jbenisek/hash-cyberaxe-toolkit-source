/* diff.c - signed-difference tools (our code): signed representations of a modular difference, exhaustive word-level
   counts of sigma-function differences, and the backward analysis of a row (rows 22-24 analysis of r2224.c, generalised). */
#define _GNU_SOURCE
#include "diff.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>

/* ---------------- hash map u64 -> u64 count */
typedef struct { u64 *k, *v; long cap, n; } HM;
static void hm_init(HM *h, long cap) { h->cap = cap; h->n = 0; h->k = calloc(cap, 8); h->v = calloc(cap, 8); }
static void hm_free(HM *h) { free(h->k); free(h->v); }
static void hm_add(HM *h, u64 key, u64 n);
static void hm_grow(HM *h) { HM g; hm_init(&g, h->cap * 2); for (long i = 0; i < h->cap; i++) if (h->v[i]) hm_add(&g, h->k[i], h->v[i]); hm_free(h); *h = g; }
static void hm_add(HM *h, u64 key, u64 n) {
  if (2 * (h->n + 1) > h->cap) hm_grow(h);
  long i = (long)((key * 0x9e3779b97f4a7c15ull) >> 20) & (h->cap - 1);
  while (h->v[i] && h->k[i] != key) i = (i + 1) & (h->cap - 1);
  if (!h->v[i]) { h->k[i] = key; h->n++; } h->v[i] += n;
}
typedef struct { u64 k, v; } KV;
static int cmpkv(const void *a, const void *b) { const KV *x = a, *y = b; return x->v < y->v ? 1 : x->v > y->v ? -1 : (x->k > y->k) - (x->k < y->k); }
static KV *hm_sorted(const HM *h, long *n) { KV *a = malloc((h->n + 1) * sizeof(KV)); long m = 0; for (long i = 0; i < h->cap; i++) if (h->v[i]) { a[m].k = h->k[i]; a[m].v = h->v[i]; m++; } qsort(a, m, sizeof(KV), cmpkv); *n = m; return a; }

/* signed pattern string, MSB first: n = (0 -> 1) i.e. +2^b, u = (1 -> 0) i.e. -2^b */
void tl_sym(u32 plus, u32 minus, char out[33]) { for (int i = 0; i < 32; i++) { int b = 31 - i; out[i] = ((plus >> b) & 1) ? 'n' : ((minus >> b) & 1) ? 'u' : '='; } out[32] = 0; }

/* ---------------- all signed-digit representations of D mod 2^32 */
typedef struct { u32 plus, minus; } SD;
static void bsd_rec(u64 r, int i, u32 pl, u32 mi, int hw, int maxhw, SD **out, long *n, long *cap) {
  if (i == 32) { if (*n == *cap) { *cap = *cap ? *cap * 2 : 256; *out = realloc(*out, *cap * sizeof(SD)); } (*out)[*n].plus = pl; (*out)[*n].minus = mi; (*n)++; return; }
  u64 mk = (i == 31) ? 0 : ((1ull << (31 - i)) - 1);
  if (!(r & 1)) { bsd_rec((r >> 1) & mk, i + 1, pl, mi, hw, maxhw, out, n, cap); return; }
  if (hw >= maxhw) return;
  bsd_rec(((r - 1) >> 1) & mk, i + 1, pl | (1u << i), mi, hw + 1, maxhw, out, n, cap);
  bsd_rec(((r + 1) >> 1) & mk, i + 1, pl, mi | (1u << i), hw + 1, maxhw, out, n, cap);
}
static int cmpsd(const void *a, const void *b) { const SD *x = a, *y = b; int hx = __builtin_popcount(x->plus | x->minus), hy = __builtin_popcount(y->plus | y->minus); if (hx != hy) return hx - hy; u32 kx = x->plus | x->minus, ky = y->plus | y->minus; return kx < ky ? -1 : kx > ky; }
long tl_bsd(u32 D, int maxhw, u32 **plus, u32 **minus) {
  SD *a = NULL; long n = 0, cap = 0; bsd_rec(D, 0, 0, 0, 0, maxhw, &a, &n, &cap);
  qsort(a, n, sizeof(SD), cmpsd);
  *plus = malloc((n + 1) * 4); *minus = malloc((n + 1) * 4);
  for (long i = 0; i < n; i++) { (*plus)[i] = a[i].plus; (*minus)[i] = a[i].minus; }
  free(a); return n;
}
void tl_print_bsd(u32 D, int maxhw, int limit, u32 mark_xor, u32 mark_plus) {
  u32 *pl, *mi; long n = tl_bsd(D, maxhw, &pl, &mi); double mass = 0;
  for (long i = 0; i < n; i++) mass += ldexp(1.0, -__builtin_popcount(pl[i] | mi[i]));
  printf("    signed patterns of %08x with weight <= %d: %ld (probability mass %.10f of the 2^32 words x; PROVED: Pr = 2^-weight each)\n", D, maxhw, n, mass);
  for (long i = 0; i < n && i < limit; i++) { char s[33]; tl_sym(pl[i], mi[i], s); int hw = __builtin_popcount(pl[i] | mi[i]);
    printf("      %s  xor %08x  w %2d  Pr 2^-%d%s\n", s, pl[i] | mi[i], hw, hw, (mark_xor && (pl[i] | mi[i]) == mark_xor && pl[i] == mark_plus) ? "   <- characteristic" : ""); }
  if (n > limit) printf("      ... %ld more\n", n - limit);
  free(pl); free(mi);
}

/* ---------------- exhaustive word count */
typedef struct { const TLSdiffCfg *g; u64 cnt[64][4]; HM hx[64], hs[64]; } SdCtx;
static void w_sdiff(void *vctx, long blk, int tid) {
  SdCtx *s = vctx; const TLSdiffCfg *g = s->g; u64 lo = (u64)blk << 20, hi = lo + (1ull << 20);
  u64 c0 = 0, c1 = 0, c2 = 0;
  for (u64 X = lo; X < hi; X++) {
    u32 x = (u32)X, y = x + g->D, xr = x ^ y;
    if (g->usexor && xr != g->xr) continue;
    c0++;
    int ok = (u32)(tl_fn(g->func, y) - tl_fn(g->func, x)) == g->T;
    if (!ok) continue;
    c1++;
    int cell = g->cellok ? g->cellok(g->cellctx, x, y) : 0; c2 += cell;
    hm_add(&s->hx[tid], xr, 1);
    hm_add(&s->hs[tid], ((u64)(x & xr) << 32) | xr, 1);
  }
  s->cnt[tid][0] += c0; s->cnt[tid][1] += c1; s->cnt[tid][2] += c2;
}
int tl_sdiff_count(const TLSdiffCfg *g, TLSdiffRes *r, int print, int limit) {
  int nth = tl_threads(); SdCtx *s = calloc(1, sizeof(SdCtx)); s->g = g;
  for (int i = 0; i < nth; i++) { hm_init(&s->hx[i], 1 << 10); hm_init(&s->hs[i], 1 << 10); }
  tl_parfor(4096, 1, w_sdiff, s);
  HM hx, hs; hm_init(&hx, 1 << 10); hm_init(&hs, 1 << 10); memset(r, 0, sizeof *r);
  for (int i = 0; i < nth; i++) {
    r->domain += s->cnt[i][0]; r->exact += s->cnt[i][1]; r->cellexact += s->cnt[i][2];
    for (long j = 0; j < s->hx[i].cap; j++) if (s->hx[i].v[j]) hm_add(&hx, s->hx[i].k[j], s->hx[i].v[j]);
    for (long j = 0; j < s->hs[i].cap; j++) if (s->hs[i].v[j]) hm_add(&hs, s->hs[i].k[j], s->hs[i].v[j]);
    hm_free(&s->hx[i]); hm_free(&s->hs[i]);
  }
  r->nxor = hx.n; r->nsigned = hs.n;
  if (print) {
    long n; KV *a = hm_sorted(&hx, &n);
    printf("    XOR patterns of the exact set: %ld\n", n);
    for (long i = 0; i < n && i < limit; i++) printf("      xor %08x  w %2d  count %12llu  share %.6f\n", (u32)a[i].k, __builtin_popcount((u32)a[i].k), (unsigned long long)a[i].v, (double)a[i].v / (double)r->exact);
    if (n > limit) printf("      ... %ld more\n", n - limit);
    free(a); a = hm_sorted(&hs, &n);
    printf("    signed patterns of the exact set: %ld\n", n);
    for (long i = 0; i < n && i < limit; i++) { u32 xr = (u32)a[i].k, xm = (u32)(a[i].k >> 32); char sy[33]; tl_sym(xr & ~xm, xm, sy);
      printf("      %s  count %12llu  share %.6f\n", sy, (unsigned long long)a[i].v, (double)a[i].v / (double)r->exact); }
    if (n > limit) printf("      ... %ld more\n", n - limit);
    free(a);
  }
  hm_free(&hx); hm_free(&hs); free(s); return 0;
}

/* ---------------- backward analysis */
static u32 cellxor(const TLModel *M, int k, int r) { if (r < 0) return 0; return M->full.c[k][r].d; }
static u32 cellmod(const TLModel *M, int k, int r) { if (r < 0) return 0; return tl_word_mod(&M->full.c[k][r]); }
static u32 s1in(u32 outmask) { u32 m = 0; for (int j = 0; j < 32; j++) if ((outmask >> j) & 1) m |= (1u << ((j + 6) & 31)) | (1u << ((j + 11) & 31)) | (1u << ((j + 25) & 31)); return m; }
static u32 s0in(u32 outmask) { u32 m = 0; for (int j = 0; j < 32; j++) if ((outmask >> j) & 1) m |= (1u << ((j + 2) & 31)) | (1u << ((j + 13) & 31)) | (1u << ((j + 22) & 31)); return m; }
static u32 pdep(u64 idx, u32 mask) { u32 r = 0; for (int b = 0; b < 32; b++) if ((mask >> b) & 1) { if (idx & 1) r |= 1u << b; idx >>= 1; } return r; }
/* distribution of dSig(w1) + dBool(w1,w2,w3) over the free relevant bits of the three words (values fixed by the cells) */
static void boolsig_dist(const TLModel *M, int k, int t, HM *h, int *sampled, int *nfree) {
  const TLCell *c[3]; u32 dx[3];
  for (int i = 0; i < 3; i++) { int r = t - 1 - i; static const TLCell zero = {0}; c[i] = r >= 0 ? &M->full.c[k][r] : &zero; dx[i] = c[i]->d; }
  u32 sigout = k == KE ? BS1(dx[0]) : BS0(dx[0]);
  u32 pos = dx[0] | dx[1] | dx[2];
  u32 rel[3] = {(k == KE ? s1in(sigout) : s0in(sigout)) | pos, pos, pos};
  u32 fr[3]; int nf = 0; for (int i = 0; i < 3; i++) { fr[i] = rel[i] & ~c[i]->m; nf += __builtin_popcount(fr[i]); }
  *nfree = nf; *sampled = nf > 26;
  u64 N = *sampled ? (1ull << 24) : (1ull << nf); TLRng R = tl_rng(7, 7, 7, (u64)t);
  int n0 = __builtin_popcount(fr[0]), n1 = __builtin_popcount(fr[1]);
  for (u64 id = 0; id < N; id++) {
    u64 a = *sampled ? tl_next(&R) : id;
    u32 x0, x1, x2;
    if (*sampled) { x0 = c[0]->v | (tl_r32(&R) & fr[0]); x1 = c[1]->v | (tl_r32(&R) & fr[1]); x2 = c[2]->v | (tl_r32(&R) & fr[2]); }
    else { x0 = c[0]->v | pdep(a, fr[0]); x1 = c[1]->v | pdep(a >> n0, fr[1]); x2 = c[2]->v | pdep(a >> (n0 + n1), fr[2]); }
    u32 y0 = x0 ^ dx[0], y1 = x1 ^ dx[1], y2 = x2 ^ dx[2], d;
    if (k == KE) d = (BS1(y0) - BS1(x0)) + (CH(y0, y1, y2) - CH(x0, x1, x2));
    else d = (BS0(y0) - BS0(x0)) + (MAJ(y0, y1, y2) - MAJ(x0, x1, x2));
    hm_add(h, d, 1);
  }
}
static double hm_prob(const HM *h, u64 key) { u64 tot = 0, hit = 0; for (long i = 0; i < h->cap; i++) if (h->v[i]) { tot += h->v[i]; if (h->k[i] == key) hit = h->v[i]; } return tot ? (double)hit / (double)tot : 0; }
static void signings(const char *name, u32 xr, u32 chiplus, u32 need_other_mod, const HM *h, u32 target_minus) {
  /* each signing s of xr: modular m(s); row holds iff X = target - m(s) - other */
  int hw = __builtin_popcount(xr);
  if (hw > 12) { printf("    signings of %s: %d difference bits, not listed\n", name, hw); return; }
  printf("    alternative signings of %s (same XOR %08x, %d signings):\n", name, xr, 1 << hw);
  int idx[32], n = 0; for (int b = 0; b < 32; b++) if ((xr >> b) & 1) idx[n++] = b;
  for (u32 s = 0; s < (1u << hw); s++) {
    u32 pl = 0, mi = 0, m = 0; for (int i = 0; i < n; i++) { if ((s >> i) & 1) { pl |= 1u << idx[i]; m += 1u << idx[i]; } else { mi |= 1u << idx[i]; m -= 1u << idx[i]; } }
    double p = hm_prob(h, (u32)(target_minus - m - need_other_mod)); char sy[33]; tl_sym(pl, mi, sy);
    printf("      %s  mod %08x  Pr[row holds] %.6g%s\n", sy, m, p, pl == chiplus ? "   <- characteristic" : "");
  }
}
int tl_backward(const TLModel *M, int b0, int b1, int maxhw, int do_enum) {
  printf("backward analysis, %s, rows %d..%d. Words' modular differences are the characteristic's signed cells.\n", M->name, b0, b1);
  printf("Model for X = dSigma + dBool: the free bits of the three input words are uniform; bits fixed by cells (values, signs) are used; two-bit and '+' conditions are not applied.\n");
  for (int t = b0; t <= b1 && t < M->nr; t++) {
    printf("\n== row %d ==\n", t);
    u32 dE = cellmod(M, KE, t), dA = cellmod(M, KA, t), dW = cellmod(M, KW, t), dE4 = cellmod(M, KE, t - 4), dA4 = cellmod(M, KA, t - 4);
    printf("  chi: dE%d %08x dA%d %08x dW%d %08x dE%d %08x dA%d %08x\n", t, dE, t, dA, t, dW, t - 4, dE4, t - 4, dA4);
    for (int k = KE; k >= KA; k--) {
      HM h; hm_init(&h, 1 << 8); int smp, nf; boolsig_dist(M, k, t, &h, &smp, &nf);
      long n; KV *a = hm_sorted(&h, &n); u64 tot = 0; for (long i = 0; i < n; i++) tot += a[i].v;
      u32 need = k == KE ? (u32)(dE - dA4 - dE4 - dW) : (u32)(dA - dE + dA4);
      double p = hm_prob(&h, need);
      printf("  %s: X%s = %s(%s%d) + %s(%s%d,%s%d,%s%d): %ld values over %d free bits (%s)\n", k == KE ? "E equation dE_t = dA_{t-4} + dE_{t-4} + X + dW_t" : "A equation dA_t = dE_t - dA_{t-4} + X",
        k == KE ? "E" : "A", k == KE ? "dS1" : "dS0", tl_kname(k), t - 1, k == KE ? "dCH" : "dMAJ", tl_kname(k), t - 1, tl_kname(k), t - 2, tl_kname(k), t - 3, n, nf, smp ? "SAMPLED 2^24" : "EXACT enumeration");
      for (long i = 0; i < n && i < 8; i++) printf("      X = %08x  Pr %.6g%s\n", (u32)a[i].k, (double)a[i].v / (double)tot, (u32)a[i].k == need ? "   <- needed by the characteristic" : "");
      printf("    needed X = %08x : Pr %.6g (%s)\n", need, p, smp ? "COMPUTED, sampled" : "PROVED under the model");
      if (k == KE) {
        u32 xw = cellxor(M, KW, t), xe = cellxor(M, KE, t - 4);
        u32 plw = xw & ~M->full.c[KW][t].v, ple = xe & ~(t - 4 >= 0 ? M->full.c[KE][t - 4].v : 0);
        printf("  words of row %d that can produce it (other words as in the characteristic), for the most likely X values:\n", t);
        for (long i = 0; i < n && i < 3; i++) {
          u32 x = (u32)a[i].k; printf("   X = %08x (Pr %.6g):\n", x, (double)a[i].v / (double)tot);
          printf("    W%d needs modular difference %08x\n", t, (u32)(dE - dA4 - dE4 - x)); tl_print_bsd((u32)(dE - dA4 - dE4 - x), maxhw, 12, xw, plw);
          if (t - 4 >= 0) { printf("    E%d needs modular difference %08x\n", t - 4, (u32)(dE - dA4 - dW - x)); tl_print_bsd((u32)(dE - dA4 - dW - x), maxhw, 12, xe, ple); }
        }
        if (xw) signings("W_t", xw, plw, dA4 + dE4, &h, dE);
        if (xe) signings("E_{t-4}", xe, ple, dA4 + dW, &h, dE);
      }
      free(a); hm_free(&h);
    }
  }
  /* schedule */
  printf("\n== message schedule: dW_t = ds1(W_{t-2}) + dW_{t-7} + ds0(W_{t-15}) + dW_{t-16} ==\n");
  printf("  base words W0..W15: modular difference = published y - x (held by construction); sigma terms constant when the word is fixed, or in an F-set of that sigma\n");
  for (int t = 16; t < M->nr; t++) {
    int js[4] = {t - 2, t - 7, t - 15, t - 16}, fn[4] = {F_s1, F_ID, F_s0, F_ID};
    u32 C = 0; int nv = 0, vj = -1, vf = -1; char desc[512] = ""; int L = 0;
    for (int q = 0; q < 4; q++) {
      int j = js[q]; u32 dj = j < 16 ? M->dl[j] : cellmod(M, KW, j);
      if (dj == 0) continue;
      if (fn[q] == F_ID) { C += dj; L += snprintf(desc + L, sizeof desc - L, " +dW%d(%08x)", j, dj); continue; }
      if (j < 16) {
        const TLVar *v = &M->var[j];
        if (v->type == V_FIXED) { u32 c = tl_fn(fn[q], M->my[j]) - tl_fn(fn[q], M->mx[j]); C += c; L += snprintf(desc + L, sizeof desc - L, " +d%s(W%d)=%08x[fixed]", fn[q] == F_s1 ? "s1" : "s0", j, c); continue; }
        if (v->type == V_FSET && v->func == fn[q]) { C += v->T; L += snprintf(desc + L, sizeof desc - L, " +d%s(W%d)=%08x[F-set]", fn[q] == F_s1 ? "s1" : "s0", j, v->T); continue; }
        if (v->type == V_LIST) { int cst = 1; u32 c0 = tl_fn(fn[q], v->vals[0] + dj) - tl_fn(fn[q], v->vals[0]); for (long i = 1; i < v->nvals; i++) if ((u32)(tl_fn(fn[q], v->vals[i] + dj) - tl_fn(fn[q], v->vals[i])) != c0) cst = 0;
          if (cst) { C += c0; L += snprintf(desc + L, sizeof desc - L, " +d%s(W%d)=%08x[list-constant]", fn[q] == F_s1 ? "s1" : "s0", j, c0); continue; } }
      }
      nv++; vj = j; vf = fn[q]; L += snprintf(desc + L, sizeof desc - L, " +d%s(W%d)[value-dependent, dW%d=%08x]", fn[q] == F_s1 ? "s1" : "s0", j, j, dj);
    }
    u32 chi = cellmod(M, KW, t);
    if (!nv) printf("  W%-2d: dW = %08x PROVED%s; characteristic %08x %s\n", t, C, desc, chi, C == chi ? "(agrees)" : "(DISAGREES: Pr 0 on this model)");
    else if (nv == 1) {
      u32 T = chi - C, dj = vj < 16 ? M->dl[vj] : cellmod(M, KW, vj);
      printf("  W%-2d: characteristic %08x =%s ; requires %s(W%d + %08x) - %s(W%d) = %08x\n", t, chi, desc, vf == F_s1 ? "s1" : "s0", vj, dj, vf == F_s1 ? "s1" : "s0", vj, T);
      if (do_enum) {
        TLSdiffCfg g = {0}; g.D = dj; g.func = vf; g.T = T; TLCellCtx cc = {M, KW, vj}; g.cellok = tl_cellctx_ok; g.cellctx = &cc;
        TLSdiffRes r; tl_sdiff_count(&g, &r, 1, 8);
        printf("    EXACT over 2^32 W%d: %llu words (2^%.4f); with W%d's printed cell: %llu (2^%.4f); ratio exact/cell %.6f\n", vj, (unsigned long long)r.exact, log2((double)r.exact), vj,
          (unsigned long long)r.cellexact, r.cellexact ? log2((double)r.cellexact) : -INFINITY, r.cellexact ? (double)r.exact / (double)r.cellexact : INFINITY);
      }
    } else printf("  W%-2d: characteristic %08x =%s ; %d value-dependent terms (joint; not enumerated)\n", t, chi, desc, nv);
  }
  return 0;
}
int tl_cellctx_ok(const void *ctx, u32 x, u32 y) { const TLCellCtx *c = ctx; return tl_word_cellok(c->M, c->k, c->row, x, y); }
