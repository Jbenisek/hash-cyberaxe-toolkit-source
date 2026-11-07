/* Half-GCD (Knuth-Schoenhage / Thull-Yap style) over F_p with NTT multiplication and exact operation counting.
 *
 * Euclid remainder sequence r_0=a, r_1=b, r_{i-1} = q_i r_i + r_{i+1}; Q_i = [[q_i,1],[1,0]]; R_j = Q_1..Q_j,
 * (r_0,r_1)^T = R_j (r_j,r_{j+1})^T; d_j = deg q_1 + .. + deg q_j, deg r_j = n - d_j.
 * hgcd(a,b,k) returns R_h, (r_h, r_{h+1}) for h = max{ j : d_j <= k }.
 *
 * Truncation lemma: if a = a* x^s + a0, b = b* x^s + b0 (deg a0, b0 < s) and the Euclid sequence of (a*,b*) has
 * 2 d_j <= deg a*, then its first j quotients are the first j quotients of (a,b).  With deg a* = 2 k1 this makes
 * the recursive call on the top halves valid for parameter k1.  After applying R_1^{-1} to the exact (a,b) and one
 * exact division step the remaining parameter is <= k - k1 - 1.
 */
#include "hgcd.h"

int hgcd_base_k = 96;
uint64_t hgcd_stat_calls, hgcd_stat_base_steps, hgcd_stat_bigdiv;

static size_t trimlen(const fp *c, size_t len) {
    size_t it = 1;
    while (len > 0 && fp_is_zero(&c[len - 1])) { len--; it++; }
    CTL(5 * it);
    return len;
}
static fp *dupv(const fp *c, size_t len) {
    fp *r = NEW_FP(len ? len : 1);
    if (len) memcpy(r, c, len * sizeof(fp));
    LD(len); ST(len); loopc(len);
    return r;
}

/* ---- naive division */
void poly_divrem_naive(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) {
    if (la < lb) { *lq = 0; memcpy(r, a, la * sizeof(fp)); LD(la); ST(la); *lr = trimlen(r, la); return; }
    CTL(3);                                                          /* the test of the quotient length */
    if (la == lb + 1 && lb >= 2) {
        /* quotient of two coefficients q0 + q1 X, remainder in one pass: r_k = a_k - q0 b_k - q1 b_(k-1); b_(k-1) is the previous b_k (register), no copy of a */
        fp inv; fp_inv(&inv, &b[lb - 1]);
        fp q1, q0, t; fp_mul(&q1, &a[lb], &inv);
        fp_mul(&t, &q1, &b[lb - 2]); fp_sub(&t, &a[lb - 1], &t); fp_mul(&q0, &t, &inv);
        LD(3); q[0] = q0; q[1] = q1; ST(2); *lq = 2; CTL(6);
        fp prev; fp_set_zero(&prev);
        for (size_t k = 0; k + 1 < lb; k++) {
            fp bk = b[k], x, y;
            fp_mul(&x, &q0, &bk); fp_sub(&x, &a[k], &x);
            if (k) { fp_mul(&y, &q1, &prev); fp_sub(&x, &x, &y); }
            r[k] = x; prev = bk;
        }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(4);
        *lr = trimlen(r, lb - 1);
        return;
    }
    fp *w = r; /* r must have room for la coefficients */
    if (w != a) { memcpy(w, a, la * sizeof(fp)); LD(la); ST(la); loopc(la); }
    fp inv; fp_inv(&inv, &b[lb - 1]);
    *lq = la - lb + 1;
    for (size_t i = la - lb + 1; i-- > 0;) {
        fp qi; fp_mul(&qi, &w[i + lb - 1], &inv); LD(1);
        q[i] = qi; ST(1);
        for (size_t j = 0; j + 1 < lb; j++) { fp t; fp_mul(&t, &qi, &b[j]); fp_sub(&w[i + j], &w[i + j], &t); }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(8);
        budget_check();
    }
    *lr = trimlen(w, lb - 1);
}

