// rotscan.c - rotational lens on the front-line residual data (research/fifties/perspectives/data).
//
// Scan AB : side-A word i vs side-B word j:  V = B_j ^ rotl(A_i, r)   (op x)
//                                            V = B_j - rotl(A_i, r)   (op s, mod 2^32)
//                                            V = ror(B_j, r) - A_i    (op r, i.e. B = rotl(A + c, r); S uses the XOR shuffle)
//           for every i, j in 0..3, r in 0..31.  Lists: dig (digest words 1,3,4,6 A vs B),
//           e1 (E1 outputs a2 b2 c2 d2, A vs B), e3 (E3 outputs e2 f2 g2 h2, A vs B),
//           plant (digest A vs a synthetic B with planted rotational relations = positive control).
// Scan WW : relations inside one 4-word set X:  V = X_j op rotl(X_i, r), (i,j,r) != (i,i,0).
//           Sets: R (residual), K1, K3, DA (digest A), RP (R1, R3, U4 = R4^ROR(R1,8), U6 = R6^ROR(R3,8)).
// Scan J  : joint over the four words, same r, word map identity:  sum_w HW(B_w ^ rotl(A_w, r)).
//
// Sources (the control design):
//   D = the data.
//   S = shuffle control (scan AB / J): B'_j(t) = A_j(t) ^ (A_j(p(t)) ^ B_j(p(t))) for op x, and
//       A_j(t) + (B_j(p(t)) - A_j(p(t))) for op s.  Keeps each row's A->B difference law, breaks its link to A.
//   C = column-shuffle control (scan WW): X_i is read at row p(t), X_j at row t. Keeps one-word marginals,
//       breaks cross-word / same-row structure.
//   U = uniform random words (splitmix64), same count. Computed once per scan (it does not depend on the list).
// Every statistic is computed separately on half 0 (train: rows [0,n/2)) and half 1 (test: rows [n/2,n)).
// p is a fixed random permutation inside each half.
//
// Per job: HW histogram, d4 histogram (d4 = Hamming distance to the nearest period-4 word = nibble repeated
// 8 times, 16 such words), per-bit ones counts, count of |V| <= 256 as a signed mod-2^32 value, count V == 0,
// collision pairs sum C(m,2) over equal values, max multiplicity and its value.
//
// Build: gcc -O3 -march=native -fopenmp -o rotscan rotscan.c
// Run:   ./rotscan <datadir> <set: rand|ctx> <outprefix>
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>

typedef uint32_t u32;
typedef uint64_t u64;

static inline u32 rotl(u32 x, int r) { r &= 31; return r ? (x << r) | (x >> (32 - r)) : x; }
static inline u32 ror(u32 x, int r) { return rotl(x, 32 - (r & 31)); }
static inline u64 sm64(u64 *s) {
    u64 z = (*s += 0x9E3779B97F4A7C15ULL);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}
static inline int d4(u32 x) {
    int d = 0;
    for (int b = 0; b < 4; b++) { int c = __builtin_popcount(x & (0x11111111u << b)); d += c < 8 - c ? c : 8 - c; }
    return d;
}

static u32 *load(const char *dir, const char *set, const char *f, int cols, u64 *rows) {
    char p[1024]; snprintf(p, sizeof p, "%s/%s/%s", dir, set, f);
    FILE *fp = fopen(p, "rb"); if (!fp) { perror(p); exit(1); }
    fseek(fp, 0, SEEK_END); long sz = ftell(fp); fseek(fp, 0, SEEK_SET);
    u32 *a = malloc(sz); if (fread(a, 1, sz, fp) != (size_t)sz) { perror("read"); exit(1); }
    fclose(fp); *rows = sz / 4 / cols; return a;
}

typedef struct { u64 hwh[33], d4h[17], bit[32], msmall, zero; double coll; u32 maxm, modev; } St;

static const u32 *g_inp;
static int cmprow(const void *a, const void *b) {   // order by the 12-word input row, ties by row index
    u64 x = *(const u64 *)a, y = *(const u64 *)b;
    int c = memcmp(g_inp + x * 12, g_inp + y * 12, 48);
    return c ? c : (x < y ? -1 : x > y);
}

static void rsort(u32 *a, u32 *t, u64 n) {  // LSD radix, two 16-bit passes; result in a
    static __thread u64 cnt[65537];
    for (int sh = 0; sh < 32; sh += 16) {
        memset(cnt, 0, sizeof cnt);
        for (u64 i = 0; i < n; i++) cnt[((a[i] >> sh) & 0xffff) + 1]++;
        for (int k = 0; k < 65536; k++) cnt[k + 1] += cnt[k];
        for (u64 i = 0; i < n; i++) t[cnt[(a[i] >> sh) & 0xffff]++] = a[i];
        u32 *s = a; a = t; t = s;
    }
}

