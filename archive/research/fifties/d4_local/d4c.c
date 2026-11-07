// D4 local section 7 construction (Sol), full 32-bit width.
// Modes:
//   stats  <arm> <N> <seed> <dumpfile|-> <dumpmax>
//   struct <arm> <Nbase> <seed>
//   brute  <arm> <ninst> <seed>      (validate cycle solver vs full 2^32 scan)
//   bench  <N>                        (time of one 2-round compression, both sides)
// arm: none | len | flags
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef uint32_t u32;
typedef uint64_t u64;

static const u32 IV[8] = {0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au,
                          0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u};
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};

static inline u32 ror(u32 v, int r) { return (v >> r) | (v << (32 - r)); }
static inline u32 rol(u32 v, int r) { return (v << r) | (v >> (32 - r)); }

// ---------------- RNG (xoshiro256**) ----------------
static u64 rs[4];
static inline u64 rotl64(u64 x, int k) { return (x << k) | (x >> (64 - k)); }
static u64 rnd64(void) {
    u64 r = rotl64(rs[1] * 5, 7) * 9, t = rs[1] << 17;
    rs[2] ^= rs[0]; rs[3] ^= rs[1]; rs[1] ^= rs[2]; rs[0] ^= rs[3]; rs[2] ^= t; rs[3] = rotl64(rs[3], 45);
    return r;
}
static u32 rnd32(void) { return (u32)(rnd64() >> 32); }
static void seed_rng(u64 s) {
    for (int i = 0; i < 4; i++) { s += 0x9E3779B97F4A7C15ull; u64 z = s; z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull; z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; rs[i] = z ^ (z >> 31); }
}

// ---------------- operation counters ----------------
static u64 OPS_WORD = 0;     // 32-bit word ops (add/sub/xor/rot) in word-level steps
static u64 OPS_DP = 0;       // DP bit-transitions (one (state, zbit) pair evaluated)
static u64 N_SOLVES = 0;

// ---------------- G halves ----------------
typedef struct { u32 a1, b1, c1, d1, a2, b2, c2, d2; } gt;
static inline void g_first(u32 A, u32 B, u32 C, u32 D, u32 x, gt *t) {
    t->a1 = A + B + x; t->d1 = ror(D ^ t->a1, 16); t->c1 = C + t->d1; t->b1 = ror(B ^ t->c1, 12); OPS_WORD += 7;
}
static inline void g_second(gt *t, u32 y) {
    t->a2 = t->a1 + t->b1 + y; t->d2 = ror(t->d1 ^ t->a2, 8); t->c2 = t->c1 + t->d2; t->b2 = ror(t->b1 ^ t->c2, 7); OPS_WORD += 7;
}
// BPIN: known first half, prescribe final b = p -> unique y
static inline u32 bpin(const gt *t, u32 p) {
    u32 c2 = t->b1 ^ rol(p, 7); u32 d2 = c2 - t->c1; u32 a2 = t->d1 ^ rol(d2, 8); OPS_WORD += 8;
    return a2 - t->a1 - t->b1;
}

// ---------------- scalar cycle solver (exact carry graph) ----------------
// Solve for z: (PA + ROR_r(QA ^ z)) ^ (PB + ROR_r(QB ^ (z + delta))) == K
// State s = cin | cd<<1 | cA<<2 | cB<<3 ; output bit i uses z bit j=(i+r)&31.
typedef struct { u32 PA, QA, PB, QB, delta, K; int r; u64 N[33][16]; } solver_t;

static u64 solve_count(solver_t *S) {
    N_SOLVES++;
    for (int s = 0; s < 16; s++) S->N[32][s] = (((s >> 1) & 1) == (s & 1));
    for (int i = 31; i >= 0; --i) {
        int j = (i + S->r) & 31;
        int pa = (S->PA >> i) & 1, pb = (S->PB >> i) & 1, k = (S->K >> i) & 1;
        int qa = (S->QA >> j) & 1, qb = (S->QB >> j) & 1, dj = (S->delta >> j) & 1;
        for (int s = 0; s < 16; s++) {
            int cin = s & 1, cd = (s >> 1) & 1, cA = (s >> 2) & 1, cB = (s >> 3) & 1;
            if (j == 0) cd = 0;
            u64 tot = 0;
            for (int zb = 0; zb < 2; zb++) {
                int sb = zb ^ dj ^ cd, cd2 = (zb & dj) | (zb & cd) | (dj & cd);
                int eA = qa ^ zb, eB = qb ^ sb;
                int fA = pa ^ eA ^ cA, fB = pb ^ eB ^ cB;
                if ((fA ^ fB) != k) continue;
                int cA2 = (pa & eA) | (pa & cA) | (eA & cA), cB2 = (pb & eB) | (pb & cB) | (eB & cB);
                tot += S->N[i + 1][cin | cd2 << 1 | cA2 << 2 | cB2 << 3];
            }
            S->N[i][s] = tot;
        }
    }
    OPS_DP += 32 * 16 * 2;
    return S->N[0][0] + S->N[0][3];
}
static u32 solve_root(const solver_t *S, u64 idx) {
    int s; if (idx < S->N[0][0]) s = 0; else { idx -= S->N[0][0]; s = 3; }
    u32 z = 0;
    for (int i = 0; i < 32; i++) {
        int j = (i + S->r) & 31;
        int pa = (S->PA >> i) & 1, pb = (S->PB >> i) & 1, k = (S->K >> i) & 1;
        int qa = (S->QA >> j) & 1, qb = (S->QB >> j) & 1, dj = (S->delta >> j) & 1;
        int cin = s & 1, cd = (s >> 1) & 1, cA = (s >> 2) & 1, cB = (s >> 3) & 1;
        if (j == 0) cd = 0;
        int chosen = -1, ns = 0;
        for (int zb = 0; zb < 2; zb++) {
            int sb = zb ^ dj ^ cd, cd2 = (zb & dj) | (zb & cd) | (dj & cd);
            int eA = qa ^ zb, eB = qb ^ sb;
            int fA = pa ^ eA ^ cA, fB = pb ^ eB ^ cB;
            if ((fA ^ fB) != k) continue;
            int cA2 = (pa & eA) | (pa & cA) | (eA & cA), cB2 = (pb & eB) | (pb & cB) | (eB & cB);
            int s2 = cin | cd2 << 1 | cA2 << 2 | cB2 << 3;
            u64 c = S->N[i + 1][s2];
            if (idx < c) { chosen = zb; ns = s2; break; }
            idx -= c;
        }
        if (chosen < 0) { fprintf(stderr, "solve_root: index out of range\n"); exit(3); }
        z |= (u32)chosen << j; s = ns;
    }
    OPS_DP += 64;
    return z;
}
static inline u32 cyc_eval(const solver_t *S, u32 z) {
    return (S->PA + ror(S->QA ^ z, S->r)) ^ (S->PB + ror(S->QB ^ (z + S->delta), S->r));
}

// ---------------- construction ----------------
typedef struct {
    u32 m1, m5, A0, A2, A3, A4, A6, A7, B0, B4, B6, alpha1hi; int h;
    u64 u1[4], u2[4];          // root-choice uniforms (FIRST, SECOND) per diagonal
    int64_t ovr1[4], ovr2[4];  // overrides of root index (-1 none)
} free_t;

typedef struct {
    u32 mA[16], mB[16], hA[4], hB[4];
    u32 UA[16], UB[16], XA[16], XB[16];
    u32 e[4];                 // D_j residual XOR (0 = pass)
    u64 c1[4], c2first[4];    // FIRST count; SECOND count for first-tried FIRST root
    int first_ok[4], second_ok_first[4], diag_ok[4], diag_ok_first[4];
    u64 idx1[4], idx2[4], c2[4]; // chosen indices / final SECOND count
    u64 tried1[4], fws[4], pairs[4]; // FIRST roots tried, FIRST roots with a SECOND root, total (x,y) pairs over tried roots
    int complete, complete_first;
    u32 d10, d13;
} cons_t;

static u64 RETRY_CAP = 16;   // FIRST roots tried until a SECOND root exists
static int COUNT_ALL = 0;     // if set, keep scanning all FIRST roots (up to RETRY_CAP) to count (x,y) pairs
static int EARLY = 0;         // if set, stop at the first diagonal that has no (x,y) pair (cost measurement)
static int COLS_ONLY = 0;     // if set, construct() stops after the column stage (U, d10, d13)
static const int DG[4][4] = {{0, 5, 10, 15}, {1, 6, 11, 12}, {2, 7, 8, 13}, {3, 4, 9, 14}};

static inline u64 pick(u64 u, u64 cnt) { return (u64)(((unsigned __int128)u * cnt) >> 64); }