/* ---- matrices */
static void mat_set_identity(mat_t *R) {
    for (int i = 0; i < 4; i++) { R->e[i] = NEW_FP(1); R->len[i] = 0; }
    fp_set_one(&R->e[0][0]); R->len[0] = 1; fp_set_one(&R->e[3][0]); R->len[3] = 1; ST(2);
    R->h = 0;
}
void mat_free(mat_t *R) { for (int i = 0; i < 4; i++) { if (R->e[i]) xfree(R->e[i]); R->e[i] = NULL; } }

/* out = e*q + f (any of the operands may be empty) ; returns trimmed length; *res freshly allocated */
static size_t poly_mul_add_small(fp **res, const fp *e, size_t le, const fp *q, size_t lq, const fp *f, size_t lf) {
    size_t lt = (le && lq) ? le + lq - 1 : 0;
    size_t lo = lt > lf ? lt : lf;
    fp *o = NEW_FP(lo ? lo : 1);
    for (size_t i = 0; i < lo; i++) fp_set_zero(&o[i]);
    ST(lo); loopc(lo);
    if (lt) {
        fp *t = NEW_FP(lt);
        poly_mul(t, e, le, q, lq);
        for (size_t i = 0; i < lt; i++) o[i] = t[i];
        LD(lt); ST(lt); loopc(lt);
        xfree(t);
    }
    for (size_t i = 0; i < lf; i++) fp_add(&o[i], &o[i], &f[i]);
    LD(2 * lf); ST(lf); loopc(lf);
    *res = o;
    return trimlen(o, lo);
}
/* R := R * [[q,1],[1,0]] */
/* two-coefficient q (q0 + q1 X): o_k = e_k q0 + e_(k-1) q1 + f_k in one pass (e_(k-1) is the previous e_k, register) */
static size_t mul_add_q2(fp **res, const fp *e, size_t le, const fp *q, const fp *f, size_t lf) {
    size_t lt = le ? le + 1 : 0;
    size_t lo = lt > lf ? lt : lf;
    fp *o = NEW_FP(lo ? lo : 1);
    fp prev; fp_set_zero(&prev);
    for (size_t k = 0; k < lo; k++) {
        fp acc, t; int have = 0;
        if (k < le) { fp ek = e[k]; fp_mul(&acc, &ek, &q[0]); have = 1; if (k) { fp_mul(&t, &prev, &q[1]); fp_add(&acc, &acc, &t); } prev = ek; }
        else if (k == le && le) { fp_mul(&acc, &prev, &q[1]); have = 1; }
        if (k < lf) { if (have) fp_add(&acc, &acc, &f[k]); else acc = f[k]; }
        o[k] = acc;
    }
    LD(le + lf); ST(lo); loopc(lo); CTL(8);                           /* boundary iterations peeled: 8 control operations */
    *res = o;
    return trimlen(o, lo);
}
static void mat_mulQ(mat_t *R, const fp *q, size_t lq) {
    fp *n0, *n2; size_t l0, l2;
    if (lq == 2) {
        CTL(2);
        l0 = mul_add_q2(&n0, R->e[0], R->len[0], q, R->e[1], R->len[1]);
        l2 = mul_add_q2(&n2, R->e[2], R->len[2], q, R->e[3], R->len[3]);
    } else {
    l0 = poly_mul_add_small(&n0, R->e[0], R->len[0], q, lq, R->e[1], R->len[1]);
    l2 = poly_mul_add_small(&n2, R->e[2], R->len[2], q, lq, R->e[3], R->len[3]);
    }
    xfree(R->e[1]); xfree(R->e[3]);
    R->e[1] = R->e[0]; R->len[1] = R->len[0];
    R->e[3] = R->e[2]; R->len[3] = R->len[2];
    R->e[0] = n0; R->len[0] = l0; R->e[2] = n2; R->len[2] = l2;
    R->h++;
}

