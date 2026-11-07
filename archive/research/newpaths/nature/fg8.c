// fg8.c - fast functional-graph test at w=8 (replaces the slow generic `nature funcgraph`, same definitions):
// f(x) = half digest (A = out0,2,5,7 or B = out1,3,4,6) of the toy message with x's 4 bytes in 4 chosen words
// (or in the top 2 bits of all 16 words: "msb2"), other words fixed (zero or seeded random); 2^32 points;
// image fraction and pair count sum n(n-1)/N against a random map; rho from random starts.
// Build: gcc -O3 -march=native -o fg8 fg8.c -lm
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>
#include <sys/mman.h>

typedef uint8_t u8;
static const u8 IV8[8] = {0x67, 0x85, 0x72, 0x3a, 0x7f, 0x8c, 0xab, 0x19};
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
static inline u8 R(u8 z, int r) { return (u8)((z >> r) | (z << (8 - r))); }
#define G8(a, b, c, d, x, y) do { a = a + b + (x); d = R(d ^ a, 4); c = c + d; b = R(b ^ c, 3); \
    a = a + b + (y); d = R(d ^ a, 2); c = c + d; b = R(b ^ c, 1); } while (0)

static int EMB[4], MODE = 0, HALF = 0, NR = 2, CTRL = 0; static u8 BASE[16];
static uint64_t rs = 0x1234;
static inline uint64_t mix64(uint64_t z) { z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull; z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; return z ^ (z >> 31); }
static inline uint64_t rnd64(void) { return mix64(rs += 0x9E3779B97F4A7C15ull); }

