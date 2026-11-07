/* h1meas.c - measurements of the Orchard map at r partial rounds on truncated outputs (our own code, 2026-10-15).
 * Map at width w: F_w(v) = low w bits of digest(v, rho), v in [0, 2^w) (v and rho are canonical field elements; rho is the function index j).
 * Per trial: walk v_0 (from the seed), v_i = F_w(v_{i-1}) until the first repeat (exact, hash map of all values):
 *   t = least index with v_t in {v_0..v_{t-1}}, mu = index of that earlier value, lambda = t - mu.
 * DP statistics at density theta = T/2^h (DP iff (v mod 2^h) < T): gaps between consecutive DPs among v_1..v_{t-1}.
 * Then the search of rho.py (one trail, DPs, table cap mcap, budget S, recovery with gap cap gmax) is run on the same map;
 * trail values are taken from the stored walk (they are digest values), the recovery evaluates the digest afresh and the returned
 * pair is checked (distinct, equal F_w).
 * Usage: h1meas fam fixed r w T h S mcap gmax K seedbase   -> one JSON line per trial on stdout.
 *   fam o|c; fixed 0: trial k uses function index j = seedbase*1000003 + k (rho = j, or control key j), fixed f >= 1: j = f - 1 for every trial (one fixed function, many starts).
 *   start v_0 = splitmix(seedbase*1000003 + k) mod 2^w.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "../impl/pallas.h"

static int R, W, FAM;              /* FAM 'o': Orchard digest(v, rho) ; FAM 'c': control, keyed splitmix (a pseudo-random function) */
static uint64_t MASK, RHO, CKEY;
static uint64_t splitmix(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
static uint64_t Fw(uint64_t v) {
    if (FAM == 'c') return splitmix(splitmix(v ^ CKEY) + CKEY) & MASK;
    uint64_t a[4] = {v, 0, 0, 0}, z[4] = {RHO, 0, 0, 0}, o[4];
    poseidon_hash_r(a, z, R, o);
    return o[0] & MASK;          /* W <= 62 */
}

int main(int argc, char **argv) {
    if (argc != 12) { fprintf(stderr, "usage: h1meas fam fixed r w T h S mcap gmax K seedbase\n"); return 2; }
    FAM = argv[1][0]; int FIXED = atoi(argv[2]); argv += 2;
    R = atoi(argv[1]); W = atoi(argv[2]);
    uint64_t T = strtoull(argv[3], 0, 10); int H = atoi(argv[4]);
    uint64_t S = strtoull(argv[5], 0, 10), MCAP = strtoull(argv[6], 0, 10), GMAX = strtoull(argv[7], 0, 10);
    int K = atoi(argv[8]); uint64_t SB = strtoull(argv[9], 0, 10);
    MASK = (W >= 64) ? ~0ULL : ((1ULL << W) - 1); uint64_t HM = (1ULL << H) - 1;
    /* walk cap: 12 sqrt(N) (P(t > cap) <= exp(-72) for a random mapping); hash table 2^k >= 2 cap */
    uint64_t cap = (uint64_t)(12.0 * (double)(1ULL << (W / 2)) * ((W & 1) ? 1.41421356 : 1.0));
    uint64_t hsz = 1; while (hsz < 2 * cap) hsz <<= 1;
    uint64_t *hk = malloc(hsz * 8); uint32_t *hv = malloc(hsz * 4); uint64_t *tr = malloc((cap + 1) * 8);
    uint64_t *pi = malloc((MCAP + 2) * 8), *pv = malloc((MCAP + 2) * 8);   /* table: index word, value word */
    if (!hk || !hv || !tr || !pi || !pv) { fprintf(stderr, "alloc\n"); return 1; }
    for (int k = 0; k < K; k++) {
        memset(hk, 0, hsz * 8);
        uint64_t j = FIXED ? (uint64_t)(FIXED - 1) : SB * 1000003ULL + (uint64_t)k; RHO = j; CKEY = splitmix(j ^ 0x5bd1e995ULL);
        uint64_t v = splitmix(SB * 1000003ULL + (uint64_t)k) & MASK;
        uint64_t t = 0, mu = 0; int cens = 0;
        uint64_t hm = hsz - 1;
        /* insert v_0 */
        for (uint64_t i = 0;; i++) {
            tr[i] = v;
            uint64_t h = (splitmix(v) & hm);
            while (hk[h] && hk[h] != v + 1) h = (h + 1) & hm;
            if (hk[h]) { t = i; mu = hv[h]; break; }
            hk[h] = v + 1; hv[h] = (uint32_t)i;
            if (i >= cap) { cens = 1; t = i; break; }
            v = Fw(v);
        }
        uint64_t lam = t - mu;
        /* DP gaps among v_1..v_{t-1} */
        uint64_t ndp = 0, last = 0, ngap = 0, sgap = 0, maxgap = 0; int first = 1;
        for (uint64_t i = 1; i < t; i++) if ((tr[i] & HM) < T) {
            ndp++;
            if (!first) { uint64_t g = i - last; ngap++; sgap += g; if (g > maxgap) maxgap = g; }
            first = 0; last = i;
        }
        /* first DP at index >= mu (cycle), detection delay */
        int64_t aprime = -1;
        for (uint64_t i = (mu ? mu : 1); i < t; i++) if ((tr[i] & HM) < T) { aprime = (int64_t)i; break; }
        if (mu == 0 && aprime < 0 && (tr[0] & HM) < T) aprime = -1;  /* start is not a stored DP */
        /* the search of rho.py on this trail */
        const char *st = "steps"; uint64_t ev = 0, rec = 0, A = 0, B = 0; int ok = 0;
        if (!cens) {
            uint64_t np = 1; pi[0] = 0; pv[0] = tr[0];
            uint64_t i = 0, x = tr[0]; int64_t hit = -1;
            while (i < S) {
                i++; ev++;
                x = (i < t) ? tr[i] : tr[mu + (i - mu) % lam];
                if ((x & HM) < T) {
                    for (uint64_t q = 1; q < np; q++) if (pv[q] == x) { hit = (int64_t)q; break; }
                    if (hit >= 0) break;
                    if (np > MCAP) { st = "table"; break; }
                    pi[np] = i; pv[np] = x; np++;
                }
            }
            if (hit >= 0) {
                uint64_t a = pi[hit], L = i - a, s = pi[hit - 1]; A = pv[hit - 1];
                uint64_t q = s + L; uint64_t lo = 0, hi = np - 1;
                while (lo < hi) { uint64_t m = (lo + hi + 1) / 2; if (pi[m] <= q) lo = m; else hi = m - 1; }
                uint64_t idx = pi[lo]; B = pv[lo];
                if (q - idx > GMAX) st = "gap";
                else {
                    for (uint64_t j = 0; j < q - idx; j++) { B = Fw(B); rec++; }
                    if (A == B) st = "start-on-cycle";
                    else {
                        st = "gap";
                        for (uint64_t j = 0; j < GMAX; j++) {
                            uint64_t nA = Fw(A), nB = Fw(B); rec += 2;
                            if (nA == nB) { st = "found"; ok = (A != B) && (Fw(A) == Fw(B)); break; }
                            A = nA; B = nB;
                        }
                    }
                }
            } else if (strcmp(st, "table")) st = "steps";
        }
        printf("{\"fam\":\"%c\",\"fn\":%llu,\"r\":%d,\"w\":%d,\"seedbase\":%llu,\"k\":%d,\"v0\":%llu,\"t\":%llu,\"mu\":%llu,\"lambda\":%llu,\"cens\":%d,"
               "\"ndp\":%llu,\"ngap\":%llu,\"sgap\":%llu,\"maxgap\":%llu,\"aprime\":%lld,\"status\":\"%s\",\"evals\":%llu,\"rec\":%llu,"
               "\"A\":%llu,\"B\":%llu,\"pair_ok\":%d}\n",
               FAM, (unsigned long long)j, R, W, (unsigned long long)SB, k, (unsigned long long)tr[0], (unsigned long long)t, (unsigned long long)mu,
               (unsigned long long)lam, cens, (unsigned long long)ndp, (unsigned long long)ngap, (unsigned long long)sgap,
               (unsigned long long)maxgap, (long long)aprime, st, (unsigned long long)ev, (unsigned long long)rec,
               (unsigned long long)(strcmp(st, "found") ? 0 : A), (unsigned long long)(strcmp(st, "found") ? 0 : B), ok);
        fflush(stdout);
    }
    return 0;
}
