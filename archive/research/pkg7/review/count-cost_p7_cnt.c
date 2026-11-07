/* Reviewer (lens: count and cost), research/pkg7 DRAFT. Own counter for the seven-word model of proof.md
 * Section 10, written from the definitions of Sections 3.3, 6.2 and 10 only (no code of the package is used).
 *
 *   N1(beta,tau,eps) = number of (d1,b1,a2) for which E1 on A and B shows beta, tau (a output), eps (c output)
 *   N3(tau,eps)      = number of (Y4 in the sub-class, h1, Y9, w8) for which E3 shows c-output difference tau,
 *                      a-output difference eps and b-output difference equal to E1's d-output difference;
 *                      also split by a rule on h1.
 *
 * Word size n and the four rotation amounts are parameters, so that the SAME functions are compared with a
 * complete enumeration at n = 8 (mode "bf") and then used at n = 32 (mode "run").
 *
 * mode bf  SEED CASES            : random constants, classes, sub-classes and rules at n = 8; prints differences
 * mode run < list of "beta tau eps" (hex) : pin H8, sub-class 07ef8303/030c0303 (or mask/value from argv)
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef unsigned __int128 u128;
typedef uint32_t u32;
typedef uint64_t u64;

static int n = 32, r1 = 16, r2 = 12, r3 = 8, r4 = 7;
static u32 M, LOW;
static u32 Y3, DY3, Y11, DY11, DELTA, ETA, SM, SV;

#define MAXC 12
typedef struct { int nc; u32 m[MAXC]; int v[MAXC]; } Rule;

static inline u32 ror(u32 x, int k) { k %= n; x &= M; if (!k) return x; return ((x >> k) | (x << (n - k))) & M; }
static inline u32 rol(u32 x, int k) { return ror(x, (n - k % n) % n); }
static inline int par(u32 x) { return __builtin_popcount(x) & 1; }

typedef struct { u32 p, q; } PQ;
typedef struct { PQ *a; size_t len, cap; } List;
static void push(List *L, u32 p, u32 q) {
    if (L->len == L->cap) { L->cap = L->cap ? 2 * L->cap : 1024; L->a = realloc(L->a, L->cap * sizeof(PQ)); if (!L->a) { fprintf(stderr, "memory\n"); exit(3); } }
    L->a[L->len].p = p; L->a[L->len].q = q; L->len++;
}
/* all p inside S (bits 0..n-2) such that q = (kh + p) mod 2^(n-1) lies inside T */
static void en_rec(List *L, u32 kh, u32 S, u32 T, int i, int c, u32 p, u32 q) {
    if (i == n - 1) { push(L, p, q); return; }
    int k = (kh >> i) & 1;
    for (int b = 0; b <= (int)((S >> i) & 1); b++) {
        int s = k + b + c, qb = s & 1;
        if (qb && !((T >> i) & 1)) continue;
        en_rec(L, kh, S, T, i + 1, s >> 1, p | ((u32)b << i), q | ((u32)qb << i));
    }
}
/* the patterns p = x AND S (top bit left out) and the bits q = y AND T (below the top bit) with 2 q = K + 2 p */
static void enumerate(List *L, u32 K, u32 S, u32 T) {
    L->len = 0;
    if (K & 1) return;
    en_rec(L, (K >> 1) & LOW, S & LOW, T, 0, 0, 0, 0);
}

static List Ls, Lt, Lu, Lv;
static u64 stat_pairs1, stat_pairs3;

