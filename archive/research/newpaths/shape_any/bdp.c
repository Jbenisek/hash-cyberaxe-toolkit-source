/* bdp.c - promotion-aware upper-bound search (shape_any agent).
   Promoted words P (any words of the base system) become sub-family constants; constants are propagated
   (an equation with one unknown fixes it, with none it is a condition on constants).  F' = N' - E' must stay
   >= Fmin (sub-family of 2^(32 F') members) and the reduced system must be consistent (matching saturates it).
   For each P the width is estimated by randomized greedy elimination; P is improved by annealing.
   Usage: bdp <base.sys> <Fmin> <iters> <seed> [initial,promoted,names]
*/
#define NOMAIN
#include "bd.c"

static int bN, bE;
static char bvname[128][24], bename[128][24];
static int bek[128], bev[128][4];

static void save_base(void) {
    bN = N; bE = E;
    memcpy(bvname, vname, sizeof vname); memcpy(bename, ename, sizeof ename);
    memcpy(bek, ek, sizeof ek); memcpy(bev, ev, sizeof ev);
}
static int apply_promo(u128 P, u128 *Peff) {
    u128 C = P; int alive[128];
    for (int e = 0; e < bE; e++) alive[e] = 1;
    for (int ch = 1; ch;) {
        ch = 0;
        for (int e = 0; e < bE; e++) if (alive[e]) {
            int cnt = 0, last = -1;
            for (int j = 0; j < bek[e]; j++) if (!(C >> bev[e][j] & 1)) { cnt++; last = bev[e][j]; }
            if (cnt == 0) { alive[e] = 0; ch = 1; }
            else if (cnt == 1) { C |= BIT(last); alive[e] = 0; ch = 1; }
        }
    }
    int nid[128];
    N = 0;
    for (int v = 0; v < bN; v++) { if (C >> v & 1) nid[v] = -1; else { nid[v] = N; strcpy(vname[N], bvname[v]); N++; } }
    for (int v = 0; v < N; v++) occ[v] = 0;
    E = 0; ALLE = 0;
    for (int e = 0; e < bE; e++) if (alive[e]) {
        ek[E] = 0; eqv[E] = 0;
        for (int j = 0; j < bek[e]; j++) { int v = nid[bev[e][j]]; if (v >= 0) { ev[E][ek[E]++] = v; eqv[E] |= BIT(v); occ[v] |= BIT(E); } }
        strcpy(ename[E], bename[e]); ALLE |= BIT(E); E++;
    }
    F = N - E;
    *Peff = C;
    if (rho(ALLE, 0) != 0) return -999;      /* over-determined: promoted values not free */
    return F;
}
static double tree_score(void) { double s = 0; for (int i = 0; i < nn; i++) if (nd[i].l >= 0) s += __builtin_pow(8.0, nd[i].J); return s; }
static int eval_P(u128 P, int Fmin, double *score, int tries) {
    u128 Pe; int f = apply_promo(P, &Pe);
    if (f < Fmin) return 999;
    int bw = 999; double bs = 1e300;
    for (int t = 0; t < tries; t++) {
        run_elim(t == 0 ? 0 : (int)(rnd() % 3000));
        int s, w = treewidth_of(nd, nn, &s);
        double sc = tree_score();
        if (w < bw || (w == bw && sc < bs)) { bw = w; bs = sc; }
    }
    *score = bs;
    return bw;
}

/* local search for the cheapest balanced neck with promotions: min rho_P(A, B(A)) with R/3 <= |A| < 2R/3 over
   remaining equations, slack <= Smax.  Returns best value; prints the witness.  (upper bound on the SAT LB) */
