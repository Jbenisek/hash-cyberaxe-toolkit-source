/* Complete enumeration at 8-bit words against the rule counter WITH A SUB-CLASS (cube) and with rules that have
 * parities of three bits. Research scratch of research/pkg7/count, not submitted.
 * It is rule_bf.c of research/h8/rule_exact with three changes:
 *   1. every class eta of a case gets a random cube: 0 to 3 extra fixed bits of e1 = Y3 + Y4 among the bits that the
 *      class leaves free (the top bit included), with random values; the enumeration keeps only the Y4 of the cube,
 *      and the counter is called with the same cube (the pair xmask, xval of n3r_orig / n3r_proj / n3x; in part B
 *      through s_xmask, s_xval of pair_calc_sub.c, the variables that the option -cube sets at 32 bits);
 *   2. six rules per case instead of four: single bits; XORs of two bits; mixed; mixed inside one class's eta;
 *      parities of three bits; "package-like" (3 to 6 conditions of weight 1, 2 or 3);
 *   3. empty outcomes are sampled 1 in 16 instead of 1 in 64 (a cube empties outcomes that the class has).
 *
 *   gcc -O2 -fopenmp -DWBITS=8 -o sub_bf8 sub_bf.c -lm          (rotations 4, 3, 2, 1 as in r2_e3count.c)
 *   ./sub_bf8 CASES_A CASES_B [seed]          H8_NOCUT=1 in the environment: the unpruned search of pair_calc.c
 *                                             SUB_BF_NOCUBE=1: no cube anywhere (must behave as rule_bf.c)
 *
 * PART A (side 3 alone, per outcome): every quadruple (Y4, h1, Y9, w8) with Y4 in the cube is run through the two
 * executions of E3 written out from the definition of G; per outcome (eta, tau, eps) the number of quadruples and,
 * per rule, the number whose h1 satisfies the rule. n3r_orig(), n3r_proj() (both walks) and the total of n3x() must
 * return exactly these numbers.
 * PART B (the whole event, per class and beta): side 1 by enumeration of every triple (d1, b1, a2); the number of
 * 7-tuples in Z with Y4 in the cube, in all and per rule, against count_beta() of pair_calc_sub.c, the same code as
 * at 32 bits, for every class and all 256 betas.
 */
#define RULE_NO_MAIN
#include "pair_calc_sub.c"

#if WBITS != 8
#error "build with -DWBITS=8"
#endif
#define NR 6
#define NW 256u
#define NSUB 8

static void random_rule(Rule *r, u64 *rs, int kind, u32 inside) {
    r->nc = 0; r->support = 0;
    int n = kind == 5 ? 3 + (int)(rnd(rs) % 4) : 1 + (int)(rnd(rs) % 3);
    u32 pool = (kind == 3 && __builtin_popcount(inside) >= 2) ? inside : WMASK;
    for (int c = 0; c < n; c++) {
        int wt = kind == 0 ? 1 : kind == 1 ? 2 : kind == 4 ? 3 : kind == 5 ? 1 + (int)(rnd(rs) % 3) : 1 + (int)(rnd(rs) & 1);
        if (wt > __builtin_popcount(pool)) wt = __builtin_popcount(pool);
        u32 m = 0;
        while (__builtin_popcount(m) < wt) {
            int b = (int)(rnd(rs) % WBITS);
            if ((pool >> b) & 1) m |= 1u << b;
        }
        r->mask[r->nc] = m; r->val[r->nc] = (int)(rnd(rs) & 1); r->support |= m; r->nc++;
    }
}

static u64 *g_cnt = NULL;                 /* [(ei * 256 + tau) * 256 + eps] * (NR + 1): total, then per rule */
static int g_etaidx[NW], g_neta;
static u32 g_etas[NW], g_subm[NW], g_subv[NW];
static u32 *g_h1 = NULL;                  /* [(beta * 256 + tau) * 256 + eps] */
static long g_identity_bad = 0, g_cubes = 0, g_cubes_nonempty = 0, g_members_all = 0, g_members_cube = 0;
static int g_nocube = 0;

