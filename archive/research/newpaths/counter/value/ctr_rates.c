/* ctr_rates.c  (research/newpaths/counter/value; research only, nothing filed)
 *
 * Real 32-bit arithmetic for the chunk-counter arrangement of pin H8 (lengths 55/63, last-chunk compression with
 * counter v12 = T0, v13 = 0, flags 3).  Order: scout_recent cone4_E1b1_B10.txt (basis C0.d1 D2.a1 D2.b1 E1.d1 S11 S4
 * X9 Y4 w6; inner word E1.d1), compiled from that file by gen_ctr.py into ctr_gen.inc.
 *
 *   ./ctr_rates check N SEED                 print N trials (all 107 words) for check_ctr.py (real compression)
 *   ./ctr_rates rates LOGOUT LOGIN SUB CUBE SEED
 *        2^LOGOUT outer steps (random basis words, Y4 in the eta class; SUB=1: also bits 21, 26 of e1 zero),
 *        2^LOGIN consecutive values of the inner word per outer step: CUBE=1 E1.c1 runs through the heavy beta cube
 *        (c1 & 0e09818b) == 02008000 from a random start (the counter arrangement); CUBE=0 E1.c1 uniform (control).
 *        Counts per trial: rule A (8 parity conditions on h1, research/pkg10 halfsearch.py RULES[8]) and its first
 *        four (gate H4); the deep E1 / E3 tables of research/h8/gpu/h8_deep.inc (listed beta, listed tau, listed
 *        outcome; listed partial E3 event); Lemma-E early word; joint counts; d1-direction co-pass of rule-A trials.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
typedef uint32_t u32;
typedef uint64_t u64;
#define HD
static inline u32 ror(u32 v, int n) { return (v >> n) | (v << (32 - n)); }
static inline u32 rol(u32 v, int n) { return (v << n) | (v >> (32 - n)); }
#define PX3 0x29D4FA98u
#define PX7 0xBEE3AF28u
#define PX11 0x44036000u
#define PX15 0x40C58500u
#define PW4 0x97475638u
#define PW13 0x0007C006u
#define ETA 0x830303CFu
static u32 Y3A, Y3B, Y11A, Y11B, W4B, DELTA5, CMASK, CVAL;
#include "ctr_gen.inc"
#include "h8_deep.inc"

static void g(u32 *a, u32 *b, u32 *c, u32 *d, u32 x, u32 y) {
    *a = *a + *b + x; *d = ror(*d ^ *a, 16); *c = *c + *d; *b = ror(*b ^ *c, 12);
    *a = *a + *b + y; *d = ror(*d ^ *a, 8); *c = *c + *d; *b = ror(*b ^ *c, 7);
}
static void setup(void) {
    const u32 IV2 = 0x3C6EF372u, IV6 = 0x1F83D9ABu;
    u32 K = IV2 + IV6;
    W4B = (((K + PW4) ^ (55u ^ 63u)) - K);
    DELTA5 = PW4 - W4B;
    u32 a = PX3, b = PX7, c = PX11, d = PX15; g(&a, &b, &c, &d, PW4, PW13); Y3A = a; Y11A = c;
    a = PX3; b = PX7; c = PX11; d = PX15; g(&a, &b, &c, &d, W4B, PW13); Y3B = a; Y11B = c;
    u32 x = rol(ETA, 16), v = (Y3B - Y3A) + x;
    if ((v & 1) || ((v >> 1) & ~x)) { fprintf(stderr, "eta\n"); exit(1); }
    CMASK = x & 0x7FFFFFFFu; CVAL = ~(v >> 1) & CMASK;
}
static u64 rs[2];
static inline u64 rnd64(void) {           /* xoroshiro128+ */
    u64 s0 = rs[0], s1 = rs[1], r = s0 + s1;
    s1 ^= s0; rs[0] = ((s0 << 55) | (s0 >> 9)) ^ s1 ^ (s1 << 14); rs[1] = (s1 << 36) | (s1 >> 28);
    return r;
}
static void seed(u64 s) { for (int i = 0; i < 2; i++) { s += 0x9E3779B97F4A7C15ull; u64 z = s; z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ull; z = (z ^ (z >> 27)) * 0x94D049BB133111EBull; rs[i] = z ^ (z >> 31); } }
static u32 member(int sub) {               /* Y4 with e1 = Y3A + Y4 in the class (and sub-class) */
    u32 e1 = (CVAL | ((u32)rnd64() & ~CMASK));
    if (sub) e1 &= ~0x04200000u;
    return e1 - Y3A;
}
#define CM 0x0E09818Bu
#define CV 0x02008000u
#define BETA_STAR 0x18b0e098u
static const u32 RM[8] = {0x00000001u, 0x00000002u, 0x00010000u, 0x00020000u, 0x00000404u, 0x00000808u, 0x01001008u, 0x02002040u};
static const u32 RV[8] = {0, 1, 0, 0, 1, 1, 0, 0};
static inline int rule(u32 h1, int n) {
    for (int i = 0; i < n; i++) if ((__builtin_popcount(h1 & RM[i]) & 1) != (int)RV[i]) return 0;
    return 1;
}
static void outer_rand(St *s, int sub) {
    memset(s, 0, sizeof *s);
    for (int i = 0; i < NBASIS; i++) *basis_ptr(s, i) = (u32)rnd64();
    s->Y4 = member(sub);
    outer_step(s);
}
static int do_check(int n, u64 sd) {
    seed(sd);
    for (int t = 0; t < n; t++) {
        St s; outer_rand(&s, t & 1);
        u32 c1 = (((u32)rnd64()) & ~CM) | CV;
        s.E1_d1 = c1 - Y11A;
        inner_step(&s);
        printf("TRIAL");
        for (int i = 0; i < NALL; i++) printf(" %s=%08x", ALL_NAMES[i], get_field(&s, i));
        printf("\n");
    }
    return 0;
}
/* counters */
enum { C_N, C_BSTAR, C_LBETA, C_LTAU, C_LOUT, C_RULE, C_GATE, C_E3, C_E3E, C_EARLY, C_ETAOK, C_TAU_RULE, C_TAU_GATE,
       C_E3_RULE, C_OUT_E3, C_R0, C_R1, C_R2, C_R3, C_R01, C_LOW16ALL, C_COP_N, C_TAU_E3E, C_OUT_RULE, NCNT };
