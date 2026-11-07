// smc38r.c - scout2-4 (hole 4): Step-3 probability of the ePrint 2026/1120 38-step characteristic as used by the
// filed r38 package (pkgR38a base, proof.md 6.2), estimated by sequential Monte Carlo under three stage predicates:
//   C  cells: the filed estimator (smc3.c logic, proof.md B.4): row 16 exact (G, 32 words), rows 17..22 propose E_i^x
//      with its x-value cells and '+' bits imposed (weight 2^-f), tail proposes W23^x with its x-value cells imposed,
//      W7 = W23 - s1(W21) - W16 - s0(W8), weight 1{W7 in F7} 2^(32-f)/|F7|, every cell and two-bit condition of rows
//      16..37 tested.
//   H  row 16 cells (W16 in G), rows 17..37 relaxed: after row i (i = 17..22) the modular differences
//      (A_{i+1}^x - A_{i+1}^y, E_{i+1}^x - E_{i+1}^y, W_{i+1}^x - W_{i+1}^y) must equal the published pair's (they are
//      functions of rows <= i); the tail requires only the collision (A34..A37, E34..E37 equal in both members).
//   R  as H with row 16 relaxed too: W16 in G' = {w : modular differences of row 17 equal the published ones,
//      s1(W16^x) - s1(W16^y) = -(dW11) (so dW18 = 0) and s0(W16^x) - s0(W16^y) = -(dW15) (so dW31 = 0)}, enumerated
//      exhaustively over 2^32 words.
// Relaxed stages use two disjoint proposal streams per particle: M_i proposals with the characteristic's cells imposed
// (weight 2^-f / M_i) and U_i uniform proposals counted only when they fall OUTSIDE the imposed set (weight 1 / U_i);
// the two strata are disjoint, so the stage mean is unbiased for Pr[stage predicate | particle]; multinomial resampling
// proportional to the weights.  Every tail success is rebuilt (W0..W6 by the inverse expansion, CV1 by inverting steps
// 7..0 of the variant) and accepted only if the full 38-step compressions of the two messages from CV1 collide (and the
// messages differ); for each success we also record whether it follows every cell of rows 16..37 ("cell path").
// usage: smc38r MODE seed NP M17 M18 M19 M20 M21 M22 MT U17 U18 U19 U20 U21 U22 UT [fixvar] [sfsout]
//        smc38r G            (enumerate G and G' over 2^32 words, recount |F7|, write Gp.txt)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <stdint.h>
#include "consts38.h"
#define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline uint32_t S0(uint32_t x){return ROR(x,2)^ROR(x,13)^ROR(x,22);}
static inline uint32_t S1(uint32_t x){return ROR(x,6)^ROR(x,11)^ROR(x,25);}
static inline uint32_t s0(uint32_t x){return ROR(x,7)^ROR(x,18)^(x>>3);}
static inline uint32_t s1(uint32_t x){return ROR(x,17)^ROR(x,19)^(x>>10);}
static inline uint32_t Ch(uint32_t x,uint32_t y,uint32_t z){return (x&y)^(~x&z);}
static inline uint32_t Mj(uint32_t x,uint32_t y,uint32_t z){return (x&y)^(x&z)^(y&z);}
typedef struct { uint32_t a[NR+4], e[NR+4], w[NR]; } Tr;
#define AA(t,i) ((t)->a[(i)+4])
#define EE(t,i) ((t)->e[(i)+4])
static inline void step(Tr *t, int i) {
    EE(t,i) = AA(t,i-4) + EE(t,i-4) + S1(EE(t,i-1)) + Ch(EE(t,i-1), EE(t,i-2), EE(t,i-3)) + KK[i] + t->w[i];
    AA(t,i) = EE(t,i) - AA(t,i-4) + S0(AA(t,i-1)) + Mj(AA(t,i-1), AA(t,i-2), AA(t,i-3));
}
static inline uint32_t sched(const Tr *t, int i) { return s1(t->w[i-2]) + t->w[i-7] + s0(t->w[i-15]) + t->w[i-16]; }
static inline uint32_t getv(const Tr *t, int k, int i) { return k == 0 ? AA(t,i) : k == 1 ? EE(t,i) : t->w[i]; }
// cells of row i (A, E with '+', W) and the two-bit conditions keyed at row i (member x) - as core.h rowok(.., 1)
static inline int rowok(const Tr *x, const Tr *y, int i) {
    uint32_t ax = AA(x,i), ay = AA(y,i), ex = EE(x,i), ey = EE(y,i), wx = x->w[i], wy = y->w[i];
    if ((ax & CM[0][i]) != CV[0][i] || (ax ^ ay) != CD[0][i]) return 0;
    if ((ex & CM[1][i]) != CV[1][i] || (ex ^ ey) != CD[1][i]) return 0;
    if (CPL[i] && ((ex ^ EE(x,i-1)) & CPL[i])) return 0;
    if ((wx & CM[2][i]) != CV[2][i] || (wx ^ wy) != CD[2][i]) return 0;
    for (int j = 0; j < NX; j++) if (XROW[j] == i) {
        uint32_t b1 = getv(x, XK1[j], XI1[j]) >> XB1[j] & 1, b2 = getv(x, XK2[j], XI2[j]) >> XB2[j] & 1;
        if ((b1 ^ b2) != (uint32_t)XNE[j]) return 0;
    }
    return 1;
}
static inline uint64_t smx(uint64_t *s) { uint64_t z = (*s += 0x9e3779b97f4a7c15ULL); z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ULL; z = (z ^ (z >> 27)) * 0x94d049bb133111ebULL; return z ^ (z >> 31); }
static inline uint64_t below(uint64_t *s, uint64_t n) { return smx(s) % n; }
static const uint32_t D7 = 0x20000000u, T7 = 0x03bff800u, DW16 = 0x20000000u;
static inline int inF7(uint32_t w) { return (uint32_t)(s0(w + D7) - s0(w)) == T7; }
static const double F7N = 287309824.0;
static uint32_t TA[NR], TE[NR], TW[NR], DLOW[NR];   // published modular differences x - y; DLOW_j = ds0(W_{j-15}) + dW_{j-16}
#define PA(m,i) ((m) ? PYA[(i)+4] : PXA[(i)+4])
#define PE(m,i) ((m) ? PYE[(i)+4] : PXE[(i)+4])
#define PW(m,i) ((m) ? PYW[i] : PXW[i])
typedef struct { Tr x, y; } P;
static void base(P *b) {
    memset(b, 0, sizeof *b);
    for (int m = 0; m < 2; m++) {
        Tr *t = m ? &b->y : &b->x;
        for (int i = 8; i < 16; i++) { AA(t,i) = PA(m,i); EE(t,i) = PE(m,i); t->w[i] = PW(m,i); }
    }
}
// variant dense part (both members), as core.h mkvar: A0..A2 replaced, E4..E6 and W8..W10 recomputed
typedef struct { uint32_t A[2][16], E[2][16], W[2][16]; } Var;
static void mkvar(Var *v, uint32_t a0, uint32_t a1, uint32_t a2) {
    for (int m = 0; m < 2; m++) {
        uint32_t *A = v->A[m], *E = v->E[m], *W = v->W[m];
        for (int i = 0; i < 16; i++) { A[i] = PA(m,i); E[i] = PE(m,i); W[i] = PW(m,i); }
        A[0] = a0; A[1] = a1; A[2] = a2;
        for (int i = 4; i <= 6; i++) E[i] = A[i] + A[i-4] - S0(A[i-1]) - Mj(A[i-1], A[i-2], A[i-3]);
        for (int i = 8; i <= 10; i++) W[i] = E[i] - A[i-4] - E[i-4] - S1(E[i-1]) - Ch(E[i-1], E[i-2], E[i-3]) - KK[i];
    }
}
static void compress38(const uint32_t cv[8], const uint32_t m[16], uint32_t out[8]) {
    Tr t; for (int j = 0; j < 4; j++) { AA(&t,-1-j) = cv[j]; EE(&t,-1-j) = cv[4+j]; }
    for (int i = 0; i < 16; i++) t.w[i] = m[i];
    for (int i = 16; i < NR; i++) t.w[i] = sched(&t, i);
    for (int i = 0; i < NR; i++) step(&t, i);
    for (int j = 0; j < 4; j++) { out[j] = cv[j] + AA(&t, NR-1-j); out[4+j] = cv[4+j] + EE(&t, NR-1-j); }
}
// rebuild the semi-free-start pair of a tail success and test the collision with full 38-step compressions
static int rebuild(const P *q, uint32_t w7, const uint32_t *vr, uint32_t cvo[8], uint32_t mx[16], uint32_t my[16]) {
    Var v; mkvar(&v, vr[0], vr[1], vr[2]);
    for (int m = 0; m < 2; m++) for (int i = 8; i <= 10; i++) if (v.W[m][i] != vr[3 + 2*(i-8) + m]) return -1;
    uint32_t W[16]; W[7] = w7;
    for (int i = 8; i < 16; i++) W[i] = q->x.w[i];
    W[6] = q->x.w[22] - s1(q->x.w[20]) - W[15] - s0(W[7]);
    for (int i = 5; i >= 0; i--) W[i] = q->x.w[i+16] - s1(q->x.w[i+14]) - W[i+9] - s0(W[i+1]);
    uint32_t A[24], E[24];   // index i+8
    for (int i = 0; i < 8; i++) { A[i+8] = v.A[0][i]; if (i >= 4) E[i+8] = v.E[0][i]; }
    for (int i = 7; i >= 0; i--) {
        A[i-4+8] = E[i+8] - A[i+8] + S0(A[i-1+8]) + Mj(A[i-1+8], A[i-2+8], A[i-3+8]);
        E[i-4+8] = E[i+8] - A[i-4+8] - S1(E[i-1+8]) - Ch(E[i-1+8], E[i-2+8], E[i-3+8]) - KK[i] - W[i];
    }
    uint32_t cv[8] = {A[7], A[6], A[5], A[4], E[7], E[6], E[5], E[4]};
    for (int i = 0; i < 16; i++) { mx[i] = W[i]; my[i] = (i < 7) ? W[i] : (i == 7 ? W[7] + D7 : q->y.w[i]); }
    // member y's Step-2 words from cv must be (W0..W6, W7 + d7): run member y forward and compare its dense part
    Tr ty; for (int j = 0; j < 4; j++) { AA(&ty,-1-j) = cv[j]; EE(&ty,-1-j) = cv[4+j]; }
    for (int i = 0; i < 16; i++) ty.w[i] = my[i];
    for (int i = 0; i < 16; i++) { step(&ty, i); if (AA(&ty,i) != v.A[1][i] || (i >= 4 && EE(&ty,i) != v.E[1][i])) return -2; }
    uint32_t h1[8], h2[8]; compress38(cv, mx, h1); compress38(cv, my, h2);
    memcpy(cvo, cv, 32);
    if (memcmp(h1, h2, 32) != 0 || memcmp(mx, my, 64) == 0) return 0;
    return 1;
}
static int cellpath(const P *q) { for (int i = 16; i < NR; i++) if (!rowok(&q->x, &q->y, i)) return 0; return 1; }
static int popc(uint32_t x) { return __builtin_popcount(x); }