static inline uint32_t f(uint32_t x) {
    if (CTRL) return (uint32_t)mix64(x ^ 0xABCDEFull);
    u8 m[16], mm[16], v[16];
    memcpy(m, BASE, 16);
    if (MODE == 0) { m[EMB[0]] = x; m[EMB[1]] = x >> 8; m[EMB[2]] = x >> 16; m[EMB[3]] = x >> 24; }
    else for (int k = 0; k < 16; k++) m[k] = (m[k] & 0x3f) | (((x >> (2 * k)) & 3) << 6);
    for (int i = 0; i < 8; i++) v[i] = IV8[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IV8[i];
    v[12] = 0; v[13] = 0; v[14] = 16; v[15] = 11;
    for (int r = 0; r < NR; r++) {
        G8(v[0], v[4], v[8], v[12], m[0], m[1]);
        G8(v[1], v[5], v[9], v[13], m[2], m[3]);
        G8(v[2], v[6], v[10], v[14], m[4], m[5]);
        G8(v[3], v[7], v[11], v[15], m[6], m[7]);
        G8(v[0], v[5], v[10], v[15], m[8], m[9]);
        G8(v[1], v[6], v[11], v[12], m[10], m[11]);
        G8(v[2], v[7], v[8], v[13], m[12], m[13]);
        G8(v[3], v[4], v[9], v[14], m[14], m[15]);
        for (int i = 0; i < 16; i++) mm[i] = m[PERM[i]];
        memcpy(m, mm, 16);
    }
    u8 o[8]; for (int i = 0; i < 8; i++) o[i] = v[i] ^ v[i + 8];
    return HALF ? (o[1] | (o[3] << 8) | (o[4] << 16) | ((uint32_t)o[6] << 24)) : (o[0] | (o[2] << 8) | (o[5] << 16) | ((uint32_t)o[7] << 24));
}

int main(int argc, char **argv) {
    // fg8 emb half zero_base seed nstarts rounds
    const char *emb = argv[1]; HALF = atoi(argv[2]); int zb = atoi(argv[3]); rs = strtoull(argv[4], 0, 0); int ns = atoi(argv[5]); NR = atoi(argv[6]);
    if (!strcmp(emb, "ctrl")) CTRL = 1; else if (!strcmp(emb, "msb2")) MODE = 1; else sscanf(emb, "%d,%d,%d,%d", &EMB[0], &EMB[1], &EMB[2], &EMB[3]);
    for (int i = 0; i < 16; i++) BASE[i] = zb ? 0 : (u8)rnd64();
    // self-check against the generic implementation: message 0..15 at w=8 -> out (244,101,85,215,148,182,146,120) (job29)
    { int sv = MODE, sc = CTRL, snr = NR; u8 sb[16]; memcpy(sb, BASE, 16); MODE = 0; CTRL = 0; NR = 2;
      for (int i = 0; i < 16; i++) BASE[i] = i; EMB[0] = 0; EMB[1] = 1; EMB[2] = 2; EMB[3] = 3;
      int sh = HALF; HALF = 0; uint32_t a = f(0x03020100); HALF = 1; uint32_t b = f(0x03020100); HALF = sh;
      // job28.compress(range(16), 8, primary_rots(8)) = [164,139,213,106,24,135,83,250]
      int ok = a == (164u | 213u << 8 | 135u << 16 | 250u << 24) && b == (139u | 106u << 8 | 24u << 16 | 83u << 24);
      printf("selfcheck (job28 vector m=0..15): %s (A=%08x B=%08x)\n", ok ? "ok" : "MISMATCH", a, b); fflush(stdout); if (!ok) return 1;
      MODE = sv; CTRL = sc; NR = snr; memcpy(BASE, sb, 16);
      if (!CTRL && MODE == 0) sscanf(emb, "%d,%d,%d,%d", &EMB[0], &EMB[1], &EMB[2], &EMB[3]); }
    // optional 8th argument: domain bits DB (default 32). Inputs 0..2^DB-1 into 2^32 bins.
    int DB = argc > 7 ? atoi(argv[7]) : 32; uint64_t ND = 1ull << DB; uint32_t DM = (uint32_t)(ND - 1);
    uint8_t *cnt = mmap(0, 1ull << 32, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (cnt == MAP_FAILED) { printf("alloc fail\n"); return 1; }
    madvise(cnt, 1ull << 32, MADV_HUGEPAGE);
    time_t t0 = time(0);
    for (uint64_t x = 0; x < ND; x++) { uint32_t y = f((uint32_t)x); if (cnt[y] < 255) cnt[y]++; }
    uint64_t img = 0, sat = 0; double s2 = 0; int mx = 0;
    for (uint64_t y = 0; y < (1ull << 32); y++) { int c = cnt[y]; if (c) img++; if (c == 255) sat++; s2 += (double)c * (c - 1); if (c > mx) mx = c; }
    double M = 4294967296.0, Nd = (double)ND, expimg = M * (1.0 - exp(Nd * log1p(-1.0 / M))), exppairs = Nd * (Nd - 1) / M;
    printf("fg8 emb=%s half=%c base=%s rounds=%d domain 2^%d: occupied bins %.0f / expected %.0f (ratio %.7f, sd ~%.1e) ; ordered pairs %.0f / expected %.0f (ratio %.6f, sd ~%.1e) ; max preimages %d ; saturated %lu ; %lds\n",
           emb, HALF ? 'B' : 'A', zb ? "zero" : "random", NR, DB, (double)img, expimg, img / expimg, sqrt(expimg * exp(-Nd / M)) / expimg,
           s2, exppairs, s2 / exppairs, sqrt(2.0 / exppairs), mx, (unsigned long)sat, (long)(time(0) - t0));
    fflush(stdout); munmap(cnt, 1ull << 32);
    double sl = 0, st = 0;
    for (int k = 0; k < ns; k++) {   // self-map x -> f(x) & DM
        uint32_t x0 = (uint32_t)rnd64() & DM, power = 1, lam = 1, tort = x0, hare = f(x0) & DM;
        while (tort != hare) { if (power == lam) { tort = hare; power <<= 1; lam = 0; } hare = f(hare) & DM; lam++; }
        uint32_t a = x0, b = x0; for (uint32_t i = 0; i < lam; i++) b = f(b) & DM;
        uint32_t mu = 0; while (a != b) { a = f(a) & DM; b = f(b) & DM; mu++; }
        sl += lam; st += mu;
    }
    printf("  rho over %d starts: mean cycle %.0f, mean tail %.0f (across-maps mean sqrt(pi N/8) = %.0f each)\n", ns, sl / ns, st / ns, sqrt(M_PI * Nd / 8));
    return 0;
}
