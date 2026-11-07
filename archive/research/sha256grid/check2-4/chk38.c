// chk38.c - check2-4: independent check of the scout2-4 (hole 4) relaxed-q3 measurement on the filed r38 package.
// Written from vt38.py (constants via kexport.py -> k38.h), not from smc38r.c.  Differences from the scout's design:
// relaxed rows use plain uniform proposals only (no stratified imposed/outside streams), resampling is systematic
// (not multinomial), the RNG is xoshiro256** (not splitmix64), the look-ahead test steps the next row with a dummy
// word instead of a difference formula, the schedule differences come from placeholder words W0..W7 with the right
// differences, and every tail success is rebuilt and checked by a separate a..h 38-step compression.
// Events (W16 in G and W7 in F7 always):
//   C  every cell of rows 16..37 (the filed q3; tail proposals uniform, not imposed)
//   T  cells of rows 16..22, published modular differences of row 23, collision after step 37
//   M  cells of row 16, the filed first row-17 test (E17^x against the program's 10-bit mask FT_ME/FT_VE),
//      published modular differences of rows 17..23, collision after step 37
//   H  cells of row 16, published modular differences of rows 17..23, collision after step 37
// usage: chk38 MODE seed NP N17 N18 N19 N20 N21 N22 NT [sfsfile]
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include "k38.h"

#define RR(x,n) (((x)>>(n))|((x)<<(32-(n))))
static inline uint32_t BS0(uint32_t x){return RR(x,2)^RR(x,13)^RR(x,22);}
static inline uint32_t BS1(uint32_t x){return RR(x,6)^RR(x,11)^RR(x,25);}
static inline uint32_t ls0(uint32_t x){return RR(x,7)^RR(x,18)^(x>>3);}
static inline uint32_t ls1(uint32_t x){return RR(x,17)^RR(x,19)^(x>>10);}
static inline uint32_t CHf(uint32_t x,uint32_t y,uint32_t z){return (x&y)|(~x&z);}
static inline uint32_t MAJf(uint32_t x,uint32_t y,uint32_t z){return (x&y)|(z&(x|y));}

typedef struct { uint32_t a[NROW+4], e[NROW+4], w[NROW]; } Mb;
#define A_(t,i) ((t)->a[(i)+4])
#define E_(t,i) ((t)->e[(i)+4])
typedef struct { Mb x, y; } Pt;
typedef struct { Pt p; double wt; } Ch;

static uint64_t S[4];
static inline uint64_t rl(uint64_t x, int k){return (x<<k)|(x>>(64-k));}
static inline uint64_t nx(void){uint64_t r=rl(S[1]*5,7)*9,t=S[1]<<17;S[2]^=S[0];S[3]^=S[1];S[1]^=S[2];S[0]^=S[3];S[2]^=t;S[3]=rl(S[3],45);return r;}
static void seedrng(uint64_t s){for(int i=0;i<4;i++){uint64_t z=(s+=0x9e3779b97f4a7c15ULL);z=(z^(z>>30))*0xbf58476d1ce4e5b9ULL;z=(z^(z>>27))*0x94d049bb133111ebULL;S[i]=z^(z>>31);}}
static inline double unif(void){return (double)(nx()>>11)*0x1.0p-53;}

