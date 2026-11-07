/* feat.c: features of toy trials (found collisions and random null trials) for the collision-pattern study.
 * Research only. Uses the runs' own construction: task5_small_h8 toy.h + tl_lines.inc (included read-only),
 * the trial of small_h8.cu (filed: counter 0, flags 11) and of counter/toy/ctr_toy.c (ctr: flags 3, counter t,
 * inner word E1.d1 -> w0, w1, t).
 * build (WSL): g++ -O2 -x c++ -DWBITS=8 -I<task5 dir> -o feat8 feat.c
 * stdin lines:
 *   H tag mode set c0c1 c0d1 d3d1 s15 g k d1     one given trial (mode 0 filed, 1 ctr; d1 used in ctr only)
 *   N tag mode set c0c1 c0d1 d3d1 s15 nmid beta R wflag rngseed
 *       R random trials of that run: g uniform in [0,nmid), k uniform, (ctr) d1 uniform in the d1 set of beta
 *       (beta > M: all d1) and t != 0 (the run's own filter). wflag 1: accept with prob mass[k][d1]/max (needs
 *       massmat file of the set), i.e. the exact model's collision weight.
 * stdout: tag mode set g k y4 d1 t fail coll w0..w15 Y1 Y6 Y9 Y12 Y14 b1 a2 e1 h1 mass
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "toy.h"
#include "tl_lines.inc"

struct Run { u32 c0c1, c0d1, d3d1, s15, ncls; u32 cls[MAXCLS]; };
static Pin pins[64]; static u32 ncls[64], cls[64][MAXCLS]; static int have[64];
static u64 *mass[64]; static u64 mmax[64];

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

static long filed_words(const Pin *p, const Run *r, u64 g, u32 k, u32 *w) {
    PRE(p, r, g, FLAGS)
    TL_OUTER
    TL_MIDDLE
    const u32 Y4 = r->cls[k];
    TL_MEMBER
    TL_TRIAL
    TL_WORDS(w)
    long fail = 0;
    { TL_FWD(w) TL_CMP(fail) }
    return fail;
}
static long ctr_words(const Pin *p, const Run *r, u64 g, u32 k, u32 d1, u32 *w, u32 *tout) {
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
    {
        const u32 CTR0 = tt, K0_a1 = nK0a, Y6 = nY6, Y10 = nY10, Y14 = nY14, Y2 = nY2;
        TL_FWD(w) TL_CMP(fail)
        (void)CTR0;
    }
    return fail;
}

/* 2-round compression (counter ctr < 2^W) with the internal words of round 2 captured */
typedef struct { u32 Y1, Y4, Y6, Y9, Y12, Y14, d1, b1, a2, e1, h1; } Cap;
static void comp(const u32 *iv, const u32 *m, u32 len, u32 ctr, u32 fl, u32 *out, Cap *c) {
    u32 v0 = iv[0], v1 = iv[1], v2 = iv[2], v3 = iv[3], v4 = iv[4], v5 = iv[5], v6 = iv[6], v7 = iv[7];
    u32 v8 = iv[0], v9 = iv[1], v10 = iv[2], v11 = iv[3], v12 = ctr & M, v13 = 0, v14 = len & M, v15 = fl & M;
    GF(v0, v4, v8, v12, m[0], m[1]);   GF(v1, v5, v9, v13, m[2], m[3]);
    GF(v2, v6, v10, v14, m[4], m[5]);  GF(v3, v7, v11, v15, m[6], m[7]);
    GF(v0, v5, v10, v15, m[8], m[9]);  GF(v1, v6, v11, v12, m[10], m[11]);
    GF(v2, v7, v8, v13, m[12], m[13]); GF(v3, v4, v9, v14, m[14], m[15]);
    GF(v0, v4, v8, v12, m[2], m[6]);
    GF(v1, v5, v9, v13, m[3], m[10]);
    GF(v2, v6, v10, v14, m[7], m[0]);  GF(v3, v7, v11, v15, m[4], m[13]);
    c->Y1 = v1; c->Y4 = v4; c->Y6 = v6; c->Y9 = v9; c->Y12 = v12; c->Y14 = v14;
    GF(v0, v5, v10, v15, m[1], m[11]);
    /* E1 = G(v1, v6, v11, v12; m12, m5) */
    v1 = (v1 + v6 + m[12]) & M; v12 = ror(v12 ^ v1, ROT1); c->d1 = v12; v11 = (v11 + v12) & M; v6 = ror(v6 ^ v11, ROT2); c->b1 = v6;
    v1 = (v1 + v6 + m[5]) & M;  c->a2 = v1; v12 = ror(v12 ^ v1, ROT3); v11 = (v11 + v12) & M; v6 = ror(v6 ^ v11, ROT4);
    GF(v2, v7, v8, v13, m[9], m[14]);
    /* E3 = G(v3, v4, v9, v14; m15, m8) */
    v3 = (v3 + v4 + m[15]) & M; c->e1 = v3; v14 = ror(v14 ^ v3, ROT1); c->h1 = v14; v9 = (v9 + v14) & M; v4 = ror(v4 ^ v9, ROT2);
    v3 = (v3 + v4 + m[8]) & M;  v14 = ror(v14 ^ v3, ROT3); v9 = (v9 + v14) & M; v4 = ror(v4 ^ v9, ROT4);
    out[0] = v0 ^ v8;  out[1] = v1 ^ v9;  out[2] = v2 ^ v10; out[3] = v3 ^ v11;
    out[4] = v4 ^ v12; out[5] = v5 ^ v13; out[6] = v6 ^ v14; out[7] = v7 ^ v15;
}