static int nid_of[128];
static int cut_eval(u128 P, u128 Abase, int Fmin, int *ok) {
    u128 Pe; int f = apply_promo(P, &Pe);
    *ok = 0;
    if (f < Fmin) return 999;
    /* map base equations to reduced indices by name order: apply_promo keeps base order of alive equations */
    u128 A = 0; int k = 0;
    for (int e = 0; e < bE; e++) {
        int alive = 0;
        for (int j = 0; j < bek[e]; j++) if (!(Pe >> bev[e][j] & 1)) { alive = 1; break; }
        /* alive in reduced system iff >= 2 unknowns originally... use name match instead */
        (void)alive;
    }
    for (int i = 0; i < E; i++) { for (k = 0; k < bE; k++) if (!strcmp(ename[i], bename[k])) break; if (Abase >> k & 1) A |= BIT(i); }
    int n = pc(A);
    if (3 * n < E || 3 * n >= 2 * E) return 999;
    *ok = 1;
    return rho(A, Bof(A));
}
static void run_cutp(int Fmin, long iters, int restarts) {
    int gbest = 999;
    for (int rr = 0; rr < restarts; rr++) {
        u128 P = 0, A = 0;
        /* random start: random promotions until F' hits Fmin, random connected A of ~half */
        for (int t = 0; t < 400; t++) { int v = (int)(rnd() % (unsigned)bN); u128 Q = P | BIT(v); u128 Pe; if (apply_promo(Q, &Pe) >= Fmin) P = Q; }
        int tgt = bE / 2; A = BIT(rnd() % (unsigned)bE);
        while (pc(A) < tgt) { int e = (int)(rnd() % (unsigned)bE); for (int j = 0; j < bek[e]; j++) { int ok = 0; for (int g = 0; g < bE; g++) if ((A >> g & 1)) for (int i = 0; i < bek[g]; i++) if (bev[g][i] == bev[e][j]) ok = 1; if (ok) { A |= BIT(e); break; } } }
        int ok; int cur = cut_eval(P, A, Fmin, &ok); if (!ok) cur = 999;
        int best = cur; u128 bP = P, bA = A;
        for (long it = 0; it < iters; it++) {
            double T = 1.5 * (1.0 - (double)it / iters) + 0.05;
            u128 P2 = P, A2 = A; int mv = (int)(rnd() % 4);
            if (mv <= 1) A2 ^= BIT(rnd() % (unsigned)bE);
            else if (mv == 2) { int a = (int)(rnd() % (unsigned)bN); P2 ^= BIT(a); }
            else { int a = (int)(rnd() % (unsigned)bN), b = (int)(rnd() % (unsigned)bN); if ((P2 >> a & 1) && !(P2 >> b & 1)) P2 ^= BIT(a) | BIT(b); else continue; }
            int c = cut_eval(P2, A2, Fmin, &ok);
            if (!ok) continue;
            if (c <= cur || (double)(rnd() % 1000000) / 1e6 < __builtin_exp((cur - c) / T)) {
                P = P2; A = A2; cur = c;
                if (c < best) { best = c; bP = P; bA = A; }
            }
        }
        u128 Pe; int f = apply_promo(bP, &Pe);
        printf("restart %d: best neck rho %d  (F'=%d, |P|=%d)  P=", rr, best, f, pc(bP));
        for (int v = 0; v < bN; v++) if (bP >> v & 1) printf("%s,", bvname[v]);
        printf("  A-calls:");
        char seen[64][8]; int ns = 0;
        for (int e = 0; e < bE; e++) if (bA >> e & 1) { char c[8]; int i = 0; while (bename[e][i] && bename[e][i] != ':' && i < 7) { c[i] = bename[e][i]; i++; } c[i] = 0; int k; for (k = 0; k < ns; k++) if (!strcmp(seen[k], c)) break; if (k == ns && ns < 64) { strcpy(seen[ns++], c); printf(" %s", c); } }
        printf("\n"); fflush(stdout);
        if (best < gbest) gbest = best;
    }
    printf("CUTP best neck over restarts: %d\n", gbest);
}

/* promotion annealing scored by the EXACT brick-level width (bd.c brick_width) */
static void run_brickp(int Fmin, long iters, u128 P) {
    brick_maxg = 12;
    double sc; u128 Pe; int f = apply_promo(P, &Pe);
    int w = f >= Fmin ? brick_width(&sc) : 999;
    double cur = w >= 999 ? 1e9 : w * 100.0 + __builtin_log(sc) / 10;
    int bw = w; u128 bP = P;
    printf("start: brick width %d (F'=%d, |P|=%d)\n", w, f, pc(P)); fflush(stdout);
    for (long it = 0; it < iters; it++) {
        double T = 3.0 * (1.0 - (double)it / iters) + 0.05;
        u128 Q = P; int mv = (int)(rnd() % 3);
        int a = (int)(rnd() % (unsigned)bN), b = (int)(rnd() % (unsigned)bN);
        if (mv == 0) { if (!(Q >> a & 1) || (Q >> b & 1)) continue; Q ^= BIT(a) | BIT(b); }
        else if (mv == 1) { if (Q >> b & 1) continue; Q |= BIT(b); }
        else { if (!(Q >> a & 1)) continue; Q ^= BIT(a); }
        f = apply_promo(Q, &Pe);
        if (f < Fmin) continue;
        double s2; int w2 = brick_width(&s2);
        if (w2 >= 999) continue;
        double c2 = w2 * 100.0 + __builtin_log(s2) / 10;
        if (c2 <= cur || (double)(rnd() % 1000000) / 1e6 < __builtin_exp((cur - c2) / T)) {
            P = Q; cur = c2;
            if (w2 < bw) {
                bw = w2; bP = P;
                printf("it %ld: brick width %d F'=%d |P|=%d groups E=%d P=", it, w2, f, pc(P), E);
                for (int v = 0; v < bN; v++) if (P >> v & 1) printf("%s,", bvname[v]);
                printf("\n"); fflush(stdout);
            }
        }
    }
    printf("BRICKP best brick width %d  P=", bw);
    for (int v = 0; v < bN; v++) if (bP >> v & 1) printf("%s,", bvname[v]);
    printf("\n");
}