static int construct(const free_t *F, const u32 hA[4], const u32 hB[4], cons_t *C) {
    u32 vA[16], vB[16];
    for (int i = 0; i < 8; i++) vA[i] = vB[i] = IV[i];
    for (int i = 0; i < 4; i++) { vA[8 + i] = vB[8 + i] = IV[i]; vA[12 + i] = hA[i]; vB[12 + i] = hB[i]; C->hA[i] = hA[i]; C->hB[i] = hB[i]; }
    u32 *mA = C->mA, *mB = C->mB;
    memset(mA, 0, 64); memset(mB, 0, 64);
    mA[1] = mB[1] = F->m1; mA[5] = mB[5] = F->m5;
    mA[0] = F->A0; mA[2] = F->A2; mA[3] = F->A3; mA[4] = F->A4; mA[6] = F->A6; mA[7] = F->A7;
    mB[0] = F->B0; mB[4] = F->B4; mB[6] = F->B6;
    gt cA[4], cB[4];
    // 7.1 columns 0,2 full; column 3 first half; column 1 side A full
    g_first(vA[0], vA[4], vA[8], vA[12], mA[0], &cA[0]); g_second(&cA[0], mA[1]);
    g_first(vB[0], vB[4], vB[8], vB[12], mB[0], &cB[0]); g_second(&cB[0], mB[1]);
    g_first(vA[2], vA[6], vA[10], vA[14], mA[4], &cA[2]); g_second(&cA[2], mA[5]);
    g_first(vB[2], vB[6], vB[10], vB[14], mB[4], &cB[2]); g_second(&cB[2], mB[5]);
    g_first(vA[3], vA[7], vA[11], vA[15], mA[6], &cA[3]);
    g_first(vB[3], vB[7], vB[11], vB[15], mB[6], &cB[3]);
    g_first(vA[1], vA[5], vA[9], vA[13], mA[2], &cA[1]); g_second(&cA[1], mA[3]);
    g_second(&cA[3], mA[7]);
    // alpha_1B: high 31 bits free, bit0 pinned
    u32 alpha = F->alpha1hi & ~1u;
    u32 t_d1 = ror(vB[13] ^ alpha, 16), t_c1 = vB[9] + t_d1, t_b1 = ror(vB[5] ^ t_c1, 12);
    OPS_WORD += 6;
    u32 bit = (cA[1].a1 ^ cA[1].b1 ^ t_b1 ^ cA[2].b2 ^ cB[2].b2) & 1; OPS_WORD += 4;
    alpha |= bit;
    mB[2] = alpha - vB[1] - vB[5]; OPS_WORD += 2;
    g_first(vB[1], vB[5], vB[9], vB[13], mB[2], &cB[1]);
    if (cB[1].a1 != alpha || ((cB[1].b1 ^ t_b1) & 1)) { fprintf(stderr, "alpha pin broken\n"); exit(4); }
    // P0 via BPIN -> m3_B
    u32 tgt5 = cA[1].b2 - (cB[0].a2 - cA[0].a2) - (mB[2] - mA[2]) - (mB[6] - mA[6]); OPS_WORD += 6;
    mB[3] = bpin(&cB[1], tgt5); g_second(&cB[1], mB[3]);
    if (cB[1].b2 != tgt5) { fprintf(stderr, "P0 broken\n"); exit(4); }
    // P2 via BPIN -> m7_B
    u32 tgt7 = cA[3].b2 + (cB[3].a1 - cA[3].a1) + (cB[3].b1 - cA[3].b1) + (cB[0].b2 - cA[0].b2)
             + (mB[4] - mA[4]) - (cB[2].a2 - cA[2].a2) - (mB[0] - mA[0]); OPS_WORD += 13;
    mB[7] = bpin(&cB[3], tgt7); g_second(&cB[3], mB[7]);
    if (cB[3].b2 != tgt7) { fprintf(stderr, "P2 broken\n"); exit(4); }
    u32 *UA = C->UA, *UB = C->UB;
    for (int j = 0; j < 4; j++) {
        UA[j] = cA[j].a2; UA[j + 4] = cA[j].b2; UA[j + 8] = cA[j].c2; UA[j + 12] = cA[j].d2;
        UB[j] = cB[j].a2; UB[j + 4] = cB[j].b2; UB[j + 8] = cB[j].c2; UB[j + 12] = cB[j].d2;
    }
    u32 d13 = 0u - (UB[3] - UA[3]) - (UB[4] - UA[4]) - (mB[4] - mA[4]);
    u32 R = (UB[1] - UA[1]) + (UB[6] - UA[6]) + (mB[3] - mA[3]); OPS_WORD += 12;
    if (R & 1) { fprintf(stderr, "R odd\n"); exit(4); }
    u32 d10 = ((0u - R) >> 1) + ((u32)(F->h & 1) << 31);
    C->d10 = d10; C->d13 = d13;
    u32 DX[4] = {0, d10, 0, 0}, DY[4] = {0, 0, d13, 0};
    // default (pre-cycle) values of the differing diagonal words: m10_B-m10_A=d10, m13_B-m13_A=d13
    mA[10] = 0; mB[10] = d10; mA[13] = 0; mB[13] = d13;
    if (COLS_ONLY) return 0;
    // 7.2 diagonals
    static solver_t S1, S2;
    C->complete = 1; C->complete_first = 1;
    for (int k = 0; k < 4; k++) {
        int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
        int sx = 8 + 2 * k, sy = 9 + 2 * k;
        S1.PA = UA[c]; S1.QA = UA[d]; S1.PB = UB[c]; S1.QB = UB[d]; S1.r = 16;
        S1.delta = (UB[a] + UB[b] + DX[k]) - (UA[a] + UA[b]); S1.K = UA[b] ^ UB[b]; OPS_WORD += 6;
        u64 n1 = solve_count(&S1);
        C->c1[k] = n1; C->first_ok[k] = n1 > 0;
        C->second_ok_first[k] = 0; C->c2first[k] = 0; C->diag_ok[k] = 0; C->diag_ok_first[k] = 0; C->c2[k] = 0;
        C->tried1[k] = 0; C->fws[k] = 0; C->pairs[k] = 0;
        if (!n1) { C->complete = 0; C->complete_first = 0; if (EARLY) return 0; continue; }
        u64 start = F->ovr1[k] >= 0 ? (u64)F->ovr1[k] % n1 : pick(F->u1[k], n1);
        u64 tries = F->ovr1[k] >= 0 ? 1 : (n1 < RETRY_CAP ? n1 : RETRY_CAP);
        int done = 0;
        for (u64 t = 0; t < tries && (!done || COUNT_ALL); t++) {
            u64 i1 = (start + t) % n1;
            u32 z = solve_root(&S1, i1);
            if (cyc_eval(&S1, z) != S1.K) { fprintf(stderr, "FIRST root wrong\n"); exit(5); }
            u32 xA = z - UA[a] - UA[b], xB = xA + DX[k]; OPS_WORD += 4;
            gt gA, gB;
            g_first(UA[a], UA[b], UA[c], UA[d], xA, &gA);
            g_first(UB[a], UB[b], UB[c], UB[d], xB, &gB);
            if (gA.b1 != gB.b1) { fprintf(stderr, "FIRST b1 mismatch\n"); exit(5); }
            S2.PA = gA.c1; S2.QA = gA.d1; S2.PB = gB.c1; S2.QB = gB.d1; S2.r = 8;
            S2.delta = gB.a1 - gA.a1 + DY[k]; S2.K = 0; OPS_WORD += 2;
            u64 n2 = solve_count(&S2);
            if (t == 0) { C->c2first[k] = n2; C->second_ok_first[k] = n2 > 0; }
            C->tried1[k]++; C->fws[k] += n2 > 0; C->pairs[k] += n2;
            if (!n2 || done) continue;
            u64 i2 = F->ovr2[k] >= 0 ? (u64)F->ovr2[k] % n2 : pick(F->u2[k], n2);
            u32 z2 = solve_root(&S2, i2);
            if (cyc_eval(&S2, z2) != 0) { fprintf(stderr, "SECOND root wrong\n"); exit(5); }
            u32 yA = z2 - gA.a1 - gA.b1, yB = yA + DY[k]; OPS_WORD += 3;
            g_second(&gA, yA); g_second(&gB, yB);
            if (gA.c2 != gB.c2 || gA.b2 != gB.b2) { fprintf(stderr, "SECOND mismatch\n"); exit(5); }
            mA[sx] = xA; mB[sx] = xB; mA[sy] = yA; mB[sy] = yB;
            C->XA[a] = gA.a2; C->XA[b] = gA.b2; C->XA[c] = gA.c2; C->XA[d] = gA.d2;
            C->XB[a] = gB.a2; C->XB[b] = gB.b2; C->XB[c] = gB.c2; C->XB[d] = gB.d2;
            C->idx1[k] = i1; C->idx2[k] = i2; C->c2[k] = n2;
            done = 1; if (t == 0) C->diag_ok_first[k] = 1;
        }
        C->diag_ok[k] = done;
        if (!done) C->complete = 0;
        if (!done && EARLY) { for (int q = k + 1; q < 4; q++) { C->first_ok[q] = 0; C->diag_ok[q] = 0; C->diag_ok_first[q] = 0; C->c1[q] = 0; C->tried1[q] = 0; C->fws[q] = 0; C->pairs[q] = 0; C->second_ok_first[q] = 0; C->c2first[q] = 0; } C->complete_first = 0; return 0; }
        if (!C->diag_ok_first[k]) C->complete_first = 0;
    }
    if (!C->complete) return 0;
    // 7.3 checks (internal self-check; organizer-code verification is done in Python)
    u32 *XA = C->XA, *XB = C->XB;
    for (int i = 4; i < 12; i++) if (XA[i] != XB[i]) { fprintf(stderr, "boundary b/c mismatch\n"); exit(6); }
    for (int j = 0; j < 4; j++) {
        u32 xa = mA[PERM[2 * j]], xb = mB[PERM[2 * j]], ya = mA[PERM[2 * j + 1]], yb = mB[PERM[2 * j + 1]];
        u32 S = (XB[j] - XA[j]) + (xb - xa) + (yb - ya);
        if (S) { fprintf(stderr, "S%d nonzero\n", j); exit(6); }
        C->e[j] = (XA[j + 12] ^ (XA[j] + XA[j + 4] + xa)) ^ (XB[j + 12] ^ (XB[j] + XB[j + 4] + xb));
        OPS_WORD += 9;
    }
    return 1;
}