static inline u32 beta_of(const Pin *p, u32 d1) { return ror(((p->y11 + d1) ^ (p->y11b + d1)) & M, ROT2); }

static int load_sets(const char *file, const char *massdir) {
    FILE *f = fopen(file, "r");
    if (!f) return 0;
    char line[512];
    while (fgets(line, sizeof line, f)) {
        int w, id; u32 x3, x7, x11, x15, w4, w13, eta, n; unsigned long long sp; double a, b;
        if (sscanf(line, "SET %d %d %x %x %x %x %x %x %x %u %llu %lf %lf", &w, &id, &x3, &x7, &x11, &x15, &w4, &w13, &eta, &n, &sp, &a, &b) != 13) continue;
        if (w != WBITS || id < 0 || id >= 64) continue;
        Pin *p = &pins[id];
        p->x3 = x3; p->x7 = x7; p->x11 = x11; p->x15 = x15; p->w4 = w4; p->w13 = w13;
        if (!fill_pin(p)) { fprintf(stderr, "set %d not a pin\n", id); return 0; }
        ncls[id] = class_members(p, eta, cls[id]);
        if (ncls[id] != n) { fprintf(stderr, "class mismatch set %d\n", id); return 0; }
        have[id] = 1;
        if (massdir && massdir[0] != '-') {
            char fn[1024];
            snprintf(fn, sizeof fn, "%s/massmat_set%d.txt", massdir, id);
            FILE *g = fopen(fn, "r");
            if (g) {
                mass[id] = (u64 *)calloc((size_t)n << WBITS, sizeof(u64));
                char *buf = (char *)malloc(1 << 16);
                while (fgets(buf, 1 << 16, g)) {
                    if (buf[0] == '#') continue;
                    char *s = buf; u32 k = (u32)strtoul(s, &s, 10); strtoul(s, &s, 16);
                    for (u32 d = 0; d <= M; d++) { u64 v = strtoull(s, &s, 10); mass[id][(k << WBITS) | d] = v; if (v > mmax[id]) mmax[id] = v; }
                }
                free(buf); fclose(g);
            }
        }
    }
    fclose(f);
    return 1;
}

