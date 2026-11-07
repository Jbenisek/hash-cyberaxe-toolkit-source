// e1filter.c - E1-only census of the one-sided condition that R = 0 forces (RESULT.md section 2):
//   dc2 = E1.c2 A ^ B must be X0 = 91de41aa or ~X0 = 6e21be55.
// Reuses the pkgCG front-line algebra from ../data/gen.c (step CO, step CT up to E1). For each context
// (7 random outer words, random member k) it enumerates the WHOLE cube j < 2^21 (c1 = 02008000 | pdep(j, ~0e09818b)).
//   e1filter <contexts> <seed> <outfile>
// Prints the bit-serial survival counts (dc2 agrees with X0, resp. ~X0, on bits 0..m-1) and writes every hit
// (context, k, j, da2, dc2) to <outfile> as text.
#define main gen_main_unused
#include "../data/gen.c"
#undef main
#include <omp.h>
#include <math.h>
static u64 mix(u64 z) { z += 0x9E3779B97F4A7C15ULL; z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: e1filter <contexts> <seed> <outfile>\n"); return 1; }
    u64 NC = strtoull(argv[1], 0, 0), seed = strtoull(argv[2], 0, 0);
    // constants exactly as gen.c main
    u32 x[4] = {X3, X7, X11, X15}, xb[4] = {X3, X7, X11, X15};
    u32 K = IV[2] + IV[6];
    W4B = (((W4 + K) ^ LEN_A ^ LEN_B) - K); DELTA5 = W4 - W4B;
    gq(&x[0], &x[1], &x[2], &x[3], W4, W13); gq(&xb[0], &xb[1], &xb[2], &xb[3], W4B, W13);
    Y3 = x[0]; Y11 = x[2]; Y3B = xb[0]; Y11B = xb[2];
    if (Y3 != 0x8127C181 || Y11 != 0x7AF77F38 || Y11B - Y11 != 0x0A08818B || DELTA5 != 0xFFFFFFF8) { fprintf(stderr, "constants mismatch\n"); return 2; }
    K2A = K + W4; K2D = ROR(K2A ^ LEN_A, 16); K2C = IV[2] + K2D; K2B = ROR(IV[6] ^ K2C, 12);
    if (!strcmp(argv[1], "check")) {   // e1filter check <inputs.u32> <keys.u32>: recompute da2, dc2 for every stored row
        FILE *fi = fopen(argv[2], "rb"), *fk = fopen(argv[3], "rb"); if (!fi || !fk) { perror("open"); return 4; }
        u32 in[12], ky[8]; u64 n = 0, bad = 0;
        while (fread(in, 4, 12, fi) == 12 && fread(ky, 4, 8, fk) == 8) {
            ctx_t o; u32 e1 = CLASS_VALUE | pdep(in[7], FREE_MASK), Y4 = e1 - Y3; step_co(in, Y4, &o);
            u32 c1 = QVALUE | pdep(in[8], ~QMASK), E1a1 = ROL(c1 - Y11, 16) ^ o.Y12, Y6 = E1a1 - o.Y1 - o.w[12];
            u32 a = o.Y1 + Y6 + o.w[12], d = ROR(o.Y12 ^ a, 16), cc = Y11 + d, b = ROR(Y6 ^ cc, 12);
            u32 a2 = a + b + o.w[5], c2 = cc + ROR(d ^ a2, 8);
            u32 ccB = Y11B + d, bB = ROR(Y6 ^ ccB, 12), a2B = a + bB + o.w[5] + DELTA5, c2B = ccB + ROR(d ^ a2B, 8);
            if ((a2 ^ a2B) != ky[0] || (c2 ^ c2B) != ky[1] || cc != c1) bad++;
            n++;
        }
        printf("check: %llu rows, %llu mismatches of (da2, dc2, c1) against keys.u32\n", (unsigned long long)n, (unsigned long long)bad);
        return bad ? 5 : 0;
    }
    const u32 X0 = 0x91de41aa, X1 = ~X0;
    // precompute pdep table for the cube: c1 = QVALUE | pdep(j, ~QMASK), j < 2^21
    const u32 NJ = 1u << 21; u32 *c1tab = malloc(NJ * 4);
    for (u32 j = 0; j < NJ; j++) c1tab[j] = QVALUE | pdep(j, ~QMASK);
    u64 surv[2][33]; memset(surv, 0, sizeof surv);
    u64 dc1bad = 0, total = 0, hits = 0;
    FILE *fh = fopen(argv[3], "w"); if (!fh) { perror(argv[3]); return 3; }
    fprintf(fh, "# ctx k j da2 dc2  (seed %s)\n", argv[2]);
    #pragma omp parallel
    {
        u64 ls[2][33]; memset(ls, 0, sizeof ls); u64 lbad = 0, ltot = 0;
        #pragma omp for schedule(dynamic, 1)
        for (u64 c = 0; c < NC; c++) {
            u64 s0 = mix(seed ^ (c * 0x100000001B3ULL));
            u32 ow[7]; for (int i = 0; i < 7; i++) { s0 = mix(s0); ow[i] = (u32)(s0 >> 32); }
            s0 = mix(s0); u32 k = (u32)(s0 >> 45); // 19 bits
            ctx_t o; u32 e1 = CLASS_VALUE | pdep(k, FREE_MASK), Y4 = e1 - Y3;
            step_co(ow, Y4, &o);
            const u32 Y1 = o.Y1, Y12 = o.Y12, w12 = o.w[12], w5 = o.w[5], w5b = o.w[5] + DELTA5;
            for (u32 j = 0; j < NJ; j++) {
                u32 c1 = c1tab[j];
                u32 E1a1 = ROL(c1 - Y11, 16) ^ Y12, Y6 = E1a1 - Y1 - w12;
                // side A
                u32 a = Y1 + Y6 + w12, d = ROR(Y12 ^ a, 16), cc = Y11 + d, b = ROR(Y6 ^ cc, 12);
                u32 a2 = a + b + w5, d2 = ROR(d ^ a2, 8), c2 = cc + d2;
                // side B
                u32 aB = a, dB = d, ccB = Y11B + dB, bB = ROR(Y6 ^ ccB, 12);
                u32 a2B = aB + bB + w5b, d2B = ROR(dB ^ a2B, 8), c2B = ccB + d2B;
                if ((cc ^ ccB) != QMASK) lbad++;
                u32 dc2 = c2 ^ c2B;
                // survival: number of low bits on which dc2 agrees with X0 / X1
                u32 m0 = dc2 ^ X0, m1 = dc2 ^ X1;
                int l0 = m0 ? __builtin_ctz(m0) : 32, l1 = m1 ? __builtin_ctz(m1) : 32;
                ls[0][l0]++; ls[1][l1]++;
                if (l0 == 32 || l1 == 32) {
                    #pragma omp critical
                    { fprintf(fh, "%llu %05x %06x %08x %08x\n", (unsigned long long)c, k, j, a2 ^ a2B, dc2); hits++; }
                }
            }
            ltot += NJ;
        }
        #pragma omp critical
        { for (int s = 0; s < 2; s++) for (int m = 0; m <= 32; m++) surv[s][m] += ls[s][m]; dc1bad += lbad; total += ltot; }
    }
    fclose(fh);
    printf("e1filter contexts %llu x 2^21 cube = %llu samples (log2 %.2f), seed %s, threads %d\n", (unsigned long long)NC,
           (unsigned long long)total, log2((double)total), argv[2], omp_get_max_threads());
    printf("dc1 != 0e09818b on %llu samples (expect 0)\n", (unsigned long long)dc1bad);
    printf("hits dc2 in {%08x, %08x}: %llu  -> log2 P = %.3f\n", X0, X1, (unsigned long long)hits, hits ? log2((double)hits / total) : -INFINITY);
    for (int s = 0; s < 2; s++) {
        printf("survival for target %08x: m = bits matched from bit 0; count(>= m), log2 fraction, step log2\n", s ? X1 : X0);
        u64 ge = total; double prev = 0;
        for (int m = 0; m <= 32; m++) {
            double lf = ge ? log2((double)ge / total) : -INFINITY;
            printf("  m=%2d  %14llu  %8.3f  %+7.3f\n", m, (unsigned long long)ge, lf, m ? lf - prev : 0.0);
            prev = lf; ge -= surv[s][m];
        }
    }
    return 0;
}