static void rand_free(free_t *F) {
    F->m1 = rnd32(); F->m5 = rnd32(); F->A0 = rnd32(); F->A2 = rnd32(); F->A3 = rnd32(); F->A4 = rnd32();
    F->A6 = rnd32(); F->A7 = rnd32(); F->B0 = rnd32(); F->B4 = rnd32(); F->B6 = rnd32(); F->alpha1hi = rnd32();
    F->h = rnd32() & 1;
    for (int k = 0; k < 4; k++) { F->u1[k] = rnd64(); F->u2[k] = rnd64(); F->ovr1[k] = -1; F->ovr2[k] = -1; }
}

static void set_arm(const char *arm, u32 hA[4], u32 hB[4]) {
    hA[0] = 0; hA[1] = 0; hA[2] = 64; hA[3] = 11;
    memcpy(hB, hA, 16);
    if (!strcmp(arm, "none")) {}
    else if (!strcmp(arm, "len")) hB[2] = 63;
    else if (!strcmp(arm, "flags")) hB[3] = 3;
    else { fprintf(stderr, "bad arm\n"); exit(1); }
}

static double now(void) { struct timespec t; clock_gettime(CLOCK_MONOTONIC, &t); return t.tv_sec + 1e-9 * t.tv_nsec; }

// ---------------- stats mode ----------------
#define MAXH 8
static int mode_stats(const char *arm, u64 N, u64 seed, const char *dump, u64 dumpmax) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    FILE *fd = NULL; if (strcmp(dump, "-")) fd = fopen(dump, "wb");
    u64 first_zero[4] = {0}, second_zero_first[4] = {0}, second_den[4] = {0}, diag_ok[4] = {0}, diag_okf[4] = {0};
    long double sum_c1[4] = {0}, sum_c2[4] = {0};
    u64 hist1[4][MAXH + 1] = {{0}}, hist2[4][MAXH + 1] = {{0}};
    u64 big1[4] = {0}, big2[4] = {0}; u64 max1[4] = {0}, max2[4] = {0};
    u64 comp = 0, compf = 0, dumped = 0;
    long double sum_pairs[4] = {0}, sum_fws[4] = {0}, sum_tried[4] = {0}; u64 maxpairs[4] = {0};
    u64 joint2[6] = {0}; // pairs of diagonals both solvable (with retry)
    u64 single[4][17] = {{0}}, all4[17] = {0}, pair[6][17] = {{0}}, trip[4][17] = {{0}};
    u64 bitset[4][32] = {{0}}, efull[4] = {0};
    const int PI[6][2] = {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}};
    const int TI[4][3] = {{1, 2, 3}, {0, 2, 3}, {0, 1, 3}, {0, 1, 2}};
    OPS_WORD = OPS_DP = N_SOLVES = 0;
    double t0 = now();
    free_t F; cons_t C;
    for (u64 n = 0; n < N; n++) {
        rand_free(&F);
        int ok = construct(&F, hA, hB, &C);
        for (int k = 0; k < 4; k++) {
            if (!C.first_ok[k]) first_zero[k]++;
            else { second_den[k]++; if (!C.second_ok_first[k]) second_zero_first[k]++; sum_c2[k] += C.c2first[k];
                   if (C.c2first[k] <= MAXH) hist2[k][C.c2first[k]]++; else big2[k]++; if (C.c2first[k] > max2[k]) max2[k] = C.c2first[k]; }
            sum_c1[k] += C.c1[k];
            if (C.c1[k] <= MAXH) hist1[k][C.c1[k]]++; else big1[k]++; if (C.c1[k] > max1[k]) max1[k] = C.c1[k];
            diag_ok[k] += C.diag_ok[k]; diag_okf[k] += C.diag_ok_first[k];
            sum_pairs[k] += C.pairs[k]; sum_fws[k] += C.fws[k]; sum_tried[k] += C.tried1[k]; if (C.pairs[k] > maxpairs[k]) maxpairs[k] = C.pairs[k];
        }
        { const int PI2[6][2] = {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}};
          for (int p = 0; p < 6; p++) joint2[p] += C.diag_ok[PI2[p][0]] & C.diag_ok[PI2[p][1]]; }
        compf += C.complete_first;
        if (fd && dumped < dumpmax && (C.diag_ok[0] | C.diag_ok[1] | C.diag_ok[2] | C.diag_ok[3])) {
            u32 fl = 0; for (int k = 0; k < 4; k++) fl |= (u32)C.diag_ok[k] << k | (u32)C.first_ok[k] << (4 + k);
            fl |= (u32)ok << 8; u32 ee[4] = {0, 0, 0, 0}; if (ok) memcpy(ee, C.e, 16);
            fwrite(C.mA, 4, 16, fd); fwrite(C.mB, 4, 16, fd); fwrite(C.hA, 4, 4, fd); fwrite(C.hB, 4, 4, fd); fwrite(&fl, 4, 1, fd); fwrite(ee, 4, 4, fd);
            dumped++;
        }
        if (!ok) continue;
        comp++;
        for (int j = 0; j < 4; j++) { for (int i = 0; i < 32; i++) bitset[j][i] += (C.e[j] >> i) & 1; efull[j] += (C.e[j] == 0); }
        for (int k = 1; k <= 16; k++) {
            u32 msk = (1u << k) - 1; int z[4];
            for (int j = 0; j < 4; j++) { z[j] = (C.e[j] & msk) == 0; single[j][k] += z[j]; }
            all4[k] += z[0] & z[1] & z[2] & z[3];
            for (int p = 0; p < 6; p++) pair[p][k] += z[PI[p][0]] & z[PI[p][1]];
            for (int t = 0; t < 4; t++) trip[t][k] += z[TI[t][0]] & z[TI[t][1]] & z[TI[t][2]];
        }
    }
    double t1 = now();
    if (fd) fclose(fd);
    printf("arm %s N %llu seed %llu\n", arm, (unsigned long long)N, (unsigned long long)seed);
    printf("complete_with_retry %llu frac %.6f ; complete_single_try %llu frac %.6f ; dumped %llu\n",
           (unsigned long long)comp, (double)comp / N, (unsigned long long)compf, (double)compf / N, (unsigned long long)dumped);
    for (int k = 0; k < 4; k++) {
        printf("diag D%d: FIRST zero %.6f mean %.4Lf max %llu | SECOND(first-tried) zero %.6f mean %.4Lf max %llu | diag ok single %.6f retry %.6f\n", k,
               (double)first_zero[k] / N, sum_c1[k] / N, (unsigned long long)max1[k],
               (double)second_zero_first[k] / second_den[k], sum_c2[k] / second_den[k], (unsigned long long)max2[k],
               (double)diag_okf[k] / N, (double)diag_ok[k] / N);
        printf("  hist FIRST 0..%d:", MAXH); for (int i = 0; i <= MAXH; i++) printf(" %llu", (unsigned long long)hist1[k][i]); printf(" >%d:%llu\n", MAXH, (unsigned long long)big1[k]);
        printf("  hist SECOND 0..%d:", MAXH); for (int i = 0; i <= MAXH; i++) printf(" %llu", (unsigned long long)hist2[k][i]); printf(" >%d:%llu\n", MAXH, (unsigned long long)big2[k]);
        printf("  over all samples: mean FIRST roots tried %.3Lf, mean FIRST roots with SECOND root %.4Lf, mean (x,y) pairs %.4Lf (max %llu); given FIRST solvable: P(diag solvable) %.4f\n",
               sum_tried[k] / N, sum_fws[k] / N, sum_pairs[k] / N, (unsigned long long)maxpairs[k],
               (N - first_zero[k]) ? (double)diag_ok[k] / (N - first_zero[k]) : 0);
    }
    printf("RETRY_CAP %llu COUNT_ALL %d\n", (unsigned long long)RETRY_CAP, COUNT_ALL);
    printf("joint diag-solvable pairs (01 02 03 12 13 23):"); for (int p = 0; p < 6; p++) printf(" %llu", (unsigned long long)joint2[p]); printf("\n");
    printf("time %.3f s ; ns/sample %.1f ; ns/complete %.1f\n", t1 - t0, 1e9 * (t1 - t0) / N, comp ? 1e9 * (t1 - t0) / comp : 0);
    printf("ops: word %llu dp_transitions %llu solves %llu ; per complete: word %.1f dp %.1f solves %.3f\n",
           (unsigned long long)OPS_WORD, (unsigned long long)OPS_DP, (unsigned long long)N_SOLVES,
           comp ? (double)OPS_WORD / comp : 0, comp ? (double)OPS_DP / comp : 0, comp ? (double)N_SOLVES / comp : 0);
    printf("D full-width pass counts:"); for (int j = 0; j < 4; j++) printf(" %llu", (unsigned long long)efull[j]); printf("\n");
    for (int k = 1; k <= 16; k++) {
        printf("k %2d single", k); for (int j = 0; j < 4; j++) printf(" %llu", (unsigned long long)single[j][k]);
        printf(" | pairs"); for (int p = 0; p < 6; p++) printf(" %llu", (unsigned long long)pair[p][k]);
        printf(" | trip"); for (int t = 0; t < 4; t++) printf(" %llu", (unsigned long long)trip[t][k]);
        printf(" | all4 %llu\n", (unsigned long long)all4[k]);
    }
    for (int j = 0; j < 4; j++) { printf("bitfreq e%d:", j); for (int i = 0; i < 32; i++) printf(" %.4f", comp ? (double)bitset[j][i] / comp : 0); printf("\n"); }
    return 0;
}

