/* traillab.c - library: characteristic files, consistent pairs, condition checks, variable sets, threads (our code). */
#define _GNU_SOURCE
#include "traillab.h"
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <pthread.h>

const u32 TL_K[64] = {
0x428a2f98,0x71374491,0xb5c0fbcf,0xe9b5dba5,0x3956c25b,0x59f111f1,0x923f82a4,0xab1c5ed5,0xd807aa98,0x12835b01,0x243185be,0x550c7dc3,
0x72be5d74,0x80deb1fe,0x9bdc06a7,0xc19bf174,0xe49b69c1,0xefbe4786,0x0fc19dc6,0x240ca1cc,0x2de92c6f,0x4a7484aa,0x5cb0a9dc,0x76f988da,
0x983e5152,0xa831c66d,0xb00327c8,0xbf597fc7,0xc6e00bf3,0xd5a79147,0x06ca6351,0x14292967,0x27b70a85,0x2e1b2138,0x4d2c6dfc,0x53380d13,
0x650a7354,0x766a0abb,0x81c2c92e,0x92722c85,0xa2bfe8a1,0xa81a664b,0xc24b8b70,0xc76c51a3,0xd192e819,0xd6990624,0xf40e3585,0x106aa070,
0x19a4c116,0x1e376c08,0x2748774c,0x34b0bcb5,0x391c0cb3,0x4ed8aa4a,0x5b9cca4f,0x682e6ff3,0x748f82ee,0x78a5636f,0x84c87814,0x8cc70208,
0x90befffa,0xa4506ceb,0xbef9a3f7,0xc67178f2};

