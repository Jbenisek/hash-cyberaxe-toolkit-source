// Meet-in-the-middle split analysis of guess sets (see SPLIT_MODEL in README).
// usage: split model solfile F logN [maxsol]
// For every solution (line "SOL v1 .. vk") and every labelling of its guesses into core Z, side A, side B:
//   PA = cl(Z+A), PB = cl(Z+B), S = PA u PB; dim(X) = |X| - #equations inside X.
//   per core value: list A from 2^(32|A|) side guesses, list B from 2^(32|B|), hash join on every separable
//   condition (output 2^(32 s'), s' = dim S - dim clZ), post-filter to members 2^(32 f'), f' = F - dim clZ;
//   the core itself costs 2^(32 cZ) guesses per surviving core value, cZ = |Z| - dim clZ.
//   log2 cost for N = 2^logN members (max-of-terms approximation; see README):
//     K0 = logN - 32 f';  if K0 >= 0: cost = K0 + 32*max(cZ, |A|, |B|, s')
//     else (one core value is more than enough: shrink lists, x + y = K0): cost = max(32 cZ, K0 + 32 s', bal)
//          bal = min over x+y=K0, -32|A|<=x<=0, -32|B|<=y<=0 of max(x + 32|A|, y + 32|B|)
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
typedef unsigned __int128 u128;
#define MAXR 4096
int n, R;
int rtype[MAXR], rcnt[MAXR], rv[MAXR][8];
u128 rmask[MAXR], rtrig[MAXR];
int occ[128][256], nocc[128];
u128 ALL, base;
int neq; u128 eqmask[MAXR];

static inline int single(u128 u) { return u && !(u & (u - 1)); }
static inline int bitidx(u128 u) {
    unsigned long long lo = (unsigned long long)u, hi = (unsigned long long)(u >> 64);
    return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi);
}
static inline int pc(u128 u) { return __builtin_popcountll((unsigned long long)u) + __builtin_popcountll((unsigned long long)(u >> 64)); }

static u128 propagate_all(u128 known) {
    int q[256], qh = 0, qt = 0;
    for (int v = 0; v < n; v++) if ((known >> v) & 1) q[qt++] = v;
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) {
            int r = occ[v][i];
            if (rtype[r] == 0) {
                u128 u = rmask[r] & ~known;
                if (single(u)) { known |= u; q[qt++] = bitidx(u); }
            } else if (!(rtrig[r] & ~known)) {
                u128 t = rmask[r] & ~rtrig[r];
                if (t & ~known) { known |= t; q[qt++] = bitidx(t); }
            }
        }
    }
    return known;
}
static int dim(u128 s) {
    int e = 0;
    for (int i = 0; i < neq; i++) if (!(eqmask[i] & ~s)) e++;
    return pc(s) - e;
}
static double dmax(double a, double b) { return a > b ? a : b; }
static double dmin(double a, double b) { return a < b ? a : b; }

