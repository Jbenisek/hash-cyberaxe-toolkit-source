// oc_stream.c - streaming ones'-complement statistics of the front-line residual (2-round BLAKE3, pkgCG family).
// Sampler = data/gen.c sample() (same constants, step CO, step CT, compression), but nothing is stored: every sample
// updates the count layout defined in oclib.py layout() (quantities D, R, E, S; see oclib.py docstring).
//   oc_stream real <out.bin> <N> <seed> <threads>   front-line pairs (fresh outer words, k, j each sample)
//   oc_stream ctrl <out.bin> <N> <seed> <threads>   CONTROL: the 16 final-state words of A and of B uniform random
// With threads=1 and seed 0x5045525350310001, mode real reproduces the rows of data/rand (same RNG order).
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <omp.h>
typedef uint32_t u32; typedef uint64_t u64; typedef int64_t i64;
#define ROR(x, n) ((u32)(((x) >> (n)) | ((x) << (32 - (n)))))
#define ROL(x, n) ROR((x), 32 - (n))
static const u32 IV[8] = {0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19};
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
static const u32 X3 = 0x29D4FA98, X7 = 0xBEE3AF28, X11 = 0x44036000, X15 = 0x40C58500, W4 = 0x97475638, W13 = 0x0007C006;
static const u32 LEN_A = 55, LEN_B = 63, FLAGS = 3;
static const u32 CLASS_VALUE = 0x030C0303, FREE_MASK = 0xFC307CFC, QMASK = 0x0E09818B, QVALUE = 0x02008000;
static u32 Y3, Y11, W4B, DELTA5, K2A, K2B, K2C, K2D;
#define MM 0xFFFFFFFFu