// ---- G and G' (row 16) ----
static uint32_t *GP; static long nGP;
static P B0;   // base particle: rows 8..15 and W8..W15 of the published pair
static uint32_t c16x, c16y, ab16x, ab16y, dw17, dA13, dpre17, dW11, dW15;
static void prep16(void) {
    base(&B0); const Tr *X = &B0.x, *Y = &B0.y;
    c16x = AA(X,12) + EE(X,12) + S1(EE(X,15)) + Ch(EE(X,15), EE(X,14), EE(X,13)) + KK[16];
    c16y = AA(Y,12) + EE(Y,12) + S1(EE(Y,15)) + Ch(EE(Y,15), EE(Y,14), EE(Y,13)) + KK[16];
    ab16x = 0u - AA(X,12) + S0(AA(X,15)) + Mj(AA(X,15), AA(X,14), AA(X,13));
    ab16y = 0u - AA(Y,12) + S0(AA(Y,15)) + Mj(AA(Y,15), AA(Y,14), AA(Y,13));
    dw17 = (s1(X->w[15]) - s1(Y->w[15])) + (X->w[10] - Y->w[10]) + DLOW[17];
    dA13 = AA(X,13) - AA(Y,13); dpre17 = dA13 + (EE(X,13) - EE(Y,13)) + dw17;
    dW11 = X->w[11] - Y->w[11]; dW15 = X->w[15] - Y->w[15];
}
// relaxed row 16 -> row 17: 1 if W16^x = w gives the published modular differences of row 17 and dW18 = dW31 = 0
static inline int row17_relaxed(uint32_t w) {
    const Tr *X = &B0.x, *Y = &B0.y; uint32_t wy = w - DW16;
    uint32_t ex = c16x + w, ey = c16y + wy, ax = ex + ab16x, ay = ey + ab16y;
    if (ax - ay != TA[16] || ex - ey != TE[16]) return -1;
    if (dw17 != TW[17]) return 0;
    uint32_t dE = dpre17 + (S1(ex) - S1(ey)) + (Ch(ex, EE(X,15), EE(X,14)) - Ch(ey, EE(Y,15), EE(Y,14)));
    if (dE != TE[17]) return 0;
    uint32_t dA = dE - dA13 + (S0(ax) - S0(ay)) + (Mj(ax, AA(X,15), AA(X,14)) - Mj(ay, AA(Y,15), AA(Y,14)));
    if (dA != TA[17]) return 0;
    if ((uint32_t)((s1(w) - s1(wy)) + dW11) != TW[18]) return 0;   // dW18 = ds1(W16) + dW11
    if ((uint32_t)((s0(w) - s0(wy)) + dW15) != TW[31]) return 0;   // dW31 = ds0(W16) + dW15 (dW24 = dW29 = 0)
    return 1;
}
static int row16_cells(uint32_t w) {
    uint32_t wy = w - DW16, ex = c16x + w, ey = c16y + wy;
    if ((ex & CM[1][16]) != CV[1][16] || (ex ^ ey) != CD[1][16] || (w & CM[2][16]) != CV[2][16] || (w ^ wy) != CD[2][16]) return 0;
    P q = B0; q.x.w[16] = w; q.y.w[16] = wy; step(&q.x, 16); step(&q.y, 16);
    return rowok(&q.x, &q.y, 16);
}
static void enum_g(void) {
    long ng = 0, ngp = 0, both = 0, f7 = 0; FILE *f = fopen("Gp.txt", "w");
    for (uint64_t v = 0; v < (1ULL << 32); v++) {
        uint32_t w = (uint32_t)v;
        f7 += inF7(w);
        int r = row17_relaxed(w);
        if (r < 0) { fprintf(stderr, "row 16 differences not deterministic at %08x\n", w); exit(1); }
        int c = row16_cells(w);
        ng += c; ngp += r; both += c && r;
        if (r) fprintf(f, "%08x %d\n", w, c);
    }
    fclose(f);
    printf("|F7| = %ld (filed 287309824)\n|G| = %ld (filed 32)  |G'| = %ld  |G and G'| = %ld\n", f7, ng, ngp, both);
}
static void load_gp(void) {
    FILE *f = fopen("Gp.txt", "r"); if (!f) { fprintf(stderr, "run 'smc38r G' first\n"); exit(1); }
    long cap = 1 << 16; GP = malloc(cap * 4); nGP = 0; unsigned w; int c;
    while (fscanf(f, "%x %d", &w, &c) == 2) { if (nGP == cap) { cap *= 2; GP = realloc(GP, cap * 4); } GP[nGP++] = w; }
    fclose(f);
}

