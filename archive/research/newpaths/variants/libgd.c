// closure / grow helpers for ihs2.py (ctypes).  n <= 128.
#include <stdio.h>
#include <stdlib.h>
typedef unsigned __int128 u128;
#define MAXR 4096
static int n, R, rtype[MAXR], rcnt[MAXR], rv[MAXR][8], occ[128][256], nocc[128];
static u128 rmask[MAXR], rtrig[MAXR], ALL, BASE;
static unsigned long long rs = 88172645463325252ULL;
static inline unsigned long long rnd(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static inline int single(u128 u) { return u && !(u & (u - 1)); }
static inline int bitidx(u128 u) { unsigned long long lo = (unsigned long long)u, hi = (unsigned long long)(u >> 64); return lo ? __builtin_ctzll(lo) : 64 + __builtin_ctzll(hi); }
static u128 prop(u128 known, u128 newb) {
    int q[256], qh = 0, qt = 0;
    for (int v = 0; v < n; v++) if ((newb >> v) & 1) q[qt++] = v;
    while (qh < qt) {
        int v = q[qh++];
        for (int i = 0; i < nocc[v]; i++) {
            int r = occ[v][i];
            if (rtype[r] == 0) { u128 u = rmask[r] & ~known; if (single(u)) { known |= u; q[qt++] = bitidx(u); } }
            else if (!(rtrig[r] & ~known)) { u128 t = rmask[r] & ~rtrig[r]; if (t & ~known) { known |= t; q[qt++] = bitidx(t); } }
        }
    }
    return known;
}
int load(const char *fn) {
    FILE *f = fopen(fn, "r");
    if (fscanf(f, "%d %d", &n, &R) != 2) return -1;
    for (int r = 0; r < R; r++) {
        if (fscanf(f, "%d %d", &rtype[r], &rcnt[r]) != 2) return -1;
        for (int i = 0; i < rcnt[r]; i++) {
            if (fscanf(f, "%d", &rv[r][i]) != 1) return -1;
            rmask[r] |= (u128)1 << rv[r][i];
            if (rtype[r] == 0 || i < rcnt[r] - 1) occ[rv[r][i]][nocc[rv[r][i]]++] = r;
            if (rtype[r] == 1 && i < rcnt[r] - 1) rtrig[r] |= (u128)1 << rv[r][i];
        }
    }
    fclose(f);
    ALL = (n == 128) ? ~(u128)0 : (((u128)1 << n) - 1);
    u128 b = 0;
    for (int r = 0; r < R; r++) if (rtype[r] == 0 && rcnt[r] == 1) b |= rmask[r];
    BASE = prop(b, b);
    return n;
}
static u128 mk(unsigned long long lo, unsigned long long hi) { return ((u128)hi << 64) | lo; }
// closure of BASE|in; returns 1 if everything
int clos(unsigned long long lo, unsigned long long hi, unsigned long long *out) {
    u128 s = BASE | mk(lo, hi); u128 c = prop(s, s);
    out[0] = (unsigned long long)c; out[1] = (unsigned long long)(c >> 64);
    return c == ALL;
}
// grow closure of in to a maximal proper closed set (random order); writes complement
void grow(unsigned long long lo, unsigned long long hi, unsigned long long seed, unsigned long long *out) {
    rs ^= seed * 0x9E3779B97F4A7C15ULL + 1;
    u128 s = BASE | mk(lo, hi); u128 C = prop(s, s);
    int ord[128], m = 0;
    for (int v = 0; v < n; v++) if (!((C >> v) & 1)) ord[m++] = v;
    for (int i = m - 1; i > 0; i--) { int j = rnd() % (i + 1); int t = ord[i]; ord[i] = ord[j]; ord[j] = t; }
    for (int i = 0; i < m; i++) {
        int v = ord[i];
        if ((C >> v) & 1) continue;
        u128 b = (u128)1 << v;
        u128 C2 = prop(C | b, b);
        if (C2 != ALL) C = C2;
    }
    u128 D = ALL & ~C;
    out[0] = (unsigned long long)D; out[1] = (unsigned long long)(D >> 64);
}