static u128 N1(u32 beta, u32 tau, u32 eps) {
    u32 Bm = rol(beta, r2);
    u32 K = (Bm - DY11) & M;
    if (K & 1) return 0;
    u32 c1fix = (K >> 1) & LOW;
    if (c1fix & ~Bm) return 0;
    u32 c1mask = Bm & LOW, nu = ror(tau, r3);
    enumerate(&Ls, (tau - DELTA - beta) & M, beta, tau);
    if (!Ls.len) return 0;
    enumerate(&Lt, (eps - DY11 - nu) & M, nu, eps);
    if (!Lt.len) return 0;
    u32 d1mask = tau & LOW & ~(1u << (r3 - 1));
    u128 tot = 0;
    for (size_t is = 0; is < Ls.len; is++) {
        u32 a2fix = Ls.a[is].q;
        for (size_t it = 0; it < Lt.len; it++) {
            u32 tt = Lt.a[it].p, c2fix = Lt.a[it].q;
            u32 d1val = (rol(tt, r3) ^ a2fix) & d1mask;
            u128 st[2][2] = {{1, 0}, {0, 0}}, nw[2][2];
            stat_pairs1++;
            for (int i = 0; i < n - 1; i++) {
                memset(nw, 0, sizeof nw);
                int y = (Y11 >> i) & 1;
                for (int bw = 0; bw < 2; bw++) for (int cy = 0; cy < 2; cy++) {
                    u128 s = st[bw][cy];
                    if (!s) continue;
                    for (int c = 0; c < 2; c++) {
                        if (((c1mask >> i) & 1) && c != (int)((c1fix >> i) & 1)) continue;
                        int diff = c - y - bw, d1b = diff & 1, nbw = diff < 0;
                        if (((d1mask >> i) & 1) && d1b != (int)((d1val >> i) & 1)) continue;
                        for (int d = 0; d < 2; d++) {
                            if (((nu >> i) & 1) && d != (int)((tt >> i) & 1)) continue;
                            int sum = c + d + cy;
                            if (((eps >> i) & 1) && (sum & 1) != (int)((c2fix >> i) & 1)) continue;
                            nw[nbw][sum >> 1] += s;
                        }
                    }
                }
                memcpy(st, nw, sizeof st);
            }
            tot += st[0][0] + st[0][1] + st[1][0] + st[1][1];
        }
    }
    tot *= 2 * (((nu >> (n - 1)) & 1) ? 1 : 2);          /* c1 top bit; d2 top bit when it is free */
    return tot << (n - __builtin_popcount(beta & LOW));  /* free bits of b1 */
}

/* out[0]: all; out[1 + r]: quadruples whose h1 satisfies rule r. Returns 0, or -1 if a rule has a shape this
 * function does not handle (a condition with two free bits, or a free bit shared by two conditions). */
static int N3(u32 tau, u32 eps, int nrules, const Rule *rules, u128 *out) {
    for (int r = 0; r <= nrules; r++) out[r] = 0;
    u32 psi = tau ^ ror(tau, r3 - r4), P = rol(psi, r2), nu3 = ror(ETA ^ eps, r3);
    u32 K3 = (tau - ETA - nu3) & M;
    if (K3 & 1) return 0;
    u32 k3h = (K3 >> 1) & LOW;
    enumerate(&Lu, (P - ETA) & M, ETA, P);
    if (!Lu.len) return 0;
    enumerate(&Lv, (eps - DY3 - psi) & M, psi, eps);
    if (!Lv.len) return 0;
    u32 y4mask = P & LOW & ~(1u << (r2 - 1));
    u32 EL = ETA & LOW, epsL = eps & LOW;
    int g1top = ((P >> (n - 1)) & 1) ? 1 : 2;
    for (size_t iu = 0; iu < Lu.len; iu++) {
        u32 u = Lu.a[iu].p, g1fix = Lu.a[iu].q;
        u32 hm[MAXC + 1], hv[MAXC + 1]; int ok[MAXC + 1];
        hm[0] = EL; hv[0] = u; ok[0] = 1;
        for (int r = 0; r < nrules; r++) {
            u32 m_ = EL, v_ = u; int good = 1;
            for (int c = 0; c < rules[r].nc && good; c++) {
                u32 mk = rules[r].m[c] & M, fr = mk & ~EL;
                int want = rules[r].v[c] ^ par(u & mk & EL);
                if (!fr) { if (want) good = 0; }
                else if (__builtin_popcount(fr) == 1 && !(m_ & fr)) { m_ |= fr; if (want) v_ |= fr; }
                else return -1;
            }
            hm[r + 1] = m_; hv[r + 1] = v_; ok[r + 1] = good;
        }
        for (size_t iv = 0; iv < Lv.len; iv++) {
            u32 v = Lv.a[iv].p, e2fix = Lv.a[iv].q;
            u32 y4val = (g1fix ^ rol(v, r2)) & y4mask;
            stat_pairs3++;
            /* Y4 against e1 = Y3 + Y4 */
            u64 cst[2] = {1, 0}, cn[2];
            for (int i = 0; i < n; i++) {
                cn[0] = cn[1] = 0;
                int y3 = (Y3 >> i) & 1;
                for (int cy = 0; cy < 2; cy++) {
                    if (!cst[cy]) continue;
                    for (int y = 0; y < 2; y++) {
                        if (((y4mask >> i) & 1) && y != (int)((y4val >> i) & 1)) continue;
                        int sum = y + y3 + cy;
                        if (((SM >> i) & 1) && (sum & 1) != (int)((SV >> i) & 1)) continue;
                        cn[sum >> 1] += cst[cy];
                    }
                }
                cst[0] = cn[0]; cst[1] = cn[1];
            }
            u64 nY = cst[0] + cst[1];
            if (!nY) continue;
            for (int r = 0; r <= nrules; r++) {
                if (!ok[r]) continue;
                u128 st[2][3] = {{1, 0, 0}, {0, 0, 0}}, nw[2][3];
                unsigned W[2];
                for (int i = 0; i < n; i++) {
                    int j = (i + r3) % n;
                    W[0] = W[1] = 0;
                    for (int a = 0; a < 2; a++) {
                        if (((hm[r] >> j) & 1) && a != (int)((hv[r] >> j) & 1)) continue;
                        for (int b = 0; b < 2; b++) {
                            if (((epsL >> j) & 1) && b != (int)((e2fix >> j) & 1)) continue;
                            W[a ^ b]++;
                        }
                    }
                    if (i == n - 1) {
                        u128 t = 0;
                        for (int cy = 0; cy < 2; cy++) for (int cz = 0; cz < 3; cz++) t += st[cy][cz];
                        out[r] += t * (W[0] + W[1]) * g1top * nY;
                        break;
                    }
                    memset(nw, 0, sizeof nw);
                    int kb = (k3h >> i) & 1, ub = (u >> i) & 1, tb = (tau >> i) & 1, nb = (nu3 >> i) & 1;
                    for (int cy = 0; cy < 2; cy++) for (int cz = 0; cz < 3; cz++) {
                        u128 s = st[cy][cz];
                        if (!s) continue;
                        for (int g = 0; g < 2; g++) {
                            if (((P >> i) & 1) && g != (int)((g1fix >> i) & 1)) continue;
                            for (int h = 0; h < 2; h++) {
                                if (!W[h]) continue;
                                int sg = g + h + cy, z = kb + ub + (nb ? h : 0) + cz, q = z & 1;
                                if (tb ? ((sg & 1) != q) : q) continue;
                                nw[sg >> 1][z >> 1] += s * W[h];
                            }
                        }
                    }
                    memcpy(st, nw, sizeof st);
                }
            }
        }
    }
    return 0;
}