// ---------------- struct mode: which free inputs move which D_j ----------------
#define NP 37
static const char *PNAME[NP] = {
    "m1", "m5", "A.m0", "A.m2", "A.m3", "A.m4", "A.m6", "A.m7", "B.m0", "B.m4", "B.m6", "alpha1hi", "h",
    "D0.FIRSTroot", "D0.SECONDroot", "D1.FIRSTroot", "D1.SECONDroot", "D2.FIRSTroot", "D2.SECONDroot", "D3.FIRSTroot", "D3.SECONDroot",
    "m1^b31", "m5^b31", "A.m0^b31", "A.m2^b31", "A.m3^b31", "A.m4^b31", "A.m6^b31", "A.m7^b31", "B.m0^b31", "B.m4^b31", "B.m6^b31", "alpha1hi^b31",
    "m1^b0", "A.m3^b0", "B.m6^b0", "alpha1hi^b1"};
static u32 *fword(free_t *F, int w) {
    switch (w) { case 0: return &F->m1; case 1: return &F->m5; case 2: return &F->A0; case 3: return &F->A2; case 4: return &F->A3;
        case 5: return &F->A4; case 6: return &F->A6; case 7: return &F->A7; case 8: return &F->B0; case 9: return &F->B4;
        case 10: return &F->B6; default: return &F->alpha1hi; }
}
static int mode_struct(const char *arm, u64 NB, u64 seed) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    u64 app[NP] = {0}, cmp[NP] = {0}, eqf[NP][4] = {{0}}, eq8[NP][4] = {{0}}, eqm[NP] = {0}, ew[NP][4] = {{0}};
    free_t F, G; cons_t C, D; u64 bases = 0, tried = 0;
    while (bases < NB) {
        rand_free(&F); tried++;
        if (!construct(&F, hA, hB, &C)) continue;
        bases++;
        for (int p = 0; p < NP; p++) {
            G = F;
            if (p <= 11) { u32 *w = fword(&G, p); u32 old = *w; do *w = rnd32(); while (*w == old); }
            else if (p == 12) G.h ^= 1;
            else if (p <= 20) {
                int k = (p - 13) / 2, sec = (p - 13) & 1;
                if (!sec) { if (C.c1[k] < 2) continue; G.ovr1[k] = (int64_t)((C.idx1[k] + 1) % C.c1[k]); }
                else { if (C.c2[k] < 2) continue; G.ovr1[k] = (int64_t)C.idx1[k]; G.ovr2[k] = (int64_t)((C.idx2[k] + 1) % C.c2[k]); }
            }
            else if (p <= 32) { *fword(&G, p - 21) ^= 0x80000000u; }
            else if (p == 33) G.m1 ^= 1; else if (p == 34) G.A3 ^= 1; else if (p == 35) G.B6 ^= 1; else G.alpha1hi ^= 2;
            app[p]++;
            if (!construct(&G, hA, hB, &D)) continue;
            cmp[p]++;
            int sameall = 1;
            for (int j = 0; j < 4; j++) {
                eqf[p][j] += D.e[j] == C.e[j]; eq8[p][j] += ((D.e[j] ^ C.e[j]) & 0xFF) == 0;
                ew[p][j] += __builtin_popcount(D.e[j] ^ C.e[j]);
                if (D.e[j] != C.e[j]) sameall = 0;
            }
            eqm[p] += sameall;
        }
    }
    printf("arm %s bases %llu (tried %llu)\n", arm, (unsigned long long)bases, (unsigned long long)tried);
    printf("%-16s %8s %8s | P(e_j unchanged) j=0..3 | P(low8 unchanged) j=0..3 | mean HW(e_j change)\n", "perturb", "applic", "complete");
    for (int p = 0; p < NP; p++) {
        printf("%-16s %8llu %8llu |", PNAME[p], (unsigned long long)app[p], (unsigned long long)cmp[p]);
        for (int j = 0; j < 4; j++) printf(" %.4f", cmp[p] ? (double)eqf[p][j] / cmp[p] : -1);
        printf(" |"); for (int j = 0; j < 4; j++) printf(" %.4f", cmp[p] ? (double)eq8[p][j] / cmp[p] : -1);
        printf(" |"); for (int j = 0; j < 4; j++) printf(" %.2f", cmp[p] ? (double)ew[p][j] / cmp[p] : -1);
        printf("\n");
    }
    return 0;
}

// ---------------- brute mode: solver vs 2^32 scan ----------------
static int mode_brute(const char *arm, int ninst, u64 seed) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    static solver_t S; int done = 0, bad = 0; u64 tries = 0;
    while (done < ninst) {
        // build a random U pair via the construction's column stage by running construct and grabbing diag-0 inputs
        free_t F; cons_t C; rand_free(&F); tries++;
        construct(&F, hA, hB, &C);
        int k = done % 4; int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
        u32 dx = k == 1 ? C.d10 : 0;
        S.PA = C.UA[c]; S.QA = C.UA[d]; S.PB = C.UB[c]; S.QB = C.UB[d]; S.r = 16;
        S.delta = (C.UB[a] + C.UB[b] + dx) - (C.UA[a] + C.UA[b]); S.K = C.UA[b] ^ C.UB[b];
        if (done & 1) { // SECOND-type instance with r=8 and random first-half values
            S.r = 8; S.PA = rnd32(); S.PB = rnd32(); S.QA = rnd32(); S.QB = rnd32(); S.delta = rnd32(); S.K = 0;
        }
        u64 n = solve_count(&S);
        if ((done < ninst / 2) && n < 2 && tries < 20000) continue; // prefer multi-root instances for half of them
        u64 bn = 0; u32 firstz = 0; int hadfirst = 0;
        for (u64 z = 0; z < (1ull << 32); z++) if (cyc_eval(&S, (u32)z) == S.K) { if (!hadfirst) { firstz = (u32)z; hadfirst = 1; } bn++; }
        // check every DP root is a true root
        int rootsbad = 0; for (u64 i = 0; i < n && i < 1000; i++) if (cyc_eval(&S, solve_root(&S, i)) != S.K) rootsbad++;
        printf("inst %d r=%d dp_count %llu brute_count %llu rootsbad %d %s\n", done, S.r, (unsigned long long)n, (unsigned long long)bn, rootsbad,
               (n == bn && !rootsbad) ? "OK" : "MISMATCH");
        if (n != bn || rootsbad) bad++;
        (void)firstz; done++; tries = 0;
    }
    printf("brute summary: %d instances, %d mismatches\n", ninst, bad);
    return bad != 0;
}

// roots: for solvable diagonals, enumerate all (x,y) pairs and count how many distinct values reach the D checks
static int cmpu32(const void *a, const void *b) { u32 x = *(const u32 *)a, y = *(const u32 *)b; return x < y ? -1 : x > y; }
static u64 ndistinct(u32 *v, u64 n, u32 mask) {
    for (u64 i = 0; i < n; i++) v[i] &= mask;
    qsort(v, n, 4, cmpu32); u64 d = n ? 1 : 0; for (u64 i = 1; i < n; i++) d += v[i] != v[i - 1]; return d;
}
static int mode_roots(const char *arm, u64 want, u64 seed, u64 cap) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    static solver_t S1, S2;
    u32 *va = malloc(cap * 4), *vb = malloc(cap * 4), *vd = malloc(cap * 4), *tmp = malloc(cap * 4);
    u64 got = 0, samples = 0;
    long double s_pairs = 0, s_da = 0, s_db = 0, s_dd = 0, s_da8 = 0, s_db8 = 0, s_dd8 = 0;
    printf("arm %s: per solvable diagonal: k pairs fws distinct(XaA) distinct(Xb) distinct(XdA^XdB) | low8 distinct: XaA Xb dXOR\n", arm);
    while (got < want) {
        free_t F; cons_t C; rand_free(&F); samples++;
        construct(&F, hA, hB, &C);
        for (int k = 0; k < 4; k++) {
            if (!C.diag_ok[k] || got >= want) continue;
            int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
            u32 dx = k == 1 ? C.d10 : 0, dy = k == 2 ? C.d13 : 0;
            S1.PA = C.UA[c]; S1.QA = C.UA[d]; S1.PB = C.UB[c]; S1.QB = C.UB[d]; S1.r = 16;
            S1.delta = (C.UB[a] + C.UB[b] + dx) - (C.UA[a] + C.UA[b]); S1.K = C.UA[b] ^ C.UB[b];
            u64 n1 = solve_count(&S1), np = 0, fws = 0;
            for (u64 i1 = 0; i1 < n1 && np < cap; i1++) {
                u32 xA = solve_root(&S1, i1) - C.UA[a] - C.UA[b];
                gt gA, gB; g_first(C.UA[a], C.UA[b], C.UA[c], C.UA[d], xA, &gA); g_first(C.UB[a], C.UB[b], C.UB[c], C.UB[d], xA + dx, &gB);
                S2.PA = gA.c1; S2.QA = gA.d1; S2.PB = gB.c1; S2.QB = gB.d1; S2.r = 8; S2.delta = gB.a1 - gA.a1 + dy; S2.K = 0;
                u64 n2 = solve_count(&S2); fws += n2 > 0;
                for (u64 i2 = 0; i2 < n2 && np < cap; i2++) {
                    u32 yA = solve_root(&S2, i2) - gA.a1 - gA.b1;
                    gt hA2 = gA, hB2 = gB; g_second(&hA2, yA); g_second(&hB2, yA + dy);
                    if (hA2.b2 != hB2.b2 || hA2.c2 != hB2.c2) { fprintf(stderr, "roots: mismatch\n"); exit(7); }
                    va[np] = hA2.a2; vb[np] = hA2.b2; vd[np] = hA2.d2 ^ hB2.d2; np++;
                }
            }
            u64 da, db, dd, da8, db8, dd8;
            memcpy(tmp, va, np * 4); da = ndistinct(tmp, np, ~0u); memcpy(tmp, va, np * 4); da8 = ndistinct(tmp, np, 0xFF);
            memcpy(tmp, vb, np * 4); db = ndistinct(tmp, np, ~0u); memcpy(tmp, vb, np * 4); db8 = ndistinct(tmp, np, 0xFF);
            memcpy(tmp, vd, np * 4); dd = ndistinct(tmp, np, ~0u); memcpy(tmp, vd, np * 4); dd8 = ndistinct(tmp, np, 0xFF);
            printf("D%d %llu %llu %llu %llu %llu | %llu %llu %llu\n", k, (unsigned long long)np, (unsigned long long)fws, (unsigned long long)da,
                   (unsigned long long)db, (unsigned long long)dd, (unsigned long long)da8, (unsigned long long)db8, (unsigned long long)dd8);
            s_pairs += np; s_da += da; s_db += db; s_dd += dd; s_da8 += da8; s_db8 += db8; s_dd8 += dd8;
            got++;
        }
    }
    printf("summary arm %s: solvable diagonals %llu from %llu samples; mean pairs %.1Lf, mean distinct XaA %.1Lf Xb %.1Lf dXOR(Xd) %.1Lf ; low8: %.1Lf %.1Lf %.1Lf\n",
           arm, (unsigned long long)got, (unsigned long long)samples, s_pairs / got, s_da / got, s_db / got, s_dd / got, s_da8 / got, s_db8 / got, s_dd8 / got);
    return 0;
}

