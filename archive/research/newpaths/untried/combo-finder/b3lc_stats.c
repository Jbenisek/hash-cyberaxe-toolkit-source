/* b3lc_stats.c -- stage statistics for the {m2,m3,m4,m6} local collision (2-round BLAKE3).
 * Modes:
 *   stage   : light correctness check of K3 and K1 against the real G call (20 solutions each)
 *   k3stat H7 FLAGS LOG2N OUT   : sample random (A,delta); record solutions; rescan clumping
 *   k2enum H6 BLEN OUT          : all A,A' with F2(A)=F2(A') (K2(a)); test K2(b); write D2 set
 *   overlap D2FILE H7 FLAGS SECONDS : sample K3 solutions; count -D in D2
 * Build: gcc -O3 -march=native -o b3stats b3lc_stats.c -lm
 */
#include "b3lc.h"
#include <time.h>
#include <math.h>

static double now(void){ struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }
static void g4(u32 a, u32 b, u32 c, u32 d, u32 x, u32 y, u32 o[4]){
  u32 v[16] = {0}; v[0] = a; v[1] = b; v[2] = c; v[3] = d; b3_g(v, 0, 1, 2, 3, x, y);
  o[0] = v[0]; o[1] = v[1]; o[2] = v[2]; o[3] = v[3];
}
static u32 parse(const char *s){ return (u32)strtoul(s, 0, 0); }

/* ---------- stage: light check (time-capped: 120 s per stage) ---------- */
static int stage(void){
  int bad = 0, n = 0; u64 tries = 0; double t0 = now();
  while (n < 20 && (tries & 0xffffff || now() - t0 < 120)){
    u32 h3 = (u32)rnd64(), h7 = (u32)rnd64(), flags = (u32)(rnd64() & 15), A = (u32)rnd64(), delta = (u32)rnd64();
    K3sol s; tries++;
    if (!k3_try(h7, flags, A, delta, &s, 1)) continue;
    n++;
    u32 m6 = A - h3 - h7, o[4], op[4];
    g4(h3, h7, B3IV[3], flags, m6, s.m7base, o); g4(h3, h7, B3IV[3], flags, m6 + delta, s.m7base, op);
    if (o[1] != op[1] || o[3] != op[3] || op[0] - o[0] != s.D || o[0] == op[0] || o[2] == op[2]) bad++;
  }
  printf("K3 real-G check: %d solutions, %llu tries, log2 rate %.2f, bad %d (%.1f s)\n", n,
         (unsigned long long)tries, log2((double)n / tries), bad, now() - t0);
  n = 0; tries = 0; t0 = now(); int b1 = 0;
  while (n < 20 && (tries & 0xffffff || now() - t0 < 120)){
    u32 h1 = (u32)rnd64(), h5 = (u32)rnd64(), thi = (u32)rnd64(), dm2 = (u32)rnd64(), dv6 = (u32)rnd64(), A = (u32)rnd64();
    K1sol s; tries++;
    if (!k1_try(h5, thi, A, dm2, dv6, (int)(rnd64() & 1), &s, 1)) continue;
    n++;
    u32 m2 = A - h1 - h5, o[4], op[4];
    g4(h1, h5, B3IV[1], thi, m2, s.m3base, o); g4(h1, h5, B3IV[1], thi, m2 + dm2, s.m3base + s.dm3, op);
    if (o[1] != op[1] || o[3] != op[3] || op[0] - o[0] != s.Dm || s.Dm + dv6 != (u32)(0u - s.dm3)) b1++;
  }
  printf("K1 real-G check: %d solutions, %llu tries, log2 rate %.2f, bad %d (%.1f s)\n", n,
         (unsigned long long)tries, log2((double)n / tries), b1, now() - t0);
  return bad + b1;
}

