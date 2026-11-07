/* not shipped: F(W) of line.c versus the reference hash. For j in {0,1,2}, 20 seeded random tau: W = tau^5, F = tail_eval(W, r), (nk, rho) = map_back(W);
   prints j r nk rho F in hex (canonical, big-endian) for poseidon_ref.hash_reduced to check.  Also prints poly_degree_m(r). */
#include "../attack.h"
#include <stdio.h>
static void phex(const fp *a) { uint64_t v[4]; fp_to_limbs(v, a); printf("%016llx%016llx%016llx%016llx", (unsigned long long)v[3], (unsigned long long)v[2], (unsigned long long)v[1], (unsigned long long)v[0]); }
int main(void) {
    for (int r = 0; r <= 5; r++) printf("M %d %zu\n", r, poly_degree_m(r));
    rng_seed(20261014);
    for (int j = 0; j < 3; j++) {
        line_t L; line_setup(&L, j);
        for (int k = 0; k < 20; k++) {
            fp tau, W, nk, rho, F; rnd_fp254(&tau); fp_pow5(&W, &tau);
            map_back(&nk, &rho, &L, &W);
            for (int r = 0; r <= 5; r++) { tail_eval(&F, &L, &W, r); printf("T %d %d %d ", j, k, r); phex(&tau); printf(" "); phex(&nk); printf(" "); phex(&rho); printf(" "); phex(&F); printf("\n"); }
        }
    }
    return 0;
}
