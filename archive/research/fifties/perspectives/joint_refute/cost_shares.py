'''Ledger shares of the front-line program (pkgCG experiments/frontline.py, sha 5936cfad) and the exact rate p of
pkgCG proof 10.1: what a free group pre-filter could save at most.'''

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

import sys; sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCG/pkg/blake3-r2/experiments'))
import frontline as F
from math import log2
rc = F.RUN_CONTEXTS
parts = dict(reps=(F.U_REP*(F.REP_BATCHES-1)+F.U_REP_TAIL)*rc, opened=F.U_OPEN*(F.A_BUDGET+1), ctx=F.U_CONTEXT*(rc+1),
             qpath=F.U_QPATH*(F.E_BUDGET+1), passl=F.U_PASS*(F.PASS_BUDGET+1), solver_credit=F.CREDIT_G,
             other=F.ONCE+9*2**20+2**27+F.S_OLD+430*2**38)
N = sum(parts.values()); print('N log2 %.4f  time_log2 %.4f' % (log2(N), log2(N/430)))
for k, v in parts.items(): print('%-14s log2 %.2f share %.4f' % (k, log2(v), v/N))
print('units per outer step %.2f ; solver credit per passing lane %.1f ; cap per call 17504' % (N/F.RUN_STEPS, F.CREDIT_G/F.PASS_BUDGET))
print('p(S) = 2^%.3f  p(all 14 outcomes) = 2^%.3f' % (log2(2**11*67633152)-128, log2(2**11*71698432)-128))
for f in (0.5625,):
    s = parts['solver_credit']/N
    print('free test dropping %.4f of solver calls saves %.3f bits (solver share %.4f)' % (f, -log2(1-f*s), s))
