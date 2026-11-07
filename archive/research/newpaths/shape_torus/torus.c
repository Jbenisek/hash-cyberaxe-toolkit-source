/* Torus (column shift by 2) symmetric families of toy 2-round BLAKE3 (shape_torus, 2026-10-08).
   Toy: word size w, rotations floor(r*w/32) of (16,12,8,7), IV = low w bits of the BLAKE3 IV,
   v12 = v13 = 0, v14 = 64 & mask, v15 = 11 (as in the brief).
   sigma = shift of the 4x4 state by 2 columns: i -> 4*(i/4) + (i%4+2)%4.

   mode 0  self-test: one-round inverse (Sol, answer W 3.3) against the forward round, random X.
   mode 1  random symmetric X: check U4=U6, U5=U7, U8=U10, U9=U11 (claimed automatic) and measure the
           probability of each round-1 symmetry condition c1..c8 (expect 2^-w each).
   mode 2  exact staged enumeration of the families (w <= 10 for the full run):
             fam6 : X symmetric and c1..c6  ->  out0 = out2, out5 = out7      (expected 2^(2w) members)
             fam8 : X symmetric and c1..c8  ->  all four relations             (expected ~1 member)
           every member is checked by the forward 2-round function.
   mode 3  hypothetical symmetric IV (IV2=IV0, IV3=IV1, IV6=IV4, IV7=IV5, v14=v12, v15=v13):
           message constant on the two orbits {0,2,3,4,6,7}, {1,5,8..15}  ->  output symmetric for every
           member; then a birthday on the 4 independent output words over all 2^(2w) members.
   Usage: torus <mode> <w> [samples_log2] [seed]
   Conditions (round-1 symmetry pairs in round-0 message indices):
     c1 m2=m7  c2 m6=m0  c3 m3=m4  c4 m10=m13  c5 m1=m9  c6 m11=m14  c7 m12=m15  c8 m5=m8          */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef uint32_t u32;
static int W, R0, R1, R2, R3;
static u32 MASK;
static u32 IV[8] = {0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au,
                    0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u};
static u32 V0[16];
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
static const int COLS[4][4] = {{0, 4, 8, 12}, {1, 5, 9, 13}, {2, 6, 10, 14}, {3, 7, 11, 15}};
static const int DIAG[4][4] = {{0, 5, 10, 15}, {1, 6, 11, 12}, {2, 7, 8, 13}, {3, 4, 9, 14}};

static inline u32 ror(u32 x, int r) { x &= MASK; return r ? (((x >> r) | (x << (W - r))) & MASK) : x; }
static inline u32 rol(u32 x, int r) { x &= MASK; return r ? (((x << r) | (x >> (W - r))) & MASK) : x; }
static inline u32 ad(u32 a, u32 b) { return (a + b) & MASK; }
static inline u32 sb(u32 a, u32 b) { return (a - b) & MASK; }

static void G(u32 *a, u32 *b, u32 *c, u32 *d, u32 x, u32 y) {
    *a = ad(ad(*a, *b), x); *d = ror(*d ^ *a, R0); *c = ad(*c, *d); *b = ror(*b ^ *c, R1);
    *a = ad(ad(*a, *b), y); *d = ror(*d ^ *a, R2); *c = ad(*c, *d); *b = ror(*b ^ *c, R3);
}

/* full 2-round compression; fills X (after round 0), Y (after round-1 columns), Z (final), out[8] */
static void comp(const u32 *m, u32 *X, u32 *Y, u32 *Z, u32 *out) {
    u32 v[16];
    memcpy(v, V0, sizeof v);
    const int *s;
    int ms[16];
    for (int r = 0; r < 2; r++) {
        for (int i = 0; i < 16; i++) ms[i] = r ? PERM[i] : i;
        for (int j = 0; j < 4; j++) {
            const int *c = COLS[j];
            G(&v[c[0]], &v[c[1]], &v[c[2]], &v[c[3]], m[ms[2 * j]], m[ms[2 * j + 1]]);
        }
        if (r == 1 && Y) memcpy(Y, v, sizeof v);
        for (int j = 0; j < 4; j++) {
            const int *c = DIAG[j];
            G(&v[c[0]], &v[c[1]], &v[c[2]], &v[c[3]], m[ms[8 + 2 * j]], m[ms[9 + 2 * j]]);
        }
        if (r == 0 && X) memcpy(X, v, sizeof v);
    }
    (void)s;
    if (Z) memcpy(Z, v, sizeof v);
    for (int i = 0; i < 8; i++) out[i] = v[i] ^ v[i + 8];
}

