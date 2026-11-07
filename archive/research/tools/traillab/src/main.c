/* traillab - CLI (our code). See README.md. */
#define _GNU_SOURCE
#include "traillab.h"
#include "smc.h"
#include "diff.h"
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int ARGC; static char **ARGV;
static const char *opt(const char *k, const char *def) { for (int i = 2; i < ARGC - 1; i++) if (!strcmp(ARGV[i], k)) return ARGV[i + 1]; return def; }
static int has(const char *k) { for (int i = 2; i < ARGC; i++) if (!strcmp(ARGV[i], k)) return 1; return 0; }
static int optall(const char *k, const char **out, int max) { int n = 0; for (int i = 2; i < ARGC - 1; i++) if (!strcmp(ARGV[i], k) && n < max) out[n++] = ARGV[i + 1]; return n; }
static const char *opt2(const char *k, const char **second) { for (int i = 2; i < ARGC - 2; i++) if (!strcmp(ARGV[i], k)) { *second = ARGV[i + 2]; return ARGV[i + 1]; } return NULL; }
static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

static TLModel *load_model(void) {
  const char *p = opt("--chi", NULL); if (!p) { fprintf(stderr, "--chi FILE required\n"); exit(2); }
  const char *ov[16]; int nov = optall("--var", ov, 16);
  TLModel *M = calloc(1, sizeof(TLModel)); if (tl_load(p, M, ov, nov)) { fprintf(stderr, "cannot load %s\n", p); exit(2); }
  if (opt("--hold-from", NULL)) {
    M->hold_from = atoi(opt("--hold-from", "0"));
    if (M->hold_from < 16 || M->hold_from <= M->e1 || M->hold_from >= M->nr) { fprintf(stderr, "--hold-from T needs max(16, e1+1) <= T < steps\n"); exit(2); }
    printf("ARTIFACT MODE (--hold-from %d): W%d..W%d of each member are held at the published values, NOT the message expansion.\n"
           "  These are not real messages; use only to reproduce the held-fixed artifact. No result of this mode is a gain.\n", M->hold_from, M->hold_from, M->nr - 1);
  }
  return M;
}
/* --relax NAME (from the file) or --relax 'name=ops' (inline) */
static int collect_relax(const TLModel *M, const TLConds *from, const TLConds **C, TLConds *store) {
  const char *rl[TL_MAXREL]; int n = optall("--relax", rl, TL_MAXREL), nc = 0;
  for (int i = 0; i < n; i++) {
    const TLConds *f = tl_find_relax(M, rl[i]);
    if (f && from == &M->base) { C[nc++] = f; continue; }
    const char *eq = strchr(rl[i], '=');
    if (f) { /* named relaxation applied on top of a non-base condition set: re-parse not possible; use as is */ C[nc++] = f; continue; }
    if (!eq) { fprintf(stderr, "relaxation '%s' not found in the file (inline form: name=ops)\n", rl[i]); exit(2); }
    char nm[48]; int L = (int)(eq - rl[i]); if (L > 47) L = 47; memcpy(nm, rl[i], L); nm[L] = 0;
    if (tl_relax_parse(M, from, eq + 1, &store[nc], nm)) exit(2);
    C[nc] = &store[nc]; nc++;
  }
  return nc;
}
static const TLConds *prefix_conds(const TLModel *M, TLConds *store) {
  const char *pr = opt("--prefix-relax", NULL);
  if (!pr) return &M->base;
  const TLConds *f = tl_find_relax(M, pr); if (f) return f;
  const char *eq = strchr(pr, '='); if (!eq) { fprintf(stderr, "prefix relaxation '%s' not found\n", pr); exit(2); }
  if (tl_relax_parse(M, &M->base, eq + 1, store, "prefix")) exit(2);
  return store;
}
static void print_model(const TLModel *M) {
  printf("model %s: %d steps, anchor row %d (x and y rows %d..%d held), E-driven rows %d..%d, lowest conditioned row %d\n", M->name, M->nr, M->anchor, M->anchor - 3, M->anchor, M->e0, M->e1, M->lorow);
  printf("  conditions: %d two-bit/linear (printed), %d in the attack model; 'except' words:", M->full.nlin, M->base.nlin);
  for (int i = 0; i < 16; i++) if (M->except[i]) printf(" W%d", i); printf("\n");
  for (int i = 0; i < 16; i++) if (M->var[i].type != V_FIXED) printf("  free word W%d (%s): %s\n", i, M->var[i].late ? "late" : "early", M->var[i].desc);
  for (int i = 0; i < M->nrelax; i++) printf("  relaxation %s\n", M->relax[i].name);
}