// keep: on bases with a solved diagonal k, perturb one free input and test whether diagonal k stays solvable
static int mode_keep(const char *arm, u64 NB, u64 seed) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    u64 app[NP] = {0}, keep[NP] = {0}, same[NP] = {0};
    free_t F, G; cons_t C, D; u64 bases = 0, samples = 0;
    while (bases < NB) {
        rand_free(&F); samples++;
        construct(&F, hA, hB, &C);
        int k = -1; for (int q = 0; q < 4; q++) if (C.diag_ok[q]) { k = q; break; }
        if (k < 0) continue;
        bases++;
        int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
        for (int p = 0; p < NP; p++) {
            if (p >= 13 && p <= 20) continue; // root choices keep the diagonal by definition
            G = F;
            if (p <= 11) { u32 *w = fword(&G, p); u32 old = *w; do *w = rnd32(); while (*w == old); }
            else if (p == 12) G.h ^= 1;
            else if (p <= 32) { *fword(&G, p - 21) ^= 0x80000000u; }
            else if (p == 33) G.m1 ^= 1; else if (p == 34) G.A3 ^= 1; else if (p == 35) G.B6 ^= 1; else G.alpha1hi ^= 2;
            app[p]++;
            construct(&G, hA, hB, &D);
            if (D.diag_ok[k]) {
                keep[p]++;
                same[p] += D.UA[a] == C.UA[a] && D.UB[a] == C.UB[a] && D.UA[b] == C.UA[b] && D.UB[b] == C.UB[b] &&
                           D.UA[c] == C.UA[c] && D.UB[c] == C.UB[c] && D.UA[d] == C.UA[d] && D.UB[d] == C.UB[d];
            }
        }
    }
    printf("arm %s keep: bases %llu (samples %llu)\n", arm, (unsigned long long)bases, (unsigned long long)samples);
    for (int p = 0; p < NP; p++) if (app[p])
        printf("%-16s applied %6llu  diag still solvable %6llu (%.4f)  of which diag inputs unchanged %llu\n", PNAME[p], (unsigned long long)app[p],
               (unsigned long long)keep[p], (double)keep[p] / app[p], (unsigned long long)same[p]);
    return 0;
}

// pi: exact invariance of each diagonal's cycle instance Pi_k = (U_c pair, U_d pair, delta_k, K_k, dy_k) under one perturbation.
// If Pi_k is unchanged, diagonal k has the same roots in z and the same outputs X; only its first message word shifts.
static void pi_of(const cons_t *C, int k, u32 out[7]) {
    int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
    u32 dx = k == 1 ? C->d10 : 0, dy = k == 2 ? C->d13 : 0;
    out[0] = C->UA[c]; out[1] = C->UB[c]; out[2] = C->UA[d]; out[3] = C->UB[d];
    out[4] = (C->UB[a] + C->UB[b] + dx) - (C->UA[a] + C->UA[b]); out[5] = C->UA[b] ^ C->UB[b]; out[6] = dy;
}
static int mode_pi(const char *arm, u64 N, u64 seed) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    // extra perturbations: 37 = A.m3 resample with h chosen to keep delta_1 ; 38 = m5 resample keeping U6 bit0 xor (alpha pin bit)
    enum { NQ = NP + 2 };
    u64 app[NQ] = {0}, inv[NQ][4] = {{0}}, all4[NQ] = {0}, inv3[NQ] = {0};
    free_t F, G; cons_t C, D;
    for (u64 n = 0; n < N; n++) {
        rand_free(&F); construct(&F, hA, hB, &C);
        u32 P0[4][7]; for (int k = 0; k < 4; k++) pi_of(&C, k, P0[k]);
        for (int p = 0; p < NQ; p++) {
            if (p >= 13 && p <= 20) continue;
            G = F;
            if (p <= 11) { u32 *w = fword(&G, p); u32 old = *w; do *w = rnd32(); while (*w == old); }
            else if (p == 12) G.h ^= 1;
            else if (p <= 32) { *fword(&G, p - 21) ^= 0x80000000u; }
            else if (p == 33) G.m1 ^= 1; else if (p == 34) G.A3 ^= 1; else if (p == 35) G.B6 ^= 1; else if (p == 36) G.alpha1hi ^= 2;
            else if (p == 37) { u32 old = G.A3; do G.A3 = rnd32(); while (G.A3 == old);
                construct(&G, hA, hB, &D); u32 t[7]; pi_of(&D, 1, t); if (t[4] != P0[1][4]) G.h ^= 1; }
            else if (p == 38) { for (;;) { u32 old = G.m5; do G.m5 = rnd32(); while (G.m5 == old);
                construct(&G, hA, hB, &D); if (((D.UA[6] ^ D.UB[6]) & 1) == ((C.UA[6] ^ C.UB[6]) & 1)) break; G.m5 = old; } }
            app[p]++;
            construct(&G, hA, hB, &D);
            int cnt = 0;
            for (int k = 0; k < 4; k++) { u32 t[7]; pi_of(&D, k, t); int e = !memcmp(t, P0[k], sizeof t); inv[p][k] += e; cnt += e; }
            all4[p] += cnt == 4; inv3[p] += cnt >= 3;
        }
    }
    printf("arm %s pi-invariance over %llu random samples: P(Pi_k unchanged) k=0..3 | P(all four) P(>=3)\n", arm, (unsigned long long)N);
    for (int p = 0; p < NQ; p++) if (app[p]) {
        const char *nm = p < NP ? PNAME[p] : (p == 37 ? "A.m3+hfix" : "m5(pinbit kept)");
        printf("%-16s", nm); for (int k = 0; k < 4; k++) printf(" %.4f", (double)inv[p][k] / app[p]);
        printf(" | %.4f %.4f\n", (double)all4[p] / app[p], (double)inv3[p] / app[p]);
    }
    return 0;
}