/* ---------- k3stat ---------- */
static int k3stat(u32 h7, u32 flags, int lg, const char *out){
  FILE *fo = fopen(out, "w"); if (!fo) { perror(out); return 1; }
  u64 N = 1ULL << lg, nsol = 0; double t0 = now();
  u32 *deltas = malloc(4096 * sizeof(u32)); int nd = 0;
  int hwD[33] = {0};
  for (u64 i = 0; i < N; i++){
    u32 A = (u32)rnd64(), delta = (u32)rnd64(); K3sol s;
    if (!k3_try(h7, flags, A, delta, &s, 1)) continue;
    nsol++;
    hwD[__builtin_popcount(s.D)]++;
    fprintf(fo, "%08x %08x %08x %llu\n", A, delta, s.D, (unsigned long long)s.nsol);
    if (nd < 4096) deltas[nd++] = delta;
  }
  double el = now() - t0;
  printf("k3stat h7=%08x flags=%u: %llu solutions in 2^%d samples (log2 rate %.2f), %.1f s\n", h7, flags,
         (unsigned long long)nsol, lg, nsol ? log2((double)nsol / N) : -999.0, el);
  printf("  HW(D) histogram:"); for (int w = 0; w <= 32; w++) if (hwD[w]) printf(" %d:%d", w, hwD[w]); printf("\n");
  /* clumping: for the first 8 found deltas, rescan 2^24 random A at the same delta */
  int nre = nd < 8 ? nd : 8;
  for (int j = 0; j < nre; j++){
    u64 hit = 0, M = 1ULL << 24; u32 dl = deltas[j];
    for (u64 i = 0; i < M; i++){ u32 A = (u32)rnd64(); if (k3_try(h7, flags, A, dl, 0, 0)) hit++; }
    printf("  rescan delta=%08x: %llu of 2^24 A (log2 %.2f)\n", dl, (unsigned long long)hit,
           hit ? log2((double)hit / M) : -999.0);
  }
  /* control: 8 random deltas (odd) rescanned */
  for (int j = 0; j < 4; j++){
    u64 hit = 0, M = 1ULL << 24; u32 dl = (u32)rnd64() | 1u;
    for (u64 i = 0; i < M; i++){ u32 A = (u32)rnd64(); if (k3_try(h7, flags, A, dl, 0, 0)) hit++; }
    printf("  control random delta=%08x: %llu of 2^24\n", dl, (unsigned long long)hit);
  }
  fclose(fo); free(deltas);
  return 0;
}

