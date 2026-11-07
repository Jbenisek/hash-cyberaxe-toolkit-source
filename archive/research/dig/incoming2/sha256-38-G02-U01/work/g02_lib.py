
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

import sys, json, math, copy
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/dig/incoming2/sha256-38-G02-U01/work'))
from g02_ledger38 import ledger, Fr, RUNS, SR, NB
import os
p2base = json.load(open(os.path.join(RUNS, 'pre2.json')))
def S(o): return o['log2_T'] + max(0.0, o['memory_log2_bytes'] - 20)
def run(k, nbB=True, **kw):
    B = 1 << k
    if 'xiter' in kw and nbB: kw['xiter'] = Fr(kw['xiter'], B)
    return ledger(show=False, B=B, nbB=nbB, **kw)
def sweep(nbB=True, kmax=50, **kw):
    out = []
    for k in range(0, kmax + 1):
        o = run(k, nbB, **kw); out.append((k, S(o), o['log2_T'], o['memory_log2_bytes']))
    return out
def best(sw): return min(sw, key=lambda r: r[1])
