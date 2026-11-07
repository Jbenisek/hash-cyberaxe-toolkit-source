/* traillab.h - lever-testing library for the 37/38-step SHA-256 characteristics (our own code).
   A characteristic file (chi/NAME.txt) gives the cells, two-bit conditions, the published pair and the attack model.
   Every pair the library produces is a real SHA-256 computation: the message words W0..W15 of both members and
   one chaining value; W16.. come from the real message expansion (no expanded word is ever held fixed). */
#ifndef TRAILLAB_H
#define TRAILLAB_H
#include <stdint.h>
#include <stdio.h>
typedef uint32_t u32;
typedef uint64_t u64;

#define TL_NR 64      /* max steps */
#define TL_O 4        /* rows -4..-1 = chaining value */
#define TL_MAXLIN 512
#define TL_MAXREL 16
enum { KA = 0, KE = 1, KW = 2 };

static inline u32 ROR(u32 x, int n) { return (x >> n) | (x << (32 - n)); }
static inline u32 BS0(u32 x) { return ROR(x, 2) ^ ROR(x, 13) ^ ROR(x, 22); }
static inline u32 BS1(u32 x) { return ROR(x, 6) ^ ROR(x, 11) ^ ROR(x, 25); }
static inline u32 ss0(u32 x) { return ROR(x, 7) ^ ROR(x, 18) ^ (x >> 3); }
static inline u32 ss1(u32 x) { return ROR(x, 17) ^ ROR(x, 19) ^ (x >> 10); }
static inline u32 CH(u32 x, u32 y, u32 z) { return (x & y) ^ (~x & z); }
static inline u32 MAJ(u32 x, u32 y, u32 z) { return (x & y) ^ (x & z) ^ (y & z); }
extern const u32 TL_K[64];

/* one cell of one word (A_t, E_t or W_t): conditions on the pair (x, y)
   (x & m) == v ; ((x ^ y) & dm) == d ; ((x ^ x_{t-1}) & q) == 0  (the '+' relation, member x) */
typedef struct { u32 m, v, dm, d, q, p; } TLCell;
/* XOR of up to 6 x-member bits = c ; checked at row 'row' (largest row among the terms) */
typedef struct { int nt; signed char k[6], b[6]; short r[6]; int c, row; } TLLin;
typedef struct {
  char name[48];
  TLCell c[3][TL_NR];
  TLLin lin[TL_MAXLIN]; int nlin;
  short lrow[TL_NR][64]; int nlrow[TL_NR];   /* index: lins closing at each row */
} TLConds;

typedef struct { u32 a[TL_NR + TL_O], e[TL_NR + TL_O], w[TL_NR]; } TLTr;
typedef struct { TLTr x, y; } TLPair;
#define TA(t, i) ((t)->a[(i) + TL_O])
#define TE(t, i) ((t)->e[(i) + TL_O])

enum { V_FIXED = 0, V_RAND, V_FSET, V_LIST, V_CELL };
enum { F_ID = 0, F_s0, F_s1, F_S0, F_S1 };
typedef struct { int type, late, func, cell, back; u32 T, bcx, bcy; u32 *vals; long nvals; char desc[96]; } TLVar;

/* free coordinates of one sample: x-member base words and the x-member E values of the E-driven rows */
typedef struct { u32 wx[16]; u32 ex[TL_NR]; } TLCoord;

typedef struct {
  char name[48];
  int nr, anchor, e0, e1, lorow;
  u32 cv[8], mx[16], my[16], dl[16];
  int have_digest; u32 digest[8];
  TLConds full;            /* every printed condition */
  TLConds base;            /* full minus the 'except' words (the attack model's conditions) */
  TLConds relax[TL_MAXREL]; int nrelax;
  TLVar var[16];
  int except[16];
  TLPair pub; TLCoord pubc;
  u32 *elist[TL_NR]; long nelist[TL_NR];   /* optional proposal list for an E-driven row (x-member E values) */
  int hold_from;           /* ARTIFACT MODE (0 = off, set by --hold-from T): W_t for t >= T are held at each member's published
                              value instead of the message expansion. Inconsistent messages; only for reproducing the held-fixed artifact. */
} TLModel;
/* expanded word u (u >= 16) of one member: the message expansion, or the published word in artifact mode */
static inline u32 tl_wnext(const TLModel *M, const TLTr *t, int ymember, int u) {
  if (M->hold_from && u >= M->hold_from) return ymember ? M->pub.y.w[u] : M->pub.x.w[u];
  return ss1(t->w[u - 2]) + t->w[u - 7] + ss0(t->w[u - 15]) + t->w[u - 16];
}