static void stats(u32 *v, u32 *tmp, u64 n, St *s) {
    memset(s, 0, sizeof *s);
    for (u64 i = 0; i < n; i++) {
        u32 x = v[i];
        s->hwh[__builtin_popcount(x)]++; s->d4h[d4(x)]++;
        for (int b = 0; b < 32; b++) s->bit[b] += (x >> b) & 1;
        if ((u32)(x + 256u) <= 512u) s->msmall++;
        if (!x) s->zero++;
    }
    rsort(v, tmp, n);
    u64 i = 0; s->maxm = 0;
    while (i < n) {
        u64 j = i; while (j < n && v[j] == v[i]) j++;
        u64 m = j - i; s->coll += (double)m * (m - 1) / 2;
        if (m > s->maxm) { s->maxm = (u32)m; s->modev = v[i]; }
        i = j;
    }
}

static void fmt(char *o, size_t cap, const char *tag, const St *s) {
    size_t k = snprintf(o, cap, "%s", tag);
    for (int q = 0; q < 33; q++) k += snprintf(o + k, cap - k, "%s%llu", q ? "," : "\t", (unsigned long long)s->hwh[q]);
    for (int q = 0; q < 17; q++) k += snprintf(o + k, cap - k, "%s%llu", q ? "," : "\t", (unsigned long long)s->d4h[q]);
    for (int q = 0; q < 32; q++) k += snprintf(o + k, cap - k, "%s%llu", q ? "," : "\t", (unsigned long long)s->bit[q]);
    snprintf(o + k, cap - k, "\t%llu\t%llu\t%.0f\t%u\t%08x\n", (unsigned long long)s->msmall,
             (unsigned long long)s->zero, s->coll, s->maxm, s->modev);
}