/* ------------------------------------------------------------------ check */
static int cmd_check(void) {
  TLModel *M = load_model(); int bad = 0;
  int st = tl_sha256_selftest(); printf("SHA-256 reference (abc) and A/E-trace vs textbook registers, 2000 random cases, step inversion: %s\n", st ? "FAIL" : "ok"); bad += st;
  print_model(M);
  u32 hx[8], hy[8]; tl_compress_ref(M->cv, M->mx, M->nr, hx); tl_compress_ref(M->cv, M->my, M->nr, hy);
  int coll = !memcmp(hx, hy, 32), dig = M->have_digest ? !memcmp(hx, M->digest, 32) : 1;
  printf("published pair: %d-step outputs %s; digest %s (%08x %08x %08x %08x %08x %08x %08x %08x)\n", M->nr, coll ? "EQUAL" : "DIFFER", dig ? "matches the file" : "DOES NOT match", hx[0], hx[1], hx[2], hx[3], hx[4], hx[5], hx[6], hx[7]); bad += !coll + !dig;
  char why[2048]; int f1 = 0, f2 = 0;
  for (int t = 0; t < M->nr; t++) { if (tl_row_fail(&M->full, &M->pub, t, why, sizeof why)) { f1++; printf("  printed conditions, row %d fails:%s\n", t, why); } }
  for (int t = 0; t < M->nr; t++) if (!tl_rowok(&M->base, &M->pub, t)) f2++;
  printf("published pair vs every printed condition (rows 0..%d): %d failing rows; vs the attack model's conditions: %d\n", M->nr - 1, f1, f2); bad += f1 + f2;
  for (int i = 0; i < M->nrelax; i++) { int f = 0; for (int t = 0; t < M->nr; t++) f += !tl_rowok(&M->relax[i], &M->pub, t); printf("relaxation %s holds on the published pair: %s\n", M->relax[i].name, f ? "NO" : "yes"); bad += f != 0; }
  /* anchored rebuild of the published coordinates */
  TLPair q; int cons = tl_build(M, &M->pubc, &q); int diff = 0;
  for (int t = -4; t < M->nr; t++) if (TA(&q.x, t) != TA(&M->pub.x, t) || TE(&q.x, t) != TE(&M->pub.x, t) || TA(&q.y, t) != TA(&M->pub.y, t) || TE(&q.y, t) != TE(&M->pub.y, t)) diff++;
  for (int t = 0; t < M->nr; t++) if (q.x.w[t] != M->pub.x.w[t] || q.y.w[t] != M->pub.y.w[t]) diff++;
  printf("rebuild of the published coordinates (backward from the anchor, E-driven rows, inverse expansion): %s, %d differing rows/words\n", cons ? "consistent" : "INCONSISTENT", diff); bad += !cons + diff;
  /* random coordinates: consistency, forward replay, incremental vs full */
  long N = atol(opt("--n", "20000")), incons = 0, fwdbad = 0, incbad = 0, expbad = 0;
  for (long it = 0; it < N; it++) {
    TLRng r = tl_rng(4242, 1, (u64)it, 0); TLCoord c = M->pubc; tl_draw_vars(M, &c, &r, 0); tl_draw_vars(M, &c, &r, 1);
    if (M->e0 >= 0) for (int t = M->e0; t <= M->e1; t++) c.ex[t] = tl_r32(&r);
    TLPair p; if (!tl_build(M, &c, &p)) incons++;
    /* x forward from its own CV and words must reproduce every row; both members' words must be the real expansion */
    TLTr fx; u32 cv[8]; for (int i = 0; i < 4; i++) { cv[i] = TA(&p.x, -1 - i); cv[4 + i] = TE(&p.x, -1 - i); }
    for (int i = 0; i < 16; i++) fx.w[i] = p.x.w[i]; tl_expand(&fx, 16, M->nr);
    for (int i = 0; i < 4; i++) { TA(&fx, -1 - i) = cv[i]; TE(&fx, -1 - i) = cv[4 + i]; }
    for (int t = 0; t < M->nr; t++) tl_step(&fx, t);
    for (int t = 0; t < M->nr; t++) if (TA(&fx, t) != TA(&p.x, t) || TE(&fx, t) != TE(&p.x, t) || fx.w[t] != p.x.w[t]) { fwdbad++; break; }
    for (int t = 16; t < M->nr; t++) if (p.y.w[t] != ss1(p.y.w[t - 2]) + p.y.w[t - 7] + ss0(p.y.w[t - 15]) + p.y.w[t - 16]) { expbad++; break; }
    if (M->e0 >= 0) for (int t = M->e0; t <= M->e1; t++) if (TE(&p.x, t) != c.ex[t]) { fwdbad++; break; }
    u32 out[8]; tl_compress_ref(cv, p.x.w, M->nr, out);
    if (out[0] != cv[0] + TA(&p.x, M->nr - 1) || out[4] != cv[4] + TE(&p.x, M->nr - 1)) fwdbad++;
    if (M->e0 >= 0) { int t = M->e0 + (int)tl_below(&r, (u64)(M->e1 - M->e0 + 1)); TLCoord c2 = c; c2.ex[t] = tl_r32(&r); TLPair a = p, b; tl_build_from(M, &c2, &a, t, M->nr - 1); tl_build(M, &c2, &b);
      for (int u = t; u < M->nr; u++) if (TA(&a.x, u) != TA(&b.x, u) || TE(&a.x, u) != TE(&b.x, u) || TA(&a.y, u) != TA(&b.y, u) || TE(&a.y, u) != TE(&b.y, u)) { incbad++; break; } }
  }
  printf("random coordinates (%ld draws, every free word and E-driven row random): y-anchor inconsistent %ld; x forward replay mismatches %ld; y expansion mismatches %ld; incremental-vs-full mismatches %ld\n", N, incons, fwdbad, expbad, incbad);
  printf("  (y-anchor inconsistent = the y member, run forward from the common CV, leaves its published dense rows: the draw lies outside the set\n"
         "   where the differences propagate as published. Such samples are still real pairs; the prefix test removes them, nothing is kept silently.)\n");
  bad += fwdbad + expbad + incbad;
  /* F-set densities */
  for (int i = 0; i < 16; i++) if (M->var[i].type == V_FSET || M->var[i].type == V_CELL) { TLRng r = tl_rng(5, 5, 5, (u64)i); long hit = 0, n = 1 << 22; for (long j = 0; j < n; j++) hit += tl_var_member(M, i, tl_r32(&r)); printf("  W%d set density (2^22 random words): %.6f = 2^%.3f\n", i, (double)hit / n, log2((double)hit / n)); }
  printf("CHECK %s\n", bad ? "FAILED" : "ok");
  return bad != 0;
}

