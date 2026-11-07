/* ctr_toy.c: scaled-down end-to-end test of the chunk-counter lever on the 55/63 path (research only).
 *
 * Toy hash = task5_small_h8/toy.h (copied unchanged): BLAKE3, 2 rounds, W-bit words, IV = top W bits, rotations
 * (4,3,2,1) at W = 8, toy byte = 2 bits, block = 16 words = 8W toy bytes, chunk = 16 blocks. Messages A, B of the
 * family: 7W-1 and 7W+7 toy bytes (55/63 at W = 8), B = A with w4 -> w4', w5 -> w5 + delta.
 *
 * Two arrangements of the same two-level trial (task5 small_h8.cu, research/h8/twolevel/two_level_H8.txt):
 *  FILED   : single-chunk messages, the colliding compression is the ROOT: counter 0, flags 11.
 *            trial = (context, X2, member Y4); w0 is derived (K0.a1 = ROL(K0.d1,R1) ^ 0).
 *  COUNTER : messages P||A and P||B, P = t identical full chunks (all zero toy bytes). The last chunk is one block,
 *            counter t, flags 3 (CHUNK_START|CHUNK_END); its CV equal for A and B gives a full collision.
 *            outer step = (context, X2, member Y4) built with flags 3; inner word = E1.d1, drawn from a set D
 *            (the d1 values of one beta, the toy analogue of "c1 in the heaviest beta's cube").
 *            Per inner trial: E1.a1 = ROL(d1,R1) ^ Y12, Y6 = E1.a1 - Y1 - w12, C2 second half inverted -> Y10, Y14,
 *            Y2, w0; K0.a1 = IV0+IV4+w0; t = ROL(K0.d1,R1) ^ K0.a1 (the counter absorbs w0); w1 = S0 - K0.a1 - K0.b1.
 *            Trials with t = 0 are skipped (that would be a single-chunk message whose last chunk is the root).
 * Every trial is hashed as two real last-chunk compressions (full 2 rounds, A and B); every collision is rebuilt as
 * two full byte strings (prefix chunks included) and hashed with the toy TREE mode (tree_hash below, written after
 * hash-smash/verifier/blake3.py); bogus = collisions the tree hash does not confirm.
 *
 * Modes:
 *   ctr_toy mass SETS ID [OUTFILE]          exact counts: sumper (must equal the SET line), mass per (member, d1),
 *                                           per beta; prints the heaviest beta and its gain
 *   ctr_toy check SETS ID BETA NTR SEED     construction checks for both arrangements (88 words vs forward, Y4,
 *                                           E1.d1, half digest, byte hash = word hash, tree hash = CV path)
 *   ctr_toy run ARR SETS ID BETA FIRST COUNT NOUTER   ARR = filed | ctr ; BETA ignored for filed
 *   ctr_toy treetest SEED N                 random messages and their toy tree hashes (for the Python cross-check)
 */
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "toy.h"
#include "tl_lines.inc"

#define CHUNKBYTES (16 * BLOCKBYTES)
#define NW (1u << WBITS)
#define SEED_BASE 820261008ull
#define F_START 1u
#define F_END 2u
#define F_PARENT 4u
#define F_ROOT 8u

typedef struct { u32 c0c1, c0d1, d3d1, s15, ncls; u32 cls[MAXCLS]; u32 nd; u32 dl[NW]; } Run;

#define PRE(p, r, g, FLGV)                                                                                       \
    const u32 IV0 = (p)->iv[0], IV1 = (p)->iv[1], IV2 = (p)->iv[2], IV3 = (p)->iv[3];                            \
    const u32 IV4 = (p)->iv[4], IV5 = (p)->iv[5], IV6 = (p)->iv[6], IV7 = (p)->iv[7];                            \
    const u32 CTR0 = 0, CTR1 = 0, LENA = LEN_A & M, FLG = (FLGV) & M;                                            \
    const u32 X3 = (p)->x3, X7 = (p)->x7, X11 = (p)->x11, X15 = (p)->x15;                                        \
    const u32 w4 = (p)->w4, w13 = (p)->w13, w14 = 0, w15 = 0;                                                    \
    const u64 oi_ = (g) >> WBITS;                                                                                \
    const u32 X2 = (u32)(g) & M, w5 = (u32)oi_ & M, S9 = (u32)(oi_ >> WBITS) & M;                                \
    const u32 S15 = ((r)->s15 + (u32)(oi_ >> (2 * WBITS))) & M;                                                  \
    const u32 C0_c1 = (r)->c0c1, C0_d1 = (r)->c0d1, D3_d1 = (r)->d3d1;

/* last-chunk compression, unrolled: counter ctr (< 2^W, so v13 = 0), flags fl; returns the 8 output words, the
   b output of C0 (Y4) and the first-half d value of E1 (E1.d1) */
