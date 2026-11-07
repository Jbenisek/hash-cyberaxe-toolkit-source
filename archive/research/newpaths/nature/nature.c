// nature.c - toy 2-round BLAKE3 experiments for research/newpaths/nature (NATURE.md).
// Toy convention = Grok job28: word size W, rotations floor(r*W/32) of (16,12,8,7), IV = low W bits,
// v12=v13=0, v14 = 2W & mask (block bytes), v15 = 11, message schedule PERM between rounds.
// Build: gcc -O3 -march=native -o nature nature.c -lm
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <time.h>

static int W = 8; static uint32_t MASK = 0xff; static int RA, RB, RC, RD; // rotations for d1,b1,d2,b2
static uint32_t IVW[8];
static const uint32_t IV32[8] = {0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
                                 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19};
static const int PERM[16] = {2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8};
static int NROUNDS = 2;

static void setw(int w) {
    W = w; MASK = (w == 32) ? 0xffffffffu : ((1u << w) - 1);
    RA = 16 * w / 32; RB = 12 * w / 32; RC = 8 * w / 32; RD = 7 * w / 32;
    for (int i = 0; i < 8; i++) IVW[i] = IV32[i] & MASK;
}
static inline uint32_t rotr(uint32_t z, int r) { z &= MASK; if (r == 0) return z; return ((z >> r) | (z << (W - r))) & MASK; }
static inline uint32_t rotl(uint32_t z, int r) { z &= MASK; if (r == 0) return z; return ((z << r) | (z >> (W - r))) & MASK; }

#define GF(a, b, c, d, x, y) do { a = (a + b + (x)) & MASK; d = rotr(d ^ a, RA); c = (c + d) & MASK; b = rotr(b ^ c, RB); \
    a = (a + b + (y)) & MASK; d = rotr(d ^ a, RC); c = (c + d) & MASK; b = rotr(b ^ c, RD); } while (0)

typedef struct { uint32_t X[16], Y[16], V[16], out[8]; } tr_t;

static void comp(const uint32_t *msg, tr_t *t) {
    uint32_t v[16], m[16], mm[16];
    for (int i = 0; i < 8; i++) v[i] = IVW[i];
    for (int i = 0; i < 4; i++) v[8 + i] = IVW[i];
    v[12] = 0; v[13] = 0; v[14] = (2 * W) & MASK; v[15] = 11 & MASK;
    for (int i = 0; i < 16; i++) m[i] = msg[i] & MASK;
    for (int r = 0; r < NROUNDS; r++) {
        GF(v[0], v[4], v[8], v[12], m[0], m[1]);
        GF(v[1], v[5], v[9], v[13], m[2], m[3]);
        GF(v[2], v[6], v[10], v[14], m[4], m[5]);
        GF(v[3], v[7], v[11], v[15], m[6], m[7]);
        if (r == 1 && t) memcpy(t->Y, v, sizeof v);
        GF(v[0], v[5], v[10], v[15], m[8], m[9]);
        GF(v[1], v[6], v[11], v[12], m[10], m[11]);
        GF(v[2], v[7], v[8], v[13], m[12], m[13]);
        GF(v[3], v[4], v[9], v[14], m[14], m[15]);
        if (r == 0 && t) memcpy(t->X, v, sizeof v);
        for (int i = 0; i < 16; i++) mm[i] = m[PERM[i]];
        memcpy(m, mm, sizeof m);
    }
    if (t) { memcpy(t->V, v, sizeof v); for (int i = 0; i < 8; i++) t->out[i] = v[i] ^ v[i + 8]; }
}
// half A = out0,2,5,7 ; half B = out1,3,4,6
static const int HA[4] = {0, 2, 5, 7}, HB[4] = {1, 3, 4, 6};
static const int TY[8] = {0, 5, 10, 15, 2, 7, 8, 13};
static const int SPECIAL[4] = {1, 9, 11, 14};
static inline int is_special(int i) { return i == 1 || i == 9 || i == 11 || i == 14; }

// rng
static uint64_t rs = 88172645463325252ull;
static inline uint64_t rnd64(void) { uint64_t z = (rs += 0x9E3779B97F4A7C15ull); z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; return z ^ (z >> 31); }
static inline uint32_t rndw(void) { return (uint32_t)rnd64() & MASK; }
static inline uint64_t mix64(uint64_t z) { z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull; z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; return z ^ (z >> 31); }

static inline int hdA(const tr_t *a, const tr_t *b) { int s = 0; for (int k = 0; k < 4; k++) s += __builtin_popcount(a->out[HA[k]] ^ b->out[HA[k]]); return s; }
static inline int eqY(const tr_t *a, const tr_t *b) { for (int k = 0; k < 8; k++) if (a->Y[TY[k]] != b->Y[TY[k]]) return 0; return 1; }
static inline uint32_t packA8(const tr_t *t) { return t->out[0] | (t->out[2] << 8) | (t->out[5] << 16) | (t->out[7] << 24); }
static inline uint32_t packB8(const tr_t *t) { return t->out[1] | (t->out[3] << 8) | (t->out[4] << 16) | (t->out[6] << 24); }

static double now(void) { struct timespec ts; clock_gettime(CLOCK_MONOTONIC, &ts); return ts.tv_sec + 1e-9 * ts.tv_nsec; }

