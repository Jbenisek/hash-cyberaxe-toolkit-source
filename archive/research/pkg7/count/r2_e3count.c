/* Number of E3 inputs that match a given E1 outcome. Research scratch, not submitted.
 *
 * Local model of the final diagonal pair (see r2_local_gpu.cu, r2_feas_gpu.cu).
 * An E1 sample fixes the XOR differences tau and eps and requires the E3
 * first-half d difference eta. This program counts the quadruples
 * (e1, h1, g1, e2) of words, in bijection with (Y4, Y14, Y9, w8), with
 *
 *     e1 ^ (e1 + D3)                 = ROL(eta, R1)
 *     g1 ^ (g1 + dh1)                = X2 = ROL(tau ^ ROR(tau,R3-R4), R2),   dh1 = (h1 ^ eta) - h1
 *     e2 ^ (e2 + D3 + df1)           = eps,  df1 = (f1 ^ psi) - f1, f1 = ROR((e1 - Y3) ^ g1, R2)
 *     (g1 + h2) ^ (g1 + dh1 + h2')   = tau,  h2 = ROR(h1 ^ e2, R3), h2' = h2 ^ ROR(eta ^ eps, R3)
 *
 * where R1..R4 are the four rotation amounts of G (16, 12, 8, 7 for BLAKE3).
 * For fixed additive differences (dh1, df1, dh2) the count is a product of two
 * carry automata and is exact. The admissible differences are enumerated in
 * full whenever that fits the work budget (the normal case); only beyond it is
 * a uniform random subset used, with the matching weight, which keeps the
 * result unbiased. The summary says how many keys needed that.
 *
 * If N3(K) is the count for the outcome K of a uniform E1 sample, the rate of
 * a zero residual relative to 2^-(4*word size) is the mean of N3(K) over E1
 * samples.
 *
 * The word size is a compile-time parameter so that exactly this code can be
 * checked against brute force on a scaled-down hash (see r2_toy.c):
 *   -DWBITS=8 (default 32); rotations default to 16,12,8,7 at 32 bits and to
 *   W/2, (3W+4)/8, (W+2)/4, (W+2)/4-1 otherwise, or -DROT1=.. -DROT2=.. etc.
 *
 *   gcc -O2 -fopenmp -o r2_e3count r2_e3count.c -lm
 *   ./r2_e3count D3 Y3 [log2 of the number of E1 samples behind the keys] [-v] < lines "KEY tau eps eta beta"
 */
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef uint32_t u32;
typedef uint64_t u64;

#ifndef WBITS
#define WBITS 32
#endif
#if WBITS == 32
#define WMASK 0xFFFFFFFFu
#ifndef ROT1
#define ROT1 16
#define ROT2 12
#define ROT3 8
#define ROT4 7
#endif
#else
#define WMASK ((1u << WBITS) - 1u)
#ifndef ROT1
#define ROT1 (WBITS / 2)
#define ROT2 ((3 * WBITS + 4) / 8)
#define ROT3 ((WBITS + 2) / 4)
#define ROT4 (ROT3 - 1)
#endif
#endif
#define ROTD (ROT3 - ROT4)
#define TOPBIT (1u << (WBITS - 1))
#define LOWBITS (WMASK >> 1)

static inline u32 ror(u32 x, int n) { x &= WMASK; n %= WBITS; return n ? ((x >> n) | (x << (WBITS - n))) & WMASK : x; }
static inline u32 rol(u32 x, int n) { x &= WMASK; n %= WBITS; return n ? ((x << n) | (x >> (WBITS - n))) & WMASK : x; }
static inline int in_s(u32 d, u32 x) { u32 t = (d + x) & WMASK; return (t & 1u) == 0 && ((t >> 1) & ~x & WMASK) == 0; }

static inline u64 rnd(u64 *s) {
    u64 z = (*s += 0x9E3779B97F4A7C15ull);
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBull;
    return z ^ (z >> 31);
}
static inline double uni(u64 *s) { return (double)(rnd(s) >> 11) * (1.0 / 9007199254740992.0); }

/* Signed sums: all d = sum_{i in a} +-2^i (mod 2^W) with k + d = sum_{i in b} +-2^i.
   ways[i][c+2] = number of such d restricted to bits i..W-1 when the carry into bit i is c. */
typedef struct { u32 k, a, b; double ways[33][6]; } Meet;

