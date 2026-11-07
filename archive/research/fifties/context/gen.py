#!/usr/bin/env python3
# Generates ctx.c (exact member walk of memberloop: context = 7 outer words, all 2^19 members) and
# writes ref.json (Python reference values for context 0, first members) for the cross-check.

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import json, os, random, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/impl/memberloop'))
import memberloop as ml
from outer import OUTER_WORDS, CLASS_FREE, CLASS_VALUE, FREE_MASK, Y3, MASK, scalar_outer, member_y

NCTX = int(sys.argv[1]) if len(sys.argv) > 1 else 256
SEED = int(sys.argv[2]) if len(sys.argv) > 2 else 20261009
rnd = random.Random(SEED)
ctxs = [[rnd.getrandbits(32) for _ in OUTER_WORDS] for _ in range(NCTX)]

v = ml.var
out = ["#include <stdint.h>", "typedef uint32_t u32;",
       "static inline u32 d_ror(u32 x, int r){ return (x >> r) | (x << (32 - r)); }",
       "#define NCTX %d" % NCTX,
       "static const u32 CTXS[NCTX][7] = {" + ",".join("{" + ",".join("0x%08xu" % w for w in c) + "}" for c in ctxs) + "};",
       "static const int CLASS_FREE[19] = {%s};" % ",".join(map(str, CLASS_FREE)),
       "static inline u32 member_y(u32 m){ u32 w=0; for(int n=0;n<19;n++) w |= ((m>>n)&1u)<<CLASS_FREE[n];"
       " return ((0x%08xu | (w & 0x%08xu)) - 0x%08xu); }" % (CLASS_VALUE, FREE_MASK, Y3)]
ctx_names = [n for n, _ in ml.CTX_LINES]
out.append("typedef struct { u32 %s; } Ctx;" % "; u32 ".join([v(w) for w in OUTER_WORDS] + [v(n) for n in ctx_names]))
out.append("static void context_pre(const u32 *ow, Ctx *C){")
for i, w in enumerate(OUTER_WORDS):
    out.append("  u32 %s = ow[%d]; C->%s = %s;" % (v(w), i, v(w), v(w)))
for name, e in ml.CTX_LINES:
    out.append("  u32 %s = %s; C->%s = %s;" % (v(name), ml.c_expr(e), v(name), v(name)))
out.append("}")
out.append("static inline void member_eval(const Ctx *C, u32 v_Y4, u32 *P, u32 *X1, u32 *D){")
for w in OUTER_WORDS + tuple(ctx_names):
    out.append("  u32 %s = C->%s; (void)%s;" % (v(w), v(w), v(w)))
for name, e in ml.DEP_LINES:
    out.append("  u32 %s = %s; (void)%s;" % (v(name), ml.c_expr(e), v(name)))
out.append("  *P = v_C0_a1; *X1 = v_X1; *D = v_D1_d1;")
out.append("}")
with open(os.path.join(HERE, "ctx_gen.h"), "w") as f:
    f.write("\n".join(out) + "\n")

# Python reference: context 0 and 1, members 0..7 and a few random ones, via the full step CO.
ref = []
for ci in (0, 1, NCTX - 1):
    for m in [0, 1, 2, 3, 12345, (1 << 19) - 1]:
        w = 0
        for n, i in enumerate(CLASS_FREE):
            w |= ((m >> n) & 1) << i
        r = scalar_outer(ctxs[ci] + [w])
        assert member_y(w)[2] == m
        ref.append([ci, m, r["Y4"], r["C0.a1"], r["X1"], r["D1.d1"]])
with open(os.path.join(HERE, "ref.json"), "w") as f:
    json.dump({"seed": SEED, "nctx": NCTX, "ref": ref}, f)
print("ctx lines", len(ml.CTX_LINES), "dep lines", len(ml.DEP_LINES), "ctxs", NCTX)