/* Sol (4): old b,c of a G call from its outputs */
static void inv_bc(u32 A, u32 B, u32 C, u32 D, u32 *b, u32 *c) {
    u32 s = rol(B, R3) ^ C, r = sb(C, D), q = rol(D, R2) ^ A;
    *b = rol(s, R1) ^ r; *c = sb(r, q);
}
/* Sol (4)+(5): messages from inputs a,b,c,d (b,c consistent) and outputs */
static void inv_xy(u32 a, u32 b, u32 d, u32 A, u32 B, u32 C, u32 D, u32 *x, u32 *y) {
    u32 s = rol(B, R3) ^ C, q = rol(D, R2) ^ A;
    u32 p = rol(q, R0) ^ d;
    *x = sb(sb(p, a), b); *y = sb(sb(A, p), s);
}
/* Sol (3): from input (a,b,c,d) and target final (B,C): messages and final A,D */
static void col_bc(u32 a, u32 b, u32 c, u32 d, u32 B, u32 C, u32 *x, u32 *y, u32 *A, u32 *D) {
    u32 s = rol(B, R3) ^ C, r = rol(s, R1) ^ b, q = sb(r, c);
    *D = sb(C, r);
    u32 p = rol(q, R0) ^ d;
    *A = rol(*D, R2) ^ q;
    *x = sb(sb(p, a), b); *y = sb(sb(*A, p), s);
}
/* fiber of inv_bc: quartet with old (b,c) and free (C,D) */
static void fiber(u32 b, u32 c, u32 C, u32 D, u32 *q4) {
    u32 r = sb(C, D), s = ror(b ^ r, R1), q = sb(r, c);
    u32 B = ror(s ^ C, R3), A = q ^ rol(D, R2);
    q4[0] = A; q4[1] = B; q4[2] = C; q4[3] = D;
}

/* one-round inverse: X -> m (Sol 3.3) */
static void round_inv(const u32 *X, u32 *m) {
    u32 U[16];
    for (int j = 0; j < 4; j++) {
        const int *d = DIAG[j];
        inv_bc(X[d[0]], X[d[1]], X[d[2]], X[d[3]], &U[d[1]], &U[d[2]]);
    }
    for (int j = 0; j < 4; j++) {
        const int *c = COLS[j];
        col_bc(V0[c[0]], V0[c[1]], V0[c[2]], V0[c[3]], U[c[1]], U[c[2]], &m[2 * j], &m[2 * j + 1], &U[c[0]], &U[c[3]]);
    }
    for (int j = 0; j < 4; j++) {
        const int *d = DIAG[j];
        inv_xy(U[d[0]], U[d[1]], U[d[3]], X[d[0]], X[d[1]], X[d[2]], X[d[3]], &m[8 + 2 * j], &m[9 + 2 * j]);
    }
}

static uint64_t rs = 88172645463325252ull;
static inline u32 rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (u32)(rs >> 11) & MASK; }
static inline int sig(int i) { return 4 * (i / 4) + (i % 4 + 2) % 4; }

static const int CP[8][2] = {{2, 7}, {6, 0}, {3, 4}, {10, 13}, {1, 9}, {11, 14}, {12, 15}, {5, 8}};

static int IVOFF = 0;   /* toy IV = bits IVOFF.. of the real IV (0 = low w bits, the default) */
static void setup(int w, int symiv) {
    W = w; MASK = (w == 32) ? 0xffffffffu : ((1u << w) - 1);
    R0 = 16 * w / 32; R1 = 12 * w / 32; R2 = 8 * w / 32; R3 = 7 * w / 32;
    for (int i = 0; i < 8; i++) V0[i] = (IV[i] >> IVOFF) & MASK;
    for (int i = 0; i < 4; i++) V0[8 + i] = (IV[i] >> IVOFF) & MASK;
    V0[12] = 0; V0[13] = 0; V0[14] = 64 & MASK; V0[15] = 11 & MASK;
    if (symiv) {
        V0[2] = V0[0]; V0[3] = V0[1]; V0[6] = V0[4]; V0[7] = V0[5];
        V0[10] = V0[8]; V0[11] = V0[9]; V0[14] = V0[12]; V0[15] = V0[13];
    }
}

