static double g_px[1 << 20];
/* Class-rate part of a pair (eta, beta) by enumeration instead of sampling. Research scratch, not submitted.
 * C version of pair_calc.py (same definitions; see that file's header), fast enough for a weight cap of 22+.
 *
 * Outcomes (tau, eps): tau runs over every XOR difference that delta + db1 can take for db1 a signed sum over
 * the bits of beta, with at most MAXTAU bits below bit 31 (depth-first over the bits of tau with the carry
 * automaton of r2_e3count.c run forwards); eps is one of the two words with eps ^ ROR(eps,1) = beta ^ ROR(eta,1).
 * For an outcome that passes the necessary conditions:
 *     N3 = exact E3 count, n3() of r2_e3count.c (through n3x.inc, which adds an optional sub-class of e1)
 *     P1 = E1 probability. Line "PAIR": the product formula M4 * M5 * 2^-(wt beta + wt tau + wt nu + wt eps)
 *          (independence of the steps assumed; a screening value only, low by a factor of about 4 on the filed
 *          constants). Line "EXACT-E1" (needs -y11): the exact count e1_exact() below, for every outcome
 *          with N3 > 0. The EXACT-E1 line is the one to use.
 * class-rate part = 2^(wt_eta - wt_beta) * sum of P1 * N3.  With MAXTAU = 31 nothing is left out for this
 * beta (every tau with a signed-sum representation is listed); a smaller cap leaves a tail out.
 *
 *   python3 -B gen_n3x.py; gcc -O2 -fopenmp -o night_pair_calc2 pair_calc.c -lm
 *   ./night_pair_calc2 D3 D11 DELTA Y3 ETA BETA [MAXTAU=22] [-y11 Y11] [-sub MASK VALUE] [-o FILE]
 * Checks: e1_bf.c (E1 count against brute force at 8-bit words), e1_amc.py (against ApproxMC at 32 bits),
 * the sampler r2_cls_gpu on several pairs; reviewers' independent checks in research/pkg4/review/.
 */
#define R2_E3COUNT_NO_MAIN
#include "r2_e3count.c"
#include "n3x.inc"

typedef struct { u32 tau, eps; double lp1, n3; } Out;
static u32 g_delta, g_beta, g_eta, g_d3, g_d11, g_y11 = 0, g_xmask = 0, g_xval = 0; static int g_have_y11 = 0;
static int g_cap;
static u32 g_eps[2]; static int g_neps;
static Out *outs; static size_t nouts = 0, capouts = 0;
static unsigned long long ntau = 0;
static inline int wtl(u32 x) { return __builtin_popcount(x & LOWBITS); }

static void emit(u32 tau, double m4) {
    ntau++;
    u32 psi = tau ^ ror(tau, ROTD), x2 = rol(psi, ROT2), nu = ror(tau, ROT3);
    if (x2 == 0 || (x2 & -x2) != (g_eta & -g_eta)) return;
    Meet m;
    meet_build(&m, 0, g_eta, x2);
    if (meet_total(&m) == 0.0) return;
    for (int e = 0; e < g_neps; e++) {
        u32 eps = g_eps[e];
        meet_build(&m, g_d11, nu, eps);
        double m5 = meet_total(&m);
        if (m5 == 0.0) continue;
        meet_build(&m, g_d3, psi, eps);
        if (meet_total(&m) == 0.0) continue;
        if (nouts == capouts) { capouts = capouts ? capouts * 2 : 4096; outs = realloc(outs, capouts * sizeof *outs); }
        outs[nouts].tau = tau; outs[nouts].eps = eps; outs[nouts].n3 = 0.0;
        outs[nouts].lp1 = log2(m4) + log2(m5) - wtl(g_beta) - wtl(tau) - wtl(nu) - wtl(eps);
        nouts++;
    }
}

/* Exact E1 probability of the outcome (tau, eps) for a prescribed beta.
 * Unknowns c1, b1, a2 (d1 = c1 - Y11). Conditions: c1 ^ (c1 + D11) = x5 = ROL(beta, R2);
 * a2 ^ (a2 + db1 + delta) = tau with db1 = (b1 ^ beta) - b1; with d2 = ROR(d1 ^ a2, R3), d2' = d2 ^ nu and
 * dd2 = d2' - d2: (c1 + d2) ^ (c1 + d2 + D11 + dd2) = eps.  For fixed additive differences (db1, dd2) the bits of
 * a2 on tau, of d2 on nu and of c2 on eps are prescribed, and the number of (c1, a2) is a carry automaton over
 * the bits of c1 (borrow of c1 - Y11, carry of c1 + d2).  Returned: probability over c1 in the beta set
 * (2^(W - wt(x5 & LOW)) values), b1 and a2 uniform. */
