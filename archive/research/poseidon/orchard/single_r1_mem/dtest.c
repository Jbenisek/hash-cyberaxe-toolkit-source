/* D-stage harness: load dump (g, F, c), run the gcd stage exactly as single.c does, print charge, peak, gcd hash. */
#include "attack.h"
#include "hgcd.h"
#include "gcd_bounds.h"
#include <time.h>
#ifdef MEMTRACE
void mem_report(void);
#endif
int main(int argc, char **argv) {
    const char *fn = argc > 1 ? argv[1] : "dump_110.bin";
    size_t m = 39062;
    fp_counters_reset(); memset(&X, 0, sizeof X);
    ntt_init(15);
    fp *g = NEW_FP(m + 1), *F = NEW_FP(m);
    FILE *fd = fopen(fn, "rb"); if (!fd) { perror("dump"); return 2; }
    if (fread(g, sizeof(fp), m + 1, fd) != m + 1 || fread(F, sizeof(fp), m, fd) != m) { fprintf(stderr, "short read\n"); return 2; }
    fclose(fd);
    mem_reset_peak();
    snap_t s0 = snap(); clock_t t0 = clock();
    fp one; fp_set_one(&one);
    fp_sub(&F[0], &F[0], &one);
    int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
    CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);
    size_t lG = 0;
    fp *G = poly_gcd_own(&lG, g, m + 1, F, (size_t)dR + 1);
    snap_t d = snap_sub(snap(), s0);
    printf("DTEST gcd_degree=%zu arith=%llu total=%llu peak=%zu secs=%.1f\n", lG ? lG - 1 : 0, (unsigned long long)snap_arith(d), (unsigned long long)snap_total(d), mem_peak, (double)(clock() - t0) / CLOCKS_PER_SEC);
    uint64_t h = 1469598103934665603ULL;
    for (size_t i = 0; i < lG; i++) for (int k = 0; k < 4; k++) { h ^= G[i].l[k]; h *= 1099511628211ULL; }
    printf("DTEST gcd_hash=%016llx\n", (unsigned long long)h);
    char hx[65]; for (size_t i = 0; i < lG; i++) { fp_to_hex(hx, &G[i]); printf("DTEST coef%zu 0x%s\n", i, hx); }
#ifdef MEMTRACE
    mem_report();
#endif
    return 0;
}
