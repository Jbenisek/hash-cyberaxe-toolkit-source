// tree64.c : 2-round BLAKE3 (prefix rounds 0,1) tree hash of M = P || X, with P = t copies of one
// 1024-byte chunk C (t >= 1, 64-bit) and X the last chunk (1..1024 bytes).  Own code, written from the
// spec; validated against hash-smash/verifier/blake3.py for small t by tree64_check.py.
// Large complete subtrees are split into 32 sub-subtrees: 4 threads x 8 SIMD lanes (gcc vectors).
// usage: tree64 T CHUNKHEX XHEX [XHEX ...]     prints the stack CVs, CV_t(X) and digest per X.
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>

typedef uint32_t u32;
typedef uint64_t u64;
typedef u32 v8 __attribute__((vector_size(32)));
#define NTH 4
#define NL 8

static const u32 IV[8] = {0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
                          0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19};
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
static u32 CW[16][16];       // chunk C as 16 blocks of 16 words
static int SCH[2][16];       // message schedule index per round

#define ROR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))
#define GS(a, b, c, d, x, y) do { \
    a = a + b + (x); d = ROR(d ^ a, 16); c = c + d; b = ROR(b ^ c, 12); \
    a = a + b + (y); d = ROR(d ^ a, 8);  c = c + d; b = ROR(b ^ c, 7); } while (0)