static inline void comp(const u32 *iv, const u32 *m, u32 len, u32 ctr, u32 fl, u32 *out, u32 *y4, u32 *e1d1) {
    u32 v0 = iv[0], v1 = iv[1], v2 = iv[2], v3 = iv[3], v4 = iv[4], v5 = iv[5], v6 = iv[6], v7 = iv[7];
    u32 v8 = iv[0], v9 = iv[1], v10 = iv[2], v11 = iv[3], v12 = ctr & M, v13 = 0, v14 = len & M, v15 = fl & M;
    GF(v0, v4, v8, v12, m[0], m[1]);   GF(v1, v5, v9, v13, m[2], m[3]);
    GF(v2, v6, v10, v14, m[4], m[5]);  GF(v3, v7, v11, v15, m[6], m[7]);
    GF(v0, v5, v10, v15, m[8], m[9]);  GF(v1, v6, v11, v12, m[10], m[11]);
    GF(v2, v7, v8, v13, m[12], m[13]); GF(v3, v4, v9, v14, m[14], m[15]);
    GF(v0, v4, v8, v12, m[2], m[6]);   *y4 = v4;
    GF(v1, v5, v9, v13, m[3], m[10]);
    GF(v2, v6, v10, v14, m[7], m[0]);  GF(v3, v7, v11, v15, m[4], m[13]);
    GF(v0, v5, v10, v15, m[1], m[11]);
    /* E1 = G(v1, v6, v11, v12; m12, m5), written out to catch d1 */
    v1 = (v1 + v6 + m[12]) & M; v12 = ror(v12 ^ v1, ROT1); *e1d1 = v12; v11 = (v11 + v12) & M; v6 = ror(v6 ^ v11, ROT2);
    v1 = (v1 + v6 + m[5]) & M;  v12 = ror(v12 ^ v1, ROT3); v11 = (v11 + v12) & M; v6 = ror(v6 ^ v11, ROT4);
    GF(v2, v7, v8, v13, m[9], m[14]);  GF(v3, v4, v9, v14, m[15], m[8]);
    out[0] = v0 ^ v8;  out[1] = v1 ^ v9;  out[2] = v2 ^ v10; out[3] = v3 ^ v11;
    out[4] = v4 ^ v12; out[5] = v5 ^ v13; out[6] = v6 ^ v14; out[7] = v7 ^ v15;
}