int main(int argc, char **argv) {
    FILE *f = fopen(argv[1], "r");
    int F = atoi(argv[3]); double logN = atof(argv[4]);
    long maxsol = argc > 5 ? atol(argv[5]) : 1000000000L;
    int zr = argc > 6 ? atoi(argv[6]) : 0;   // core = first zr guesses (fixed); others only A or B
    if (fscanf(f, "%d %d", &n, &R) != 2) return 1;
    for (int r = 0; r < R; r++) {
        if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return 1;
        for (int i = 0; i < rcnt[r]; i++) {
            if (fscanf(f, "%d", &rv[r][i]) != 1) return 1;
            rmask[r] |= (u128)1 << rv[r][i];
            if (rtype[r] == 0 || i < rcnt[r] - 1) occ[rv[r][i]][nocc[rv[r][i]]++] = r;
            if (rtype[r] == 1 && i < rcnt[r] - 1) rtrig[r] |= (u128)1 << rv[r][i];
        }
        if (rtype[r] == 0) eqmask[neq++] = rmask[r];
    }
    fclose(f);
    ALL = (n == 128) ? ~(u128)0 : (((u128)1 << n) - 1);
    base = 0;
    for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1) base |= rmask[r];
    base = propagate_all(base);
    FILE *g = fopen(argv[2], "r");
    char line[4096];
    double best = 1e9; long nsol = 0; long hist[400] = {0};
    while (fgets(line, sizeof line, g) && nsol < maxsol) {
        if (strncmp(line, "SOL", 3)) continue;
        int gs[32], k = 0; char *p = line + 3;
        while (1) { int v, c; if (sscanf(p, "%d%n", &v, &c) != 1) break; gs[k++] = v; p += c; }
        static u128 cl[1 << 17];
        { u128 s0 = base; for (int i = 0; i < k; i++) s0 |= (u128)1 << gs[i];
          if (propagate_all(s0) != ALL) { static long bad = 0; if (++bad <= 3) fprintf(stderr, "skipping a set whose closure is not everything\n"); continue; } }
        nsol++;
        for (int m = 0; m < (1 << k); m++) {
            u128 s = base;
            for (int i = 0; i < k; i++) if (m >> i & 1) s |= (u128)1 << gs[i];
            cl[m] = propagate_all(s);
        }
        static int dm[1 << 17];
        for (int m = 0; m < (1 << k); m++) dm[m] = dim(cl[m]);
        double solbest = 1e9; int bz = 0, ba = 0, bb = 0;
        int tot = 1; if (zr) tot = 1 << (k - zr); else for (int i = 0; i < k; i++) tot *= 3;
        for (int code = 0; code < tot; code++) {
            int c = code, Z = 0, A = 0, B = 0;
            if (zr) { Z = (1 << zr) - 1; for (int i = zr; i < k; i++) { if ((c >> (i - zr)) & 1) B |= 1 << i; else A |= 1 << i; } }
            else for (int i = 0; i < k; i++) { int l = c % 3; c /= 3; if (l == 0) Z |= 1 << i; else if (l == 1) A |= 1 << i; else B |= 1 << i; }
            if (A > B && B) continue;                 // symmetry
            int nZ = __builtin_popcount(Z), nA = __builtin_popcount(A), nB = __builtin_popcount(B);
            u128 S = cl[Z | A] | cl[Z | B];
            int dZ = dm[Z], dS = dim(S);
            int cZ = nZ - dZ, sp = dS - dZ, fp = F - dZ;
            double K0 = logN - 32.0 * fp, cost;
            if (K0 >= 0) {
                cost = K0 + 32.0 * dmax(dmax(cZ, nA), dmax(nB, sp));
            } else {
                // x + y = K0 with x in [-32nA,0], y in [-32nB,0]; balance x+32nA = y+32nB
                double x = (K0 + 32.0 * nB - 32.0 * nA) / 2.0;
                if (x > 0) x = 0; if (x < -32.0 * nA) x = -32.0 * nA;
                double y = K0 - x;
                if (y > 0) { y = 0; x = K0; } if (y < -32.0 * nB) { y = -32.0 * nB; x = K0 - y; }
                if (x < -32.0 * nA) x = -32.0 * nA;   // infeasible case: lists too small (should not happen if K0 >= -32(nA+nB))
                double bal = dmax(x + 32.0 * nA, y + 32.0 * nB);
                cost = dmax(dmax(32.0 * cZ, K0 + 32.0 * sp), bal);
            }
            cost = dmax(cost, logN);
            if (cost < solbest) { solbest = cost; bz = Z; ba = A; bb = B; }
        }
        int hb = (int)solbest; if (hb < 0) hb = 0; if (hb > 399) hb = 399; hist[hb]++;
        if (solbest < best - 1e-9) {
            best = solbest;
            printf("NEWBEST %.1f  sol#%ld  Z=", best, nsol);
            for (int i = 0; i < k; i++) if (bz >> i & 1) printf("%d,", gs[i]);
            printf(" A="); for (int i = 0; i < k; i++) if (ba >> i & 1) printf("%d,", gs[i]);
            printf(" B="); for (int i = 0; i < k; i++) if (bb >> i & 1) printf("%d,", gs[i]);
            u128 S = cl[bz | ba] | cl[bz | bb];
            printf("  dimZ=%d dimA=%d dimB=%d dimS=%d |S|=%d\n", dm[bz], dm[bz | ba], dm[bz | bb], dim(S), pc(S));
            fflush(stdout);
        }
    }
    printf("solutions %ld best %.1f\nhistogram of per-solution best (floor):", nsol, best);
    for (int i = 0; i < 400; i++) if (hist[i]) printf(" %d:%ld", i, hist[i]);
    printf("\n");
    return 0;
}