// ---------------- fast solvability (bitmask carry automaton) ----------------
static uint16_t TL[64][256], TH[64][256];
static void init_tables(void) {
    for (int p6 = 0; p6 < 64; p6++) {
        int pa = p6 & 1, pb = (p6 >> 1) & 1, k = (p6 >> 2) & 1, qa = (p6 >> 3) & 1, qb = (p6 >> 4) & 1, dj = (p6 >> 5) & 1;
        uint16_t succ[16];
        for (int s = 0; s < 16; s++) {
            int cin = s & 1, cd = (s >> 1) & 1, cA = (s >> 2) & 1, cB = (s >> 3) & 1; uint16_t m = 0;
            for (int zb = 0; zb < 2; zb++) {
                int sb = zb ^ dj ^ cd, cd2 = (zb & dj) | (zb & cd) | (dj & cd);
                int eA = qa ^ zb, eB = qb ^ sb, fA = pa ^ eA ^ cA, fB = pb ^ eB ^ cB;
                if ((fA ^ fB) != k) continue;
                int cA2 = (pa & eA) | (pa & cA) | (eA & cA), cB2 = (pb & eB) | (pb & cB) | (eB & cB);
                m |= 1u << (cin | cd2 << 1 | cA2 << 2 | cB2 << 3);
            }
            succ[s] = m;
        }
        for (int m8 = 0; m8 < 256; m8++) { uint16_t lo = 0, hi = 0;
            for (int b = 0; b < 8; b++) if ((m8 >> b) & 1) { lo |= succ[b]; hi |= succ[b + 8]; }
            TL[p6][m8] = lo; TH[p6][m8] = hi; }
    }
}
static int fast_solvable(const solver_t *S) {
    uint32_t mask = 0x0009;
    for (int i = 0; i < 32; i++) {
        int j = (i + S->r) & 31;
        if (j == 0) { uint32_t m1 = mask & 0xCCCC; mask = (mask & 0x3333) | (m1 >> 2); }
        int p6 = ((S->PA >> i) & 1) | ((S->PB >> i) & 1) << 1 | ((S->K >> i) & 1) << 2 | ((S->QA >> j) & 1) << 3 | ((S->QB >> j) & 1) << 4 | ((S->delta >> j) & 1) << 5;
        mask = TL[p6][mask & 0xFF] | TH[p6][mask >> 8];
        if (!mask) return 0;
    }
    return (mask & 0x9999) != 0;
}
static u64 N_FAST = 0;
static int first_fast(const cons_t *C, int k) {
    static solver_t S1;
    int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
    u32 dx = k == 1 ? C->d10 : 0;
    S1.PA = C->UA[c]; S1.QA = C->UA[d]; S1.PB = C->UB[c]; S1.QB = C->UB[d]; S1.r = 16;
    S1.delta = (C->UB[a] + C->UB[b] + dx) - (C->UA[a] + C->UA[b]); S1.K = C->UA[b] ^ C->UB[b];
    N_FAST++;
    return fast_solvable(&S1);
}
// does diagonal k (column state in C) have at least one (x,y) pair?
static int diag_has_pair(const cons_t *C, int k) {
    static solver_t S1, S2;
    int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
    u32 dx = k == 1 ? C->d10 : 0, dy = k == 2 ? C->d13 : 0;
    S1.PA = C->UA[c]; S1.QA = C->UA[d]; S1.PB = C->UB[c]; S1.QB = C->UB[d]; S1.r = 16;
    S1.delta = (C->UB[a] + C->UB[b] + dx) - (C->UA[a] + C->UA[b]); S1.K = C->UA[b] ^ C->UB[b];
    N_FAST++;
    if (!fast_solvable(&S1)) return 0;
    u64 n1 = solve_count(&S1);
    for (u64 i1 = 0; i1 < n1; i1++) {
        u32 xA = solve_root(&S1, i1) - C->UA[a] - C->UA[b];
        gt gA, gB; g_first(C->UA[a], C->UA[b], C->UA[c], C->UA[d], xA, &gA); g_first(C->UB[a], C->UB[b], C->UB[c], C->UB[d], xA + dx, &gB);
        S2.PA = gA.c1; S2.QA = gA.d1; S2.PB = gB.c1; S2.QB = gB.d1; S2.r = 8; S2.delta = gB.a1 - gA.a1 + dy; S2.K = 0;
        N_FAST++;
        if (fast_solvable(&S2)) return 1;
    }
    return 0;
}