static inline void fwd(Mb *t, int i) {
    uint32_t e = A_(t,i-4) + E_(t,i-4) + BS1(E_(t,i-1)) + CHf(E_(t,i-1),E_(t,i-2),E_(t,i-3)) + KC[i] + t->w[i];
    E_(t,i) = e; A_(t,i) = e - A_(t,i-4) + BS0(A_(t,i-1)) + MAJf(A_(t,i-1),A_(t,i-2),A_(t,i-3));
}
static inline uint32_t sch(const Mb *t, int j){return ls1(t->w[j-2]) + t->w[j-7] + ls0(t->w[j-15]) + t->w[j-16];}
static inline uint32_t vget(const Mb *t, int k, int i){return k==0 ? A_(t,i) : k==1 ? E_(t,i) : t->w[i];}
static const uint32_t *CMk[3]={CMA,CME,CMW}, *CVk[3]={CVA,CVE,CVW}, *CDk[3]={CDA,CDE,CDW};
static int cellrow(const Pt *p, int i) {
    for (int k = 0; k < 3; k++) {
        uint32_t vx = vget(&p->x,k,i), vy = vget(&p->y,k,i);
        if ((vx & CMk[k][i]) != CVk[k][i] || (vx ^ vy) != CDk[k][i]) return 0;
    }
    if ((E_(&p->x,i) ^ E_(&p->x,i-1)) & PLS[i]) return 0;
    for (int j = 0; j < NTB; j++) if (TROW[j] == i) {
        uint32_t b1 = (vget(&p->x,TK1[j],TI1[j]) >> TB1[j]) & 1, b2 = (vget(&p->x,TK2[j],TI2[j]) >> TB2[j]) & 1;
        if ((b1 ^ b2) != (uint32_t)TNE[j]) return 0;
    }
    return 1;
}
static uint32_t TDA[NROW], TDE[NROW], TDW[NROW];
static inline int inF7(uint32_t w){return (uint32_t)(ls0(w + CD7) - ls0(w)) == CT7;}
static double F7N;
// modular differences of row j given rows <= j-1 (dummy W_j^x = 0, W_j^y = -dW_j): 1 if they are the published ones
static int nextok(const Pt *p, int j) {
    uint32_t dw = sch(&p->x,j) - sch(&p->y,j);
    if (dw != TDW[j]) return 0;
    Pt q = *p; q.x.w[j] = 0; q.y.w[j] = 0u - dw; fwd(&q.x,j); fwd(&q.y,j);
    return (uint32_t)(E_(&q.x,j) - E_(&q.y,j)) == TDE[j] && (uint32_t)(A_(&q.x,j) - A_(&q.y,j)) == TDA[j];
}
static void F38(const uint32_t cv[8], const uint32_t m[16], uint32_t out[8]) {
    uint32_t w[NROW]; for (int i = 0; i < 16; i++) w[i] = m[i];
    for (int i = 16; i < NROW; i++) w[i] = ls1(w[i-2]) + w[i-7] + ls0(w[i-15]) + w[i-16];
    uint32_t a=cv[0],b=cv[1],c=cv[2],d=cv[3],e=cv[4],f=cv[5],g=cv[6],h=cv[7];
    for (int i = 0; i < NROW; i++) {
        uint32_t t1 = h + BS1(e) + CHf(e,f,g) + KC[i] + w[i], t2 = BS0(a) + MAJf(a,b,c);
        h=g; g=f; f=e; e=d+t1; d=c; c=b; b=a; a=t1+t2;
    }
    uint32_t r[8]={a,b,c,d,e,f,g,h}; for (int i = 0; i < 8; i++) out[i] = cv[i] + r[i];
}
// variant record: j, k, a0, a1, a2, then member m at 5 + 36 m: A0..A15 (16), E4..E15 (12), W8..W15 (8)
#define VA(v,m,i) (VSR[v][5 + 36*(m) + (i)])
#define VE(v,m,i) (VSR[v][5 + 36*(m) + 16 + (i) - 4])
#define VW(v,m,i) (VSR[v][5 + 36*(m) + 28 + (i) - 8])
static long nbad[8];
// rebuild (CV1, M1, M1') from a tail success and verify; returns 1 if it is a verified collision of the variant's pair
static int verify(const Pt *q, int v, uint32_t w7, uint32_t cv[8], uint32_t mx[16], uint32_t my[16], int *cellp, int *ft) {
    uint32_t W[NROW]; W[7] = w7;
    for (int i = 8; i < 16; i++) W[i] = VW(v,0,i);
    for (int i = 16; i <= 22; i++) W[i] = q->x.w[i];
    W[6] = W[22] - ls1(W[20]) - W[15] - ls0(W[7]);
    for (int i = 5; i >= 0; i--) W[i] = W[i+16] - ls1(W[i+14]) - W[i+9] - ls0(W[i+1]);
    uint32_t A[12], E[12];                    // index i + 4, i = -4..7
    for (int i = 0; i < 8; i++) A[i+4] = VA(v,0,i);
    for (int i = 4; i < 8; i++) E[i+4] = VE(v,0,i);
    for (int i = 7; i >= 0; i--) {
        uint32_t am4 = E[i+4] - A[i+4] + BS0(A[i+3]) + MAJf(A[i+3], A[i+2], A[i+1]);
        if (i >= 4 && am4 != A[i]) { nbad[0]++; return 0; }
        A[i] = am4;
        E[i] = E[i+4] - A[i] - BS1(E[i+3]) - CHf(E[i+3], E[i+2], E[i+1]) - KC[i] - W[i];
    }
    uint32_t c0[8] = {A[3], A[2], A[1], A[0], E[3], E[2], E[1], E[0]};
    memcpy(cv, c0, 32);
    for (int i = 0; i < 16; i++) { mx[i] = W[i]; my[i] = i < 7 ? W[i] : i == 7 ? W[7] + CD7 : VW(v,1,i); }
    // forward traces of both members from cv (A/E recurrence) and their comparison with the variant and the particle
    Pt t; memset(&t, 0, sizeof t);
    for (int m = 0; m < 2; m++) {
        Mb *tm = m ? &t.y : &t.x; const uint32_t *mm = m ? my : mx;
        for (int j = 0; j < 4; j++) { A_(tm,-1-j) = cv[j]; E_(tm,-1-j) = cv[4+j]; }
        for (int i = 0; i < 16; i++) tm->w[i] = mm[i];
        for (int i = 16; i < NROW; i++) tm->w[i] = sch(tm, i);
        for (int i = 0; i < NROW; i++) fwd(tm, i);
        for (int i = 0; i < 16; i++) if (A_(tm,i) != VA(v,m,i) || (i >= 4 && E_(tm,i) != VE(v,m,i))) { nbad[1]++; return 0; }
        const Mb *qm = m ? &q->y : &q->x;
        for (int i = 16; i < NROW; i++) if (A_(tm,i) != A_(qm,i) || E_(tm,i) != E_(qm,i) || tm->w[i] != qm->w[i]) { nbad[2]++; return 0; }
    }
    uint32_t hx[8], hy[8]; F38(cv, mx, hx); F38(cv, my, hy);
    if (memcmp(hx, hy, 32) != 0) { nbad[3]++; return 0; }
    if (memcmp(mx, my, 64) == 0) { nbad[4]++; return 0; }
    if (!inF7(mx[7])) { nbad[5]++; return 0; }
    int gi = -1; for (int k = 0; k < 32; k++) if (GW[k] == t.x.w[16]) gi = k;
    if (gi < 0 || !cellrow(&t, 16)) { nbad[6]++; return 0; }
    *cellp = 1; for (int i = 16; i < NROW && *cellp; i++) *cellp = cellrow(&t, i);
    *ft = (E_(&t.x,17) & FT_ME[gi]) == FT_VE[gi] && (uint32_t)(E_(&t.x,17) - t.x.w[17]) == FT_C17[gi];
    return 1;
}