/* ------------------------------------------------------------------ varcount */
typedef struct { const TLModel *M; int i; u64 cnt[64]; } VCCtx;
static void w_vc(void *v, long blk, int tid) { VCCtx *s = v; u64 c = 0; for (u64 x = (u64)blk << 20; x < ((u64)blk + 1) << 20; x++) c += tl_var_member(s->M, s->i, (u32)x); s->cnt[tid] += c; }
static int cmd_varcount(void) {
  TLModel *M = load_model(); const char *w = opt("--word", "W7"); int k, i; if (tl_parse_word(w, &k, &i) < 0 || k != KW || i > 15) return 2;
  VCCtx s = {M, i, {0}}; double t0 = now(); tl_parfor(4096, 1, w_vc, &s); u64 c = 0; for (int j = 0; j < 64; j++) c += s.cnt[j];
  printf("VARCOUNT %s W%d (%s): %llu members of 2^32 (2^%.6f) [EXACT, %.1f s]\n", M->name, i, M->var[i].desc, (unsigned long long)c, log2((double)c), now() - t0);
  return 0;
}

/* ------------------------------------------------------------------ window */
static void print_win(const TLModel *M, const TLWinCfg *g, const TLWinRes *r, const char *tag) {
  u64 n = r->cnt[CN_N]; double lo, hi;
  printf("%s prefix log2 P(rows %d..%d) = %.4f", tag, M->lorow, g->a - 1, r->log2prefix);
  if (g->a <= M->e1) printf(" ; window carrier log2 %.4f (%s)", r->log2carrier, g->carrier ? "union of cell events on E-driven window rows" : "none");
  printf("\n%s samples %llu (late words %s), prefix broken by redraw %llu, y-anchor inconsistent %llu, replay mismatches %llu\n", tag, (unsigned long long)n,
    r->latefree ? "redrawn per sample" : "fixed by the prefix", (unsigned long long)r->cnt[CN_BROKEN], (unsigned long long)r->cnt[CN_INCONS], (unsigned long long)r->cnt[CN_REPLAYBAD]);
  const char *ev = g->event ? "zero output difference after the last step" : "zero state difference after row b";
  for (int k = 0; k < g->nc; k++) { u64 c = r->cnt[CN_EV0 + k]; tl_wilson((double)c, (double)n, &lo, &hi);
    printf("%s   %-14s rows %d..%d: %12llu  rate %.6e (log2 %8.4f) 95%% [%.4e, %.4e]  with exact %llu\n", tag, g->C[k]->name, g->a, g->b, (unsigned long long)c, n ? (double)c / n : 0, c ? log2((double)c / n) : -INFINITY, lo, hi, (unsigned long long)r->cnt[CN_JOINT0 + k]); }
  { u64 c = r->cnt[CN_EXACT]; tl_wilson((double)c, (double)n, &lo, &hi);
    printf("%s   %-14s %s%s: %12llu  rate %.6e (log2 %8.4f) 95%% [%.4e, %.4e]\n", tag, "EXACT", ev, (g->carrier && g->a <= M->e1) ? " AND carrier" : "", (unsigned long long)c, n ? (double)c / n : 0, c ? log2((double)c / n) : -INFINITY, lo, hi); }
  printf("%s   ratios to '%s' (95%% cluster-robust over particles; halves = particles split in two):\n", tag, g->C[0]->name);
  printf("%s     EXACT/%s = %.5f +- %.5f  (log2 %+.4f)  halves %.5f +- %.5f | %.5f +- %.5f\n", tag, g->C[0]->name, r->rat[0], r->rath[0], log2(r->rat[0]), r->ratA[0], r->rathA[0], r->ratB[0], r->rathB[0]);
  for (int k = 1; k < g->nc; k++) printf("%s     %s/%s = %.5f +- %.5f  (log2 %+.4f)  halves %.5f +- %.5f | %.5f +- %.5f\n", tag, g->C[k]->name, g->C[0]->name, r->rat[k], r->rath[k], log2(r->rat[k]), r->ratA[k], r->rathA[k], r->ratB[k], r->rathB[k]);
  { double q = r->log2prefix + (r->cnt[CN_EV0] ? log2((double)r->cnt[CN_EV0] / (double)n) : -INFINITY);
    printf("%s   log2 P(rows %d..%d, model cells) = prefix + log2 rate(cells) = %.4f\n", tag, M->lorow, g->b, q); }
  if (g->eqrow > 0) { printf("%s   equivalence: predicate = zero state difference after row %d", tag, g->eqrow); for (int j = 0; j < g->neqw; j++) printf(" and dW%d = 0", g->eqw[j]);
    printf(": predicate and EXACT %llu ; predicate, not EXACT %llu ; EXACT, not predicate %llu\n", (unsigned long long)r->cnt[CN_EQ_EX], (unsigned long long)r->cnt[CN_EQ_NEX], (unsigned long long)r->cnt[CN_NEQ_EX]); }
}
static int cmd_window(void) {
  TLModel *M = load_model(); TLWinCfg g; memset(&g, 0, sizeof g);
  const char *b2; const char *a1 = opt2("--rows", &b2); if (!a1) { fprintf(stderr, "--rows A B\n"); return 2; }
  g.a = atoi(a1); g.b = atoi(b2); if (g.b >= M->nr || g.a > g.b) { fprintf(stderr, "bad rows\n"); return 2; }
  const char *ev = opt("--event", "out"); g.event = !strcmp(ev, "out"); if (strcmp(ev, "out") && strcmp(ev, "state")) return 2;
  g.np = atoi(opt("--np", "2048")); g.m = atoi(opt("--m", "256")); g.mt2 = atoi(opt("--mt2", "1024")); g.mw = atoi(opt("--mw", "256")); g.mt = atoi(opt("--mt", "4096"));
  g.carrier = strcmp(opt("--carrier", "union"), "none") != 0; g.verbose = !has("--quiet");
  static TLConds st_pre, st_rel[TL_MAXREL]; g.pre = prefix_conds(M, &st_pre);
  g.C[0] = &M->base; g.nc = 1 + collect_relax(M, &M->base, g.C + 1, st_rel);
  if (opt("--equiv", NULL)) { char *s = strdup(opt("--equiv", "")), *sv = NULL; int first = 1;
    for (char *t = strtok_r(s, ",", &sv); t; t = strtok_r(NULL, ",", &sv)) { if (*t == 'W') t++; int v = atoi(t);
      if (first) { g.eqrow = v; first = 0; } else if (g.neqw < 8) { if (v < 16 || v >= M->nr) { fprintf(stderr, "--equiv: W%d not an expanded word\n", v); return 2; } g.eqw[g.neqw++] = v; } }
    free(s); if (g.eqrow < 1 || g.eqrow >= M->nr) { fprintf(stderr, "--equiv R,Wj,...\n"); return 2; } }
  const char *seeds = opt("--seeds", "1"); u64 sd[64]; int ns = 0; { char *s = strdup(seeds), *sv = NULL; for (char *t = strtok_r(s, ",", &sv); t && ns < 64; t = strtok_r(NULL, ",", &sv)) sd[ns++] = strtoull(t, NULL, 10); free(s); }
  if (has("--no-elist")) { for (int t = 0; t < TL_NR; t++) { M->elist[t] = NULL; M->nelist[t] = 0; } }
  extern int tl_w16on, tl_autolist, tl_d174on; tl_w16on = has("--w16stats"); tl_autolist = has("--autolist"); tl_d174on = has("--d174stats");
  tl_prefix_marg_on = has("--prefix-marginals");
  memset(tl_prefix_marg_props, 0, sizeof tl_prefix_marg_props);
  memset(tl_prefix_marg_hits, 0, sizeof tl_prefix_marg_hits);
  memset(tl_prefix_w78_props, 0, sizeof tl_prefix_w78_props);
  memset(tl_prefix_w78_hits, 0, sizeof tl_prefix_w78_hits);
  print_model(M);
  printf("WINDOW rows %d..%d event=%s np %d m %d mt2 %d mw %d mt %d threads %d prefix-conditions %s\n", g.a, g.b, ev, g.np, g.m, g.mt2, g.mw, g.mt, tl_threads(), g.pre->name);
  TLWinRes tot; memset(&tot, 0, sizeof tot); double rs[64], rh[64][TL_MAXREL + 1], q3[64]; int nr = 0;
  for (int s = 0; s < ns; s++) {
    g.seed = sd[s]; TLWinRes r; double t0 = now();
    printf("-- seed %llu\n", (unsigned long long)g.seed);
    if (tl_window(M, &g, &r)) { printf("  seed %llu: no samples\n", (unsigned long long)g.seed); continue; }
    char tag[32]; snprintf(tag, sizeof tag, "[s%llu]", (unsigned long long)g.seed); print_win(M, &g, &r, tag);
    printf("[s%llu]   time %.1f s\n", (unsigned long long)g.seed, now() - t0);
    for (int k = 0; k < CN_COUNT; k++) tot.cnt[k] += r.cnt[k];
    for (int k = 0; k < g.nc; k++) rh[nr][k] = r.rath[k];
    q3[nr] = r.log2prefix + (r.cnt[CN_EV0] ? log2((double)r.cnt[CN_EV0] / (double)r.cnt[CN_N]) : -INFINITY);
    rs[nr++] = r.rat[0];
  }
  if (nr) { /* pooled 95% half-widths: independent seeds, combined as sqrt(sum h_s^2)/n_seeds (equal-size seeds) */
    double hp[TL_MAXREL + 1]; for (int k = 0; k < g.nc; k++) { double s2 = 0; for (int i = 0; i < nr; i++) s2 += rh[i][k] * rh[i][k]; hp[k] = sqrt(s2) / nr; }
    double qm = 0, qv = 0; for (int i = 0; i < nr; i++) qm += q3[i]; qm /= nr; for (int i = 0; i < nr; i++) qv += (q3[i] - qm) * (q3[i] - qm); qv = nr > 1 ? qv / (nr - 1) : 0;
    printf("== summary over %d seed(s): EXACT/%s %.5f +- %.5f", nr, g.C[0]->name, (double)tot.cnt[CN_EXACT] / (double)tot.cnt[CN_EV0], hp[0]);
    for (int k = 1; k < g.nc; k++) printf(" ; %s/%s %.5f +- %.5f", g.C[k]->name, g.C[0]->name, (double)tot.cnt[CN_EV0 + k] / (double)tot.cnt[CN_EV0], hp[k]);
    printf("\n== summary: log2 P(rows %d..%d, model cells) mean %.4f, seed sd %.4f (seeds:", M->lorow, g.b, qm, sqrt(qv)); for (int i = 0; i < nr; i++) printf(" %.4f", q3[i]); printf(")\n");
    if (g.eqrow > 0) printf("== summary: equivalence counts pooled: predicate and EXACT %llu ; predicate, not EXACT %llu ; EXACT, not predicate %llu\n", (unsigned long long)tot.cnt[CN_EQ_EX], (unsigned long long)tot.cnt[CN_EQ_NEX], (unsigned long long)tot.cnt[CN_NEQ_EX]);
  }
  if (tl_w16on) { extern u64 tl_w16_N[64], tl_w16_EX[64], tl_w16_FALSE, tl_w16_EXN, tl_w16_HLOST; extern u64 tl_death[64][TL_NR][4]; extern void tl_w16_hist_dump(FILE *);
    for (int k = 0; k < 64; k++) if (tl_w16_N[k]) printf("W16MASK %02x N %llu EXACT %llu\n", k, (unsigned long long)tl_w16_N[k], (unsigned long long)tl_w16_EX[k]);
    printf("W16HASH exact samples hashed independently %llu, false collisions %llu, hist slots lost %llu\n", (unsigned long long)tl_w16_EXN, (unsigned long long)tl_w16_FALSE, (unsigned long long)tl_w16_HLOST);
    for (int k = 0; k < 64; k++) for (int t = 0; t < TL_NR; t++) for (int d = 0; d < 4; d++) if (tl_death[k][t][d]) printf("DEATH mask %02x row %d kind %c n %llu\n", k, t, "AEWl"[d], (unsigned long long)tl_death[k][t][d]);
    { extern u64 tl_cne[64][TL_NR]; for (int k = 0; k < 64; k++) for (int t = 0; t < TL_NR; t++) if (tl_cne[k][t]) printf("CNE mask %02x firstW %d n %llu\n", k, t, (unsigned long long)tl_cne[k][t]); }
    { extern u64 tl_stg[64][TL_NR][2]; for (int k = 0; k < 64; k++) for (int t = 0; t < TL_NR; t++) if (tl_stg[k][t][0]) printf("STG mask %02x row %d prop %llu acc %llu\n", k, t, (unsigned long long)tl_stg[k][t][0], (unsigned long long)tl_stg[k][t][1]); }
    tl_w16_hist_dump(stdout); }
  if (tl_d174on) { extern u64 tl_d174_mask[1u << 13];
    printf("D174 co-failure masks (bit 0..8 E17 bits 30,23,22,18,17,12,9,5,4; bit 9..11 E17 x2; bit 12 A15[29]=A17[29])\n");
    for (int k = 0; k < (1 << 13); k++) if (tl_d174_mask[k]) printf("D174MASK %04x n %llu\n", k, (unsigned long long)tl_d174_mask[k]);
  }
  if (ns > 1) {
    printf("== pooled over %d seeds: samples %llu\n", ns, (unsigned long long)tot.cnt[CN_N]);
    for (int k = 0; k < g.nc; k++) printf("   %-14s %llu (with exact %llu)\n", g.C[k]->name, (unsigned long long)tot.cnt[CN_EV0 + k], (unsigned long long)tot.cnt[CN_JOINT0 + k]);
    printf("   EXACT          %llu\n", (unsigned long long)tot.cnt[CN_EXACT]);
    double m = 0, v = 0; for (int i = 0; i < nr; i++) m += rs[i]; m /= nr; for (int i = 0; i < nr; i++) v += (rs[i] - m) * (rs[i] - m); v = nr > 1 ? v / (nr - 1) : 0;
    printf("   EXACT/%s pooled %.5f ; per-seed mean %.5f, seed-to-seed sd %.5f, 95%% of the mean +- %.5f\n", g.C[0]->name, (double)tot.cnt[CN_EXACT] / (double)tot.cnt[CN_EV0], m, sqrt(v), nr > 1 ? 1.96 * sqrt(v / nr) : NAN);
    for (int k = 1; k < g.nc; k++) printf("   %s/%s pooled %.5f\n", g.C[k]->name, g.C[0]->name, (double)tot.cnt[CN_EV0 + k] / (double)tot.cnt[CN_EV0]);
  }
  if (tl_prefix_marg_on) {
    printf("PREFIX_MARGINALS (prefix-stage proposals; diagnostic only)\n");
    for (int k = 0; k < 10; k++) {
      u64 p = tl_prefix_marg_props[k], h = tl_prefix_marg_hits[k];
      double q = p ? (double)h / (double)p : 0.0;
      printf("PREFMARG %-3s row %d props %llu hits %llu rate %.12e log2 %.9f\n",
             tl_prefix_marg_name[k], tl_prefix_marg_row[k], (unsigned long long)p,
             (unsigned long long)h, q, q > 0.0 ? log2(q) : -INFINITY);
    }
    for (int k = 0; k < 2; k++) {
      u64 p = tl_prefix_w78_props[k], h = tl_prefix_w78_hits[k];
      double q = p ? (double)h / (double)p : 0.0;
      printf("PREFMARG W%d row %d final-props %llu hits %llu rate %.12e log2 %.9f\n",
             7 + k, 7 + k, (unsigned long long)p, (unsigned long long)h,
             q, q > 0.0 ? log2(q) : -INFINITY);
    }
  }
  return 0;
}