/* ---- pointwise helpers */
static void pw_mul(fp *dst, const fp *x, const fp *y, size_t N) {
    for (size_t i = 0; i < N; i++) fp_mul(&dst[i], &x[i], &y[i]);
    LD(2 * N); ST(N); loopc(N);
}
static void pw_mulsub(fp *acc, const fp *x, const fp *y, size_t N) {   /* acc -= x*y */
    for (size_t i = 0; i < N; i++) { fp t; fp_mul(&t, &x[i], &y[i]); fp_sub(&acc[i], &acc[i], &t); }
    LD(3 * N); ST(N); loopc(N);
}
static void pw_muladd(fp *acc, const fp *x, const fp *y, size_t N) {   /* acc += x*y */
    for (size_t i = 0; i < N; i++) { fp t; fp_mul(&t, &x[i], &y[i]); fp_add(&acc[i], &acc[i], &t); }
    LD(3 * N); ST(N); loopc(N);
}
/* transform of src (len coefficients) reduced modulo x^N-1 */
static void prep(const plan_t *P, fp *buf, const fp *src, size_t len) {
    size_t N = P->N;
    if (len <= N) { ntt_fwd(P, buf, src, 0, len); return; }
    for (size_t i = 0; i < N; i++) buf[i] = src[i];
    LD(N); ST(N); loopc(N);
    for (size_t i = N; i < len; i++) fp_add(&buf[i % N], &buf[i % N], &src[i]);
    LD(2 * (len - N)); ST(len - N); loopc(len - N);
    ntt_fwd(P, buf, buf, 0, N);
}
static void finish(const plan_t *P, fp *out, fp *T, size_t outlen) {
    ntt_inv(P, T, outlen);
    fp inv; plan_invN(P, &inv);
    for (size_t i = 0; i < outlen; i++) fp_mul(&out[i], &T[i], &inv);
    LD(outlen); ST(outlen); loopc(outlen);
}

/* (c,d) = R^{-1}(a,b): c = s(r22 a - r12 b), d = s(r11 b - r21 a), s = (-1)^h.  deg c = n - deg r11.
 * Lean: every operand spectrum is generated row by row from the compact polynomial; the outputs are built in
 * buffers of N slots (N >= nres) that are handed back as the result arrays. */
static void apply_inv(fp **c, size_t *lc, fp **d, size_t *ld, const mat_t *R, const fp *a, size_t la, const fp *b, size_t lb) {
    if (R->h == 0) { *c = dupv(a, la); *lc = la; *d = dupv(b, lb); *ld = lb; return; }
    size_t sumdeg = R->len[0] - 1;
    size_t nres = la - sumdeg;                     /* deg c + 1 */
    plan_t P = plan3_for_len(nres);
    size_t N = P.N;
    fp *tH = NEW_FP(P.n), *tS = NEW_FP(P.n);
    *c = NEW_FP(N); *d = NEW_FP(N);
    int sgn = (R->h & 1) ? -1 : 1;
    CTL(60);                                 /* operand selection: about 60 executed comparisons, branches and index operations */
    /* c = s (r22 a - r12 b), d = s (r11 b - r21 a), s = (-1)^h.  Shared transforms: a and b are transformed once per row, every matrix entry once per row. */
    bilin_grp_t G[2]; int ng = 0;
    {
        const fp *V[2] = { a, b }; size_t lV[2] = { la, lb };
        const int ec[2] = { 3, 1 }, ed[2] = { 2, 0 };                 /* entry multiplying V[v] in c and in d */
        const int sc[2] = { sgn, -sgn }, sd[2] = { -sgn, sgn };
        for (int v = 0; v < 2; v++) {
            bilin_grp_t *g = &G[ng]; memset(g, 0, sizeof *g); g->nh = 1; g->H[0] = V[v]; g->lH[0] = lV[v];
            g->o[0][0] = g->o[1][0] = g->o[0][1] = g->o[1][1] = -1;
            if (!lV[v]) continue;
            if (R->len[ec[v]]) { g->S[g->ns] = R->e[ec[v]]; g->lS[g->ns] = R->len[ec[v]]; g->o[g->ns][0] = 0; g->sg[g->ns][0] = (signed char)sc[v]; g->ns++; }
            if (R->len[ed[v]]) { g->S[g->ns] = R->e[ed[v]]; g->lS[g->ns] = R->len[ed[v]]; g->o[g->ns][0] = 1; g->sg[g->ns][0] = (signed char)sd[v]; g->ns++; }
            if (g->ns) ng++;
            CTL(10);
        }
    }
    fp *outs[2] = { *c, *d }; size_t olen[2] = { nres, nres }; int eps[2];
    conv_bilin_otf(&P, 2, outs, olen, ng, G, tH, NULL, tS, eps);
    xfree(tH); xfree(tS);
    fp inv; plan_invN(&P, &inv);
    for (int k = 0; k < 2; k++) {
        fp *o = outs[k]; CTL(3);
        if (!eps[k]) { for (size_t i = 0; i < nres; i++) fp_set_zero(&o[i]); ST(nres); loopc(nres); continue; }
        fp sc = inv; if (eps[k] < 0) fp_neg(&sc, &inv);
        for (size_t i = 0; i < nres; i++) fp_mul(&o[i], &o[i], &sc);
        LD(nres); ST(nres); loopc(nres);
    }
    *lc = trimlen(*c, nres); *ld = trimlen(*d, nres);
}

