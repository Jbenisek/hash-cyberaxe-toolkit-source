/* CLI for the block harness.
 *   harness check  configs.txt                      -> derive(D), derive(O) reproduce R; base observables hold the design
 *   harness apply  configs.txt cases.txt out.txt    -> batch apply(): one result line per case (format in HARNESS.md)
 *   harness bench  configs.txt [n]                  -> ns per apply() and per apply_fast(), each frame
 *   harness census configs.txt                      -> every single-bit and adjacent-pair flip of every coordinate word */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "harness.h"

static const char *FRAME_WORDS[3][14] = {
  { "Y4", "Y9", "w8", "D2.b1", "D3.a1", "K0.b1", "K3.d1", "S14", "S15", "C0.b1", "Y14" },
  { "C0.d1", "D2.a1", "D2.b1", "S11", "S4", "X9", "w6", "Y4", "T1", "E1.c1" },
  { "w0", "w1", "w2", "w3", "w5", "w6", "w7", "w8", "w9", "w10", "w11", "w12", "T0", "T1" } };
static const char *DNAME[ND] = { "Y3", "Y4", "Y9", "Y14", "w8", "Y3B", "X3", "X7", "X11", "X15", "Y11", "Y11B",
                                 "dY7", "dY15", "T1RANGE", "CLASS", "ETA", "DIG0257", "K3", "R0EQ" };

static config_t *CF; static int NCF;
static int load(const char *path) {
  FILE *f = fopen(path, "r"); if (!f) { perror(path); exit(1); }
  int cap = 256; CF = malloc(cap * sizeof(config_t)); NCF = 0;
  config_t c; char pool[8];
  while (fscanf(f, "%d %7s", &c.id, pool) == 2) {
    c.pool = pool[0];
    for (int i = 0; i < 11; i++) if (fscanf(f, "%x", &c.D[i]) != 1) exit(2);
    for (int i = 0; i < 10; i++) if (fscanf(f, "%x", &c.O[i]) != 1) exit(2);
    for (int i = 0; i < 14; i++) if (fscanf(f, "%x", &c.R[i]) != 1) exit(2);
    base_obs(&c);
    if (NCF == cap) { cap *= 2; CF = realloc(CF, cap * sizeof(config_t)); }
    CF[NCF++] = c;
  }
  fclose(f); return NCF;
}
static uint64_t S = 0x9E3779B97F4A7C15ull;
static uint64_t rnd64(void) { uint64_t z = (S += 0x9E3779B97F4A7C15ull); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
                              z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; return z ^ (z >> 31); }
static double now_s(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }
static int hw(uint32_t x) { return __builtin_popcount(x); }

static int cmd_check(void) {
  int bad = 0, t1v = 0; uint32_t zero[14] = { 0 }; result_t res;
  for (int k = 0; k < NCF; k++) {
    config_t *c = &CF[k]; uint32_t r[14], v[NW];
    for (int fr = 0; fr < 2; fr++) {
      uint32_t chk = derive(fr, fr == FR_D ? c->D : c->O, r, v);
      if (chk || memcmp(r, c->R, sizeof r)) { bad++; printf("config %d: frame %c does not reproduce R\n", c->id, "DOR"[fr]); }
    }
    const uint32_t *b = c->base;
    int ok = b[O_Y3] == Y3C && b[O_Y11] == Y11C && b[O_Y3B] == Y3BC && b[O_Y11B] == Y11BC && b[O_X3] == X3C &&
             b[O_X7] == X7C && b[O_X11] == X11C && b[O_X15] == X15C && b[O_DY7] == 0 && b[O_DY15] == 0 &&
             b[O_CLS] == 1 && b[O_ETA] == 1 && !(b[O_DD] | b[O_DD + 2] | b[O_DD + 5] | b[O_DD + 7]) && b[O_R0DIFF] == 0 &&
             b[O_Y4] == c->D[0] && b[O_Y9] == c->D[1] && b[O_W8] == c->D[2] && b[O_Y14] == c->D[10];
    for (int i = 0; i < 4; i++) ok &= b[O_RES + i] == (b[O_K1 + i] ^ b[O_K3 + i]);
    for (int fr = 0; fr < 3; fr++) { apply(c, fr, zero, &res); ok &= res.damage == 0 && res.info == (1u << I_SAME); }
    if (!ok) { bad++; printf("config %d: base observables violate the design\n", c->id); }
    t1v += t1_ok(b[O_T1]);
  }
  printf("configs %d, T1-valid %d, failures %d\n", NCF, t1v, bad);
  return bad != 0;
}

