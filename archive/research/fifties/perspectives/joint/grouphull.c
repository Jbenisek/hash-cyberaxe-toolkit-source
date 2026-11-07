// grouphull.c - conditional GF(2) structure of R inside one (context, member) group, over the WHOLE cube j < 2^21.
// Reuses the pkgCG algebra of ../data/gen.c (step CO + step CT up to E1/E3; no compression needed because
// R = K1 ^ K3 exactly, DATA.md). For each group: affine rank of {R(j)} after 2^10, 2^14 and 2^21 cube points, and
// whether 0 lies in the affine hull (every relation a.R = const has const = 0).
//   grouphull check <inputs.u32> <keys.u32>      recompute K1, K3 for every stored row and compare
//   grouphull <groups> <seed>
#define main gen_main_unused
#include "../data/gen.c"
#undef main
#include <omp.h>
#include <math.h>
static u64 mix(u64 z) { z += 0x9E3779B97F4A7C15ULL; z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL; z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL; return z ^ (z >> 31); }
static void keys_of(const ctx_t *o, u32 c1, u32 K1[4], u32 K3[4]) {
    u32 E1a1 = ROL(c1 - Y11, 16) ^ o->Y12, Y6 = E1a1 - o->Y1 - o->w[12], Y10 = ROL(Y6, 7) ^ o->C2b1, Y14 = Y10 - o->C2c1;
    u32 m[2][4], out1[2][4], out3[2][4];
    ghalf(o->Y1, Y6, Y11, o->Y12, o->w[12], o->w[5], m[0], out1[0]);
    ghalf(o->Y1, Y6, Y11B, o->Y12, o->w[12], o->w[5] + DELTA5, m[1], out1[1]);
    ghalf(Y3, o->Y4, o->Y9, Y14, 0, o->w[8], m[0], out3[0]);
    ghalf(Y3B, o->Y4, o->Y9, Y14, 0, o->w[8], m[1], out3[1]);
    K1[0] = out1[0][0] ^ out1[1][0]; K1[1] = out1[0][2] ^ out1[1][2]; K1[2] = out1[0][3] ^ out1[1][3]; K1[3] = out1[0][1] ^ out1[1][1];
    K3[0] = out3[0][2] ^ out3[1][2]; K3[1] = out3[0][0] ^ out3[1][0]; K3[2] = out3[0][1] ^ out3[1][1]; K3[3] = out3[0][3] ^ out3[1][3];
}
typedef struct { u64 v[128][2]; int has[128]; int rank; } basis_t;   // pivot = highest set bit
static int top(u64 lo, u64 hi) { return hi ? 64 + 63 - __builtin_clzll(hi) : lo ? 63 - __builtin_clzll(lo) : -1; }
static int insert(basis_t *B, u64 lo, u64 hi) {   // returns 1 if independent
    for (;;) { int t = top(lo, hi); if (t < 0) return 0; if (!B->has[t]) { B->has[t] = 1; B->v[t][0] = lo; B->v[t][1] = hi; B->rank++; return 1; } lo ^= B->v[t][0]; hi ^= B->v[t][1]; }
}
static int inspan(const basis_t *B, u64 lo, u64 hi) {
    for (;;) { int t = top(lo, hi); if (t < 0) return 1; if (!B->has[t]) return 0; lo ^= B->v[t][0]; hi ^= B->v[t][1]; }
}
static void init_consts(void) {
    u32 x[4] = {X3, X7, X11, X15}, xb[4] = {X3, X7, X11, X15};
    u32 K = IV[2] + IV[6];
    W4B = (((W4 + K) ^ LEN_A ^ LEN_B) - K); DELTA5 = W4 - W4B;
    gq(&x[0], &x[1], &x[2], &x[3], W4, W13); gq(&xb[0], &xb[1], &xb[2], &xb[3], W4B, W13);
    Y3 = x[0]; Y11 = x[2]; Y3B = xb[0]; Y11B = xb[2];
    K2A = K + W4; K2D = ROR(K2A ^ LEN_A, 16); K2C = IV[2] + K2D; K2B = ROR(IV[6] ^ K2C, 12);
}
int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: grouphull check <inputs.u32> <keys.u32> | grouphull <groups> <seed>\n"); return 1; }
    init_consts();
    if (Y3 != 0x8127C181 || Y11 != 0x7AF77F38 || Y11B - Y11 != 0x0A08818B || DELTA5 != 0xFFFFFFF8) { fprintf(stderr, "constants mismatch\n"); return 2; }
    if (!strcmp(argv[1], "check")) {
        FILE *fi = fopen(argv[2], "rb"), *fk = fopen(argv[3], "rb"); if (!fi || !fk) { perror("open"); return 4; }
        u32 in[12], ky[8]; u64 n = 0, bad = 0;
        while (fread(in, 4, 12, fi) == 12 && fread(ky, 4, 8, fk) == 8) {
            ctx_t o; u32 e1 = CLASS_VALUE | pdep(in[7], FREE_MASK), Y4 = e1 - Y3; step_co(in, Y4, &o);
            u32 K1[4], K3[4]; keys_of(&o, QVALUE | pdep(in[8], ~QMASK), K1, K3);
            for (int i = 0; i < 4; i++) if (K1[i] != ky[i] || K3[i] != ky[4 + i]) { bad++; break; }
            n++;
        }
        printf("check: %llu rows, %llu rows with a K1/K3 mismatch against keys.u32\n", (unsigned long long)n, (unsigned long long)bad);
        return bad ? 5 : 0;
    }
    u64 NG = strtoull(argv[1], 0, 0), seed = strtoull(argv[2], 0, 0);
    const u32 NJ = 1u << 21;
    u32 *c1tab = malloc(NJ * 4); for (u32 j = 0; j < NJ; j++) c1tab[j] = QVALUE | pdep(j, ~QMASK);
    int (*out)[8] = calloc(NG, sizeof *out);
    #pragma omp parallel for schedule(dynamic, 1)
    for (u64 g = 0; g < NG; g++) {
        u64 s0 = mix(seed ^ (g * 0x100000001B3ULL));
        u32 ow[7]; for (int i = 0; i < 7; i++) { s0 = mix(s0); ow[i] = (u32)(s0 >> 32); }
        s0 = mix(s0); u32 k = (u32)(s0 >> 45);
        ctx_t o; u32 e1 = CLASS_VALUE | pdep(k, FREE_MASK), Y4 = e1 - Y3; step_co(ow, Y4, &o);
        // random order of the cube so that the 2^10 / 2^14 prefixes are random subsets
        u32 *ord = malloc(NJ * 4); for (u32 j = 0; j < NJ; j++) ord[j] = j;
        for (u32 j = NJ - 1; j > 0; j--) { s0 = mix(s0); u32 r = (u32)(s0 % (j + 1)); u32 t = ord[j]; ord[j] = ord[r]; ord[r] = t; }
        basis_t *B = calloc(1, sizeof(basis_t)); u64 lo0 = 0, hi0 = 0; int r10 = 0, r14 = 0, z10 = 0, z14 = 0;
        for (u32 q = 0; q < NJ; q++) {
            u32 K1[4], K3[4]; keys_of(&o, c1tab[ord[q]], K1, K3);
            u64 lo = (u64)(K1[0] ^ K3[0]) | (u64)(K1[1] ^ K3[1]) << 32, hi = (u64)(K1[2] ^ K3[2]) | (u64)(K1[3] ^ K3[3]) << 32;
            if (q == 0) { lo0 = lo; hi0 = hi; continue; }
            if (B->rank < 128) insert(B, lo ^ lo0, hi ^ hi0);
            if (q + 1 == 1024) { r10 = B->rank; z10 = inspan(B, lo0, hi0); }
            if (q + 1 == 16384) { r14 = B->rank; z14 = inspan(B, lo0, hi0); }
        }
        out[g][0] = r10; out[g][1] = z10; out[g][2] = r14; out[g][3] = z14; out[g][4] = B->rank; out[g][5] = inspan(B, lo0, hi0); out[g][6] = (int)k;
        free(ord); free(B);
    }
    printf("grouphull: %llu groups (random 7 outer words + member k), whole cube 2^21 each, seed %s\n", (unsigned long long)NG, argv[2]);
    printf("group  k      rank@2^10 0in  rank@2^14 0in  rank@2^21 0in\n");
    int zfull = 0, zfalse10 = 0; double sr = 0;
    for (u64 g = 0; g < NG; g++) {
        printf("%5llu  %05x  %5d     %d    %5d     %d    %5d     %d\n", (unsigned long long)g, out[g][6], out[g][0], out[g][1], out[g][2], out[g][3], out[g][4], out[g][5]);
        zfull += out[g][5]; sr += out[g][4]; if (!out[g][1] && out[g][5]) zfalse10++;
    }
    printf("summary: mean full-cube rank %.2f ; groups with 0 in the full-cube hull %d of %llu ; groups the 2^10 sample excluded (0 not in its hull) but the full cube admits: %d\n",
           sr / NG, zfull, (unsigned long long)NG, zfalse10);
    return 0;
}