static double e1_exact(u32 d11, u32 delta, u32 y11, u32 beta, u32 tau, u32 eps, u32 *la, u32 *lb) {
    const u32 LOW = LOWBITS;
    u32 x5 = rol(beta, ROT2), nu = ror(tau, ROT3);
    u32 x5m = x5 & LOW, c1v = ~(((d11 + x5) & WMASK) >> 1) & x5m;
    u32 tm = tau & LOW, nm = nu & LOW, em = eps & LOW, um = rol(nm, ROT3);
    Meet m4, m5;
    meet_build(&m4, delta, beta, tau);
    meet_build(&m5, d11, nu, eps);
    if (meet_total(&m4) == 0.0 || meet_total(&m5) == 0.0) return 0.0;
    if (meet_total(&m4) > CAP_LIST || meet_total(&m5) > CAP_LIST) return -1.0;
    int na = meet_enum(&m4, la, CAP_LIST), nb = meet_enum(&m5, lb, CAP_LIST);
    double total = 0.0;
    for (int ia = 0; ia < na; ia++) {
        u32 d4 = (delta + la[ia]) & WMASK;
        u32 a2v = ~(((d4 + tau) & WMASK) >> 1) & tm;
        for (int ib = 0; ib < nb; ib++) {
            u32 dd2 = lb[ib];
            u32 d2v = ~(((dd2 + nu) & WMASK) >> 1) & nm;
            u32 c2v = ~(((d11 + dd2 + eps) & WMASK) >> 1) & em;
            u32 uv = rol(d2v, ROT3);
            double st[2][2] = {{1.0, 0.0}, {0.0, 0.0}}, nx[2][2];      /* [borrow][carry] */
            for (int i = 0; i < WBITS; i++) {
                nx[0][0] = nx[0][1] = nx[1][0] = nx[1][1] = 0.0;
                int yb = (y11 >> i) & 1, j = (i + ROT3) % WBITS;
                int ufix = (um >> j) & 1, uval = (uv >> j) & 1;
                int utied = !ufix && ((tm >> j) & 1);               /* u_j follows d1_j: one value, unconstrained use */
                for (int b = 0; b < 2; b++) for (int k = 0; k < 2; k++) {
                    double v = st[b][k];
                    if (v == 0.0) continue;
                    for (int c = 0; c < 2; c++) {
                        if (((x5m >> i) & 1) && (int)((c1v >> i) & 1) != c) continue;
                        int d1 = c ^ yb ^ b;
                        if (((tm >> i) & 1) && ((um >> i) & 1) && d1 != (int)(((a2v ^ uv) >> i) & 1)) continue;
                        int bo = ((!c) & yb) | ((!(c ^ yb)) & b);
                        for (int d2 = 0; d2 < 2; d2++) {
                            if (ufix && d2 != uval) continue;
                            int sum = c ^ d2 ^ k;
                            if (((em >> i) & 1) && sum != (int)((c2v >> i) & 1)) continue;
                            int ko = (c & d2) | (c & k) | (d2 & k);
                            nx[bo][ko] += utied ? v * 0.5 : v;
                        }
                    }
                }
                memcpy(st, nx, sizeof st);
            }
            total += st[0][0] + st[0][1] + st[1][0] + st[1][1];
        }
    }
    /* total counts (c1, u) with u = d1 ^ a2 in bijection with a2; b1 contributes 2^(W - wt(beta & LOW)) per db1 */
    double lg = log2(total) + (WBITS - __builtin_popcount(beta & LOW)) - (WBITS - __builtin_popcount(x5m)) - 2.0 * WBITS;
    return total > 0.0 ? exp2(lg) : 0.0;
}