// ---------------- selftest: print outputs for messages generated from a seed (compare with job28.py)
static void selftest(int w, uint64_t seed, int n) {
    setw(w); rs = seed; tr_t t; uint32_t m[16];
    for (int k = 0; k < n; k++) {
        for (int i = 0; i < 16; i++) m[i] = rndw();
        comp(m, &t);
        printf("M"); for (int i = 0; i < 16; i++) printf(" %x", m[i]);
        printf(" | O"); for (int i = 0; i < 8; i++) printf(" %x", t.out[i]); printf("\n");
    }
}

// ---------------- N1: neutrality of single-bit and single-word mutations; avalanche into half A
static void neutral(int w, uint64_t seed, long nbase) {
    setw(w); rs = seed;
    int nb = 16 * w; double *sumhd = calloc(nb, sizeof(double)); long *neuA = calloc(nb, sizeof(long)), *neuS = calloc(nb, sizeof(long));
    long *hist = calloc(4 * w + 1, sizeof(long)); long wordNeuA = 0, wordNeuS = 0, wordTrials = 0; long hdmin = 1 << 30;
    tr_t t0, t1; uint32_t m[16];
    for (long bi = 0; bi < nbase; bi++) {
        for (int i = 0; i < 16; i++) m[i] = rndw();
        comp(m, &t0);
        for (int p = 0; p < nb; p++) {
            int wi = p / w, bt = p % w; m[wi] ^= 1u << bt; comp(m, &t1); m[wi] ^= 1u << bt;
            int h = hdA(&t0, &t1); sumhd[p] += h; hist[h]++; if (h < hdmin) hdmin = h;
            if (h == 0) neuA[p]++;
            if (!is_special(wi) && eqY(&t0, &t1)) neuS[p]++;
        }
        for (int wi = 0; wi < 16; wi++) {
            uint32_t old = m[wi], nv; do nv = rndw(); while (nv == old);
            m[wi] = nv; comp(m, &t1); m[wi] = old; wordTrials++;
            if (hdA(&t0, &t1) == 0) wordNeuA++;
            if (!is_special(wi) && eqY(&t0, &t1)) wordNeuS++;
        }
    }
    long totA = 0, totS = 0; double mn = 1e9, mx = 0; int pmn = -1, pmx = -1;
    for (int p = 0; p < nb; p++) { totA += neuA[p]; totS += neuS[p]; double a = sumhd[p] / nbase; if (a < mn) { mn = a; pmn = p; } if (a > mx) { mx = a; pmx = p; } }
    printf("neutral w=%d bases=%ld bitflips=%ld halfA_bits=%d\n", w, nbase, nbase * nb, 4 * w);
    printf("  single-bit: halfA-neutral %ld (random expect %.3g), strong(Y)-neutral %ld (random expect %.3g)\n",
           totA, (double)nbase * nb * pow(2, -4 * w), totS, (double)nbase * nb * pow(2, -8 * w));
    printf("  single-word: trials %ld halfA-neutral %ld (expect %.3g) strong-neutral %ld\n", wordTrials, wordNeuA, wordTrials * pow(2, -4 * w), wordNeuS);
    printf("  avalanche into half A: mean per position min %.3f (word %d bit %d) max %.3f (word %d bit %d); global min hd %ld; ideal %d\n",
           mn, pmn / w, pmn % w, mx, pmx / w, pmx % w, hdmin, 2 * w);
    printf("  per-word mean hd:"); for (int wi = 0; wi < 16; wi++) { double s = 0; for (int b = 0; b < w; b++) s += sumhd[wi * w + b]; printf(" m%d=%.2f", wi, s / nbase / w); } printf("\n");
    printf("  hd histogram (low end):"); for (int h = 0; h <= 4 * w && h <= 12; h++) printf(" %d:%ld", h, hist[h]); printf("\n");
    // lowest 8 positions
    printf("  lowest-mean positions:");
    for (int k = 0; k < 8; k++) { double best = 1e9; int bp = -1; for (int p = 0; p < nb; p++) { double a = sumhd[p] / nbase; if (a < best) { best = a; bp = p; } } printf(" m%d.b%d=%.2f", bp / w, bp % w, best); sumhd[bp] = 1e18; }
    printf("\n");
}