static inline void gq(u32 *a, u32 *b, u32 *c, u32 *d, u32 x, u32 y) {
    *a = *a + *b + x; *d = ROR(*d ^ *a, 16); *c = *c + *d; *b = ROR(*b ^ *c, 12);
    *a = *a + *b + y; *d = ROR(*d ^ *a, 8); *c = *c + *d; *b = ROR(*b ^ *c, 7);
}
static inline void G(u32 *v, int a, int b, int c, int d, u32 x, u32 y) { gq(&v[a], &v[b], &v[c], &v[d], x, y); }
static void compress2(const u32 w[16], u32 t, u32 blen, u32 flags, u32 v[16]) {
    u32 m[16], m2[16];
    for (int i = 0; i < 8; i++) v[i] = IV[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IV[i];
    v[12] = t; v[13] = 0; v[14] = blen; v[15] = flags;
    memcpy(m, w, 64);
    for (int r = 0; r < 2; r++) {
        G(v, 0, 4, 8, 12, m[0], m[1]); G(v, 1, 5, 9, 13, m[2], m[3]); G(v, 2, 6, 10, 14, m[4], m[5]); G(v, 3, 7, 11, 15, m[6], m[7]);
        G(v, 0, 5, 10, 15, m[8], m[9]); G(v, 1, 6, 11, 12, m[10], m[11]); G(v, 2, 7, 8, 13, m[12], m[13]); G(v, 3, 4, 9, 14, m[14], m[15]);
        for (int i = 0; i < 16; i++) m2[i] = m[PERM[i]];
        memcpy(m, m2, 64);
    }
}
static u32 pdep(u32 x, u32 mask) { u32 r = 0; int n = 0; for (int i = 0; i < 32; i++) if (mask >> i & 1) { r |= (x >> n & 1) << i; n++; } return r; }
static inline u64 next64(u64 *sm) { u64 z = (*sm += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static inline u32 next32(u64 *sm) { return (u32)(next64(sm) >> 32); }

typedef struct { u32 Y1, Y12, e1, w[16], C2a1, C2b1, C2c1, C2d1, K0b1, K0d1, S0; } ctx_t;
static void step_co(const u32 ow[7], u32 Y4, ctx_t *o) {   // identical algebra to data/gen.c step_co
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
    u32 Y1 = C1a1 + C1b1 + w10, C2c1 = X10 + C2d1, C2b1 = ROR(X6 ^ C2c1, 12);
    u32 K0d1 = K0c1 - IV[0], S0 = ROL(S12, 8) ^ K0d1, D0a1 = ROL(D0d1, 16) ^ S15;
    u32 w8 = D0a1 - S0 - S5, w5 = S2 - K2A - K2B, w9 = X0 - D0a1 - D0b1, w11 = X1 - D1a1 - D1b1;
    memset(o, 0, sizeof *o);
    o->Y1 = Y1; o->Y12 = Y12; o->e1 = Y3 + Y4;
    o->C2a1 = C2a1; o->C2b1 = C2b1; o->C2c1 = C2c1; o->C2d1 = C2d1; o->K0b1 = K0b1; o->K0d1 = K0d1; o->S0 = S0;
    o->w[2] = w2; o->w[3] = w3; o->w[4] = W4; o->w[5] = w5; o->w[6] = w6; o->w[7] = w7; o->w[8] = w8; o->w[9] = w9;
    o->w[10] = w10; o->w[11] = w11; o->w[12] = w12; o->w[13] = W13; o->w[14] = 0; o->w[15] = 0;
}
// one front-line pair; returns 0 when t = 0 (skipped exactly as gen.c does)
static int sample(u64 *sm, u32 va[16], u32 vb[16]) {
    u32 ow[7]; for (int i = 0; i < 7; i++) ow[i] = next32(sm);
    u32 k = next32(sm) >> 13, j = next32(sm) >> 11;
    ctx_t o; u32 e1 = CLASS_VALUE | pdep(k, FREE_MASK), Y4 = e1 - Y3, c1 = QVALUE | pdep(j, ~QMASK);
    step_co(ow, Y4, &o);
    u32 E1a1 = ROL(c1 - Y11, 16) ^ o.Y12, Y6 = E1a1 - o.Y1 - o.w[12], Y10 = ROL(Y6, 7) ^ o.C2b1, Y14 = Y10 - o.C2c1;
    u32 Y2 = ROL(Y14, 8) ^ o.C2d1, w0 = Y2 - o.C2a1 - o.C2b1, K0a1 = IV[0] + IV[4] + w0;
    u32 t = ROL(o.K0d1, 16) ^ K0a1, w1 = o.S0 - K0a1 - o.K0b1;
    if (t == 0) return 0;
    u32 wa[16], wb[16];
    memcpy(wa, o.w, 64); wa[0] = w0; wa[1] = w1;
    memcpy(wb, wa, 64); wb[4] = W4B; wb[5] = wa[5] + DELTA5;
    compress2(wa, t, LEN_A, FLAGS, va); compress2(wb, t, LEN_B, FLAGS, vb);
    return 1;
}

// ---- count layout (must equal oclib.py layout()) ----
#define NMODS 16
static const u32 MODS[NMODS] = {3, 5, 15, 17, 51, 85, 255, 257, 771, 1285, 3855, 4369, 13107, 21845, 65535, 65537};
static const u32 JM[4] = {3, 5, 15, 17};
static const u32 CIDX[6] = {2, 8, 16, 64, 2048, 8192};   // (17,2) (17,16) (257,2) (257,16) (65537,2) (65537,16)
static size_t PER_W, PER_Q, JOFF[4], TOTAL;
static u32 DL17[17], DL257[257], DL65537[65537];

static void setup_layout(void) {
    PER_W = 0; for (int i = 0; i < NMODS; i++) PER_W += MODS[i];
    PER_W += 2 + 32; for (int i = 0; i < 6; i++) PER_W += CIDX[i];
    size_t o = 4 * PER_W; for (int i = 0; i < 4; i++) { JOFF[i] = o; o += (size_t)JM[i] * JM[i] * JM[i] * JM[i]; }
    PER_Q = o; TOTAL = 4 * PER_Q + 1;
    u32 *T[3] = {DL17, DL257, DL65537}; u32 P[3] = {17, 257, 65537};
    for (int k = 0; k < 3; k++) { u64 x = 1; for (u32 e = 0; e < P[k] - 1; e++) { T[k][x] = e; x = x * 3 % P[k]; } }
}
static inline void addword(u32 *h, u32 v) {   // v in [0, M); h points at this (q, w) block
    size_t o = 0;
    h[o + v % 3u]++; o += 3; h[o + v % 5u]++; o += 5; h[o + v % 15u]++; o += 15; h[o + v % 17u]++; o += 17;
    h[o + v % 51u]++; o += 51; h[o + v % 85u]++; o += 85; h[o + v % 255u]++; o += 255; h[o + v % 257u]++; o += 257;
    h[o + v % 771u]++; o += 771; h[o + v % 1285u]++; o += 1285; h[o + v % 3855u]++; o += 3855; h[o + v % 4369u]++; o += 4369;
    h[o + v % 13107u]++; o += 13107; h[o + v % 21845u]++; o += 21845; h[o + v % 65535u]++; o += 65535; h[o + v % 65537u]++; o += 65537;
    h[o] += (v % 0x11111111u) == 0; o++; h[o] += (v % 0x01010101u) == 0; o++;
    u32 r3 = v % 3u, r5 = v % 5u, r17 = v % 17u, r257 = v % 257u, r65537 = v % 65537u;
    h[o + ((r3 == 0) | (r5 == 0) << 1 | (r17 == 0) << 2 | (r257 == 0) << 3 | (r65537 == 0) << 4)]++; o += 32;
    if (r17) { h[o + (DL17[r17] & 1)]++; h[o + 2 + (DL17[r17] & 7)]++; } o += 10;
    if (r257) { h[o + (DL257[r257] & 15)]++; h[o + 16 + (DL257[r257] & 63)]++; } o += 80;
    if (r65537) { h[o + (DL65537[r65537] & 2047)]++; h[o + 2048 + (DL65537[r65537] & 8191)]++; }
}
static inline u32 oc(u32 x) { return x == MM ? 0 : x; }
static inline u32 ocsub(u32 a, u32 b) { a = oc(a); b = oc(b); return a >= b ? a - b : (u32)((u64)a + MM - b); }
static const int IDX[4] = {1, 3, 4, 6};
// all four quantities of one pair; rprev = XOR residual of the previous pair of this thread (surrogate S)
// quantities are buffered (B pairs) and then histogrammed block by block so each pass stays cache resident
#define BUF 32768
static void quant(u32 Q[4][4], const u32 va[16], const u32 vb[16], u32 rprev[4]) {
    for (int w = 0; w < 4; w++) {
        int i = IDX[w];
        u32 dA = va[i] ^ va[i + 8], dB = vb[i] ^ vb[i + 8], R = dA ^ dB;
        u32 D = ocsub(dA, dB);
        i64 e = (i64)D - (i64)ocsub(va[i], vb[i]) - (i64)ocsub(va[i + 8], vb[i + 8]);
        e %= (i64)MM; if (e < 0) e += MM;
        Q[0][w] = D; Q[1][w] = oc(R); Q[2][w] = (u32)e; Q[3][w] = ocsub(dA, dA ^ rprev[w]);
        rprev[w] = R;
    }
}
static void flush(u32 *h, u32 (*buf)[4][4], size_t nb) {
    for (int q = 0; q < 4; q++) {
        u32 *hq = h + (size_t)q * PER_Q;
        for (int w = 0; w < 4; w++) { u32 *hb = hq + (size_t)w * PER_W; for (size_t s = 0; s < nb; s++) addword(hb, buf[s][q][w]); }
        for (int m = 0; m < 4; m++) {
            u32 mm = JM[m];
            for (size_t s = 0; s < nb; s++) {
                u64 ix = 0;
                for (int w = 0; w < 4; w++) ix = ix * mm + buf[s][q][w] % mm;
                hq[JOFF[m] + ix]++;
            }
        }
    }
}
int main(int argc, char **argv) {
    if (argc < 6) { fprintf(stderr, "usage: oc_stream real|ctrl <out.bin> <N> <seed> <threads>\n"); return 1; }
    int ctrl = !strcmp(argv[1], "ctrl");
    u64 N = strtoull(argv[3], 0, 0), seed = strtoull(argv[4], 0, 0); int T = atoi(argv[5]);
    u32 x[4] = {X3, X7, X11, X15}, xb[4] = {X3, X7, X11, X15};
    u32 K = IV[2] + IV[6];
    W4B = (((W4 + K) ^ LEN_A ^ LEN_B) - K); DELTA5 = W4 - W4B;
    gq(&x[0], &x[1], &x[2], &x[3], W4, W13); gq(&xb[0], &xb[1], &xb[2], &xb[3], W4B, W13);
    Y3 = x[0]; Y11 = x[2];
    if (Y3 != 0x8127C181 || Y11 != 0x7AF77F38 || DELTA5 != 0xFFFFFFF8) { fprintf(stderr, "constants mismatch\n"); return 2; }
    K2A = K + W4; K2D = ROR(K2A ^ LEN_A, 16); K2C = IV[2] + K2D; K2B = ROR(IV[6] ^ K2C, 12);
    setup_layout();
    u64 *tot = calloc(TOTAL, 8); u64 skipped = 0;
    double t0 = omp_get_wtime();
    omp_set_num_threads(T);
    #pragma omp parallel reduction(+:skipped)
    {
        int tid = omp_get_thread_num(), nt = omp_get_num_threads();
        u64 n = N / nt + ((u64)tid < N % nt);
        u64 sm = seed + (u64)tid * 0x0001000000000000ULL;   // thread 0 uses the seed itself (gen.c order)
        u32 *h = calloc(TOTAL, 4);
        u32 va[16], vb[16], rprev[4] = {0, 0, 0, 0};
        // warm-up pair (not counted) so the surrogate has a previous residual; the counted stream starts after it
        // NOTE: for the gen.c reproduction check, compare against data rows 1.. (row 0 is the warm-up)
        if (ctrl) { for (int i = 0; i < 16; i++) { va[i] = next32(&sm); vb[i] = next32(&sm); } }
        else { while (!sample(&sm, va, vb)) skipped++; }
        for (int w = 0; w < 4; w++) rprev[w] = (va[IDX[w]] ^ va[IDX[w] + 8]) ^ (vb[IDX[w]] ^ vb[IDX[w] + 8]);
        u32 (*buf)[4][4] = malloc(sizeof(u32[4][4]) * BUF); size_t nb = 0;
        for (u64 s = 0; s < n; s++) {
            if (ctrl) { for (int i = 0; i < 16; i++) { va[i] = next32(&sm); vb[i] = next32(&sm); } }
            else { while (!sample(&sm, va, vb)) skipped++; }
            quant(buf[nb++], va, vb, rprev);
            if (nb == BUF) { flush(h, buf, nb); nb = 0; }
        }
        if (nb) flush(h, buf, nb);
        free(buf);
        #pragma omp critical
        { for (size_t i = 0; i < TOTAL - 1; i++) tot[i] += h[i]; }
        free(h);
    }
    tot[TOTAL - 1] = N;
    FILE *f = fopen(argv[2], "wb"); if (!f) { perror(argv[2]); return 3; }
    fwrite(tot, 8, TOTAL, f); fclose(f);
    printf("mode %s N %llu seed %llx threads %d skipped_t0 %llu total_cells %zu time %.1f s\n", argv[1],
           (unsigned long long)N, (unsigned long long)seed, T, (unsigned long long)skipped, TOTAL, omp_get_wtime() - t0);
    return 0;
}
