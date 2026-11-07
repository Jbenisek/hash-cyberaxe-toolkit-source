/* toy.h: the scaled-down hash of task 5 and the scaled-down NEW length family. Research, not submitted.
 *
 * THE HASH. BLAKE3 with 2 rounds and W-bit words, W = 8, 10 or 12 (as in the scaled-down runs of the filed
 * proof, Section 10, and in research/r2_toy_gpu.cu): IV words = the top W bits of the real IV words, the same
 * permutation, flags 11, counter 0, and the rotations (W/2, (3W+4)/8, (W+2)/4, (W+2)/4 - 1), that is
 * (4,3,2,1), (5,4,3,2), (6,5,3,2). New here: messages are BYTE STRINGS. A toy byte has 2 bits; a word is W/2
 * toy bytes, lowest first; a block is 16 words = 8W toy bytes; the block length (the number of toy bytes of the
 * message) goes into v[14] exactly as in BLAKE3, and the bytes after the end of the message are zero.
 *
 * THE FAMILY (analogue of 55 and 63 bytes, XOR 8). Message A has LEN_A = 7W - 1 toy bytes and message B has
 * LEN_B = 7W + 7: 55/63 for W = 8, 69/77 for W = 10, 83/91 for W = 12. LEN_A XOR LEN_B = 8 = 2^3 for all three.
 * LEN_A ends one toy byte before the end of w13, so both messages have w14 = w15 = 0 and the top toy byte (top
 * two bits) of w13 = 0, as the real family has w14 = w15 = 0 and the top byte of w13 = 0.
 * The pinned call needs a run of at least W/2 + 1 - 3 bits from bit 3: 2, 3, 4 of the 5, 7, 9 bits there are.
 */
#ifndef TOY_H
#define TOY_H
#include <stdint.h>
#include <string.h>

typedef uint32_t u32;
typedef unsigned long long u64;
typedef unsigned char u8;

#ifdef __CUDACC__
#define HD __host__ __device__
#else
#define HD
#endif

#ifndef WBITS
#define WBITS 8
#endif
#if WBITS != 8 && WBITS != 10 && WBITS != 12
#error "WBITS must be 8, 10 or 12"
#endif
#define M ((1u << WBITS) - 1u)
#define ROT1 (WBITS / 2)
#define ROT2 ((3 * WBITS + 4) / 8)
#define ROT3 ((WBITS + 2) / 4)
#define ROT4 (ROT3 - 1)
#define WBYTES (WBITS / 2)                 /* toy bytes per word */
#define BLOCKBYTES (16 * WBYTES)           /* toy bytes per block */
#define LEN_A (7u * WBITS - 1u)
#define LEN_B (7u * WBITS + 7u)
#define FLAGS 11u
#define MAXCLS 64                          /* largest class a run can use */
#if ((7 * WBITS - 1) ^ (7 * WBITS + 7)) != 8
#error "the two lengths must differ in bit 3 only"
#endif

/* the bits of word j that belong to a message of len toy bytes (a compile-time constant for constant len) */
#define LNB(j, len) ((int)(len) - (j) * WBYTES)
#define LMASK(j, len) (LNB(j, len) <= 0 ? 0u : (LNB(j, len) >= WBYTES ? M : ((1u << (2 * LNB(j, len))) - 1u)))

HD static inline u32 ror(u32 x, int n) { x &= M; return ((x >> n) | (x << (WBITS - n))) & M; }
HD static inline u32 rol(u32 x, int n) { x &= M; return ((x << n) | (x >> (WBITS - n))) & M; }

#define GF(a, b, c, d, x, y)                                                                  \
    do {                                                                                      \
        a = (a + b + (x)) & M; d = ror(d ^ a, ROT1); c = (c + d) & M; b = ror(b ^ c, ROT2);   \
        a = (a + b + (y)) & M; d = ror(d ^ a, ROT3); c = (c + d) & M; b = ror(b ^ c, ROT4);   \
    } while (0)

/* a constant set: six constants and what follows from them */
struct Pin { u32 x3, x7, x11, x15, w4, w13, w4b, delta, y3, y3b, y11, y11b; u32 iv[8]; };

