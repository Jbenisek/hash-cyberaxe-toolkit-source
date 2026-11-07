'''Print the split_e3 design order (ev.py DESIGN) with, for every solved word, its relation and its dependency on B/g.
Read-only use of split_e3/ev.py.'''

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
d = ev.Design(*ev.DESIGN)
print('F', d.F, 'B', d.B, 'g', d.g)
print('params', d.params)
for i, w in d.ord:
    r = ev.REL[i]
    dep = sorted(d.dep[w] - set(d.F))
    tag = 'LOOP' if (i, w) in d.loop else ('pre ' if (i, w) in d.pre else 'post')
    print('%s %-6s <- %-55s dep %s' % (tag, w, ev.rels.show(r), dep))
print('check', ev.rels.show(ev.REL[d.chk]))
print('T1 dep', sorted(d.dep['T1'] - set(d.F)))
