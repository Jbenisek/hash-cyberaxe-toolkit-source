/* For H3: how many trials satisfy rule A, and how many batches enter stage 2, in the layout of proof.md 6.4 itself.
 * CPU only. Research helper, not submitted.
 *
 * Written by a reviewing helper agent (lens mathematics and cost) from proof.md Sections 4, 6.1, 6.3, 6.5, as
 * review/math_rule_share.c. This copy differs from it in this comment only. tools/rule_share.sh builds it under a
 * name of its own, checks it against the real compression (tools/rule_share_vectors.py) and keeps its output in
 * evidence/rule_share_<seed>.txt, which tools/pkg5_data.py reads. The constants below are those of pin B, class
 * e7c1815f and rule A6; tools/pkg5_data.py compares them with PART A before it quotes the output.
 *
 * A "run" has four seed words X2, X5, X6, X9 and X1 = X10 = 0 (step 1), so S5 is the same in all its contexts.
 * Contexts: X12 < 2^8, X13 < 2^16, X14 any, drawn at random inside these ranges (a run of 6.4 takes all of them).
 * For every context a few random alpha; for every (context, alpha) ALL 65,536 members in the order of their
 * numbers, seven per batch as in 6.5, the last batch with two members.
 *
 *   math_rule_share RUNS CONTEXTS ALPHAS SEED          one line per run, then a summary
 *   math_rule_share vectors N SEED                     N lines "nine words, alpha, k, z, pass" for the Python check
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <omp.h>
typedef uint32_t u32;
typedef uint64_t u64;
static const u32 IV[8] = {0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au, 0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u};
#define CX3 0xD5D881CAu
#define CX7 0xAA277E35u
#define CX11 0x1F208000u
#define CX15 0x123F2142u
#define CW4 0x7FFFFFFFu
#define CW13 0xFFFD6E01u
#define CY3 0x3F52EDA0u
#define QMASK 0x015FE7C1u
#define QVALUE 0x00036181u
#define RS 0x0F008000u
#define RALL 0x0F008100u
#define RV 0x0A008000u
static inline u32 ror(u32 v, int n) { return (v >> n) | (v << (32 - n)); }
static inline u32 rol(u32 v, int n) { return (v << n) | (v >> (32 - n)); }
static u64 sm(u64 *s) { u64 z = (*s += 0x9E3779B97F4A7C15ull); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull; z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; return z ^ (z >> 31); }
typedef struct { u32 X[16], S[16], w[16]; } ctx_t;
static u32 U[65536];                       /* ROL(Y4, 7) of member k */

static void col_inv(int j, u32 sb, u32 sc, u32 d0, u32 *sa, u32 *sd, u32 *x, u32 *y) {
    u32 b1 = rol(sb, 7) ^ sc, c1 = rol(b1, 12) ^ IV[4 + j];
    *sd = sc - c1;
    u32 d1 = c1 - IV[j], a1 = rol(d1, 16) ^ d0;
    *x = a1 - IV[j] - IV[4 + j];
    *sa = rol(*sd, 8) ^ d1;
    *y = *sa - a1 - b1;
}