// ---------------- N2: compensatory moves (2-word and 3-word slices), w=8 only
static void pairs8(uint64_t seed, int nbase) {
    setw(8); rs = seed; tr_t t0, t1; uint32_t m[16];
    long hitsA = 0, hitsS = 0, evals = 0; double t = now();
    for (int bi = 0; bi < nbase; bi++) {
        for (int i = 0; i < 16; i++) m[i] = rndw(); comp(m, &t0); uint32_t refA = packA8(&t0);
        for (int i = 0; i < 16; i++) for (int j = i + 1; j < 16; j++) {
            uint32_t oi = m[i], oj = m[j];
            for (uint32_t u = 0; u < 256; u++) for (uint32_t v = 0; v < 256; v++) {
                if (u == oi && v == oj) continue;
                m[i] = u; m[j] = v; comp(m, &t1); evals++;
                if (packA8(&t1) == refA) { hitsA++; printf("  pairhitA base %d words %d %d\n", bi, i, j); }
                if (!is_special(i) && !is_special(j) && eqY(&t0, &t1)) { hitsS++; printf("  pairhitS base %d words %d %d\n", bi, i, j); }
            }
            m[i] = oi; m[j] = oj;
        }
    }
    printf("pairs w=8 bases=%d evals=%ld halfA-neutral=%ld (expect %.4f) strong-neutral=%ld (expect %.3g) time %.1fs\n",
           nbase, evals, hitsA, evals * pow(2, -32), hitsS, evals * pow(2, -64), now() - t);
}
static void triples8(uint64_t seed, int base_idx) {
    setw(8); rs = seed; tr_t t0, t1; uint32_t m[16];
    for (int b = 0; b <= base_idx; b++) for (int i = 0; i < 16; i++) m[i] = rndw();
    comp(m, &t0); uint32_t refA = packA8(&t0);
    long hitsA = 0, hitsS = 0, evals = 0; double t = now();
    for (int i = 0; i < 16; i++) for (int j = i + 1; j < 16; j++) for (int k = j + 1; k < 16; k++) {
        uint32_t oi = m[i], oj = m[j], ok = m[k]; long ha = 0;
        for (uint32_t u = 0; u < 256; u++) for (uint32_t v = 0; v < 256; v++) for (uint32_t z = 0; z < 256; z++) {
            if (u == oi && v == oj && z == ok) continue;
            m[i] = u; m[j] = v; m[k] = z; comp(m, &t1); evals++;
            if (packA8(&t1) == refA) { hitsA++; ha++; }
            if (!is_special(i) && !is_special(j) && !is_special(k) && eqY(&t0, &t1)) { hitsS++; printf("  triplehitS %d %d %d\n", i, j, k); }
        }
        m[i] = oi; m[j] = oj; m[k] = ok;
        if (ha) printf("  triple %d %d %d halfA-neutral %ld\n", i, j, k, ha);
        fflush(stdout);
    }
    printf("triples w=8 base=%d evals=%ld halfA-neutral=%ld (expect %.3f) strong-neutral=%ld (expect %.3g) time %.1fs\n",
           base_idx, evals, hitsA, evals * pow(2, -32), hitsS, evals * pow(2, -64), now() - t);
}

// ---------------- C1: pivot root distributions (codon degeneracy)
// (a,c) pivot: q + ROR_RC(q ^ A) = T ; (b,d) pivot: ROR_RB(b ^ r) ^ (r + D) = K
static long count_ac(uint32_t A, uint32_t T) { // bit-serial with 2^RC seeds, verify
    long n = 0;
    for (uint32_t s = 0; s < (1u << RC); s++) {
        uint32_t q = s, h = 0;
        for (int i = 0; i + RC < W; i++) {
            uint32_t qi = (q >> i) & 1, Ti = (T >> i) & 1, ui = Ti ^ qi ^ h;
            uint32_t bitpos = i + RC, Ab = (A >> bitpos) & 1; q |= (ui ^ Ab) << bitpos;
            h = (qi & ui) | (qi & h) | (ui & h);
        }
        if (((q + rotr(q ^ A, RC)) & MASK) == T) n++;
    }
    return n;
}
static void pivot_ac(int w, uint64_t seed, long nsamp) {
    setw(w); rs = seed;
    printf("pivot_ac w=%d rot=%d max seeds %d\n", w, RC, 1 << RC);
    if (w <= 16) {
        uint32_t N = 1u << w; uint32_t *h = malloc(sizeof(uint32_t) * N); long dist[70000] = {0}; long gmax = 0; uint32_t amax = 0, tmax = 0;
        double sumsq = 0;
        for (uint32_t A = 0; A < N; A++) {
            memset(h, 0, sizeof(uint32_t) * N);
            for (uint32_t q = 0; q < N; q++) h[(q + rotr(q ^ A, RC)) & MASK]++;
            for (uint32_t T = 0; T < N; T++) { dist[h[T]]++; sumsq += (double)h[T] * h[T]; if (h[T] > gmax) { gmax = h[T]; amax = A; tmax = T; } }
        }
        double tot = (double)N * N;
        printf("  exhaustive: max roots %ld at A=%x T=%x ; E_T[n]=1 ; E_T[n^2]=%.4f (siblings per random member incl. itself)\n", gmax, amax, tmax, sumsq / tot);
        printf("  P(n=k) over uniform (A,T):"); for (int k = 0; k <= gmax && k < 70000; k++) if (dist[k]) printf(" %d:%.3e", k, dist[k] / tot); printf("\n");
        // per-A worst case E_T[n^2]
        double best = 0; uint32_t ab = 0;
        for (uint32_t A = 0; A < N; A++) { memset(h, 0, sizeof(uint32_t) * N); for (uint32_t q = 0; q < N; q++) h[(q + rotr(q ^ A, RC)) & MASK]++;
            double s = 0; for (uint32_t T = 0; T < N; T++) s += (double)h[T] * h[T]; s /= N; if (s > best) { best = s; ab = A; } }
        printf("  most degenerate A=%x: E_T[n^2]=%.3f (siblings per random member)\n", ab, best);
        free(h);
    } else { // sampled: size-biased (T from random q) and uniform T
        long hist_u[300] = {0}, hist_sb[300] = {0}; double s_u = 0, s_sb = 0;
        for (long k = 0; k < nsamp; k++) {
            uint32_t A = rndw(), T = rndw(); long n = count_ac(A, T); if (n < 300) hist_u[n]++; s_u += n;
            uint32_t q = rndw(); uint32_t T2 = (q + rotr(q ^ A, RC)) & MASK; long n2 = count_ac(A, T2); if (n2 < 300) hist_sb[n2]++; s_sb += n2;
        }
        printf("  sampled %ld: E_uniformT[n]=%.4f  E_sizebiased[n]=E[n^2]/E[n]=%.4f\n", nsamp, s_u / nsamp, s_sb / nsamp);
        printf("  uniform T  P(n=k):"); for (int k = 0; k < 300; k++) if (hist_u[k]) printf(" %d:%.4f", k, hist_u[k] / (double)nsamp); printf("\n");
        printf("  size-biased P(n=k):"); for (int k = 0; k < 300; k++) if (hist_sb[k]) printf(" %d:%.4f", k, hist_sb[k] / (double)nsamp); printf("\n");
        printf("  check Sol extreme A=0,T=ffffffff: n=%ld\n", count_ac(0, MASK));
        // special A values
        uint32_t As[4] = {0, MASK, 0x80000000u & MASK, 0x0f0f0f0fu & MASK};
        for (int a = 0; a < 4; a++) { double s = 0; long mx = 0; long ns = nsamp / 8; for (long k = 0; k < ns; k++) { uint32_t q = rndw(); uint32_t T2 = (q + rotr(q ^ As[a], RC)) & MASK; long n2 = count_ac(As[a], T2); s += n2; if (n2 > mx) mx = n2; }
            printf("  A=%x size-biased E[n]=%.3f max seen %ld\n", As[a], s / ns, mx); }
    }
}
static void pivot_bd(int w, uint64_t seed, long nsamp) {
    setw(w); rs = seed; uint32_t N = 1u << w; uint32_t *h = malloc(sizeof(uint32_t) * N);
    long dist[70000] = {0}; long gmax = 0; double sumsq = 0, tot = 0; long npar = (w <= 8) ? (long)N * N : nsamp;
    for (long k = 0; k < npar; k++) {
        uint32_t b, D; if (w <= 8) { b = k / N; D = k % N; } else { b = rndw(); D = rndw(); }
        memset(h, 0, sizeof(uint32_t) * N);
        for (uint32_t r = 0; r < N; r++) h[rotr(b ^ r, RB) ^ ((r + D) & MASK)]++;
        for (uint32_t K = 0; K < N; K++) { dist[h[K]]++; sumsq += (double)h[K] * h[K]; if (h[K] > gmax) gmax = h[K]; tot++; }
    }
    printf("pivot_bd w=%d rotB=%d params=%ld: max roots %ld ; E[n^2]=%.4f\n  P(n=k):", w, RB, npar, gmax, sumsq / tot);
    for (int k = 0; k <= gmax && k < 70000; k++) if (dist[k]) printf(" %d:%.3e", k, dist[k] / tot); printf("\n");
    free(h);
}

