'''Batch coordinates for the t1filter table: which free words can vary while the TABLE inputs (Y4, X4, X8, w6, S11)
stay fixed?  Design B2 = (D2.b1, K3.d1, S15, X4 | D3.a1, K0.b1), g = C0.b1: check that it is a valid k=1 design on the
exact relation set, that the 21-equation loop is the same, and print the dependency of every loop parameter on
the two varying words (D3.a1, K0.b1).'''

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

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
d0 = ev.Design(*ev.DESIGN)
F = ('Y4', 'Y9', 'w8'); HELD2 = ('D2.b1', 'K3.d1', 'S15', 'X4'); VAR2 = ('D3.a1', 'K0.b1')
d2 = ev.Design(F, HELD2 + VAR2, 'C0.b1')
print('B2 design valid; check relation:', ev.rels.show(ev.REL[d2.chk]))
print('loop words same as original:', [w for _, w in d2.loop] == [w for _, w in d0.loop], '; params same:', d2.params == d0.params)
for p in d0.params + ['K1.d1', 'w5', 'S14', 'S6']:
    dv = sorted(set(VAR2) & d2.dep[p]); print('  %-6s depends on varying words %s' % (p, dv))