static void bf_side3(u32 d3, u32 y3, u64 *rs) {
    for (u32 i = 0; i < NW; i++) g_etaidx[i] = -1;
    g_neta = 0;
    for (u32 y4 = 0; y4 < NW; y4++) {
        u32 e1 = (y3 + y4) & WMASK, e1b = (y3 + d3 + y4) & WMASK, eta = ror(e1 ^ e1b, ROT1);
        if (g_etaidx[eta] < 0) { g_etaidx[eta] = g_neta; g_etas[g_neta++] = eta; }
    }
    for (int ei = 0; ei < g_neta; ei++) {             /* the cube of each class */
        u32 e1m = rol(g_etas[ei], ROT1) & LOWBITS, freeb = ~e1m & WMASK, m = 0;
        int want = g_nocube ? 0 : (int)(rnd(rs) % 4);
        if (want > __builtin_popcount(freeb)) want = __builtin_popcount(freeb);
        while (__builtin_popcount(m) < want) {
            int b = (int)(rnd(rs) % WBITS);
            if ((freeb >> b) & 1) m |= 1u << b;
        }
        g_subm[ei] = m; g_subv[ei] = (u32)rnd(rs) & m;
        g_cubes++; g_cubes_nonempty += m != 0;
    }
    for (u32 y4 = 0; y4 < NW; y4++) {
        u32 e1 = (y3 + y4) & WMASK, e1b = (y3 + d3 + y4) & WMASK, eta = ror(e1 ^ e1b, ROT1);
        int ei = g_etaidx[eta];
        g_members_all++; g_members_cube += (e1 & g_subm[ei]) == g_subv[ei];
    }
    free(g_cnt);
    g_cnt = calloc((size_t)g_neta * NW * NW * (NR + 1), sizeof(u64));
    unsigned char pm[NW];
    for (u32 h = 0; h < NW; h++) {
        pm[h] = 0;
        for (int r = 0; r < NR; r++) if (rule_ok(&g_rule[r], h)) pm[h] |= (unsigned char)(1u << r);
    }
    long bad = 0;
    #pragma omp parallel for schedule(dynamic, 1) reduction(+:bad)
    for (int ei = 0; ei < g_neta; ei++) {
        u64 *base = g_cnt + (size_t)ei * NW * NW * (NR + 1);
        for (u32 y4 = 0; y4 < NW; y4++) {
            u32 e1 = (y3 + y4) & WMASK, e1b = (y3 + d3 + y4) & WMASK, eta = ror(e1 ^ e1b, ROT1);
            if (g_etaidx[eta] != ei) continue;
            if ((e1 & g_subm[ei]) != g_subv[ei]) continue;            /* Y4 outside the cube */
            for (u32 h1 = 0; h1 < NW; h1++) {
                u32 h1b = h1 ^ eta;
                unsigned m = pm[h1];
                for (u32 y9 = 0; y9 < NW; y9++) {
                    u32 g1 = (y9 + h1) & WMASK, g1b = (y9 + h1b) & WMASK;
                    u32 f1 = ror(y4 ^ g1, ROT2), f1b = ror(y4 ^ g1b, ROT2);
                    for (u32 w8 = 0; w8 < NW; w8++) {
                        u32 e2 = (e1 + f1 + w8) & WMASK, e2b = (e1b + f1b + w8) & WMASK;
                        u32 h2 = ror(h1 ^ e2, ROT3), h2b = ror(h1b ^ e2b, ROT3);
                        u32 g2 = (g1 + h2) & WMASK, g2b = (g1b + h2b) & WMASK;
                        u32 f2 = ror(f1 ^ g2, ROT4), f2b = ror(f1b ^ g2b, ROT4);
                        u32 tau = g2 ^ g2b, eps = e2 ^ e2b;
                        if ((h2 ^ h2b) != ror(eta ^ eps, ROT3)) bad++;
                        if ((f2 ^ f2b) != ror(tau, ROT3)) continue;
                        u64 *c = base + ((size_t)tau * NW + eps) * (NR + 1);
                        c[0]++;
                        for (int r = 0; r < NR; r++) if ((m >> r) & 1) c[1 + r]++;
                    }
                }
            }
        }
    }
    g_identity_bad += bad;
}

static void bf_side1(u32 d11, u32 y11, u32 delta) {
    if (!g_h1) g_h1 = malloc((size_t)NW * NW * NW * sizeof(u32));
    memset(g_h1, 0, (size_t)NW * NW * NW * sizeof(u32));
    for (u32 d1 = 0; d1 < NW; d1++) {
        u32 c1 = (y11 + d1) & WMASK, c1b = (y11 + d11 + d1) & WMASK, beta = ror(c1 ^ c1b, ROT2);
        for (u32 b1 = 0; b1 < NW; b1++) {
            u32 b1b = b1 ^ beta;
            for (u32 a2 = 0; a2 < NW; a2++) {
                u32 a2b = (a2 + b1b - b1 + delta) & WMASK, tau = a2 ^ a2b;
                u32 d2 = ror(d1 ^ a2, ROT3), d2b = ror(d1 ^ a2b, ROT3);
                u32 c2 = (c1 + d2) & WMASK, c2b = (c1b + d2b) & WMASK, eps = c2 ^ c2b;
                u32 b2 = ror(b1 ^ c2, ROT4), b2b = ror(b1b ^ c2b, ROT4);
                if ((d2 ^ d2b) != ror(tau, ROT3) || (b2 ^ b2b) != ror(beta ^ eps, ROT4)) g_identity_bad++;
                g_h1[((size_t)beta * NW + tau) * NW + eps]++;
            }
        }
    }
}