/* ------------------------------------------------------------------ exact */
static u32 dep32(u64 idx, u32 mask);
static void print_exact(const TLExactCfg *g, const TLExactRes *r, const char *tag) {
  printf("%s enumerated %llu, members %llu, y-anchor inconsistent %llu\n", tag, (unsigned long long)r->total, (unsigned long long)r->c[EX_MEMBER], (unsigned long long)r->c[EX_INCONS]);
  printf("%s   prefix rows (< %d) hold: %llu\n", tag, g->a, (unsigned long long)r->c[EX_PRE]);
  printf("%s   EXACT (%s): %llu ; with prefix %llu\n", tag, g->event ? "zero output difference" : "zero state after row b", (unsigned long long)r->c[EX_EXACT], (unsigned long long)r->c[EX_PEXACT]);
  for (int k = 0; k < g->nc; k++) printf("%s   %-14s rows %d..%d: %llu ; with prefix %llu ; with prefix and exact %llu\n", tag, g->C[k]->name, g->a, g->b, (unsigned long long)r->c[EX_EV0 + k], (unsigned long long)r->c[EX_PEV0 + k], (unsigned long long)r->c[EX_PXEV0 + k]);
  if (r->c[EX_PEV0]) printf("%s   ratio (prefix and exact) / (prefix and %s) = %.6f\n", tag, g->C[0]->name, (double)r->c[EX_PEXACT] / (double)r->c[EX_PEV0]);
  if (r->hist) {
    u64 n1 = g->sp[0].n, dom = n1 * (g->nsp > 1 ? g->sp[1].n : 1); long nz = 0;
    for (u64 id = 0; id < dom; id++) nz += r->hist[id] != 0;
    printf("%s   enumerated values passing the prefix and %s: %ld distinct\n", tag, g->C[g->hist - 1]->name, nz);
    for (u64 id = 0; id < dom; id++) if (r->hist[id]) {
      printf("%s     ", tag);
      for (int s = 0; s < g->nsp; s++) { const TLEnumSpec *e = &g->sp[s]; u64 ix = s ? id / n1 : id % n1;
        if (e->kind == ES_MASK) printf("%s%d bits %08x  ", tl_kname(e->k), e->row, dep32(ix, e->mask));
        else printf("%s%d index %llu  ", tl_kname(e->k), e->row, (unsigned long long)ix); }
      printf(": %llu\n", (unsigned long long)r->hist[id]);
    }
  }
}
static int cmd_exact(void) {
  TLModel *M = load_model(); TLExactCfg g; memset(&g, 0, sizeof g);
  const char *b2; const char *a1 = opt2("--rows", &b2); if (!a1) { fprintf(stderr, "--rows A B\n"); return 2; }
  g.a = atoi(a1); g.b = atoi(b2); const char *ev = opt("--event", "out"); g.event = !strcmp(ev, "out");
  const char *sp[2]; g.nsp = optall("--enum", sp, 2); if (!g.nsp) { fprintf(stderr, "--enum SPEC\n"); return 2; }
  for (int i = 0; i < g.nsp; i++) if (tl_spec_parse(M, sp[i], &g.sp[i])) { fprintf(stderr, "bad --enum %s\n", sp[i]); return 2; }
  static TLConds st_pre, st_rel[TL_MAXREL]; g.pre = prefix_conds(M, &st_pre);
  g.C[0] = &M->base; g.nc = 1 + collect_relax(M, &M->base, g.C + 1, st_rel);
  if (opt("--hist", NULL)) { for (int k = 0; k < g.nc; k++) if (!strcmp(g.C[k]->name, opt("--hist", ""))) g.hist = k + 1; if (!g.hist) { fprintf(stderr, "--hist NAME: cells or a relaxation given with --relax\n"); return 2; } }
  print_model(M);
  printf("EXACT rows %d..%d event=%s enum %s%s%s (%llu x %llu values)\n", g.a, g.b, ev, sp[0], g.nsp > 1 ? " x " : "", g.nsp > 1 ? sp[1] : "", (unsigned long long)g.sp[0].n, (unsigned long long)(g.nsp > 1 ? g.sp[1].n : 1));
  const char *base = opt("--base", "pub");
  if (!strcmp(base, "pub")) { TLExactRes r; double t0 = now(); tl_exact(M, &g, &M->pubc, &r); print_exact(&g, &r, "[pub]"); printf("[pub]   time %.1f s\n", now() - t0); return 0; }
  if (strcmp(base, "smc")) { fprintf(stderr, "--base pub|smc\n"); return 2; }
  int np = atoi(opt("--np", "256")), pick = atoi(opt("--pick", "4")); u64 seed = strtoull(opt("--seed", "1"), NULL, 10);
  int tmin = 64; for (int i = 0; i < g.nsp; i++) { int r = g.sp[i].k == KE ? g.sp[i].row : M->e1 + 1; if (r < tmin) tmin = r; }
  int a0 = tmin; if (a0 > g.a) a0 = g.a;
  printf("bases: SMC prefix to row %d (np %d, seed %llu), %d particles\n", a0 - 1, np, (unsigned long long)seed, pick);
  double l2; TLPart *P = tl_smc_prefix(M, g.pre, a0, np, atoi(opt("--m", "256")), atoi(opt("--mt2", "1024")), seed, &l2, 1);
  if (!P) return 1;
  TLExactRes sum; memset(&sum, 0, sizeof sum);
  for (int j = 0; j < pick; j++) { int idx = (int)((long)j * np / pick); TLExactRes r; char tag[32]; snprintf(tag, sizeof tag, "[base %d]", idx); double t0 = now();
    tl_exact(M, &g, &P[idx].c, &r); print_exact(&g, &r, tag); printf("%s   time %.1f s\n", tag, now() - t0);
    sum.total += r.total; for (int k = 0; k < EX_COUNT; k++) sum.c[k] += r.c[k];
    if (r.hist) { if (!sum.hist) sum.hist = calloc(r.total, 8); for (u64 i = 0; i < r.total; i++) sum.hist[i] += r.hist[i]; free(r.hist); } }
  print_exact(&g, &sum, "[sum]");
  return 0;
}