/* step S1; f = X1, X2, X5, X6, X9, X10, X12, X13, X14 */
static void context(const u32 f[9], ctx_t *c) {
    u32 *X = c->X, *S = c->S, *w = c->w;
    memset(c, 0, sizeof *c);
    X[1] = f[0]; X[2] = f[1]; X[5] = f[2]; X[6] = f[3]; X[9] = f[4]; X[10] = f[5]; X[12] = f[6]; X[13] = f[7]; X[14] = f[8];
    X[3] = CX3; X[7] = CX7; X[11] = CX11; X[15] = CX15; w[4] = CW4; w[13] = CW13; w[15] = 0;
    u32 K = IV[2] + IV[6], p = K + CW4, q = ror(p ^ 60, 16), r = q + IV[2], u = ror(r ^ IV[6], 12);
    u32 bD1 = rol(X[6], 7) ^ X[11], cc = X[11] - X[12], dD1 = rol(X[12], 8) ^ X[1];
    S[6] = rol(bD1, 12) ^ cc; S[11] = cc - dD1;
    S[10] = u ^ rol(S[6], 7);
    u32 bD0 = rol(X[5], 7) ^ X[10]; cc = X[10] - X[15]; S[5] = rol(bD0, 12) ^ cc;
    u32 dD0 = cc - S[10]; X[0] = dD0 ^ rol(X[15], 8);
    S[14] = S[10] - r; S[2] = rol(S[14], 8) ^ q; w[5] = S[2] - p - u;
    u32 d = rol(X[14], 8) ^ X[3], aD3 = rol(d, 16) ^ S[14], b = X[3] - aD3 - w[15];
    X[4] = ror(b ^ X[9], 7); cc = X[9] - X[14]; S[4] = rol(b, 12) ^ cc; S[9] = cc - d;
    col_inv(1, S[5], S[9], 0, &S[1], &S[13], &w[2], &w[3]);
    d = rol(X[13], 8) ^ X[2];
    u32 a = rol(d, 16) ^ S[13];
    b = X[2] - a - w[13]; X[8] = b ^ rol(X[7], 7); cc = X[8] - X[13];
    S[7] = rol(b, 12) ^ cc; S[8] = cc - d; w[12] = a - S[2] - S[7];
    col_inv(0, S[4], S[8], 0, &S[0], &S[12], &w[0], &w[1]);
    col_inv(3, S[7], S[11], 11, &S[3], &S[15], &w[6], &w[7]);
    a = rol(dD0, 16) ^ S[15]; w[8] = a - S[0] - S[5]; w[9] = X[0] - a - bD0;
    a = rol(dD1, 16) ^ S[12]; w[10] = a - S[1] - S[6]; w[11] = X[1] - a - bD1;
    w[14] = aD3 - S[3] - S[4];
}

typedef struct { u32 pa, pb, pc, pd; } al_t;
/* the D0 family and the first half of C0 (6.1) */
static void per_alpha(const ctx_t *c, u32 alpha, al_t *o) {
    const u32 *X = c->X, *S = c->S, *w = c->w;
    u32 cc = alpha - X[15], dD0 = cc - S[10], X0 = rol(X[15], 8) ^ dD0;
    o->pa = X0 + X[4] + w[2]; o->pd = ror(X[12] ^ o->pa, 16); o->pc = X[8] + o->pd; o->pb = ror(X[4] ^ o->pc, 12);
}
/* z of one trial: C0 backwards, K3 with S7 kept, C2 to its fifth value (6.1, 6.5 stage A) */
static inline u32 zword(const ctx_t *c, u32 alpha, const al_t *o, u32 uy) {
    u32 Y8 = uy ^ o->pb, Y12 = Y8 - o->pc, Y0 = rol(Y12, 8) ^ o->pd, w6 = Y0 - o->pa - o->pb;
    u32 ka = IV[3] + IV[7] + w6, kd = ror(ka ^ 11, 16), kc = IV[3] + kd, kb = ror(IV[7] ^ kc, 12);
    u32 S11 = rol(c->S[7], 7) ^ kb, S15 = S11 - kc, S3 = rol(S15, 8) ^ kd, w7 = S3 - ka - kb;
    u32 a1 = c->X[2] + c->X[6] + w7, d1 = ror(c->X[14] ^ a1, 16), c1 = alpha + d1, b1 = ror(c->X[6] ^ c1, 12);
    u32 a2 = a1 + b1 + c->w[0];
    return a2 ^ d1;
}
static inline int rule(u32 z) { return (((z ^ ((z >> 1) & RS)) & RALL) ^ RV) == 0; }