static void make_rules(u64 *rs, u32 d3, u32 y3) {
    u32 e1 = y3 & WMASK, e1b = (y3 + d3) & WMASK;
    u32 inside = ror(e1 ^ e1b, ROT1) & LOWBITS;        /* eta of the class of Y4 = 0, below the top bit */
    g_nrule = NR;
    for (int r = 0; r < NR; r++) random_rule(&g_rule[r], rs, r, inside);
}

static int rule_has_wt3(const Rule *r) {
    for (int c = 0; c < r->nc; c++) if (__builtin_popcount(r->mask[c]) >= 3) return 1;
    return 0;
}

int main(int argc, char **argv) {
    int cases_a = argc > 1 ? atoi(argv[1]) : 3, cases_b = argc > 2 ? atoi(argv[2]) : 3;
    u64 rs = argc > 3 ? strtoull(argv[3], NULL, 0) : 1;
    g_nocut = getenv("H8_NOCUT") != NULL;
    g_nocube = getenv("SUB_BF_NOCUBE") != NULL;
    g_mode = 3;
    static const u64 zero[NR + 1] = {0};
    if (!g_sc_ok) { scratch_init(&g_sc); g_sc_ok = 1; }

    /* ---- part A ---- */
    long a_out = 0, a_ok[3] = {0, 0, 0}, a_bad[3] = {0, 0, 0}, a_x_ok = 0, a_x_bad = 0, a_zero_ok = 0, a_zero_bad = 0;
    long a_rule_cmp = 0, a_rule_bad = 0, a_mixed = 0, a_all = 0, a_none = 0, a_free = 0, a_status = 0, shown = 0;
    long a_out_cube = 0, a_wt3 = 0, a_wt3_split = 0;
    double a_sol = 0.0;
    for (int c = 0; c < cases_a; c++) {
        u32 d3 = (u32)rnd(&rs) & WMASK, y3 = (u32)rnd(&rs) & WMASK;
        if (d3 == 0) { c--; continue; }
        make_rules(&rs, d3, y3);
        bf_side3(d3, y3, &rs);
        for (u32 eta = 0; eta < NW; eta++) {
            int ei = g_etaidx[eta];
            u32 xm = ei >= 0 ? g_subm[ei] : 0, xv = ei >= 0 ? g_subv[ei] : 0;
            for (u32 tau = 0; tau < NW; tau++) for (u32 eps = 0; eps < NW; eps++) {
                const u64 *v = ei >= 0 ? g_cnt + (((size_t)ei * NW + tau) * NW + eps) * (NR + 1) : zero;
                if (v[0] == 0 && (rnd(&rs) & 15)) continue;
                ResR res[3];
                res[0] = n3r_orig(d3, y3, tau, eps, eta, xm, xv);
                N3R_WALK = 1; res[1] = n3r_proj(d3, y3, tau, eps, eta, xm, xv);      /* walk from the df1 list */
                N3R_WALK = 2; res[2] = n3r_proj(d3, y3, tau, eps, eta, xm, xv);      /* walk from the class patterns */
                N3R_WALK = 0;
                u64 r2 = 0x243F6A8885A308D3ull ^ ((u64)tau << 32) ^ eps ^ ((u64)eta << 16);
                Result x = n3x(d3, y3, tau, eps, eta, &g_sc, &r2, xm, xv);
                a_status += (res[0].status != 0) + (res[1].status != 0) + (res[2].status != 0);
                if (v[0] == 0) {
                    if (res[0].n == 0 && res[1].n == 0 && res[2].n == 0 && x.n == 0.0) a_zero_ok++; else a_zero_bad++;
                    continue;
                }
                a_out++; a_sol += (double)v[0]; a_out_cube += xm != 0;
                if (!x.sampled && x.n == (double)v[0]) a_x_ok++; else a_x_bad++;
                for (int f = 0; f < 3; f++) {
                    int good = res[f].n == (big)v[0];
                    for (int r = 0; r < NR; r++) {
                        a_rule_cmp++;
                        if (res[f].pass[r] != (big)v[1 + r]) { a_rule_bad++; good = 0; }
                    }
                    if (good) a_ok[f]++;
                    else {
                        a_bad[f]++;
                        if (shown++ < 4) printf("MISMATCH part A function %d d3 %02x y3 %02x eta %02x cube %02x/%02x tau %02x eps %02x: enumeration %llu counter %llu\n",
                                                f, d3, y3, eta, xm, xv, tau, eps, (unsigned long long)v[0], (unsigned long long)res[f].n);
                    }
                }
                for (int r = 0; r < NR; r++) {
                    int split = !(v[1 + r] == v[0] || v[1 + r] == 0);
                    if (v[1 + r] == v[0]) a_all++; else if (v[1 + r] == 0) a_none++; else a_mixed++;
                    if (g_rule[r].support & ~(eta & LOWBITS) & WMASK) a_free++;
                    if (rule_has_wt3(&g_rule[r])) { a_wt3++; a_wt3_split += split; }
                }
            }
        }
    }
    printf("A side 3 with rules and cubes at %d-bit words%s: %d cases; outcomes with solutions %ld (in a class with a proper cube %ld; solutions %.0f): "
           "n3r_orig equal %ld different %ld, n3r_proj from the df1 list equal %ld different %ld, n3r_proj from the class patterns equal %ld different %ld, "
           "n3x total equal %ld different %ld; empty outcomes sampled: agree %ld disagree %ld; not counted %ld\n",
           WBITS, g_nocube ? " (NO cube)" : "", cases_a, a_out, a_out_cube, a_sol, a_ok[0], a_bad[0], a_ok[1], a_bad[1], a_ok[2], a_bad[2],
           a_x_ok, a_x_bad, a_zero_ok, a_zero_bad, a_status);
    printf("A rule counts compared (outcome, rule, function) %ld, different %ld; (outcome, rule) pairs: all pass %ld, none %ld, "
           "split %ld; with a rule bit outside eta below bit %d: %ld; with a three-bit parity in the rule %ld (split %ld)\n",
           a_rule_cmp, a_rule_bad, a_all, a_none, a_mixed, WBITS - 1, a_free, a_wt3, a_wt3_split);

    /* ---- part B ---- */
    long b_cmp = 0, b_bad = 0, b_pos = 0, b_rulepos = 0, b_split = 0, b_e1cmp = 0, b_e1bad = 0, b_both_eq = 0, b_both_df = 0;
    long b_notc = 0, b_bfout = 0, b_ctrout = 0, b_classes = 0, b_infeasible_pos = 0, b_proj = 0, b_listed = 0, b_pos_cube = 0;
    /* RULE_BF_CAPWORK=LOG2 in the environment: part B with the cap on the triples of n3r_orig, as the 32-bit runs
       use it (-capwork), so that the outcomes above it are counted by n3r_proj alone */
    if (getenv("RULE_BF_CAPWORK")) N3R_CAP_WORK = exp2(atof(getenv("RULE_BF_CAPWORK")));
    big *bf = malloc((size_t)NW * NW * (NR + 1) * sizeof(big));
    long double b_z = 0.0L;
    for (int c = 0; c < cases_b * NSUB; c++) {
        /* a case = one side 3 (D3, Y3, rules, cubes) with NSUB different sides 1 (D11, Y11, delta) */
        static u32 d3, y3;
        if (c % NSUB == 0) {
            do { d3 = (u32)rnd(&rs) & WMASK; y3 = (u32)rnd(&rs) & WMASK; } while (d3 == 0);
            make_rules(&rs, d3, y3);
            bf_side3(d3, y3, &rs);
        }
        u32 d11, y11 = (u32)rnd(&rs) & WMASK;
        do d11 = (u32)rnd(&rs) & WMASK; while (d11 == 0);
        u32 dabs = 2u * (1u + (u32)(rnd(&rs) % 8)), delta = (rnd(&rs) & 1) ? dabs : ((NW - dabs) & WMASK);
        bf_side1(d11, y11, delta);
        b_classes += g_neta;
        memset(bf, 0, (size_t)NW * NW * (NR + 1) * sizeof(big));
        for (int ei = 0; ei < g_neta; ei++) {
            u32 eta = g_etas[ei];
            for (u32 tau = 0; tau < NW; tau++) for (u32 eps = 0; eps < NW; eps++) {
                const u64 *v = g_cnt + (((size_t)ei * NW + tau) * NW + eps) * (NR + 1);
                if (v[0] == 0) continue;
                for (u32 beta = 0; beta < NW; beta++) {
                    if (ror(beta ^ eps, ROT4) != ror(eta ^ eps, ROT3)) continue;      /* fourth equality of Z */
                    u32 h = g_h1[((size_t)beta * NW + tau) * NW + eps];
                    if (!h) continue;
                    b_bfout++;
                    big *s = bf + ((size_t)ei * NW + beta) * (NR + 1);
                    for (int r = 0; r <= NR; r++) s[r] += (big)h * (big)v[r];
                }
            }
        }
        for (int ei = 0; ei < g_neta; ei++) {
            u32 eta = g_etas[ei];
            s_xmask = g_subm[ei]; s_xval = g_subv[ei];               /* what the option -cube sets at 32 bits */
            for (u32 beta = 0; beta < NW; beta++) {
                long rc = count_beta(d3, d11, delta, y3, y11, eta, beta);
                big s[NR + 1];
                for (int r = 0; r <= NR; r++) s[r] = 0;
                if (rc >= 0) for (size_t i = 0; i < g_noutr; i++) {
                    const OutR *o = &g_outr[i];
                    if (o->n3st != 0 || o->e1st != 0) b_notc++;
                    b_listed++; b_proj += o->fn;
                    if (o->both == 1) b_both_eq++; else if (o->both == 0) b_both_df++;
                    if (o->n3 > 0) {
                        b_e1cmp++;
                        if (o->e1 != (big)g_h1[((size_t)beta * NW + o->tau) * NW + o->eps]) b_e1bad++;
                        if (o->e1 > 0) b_ctrout++;
                    }
                    s[0] += o->e1 * o->n3;
                    for (int r = 0; r < NR; r++) s[1 + r] += o->e1 * o->pass[r];
                }
                const big *t = bf + ((size_t)ei * NW + beta) * (NR + 1);
                if (rc < 0 && t[0] != 0) b_infeasible_pos++;
                if (t[0] != 0) { b_pos++; b_z += (long double)t[0]; b_pos_cube += s_xmask != 0; }
                for (int r = 0; r <= NR; r++) {
                    b_cmp++;
                    if (s[r] != t[r]) {
                        b_bad++;
                        if (shown++ < 8) printf("MISMATCH part B d3 %02x y3 %02x d11 %02x y11 %02x delta %02x eta %02x cube %02x/%02x beta %02x column %d: enumeration %.0Lf counter %.0Lf\n",
                                                d3, y3, d11, y11, delta, eta, s_xmask, s_xval, beta, r, (long double)t[r], (long double)s[r]);
                    }
                    if (r > 0 && t[0] != 0) { b_rulepos++; if (t[r] != 0 && t[r] != t[0]) b_split++; }
                }
            }
        }
    }
    s_xmask = 0; s_xval = 0;
    printf("B whole event at %d-bit words%s%s: %d sides 3 with 8 sides 1 each, %ld classes in all; (class, beta) pairs with Z-tuples %ld (in a class with a proper cube %ld; 7-tuples in Z in all %.0Lf); "
           "integers compared (class, beta, total or rule) %ld, different %ld; rule counts on pairs with Z-tuples %ld, of them split by the rule %ld\n",
           WBITS, g_nocut ? " (unpruned search)" : "", g_nocube ? " (NO cube)" : "", cases_b, b_classes, b_pos, b_pos_cube, b_z, b_cmp, b_bad, b_rulepos, b_split);
    printf("B outcomes with a nonzero product: enumeration %ld, counter %ld; E1 against the side-1 histogram: compared %ld, different %ld; "
           "n3r_orig against n3r_proj: equal %ld, different %ld; not counted %ld; pairs the counter calls impossible that have Z-tuples %ld; "
           "identities of the differences violated in the enumeration %ld\n",
           b_bfout, b_ctrout, b_e1cmp, b_e1bad, b_both_eq, b_both_df, b_notc, b_infeasible_pos, g_identity_bad);
    printf("B outcomes listed by the counter %ld, of them counted by n3r_proj alone (n3r_orig above its cap of 2^%.0f triples) %ld\n",
           b_listed, N3R_CAP_WORK < 1e299 ? log2(N3R_CAP_WORK) : 999.0, b_proj);
    printf("cubes: classes %ld, with a proper cube %ld; members of the classes %ld, inside the cubes %ld\n",
           g_cubes, g_cubes_nonempty, g_members_all, g_members_cube);
    int fail = a_bad[0] || a_bad[1] || a_bad[2] || a_x_bad || a_zero_bad || a_rule_bad || a_status || b_bad || b_e1bad || b_both_df || b_notc
               || b_infeasible_pos || g_identity_bad || b_bfout != b_ctrout;
    printf("RESULT %s\n", fail ? "DIFFERENCES FOUND" : "zero differences");
    return fail;
}