static void meet_build(Meet *m, u32 k, u32 a, u32 b) {
    const int top = WBITS - 1;
    m->k = k; m->a = a; m->b = b;
    for (int c = -2; c <= 3; c++)
        m->ways[top][c + 2] = (((c + (int)((k >> top) & 1) + (int)((a >> top) & 1) + (int)((b >> top) & 1)) & 1) == 0) ? 1.0 : 0.0;
    for (int i = top - 1; i >= 0; i--) {
        int ki = (k >> i) & 1, ai = (a >> i) & 1, bi = (b >> i) & 1;
        for (int c = -2; c <= 3; c++) {
            double w = 0.0;
            if (((c + ki + ai + bi) & 1) == 0) {
                for (int si = 0; si < (ai ? 2 : 1); si++) {
                    int s = ai ? (si ? 1 : -1) : 0;
                    for (int ti = 0; ti < (bi ? 2 : 1); ti++) {
                        int t = bi ? (ti ? 1 : -1) : 0;
                        w += m->ways[i + 1][((c + ki + s - t) >> 1) + 2];
                    }
                }
            }
            m->ways[i][c + 2] = w;
        }
    }
}
static inline double meet_total(const Meet *m) { return m->ways[0][2]; }

static u32 meet_sample(const Meet *m, u64 *rs) {
    int c = 0; u32 d = 0;
    for (int i = 0; i < WBITS - 1; i++) {
        int ki = (m->k >> i) & 1, ai = (m->a >> i) & 1, bi = (m->b >> i) & 1;
        double r = uni(rs) * m->ways[i][c + 2], acc = 0.0;
        int ps = 0, pn = c, found = 0;
        for (int si = 0; si < (ai ? 2 : 1) && !found; si++) {
            int s = ai ? (si ? 1 : -1) : 0;
            for (int ti = 0; ti < (bi ? 2 : 1); ti++) {
                int t = bi ? (ti ? 1 : -1) : 0;
                int nx = (c + ki + s - t) >> 1;
                double w = m->ways[i + 1][nx + 2];
                if (w == 0.0) continue;
                ps = s; pn = nx; acc += w;           /* the last admissible option doubles as a fallback */
                if (r < acc) { found = 1; break; }
            }
        }
        d += (u32)(ps * (int)(1u << i));
        c = pn;
    }
    if ((m->a >> (WBITS - 1)) & 1) d += TOPBIT;
    return d & WMASK;
}

static int meet_enum_rec(const Meet *m, int i, int c, u32 d, u32 *out, int n, int cap) {
    if (i == WBITS - 1) {
        if (n < cap) out[n++] = (d + (((m->a >> (WBITS - 1)) & 1) ? TOPBIT : 0u)) & WMASK;
        return n;
    }
    int ki = (m->k >> i) & 1, ai = (m->a >> i) & 1, bi = (m->b >> i) & 1;
    for (int si = 0; si < (ai ? 2 : 1); si++) {
        int s = ai ? (si ? 1 : -1) : 0;
        for (int ti = 0; ti < (bi ? 2 : 1); ti++) {
            int t = bi ? (ti ? 1 : -1) : 0;
            int nx = (c + ki + s - t) >> 1;
            if (m->ways[i + 1][nx + 2] == 0.0) continue;
            n = meet_enum_rec(m, i + 1, nx, d + (u32)(s * (int)(1u << i)), out, n, cap);
            if (n >= cap) return n;
        }
    }
    return n;
}
static int meet_enum(const Meet *m, u32 *out, int cap) {
    if (meet_total(m) == 0.0) return 0;
    return meet_enum_rec(m, 0, 0, 0, out, 0, cap);
}

/* #e1 with (e1 & fm) == fv and ((e1 - y3) & ym) == yv */
static double count_e(u32 fm, u32 fv, u32 y3, u32 ym, u32 yv) {
    double st[2] = {1.0, 0.0}, nx[2];
    for (int i = 0; i < WBITS; i++) {
        nx[0] = nx[1] = 0.0;
        int yb = (y3 >> i) & 1;
        for (int b = 0; b < 2; b++) {
            if (st[b] == 0.0) continue;
            for (int e = 0; e < 2; e++) {
                if (((fm >> i) & 1) && (((fv >> i) & 1) != (u32)e)) continue;
                int diff = e ^ yb ^ b;
                if (((ym >> i) & 1) && (((yv >> i) & 1) != (u32)diff)) continue;
                int bo = ((!e) & yb) | ((!(e ^ yb)) & b);
                nx[bo] += st[b];
            }
        }
        st[0] = nx[0]; st[1] = nx[1];
        if (st[0] == 0.0 && st[1] == 0.0) return 0.0;
    }
    return st[0] + st[1];
}