static void emit(const char *tag, int mode, int id, const Run *r, u64 g, u32 k, u32 d1in) {
    const Pin *p = &pins[id];
    u32 w[16], t = 0;
    long fail = mode ? ctr_words(p, r, g, k, d1in, w, &t) : filed_words(p, r, g, k, w);
    u32 a[16], b[16], wb[16], ha[8], hb[8];
    memcpy(wb, w, sizeof wb); wb[4] = p->w4b; wb[5] = (w[5] + p->delta) & M;
    int cut = 0;
    for (int j = 0; j < 16; j++) { a[j] = w[j] & len_mask(j, LEN_A); b[j] = wb[j] & len_mask(j, LEN_B); cut |= (a[j] != w[j]) | (b[j] != wb[j]); }
    Cap ca, cb;
    const u32 fl = mode ? 3u : FLAGS;
    comp(p->iv, a, LEN_A, t, fl, ha, &ca);
    comp(p->iv, b, LEN_B, t, fl, hb, &cb);
    int coll = !memcmp(ha, hb, sizeof ha);
    fail += cut + (ca.Y4 != r->cls[k]) + (cb.Y4 != r->cls[k]) + (mode && ca.d1 != d1in);
    long long ms = mass[id] ? (long long)mass[id][(k << WBITS) | ca.d1] : -1;
    printf("%s %d %d %llu %u %u %u %u %ld %d", tag, mode, id, g, k, r->cls[k], ca.d1, t, fail, coll);
    for (int j = 0; j < 16; j++) printf(" %u", w[j]);
    printf(" %u %u %u %u %u %u %u %u %u %lld\n", ca.Y1, ca.Y6, ca.Y9, ca.Y12, ca.Y14, ca.b1, ca.a2, ca.e1, ca.h1, ms);
}

/* exact model, E3 side given: number of (h1, Y9, b1, a2) out of 2^(4W) that make trial (set, member k, E1.d1, w8)
   collide (formulas of ctr_toy.c cmd_mass); P(coll | k, d1, w8) = count / 2^(4W) */
static u32 *T3; static u32 used3[1u << 16];
static unsigned long long p3(int id, u32 k, u32 d1, u32 w8) {
    const Pin *p = &pins[id];
    if (!T3) T3 = (u32 *)calloc((size_t)1 << (3 * WBITS), sizeof(u32));
    const u32 Y4 = cls[id][k], e1 = (p->y3 + Y4) & M, e1b = (p->y3b + Y4) & M;
    u32 nset = 0;
    for (u32 h1 = 0; h1 <= M; h1++) {
        const u32 Y14 = rol(h1, ROT1) ^ e1, h1b = ror(Y14 ^ e1b, ROT1);
        for (u32 Y9 = 0; Y9 <= M; Y9++) {
            const u32 g1 = (Y9 + h1) & M, f1 = ror(Y4 ^ g1, ROT2), g1b = (Y9 + h1b) & M, f1b = ror(Y4 ^ g1b, ROT2);
            u32 e2 = (e1 + f1 + w8) & M, h2 = ror(h1 ^ e2, ROT3), g2 = (g1 + h2) & M, f2 = ror(f1 ^ g2, ROT4);
            u32 e2b = (e1b + f1b + w8) & M, h2b = ror(h1b ^ e2b, ROT3), g2b = (g1b + h2b) & M, f2b = ror(f1b ^ g2b, ROT4);
            u32 dA = e2 ^ e2b, dB = f2 ^ f2b, dC = g2 ^ g2b, dD = h2 ^ h2b;
            if (dB != ror(dC, ROT3)) continue;
            u32 key = (dC << (2 * WBITS)) | (dA << WBITS) | dD;
            if (T3[key] == 0 && nset < (1u << 16)) used3[nset++] = key;
            T3[key]++;
        }
    }
    unsigned long long s = 0;
    for (u32 b1 = 0; b1 <= M; b1++)
        for (u32 a2 = 0; a2 <= M; a2++) {
            u32 c1 = (p->y11 + d1) & M, c1b = (p->y11b + d1) & M, Y6 = rol(b1, ROT2) ^ c1;
            u32 b1b = ror(Y6 ^ c1b, ROT2), a2b = (a2 - b1 + b1b + p->delta) & M;
            u32 d2 = ror(d1 ^ a2, ROT3), c2 = (c1 + d2) & M, b2 = ror(b1 ^ c2, ROT4);
            u32 d2b = ror(d1 ^ a2b, ROT3), c2b = (c1b + d2b) & M, b2b = ror(b1b ^ c2b, ROT4);
            u32 da = a2 ^ a2b, db = b2 ^ b2b, dc = c2 ^ c2b;
            s += T3[(da << (2 * WBITS)) | (dc << WBITS) | db];
        }
    for (u32 i = 0; i < nset; i++) T3[used3[i]] = 0;
    return s;
}