/* out = A * B (2x2 polynomial matrices), lean: one N-slot product buffer reused for the four entries */
static void mat_mul(mat_t *out, const mat_t *A, const mat_t *B) {
    size_t Lmax = 1;
    size_t L[4];
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
        size_t l = 0;
        for (int t = 0; t < 2; t++) {
            size_t la = A->len[2 * i + t], lb = B->len[2 * t + j];
            if (la && lb && la + lb - 1 > l) l = la + lb - 1;
        }
        L[2 * i + j] = l; if (l > Lmax) Lmax = l;
    }
    out->h = A->h + B->h;
    if (Lmax <= 48) {
        for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
            size_t l = L[2 * i + j];
            fp *o = NEW_FP(l ? l : 1);
            for (size_t u = 0; u < l; u++) fp_set_zero(&o[u]);
            ST(l);
            for (int t = 0; t < 2; t++) {
                size_t la = A->len[2 * i + t], lb = B->len[2 * t + j];
                if (!la || !lb) continue;
                fp *tmp = NEW_FP(la + lb - 1);
                poly_mul_naive(tmp, A->e[2 * i + t], la, B->e[2 * t + j], lb);
                for (size_t u = 0; u < la + lb - 1; u++) fp_add(&o[u], &o[u], &tmp[u]);
                LD(2 * (la + lb - 1)); ST(la + lb - 1); loopc(la + lb - 1);
                xfree(tmp);
            }
            out->e[2 * i + j] = o; out->len[2 * i + j] = trimlen(o, l);
        }
        return;
    }
    plan_t P = plan3_for_len(Lmax);
    size_t N = P.N;
    /* shared transforms: the entries of the right factor (held, up to two per group) and of the left factor (streamed) are transformed once per row */
    fp *tH0 = NEW_FP(P.n), *tH1 = NEW_FP(P.n), *tS = NEW_FP(P.n);
    fp *ob[4]; size_t ol[4];
    for (int k_ = 0; k_ < 4; k_++) { ob[k_] = NEW_FP(N); ol[k_] = L[k_]; }
    bilin_grp_t G[2]; int ng = 0;
    for (int t = 0; t < 2; t++) {
        bilin_grp_t *g = &G[ng]; memset(g, 0, sizeof *g); int hj[2] = { -1, -1 };
        g->o[0][0] = g->o[1][0] = g->o[0][1] = g->o[1][1] = -1;
        for (int j = 0; j < 2; j++) if (B->len[2 * t + j]) { hj[j] = g->nh; g->H[g->nh] = B->e[2 * t + j]; g->lH[g->nh] = B->len[2 * t + j]; g->nh++; }
        for (int i = 0; i < 2; i++) if (A->len[2 * i + t]) {
            g->S[g->ns] = A->e[2 * i + t]; g->lS[g->ns] = A->len[2 * i + t];
            for (int j = 0; j < 2; j++) if (hj[j] >= 0) { g->o[g->ns][hj[j]] = (signed char)(2 * i + j); g->sg[g->ns][hj[j]] = 1; }
            g->ns++;
        }
        if (g->nh && g->ns) ng++;
        CTL(20);
    }
    int eps[4];
    conv_bilin_otf(&P, 4, ob, ol, ng, G, tH0, tH1, tS, eps);
    xfree(tH0); xfree(tH1); xfree(tS);
    fp inv; plan_invN(&P, &inv);
    for (int k = 0; k < 4; k++) {
        size_t l = L[k]; fp *o = NEW_FP(l ? l : 1); CTL(3);
        if (eps[k]) {
            fp sc = inv; if (eps[k] < 0) fp_neg(&sc, &inv);
            for (size_t u = 0; u < l; u++) fp_mul(&o[u], &ob[k][u], &sc);
            LD(l); ST(l); loopc(l);
        }
        xfree(ob[k]);
        out->e[k] = o; out->len[k] = l ? trimlen(o, l) : 0;
    }
}

