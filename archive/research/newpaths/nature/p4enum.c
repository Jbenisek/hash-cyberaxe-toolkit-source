// p4enum.c - enumerate every carry-free colliding characteristic inside the period-K subspace (K = 1, 2, 4)
// of 2-round BLAKE3 (w = 32) and score it with the Lipmaa-Moriai weight of every addition:
//   weight(alpha, beta -> alpha^beta) = popcount((alpha|beta) & 0x7fffffff) = (32/K)*hw(p) - p_{31 mod K}
// Input: pK_basis.txt from period4.py.  Gray-code walk over all 2^dim - 1 nonzero kernel vectors.
// Build: gcc -O3 -march=native -o p4enum p4enum.c
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

int main(int argc, char **argv) {
    const char *fn = argc > 1 ? argv[1] : "p4_basis.txt";
    FILE *f = fopen(fn, "r"); if (!f) { perror(fn); return 1; }
    int K, dim, nadd; if (fscanf(f, "%d %d %d", &K, &dim, &nadd) != 3) return 1;
    int *rnd = malloc(sizeof(int) * nadd); for (int i = 0; i < nadd; i++) if (fscanf(f, "%d", &rnd[i]) != 1) return 1;
    // packed nibbles: addition i -> word i/16, shift 4*(i%16)
    uint64_t (*A)[6] = calloc(dim, sizeof *A), (*B)[6] = calloc(dim, sizeof *B); int (*msg)[16] = calloc(dim, sizeof *msg);
    for (int k = 0; k < dim; k++) {
        for (int i = 0; i < 16; i++) if (fscanf(f, "%d", &msg[k][i]) != 1) return 1;
        char bar[4]; if (fscanf(f, "%3s", bar) != 1) return 1;
        for (int i = 0; i < nadd; i++) { int pa, pb; if (fscanf(f, "%d,%d", &pa, &pb) != 2) return 1;
            A[k][i / 16] |= (uint64_t)pa << (4 * (i % 16)); B[k][i / 16] |= (uint64_t)pb << (4 * (i % 16)); }
    }
    fclose(f);
    for (int i = 0; i < nadd; i++) if (rnd[i] != (i < 48 ? 0 : 1)) { printf("unexpected round layout\n"); return 1; }
    int per = 32 / K, msbbit = 31 % K;
    static uint16_t wt16[65536];
    for (int c = 0; c < 65536; c++) { int s = 0; for (int n = 0; n < 4; n++) { int p = (c >> (4 * n)) & 15; s += per * __builtin_popcount(p) - ((p >> msbbit) & 1); } wt16[c] = s; }
    uint64_t a[6] = {0}, b[6] = {0};
    int bestW = 1 << 30, bestW1 = 1 << 30, bestW0 = 1 << 30; uint64_t gW = 0, gW1 = 0; int bw_w1 = 0, bw1_w = 0;
    static uint64_t hist1[2000], histW[3000];
    uint64_t N = 1ull << dim;
    for (uint64_t i = 1; i < N; i++) {
        int k = __builtin_ctzll(i);
        for (int j = 0; j < 6; j++) { a[j] ^= A[k][j]; b[j] ^= B[k][j]; }
        int w0 = 0, w1 = 0;
        for (int j = 0; j < 3; j++) { uint64_t o = a[j] | b[j]; w0 += wt16[o & 0xffff] + wt16[(o >> 16) & 0xffff] + wt16[(o >> 32) & 0xffff] + wt16[o >> 48]; }
        for (int j = 3; j < 6; j++) { uint64_t o = a[j] | b[j]; w1 += wt16[o & 0xffff] + wt16[(o >> 16) & 0xffff] + wt16[(o >> 32) & 0xffff] + wt16[o >> 48]; }
        int W = w0 + w1; uint64_t g = i ^ (i >> 1);
        if (w1 < 2000) hist1[w1]++; if (W < 3000) histW[W]++;
        if (W < bestW) { bestW = W; gW = g; bw_w1 = w1; }
        if (w1 < bestW1 || (w1 == bestW1 && W < bw1_w)) { bestW1 = w1; gW1 = g; bw1_w = W; }
        if (w0 < bestW0) bestW0 = w0;
    }
    printf("period-%d kernel dim %d: %llu nonzero colliding carry-free characteristics\n", K, dim, (unsigned long long)(N - 1));
    printf("  best total W = %d (W1 %d) ; best round-1 W1 = %d (total %d) ; best W0 alone %d\n", bestW, bw_w1, bestW1, bw1_w, bestW0);
    uint64_t gs[2] = {gW, gW1}; const char *nm[2] = {"bestW", "bestW1"};
    for (int t = 0; t < 2; t++) {
        int md[16] = {0}; for (int k = 0; k < dim; k++) if ((gs[t] >> k) & 1) for (int q = 0; q < 16; q++) md[q] ^= msg[k][q];
        printf("  %s message pattern (per word, %d-bit pattern):", nm[t], K); for (int q = 0; q < 16; q++) printf(" %x", md[q]); printf("\n");
    }
    printf("  lowest W1 values (count):"); int shown = 0; for (int w = 0; w < 2000 && shown < 8; w++) if (hist1[w]) { printf(" %d:%llu", w, (unsigned long long)hist1[w]); shown++; } printf("\n");
    printf("  lowest W values (count):"); shown = 0; for (int w = 0; w < 3000 && shown < 8; w++) if (histW[w]) { printf(" %d:%llu", w, (unsigned long long)histW[w]); shown++; } printf("\n");
    return 0;
}