/* splitmix64 counter RNG */
typedef struct { u64 s; } TLRng;
static inline u64 tl_mix(u64 z) { z += 0x9e3779b97f4a7c15ull; z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull; z = (z ^ (z >> 27)) * 0x94d049bb133111ebull; return z ^ (z >> 31); }
static inline u64 tl_next(TLRng *r) { r->s += 0x9e3779b97f4a7c15ull; u64 z = r->s; z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9ull; z = (z ^ (z >> 27)) * 0x94d049bb133111ebull; return z ^ (z >> 31); }
static inline u32 tl_r32(TLRng *r) { return (u32)(tl_next(r) >> 32); }
static inline u64 tl_below(TLRng *r, u64 n) { return (u64)(((__uint128_t)tl_next(r) * n) >> 64); }
static inline TLRng tl_rng(u64 a, u64 b, u64 c, u64 d) { TLRng r; r.s = tl_mix(tl_mix(tl_mix(a ^ 0x5151) ^ b) ^ (c * 0x9e3779b1ull)) ^ d * 0xd1b54a32d192ed03ull; return r; }

/* model */
int  tl_load(const char *path, TLModel *M, const char *varoverride[], int nover);
int  tl_relax_parse(const TLModel *M, const TLConds *from, const char *spec, TLConds *out, const char *name);
const TLConds *tl_find_relax(const TLModel *M, const char *name);
void tl_conds_index(TLConds *C);
int  tl_parse_word(const char *s, int *k, int *row);       /* "E18" -> KE,18 */
const char *tl_kname(int k);
u32  tl_fn(int f, u32 x);
int  tl_fname(const char *s);

/* pairs */
void tl_step(TLTr *t, int i);                 /* row i from rows i-4..i-1 and w[i] */
void tl_unstep(TLTr *t, int i);               /* row i-4 from rows i-3..i and w[i] */
void tl_expand(TLTr *t, int from, int nr);
int  tl_build(const TLModel *M, const TLCoord *c, TLPair *p);     /* full, consistent rebuild; returns 1 if CVx==CVy-anchor-consistent */
void tl_build_from(const TLModel *M, const TLCoord *c, TLPair *p, int t, int hi); /* incremental: rows t..hi (t in edrive or later) */
void tl_edrive_row(const TLModel *M, TLPair *p, int t, u32 ex);  /* one E-driven row on both members */
int  tl_rowok(const TLConds *C, const TLPair *p, int t);
int  tl_rowsok(const TLConds *C, const TLPair *p, int lo, int hi);
int  tl_row_fail(const TLConds *C, const TLPair *p, int t, char *why, int n);
int  tl_state_eq(const TLPair *p, int b);
u32  tl_draw_var(const TLModel *M, int i, TLRng *r);
int  tl_var_member(const TLModel *M, int i, u32 w);
void tl_draw_vars(const TLModel *M, TLCoord *c, TLRng *r, int late);
void tl_compress_ref(const u32 cv[8], const u32 w16[16], int nr, u32 out[8]); /* independent reference */
int  tl_sha256_selftest(void);
u32  tl_word_mod(const TLCell *c);            /* signed modular difference of a cell (u/n bits) */
int  tl_word_cellok(const TLModel *M, int k, int row, u32 x, u32 y);  /* row cell + lins only on this word (full) */

/* threads */
int  tl_threads(void);
void tl_set_threads(int n);
void tl_parfor(long n, long chunk, void (*fn)(void *ctx, long i, int tid), void *ctx);

/* stats */
void tl_wilson(double k, double n, double *lo, double *hi);
#endif