/* ------------------------------------------------------------------ sdiff / backward */
static int cmd_sdiff(void) {
  u32 D = (u32)strtoul(opt("--delta", "0"), NULL, 16); int maxhw = atoi(opt("--maxhw", "8")), lim = atoi(opt("--limit", "24"));
  const char *fn = opt("--func", NULL);
  if (!fn) { printf("SDIFF delta %08x\n", D); tl_print_bsd(D, maxhw, lim, 0, 0); return 0; }
  TLSdiffCfg g; memset(&g, 0, sizeof g); g.D = D; g.func = tl_fname(fn); if (g.func < 0) { fprintf(stderr, "--func id|s0|s1|S0|S1\n"); return 2; }
  g.T = (u32)strtoul(opt("--out", "0"), NULL, 16);
  if (opt("--xor", NULL)) { g.usexor = 1; g.xr = (u32)strtoul(opt("--xor", "0"), NULL, 16); }
  TLModel *M = NULL; TLCellCtx cc;
  if (opt("--cell", NULL)) { M = load_model(); int k, r; if (tl_parse_word(opt("--cell", ""), &k, &r) < 0) return 2; cc.M = M; cc.k = k; cc.row = r; g.cellok = tl_cellctx_ok; g.cellctx = &cc; }
  double t0 = now(); TLSdiffRes r; tl_sdiff_count(&g, &r, 1, lim);
  printf("SDIFF %s(x + %08x) - %s(x) = %08x%s: domain %llu, EXACT count %llu (2^%.4f)", fn, D, fn, g.T, g.usexor ? " with the XOR filter" : "", (unsigned long long)r.domain, (unsigned long long)r.exact, r.exact ? log2((double)r.exact) : -INFINITY);
  if (M) printf(", with %s's printed cell %llu (2^%.4f), ratio %.6f", opt("--cell", ""), (unsigned long long)r.cellexact, r.cellexact ? log2((double)r.cellexact) : -INFINITY, r.cellexact ? (double)r.exact / r.cellexact : INFINITY);
  printf(" [%.1f s]\n", now() - t0);
  return 0;
}
static int cmd_backward(void) {
  TLModel *M = load_model(); const char *b2; const char *a1 = opt2("--rows", &b2); if (!a1) { fprintf(stderr, "--rows B0 B1\n"); return 2; }
  return tl_backward(M, atoi(a1), atoi(b2), atoi(opt("--maxhw", "6")), !has("--noenum"));
}