/* Complete 2-round compression of sixteen words with block length len, written out call by call.
   *y4 gets v[4] after the first call of round 1 (the b output of C0). */
HD static inline void compress2(const u32 *iv, const u32 *m, u32 len, u32 *out, u32 *y4) {
    u32 v0 = iv[0], v1 = iv[1], v2 = iv[2], v3 = iv[3], v4 = iv[4], v5 = iv[5], v6 = iv[6], v7 = iv[7];
    u32 v8 = iv[0], v9 = iv[1], v10 = iv[2], v11 = iv[3], v12 = 0, v13 = 0, v14 = len & M, v15 = FLAGS & M;
    GF(v0, v4, v8, v12, m[0], m[1]);   GF(v1, v5, v9, v13, m[2], m[3]);
    GF(v2, v6, v10, v14, m[4], m[5]);  GF(v3, v7, v11, v15, m[6], m[7]);
    GF(v0, v5, v10, v15, m[8], m[9]);  GF(v1, v6, v11, v12, m[10], m[11]);
    GF(v2, v7, v8, v13, m[12], m[13]); GF(v3, v4, v9, v14, m[14], m[15]);
    /* round 1: the words in the order 2 6 3 10 7 0 4 13 1 11 12 5 9 14 15 8 */
    GF(v0, v4, v8, v12, m[2], m[6]);   *y4 = v4;
    GF(v1, v5, v9, v13, m[3], m[10]);
    GF(v2, v6, v10, v14, m[7], m[0]);  GF(v3, v7, v11, v15, m[4], m[13]);
    GF(v0, v5, v10, v15, m[1], m[11]); GF(v1, v6, v11, v12, m[12], m[5]);
    GF(v2, v7, v8, v13, m[9], m[14]);  GF(v3, v4, v9, v14, m[15], m[8]);
    out[0] = v0 ^ v8;  out[1] = v1 ^ v9;  out[2] = v2 ^ v10; out[3] = v3 ^ v11;
    out[4] = v4 ^ v12; out[5] = v5 ^ v13; out[6] = v6 ^ v14; out[7] = v7 ^ v15;
}

/* ---------------------------------------- host only from here ---------------------------------------- */

static const u32 IV32[8] = {0x6A09E667u, 0xBB67AE85u, 0x3C6EF372u, 0xA54FF53Au,
                            0x510E527Fu, 0x9B05688Cu, 0x1F83D9ABu, 0x5BE0CD19u};

