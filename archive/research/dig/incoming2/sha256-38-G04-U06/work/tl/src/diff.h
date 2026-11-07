/* diff.h - signed-difference tools (our code) */
#ifndef TL_DIFF_H
#define TL_DIFF_H
#include "traillab.h"
typedef struct { const TLModel *M; int k, row; } TLCellCtx;
typedef struct {
  u32 D; int func; u32 T;               /* count x with func(x+D) - func(x) == T */
  int usexor; u32 xr;                   /* optional: x ^ (x+D) == xr */
  int (*cellok)(const void *ctx, u32 x, u32 y); const void *cellctx;   /* optional: the printed cell of that word */
} TLSdiffCfg;
typedef struct { u64 domain, exact, cellexact; long nxor, nsigned; } TLSdiffRes;
void tl_sym(u32 plus, u32 minus, char out[33]);
long tl_bsd(u32 D, int maxhw, u32 **plus, u32 **minus);
void tl_print_bsd(u32 D, int maxhw, int limit, u32 mark_xor, u32 mark_plus);
int  tl_sdiff_count(const TLSdiffCfg *g, TLSdiffRes *r, int print, int limit);
int  tl_backward(const TLModel *M, int b0, int b1, int maxhw, int do_enum);
int  tl_cellctx_ok(const void *ctx, u32 x, u32 y);
#endif