static void comp(u32 out[8], const u32 cv[8], const u32 m[16], u64 ctr, u32 blen, u32 flags) {
    u32 v[16];
    for (int i = 0; i < 8; i++) v[i] = cv[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IV[i];
    v[12] = (u32)ctr; v[13] = (u32)(ctr >> 32); v[14] = blen; v[15] = flags;
    for (int r = 0; r < 2; r++) {
        const int *s = SCH[r];
        GS(v[0], v[4], v[8], v[12], m[s[0]], m[s[1]]);
        GS(v[1], v[5], v[9], v[13], m[s[2]], m[s[3]]);
        GS(v[2], v[6], v[10], v[14], m[s[4]], m[s[5]]);
        GS(v[3], v[7], v[11], v[15], m[s[6]], m[s[7]]);
        GS(v[0], v[5], v[10], v[15], m[s[8]], m[s[9]]);
        GS(v[1], v[6], v[11], v[12], m[s[10]], m[s[11]]);
        GS(v[2], v[7], v[8], v[13], m[s[12]], m[s[13]]);
        GS(v[3], v[4], v[9], v[14], m[s[14]], m[s[15]]);
    }
    for (int i = 0; i < 8; i++) out[i] = v[i] ^ v[i + 8];
}

static void chunk_cv(u32 out[8], u64 ctr) {
    u32 cv[8];
    memcpy(cv, IV, sizeof cv);
    for (int k = 0; k < 16; k++)
        comp(cv, cv, CW[k], ctr, 64, (k == 0 ? 1 : 0) | (k == 15 ? 2 : 0));
    memcpy(out, cv, sizeof cv);
}

static void parent(u32 out[8], const u32 l[8], const u32 r[8], u32 flags) {
    u32 m[16];
    memcpy(m, l, 32); memcpy(m + 8, r, 32);
    comp(out, IV, m, 0, 64, flags);
}

// ---- vector versions: 8 independent lanes, same chunk content, lane-specific counters ----
static void compv(v8 out[8], const v8 cv[8], const v8 m[16], v8 clo, v8 chi, u32 blen, u32 flags) {
    v8 v[16];
    for (int i = 0; i < 8; i++) v[i] = cv[i];
    for (int i = 0; i < 4; i++) v[8 + i] = (v8){0} + IV[i];
    v[12] = clo; v[13] = chi; v[14] = (v8){0} + blen; v[15] = (v8){0} + flags;
    for (int r = 0; r < 2; r++) {
        const int *s = SCH[r];
        GS(v[0], v[4], v[8], v[12], m[s[0]], m[s[1]]);
        GS(v[1], v[5], v[9], v[13], m[s[2]], m[s[3]]);
        GS(v[2], v[6], v[10], v[14], m[s[4]], m[s[5]]);
        GS(v[3], v[7], v[11], v[15], m[s[6]], m[s[7]]);
        GS(v[0], v[5], v[10], v[15], m[s[8]], m[s[9]]);
        GS(v[1], v[6], v[11], v[12], m[s[10]], m[s[11]]);
        GS(v[2], v[7], v[8], v[13], m[s[12]], m[s[13]]);
        GS(v[3], v[4], v[9], v[14], m[s[14]], m[s[15]]);
    }
    for (int i = 0; i < 8; i++) out[i] = v[i] ^ v[i + 8];
}
static v8 CWV[16][16];
static void chunk_cv_v(v8 out[8], v8 clo, v8 chi) {
    v8 cv[8];
    for (int i = 0; i < 8; i++) cv[i] = (v8){0} + IV[i];
    for (int k = 0; k < 16; k++)
        compv(cv, cv, CWV[k], clo, chi, 64, (k == 0 ? 1 : 0) | (k == 15 ? 2 : 0));
    memcpy(out, cv, sizeof cv);
}
static void parent_v(v8 out[8], const v8 l[8], const v8 r[8]) {
    v8 m[16], ivv[8];
    for (int i = 0; i < 8; i++) { m[i] = l[i]; m[8 + i] = r[i]; ivv[i] = (v8){0} + IV[i]; }
    compv(out, ivv, m, (v8){0}, (v8){0}, 64, 4);
}
// complete subtree of 2^k chunks per lane; lane j starts at base[j]
static void subtree_v(v8 out[8], const u64 base[NL], int k) {
    v8 stk[64][8];
    int cnt[64];
    int sp = 0;
    u64 n = 1ULL << k;
    for (u64 i = 0; i < n; i++) {
        u32 lo[NL], hi[NL];
        for (int j = 0; j < NL; j++) { u64 c = base[j] + i; lo[j] = (u32)c; hi[j] = (u32)(c >> 32); }
        v8 clo, chi;
        memcpy(&clo, lo, 32); memcpy(&chi, hi, 32);
        v8 cv[8];
        chunk_cv_v(cv, clo, chi);
        int lev = 0;
        while (sp > 0 && cnt[sp - 1] == lev) {
            parent_v(cv, stk[sp - 1], cv);
            sp--; lev++;
        }
        memcpy(stk[sp], cv, sizeof cv); cnt[sp] = lev; sp++;
    }
    memcpy(out, stk[0], sizeof stk[0]);
}
// scalar complete subtree
static void subtree_s(u32 out[8], u64 base, int k) {
    if (k == 0) { chunk_cv(out, base); return; }
    u32 l[8], r[8];
    subtree_s(l, base, k - 1);
    subtree_s(r, base + (1ULL << (k - 1)), k - 1);
    parent(out, l, r, 4);
}
typedef struct { u64 base; int k; u32 res[NL][8]; } job_t;
static void *worker(void *p) {
    job_t *J = p;
    u64 b[NL];
    for (int j = 0; j < NL; j++) b[j] = J->base + ((u64)j << J->k);
    v8 out[8];
    subtree_v(out, b, J->k);
    for (int i = 0; i < 8; i++) for (int j = 0; j < NL; j++) J->res[j][i] = out[i][j];
    return NULL;
}
// complete subtree of 2^k chunks starting at base: parallel when k >= 5
static void subtree(u32 out[8], u64 base, int k) {
    if (k < 5) { subtree_s(out, base, k); return; }
    int ks = k - 5;          // 32 leaves of 2^ks chunks: thread t holds leaves 8t..8t+7
    job_t J[NTH];
    pthread_t th[NTH];
    for (int t = 0; t < NTH; t++) { J[t].base = base + ((u64)(NL * t) << ks); J[t].k = ks;
        pthread_create(&th[t], NULL, worker, &J[t]); }
    for (int t = 0; t < NTH; t++) pthread_join(th[t], NULL);
    u32 lv[32][8];
    for (int t = 0; t < NTH; t++) for (int j = 0; j < NL; j++) memcpy(lv[NL * t + j], J[t].res[j], 32);
    for (int w = 32; w > 1; w /= 2)
        for (int i = 0; i < w / 2; i++) parent(lv[i], lv[2 * i], lv[2 * i + 1], 4);
    memcpy(out, lv[0], 32);
}

static int hexval(char c) { return c <= '9' ? c - '0' : (c | 32) - 'a' + 10; }
static size_t unhex(const char *s, unsigned char *b) {
    size_t n = strlen(s) / 2;
    for (size_t i = 0; i < n; i++) b[i] = (unsigned char)(hexval(s[2 * i]) * 16 + hexval(s[2 * i + 1]));
    return n;
}
static void words_le(u32 w[16], const unsigned char *b, size_t n) {
    unsigned char blk[64] = {0};
    memcpy(blk, b, n);
    for (int i = 0; i < 16; i++) w[i] = blk[4 * i] | blk[4 * i + 1] << 8 | blk[4 * i + 2] << 16 | (u32)blk[4 * i + 3] << 24;
}
static void pr(const char *tag, const u32 *w) {
    printf("%s", tag);
    for (int i = 0; i < 8; i++) printf(" %08x", w[i]);
    printf("\n");
}

int main(int argc, char **argv) {
    if (argc < 4) { fprintf(stderr, "usage: tree64 T CHUNKHEX XHEX...\n"); return 1; }
    u64 t = strtoull(argv[1], NULL, 0);
    unsigned char cb[1024];
    if (unhex(argv[2], cb) != 1024) { fprintf(stderr, "chunk must be 1024 bytes\n"); return 1; }
    for (int i = 0; i < 16; i++) SCH[0][i] = i;
    for (int i = 0; i < 16; i++) SCH[1][i] = PERM[i];
    for (int k = 0; k < 16; k++) { words_le(CW[k], cb + 64 * k, 64);
        for (int i = 0; i < 16; i++) CWV[k][i] = (v8){0} + CW[k][i]; }
    // stack after t chunks: one complete subtree per set bit of t, highest first
    u32 stack[64][8];
    int sp = 0;
    u64 off = 0;
    for (int k = 63; k >= 0; k--) if (t >> k & 1) { subtree(stack[sp++], off, k); off += 1ULL << k; }
    printf("t %llu v12 %08x v13 %08x stack %d\n", (unsigned long long)t, (u32)t, (u32)(t >> 32), sp);
    for (int i = 0; i < sp; i++) { char tag[32]; snprintf(tag, sizeof tag, "stack%d", i); pr(tag, stack[i]); }
    for (int a = 3; a < argc; a++) {
        unsigned char xb[1024];
        size_t n = unhex(argv[a], xb);
        // last chunk: blocks of 64, CHUNK_START on first, CHUNK_END on last, counter t, non-root
        size_t nb = n == 0 ? 1 : (n + 63) / 64;
        u32 cv[8], w[16];
        memcpy(cv, IV, 32);
        for (size_t k = 0; k < nb; k++) {
            size_t bl = (k == nb - 1) ? n - 64 * k : 64;
            words_le(w, xb + 64 * k, bl);
            comp(cv, cv, w, t, (u32)bl, (k == 0 ? 1 : 0) | (k == nb - 1 ? 2 : 0));
        }
        u32 cvx[8];
        memcpy(cvx, cv, 32);
        int s = sp;
        while (s > 1) { parent(cv, stack[s - 1], cv, 4); s--; }
        u32 dig[8];
        parent(dig, stack[0], cv, 4 | 8);
        printf("x%d len %zu\n", a - 3, n);
        pr("cvx", cvx);
        pr("digest_words", dig);
    }
    return 0;
}