typedef struct { P p; double w; } S;
int main(int argc, char **argv) {
    for (int i = 0; i < NR; i++) {
        TA[i] = PXA[i+4] - PYA[i+4]; TE[i] = PXE[i+4] - PYE[i+4]; TW[i] = PXW[i] - PYW[i]; DLOW[i] = 0;
    }
    DLOW[22] = 0u - T7;                                   // s0(W7^x) - s0(W7^y) for W7 in F7
    DLOW[23] = (s0(PXW[8]) - s0(PYW[8])) + (0u - D7);      // ds0(W8) + dW7
    prep16();
    if (argc >= 2 && argv[1][0] == 'G') { enum_g(); return 0; }
    if (argc < 18) { fprintf(stderr, "usage: smc38r CUT seed NP M17..M22 MT U17..U22 UT [fixvar] [sfsout]\n"); return 1; }
    // CUT: rows 16..CUT keep the characteristic's cells, rows CUT+1..37 are relaxed (modular differences, collision at
    // the end).  C = 37 (the filed estimator), H = 16, R = 15 (row 16 relaxed too: G').
    // P<s> (s = 18..23): plain Monte Carlo check without importance weights: cell stages 17..s-1 (SMC), then for
    // every particle MT plain samples of rows s..37 (E_i^x uniform for i = s..22, W7 uniform in F7 by rejection,
    // variant uniform from the sample), counting the cell event of rows s..37 and the collision event.
    int plain = argv[1][0] == 'P' ? atoi(argv[1] + 1) : 0;
    int cut = argv[1][0] == 'C' || plain ? 37 : argv[1][0] == 'H' ? 16 : argv[1][0] == 'R' ? 15 : atoi(argv[1]);
    if (cut < 15 || cut > 37 || (plain && (plain < 18 || plain > 23))) { fprintf(stderr, "CUT 15..37, C/H/R or P18..P23\n"); return 1; }
    char mode = cut == 37 ? 'C' : 'X';
    uint64_t seed0 = strtoull(argv[2], 0, 10), seed = seed0; seed = smx(&seed);
    int NP = atoi(argv[3]); long MS[23], US[23], MT, UT;
    for (int i = 17; i <= 22; i++) MS[i] = atol(argv[4 + i - 17]);
    MT = atol(argv[10]);
    for (int i = 17; i <= 22; i++) US[i] = atol(argv[11 + i - 17]);
    UT = atol(argv[17]);
    long FIXV = argc > 18 ? atol(argv[18]) : -1;
    FILE *fs = argc > 19 ? fopen(argv[19], "w") : NULL;
    for (int i = 17; i <= 22; i++) if (i <= cut) US[i] = 0;    // a cell stage has no mass outside the imposed set
    if (cut >= 23) UT = 0;
    // sanity: published targets of the relaxed predicates are what the characteristic's cells force
    if (TW[16] != DW16 || TW[18] != 0 || TW[31] != 0 || TW[23] != DLOW[23] + DW16) { fprintf(stderr, "target mismatch\n"); return 1; }
    // stage 16
    double est, logs[12]; int ns = 0;
    P *cur = malloc(sizeof(P) * (size_t)NP);
    // stage-16 start set: cut >= 17: G (cells of row 16); cut 16: G words whose row-17 modular differences and W16
    // sigma conditions hold (G and G'); cut 15: G' (exhaustive list from 'smc38r G')
    uint32_t G0[32]; long nG0 = 0;
    for (int k = 0; k < 32; k++) if (cut >= 17 || row17_relaxed(GW[k]) == 1) G0[nG0++] = GW[k];
    if (cut == 15) load_gp();
    if (nG0 == 0) { fprintf(stderr, "no G word passes the relaxed row 17\n"); return 1; }
    est = (cut == 15 ? (double)nGP : (double)nG0) / 4294967296.0; logs[ns++] = log2(est);
    for (int p = 0; p < NP; p++) {
        uint32_t w = cut == 15 ? GP[below(&seed, nGP)] : G0[below(&seed, nG0)];
        base(&cur[p]); cur[p].x.w[16] = w; cur[p].y.w[16] = w - DW16; step(&cur[p].x, 16); step(&cur[p].y, 16);
        if (cut >= 16 && !rowok(&cur[p].x, &cur[p].y, 16)) { fprintf(stderr, "G mismatch\n"); return 1; }
        if (cut <= 16 && row17_relaxed(w) != 1) { fprintf(stderr, "G' mismatch\n"); return 1; }
    }
    S *sv = NULL; size_t cap = 0; double *cum = NULL; size_t ccap = 0;
    long hitsC[23] = {0}, hitsU[23] = {0};
    for (int i = 17; i <= 22; i++) {
        if (plain && i >= plain) break;
        int cellstage = i <= cut, modstage = i >= cut;
        uint32_t m = CM[1][i], vv = CV[1][i], pq = CPL[i]; int fb = popc(m) + popc(pq);
        double wC = MS[i] ? ldexp(1.0, -fb) / (double)MS[i] : 0, wU = US[i] ? 1.0 / (double)US[i] : 0;
        size_t n = 0; double tot = 0; int j = i + 1;
        for (int p = 0; p < NP; p++) {
            const P *q = &cur[p]; const Tr *X = &q->x, *Y = &q->y;
            uint32_t e1x = EE(X,i-1), e2x = EE(X,i-2), e3x = EE(X,i-3), e1y = EE(Y,i-1), e2y = EE(Y,i-2), e3y = EE(Y,i-3);
            uint32_t a1x = AA(X,i-1), a2x = AA(X,i-2), a3x = AA(X,i-3), a1y = AA(Y,i-1), a2y = AA(Y,i-2), a3y = AA(Y,i-3);
            uint32_t cx = AA(X,i-4) + EE(X,i-4) + S1(e1x) + Ch(e1x, e2x, e3x) + KK[i];
            uint32_t cy = AA(Y,i-4) + EE(Y,i-4) + S1(e1y) + Ch(e1y, e2y, e3y) + KK[i];
            uint32_t dw = (s1(X->w[i-2]) - s1(Y->w[i-2])) + (X->w[i-7] - Y->w[i-7]) + DLOW[i];
            uint32_t abx = 0u - AA(X,i-4) + S0(a1x) + Mj(a1x, a2x, a3x), aby = 0u - AA(Y,i-4) + S0(a1y) + Mj(a1y, a2y, a3y);
            // next row j = i + 1: its modular differences are functions of rows <= i
            uint32_t dWj = (s1(X->w[j-2]) - s1(Y->w[j-2])) + (X->w[j-7] - Y->w[j-7]) + DLOW[j];
            uint32_t dA4 = AA(X,j-4) - AA(Y,j-4), dpre = dA4 + (EE(X,j-4) - EE(Y,j-4)) + dWj;
            if (modstage && dWj != TW[j]) continue;
            long tot_c = MS[i] + US[i];
            for (long c = 0; c < tot_c; c++) {
                int instream = c < MS[i]; uint32_t e;
                if (instream) { e = ((uint32_t)smx(&seed) & ~m) | vv; if (pq) e = (e & ~pq) | (e1x & pq); }
                else { e = (uint32_t)smx(&seed); if ((e & m) == vv && !((e ^ e1x) & pq)) continue; }
                uint32_t wx = e - cx, wy = wx - dw, ey = cy + wy, ax = e + abx, ay = ey + aby;
                if (cellstage) {
                    if ((e ^ ey) != CD[1][i] || (ax & CM[0][i]) != CV[0][i] || (ax ^ ay) != CD[0][i]) continue;
                    if ((wx & CM[2][i]) != CV[2][i] || (wx ^ wy) != CD[2][i]) continue;
                }
                if (modstage) {
                    uint32_t dE = dpre + (S1(e) - S1(ey)) + (Ch(e, e1x, e2x) - Ch(ey, e1y, e2y));
                    if (dE != TE[j]) continue;
                    uint32_t dA = dE - dA4 + (S0(ax) - S0(ay)) + (Mj(ax, a1x, a2x) - Mj(ay, a1y, a2y));
                    if (dA != TA[j]) continue;
                }
                if (n == cap) { cap = cap ? 2 * cap : 1 << 16; sv = realloc(sv, cap * sizeof(S)); }
                S *s = &sv[n]; s->p = *q;
                s->p.x.w[i] = wx; s->p.y.w[i] = wy; step(&s->p.x, i); step(&s->p.y, i);
                if (EE(&s->p.x,i) != e || EE(&s->p.y,i) != ey || AA(&s->p.x,i) != ax || AA(&s->p.y,i) != ay) { fprintf(stderr, "step mismatch\n"); return 1; }
                if (cellstage && !rowok(&s->p.x, &s->p.y, i)) continue;
                if (!cellstage && ((uint32_t)(ax - ay) != TA[i] || (uint32_t)(e - ey) != TE[i] || (uint32_t)(wx - wy) != TW[i])) { fprintf(stderr, "row %d differences off\n", i); return 1; }
                s->w = instream ? wC : wU; tot += s->w; n++;
                if (instream) hitsC[i]++; else hitsU[i]++;
            }
        }
        double fac = tot / NP; est *= fac; logs[ns++] = log2(fac);
        if (!n) { printf("cut %d seed %llu: extinct at row %d\n", cut, (unsigned long long)seed0, i); return 0; }
        if (n > ccap) { ccap = n; cum = realloc(cum, ccap * sizeof(double)); }
        double acc = 0; for (size_t k = 0; k < n; k++) { acc += sv[k].w; cum[k] = acc; }
        for (int p = 0; p < NP; p++) {
            double u = (double)(smx(&seed) >> 11) * 0x1.0p-53 * acc;
            size_t lo = 0, hi = n - 1; while (lo < hi) { size_t mid = (lo + hi) / 2; if (cum[mid] > u) hi = mid; else lo = mid + 1; }
            cur[p] = sv[lo].p;
        }
    }
    if (plain) {
        uint64_t ncell = 0, ncoll = 0, nbad = 0, ntot = 0;
        for (int p = 0; p < NP; p++) for (long c = 0; c < MT; c++) {
            P q = cur[p]; ntot++;
            for (int i = plain; i <= 22; i++) {
                uint32_t e = (uint32_t)smx(&seed);
                uint32_t cx = AA(&q.x,i-4) + EE(&q.x,i-4) + S1(EE(&q.x,i-1)) + Ch(EE(&q.x,i-1), EE(&q.x,i-2), EE(&q.x,i-3)) + KK[i];
                uint32_t dw = (s1(q.x.w[i-2]) - s1(q.y.w[i-2])) + (q.x.w[i-7] - q.y.w[i-7]) + DLOW[i];
                q.x.w[i] = e - cx; q.y.w[i] = q.x.w[i] - dw; step(&q.x, i); step(&q.y, i);
            }
            const uint32_t *vr = FIXV >= 0 ? VAR[FIXV] : VAR[below(&seed, NVAR)];
            uint32_t w7; do w7 = (uint32_t)smx(&seed); while (!inF7(w7));
            q.x.w[8] = vr[3]; q.y.w[8] = vr[4]; q.x.w[9] = vr[5]; q.y.w[9] = vr[6]; q.x.w[10] = vr[7]; q.y.w[10] = vr[8];
            q.x.w[23] = s1(q.x.w[21]) + q.x.w[16] + s0(q.x.w[8]) + w7; q.y.w[23] = s1(q.y.w[21]) + q.y.w[16] + s0(q.y.w[8]) + (w7 + D7);
            for (int i = 23; i < NR; i++) { if (i > 23) { q.x.w[i] = sched(&q.x, i); q.y.w[i] = sched(&q.y, i); } step(&q.x, i); step(&q.y, i); }
            int coll = 1; for (int i = NR - 4; i < NR; i++) if (AA(&q.x,i) != AA(&q.y,i) || EE(&q.x,i) != EE(&q.y,i)) coll = 0;
            int cell = 1; for (int i = plain; i < NR && cell; i++) cell = rowok(&q.x, &q.y, i);
            if (cell && !coll) nbad++;
            if (coll) { uint32_t cv[8], mx[16], my[16]; if (rebuild(&q, w7, vr, cv, mx, my) != 1) { nbad++; continue; } }
            ncell += cell; ncoll += coll;
        }
        printf("plain from row %d seed %llu NP %d MT %ld: samples %llu  cell %llu (2^%.4f)  collision %llu (2^%.4f)  ratio %.4f  bad %llu  stages:",
               plain, (unsigned long long)seed0, NP, MT, (unsigned long long)ntot, (unsigned long long)ncell, log2((double)ncell / ntot),
               (unsigned long long)ncoll, log2((double)ncoll / ntot), ncell ? (double)ncoll / ncell : 0.0, (unsigned long long)nbad);
        for (int k = 0; k < ns; k++) printf(" %.3f", logs[k]);
        printf("\n");
        return 0;
    }
    // tail: W23 proposals, variant from the embedded sample, collision (H/R) or every cell (C) through row 37
    uint32_t m23 = CM[2][23], v23 = CV[2][23]; int f23 = popc(m23);
    double wTC = MT ? ldexp(1.0, 32 - f23) / F7N / (double)MT : 0, wTU = UT ? ldexp(1.0, 32) / F7N / (double)UT : 0;
    double tt = 0, tcell = 0; long nhit = 0, nhitU = 0, ncell = 0, bad = 0;
    for (int p = 0; p < NP; p++) for (long c = 0; c < MT + UT; c++) {
        const P *q0 = &cur[p]; int instream = c < MT;
        const uint32_t *vr = FIXV >= 0 ? VAR[FIXV] : VAR[below(&seed, NVAR)];
        uint32_t w23 = (uint32_t)smx(&seed);
        if (instream) w23 = (w23 & ~m23) | v23; else if ((w23 & m23) == v23) continue;
        uint32_t w7 = w23 - s1(q0->x.w[21]) - q0->x.w[16] - s0(vr[3]);
        if (!inF7(w7)) continue;
        P q = *q0;
        q.x.w[8] = vr[3]; q.y.w[8] = vr[4]; q.x.w[9] = vr[5]; q.y.w[9] = vr[6]; q.x.w[10] = vr[7]; q.y.w[10] = vr[8];
        q.x.w[23] = w23; q.y.w[23] = s1(q.y.w[21]) + q.y.w[16] + s0(q.y.w[8]) + (w7 + D7);
        int ok = 1;
        for (int i = 23; i < NR && ok; i++) {
            if (i > 23) { q.x.w[i] = sched(&q.x, i); q.y.w[i] = sched(&q.y, i); }
            step(&q.x, i); step(&q.y, i);
            if (i <= cut) ok = rowok(&q.x, &q.y, i);
        }
        if (!ok) continue;
        for (int i = NR - 4; i < NR; i++) if (AA(&q.x,i) != AA(&q.y,i) || EE(&q.x,i) != EE(&q.y,i)) ok = 0;
        if (!ok) { if (mode == 'C') bad++; continue; }
        uint32_t cv[8], mx[16], my[16];
        int rb = rebuild(&q, w7, vr, cv, mx, my);
        if (rb != 1) { bad++; continue; }
        double w = instream ? wTC : wTU; tt += w; nhit++; if (!instream) nhitU++;
        int cp = cellpath(&q); if (cp) { tcell += w; ncell++; }
        if (fs) {
            fprintf(fs, "%d %d %08x %08x %08x", cp, instream, vr[0], vr[1], vr[2]);
            for (int k = 0; k < 8; k++) fprintf(fs, " %08x", cv[k]);
            for (int k = 0; k < 16; k++) fprintf(fs, " %08x", mx[k]);
            for (int k = 0; k < 16; k++) fprintf(fs, " %08x", my[k]);
            fprintf(fs, "\n");
        }
    }
    if (fs) fclose(fs);
    double tf = tt / NP; est *= tf; logs[ns++] = log2(tf > 0 ? tf : 1e-300);
    printf("cut %d seed %llu NP %d: log2 q3 = %.4f  stages:", cut, (unsigned long long)seed0, NP, log2(est));
    for (int k = 0; k < ns; k++) printf(" %.3f", logs[k]);
    printf("  tail hits %ld (uniform-outside %ld) cellpath %ld weightfrac %.4f bad %ld  hitsC/U:", nhit, nhitU, ncell, tt > 0 ? tcell / tt : 0, bad);
    for (int i = 17; i <= 22; i++) printf(" %ld/%ld", hitsC[i], hitsU[i]);
    printf("\n");
    return 0;
}