int main(int argc, char **argv) {
    if (argc < 2 || !load_sets(argv[1], argc > 2 ? argv[2] : NULL)) { fprintf(stderr, "usage: feat SETS [MASSDIR] < lines\n"); return 2; }
    char line[1024];
    while (fgets(line, sizeof line, stdin)) {
        char kind[4], tag[128]; int mode, id; Run r;
        if (sscanf(line, "%3s %127s %d %d", kind, tag, &mode, &id) != 4 || id < 0 || id >= 64 || !have[id]) continue;
        r.ncls = ncls[id]; memcpy(r.cls, cls[id], sizeof r.cls);
        if (kind[0] == 'P') {   /* P tag mode set k d1 w8 */
            u32 k, d1, w8;
            if (sscanf(line, "%*s %*s %*d %*d %u %u %u", &k, &d1, &w8) != 3 || k >= ncls[id]) continue;
            printf("%s %llu\n", tag, p3(id, k, d1 & M, w8 & M));
            continue;
        }
        if (kind[0] == 'H') {
            unsigned long long g; u32 k, d1;
            if (sscanf(line, "%*s %*s %*d %*d %u %u %u %u %llu %u %u", &r.c0c1, &r.c0d1, &r.d3d1, &r.s15, &g, &k, &d1) != 7) continue;
            emit(tag, mode, id, &r, g, k, d1);
        } else {
            unsigned long long nmid, rs; u32 beta, R, wf;
            if (sscanf(line, "%*s %*s %*d %*d %u %u %u %u %llu %u %u %u %llu", &r.c0c1, &r.c0d1, &r.d3d1, &r.s15, &nmid, &beta, &R, &wf, &rs) != 9) continue;
            if (wf && !mass[id]) { fprintf(stderr, "no mass table for set %d\n", id); return 3; }
            u32 dl[1 << WBITS], nd = 0;
            for (u32 d = 0; d <= M; d++) if (beta > M || beta_of(&pins[id], d) == beta) dl[nd++] = d;
            u64 s = rs;
            for (u32 got = 0; got < R;) {
                u64 g = splitmix(&s) % nmid; u32 k = (u32)(splitmix(&s) % r.ncls); u32 d1 = mode ? dl[splitmix(&s) % nd] : 0;
                u32 w[16], t = 0;
                if (mode) { ctr_words(&pins[id], &r, g, k, d1, w, &t); if (t == 0) continue; }
                if (wf) {
                    u32 dd = d1;
                    if (!mode) { u32 a[16], ha[8]; Cap c; filed_words(&pins[id], &r, g, k, w);
                                 for (int j = 0; j < 16; j++) a[j] = w[j] & len_mask(j, LEN_A);
                                 comp(pins[id].iv, a, LEN_A, 0, FLAGS, ha, &c); dd = c.d1; }
                    u64 m = mass[id][(k << WBITS) | dd];
                    double u = (double)(splitmix(&s) >> 11) * (1.0 / 9007199254740992.0);
                    if (u * (double)mmax[id] >= (double)m) continue;
                }
                emit(tag, mode, id, &r, g, k, d1);
                got++;
            }
        }
    }
    return 0;
}
