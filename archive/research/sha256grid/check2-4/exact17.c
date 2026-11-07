// exact17.c - check2-4: exact row-17 counts for every G word (rows 12..15 published, row 16 from the G word).
// Over the 2^22 values of E17^x that pass the filed first row-17 test (mask FT_ME / value FT_VE, 10 bits) count
//   cells : every cell of row 17 (A, E, W x-values and XOR differences, '+', two-bit conditions keyed at 17)
//   rel   : published modular differences of row 18 (dummy-word step of row 18)
//   both  : cells and rel
// The M-event stage-17 factor is 2^-10 x mean(rel)/2^22 over G; the cell stage factor is 2^-10 x mean(cells)/2^22.
#include <stdio.h>
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
static inline void fwd(Mb *t, int i) {
    uint32_t e = A_(t,i-4) + E_(t,i-4) + BS1(E_(t,i-1)) + CHf(E_(t,i-1),E_(t,i-2),E_(t,i-3)) + KC[i] + t->w[i];
    E_(t,i) = e; A_(t,i) = e - A_(t,i-4) + BS0(A_(t,i-1)) + MAJf(A_(t,i-1),A_(t,i-2),A_(t,i-3));
}
static inline uint32_t sch(const Mb *t, int j){return ls1(t->w[j-2]) + t->w[j-7] + ls0(t->w[j-15]) + t->w[j-16];}
static inline uint32_t vget(const Mb *t, int k, int i){return k==0 ? A_(t,i) : k==1 ? E_(t,i) : t->w[i];}
static const uint32_t *CMk[3]={CMA,CME,CMW}, *CVk[3]={CVA,CVE,CVW}, *CDk[3]={CDA,CDE,CDW};
static int cellrow(const Pt *p, int i) {
    for (int k = 0; k < 3; k++) { uint32_t vx = vget(&p->x,k,i), vy = vget(&p->y,k,i);
        if ((vx & CMk[k][i]) != CVk[k][i] || (vx ^ vy) != CDk[k][i]) return 0; }
    if ((E_(&p->x,i) ^ E_(&p->x,i-1)) & PLS[i]) return 0;
    for (int j = 0; j < NTB; j++) if (TROW[j] == i) {
        uint32_t b1 = (vget(&p->x,TK1[j],TI1[j]) >> TB1[j]) & 1, b2 = (vget(&p->x,TK2[j],TI2[j]) >> TB2[j]) & 1;
        if ((b1 ^ b2) != (uint32_t)TNE[j]) return 0; }
    return 1;
}
int main(void) {
    uint32_t TDA18 = XA[22] - YA[22], TDE18 = XE[22] - YE[22], TDW18 = XW[18] - YW[18];
    Pt base; memset(&base, 0, sizeof base);
    for (int i = -4; i < 16; i++) { A_(&base.x,i) = XA[i+4]; E_(&base.x,i) = XE[i+4]; A_(&base.y,i) = YA[i+4]; E_(&base.y,i) = YE[i+4]; }
    for (int i = 0; i < 16; i++) { base.x.w[i] = XW[i]; base.y.w[i] = YW[i]; }
    double sc = 0, sr = 0, sb = 0;
    for (int g = 0; g < 32; g++) {
        Pt p = base; p.x.w[16] = GW[g]; p.y.w[16] = GW[g] - CDW16; fwd(&p.x,16); fwd(&p.y,16);
        uint32_t dw17 = sch(&p.x,17) - sch(&p.y,17), dw18 = sch(&p.x,18) - sch(&p.y,18);
        uint32_t m = FT_ME[g], v = FT_VE[g], free = ~m; long nc = 0, nr = 0, nb = 0, n = 0;
        // enumerate the 2^22 values with the mask's bits fixed: iterate over subsets of the free bits
        uint32_t s = 0;
        do {
            uint32_t e = s | v; n++;
            Pt q = p; q.x.w[17] = e - (A_(&p.x,13) + E_(&p.x,13) + BS1(E_(&p.x,16)) + CHf(E_(&p.x,16),E_(&p.x,15),E_(&p.x,14)) + KC[17]);
            q.y.w[17] = q.x.w[17] - dw17; fwd(&q.x,17); fwd(&q.y,17);
            if (E_(&q.x,17) != e) { fprintf(stderr, "E17 mismatch\n"); return 1; }
            int c = cellrow(&q,17);
            Pt r = q; r.x.w[18] = 0; r.y.w[18] = 0u - dw18; fwd(&r.x,18); fwd(&r.y,18);
            int rel = dw18 == TDW18 && (uint32_t)(E_(&r.x,18) - E_(&r.y,18)) == TDE18 && (uint32_t)(A_(&r.x,18) - A_(&r.y,18)) == TDA18;
            nc += c; nr += rel; nb += c && rel;
            s = (s - free) & free;
        } while (s != 0);
        printf("G %2d %08x  mask-set %ld  cells %ld  rel %ld (2^%.4f of 2^32)  both %ld  dW17 %08x dW18 %08x\n", g, GW[g], n, nc, nr,
               log2((double)nr) - 10 - 22, nb, dw17, dw18);
        sc += (double)nc / n; sr += (double)nr / n; sb += (double)nb / n;
    }
    printf("G-average: row-17 cells 2^%.4f; M-event stage 17 (mask and row-18 modular differences) 2^%.4f; cells and rel 2^%.4f\n",
           log2(sc / 32) - 10, log2(sr / 32) - 10, log2(sb / 32) - 10);
    return 0;
}