/* ---------- k2enum: all K2(a) solutions for one instance by bucketed sort ---------- */
static void radix64(u64 *a, u64 *tmp, size_t n, int lo_bit, int hi_bit){
  for (int sh = lo_bit; sh < hi_bit; sh += 8){
    size_t cnt[257]; memset(cnt, 0, sizeof cnt);
    for (size_t i = 0; i < n; i++) cnt[((a[i] >> sh) & 255) + 1]++;
    for (int b = 0; b < 256; b++) cnt[b + 1] += cnt[b];
    for (size_t i = 0; i < n; i++) tmp[cnt[(a[i] >> sh) & 255]++] = a[i];
    memcpy(a, tmp, n * sizeof(u64));
  }
}
static inline u32 F2(u32 h6, u32 blen, u32 A){ return A + ror32(h6 ^ (B3IV[2] + ror32(blen ^ A, 16)), 12); }
static int k2enum(u32 h6, u32 blen, const char *out){
  FILE *fo = fopen(out, "wb"); if (!fo) { perror(out); return 1; }
  const int TB = 3; const size_t CAP = (size_t)1 << (32 - TB + 1) ; /* generous */
  u64 *buf = malloc(CAP * sizeof(u64)), *tmp = malloc(CAP * sizeof(u64));
  if (!buf || !tmp) { fprintf(stderr, "oom\n"); return 1; }
  u64 ncoll = 0, nb = 0, maxrun = 0; double t0 = now();
  int hwdm[33] = {0};
  for (u32 bucket = 0; bucket < (1u << TB); bucket++){
    size_t n = 0;
    for (u64 A64 = 0; A64 < (1ULL << 32); A64++){
      u32 A = (u32)A64, F = F2(h6, blen, A);
      if ((F >> (32 - TB)) == bucket) buf[n++] = ((u64)F << 32) | A;
    }
    radix64(buf, tmp, n, 32, 64 - TB);
    size_t i = 0;
    while (i < n){
      size_t j = i + 1; u32 F = (u32)(buf[i] >> 32);
      while (j < n && (u32)(buf[j] >> 32) == F) j++;
      if (j - i > maxrun) maxrun = j - i;
      for (size_t x = i; x < j; x++) for (size_t y = i; y < j; y++){
        if (x == y) continue;
        u32 A = (u32)buf[x], Ap = (u32)buf[y], dm4 = Ap - A;
        ncoll++;
        if (k2_b(h6, blen, A, dm4, 0)){
          nb++; hwdm[__builtin_popcount(dm4)]++;
          u32 rec[2] = {dm4, A}; fwrite(rec, sizeof rec, 1, fo);
        }
      }
      i = j;
    }
    fprintf(stderr, "bucket %u: n=%zu ordered coll so far %llu, (b) passes %llu, %.1f s\n", bucket, n,
            (unsigned long long)ncoll, (unsigned long long)nb, now() - t0);
  }
  printf("k2enum h6=%08x blen=%u: ordered K2(a) pairs %llu (log2 %.3f), K2(a)&(b) %llu (log2 %.3f), P(b|a)=2^%.3f, max run %llu, %.1f s\n",
         h6, blen, (unsigned long long)ncoll, log2((double)ncoll), (unsigned long long)nb, log2((double)nb),
         log2((double)nb / ncoll), (unsigned long long)maxrun, now() - t0);
  printf("  HW(dm4) histogram of K2-solvable:"); for (int w = 0; w <= 32; w++) if (hwdm[w]) printf(" %d:%d", w, hwdm[w]); printf("\n");
  fclose(fo); free(tmp);
  { /* 2-adic valuation histogram of K2-solvable dm4 */
    FILE *fi = fopen(out, "rb"); u32 r2[2]; u64 vh[33] = {0};
    while (fread(r2, sizeof r2, 1, fi) == 1) vh[r2[0] ? __builtin_ctz(r2[0]) : 32]++;
    fclose(fi);
    printf("  v2(dm4) histogram of K2-solvable:"); for (int w = 0; w <= 32; w++) if (vh[w]) printf(" %d:%llu", w, (unsigned long long)vh[w]); printf("\n");
  }
  /* bitmap of K2-solvable dm4 (2^32 bits) written next to OUT as OUT.bm */
  {
    u32 *bm = (u32 *)buf; memset(bm, 0, (size_t)1 << 29);
    FILE *fi = fopen(out, "rb"); u32 rec[2]; u64 distinct = 0;
    while (fread(rec, sizeof rec, 1, fi) == 1){ u32 k = rec[0]; if (!((bm[k >> 5] >> (k & 31)) & 1)) { distinct++; bm[k >> 5] |= 1u << (k & 31); } }
    fclose(fi);
    char name[1024]; snprintf(name, sizeof name, "%s.bm", out);
    FILE *fb = fopen(name, "wb"); fwrite(bm, 1, (size_t)1 << 29, fb); fclose(fb);
    printf("  distinct K2-solvable dm4: %llu (log2 %.3f) -> bitmap %s\n", (unsigned long long)distinct, log2((double)distinct), name);
  }
  free(buf);
  return 0;
}