/* ------------------------------------------------------------------ SHA-256 pieces */
void tl_step(TLTr *t, int i) {
  u32 e = TA(t, i - 4) + TE(t, i - 4) + BS1(TE(t, i - 1)) + CH(TE(t, i - 1), TE(t, i - 2), TE(t, i - 3)) + TL_K[i] + t->w[i];
  TE(t, i) = e;
  TA(t, i) = e - TA(t, i - 4) + BS0(TA(t, i - 1)) + MAJ(TA(t, i - 1), TA(t, i - 2), TA(t, i - 3));
}
void tl_unstep(TLTr *t, int i) {
  u32 a4 = TE(t, i) - TA(t, i) + BS0(TA(t, i - 1)) + MAJ(TA(t, i - 1), TA(t, i - 2), TA(t, i - 3));
  TA(t, i - 4) = a4;
  TE(t, i - 4) = TE(t, i) - a4 - BS1(TE(t, i - 1)) - CH(TE(t, i - 1), TE(t, i - 2), TE(t, i - 3)) - TL_K[i] - t->w[i];
}
void tl_expand(TLTr *t, int from, int nr) {
  for (int i = from < 16 ? 16 : from; i < nr; i++) t->w[i] = ss1(t->w[i - 2]) + t->w[i - 7] + ss0(t->w[i - 15]) + t->w[i - 16];
}
static void trace_fwd(TLTr *t, const u32 cv[8], const u32 w16[16], int nr) {
  for (int i = 0; i < 16; i++) t->w[i] = w16[i];
  tl_expand(t, 16, nr);
  for (int i = 0; i < 4; i++) { TA(t, -1 - i) = cv[i]; TE(t, -1 - i) = cv[4 + i]; }
  for (int i = 0; i < nr; i++) tl_step(t, i);
}
/* independent reference: textbook a..h registers */
void tl_compress_ref(const u32 cv[8], const u32 w16[16], int nr, u32 out[8]) {
  u32 W[64], a = cv[0], b = cv[1], c = cv[2], d = cv[3], e = cv[4], f = cv[5], g = cv[6], h = cv[7];
  for (int i = 0; i < 16; i++) W[i] = w16[i];
  for (int i = 16; i < 64; i++) W[i] = ss1(W[i - 2]) + W[i - 7] + ss0(W[i - 15]) + W[i - 16];
  for (int i = 0; i < nr; i++) {
    u32 t1 = h + BS1(e) + CH(e, f, g) + TL_K[i] + W[i], t2 = BS0(a) + MAJ(a, b, c);
    h = g; g = f; f = e; e = d + t1; d = c; c = b; b = a; a = t1 + t2;
  }
  out[0] = cv[0] + a; out[1] = cv[1] + b; out[2] = cv[2] + c; out[3] = cv[3] + d;
  out[4] = cv[4] + e; out[5] = cv[5] + f; out[6] = cv[6] + g; out[7] = cv[7] + h;
}
int tl_sha256_selftest(void) {
  static const u32 IV[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
  static const u32 ABC[8] = {0xba7816bf,0x8f01cfea,0x414140de,0x5dae2223,0xb00361a3,0x96177a9c,0xb410ff61,0xf20015ad};
  u32 m[16] = {0x61626380}; m[15] = 24; u32 o[8]; tl_compress_ref(IV, m, 64, o);
  int bad = memcmp(o, ABC, 32) != 0;
  /* the A/E trace must agree with the reference on random inputs for every step count */
  TLRng r = tl_rng(1, 2, 3, 4);
  for (int it = 0; it < 2000; it++) {
    u32 cv[8], w[16]; for (int i = 0; i < 8; i++) cv[i] = tl_r32(&r); for (int i = 0; i < 16; i++) w[i] = tl_r32(&r);
    int nr = 16 + (int)tl_below(&r, 49); TLTr t; trace_fwd(&t, cv, w, nr); u32 ref[8]; tl_compress_ref(cv, w, nr, ref);
    u32 f[8] = {TA(&t, nr - 1), TA(&t, nr - 2), TA(&t, nr - 3), TA(&t, nr - 4), TE(&t, nr - 1), TE(&t, nr - 2), TE(&t, nr - 3), TE(&t, nr - 4)};
    for (int i = 0; i < 8; i++) if (cv[i] + f[i] != ref[i]) bad++;
    /* unstep inverts step */
    TLTr u = t; for (int i = nr - 1; i >= 4; i--) tl_unstep(&u, i);
    for (int i = -4; i < nr; i++) if (TA(&u, i) != TA(&t, i) || TE(&u, i) != TE(&t, i)) { bad++; break; }
  }
  return bad;
}

/* ------------------------------------------------------------------ names and functions */
const char *tl_kname(int k) { return k == KA ? "A" : k == KE ? "E" : "W"; }
int tl_parse_word(const char *s, int *k, int *row) {
  while (*s == ' ') s++;
  if (*s == 'A') *k = KA; else if (*s == 'E') *k = KE; else if (*s == 'W') *k = KW; else return -1;
  char *end; long r = strtol(s + 1, &end, 10); if (end == s + 1 || r < 0 || r >= TL_NR) return -1; *row = (int)r; return (int)(end - s);
}
u32 tl_fn(int f, u32 x) { switch (f) { case F_s0: return ss0(x); case F_s1: return ss1(x); case F_S0: return BS0(x); case F_S1: return BS1(x); default: return x; } }
int tl_fname(const char *s) {
  if (!strcmp(s, "id")) return F_ID; if (!strcmp(s, "s0")) return F_s0; if (!strcmp(s, "s1")) return F_s1;
  if (!strcmp(s, "S0")) return F_S0; if (!strcmp(s, "S1")) return F_S1; return -1;
}
u32 tl_word_mod(const TLCell *c) {
  u32 d = 0; for (int b = 0; b < 32; b++) if ((c->d >> b) & 1) { if ((c->v >> b) & 1) d -= 1u << b; else d += 1u << b; }
  return d;
}

/* ------------------------------------------------------------------ conditions */
void tl_conds_index(TLConds *C) {
  memset(C->nlrow, 0, sizeof C->nlrow);
  for (int i = 0; i < C->nlin; i++) {
    TLLin *l = &C->lin[i]; int r = -1; for (int j = 0; j < l->nt; j++) if (l->r[j] > r) r = l->r[j];
    l->row = r; if (r < 0 || r >= TL_NR) continue;
    if (C->nlrow[r] >= 64) { fprintf(stderr, "too many two-bit conditions at row %d\n", r); exit(2); }
    C->lrow[r][C->nlrow[r]++] = (short)i;
  }
}
static inline u32 gv(const TLTr *t, int k, int r) { return k == KA ? TA(t, r) : k == KE ? TE(t, r) : t->w[r]; }
int tl_rowok(const TLConds *C, const TLPair *p, int t) {
  for (int k = 0; k < 3; k++) {
    const TLCell *c = &C->c[k][t]; u32 x = gv(&p->x, k, t), y = gv(&p->y, k, t);
    if ((x & c->m) != c->v || ((x ^ y) & c->dm) != c->d) return 0;
    if (c->q && ((x ^ gv(&p->x, k, t - 1)) & c->q)) return 0;
  }
  for (int j = 0; j < C->nlrow[t]; j++) {
    const TLLin *l = &C->lin[C->lrow[t][j]]; u32 s = 0;
    for (int i = 0; i < l->nt; i++) s ^= gv(&p->x, l->k[i], l->r[i]) >> l->b[i];
    if ((s & 1u) != (u32)l->c) return 0;
  }
  return 1;
}
int tl_rowsok(const TLConds *C, const TLPair *p, int lo, int hi) {
  if (lo < 0) lo = 0;
  for (int t = lo; t <= hi; t++) if (!tl_rowok(C, p, t)) return 0;
  return 1;
}
int tl_row_fail(const TLConds *C, const TLPair *p, int t, char *why, int n) {
  int bad = 0; why[0] = 0;
  for (int k = 0; k < 3; k++) {
    const TLCell *c = &C->c[k][t]; u32 x = gv(&p->x, k, t), y = gv(&p->y, k, t);
    u32 bv = (x & c->m) ^ c->v, bd = ((x ^ y) & c->dm) ^ c->d, bq = c->q ? ((x ^ gv(&p->x, k, t - 1)) & c->q) : 0;
    if (bv | bd | bq) { bad++; int L = (int)strlen(why); snprintf(why + L, n - L, " %s%d[val %08x xor %08x plus %08x]", tl_kname(k), t, bv, bd, bq); }
  }
  for (int j = 0; j < C->nlrow[t]; j++) {
    const TLLin *l = &C->lin[C->lrow[t][j]]; u32 s = 0;
    for (int i = 0; i < l->nt; i++) s ^= gv(&p->x, l->k[i], l->r[i]) >> l->b[i];
    if ((s & 1u) != (u32)l->c) { bad++; int L = (int)strlen(why); snprintf(why + L, n - L, " lin#%d(", (int)C->lrow[t][j]);
      for (int i = 0; i < l->nt; i++) { L = (int)strlen(why); snprintf(why + L, n - L, "%s%s%d[%d]", i ? "^" : "", tl_kname(l->k[i]), l->r[i], l->b[i]); }
      L = (int)strlen(why); snprintf(why + L, n - L, "=%d)", l->c); }
  }
  return bad;
}
int tl_state_eq(const TLPair *p, int b) {
  for (int i = b - 3; i <= b; i++) if (TA(&p->x, i) != TA(&p->y, i) || TE(&p->x, i) != TE(&p->y, i)) return 0;
  return 1;
}

/* ------------------------------------------------------------------ cell strings and lins */
static int parse_cellstr(TLCell *c, const char *s) {
  if ((int)strlen(s) != 32) return -1;
  memset(c, 0, sizeof *c);
  for (int i = 0; i < 32; i++) {
    u32 bit = 1u << (31 - i);
    switch (s[i]) {
      case '=': case '-': c->dm |= bit; break;
      case '0': c->m |= bit; c->dm |= bit; break;
      case '1': c->m |= bit; c->v |= bit; c->dm |= bit; break;
      case 'u': c->m |= bit; c->v |= bit; c->dm |= bit; c->d |= bit; break;
      case 'n': c->m |= bit; c->dm |= bit; c->d |= bit; break;
      case 'x': c->dm |= bit; c->d |= bit; break;
      case '+': c->dm |= bit; c->p |= bit; break;
      case '?': break;
      default: return -1;
    }
  }
  return 0;
}
static void derive_q(TLConds *C) {
  for (int k = 0; k < 3; k++) for (int t = 0; t < TL_NR; t++) C->c[k][t].q = t > 0 ? (C->c[k][t].p & C->c[k][t - 1].p) : 0;
}
/* "E18[1]^E18[11]=0" or "A15[29] = A17[29]" / "!=" */
static int parse_term(const char **ps, int *k, int *r, int *b) {
  const char *s = *ps; while (*s == ' ') s++;
  int n = tl_parse_word(s, k, r); if (n < 0) return -1; s += n;
  if (*s != '[') return -1; char *e; long bb = strtol(s + 1, &e, 10); if (*e != ']' || bb < 0 || bb > 31) return -1;
  *b = (int)bb; *ps = e + 1; return 0;
}
static int parse_lin(const char *s, TLLin *l) {
  memset(l, 0, sizeof *l);
  for (;;) {
    int k, r, b; if (parse_term(&s, &k, &r, &b)) return -1;
    if (l->nt >= 6) return -1; l->k[l->nt] = (signed char)k; l->r[l->nt] = (short)r; l->b[l->nt] = (signed char)b; l->nt++;
    while (*s == ' ') s++;
    if (*s == '^') { s++; continue; }
    if (s[0] == '!' && s[1] == '=') { s += 2; while (*s == ' ') s++;
      if (*s == 'A' || *s == 'E' || *s == 'W') { if (parse_term(&s, &k, &r, &b)) return -1; l->k[l->nt] = (signed char)k; l->r[l->nt] = (short)r; l->b[l->nt] = (signed char)b; l->nt++; l->c = 1; return 0; }
      l->c = 1 ^ (int)strtol(s, NULL, 10); return 0; }
    if (*s == '=') { s++; while (*s == ' ') s++;
      if (*s == 'A' || *s == 'E' || *s == 'W') { if (parse_term(&s, &k, &r, &b)) return -1; l->k[l->nt] = (signed char)k; l->r[l->nt] = (short)r; l->b[l->nt] = (signed char)b; l->nt++; l->c = 0; return 0; }
      l->c = (int)strtol(s, NULL, 10) & 1; return 0; }
    return -1;
  }
}
static int lin_touches(const TLLin *l, int k, int r) { for (int i = 0; i < l->nt; i++) if (l->k[i] == k && l->r[i] == r) return 1; return 0; }
static void drop_lins(TLConds *C, int k, int r) {
  int j = 0; for (int i = 0; i < C->nlin; i++) if (!lin_touches(&C->lin[i], k, r)) C->lin[j++] = C->lin[i]; C->nlin = j;
}
static int add_lin(TLConds *C, const TLLin *l) { if (C->nlin >= TL_MAXLIN) return -1; C->lin[C->nlin++] = *l; return 0; }

/* relaxation ops, ';'-separated:
   dropv K<r> mask | dropsign K<r> mask | dropx K<r> mask | droprow K<r> | dropx2 K<r> | dropq K<r> mask |
   lin <expr>=c | parity K<r>[b],K<r>[b],... | sym K<r> <32 symbols> | setv K<r> mask value */
int tl_relax_parse(const TLModel *M, const TLConds *from, const char *spec, TLConds *out, const char *name) {
  (void)M;
  if (out != from) *out = *from;
  snprintf(out->name, sizeof out->name, "%s", name);
  char *buf = strdup(spec), *save = NULL;
  for (char *op = strtok_r(buf, ";", &save); op; op = strtok_r(NULL, ";", &save)) {
    while (*op == ' ') op++;
    if (!*op) continue;
    char kw[32] = {0}; int n = 0; sscanf(op, "%31s%n", kw, &n); const char *arg = op + n; while (*arg == ' ') arg++;
    if (!strcmp(kw, "lin")) { TLLin l; if (parse_lin(arg, &l) || add_lin(out, &l)) { fprintf(stderr, "bad lin '%s'\n", arg); free(buf); return -1; } continue; }
    if (!strcmp(kw, "parity")) {
      int k0 = -1, r0 = 0, b0 = 0, v0 = 0; const char *s = arg;
      for (;;) {
        int k, r, b; if (parse_term(&s, &k, &r, &b)) { fprintf(stderr, "bad parity '%s'\n", arg); free(buf); return -1; }
        TLCell *c = &out->c[k][r];
        if (!((c->m >> b) & 1) || ((c->d >> b) & 1)) { fprintf(stderr, "parity: %s%d[%d] has no value-only condition\n", tl_kname(k), r, b); free(buf); return -1; }
        int v = (c->v >> b) & 1; c->m &= ~(1u << b); c->v &= ~(1u << b);
        if (k0 < 0) { k0 = k; r0 = r; b0 = b; v0 = v; }
        else { TLLin l; memset(&l, 0, sizeof l); l.nt = 2; l.k[0] = (signed char)k0; l.r[0] = (short)r0; l.b[0] = (signed char)b0; l.k[1] = (signed char)k; l.r[1] = (short)r; l.b[1] = (signed char)b; l.c = v0 ^ v; add_lin(out, &l); }
        while (*s == ' ') s++; if (*s == ',') { s++; continue; } break;
      }
      continue;
    }
    int k, r; int m = tl_parse_word(arg, &k, &r);
    if (m < 0) { fprintf(stderr, "relax op '%s': bad word\n", op); free(buf); return -1; }
    const char *rest = arg + m; while (*rest == ' ') rest++;
    TLCell *c = &out->c[k][r]; u32 mask = (u32)strtoul(rest, NULL, 16);
    if (!strcmp(kw, "dropv")) { u32 mm = mask & ~c->d; c->m &= ~mm; c->v &= c->m; }
    else if (!strcmp(kw, "dropsign")) { u32 mm = mask & c->d; c->m &= ~mm; c->v &= c->m; }
    else if (!strcmp(kw, "dropx")) { c->m &= ~mask; c->v &= c->m; c->dm &= ~mask; c->d &= c->dm; c->q &= ~mask; }
    else if (!strcmp(kw, "dropq")) { c->q &= ~mask; }
    else if (!strcmp(kw, "droprow")) { memset(c, 0, sizeof *c); drop_lins(out, k, r); if (r + 1 < TL_NR) out->c[k][r + 1].q = 0; }
    else if (!strcmp(kw, "dropx2")) { drop_lins(out, k, r); }
    else if (!strcmp(kw, "sym")) { TLCell nc; if (parse_cellstr(&nc, rest)) { fprintf(stderr, "sym: bad symbols\n"); free(buf); return -1; } nc.q = c->q; *c = nc; }
    else if (!strcmp(kw, "setv")) { char *e; u32 mk = (u32)strtoul(rest, &e, 16); u32 vv = (u32)strtoul(e, NULL, 16); c->m |= mk; c->v = (c->v & ~mk) | (vv & mk); }
    else { fprintf(stderr, "unknown relax op '%s'\n", kw); free(buf); return -1; }
  }
  free(buf); tl_conds_index(out); return 0;
}
const TLConds *tl_find_relax(const TLModel *M, const char *name) {
  for (int i = 0; i < M->nrelax; i++) if (!strcmp(M->relax[i].name, name)) return &M->relax[i];
  return NULL;
}

/* ------------------------------------------------------------------ variables */
int tl_word_cellok(const TLModel *M, int k, int row, u32 x, u32 y) {
  const TLCell *c = &M->full.c[k][row];
  if ((x & c->m) != c->v || ((x ^ y) & c->dm) != c->d) return 0;
  for (int i = 0; i < M->full.nlin; i++) {
    const TLLin *l = &M->full.lin[i]; int only = 1; for (int j = 0; j < l->nt; j++) if (l->k[j] != k || l->r[j] != row) only = 0;
    if (!only) continue; u32 s = 0; for (int j = 0; j < l->nt; j++) s ^= x >> l->b[j]; if ((s & 1u) != (u32)l->c) return 0;
  }
  return 1;
}
/* 'back': the word W_i moves E_{i-4} only (rows i-3..i are held); require E_{i-4}'s cell on both members */
static int back_ok(const TLModel *M, int i, u32 w) {
  const TLVar *v = &M->var[i]; u32 ex = v->bcx - w, ey = v->bcy - (w + M->dl[i]);
  const TLCell *c = &M->full.c[KE][i - 4];
  if ((ex & c->m) != c->v || ((ex ^ ey) & c->dm) != c->d) return 0;
  for (int j = 0; j < M->full.nlin; j++) {
    const TLLin *l = &M->full.lin[j]; int only = 1; for (int q = 0; q < l->nt; q++) if (l->k[q] != KE || l->r[q] != i - 4) only = 0;
    if (!only) continue; u32 s = 0; for (int q = 0; q < l->nt; q++) s ^= ex >> l->b[q]; if ((s & 1u) != (u32)l->c) return 0;
  }
  return 1;
}
int tl_var_member(const TLModel *M, int i, u32 w) {
  const TLVar *v = &M->var[i];
  if (v->back && !back_ok(M, i, w)) return 0;
  switch (v->type) {
    case V_FIXED: return w == M->mx[i];
    case V_RAND: return 1;
    case V_LIST: for (long j = 0; j < v->nvals; j++) if (v->vals[j] == w) return 1; return 0;
    case V_FSET: if ((u32)(tl_fn(v->func, w + M->dl[i]) - tl_fn(v->func, w)) != v->T) return 0;
      return v->cell ? tl_word_cellok(M, KW, i, w, w + M->dl[i]) : 1;
    case V_CELL: return tl_word_cellok(M, KW, i, w, w + M->dl[i]);
  }
  return 0;
}
u32 tl_draw_var(const TLModel *M, int i, TLRng *r) {
  const TLVar *v = &M->var[i];
  switch (v->type) {
    case V_FIXED: return M->mx[i];
    case V_RAND: return tl_r32(r);
    case V_LIST: return v->vals[tl_below(r, (u64)v->nvals)];
    default: {
      const TLCell *c = &M->full.c[KW][i]; int forced = (v->type == V_CELL || v->cell);
      for (long it = 0; it < (1L << 34); it++) {
        u32 w = tl_r32(r); if (forced) w = (w & ~c->m) | c->v;
        if (tl_var_member(M, i, w)) return w;
      }
      fprintf(stderr, "variable W%d: no member found\n", i); exit(3);
    }
  }
}
void tl_draw_vars(const TLModel *M, TLCoord *c, TLRng *r, int late) {
  for (int i = 0; i < 16; i++) if (M->var[i].type != V_FIXED && M->var[i].late == late) c->wx[i] = tl_draw_var(M, i, r);
}

/* ------------------------------------------------------------------ building pairs */
void tl_edrive_row(const TLModel *M, TLPair *p, int t, u32 ex) {
  TLTr *x = &p->x, *y = &p->y;
  u32 rest = TA(x, t - 4) + TE(x, t - 4) + BS1(TE(x, t - 1)) + CH(TE(x, t - 1), TE(x, t - 2), TE(x, t - 3)) + TL_K[t];
  x->w[t] = ex - rest;
  TE(x, t) = ex; TA(x, t) = ex - TA(x, t - 4) + BS0(TA(x, t - 1)) + MAJ(TA(x, t - 1), TA(x, t - 2), TA(x, t - 3));
  /* y word: the real expansion, written as x word + member differences (W_{t-16} and, for t-15<=5, W_{t-15} have no difference) */
  u32 d = (ss1(y->w[t - 2]) - ss1(x->w[t - 2])) + (y->w[t - 7] - x->w[t - 7]) + M->dl[t - 16];
  if (t - 15 >= 0) d += ss0(y->w[t - 15]) - ss0(x->w[t - 15]);
  y->w[t] = x->w[t] + d;
  tl_step(y, t);
}
static void solve_low_words(const TLModel *M, TLTr *x) {
  for (int t = M->e1; t >= M->e0; t--) x->w[t - 16] = x->w[t] - ss1(x->w[t - 2]) - x->w[t - 7] - ss0(x->w[t - 15]);
}
/* full rebuild from the free coordinates. x: anchored rows + forward + E-driven + backward to the CV; y: forward from that CV.
   returns 1 when the y member reproduces its anchored rows (the model's consistency), else 0. */
int tl_build(const TLModel *M, const TLCoord *c, TLPair *p) {
  TLTr *x = &p->x, *y = &p->y; int K = M->anchor, nr = M->nr;
  for (int i = 0; i < 16; i++) x->w[i] = c->wx[i];
  if (K >= 0) {
    for (int i = K - 3; i <= K; i++) { TA(x, i) = TA(&M->pub.x, i); TE(x, i) = TE(&M->pub.x, i); }
    for (int t = K + 1; t < 16 && t < nr; t++) tl_step(x, t);
    int next = 16;
    if (M->e0 >= 0) {
      for (int t = 16; t < M->e0; t++) { x->w[t] = tl_wnext(M, x, 0, t); tl_step(x, t); }
      for (int t = M->e0; t <= M->e1; t++) {
        u32 rest = TA(x, t - 4) + TE(x, t - 4) + BS1(TE(x, t - 1)) + CH(TE(x, t - 1), TE(x, t - 2), TE(x, t - 3)) + TL_K[t];
        x->w[t] = c->ex[t] - rest; tl_step(x, t);
      }
      solve_low_words(M, x);
      next = M->e1 + 1;
    }
    for (int t = next; t < nr; t++) { x->w[t] = tl_wnext(M, x, 0, t); tl_step(x, t); }
    for (int t = K; t >= 0; t--) tl_unstep(x, t);
  } else {
    u32 w16[16]; memcpy(w16, c->wx, sizeof w16); trace_fwd(x, M->cv, w16, nr);
  }
  u32 cv[8]; for (int i = 0; i < 4; i++) { cv[i] = TA(x, -1 - i); cv[4 + i] = TE(x, -1 - i); }
  u32 wy[16]; for (int i = 0; i < 16; i++) wy[i] = x->w[i] + M->dl[i];
  for (int i = 0; i < 16; i++) y->w[i] = wy[i];
  for (int i = 16; i < nr; i++) y->w[i] = tl_wnext(M, y, 1, i);
  for (int i = 0; i < 4; i++) { TA(y, -1 - i) = cv[i]; TE(y, -1 - i) = cv[4 + i]; }
  for (int i = 0; i < nr; i++) tl_step(y, i);
  if (K < 0) return 1;
  for (int i = K - 3; i <= K; i++) if (TA(y, i) != TA(&M->pub.y, i) || TE(y, i) != TE(&M->pub.y, i)) return 0;
  return 1;
}
/* incremental: rows >= t recomputed (t >= e0); rows < t of p must be current. Does not solve W0..W5 / the CV. */
void tl_build_from(const TLModel *M, const TLCoord *c, TLPair *p, int t, int hi) {
  int nr = hi + 1 < M->nr ? hi + 1 : M->nr, s = t;
  if (M->e0 >= 0 && t <= M->e1) { int top = M->e1 < nr - 1 ? M->e1 : nr - 1; for (int u = t; u <= top; u++) tl_edrive_row(M, p, u, c->ex[u]); s = M->e1 + 1; }
  for (int u = s; u < nr; u++) {
    p->x.w[u] = tl_wnext(M, &p->x, 0, u);
    p->y.w[u] = tl_wnext(M, &p->y, 1, u);
    tl_step(&p->x, u); tl_step(&p->y, u);
  }
}

/* ------------------------------------------------------------------ loading */
static int hexlist(const char *s, u32 *out, int n) {
  int k = 0; while (k < n) { while (*s == ' ' || *s == '\t') s++; if (!isxdigit((unsigned char)*s)) break; char *e; out[k++] = (u32)strtoul(s, &e, 16); s = e; }
  return k;
}
static int load_listfile(const char *path, u32 **vals, long *n) {
  FILE *f = fopen(path, "r"); if (!f) { perror(path); return -1; }
  long cap = 1 << 16; *vals = malloc(cap * 4); *n = 0; char tok[64];
  while (fscanf(f, "%63s", tok) == 1) {
    if (strlen(tok) != 8) continue; int ok = 1; for (int i = 0; i < 8; i++) if (!isxdigit((unsigned char)tok[i])) ok = 0; if (!ok) continue;
    if (*n == cap) { cap *= 2; *vals = realloc(*vals, cap * 4); }
    (*vals)[(*n)++] = (u32)strtoul(tok, NULL, 16);
  }
  fclose(f); return 0;
}
static int parse_var(TLModel *M, const char *line) {
  int k, i; int n = tl_parse_word(line, &k, &i);
  if (n < 0 || k != KW || i > 15) { fprintf(stderr, "var: need W0..W15: %s\n", line); return -1; }
  const char *s = line + n; char kind[32] = {0}; int m = 0; sscanf(s, "%31s%n", kind, &m); s += m;
  TLVar *v = &M->var[i]; TLVar old = *v; memset(v, 0, sizeof *v);
  snprintf(v->desc, sizeof v->desc, "%.90s", line);
  { char *h = strchr(v->desc, '#'); if (h) *h = 0; }
  if (strstr(s, " late")) v->late = 1;
  if (strstr(s, " back")) {
    if (i < 4 || i > M->anchor) { fprintf(stderr, "back: needs 4 <= i <= anchor\n"); return -1; }
    v->back = 1; const TLTr *x = &M->pub.x, *y = &M->pub.y;
    v->bcx = TE(x, i) - TA(x, i - 4) - BS1(TE(x, i - 1)) - CH(TE(x, i - 1), TE(x, i - 2), TE(x, i - 3)) - TL_K[i];
    v->bcy = TE(y, i) - TA(y, i - 4) - BS1(TE(y, i - 1)) - CH(TE(y, i - 1), TE(y, i - 2), TE(y, i - 3)) - TL_K[i];
  }
  if (!strcmp(kind, "fixed")) v->type = V_FIXED;
  else if (!strcmp(kind, "rand")) v->type = V_RAND;
  else if (!strcmp(kind, "cell")) v->type = V_CELL;
  else if (!strcmp(kind, "fset") || !strcmp(kind, "cell+fset")) {
    v->type = V_FSET; v->cell = !strcmp(kind, "cell+fset");
    char fn[8] = {0}; u32 T; if (sscanf(s, "%7s %x", fn, &T) != 2 || (v->func = tl_fname(fn)) < 0) { fprintf(stderr, "fset: need func T: %s\n", line); return -1; }
    v->T = T;
  } else if (!strcmp(kind, "list")) {
    v->type = V_LIST; while (*s == ' ') s++;
    if (*s == '@') { char path[512]; sscanf(s + 1, "%511s", path); if (load_listfile(path, &v->vals, &v->nvals)) return -1; }
    else { v->vals = malloc(4096 * 4); v->nvals = hexlist(s, v->vals, 4096); }
    if (v->nvals < 1) { fprintf(stderr, "empty list: %s\n", line); return -1; }
  } else if (!strcmp(kind, "a0list")) {
    /* W_i from A_{i-8} values (A0-variants): W_i = W_iC - (a0 + C4), C4 = A_{i-4} - S0(A_{i-5}) - MAJ(A_{i-5},A_{i-6},A_{i-7}) */
    v->type = V_LIST; while (*s == ' ') s++; char path[512] = {0}; sscanf(s + (*s == '@'), "%511s", path);
    if (load_listfile(path, &v->vals, &v->nvals)) return -1;
    const TLTr *x = &M->pub.x;
    u32 C4 = TA(x, i - 4) - BS0(TA(x, i - 5)) - MAJ(TA(x, i - 5), TA(x, i - 6), TA(x, i - 7));
    u32 WC = TE(x, i) - TA(x, i - 4) - BS1(TE(x, i - 1)) - CH(TE(x, i - 1), TE(x, i - 2), TE(x, i - 3)) - TL_K[i];
    if (WC - (TA(x, i - 8) + C4) != M->mx[i]) { fprintf(stderr, "a0list: constant self-check failed for W%d\n", i); return -1; }
    for (long j = 0; j < v->nvals; j++) v->vals[j] = WC - (v->vals[j] + C4);
  } else { fprintf(stderr, "unknown var kind '%s'\n", kind); *v = old; return -1; }
  return 0;
}
int tl_load(const char *path, TLModel *M, const char *varoverride[], int nover) {
  FILE *f = fopen(path, "r"); if (!f) { perror(path); return -1; }
  memset(M, 0, sizeof *M); M->anchor = -1; M->e0 = M->e1 = -1;
  char *line = NULL; size_t cap = 0; int ln = 0, nv = 0;
  char *relax_lines[TL_MAXREL]; char relax_names[TL_MAXREL][48]; int nrl = 0;
  char *var_lines[64]; int nvl = 0;
  while (getline(&line, &cap, f) > 0) {
    ln++; char *h = strchr(line, '#'); if (h) *h = 0;
    char *s = line; while (*s == ' ' || *s == '\t') s++; size_t L = strlen(s); while (L && (s[L - 1] == '\n' || s[L - 1] == '\r' || s[L - 1] == ' ')) s[--L] = 0;
    if (!*s) continue;
    char kw[32] = {0}; int n = 0; sscanf(s, "%31s%n", kw, &n); char *a = s + n; while (*a == ' ') a++;
    if (!strcmp(kw, "name")) snprintf(M->name, sizeof M->name, "%s", a);
    else if (!strcmp(kw, "steps")) M->nr = atoi(a);
    else if (!strcmp(kw, "convention")) {}
    else if (!strcmp(kw, "cv")) nv += hexlist(a, M->cv, 8) == 8;
    else if (!strcmp(kw, "mx")) nv += hexlist(a, M->mx, 16) == 16;
    else if (!strcmp(kw, "my")) nv += hexlist(a, M->my, 16) == 16;
    else if (!strcmp(kw, "digest")) M->have_digest = hexlist(a, M->digest, 8) == 8;
    else if (!strcmp(kw, "row")) {
      int r; char sa[64], se[64], sw[64];
      if (sscanf(a, "%d %63s %63s %63s", &r, sa, se, sw) != 4 || r < 0 || r >= TL_NR ||
          parse_cellstr(&M->full.c[KA][r], sa) || parse_cellstr(&M->full.c[KE][r], se) || parse_cellstr(&M->full.c[KW][r], sw)) {
        fprintf(stderr, "%s:%d bad row line\n", path, ln); return -1; }
    }
    else if (!strcmp(kw, "x2") || !strcmp(kw, "lin")) { TLLin l; if (parse_lin(a, &l) || add_lin(&M->full, &l)) { fprintf(stderr, "%s:%d bad condition\n", path, ln); return -1; } }
    else if (!strcmp(kw, "anchor")) M->anchor = atoi(a);
    else if (!strcmp(kw, "elist")) { int r = atoi(a); char *q = a; while (*q && *q != ' ') q++; if (r < 16 || r >= TL_NR) return -1;
      M->elist[r] = malloc(4096 * 4); M->nelist[r] = hexlist(q, M->elist[r], 4096); if (M->nelist[r] < 1) { fprintf(stderr, "empty elist\n"); return -1; } }
    else if (!strcmp(kw, "edrive")) { if (sscanf(a, "%d %d", &M->e0, &M->e1) != 2) return -1; }
    else if (!strcmp(kw, "except")) { char *sv = NULL; for (char *t = strtok_r(a, " ", &sv); t; t = strtok_r(NULL, " ", &sv)) { int k, r; if (tl_parse_word(t, &k, &r) < 0 || k != KW || r > 15) { fprintf(stderr, "except: W0..W15\n"); return -1; } M->except[r] = 1; } }
    else if (!strcmp(kw, "var")) { if (nvl < 64) var_lines[nvl++] = strdup(a); }
    else if (!strcmp(kw, "relax")) { if (nrl < TL_MAXREL) { int m = 0; sscanf(a, "%47s%n", relax_names[nrl], &m); relax_lines[nrl++] = strdup(a + m); } }
    else { fprintf(stderr, "%s:%d unknown keyword '%s'\n", path, ln, kw); return -1; }
  }
  free(line); fclose(f);
  if (nv != 3 || M->nr < 17 || M->nr > TL_NR) { fprintf(stderr, "%s: need cv, mx, my and steps\n", path); return -1; }
  for (int i = 0; i < 16; i++) M->dl[i] = M->my[i] - M->mx[i];
  derive_q(&M->full); tl_conds_index(&M->full); snprintf(M->full.name, sizeof M->full.name, "full");
  M->base = M->full; snprintf(M->base.name, sizeof M->base.name, "cells");
  for (int i = 0; i < 16; i++) if (M->except[i]) { memset(&M->base.c[KW][i], 0, sizeof(TLCell)); drop_lins(&M->base, KW, i); }
  tl_conds_index(&M->base);
  /* published trace */
  trace_fwd(&M->pub.x, M->cv, M->mx, M->nr); trace_fwd(&M->pub.y, M->cv, M->my, M->nr);
  memcpy(M->pubc.wx, M->mx, sizeof M->pubc.wx);
  for (int t = 0; t < TL_NR; t++) M->pubc.ex[t] = t < M->nr ? TE(&M->pub.x, t) : 0;
  for (int i = 0; i < 16; i++) M->var[i].type = V_FIXED;
  for (int i = 0; i < nvl; i++) { if (parse_var(M, var_lines[i])) return -1; free(var_lines[i]); }
  for (int i = 0; i < nover; i++) if (parse_var(M, varoverride[i])) return -1;
  if (M->e0 >= 0) {
    if (M->e0 < 16 || M->e1 > 21 || M->e1 < M->e0 || M->anchor < 5) { fprintf(stderr, "edrive needs 16 <= e0 <= e1 <= 21 and anchor >= 5\n"); return -1; }
    for (int t = M->e0; t <= M->e1; t++) if (M->dl[t - 16] != 0 || M->var[t - 16].type != V_FIXED) { fprintf(stderr, "edrive: W%d must have no difference and no var\n", t - 16); return -1; }
  }
  for (int i = 0; i < 16; i++) if (M->var[i].type != V_FIXED && M->e0 >= 0 && i <= M->e1 - 16) { fprintf(stderr, "W%d is solved by edrive\n", i); return -1; }
  M->lorow = TL_NR;
  for (int t = 0; t < M->nr; t++) { int any = M->base.nlrow[t] > 0; for (int k = 0; k < 3; k++) { const TLCell *c = &M->base.c[k][t]; if (c->m || c->d || c->q) any = 1; } if (any && t < M->lorow) M->lorow = t; }
  for (int i = 0; i < nrl; i++) {
    if (tl_relax_parse(M, &M->base, relax_lines[i], &M->relax[M->nrelax], relax_names[i])) { fprintf(stderr, "relax %s\n", relax_names[i]); return -1; }
    M->nrelax++; free(relax_lines[i]);
  }
  return 0;
}

/* ------------------------------------------------------------------ threads */
static int NTHR = 6;
int tl_threads(void) { return NTHR; }
void tl_set_threads(int n) { NTHR = n < 1 ? 1 : n > 64 ? 64 : n; }
typedef struct { long n, chunk; void (*fn)(void *, long, int); void *ctx; long next; } PF;
typedef struct { PF *pf; int tid; } PFT;
static void *pf_run(void *arg) {
  PFT *t = arg; PF *pf = t->pf;
  for (;;) {
    long s = __atomic_fetch_add(&pf->next, pf->chunk, __ATOMIC_RELAXED);
    if (s >= pf->n) break; long e = s + pf->chunk; if (e > pf->n) e = pf->n;
    for (long i = s; i < e; i++) pf->fn(pf->ctx, i, t->tid);
  }
  return NULL;
}
void tl_parfor(long n, long chunk, void (*fn)(void *ctx, long i, int tid), void *ctx) {
  PF pf = {n, chunk < 1 ? 1 : chunk, fn, ctx, 0}; pthread_t th[64]; PFT a[64];
  for (int i = 0; i < NTHR; i++) { a[i].pf = &pf; a[i].tid = i; pthread_create(&th[i], NULL, pf_run, &a[i]); }
  for (int i = 0; i < NTHR; i++) pthread_join(th[i], NULL);
}

void tl_wilson(double k, double n, double *lo, double *hi) {
  if (n <= 0) { *lo = 0; *hi = 1; return; }
  double z = 1.96, p = k / n, d = 1 + z * z / n, c = p + z * z / (2 * n), w = z * sqrt(p * (1 - p) / n + z * z / (4 * n * n));
  *lo = (c - w) / d; *hi = (c + w) / d;
}