/* ------------------------------------------------------------------ flip (word level: what flipping value bits of an expanded word does downstream) */
static u32 dep32(u64 idx, u32 mask) { u32 r = 0; for (int b = 0; b < 32; b++) if ((mask >> b) & 1) { if (idx & 1) r |= 1u << b; idx >>= 1; } return r; }
static int cmd_flip(void) {
  TLModel *M = load_model(); int k, t;
  if (tl_parse_word(opt("--word", "W22"), &k, &t) < 0 || k != KW || t < 16 || t >= M->nr) { fprintf(stderr, "--word W<t>, 16 <= t < steps\n"); return 2; }
  u32 mask = (u32)strtoul(opt("--mask", "0"), NULL, 16); const TLTr *X = &M->pub.x, *Y = &M->pub.y;
  if (!mask || ((X->w[t] ^ Y->w[t]) & mask)) { fprintf(stderr, "--mask must be nonzero and on bits where W%d has no difference\n", t); return 2; }
  int nb = __builtin_popcount(mask), bl[32], n = 0; for (int b = 0; b < 32; b++) if ((mask >> b) & 1) bl[n++] = b;
  printf("FLIP %s W%d bits (", M->name, t); for (int i = 0; i < nb; i++) printf("%s%d", i ? "," : "", bl[i]);
  printf(") set to every pattern in BOTH members of the published pair; W%d..W%d re-expanded from it (words < W%d unchanged; word-level test)\n", t + 1, M->nr - 1, t);
  printf("  published W%dx %08x, dW%d %08x (xor %08x); published dW%d %08x\n", t, X->w[t], t, Y->w[t] - X->w[t], X->w[t] ^ Y->w[t], t + 2, t + 2 < M->nr ? Y->w[t + 2] - X->w[t + 2] : 0);
  int keep = 0, pubp = -1;
  for (u64 p = 0; p < (1ull << nb); p++) {
    TLTr x = *X, y = *Y; u32 v = dep32(p, mask); x.w[t] = (X->w[t] & ~mask) | v; y.w[t] = (Y->w[t] & ~mask) | v;
    for (int u = t + 1; u < M->nr; u++) { x.w[u] = ss1(x.w[u - 2]) + x.w[u - 7] + ss0(x.w[u - 15]) + x.w[u - 16]; y.w[u] = ss1(y.w[u - 2]) + y.w[u - 7] + ss0(y.w[u - 15]) + y.w[u - 16]; }
    int first = -1; for (int u = t + 1; u < M->nr; u++) if (y.w[u] - x.w[u] != Y->w[u] - X->w[u]) { first = u; break; }
    char pat[33]; for (int i = 0; i < nb; i++) pat[i] = (char)('0' + ((v >> bl[i]) & 1)); pat[nb] = 0;
    int isp = v == (X->w[t] & mask); if (isp) pubp = (int)p; keep += first < 0;
    printf("  pattern %s: ds1(W%d) %08x", pat, t, ss1(y.w[t]) - ss1(x.w[t]));
    if (t + 2 < M->nr) printf("  dW%d %08x (xor %08x)", t + 2, y.w[t + 2] - x.w[t + 2], x.w[t + 2] ^ y.w[t + 2]);
    printf("  %s%s\n", first < 0 ? "every later modular dW as published" : "", isp ? "   <- published" : "");
    if (first >= 0) printf("      first later word with a different modular difference: W%d (%08x, published %08x)\n", first, y.w[first] - x.w[first], Y->w[first] - X->w[first]);
  }
  printf("FLIP result: %d of %d patterns keep every later modular difference%s\n", keep, 1 << nb, (keep == 1 && pubp >= 0) ? " (only the published pattern)" : "");
  return 0;
}

