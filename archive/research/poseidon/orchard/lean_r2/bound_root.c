/* Cost of one shift of the root finder (find_root compiled with ROOT_TRIES=1) on a monic polynomial of degree DEG_CAP without roots.
 * The cost of a shift is monotone in the degree, so this is the cost bound of any shift for degree <= DEG_CAP. */
#include "attack.h"
#ifndef DEG_CAP
#define DEG_CAP 16
#endif
int main(void) {
    rng_seed(3); ntt_init(4);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    fp G[DEG_CAP + 1]; for (int i = 0; i < DEG_CAP; i++) rnd_fp254(&G[i]); fp_set_one(&G[DEG_CAP]);
    fp root; snap_t s0 = snap();
    find_root(&root, G, DEG_CAP);
    snap_t d = snap_sub(snap(), s0);
    printf("BOUND_ROOT_SHIFT deg=%d cost=%llu\n", DEG_CAP, (unsigned long long)snap_total(d));
    return 0;
}