/* #(g1, h1, e2): g1 fixed on gm, h1 fixed on hm, e2 fixed on em, (h1^e2) fixed on xm,
   g2 = g1 + ROR(h1 ^ e2, R3) fixed on tm. */
static double count_g(u32 gm, u32 gv, u32 hm, u32 hv, u32 em, u32 ev, u32 xm, u32 xv, u32 tm, u32 tv) {
    double w[32][2];
    for (int j = 0; j < WBITS; j++) {
        w[j][0] = w[j][1] = 0.0;
        for (int h = 0; h < 2; h++) {
            if (((hm >> j) & 1) && (((hv >> j) & 1) != (u32)h)) continue;
            for (int e = 0; e < 2; e++) {
                if (((em >> j) & 1) && (((ev >> j) & 1) != (u32)e)) continue;
                int x = h ^ e;
                if (((xm >> j) & 1) && (((xv >> j) & 1) != (u32)x)) continue;
                w[j][x] += 1.0;
            }
        }
        if (w[j][0] == 0.0 && w[j][1] == 0.0) return 0.0;
    }
    double st[2] = {1.0, 0.0}, nx[2];
    for (int i = 0; i < WBITS; i++) {
        nx[0] = nx[1] = 0.0;
        int j = (i + ROT3) % WBITS;
        for (int c = 0; c < 2; c++) {
            if (st[c] == 0.0) continue;
            for (int g = 0; g < 2; g++) {
                if (((gm >> i) & 1) && (((gv >> i) & 1) != (u32)g)) continue;
                for (int h = 0; h < 2; h++) {
                    if (w[j][h] == 0.0) continue;
                    int sum = g ^ h ^ c;
                    if (((tm >> i) & 1) && (((tv >> i) & 1) != (u32)sum)) continue;
                    int co = (g & h) | (g & c) | (h & c);
                    nx[co] += st[c] * w[j][h];
                }
            }
        }
        st[0] = nx[0]; st[1] = nx[1];
        if (st[0] == 0.0 && st[1] == 0.0) return 0.0;
    }
    return st[0] + st[1];
}

#define CAP_LIST 65536          /* largest list of dh1 or df1 values enumerated in full */
static double PAIR_BUDGET = 4194304.0;  /* most (dh1, df1) pairs evaluated exactly per key (-b log2) */
static long PAIR_SAMPLES = 65536;       /* pairs drawn when the budget is exceeded (-s log2) */
#define CAP_THIRD 1024          /* most dh2 values enumerated per dh1 */
#define THIRD_SAMPLES 64

typedef struct { double n; int sampled; double na, nb; } Result;
typedef struct { u32 *la, *lb, *lc; double *nca; } Scratch;

static void scratch_init(Scratch *sc) {
    sc->la = malloc(CAP_LIST * sizeof(u32)); sc->lb = malloc(CAP_LIST * sizeof(u32));
    sc->lc = malloc(CAP_THIRD * sizeof(u32)); sc->nca = malloc(CAP_LIST * sizeof(double));
}
static void scratch_free(Scratch *sc) { free(sc->la); free(sc->lb); free(sc->lc); free(sc->nca); }