// ---------------- C1b: do pivot siblings survive the round-0 coupling? (w<=16, brute force over the pivot unknown)
// Column c: inputs a,b,c,d from X, message x,y; fixed outputs per column type.
static void Ginv_from_q(uint32_t a, uint32_t b, uint32_t c, uint32_t d, uint32_t A, uint32_t q, uint32_t *x, uint32_t *y) {
    uint32_t p = rotl(q, RA) ^ d, r = (c + q) & MASK, s = rotr(b ^ r, RB);
    *x = (p - a - b) & MASK; *y = (A - p - s) & MASK;
}
static void variants(int w, uint64_t seed, long nbase) {
    setw(w); rs = seed; uint32_t N = 1u << w; tr_t t0, t1; uint32_t m[16], m2[16];
    // column defs: inputs X[ci], X[4+ci], X[8+ci], X[12+ci] ; message words (round-1 col ci uses m[PERM[2ci]], m[PERM[2ci+1]])
    long sib[4] = {0}, surv[4] = {0}, maxsib[4] = {0};
    for (long bi = 0; bi < nbase; bi++) {
        for (int i = 0; i < 16; i++) m[i] = rndw(); comp(m, &t0);
        for (int ci = 0; ci < 4; ci++) {
            uint32_t a = t0.X[ci], b = t0.X[4 + ci], c = t0.X[8 + ci], d = t0.X[12 + ci];
            int ix = PERM[2 * ci], iy = PERM[2 * ci + 1];
            long ns = 0;
            if (ci == 0 || ci == 2) { // fixed A (Y[ci]) and C (Y[8+ci])
                uint32_t A = t0.Y[ci], C = t0.Y[8 + ci], T = (C - c) & MASK;
                for (uint32_t q = 0; q < N; q++) if (((q + rotr(q ^ A, RC)) & MASK) == T) {
                    uint32_t x, y; Ginv_from_q(a, b, c, d, A, q, &x, &y);
                    if (x == m[ix] && y == m[iy]) continue; ns++;
                    memcpy(m2, m, sizeof m); m2[ix] = x; m2[iy] = y; comp(m2, &t1);
                    // sanity: with X unchanged the column would give same A,C; real check: strong fiber membership
                    if (eqY(&t0, &t1)) surv[ci]++;
                }
            } else { // fixed B (Y[4+ci]) and D (Y[12+ci])
                uint32_t B = t0.Y[4 + ci], D = t0.Y[12 + ci], K = rotl(B, RD);
                for (uint32_t r = 0; r < N; r++) if ((rotr(b ^ r, RB) ^ ((r + D) & MASK)) == K) {
                    uint32_t q = (r - c) & MASK, s = rotr(b ^ r, RB), p = rotl(q, RA) ^ d, A = rotl(D, RC) ^ q;
                    uint32_t x = (p - a - b) & MASK, y = (A - p - s) & MASK;
                    if (x == m[ix] && y == m[iy]) continue; ns++;
                    memcpy(m2, m, sizeof m); m2[ix] = x; m2[iy] = y; comp(m2, &t1);
                    if (eqY(&t0, &t1)) surv[ci]++;
                }
            }
            sib[ci] += ns; if (ns > maxsib[ci]) maxsib[ci] = ns;
        }
    }
    printf("variants w=%d bases=%ld\n", w, nbase);
    for (int ci = 0; ci < 4; ci++) printf("  column C%d (%s pivot): siblings per base %.3f (max %ld); survivors in strong fiber %ld (random expect %.3g)\n",
        ci, (ci % 2 == 0) ? "a,c" : "b,d", sib[ci] / (double)nbase, maxsib[ci], surv[ci], sib[ci] * pow(2, -8 * w));
    // in-relaxed-system check: siblings DO keep the column outputs when X is held (sanity of inversion)
    long okc = 0, tot = 0;
    for (long bi = 0; bi < 200; bi++) {
        for (int i = 0; i < 16; i++) m[i] = rndw(); comp(m, &t0);
        uint32_t a = t0.X[0], b = t0.X[4], c = t0.X[8], d = t0.X[12], A = t0.Y[0], C = t0.Y[8], T = (C - c) & MASK;
        for (uint32_t q = 0; q < N; q++) if (((q + rotr(q ^ A, RC)) & MASK) == T) {
            uint32_t x, y; Ginv_from_q(a, b, c, d, A, q, &x, &y);
            uint32_t aa = a, bb = b, cc = c, dd = d; GF(aa, bb, cc, dd, x, y); tot++; if (aa == A && cc == C) okc++;
        }
    }
    printf("  sanity (X held fixed): sibling (x,y) reproduce column outputs (A,C): %ld/%ld\n", okc, tot);
}

