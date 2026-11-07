"""Price the q3 lever with levers_r38.py's exact ledger arithmetic (read-only import; COMPUTED rows)."""

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

import io, contextlib, runpy, sys
from fractions import Fraction
from decimal import Decimal
sys.dont_write_bytecode = True
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(_hca_public_path_text('__HCA_WORKSPACE__/research/sha256grid/map-r38/levers_r38.py'))
total, log2, C, A70, A64, base, d = g['total'], g['log2'], g['C'], g['A70'], g['A64'], g['base'], g['d_struct']
def T(ng, a_s=A70): return float(log2(Fraction(total(A70, a_s, A64, ng_scale=ng))) - log2(C))
pad = Fraction(50, 51)
print('leader ledger %.5f; derivative row (no 2%% pad) %.5f' % (float(base), T(pad)))
for lab, b in (('2^-101.0101 (leader fixed-sample bound)', '-101.0101'), ('2^-101.0002 (G2 bound, this study)', '-101.0002')):
    f = Fraction(str(Decimal(2) ** (Decimal(-102) - Decimal(b))))
    print('q3_model -> %s:' % lab)
    print('   q3 only            %.5f  (vs 72.64 %+.4f, vs 72.61489 %+.4f)' % (T(f), T(f) - 72.64, T(f) - 72.61489))
    print('   q3 + no 2%% pad     %.5f' % T(f * pad))
    print('   q3 + pair %.6f %.5f' % (float(d), T(f / (2 - d))))
    print('   q3 + pair + no pad %.5f' % T(f / (2 - d) * pad))