static Result n3(u32 d3, u32 y3, u32 tau, u32 eps, u32 eta, Scratch *sc, u64 *rs) {
    const u32 LOW = LOWBITS;
    Result res = {0.0, 0, 0.0, 0.0};
    u32 x1 = rol(eta, ROT1);
    if (!in_s(d3, x1)) return res;
    u32 psi = tau ^ ror(tau, ROTD), x2 = rol(psi, ROT2), mu = ror(eta ^ eps, ROT3);
    u32 e1m = x1 & LOW, e1v = ~(((d3 + x1) & WMASK) >> 1) & e1m;
    u32 hm = eta & LOW, gm = x2 & LOW, pm = psi & LOW, em = eps & LOW, mm = mu & LOW, tm = tau & LOW;
    u32 ygm = rol(pm, ROT2), ym = ygm & gm, xm = rol(mm, ROT3);
    int couple = (int)((ygm >> (WBITS - 1)) & 1);                  /* top bit: Y4 ^ g1 fixed, g1 free */
    Meet ma, mb, mc;
    meet_build(&ma, 0, eta, x2);
    meet_build(&mb, d3, psi, eps);
    double na = meet_total(&ma), nb = meet_total(&mb);
    res.na = na; res.nb = nb;
    if (na == 0.0 || nb == 0.0) return res;
    int full_a = na <= CAP_LIST, full_b = nb <= CAP_LIST;
    int ea = 0, eb = 0;
    if (full_a) {
        /* keep only dh1 for which some dh2 exists */
        int raw = meet_enum(&ma, sc->la, CAP_LIST);
        for (int i = 0; i < raw; i++) {
            meet_build(&mc, sc->la[i], mu, tau);
            double nc = meet_total(&mc);
            if (nc > 0.0) { sc->la[ea] = sc->la[i]; sc->nca[ea] = nc; ea++; }
        }
        if (ea == 0) return res;
    }
    if (full_b) eb = meet_enum(&mb, sc->lb, CAP_LIST);
    double space = (full_a ? (double)ea : na) * (full_b ? (double)eb : nb);
    int exact = full_a && full_b && space <= PAIR_BUDGET;
    long npairs = exact ? (long)ea * eb : PAIR_SAMPLES;
    double wpair = exact ? 1.0 : space / (double)PAIR_SAMPLES;
    if (!exact) res.sampled = 1;
    double total = 0.0;
    u32 last_dh1 = 0; int have_c = 0, nthird = 0, exact3 = 1; double nc = 0.0;
    for (long ip = 0; ip < npairs; ip++) {
        u32 dh1, df1;
        if (exact) { dh1 = sc->la[ip / eb]; df1 = sc->lb[ip % eb]; }
        else {
            dh1 = full_a ? sc->la[rnd(rs) % (u64)ea] : meet_sample(&ma, rs);
            df1 = full_b ? sc->lb[rnd(rs) % (u64)eb] : meet_sample(&mb, rs);
        }
        u32 gv = ~(((dh1 + x2) & WMASK) >> 1) & gm;
        u32 fv = ~(((df1 + psi) & WMASK) >> 1) & pm;                /* f1 bits on psi (top bit of psi free) */
        u32 ygv = rol(fv, ROT2);                                    /* (Y4 ^ g1) on ygm */
        u32 yv = (ygv ^ gv) & ym;                                   /* Y4 fixed where both are fixed */
        double ce[2];
        if (!couple) {
            ce[0] = count_e(e1m, e1v, y3, ym, yv); ce[1] = 0.0;
        } else {
            for (u32 v = 0; v < 2; v++) {
                u32 want = ((ygv >> (WBITS - 1)) & 1) ^ v;          /* Y4 top bit when g1 top bit = v */
                ce[v] = count_e(e1m, e1v, y3, ym | TOPBIT, yv | (want << (WBITS - 1)));
            }
        }
        if (ce[0] == 0.0 && ce[1] == 0.0) continue;
        if (!have_c || dh1 != last_dh1) {
            meet_build(&mc, dh1, mu, tau);
            nc = meet_total(&mc);
            exact3 = nc <= CAP_THIRD;
            nthird = nc == 0.0 ? 0 : (exact3 ? meet_enum(&mc, sc->lc, CAP_THIRD) : THIRD_SAMPLES);
            last_dh1 = dh1; have_c = 1;
        }
        if (nthird == 0) continue;
        if (!exact3) res.sampled = 1;
        double w3 = exact3 ? 1.0 : nc / (double)THIRD_SAMPLES;
        u32 hv = ~(((dh1 + eta) & WMASK) >> 1) & hm;
        u32 ev = ~(((d3 + df1 + eps) & WMASK) >> 1) & em;
        for (int ic = 0; ic < nthird; ic++) {
            u32 dh2 = exact3 ? sc->lc[ic] : meet_sample(&mc, rs);
            u32 mv = ~(((dh2 + mu) & WMASK) >> 1) & mm;             /* h2 bits on mu (top bit free) */
            u32 xv = rol(mv, ROT3);                                 /* (h1 ^ e2) on xm */
            u32 tv = ~(((dh1 + dh2 + tau) & WMASK) >> 1) & tm;
            if (!couple) {
                total += wpair * w3 * ce[0] * count_g(gm, gv, hm, hv, em, ev, xm, xv, tm, tv);
            } else {
                for (u32 v = 0; v < 2; v++) {
                    if (ce[v] == 0.0) continue;
                    total += wpair * w3 * ce[v] * count_g(gm | TOPBIT, gv | (v << (WBITS - 1)), hm, hv, em, ev, xm, xv, tm, tv);
                }
            }
        }
    }
    res.n = total;
    return res;
}