int main(int argc, char **argv) {
    int free_pos[16], nf = 0;
    for (int i = 0; i < 32; i++) if (!(QMASK >> i & 1)) free_pos[nf++] = i;
    if (nf != 16) return 2;
    for (u32 k = 0; k < 65536; k++) {
        u32 e1 = QVALUE;
        for (int j = 0; j < 16; j++) e1 |= (k >> j & 1) << free_pos[j];
        U[k] = rol(e1 - CY3, 7);
    }
    if (argc == 4 && !strcmp(argv[1], "vectors")) {
        u64 s = strtoull(argv[3], 0, 10);
        for (int i = 0; i < atoi(argv[2]); i++) {
            u32 f[9];
            for (int j = 0; j < 9; j++) f[j] = (u32)sm(&s);
            u32 alpha = (u32)sm(&s), k = (u32)sm(&s) & 0xFFFF;
            ctx_t c; al_t o;
            context(f, &c); per_alpha(&c, alpha, &o);
            u32 z = zword(&c, alpha, &o, U[k]);
            for (int j = 0; j < 9; j++) printf("%08x ", f[j]);
            printf("%08x %u %08x %d\n", alpha, k, z, rule(z));
        }
        return 0;
    }
    if (argc != 5) { fprintf(stderr, "usage\n"); return 2; }
    int runs = atoi(argv[1]), nctx = atoi(argv[2]), nal = atoi(argv[3]);
    u64 seed = strtoull(argv[4], 0, 10);
    double *share = malloc(sizeof(double) * runs), *enter = malloc(sizeof(double) * runs);
    u64 *P = calloc(runs, sizeof(u64)), *E = calloc(runs, sizeof(u64));
    u32 *lo = malloc(sizeof(u32) * runs), *hi = malloc(sizeof(u32) * runs);
    #pragma omp parallel for schedule(dynamic, 1)
    for (int r = 0; r < runs; r++) {
        u64 s = seed * 1000003ull + (u64)r;
        u32 X2 = (u32)sm(&s), X5 = (u32)sm(&s), X6 = (u32)sm(&s), X9 = (u32)sm(&s);
        u64 pass = 0, ent = 0; u32 mn = 0xFFFFFFFFu, mx = 0;
        for (int ci = 0; ci < nctx; ci++) {
            u32 f[9] = {0, X2, X5, X6, X9, 0, (u32)sm(&s) & 0xFF, (u32)sm(&s) & 0xFFFF, (u32)sm(&s)};
            ctx_t c; context(f, &c);
            for (int ai = 0; ai < nal; ai++) {
                u32 alpha = (u32)sm(&s); al_t o; per_alpha(&c, alpha, &o);
                u32 here = 0;
                for (u32 j = 0; j < 9363; j++) {
                    int any = 0;
                    for (u32 k = 7 * j; k < 7 * j + 7 && k < 65536; k++) { int p = rule(zword(&c, alpha, &o, U[k])); here += p; any |= p; }
                    ent += any;
                }
                pass += here; if (here < mn) mn = here; if (here > mx) mx = here;
            }
        }
        double tr = (double)nctx * nal * 65536.0, bt = (double)nctx * nal * 9363.0;
        P[r] = pass; E[r] = ent; share[r] = pass / tr; enter[r] = ent / bt; lo[r] = mn; hi[r] = mx;
    }
    double tr = (double)nctx * nal * 65536.0, bt = (double)nctx * nal * 9363.0, sd = sqrt(tr / 64.0 * 63.0 / 64.0);
    double smin = 9, smax = 0, emin = 9, emax = 0, chi = 0; u64 tp = 0, te = 0; u32 gl = 0xFFFFFFFFu, gh = 0;
    for (int r = 0; r < runs; r++) {
        printf("RUN %d trials %.0f satisfy_rule_A %llu share*64 %.6f dev_sd %+.2f batches %.0f enter_stage_2 %llu share %.6f per(context,alpha) min %u max %u\n",
               r, tr, (unsigned long long)P[r], share[r] * 64.0, ((double)P[r] - tr / 64.0) / sd, bt, (unsigned long long)E[r], enter[r], lo[r], hi[r]);
        if (share[r] < smin) smin = share[r]; if (share[r] > smax) smax = share[r];
        if (enter[r] < emin) emin = enter[r]; if (enter[r] > emax) emax = enter[r];
        double d = ((double)P[r] - tr / 64.0) / sd; chi += d * d; tp += P[r]; te += E[r];
        if (lo[r] < gl) gl = lo[r]; if (hi[r] > gh) gh = hi[r];
    }
    printf("SUMMARY runs %d trials_per_run 2^%.2f; share of trials that satisfy rule A, times 64: min %.6f max %.6f all %.6f; chi-square of the runs against 2^-6 (binomial) %.1f on %d; "
           "share of batches that enter stage 2: min %.6f max %.6f all %.6f (budget 0.125, 7/64 = 0.109375, 1-(63/64)^7 = %.6f); passes per (context, alpha) of 65536: min %u max %u\n",
           runs, log2(tr), smin * 64, smax * 64, (double)tp / (tr * runs) * 64, chi, runs, emin, emax, (double)te / (bt * runs), 1 - pow(63.0 / 64.0, 7), gl, gh);
    return 0;
}
