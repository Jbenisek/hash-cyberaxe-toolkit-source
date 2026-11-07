/* Orchard Poseidon, r partial rounds: two-family collision attack with a proved success probability.
 * usage: twofam r seed [family wordhex]     (the optional pair forces the sampled point x, for tests)
 *        twofam selftest
 * One attempt: sample x uniformly from C_0 u C_1 (2p-1 inputs), y = H(x); for h = 0, 1: F_h(W) = f_h(W) - y (degree 5^(6+r)),
 * R = W^p mod F_h, G = gcd(F_h, R - W) = product of the distinct roots in F_p, remove the roots that are x itself, and
 * isolate one remaining root (split.c).  Every field operation, load, store, loop-control op and random word is counted. */
#include "attack.h"
#include "pallas_consts.h"
#include <time.h>
#include <math.h>

typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[32]; static int nst;
static snap_t cur; static clock_t tcur;
static size_t gpeak;
static void stage_begin(void) { cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
    printf("  %-44s arith=%14llu other=%14llu total=%14llu %7.1fs peak=%zu\n", name, (unsigned long long)snap_arith(s->d),
           (unsigned long long)(snap_total(s->d) - snap_arith(s->d)), (unsigned long long)snap_total(s->d), s->sec, s->peak);
    fflush(stdout);
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

static size_t degD(int r) { size_t D = 1; for (int i = 0; i < 6 + r; i++) D *= 5; return D; }

/* F = (f_h - y) / lead, monic of degree D, from D+1 .. N evaluations of the digest on the family at W = theta^k (k < N, N = 3 * 2^a >= D + 1) */
static void build_F(fp *F, const line_t *L, const fp *y, int r) {
    size_t D = degD(r);
    plan_t P = plan_for_len(D + 1, 1);
    size_t H = P.N;
    fp *buf = NEW_FP(H);
    fp theta, s, one;
    fp_set_one(&one);
    plan_theta(&P, &theta);
    s = one;
    for (size_t k = 0; k < H; k++) {
        fp F1;
        snap_t e0 = snap();
        tail_eval(&F1, L, &s, r);
        snap_restore(e0);
        X.perm += (uint64_t)poseidon_C(r);               /* one target-compression unit per evaluation of H */
        buf[layout_index(&P, k)] = F1;
        fp_mul(&s, &s, &theta);
        CTL(2 + 4);
    }
    ST(H); loopc(H);
    ntt_inv(&P, buf, D + 1);                              /* buf[k] = N f_k */
    fp invN, lead, il, sc, t;
    plan_invN(&P, &invN);
    fp_mul(&lead, &buf[D], &invN);                        /* leading coefficient of f_h */
    if (fp_is_zero(&lead)) { printf("leading coefficient is zero\n"); exit(78); }
    CTL(3);
    fp_inv(&il, &lead); CTL(INV_CTL);
    fp_mul(&sc, &invN, &il);
    for (size_t k = 0; k < D; k++) fp_mul(&F[k], &buf[k], &sc);
    fp_mul(&t, y, &il); fp_sub(&F[0], &F[0], &t);
    fp_set_one(&F[D]);
    LD(D + 1); ST(D + 1); loopc(D + 1);
    xfree(buf);
}

/* ---- 256-bit helpers (constants of the program: N = 2p - 1) */
static int lt256(const uint64_t a[4], const uint64_t b[4]) { for (int i = 3; i >= 0; i--) { if (a[i] != b[i]) return a[i] < b[i]; } return 0; }
static void sub256(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) { unsigned __int128 br = 0; for (int i = 0; i < 4; i++) { unsigned __int128 d = (unsigned __int128)a[i] - b[i] - (uint64_t)br; r[i] = (uint64_t)d; br = (d >> 64) & 1; } }
static void add1_256(uint64_t r[4], const uint64_t a[4]) { unsigned __int128 c = 1; for (int i = 0; i < 4; i++) { unsigned __int128 s = (unsigned __int128)a[i] + (uint64_t)c; r[i] = (uint64_t)s; c = s >> 64; } }

int main(int argc, char **argv) {
    int r = argc > 1 && strcmp(argv[1], "selftest") ? atoi(argv[1]) : 1;
    int selftest = argc > 1 && !strcmp(argv[1], "selftest");
    uint64_t seed = argc > 2 ? strtoull(argv[2], 0, 0) : 1;
    int force_h = argc > 3 ? atoi(argv[3]) : -1;
    rng_seed(seed);
    size_t D = degD(r);
    printf("r=%d seed=%llu D=%zu\n", r, (unsigned long long)seed, D);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    uint64_t total_all = 0;
    nst = 0;
    stage_begin(); ntt_init(16); stage_end("init (twiddle table)");
    line_t L[2]; fp W0s, W1s;
    stage_begin();
    {
        snap_t s0 = snap();
        line_setup(&L[0], 0); line_setup(&L[1], 1);
        /* intersection of the two families: Q0 + t0 (a0,b0) = Q1 + t1 (a1,b1) */
        fp dU, dV, det, idet, t, u, t0, t1, ta, tb;
        fp_sub(&dU, &L[1].UQ, &L[0].UQ); fp_sub(&dV, &L[1].VQ, &L[0].VQ);
        fp_mul(&t, &L[1].a, &L[0].b); fp_mul(&u, &L[0].a, &L[1].b); fp_sub(&det, &t, &u);        /* a1 b0 - a0 b1 */
        fp_inv(&idet, &det);
        fp_mul(&t, &L[1].a, &dV); fp_mul(&u, &dU, &L[1].b); fp_sub(&ta, &t, &u); fp_mul(&t0, &ta, &idet);   /* (a1 dV - b1 dU)/det */
        fp_mul(&t, &L[0].a, &dV); fp_mul(&u, &L[0].b, &dU); fp_sub(&tb, &t, &u); fp_mul(&t1, &tb, &idet);   /* (a0 dV - b0 dU)/det */
        fp_pow5(&W0s, &t0); fp_pow5(&W1s, &t1);
        bound_mem_since(s0); CTL(INV_CTL);
    }
    stage_end("two line setups + intersection");
    if (selftest) {
        /* uncounted checks */
        snap_t keep = snap();
        fp n1, r1, n2, r2;
        map_back(&n1, &r1, &L[0], &W0s); map_back(&n2, &r2, &L[1], &W1s);
        printf("intersection consistent: %d\n", fp_eq(&n1, &n2) && fp_eq(&r1, &r2));
        fp d0, d1;
        tail_eval(&d0, &L[0], &W0s, r); tail_eval(&d1, &L[1], &W1s, r);
        fp h0; poseidon_hash_r_fp(&h0, &n1, &r1, r);
        printf("digest on both families equals the reference hash: %d\n", fp_eq(&d0, &h0) && fp_eq(&d1, &h0));
        fp zero; fp_set_zero(&zero);
        fp y; rnd_fp254(&y);
        fp *F = NEW_FP(D + 1);
        build_F(F, &L[1], &zero, r);
        fp w, acc; rnd_fp254(&w); fp_set_zero(&acc);
        for (size_t k = D + 1; k-- > 0;) { fp_mul(&acc, &acc, &w); fp_add(&acc, &acc, &F[k]); }
        fp ev, lead_ev; tail_eval(&ev, &L[1], &w, r);
        /* F is monic scaled: compare F(w) * lead with f(w): recover lead from tail_eval at two points is awkward; compare ratios */
        fp w2; rnd_fp254(&w2); fp acc2; fp_set_zero(&acc2);
        for (size_t k = D + 1; k-- > 0;) { fp_mul(&acc2, &acc2, &w2); fp_add(&acc2, &acc2, &F[k]); }
        fp ev2; tail_eval(&ev2, &L[1], &w2, r);
        fp lhs, rhs; fp_mul(&lhs, &acc, &ev2); fp_mul(&rhs, &acc2, &ev);
        printf("interpolated polynomial matches the digest at 2 random points (ratio test): %d\n", fp_eq(&lhs, &rhs));
        (void)lead_ev; (void)y;
        xfree(F);
        snap_restore(keep);
        return 0;
    }
    /* ---- sample x uniformly from the union ---- */
    stage_begin();
    uint64_t Nlim[4], w[4], Plim[4], W1l[4];
    {   /* N = 2p - 1 */
        unsigned __int128 c = 0;
        for (int i = 0; i < 4; i++) { unsigned __int128 s = (unsigned __int128)PALLAS_P[i] * 2 + (uint64_t)c; Nlim[i] = (uint64_t)s; c = s >> 64; }
        uint64_t one4[4] = { 1, 0, 0, 0 }; sub256(Nlim, Nlim, one4);
        memcpy(Plim, PALLAS_P, 32);
    }
    int hx; fp Wx;
    if (force_h >= 0) {
        hx = force_h; fp_from_hex(&Wx, argv[4]);
        CTL(10);
    } else {
        int got = 0;
        for (int tr = 0; tr < 128 && !got; tr++) {
            rnd_u256(w); CTL(3 + 8);                                  /* loop, comparison with N */
            if (lt256(w, Nlim)) got = 1;
        }
        if (!got) { printf("sampling halt\n"); return 3; }
        CTL(8);
        if (lt256(w, Plim)) { hx = 0; fp_from_limbs(&Wx, w); }
        else {
            uint64_t v[4]; sub256(v, w, Plim); CTL(8);
            fp_to_limbs(W1l, &W1s); CTL(8);
            if (!lt256(v, W1l)) { add1_256(v, v); CTL(8); }
            hx = 1; fp_from_limbs(&Wx, v);
        }
    }
    CTL(6 + 40);                                                     /* family test and the control of the driver (calls, tests of found and failed) */
    int x_is_I = (hx == 0 && fp_eq(&Wx, &W0s)); CTL(4);
    fp y;
    {
        snap_t e0 = snap();
        tail_eval(&y, &L[hx], &Wx, r);
        snap_restore(e0);
        X.perm += (uint64_t)poseidon_C(r);
    }
    stage_end("sample x, y = H(x)");
    printf("x: family %d%s\n", hx, x_is_I ? " (intersection point)" : "");
    fp Wr; int found = 0, hr = -1; int failed_split = 0;
    for (int h = 0; h < 2 && !found && !failed_split; h++) {
        fp *F = NEW_FP(D + 1);
        char nm[64];
        stage_begin(); build_F(F, &L[h], &y, r); snprintf(nm, sizeof nm, "family %d: build F (evaluations + NTT)", h); stage_end(nm);
        fp *R = NEW_FP(D);
        stage_begin(); powx_lean(R, F, D, PALLAS_P, 1);
        { fp one; fp_set_one(&one); fp_sub(&R[1], &R[1], &one); LD(1); ST(1); }
        snprintf(nm, sizeof nm, "family %d: W^p mod F", h); stage_end(nm);
        fp *Gb = NEW_FP(D + 1);
        stage_begin();
        size_t dg = gcd_cl(Gb, F, D, R, D - 1);
        xfree(F); xfree(R);
        snprintf(nm, sizeof nm, "family %d: gcd(F, W^p - W)", h); stage_end(nm);
        uint64_t bound = gcd_cost_bound(D, D - 1), got = snap_total(st[nst - 1].d);
        printf("    gcd degree %zu, charged %llu, derived bound %llu (%s)\n", dg, (unsigned long long)got, (unsigned long long)bound, got <= bound ? "within" : "EXCEEDED"); fflush(stdout);
        CTL(2); if (got > bound) return 4;
        stage_begin();
        fp *G = NEW_FP(dg + 1); memcpy(G, Gb, (dg + 1) * sizeof(fp)); LD(dg + 1); ST(dg + 1); loopc(dg + 1);
        xfree(Gb);
        size_t d = dg;
        if (h == hx) { G = deflate(G, d, &Wx); d--; }
        if (h == 1 && x_is_I) { G = deflate(G, d, &W1s); d--; }
        CTL(8 + 40);                                                 /* the two tests above and the control of the driver loop over the families */
        snprintf(nm, sizeof nm, "family %d: remove the roots of x", h); stage_end(nm);
        printf("    remaining roots: %zu\n", d);
        if (d >= 1) {
            stage_begin();
            if (split_find_root(&Wr, G, d)) { found = 1; hr = h; } else failed_split = 1;
            snprintf(nm, sizeof nm, "family %d: isolate one root", h); stage_end(nm);
        } else xfree(G);
    }
    int success = 0;
    fp nk1, rho1, nk2, rho2, dg1, dg2;
    if (found) {
        stage_begin();
        snap_t s0 = snap();
        map_back(&nk1, &rho1, &L[hx], &Wx);
        map_back(&nk2, &rho2, &L[hr], &Wr);
        bound_mem_since(s0);
        stage_end("map back (two inputs)");
        stage_begin();
        poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
        poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
        { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
        stage_end("verification (2 reference hashes)");
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
        success = fp_eq(&dg1, &dg2) && !same_in;
    }
    for (int i = 0; i < nst; i++) total_all += snap_total(st[i].d);
    printf("RESULT found=%d success=%d split_levels=%llu split_tries=%llu\n", found, success, (unsigned long long)SPL_levels, (unsigned long long)SPL_tries);
    if (success) {
        phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
        phex("COLLISION digest", &dg1);
    }
    printf("SUMMARY total_all=%llu units=%.1f log2_units=%.4f heap_peak=%zu\n", (unsigned long long)total_all, (double)total_all / poseidon_C(r), log2((double)total_all / poseidon_C(r)), gpeak);
    printf("SPLIT shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_shift, (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    return success ? 0 : 1;
}
