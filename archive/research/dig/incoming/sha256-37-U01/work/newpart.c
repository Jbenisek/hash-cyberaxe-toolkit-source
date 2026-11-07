
/* ---- row Q2 scan (our code; reuses zoneD helpers unchanged) ---- */
static u32 pdep32(u32 src, u32 mask) { u32 r = 0; for (u32 m = mask; m; m &= m - 1) { if (src & 1) r |= m & -m; src >>= 1; } return r; }
static TLModel *M2;
static void dropbit(TLConds *C, int k, int r, int b) { TLCell *c = &C->c[k][r]; u32 m = ~(1u << b); c->m &= m; c->v &= m; c->dm &= m; c->d &= m; c->q &= m; c->p &= m; }
static void mkrow(TLPair *p, int r, u32 ex) {
  u32 restx = TA(&p->x, r - 4) + TE(&p->x, r - 4) + BS1(TE(&p->x, r - 1)) + CH(TE(&p->x, r - 1), TE(&p->x, r - 2), TE(&p->x, r - 3)) + TL_K[r];
  u32 resty = TA(&p->y, r - 4) + TE(&p->y, r - 4) + BS1(TE(&p->y, r - 1)) + CH(TE(&p->y, r - 1), TE(&p->y, r - 2), TE(&p->y, r - 3)) + TL_K[r];
  u32 wx = ex - restx, wy = wx + M->dl[r];
  p->x.w[r] = wx; p->y.w[r] = wy; TE(&p->x, r) = ex; TE(&p->y, r) = resty + wy;
  TA(&p->x, r) = ex - TA(&p->x, r - 4) + BS0(TA(&p->x, r - 1)) + MAJ(TA(&p->x, r - 1), TA(&p->x, r - 2), TA(&p->x, r - 3));
  TA(&p->y, r) = TE(&p->y, r) - TA(&p->y, r - 4) + BS0(TA(&p->y, r - 1)) + MAJ(TA(&p->y, r - 1), TA(&p->y, r - 2), TA(&p->y, r - 3));
}
/* enumerate E_r^x candidates (value bits fm/fv fixed), rows < r of base B held; count whole-row passes under C; store passing E values */
static long rowcount(const TLPair *B, int r, const TLConds *C, u32 fm, u32 fv, u32 *keep, long kcap) {
  u64 n = 1ull << (32 - __builtin_popcount(fm)); long ok = 0; TLPair p = *B;
  for (u64 j = 0; j < n; j++) {
    u32 ex = (fv & fm) | pdep32((u32)j, ~fm);
    mkrow(&p, r, ex);
    if (tl_rowok(C, &p, r)) { if (keep && ok < kcap) keep[ok] = ex; ok++; }
  }
  return ok;
}
/* consistent build with anchor row r replaced by pair row of q (both members); coordinates cc */
static int build_mod(const TLPair *q, int r, const TLCoord *cc, TLPair *out) {
  memcpy(M2, M, sizeof(TLModel));
  TA(&M2->pub.x, r) = TA(&q->x, r); TE(&M2->pub.x, r) = TE(&q->x, r); TA(&M2->pub.y, r) = TA(&q->y, r); TE(&M2->pub.y, r) = TE(&q->y, r);
  return tl_build(M2, cc, out);
}
static void fullpath(const TLPair *p, int cons, const TLPair *base, char *buf, int n) {
  int dm = diffpres(p, base, 15, 0), fm = rows_fail_mask(&M->base, p, 0, 15);
  int r1622 = tl_rowsok(&M->base, p, 16, 22), r2336 = tl_rowsok(&M->base, p, 23, 36), ex = tl_state_eq(p, 36);
  snprintf(buf, n, "cons%d dmod15=%d failmask<=15=%04x exp=%d r16-22=%d r23-36=%d EXACT=%d", cons, dm, fm, expdiff_ok(p), r1622, r2336, ex);
}
static void cmd_row(int r) {
  TLRng rg = tl_rng(2026, 10, 12, 14);
  PB[0] = P0; CB[0] = C0; nb = 1;
  for (int j = 0; j < 12 && nb < 6; j++) { TLCoord c = C0; c.wx[8] = tl_draw_var(M, 8, &rg); TLPair p; if (c.wx[8] != C0.wx[8] && valid15(&c, &p)) { PB[nb] = p; CB[nb] = c; nb++; } }
  M2 = malloc(sizeof(TLModel));
  const TLCell *ce = &M->full.c[KE][r];
  printf("ROW %d  bases=%d (P0 + A0-variants)\n", r, nb);
  for (int k = 0; k < 3; k++) { const TLCell *c = &M->full.c[k][r]; char s[40]; for (int b = 31; b >= 0; b--) s[31 - b] = sym(c, b); s[32] = 0; printf("%s%d %s\n", tl_kname(k), r, s); }
  printf("published pair rows 0..15 under base conds: %s; EXACT %d\n", tl_rowsok(&M->base, &P0, 0, 15) ? "ok" : "FAIL", tl_state_eq(&P0, 36));
  { TLPair q; int cons = build_mod(&P0, r, &C0, &q); char buf[200]; fullpath(&q, cons, &P0, buf, sizeof buf); printf("VALIDATE unmodified-anchor rebuild: %s identical-w:%d\n", buf, !memcmp(q.x.w, P0.x.w, 37 * 4)); }
  u32 fm0 = ce->m, fv0 = ce->v; long base_cnt[6];
  for (int i = 0; i < nb; i++) base_cnt[i] = rowcount(&PB[i], r, &M->base, fm0, fv0, NULL, 0);
  printf("BASELINE whole-row %d count (E candidates 2^%d, all printed conditions):", r, 32 - __builtin_popcount(fm0)); for (int i = 0; i < nb; i++) printf(" %ld", base_cnt[i]); printf("\n");
  int items[80][2]; int ni = 0;
  if (r == 14) {
    int ab[] = {15, 23, 25}, eb[] = {1,2,3,4,6,7,8,9,10,11,12,15,18,19,20,21,22,23,24,25,26,27,29}, wb[] = {1,3,9,11,13,18,20,22,26,30};
    for (int i = 0; i < 3; i++) { items[ni][0] = KA; items[ni++][1] = ab[i]; }
    for (int i = 0; i < 23; i++) { items[ni][0] = KE; items[ni++][1] = eb[i]; }
    for (int i = 0; i < 10; i++) { items[ni][0] = KW; items[ni++][1] = wb[i]; }
    items[ni][0] = KE; items[ni++][1] = 30; items[ni][0] = KE; items[ni++][1] = 17;
  } else { int bs[] = {30, 29, 21, 16, 11, 4, 25, 13, 5}; for (int i = 0; i < 9; i++) { items[ni][0] = KA; items[ni++][1] = bs[i]; } for (int b = 0; b < 32; b += 5) { items[ni][0] = KE; items[ni++][1] = b; } }
  TLConds *CD = malloc(sizeof(TLConds));
  for (int it = 0; it < ni; it++) {
    int k = items[it][0], b = items[it][1]; u32 m = 1u << b;
    printf("\n%s%d[%d] '%c'\n", tl_kname(k), r, b, sym(&M->full.c[k][r], b));
    printf("  A local-flip first-break (P0, variants):");
    for (int i = 0; i < nb; i++) {
      TLPair p = PB[i];
      if (k == KW) { p.x.w[r] ^= m; p.y.w[r] = p.x.w[r] + M->dl[r]; } else { sv(&p.x, k, r, gv(&p.x, k, r) ^ m); sv(&p.y, k, r, gv(&p.y, k, r) ^ m); }
      int t = local_break(&p, 0, 15); if (t < 0) printf(" -"); else printf(" %c%d", t & 1 ? 'A' : 'E', t / 2);
    }
    printf("\n");
    memcpy(CD, &M->base, sizeof(TLConds)); dropbit(CD, k, r, b);
    u32 fm = fm0, fv = fv0; if (k == KE) { fm &= ~m; fv &= ~m; }
    printf("  B row-local count with condition dropped (P0, variants):");
    for (int i = 0; i < nb; i++) printf(" %ld", rowcount(&PB[i], r, CD, fm, fv, NULL, 0));
    printf("   (baseline %ld)\n", base_cnt[0]);
    { TLPair q; int cons; TLCoord cc = C0; char buf[200];
      if (k == KW) { cc.wx[r] ^= m; cons = tl_build(M, &cc, &q); }
      else { TLPair f = P0; sv(&f.x, k, r, gv(&f.x, k, r) ^ m); sv(&f.y, k, r, gv(&f.y, k, r) ^ m); cons = build_mod(&f, r, &cc, &q); }
      fullpath(&q, cons, &P0, buf, sizeof buf); printf("  C consistent bit-flip (P0): %s\n", buf); }
    { u32 keep[256]; long nk = rowcount(&P0, r, CD, fm, fv, keep, 256); long extra = 0, ev = 0, rows15 = 0, cons1 = 0, dmok = 0; u32 pubE = TE(&P0.x, r);
      for (long j = 0; j < nk && j < 256; j++) {
        if (keep[j] == pubE) continue; extra++;
        TLPair p = P0; mkrow(&p, r, keep[j]);
        TLCoord cc = C0; cc.wx[r] = p.x.w[r]; TLPair q; int cons = build_mod(&p, r, &cc, &q); cons1 += cons;
        if (cons) { dmok += diffpres(&q, &P0, 15, 0); rows15 += tl_rowsok(CD, &q, 0, 15) && fs(6, cc.wx[6]) && fs(7, cc.wx[7]); ev += tl_state_eq(&q, 36); }
      }
      printf("  D relaxed-row extra solutions on P0: %ld total passing (published among them: %d), extras %ld; consistent %ld; dmod<=15 kept %ld; rows<=15 ok (dropped conds) %ld; full-path EXACT %ld\n", nk, 1, extra, cons1, dmok, rows15, ev); }
  }
}
int main(int argc, char **argv) {
  const char *chi = "../../../../tools/traillab/chi/chi37.txt";
  tl_set_threads(2);
  M = calloc(1, sizeof(TLModel)); if (tl_load(chi, M, NULL, 0)) return 2;
  P0 = M->pub; C0 = M->pubc;
  { TLPair q; int cons = tl_build(M, &C0, &q); if (!cons || memcmp(&q.x.w, &P0.x.w, 16 * 4)) { printf("P0 rebuild mismatch\n"); return 3; } }
  cmd_row(argc > 1 ? atoi(argv[1]) : 14);
  return 0;
}