/* ---------------- toy tree mode, written after hash-smash/verifier/blake3.py (array state, loop) ---------------- */
static void tcomp(const u32 *cv, const u32 *w, u64 ctr, u32 blen, u32 fl, u32 *out8) {
    static const int P[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
    u32 v[16], m[16], t[16];
    for (int i = 0; i < 8; i++) v[i] = cv[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IV32[i] >> (32 - WBITS);
    v[12] = (u32)(ctr & M); v[13] = (u32)((ctr >> WBITS) & M); v[14] = blen & M; v[15] = fl & M;
    memcpy(m, w, sizeof m);
    for (int r = 0; r < 2; r++) {
        GF(v[0], v[4], v[8], v[12], m[0], m[1]);   GF(v[1], v[5], v[9], v[13], m[2], m[3]);
        GF(v[2], v[6], v[10], v[14], m[4], m[5]);  GF(v[3], v[7], v[11], v[15], m[6], m[7]);
        GF(v[0], v[5], v[10], v[15], m[8], m[9]);  GF(v[1], v[6], v[11], v[12], m[10], m[11]);
        GF(v[2], v[7], v[8], v[13], m[12], m[13]); GF(v[3], v[4], v[9], v[14], m[14], m[15]);
        for (int i = 0; i < 16; i++) t[i] = m[P[i]];
        memcpy(m, t, sizeof m);
    }
    for (int i = 0; i < 8; i++) out8[i] = v[i] ^ v[i + 8];
}
static void block_words(const u8 *b, u32 n, u32 *w) {           /* n toy bytes (<= BLOCKBYTES), zero padded */
    for (int i = 0; i < 16; i++) {
        w[i] = 0;
        for (int j = 0; j < WBYTES; j++) { u32 k = (u32)(i * WBYTES + j); if (k < n) w[i] |= (u32)(b[k] & 3u) << (2 * j); }
    }
}
typedef struct { u32 cv[8], w[16]; u64 ctr; u32 blen, fl; } Out;
static void chunk_out(const u8 *c, u32 n, u64 ctr, Out *o) {    /* n toy bytes of one chunk (1..CHUNKBYTES, or 0) */
    u32 cv[8];
    for (int i = 0; i < 8; i++) cv[i] = IV32[i] >> (32 - WBITS);
    u32 last = n == 0 ? 0 : (n - 1) / BLOCKBYTES * BLOCKBYTES;
    for (u32 off = 0;; off += BLOCKBYTES) {
        u32 bl = n - off < BLOCKBYTES ? n - off : BLOCKBYTES, w[16];
        u32 fl = off == 0 ? F_START : 0u;
        block_words(c + off, bl, w);
        if (off == last) { memcpy(o->cv, cv, sizeof cv); memcpy(o->w, w, sizeof w); o->ctr = ctr; o->blen = bl; o->fl = fl | F_END; return; }
        tcomp(cv, w, ctr, BLOCKBYTES, fl, cv);
    }
}
static void parent_out(const u32 *l, const u32 *r, Out *o) {
    for (int i = 0; i < 8; i++) { o->cv[i] = IV32[i] >> (32 - WBITS); o->w[i] = l[i]; o->w[8 + i] = r[i]; }
    o->ctr = 0; o->blen = BLOCKBYTES; o->fl = F_PARENT;
}
static void tree_hash(const u8 *d, u64 len, u32 *dig) {
    u64 nch = len == 0 ? 1 : (len + CHUNKBYTES - 1) / CHUNKBYTES;
    static u32 stack[64][8];
    int sp = 0;
    Out o;
    for (u64 c = 0; c + 1 < nch; c++) {
        u32 cv[8];
        chunk_out(d + c * CHUNKBYTES, CHUNKBYTES, c, &o);
        tcomp(o.cv, o.w, o.ctr, o.blen, o.fl, cv);
        u64 tot = c + 1;
        while ((tot & 1) == 0) { Out q; sp--; parent_out(stack[sp], cv, &q); tcomp(q.cv, q.w, q.ctr, q.blen, q.fl, cv); tot >>= 1; }
        memcpy(stack[sp++], cv, sizeof cv);
    }
    chunk_out(d + (nch - 1) * CHUNKBYTES, (u32)(len - (nch - 1) * CHUNKBYTES), nch - 1, &o);
    while (sp > 0) { u32 cv[8]; tcomp(o.cv, o.w, o.ctr, o.blen, o.fl, cv); sp--; Out q; parent_out(stack[sp], cv, &q); o = q; }
    tcomp(o.cv, o.w, 0, o.blen, o.fl | F_ROOT, dig);
}

/* ---------------- sets, classes, beta ---------------- */
static int read_set(const char *file, int id, Pin *p, u32 *eta, u32 *n, u64 *sumper) {
    FILE *f = fopen(file, "r");
    char line[512];
    if (!f) return 0;
    while (fgets(line, sizeof line, f)) {
        int w, i; double a, b; u32 fy[5];
        if (sscanf(line, "SET %d %d %x %x %x %x %x %x %x %u %llu %lf %lf %x %x %x %x %x", &w, &i, &p->x3, &p->x7, &p->x11, &p->x15, &p->w4, &p->w13,
                   eta, n, sumper, &a, &b, &fy[0], &fy[1], &fy[2], &fy[3], &fy[4]) == 18 && w == WBITS && i == id) { fclose(f); return 1; }
    }
    fclose(f);
    return 0;
}
static inline u32 beta_of(const Pin *p, u32 d1) { return ror(((p->y11 + d1) ^ (p->y11b + d1)) & M, ROT2); }

static int load(const char *file, int id, Pin *p, Run *r, u32 *eta, u64 *sumper) {
    u32 n;
    static u32 cls[NW];
    if (!read_set(file, id, p, eta, &n, sumper)) { fprintf(stderr, "no SET %d %d in %s\n", WBITS, id, file); return 0; }
    if (!fill_pin(p)) { fprintf(stderr, "set %d is not a pin\n", id); return 0; }
    r->ncls = class_members(p, *eta, cls);
    if (r->ncls != n || n > MAXCLS || n == 0) { fprintf(stderr, "class mismatch\n"); return 0; }
    for (u32 k = 0; k < n; k++) r->cls[k] = cls[k];
    return 1;
}

/* ---------------- exact counts ---------------- */
static int cmd_mass(const char *file, int id, const char *outfile) {
    Pin p; Run r; u32 eta; u64 sumref;
    if (!load(file, id, &p, &r, &eta, &sumref)) return 2;
    const u32 n = r.ncls;
    u32 *e1key = (u32 *)malloc(sizeof(u32) << (3 * WBITS));
    u32 *T3 = (u32 *)calloc((size_t)1 << (3 * WBITS), sizeof(u32));
    u8 *bm = (u8 *)calloc((size_t)1 << (3 * WBITS - 3), 1);
    static u64 mass[MAXCLS][NW];
    long bad = 0;
    for (u32 d1 = 0; d1 < NW; d1++)
        for (u32 b1 = 0; b1 < NW; b1++)
            for (u32 a2 = 0; a2 < NW; a2++) {
                u32 c1 = (p.y11 + d1) & M, c1b = (p.y11b + d1) & M, Y6 = rol(b1, ROT2) ^ c1;
                u32 b1b = ror(Y6 ^ c1b, ROT2), a2b = (a2 - b1 + b1b + p.delta) & M;
                u32 d2 = ror(d1 ^ a2, ROT3), c2 = (c1 + d2) & M, b2 = ror(b1 ^ c2, ROT4);
                u32 d2b = ror(d1 ^ a2b, ROT3), c2b = (c1b + d2b) & M, b2b = ror(b1b ^ c2b, ROT4);
                u32 da = a2 ^ a2b, db = b2 ^ b2b, dc = c2 ^ c2b, dd = d2 ^ d2b;
                if (dd != ror(da, ROT3)) bad++;
                e1key[(d1 << (2 * WBITS)) | (b1 << WBITS) | a2] = (da << (2 * WBITS)) | (dc << WBITS) | db;
            }
    for (u32 k = 0; k < n; k++) {
        const u32 Y4 = r.cls[k], e1 = (p.y3 + Y4) & M, e1b = (p.y3b + Y4) & M;
        u32 nset = 0;
        static u32 used[1u << 22];
        for (u32 h1 = 0; h1 < NW; h1++) {
            const u32 Y14 = rol(h1, ROT1) ^ e1, h1b = ror(Y14 ^ e1b, ROT1);
            for (u32 Y9 = 0; Y9 < NW; Y9++) {
                const u32 g1 = (Y9 + h1) & M, f1 = ror(Y4 ^ g1, ROT2), g1b = (Y9 + h1b) & M, f1b = ror(Y4 ^ g1b, ROT2);
                for (u32 w8 = 0; w8 < NW; w8++) {
                    u32 e2 = (e1 + f1 + w8) & M, h2 = ror(h1 ^ e2, ROT3), g2 = (g1 + h2) & M, f2 = ror(f1 ^ g2, ROT4);
                    u32 e2b = (e1b + f1b + w8) & M, h2b = ror(h1b ^ e2b, ROT3), g2b = (g1b + h2b) & M, f2b = ror(f1b ^ g2b, ROT4);
                    u32 dA = e2 ^ e2b, dB = f2 ^ f2b, dC = g2 ^ g2b, dD = h2 ^ h2b;
                    if (dB != ror(dC, ROT3)) continue;
                    u32 key = (dC << (2 * WBITS)) | (dA << WBITS) | dD;
                    if (T3[key] == 0 && nset < (1u << 22)) used[nset++] = key;
                    T3[key]++; bm[key >> 3] |= (u8)(1u << (key & 7));
                }
            }
        }
        for (u32 d1 = 0; d1 < NW; d1++) {
            u64 s = 0;
            const u32 *ek = e1key + ((size_t)d1 << (2 * WBITS));
            for (u32 i = 0; i < NW * NW; i++) { u32 key = ek[i]; if (bm[key >> 3] & (1u << (key & 7))) s += T3[key]; }
            mass[k][d1] = s;
        }
        if (nset >= (1u << 22)) { memset(T3, 0, sizeof(u32) << (3 * WBITS)); memset(bm, 0, (size_t)1 << (3 * WBITS - 3)); }
        else for (u32 i = 0; i < nset; i++) { T3[used[i]] = 0; bm[used[i] >> 3] = 0; }
    }
    u64 sum = 0;
    static u64 bmass[NW]; static u32 bcnt[NW];
    for (u32 d1 = 0; d1 < NW; d1++) { u64 s = 0; for (u32 k = 0; k < n; k++) s += mass[k][d1]; sum += s; bmass[beta_of(&p, d1)] += s; bcnt[beta_of(&p, d1)]++; }
    printf("MASS W %d set %d eta %x n %u sumper %llu ref %llu %s e1model_bad %ld\n", WBITS, id, eta, n, sum, sumref, sum == sumref ? "EQUAL" : "DIFFERENT", bad);
    u32 best = 0; double bestg = -1;
    for (u32 b = 0; b < NW; b++) if (bcnt[b]) {
        double g = ((double)bmass[b] / bcnt[b]) / ((double)sum / NW);
        printf("BETA %x nd1 %u mass %llu share %.5f gain %.4f\n", b, bcnt[b], bmass[b], (double)bmass[b] / sum, g);
        if (bmass[b] > 0 && (g > bestg || (g == bestg && bcnt[b] > bcnt[best]))) { bestg = g; best = b; }
    }
    /* heaviest beta by total mass (the claim's choice) and best by gain */
    u32 heavy = 0;
    for (u32 b = 0; b < NW; b++)   /* largest total mass; a tie goes to the smaller d1 set (higher gain) */
        if (bcnt[b] && (bcnt[heavy] == 0 || bmass[b] > bmass[heavy] || (bmass[b] == bmass[heavy] && bcnt[b] < bcnt[heavy]))) heavy = b;
    double gh = ((double)bmass[heavy] / bcnt[heavy]) / ((double)sum / NW);
    printf("HEAVIEST beta %x nd1 %u mass %llu share %.5f gain %.4f\n", heavy, bcnt[heavy], bmass[heavy], (double)bmass[heavy] / sum, gh);
    printf("BESTGAIN beta %x nd1 %u mass %llu gain %.4f\n", best, bcnt[best], bmass[best], bestg);
    printf("D1LIST beta %x:", heavy);
    for (u32 d1 = 0; d1 < NW; d1++) if (beta_of(&p, d1) == heavy) printf(" %x", d1);
    printf("\n");
    if (outfile) {
        FILE *f = fopen(outfile, "w");
        fprintf(f, "# mass[member][d1] for W %d set %d eta %x n %u sumper %llu: one line per member: k y4 then %u numbers\n", WBITS, id, eta, n, sum, NW);
        for (u32 k = 0; k < n; k++) { fprintf(f, "%u %x", k, r.cls[k]); for (u32 d1 = 0; d1 < NW; d1++) fprintf(f, " %llu", mass[k][d1]); fprintf(f, "\n"); }
        fclose(f);
    }
    free(e1key); free(T3); free(bm);
    return sum == sumref ? 0 : 1;
}

/* ---------------- the two trial constructions ---------------- */
/* FILED: sixteen words of trial (g, k); with cmp the number of the 88 solved words differing from forward */
static long filed_words(const Pin *p, const Run *r, u64 g, u32 k, u32 *w, int cmp) {
    PRE(p, r, g, FLAGS)
    TL_OUTER
    TL_MIDDLE
    const u32 Y4 = r->cls[k];
    TL_MEMBER
    TL_TRIAL
    TL_WORDS(w)
    long fail = 0;
    if (cmp) { TL_FWD(w) TL_CMP(fail) }
    return fail;
}
/* COUNTER: sixteen words and the counter t of trial (g, k, d1) */
static long ctr_words(const Pin *p, const Run *r, u64 g, u32 k, u32 d1, u32 *w, u32 *tout, int cmp) {
    PRE(p, r, g, 3u)
    TL_OUTER
    TL_MIDDLE
    const u32 Y4 = r->cls[k];
    TL_MEMBER
    TL_TRIAL
    TL_WORDS(w)
    const u32 nE1a1 = rol(d1, ROT1) ^ Y12;
    const u32 nY6 = (nE1a1 - Y1 - w12) & M;
    const u32 nY10 = rol(nY6, ROT4) ^ C2_b1;
    const u32 nY14 = (nY10 - C2_c1) & M;
    const u32 nY2 = rol(nY14, ROT3) ^ C2_d1;
    const u32 nw0 = (nY2 - C2_a1 - C2_b1) & M;
    const u32 nK0a = (IV0 + IV4 + nw0) & M;
    const u32 tt = rol(K0_d1, ROT1) ^ nK0a;
    const u32 nw1 = (S0 - nK0a - K0_b1) & M;
    w[0] = nw0; w[1] = nw1; *tout = tt;
    long fail = 0;
    if (cmp) {
        const u32 CTRX = tt;
        {
            const u32 CTR0 = CTRX, K0_a1 = nK0a, Y6 = nY6, Y10 = nY10, Y14 = nY14, Y2 = nY2;
            TL_FWD(w)
            TL_CMP(fail)
            (void)CTR0;
        }
    }
    return fail;
}

/* ---------------- runs ---------------- */
typedef struct { u64 trials, tzero, bad, coll, z1, z3, z4, z6, z2; } Cnt;
typedef struct { u64 g; u32 k, d1, t; } Hit;
#define MAXH 100000
static Hit hits[MAXH];
static long nh;

#define MKAB(wa, a, b, cut)                                                                                    \
    for (int j = 0; j < 16; j++) { a[j] = wa[j] & len_mask(j, LEN_A); cut |= a[j] ^ wa[j]; }                  \
    { u32 t4 = wa[4], t5 = wa[5]; wa[4] = p->w4b; wa[5] = (wa[5] + p->delta) & M;                               \
      for (int j = 0; j < 16; j++) { b[j] = wa[j] & len_mask(j, LEN_B); cut |= b[j] ^ wa[j]; }                 \
      wa[4] = t4; wa[5] = t5; }

static inline void score(const u32 *ha, const u32 *hb, u32 extra, Cnt *c, int *coll) {
    u32 half = (ha[0] ^ hb[0]) | (ha[2] ^ hb[2]) | (ha[5] ^ hb[5]) | (ha[7] ^ hb[7]);
    u32 e1 = ha[1] ^ hb[1], e3 = ha[3] ^ hb[3], e4 = ha[4] ^ hb[4], e6 = ha[6] ^ hb[6];
    u32 nz = (e1 == 0) + (e3 == 0) + (e4 == 0) + (e6 == 0);
    c->trials++;
    if (half | extra) c->bad++;
    c->z1 += e1 == 0; c->z3 += e3 == 0; c->z4 += e4 == 0; c->z6 += e6 == 0; c->z2 += nz >= 2;
    *coll = (half | e1 | e3 | e4 | e6) == 0;
    if (*coll) c->coll++;
}

static void filed_step(const Pin *p, const Run *r, u64 g, Cnt *c) {
    PRE(p, r, g, FLAGS)
    TL_OUTER
    TL_MIDDLE
    for (u32 k = 0; k < r->ncls; k++) {
        const u32 Y4 = r->cls[k];
        TL_MEMBER
        TL_TRIAL
        u32 wa[16], a[16], b[16], ha[8], hb[8], ya, yb, da, db, cut = 0;
        TL_WORDS(wa)
        MKAB(wa, a, b, cut)
        comp(p->iv, a, LEN_A, 0, FLAGS, ha, &ya, &da);
        comp(p->iv, b, LEN_B, 0, FLAGS, hb, &yb, &db);
        int coll;
        score(ha, hb, cut | (ya ^ Y4) | (yb ^ Y4), c, &coll);
        if (coll && nh < MAXH) { hits[nh].g = g; hits[nh].k = k; hits[nh].d1 = da; hits[nh].t = 0; nh++; }
    }
}

static void ctr_step(const Pin *p, const Run *r, u64 g, Cnt *c) {
    PRE(p, r, g, 3u)
    TL_OUTER
    TL_MIDDLE
    for (u32 k = 0; k < r->ncls; k++) {
        const u32 Y4 = r->cls[k];
        TL_MEMBER
        TL_TRIAL
        u32 wa[16];
        TL_WORDS(wa)
        for (u32 j = 0; j < r->nd; j++) {
            const u32 d1 = r->dl[j];
            const u32 nE1a1 = rol(d1, ROT1) ^ Y12;
            const u32 nY6 = (nE1a1 - Y1 - w12) & M;
            const u32 nY10 = rol(nY6, ROT4) ^ C2_b1;
            const u32 nY14 = (nY10 - C2_c1) & M;
            const u32 nY2 = rol(nY14, ROT3) ^ C2_d1;
            const u32 nw0 = (nY2 - C2_a1 - C2_b1) & M;
            const u32 nK0a = (IV0 + IV4 + nw0) & M;
            const u32 tt = rol(K0_d1, ROT1) ^ nK0a;
            const u32 nw1 = (S0 - nK0a - K0_b1) & M;
            if (tt == 0) { c->tzero++; continue; }
            wa[0] = nw0; wa[1] = nw1;
            u32 a[16], b[16], ha[8], hb[8], ya, yb, da, db, cut = 0;
            MKAB(wa, a, b, cut)
            comp(p->iv, a, LEN_A, tt, 3u, ha, &ya, &da);
            comp(p->iv, b, LEN_B, tt, 3u, hb, &yb, &db);
            int coll;
            score(ha, hb, cut | (ya ^ Y4) | (yb ^ Y4) | (da ^ d1) | (db ^ d1), c, &coll);
            if (coll && nh < MAXH) { hits[nh].g = g; hits[nh].k = k; hits[nh].d1 = d1; hits[nh].t = tt; nh++; }
        }
    }
}

static u64 run_key(u64 a, u64 b, u64 c, u64 d) {
    u64 t = SEED_BASE ^ (a * 0x9E3779B97F4A7C15ull) ^ (b * 0xC2B2AE3D27D4EB4Full) ^ (c * 0x165667B19E3779F9ull) ^ (d * 0x27D4EB2F165667C5ull);
    u64 z = splitmix(&t);
    t = z ^ 0xD6E8FEB86659FD93ull;
    return splitmix(&t);
}

/* rebuild one hit as full byte strings, hash both with the tree mode; returns 1 if the digests are equal */
static int verify_hit(const Pin *p, const Run *r, int ctr, const Hit *h, u8 *A, u8 *B, u32 *dig) {
    u32 w[16], wb[16], t = 0;
    if (ctr) { if (ctr_words(p, r, h->g, h->k, h->d1, w, &t, 1) != 0 || t != h->t || t == 0) return 0; }
    else if (filed_words(p, r, h->g, h->k, w, 1) != 0) return 0;
    memcpy(wb, w, sizeof wb);
    wb[4] = p->w4b; wb[5] = (w[5] + p->delta) & M;
    u8 fa[BLOCKBYTES], fb[BLOCKBYTES];
    words_to_bytes(w, fa); words_to_bytes(wb, fb);
    for (u32 j = LEN_A; j < BLOCKBYTES; j++) if (fa[j]) return 0;
    for (u32 j = LEN_B; j < BLOCKBYTES; j++) if (fb[j]) return 0;
    memcpy(A, fa, LEN_A); memcpy(B, fb, LEN_B);
    u64 pre = (u64)t * CHUNKBYTES;
    u8 *ma = (u8 *)calloc(pre + LEN_B, 1), *mb = (u8 *)calloc(pre + LEN_B, 1);
    memcpy(ma + pre, A, LEN_A); memcpy(mb + pre, B, LEN_B);
    u32 ha[8], hb[8];
    tree_hash(ma, pre + LEN_A, ha); tree_hash(mb, pre + LEN_B, hb);
    free(ma); free(mb);
    for (int i = 0; i < 8; i++) if (ha[i] != hb[i]) return 0;
    memcpy(dig, ha, sizeof ha);
    return 1;
}

static int cmd_run(const char *arr, const char *file, int id, u32 beta, long first, long count, long long nouter) {
    Pin p; static Run r; u32 eta; u64 sumper;
    const int ctr = !strcmp(arr, "ctr");
    if (!ctr && strcmp(arr, "filed")) { fprintf(stderr, "ARR must be filed or ctr\n"); return 2; }
    if (!load(file, id, &p, &r, &eta, &sumper)) return 2;
    r.nd = 0;   /* BETA > M (e.g. 100): the control, all d1 values */
    for (u32 d1 = 0; d1 < NW; d1++) if (beta > M || beta_of(&p, d1) == beta) r.dl[r.nd++] = d1;
    if (ctr && r.nd == 0) { fprintf(stderr, "no d1 with beta %x\n", beta); return 2; }
    const u64 nmid = (u64)nouter << WBITS;
    printf("HEAD arr %s W %d set %d eta %x ncls %u sumper %llu beta %x nd %u nouter %lld first %ld count %ld\n", arr, WBITS, id, eta, r.ncls, sumper,
           ctr ? beta : 0u, ctr ? r.nd : 0u, nouter, first, count);
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    Cnt tot; memset(&tot, 0, sizeof tot);
    long bog_all = 0;
    for (long run = first; run < first + count; run++) {
        u64 st = run_key((u64)WBITS, (u64)id + 1, (u64)(ctr ? 2 : 1), (u64)run + 1);
        r.c0c1 = (u32)splitmix(&st) & M; r.c0d1 = (u32)splitmix(&st) & M; r.d3d1 = (u32)splitmix(&st) & M; r.s15 = (u32)splitmix(&st) & M;
        Cnt c; memset(&c, 0, sizeof c);
        nh = 0;
        for (u64 g = 0; g < nmid; g++) { if (ctr) ctr_step(&p, &r, g, &c); else filed_step(&p, &r, g, &c); }
        long bogus = (u64)nh != c.coll;
        for (long i = 0; i < nh; i++) {
            u8 A[BLOCKBYTES], B[BLOCKBYTES]; u32 dig[8];
            if (!verify_hit(&p, &r, ctr, &hits[i], A, B, dig)) { bogus++; continue; }
            printf("HIT arr %s W %d set %d run %ld outer %llu x2 %x member %u y4 %x d1 %x t %u A ", arr, WBITS, id, run, hits[i].g >> WBITS,
                   (u32)hits[i].g & M, hits[i].k, r.cls[hits[i].k], hits[i].d1, hits[i].t);
            for (u32 j = 0; j < LEN_A; j++) putchar('0' + A[j]);
            printf(" B ");
            for (u32 j = 0; j < LEN_B; j++) putchar('0' + B[j]);
            printf(" digest");
            for (int j = 0; j < 8; j++) printf(" %x", dig[j]);
            printf("\n");
        }
        printf("RUN arr %s W %d set %d run %ld seed %x %x %x %x nouter %lld trials %llu tzero %llu bad %llu coll %llu bogus %ld z1 %llu z3 %llu z4 %llu z6 %llu z2 %llu\n",
               arr, WBITS, id, run, r.c0c1, r.c0d1, r.d3d1, r.s15, nouter, c.trials, c.tzero, c.bad, c.coll, bogus, c.z1, c.z3, c.z4, c.z6, c.z2);
        fflush(stdout);
        tot.trials += c.trials; tot.tzero += c.tzero; tot.bad += c.bad; tot.coll += c.coll; bog_all += bogus;
    }
    clock_gettime(CLOCK_MONOTONIC, &t1);
    double secs = (double)(t1.tv_sec - t0.tv_sec) + 1e-9 * (double)(t1.tv_nsec - t0.tv_nsec);
    printf("PART arr %s W %d set %d first %ld count %ld trials %llu tzero %llu bad %llu coll %llu bogus %ld seconds %.1f rate %.3g\n", arr, WBITS, id, first,
           count, tot.trials, tot.tzero, tot.bad, tot.coll, bog_all, secs, secs > 0 ? tot.trials / secs : 0.0);
    printf("END\n");
    return 0;
}

/* ---------------- checks ---------------- */
static int cmd_check(const char *file, int id, u32 beta, long ntr, u64 seed) {
    Pin p; static Run r; u32 eta; u64 sumper;
    if (!load(file, id, &p, &r, &eta, &sumper)) return 2;
    r.nd = 0;
    for (u32 d1 = 0; d1 < NW; d1++) if (beta_of(&p, d1) == beta) r.dl[r.nd++] = d1;
    u64 rs = seed;
    long f_names = 0, f_half = 0, f_y4 = 0, f_bytes = 0, f_tree = 0;
    long c_names = 0, c_half = 0, c_y4 = 0, c_d1 = 0, c_bytes = 0, c_tree = 0, c_tz = 0, c_wonly = 0, c_n = 0;
    for (long i = 0; i < ntr; i++) {
        r.c0c1 = (u32)splitmix(&rs) & M; r.c0d1 = (u32)splitmix(&rs) & M; r.d3d1 = (u32)splitmix(&rs) & M; r.s15 = (u32)splitmix(&rs) & M;
        u64 g = splitmix(&rs) & ((1ull << (3 * WBITS)) - 1ull);
        u32 k = (u32)(splitmix(&rs) % r.ncls);
        u32 d1 = r.nd ? r.dl[splitmix(&rs) % r.nd] : (u32)splitmix(&rs) & M;
        if (splitmix(&rs) & 1) d1 = (u32)splitmix(&rs) & M;   /* half the checks with any d1 */
        for (int arr = 0; arr < 2; arr++) {
            u32 w[16], wb[16], a[16], b[16], ha[8], hb[8], ya, yb, da, db, t = 0;
            long fail = arr ? ctr_words(&p, &r, g, k, d1, w, &t, 1) : filed_words(&p, &r, g, k, w, 1);
            if (arr && t == 0) { c_tz++; continue; }
            memcpy(wb, w, sizeof wb); wb[4] = p.w4b; wb[5] = (w[5] + p.delta) & M;
            for (int j = 0; j < 16; j++) { a[j] = w[j] & len_mask(j, LEN_A); b[j] = wb[j] & len_mask(j, LEN_B); }
            int cut = 0;
            for (int j = 0; j < 16; j++) cut |= (a[j] != w[j]) | (b[j] != wb[j]);
            const u32 fl = arr ? 3u : FLAGS;
            comp(p.iv, a, LEN_A, t, fl, ha, &ya, &da); comp(p.iv, b, LEN_B, t, fl, hb, &yb, &db);
            int half = ha[0] == hb[0] && ha[2] == hb[2] && ha[5] == hb[5] && ha[7] == hb[7];
            /* tree hash of P||A against the CV path: the last chunk's 8 outputs are what the tree uses */
            u8 fa[BLOCKBYTES];
            words_to_bytes(w, fa);
            u64 pre = (u64)t * CHUNKBYTES;
            u8 *ma = (u8 *)calloc(pre + LEN_A, 1);
            memcpy(ma + pre, fa, LEN_A);
            u32 dig[8], dig2[8];
            tree_hash(ma, pre + LEN_A, dig);
            /* the same digest from the chunk CV: prefix CVs, then parents over (prefix stack, ha) */
            int treeok;
            if (!arr) treeok = !memcmp(dig, ha, sizeof ha);
            else {
                /* replace the last chunk's compression output by ha: tree over t+1 chunks */
                u64 nch = t + 1; static u32 st[64][8]; int sp = 0; Out o;
                for (u64 c = 0; c + 1 < nch; c++) {
                    u32 cv[8];
                    chunk_out(ma + c * CHUNKBYTES, CHUNKBYTES, c, &o); tcomp(o.cv, o.w, o.ctr, o.blen, o.fl, cv);
                    u64 tot = c + 1;
                    while ((tot & 1) == 0) { Out q; sp--; parent_out(st[sp], cv, &q); tcomp(q.cv, q.w, q.ctr, q.blen, q.fl, cv); tot >>= 1; }
                    memcpy(st[sp++], cv, sizeof cv);
                }
                u32 cv[8]; memcpy(cv, ha, sizeof cv);
                sp--; parent_out(st[sp], cv, &o);
                while (sp > 0) { tcomp(o.cv, o.w, o.ctr, o.blen, o.fl, cv); sp--; Out q; parent_out(st[sp], cv, &q); o = q; }
                tcomp(o.cv, o.w, 0, o.blen, o.fl | F_ROOT, dig2);
                treeok = !memcmp(dig, dig2, sizeof dig);
            }
            free(ma);
            if (!arr) { f_names += fail == 0; f_half += half; f_y4 += ya == r.cls[k] && yb == r.cls[k]; f_bytes += !cut; f_tree += treeok; }
            else {
                c_n++; c_names += fail == 0; c_half += half; c_y4 += ya == r.cls[k] && yb == r.cls[k]; c_d1 += da == d1 && db == d1; c_bytes += !cut; c_tree += treeok;
                /* only w0, w1 move with d1: compare with another d1 */
                u32 w2[16], t2; u32 d1b = (d1 + 1 + (u32)(splitmix(&rs) % (NW - 1))) & M;
                ctr_words(&p, &r, g, k, d1b, w2, &t2, 0);
                int wo = w2[0] != w[0];
                for (int j = 2; j < 16; j++) wo = wo && w2[j] == w[j];
                c_wonly += wo;
            }
        }
    }
    printf("CHECK W %d set %d beta %x nd %u trials %ld\n", WBITS, id, beta, r.nd, ntr);
    printf("FILED   : 88 words = forward %ld, half digest equal %ld, Y4 = member %ld, no cut bits %ld, tree hash = root CV %ld (of %ld)\n", f_names, f_half, f_y4,
           f_bytes, f_tree, ntr);
    printf("COUNTER : 88 words = forward (counter t, flags 3) %ld, half digest equal %ld, Y4 = member %ld, E1.d1 = drawn d1 %ld, no cut bits %ld, "
           "tree hash of P||A = tree over (prefix CVs, last-chunk outputs) %ld, only w0 w1 move with d1 %ld (of %ld; t = 0 skipped %ld)\n",
           c_names, c_half, c_y4, c_d1, c_bytes, c_tree, c_wonly, c_n, c_tz);
    int ok = f_names == ntr && f_half == ntr && f_y4 == ntr && f_bytes == ntr && f_tree == ntr && c_names == c_n && c_half == c_n && c_y4 == c_n &&
             c_d1 == c_n && c_bytes == c_n && c_tree == c_n && c_wonly == c_n;
    printf("CHECK %s\n", ok ? "ALL RIGHT" : "FAILED");
    return ok ? 0 : 1;
}

static int cmd_treetest(u64 seed, int n) {
    u64 rs = seed;
    for (int i = 0; i < n; i++) {
        u64 len = splitmix(&rs) % (5 * CHUNKBYTES + 7);
        if (i % 7 == 0) len = (u64)(splitmix(&rs) % 6) * CHUNKBYTES;
        u8 *m = (u8 *)malloc(len + 1);
        for (u64 j = 0; j < len; j++) m[j] = (u8)(splitmix(&rs) & 3u);
        u32 d[8];
        tree_hash(m, len, d);
        printf("TT %llu ", len);
        for (u64 j = 0; j < len; j++) putchar('0' + m[j]);
        printf(" digest");
        for (int j = 0; j < 8; j++) printf(" %x", d[j]);
        printf("\n");
        free(m);
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc >= 4 && !strcmp(argv[1], "mass")) return cmd_mass(argv[2], atoi(argv[3]), argc > 4 ? argv[4] : NULL);
    if (argc >= 7 && !strcmp(argv[1], "check")) return cmd_check(argv[2], atoi(argv[3]), (u32)strtoul(argv[4], NULL, 16), atol(argv[5]), strtoull(argv[6], NULL, 10));
    if (argc >= 9 && !strcmp(argv[1], "run"))
        return cmd_run(argv[2], argv[3], atoi(argv[4]), (u32)strtoul(argv[5], NULL, 16), atol(argv[6]), atol(argv[7]), atoll(argv[8]));
    if (argc >= 4 && !strcmp(argv[1], "treetest")) return cmd_treetest(strtoull(argv[2], NULL, 10), atoi(argv[3]));
    fprintf(stderr, "usage: mass SETS ID [OUT] | check SETS ID BETA NTR SEED | run filed|ctr SETS ID BETA FIRST COUNT NOUTER | treetest SEED N\n");
    return 2;
}
