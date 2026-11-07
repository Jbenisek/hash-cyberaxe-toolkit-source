// local38.c - scout2-4: exact local counts behind the relaxed-SMC gains (r38 characteristic, filed pkgR38a data).
//  (1) W23: words w with the cells of W23 (x-values, XOR pattern of w vs w - dW23, the 4 two-bit conditions) versus
//      words with only the modular condition that matters downstream, s1(w) - s1(w - dW23) = published ds1(W23)
//      (it fixes dW25; dW30 = dW23 + ds0(W15) holds for every w).
//  (2) W25: cells ('n' at bit 29 and the 3 two-bit conditions) versus s1(w) - s1(w - dW25) = published ds1(W25)
//      (it fixes dW27).
//  (3) Row 17 for the first K words of G: over all 2^32 values of E17^x, the number with every cell of row 17 AND the
//      published modular differences of row 18, versus the number with the row-18 modular differences only.
// usage: local38 K
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "consts38.h"
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline uint32_t S0(uint32_t x){return ROR(x,2)^ROR(x,13)^ROR(x,22);}
static inline uint32_t S1(uint32_t x){return ROR(x,6)^ROR(x,11)^ROR(x,25);}
static inline uint32_t s1(uint32_t x){return ROR(x,17)^ROR(x,19)^(x>>10);}
static inline uint32_t Ch(uint32_t x,uint32_t y,uint32_t z){return (x&y)^(~x&z);}
static inline uint32_t Mj(uint32_t x,uint32_t y,uint32_t z){return (x&y)^(x&z)^(y&z);}
static int twobit_w(int row, uint32_t w) {   // two-bit conditions with both words W_row (member x)
    for (int j = 0; j < NX; j++) if (XROW[j] == row && XK1[j] == 2 && XK2[j] == 2 && XI1[j] == row && XI2[j] == row)
        if ((((w >> XB1[j]) ^ (w >> XB2[j])) & 1) != (uint32_t)XNE[j]) return 0;
    return 1;
}
static void wcount(int row) {
    uint32_t dW = PXW[row] - PYW[row], t = s1(PXW[row]) - s1(PYW[row]);
    uint64_t nc = 0, nr = 0, nb = 0;
    for (uint64_t v = 0; v < (1ULL << 32); v++) {
        uint32_t w = (uint32_t)v, wy = w - dW;
        int c = (w & CM[2][row]) == CV[2][row] && (w ^ wy) == CD[2][row] && twobit_w(row, w);
        int r = (uint32_t)(s1(w) - s1(wy)) == t;
        nc += c; nr += r; nb += c && r;
    }
    printf("W%d: dW %08x target ds1 %08x  cells %llu (2^%.4f)  relaxed %llu (2^%.4f)  cells&relaxed %llu  ratio %.4f\n",
           row, dW, t, (unsigned long long)nc, __builtin_log2((double)nc), (unsigned long long)nr, __builtin_log2((double)nr),
           (unsigned long long)nb, (double)nr / (double)nc);
}
int main(int argc, char **argv) {
    int K = argc > 1 ? atoi(argv[1]) : 2;
    wcount(23); wcount(25);
    // row 17 from row 16 = G word g (rows 12..15 published)
    uint32_t A[2][NR+4], E[2][NR+4], W[2][NR+4];   // A, E: index i+4
    for (int m = 0; m < 2; m++) for (int i = -4; i < NR; i++) { A[m][i+4] = m ? PYA[i+4] : PXA[i+4]; E[m][i+4] = m ? PYE[i+4] : PXE[i+4]; }
    for (int m = 0; m < 2; m++) for (int i = 0; i < NR; i++) W[m][i] = m ? PYW[i] : PXW[i];
#define a(m,i) A[m][(i)+4]
#define e(m,i) E[m][(i)+4]
    uint32_t tA18 = PXA[22] - PYA[22], tE18 = PXE[22] - PYE[22], tA17 = PXA[21] - PYA[21], tE17 = PXE[21] - PYE[21];
    for (int g = 0; g < K && g < 32; g++) {
        for (int m = 0; m < 2; m++) {
            W[m][16] = m ? GW[g] - 0x20000000u : GW[g];
            e(m,16) = a(m,12) + e(m,12) + S1(e(m,15)) + Ch(e(m,15), e(m,14), e(m,13)) + KK[16] + W[m][16];
            a(m,16) = e(m,16) - a(m,12) + S0(a(m,15)) + Mj(a(m,15), a(m,14), a(m,13));
        }
        uint32_t cx = a(0,13) + e(0,13) + S1(e(0,16)) + Ch(e(0,16), e(0,15), e(0,14)) + KK[17];
        uint32_t cy = a(1,13) + e(1,13) + S1(e(1,16)) + Ch(e(1,16), e(1,15), e(1,14)) + KK[17];
        uint32_t dw17 = (s1(W[0][15]) - s1(W[1][15])) + (W[0][10] - W[1][10]);
        uint32_t abx = 0u - a(0,13) + S0(a(0,16)) + Mj(a(0,16), a(0,15), a(0,14)), aby = 0u - a(1,13) + S0(a(1,16)) + Mj(a(1,16), a(1,15), a(1,14));
        uint32_t dW18 = (s1(W[0][16]) - s1(W[1][16])) + (W[0][11] - W[1][11]);
        uint32_t dA14 = a(0,14) - a(1,14), dpre = dA14 + (e(0,14) - e(1,14)) + dW18;
        uint64_t nrel = 0, nboth = 0;
        for (uint64_t v = 0; v < (1ULL << 32); v++) {
            uint32_t ex = (uint32_t)v, wx = ex - cx, wy = wx - dw17, ey = cy + wy, ax = ex + abx, ay = ey + aby;
            if (ex - ey != tE17 || ax - ay != tA17) { fprintf(stderr, "row 17 modular differences not fixed\n"); return 1; }
            uint32_t dE = dpre + (S1(ex) - S1(ey)) + (Ch(ex, e(0,16), e(0,15)) - Ch(ey, e(1,16), e(1,15)));
            if (dE != tE18) continue;
            uint32_t dA = dE - dA14 + (S0(ax) - S0(ay)) + (Mj(ax, a(0,16), a(0,15)) - Mj(ay, a(1,16), a(1,15)));
            if (dA != tA18) continue;
            nrel++;
            // every cell of row 17 (A, E, '+', W) and the two-bit conditions keyed at row 17 (member x)
            if ((ax & CM[0][17]) != CV[0][17] || (ax ^ ay) != CD[0][17]) continue;
            if ((ex & CM[1][17]) != CV[1][17] || (ex ^ ey) != CD[1][17]) continue;
            if ((ex ^ e(0,16)) & CPL[17]) continue;
            if ((wx & CM[2][17]) != CV[2][17] || (wx ^ wy) != CD[2][17]) continue;
            int ok = 1;
            for (int j = 0; j < NX && ok; j++) if (XROW[j] == 17) {
                uint32_t v1 = XK1[j] == 0 ? (XI1[j] == 17 ? ax : a(0, XI1[j])) : XK1[j] == 1 ? (XI1[j] == 17 ? ex : e(0, XI1[j])) : (XI1[j] == 17 ? wx : W[0][XI1[j]]);
                uint32_t v2 = XK2[j] == 0 ? (XI2[j] == 17 ? ax : a(0, XI2[j])) : XK2[j] == 1 ? (XI2[j] == 17 ? ex : e(0, XI2[j])) : (XI2[j] == 17 ? wx : W[0][XI2[j]]);
                if ((((v1 >> XB1[j]) ^ (v2 >> XB2[j])) & 1) != (uint32_t)XNE[j]) ok = 0;
            }
            nboth += ok;
        }
        printf("row 17, W16 = %08x: E17 values with row-18 modular differences %llu (2^%.4f); with every row-17 cell too %llu (2^%.4f); ratio %.4f\n",
               GW[g], (unsigned long long)nrel, __builtin_log2((double)nrel), (unsigned long long)nboth, __builtin_log2((double)nboth), (double)nrel / (double)nboth);
        fflush(stdout);
    }
    return 0;
}