// ---------------- seq: keeper-based search for completed constructions ----------------
// Same construction (7.1-7.3); only the FREE inputs are chosen adaptively:
//  A: random free inputs until diagonal 1 has a pair.
//  B: resample A.m3 (h re-chosen so delta_1 is unchanged => Pi_1 unchanged) until diagonal 0 has a pair.
//  C: choose U5_A in {U : (U+c) xor U = K0} (keeps Pi_0), m3_A = BPIN(U5_A), h fixed again (keeps Pi_1);
//     test diagonals 2 and 3.  On success run construct() from scratch with these free inputs.
typedef struct { u32 xA, yA, xB, yB, XA[4], XB[4]; } pairrec;
static int mode_seq(const char *arm, double seconds, u64 seed, const char *dump, u64 ncombo) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed); init_tables();
    // self-test fast_solvable vs exact count
    { static solver_t S; u64 bad = 0;
      for (int n = 0; n < 300000; n++) { S.r = (n & 1) ? 8 : 16; S.PA = rnd32(); S.PB = rnd32(); S.QA = rnd32(); S.QB = rnd32(); S.delta = rnd32();
        S.K = (n % 3 == 0) ? 0 : rnd32(); if (n % 5 == 0) { u32 z0 = rnd32(); S.K = 0; S.K = cyc_eval(&S, z0); }
        bad += (solve_count(&S) > 0) != fast_solvable(&S); }
      printf("fast_solvable self-test: 300000 instances, %llu disagreements\n", (unsigned long long)bad); if (bad) return 2; }
    FILE *fd = strcmp(dump, "-") ? fopen(dump, "wb") : NULL;
    double t0 = now(); u64 nA = 0, nB = 0, nC = 0, found = 0, pifail = 0, rounds = 0, nCent = 0;
    u64 cf2 = 0, cf3 = 0, cf23 = 0, cp2 = 0, cp3 = 0, ent2 = 0, ent3 = 0, ent23 = 0; int COUNT_C = getenv("COUNT_C") ? atoi(getenv("COUNT_C")) : 0;
    long double sumS = 0;
    free_t F; cons_t C, D;
    // D statistics over the root-choice ensemble of every completed column state
    u64 single[4][17] = {{0}}, all4[17] = {0}, pair[6][17] = {{0}}, trip[4][17] = {{0}}, combos = 0, efull[4] = {0};
    const int PI[6][2] = {{0, 1}, {0, 2}, {0, 3}, {1, 2}, {1, 3}, {2, 3}};
    const int TI[4][3] = {{1, 2, 3}, {0, 2, 3}, {0, 1, 3}, {0, 1, 2}};
    u64 mv[4][4] = {{0}}, mvn[4] = {0}; // root resample of diag k: count e_j changed
    static u64 pk_app[NP], pk_ok[NP], pk_same[NP][4];
    while (now() - t0 < seconds) {
        // Stage A
        COLS_ONLY = 1;
        do { rand_free(&F); construct(&F, hA, hB, &C); nA++; } while (!diag_has_pair(&C, 1) && now() - t0 < seconds);
        if (now() - t0 >= seconds) break;
        u32 base1[7]; pi_of(&C, 1, base1);
        rounds++;
        // Stage B
        for (u64 b = 0; b < (1u << 19) && now() - t0 < seconds; b++) {
            F.A3 = rnd32(); construct(&F, hA, hB, &C); nB++;
            u32 t1[7]; pi_of(&C, 1, t1); if (t1[4] != base1[4]) { F.h ^= 1; construct(&F, hA, hB, &C); pi_of(&C, 1, t1); }
            if (memcmp(t1, base1, sizeof t1)) { pifail++; continue; }
            if (!diag_has_pair(&C, 0)) continue;
            // Stage C: set of U5_A preserving K0 = U5_A ^ U5_B with fixed c = U5_B - U5_A
            u32 base0[7]; pi_of(&C, 0, base0);
            u32 K0 = C.UA[5] ^ C.UB[5], cc = C.UB[5] - C.UA[5];
            u32 req = 0, fixedv = 0; int freepos[32], nfree = 0;
            for (int i = 0; i < 32; i++) { u32 carry_i = ((K0 >> i) ^ (cc >> i)) & 1; req |= carry_i << i; }
            for (int i = 0; i < 32; i++) {
                u32 ci = (cc >> i) & 1, cr = (req >> i) & 1;
                if (i == 31 || ci == cr) freepos[nfree++] = i;
                else fixedv |= ((req >> (i + 1)) & 1) << i; // U_i must equal required carry into i+1
            }
            sumS += nfree; nCent++;
            gt h1; // col1-A first half: initial v1,v5,v9,v13 = IV1, IV5, IV1, ctr_hi(A)
            g_first(IV[1], IV[5], IV[1], hA[1], F.A2, &h1);
            u64 Ssz = 1ull << nfree, cap = Ssz < (1ull << 24) ? Ssz : (1ull << 24);
            int e2 = 0, e3 = 0;
            for (u64 s = 0; s < cap && now() - t0 < seconds; s++) {
                u32 U = fixedv; for (int q = 0; q < nfree; q++) if ((s >> q) & 1) U |= 1u << freepos[q];
                if (((U + cc) ^ U) != K0) { pifail++; continue; }
                F.A3 = bpin(&h1, U); construct(&F, hA, hB, &C); nC++;
                u32 t0b[7], t1b[7]; pi_of(&C, 1, t1b); if (t1b[4] != base1[4]) { F.h ^= 1; construct(&F, hA, hB, &C); pi_of(&C, 1, t1b); }
                pi_of(&C, 0, t0b);
                if (memcmp(t1b, base1, sizeof t1b) || memcmp(t0b, base0, sizeof t0b)) { pifail++; continue; }
                { int f2 = first_fast(&C, 2), f3 = first_fast(&C, 3); cf2 += f2; cf3 += f3; cf23 += f2 & f3;
                  if (COUNT_C) { int p2 = f2 ? diag_has_pair(&C, 2) : 0, p3 = f3 ? diag_has_pair(&C, 3) : 0; cp2 += p2; cp3 += p3; e2 |= p2; e3 |= p3; }
                  if (!(f2 & f3)) continue; }
                if (!diag_has_pair(&C, 2)) continue;
                if (!diag_has_pair(&C, 3)) continue;
                // all four diagonals have pairs: run the construction exactly as written
                COLS_ONLY = 0; u64 rc = RETRY_CAP; RETRY_CAP = 1ull << 40;
                int ok = construct(&F, hA, hB, &D);
                RETRY_CAP = rc;
                found += ok;
                printf("FOUND complete=%d after A %llu B %llu C %llu (t=%.1fs) nfree=%d e=%08x %08x %08x %08x\n", ok, (unsigned long long)nA,
                       (unsigned long long)nB, (unsigned long long)nC, now() - t0, nfree, D.e[0], D.e[1], D.e[2], D.e[3]);
                printf("  free: m1 %08x m5 %08x A0 %08x A2 %08x A3 %08x A4 %08x A6 %08x A7 %08x B0 %08x B4 %08x B6 %08x alpha %08x h %d\n",
                       F.m1, F.m5, F.A0, F.A2, F.A3, F.A4, F.A6, F.A7, F.B0, F.B4, F.B6, F.alpha1hi, F.h);
                fflush(stdout);
                if (ok) {
                    // perturb each free input of the completed construction; does it stay complete, which D_j stay equal?
                    { u64 rc2 = RETRY_CAP; RETRY_CAP = 1ull << 40; cons_t D2; free_t G;
                      for (int p = 0; p < NP; p++) { if (p >= 13 && p <= 20) continue;
                        int reps = p <= 11 ? 20 : 1;
                        for (int rep = 0; rep < reps; rep++) {
                            G = F;
                            if (p <= 11) { u32 *w = fword(&G, p); u32 old = *w; do *w = rnd32(); while (*w == old); }
                            else if (p == 12) G.h ^= 1;
                            else if (p <= 32) { *fword(&G, p - 21) ^= 0x80000000u; }
                            else if (p == 33) G.m1 ^= 1; else if (p == 34) G.A3 ^= 1; else if (p == 35) G.B6 ^= 1; else G.alpha1hi ^= 2;
                            int ok2 = construct(&G, hA, hB, &D2);
                            pk_app[p]++; if (ok2) { pk_ok[p]++; for (int j = 0; j < 4; j++) pk_same[p][j] += D2.e[j] == D.e[j]; }
                        } }
                      RETRY_CAP = rc2; }
                    // enumerate all (x,y) pairs per diagonal (cap) and sample root combinations
                    u64 cap2 = 1u << 20; pairrec *L[4]; u64 nl[4];
                    for (int k = 0; k < 4; k++) {
                        L[k] = malloc(cap2 * sizeof(pairrec)); nl[k] = 0;
                        static solver_t S1, S2; int a = DG[k][0], bb = DG[k][1], c = DG[k][2], d = DG[k][3];
                        u32 dx = k == 1 ? D.d10 : 0, dy = k == 2 ? D.d13 : 0;
                        S1.PA = D.UA[c]; S1.QA = D.UA[d]; S1.PB = D.UB[c]; S1.QB = D.UB[d]; S1.r = 16;
                        S1.delta = (D.UB[a] + D.UB[bb] + dx) - (D.UA[a] + D.UA[bb]); S1.K = D.UA[bb] ^ D.UB[bb];
                        u64 n1 = solve_count(&S1);
                        for (u64 i1 = 0; i1 < n1 && nl[k] < cap2; i1++) {
                            u32 xA = solve_root(&S1, i1) - D.UA[a] - D.UA[bb];
                            gt gA, gB; g_first(D.UA[a], D.UA[bb], D.UA[c], D.UA[d], xA, &gA); g_first(D.UB[a], D.UB[bb], D.UB[c], D.UB[d], xA + dx, &gB);
                            S2.PA = gA.c1; S2.QA = gA.d1; S2.PB = gB.c1; S2.QB = gB.d1; S2.r = 8; S2.delta = gB.a1 - gA.a1 + dy; S2.K = 0;
                            if (!fast_solvable(&S2)) continue;
                            u64 n2 = solve_count(&S2);
                            for (u64 i2 = 0; i2 < n2 && nl[k] < cap2; i2++) {
                                u32 yA = solve_root(&S2, i2) - gA.a1 - gA.b1; gt pA = gA, pB = gB; g_second(&pA, yA); g_second(&pB, yA + dy);
                                pairrec *r = &L[k][nl[k]++]; r->xA = xA; r->xB = xA + dx; r->yA = yA; r->yB = yA + dy;
                                r->XA[0] = pA.a2; r->XA[1] = pA.b2; r->XA[2] = pA.c2; r->XA[3] = pA.d2; r->XB[0] = pB.a2; r->XB[1] = pB.b2; r->XB[2] = pB.c2; r->XB[3] = pB.d2;
                            }
                        }
                    }
                    printf("  pairs per diagonal: %llu %llu %llu %llu\n", (unsigned long long)nl[0], (unsigned long long)nl[1], (unsigned long long)nl[2], (unsigned long long)nl[3]);
                    u32 mA[16], mB[16]; memcpy(mA, D.mA, 64); memcpy(mB, D.mB, 64);
                    for (u64 t = 0; t < ncombo; t++) {
                        u64 pick4[4]; for (int k = 0; k < 4; k++) pick4[k] = rnd64() % nl[k];
                        u32 XA[16], XB[16], e[4];
                        for (int rep = 0; rep < 2; rep++) {
                            for (int k = 0; k < 4; k++) { pairrec *r = &L[k][pick4[k]];
                                for (int w = 0; w < 4; w++) { XA[DG[k][w]] = r->XA[w]; XB[DG[k][w]] = r->XB[w]; }
                                mA[8 + 2 * k] = r->xA; mB[8 + 2 * k] = r->xB; mA[9 + 2 * k] = r->yA; mB[9 + 2 * k] = r->yB; }
                            u32 ee[4];
                            for (int j = 0; j < 4; j++) {
                                u32 xa = mA[PERM[2 * j]], xb = mB[PERM[2 * j]], ya = mA[PERM[2 * j + 1]], yb = mB[PERM[2 * j + 1]];
                                if ((XB[j] - XA[j]) + (xb - xa) + (yb - ya)) { fprintf(stderr, "combo S fail\n"); exit(9); }
                                ee[j] = (XA[j + 12] ^ (XA[j] + XA[j + 4] + xa)) ^ (XB[j + 12] ^ (XB[j] + XB[j + 4] + xb));
                            }
                            for (int i = 4; i < 12; i++) if (XA[i] != XB[i]) { fprintf(stderr, "combo bc fail\n"); exit(9); }
                            if (rep == 0) {
                                memcpy(e, ee, 16);
                                if (fd && t < 2000) { u32 fl = 0x1FF; fwrite(mA, 4, 16, fd); fwrite(mB, 4, 16, fd); fwrite(D.hA, 4, 4, fd); fwrite(D.hB, 4, 4, fd); fwrite(&fl, 4, 1, fd); fwrite(ee, 4, 4, fd); }
                                if (t < 20000) { int kk = t % 4; pick4[kk] = rnd64() % nl[kk]; mvn[kk]++; continue; }
                                break;
                            } else { int kk = t % 4; for (int j = 0; j < 4; j++) mv[kk][j] += ee[j] != e[j]; }
                        }
                        combos++;
                        for (int j = 0; j < 4; j++) efull[j] += e[j] == 0;
                        for (int k = 1; k <= 16; k++) { u32 msk = (1u << k) - 1; int z[4];
                            for (int j = 0; j < 4; j++) { z[j] = (e[j] & msk) == 0; single[j][k] += z[j]; }
                            all4[k] += z[0] & z[1] & z[2] & z[3];
                            for (int p = 0; p < 6; p++) pair[p][k] += z[PI[p][0]] & z[PI[p][1]];
                            for (int q = 0; q < 4; q++) trip[q][k] += z[TI[q][0]] & z[TI[q][1]] & z[TI[q][2]]; }
                    }
                    for (int k = 0; k < 4; k++) free(L[k]);
                }
                COLS_ONLY = 1;
            }
            COLS_ONLY = 1;
            ent2 += e2; ent3 += e3; ent23 += e2 & e3;
        }
    }
    printf("stage C entries with some diag2 pair %llu, some diag3 pair %llu, both (different members) %llu\n",
           (unsigned long long)ent2, (unsigned long long)ent3, (unsigned long long)ent23);
    double t1 = now();
    if (fd) fclose(fd);
    printf("seq arm %s: time %.1f s rounds %llu A %llu B %llu C-entries %llu C %llu fastchecks %llu found %llu pifail %llu mean log2|S| %.2Lf\n", arm, t1 - t0,
           (unsigned long long)rounds, (unsigned long long)nA, (unsigned long long)nB, (unsigned long long)nCent, (unsigned long long)nC, (unsigned long long)N_FAST,
           (unsigned long long)found, (unsigned long long)pifail, nCent ? sumS / (long double)nCent : 0);
    printf("stage C: FIRST2 ok %llu FIRST3 ok %llu both %llu ; pair2 %llu pair3 %llu (COUNT_C=%d)\n", (unsigned long long)cf2, (unsigned long long)cf3,
           (unsigned long long)cf23, (unsigned long long)cp2, (unsigned long long)cp3, COUNT_C);
    printf("root-combination ensemble: %llu combos; full-width D passes %llu %llu %llu %llu\n", (unsigned long long)combos,
           (unsigned long long)efull[0], (unsigned long long)efull[1], (unsigned long long)efull[2], (unsigned long long)efull[3]);
    printf("perturbations of completed constructions: applied, still complete, and among complete: count of e_j unchanged j=0..3\n");
    for (int p = 0; p < NP; p++) if (pk_app[p]) printf("  %-16s %5llu %5llu | %llu %llu %llu %llu\n", PNAME[p], (unsigned long long)pk_app[p], (unsigned long long)pk_ok[p],
        (unsigned long long)pk_same[p][0], (unsigned long long)pk_same[p][1], (unsigned long long)pk_same[p][2], (unsigned long long)pk_same[p][3]);
    for (int k = 0; k < 4; k++) { printf("resample diag%d pair (n=%llu): P(e_j changed) j=0..3:", k, (unsigned long long)mvn[k]);
        for (int j = 0; j < 4; j++) printf(" %.4f", mvn[k] ? (double)mv[k][j] / mvn[k] : -1); printf("\n"); }
    for (int k = 1; k <= 16; k++) {
        printf("k %2d single", k); for (int j = 0; j < 4; j++) printf(" %llu", (unsigned long long)single[j][k]);
        printf(" | pairs"); for (int p = 0; p < 6; p++) printf(" %llu", (unsigned long long)pair[p][k]);
        printf(" | trip"); for (int q = 0; q < 4; q++) printf(" %llu", (unsigned long long)trip[q][k]);
        printf(" | all4 %llu\n", (unsigned long long)all4[k]);
    }
    return 0;
}