#define NL 4   // AB lists
#define NW 5   // WW sets
static const char *LN[NL] = {"dig", "e1", "e3", "plant"};
static const char *WN[NW] = {"R", "K1", "K3", "DA", "RP"};

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: %s datadir set outprefix\n", argv[0]); return 1; }
    const char *dir = argv[1], *set = argv[2], *outp = argv[3];
    u64 N, n2;
    u32 *dig = load(dir, set, "dig.u32", 8, &N);
    u32 *eout = load(dir, set, "eout.u32", 16, &n2); if (n2 != N) return 2;
    u32 *res = load(dir, set, "res.u32", 4, &n2); if (n2 != N) return 2;
    u32 *keys = load(dir, set, "keys.u32", 8, &n2); if (n2 != N) return 2;
    u32 *inp = load(dir, set, "inputs.u32", 12, &n2); if (n2 != N) return 2;
    {   // drop repeated input rows (ctx/ draws j with replacement); keep the first copy, keep row order
        u64 *ix = malloc(N * 8); for (u64 t = 0; t < N; t++) ix[t] = t;
        g_inp = inp; qsort(ix, N, 8, cmprow);
        unsigned char *drop = calloc(N, 1); u64 nd = 0;
        for (u64 q = 1; q < N; q++) if (!memcmp(inp + ix[q] * 12, inp + ix[q - 1] * 12, 48)) { drop[ix[q]] = 1; nd++; }
        u64 m = 0;
        for (u64 t = 0; t < N; t++) if (!drop[t]) {
            memmove(dig + m * 8, dig + t * 8, 32); memmove(eout + m * 16, eout + t * 16, 64);
            memmove(res + m * 4, res + t * 4, 16); memmove(keys + m * 8, keys + t * 8, 32); m++;
        }
        fprintf(stderr, "[%s] dropped %llu repeated input rows, %llu remain\n", set, (unsigned long long)nd,
                (unsigned long long)m);
        N = m; free(ix); free(drop);
    }
    u64 n = N / 2;  // rows per half
    // column arrays: AB lists: LA[l][w][row], LB[l][w][row]
    u32 *LA[NL][4], *LB[NL][4], *WX[NW][4], *UA[4], *UB[4];
    for (int l = 0; l < NL; l++) for (int w = 0; w < 4; w++) { LA[l][w] = malloc(N * 4); LB[l][w] = malloc(N * 4); }
    for (int s = 0; s < NW; s++) for (int w = 0; w < 4; w++) WX[s][w] = malloc(N * 4);
    for (int w = 0; w < 4; w++) { UA[w] = malloc(N * 4); UB[w] = malloc(N * 4); }
    u64 seed = 0x524F5441544E3031ULL;  // fixed
    u64 planted[4] = {0, 0, 0, 0};
    for (u64 t = 0; t < N; t++) {
        for (int w = 0; w < 4; w++) {
            LA[0][w][t] = dig[t * 8 + w]; LB[0][w][t] = dig[t * 8 + 4 + w];
            LA[1][w][t] = eout[t * 16 + w]; LB[1][w][t] = eout[t * 16 + 4 + w];
            LA[2][w][t] = eout[t * 16 + 8 + w]; LB[2][w][t] = eout[t * 16 + 12 + w];
            LA[3][w][t] = dig[t * 8 + w];
            WX[0][w][t] = res[t * 4 + w]; WX[1][w][t] = keys[t * 8 + w]; WX[2][w][t] = keys[t * 8 + 4 + w];
            WX[3][w][t] = dig[t * 8 + w];
            UA[w][t] = (u32)sm64(&seed); UB[w][t] = (u32)sm64(&seed);
        }
        WX[4][0][t] = res[t * 4 + 0]; WX[4][1][t] = res[t * 4 + 1];
        WX[4][2][t] = res[t * 4 + 2] ^ ror(res[t * 4 + 0], 8);
        WX[4][3][t] = res[t * 4 + 3] ^ ror(res[t * 4 + 1], 8);
        // planted positive control
        u32 *a = &LA[3][0][0]; (void)a;
        for (int w = 0; w < 4; w++) LB[3][w][t] = (u32)sm64(&seed);
        u64 z = sm64(&seed);
        if ((z & 0x3fff) == 0) { LB[3][0][t] = rotl(LA[3][0][t], 5) ^ 0x12345678u; planted[0]++; }
        if (((z >> 14) & 0x3fff) == 0) {
            u32 e = 0; int k = (int)((z >> 28) & 3); u64 zz = sm64(&seed);
            for (int q = 0; q < k; q++) e |= 1u << ((zz >> (5 * q)) & 31);
            LB[3][1][t] = rotl(LA[3][1][t], 11) ^ e; planted[1]++;
        }
        if (((z >> 30) & 0x3fff) == 0) {
            u32 e = 0; int k = (int)((z >> 44) % 3); u64 zz = sm64(&seed);
            for (int q = 0; q < k; q++) e |= 1u << ((zz >> (5 * q)) & 31);
            LB[3][2][t] = rotl(LA[3][2][t], 7) ^ 0x33333333u ^ e; planted[2]++;
        }
        if (((z >> 46) & 0xfff) == 0) {
            int dlt = (int)((z >> 58) & 63) - 32;
            if (sm64(&seed) & 1) LB[3][3][t] = rotl(LA[3][3][t], 13) + (u32)dlt;       // op s relation
            else LB[3][3][t] = rotl(LA[3][3][t] + 0x0BADCAFEu, 13);                   // op r relation
            planted[3]++;
        }
    }
    fprintf(stderr, "[%s] N=%llu n/half=%llu planted %llu %llu %llu %llu\n", set, (unsigned long long)N,
            (unsigned long long)n, (unsigned long long)planted[0], (unsigned long long)planted[1],
            (unsigned long long)planted[2], (unsigned long long)planted[3]);
    // permutations per half
    u64 *perm[2];
    for (int h = 0; h < 2; h++) {
        perm[h] = malloc(n * 8);
        for (u64 t = 0; t < n; t++) perm[h][t] = t;
        for (u64 t = n - 1; t > 0; t--) { u64 k = sm64(&seed) % (t + 1); u64 x = perm[h][t]; perm[h][t] = perm[h][k]; perm[h][k] = x; }
    }
    // ---- job list ----
    typedef struct { int scan, lst, i, j, r, op, src, half; } Job;  // src 0 D, 1 S/C, 2 U
    u64 cap = 64000; Job *jobs = malloc(cap * sizeof(Job)); u64 nj = 0;
    for (int h = 0; h < 2; h++) for (int op = 0; op < 3; op++) for (int i = 0; i < 4; i++) for (int j = 0; j < 4; j++)
        for (int r = 0; r < 32; r++) {
            for (int l = 0; l < NL; l++) for (int src = 0; src < 2; src++) jobs[nj++] = (Job){0, l, i, j, r, op, src, h};
            jobs[nj++] = (Job){0, -1, i, j, r, op, 2, h};
            if (op == 2 || (i == j && r == 0)) continue;
            for (int s = 0; s < NW; s++) for (int src = 0; src < 2; src++) jobs[nj++] = (Job){1, s, i, j, r, op, src, h};
            jobs[nj++] = (Job){1, -1, i, j, r, op, 2, h};
        }
    fprintf(stderr, "jobs %llu\n", (unsigned long long)nj);
    char **lines = calloc(nj, sizeof(char *));
    int nth = omp_get_max_threads();
    u32 **bufv = malloc(nth * sizeof(u32 *)), **buft = malloc(nth * sizeof(u32 *));
    for (int q = 0; q < nth; q++) { bufv[q] = malloc(n * 4); buft[q] = malloc(n * 4); }
    #pragma omp parallel for schedule(dynamic, 4)
    for (u64 q = 0; q < nj; q++) {
        Job jb = jobs[q]; int th = omp_get_thread_num(); u32 *v = bufv[th];
        u64 off = (u64)jb.half * n; u64 *pm = perm[jb.half];
        if (jb.scan == 0) {
            u32 *A = jb.src == 2 ? UA[jb.i] : LA[jb.lst][jb.i];
            u32 *B = jb.src == 2 ? UB[jb.j] : LB[jb.lst][jb.j];
            u32 *Aj = jb.src == 2 ? NULL : LA[jb.lst][jb.j];
            for (u64 t = 0; t < n; t++) {
                u32 a = rotl(A[off + t], jb.r), b;
                if (jb.src == 1) {
                    u64 p = off + pm[t];
                    b = jb.op == 1 ? (Aj[off + t] + (B[p] - Aj[p])) : (Aj[off + t] ^ (Aj[p] ^ B[p]));
                } else b = B[off + t];
                v[t] = jb.op == 0 ? (b ^ a) : jb.op == 1 ? (b - a) : (ror(b, jb.r) - A[off + t]);
            }
        } else {
            u32 *Xi = jb.src == 2 ? UA[jb.i] : WX[jb.lst][jb.i];
            u32 *Xj = jb.src == 2 ? (jb.i == jb.j ? UA[jb.j] : UB[jb.j]) : WX[jb.lst][jb.j];
            for (u64 t = 0; t < n; t++) {
                u64 ti = jb.src == 1 ? off + pm[t] : off + t;
                u32 a = rotl(Xi[ti], jb.r), b = Xj[off + t];
                v[t] = jb.op == 0 ? (b ^ a) : (b - a);
            }
        }
        St s; stats(v, buft[th], n, &s);
        char tag[128];
        const char *ln = jb.lst < 0 ? "U" : (jb.scan == 0 ? LN[jb.lst] : WN[jb.lst]);
        snprintf(tag, sizeof tag, "%s\t%s\t%s\t%d\t%d\t%d\t%c\t%c\t%d", jb.scan == 0 ? "AB" : "WW", ln,
                 jb.src == 0 ? "D" : jb.src == 1 ? (jb.scan == 0 ? "S" : "C") : "U", jb.i, jb.j, jb.r,
                 "xsr"[jb.op], jb.half == 0 ? 'T' : 'V', (int)n);
        lines[q] = malloc(2048); fmt(lines[q], 2048, tag, &s);
    }
    char p[1024]; snprintf(p, sizeof p, "%s_scan.tsv", outp);
    FILE *fo = fopen(p, "w");
    fprintf(fo, "scan\tlist\tsrc\ti\tj\tr\top\thalf\tn\thw_hist\td4_hist\tbit_ones\tmsmall\tzero\tcoll\tmaxm\tmodev\n");
    for (u64 q = 0; q < nj; q++) fputs(lines[q], fo);
    fclose(fo);
    // ---- joint scan ----
    snprintf(p, sizeof p, "%s_joint.tsv", outp);
    fo = fopen(p, "w");
    fprintf(fo, "list\tsrc\tr\thalf\tn\thwsum_hist(0..128)\td4sum_hist(0..64)\n");
    for (int h = 0; h < 2; h++) for (int l = -1; l < NL; l++) for (int src = 0; src < 2; src++) for (int r = 0; r < 32; r++) {
        if (l < 0 && src == 1) continue;
        u64 hh[129] = {0}, dh[65] = {0}; u64 off = (u64)h * n; u64 *pm = perm[h];
        for (u64 t = 0; t < n; t++) {
            int hs = 0, ds = 0;
            for (int w = 0; w < 4; w++) {
                u32 a, b;
                if (l < 0) { a = UA[w][off + t]; b = UB[w][off + t]; }
                else {
                    a = LA[l][w][off + t];
                    if (src == 1) { u64 pp = off + pm[t]; b = a ^ (LA[l][w][pp] ^ LB[l][w][pp]); }
                    else b = LB[l][w][off + t];
                }
                u32 x = b ^ rotl(a, r); hs += __builtin_popcount(x); ds += d4(x);
            }
            hh[hs]++; dh[ds]++;
        }
        fprintf(fo, "%s\t%s\t%d\t%c\t%llu\t", l < 0 ? "U" : LN[l], l < 0 ? "U" : (src ? "S" : "D"), r, h ? 'V' : 'T',
                (unsigned long long)n);
        for (int q = 0; q < 129; q++) fprintf(fo, "%s%llu", q ? "," : "", (unsigned long long)hh[q]);
        fprintf(fo, "\t");
        for (int q = 0; q < 65; q++) fprintf(fo, "%s%llu", q ? "," : "", (unsigned long long)dh[q]);
        fprintf(fo, "\n");
    }
    fclose(fo);
    fprintf(stderr, "done\n");
    return 0;
}
