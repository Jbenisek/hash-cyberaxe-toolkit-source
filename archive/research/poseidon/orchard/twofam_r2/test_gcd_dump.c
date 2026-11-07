/* Debug: classical Euclid on the dumped pair (F, R), checking that the current pair vanishes at the known common root Wx. */
#include "attack.h"
static int deg_of(const fp *a, int top) { while (top >= 0 && fp_is_zero(&a[top])) top--; return top; }
static int vanishes(const fp *A, int dA, const fp *w) { fp acc; fp_set_zero(&acc); for (int k = dA; k >= 0; k--) { fp_mul(&acc, &acc, w); fp_add(&acc, &acc, &A[k]); } return fp_is_zero(&acc); }
int main(int argc, char **argv) {
    size_t D = 390625; ntt_init(18);
    fp *F = NEW_FP(D + 1), *R = NEW_FP(D); fp Wx;
    FILE *fi = fopen("logs/dump_FR.bin", "rb");
    if (fread(F, sizeof(fp), D + 1, fi) != D + 1 || fread(R, sizeof(fp), D, fi) != D || fread(&Wx, sizeof(fp), 1, fi) != 1) return 9; fclose(fi);
    int period = argc > 1 ? atoi(argv[1]) : 2000; long start = argc > 2 ? atol(argv[2]) : 0;
    size_t da = D, db = D - 1, cap = D + 1;
    fp *A = NEW_FP(cap), *B = NEW_FP(cap);
    memcpy(A, F, (da + 1) * sizeof(fp)); memcpy(B, R, (db + 1) * sizeof(fp));
    int dA = deg_of(A, (int)da), dB = deg_of(B, (int)db);
    printf("start dA=%d dB=%d vanish A %d B %d\n", dA, dB, vanishes(A, dA, &Wx), vanishes(B, dB, &Wx)); fflush(stdout);
    long elim = 0;
    while (dB >= 0) {
        fp ilc; fp_inv(&ilc, &B[dB]);
        while (dA >= dB) {
            fp q; fp_mul(&q, &A[dA], &ilc);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            fp_set_zero(&A[dA]);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            dA = nd; elim++;
            if ((elim >= start && elim % period == 0) || (elim < start && elim % 4000 == 0) || dA < 0) {
                int va = dA >= 0 ? vanishes(A, dA, &Wx) : 1, vb = vanishes(B, dB, &Wx);
                printf("elim %ld dA=%d dB=%d vanish A %d B %d\n", elim, dA, dB, va, vb); fflush(stdout);
                if (!va || !vb) { printf("FIRST VIOLATION in this window\n"); return 1; }
            }
            if (dA < 0) break;
        }
        fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td;
    }
    printf("done, final degree %d\n", dA);
    return 0;
}