/* ------------------------------------------------------------------ rowtable: the row-T table over a listed free word (exact) */
typedef struct { const TLModel *M; int T, over; long nv, nblk; const u32 *vals; u32 fm, fv; TLPair *bp; int *bok; u64 *perv; u32 *uv[64]; long un[64], ucap[64]; } RTCtx;
static void w_rt(void *vctx, long i, int tid) {
  RTCtx *s = vctx; long vi = i / s->nblk, blk = i % s->nblk; if (!s->bok[vi]) return;
  TLPair q = s->bp[vi]; u32 fr = ~s->fm; u64 nfree = 1ull << __builtin_popcount(fr), lo = (u64)blk << 16, hi = lo + (1ull << 16); if (hi > nfree) hi = nfree;
  u64 c = 0;
  for (u64 id = lo; id < hi; id++) {
    u32 e = s->fv | dep32(id, fr); tl_edrive_row(s->M, &q, s->T, e);
    if (!tl_rowok(&s->M->base, &q, s->T)) continue;
    c++; u32 u = q.x.w[s->T] - ss1(q.x.w[s->T - 2]) - q.x.w[s->T - 7];
    if (s->un[tid] == s->ucap[tid]) { s->ucap[tid] = s->ucap[tid] ? 2 * s->ucap[tid] : 1 << 16; s->uv[tid] = realloc(s->uv[tid], s->ucap[tid] * 4); }
    s->uv[tid][s->un[tid]++] = u;
  }
  __atomic_fetch_add(&s->perv[vi], c, __ATOMIC_RELAXED);
}
static int cmpu32(const void *a, const void *b) { u32 x = *(const u32 *)a, y = *(const u32 *)b; return x < y ? -1 : x > y; }
static int cmd_rowtable(void) {
  TLModel *M = load_model(); int T = atoi(opt("--row", "16")), k, over;
  if (tl_parse_word(opt("--over", "W15"), &k, &over) < 0 || k != KW || over > 15 || M->var[over].type != V_LIST) { fprintf(stderr, "--over W<i> with a listed set\n"); return 2; }
  if (T != M->e0) { fprintf(stderr, "--row must be the first E-driven row %d\n", M->e0); return 2; }
  RTCtx s; memset(&s, 0, sizeof s); s.M = M; s.T = T; s.over = over; s.vals = M->var[over].vals; s.nv = M->var[over].nvals;
  s.fm = M->base.c[KE][T].m; s.fv = M->base.c[KE][T].v; s.nblk = (long)(((1ull << __builtin_popcount(~s.fm)) + 65535) >> 16);
  s.bp = calloc(s.nv, sizeof(TLPair)); s.bok = calloc(s.nv, sizeof(int)); s.perv = calloc(s.nv, 8);
  printf("ROWTABLE %s row %d over W%d (%ld values; published coordinates otherwise): E%dx runs over its %d free bits (the %d fixed x-bits imposed); u = W%dx - s1(W%dx) - W%dx\n",
    M->name, T, over, s.nv, T, 32 - __builtin_popcount(s.fm), __builtin_popcount(s.fm), T, T - 2, T - 7);
  for (long v = 0; v < s.nv; v++) { TLCoord c = M->pubc; c.wx[over] = s.vals[v]; int cons = tl_build(M, &c, &s.bp[v]);
    s.bok[v] = cons && tl_rowsok(&M->base, &s.bp[v], M->lorow, T - 1); }
  double t0 = now(); tl_parfor(s.nv * s.nblk, 1, w_rt, &s);
  long tot = 0, ne = 0, nok = 0; for (long v = 0; v < s.nv; v++) { tot += (long)s.perv[v]; ne += s.perv[v] > 0; nok += s.bok[v]; }
  for (long v = 0; v < s.nv; v++) printf("  W%d = %08x: prefix rows %d..%d %s, row-%d passes %llu\n", over, s.vals[v], M->lorow, T - 1, s.bok[v] ? "hold" : "FAIL", T, (unsigned long long)s.perv[v]);
  long n = 0; for (int i = 0; i < 64; i++) n += s.un[i]; u32 *all = malloc((n + 1) * 4); long o = 0;
  for (int i = 0; i < 64; i++) { if (s.un[i]) memcpy(all + o, s.uv[i], s.un[i] * 4); o += s.un[i]; free(s.uv[i]); }
  qsort(all, n, 4, cmpu32); long d = n ? 1 : 0; for (long i = 1; i < n; i++) d += all[i] != all[i - 1];
  printf("ROWTABLE result: %ld (u, W%d) pairs, %ld distinct u, %ld of %ld W%d values nonempty, prefix holds for %ld [EXACT, %.1f s]\n", tot, over, d, ne, s.nv, over, nok, now() - t0);
  return 0;
}

int main(int argc, char **argv) {
  ARGC = argc; ARGV = argv;
  if (argc < 2) { fprintf(stderr, "usage: traillab check|window|exact|sdiff|backward|varcount|flip|rowtable [options]  (see README.md)\n"); return 2; }
  tl_set_threads(atoi(opt("--threads", "6")));
  setvbuf(stdout, NULL, _IOLBF, 0);
  if (!strcmp(argv[1], "check")) return cmd_check();
  if (!strcmp(argv[1], "window")) return cmd_window();
  if (!strcmp(argv[1], "exact")) return cmd_exact();
  if (!strcmp(argv[1], "sdiff")) return cmd_sdiff();
  if (!strcmp(argv[1], "backward")) return cmd_backward();
  if (!strcmp(argv[1], "varcount")) return cmd_varcount();
  if (!strcmp(argv[1], "flip")) return cmd_flip();
  if (!strcmp(argv[1], "rowtable")) return cmd_rowtable();
  fprintf(stderr, "unknown command %s\n", argv[1]); return 2;
}