/* ---- base case: plain Euclid until the next quotient would exceed the remaining budget.
 * own != 0: a and b are xalloc'ed arrays whose ownership passes to the callee. */
static void hgcd_base(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    fp *x = own ? (fp *)a : dupv(a, la), *y = own ? (fp *)b : dupv(b, lb);
    size_t lx = la, ly = lb, sum = 0;
    if (want_mat) mat_set_identity(R);
    while (ly > 0) {
        budget_check(); CTL(12);
        size_t dq = lx - ly;
        if (dq > k - sum) break;
        fp *q = NEW_FP(dq + 1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        if (want_mat) mat_mulQ(R, q, lq);
        sum += dq;
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
        hgcd_stat_base_steps++;
    }
    if (c) { *c = x; *lc = lx; } else xfree(x);
    if (d) { *d = y; *ld = ly; } else xfree(y);
}

int hgcd_k1_pct = 50;

void hgcd(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    hgcd_stat_calls++; CTL(40);
    budget_check();
    size_t n = la - 1;
    if (lb == 0 || n - (lb - 1) > k) {
        if (want_mat) mat_set_identity(R);
        if (own) {
            if (c) { *c = (fp *)a; *lc = la; } else xfree((void *)a);
            if (d) { *d = (fp *)b; *ld = lb; } else xfree((void *)b);
        } else {
            if (c) { *c = dupv(a, la); *lc = la; }
            if (d) { *d = dupv(b, lb); *ld = lb; }
        }
        return;
    }
    if (k <= (size_t)hgcd_base_k) { hgcd_base(R, c, lc, d, ld, a, la, b, lb, k, want_mat, own); return; }
    size_t k1 = (k * (size_t)hgcd_k1_pct + 99) / 100;
    if (2 * k1 > n) k1 = n / 2;
    size_t s = n - 2 * k1;
    mat_t R1; fp *cc, *dd; size_t lcc, ldd;
    {
        const fp *as = a + s; size_t las = la - s;
        const fp *bs = b + s; size_t lbs = lb > s ? lb - s : 0;
        hgcd(&R1, NULL, NULL, NULL, NULL, as, las, bs, lbs, k1, 1, 0);
    }
    if (R1.h == 0) {
        if (own) { cc = (fp *)a; dd = (fp *)b; } else { cc = dupv(a, la); dd = dupv(b, lb); }
        lcc = la; ldd = lb;
    } else {
        apply_inv(&cc, &lcc, &dd, &ldd, &R1, a, la, b, lb);
        budget_check();
        if (own) { xfree((void *)a); xfree((void *)b); }
    }
    int r1freed = 0;
    if (!want_mat) { mat_free(&R1); r1freed = 1; }      /* memory only: the matrix is not needed once it has been applied */
    size_t sumdeg = n - (lcc - 1);
    size_t k2 = k - sumdeg;
    if (ldd == 0 || (lcc - ldd) > k2) {
        if (want_mat) *R = R1; else if (!r1freed) mat_free(&R1);
        if (c) { *c = cc; *lc = lcc; } else xfree(cc);
        if (d) { *d = dd; *ld = ldd; } else xfree(dd);
        return;
    }
    size_t dq = lcc - ldd;
    fp *q = NEW_FP(dq + 1), *rem = NEW_FP(lcc); size_t lq, lrem;
    poly_divrem_naive(q, &lq, rem, &lrem, cc, lcc, dd, ldd);
    xfree(cc);
    if (!want_mat) xfree(q);
    if (dq > 32) hgcd_stat_bigdiv++;
    size_t k3 = k2 - dq;
    mat_t R2;
    hgcd(&R2, c, lc, d, ld, dd, ldd, rem, lrem, k3, want_mat, 1);
    if (want_mat) {
        mat_mulQ(&R1, q, lq);
        mat_mul(R, &R1, &R2);
        budget_check();
        mat_free(&R2);
    }
    if (!r1freed) mat_free(&R1);
    if (want_mat) xfree(q);
}

/* ---- gcd */
static size_t monic_out(fp *out, const fp *x, size_t lx) {
    if (!lx) return 0;
    fp inv; fp_inv(&inv, &x[lx - 1]);
    for (size_t i = 0; i + 1 < lx; i++) fp_mul(&out[i], &x[i], &inv);
    fp_set_one(&out[lx - 1]);
    LD(lx); ST(lx); loopc(lx);
    return lx;
}
size_t poly_gcd_naive(fp *out, const fp *a, size_t la, const fp *b, size_t lb) {
    fp *x = dupv(a, la), *y = dupv(b, lb); size_t lx = la, ly = lb;
    while (ly > 0) {
        fp *q = NEW_FP(lx > ly ? lx - ly + 1 : 1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
    }
    size_t l = monic_out(out, x, lx);
    xfree(x); xfree(y);
    return l;
}
/* gcd(a, b) (la >= lb); the inputs are copied (the caller keeps its arrays).  Use poly_gcd_fast_own to give them away. */
size_t poly_gcd_fast_own(fp *out, size_t cap, fp *x, size_t lx, fp *y, size_t ly) {
    if (lx < ly) { fp *t = x; x = y; y = t; size_t tl = lx; lx = ly; ly = tl; }
    if (lx == ly && ly > 0) {   /* equal degrees: one division step first */
        fp *q = NEW_FP(1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
    }
    while (ly > 0) {
        size_t n = lx - 1;
        if (n <= 2 * (size_t)hgcd_base_k) {
            fp *q = NEW_FP(lx - ly + 1), *r = NEW_FP(lx); size_t lq, lr;
            poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
            xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
            continue;
        }
        fp *c, *d; size_t lc, ld;
        hgcd(NULL, &c, &lc, &d, &ld, x, lx, y, ly, (n + 1) / 2, 0, 1);
        if (ld == 0) { x = c; lx = lc; y = d; ly = 0; break; }
        fp *q = NEW_FP(lc - ld + 1), *r = NEW_FP(lc); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, c, lc, d, ld);
        xfree(c); xfree(q);
        x = d; lx = ld; y = r; ly = lr;
    }
    budget_check();
    size_t l = lx > cap ? (size_t)-1 : monic_out(out, x, lx);
    xfree(x); xfree(y);
    return l;
}
size_t poly_gcd_fast(fp *out, const fp *a, size_t la, const fp *b, size_t lb) {
    return poly_gcd_fast_own(out, la, dupv(a, la), la, dupv(b, lb), lb);
}
