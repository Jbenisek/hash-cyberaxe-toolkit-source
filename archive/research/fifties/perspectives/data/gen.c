// gen.c - samples of the front-line residual of 2-round BLAKE3 (pkgCG family: frontline.py step CO + step CT).
// One sample = 7 outer words (C0.d1 D2.a1 D2.b1 S11 S4 X9 w6), member k (19 bits, Y4 = e1 - Y3), cube index j
// (21 bits, E1.c1 = 02008000 | pdep(j, ~0e09818b)). Blocks A (55 bytes) and B (63 bytes) at counter t, flags 3,
// both compressed with a plain 2-round BLAKE3 compression. Digest words 0,2,5,7 are equal for every sample;
// the residual R = digest words (1,3,4,6) XOR = K1 XOR K3 (sol_answer_D5_split.md section 1).
//   gen rand <outdir> <N> <seed>            N independent samples (fresh outer words, k, j each)
//   gen ctx  <outdir> <C> <Mk> <Jc> <seed>  C contexts x Mk members x Jc cube indices (random, with replacement)
// Files written in <outdir> (little-endian u32, row-major, one row per sample):
//   inputs.u32  12: ow0..ow6, k, j, Y4, c1, t
//   einputs.u32  9: Y1 Y6 Y12 w12 w5 | Y4 Y9 Y14 w8        (side A; side B differs only by Y3', Y11', w4', w5+DELTA5)
//   dig.u32      8: digest A words 1,3,4,6 | digest B words 1,3,4,6
//   eout.u32    16: E1 A (a2 b2 c2 d2) | E1 B | E3 A (e2 f2 g2 h2) | E3 B   (round-2 diagonal outputs)
//   emid.u32    16: E1 A (a1 b1 c1 d1) | E1 B | E3 A (e1 f1 g1 h1) | E3 B   (half-G values)
//   keys.u32     8: K1 (1,3,4,6) | K3 (1,3,4,6)
//   res.u32      4: R (1,3,4,6)
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
typedef uint32_t u32; typedef uint64_t u64;
#define ROR(x, n) ((u32)(((x) >> (n)) | ((x) << (32 - (n)))))
#define ROL(x, n) ROR((x), 32 - (n))
static const u32 IV[8] = {0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19};
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
static const u32 X3 = 0x29D4FA98, X7 = 0xBEE3AF28, X11 = 0x44036000, X15 = 0x40C58500, W4 = 0x97475638, W13 = 0x0007C006;
static const u32 LEN_A = 55, LEN_B = 63, FLAGS = 3, ETA = 0x830303CF;
static const u32 CLASS_VALUE = 0x030C0303, FREE_MASK = 0xFC307CFC, QMASK = 0x0E09818B, QVALUE = 0x02008000;
static u32 Y3, Y11, Y3B, Y11B, W4B, DELTA5, K2A, K2B, K2C, K2D;

