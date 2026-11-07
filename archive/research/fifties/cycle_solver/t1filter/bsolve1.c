/* LAYOUT 1 copy (batch_*.txt from gen_batch.py: only K0.b1 varies, X9 and S6 batch constants); used for run 'v'.
 * The production/main solver is bsolve.c (layout 2).  Binary: bsolve1.
 * t1filter batch solver for the split_e3 21-equation cycle (design ev.DESIGN, loop variable g = C0.b1).
 *
 * Reformulation (exact, see RESULT.md):
 *   upstream (C0 block, params Y4,X4,X8,w6 -- batch constants):
 *     Y8 = rol(Y4,7)^g ; c = rol(g^rol(X4,20),12) [C0.c1] ; Y12 = Y8-c ; d = c-X8 [C0.d1] ;
 *     Y0 = rol(Y12,8)^d ; a = Y0-g-w6 [C0.a1] ; A' = a - X4 + 0x566d1711   (so K1.a1 = A' - X0)
 *   T1 = K1.a1 ^ rol(K1.d1,16) with K1.d1 g-free  =>
 *     T1 in [0,2^W)  <=>  A' in [lo, lo+2^W) mod 2^32,  lo = X0 + (R & ~(2^W-1)),  R = rol(K1.d1,16);  T1 = 0 <=> A' = X0+R
 *   g-only (S11 batch constant): X12 = rol(d,16)^a ; D1.d1 = 0x44036000 - X12 - S11 ; X1 = rol(X12,8)^D1.d1 ;
 *     r = rol(D1.d1,16) ; p = X1 - a
 *   per proposal (only K0.b1 varies): Q = X5 + S1 - K1.b1 + X0 + (X4 - 0x566d1711) ; P = S1 + S6 ; X5r = rol(X5,20)
 *   per candidate: e = p+Q [C1.a1] ; dd = rol(e,16)^rol(X13,16) [C1.d1] ; cc = X9+dd [C1.c1] ;
 *     b = rol(cc,20)^X5r [C1.b1] ; w = (r^S12)-P [w10] ; y = e+b+w [Y1] ; z = rol(dd^y,24) [Y13] ; root iff Y9-cc-z == 0
 * Modes:
 *   table : production layout. Entries (A',g,r,p) sorted by A' (built only for the 2^16-wide A' buckets touched by this
 *           run's proposals, to bound memory); each proposal = two binary searches + a scan of its candidates.
 *   stream: g-major order of the same computation (memory O(proposals)); used for wide-W validation.
 * Output: one line per root with T1 in [1,2^W): "pid g T1"; per-proposal stats "S pid candidates ops".
 * usage: bsolve <batchfile> <W> <table|stream> <b0> <b1> <outfile>
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <time.h>
typedef uint32_t u32;
typedef uint64_t u64;
static inline u32 rol(u32 x, int n) { return (x << n) | (x >> (32 - n)); }
typedef struct { u32 a, g, r, p; } ent;
typedef struct { int pid; u32 S12, S1, X0, X5, K1b1, K1d1; u32 R, lo, Q, P, X5r, z0; u64 ncand, nops; } prop;
static u32 Y4, Y9, X4, X8, w6, S11, X13, X9, S6;      /* batch constants */
static u32 rY4, rX4, kA, kD, X13r, kQ;
static u32 W, MASKHI; static u64 SPAN;
static inline u32 upA(u32 g, u32 *pa, u32 *pd) {      /* 10 ops */
    u32 Y8 = rY4 ^ g;
    u32 c = rol(g ^ rX4, 12);
    u32 Y12 = Y8 - c;
    u32 d = c - X8;
    u32 Y0 = rol(Y12, 8) ^ d;
    u32 a = Y0 - g - w6;
    *pa = a; *pd = d;
    return a + kA;
}
static inline void gonly(u32 a, u32 d, u32 *pr, u32 *pp) {   /* 7 ops */
    u32 X12 = rol(d, 16) ^ a;
    u32 D1d1 = kD - X12;
    u32 X1 = rol(X12, 8) ^ D1d1;
    *pr = rol(D1d1, 16);
    *pp = X1 - a;
}
static inline int cand(const prop *q, u32 r, u32 p) {   /* 14 arithmetic + 1 compare; +2 loads (r,p) = 17 */
    u32 e = p + q->Q;
    u32 dd = rol(e, 16) ^ X13r;
    u32 cc = X9 + dd;
    u32 b = rol(cc, 20) ^ q->X5r;
    u32 w = (r ^ q->S12) - q->P;
    u32 y = e + b + w;
    u32 z = rol(dd ^ y, 24);
    return (u32)(Y9 - cc - z) == 0u;
}
#define OPS_CAND 17
#define OPS_PROP 9   /* R 1, lo 2, Q 4, P 1, X5r 1 (excluding the K0.b1 pre-part and the binary searches, counted apart) */
static void setup_prop(prop *q) {
    q->R = rol(q->K1d1, 16);
    q->lo = q->X0 + (q->R & MASKHI);
    q->z0 = q->X0 + q->R;                      /* A' giving T1 = 0 (excluded; tested only on roots) */
    q->Q = q->X5 + q->S1 - q->K1b1 + q->X0 + kQ;
    q->P = q->S1 + S6;
    q->X5r = rol(q->X5, 20);
    q->ncand = 0; q->nops = OPS_PROP;
}
static FILE *fo;
static u64 tot_roots = 0;
static void emit(const prop *q, u32 g, u32 Ap) {
    u32 T1 = (Ap - q->X0) ^ q->R;
    if (T1 == 0) return;                       /* T1 = 0 is outside [1,2^W) */
    fprintf(fo, "R %d %08x %u\n", q->pid, g, T1); tot_roots++;
}
/* lower_bound on sorted entries by key a */
static u64 lb(const ent *E, u64 n, u32 key, u64 *steps) {
    u64 lo = 0, hi = n; while (lo < hi) { u64 m = (lo + hi) >> 1; (*steps)++; if (E[m].a < key) lo = m + 1; else hi = m; }
    return lo;
}
int main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage\n"); return 1; }
    FILE *f = fopen(argv[1], "r"); W = atoi(argv[2]); int mode_table = !strcmp(argv[3], "table");
    int b0 = atoi(argv[4]), b1 = atoi(argv[5]); fo = fopen(argv[6], "w");
    MASKHI = (W >= 32) ? 0u : ~((1u << W) - 1u); SPAN = (u64)1 << W;
    int nb; if (fscanf(f, "%d", &nb) != 1) return 1;
    u64 grand_cand = 0, grand_ops = 0, nprop_all = 0, max_ops = 0, table_entries_max = 0;
    for (int bi = 0; bi < nb; bi++) {
        int bid, np; char tagc[4];
        if (fscanf(f, "%3s %d %d %x %x %x %x %x %x %x %x %x", tagc, &bid, &np, &Y4, &Y9, &X4, &X8, &w6, &S11, &X13, &X9, &S6) != 12) return 2;
        prop *P = calloc(np, sizeof(prop));
        for (int j = 0; j < np; j++)
            if (fscanf(f, "%3s %d %x %x %x %x %x %x", tagc, &P[j].pid, &P[j].S12, &P[j].S1, &P[j].X0, &P[j].X5, &P[j].K1b1, &P[j].K1d1) != 8) return 3;
        if (bi < b0 || bi >= b1) { free(P); continue; }
        clock_t t0 = clock();
        rY4 = rol(Y4, 7); rX4 = rol(X4, 20); kA = 0x566d1711u - X4; kD = 0x44036000u - S11; X13r = rol(X13, 16); kQ = X4 - 0x566d1711u;
        for (int j = 0; j < np; j++) setup_prop(&P[j]);
        if (mode_table) {
            /* mark 2^16-buckets touched by the proposals' A' ranges */
            static uint8_t mark[65536]; memset(mark, 0, sizeof mark);
            for (int j = 0; j < np; j++) {
                u64 nbk = (SPAN >> 16) + 1; if (nbk > 65536) nbk = 65536;
                for (u64 t = 0; t < nbk; t++) mark[((P[j].lo >> 16) + t) & 0xffff] = 1;
            }
            static u64 cnt[65537]; memset(cnt, 0, sizeof cnt);
            for (u64 gg = 0; gg < ((u64)1 << 32); gg++) { u32 a, d; u32 Ap = upA((u32)gg, &a, &d); cnt[(Ap >> 16) + 1] += mark[Ap >> 16]; }
            for (int b = 0; b < 65536; b++) cnt[b + 1] += cnt[b];
            u64 n = cnt[65536]; if (n > table_entries_max) table_entries_max = n;
            ent *E = malloc(n * sizeof(ent)), *T = NULL; u64 *pos = malloc(65536 * sizeof(u64));
            for (int b = 0; b < 65536; b++) pos[b] = cnt[b];
            for (u64 gg = 0; gg < ((u64)1 << 32); gg++) {
                u32 a, d; u32 Ap = upA((u32)gg, &a, &d);
                if (mark[Ap >> 16]) { ent e; e.a = Ap; e.g = (u32)gg; gonly(a, d, &e.r, &e.p); E[pos[Ap >> 16]++] = e; }
            }
            /* sort each bucket by low 16 bits (counting sort) */
            u64 maxb = 0; for (int b = 0; b < 65536; b++) if (cnt[b + 1] - cnt[b] > maxb) maxb = cnt[b + 1] - cnt[b];
            T = malloc((maxb + 1) * sizeof(ent)); static u64 c2[65537];
            for (int b = 0; b < 65536; b++) {
                u64 s = cnt[b], e = cnt[b + 1]; if (e - s < 2) continue;
                memset(c2, 0, sizeof c2);
                for (u64 i = s; i < e; i++) c2[(E[i].a & 0xffff) + 1]++;
                for (int k = 0; k < 65536; k++) c2[k + 1] += c2[k];
                for (u64 i = s; i < e; i++) T[c2[E[i].a & 0xffff]++] = E[i];
                memcpy(E + s, T, (e - s) * sizeof(ent));
            }
            free(T); free(pos);
            clock_t t1 = clock();
            /* queries */
            for (int j = 0; j < np; j++) {
                prop *q = &P[j]; u64 steps = 0;
                u32 lo = q->lo; u64 hi = (u64)lo + SPAN;          /* [lo, hi) possibly wrapping */
                u64 segs[2][2]; int ns = 0;
                if (W >= 32) { segs[0][0] = 0; segs[0][1] = (u64)1 << 32; ns = 1; }
                else if (hi <= ((u64)1 << 32)) { segs[0][0] = lo; segs[0][1] = hi; ns = 1; }
                else { segs[0][0] = lo; segs[0][1] = (u64)1 << 32; segs[1][0] = 0; segs[1][1] = hi - ((u64)1 << 32); ns = 2; }
                for (int s = 0; s < ns; s++) {
                    u64 i0 = lb(E, n, (u32)segs[s][0], &steps);
                    u64 i1 = (segs[s][1] >= ((u64)1 << 32)) ? n : lb(E, n, (u32)segs[s][1], &steps);
                    for (u64 i = i0; i < i1; i++) {
                        if (cand(q, E[i].r, E[i].p)) emit(q, E[i].g, E[i].a);
                    }
                    q->ncand += i1 - i0;
                }
                q->nops += q->ncand * OPS_CAND + steps * 2;     /* each binary-search step: 1 load + 1 compare */
            }
            free(E);
            fprintf(stderr, "batch %d: table %llu entries, build %.1fs, queries %.2fs\n", bid, (unsigned long long)n,
                    (double)(t1 - t0) / CLOCKS_PER_SEC, (double)(clock() - t1) / CLOCKS_PER_SEC);
        } else {
            /* stream: per 2^16 bucket, list of proposals whose range touches it */
            int *head = malloc(65536 * sizeof(int)); memset(head, -1, 65536 * sizeof(int));
            u64 cap = 0; for (int j = 0; j < np; j++) cap += ((SPAN >> 16) + 2 < 65536 ? (SPAN >> 16) + 2 : 65536);
            int *nxt = malloc(cap * sizeof(int)), *who = malloc(cap * sizeof(int)); u64 used = 0;
            for (int j = 0; j < np; j++) {
                u64 nbk = (SPAN >> 16) + 1; if (nbk > 65536) nbk = 65536;
                for (u64 t = 0; t < nbk; t++) { int b = ((P[j].lo >> 16) + t) & 0xffff; who[used] = j; nxt[used] = head[b]; head[b] = (int)used; used++; }
            }
            for (u64 gg = 0; gg < ((u64)1 << 32); gg++) {
                u32 a, d; u32 Ap = upA((u32)gg, &a, &d); int h = head[Ap >> 16]; if (h < 0) continue;
                u32 r, p; int have = 0;
                for (; h >= 0; h = nxt[h]) {
                    prop *q = &P[who[h]];
                    if ((u64)(u32)(Ap - q->lo) >= SPAN) continue;
                    if (!have) { gonly(a, d, &r, &p); have = 1; }
                    q->ncand++;
                    if (cand(q, r, p)) emit(q, (u32)gg, Ap);
                }
            }
            for (int j = 0; j < np; j++) P[j].nops += P[j].ncand * OPS_CAND;
            free(head); free(nxt); free(who);
            fprintf(stderr, "batch %d: stream %.1fs\n", bid, (double)(clock() - t0) / CLOCKS_PER_SEC);
        }
        for (int j = 0; j < np; j++) {
            fprintf(fo, "S %d %llu %llu\n", P[j].pid, (unsigned long long)P[j].ncand, (unsigned long long)P[j].nops);
            grand_cand += P[j].ncand; grand_ops += P[j].nops; nprop_all++; if (P[j].nops > max_ops) max_ops = P[j].nops;
        }
        fflush(fo); free(P);
    }
    fprintf(fo, "T proposals %llu candidates %llu ops %llu maxops %llu roots %llu table_entries_max %llu\n",
            (unsigned long long)nprop_all, (unsigned long long)grand_cand, (unsigned long long)grand_ops,
            (unsigned long long)max_ops, (unsigned long long)tot_roots, (unsigned long long)table_entries_max);
    fclose(fo); return 0;
}