static const char *CN[NCNT] = {"trials", "beta=18b0e098", "listed beta", "listed tau", "listed E1 outcome", "rule A (8)",
    "gate H4", "listed partial E3", "listed partial E3 eps 6e21be55", "early word 0", "eta condition", "listed tau & rule A",
    "listed tau & gate H4", "listed partial E3 & rule A", "listed outcome & listed partial E3", "residual word 0 zero",
    "residual word 1 zero", "residual word 2 zero", "residual word 3 zero", "residual words 0,1 zero",
    "residual low 16 bits all zero", "rule-A trials with flips", "listed tau & partial E3 eps 6e21be55",
    "listed outcome & rule A"};
static int do_rates(int lo, int li, int sub, int cube, u64 sd) {
    seed(sd);
    u64 c[NCNT]; memset(c, 0, sizeof c);
    u64 cop_gate[32], cop_rule[32]; memset(cop_gate, 0, sizeof cop_gate); memset(cop_rule, 0, sizeof cop_rule);
    double sq_rule = 0, sq_tau = 0; u64 nouter = 1ull << lo, ninner = 1ull << li;
    int freebits[32], nf = 0; for (int j = 0; j < 32; j++) if (!((CM >> j) & 1)) freebits[nf++] = j;
    for (u64 o = 0; o < nouter; o++) {
        St s; outer_rand(&s, sub);
        const u32 Y12 = s.Y12, KY = s.Y1 + s.w12, C2b = s.C2_b1, C2c = s.C2_c1, w5 = s.w5, w5b = s.w5 + DELTA5;
        const u32 y4 = s.Y4, y9 = s.Y9, w8 = s.w8, e1 = Y3A + y4, e1b = Y3B + y4, etaw = ror(e1 ^ e1b, 16);
        u32 u = ((u32)rnd64()) & ~CM;
        u64 r_rule = 0, r_tau = 0;
        for (u64 i = 0; i < ninner; i++) {
            u32 c1;
            if (cube) { u = ((u | CM) + 1) & ~CM; c1 = u | CV; } else c1 = (u32)rnd64();
            u32 d1 = c1 - Y11A, a1 = rol(d1, 16) ^ Y12, y6 = a1 - KY, y10 = rol(y6, 7) ^ C2b, y14 = y10 - C2c;
            /* E1 for A and B */
            u32 b1 = ror(y6 ^ c1, 12), a2 = a1 + b1 + w5, d2 = ror(d1 ^ a2, 8), c2 = c1 + d2, b2 = ror(b1 ^ c2, 7);
            u32 c1b = Y11B + d1, b1b = ror(y6 ^ c1b, 12), a2b = a1 + b1b + w5b, d2b = ror(d1 ^ a2b, 8), c2b = c1b + d2b, b2b = ror(b1b ^ c2b, 7);
            u32 beta = b1 ^ b1b, tau = a2 ^ a2b, eps = c2 ^ c2b;
            /* E3 for A and B (w15 = 0) */
            u32 h1 = ror(y14 ^ e1, 16), g1 = y9 + h1, f1 = ror(y4 ^ g1, 12), e2 = e1 + f1 + w8, h2 = ror(h1 ^ e2, 8), g2 = g1 + h2, f2 = ror(f1 ^ g2, 7);
            u32 h1b = ror(y14 ^ e1b, 16), g1b = y9 + h1b, f1b = ror(y4 ^ g1b, 12), e2b = e1b + f1b + w8, h2b = ror(h1b ^ e2b, 8), g2b = g1b + h2b, f2b = ror(f1b ^ g2b, 7);
            u32 psi = rol(f2 ^ f2b, 7) ^ g2 ^ g2b, eps3 = e2 ^ e2b;
            u32 r0 = a2 ^ g2 ^ a2b ^ g2b, r1 = e2 ^ c2 ^ e2b ^ c2b, r2 = f2 ^ d2 ^ f2b ^ d2b, r3 = b2 ^ h2 ^ b2b ^ h2b;
            u32 el = e1_listed(beta, tau, eps), e3 = e3_listed(psi, eps3);
            int ra = rule(h1, 8), ga = ra ? 1 : rule(h1, 4);
            c[C_N]++;
            c[C_BSTAR] += beta == BETA_STAR;
            c[C_LBETA] += el & 1; c[C_LTAU] += (el >> 1) & 1; c[C_LOUT] += (el >> 2) & 1;
            c[C_RULE] += ra; c[C_GATE] += ga;
            c[C_E3] += e3 != 0; c[C_E3E] += e3 == 2;
            c[C_EARLY] += (f1 ^ f1b ^ tau ^ ror(tau, 1)) == 0;
            c[C_ETAOK] += (eps ^ rol(beta ^ eps, 1)) == etaw;
            c[C_TAU_RULE] += ((el >> 1) & 1) & ra; c[C_TAU_GATE] += ((el >> 1) & 1) & ga;
            c[C_E3_RULE] += (e3 != 0) & ra; c[C_OUT_E3] += ((el >> 2) & 1) & (e3 != 0);
            c[C_TAU_E3E] += ((el >> 1) & 1) & (e3 == 2); c[C_OUT_RULE] += ((el >> 2) & 1) & ra;
            c[C_R0] += r0 == 0; c[C_R1] += r1 == 0; c[C_R2] += r2 == 0; c[C_R3] += r3 == 0; c[C_R01] += (r0 | r1) == 0;
            c[C_LOW16ALL] += ((r0 | r1 | r2 | r3) & 0xFFFFu) == 0;
            r_rule += ra; r_tau += (el >> 1) & 1;
            if (ra) {   /* neighbours in the inner direction: flip one free bit of c1 (stays in the cube) */
                c[C_COP_N]++;
                for (int k = 0; k < nf; k++) {
                    u32 cc = c1 ^ (1u << freebits[k]);
                    u32 dd = cc - Y11A, aa = rol(dd, 16) ^ Y12, yy6 = aa - KY, yy14 = (rol(yy6, 7) ^ C2b) - C2c;
                    u32 hh = ror(yy14 ^ e1, 16);
                    cop_gate[k] += rule(hh, 4); cop_rule[k] += rule(hh, 8);
                }
            }
        }
        sq_rule += (double)r_rule * r_rule; sq_tau += (double)r_tau * r_tau;
    }
    printf("RUN rates lo=%d li=%d sub=%d cube=%d seed=%llu\n", lo, li, sub, cube, (unsigned long long)sd);
    for (int i = 0; i < NCNT; i++) printf("CNT %-40s %llu\n", CN[i], (unsigned long long)c[i]);
    printf("SQ rule_per_outer %.6e tau_per_outer %.6e outer %llu inner %llu\n", sq_rule, sq_tau,
           (unsigned long long)nouter, (unsigned long long)ninner);
    for (int k = 0; k < nf; k++) printf("COP bit %2d gate %llu rule %llu\n", freebits[k], (unsigned long long)cop_gate[k], (unsigned long long)cop_rule[k]);
    return 0;
}
int main(int argc, char **argv) {
    setup();
    if (argc >= 4 && !strcmp(argv[1], "check")) return do_check(atoi(argv[2]), strtoull(argv[3], 0, 10));
    if (argc >= 7 && !strcmp(argv[1], "rates")) return do_rates(atoi(argv[2]), atoi(argv[3]), atoi(argv[4]), atoi(argv[5]), strtoull(argv[6], 0, 10));
    fprintf(stderr, "usage: see header\n");
    return 1;
}
