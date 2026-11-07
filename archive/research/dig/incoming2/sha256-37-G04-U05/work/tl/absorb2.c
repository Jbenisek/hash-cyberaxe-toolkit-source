/* absorb2.c - published pair + absorbable chaining-value difference.  Own code (links traillab's tl_load / tl_compress_ref).
   Validation: published pair (cv, mx, my) gives equal 37-step digests (printed digest).
   Test: member x keeps (cv, mx).  Member y gets cv_y = cv + delta with delta random on the E words only (e,f,g,h = 128 bits) and
   W0..W3 of y re-solved so that rows 0..3 of y equal rows 0..3 of x (the absorption of absorb.c); W4..W15 of y are the published my.
   Then the 37-step digests are compared with the real compression.  Also: how many of the trials have dW0..dW3 (y vs published my) = 0?
   Also the control: delta = 0 must reproduce the printed digest equality. */
#include "src/traillab.h"
#include <string.h>
#include <stdlib.h>
static u32 rr(u64 *s) { *s ^= *s << 13; *s ^= *s >> 7; *s ^= *s << 17; return (u32)(*s >> 20); }
int main(int argc, char **argv) {
  long N = argc > 1 ? atol(argv[1]) : 100000;
  TLModel *M = calloc(1, sizeof *M); if (tl_load("chi/chi37.txt", M, NULL, 0)) { puts("load failed"); return 1; }
  u32 ox[8], oy[8];
  /* published: x = mx (M'), y = my (M) */
  tl_compress_ref(M->cv, M->mx, 37, ox); tl_compress_ref(M->cv, M->my, 37, oy);
  printf("published pair: digests equal %s ; matches printed digest %s\n", memcmp(ox, oy, 32) ? "NO" : "yes", memcmp(ox, M->digest, 32) ? "NO" : "yes");
  u64 s = 0x1234567899ull; long zero = 0, aonly = 0, dw0 = 0; long pc_sum = 0, pc_min = 999;
  for (long t = 0; t < N; t++) {
    u32 cvy[8]; memcpy(cvy, M->cv, 32);
    u32 d[8] = {0}; int nz = 0;
    for (int k = 4; k < 8; k++) { d[k] = (t == 0) ? 0 : rr(&s); cvy[k] += d[k]; nz |= d[k] != 0; }
    /* rows of x from its own CV, rows of y from cvy with W_i solved so that E_i^y = E_i^x ; cv order a b c d e f g h = A-1 A-2 A-3 A-4 E-1 E-2 E-3 E-4 */
    TLTr X, Y; memset(&X, 0, sizeof X); memset(&Y, 0, sizeof Y);
    for (int i = 0; i < 4; i++) { TA(&X, -1 - i) = M->cv[i]; TE(&X, -1 - i) = M->cv[4 + i]; TA(&Y, -1 - i) = cvy[i]; TE(&Y, -1 - i) = cvy[4 + i]; }
    for (int i = 0; i < 16; i++) X.w[i] = M->mx[i];
    for (int i = 0; i < 4; i++) tl_step(&X, i);
    u32 wy[16]; memcpy(wy, M->my, 64);
    for (int i = 0; i < 4; i++) { Y.w[i] = 0; tl_step(&Y, i); u32 e0 = TE(&Y, i); Y.w[i] = TE(&X, i) - e0; wy[i] = Y.w[i]; tl_step(&Y, i); }
    for (int i = 0; i < 4; i++) if (TA(&X, i) != TA(&Y, i) || TE(&X, i) != TE(&Y, i)) { printf("ABSORPTION FAILED t=%ld row %d\n", t, i); return 2; }
    /* y's own W0..W3 differ from x's mx by absorb; x's mx has W0..W5 as printed.  y words W4..15 = published my. */
    tl_compress_ref(cvy, wy, 37, oy);
    int same = !memcmp(ox, oy, 32);
    zero += same;
    if (nz) { int pc = 0; for (int k = 0; k < 8; k++) pc += __builtin_popcount(ox[k] ^ oy[k]); pc_sum += pc; if (pc < pc_min) pc_min = pc; }
    int w0 = 1; for (int i = 0; i < 4; i++) if (wy[i] != M->mx[i]) w0 = 0; dw0 += w0 && nz;
    if (t == 0) printf("control delta=0: y built by absorption equals published digest: %s\n", same ? "yes" : "NO");
  }
  printf("trials %ld (E-word deltas, rows 0..3 identical in every trial by construction, checked): digest collisions %ld ; mean digest popcount difference %.1f ; min %ld ; trials with dW0..dW3 = 0 and delta != 0: %ld\n", N, zero - 1, (double)pc_sum / (N - 1), pc_min, dw0);
  return 0;
}