/* ---------- overlap: K3 sampling vs D2 set (open addressing) ---------- */
static u32 *H; static u64 HM;
static void hins(u32 k){ u64 i = ((u64)k * 0x9E3779B1u) & HM; while (H[i] != 0xffffffffu) { if (H[i] == k) return; i = (i + 1) & HM; } H[i] = k; }
static int hhas(u32 k){ u64 i = ((u64)k * 0x9E3779B1u) & HM; while (H[i] != 0xffffffffu) { if (H[i] == k) return 1; i = (i + 1) & HM; } return 0; }
static int overlap(const char *d2file, u32 h7, u32 flags, double secs){
  FILE *f = fopen(d2file, "rb"); if (!f) { perror(d2file); return 1; }
  HM = (1ULL << 24) - 1; H = malloc((HM + 1) * sizeof(u32)); memset(H, 0xff, (HM + 1) * sizeof(u32));
  u32 rec[2]; u64 n = 0;
  while (fread(rec, sizeof rec, 1, f) == 1) { hins(rec[0]); n++; }
  fclose(f);
  u64 distinct = 0; for (u64 i = 0; i <= HM; i++) if (H[i] != 0xffffffffu) distinct++;
  printf("overlap: D2 records %llu, distinct dm4 %llu (log2 %.3f)\n", (unsigned long long)n, (unsigned long long)distinct, log2((double)distinct));
  double t0 = now(); u64 tries = 0, nk3 = 0, hits = 0;
  while (now() - t0 < secs){
    for (int r = 0; r < (1 << 20); r++){
      u32 A = (u32)rnd64(), delta = (u32)rnd64(); K3sol s; tries++;
      if (!k3_try(h7, flags, A, delta, &s, 1)) continue;
      nk3++;
      if (hhas((u32)(0u - s.D))) { hits++; printf("  HIT A=%08x delta=%08x D=%08x\n", A, delta, s.D); }
    }
  }
  printf("overlap: K3 solutions %llu in %llu tries (log2 rate %.2f); hits %llu; expected if independent %.4f\n",
         (unsigned long long)nk3, (unsigned long long)tries, log2((double)nk3 / tries), (unsigned long long)hits,
         nk3 * (double)distinct / 4294967296.0);
  return 0;
}

static int rottest(void){
  int bad = 0;
  for (int R = 8; R <= 16; R += 8){
    for (int it = 0; it < 200000; it++){
      u32 c = (u32)rnd64(), cp = (u32)rnd64(), Dl = (u32)rnd64(), w = (u32)rnd64();
      if (it & 1) Dl &= (u32)rnd64();
      u32 M = ror32(cp ^ (w + Dl), R) - ror32(c ^ w, R), ww; u64 cnt;
      if (!rotdp(c, cp, Dl, R, M, rnd64(), &ww, &cnt)) { bad++; continue; }
      if (ror32(cp ^ (ww + Dl), R) - ror32(c ^ ww, R) != M) bad++;
    }
    printf("rottest R=%d forward: bad=%d\n", R, bad);
  }
  /* exact counts vs brute force, 2 instances per R */
  for (int R = 8; R <= 16; R += 8) for (int k = 0; k < 2; k++){
    u32 c = (u32)rnd64(), cp = (u32)rnd64(), Dl = (u32)rnd64() & (u32)rnd64(), w0 = (u32)rnd64();
    u32 M = ror32(cp ^ (w0 + Dl), R) - ror32(c ^ w0, R); u64 cnt, bf = 0;
    rotdp(c, cp, Dl, R, M, 0, 0, &cnt);
    for (u64 w = 0; w < (1ULL << 32); w++){ u32 x = (u32)w; if (ror32(cp ^ (x + Dl), R) - ror32(c ^ x, R) == M) bf++; }
    printf("rottest R=%d exact: dp=%llu brute=%llu %s\n", R, (unsigned long long)cnt, (unsigned long long)bf, cnt == bf ? "OK" : "MISMATCH");
    if (cnt != bf) bad++;
  }
  return bad;
}

int main(int argc, char **argv){
  if (argc < 2) return 1;
  setvbuf(stdout, NULL, _IOLBF, 0);
  g_rng = 0xB3C0FFEEULL ^ ((u64)time(0) << 20);
  if (!strcmp(argv[1], "rottest")) return rottest();
  if (!strcmp(argv[1], "stage")) return stage();
  if (!strcmp(argv[1], "k3stat") && argc >= 6) return k3stat(parse(argv[2]), parse(argv[3]), atoi(argv[4]), argv[5]);
  if (!strcmp(argv[1], "k2enum") && argc >= 5) return k2enum(parse(argv[2]), parse(argv[3]), argv[4]);
  if (!strcmp(argv[1], "overlap") && argc >= 6) return overlap(argv[2], parse(argv[3]), parse(argv[4]), atof(argv[5]));
  fprintf(stderr, "bad args\n"); return 1;
}