static void pr128(u128 x) {
    char b[64]; int k = 63; b[k] = 0;
    if (!x) b[--k] = '0';
    while (x) { b[--k] = '0' + (int)(x % 10); x /= 10; }
    fputs(b + k, stdout);
}

/* ------------------------------------------------------------------ complete enumeration at n = 8 */
static u64 rs;
static u32 rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return (u32)(rs >> 16); }

static int rule_ok(const Rule *R, u32 h1) {
    for (int c = 0; c < R->nc; c++) if (par(h1 & R->m[c]) != R->v[c]) return 0;
    return 1;
}

static int bf_case(int id) {
    n = 8; r1 = 4; r2 = 3; r3 = 2; r4 = 1; M = 0xff; LOW = 0x7f;
    Y3 = rnd() & M; DY3 = rnd() & M; Y11 = rnd() & M; DY11 = rnd() & M; DELTA = rnd() & M;
    if (!DY3) DY3 = 1;
    if (!DY11) DY11 = 8;
    u32 y40 = rnd() & M, e10 = (Y3 + y40) & M, x = e10 ^ ((e10 + DY3) & M);
    ETA = ror(x, r1);
    SM = x & LOW; SV = e10 & SM;
    int extra = rnd() % 4;
    for (int k = 0; k < extra; k++) { u32 b = 1u << (rnd() % 8); if (!(SM & b)) { SM |= b; if (rnd() & 1) SV |= b; } }
    Rule rules[3]; int nrules = 3;
    u32 EL = ETA & LOW;
    for (int r = 0; r < nrules; r++) {
        u32 used = 0; rules[r].nc = 0;
        int want = 1 + rnd() % 4;
        for (int c = 0; c < want; c++) {
            u32 mk = 0; int tries = 0;
            int k = rnd() % 4;                         /* 0..3 bits inside eta */
            for (int t = 0; t < k; t++) mk |= (1u << (rnd() % 8)) & EL;
            if (rnd() & 1) { u32 b; do { b = 1u << (rnd() % 8); } while (((b & EL) || (b & used)) && ++tries < 50); if (tries < 50) { mk |= b; used |= b; } }
            if (!mk) continue;
            rules[r].m[rules[r].nc] = mk; rules[r].v[rules[r].nc] = rnd() & 1; rules[r].nc++;
        }
    }
    static u32 *H1; static u64 *H3; /* H1[beta<<16|tau<<8|eps]; H3[(1+r)... ][tau<<8|eps] */
    if (!H1) { H1 = malloc(sizeof(u32) << 24); H3 = malloc(sizeof(u64) * 4 << 16); }
    memset(H1, 0, sizeof(u32) << 24); memset(H3, 0, sizeof(u64) * 4 << 16);
    u64 bad_id = 0;
    for (u32 d1 = 0; d1 < 256; d1++) for (u32 b1 = 0; b1 < 256; b1++) for (u32 a2 = 0; a2 < 256; a2++) {
        u32 c1 = (Y11 + d1) & M, c1p = (c1 + DY11) & M, y6 = rol(b1, r2) ^ c1, b1p = ror(y6 ^ c1p, r2);
        u32 a2p = (a2 + DELTA + b1p - b1) & M, d2 = ror(d1 ^ a2, r3), d2p = ror(d1 ^ a2p, r3);
        u32 c2 = (c1 + d2) & M, c2p = (c1p + d2p) & M, b2 = ror(b1 ^ c2, r4), b2p = ror(b1p ^ c2p, r4);
        u32 beta = b1 ^ b1p, tau = a2 ^ a2p, eps = c2 ^ c2p;
        if ((d2 ^ d2p) != ror(tau, r3) || (b2 ^ b2p) != ror(beta ^ eps, r4)) bad_id++;
        H1[beta << 16 | tau << 8 | eps]++;
    }
    u64 joint[4] = {0, 0, 0, 0}, members = 0;
    for (u32 y4 = 0; y4 < 256; y4++) {
        u32 e1 = (Y3 + y4) & M, e1p = (e1 + DY3) & M;
        if ((e1 & SM) != SV) continue;
        members++;
        if (ror(e1 ^ e1p, r1) != ETA) bad_id++;
        for (u32 h1 = 0; h1 < 256; h1++) {
            u32 y14 = rol(h1, r1) ^ e1, h1p = ror(y14 ^ e1p, r1);
            int rk[4] = {1, rule_ok(&rules[0], h1), rule_ok(&rules[1], h1), rule_ok(&rules[2], h1)};
            for (u32 y9 = 0; y9 < 256; y9++) {
                u32 g1 = (y9 + h1) & M, g1p = (y9 + h1p) & M, f1 = ror(y4 ^ g1, r2), f1p = ror(y4 ^ g1p, r2);
                for (u32 w8 = 0; w8 < 256; w8++) {
                    u32 e2 = (e1 + f1 + w8) & M, e2p = (e1p + f1p + w8) & M;
                    u32 h2 = ror(h1 ^ e2, r3), h2p = ror(h1p ^ e2p, r3), g2 = (g1 + h2) & M, g2p = (g1p + h2p) & M;
                    u32 f2 = ror(f1 ^ g2, r4), f2p = ror(f1p ^ g2p, r4);
                    u32 da = e2 ^ e2p, db = f2 ^ f2p, dc = g2 ^ g2p, dd = h2 ^ h2p;
                    /* R = 0: E1.a = E3.c, E3.a = E1.c, E3.b = E1.d, E1.b = E3.d (digest words 1, 3, 4, 6) */
                    if (db != ror(dc, r3)) continue;       /* E1.d difference is ROR(tau, r3), checked above */
                    for (int r = 0; r < 4; r++) if (rk[r]) H3[(size_t)r << 16 | dc << 8 | da]++;
                    u32 beta = rol(dd, r4) ^ da;           /* E1.b difference ROR(beta^eps, r4) = dd */
                    u32 c = H1[beta << 16 | dc << 8 | da];
                    if (c) for (int r = 0; r < 4; r++) if (rk[r]) joint[r] += c;
                }
            }
        }
    }
    /* the counter */
    u64 dif1 = 0, dif3 = 0, nz1 = 0, nz3 = 0; int unsup = 0;
    u128 cj[4] = {0, 0, 0, 0};
    static u128 *C3; if (!C3) C3 = malloc(sizeof(u128) * 4 << 16);
    for (u32 tau = 0; tau < 256; tau++) for (u32 eps = 0; eps < 256; eps++) {
        u128 o[4];
        if (N3(tau, eps, 3, rules, o)) { unsup = 1; break; }
        for (int r = 0; r < 4; r++) { C3[(size_t)r << 16 | tau << 8 | eps] = o[r]; if (o[r] != H3[(size_t)r << 16 | tau << 8 | eps]) dif3++; if (H3[(size_t)r << 16 | tau << 8 | eps]) nz3++; }
    }
    if (unsup) { printf("case %d: rule shape not handled, skipped\n", id); return 0; }
    for (u32 beta = 0; beta < 256; beta++) for (u32 tau = 0; tau < 256; tau++) for (u32 eps = 0; eps < 256; eps++) {
        u32 k = beta << 16 | tau << 8 | eps;
        u128 c = N1(beta, tau, eps);
        if (c != H1[k]) dif1++;
        if (H1[k]) nz1++;
        if (c && ETA == (eps ^ rol(beta ^ eps, r3 - r4)))
            for (int r = 0; r < 4; r++) cj[r] += c * C3[(size_t)r << 16 | tau << 8 | eps];
    }
    int bad = dif1 || dif3 || bad_id;
    for (int r = 0; r < 4; r++) if (cj[r] != joint[r]) bad = 1;
    printf("case %d: members %llu eta %02x sub %02x/%02x rules %d,%d,%d cond; nonzero N1 %llu, N3 %llu; differ N1 %llu, N3 %llu, identities %llu; joint bf %llu %llu %llu %llu counter ",
           id, (unsigned long long)members, ETA, SM, SV, rules[0].nc, rules[1].nc, rules[2].nc, (unsigned long long)nz1, (unsigned long long)nz3,
           (unsigned long long)dif1, (unsigned long long)dif3, (unsigned long long)bad_id,
           (unsigned long long)joint[0], (unsigned long long)joint[1], (unsigned long long)joint[2], (unsigned long long)joint[3]);
    for (int r = 0; r < 4; r++) { pr128(cj[r]); putchar(' '); }
    printf("%s\n", bad ? "DIFFERENT" : "equal");
    fflush(stdout);
    return bad;
}