int main(int argc, char **argv) {
    readsys(argv[1]); save_base();
    if (argc > 2 && !strcmp(argv[2], "brickp")) {
        rs ^= (uint64_t)atoll(argv[5]) * 0x9E3779B97F4A7C15ULL;
        u128 P = 0;
        if (argc > 6) { char buf[2048]; strncpy(buf, argv[6], sizeof buf - 1); buf[sizeof buf - 1] = 0;
            for (char *t = strtok(buf, ","); t; t = strtok(NULL, ",")) { int v; for (v = 0; v < bN; v++) if (!strcmp(bvname[v], t)) break; if (v < bN) P |= BIT(v); } }
        run_brickp(atoi(argv[3]), atol(argv[4]), P); return 0;
    }
    if (argc > 2 && !strcmp(argv[2], "cutp")) { rs ^= (uint64_t)atoll(argv[6]) * 0x9E3779B97F4A7C15ULL; run_cutp(atoi(argv[3]), atol(argv[4]), atoi(argv[5])); return 0; }
    int Fmin = atoi(argv[2]); long iters = atol(argv[3]); rs ^= (uint64_t)atoll(argv[4]) * 0x9E3779B97F4A7C15ULL;
    u128 P = 0;
    if (argc > 5) {
        char buf[2048]; strncpy(buf, argv[5], sizeof buf - 1); buf[sizeof buf - 1] = 0;
        for (char *t = strtok(buf, ","); t; t = strtok(NULL, ",")) {
            int v; for (v = 0; v < bN; v++) if (!strcmp(bvname[v], t)) break;
            if (v < bN) P |= BIT(v); else fprintf(stderr, "unknown %s\n", t);
        }
    }
    double sc; int w = eval_P(P, Fmin, &sc, 3);
    printf("base %s: N=%d E=%d F=%d; start |P|=%d width %d\n", argv[1], bN, bE, bN - bE, pc(P), w);
    fflush(stdout);
    u128 bestP = P; int bw = w; double bsc = sc, cur = (w >= 999 ? 1e9 : w * 100.0 + __builtin_log(sc) / 10);
    for (long it = 0; it < iters; it++) {
        double T = 3.0 * (1.0 - (double)it / iters) + 0.05;
        u128 Q = P; int mv = (int)(rnd() % 3);
        int a = (int)(rnd() % (unsigned)bN), b = (int)(rnd() % (unsigned)bN);
        if (mv == 0) { if (!(Q >> a & 1) || (Q >> b & 1)) continue; Q ^= BIT(a) | BIT(b); }
        else if (mv == 1) { if (Q >> b & 1) continue; Q |= BIT(b); }
        else { if (!(Q >> a & 1)) continue; Q ^= BIT(a); }
        double s2; int w2 = eval_P(Q, Fmin, &s2, 2);
        if (w2 >= 999) continue;
        double c2 = w2 * 100.0 + __builtin_log(s2) / 10;
        if (c2 <= cur || (double)(rnd() % 1000000) / 1e6 < __builtin_exp((cur - c2) / T)) {
            P = Q; cur = c2;
            if (w2 < bw || (w2 == bw && s2 < bsc)) {
                bw = w2; bsc = s2; bestP = P;
                u128 Pe; int f = apply_promo(P, &Pe);
                printf("it %ld: width %d F'=%d |P|=%d P=", it, w2, f, pc(P));
                for (int v = 0; v < bN; v++) if (P >> v & 1) printf("%s,", bvname[v]);
                printf("\n"); fflush(stdout);
            }
        }
    }
    /* final: longer evaluation of the best P */
    u128 Pe; int f = apply_promo(bestP, &Pe);
    printf("BEST width %d  F'=%d  |P|=%d  derived constants %d  remaining N=%d E=%d\nP=", bw, f, pc(bestP), pc(Pe) - pc(bestP), N, E);
    for (int v = 0; v < bN; v++) if (bestP >> v & 1) printf("%s,", bvname[v]);
    printf("\n");
    best_w = 1 << 30; best_sumexp = 1 << 30;
    for (int t = 0; t < 30; t++) { run_elim(t == 0 ? 0 : (int)(rnd() % 3000)); consider_best(); }
    int jh[64] = {0};
    for (int i = 0; i < best_nn; i++) if (best_nd[i].l >= 0 && best_nd[i].J < 64) jh[best_nd[i].J]++;
    printf("tree width %d, join-width histogram:", best_w);
    for (int x = 0; x < 64; x++) if (jh[x]) printf(" J%d:%d", x, jh[x]);
    printf("\n");
    printtree(best_nd, best_nn - 1, 0, stdout);
    return 0;
}
