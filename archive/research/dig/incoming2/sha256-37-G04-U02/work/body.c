/* scan.c - sha256-37-G04-U02 (our code; reuses job5 library-linked helpers copied in head.inc).
   dep [SEED]               dependency matrix CV word -> W0..W7, partner bijection, gate inputs
   bucket MODE LOG2N SEED   forward model; MODE 0 baseline, 1 fix A_-3, 2 fix A_-4, 3 fix E_-4 (to a seed constant), 4 fix A_-3=0
   real LOG2N SEED          real first blocks: CV word byte uniformity, all vs gate-passing */
static const u32 IV[8] = {0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19};
static const char *WN[8] = {"A_-4","A_-3","A_-2","A_-1","E_-4","E_-3","E_-2","E_-1"};
/* index j: 0..3 = A[0..3] (A_-4..A_-1), 4..7 = E[0..3] (E_-4..E_-1) */
static void wfrom(u32 *cv8, u32 a0, u32 *W) { u32 A[18], E[18]; memset(A,0,sizeof A); memset(E,0,sizeof E); for (int i=0;i<4;i++){A[i]=cv8[i];E[i]=cv8[4+i];} words_from_cv(A,E,a0,W); }
static int cmpu2(const void *a, const void *b) { u32 x = *(const u32 *)a, y = *(const u32 *)b; return x < y ? -1 : x > y; }
static void cmd_dep(u64 seed) {
  TLRng r = tl_rng(seed, 1, 0, 0);
  long chg[8][8] = {{0}}; int NS = 20000;
  for (int s = 0; s < NS; s++) {
    u32 a0 = W8C - G[tl_below(&r, nG)] - C4, cv[8], W[8], W2[8]; for (int i = 0; i < 8; i++) cv[i] = tl_r32(&r);
    wfrom(cv, a0, W);
    for (int j = 0; j < 8; j++) { u32 c2[8]; memcpy(c2, cv, 32); do c2[j] = tl_r32(&r); while (c2[j] == cv[j]); wfrom(c2, a0, W2);
      for (int i = 0; i < 8; i++) chg[j][i] += W[i] != W2[i]; }
  }
  printf("DEP matrix: fraction of %d random (CV,a0,redraw) where redrawing CV word (row) changes W_i (col), Lemma 4.1 map\n        ", NS);
  for (int i = 0; i < 8; i++) printf(" W%d     ", i); printf("\n");
  for (int j = 0; j < 8; j++) { printf("%-5s   ", WN[j]); for (int i = 0; i < 8; i++) printf(" %.4f ", (double)chg[j][i] / NS); printf("\n"); }
  int partner[8] = {4, 5, 6, 7, 0, 1, 2, 3}; long NV = 1 << 22;
  u32 *out = malloc(NV * 4);
  for (int j = 0; j < 8; j++) {
    int okall = 1; long mind = NV;
    for (int rep = 0; rep < 4; rep++) {
      u32 a0 = W8C - G[tl_below(&r, nG)] - C4, cv[8], W[8]; for (int i = 0; i < 8; i++) cv[i] = tl_r32(&r);
      u32 base = tl_r32(&r);
      for (long k = 0; k < NV; k++) { cv[j] = base + (u32)k * 1019u; wfrom(cv, a0, W); out[k] = W[partner[j]]; }
      qsort(out, NV, 4, cmpu2); long d = 1; for (long k = 1; k < NV; k++) d += out[k] != out[k-1];
      if (d != NV) okall = 0; if (d < mind) mind = d;
    }
    printf("PARTNER %-5s -> W%d: 4 x %ld distinct input values (word varied, other 7 held) give %s outputs (min distinct %ld)\n", WN[j], partner[j], NV, okall ? "all distinct (injective on the sample)" : "COLLISIONS", mind);
  }
}
#define NB 256
#define HB 4096
typedef struct { u64 good, pass, grp, tot; u64 n[4][NB], p[4][NB]; u64 h[4][HB]; u64 allc[3][2][NB], goodc[3][2][NB]; } BAcc;
typedef struct { u64 seed; long nper; int K; int mode; u32 fixv; int real; BAcc *acc; int nt; } BCtx;
static void tally(BAcc *a, const u32 *A, const u32 *W, int p, int first) {
  a->good++; a->pass += p; u32 x[4] = {A[1] >> 24, A[1] & 255, A[0] >> 24, A[0] & 255};
  for (int q = 0; q < 4; q++) { a->n[q][x[q]]++; a->p[q][x[q]] += p; }
  if (first) { a->grp++; a->h[0][W[4] >> 20]++; a->h[1][W[4] & 4095]++; a->h[2][W[5] >> 20]++; a->h[3][W[5] & 4095]++; }
}
static void w_bucket2(void *v, long ti, int tid) {
  BCtx *s = v; BAcc *a = &s->acc[ti]; TLRng r = tl_rng(s->seed, 606, (u64)ti, 3);
  u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); u64 g = tl_below(&r, (u64)nG);
  while ((long)a->good < s->nper) {
    u32 w8 = G[g++ % (u64)nG], e4 = W8C - w8, a0 = e4 - C4;
    if (s->real) {
      u32 m0[16], cv[8]; for (int i = 0; i < 16; i++) m0[i] = tl_r32(&r); tl_compress_ref(IV, m0, 37, cv); a->tot++;
      for (int i = 0; i < 4; i++) { A[3 - i] = cv[i]; E[3 - i] = cv[4 + i]; }
      /* cv[i] = A_{-1-i}, cv[4+i] = E_{-1-i}: A_-3 = cv[2], A_-4 = cv[3], E_-4 = cv[7] */
      u32 wv[3] = {cv[2], cv[3], cv[7]};
      for (int q = 0; q < 3; q++) { a->allc[q][0][wv[q] >> 24]++; a->allc[q][1][wv[q] & 255]++; }
      words_from_cv(A, E, a0, W); if (!fs(7, W[7]) || !fs(6, W[6])) continue;
      for (int q = 0; q < 3; q++) { a->goodc[q][0][wv[q] >> 24]++; a->goodc[q][1][wv[q] & 255]++; }
      u32 u = W[0] + ss0(W[1]); tally(a, A, W, lookup(u) != 0, 1);
      continue;
    }
    A[3] = tl_r32(&r); for (int i = 0; i < 3; i++) A[i] = tl_r32(&r); for (int i = 0; i < 4; i++) E[i] = tl_r32(&r);
    if (s->mode == 1 || s->mode == 4) A[1] = s->fixv; if (s->mode == 2) A[0] = s->fixv; if (s->mode == 3) E[0] = s->fixv;
    words_from_cv(A, E, a0, W); if (!fs(7, W[7])) continue;
    int ok6 = 0; for (int t = 0; t < 4096 && !ok6; t++) { A[2] = tl_r32(&r); words_from_cv(A, E, a0, W); ok6 = fs(6, W[6]); }
    if (!ok6) continue;
    for (int k = 0; k < s->K; k++) {
      A[1] = tl_r32(&r); A[0] = tl_r32(&r); for (int i = 0; i < 4; i++) E[i] = tl_r32(&r);
      if (s->mode == 1 || s->mode == 4) A[1] = s->fixv; if (s->mode == 2) A[0] = s->fixv; if (s->mode == 3) E[0] = s->fixv;
      words_from_cv(A, E, a0, W);
      u32 u = W[0] + ss0(W[1]); tally(a, A, W, lookup(u) != 0, k == 0);
    }
  }
}
static double chi2p(double x, int k) { double z = (cbrt(x / k) - (1 - 2.0 / (9 * k))) / sqrt(2.0 / (9 * k)); return 0.5 * erfc(z / sqrt(2)); }
static void unif(const char *nm, const u64 *c, int nb) { double t = 0, chi = 0; for (int i = 0; i < nb; i++) t += c[i]; double e = t / nb; for (int i = 0; i < nb; i++) chi += (c[i] - e) * (c[i] - e) / e;
  printf("UNIFORM %-30s n %.0f bins %d chi2 %.1f dof %d p %.4g\n", nm, t, nb, chi, nb - 1, chi2p(chi, nb - 1)); }