static int cmd_apply(const char *cases, const char *outp) {
  FILE *f = fopen(cases, "r"), *o = fopen(outp, "w"); if (!f || !o) { perror("open"); return 1; }
  long id; int ci; char fc[4]; uint32_t m[14]; result_t res; long n = 0;
  while (fscanf(f, "%ld %d %3s", &id, &ci, fc) == 3) {
    int fr = fc[0] == 'D' ? FR_D : fc[0] == 'O' ? FR_O : FR_R;
    for (int i = 0; i < NCOORD[fr]; i++) if (fscanf(f, "%x", &m[i]) != 1) return 2;
    apply(&CF[ci], fr, m, &res);
    uint32_t t1, k[4], fd = apply_fast(&CF[ci], fr, m, &t1, k);
    fprintf(o, "%ld %x %x %08x", id, res.damage, res.info, res.chk);
    for (int i = 0; i < NOBS; i++) fprintf(o, " %08x", res.now[i]);
    fprintf(o, " | %x %08x %08x %08x %08x %08x\n", fd, t1, k[0], k[1], k[2], k[3]);
    n++;
  }
  fclose(f); fclose(o); printf("applied %ld cases\n", n); return 0;
}

static int cmd_bench(long n) {
  uint32_t *masks = malloc(sizeof(uint32_t) * 14 * 4096); result_t res; volatile uint32_t sink = 0;
  for (int fr = 0; fr < 3; fr++) {
    for (int j = 0; j < 4096; j++) {
      uint32_t *m = masks + 14 * j; memset(m, 0, 14 * 4);
      int nb = 1 + rnd64() % 4;
      for (int b = 0; b < nb; b++) { uint64_t z = rnd64(); m[(z >> 8) % NCOORD[fr]] ^= 1u << (z & 31); }
    }
    double t = now_s();
    for (long i = 0; i < n; i++) { apply(&CF[i % NCF], fr, masks + 14 * (i & 4095), &res); sink ^= res.damage ^ res.now[O_K1]; }
    double tf = now_s() - t; t = now_s();
    for (long i = 0; i < n; i++) { uint32_t t1, k[4]; sink ^= apply_fast(&CF[i % NCF], fr, masks + 14 * (i & 4095), &t1, k) ^ k[0]; }
    double tq = now_s() - t;
    printf("frame %c: apply %.1f ns, apply_fast %.1f ns (n=%ld, one core)\n", "DOR"[fr], 1e9 * tf / n, 1e9 * tq / n, n);
  }
  free(masks); return (int)(sink & 0);
}

static int cmd_census(void) {
  result_t res; uint32_t m[14];
  for (int fr = 0; fr < 3; fr++) {
    printf("frame %c (%d configs): word  single:[zero-damage with the point moved / and K1 moved]  adjacent-pair:[same]  null blocks  single-bit damage frequency\n", "DOR"[fr], NCF);
    for (int w = 0; w < NCOORD[fr]; w++) {
      long z1 = 0, k1 = 0, z2 = 0, k2 = 0, n1 = 0, n2 = 0, nul = 0; long cnt[ND] = { 0 };
      for (int c = 0; c < NCF; c++)
        for (int b = 0; b < 32; b++)
          for (int pair = 0; pair < 2; pair++) {
            if (pair && b == 31) continue;
            memset(m, 0, sizeof m); m[w] = pair ? 3u << b : 1u << b;
            apply(&CF[c], fr, m, &res);
            int moved = (res.now[O_K1] ^ CF[c].base[O_K1]) | (res.now[O_K1 + 1] ^ CF[c].base[O_K1 + 1]) |
                        (res.now[O_K1 + 2] ^ CF[c].base[O_K1 + 2]) | (res.now[O_K1 + 3] ^ CF[c].base[O_K1 + 3]);
            int zero = !res.damage && !(res.info >> I_SAME & 1);   /* zero damage AND the real point moved */
            nul += res.info >> I_SAME & 1;
            if (!pair) { n1++; z1 += zero; k1 += zero && moved; for (int d = 0; d < ND; d++) cnt[d] += res.damage >> d & 1; }
            else { n2++; z2 += zero; k2 += zero && moved; }
          }
      printf("  %-6s single %ld: [%ld / %ld]  pair %ld: [%ld / %ld]  null(same point) %ld  damage freq:", FRAME_WORDS[fr][w], n1, z1, k1, n2, z2, k2, nul);
      for (int d = 0; d < ND; d++) if (cnt[d]) printf(" %s=%.2f", DNAME[d], (double)cnt[d] / n1);
      printf("\n");
    }
  }
  return 0;
}

int main(int argc, char **argv) {
  if (argc < 3) { fprintf(stderr, "usage: harness check|apply|bench|census configs.txt ...\n"); return 1; }
  load(argv[2]);
  if (!strcmp(argv[1], "check")) return cmd_check();
  if (!strcmp(argv[1], "apply")) return cmd_apply(argv[3], argv[4]);
  if (!strcmp(argv[1], "bench")) return cmd_bench(argc > 3 ? atol(argv[3]) : 2000000);
  if (!strcmp(argv[1], "census")) return cmd_census();
  return 1;
}