/* ---- pruned search (mk_pruned.py) ---- */
typedef struct { unsigned char ra[6], sb, pe[2], na[2][6], nb[2]; } Aut;
static unsigned long long g_cut = 0;
static int g_nocut = 0;                                  /* H8_NOCUT in the environment: search as before, no cut */
static inline unsigned aut_step(unsigned in, int ki, int ai, int bi) {
    unsigned out = 0;
    for (int c = -2; c <= 3; c++) {
        if (!((in >> (c + 2)) & 1) || (((c + ki + ai + bi) & 1) != 0)) continue;
        for (int si = 0; si < (ai ? 2 : 1); si++) {
            int s = ai ? (si ? 1 : -1) : 0;
            for (int ti = 0; ti < (bi ? 2 : 1); ti++) {
                int t = bi ? (ti ? 1 : -1) : 0;
                out |= 1u << (((c + ki + s - t) >> 1) + 2);
            }
        }
    }
    return out;
}
static inline unsigned aut_top(unsigned in, int ki, int ai, int bi) {
    for (int c = -2; c <= 3; c++) if (((in >> (c + 2)) & 1) && (((c + ki + ai + bi) & 1) == 0)) return 1u;
    return 0u;
}
static void aut_init(Aut *a) {
    for (int c = 0; c < 6; c++) { a->ra[c] = (unsigned char)(1u << c); a->na[0][c] = a->na[1][c] = (unsigned char)(1u << c); }
    a->sb = 4; a->pe[0] = a->pe[1] = 4; a->nb[0] = a->nb[1] = 4;      /* carry 0 */
}
/* tau has its bits 0..i decided (i < top). Returns 0 when no completion can pass emit(). */
static int aut_advance(Aut *a, int i, u32 tau) {
    const int top = WBITS - 1;
    int ti = (tau >> i) & 1;
    int q = (i - ROT3 + WBITS) % WBITS;                 /* bit q of nu = ROR(tau, ROT3) is bit i of tau */
    for (int e = 0; e < g_neps; e++) {
        int ki = (g_d11 >> q) & 1, bi = (g_eps[e] >> q) & 1;
        if (i < ROT3) {
            for (int c = 0; c < 6; c++)
                a->na[e][c] = (unsigned char)(q == top ? aut_top(a->na[e][c], ki, ti, bi) : aut_step(a->na[e][c], ki, ti, bi));
        } else a->nb[e] = (unsigned char)aut_step(a->nb[e], ki, ti, bi);
    }
    if (i >= 1) {
        int p = i - 1, pp = (int)((tau >> p) & 1) ^ ti;  /* bit p of psi = tau XOR ROR(tau, 1) */
        for (int e = 0; e < g_neps; e++)
            a->pe[e] = (unsigned char)aut_step(a->pe[e], (g_d3 >> p) & 1, pp, (g_eps[e] >> p) & 1);
        if (p <= top - ROT2) {
            int j = p + ROT2, ej = (g_eta >> j) & 1;     /* bit j of x2 = ROL(psi, ROT2) */
            for (int c = 0; c < 6; c++)
                a->ra[c] = (unsigned char)(j == top ? aut_top(a->ra[c], 0, ej, pp) : aut_step(a->ra[c], 0, ej, pp));
        } else {
            int j = p - (WBITS - ROT2);
            a->sb = (unsigned char)aut_step(a->sb, 0, (g_eta >> j) & 1, pp);
        }
    }
    unsigned anyra = 0;
    for (int c = 0; c < 6; c++) anyra |= a->ra[c];
    if (!anyra || !a->sb) return 0;
    for (int e = 0; e < g_neps; e++) {
        unsigned anyna = 0;
        for (int c = 0; c < 6; c++) anyna |= a->na[e][c];
        if (a->pe[e] && anyna && a->nb[e]) return 1;
    }
    return 0;
}

/* cnt[c+2] = number of partial sign choices on beta (bits below i) that leave carry c */
static void dfs(int i, const double *cnt, u32 tau, int w, const Aut *au) {
    const int top = WBITS - 1;
    int ki = (g_delta >> i) & 1, ai = (g_beta >> i) & 1;
    for (int bi = 0; bi < 2; bi++) {
        if (i == top) {
            double m4 = 0.0;
            for (int c = -2; c <= 3; c++)
                if (cnt[c + 2] != 0.0 && (((c + ki + ai + bi) & 1) == 0)) m4 += cnt[c + 2];
            if (m4 != 0.0) emit(tau | ((u32)bi << top), m4);
            continue;
        }
        if (w + bi > g_cap) continue;
        double nx[6] = {0, 0, 0, 0, 0, 0};
        int any = 0;
        for (int c = -2; c <= 3; c++) {
            double v = cnt[c + 2];
            if (v == 0.0 || (((c + ki + ai + bi) & 1) != 0)) continue;
            for (int si = 0; si < (ai ? 2 : 1); si++) {
                int s = ai ? (si ? 1 : -1) : 0;
                for (int ti = 0; ti < (bi ? 2 : 1); ti++) {
                    int t = bi ? (ti ? 1 : -1) : 0;
                    nx[((c + ki + s - t) >> 1) + 2] += v; any = 1;
                }
            }
        }
        if (!any) continue;
        Aut a2 = *au;
        u32 t2 = tau | ((u32)bi << i);
        if (!aut_advance(&a2, i, t2) && !g_nocut) { g_cut++; continue; }
        dfs(i + 1, nx, t2, w + bi, &a2);
    }
}

