#include "pallas.h"
#include "pallas_consts.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

static int fails = 0;
#define CHECK(c, ...) do { if (!(c)) { fails++; printf("FAIL line %d: ", __LINE__); printf(__VA_ARGS__); printf("\n"); } } while (0)
#define LLU(x) ((unsigned long long)(x))

static uint64_t rng_s = 88172645463325252ULL;
static uint64_t rnd64(void) { rng_s ^= rng_s << 13; rng_s ^= rng_s >> 7; rng_s ^= rng_s << 17; return rng_s; }
static void rnd_fp(fp *r) {
    uint64_t v[4];
    do { v[0] = rnd64(); v[1] = rnd64(); v[2] = rnd64(); v[3] = rnd64() & 0x7fffffffffffffffULL; } while (!fp_limbs_canonical(v));
    fp_from_limbs(r, v);
}
static int popcnt(const uint64_t e[4], int *top) {
    int c = 0; *top = -1;
    for (int i = 255; i >= 0; i--) if ((e[i / 64] >> (i % 64)) & 1) { c++; if (*top < 0) *top = i; }
    return c;
}

int main(int argc, char **argv) {
    const char *dir = argc > 1 ? argv[1] : ".";
    char path[512], line[1024];

    /* ---- Montgomery parameters sanity */
    CHECK((uint64_t)(PALLAS_INV * PALLAS_P[0] + 1) == 0, "INV");
    { fp one; fp_set_one(&one); uint64_t v[4]; fp_to_limbs(v, &one); CHECK(v[0] == 1 && !v[1] && !v[2] && !v[3], "one"); }

    /* ---- field vectors from Python big-int */
    snprintf(path, sizeof path, "%s/field_vectors.txt", dir);
    FILE *f = fopen(path, "r"); if (!f) { printf("cannot open %s\n", path); return 2; }
    int nfv = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#') continue;
        char h[6][65]; int lg;
        if (sscanf(line, "%64s %64s %64s %64s %64s %64s %d", h[0], h[1], h[2], h[3], h[4], h[5], &lg) != 7) continue;
        fp a, b, e_add, e_sub, e_mul, e_inv, t;
        CHECK(!fp_from_hex(&a, h[0]) && !fp_from_hex(&b, h[1]) && !fp_from_hex(&e_add, h[2]) && !fp_from_hex(&e_sub, h[3]) && !fp_from_hex(&e_mul, h[4]) && !fp_from_hex(&e_inv, h[5]), "hex");
        fp_add(&t, &a, &b); CHECK(fp_eq(&t, &e_add), "add %d", nfv);
        fp_sub(&t, &a, &b); CHECK(fp_eq(&t, &e_sub), "sub %d", nfv);
        fp_mul(&t, &a, &b); CHECK(fp_eq(&t, &e_mul), "mul %d", nfv);
        { fp s1, s2; fp_sqr(&s1, &a); fp_mul(&s2, &a, &a); CHECK(fp_eq(&s1, &s2), "sqr %d", nfv); }
        fp_inv(&t, &a); CHECK(fp_eq(&t, &e_inv), "inv %d", nfv);
        int L = fp_legendre(&a); CHECK((L == 0 ? 0 : (L == 1 ? 1 : 2)) == lg, "legendre %d", nfv);
        fp s; int ok = fp_sqrt(&s, &a); CHECK(ok == (lg != 2), "sqrt flag %d", nfv);
        if (ok) { fp s2; fp_sqr(&s2, &s); CHECK(fp_eq(&s2, &a), "sqrt value %d", nfv); }
        { char hx[65]; fp_to_hex(hx, &a); CHECK(strcmp(hx, h[0]) == 0, "hex roundtrip %d", nfv); }
        nfv++;
    }
    fclose(f);
    printf("field vectors checked (add, sub, mul, sqr, inv, legendre, sqrt, hex): %d\n", nfv);

    /* ---- random identities, sqrt on squares and non-residues */
    int sq_ok = 0, nr_ok = 0;
    for (int i = 0; i < 2000; i++) {
        fp a, b, c, t, u, s; rnd_fp(&a); rnd_fp(&b); rnd_fp(&c);
        fp_mul(&t, &a, &b); fp_mul(&u, &b, &a); CHECK(fp_eq(&t, &u), "comm");
        fp_add(&t, &b, &c); fp_mul(&t, &a, &t); fp_mul(&u, &a, &b); fp_mul(&c, &a, &c); fp_add(&u, &u, &c); CHECK(fp_eq(&t, &u), "distrib");
        fp_inv(&t, &a); fp_mul(&t, &t, &a); fp_set_one(&u); CHECK(fp_eq(&t, &u), "inv");
        fp_sqr(&t, &a); CHECK(fp_sqrt(&s, &t) == 1, "sqrt of square"); fp_sqr(&u, &s); CHECK(fp_eq(&u, &t), "sqrt root"); sq_ok++;
        fp_neg(&t, &a); fp_add(&t, &t, &a); CHECK(fp_is_zero(&t), "neg");
        if (fp_legendre(&b) == -1) { CHECK(fp_sqrt(&s, &b) == 0, "sqrt of nonresidue"); nr_ok++; }
    }
    printf("random identities ok; sqrt on %d squares and %d non-residues\n", sq_ok, nr_ok);
    /* squares of elements with deep 2-adic structure: x = z^k * odd part (worst cases for Tonelli-Shanks) */
    {
        fp z, t, s, u; memcpy(z.l, PALLAS_Z_M, 32);
        int worst = 0;
        for (int k = 0; k < 64; k++) {
            fp a; rnd_fp(&a); fp_pow(&t, &z, (uint64_t[4]){ (uint64_t)k * 67108859ULL + 1, 0, 0, 0 }); fp_mul(&a, &a, &t); fp_sqr(&a, &a);
            fp_counters_reset(); int ok = fp_sqrt(&s, &a); uint64_t c = fp_prim_total(); if ((int)c > worst) worst = (int)c;
            fp_sqr(&u, &s); CHECK(ok && fp_eq(&u, &a), "TS deep %d", k);
        }
        printf("Tonelli-Shanks max primitives seen over 64 random squares: %d\n", worst);
        fp five, one, m1; fp_from_u64(&five, 5); CHECK(fp_legendre(&five) == -1, "5 nonresidue");
        t = z; for (int i = 0; i < 31; i++) fp_sqr(&t, &t); fp_set_one(&one); fp_neg(&m1, &one); CHECK(fp_eq(&t, &m1), "Z^(2^31) = -1");
    }

    /* ---- exact counter checks */
    {
        fp a, t, s; rnd_fp(&a); int top, pc = popcnt(PALLAS_PM2, &top);
        fp_counters_reset(); fp_inv(&t, &a);
        CHECK(fp_cnt.sqr == (uint64_t)top && fp_cnt.mul == (uint64_t)(pc - 1) && fp_cnt.add == 0 && fp_cnt.sub == 0, "inv count sqr=%llu mul=%llu", LLU(fp_cnt.sqr), LLU(fp_cnt.mul));
        printf("fp_inv: bitlen(p-2)=%d popcount=%d -> %llu sqr + %llu mul = %llu primitives (inv_calls=%llu)\n", top + 1, pc, LLU(fp_cnt.sqr), LLU(fp_cnt.mul), LLU(fp_prim_total()), LLU(fp_cnt.inv_calls));
        fp_counters_reset(); fp_legendre(&a);
        printf("fp_legendre: %llu sqr + %llu mul = %llu primitives\n", LLU(fp_cnt.sqr), LLU(fp_cnt.mul), LLU(fp_prim_total()));
        fp_sqr(&t, &a); fp_counters_reset(); fp_sqrt(&s, &t);
        printf("fp_sqrt on a random square (one sample): %llu sqr + %llu mul = %llu primitives\n", LLU(fp_cnt.sqr), LLU(fp_cnt.mul), LLU(fp_prim_total()));
        fp_counters_reset(); fp_add(&t, &a, &a); fp_sub(&t, &a, &a); fp_mul(&t, &a, &a); fp_sqr(&t, &a); fp_neg(&t, &a); fp_dbl(&t, &a); fp_pow5(&t, &a);
        CHECK(fp_cnt.add == 2 && fp_cnt.sub == 2 && fp_cnt.mul == 2 && fp_cnt.sqr == 3, "unit counts add=%llu sub=%llu mul=%llu sqr=%llu", LLU(fp_cnt.add), LLU(fp_cnt.sub), LLU(fp_cnt.mul), LLU(fp_cnt.sqr));
    }

    /* ---- Poseidon vs Python reference */
    snprintf(path, sizeof path, "%s/poseidon_vectors.txt", dir);
    f = fopen(path, "r"); if (!f) { printf("cannot open %s\n", path); return 2; }
    int npv[57] = {0}, total = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#') continue;
        int r; char hn[65], hr[65], hd[65];
        if (sscanf(line, "%d %64s %64s %64s", &r, hn, hr, hd) != 4) continue;
        fp nk, rho, d, o;
        CHECK(fp_from_hex(&nk, hn) == 0 && fp_from_hex(&rho, hr) == 0 && fp_from_hex(&d, hd) == 0, "hex");
        fp_counters_reset();
        poseidon_hash_r_fp(&o, &nk, &rho, r);
        CHECK(fp_eq(&o, &d), "poseidon r=%d mismatch (line %d)", r, total);
        CHECK(fp_prim_total() == (uint64_t)poseidon_C(r) && fp_cnt.add == (uint64_t)(72 + 9 * r) && fp_cnt.mul + fp_cnt.sqr == (uint64_t)(144 + 12 * r) && fp_cnt.sub == 0,
              "count r=%d: add=%llu mul+sqr=%llu", r, LLU(fp_cnt.add), LLU(fp_cnt.mul + fp_cnt.sqr));
        uint64_t a4[4], b4[4], o4[4], e4[4]; fp_to_limbs(a4, &nk); fp_to_limbs(b4, &rho); fp_to_limbs(e4, &d);
        CHECK(poseidon_hash_r(a4, b4, r, o4) == 0 && memcmp(o4, e4, 32) == 0, "limb API r=%d", r);
        npv[r]++; total++;
    }
    fclose(f);
    printf("poseidon vectors checked: %d  (r=0:%d r=1:%d r=2:%d r=3:%d r=5:%d r=10:%d r=30:%d r=55:%d r=56:%d)\n", total, npv[0], npv[1], npv[2], npv[3], npv[5], npv[10], npv[30], npv[55], npv[56]);
    printf("per-call primitive count == C(r) = 216+21r on every vector (r=1: %d, r=2: %d), one call = 1 unit\n", poseidon_C(1), poseidon_C(2));
    {
        uint64_t bad[4] = {PALLAS_P[0], PALLAS_P[1], PALLAS_P[2], PALLAS_P[3]}, ok4[4] = {0, 0, 0, 0}, o4[4];
        CHECK(poseidon_hash_r(bad, ok4, 1, o4) == -1 && poseidon_hash_r(ok4, bad, 1, o4) == -1 && poseidon_hash_r(ok4, ok4, 57, o4) == -1, "noncanonical/range reject");
    }

    /* ---- speed (information only) */
    {
        fp a, b, o; rnd_fp(&a); rnd_fp(&b);
        clock_t t0 = clock(); for (int i = 0; i < 200000; i++) { poseidon_hash_r_fp(&o, &a, &b, 1); a = o; }
        double s = (double)(clock() - t0) / CLOCKS_PER_SEC;
        printf("speed r=1: %.2f us/hash (200000 hashes, %.3f s)\n", s / 200000 * 1e6, s);
        t0 = clock(); fp x = a; for (int i = 0; i < 20000000; i++) fp_mul(&x, &x, &b);
        s = (double)(clock() - t0) / CLOCKS_PER_SEC;
        printf("speed fp_mul: %.1f ns/mul (checksum limb %llx)\n", s / 20000000 * 1e9, LLU(x.l[0]));
    }

    printf(fails ? "FAILED: %d checks\n" : "ALL CHECKS PASSED\n", fails);
    return fails != 0;
}
