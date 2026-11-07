// walsh.c - joint lens: every GF(2) mask of weight 1..4 over the 128 residual bits, with train/test and controls.
//   walsh <res.u32> <raw|spiral> <rows> <seed> [maxw]
// Coordinates: raw    W = (R1, R3, R4, R6)
//              spiral W = (R1, R3, R4 ^ ROR(R1,8), R6 ^ ROR(R3,8) ^ ROR(eta,8))   (a linear bijection of R; RESULT.md s.2)
// Data sets (each split into train = first rows/2, test = last rows/2; shuffles act within each half):
//   D  = data;  S1, S2 = data with each of the 4 words permuted independently (keeps every word's own law,
//   destroys cross-word dependence);  U = uniform random words (splitmix64, same count).
// For mask a: c = E[(-1)^(a.W)].  Raw test: D against U.  Cross-word test: excess x = c_D - c_S1 against the
// control excess c_S2 - c_S1 (exactly 0 for one-word masks).  z = c*sqrt(n), z_x = x*sqrt(n/2), n = rows/2.
// Discovery on train at |z| > ZT, confirmation on test at |z| > 3 with the same sign.
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <omp.h>
typedef uint32_t u32; typedef uint64_t u64;
#define ROR(x, n) ((u32)(((x) >> (n)) | ((x) << (32 - (n)))))
#define NB 128
#define TOPK 25
enum { DS_D, DS_S1, DS_S2, DS_U, NDS };
static u64 *col[NDS][NB][2]; // [dataset][bit][half] -> nw words
static int nw; static double nhalf;
static u64 sm;
static u64 next64(void) { u64 z = (sm += 0x9E3779B97F4A7C15ULL); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static void shuffle(u32 *a, long n) { for (long i = n - 1; i > 0; i--) { long j = (long)(next64() % (u64)(i + 1)); u32 t = a[i]; a[i] = a[j]; a[j] = t; } }
typedef struct { double key; int b[4]; int w; double ctr, cte, xtr, xte; } hit_t;
typedef struct {
    hit_t topraw[TOPK], topx[TOPK]; int nraw, nx;
    double maxD, maxU, maxX, maxXc; // max |z| train: raw D, raw U, excess D-S1, excess S2-S1 (cross-word masks only for X)
    u64 nmask, ncross, hitD, hitU, confD, confU, hitX, hitXc, confX, confXc;
} acc_t;
static void topins(hit_t *t, int *n, hit_t h) {
    if (*n < TOPK) { t[(*n)++] = h; } else { int m = 0; for (int i = 1; i < TOPK; i++) if (t[i].key < t[m].key) m = i; if (h.key <= t[m].key) return; t[m] = h; }
}
static double ZT = 6.0;
static int spiral, coupling;
static inline void count4(const u64 *pre[NDS][2], const u64 *last[NDS][2], int cnt[NDS][2]) {
    for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) {
        const u64 *p = pre[d][h], *q = last[d][h]; long s = 0;
        if (p) { for (int i = 0; i < nw; i++) s += __builtin_popcountll(p[i] ^ q[i]); }
        else   { for (int i = 0; i < nw; i++) s += __builtin_popcountll(q[i]); }
        cnt[d][h] = (int)s;
    }
}
static void record(acc_t *A, const int *b, int w, int cnt[NDS][2]) {
    double c[NDS][2]; for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) c[d][h] = 1.0 - 2.0 * cnt[d][h] / nhalf;
    double sq = sqrt(nhalf), sx = sqrt(nhalf / 2);
    int words = 0; for (int i = 0; i < w; i++) words |= 1 << (b[i] >> 5);
    int cross = coupling ? 1 : __builtin_popcount(words) > 1;
    A->nmask++; A->ncross += cross;
    double zD = fabs(c[DS_D][0]) * sq, zU = fabs(c[DS_U][0]) * sq;
    if (zD > A->maxD) A->maxD = zD;
    if (zU > A->maxU) A->maxU = zU;
    if (zD > ZT) { A->hitD++; if (c[DS_D][0] * c[DS_D][1] > 0 && fabs(c[DS_D][1]) * sq > 3) A->confD++; }
    if (zU > ZT) { A->hitU++; if (c[DS_U][0] * c[DS_U][1] > 0 && fabs(c[DS_U][1]) * sq > 3) A->confU++; }
    hit_t h; memset(&h, 0, sizeof h); for (int i = 0; i < w; i++) h.b[i] = b[i]; for (int i = w; i < 4; i++) h.b[i] = -1; h.w = w;
    h.key = fabs(c[DS_D][0]); h.ctr = c[DS_D][0]; h.cte = c[DS_D][1];
    double xtr = c[DS_D][0] - c[DS_S1][0], xte = c[DS_D][1] - c[DS_S1][1];
    h.xtr = xtr; h.xte = xte;
    topins(A->topraw, &A->nraw, h);
    if (cross) {
        double zx = fabs(xtr) * sx, zxc = fabs(c[DS_S2][0] - c[DS_S1][0]) * sx;
        double xcte = c[DS_S2][1] - c[DS_S1][1];
        if (zx > A->maxX) A->maxX = zx;
        if (zxc > A->maxXc) A->maxXc = zxc;
        if (zx > ZT) { A->hitX++; if (xtr * xte > 0 && fabs(xte) * sx > 3) A->confX++; }
        if (zxc > ZT) { A->hitXc++; if ((c[DS_S2][0] - c[DS_S1][0]) * xcte > 0 && fabs(xcte) * sx > 3) A->confXc++; }
        hit_t g = h; g.key = fabs(xtr); topins(A->topx, &A->nx, g);
    }
}
static void merge(acc_t *T, acc_t *A) {
    for (int i = 0; i < A->nraw; i++) topins(T->topraw, &T->nraw, A->topraw[i]);
    for (int i = 0; i < A->nx; i++) topins(T->topx, &T->nx, A->topx[i]);
    if (A->maxD > T->maxD) T->maxD = A->maxD;
    if (A->maxU > T->maxU) T->maxU = A->maxU;
    if (A->maxX > T->maxX) T->maxX = A->maxX;
    if (A->maxXc > T->maxXc) T->maxXc = A->maxXc;
    T->nmask += A->nmask; T->ncross += A->ncross; T->hitD += A->hitD; T->hitU += A->hitU; T->confD += A->confD; T->confU += A->confU;
    T->hitX += A->hitX; T->hitXc += A->hitXc; T->confX += A->confX; T->confXc += A->confXc;
}
static const char *WN[4] = {"1", "3", "4", "6"};
static const char *WS[4] = {"R1", "R3", "U3", "U1"};
static const char *WS7[4] = {"R1", "R3", "Z7", "Q7"};
static void transform(u32 *R, long N) {
    const u32 ETA = 0x830303CF;
    if (spiral == 1) for (long r = 0; r < N; r++) { u32 *x = R + 4 * r; x[2] ^= ROR(x[0], 8); x[3] ^= ROR(x[1], 8) ^ ROR(ETA, 8); }
    if (spiral == 2) for (long r = 0; r < N; r++) { u32 *x = R + 4 * r; x[2] ^= ROR(x[0], 7); x[3] ^= ROR(x[1], 7); }
}
static void pmask(const hit_t *h, char *s) {
    s[0] = 0; for (int i = 0; i < h->w; i++) { char t[32]; snprintf(t, sizeof t, "%s%s.%d", i ? "+" : "", spiral == 1 ? WS[h->b[i] >> 5] : spiral == 2 ? WS7[h->b[i] >> 5] : WN[h->b[i] >> 5], h->b[i] & 31); strcat(s, t); }
}
static int cmph(const void *a, const void *b) { double x = ((const hit_t *)a)->key, y = ((const hit_t *)b)->key; return x < y ? 1 : x > y ? -1 : 0; }
static void report(int w, acc_t *T) {
    printf("\n=== weight %d: %llu masks (%llu span >= 2 words)  n = %.0f rows per half, sigma(c) = %.5f ===\n", w,
           (unsigned long long)T->nmask, (unsigned long long)T->ncross, nhalf, 1 / sqrt(nhalf));
    printf("RAW  max|z| train: data %.2f  uniform control %.2f | |z|>%.0f on train: data %llu (confirmed on test %llu)  uniform %llu (confirmed %llu)\n",
           T->maxD, T->maxU, ZT, (unsigned long long)T->hitD, (unsigned long long)T->confD, (unsigned long long)T->hitU, (unsigned long long)T->confU);
    printf("%s max|z| train %.2f ; control (%s) %.2f | |z|>%.0f: data %llu (confirmed %llu)  control %llu (confirmed %llu)\n",
           coupling ? "COUPLING excess (data - K1^K3 re-paired 1), all masks," : "XWORD excess (data - shuffle1)",
           T->maxX, coupling ? "re-paired 2 - re-paired 1" : "shuffle2 - shuffle1", T->maxXc, ZT, (unsigned long long)T->hitX, (unsigned long long)T->confX, (unsigned long long)T->hitXc, (unsigned long long)T->confXc);
    qsort(T->topraw, T->nraw, sizeof(hit_t), cmph); qsort(T->topx, T->nx, sizeof(hit_t), cmph);
    char s[128];
    printf("top raw |c| (train): mask  c_train  c_test  excess_train  excess_test\n");
    for (int i = 0; i < T->nraw; i++) { pmask(&T->topraw[i], s); printf("  %-28s %+.5f %+.5f %+.5f %+.5f\n", s, T->topraw[i].ctr, T->topraw[i].cte, T->topraw[i].xtr, T->topraw[i].xte); }
    printf("top cross-word |excess| (train): mask  c_train  c_test  excess_train  excess_test  z_ex_train  z_ex_test\n");
    double sx = sqrt(nhalf / 2);
    for (int i = 0; i < T->nx; i++) { pmask(&T->topx[i], s); printf("  %-28s %+.5f %+.5f %+.5f %+.5f %+7.2f %+7.2f\n", s, T->topx[i].ctr, T->topx[i].cte, T->topx[i].xtr, T->topx[i].xte, T->topx[i].xtr * sx, T->topx[i].xte * sx); }
    fflush(stdout);
}
int main(int argc, char **argv) {
    if (argc < 5) { fprintf(stderr, "usage: walsh <res.u32|keys.u32> <raw|spiral|spiral7|kraw|kspiral|kspiral7> <rows> <seed> [maxw]\n"); return 1; }
    // k* modes (coupling test): input is keys.u32 (K1 | K3); D = K1 ^ K3 (= R), S1/S2 = K1 ^ K3 of another row of the
    // same half (whole K3 row re-paired), so every within-K1 and within-K3 law is kept and only K1-K3 coupling is removed.
    coupling = argv[2][0] == 'k';
    const char *cm = argv[2] + coupling;
    spiral = !strcmp(cm, "spiral") ? 1 : !strcmp(cm, "spiral7") ? 2 : 0;
    long N = atol(argv[3]); sm = strtoull(argv[4], 0, 0); int maxw = argc > 5 ? atoi(argv[5]) : 4;
    FILE *f = fopen(argv[1], "rb"); if (!f) { perror(argv[1]); return 2; }
    int ncol = coupling ? 8 : 4;
    u32 *R = malloc(N * 4 * ncol); if (fread(R, 4 * ncol, N, f) != (size_t)N) { fprintf(stderr, "short read\n"); return 3; } fclose(f);
    u32 *KK = 0;
    if (coupling) { KK = R; R = malloc(N * 16); for (long r = 0; r < N; r++) for (int w = 0; w < 4; w++) R[4 * r + w] = KK[8 * r + w] ^ KK[8 * r + 4 + w]; }
    long H = N / 2; nw = (int)(H / 64); nhalf = (double)H;
    u32 *tmp = malloc(N * 16);
    for (int d = 0; d < NDS; d++) {
        if (d == DS_D) { memcpy(tmp, R, N * 16); transform(tmp, N); }
        else if (d == DS_U) { for (long i = 0; i < 4 * N; i++) tmp[i] = (u32)(next64() >> 32); }
        else if (coupling) {
            long *pi = malloc(H * sizeof(long));
            for (int h = 0; h < 2; h++) {
                for (long i = 0; i < H; i++) pi[i] = i;
                for (long i = H - 1; i > 0; i--) { long j = (long)(next64() % (u64)(i + 1)); long t = pi[i]; pi[i] = pi[j]; pi[j] = t; }
                for (long i = 0; i < H; i++) for (int w = 0; w < 4; w++) tmp[4 * (h * H + i) + w] = KK[8 * (h * H + i) + w] ^ KK[8 * (h * H + pi[i]) + 4 + w];
            }
            free(pi); transform(tmp, N);
        }
        else {
            memcpy(tmp, R, N * 16); transform(tmp, N);
            memcpy(tmp, R, N * 16);
            u32 *colw = malloc(H * 4);
            for (int h = 0; h < 2; h++) for (int w = 0; w < 4; w++) {
                for (long i = 0; i < H; i++) colw[i] = tmp[4 * (h * H + i) + w];
                shuffle(colw, H);
                for (long i = 0; i < H; i++) tmp[4 * (h * H + i) + w] = colw[i];
            }
            free(colw);
        }
        for (int b = 0; b < NB; b++) for (int h = 0; h < 2; h++) {
            u64 *c = calloc(nw, 8); col[d][b][h] = c;
            for (long i = 0; i < H; i++) { u32 v = tmp[4 * (h * H + i) + (b >> 5)] >> (b & 31) & 1; c[i >> 6] |= (u64)v << (i & 63); }
        }
    }
    free(tmp);
    printf("walsh %s coords=%s rows=%ld (train %ld, test %ld) seed=%s threads=%d ZT=%.1f\n", argv[1], argv[2], N, H, H, argv[4], omp_get_max_threads(), ZT);
    for (int w = 1; w <= maxw; w++) {
        acc_t T; memset(&T, 0, sizeof T);
        int npair = NB * NB;
        #pragma omp parallel
        {
            acc_t A; memset(&A, 0, sizeof A);
            u64 *buf = malloc((size_t)NDS * 2 * nw * 8);
            #pragma omp for schedule(dynamic, 1)
            for (int ij = 0; ij < npair; ij++) {
                int i = ij / NB, j = ij % NB; int b[4];
                const u64 *pre[NDS][2], *last[NDS][2]; int cnt[NDS][2];
                if (w == 1) { if (j) continue; b[0] = i; for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) { pre[d][h] = 0; last[d][h] = col[d][i][h]; } count4(pre, last, cnt); record(&A, b, 1, cnt); continue; }
                if (j <= i) continue;
                if (w == 2) { b[0] = i; b[1] = j; for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) { pre[d][h] = col[d][i][h]; last[d][h] = col[d][j][h]; } count4(pre, last, cnt); record(&A, b, 2, cnt); continue; }
                // w >= 3: buf = col_i ^ col_j, then (w==3) add k ; (w==4) add k then l
                for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) { u64 *p = buf + ((size_t)(d * 2 + h)) * nw; const u64 *x = col[d][i][h], *y = col[d][j][h]; for (int q = 0; q < nw; q++) p[q] = x[q] ^ y[q]; }
                if (w == 3) {
                    for (int k = j + 1; k < NB; k++) { b[0] = i; b[1] = j; b[2] = k;
                        for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) { pre[d][h] = buf + ((size_t)(d * 2 + h)) * nw; last[d][h] = col[d][k][h]; }
                        count4(pre, last, cnt); record(&A, b, 3, cnt); }
                } else {
                    u64 *buf2 = malloc((size_t)NDS * 2 * nw * 8);
                    for (int k = j + 1; k < NB; k++) {
                        for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) { u64 *p = buf2 + ((size_t)(d * 2 + h)) * nw; const u64 *x = buf + ((size_t)(d * 2 + h)) * nw, *y = col[d][k][h]; for (int q = 0; q < nw; q++) p[q] = x[q] ^ y[q]; }
                        for (int l = k + 1; l < NB; l++) { b[0] = i; b[1] = j; b[2] = k; b[3] = l;
                            for (int d = 0; d < NDS; d++) for (int h = 0; h < 2; h++) { pre[d][h] = buf2 + ((size_t)(d * 2 + h)) * nw; last[d][h] = col[d][l][h]; }
                            count4(pre, last, cnt); record(&A, b, 4, cnt); }
                    }
                    free(buf2);
                }
            }
            #pragma omp critical
            merge(&T, &A);
            free(buf);
        }
        report(w, &T);
    }
    return 0;
}
