'''Ops per candidate g (loop + check, rotation = 1 op, as split_e3/ev.py Design.cuda) for every k=1 design, and the
cost of the T1 value given a root (words that depend on g but are off the loop).  Also: for the front design, which
designs' free words are g-independent there (so its instances map onto them without a solve).
usage: python opscount.py  (writes opscount_out.txt)'''

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

import sys, pickle, collections
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3'))
import ev
rows = pickle.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/designs.pkl'), 'rb'))
F = ('Y4', 'Y9', 'w8'); res = []
front = ev.Design(*ev.DESIGN)
pre_front = set(F) | set(front.B) | {w for _, w in front.pre}
for row in rows:
    g, B = row[2], row[3]
    if g not in ev.WORDS or any(w not in ev.WORDS for w in B): continue
    d = ev.Design(F, B, g)
    lines, chk, ops = d.cuda()
    mappable = all(w in pre_front for w in B)
    res.append((ops, len(d.loop), len(d.params), g, B, mappable))
res.sort()
out = open('opscount_out.txt', 'w')
def p(*a):
    print(*a); print(*a, file=out)
p('designs', len(res))
p('ops per candidate histogram (lowest 12):', sorted(collections.Counter(r[0] for r in res).items())[:12])
p('front design', ev.DESIGN, 'ops', front.cuda()[2])
for r in res[:15]:
    p('ops=%d loop=%d params=%d g=%s B=%s mappable-from-front=%s' % r)
p('lowest-ops designs whose B is computable from a front-design instance:')
for r in [r for r in res if r[5]][:8]:
    p('ops=%d loop=%d params=%d g=%s B=%s' % r[:5])