// ---------------- G1: functional graph of x(32 bits) -> half digest, w=8
static int EMB[4]; static int EMBMODE = 0; static uint32_t BASEM[16]; static int HALF = 0; static int CTRL = 0;
static inline uint32_t fmap(uint32_t x) {
    if (CTRL) return (uint32_t)mix64(x ^ 0x1234567ull);
    uint32_t m[16]; memcpy(m, BASEM, sizeof m); tr_t t;
    if (EMBMODE == 0) { for (int k = 0; k < 4; k++) m[EMB[k]] = (x >> (8 * k)) & 0xff; }
    else { for (int k = 0; k < 16; k++) m[k] = (m[k] & 0x3f) | (((x >> (2 * k)) & 3) << 6); } // top-2 bits of every word
    comp(m, &t); return HALF ? packB8(&t) : packA8(&t);
}
static void funcgraph(const char *emb, int half, int zero_base, uint64_t seed, int nstarts, int rounds) {
    setw(8); rs = seed; HALF = half; NROUNDS = rounds;
    if (!strcmp(emb, "ctrl")) CTRL = 1; else if (!strcmp(emb, "msb2")) EMBMODE = 1;
    else sscanf(emb, "%d,%d,%d,%d", &EMB[0], &EMB[1], &EMB[2], &EMB[3]);
    for (int i = 0; i < 16; i++) BASEM[i] = zero_base ? 0 : rndw();
    uint8_t *cnt = calloc(1ull << 32, 1); if (!cnt) { printf("alloc fail\n"); return; }
    double t = now();
    for (uint64_t x = 0; x < (1ull << 32); x++) { uint32_t y = fmap((uint32_t)x); if (cnt[y] < 255) cnt[y]++; }
    double t1 = now();
    uint64_t img = 0, sat = 0; double s2 = 0; int mx = 0;
    for (uint64_t y = 0; y < (1ull << 32); y++) { int c = cnt[y]; if (c) img++; if (c == 255) sat++; s2 += (double)c * (c - 1); if (c > mx) mx = c; }
    double N = 4294967296.0;
    printf("funcgraph emb=%s half=%c base=%s rounds=%d: image fraction %.7f (random 0.6321206) ; sum n(n-1)/N = %.6f (random 1.0000) ; max preimages %d ; saturated %lu ; eval time %.0fs\n",
           emb, half ? 'B' : 'A', zero_base ? "zero" : "random", rounds, img / N, s2 / N, mx, (unsigned long)sat, t1 - t);
    free(cnt);
    // rho statistics via Brent
    double sl = 0, st = 0; double ss = 0;
    for (int k = 0; k < nstarts; k++) {
        uint32_t x0 = (uint32_t)rnd64(); uint32_t power = 1, lam = 1, tort = x0, hare = fmap(x0);
        while (tort != hare) { if (power == lam) { tort = hare; power <<= 1; lam = 0; } hare = fmap(hare); lam++; }
        uint32_t a = x0, b = x0; for (uint32_t i = 0; i < lam; i++) b = fmap(b);
        uint32_t mu = 0; while (a != b) { a = fmap(a); b = fmap(b); mu++; }
        sl += lam; st += mu; ss += (double)(lam + mu);
    }
    printf("  rho over %d starts: mean cycle %.0f, mean tail %.0f (random sqrt(pi N/8)=%.0f each), mean rho %.0f (random %.0f) ; total time %.0fs\n",
           nstarts, sl / nstarts, st / nstarts, sqrt(M_PI * N / 8), ss / nstarts, sqrt(M_PI * N / 2), now() - t);
}

