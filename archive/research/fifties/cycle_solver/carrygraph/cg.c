/* Carry-graph (bit-serial time-sweep) solver for the split_e3 cycle, generic word size n <= 32.
   Reads a schedule file from sched.py (structure + event list) and an instance file
   (lines: id c_0 ... c_K-1, the per-addition operand xconsts and additive consts, hex).
   Mode "dfs": depth-first over the schedule; returns the full root set of g and counts transitions (event executions)
               and primitive ops (model below).
   Mode "ex":  exhaustive reference over all 2^n values of g (word-level evaluation).
   usage: cg dfs|ex sched.txt inst.txt out.txt
   Primitive-op model per event (add/sub/xor/and/or/shift/rotate/load/store/compare = 1):
     G guess bit: 3 per branch (shift, or, store)       C carry guess: 2 per branch       Z: 1        V: 2
     A addition bit: 4 per term (load, shift, and, xor) + 3 per operand (xconst bit: shift, and, xor) + 1 per operand
       (accumulate) + 3 (const bit) + 1 (add carry) + 3 (out bit, new carry, store/compare)                    */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MAXA 9
#define MAXOP 3
#define MAXT 3
#define MAXEV 4096
typedef struct { int nterm; int w[MAXT], r[MAXT]; } Op;
typedef struct { int nsum, nop; Op op[MAXOP]; } Add;
static int n, na; static Add A[MAXA];
static int nev; static int ET[MAXEV], E1[MAXEV], E2[MAXEV], E3[MAXEV], ECOST[MAXEV];
static uint32_t XC[MAXA][MAXOP], KC[MAXA], MASK;
typedef struct { uint32_t v[MAXA + 1]; int carry[MAXA]; int gcarry[MAXA]; } St;
static unsigned long long trans, ops, nroot; static uint32_t roots[1024];

static inline uint32_t rotl(uint32_t x, int r) { r %= n; return r ? (((x << r) | (x >> (n - r))) & MASK) : x; }

static void dfs(int e, St s) {
  for (; e < nev; e++) {
    trans++; ops += ECOST[e];
    switch (ET[e]) {
    case 0: { /* guess bit E2 of word E1 */
      int w = E1[e], b = E2[e];
      St t = s; t.v[w] &= ~(1u << b); dfs(e + 1, t);
      trans++; ops += ECOST[e];
      t = s; t.v[w] |= (1u << b); dfs(e + 1, t);
      return; }
    case 1: { /* guess carry of addition E1, E2 values */
      int z = E1[e];
      for (int c = 0; c < E2[e]; c++) {
        St t = s; t.carry[z] = c; t.gcarry[z] = c;
        if (c) { trans++; ops += ECOST[e]; }
        dfs(e + 1, t);
      }
      return; }
    case 2: s.carry[E1[e]] = 0; break;
    case 3: { /* addition E1 bit E2 mode E3 */
      int z = E1[e], j = E2[e]; int sum = s.carry[z] + ((KC[z] >> j) & 1);
      for (int k = 0; k < A[z].nop; k++) {
        uint32_t b = (XC[z][k] >> j) & 1;
        for (int q = 0; q < A[z].op[k].nterm; q++) {
          int w = A[z].op[k].w[q], jj = ((j - A[z].op[k].r[q]) % n + n) % n;
          b ^= (s.v[w] >> jj) & 1;
        }
        sum += b;
      }
      uint32_t o = sum & 1; s.carry[z] = sum >> 1;
      int w = z + 1;                       /* output word index (z = 8 is chk: no word) */
      if (E3[e] == 2) { if (o) return; }
      else if (E3[e] == 1) { if (((s.v[w] >> j) & 1) != o) return; }
      else { s.v[w] = (s.v[w] & ~(1u << j)) | (o << j); }
      break; }
    case 4: if (s.carry[E1[e]] != s.gcarry[E1[e]]) return; break;
    }
  }
  if (nroot < 1024) roots[nroot] = s.v[0];
  nroot++;
}