int main(int argc, char **argv) {
    if (argc >= 4 && !strcmp(argv[1], "bf")) {
        rs = 0x9E3779B97F4A7C15ULL ^ (u64)strtoull(argv[2], 0, 10) * 0xD1B54A32D192ED03ULL;
        for (int i = 0; i < 20; i++) rnd();
        int cases = atoi(argv[3]), bad = 0;
        for (int c = 0; c < cases; c++) bad += bf_case(c);
        printf("bf seed %s: cases %d, different %d\n", argv[2], cases, bad);
        return bad ? 1 : 0;
    }
    if (argc >= 2 && !strcmp(argv[1], "run")) {
        n = 32; r1 = 16; r2 = 12; r3 = 8; r4 = 7; M = 0xffffffffu; LOW = 0x7fffffffu;
        /* pin H8, typed from proof.md 3.2 and 6.1/6.2: Y3, Y3', Y11, Y11', delta, eta */
        Y3 = 0x8127c181u; DY3 = 0x7edf3e7eu - 0x8127c181u; Y11 = 0x7af77f38u; DY11 = 0x850000c3u - 0x7af77f38u;
        DELTA = 0xfffffff8u; ETA = 0x830303cfu;
        SM = 0x07ef8303u; SV = 0x030c0303u;
        if (argc >= 4) { SM = (u32)strtoul(argv[2], 0, 16); SV = (u32)strtoul(argv[3], 0, 16); }
        Rule rules[3] = {
            {8, {0x00000001, 0x00000002, 0x00010000, 0x00020000, 0x00000404, 0x00000808, 0x01001008, 0x02002040}, {0, 1, 0, 0, 1, 1, 0, 0}},
            {6, {0x00000001, 0x00000002, 0x00010000, 0x00020000, 0x00000404, 0x00000808}, {0, 1, 0, 0, 1, 1}},
            {4, {0x00000001, 0x00000002, 0x00010000, 0x00020000}, {0, 1, 0, 0}}};
        char line[256];
        while (fgets(line, sizeof line, stdin)) {
            unsigned b, t, e;
            if (sscanf(line, "%x %x %x", &b, &t, &e) != 3) continue;
            u128 o[4];
            stat_pairs1 = stat_pairs3 = 0;
            u128 c1 = N1(b, t, e);
            int ok = (ETA == (e ^ rol(b ^ e, r3 - r4)));
            if (N3(t, e, 3, rules, o)) { printf("%08x %08x %08x UNSUPPORTED\n", b, t, e); continue; }
            printf("%08x\t%08x\t%08x\t%d\t", b, t, e, ok);
            pr128(c1); putchar('\t'); pr128(o[0]); putchar('\t'); pr128(o[1]); putchar('\t'); pr128(o[2]); putchar('\t'); pr128(o[3]);
            printf("\t%llu\t%llu\n", (unsigned long long)stat_pairs1, (unsigned long long)stat_pairs3);
            fflush(stdout);
        }
        return 0;
    }
    fprintf(stderr, "usage: bf SEED CASES | run [MASK VALUE] < outcomes\n");
    return 2;
}
