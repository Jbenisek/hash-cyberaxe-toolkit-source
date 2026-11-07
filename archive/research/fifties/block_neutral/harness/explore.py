'''One-off look at the split_e3 design: relation counts, solved-word coefficients, frame-O (outer basis + T1) order.'''

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
from ev import REL, WORDS, order, Design, DESIGN
d = Design(*DESIGN)
print('relations', len(REL), 'words', len(WORDS))
print('design ord', len(d.ord), 'check', REL[d.chk][3], 'loop', len(d.loop), 'pre', len(d.pre), 'params', d.params)
bad = [(REL[i][3], w, REL[i][1][w]) for i, w in d.ord if REL[i][0] == 'add' and abs(REL[i][1][w]) != 1]
print('solved words with |coef| != 1:', bad)
coefs = sorted({c for r in REL if r[0] == 'add' for c in r[1].values()})
print('all add coefs', coefs)
basis = ['C0.d1', 'D2.a1', 'D2.b1', 'S11', 'S4', 'X9', 'w6', 'Y4', 'T1']
o, ch, kn = order(set(basis))
print('frame O: solved', len(o), 'checks', len(ch), 'unknown', sorted(set(WORDS) - kn))
print('T1 in deps of:', [REL[i][3] for i, w in d.ord if 'T1' in ev.wset(REL[i])])
print('words', WORDS)
