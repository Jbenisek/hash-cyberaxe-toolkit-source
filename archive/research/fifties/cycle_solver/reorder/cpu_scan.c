#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#define ROL(x,n) (((x) << (n)) | ((x) >> (32 - (n))))
static inline uint32_t loopc(uint32_t g, const uint32_t *P, uint32_t *c0b1) {
  uint32_t v_C1_d1 = (ROL(P[6],16) ^ ROL(g,16));
  uint32_t v_C1_c1 = (0x00000000u +P[10] +v_C1_d1);
  uint32_t v_Y13 = (0x00000000u -v_C1_c1 +P[12]);
  uint32_t v_Y1 = ROL((v_Y13 ^ ROL(v_C1_d1,24)),8);
  uint32_t v_C1_b1 = (ROL(P[8],20) ^ ROL(v_C1_c1,20));
  uint32_t v_w10 = (0x00000000u -g -v_C1_b1 +v_Y1);
  uint32_t v_D1_a1 = (0x00000000u +P[1] +P[4] +v_w10);
  uint32_t v_D1_d1 = ROL((v_D1_a1 ^ P[3]),16);
  uint32_t v_D1_c1 = (0x00000000u +P[2] +v_D1_d1);
  uint32_t v_X12 = (0x44036000u -v_D1_c1);
  uint32_t v_X1 = (ROL(v_X12,8) ^ v_D1_d1);
  uint32_t v_w3 = (0x00000000u -v_X1 -P[8] +g);
  uint32_t v_K1_a1 = (0x00000000u +P[1] -P[0] -v_w3);
  uint32_t v_w2 = (0xa992e8efu +v_K1_a1);
  uint32_t v_C0_a1 = (0x00000000u +P[7] +v_w2 +P[5]);
  uint32_t v_C0_d1 = ROL((v_X12 ^ v_C0_a1),16);
  uint32_t v_C0_c1 = (0x00000000u +P[9] +v_C0_d1);
  uint32_t v_C0_b1 = (ROL(P[7],20) ^ ROL(v_C0_c1,20));
  uint32_t v_Y8 = (ROL(P[11],7) ^ v_C0_b1);
  uint32_t v_Y12 = (0x00000000u +v_Y8 -v_C0_c1);
  uint32_t v_Y0 = (ROL(v_Y12,8) ^ v_C0_d1);
  *c0b1 = v_C0_b1;
  return (0x00000000u -v_Y0 +v_C0_b1 +P[13] +v_C0_a1);
}
static inline uint32_t loopk(uint32_t g, const uint32_t *P) {
  uint32_t v_C1_d1 = (ROL(P[6],16) ^ ROL(g,16));
  uint32_t v_C1_c1 = (0x00000000u +P[10] +v_C1_d1);
  uint32_t v_Y13 = (0x00000000u -v_C1_c1 +P[12]);
  uint32_t v_Y1 = ROL((v_Y13 ^ ROL(v_C1_d1,24)),8);
  uint32_t v_C1_b1 = (ROL(P[8],20) ^ ROL(v_C1_c1,20));
  uint32_t v_w10 = (0x00000000u -g -v_C1_b1 +v_Y1);
  uint32_t v_D1_a1 = (0x00000000u +P[1] +P[4] +v_w10);
  uint32_t v_D1_d1 = ROL((v_D1_a1 ^ P[3]),16);
  uint32_t v_D1_c1 = (0x00000000u +P[2] +v_D1_d1);
  uint32_t v_X12 = (0x44036000u -v_D1_c1);
  uint32_t v_X1 = (ROL(v_X12,8) ^ v_D1_d1);
  uint32_t v_w3 = (0x00000000u -v_X1 -P[8] +g);
  uint32_t v_K1_a1 = (0x00000000u +P[1] -P[0] -v_w3);
  uint32_t v_w2 = (0xa992e8efu +v_K1_a1);
  uint32_t v_C0_a1 = (0x00000000u +P[7] +v_w2 +P[5]);
  uint32_t v_C0_d1 = ROL((v_X12 ^ v_C0_a1),16);
  uint32_t v_C0_c1 = (0x00000000u +P[9] +v_C0_d1);
  uint32_t v_C0_b1 = (ROL(P[7],20) ^ ROL(v_C0_c1,20));
  uint32_t v_Y8 = (ROL(P[11],7) ^ v_C0_b1);
  uint32_t v_Y12 = (0x00000000u +v_Y8 -v_C0_c1);
  uint32_t v_Y0 = (ROL(v_Y12,8) ^ v_C0_d1);
  
  return (0x00000000u -v_Y0 +v_C0_b1 +P[13] +v_C0_a1);
}
int main(int argc, char **argv) {
  FILE *f = fopen(argv[1], "r"); FILE *o = fopen(argv[2], "w");
  int lo = atoi(argv[3]), hi = atoi(argv[4]);
  uint32_t P[14]; int id;
  while (fscanf(f, "%d", &id) == 1) {
    for (int i = 0; i < 14; i++) fscanf(f, "%x", &P[i]);
    if (id < lo || id >= hi) continue;
    unsigned n = 0; uint32_t r[64], rb[64];
    static uint32_t buf[4096];
    for (uint64_t base = 0; base < (1ull << 32); base += 4096) {
      for (uint32_t j = 0; j < 4096; j++) buf[j] = loopk((uint32_t)base + j, P);
      for (uint32_t j = 0; j < 4096; j++) if (buf[j] == 0u) { uint32_t cb, g = (uint32_t)base + j; loopc(g, P, &cb); if (n < 64) { r[n] = g; rb[n] = cb; } n++; }
    }
    fprintf(o, "%d %u", id, n);
    for (unsigned i = 0; i < n && i < 64; i++) fprintf(o, " %08x:%08x", r[i], rb[i]);
    fprintf(o, "\n"); fflush(o);
  }
  fclose(o); return 0;
}