static void bkt(const char *nm, const u64 *n, const u64 *p, double ph) {
  double chi = 0, mx = 0, mn = 1e9; int imx = 0, imn = 0;
  for (int b = 0; b < NB; b++) { double e = n[b] * ph; if (e > 0) chi += (p[b] - e) * (p[b] - e) / (e * (1 - ph)); double rt = (double)p[b] / n[b] / ph; if (rt > mx) { mx = rt; imx = b; } if (rt < mn) { mn = rt; imn = b; } }
  printf("BUCKETS %-12s chi2 %.1f on %d dof, p = %.4g | max bucket %02x ratio %.4f | min bucket %02x ratio %.4f\n", nm, chi, NB - 1, chi2p(chi, NB - 1), imx, mx, imn, mn); }
static void cmd_bucket2(int mode, int lg, u64 seed, int real) {
  BCtx s; memset(&s, 0, sizeof s); s.seed = seed; s.K = 256; s.nt = 384; s.mode = mode; s.real = real;
  TLRng rr = tl_rng(seed, 77, 0, 0); s.fixv = mode == 4 ? 0 : tl_r32(&rr); s.acc = calloc(s.nt, sizeof(BAcc));
  if (real) s.nper = (long)(ldexp(1.0, lg) * pow(2, -9.8796) / s.nt); else s.nper = (long)((1ull << lg) / s.nt);
  double t0 = time(NULL); tl_parfor(s.nt, 1, w_bucket2, &s);
  BAcc *T = calloc(1, sizeof(BAcc));
  for (int t = 0; t < s.nt; t++) { BAcc *a = &s.acc[t]; T->good += a->good; T->pass += a->pass; T->grp += a->grp; T->tot += a->tot;
    for (int q = 0; q < 4; q++) { for (int b = 0; b < NB; b++) { T->n[q][b] += a->n[q][b]; T->p[q][b] += a->p[q][b]; } for (int b = 0; b < HB; b++) T->h[q][b] += a->h[q][b]; }
    for (int q = 0; q < 3; q++) for (int h = 0; h < 2; h++) for (int b = 0; b < NB; b++) { T->allc[q][h][b] += a->allc[q][h][b]; T->goodc[q][h][b] += a->goodc[q][h][b]; } }
  double ph = (double)T->pass / T->good, lo, hi; tl_wilson(T->pass, T->good, &lo, &hi);
  printf("RESULT %s mode %d fixv %08x seed %llu: good %llu groups %llu | row16 any-l %llu = 2^%.4f [2^%.4f, 2^%.4f] (table 2^%.4f) | %.0f s\n", real ? "real" : "fwd", mode, mode ? s.fixv : 0, (unsigned long long)seed,
    (unsigned long long)T->good, (unsigned long long)T->grp, (unsigned long long)T->pass, log2(ph), log2(lo), log2(hi), log2(1042240.0 / 4294967296.0), time(NULL) - t0);
  if (real) { double gl, gh; tl_wilson(T->good, T->tot, &gl, &gh); printf("REAL blocks %llu good %llu = 2^%.4f [2^%.4f, 2^%.4f] (exact 2^-9.8796)\n", (unsigned long long)T->tot, (unsigned long long)T->good, log2((double)T->good / T->tot), log2(gl), log2(gh));
    const char *cn[3] = {"A_-3", "A_-4", "E_-4"}; char b[64];
    for (int q = 0; q < 3; q++) for (int h = 0; h < 2; h++) { sprintf(b, "all blocks %s %s", cn[q], h ? "low8" : "hi8"); unif(b, T->allc[q][h], NB); sprintf(b, "gate-pass %s %s", cn[q], h ? "low8" : "hi8"); unif(b, T->goodc[q][h], NB); }
  }
  if (mode == 0 && !real) { bkt("A_-3>>24", T->n[0], T->p[0], ph); bkt("A_-3&ff", T->n[1], T->p[1], ph); bkt("A_-4>>24", T->n[2], T->p[2], ph); bkt("A_-4&ff", T->n[3], T->p[3], ph); }
  unif("W4 top12 (per group)", T->h[0], HB); unif("W4 low12 (per group)", T->h[1], HB); unif("W5 top12 (per group)", T->h[2], HB); unif("W5 low12 (per group)", T->h[3], HB);
}
int main(int argc, char **argv) {
  const char *chi = "../../../../tools/traillab/chi/chi37.txt"; int th = 3;
  for (int i = 1; i < argc - 1; i++) if (!strcmp(argv[i], "--threads")) th = atoi(argv[i + 1]);
  setvbuf(stdout, NULL, _IOLBF, 0); tl_set_threads(th); if (tl_sha256_selftest()) { printf("selftest FAIL\n"); return 9; }
  M = calloc(1, sizeof(TLModel)); if (tl_load(chi, M, NULL, 0)) return 2; P0 = M->pub; C0 = M->pubc;
  { TLPair q; int cons = tl_build(M, &C0, &q); if (!cons || memcmp(&q.x.w, &P0.x.w, 64)) { printf("P0 rebuild mismatch\n"); return 3; } }
  const char *cmd = argv[1];
  enum_G(); init_fwd(); printf("G = %ld\n", nG);
  { u32 A[18], E[18], W[8]; memcpy(A, SA, sizeof A); memcpy(E, SE, sizeof E); words_from_cv(A, E, TA(&P0.x, 0), W); int bad = 0; for (int i = 0; i < 8; i++) bad += W[i] != P0.x.w[i]; printf("Lemma 4.1 map on published CV: %s\n", bad ? "DIFFER" : "W0..W7 equal published"); if (bad) return 6; }
  if (!strcmp(cmd, "dep")) { cmd_dep(argc > 2 ? atoll(argv[2]) : 1); return 0; }
  build_table();
  if (!strcmp(cmd, "bucket")) cmd_bucket2(atoi(argv[2]), atoi(argv[3]), strtoull(argv[4], NULL, 10), 0);
  else if (!strcmp(cmd, "real")) cmd_bucket2(0, atoi(argv[2]), strtoull(argv[3], NULL, 10), 1);
  return 0;
}