// gbrute: G-level full scans of FIRST (over x) and SECOND (over y) for construction-derived diagonals
static int mode_gbrute(const char *arm, int ninst, u64 seed) {
    u32 hA[4], hB[4]; set_arm(arm, hA, hB); seed_rng(seed);
    static solver_t S; int bad = 0;
    for (int inst = 0; inst < ninst; inst++) {
        int k = inst % 4, want = inst < ninst - 2; // last two instances: unsolvable FIRST
        free_t F; cons_t C; u64 n1;
        int a = DG[k][0], b = DG[k][1], c = DG[k][2], d = DG[k][3];
        u32 dx, dy;
        for (;;) {
            rand_free(&F); construct(&F, hA, hB, &C);
            dx = k == 1 ? C.d10 : 0; dy = k == 2 ? C.d13 : 0;
            S.PA = C.UA[c]; S.QA = C.UA[d]; S.PB = C.UB[c]; S.QB = C.UB[d]; S.r = 16;
            S.delta = (C.UB[a] + C.UB[b] + dx) - (C.UA[a] + C.UA[b]); S.K = C.UA[b] ^ C.UB[b];
            n1 = solve_count(&S);
            if ((n1 > 0) == want) break;
        }
        u64 g1 = 0; u32 xr = 0; gt tA, tB;
        for (u64 x = 0; x < (1ull << 32); x++) {
            u32 xa = (u32)x;
            u32 a1A = C.UA[a] + C.UA[b] + xa, a1B = C.UB[a] + C.UB[b] + xa + dx;
            u32 b1A = ror(C.UA[b] ^ (C.UA[c] + ror(C.UA[d] ^ a1A, 16)), 12);
            u32 b1B = ror(C.UB[b] ^ (C.UB[c] + ror(C.UB[d] ^ a1B, 16)), 12);
            if (b1A == b1B) { if (!g1) xr = xa; g1++; }
        }
        printf("inst %d diag D%d FIRST dp %llu gscan %llu %s", inst, k, (unsigned long long)n1, (unsigned long long)g1, n1 == g1 ? "OK" : "MISMATCH");
        if (n1 != g1) bad++;
        if (g1) {
            g_first(C.UA[a], C.UA[b], C.UA[c], C.UA[d], xr, &tA); g_first(C.UB[a], C.UB[b], C.UB[c], C.UB[d], xr + dx, &tB);
            S.PA = tA.c1; S.QA = tA.d1; S.PB = tB.c1; S.QB = tB.d1; S.r = 8; S.delta = tB.a1 - tA.a1 + dy; S.K = 0;
            u64 n2 = solve_count(&S), g2 = 0;
            for (u64 y = 0; y < (1ull << 32); y++) {
                u32 ya = (u32)y;
                u32 c2A = tA.c1 + ror(tA.d1 ^ (tA.a1 + tA.b1 + ya), 8), c2B = tB.c1 + ror(tB.d1 ^ (tB.a1 + tB.b1 + ya + dy), 8);
                g2 += c2A == c2B;
            }
            printf(" | SECOND (x=%08x) dp %llu gscan %llu %s", xr, (unsigned long long)n2, (unsigned long long)g2, n2 == g2 ? "OK" : "MISMATCH");
            if (n2 != g2) bad++;
        }
        printf("\n"); fflush(stdout);
    }
    printf("gbrute summary: %d instances, %d mismatches\n", ninst, bad);
    return bad != 0;
}

// plant mode: random instances with a planted root; DP must count >=1 and enumerate the planted z
static int mode_plant(u64 N, u64 seed) {
    seed_rng(seed); static solver_t S; u64 bad = 0, found = 0, enumd = 0; long double sumc = 0;
    for (u64 n = 0; n < N; n++) {
        S.r = (n & 1) ? 8 : 16; S.PA = rnd32(); S.PB = rnd32(); S.QA = rnd32(); S.QB = rnd32(); S.delta = rnd32();
        u32 z0 = rnd32(); S.K = 0; S.K = cyc_eval(&S, z0);
        u64 c = solve_count(&S); sumc += c;
        if (c == 0) { bad++; continue; }
        if (c <= 20000) { enumd++; int hit = 0; u32 prev = 0;
            for (u64 i = 0; i < c; i++) { u32 z = solve_root(&S, i); if (cyc_eval(&S, z) != S.K) bad++; if (z == z0) hit = 1; (void)prev; }
            found += hit; }
    }
    printf("plant: N %llu bad %llu enumerated %llu planted_found %llu mean_count_given_planted %.2Lf\n",
           (unsigned long long)N, (unsigned long long)bad, (unsigned long long)enumd, (unsigned long long)found, sumc / N);
    return bad != 0 || found != enumd;
}

static int mode_bench(u64 N) {
    seed_rng(1); u32 m[16], v[16]; volatile u32 sink = 0; double t0 = now();
    for (u64 n = 0; n < N; n++) {
        for (int i = 0; i < 16; i++) m[i] = rnd32();
        for (int i = 0; i < 8; i++) v[i] = IV[i]; for (int i = 0; i < 4; i++) v[8 + i] = IV[i]; v[12] = 0; v[13] = 0; v[14] = 64; v[15] = 11;
        u32 mm[16]; memcpy(mm, m, 64);
        for (int r = 0; r < 2; r++) {
            const int idx[8][4] = {{0, 4, 8, 12}, {1, 5, 9, 13}, {2, 6, 10, 14}, {3, 7, 11, 15}, {0, 5, 10, 15}, {1, 6, 11, 12}, {2, 7, 8, 13}, {3, 4, 9, 14}};
            for (int g = 0; g < 8; g++) { gt t; g_first(v[idx[g][0]], v[idx[g][1]], v[idx[g][2]], v[idx[g][3]], mm[2 * g], &t); g_second(&t, mm[2 * g + 1]);
                v[idx[g][0]] = t.a2; v[idx[g][1]] = t.b2; v[idx[g][2]] = t.c2; v[idx[g][3]] = t.d2; }
            u32 t2[16]; for (int i = 0; i < 16; i++) t2[i] = mm[PERM[i]]; memcpy(mm, t2, 64);
        }
        for (int i = 0; i < 8; i++) sink ^= v[i] ^ v[i + 8];
    }
    double t1 = now();
    printf("bench: 2-round compression incl. 16 rnd32 msg gen: %.1f ns each\n", 1e9 * (t1 - t0) / N);
    return (int)(sink & 0);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "usage\n"); return 1; }
    if (getenv("RETRY_CAP")) RETRY_CAP = strtoull(getenv("RETRY_CAP"), 0, 10);
    if (getenv("COUNT_ALL")) COUNT_ALL = atoi(getenv("COUNT_ALL"));
    if (getenv("EARLY")) EARLY = atoi(getenv("EARLY"));
    if (!strcmp(argv[1], "stats")) return mode_stats(argv[2], strtoull(argv[3], 0, 10), strtoull(argv[4], 0, 10), argv[5], strtoull(argv[6], 0, 10));
    if (!strcmp(argv[1], "struct")) return mode_struct(argv[2], strtoull(argv[3], 0, 10), strtoull(argv[4], 0, 10));
    if (!strcmp(argv[1], "brute")) return mode_brute(argv[2], atoi(argv[3]), strtoull(argv[4], 0, 10));
    if (!strcmp(argv[1], "bench")) return mode_bench(strtoull(argv[2], 0, 10));
    if (!strcmp(argv[1], "seq")) return mode_seq(argv[2], atof(argv[3]), strtoull(argv[4], 0, 10), argv[5], strtoull(argv[6], 0, 10));
    if (!strcmp(argv[1], "pi")) return mode_pi(argv[2], strtoull(argv[3], 0, 10), strtoull(argv[4], 0, 10));
    if (!strcmp(argv[1], "keep")) return mode_keep(argv[2], strtoull(argv[3], 0, 10), strtoull(argv[4], 0, 10));
    if (!strcmp(argv[1], "roots")) return mode_roots(argv[2], strtoull(argv[3], 0, 10), strtoull(argv[4], 0, 10), strtoull(argv[5], 0, 10));
    if (!strcmp(argv[1], "gbrute")) return mode_gbrute(argv[2], atoi(argv[3]), strtoull(argv[4], 0, 10));
    if (!strcmp(argv[1], "plant")) return mode_plant(strtoull(argv[2], 0, 10), strtoull(argv[3], 0, 10));
    return 1;
}