int main(int argc, char **argv) {
    if (argc < 11) { fprintf(stderr, "usage: chk38 MODE seed NP N17 N18 N19 N20 N21 N22 NT [sfsfile]\n"); return 1; }
    char mode = argv[1][0]; uint64_t seed = strtoull(argv[2], 0, 10); int NP = atoi(argv[3]);
    long N[23]; for (int i = 17; i <= 22; i++) N[i] = atol(argv[4 + i - 17]); long NT = atol(argv[10]);
    FILE *fs = argc > 11 ? fopen(argv[11], "w") : NULL;
    if (mode != 'C' && mode != 'T' && mode != 'M' && mode != 'H') { fprintf(stderr, "mode C, T, M or H\n"); return 1; }
    int lastcell = mode == 'C' ? 37 : mode == 'T' ? 22 : 16;   // rows 16..lastcell keep the cells
    seedrng(seed);
    for (int i = 0; i < NROW; i++) { TDA[i] = XA[i+4] - YA[i+4]; TDE[i] = XE[i+4] - YE[i+4]; TDW[i] = XW[i] - YW[i]; }
    F7N = 287309824.0;
    // base particle: rows -4..15 of the published pair, W0..W15 published (placeholders for W0..W7 carry the right
    // differences: W0..W6 equal, W7^y = W7^x + d7 with W7^x in F7)
    Pt base; memset(&base, 0, sizeof base);
    for (int i = -4; i < 16; i++) { A_(&base.x,i) = XA[i+4]; E_(&base.x,i) = XE[i+4]; A_(&base.y,i) = YA[i+4]; E_(&base.y,i) = YE[i+4]; }
    for (int i = 0; i < 16; i++) { base.x.w[i] = XW[i]; base.y.w[i] = YW[i]; }
    if (!inF7(XW[7]) || YW[7] != XW[7] + CD7) { fprintf(stderr, "published W7 placeholder not in F7\n"); return 1; }
    for (int i = 0; i < 7; i++) if (XW[i] != YW[i]) { fprintf(stderr, "W0..W6 differ\n"); return 1; }
    // stage 16: G (exact), filtered by the row-17 modular differences for M and H
    int gl[32], ng = 0;
    for (int k = 0; k < 32; k++) {
        Pt p = base; p.x.w[16] = GW[k]; p.y.w[16] = GW[k] - CDW16;
        if (sch(&p.x,16) - sch(&p.y,16) != CDW16) { fprintf(stderr, "dW16\n"); return 1; }
        fwd(&p.x,16); fwd(&p.y,16);
        if (!cellrow(&p,16)) { fprintf(stderr, "G word fails row 16\n"); return 1; }
        if (lastcell == 16 && !nextok(&p,17)) continue;
        gl[ng++] = k;
    }
    double logq = log2((double)ng / 4294967296.0), fac[8]; int nf = 0; fac[nf++] = logq;
    Pt *cur = malloc(sizeof(Pt) * (size_t)NP);
    for (int p = 0; p < NP; p++) {
        int k = gl[nx() % (uint64_t)ng]; cur[p] = base; cur[p].x.w[16] = GW[k]; cur[p].y.w[16] = GW[k] - CDW16;
        fwd(&cur[p].x,16); fwd(&cur[p].y,16);
    }
    Ch *kid = NULL; size_t kcap = 0; long hits[23] = {0};
    for (int i = 17; i <= 22; i++) {
        int cell = i <= lastcell, mask17 = (mode == 'M' && i == 17), look = i >= lastcell;
        size_t nk = 0; double tot = 0;
        for (int p = 0; p < NP; p++) {
            const Pt *q = &cur[p]; const Mb *X = &q->x, *Y = &q->y;
            uint32_t cx = A_(X,i-4) + E_(X,i-4) + BS1(E_(X,i-1)) + CHf(E_(X,i-1),E_(X,i-2),E_(X,i-3)) + KC[i];
            uint32_t cy = A_(Y,i-4) + E_(Y,i-4) + BS1(E_(Y,i-1)) + CHf(E_(Y,i-1),E_(Y,i-2),E_(Y,i-3)) + KC[i];
            uint32_t ax0 = BS0(A_(X,i-1)) + MAJf(A_(X,i-1),A_(X,i-2),A_(X,i-3)) - A_(X,i-4);
            uint32_t ay0 = BS0(A_(Y,i-1)) + MAJf(A_(Y,i-1),A_(Y,i-2),A_(Y,i-3)) - A_(Y,i-4);
            uint32_t dw = sch(X,i) - sch(Y,i);
            uint32_t m = 0, val = 0; double w1 = 1.0 / (double)N[i];
            int gi = -1;
            if (cell) { m = CME[i] | PLS[i]; val = CVE[i] | (E_(X,i-1) & PLS[i]); w1 = ldexp(1.0, -__builtin_popcount(m)) / (double)N[i]; }
            if (mask17) {
                for (int k = 0; k < 32; k++) if (GW[k] == X->w[16]) gi = k;
                m = FT_ME[gi]; val = FT_VE[gi]; w1 = ldexp(1.0, -__builtin_popcount(m)) / (double)N[i];
                if (cx != FT_C17[gi]) { fprintf(stderr, "c17 mismatch\n"); return 1; }
            }
            // look-ahead constants for row j = i + 1 (dummy W_j^x = 0)
            int j = i + 1; uint32_t dwj = 0, hx = 0, hy = 0;
            if (look) {
                dwj = sch(X,j) - sch(Y,j);
                if (dwj != TDW[j]) continue;
                hx = A_(X,j-4) + E_(X,j-4) + KC[j]; hy = A_(Y,j-4) + E_(Y,j-4) + KC[j] - dwj;
            }
            for (long c = 0; c < N[i]; c++) {
                uint32_t e = (uint32_t)(nx() >> 32);
                if (m) e = (e & ~m) | val;
                uint32_t wx = e - cx, wy = wx - dw, ey = cy + wy, ax = e + ax0, ay = ey + ay0;
                if (cell) {
                    if ((ax & CMA[i]) != CVA[i] || (ax ^ ay) != CDA[i] || (e ^ ey) != CDE[i]) continue;
                    if ((wx & CMW[i]) != CVW[i] || (wx ^ wy) != CDW[i]) continue;
                }
                if (look) {
                    uint32_t ejx = hx + BS1(e) + CHf(e, E_(X,i-1), E_(X,i-2)), ejy = hy + BS1(ey) + CHf(ey, E_(Y,i-1), E_(Y,i-2));
                    if ((uint32_t)(ejx - ejy) != TDE[j]) continue;
                    uint32_t ajx = ejx - A_(X,j-4) + BS0(ax) + MAJf(ax, A_(X,i-1), A_(X,i-2));
                    uint32_t ajy = ejy - A_(Y,j-4) + BS0(ay) + MAJf(ay, A_(Y,i-1), A_(Y,i-2));
                    if ((uint32_t)(ajx - ajy) != TDA[j]) continue;
                }
                if (nk == kcap) { kcap = kcap ? 2 * kcap : 65536; kid = realloc(kid, kcap * sizeof(Ch)); if (!kid) { fprintf(stderr, "oom\n"); return 1; } }
                Ch *ch = &kid[nk]; ch->p = *q; ch->p.x.w[i] = wx; ch->p.y.w[i] = wy; fwd(&ch->p.x,i); fwd(&ch->p.y,i);
                if (E_(&ch->p.x,i) != e || E_(&ch->p.y,i) != ey || A_(&ch->p.x,i) != ax || A_(&ch->p.y,i) != ay) { fprintf(stderr, "step mismatch\n"); return 1; }
                if (cell && !cellrow(&ch->p, i)) continue;
                if (look && !nextok(&ch->p, j)) { fprintf(stderr, "look-ahead mismatch row %d\n", j); return 1; }
                if (!cell && ((uint32_t)(A_(&ch->p.x,i) - A_(&ch->p.y,i)) != TDA[i] || (uint32_t)(E_(&ch->p.x,i) - E_(&ch->p.y,i)) != TDE[i] || (uint32_t)(wx - wy) != TDW[i])) { fprintf(stderr, "row %d differences off\n", i); return 1; }
                ch->wt = w1; tot += w1; nk++;
            }
        }
        hits[i] = (long)nk; double f = tot / NP; fac[nf++] = log2(f); logq += log2(f);
        if (!nk) { printf("mode %c seed %llu: extinct at row %d\n", mode, (unsigned long long)seed, i); return 0; }
        // systematic resampling
        double u = unif() * tot / NP, acc = kid[0].wt; size_t k = 0;
        for (int p = 0; p < NP; p++) {
            double tg = u + (double)p * tot / NP;
            while (acc <= tg && k + 1 < nk) { k++; acc += kid[k].wt; }
            cur[p] = kid[k].p;
        }
    }
    // tail: uniform W23^x, variant uniform from the 512, weight 1{W7 in F7, event} 2^32/|F7| / NT
    double wt = 4294967296.0 / F7N / (double)NT, tt = 0, tcell = 0, tft = 0; long nh = 0, ncp = 0, nft = 0, nver = 0, nfail = 0;
    for (int p = 0; p < NP; p++) for (long c = 0; c < NT; c++) {
        const Pt *q0 = &cur[p];
        int v = (int)(nx() >> 55) & (NVS - 1);
        uint32_t w23 = (uint32_t)(nx() >> 32);
        uint32_t w7 = w23 - ls1(q0->x.w[21]) - q0->x.w[16] - ls0(VW(v,0,8));
        if (!inF7(w7)) continue;
        Pt q = *q0;
        q.x.w[7] = w7; q.y.w[7] = w7 + CD7;
        for (int i = 8; i < 16; i++) { q.x.w[i] = VW(v,0,i); q.y.w[i] = VW(v,1,i); }
        int ok = 1;
        for (int i = 23; i < NROW && ok; i++) {
            q.x.w[i] = sch(&q.x,i); q.y.w[i] = sch(&q.y,i);
            fwd(&q.x,i); fwd(&q.y,i);
            if (mode == 'C') ok = cellrow(&q, i);
        }
        if (q.x.w[23] != w23) { fprintf(stderr, "W23 mismatch\n"); return 1; }
        if (!ok) continue;
        for (int i = NROW - 4; i < NROW; i++) if (A_(&q.x,i) != A_(&q.y,i) || E_(&q.x,i) != E_(&q.y,i)) ok = 0;
        if (!ok) { if (mode == 'C') nfail++; continue; }
        uint32_t cv[8], mx[16], my[16]; int cp = 0, ft = 0;
        if (!verify(&q, v, w7, cv, mx, my, &cp, &ft)) { nfail++; continue; }
        nver++; nh++; tt += wt; if (cp) { ncp++; tcell += wt; } if (ft) { nft++; tft += wt; }
        if (fs) {
            fprintf(fs, "%c %d %d %u %u %08x %08x %08x", mode, cp, ft, VSR[v][0], VSR[v][1], VSR[v][2], VSR[v][3], VSR[v][4]);
            for (int k = 0; k < 8; k++) fprintf(fs, " %08x", cv[k]);
            for (int k = 0; k < 16; k++) fprintf(fs, " %08x", mx[k]);
            for (int k = 0; k < 16; k++) fprintf(fs, " %08x", my[k]);
            fprintf(fs, "\n");
        }
    }
    if (fs) fclose(fs);
    double tf = tt / NP; fac[nf++] = log2(tf > 0 ? tf : 1e-300); logq += log2(tf > 0 ? tf : 1e-300);
    printf("mode %c seed %llu NP %d: log2 q3 = %.4f  stages:", mode, (unsigned long long)seed, NP, logq);
    for (int k = 0; k < nf; k++) printf(" %.3f", fac[k]);
    printf("  |Gused| %d  tail successes %ld verified %ld failed %ld (bad %ld/%ld/%ld/%ld/%ld/%ld/%ld)  cellpath %ld (wfrac %.4f)  firsttest %ld (wfrac %.4f)  kids:",
           ng, nh, nver, nfail, nbad[0], nbad[1], nbad[2], nbad[3], nbad[4], nbad[5], nbad[6], ncp, tt > 0 ? tcell / tt : 0, nft, tt > 0 ? tft / tt : 0);
    for (int i = 17; i <= 22; i++) printf(" %ld", hits[i]);
    printf("\n");
    return 0;
}
