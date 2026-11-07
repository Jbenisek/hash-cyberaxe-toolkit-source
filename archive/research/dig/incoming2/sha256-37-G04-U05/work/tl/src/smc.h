/* smc.h - sampling, window counting and exact enumeration (our code) */
#ifndef TL_SMC_H
#define TL_SMC_H
#include "traillab.h"

typedef struct { TLPair p; TLCoord c; u32 alive; } TLPart;

/* per-particle counters */
enum { CN_N = 0, CN_BROKEN, CN_INCONS, CN_REPLAYBAD, CN_EXACT, CN_EV0, CN_JOINT0 = CN_EV0 + TL_MAXREL + 1,
       CN_EQ_EX = CN_JOINT0 + TL_MAXREL + 1, CN_EQ_NEX, CN_NEQ_EX, CN_COUNT };   /* --equiv: predicate and EXACT, predicate only, EXACT only */

typedef struct {
  int a, b, event;          /* window rows; event 0 = zero state after row b, 1 = zero output after the last step */
  int np, m, mt2, mw, mt;   /* particles; proposals: prefix E stages, late prefix stage, window E stages, final */
  u64 seed; int carrier;    /* carrier 1 = union of the cell events filters window E-driven rows, 0 = none */
  const TLConds *pre;       /* conditions of the prefix rows */
  const TLConds *C[TL_MAXREL + 1]; int nc;   /* C[0] = printed cells, C[1..] = relaxations */
  int verbose;
  int eqrow, neqw, eqw[8];  /* --equiv R,j1,j2..: predicate = zero state difference after row R and dW_j = 0 (modular) for every listed j */
} TLWinCfg;
typedef struct {
  double log2prefix, log2carrier; int latefree;
  u64 cnt[CN_COUNT];
  double rat[TL_MAXREL + 1], rath[TL_MAXREL + 1], ratA[TL_MAXREL + 1], rathA[TL_MAXREL + 1], ratB[TL_MAXREL + 1], rathB[TL_MAXREL + 1];
} TLWinRes;

TLPart *tl_smc_prefix(const TLModel *M, const TLConds *pre, int a, int np, int m, int mt2, u64 seed, double *log2est, int verbose);
int tl_window(const TLModel *M, const TLWinCfg *g, TLWinRes *res);

/* exact enumeration */
enum { ES_ALL, ES_MASK, ES_CELL, ES_LIST, ES_SET, ES_SETCELL };
typedef struct { int k, row, kind; u32 mask, fix; u64 n; } TLEnumSpec;
enum { EX_MEMBER = 0, EX_INCONS, EX_PRE, EX_EXACT, EX_PEXACT, EX_EV0, EX_PEV0 = EX_EV0 + TL_MAXREL + 1, EX_PXEV0 = EX_PEV0 + TL_MAXREL + 1, EX_COUNT = EX_PXEV0 + TL_MAXREL + 1 };
typedef struct {
  int a, b, event; TLEnumSpec sp[2]; int nsp;
  const TLConds *pre; const TLConds *C[TL_MAXREL + 1]; int nc;
  int hist;   /* 1 + index into C: histogram of the enumerated index over (prefix and C[hist-1]); only when total <= 2^16 */
} TLExactCfg;
typedef struct { u64 total; u64 c[EX_COUNT]; u64 *hist; } TLExactRes;
int tl_spec_parse(const TLModel *M, const char *s, TLEnumSpec *e);
int tl_exact(const TLModel *M, const TLExactCfg *g, const TLCoord *bc, TLExactRes *r);
#endif
