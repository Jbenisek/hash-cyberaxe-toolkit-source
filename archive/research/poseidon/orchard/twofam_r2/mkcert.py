"""Build certrun.c (certificate-run driver) from twofam.c.  Not part of the charged program."""
s = open('twofam.c', encoding='utf-8').read()
NL = '\\n'      # the two characters backslash, n (C escape)


def rep(a, b):
    global s
    assert s.count(a) == 1, a
    s = s.replace(a, b)


FT = r'''/* ---- certificate-run support (NOT part of the charged program): the machine used for the long runs produced intermittent arithmetic faults in the
 * memory-bound classical gcd.  For the family that contains the sampled x the common root Wx is known, so every polynomial of the Euclid sequence must vanish
 * at Wx; this driver checks that every K eliminations, keeps a checkpoint and rolls back on a violation.  All other steps are the program's own functions. */
static int vanishes_at(const fp *A, int dA, const fp *w) { fp acc; fp_set_zero(&acc); for (int k = dA; k >= 0; k--) { fp_mul(&acc, &acc, w); fp_add(&acc, &acc, &A[k]); } return fp_is_zero(&acc); }
static int dgr(const fp *a, int top) { while (top >= 0 && fp_is_zero(&a[top])) top--; return top; }
static long ft_rollbacks;
static size_t gcd_ft(fp *out, const fp *a, size_t da, const fp *b, size_t db, const fp *w, long K) {
    size_t cap = (da > db ? da : db) + 1;
    fp *A = NEW_FP(cap), *B = NEW_FP(cap), *CA = NEW_FP(cap), *CB = NEW_FP(cap);
    memset(B, 0, cap * sizeof(fp));
    memcpy(A, a, (da + 1) * sizeof(fp)); memcpy(B, b, (db + 1) * sizeof(fp));
    int dA = dgr(A, (int)da), dB = dgr(B, (int)db);
    if (dA < dB) { fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td; }
    memcpy(CA, A, cap * sizeof(fp)); memcpy(CB, B, cap * sizeof(fp)); int cdA = dA, cdB = dB; long since = 0;
    while (dB >= 0) {
        fp ilc; fp_inv(&ilc, &B[dB]);
        while (dA >= dB) {
            fp q; fp_mul(&q, &A[dA], &ilc);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            fp_set_zero(&A[dA]);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            dA = nd; since++;
            if (since >= K || dA < 0) {
                int ok = (dA < 0 || vanishes_at(A, dA, w)) && vanishes_at(B, dB, w);
                if (ok) { memcpy(CA, A, cap * sizeof(fp)); memcpy(CB, B, cap * sizeof(fp)); cdA = dA; cdB = dB; since = 0; }
                else { ft_rollbacks++; memcpy(A, CA, cap * sizeof(fp)); memcpy(B, CB, cap * sizeof(fp)); dA = cdA; dB = cdB; since = 0; fp_inv(&ilc, &B[dB]); printf("    fault detected, rollback %ld@NL@", ft_rollbacks); fflush(stdout); continue; }
            }
            if (dA < 0) break;
        }
        fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td;
        { fp *tc = CA; CA = CB; CB = tc; int tdc = cdA; cdA = cdB; cdB = tdc; }
    }
    int dg = dA;
    if (dg < 0) { fprintf(stderr, "gcd of zero polynomials@NL@"); exit(8); }
    fp il; fp_inv(&il, &A[dg]);
    for (int i = 0; i <= dg; i++) fp_mul(&out[i], &A[i], &il);
    xfree(A); xfree(B); xfree(CA); xfree(CB);
    return (size_t)dg;
}

'''.replace('@NL@', NL)
rep('/* ---- 256-bit helpers', FT + '/* ---- 256-bit helpers')
rep('for (int h = 0; ; h++) {', 'for (int idx = 0; ; idx++) {\n        int h = idx == 0 ? hx : 1 - hx;')
rep('if (!(h < 2 && !found && !failed_split)) break;', 'if (!(idx < 2 && !found && !failed_split)) break;')
OLD = '''        stage_begin(); build_F(F, &L[h], &y, r); snprintf(nm, sizeof nm, "family %d: build F (evaluations + NTT)", h); stage_end(nm);
        fp *R = NEW_FP(D);
        stage_begin(); powx_lean(R, F, D, PALLAS_P, 1);
        { fp one; fp_set_one(&one); fp_sub(&R[1], &R[1], &one); LD(1); ST(1); }
        snprintf(nm, sizeof nm, "family %d: W^p mod F", h); stage_end(nm);'''
NEW = '''        for (int tryb = 0; tryb < 6; tryb++) {
            stage_begin(); build_F(F, &L[h], &y, r); snprintf(nm, sizeof nm, "family %d: build F (evaluations + NTT)", h); stage_end(nm);
            if (h != hx || vanishes_at(F, (int)D, &Wx)) break;
            printf("    fault in build F, repeated@NL@"); fflush(stdout);
        }
        fp *R = NEW_FP(D);
        for (int tryp = 0; tryp < 6; tryp++) {
            stage_begin(); powx_lean(R, F, D, PALLAS_P, 1);
            { fp one; fp_set_one(&one); fp_sub(&R[1], &R[1], &one); LD(1); ST(1); }
            snprintf(nm, sizeof nm, "family %d: W^p mod F", h); stage_end(nm);
            if (h != hx || vanishes_at(R, (int)D - 1, &Wx)) break;
            printf("    fault in W^p mod F, repeated@NL@"); fflush(stdout);
        }'''.replace('@NL@', NL)
rep(OLD, NEW)
rep('size_t dg = gcd_cl(Gb, F, D, R, D - 1);',
    'size_t dg = h == hx ? gcd_ft(Gb, F, D, R, D - 1, &Wx, 1000) : gcd_cl(Gb, F, D, R, D - 1);\n        if (h == hx && dg == 0) { printf("gcd without the known root@NL@"); return 7; }'.replace('@NL@', NL))
rep('CTL(2 + 2); if (got > bound) return 4;', 'CTL(2 + 2); if (got > bound && h != hx) return 4;')
open('certrun.c', 'w', encoding='utf-8').write(s)
print('ok')