// ---------------- I1: clonal selection (CLONALG) vs birthday, half-A collisions at w=8
static uint8_t *seenA, *seenM;
static inline int bm_test_set(uint8_t *bm, uint32_t k) { uint8_t b = 1u << (k & 7); int r = bm[k >> 3] & b; bm[k >> 3] |= b; return r != 0; }
static uint32_t mfp(const uint32_t *m) { uint64_t h = 0x9E37; for (int i = 0; i < 16; i++) h = mix64(h ^ (m[i] + ((uint64_t)i << 40))); return (uint32_t)h; }
typedef struct { uint32_t m[16], mp[16]; uint32_t ka, kb; int aff; } ab_t;
static int cmpab(const void *x, const void *y) { return ((const ab_t *)y)->aff - ((const ab_t *)x)->aff; }
static void clonalg(uint64_t seed, int runs, long budget, int use_table) {
    setw(8); rs = seed; tr_t t;
    seenA = calloc(1ull << 29, 1); seenM = calloc(1ull << 29, 1);
    double sumE = 0; int succ = 0; double collA_tot = 0, expect_tot = 0;
    for (int run = 0; run < runs; run++) {
        memset(seenA, 0, 1ull << 29); memset(seenM, 0, 1ull << 29);
        const int P = 50, NSEL = 10, D = 5; ab_t pop[50]; ab_t *cl = malloc(sizeof(ab_t) * 400);
        long evals = 0, distinct = 0, collA = 0; int found = 0;
#define EVAL(mm, key) do { comp(mm, &t); key = packA8(&t); evals++; uint32_t f_ = mfp(mm); if (!bm_test_set(seenM, f_)) { distinct++; if (bm_test_set(seenA, key)) { collA++; if (use_table && !found) { found = 1; } } } } while (0)
        for (int i = 0; i < P; i++) { for (int k = 0; k < 16; k++) { pop[i].m[k] = rndw(); pop[i].mp[k] = rndw(); }
            EVAL(pop[i].m, pop[i].ka); EVAL(pop[i].mp, pop[i].kb); pop[i].aff = 32 - __builtin_popcount(pop[i].ka ^ pop[i].kb); }
        while (evals < budget && !found) {
            qsort(pop, P, sizeof(ab_t), cmpab);
            if (pop[0].aff == 32 && memcmp(pop[0].m, pop[0].mp, sizeof pop[0].m)) { found = 1; break; }
            int nc = 0;
            for (int r = 0; r < NSEL; r++) {
                int ncl = (int)(0.5 * P / (r + 1) + 0.5); double rate = exp(-3.0 * pop[r].aff / 32.0); int kflip = 1 + (int)(12 * rate);
                for (int c = 0; c < ncl; c++) { cl[nc] = pop[r]; for (int f = 0; f < kflip; f++) { int pos = rnd64() % 128; cl[nc].mp[pos / 8] ^= 1u << (pos % 8); }
                    EVAL(cl[nc].mp, cl[nc].kb); cl[nc].aff = 32 - __builtin_popcount(cl[nc].ka ^ cl[nc].kb);
                    if (cl[nc].aff == 32 && memcmp(cl[nc].m, cl[nc].mp, sizeof cl[nc].m)) found = 1;
                    if (cl[nc].aff > pop[r].aff) pop[r] = cl[nc];
                    nc++; }
            }
            for (int i = P - D; i < P; i++) { for (int k = 0; k < 16; k++) { pop[i].m[k] = rndw(); pop[i].mp[k] = rndw(); }
                EVAL(pop[i].m, pop[i].ka); EVAL(pop[i].mp, pop[i].kb); pop[i].aff = 32 - __builtin_popcount(pop[i].ka ^ pop[i].kb); }
        }
        if (found) { succ++; sumE += evals; }
        double ex = (double)distinct * distinct / 2 / 4294967296.0; collA_tot += collA; expect_tot += ex;
        int bestaff = 0; for (int i = 0; i < P; i++) if (pop[i].aff > bestaff) bestaff = pop[i].aff;
        printf("  clonalg run %d: %s after %ld evals ; best pair affinity %d/32 ; distinct msgs %ld ; halfA repeats among distinct msgs %ld (uniform expect %.1f)\n",
               run, found ? "FOUND" : "none", evals, bestaff, distinct, collA, ex);
        free(cl); fflush(stdout);
    }
    printf("clonalg table=%d runs=%d success %d mean evals to success %.0f ; birthday reference (table, uniform) sqrt(pi/2*2^32)=%.0f ; pair-only random reference 2^32\n",
           use_table, runs, succ, succ ? sumE / succ : -1, sqrt(M_PI / 2 * 4294967296.0));
    printf("  pooled concentration: halfA repeats %.0f vs uniform %.1f ratio %.3f\n", collA_tot, expect_tot, collA_tot / expect_tot);
}
static void birthday_ref(uint64_t seed, int runs) {
    setw(8); rs = seed; tr_t t; uint32_t m[16]; seenA = calloc(1ull << 29, 1); double s = 0;
    for (int r = 0; r < runs; r++) { memset(seenA, 0, 1ull << 29); long e = 0;
        while (1) { for (int i = 0; i < 16; i++) m[i] = rndw(); comp(m, &t); e++; if (bm_test_set(seenA, packA8(&t))) break; }
        s += e; }
    printf("birthday uniform runs=%d mean evals %.0f (theory %.0f)\n", runs, s / runs, sqrt(M_PI / 2 * 4294967296.0));
}