static uint32_t evalw(uint32_t g) {
  uint32_t v[MAXA + 1]; v[0] = g;
  for (int z = 0; z < na; z++) {
    uint32_t sum = KC[z];
    for (int k = 0; k < A[z].nop; k++) {
      uint32_t x = XC[z][k];
      for (int q = 0; q < A[z].op[k].nterm; q++) x ^= rotl(v[A[z].op[k].w[q]], A[z].op[k].r[q]);
      sum += x;
    }
    v[z + 1] = sum & MASK;
  }
  return v[na];
}

static int cmpu(const void *a, const void *b) { uint32_t x = *(const uint32_t *)a, y = *(const uint32_t *)b; return x < y ? -1 : x > y; }

int main(int argc, char **argv) {
  if (argc < 5) { fprintf(stderr, "usage: cg dfs|ex sched inst out\n"); return 1; }
  int ex = !strcmp(argv[1], "ex");
  FILE *f = fopen(argv[2], "r"); if (!f) return 2;
  if (fscanf(f, "%d %d", &n, &na) != 2) return 3;
  MASK = n == 32 ? 0xFFFFFFFFu : ((1u << n) - 1);
  for (int z = 0; z < na; z++) {
    fscanf(f, "%d %d", &A[z].nsum, &A[z].nop);
    for (int k = 0; k < A[z].nop; k++) {
      fscanf(f, "%d", &A[z].op[k].nterm);
      for (int q = 0; q < A[z].op[k].nterm; q++) fscanf(f, "%d %d", &A[z].op[k].w[q], &A[z].op[k].r[q]);
    }
  }
  fscanf(f, "%d", &nev);
  for (int e = 0; e < nev; e++) {
    fscanf(f, "%d %d %d %d", &ET[e], &E1[e], &E2[e], &E3[e]);
    switch (ET[e]) {
    case 0: ECOST[e] = 3; break; case 1: ECOST[e] = 2; break; case 2: ECOST[e] = 1; break; case 4: ECOST[e] = 2; break;
    case 3: { int z = E1[e], c = 3 + 1 + 3; for (int k = 0; k < A[z].nop; k++) c += 3 + 1 + 4 * A[z].op[k].nterm; ECOST[e] = c; break; }
    }
  }
  fclose(f);
  FILE *fi = fopen(argv[3], "r"), *fo = fopen(argv[4], "w"); if (!fi || !fo) return 4;
  int id; int nk = 0; for (int z = 0; z < na; z++) nk += A[z].nop + 1;
  while (fscanf(fi, "%d", &id) == 1) {
    int k = 0;
    for (int z = 0; z < na; z++) {
      for (int q = 0; q < A[z].nop; q++) { unsigned x; fscanf(fi, "%x", &x); XC[z][q] = x & MASK; k++; }
      { unsigned x; fscanf(fi, "%x", &x); KC[z] = x & MASK; k++; }
    }
    trans = ops = nroot = 0;
    if (ex) {
      for (uint64_t g = 0; g <= MASK; g++) if (evalw((uint32_t)g) == 0) { if (nroot < 1024) roots[nroot] = (uint32_t)g; nroot++; }
      ops = (MASK + 1ull) * 43ull;   /* counted as in split_e3 (43 ops per candidate at n = 32) */
    } else {
      St s; memset(&s, 0, sizeof s); dfs(0, s);
    }
    unsigned long long m = nroot < 1024 ? nroot : 1024;
    qsort(roots, m, 4, cmpu);
    fprintf(fo, "%d %llu %llu %llu", id, nroot, trans, ops);
    for (unsigned long long i = 0; i < m; i++) fprintf(fo, " %x", roots[i]);
    fprintf(fo, "\n"); fflush(fo);
  }
  fclose(fo); return 0;
}
