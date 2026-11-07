/* Radix-3 stage helpers.  Mask tables: for an input pattern nzb (bit t set = position t of the Good-Thomas triple is nonzero) and the
 * rotation rot of the element, bit i1 of the DFT input mask is set when nzb has bit (rot + i1) % 3. */
static int mask_of(int nzb, int rot) {
    int m = 0;
    for (int i1 = 0; i1 < 3; i1++) if ((nzb >> ((rot + i1) % 3)) & 1) m |= 1 << i1;
    return m;
}
/* All three outputs from the inputs flagged in mask (switch on the mask: 3 operations, then straight-line field operations). */
static void dft3_masked(const fp *v, int mask, fp *o) {
    CTL(3);
    fp t;
    switch (mask) {
    case 1: o[0] = o[1] = o[2] = v[0]; break;
    case 2: o[0] = v[1]; fp_mul(&o[1], &v[1], &W3[1]); fp_mul(&o[2], &v[1], &W3[2]); break;
    case 4: o[0] = v[2]; fp_mul(&o[1], &v[2], &W3[2]); fp_mul(&o[2], &v[2], &W3[1]); break;
    case 3: fp_add(&o[0], &v[0], &v[1]); fp_mul(&t, &v[1], &W3[1]); fp_add(&o[1], &v[0], &t); fp_mul(&t, &v[1], &W3[2]); fp_add(&o[2], &v[0], &t); break;
    case 5: fp_add(&o[0], &v[0], &v[2]); fp_mul(&t, &v[2], &W3[2]); fp_add(&o[1], &v[0], &t); fp_mul(&t, &v[2], &W3[1]); fp_add(&o[2], &v[0], &t); break;
    case 6: { fp a, b; fp_add(&o[0], &v[1], &v[2]);
              fp_mul(&a, &v[1], &W3[1]); fp_mul(&b, &v[2], &W3[2]); fp_add(&o[1], &a, &b);
              fp_mul(&a, &v[1], &W3[2]); fp_mul(&b, &v[2], &W3[1]); fp_add(&o[2], &a, &b); break; }
    default: dft3_full(v, o); break;
    }
}
/* output k only, inputs flagged in mask: o = sum_i v[i] w^(ik).  Per input: presence test (2), first test (2), exponent selection by the switch on k (2 per call). */
static void dft3_one(const fp *v, int mask, int k, fp *o) {
    CTL(3);
    int first = 1; fp acc;
    for (int i = 0; i < 3; i++) {
        CTL(4);
        if (!((mask >> i) & 1)) continue;
        fp term = v[i]; int e = (i * k) % 3;
        if (e) fp_mul(&term, &v[i], &W3[e]);
        if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
    }
    CTL(2);
    *o = acc;
}
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(6);
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        if (dst == src && off == 0) { for (size_t i = len; i < n; i++) dst[i] = z; if (n > len) { ST(n - len); loopc(n - len); } return; }
        for (size_t i = 0; i < n; i++) { if (i < len) { dst[i] = src[off + i]; LD(1); } else dst[i] = z; }
        ST(n); loopc(n); CTL(2 * n); return;
    }
    /* regions of constant nonzero pattern: [0,b1) all three positions, [b1,b2) positions 0,1, [b2,b3) position 0, [b3,n) none */
    size_t b1 = len > 2 * n ? len - 2 * n : 0, b2 = len > n ? len - n : 0, b3 = len;
    if (b1 > n) b1 = n; if (b2 > n) b2 = n; if (b3 > n) b3 = n;
    size_t bnd[5] = { 0, b1, b2, b3, n }; static const int NZB[4] = { 7, 3, 1, 0 };
    CTL(25);
    int c0 = P->c0 % 3;
    for (int q = 0; q < 4; q++) {
        int nzb = NZB[q], MT[3];
        for (int r = 0; r < 3; r++) MT[r] = mask_of(nzb, r);
        CTL(30);                                        /* region loop, mask table (3 entries x 9 operations) */
        int rot = (int)((c0 * (bnd[q] % 3)) % 3);
        rot = (rot + 3 - c0) % 3; CTL(6);
        for (size_t i0 = bnd[q]; i0 < bnd[q + 1]; i0++) {
            fp u[3], v[3], o[3];
            CTL(3 + 4 + 2);                             /* loop; rot update: add, compare, branch, subtract; mask lookup */
            rot = rot + c0; if (rot >= 3) rot -= 3;
            int mask = MT[rot];
            CTL(2);
            if (mask == 0) { fp_set_zero(&o[0]); o[1] = o[0]; o[2] = o[0]; }
            else {
                for (int t = 0; t < 3; t++) { CTL(3); if ((nzb >> t) & 1) { u[t] = src[off + i0 + n * (size_t)t]; LD(1); CTL(2); } }
                CTL(3);                                 /* switch on rot: constant permutation */
                switch (rot) { case 0: v[0] = u[0]; v[1] = u[1]; v[2] = u[2]; break; case 1: v[0] = u[1]; v[1] = u[2]; v[2] = u[0]; break; default: v[0] = u[2]; v[1] = u[0]; v[2] = u[1]; break; }
                dft3_masked(v, mask, o);
            }
            dst[i0] = o[0]; dst[i0 + n] = o[1]; dst[i0 + 2 * n] = o[2];
            ST(3); CTL(2);
        }
    }
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n; int c0 = P->c0 % 3, rot = (3 - P->c0 % 3) % 3;
    CTL(6);
    for (size_t i0 = 0; i0 < n; i0++) {
        CTL(3 + 4);
        rot = rot + c0; if (rot >= 3) rot -= 3;
        /* need bit i1: position i0 + n*((rot+i1)%3) < outlen.  Fast path: i0 + 2n < outlen means all needed (one compare) */
        int need;
        CTL(2);
        if (i0 + 2 * n < outlen) need = 7;
        else {
            need = 0;
            for (int i1 = 0; i1 < 3; i1++) { size_t pos = i0 + n * (size_t)((rot + i1) % 3); CTL(8); if (pos < outlen) need |= 1 << i1; }
        }
        CTL(2);
        if (!need) continue;
        fp A[3], B[3], v[3];
        for (int k = 0; k < 3; k++) A[k] = buf[i0 + n * (size_t)k];
        LD(3); CTL(2);
        B[0] = A[0]; B[1] = A[2]; B[2] = A[1];
        CTL(2);
        if (need == 7) dft3_full(B, v); else dft3_sel(B, 7, need, v);
        CTL(3);                                         /* switch on rot for the destination permutation */
        { int d0, d1, d2; if (rot == 0) { d0 = 0; d1 = 1; d2 = 2; } else if (rot == 1) { d0 = 1; d1 = 2; d2 = 0; } else { d0 = 2; d1 = 0; d2 = 1; }
          int dd[3] = { d0, d1, d2 };
          for (int i1 = 0; i1 < 3; i1++) { CTL(2); if ((need >> i1) & 1) { buf[i0 + n * (size_t)dd[i1]] = v[i1]; ST(1); CTL(2); } } }
    }
}
/* lean variant: row r of the Good-Thomas stage for the compact vector B */
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N; int c0 = P->c0 % 3, rot = (3 - P->c0 % 3) % 3;
    size_t nb = N - boff;                               /* boff < N or boff = 0 */
    CTL(10);
    for (size_t i0 = 0; i0 < n; i0++) {
        fp u[3], v[3]; int nz[3], nzb = 0; fp o;
        CTL(3 + 4);
        rot = rot + c0; if (rot >= 3) rot -= 3;
        for (int t = 0; t < 3; t++) {
            size_t idx = i0 + n * (size_t)t + nb;       /* position + N - boff */
            int any = 0; fp acc;
            CTL(2 + 3 + 2);                             /* idx (2: add, add), reduction mod N (compare, branch, subtract), any, loop-entry compare */
            if (idx >= N) idx -= N;
            for (; idx < lenB; idx += N) {              /* fold modulo x^N - 1 when lenB > N */
                CTL(2 + 2 + 1);                         /* compare, branch, first test (2), increment */
                if (!any) { acc = B[idx]; any = 1; } else fp_add(&acc, &acc, &B[idx]);
                LD(1);
            }
            CTL(3);                                     /* nz assignment, if (any), nzb bit */
            nz[t] = any; if (any) { u[t] = acc; nzb |= 1 << t; }
        }
        CTL(3);                                         /* switch on rot for the permutation */
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }
        CTL(4);                                         /* mask from nzb: table lookup (2), mask == 0 test (2) */
        if (mask == 0) fp_set_zero(&o);
        else dft3_one(v, mask, r, &o);
        tmp[i0] = o; ST(1); CTL(1);
    }
}