// ---------------- P1: landscape autocorrelation and annealing vs random for a 16-bit partial target (w=8)
static void autocorr(int w, uint64_t seed, long n, int nflip) {
    setw(w); rs = seed; tr_t t0, t1, tt; uint32_t m[16], tg[16];
    double sx = 0, sy = 0, sxx = 0, syy = 0, sxy = 0;
    for (long k = 0; k < n; k++) {
        for (int i = 0; i < 16; i++) { m[i] = rndw(); tg[i] = rndw(); }
        comp(tg, &tt); comp(m, &t0);
        for (int f = 0; f < nflip; f++) { int p = rnd64() % (16 * w); m[p / w] ^= 1u << (p % w); }
        comp(m, &t1);
        double x = hdA(&t0, &tt), y = hdA(&t1, &tt);
        sx += x; sy += y; sxx += x * x; syy += y * y; sxy += x * y;
    }
    double cov = sxy / n - (sx / n) * (sy / n), vx = sxx / n - (sx / n) * (sx / n), vy = syy / n - (sy / n) * (sy / n);
    printf("autocorr w=%d flips=%d n=%ld: corr(f(m), f(m^e)) = %.5f (+-%.5f) ; mean f %.3f (ideal %d)\n", w, nflip, n, cov / sqrt(vx * vy), 1 / sqrt((double)n), sx / n, 2 * w);
}
static inline int e16(const tr_t *t, uint32_t tg) { return __builtin_popcount(((t->out[0]) | (t->out[2] << 8)) ^ tg); }
static void anneal(uint64_t seed, int runs, long budget) {
    setw(8); rs = seed; tr_t t; uint32_t m[16]; double sumSA = 0, sumR = 0; int okSA = 0, okR = 0;
    for (int r = 0; r < runs; r++) {
        uint32_t tg = rnd64() & 0xffff; long e = 0; int found = 0;
        // simulated annealing with restarts
        while (e < budget && !found) {
            for (int i = 0; i < 16; i++) m[i] = rndw(); comp(m, &t); e++; int E = e16(&t, tg);
            for (int step = 0; step < 4000 && !found && e < budget; step++) {
                double T = 2.0 * (1.0 - step / 4000.0) + 0.2;
                int nf = 1 + (rnd64() % 2); int pos[2]; for (int f = 0; f < nf; f++) { pos[f] = rnd64() % 128; m[pos[f] / 8] ^= 1u << (pos[f] % 8); }
                comp(m, &t); e++; int E2 = e16(&t, tg);
                if (E2 == 0) { found = 1; break; }
                if (E2 <= E || (rnd64() % 1000000) / 1e6 < exp(-(E2 - E) / T)) E = E2;
                else for (int f = 0; f < nf; f++) m[pos[f] / 8] ^= 1u << (pos[f] % 8);
            }
        }
        if (found) { okSA++; sumSA += e; }
        long e2 = 0; found = 0;
        while (e2 < budget) { for (int i = 0; i < 16; i++) m[i] = rndw(); comp(m, &t); e2++; if (e16(&t, tg) == 0) { found = 1; break; } }
        if (found) { okR++; sumR += e2; }
    }
    printf("anneal 16-bit target (out0,out2) w=8 runs=%d: SA success %d mean evals %.0f ; random success %d mean evals %.0f ; theory random 65536\n",
           runs, okSA, okSA ? sumSA / okSA : -1, okR, okR ? sumR / okR : -1);
}

// ---------------- D1: palindromic output differences of one G (DNA mirror): dA==dC and dB==dD
static void palin(int w, uint64_t seed, long n) {
    setw(w); rs = seed;
    const char *names[8] = {"x", "y", "x,y", "a", "b", "c", "d", "all6"};
    for (int ty = 0; ty < 8; ty++) {
        long hit = 0, hitnz = 0;
        for (long k = 0; k < n; k++) {
            uint32_t in[6], in2[6]; for (int i = 0; i < 6; i++) in[i] = rndw(); memcpy(in2, in, sizeof in);
            // ports: 0 a,1 b,2 c,3 d,4 x,5 y
            int sel[6] = {0}; if (ty == 0) sel[4] = 1; else if (ty == 1) sel[5] = 1; else if (ty == 2) sel[4] = sel[5] = 1;
            else if (ty <= 6) sel[ty - 3] = 1; else for (int i = 0; i < 6; i++) sel[i] = 1;
            int any = 0; for (int i = 0; i < 6; i++) if (sel[i]) { uint32_t dlt; do dlt = rndw(); while (!dlt); in2[i] ^= dlt; any = 1; }
            (void)any;
            uint32_t a = in[0], b = in[1], c = in[2], d = in[3]; GF(a, b, c, d, in[4], in[5]);
            uint32_t a2 = in2[0], b2 = in2[1], c2 = in2[2], d2 = in2[3]; GF(a2, b2, c2, d2, in2[4], in2[5]);
            uint32_t dA = a ^ a2, dB = b ^ b2, dC = c ^ c2, dD = d ^ d2;
            if (dA == dC && dB == dD) { hit++; if (dA | dB) hitnz++; }
        }
        printf("palin w=%d diff-in=%s n=%ld: palindromic %ld (nonzero %ld) ; rate/random(2^-%d) = %.3f\n", w, names[ty], n, hit, hitnz, 2 * w, hit / (n * pow(2, -2 * w)));
    }
}