static inline u64 splitmix(u64 *s) {
    u64 z = (*s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}

/* Completes a constant set. Returns 1 if it is a pin of the family: the top toy byte of w13 is zero, and the
   call C3 = G(X3, X7, X11, X15; w4, w13) has the same b and d outputs for w4 and for
   w4' = ((K + w4) XOR 8) - K, K = IV2 + IV6 (the length cancellation of Lemma L' with XOR 8). */
static int fill_pin(Pin *p) {
    for (int i = 0; i < 8; i++) p->iv[i] = IV32[i] >> (32 - WBITS);
    const u32 K = (p->iv[2] + p->iv[6]) & M;
    if (p->w13 >> (WBITS - 2)) return 0;
    p->w4b = ((((p->w4 + K) & M) ^ (LEN_A ^ LEN_B)) - K) & M;
    u32 a = p->x3, b = p->x7, c = p->x11, d = p->x15;       GF(a, b, c, d, p->w4, p->w13);
    u32 a2 = p->x3, b2 = p->x7, c2 = p->x11, d2 = p->x15;   GF(a2, b2, c2, d2, p->w4b, p->w13);
    if (b != b2 || d != d2 || (a == a2 && c == c2)) return 0;
    p->delta = (p->w4 - p->w4b) & M;
    p->y3 = a; p->y3b = a2; p->y11 = c; p->y11b = c2;
    return 1;
}

/* random search for a pin; the same draws as small_tools.c */
static int make_pin(Pin *p, u64 *rs) {
    for (long t = 0; t < (1L << 40); t++) {
        u64 r = splitmix(rs), r2 = splitmix(rs);
        p->x3 = (u32)r & M; p->x7 = (u32)(r >> 16) & M; p->x11 = (u32)(r >> 32) & M; p->x15 = (u32)(r >> 48) & M;
        p->w4 = (u32)r2 & M; p->w13 = (u32)(r2 >> 16) & (M >> 2);
        if (fill_pin(p)) return 1;
    }
    return 0;
}

/* eta = XOR difference between A and B of the first-half d value of E3, a function of Y4 alone (w15 = 0) */
static inline u32 eta_of(const Pin *p, u32 y4) { return ror(((p->y3 + y4) ^ (p->y3b + y4)) & M, ROT1); }

/* The class of eta: all Y4 with that eta, in the order of their member numbers (the bits of the number fill
   the free bits of e1 = Y3 + Y4 from the lowest up, which is the order of increasing e1). Returns the size. */
static u32 class_members(const Pin *p, u32 eta, u32 *cls) {
    u32 n = 0;
    for (u32 e1 = 0; e1 <= M; e1++) {
        u32 y4 = (e1 - p->y3) & M;
        if (eta_of(p, y4) == eta) cls[n++] = y4;
    }
    return n;
}

/* The same class from the formula of Lemma Q': e1 AND mask = value. Returns 0 if no Y4 gives eta. */
static int class_mask_value(const Pin *p, u32 eta, u32 *mask, u32 *value) {
    u32 x = rol(eta, ROT1), v = (((p->y3b - p->y3) & M) + x) & M;
    if ((v & 1u) || ((v >> 1) & ~x & M)) return 0;
    *mask = x & (M >> 1);
    *value = ~(v >> 1) & *mask;
    return 1;
}

static inline u32 len_mask(int j, u32 len) {
    int nb = (int)len - j * WBYTES;
    return nb <= 0 ? 0u : (nb >= WBYTES ? M : ((1u << (2 * nb)) - 1u));
}

/* sixteen words -> the 8W toy bytes of a block */
static void words_to_bytes(const u32 *w, u8 *b) {
    for (int i = 0; i < 16; i++)
        for (int j = 0; j < WBYTES; j++) b[i * WBYTES + j] = (u8)((w[i] >> (2 * j)) & 3u);
}

/* Complete 2-round toy hash of a byte string of len toy bytes (each 0..3), len <= 8W. Written separately from
   compress2: bytes to words here, a loop with the permutation table, state in an array. */
static void hash_bytes(const u8 *msg, u32 len, u32 *out) {
    static const int P[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
    u8 blk[BLOCKBYTES];
    u32 v[16], m[16], t[16];
    memset(blk, 0, sizeof blk);
    memcpy(blk, msg, len);
    for (int i = 0; i < 16; i++) {
        m[i] = 0;
        for (int j = 0; j < WBYTES; j++) m[i] |= (u32)blk[i * WBYTES + j] << (2 * j);
    }
    for (int i = 0; i < 8; i++) v[i] = IV32[i] >> (32 - WBITS);
    for (int i = 0; i < 4; i++) v[8 + i] = IV32[i] >> (32 - WBITS);
    v[12] = 0; v[13] = 0; v[14] = len & M; v[15] = FLAGS & M;
    for (int r = 0; r < 2; r++) {
        GF(v[0], v[4], v[8], v[12], m[0], m[1]);   GF(v[1], v[5], v[9], v[13], m[2], m[3]);
        GF(v[2], v[6], v[10], v[14], m[4], m[5]);  GF(v[3], v[7], v[11], v[15], m[6], m[7]);
        GF(v[0], v[5], v[10], v[15], m[8], m[9]);  GF(v[1], v[6], v[11], v[12], m[10], m[11]);
        GF(v[2], v[7], v[8], v[13], m[12], m[13]); GF(v[3], v[4], v[9], v[14], m[14], m[15]);
        for (int i = 0; i < 16; i++) t[i] = m[P[i]];
        memcpy(m, t, sizeof m);
    }
    for (int i = 0; i < 8; i++) out[i] = v[i] ^ v[i + 8];
}
#endif