#ifndef PAIR_CALC_NO_MAIN
static int pair_main(int argc, char **argv) {
    if (argc < 7) { fprintf(stderr, "usage: %s D3 D11 DELTA Y3 ETA BETA [MAXTAU] [-o FILE]\n", argv[0]); return 2; }
    u32 y3;
    g_d3 = (u32)strtoul(argv[1], NULL, 16); g_d11 = (u32)strtoul(argv[2], NULL, 16); g_delta = (u32)strtoul(argv[3], NULL, 16);
    y3 = (u32)strtoul(argv[4], NULL, 16); g_eta = (u32)strtoul(argv[5], NULL, 16); g_beta = (u32)strtoul(argv[6], NULL, 16);
    g_cap = 22; const char *outf = NULL;
    for (int i = 7; i < argc; i++) {
        if (!strcmp(argv[i], "-o") && i + 1 < argc) outf = argv[++i];
        else if (!strcmp(argv[i], "-y11") && i + 1 < argc) { g_y11 = (u32)strtoul(argv[++i], NULL, 16); g_have_y11 = 1; }
        else if (!strcmp(argv[i], "-sub") && i + 2 < argc) { g_xmask = (u32)strtoul(argv[i + 1], NULL, 16); g_xval = (u32)strtoul(argv[i + 2], NULL, 16); i += 2; }
        else g_cap = atoi(argv[i]);
    }
    u32 x1 = rol(g_eta, ROT1), x5 = rol(g_beta, ROT2);
    if (!in_s(g_d3, x1) || !in_s(g_d11, x5)) { printf("PAIR %08x %08x infeasible\n", g_eta, g_beta); return 0; }
    int we = wtl(x1) + __builtin_popcount(g_xmask), wb = wtl(x5);    /* a sub-class counts as a smaller class */
    u32 p = g_beta ^ ror(g_eta, ROTD);
    g_neps = 0;
    if ((__builtin_popcount(p) & 1) == 0) {
        u32 s = 0;
        for (int i = 0; i < WBITS - 1; i++) if (((s >> i) & 1) ^ ((p >> i) & 1)) s |= 1u << (i + 1);
        g_eps[0] = s; g_eps[1] = s ^ WMASK; g_neps = 2;
    }
    if (g_neps == 0) { printf("PAIR %08x %08x wt_eta %d wt_beta %d: no eps (odd weight)  class-rate part 0\n", g_eta, g_beta, we, wb); return 0; }
    double c0[6] = {0, 0, 1, 0, 0, 0};
    { Aut a0; aut_init(&a0); g_nocut = getenv("H8_NOCUT") != NULL; if (ROTD != 1) { fprintf(stderr, "ROTD must be 1\n"); return 2; } dfs(0, c0, 0, 0, &a0); }
    double total = 0.0, best = 0.0, p1sum = 0.0; long positive = 0, sampled = 0;
    #pragma omp parallel
    {
        Scratch sc; scratch_init(&sc);
        #pragma omp for schedule(dynamic, 4) reduction(+:total, positive, sampled, p1sum)
        for (long i = 0; i < (long)nouts; i++) {
            u64 rs = 0x243F6A8885A308D3ull ^ ((u64)outs[i].tau << 32) ^ outs[i].eps ^ ((u64)g_eta << 16);
            Result r = n3x(g_d3, y3, outs[i].tau, outs[i].eps, g_eta, &sc, &rs, g_xmask, g_xval);
            outs[i].n3 = r.n;
            p1sum += exp2(outs[i].lp1);
            if (r.n > 0.0) { double t = exp2(outs[i].lp1) * r.n; total += t; positive++; sampled += r.sampled; }
        }
        scratch_free(&sc);
    }
    for (size_t i = 0; i < nouts; i++) { double t = outs[i].n3 > 0 ? exp2(outs[i].lp1) * outs[i].n3 : 0.0; if (t > best) best = t; }
    double xtotal = 0.0, xbest = 0.0, xp1 = 0.0; long skipped = 0;
    if (g_have_y11) {
        #pragma omp parallel
        {
            u32 *la = malloc(CAP_LIST * sizeof(u32)), *lb = malloc(CAP_LIST * sizeof(u32));
            #pragma omp for schedule(dynamic, 1) reduction(+:xtotal, xp1, skipped)
            for (long i = 0; i < (long)nouts; i++) {
                if (outs[i].n3 <= 0.0) continue;
                double p = e1_exact(g_d11, g_delta, g_y11, g_beta, outs[i].tau, outs[i].eps, la, lb);
                if (p < 0.0) { skipped++; p = exp2(outs[i].lp1); }
                { outs[i].lp1 = p > 0.0 ? log2(p) : -999.0; if (i < (1 << 20)) g_px[i] = p; }
                xtotal += p * outs[i].n3; xp1 += p;
            }
            free(la); free(lb);
        }
        for (size_t i = 0; i < nouts; i++) { double t = outs[i].n3 > 0 ? exp2(outs[i].lp1) * outs[i].n3 : 0.0; if (t > xbest) xbest = t; }
    }
    double part = total * exp2((double)(we - wb));
    printf("PAIR %08x %08x wt_eta %d wt_beta %d cap %d taus %llu passing %zu positive %ld sampled %ld  E1 probability of passing 2^%.1f  "
           "class-rate part %.1f (log2 %.2f)  largest share %.2f\n", g_eta, g_beta, we, wb, g_cap, ntau, nouts, positive, sampled,
           p1sum > 0 ? log2(p1sum) : 0.0, part, part > 0 ? log2(part) : 0.0, total > 0 ? best / total : 0.0);
    if (g_have_y11) {
        double xpart = xtotal * exp2((double)(we - wb));
        printf("EXACT-E1 %08x %08x Y11 %08x: E1 probability of the positive outcomes 2^%.1f  class-rate part %.1f (log2 %.2f)  largest share %.2f  formula fallbacks %ld\n",
               g_eta, g_beta, g_y11, xp1 > 0 ? log2(xp1) : 0.0, xpart, xpart > 0 ? log2(xpart) : 0.0, xtotal > 0 ? xbest / xtotal : 0.0, skipped);
    }
    if (outf) {
        FILE *f = strcmp(outf, "-") ? fopen(outf, "w") : stdout;
        for (size_t i = 0; i < nouts; i++)
            if (outs[i].n3 > 0.0) fprintf(f, "OUT %08x %08x log2P1 %.2f log2N3 %.2f E1 %.0f N3 %.0f\n", outs[i].tau, outs[i].eps, outs[i].lp1, log2(outs[i].n3), i < (size_t)(1 << 20) && outs[i].lp1 > -900.0 ? g_px[i] * exp2(96.0 - __builtin_popcount(rol(g_beta, ROT2) & LOWBITS)) : 0.0, outs[i].n3);
        if (f != stdout) fclose(f);
    }
    return 0;
}

int main(int argc, char **argv) {
    if (argc < 8) { fprintf(stderr, "usage: %s D3 D11 DELTA Y3 ETA BETAFILE Y11\n", argv[0]); return 2; }
    FILE *bf = fopen(argv[6], "r");
    if (!bf) { perror(argv[6]); return 2; }
    char line[256], beta[32];
    static char cap[] = "31", oy[] = "-y11", oo[] = "-o", dash[] = "-";
    while (fgets(line, sizeof line, bf)) {
        if (sscanf(line, "%31s", beta) != 1) continue;
        nouts = 0; ntau = 0; g_neps = 0; g_cut = 0; g_have_y11 = 0; g_xmask = 0; g_xval = 0;   /* the state main() starts from */
        char *av[] = {argv[0], argv[1], argv[2], argv[3], argv[4], argv[5], beta, cap, oy, argv[7], oo, dash, NULL};
        int rc = pair_main(12, av);
        printf("DONE %s exit %d\n", beta, rc);
        fflush(stdout);
    }
    fclose(bf);
    return 0;
}
#endif