// ---------------- N4: evolution of mutational robustness (van Nimwegen et al.): are there messages whose single-bit
// mutants change few half-A bits?  R(m) = #bit positions whose flip changes <= thr bits of half A.
static int robustR(uint32_t *m, int thr) {
    tr_t t0, t1; comp(m, &t0); int R = 0; int nb = 16 * W;
    for (int p = 0; p < nb; p++) { m[p / W] ^= 1u << (p % W); comp(m, &t1); m[p / W] ^= 1u << (p % W); if (hdA(&t0, &t1) <= thr) R++; }
    return R;
}
static void robust(int w, uint64_t seed, int thr, int steps) {
    setw(w); rs = seed; uint32_t m[16], best[16];
    // control: best of `steps` random messages
    int rmax = 0; double rsum = 0;
    for (int s = 0; s < steps; s++) { for (int i = 0; i < 16; i++) m[i] = rndw(); int R = robustR(m, thr); rsum += R; if (R > rmax) rmax = R; }
    // hill climb (accept if not worse), word or bit mutations
    for (int i = 0; i < 16; i++) best[i] = rndw(); int Rb = robustR(best, thr);
    for (int s = 0; s < steps; s++) {
        memcpy(m, best, sizeof m);
        if (rnd64() & 1) m[rnd64() % 16] = rndw(); else { int p = rnd64() % (16 * w); m[p / w] ^= 1u << (p % w); }
        int R = robustR(m, thr); if (R >= Rb) { Rb = R; memcpy(best, m, sizeof m); }
    }
    printf("robust w=%d thr=%d steps=%d: random messages mean R %.3f max R %d ; hill-climbed R %d\n", w, thr, steps, rsum / steps, rmax, Rb);
}

// ---------------- D1b: the d-palindrome mechanism. Input difference only in d, delta = ROL_RA(u) with ROR_RB(u) = u
// (u has period gcd(RB, W)).  Carry-free prediction: output difference (u, 0, u, 0) with probability 2^-(3 x weight).
static void dpal(int w, uint32_t u, uint64_t seed, long n) {
    setw(w); rs = seed; u &= MASK; uint32_t delta = rotl(u, RA); long hit = 0, hitany = 0;
    for (long k = 0; k < n; k++) {
        uint32_t a = rndw(), b = rndw(), c = rndw(), d = rndw(), x = rndw(), y = rndw();
        uint32_t a1 = a, b1 = b, c1 = c, d1 = d; GF(a1, b1, c1, d1, x, y);
        uint32_t a2 = a, b2 = b, c2 = c, d2 = d ^ delta; GF(a2, b2, c2, d2, x, y);
        uint32_t dA = a1 ^ a2, dB = b1 ^ b2, dC = c1 ^ c2, dD = d1 ^ d2;
        if (dA == u && dB == 0 && dC == u && dD == 0) hit++;
        if (dA == dC && dB == dD) hitany++;
    }
    int wt = __builtin_popcount(u & (MASK >> 1));
    printf("dpal w=%d u=%x (ROR_RB(u)==u: %d) n=%ld: (u,0,u,0) %ld -> 2^%.2f ; any palindrome %ld ; carry-free prediction 2^-%d\n",
           w, u, rotr(u, RB) == u, n, hit, hit ? log2((double)hit / n) : -99.0, hitany, 3 * wt);
}

int main(int argc, char **argv) {
    if (argc < 2) { fprintf(stderr, "modes: selftest neutral pairs triples pivot_ac pivot_bd variants funcgraph clonalg birthday autocorr anneal palin\n"); return 1; }
    const char *md = argv[1];
    if (!strcmp(md, "selftest")) selftest(atoi(argv[2]), strtoull(argv[3], 0, 0), atoi(argv[4]));
    else if (!strcmp(md, "neutral")) neutral(atoi(argv[2]), strtoull(argv[3], 0, 0), atol(argv[4]));
    else if (!strcmp(md, "pairs")) pairs8(strtoull(argv[2], 0, 0), atoi(argv[3]));
    else if (!strcmp(md, "triples")) triples8(strtoull(argv[2], 0, 0), atoi(argv[3]));
    else if (!strcmp(md, "pivot_ac")) pivot_ac(atoi(argv[2]), strtoull(argv[3], 0, 0), atol(argv[4]));
    else if (!strcmp(md, "pivot_bd")) pivot_bd(atoi(argv[2]), strtoull(argv[3], 0, 0), atol(argv[4]));
    else if (!strcmp(md, "variants")) variants(atoi(argv[2]), strtoull(argv[3], 0, 0), atol(argv[4]));
    else if (!strcmp(md, "funcgraph")) funcgraph(argv[2], atoi(argv[3]), atoi(argv[4]), strtoull(argv[5], 0, 0), atoi(argv[6]), atoi(argv[7]));
    else if (!strcmp(md, "clonalg")) clonalg(strtoull(argv[2], 0, 0), atoi(argv[3]), atol(argv[4]), atoi(argv[5]));
    else if (!strcmp(md, "birthday")) birthday_ref(strtoull(argv[2], 0, 0), atoi(argv[3]));
    else if (!strcmp(md, "autocorr")) autocorr(atoi(argv[2]), strtoull(argv[3], 0, 0), atol(argv[4]), atoi(argv[5]));
    else if (!strcmp(md, "anneal")) anneal(strtoull(argv[2], 0, 0), atoi(argv[3]), atol(argv[4]));
    else if (!strcmp(md, "palin")) palin(atoi(argv[2]), strtoull(argv[3], 0, 0), atol(argv[4]));
    else if (!strcmp(md, "dpal")) dpal(atoi(argv[2]), (uint32_t)strtoul(argv[3], 0, 16), strtoull(argv[4], 0, 0), atol(argv[5]));
    else if (!strcmp(md, "robust")) robust(atoi(argv[2]), strtoull(argv[3], 0, 0), atoi(argv[4]), atoi(argv[5]));
    else { fprintf(stderr, "unknown mode\n"); return 1; }
    return 0;
}