static void gq(u32 *a, u32 *b, u32 *c, u32 *d, u32 x, u32 y) {
    *a = *a + *b + x; *d = ROR(*d ^ *a, 16); *c = *c + *d; *b = ROR(*b ^ *c, 12);
    *a = *a + *b + y; *d = ROR(*d ^ *a, 8); *c = *c + *d; *b = ROR(*b ^ *c, 7);
}
static void G(u32 *v, int a, int b, int c, int d, u32 x, u32 y) { gq(&v[a], &v[b], &v[c], &v[d], x, y); }
// half G: values after the first half (a1 b1 c1 d1) and after the second (a2 b2 c2 d2)
static void ghalf(u32 a, u32 b, u32 c, u32 d, u32 x, u32 y, u32 mid[4], u32 out[4]) {
    a = a + b + x; d = ROR(d ^ a, 16); c = c + d; b = ROR(b ^ c, 12);
    mid[0] = a; mid[1] = b; mid[2] = c; mid[3] = d;
    a = a + b + y; d = ROR(d ^ a, 8); c = c + d; b = ROR(b ^ c, 7);
    out[0] = a; out[1] = b; out[2] = c; out[3] = d;
}
// 2-round compression; ys = state after the round-2 column step; returns final v (16 words)
static void compress2(const u32 w[16], u32 t, u32 blen, u32 flags, u32 v[16], u32 ys[16]) {
    u32 m[16], m2[16];
    for (int i = 0; i < 8; i++) v[i] = IV[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IV[i];
    v[12] = t; v[13] = 0; v[14] = blen; v[15] = flags;
    memcpy(m, w, 64);
    for (int r = 0; r < 2; r++) {
        G(v, 0, 4, 8, 12, m[0], m[1]); G(v, 1, 5, 9, 13, m[2], m[3]); G(v, 2, 6, 10, 14, m[4], m[5]); G(v, 3, 7, 11, 15, m[6], m[7]);
        if (r == 1) memcpy(ys, v, 64);
        G(v, 0, 5, 10, 15, m[8], m[9]); G(v, 1, 6, 11, 12, m[10], m[11]); G(v, 2, 7, 8, 13, m[12], m[13]); G(v, 3, 4, 9, 14, m[14], m[15]);
        for (int i = 0; i < 16; i++) m2[i] = m[PERM[i]];
        memcpy(m, m2, 64);
    }
}
static u32 pdep(u32 x, u32 mask) { u32 r = 0; int n = 0; for (int i = 0; i < 32; i++) if (mask >> i & 1) { r |= (x >> n & 1) << i; n++; } return r; }
static u64 sm;
static u64 next64(void) { u64 z = (sm += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static u32 next32(void) { return (u32)(next64() >> 32); }

typedef struct {   // step CO context words that step CT and the checks read
    u32 Y0, Y1, Y5, Y8, Y9, Y12, Y13, Y4, e1, w[16], C2a1, C2b1, C2c1, C2d1, K0b1, K0d1, S0;
} ctx_t;
static void step_co(const u32 ow[7], u32 Y4, ctx_t *o) {
    u32 C0d1 = ow[0], D2a1 = ow[1], D2b1 = ow[2], S11 = ow[3], S4 = ow[4], X9 = ow[5], w6 = ow[6];
    u32 X2 = D2a1 + D2b1 + W13, X8 = ROL(X7, 7) ^ D2b1, C0c1 = X8 + C0d1;
    u32 K3a1 = IV[3] + IV[7] + w6, K3d1 = ROR(K3a1 ^ FLAGS, 16), K3c1 = IV[3] + K3d1;
    u32 S15 = S11 - K3c1, S3 = ROL(S15, 8) ^ K3d1, K3b1 = ROR(IV[7] ^ K3c1, 12), D3a1 = S3 + S4;
    u32 S7 = ROR(K3b1 ^ S11, 7), D3b1 = X3 - D3a1, D2c1 = ROL(D2b1, 12) ^ S7, D3c1 = ROL(D3b1, 12) ^ S4;
    u32 X4 = ROR(D3b1 ^ X9, 7), X13 = X8 - D2c1, X14 = X9 - D3c1, C0b1 = ROR(X4 ^ C0c1, 12);
    u32 D2d1 = ROL(X13, 8) ^ X2, D3d1 = ROL(X14, 8) ^ X3, Y8 = ROL(Y4, 7) ^ C0b1, S13 = ROL(D2d1, 16) ^ D2a1;
    u32 S9 = D3c1 - D3d1, Y12 = Y8 - C0c1, K1c1 = S9 - S13, Y0 = ROL(Y12, 8) ^ C0d1, K1d1 = K1c1 - IV[1];
    u32 C0a1 = Y0 - C0b1 - w6, K1a1 = ROL(K1d1, 16), w2 = K1a1 - IV[1] - IV[5], X0 = C0a1 - X4 - w2;
    u32 S14 = ROL(D3d1, 16) ^ D3a1, K1b1 = ROR(IV[5] ^ K1c1, 12), S10 = K2C + S14, D0d1 = ROL(X15, 8) ^ X0;
    u32 S5 = ROR(K1b1 ^ S9, 7), D0c1 = S10 + D0d1, D0b1 = ROR(S5 ^ D0c1, 12), X10 = D0c1 + X15;
    u32 X5 = ROR(D0b1 ^ X10, 7), S1 = ROL(S13, 8) ^ K1d1, w3 = S1 - K1a1 - K1b1, X12 = ROL(C0d1, 16) ^ C0a1;
    u32 D1c1 = X11 - X12, D1d1 = D1c1 - S11, S8 = D2c1 - D2d1, K0b1 = ROL(S4, 7) ^ S8, S2 = ROL(S14, 8) ^ K2D;
    u32 S6 = ROR(K2B ^ S10, 7), X1 = ROL(X12, 8) ^ D1d1, K0c1 = ROL(K0b1, 12) ^ IV[4], D1b1 = ROR(S6 ^ D1c1, 12);
    u32 C1a1 = X1 + X5 + w3, S12 = S8 - K0c1, w7 = S3 - K3a1 - K3b1, X6 = ROR(D1b1 ^ X11, 7);
    u32 C1d1 = ROR(X13 ^ C1a1, 16), D1a1 = ROL(D1d1, 16) ^ S12, C1c1 = X9 + C1d1, C2a1 = X2 + X6 + w7;
    u32 w10 = D1a1 - S1 - S6, C1b1 = ROR(X5 ^ C1c1, 12), C2d1 = ROR(X14 ^ C2a1, 16), w12 = D2a1 - S2 - S7;
    u32 Y1 = C1a1 + C1b1 + w10, C2c1 = X10 + C2d1, Y13 = ROR(C1d1 ^ Y1, 8), C2b1 = ROR(X6 ^ C2c1, 12);
    u32 K0d1 = K0c1 - IV[0], Y9 = C1c1 + Y13, S0 = ROL(S12, 8) ^ K0d1, D0a1 = ROL(D0d1, 16) ^ S15;
    u32 w8 = D0a1 - S0 - S5, w5 = S2 - K2A - K2B, w9 = X0 - D0a1 - D0b1, w11 = X1 - D1a1 - D1b1;
    u32 Y5 = ROR(C1b1 ^ Y9, 7);
    memset(o, 0, sizeof *o);
    o->Y0 = Y0; o->Y1 = Y1; o->Y5 = Y5; o->Y8 = Y8; o->Y9 = Y9; o->Y12 = Y12; o->Y13 = Y13; o->Y4 = Y4; o->e1 = Y3 + Y4;
    o->C2a1 = C2a1; o->C2b1 = C2b1; o->C2c1 = C2c1; o->C2d1 = C2d1; o->K0b1 = K0b1; o->K0d1 = K0d1; o->S0 = S0;
    o->w[2] = w2; o->w[3] = w3; o->w[4] = W4; o->w[5] = w5; o->w[6] = w6; o->w[7] = w7; o->w[8] = w8; o->w[9] = w9;
    o->w[10] = w10; o->w[11] = w11; o->w[12] = w12; o->w[13] = W13; o->w[14] = 0; o->w[15] = 0;
}
static u64 fails[8], made, skipped;
static const char *FAILNAME[8] = {"Y state A", "Y state B", "words 0,2,5,7", "E1/E3 vs final state", "c1/h1/dh1=eta", "R = K1^K3", "t>>32 or byte tail", "unused"};
static FILE *fo[7];
static const char *FNAME[7] = {"inputs.u32", "einputs.u32", "dig.u32", "eout.u32", "emid.u32", "keys.u32", "res.u32"};
// one sample; returns 0 when t = 0 (not a front-line instance)
static int sample(const u32 ow[7], u32 k, u32 j) {
    ctx_t o; u32 e1 = CLASS_VALUE | pdep(k, FREE_MASK), Y4 = e1 - Y3, c1 = QVALUE | pdep(j, ~QMASK);
    step_co(ow, Y4, &o);
    // step CT
    u32 E1a1 = ROL(c1 - Y11, 16) ^ o.Y12, Y6 = E1a1 - o.Y1 - o.w[12], Y10 = ROL(Y6, 7) ^ o.C2b1, Y14 = Y10 - o.C2c1;
    u32 Y2 = ROL(Y14, 8) ^ o.C2d1, E3h1 = ROR(Y14 ^ o.e1, 16), w0 = Y2 - o.C2a1 - o.C2b1, K0a1 = IV[0] + IV[4] + w0;
    u32 t = ROL(o.K0d1, 16) ^ K0a1, w1 = o.S0 - K0a1 - o.K0b1;
    if (t == 0) { skipped++; return 0; }
    u32 wa[16], wb[16], va[16], vb[16], ya[16], yb[16];
    memcpy(wa, o.w, 64); wa[0] = w0; wa[1] = w1;
    memcpy(wb, wa, 64); wb[4] = W4B; wb[5] = wa[5] + DELTA5;
    if ((wa[13] >> 24) || wa[14] || wa[15]) fails[6]++;
    compress2(wa, t, LEN_A, FLAGS, va, ya); compress2(wb, t, LEN_B, FLAGS, vb, yb);
    u32 pred[16] = {o.Y0, o.Y1, Y2, Y3, Y4, o.Y5, Y6, 0, o.Y8, o.Y9, Y10, Y11, o.Y12, o.Y13, Y14, 0};
    int bad = 0; for (int i = 0; i < 16; i++) if (i != 7 && i != 15 && ya[i] != pred[i]) bad = 1;
    if (bad) fails[0]++;
    bad = 0; for (int i = 0; i < 16; i++) { u32 p = i == 3 ? Y3B : i == 11 ? Y11B : ya[i]; if (yb[i] != p) bad = 1; }
    if (bad) fails[1]++;
    u32 da[8], db[8]; for (int i = 0; i < 8; i++) { da[i] = va[i] ^ va[i + 8]; db[i] = vb[i] ^ vb[i + 8]; }
    if (da[0] != db[0] || da[2] != db[2] || da[5] != db[5] || da[7] != db[7]) fails[2]++;
    // E1 = G(Y1,Y6,Y11,Y12; w12,w5), E3 = G(Y3,Y4,Y9,Y14; w15,w8): round-2 message words after one permutation
    u32 e1m[2][4], e1o[2][4], e3m[2][4], e3o[2][4];
    u32 *Wv[2] = {wa, wb}, *Yv[2] = {ya, yb}, *Vv[2] = {va, vb};
    for (int s = 0; s < 2; s++) {
        u32 *y = Yv[s], *w = Wv[s], *v = Vv[s];
        ghalf(y[1], y[6], y[11], y[12], w[12], w[5], e1m[s], e1o[s]);
        ghalf(y[3], y[4], y[9], y[14], w[15], w[8], e3m[s], e3o[s]);
        if (e1o[s][0] != v[1] || e1o[s][1] != v[6] || e1o[s][2] != v[11] || e1o[s][3] != v[12] ||
            e3o[s][0] != v[3] || e3o[s][1] != v[4] || e3o[s][2] != v[9] || e3o[s][3] != v[14]) fails[3]++;
    }
    if (e1m[0][2] != c1 || e3m[0][3] != E3h1 || (e3m[0][3] ^ e3m[1][3]) != ETA) fails[4]++;
    // K1 (1,3,4,6) = (da2, dc2, dd2, db2); K3 (1,3,4,6) = (dg2, de2, df2, dh2)
    u32 K1[4] = {e1o[0][0] ^ e1o[1][0], e1o[0][2] ^ e1o[1][2], e1o[0][3] ^ e1o[1][3], e1o[0][1] ^ e1o[1][1]};
    u32 K3[4] = {e3o[0][2] ^ e3o[1][2], e3o[0][0] ^ e3o[1][0], e3o[0][1] ^ e3o[1][1], e3o[0][3] ^ e3o[1][3]};
    static const int IDX[4] = {1, 3, 4, 6};
    u32 R[4]; for (int i = 0; i < 4; i++) { R[i] = da[IDX[i]] ^ db[IDX[i]]; if (R[i] != (K1[i] ^ K3[i])) fails[5]++; }
    u32 rin[12] = {ow[0], ow[1], ow[2], ow[3], ow[4], ow[5], ow[6], k, j, Y4, c1, t};
    u32 rein[9] = {o.Y1, Y6, o.Y12, wa[12], wa[5], Y4, o.Y9, Y14, wa[8]};
    u32 rdig[8] = {da[1], da[3], da[4], da[6], db[1], db[3], db[4], db[6]};
    u32 reo[16], rem[16], rk[8];
    for (int i = 0; i < 4; i++) { reo[i] = e1o[0][i]; reo[4 + i] = e1o[1][i]; reo[8 + i] = e3o[0][i]; reo[12 + i] = e3o[1][i];
                                  rem[i] = e1m[0][i]; rem[4 + i] = e1m[1][i]; rem[8 + i] = e3m[0][i]; rem[12 + i] = e3m[1][i];
                                  rk[i] = K1[i]; rk[4 + i] = K3[i]; }
    fwrite(rin, 4, 12, fo[0]); fwrite(rein, 4, 9, fo[1]); fwrite(rdig, 4, 8, fo[2]); fwrite(reo, 4, 16, fo[3]);
    fwrite(rem, 4, 16, fo[4]); fwrite(rk, 4, 8, fo[5]); fwrite(R, 4, 4, fo[6]);
    made++;
    return 1;
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: gen rand <outdir> <N> <seed> | gen ctx <outdir> <C> <Mk> <Jc> <seed>\n"); return 1; }
    u32 x[4] = {X3, X7, X11, X15}, xb[4] = {X3, X7, X11, X15};
    u32 K = IV[2] + IV[6];
    W4B = (((W4 + K) ^ LEN_A ^ LEN_B) - K); DELTA5 = W4 - W4B;
    gq(&x[0], &x[1], &x[2], &x[3], W4, W13); gq(&xb[0], &xb[1], &xb[2], &xb[3], W4B, W13);
    Y3 = x[0]; Y11 = x[2]; Y3B = xb[0]; Y11B = xb[2];
    if (Y3 != 0x8127C181 || Y11 != 0x7AF77F38 || Y3B - Y3 != 0xFDB77CFD || Y11B - Y11 != 0x0A08818B || DELTA5 != 0xFFFFFFF8 || x[1] != xb[1] || x[3] != xb[3]) {
        fprintf(stderr, "constants mismatch\n"); return 2; }
    K2A = K + W4; K2D = ROR(K2A ^ LEN_A, 16); K2C = IV[2] + K2D; K2B = ROR(IV[6] ^ K2C, 12);
    char path[4096];
    for (int f = 0; f < 7; f++) { snprintf(path, sizeof path, "%s/%s", argv[2], FNAME[f]); fo[f] = fopen(path, "wb"); if (!fo[f]) { perror(path); return 3; } }
    u32 ow[7];
    if (!strcmp(argv[1], "rand")) {
        u64 N = strtoull(argv[3], 0, 0); sm = strtoull(argv[4], 0, 0);
        while (made < N) { for (int i = 0; i < 7; i++) ow[i] = next32(); u32 k = next32() >> 13, j = next32() >> 11; sample(ow, k, j); }
    } else if (!strcmp(argv[1], "ctx") && argc >= 7) {
        u64 C = strtoull(argv[3], 0, 0), Mk = strtoull(argv[4], 0, 0), Jc = strtoull(argv[5], 0, 0); sm = strtoull(argv[6], 0, 0);
        for (u64 c = 0; c < C; c++) {
            for (int i = 0; i < 7; i++) ow[i] = next32();
            for (u64 m = 0; m < Mk; m++) { u32 k = next32() >> 13; for (u64 q = 0; q < Jc; q++) { u32 j = next32() >> 11; while (!sample(ow, k, j)) j = next32() >> 11; } }
        }
    } else { fprintf(stderr, "bad mode\n"); return 1; }
    for (int f = 0; f < 7; f++) fclose(fo[f]);
    printf("samples %llu skipped_t0 %llu\n", (unsigned long long)made, (unsigned long long)skipped);
    printf("constants Y3 %08x Y3' %08x Y11 %08x Y11' %08x W4' %08x DELTA5 %08x\n", Y3, Y3B, Y11, Y11B, W4B, DELTA5);
    u64 tot = 0; for (int i = 0; i < 7; i++) { printf("fail %-22s %llu\n", FAILNAME[i], (unsigned long long)fails[i]); tot += fails[i]; }
    printf("internal_failures_total %llu\n", (unsigned long long)tot);
    return tot ? 4 : 0;
}
