'''For every k=1 design (REL model, F = {Y4,Y9,w8}): which loop parameters (inputs of the cyclic component that do
not depend on g) VARY with the free words B, and which are fixed by F and constants only.
A design whose loop reads B through a single 32-bit parameter that enters at the check would allow a one-time
2^32 table (h(g) = p) and an O(1) solve; this script measures how far every design is from that.
usage: python params.py  (writes params_out.txt)'''

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
REL = ev.REL
rows = pickle.load(open(_hca_public_path_text('__HCA_WORKSPACE__/research/fifties/split_e3/designs.pkl'), 'rb'))
F = ('Y4', 'Y9', 'w8'); res = []
for row in rows:
    g, B = row[2], row[3]
    if g not in ev.WORDS or any(w not in ev.WORDS for w in B): continue
    d = ev.Design(F, B, g)
    var = [p for p in d.params if d.dep.get(p, {p}) & set(B)]
    fixed = [p for p in d.params if p not in var]
    # position (index in loop) where each varying param first enters
    loopw = [w for _, w in d.loop]
    entry = {}
    for k, (i, w) in enumerate(d.loop):
        for x in ev.wset(REL[i]):
            if x in var and x not in entry: entry[x] = k
    for x in ev.wset(REL[d.chk]):
        if x in var and x not in entry: entry[x] = len(d.loop)
    first = min(entry.values()) if entry else len(d.loop)
    # rank-like count: how many distinct B words each varying param reads
    res.append((len(var), -first, len(d.loop), g, B, var, fixed, sorted(entry.items(), key=lambda t: t[1])))
res.sort()
out = open('params_out.txt', 'w')
def p(*a):
    print(*a); print(*a, file=out)
p('designs', len(res))
p('number of B-dependent loop parameters, histogram:', sorted(collections.Counter(r[0] for r in res).items()))
p('loop steps before the first B-dependent parameter enters (max over designs):', max(-r[1] for r in res))
p('histogram of that prefix length:', sorted(collections.Counter(-r[1] for r in res).items()))
for r in res[:12]:
    p('nvar=%d prefix=%d loop=%d g=%s B=%s\n   varying=%s\n   fixed=%s\n   entry=%s' % (r[0], -r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
best = sorted(res, key=lambda r: (r[1], r[0]))[:5]
p('longest B-free prefixes:')
for r in best:
    p('nvar=%d prefix=%d loop=%d g=%s B=%s entry=%s' % (r[0], -r[1], r[2], r[3], r[4], r[7]))