#ifndef R2_E3COUNT_NO_MAIN
typedef struct { u32 tau, eps, eta; } Key;

int main(int argc, char **argv) {
    if (argc < 3) { fprintf(stderr, "usage: %s D3 Y3 [log2 samples] [-v] < KEY lines\n", argv[0]); return 2; }
    u32 d3 = (u32)strtoul(argv[1], NULL, 16), y3 = (u32)strtoul(argv[2], NULL, 16);
    double logs = argc > 3 && argv[3][0] != '-' ? atof(argv[3]) : -1.0;
    int verbose = 0;
    for (int i = 3; i < argc; i++) {
        if (!strcmp(argv[i], "-v")) verbose = 1;
        else if (!strcmp(argv[i], "-b") && i + 1 < argc) PAIR_BUDGET = exp2(atof(argv[++i]));
        else if (!strcmp(argv[i], "-s") && i + 1 < argc) PAIR_SAMPLES = 1L << atoi(argv[++i]);
    }
    size_t cap = 1 << 16, nkeys = 0;
    Key *keys = malloc(cap * sizeof *keys);
    char line[256];
    while (fgets(line, sizeof line, stdin)) {
        u32 tau, eps, eta, beta;
        if (sscanf(line, "KEY %x %x %x %x", &tau, &eps, &eta, &beta) != 4) continue;
        if (nkeys == cap) { cap *= 2; keys = realloc(keys, cap * sizeof *keys); }
        keys[nkeys].tau = tau; keys[nkeys].eps = eps; keys[nkeys].eta = eta; nkeys++;
    }
    Result *out = malloc((nkeys ? nkeys : 1) * sizeof *out);
    #pragma omp parallel
    {
        Scratch sc;
        scratch_init(&sc);
        #pragma omp for schedule(dynamic, 16)
        for (long i = 0; i < (long)nkeys; i++) {
            u64 rs = 0x243F6A8885A308D3ull ^ ((u64)keys[i].tau << 32) ^ keys[i].eps ^ ((u64)keys[i].eta << 16);
            out[i] = n3(d3, y3, keys[i].tau, keys[i].eps, keys[i].eta, &sc, &rs);
        }
        scratch_free(&sc);
    }
    long positive = 0, sampled = 0;
    double sum = 0.0, sumsq = 0.0, best = 0.0, lna = 0.0, lnb = 0.0;
    for (size_t i = 0; i < nkeys; i++) {
        double n = out[i].n;
        positive += n > 0.0; sampled += out[i].sampled; sum += n; sumsq += n * n; if (n > best) best = n;
        if (out[i].na > 0) lna += log2(out[i].na);
        if (out[i].nb > 0) lnb += log2(out[i].nb);
        if (verbose) printf("N3 %08x %08x %08x  %s%.2f%s\n", keys[i].tau, keys[i].eps, keys[i].eta, n > 0 ? "2^" : "", n > 0 ? log2(n) : 0.0,
                            out[i].sampled ? "  sampled" : "");
    }
    printf("E3COUNT keys %zu  with solutions %ld  sum 2^%.2f  largest 2^%.2f  keys needing sampled branches %ld  mean log2 list sizes %.1f %.1f",
           nkeys, positive, sum > 0 ? log2(sum) : -INFINITY, best > 0 ? log2(best) : -INFINITY, sampled,
           nkeys ? lna / nkeys : 0.0, nkeys ? lnb / nkeys : 0.0);
    if (logs >= 0 && sum > 0) {
        double c = sum / exp2(logs);
        double se = sqrt(sumsq) / exp2(logs);
        printf("  rate relative to uniform: %.4g (log2 %.2f), one-sigma about %.2g", c, log2(c), se);
    }
    printf("\n");
    return 0;
}
#endif