static int check_member(const u32 *m, int full) {
    u32 X[16], Y[16], Z[16], out[8];
    comp(m, X, Y, Z, out);
    for (int i = 0; i < 16; i++) if (X[i] != X[sig(i)]) return -1;
    int ok = (out[0] == out[2]) && (out[5] == out[7]);
    if (full) ok = ok && (out[1] == out[3]) && (out[4] == out[6]);
    return ok;
}

int main(int argc, char **argv) {
    int mode = atoi(argv[1]), w = atoi(argv[2]);
    int lg = argc > 3 ? atoi(argv[3]) : 20;
    if (argc > 4) rs ^= (uint64_t)atoll(argv[4]) * 0x9E3779B97F4A7C15ull;
    if (argc > 4 && mode == 2) IVOFF = atoi(argv[4]);
    setup(w, mode == 3);
    if (mode == 0) {
        long bad = 0;
        for (long t = 0; t < (1L << lg); t++) {
            u32 X[16], m[16], X2[16], out[8];
            for (int i = 0; i < 16; i++) X[i] = rnd();
            round_inv(X, m);
            comp(m, X2, NULL, NULL, out);
            bad += memcmp(X, X2, sizeof X) != 0;
        }
        printf("w=%d rot=(%d,%d,%d,%d): round-0 inverse self-test, %ld samples, mismatches %ld\n", w, R0, R1, R2, R3, 1L << lg, bad);
        return 0;
    }
    if (mode == 1) {
        long usym_bad = 0, hit[8] = {0}, n = 1L << lg, both12 = 0, outrel = 0;
        for (long t = 0; t < n; t++) {
            u32 X[16], m[16], U[16];
            for (int i = 0; i < 16; i++) if (sig(i) > i) { X[i] = rnd(); X[sig(i)] = X[i]; }
            round_inv(X, m);
            for (int j = 0; j < 4; j++) { const int *d = DIAG[j]; inv_bc(X[d[0]], X[d[1]], X[d[2]], X[d[3]], &U[d[1]], &U[d[2]]); }
            if (U[4] != U[6] || U[5] != U[7] || U[8] != U[10] || U[9] != U[11]) usym_bad++;
            for (int k = 0; k < 8; k++) hit[k] += m[CP[k][0]] == m[CP[k][1]];
            both12 += (m[2] == m[7]) && (m[6] == m[0]);
            u32 out[8]; comp(m, NULL, NULL, NULL, out);
            outrel += (out[0] == out[2]);
        }
        printf("w=%d: %ld random symmetric X; U-symmetry violations %ld\n", w, n, usym_bad);
        for (int k = 0; k < 8; k++)
            printf("  c%d m%d=m%d: rate %.3e  (2^-w = %.3e)\n", k + 1, CP[k][0], CP[k][1], (double)hit[k] / n, 1.0 / (1u << w));
        printf("  c1&c2 joint rate %.3e (2^-2w = %.3e); out0=out2 rate %.3e\n", (double)both12 / n,
               1.0 / ((double)(1u << w) * (1u << w)), (double)outrel / n);
        return 0;
    }
    if (mode == 2) {
        /* stage 1: (R,S) -> K1, K3 ; (P,Q) -> K0, K2 */
        long N = 1L << (2 * w);
        u32 *pq_key = malloc(sizeof(u32) * N);    /* key m0|m4 */
        for (long z = 0; z < N; z++) {
            u32 P = z & MASK, Q = (z >> w) & MASK, x0, y0, x2, y2, A, D;
            col_bc(V0[0], V0[4], V0[8], V0[12], P, Q, &x0, &y0, &A, &D);
            col_bc(V0[2], V0[6], V0[10], V0[14], P, Q, &x2, &y2, &A, &D);
            pq_key[z] = x0 | (x2 << w);
        }
        /* bucket (P,Q) by key: counting sort */
        long K = 1L << (2 * w);
        u32 *cnt = calloc(K + 1, sizeof(u32));
        for (long z = 0; z < N; z++) cnt[pq_key[z] + 1]++;
        for (long k = 0; k < K; k++) cnt[k + 1] += cnt[k];
        u32 *ord = malloc(sizeof(u32) * N);
        u32 *pos = malloc(sizeof(u32) * (K + 1));
        memcpy(pos, cnt, sizeof(u32) * (K + 1));
        for (long z = 0; z < N; z++) ord[pos[pq_key[z]]++] = (u32)z;
        long c7n = 0, c8n = 0, rs_hit = 0, s1 = 0, rs_c1 = 0, fam6 = 0, fam8 = 0, bad6 = 0, bad8 = 0, sym_extra = 0;
        long stage2_lim = (argc > 3 && atoi(argv[3]) >= 0) ? (1L << atoi(argv[3])) : -1;
        long Nq = 1L << (2 * w), cap = 1L << (w + 6), overflow = 0;
        u32 *q0m = malloc(sizeof(u32) * 4 * cap), *q1m = malloc(sizeof(u32) * 4 * cap);
        for (long z = 0; z < N; z++) {
            u32 R = z & MASK, S = (z >> w) & MASK, x1, y1, x3, y3, A1, D1, A3, D3;
            col_bc(V0[1], V0[5], V0[9], V0[13], R, S, &x1, &y1, &A1, &D1);
            col_bc(V0[3], V0[7], V0[11], V0[15], R, S, &x3, &y3, &A3, &D3);
            if (x1 != y3) continue;                 /* c1: m2 = m7 */
            rs_c1++;
            u32 key = x3 | (y1 << w);               /* need m0 = m6 (=x3) and m4 = m3 (=y1) */
            rs_hit += cnt[key + 1] > cnt[key];
            for (u32 k = cnt[key]; k < cnt[key + 1]; k++) {
                u32 zz = ord[k], P = zz & MASK, Q = (zz >> w) & MASK;
                u32 m[16];
                u32 A0, D0, A2, D2;
                m[2] = x1; m[3] = y1; m[6] = x3; m[7] = y3;
                col_bc(V0[0], V0[4], V0[8], V0[12], P, Q, &m[0], &m[1], &A0, &D0);
                col_bc(V0[2], V0[6], V0[10], V0[14], P, Q, &m[4], &m[5], &A2, &D2);
                s1++;
                if (stage2_lim >= 0 && s1 > stage2_lim) continue;
                /* stage 2: Q0 in fiber(R,Q) ; D0 input (A0,R,Q,D3), D2 input (A2,R,Q,D1) */
                long n0 = 0, n1 = 0;
                for (long c = 0; c < Nq; c++) {
                    u32 q4[4], x8, y9, x12, y13;
                    fiber(R, Q, c & MASK, (c >> w) & MASK, q4);
                    inv_xy(A0, R, D3, q4[0], q4[1], q4[2], q4[3], &x8, &y9);
                    if (y9 != m[1]) continue;       /* c5 */
                    if (n0 >= cap) { overflow++; continue; }
                    inv_xy(A2, R, D1, q4[0], q4[1], q4[2], q4[3], &x12, &y13);
                    q0m[4 * n0] = (u32)c; q0m[4 * n0 + 1] = x8; q0m[4 * n0 + 2] = x12; q0m[4 * n0 + 3] = y13;
                    n0++;
                }
                for (long c = 0; c < Nq; c++) {
                    u32 q4[4], x10, y11, x14, y15;
                    fiber(P, S, c & MASK, (c >> w) & MASK, q4);
                    inv_xy(A1, P, D0, q4[0], q4[1], q4[2], q4[3], &x10, &y11);
                    inv_xy(A3, P, D2, q4[0], q4[1], q4[2], q4[3], &x14, &y15);
                    if (y11 != x14) continue;       /* c6 */
                    if (n1 >= cap) { overflow++; continue; }
                    q1m[4 * n1] = (u32)c; q1m[4 * n1 + 1] = x10; q1m[4 * n1 + 2] = y11; q1m[4 * n1 + 3] = y15;
                    n1++;
                }
                for (long i = 0; i < n0; i++)
                    for (long j = 0; j < n1; j++) {
                        if (q1m[4 * j + 1] != q0m[4 * i + 3]) continue;   /* c4: m10 = m13 */
                        m[8] = q0m[4 * i + 1]; m[12] = q0m[4 * i + 2]; m[13] = q0m[4 * i + 3]; m[9] = m[1];
                        m[10] = q1m[4 * j + 1]; m[11] = q1m[4 * j + 2]; m[14] = m[11]; m[15] = q1m[4 * j + 3];
                        fam6++;
                        int r6 = check_member(m, 0);
                        if (r6 != 1) bad6++;
                        u32 out[8]; comp(m, NULL, NULL, NULL, out);
                        sym_extra += (out[1] == out[3]);
                        c7n += m[12] == m[15]; c8n += m[5] == m[8];
                        if (m[12] == m[15] && m[5] == m[8]) {
                            fam8++;
                            if (check_member(m, 1) != 1) bad8++;
                            printf("  fam8 member:");
                            for (int t = 0; t < 16; t++) printf(" %x", m[t]);
                            printf("\n");
                        }
                    }
            }
        }
        printf("w=%d ivoff=%d: stage 1 (c1,c2,c3): (R,S) passing c1 = %ld (expect 2^%d); (R,S) hitting the (m0,m4) curve = %ld (mean 1); solutions = %ld (mean 2^%d)\n",
               w, IVOFF, rs_c1, w, rs_hit, s1, w);
        printf("  among fam6: c7 (m12=m15) holds %ld, c8 (m5=m8) holds %ld (expect fam6*2^-%d each)\n", c7n, c8n, w);
        if (stage2_lim >= 0) printf("  stage 2 run on the first %ld stage-1 solutions only\n", stage2_lim);
        printf("  fam6 members (c1..c6) = %ld (expect 2^%d per full run); forward-check failures %ld; of them out1=out3 by chance %ld\n",
               fam6, 2 * w, bad6, sym_extra);
        printf("  fam8 members (c1..c8) = %ld (expect ~1); forward-check failures %ld\n", fam8, bad8);
        return 0;
    }
    if (mode == 4) {
        /* fast fully-symmetric (fam8) search, O(1) per stage-1 solution:
           K0,K2 share final (b,c) = (P,Q), hence share s = ROL7(P)^Q (their b1), and m0, m4 depend on s only.
           c5,c8 fix (m8,m9) = (m5,m1): Q0 = G(A0,R,Q,D3; m5,m1) forward; D2 gives (m12,m13) by inversion.
           c4 fixes m10 = m13; c6 (m14 = m11) is then solved through T1 = ROL16(q) of Q1; remaining test:
           D3's y equals m12 (c7).  Parity claim: needs sum of IV0..IV7 even (bit 0).
           argv[4]: IV offset (>=0) or negative = random IV with that seed. */
        int ivarg = argc > 4 ? atoi(argv[4]) : 0;
        if (ivarg < 0) {
            uint64_t z = (uint64_t)(-ivarg) * 0x9E3779B97F4A7C15ull + 12345;
            for (int i = 0; i < 8; i++) { z ^= z << 13; z ^= z >> 7; z ^= z << 17; IV[i] = (u32)(z >> 20); }
            IVOFF = 0;
        } else IVOFF = ivarg;
        setup(w, 0);
        int par = 0;
        for (int i = 0; i < 8; i++) par ^= V0[i] & 1;
        long S = 1L << w;
        /* table over s: key (m0,m4) -> list of s */
        u32 *key = malloc(sizeof(u32) * S);
        for (long s = 0; s < S; s++) {
            u32 P = 0, Q = (u32)s;  /* ROL7(0)^Q = s: any (P,Q) on the curve gives the same m0,m4 */
            u32 x0, y0, x2, y2, A, D;
            col_bc(V0[0], V0[4], V0[8], V0[12], P, Q, &x0, &y0, &A, &D);
            col_bc(V0[2], V0[6], V0[10], V0[14], P, Q, &x2, &y2, &A, &D);
            key[s] = x0 | (x2 << w);
        }
        long hits = 0, s1 = 0, fam8 = 0, bad = 0, hits_with = 0;
        for (long z = 0; z < S * S; z++) {
            u32 R = z & MASK, Sx = (z >> w) & MASK, m[16], A1, D1, A3, D3;
            col_bc(V0[1], V0[5], V0[9], V0[13], R, Sx, &m[2], &m[3], &A1, &D1);
            col_bc(V0[3], V0[7], V0[11], V0[15], R, Sx, &m[6], &m[7], &A3, &D3);
            if (m[2] != m[7]) continue;
            u32 want = m[6] | (m[3] << w);
            for (long s = 0; s < S; s++) {
                if (key[s] != want) continue;
                hits++;
                long f_this = 0;
                for (long P = 0; P < S; P++) {
                    u32 Q = rol((u32)P, R3) ^ (u32)s, A0, D0, A2, D2;
                    col_bc(V0[0], V0[4], V0[8], V0[12], (u32)P, Q, &m[0], &m[1], &A0, &D0);
                    col_bc(V0[2], V0[6], V0[10], V0[14], (u32)P, Q, &m[4], &m[5], &A2, &D2);
                    s1++;
                    u32 a = A0, b = R, c = Q, d = D3;
                    m[8] = m[5]; m[9] = m[1];
                    G(&a, &b, &c, &d, m[8], m[9]);          /* Q0 */
                    inv_xy(A2, R, D1, a, b, c, d, &m[12], &m[13]);
                    m[10] = m[13];
                    u32 gam = ad(ad(m[10], A1), (u32)P), T1 = gam ^ D0, del = T1 ^ D2;
                    m[14] = sb(sb(del, A3), (u32)P);
                    m[11] = m[14];
                    u32 a1 = A1, b1 = (u32)P, c1 = Sx, d1 = D0;
                    G(&a1, &b1, &c1, &d1, m[10], m[11]);    /* Q1 */
                    u32 x14, y15;
                    inv_xy(A3, (u32)P, D2, a1, b1, c1, d1, &x14, &y15);
                    if (x14 != m[14]) bad++;
                    if (y15 != m[12]) continue;
                    m[15] = y15;
                    fam8++; f_this++;
                    if (check_member(m, 1) != 1) bad++;
                }
                hits_with += f_this > 0;
                if (f_this) printf("  curve hit R=%x S=%x s=%lx: fam8 members on this curve %ld of 2^%d\n", R, Sx, s, f_this, w);
            }
        }
        printf("w=%d iv=%d parity(IV0..7 bit0)=%d: curve hits %ld, stage-1 solutions %ld, fam8 members %ld (hits with members %ld), "
               "construction/forward failures %ld\n", w, ivarg, par, hits, s1, fam8, hits_with, bad);
        return 0;
    }
    if (mode == 3) {
        long N = 1L << (2 * w), bad = 0;
        u32 *key = malloc(sizeof(u32) * 2 * N);
        int okall = 1;
        for (long z = 0; z < N; z++) {
            u32 a = z & MASK, b = (z >> w) & MASK, m[16], out[8];
            for (int i = 0; i < 16; i++) m[i] = b;
            m[0] = m[2] = m[3] = m[4] = m[6] = m[7] = a;
            comp(m, NULL, NULL, NULL, out);
            if (out[0] != out[2] || out[1] != out[3] || out[4] != out[6] || out[5] != out[7]) { bad++; okall = 0; }
            /* 4 independent words, 4w bits: hash to 64 bits for the birthday count */
            uint64_t h = 0;
            h = ((uint64_t)out[0] << (3 * w)) | ((uint64_t)out[1] << (2 * w)) | ((uint64_t)out[4] << w) | out[5];
            key[2 * z] = (u32)h; key[2 * z + 1] = (u32)(h >> 32);
        }
        /* count colliding pairs by sorting */
        uint64_t *hv = malloc(sizeof(uint64_t) * N);
        for (long z = 0; z < N; z++) hv[z] = ((uint64_t)key[2 * z + 1] << 32) | key[2 * z];
        int cmp(const void *x, const void *y) { uint64_t a = *(const uint64_t *)x, b = *(const uint64_t *)y; return a < b ? -1 : a > b; }
        qsort(hv, N, sizeof(uint64_t), cmp);
        long pairs = 0;
        for (long z = 1; z < N; z++) if (hv[z] == hv[z - 1]) pairs++;
        printf("w=%d symmetric-IV hypothetical: 2^%d two-orbit messages, symmetry violations %ld (%s); "
               "full-digest collisions found %ld (expect ~2^(4w-1)/2^(4w) = 0.5)\n", w, 2 * w, bad, okall ? "all symmetric" : "NOT", pairs);
        return 0;
    }
    return 0;
}
